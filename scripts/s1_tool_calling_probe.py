"""S-1: does the default model call ``emit_finding`` reliably? (technical_stack.md section 7, research R-21, quickstart C1)

Needs a real key in AGENTIC_REVIEW_API_KEY and network access, so it is NOT part of pytest. It builds a fixture
repository with one planted defect, then runs the real assembly and the real review port against the provider N times per
model at temperature 0. It records figures and sets no pass mark: the maintainer reads them and decides (Principle VI).

    uv run python scripts/s1_tool_calling_probe.py --runs 50 --model meta/llama-3.3-70b-instruct
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from langchain_core.messages import AIMessage
from pydantic import ValidationError

from agentic_review.core.agent.build import build_review_port
from agentic_review.core.assembly.prompt import assemble
from agentic_review.core.changeset.model import ScopeRequest
from agentic_review.core.changeset.resolve import resolve
from agentic_review.core.changeset.summary import measure_new_files
from agentic_review.core.config.credentials import Credential, CredentialProblem, find_credential
from agentic_review.core.config.redact import redact
from agentic_review.core.config.settings import DEFAULT_BASE_URL, AgentSettings, BudgetSettings
from agentic_review.core.findings.model import FindingDraft
from agentic_review.core.findings.validation import Rejected, validate_call

DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "specs" / "001-walking-skeleton" / "s1-results.md"

BEFORE = """\
import { fetchUser, type User } from "./api";
import { logger } from "./logger";

export async function loadUser(id: string): Promise<User | null> {
  try {
    return await fetchUser(id);
  } catch (error) {
    logger.warn("user lookup failed", error);
    return null;
  }
}

export function displayName(user: User): string {
  return user.name.trim();
}
"""

# The planted defect: without `await`, a rejected promise escapes the try/catch, so loadUser rejects instead of
# returning null. A harmless rename in the second function gives the diff a second hunk.
AFTER = BEFORE.replace("return await fetchUser(id);", "return fetchUser(id);").replace(
    "return user.name.trim();", "const name = user.name;\n  return name.trim();"
)


@dataclass
class RunRecord:
    index: int
    model: str
    calls: int = 0
    valid: int = 0
    schema_rejected: int = 0
    reference_rejected: int = 0
    invalid_json: int = 0
    no_call: bool = False
    repair_turns: int = 0
    completion: str = ""
    tokens_in: int | None = None
    tokens_out: int | None = None
    latency_s: float = 0.0
    error: str | None = None
    severities: list[str] = field(default_factory=list)


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, shell=False, check=True, capture_output=True)


def build_fixture(root: Path) -> Path:
    repo = root / "s1-fixture"
    (repo / "src").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "S-1 probe")
    git(repo, "config", "user.email", "s1@example.invalid")
    git(repo, "config", "core.autocrlf", "false")
    (repo / "src" / "user.ts").write_bytes(BEFORE.encode())
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fixture")
    (repo / "src" / "user.ts").write_bytes(AFTER.encode())
    return repo


def probe_once(index: int, model: str, base_url: str, credential: Credential, repo: Path) -> RunRecord:
    record = RunRecord(index=index, model=model)
    change_set = resolve(repo, ScopeRequest(kind="working-tree"), (), was_defaulted=True)
    context = assemble(change_set, measure_new_files(change_set), BudgetSettings())
    settings = AgentSettings(model=model, base_url=base_url, temperature=0)
    port = build_review_port(settings, credential)

    started = time.perf_counter()
    try:
        outcome = port.review(context)
    except Exception as error:  # the review step does not map provider errors until User Story 2
        record.latency_s = time.perf_counter() - started
        record.error = redact(f"{type(error).__name__}: {error}", credential.reveal())[:200]
        return record
    record.latency_s = time.perf_counter() - started

    for message in port.last_transcript:
        if not isinstance(message, AIMessage):
            continue
        record.invalid_json += len(message.invalid_tool_calls)
        for call in message.tool_calls:
            try:
                FindingDraft.model_validate(call["args"])
            except ValidationError:
                if call["name"] == "emit_finding":
                    record.schema_rejected += 1
                    continue
            if isinstance(validate_call(call["name"], call["args"], context.material), Rejected):
                record.reference_rejected += 1
    record.calls = outcome.tool_calls_total
    record.valid = len(outcome.findings)
    record.severities = [f.severity for f in outcome.findings]
    record.no_call = outcome.completion_status == "no-tool-call"
    record.repair_turns = outcome.repair_turns
    record.completion = outcome.completion_status
    record.tokens_in, record.tokens_out = outcome.tokens_in, outcome.tokens_out
    return record


def write_results(path: Path, records: list[RunRecord], runs: int, base_url: str) -> None:
    lines = [
        "# S-1 results: does the model call `emit_finding`?",
        "",
        f"Written by `scripts/s1_tool_calling_probe.py` on {datetime.now(UTC):%Y-%m-%d %H:%M} UTC.",
        f"Endpoint `{base_url}`, temperature 0, {runs} runs per model, one planted defect "
        "(a missing `await` inside `try/catch` in `src/user.ts`).",
        "",
        "**No pass mark is set** (research R-21). The maintainer reads these figures and decides the default model and "
        "whether FR-5.6b's structured-output fallback is pulled forward.",
        "",
        "## Summary",
        "",
        "| Model | Runs | Errors | No call | Calls | Valid | Schema-rejected | Reference-rejected | Invalid JSON "
        "| Runs with ≥1 valid | Mean latency (s) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for model in dict.fromkeys(r.model for r in records):
        rows = [r for r in records if r.model == model]
        ok = [r for r in rows if r.error is None]
        mean = sum(r.latency_s for r in ok) / len(ok) if ok else 0.0
        lines.append(
            f"| `{model}` | {len(rows)} | {len(rows) - len(ok)} | {sum(r.no_call for r in ok)} "
            f"| {sum(r.calls for r in ok)} | {sum(r.valid for r in ok)} | {sum(r.schema_rejected for r in ok)} "
            f"| {sum(r.reference_rejected for r in ok)} | {sum(r.invalid_json for r in ok)} "
            f"| {sum(1 for r in ok if r.valid)} | {mean:.2f} |"
        )
    lines += [
        "",
        "## Per run",
        "",
        "| # | Model | Completion | Calls | Valid | Schema-rej. | Ref.-rej. | Invalid JSON | Repair turns "
        "| Severities | Tokens in/out | Latency (s) | Error |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        lines.append(
            f"| {r.index} | `{r.model}` | {r.completion or '-'} | {r.calls} | {r.valid} | {r.schema_rejected} "
            f"| {r.reference_rejected} | {r.invalid_json} | {r.repair_turns} | {', '.join(r.severities) or '-'} "
            f"| {r.tokens_in}/{r.tokens_out} | {r.latency_s:.2f} | {r.error or ''} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", type=int, default=50)
    parser.add_argument("--model", action="append", help="repeatable; defaults to the configured default model")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    models = args.model or [AgentSettings().model]

    with tempfile.TemporaryDirectory() as scratch:
        repo = build_fixture(Path(scratch))
        credential = find_credential(os.environ, repo)
        if isinstance(credential, CredentialProblem):
            print(credential.message, file=sys.stderr)
            return 3
        records = []
        for model in models:
            for index in range(1, args.runs + 1):
                record = probe_once(index, model, args.base_url, credential, repo)
                records.append(record)
                status = record.error or f"{record.completion}, {record.valid} valid of {record.calls} calls"
                print(f"[{model}] run {index}/{args.runs}: {status} ({record.latency_s:.1f}s)", flush=True)

    write_results(args.output, records, args.runs, args.base_url)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

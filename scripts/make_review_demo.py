"""Build a small TypeScript/JavaScript git repository with planted defects, to try `agentic-review review` on.

The repository gets a clean first commit, then uncommitted edits that introduce known defects, so the review sees a
real diff. It also exercises the parts of the output that are not findings: an excluded build file, a non-TypeScript
file, a deleted file and an untracked new file.

    uv run python scripts/make_review_demo.py                      # creates ../review-demo next to this project
    uv run python scripts/make_review_demo.py --dest C:\\tmp\\demo   # anywhere else
    uv run python scripts/make_review_demo.py --force              # rebuild an existing demo

Then, from inside the demo repository:

    uv run --project "<this project>" --env-file "<this project>/.env" agentic-review review

Keep the demo OUTSIDE this project's directory: git lists a nested repository as an untracked directory, which the
current build does not handle.
"""

from __future__ import annotations

import argparse
import shutil
import stat
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEST = PROJECT_ROOT.parent / "review-demo"

# ---------------------------------------------------------------------------------------------------------------------
# The clean first commit.
# ---------------------------------------------------------------------------------------------------------------------

BASELINE: dict[str, str] = {
    "package.json": """\
{
  "name": "review-demo",
  "version": "1.0.0",
  "type": "module"
}
""",
    "README.md": "# review-demo\n\nA fixture for agentic-review.\n",
    "src/users.ts": """\
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

export function averageAge(users: User[]): number {
  if (users.length === 0) {
    return 0;
  }
  let total = 0;
  for (let i = 0; i < users.length; i++) {
    total += users[i].age;
  }
  return total / users.length;
}
""",
    "src/search.ts": """\
import { db } from "./db";

export async function findUsersByName(name: string) {
  return db.query("SELECT id, name FROM users WHERE name = $1", [name]);
}
""",
    "src/format.js": """\
export function formatPrice(cents) {
  return `$${(cents / 100).toFixed(2)}`;
}
""",
    "src/legacy.ts": "export const LEGACY_FLAG = true;\n",
    "dist/bundle.js": "console.log('built');\n",
}

# ---------------------------------------------------------------------------------------------------------------------
# Uncommitted edits. Each planted defect is described in PLANTED below.
# ---------------------------------------------------------------------------------------------------------------------

EDITS: dict[str, str] = {
    "src/users.ts": """\
import { fetchUser, type User } from "./api";
import { logger } from "./logger";

export async function loadUser(id: string): Promise<User | null> {
  try {
    return fetchUser(id);
  } catch (error) {
    logger.warn("user lookup failed", error);
    return null;
  }
}

export function averageAge(users: User[]): number {
  let total = 0;
  for (let i = 0; i <= users.length; i++) {
    total += users[i].age;
  }
  return total / users.length;
}
""",
    "src/search.ts": """\
import { db } from "./db";

export async function findUsersByName(name: string) {
  return db.query("SELECT id, name FROM users WHERE name = '" + name + "'");
}
""",
    "src/format.js": """\
export function formatPrice(cents) {
  const unused = cents * 2;
  return `$${(cents / 100).toFixed(2)}`;
}
""",
    "src/retry.ts": """\
export async function withRetry<T>(operation: () => Promise<T>, attempts = 3): Promise<T | undefined> {
  for (let attempt = 1; attempt <= attempts; attempt++) {
    try {
      return await operation();
    } catch {
      // try again
    }
  }
  return undefined;
}
""",
    "README.md": "# review-demo\n\nA fixture for agentic-review, now with planted defects.\n",
    "dist/bundle.js": "console.log('rebuilt');\n",
}

DELETED = ["src/legacy.ts"]

PLANTED = [
    ("src/users.ts", "6", "error-handling", "important or blocking",
     "`return fetchUser(id)` without `await`: a rejected promise escapes the try/catch, so the function rejects "
     "instead of returning null."),
    ("src/users.ts", "15-16", "correctness", "blocking",
     "`i <= users.length` reads one element past the end (`users[users.length].age` throws)."),
    ("src/users.ts", "13-19", "correctness", "important",
     "The empty-array guard was removed: `averageAge([])` now returns NaN (0 / 0)."),
    ("src/search.ts", "4", "security", "blocking",
     "The parameterised query became string concatenation: SQL injection through `name`."),
    ("src/retry.ts", "5-7", "error-handling", "important",
     "New file: every error is swallowed and the caller gets `undefined` with no cause, even for non-retryable errors."),
    ("src/format.js", "2", "maintainability", "nit",
     "`unused` is computed and never read."),
]

EXPECTED_OUTPUT = [
    "Reviewed: src/format.js, src/retry.ts (untracked, so added), src/search.ts, src/users.ts",
    "Listed, not reviewed: PLANTED_DEFECTS.md and README.md (not TypeScript or JavaScript); src/legacy.ts (deleted)",
    "Excluded: dist/bundle.js (default:build-output)",
    "Exit code: 1 if any finding is blocking, 0 otherwise",
]


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, shell=False, check=True, capture_output=True)


def write(root: Path, files: dict[str, str]) -> None:
    for relative, text in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))  # LF endings on every OS


def _make_writable(func, path, _exc) -> None:  # noqa: ANN001 - shutil.rmtree onerror signature
    Path(path).chmod(stat.S_IWRITE)
    func(path)


def planted_defects_markdown() -> str:
    lines = [
        "# Planted defects",
        "",
        "What a good review of the uncommitted change should find. Line numbers are in the edited files.",
        "This file is Markdown, so the reviewer lists it but does not send it to the model.",
        "",
        "| File | Lines | Category | Expected severity | Defect |",
        "|---|---|---|---|---|",
        *(f"| `{f}` | {lines_} | {cat} | {sev} | {text} |" for f, lines_, cat, sev, text in PLANTED),
        "",
        "## Expected shape of the output",
        "",
        *(f"- {item}" for item in EXPECTED_OUTPUT),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST, help=f"where to create it (default: {DEFAULT_DEST})")
    parser.add_argument("--force", action="store_true", help="delete and rebuild an existing destination")
    args = parser.parse_args()
    dest: Path = args.dest.resolve()

    if dest == PROJECT_ROOT or PROJECT_ROOT in dest.parents:
        print(f"Refusing to create the demo inside this project ({PROJECT_ROOT}). Choose a --dest outside it.",
              file=sys.stderr)
        return 2
    if dest.exists():
        if not args.force:
            print(f"{dest} already exists. Use --force to rebuild it.", file=sys.stderr)
            return 2
        shutil.rmtree(dest, onerror=_make_writable)

    dest.mkdir(parents=True)
    git(dest, "init", "-q", "-b", "main")
    git(dest, "config", "user.name", "Review Demo")
    git(dest, "config", "user.email", "review-demo@example.invalid")
    git(dest, "config", "core.autocrlf", "false")
    write(dest, BASELINE)
    git(dest, "add", "-A")
    git(dest, "commit", "-q", "-m", "Initial clean version")

    write(dest, EDITS)
    for relative in DELETED:
        (dest / relative).unlink()
    (dest / "PLANTED_DEFECTS.md").write_bytes(planted_defects_markdown().encode("utf-8"))

    print(f"Demo repository created at {dest}\n")
    print("Planted defects (also in PLANTED_DEFECTS.md):")
    for file, lines_, category, severity, text in PLANTED:
        print(f"  {file}:{lines_}  [{severity}, {category}]  {text}")
    print("\nRun the review from inside it:")
    print(f'  cd "{dest}"')
    print(f'  uv run --project "{PROJECT_ROOT}" --env-file "{PROJECT_ROOT / ".env"}" agentic-review review')
    return 0


if __name__ == "__main__":
    sys.exit(main())

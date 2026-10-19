# Contract: Internal Seams (001)

These are **not** user-facing. They are the Python boundaries that the constitution's structural principles (II, III)
and the frozen interfaces (SRS §5) depend on, so they are written down before tasks are generated. Everything
else is ordinary code.

Signatures are indicative: names may be refined during implementation, but **the direction of each dependency and what
crosses each seam may not** without revisiting this plan.

---

## 1 · Pipeline: the only owner of order (ADR-0001) · `agents/pipeline_agent.py`

```python
@dataclass(frozen=True)
class ReviewRequest:
    cwd: Path
    scope: ScopeKind | None          # None = not given on the command line
    base: str | None
    head: str | None                 # --head REF; range only, None = HEAD
    pr: str | None                   # --pr URL; selects the pull-request scope by itself
    commit: str | None               # --commit REF; selects the commit scope by itself (User Story 4)
    config_path: Path | None
    ceiling: int | None

@dataclass(frozen=True)
class PreflightFailure:
    message: str                     # already redacted; the CLI prints it to stderr

@dataclass(frozen=True)
class Reviewed:
    report: ReviewReport             # verdict already computed in core
    ignored_settings: tuple[str, ...]

def run_review(
    request: ReviewRequest,
    *,
    env: Mapping[str, str],
    clock: Callable[[], float] = time.monotonic,
    now: Callable[[], datetime] = utc_now,
    review_port: ReviewPort | None = None,   # None = build the default through agents/review_port.py
    pull_requests: PullRequestSource | None = None,   # None = GitPullRequestSource(); see §2a
) -> PreflightFailure | Reviewed: ...
```

Order: **preflight → change set → [nothing to review? → output] → assembly → [budget exhausted? → output] →
review → output**. After preflight nothing raises (Principle V). Every stage that runs is timed.

## 2 · Change set: producer of the frozen structure · `core/changeset/`

```python
def locate_repository(cwd: Path) -> Path | None: ...
def ref_exists(repo_root: Path, ref: str) -> bool: ...
def head_is_unborn(repo_root: Path) -> bool: ...
def resolve(repo_root: Path, scope: ScopeRequest, exclude: Sequence[str]) -> ChangeSet: ...
def measure_new_files(change_set: ChangeSet) -> Mapping[str, int]: ...   # reviewable files only
def summarise(change_set: ChangeSet) -> ChangeSummary: ...
```

The **only** package that runs git (R-3). `ChangeSet` is what v3's Action adapter will produce by other means
(FR-10.3c), so nothing downstream may reach past it to git.

```python
def diff_branches(repo_root: Path, base: str, head: str, exclude: Sequence[str]) -> BranchDiff: ...
def have_merge_base(repo_root: Path, base: str, head: str) -> bool: ...
```

`diff_branches` is `git diff base...head` as a function: files, exclusions, and the two commits compared. The
`range` scope calls it on the local repository; the pull-request scope calls it on a repository it fetched.

## 2a · Pull-request source: the seam a better reader replaces · `core/changeset/pull_request.py`

```python
def parse_pull_request_url(url: str) -> PullRequestRef | None: ...   # https://github.com/<owner>/<repo>/pull/<n>

class PullRequestSource(Protocol):
    def open(self, pr: PullRequestRef, *, base: str | None) -> OpenedPullRequest: ...   # raises PullRequestError

class OpenedPullRequest(Protocol):
    def change_set(self, exclude: Sequence[str]) -> ChangeSet: ...
    def line_counts(self, change_set: ChangeSet) -> Mapping[str, int]: ...
    def close(self) -> None: ...
```

`open` is called by preflight (check 5) and may fail; after it, nothing may. `change_set` and `line_counts` are
called by the change-set stage; `close` by `run_review`, in a `finally`. The source reaches the pipeline as run
context (`PipelineDeps.pull_requests`), the way the review port's factory does.

**What may cross this seam: a `ChangeSet` and line counts. Nothing else.** No path, no remote name, no ref that only
one implementation would have. `GitPullRequestSource` — a blobless, no-checkout clone, then `diff_branches` — is the
only implementation and is **interim**: one backed by the GitHub MCP server is expected to replace it (ADR-0011,
R-25). `tests/integration/test_pull_request_scope.py` holds the seam with a source that never touches git.

## 3 · Assembly: the only budget owner · `core/assembly/`

```python
def assemble(change_set: ChangeSet, line_counts: Mapping[str, int], budget: BudgetSettings
             ) -> ReviewContext | BudgetExhausted: ...
```

## 4 · Review port: provider-independent (FR-0.3) · protocol in `core/findings/`, implementation in `agents/review_port.py`

```python
class ReviewPort(Protocol):
    def review(self, context: ReviewContext) -> ReviewOutcome: ...

# agents/ - the ONLY package importing langchain_* / langgraph / openai (ADR-0010)
def build_review_port(settings: AgentSettings, credential: Credential,
                      *, chat_model: BaseChatModel | None = None) -> ReviewPort: ...
```

`chat_model` is the test injection point for the scripted stand-in (R-19). Production passes `None`, and
`ChatOpenAI` is built inside.

## 5 · Findings: validation · `core/findings/`

```python
def validate_call(name: str, args: object, material: RunMaterial) -> Accepted | Rejected: ...
def tool_schema() -> dict: ...                   # generated from FindingDraft, refs inlined
def report_schema() -> dict: ...                 # generated from ReviewReport
def fingerprint(draft: FindingDraft) -> str: ...
```

These are pure functions with no I/O, so they can be tested without a framework in the fixture (FR-5.8).

## 6 · Output: verdict and rendering · `core/output/`

```python
def compute_verdict(completion: CompletionStatus, findings: Sequence[Finding]) -> Verdict: ...
def build_report(...) -> ReviewReport: ...
def render_terminal(report: ReviewReport, console: rich.console.Console) -> None: ...
def to_json(report: ReviewReport) -> str: ...
```

`render_terminal` and `to_json` take the **same** `ReviewReport` (FR-027). Neither recomputes anything.

## 7 · CLI: translation only · `cli/`

The CLI parses flags (after the `--json` argv normalisation, R-18), calls `run_review`, chooses streams, writes, and maps
`report.verdict` → exit code. It contains **no** logic that decides what is a finding (FR-10.2), and nothing imports
it (import contract 6).

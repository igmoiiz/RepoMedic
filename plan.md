# RepoMedic — Implementation Plan

## Planning rules

- Build in vertical slices that can be run and tested.
- Do not scaffold every planned module as empty files.
- Every milestone ends with tests and working documentation.
- Keep the original repository untouched during diagnosis.
- Prefer a small, reproducible benchmark over subjective demo claims.
- Record decisions and deviations in `docs/DECISIONS.md`.
- Do not begin the next milestone while critical tests from the current milestone fail.

## Phase 0 — Repository and development foundation

### Tasks
- Create the project layout and `pyproject.toml`.
- Establish Python 3.12 baseline and `.venv`.
- Configure formatter, linter, type checker, and pytest.
- Add `.gitignore`, `.env.example`, and safe configuration defaults.
- Create `AGENTS.md`, `MASTER.md`, and the product/architecture/security docs.
- Add a simple CLI health/status command.
- Document clean setup and verification commands.

### Acceptance criteria
- Setup succeeds from a clean clone using documented commands.
- All Python project commands run inside `.venv`.
- Lint, type checks, and tests run without global package dependencies.
- No secrets or local artifacts are tracked.

## Phase 1 — Repository inspection and test execution

### Tasks
- Validate a user-selected repository path.
- Detect Git status, branch, and existing modifications.
- Identify Python project metadata and test configuration.
- Implement ignore/exclusion rules.
- Build a controlled test runner with timeouts and output limits.
- Capture structured execution results.

### Acceptance criteria
- Invalid paths are rejected.
- Pre-existing modifications are recorded and never overwritten.
- A known passing and failing fixture are distinguished correctly.
- Timeouts and non-zero exit codes are reported accurately.
- Tests can run without a model API key.

## Phase 2 — Python source index and fault localization

### Tasks
- Parse Python files with `ast`.
- Index modules, classes, functions, imports, and source ranges.
- Connect traceback frames and failed assertions to indexed symbols.
- Add optional coverage collection.
- Add optional Git-diff signals.
- Implement and document an interpretable location-ranking algorithm.

### Acceptance criteria
- Source references point to valid paths and line ranges.
- Parse errors are recorded without crashing the whole investigation.
- Ranking is deterministic for identical evidence and configuration.
- Unit tests cover nested functions, imports, syntax errors, and excluded paths.

## Phase 3 — Evidence ledger and hypothesis engine

### Tasks
- Define typed models for evidence, hypotheses, experiments, and status transitions.
- Persist events in SQLite.
- Add a provider-neutral model interface.
- Generate hypotheses grounded in collected evidence.
- Validate model outputs and reject unsupported evidence references.
- Add bounded experiment selection and execution.

### Acceptance criteria
- Every diagnosis claim can be traced to evidence or is labeled as inference.
- Invalid model output cannot crash or bypass policy.
- The system can return `INCONCLUSIVE`.
- Time, experiment, output, and model-call budgets are enforced.
- Provider failures are recoverable and clearly reported.

## Phase 4 — Diagnostic report and local UI

### Tasks
- Add a local FastAPI service.
- Build a React/TypeScript UI.
- Show session status, timeline, source references, hypotheses, and evidence graph.
- Stream or poll structured investigation events.
- Add report export with secret-aware redaction.

### Acceptance criteria
- The entire diagnosis is viewable without reading raw logs.
- Every source reference resolves correctly.
- Failed and incomplete investigations are visible.
- API is loopback-bound by default and state-changing actions are protected.
- UI does not fabricate results when the backend fails.

## Phase 5 — Patch proposal and approval

### Tasks
- Create an isolated Git worktree for patching.
- Generate a unified diff.
- Validate patch paths and changed-file policy.
- Run targeted verification in the isolated workspace.
- Implement explicit approval and safe application.
- Detect repository changes that invalidate a prepared patch.

### Acceptance criteria
- The original working tree is unchanged before approval.
- Full diff is visible before approval.
- No patch is applied without a separate explicit approval.
- Failed tests prevent the patch from being labeled verified.
- Pre-existing changes survive all workflows.

## Phase 6 — Benchmark, reliability, and release

### Tasks
- Create a fixture set with known bugs and expected behavior.
- Compare with traceback-only and basic LLM baselines.
- Measure top-1/top-5 localization, root-cause correctness, repair verification, regression rate, latency, and cost.
- Add adversarial security tests.
- Profile memory and runtime.
- Document limitations and reproducible benchmark commands.

### Acceptance criteria
- Results can be reproduced from documented commands.
- Baseline and RepoMedic use the same test cases.
- Metrics are reported without cherry-picking.
- No unmeasured performance claims appear in documentation.
- Known limitations and residual risks are published.

## Development quality gates

Run the applicable checks before each milestone is considered complete:
1. Formatter check.
2. Linter.
3. Type checker.
4. Unit tests.
5. Integration tests.
6. Security tests for changed boundaries.
7. End-to-end fixture test.
8. Manual review of user-visible errors and logs.

Use the commands actually configured in `pyproject.toml`; do not claim a check ran if it did not.

## Priority order

P0: repository safety, reproducible test runner, evidence data model.
P1: source indexing, fault localization, diagnostic report.
P2: hypothesis/experiment loop and local UI.
P3: patch proposal, isolated verification, approval.
P4: benchmark expansion, optimization, packaging.

## Definition of done

A feature is done only when it is implemented, tested, documented, handles expected failure paths, and does not violate `security.md`. A passing happy-path demo alone is insufficient.

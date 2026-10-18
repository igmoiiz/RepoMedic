# RepoMedic — Architecture

## 1. Architecture goals

- Local-first, Python-first, single-user MVP.
- Clear boundaries between deterministic tools and probabilistic model reasoning.
- Testable modules with replaceable model providers.
- Structured investigation state and event history.
- Safe handling of untrusted repositories.
- No unnecessary microservices or infrastructure.

## 2. High-level components

### Frontend
Initial proposal: React + TypeScript + Vite, Tailwind CSS, shadcn/ui, and React Flow for the evidence graph.
Responsibilities:
- repository/session selection;
- investigation status and event timeline;
- ranked hypotheses and supporting evidence;
- source references;
- experiment results;
- report display and export;
- patch diff review and explicit approval.

### Local API
FastAPI serves the local UI/API and streams investigation events when needed.
Responsibilities:
- validate requests and repository paths;
- create and query investigation sessions;
- expose structured evidence and reports;
- enforce approval state transitions;
- avoid executing arbitrary commands directly from request text.

### Workflow orchestrator
Use an explicit Python state machine for the MVP. Do not introduce a complex agent framework unless real workflow requirements justify it.
Suggested states:
`CREATED -> REPOSITORY_INSPECTED -> FAILURE_REPRODUCTION -> ANALYSIS -> HYPOTHESIS_REVIEW -> EXPERIMENTS -> REPORT_READY -> PATCH_PROPOSED -> PATCH_VERIFIED -> APPROVAL_PENDING -> APPLIED`
Terminal/exception states should include `INCONCLUSIVE`, `CANCELLED`, `FAILED`, and `BLOCKED_BY_POLICY`.
State transitions must be validated and persisted.

### Repository inspector
- Validate the selected root and resolve paths.
- Detect Git repository and current branch/status.
- Identify Python files and project metadata.
- Respect `.gitignore` and configurable exclusions.
- Exclude `.env`, credentials, private keys, virtual environments, caches, build outputs, and large/generated files from indexing.
- Do not change the repository during inspection.

### Static-analysis engine
- Use Python `ast` for initial parsing and symbol extraction.
- Add LibCST only when preserving formatting for source transformation is needed.
- Build a lightweight index of modules, classes, functions, imports, and references.
- Record parser failures rather than silently skipping files.
- Treat static call relationships as approximations, especially for dynamic Python behavior.

### Execution engine
- Run only approved, explicit commands.
- Capture command, working directory, exit code, duration, stdout, stderr, timeout, and cancellation state.
- Use argument arrays rather than shell command concatenation.
- Apply timeouts and output limits.
- Do not execute model-generated shell commands without policy validation and user consent.
- For untrusted repositories, use a restricted isolated environment. A container is defense-in-depth, not a complete sandbox.
- Preserve the user's current working tree and existing modifications.

### Fault-localization engine
Start with interpretable signals:
- traceback frames and failing assertion;
- test file and test name;
- coverage data where available;
- suspicious lines in relevant call paths;
- static analysis findings;
- recent Git diff, only if available and relevant.

Use a documented scoring function for ranking suspicious locations. Keep raw signals available so ranking can be debugged and evaluated.

### Hypothesis engine
Each hypothesis should include:
- stable ID;
- concise claim;
- candidate source locations;
- supporting evidence IDs;
- contradicting evidence IDs;
- status (`candidate`, `supported`, `contradicted`, `verified`, `unresolved`);
- confidence label with a documented meaning;
- experiment proposal;
- reason for ranking.

LLM-generated statements are not evidence by themselves. Evidence must refer to tool observations, source excerpts, test outcomes, or explicitly identified external information.

### Experiment engine
- Choose targeted experiments that distinguish the highest-ranked competing hypotheses.
- Use a bounded budget for time, test runs, output, and model calls.
- Record experiment intent, command or method, input, result, and interpretation.
- Separate environment failures from evidence about the defect.
- Never mutate the original repository as part of diagnosis.

### Patch manager
- Optional in the MVP.
- Create a dedicated Git worktree or another verified isolated copy.
- Generate a unified diff and inspect changed paths.
- Reject paths outside the allowed worktree and dangerous file changes.
- Run targeted tests and applicable regression checks.
- Keep verified and unverified status explicit.
- Require a separate, explicit approval action before applying changes to the user's working branch.
- Never commit, push, or open a PR automatically in the MVP.

### Persistence
Use SQLite for sessions, state transitions, event records, evidence metadata, and reports.
Store large outputs as bounded local artifacts with safe paths. Avoid persisting secrets or entire repository contents unnecessarily.
Use schema migrations if the database schema evolves.

### Model adapter
Define a provider-neutral interface for:
- structured hypothesis generation;
- experiment recommendation;
- report synthesis;
- optional patch proposal.

Validate model output against typed schemas. Handle timeouts, malformed output, rate limits, and provider errors. Do not require a particular model provider for deterministic tests.

## 3. Data flow

1. User chooses repository and describes a failure or selects a test.
2. Inspector validates repository and reports Git state.
3. User authorizes the planned test command.
4. Execution engine captures the failure.
5. Static analysis and optional coverage identify relevant code.
6. Fault-localization engine ranks suspicious locations.
7. Hypothesis engine creates evidence-linked candidate explanations.
8. Experiment engine runs approved, bounded experiments.
9. Evidence ledger updates and hypothesis statuses change.
10. Report generator presents findings and uncertainty.
11. If requested, patch manager creates an isolated patch proposal.
12. Verification runs and records actual results.
13. User reviews the diff and explicitly approves application.

## 4. Suggested package structure

```text
repomedic/
  AGENTS.md
  MASTER.md
  project.md
  architecture.md
  security.md
  plan.md
  opencode.json
  pyproject.toml
  .gitignore
  .env.example
  backend/
    pyproject.toml              # only if the team chooses a separately managed backend
  src/
    repomedic/
      __init__.py
      cli.py
      config.py
      api/
      core/
        models.py
        state_machine.py
        events.py
      repository/
        inspector.py
        git.py
        exclusions.py
      execution/
        runner.py
        policies.py
        results.py
      analysis/
        python_index.py
        fault_localization.py
        evidence.py
      diagnosis/
        hypotheses.py
        experiments.py
        report.py
      patching/
        worktree.py
        diff.py
        verification.py
      storage/
        database.py
        repositories.py
      models/
        adapter.py
  frontend/
  tests/
    unit/
    integration/
    fixtures/
      buggy_projects/
  docs/
```

Do not create empty modules just to match this tree. Add a module when there is an implemented responsibility for it. Prefer one root `pyproject.toml` and one root virtual environment for the MVP unless dependency boundaries prove that a split is necessary.

## 5. Local development and packaging

- Python 3.12 is the initial baseline unless dependency compatibility checks justify another supported version.
- Create `.venv` in the project root.
- Install runtime and development dependencies into `.venv`.
- Invoke Python tools through `.venv` or `python -m ...`; never rely on globally installed project packages.
- Keep `pyproject.toml` as the dependency and tool configuration source of truth.
- Commit a lockfile if the selected package manager supports it; choose one package-management workflow and document it.
- Keep frontend dependencies in `frontend/node_modules`; do not install Node packages into the Python environment.
- Do not commit `.venv`, `node_modules`, caches, local databases, logs, repository snapshots, or secrets.
- Document a reproducible setup from a clean clone.

## 6. Testing layers

- Unit: parsers, schemas, state transitions, scoring, path validation, policy checks.
- Integration: Git inspection, controlled test execution, SQLite persistence, model adapter error handling.
- End-to-end: known faulty fixture -> reproduced failure -> diagnosis -> report.
- Safety: path traversal, symlink handling, secret exclusions, timeout handling, output limits, malformed model output, unapproved patch application.
- Regression: every discovered defect becomes a reproducible test where feasible.

## 7. Architectural constraints

- No LLM is the source of truth for test outcomes.
- No silent writes to a user's repository.
- No unbounded tool loops.
- No secrets in logs, prompts, reports, or committed files.
- No network access from a repository execution sandbox unless explicitly required and approved.
- No claim of sandbox security without threat-model testing.

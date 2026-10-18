---
title: "Phase 1 — Repository inspection and test execution"
type: task
status: pending
priority: high
depends_on: []
tags:
  - repomedic
  - phase-1
  - code
---

# Phase 1 — Repository inspection and test execution

## Tasks

- Validate a user-selected repository path
- Detect Git status, branch, and existing modifications
- Identify Python project metadata and test configuration
- Implement ignore/exclusion rules
- Build a controlled test runner with timeouts and output limits
- Capture structured execution results

## Acceptance criteria

- Invalid paths are rejected
- Pre-existing modifications are recorded and never overwritten
- A known passing and failing fixture are distinguished correctly
- Timeouts and non-zero exit codes are reported accurately
- Tests can run without a model API key

## Scope

- `src/repomedic/repository/inspector.py`
- `src/repomedic/repository/git.py`
- `src/repomedic/repository/exclusions.py`
- `src/repomedic/execution/runner.py`
- `src/repomedic/execution/policies.py`
- `src/repomedic/execution/results.py`
- Tests under `tests/unit/` and `tests/integration/`

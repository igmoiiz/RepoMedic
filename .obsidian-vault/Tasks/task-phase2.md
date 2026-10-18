---
title: "Phase 2 — Python source index and fault localization"
type: task
status: pending
priority: high
depends_on:
  - task-phase1
tags:
  - repomedic
  - phase-2
  - code
---

# Phase 2 — Python source index and fault localization

## Tasks

- Parse Python files with `ast`
- Index modules, classes, functions, imports, and source ranges
- Connect traceback frames and failed assertions to indexed symbols
- Add optional coverage collection
- Add optional Git-diff signals
- Implement and document an interpretable location-ranking algorithm

## Acceptance criteria

- Source references point to valid paths and line ranges
- Parse errors are recorded without crashing the whole investigation
- Ranking is deterministic for identical evidence and configuration
- Unit tests cover nested functions, imports, syntax errors, and excluded paths

## Scope

- `src/repomedic/analysis/python_index.py`
- `src/repomedic/analysis/fault_localization.py`
- `src/repomedic/analysis/evidence.py`

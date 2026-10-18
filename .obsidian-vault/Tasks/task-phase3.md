---
title: "Phase 3 — Evidence ledger and hypothesis engine"
type: task
status: completed
priority: high
depends_on:
  - task-phase2
tags:
  - repomedic
  - phase-3
  - code
---

# Phase 3 — Evidence ledger and hypothesis engine

## Tasks

- Define typed models for evidence, hypotheses, experiments, and status transitions
- Persist events in SQLite
- Add a provider-neutral model interface
- Generate hypotheses grounded in collected evidence
- Validate model outputs and reject unsupported evidence references
- Add bounded experiment selection and execution

## Acceptance criteria

- Every diagnosis claim can be traced to evidence or is labeled as inference
- Invalid model output cannot crash or bypass policy
- The system can return `INCONCLUSIVE`
- Time, experiment, output, and model-call budgets are enforced
- Provider failures are recoverable and clearly reported

## Scope

- `src/repomedic/core/models.py`
- `src/repomedic/core/state_machine.py`
- `src/repomedic/core/events.py`
- `src/repomedic/diagnosis/hypotheses.py`
- `src/repomedic/diagnosis/experiments.py`
- `src/repomedic/models/adapter.py`
- `src/repomedic/storage/database.py`
- `src/repomedic/storage/repositories.py`

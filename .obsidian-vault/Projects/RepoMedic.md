---
title: RepoMedic
type: project
status: active
priority: high
created: 2026-10-18
tags:
  - repomedic
  - project
---

# RepoMedic

Python-first, local-first debugging intelligence platform. Investigates reproducible failures, constructs evidence-backed root-cause explanations, and presents hypotheses and experiments to a developer.

## Key documents

- [[MASTER]] — Operating contract
- [[project]] — Product scope
- [[architecture]] — Component boundaries
- [[security]] — Threat model
- [[plan]] — Milestones
- [[DECISIONS]] — Design decisions log

## Non-negotiable invariants

1. Never claim tests passed unless actually run
2. Never treat LLM output as authoritative evidence
3. Never apply patches without explicit approval
4. Never overwrite user changes
5. Never execute arbitrary model-generated commands
6. Never send repo contents to remote model silently
7. Never index secret files
8. Never use unbounded loops
9. Never suppress real errors
10. Never weaken tests to pass
11. Never fabricate results
12. Never make broad unrelated refactors
13. Never create empty abstractions
14. Never claim bug-free

## Current status

**Phase:** 0 (foundation) complete
**Next:** Phase 1 — Repository inspection and test execution
**Stack:** Python 3.12, pydantic, typer, hatchling, pytest, ruff, mypy
**Repo:** `D:\WorkSpace\SaaS Projects\RepoMedic`

## Success criteria

- Deterministic test fixtures with known faulty locations
- Baseline comparison vs traceback-only
- Top-1 / top-5 fault localization
- Diagnosis correctness separate from repair success
- Regression rate, runtime, model calls, cost
- End-to-end demo without fabricated results

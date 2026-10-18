---
title: "Phase 6 — Benchmark, reliability, and release"
type: task
status: pending
priority: low
depends_on:
  - task-phase5
tags:
  - repomedic
  - phase-6
  - code
---

# Phase 6 — Benchmark, reliability, and release

## Tasks

- Create a fixture set with known bugs and expected behavior
- Compare with traceback-only and basic LLM baselines
- Measure top-1/top-5 localization, root-cause correctness, repair verification, regression rate, latency, and cost
- Add adversarial security tests
- Profile memory and runtime
- Document limitations and reproducible benchmark commands

## Acceptance criteria

- Results can be reproduced from documented commands
- Baseline and RepoMedic use the same test cases
- Metrics are reported without cherry-picking
- No unmeasured performance claims appear in documentation
- Known limitations and residual risks are published

## Scope

- `tests/fixtures/buggy_projects/`
- `docs/benchmark.md`
- `docs/limitations.md`

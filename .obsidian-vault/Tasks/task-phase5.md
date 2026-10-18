---
title: "Phase 5 — Patch proposal and approval"
type: task
status: pending
priority: medium
depends_on:
  - task-phase4
tags:
  - repomedic
  - phase-5
  - code
---

# Phase 5 — Patch proposal and approval

## Tasks

- Create an isolated Git worktree for patching
- Generate a unified diff
- Validate patch paths and changed-file policy
- Run targeted verification in the isolated workspace
- Implement explicit approval and safe application
- Detect repository changes that invalidate a prepared patch

## Acceptance criteria

- The original working tree is unchanged before approval
- Full diff is visible before approval
- No patch is applied without a separate explicit approval
- Failed tests prevent the patch from being labeled verified
- Pre-existing changes survive all workflows

## Scope

- `src/repomedic/patching/worktree.py`
- `src/repomedic/patching/diff.py`
- `src/repomedic/patching/verification.py`

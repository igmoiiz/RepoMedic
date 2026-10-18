---
title: "Phase 4 — Diagnostic report and local UI"
type: task
status: completed
priority: medium
depends_on:
  - task-phase3
tags:
  - repomedic
  - phase-4
  - code
---

# Phase 4 — Diagnostic report and local UI

## Tasks

- Add a local FastAPI service
- Build a React/TypeScript UI
- Show session status, timeline, source references, hypotheses, and evidence graph
- Stream or poll structured investigation events
- Add report export with secret-aware redaction

## Acceptance criteria

- The entire diagnosis is viewable without reading raw logs
- Every source reference resolves correctly
- Failed and incomplete investigations are visible
- API is loopback-bound by default and state-changing actions are protected
- UI does not fabricate results when the backend fails

## Scope

- `src/repomedic/api/`
- `src/repomedic/diagnosis/report.py`
- `src/repomedic/cli.py`
- `frontend/` (React + TypeScript + Vite)

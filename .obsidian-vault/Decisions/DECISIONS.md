# RepoMedic — Decisions Log

---

## 2026-10-18 — Phase 0 foundation committed

**Context:** Initial project setup. Need to establish stack, tooling, and invariants before implementation.

**Decision:** Python 3.12 baseline, hatchling build backend, pydantic for typed models, typer for CLI, pytest/ruff/mypy for quality gates. Single root `pyproject.toml`, single root `.venv`.

**Alternatives considered:**
- setuptools instead of hatchling — hatchling is simpler and faster
- click instead of typer — typer is lighter and pydantic-native
- poetry for dependency management — overkill for MVP scope

**Conventions chosen:**
- Line length: 100 (ruff)
- Double quotes, space indent (ruff format)
- Strict mypy
- Test path: `tests/`, source path: `src/repomedic/`

**Consequences:** All future dependencies must be declared in `pyproject.toml`. No global installs. Strict type checking from day one.

# Architecture Decision Log

Record material technical decisions here.

## ADR-0001 — Python-first, local-first diagnostic MVP
- Status: Accepted as initial direction
- Decision: Build a Python-first local debugging intelligence tool; prioritize evidence-backed diagnosis before repair automation.
- Rationale: Keeps the first release focused and allows deterministic testing of core behavior.
- Consequences: Multi-language support and remote execution are out of scope initially.

## ADR-0002 — Root virtual environment
- Status: Accepted as initial direction
- Decision: Use one root `.venv` and one root `pyproject.toml` for Python dependencies in the MVP.
- Rationale: Simple, reproducible setup with fewer dependency-management boundaries.
- Consequences: Add a separately managed backend environment only if later requirements justify it.

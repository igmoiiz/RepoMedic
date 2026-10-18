# RepoMedic

RepoMedic is a Python-first, local-first debugging intelligence project. It aims to investigate reproducible failures, build evidence-backed root-cause explanations, and present diagnostic reports before proposing code changes.

## Status

Planning and repository foundation. The diagnostic engine is not implemented by these documents alone. Do not represent planned features as available functionality.

## Start here

1. Read `AGENTS.md`.
2. Read `MASTER.md`.
3. Read `project.md`, `architecture.md`, `security.md`, and `plan.md`.
4. Follow Phase 0 in `plan.md`.

## Python environment

Use Python 3.12 and a root `.venv`. Example setup on Linux/macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run checks using the active `.venv`:

```bash
python -m pytest
python -m ruff check .
python -m ruff format --check .
python -m mypy src
```

These commands are intended setup/check commands; they are not evidence that tests already pass. The implementation must add the package entry point and tests before the full project is functional.

## OpenCode

The repository includes `AGENTS.md` and a minimal `opencode.json` referencing the project instructions. Confirm config compatibility with your installed OpenCode version before relying on optional settings. Do not put API keys in the config file.

## Security warning

A Python virtual environment isolates dependencies; it does not sandbox code. Do not run tests from untrusted repositories on your host without a suitable isolation boundary.

"""Integration tests for the full inspection pipeline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from repomedic.execution.policies import ExecutionPolicy
from repomedic.execution.runner import ExecutionRunner
from repomedic.repository.inspector import Inspector


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )


def test_full_inspection_then_execution(tmp_path: Path) -> None:
    _init_repo(tmp_path)

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "fixture"\nversion = "0.1.0"\n'
        'requires-python = ">=3.12"\ndependencies = []\n'
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return 42\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text(
        "def test_run():\n    assert True\n"
    )
    (tmp_path / "pytest.ini").write_text("[pytest]\ntestpaths = tests\n")

    inspector = Inspector()
    result = inspector.inspect(tmp_path)

    assert result.is_valid
    assert result.git.is_git_repo
    assert result.project.name == "fixture"
    assert len(result.python_files) == 2
    assert "pytest.ini" in result.project.test_config

    runner = ExecutionRunner()
    exec_result = runner.run(
        [sys.executable, "-m", "pytest", "--tb=short", "-q"],
        cwd=tmp_path,
    )

    assert exec_result.exit_code == 0
    assert "1 passed" in exec_result.stdout or "no tests ran" in exec_result.stdout


def test_inspection_detects_dirty_state(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    (tmp_path / "tracked.py").write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "add tracked"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )

    (tmp_path / "tracked.py").write_text("x = 2\n")
    (tmp_path / "new_file.py").write_text("y = 3\n")

    inspector = Inspector()
    result = inspector.inspect(tmp_path)

    assert result.git.is_dirty
    assert "tracked.py" in result.git.modified_files
    assert "new_file.py" in result.git.untracked_files

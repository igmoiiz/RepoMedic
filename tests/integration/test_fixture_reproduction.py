"""Integration test reproducing a known failing fixture."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from repomedic.execution.runner import ExecutionRunner
from repomedic.repository.inspector import Inspector


def test_failing_fixture_reproduction(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "buggy.py").write_text(
        "def divide(a, b):\n"
        "    return a / b\n"
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_buggy.py").write_text(
        "from src.buggy import divide\n"
        "\n"
        "def test_divide_by_zero():\n"
        "    assert divide(1, 0) is not None\n"
    )

    inspector = Inspector()
    insp = inspector.inspect(tmp_path)
    assert insp.is_valid

    runner = ExecutionRunner()
    result = runner.run(
        [sys.executable, "-m", "pytest", "tests/", "--tb=short", "-q"],
        cwd=tmp_path,
    )

    assert result.exit_code != 0
    assert "ZeroDivisionError" in result.stdout


def test_passing_fixture_reproduction(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "good.py").write_text(
        "def add(a, b):\n"
        "    return a + b\n"
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_good.py").write_text(
        "from src.good import add\n"
        "\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n"
    )

    runner = ExecutionRunner()
    result = runner.run(
        [sys.executable, "-m", "pytest", "tests/", "--tb=short", "-q"],
        cwd=tmp_path,
    )

    assert result.exit_code == 0

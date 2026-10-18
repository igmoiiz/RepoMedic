"""Unit tests for execution runner."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from repomedic.execution.policies import ExecutionPolicy, PolicyViolation
from repomedic.execution.runner import ExecutionRunner


def test_run_simple_command(tmp_path: Path) -> None:
    runner = ExecutionRunner()
    result = runner.run([sys.executable, "-c", "print('hello')"], cwd=tmp_path)

    assert result.exit_code == 0
    assert "hello" in result.stdout
    assert result.stderr == ""
    assert result.duration_seconds >= 0
    assert not result.timed_out


def test_run_command_with_stderr(tmp_path: Path) -> None:
    runner = ExecutionRunner()
    result = runner.run(
        [sys.executable, "-c", "import sys; sys.stderr.write('error')"],
        cwd=tmp_path,
    )

    assert result.exit_code == 0
    assert "error" in result.stderr


def test_run_command_nonzero_exit(tmp_path: Path) -> None:
    runner = ExecutionRunner()
    result = runner.run(
        [sys.executable, "-c", "import sys; sys.exit(42)"],
        cwd=tmp_path,
    )

    assert result.exit_code == 42


def test_run_command_not_found(tmp_path: Path) -> None:
    runner = ExecutionRunner()
    result = runner.run(["nonexistent_command_xyz"], cwd=tmp_path)

    assert result.exit_code is None
    assert "Command not found" in result.stderr


def test_run_timeout(tmp_path: Path) -> None:
    policy = ExecutionPolicy(timeout_seconds=0.5)
    runner = ExecutionRunner(policy)
    result = runner.run(
        [sys.executable, "-c", "import time; time.sleep(10)"],
        cwd=tmp_path,
    )

    assert result.timed_out
    assert result.exit_code is not None


def test_run_output_truncation(tmp_path: Path) -> None:
    policy = ExecutionPolicy(max_output_bytes=100)
    runner = ExecutionRunner(policy)
    result = runner.run(
        [sys.executable, "-c", "print('x' * 10000)"],
        cwd=tmp_path,
    )

    assert result.output_truncated
    assert len(result.stdout.encode("utf-8")) <= 100


def test_run_policy_violation() -> None:
    policy = ExecutionPolicy(
        require_working_dir=True,
        allowed_working_dirs=[Path("/allowed")],
    )
    runner = ExecutionRunner(policy)

    with pytest.raises(PolicyViolation):
        runner.run([sys.executable, "--version"], cwd=Path("/not/allowed"))


def test_run_total_bytes_truncation_flag(tmp_path: Path) -> None:
    policy = ExecutionPolicy(max_output_bytes=5000, max_total_bytes=100)
    runner = ExecutionRunner(policy)
    result = runner.run(
        [sys.executable, "-c", "print('x' * 200)"],
        cwd=tmp_path,
    )

    assert result.output_truncated

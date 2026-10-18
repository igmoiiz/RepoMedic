"""Unit tests for execution policies."""

from __future__ import annotations

from pathlib import Path

import pytest

from repomedic.execution.policies import ExecutionPolicy, PolicyViolation


def test_default_policy() -> None:
    policy = ExecutionPolicy()
    assert policy.timeout_seconds == 60.0
    assert policy.max_output_bytes == 1_048_576
    assert policy.max_total_bytes == 2_097_152
    assert not policy.require_working_dir
    assert not policy.network_allowed


def test_validate_working_dir_not_required() -> None:
    policy = ExecutionPolicy(require_working_dir=False)
    assert policy.validate_working_dir(Path("/any/path"))


def test_validate_working_dir_allowed() -> None:
    allowed = Path("/allowed/dir")
    policy = ExecutionPolicy(
        require_working_dir=True,
        allowed_working_dirs=[allowed],
    )
    assert policy.validate_working_dir(allowed / "subdir")


def test_validate_working_dir_rejected() -> None:
    allowed = Path("/allowed/dir")
    policy = ExecutionPolicy(
        require_working_dir=True,
        allowed_working_dirs=[allowed],
    )
    assert not policy.validate_working_dir(Path("/other/dir"))


def test_policy_violation_is_exception() -> None:
    exc = PolicyViolation("test reason")
    assert exc.reason == "test reason"
    assert str(exc) == "test reason"

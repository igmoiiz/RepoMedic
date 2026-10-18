"""Unit tests for patch verification and approval tracking."""

from __future__ import annotations

import subprocess
from pathlib import Path

from repomedic.patching.verification import ApprovalTracker, PatchVerifier, VerificationResult


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )


def test_verification_result_to_dict() -> None:
    result = VerificationResult(
        success=True,
        exit_code=0,
        changed_files=["src/main.py"],
    )
    d = result.to_dict()
    assert d["success"] is True
    assert d["exit_code"] == 0
    assert d["changed_files"] == ["src/main.py"]


def test_verification_result_failure() -> None:
    result = VerificationResult(success=False, error="validation failed")
    assert result.success is False
    assert result.error == "validation failed"


def test_approval_tracker_initially_not_approved() -> None:
    tracker = ApprovalTracker()
    assert tracker.is_approved is False
    assert tracker.approval_timestamp is None


def test_approval_tracker_approve() -> None:
    tracker = ApprovalTracker()
    tracker.approve()
    assert tracker.is_approved is True
    assert tracker.approval_timestamp is not None


def test_approval_request_not_approved() -> None:
    tracker = ApprovalTracker()
    result = tracker.request_approval()
    assert result["approved"] is False


def test_approval_status_after_approve() -> None:
    tracker = ApprovalTracker()
    tracker.approve()
    status = tracker.get_status()
    assert status["approved"] is True
    assert status["approval_timestamp"] is not None


def test_check_repo_unchanged_clean(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    verifier = PatchVerifier(repo)
    assert verifier.check_repo_unchanged() is True


def test_check_repo_unchanged_dirty(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    (repo / "dirty.txt").write_text("dirty")
    verifier = PatchVerifier(repo)
    assert verifier.check_repo_unchanged() is False

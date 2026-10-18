"""Integration tests for the patch proposal pipeline."""

from __future__ import annotations

import subprocess
from pathlib import Path

from repomedic.patching.diff import get_changed_files, validate_patch_paths
from repomedic.patching.verification import ApprovalTracker, PatchVerifier
from repomedic.patching.worktree import WorktreeManager


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )


def test_worktree_patch_workflow(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("def run():\n    return 42\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "add app"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    mgr = WorktreeManager(repo)
    worktree_path = tmp_path / "patch-worktree"
    mgr.create(worktree_path, "repomedic-patch")

    (worktree_path / "src" / "app.py").write_text(
        "def run():\n    return 43\n", encoding="utf-8"
    )

    changed = get_changed_files(worktree_path)
    assert len(changed) == 1
    assert changed[0] == "src/app.py"

    validate_patch_paths(changed)

    verifier = PatchVerifier(repo)
    assert verifier.check_repo_unchanged() is True

    mgr.remove(worktree_path, force=True)
    assert not worktree_path.exists()


def test_approval_blocks_application(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    verifier = PatchVerifier(repo)
    result = verifier._worktree_mgr.get_status()
    assert result["clean"] is True

    tracker = ApprovalTracker()
    assert tracker.is_approved is False

    approval_response = tracker.request_approval()
    assert approval_response["approved"] is False


def test_worktree_removed_after_failure(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    (repo / "file.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(repo), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init file"],
        cwd=str(repo),
        capture_output=True,
        check=True,
    )

    mgr = WorktreeManager(repo)
    worktree_path = tmp_path / "wt"
    mgr.create(worktree_path, "patch-branch")

    (worktree_path / "file.py").write_text("x = 2\n", encoding="utf-8")

    changed = get_changed_files(worktree_path)
    validate_patch_paths(changed)

    mgr.remove(worktree_path, force=True)
    assert not worktree_path.exists()

    status = mgr.get_status()
    assert status["clean"] is True

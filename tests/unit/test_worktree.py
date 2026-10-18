"""Unit tests for worktree management."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from repomedic.patching.worktree import WorktreeError, WorktreeManager


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(path),
        capture_output=True,
        check=True,
    )


def test_create_worktree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    mgr = WorktreeManager(repo)
    worktree_path = tmp_path / "worktree"
    result = mgr.create(worktree_path, "test-branch")

    assert result == worktree_path
    assert worktree_path.exists()


def test_create_worktree_already_exists(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    mgr = WorktreeManager(repo)
    worktree_path = tmp_path / "worktree"
    worktree_path.mkdir()

    with pytest.raises(WorktreeError, match="already exists"):
        mgr.create(worktree_path, "test-branch")


def test_remove_worktree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    mgr = WorktreeManager(repo)
    worktree_path = tmp_path / "worktree"
    mgr.create(worktree_path, "test-branch")
    mgr.remove(worktree_path)

    assert not worktree_path.exists()


def test_remove_nonexistent_worktree(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    mgr = WorktreeManager(repo)
    mgr.remove(tmp_path / "nonexistent")


def test_list_worktrees(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    mgr = WorktreeManager(repo)
    worktrees = mgr.list_worktrees()
    assert len(worktrees) >= 1


def test_get_status_clean(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    mgr = WorktreeManager(repo)
    status = mgr.get_status()
    assert status["clean"] is True


def test_get_status_dirty(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    (repo / "dirty.txt").write_text("dirty")

    mgr = WorktreeManager(repo)
    status = mgr.get_status()
    assert status["clean"] is False
    assert "dirty.txt" in status["changed_files"]

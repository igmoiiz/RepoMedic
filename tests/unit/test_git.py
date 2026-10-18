"""Unit tests for git repository inspection."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from repomedic.repository.git import GitCommandError, get_git_status, is_git_repo


def test_is_git_repo_true(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    assert is_git_repo(tmp_path)


def test_is_git_repo_false(tmp_path: Path) -> None:
    assert not is_git_repo(tmp_path)


def test_get_git_status_not_a_repo(tmp_path: Path) -> None:
    status = get_git_status(tmp_path)
    assert not status.is_git_repo
    assert status.branch is None
    assert status.commit is None


def test_get_git_status_clean_repo(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )
    status = get_git_status(tmp_path)
    assert status.is_git_repo
    assert status.branch in ("main", "master")
    assert status.commit is not None
    assert not status.is_dirty


def test_get_git_status_dirty_repo(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
    )
    (tmp_path / "new_file.txt").write_text("content")
    (tmp_path / "untracked.py").write_text("print('hi')")

    status = get_git_status(tmp_path)
    assert status.is_dirty
    assert len(status.untracked_files) == 2

"""Git repository inspection."""

from __future__ import annotations

import subprocess
from pathlib import Path

from repomedic.core.models import GitStatus


class GitCommandError(Exception):
    """Raised when a git command fails unexpectedly."""

    def __init__(self, message: str, returncode: int | None = None) -> None:
        super().__init__(message)
        self.returncode = returncode


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the completed process."""
    try:
        return subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            shell=False,
        )
    except FileNotFoundError as e:
        raise GitCommandError("git executable not found") from e
    except subprocess.TimeoutExpired as e:
        raise GitCommandError("git command timed out") from e


def is_git_repo(path: Path) -> bool:
    """Check if the given path is inside a git repository."""
    try:
        result = _run_git(["rev-parse", "--git-dir"], path)
        return result.returncode == 0
    except GitCommandError:
        return False


def get_git_status(path: Path) -> GitStatus:
    """Get the git status of the repository at the given path."""
    if not is_git_repo(path):
        return GitStatus(is_git_repo=False)

    try:
        branch_result = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], path)
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None

        commit_result = _run_git(["rev-parse", "HEAD"], path)
        commit = commit_result.stdout.strip() if commit_result.returncode == 0 else None

        status_result = _run_git(["status", "--porcelain"], path)
        lines = status_result.stdout.strip().splitlines() if status_result.returncode == 0 else []

        modified: list[str] = []
        untracked: list[str] = []
        for line in lines:
            if not line:
                continue
            status_code = line[:2]
            filename = line[2:].strip()
            if "??" in status_code:
                untracked.append(filename)
            else:
                modified.append(filename)

        return GitStatus(
            is_git_repo=True,
            branch=branch,
            commit=commit,
            is_dirty=bool(lines),
            modified_files=modified,
            untracked_files=untracked,
        )
    except GitCommandError:
        return GitStatus(is_git_repo=True)

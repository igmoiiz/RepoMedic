"""Git worktree management for isolated patch work."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class WorktreeError(Exception):
    pass


class WorktreeManager:
    """Manages an isolated Git worktree for patch operations."""

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root.resolve()

    def create(self, worktree_path: Path, branch_name: str) -> Path:
        if worktree_path.exists():
            raise WorktreeError(f"Worktree path already exists: {worktree_path}")

        try:
            subprocess.run(
                ["git", "worktree", "add", str(worktree_path), "-b", branch_name],
                cwd=str(self._repo_root),
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
                shell=False,
            )
        except subprocess.CalledProcessError as e:
            raise WorktreeError(f"Failed to create worktree: {e.stderr}") from e
        except subprocess.TimeoutExpired as e:
            raise WorktreeError("Worktree creation timed out") from e
        except FileNotFoundError as e:
            raise WorktreeError("git executable not found") from e

        return worktree_path

    def remove(self, worktree_path: Path, force: bool = False) -> None:
        if not worktree_path.exists():
            return

        args = ["git", "worktree", "remove"]
        if force:
            args.append("--force")
        args.append(str(worktree_path))

        try:
            subprocess.run(
                args,
                cwd=str(self._repo_root),
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
                shell=False,
            )
        except subprocess.CalledProcessError as e:
            raise WorktreeError(f"Failed to remove worktree: {e.stderr}") from e

    def list_worktrees(self) -> list[dict[str, str]]:
        try:
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                cwd=str(self._repo_root),
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
                shell=False,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

        worktrees: list[dict[str, str]] = []
        current: dict[str, str] = {}
        for line in result.stdout.splitlines():
            if not line:
                if current:
                    worktrees.append(current)
                    current = {}
                continue
            if " " in line:
                key, value = line.split(" ", 1)
                current[key] = value
        if current:
            worktrees.append(current)
        return worktrees

    def get_status(self) -> dict[str, Any]:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self._repo_root),
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
                shell=False,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {"clean": False, "error": "git status failed"}

        lines = [l for l in result.stdout.strip().splitlines() if l]
        return {
            "clean": len(lines) == 0,
            "changed_files": [l[3:] for l in lines],
        }

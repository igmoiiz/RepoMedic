"""Patch verification in isolated workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from repomedic.execution.policies import ExecutionPolicy
from repomedic.execution.runner import ExecutionRunner
from repomedic.patching.diff import DiffError, generate_diff, get_changed_files, validate_patch_paths
from repomedic.patching.worktree import WorktreeError, WorktreeManager


class VerificationResult:
    def __init__(
        self,
        success: bool,
        exit_code: int | None = None,
        stdout: str = "",
        stderr: str = "",
        changed_files: list[str] | None = None,
        error: str | None = None,
    ) -> None:
        self.success = success
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.changed_files = changed_files or []
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "changed_files": self.changed_files,
            "error": self.error,
        }


class PatchVerifier:
    """Verifies patches in an isolated Git worktree."""

    def __init__(
        self,
        repo_root: Path,
        test_command: list[str] | None = None,
        allowed_paths: list[str] | None = None,
    ) -> None:
        self._repo_root = repo_root.resolve()
        self._worktree_mgr = WorktreeManager(self._repo_root)
        self._test_command = test_command
        self._allowed_paths = allowed_paths
        self._runner = ExecutionRunner(ExecutionPolicy(timeout_seconds=120.0))

    def verify_in_worktree(
        self, worktree_path: Path, branch_name: str = "repomedic-patch"
    ) -> VerificationResult:
        try:
            self._worktree_mgr.create(worktree_path, branch_name)
        except WorktreeError as e:
            return VerificationResult(success=False, error=str(e))

        try:
            changed = get_changed_files(worktree_path)
            if not changed:
                return VerificationResult(success=False, error="No changes in worktree")

            try:
                validate_patch_paths(changed, self._allowed_paths)
            except Exception as e:
                return VerificationResult(
                    success=False,
                    changed_files=changed,
                    error=f"Patch validation failed: {e}",
                )

            if self._test_command:
                result = self._runner.run(self._test_command, cwd=worktree_path)
                return VerificationResult(
                    success=result.exit_code == 0,
                    exit_code=result.exit_code,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    changed_files=changed,
                )

            return VerificationResult(success=True, changed_files=changed)

        except DiffError as e:
            return VerificationResult(success=False, error=str(e))

    def check_repo_unchanged(self) -> bool:
        status = self._worktree_mgr.get_status()
        return status.get("clean", False)

    def cleanup(self, worktree_path: Path) -> None:
        self._worktree_mgr.remove(worktree_path, force=True)


class ApprovalTracker:
    """Tracks explicit approval state for patch application."""

    def __init__(self) -> None:
        self._approved: bool = False
        self._approval_timestamp: str | None = None

    def request_approval(self) -> dict[str, Any]:
        return {
            "approved": False,
            "message": "Patch requires explicit user approval before application",
        }

    def approve(self) -> None:
        from datetime import datetime, timezone

        self._approved = True
        self._approval_timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def is_approved(self) -> bool:
        return self._approved

    @property
    def approval_timestamp(self) -> str | None:
        return self._approval_timestamp

    def get_status(self) -> dict[str, Any]:
        return {
            "approved": self._approved,
            "approval_timestamp": self._approval_timestamp,
        }

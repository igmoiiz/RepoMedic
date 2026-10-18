"""Execution policies for controlled command execution."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class ExecutionPolicy(BaseModel):
    """Policy configuration for command execution."""

    timeout_seconds: float = Field(default=60.0, gt=0)
    max_output_bytes: int = Field(default=1_048_576, gt=0)
    max_total_bytes: int = Field(default=2_097_152, gt=0)
    allowed_working_dirs: list[Path] = Field(default_factory=list)
    require_working_dir: bool = False
    network_allowed: bool = False
    env_allowlist: list[str] | None = None

    def validate_working_dir(self, cwd: Path) -> bool:
        """Check if the working directory is allowed."""
        if not self.require_working_dir:
            return True
        resolved = cwd.resolve()
        return any(
            resolved.is_relative_to(allowed.resolve())
            for allowed in self.allowed_working_dirs
        )


class PolicyViolation(Exception):
    """Raised when a command violates the execution policy."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason

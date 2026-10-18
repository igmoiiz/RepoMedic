"""Controlled command execution with timeouts and output limits."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from repomedic.core.models import ExecutionResult
from repomedic.execution.policies import ExecutionPolicy, PolicyViolation
from repomedic.execution.results import truncate_output


class ExecutionRunner:
    """Runs commands with controlled timeouts, output limits, and policy checks."""

    def __init__(self, policy: ExecutionPolicy | None = None) -> None:
        self._policy = policy or ExecutionPolicy()

    def run(self, command: list[str], cwd: Path | None = None) -> ExecutionResult:
        """Run a command and return a structured ExecutionResult."""
        working_dir = cwd.resolve() if cwd else Path.cwd()

        if self._policy.require_working_dir and not self._policy.validate_working_dir(working_dir):
            raise PolicyViolation(
                f"Working directory {working_dir} is not in the allowed list"
            )

        env = self._build_env()
        stdout_parts: list[str] = []
        stderr_parts: list[str] = []
        total_bytes = 0
        timed_out = False
        cancelled = False
        output_truncated = False
        exit_code: int | None = None

        start = time.monotonic()
        process: subprocess.Popen[str] | None = None

        try:
            process = subprocess.Popen(
                command,
                cwd=str(working_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                shell=False,
            )

            assert process.stdout is not None
            assert process.stderr is not None

            try:
                stdout_data, stderr_data = process.communicate(
                    timeout=self._policy.timeout_seconds
                )
            except subprocess.TimeoutExpired:
                timed_out = True
                self._kill_process(process)
                stdout_data, stderr_data = process.communicate()

            stdout_truncated, stdout_was_truncated = truncate_output(
                stdout_data or "", self._policy.max_output_bytes
            )
            stderr_truncated, stderr_was_truncated = truncate_output(
                stderr_data or "", self._policy.max_output_bytes
            )

            output_truncated = stdout_was_truncated or stderr_was_truncated
            stdout_parts.append(stdout_truncated)
            stderr_parts.append(stderr_truncated)
            total_bytes = len(stdout_truncated.encode("utf-8")) + len(
                stderr_truncated.encode("utf-8")
            )
            exit_code = process.returncode

        except FileNotFoundError:
            stderr_parts.append(f"Command not found: {command[0]}")
        except PermissionError:
            stderr_parts.append(f"Permission denied: {command[0]}")

        duration = time.monotonic() - start

        return ExecutionResult(
            command=command,
            cwd=working_dir,
            exit_code=exit_code,
            stdout="".join(stdout_parts),
            stderr="".join(stderr_parts),
            duration_seconds=round(duration, 3),
            timed_out=timed_out,
            cancelled=cancelled,
            output_truncated=output_truncated or total_bytes > self._policy.max_total_bytes,
        )

    def _build_env(self) -> dict[str, str]:
        """Build a clean environment for subprocess execution."""
        if self._policy.env_allowlist is None:
            return dict(os.environ)

        return {
            key: os.environ[key]
            for key in self._policy.env_allowlist
            if key in os.environ
        }

    @staticmethod
    def _kill_process(process: subprocess.Popen[str]) -> None:
        """Kill a process and its children."""
        try:
            process.kill()
        except ProcessLookupError:
            pass

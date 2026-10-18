"""Experiment engine: bounded experiment selection and execution."""

from __future__ import annotations

import uuid
from typing import Any

from repomedic.execution.policies import ExecutionPolicy, PolicyViolation
from repomedic.execution.runner import ExecutionRunner


class BudgetExceeded(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ExperimentEngine:
    def __init__(
        self,
        runner: ExecutionRunner | None = None,
        max_experiments: int = 5,
        max_total_runtime_seconds: float = 300.0,
    ) -> None:
        self._runner = runner or ExecutionRunner()
        self._max_experiments = max_experiments
        self._max_total_runtime = max_total_runtime_seconds
        self._experiments_run = 0
        self._total_runtime = 0.0

    def run_experiment(
        self,
        intent: str,
        command: list[str],
        investigation_id: str,
    ) -> dict[str, Any]:
        if self._experiments_run >= self._max_experiments:
            raise BudgetExceeded(
                f"Maximum number of experiments ({self._max_experiments}) reached"
            )

        exp_id = str(uuid.uuid4())
        self._experiments_run += 1

        try:
            result = self._runner.run(command)
        except PolicyViolation as e:
            return {
                "id": exp_id,
                "investigation_id": investigation_id,
                "intent": intent,
                "command": command,
                "result_summary": f"Policy violation: {e.reason}",
                "success": False,
            }

        self._total_runtime += result.duration_seconds

        if self._total_runtime > self._max_total_runtime:
            raise BudgetExceeded(
                f"Total runtime budget ({self._max_total_runtime}s) exceeded"
            )

        return {
            "id": exp_id,
            "investigation_id": investigation_id,
            "intent": intent,
            "command": command,
            "result_summary": f"exit={result.exit_code} duration={result.duration_seconds:.2f}s",
            "success": result.exit_code == 0,
            "exit_code": result.exit_code,
            "stdout": result.stdout[:1000] if result.stdout else "",
            "stderr": result.stderr[:1000] if result.stderr else "",
            "duration_seconds": result.duration_seconds,
        }

    @property
    def experiments_run(self) -> int:
        return self._experiments_run

    @property
    def total_runtime(self) -> float:
        return self._total_runtime

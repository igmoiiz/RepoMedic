"""Unit tests for experiment engine."""

from __future__ import annotations

import sys

import pytest

from repomedic.diagnosis.experiments import BudgetExceeded, ExperimentEngine


def test_run_experiment_success() -> None:
    engine = ExperimentEngine()
    result = engine.run_experiment(
        "Check Python version",
        [sys.executable, "--version"],
        "inv-1",
    )

    assert result["success"] is True
    assert result["exit_code"] == 0
    assert result["investigation_id"] == "inv-1"
    assert result["intent"] == "Check Python version"


def test_run_experiment_failure() -> None:
    engine = ExperimentEngine()
    result = engine.run_experiment(
        "Failing command",
        [sys.executable, "-c", "import sys; sys.exit(1)"],
        "inv-1",
    )

    assert result["success"] is False
    assert result["exit_code"] == 1


def test_budget_max_experiments() -> None:
    engine = ExperimentEngine(max_experiments=2)

    engine.run_experiment("Test 1", [sys.executable, "--version"], "inv-1")
    engine.run_experiment("Test 2", [sys.executable, "--version"], "inv-1")

    with pytest.raises(BudgetExceeded, match="Maximum number of experiments"):
        engine.run_experiment("Test 3", [sys.executable, "--version"], "inv-1")


def test_experiments_run_count() -> None:
    engine = ExperimentEngine()
    engine.run_experiment("Test", [sys.executable, "--version"], "inv-1")

    assert engine.experiments_run == 1


def test_total_runtime_tracked() -> None:
    engine = ExperimentEngine()
    engine.run_experiment("Test", [sys.executable, "--version"], "inv-1")

    assert engine.total_runtime >= 0


def test_result_truncation() -> None:
    engine = ExperimentEngine()
    result = engine.run_experiment(
        "Long output",
        [sys.executable, "-c", "print('x' * 5000)"],
        "inv-1",
    )

    assert len(result["stdout"]) <= 1000

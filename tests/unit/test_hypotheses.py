"""Unit tests for hypothesis engine."""

from __future__ import annotations

import pytest

from repomedic.diagnosis.hypotheses import HypothesisEngine


def test_generate_from_traceback_evidence() -> None:
    engine = HypothesisEngine()
    evidence = [
        {
            "source": "traceback",
            "file_path": "src/app.py",
            "line_start": 10,
            "line_end": 10,
            "description": "ZeroDivisionError in divide()",
        }
    ]
    results = engine.generate(evidence, "inv-1")

    assert len(results) >= 1
    assert results[0]["investigation_id"] == "inv-1"
    assert results[0]["status"] == "candidate"
    assert results[0]["confidence"] in ("low", "medium", "high")


def test_generate_empty_evidence() -> None:
    engine = HypothesisEngine()
    results = engine.generate([], "inv-1")

    assert len(results) == 1
    assert "Insufficient" in results[0]["claim"]


def test_update_status_valid() -> None:
    engine = HypothesisEngine()
    hypothesis = {
        "id": "hyp-1",
        "status": "candidate",
        "confidence": "low",
    }
    result = engine.update_status(hypothesis, "supported", "high")

    assert result["status"] == "supported"
    assert result["confidence"] == "high"


def test_update_status_invalid() -> None:
    engine = HypothesisEngine()
    hypothesis = {"id": "hyp-1", "status": "candidate", "confidence": "low"}

    with pytest.raises(ValueError, match="Invalid hypothesis status"):
        engine.update_status(hypothesis, "bogus_status")


def test_update_confidence_invalid() -> None:
    engine = HypothesisEngine()
    hypothesis = {"id": "hyp-1", "status": "candidate", "confidence": "low"}

    with pytest.raises(ValueError, match="Invalid confidence level"):
        engine.update_status(hypothesis, "supported", "very_high")


def test_generate_multiple_hypotheses() -> None:
    engine = HypothesisEngine()
    evidence = [
        {
            "source": "traceback",
            "file_path": "src/a.py",
            "line_start": 10,
            "line_end": 10,
            "description": "Error A",
        },
        {
            "source": "test_assertion",
            "file_path": "tests/test_a.py",
            "line_start": 5,
            "line_end": 5,
            "description": "Assertion B",
        },
    ]
    results = engine.generate(evidence, "inv-1")

    assert len(results) >= 2
    ranks = [r["rank"] for r in results]
    assert ranks == [1, 2]

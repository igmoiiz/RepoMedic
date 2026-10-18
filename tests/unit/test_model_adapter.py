"""Unit tests for provider-neutral model adapter."""

from __future__ import annotations

from repomedic.models.adapter import DeterministicAdapter, ModelResponse


def test_generate_hypotheses_from_traceback() -> None:
    adapter = DeterministicAdapter()
    evidence = [
        {
            "source": "traceback",
            "file_path": "src/app.py",
            "line_start": 10,
            "line_end": 10,
            "description": "ZeroDivisionError",
        }
    ]
    response = adapter.generate_hypotheses(evidence)

    assert len(response.hypotheses) >= 1
    assert "ZeroDivisionError" in response.hypotheses[0].claim


def test_generate_hypotheses_from_assertion() -> None:
    adapter = DeterministicAdapter()
    evidence = [
        {
            "source": "test_assertion",
            "file_path": "tests/test_app.py",
            "line_start": 5,
            "line_end": 5,
            "description": "assert 1 == 2",
        }
    ]
    response = adapter.generate_hypotheses(evidence)

    assert len(response.hypotheses) >= 1
    assert "assert 1 == 2" in response.hypotheses[0].claim


def test_generate_hypotheses_empty_evidence() -> None:
    adapter = DeterministicAdapter()
    response = adapter.generate_hypotheses([])

    assert len(response.hypotheses) == 1
    assert "Insufficient evidence" in response.hypotheses[0].claim


def test_generate_respects_max_hypotheses() -> None:
    adapter = DeterministicAdapter()
    evidence = [
        {
            "source": "traceback",
            "file_path": f"src/file{i}.py",
            "line_start": i * 10,
            "line_end": i * 10,
            "description": f"Error {i}",
        }
        for i in range(10)
    ]
    response = adapter.generate_hypotheses(evidence, max_hypotheses=2)

    assert len(response.hypotheses) <= 2


def test_validate_output_valid_json() -> None:
    adapter = DeterministicAdapter()
    json_str = '{"hypotheses": [{"claim": "test", "confidence": "high"}]}'
    result = adapter.validate_output(json_str)

    assert len(result.hypotheses) == 1
    assert result.hypotheses[0].claim == "test"


def test_validate_output_invalid_json() -> None:
    adapter = DeterministicAdapter()
    result = adapter.validate_output("not valid json")

    assert len(result.hypotheses) == 0
    assert result.raw_output == "not valid json"

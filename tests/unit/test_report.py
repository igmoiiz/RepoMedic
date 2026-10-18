"""Unit tests for diagnostic report generation."""

from __future__ import annotations

from repomedic.diagnosis.report import redact_secrets, ReportGenerator


def test_redact_secrets_basic() -> None:
    text = "Error occurred"
    assert redact_secrets(text) == text


def test_redact_secrets_api_key() -> None:
    text = 'api_key = "sk-abc123def456"'
    result = redact_secrets(text)
    assert "[REDACTED]" in result


def test_redact_secrets_private_key() -> None:
    text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEow=="
    result = redact_secrets(text)
    assert "[REDACTED]" in result


def test_redact_secrets_token() -> None:
    text = "token=abcdef1234567890"
    result = redact_secrets(text)
    assert "[REDACTED]" in result


def test_report_generation_structure() -> None:
    gen = ReportGenerator()
    investigation = {
        "id": "inv-1",
        "repository_root": "/repo",
        "state": "ANALYSIS",
        "created_at": "2026-10-18T00:00:00Z",
    }
    events = [{"timestamp": "2026-10-18T00:01:00Z", "event_type": "STATE_CHANGED"}]
    evidence = [{"source": "traceback", "file_path": "src/app.py", "line_start": 10, "description": "Error"}]
    hypotheses = [{"rank": 1, "claim": "Divide by zero", "status": "candidate", "confidence": "medium"}]

    report = gen.generate(investigation, events, evidence, hypotheses)

    assert report["investigation_id"] == "inv-1"
    assert report["evidence_count"] == 1
    assert report["hypothesis_count"] == 1
    assert report["event_count"] == 1
    assert report["redacted"] is True
    assert "Diagnostic Report" in report["report_markdown"]


def test_report_redacts_secrets() -> None:
    gen = ReportGenerator()
    evidence = [{"source": "execution", "file_path": "src/app.py", "line_start": 1, "description": "api_key=secret123"}]

    report = gen.generate(
        {"id": "inv-1", "state": "ANALYSIS", "repository_root": "/r", "created_at": "now"},
        [],
        evidence,
        [],
    )

    assert "[REDACTED]" in report["report_markdown"]


def test_to_json() -> None:
    gen = ReportGenerator()
    report = {"key": "value"}
    json_str = gen.to_json(report)
    assert '"key": "value"' in json_str

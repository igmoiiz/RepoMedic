"""Unit tests for execution result helpers."""

from __future__ import annotations

from repomedic.execution.results import truncate_output


def test_truncate_output_no_truncation_needed() -> None:
    text = "hello world"
    result, truncated = truncate_output(text, 100)
    assert result == text
    assert not truncated


def test_truncate_output_truncates_long_text() -> None:
    text = "a" * 1000
    result, truncated = truncate_output(text, 100)
    assert len(result.encode("utf-8")) <= 100
    assert truncated


def test_truncate_output_unicode_boundary() -> None:
    text = "é" * 100
    result, truncated = truncate_output(text, 50)
    assert len(result.encode("utf-8")) <= 50
    assert truncated


def test_truncate_output_empty_string() -> None:
    result, truncated = truncate_output("", 100)
    assert result == ""
    assert not truncated

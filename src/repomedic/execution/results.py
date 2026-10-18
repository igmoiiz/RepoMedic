"""Execution result helpers."""

from __future__ import annotations

from repomedic.core.models import ExecutionResult


def truncate_output(text: str, max_bytes: int) -> tuple[str, bool]:
    """Truncate output text to fit within max_bytes when encoded as UTF-8.

    Returns the truncated text and whether truncation occurred.
    """
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text, False

    truncated = encoded[:max_bytes].decode("utf-8", errors="ignore")
    return truncated, True

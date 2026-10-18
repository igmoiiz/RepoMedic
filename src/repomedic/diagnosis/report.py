"""Diagnostic report generation with secret-aware redaction."""

from __future__ import annotations

import re
from typing import Any


SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|pwd)\s*[=:]\s*\S+"),
    re.compile(r"(?i)BEGIN\s+(RSA\s+)?PRIVATE\s+KEY"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]

REDACTION_PLACEHOLDER = "[REDACTED]"


def redact_secrets(text: str) -> str:
    result = text
    for pattern in SECRET_PATTERNS:
        result = pattern.sub(REDACTION_PLACEHOLDER, result)
    return result


class ReportGenerator:
    """Generates a diagnostic report from investigation data."""

    def generate(
        self,
        investigation: dict[str, Any],
        events: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
        hypotheses: list[dict[str, Any]],
    ) -> dict[str, Any]:
        lines: list[str] = []
        lines.append(f"# Diagnostic Report: {investigation.get('id', 'unknown')}")
        lines.append("")
        lines.append(f"**Repository:** {investigation.get('repository_root', 'unknown')}")
        lines.append(f"**State:** {investigation.get('state', 'unknown')}")
        lines.append(f"**Created:** {investigation.get('created_at', 'unknown')}")
        lines.append("")

        lines.append("## Timeline")
        lines.append("")
        for event in events:
            ts = event.get("timestamp", "?")
            etype = event.get("event_type", "?")
            lines.append(f"- `{ts}` — {etype}")
        lines.append("")

        lines.append("## Evidence")
        lines.append("")
        for ev in evidence:
            desc = redact_secrets(ev.get("description", ""))
            loc = ev.get("file_path", "?")
            line = ev.get("line_start", "?")
            source = ev.get("source", "?")
            lines.append(f"- `{source}` {loc}:{line} — {desc}")
        lines.append("")

        lines.append("## Hypotheses")
        lines.append("")
        for hyp in hypotheses:
            claim = redact_secrets(hyp.get("claim", ""))
            status = hyp.get("status", "?")
            confidence = hyp.get("confidence", "?")
            rank = hyp.get("rank", "?")
            lines.append(f"### #{rank} [{status}/{confidence}] {claim}")
            lines.append("")

        report_text = "\n".join(lines)

        return {
            "investigation_id": investigation.get("id", ""),
            "state": investigation.get("state", ""),
            "report_markdown": report_text,
            "evidence_count": len(evidence),
            "hypothesis_count": len(hypotheses),
            "event_count": len(events),
            "redacted": True,
        }

    def to_json(self, report: dict[str, Any]) -> str:
        import json

        return json.dumps(report, indent=2)

"""Data access layer for investigations, evidence, and hypotheses."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InvestigationRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(self, investigation_id: str, repository_root: str, state: str) -> None:
        now = _now()
        self._conn.execute(
            "INSERT INTO investigations (id, repository_root, state, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (investigation_id, repository_root, state, now, now),
        )
        self._conn.commit()

    def update_state(self, investigation_id: str, new_state: str) -> None:
        self._conn.execute(
            "UPDATE investigations SET state = ?, updated_at = ? WHERE id = ?",
            (new_state, _now(), investigation_id),
        )
        self._conn.commit()

    def get(self, investigation_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT id, repository_root, state, created_at, updated_at FROM investigations WHERE id = ?",
            (investigation_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "repository_root": row[1],
            "state": row[2],
            "created_at": row[3],
            "updated_at": row[4],
        }


class EventRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def append(
        self,
        investigation_id: str,
        event_type: str,
        payload: dict,
        sequence: int,
    ) -> None:
        self._conn.execute(
            "INSERT INTO events (investigation_id, event_type, timestamp, payload, sequence) VALUES (?, ?, ?, ?, ?)",
            (investigation_id, event_type, _now(), json.dumps(payload), sequence),
        )
        self._conn.commit()

    def get_events(self, investigation_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT event_type, timestamp, payload, sequence FROM events WHERE investigation_id = ? ORDER BY sequence",
            (investigation_id,),
        ).fetchall()
        return [
            {
                "event_type": r[0],
                "timestamp": r[1],
                "payload": json.loads(r[2]),
                "sequence": r[3],
            }
            for r in rows
        ]


class EvidenceRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(
        self,
        evidence_id: str,
        investigation_id: str,
        source: str,
        file_path: str,
        line_start: int | None,
        line_end: int | None,
        description: str,
        raw_excerpt: str | None = None,
    ) -> None:
        self._conn.execute(
            "INSERT INTO evidence (id, investigation_id, source, file_path, line_start, line_end, description, raw_excerpt, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (evidence_id, investigation_id, source, file_path, line_start, line_end, description, raw_excerpt, _now()),
        )
        self._conn.commit()

    def get_for_investigation(self, investigation_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id, source, file_path, line_start, line_end, description FROM evidence WHERE investigation_id = ?",
            (investigation_id,),
        ).fetchall()
        return [
            {
                "id": r[0],
                "source": r[1],
                "file_path": r[2],
                "line_start": r[3],
                "line_end": r[4],
                "description": r[5],
            }
            for r in rows
        ]


class HypothesisRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def add(
        self,
        hypothesis_id: str,
        investigation_id: str,
        claim: str,
        status: str,
        confidence: str,
        supporting_evidence: list[str],
        contradicting_evidence: list[str],
        candidate_locations: list[dict],
        experiment_proposal: str | None = None,
        rank: int = 0,
    ) -> None:
        now = _now()
        self._conn.execute(
            "INSERT INTO hypotheses (id, investigation_id, claim, status, confidence, supporting_evidence, contradicting_evidence, candidate_locations, experiment_proposal, rank, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                hypothesis_id,
                investigation_id,
                claim,
                status,
                confidence,
                json.dumps(supporting_evidence),
                json.dumps(contradicting_evidence),
                json.dumps(candidate_locations),
                experiment_proposal,
                rank,
                now,
                now,
            ),
        )
        self._conn.commit()

    def update_status(self, hypothesis_id: str, status: str, confidence: str) -> None:
        self._conn.execute(
            "UPDATE hypotheses SET status = ?, confidence = ?, updated_at = ? WHERE id = ?",
            (status, confidence, _now(), hypothesis_id),
        )
        self._conn.commit()

    def get_for_investigation(self, investigation_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT id, claim, status, confidence, rank FROM hypotheses WHERE investigation_id = ? ORDER BY rank",
            (investigation_id,),
        ).fetchall()
        return [
            {
                "id": r[0],
                "claim": r[1],
                "status": r[2],
                "confidence": r[3],
                "rank": r[4],
            }
            for r in rows
        ]

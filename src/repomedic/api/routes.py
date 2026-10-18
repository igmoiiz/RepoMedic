"""API routes for investigation management."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from repomedic.core.state_machine import InvestigationState
from repomedic.storage.database import get_connection, init_db
from repomedic.storage.repositories import (
    EvidenceRepository,
    EventRepository,
    HypothesisRepository,
    InvestigationRepository,
)


router = APIRouter()


class _AppState:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path


class _App:
    def __init__(self, db_path: Path | None = None) -> None:
        self.state = _AppState(db_path)


def _get_conn(db_path: Path | None = None):
    path = db_path or Path("data/repomedic.db")
    return get_connection(path)


@router.post("/investigations")
def create_investigation(payload: dict[str, Any]) -> dict[str, Any]:
    investigation_id = str(uuid.uuid4())
    repo_root = payload.get("repository_root", "")

    conn = init_db(Path("data/repomedic.db"))
    repo = InvestigationRepository(conn)
    repo.create(investigation_id, repo_root, InvestigationState.CREATED.value)

    return {
        "id": investigation_id,
        "repository_root": repo_root,
        "state": InvestigationState.CREATED.value,
    }


@router.get("/investigations/{investigation_id}")
def get_investigation(investigation_id: str) -> dict[str, Any]:
    conn = _get_conn()
    repo = InvestigationRepository(conn)
    result = repo.get(investigation_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Investigation not found")

    return result


@router.patch("/investigations/{investigation_id}/state")
def update_investigation_state(
    investigation_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    new_state = payload.get("state", "")

    try:
        state_enum = InvestigationState(new_state)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid state: {new_state}")

    conn = _get_conn()
    repo = InvestigationRepository(conn)
    repo.update_state(investigation_id, state_enum.value)

    return {"id": investigation_id, "state": state_enum.value}


@router.get("/investigations/{investigation_id}/events")
def get_investigation_events(investigation_id: str) -> list[dict[str, Any]]:
    conn = _get_conn()
    repo = EventRepository(conn)
    return repo.get_events(investigation_id)


@router.post("/investigations/{investigation_id}/evidence")
def add_evidence(investigation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    evidence_id = str(uuid.uuid4())

    conn = _get_conn()
    repo = EvidenceRepository(conn)
    repo.add(
        evidence_id,
        investigation_id,
        payload.get("source", ""),
        payload.get("file_path", ""),
        payload.get("line_start"),
        payload.get("line_end"),
        payload.get("description", ""),
        payload.get("raw_excerpt"),
    )

    return {"id": evidence_id, "investigation_id": investigation_id}


@router.get("/investigations/{investigation_id}/evidence")
def get_evidence(investigation_id: str) -> list[dict[str, Any]]:
    conn = _get_conn()
    repo = EvidenceRepository(conn)
    return repo.get_for_investigation(investigation_id)


@router.get("/investigations/{investigation_id}/hypotheses")
def get_hypotheses(investigation_id: str) -> list[dict[str, Any]]:
    conn = _get_conn()
    repo = HypothesisRepository(conn)
    return repo.get_for_investigation(investigation_id)


@router.patch("/hypotheses/{hypothesis_id}/status")
def update_hypothesis_status(
    hypothesis_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    conn = _get_conn()
    repo = HypothesisRepository(conn)
    repo.update_status(
        hypothesis_id,
        payload.get("status", ""),
        payload.get("confidence"),
    )

    return {"id": hypothesis_id, "status": payload.get("status")}

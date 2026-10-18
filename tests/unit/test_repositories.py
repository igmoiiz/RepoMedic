"""Unit tests for repository data access layer."""

from __future__ import annotations

from pathlib import Path

from repomedic.storage.database import init_db
from repomedic.storage.repositories import (
    EvidenceRepository,
    EventRepository,
    HypothesisRepository,
    InvestigationRepository,
)


def _make_conn(tmp_path: Path):
    return init_db(tmp_path / "test.db")


def test_investigation_crud(tmp_path: Path) -> None:
    conn = _make_conn(tmp_path)
    repo = InvestigationRepository(conn)

    repo.create("inv-1", "/repo", "CREATED")
    result = repo.get("inv-1")

    assert result is not None
    assert result["id"] == "inv-1"
    assert result["repository_root"] == "/repo"
    assert result["state"] == "CREATED"


def test_investigation_update_state(tmp_path: Path) -> None:
    conn = _make_conn(tmp_path)
    repo = InvestigationRepository(conn)

    repo.create("inv-1", "/repo", "CREATED")
    repo.update_state("inv-1", "ANALYSIS")

    result = repo.get("inv-1")
    assert result["state"] == "ANALYSIS"


def test_event_append_and_retrieve(tmp_path: Path) -> None:
    conn = _make_conn(tmp_path)
    inv_repo = InvestigationRepository(conn)
    event_repo = EventRepository(conn)

    inv_repo.create("inv-1", "/repo", "CREATED")
    event_repo.append("inv-1", "STATE_CHANGED", {"new_state": "ANALYSIS"}, 1)

    events = event_repo.get_events("inv-1")
    assert len(events) == 1
    assert events[0]["event_type"] == "STATE_CHANGED"
    assert events[0]["sequence"] == 1


def test_evidence_add_and_retrieve(tmp_path: Path) -> None:
    conn = _make_conn(tmp_path)
    inv_repo = InvestigationRepository(conn)
    ev_repo = EvidenceRepository(conn)

    inv_repo.create("inv-1", "/repo", "CREATED")
    ev_repo.add("ev-1", "inv-1", "traceback", "src/app.py", 10, 10, "Error here")

    results = ev_repo.get_for_investigation("inv-1")
    assert len(results) == 1
    assert results[0]["source"] == "traceback"
    assert results[0]["file_path"] == "src/app.py"


def test_hypothesis_add_and_retrieve(tmp_path: Path) -> None:
    conn = _make_conn(tmp_path)
    inv_repo = InvestigationRepository(conn)
    hyp_repo = HypothesisRepository(conn)

    inv_repo.create("inv-1", "/repo", "CREATED")
    hyp_repo.add(
        "hyp-1",
        "inv-1",
        "Division by zero",
        "candidate",
        "medium",
        ["ev-1"],
        [],
        [{"file_path": "src/app.py", "line_start": 10, "line_end": 10}],
        rank=1,
    )

    results = hyp_repo.get_for_investigation("inv-1")
    assert len(results) == 1
    assert results[0]["claim"] == "Division by zero"
    assert results[0]["status"] == "candidate"


def test_hypothesis_update_status(tmp_path: Path) -> None:
    conn = _make_conn(tmp_path)
    inv_repo = InvestigationRepository(conn)
    hyp_repo = HypothesisRepository(conn)

    inv_repo.create("inv-1", "/repo", "CREATED")
    hyp_repo.add(
        "hyp-1",
        "inv-1",
        "Test claim",
        "candidate",
        "low",
        [],
        [],
        [],
    )

    hyp_repo.update_status("hyp-1", "supported", "high")

    results = hyp_repo.get_for_investigation("inv-1")
    assert results[0]["status"] == "supported"
    assert results[0]["confidence"] == "high"

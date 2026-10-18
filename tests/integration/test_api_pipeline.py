"""Integration tests for API and report pipeline."""

from __future__ import annotations

from pathlib import Path

from repomedic.diagnosis.report import ReportGenerator
from repomedic.models.adapter import DeterministicAdapter
from repomedic.storage.database import init_db
from repomedic.storage.repositories import (
    EvidenceRepository,
    EventRepository,
    HypothesisRepository,
    InvestigationRepository,
)


def test_full_api_data_pipeline(tmp_path: Path) -> None:
    db_path = tmp_path / "api.db"
    conn = init_db(db_path)

    inv_repo = InvestigationRepository(conn)
    ev_repo = EventRepository(conn)
    evd_repo = EvidenceRepository(conn)
    hyp_repo = HypothesisRepository(conn)

    inv_repo.create("inv-api", "/test/repo", "ANALYSIS")
    ev_repo.append("inv-api", "STATE_CHANGED", {"new_state": "ANALYSIS"}, 1)
    evd_repo.add("ev-1", "inv-api", "traceback", "src/app.py", 10, 10, "ZeroDivisionError")

    stored_evidence = evd_repo.get_for_investigation("inv-api")

    from repomedic.diagnosis.hypotheses import HypothesisEngine

    engine = HypothesisEngine(DeterministicAdapter())
    hypotheses = engine.generate(stored_evidence, "inv-api")

    for hyp in hypotheses:
        hyp_repo.add(
            hyp["id"], hyp["investigation_id"], hyp["claim"], hyp["status"],
            hyp["confidence"], hyp["supporting_evidence"], hyp["contradicting_evidence"],
            hyp["candidate_locations"], hyp["experiment_proposal"], hyp["rank"],
        )

    investigation = inv_repo.get("inv-api")
    events = ev_repo.get_events("inv-api")
    evidence = evd_repo.get_for_investigation("inv-api")
    stored_hypotheses = hyp_repo.get_for_investigation("inv-api")

    gen = ReportGenerator()
    report = gen.generate(investigation, events, evidence, stored_hypotheses)

    assert report["investigation_id"] == "inv-api"
    assert report["state"] == "ANALYSIS"
    assert report["evidence_count"] >= 1
    assert report["hypothesis_count"] >= 1
    assert "Diagnostic Report" in report["report_markdown"]

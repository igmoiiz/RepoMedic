"""Integration tests for evidence -> hypothesis pipeline."""

from __future__ import annotations

from pathlib import Path

from repomedic.diagnosis.experiments import ExperimentEngine
from repomedic.diagnosis.hypotheses import HypothesisEngine
from repomedic.models.adapter import DeterministicAdapter
from repomedic.storage.database import init_db
from repomedic.storage.repositories import (
    EvidenceRepository,
    HypothesisRepository,
    InvestigationRepository,
)


def test_full_evidence_to_hypothesis_pipeline(tmp_path: Path) -> None:
    db_path = tmp_path / "inv.db"
    conn = init_db(db_path)

    inv_repo = InvestigationRepository(conn)
    ev_repo = EvidenceRepository(conn)
    hyp_repo = HypothesisRepository(conn)

    inv_repo.create("inv-1", "/test/repo", "ANALYSIS")

    ev_repo.add("ev-1", "inv-1", "traceback", "src/calc.py", 7, 7, "ZeroDivisionError")
    ev_repo.add("ev-2", "inv-1", "test_assertion", "tests/test_calc.py", 10, 10, "assert divide(1, 0)")

    stored_evidence = ev_repo.get_for_investigation("inv-1")

    engine = HypothesisEngine(DeterministicAdapter())
    hypotheses = engine.generate(stored_evidence, "inv-1")

    assert len(hypotheses) >= 1

    for hyp in hypotheses:
        hyp_repo.add(
            hyp["id"],
            hyp["investigation_id"],
            hyp["claim"],
            hyp["status"],
            hyp["confidence"],
            hyp["supporting_evidence"],
            hyp["contradicting_evidence"],
            hyp["candidate_locations"],
            hyp["experiment_proposal"],
            hyp["rank"],
        )

    stored = hyp_repo.get_for_investigation("inv-1")
    assert len(stored) == len(hypotheses)
    assert stored[0]["status"] == "candidate"


def test_experiment_updates_hypothesis(tmp_path: Path) -> None:
    engine = HypothesisEngine()
    hyp = {
        "id": "hyp-1",
        "claim": "Divide by zero causes crash",
        "status": "candidate",
        "confidence": "low",
        "supporting_evidence": ["ev-1"],
        "contradicting_evidence": [],
        "candidate_locations": [],
        "experiment_proposal": None,
        "rank": 1,
    }

    updated = engine.update_status(hyp, "supported", "high")
    assert updated["status"] == "supported"
    assert updated["confidence"] == "high"


def test_inconclusive_when_no_evidence(tmp_path: Path) -> None:
    engine = HypothesisEngine()
    results = engine.generate([], "inv-1")

    assert len(results) == 1
    assert "Insufficient" in results[0]["claim"]
    assert results[0]["confidence"] == "low"

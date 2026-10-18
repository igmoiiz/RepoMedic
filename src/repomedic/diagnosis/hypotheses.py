"""Hypothesis engine: generates and manages diagnostic hypotheses."""

from __future__ import annotations

import uuid
from typing import Any

from repomedic.models.adapter import DeterministicAdapter, HypothesisOutput, ModelAdapter


CONFIDENCE_LEVELS: frozenset[str] = frozenset({"low", "medium", "high"})
VALID_STATUSES: frozenset[str] = frozenset({
    "candidate",
    "supported",
    "contradicted",
    "verified",
    "unresolved",
})


class HypothesisEngine:
    """Generates hypotheses grounded in collected evidence."""

    def __init__(self, adapter: ModelAdapter | None = None) -> None:
        self._adapter = adapter or DeterministicAdapter()

    def generate(
        self,
        evidence: list[dict[str, Any]],
        investigation_id: str,
    ) -> list[dict[str, Any]]:
        response = self._adapter.generate_hypotheses(evidence)
        results: list[dict[str, Any]] = []

        for idx, hyp in enumerate(response.hypotheses):
            hyp_id = str(uuid.uuid4())
            results.append({
                "id": hyp_id,
                "investigation_id": investigation_id,
                "claim": hyp.claim,
                "status": "candidate",
                "confidence": hyp.confidence if hyp.confidence in CONFIDENCE_LEVELS else "low",
                "supporting_evidence": hyp.supporting_evidence,
                "contradicting_evidence": hyp.contradicting_evidence,
                "candidate_locations": hyp.candidate_locations,
                "experiment_proposal": hyp.experiment_proposal,
                "rank": idx + 1,
            })

        return results

    def update_status(
        self,
        hypothesis: dict[str, Any],
        new_status: str,
        confidence: str | None = None,
    ) -> dict[str, Any]:
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid hypothesis status: {new_status}")

        hypothesis["status"] = new_status
        if confidence is not None:
            if confidence not in CONFIDENCE_LEVELS:
                raise ValueError(f"Invalid confidence level: {confidence}")
            hypothesis["confidence"] = confidence
        return hypothesis

"""Provider-neutral LLM adapter for hypothesis generation and report synthesis."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class HypothesisOutput(BaseModel):
    claim: str
    candidate_locations: list[dict[str, Any]] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    experiment_proposal: str | None = None
    confidence: str = "medium"


class ModelResponse(BaseModel):
    hypotheses: list[HypothesisOutput] = Field(default_factory=list)
    raw_output: str = ""


class ModelAdapter(ABC):
    @abstractmethod
    def generate_hypotheses(
        self,
        evidence: list[dict[str, Any]],
        max_hypotheses: int = 3,
    ) -> ModelResponse:
        ...

    @abstractmethod
    def validate_output(self, output: str) -> ModelResponse:
        ...


class DeterministicAdapter(ModelAdapter):
    """Offline adapter that generates hypotheses from evidence without a model."""

    def generate_hypotheses(
        self,
        evidence: list[dict[str, Any]],
        max_hypotheses: int = 3,
    ) -> ModelResponse:
        hypotheses: list[HypothesisOutput] = []
        traceback_evidence = [e for e in evidence if e.get("source") == "traceback"]
        assertion_evidence = [e for e in evidence if e.get("source") == "test_assertion"]

        if traceback_evidence:
            for ev in traceback_evidence[:max_hypotheses]:
                hypotheses.append(
                    HypothesisOutput(
                        claim=f"Failure at {ev['file_path']}:{ev['line_start']} — {ev['description']}",
                        candidate_locations=[{
                            "file_path": ev["file_path"],
                            "line_start": ev["line_start"],
                            "line_end": ev.get("line_end") or ev["line_start"],
                        }],
                        supporting_evidence=[f"traceback:{ev['line_start']}"],
                        experiment_propose=None,
                        confidence="medium",
                    )
                )

        if assertion_evidence:
            for ev in assertion_evidence[:max_hypotheses]:
                hypotheses.append(
                    HypothesisOutput(
                        claim=f"Assertion failure: {ev['description']}",
                        candidate_locations=[{
                            "file_path": ev["file_path"],
                            "line_start": ev["line_start"],
                            "line_end": ev.get("line_end") or ev["line_start"],
                        }],
                        supporting_evidence=[f"test_assertion:{ev['line_start']}"],
                        confidence="medium",
                    )
                )

        if not hypotheses:
            hypotheses.append(
                HypothesisOutput(
                    claim="Insufficient evidence to form a hypothesis",
                    candidate_locations=[],
                    supporting_evidence=[],
                    confidence="low",
                )
            )

        return ModelResponse(hypotheses=hypotheses)

    def validate_output(self, output: str) -> ModelResponse:
        try:
            return ModelResponse.model_validate_json(output)
        except Exception:
            return ModelResponse(hypotheses=[], raw_output=output)

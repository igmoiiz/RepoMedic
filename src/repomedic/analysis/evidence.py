"""Evidence models for fault localization."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class EvidenceSource(str, Enum):
    TRACEBACK = "traceback"
    TEST_ASSERTION = "test_assertion"
    COVERAGE = "coverage"
    GIT_DIFF = "git_diff"
    STATIC_ANALYSIS = "static_analysis"
    EXECUTION = "execution"


class Evidence(BaseModel):
    source: EvidenceSource
    file_path: str
    line_start: int | None = None
    line_end: int | None = None
    description: str
    raw_excerpt: str | None = None


class LocationScore(BaseModel):
    file_path: str
    line_start: int
    line_end: int
    score: float = 0.0
    evidence_ids: list[str] = Field(default_factory=list)
    reason: str = ""

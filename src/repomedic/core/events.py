"""Event models for investigation tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class EventType(str, Enum):
    STATE_CHANGED = "STATE_CHANGED"
    EVIDENCE_ADDED = "EVIDENCE_ADDED"
    HYPOTHESIS_CREATED = "HYPOTHESIS_CREATED"
    HYPOTHESIS_UPDATED = "HYPOTHESIS_UPDATED"
    EXPERIMENT_STARTED = "EXPERIMENT_STARTED"
    EXPERIMENT_COMPLETED = "EXPERIMENT_COMPLETED"
    ERROR_OCCURRED = "ERROR_OCCURRED"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"


class Event(BaseModel):
    event_type: EventType
    investigation_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict = Field(default_factory=dict)
    sequence: int = 0

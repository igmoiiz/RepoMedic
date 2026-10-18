"""Unit tests for event models."""

from __future__ import annotations

from repomedic.core.events import Event, EventType


def test_event_creation() -> None:
    event = Event(
        event_type=EventType.STATE_CHANGED,
        investigation_id="inv-123",
        payload={"new_state": "ANALYSIS"},
    )
    assert event.event_type == EventType.STATE_CHANGED
    assert event.investigation_id == "inv-123"
    assert event.payload == {"new_state": "ANALYSIS"}
    assert event.sequence == 0


def test_event_with_sequence() -> None:
    event = Event(
        event_type=EventType.EVIDENCE_ADDED,
        investigation_id="inv-456",
        sequence=5,
    )
    assert event.sequence == 5

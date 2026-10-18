"""Unit tests for investigation state machine."""

from __future__ import annotations

import pytest

from repomedic.core.state_machine import (
    InvestigationState,
    InvalidTransition,
    can_transition,
    transition,
)


def test_valid_transition() -> None:
    result = transition(
        InvestigationState.CREATED,
        InvestigationState.REPOSITORY_INSPECTED,
    )
    assert result == InvestigationState.REPOSITORY_INSPECTED


def test_invalid_transition() -> None:
    with pytest.raises(InvalidTransition):
        transition(
            InvestigationState.CREATED,
            InvestigationState.APPLIED,
        )


def test_can_transition_true() -> None:
    assert can_transition(
        InvestigationState.ANALYSIS,
        InvestigationState.HYPOTHESIS_REVIEW,
    )


def test_can_transition_false() -> None:
    assert not can_transition(
        InvestigationState.CANCELLED,
        InvestigationState.ANALYSIS,
    )


def test_terminal_state_no_transitions() -> None:
    assert not can_transition(
        InvestigationState.APPLIED,
        InvestigationState.ANALYSIS,
    )


def test_invalid_transition_exception_details() -> None:
    exc = InvalidTransition(
        InvestigationState.CREATED,
        InvestigationState.APPLIED,
    )
    assert exc.from_state == InvestigationState.CREATED
    assert exc.to_state == InvestigationState.APPLIED

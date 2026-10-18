"""Investigation state machine."""

from __future__ import annotations

from enum import Enum


class InvestigationState(str, Enum):
    CREATED = "CREATED"
    REPOSITORY_INSPECTED = "REPOSITORY_INSPECTED"
    FAILURE_REPRODUCTION = "FAILURE_REPRODUCTION"
    ANALYSIS = "ANALYSIS"
    HYPOTHESIS_REVIEW = "HYPOTHESIS_REVIEW"
    EXPERIMENTS = "EXPERIMENTS"
    REPORT_READY = "REPORT_READY"
    PATCH_PROPOSED = "PATCH_PROPOSED"
    PATCH_VERIFIED = "PATCH_VERIFIED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    APPLIED = "APPLIED"
    INCONCLUSIVE = "INCONCLUSIVE"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"


TERMINAL_STATES: frozenset[InvestigationState] = frozenset({
    InvestigationState.INCONCLUSIVE,
    InvestigationState.CANCELLED,
    InvestigationState.FAILED,
    InvestigationState.BLOCKED_BY_POLICY,
    InvestigationState.APPLIED,
})

VALID_TRANSITIONS: dict[InvestigationState, set[InvestigationState]] = {
    InvestigationState.CREATED: {
        InvestigationState.REPOSITORY_INSPECTED,
        InvestigationState.CANCELLED,
        InvestigationState.FAILED,
    },
    InvestigationState.REPOSITORY_INSPECTED: {
        InvestigationState.FAILURE_REPRODUCTION,
        InvestigationState.ANALYSIS,
        InvestigationState.INCONCLUSIVE,
        InvestigationState.CANCELLED,
        InvestigationState.FAILED,
    },
    InvestigationState.FAILURE_REPRODUCTION: {
        InvestigationState.ANALYSIS,
        InvestigationState.INCONCLUSIVE,
        InvestigationState.CANCELLED,
        InvestigationState.FAILED,
    },
    InvestigationState.ANALYSIS: {
        InvestigationState.HYPOTHESIS_REVIEW,
        InvestigationState.INCONCLUSIVE,
        InvestigationState.CANCELLED,
        InvestigationState.FAILED,
    },
    InvestigationState.HYPOTHESIS_REVIEW: {
        InvestigationState.EXPERIMENTS,
        InvestigationState.REPORT_READY,
        InvestigationState.INCONCLUSIVE,
        InvestigationState.CANCELLED,
        InvestigationState.FAILED,
    },
    InvestigationState.EXPERIMENTS: {
        InvestigationState.REPORT_READY,
        InvestigationState.HYPOTHESIS_REVIEW,
        InvestigationState.INCONCLUSIVE,
        InvestigationState.CANCELLED,
        InvestigationState.FAILED,
    },
    InvestigationState.REPORT_READY: {
        InvestigationState.PATCH_PROPOSED,
        InvestigationState.CANCELLED,
    },
    InvestigationState.PATCH_PROPOSED: {
        InvestigationState.PATCH_VERIFIED,
        InvestigationState.APPROVAL_PENDING,
        InvestigationState.CANCELLED,
        InvestigationState.FAILED,
    },
    InvestigationState.PATCH_VERIFIED: {
        InvestigationState.APPROVAL_PENDING,
        InvestigationState.CANCELLED,
    },
    InvestigationState.APPROVAL_PENDING: {
        InvestigationState.APPLIED,
        InvestigationState.CANCELLED,
        InvestigationState.FAILED,
    },
    InvestigationState.INCONCLUSIVE: set(),
    InvestigationState.CANCELLED: set(),
    InvestigationState.FAILED: set(),
    InvestigationState.BLOCKED_BY_POLICY: set(),
    InvestigationState.APPLIED: set(),
}


class InvalidTransition(Exception):
    def __init__(self, from_state: InvestigationState, to_state: InvestigationState) -> None:
        super().__init__(f"Cannot transition from {from_state} to {to_state}")
        self.from_state = from_state
        self.to_state = to_state


def can_transition(
    from_state: InvestigationState, to_state: InvestigationState
) -> bool:
    return to_state in VALID_TRANSITIONS.get(from_state, set())


def transition(
    from_state: InvestigationState, to_state: InvestigationState
) -> InvestigationState:
    if not can_transition(from_state, to_state):
        raise InvalidTransition(from_state, to_state)
    return to_state

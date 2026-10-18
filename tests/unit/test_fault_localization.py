"""Unit tests for fault localization."""

from __future__ import annotations

from pathlib import Path

from repomedic.analysis.evidence import Evidence, EvidenceSource
from repomedic.analysis.fault_localization import FaultLocalizer
from repomedic.analysis.python_index import ModuleIndex, SourceRange, SymbolInfo


def _make_index() -> dict[Path, ModuleIndex]:
    idx = ModuleIndex(
        path=Path("src/app.py"),
        symbols=[
            SymbolInfo(
                name="process",
                kind="function",
                range=SourceRange(start_line=10, end_line=20),
            ),
            SymbolInfo(
                name="validate",
                kind="function",
                range=SourceRange(start_line=25, end_line=35),
            ),
        ],
    )
    return {Path("src/app.py"): idx}


def test_rank_traceback_evidence() -> None:
    localizer = FaultLocalizer(_make_index())
    evidence = [
        Evidence(
            source=EvidenceSource.TRACEBACK,
            file_path="src/app.py",
            line_start=15,
            line_end=15,
            description="Division by zero in process()",
        )
    ]
    ranked = localizer.rank(evidence)
    assert len(ranked) >= 1
    assert ranked[0].score > 0


def test_rank_assertion_evidence() -> None:
    localizer = FaultLocalizer(_make_index())
    evidence = [
        Evidence(
            source=EvidenceSource.TEST_ASSERTION,
            file_path="tests/test_app.py",
            line_start=10,
            line_end=10,
            description="Assertion failed",
        )
    ]
    ranked = localizer.rank(evidence)
    assert ranked[0].score >= 2.5


def test_rank_multiple_evidence() -> None:
    localizer = FaultLocalizer(_make_index())
    evidence = [
        Evidence(
            source=EvidenceSource.TRACEBACK,
            file_path="src/app.py",
            line_start=15,
            line_end=15,
            description="Error in process",
        ),
        Evidence(
            source=EvidenceSource.COVERAGE,
            file_path="src/app.py",
            line_start=15,
            line_end=15,
            description="Line not covered",
        ),
    ]
    ranked = localizer.rank(evidence)
    assert ranked[0].score > 3.0


def test_rank_empty_evidence() -> None:
    localizer = FaultLocalizer(_make_index())
    assert localizer.rank([]) == []


def test_rank_deterministic() -> None:
    evidence = [
        Evidence(
            source=EvidenceSource.TRACEBACK,
            file_path="src/app.py",
            line_start=15,
            line_end=15,
            description="Error",
        )
    ]
    localizer1 = FaultLocalizer(_make_index())
    localizer2 = FaultLocalizer(_make_index())
    result1 = localizer1.rank(evidence)
    result2 = localizer2.rank(evidence)
    assert [r.score for r in result1] == [r.score for r in result2]
    assert [r.file_path for r in result1] == [r.file_path for r in result2]


def test_test_related_locations() -> None:
    localizer = FaultLocalizer(_make_index(), test_files={Path("tests/test_app.py")})
    evidence = [
        Evidence(
            source=EvidenceSource.TEST_ASSERTION,
            file_path="tests/test_app.py",
            line_start=10,
            line_end=10,
            description="Test assertion failed",
        )
    ]
    results = localizer.find_test_related_locations(evidence)
    assert len(results) == 1
    assert results[0].score == 2.0


def test_score_capped_at_max() -> None:
    localizer = FaultLocalizer(_make_index())
    evidence = [
        Evidence(
            source=EvidenceSource.TRACEBACK,
            file_path="src/app.py",
            line_start=15,
            line_end=15,
            description="Error",
        ),
        Evidence(
            source=EvidenceSource.COVERAGE,
            file_path="src/app.py",
            line_start=15,
            line_end=15,
            description="Not covered",
        ),
        Evidence(
            source=EvidenceSource.GIT_DIFF,
            file_path="src/app.py",
            line_start=15,
            line_end=15,
            description="Recently changed",
        ),
        Evidence(
            source=EvidenceSource.EXECUTION,
            file_path="src/app.py",
            line_start=15,
            line_end=15,
            description="Executed",
        ),
    ]
    ranked = localizer.rank(evidence)
    assert ranked[0].score <= 10.0

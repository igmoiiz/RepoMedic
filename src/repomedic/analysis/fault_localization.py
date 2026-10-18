"""Fault localization: rank suspicious source locations."""

from __future__ import annotations

from pathlib import Path

from repomedic.analysis.evidence import Evidence, EvidenceSource, LocationScore
from repomedic.analysis.python_index import ModuleIndex, resolve_symbol_at_line


TRACEBACK_WEIGHT = 3.0
TEST_FILE_WEIGHT = 2.0
ASSERTION_WEIGHT = 2.5
COVERAGE_WEIGHT = 1.5
GIT_DIFF_WEIGHT = 1.0
CALL_PATH_WEIGHT = 1.5
MAX_SCORE = 10.0


class FaultLocalizer:
    """Ranks source locations by suspicion score based on evidence."""

    def __init__(
        self,
        indexes: dict[Path, ModuleIndex],
        test_files: set[Path] | None = None,
    ) -> None:
        self._indexes = indexes
        self._test_files = test_files or set()

    def rank(self, evidence: list[Evidence]) -> list[LocationScore]:
        """Rank locations from highest to lowest suspicion."""
        scores: dict[tuple[str, int, int], LocationScore] = {}

        for ev in evidence:
            if ev.line_start is None:
                continue

            key = (ev.file_path, ev.line_start, ev.line_end or ev.line_start)
            if key not in scores:
                scores[key] = LocationScore(
                    file_path=ev.file_path,
                    line_start=ev.line_start,
                    line_end=ev.line_end or ev.line_start,
                )

            entry = scores[key]
            entry.score += self._weight_for(ev.source)
            entry.evidence_ids.append(f"{ev.source.value}:{ev.line_start}")
            entry.reason = ev.description

        self._apply_traceback_call_path_evidence(evidence, scores)

        ranked = sorted(scores.values(), key=lambda s: s.score, reverse=True)
        for s in ranked:
            s.score = min(s.score, MAX_SCORE)
        return ranked

    def _weight_for(self, source: EvidenceSource) -> float:
        weights = {
            EvidenceSource.TRACEBACK: TRACEBACK_WEIGHT,
            EvidenceSource.TEST_ASSERTION: ASSERTION_WEIGHT,
            EvidenceSource.COVERAGE: COVERAGE_WEIGHT,
            EvidenceSource.GIT_DIFF: GIT_DIFF_WEIGHT,
            EvidenceSource.STATIC_ANALYSIS: TEST_FILE_WEIGHT,
            EvidenceSource.EXECUTION: TEST_FILE_WEIGHT,
        }
        return weights.get(source, 1.0)

    def _apply_traceback_call_path_evidence(
        self,
        evidence: list[Evidence],
        scores: dict[tuple[str, int, int], LocationScore],
    ) -> None:
        traceback_files = {
            ev.file_path
            for ev in evidence
            if ev.source == EvidenceSource.TRACEBACK and ev.line_start is not None
        }

        for ev in evidence:
            if ev.source != EvidenceSource.TRACEBACK or ev.line_start is None:
                continue

            matching = [
                idx
                for path, idx in self._indexes.items()
                if str(path) == ev.file_path or Path(ev.file_path) == path
            ]
            if not matching:
                continue

            idx = matching[0]
            sym = resolve_symbol_at_line(idx, ev.line_start)
            if sym is None:
                continue

            symbol_range = sym.range
            key = (ev.file_path, symbol_range.start_line, symbol_range.end_line)
            if key in scores:
                scores[key].score += CALL_PATH_WEIGHT
                scores[key].reason += f" (contains {sym.name})"

    def find_test_related_locations(
        self, evidence: list[Evidence]
    ) -> list[LocationScore]:
        """Find locations in or near test files."""
        results: list[LocationScore] = []
        for ev in evidence:
            if ev.line_start is None:
                continue
            try:
                ev_path = Path(ev.file_path)
            except (TypeError, ValueError):
                continue

            if ev_path in self._test_files or any(
                str(tf) in ev.file_path for tf in self._test_files
            ):
                results.append(
                    LocationScore(
                        file_path=ev.file_path,
                        line_start=ev.line_start,
                        line_end=ev.line_end or ev.line_start,
                        score=TEST_FILE_WEIGHT,
                        evidence_ids=[f"{ev.source.value}:{ev.line_start}"],
                        reason="Test file location",
                    )
                )
        return results

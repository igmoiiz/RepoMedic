"""Benchmark tests: fault localization metrics on known buggy fixtures."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from repomedic.analysis.evidence import Evidence, EvidenceSource
from repomedic.analysis.fault_localization import FaultLocalizer
from repomedic.analysis.python_index import PythonIndexBuilder


FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "buggy_projects"

FIXTURES = [
    {
        "name": "divide_by_zero",
        "buggy_file": "src/calc.py",
        "buggy_line": 2,
        "description": "Division by zero",
    },
    {
        "name": "off_by_one",
        "buggy_file": "src/sequence.py",
        "buggy_line": 2,
        "description": "Off-by-one error in get_last",
    },
    {
        "name": "wrong_comparison",
        "buggy_file": "src/compare.py",
        "buggy_line": 7,
        "description": "Wrong comparison operator in is_greater",
    },
    {
        "name": "wrong_comparison",
        "buggy_file": "src/compare.py",
        "buggy_line": 11,
        "description": "Wrong comparison in find_max",
    },
    {
        "name": "infinite_loop",
        "buggy_file": "src/loop.py",
        "buggy_line": 5,
        "description": "Wrong decrement step in countdown",
    },
]


def _run_fixture_tests(fixture_path: Path) -> tuple[int, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(fixture_path / "src")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--tb=short", "-q"],
        cwd=str(fixture_path),
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    return result.returncode, result.stdout


def _build_index(fixture_path: Path) -> dict[Path, object]:
    builder = PythonIndexBuilder()
    python_files = list(fixture_path.rglob("*.py"))
    indexes = {}
    for f in python_files:
        try:
            rel = f.relative_to(fixture_path)
        except ValueError:
            continue
        if "__pycache__" in rel.parts:
            continue
        idx = builder.build(f, fixture_path)
        indexes[rel] = idx
    return indexes


def _extract_traceback_file(stdout: str) -> tuple[str, int] | None:
    src_matches: list[tuple[str, int]] = []
    test_matches: list[tuple[str, int]] = []

    for line in stdout.splitlines():
        stripped = line.strip()
        if ".py:" not in stripped:
            continue

        if stripped.startswith("tests/") or stripped.startswith("src/") or "tests\\" in stripped or "src\\" in stripped:
            parts = stripped.split(":")
            if len(parts) >= 2:
                file_part = parts[0].strip()
                try:
                    line_num = int(parts[1])
                except ValueError:
                    continue
                if file_part.startswith("src/") or file_part.startswith("src\\"):
                    src_matches.append((file_part, line_num))
                else:
                    test_matches.append((file_part, line_num))

    if src_matches:
        return src_matches[0]
    if test_matches:
        return test_matches[0]
    return None


def test_all_fixtures_fail_as_expected() -> None:
    for fixture in FIXTURES:
        fixture_path = FIXTURES_DIR / fixture["name"]
        if not fixture_path.exists():
            continue
        exit_code, stdout = _run_fixture_tests(fixture_path)
        assert exit_code != 0, f"Fixture {fixture['name']} should have failing tests"


def test_top1_localization_divide_by_zero() -> None:
    fixture = FIXTURES[0]
    fixture_path = FIXTURES_DIR / fixture["name"]
    exit_code, stdout = _run_fixture_tests(fixture_path)

    indexes = _build_index(fixture_path)
    localizer = FaultLocalizer(indexes)

    traceback_info = _extract_traceback_file(stdout)
    assert traceback_info is not None, "Could not extract traceback location"

    file_path, line_num = traceback_info
    evidence = [
        Evidence(
            source=EvidenceSource.TRACEBACK,
            file_path=file_path,
            line_start=line_num,
            line_end=line_num,
            description="Traceback frame",
        )
    ]

    ranked = localizer.rank(evidence)
    assert len(ranked) > 0

    top1 = ranked[0]
    assert fixture["buggy_file"].replace("/", os.sep) in top1.file_path


def test_top5_localization_all_fixtures() -> None:
    hits = 0
    total = 0

    for fixture in FIXTURES:
        fixture_path = FIXTURES_DIR / fixture["name"]
        if not fixture_path.exists():
            continue

        exit_code, stdout = _run_fixture_tests(fixture_path)
        if exit_code == 0:
            continue

        indexes = _build_index(fixture_path)
        localizer = FaultLocalizer(indexes)

        traceback_info = _extract_traceback_file(stdout)
        if traceback_info is None:
            continue

        file_path, line_num = traceback_info
        evidence = [
            Evidence(
                source=EvidenceSource.TRACEBACK,
                file_path=file_path,
                line_start=line_num,
                line_end=line_num,
                description="Traceback frame",
            )
        ]

        ranked = localizer.rank(evidence)
        total += 1

        top5_files = [r.file_path for r in ranked[:5]]
        buggy_normalized = fixture["buggy_file"].replace("/", os.sep)
        if any(buggy_normalized in f for f in top5_files):
            hits += 1

    if total > 0:
        top5_rate = hits / total
        assert top5_rate >= 0.4, f"Top-5 rate {top5_rate:.2f} below 0.4 threshold"


def test_deterministic_ranking() -> None:
    fixture_path = FIXTURES_DIR / "divide_by_zero"
    indexes = _build_index(fixture_path)
    localizer = FaultLocalizer(indexes)

    evidence = [
        Evidence(
            source=EvidenceSource.TRACEBACK,
            file_path="src/calc.py",
            line_start=2,
            line_end=2,
            description="Traceback",
        )
    ]

    result1 = localizer.rank(evidence)
    result2 = localizer.rank(evidence)

    assert len(result1) == len(result2)
    for r1, r2 in zip(result1, result2):
        assert r1.score == r2.score
        assert r1.file_path == r2.file_path

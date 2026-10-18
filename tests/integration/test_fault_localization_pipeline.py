"""Integration tests for the fault localization pipeline."""

from __future__ import annotations

from pathlib import Path

from repomedic.analysis.evidence import Evidence, EvidenceSource
from repomedic.analysis.fault_localization import FaultLocalizer
from repomedic.analysis.python_index import PythonIndexBuilder


def test_index_then_rank_pipeline(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "calc.py").write_text(
        "def add(a, b):\n"
        "    return a + b\n"
        "\n"
        "def divide(a, b):\n"
        "    return a / b\n"
        "\n"
        "def multiply(a, b):\n"
        "    result = add(a, b)\n"
        "    return result * b\n",
        encoding="utf-8",
    )

    builder = PythonIndexBuilder()
    index = builder.build(src_dir / "calc.py", tmp_path)
    assert index.parse_error is None
    assert len(index.symbols) == 3

    evidence = [
        Evidence(
            source=EvidenceSource.TRACEBACK,
            file_path="src/calc.py",
            line_start=7,
            line_end=7,
            description="ZeroDivisionError in divide()",
        )
    ]
    localizer = FaultLocalizer({Path("src/calc.py"): index})
    ranked = localizer.rank(evidence)

    assert len(ranked) >= 1
    assert ranked[0].file_path == "src/calc.py"
    assert ranked[0].score >= 3.0
    assert any("divide" in r.reason for r in ranked)


def test_rank_multiple_files(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("def foo():\n    pass\n", encoding="utf-8")
    (tmp_path / "src" / "b.py").write_text("def bar():\n    pass\n", encoding="utf-8")

    builder = PythonIndexBuilder()
    index_a = builder.build(tmp_path / "src" / "a.py", tmp_path)
    index_b = builder.build(tmp_path / "src" / "b.py", tmp_path)

    evidence = [
        Evidence(
            source=EvidenceSource.TRACEBACK,
            file_path="src/b.py",
            line_start=2,
            line_end=2,
            description="Error in bar()",
        )
    ]
    localizer = FaultLocalizer({Path("src/a.py"): index_a, Path("src/b.py"): index_b})
    ranked = localizer.rank(evidence)

    assert ranked[0].file_path == "src/b.py"

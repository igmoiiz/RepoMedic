"""Unit tests for Python source indexing."""

from __future__ import annotations

from pathlib import Path

from repomedic.analysis.python_index import (
    ModuleIndex,
    PythonIndexBuilder,
    resolve_symbol_at_line,
)


def _write_file(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_build_simple_module(tmp_path: Path) -> None:
    src = _write_file(tmp_path / "mod.py", "def foo():\n    pass\n\nclass Bar:\n    def baz(self):\n        pass\n")
    builder = PythonIndexBuilder()
    index = builder.build(src, tmp_path)

    assert index.parse_error is None
    assert len(index.symbols) == 3
    names = [s.name for s in index.symbols]
    assert "foo" in names
    assert "Bar" in names
    assert "baz" in names


def test_build_with_imports(tmp_path: Path) -> None:
    src = _write_file(tmp_path / "imports.py", "import os\nfrom pathlib import Path\nfrom typing import Optional\n")
    builder = PythonIndexBuilder()
    index = builder.build(src, tmp_path)

    assert len(index.imports) == 3
    assert index.imports[0].module == "os"
    assert index.imports[1].module == "pathlib"
    assert "Path" in index.imports[1].names


def test_build_syntax_error(tmp_path: Path) -> None:
    src = _write_file(tmp_path / "bad.py", "def foo(\n")
    builder = PythonIndexBuilder()
    index = builder.build(src, tmp_path)

    assert index.parse_error is not None
    assert "SyntaxError" in index.parse_error


def test_build_async_function(tmp_path: Path) -> None:
    src = _write_file(tmp_path / "async.py", "async def fetch():\n    pass\n")
    builder = PythonIndexBuilder()
    index = builder.build(src, tmp_path)

    assert any(s.name == "fetch" for s in index.symbols)


def test_build_decorated_function(tmp_path: Path) -> None:
    src = _write_file(tmp_path / "deco.py", "@app.route('/')\ndef handler():\n    pass\n")
    builder = PythonIndexBuilder()
    index = builder.build(src, tmp_path)

    handler = next(s for s in index.symbols if s.name == "handler")
    assert "app.route" in handler.decorators


def test_resolve_symbol_at_line_function() -> None:
    index = ModuleIndex(
        path=Path("test.py"),
        symbols=[],
    )
    from repomedic.analysis.python_index import SourceRange, SymbolInfo

    index.symbols.append(
        SymbolInfo(
            name="foo",
            kind="function",
            range=SourceRange(start_line=1, end_line=5),
        )
    )
    index.symbols.append(
        SymbolInfo(
            name="bar",
            kind="function",
            range=SourceRange(start_line=10, end_line=15),
        )
    )

    result = resolve_symbol_at_line(index, 3)
    assert result is not None
    assert result.name == "foo"

    result2 = resolve_symbol_at_line(index, 12)
    assert result2 is not None
    assert result2.name == "bar"


def test_resolve_symbol_at_line_nested() -> None:
    from repomedic.analysis.python_index import SourceRange, SymbolInfo

    index = ModuleIndex(
        path=Path("nested.py"),
        symbols=[
            SymbolInfo(
                name="outer",
                kind="function",
                range=SourceRange(start_line=1, end_line=10),
            ),
            SymbolInfo(
                name="inner",
                kind="function",
                range=SourceRange(start_line=3, end_line=7),
            ),
        ],
    )

    result = resolve_symbol_at_line(index, 5)
    assert result is not None
    assert result.name == "inner"


def test_resolve_symbol_not_found() -> None:
    index = ModuleIndex(path=Path("empty.py"), symbols=[])
    result = resolve_symbol_at_line(index, 42)
    assert result is None


def test_build_project(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    _write_file(tmp_path / "src" / "a.py", "def a(): pass\n")
    _write_file(tmp_path / "src" / "b.py", "def b(): pass\n")

    builder = PythonIndexBuilder()
    python_files = [Path("src/a.py"), Path("src/b.py")]
    indexes = builder.build_project(tmp_path, python_files)

    assert len(indexes) == 2

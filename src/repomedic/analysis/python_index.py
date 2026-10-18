"""Python source indexing using ast."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class SourceRange:
    start_line: int
    end_line: int
    start_col: int = 0
    end_col: int = 0


@dataclass
class SymbolInfo:
    name: str
    kind: str
    range: SourceRange
    parent: str | None = None
    decorators: list[str] = field(default_factory=list)


@dataclass
class ImportInfo:
    module: str
    names: list[str] = field(default_factory=list)
    level: int = 0
    line: int = 0


@dataclass
class ModuleIndex:
    path: Path
    symbols: list[SymbolInfo] = field(default_factory=list)
    imports: list[ImportInfo] = field(default_factory=list)
    parse_error: str | None = None


class PythonIndexBuilder:
    def build(self, file_path: Path, root: Path) -> ModuleIndex:
        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            return ModuleIndex(path=file_path.relative_to(root), parse_error=str(e))

        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as e:
            return ModuleIndex(
                path=file_path.relative_to(root),
                parse_error=f"SyntaxError: {e.msg}",
            )

        relative = file_path.relative_to(root)
        index = ModuleIndex(path=relative)

        for node in tree.body:
            if isinstance(node, ast.Import):
                self._handle_import(node, index)
            elif isinstance(node, ast.ImportFrom):
                self._handle_import_from(node, index)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._handle_function(node, index)
            elif isinstance(node, ast.ClassDef):
                self._handle_class(node, index)

        return index

    def build_project(
        self, root: Path, python_files: list[Path]
    ) -> dict[Path, ModuleIndex]:
        indexes: dict[Path, ModuleIndex] = {}
        for file_path in python_files:
            try:
                full_path = root / file_path
                relative = full_path.relative_to(root)
            except ValueError:
                continue
            indexes[file_path] = self.build(full_path, root)
        return {k: v for k, v in indexes.items() if k is not None}

    def _handle_import(self, node: ast.Import, index: ModuleIndex) -> None:
        for alias in node.names:
            index.imports.append(
                ImportInfo(module=alias.name, line=node.lineno)
            )

    def _handle_import_from(self, node: ast.ImportFrom, index: ModuleIndex) -> None:
        module = node.module or ""
        names = [alias.name for alias in node.names]
        index.imports.append(
            ImportInfo(module=module, names=names, level=node.level, line=node.lineno)
        )

    def _handle_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, index: ModuleIndex
    ) -> None:
        decorators = [self._format_decorator(d) for d in node.decorator_list]

        end_line = getattr(node, "end_lineno", node.lineno) or node.lineno
        index.symbols.append(
            SymbolInfo(
                name=node.name,
                kind="function",
                range=SourceRange(
                    start_line=node.lineno,
                    end_line=end_line,
                    start_col=node.col_offset,
                ),
                decorators=decorators,
            )
        )

    @staticmethod
    def _format_decorator(node: ast.expr) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parts: list[str] = []
            current: ast.expr = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        if isinstance(node, ast.Call):
            return PythonIndexBuilder._format_decorator(node.func)
        return ""

    def _handle_class(self, node: ast.ClassDef, index: ModuleIndex) -> None:
        end_line = getattr(node, "end_lineno", node.lineno) or node.lineno
        index.symbols.append(
            SymbolInfo(
                name=node.name,
                kind="class",
                range=SourceRange(
                    start_line=node.lineno,
                    end_line=end_line,
                    start_col=node.col_offset,
                ),
            )
        )

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._handle_method(item, index, class_name=node.name)

    def _handle_method(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        index: ModuleIndex,
        class_name: str,
    ) -> None:
        end_line = getattr(node, "end_lineno", node.lineno) or node.lineno
        index.symbols.append(
            SymbolInfo(
                name=node.name,
                kind="method",
                range=SourceRange(
                    start_line=node.lineno,
                    end_line=end_line,
                    start_col=node.col_offset,
                ),
                parent=class_name,
            )
        )


def resolve_symbol_at_line(index: ModuleIndex, line: int) -> SymbolInfo | None:
    candidates: list[SymbolInfo] = []
    for sym in index.symbols:
        if sym.range.start_line <= line <= sym.range.end_line:
            candidates.append(sym)

    if not candidates:
        return None

    candidates.sort(key=lambda s: (s.range.end_line - s.range.start_line))
    return candidates[0]


def resolve_traceback_frame(
    indexes: dict[Path, ModuleIndex], file_path: Path, line: int
) -> SymbolInfo | None:

    matching_indexes = [
        idx for path, idx in indexes.items() if path == file_path or str(path) == str(file_path)
    ]
    if not matching_indexes:
        return None
    return resolve_symbol_at_line(matching_indexes[0], line)

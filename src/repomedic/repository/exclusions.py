"""File exclusion rules for repository inspection."""

from __future__ import annotations

import fnmatch
from pathlib import Path


DEFAULT_EXCLUDED_NAMES: frozenset[str] = frozenset(
    {
        ".env",
        ".env.local",
        ".env.production",
        ".git",
        ".hg",
        ".svn",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".nox",
        ".coverage",
        ".coverage.*",
        ".DS_Store",
        "Thumbs.db",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "env",
        "dist",
        "build",
        "*.egg-info",
        "htmlcov",
        "secrets",
        ".trash",
        ".obsidian",
    }
)

DEFAULT_EXCLUDED_PATTERNS: tuple[str, ...] = (
    "*.pyc",
    "*.pyo",
    "*.pem",
    "*.key",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "*.log",
)


class ExclusionRules:
    """Determines which files and directories to exclude from indexing."""

    def __init__(
        self,
        *,
        excluded_names: set[str] | None = None,
        excluded_patterns: tuple[str, ...] | None = None,
        max_file_size: int = 1_048_576,
    ) -> None:
        self._names = excluded_names if excluded_names is not None else set(DEFAULT_EXCLUDED_NAMES)
        self._patterns = excluded_patterns if excluded_patterns is not None else DEFAULT_EXCLUDED_PATTERNS
        self._max_file_size = max_file_size

    def should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded."""
        if path.name in self._names:
            return True
        if any(fnmatch.fnmatch(path.name, pat) for pat in self._patterns):
            return True
        return False

    def is_safe_to_read(self, path: Path) -> bool:
        """Check if a file is safe to read (exists, is file, not too large)."""
        if not path.is_file():
            return False
        try:
            return path.stat().st_size <= self._max_file_size
        except OSError:
            return False

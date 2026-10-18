"""Repository inspection and validation."""

from __future__ import annotations

import subprocess
from pathlib import Path

from repomedic.core.models import InspectionResult, ProjectMetadata
from repomedic.repository.exclusions import ExclusionRules
from repomedic.repository.git import get_git_status, is_git_repo


TEST_CONFIG_FILES: tuple[str, ...] = ("pytest.ini", "tox.ini", "setup.cfg", "pyproject.toml")


class Inspector:
    """Inspects a repository and produces a structured InspectionResult."""

    def __init__(self, exclusions: ExclusionRules | None = None) -> None:
        self._exclusions = exclusions or ExclusionRules()

    def inspect(self, root: Path) -> InspectionResult:
        """Inspect the repository at the given root path."""
        errors: list[str] = []

        resolved = root.resolve()
        if not resolved.exists():
            return InspectionResult(
                root=resolved,
                is_valid=False,
                errors=[f"Path does not exist: {resolved}"],
            )

        if not resolved.is_dir():
            return InspectionResult(
                root=resolved,
                is_valid=False,
                errors=[f"Path is not a directory: {resolved}"],
            )

        git = get_git_status(resolved)
        if not is_git_repo(resolved):
            errors.append("Not a git repository")

        python_files = self._find_python_files(resolved)
        project = self._detect_project_metadata(resolved)

        return InspectionResult(
            root=resolved,
            is_valid=not errors,
            errors=errors,
            git=git,
            python_files=python_files,
            project=project,
        )

    def _find_python_files(self, root: Path) -> list[Path]:
        """Find all Python files in the repository, respecting exclusions."""
        python_files: list[Path] = []
        for path in root.rglob("*.py"):
            try:
                resolved = path.resolve()
            except OSError:
                continue

            try:
                relative = resolved.relative_to(root)
            except ValueError:
                continue

            if any(self._exclusions.should_exclude(Path(part)) for part in relative.parts):
                continue

            if self._exclusions.is_safe_to_read(resolved):
                python_files.append(relative)

        return sorted(python_files)

    def _detect_project_metadata(self, root: Path) -> ProjectMetadata:
        """Detect project metadata from common config files."""
        metadata = ProjectMetadata()

        pyproject = root / "pyproject.toml"
        if pyproject.is_file():
            metadata.has_pyproject = True
            self._parse_pyproject(pyproject, metadata)

        setup_py = root / "setup.py"
        if setup_py.is_file():
            metadata.has_setup_py = True

        requirements = root / "requirements.txt"
        if requirements.is_file():
            metadata.has_requirements = True

        metadata.test_config = [
            f for f in TEST_CONFIG_FILES if (root / f).is_file()
        ]

        return metadata

    def _parse_pyproject(self, path: Path, metadata: ProjectMetadata) -> None:
        """Extract basic metadata from pyproject.toml using stdlib tomllib."""
        import tomllib

        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            return

        project = data.get("project", {})
        metadata.name = project.get("name")

        requires_python = project.get("requires-python", "")
        if requires_python:
            metadata.python_version = requires_python

        deps = project.get("dependencies", [])
        metadata.dependencies = list(deps)

        for group_name, group_deps in data.get("dependency-groups", {}).items():
            if isinstance(group_deps, list):
                metadata.dependencies.extend(str(d) for d in group_deps)

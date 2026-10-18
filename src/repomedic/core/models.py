"""Core data models for RepoMedic."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class GitStatus(BaseModel):
    """Git repository state."""

    is_git_repo: bool = False
    branch: str | None = None
    commit: str | None = None
    is_dirty: bool = False
    modified_files: list[str] = Field(default_factory=list)
    untracked_files: list[str] = Field(default_factory=list)


class ProjectMetadata(BaseModel):
    """Detected project metadata."""

    name: str | None = None
    python_version: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    has_pyproject: bool = False
    has_setup_py: bool = False
    has_requirements: bool = False
    test_config: list[str] = Field(default_factory=list)


class InspectionResult(BaseModel):
    """Result of repository inspection."""

    root: Path
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    git: GitStatus = Field(default_factory=GitStatus)
    python_files: list[Path] = Field(default_factory=list)
    project: ProjectMetadata = Field(default_factory=ProjectMetadata)


class ExecutionResult(BaseModel):
    """Structured result of a command execution."""

    command: list[str]
    cwd: Path
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    timed_out: bool = False
    cancelled: bool = False
    output_truncated: bool = False

"""Unified diff generation and validation."""

from __future__ import annotations

import subprocess
from pathlib import Path

from repomedic.patching.worktree import WorktreeManager

DANGEROUS_PATHS: frozenset[str] = frozenset({
    ".git",
    ".env",
    ".env.local",
    ".env.production",
    "secrets",
    "credentials",
})

DANGEROUS_EXTENSIONS: frozenset[str] = frozenset({
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".sqlite",
    ".sqlite3",
    ".db",
})


class DiffError(Exception):
    pass


class PatchValidationError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def generate_diff(repo_root: Path, from_ref: str = "HEAD") -> str:
    try:
        result = subprocess.run(
            ["git", "diff", from_ref],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
            shell=False,
        )
    except subprocess.CalledProcessError as e:
        raise DiffError(f"git diff failed: {e.stderr}") from e
    except FileNotFoundError as e:
        raise DiffError("git executable not found") from e

    return result.stdout


def generate_diff_between(repo_root: Path, from_ref: str, to_ref: str) -> str:
    try:
        result = subprocess.run(
            ["git", "diff", f"{from_ref}..{to_ref}"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
            shell=False,
        )
    except subprocess.CalledProcessError as e:
        raise DiffError(f"git diff failed: {e.stderr}") from e

    return result.stdout


def get_changed_files(repo_root: Path, from_ref: str = "HEAD") -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", from_ref],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
            shell=False,
        )
    except subprocess.CalledProcessError as e:
        raise DiffError(f"git diff --name-only failed: {e.stderr}") from e

    return [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]


def validate_patch_paths(
    changed_files: list[str],
    allowed_paths: list[str] | None = None,
) -> None:
    for filepath in changed_files:
        path = Path(filepath)

        if path.is_absolute() or filepath.startswith("/") or filepath.startswith("\\"):
            raise PatchValidationError(f"Absolute path not allowed: {filepath}")

        parts = path.parts
        for part in parts:
            if part in DANGEROUS_PATHS:
                raise PatchValidationError(
                    f"Patch touches protected path: {filepath}"
                )

        if path.suffix.lower() in DANGEROUS_EXTENSIONS:
            raise PatchValidationError(
                f"Patch touches protected file type: {filepath}"
            )

        if ".." in parts:
            raise PatchValidationError(
                f"Path traversal detected: {filepath}"
            )

        if allowed_paths is not None:
            normalized = filepath.replace("\\", "/")
            if not any(
                normalized == allowed or normalized.startswith(allowed.rstrip("/") + "/")
                for allowed in allowed_paths
            ):
                raise PatchValidationError(
                    f"Patch path {filepath} is not in allowed paths"
                )


def parse_diff_patch(diff_text: str) -> list[dict[str, str]]:
    patches: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            if current is not None:
                patches.append(current)
            current = {"header": line, "body": ""}
        elif current is not None:
            current["body"] += line + "\n"

    if current is not None:
        patches.append(current)

    return patches

"""Unit tests for diff generation and validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from repomedic.patching.diff import (
    DANGEROUS_EXTENSIONS,
    DANGEROUS_PATHS,
    DiffError,
    PatchValidationError,
    parse_diff_patch,
    validate_patch_paths,
)


def test_validate_normal_paths() -> None:
    validate_patch_paths(["src/main.py", "tests/test_main.py"])


def test_validate_absolute_path_rejected() -> None:
    with pytest.raises(PatchValidationError, match="Absolute path"):
        validate_patch_paths(["/etc/passwd"])


def test_validate_path_traversal_rejected() -> None:
    with pytest.raises(PatchValidationError, match="traversal"):
        validate_patch_paths(["../outside.py"])


def test_validate_dangerous_path_rejected() -> None:
    with pytest.raises(PatchValidationError, match="protected path"):
        validate_patch_paths([".env"])


def test_validate_dangerous_extension_rejected() -> None:
    with pytest.raises(PatchValidationError, match="protected file type"):
        validate_patch_paths(["secrets.pem"])


def test_validate_allowed_paths() -> None:
    validate_patch_paths(["src/main.py"], allowed_paths=["src/"])


def test_validate_disallowed_path() -> None:
    with pytest.raises(PatchValidationError, match="not in allowed paths"):
        validate_patch_paths(["lib/other.py"], allowed_paths=["src/"])


def test_dangerous_paths_not_empty() -> None:
    assert len(DANGEROUS_PATHS) > 0
    assert ".git" in DANGEROUS_PATHS
    assert ".env" in DANGEROUS_PATHS


def test_dangerous_extensions_not_empty() -> None:
    assert len(DANGEROUS_EXTENSIONS) > 0
    assert ".pem" in DANGEROUS_EXTENSIONS


def test_parse_diff_patch_empty() -> None:
    assert parse_diff_patch("") == []


def test_parse_diff_patch_basic() -> None:
    diff_text = (
        "diff --git a/src/main.py b/src/main.py\n"
        "index abc..def 100644\n"
        "--- a/src/main.py\n"
        "+++ b/src/main.py\n"
        "@@ -1,3 +1,4 @@\n"
        " context\n"
        "+added line\n"
    )
    patches = parse_diff_patch(diff_text)
    assert len(patches) == 1
    assert "src/main.py" in patches[0]["header"]


def test_parse_diff_patch_multiple() -> None:
    diff_text = (
        "diff --git a/file1.py b/file1.py\n"
        "--- a/file1.py\n"
        "+++ b/file1.py\n"
        "@@ -1 +1 @@\n"
        "-old\n"
        "+new\n"
        "diff --git a/file2.py b/file2.py\n"
        "--- a/file2.py\n"
        "+++ b/file2.py\n"
        "@@ -1 +1 @@\n"
        "-old\n"
        "+new\n"
    )
    patches = parse_diff_patch(diff_text)
    assert len(patches) == 2


def test_generate_diff_not_git_repo(tmp_path: Path) -> None:
    from repomedic.patching.diff import generate_diff

    with pytest.raises(DiffError):
        generate_diff(tmp_path)


def test_get_changed_files_not_git_repo(tmp_path: Path) -> None:
    from repomedic.patching.diff import get_changed_files

    with pytest.raises(DiffError):
        get_changed_files(tmp_path)

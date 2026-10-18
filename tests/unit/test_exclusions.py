"""Unit tests for repository exclusions."""

from __future__ import annotations

from pathlib import Path

from repomedic.repository.exclusions import ExclusionRules


def test_excludes_env_files() -> None:
    rules = ExclusionRules()
    assert rules.should_exclude(Path(".env"))
    assert rules.should_exclude(Path(".env.local"))
    assert rules.should_exclude(Path(".env.production"))


def test_excludes_secret_files() -> None:
    rules = ExclusionRules()
    assert rules.should_exclude(Path("secret.pem"))
    assert rules.should_exclude(Path("id_rsa.key"))


def test_excludes_caches() -> None:
    rules = ExclusionRules()
    assert rules.should_exclude(Path("__pycache__"))
    assert rules.should_exclude(Path(".pytest_cache"))
    assert rules.should_exclude(Path(".mypy_cache"))


def test_excludes_venv() -> None:
    rules = ExclusionRules()
    assert rules.should_exclude(Path(".venv"))
    assert rules.should_exclude(Path("venv"))
    assert rules.should_exclude(Path("env"))


def test_excludes_build_outputs() -> None:
    rules = ExclusionRules()
    assert rules.should_exclude(Path("dist"))
    assert rules.should_exclude(Path("build"))
    assert rules.should_exclude(Path("htmlcov"))


def test_allows_normal_python_files() -> None:
    rules = ExclusionRules()
    assert not rules.should_exclude(Path("src/main.py"))
    assert not rules.should_exclude(Path("tests/test_foo.py"))
    assert not rules.should_exclude(Path("lib/utils.py"))


def test_allows_normal_directories() -> None:
    rules = ExclusionRules()
    assert not rules.should_exclude(Path("src"))
    assert not rules.should_exclude(Path("tests"))
    assert not rules.should_exclude(Path("docs"))


def test_custom_excluded_names() -> None:
    rules = ExclusionRules(excluded_names={"custom_dir"})
    assert rules.should_exclude(Path("custom_dir"))
    assert not rules.should_exclude(Path("other_dir"))


def test_is_safe_to_read_too_large(tmp_path: Path) -> None:
    rules = ExclusionRules(max_file_size=10)
    large_file = tmp_path / "large.py"
    large_file.write_text("x" * 100)
    assert not rules.is_safe_to_read(large_file)


def test_is_safe_to_read_normal_size(tmp_path: Path) -> None:
    rules = ExclusionRules(max_file_size=1024)
    normal_file = tmp_path / "normal.py"
    normal_file.write_text("print('hello')")
    assert rules.is_safe_to_read(normal_file)


def test_is_safe_to_read_nonexistent() -> None:
    rules = ExclusionRules()
    assert not rules.is_safe_to_read(Path("/nonexistent/file.py"))

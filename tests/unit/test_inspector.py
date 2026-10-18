"""Unit tests for repository inspector."""

from __future__ import annotations

import subprocess
from pathlib import Path

from repomedic.repository.inspector import Inspector


def test_inspect_nonexistent_path() -> None:
    inspector = Inspector()
    result = inspector.inspect(Path("/nonexistent/path"))
    assert not result.is_valid
    assert len(result.errors) == 1
    assert "does not exist" in result.errors[0]


def test_inspect_file_instead_of_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "file.py"
    file_path.write_text("print('hello')")
    inspector = Inspector()
    result = inspector.inspect(file_path)
    assert not result.is_valid
    assert "not a directory" in result.errors[0]


def test_inspect_valid_python_project(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "test-project"\nversion = "0.1.0"\n'
        'requires-python = ">=3.12"\ndependencies = ["pydantic>=2.7"]\n'
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def main(): pass")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_main(): pass")

    inspector = Inspector()
    result = inspector.inspect(tmp_path)

    assert result.is_valid
    assert result.git.is_git_repo
    assert result.project.has_pyproject
    assert result.project.name == "test-project"
    assert result.project.python_version == ">=3.12"
    assert "pydantic>=2.7" in result.project.dependencies
    assert len(result.python_files) == 2


def test_inspect_respects_exclusions(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)

    (tmp_path / ".env").write_text("SECRET=123")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "main.cpython-312.pyc").write_bytes(b"fake")

    inspector = Inspector()
    result = inspector.inspect(tmp_path)

    assert result.is_valid
    file_names = [f.name for f in result.python_files]
    assert "main.py" in file_names
    assert "main.cpython-312.pyc" not in file_names


def test_inspect_detects_test_config(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)

    (tmp_path / "pytest.ini").write_text("[pytest]\ntestpaths = tests")
    (tmp_path / "tox.ini").write_text("[tox]\nenvlist = py312")

    inspector = Inspector()
    result = inspector.inspect(tmp_path)

    assert result.project.test_config == ["pytest.ini", "tox.ini"]


def test_inspect_non_git_directory(tmp_path: Path) -> None:
    (tmp_path / "script.py").write_text("print('hello')")
    inspector = Inspector()
    result = inspector.inspect(tmp_path)
    assert not result.is_valid
    assert "Not a git repository" in result.errors
    assert result.python_files != []

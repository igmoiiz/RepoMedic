"""Unit tests for SQLite database setup."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from repomedic.storage.database import init_db


def test_init_db_creates_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = init_db(db_path)

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    table_names = [t[0] for t in tables]

    assert "investigations" in table_names
    assert "events" in table_names
    assert "evidence" in table_names
    assert "hypotheses" in table_names
    assert "experiments" in table_names


def test_init_db_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    init_db(db_path)
    init_db(db_path)

    tables = db_path.read_bytes()
    assert tables


def test_init_db_creates_indexes(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"
    conn = init_db(db_path)

    indexes = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    index_names = [i[0] for i in indexes]

    assert "idx_events_investigation" in index_names
    assert "idx_evidence_investigation" in index_names

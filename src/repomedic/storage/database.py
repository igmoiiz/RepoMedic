"""SQLite database setup and schema."""

from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS investigations (
    id TEXT PRIMARY KEY,
    repository_root TEXT NOT NULL,
    state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    investigation_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    payload TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    FOREIGN KEY (investigation_id) REFERENCES investigations(id)
);

CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    investigation_id TEXT NOT NULL,
    source TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_start INTEGER,
    line_end INTEGER,
    description TEXT NOT NULL,
    raw_excerpt TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (investigation_id) REFERENCES investigations(id)
);

CREATE TABLE IF NOT EXISTS hypotheses (
    id TEXT PRIMARY KEY,
    investigation_id TEXT NOT NULL,
    claim TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence TEXT NOT NULL,
    supporting_evidence TEXT NOT NULL,
    contradicting_evidence TEXT NOT NULL,
    candidate_locations TEXT NOT NULL,
    experiment_proposal TEXT,
    rank INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (investigation_id) REFERENCES investigations(id)
);

CREATE TABLE IF NOT EXISTS experiments (
    id TEXT PRIMARY KEY,
    investigation_id TEXT NOT NULL,
    intent TEXT NOT NULL,
    command TEXT NOT NULL,
    result_summary TEXT NOT NULL,
    success INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (investigation_id) REFERENCES investigations(id)
);

CREATE INDEX IF NOT EXISTS idx_events_investigation ON events(investigation_id);
CREATE INDEX IF NOT EXISTS idx_evidence_investigation ON evidence(investigation_id);
CREATE INDEX IF NOT EXISTS idx_hypotheses_investigation ON hypotheses(investigation_id);
CREATE INDEX IF NOT EXISTS idx_experiments_investigation ON experiments(investigation_id);
"""


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def get_connection(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(str(db_path))

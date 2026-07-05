"""Persistencia SQLite de ManimStudio.

Un solo usuario y bajo volumen: sqlite3 sincrono con lock es suficiente y
evita otra dependencia. WAL para que lecturas (historial) no bloqueen al
worker que actualiza estados.
"""

import json
import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    scene TEXT NOT NULL,
    quality TEXT NOT NULL,
    timeout INTEGER NOT NULL,
    status TEXT NOT NULL,
    script TEXT NOT NULL,
    video_path TEXT,
    error TEXT,
    created_at REAL NOT NULL,
    started_at REAL,
    finished_at REAL
);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC);
"""

# Migraciones aditivas (ALTER TABLE ADD COLUMN es no destructivo en SQLite).
MIGRATIONS = (
    ("size_bytes", "ALTER TABLE jobs ADD COLUMN size_bytes INTEGER"),
    ("thumb_path", "ALTER TABLE jobs ADD COLUMN thumb_path TEXT"),
)


class Database:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.executescript(SCHEMA)
            cols = {r["name"] for r in self._conn.execute("PRAGMA table_info(jobs)")}
            for col, ddl in MIGRATIONS:
                if col not in cols:
                    self._conn.execute(ddl)
            self._conn.commit()

    def insert_job(self, job: dict) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO jobs (id, scene, quality, timeout, status, script, created_at)"
                " VALUES (:id, :scene, :quality, :timeout, :status, :script, :created_at)",
                job,
            )
            self._conn.commit()

    def update_job(self, job_id: str, **fields) -> None:
        if not fields:
            return
        cols = ", ".join(f"{k} = :{k}" for k in fields)
        fields["id"] = job_id
        with self._lock:
            self._conn.execute(f"UPDATE jobs SET {cols} WHERE id = :id", fields)
            self._conn.commit()

    def get_job(self, job_id: str) -> dict | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None

    def list_jobs(self, limit: int = 50) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, scene, quality, timeout, status, video_path, error,"
                " created_at, started_at, finished_at, size_bytes, thumb_path,"
                " length(script) AS script_len"
                " FROM jobs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def get_script(self, job_id: str) -> str | None:
        with self._lock:
            row = self._conn.execute("SELECT script FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return row["script"] if row else None

    def delete_job(self, job_id: str) -> bool:
        with self._lock:
            cur = self._conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
            self._conn.commit()
        return cur.rowcount > 0

    def mark_interrupted(self) -> int:
        """Jobs que quedaron 'queued'/'running' tras un reinicio del backend."""
        with self._lock:
            cur = self._conn.execute(
                "UPDATE jobs SET status = 'error', error = 'interrumpido por reinicio del servidor',"
                " finished_at = ? WHERE status IN ('queued', 'running')",
                (time.time(),),
            )
            self._conn.commit()
        return cur.rowcount

    def close(self) -> None:
        with self._lock:
            self._conn.close()

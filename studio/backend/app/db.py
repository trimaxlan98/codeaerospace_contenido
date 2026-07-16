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

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    quality TEXT NOT NULL,
    style_block TEXT DEFAULT '',
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS clips (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id),
    position INTEGER NOT NULL,
    title TEXT NOT NULL,
    script TEXT NOT NULL DEFAULT '',
    scene TEXT DEFAULT '',
    final_state TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    job_id TEXT,
    rendered_hash TEXT,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_clips_project ON clips(project_id, position);
"""

# Migraciones aditivas (ALTER TABLE ADD COLUMN es no destructivo en SQLite).
MIGRATIONS = (
    ("size_bytes", "ALTER TABLE jobs ADD COLUMN size_bytes INTEGER"),
    ("thumb_path", "ALTER TABLE jobs ADD COLUMN thumb_path TEXT"),
    ("project_id", "ALTER TABLE jobs ADD COLUMN project_id TEXT"),
    ("clip_id", "ALTER TABLE jobs ADD COLUMN clip_id TEXT"),
    ("content_hash", "ALTER TABLE jobs ADD COLUMN content_hash TEXT"),
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

    # ── proyectos ────────────────────────────────────────────────────────────

    def insert_project(self, p: dict) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO projects (id, name, description, quality, style_block,"
                " created_at, updated_at)"
                " VALUES (:id, :name, :description, :quality, :style_block,"
                " :created_at, :updated_at)",
                p,
            )
            self._conn.commit()

    def get_project(self, pid: str) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM projects WHERE id = ?", (pid,)
            ).fetchone()
        return dict(row) if row else None

    def list_projects(self) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def update_project(self, pid: str, **fields) -> None:
        if not fields:
            return
        cols = ", ".join(f"{k} = :{k}" for k in fields)
        fields["id"] = pid
        with self._lock:
            self._conn.execute(f"UPDATE projects SET {cols} WHERE id = :id", fields)
            self._conn.commit()

    def delete_project(self, pid: str) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM clips WHERE project_id = ?", (pid,))
            self._conn.execute("DELETE FROM projects WHERE id = ?", (pid,))
            self._conn.commit()

    # ── clips ────────────────────────────────────────────────────────────────

    def insert_clip(self, c: dict) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO clips (id, project_id, position, title, script, scene,"
                " final_state, notes, job_id, rendered_hash, created_at, updated_at)"
                " VALUES (:id, :project_id, :position, :title, :script, :scene,"
                " :final_state, :notes, :job_id, :rendered_hash, :created_at, :updated_at)",
                c,
            )
            self._conn.commit()

    def get_clip(self, cid: str) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM clips WHERE id = ?", (cid,)
            ).fetchone()
        return dict(row) if row else None

    def list_clips(self, pid: str) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM clips WHERE project_id = ? ORDER BY position", (pid,)
            ).fetchall()
        return [dict(r) for r in rows]

    def update_clip(self, cid: str, **fields) -> None:
        if not fields:
            return
        cols = ", ".join(f"{k} = :{k}" for k in fields)
        fields["id"] = cid
        with self._lock:
            self._conn.execute(f"UPDATE clips SET {cols} WHERE id = :id", fields)
            self._conn.commit()

    def delete_clip(self, cid: str) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM clips WHERE id = ?", (cid,))
            self._conn.commit()

    def clip_job_ids(self) -> set[str]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT job_id FROM clips WHERE job_id IS NOT NULL"
            ).fetchall()
        return {r["job_id"] for r in rows}

    def clips_unlink_job(self, job_id: str) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE clips SET job_id = NULL, rendered_hash = NULL WHERE job_id = ?",
                (job_id,),
            )
            self._conn.commit()

    def renumber_clips(self, pid: str, ordered_ids: list[str]) -> None:
        with self._lock:
            self._conn.executemany(
                "UPDATE clips SET position = ? WHERE id = ? AND project_id = ?",
                [(i, cid, pid) for i, cid in enumerate(ordered_ids)],
            )
            self._conn.commit()

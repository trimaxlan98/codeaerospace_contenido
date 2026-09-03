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

-- Fila unica (id=1): password vigente + flag de cambio obligatorio. Vive en
-- la DB (mutable) en vez de en /etc/manimstudio/env (solo lectura para el
-- proceso, ver ReadOnlyPaths/ProtectSystem del unit) para poder cambiarla
-- desde /api/change-password sin reiniciar el servicio.
CREATE TABLE IF NOT EXISTS auth (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    password_hash TEXT NOT NULL,
    must_change_password INTEGER NOT NULL DEFAULT 0,
    updated_at REAL NOT NULL
);
"""

# Migraciones aditivas (ALTER TABLE ADD COLUMN es no destructivo en SQLite),
# por tabla. Las columnas nuevas viven SOLO aqui, no en SCHEMA: asi una base
# nueva y una existente pasan por el mismo camino.
MIGRATIONS = {
    "jobs": (
        ("size_bytes", "ALTER TABLE jobs ADD COLUMN size_bytes INTEGER"),
        ("thumb_path", "ALTER TABLE jobs ADD COLUMN thumb_path TEXT"),
        ("project_id", "ALTER TABLE jobs ADD COLUMN project_id TEXT"),
        ("clip_id", "ALTER TABLE jobs ADD COLUMN clip_id TEXT"),
        ("content_hash", "ALTER TABLE jobs ADD COLUMN content_hash TEXT"),
        # Formato PEDIDO al renderizar; resolucion MEDIDA sobre el archivo
        # que salio (ffprobe). Se guardan las dos: si no coinciden, es que
        # la escena no aplico el lienzo y hay que verlo, no taparlo.
        ("formato", "ALTER TABLE jobs ADD COLUMN formato TEXT NOT NULL"
                    " DEFAULT 'horizontal'"),
        ("resolution", "ALTER TABLE jobs ADD COLUMN resolution TEXT"),
        # Fondo PEDIDO al renderizar una presentacion. Viaja con el job
        # misma razon que el formato: un reintento tiene que producir el
        # MISMO archivo que el intento original.
        ("fondo", "ALTER TABLE jobs ADD COLUMN fondo TEXT NOT NULL"
                  " DEFAULT 'marca'"),
        # Mezcla de audio del promo: el mp4 sonorizado vive AL LADO del mudo
        # (re-mezclar no obliga a re-renderizar) y el hash dice si sigue
        # correspondiendo al manifiesto y al video actuales.
        ("audio_path", "ALTER TABLE jobs ADD COLUMN audio_path TEXT"),
        ("audio_hash", "ALTER TABLE jobs ADD COLUMN audio_hash TEXT"),
        # Informe de verificacion del promo (costura del bucle, duracion,
        # audio y frames), medido sobre el archivo que la app sirve.
        ("verify_json", "ALTER TABLE jobs ADD COLUMN verify_json TEXT"),
        ("verify_hash", "ALTER TABLE jobs ADD COLUMN verify_hash TEXT"),
    ),
    "clips": (
        # Manifiesto de audio del promo (misma forma que el promo.json de
        # los promos escritos a mano). NULL en un clip de curso.
        ("audio_json", "ALTER TABLE clips ADD COLUMN audio_json TEXT"),
    ),
    "projects": (
        ("tipo", "ALTER TABLE projects ADD COLUMN tipo TEXT NOT NULL"
                 " DEFAULT 'curso'"),
        ("formato", "ALTER TABLE projects ADD COLUMN formato TEXT NOT NULL"
                    " DEFAULT 'horizontal'"),
        # Color de fondo de una PRESENTACION: lo elige quien
        # presenta, no la marca (una plantilla de tesis suele ser blanca).
        # Es una columna y no parte del style_block porque el runner tiene
        # que pasarlo por entorno al renderizar, igual que el formato.
        ("fondo", "ALTER TABLE projects ADD COLUMN fondo TEXT NOT NULL"
                  " DEFAULT 'marca'"),
        # Estilo visual con NOMBRE ("lienzo", "consola"...): lo declara el
        # curso.json de los verticales y no se puede deducir del style_block
        # sin adivinar. Vive aqui para que exportar las fuentes devuelva el
        # mismo manifiesto que entro.
        ("estilo", "ALTER TABLE projects ADD COLUMN estilo TEXT NOT NULL"
                   " DEFAULT ''"),
    ),
}


class Database:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.executescript(SCHEMA)
            for tabla, migraciones in MIGRATIONS.items():
                cols = {r["name"] for r in
                        self._conn.execute(f"PRAGMA table_info({tabla})")}
                for col, ddl in migraciones:
                    if col not in cols:
                        self._conn.execute(ddl)
            self._conn.commit()

    def insert_job(self, job: dict) -> None:
        # project_id/clip_id/content_hash son opcionales (jobs sueltos de
        # /api/jobs no los traen): se completan con None si faltan.
        job = {"project_id": None, "clip_id": None, "content_hash": None,
               "formato": "horizontal", "fondo": "marca", **job}
        with self._lock:
            self._conn.execute(
                "INSERT INTO jobs (id, scene, quality, timeout, status, script,"
                " created_at, project_id, clip_id, content_hash, formato, fondo)"
                " VALUES (:id, :scene, :quality, :timeout, :status, :script,"
                " :created_at, :project_id, :clip_id, :content_hash, :formato,"
                " :fondo)",
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
                " project_id, clip_id, formato, fondo, resolution, audio_path,"
                " audio_hash, length(script) AS script_len"
                " FROM jobs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    def project_jobs(self, pid: str, limit: int = 500) -> list[dict]:
        """Jobs de un proyecto, del mas reciente al mas viejo.

        `list_jobs` no filtra, y el progreso de un lote necesita solo los de
        un curso: recorrer las ~40 000 filas del historial para quedarse con
        veinte seria absurdo en un endpoint que la interfaz sondea.
        """
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, scene, quality, status, error, created_at,"
                " started_at, finished_at, size_bytes, clip_id, project_id"
                " FROM jobs WHERE project_id = ?"
                " ORDER BY created_at DESC LIMIT ?",
                (pid, limit),
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

    # ── autenticacion (password mutable + flag de cambio obligatorio) ─────────

    def ensure_auth_seed(self, password_hash: str) -> None:
        """Siembra la fila unica de auth desde el hash de entorno la primera vez.

        Solo inserta si la tabla esta vacia: no pisa una password ya cambiada
        por el usuario en una instalacion existente. must_change_password
        arranca en 0 (comportamiento historico); forzar el cambio en un
        usuario concreto es una operacion explicita via set_password().
        """
        with self._lock:
            row = self._conn.execute("SELECT 1 FROM auth WHERE id = 1").fetchone()
            if row is None:
                self._conn.execute(
                    "INSERT INTO auth (id, password_hash, must_change_password, updated_at)"
                    " VALUES (1, ?, 0, ?)",
                    (password_hash, time.time()),
                )
                self._conn.commit()

    def get_auth(self) -> dict | None:
        with self._lock:
            row = self._conn.execute("SELECT * FROM auth WHERE id = 1").fetchone()
        return dict(row) if row else None

    def set_password(self, password_hash: str, must_change_password: bool) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE auth SET password_hash = ?, must_change_password = ?, updated_at = ?"
                " WHERE id = 1",
                (password_hash, int(must_change_password), time.time()),
            )
            self._conn.commit()

    # ── proyectos ────────────────────────────────────────────────────────────

    def insert_project(self, p: dict) -> None:
        # Los defectos repiten los de projects.py (TIPO_DEFECTO /
        # FORMATO_DEFECTO); no se importa de alli para no cerrar el ciclo
        # projects -> db -> projects.
        p = {"tipo": "curso", "formato": "horizontal", "fondo": "marca",
             "estilo": "", **p}
        with self._lock:
            self._conn.execute(
                "INSERT INTO projects (id, name, description, quality, style_block,"
                " tipo, formato, fondo, estilo, created_at, updated_at)"
                " VALUES (:id, :name, :description, :quality, :style_block,"
                " :tipo, :formato, :fondo, :estilo, :created_at, :updated_at)",
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

    def reorder_clips(self, pid: str, cid: str, position: int | None,
                       delete: bool = False) -> list[str] | None:
        """Mueve o borra `cid` y renumera el proyecto bajo UN solo lock.

        Lee el orden actual, borra o reubica el clip y renumera todo en la
        misma seccion critica (evita la carrera de leer-luego-renumerar en
        dos llamadas separadas). Devuelve el nuevo orden de ids, o None si
        `cid` no pertenece a `pid` (el llamador decide como reportarlo).
        """
        with self._lock:
            rows = self._conn.execute(
                "SELECT id FROM clips WHERE project_id = ? ORDER BY position", (pid,)
            ).fetchall()
            ids = [r["id"] for r in rows]
            if cid not in ids:
                return None
            ids.remove(cid)
            if delete:
                self._conn.execute("DELETE FROM clips WHERE id = ?", (cid,))
            else:
                position = max(0, min(position, len(ids)))
                ids.insert(position, cid)
            self._conn.executemany(
                "UPDATE clips SET position = ? WHERE id = ? AND project_id = ?",
                [(i, x, pid) for i, x in enumerate(ids)],
            )
            self._conn.commit()
        return ids

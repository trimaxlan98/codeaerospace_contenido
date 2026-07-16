"""Servicio de Proyectos (cursos): agrupan clips ordenados con continuidad.

Un proyecto fija la calidad de render (resolucion/fps) para todos sus
clips, de forma que los videos resultantes se puedan unir sin recodificar
(`ffmpeg -f concat -c copy`). El estilo visual compartido (`style_block`)
se antepone al script de cada clip antes de renderizar; el hash del
compuesto detecta cuando un clip quedo desactualizado respecto a su
ultimo render bueno (`stale`).

Este modulo es puro (sin FastAPI, sin cola de jobs): la integracion con
la API y el JobManager llega en el Sprint 2.
"""

import hashlib
import re
import time
import uuid

from .db import Database

QUALITY_SPECS = {
    "ql": {"resolution": "854x480", "fps": 15},
    "qm": {"resolution": "1280x720", "fps": 30},
    "qh": {"resolution": "1920x1080", "fps": 60},
}
QUALITIES = set(QUALITY_SPECS)

STYLE_MARKER = "# --- fin estilo del proyecto ---"


def compose_script(style_block: str, script: str) -> str:
    """Antepone el estilo del proyecto al script del clip.

    Sin estilo (vacio o solo espacios) devuelve el script tal cual, para
    que los proyectos sin `style_block` se comporten igual que un render
    suelto de hoy.
    """
    if not style_block.strip():
        return script
    return f"{style_block.rstrip()}\n\n{STYLE_MARKER}\n\n{script}"


def content_hash(style_block: str, script: str, scene: str) -> str:
    """sha256 hex del script compuesto (estilo + clip) mas la escena.

    La escena participa del hash a proposito: dos renders del mismo script
    compuesto pero con `scene` distinta producen videos distintos (el
    script puede definir varias escenas, p.ej. Intro y Outro), asi que un
    cambio de escena sin tocar el script debe marcar el clip como `stale`
    igual que un cambio de script. La combinacion es determinista: mismo
    (style_block, script, scene) siempre produce el mismo hash.
    """
    composed = compose_script(style_block, script)
    digest = hashlib.sha256(composed.encode("utf-8"))
    digest.update(b"\n# scene: " + scene.encode("utf-8"))
    return digest.hexdigest()


def style_offset(style_block: str) -> int:
    """Lineas que el estilo antepone al script del clip (0 si no hay estilo)."""
    if not style_block.strip():
        return 0
    return len(compose_script(style_block, "X").splitlines()) - 1


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
    return slug or "clip"


def project_slug(name: str) -> str:
    """Slug de nombre de proyecto, para el nombre de archivo del zip."""
    return _slugify(name)


def clip_public(clip: dict) -> dict:
    """Vista del clip sin el script completo (evita respuestas pesadas)."""
    public = {k: v for k, v in clip.items() if k != "script"}
    public["script_len"] = len(clip.get("script") or "")
    return public


class ProjectService:
    def __init__(self, db: Database) -> None:
        self.db = db

    # ── proyectos ────────────────────────────────────────────────────────────

    def create_project(self, name: str, description: str, quality: str,
                        style_block: str) -> dict:
        if quality not in QUALITIES:
            raise ValueError(f"calidad invalida: {quality}")
        now = time.time()
        project = {
            "id": uuid.uuid4().hex[:16],
            "name": name,
            "description": description or "",
            "quality": quality,
            "style_block": style_block or "",
            "created_at": now,
            "updated_at": now,
        }
        self.db.insert_project(project)
        return project

    def get_project_detail(self, pid: str) -> dict | None:
        project = self.db.get_project(pid)
        if not project:
            return None
        clips = []
        for clip in self.db.list_clips(pid):
            expected = content_hash(project["style_block"], clip.get("script") or "",
                                    clip.get("scene") or "")
            has_render = bool(clip.get("job_id"))
            stale = has_render and clip.get("rendered_hash") != expected
            if not has_render:
                status = "no_render"
            elif stale:
                status = "stale"
            else:
                status = "rendered"
            clips.append({**clip_public(clip), "stale": stale, "status": status})
        return {**project, "clips": clips}

    def list_projects_summary(self) -> list[dict]:
        summaries = []
        for project in self.db.list_projects():
            clips = self.db.list_clips(project["id"])
            rendered_count = stale_count = 0
            for clip in clips:
                if not clip.get("job_id"):
                    continue
                expected = content_hash(project["style_block"], clip.get("script") or "",
                                        clip.get("scene") or "")
                if clip.get("rendered_hash") != expected:
                    stale_count += 1
                else:
                    rendered_count += 1
            public = {k: v for k, v in project.items() if k != "style_block"}
            summaries.append({
                **public,
                "clip_count": len(clips),
                "rendered_count": rendered_count,
                "stale_count": stale_count,
            })
        return summaries

    def update_project(self, pid: str, **fields) -> dict:
        if "quality" in fields:
            clips = self.db.list_clips(pid)
            if any(c.get("job_id") for c in clips):
                raise ValueError(
                    "no se puede cambiar la calidad: hay clips con render vigente"
                )
        fields["updated_at"] = time.time()
        self.db.update_project(pid, **fields)
        return self.db.get_project(pid)

    def delete_project(self, pid: str) -> None:
        # Los jobs conservan project_id/clip_id como texto historico: solo
        # se borran las filas de projects/clips (los jobs quedan sueltos).
        self.db.delete_project(pid)

    # ── clips ────────────────────────────────────────────────────────────────

    def add_clip(self, pid: str, title: str, script: str = "", scene: str = "",
                 position: int | None = None, adopt_job: dict | None = None) -> dict:
        project = self.db.get_project(pid)
        if not project:
            raise ValueError("proyecto no encontrado")

        job_id = None
        rendered_hash = None
        if adopt_job:
            script = adopt_job.get("script") or ""
            scene = adopt_job.get("scene") or ""
            composed = compose_script(project["style_block"], script)
            if adopt_job.get("quality") == project["quality"] and composed == adopt_job.get("script"):
                job_id = adopt_job.get("id")
                rendered_hash = content_hash(project["style_block"], script, scene)

        existing = self.db.list_clips(pid)
        n = len(existing)
        if position is None:
            position = n
        else:
            position = max(0, min(position, n))

        cid = uuid.uuid4().hex[:16]
        now = time.time()
        clip = {
            "id": cid, "project_id": pid, "position": position, "title": title,
            "script": script, "scene": scene, "final_state": "", "notes": "",
            "job_id": job_id, "rendered_hash": rendered_hash,
            "created_at": now, "updated_at": now,
        }
        self.db.insert_clip(clip)

        ordered_ids = [c["id"] for c in existing]
        ordered_ids.insert(position, cid)
        self.db.renumber_clips(pid, ordered_ids)

        return self.db.get_clip(cid)

    def update_clip(self, cid: str, **fields) -> dict:
        fields["updated_at"] = time.time()
        self.db.update_clip(cid, **fields)
        return self.db.get_clip(cid)

    def move_clip(self, pid: str, cid: str, position: int) -> None:
        # list+renumber en una sola seccion critica (evita la carrera entre
        # leer el orden y renumerar que existia con list_clips+renumber_clips).
        if self.db.reorder_clips(pid, cid, position) is None:
            raise ValueError("clip no encontrado en el proyecto")

    def delete_clip(self, pid: str, cid: str) -> None:
        # Misma seccion critica que move_clip; ademas valida que el clip
        # pertenezca al proyecto antes de borrar (igual que move_clip).
        if self.db.reorder_clips(pid, cid, position=None, delete=True) is None:
            raise ValueError("clip no encontrado en el proyecto")

    # ── ciclo de vida del render ─────────────────────────────────────────────

    def handle_job_done(self, job: dict) -> None:
        """Al terminar un job ligado a un clip, actualiza el render vigente.

        Solo enlaza si el clip aun existe y sigue perteneciendo al mismo
        proyecto que el job (evita colgar referencias tras borrados a
        mitad de render).
        """
        clip_id = job.get("clip_id")
        if not clip_id:
            return
        clip = self.db.get_clip(clip_id)
        if not clip or clip.get("project_id") != job.get("project_id"):
            return
        self.db.update_clip(
            clip_id,
            job_id=job["id"],
            rendered_hash=job.get("content_hash"),
            updated_at=time.time(),
        )

    # ── exportacion ──────────────────────────────────────────────────────────

    def export_manifest(self, pid: str, jobs_by_id: dict[str, dict]) -> dict:
        project = self.db.get_project(pid)
        if not project:
            raise ValueError("proyecto no encontrado")
        spec = QUALITY_SPECS[project["quality"]]

        items = []
        for clip in self.db.list_clips(pid):
            job_id = clip.get("job_id")
            if not job_id:
                continue
            job = jobs_by_id.get(job_id)
            if not job:
                continue
            expected = content_hash(project["style_block"], clip.get("script") or "",
                                    clip.get("scene") or "")
            if clip.get("rendered_hash") != expected:
                continue  # desactualizado: no entra en el manifiesto
            filename = f"{clip['position'] + 1:03d}-{_slugify(clip['title'])}.mp4"
            items.append({
                "clip_id": clip["id"],
                "position": clip["position"],
                "title": clip["title"],
                "filename": filename,
                "job_id": job_id,
                "content_hash": clip.get("rendered_hash"),
                "final_state": clip.get("final_state") or "",
                "notes": clip.get("notes") or "",
                "video_path": job.get("video_path"),
                "size_bytes": job.get("size_bytes"),
            })

        return {
            "project_id": pid,
            "name": project["name"],
            "quality": project["quality"],
            "resolution": spec["resolution"],
            "fps": spec["fps"],
            "clips": items,
        }

    def export_full_manifest(self, pid: str, jobs_by_id: dict[str, dict]) -> dict:
        """Manifiesto completo del curso, para los endpoints /export y /archive.

        A diferencia de `export_manifest` (uso interno del Sprint 1, que solo
        lista clips con render vigente), este incluye TODOS los clips del
        proyecto -- con o sin render, vigente o no -- para que la UI y el zip
        de exportacion puedan mostrar el estado completo del curso. `has_video`
        solo es `True` si el clip tiene un render vigente (no `stale`) con
        video asociado: un clip desactualizado no entra en `concat` aunque su
        video anterior siga en disco.
        """
        project = self.db.get_project(pid)
        if not project:
            raise ValueError("proyecto no encontrado")
        spec = QUALITY_SPECS[project["quality"]]

        clips = []
        concat = []
        for clip in self.db.list_clips(pid):
            job_id = clip.get("job_id")
            expected = content_hash(project["style_block"], clip.get("script") or "",
                                    clip.get("scene") or "")
            has_render = bool(job_id)
            stale = has_render and clip.get("rendered_hash") != expected
            job = jobs_by_id.get(job_id) if job_id else None
            # Alineado con /api/jobs/{id}/video (main.py): solo cuenta como
            # video vigente si el job terminó en "done" (evita ofrecer un
            # video_path de un job aún en curso o fallido).
            has_video = bool(job and job.get("status") == "done"
                             and job.get("video_path") and not stale)
            filename = f"{clip['position'] + 1:03d}-{_slugify(clip['title'])}.mp4"

            duration_s = None
            size_bytes = None
            video_path = None
            if has_video:
                started = job.get("started_at")
                finished = job.get("finished_at")
                if started is not None and finished is not None:
                    duration_s = finished - started
                size_bytes = job.get("size_bytes")
                video_path = job.get("video_path")

            clips.append({
                "position": clip["position"],
                "title": clip["title"],
                "scene": clip.get("scene") or "",
                "filename": filename,
                "has_video": has_video,
                "duration_s": duration_s,
                "size_bytes": size_bytes,
                "stale": stale,
                # Internos, no forman parte del manifiesto publico (se
                # descartan antes de responder / escribir manifest.json):
                "video_path": video_path,
                "job_id": job_id if has_video else None,
            })
            if has_video:
                concat.append(f"file '{filename}'")

        return {
            "project": {
                "id": project["id"],
                "name": project["name"],
                "description": project["description"],
                "quality": project["quality"],
            },
            "specs": spec,
            "generated_at": time.time(),
            "clips": clips,
            "concat": concat,
        }

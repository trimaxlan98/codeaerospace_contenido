"""API HTTP de Proyectos (cursos): CRUD de proyectos/clips y su enlace con
el JobManager para renderizar clips con el estilo del proyecto compuesto.

Se monta como router aparte (`make_router`) en vez de vivir en `main.py`
para no importar los globals de ahi (evita un ciclo de import): `main.py`
crea `db`/`manager`/`service` y llama a `make_router(cfg, db, manager,
service)` despues.
"""

import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .auth import require_auth
from .db import Database
from .jobs import JobManager
from .projects import (QUALITIES, ProjectService, clip_public, compose_script,
                       content_hash, style_offset)
from .scenes import detect_scenes

RE_JOB_ID = re.compile(r"^[a-f0-9]{8,32}$")


# ── modelos ───────────────────────────────────────────────────────────────────

class ProjectCreateBody(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    quality: str
    style_block: str = ""


class ProjectUpdateBody(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    quality: str | None = None
    style_block: str | None = None


class ClipCreateBody(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    script: str = ""
    scene: str = Field(default="", max_length=128)
    position: int | None = None
    from_job_id: str | None = None


class ClipUpdateBody(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    script: str | None = None
    scene: str | None = None
    final_state: str | None = None
    notes: str | None = None


class MoveBody(BaseModel):
    position: int


def make_router(cfg, db: Database, manager: JobManager, service: ProjectService) -> APIRouter:
    router = APIRouter(prefix="/api/projects", tags=["projects"])

    def _check_style_size(text: str) -> None:
        if len(text.encode("utf-8", errors="replace")) > cfg.max_script_bytes:
            raise HTTPException(status_code=413, detail="Bloque de estilo demasiado grande")

    def _check_clip_script_size(text: str) -> None:
        if len(text.encode("utf-8", errors="replace")) > cfg.max_script_bytes:
            raise HTTPException(status_code=413, detail="Script demasiado grande")

    def _check_script(script: str) -> None:
        if len(script.encode("utf-8", errors="replace")) > cfg.max_script_bytes:
            raise HTTPException(status_code=413, detail="Script demasiado grande")
        if not script.strip():
            raise HTTPException(status_code=422, detail="Script vacio")

    def _check_quota() -> None:
        quota = cfg.max_storage_mb * 1024 * 1024
        used = manager.storage_usage()
        if used >= quota:
            raise HTTPException(
                status_code=507,
                detail=(f"Almacenamiento lleno: {used / 2**20:.0f} MB usados de "
                        f"{cfg.max_storage_mb} MB. Borra videos de la Biblioteca "
                        "para liberar espacio."))

    def _require_project(pid: str) -> dict:
        project = db.get_project(pid)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return project

    def _require_clip(pid: str, cid: str) -> dict:
        clip = db.get_clip(cid)
        if not clip or clip.get("project_id") != pid:
            raise HTTPException(status_code=404, detail="Clip no encontrado")
        return clip

    # ── proyectos ────────────────────────────────────────────────────────────

    @router.get("")
    async def list_projects(_=Depends(require_auth)):
        return {"projects": service.list_projects_summary()}

    @router.post("", status_code=201)
    async def create_project(body: ProjectCreateBody, _=Depends(require_auth)):
        if body.quality not in QUALITIES:
            raise HTTPException(status_code=422, detail="Calidad invalida (ql/qm/qh)")
        _check_style_size(body.style_block)
        return service.create_project(body.name, body.description, body.quality,
                                      body.style_block)

    @router.get("/{pid}")
    async def get_project(pid: str, _=Depends(require_auth)):
        detail = service.get_project_detail(pid)
        if not detail:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return detail

    @router.patch("/{pid}")
    async def update_project(pid: str, body: ProjectUpdateBody, _=Depends(require_auth)):
        _require_project(pid)
        raw = body.model_dump(exclude_unset=True)
        if "quality" in raw and raw["quality"] not in QUALITIES:
            raise HTTPException(status_code=422, detail="Calidad invalida (ql/qm/qh)")
        if "style_block" in raw:
            _check_style_size(raw["style_block"])
        # Whitelist explicita (M3): nunca reenviar el body crudo a update_project.
        allowed = {"name", "description", "style_block", "quality"}
        fields = {k: v for k, v in raw.items() if k in allowed}
        try:
            return service.update_project(pid, **fields)
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))

    @router.delete("/{pid}")
    async def delete_project(pid: str, _=Depends(require_auth)):
        _require_project(pid)
        service.delete_project(pid)
        return {"ok": True}

    # ── clips ────────────────────────────────────────────────────────────────

    @router.get("/{pid}/clips/{cid}/script")
    async def get_clip_script(pid: str, cid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        clip = _require_clip(pid, cid)
        return {"script": clip.get("script") or "",
                "style_offset": style_offset(project["style_block"])}

    @router.post("/{pid}/clips", status_code=201)
    async def create_clip(pid: str, body: ClipCreateBody, _=Depends(require_auth)):
        _require_project(pid)
        _check_clip_script_size(body.script)

        adopt_job = None
        if body.from_job_id is not None:
            if not RE_JOB_ID.match(body.from_job_id):
                raise HTTPException(status_code=404, detail="Job no encontrado")
            adopt_job = db.get_job(body.from_job_id)
            if not adopt_job:
                raise HTTPException(status_code=404, detail="Job no encontrado")

        try:
            clip = service.add_clip(pid, body.title, script=body.script,
                                    scene=body.scene, position=body.position,
                                    adopt_job=adopt_job)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return clip_public(clip)

    @router.patch("/{pid}/clips/{cid}")
    async def update_clip(pid: str, cid: str, body: ClipUpdateBody,
                          _=Depends(require_auth)):
        _require_clip(pid, cid)
        raw = body.model_dump(exclude_unset=True)
        if "script" in raw and raw["script"] is not None:
            _check_clip_script_size(raw["script"])
        # Whitelist explicita (M3): nunca reenviar el body crudo a update_clip.
        allowed = {"title", "script", "scene", "final_state", "notes"}
        fields = {k: v for k, v in raw.items() if k in allowed}
        clip = service.update_clip(cid, **fields)
        return clip_public(clip)

    @router.delete("/{pid}/clips/{cid}")
    async def delete_clip(pid: str, cid: str, _=Depends(require_auth)):
        _require_clip(pid, cid)
        try:
            service.delete_clip(pid, cid)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return {"ok": True}

    @router.post("/{pid}/clips/{cid}/move")
    async def move_clip(pid: str, cid: str, body: MoveBody, _=Depends(require_auth)):
        _require_clip(pid, cid)
        try:
            service.move_clip(pid, cid, body.position)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        detail = service.get_project_detail(pid)
        return {"clips": detail["clips"]}

    # ── render ───────────────────────────────────────────────────────────────

    @router.post("/{pid}/clips/{cid}/render", status_code=201)
    async def render_clip(pid: str, cid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        clip = _require_clip(pid, cid)
        if not clip.get("scene"):
            raise HTTPException(status_code=422, detail="El clip no tiene escena asignada")

        script = clip.get("script") or ""
        composed = compose_script(project["style_block"], script)
        _check_script(composed)
        try:
            available = detect_scenes(composed)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Script invalido: {e}")
        if clip["scene"] not in available:
            raise HTTPException(status_code=422,
                                detail=f"La escena '{clip['scene']}' no existe en el script")
        _check_quota()

        chash = content_hash(project["style_block"], script, clip["scene"])
        return manager.create_job(composed, clip["scene"], project["quality"],
                                  timeout=cfg.default_timeout, project_id=pid,
                                  clip_id=cid, content_hash=chash)

    @router.post("/{pid}/render-stale")
    async def render_stale(pid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        detail = service.get_project_detail(pid)

        queued: list[str] = []
        skipped: list[dict] = []
        for clip_summary in detail["clips"]:
            if clip_summary["status"] not in ("stale", "no_render"):
                continue
            cid = clip_summary["id"]
            clip = db.get_clip(cid)
            script = clip.get("script") or ""
            scene = clip.get("scene") or ""

            if not scene:
                skipped.append({"clip_id": cid, "error": "el clip no tiene escena asignada"})
                continue

            composed = compose_script(project["style_block"], script)
            try:
                _check_script(composed)
                available = detect_scenes(composed)
            except HTTPException as e:
                skipped.append({"clip_id": cid, "error": e.detail})
                continue
            except ValueError as e:
                skipped.append({"clip_id": cid, "error": f"script invalido: {e}"})
                continue
            if scene not in available:
                skipped.append({"clip_id": cid,
                               "error": f"la escena '{scene}' no existe en el script"})
                continue

            try:
                _check_quota()
            except HTTPException as e:
                skipped.append({"clip_id": cid, "error": e.detail})
                continue

            chash = content_hash(project["style_block"], script, scene)
            job = manager.create_job(composed, scene, project["quality"],
                                     timeout=cfg.default_timeout, project_id=pid,
                                     clip_id=cid, content_hash=chash)
            queued.append(job["id"])

        return {"queued": queued, "skipped": skipped}

    return router

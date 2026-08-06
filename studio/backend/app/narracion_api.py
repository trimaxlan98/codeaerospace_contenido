"""API HTTP de narracion de proyectos: estado por clip, generacion en
segundo plano y descarga de audio/texto.

Router aparte (`make_router`) por la misma razon que projects_api: `main.py`
crea `db`/`narracion` y monta el router despues, sin ciclos de import.
"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .auth import require_auth
from .db import Database
from .narracion import NarracionService, etiqueta_clip


class NarracionStartBody(BaseModel):
    clips: list[str] | None = Field(default=None, max_length=200)
    force: bool = False


def make_router(cfg, db: Database, narracion: NarracionService) -> APIRouter:
    router = APIRouter(prefix="/api/projects", tags=["narracion"])

    def _require_project(pid: str) -> dict:
        project = db.get_project(pid)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return project

    def _clip_file(project: dict, cid: str, ext: str) -> Path:
        clip = db.get_clip(cid)
        if not clip or clip.get("project_id") != project["id"]:
            raise HTTPException(status_code=404, detail="Clip no encontrado")
        destino = narracion.destino(project)
        estado = narracion._leer_estado(destino)
        previo = estado.get(cid) or {}
        etiqueta = previo.get("etiqueta") or etiqueta_clip(
            clip["position"], clip["title"])
        path = (destino / f"{etiqueta}{ext}").resolve()
        # Defensa en profundidad (misma politica que /api/jobs/{id}/video):
        # el archivo debe vivir dentro del directorio de guiones del proyecto.
        if not path.is_file() or destino.resolve() not in path.parents:
            raise HTTPException(status_code=404, detail="Narracion no disponible")
        return path

    @router.get("/{pid}/narracion")
    async def estado(pid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        return narracion.estado_proyecto(project)

    @router.post("/{pid}/narracion", status_code=202)
    async def generar(pid: str, body: NarracionStartBody,
                      _=Depends(require_auth)):
        project = _require_project(pid)
        try:
            res = narracion.start(project, clip_ids=body.clips,
                                  force=body.force)
        except ValueError as e:
            status = 503 if "service account" in str(e) else 409
            raise HTTPException(status_code=status, detail=str(e))
        return res | {"run": narracion.run_public()}

    @router.post("/{pid}/narracion/cancel")
    async def cancelar(pid: str, _=Depends(require_auth)):
        _require_project(pid)
        if not narracion.cancel():
            raise HTTPException(status_code=409,
                                detail="No hay ninguna narracion en curso")
        return {"ok": True}

    @router.get("/{pid}/narracion/{cid}/audio")
    async def audio(pid: str, cid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        path = _clip_file(project, cid, ".wav")
        return FileResponse(path, media_type="audio/wav", filename=path.name)

    @router.get("/{pid}/narracion/{cid}/texto")
    async def texto(pid: str, cid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        md = _clip_file(project, cid, ".md")
        txt = md.with_suffix(".txt")
        return {"md": md.read_text(),
                "txt": txt.read_text() if txt.is_file() else ""}

    return router

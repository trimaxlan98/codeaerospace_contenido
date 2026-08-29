"""API HTTP de la presentacion de presentacion: estado, armado y descarga del .pptx.

Router aparte por la misma razon que `pelicula_api`: `main.py` construye los
servicios y monta el router despues, sin ciclos de import.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .auth import require_auth
from .db import Database
from .presentaciones import DECK_DEFECTO, PresentacionError, PresentacionService

MIME_PPTX = ("application/vnd.openxmlformats-officedocument"
             ".presentationml.presentation")


class PresentacionBody(BaseModel):
    deck: str = DECK_DEFECTO
    bucle: bool = False


def make_router(cfg, db: Database, presentaciones: PresentacionService) -> APIRouter:
    router = APIRouter(prefix="/api/projects", tags=["presentacion"])

    def _require_presentacion(pid: str) -> dict:
        project = db.get_project(pid)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        if (project.get("tipo") or "curso") != "presentacion":
            raise HTTPException(
                status_code=409,
                detail="Este proyecto no es una presentacion de presentación")
        return project

    @router.get("/{pid}/presentacion")
    async def estado(pid: str, _=Depends(require_auth)):
        return presentaciones.estado(_require_presentacion(pid))

    @router.post("/{pid}/presentacion", status_code=202)
    async def armar(pid: str, body: PresentacionBody, _=Depends(require_auth)):
        project = _require_presentacion(pid)
        try:
            res = presentaciones.start(project, body.model_dump())
        except PresentacionError as e:
            raise HTTPException(status_code=409, detail=str(e))
        return res | {"run": presentaciones.estado(project)["run"]}

    @router.post("/{pid}/presentacion/cancel")
    async def cancelar(pid: str, _=Depends(require_auth)):
        _require_presentacion(pid)
        if not presentaciones.cancel():
            raise HTTPException(status_code=409,
                                detail="No hay ningún armado en curso")
        return {"ok": True}

    @router.get("/{pid}/presentacion/deck")
    async def deck(pid: str, _=Depends(require_auth)):
        project = _require_presentacion(pid)
        path = presentaciones.deck_path(project)
        if path is None:
            raise HTTPException(status_code=404,
                                detail="Esta presentacion todavía no está armada")
        return FileResponse(path, media_type=MIME_PPTX,
                            filename=presentaciones.nombre_descarga(project))

    @router.delete("/{pid}/presentacion")
    async def borrar(pid: str, _=Depends(require_auth)):
        project = _require_presentacion(pid)
        if presentaciones.running:
            raise HTTPException(
                status_code=409,
                detail="Hay un armado en curso; cancélalo primero")
        if not presentaciones.borrar(project):
            raise HTTPException(status_code=404, detail="No hay deck que borrar")
        return {"ok": True}

    return router

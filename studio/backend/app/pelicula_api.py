"""API HTTP de la pelicula de un curso: estado, montaje y descarga.

Router aparte por la misma razon que `narracion_api`: `main.py` construye los
servicios y monta el router despues, sin ciclos de import.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .auth import require_auth
from .db import Database
from .pelicula import (DUR_DEFECTO, DUR_MAX, DUR_MIN, PeliculaError,
                       PeliculaService, TRANSICION_DEFECTO)


class PeliculaBody(BaseModel):
    transicion: str = TRANSICION_DEFECTO
    duracion_transicion: float = Field(default=DUR_DEFECTO, ge=DUR_MIN,
                                       le=DUR_MAX)
    narracion: bool = True
    intro_job_id: str | None = Field(default=None, max_length=32)
    cierre_job_id: str | None = Field(default=None, max_length=32)


def make_router(cfg, db: Database, pelicula: PeliculaService) -> APIRouter:
    router = APIRouter(prefix="/api/projects", tags=["pelicula"])

    def _require_project(pid: str) -> dict:
        project = db.get_project(pid)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
        return project

    @router.get("/{pid}/pelicula")
    async def estado(pid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        return pelicula.estado(project)

    @router.post("/{pid}/pelicula", status_code=202)
    async def montar(pid: str, body: PeliculaBody, _=Depends(require_auth)):
        project = _require_project(pid)
        try:
            res = pelicula.start(project, body.model_dump())
        except PeliculaError as e:
            raise HTTPException(status_code=409, detail=str(e))
        return res | {"run": pelicula.estado(project)["run"]}

    @router.post("/{pid}/pelicula/cancel")
    async def cancelar(pid: str, _=Depends(require_auth)):
        _require_project(pid)
        if not pelicula.cancel():
            raise HTTPException(status_code=409,
                                detail="No hay ningun montaje en curso")
        return {"ok": True}

    @router.get("/{pid}/pelicula/video")
    async def video(pid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        path = pelicula.video_path(project)
        if path is None:
            raise HTTPException(status_code=404,
                                detail="Este curso todavia no esta montado")
        # FileResponse trae soporte de Range: el navegador puede saltar en un
        # archivo de media hora sin descargarlo entero.
        return FileResponse(path, media_type="video/mp4",
                            filename=pelicula.nombre_descarga(project))

    @router.delete("/{pid}/pelicula")
    async def borrar(pid: str, _=Depends(require_auth)):
        project = _require_project(pid)
        if pelicula.running:
            raise HTTPException(status_code=409,
                                detail="Hay un montaje en curso; cancelalo primero")
        if not pelicula.borrar(project):
            raise HTTPException(status_code=404, detail="No hay pelicula que borrar")
        return {"ok": True}

    return router

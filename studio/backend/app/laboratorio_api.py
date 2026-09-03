"""API HTTP del Laboratorio (ejecutar Python de validacion en el sandbox).

Router aparte (`make_router`) por la misma razon que `pelicula_api`: `main.py`
construye el servicio y monta el router despues, sin ciclos de import.

La ejecucion se lanza **en segundo plano** y el cliente consulta el estado.
Una sonda son 1-3 s, pero el tope es de 900 s y nginx corta una peticion
mucho antes: devolver 202 con el id y dejar que la vista pregunte es lo
unico que funciona para los dos casos con el mismo codigo.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .auth import require_auth
from .laboratorio import (HISTORIAL_MAX, PLANTILLA, TIMEOUT_DEFECTO,
                          TIMEOUT_MAX, TIMEOUT_MIN, TIMEOUT_SONDA,
                          LaboratorioError, LaboratorioService)


class EjecutarBody(BaseModel):
    script: str = Field(min_length=1)
    timeout: int = Field(default=TIMEOUT_DEFECTO, ge=TIMEOUT_MIN,
                         le=TIMEOUT_MAX)
    titulo: str = Field(default="", max_length=80)


def make_router(cfg, lab: LaboratorioService) -> APIRouter:
    router = APIRouter(prefix="/api/laboratorio", tags=["laboratorio"])

    def _lanzar(meta: dict) -> dict:
        # La tarea se guarda en el propio bucle: si el backend se reinicia a
        # mitad, la ejecucion queda en "corriendo" y su directorio se puede
        # borrar. No hay reanudacion, y no debe haberla: un script a medias
        # no se repite solo.
        asyncio.get_event_loop().create_task(lab.correr(meta["id"]))
        return meta

    @router.get("")
    async def listar(_=Depends(require_auth)):
        """Las ultimas ejecuciones (sin la salida: ver el detalle)."""
        return {"ejecuciones": lab.listar(HISTORIAL_MAX),
                "ocupado": lab.ocupado,
                "plantilla": PLANTILLA,
                "timeout": {"min": TIMEOUT_MIN, "max": TIMEOUT_MAX,
                            "defecto": TIMEOUT_DEFECTO}}

    @router.get("/sondas")
    async def sondas(_=Depends(require_auth)):
        """Las `sonda_*.py` del repo: es la forma de verificar una libreria
        desde la app, sin abrir una terminal."""
        return {"sondas": lab.sondas()}

    @router.post("/sondas/{nombre}", status_code=202)
    async def correr_sonda(nombre: str, _=Depends(require_auth)):
        if not lab.existe_sonda(nombre):
            raise HTTPException(status_code=404, detail="Esa sonda no existe")
        try:
            meta = lab.crear(None, TIMEOUT_SONDA, sonda=nombre)
        except LaboratorioError as e:
            raise HTTPException(status_code=409, detail=str(e))
        return _lanzar(meta)

    @router.post("", status_code=202)
    async def ejecutar(body: EjecutarBody, _=Depends(require_auth)):
        if len(body.script.encode("utf-8", errors="replace")) > cfg.max_script_bytes:
            raise HTTPException(status_code=413, detail="Script demasiado grande")
        try:
            meta = lab.crear(body.script, body.timeout, titulo=body.titulo)
        except LaboratorioError as e:
            raise HTTPException(status_code=409, detail=str(e))
        return _lanzar(meta)

    @router.get("/{lab_id}")
    async def detalle(lab_id: str, _=Depends(require_auth)):
        meta = lab.obtener(lab_id)
        if meta is None:
            raise HTTPException(status_code=404, detail="Ejecución no encontrada")
        return meta

    @router.get("/{lab_id}/archivos/{nombre}")
    async def archivo(lab_id: str, nombre: str, _=Depends(require_auth)):
        try:
            ruta, mime = lab.archivo(lab_id, nombre)
        except LaboratorioError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return FileResponse(ruta, media_type=mime, filename=nombre)

    @router.delete("/{lab_id}")
    async def borrar(lab_id: str, _=Depends(require_auth)):
        try:
            if not lab.borrar(lab_id):
                raise HTTPException(status_code=404,
                                    detail="Ejecución no encontrada")
        except LaboratorioError as e:
            raise HTTPException(status_code=409, detail=str(e))
        return {"ok": True}

    return router

"""API de la Biblioteca de entregas (solo lectura sobre `exports/`)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from .auth import require_auth
from .entregas import EntregasService


def make_router(entregas: EntregasService) -> APIRouter:
    router = APIRouter(prefix="/api/entregas", tags=["entregas"])

    @router.get("")
    async def listar(ruta: str = Query(default="", max_length=500),
                     _=Depends(require_auth)):
        if not entregas.disponible():
            return {"ruta": "", "padre": None, "titulo": "Biblioteca",
                    "carpetas": [], "archivos": [], "bytes": 0,
                    "vacio": "todavia no hay entregas en exports/"}
        try:
            return entregas.listar(ruta)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Esa carpeta no existe")

    @router.get("/archivo/{ruta:path}")
    async def archivo(ruta: str, _=Depends(require_auth)):
        """Sirve el archivo. `FileResponse` trae Range, asi que el navegador
        puede saltar dentro de una pelicula de media hora sin bajarla."""
        try:
            path, media = entregas.archivo(ruta)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Ese archivo no existe")
        return FileResponse(path, media_type=media, filename=path.name)

    return router

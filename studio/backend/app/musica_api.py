"""Banco de musica audible.

Hermano de `sfx_api`, y por la misma razon: un desplegable con ocho nombres
—«deriva», «telemetria», «cuerdas_frias»— no dice nada. Aqui cada tema se
sintetiza una vez (`musica.py banco` dentro del contenedor, porque el backend
no tiene numpy) como una vista previa de 12 s en `exports/musica/`, y la
interfaz la reproduce antes de que nadie monte nada.

La sintesis es determinista: el mismo tema suena igual siempre, asi que basta
generar el banco una vez y no caduca. Lo que la pieza acabe llevando NO es
este wav — es una cama de la duracion exacta del video, generada al mezclar —
pero suena a esto, que es lo que hay que poder juzgar antes de elegir.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from . import audio_promo
from .auth import require_auth
from .runner_client import RunnerError


def make_router(cfg, runner) -> APIRouter:
    router = APIRouter(prefix="/api/musica", tags=["musica"])
    # Un solo turno, como la paleta: sintetizar los ocho tarda ~1 min y
    # lanzarlo dos veces a la vez no adelanta nada.
    estado = {"generando": False}

    def _listos() -> list[str]:
        """Los temas que estan Y siguen en el catalogo.

        El directorio sobrevive a los cambios de `TEMAS`: una corrida vieja
        deja wavs de temas retirados, y ofrecerlos seria ofrecer algo que la
        mezcla ya no sabe sintetizar (mismo tropiezo que la paleta de SFX).
        """
        if not cfg.musica_dir.is_dir():
            return []
        vivos = set(audio_promo.TEMAS)
        return sorted(p.stem for p in cfg.musica_dir.glob("*.wav")
                      if p.stem in vivos)

    @router.get("")
    async def listar(_=Depends(require_auth)):
        listos = set(_listos())
        temas = [dict(audio_promo.TEMAS_INFO.get(n, {}), nombre=n,
                      listo=n in listos)
                 for n in audio_promo.TEMAS]
        return {
            "temas": temas,
            "listos": sorted(listos),
            "completo": listos >= set(audio_promo.TEMAS),
            "generando": estado["generando"],
            "db_defecto": audio_promo.MUSICA_DB,
            "db_aviso": audio_promo.MUSICA_DB_AVISO,
        }

    @router.post("")
    async def generar(_=Depends(require_auth)):
        if estado["generando"]:
            raise HTTPException(status_code=409,
                                detail="Ya se está sintetizando la música")
        estado["generando"] = True
        try:
            temas = await runner.musica()
        except (RunnerError, asyncio.TimeoutError) as e:
            raise HTTPException(status_code=502,
                                detail=f"La síntesis falló: {e}")
        finally:
            estado["generando"] = False
        return {"temas": temas, "listos": _listos()}

    @router.get("/{nombre}")
    async def oir(nombre: str, _=Depends(require_auth)):
        # El nombre va contra el conjunto CERRADO del catalogo: nada que
        # venga de la URL toca el sistema de archivos sin pasar por aqui.
        if nombre not in audio_promo.TEMAS:
            raise HTTPException(status_code=404, detail="Ese tema no existe")
        path = (cfg.musica_dir / f"{nombre}.wav").resolve()
        if not path.is_file() or cfg.musica_dir.resolve() not in path.parents:
            raise HTTPException(
                status_code=404,
                detail="El banco de música todavía no está sintetizado")
        return FileResponse(path, media_type="audio/wav",
                            filename=f"{nombre}.wav")

    return router

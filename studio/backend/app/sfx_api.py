"""Banco de sonidos audible.

Los 18 efectos de `sfx.py` se elegian a ciegas: un desplegable con dieciocho
nombres —«sting», «subrayado», «nebulosa_cierre»— y ninguna forma de oirlos
sin montar una mezcla entera y mirar el resultado. Se elegia por el nombre y
se corregia por ensayo y error.

Aqui se sintetizan una vez (`sfx.py paleta` dentro del contenedor, porque el
backend no tiene numpy) como wavs sueltos en `exports/sfx/`, y la interfaz los
reproduce al pasar por encima. La sintesis es determinista: el mismo efecto
suena igual siempre, asi que basta generarlos una vez y no caducan.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from . import audio_promo
from .auth import require_auth
from .runner_client import RunnerError


def make_router(cfg, runner) -> APIRouter:
    router = APIRouter(prefix="/api/sfx", tags=["sfx"])
    # Un solo turno: sintetizar los 18 tarda ~1 min y no tiene sentido
    # lanzarlo dos veces a la vez.
    estado = {"generando": False}

    def _listos() -> list[str]:
        """Los que estan Y siguen en la paleta.

        El directorio sobrevive a los cambios de `PALETA`: una corrida vieja
        deja wavs de efectos que ya no existen (`pad_intro`, `pad_cierre`
        siguen ahi de la paleta anterior). Enumerarlos sin filtrar ofreceria
        en la interfaz sonidos que la mezcla ya no sabe sintetizar.
        """
        if not cfg.sfx_dir.is_dir():
            return []
        vivos = set(audio_promo.SONIDOS)
        return sorted(p.stem for p in cfg.sfx_dir.glob("*.wav")
                      if p.stem in vivos)

    @router.get("")
    async def listar(_=Depends(require_auth)):
        listos = _listos()
        return {
            "sonidos": list(audio_promo.SONIDOS),
            "listos": listos,
            "completo": set(listos) >= set(audio_promo.SONIDOS),
            "generando": estado["generando"],
        }

    @router.post("")
    async def generar(_=Depends(require_auth)):
        if estado["generando"]:
            raise HTTPException(status_code=409,
                                detail="Ya se está sintetizando el banco")
        estado["generando"] = True
        try:
            sonidos = await runner.paleta()
        except (RunnerError, asyncio.TimeoutError) as e:
            raise HTTPException(status_code=502,
                                detail=f"La síntesis falló: {e}")
        finally:
            estado["generando"] = False
        return {"sonidos": sonidos, "listos": _listos()}

    @router.get("/{nombre}")
    async def oir(nombre: str, _=Depends(require_auth)):
        # El nombre va contra el conjunto CERRADO de la paleta: nada que
        # venga de la URL toca el sistema de archivos sin pasar por aqui.
        if nombre not in audio_promo.SONIDOS:
            raise HTTPException(status_code=404, detail="Ese sonido no existe")
        path = (cfg.sfx_dir / f"{nombre}.wav").resolve()
        if not path.is_file() or cfg.sfx_dir.resolve() not in path.parents:
            raise HTTPException(
                status_code=404,
                detail="El banco todavía no está sintetizado")
        return FileResponse(path, media_type="audio/wav",
                            filename=f"{nombre}.wav")

    return router

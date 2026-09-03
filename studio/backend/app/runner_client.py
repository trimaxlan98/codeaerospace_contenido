"""Cliente del socket Unix del manim-runner (unico puente hacia Docker)."""

import asyncio
import json
from typing import AsyncIterator


class RunnerError(Exception):
    pass


class RunnerClient:
    def __init__(self, socket_path: str) -> None:
        self.socket_path = socket_path

    async def _connect(self) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        try:
            return await asyncio.open_unix_connection(self.socket_path)
        except (FileNotFoundError, ConnectionRefusedError, PermissionError) as e:
            raise RunnerError(f"runner no disponible: {e}") from e

    async def _request_one(self, payload: dict, timeout: float = 30.0) -> dict:
        reader, writer = await self._connect()
        try:
            writer.write((json.dumps(payload) + "\n").encode())
            await writer.drain()
            raw = await asyncio.wait_for(reader.readline(), timeout=timeout)
            if not raw:
                raise RunnerError("runner cerro la conexion sin responder")
            return json.loads(raw)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def ping(self) -> bool:
        try:
            resp = await self._request_one({"cmd": "ping"}, timeout=5)
            return resp.get("type") == "pong"
        except (RunnerError, asyncio.TimeoutError, json.JSONDecodeError):
            return False

    async def stats(self) -> list[dict]:
        resp = await self._request_one({"cmd": "stats"}, timeout=30)
        if resp.get("type") != "stats":
            raise RunnerError(resp.get("error", "respuesta inesperada del runner"))
        return resp.get("containers", [])

    async def cancel(self, job_id: str) -> None:
        await self._request_one({"cmd": "cancel", "job_id": job_id}, timeout=30)

    async def thumbnail(self, job_id: str) -> dict:
        """Miniatura + resolucion medida del video del job.

        Devuelve {"thumb": ruta relativa, "resolution": "1080x1920"}. La
        resolucion puede faltar (ffprobe fallo) sin que la miniatura falle.
        """
        resp = await self._request_one({"cmd": "thumbnail", "job_id": job_id}, timeout=120)
        if resp.get("type") != "ok":
            raise RunnerError(resp.get("error", "thumbnail fallo"))
        return {"thumb": resp.get("thumb", ""),
                "resolution": resp.get("resolution", "")}

    async def postproceso(self, job_id: str, con_voz: bool) -> str:
        """Mezcla el audio del promo sobre el video del job (sfx.py en el
        contenedor). Devuelve la ruta relativa del mp4 sonorizado."""
        resp = await self._request_one(
            {"cmd": "postproceso", "job_id": job_id, "con_voz": con_voz},
            timeout=360)
        if resp.get("type") != "ok":
            raise RunnerError(resp.get("error", "la mezcla de audio fallo"))
        return resp.get("audio", "")

    async def cortar_presentacion(self, project_id: str) -> dict:
        """Parte los renders de una presentacion en sus fragmentos
        (cortar_presentacion.py en el contenedor). Devuelve el informe: un
        fragmento por slide.

        Timeout generoso porque cada fragmento se recodifica y ademas se
        genera su GIF, y el contenedor esta capado a 1.5 vCPU.
        """
        resp = await self._request_one(
            {"cmd": "presentacion", "project_id": project_id}, timeout=3600)
        if resp.get("type") != "ok":
            raise RunnerError(
                resp.get("error", "el corte de la presentacion fallo"))
        return resp.get("informe", {})

    async def ensamblar(self, project_id: str, modo: str = "montar") -> dict:
        """Monta la pelicula del proyecto (ensamblar.py en el contenedor).

        El timeout es largo a proposito: con transiciones se recodifica la
        pelicula entera y en el VPS (1.5 vCPU) un curso de media hora tarda
        decenas de minutos. Sin transiciones son segundos, porque el video se
        copia. El plan ya esta escrito en exports/peliculas/<pid>/plan.json.

        `modo="verificar"` mide la pelicula ya montada contra ese mismo plan
        en vez de volver a montarla.
        """
        resp = await self._request_one(
            {"cmd": "ensamblar", "project_id": project_id, "modo": modo},
            timeout=14700 if modo == "montar" else 360)
        if resp.get("type") != "ok":
            raise RunnerError(resp.get("error", "el montaje fallo"))
        return resp.get("informe") or {}

    async def paleta(self) -> list[str]:
        """Sintetiza el banco de sonidos (wavs sueltos) para poder oirlo."""
        resp = await self._request_one({"cmd": "paleta"}, timeout=660)
        if resp.get("type") != "ok":
            raise RunnerError(resp.get("error", "la sintesis del banco fallo"))
        return resp.get("sonidos") or []

    async def musica(self) -> list[str]:
        """Sintetiza el banco de musica (una vista previa por tema)."""
        resp = await self._request_one({"cmd": "musica"}, timeout=960)
        if resp.get("type") != "ok":
            raise RunnerError(resp.get("error", "la sintesis de musica fallo"))
        return resp.get("temas") or []

    async def verificar(self, job_id: str, frames: int = 6,
                        dur_min: float = 8.0, dur_max: float = 15.0) -> dict:
        """Informe medido del promo (bucle, duracion, audio, frames)."""
        resp = await self._request_one(
            {"cmd": "verificar", "job_id": job_id, "frames": frames,
             "dur_min": dur_min, "dur_max": dur_max}, timeout=360)
        if resp.get("type") != "ok":
            raise RunnerError(resp.get("error", "la verificacion fallo"))
        return resp.get("informe") or {}

    async def render(
        self, job_id: str, scene: str, quality: str, timeout: int,
        formato: str = "horizontal", corto: int = 1080, largo: int = 1920,
        fps: int = 60, fondo: str = "marca",
    ) -> AsyncIterator[dict]:
        """Genera eventos {"type": "log"|"done"|"error", ...} del render.

        Cerrar el generador (p.ej. por cancelacion del task) cierra la
        conexion, y el runner mata el contenedor de render al detectarlo.
        """
        reader, writer = await self._connect()
        try:
            writer.write((json.dumps({
                "cmd": "render", "job_id": job_id, "scene": scene,
                "quality": quality, "timeout": timeout,
                "formato": formato, "corto": corto, "largo": largo, "fps": fps,
                "fondo": fondo,
            }) + "\n").encode())
            await writer.drain()
            # margen sobre el timeout del runner para recibir el "done"
            deadline = timeout + 60
            while True:
                raw = await asyncio.wait_for(reader.readline(), timeout=deadline)
                if not raw:
                    yield {"type": "error", "error": "conexion con el runner perdida"}
                    return
                event = json.loads(raw)
                yield event
                if event.get("type") in ("done", "error"):
                    return
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

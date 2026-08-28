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
        fps: int = 60,
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

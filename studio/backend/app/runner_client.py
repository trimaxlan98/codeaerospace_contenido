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

    async def render(
        self, job_id: str, scene: str, quality: str, timeout: int
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

#!/usr/bin/env python3
"""ManimStudio runner: superficie minima de control sobre Docker.

Este demonio es el UNICO proceso de ManimStudio con acceso al socket de
Docker. El backend web (usuario sin privilegios, sin grupo docker) le habla
por un socket Unix con permisos 0660 root:manimstudio.

Superficie deliberadamente minima — no es un proxy generico de Docker:
  - render : `docker compose run` del servicio `manim-render` de ESTE
             compose file, con script/escena/calidad validados por regex.
  - cancel : `docker rm -f` de un contenedor cuyo nombre coincide con el
             prefijo fijo de render de ManimStudio (no puede tocar otros).
  - stats  : lectura agregada (`docker ps` + `docker stats --no-stream`),
             solo nombre/estado/%cpu/%mem. Nunca env vars, logs ni exec.
  - ping   : healthcheck.

Protocolo: una linea JSON de peticion; respuestas como lineas JSON. Para
`render` se transmiten eventos {"type":"log"|"done"} por la misma conexion.
"""

import asyncio
import grp
import json
import os
import re
import signal
import sys

COMPOSE_FILE = "/var/www/codeaerospace_contenido/docker-compose.yml"
PROJECT_DIR = "/var/www/codeaerospace_contenido"
RENDER_JOBS_DIR = "render_jobs"  # relativo al workspace montado
SOCKET_PATH = "/run/manimstudio/runner.sock"
SOCKET_GROUP = "manimstudio"
CONTAINER_PREFIX = "manimstudio-render-"

RE_JOB_ID = re.compile(r"^[a-f0-9]{8,32}$")
RE_SCENE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")
QUALITIES = {"ql", "qm", "qh"}
TIMEOUT_MIN, TIMEOUT_MAX = 30, 1800
MAX_LOG_LINE = 4000  # caracteres por linea reenviada
STATS_CACHE_TTL = 4.0  # docker stats es caro; cachear para no castigar 2 vCPU

_stats_cache = {"ts": 0.0, "data": None}
_stats_lock = asyncio.Lock()


def log(msg: str) -> None:
    print(msg, flush=True)


async def run_cmd(*argv: str, timeout: float = 30.0) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *argv, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return 124, "", "timeout"
    return proc.returncode or 0, out.decode(errors="replace"), err.decode(errors="replace")


async def send(writer: asyncio.StreamWriter, obj: dict) -> None:
    writer.write((json.dumps(obj) + "\n").encode())
    await writer.drain()


# ── render ────────────────────────────────────────────────────────────────────

async def handle_render(req: dict, writer: asyncio.StreamWriter) -> None:
    job_id = str(req.get("job_id", ""))
    scene = str(req.get("scene", ""))
    quality = str(req.get("quality", ""))
    timeout = req.get("timeout", 600)

    if not RE_JOB_ID.match(job_id):
        await send(writer, {"type": "error", "error": "job_id invalido"})
        return
    if not RE_SCENE.match(scene):
        await send(writer, {"type": "error", "error": "nombre de escena invalido"})
        return
    if quality not in QUALITIES:
        await send(writer, {"type": "error", "error": "calidad invalida"})
        return
    if not isinstance(timeout, int) or not (TIMEOUT_MIN <= timeout <= TIMEOUT_MAX):
        await send(writer, {"type": "error", "error": "timeout fuera de rango"})
        return

    # El script SIEMPRE se lee de la ruta canonica del job: el backend lo
    # escribio ahi. El runner no acepta rutas arbitrarias.
    script_rel = f"{RENDER_JOBS_DIR}/{job_id}/scene.py"
    script_abs = os.path.join(PROJECT_DIR, script_rel)
    if not os.path.isfile(script_abs):
        await send(writer, {"type": "error", "error": "script del job no encontrado"})
        return

    container = CONTAINER_PREFIX + job_id
    argv = [
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", "--name", container,
        "manim-render",
        "manim", "render", f"-{quality}", "--disable_caching",
        "--media_dir", f"/workspace/{RENDER_JOBS_DIR}/{job_id}/media",
        f"/workspace/{script_rel}", scene,
    ]
    log(f"[render] job={job_id} scene={scene} q={quality} timeout={timeout}s")

    proc = await asyncio.create_subprocess_exec(
        *argv,
        cwd=PROJECT_DIR,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    async def stream_logs() -> None:
        assert proc.stdout is not None
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            text = line.decode(errors="replace").rstrip("\n")[:MAX_LOG_LINE]
            await send(writer, {"type": "log", "line": text})

    timed_out = False
    try:
        await asyncio.wait_for(stream_logs(), timeout=timeout)
        exit_code = await proc.wait()
    except asyncio.TimeoutError:
        timed_out = True
        await force_remove(container)
        proc.kill()
        await proc.wait()
        exit_code = 124
    except (ConnectionResetError, BrokenPipeError):
        # El backend cerro la conexion (p.ej. cancelacion): matar el render.
        await force_remove(container)
        proc.kill()
        await proc.wait()
        return

    await send(writer, {"type": "done", "exit_code": exit_code, "timed_out": timed_out})
    log(f"[render] job={job_id} exit={exit_code} timed_out={timed_out}")


async def force_remove(container: str) -> None:
    await run_cmd("docker", "rm", "-f", container)


async def handle_cancel(req: dict, writer: asyncio.StreamWriter) -> None:
    job_id = str(req.get("job_id", ""))
    if not RE_JOB_ID.match(job_id):
        await send(writer, {"type": "error", "error": "job_id invalido"})
        return
    # Solo contenedores con el prefijo propio: imposible tocar produccion.
    await force_remove(CONTAINER_PREFIX + job_id)
    log(f"[cancel] job={job_id}")
    await send(writer, {"type": "ok"})


# ── stats ─────────────────────────────────────────────────────────────────────

async def collect_stats() -> dict:
    ps_code, ps_out, _ = await run_cmd(
        "docker", "ps", "-a", "--format", "{{json .}}", timeout=15
    )
    st_code, st_out, _ = await run_cmd(
        "docker", "stats", "--no-stream", "--format", "{{json .}}", timeout=25
    )
    containers: dict[str, dict] = {}
    if ps_code == 0:
        for line in ps_out.splitlines():
            try:
                c = json.loads(line)
            except json.JSONDecodeError:
                continue
            # Solo campos agregados e inocuos. Nada de Command/Mounts/Env.
            containers[c.get("Names", "?")] = {
                "name": c.get("Names", "?"),
                "state": c.get("State", "unknown"),
                "status": c.get("Status", ""),
                "cpu_pct": 0.0,
                "mem_pct": 0.0,
                "mem_usage": "",
            }
    if st_code == 0:
        for line in st_out.splitlines():
            try:
                s = json.loads(line)
            except json.JSONDecodeError:
                continue
            name = s.get("Name", "?")
            entry = containers.setdefault(name, {
                "name": name, "state": "running", "status": "",
                "cpu_pct": 0.0, "mem_pct": 0.0, "mem_usage": "",
            })
            try:
                entry["cpu_pct"] = float(s.get("CPUPerc", "0%").strip("%"))
                entry["mem_pct"] = float(s.get("MemPerc", "0%").strip("%"))
            except ValueError:
                pass
            entry["mem_usage"] = s.get("MemUsage", "")
    return {"type": "stats", "containers": sorted(containers.values(), key=lambda c: c["name"])}


async def handle_stats(writer: asyncio.StreamWriter) -> None:
    async with _stats_lock:
        now = asyncio.get_event_loop().time()
        if _stats_cache["data"] is None or now - _stats_cache["ts"] > STATS_CACHE_TTL:
            _stats_cache["data"] = await collect_stats()
            _stats_cache["ts"] = now
    await send(writer, _stats_cache["data"])


# ── servidor ──────────────────────────────────────────────────────────────────

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        raw = await asyncio.wait_for(reader.readline(), timeout=10)
        if not raw:
            return
        try:
            req = json.loads(raw)
        except json.JSONDecodeError:
            await send(writer, {"type": "error", "error": "json invalido"})
            return
        cmd = req.get("cmd")
        if cmd == "render":
            await handle_render(req, writer)
        elif cmd == "cancel":
            await handle_cancel(req, writer)
        elif cmd == "stats":
            await handle_stats(writer)
        elif cmd == "ping":
            await send(writer, {"type": "pong"})
        else:
            await send(writer, {"type": "error", "error": "comando desconocido"})
    except (asyncio.TimeoutError, ConnectionResetError, BrokenPipeError):
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


async def main() -> None:
    os.makedirs(os.path.dirname(SOCKET_PATH), mode=0o750, exist_ok=True)
    if os.path.exists(SOCKET_PATH):
        os.unlink(SOCKET_PATH)
    server = await asyncio.start_unix_server(handle_client, path=SOCKET_PATH)
    gid = grp.getgrnam(SOCKET_GROUP).gr_gid
    # El grupo debe poder atravesar el directorio ademas de usar el socket.
    os.chown(os.path.dirname(SOCKET_PATH), 0, gid)
    os.chmod(os.path.dirname(SOCKET_PATH), 0o750)
    os.chown(SOCKET_PATH, 0, gid)
    os.chmod(SOCKET_PATH, 0o660)
    log(f"manim-runner escuchando en {SOCKET_PATH} (grupo {SOCKET_GROUP})")

    loop = asyncio.get_event_loop()
    stop = loop.create_future()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: stop.done() or stop.set_result(None))
    async with server:
        await stop


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)

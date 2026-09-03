#!/usr/bin/env python3
"""ManimStudio runner: superficie minima de control sobre Docker.

Este demonio es el UNICO proceso de ManimStudio con acceso al socket de
Docker. El backend web (usuario sin privilegios, sin grupo docker) le habla
por un socket Unix con permisos 0660 root:manimstudio.

Superficie deliberadamente minima — no es un proxy generico de Docker:
  - render : `docker compose run` del servicio `manim-render` de ESTE
             compose file, con script/escena/calidad validados por regex.
             El lienzo (formato/lado corto/fps) entra como variables
             PROMO_* validadas contra un conjunto y rangos cerrados; las
             lee la escena, no el runner.
  - postproceso : `studio/tools/sfx.py promo` en el MISMO contenedor, sobre
             el directorio del job (manifiesto y voz los deja el backend
             ahi). Ruta del script fija; solo recibe el job_id.
  - verificar : `studio/tools/promo_verifica.py` en el MISMO contenedor:
             mide costura del bucle, duracion, audio y frames del archivo
             que la app sirve, y devuelve el informe JSON.
  - frames : `studio/tools/hoja_contactos.py tira` en el MISMO contenedor:
             la hoja de contactos del render (N fotogramas equiespaciados y
             el ultimo real). Solo llegan el job_id y cuantos.
  - fotograma : el mismo script en modo `figura`: un PNG a la resolucion
             pedida desde el mp4 del job. El nombre del archivo lo DERIVA el
             runner de (t, ancho); del exterior no llega ninguna ruta.
  - ejecutar : Python de validacion (las `sonda_*.py`, o un script escrito en
             el Laboratorio) en el MISMO contenedor: sin red, repo read-only
             y como unico directorio escribible render_jobs/lab/<lab_id>.
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
import pwd
import re
import signal
import sys

# Los defaults son los del VPS (systemd no pasa ninguna MS_* al runner, asi que
# produccion los usa tal cual). Las variables existen para poder levantar el
# runner en un clon local de desarrollo, donde no hay /var/www ni usuario
# manimstudio.
PROJECT_DIR = os.environ.get("MS_WORKSPACE", "/var/www/codeaerospace_contenido")
COMPOSE_FILE = os.environ.get("MS_COMPOSE_FILE", os.path.join(PROJECT_DIR, "docker-compose.yml"))
RENDER_JOBS_DIR = "render_jobs"  # relativo al workspace montado
SOCKET_PATH = os.environ.get("MS_RUNNER_SOCKET", "/run/manimstudio/runner.sock")
SOCKET_GROUP = os.environ.get("MS_RUNNER_SOCKET_GROUP", "manimstudio")
CONTAINER_PREFIX = "manimstudio-render-"
# Mezcla de audio de un promo: el unico script del repo que el runner
# ejecuta ademas de manim, en ruta fija (no llega del exterior).
SFX_SCRIPT = "studio/tools/sfx.py"
AUDIO_TIMEOUT = 300
# Verificacion del promo (costura del bucle, duracion, audio y frames), en
# el mismo contenedor y con la misma regla: ruta fija, solo el job_id.
VERIFICA_SCRIPT = "studio/tools/promo_verifica.py"
VERIFICA_TIMEOUT = 300
FRAMES_MAX = 12
# Montaje de la pelicula de un curso: mismo patron que los dos de arriba (ruta
# fija del script, solo llega el project_id). El directorio de salida se deriva
# aqui, nunca viene del exterior; es la MISMA ruta que cfg.peliculas_dir del
# backend.
ENSAMBLAR_SCRIPT = "studio/tools/ensamblar.py"
PELICULAS_DIR = "exports/peliculas"
# Banco de sonidos audible: `sfx.py paleta` sintetiza los 18 efectos como wavs
# sueltos para que se puedan OIR antes de elegirlos. Sin argumentos del
# exterior: destino fijo.
SFX_DIR = "exports/sfx"
SFX_TIMEOUT = 600
# Banco de MUSICA: `musica.py banco` deja una vista previa de 12 s de cada
# tema para poder elegirlo oyendo. Misma regla que la paleta: ruta fija del
# script y destino fijo, cero argumentos del exterior. Misma ruta que
# cfg.musica_dir del backend: si una cambia, la otra tambien.
MUSICA_SCRIPT = "studio/tools/musica.py"
MUSICA_DIR = "exports/musica"
# Ocho temas de 12 s con Karplus-Strong y tres FFT por tema: ~1 min medido en
# el contenedor. El tope generoso cubre el VPS a 1.5 vCPU.
MUSICA_TIMEOUT = 900
# 4 h + margen: con transiciones se recodifica la pelicula entera y el
# contenedor esta capado a 1.5 vCPU. Sin transiciones son segundos.
ENSAMBLAR_TIMEOUT = 14400
# Medir la pelicula ya no es solo leer su duracion: desde R3c saca dos
# fotogramas por union y compara los picos pieza a pieza. Medido en el
# contenedor sobre cuatro piezas de 480p15, 1.3 s de trabajo; a 1080p60 y
# treinta piezas la extrapolacion se va a varios minutos, y el VPS corre a
# 1.5 vCPU. Los 300 s de VERIFICA_TIMEOUT (que es el del promo, una pieza)
# se quedaban cortos.
ENSAMBLAR_VERIFICA_TIMEOUT = 1800
# Presentaciones: `cortar_presentacion.py` parte el render de cada clip en
# sus fragmentos (uno por clic del ponente) y saca posters y GIF. Trabaja
# dentro del contenedor porque el backend no tiene ffmpeg; el .pptx lo arma
# despues el backend, que si tiene python-pptx. Misma ruta que
# cfg.presentaciones_dir: si una cambia, la otra tambien.
CORTAR_SCRIPT = "studio/tools/cortar_presentacion.py"
PRESENTACIONES_DIR = "exports/presentaciones"
# Cortar es recodificar fragmentos cortos y generar GIF: minutos, no horas.
CORTAR_TIMEOUT = 3600

# Grabaciones propias de narracion (PUT .../narracion/{cid}/audio): el backend
# deja el archivo subido en guiones/<slug>/ y pide convertirlo a WAV mono
# 24 kHz con el ffmpeg del contenedor. Solo entran un slug y dos nombres de
# archivo con forma cerrada; el directorio se monta rw solo para esa llamada.
GUIONES_DIR = "guiones"
NORMALIZAR_TIMEOUT = 240
RE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
RE_SUBIDA = re.compile(r"^[0-9]{2}-[a-z0-9-]{1,60}\.subida(?:\.[a-z0-9]{2,5})?$")

RE_JOB_ID = re.compile(r"^[a-f0-9]{8,32}$")
RE_SCENE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")
QUALITIES = {"ql", "qm", "qh"}
# El lienzo (formato/lado corto/fps) viaja al contenedor por entorno, y la
# escena lo aplica con promo.formato(). Se valida contra un conjunto y unos
# rangos cerrados, igual que la calidad: son valores que entran en la linea
# de comandos de docker, no texto libre.
FORMATOS = {"horizontal", "vertical", "cuadrado", "clasico"}
# El fondo solo lo lee `presentacion.lienzo()`; un curso o un promo lo
# ignoran. Se
# valida aqui igual que el formato porque acaba en la linea de comandos de
# docker: nombre corto o color "#rrggbb", nunca texto libre.
RE_FONDO = re.compile(r"^(?:[a-z]{1,16}|#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}))\Z")
CORTO_MIN, CORTO_MAX = 240, 2160
LARGO_MAX = 3840
FPS_MIN, FPS_MAX = 5, 120
TIMEOUT_MIN, TIMEOUT_MAX = 30, 1800
MAX_LOG_LINE = 4000  # caracteres por linea reenviada
STATS_CACHE_TTL = 4.0  # docker stats es caro; cachear para no castigar 2 vCPU

_stats_cache = {"ts": 0.0, "data": None}
_stats_lock = asyncio.Lock()

# Los contenedores de render/miniatura corren con el uid:gid de manimstudio:
# asi los archivos que crean en render_jobs/ pueden ser limpiados/borrados por
# el backend (que corre como ese usuario). HOME=/tmp para las caches de manim.
# En un clon de desarrollo ese usuario no existe: se cae al uid:gid actual, que
# es justamente quien corre el backend ahi.
try:
    _ms = pwd.getpwnam(os.environ.get("MS_RUNNER_USER", "manimstudio"))
    _run_uid, _run_gid = _ms.pw_uid, _ms.pw_gid
except KeyError:
    _run_uid, _run_gid = os.getuid(), os.getgid()
RUN_AS_ARGS = ("--user", f"{_run_uid}:{_run_gid}", "-e", "HOME=/tmp")


def _asegurar_dir_del_runner(path: str) -> None:
    """Crea `path` (si falta) con el uid:gid con que corren los contenedores.
    El runner es root: un `makedirs` a secas deja el directorio root:root y
    el contenedor (manimstudio) no puede escribir en el — paso en produccion
    con exports/musica el 2026-09-03."""
    creado = not os.path.isdir(path)
    os.makedirs(path, exist_ok=True)
    if creado:
        try:
            os.chown(path, _run_uid, _run_gid)
        except OSError:
            pass


def montaje_render_jobs() -> str:
    """El `-v` que le da al contenedor los videos ya renderizados, read-only.

    El repo montado read-only NO basta: en una instalacion donde `render_jobs`
    es un enlace simbolico a otro disco (ver studio/docs/ARTEFACTOS-LOCALES.md)
    ese enlace, dentro del contenedor, apunta a un destino que no esta montado
    y no se puede leer nada. Por eso se monta el destino REAL (realpath).

    De solo lectura: montar la pelicula y cortar una presentacion LEEN los
    renders,
    no los tocan.
    """
    jobs_abs = os.path.join(PROJECT_DIR, RENDER_JOBS_DIR)
    return f"{os.path.realpath(jobs_abs)}:/workspace/{RENDER_JOBS_DIR}:ro"


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
    formato = str(req.get("formato", "horizontal"))
    fondo = str(req.get("fondo") or "marca")
    corto = req.get("corto", 1080)
    largo = req.get("largo", 1920)
    fps = req.get("fps", 60)

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
    if formato not in FORMATOS:
        await send(writer, {"type": "error", "error": "formato invalido"})
        return
    if not RE_FONDO.match(fondo):
        await send(writer, {"type": "error", "error": "fondo invalido"})
        return
    if not isinstance(corto, int) or not (CORTO_MIN <= corto <= CORTO_MAX):
        await send(writer, {"type": "error", "error": "lado corto fuera de rango"})
        return
    if not isinstance(largo, int) or not (corto <= largo <= LARGO_MAX):
        await send(writer, {"type": "error", "error": "lado largo fuera de rango"})
        return
    if not isinstance(fps, int) or not (FPS_MIN <= fps <= FPS_MAX):
        await send(writer, {"type": "error", "error": "fps fuera de rango"})
        return

    # El script SIEMPRE se lee de la ruta canonica del job: el backend lo
    # escribio ahi. El runner no acepta rutas arbitrarias.
    script_rel = f"{RENDER_JOBS_DIR}/{job_id}/scene.py"
    script_abs = os.path.join(PROJECT_DIR, script_rel)
    if not os.path.isfile(script_abs):
        await send(writer, {"type": "error", "error": "script del job no encontrado"})
        return

    container = CONTAINER_PREFIX + job_id
    # El repo se monta read-only (docker-compose.yml); solo el directorio de
    # ESTE job se monta rw, por invocacion, para que Manim pueda escribir
    # media/ sin exponer el resto del repo en escritura.
    job_mount = f"{os.path.join(PROJECT_DIR, RENDER_JOBS_DIR, job_id)}:/workspace/{RENDER_JOBS_DIR}/{job_id}:rw"
    # El flag -q sigue mandando en un render 16:9 normal. Las variables
    # PROMO_* solo las lee una escena que llame a promo.formato(): un curso
    # las ignora y renderiza exactamente igual que antes.
    # PROMO_* las lee promo.formato(); PRESENTACION_* las lee
    # presentacion.lienzo(), que
    # ademas acepta las PROMO_* como respaldo. Se pasan las dos familias: una
    # escena de curso ignora ambas y renderiza igual que siempre. Lo unico
    # que NO tiene equivalente en promo es el fondo.
    lienzo = ("-e", f"PROMO_FORMATO={formato}", "-e", f"PROMO_CALIDAD={quality}",
              "-e", f"PROMO_CORTO={corto}", "-e", f"PROMO_LARGO={largo}",
              "-e", f"PROMO_FPS={fps}",
              "-e", f"PRESENTACION_FORMATO={formato}",
              "-e", f"PRESENTACION_FONDO={fondo}")
    argv = [
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS, *lienzo,
        "-v", job_mount,
        "--name", container,
        "manim-render",
        "manim", "render", f"-{quality}", "--disable_caching",
        "--media_dir", f"/workspace/{RENDER_JOBS_DIR}/{job_id}/media",
        f"/workspace/{script_rel}", scene,
    ]
    log(f"[render] job={job_id} scene={scene} q={quality} fmt={formato}"
        f" fondo={fondo} {corto}x{largo} fps={fps} timeout={timeout}s")

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


def video_del_job(job_id: str) -> str | None:
    """Ruta (relativa al repo) del mp4 mas reciente del job, o None.

    Siempre dentro de la ruta canonica del job: el runner no acepta rutas
    del exterior. Ignora los parciales de manim.
    """
    media_abs = os.path.join(PROJECT_DIR, RENDER_JOBS_DIR, job_id, "media", "videos")
    video_rel = None
    newest = -1.0
    for root, _dirs, files in os.walk(media_abs):
        if "partial_movie_files" in root:
            continue
        for f in files:
            if f.endswith(".mp4"):
                p = os.path.join(root, f)
                mtime = os.path.getmtime(p)
                if mtime > newest:
                    newest = mtime
                    video_rel = os.path.relpath(p, PROJECT_DIR)
    return video_rel


async def handle_thumbnail(req: dict, writer: asyncio.StreamWriter) -> None:
    """Extrae 1 frame del video final del job como thumb.jpg.

    Corre DENTRO del contenedor manim-render (el backend no tiene ffmpeg).
    Solo recibe job_id: el video se localiza en la ruta canonica del job,
    nunca se aceptan rutas arbitrarias.
    """
    job_id = str(req.get("job_id", ""))
    if not RE_JOB_ID.match(job_id):
        await send(writer, {"type": "error", "error": "job_id invalido"})
        return

    video_rel = video_del_job(job_id)
    if video_rel is None:
        await send(writer, {"type": "error", "error": "video del job no encontrado"})
        return

    thumb_rel = f"{RENDER_JOBS_DIR}/{job_id}/thumb.jpg"
    container = f"{CONTAINER_PREFIX}{job_id}-thumb"
    job_mount = f"{os.path.join(PROJECT_DIR, RENDER_JOBS_DIR, job_id)}:/workspace/{RENDER_JOBS_DIR}/{job_id}:rw"
    code, _out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", job_mount,
        "--name", container,
        "--entrypoint", "ffmpeg", "manim-render",
        "-y", "-i", f"/workspace/{video_rel}",
        "-frames:v", "1", "-vf", "scale=320:-1",
        f"/workspace/{thumb_rel}",
        timeout=90,
    )
    if code != 0:
        await force_remove(container)
        log(f"[thumbnail] job={job_id} fallo (code={code})")
        await send(writer, {"type": "error",
                            "error": f"ffmpeg salio con codigo {code}: {err[-300:]}"})
        return
    resolution = await _resolucion(video_rel, job_id, job_mount)
    log(f"[thumbnail] job={job_id} ok res={resolution or '?'}")
    await send(writer, {"type": "ok", "thumb": thumb_rel,
                        "resolution": resolution})


async def _resolucion(video_rel: str, job_id: str, job_mount: str) -> str:
    """WxH del video, medido con ffprobe dentro del contenedor.

    Devuelve "" si falla: la resolucion es informativa y no puede tumbar un
    render que ya termino bien.
    """
    container = f"{CONTAINER_PREFIX}{job_id}-probe"
    code, out, _err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", job_mount,
        "--name", container,
        "--entrypoint", "ffprobe", "manim-render",
        "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0", f"/workspace/{video_rel}",
        timeout=90,
    )
    if code != 0:
        await force_remove(container)
        return ""
    valor = out.strip().splitlines()[-1].strip() if out.strip() else ""
    return valor if re.fullmatch(r"\d{2,5}x\d{2,5}", valor) else ""


async def force_remove(container: str) -> None:
    await run_cmd("docker", "rm", "-f", container)


async def handle_postproceso(req: dict, writer: asyncio.StreamWriter) -> None:
    """Mezcla la cama de sonido (y la voz, si la hay) sobre el video del job.

    Corre `studio/tools/sfx.py promo` DENTRO del contenedor manim-render: el
    backend no tiene numpy ni ffmpeg, y el script vive en el repo montado
    read-only. Igual que el thumbnail, solo recibe `job_id`: el manifiesto
    (`promo.json`) y la voz (`voz.wav`) los dejo el backend en el directorio
    del job, y la salida se escribe ahi mismo. Ninguna ruta viene de fuera.
    """
    job_id = str(req.get("job_id", ""))
    con_voz = bool(req.get("con_voz"))
    if not RE_JOB_ID.match(job_id):
        await send(writer, {"type": "error", "error": "job_id invalido"})
        return

    video_rel = video_del_job(job_id)
    if video_rel is None:
        await send(writer, {"type": "error", "error": "video del job no encontrado"})
        return

    job_rel = f"{RENDER_JOBS_DIR}/{job_id}"
    job_abs = os.path.join(PROJECT_DIR, job_rel)
    if not os.path.isfile(os.path.join(job_abs, "promo.json")):
        await send(writer, {"type": "error", "error": "el job no tiene promo.json"})
        return
    if con_voz and not os.path.isfile(os.path.join(job_abs, "voz.wav")):
        await send(writer, {"type": "error", "error": "el job no tiene voz.wav"})
        return

    salida_rel = f"{job_rel}/promo_audio.mp4"
    container = f"{CONTAINER_PREFIX}{job_id}-audio"
    job_mount = f"{job_abs}:/workspace/{job_rel}:rw"
    argv = [
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", job_mount,
        "--name", container,
        "--entrypoint", "python3", "manim-render",
        f"/workspace/{SFX_SCRIPT}", "promo",
        f"/workspace/{job_rel}", f"/workspace/{video_rel}",
        f"/workspace/{salida_rel}",
    ]
    if con_voz:
        argv.append(f"/workspace/{job_rel}/voz.wav")

    code, out, err = await run_cmd(*argv, timeout=AUDIO_TIMEOUT)
    if code != 0 or not os.path.isfile(os.path.join(PROJECT_DIR, salida_rel)):
        await force_remove(container)
        log(f"[audio] job={job_id} fallo (code={code})")
        await send(writer, {"type": "error",
                            "error": f"sfx.py salio con codigo {code}:"
                                     f" {(err or out)[-300:]}"})
        return
    log(f"[audio] job={job_id} ok voz={con_voz}")
    await send(writer, {"type": "ok", "audio": salida_rel,
                        "detalle": out.strip()[-300:]})


async def handle_verificar(req: dict, writer: asyncio.StreamWriter) -> None:
    """Mide el promo sobre el archivo que la app sirve y devuelve el informe.

    Prefiere el mp4 CON sonido si ya se mezclo (es el que ve el publico) y
    cae al mudo si no existe. Corre `promo_verifica.py` en el contenedor —
    el backend no tiene ffmpeg — y deja los PNG en <job>/verificacion/.
    """
    job_id = str(req.get("job_id", ""))
    frames = req.get("frames", 6)
    dur_min = req.get("dur_min", 8.0)
    dur_max = req.get("dur_max", 15.0)
    if not RE_JOB_ID.match(job_id):
        await send(writer, {"type": "error", "error": "job_id invalido"})
        return
    if not isinstance(frames, int) or not (1 <= frames <= FRAMES_MAX):
        await send(writer, {"type": "error", "error": "frames fuera de rango"})
        return
    if not all(isinstance(v, (int, float)) and 0 < v <= 600
               for v in (dur_min, dur_max)) or dur_min >= dur_max:
        await send(writer, {"type": "error", "error": "rango de duracion invalido"})
        return

    job_rel = f"{RENDER_JOBS_DIR}/{job_id}"
    job_abs = os.path.join(PROJECT_DIR, job_rel)
    sonoro_rel = f"{job_rel}/promo_audio.mp4"
    if os.path.isfile(os.path.join(PROJECT_DIR, sonoro_rel)):
        video_rel = sonoro_rel
    else:
        video_rel = video_del_job(job_id)
    if video_rel is None:
        await send(writer, {"type": "error", "error": "video del job no encontrado"})
        return

    container = f"{CONTAINER_PREFIX}{job_id}-verifica"
    job_mount = f"{job_abs}:/workspace/{job_rel}:rw"
    code, out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", job_mount,
        "--name", container,
        "--entrypoint", "python3", "manim-render",
        f"/workspace/{VERIFICA_SCRIPT}", f"/workspace/{video_rel}",
        f"/workspace/{job_rel}/verificacion",
        "--frames", str(frames), "--min", str(dur_min), "--max", str(dur_max),
        timeout=VERIFICA_TIMEOUT,
    )
    if code != 0:
        await force_remove(container)
        log(f"[verifica] job={job_id} fallo (code={code})")
        await send(writer, {"type": "error",
                            "error": f"la verificacion salio con codigo {code}:"
                                     f" {(err or out)[-300:]}"})
        return
    try:
        informe = json.loads(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        await send(writer, {"type": "error",
                            "error": "la verificacion no devolvio un informe"})
        return
    log(f"[verifica] job={job_id} ok={informe.get('ok')}")
    await send(writer, {"type": "ok", "informe": informe})


async def handle_ensamblar(req: dict, writer: asyncio.StreamWriter) -> None:
    """Monta la pelicula de un proyecto con `ensamblar.py` en el contenedor.

    Igual que `postproceso` y `verificar`: del exterior solo llega un id
    validado con regex. El plan (que clips, en que orden, con que voz y que
    empalme) lo escribio el backend en <peliculas>/<pid>/plan.json, y sus rutas
    apuntan dentro de /workspace, que el contenedor ve read-only. Lo unico
    montado con escritura es el directorio de la pelicula.
    """
    pid = str(req.get("project_id", ""))
    modo = str(req.get("modo") or "montar")
    if not RE_JOB_ID.match(pid):
        await send(writer, {"type": "error", "error": "project_id invalido"})
        return
    if modo not in ("montar", "verificar"):
        await send(writer, {"type": "error", "error": "modo invalido"})
        return

    peli_rel = f"{PELICULAS_DIR}/{pid}"
    peli_abs = os.path.join(PROJECT_DIR, peli_rel)
    if not os.path.isfile(os.path.join(peli_abs, "plan.json")):
        await send(writer, {"type": "error", "error": "no hay plan que montar"})
        return

    container = f"{CONTAINER_PREFIX}{pid}-pelicula-{modo}"
    peli_mount = f"{peli_abs}:/workspace/{peli_rel}:rw"
    code, out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", peli_mount, "-v", montaje_render_jobs(),
        "--name", container,
        "--entrypoint", "python3", "manim-render",
        f"/workspace/{ENSAMBLAR_SCRIPT}", modo,
        f"/workspace/{peli_rel}/plan.json",
        f"/workspace/{peli_rel}/pelicula.mp4",
        timeout=(ENSAMBLAR_TIMEOUT if modo == "montar"
                 else ENSAMBLAR_VERIFICA_TIMEOUT),
    )
    if code != 0:
        await force_remove(container)
        log(f"[pelicula] pid={pid} modo={modo} fallo (code={code})")
        await send(writer, {"type": "error",
                            "error": f"{modo} salio con codigo {code}:"
                                     f" {(err or out)[-300:]}"})
        return
    try:
        informe = json.loads(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        await send(writer, {"type": "error",
                            "error": "el montaje no devolvio un informe"})
        return
    # En `verificar`, `ok:false` NO es un fallo del comando: es el resultado
    # (la pelicula tiene problemas). Solo el montaje puede fallar de verdad.
    if modo == "montar" and not informe.get("ok"):
        await send(writer, {"type": "error",
                            "error": informe.get("error", "montaje fallido")})
        return
    log(f"[pelicula] pid={pid} {modo} ok={informe.get('ok')} "
        f"piezas={informe.get('piezas')} dur={informe.get('duracion')}")
    await send(writer, {"type": "ok", "informe": informe})


async def handle_presentacion(req: dict, writer: asyncio.StreamWriter) -> None:
    """Parte los renders de una presentacion en sus fragmentos
    (`cortar_presentacion.py`).

    Igual que `ensamblar`: del exterior solo llega un id validado con regex.
    El plan (que videos, en que instantes cortar, con que nombre) lo escribio
    el backend en <presentaciones>/<pid>/plan.json y sus rutas apuntan dentro de
    /workspace, que el contenedor ve read-only. Lo unico montado con escritura
    es el directorio de la presentacion.

    Aqui NO se arma el .pptx: eso lo hace el backend con python-pptx, que no
    necesita ffmpeg. Partir la division asi evita meter una dependencia mas en
    la imagen de manim (y con ella, una reconstruccion en el VPS).
    """
    pid = str(req.get("project_id", ""))
    if not RE_JOB_ID.match(pid):
        await send(writer, {"type": "error", "error": "project_id invalido"})
        return

    pres_rel = f"{PRESENTACIONES_DIR}/{pid}"
    pres_abs = os.path.join(PROJECT_DIR, pres_rel)
    if not os.path.isfile(os.path.join(pres_abs, "plan.json")):
        await send(writer, {"type": "error", "error": "no hay plan que cortar"})
        return

    container = f"{CONTAINER_PREFIX}{pid}-presentacion"
    pres_mount = f"{pres_abs}:/workspace/{pres_rel}:rw"
    code, out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", pres_mount, "-v", montaje_render_jobs(),
        "--name", container,
        "--entrypoint", "python3", "manim-render",
        f"/workspace/{CORTAR_SCRIPT}",
        f"/workspace/{pres_rel}/plan.json",
        timeout=CORTAR_TIMEOUT,
    )
    if code != 0:
        await force_remove(container)
        log(f"[presentacion] pid={pid} fallo (code={code})")
        await send(writer, {"type": "error",
                            "error": f"el corte salio con codigo {code}:"
                                     f" {(err or out)[-300:]}"})
        return
    try:
        informe = json.loads(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        await send(writer, {"type": "error",
                            "error": "el corte no devolvio un informe"})
        return
    if not informe.get("ok"):
        await send(writer, {"type": "error",
                            "error": informe.get("error", "corte fallido")})
        return
    log(f"[presentacion] pid={pid} ok fragmentos={informe.get('total')}")
    await send(writer, {"type": "ok", "informe": informe})


async def handle_paleta(req: dict, writer: asyncio.StreamWriter) -> None:
    """Sintetiza el banco de sonidos como wavs sueltos (`sfx.py paleta`).

    El backend no tiene numpy: la sintesis vive donde vive todo lo demas que
    necesita librerias, en el contenedor. No recibe NADA del exterior — ni
    siquiera un id: el destino es una ruta fija.
    """
    destino_abs = os.path.join(PROJECT_DIR, SFX_DIR)
    _asegurar_dir_del_runner(destino_abs)
    container = f"{CONTAINER_PREFIX}paleta"
    code, out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", f"{destino_abs}:/workspace/{SFX_DIR}:rw",
        "--name", container,
        "--entrypoint", "python3", "manim-render",
        f"/workspace/{SFX_SCRIPT}", "paleta", f"/workspace/{SFX_DIR}",
        timeout=SFX_TIMEOUT,
    )
    if code != 0:
        await force_remove(container)
        log(f"[paleta] fallo (code={code})")
        await send(writer, {"type": "error",
                            "error": f"sfx.py paleta salio con codigo {code}:"
                                     f" {(err or out)[-300:]}"})
        return
    wavs = sorted(f[:-4] for f in os.listdir(destino_abs) if f.endswith(".wav"))
    log(f"[paleta] ok {len(wavs)} efectos")
    await send(writer, {"type": "ok", "sonidos": wavs})


async def handle_normalizar_voz(req: dict, writer: asyncio.StreamWriter) -> None:
    """Convierte una grabacion subida a WAV mono 24 kHz s16 (ffmpeg en el
    contenedor). Ver GUIONES_DIR: rutas cerradas, montaje rw del directorio
    del proyecto y nada mas."""
    slug = str(req.get("slug", ""))
    entrada = str(req.get("entrada", ""))
    salida = str(req.get("salida", ""))
    if not RE_SLUG.match(slug) or not RE_SUBIDA.match(entrada) \
            or not RE_SUBIDA.match(salida) or not salida.endswith(".wav"):
        await send(writer, {"type": "error", "error": "parametros invalidos"})
        return
    dir_rel = f"{GUIONES_DIR}/{slug}"
    dir_abs = os.path.join(PROJECT_DIR, dir_rel)
    if not os.path.isfile(os.path.join(dir_abs, entrada)):
        await send(writer, {"type": "error", "error": "archivo subido no encontrado"})
        return
    container = f"{CONTAINER_PREFIX}voz-{slug[:24]}"
    code, out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", f"{os.path.realpath(dir_abs)}:/workspace/{dir_rel}:rw",
        "--name", container,
        "--entrypoint", "ffmpeg", "manim-render",
        "-y", "-v", "error", "-i", f"/workspace/{dir_rel}/{entrada}",
        "-vn", "-ac", "1", "-ar", "24000", "-sample_fmt", "s16",
        "-f", "wav", f"/workspace/{dir_rel}/{salida}",
        timeout=NORMALIZAR_TIMEOUT,
    )
    if code != 0 or not os.path.isfile(os.path.join(dir_abs, salida)):
        await force_remove(container)
        log(f"[voz] slug={slug} conversion fallo (code={code})")
        await send(writer, {"type": "error",
                            "error": f"ffmpeg salio con codigo {code}:"
                                     f" {(err or out)[-300:]}"})
        return
    log(f"[voz] slug={slug} ok {entrada} -> {salida}")
    await send(writer, {"type": "ok", "salida": f"{dir_rel}/{salida}"})


async def handle_musica(req: dict, writer: asyncio.StreamWriter) -> None:
    """Sintetiza el banco de musica como wavs sueltos (`musica.py banco`).

    Calcado de `handle_paleta`, y por la misma razon: el backend no tiene
    numpy y la sintesis vive donde vive todo lo que necesita librerias. No
    recibe NADA del exterior — ni siquiera un id: el destino es una ruta fija.
    """
    destino_abs = os.path.join(PROJECT_DIR, MUSICA_DIR)
    _asegurar_dir_del_runner(destino_abs)
    container = f"{CONTAINER_PREFIX}musica"
    code, out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", f"{destino_abs}:/workspace/{MUSICA_DIR}:rw",
        "--name", container,
        "--entrypoint", "python3", "manim-render",
        f"/workspace/{MUSICA_SCRIPT}", "banco", f"/workspace/{MUSICA_DIR}",
        timeout=MUSICA_TIMEOUT,
    )
    if code != 0:
        await force_remove(container)
        log(f"[musica] fallo (code={code})")
        await send(writer, {"type": "error",
                            "error": f"musica.py banco salio con codigo {code}:"
                                     f" {(err or out)[-300:]}"})
        return
    wavs = sorted(f[:-4] for f in os.listdir(destino_abs) if f.endswith(".wav"))
    log(f"[musica] ok {len(wavs)} temas")
    await send(writer, {"type": "ok", "temas": wavs})


async def handle_cancel(req: dict, writer: asyncio.StreamWriter) -> None:
    job_id = str(req.get("job_id", ""))
    if not RE_JOB_ID.match(job_id):
        await send(writer, {"type": "error", "error": "job_id invalido"})
        return
    # Solo contenedores con el prefijo propio: imposible tocar produccion.
    await force_remove(CONTAINER_PREFIX + job_id)
    log(f"[cancel] job={job_id}")
    await send(writer, {"type": "ok"})


# ── fotogramas y laboratorio (R3b) ────────────────────────────────────────────
#
# Tres comandos que cierran la brecha «lo que se ve y lo que se mide en la
# terminal, en la app»:
#
#   - frames    : la hoja de contactos de un render (N fotogramas + el ultimo
#                 real). `hoja_contactos.py tira` en el contenedor, ruta fija
#                 del script y del destino; del exterior solo llegan el job_id
#                 y cuantos fotogramas.
#   - fotograma : un PNG a la resolucion pedida desde el mp4 del job (la
#                 figura de una tesis). El nombre del archivo lo DERIVA el
#                 runner de (t, ancho): nunca llega del exterior.
#   - ejecutar  : Python de validacion en el sandbox (las `sonda_*.py`). El
#                 mismo contenedor que un render —que ya ejecuta Python
#                 arbitrario— con el repo read-only, sin red, y como unico
#                 directorio escribible el del laboratorio.

CONTACTOS_SCRIPT = "studio/tools/hoja_contactos.py"
CONTACTOS_TIMEOUT = 300
# Tope de la hoja: mas de 24 miniaturas no se revisan de una mirada, y cada
# una es un `ffmpeg -ss` con su decodificacion.
HOJA_MAX = 24
ANCHO_TIRA = 480
# 4K: mas alla no hay pantalla ni pagina. Es el mismo techo que ANCHO_MAX de
# hoja_contactos.py (si uno cambia, el otro tambien).
ANCHO_FIGURA_MIN, ANCHO_FIGURA_MAX = 320, 3840
T_MAX = 21600.0  # 6 h: cualquier instante posible de una pelicula montada

# Laboratorio: un directorio por ejecucion bajo render_jobs/lab/, escrito por
# el backend (script.py) y montado rw solo para su contenedor.
LAB_DIR = f"{RENDER_JOBS_DIR}/lab"
LAB_TIMEOUT_MIN, LAB_TIMEOUT_MAX = 30, 900
# Tope por flujo. Una sonda imprime ~100 lineas; un bucle desbocado imprime
# hasta llenar el disco del backend si nadie corta.
LAB_SALIDA_MAX = 200 * 1024
# `import sistemas` tiene que funcionar en el laboratorio igual que en una
# sonda: es la MISMA ruta que cfg.manim_extensions_dir del backend.
LAB_PYTHONPATH = "/workspace/studio/content/manim_extensions"
# Sondas: ruta CERRADA (studio/tools/sonda_<nombre>.py) y sin argumentos.
RE_SONDA = re.compile(r"^[a-z0-9_]{1,32}$")
SONDAS_DIR = "studio/tools"
# Lo que un script del laboratorio puede dejar como resultado. Fuera de esta
# lista no se enumera (ni se sirve): un .py o un .sh producidos por el script
# no son un resultado que la app tenga que ofrecer de vuelta.
LAB_EXT = {".png", ".jpg", ".jpeg", ".svg", ".wav", ".txt", ".json",
           ".csv", ".md", ".log"}
RE_LAB_ARCHIVO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


def _recorta(texto: str) -> str:
    """Salida acotada, diciendo que se acoto (un limite silencioso miente)."""
    if len(texto) <= LAB_SALIDA_MAX:
        return texto
    return texto[:LAB_SALIDA_MAX] + f"\n… [recortado en {LAB_SALIDA_MAX} bytes]"


# `docker compose run` escribe su propio progreso en stderr ("Container …
# Creating/Created/Removing"). En los demas comandos da igual porque lo que se
# lee es el JSON de stdout; aqui NO: el stderr del laboratorio se le ensena al
# usuario tal cual, y con esas dos lineas siempre delante un traceback de
# Python queda enterrado bajo ruido del orquestador.
RE_COMPOSE = re.compile(
    r"^\s*(?:Container|Network|Volume|Image)\s+\S+\s+"
    r"(?:Creating|Created|Starting|Started|Stopping|Stopped|Removing|Removed|"
    r"Recreate|Recreated|Running|Waiting|Pulling|Pulled|Built|Building)\s*$")


def _limpia_stderr(texto: str) -> str:
    return "\n".join(l for l in texto.splitlines() if not RE_COMPOSE.match(l))


async def handle_frames(req: dict, writer: asyncio.StreamWriter) -> None:
    """Hoja de contactos del render: n fotogramas + el ultimo real."""
    job_id = str(req.get("job_id", ""))
    n = req.get("n", 8)
    if not RE_JOB_ID.match(job_id):
        await send(writer, {"type": "error", "error": "job_id invalido"})
        return
    if not isinstance(n, int) or isinstance(n, bool) or not (1 <= n <= HOJA_MAX):
        await send(writer, {"type": "error", "error": "n fuera de rango"})
        return

    video_rel = video_del_job(job_id)
    if video_rel is None:
        await send(writer, {"type": "error", "error": "video del job no encontrado"})
        return

    job_rel = f"{RENDER_JOBS_DIR}/{job_id}"
    job_abs = os.path.join(PROJECT_DIR, job_rel)
    container = f"{CONTAINER_PREFIX}{job_id}-frames"
    job_mount = f"{os.path.realpath(job_abs)}:/workspace/{job_rel}:rw"
    code, out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", job_mount,
        "--name", container,
        "--entrypoint", "python3", "manim-render",
        f"/workspace/{CONTACTOS_SCRIPT}", "tira",
        f"/workspace/{video_rel}", f"/workspace/{job_rel}/frames",
        "--n", str(n), "--ancho", str(ANCHO_TIRA),
        timeout=CONTACTOS_TIMEOUT,
    )
    informe = _ultimo_json(out)
    if code != 0 or informe is None or not informe.get("ok"):
        await force_remove(container)
        detalle = (informe or {}).get("error") or (err or out)[-300:]
        log(f"[frames] job={job_id} fallo (code={code})")
        await send(writer, {"type": "error",
                            "error": f"la hoja de contactos fallo: {detalle}"})
        return
    log(f"[frames] job={job_id} ok n={n} dur={informe.get('duracion')}")
    await send(writer, {"type": "ok", "informe": informe})


async def handle_fotograma(req: dict, writer: asyncio.StreamWriter) -> None:
    """Un fotograma a la resolucion pedida: la figura estatica de un paper."""
    job_id = str(req.get("job_id", ""))
    t = req.get("t", 0.0)
    ancho = req.get("ancho", 1920)
    formato = str(req.get("formato") or "png")
    if not RE_JOB_ID.match(job_id):
        await send(writer, {"type": "error", "error": "job_id invalido"})
        return
    if isinstance(t, bool) or not isinstance(t, (int, float)) \
            or not (0 <= float(t) <= T_MAX):
        await send(writer, {"type": "error", "error": "instante fuera de rango"})
        return
    if not isinstance(ancho, int) or isinstance(ancho, bool) \
            or not (ANCHO_FIGURA_MIN <= ancho <= ANCHO_FIGURA_MAX):
        await send(writer, {"type": "error", "error": "ancho fuera de rango"})
        return
    if formato != "png":
        await send(writer, {"type": "error", "error": "formato invalido"})
        return

    video_rel = video_del_job(job_id)
    if video_rel is None:
        await send(writer, {"type": "error", "error": "video del job no encontrado"})
        return

    # El nombre lo DERIVA el runner de los dos numeros ya validados: del
    # exterior no llega ni una ruta ni un nombre de archivo.
    nombre = f"t{int(round(float(t) * 1000)):08d}_{ancho}.png"
    job_rel = f"{RENDER_JOBS_DIR}/{job_id}"
    job_abs = os.path.join(PROJECT_DIR, job_rel)
    container = f"{CONTAINER_PREFIX}{job_id}-figura"
    job_mount = f"{os.path.realpath(job_abs)}:/workspace/{job_rel}:rw"
    code, out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", job_mount,
        "--name", container,
        "--entrypoint", "python3", "manim-render",
        f"/workspace/{CONTACTOS_SCRIPT}", "figura",
        f"/workspace/{video_rel}", f"/workspace/{job_rel}/figuras/{nombre}",
        "--t", f"{float(t):.4f}", "--ancho", str(ancho),
        timeout=CONTACTOS_TIMEOUT,
    )
    informe = _ultimo_json(out)
    if code != 0 or informe is None or not informe.get("ok"):
        await force_remove(container)
        detalle = (informe or {}).get("error") or (err or out)[-300:]
        log(f"[figura] job={job_id} fallo (code={code})")
        await send(writer, {"type": "error",
                            "error": f"el fotograma fallo: {detalle}"})
        return
    log(f"[figura] job={job_id} ok {nombre} {informe.get('ancho')}x{informe.get('alto')}")
    await send(writer, {"type": "ok", "informe": informe})


def _ultimo_json(salida: str) -> dict | None:
    """El informe es la ULTIMA linea de stdout (el resto puede ser ruido de
    docker compose o de ffmpeg)."""
    try:
        return json.loads(salida.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None


def _archivos_lab(lab_abs: str) -> list[dict]:
    """Lo que el script dejo en su directorio: nombre y tamano.

    Solo el primer nivel y solo extensiones de resultado: ni se recorre el
    arbol ni se enumera lo que el propio laboratorio escribio (script.py,
    meta.json)."""
    salida = []
    try:
        nombres = sorted(os.listdir(lab_abs))
    except OSError:
        return salida
    for nombre in nombres:
        if nombre in ("script.py", "meta.json"):
            continue
        if not RE_LAB_ARCHIVO.match(nombre):
            continue
        if os.path.splitext(nombre)[1].lower() not in LAB_EXT:
            continue
        ruta = os.path.join(lab_abs, nombre)
        if not os.path.isfile(ruta):
            continue
        salida.append({"nombre": nombre, "bytes": os.path.getsize(ruta)})
    return salida


async def handle_ejecutar(req: dict, writer: asyncio.StreamWriter) -> None:
    """Corre Python de validacion en el sandbox y devuelve lo que produjo.

    Ejecutar Python no confiable NO es una capacidad nueva: cada render lo
    hace desde el primer dia (una escena de manim es Python arbitrario). Lo
    que cambia es que aqui el script no dibuja, mide. Las garantias son las
    mismas y estan en docker-compose.yml: sin red, repo read-only, cap_drop
    ALL, no-new-privileges, 1.5 vCPU / 2 GB / 256 pids y --rm. Lo unico
    escribible es el directorio de ESTA ejecucion.
    """
    lab_id = str(req.get("lab_id", ""))
    sonda = str(req.get("sonda") or "")
    timeout = req.get("timeout", 120)
    if not RE_JOB_ID.match(lab_id):
        await send(writer, {"type": "error", "error": "lab_id invalido"})
        return
    if not isinstance(timeout, int) or isinstance(timeout, bool) \
            or not (LAB_TIMEOUT_MIN <= timeout <= LAB_TIMEOUT_MAX):
        await send(writer, {"type": "error", "error": "timeout fuera de rango"})
        return

    lab_rel = f"{LAB_DIR}/{lab_id}"
    lab_abs = os.path.join(PROJECT_DIR, lab_rel)
    if not os.path.isdir(lab_abs):
        await send(writer, {"type": "error",
                            "error": "el directorio del laboratorio no existe"})
        return

    if sonda:
        if not RE_SONDA.match(sonda):
            await send(writer, {"type": "error", "error": "sonda invalida"})
            return
        script_rel = f"{SONDAS_DIR}/sonda_{sonda}.py"
        if not os.path.isfile(os.path.join(PROJECT_DIR, script_rel)):
            await send(writer, {"type": "error", "error": "esa sonda no existe"})
            return
    else:
        script_rel = f"{lab_rel}/script.py"
        if not os.path.isfile(os.path.join(PROJECT_DIR, script_rel)):
            await send(writer, {"type": "error",
                                "error": "el laboratorio no tiene script.py"})
            return

    container = f"{CONTAINER_PREFIX}{lab_id}-lab"
    lab_mount = f"{os.path.realpath(lab_abs)}:/workspace/{lab_rel}:rw"
    code, out, err = await run_cmd(
        "docker", "compose", "-f", COMPOSE_FILE, "--profile", "render",
        "run", "--rm", "--no-deps", "-T", *RUN_AS_ARGS,
        "-v", lab_mount,
        "-w", f"/workspace/{lab_rel}",
        "-e", f"PYTHONPATH={LAB_PYTHONPATH}",
        "--name", container,
        "--entrypoint", "python3", "manim-render",
        f"/workspace/{script_rel}",
        # Margen sobre el timeout pedido: arrancar el contenedor y bajarlo no
        # es tiempo del script, y sin margen un script que tarda justo lo
        # pedido se reporta como matado por el runner.
        timeout=timeout + 30,
    )
    timed_out = code == 124
    if timed_out:
        await force_remove(container)
    # Un `exit 1` NO es un fallo del comando: es el resultado (una sonda con
    # invariantes rotos sale con 1 a proposito). Solo el timeout y el runner
    # caido son errores de verdad.
    log(f"[lab] id={lab_id} sonda={sonda or '-'} exit={code} "
        f"timed_out={timed_out} archivos={len(_archivos_lab(lab_abs))}")
    await send(writer, {"type": "ok", "code": code, "timed_out": timed_out,
                        "stdout": _recorta(out),
                        "stderr": _recorta(_limpia_stderr(err)),
                        "archivos": _archivos_lab(lab_abs)})


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
        elif cmd == "postproceso":
            await handle_postproceso(req, writer)
        elif cmd == "verificar":
            await handle_verificar(req, writer)
        elif cmd == "ensamblar":
            await handle_ensamblar(req, writer)
        elif cmd == "presentacion":
            await handle_presentacion(req, writer)
        elif cmd == "normalizar_voz":
            await handle_normalizar_voz(req, writer)
        elif cmd == "paleta":
            await handle_paleta(req, writer)
        elif cmd == "musica":
            await handle_musica(req, writer)
        elif cmd == "thumbnail":
            await handle_thumbnail(req, writer)
        elif cmd == "frames":
            await handle_frames(req, writer)
        elif cmd == "fotograma":
            await handle_fotograma(req, writer)
        elif cmd == "ejecutar":
            await handle_ejecutar(req, writer)
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
    try:
        gid = grp.getgrnam(SOCKET_GROUP).gr_gid
        # El grupo debe poder atravesar el directorio ademas de usar el socket.
        os.chown(os.path.dirname(SOCKET_PATH), 0, gid)
        os.chmod(os.path.dirname(SOCKET_PATH), 0o750)
        os.chown(SOCKET_PATH, 0, gid)
        os.chmod(SOCKET_PATH, 0o660)
        log(f"manim-runner escuchando en {SOCKET_PATH} (grupo {SOCKET_GROUP})")
    except (KeyError, PermissionError) as exc:
        # Desarrollo local: sin grupo manimstudio o sin root para el chown. El
        # socket queda con los permisos del usuario que lo creo, que es el mismo
        # que corre el backend. En el VPS esto NO se alcanza (runner = root).
        os.chmod(SOCKET_PATH, 0o600)
        log(f"manim-runner escuchando en {SOCKET_PATH} "
            f"(modo dev, solo el usuario actual: {exc})")

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

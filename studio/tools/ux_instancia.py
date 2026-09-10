#!/usr/bin/env python3
"""Instancia local de ManimStudio para el QA visual del rediseno.

La auditoria (`ux_auditoria.mjs`) mide el pixel que se pinta, y una vista
vacia no pinta casi nada: sin datos, el instrumento da 0 fallos porque no hay
texto que medir. Este script levanta un backend real sobre un workspace
aislado (/tmp) y lo SIEMBRA con un catalogo parecido al de produccion:
familias de cursos, clips, un promo vertical, guiones, una narracion grabada
y un historial de renders con sus estados.

Lo que NO toca: la base de datos de desarrollo, `render_jobs/` ni `exports/`.
El contenido de solo lectura (lecciones, animaciones, cursos del repo,
entregas) se enlaza al repo real para que las vistas ensenen lo de verdad.

    studio/backend/venv/bin/python studio/tools/ux_instancia.py [--puerto 3002]

Imprime `COOKIE=<cookie de sesion firmada>` y se queda corriendo hasta
Ctrl-C. Con eso:

    node studio/tools/ux_auditoria.mjs --base http://127.0.0.1:4173 \
         --cookie "$COOKIE"
"""

import argparse
import json
import os
import shutil
import signal
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BACKEND = REPO / "studio" / "backend"
USUARIO = "ux"
PASSWORD = "ux-qa-password-123"

SCRIPT_CLIP = '''from manim import *


class Clip{n}(Scene):
    def construct(self):
        titulo = Text("{titulo}", font_size=42)
        self.play(Write(titulo))
        self.wait(1.2)
        self.play(FadeOut(titulo))
'''

CATALOGO = [
    ("Aerodinamica · 1.1 El flujo alrededor del perfil",
     "Lineas de corriente, angulo de ataque y el primer mapa de presiones.",
     "curso", "horizontal", ["El perfil en la corriente", "Presion arriba y abajo",
                             "El angulo de ataque", "Lo que sostiene al avion"]),
    ("Aerodinamica · 1.2 Capa limite y transicion",
     "De laminar a turbulenta: donde se pega el aire y donde se suelta.",
     "curso", "horizontal", ["El aire pegado a la piel", "Laminar",
                             "La transicion", "Turbulenta"]),
    ("Aerodinamica · 2.1 Resistencia inducida",
     "El precio de la sustentacion: torbellinos en la punta del ala.",
     "curso", "horizontal", ["El torbellino de punta", "La estela",
                             "El alargamiento"]),
    ("Metrologia optica · 1.1 La luz como regla",
     "Medir con longitudes de onda: el patron que no se desgasta.",
     "curso", "horizontal", ["La onda como patron", "Contar franjas",
                             "El error de la regla", "La incertidumbre"]),
    ("Metrologia optica · 1.2 Interferometria",
     "Dos caminos, una diferencia: leer nanometros con franjas.",
     "curso", "horizontal", ["Dos caminos", "La franja se mueve",
                             "Nanometros"]),
    ("Promo · Satelites en 60 segundos",
     "Pieza vertical para redes: una orbita, un enlace, un dato.",
     "promo", "vertical", ["El pase", "El enlace", "El dato"]),
]


def log(msg):
    print(f"· {msg}", flush=True)


def entorno(ws: Path) -> dict:
    import bcrypt
    env = dict(os.environ)
    env.update({
        "MS_ADMIN_USER": USUARIO,
        "MS_ADMIN_PASSWORD_HASH": bcrypt.hashpw(
            PASSWORD.encode(), bcrypt.gensalt(rounds=4)).decode(),
        "MS_SECRET_KEY": "ux-qa-secret-key",
        "MS_WORKSPACE": str(ws),
        "MS_DB_PATH": str(ws / "manimstudio.db"),
        "MS_RUNNER_SOCKET": str(ws / "runner.sock"),
        "MS_COOKIE_SECURE": "0",
        "MS_GCP_KEY_PATH": str(ws / "no-hay-clave.json"),
        # Contenido de solo lectura: el del repo, para que las vistas
        # ensenen lo real (lecciones, animaciones, cursos, entregas).
        "MS_LESSONS_DIR": str(REPO / "studio" / "content" / "lessons"),
        "MS_ANIMATIONS_DIR": str(REPO / "studio" / "content" / "animations"),
        "MS_CONTENT_DIR": str(REPO / "studio" / "content"),
        "MS_EXPORTS_DIR": str(REPO / "exports"),
        "MS_PELICULAS_DIR": str(ws / "exports" / "peliculas"),
        "MS_GUIONES_DIR": str(ws / "guiones"),
        # Voz sin salir a la red ni a GCP.
        "MS_TTS_PROVIDER": "archivo",
        "MS_TTS_PROVEEDORES": "archivo",
        "MS_PIPER_VOICES_DIR": str(ws / "voces"),
        "PYTHONPATH": str(BACKEND),
    })
    return env


def preparar(ws: Path) -> None:
    if ws.exists():
        shutil.rmtree(ws)
    (ws / "studio").mkdir(parents=True)
    # Las sondas del Laboratorio salen de <workspace>/studio/tools.
    (ws / "studio" / "tools").symlink_to(REPO / "studio" / "tools")
    (ws / "render_jobs").mkdir()
    (ws / "exports" / "peliculas").mkdir(parents=True)


class Cliente:
    def __init__(self, base: str) -> None:
        self.base = base
        self.cookie = ""

    def pide(self, metodo: str, ruta: str, cuerpo=None, crudo=None,
             tipo="application/json"):
        datos = crudo if crudo is not None else (
            json.dumps(cuerpo).encode() if cuerpo is not None else None)
        req = urllib.request.Request(self.base + ruta, data=datos, method=metodo)
        if datos is not None:
            req.add_header("Content-Type", tipo)
        if self.cookie:
            req.add_header("Cookie", f"ms_session={self.cookie}")
        with urllib.request.urlopen(req, timeout=30) as r:
            cabecera = r.headers.get("Set-Cookie", "")
            if "ms_session=" in cabecera:
                self.cookie = cabecera.split("ms_session=")[1].split(";")[0]
            texto = r.read().decode()
        return json.loads(texto) if texto.strip().startswith(("{", "[")) else texto


def wav_silencio(path: Path, segundos: float = 2.5, rate: int = 24000) -> bytes:
    """Un WAV valido y silencioso: sirve de 'grabacion propia' sin red."""
    marcos = int(segundos * rate)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        # Un tono muy bajo en vez de silencio puro: `registrar_subida`
        # recorta el silencio y una pista muda quedaria en cero.
        w.writeframes(b"".join(
            struct.pack("<h", int(600 * ((i // 40) % 2 * 2 - 1)))
            for i in range(marcos)))
    return path.read_bytes()


def sembrar(base: str, ws: Path) -> str:
    c = Cliente(base)
    c.pide("POST", "/api/login", {"username": USUARIO, "password": PASSWORD})
    proyectos = []
    for nombre, desc, tipo, formato, clips in CATALOGO:
        p = c.pide("POST", "/api/projects", {
            "name": nombre, "description": desc, "quality": "qm",
            "tipo": tipo, "formato": formato, "fondo": "marca",
        })
        for i, titulo in enumerate(clips, 1):
            c.pide("POST", f"/api/projects/{p['id']}/clips", {
                "title": titulo, "scene": f"Clip{i}",
                "script": SCRIPT_CLIP.format(n=i, titulo=titulo),
            })
        proyectos.append(c.pide("GET", f"/api/projects/{p['id']}"))
    log(f"{len(proyectos)} proyectos sembrados")

    # Guion escrito en dos cursos y una grabacion propia en el primer clip:
    # asi el indice ensena narracion parcial y el detalle los tres estados.
    wav = wav_silencio(ws / "voz.wav")
    narrados = 0
    for p in proyectos[:2]:
        for clip in p["clips"][:2]:
            c.pide("PUT", f"/api/projects/{p['id']}/narracion/{clip['id']}/guion", {
                "secciones": [
                    {"t_inicio": 0, "t_fin": 4, "texto": (
                        f"{clip['title']}. Lo que se ve en pantalla no es un "
                        "adorno: cada trazo mide algo.")},
                    {"t_inicio": 4, "t_fin": 9, "texto": (
                        "La escala de la figura sale de los datos, no de lo "
                        "que quede bonito en el cuadro.")},
                ]})
        clip = p["clips"][0]
        c.pide("PUT",
               f"/api/projects/{p['id']}/narracion/{clip['id']}/audio?nombre=voz.wav",
               crudo=wav, tipo="audio/wav")
        narrados += 1
    log(f"guiones en 4 clips, narracion grabada en {narrados}")

    # Historial de renders: la cola en memoria no puede producirlo sin el
    # runner, asi que se escribe en la base con los estados que pinta la UI.
    sys.path.insert(0, str(BACKEND))
    from app.db import Database  # noqa: E402  (necesita el env ya puesto)
    db = Database(ws / "manimstudio.db")
    ahora = time.time()
    plan = [
        ("done", 0), ("done", 1), ("done", 2), ("error", 3), ("queued", 4),
    ]
    for i, (estado, k) in enumerate(plan):
        p = proyectos[k % len(proyectos)]
        clip = p["clips"][0]
        # El id de un job es hexadecimal de 16 (RE_JOB_ID en la API): con
        # letras fuera de [0-9a-f] la app pide un job que devuelve 404 y el
        # QA lo cuenta como error de consola de la interfaz.
        jid = f"fada{i:04d}" + "0" * 8
        job_dir = ws / "render_jobs" / jid
        job_dir.mkdir(parents=True, exist_ok=True)
        video = job_dir / "video.mp4"
        video.write_bytes(b"\x00" * 4096)
        db.insert_job({
            "id": jid, "scene": clip["scene"] or "Clip1", "quality": "qm",
            "timeout": 600, "status": estado,
            "script": SCRIPT_CLIP.format(n=1, titulo=clip["title"]),
            "created_at": ahora - 3600 * (i + 1),
            "project_id": p["id"], "clip_id": clip["id"],
            "content_hash": None, "formato": p.get("formato", "horizontal"),
            "fondo": "marca",
        })
        if estado == "done":
            db.update_job(jid, started_at=ahora - 3600 * (i + 1) + 5,
                          finished_at=ahora - 3600 * (i + 1) + 95,
                          video_path=str(video), size_bytes=4096,
                          resolution="1280x720")
        elif estado == "error":
            db.update_job(
                jid, started_at=ahora - 3600 * (i + 1) + 5,
                finished_at=ahora - 3600 * (i + 1) + 12,
                error="Traceback (most recent call last):\n"
                      "  File \"scene.py\", line 12, in construct\n"
                      "    self.play(Write(titulo))\n"
                      "NameError: name 'titulo' is not defined")
    log(f"{len(plan)} renders en el historial")
    return c.cookie


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", type=int, default=3002)
    ap.add_argument("--ws", default="/tmp/ms-ux")
    args = ap.parse_args()

    ws = Path(args.ws)
    preparar(ws)
    env = entorno(ws)
    base = f"http://127.0.0.1:{args.puerto}"

    proc = subprocess.Popen(
        [str(BACKEND / "venv" / "bin" / "uvicorn"), "app.main:app",
         "--host", "127.0.0.1", "--port", str(args.puerto), "--log-level", "warning"],
        cwd=str(BACKEND), env=env)
    try:
        for _ in range(120):
            try:
                urllib.request.urlopen(base + "/api/health", timeout=2).read()
                break
            except (urllib.error.URLError, OSError):
                time.sleep(0.5)
        else:
            raise SystemExit("el backend no respondio a /api/health")
        log(f"backend vivo en {base}")
        cookie = sembrar(base, ws)
        print(f"\nCOOKIE={cookie}\nBASE={base}\n", flush=True)
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
        proc.wait()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

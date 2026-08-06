"""Narracion de clips: guion cronometrado con Gemini + voz con Gemini TTS.

Logica compartida entre el CLI (studio/tools/guiones.py) y el endpoint
"Generar narracion" de Proyectos. La salida vive en <workspace>/guiones/
<slug-proyecto>/ (md + txt + wav + estado.json), fuera de render_jobs/ y de
la cola de render: narrar no encola jobs ni toca los videos.

Reusa la service account del asistente IA (mismo feature-flag: sin
gcp-key.json no hay narracion). El SDK de google-genai se importa perezoso,
igual que en ai.py (el servicio corre con MemoryMax=512M).
"""

import asyncio
import hashlib
import json
import re
import struct
import time
import unicodedata
import wave
from pathlib import Path

from .projects import compose_script

# Narracion en español pausada: ~2.2 palabras/s, y solo se apunta al 90 %
# de la duracion del video para dejar aire entre secciones.
PALABRAS_POR_SEGUNDO = 2.2
MARGEN = 0.9
MAX_PALABRAS_SIN_RENDER = 160
TTS_RATE = 24_000  # PCM mono 16-bit que devuelve Gemini TTS
TTS_MAX_CHARS = 3_000  # por llamada; las secciones se agrupan hasta este tope
PAUSA_ENTRE_TROZOS_S = 0.35
# El audio puede exceder el video hasta este factor antes de reintentar con
# un presupuesto de palabras mas corto.
TOLERANCIA_AUDIO = 1.05
# Alineado por secciones: silencio maximo insertado entre secciones (los
# t_inicio del guion son estimados; huecos mas largos son casi siempre un
# error de estimacion y desincronizan el final).
MAX_HUECO_S = 2.5
# Recorte de silencio del TTS: umbral de amplitud (int16) y margen conservado.
UMBRAL_SILENCIO = 300
MARGEN_SILENCIO_S = 0.12

INSTRUCCION_TTS = (
    "Lee el siguiente guion de un video de divulgación científica en "
    "español, con tono cálido, claro y pausado, como la voz en off de un "
    "documental:\n\n"
)

GUION_SCHEMA = {
    "type": "object",
    "properties": {
        "secciones": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "t_inicio": {"type": "number"},
                    "t_fin": {"type": "number"},
                    "momento": {"type": "string"},
                    "texto": {"type": "string"},
                },
                "required": ["t_inicio", "t_fin", "momento", "texto"],
            },
        },
    },
    "required": ["secciones"],
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]
    return slug or "clip"


def etiqueta_clip(position: int, title: str) -> str:
    return f"{position + 1:02d}-{slugify(title)}"


def duracion_mp4(path: Path) -> float | None:
    """Duracion en segundos leyendo el atomo moov/mvhd (sin ffprobe)."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    pos, end = 0, len(data)
    while pos + 8 <= end:  # nivel raiz: buscar moov
        size, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if size < 8:
            return None
        if kind == b"moov":
            inner, inner_end = pos + 8, pos + size
            while inner + 8 <= min(inner_end, end):
                isize, ikind = struct.unpack(">I4s", data[inner:inner + 8])
                if isize < 8:
                    return None
                if ikind == b"mvhd":
                    body = data[inner + 8:inner + isize]
                    version = body[0]
                    if version == 1:
                        timescale, duration = struct.unpack(">IQ", body[20:32])
                    else:
                        timescale, duration = struct.unpack(">II", body[12:20])
                    return duration / timescale if timescale else None
                inner += isize
            return None
        pos += size
    return None


def hash_guion(script_compuesto: str, scene: str, video_s: float | None,
               voz: str) -> str:
    """Detecta guiones desactualizados: cambia el script, la escena, la
    duracion del render (redondeada al segundo) o la voz -> stale."""
    h = hashlib.sha256(script_compuesto.encode())
    h.update(f"\n# scene: {scene}".encode())
    h.update(f"\n# video_s: {round(video_s) if video_s else 0}".encode())
    h.update(f"\n# voz: {voz}".encode())
    return h.hexdigest()


# ── Vertex AI ────────────────────────────────────────────────────────────────

class VertexNarrador:
    """Cliente Vertex para guion (JSON) y TTS. Llamadas bloqueantes: usarlo
    desde un thread (asyncio.to_thread) o desde un CLI."""

    def __init__(self, key_path: Path, location: str, model_guion: str,
                 model_tts: str) -> None:
        if not key_path.is_file():
            raise RuntimeError(
                f"No existe la service account {key_path}: la narracion "
                "necesita el mismo acceso a Vertex AI que el asistente IA.")
        from google import genai
        from google.oauth2 import service_account

        self.types = __import__("google.genai.types", fromlist=["types"])
        self.model_guion = model_guion
        self.model_tts = model_tts
        project = json.loads(key_path.read_text())["project_id"]
        creds = service_account.Credentials.from_service_account_file(
            str(key_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"])
        self.client = genai.Client(vertexai=True, project=project,
                                   location=location, credentials=creds)

    def guion(self, system: str, user: str) -> dict:
        t = self.types
        resp = self.client.models.generate_content(
            model=self.model_guion,
            contents=user,
            config=t.GenerateContentConfig(
                system_instruction=system,
                temperature=0.6,
                max_output_tokens=8192,
                response_mime_type="application/json",
                response_schema=GUION_SCHEMA,
            ),
        )
        return json.loads(resp.text)

    def tts(self, texto: str, voz: str) -> bytes:
        t = self.types
        for intento in (1, 2, 3):
            try:
                resp = self.client.models.generate_content(
                    model=self.model_tts,
                    contents=INSTRUCCION_TTS + texto,
                    config=t.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=t.SpeechConfig(
                            voice_config=t.VoiceConfig(
                                prebuilt_voice_config=t.PrebuiltVoiceConfig(
                                    voice_name=voz))),
                    ),
                )
                part = resp.candidates[0].content.parts[0]
                return part.inline_data.data
            except Exception:
                if intento == 3:
                    raise
                time.sleep(5 * intento)
        raise RuntimeError("unreachable")


def prompt_guion(curso: dict, clip: dict, script_compuesto: str,
                 video_s: float | None, max_palabras: int) -> tuple[str, str]:
    dur = f"{video_s:.1f} segundos" if video_s else "desconocida (sin render)"
    system = (
        "Eres guionista de divulgación científica en español (estilo "
        "3Blue1Brown: cercano, preciso, sin grandilocuencia). Recibes el "
        "script de Manim de un clip de video ya renderizado: los comentarios, "
        "los textos en pantalla y los run_time/wait te dicen qué se ve y "
        "cuándo. Escribe la narración en off que acompaña al video.\n"
        "Reglas:\n"
        "- Divide la narración en secciones alineadas con los momentos "
        "visuales del script; t_inicio/t_fin en segundos aproximados según "
        "los run_time y wait acumulados.\n"
        f"- La narración completa NO debe superar {max_palabras} palabras "
        "(el video dura " + dur + " y la voz debe caber con aire).\n"
        "- No leas en voz alta los textos que ya aparecen en pantalla: "
        "complétalos o coméntalos, no los repitas literalmente.\n"
        "- Frases cortas, aptas para texto-a-voz: sin fórmulas en notación "
        "matemática (di «zeta al cuadrado más c», no «z^2+c»), sin "
        "paréntesis largos ni siglas sin desarrollar.\n"
        "- 'momento' es una etiqueta breve de lo que se ve en pantalla."
    )
    user = (
        f"CURSO: {curso['name']}\n"
        f"DESCRIPCION DEL CURSO: {curso['description']}\n"
        f"CLIP {clip['position'] + 1} de {curso['total_clips']}: {clip['title']}\n"
        f"ESCENA: {clip['scene']}\n"
        f"DURACION REAL DEL VIDEO: {dur}\n\n"
        f"SCRIPT MANIM (estilo del curso + clip):\n{script_compuesto}"
    )
    return system, user


def render_md(curso: dict, clip: dict, secciones: list[dict], narracion: str,
              video_s: float | None, voz: str, model_tts: str) -> str:
    lineas = [
        f"# {clip['title']}",
        "",
        f"- **Curso:** {curso['name']}",
        f"- **Escena:** `{clip['scene']}`",
        f"- **Duración del video:** "
        + (f"{video_s:.1f} s" if video_s else "sin render"),
        f"- **Voz:** {voz} ({model_tts})",
        f"- **Palabras:** {len(narracion.split())}",
        "",
        "## Guion por secciones",
        "",
        "| Tiempo | Momento visual | Narración |",
        "|---|---|---|",
    ]
    for s in secciones:
        texto = s["texto"].replace("|", "\\|").replace("\n", " ")
        momento = s["momento"].replace("|", "\\|")
        lineas.append(f"| {s['t_inicio']:.0f}–{s['t_fin']:.0f} s "
                      f"| {momento} | {texto} |")
    lineas += ["", "## Narración completa", "", narracion, ""]
    return "\n".join(lineas)


def _escribir_wav(pcm: bytes, wav_path: Path) -> float:
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TTS_RATE)
        w.writeframes(pcm)
    return len(pcm) / 2 / TTS_RATE


def _pcm_agrupado(vertex: VertexNarrador, secciones: list[dict],
                  voz: str) -> bytes:
    """Secciones agrupadas hasta TTS_MAX_CHARS con una pausa breve entre
    trozos (sin tiempos: narracion continua)."""
    trozos: list[str] = []
    actual = ""
    for s in secciones:
        candidato = (actual + "\n\n" + s["texto"]).strip()
        if actual and len(candidato) > TTS_MAX_CHARS:
            trozos.append(actual)
            actual = s["texto"]
        else:
            actual = candidato
    if actual:
        trozos.append(actual)

    pausa = b"\x00\x00" * int(TTS_RATE * PAUSA_ENTRE_TROZOS_S)
    pcm = b""
    for i, trozo in enumerate(trozos):
        if i:
            pcm += pausa
        pcm += _recortar_silencio(vertex.tts(trozo, voz))
    return pcm


def _recortar_silencio(audio: bytes) -> bytes:
    """Quita el silencio inicial/final que mete el TTS en cada llamada
    (conservando un margen breve): sin esto, narrar por secciones acumula
    varios segundos muertos y el audio se pasa del video."""
    n = len(audio) // 2
    muestras = struct.unpack(f"<{n}h", audio[:n * 2])
    ini, fin = 0, n
    while ini < n and abs(muestras[ini]) < UMBRAL_SILENCIO:
        ini += 1
    while fin > ini and abs(muestras[fin - 1]) < UMBRAL_SILENCIO:
        fin -= 1
    margen = int(TTS_RATE * MARGEN_SILENCIO_S)
    ini, fin = max(0, ini - margen), min(n, fin + margen)
    return audio[ini * 2:fin * 2]


def _pcm_alineado(vertex: VertexNarrador, secciones: list[dict],
                  voz: str) -> bytes:
    """Cada seccion se sintetiza aparte (con su silencio recortado) y se
    coloca en su t_inicio: la voz cae sobre el momento visual que comenta.
    El hueco insertado se acota a MAX_HUECO_S (los tiempos del guion son
    estimados) y si una seccion se pasa de largo, la siguiente cede hacia
    adelante (con la pausa minima) en cascada."""
    pausa_min = int(TTS_RATE * PAUSA_ENTRE_TROZOS_S)
    hueco_max = int(TTS_RATE * MAX_HUECO_S)
    pcm = bytearray()
    cursor = 0  # muestras escritas
    for i, s in enumerate(secciones):
        audio = _recortar_silencio(vertex.tts(s["texto"], voz))
        offset = int(float(s["t_inicio"]) * TTS_RATE)
        if i:
            offset = max(min(offset, cursor + hueco_max), cursor + pausa_min)
        else:
            offset = min(offset, hueco_max)
        pcm.extend(b"\x00\x00" * max(0, offset - cursor))
        pcm.extend(audio)
        cursor = offset + len(audio) // 2
    return bytes(pcm)


def sintetizar(vertex: VertexNarrador, secciones: list[dict], voz: str,
               wav_path: Path) -> float:
    """TTS a WAV. Con tiempos por seccion (t_inicio) el audio se alinea a los
    momentos visuales del guion; sin tiempos se narra de corrido. Devuelve la
    duracion del audio en segundos."""
    alineable = (len(secciones) > 1
                 and all(isinstance(s.get("t_inicio"), (int, float))
                         for s in secciones))
    pcm = (_pcm_alineado(vertex, secciones, voz) if alineable
           else _pcm_agrupado(vertex, secciones, voz))
    return _escribir_wav(pcm, wav_path)


def generar_clip(vertex: VertexNarrador, curso: dict, clip: dict,
                 compuesto: str, video_s: float | None, voz: str,
                 destino: Path, etiqueta: str, solo_guion: bool = False,
                 log=print) -> dict:
    """Genera guion (+ audio) de UN clip y escribe md/txt/wav en `destino`.
    Devuelve la entrada para estado.json. Bloqueante (Vertex)."""
    md_path = destino / f"{etiqueta}.md"
    txt_path = destino / f"{etiqueta}.txt"
    wav_path = destino / f"{etiqueta}.wav"

    max_palabras = (int(video_s * PALABRAS_POR_SEGUNDO * MARGEN)
                    if video_s else MAX_PALABRAS_SIN_RENDER)
    log(f"[{etiqueta}] guion… (video "
        + (f"{video_s:.0f} s, tope {max_palabras} palabras)"
           if video_s else f"sin render, tope {MAX_PALABRAS_SIN_RENDER} palabras)"))
    system, user = prompt_guion(curso, clip, compuesto, video_s, max_palabras)
    data = vertex.guion(system, user)
    secciones = data["secciones"]
    narracion = "\n\n".join(s["texto"].strip() for s in secciones)

    audio_s = None
    if not solo_guion:
        log(f"[{etiqueta}] narrando con {voz}…")
        audio_s = sintetizar(vertex, secciones, voz, wav_path)
        if video_s and audio_s > video_s * TOLERANCIA_AUDIO:
            log(f"[{etiqueta}] audio {audio_s:.0f} s > video "
                f"{video_s:.0f} s: reintento con guion más corto…")
            system, user = prompt_guion(
                curso, clip, compuesto, video_s,
                int(max_palabras * video_s / audio_s * 0.95))
            data = vertex.guion(system, user)
            secciones = data["secciones"]
            narracion = "\n\n".join(s["texto"].strip() for s in secciones)
            audio_s = sintetizar(vertex, secciones, voz, wav_path)
            if audio_s > video_s * TOLERANCIA_AUDIO:
                log(f"[{etiqueta}] AVISO: el audio ({audio_s:.0f} s) "
                    "sigue más largo que el video; revisar en montaje.")

    md_path.write_text(render_md(curso, clip, secciones, narracion,
                                 video_s, voz, vertex.model_tts))
    txt_path.write_text(narracion + "\n")
    # Secciones con tiempos: permiten re-sintetizar el audio alineado sin
    # volver a generar el guion (CLI --solo-audio).
    (destino / f"{etiqueta}.secciones.json").write_text(
        json.dumps(secciones, ensure_ascii=False, indent=2))
    return {
        "hash": hash_guion(compuesto, clip["scene"] or "", video_s, voz),
        "etiqueta": etiqueta, "voz": voz,
        "video_s": round(video_s, 1) if video_s else None,
        "audio_s": round(audio_s, 1) if audio_s else None,
        "palabras": len(narracion.split()),
        "generado": time.time(),
    }


# ── servicio (backend) ───────────────────────────────────────────────────────

class NarracionService:
    """Estado y generacion de narraciones desde la API.

    Una sola generacion en curso a la vez (app de sesion unica y una sola
    cuota de Vertex): `start` devuelve 409 via ValueError si ya hay una.
    El progreso vive en memoria (`run_public`); el resultado durable es
    estado.json + los archivos, asi que un reinicio a mitad solo pierde el
    progreso visual, no el trabajo ya escrito.
    """

    def __init__(self, cfg, db) -> None:
        self.cfg = cfg
        self.db = db
        self._run: dict | None = None
        self._cancel = False
        self._task: asyncio.Task | None = None
        # Cache de duraciones de mp4 (leer el mvhd carga el archivo entero;
        # sin cache cada poll de estado releeria todos los videos del curso).
        self._dur_cache: dict[str, tuple[float, float | None]] = {}

    @property
    def enabled(self) -> bool:
        return self.cfg.gcp_key_path.is_file()

    @property
    def running(self) -> bool:
        return self._run is not None and not self._run.get("finished")

    # ── consulta ─────────────────────────────────────────────────────────

    def destino(self, project: dict) -> Path:
        return self.cfg.guiones_dir / slugify(project["name"])

    def _leer_estado(self, destino: Path) -> dict:
        p = destino / "estado.json"
        try:
            return json.loads(p.read_text()) if p.is_file() else {}
        except (OSError, ValueError):
            return {}

    def _video_s(self, clip: dict) -> float | None:
        job = self.db.get_job(clip["job_id"]) if clip.get("job_id") else None
        if not job or job.get("status") != "done" or not job.get("video_path"):
            return None
        path = Path(job["video_path"])
        try:
            mtime = path.stat().st_mtime
        except OSError:
            return None
        cached = self._dur_cache.get(str(path))
        if cached and cached[0] == mtime:
            return cached[1]
        dur = duracion_mp4(path)
        self._dur_cache[str(path)] = (mtime, dur)
        return dur

    def estado_proyecto(self, project: dict) -> dict:
        """Estado de narracion por clip + progreso de la corrida en curso."""
        destino = self.destino(project)
        estado = self._leer_estado(destino)
        voz = self.cfg.tts_voice
        clips_out = []
        for clip in self.db.list_clips(project["id"]):
            compuesto = compose_script(project["style_block"],
                                       clip.get("script") or "")
            video_s = self._video_s(clip)
            h = hash_guion(compuesto, clip.get("scene") or "", video_s, voz)
            previo = estado.get(clip["id"]) or {}
            etiqueta = previo.get("etiqueta") or etiqueta_clip(
                clip["position"], clip["title"])
            has_texto = (destino / f"{etiqueta}.md").is_file()
            has_audio = (destino / f"{etiqueta}.wav").is_file()
            if not previo or not has_texto:
                st = "sin_narracion"
            elif previo.get("hash") != h or not has_audio:
                st = "desactualizada"
            else:
                st = "al_dia"
            audio_s = previo.get("audio_s")
            clips_out.append({
                "clip_id": clip["id"], "position": clip["position"],
                "title": clip["title"], "etiqueta": etiqueta, "estado": st,
                "video_s": video_s and round(video_s, 1),
                "audio_s": audio_s, "palabras": previo.get("palabras"),
                "voz": previo.get("voz"), "generado": previo.get("generado"),
                "has_texto": has_texto, "has_audio": has_audio,
                "aviso_largo": bool(video_s and audio_s
                                    and audio_s > video_s * TOLERANCIA_AUDIO),
            })
        return {"enabled": self.enabled, "voz": voz, "clips": clips_out,
                "run": self.run_public()}

    def run_public(self) -> dict | None:
        if self._run is None:
            return None
        r = self._run
        return {k: r[k] for k in ("project_id", "total", "done", "current",
                                  "errores", "started", "finished")}

    # ── generacion ───────────────────────────────────────────────────────

    def _plan(self, project: dict, clip_ids: list[str] | None,
              force: bool) -> list[dict]:
        """Trabajo por clip, resuelto ANTES de lanzar el thread (la DB y los
        mp4 se consultan aqui; el thread solo habla con Vertex y el disco)."""
        estado = self._leer_estado(self.destino(project))
        voz = self.cfg.tts_voice
        plan = []
        for clip in self.db.list_clips(project["id"]):
            if clip_ids is not None and clip["id"] not in clip_ids:
                continue
            compuesto = compose_script(project["style_block"],
                                       clip.get("script") or "")
            video_s = self._video_s(clip)
            h = hash_guion(compuesto, clip.get("scene") or "", video_s, voz)
            etiqueta = etiqueta_clip(clip["position"], clip["title"])
            previo = estado.get(clip["id"]) or {}
            destino = self.destino(project)
            al_dia = (previo.get("hash") == h
                      and (destino / f"{etiqueta}.md").is_file()
                      and (destino / f"{etiqueta}.wav").is_file())
            if al_dia and not force:
                continue
            plan.append({"clip": clip, "compuesto": compuesto,
                         "video_s": video_s, "etiqueta": etiqueta})
        return plan

    def start(self, project: dict, clip_ids: list[str] | None = None,
              force: bool = False) -> dict:
        """Lanza la generacion en segundo plano. ValueError si ya hay una
        corrida activa o si Vertex no esta configurado."""
        if not self.enabled:
            raise ValueError("Narracion no disponible: falta la service "
                             "account de Vertex AI")
        if self.running:
            raise ValueError("Ya hay una narracion en curso")
        plan = self._plan(project, clip_ids, force)
        if not plan:
            return {"queued": []}
        self._cancel = False
        self._run = {"project_id": project["id"], "total": len(plan),
                     "done": 0, "current": None, "errores": [],
                     "started": time.time(), "finished": False}
        curso = {"name": project["name"], "description": project["description"],
                 "total_clips": len(self.db.list_clips(project["id"]))}
        destino = self.destino(project)
        self._task = asyncio.get_running_loop().create_task(
            self._correr(plan, curso, destino))
        return {"queued": [item["clip"]["id"] for item in plan]}

    def cancel(self) -> bool:
        if not self.running:
            return False
        self._cancel = True
        return True

    async def _correr(self, plan: list[dict], curso: dict,
                      destino: Path) -> None:
        try:
            await asyncio.to_thread(self._generar, plan, curso, destino)
        except Exception as e:  # fallo de setup (p.ej. credenciales rotas)
            self._run["errores"].append({"clip_id": None,
                                         "error": f"{type(e).__name__}: {e}"})
        finally:
            self._run["current"] = None
            self._run["finished"] = True

    def _generar(self, plan: list[dict], curso: dict, destino: Path) -> None:
        """Cuerpo bloqueante (corre en thread): un clip tras otro, escribiendo
        estado.json tras cada uno para que un corte a mitad no pierda nada."""
        destino.mkdir(parents=True, exist_ok=True)
        vertex = self._vertex()
        voz = self.cfg.tts_voice
        estado_path = destino / "estado.json"
        for item in plan:
            if self._cancel:
                break
            clip = item["clip"]
            self._run["current"] = {"clip_id": clip["id"],
                                    "etiqueta": item["etiqueta"]}
            try:
                entry = generar_clip(vertex, curso, clip, item["compuesto"],
                                     item["video_s"], voz, destino,
                                     item["etiqueta"], log=lambda _m: None)
            except Exception as e:
                self._run["errores"].append(
                    {"clip_id": clip["id"],
                     "error": f"{type(e).__name__}: {e}"})
                continue
            estado = self._leer_estado(destino)
            estado[clip["id"]] = entry
            estado_path.write_text(json.dumps(estado, indent=2))
            self._run["done"] += 1

    def _vertex(self) -> VertexNarrador:
        return VertexNarrador(self.cfg.gcp_key_path, self.cfg.gcp_location,
                              self.cfg.gemini_model_deep,
                              self.cfg.gemini_model_tts)

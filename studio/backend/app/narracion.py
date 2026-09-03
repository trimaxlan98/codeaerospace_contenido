"""Narracion de clips: guion cronometrado + voz.

Logica compartida entre el CLI (studio/tools/guiones.py) y el endpoint
"Generar narracion" de Proyectos. La salida vive en <workspace>/guiones/
<slug-proyecto>/ (md + txt + wav + secciones.json + estado.json), fuera de
render_jobs/ y de la cola de render: narrar no encola jobs ni toca los
videos.

La voz la pone un PROVEEDOR (app/tts.py): Vertex (Gemini TTS, el original),
edge-tts (gratis, red desde el backend), Piper (offline) o una grabacion
propia subida por el dueno. El guion lo escribe Gemini si hay credenciales;
si no, se escribe a mano (PUT .../guion) y el proveedor solo lo habla.
Desde 2026-09-03 la app no depende de GCP para tener voz.
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

from . import tts as tts_mod
from .projects import compose_script
from .tts import (GUION_SCHEMA, INSTRUCCION_TTS, TTS_RATE,  # noqa: F401
                  VertexNarrador)

# Narracion en español pausada: ~2.2 palabras/s, y solo se apunta al 90 %
# de la duracion del video para dejar aire entre secciones.
PALABRAS_POR_SEGUNDO = 2.2
MARGEN = 0.9
MAX_PALABRAS_SIN_RENDER = 160
TTS_MAX_CHARS = 3_000  # por llamada; las secciones se agrupan hasta este tope
PAUSA_ENTRE_TROZOS_S = 0.35
# El audio puede exceder el video hasta este factor antes de reintentar con
# un presupuesto de palabras mas corto.
TOLERANCIA_AUDIO = 1.05
# Intentos de guion (el primero + reintentos mas cortos) cuando el audio no
# cabe. Se conserva el intento que mejor encaja, no el ultimo: el TTS varia
# entre corridas y un reintento puede salir peor que el original.
MAX_INTENTOS_GUION = 3
# Alineado por secciones: silencio maximo insertado entre secciones (los
# t_inicio del guion son estimados; huecos mas largos son casi siempre un
# error de estimacion y desincronizan el final).
MAX_HUECO_S = 2.5
# Recorte de silencio del TTS: umbral de amplitud (int16) y margen conservado.
UMBRAL_SILENCIO = 300
MARGEN_SILENCIO_S = 0.12

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


def _pcm_agrupado(vertex, secciones: list[dict],
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


def _ensamblar(secciones: list[dict], audios: list[bytes],
               holgura: float = 1.0, hueco_max_s: float = MAX_HUECO_S) -> bytes:
    """Coloca cada seccion en su t_inicio: la voz cae sobre el momento visual
    que comenta. El hueco insertado se acota a MAX_HUECO_S (los tiempos del
    guion son estimados) y si una seccion se pasa de largo, la siguiente cede
    hacia adelante (con la pausa minima) en cascada.

    `holgura` escala los silencios que se insertan (1.0 = tiempos tal cual,
    0.0 = secciones pegadas una tras otra, el minimo posible). `hueco_max_s`
    es el tope del silencio insertado: 2.5 s para un guion ESTIMADO por
    Gemini; para uno escrito a mano los tiempos son deliberados (huecos de
    4-7 s en un vertical) y el tope se levanta (`exacto`)."""
    pausa_min = int(TTS_RATE * PAUSA_ENTRE_TROZOS_S * holgura)
    hueco_max = int(TTS_RATE * hueco_max_s * holgura)
    pcm = bytearray()
    cursor = 0  # muestras escritas
    for i, (s, audio) in enumerate(zip(secciones, audios)):
        offset = int(float(s["t_inicio"]) * TTS_RATE)
        if i:
            offset = max(min(offset, cursor + hueco_max), cursor + pausa_min)
        else:
            offset = min(offset, hueco_max)
        pcm.extend(b"\x00\x00" * max(0, offset - cursor))
        pcm.extend(audio)
        cursor = offset + len(audio) // 2
    return bytes(pcm)


def _ajustar_al_limite(secciones: list[dict], audios: list[bytes],
                       limite_s: float, hueco_max_s: float = MAX_HUECO_S) -> bytes:
    """Mayor holgura entre secciones que aun cabe en `limite_s` (busqueda
    binaria). Recortar silencio no toca la voz, asi que es lo primero que se
    sacrifica antes de pedir un guion mas corto."""
    limite = int(limite_s * TTS_RATE)
    minimo = _ensamblar(secciones, audios, 0.0, hueco_max_s)
    if len(minimo) // 2 > limite:
        return minimo  # ni pegadas caben: lo resuelve el reintento de guion
    lo, hi, mejor = 0.0, 1.0, minimo
    for _ in range(8):
        mid = (lo + hi) / 2
        pcm = _ensamblar(secciones, audios, mid, hueco_max_s)
        if len(pcm) // 2 <= limite:
            mejor, lo = pcm, mid
        else:
            hi = mid
    return mejor


def _pcm_alineado(vertex, secciones: list[dict], voz: str,
                  limite_s: float | None = None, exacto: bool = False) -> bytes:
    """Cada seccion se sintetiza aparte (con su silencio recortado) y se
    ensambla sobre los tiempos del guion, comprimiendo los silencios si hace
    falta para no pasarse de `limite_s`. Con `exacto` los t_inicio se
    respetan sin tope de hueco (guion escrito a mano)."""
    audios = [_recortar_silencio(vertex.tts(s["texto"], voz))
              for s in secciones]
    hueco = 1e9 if exacto else MAX_HUECO_S
    pcm = _ensamblar(secciones, audios, 1.0, hueco)
    if limite_s and len(pcm) // 2 > limite_s * TTS_RATE:
        pcm = _ajustar_al_limite(secciones, audios, limite_s, hueco)
    return pcm


def sintetizar(vertex, secciones: list[dict], voz: str,
               wav_path: Path, limite_s: float | None = None,
               exacto: bool = False) -> float:
    """TTS a WAV. Con tiempos por seccion (t_inicio) el audio se alinea a los
    momentos visuales del guion; sin tiempos se narra de corrido. Devuelve la
    duracion del audio en segundos."""
    alineable = (len(secciones) > 1
                 and all(isinstance(s.get("t_inicio"), (int, float))
                         for s in secciones))
    pcm = (_pcm_alineado(vertex, secciones, voz, limite_s, exacto) if alineable
           else _pcm_agrupado(vertex, secciones, voz))
    return _escribir_wav(pcm, wav_path)


def _mejor_intento(candidato: float, actual: float | None,
                   limite: float | None) -> bool:
    """¿El intento `candidato` encaja mejor que `actual`? Caber en el video
    manda; entre los que caben gana el mas largo (mas contenido narrado) y
    entre los que no, el que menos se pasa."""
    if actual is None:
        return True
    if limite is None:
        return False
    cabe, cabia = candidato <= limite, actual <= limite
    if cabe != cabia:
        return cabe
    return candidato > actual if cabe else candidato < actual


def validar_secciones(secciones) -> list[dict]:
    """Guion escrito a mano (PUT .../guion): misma forma que el de Gemini.
    Devuelve las secciones normalizadas o lanza ValueError legible."""
    if not isinstance(secciones, list) or not secciones:
        raise ValueError("el guion necesita al menos una seccion")
    if len(secciones) > 200:
        raise ValueError("demasiadas secciones (tope 200)")
    out = []
    t_prev = -1.0
    for i, s in enumerate(secciones, 1):
        if not isinstance(s, dict):
            raise ValueError(f"seccion {i}: no es un objeto")
        texto = str(s.get("texto") or "").strip()
        if not texto:
            raise ValueError(f"seccion {i}: texto vacio")
        if len(texto) > 2000:
            raise ValueError(f"seccion {i}: texto demasiado largo (tope 2000)")
        try:
            t0 = float(s.get("t_inicio", 0))
        except (TypeError, ValueError):
            raise ValueError(f"seccion {i}: t_inicio no es un numero")
        if t0 < 0 or t0 > 7200:
            raise ValueError(f"seccion {i}: t_inicio fuera de rango")
        if t0 < t_prev:
            raise ValueError(f"seccion {i}: t_inicio retrocede")
        t_prev = t0
        try:
            t1 = float(s.get("t_fin", t0))
        except (TypeError, ValueError):
            raise ValueError(f"seccion {i}: t_fin no es un numero")
        if t1 < t0:
            t1 = t0
        out.append({"t_inicio": round(t0, 2), "t_fin": round(t1, 2),
                    "momento": str(s.get("momento") or "")[:120],
                    "texto": texto})
    return out


def generar_clip(narrador, curso: dict, clip: dict,
                 compuesto: str, video_s: float | None, voz: str,
                 destino: Path, etiqueta: str, solo_guion: bool = False,
                 log=print, secciones: list[dict] | None = None,
                 guionista=None) -> dict:
    """Genera guion (+ audio) de UN clip y escribe md/txt/wav en `destino`.
    Devuelve la entrada para estado.json. Bloqueante (red o subproceso).

    `narrador` pone la voz (cualquier proveedor de tts.py). El guion lo
    escribe `guionista` (Vertex) si se pasa; si no, tiene que venir ya en
    `secciones` (escrito a mano) y entonces no se reintenta con un guion mas
    corto: solo se comprimen los silencios para que quepa.
    """
    md_path = destino / f"{etiqueta}.md"
    txt_path = destino / f"{etiqueta}.txt"
    wav_path = destino / f"{etiqueta}.wav"

    if guionista is None and secciones is None \
            and getattr(narrador, "id", "vertex") == "vertex":
        guionista = narrador

    max_palabras = (int(video_s * PALABRAS_POR_SEGUNDO * MARGEN)
                    if video_s else MAX_PALABRAS_SIN_RENDER)
    if secciones is None:
        if guionista is None:
            raise RuntimeError(
                "no hay guion para este clip y el proveedor de voz no lo "
                "escribe: escribelo en la app (Guion) o configura Vertex")
        log(f"[{etiqueta}] guion… (video "
            + (f"{video_s:.0f} s, tope {max_palabras} palabras)"
               if video_s else f"sin render, tope {MAX_PALABRAS_SIN_RENDER} palabras)"))
        system, user = prompt_guion(curso, clip, compuesto, video_s, max_palabras)
        data = guionista.guion(system, user)
        secciones = data["secciones"]
        puede_reescribir = True
    else:
        secciones = validar_secciones(secciones)
        puede_reescribir = False
    narracion = "\n\n".join(s["texto"].strip() for s in secciones)

    audio_s = None
    if not solo_guion:
        limite = video_s * TOLERANCIA_AUDIO if video_s else None
        tmp = destino / f"{etiqueta}.intento.wav"
        mejor: dict | None = None
        for intento in range(1, MAX_INTENTOS_GUION + 1):
            log(f"[{etiqueta}] narrando con {voz}…"
                + (f" (intento {intento})" if intento > 1 else ""))
            audio_s = sintetizar(narrador, secciones, voz, tmp, limite,
                                 exacto=not puede_reescribir)
            if _mejor_intento(audio_s, mejor and mejor["audio_s"], limite):
                mejor = {"audio_s": audio_s, "secciones": secciones,
                         "narracion": narracion}
                tmp.replace(wav_path)
            if limite is None or audio_s <= limite \
                    or intento == MAX_INTENTOS_GUION or not puede_reescribir:
                break
            # Aun no cabe: guion mas corto en proporcion a lo que se paso.
            log(f"[{etiqueta}] audio {audio_s:.0f} s > video "
                f"{video_s:.0f} s: reintento con guion más corto…")
            max_palabras = max(20, int(max_palabras * video_s / audio_s * .95))
            system, user = prompt_guion(curso, clip, compuesto, video_s,
                                        max_palabras)
            data = guionista.guion(system, user)
            secciones = data["secciones"]
            narracion = "\n\n".join(s["texto"].strip() for s in secciones)
        tmp.unlink(missing_ok=True)
        # El mejor intento manda: el ultimo puede haber salido peor.
        audio_s = mejor["audio_s"]
        secciones, narracion = mejor["secciones"], mejor["narracion"]
        if limite and audio_s > limite:
            log(f"[{etiqueta}] AVISO: el audio ({audio_s:.0f} s) sigue más "
                f"largo que el video ({video_s:.0f} s); mux.sh lo ajusta "
                "con atempo al montar.")

    model_tts = getattr(narrador, "model_tts", "tts")
    md_path.write_text(render_md(curso, clip, secciones, narracion,
                                 video_s, voz, model_tts))
    txt_path.write_text(narracion + "\n")
    # Secciones con tiempos: permiten re-sintetizar el audio alineado sin
    # volver a generar el guion (CLI --solo-audio, o cambiar de voz).
    (destino / f"{etiqueta}.secciones.json").write_text(
        json.dumps(secciones, ensure_ascii=False, indent=2))
    return {
        "hash": hash_guion(compuesto, clip["scene"] or "", video_s, voz),
        "etiqueta": etiqueta, "voz": voz,
        "proveedor": getattr(narrador, "id", "vertex"),
        "origen": "tts",
        "video_s": round(video_s, 1) if video_s else None,
        "audio_s": round(audio_s, 1) if audio_s else None,
        "palabras": len(narracion.split()),
        "generado": time.time(),
    }


# ── servicio (backend) ───────────────────────────────────────────────────────

class NarracionService:
    """Estado y generacion de narraciones desde la API.

    Una sola generacion en curso a la vez (app de sesion unica): `start`
    devuelve 409 via ValueError si ya hay una. El progreso vive en memoria
    (`run_public`); el resultado durable es estado.json + los archivos, asi
    que un reinicio a mitad solo pierde el progreso visual, no el trabajo ya
    escrito.
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
        """Hay al menos un proveedor que SINTETIZA (la grabacion propia
        siempre esta, pero no cuenta: no genera nada sola)."""
        return tts_mod.proveedor_defecto(self.cfg) is not None

    @property
    def running(self) -> bool:
        return self._run is not None and not self._run.get("finished")

    def proveedores(self) -> list[dict]:
        return tts_mod.catalogo(self.cfg)

    def proveedor_defecto(self) -> str | None:
        return tts_mod.proveedor_defecto(self.cfg)

    def voz_defecto(self, proveedor: str | None = None) -> str:
        proveedor = proveedor or self.proveedor_defecto()
        return tts_mod.voz_defecto(self.cfg, proveedor) if proveedor else ""

    def resolver_voz(self, proveedor: str | None, voz: str | None) -> tuple[str, str]:
        """(proveedor, voz) validados contra el catalogo. ValueError si el
        proveedor no esta disponible o la voz no es suya."""
        proveedor = proveedor or self.proveedor_defecto()
        if not proveedor:
            raise ValueError("Narracion no disponible: ningun proveedor de "
                             "voz instalado (edge-tts, piper o Vertex)")
        cat = {p["id"]: p for p in self.proveedores()}
        p = cat.get(proveedor)
        if not p:
            raise ValueError(f"proveedor de voz desconocido: {proveedor}")
        if not p["disponible"]:
            raise ValueError(f"proveedor {proveedor} no disponible: "
                             f"{p['motivo'] or 'desactivado'}")
        voz = voz or p["voz_defecto"] or ""
        if p["voces"] and voz not in {v["id"] for v in p["voces"]}:
            raise ValueError(f"la voz {voz!r} no es de {proveedor}")
        return proveedor, voz

    # ── consulta ─────────────────────────────────────────────────────────

    def destino(self, project: dict) -> Path:
        return self.cfg.guiones_dir / slugify(project["name"])

    def _leer_estado(self, destino: Path) -> dict:
        p = destino / "estado.json"
        try:
            return json.loads(p.read_text()) if p.is_file() else {}
        except (OSError, ValueError):
            return {}

    def _escribir_estado(self, destino: Path, clip_id: str, entry: dict) -> None:
        destino.mkdir(parents=True, exist_ok=True)
        estado = self._leer_estado(destino)
        estado[clip_id] = entry
        (destino / "estado.json").write_text(json.dumps(estado, indent=2))

    def resumen_audio(self, project: dict, clips: list[dict]) -> dict:
        """Cuantos clips ya tienen audio, sin abrir un solo mp4.

        `estado_proyecto` no sirve para el indice de cursos: para decidir si
        una narracion esta *desactualizada* necesita la duracion del video, y
        `duracion_mp4` lee el archivo entero. Con ~60 cursos y ~300 clips eso
        seria cargar cientos de MB en cada `GET /api/projects`. Aqui solo se
        hace un `stat` por clip, que es lo justo para responder "que falta
        narrar" desde la lista.
        """
        destino = self.destino(project)
        estado = self._leer_estado(destino)
        con_audio = 0
        for clip in clips:
            previo = estado.get(clip["id"]) or {}
            etiqueta = previo.get("etiqueta") or etiqueta_clip(
                clip["position"], clip["title"])
            if (destino / f"{etiqueta}.wav").is_file():
                con_audio += 1
        return {"narrated_count": con_audio}

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

    def _hash_vigente(self, project: dict, clip: dict, previo: dict,
                      video_s: float | None, voz: str | None = None) -> str:
        """El hash que tendria la narracion de este clip HOY. La voz que
        entra en el hash es la de la narracion existente (cambiar el
        proveedor por defecto no deja desactualizado todo el catalogo);
        `voz` la fuerza cuando se va a generar con otra."""
        compuesto = compose_script(project["style_block"],
                                   clip.get("script") or "")
        v = voz or previo.get("voz") or self.voz_defecto()
        return hash_guion(compuesto, clip.get("scene") or "", video_s, v)

    def estado_proyecto(self, project: dict) -> dict:
        """Estado de narracion por clip + progreso de la corrida en curso."""
        destino = self.destino(project)
        estado = self._leer_estado(destino)
        proveedor = self.proveedor_defecto()
        clips_out = []
        for clip in self.db.list_clips(project["id"]):
            video_s = self._video_s(clip)
            previo = estado.get(clip["id"]) or {}
            h = self._hash_vigente(project, clip, previo, video_s)
            etiqueta = previo.get("etiqueta") or etiqueta_clip(
                clip["position"], clip["title"])
            has_texto = (destino / f"{etiqueta}.md").is_file()
            has_guion = (destino / f"{etiqueta}.secciones.json").is_file()
            has_audio = (destino / f"{etiqueta}.wav").is_file()
            if not previo and not has_guion:
                st = "sin_narracion"
            elif not has_audio:
                st = "guion" if has_guion else "sin_narracion"
            elif previo.get("hash") != h:
                st = "desactualizada"
            else:
                st = "al_dia"
            audio_s = previo.get("audio_s")
            clips_out.append({
                "clip_id": clip["id"], "position": clip["position"],
                "title": clip["title"], "etiqueta": etiqueta, "estado": st,
                "video_s": video_s and round(video_s, 1),
                "audio_s": audio_s, "palabras": previo.get("palabras"),
                "voz": previo.get("voz"), "proveedor": previo.get("proveedor"),
                "origen": previo.get("origen"),
                "generado": previo.get("generado"),
                "has_texto": has_texto, "has_audio": has_audio,
                "has_guion": has_guion,
                "aviso_largo": bool(video_s and audio_s
                                    and audio_s > video_s * TOLERANCIA_AUDIO),
            })
        return {"enabled": self.enabled, "proveedor": proveedor,
                "voz": self.voz_defecto(proveedor) if proveedor else None,
                "proveedores": self.proveedores(),
                "escribe_guion": any(p["escribe_guion"]
                                     for p in self.proveedores()),
                "clips": clips_out, "run": self.run_public()}

    def run_public(self) -> dict | None:
        if self._run is None:
            return None
        r = self._run
        return {k: r.get(k) for k in ("project_id", "total", "done", "current",
                                      "errores", "started", "finished",
                                      "proveedor", "voz")}

    # ── guion escrito a mano ─────────────────────────────────────────────

    def _etiqueta(self, project: dict, clip: dict) -> str:
        previo = self._leer_estado(self.destino(project)).get(clip["id"]) or {}
        return previo.get("etiqueta") or etiqueta_clip(clip["position"],
                                                      clip["title"])

    def leer_guion(self, project: dict, clip: dict) -> list[dict] | None:
        p = self.destino(project) / f"{self._etiqueta(project, clip)}.secciones.json"
        try:
            return json.loads(p.read_text()) if p.is_file() else None
        except (OSError, ValueError):
            return None

    def guardar_guion(self, project: dict, clip: dict, secciones) -> dict:
        """Escribe el guion (secciones.json + txt + md) sin sintetizar. Si
        habia audio, queda `desactualizada`: el hash se vacia."""
        secciones = validar_secciones(secciones)
        destino = self.destino(project)
        destino.mkdir(parents=True, exist_ok=True)
        etiqueta = self._etiqueta(project, clip)
        previo = self._leer_estado(destino).get(clip["id"]) or {}
        narracion = "\n\n".join(s["texto"] for s in secciones)
        video_s = self._video_s(clip)
        curso = {"name": project["name"]}
        (destino / f"{etiqueta}.secciones.json").write_text(
            json.dumps(secciones, ensure_ascii=False, indent=2))
        (destino / f"{etiqueta}.txt").write_text(narracion + "\n")
        (destino / f"{etiqueta}.md").write_text(render_md(
            curso, clip, secciones, narracion, video_s,
            previo.get("voz") or "—", "guion escrito a mano"))
        entry = dict(previo)
        entry.update({"hash": "", "etiqueta": etiqueta,
                      "palabras": len(narracion.split()),
                      "guion_editado": time.time()})
        self._escribir_estado(destino, clip["id"], entry)
        return entry

    # ── grabacion propia ─────────────────────────────────────────────────

    def registrar_subida(self, project: dict, clip: dict, pcm: bytes,
                         nombre: str = "") -> dict:
        """Deja una grabacion del dueno como LA narracion del clip: PCM ya
        decodificado a TTS_RATE, silencio recortado, en la ruta canonica
        (la misma que produce el TTS), asi `pelicula.plan` la recoge sin
        saber de donde salio."""
        if len(pcm) < TTS_RATE:  # menos de medio segundo
            raise ValueError("la grabacion es demasiado corta o vacia")
        pcm = _recortar_silencio(pcm)
        destino = self.destino(project)
        destino.mkdir(parents=True, exist_ok=True)
        etiqueta = self._etiqueta(project, clip)
        audio_s = _escribir_wav(pcm, destino / f"{etiqueta}.wav")
        video_s = self._video_s(clip)
        previo = self._leer_estado(destino).get(clip["id"]) or {}
        if not (destino / f"{etiqueta}.md").is_file():
            (destino / f"{etiqueta}.md").write_text(
                f"# {clip['title']}\n\n- **Curso:** {project['name']}\n"
                f"- **Voz:** grabacion propia ({nombre or 'archivo'})\n"
                f"- **Duracion del audio:** {audio_s:.1f} s\n")
        entry = {
            "hash": self._hash_vigente(project, clip, {}, video_s, "propia"),
            "etiqueta": etiqueta, "voz": "propia", "proveedor": "archivo",
            "origen": "subido", "archivo": nombre[:120],
            "video_s": round(video_s, 1) if video_s else None,
            "audio_s": round(audio_s, 1),
            "palabras": previo.get("palabras"),
            "generado": time.time(),
        }
        self._escribir_estado(destino, clip["id"], entry)
        return entry

    # ── generacion ───────────────────────────────────────────────────────

    def _plan(self, project: dict, clip_ids: list[str] | None,
              force: bool, voz: str) -> list[dict]:
        """Trabajo por clip, resuelto ANTES de lanzar el thread (la DB y los
        mp4 se consultan aqui; el thread solo habla con el proveedor y el
        disco)."""
        destino = self.destino(project)
        estado = self._leer_estado(destino)
        plan = []
        for clip in self.db.list_clips(project["id"]):
            if clip_ids is not None and clip["id"] not in clip_ids:
                continue
            compuesto = compose_script(project["style_block"],
                                       clip.get("script") or "")
            video_s = self._video_s(clip)
            previo = estado.get(clip["id"]) or {}
            h = self._hash_vigente(project, clip, previo, video_s, voz)
            etiqueta = etiqueta_clip(clip["position"], clip["title"])
            al_dia = (previo.get("hash") == h
                      and (destino / f"{etiqueta}.md").is_file()
                      and (destino / f"{etiqueta}.wav").is_file())
            if al_dia and not force:
                continue
            sec_path = destino / f"{etiqueta}.secciones.json"
            secciones = None
            if sec_path.is_file():
                try:
                    secciones = json.loads(sec_path.read_text())
                except (OSError, ValueError):
                    secciones = None
            plan.append({"clip": clip, "compuesto": compuesto,
                         "video_s": video_s, "etiqueta": etiqueta,
                         "secciones": secciones})
        return plan

    def start(self, project: dict, clip_ids: list[str] | None = None,
              force: bool = False, proveedor: str | None = None,
              voz: str | None = None, solo_audio: bool = False) -> dict:
        """Lanza la generacion en segundo plano. ValueError si ya hay una
        corrida activa, si el proveedor no esta disponible, o si hay que
        escribir un guion y nadie sabe escribirlo."""
        if not self.enabled:
            raise ValueError("Narracion no disponible: ningun proveedor de "
                             "voz instalado (edge-tts, piper o Vertex)")
        if self.running:
            raise ValueError("Ya hay una narracion en curso")
        proveedor, voz = self.resolver_voz(proveedor, voz)
        if proveedor == "archivo":
            raise ValueError("la grabacion propia se sube por clip, no se "
                             "genera")
        plan = self._plan(project, clip_ids, force, voz)
        if not plan:
            return {"queued": []}
        cat = {p["id"]: p for p in self.proveedores()}
        con_guionista = cat["vertex"]["escribe_guion"] and not solo_audio
        # Con guion guardado y `solo_audio`, o con un proveedor que no
        # escribe, se usa el guion existente. Si no lo hay, hace falta
        # Vertex; si tampoco, se dice QUE clips necesitan guion.
        if not con_guionista:
            faltan = [i["clip"]["title"] for i in plan if i["secciones"] is None]
            if faltan:
                raise ValueError(
                    "sin guion en: " + ", ".join(faltan[:6])
                    + (" …" if len(faltan) > 6 else "")
                    + ". Escribelo desde «Guion» (o configura Vertex)")
        else:
            for item in plan:
                item["secciones"] = None  # Vertex lo (re)escribe
        self._cancel = False
        self._run = {"project_id": project["id"], "total": len(plan),
                     "done": 0, "current": None, "errores": [],
                     "started": time.time(), "finished": False,
                     "proveedor": proveedor, "voz": voz}
        curso = {"name": project["name"], "description": project["description"],
                 "total_clips": len(self.db.list_clips(project["id"]))}
        destino = self.destino(project)
        self._task = asyncio.get_running_loop().create_task(
            self._correr(plan, curso, destino, proveedor, voz, con_guionista))
        return {"queued": [item["clip"]["id"] for item in plan],
                "proveedor": proveedor, "voz": voz}

    def cancel(self) -> bool:
        if not self.running:
            return False
        self._cancel = True
        return True

    async def _correr(self, plan: list[dict], curso: dict, destino: Path,
                      proveedor: str, voz: str, con_guionista: bool) -> None:
        try:
            await asyncio.to_thread(self._generar, plan, curso, destino,
                                    proveedor, voz, con_guionista)
        except Exception as e:  # fallo de setup (p.ej. credenciales rotas)
            self._run["errores"].append({"clip_id": None,
                                         "error": f"{type(e).__name__}: {e}"})
        finally:
            self._run["current"] = None
            self._run["finished"] = True

    def _generar(self, plan: list[dict], curso: dict, destino: Path,
                 proveedor: str = "vertex", voz: str | None = None,
                 con_guionista: bool = True) -> None:
        """Cuerpo bloqueante (corre en thread): un clip tras otro, escribiendo
        estado.json tras cada uno para que un corte a mitad no pierda nada."""
        destino.mkdir(parents=True, exist_ok=True)
        narrador = self._narrador(proveedor)
        guionista = None
        if con_guionista:
            guionista = narrador if proveedor == "vertex" else self._vertex()
        voz = voz or self.voz_defecto(proveedor)
        estado_path = destino / "estado.json"
        for item in plan:
            if self._cancel:
                break
            clip = item["clip"]
            self._run["current"] = {"clip_id": clip["id"],
                                    "etiqueta": item["etiqueta"]}
            try:
                entry = generar_clip(narrador, curso, clip, item["compuesto"],
                                     item["video_s"], voz, destino,
                                     item["etiqueta"], log=lambda _m: None,
                                     secciones=item.get("secciones"),
                                     guionista=guionista)
            except Exception as e:
                self._run["errores"].append(
                    {"clip_id": clip["id"],
                     "error": f"{type(e).__name__}: {e}"})
                continue
            estado = self._leer_estado(destino)
            estado[clip["id"]] = entry
            estado_path.write_text(json.dumps(estado, indent=2))
            self._run["done"] += 1

    def _narrador(self, proveedor: str):
        if proveedor == "vertex":
            return self._vertex()
        return tts_mod.fabricar(self.cfg, proveedor)

    def narrador_defecto(self):
        """Para la voz de los promos (audio_api): el proveedor por defecto."""
        proveedor = self.proveedor_defecto()
        if not proveedor:
            raise RuntimeError("ningun proveedor de voz disponible")
        return self._narrador(proveedor)

    def _vertex(self) -> VertexNarrador:
        return VertexNarrador(self.cfg.gcp_key_path, self.cfg.gcp_location,
                              self.cfg.gemini_model_deep,
                              self.cfg.gemini_model_tts)

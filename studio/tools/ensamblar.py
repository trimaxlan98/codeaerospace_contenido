#!/usr/bin/env python3
"""Monta un curso completo: clips en orden, su narracion, la marca y el empalme.

Hasta ahora esto se hacia FUERA de la app: descargar el zip, `unzip`, `sh mux.sh`.
Este script hace lo mismo dentro del contenedor manim (que es el unico sitio con
ffmpeg) y deja un solo archivo. La logica de la voz es la misma de `mux.sh`
—portada linea a linea, incluidos sus dos aprendizajes— para que la pelicula que
monta la app y la que monta el zip suenen igual.

Uso:
    ensamblar.py montar    <plan.json> <salida.mp4>
    ensamblar.py verificar <plan.json> <pelicula.mp4>

El plan lo escribe el backend; todas sus rutas son relativas al workspace:

    {
      "proyecto": "Algebra lineal - 1.1 El vector",
      "fps": 60,
      "transicion": {"tipo": "corte", "duracion": 0.6},
      "musica": {"tema": "orbita", "db": -24},
      "piezas": [
        {"titulo": "Clip 1", "video": "render_jobs/ab../media/.../Clip1.mp4",
         "voz": "guiones/algebra/01-el-vector.wav"},
        ...
      ]
    }

`musica` (opcional) pone una cama musical bajo la pelicula ENTERA, sintetizada
por `musica.py` con la duracion medida del montaje y agachada 9 dB donde hay
voz (*ducking*). Sin `musica` no cambia nada: el paso ni se ejecuta.

La envolvente del ducking se mide sobre el montaje SIN musica (el intermedio
`unida.mp4`), nunca sobre la pelicula ya mezclada: medida ahi, la propia cama
supera el umbral y se agacha a si misma — 96 % del metraje agachado en la
prueba, contra el 37 % real.

`tipo` de transicion:
  corte    empalme seco. NO recodifica el video (concat -c copy): es el unico
           camino barato y el que se usa por defecto.
  fundido | negro | deslizar
           empalmes de verdad (xfade). Recodifican la pelicula ENTERA: en el VPS
           (1.5 vCPU) un curso de 30 min tarda decenas de minutos. Es opt-in y la
           interfaz avisa del coste.

La ultima linea de stdout es un JSON con el informe. `montar` devuelve lo que se
hizo (duracion medida, resolucion, tamano y que llevaba cada pieza); `verificar`
mide la pelicula ya montada contra su plan — duracion, sonido pieza a pieza y
resolucion — porque la union puede salir mal SIN fallar.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# El ratio maximo al que se acelera una voz que no cabe en su clip. Mas alla se
# nota aunque atempo preserve el tono; el resto se recorta. Mismo numero que
# mux.sh: si uno cambia, el otro tambien.
ATEMPO_MAX = 1.15
# Holgura por debajo de la cual no vale la pena tocar la voz.
ATEMPO_MIN = 1.005

# Empalmes disponibles -> nombre de la transicion de xfade. `corte` no esta:
# es el camino sin recodificar.
TRANSICIONES = {
    "fundido": "fade",
    "negro": "fadeblack",
    "blanco": "fadewhite",
    "deslizar": "slideleft",
    "barrido": "wipeleft",
    "disolver": "dissolve",
}
DUR_TRANSICION_MIN = 0.1
DUR_TRANSICION_MAX = 3.0

# ── cama musical ──────────────────────────────────────────────────────────────
# Cuanto se agacha la musica donde suena la voz. 9 dB es el escalon que deja
# la musica presente y la palabra por delante; con 6 todavia compite y con 12
# el bombeo se oye como un error.
DUCK_DB = -9.0
# Por debajo de esto un tramo del montaje es silencio, no voz bajita (el suelo
# de ruido del AAC a 24 kHz queda muy por debajo). Nota: la musica se aparta
# bajo CUALQUIER sonido del montaje, no solo bajo la voz — en un curso narrado
# eso es la voz, y en un clip con cama de SFX tambien la cama. Es lo que se
# quiere: la musica es el fondo de todo lo demas, no un cuarto instrumento.
DUCK_UMBRAL_DB = -40.0
# Ataque corto y liberacion larga: la musica se aparta enseguida y vuelve sin
# que se note. Al reves (ataque largo) se come la primera silaba.
DUCK_ATAQUE_S, DUCK_LIBERA_S = 0.12, 0.60
# La envolvente se mide a 100 Hz sobre un decimado a 4 kHz: una pelicula de
# media hora a 24 kHz en float son cientos de MB y no hace falta ni uno.
ENV_HZ, ENV_SR = 100.0, 4000
MUSICA_DB_DEFECTO = -24.0
MUSICA_DB_MIN, MUSICA_DB_MAX = -60.0, 0.0

# Audio comun a todas las piezas: sin esto, un concat que mezcla clips con y sin
# pista de audio sale roto (y sin avisar).
AUDIO_ARGS = ("-c:a", "aac", "-b:a", "192k", "-ar", "24000", "-ac", "1")
SILENCIO = "anullsrc=r=24000:cl=mono"

# Suma de DOS pistas mono a ganancia unidad, sin `amix`.
#
# TRAMPA MEDIDA (2026-09-03): `amix=...:normalize=0` no existe en el ffmpeg de
# la imagen — Debian 11 trae 4.3.9 y esa opcion llego en 4.4. Un `amix` sin
# ella divide cada entrada por el numero de entradas, asi que la pelicula
# entera bajaria 6 dB por el hecho de anadir una segunda pista. `amerge`+`pan`
# suma con ganancia 1 y funciona desde ffmpeg 2.x. El `aformat` explicito
# evita que amerge se plante ante dos entradas con formatos distintos (aac
# decodificado contra wav pcm).
FMT_MONO = "aformat=sample_fmts=fltp:sample_rates=24000:channel_layouts=mono"


def suma_mono(a: str, b: str, salida: str) -> str:
    """Filtergraph que suma dos etiquetas de audio mono en `salida`."""
    return (f"{a}{FMT_MONO}[sa];{b}{FMT_MONO}[sb];"
            f"[sa][sb]amerge=inputs=2,pan=mono|c0=c0+c1{salida}")


class ErrorPlan(Exception):
    """El plan no describe una pelicula montable."""


# ── medir ─────────────────────────────────────────────────────────────────────

def _corre(*argv, timeout=None):
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)


def duracion(ruta) -> float:
    """Duracion en segundos, medida con ffprobe (nunca estimada)."""
    r = _corre("ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "csv=p=0", str(ruta), timeout=60)
    if r.returncode != 0 or not r.stdout.strip():
        raise ErrorPlan(f"no se pudo medir {ruta}: {r.stderr.strip()[-200:]}")
    return float(r.stdout.strip())


def tiene_audio(ruta) -> bool:
    """¿El mp4 ya trae pista de audio?

    Desde el sprint E3 un clip de curso puede llegar con su CAMA DE SONIDO ya
    mezclada (`sfx.py` sobre el mp4 mudo). Si ademas hay narracion, hay que
    MEZCLAR las dos: mapear solo la voz tiraba la cama por la borda sin que
    nada fallara.
    """
    r = _corre("ffprobe", "-v", "error", "-select_streams", "a",
               "-show_entries", "stream=index", "-of", "csv=p=0",
               str(ruta), timeout=60)
    return r.returncode == 0 and bool(r.stdout.strip())


def resolucion(ruta) -> str:
    r = _corre("ffprobe", "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x",
               str(ruta), timeout=60)
    return r.stdout.strip() if r.returncode == 0 else ""


def ratio_atempo(dur_voz: float, dur_video: float) -> float:
    """Cuanto hay que acelerar la voz para que quepa. 1.0 = no tocarla.

    Portado de mux.sh: por debajo de ATEMPO_MIN no vale la pena, por encima de
    ATEMPO_MAX se nota mas el pitido que la cola perdida.
    """
    if dur_video <= 0:
        return 1.0
    r = dur_voz / dur_video
    if r < ATEMPO_MIN:
        return 1.0
    return min(r, ATEMPO_MAX)


# ── plan ──────────────────────────────────────────────────────────────────────

def lee_plan(ruta) -> dict:
    try:
        plan = json.loads(Path(ruta).read_text())
    except (OSError, ValueError) as exc:
        raise ErrorPlan(f"plan ilegible: {exc}") from exc
    piezas = plan.get("piezas")
    if not isinstance(piezas, list) or not piezas:
        raise ErrorPlan("el plan no tiene piezas")
    for p in piezas:
        if not isinstance(p, dict) or not p.get("video"):
            raise ErrorPlan("una pieza no tiene video")
    tr = plan.get("transicion") or {}
    tipo = tr.get("tipo", "corte")
    if tipo != "corte" and tipo not in TRANSICIONES:
        raise ErrorPlan(f"transicion desconocida: {tipo}")
    dur = float(tr.get("duracion", 0.6))
    if tipo != "corte" and not (DUR_TRANSICION_MIN <= dur <= DUR_TRANSICION_MAX):
        raise ErrorPlan(f"duracion de transicion fuera de rango: {dur}")
    mus = plan.get("musica")
    if mus:
        if not isinstance(mus, dict) or not mus.get("tema"):
            raise ErrorPlan("la musica del plan no dice que tema")
        db = float(mus.get("db", MUSICA_DB_DEFECTO))
        if not (MUSICA_DB_MIN <= db <= MUSICA_DB_MAX):
            raise ErrorPlan(f"nivel de musica fuera de rango: {db}")
    return plan


# ── paso 1: cada pieza con su audio ───────────────────────────────────────────

def args_pieza(video: str, voz: str | None, salida: str,
               ratio: float = 1.0, cama: bool = False) -> list[str]:
    """Argumentos de ffmpeg para dejar una pieza con UNA pista de audio.

    El video se COPIA siempre (`-c:v copy`): este paso solo toca el audio, asi
    que cuesta segundos aunque el clip dure minutos. Cuatro casos:

        voz + cama   se SUMAN a ganancia unidad (`suma_mono`, ver la trampa
                     del amix ahi arriba). El nivel de la cama es cosa del
                     manifiesto —nace en -16 dB para un clip de curso— y aqui
                     no se toca: una ganancia escondida haria que el nivel que
                     se eligio en la interfaz no fuera el que se oye.
        voz sola     apad + -shortest, como mux.sh.
        cama sola    se re-codifica al formato comun (24 kHz mono) para que
                     el `concat -c copy` no encuentre dos audios distintos.
        ninguna      pista de silencio: un concat que mezcla clips con y sin
                     audio sale mudo desde el primero que no la tiene.
    """
    af = "apad" if ratio == 1.0 else f"atempo={ratio:.4f},apad"
    if voz and cama:
        filtro = f"[1:a]{af}[v];" + suma_mono("[0:a]", "[v]", "[a]")
        return ["ffmpeg", "-y", "-nostdin", "-i", video, "-i", voz,
                "-filter_complex", filtro, "-map", "0:v", "-map", "[a]",
                "-c:v", "copy", *AUDIO_ARGS, "-shortest", salida]
    if voz:
        return ["ffmpeg", "-y", "-nostdin", "-i", video, "-i", voz,
                "-c:v", "copy", *AUDIO_ARGS, "-af", af, "-shortest", salida]
    if cama:
        return ["ffmpeg", "-y", "-nostdin", "-i", video,
                "-map", "0:v", "-map", "0:a",
                "-c:v", "copy", *AUDIO_ARGS, salida]
    return ["ffmpeg", "-y", "-nostdin", "-i", video,
            "-f", "lavfi", "-i", SILENCIO,
            "-c:v", "copy", *AUDIO_ARGS, "-shortest", salida]


# ── paso 2: unir ──────────────────────────────────────────────────────────────

def filtro_xfade(duraciones: list[float], transicion: str, d: float) -> str:
    """Filtergraph que encadena N piezas con la misma transicion.

    El offset de cada empalme se calcula sobre lo YA acumulado, no sobre la
    suma de las duraciones: cada xfade acorta el resultado en `d`, y usar la
    suma cruda desplaza los empalmes cada vez mas (el ultimo cae fuera del
    video y ffmpeg lo pega sin fundir, en silencio).
    """
    if len(duraciones) < 2:
        raise ErrorPlan("hacen falta al menos dos piezas para una transicion")
    partes = []
    acc = duraciones[0]
    v_ant, a_ant = "[0:v]", "[0:a]"
    for i in range(1, len(duraciones)):
        offset = max(acc - d, 0.0)
        v_out = f"[v{i}]" if i < len(duraciones) - 1 else "[vout]"
        a_out = f"[a{i}]" if i < len(duraciones) - 1 else "[aout]"
        partes.append(f"{v_ant}[{i}:v]xfade=transition={transicion}"
                      f":duration={d:.3f}:offset={offset:.3f}{v_out}")
        partes.append(f"{a_ant}[{i}:a]acrossfade=d={d:.3f}:c1=tri:c2=tri{a_out}")
        v_ant, a_ant = v_out, a_out
        acc = acc + duraciones[i] - d
    return ";".join(partes)


def args_concat(lista: str, salida: str) -> list[str]:
    """Union sin recodificar. La lista debe vivir en el MISMO directorio que
    los mp4: ffmpeg resuelve las rutas relativas de un concat.txt contra el
    directorio del archivo, no contra el cwd (esto ya monto un curso mudo una
    vez sin que nada fallara)."""
    return ["ffmpeg", "-y", "-nostdin", "-f", "concat", "-safe", "0",
            "-i", lista, "-c", "copy", "-movflags", "+faststart", salida]


def args_xfade(entradas: list[str], filtro: str, fps: int,
               salida: str) -> list[str]:
    argv = ["ffmpeg", "-y", "-nostdin"]
    for e in entradas:
        argv += ["-i", e]
    argv += ["-filter_complex", filtro, "-map", "[vout]", "-map", "[aout]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", str(fps),
             *AUDIO_ARGS, "-movflags", "+faststart", salida]
    return argv


# ── paso 3: la cama musical ───────────────────────────────────────────────────

def envolvente(video, hz: float = ENV_HZ, sr: int = ENV_SR):
    """Envolvente RMS del audio de `video`, muestreada a `hz`.

    Decimando a `sr` primero: media hora a 24 kHz en float64 son 345 MB y la
    envolvente no gana ni un decimal por tenerlos. None si no hay audio.
    """
    import numpy as np
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-nostdin", "-i", str(video),
         "-map", "0:a?", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
        capture_output=True, timeout=3600)
    if r.returncode != 0 or not r.stdout:
        return None
    x = np.frombuffer(r.stdout, dtype="<i2").astype(np.float32) / 32768.0
    k = max(1, int(round(sr / hz)))
    n = len(x) // k
    if n == 0:
        return None
    return np.sqrt((x[:n * k].reshape(n, k).astype(np.float64) ** 2).mean(1))


def curva_ducking(env, hz: float = ENV_HZ, duck_db: float = DUCK_DB,
                  umbral_db: float = DUCK_UMBRAL_DB,
                  ataque: float = DUCK_ATAQUE_S, libera: float = DUCK_LIBERA_S):
    """De la envolvente de la pelicula a la ganancia LINEAL de la musica.

    Funcion pura: se prueba sin ffmpeg y sin montar nada, que es justo lo que
    hace falta para poder cambiar el escalon sin volver a montar un curso.

    Un polo asimetrico — rapido para bajar, lento para subir — porque el
    error que se oye es siempre el mismo: la musica que tarda en apartarse se
    come la primera silaba, y la que vuelve de golpe bombea.
    """
    import numpy as np
    env = np.asarray(env, dtype=float)
    objetivo = np.where(env > 10 ** (umbral_db / 20), 10 ** (duck_db / 20), 1.0)
    a_at = float(np.exp(-1.0 / max(ataque * hz, 1e-6)))
    a_re = float(np.exp(-1.0 / max(libera * hz, 1e-6)))
    g = np.empty(len(objetivo))
    y = 1.0
    for i, o in enumerate(objetivo):
        a = a_at if o < y else a_re
        y = a * y + (1 - a) * o
        g[i] = y
    return g


def args_musica(video: str, musica_wav: str, salida: str) -> list[str]:
    """Mezcla la cama bajo el montaje. El video se COPIA.

    La suma va a ganancia unidad (`suma_mono`): la pelicula tiene que sonar
    igual que antes, con musica debajo, no 6 dB mas baja por haberla anadido.

    El `alimiter` es una red, no un efecto: con la musica en -24 dB y la voz
    en -1.5 la suma pica en -0.9 dBFS y no llega a tocarlo; existe por si
    alguien sube la cama. `level=disabled` es obligatorio — el auto-level de
    alimiter viene ENCENDIDO por defecto y sin apagarlo el filtro sube la
    pelicula entera hasta el techo, que es exactamente lo contrario de lo que
    se le pide.
    """
    return ["ffmpeg", "-y", "-nostdin", "-i", video, "-i", musica_wav,
            "-filter_complex",
            suma_mono("[0:a]", "[1:a]", "[m]")
            + ";[m]alimiter=limit=0.94:attack=5:release=60:level=disabled[a]",
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", *AUDIO_ARGS,
            "-shortest", "-movflags", "+faststart", salida]


def pon_musica(video, salida, mus: dict, tmp: Path, verbose=True) -> dict:
    """Cama musical bajo la pelicula ya montada. Devuelve lo medido.

    El orden importa: primero se MIDE la pelicula (duracion real y envolvente
    de la voz), luego se sintetiza la cama de esa duracion exacta con la
    ganancia de ducking ya aplicada, y solo entonces se mezcla. Sintetizar
    antes de medir daria una cama que sobra o falta al final.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import musica as musica_mod

    total = duracion(video)
    tema = str(mus["tema"])
    db = float(mus.get("db", MUSICA_DB_DEFECTO))
    env = envolvente(video)
    ganancia = None
    tramo_voz = 0.0
    if env is not None and len(env):
        g = curva_ducking(env, ENV_HZ)
        ganancia = (g, ENV_HZ)
        tramo_voz = float((g < 0.9).mean())
    wav = tmp / "musica.wav"
    musica_mod.escribe_cama(wav, tema, total, db, mus.get("bpm"),
                            ganancia=ganancia)
    if verbose:
        print(f"[musica] {tema} {total:.1f} s a {db:.0f} dB, ducking sobre el "
              f"{tramo_voz * 100:.0f} % de la pelicula", file=sys.stderr)
    r = _corre(*args_musica(str(video), str(wav), str(salida)), timeout=7200)
    if r.returncode != 0 or not Path(salida).is_file():
        raise ErrorPlan(f"la cama musical salio con {r.returncode}: "
                        f"{r.stderr.strip()[-300:]}")
    return {"tema": tema, "db": db, "duracion": round(total, 3),
            "ducking_db": DUCK_DB, "tramo_con_voz": round(tramo_voz, 3)}


# ── orquestacion ──────────────────────────────────────────────────────────────

def ensamblar(plan_path, salida, trabajo=None, verbose=True) -> dict:
    plan = lee_plan(plan_path)
    raiz = Path(plan.get("raiz", "."))
    piezas = plan["piezas"]
    tr = plan.get("transicion") or {}
    tipo = tr.get("tipo", "corte")
    d_tr = float(tr.get("duracion", 0.6))
    fps = int(plan.get("fps", 60))
    mus = plan.get("musica") or None

    tmp = Path(trabajo) if trabajo else Path(tempfile.mkdtemp(prefix="pelicula-"))
    tmp.mkdir(parents=True, exist_ok=True)
    borrar_tmp = trabajo is None
    detalle = []

    try:
        # Paso 1 — cada pieza queda con pista de audio (video copiado).
        montadas = []
        for i, p in enumerate(piezas):
            video = raiz / p["video"]
            if not video.is_file():
                raise ErrorPlan(f"falta el video de la pieza {i + 1}: {p['video']}")
            voz_rel = p.get("voz")
            voz = raiz / voz_rel if voz_rel else None
            if voz is not None and not voz.is_file():
                voz, voz_rel = None, None
            dur_v = duracion(video)
            ratio = 1.0
            if voz is not None:
                ratio = ratio_atempo(duracion(voz), dur_v)
            destino = tmp / f"{i:03d}.mp4"
            cama = tiene_audio(video)
            argv = args_pieza(str(video), str(voz) if voz else None,
                              str(destino), ratio, cama)
            r = _corre(*argv, timeout=1800)
            if r.returncode != 0 or not destino.is_file():
                raise ErrorPlan(f"pieza {i + 1}: ffmpeg salio con "
                                f"{r.returncode}: {r.stderr.strip()[-300:]}")
            montadas.append(destino)
            detalle.append({
                "titulo": p.get("titulo", f"pieza {i + 1}"),
                "duracion": round(dur_v, 3),
                "voz": bool(voz),
                "cama": cama,
                "atempo": round(ratio, 4) if ratio != 1.0 else None,
            })
            if verbose:
                print(f"[{i + 1}/{len(piezas)}] {p.get('titulo', '')} "
                      f"{dur_v:.1f}s voz={'si' if voz else 'no'} "
                      f"cama={'si' if cama else 'no'}", file=sys.stderr)

        salida = Path(salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        # Con musica la union va a un intermedio: la cama necesita la duracion
        # MEDIDA del montaje, asi que solo puede ponerse despues de unir.
        unida = (tmp / "unida.mp4") if mus else salida

        # Paso 2 — unir.
        if tipo == "corte" or len(montadas) == 1:
            lista = tmp / "concat.txt"
            lista.write_text("".join(f"file '{m.name}'\n" for m in montadas))
            argv = args_concat(str(lista), str(Path(unida).resolve()))
            r = _corre(*argv, timeout=3600)
        else:
            duraciones = [duracion(m) for m in montadas]
            filtro = filtro_xfade(duraciones, TRANSICIONES[tipo], d_tr)
            argv = args_xfade([str(m) for m in montadas], filtro, fps,
                              str(Path(unida).resolve()))
            r = _corre(*argv, timeout=14400)
        if r.returncode != 0 or not Path(unida).is_file():
            raise ErrorPlan(f"la union salio con {r.returncode}: "
                            f"{r.stderr.strip()[-300:]}")

        # Paso 3 — la cama musical (opcional).
        info_musica = None
        if mus:
            info_musica = pon_musica(unida, salida, mus, tmp, verbose)

        informe = {
            "ok": True,
            "proyecto": plan.get("proyecto", ""),
            "piezas": len(montadas),
            "con_voz": sum(1 for d in detalle if d["voz"]),
            "con_cama": sum(1 for d in detalle if d["cama"]),
            "transicion": tipo,
            "duracion": round(duracion(salida), 3),
            "resolucion": resolucion(salida),
            "bytes": salida.stat().st_size,
            "musica": info_musica,
            "detalle": detalle,
        }
        return informe
    finally:
        if borrar_tmp:
            shutil.rmtree(tmp, ignore_errors=True)


# ── verificacion ──────────────────────────────────────────────────────────────

# Por debajo de esto un tramo es silencio digital, no "bajito": el suelo de
# ruido del AAC a 24 kHz mono queda muy por encima.
SILENCIO_DB = -60.0
# Cuanto puede desviarse la duracion medida de la prevista sin que sea un
# sintoma. El re-encode cuadra a frames enteros y a los fps del proyecto, asi
# que medio segundo de margen es normal; dos son otra cosa.
TOLERANCIA_S = 0.5


def pico_db(video, inicio: float, dur: float) -> float | None:
    """Pico en dBFS de un tramo del archivo, o None si no hay audio.

    Se mide con `volumedetect` sobre el TRAMO (`-ss`/`-t`), no sobre el archivo
    entero: lo que interesa es si una pieza concreta se quedo muda, y un solo
    numero global no lo dice.
    """
    # `-v info`, no `error`: volumedetect escribe su resumen en stderr a nivel
    # INFO, y con `-v error` la medicion sale vacia y toda pieza parece muda.
    r = _corre("ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-v", "info",
               "-ss", f"{inicio:.3f}", "-t", f"{max(dur, 0.05):.3f}",
               "-i", str(video),
               "-map", "0:a?", "-af", "volumedetect", "-f", "null", "-",
               timeout=600)
    for linea in (r.stderr or "").splitlines():
        if "max_volume:" in linea:
            try:
                return float(linea.split("max_volume:")[1].strip().split()[0])
            except (IndexError, ValueError):
                return None
    return None


def diagnostico(medida: float, prevista: float, mudos: list[str],
                res_medida: str, res_plan: str) -> list[str]:
    """De las medidas a los problemas. Funcion pura: se prueba sin ffmpeg.

    Vive aparte de `verificar` a proposito — lo que decide si una pelicula
    esta bien es esta lista de reglas, y tiene que poder cambiarse y probarse
    sin montar nada.
    """
    problemas = []
    desfase = medida - prevista
    if abs(desfase) > TOLERANCIA_S:
        problemas.append(
            f"la pelicula dura {medida:.2f} s y deberia durar {prevista:.2f} s"
            f" ({desfase:+.2f} s): falta o sobra material")
    if mudos:
        problemas.append(f"{len(mudos)} piezas perdieron su sonido al montar: "
                         + ", ".join(mudos[:4])
                         + ("…" if len(mudos) > 4 else ""))
    if res_plan and res_medida and res_plan != res_medida:
        problemas.append(f"la pelicula es {res_medida} y el curso es {res_plan}")
    return problemas


def espera_sonido(pieza: dict, video) -> bool:
    """¿Esta pieza TRAIA sonido que la pelicula pueda perder?

    Un curso sin narrar es mudo a proposito: acusarlo cada vez convertiria la
    medicion en ruido que se aprende a ignorar. Solo cuenta como perdida el
    silencio de una pieza que llevaba voz o cama.
    """
    return bool(pieza.get("voz")) or (video.is_file() and tiene_audio(video))


def verificar(plan_path, pelicula) -> dict:
    """Mide la pelicula montada contra el plan del que salio.

    Tres comprobaciones, todas objetivas, y cada una caza un fallo que la
    union puede producir SIN fallar:

      duracion     si falta una pieza, o si el offset de un xfade la dejo
                   fuera, el total no cuadra con la suma menos los empalmes.
      audio        un `concat` que mezcla clips con y sin pista sale mudo
                   desde el primero que no la tiene. Se mide pieza a pieza (un
                   pico global sano puede convivir con media pelicula muda) y
                   solo se acusa a las que TRAIAN sonido: un curso sin narrar
                   es mudo a proposito.
      resolucion   la que dice el plan es la del proyecto; si no coincide, se
                   colo material de otro tamano.
    """
    plan = lee_plan(plan_path)
    pelicula = Path(pelicula)
    if not pelicula.is_file():
        raise ErrorPlan("no hay pelicula que medir")

    raiz = Path(plan.get("raiz", "."))
    tr = plan.get("transicion") or {}
    tipo = tr.get("tipo", "corte")
    d_tr = float(tr.get("duracion", 0.6)) if tipo != "corte" else 0.0

    duraciones, esperaba = [], []
    for p in plan["piezas"]:
        video = raiz / p["video"]
        existe = video.is_file()
        duraciones.append(duracion(video) if existe else 0.0)
        esperaba.append(espera_sonido(p, video))
    prevista = sum(duraciones) - d_tr * max(len(duraciones) - 1, 0)
    medida = duracion(pelicula)

    # Los tramos se recorren sobre la pelicula YA montada: cada empalme la
    # acorta, asi que el inicio de cada pieza no es la suma de las anteriores.
    tramos, t = [], 0.0
    for p, dur, con_sonido in zip(plan["piezas"], duraciones, esperaba):
        pico = pico_db(pelicula, t + 0.05, max(dur - 0.1, 0.1))
        callado = pico is None or pico <= SILENCIO_DB
        tramos.append({
            "titulo": p.get("titulo", ""),
            "inicio": round(t, 3),
            "duracion": round(dur, 3),
            "pico_db": pico,
            "esperaba_sonido": con_sonido,
            "mudo": callado,
            "perdio_sonido": con_sonido and callado,
        })
        t += dur - d_tr

    res_medida = resolucion(pelicula)
    res_plan = plan.get("resolucion", "")
    mudos = [x["titulo"] for x in tramos if x["perdio_sonido"]]
    desfase = medida - prevista
    problemas = diagnostico(medida, prevista, mudos, res_medida, res_plan)

    return {
        "ok": not problemas,
        "problemas": problemas,
        "duracion_medida": round(medida, 3),
        "duracion_prevista": round(prevista, 3),
        "desfase": round(desfase, 3),
        "tolerancia": TOLERANCIA_S,
        "resolucion": res_medida,
        "resolucion_esperada": res_plan,
        "piezas": len(tramos),
        "mudas": len(mudos),
        "tramos": tramos,
    }


def main(argv):
    if len(argv) != 4 or argv[1] not in ("montar", "verificar"):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        if argv[1] == "montar":
            informe = ensamblar(argv[2], argv[3])
        else:
            informe = verificar(argv[2], argv[3])
    except ErrorPlan as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    print(json.dumps(informe))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

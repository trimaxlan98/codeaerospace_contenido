#!/usr/bin/env python3
"""Monta un curso completo: clips en orden, su narracion, la marca y el empalme.

Hasta ahora esto se hacia FUERA de la app: descargar el zip, `unzip`, `sh mux.sh`.
Este script hace lo mismo dentro del contenedor manim (que es el unico sitio con
ffmpeg) y deja un solo archivo. La logica de la voz es la misma de `mux.sh`
—portada linea a linea, incluidos sus dos aprendizajes— para que la pelicula que
monta la app y la que monta el zip suenen igual.

Uso:
    ensamblar.py <plan.json> <salida.mp4>

El plan lo escribe el backend; todas sus rutas son relativas al workspace:

    {
      "proyecto": "Algebra lineal - 1.1 El vector",
      "fps": 60,
      "transicion": {"tipo": "corte", "duracion": 0.6},
      "piezas": [
        {"titulo": "Clip 1", "video": "render_jobs/ab../media/.../Clip1.mp4",
         "voz": "guiones/algebra/01-el-vector.wav"},
        ...
      ]
    }

`tipo` de transicion:
  corte    empalme seco. NO recodifica el video (concat -c copy): es el unico
           camino barato y el que se usa por defecto.
  fundido | negro | deslizar
           empalmes de verdad (xfade). Recodifican la pelicula ENTERA: en el VPS
           (1.5 vCPU) un curso de 30 min tarda decenas de minutos. Es opt-in y la
           interfaz avisa del coste.

La ultima linea de stdout es un JSON con el informe (duracion medida, resolucion,
tamano y que se hizo con cada pieza).
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

# Audio comun a todas las piezas: sin esto, un concat que mezcla clips con y sin
# pista de audio sale roto (y sin avisar).
AUDIO_ARGS = ("-c:a", "aac", "-b:a", "192k", "-ar", "24000", "-ac", "1")
SILENCIO = "anullsrc=r=24000:cl=mono"


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
    return plan


# ── paso 1: cada pieza con su audio ───────────────────────────────────────────

def args_pieza(video: str, voz: str | None, salida: str,
               ratio: float = 1.0) -> list[str]:
    """Argumentos de ffmpeg para dejar una pieza con pista de audio.

    El video se COPIA siempre (`-c:v copy`): este paso solo toca el audio, asi
    que cuesta segundos aunque el clip dure minutos.
    """
    if voz:
        af = "apad" if ratio == 1.0 else f"atempo={ratio:.4f},apad"
        return ["ffmpeg", "-y", "-nostdin", "-i", video, "-i", voz,
                "-c:v", "copy", *AUDIO_ARGS, "-af", af, "-shortest", salida]
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


# ── orquestacion ──────────────────────────────────────────────────────────────

def ensamblar(plan_path, salida, trabajo=None, verbose=True) -> dict:
    plan = lee_plan(plan_path)
    raiz = Path(plan.get("raiz", "."))
    piezas = plan["piezas"]
    tr = plan.get("transicion") or {}
    tipo = tr.get("tipo", "corte")
    d_tr = float(tr.get("duracion", 0.6))
    fps = int(plan.get("fps", 60))

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
            argv = args_pieza(str(video), str(voz) if voz else None,
                              str(destino), ratio)
            r = _corre(*argv, timeout=1800)
            if r.returncode != 0 or not destino.is_file():
                raise ErrorPlan(f"pieza {i + 1}: ffmpeg salio con "
                                f"{r.returncode}: {r.stderr.strip()[-300:]}")
            montadas.append(destino)
            detalle.append({
                "titulo": p.get("titulo", f"pieza {i + 1}"),
                "duracion": round(dur_v, 3),
                "voz": bool(voz),
                "atempo": round(ratio, 4) if ratio != 1.0 else None,
            })
            if verbose:
                print(f"[{i + 1}/{len(piezas)}] {p.get('titulo', '')} "
                      f"{dur_v:.1f}s voz={'si' if voz else 'no'}",
                      file=sys.stderr)

        salida = Path(salida)
        salida.parent.mkdir(parents=True, exist_ok=True)

        # Paso 2 — unir.
        if tipo == "corte" or len(montadas) == 1:
            lista = tmp / "concat.txt"
            lista.write_text("".join(f"file '{m.name}'\n" for m in montadas))
            argv = args_concat(str(lista), str(salida.resolve()))
            r = _corre(*argv, timeout=3600)
        else:
            duraciones = [duracion(m) for m in montadas]
            filtro = filtro_xfade(duraciones, TRANSICIONES[tipo], d_tr)
            argv = args_xfade([str(m) for m in montadas], filtro, fps,
                              str(salida.resolve()))
            r = _corre(*argv, timeout=14400)
        if r.returncode != 0 or not salida.is_file():
            raise ErrorPlan(f"la union salio con {r.returncode}: "
                            f"{r.stderr.strip()[-300:]}")

        informe = {
            "ok": True,
            "proyecto": plan.get("proyecto", ""),
            "piezas": len(montadas),
            "con_voz": sum(1 for d in detalle if d["voz"]),
            "transicion": tipo,
            "duracion": round(duracion(salida), 3),
            "resolucion": resolucion(salida),
            "bytes": salida.stat().st_size,
            "detalle": detalle,
        }
        return informe
    finally:
        if borrar_tmp:
            shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        informe = ensamblar(argv[1], argv[2])
    except ErrorPlan as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    print(json.dumps(informe))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

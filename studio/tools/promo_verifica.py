#!/usr/bin/env python3
"""Verificacion de un promo: se mide sobre el ARCHIVO, no a ojo.

Un promo se juzga por cuatro cosas, y ninguna se ve bien mirando el video
una vez:

  1. **La costura del bucle.** El ultimo frame tiene que ser el primero. Se
     compara SOBRE EL SUELO DEL CODEC: dos frames que en la escena son el
     mismo dibujo no salen identicos del h264 (en fondo plano y oscuro la
     cuantizacion llega al 0.18 % de los subpixeles). Sin descontar ese
     suelo, un bucle perfecto parece sucio.
  2. **La duracion**: 8-15 s. Mas corto no cuenta nada, mas largo se cae del
     formato de redes.
  3. **El audio**: que exista, a que pico suena y —lo que rompe el bucle—
     que los dos extremos esten en silencio.
  4. **Los frames**: una tira equiespaciada y el par primero|ultimo, para
     mirar la composicion en vez de suponerla.

Este modulo es la UNICA implementacion: lo importa `render_promo.py` (CLI
local) y lo ejecuta el runner de ManimStudio dentro del contenedor manim
(el backend no tiene ffmpeg). Solo stdlib: ni numpy ni manim.

    python3 promo_verifica.py <video.mp4> <directorio-de-salida>
        [--frames 6] [--min 8] [--max 15]

Escribe los PNG en el directorio y el informe JSON por stdout.
"""

import argparse
import json
import math
import struct
import subprocess
import sys
import wave
from pathlib import Path

# Umbrales de la costura, aplicados SOBRE EL SUELO del codec.
COSTURA_DIF_MEDIA = 0.5     # diferencia media por subpixel (0-255)
COSTURA_PCT_PIXELES = 0.20  # % de subpixeles con salto visible

# Un promo dura esto (el rango del formato de redes).
DUR_MIN, DUR_MAX = 8.0, 15.0

# Los extremos del audio: por encima de esto, el salto del bucle se oye.
SILENCIO_DB = -40.0
VENTANA_EXTREMO_S = 0.10

# El ultimo frame NO se saca con `-ss dur-epsilon`: si el salto cae despues
# del ultimo paquete, ffmpeg sale con exito y no escribe nada. Se decodifica
# la cola con `-update 1` (cada frame pisa al anterior) y lo que queda al
# terminar ES el ultimo frame.
COLA_FINAL = 0.35

# Ancho al que se reducen los frames para compararlos: comparar 2 MP en
# Python puro es lento y no hace falta — una costura no es cosa de un pixel.
ANCHO_COMPARA = 240


def _ff(*args: str, binario: bool = False):
    return subprocess.run(["ffmpeg", "-nostdin", "-v", "error", *args],
                          capture_output=True, check=True).stdout


def ffprobe(video: Path, campos: str, stream: str | None = None) -> str:
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream, "-show_entries", f"stream={campos}"]
    else:
        cmd += ["-show_entries", f"format={campos}"]
    cmd += ["-of", "csv=p=0", str(video)]
    return subprocess.run(cmd, capture_output=True, text=True,
                          check=True).stdout.strip()


def datos_video(video: Path) -> dict:
    """Duracion, dimensiones y fps reales del mp4."""
    dur = float(ffprobe(video, "duration"))
    ancho, alto, tasa = ffprobe(video, "width,height,r_frame_rate",
                                stream="v:0").split(",")[:3]
    num, _, den = tasa.partition("/")
    fps = float(num) / float(den or 1)
    return {"dur": dur, "ancho": int(ancho), "alto": int(alto), "fps": fps}


# ── frames ───────────────────────────────────────────────────────────────────

def _frame(video: Path, t: float, destino: Path) -> None:
    _ff("-ss", f"{t:.4f}", "-i", str(video), "-frames:v", "1", "-y", str(destino))


def _frame_final(video: Path, destino: Path) -> None:
    _ff("-sseof", f"-{COLA_FINAL}", "-i", str(video), "-update", "1", "-y",
        str(destino))


def _crudo(video: Path, t: float, ancho: int = ANCHO_COMPARA) -> bytes:
    return _ff("-ss", f"{t:.4f}", "-i", str(video), "-vf", f"scale={ancho}:-2",
               "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-")


def _crudo_final(video: Path, tam: int, ancho: int = ANCHO_COMPARA) -> bytes:
    cola = _ff("-sseof", f"-{COLA_FINAL}", "-i", str(video), "-vf",
               f"scale={ancho}:-2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-")
    return cola[-tam:] if len(cola) >= tam else b""


def _comparar(a: bytes, b: bytes) -> tuple[float, float]:
    """(diferencia media por subpixel, % de subpixeles con salto visible)."""
    if not a or len(a) != len(b):
        return float("nan"), float("nan")
    total = sum(abs(x - y) for x, y in zip(a, b))
    visibles = sum(1 for x, y in zip(a, b) if abs(x - y) > 8)
    return total / len(a), 100.0 * visibles / len(a)


def medir_bucle(video: Path, datos: dict, destino: Path) -> dict:
    """¿Se nota el corte cuando la app repite el video?"""
    destino.mkdir(parents=True, exist_ok=True)
    _frame(video, 0.0, destino / "primero.png")
    _frame_final(video, destino / "ultimo.png")
    _ff("-y", "-i", str(destino / "primero.png"), "-i", str(destino / "ultimo.png"),
        "-filter_complex", "[0:v][1:v]hstack=inputs=2", str(destino / "costura.png"))

    a = _crudo(video, 0.0)
    b = _crudo_final(video, len(a))
    media, pct = _comparar(a, b)
    # El suelo: dos frames consecutivos del respiro inicial, que en la
    # escena son el MISMO dibujo.
    piso_media, piso_pct = _comparar(a, _crudo(video, 1.5 / datos["fps"]))
    if media != media or piso_media != piso_media:  # NaN
        return {"ok": False, "media": None, "pct": None,
                "piso_media": None, "piso_pct": None,
                "sobre_piso_media": None, "sobre_piso_pct": None,
                "motivo": "no se pudieron comparar los frames"}
    sobre_media = media - piso_media
    sobre_pct = pct - piso_pct
    return {"ok": sobre_media <= COSTURA_DIF_MEDIA and sobre_pct <= COSTURA_PCT_PIXELES,
            "media": round(media, 4), "pct": round(pct, 4),
            "piso_media": round(piso_media, 4), "piso_pct": round(piso_pct, 4),
            "sobre_piso_media": round(max(0.0, sobre_media), 4),
            "sobre_piso_pct": round(max(0.0, sobre_pct), 4)}


def extraer_frames(video: Path, destino: Path, cuantos: int, dur: float) -> list[str]:
    destino.mkdir(parents=True, exist_ok=True)
    for viejo in destino.glob("f[0-9][0-9].png"):
        viejo.unlink()
    nombres = []
    for i in range(cuantos):
        nombre = f"f{i + 1:02d}.png"
        _frame(video, dur * (i + 0.5) / cuantos, destino / nombre)
        nombres.append(nombre)
    return nombres


# ── audio ────────────────────────────────────────────────────────────────────

def _db(amplitud: float) -> float:
    return -120.0 if amplitud <= 0 else round(20 * math.log10(amplitud), 1)


def medir_audio(video: Path, destino: Path) -> dict:
    """Pico y extremos del audio, leyendo MUESTRAS.

    No se usa `volumedetect` sobre ventanas cortas: una ventana de 50 ms
    arrastra el frame AAC entero y acusa de ruidoso un arranque que en las
    muestras es cero exacto.
    """
    try:
        info = ffprobe(video, "codec_name,sample_rate,channels", stream="a:0")
    except subprocess.CalledProcessError:
        info = ""
    if not info:
        return {"tiene_audio": False, "ok": False,
                "motivo": "el video no lleva pista de audio"}
    codec, hz, canales = (info.split(",") + ["", "", ""])[:3]

    crudo = destino / "audio.wav"
    _ff("-y", "-i", str(video), "-ac", "1", "-ar", "24000", "-f", "wav", str(crudo))
    with wave.open(str(crudo)) as w:
        n, sr = w.getnframes(), w.getframerate()
        muestras = struct.unpack(f"<{n}h", w.readframes(n))
    crudo.unlink(missing_ok=True)
    if not n:
        return {"tiene_audio": False, "ok": False,
                "motivo": "la pista de audio esta vacia"}

    ventana = max(1, int(VENTANA_EXTREMO_S * sr))
    pico = _db(max(abs(x) for x in muestras) / 32768)
    entrada = _db(max(abs(x) for x in muestras[:ventana]) / 32768)
    salida = _db(max(abs(x) for x in muestras[-ventana:]) / 32768)
    extremos_ok = entrada <= SILENCIO_DB and salida <= SILENCIO_DB
    return {"tiene_audio": True, "ok": extremos_ok,
            "codec": codec, "hz": int(hz or 0), "canales": int(canales or 0),
            "dur": round(n / sr, 2), "pico_db": pico,
            "entrada_db": entrada, "salida_db": salida,
            "extremos_ok": extremos_ok}


# ── informe ──────────────────────────────────────────────────────────────────

def verificar(video: Path, destino: Path, frames: int = 6,
              dur_min: float = DUR_MIN, dur_max: float = DUR_MAX) -> dict:
    destino.mkdir(parents=True, exist_ok=True)
    datos = datos_video(video)
    bucle = medir_bucle(video, datos, destino)
    audio = medir_audio(video, destino)
    tira = extraer_frames(video, destino, frames, datos["dur"])
    duracion = {"ok": dur_min <= datos["dur"] <= dur_max,
                "min": dur_min, "max": dur_max, "s": round(datos["dur"], 2)}
    return {
        "ok": bool(bucle["ok"] and duracion["ok"]
                   and (audio["ok"] or not audio["tiene_audio"])),
        "archivo": video.name,
        "video": {**datos, "dur": round(datos["dur"], 2),
                  "fps": round(datos["fps"], 2),
                  "resolucion": f"{datos['ancho']}x{datos['alto']}"},
        "duracion": duracion,
        "bucle": bucle,
        "audio": audio,
        "frames": tira,
        "costura": "costura.png",
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video")
    p.add_argument("destino")
    p.add_argument("--frames", type=int, default=6)
    p.add_argument("--min", type=float, default=DUR_MIN)
    p.add_argument("--max", type=float, default=DUR_MAX)
    args = p.parse_args(argv[1:])
    informe = verificar(Path(args.video), Path(args.destino), args.frames,
                        args.min, args.max)
    print(json.dumps(informe, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

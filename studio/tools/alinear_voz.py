#!/usr/bin/env python3
"""Narra una pieza vertical con la voz EXACTAMENTE en su t_inicio.

Por que no vale `narrar_promo.py` aqui: su ensamblador acota el silencio que
mete entre frases a MAX_HUECO_S = 2.5 s (`app.narracion._ensamblar`). Eso
esta bien para un guion de curso horizontal, que habla casi todo el rato,
pero en un curso vertical la voz es rala a proposito —la imagen enseña y la
voz remata— y hay huecos de 4 a 7 segundos. Con el tope, cada frase se
adelanta hasta 2.8 s y acaba comentando el plano equivocado.

Aqui cada frase se sintetiza por separado, se le recorta el silencio y se
coloca en su instante, sin tope. Si una frase se pasa de larga y pisa a la
siguiente, se avisa (con cuanto) en vez de disimularlo: eso se arregla
acortando el texto, no moviendo el audio.

    studio/backend/venv/bin/python studio/tools/alinear_voz.py \
        <dir con clip.json> <salida.wav> [--limite S] [--voz Kore]

Necesita las credenciales de Vertex (`/etc/manimstudio/gcp-key.json`), que
solo estan en el VPS: se ejecuta alli y el wav se baja.
"""
import argparse
import json
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))
from app.narracion import (TTS_RATE, _escribir_wav,  # noqa: E402
                           _recortar_silencio)
from app.tts import narrador_desde_entorno  # noqa: E402

PAUSA_MINIMA_S = 0.25     # si una frase pisa a la siguiente, este es el aire
COLA_MINIMA_S = 0.8       # silencio que tiene que quedar al final


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pieza", type=Path)
    p.add_argument("salida", type=Path)
    p.add_argument("--limite", type=float, default=None)
    p.add_argument("--voz", default=None)
    p.add_argument("--proveedor", default=None,
                   choices=["vertex", "edge", "piper"])
    args = p.parse_args()

    manifiesto = json.loads((args.pieza / "clip.json").read_text())
    spec = manifiesto["voz"]
    secciones = spec["secciones"]
    limite = args.limite or manifiesto.get("duracion_objetivo")
    # La voz del clip.json (p.ej. "Charon") solo vale para su proveedor; con
    # otro se usa la voz por defecto de ese proveedor salvo --voz.
    voz_pedida = args.voz or (spec.get("voz") if (args.proveedor or
                              os.environ.get("MS_TTS_PROVIDER", "edge")) == "vertex" else None)
    vertex, voz = narrador_desde_entorno(args.proveedor, voz_pedida)
    print(f"voz: {vertex.id} · {voz}")

    audios = [_recortar_silencio(vertex.tts(s["texto"], voz))
              for s in secciones]

    pcm = bytearray()
    cursor = 0
    empujes = []
    for s, a in zip(secciones, audios):
        pedido = int(float(s["t_inicio"]) * TTS_RATE)
        off = pedido
        if off < cursor:
            off = cursor + int(PAUSA_MINIMA_S * TTS_RATE)
            empujes.append((float(s["t_inicio"]), (off - pedido) / TTS_RATE))
        pcm.extend(b"\x00\x00" * (off - cursor))
        pcm.extend(a)
        cursor = off + len(a) // 2

    dur = _escribir_wav(bytes(pcm), args.salida)
    print(f"{args.salida}  {dur:.2f} s  (voz {voz}, {len(secciones)} frases)")
    for t, cuanto in empujes:
        print(f"  AVISO: la frase de {t:.1f} s entro {cuanto:.2f} s tarde "
              "(la anterior se paso de larga: acorta el texto)")
    if limite:
        if dur > float(limite) - COLA_MINIMA_S:
            print(f"  AVISO: la voz ({dur:.2f} s) no deja {COLA_MINIMA_S} s "
                  f"de cola en un video de {float(limite):.2f} s")
            return 1
        print(f"  cola de silencio: {float(limite) - dur:.2f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

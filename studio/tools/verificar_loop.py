#!/usr/bin/env python3
"""Verifica que un video empalme consigo mismo (loop sin costura).

Compara el salto último→primer cuadro con el salto normal entre cuadros consecutivos. Si el salto de
empalme es parecido al normal (razón ≲ 1.5) el loop no se nota; si es mucho mayor, hay un corte.
Se compara a baja resolución (90×160) para que el ruido de compresión de los bordes (el primer cuadro es
un I-frame y el último no) no se confunda con un corte. Para el audio mide la discontinuidad entre la última y la primera muestra frente a la pendiente media.

OJO: en escenas casi estáticas el MP4 da falsos «CORTE» (el primer cuadro es un I-frame y el último
no; la diferencia de compresión supera al movimiento). La prueba definitiva es sin compresión:
  manim render -r 270,480 --fps 30 --format png --media_dir /tmp/x archivo.py Escena
  python3 verificar_loop.py --png /tmp/x/images/...      (compara PNG último→primero)
Verificado así el 2026-10-02: ReelOrbitEye, ReelATP y ReelModelo empalman igual que un paso normal.

Uso: python3 verificar_loop.py video.mp4 [...]   |   python3 verificar_loop.py --png carpeta
"""
import subprocess
import sys

import numpy as np


def cuadros(ruta, ancho=90, alto=160):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", ruta, "-vf", f"scale={ancho}:{alto},format=rgb24",
                                   "-f", "rawvideo", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, alto, ancho, 3).astype(np.float32)


def audio(ruta):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", ruta, "-vn", "-ac", "1", "-ar", "48000", "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32)


if sys.argv[1:2] == ["--png"]:
    import glob
    from PIL import Image
    fs = sorted(glob.glob(f"{sys.argv[2]}/**/*.png", recursive=True))
    ims = [np.asarray(Image.open(f).convert("RGB"), np.float32) for f in fs]
    pasos = [np.abs(ims[i + 1] - ims[i]).mean() for i in range(len(ims) - 1)]
    salto = np.abs(ims[0] - ims[-1]).mean()
    ok = salto < 1.6 * np.percentile(pasos, 90)
    print(f"{len(fs)} PNG  empalme={salto:.3f}  paso mediana={np.median(pasos):.3f}  {'OK' if ok else 'CORTE'}")
    sys.exit(0 if ok else 1)


def audio_wav(ruta):
    """Muestras del WAV original (sin el retardo del AAC): la costura real del audio."""
    import wave
    w = wave.open(ruta)
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).astype(np.float32) / 32768
    return x


fallos = 0

for ruta in sys.argv[1:]:
    c = cuadros(ruta)
    paso = np.abs(np.diff(c, axis=0)).mean((1, 2, 3))
    salto = np.abs(c[0] - c[-1]).mean()
    razon = salto / max(np.median(paso), 1e-6)
    ok_v = razon < 1.6
    a = audio(ruta)
    pend = np.abs(np.diff(a)).mean()
    cost = abs(a[0] - a[-1]) / max(pend, 1e-9)
    # El AAC añade ~21 ms de retardo inicial: se mira una ventana de 25 ms alrededor de la costura.
    rms_ini, rms_fin = np.sqrt((a[:1200] ** 2).mean()), np.sqrt((a[-1200:] ** 2).mean())
    # Costura de audio: en el WAV hermano (el AAC mete ~21 ms de silencio al inicio y la falsea).
    import os
    wav = os.path.splitext(ruta)[0] + ".wav"
    ok_a, txt_a = True, "sin WAV"
    if os.path.exists(wav):
        x = audio_wav(wav)
        paso_a = np.percentile(np.abs(np.diff(x, axis=0)).max(1), 99)
        cost_a = np.abs(x[0] - x[-1]).max()
        ok_a = cost_a <= paso_a
        txt_a = f"costura WAV={cost_a:.4f} vs paso p99={paso_a:.4f} {'OK' if ok_a else 'CLIC'}"
    print(f"{ruta.split('/')[-1]:24s} cuadros={len(c)} dur={len(a)/48000:.3f}s  "
          f"video: salto de empalme={salto:.2f} vs normal={np.median(paso):.2f} (x{razon:.2f}) {'OK' if ok_v else 'CORTE?'}  "
          f"audio: {txt_a}")
    fallos += (not ok_a)
sys.exit(1 if fallos else 0)

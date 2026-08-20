#!/usr/bin/env python3
"""sfx.py - efectos de sonido de marca para los videos de CO.DE Academy.

Sintetiza con numpy (sin assets externos, reproducible) una paleta corta de
efectos y las mezclas de los clips de identidad (intro "Encendido" y cierre
"Despedida"), y las pega al mp4 con ffmpeg.

Formato de salida SIEMPRE 24000 Hz mono (identico a la narracion TTS): asi
el `concat -c copy` de exports/mux.sh une clips con voz y clips con SFX sin
re-encodear. Los picos del master quedan en -6 dBFS (la marca suena por
debajo de la voz, que pica en -1.5..-0.5 dB).

Uso:
  sfx.py paleta [dir]     escribe la paleta de wavs sueltos (audicion/post)
  sfx.py marca            genera intro.wav/cierre.wav sincronizados con la
                          coreografia y los pega en
                          exports/marca-intro-y-cierre/{intro,cierre}.mp4
                          (respaldo {intro,cierre}_mudo.mp4 la primera vez;
                          re-ejecutar es idempotente: parte del *_mudo)
  sfx.py mezclar out.wav DUR evento@t[:dB] ...
                          mezcla generica para videos futuros, p. ej.:
                          sfx.py mezclar fx.wav 32 barrido@0.5:-8 tick@4:-12
  sfx.py aplicar video.mp4 audio.wav [out.mp4]
                          pega un wav a un mp4 (aac 24k mono, -shortest)

Corre en el host o dentro del contenedor manim; en ambos casos el canario
de main() verifica el numpy antes de sintetizar. Historia: el numpy del
sistema fue un 1.26.4 compilado del sdist sobre Python 3.14 (combo no
soportado) que corrompia arrays de forma silenciosa y no determinista;
arreglado el 2026-08-20 con numpy 2.5 (pip --user --break-system-packages).
Si el canario vuelve a abortar, usar el contenedor:

  docker run --rm --user $(id -u):$(id -g) -v "$PWD":/workspace \
    -w /workspace codeaerospace_contenido-manim python3 studio/tools/sfx.py marca
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 24000
REPO = Path(__file__).resolve().parents[2]
MARCA = REPO / "exports" / "marca-intro-y-cierre"


# ---------------------------------------------------------------- utilidades
def _t(dur):
    return np.arange(int(round(dur * SR))) / SR


def _env(n, ataque, caida):
    """Envolvente cosenoidal ataque/meseta/caida."""
    e = np.ones(n)
    na, nc = min(int(ataque * SR), n), min(int(caida * SR), n)
    if na:
        e[:na] = (1 - np.cos(np.linspace(0, np.pi, na))) / 2
    if nc:
        e[-nc:] *= (1 + np.cos(np.linspace(0, np.pi, nc))) / 2
    return e


def _filtra(x, lo, hi, suav=0.35):
    """Pasabanda por FFT con bordes sigmoides en log-frecuencia."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    f[0] = 1e-6
    lf = np.log2(f)
    w = 1 / (1 + np.exp(-(lf - np.log2(lo)) / suav))
    w *= 1 / (1 + np.exp((lf - np.log2(hi)) / suav))
    return np.fft.irfft(X * w, len(x))


def _norm(x, pico=1.0):
    m = float(np.max(np.abs(x))) or 1.0
    return x * (pico / m)


def _reverbera(x, dec=1.6, mezcla=0.3):
    """Cola de reverberacion sintetica (IR de ruido decayente, oscura)."""
    n_ir = int(dec * 2 * SR)
    t = np.arange(n_ir) / SR
    ir = np.random.default_rng(21).standard_normal(n_ir) * np.exp(-3 * t / dec)
    ir = _filtra(ir, 120, 3200)
    # IR con energia unitaria: la cola conserva la energia de la senal seca
    # (normalizarla al pico inflaba la reverb de los transitorios brillantes
    # como los ticks y devolvia los agudos a la mezcla)
    ir /= np.sqrt(float((ir ** 2).sum()))
    N = len(x) + n_ir - 1
    hum = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[: len(x)]
    return x + mezcla * hum


def escribe_wav(ruta, x):
    datos = np.clip(x, -1, 1)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((datos * 32767).astype("<i2").tobytes())


# ------------------------------------------------------------------- paleta
def barrido(dur=1.8):
    """Whoosh de escaneo: ruido que se abre de graves a brillos."""
    n = int(dur * SR)
    ruido = np.random.default_rng(7).standard_normal(n)
    bajo = _norm(_filtra(ruido, 80, 500))
    alto = _norm(_filtra(ruido, 700, 3500))
    t = np.linspace(0, 1, n)
    x = bajo * (1 - t) + alto * t * 0.6
    return _norm(x * _env(n, dur * 0.45, dur * 0.35))


def aire(dur=0.8):
    """Soplo suave (aparicion de un texto)."""
    n = int(dur * SR)
    ruido = np.random.default_rng(11).standard_normal(n)
    x = _filtra(ruido, 400, 2500)
    return _norm(x * _env(n, dur * 0.35, dur * 0.5))


def blip(f=880.0, dur=0.09):
    """Blip digital corto (piezas que encajan, etiquetas HUD)."""
    t = _t(dur)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)
    return _norm(x * _env(len(t), 0.005, dur * 0.7))


def tick(dur=0.035):
    """Tick de cursor (el punto ambar parpadea)."""
    n = int(dur * SR)
    ruido = np.random.default_rng(3).standard_normal(n)
    x = _filtra(ruido, 1500, 4500)
    return _norm(x * _env(n, 0.002, dur * 0.8))


def pad(dur=6.0, f0=110.0):
    """Colchon armonico calido y oscuro que respira debajo de todo.

    El vibrato va sumado a la FASE (desviacion fija ~2 Hz): multiplicarlo
    por t hacia crecer la desviacion con los segundos y llenaba el colchon
    de laterales asperos (sono estridente; feedback del dueno 2026-08-20).
    """
    t = _t(dur)
    vib = 0.4 * np.sin(2 * np.pi * 4.5 * t)
    x = np.zeros(len(t))
    for k, a in [(1, 1.0), (1.5, 0.35), (2, 0.18)]:
        x += a * np.sin(2 * np.pi * f0 * k * t + vib * k + k)
    x = _filtra(x, 50, 900)
    return _norm(x * _env(len(t), dur * 0.4, dur * 0.45))


def cuerda(f0=110.0, dur=3.5):
    """Cuerda pulsada (Karplus-Strong): acustica, calida, se apaga sola."""
    N = int(round(SR / f0))
    buf = np.random.default_rng(int(f0 * 10)).uniform(-1, 1, N)
    for _ in range(4):  # pua de fieltro: sin ataque metalico
        buf = np.convolve(buf, [0.25, 0.5, 0.25], mode="same")
    n = int(dur * SR)
    out = np.empty(n)
    j = 0
    for i in range(n):
        out[i] = buf[j]
        buf[j] = 0.9965 * 0.5 * (buf[j] + buf[(j + 1) % N])
        j = (j + 1) % N
    out = _filtra(out, 60, 2200)
    return _norm(out * _env(n, 0.004, dur * 0.45))


def subrayado(f0=280.0, f1=1100.0, dur=1.0):
    """Glissando ascendente (el subrayado se dibuja)."""
    n = int(dur * SR)
    f = f0 * (f1 / f0) ** np.linspace(0, 1, n)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    soplo = _filtra(np.random.default_rng(5).standard_normal(n), 600, 3000)
    x = x + 0.25 * _norm(soplo)
    return _norm(x * _env(n, dur * 0.15, dur * 0.4))


def sting(f0=220.0, dur=2.4):
    """Resolucion final: fundamental y quinta que se funden."""
    t = _t(dur)
    x = np.sin(2 * np.pi * f0 * t) + 0.3 * np.sin(2 * np.pi * 2 * f0 * t)
    n5 = int(0.25 * SR)
    q = np.sin(2 * np.pi * f0 * 1.5 * _t(dur - 0.25))
    x[n5:] += 0.8 * q
    x = _filtra(x, 60, 2000)
    return _norm(x * _env(len(t), 0.08, dur * 0.6))


def pulso(f0=196.0, dur=1.4):
    """Pulso grave y redondo (el punto ambar respira)."""
    t = _t(dur)
    x = np.sin(2 * np.pi * f0 * t) + 0.4 * np.sin(2 * np.pi * f0 * 0.5 * t)
    return _norm(x * _env(len(t), 0.05, dur * 0.75))


def nebulosa(dur=7.0, f0=110.0):
    """Colchon espacial y tranquilo: capas desafinadas que laten despacio
    (batido de ~0.4 Hz), un viento oscuro muy tenue y reverberacion larga.
    Todo por debajo de ~950 Hz: espacial, no estridente."""
    t = _t(dur)
    x = np.zeros(len(t))
    for f, a, fase in [(f0 * 0.5, 0.6, 0.0), (f0, 1.0, 1.0),
                       (f0 * 1.004, 0.9, 2.0), (f0 * 1.5, 0.25, 3.0)]:
        x += a * np.sin(2 * np.pi * f * t + fase)
    x *= 1 + 0.25 * np.sin(2 * np.pi * 0.13 * t + 1)  # respira muy despacio
    viento = _filtra(np.random.default_rng(9).standard_normal(len(t)),
                     150, 900)
    x += 0.15 * _norm(viento) * (1 + np.sin(2 * np.pi * 0.09 * t)) / 2
    x = _filtra(x, 45, 950)
    x = _reverbera(x, 1.8, 0.35)
    return _norm(x * _env(len(t), dur * 0.35, dur * 0.4))


PALETA = {
    "barrido": barrido,
    "aire": aire,
    "aire_largo": lambda: aire(1.6),
    "blip_grave": lambda: blip(587),
    "blip_medio": lambda: blip(740),
    "blip_agudo": lambda: blip(880),
    "blip_hud": lambda: blip(1320, 0.07),
    "tick": tick,
    "pad": pad,
    "cuerda_la2": lambda: cuerda(110.0),
    "cuerda_mi3": lambda: cuerda(164.81),
    "cuerda_la3": lambda: cuerda(220.0, 3.0),
    "nebulosa": nebulosa,
    "nebulosa_intro": lambda: nebulosa(7.4, 110),
    "nebulosa_cierre": lambda: nebulosa(6.2, 110),
    "subrayado": subrayado,
    "sting": sting,
    "pulso": pulso,
}


# ------------------------------------------------------------------- mezcla
def mezclar(total, eventos, fade_in=0.3, fade_out=(None, None)):
    """eventos: lista de (nombre, t0, dB). Devuelve el master a -6 dBFS."""
    n = int(round(total * SR))
    m = np.zeros(n)
    for nombre, t0, db in eventos:
        x = PALETA[nombre]() * 10 ** (db / 20)
        i = int(t0 * SR)
        j = min(n, i + len(x))
        if i < n:
            m[i:j] += x[: j - i]
    m = _reverbera(m, 1.4, 0.18)  # todos los eventos comparten el espacio
    m = _filtra(m, 40, 11000)  # sin retumbe ni siseo extremo
    if fade_in:
        k = int(fade_in * SR)
        m[:k] *= np.linspace(0, 1, k)
    ini, fin = fade_out
    if ini is not None:
        i, j = int(ini * SR), min(int(fin * SR), n)
        m[i:j] *= (1 + np.cos(np.linspace(0, np.pi, j - i))) / 2
        m[j:] = 0
    return _norm(m, 10 ** (-6 / 20))  # picos a -6 dBFS


# La coreografia documentada en docs/plan_contenido/marca-intro-y-cierre.md:
# los tiempos de cada evento estan alineados con esas fases.
def mezcla_intro(total):
    return mezclar(total, [
        ("barrido", 0.45, -8),      # linea de escaneo 0.5-2.3 s
        ("aire_largo", 0.60, -16),  # la reticula se enciende a su paso
        ("nebulosa_intro", 1.80, -13),  # colchon espacial del ensamblado
        ("blip_grave", 2.70, -14),  # CO
        ("blip_medio", 3.20, -13),  # DE
        ("blip_agudo", 3.70, -12),  # el punto llega
        ("tick", 4.55, -10),        # cursor parpadea x2
        ("tick", 4.95, -10),
        ("aire", 5.20, -15),        # ACADEMY aparece
        ("blip_hud", 5.75, -16),    # etiqueta HUD
        ("pulso", 7.70, -12),       # respiro: pulso del punto ambar
    ], fade_in=0.3, fade_out=(9.2, 10.1))


def mezcla_cierre(total):
    return mezclar(total, [
        ("nebulosa_cierre", 0.50, -12),  # colchon espacial: entra el wordmark
        ("aire_largo", 0.70, -16),
        ("subrayado", 2.20, -10),   # el degradado ambar->naranja se dibuja
        ("blip_grave", 3.40, -18),  # pie "Sigue explorando."
        ("tick", 5.10, -9),         # doble parpadeo firma
        ("tick", 5.90, -9),
        ("sting", 6.30, -10),       # resolucion llamativa hacia el negro
    ], fade_in=0.4, fade_out=(7.2, 8.5))


# ------------------------------------------------------------------- ffmpeg
def dur_video(ruta):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(ruta)],
        check=True, capture_output=True, text=True).stdout.strip()
    return float(out)


def aplicar(video, audio, salida):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
         "-i", str(audio), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-ar", str(SR), "-ac", "1", "-shortest", str(salida)], check=True)
    print(f"  {salida}")


def marca():
    for nombre, mezcla in (("intro", mezcla_intro), ("cierre", mezcla_cierre)):
        mp4 = MARCA / f"{nombre}.mp4"
        mudo = MARCA / f"{nombre}_mudo.mp4"
        if not mudo.exists():
            mudo.write_bytes(mp4.read_bytes())  # respaldo del original mudo
        total = dur_video(mudo)
        wav = MARCA / f"{nombre}.wav"
        escribe_wav(wav, mezcla(total))
        print(f"{nombre}: {total:.2f} s")
        aplicar(mudo, wav, mp4)


def _numpy_sano():
    """Canario contra el numpy roto del sistema (ver docstring de cabecera):
    un seno de 5 kHz tiene que salir aplastado de un pasabanda 150-900."""
    t = np.arange(177600) / SR
    y = _filtra(np.sin(2 * np.pi * 5000 * t), 150, 900)
    return float(np.sqrt((y ** 2).mean())) < 0.01


def main(argv):
    orden = argv[1] if len(argv) > 1 else "marca"
    if orden in ("marca", "paleta", "mezclar") and not _numpy_sano():
        print("ERROR: este numpy corrompe la sintesis (combo numpy/python no"
              " soportado).\nEjecuta dentro del contenedor manim:\n"
              '  docker run --rm --user $(id -u):$(id -g) -v "$PWD":/workspace'
              " \\\n    -w /workspace codeaerospace_contenido-manim"
              f" python3 studio/tools/sfx.py {orden}")
        return 2
    if orden == "marca":
        marca()
    elif orden == "paleta":
        destino = Path(argv[2]) if len(argv) > 2 else REPO / "exports" / "sfx"
        destino.mkdir(parents=True, exist_ok=True)
        for nombre, fn in PALETA.items():
            escribe_wav(destino / f"{nombre}.wav", _norm(fn(), 0.5))
        print(f"{len(PALETA)} efectos en {destino}")
    elif orden == "mezclar":
        salida, total = argv[2], float(argv[3])
        eventos = []
        for spec in argv[4:]:
            cuerpo, _, db = spec.partition(":")
            nombre, _, t0 = cuerpo.partition("@")
            eventos.append((nombre, float(t0), float(db or -12)))
        escribe_wav(salida, mezclar(total, eventos))
        print(salida)
    elif orden == "aplicar":
        video, audio = Path(argv[2]), Path(argv[3])
        salida = Path(argv[4]) if len(argv) > 4 else video.with_name(
            video.stem + "_sfx.mp4")
        aplicar(video, audio, salida)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

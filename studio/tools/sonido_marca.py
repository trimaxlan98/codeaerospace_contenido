#!/usr/bin/env python3
"""Banda sonora sintética de los videos de la marca Co.De Aerospace (sin muestras ni red).

Cada sonido se sincroniza con los eventos de `marca_aerospace.animar_entrada` (tiempos medidos en el
video: órbitas 0–2.4 s, paneles y letras 2.4–4.6 s, punto y AEROSPACE 4.6–5.95 s, destello 5.95–6.85 s).
Paleta: pentatónica de La (A C# E F# A) — un pulso por órbita —, whooshes de ruido filtrado,
clics mecánicos para los paneles, golpe grave para el punto y un acorde final A add9.

Uso:  python3 sonido_marca.py [carpeta_videos]      (por defecto exports/marca-codeaerospace)
Salida: <carpeta>/con_sonido/<Video>.mp4 (el video se copia sin recodificar) y <Video>.wav.
Los originales no se tocan. Determinista (semilla fija).
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
RNG = np.random.default_rng(7)
A = lambda n: 440.0 * 2 ** ((n) / 12)          # n = semitonos sobre La4
PENTA = [A(x) for x in (0, 2, 4, 7, 9, 12)]    # A B C# E F# A


class Mezcla:
    def __init__(self, dur):
        self.n = int((dur + 0.5) * SR)
        self.buf = np.zeros((self.n, 2))
        self.dur = dur

    def poner(self, t, x, vol=1.0, pan=0.0):
        i = int(t * SR)
        if i >= self.n:
            return
        x = x[: self.n - i]
        ang = (pan + 1) * np.pi / 4
        self.buf[i:i + len(x), 0] += x * vol * np.cos(ang)
        self.buf[i:i + len(x), 1] += x * vol * np.sin(ang)


def tt(d):
    return np.arange(int(d * SR)) / SR


def env(d, a=0.005, r=None, curva=3.0):
    t = tt(d)
    r = d - a if r is None else r
    e = np.minimum(t / max(a, 1e-4), 1.0) * np.exp(-curva * np.clip(t - a, 0, None) / max(r, 1e-3))
    return e * np.minimum((d - t) / 0.02, 1.0)


def pluck(f, d=1.2, vol=1.0, brillo=0.35):
    """Campana suave: fundamental + armónicos inarmónicos leves, ataque de 3 ms."""
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-6 * t) \
        + brillo * 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-9 * t)
    return x * env(d, 0.003, d * 0.35, 4.5) * vol


def ruido_filtrado(d, f0, f1, q=0.5):
    """Ruido blanco pasado por una banda cuya frecuencia central barre f0→f1 (por bloques FFT)."""
    n = int(d * SR)
    w = RNG.standard_normal(n)
    out = np.zeros(n)
    bloque = 2048
    ventana = np.hanning(bloque)
    for k, i in enumerate(range(0, n - bloque, bloque // 2)):
        c = f0 * (f1 / f0) ** (i / n)
        f = np.fft.rfftfreq(bloque, 1 / SR)
        g = np.exp(-0.5 * (np.log2(np.maximum(f, 1) / c) / q) ** 2)
        seg = np.fft.irfft(np.fft.rfft(w[i:i + bloque] * ventana) * g)
        out[i:i + bloque] += seg * ventana
    return out / (np.abs(out).max() + 1e-9)


def whoosh(d, f0, f1, vol=1.0, pico=0.5, q=0.55):
    x = ruido_filtrado(d, f0, f1, q)
    t = tt(d) / d
    e = np.sin(np.pi * np.clip(t / (2 * pico) if False else t, 0, 1)) ** 2
    e = np.where(t < pico, (t / pico) ** 1.6, ((1 - t) / (1 - pico)) ** 1.6)
    return x * e * vol


def glide(f0, f1, d, vol=1.0):
    t = tt(d)
    f = f0 * (f1 / f0) ** (t / d)
    fase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(fase) * env(d, 0.01, d * 0.5, 3.0) * vol


def clic(vol=1.0, f=2400):
    d = 0.06
    t = tt(d)
    x = RNG.standard_normal(len(t)) * np.exp(-t * 90)
    x = x - np.convolve(x, np.ones(6) / 6, "same")           # filtro pasaaltas simple
    return (x * 0.8 + np.sin(2 * np.pi * f * t) * np.exp(-t * 120) * 0.5) * vol


def servo(d, f0, f1, vol=1.0):
    t = tt(d)
    f = f0 + (f1 - f0) * (t / d)
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sign(np.sin(fase)) * 0.3 + np.sin(fase)) * (0.7 + 0.3 * np.sin(2 * np.pi * 38 * t))
    return x * env(d, 0.04, d * 0.6, 1.5) * vol * 0.4


def golpe(f=62, d=0.7, vol=1.0):
    t = tt(d)
    fase = 2 * np.pi * np.cumsum(f * (1 + 1.6 * np.exp(-t * 30))) / SR
    return np.sin(fase) * np.exp(-t * 7) * np.minimum(t / 0.004, 1) * vol


def gota(f=330, d=0.35, vol=1.0):
    t = tt(d)
    fase = 2 * np.pi * np.cumsum(f * (1 + 0.5 * np.exp(-t * 40))) / SR
    return np.sin(fase) * np.exp(-t * 14) * vol


def pad(d, notas, vol=1.0, ataque=0.9, cola=1.2):
    t = tt(d)
    x = np.zeros_like(t)
    for k, f in enumerate(notas):
        for det in (-0.07, 0.07):
            x += np.sin(2 * np.pi * (f * (1 + det * 0.01 * (k + 1))) * t + k)
    e = np.minimum(t / ataque, 1) * np.minimum((d - t) / cola, 1)
    return x / (len(notas) * 2) * e ** 2 * vol


def acorde(vol=1.0, d=2.6):
    """A add9: La, Mi, Do#, Si arriba; campanas escalonadas."""
    out = np.zeros(int(d * SR))
    for k, n in enumerate((-12, 0, 4, 7, 14)):
        p = pluck(A(n), d - k * 0.05, vol * (0.9 - 0.1 * k), 0.5)
        out[int(k * 0.05 * SR):int(k * 0.05 * SR) + len(p)] += p
    return out * vol


def brillo(d, vol=1.0):
    """Centelleo agudo del destello: campanitas aleatorias en la pentatónica alta."""
    out = np.zeros(int(d * SR))
    for k in range(int(d * 14)):
        i = int(RNG.uniform(0, d - 0.25) * SR)
        p = pluck(A(int(RNG.choice([12, 14, 16, 19, 21, 24]))), 0.25, 0.08 * RNG.uniform(.5, 1))
        out[i:i + len(p)] += p
    return out * vol


def fondo(m, t0, t1, vol=0.5, notas=(A(-24), A(-17), A(-12))):
    m.poner(t0, pad(t1 - t0, notas, vol, ataque=min(1.0, (t1 - t0) / 3), cola=min(1.4, (t1 - t0) / 3)))


# ---- guiones de cada video -------------------------------------------------------------------------

def intro(m):
    fondo(m, 0.0, m.dur, 0.5)
    m.poner(0.0, golpe(55, 1.2, 0.35))
    for i in range(6):                                  # una órbita = una nota, con cometa
        t0 = 0.24 * i
        m.poner(t0, whoosh(0.9, 500 + 300 * i, 3500 + 500 * i, 0.16), pan=-0.7 + 0.28 * i)
        m.poner(t0 + 0.55, pluck(PENTA[i], 1.5, 0.30), pan=-0.5 + 0.2 * i)
    m.poner(0.35, glide(300, 900, 1.9, 0.07), pan=-0.6)                      # luna sube
    m.poner(2.25, pluck(A(16), 1.6, 0.30), pan=-0.5)                          # luna llega
    m.poner(0.6, glide(500, 1300, 1.7, 0.06), pan=0.6)                        # satélite plegado
    m.poner(2.3, pluck(A(19), 1.6, 0.30), pan=0.55)                           # satélite llega
    m.poner(2.5, servo(1.1, 180, 520, 0.8), pan=0.4)                          # paneles
    m.poner(2.55, clic(0.6), pan=0.3)
    m.poner(3.55, clic(0.5), pan=0.3)
    m.poner(2.45, whoosh(1.9, 300, 4200, 0.12))                               # trazo de CO.DE
    for k, n in enumerate((0, 4, 7, 12)):                                    # C·O·D·E
        m.poner(3.6 + 0.26 * k, pluck(A(n - 12), 0.9, 0.34), pan=-0.3 + 0.2 * k)
    for k, tb in enumerate((4.93, 5.26, 5.42, 5.47)):                        # el punto rebota
        m.poner(tb, gota(380 + 30 * k, 0.3, 0.55 * 0.6 ** k), pan=0.0)
    m.poner(4.93, golpe(60, 0.7, 0.55))
    m.poner(4.85, whoosh(1.15, 600, 6500, 0.2, 0.7))                          # AEROSPACE se abre
    m.poner(5.95, whoosh(0.9, 800, 9000, 0.22, 0.75), pan=0.0)               # destello
    m.poner(5.95, brillo(1.0, 1.0), pan=0.2)
    m.poner(6.0, acorde(0.55, m.dur - 6.0 + 0.4))
    m.poner(6.0, golpe(55, 1.5, 0.4))


def trazo(m, dur_anim=2.6, t0=0.0, partes=13, lag=0.08, ruta_final=True):
    paso = dur_anim / (1 + (partes - 1) * lag) * lag
    d = dur_anim / (1 + (partes - 1) * lag)
    m.poner(t0, whoosh(dur_anim, 350, 5000, 0.14, 0.65))
    for i in range(partes):
        n = [0, 2, 4, 7, 9, 12][i % 6]
        m.poner(t0 + paso * i + d * 0.35, pluck(A(n), 0.9, 0.22), pan=-0.6 + 1.2 * (i / max(partes - 1, 1)))
    if ruta_final:
        m.poner(t0 + dur_anim, acorde(0.5, 2.0))
        m.poner(t0 + dur_anim, brillo(0.7, 0.8))


def ensamble(m):
    fondo(m, 0, m.dur, 0.4)
    dirs = [-0.8, 0.8, 0.0, -0.4, 0.0, 0.4, 0.0]
    for i in range(7):
        t0 = 0.2 * i
        m.poner(t0, whoosh(0.8, 600, 2500, 0.12), pan=dirs[i])
        m.poner(t0 + 0.9, clic(0.8), pan=dirs[i])                   # encaja
        m.poner(t0 + 0.9, golpe(80 + 8 * i, 0.3, 0.3))
        m.poner(t0 + 0.92, pluck(PENTA[i % 6], 1.0, 0.22), pan=dirs[i])
    m.poner(2.4, acorde(0.55, 2.0))
    m.poner(2.4, golpe(55, 1.2, 0.35))


def sting(m):
    m.poner(0.0, golpe(55, 1.0, 0.45))
    m.poner(0.0, whoosh(0.7, 400, 5000, 0.2, 0.8))
    m.poner(0.55, brillo(1.0, 0.9))
    m.poner(0.6, whoosh(1.0, 900, 9000, 0.15, 0.7))
    m.poner(0.6, acorde(0.6, 1.4))


def cierre(m):
    fondo(m, 0, m.dur, 0.4)
    trazo(m, 2.08, 0.0, 13, 0.08, ruta_final=True)
    m.poner(2.1, pluck(A(12), 0.9, 0.25), pan=0.0)                  # aparece codeaerospace.com
    m.poner(2.1, whoosh(0.7, 2000, 5000, 0.07))
    m.poner(4.38, whoosh(1.2, 6000, 400, 0.18, 0.4))                # salida, barrido hacia abajo
    for k, n in enumerate((12, 9, 7, 4, 0)):
        m.poner(4.4 + 0.17 * k, pluck(A(n), 0.8, 0.16), pan=0.3 - 0.15 * k)


def rotulos(m):
    fondo(m, 0, m.dur, 0.4)
    # Portada: la regla se dibuja con cometa, el título sube y el subtítulo aparece
    m.poner(0.0, golpe(55, 1.2, 0.3))
    m.poner(0.05, whoosh(0.95, 600, 4500, 0.16, 0.6), pan=-0.4)
    m.poner(0.15, pluck(A(-12), 1.2, 0.26), pan=-0.2)
    m.poner(0.45, pluck(A(0), 1.0, 0.2), pan=0.0)
    m.poner(0.9, pluck(A(12), 1.4, 0.24), pan=0.4)                 # punto al final de la regla
    # Tercio inferior entra y sale
    m.poner(2.3, whoosh(0.8, 500, 3000, 0.14, 0.6), pan=-0.5)
    m.poner(2.9, clic(0.5), pan=-0.5)
    m.poner(2.95, pluck(A(7), 1.3, 0.24), pan=-0.4)
    m.poner(4.5, whoosh(0.5, 3000, 600, 0.1, 0.4), pan=-0.5)
    # Cortinilla orbital: el satélite cruza de izquierda a derecha
    m.poner(5.0, whoosh(1.3, 250, 3800, 0.26, 0.55), pan=0.0)
    m.poner(5.0, glide(260, 1500, 1.2, 0.07), pan=0.5)
    m.poner(5.65, brillo(0.6, 0.6), pan=0.3)
    m.poner(5.95, pluck(A(14), 1.2, 0.22), pan=0.3)
    # Capítulo: numeral, regla con cometa, título
    for k in range(4):
        m.poner(6.3 + 0.1 * k, clic(0.25), pan=-0.3)
    m.poner(6.3, pluck(A(-5), 1.4, 0.3), pan=-0.3)
    m.poner(6.55, whoosh(0.65, 700, 4500, 0.14, 0.6), pan=0.0)
    m.poner(7.2, pluck(A(9), 1.3, 0.24), pan=0.3)
    m.poner(8.3, whoosh(0.5, 2500, 500, 0.08, 0.4))
    # Cierre de marca (logo en trazo, sitio, salida)
    trazo(m, 2.08, 8.8, 13, 0.08, ruta_final=True)
    m.poner(10.9, whoosh(0.8, 1500, 5000, 0.07), pan=0.0)
    m.poner(10.95, pluck(A(12), 1.0, 0.24), pan=0.0)
    m.poner(13.0, whoosh(1.2, 6000, 400, 0.18, 0.4))
    for k, n in enumerate((12, 9, 7, 4, 0)):
        m.poner(13.0 + 0.15 * k, pluck(A(n), 0.8, 0.15), pan=0.3 - 0.15 * k)


def marca_de_agua(m):
    """El satélite da una vuelta por la elipse en 4 s: un tono suave que viaja de lado a lado (pan y
    brillo siguen su posición), sin remate para que el bucle empalme."""
    fondo(m, 0, m.dur, 0.3)
    t = tt(m.dur)
    ang = 2 * np.pi * t / 4.0                                   # 0 = derecha, antihorario
    x, y = np.cos(ang), np.sin(ang)                             # y>0 arriba: más agudo y más lejos
    f = 440 * (1 + 0.06 * y)
    tono = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    tono *= 0.10 * (1 + 0.25 * np.sin(2 * np.pi * 6 * t)) * (0.8 + 0.2 * np.cos(ang))
    pos = (x + 1) * np.pi / 4
    m.buf[: len(t), 0] += tono * np.cos(pos)
    m.buf[: len(t), 1] += tono * np.sin(pos)
    estela = ruido_filtrado(m.dur, 1500, 1500, 0.8) * 0.05 * (0.6 + 0.4 * y)
    m.buf[: len(t), 0] += estela * np.cos(pos)
    m.buf[: len(t), 1] += estela * np.sin(pos)
    m.poner(0.0, pluck(A(12), 1.2, 0.15), pan=1.0)               # arranque: el satélite en la derecha


ESCENAS = {
    "LogoCoDeIntro": intro, "LogoCoDeIntroClaro": intro, "LogoCoDeVertical": intro,
    "LogoCoDeTrazo": lambda m: (fondo(m, 0, m.dur, 0.4), trazo(m)),
    "LogoCoDeEnsamble": ensamble, "LogoCoDeMarcaDeAgua": marca_de_agua, "RotulosAerospace": rotulos, "LogoCoDeSting": sting, "LogoCoDeCierre": cierre,
}


# ---- reels verticales (mismos tiempos + las órbitas gigantes del fondo y el sitio al final) ------------

def orbitas_gigantes(m):
    """Tres órbitas de pantalla completa que se dibujan con cometa en 0, 0.5 y 1.0 s (2 s cada una)."""
    for k, pan in enumerate((-0.6, 0.6, 0.0)):
        m.poner(0.5 * k, whoosh(2.0, 250 + 100 * k, 2200 + 600 * k, 0.09, 0.5, 0.6), pan=pan)
        m.poner(0.5 * k + 1.9, pluck(PENTA[k] / 2, 1.8, 0.10), pan=pan)


def reel_intro(m):
    orbitas_gigantes(m)
    intro(m)
    m.poner(6.95, pluck(A(12), 1.2, 0.2))              # aparece el sitio


def reel_trazo(m):
    orbitas_gigantes(m)
    fondo(m, 0, m.dur, 0.4)
    trazo(m)


def reel_ensamble(m):
    orbitas_gigantes(m)
    ensamble(m)


def reel_sting(m):
    sting(m)


def reel_cierre(m):
    orbitas_gigantes(m)
    cierre(m)


def reel_rotulos(m):
    orbitas_gigantes(m)
    rotulos(m)


ESCENAS_V = {
    "ReelIntro": reel_intro, "ReelIntroClaro": reel_intro, "ReelTrazo": reel_trazo,
    "ReelEnsamble": reel_ensamble, "ReelSting": reel_sting, "ReelCierre": reel_cierre,
    "ReelMarcaDeAgua": marca_de_agua, "ReelRotulos": reel_rotulos,
}


def logo_entorno(m):
    """Logo sobre un entorno espacial: la entrada orbital y el sitio, sin las órbitas gigantes."""
    intro(m)
    m.poner(6.95, pluck(A(12), 1.2, 0.2))


ESCENAS_LE = {f"LogoEntorno{t}": logo_entorno for t in
              ("Orbita", "Nebulosa", "Mision", "Marte", "Lunar", "Solar", "Espectro", "Lanzamiento", "Fisica", "Caos")}


def duracion(mp4):
    s = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(mp4)], text=True)
    return float(s)


def master(buf, dur):
    buf = buf[: int(dur * SR)].copy()
    # Reverb corta (ecos difusos) para pegar los sonidos
    for ret, g in ((0.043, 0.22), (0.071, 0.16), (0.113, 0.11), (0.167, 0.07)):
        i = int(ret * SR)
        buf[i:] += buf[:-i][:, ::-1] * g
    buf *= np.minimum((dur - np.arange(len(buf)) / SR) / 0.25, 1.0)[:, None].clip(0, 1)  # salida suave
    buf = np.tanh(buf * 1.1)
    buf *= 10 ** (-1.5 / 20) / (np.abs(buf).max() + 1e-9)
    return buf


def escribir_wav(ruta, x):
    pcm = (x * 32767).astype("<i2")
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "exports/marca-codeaerospace"
    for sub, escenas in ((carpeta, ESCENAS), (carpeta / "vertical", ESCENAS_V),
                         (carpeta.parent / "estudio" / "logo_entornos" / "animados", ESCENAS_LE)):
        if sub.exists():
            mezclar(sub, escenas)


def mezclar(carpeta, escenas):
    salida = carpeta / "con_sonido"
    salida.mkdir(exist_ok=True)
    for nombre, f in escenas.items():
        mp4 = carpeta / f"{nombre}.mp4"
        if not mp4.exists():
            continue
        import zlib
        global RNG
        RNG = np.random.default_rng(zlib.crc32(nombre.encode()))   # una semilla por escena: determinista
        dur = duracion(mp4)
        m = Mezcla(dur)
        f(m)
        wav = salida / f"{nombre}.wav"
        escribir_wav(wav, master(m.buf, dur))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                        "-af", "loudnorm=I=-17:TP=-3:LRA=7,alimiter=limit=0.7:level=disabled", "-ar", "48000", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(salida / f"{nombre}.mp4")], check=True)
        print("ok", nombre, f"{dur:.2f}s")


if __name__ == "__main__":
    main()

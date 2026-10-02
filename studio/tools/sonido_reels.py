#!/usr/bin/env python3
"""Audio en LOOP SIN COSTURA de los reels promocionales (33-reels-promo.py).

Todo se compone en una línea de tiempo CIRCULAR de duración exacta T: las colas de los sonidos que pasan
del final se enrollan al principio, el colchón usa frecuencias de ciclo entero y no hay acorde final ni
fundido de salida; el audio de 12.000 s empalma consigo mismo. Cada reel declara su `desfase` (la fase
del ciclo en que empieza el video) y el audio se rota igual.

Uso:  python3 sonido_reels.py [carpeta]   (por defecto exports/marca-codeaerospace/reels-promo)
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

import sonido_marca as sm
from sonido_marca import A, PENTA, SR, clic, glide, golpe, pluck, tt, whoosh

RNG = np.random.default_rng(3)


class Circular:
    def __init__(self, T):
        self.T, self.n = T, int(round(T * SR))
        self.buf = np.zeros((self.n, 2))

    def poner(self, t, x, vol=1.0, pan=0.0):
        i = int(round((t % self.T) * SR)) % self.n
        ang = (pan + 1) * np.pi / 4
        x = np.asarray(x)[: self.n]
        primero = min(len(x), self.n - i)
        for dst, src in ((slice(i, i + primero), x[:primero]), (slice(0, len(x) - primero), x[primero:])):
            self.buf[dst, 0] += src * vol * np.cos(ang)
            self.buf[dst, 1] += src * vol * np.sin(ang)

    def sumar(self, x, vol=1.0):
        self.buf += np.asarray(x)[:, None] * vol


def ciclo_entero(f, T):
    return round(f * T) / T


def colchon(m, notas=(A(-24), A(-17), A(-12)), vol=0.3):
    """Pad continuo: frecuencias de ciclo entero y oscilación lenta de 1 ciclo por T → empalma exacto."""
    t = np.arange(m.n) / SR
    x = np.zeros(m.n)
    for k, f in enumerate(notas):
        f = ciclo_entero(f, m.T)
        for det in (-1.0, 1.0):
            x += np.sin(2 * np.pi * (f + det * (k + 1) / m.T) * t + k)   # desafinación de ciclos enteros: empalma exacto
    x /= len(notas) * 2
    m.sumar(x * (0.85 + 0.15 * np.sin(2 * np.pi * t / m.T)), vol)


def ruido_circular(m, lo, hi, vol, mod=None):
    w = np.fft.rfft(RNG.standard_normal(m.n))
    f = np.fft.rfftfreq(m.n, 1 / SR)
    w *= np.exp(-0.5 * (np.log2(np.maximum(f, 1) / np.sqrt(lo * hi)) / (np.log2(hi / lo) / 2)) ** 2)
    x = np.fft.irfft(w, m.n)
    x /= np.abs(x).max()
    t = np.arange(m.n) / SR
    m.sumar(x * (mod(t) if mod else 1.0), vol)


def doppler_d(tau, T=12.0):
    return -0.27 * np.tanh((tau - T / 2) / (0.11 * T))


def doppler_amp(tau, T=12.0):
    return np.exp(-((tau - T / 2) / (0.27 * T)) ** 2)


# ── 1 · La cascada ───────────────────────────────────────────────────────────────────────────────

def cascada(m):
    T = m.T
    t = np.arange(m.n) / SR
    colchon(m, vol=0.28)
    amp = doppler_amp(t, T)
    f = 740 + 330 * doppler_d(t, T) / 0.27                       # el tono baja como el Doppler
    fase = 2 * np.pi * np.cumsum(f) / SR
    m.sumar((np.sin(fase) + 0.3 * np.sin(2 * fase)) * amp * 0.13)
    ruido_circular(m, 700, 3800, 0.05, lambda tt_: 0.5 + 0.5 * doppler_amp(tt_, T))
    rng = np.random.default_rng(5)
    for k in range(8):                                           # ráfagas FSK de dos tonos
        r0 = (0.17 + 0.085 * k) * T
        for j in range(int(0.32 / 0.05)):
            fr = 1500 if rng.integers(0, 2) else 2100
            d = 0.05
            seg = np.sin(2 * np.pi * fr * tt(d)) * sm.env(d, 0.004, d * 0.6, 2.0)
            m.poner(r0 + j * d, seg, 0.045 * doppler_amp(r0, T) ** 0.5, pan=0.3)
    for i in range(4):                                           # cada leyenda nueva
        m.poner(3 * i - 1.5 + 0.25, pluck(PENTA[i], 1.4, 0.26), pan=(-1) ** i * 0.3)


# ── 2 · ¿0.1° alcanza? ───────────────────────────────────────────────────────────────────────────

def atp(m):
    T = m.T
    t = np.arange(m.n) / SR
    colchon(m, vol=0.26)
    ruido_circular(m, 500, 2500, 0.03)
    # Servo de la montura: grave constante al seguir; sube y baja en el reposicionamiento (11–12 s).
    campana = np.where(t >= 11, np.sin(np.pi * np.clip(t - 11, 0, 1)) ** 2, 0.0)
    f = 120 + 520 * campana
    fase = 2 * np.pi * np.cumsum(f) / SR
    servo = (np.sign(np.sin(fase)) * 0.25 + np.sin(fase)) * (0.7 + 0.3 * np.sin(2 * np.pi * 31 * t))
    m.sumar(servo * (0.05 + 0.10 * campana) * (np.where(t < 10.6, 1.0, 0.0) + np.where(t >= 10.6, 1.0, 0.0)))
    m.poner(11.0, whoosh(1.0, 5500, 600, 0.10, 0.4), pan=0.0)
    for i, a in enumerate((11.5, 2.2, 4.4, 6.6, 8.8)):          # cambio de controlador
        m.poner(a + 0.1, pluck(PENTA[i % 5], 1.3, 0.28), pan=-0.4 + 0.2 * i)
        m.poner(a + 0.1, clic(0.5))
    for k in range(6):                                           # tic del haz alineándose
        m.poner(1.0 + 1.9 * k, glide(1200, 1800, 0.12, 0.035), pan=0.5)


# ── 7 · El modelo ────────────────────────────────────────────────────────────────────────────────

def modelo(m):
    colchon(m, notas=(A(-24), A(-17), A(-12), A(-8)), vol=0.30)
    ruido_circular(m, 900, 5000, 0.025)
    notas = (A(0), A(7), A(4))                                   # La → Mi → Do# → (vuelve a La)
    for i, n in enumerate(notas):
        t0 = 4.0 * i
        m.poner(t0, pluck(n, 2.4, 0.34), pan=(-0.4, 0.4, -0.2)[i])
        m.poner(t0, golpe(58, 0.9, 0.4))
        m.poner(t0 + 0.6, sm.brillo(1.0, 0.7))
        m.poner(t0 + 0.4, whoosh(3.4, 300, 3200, 0.11, 0.7), pan=(0.4, -0.5, 0.0)[i])   # el pulso recorre el anillo
        m.poner(t0 - 2 + 0.25, pluck(PENTA[i] / 2, 1.2, 0.12), pan=0.0)                  # leyenda nueva


# ── Logo vivo (35-logo-vivo.py): destellos por las 6 órbitas, uno cada T/6, y la luna que late ─────────

def logo_vivo(m):
    T = m.T
    t = np.arange(m.n) / SR
    colchon(m, notas=(A(-24), A(-12), A(-5)), vol=0.30)
    ruido_circular(m, 1500, 6000, 0.018)
    latido = (1 - np.cos(4 * np.pi * t / T)) / 2                     # 2 latidos por periodo, como la luna
    m.sumar(np.sin(2 * np.pi * ciclo_entero(A(-17), T) * t) * latido * 0.05)
    notas = (0, 4, 7, 9, 12, 7)                                      # una nota por destello (pentatónica)
    for turno in range(6):
        t0 = turno * T / 6
        m.poner(t0 + 0.05, pluck(A(notas[turno]), 1.6, 0.20), pan=(-0.5, 0.5)[turno % 2])
        m.poner(t0, whoosh(0.32 * T, 1800, 5200, 0.035, 0.45), pan=(-0.5, 0.5)[turno % 2])


REELS_VIVO = {f"LogoVivo{t}": (logo_vivo, 8.0, 0.0) for t in ("Orbita", "Nebulosa", "Marte", "Lunar", "Fisica", "Espectro")}

REELS = {
    "ReelOrbitEye": (cascada, 12.0, 0.0),
    "ReelATP": (atp, 12.0, 4.0),
    "ReelModelo": (modelo, 12.0, 0.0),
}


def master(m, desfase):
    b = m.buf
    n = len(b)
    for ret, g in ((0.043, 0.22), (0.071, 0.16), (0.113, 0.11), (0.167, 0.07)):    # reverb circular
        b = b + np.roll(b[:, ::-1], int(ret * SR), axis=0) * g
    b = np.roll(b, -int(round(desfase * SR)), axis=0)                              # fase inicial del video
    b *= 10 ** (-19 / 20) / (np.sqrt((b ** 2).mean()) + 1e-9)                      # ≈ -17 LUFS
    b = np.tanh(b * 1.2) / np.tanh(1.2)
    return b * 10 ** (-1.5 / 20) / max(np.abs(b).max(), 1e-9)


def main():
    raiz = Path(__file__).resolve().parents[2] / "exports"
    grupos = [(raiz / "marca-codeaerospace/reels-promo", REELS), (raiz / "estudio/logo_vivo", REELS_VIVO)]
    if len(sys.argv) > 1:
        grupos = [(Path(sys.argv[1]), {**REELS, **REELS_VIVO})]
    for carpeta, reels in grupos:
        if carpeta.exists():
            mezclar(carpeta, reels)


def mezclar(carpeta, reels):
    salida = carpeta / "con_sonido"
    salida.mkdir(exist_ok=True)
    for nombre, (f, T, desfase) in reels.items():
        mp4 = carpeta / f"{nombre}.mp4"
        if not mp4.exists():
            continue
        import zlib
        global RNG
        semilla = zlib.crc32(nombre.encode())          # una semilla por reel: el audio no depende de cuáles existan
        RNG = np.random.default_rng(semilla)
        sm.RNG = np.random.default_rng(semilla + 1)
        m = Circular(T)
        f(m)
        x = master(m, desfase)
        wav = salida / f"{nombre}.wav"
        sm.escribir_wav(wav, x)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                        str(salida / f"{nombre}.mp4")], check=True)
        print("ok", nombre, f"{len(x) / SR:.3f}s", "costura:", f"{np.abs(x[0] - x[-1]).max():.4f}")


if __name__ == "__main__":
    main()

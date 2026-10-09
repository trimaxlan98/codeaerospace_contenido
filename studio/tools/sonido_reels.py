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
from sonido_marca import A, PENTA, SR, clic, glide, golpe, gota, pluck, servo, tt, whoosh

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


# ── Doppler real (36-reel-datos-reales.py): el tono sigue la curva S REAL del pase de la ISS ───────────

def doppler_real(m):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "content/manim_extensions"))
    from datos_orbitales.ejemplos import pase_estrella
    e = pase_estrella()
    d = e["doppler"]
    u_d = d["t"] / d["t"][-1]
    T = m.T
    t = np.arange(m.n) / SR
    u = t / T                                                        # tiempo de fase (el video empieza en `desfase`)
    df = np.interp(u, u_d, d["df"] / 1e3)                            # kHz, + al acercarse
    suave = lambda v: np.clip(v, 0, 1) ** 2 * (3 - 2 * np.clip(v, 0, 1))
    env = np.minimum(suave(u / 0.07), suave((1 - u) / 0.07))        # el pase aparece y desaparece (empalme limpio)
    colchon(m, notas=(A(-24), A(-17), A(-12)), vol=0.26)
    ruido_circular(m, 800, 4000, 0.03 * 1.0, lambda tt_: 0.6 + 0.4 * np.interp(tt_ / T, u_d, np.abs(d["df"]) / np.abs(d["df"]).max()))
    f = 900 + 70 * df                                                # 207…1593 Hz: baja como el Doppler
    fase = 2 * np.pi * np.cumsum(f) / SR
    m.sumar((np.sin(fase) + 0.25 * np.sin(2 * fase)) * env * 0.12)
    m.poner(e["t_cruce_s"] / d["t"][-1] * T, pluck(A(12), 1.4, 0.22))        # cruce por cero: el punto más cercano
    m.poner(0.0, pluck(A(0), 1.2, 0.12))



# ── Divulgación (37-reels-divulgacion.py), ronda 5: título → cuerpo → logo → disolución al inicio ──────────────
# Cada función recibe un Circular de duración V = H0 + TB + 5.0. Los eventos del cuerpo se desplazan H0 (el reloj de la
# escena vale 0 durante el título); el cierre usa el sonido de marca (`trazo`) y una cola que se funde con el inicio.

def _fisica():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "content/manim_extensions"))
    import divulgacion_fisica as F
    return F


class _Cuerpo:
    """Vista del Circular con el tiempo del cuerpo (suma H0 a cada instante)."""

    def __init__(self, m, F):
        self.m, self.F, self.T, self.n = m, F, m.T, m.n

    def poner(self, t, x, vol=1.0, pan=0.0):
        self.m.poner(self.F.H0 + t, x, vol, pan)

    def sumar(self, x, vol=1.0):
        self.m.sumar(x, vol)


def _ventana_cuerpo(m, F, tb, borde=0.4):
    """Envolvente 0→1→0 que vale 1 mientras dura el cuerpo (sobre la línea de tiempo de todo el video)."""
    t = np.arange(m.n) / SR
    a, b = F.H0, F.H0 + tb
    return np.clip((t - a) / borde, 0, 1) * np.clip((b - t) / borde, 0, 1)


def _cierre_sonoro(m, F, tb):
    """Logo: el fondo Órbita entra con un barrido, el trazo suena nota a nota y el acorde se apaga al disolverse."""
    a = F.H0 + tb
    m.poner(a, whoosh(F.LOGO_FADE_IN + 0.3, 300, 2600, 0.10, 0.6), pan=0.0)
    m.poner(a, golpe(52, 1.2, 0.30))
    sm.trazo(m, F.LOGO_ANIM, t0=a + F.LOGO_RETRASO, partes=13, lag=0.08, ruta_final=True)
    m.poner(a + F.LOGO_RETRASO + F.LOGO_ANIM + 0.5, pluck(A(12), 1.4, 0.22), pan=0.0)         # aparece el sitio
    m.poner(m.T - F.LOGO_FADE_OUT, whoosh(F.LOGO_FADE_OUT, 2400, 500, 0.06, 0.4))               # se disuelve en el título


def _leyendas(mc, F, nombre, vol=0.11):
    for i, t0 in enumerate(F.leyendas(nombre)):
        mc.poner(t0 + 0.2, pluck(PENTA[i % 5], 1.3, vol), pan=(-0.3, 0.3)[i % 2])


def _base(m, F, nombre, notas=(A(-24), A(-17), A(-12)), vol=0.26, ruido=(900, 4500, 0.02)):
    colchon(m, notas=notas, vol=vol)
    ruido_circular(m, ruido[0], ruido[1], ruido[2])
    return _Cuerpo(m, F), F.CUERPO[nombre]


def no_se_cae(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelNoSeCae", ruido=(600, 3000, 0.02))
    for i, (k, t0, dur) in enumerate(F.NEWTON_PLAN):
        mc.poner(t0, golpe(70, 0.5, 0.35))                                  # el cañonazo
        mc.poner(t0, whoosh(min(dur, 1.6), 900, 2600 + 900 * i, 0.07, 0.3), pan=0.3)
        if k < 1:
            mc.poner(t0 + dur, gota(220 - 30 * i, 0.4, 0.25), pan=0.2 * i)  # cae al suelo
        else:                                                               # entra en órbita: una nota que no termina
            mc.poner(t0 + 0.2, pluck(A(12), 2.0, 0.26))
            t = np.arange(m.n) / SR
            ini, fin = F.H0 + t0, F.H0 + tb
            env = np.clip((t - ini) / 0.8, 0, 1) * np.clip((fin - t) / 0.8, 0, 1)
            f = ciclo_entero(A(7), m.T)
            m.sumar(np.sin(2 * np.pi * f * t) * env * (0.7 + 0.3 * np.sin(2 * np.pi * 3 * t / m.T * 10)) * 0.05)
    _leyendas(mc, F, "ReelNoSeCae")
    _cierre_sonoro(m, F, tb)


def tres_alturas(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelTresAlturas", (A(-24), A(-19), A(-12)), ruido=(1200, 5000, 0.015))
    for j in range(int(tb / (F.ALT_T / 15)) + 1):                           # LEO: un tic por vuelta
        mc.poner(j * F.ALT_T / 15, clic(0.16, 3200), pan=0.35)
    for j in range(int(tb / (F.ALT_T / 2)) + 1):
        mc.poner(j * F.ALT_T / 2, pluck(A(4), 1.4, 0.15), pan=-0.3)
    for j in range(int(tb / F.ALT_T) + 1):
        mc.poner(j * F.ALT_T, golpe(55, 1.2, 0.28))                         # GEO: una vez por día
    _leyendas(mc, F, "ReelTresAlturas", 0.16)
    _cierre_sonoro(m, F, tb)


def hohmann(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelHohmann", (A(-24), A(-17), A(-10)), ruido=(700, 3500, 0.02))
    for i, tq in enumerate(F.HOH_QUEMAS):
        sube = i < 2
        mc.poner(tq, golpe(62 if sube else 48, 0.8, 0.35))
        mc.poner(tq, whoosh(1.1, 500 if sube else 3200, 3200 if sube else 500, 0.10, 0.35), pan=0.25)
        mc.poner(tq + 0.1, pluck(A((0, 7, 4, -5)[i]), 1.6, 0.24), pan=(-0.3, 0.3, 0.3, -0.3)[i])
    for j in range(int(F.HOH_SEG[0][1] // 1) + 2):                          # órbita baja: pulso tranquilo
        mc.poner(0.5 + j * 0.9, clic(0.07, 2200), pan=0.3)
    _leyendas(mc, F, "ReelHohmann", 0.07)
    _cierre_sonoro(m, F, tb)


def latencia(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelLatencia", (A(-24), A(-17), A(-12)), 0.24, (900, 4500, 0.0))
    ida = F.LAT_IDA
    vuelta = F.LAT_LEO_MS / 1e3 * F.LAT_LENTO                               # 0.09 s: el rebote LEO es un zumbido de tics
    for j in range(F.LAT_VIAJES + 1):
        mc.poner(ida + j * vuelta, clic(0.10, 2600 + 400 * (j % 2)), pan=-0.45)
    mc.poner(ida, pluck(A(12), 0.9, 0.22))
    mc.poner(ida, glide(700, 1400, 3.0, 0.035), pan=0.35)                   # el pulso a GEO sube…
    mc.poner(ida + 3.0, pluck(A(16), 1.2, 0.22), pan=0.35)                  # …toca el satélite…
    mc.poner(ida + 3.0, glide(1400, 700, 3.0, 0.035), pan=0.35)              # …y baja
    mc.poner(ida + 6.0, pluck(A(0), 2.2, 0.30))
    mc.poner(ida + 6.0, golpe(58, 0.9, 0.3))
    _leyendas(mc, F, "ReelLatencia")
    _cierre_sonoro(m, F, tb)


def areas_iguales(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelAreasIguales", (A(-24), A(-17), A(-12)), 0.24, (800, 4000, 0.015))
    paso = F.MOL_T / F.MOL_N
    vmin, vmax = F.MOL_VA, F.MOL_VP
    for k in range(int(tb / paso)):                                         # una nota por franja: más aguda cuanto más rápido
        r = np.linalg.norm(F.mol_pos(k * paso))
        v = F.v_visviva(r, F.MOL_A)
        n = int(round(12 * np.log2(v / vmin) / np.log2(vmax / vmin) * 2)) // 2 * 2
        mc.poner(k * paso, pluck(A(n - 5), 1.3, 0.20), pan=0.4 * np.sin(2 * np.pi * k / F.MOL_N))
    for j in range(int(tb / F.MOL_T) + 1):
        mc.poner(j * F.MOL_T, whoosh(1.2, 900, 4200, 0.07, 0.5))             # el paso por el perigeo
    _leyendas(mc, F, "ReelAreasIguales", 0.07)
    _cierre_sonoro(m, F, tb)


def ventana_contacto(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelVentanaContacto", (A(-24), A(-17), A(-12)), 0.25, (900, 4500, 0.02))
    t = np.arange(m.n) / SR
    a, b = F.H0 + F.VEN_AOS, F.H0 + F.VEN_LOS
    u = np.clip((t - a) / (b - a), 0, 1)
    env = ((t >= a) & (t <= b)).astype(float) * np.minimum(np.clip((t - a) / 0.08, 0, 1), np.clip((b - t) / 0.08, 0, 1))
    f = 1500 - 500 * np.tanh((u - 0.5) * 4)                                 # baliza con Doppler: alta al acercarse, baja al irse
    fase = 2 * np.pi * np.cumsum(f) / SR
    pulsos = (np.sin(2 * np.pi * 8 * t) > 0).astype(float)
    m.sumar(np.sin(fase) * env * pulsos * 0.07)
    m.poner(a, pluck(A(12), 1.2, 0.26), pan=-0.3)
    m.poner(b, pluck(A(7), 1.4, 0.22), pan=0.3)
    for j in range(8):                                                      # el resto de la vuelta: pulso lento
        mc.poner(0.6 + j * 1.2, clic(0.07, 1800))
    _leyendas(mc, F, "ReelVentanaContacto", 0.07)
    _cierre_sonoro(m, F, tb)


def velocidad_escape(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelVelocidadEscape", (A(-24), A(-17), A(-12)), 0.25, (900, 4500, 0.018))
    for i, (k, t0) in enumerate(F.ESC_PLAN):
        mc.poner(t0, golpe(66, 0.5, 0.3))
        if k < np.sqrt(2) - 1e-6:                                            # vuelve: nota que se cierra
            mc.poner(t0 + 0.1, pluck(A((0, 4)[i]), 2.0, 0.24), pan=(-0.3, 0.3)[i])
        else:                                                               # escapa: barrido que sube y se pierde
            mc.poner(t0, glide(500 + 200 * i, 2400 + 600 * i, F.ESC_D, 0.05), pan=(0.4, -0.4)[i - 2])
            mc.poner(t0 + 0.1, pluck(A((7, 12)[i - 2]), 1.6, 0.22))
    _leyendas(mc, F, "ReelVelocidadEscape", 0.07)
    _cierre_sonoro(m, F, tb)


def cobertura(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelCobertura", (A(-24), A(-19), A(-12)), 0.25, (900, 4500, 0.0))
    t = np.arange(m.n) / SR
    tc = np.clip(t - F.H0, 0, tb)
    h = np.interp(tc, tc[::480], np.array([F.cob_altura(x) for x in tc[::480]]))
    u = np.log(h / F.COB_H[0]) / np.log(F.COB_H[1] / F.COB_H[0])             # 0 en LEO, 1 en GEO
    f = 300 + 500 * u                                                       # el tono sube con la altura
    fase = 2 * np.pi * np.cumsum(f) / SR
    m.sumar(np.sin(fase) * 0.045 * _ventana_cuerpo(m, F, tb))
    _leyendas(mc, F, "ReelCobertura", 0.16)
    _cierre_sonoro(m, F, tb)


def amaneceres(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelAmaneceres", (A(-24), A(-17), A(-12)), 0.25, (900, 4500, 0.0))
    t = np.arange(m.n) / SR
    th_s = np.arcsin(F.R_T / F.AMA_A)
    t_ocaso = F.AMA_T * (1 - 2 * th_s / (2 * np.pi))                        # fracción de la vuelta a la luz
    fase_v = np.mod(t - F.H0, F.AMA_T)
    luz = np.clip(np.minimum(fase_v / 0.6, (t_ocaso - fase_v) / 0.6), 0, 1) * _ventana_cuerpo(m, F, tb)
    ruido_circular(m, 2000, 7000, 0.035, lambda tt_: np.interp(tt_, t, luz))
    for n in range(int(tb / F.AMA_T) + 1):
        mc.poner(n * F.AMA_T, sm.brillo(1.6, 0.8))                          # amanecer
        mc.poner(n * F.AMA_T + 0.05, pluck(A(12), 2.0, 0.28))
        if n * F.AMA_T + t_ocaso < tb:
            mc.poner(n * F.AMA_T + t_ocaso, pluck(A(-5), 2.2, 0.22), pan=0.3)  # ocaso
    _leyendas(mc, F, "ReelAmaneceres", 0.07)
    _cierre_sonoro(m, F, tb)


def cohete(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelCohete", (A(-24), A(-17), A(-12)), 0.22, (900, 4500, 0.0))
    t = np.arange(m.n) / SR
    tc = t - F.H0
    llena = np.clip(1 - np.abs(tc - F.COH_LLENA / 2) / (F.COH_LLENA / 2), 0, 1)
    ruido_circular(m, 300, 1200, 0.05, lambda tt_: np.interp(tt_, t, llena))
    quema = ((tc >= F.COH_LLENA) & (tc < F.COH_QUEMA)).astype(float)
    quema = np.convolve(quema, np.ones(2400) / 2400, mode="same")
    ruido_circular(m, 60, 700, 0.22, lambda tt_: np.interp(tt_, t, quema))  # el rugido
    mc.poner(F.COH_LLENA, golpe(52, 1.0, 0.45))
    u = np.clip((tc - F.COH_LLENA) / (F.COH_QUEMA - F.COH_LLENA), 0, 1)
    fase = 2 * np.pi * np.cumsum(180 + 420 * u ** 2) / SR                   # el tono sube: cada km/s cuesta más
    m.sumar(np.sin(fase) * quema * 0.04)
    mc.poner(F.COH_QUEMA, pluck(A(12), 2.0, 0.28))
    _leyendas(mc, F, "ReelCohete", 0.07)
    _cierre_sonoro(m, F, tb)


def gravedad(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelGravedadISS", (A(-24), A(-19), A(-12)), 0.27, (900, 4000, 0.015))
    for j in range(int(tb / 3.0)):
        mc.poner(0.8 + j * 3.0, gota(330 - 40 * (j % 2), 0.5, 0.2), pan=(-0.3, 0.3)[j % 2])
    mc.poner(0.8, whoosh(1.6, 300, 1500, 0.06, 0.6))                         # las barras se llenan
    _leyendas(mc, F, "ReelGravedadISS", 0.14)
    _cierre_sonoro(m, F, tb)


def mensaje_marte(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelMensajeMarte", (A(-24), A(-17), A(-10)), 0.25, (600, 3000, 0.02))
    paso = F.MAR_T / F.MAR_PULSOS
    for j in range(int(tb / paso)):                                         # un bip por pulso; más grave cuanto más lejos
        t0 = j * paso
        f = 1400 - 700 * (F.mar_minutos(t0) - F.MAR_MIN) / (F.MAR_MAX - F.MAR_MIN)
        d = 0.09
        mc.poner(t0, np.sin(2 * np.pi * f * tt(d)) * sm.env(d, 0.004, d * 0.7, 2.0), 0.08, pan=-0.2)
    _leyendas(mc, F, "ReelMensajeMarte", 0.14)
    _cierre_sonoro(m, F, tb)


def clarke(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelClarke", (A(-24), A(-17), A(-12)), 0.26, (1500, 6000, 0.015))
    for i, t0 in enumerate(F.CLA_APARECE):                                  # entra cada satélite con su nota
        mc.poner(t0, pluck(A((0, 4, 7)[i]), 1.8, 0.22), pan=(-0.5, 0.0, 0.5)[i])
        mc.poner(t0, whoosh(0.9, 500, 2400, 0.05, 0.5), pan=(-0.5, 0.0, 0.5)[i])
    _leyendas(mc, F, "ReelClarke", 0.12)
    _cierre_sonoro(m, F, tb)


def laser_luna(m):
    F = _fisica()
    mc, tb = _base(m, F, "ReelLaserLuna", (A(-24), A(-17), A(-12)), 0.22, (900, 4500, 0.0))
    for t0 in F.LUN_DISPAROS:
        mc.poner(t0, glide(2600, 1800, 0.18, 0.08))                         # disparo
        mc.poner(t0 + F.LUN_IDA, pluck(A(12), 1.0, 0.24))                   # toca la Luna
        mc.poner(t0 + 2 * F.LUN_IDA, pluck(A(7), 1.4, 0.28))                # vuelve
        mc.poner(t0 + 2 * F.LUN_IDA, clic(0.3, 3000))
    _leyendas(mc, F, "ReelLaserLuna", 0.12)
    _cierre_sonoro(m, F, tb)


_FUNCIONES = {"ReelNoSeCae": no_se_cae, "ReelTresAlturas": tres_alturas, "ReelHohmann": hohmann, "ReelLatencia": latencia,
              "ReelAreasIguales": areas_iguales, "ReelVentanaContacto": ventana_contacto, "ReelVelocidadEscape": velocidad_escape,
              "ReelCobertura": cobertura, "ReelAmaneceres": amaneceres, "ReelCohete": cohete, "ReelGravedadISS": gravedad,
              "ReelMensajeMarte": mensaje_marte, "ReelClarke": clarke, "ReelLaserLuna": laser_luna}


def _registrar_divulgacion():
    """REELS_DIVULGACION = {nombre: (función, V, 0.0)} con V = duración total (título + cuerpo + logo)."""
    F = _fisica()
    return {n: (f, F.duracion_total(F.CUERPO[n]), 0.0) for n, f in _FUNCIONES.items()}


REELS_DIVULGACION = _registrar_divulgacion()

# ── Serie «Estación ATP» (38-reels-ats.py): mismo esquema título → cuerpo → logo; tiempos de datos_ats.py ──────────────

def _ats():
    _fisica()
    import datos_ats as DA
    return DA


def _leyendas_ats(mc, DA, nombre, vol=0.10):
    for i, t0 in enumerate(DA.LEYENDAS[nombre]):
        mc.poner(t0 + 0.2, pluck(PENTA[i % 5], 1.3, vol), pan=(-0.3, 0.3)[i % 2])


def _fin_ats(m, DA, nombre, mc):
    _leyendas_ats(mc, DA, nombre)
    _cierre_sonoro(m, _fisica(), DA.CUERPO[nombre])


def _tono(m, f_hz, env, vol, F):
    """Seno de frecuencia variable `f_hz` (array sobre todo el video) con envolvente `env`."""
    fase = 2 * np.pi * np.cumsum(f_hz) / SR
    m.sumar(np.sin(fase) * env * vol)


def ats_pase(m):
    DA = _ats(); F = _fisica()
    mc, tb = _base(m, DA, "ReelAtpPase", (A(-24), A(-17), A(-12)), 0.25, (900, 4000, 0.015))
    t = np.arange(m.n) / SR
    p = DA.pase("demo-pase")["series"]
    u = np.clip((t - F.H0 - DA.PASE_T0) / (DA.PASE_T1 - DA.PASE_T0), 0, 1)
    el = np.interp(u * p["t"][-1], p["t"], p["el"])
    env = np.clip((t - F.H0 - DA.PASE_T0) / 0.5, 0, 1) * np.clip((F.H0 + DA.PASE_T1 + 0.4 - t) / 0.8, 0, 1)
    _tono(m, 220 + 7 * el, env, 0.05, F)                                   # el tono sube con la elevación del satélite
    for j in range(int((DA.PASE_T1 - DA.PASE_T0) / 1.0)):
        mc.poner(DA.PASE_T0 + j, clic(0.06, 2400), pan=0.3)
    mc.poner(DA.PASE_T1, pluck(A(12), 1.6, 0.24))
    _fin_ats(m, DA, "ReelAtpPase", mc)


def ats_keyhole(m):
    DA = _ats(); F = _fisica()
    mc, tb = _base(m, DA, "ReelAtpKeyhole", (A(-24), A(-19), A(-12)), 0.24, (900, 4500, 0.015))
    t0 = DA.KH_T0 + 6.0 / DA.KH_SIM_X                                       # culminación: ts = 0
    mc.poner(t0 - 0.2, whoosh(0.9, 400, 3800, 0.10, 0.5), pan=0.0)
    mc.poner(t0 + 0.5, servo(7.0, 150, 260, 0.9), pan=-0.3)                  # el motor trabajando al tope
    for j in range(24):                                                     # mientras está fuera del haz: pulsos
        mc.poner(t0 + 0.8 + j * 0.35, clic(0.10, 1300), pan=0.4)
    for tb_, n in ((15.5, -5), (16.6, 4), (17.7, 12)):
        mc.poner(tb_, pluck(A(n), 1.5, 0.24), pan=0.0)
    _fin_ats(m, DA, "ReelAtpKeyhole", mc)


def ats_autotrack(m):
    DA = _ats(); F = _fisica()
    mc, tb = _base(m, DA, "ReelAtpAutotrack", (A(-24), A(-17), A(-12)), 0.24, (1000, 4500, 0.012))
    t = np.arange(m.n) / SR
    env = np.clip((t - F.H0 - 0.8) / 0.6, 0, 1) * np.clip((F.H0 + DA.AT_T1 + 0.3 - t) / 0.8, 0, 1)
    scan = 0.5 + 0.5 * np.sin(2 * np.pi * 1.7 * t)
    m.sumar(np.sin(2 * np.pi * 262 * t) * env * 0.03 * (1.0 + 0.8 * scan), 1.0)             # programa: temblor que no se corrige
    m.sumar(np.sin(2 * np.pi * 523 * t) * env * 0.03 * suave_np((t - F.H0 - 8.0) / 3.0), 1.0)  # autotrack: se limpia y se afina
    mc.poner(10.0, pluck(A(12), 1.8, 0.26))
    mc.poner(10.0, brillo_(0.9, 0.5))
    _fin_ats(m, DA, "ReelAtpAutotrack", mc)


def ats_doppler(m):
    DA = _ats(); F = _fisica()
    mc, tb = _base(m, DA, "ReelAtpDoppler", (A(-24), A(-17), A(-12)), 0.25, (900, 4500, 0.02))
    t = np.arange(m.n) / SR
    p = DA.pase("demo-pase")["series"]
    u = np.clip((t - F.H0 - DA.DOP_T0) / (DA.DOP_T1 - DA.DOP_T0), 0, 1)
    d = np.interp(u * p["t"][-1], p["t"], p["doppler_hz"]) / 50545.0
    env = np.clip((t - F.H0 - DA.DOP_T0) / 0.4, 0, 1) * np.clip((F.H0 + DA.DOP_T1 + 0.3 - t) / 0.5, 0, 1)
    _tono(m, 900 + 420 * d, env, 0.07, F)                                  # el tono baja como el Doppler
    mc.poner(6.0, whoosh(1.0, 400, 3200, 0.07, 0.4))                         # ventana ancha
    mc.poner(8.8, whoosh(1.8, 3200, 500, 0.08, 0.5), pan=0.3)                # se encoge
    mc.poner(11.7, pluck(A(0), 1.6, 0.22))
    _fin_ats(m, DA, "ReelAtpDoppler", mc)


def ats_orbita(m):
    DA = _ats(); F = _fisica()
    mc, tb = _base(m, DA, "ReelAtpOrbita", (A(-24), A(-17), A(-12)), 0.25, (900, 4500, 0.015))
    for j, (t0, km) in enumerate(zip(DA.OD_PASOS, [k for _, k in DA.OD_TLE_KM])):
        mc.poner(t0, pluck(A(-2 * j), 1.3, 0.2), pan=-0.3 + 0.15 * j)       # cada escalón es más grave: peor
        mc.poner(t0, golpe(70 - 3 * j, 0.4, 0.18))
    mc.poner(12.8, whoosh(1.4, 300, 3000, 0.09, 0.5))
    mc.poner(13.2, pluck(A(12), 1.8, 0.28))
    mc.poner(13.2, brillo_(0.9, 0.5))
    _fin_ats(m, DA, "ReelAtpOrbita", mc)


def ats_sol(m):
    DA = _ats(); F = _fisica()
    mc, tb = _base(m, DA, "ReelAtpSol", (A(-24), A(-17), A(-12)), 0.25, (900, 4500, 0.015))
    for (a, b) in (DA.SOL_BARRIDO_AZ, DA.SOL_BARRIDO_EL):
        mc.poner(a, glide(450, 1500, (b - a) / 2, 0.06), pan=-0.3)           # sube hacia el pico de potencia…
        mc.poner(a + (b - a) / 2, glide(1500, 450, (b - a) / 2, 0.06), pan=0.3)   # …y baja
        mc.poner(a + (b - a) / 2, pluck(A(7), 1.0, 0.18))
    mc.poner(DA.SOL_CORRIGE, servo(1.4, 200, 520, 0.8), pan=0.2)
    mc.poner(DA.SOL_CORRIGE + 1.4, pluck(A(12), 1.8, 0.28))
    for t0, n in ((9.8, 0), (11.0, 4), (14.4, 7)):
        mc.poner(t0, pluck(A(n), 1.2, 0.18), pan=0.2)
    _fin_ats(m, DA, "ReelAtpSol", mc)


def ats_pnt(m):
    DA = _ats(); F = _fisica()
    mc, tb = _base(m, DA, "ReelAtpPnt", (A(-24), A(-17), A(-10)), 0.25, (700, 3500, 0.015))
    for j in range(8):                                                      # pases de satélites: tonos que bajan
        mc.poner(0.8 + j * 0.65, glide(1400 - 60 * j, 700, 0.6, 0.04), pan=(-0.5, 0.5)[j % 2])
    for t0, n in zip((6.2, 8.4, 12.2, 14.6, 17.0), (12, 7, 4, 0, -5)):      # el error crece: cada nota es más grave
        mc.poner(t0, pluck(A(n), 1.6, 0.24), pan=0.0)
        mc.poner(t0, golpe(70, 0.4, 0.16))
    _fin_ats(m, DA, "ReelAtpPnt", mc)


def ats_laser(m):
    DA = _ats(); F = _fisica()
    mc, tb = _base(m, DA, "ReelAtpLaser", (A(-24), A(-17), A(-12)), 0.24, (1500, 6000, 0.012))
    t = np.arange(m.n) / SR
    s0, s1 = DA.LASER_BUSCA[0], DA.LASER_ENCUENTRA
    u = np.clip((t - F.H0 - s0) / (s1 - s0), 0, 1)
    env = ((t >= F.H0 + s0) & (t <= F.H0 + s1)).astype(float)
    _tono(m, 500 + 900 * np.sqrt(u), env * np.clip((F.H0 + s1 + 0.1 - t) / 0.2, 0, 1), 0.04, F)    # la espiral se cierra: sube
    for j in range(22):
        mc.poner(s0 + j * (s1 - s0) / 22, clic(0.07, 2800 + 80 * j), pan=0.3)
    mc.poner(s1, pluck(A(12), 1.8, 0.30))
    mc.poner(s1, brillo_(1.0, 0.7))
    mc.poner(9.5, glide(900, 1100, 3.0, 0.03), pan=0.3)                      # enlace cerrado: zumbido tranquilo
    _fin_ats(m, DA, "ReelAtpLaser", mc)


def ats_mpc(m):
    DA = _ats(); F = _fisica()
    mc, tb = _base(m, DA, "ReelAtpMpc", (A(-24), A(-17), A(-12)), 0.25, (900, 4500, 0.015))
    mc.poner(6.5, whoosh(1.0, 500, 1800, 0.06, 0.4))                          # mira 2 s
    mc.poner(13.0, whoosh(3.0, 400, 4200, 0.08, 0.7), pan=0.2)                # mira 36 s
    for t0, n in ((2.0, -5), (8.2, -2), (15.3, 4), (15.3, 12)):
        mc.poner(t0, pluck(A(n), 1.4, 0.22), pan=0.0)
    _fin_ats(m, DA, "ReelAtpMpc", mc)


def ats_lockstep(m):
    DA = _ats(); F = _fisica()
    mc, tb = _base(m, DA, "ReelAtpLockstep", (A(-24), A(-17), A(-12)), 0.25, (900, 4500, 0.015))
    t = np.arange(m.n) / SR
    conv = np.clip((t - F.H0 - 9.0) / 2.5, 0, 1)
    env = np.clip((t - F.H0 - 1.0) / 0.5, 0, 1) * np.clip((F.H0 + 12.5 - t) / 0.6, 0, 1)
    for j, df in enumerate((-9.0, -3.0, 4.0, 11.0)):                         # cuatro corridas desafinadas que se vuelven una
        m.sumar(np.sin(2 * np.pi * (330 + df * (1 - conv)) * t) * env * 0.022, 1.0)
    for j in range(10):
        mc.poner(6.0 + j * 0.6, clic(0.09, 2200), pan=0.2)                  # el reloj espera y avanza
    mc.poner(12.8, pluck(A(12), 1.8, 0.28))
    _fin_ats(m, DA, "ReelAtpLockstep", mc)


def suave_np(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def brillo_(d, vol):
    return sm.brillo(d, vol)


_FUNCIONES_ATS = {"ReelAtpPase": ats_pase, "ReelAtpKeyhole": ats_keyhole, "ReelAtpAutotrack": ats_autotrack, "ReelAtpDoppler": ats_doppler,
                  "ReelAtpOrbita": ats_orbita, "ReelAtpSol": ats_sol, "ReelAtpPnt": ats_pnt, "ReelAtpLaser": ats_laser,
                  "ReelAtpMpc": ats_mpc, "ReelAtpLockstep": ats_lockstep}


def _registrar_ats():
    DA = _ats()
    return {n: (f, DA.duracion(n), 0.0) for n, f in _FUNCIONES_ATS.items()}


REELS_ATS = _registrar_ats()

# ══ Serie «CO.DE Triage» (39-reels-triage.py): tiempos en datos_triage.py y en la escena ══════════════════════════════
def _tri():
    _fisica()
    import datos_triage as DT
    return DT


def _fin_tri(m, DT, nombre, mc):
    _leyendas_ats(mc, DT, nombre)
    _cierre_sonoro(m, _fisica(), DT.CUERPO[nombre])


def _siseo(m, F, t0, t1, vol=0.025, lo=2500, hi=7000):
    """Ruido de radio (el «siseo» de la cascada) entre t0 y t1 del cuerpo."""
    ruido_circular(m, lo, hi, vol, mod=lambda t: np.clip((t - F.H0 - t0) / 0.5, 0, 1) * np.clip((F.H0 + t1 - t) / 0.6, 0, 1))


def tri_cascada(m):
    DT = _tri(); F = _fisica()
    mc, tb = _base(m, DT, "ReelTriCascada", (A(-24), A(-17), A(-12)), 0.24, (900, 4000, 0.012))
    _siseo(m, F, 1.0, 15.0)
    t = np.arange(m.n) / SR
    u = np.clip((t - F.H0 - 1.0) / 14.0, 0, 1)
    amp = np.exp(-((u - 0.5) / 0.33) ** 2) * ((t > F.H0 + 1.0) & (t < F.H0 + 15.0))
    _tono(m, 700 + 500 * (0.5 - 0.26 * np.tanh((u - 0.5) / 0.14)), amp, 0.045, F)      # la señal: su tono sigue a la línea
    for j in range(14):
        mc.poner(1.0 + j, clic(0.05, 2000), pan=0.2)                                     # cada fila nueva
    mc.poner(13.0, pluck(A(12), 1.6, 0.26))
    _fin_tri(m, DT, "ReelTriCascada", mc)


def tri_doppler(m):
    DT = _tri(); F = _fisica()
    mc, tb = _base(m, DT, "ReelTriDoppler", (A(-24), A(-17), A(-12)), 0.24, (900, 4000, 0.012))
    t = np.arange(m.n) / SR
    u = np.clip((t - F.H0 - 1.0) / 13.0, 0, 1)
    env = np.clip((t - F.H0 - 1.0) / 0.5, 0, 1) * np.clip((F.H0 + 14.2 - t) / 0.8, 0, 1)
    f = 520 * (1 + 0.16 * -np.tanh((u - 0.5) / 0.12))                                   # agudo al acercarse, grave al alejarse
    _tono(m, f, env * (0.6 + 0.4 * np.exp(-((u - 0.5) / 0.3) ** 2)), 0.05, F)
    mc.poner(7.5, whoosh(1.4, 600, 2400, 0.06, 0.5))
    mc.poner(14.5, pluck(A(7), 1.6, 0.24))
    _fin_tri(m, DT, "ReelTriDoppler", mc)


def tri_ruido(m):
    DT = _tri(); F = _fisica()
    mc, tb = _base(m, DT, "ReelTriRuido", (A(-24), A(-17), A(-12)), 0.24, (900, 4500, 0.012))
    _siseo(m, F, 1.0, 8.0, 0.02)
    mc.poner(1.0, pluck(A(5), 1.4, 0.24), pan=-0.4)                                     # con señal
    mc.poner(3.2, golpe(80, 0.5, 0.14), pan=0.0)                                       # solo ruido
    mc.poner(5.4, whoosh(0.5, 3000, 300, 0.06, 0.2), pan=0.4)                           # falló
    mc.poner(5.6, golpe(55, 0.6, 0.2), pan=0.4)
    for j in range(16):
        mc.poner(11.0 + 0.4 * j, clic(0.05, 1800 + 60 * (j % 4)), pan=(-0.3, 0.3)[j % 2])
    _fin_tri(m, DT, "ReelTriRuido", mc)


def tri_red(m):
    DT = _tri(); F = _fisica()
    mc, tb = _base(m, DT, "ReelTriRedNeuronal", (A(-24), A(-17), A(-12)), 0.24, (900, 4500, 0.012))
    for j in range(24):
        mc.poner(1.0 + j * 5.5 / 24, clic(0.04, 2600), pan=-0.5 + j / 24)               # la lupa recorre la imagen
    for t0, nota in ((3.2, -5), (7.0, 0), (7.4, 2), (7.8, 4), (9.4, 7)):
        mc.poner(t0, pluck(A(nota), 1.2, 0.20))
    mc.poner(11.8, whoosh(1.4, 400, 2000, 0.05, 0.6))
    mc.poner(12.6, pluck(A(12), 1.8, 0.28)); mc.poner(12.6, brillo_(0.9, 0.5))
    _fin_tri(m, DT, "ReelTriRedNeuronal", mc)


def tri_aprender(m):
    DT = _tri(); F = _fisica()
    mc, tb = _base(m, DT, "ReelTriAprender", (A(-24), A(-17), A(-12)), 0.24, (900, 4500, 0.012))
    for j in range(30):
        mc.poner(0.8 + j * 4.2 / 30, clic(0.035, 2200 + 30 * j), pan=(-0.3, 0.3)[j % 2])
    mc.poner(6.3, golpe(60, 0.7, 0.22)); mc.poner(6.4, servo(0.4, 300, 220, 0.04))    # se cierra el examen
    for j in range(20):
        mc.poner(12.75 + j * 2.2 / 20, gota(600 + 20 * j, 0.15, 0.08), pan=-0.4 + j / 25)
    mc.poner(15.1, pluck(A(12), 1.8, 0.28))
    _fin_tri(m, DT, "ReelTriAprender", mc)


def tri_buen_pase(m):
    DT = _tri(); F = _fisica()
    mc, tb = _base(m, DT, "ReelTriBuenPase", (A(-24), A(-17), A(-12)), 0.24, (900, 4500, 0.012))
    for t0, nota in ((5.8, 0), (9.0, 4), (12.4, -12)):
        mc.poner(t0, whoosh(1.2, 400, 1600 if nota >= 0 else 700, 0.05, 0.5))
        mc.poner(t0 + 1.3, pluck(A(nota), 1.5, 0.24))
    _fin_tri(m, DT, "ReelTriBuenPase", mc)


def tri_placebo(m):
    DT = _tri(); F = _fisica()
    mc, tb = _base(m, DT, "ReelTriPlacebo", (A(-24), A(-17), A(-12)), 0.24, (900, 4500, 0.012))
    for k, t0 in enumerate((6.6, 8.6, 10.6)):
        for j in range(8):
            mc.poner(t0 + j * 0.09, clic(0.06, 1500 + 200 * (j % 3)), pan=(-0.4, 0.4)[j % 2])   # barajar
        mc.poner(t0 + 1.0, pluck(A(-2 + 2 * k), 1.2, 0.20))
    mc.poner(12.4, golpe(50, 0.9, 0.26)); mc.poner(12.4, pluck(A(-5), 1.8, 0.2))
    _fin_tri(m, DT, "ReelTriPlacebo", mc)


def tri_trampa(m):
    DT = _tri(); F = _fisica()
    mc, tb = _base(m, DT, "ReelTriTrampa", (A(-24), A(-17), A(-12)), 0.24, (900, 4500, 0.012))
    for j in range(10):
        mc.poner(1.6 + 0.1 * j, gota(500 + 30 * j, 0.15, 0.07))
    for j in range(6):
        mc.poner(5.5 + j * 0.6, clic(0.06, 900), pan=0.2)                                # alarma suave
    mc.poner(9.0, whoosh(0.8, 2400, 300, 0.07, 0.3)); mc.poner(9.1, golpe(55, 0.8, 0.24))
    mc.poner(10.5, servo(1.5, 500, 380, 0.03))
    mc.poner(12.2, pluck(A(7), 1.8, 0.26))
    _fin_tri(m, DT, "ReelTriTrampa", mc)


def tri_plataforma(m):
    DT = _tri(); F = _fisica()
    mc, tb = _base(m, DT, "ReelTriPlataforma", (A(-24), A(-17), A(-12)), 0.24, (900, 4500, 0.012))
    mc.poner(5.6, golpe(65, 0.6, 0.2))
    for j in range(24):
        mc.poner(6.0 + 0.45 * j + 0.9, clic(0.045, 2400), pan=0.0)                      # pasa por la IA
        mc.poner(6.0 + 0.45 * j + 1.8, gota(400 + 120 * (j % 3), 0.12, 0.06), pan=(-0.4, 0.0, 0.4)[j % 3])
    _fin_tri(m, DT, "ReelTriPlataforma", mc)


def tri_pronostico(m):
    DT = _tri(); F = _fisica()
    mc, tb = _base(m, DT, "ReelTriPronostico", (A(-24), A(-17), A(-12)), 0.24, (900, 4500, 0.012))
    for i in range(5):
        mc.poner(2.4 + 0.5 * i, pluck(A(-5 + 2 * i), 0.9, 0.14), pan=-0.3 + 0.15 * i)
    mc.poner(6.0, servo(1.6, 300, 500, 0.04)); mc.poner(7.7, pluck(A(12), 1.4, 0.24))
    mc.poner(12.0, whoosh(0.9, 500, 2000, 0.05, 0.5)); mc.poner(12.5, pluck(A(7), 1.5, 0.22))
    _fin_tri(m, DT, "ReelTriPronostico", mc)


_FUNCIONES_TRI = {"ReelTriCascada": tri_cascada, "ReelTriDoppler": tri_doppler, "ReelTriRuido": tri_ruido, "ReelTriRedNeuronal": tri_red,
                  "ReelTriAprender": tri_aprender, "ReelTriBuenPase": tri_buen_pase, "ReelTriPlacebo": tri_placebo,
                  "ReelTriTrampa": tri_trampa, "ReelTriPlataforma": tri_plataforma, "ReelTriPronostico": tri_pronostico}


def _registrar_tri():
    DT = _tri()
    return {n: (f, DT.duracion(n), 0.0) for n, f in _FUNCIONES_TRI.items()}


REELS_TRIAGE = _registrar_tri()

# ══ Serie «Clima espacial» (40-reels-clima.py): tiempos en datos_clima.py y en la escena ══════════════════════════════
def _clima():
    _fisica()
    import datos_clima as DC
    return DC


def _fin_clima(m, DC, nombre, mc):
    _leyendas_ats(mc, DC, nombre)
    _cierre_sonoro(m, _fisica(), DC.CUERPO[nombre])


def _env(m, F, t0, t1, a=0.5, b=0.8):
    t = np.arange(m.n) / SR
    return np.clip((t - F.H0 - t0) / a, 0, 1) * np.clip((F.H0 + t1 - t) / b, 0, 1)


_NOTAS_SOL = (A(-26), A(-19), A(-14))          # colchón más grave y cálido que el de las otras series


def sol_luz(m):
    DC = _clima(); F = _fisica()
    mc, tb = _base(m, DC, "ReelSolLuz", _NOTAS_SOL, 0.25, (700, 3500, 0.012))
    t = np.arange(m.n) / SR
    u = np.clip((t - F.H0 - 1.5) / 12.0, 0, 1)
    _tono(m, 300 + 500 * u, _env(m, F, 1.5, 13.6, 0.3, 0.3), 0.04, F)                  # el fotón viaja: el tono sube
    for j in range(9):
        mc.poner(1.5 + j * 12.0 / 8.3, clic(0.05, 2000), pan=0.3)                       # cada minuto del reloj
    mc.poner(13.5, pluck(A(12), 1.8, 0.3)); mc.poner(13.5, brillo_(1.0, 0.6))
    _fin_clima(m, DC, "ReelSolLuz", mc)


def sol_viento(m):
    DC = _clima(); F = _fisica()
    mc, tb = _base(m, DC, "ReelSolViento", _NOTAS_SOL, 0.25, (700, 3500, 0.012))
    _siseo(m, F, 0.4, 18.5, 0.035, 300, 2500)                                          # el viento
    mc.poner(5.5, whoosh(1.5, 300, 2500, 0.07, 0.5))
    mc.poner(11.0, golpe(60, 0.8, 0.2)); mc.poner(11.0, pluck(A(7), 1.6, 0.24))
    _fin_clima(m, DC, "ReelSolViento", mc)


def sol_escudo(m):
    DC = _clima(); F = _fisica()
    mc, tb = _base(m, DC, "ReelSolEscudo", _NOTAS_SOL, 0.25, (700, 3500, 0.012))
    for j, L in enumerate((1.6, 2.2, 3.0, 4.1, 5.4)):
        mc.poner(0.6 + 0.35 * L, pluck(A(-5 + 3 * j), 1.0, 0.14), pan=-0.3 + 0.15 * j)  # se dibuja cada línea
    _siseo(m, F, 5.5, 19.5, 0.03, 300, 2500)
    mc.poner(6.5, servo(2.5, 200, 140, 0.04))                                          # se aplasta
    for j in range(6):
        mc.poner(12.6 + 0.9 * j, gota(800 + 60 * j, 0.25, 0.08), pan=(-0.5, 0.5)[j % 2])   # auroras en los polos
    _fin_clima(m, DC, "ReelSolEscudo", mc)


def sol_aurora(m):
    DC = _clima(); F = _fisica()
    mc, tb = _base(m, DC, "ReelSolAurora", _NOTAS_SOL, 0.25, (700, 3500, 0.012))
    for j in range(14):
        mc.poner(0.8 + j * 0.45, gota(500 + 40 * (j % 5), 0.2, 0.07), pan=-0.4 + (j % 5) * 0.2)
    t = np.arange(m.n) / SR
    for f0, t0 in ((392.0, 6.0), (523.25, 12.6), (261.6, 13.0)):                     # cada color, un tono que brilla
        f = ciclo_entero(f0, m.T)
        m.sumar(np.sin(2 * np.pi * f * t) * _env(m, F, t0, tb + 0.3, 1.5, 1.0) * (0.7 + 0.3 * np.sin(2 * np.pi * 4 * t / m.T)) * 0.022)
    _fin_clima(m, DC, "ReelSolAurora", mc)


def sol_manchas(m):
    DC = _clima(); F = _fisica()
    mc, tb = _base(m, DC, "ReelSolManchas", _NOTAS_SOL, 0.25, (700, 3500, 0.012))
    mc.poner(1.5, pluck(A(7), 1.2, 0.2)); mc.poner(3.0, pluck(A(-2), 1.2, 0.2))
    t = np.arange(m.n) / SR
    a = 1986.5 + np.clip((t - F.H0 - 6.8) / 5.5, 0, 1) * (DC.FIN_CURVA - 1986.5)
    _tono(m, 260 + 2.2 * DC.manchas(a), _env(m, F, 6.8, 12.4, 0.3, 0.3), 0.04, F)    # la curva suena: más manchas, más agudo
    mc.poner(11.0, pluck(A(5), 1.4, 0.2)); mc.poner(12.6, pluck(A(12), 1.8, 0.26))
    _fin_clima(m, DC, "ReelSolManchas", mc)


def sol_llamarada(m):
    DC = _clima(); F = _fisica()
    mc, tb = _base(m, DC, "ReelSolLlamarada", _NOTAS_SOL, 0.25, (700, 3500, 0.012))
    mc.poner(1.5, golpe(48, 1.2, 0.35)); mc.poner(1.5, brillo_(1.2, 0.8))
    mc.poner(2.0, whoosh(6.5, 400, 1800, 0.05, 0.85))
    mc.poner(8.9, whoosh(0.4, 4000, 300, 0.08, 0.2))
    _siseo(m, F, 8.9, 13.0, 0.05, 1500, 6000)                                          # la radio se vuelve estática
    _fin_clima(m, DC, "ReelSolLlamarada", mc)


def sol_eyeccion(m):
    DC = _clima(); F = _fisica()
    mc, tb = _base(m, DC, "ReelSolEyeccion", _NOTAS_SOL, 0.25, (700, 3500, 0.012))
    mc.poner(1.0, whoosh(10.0, 120, 900, 0.07, 0.95))
    for j in (1.0, 4.3, 7.6):
        mc.poner(j, clic(0.08, 1200), pan=-0.3)                                        # día 1, 2, 3
    mc.poner(11.0, golpe(42, 1.4, 0.4)); mc.poner(11.2, servo(1.5, 180, 90, 0.05))
    mc.poner(11.8, pluck(A(-5), 1.8, 0.24))
    _fin_clima(m, DC, "ReelSolEyeccion", mc)


def sol_satelites(m):
    DC = _clima(); F = _fisica()
    mc, tb = _base(m, DC, "ReelSolSatelites", _NOTAS_SOL, 0.25, (700, 3500, 0.012))
    mc.poner(5.5, servo(3.0, 120, 220, 0.04))                                          # la atmósfera se infla
    rng = np.random.default_rng(5)
    for j in range(14):
        tj = 10.0 + j * 0.42 + rng.uniform(-0.1, 0.1)
        mc.poner(tj, whoosh(0.5, 2600, 500, 0.035, 0.3), pan=rng.uniform(-0.5, 0.5))   # caen
    _fin_clima(m, DC, "ReelSolSatelites", mc)


def sol_gps(m):
    DC = _clima(); F = _fisica()
    mc, tb = _base(m, DC, "ReelSolGps", _NOTAS_SOL, 0.25, (700, 3500, 0.012))
    for j in range(10):
        mc.poner(0.8 + j * 0.55, clic(0.05, 1575), pan=-0.2)                          # pulsos de la señal (L1 ≈ 1575 MHz, guiño)
    t = np.arange(m.n) / SR
    k = np.clip((t - F.H0 - 6.5) / 2.5, 0, 1)
    _tono(m, 440 + 30 * k * np.sin(2 * np.pi * 3 * t), _env(m, F, 6.0, 12.4, 0.5, 0.5), 0.03, F)   # se agita
    mc.poner(12.5, pluck(A(-2), 1.6, 0.22))
    _fin_clima(m, DC, "ReelSolGps", mc)


def sol_tormenta(m):
    DC = _clima(); F = _fisica()
    mc, tb = _base(m, DC, "ReelSolTormenta", _NOTAS_SOL, 0.25, (700, 3500, 0.012))
    for j in range(8):
        mc.poner(0.8 + j * 0.13, clic(0.06, 3000 + 300 * (j % 3)), pan=0.3)            # chispas del telégrafo
    mc.poner(6.2, golpe(45, 1.2, 0.3)); mc.poner(6.4, whoosh(0.6, 2000, 200, 0.05, 0.2))   # apagón
    t = np.arange(m.n) / SR
    m.sumar(np.sin(2 * np.pi * ciclo_entero(330, m.T) * t) * _env(m, F, 12.2, tb + 0.3, 1.5, 1.0) * 0.025)
    mc.poner(12.2, pluck(A(12), 1.8, 0.26))
    _fin_clima(m, DC, "ReelSolTormenta", mc)


_FUNCIONES_CLIMA = {"ReelSolLuz": sol_luz, "ReelSolViento": sol_viento, "ReelSolEscudo": sol_escudo, "ReelSolAurora": sol_aurora,
                    "ReelSolManchas": sol_manchas, "ReelSolLlamarada": sol_llamarada, "ReelSolEyeccion": sol_eyeccion,
                    "ReelSolSatelites": sol_satelites, "ReelSolGps": sol_gps, "ReelSolTormenta": sol_tormenta}


def _registrar_clima():
    DC = _clima()
    return {n: (f, DC.duracion(n), 0.0) for n, f in _FUNCIONES_CLIMA.items()}


REELS_CLIMA = _registrar_clima()

# ══ Serie «Inteligencia artificial» (41-reels-ia.py): tiempos en datos_ia.py y en la escena ═══════════════════════════
def _ia():
    _fisica()
    import datos_ia as DI
    return DI


def _fin_ia(m, DI, nombre, mc):
    _leyendas_ats(mc, DI, nombre)
    _cierre_sonoro(m, _fisica(), DI.CUERPO[nombre])


_NOTAS_IA = (A(-24), A(-15), A(-10))           # colchón con la séptima: más «digital» que el de las otras series


def _arpegio(mc, t0, notas, paso=0.12, vol=0.14):
    for j, nt in enumerate(notas):
        mc.poner(t0 + j * paso, pluck(A(nt), 0.8, vol), pan=-0.4 + 0.8 * j / max(len(notas) - 1, 1))


def ia_neurona(m):
    DI = _ia(); F = _fisica()
    mc, tb = _base(m, DI, "ReelIaNeurona", _NOTAS_IA, 0.24, (900, 4500, 0.010))
    for k in range(3):
        mc.poner(0.6 + 0.5 * k, clic(0.07, 1800 + 300 * k), pan=-0.4)
    for j in range(12):
        mc.poner(7.0 + 0.4 * j, gota(500 + 80 * (j % 3), 0.15, 0.07), pan=-0.3 + 0.3 * (j % 3))
    _arpegio(mc, 12.6, (0, 4, 7, 12))
    _fin_ia(m, DI, "ReelIaNeurona", mc)


def ia_aprende(m):
    DI = _ia(); F = _fisica()
    mc, tb = _base(m, DI, "ReelIaAprende", _NOTAS_IA, 0.24, (900, 4500, 0.010))
    t = np.arange(m.n) / SR
    ruta = DI.descenso(x0=0.05, paso=0.12, n=40)
    i = np.clip((t - F.H0 - 5.5) / 8.5 * (len(ruta) - 1), 0, len(ruta) - 1)
    e = DI.error(np.interp(i, np.arange(len(ruta)), ruta))
    t_ = np.arange(m.n) / SR
    env = np.clip((t_ - F.H0 - 5.5) / 0.4, 0, 1) * np.clip((F.H0 + 14.3 - t_) / 0.5, 0, 1)
    _tono(m, 220 + 140 * e, env, 0.04, F)                                              # el tono baja con el error
    _arpegio(mc, 14.0, (12, 7, 4, 0), 0.14, 0.18)
    _fin_ia(m, DI, "ReelIaAprende", mc)


def ia_palabras(m):
    DI = _ia(); F = _fisica()
    mc, tb = _base(m, DI, "ReelIaPalabras", _NOTAS_IA, 0.24, (900, 4500, 0.010))
    for k in range(16):
        mc.poner(0.8 + 0.28 * k, gota(400 + 45 * (k % 7), 0.14, 0.07), pan=-0.5 + (k % 5) * 0.25)
    mc.poner(12.6, glide(330, 495, 0.8, 0.05)); mc.poner(13.6, glide(392, 588, 0.8, 0.05))
    mc.poner(14.4, pluck(A(12), 1.6, 0.26))
    _fin_ia(m, DI, "ReelIaPalabras", mc)


def ia_atencion(m):
    DI = _ia(); F = _fisica()
    mc, tb = _base(m, DI, "ReelIaAtencion", _NOTAS_IA, 0.24, (900, 4500, 0.010))
    for t0, base in ((2.5, -5), (11.0, 0)):
        _arpegio(mc, t0, (base, base + 3, base + 7, base + 10, base + 12), 0.15, 0.12)
    mc.poner(6.0, pluck(A(-2), 1.4, 0.22)); mc.poner(14.0, pluck(A(7), 1.4, 0.22))
    _fin_ia(m, DI, "ReelIaAtencion", mc)


def ia_siguiente(m):
    DI = _ia(); F = _fisica()
    mc, tb = _base(m, DI, "ReelIaSiguiente", _NOTAS_IA, 0.24, (900, 4500, 0.010))
    for j in range(14):
        mc.poner(0.6 + j * 0.42, clic(0.04, 2600), pan=0.2)                              # el cursor que parpadea
    for k in range(5):
        mc.poner(2.2 + 0.4 * k, pluck(A(-5 + 2 * k), 0.8, 0.12), pan=-0.3)
    mc.poner(7.0, whoosh(1.2, 500, 2200, 0.05, 0.5)); mc.poner(8.2, pluck(A(12), 1.6, 0.26))
    _fin_ia(m, DI, "ReelIaSiguiente", mc)


def ia_pixeles(m):
    DI = _ia(); F = _fisica()
    mc, tb = _base(m, DI, "ReelIaPixeles", _NOTAS_IA, 0.24, (900, 4500, 0.010))
    for j in range(16):
        mc.poner(7.0 + 0.08 * j, clic(0.05, 1500 + 120 * (j % 4)), pan=-0.3 + 0.04 * j)
    t = np.arange(m.n) / SR
    env = np.clip((t - F.H0 - 11.8) / 0.3, 0, 1) * np.clip((F.H0 + 14.4 - t) / 0.3, 0, 1)
    _tono(m, 200 + 600 * np.clip((t - F.H0 - 11.8) / 2.4, 0, 1), env, 0.035, F)        # el contador sube
    mc.poner(14.3, pluck(A(12), 1.6, 0.24))
    _fin_ia(m, DI, "ReelIaPixeles", mc)


def ia_memoriza(m):
    DI = _ia(); F = _fisica()
    mc, tb = _base(m, DI, "ReelIaMemoriza", _NOTAS_IA, 0.24, (900, 4500, 0.010))
    for k in range(11):
        mc.poner(0.6 + 0.12 * k, gota(500 + 30 * k, 0.12, 0.06))
    mc.poner(4.0, glide(300, 420, 1.8, 0.04))
    t = np.arange(m.n) / SR
    env = np.clip((t - F.H0 - 6.5) / 0.3, 0, 1) * np.clip((F.H0 + 8.4 - t) / 0.3, 0, 1)
    _tono(m, 420 + 120 * np.sin(2 * np.pi * 6 * t), env, 0.03, F)                    # la curva nerviosa
    for k in range(5):
        mc.poner(12.6 + 0.25 * k, clic(0.08, 900), pan=-0.4 + 0.2 * k)
    mc.poner(14.0, pluck(A(-5), 1.6, 0.22))
    _fin_ia(m, DI, "ReelIaMemoriza", mc)


def ia_sesgo(m):
    DI = _ia(); F = _fisica()
    mc, tb = _base(m, DI, "ReelIaSesgo", _NOTAS_IA, 0.24, (900, 4500, 0.010))
    for k in range(12):
        mc.poner(0.6 + 0.15 * k, pluck(A(7 + (k % 3)), 0.5, 0.08), pan=-0.5 + (k % 6) * 0.2)
    mc.poner(7.3, pluck(A(12), 1.2, 0.22))
    mc.poner(10.3, golpe(60, 0.6, 0.2)); mc.poner(10.4, glide(400, 300, 0.6, 0.05))
    _fin_ia(m, DI, "ReelIaSesgo", mc)


def ia_inventa(m):
    DI = _ia(); F = _fisica()
    mc, tb = _base(m, DI, "ReelIaInventa", _NOTAS_IA, 0.24, (900, 4500, 0.010))
    for j in range(26):
        mc.poner(2.3 + j * 0.1, clic(0.035, 2400 + 200 * (j % 3)), pan=-0.2)          # tecleo
    mc.poner(6.6, golpe(55, 0.8, 0.28)); mc.poner(6.7, glide(500, 300, 0.5, 0.05))
    mc.poner(12.6, pluck(A(7), 1.4, 0.22)); mc.poner(13.2, pluck(A(12), 1.6, 0.26))
    _fin_ia(m, DI, "ReelIaInventa", mc)


def ia_espacio(m):
    DI = _ia(); F = _fisica()
    mc, tb = _base(m, DI, "ReelIaEspacio", _NOTAS_IA, 0.24, (900, 4500, 0.010))
    nub = [True, True, False, True, True, False, True, True, True, False, True, False]
    for k, nb in enumerate(nub):
        t0 = 1.0 + 1.05 * k
        mc.poner(t0 + 0.8, clic(0.05, 2000), pan=0.0)
        if t0 + 0.8 < 6.5 or not nb:
            mc.poner(t0 + 1.6, gota(700, 0.15, 0.07), pan=0.0)                           # baja a tierra
        else:
            mc.poner(t0 + 0.9, whoosh(0.5, 1800, 400, 0.04, 0.3), pan=(-0.5, 0.5)[k % 2])  # descartada
    mc.poner(6.5, pluck(A(12), 1.4, 0.24))
    _fin_ia(m, DI, "ReelIaEspacio", mc)


_FUNCIONES_IA = {"ReelIaNeurona": ia_neurona, "ReelIaAprende": ia_aprende, "ReelIaPalabras": ia_palabras, "ReelIaAtencion": ia_atencion,
                 "ReelIaSiguiente": ia_siguiente, "ReelIaPixeles": ia_pixeles, "ReelIaMemoriza": ia_memoriza, "ReelIaSesgo": ia_sesgo,
                 "ReelIaInventa": ia_inventa, "ReelIaEspacio": ia_espacio}


def _registrar_ia():
    DI = _ia()
    return {n: (f, DI.duracion(n), 0.0) for n, f in _FUNCIONES_IA.items()}


REELS_IA = _registrar_ia()

# ══ Serie «Robótica» (42-reels-robotica.py): tiempos en datos_rob.py y en la escena ═══════════════════════════════════
def _rob():
    _fisica()
    import datos_rob as DR
    return DR


def _fin_rob(m, DR, nombre, mc):
    _leyendas_ats(mc, DR, nombre)
    _cierre_sonoro(m, _fisica(), DR.CUERPO[nombre])


_NOTAS_ROB = (A(-26), A(-17), A(-12))           # colchón grave y «mecánico»


def rob_bogie(m):
    DR = _rob(); F = _fisica()
    mc, tb = _base(m, DR, "ReelRobBogie", _NOTAS_ROB, 0.25, (700, 3200, 0.012))
    t = np.arange(m.n) / SR
    env = np.clip((t - F.H0 - 1.2) / 0.4, 0, 1) * np.clip((F.H0 + 14.2 - t) / 0.5, 0, 1)
    _tono(m, 110 + 12 * np.sin(2 * np.pi * 3.0 * t), env, 0.03, F)                        # el zumbido del motor
    for k in range(7):
        mc.poner(3.0 + 1.55 * k, clic(0.07, 900 + 80 * (k % 3)), pan=-0.3 + 0.1 * k)       # cada rueda sube a la roca
    mc.poner(12.8, pluck(A(7), 1.4, 0.22)); mc.poner(13.3, pluck(A(12), 1.6, 0.24))
    _fin_rob(m, DR, "ReelRobBogie", mc)


def rob_patina(m):
    DR = _rob(); F = _fisica()
    mc, tb = _base(m, DR, "ReelRobPatina", _NOTAS_ROB, 0.25, (700, 3200, 0.012))
    t = np.arange(m.n) / SR
    env = np.clip((t - F.H0 - 1.2) / 0.4, 0, 1) * np.clip((F.H0 + 11.2 - t) / 0.5, 0, 1)
    _tono(m, 140, env, 0.03, F)
    _siseo(m, F, 1.2, 11.0, 0.04, 1200, 4500)                                             # la arena que sale despedida
    mc.poner(11.0, golpe(55, 0.8, 0.22)); mc.poner(11.2, pluck(A(-2), 1.4, 0.2))
    _fin_rob(m, DR, "ReelRobPatina", mc)


def rob_mundos(m):
    DR = _rob(); F = _fisica()
    mc, tb = _base(m, DR, "ReelRobMundos", _NOTAS_ROB, 0.25, (700, 3200, 0.012))
    for k in range(5):
        mc.poner(0.6 + 0.35 * k, gota(500 + 70 * k, 0.15, 0.08), pan=-0.4 + 0.2 * k)
    mc.poner(2.0, whoosh(3.2, 300, 1800, 0.05, 0.6))
    for k in range(5):
        mc.poner(5.2 + 0.25 * k, pluck(A(-5 + 2 * k), 0.9, 0.12), pan=-0.4 + 0.2 * k)
    mc.poner(12.6, golpe(48, 0.9, 0.25)); mc.poner(12.7, glide(300, 150, 1.0, 0.04))
    _fin_rob(m, DR, "ReelRobMundos", mc)


def rob_ruta(m):
    DR = _rob(); F = _fisica()
    mc, tb = _base(m, DR, "ReelRobRuta", _NOTAS_ROB, 0.25, (700, 3200, 0.012))
    for j in range(50):
        mc.poner(3.5 + j * 6.0 / 50, clic(0.04, 2200 + 20 * j), pan=-0.4 + 0.016 * j)      # el buscador prueba casillas
    mc.poner(10.0, pluck(A(12), 1.6, 0.26)); mc.poner(10.0, brillo_(1.0, 0.5))
    t = np.arange(m.n) / SR
    _tono(m, 260 + 90 * np.clip((t - F.H0 - 12.8) / 5.5, 0, 1), _env(m, F, 12.8, 18.4, 0.3, 0.4), 0.03, F)
    _fin_rob(m, DR, "ReelRobRuta", mc)


def rob_alarmas(m):
    DR = _rob(); F = _fisica()
    mc, tb = _base(m, DR, "ReelRobAlarmas", _NOTAS_ROB, 0.25, (700, 3200, 0.012))
    t = np.arange(m.n) / SR
    a = np.clip((t - F.H0 - 1.5) / 9.0, 0, 1) * 38.0
    _tono(m, 200 + 8 * a, _env(m, F, 1.5, 10.5, 0.3, 0.5), 0.035, F)                      # el tono sube con la inclinación
    for j in range(6):
        mc.poner(8.6 + 0.4 * j, clic(0.1, 1200), pan=0.2)                                  # alarma
    mc.poner(8.6, golpe(60, 0.7, 0.25))
    mc.poner(13.5, pluck(A(7), 1.4, 0.22)); mc.poner(14.2, pluck(A(12), 1.6, 0.25))
    _fin_rob(m, DR, "ReelRobAlarmas", mc)


def rob_retardo(m):
    DR = _rob(); F = _fisica()
    mc, tb = _base(m, DR, "ReelRobRetardo", _NOTAS_ROB, 0.25, (700, 3200, 0.012))
    mc.poner(1.2, whoosh(1.2, 600, 2400, 0.06, 0.5), pan=-0.2); mc.poner(3.0, whoosh(1.2, 2400, 600, 0.05, 0.5), pan=0.2)
    mc.poner(6.0, whoosh(7.0, 200, 1400, 0.06, 0.9)); mc.poner(14.0, whoosh(7.0, 1400, 200, 0.05, 0.1))
    for j in range(11):
        mc.poner(6.0 + 0.62 * j, clic(0.05, 1400), pan=0.0)                                # el reloj cuenta minutos
    mc.poner(13.0, golpe(55, 0.8, 0.22)); mc.poner(13.0, glide(400, 200, 0.5, 0.05))
    _fin_rob(m, DR, "ReelRobRetardo", mc)


def rob_autonomo(m):
    DR = _rob(); F = _fisica()
    mc, tb = _base(m, DR, "ReelRobAutonomo", _NOTAS_ROB, 0.25, (700, 3200, 0.012))
    for k, t0 in enumerate((1.0, 3.2, 5.4, 8.2)):
        mc.poner(t0, pluck(A(-5 + 3 * k), 1.0, 0.16), pan=-0.3 + 0.2 * k)
    t = np.arange(m.n) / SR
    u = np.clip((t - F.H0 - 2.0) / 11.0, 0, 1)
    _tono(m, 180 + 360 * u, _env(m, F, 2.0, 13.0, 0.4, 0.5), 0.03, F)
    mc.poner(13.0, pluck(A(12), 1.6, 0.26)); mc.poner(13.0, brillo_(1.0, 0.5))
    _fin_rob(m, DR, "ReelRobAutonomo", mc)


def rob_validacion(m):
    DR = _rob(); F = _fisica()
    mc, tb = _base(m, DR, "ReelRobValidacion", _NOTAS_ROB, 0.25, (700, 3200, 0.012))
    for k in range(30):
        mc.poner(0.5 + 0.03 * k, gota(500 + 15 * k, 0.1, 0.05), pan=-0.4 + 0.027 * k)
    mc.poner(6.5, golpe(52, 0.9, 0.26)); mc.poner(6.6, glide(500, 260, 0.9, 0.05))          # los casos nuevos: baja
    mc.poner(13.0, whoosh(1.0, 400, 2200, 0.05, 0.6)); mc.poner(13.9, pluck(A(12), 1.6, 0.26))
    _fin_rob(m, DR, "ReelRobValidacion", mc)


def rob_ros(m):
    DR = _rob(); F = _fisica()
    mc, tb = _base(m, DR, "ReelRobROS", _NOTAS_ROB, 0.25, (700, 3200, 0.012))
    for t0, nt in ((0.6, -5), (1.6, 0), (7.0, 4), (7.6, 7)):
        mc.poner(t0, pluck(A(nt), 1.0, 0.16), pan=(-0.3, 0.3)[int(t0) % 2])
    for j in range(12):
        mc.poner(3.0 + 1.8 * j / 2.0, clic(0.05, 2000 + 150 * (j % 3)), pan=-0.4 + 0.07 * j)   # mensajes
    for j in range(14):
        mc.poner(13.5 + 0.5 * j, clic(0.06, 1300), pan=0.0)                                     # el reloj común
    mc.poner(14.0, pluck(A(12), 1.6, 0.25))
    _fin_rob(m, DR, "ReelRobROS", mc)


def rob_cerebro(m):
    DR = _rob(); F = _fisica()
    mc, tb = _base(m, DR, "ReelRobCerebro", _NOTAS_ROB, 0.25, (700, 3200, 0.012))
    for t0 in (1.0, 5.6, 11.4):
        mc.poner(t0, whoosh(0.8, 600, 1800, 0.05, 0.5)); mc.poner(t0 + 0.8, golpe(70, 0.4, 0.22))   # el enchufe
    t = np.arange(m.n) / SR
    for a, b, f0 in ((1.6, 6.2, 330.0), (6.2, 11.4, 392.0)):
        m.sumar(np.sin(2 * np.pi * ciclo_entero(f0, m.T) * t) * _env(m, F, a, b, 0.5, 0.5) * (0.7 + 0.3 * np.sin(1.4 * 2 * np.pi * (t - F.H0 - a))) * 0.03)
    mc.poner(12.6, pluck(A(-2), 1.6, 0.2))
    _fin_rob(m, DR, "ReelRobCerebro", mc)


_FUNCIONES_ROB = {"ReelRobBogie": rob_bogie, "ReelRobPatina": rob_patina, "ReelRobMundos": rob_mundos, "ReelRobRuta": rob_ruta,
                  "ReelRobAlarmas": rob_alarmas, "ReelRobRetardo": rob_retardo, "ReelRobAutonomo": rob_autonomo,
                  "ReelRobValidacion": rob_validacion, "ReelRobROS": rob_ros, "ReelRobCerebro": rob_cerebro}


def _registrar_rob():
    DR = _rob()
    return {n: (f, DR.duracion(n), 0.0) for n, f in _FUNCIONES_ROB.items()}


REELS_ROB = _registrar_rob()

# ══ Serie «Electromagnetismo» (43-reels-em.py): tiempos en datos_em.py y en la escena ═══════════════════════════════════
def _em():
    _fisica()
    import datos_em as DE
    return DE


def _fin_em(m, DE, nombre, mc):
    _leyendas_ats(mc, DE, nombre)
    _cierre_sonoro(m, _fisica(), DE.CUERPO[nombre])


_NOTAS_EM = (A(-24), A(-19), A(-12))            # colchón grave, quinta abierta: «campo»


def _zumbido(m, F, t0, t1, f0, vol=0.025, vib=0.0):
    t = np.arange(m.n) / SR
    _tono(m, f0 + vib * np.sin(2 * np.pi * 0.5 * t), _env(m, F, t0, t1, 0.5, 0.6), vol, F)


def em_escudo(m):
    DE = _em(); F = _fisica()
    mc, tb = _base(m, DE, "ReelEMEscudo", _NOTAS_EM, 0.25, (900, 4000, 0.012))
    for k in range(4):
        mc.poner(0.6 + 0.5 * k, pluck(A(-5 + 3 * k), 1.0, 0.14), pan=-0.3 + 0.2 * k)          # las líneas del campo
    _siseo(m, F, 6.0, 20.0, 0.03, 1500, 5000)                                                 # el viento solar
    mc.poner(7.0, whoosh(1.6, 300, 1600, 0.05, 0.6))
    mc.poner(13.0, golpe(55, 0.8, 0.2)); mc.poner(13.2, pluck(A(7), 1.4, 0.2))
    _fin_em(m, DE, "ReelEMEscudo", mc)


def em_espiral(m):
    DE = _em(); F = _fisica()
    mc, tb = _base(m, DE, "ReelEMEspiral", _NOTAS_EM, 0.25, (900, 4000, 0.012))
    t = np.arange(m.n) / SR
    _tono(m, 330 * (1 + 0.04 * np.sin(2 * np.pi * 2.2 * t)), _env(m, F, 0.6, 12.3, 0.4, 0.8), 0.03, F)   # el giro
    for j in range(3):
        mc.poner(7.0 + 2.5 + 5.0 * j, clic(0.08, 1500), pan=0.4)                                 # rebotes (aprox.)
        mc.poner(7.0 + 5.0 * j, clic(0.08, 1500), pan=-0.4)
    mc.poner(12.8, golpe(50, 0.9, 0.22)); mc.poner(13.0, pluck(A(5), 1.4, 0.2))
    _fin_em(m, DE, "ReelEMEspiral", mc)


def em_aurora(m):
    DE = _em(); F = _fisica()
    mc, tb = _base(m, DE, "ReelEMAurora", _NOTAS_EM, 0.25, (900, 4000, 0.012))
    for j in range(8):
        mc.poner(0.8 + 0.6 * j, gota(700 + 40 * j, 0.12, 0.05), pan=0.3 - 0.08 * j)
    t = np.arange(m.n) / SR
    for f0, nt in ((A(12), 0.0), (A(16), 0.7), (A(19), 1.4)):
        m.sumar(np.sin(2 * np.pi * ciclo_entero(f0, m.T) * t) * _env(m, F, 6.4 + nt, 20.0, 1.2, 0.8) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * t + nt)) * 0.012)
    mc.poner(12.8, pluck(A(7), 1.4, 0.18)); mc.poner(13.2, pluck(A(12), 1.6, 0.18))
    _fin_em(m, DE, "ReelEMAurora", mc)


def em_torque(m):
    DE = _em(); F = _fisica()
    mc, tb = _base(m, DE, "ReelEMTorque", _NOTAS_EM, 0.25, (900, 4000, 0.012))
    _zumbido(m, F, 1.0, 12.4, 120, 0.03)                                                      # corriente en la bobina
    mc.poner(1.0, clic(0.08, 900))
    t = np.arange(m.n) / SR
    u = np.clip(t - F.H0 - 2.0, 0, None)
    _tono(m, 260 + 120 * np.exp(-0.32 * u) * np.cos(0.9 * u), _env(m, F, 2.0, 12.4, 0.4, 0.6), 0.02, F)
    mc.poner(13.6, whoosh(2.4, 300, 1200, 0.04, 0.6)); mc.poner(15.6, pluck(A(7), 1.4, 0.2))
    _fin_em(m, DE, "ReelEMTorque", mc)


def em_luz(m):
    DE = _em(); F = _fisica()
    mc, tb = _base(m, DE, "ReelEMLuz", _NOTAS_EM, 0.25, (900, 4000, 0.012))
    mc.poner(0.4, pluck(A(-5), 1.0, 0.16), pan=-0.3); mc.poner(1.0, pluck(A(-1), 1.0, 0.16), pan=0.3)
    mc.poner(6.0, golpe(60, 0.6, 0.18))
    mc.poner(7.4, whoosh(2.4, 200, 3000, 0.05, 0.8)); mc.poner(9.8, brillo_(1.0, 0.5)); mc.poner(9.8, pluck(A(12), 1.6, 0.22))
    t = np.arange(m.n) / SR
    m.sumar(np.sin(2 * np.pi * ciclo_entero(A(7), m.T) * t) * _env(m, F, 12.6, 20.0, 0.8, 0.8) * (0.7 + 0.3 * np.sin(2 * np.pi * 1.25 * t)) * 0.015)
    _fin_em(m, DE, "ReelEMLuz", mc)


def em_bandas(m):
    DE = _em(); F = _fisica()
    mc, tb = _base(m, DE, "ReelEMBandas", _NOTAS_EM, 0.25, (900, 4000, 0.012))
    for k in range(4):
        mc.poner(0.5 + 1.2 * k, pluck(A(-5 + 5 * k), 1.0, 0.16), pan=-0.3 + 0.2 * k)          # ondas más chicas, nota más alta
    mc.poner(13.0, brillo_(1.0, 0.5)); mc.poner(13.0, pluck(A(19), 1.6, 0.2))
    _fin_em(m, DE, "ReelEMBandas", mc)


def em_antena(m):
    DE = _em(); F = _fisica()
    mc, tb = _base(m, DE, "ReelEMAntena", _NOTAS_EM, 0.25, (900, 4000, 0.012))
    for j in range(12):
        mc.poner(1.0 + 1.0 * j, gota(520, 0.18, 0.06), pan=0.0)                                 # cada frente que sale
    mc.poner(12.8, golpe(55, 0.7, 0.2)); mc.poner(13.6, pluck(A(7), 1.4, 0.2))
    _fin_em(m, DE, "ReelEMAntena", mc)


def em_ionosfera(m):
    DE = _em(); F = _fisica()
    mc, tb = _base(m, DE, "ReelEMIonosfera", _NOTAS_EM, 0.25, (900, 4000, 0.012))
    _siseo(m, F, 0.6, 20.0, 0.015, 2500, 6000)
    for k, t0 in enumerate((6.0 + 5.0 / 4, 6.0 + 5.0 * 3 / 4)):
        mc.poner(t0, clic(0.1, 1100), pan=-0.3 + 0.6 * k)                                       # rebotes en la capa
    mc.poner(12.8, whoosh(2.5, 400, 3000, 0.05, 0.8)); mc.poner(15.3, pluck(A(12), 1.6, 0.22))
    _fin_em(m, DE, "ReelEMIonosfera", mc)


def em_cable(m):
    DE = _em(); F = _fisica()
    mc, tb = _base(m, DE, "ReelEMCable", _NOTAS_EM, 0.25, (900, 4000, 0.012))
    _zumbido(m, F, 5.5, 20.0, 150, 0.025)
    for j in range(8):
        mc.poner(5.5 + 0.12 * j, clic(0.05, 1800 + 60 * j), pan=-0.3 + 0.08 * j)
    mc.poner(8.0, pluck(A(7), 1.4, 0.2))
    mc.poner(12.8, golpe(50, 0.9, 0.22)); mc.poner(12.9, glide(400, 200, 0.8, 0.05))
    _fin_em(m, DE, "ReelEMCable", mc)


def em_senal(m):
    DE = _em(); F = _fisica()
    mc, tb = _base(m, DE, "ReelEMSenal", _NOTAS_EM, 0.25, (900, 4000, 0.012))
    for k in range(3):
        mc.poner(1.0 + 1.6 * k, pluck(A(7 - 5 * k), 1.0, 0.18 / (k + 1)), pan=-0.3 + 0.3 * k)  # cada vez más débil
    mc.poner(13.0, glide(900, 120, 3.0, 0.04)); mc.poner(16.0, gota(1800, 0.2, 0.03))
    _fin_em(m, DE, "ReelEMSenal", mc)


_FUNCIONES_EM = {"ReelEMEscudo": em_escudo, "ReelEMEspiral": em_espiral, "ReelEMAurora": em_aurora, "ReelEMTorque": em_torque,
                 "ReelEMLuz": em_luz, "ReelEMBandas": em_bandas, "ReelEMAntena": em_antena, "ReelEMIonosfera": em_ionosfera,
                 "ReelEMCable": em_cable, "ReelEMSenal": em_senal}


def _registrar_em():
    DE = _em()
    return {n: (f, DE.duracion(n), 0.0) for n, f in _FUNCIONES_EM.items()}


REELS_EM = _registrar_em()


# ══ Serie «Electrónica espacial» (44-reels-electronica.py): tiempos en datos_el.py y en la escena ════════════════════════
def _el():
    _fisica()
    import datos_el as DL
    return DL


def _fin_el(m, DL, nombre, mc):
    _leyendas_ats(mc, DL, nombre)
    _cierre_sonoro(m, _fisica(), DL.CUERPO[nombre])


_NOTAS_EL = (A(-24), A(-17), A(-10))            # colchón grave con séptima: «circuito»


def _golpe_ion(mc, t0, pan=0.0):
    mc.poner(t0 - 0.5, whoosh(0.6, 800, 4000, 0.04, 0.5), pan=pan)
    mc.poner(t0, clic(0.06, 2600), pan=pan); mc.poner(t0 + 0.02, golpe(70, 0.4, 0.14))


def el_bit(m):
    DL = _el(); F = _fisica()
    mc, tb = _base(m, DL, "ReelELBit", _NOTAS_EL, 0.25, (1200, 5000, 0.010))
    for k in range(10):
        mc.poner(0.2 + 0.12 * k, clic(0.04, 1500 + 90 * k), pan=-0.4 + 0.08 * k)          # las celdas
    _golpe_ion(mc, 3.2, -0.2); _golpe_ion(mc, 15.0, 0.3)
    mc.poner(7.4, glide(300, 900, 1.4, 0.04)); mc.poner(8.6, gota(1800, 0.15, 0.04))
    mc.poner(10.0, pluck(A(7), 1.2, 0.18)); mc.poner(13.2, pluck(A(5), 1.4, 0.16))
    _fin_el(m, DL, "ReelELBit", mc)


def el_voto(m):
    DL = _el(); F = _fisica()
    mc, tb = _base(m, DL, "ReelELVoto", _NOTAS_EL, 0.25, (1200, 5000, 0.010))
    for k in range(3):
        mc.poner(0.9 + 0.3 * k, pluck(A(-5 + 4 * k), 1.0, 0.14), pan=-0.4 + 0.4 * k)
    mc.poner(2.6, pluck(A(7), 1.2, 0.16))
    _golpe_ion(mc, 7.0, 0.0)
    mc.poner(8.8, clic(0.06, 1200)); mc.poner(10.2, clic(0.06, 1600))
    mc.poner(13.6, brillo_(0.8, 0.4)); mc.poner(13.7, pluck(A(12), 1.4, 0.18))
    _fin_el(m, DL, "ReelELVoto", mc)


def el_hamming(m):
    DL = _el(); F = _fisica()
    mc, tb = _base(m, DL, "ReelELHamming", _NOTAS_EL, 0.25, (1200, 5000, 0.010))
    for k in range(7):
        mc.poner(0.5 + 0.45 * k + (0.8 if k >= 4 else 0), clic(0.05, 1400 + 120 * k), pan=-0.45 + 0.15 * k)
    _golpe_ion(mc, 6.6, 0.2)
    for r, ok in enumerate((True, False, False)):
        mc.poner(8.0 + r, pluck(A(7) if ok else A(1), 0.9, 0.15), pan=-0.3 + 0.3 * r)
    mc.poner(11.0, pluck(A(5), 1.2, 0.16))
    mc.poner(13.2, brillo_(0.9, 0.4)); mc.poner(13.3, pluck(A(12), 1.5, 0.2))
    _fin_el(m, DL, "ReelELHamming", mc)


def el_dosis(m):
    DL = _el(); F = _fisica()
    mc, tb = _base(m, DL, "ReelELDosis", _NOTAS_EL, 0.25, (1200, 5000, 0.010))
    rng = np.random.default_rng(44)
    for j in range(26):
        mc.poner(0.8 + 0.43 * j, clic(0.03, rng.uniform(2200, 4200)), pan=rng.uniform(-0.6, 0.6))   # el «contador Geiger»
    for k in range(3):
        mc.poner(6.8 + 1.6 * k, pluck(A(-3 + 5 * k), 1.2, 0.16), pan=-0.3 + 0.3 * k)
    mc.poner(13.2, pluck(A(14), 1.6, 0.18))
    _fin_el(m, DL, "ReelELDosis", mc)


def el_latch(m):
    DL = _el(); F = _fisica()
    mc, tb = _base(m, DL, "ReelELLatch", _NOTAS_EL, 0.25, (1200, 5000, 0.010))
    _golpe_ion(mc, 3.6, -0.3)
    _zumbido(m, F, 3.7, 7.2, 110, 0.04)                                                      # la corriente desbocada
    t = np.arange(m.n) / SR
    m.sumar(np.sin(2 * np.pi * ciclo_entero(880, m.T) * t) * _env(m, F, 5.6, 7.2, 0.3, 0.05) * 0.010)   # alarma
    mc.poner(7.2, clic(0.1, 700)); mc.poner(7.25, golpe(50, 0.6, 0.18))
    mc.poner(8.6, clic(0.08, 1100)); mc.poner(8.8, pluck(A(7), 1.2, 0.16))
    _fin_el(m, DL, "ReelELLatch", mc)


def el_panel(m):
    DL = _el(); F = _fisica()
    mc, tb = _base(m, DL, "ReelELPanel", _NOTAS_EL, 0.25, (1200, 5000, 0.010))
    t = np.arange(m.n) / SR
    m.sumar(np.sin(2 * np.pi * ciclo_entero(A(12), m.T) * t) * _env(m, F, 1.8, 20.0, 1.2, 0.8) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t)) * 0.010)
    mc.poner(6.4, golpe(60, 0.6, 0.18)); mc.poner(6.5, pluck(A(7), 1.4, 0.2))
    mc.poner(8.2, glide(300, 500, 1.0, 0.03)); mc.poner(9.2, glide(300, 900, 1.0, 0.03))
    _fin_el(m, DL, "ReelELPanel", mc)


def el_bateria(m):
    DL = _el(); F = _fisica()
    mc, tb = _base(m, DL, "ReelELBateria", _NOTAS_EL, 0.25, (1200, 5000, 0.010))
    a0 = 0.75 - np.arcsin(2.9 / 3.4) / (2 * np.pi)
    for k in range(5):                                                                     # cada noche y cada amanecer
        mc.poner(4.0 * (k + a0), gota(500, 0.2, 0.04), pan=0.3)
        mc.poner(4.0 * (k + 1.5 - a0), gota(1100, 0.15, 0.04), pan=-0.3)
    mc.poner(13.0, pluck(A(7), 1.4, 0.18))
    _fin_el(m, DL, "ReelELBateria", mc)


def el_calor(m):
    DL = _el(); F = _fisica()
    mc, tb = _base(m, DL, "ReelELCalor", _NOTAS_EL, 0.25, (1200, 5000, 0.010))
    _siseo(m, F, 1.0, 12.0, 0.02, 600, 2500)                                                  # el aire del ventilador
    mc.poner(7.2, glide(250, 700, 3.0, 0.035))                                                # el termómetro sube
    mc.poner(13.0, golpe(55, 0.6, 0.16)); mc.poner(13.6, pluck(A(5), 1.4, 0.18))
    _fin_el(m, DL, "ReelELCalor", mc)


def el_bajada(m):
    DL = _el(); F = _fisica()
    mc, tb = _base(m, DL, "ReelELBajada", _NOTAS_EL, 0.25, (1200, 5000, 0.010))
    for k in range(4):
        t0 = 0.8 + 4.4 * k
        _siseo(m, F, t0, t0 + 3.4, 0.014, 3000, 7000)                                         # el enlace
        for j in range(10):
            mc.poner(t0 + 0.3 + 0.3 * j, clic(0.03, 2400 + 200 * (j % 3)), pan=-0.4 + 0.08 * j)
        mc.poner(t0 + 3.4, pluck(PENTA[k % 5] if k < 3 else A(12), 1.0, 0.13))
    _fin_el(m, DL, "ReelELBajada", mc)


def el_lento(m):
    DL = _el(); F = _fisica()
    mc, tb = _base(m, DL, "ReelELLento", _NOTAS_EL, 0.25, (1200, 5000, 0.010))
    for j in range(16):
        mc.poner(0.5 + 0.8 * j, clic(0.05, 900), pan=-0.3)                                     # el reloj lento
    mc.poner(7.0, golpe(60, 0.6, 0.16)); mc.poner(8.0, pluck(A(7), 1.2, 0.16))
    t = np.arange(m.n) / SR
    m.sumar(np.sign(np.sin(2 * np.pi * ciclo_entero(150, m.T) * t)) * _env(m, F, 13.0, 20.0, 0.8, 0.8)
            * (0.5 + 0.5 * np.sin(2 * np.pi * ciclo_entero(9 / np.pi, m.T) * t) ** 2) * 0.004)   # las aspas de Ingenuity
    mc.poner(13.4, pluck(A(12), 1.6, 0.18))
    _fin_el(m, DL, "ReelELLento", mc)


_FUNCIONES_EL = {"ReelELBit": el_bit, "ReelELVoto": el_voto, "ReelELHamming": el_hamming, "ReelELDosis": el_dosis,
                 "ReelELLatch": el_latch, "ReelELPanel": el_panel, "ReelELBateria": el_bateria, "ReelELCalor": el_calor,
                 "ReelELBajada": el_bajada, "ReelELLento": el_lento}


def _registrar_el():
    DL = _el()
    return {n: (f, DL.duracion(n), 0.0) for n, f in _FUNCIONES_EL.items()}


REELS_EL = _registrar_el()


# ══ Serie «Cálculo en el espacio» (45-reels-calculo.py): tiempos en datos_ca.py y en la escena ═══════════════════════════
def _ca():
    _fisica()
    import datos_ca as DC
    return DC


def _fin_ca(m, DC, nombre, mc):
    _leyendas_ats(mc, DC, nombre)
    _cierre_sonoro(m, _fisica(), DC.CUERPO[nombre])


_NOTAS_CA = (A(-24), A(-15), A(-12))            # colchón grave con sexta: «pizarrón tranquilo»


def ca_derivada(m):
    DC = _ca(); F = _fisica()
    mc, tb = _base(m, DC, "ReelCADerivada", _NOTAS_CA, 0.25, (900, 4000, 0.010))
    t = np.arange(m.n) / SR
    u = np.clip((t - F.H0 - 1.0) / 10.5, 0, 1)
    pend = 1 + 0.2 * np.pi * np.cos(2 * np.pi * (0.08 + 0.84 * (0.5 - 0.5 * np.cos(np.pi * u))))
    _tono(m, 220 * pend, _env(m, F, 1.0, 12.3, 0.4, 0.6), 0.02, F)                          # el tono sigue a la pendiente
    mc.poner(7.0, whoosh(4.8, 400, 2400, 0.05, 0.5)); mc.poner(11.8, pluck(A(7), 1.2, 0.18))
    mc.poner(13.0, golpe(55, 0.6, 0.16)); mc.poner(13.2, pluck(A(12), 1.4, 0.18))
    _fin_ca(m, DC, "ReelCADerivada", mc)


def ca_integral(m):
    DC = _ca(); F = _fisica()
    mc, tb = _base(m, DC, "ReelCAIntegral", _NOTAS_CA, 0.25, (900, 4000, 0.010))
    for j, (nb, t0) in enumerate(((4, 1.0), (8, 2.6), (16, 4.2))):
        for k in range(min(nb, 8)):
            mc.poner(t0 + 0.07 * k, clic(0.04, 1200 + 150 * j + 40 * k), pan=-0.4 + 0.1 * k)       # cada rebanada
    mc.poner(5.8, brillo_(0.8, 0.4))
    mc.poner(7.0, glide(300, 900, 2.0, 0.04)); mc.poner(9.0, pluck(A(7), 1.2, 0.18))
    mc.poner(13.0, gota(900, 0.2, 0.05)); mc.poner(14.5, pluck(A(-5), 1.2, 0.16))
    _fin_ca(m, DC, "ReelCAIntegral", mc)


def ca_maximo(m):
    DC = _ca(); F = _fisica()
    mc, tb = _base(m, DC, "ReelCAMaximo", _NOTAS_CA, 0.25, (900, 4000, 0.010))
    for j in range(3):
        t0 = 0.8 + 1.4 * j
        mc.poner(t0, golpe(80, 0.25, 0.12)); mc.poner(t0 + DC.T_AIRE_TIERRA_S, clic(0.06, 900))
    mc.poner(6.6, golpe(70, 0.4, 0.14)); mc.poner(6.6, glide(300, 700, DC.V_SALTO / 1.62, 0.035))
    mc.poner(6.6 + DC.V_SALTO / 1.62, pluck(A(12), 1.6, 0.2))                                  # arriba: pendiente cero
    mc.poner(6.6 + DC.V_SALTO / 1.62, glide(700, 300, DC.V_SALTO / 1.62, 0.03))
    mc.poner(6.6 + DC.T_AIRE_LUNA_S, golpe(60, 0.6, 0.16))
    mc.poner(12.8, pluck(A(7), 1.4, 0.16))
    _fin_ca(m, DC, "ReelCAMaximo", mc)


def ca_pasos(m):
    DC = _ca(); F = _fisica()
    mc, tb = _base(m, DC, "ReelCAPasos", _NOTAS_CA, 0.25, (900, 4000, 0.010))
    for k in range(DC.PASOS_MAL):
        mc.poner(0.8 + 8.2 * k / DC.PASOS_MAL, clic(0.05, 900 + 60 * k), pan=-0.4 + 0.04 * k)    # cada paso, cada vez más agudo
    mc.poner(12.8, whoosh(3.2, 300, 1500, 0.04, 0.5)); mc.poner(16.0, pluck(A(12), 1.6, 0.2))
    _fin_ca(m, DC, "ReelCAPasos", mc)


def ca_giro(m):
    DC = _ca(); F = _fisica()
    mc, tb = _base(m, DC, "ReelCAGiro", _NOTAS_CA, 0.25, (900, 4000, 0.010))
    _zumbido(m, F, 0.4, 20.0, 90, 0.02, vib=2.0)                                              # el anillo que gira
    mc.poner(1.6, pluck(A(5), 1.0, 0.14)); mc.poner(3.4, pluck(A(0), 1.0, 0.14))
    mc.poner(7.0, golpe(55, 0.6, 0.16)); mc.poner(7.2, pluck(A(7), 1.4, 0.18))
    mc.poner(13.0, glide(400, 1100, 1.2, 0.04))
    _fin_ca(m, DC, "ReelCAGiro", mc)


def ca_tasas(m):
    DC = _ca(); F = _fisica()
    mc, tb = _base(m, DC, "ReelCATasas", _NOTAS_CA, 0.25, (900, 4000, 0.010))
    S = 1 / (1 / 3.6 - 1 / (3.6 * DC.T_MARTE_D / DC.T_TIERRA_D))
    for k in range(3):
        t0 = 1.0 + k * S
        if t0 < 20:
            mc.poner(t0, brillo_(0.8, 0.4)); mc.poner(t0, pluck(A(12), 1.4, 0.18))             # cada alineación
    for k in range(6):
        mc.poner(1.0 + 3.6 * k, gota(700, 0.12, 0.03), pan=-0.3)                                # cada año de la Tierra
    _fin_ca(m, DC, "ReelCATasas", mc)


def ca_plutonio(m):
    DC = _ca(); F = _fisica()
    mc, tb = _base(m, DC, "ReelCAPlutonio", _NOTAS_CA, 0.25, (900, 4000, 0.010))
    for k in range(4):
        mc.poner(1.6 + 1.0 * k, pluck(A(12 - 5 * k), 1.0, 0.18 / (k + 1) ** 0.5), pan=-0.3 + 0.2 * k)   # cada mitad, más grave
    mc.poner(7.0, pluck(A(7), 1.2, 0.16)); mc.poner(8.4, glide(600, 480, 1.6, 0.03))
    mc.poner(13.6, glide(600, 300, 1.6, 0.035))
    _fin_ca(m, DC, "ReelCAPlutonio", mc)


def ca_aire(m):
    DC = _ca(); F = _fisica()
    mc, tb = _base(m, DC, "ReelCAAire", _NOTAS_CA, 0.25, (900, 4000, 0.010))
    _siseo(m, F, 0.4, 12.0, 0.018, 600, 3000)                                                 # el aire
    for k in range(1, 6):
        mc.poner(1.6 + 0.8 * k, pluck(A(-5 + 3 * k), 0.9, 0.16 / k ** 0.5), pan=-0.3 + 0.12 * k)
    mc.poner(7.0, golpe(60, 0.5, 0.14)); mc.poner(9.0, whoosh(1.2, 500, 1500, 0.04, 0.5))
    mc.poner(13.0, glide(400, 1600, 2.0, 0.03))
    _fin_ca(m, DC, "ReelCAAire", mc)


def ca_horizonte(m):
    DC = _ca(); F = _fisica()
    mc, tb = _base(m, DC, "ReelCAHorizonte", _NOTAS_CA, 0.25, (900, 4000, 0.010))
    for t0, nota in ((0.8, A(0)), (6.8, A(7)), (13.3, A(12))):
        mc.poner(t0 - 0.8, whoosh(1.6, 300, 1500, 0.035, 0.6)); mc.poner(t0, pluck(nota, 1.4, 0.18))
    mc.poner(7.6, brillo_(0.6, 0.3))
    _fin_ca(m, DC, "ReelCAHorizonte", mc)


def ca_tunel(m):
    DC = _ca(); F = _fisica()
    mc, tb = _base(m, DC, "ReelCATunel", _NOTAS_CA, 0.25, (900, 4000, 0.010))
    t = np.arange(m.n) / SR
    fase = 2 * np.pi * np.clip(t - F.H0 - 1.0, 0, None) / 8.0
    _tono(m, 260 + 140 * np.abs(np.sin(fase)), _env(m, F, 1.0, 20.0, 0.6, 0.6), 0.018, F)     # más agudo al pasar por el centro
    for k in range(4):
        mc.poner(1.0 + 4.0 * k + 4.0, clic(0.08, 1000), pan=(-0.3, 0.3)[k % 2])                 # cada llegada a un extremo
    mc.poner(5.2, pluck(A(7), 1.2, 0.16)); mc.poner(13.4, pluck(A(12), 1.4, 0.18))
    _fin_ca(m, DC, "ReelCATunel", mc)


_FUNCIONES_CA = {"ReelCADerivada": ca_derivada, "ReelCAIntegral": ca_integral, "ReelCAMaximo": ca_maximo, "ReelCAPasos": ca_pasos,
                 "ReelCAGiro": ca_giro, "ReelCATasas": ca_tasas, "ReelCAPlutonio": ca_plutonio, "ReelCAAire": ca_aire,
                 "ReelCAHorizonte": ca_horizonte, "ReelCATunel": ca_tunel}


def _registrar_ca():
    DC = _ca()
    return {n: (f, DC.duracion(n), 0.0) for n, f in _FUNCIONES_CA.items()}


REELS_CA = _registrar_ca()

REELS_DATOS = {"ReelDopplerReal": (doppler_real, 12.0, 4.2)}

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
    grupos = [(raiz / "marca-codeaerospace/reels-promo", REELS), (raiz / "estudio/logo_vivo", REELS_VIVO),
              (raiz / "estudio/reels_datos", REELS_DATOS), (raiz / "estudio/reels_divulgacion", REELS_DIVULGACION),
              (raiz / "estudio/reels_ats", REELS_ATS), (raiz / "estudio/reels_triage", REELS_TRIAGE),
              (raiz / "estudio/reels_clima", REELS_CLIMA),
              (raiz / "estudio/reels_ia", REELS_IA),
              (raiz / "estudio/reels_robotica", REELS_ROB),
              (raiz / "estudio/reels_em", REELS_EM),
              (raiz / "estudio/reels_electronica", REELS_EL),
              (raiz / "estudio/reels_calculo", REELS_CA)]
    if len(sys.argv) > 1:
        grupos = [(Path(sys.argv[1]), {**REELS, **REELS_VIVO, **REELS_DATOS, **REELS_DIVULGACION, **REELS_ATS, **REELS_TRIAGE, **REELS_CLIMA, **REELS_IA, **REELS_ROB, **REELS_EM, **REELS_EL, **REELS_CA})]
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

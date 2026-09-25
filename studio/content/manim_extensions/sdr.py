"""Radio definida por software: la radio real, eslabon a eslabon.

Libreria de la familia "SDR" (curso 38, 24 lecciones). El principio que la
ordena: **una radio es una cadena de aritmetica y cada eslabon deja una
huella medible**. Toda funcion numerica devuelve lo MEDIDO sobre la senal
que se dibuja; lo que viene de una norma o de una hoja de datos se devuelve
aparte (constantes en mayusculas) para que el clip lo pinte en gris.

Sustrato que reutiliza (no duplica):
  algebra_lineal : _Anclada, fmt
  comunicaciones : PlanoIQ (el plano I/Q), constelaciones, awgn
  dsp            : escalones (cuantizador), Escalera
  bloques        : bloque, conectar, flujo

`scipy.signal` SOLO en la sonda (studio/tools/sonda_sdr.py) como oraculo
independiente; lo que el espectador ve funcionando se implementa aqui en
numpy.

Convenciones:
- senales complejas de banda base en np.complex128, fs en Hz;
- `espectro_db(x, fs)` -> (f, db) con f CENTRADA (fftshift) para senales
  complejas y db relativo al maximo (o a `ref`);
- semillas fijas en todas partes.
"""

import math

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Circle, DashedLine, Dot,
                   ImageMobject, Line, Polygon, Rectangle, Text, VGroup,
                   VMobject)

from algebra_lineal import _Anclada, fmt  # noqa: F401
from bloques import bloque, conectar, flujo  # noqa: F401
from code_brand import FUENTE_HUD
from comunicaciones import PlanoIQ  # noqa: F401
from dsp import Escalera, escalones  # noqa: F401

# =====================================================================
# Paleta por ROL (el color dice el papel; ver §8 del plan)
# =====================================================================
C_CALCULO = "#22d3ee"   # cian: cifra calculada aqui
C_SENAL = "#f59e0b"     # ambar: la senal que se quiere recibir
C_I = "#3b82f6"         # azul: componente I
C_Q = "#a78bfa"         # violeta: componente Q
C_LO = "#e879f9"        # fucsia: lo que PONE el receptor (LO, NCO, lazo)
C_RUIDO = "#f43f5e"     # rojo: ruido, imagen, espurio, interferente
C_OK = "#34d399"        # verde: lo recuperado, lo decodificado
C_DATO = "#94a0b0"      # gris: norma, hoja de datos, parametro elegido
C_EJE = "#31414f"       # mobiliario
C_TENUE = "#8b98a8"

K_BOLTZMANN = 1.380649e-23
T0 = 290.0

# Hoja de datos del RTL-SDR (R820T2 + RTL2832U). GRIS en pantalla.
RTL = {
    "fs": 2.4e6,            # tasa estable habitual (muestras complejas/s)
    "bits": 8,
    "f_min": 24e6,
    "f_max": 1766e6,
}


# =====================================================================
# 0. Utilidades de medida
# =====================================================================
def db10(p):
    return 10.0 * np.log10(np.maximum(np.asarray(p, float), 1e-300))


def ventana(nombre, n):
    if nombre in (None, "rect"):
        return np.ones(n)
    if nombre == "hann":
        return 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n) / n)
    if nombre == "blackman":
        k = 2 * np.pi * np.arange(n) / n
        return 0.42 - 0.5 * np.cos(k) + 0.08 * np.cos(2 * k)
    raise ValueError(nombre)


def espectro_db(x, fs, nfft=None, ventana_nombre="hann", ref=None,
                promedios=None):
    """Espectro (Welch sin solape) en dB. Devuelve (f, db).

    - Compleja: f de -fs/2 a fs/2 (fftshift). Real: tambien los dos lados,
      para que se VEA la simetria que tiene una senal real.
    - `ref=None` normaliza al maximo (0 dB); `ref="abs"` devuelve potencia
      por bin sin normalizar (para comparar dos espectros entre si).
    """
    x = np.asarray(x)
    nfft = int(nfft or min(len(x), 4096))
    nseg = len(x) // nfft if promedios is None else int(promedios)
    nseg = max(1, min(nseg, len(x) // nfft))
    w = ventana(ventana_nombre, nfft)
    acc = np.zeros(nfft)
    for k in range(nseg):
        seg = x[k * nfft:(k + 1) * nfft] * w
        acc += np.abs(np.fft.fft(seg)) ** 2
    p = np.fft.fftshift(acc / (nseg * np.sum(w) ** 2))
    f = np.fft.fftshift(np.fft.fftfreq(nfft, 1.0 / fs))
    if ref is None:
        d = db10(p) - db10(p.max())
    elif ref == "abs":
        d = db10(p)
    else:
        d = db10(p) - float(ref)
    return f, d


def pico(f, db, f_lo=None, f_hi=None):
    """Frecuencia (interpolacion parabolica) y nivel del maximo en un tramo."""
    f = np.asarray(f)
    db = np.asarray(db)
    m = np.ones_like(f, bool)
    if f_lo is not None:
        m &= f >= f_lo
    if f_hi is not None:
        m &= f <= f_hi
    idx = np.flatnonzero(m)
    k = idx[np.argmax(db[idx])]
    if 0 < k < len(f) - 1:
        a, b, c = db[k - 1], db[k], db[k + 1]
        den = a - 2 * b + c
        d = 0.5 * (a - c) / den if den != 0 else 0.0
        df = f[1] - f[0]
        return float(f[k] + d * df), float(b - 0.25 * (a - c) * d)
    return float(f[k]), float(db[k])


def para_dibujar(f, db, puntos=900, f_lo=None, f_hi=None):
    """Reduce un espectro largo a `puntos` columnas tomando el MAXIMO de
    cada columna (asi un tono de un bin no desaparece al diezmar, que es
    lo que hace un analizador). Recorta antes a [f_lo, f_hi]."""
    f = np.asarray(f, float)
    db = np.asarray(db, float)
    m = np.ones_like(f, bool)
    if f_lo is not None:
        m &= f >= f_lo
    if f_hi is not None:
        m &= f <= f_hi
    f, db = f[m], db[m]
    if len(f) <= puntos:
        return f, db
    k = len(f) // puntos
    n = k * puntos
    return (f[:n].reshape(puntos, k).mean(axis=1),
            db[:n].reshape(puntos, k).max(axis=1))


def potencia_tono(x, f, fs):
    """Potencia de la componente compleja exp(j2*pi*f*n/fs) de x (proyeccion
    exacta, sin malla): |<x, e>|^2 / N^2."""
    n = np.arange(len(x))
    e = np.exp(-2j * np.pi * f * n / fs)
    return float(np.abs(np.sum(x * e) / len(x)) ** 2)


def tono(f, fs, n, amp=1.0, fase=0.0, complejo=True):
    t = np.arange(n) / fs
    if complejo:
        return amp * np.exp(1j * (2 * np.pi * f * t + fase))
    return amp * np.cos(2 * np.pi * f * t + fase)


def ruido_complejo(n, potencia=1.0, semilla=1):
    r = np.random.default_rng(semilla)
    s = math.sqrt(potencia / 2.0)
    return s * (r.standard_normal(n) + 1j * r.standard_normal(n))


# =====================================================================
# 1.1 De la antena al numero
# =====================================================================
def caudal_bps(fs=RTL["fs"], bits=RTL["bits"], canales=2):
    """Bits por segundo que salen por el USB: fs * (I y Q) * bits."""
    return float(fs * canales * bits)


def caudal_audio(fs=48000.0, bits=16, canales=1):
    return float(fs * canales * bits)


def reduccion():
    return caudal_bps() / caudal_audio()


# Banda de FM comercial (reglamento de las Americas: canales de 200 kHz en
# decimas impares). Emisoras SINTETICAS: frecuencias y niveles elegidos con
# semilla; lo medido es cuantas caben en la ventana.
def banda_fm(semilla=38, n=22):
    r = np.random.default_rng(semilla)
    canales = np.round(np.arange(88.1, 108.0, 0.2), 1)
    elegidas = np.sort(r.choice(canales, size=n, replace=False))
    niveles = r.uniform(-58.0, -12.0, size=n)
    niveles[np.argmax(niveles)] = 0.0
    return elegidas * 1e6, niveles


def espectro_banda_fm(semilla=38, f0=87.5e6, f1=108.5e6, puntos=1050,
                      piso=-80.0):
    """Espectro DIBUJABLE de la banda FM (dB relativos): cada emisora es una
    meseta de ~180 kHz sobre un piso con rizado. Es un modelo de la forma,
    no una captura: las cifras que se rotulan son conteos (emisoras_en)."""
    fe, ne = banda_fm(semilla)
    f = np.linspace(f0, f1, puntos)
    r = np.random.default_rng(semilla + 1)
    p = 10 ** ((piso + 2.0 * r.standard_normal(puntos)) / 10)
    for fc, lv in zip(fe, ne):
        forma = np.exp(-((f - fc) / 85e3) ** 6)
        p += 10 ** (lv / 10) * forma
    return f, db10(p)


def emisoras_en(centro, ancho=RTL["fs"], semilla=38):
    """Emisoras cuyo canal (+-100 kHz) cae ENTERO dentro de la ventana."""
    fe, _ = banda_fm(semilla)
    m = np.abs(fe - centro) <= ancho / 2 - 100e3
    return int(np.sum(m)), fe[m]


def sqnr_adc(bits, n=1 << 16, semilla=3, amp=0.999):
    """SQNR MEDIDA de un seno casi a fondo de escala cuantizado a `bits`
    (rango [-1, 1], 2^bits niveles). Frecuencia inconmensurable con fs para
    que el error se reparta como ruido."""
    r = np.random.default_rng(semilla)
    t = np.arange(n)
    x = amp * np.sin(2 * np.pi * 0.0123456789 * t + r.uniform(0, 2 * np.pi))
    xq, err, _ = escalones(x, bits)
    return float(db10(np.mean(x ** 2)) - db10(np.mean(err ** 2)))


def sqnr_teorica(bits):
    return 6.02 * bits + 1.76


# =====================================================================
# 1.2 Mezclar es multiplicar
# =====================================================================
FS_RF = 500e6       # malla de simulacion en RF (parametro, no se rotula)
N_RF = 1 << 15
F_SENAL = 100.3e6   # la emisora que se quiere
F_IF = 10.7e6       # la FI clasica de FM (dato)
F_LO = F_SENAL - F_IF   # 89.6 MHz
F_IMAGEN = F_LO - F_IF  # 78.9 MHz


def mezclar_real(f1=F_SENAL, f2=F_LO, fs=FS_RF, n=N_RF):
    """cos(f1) * cos(f2). Devuelve (f, db, [f_suma, f_dif] medidas)."""
    x = tono(f1, fs, n, complejo=False) * tono(f2, fs, n, complejo=False)
    f, d = espectro_db(x, fs, nfft=n, ventana_nombre="blackman")
    fs_med, _ = pico(f, d, f_lo=0.5 * (f1 + f2), f_hi=fs / 2)
    fd_med, _ = pico(f, d, f_lo=1e6, f_hi=0.5 * (f1 + f2))
    return f, d, (fs_med, fd_med)


def imagen_real(f_lo=F_LO, f_if=F_IF):
    """Las dos frecuencias de RF que un mezclador REAL lleva a la misma FI."""
    return f_lo + f_if, f_lo - f_if


def mezcla_imagen(f_lo=F_LO, f_if=F_IF, fs=FS_RF, n=N_RF, complejo=False,
                  nivel_imagen_db=-6.0):
    """La emisora (f_lo+f_if) y una emisora en la imagen (f_lo-f_if), las dos
    reales, mezcladas con un LO real o complejo. Devuelve las potencias
    MEDIDAS (proyeccion exacta) de cada una al llegar a +f_if y a -f_if:
    {"deseada": (p_mas, p_menos), "imagen": (p_mas, p_menos)} en dB."""
    a_img = 10 ** (nivel_imagen_db / 20)
    t = np.arange(n) / fs
    lo = np.exp(-2j * np.pi * f_lo * t) if complejo else \
        np.cos(2 * np.pi * f_lo * t)
    out = {}
    for nombre, fr, a in (("deseada", f_lo + f_if, 1.0),
                          ("imagen", f_lo - f_if, a_img)):
        y = a * np.cos(2 * np.pi * fr * t) * lo
        out[nombre] = (float(db10(potencia_tono(y, +f_if, fs))),
                       float(db10(potencia_tono(y, -f_if, fs))))
    return out


def desplazar(x, f, fs):
    """Multiplica por exp(-j2*pi*f*n/fs): el espectro se corre -f."""
    n = np.arange(len(x))
    return x * np.exp(-2j * np.pi * f * n / fs)


def captura_banda(centro=98.0e6, fs=RTL["fs"], n=1 << 14, semilla=38,
                  snr_piso=-70.0):
    """Captura COMPLEJA sintetica de la ventana de un RTL-SDR centrada en
    `centro`: cada emisora de banda_fm dentro de la ventana es un tono FM
    de banda estrecha (tono con modulacion suave) a su offset. Para los
    espectros de las lecciones de mezcla y NCO."""
    fe, ne = banda_fm(semilla)
    r = np.random.default_rng(semilla + 7)
    t = np.arange(n) / fs
    x = ruido_complejo(n, 10 ** (snr_piso / 10), semilla + 11)
    for fc, lv in zip(fe, ne):
        off = fc - centro
        if abs(off) < fs / 2 - 60e3:
            a = 10 ** (lv / 20)
            fm = r.uniform(400, 1500)
            beta = r.uniform(20, 45)
            x = x + a * np.exp(1j * (2 * np.pi * off * t
                                     + beta * np.sin(2 * np.pi * fm * t)
                                     + r.uniform(0, 2 * np.pi)))
    return x


# =====================================================================
# 1.3 Las cicatrices del cero-IF
# =====================================================================
def desbalance_iq(x, eps=0.05, phi_deg=3.0):
    """Modelo de desbalance de ganancia (1+eps) y fase phi en la rama Q:
    I' = I ;  Q' = g (Q cos phi - I sin phi).
    Equivale a y = mu x + nu conj(x) con mu = (1 + g e^-jphi)/2,
    nu = (1 - g e^jphi)/2."""
    g = 1.0 + eps
    p = math.radians(phi_deg)
    i, q = x.real, x.imag
    return i + 1j * g * (q * math.cos(p) - i * math.sin(p))


def irr_db(eps=0.05, phi_deg=3.0):
    """Rechazo de imagen TEORICO: |mu|^2 / |nu|^2."""
    g = 1.0 + eps
    c = math.cos(math.radians(phi_deg))
    return 10 * math.log10((1 + 2 * g * c + g * g) / (1 - 2 * g * c + g * g))


def irr_medida(y, x):
    """IRR MEDIDA sin malla: ajusta y = a x + b conj(x) por minimos
    cuadrados contra la senal limpia conocida x; IRR = |a|^2/|b|^2."""
    A = np.column_stack([x, np.conj(x)])
    (a, b), *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(10 * np.log10(np.abs(a) ** 2 / max(np.abs(b) ** 2, 1e-300)))


def corregir_iq(y):
    """Correccion CIEGA (Gram-Schmidt por momentos): quita a Q' la parte
    correlada con I' y la iguala en potencia. Solo usa estadisticas de y."""
    i, q = y.real.copy(), y.imag.copy()
    i = i - i.mean()
    q = q - q.mean()
    q1 = q - (np.mean(i * q) / np.mean(i * i)) * i
    q1 *= math.sqrt(np.mean(i * i) / np.mean(q1 * q1))
    return i + 1j * q1


def senal_iq_prueba(n=1 << 14, fs=RTL["fs"], f=180e3, snr_db=45.0,
                    semilla=5):
    """Un tono complejo en +f con ruido (la senal limpia y la ruidosa)."""
    x = tono(f, fs, n)
    return x, x + ruido_complejo(n, 10 ** (-snr_db / 10), semilla)


def irr_corregida_minima(eps=0.05, phi_deg=3.0):
    """La IRR tras la correccion ciega DEPENDE DE LA MALLA (82 dB con 8192
    muestras, 130 con 12000: el tono no cierra ciclos y sesga los
    momentos). Se rotula solo el SUELO del barrido, redondeado hacia abajo
    a decenas: "mas de X dB". Devuelve (suelo_decenas, minimo, maximo)."""
    vals = []
    for n in (8192, 12000, 16384, 32768):
        for sem in (1, 2, 3):
            xl, xn = senal_iq_prueba(n=n, semilla=sem)
            vals.append(irr_medida(corregir_iq(desbalance_iq(xn, eps,
                                                             phi_deg)), xl))
    return int(10 * math.floor(min(vals) / 10)), min(vals), max(vals)


def con_dc(x, nivel_dbc=-12.0, fase=0.7):
    """Suma el offset de DC (fuga del LO) a `nivel_dbc` de la senal."""
    p = np.mean(np.abs(x) ** 2)
    return x + math.sqrt(p * 10 ** (nivel_dbc / 10)) * np.exp(1j * fase)


def quitar_dc(x, alfa=0.995):
    """Bloqueador de DC IIR: y[n] = x[n] - x[n-1] + alfa y[n-1]."""
    y = np.empty_like(x)
    prev_x = 0.0
    prev_y = 0.0
    for k, v in enumerate(x):
        prev_y = v - prev_x + alfa * prev_y
        prev_x = v
        y[k] = prev_y
    return y


def dc_dbc(x, ref_p=None, desde=0):
    """Nivel de la componente de DC (media) respecto a la potencia de la
    senal `ref_p` (o de x). Coherente: no depende de la malla."""
    x = np.asarray(x)[desde:]
    p = np.mean(np.abs(x) ** 2) if ref_p is None else ref_p
    return float(db10(np.abs(np.mean(x)) ** 2 / p))


# =====================================================================
# 2.1 El piso de ruido
# =====================================================================
def ktb_dbm(b_hz=1.0, t=T0):
    return float(10 * math.log10(K_BOLTZMANN * t * b_hz * 1000.0))


def friis(etapas):
    """etapas = [(ganancia_db, nf_db), ...] en orden desde la antena.
    Devuelve la NF total en dB."""
    f_tot = 0.0
    g_acum = 1.0
    for k, (g_db, nf_db) in enumerate(etapas):
        f = 10 ** (nf_db / 10)
        f_tot += f if k == 0 else (f - 1) / g_acum
        g_acum *= 10 ** (g_db / 10)
    return float(10 * math.log10(f_tot))


# Parametros ELEGIDOS de la cascada del 2.1 (gris en pantalla)
CABLE = (-3.0, 3.0)        # 3 dB de perdidas: NF = perdida
LNA = (20.0, 0.8)
RECEPTOR = (30.0, 6.0)     # el propio SDR


def sensibilidad_dbm(b_hz, nf_db, snr_min_db):
    return ktb_dbm(b_hz) + nf_db + snr_min_db


def snr_db(p_senal_dbm, b_hz, nf_db):
    return p_senal_dbm - (ktb_dbm(b_hz) + nf_db)


def snr_medida(p_senal_dbm, b_hz, nf_db, n=1 << 15, semilla=9):
    """La misma SNR, MEDIDA: un tono y ruido complejo con la potencia de
    kTB*F*B, en unidades de mW; se estima el tono por proyeccion y el
    ruido por el residuo."""
    fs = b_hz
    ps = 10 ** (p_senal_dbm / 10)
    pn = 10 ** ((ktb_dbm(b_hz) + nf_db) / 10)
    x = tono(0.1234 * fs, fs, n, amp=math.sqrt(ps))
    y = x + ruido_complejo(n, pn, semilla)
    a = np.vdot(x, y) / np.vdot(x, x)
    res = y - a * x
    return float(db10(np.abs(a) ** 2 * ps) - db10(np.mean(np.abs(res) ** 2)))


# =====================================================================
# 2.2 La ganancia justa (ADC de 8 bits)
# =====================================================================
def adc(x, bits=8, fondo=1.0):
    """ADC complejo: recorta I y Q a +-fondo y cuantiza a 2^bits niveles."""
    def q(v):
        v = np.clip(v, -fondo, fondo * (1 - 2.0 / 2 ** bits))
        paso = 2 * fondo / 2 ** bits
        return (np.floor(v / paso) + 0.5) * paso
    return q(x.real) + 1j * q(x.imag)


def niveles_usados(x, bits=8):
    y = adc(x, bits)
    return int(len(np.unique(np.round(y.real * 2 ** bits))))


def escenario_ganancia(n=1 << 14, semilla=21, snr_entrada_db=30.0):
    """Senal de prueba del 2.2: un tono complejo (amplitud 1 por
    convencion) y ruido termico a `snr_entrada_db`. La ganancia escala el
    conjunto antes del ADC."""
    fs = 1.0
    x = tono(0.0371, fs, n)
    w = ruido_complejo(n, 10 ** (-snr_entrada_db / 10), semilla)
    return x, w


def sinad_tras_adc(ganancia_db, x, w, bits=8, nivel_ref_db=-60.0):
    """SINAD MEDIDA a la salida del ADC. La senal entra a `nivel_ref_db`
    dBFS con ganancia 0 dB; se ajusta y = a*x (proyeccion) y todo lo demas
    (ruido termico + cuantizacion + recorte) es el residuo."""
    g = 10 ** ((ganancia_db + nivel_ref_db) / 20)
    y = adc(g * (x + w), bits)
    a = np.vdot(x, y) / np.vdot(x, x)
    res = y - a * x
    return float(db10(np.abs(a) ** 2) - db10(np.mean(np.abs(res) ** 2)))


def snr_vs_ganancia(ganancias_db=None, **kw):
    if ganancias_db is None:
        ganancias_db = np.arange(0.0, 76.0, 1.0)
    x, w = escenario_ganancia(**kw)
    return np.asarray(ganancias_db, float), np.array(
        [sinad_tras_adc(g, x, w) for g in ganancias_db])


def punto_dulce(g, s, tolerancia_db=1.0):
    """El tramo de ganancias a menos de `tolerancia_db` del maximo y su
    centro (mas estable que el argmax puro, que baila con el ruido)."""
    m = s >= s.max() - tolerancia_db
    idx = np.flatnonzero(m)
    return float(g[idx[0]]), float(g[idx[-1]]), float(0.5 * (g[idx[0]]
                                                              + g[idx[-1]])), float(s.max())


def espurio_max_dbc(ganancia_db, bits=8, nivel_ref_db=-60.0, n=1 << 14):
    """Recorte de un tono complejo EN BIN: nivel del mayor espurio (fuera
    del tono) respecto al tono, en dBc. Coherente: estable con la malla."""
    k = 611
    x = np.exp(2j * np.pi * k * np.arange(n) / n)
    g = 10 ** ((ganancia_db + nivel_ref_db) / 20)
    y = adc(g * x, bits)
    Y = np.abs(np.fft.fft(y)) ** 2
    pt = Y[k]
    Y[k] = 0
    return float(db10(Y.max() / pt)), int(np.argmax(Y))


def agc(env_db, ref=0.5, mu=0.02, g0_db=0.0):
    """AGC de lazo sobre una envolvente (en dB, por muestra lenta):
    g[n+1] = g[n] + mu * (ref_db - salida_db). Devuelve la salida en dB."""
    ref_db = 20 * math.log10(ref)
    g = g0_db
    out = np.empty_like(env_db)
    for k, e in enumerate(env_db):
        out[k] = e + g
        g += mu * (ref_db - out[k]) * 10
    return out


def desvanecimiento(n=600, rango_db=30.0, semilla=4):
    """Envolvente lenta que recorre `rango_db` (parametro elegido)."""
    r = np.random.default_rng(semilla)
    t = np.linspace(0, 1, n)
    base = -rango_db / 2 * np.cos(2 * np.pi * 1.5 * t) - rango_db / 2 * 0.0
    return base + 1.0 * np.convolve(r.standard_normal(n), np.ones(15) / 15,
                                    mode="same")


# =====================================================================
# 2.3 Senales que saturan
# =====================================================================
FS_IM = 400e6
N_IM = 4000                 # bin = 0.1 MHz: todos los tonos caen en bin
F_IM1, F_IM2 = 98.1e6, 98.5e6
A1_AMP, A3_AMP = 10.0, -1.0    # y = a1 x + a3 x^3  (parametros elegidos)


def amplificador(x, a1=A1_AMP, a3=A3_AMP):
    return a1 * x + a3 * x ** 3


def iip3_teorico(a1=A1_AMP, a3=A3_AMP):
    """Amplitud de entrada (por tono) del punto de interseccion de 3.er
    orden: sqrt(4/3 |a1/a3|). En dB respecto a amplitud 1."""
    return 20 * math.log10(math.sqrt(4.0 / 3.0 * abs(a1 / a3)))


def dos_tonos_im(amp, fs=FS_IM, n=N_IM, f1=F_IM1, f2=F_IM2):
    """Salida del amplificador con dos tonos de amplitud `amp`. Devuelve
    (f, db_abs, niveles) con niveles = dict de potencia MEDIDA (dB) de la
    fundamental f1 y de los productos 2f1-f2 y 2f2-f1 (proyeccion)."""
    t = np.arange(n) / fs
    x = amp * (np.cos(2 * np.pi * f1 * t) + np.cos(2 * np.pi * f2 * t))
    y = amplificador(x)
    niv = {}
    for nombre, f in (("fund", f1), ("im_bajo", 2 * f1 - f2),
                      ("im_alto", 2 * f2 - f1)):
        niv[nombre] = float(db10(4 * potencia_tono(y, f, fs)))
    f, d = espectro_db(y, fs, nfft=n, ventana_nombre="blackman", ref="abs")
    return f, d, niv


def recta_ip3(amps_db=None):
    """Barrido de entrada: niveles medidos de fundamental e IM3, pendientes
    ajustadas en el tramo bajo y el IIP3 extrapolado (dB re amplitud 1)."""
    if amps_db is None:
        amps_db = np.arange(-40.0, -9.0, 2.0)
    fund, im = [], []
    for a_db in amps_db:
        _, _, niv = dos_tonos_im(10 ** (a_db / 20))
        fund.append(niv["fund"])
        im.append(niv["im_bajo"])
    fund, im = np.array(fund), np.array(im)
    bajo = amps_db <= -20
    p1 = np.polyfit(amps_db[bajo], fund[bajo], 1)
    p3 = np.polyfit(amps_db[bajo], im[bajo], 1)
    iip3 = (p1[1] - p3[1]) / (p3[0] - p1[0])
    return {"entrada_db": amps_db, "fund_db": fund, "im3_db": im,
            "pendiente_1": float(p1[0]), "pendiente_3": float(p3[0]),
            "iip3_db": float(iip3), "oip3_db": float(np.polyval(p1, iip3)),
            "ajuste_1": p1, "ajuste_3": p3}


AMP_BLOQUEADOR = 2.2     # amplitud del bloqueador (el IIP3 es 3.65)
ATEN_FILTRO_DB = 40.0    # rechazo del filtro de banda FM (parametro)


def ganancia_debil(amp_bloqueador, amp_debil=1e-3, fs=FS_IM, n=N_IM,
                   f_blq=F_IM1, f_deb=137.1e6):
    """Ganancia (dB) que ve una senal DEBIL en f_deb cuando un bloqueador
    de amplitud `amp_bloqueador` comprime el amplificador (desensibilizacion).
    Medida por proyeccion."""
    t = np.arange(n) / fs
    x = amp_debil * np.cos(2 * np.pi * f_deb * t) + \
        amp_bloqueador * np.cos(2 * np.pi * f_blq * t)
    y = amplificador(x)
    return float(db10(4 * potencia_tono(y, f_deb, fs)) -
                 db10(amp_debil ** 2))


# =====================================================================
# Dibujo
# =====================================================================
def _hud(texto, font_size=18, color=C_TENUE):
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


class Espectro(_Anclada):
    """Espectro en dB en MARCO PROPIO (no Axes: no cruza por el origen).

    Espectro(f, db, piso=-80, techo=0, ancho=10, alto=3, color=C_SENAL)
      .ejes  .curva  .area
      .en(f, db)                 punto de pantalla
      .marca_f(f, color)         vertical punteada del suelo al techo
      .banda(f0, f1, color, op)  rectangulo translucido de f0 a f1
      .con_db(db2, color)        GEMELA (mismo f, mismo marco)
      .marcas(valores, textos)   ticks + rotulos Space Mono bajo el eje

    La curva se RECORTA a [piso, techo] antes de dibujar (no hay segmentos
    pegados al borde por np.clip: los puntos fuera se ponen en el borde,
    que es lo que se ve en un analizador real).
    """

    def __init__(self, f, db, piso=-80.0, techo=0.0, ancho=10.0, alto=3.0,
                 color=C_SENAL, area=True, grosor=2.4, **kwargs):
        super().__init__(**kwargs)
        self.f = np.asarray(f, float)
        self.db = np.asarray(db, float)
        self.piso, self.techo = float(piso), float(techo)
        self.ancho, self.alto = float(ancho), float(alto)
        self.color = color
        self._con_area = area
        self._grosor = grosor
        self._poner_ancla(ORIGIN)
        ex = Line(self.en(self.f[0], self.piso), self.en(self.f[-1], self.piso),
                  color=C_EJE, stroke_width=1.8)
        self.ejes = VGroup(ex)
        pts = [self.en(a, b) for a, b in zip(self.f, self.db)]
        self.curva = VMobject(stroke_color=color, stroke_width=grosor)
        self.curva.set_points_as_corners(pts)
        if area:
            self.area = Polygon(self.en(self.f[0], self.piso), *pts,
                                self.en(self.f[-1], self.piso),
                                stroke_width=0, fill_color=color,
                                fill_opacity=0.16)
        else:
            self.area = VGroup()
        self.add(self.ejes, self.area, self.curva)

    def en(self, f, db):
        fx = (float(f) - self.f[0]) / (self.f[-1] - self.f[0])
        fy = (min(max(float(db), self.piso), self.techo) - self.piso) / \
            (self.techo - self.piso)
        return self._origen() + np.array([(fx - 0.5) * self.ancho,
                                          (fy - 0.5) * self.alto, 0.0])

    def x_de(self, f):
        return float(self.en(f, self.piso)[0])

    def marca_f(self, f, color=C_CALCULO, ancho=1.8):
        return DashedLine(self.en(f, self.piso), self.en(f, self.techo),
                          color=color, stroke_width=ancho, dash_length=0.08)

    def banda(self, f0, f1, color=C_LO, opacidad=0.14, trazo=2.0):
        a, b = self.en(f0, self.piso), self.en(f1, self.techo)
        r = Rectangle(width=abs(b[0] - a[0]), height=abs(b[1] - a[1]),
                      stroke_color=color, stroke_width=trazo,
                      fill_color=color, fill_opacity=opacidad)
        return r.move_to((a + b) / 2)

    def con_db(self, db2, color=None):
        o = Espectro(self.f, db2, self.piso, self.techo, self.ancho,
                     self.alto, color or self.color, self._con_area,
                     self._grosor)
        o.shift(self._origen() - o._origen())
        return o

    def marcas(self, valores, textos=None, font_size=17, color=C_TENUE):
        g = VGroup()
        for k, v in enumerate(valores):
            p = self.en(v, self.piso)
            g.add(Line(p, p + DOWN * 0.1, color=C_EJE, stroke_width=1.8))
            t = _hud(textos[k] if textos else v, font_size, color)
            t.next_to(p, DOWN, buff=0.16)
            g.add(t)
        return g


class Cadena(VGroup):
    """La cadena de recepcion como bloques en fila.

    Cadena(("ANTENA", "LNA", "MEZCLADOR", "FILTRO", "ADC", "USB"),
           ancho_total=12.4, alto=0.8, lo_en="MEZCLADOR")
      .bloques  (VGroup de bloque(); .bloques[i][0] caja, [1] texto)
      .flechas  (VGroup de conectar(); len = len(bloques) - 1)
      .lo       (VGroup circulo LO + rotulo + flecha al mezclador) o vacio
      .indice(nombre)
      .teñir(i, color) -> lista de animaciones .animate
    """

    def __init__(self, eslabones, ancho_total=12.4, alto=0.8, sep=0.42,
                 color=C_TENUE, lo_en="MEZCLADOR", tamano=20, **kwargs):
        super().__init__(**kwargs)
        self.nombres = list(eslabones)
        n = len(self.nombres)
        ancho = (ancho_total - sep * (n - 1)) / n
        self.bloques = VGroup(*[bloque(e, ancho=ancho, alto=alto, color=color,
                                       tamano=tamano, opacidad_relleno=0.08)
                                for e in self.nombres])
        self.bloques.arrange(RIGHT, buff=sep)
        self.flechas = VGroup(*[conectar(self.bloques[i], self.bloques[i + 1],
                                         color=C_TENUE, grosor=2.2,
                                         margen=0.04)
                                for i in range(n - 1)])
        self.lo = VGroup()
        if lo_en in self.nombres:
            b = self.bloques[self.nombres.index(lo_en)]
            c = Circle(radius=0.26, color=C_LO, stroke_width=2.4)
            c.next_to(b, DOWN, buff=0.55)
            onda = VMobject(stroke_color=C_LO, stroke_width=2.2)
            xs = np.linspace(-0.16, 0.16, 30)
            onda.set_points_smoothly([c.get_center() + np.array(
                [x, 0.09 * math.sin(x / 0.16 * 2 * math.pi), 0]) for x in xs])
            et = _hud("LO", 17, C_LO)
            et.next_to(c, RIGHT, buff=0.14)
            fl = Line(c.get_top(), b.get_bottom(), color=C_LO,
                      stroke_width=2.2)
            self.lo = VGroup(c, onda, et, fl)
        self.add(self.bloques, self.flechas, self.lo)

    def indice(self, nombre):
        return self.nombres.index(nombre)


class Medidor(_Anclada):
    """Barra vertical de nivel en dBFS (de `minimo` a 0) con la franja de
    recorte en rojo arriba. .nivel(db) -> Rectangle de relleno (gemela
    estructural: siempre un Rectangle), .en(db) -> punto del borde."""

    def __init__(self, alto=3.0, ancho=0.42, minimo=-60.0, recorte=-1.0,
                 **kwargs):
        super().__init__(**kwargs)
        self.alto, self.ancho = float(alto), float(ancho)
        self.minimo, self.recorte = float(minimo), float(recorte)
        self._poner_ancla(ORIGIN)
        self.marco = Rectangle(width=self.ancho, height=self.alto,
                               stroke_color=C_TENUE, stroke_width=1.8)
        self.marco.move_to(self._origen())
        zona = Rectangle(width=self.ancho, height=self.en(0)[1] -
                         self.en(self.recorte)[1] + 1e-3, stroke_width=0,
                         fill_color=C_RUIDO, fill_opacity=0.55)
        zona.move_to((self.en(0) + self.en(self.recorte)) / 2)
        self.zona = zona
        self.add(self.marco, zona)

    def en(self, db):
        fy = (min(max(db, self.minimo), 0.0) - self.minimo) / (-self.minimo)
        return self._origen() + np.array([0.0, (fy - 0.5) * self.alto, 0.0])

    def nivel(self, db, color=C_SENAL):
        h = max(self.en(db)[1] - self.en(self.minimo)[1], 0.01)
        r = Rectangle(width=self.ancho * 0.72, height=h, stroke_width=0,
                      fill_color=color, fill_opacity=0.85)
        r.move_to(self.en(self.minimo) + UP * h / 2)
        return r


def _colormap(p):
    """0..1 -> negro, azul, ambar, blanco (el del waterfall del curso 8)."""
    p = np.clip(p, 0, 1)
    cs = np.array([[5, 7, 10], [20, 50, 120], [245, 158, 11],
                   [255, 250, 235]], float)
    xs = np.array([0.0, 0.45, 0.8, 1.0])
    out = np.empty(p.shape + (3,))
    for c in range(3):
        out[..., c] = np.interp(p, xs, cs[:, c])
    return out.astype(np.uint8)


def waterfall(filas_db, ancho=8.0, alto=3.2, piso=-70.0, techo=0.0):
    """ImageMobject de un waterfall (filas = tiempo hacia abajo). SIEMPRE
    en Group, nunca en VGroup."""
    d = (np.asarray(filas_db, float) - piso) / (techo - piso)
    img = ImageMobject(_colormap(d))
    img.stretch_to_fit_width(ancho)
    img.stretch_to_fit_height(alto)
    return img

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
    if len(x) < nfft:
        # senal mas corta que nfft: UN segmento con la ventana de su largo
        # y FFT rellenada con ceros hasta nfft (interpola el espectro, no
        # anade resolucion). Antes reventaba por el broadcast.
        w = ventana(ventana_nombre, len(x))
        acc = np.abs(np.fft.fft(x * w, nfft)) ** 2
        nseg = 1
    else:
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
    # array_split reparte TODAS las muestras (la version con reshape tiraba
    # la cola derecha cuando len no era multiplo de `puntos`: un 8.5 % del
    # espectro en un caso real del curso, y el dibujo salia asimetrico).
    trozos_f = np.array_split(f, puntos)
    trozos_d = np.array_split(db, puntos)
    fc = np.array([t.mean() for t in trozos_f])
    fc[0], fc[-1] = f[0], f[-1]          # conserva los extremos exactos
    return fc, np.array([t.max() for t in trozos_d])


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

# =====================================================================
# LOTE 2 · 3.1 Sintonizar en software
# =====================================================================
def nco(f, fs, n, fase0=0.0):
    """Oscilador numerico: acumulador de fase -> exp(-j fase). Devuelve el
    fasor que MULTIPLICA (mueve el espectro -f)."""
    fase = fase0 + 2 * np.pi * f / fs * np.arange(n)
    return np.exp(-1j * fase)


def nco_por_bloques(f, fs, n, bloque, continuo=True):
    """El mismo NCO generado por bloques. Si `continuo` es False, el
    acumulador se REINICIA en cada bloque (el error clasico): la fase salta
    y aparecen espurios cada fs/bloque."""
    out = np.empty(n, complex)
    fase = 0.0
    paso = 2 * np.pi * f / fs
    for k in range(0, n, bloque):
        m = min(bloque, n - k)
        if not continuo:
            fase = 0.0
        out[k:k + m] = np.exp(-1j * (fase + paso * np.arange(m)))
        fase = (fase + paso * m) % (2 * np.pi)
    return out


def espurio_nco_dbc(f=37.5e3, fs=240e3, bloque=1000):
    """El NCO reiniciado por bloques es PERIODICO de periodo `bloque`: su
    espectro son rayas exactas en multiplos de fs/bloque. La FFT de UN
    periodo da la potencia exacta de cada raya (sin malla): portadora = la
    mayor, espurio = la segunda. Devuelve (dBc, separacion_hz)."""
    y = np.conj(nco_por_bloques(f, fs, bloque, bloque, continuo=False))
    p = np.abs(np.fft.fft(y)) ** 2
    orden = np.argsort(p)[::-1]
    return float(db10(p[orden[1]] / p[orden[0]])), float(fs / bloque)


def emisoras_captura(centro=96.4e6, fs=RTL["fs"], semilla=38):
    """Offsets (Hz) y niveles de las emisoras que caben en la captura."""
    fe, ne = banda_fm(semilla)
    m = np.abs(fe - centro) < fs / 2 - 60e3
    return fe[m] - centro, ne[m]


# =====================================================================
# 3.2 Filtrar y diezmar
# =====================================================================
def kaiser_taps(aten_db, transicion_hz, fs):
    """Numero de coeficientes por la formula de Kaiser (impar)."""
    dw = 2 * np.pi * transicion_hz / fs
    n = int(math.ceil((aten_db - 7.95) / (2.285 * dw))) + 1
    return n + (1 - n % 2)


def kaiser_beta(aten_db):
    if aten_db > 50:
        return 0.1102 * (aten_db - 8.7)
    if aten_db >= 21:
        return 0.5842 * (aten_db - 21) ** 0.4 + 0.07886 * (aten_db - 21)
    return 0.0


def fir_paso_bajo(n_taps, corte_hz, fs, aten_db=60.0):
    """Sinc enventanado con Kaiser (implementacion propia)."""
    m = np.arange(n_taps) - (n_taps - 1) / 2
    fc = corte_hz / fs
    h = 2 * fc * np.sinc(2 * fc * m)
    h *= np.kaiser(n_taps, kaiser_beta(aten_db))
    return h / h.sum()


def respuesta_db(h, fs, n=16384):
    H = np.fft.fftshift(np.fft.fft(h, n))
    f = np.fft.fftshift(np.fft.fftfreq(n, 1 / fs))
    return f, db10(np.abs(H) ** 2)


def aten_minima(h, fs, desde_hz):
    """Peor atenuacion (nivel de LOBULO mas alto) a partir de `desde_hz`:
    no depende de la malla (lo que se mueve es la profundidad de nulos)."""
    f, d = respuesta_db(h, fs, 1 << 16)
    return float(-d[np.abs(f) >= desde_hz].max())


def diezmar(x, m, h=None):
    if h is not None:
        x = np.convolve(x, h, mode="same")
    return x[::m]


def fuga_vecina(con_filtro, off_vecina=500e3, m=10, fs=RTL["fs"],
                n=1 << 16, n_taps=None, semilla=3):
    """Canal en 0 Hz (tono de -6 dB... una emisora) y una VECINA a
    `off_vecina` del mismo nivel. Tras diezmar por m, la vecina cae
    plegada en off_vecina mod fs/m (dentro del canal). Devuelve el nivel
    (dBc) de la vecina plegada respecto al canal, por proyeccion."""
    fs2 = fs / m
    f_des = -40e3
    x = tono(f_des, fs, n) + tono(off_vecina, fs, n)
    h = None
    if con_filtro:
        n_taps = n_taps or kaiser_taps(60.0, 40e3, fs)
        h = fir_paso_bajo(n_taps, 100e3, fs)
    y = diezmar(x, m, h)
    f_pleg = ((off_vecina + fs2 / 2) % fs2) - fs2 / 2
    y = y[200:-200]
    return float(db10(potencia_tono(y, f_pleg, fs2) /
                      potencia_tono(y, f_des, fs2))), float(f_pleg)


def fuga_vecina_suelo():
    """Con filtro, el nivel de la vecina plegada baila con la longitud de
    la captura (-72 / -68 dBc): se rotula solo el TECHO del barrido,
    redondeado hacia arriba a decenas ("menos de -60 dBc")."""
    v = [fuga_vecina(True, n=n)[0] for n in (1 << 14, 1 << 15, 1 << 16,
                                             50000)]
    return int(10 * math.ceil(max(v) / 10)), min(v), max(v)


def coste_una_etapa(fs=RTL["fs"], m=10, paso=100e3, rechazo=140e3,
                    aten=60.0):
    """MAC por segundo de un FIR unico polifasico que diezma por m."""
    n = kaiser_taps(aten, rechazo - paso, fs)
    return n, n * fs / m


def coste_dos_etapas(fs=RTL["fs"], m1=5, m2=2, paso=100e3, rechazo=140e3,
                     aten=60.0):
    """Primera etapa ancha (su transicion llega hasta fs/m1 - rechazo,
    donde empiezan los alias que la segunda ya no puede quitar), segunda
    estrecha a fs/m1."""
    fs1 = fs / m1
    n1 = kaiser_taps(aten, (fs1 - rechazo) - paso, fs)
    n2 = kaiser_taps(aten, rechazo - paso, fs1)
    return n1, n2, n1 * fs1 + n2 * fs1 / m2


# =====================================================================
# 3.3 El reloj que miente
# =====================================================================
def ppm_a_hz(ppm, f):
    return float(ppm * 1e-6 * f)


def estimar_ppm(ppm_real=27.0, f_ref=144.39e6, fs=RTL["fs"], n=1 << 15,
                snr_db=20.0, semilla=8):
    """Una portadora de referencia de frecuencia CONOCIDA llega corrida por
    el error del cristal; su pico (interpolacion parabolica sobre FFT con
    ceros) da el error en Hz y en ppm."""
    f_off = 50e3                              # sintonia intencional (dato)
    err = ppm_real * 1e-6 * f_ref
    x = tono(f_off + err, fs, n) + ruido_complejo(n, 10 ** (-snr_db / 10),
                                                  semilla)
    f, d = espectro_db(x, fs, nfft=n, ventana_nombre="hann")
    fp, _ = pico(f, d)
    est = (fp - f_off) / f_ref * 1e6
    return float(est), float(fp - f_off)


def deriva_termica(minutos=10.0, n_filas=120, ppm_total=2.2, f=437e6):
    """Curva de deriva (Hz) de un cristal que se calienta: sube como
    1 - exp(-t/tau). Parametros elegidos (gris)."""
    t = np.linspace(0, minutos, n_filas)
    return t, ppm_total * 1e-6 * f * (1 - np.exp(-t / 3.0))


def waterfall_deriva(n_filas=120, columnas=256, fs=48e3, f0=-6e3,
                     semilla=12, **kw):
    """Waterfall (filas de dB) de un tono que deriva segun deriva_termica,
    visto en una ventana de fs. Devuelve (filas_db, t, deriva_hz,
    deriva_medida_hz) con la deriva medida fila a fila por el pico."""
    t, dh = deriva_termica(n_filas=n_filas, **kw)
    r = np.random.default_rng(semilla)
    filas = []
    med = []
    for k in range(n_filas):
        x = tono(f0 + dh[k], fs, columnas * 4) + ruido_complejo(
            columnas * 4, 0.05, int(r.integers(1 << 30)))
        f, d = espectro_db(x, fs, nfft=columnas, ref="abs")
        filas.append(d)
        med.append(pico(f, d)[0])
    filas = np.array(filas)
    filas -= filas.max()
    med = np.array(med) - f0
    return filas, t, dh, med


# =====================================================================
# 4.1 El discriminador
# =====================================================================
FS_MPX = 228e3          # 12 x 19 kHz = 192 muestras por bit RDS
DESV_FM = 75e3          # desviacion maxima de la FM comercial (dato)


def fm_modular(m, fs, desviacion=DESV_FM):
    """Banda base compleja: fase = 2*pi*desv*cumsum(m)/fs, |m| <= 1."""
    return np.exp(1j * 2 * np.pi * desviacion * np.cumsum(m) / fs)


def discriminador(x, fs):
    """Discriminador polar: frecuencia instantanea en Hz.
    angle(x[n] * conj(x[n-1])) * fs / (2 pi)."""
    d = np.angle(x[1:] * np.conj(x[:-1])) * fs / (2 * np.pi)
    return np.concatenate([[d[0]], d])


def carson(desviacion, fm):
    return 2.0 * (desviacion + fm)


def ancho_ocupado(x, fs, frac=0.98, nfft=8192):
    """Ancho que contiene `frac` de la potencia (medido)."""
    f, d = espectro_db(x, fs, nfft=nfft, ref="abs")
    p = 10 ** (d / 10)
    c = np.cumsum(p) / p.sum()
    lo = f[np.searchsorted(c, (1 - frac) / 2)]
    hi = f[np.searchsorted(c, 1 - (1 - frac) / 2)]
    return float(hi - lo)


def deenfasis(y, fs, tau=75e-6):
    """Filtro de deenfasis de un polo (tau = 75 us en America, dato)."""
    a = math.exp(-1.0 / (fs * tau))
    out = np.empty_like(y)
    acc = 0.0
    for k, v in enumerate(y):
        acc = (1 - a) * v + a * acc
        out[k] = acc
    return out


def mejora_deenfasis(fs=FS_MPX, n=1 << 16, cnr_db=15.0, semilla=5,
                     banda=15e3):
    """Ruido de audio (0-15 kHz) a la salida del discriminador, sin y con
    deenfasis, con portadora sin modular + ruido (CNR elegido). Devuelve
    la mejora en dB (medida)."""
    x = np.ones(n, complex) + ruido_complejo(n, 10 ** (-cnr_db / 10),
                                             semilla)
    d = discriminador(x, fs)
    e = deenfasis(d, fs)
    # la ganancia del deenfasis a 1 kHz se normaliza (se compara ruido
    # a igual nivel de audio)
    f, p1 = espectro_db(d, fs, nfft=4096, ref="abs")
    _, p2 = espectro_db(e, fs, nfft=4096, ref="abs")
    m = (np.abs(f) > 50) & (np.abs(f) <= banda)
    g1k = 1.0 / math.sqrt(1 + (2 * math.pi * 1e3 * 75e-6) ** 2)
    ruido1 = np.sum(10 ** (p1[m] / 10))
    ruido2 = np.sum(10 ** (p2[m] / 10)) / g1k ** 2
    return float(db10(ruido1 / ruido2))


# =====================================================================
# 4.2 El multiplex estereo
# =====================================================================
F_PILOTO = 19e3
F_RDS = 57e3


def mpx(n=1 << 15, fs=FS_MPX, f_l=1000.0, f_r=3000.0, rds=None,
        nivel_piloto=0.09, nivel_rds=0.04):
    """Senal MPX: (L+R)/2 + piloto 19k + (L-R)/2 * cos(38k) + RDS."""
    t = np.arange(n) / fs
    L = 0.45 * np.sin(2 * np.pi * f_l * t)
    R = 0.45 * np.sin(2 * np.pi * f_r * t)
    fase_p = 2 * np.pi * F_PILOTO * t
    y = (L + R) / 2 + nivel_piloto * np.sin(fase_p) + \
        (L - R) / 2 * np.sin(2 * fase_p - np.pi / 2 + np.pi / 2)
    y = (L + R) / 2 + nivel_piloto * np.cos(fase_p) + \
        (L - R) / 2 * np.cos(2 * fase_p)
    if rds is not None:
        y = y + nivel_rds * rds[:n] * np.cos(3 * fase_p)
    return y, L, R


def pll_piloto(y, fs=FS_MPX, kp=0.02, ki=4e-5):
    """PLL de segundo orden enganchado al piloto de 19 kHz (fase del NCO,
    que arranca con un error de frecuencia de 30 Hz a proposito).
    Devuelve (fase_nco, error_de_fase)."""
    n = len(y)
    fase = np.empty(n)
    err = np.empty(n)
    ph = 0.0
    w = 2 * np.pi * (F_PILOTO + 30.0) / fs
    integ = 0.0
    for k in range(n):
        fase[k] = ph
        e = -y[k] * math.sin(ph)
        err[k] = e
        integ += ki * e
        ph += w + kp * e + integ
    return fase, err


def separar_lr(y, fase_piloto, fs=FS_MPX, n_taps=255):
    """Matriz estereo con la subportadora REGENERADA (2 x fase del piloto
    enganchado): L = S + D, R = S - D, con S y D paso bajo a 15 kHz."""
    h = fir_paso_bajo(n_taps, 15e3, fs)
    s = np.convolve(y, h, mode="same")
    d = 2 * np.convolve(y * np.cos(2 * fase_piloto), h, mode="same")
    return s + d, s - d


def separacion_db(L_rx, R_rx, f_l=1000.0, f_r=3000.0, fs=FS_MPX, desde=8000):
    """Diafonia: cuanto del tono de R (3 kHz) aparece en el canal L
    respecto al tono propio de L (proyeccion, coherente)."""
    a = L_rx[desde:]
    return float(db10(potencia_tono(a, f_l, fs) / potencia_tono(a, f_r, fs)))


def precio_estereo(fs=FS_MPX, n=1 << 16, cnr_db=20.0, semilla=6):
    """Ruido tras el discriminador en la banda mono (0-15 k) contra la banda
    de la diferencia (23-53 k): la FM pone ruido que crece con f^2.
    Devuelve la diferencia en dB (medida)."""
    x = np.ones(n, complex) + ruido_complejo(n, 10 ** (-cnr_db / 10), semilla)
    d = discriminador(x, fs)
    f, p = espectro_db(d, fs, nfft=4096, ref="abs")
    pl = 10 ** (p / 10)
    mono = pl[(np.abs(f) > 50) & (np.abs(f) <= 15e3)].sum()
    dif = pl[(np.abs(f) >= 23e3) & (np.abs(f) <= 53e3)].sum()
    # la diferencia ocupa el doble de ancho: se compara por hercio no;
    # lo que llega al oido es la banda demodulada de 15 kHz: la banda
    # 23-53 k baja a 0-15 k por los dos lados (se suman).
    return float(db10(dif / mono))


# =====================================================================
# 4.3 RDS
# =====================================================================
RDS_BPS = 1187.5
MUESTRAS_BIT = int(FS_MPX / RDS_BPS)       # 192
_G_RDS = 0b10110111001                      # x^10+x^8+x^7+x^5+x^4+x^3+1
OFFSETS = {"A": 0b0011111100, "B": 0b0110011000, "C": 0b0101101000,
           "D": 0b0110110100}


def _crc10(data16):
    reg = data16 << 10
    for i in range(25, 9, -1):
        if reg & (1 << i):
            reg ^= _G_RDS << (i - 10)
    return reg & 0x3FF


def bloque_rds(data16, offset):
    return (data16 << 10) | (_crc10(data16) ^ OFFSETS[offset])


def sindrome(bloque26):
    """Sindrome de un bloque de 26 bits: igual al offset si no hay error."""
    reg = bloque26
    for i in range(25, 9, -1):
        if reg & (1 << i):
            reg ^= _G_RDS << (i - 10)
    return reg & 0x3FF


def que_offset(bloque26):
    s = sindrome(bloque26)
    for k, v in OFFSETS.items():
        if v == s:
            return k
    return None


def grupos_ps(ps="CODE FM ", pi=0xC0DE):
    """Cuatro grupos 0A con el nombre de la emisora (8 caracteres ASCII),
    dos caracteres por grupo. Devuelve la lista de bits (MSB primero)."""
    ps = (ps + " " * 8)[:8]
    bits = []
    for seg in range(4):
        b1 = pi
        b2 = (0b0000 << 12) | (0 << 11) | (0 << 10) | (0 << 5) | seg
        b3 = pi
        b4 = (ord(ps[2 * seg]) << 8) | ord(ps[2 * seg + 1])
        for data, off in ((b1, "A"), (b2, "B"), (b3, "C"), (b4, "D")):
            blk = bloque_rds(data, off)
            bits += [(blk >> (25 - i)) & 1 for i in range(26)]
    return np.array(bits, int)


def rds_banda_base(bits, fs=FS_MPX):
    """Codificacion diferencial + bifase (Manchester) + pulso: forma de
    onda de banda base (+-1) a fs, MUESTRAS_BIT muestras por bit."""
    dif = np.zeros(len(bits), int)
    prev = 0
    for k, b in enumerate(bits):
        prev ^= int(b)
        dif[k] = prev
    sim = 2 * dif - 1
    mitad = MUESTRAS_BIT // 2
    forma = np.concatenate([np.ones(mitad), -np.ones(mitad)])
    onda = np.concatenate([s * forma for s in sim])
    h = fir_paso_bajo(129, 2.4e3, fs, 40.0)
    return np.convolve(onda, h, mode="same")


def rds_recibir(mpx_rx, fase_piloto, n_bits, fs=FS_MPX):
    """Baja la subportadora con 3 x fase del piloto, filtra, busca la fase
    de reloj que maximiza la energia de la decision bifase y decide cada
    bit; decodificacion diferencial. Devuelve los bits."""
    bb = mpx_rx * np.cos(3 * fase_piloto)
    h = fir_paso_bajo(257, 2.4e3, fs, 50.0)
    bb = np.convolve(bb, h, mode="same")
    mitad = MUESTRAS_BIT // 2
    mejor = None
    for desfase in range(0, MUESTRAS_BIT, 4):
        v = []
        for k in range(n_bits):
            a = desfase + k * MUESTRAS_BIT
            if a + MUESTRAS_BIT > len(bb):
                break
            v.append(bb[a:a + mitad].sum() - bb[a + mitad:a + MUESTRAS_BIT].sum())
        v = np.array(v)
        e = np.abs(v).mean()
        if mejor is None or e > mejor[0]:
            mejor = (e, desfase, v)
    _, desfase, v = mejor
    dif = (v > 0).astype(int)
    bits = np.empty_like(dif)
    prev = 0
    for k, d in enumerate(dif):
        bits[k] = d ^ prev
        prev = d
    return bits, desfase


def buscar_bloques(bits):
    """Desliza una ventana de 26 bits y devuelve las posiciones cuyo
    sindrome coincide con un offset (sincronia de bloque)."""
    hits = []
    for i in range(len(bits) - 25):
        val = 0
        for b in bits[i:i + 26]:
            val = (val << 1) | int(b)
        o = que_offset(val)
        if o:
            hits.append((i, o, val >> 10))
    return hits


def ps_de(hits):
    """Reconstruye el nombre de la emisora con los bloques B (segmento) y
    D (dos caracteres) de grupos 0A consecutivos."""
    ps = ["?"] * 8
    for j, (i, o, d) in enumerate(hits):
        if o == "B":
            seg = d & 0b11
            for (i2, o2, d2) in hits[j + 1:j + 4]:
                if o2 == "D" and i2 == i + 52:
                    ps[2 * seg] = chr(d2 >> 8)
                    ps[2 * seg + 1] = chr(d2 & 0xFF)
    return "".join(ps)


def cadena_rds(ps="CODE FM ", cnr_db=25.0, semilla=2):
    """La cadena entera: grupos -> banda base -> MPX -> FM -> ruido ->
    discriminador -> PLL del piloto -> RDS -> bloques -> nombre."""
    bits = np.tile(grupos_ps(ps), 2)
    rds = rds_banda_base(bits)
    n = len(rds)
    y, _, _ = mpx(n=n, rds=rds)
    x = fm_modular(y / np.max(np.abs(y)), FS_MPX)
    x = x + ruido_complejo(n, 10 ** (-cnr_db / 10), semilla)
    d = discriminador(x, FS_MPX) / DESV_FM
    fase, _ = pll_piloto(d)
    rx, desf = rds_recibir(d, fase, len(bits))
    hits = buscar_bloques(rx)
    return {"bits_tx": bits, "bits_rx": rx, "hits": hits,
            "ps": ps_de(hits), "errores": int(np.sum(rx != bits[:len(rx)])),
            "desfase": desf}

# =====================================================================
# LOTE 3 · 5.1 La constelacion que gira
# =====================================================================
QPSK = np.exp(1j * (np.pi / 4 + np.pi / 2 * np.arange(4)))


def simbolos_qpsk(n, semilla=1):
    r = np.random.default_rng(semilla)
    return QPSK[r.integers(0, 4, n)]


def simbolos_bpsk(n, semilla=1):
    r = np.random.default_rng(semilla)
    return (2 * r.integers(0, 2, n) - 1).astype(complex)


def con_desfase(sim, df_rs, fase0=0.0):
    """Aplica un desfase de frecuencia df_rs (ciclos por simbolo)."""
    k = np.arange(len(sim))
    return sim * np.exp(1j * (2 * np.pi * df_rs * k + fase0))


def estimar_desfase_x4(rx, nfft=None):
    """Estimador a la CUARTA potencia: rx^4 borra la QPSK y deja una raya
    en 4*df. Devuelve df estimado (ciclos por simbolo) con interpolacion
    parabolica."""
    z = rx ** 4
    nfft = int(nfft or 4 * len(z))
    Z = np.abs(np.fft.fft(z, nfft)) ** 2
    k = int(np.argmax(Z))
    a, b, c = Z[(k - 1) % nfft], Z[k], Z[(k + 1) % nfft]
    den = a - 2 * b + c
    d = 0.5 * (a - c) / den if den != 0 else 0.0
    f4 = ((k + d) / nfft + 0.5) % 1.0 - 0.5
    return f4 / 4.0


def escenario_giro(n=2048, df_rs=0.0037, snr_db=15.0, semilla=4):
    sim = simbolos_qpsk(n, semilla)
    rx = con_desfase(sim, df_rs, 0.4)
    rx = rx + ruido_complejo(n, 10 ** (-snr_db / 10), semilla + 1)
    return sim, rx


# =====================================================================
# 5.2 El lazo de Costas
# =====================================================================
def ganancias_lazo(bn_rs, zeta=0.707):
    """Ganancias (kp, ki) de un lazo de 2.o orden para un ancho de banda
    de ruido normalizado bn_rs (por simbolo), detector de ganancia 1."""
    theta = bn_rs / (zeta + 1 / (4 * zeta))
    d = 1 + 2 * zeta * theta + theta ** 2
    return 4 * zeta * theta / d, 4 * theta ** 2 / d


def costas_bpsk(rx, bn_rs=0.02, zeta=0.707):
    """Lazo de Costas para BPSK a una muestra por simbolo: error = I*Q
    (normalizado). Devuelve (salida corregida, fase del NCO, error)."""
    kp, ki = ganancias_lazo(bn_rs, zeta)
    n = len(rx)
    out = np.empty(n, complex)
    fase = np.empty(n)
    err = np.empty(n)
    ph = 0.0
    integ = 0.0
    for k in range(n):
        y = rx[k] * np.exp(-1j * ph)
        out[k] = y
        fase[k] = ph
        e = np.real(y) * np.imag(y) / (np.abs(y) ** 2 + 1e-12)
        err[k] = e
        integ += ki * e
        ph += kp * e + integ
    return out, fase, err


def tiempo_enganche(fase_nco, fase_real, umbral=0.15, sostener=50):
    """Primer simbolo desde el que el error de fase (modulo pi, por la
    ambiguedad de la BPSK) queda por debajo de `umbral` durante
    `sostener` simbolos seguidos. None si no engancha."""
    e = np.angle(np.exp(1j * 2 * (fase_nco - fase_real))) / 2
    e = np.convolve(np.abs(e), np.ones(20) / 20, mode="same")
    bien = e < umbral
    for k in range(len(bien) - sostener):
        if bien[k:k + sostener].all():
            return k
    return None


def jitter_fase(fase_nco, fase_real, desde):
    e = np.angle(np.exp(1j * 2 * (fase_nco - fase_real))) / 2
    return float(np.std(e[desde:]))


def escenario_costas(n=1500, df_rs=0.002, fase0=1.1, snr_db=10.0,
                     semilla=7):
    sim = simbolos_bpsk(n, semilla)
    k = np.arange(n)
    fase_real = 2 * np.pi * df_rs * k + fase0
    rx = sim * np.exp(1j * fase_real) + ruido_complejo(
        n, 10 ** (-snr_db / 10), semilla + 1)
    return sim, rx, fase_real


def ambiguedad_180(sim, out):
    """True si el lazo engancho invertido (los bits salen negados)."""
    a = np.sign(np.real(out[-300:]))
    return bool(np.mean(a == np.real(sim[-300:])) < 0.5)


def diferencial(bits):
    out = np.zeros(len(bits), int)
    prev = 0
    for k, b in enumerate(bits):
        prev ^= int(b)
        out[k] = prev
    return out


def dediferencial(bits):
    b = np.asarray(bits, int)
    return np.concatenate([[b[0]], b[1:] ^ b[:-1]])


# =====================================================================
# 5.3 El reloj de simbolo
# =====================================================================
def rrc(beta=0.35, span=8, sps=8):
    """Raiz de coseno alzado (energia unidad)."""
    t = np.arange(-span * sps / 2, span * sps / 2 + 1) / sps
    h = np.empty_like(t)
    for i, ti in enumerate(t):
        if abs(ti) < 1e-12:
            h[i] = 1 - beta + 4 * beta / np.pi
        elif abs(abs(ti) - 1 / (4 * beta)) < 1e-9:
            h[i] = beta / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * beta))
                                        + (1 - 2 / np.pi) * np.cos(np.pi / (4 * beta)))
        else:
            h[i] = (np.sin(np.pi * ti * (1 - beta)) + 4 * beta * ti *
                    np.cos(np.pi * ti * (1 + beta))) / (
                np.pi * ti * (1 - (4 * beta * ti) ** 2))
    return h / np.sqrt(np.sum(h ** 2))


def senal_con_pulsos(sim, sps=8, beta=0.35, span=8):
    up = np.zeros(len(sim) * sps, complex)
    up[::sps] = sim
    h = rrc(beta, span, sps)
    tx = np.convolve(up, h)
    rx = np.convolve(tx, h)
    retardo = len(h) - 1           # dos filtros de span*sps/2 cada uno
    return rx, retardo


def muestrear_en(rx, retardo, sps, tau, n):
    """Muestras a (retardo + k*sps + tau*sps), interpolacion lineal."""
    pos = retardo + np.arange(n) * sps + tau * sps
    i0 = np.floor(pos).astype(int)
    fr = pos - i0
    ok_ = (i0 + 1) < len(rx)
    i0, fr = i0[ok_], fr[ok_]
    return (1 - fr) * rx[i0] + fr * rx[i0 + 1]


def ber_vs_desfase(taus, n=20000, snr_db=7.0, sps=8, semilla=3):
    """BER MEDIDA de BPSK al muestrear a destiempo (fraccion de simbolo)."""
    sim = simbolos_bpsk(n, semilla)
    rx, ret = senal_con_pulsos(sim, sps)
    ruido = ruido_complejo(len(rx), 10 ** (-snr_db / 10) , semilla + 5)
    # el ruido se filtra con el mismo RRC del receptor (potencia por simbolo)
    h = rrc(0.35, 8, sps)
    rx = rx + np.convolve(ruido, h, mode="same") * np.sqrt(1.0)
    out = []
    for tau in taus:
        y = muestrear_en(rx, ret, sps, tau, n - 10)
        out.append(float(np.mean(np.sign(np.real(y)) !=
                                 np.real(sim[:len(y)]))))
    return np.array(out)


def gardner_curva_s(taus, n=4000, sps=8, semilla=2):
    """Curva S del detector de Gardner: error medio frente al desfase de
    muestreo (sin ruido). e = Re{(y[k] - y[k-1]) * conj(y[k-1/2])}."""
    sim = simbolos_bpsk(n, semilla)
    rx, ret = senal_con_pulsos(sim, sps)
    out = []
    for tau in taus:
        y = muestrear_en(rx, ret, sps, tau, n - 10)
        ym = muestrear_en(rx, ret, sps, tau - 0.5, n - 10)
        m = min(len(y), len(ym))
        e = np.real((y[1:m] - y[:m - 1]) * np.conj(ym[1:m]))
        out.append(float(np.mean(e)))
    return np.array(out)


def lazo_reloj(n=1500, sps=8, tau0=0.37, snr_db=15.0, bn=0.01,
               semilla=9):
    """Lazo de reloj con detector de Gardner e interpolador lineal. El
    reloj del receptor arranca desfasado `tau0` simbolos; la correccion
    c empieza en 0 y el lazo la lleva a -tau0. Devuelve (desfase efectivo
    tau0 + c por simbolo, muestras tomadas, simbolos)."""
    sim = simbolos_bpsk(n, semilla)
    rx, ret = senal_con_pulsos(sim, sps)
    rx = rx + ruido_complejo(len(rx), 10 ** (-snr_db / 10) / sps,
                             semilla + 3)
    kp, ki = ganancias_lazo(bn, 1.0)
    c = 0.0
    integ = 0.0
    m = n - 20
    taus = np.empty(m)
    ys = np.empty(m, complex)
    prev = 0.0

    def en(k, t_):
        p = ret + k * sps + t_ * sps
        i0 = int(np.floor(p))
        fr = p - i0
        return (1 - fr) * rx[i0] + fr * rx[i0 + 1]
    for k in range(1, m):
        t_ = tau0 + c
        y = en(k, t_)
        ym = en(k, t_ - 0.5)
        e = np.real((y - prev) * np.conj(ym))
        prev = y
        integ += ki * e
        c -= kp * e + integ
        taus[k] = tau0 + c
        ys[k] = y
    taus[0], ys[0] = tau0, en(0, tau0)
    return taus, ys, sim[:m]


def evm_pct(y, sim):
    """EVM (%) respecto a la constelacion ideal, con la escala ajustada."""
    a = np.vdot(sim, y) / np.vdot(sim, sim)
    return float(100 * np.sqrt(np.mean(np.abs(y / a - sim) ** 2) /
                               np.mean(np.abs(sim) ** 2)))


# =====================================================================
# 6.1 ADS-B
# =====================================================================
_CRC24 = 0xFFF409
_ADSB_CHARS = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ##### ###############0123456789######"


def crc24(bits88):
    """Resto de 24 bits del polinomio de Modo S sobre los 88 bits."""
    reg = 0
    for b in bits88:
        reg = ((reg << 1) | int(b))
    reg <<= 24
    for i in range(111, 23, -1):
        if reg & (1 << i):
            reg ^= (_CRC24 | (1 << 24)) << (i - 24)
    return reg & 0xFFFFFF


def _a_bits(valor, n):
    return [(valor >> (n - 1 - i)) & 1 for i in range(n)]


def adsb_identificacion(icao=0x0D0C38, indicativo="CODE101 "):
    """Mensaje DF17, tipo 4 (identificacion): 112 bits con su CRC."""
    ind = (indicativo + " " * 8)[:8]
    bits = _a_bits(17, 5) + _a_bits(5, 3) + _a_bits(icao, 24)
    me = _a_bits(4, 5) + _a_bits(0, 3)
    for ch in ind:
        me += _a_bits(_ADSB_CHARS.index(ch), 6)
    bits += me
    return np.array(bits + _a_bits(crc24(bits), 24), int)


def adsb_pulsos(bits, fs=2e6):
    """Envolvente PPM a 2 MS/s: preambulo (pulsos en 0, 1, 3.5 y 4.5 us)
    + un bit por microsegundo (1 = alto-bajo, 0 = bajo-alto)."""
    spu = int(fs / 1e6)
    pre = np.zeros(8 * spu)
    for t in (0.0, 1.0, 3.5, 4.5):
        a = int(t * spu)
        pre[a:a + spu // 2] = 1
    dat = []
    for b in bits:
        dat += [1, 0] if b else [0, 1]
    return np.concatenate([pre, np.repeat(dat, spu // 2)])


def adsb_captura(bits, snr_db=12.0, offset=137, n_total=600, semilla=5,
                 fs=2e6):
    """Magnitud |IQ| de una captura con el mensaje en `offset` muestras."""
    env = adsb_pulsos(bits, fs)
    x = np.zeros(n_total, complex)
    x[offset:offset + len(env)] = env * np.exp(1j * 0.7)
    x = x + ruido_complejo(n_total, 10 ** (-snr_db / 10), semilla)
    return np.abs(x)


def adsb_buscar_preambulo(mag, fs=2e6):
    """Correlacion con el patron del preambulo; devuelve (offset, curva)."""
    patron = adsb_pulsos([], fs)
    patron = patron - patron.mean()
    c = np.correlate(mag - mag.mean(), patron, mode="valid")
    return int(np.argmax(c)), c


def adsb_buscar(mag, fs=2e6, candidatos=8):
    """Como un decodificador real: los `candidatos` picos mas altos de la
    correlacion se prueban en orden y el CRC decide. Devuelve (offset,
    decodificado, rechazados) o (None, None, rechazados)."""
    _, c = adsb_buscar_preambulo(mag, fs)
    orden = np.argsort(c)[::-1]
    vistos, rechazados = [], []
    for k in orden:
        if any(abs(int(k) - v) < 2 for v in vistos):
            continue
        vistos.append(int(k))
        if int(k) + 8 * int(fs / 1e6) + 224 > len(mag):
            continue
        d = adsb_decodificar(mag, int(k), fs)
        if d["crc_ok"]:
            return int(k), d, rechazados
        rechazados.append(int(k))
        if len(vistos) >= candidatos:
            break
    return None, None, rechazados


def adsb_decodificar(mag, offset, fs=2e6):
    spu = int(fs / 1e6)
    a = offset + 8 * spu
    bits = []
    for k in range(112):
        p = a + k * spu
        bits.append(1 if mag[p] > mag[p + 1] else 0)
    bits = np.array(bits, int)
    resto = crc24(bits[:88])
    recibido = int("".join(map(str, bits[88:])), 2)
    icao = int("".join(map(str, bits[8:32])), 2)
    ind = ""
    for i in range(8):
        v = int("".join(map(str, bits[40 + 6 * i:46 + 6 * i])), 2)
        ind += _ADSB_CHARS[v]
    return {"bits": bits, "df": int("".join(map(str, bits[:5])), 2),
            "icao": f"{icao:06X}", "indicativo": ind,
            "crc_ok": resto == recibido, "sindrome": resto ^ recibido}


# =====================================================================
# 6.2 AIS
# =====================================================================
def crc16_x25(bits):
    """CRC-16/X.25 (HDLC) sobre bits en orden de transmision (LSB primero
    por byte, como los manda HDLC)."""
    crc = 0xFFFF
    for b in bits:
        x = (crc ^ int(b)) & 1
        crc >>= 1
        if x:
            crc ^= 0x8408
    return crc ^ 0xFFFF


def ais_mensaje1(mmsi=345070001, lat=19.4326, lon=-99.1332, sog=12.3,
                 cog=87.5):
    """Mensaje AIS tipo 1 (168 bits) con posicion. Barco FICTICIO."""
    b = []
    b += _a_bits(1, 6) + _a_bits(0, 2) + _a_bits(mmsi, 30) + _a_bits(0, 4)
    b += _a_bits(128, 8) + _a_bits(int(round(sog * 10)), 10) + [0]
    b += _a_bits(int(round(lon * 600000)) & ((1 << 28) - 1), 28)
    b += _a_bits(int(round(lat * 600000)) & ((1 << 27) - 1), 27)
    b += _a_bits(int(round(cog * 10)), 12) + _a_bits(511, 9)
    b += _a_bits(30, 6) + _a_bits(0, 2) + _a_bits(0, 3) + [0]
    b += _a_bits(0, 19)
    return np.array(b, int)


def _por_bytes_lsb(bits):
    """Reordena a orden de transmision HDLC: cada byte LSB primero."""
    out = []
    for i in range(0, len(bits), 8):
        out += list(bits[i:i + 8][::-1])
    return out


def relleno(bits):
    """Bit stuffing: tras cinco unos seguidos se inserta un cero."""
    out, cuenta, insertados = [], 0, 0
    for b in bits:
        out.append(int(b))
        cuenta = cuenta + 1 if b else 0
        if cuenta == 5:
            out.append(0)
            cuenta = 0
            insertados += 1
    return out, insertados


def quitar_relleno(bits):
    out, cuenta = [], 0
    saltar = False
    for b in bits:
        if saltar:
            saltar = False
            cuenta = 0
            continue
        out.append(int(b))
        cuenta = cuenta + 1 if b else 0
        if cuenta == 5:
            saltar = True
    return out


BANDERA = [0, 1, 1, 1, 1, 1, 1, 0]


def ais_trama(msg_bits):
    """Entrenamiento + bandera + (datos + CRC) con relleno + bandera."""
    tx = _por_bytes_lsb(msg_bits)
    crc = crc16_x25(tx)
    tx = tx + [(crc >> i) & 1 for i in range(16)]
    rell, ins = relleno(tx)
    ent = [0, 1] * 12
    return np.array(ent + BANDERA + rell + BANDERA + [0] * 8, int), ins


def nrzi(bits):
    """NRZI de HDLC: un 0 cambia el nivel, un 1 lo mantiene."""
    out, nivel = [], 1
    for b in bits:
        if b == 0:
            nivel ^= 1
        out.append(nivel)
    return np.array(out, int)


def de_nrzi(niveles):
    n = np.asarray(niveles, int)
    return np.concatenate([[1], (n[1:] == n[:-1]).astype(int)])


def gmsk(niveles, sps=8, bt=0.4, h=0.5):
    """GMSK: NRZ filtrado gaussiano + integracion de fase (indice h)."""
    nrz = np.repeat(2 * np.asarray(niveles) - 1, sps).astype(float)
    t = np.arange(-2 * sps, 2 * sps + 1) / sps
    sigma = np.sqrt(np.log(2)) / (2 * np.pi * bt)
    g = np.exp(-t ** 2 / (2 * sigma ** 2))
    g /= g.sum()
    f = np.convolve(nrz, g, mode="same")
    return np.exp(1j * np.pi * h * np.cumsum(f) / sps)


def ais_recibir(x, sps=8):
    """Discriminador -> decision al centro de cada bit -> NRZI -> busca
    banderas -> quita relleno -> CRC -> campos."""
    # giro de fase a lo largo de CADA bit entero (discriminador integrado
    # sobre el bit): mucho mas robusto que una sola muestra
    h = fir_paso_bajo(8 * sps + 1, 1.5 / sps, 2.0)   # canal: 0.75 x tasa de bit
    x = np.convolve(x, h, mode="same")
    nb = (len(x) - 1) // sps
    giro = np.angle(x[sps:nb * sps + 1:sps] * np.conj(x[0:nb * sps:sps]))
    niveles = (giro > 0).astype(int)
    bits = de_nrzi(niveles)
    s = "".join(map(str, bits))
    i = s.find("01111110")
    j = s.find("01111110", i + 8)
    if i < 0 or j < 0:
        return None
    cuerpo = quitar_relleno(bits[i + 8:j])
    if len(cuerpo) < 184:
        return None
    datos, crc_rx = cuerpo[:-16], cuerpo[-16:]
    crc_ok = crc16_x25(datos) == sum(b << k for k, b in enumerate(crc_rx))
    msg = []
    for k in range(0, len(datos), 8):
        msg += list(datos[k:k + 8][::-1])

    def campo(a, n, signo=False):
        v = int("".join(map(str, msg[a:a + n])), 2)
        if signo and v >= 1 << (n - 1):
            v -= 1 << n
        return v
    return {"crc_ok": crc_ok, "tipo": campo(0, 6), "mmsi": campo(8, 30),
            "sog": campo(50, 10) / 10, "lon": campo(61, 28, True) / 600000,
            "lat": campo(89, 27, True) / 600000, "cog": campo(116, 12) / 10,
            "bits": len(datos)}


def cadena_ais(snr_db=12.0, semilla=3, sps=8):
    msg = ais_mensaje1()
    trama, ins = ais_trama(msg)
    x = gmsk(nrzi(trama), sps)
    x = x + ruido_complejo(len(x), 10 ** (-snr_db / 10), semilla)
    r = ais_recibir(x, sps)
    return r, ins, trama


# =====================================================================
# 6.3 LoRa
# =====================================================================
def chirp_lora(sf, simbolo=0, arriba=True):
    """Un simbolo LoRa muestreado a 1 muestra por chip (fs = BW): chirp
    que empieza en la frecuencia `simbolo` y da la vuelta en BW."""
    n = 2 ** sf
    k = np.arange(n)
    fase = 2 * np.pi * (k * k / (2 * n) + (simbolo / n - 0.5) * k)
    c = np.exp(1j * fase)
    return c if arriba else np.conj(c)


def lora_demodular(rx, sf):
    """Multiplica por el chirp base conjugado y toma la FFT: el pico es el
    simbolo."""
    n = 2 ** sf
    base = chirp_lora(sf, 0)
    return int(np.argmax(np.abs(np.fft.fft(rx[:n] * np.conj(base)))))


def ser_lora(sf, snr_db, n_sim=300, semilla=1):
    """Tasa de error de simbolo MEDIDA a una SNR (por muestra, en BW)."""
    r = np.random.default_rng(semilla)
    err = 0
    for i in range(n_sim):
        s = int(r.integers(0, 2 ** sf))
        rx = chirp_lora(sf, s) + ruido_complejo(2 ** sf, 10 ** (-snr_db / 10),
                                                int(r.integers(1 << 30)))
        err += lora_demodular(rx, sf) != s
    return err / n_sim


def umbral_lora(sf, objetivo=0.01, snrs=None, **kw):
    """SNR mas baja (paso 0.5 dB) con SER <= objetivo."""
    snrs = np.arange(-25.0, 0.1, 0.5) if snrs is None else snrs
    for s in snrs:
        if ser_lora(sf, s, **kw) <= objetivo:
            return float(s)
    return None


def tiempo_simbolo_ms(sf, bw=125e3):
    return 2 ** sf / bw * 1e3

# =====================================================================
# LOTE 4 · 7.1 El Doppler de un pase
# =====================================================================
from comunicaciones import doppler_de, fspl_db, pase_leo  # noqa: E402,F401


def doppler_pase(f_hz=437e6, h_km=550.0, elev_max=60.0, n=601):
    """Curva de Doppler (Hz) de un pase LEO (usa pase_leo del curso 24).
    Devuelve (t_s, doppler_hz, tasa_hz_s)."""
    p = pase_leo(h_km, elev_max, n)
    d = doppler_de(p, f_hz / 1e6) * 1e3
    tasa = np.gradient(d, p["t_s"])
    return p["t_s"], d, tasa


def residuo_seguimiento(error_tiempo_s=2.0, **kw):
    """El NCO sigue la PREDICCION del Doppler; si la prediccion va
    `error_tiempo_s` adelantada (reloj o TLE viejos), el residuo es
    d(t) - d(t + e). Devuelve (t, residuo_hz)."""
    t, d, _ = doppler_pase(**kw)
    pred = np.interp(t + error_tiempo_s, t, d)
    return t, d - pred


# =====================================================================
# 7.2 Meteor: del QPSK a la imagen
# =====================================================================
ASM = 0x1ACFFC1D
_G1, _G2 = 0o171, 0o133          # k = 7, tasa 1/2 (el de CCSDS y Meteor)


def _paridad(v):
    return bin(v).count("1") & 1


def conv_k7(bits):
    """Codificador convolucional k=7 tasa 1/2 (171, 133 octal)."""
    s = 0
    out = np.empty(2 * len(bits), int)
    for i, b in enumerate(bits):
        s = ((s << 1) | int(b)) & 0x7F
        out[2 * i] = _paridad(s & _G1)
        out[2 * i + 1] = _paridad(s & _G2)
    return out


def viterbi_k7(suaves):
    """Viterbi de decision SUAVE para conv_k7 (64 estados, vectorizado).
    `suaves`: valores reales por bit codificado (+1 ~ bit 0, -1 ~ bit 1)."""
    r = np.asarray(suaves, float).reshape(-1, 2)
    T = len(r)
    ns = 64
    est = np.arange(ns)
    # para cada estado nuevo s2 = ((s << 1) | b) & 63, predecesores s>>1 y
    # (s>>1)|32 ; el bit de entrada es s2 & 1
    pre0 = est >> 1
    pre1 = (est >> 1) | 32
    b = est & 1
    reg0 = ((pre0 << 1) | b) & 0x7F
    reg1 = ((pre1 << 1) | b) & 0x7F
    def sal(reg):
        o1 = np.array([_paridad(v & _G1) for v in reg])
        o2 = np.array([_paridad(v & _G2) for v in reg])
        return 1 - 2 * o1, 1 - 2 * o2
    a1, a2 = sal(reg0)
    c1, c2 = sal(reg1)
    met = np.full(ns, -1e18)
    met[0] = 0.0
    dec = np.empty((T, ns), bool)
    for t in range(T):
        m0 = met[pre0] + a1 * r[t, 0] + a2 * r[t, 1]
        m1 = met[pre1] + c1 * r[t, 0] + c2 * r[t, 1]
        dec[t] = m1 > m0
        met = np.where(dec[t], m1, m0)
    s = int(np.argmax(met))
    bits = np.empty(T, int)
    for t in range(T - 1, -1, -1):
        bits[t] = s & 1
        s = (s >> 1) | (32 if dec[t, s] else 0)
    return bits


def imagen_tierra(ancho=48, alto=32, semilla=21):
    """Imagen SINTETICA de 8 bits: costa, mar y nubes (ruido suavizado).
    No es una imagen real de Meteor: se declara en pantalla."""
    r = np.random.default_rng(semilla)
    y, x = np.mgrid[0:alto, 0:ancho] / np.array([alto, ancho])[:, None, None]
    tierra = (x + 0.25 * np.sin(6 * y) > 0.55).astype(float)
    base = 60 + 70 * tierra
    ruido = r.standard_normal((alto, ancho))
    for _ in range(4):
        ruido = (ruido + np.roll(ruido, 1, 0) + np.roll(ruido, 1, 1)
                 + np.roll(ruido, -1, 0) + np.roll(ruido, -1, 1)) / 5
    nubes = np.clip((ruido - 0.1) * 900, 0, 125)
    return np.clip(base + nubes, 0, 255).astype(np.uint8)


def _bits_de_imagen(img):
    return np.unpackbits(img.reshape(-1)).astype(int)


def _imagen_de_bits(bits, forma):
    return np.packbits(np.asarray(bits[:forma[0] * forma[1] * 8],
                                  np.uint8)).reshape(forma)


def qpsk_de_bits(bits):
    b = np.asarray(bits).reshape(-1, 2)
    return ((1 - 2 * b[:, 0]) + 1j * (1 - 2 * b[:, 1])) / np.sqrt(2)


def cadena_meteor(esn0_db=4.0, rotacion=1, semilla=4, img=None):
    """Imagen -> bits -> k=7 -> [ASM codificado + datos] -> QPSK -> canal
    (ruido + ambiguedad de fase de k*90 grados) -> busca la rotacion con
    la correlacion del ASM -> Viterbi suave -> imagen.
    Devuelve dict con BER cruda (decision dura), BER tras Viterbi, la
    imagen recibida y las correlaciones del ASM en las 4 rotaciones."""
    img = imagen_tierra() if img is None else img
    datos = _bits_de_imagen(img)
    asm_bits = np.array(_a_bits(ASM, 32), int)
    todo = np.concatenate([asm_bits, datos, np.zeros(6, int)])
    cod = conv_k7(todo)
    sim = qpsk_de_bits(cod)
    n = len(sim)
    rx = sim * np.exp(1j * np.pi / 2 * rotacion) + ruido_complejo(
        n, 10 ** (-esn0_db / 10), semilla)
    asm_cod = qpsk_de_bits(cod[:64])
    corr = []
    for k in range(4):
        z = rx[:32] * np.exp(-1j * np.pi / 2 * k)
        corr.append(float(np.real(np.vdot(asm_cod, z)) / 32))
    k = int(np.argmax(corr))
    z = rx * np.exp(-1j * np.pi / 2 * k)
    suaves = np.empty(2 * n)
    suaves[0::2], suaves[1::2] = z.real, z.imag
    duros = (suaves < 0).astype(int)
    ber_cruda = float(np.mean(duros != cod))
    dec = viterbi_k7(suaves)
    rec = dec[32:32 + len(datos)]
    ber_dec = float(np.mean(rec != datos))
    return {"img": img, "img_rx": _imagen_de_bits(rec, img.shape),
            "ber_cruda": ber_cruda, "ber_viterbi": ber_dec,
            "errores_viterbi": int(np.sum(rec != datos)),
            "corr_asm": corr, "rotacion_hallada": k,
            "img_cruda": _imagen_de_bits(np.where(
                np.random.default_rng(semilla + 1).random(len(datos))
                < ber_cruda, 1 - datos, datos), img.shape)}


# =====================================================================
# 7.3 GPS bajo el ruido
# =====================================================================
_G2_FASES = {1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9), 5: (1, 9),
             6: (2, 10), 7: (1, 8), 8: (2, 9), 9: (3, 10), 10: (2, 3)}


def codigo_ca(prn):
    """Codigo C/A de 1023 chips (G1 xor G2 con selector de fase)."""
    g1 = [1] * 10
    g2 = [1] * 10
    a, b = _G2_FASES[prn]
    out = np.empty(1023, int)
    for i in range(1023):
        out[i] = g1[9] ^ (g2[a - 1] ^ g2[b - 1])
        n1 = g1[2] ^ g1[9]
        n2 = g2[1] ^ g2[2] ^ g2[5] ^ g2[7] ^ g2[8] ^ g2[9]
        g1 = [n1] + g1[:9]
        g2 = [n2] + g2[:9]
    return out


def gps_captura(prn=7, fase_chip=600, doppler=2500.0, snr_db=-20.0,
                fs=2.046e6, semilla=6, ms=10):
    """1 ms (o `ms`) de senal C/A muestreada a 2 muestras por chip, con
    Doppler y fase de codigo, bajo ruido (SNR por muestra)."""
    c = 1 - 2 * codigo_ca(prn)
    spc = int(fs / 1.023e6)
    x = np.tile(np.repeat(np.roll(c, -fase_chip), spc), ms)
    n = len(x)
    t = np.arange(n) / fs
    x = x * np.exp(1j * 2 * np.pi * doppler * t)
    return x + ruido_complejo(n, 10 ** (-snr_db / 10), semilla)


def gps_adquirir(x, prn=7, fs=2.046e6, dopplers=None, ms=10):
    """Rejilla Doppler x fase de codigo por correlacion circular (FFT),
    sumando |corr|^2 de `ms` milisegundos (integracion NO coherente).
    Devuelve (dopplers, rejilla |corr|^2, (i_doppler, fase_muestra),
    cociente pico / segundo pico en dB)."""
    if dopplers is None:
        dopplers = np.arange(-5000.0, 5001.0, 500.0)
    c = 1 - 2 * codigo_ca(prn)
    spc = int(fs / 1.023e6)
    ref = np.repeat(c, spc).astype(complex)
    n = len(ref)
    R = np.conj(np.fft.fft(ref))
    rej = np.zeros((len(dopplers), n))
    for m in range(ms):
        xm = x[m * n:(m + 1) * n]
        t = (np.arange(n) + m * n) / fs
        for i, fd in enumerate(dopplers):
            z = np.fft.ifft(np.fft.fft(xm * np.exp(-2j * np.pi * fd * t)) * R)
            rej[i] += np.abs(z) ** 2
    i, j = np.unravel_index(np.argmax(rej), rej.shape)
    fila = rej[i].copy()
    for k in range(-spc, spc + 1):
        fila[(j + k) % n] = 0
    otro = max(fila.max(), np.delete(rej, i, axis=0).max())
    return dopplers, rej, (int(i), int(j)), float(db10(rej[i, j] / otro))


def ganancia_correlacion_db(n_chips=1023):
    return float(10 * np.log10(n_chips))


# =====================================================================
# 8.1 Transmitir
# =====================================================================
def imagenes_dac(f0_rel=0.1, k_max=3, sobre=64, n_per=200):
    """DAC con retencion de orden cero: simula la salida escalonada con
    `sobre` puntos por muestra y mide (proyeccion coherente) el nivel de
    cada imagen en k*fs +- f0 respecto al tono. Devuelve lista de
    (f_rel, dBc) y el valor teorico sinc."""
    n = n_per * int(round(1 / f0_rel))
    x = np.cos(2 * np.pi * f0_rel * np.arange(n))
    y = np.repeat(x, sobre)
    fs2 = float(sobre)
    p0 = potencia_tono(y.astype(complex), f0_rel, fs2)
    out = []
    for k in range(1, k_max + 1):
        for s in (-1, 1):
            f = k + s * f0_rel
            p = potencia_tono(y.astype(complex), f, fs2)
            teo = 20 * np.log10(abs(np.sinc(f)) / abs(np.sinc(f0_rel)))
            out.append((f, float(db10(p / p0)), float(teo)))
    return out


# =====================================================================
# 8.2 Dos antenas: de donde viene
# =====================================================================
def doa_estimar(theta_deg, d_lambda=0.5, snr_db=10.0, n=2000, semilla=3):
    """Dos antenas a d (en longitudes de onda). La diferencia de fase de la
    senal entre ellas da sin(theta). Devuelve los angulos compatibles
    (uno si d <= 1/2; varios si d > 1/2) y el desfase medido."""
    r = np.random.default_rng(semilla)
    s = np.exp(1j * 2 * np.pi * r.random(n))
    fase = 2 * np.pi * d_lambda * math.sin(math.radians(theta_deg))
    x1 = s + ruido_complejo(n, 10 ** (-snr_db / 10), semilla + 1)
    x2 = s * np.exp(-1j * fase) + ruido_complejo(n, 10 ** (-snr_db / 10),
                                                 semilla + 2)
    dphi = float(np.angle(np.vdot(x2, x1)))
    angulos = []
    for k in range(-3, 4):
        v = (dphi + 2 * np.pi * k) / (2 * np.pi * d_lambda)
        if abs(v) <= 1:
            angulos.append(math.degrees(math.asin(v)))
    return sorted(angulos), dphi


def factor_arreglo(theta_apunta_deg, d_lambda=0.5, n_ant=2, puntos=361):
    th = np.linspace(-90, 90, puntos)
    fase = 2 * np.pi * d_lambda * (np.sin(np.radians(th)) -
                                   math.sin(math.radians(theta_apunta_deg)))
    af = np.abs(np.sum(np.exp(1j * np.outer(np.arange(n_ant), fase)),
                       axis=0)) / n_ant
    return th, db10(af ** 2)


# =====================================================================
# 8.3 La estacion completa: presupuesto de Meteor
# =====================================================================
R_T = 6371.0


def alcance_km(h_km, elev_deg):
    e = math.radians(elev_deg)
    rs = R_T + h_km
    return float(-R_T * math.sin(e) + math.sqrt(rs ** 2 -
                                                (R_T * math.cos(e)) ** 2))


PRESUPUESTO = {          # PARAMETROS ELEGIDOS (gris), no medidos
    "p_tx_dbm": 37.0,     # 5 W
    "g_tx_dbi": 0.0,
    "f_hz": 137.9e6,
    "h_km": 830.0,
    "elev_deg": 20.0,
    "g_rx_dbi": 3.0,      # antena QFH
    "perdidas_db": 3.0,   # polarizacion + apuntamiento
    "nf_db": 1.04,        # el LNA en la antena del 2.1
    "b_hz": 72e3,         # = tasa de simbolos: la SNR es Es/N0
    "esn0_req_db": 4.0,   # donde la cadena del 7.2 da 0 errores (10/10)
}


def presupuesto(p=PRESUPUESTO):
    d = alcance_km(p["h_km"], p["elev_deg"])
    fspl = fspl_db(d, p["f_hz"] / 1e9)
    prx = p["p_tx_dbm"] + p["g_tx_dbi"] - fspl + p["g_rx_dbi"] - \
        p["perdidas_db"]
    ruido = ktb_dbm(p["b_hz"]) + p["nf_db"]
    snr = prx - ruido
    return {"alcance_km": d, "fspl_db": fspl, "prx_dbm": prx,
            "ruido_dbm": ruido, "snr_db": snr,
            "margen_db": snr - p["esn0_req_db"]}

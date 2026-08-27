"""Procesamiento digital de senales: piezas de dibujo y funciones medidas.

Libreria de la familia "Procesamiento de senales" (curso 27). El principio
que la ordena: **la secuencia se ve discreta**. Lo que es una lista de
numeros se dibuja con tallos (Secuencia), nunca con una curva; la curva
azul es el mundo continuo del que se tomaron.

Sustrato que reutiliza (no duplica):
  algebra_lineal : _Anclada, fmt, C_EJE, C_REJILLA, grafica, plano
  comunicaciones : Onda, EspectroArea, muestrear, alias_de, cuantizar,
                   snr_cuantizacion, psd_db, awgn, secuencia_pn
  bloques        : bloque, conectar, flujo

`scipy.signal` esta disponible (llega con manim). Se usa para los disenos
estandar; lo que el espectador tiene que VER funcionando (DFT como matriz,
mariposas, convolucion paso a paso, LMS, PLL, CIC, Q15) se implementa a
mano en numpy.

Toda funcion numerica devuelve lo MEDIDO sobre los datos que se dibujan.
Nada de cifras de tabla.
"""

import math

import numpy as np
from manim import (DashedLine, Dot, Line, ORIGIN, Polygon, Rectangle, Text,
                   VGroup, VMobject)

from algebra_lineal import C_EJE, C_REJILLA, _Anclada, fmt  # noqa: F401
from comunicaciones import (Onda, alias_de, cuantizar,  # noqa: F401
                            snr_cuantizacion)

# =====================================================================
# Paleta por ROL (el color dice el papel)
# =====================================================================
C_SENAL = "#3b82f6"    # azul: el mundo continuo, la entrada
C_MUESTRA = "#f59e0b"  # ambar: la secuencia x[n], h[n], los coeficientes
C_CALCULO = "#22d3ee"  # cian: TODA cifra calculada aqui
C_RUIDO = "#f43f5e"    # rojo: ruido, error, alias, desbordamiento
C_SALIDA = "#34d399"   # verde: la salida y[n], lo reconstruido
C_IDEAL = "#a78bfa"    # violeta: el ideal, el limite teorico
C_APREND = "#e879f9"   # fucsia: lo adaptado, lo aprendido
C_BANDA = "#fb923c"    # naranja: el espectro, las replicas
C_DATO = "#94a0b0"     # gris: dato publico, NO medido aqui

MUESTRAS_MAX = 4000


# =====================================================================
# 1. La senal viva del curso: la vibracion de un lanzador
# =====================================================================
# Tres tonos deterministas: el modo longitudinal lento ("pogo"), un modo
# estructural y una resonancia alta. La misma funcion en todo el modulo 1
# para que el espectador reconozca la senal de un clip a otro.
F_POGO, F_ESTRUCT, F_ALTA = 18.5, 62.0, 220.0
A_POGO, A_ESTRUCT, A_ALTA = 1.00, 0.45, 0.28
P_POGO, P_ESTRUCT, P_ALTA = 0.0, 0.62, 1.90


def vibracion(t):
    """Aceleracion normalizada del lanzador en t (segundos). Deterministica
    y sin ruido: lo que se muestrea en el modulo 1."""
    t = np.asarray(t, dtype=float)
    y = (A_POGO * np.sin(2 * np.pi * F_POGO * t + P_POGO)
         + A_ESTRUCT * np.sin(2 * np.pi * F_ESTRUCT * t + P_ESTRUCT)
         + A_ALTA * np.sin(2 * np.pi * F_ALTA * t + P_ALTA))
    return y / (A_POGO + A_ESTRUCT + A_ALTA)


def muestras_de(f, fs, n, t0=0.0):
    """n muestras de f a fs desde t0. -> (tk, xk)"""
    tk = t0 + np.arange(int(n)) / float(fs)
    return tk, np.asarray(f(tk), dtype=float)


# =====================================================================
# 2. Espectro y replicas
# =====================================================================
def espectro(x, fs, nfft=None, ventana="hann", norm=True, ref=None):
    """|DFT| en dB de una secuencia real, un solo lado. -> (f, db)

    Normalizado a pico 0 dB si `norm`. **Ojo con las gemelas**: `norm`
    normaliza CADA array a su propio pico, asi que dos espectros que se
    van a comparar en pantalla nivel contra nivel tienen que compartir
    referencia — para eso esta `ref` (valor lineal, p.ej. el pico del
    primero, que devuelve `pico_espectro`). Sin eso, dos curvas con
    ruidos muy distintos se dibujan igual de altas y la comparacion
    miente.

    La ventana por defecto es hann porque casi todo lo que se dibuja es
    un trozo de senal, no un periodo entero (la fuga es real y se ve).
    """
    x = np.asarray(x, dtype=float)
    n = int(nfft or len(x))
    w = ventana_de(ventana, len(x))
    xw = x * w
    if n > len(xw):
        xw = np.concatenate([xw, np.zeros(n - len(xw))])
    mag = np.abs(np.fft.rfft(xw[:n], n=n))
    mag = np.maximum(mag, 1e-12)
    if ref is not None:
        divisor = float(ref)
    else:
        divisor = mag.max() if norm else 1.0
    db = 20.0 * np.log10(mag / divisor)
    return np.fft.rfftfreq(n, d=1.0 / fs), db


def pico_espectro(x, ventana="hann", nfft=None):
    """El pico LINEAL del espectro de x: la referencia que se pasa como
    `ref` a `espectro()` para que dos gemelas compartan escala."""
    x = np.asarray(x, dtype=float)
    n = int(nfft or len(x))
    xw = x * ventana_de(ventana, len(x))
    if n > len(xw):
        xw = np.concatenate([xw, np.zeros(n - len(xw))])
    return float(np.maximum(np.abs(np.fft.rfft(xw[:n], n=n)), 1e-12).max())


def espectro_analogico(f, fs_ref, banda, n=2048, ventana="hann"):
    """Espectro de la senal CONTINUA (muy sobremuestreada) recortado a
    `banda` Hz. Es la banda base que luego se replica. -> (f, db)"""
    fs_alto = max(20.0 * banda, 4.0 * fs_ref)
    t = np.arange(n) / fs_alto
    fr, db = espectro(f(t), fs_alto, ventana=ventana)
    m = fr <= banda
    return fr[m], db[m]


def replicas(f_base, db_base, fs, k=2, piso_db=-60.0, f_max=None,
             copias=None):
    """El espectro que ve el muestreador: la banda base COPIADA cada fs.

    Devuelve (f, db) en un eje bilateral. Con `f_max` el eje queda FIJO
    (imprescindible para animar dos fs distintas con Transform: las
    gemelas necesitan el mismo eje), y con `copias` se elige que replicas
    dibujar — `copias=(0,)` es la banda base sola, la gemela natural.

    Las copias se suman en POTENCIA: donde dos se cruzan, la suma sube.
    Por eso el solape se ve, no se afirma.
    """
    f_base = np.asarray(f_base, dtype=float)
    lin = 10.0 ** (np.asarray(db_base, dtype=float) / 10.0)
    if f_max is None:
        f_max = (k + 0.5) * fs
    else:
        f_max = float(f_max)
        k = int(math.ceil(f_max / fs)) + 1
    paso = float(f_base[1] - f_base[0]) if len(f_base) > 1 else fs / 512.0
    eje = np.arange(-f_max, f_max + paso, paso)
    ms = range(-k, k + 1) if copias is None else copias
    acc = np.zeros_like(eje)
    for m in ms:
        # la senal es real: cada copia es par respecto a su centro
        acc += np.interp(np.abs(eje - m * fs), f_base, lin, left=0.0,
                         right=0.0)
    tope = acc.max() if acc.max() > 0 else 1.0
    acc = np.maximum(acc / tope, 10.0 ** (piso_db / 10.0))
    return eje, 10.0 * np.log10(acc)


def banda_ocupada(f, db, umbral_db=-40.0):
    """La frecuencia mas alta que supera el umbral. -> Hz (medido)"""
    f, db = np.asarray(f, float), np.asarray(db, float)
    sobre = f[db >= umbral_db]
    return float(sobre.max()) if len(sobre) else 0.0


def guarda(fs, banda):
    """Hueco MEDIDO entre el borde de una replica y el de la vecina:
    fs - 2*banda. Negativo = se solapan."""
    return float(fs) - 2.0 * float(banda)


def solape_db(f_base, db_base, fs, banda):
    """Cuanta energia de la primera replica cae DENTRO de la banda base,
    en dB relativos a la energia de la banda base. -1 (mucho) a -inf."""
    f_base = np.asarray(f_base, float)
    lin = 10.0 ** (np.asarray(db_base, float) / 10.0)
    dentro = f_base <= banda
    e_base = float(np.sum(lin[dentro]))
    # la replica centrada en fs, vista en la banda base, vale
    # |X(fs - f)| para f en [0, banda]
    intruso = np.interp(np.abs(fs - f_base[dentro]), f_base, lin, left=0.0,
                        right=0.0)
    e_int = float(np.sum(intruso))
    if e_int <= 0.0:
        return -np.inf
    return 10.0 * math.log10(e_int / e_base)


def butter_db(f, fc, orden=6):
    """|H(f)| en dB de un Butterworth ANALOGICO (el filtro antialias que
    va ANTES del muestreador). Formula exacta, sin diseno numerico."""
    f = np.asarray(f, dtype=float)
    return -10.0 * np.log10(1.0 + (np.abs(f) / float(fc)) ** (2 * int(orden)))


def con_antialias(f_base, db_base, fc, orden=6):
    """La banda base DESPUES del filtro antialias. -> db (mismo eje)"""
    return np.asarray(db_base, float) + butter_db(f_base, fc, orden)


# =====================================================================
# 3. Reconstruccion
# =====================================================================
def reconstruir_sinc(tk, xk, t):
    """Interpolacion de Whittaker-Shannon: cada muestra pone una sinc.
    -> x(t) reconstruido (array del tamano de t)."""
    tk = np.asarray(tk, float)
    xk = np.asarray(xk, float)
    t = np.asarray(t, float)
    ts = float(tk[1] - tk[0])
    return np.array([float(np.sum(xk * np.sinc((ti - tk) / ts)))
                     for ti in t])


def zoh(tk, xk, t):
    """El DAC que RETIENE: escalon hasta la muestra siguiente."""
    tk = np.asarray(tk, float)
    xk = np.asarray(xk, float)
    idx = np.clip(np.searchsorted(tk, np.asarray(t, float), side="right") - 1,
                  0, len(xk) - 1)
    return xk[idx]


def droop_db(f, fs):
    """Caida del ZOH en f: 20 log10 |sinc(f/fs)|. En fs/2 son -3.92 dB."""
    return float(20.0 * math.log10(abs(np.sinc(float(f) / float(fs)))))


def error_rms(a, b):
    """RMS de la diferencia (para decir 'reconstruye' con una cifra)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.sqrt(np.mean((a - b) ** 2)))


def snr_jitter(f_hz, sigma_s, n=20000, semilla=11):
    """SNR MEDIDA de muestrear un tono de f_hz con instantes que tiemblan
    sigma_s segundos (rms). La teoria dice -20 log10(2 pi f sigma).
    -> (snr_medida_db, snr_teorica_db)"""
    rng = np.random.default_rng(semilla)
    fs = 8.0 * float(f_hz)
    tk = np.arange(n) / fs
    limpio = np.sin(2 * np.pi * f_hz * tk)
    sucio = np.sin(2 * np.pi * f_hz * (tk + rng.normal(0.0, sigma_s, n)))
    err = sucio - limpio
    medida = 10.0 * math.log10(float(np.mean(limpio ** 2) /
                                     np.mean(err ** 2)))
    teorica = -20.0 * math.log10(2 * math.pi * float(f_hz) * float(sigma_s))
    return medida, teorica


# =====================================================================
# 4. Cuantizacion
# =====================================================================
def escalones(x, bits, x_min=-1.0, x_max=1.0):
    """La version cuantizada y el error. -> (xq, err, paso)"""
    x = np.asarray(x, dtype=float)
    _, xq = cuantizar(x, bits, x_min, x_max)
    paso = (x_max - x_min) / (2 ** int(bits))
    return xq, x - xq, paso


def sqnr_medida(x, bits, x_min=-1.0, x_max=1.0):
    """SNR de cuantizacion MEDIDA sobre exactamente esta senal, en dB."""
    return float(snr_cuantizacion(np.asarray(x, float), bits, x_min, x_max))


def recta_bits(x, bits_lista):
    """SQNR medida para cada numero de bits + la recta ajustada.
    -> (bits, sqnr_db, pendiente_db_por_bit, ordenada_db)"""
    bits = np.asarray(list(bits_lista), dtype=float)
    sq = np.array([sqnr_medida(x, int(b)) for b in bits])
    pend, orde = np.polyfit(bits, sq, 1)
    return bits, sq, float(pend), float(orde)


def dither(x, bits, semilla=5, amplitud=1.0):
    """Cuantizar con y sin dither TPDF de `amplitud` pasos.
    -> (xq_sin, xq_con, paso)"""
    x = np.asarray(x, float)
    paso = 2.0 / (2 ** int(bits))
    rng = np.random.default_rng(semilla)
    d = (rng.random(len(x)) - rng.random(len(x))) * amplitud * paso
    _, q_sin = cuantizar(x, bits)
    _, q_con = cuantizar(np.clip(x + d, -1.0, 1.0), bits)
    return q_sin, q_con, paso


def espurio_db(x, xq, fs, f_tono, ancho_bins=3):
    """El espurio MAS ALTO del error de cuantizacion, en dB bajo el tono.

    Mide sobre el error (xq - x): busca su pico ignorando los bins del
    propio tono. Devuelve (espurio_db, piso_db) — el piso es la mediana.
    """
    err = np.asarray(xq, float) - np.asarray(x, float)
    n = len(err)
    f = np.fft.rfftfreq(n, d=1.0 / fs)
    mag = np.abs(np.fft.rfft(err * ventana_de("hann", n)))
    ref = np.abs(np.fft.rfft(np.asarray(x, float) * ventana_de("hann", n)))
    ref_pico = float(ref.max())
    lejos = np.abs(f - f_tono) > ancho_bins * (fs / n)
    pico = float(mag[lejos].max())
    piso = float(np.median(mag[lejos]))
    return (20.0 * math.log10(pico / ref_pico),
            20.0 * math.log10(max(piso, 1e-15) / ref_pico))


def noise_shaping(x, bits, orden=1):
    """Cuantizacion con realimentacion del error (error feedback).

    El error de una muestra se resta de la siguiente: el ruido sale
    empujado hacia las frecuencias altas. -> (xq, err)
    """
    x = np.asarray(x, float)
    paso = 2.0 / (2 ** int(bits))
    xq = np.zeros_like(x)
    e1 = e2 = 0.0
    for i, xi in enumerate(x):
        if orden >= 2:
            v = xi - 2.0 * e1 + e2
        else:
            v = xi - e1
        q = np.clip(np.round(v / paso - 0.5) + 0.5, -2 ** (bits - 1) + 0.5,
                    2 ** (bits - 1) - 0.5) * paso
        e2, e1 = e1, q - v
        xq[i] = q
    return xq, xq - x


def sqnr_en_banda(x, xq, fs, f_banda):
    """SNR contando solo el ruido que cae DENTRO de la banda util (lo que
    de verdad molesta cuando se sobremuestrea). -> dB medidos"""
    x, xq = np.asarray(x, float), np.asarray(xq, float)
    n = len(x)
    f = np.fft.rfftfreq(n, d=1.0 / fs)
    w = ventana_de("hann", n)
    px = np.abs(np.fft.rfft(x * w)) ** 2
    pe = np.abs(np.fft.rfft((xq - x) * w)) ** 2
    dentro = f <= f_banda
    return 10.0 * math.log10(float(px[dentro].sum() /
                                   max(pe[dentro].sum(), 1e-30)))


# =====================================================================
# 5. Ventanas (las necesita el modulo 3, pero el espectro ya las usa)
# =====================================================================
def ventana_de(nombre, n):
    """Ventana por nombre, calculada a mano (n muestras)."""
    n = int(n)
    k = np.arange(n)
    if nombre in (None, "rect", "rectangular"):
        return np.ones(n)
    if nombre == "hann":
        return 0.5 - 0.5 * np.cos(2 * np.pi * k / (n - 1))
    if nombre == "hamming":
        return 0.54 - 0.46 * np.cos(2 * np.pi * k / (n - 1))
    if nombre == "blackman":
        return (0.42 - 0.5 * np.cos(2 * np.pi * k / (n - 1))
                + 0.08 * np.cos(4 * np.pi * k / (n - 1)))
    raise ValueError(f"ventana desconocida: {nombre}")


# =====================================================================
# 6. Sistemas LTI, convolucion y correlacion
# =====================================================================
def impulso(n, k=0):
    """delta[n - k] en una secuencia de n muestras."""
    x = np.zeros(int(n))
    x[int(k)] = 1.0
    return x


def respuesta_impulso(b, a, n):
    """h[n] de un sistema (b, a) por recursion directa (sin scipy: el
    espectador ve que h ES la salida ante un impulso)."""
    return filtrar(b, a, impulso(int(n)))


def filtrar(b, a, x):
    """Ecuacion en diferencias directa (forma I), la que se dibuja."""
    b = np.asarray(b, float)
    a = np.asarray(a, float)
    x = np.asarray(x, float)
    if a[0] != 1.0:
        b, a = b / a[0], a / a[0]
    y = np.zeros(len(x))
    for n in range(len(x)):
        acc = 0.0
        for i in range(len(b)):
            if n - i >= 0:
                acc += b[i] * x[n - i]
        for j in range(1, len(a)):
            if n - j >= 0:
                acc -= a[j] * y[n - j]
        y[n] = acc
    return y


def convolucion(x, h):
    """y = x * h (longitud N + M - 1), a mano."""
    x = np.asarray(x, float)
    h = np.asarray(h, float)
    y = np.zeros(len(x) + len(h) - 1)
    for n in range(len(y)):
        acc = 0.0
        for k in range(len(x)):
            if 0 <= n - k < len(h):
                acc += x[k] * h[n - k]
        y[n] = acc
    return y


def pasos_convolucion(x, h):
    """Un dict por muestra de salida, para animar el deslizamiento:
    {'n', 'k' (indices de x que solapan), 'productos', 'y'}"""
    x = np.asarray(x, float)
    h = np.asarray(h, float)
    pasos = []
    for n in range(len(x) + len(h) - 1):
        ks = [k for k in range(len(x)) if 0 <= n - k < len(h)]
        pr = [float(x[k] * h[n - k]) for k in ks]
        pasos.append({"n": n, "k": ks, "productos": pr, "y": float(sum(pr))})
    return pasos


def macs_convolucion(x, h):
    """Multiplicaciones REALES que cuesta la convolucion directa."""
    return int(sum(len(p["k"]) for p in pasos_convolucion(x, h)))


def suma_abs(h):
    """sum |h[n]|: finita = BIBO estable."""
    return float(np.sum(np.abs(np.asarray(h, float))))


def correlacion(x, y):
    """Correlacion cruzada completa. -> (retardos, r)"""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    r = np.correlate(x, y, mode="full")
    lags = np.arange(-(len(y) - 1), len(x))
    return lags, r


def chirp(t, f0, f1, dur):
    """Barrido lineal de f0 a f1 en `dur` segundos."""
    t = np.asarray(t, float)
    k = (f1 - f0) / dur
    return np.sin(2 * np.pi * (f0 * t + 0.5 * k * t ** 2))


def enterrar(patron, snr_db, n_total, offset, semilla=3):
    """El patron escondido en ruido dentro de un registro largo.
    -> (rx, snr_medida_db)"""
    rng = np.random.default_rng(semilla)
    patron = np.asarray(patron, float)
    pot_s = float(np.mean(patron ** 2))
    sigma = math.sqrt(pot_s / (10.0 ** (snr_db / 10.0)))
    rx = rng.normal(0.0, sigma, int(n_total))
    rx[offset:offset + len(patron)] += patron
    medida = 10.0 * math.log10(pot_s / (sigma ** 2))
    return rx, medida


def ganancia_proceso_db(rx, patron, offset):
    """Cuanto sube la senal sobre el ruido al correlar, MEDIDO:
    (pico/rms_lejos) del correlador menos (pico/rms) de la entrada."""
    lags, r = correlacion(rx, patron)
    i = int(np.argmax(r))
    pico = float(r[i])
    fuera = np.ones(len(r), dtype=bool)
    fuera[max(0, i - 8):i + 9] = False
    rms_r = float(np.sqrt(np.mean(r[fuera] ** 2)))
    antes = float(np.max(np.abs(patron)) /
                  np.sqrt(np.mean(np.asarray(rx, float) ** 2)))
    return (20.0 * math.log10(pico / rms_r) - 20.0 * math.log10(antes),
            int(lags[i]))


def ancho_pico(lags, r, caida_db=3.0):
    """Ancho del pico de correlacion a -3 dB, en muestras (medido)."""
    r = np.abs(np.asarray(r, float))
    i = int(np.argmax(r))
    umbral = r[i] * 10.0 ** (-caida_db / 20.0)
    izq = i
    while izq > 0 and r[izq] > umbral:
        izq -= 1
    der = i
    while der < len(r) - 1 and r[der] > umbral:
        der += 1
    return int(lags[der] - lags[izq])


def compresion(patron, lags, r):
    """Cuanto ACORTA el correlador el pulso: largo del patron dividido
    entre el ancho a -3 dB del pico. -> (razon, ancho_muestras)"""
    ancho = ancho_pico(lags, r)
    return float(len(patron)) / max(ancho, 1), int(ancho)


def pn_larga(n=127, semilla_reg=0b1000001):
    """m-secuencia de un LFSR de m etapas, chips +-1 (misma construccion
    que `comunicaciones.secuencia_pn`, generalizada).

    Polinomios primitivos: x^5+x^2+1, x^6+x^5+1, x^7+x^6+1, x^8+x^6+x^5+x^4+1.
    La autocorrelacion CIRCULAR vale n en el origen y -1 en todo lo demas
    (se comprueba en la sonda).
    """
    m = int(round(math.log2(n + 1)))
    if 2 ** m - 1 != int(n):
        raise ValueError("n tiene que ser 2^m - 1")
    tomas = {5: ((4, 1),), 6: ((5, 4),), 7: ((6, 5),),
             8: ((7, 5, 4, 3),)}[m][0]
    reg = [int(b) for b in format(semilla_reg & (2 ** m - 1), f"0{m}b")]
    if not any(reg):
        reg[-1] = 1
    chips = []
    for _ in range(int(n)):
        chips.append(reg[-1])
        nuevo = 0
        for t in tomas:
            nuevo ^= reg[t]
        reg = [nuevo] + reg[:-1]
    return np.array([1.0 if c else -1.0 for c in chips])


def autocorr_circular(x):
    """R[k] = sum x[i] x[i+k mod n]: la que vale -1 fuera del origen."""
    x = np.asarray(x, float)
    return np.array([float(np.dot(x, np.roll(x, -k))) for k in range(len(x))])


# =====================================================================
# 7. Piezas de dibujo
# =====================================================================
class Secuencia(_Anclada):
    """x[n] con TALLOS (nunca una curva): la firma visual de la familia.

    .en(n, y)          punto del plano de la pieza
    .tallo(i) .punto(i)
    .marcar(i, color)  circulo de resalte sobre una muestra
    .ventana(a, b)     rectangulo translucido sobre un tramo
    .curva_de(t, y)    una curva continua en la MISMA caja (el mundo)
    .con_valores(y2)   GEMELA de estructura identica (Transform seguro)
    """

    _EPS = 0.012   # tallo minimo visible: mantiene la estructura gemela

    def __init__(self, x, n0=0, rango_y=None, ancho=8.0, alto=2.4,
                 color=C_MUESTRA, radio=0.055, grosor=2.4, eje_y=True,
                 **kwargs):
        super().__init__(**kwargs)
        self.x = np.asarray(x, dtype=float)
        if len(self.x) > MUESTRAS_MAX:
            raise ValueError("secuencia demasiado larga para dibujar")
        self.n0 = int(n0)
        if rango_y is None:
            m = float(np.max(np.abs(self.x))) * 1.2 + 1e-9
            rango_y = (-m, m)
        self.y0, self.y1 = float(rango_y[0]), float(rango_y[1])
        self.nmin = self.n0 - 0.5
        self.nmax = self.n0 + len(self.x) - 0.5
        self.ancho, self.alto = float(ancho), float(alto)
        self.color, self.radio, self.grosor = color, radio, grosor
        self.eje_y = bool(eje_y)
        self._poner_ancla(ORIGIN)
        cy = 0.0 if self.y0 <= 0 <= self.y1 else self.y0
        ex = Line(self.en(self.nmin, cy), self.en(self.nmax, cy),
                  color=C_EJE, stroke_width=1.6)
        self.ejes = VGroup(ex)
        if self.eje_y:
            self.ejes.add(Line(self.en(self.nmin, self.y0),
                               self.en(self.nmin, self.y1), color=C_EJE,
                               stroke_width=1.6))
        self.tallos = VGroup()
        self.puntos = VGroup()
        for i, v in enumerate(self.x):
            n = self.n0 + i
            v_dib = v if abs(v) > 1e-9 else self._EPS * (self.y1 - self.y0)
            self.tallos.add(Line(self.en(n, cy), self.en(n, v_dib),
                                 color=color, stroke_width=grosor))
            self.puntos.add(Dot(self.en(n, v), radius=radio, color=color))
        self.add(self.ejes, self.tallos, self.puntos)

    def en(self, n, y):
        fx = (float(n) - self.nmin) / (self.nmax - self.nmin)
        fy = ((float(np.clip(y, self.y0, self.y1)) - self.y0)
              / (self.y1 - self.y0))
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (fy - 0.5) * self.alto, 0.0]))

    def tallo(self, i):
        return self.tallos[int(i)]

    def punto(self, i):
        return self.puntos[int(i)]

    def marcar(self, i, color=C_CALCULO, radio=None):
        p = self.puntos[int(i)]
        return Dot(p.get_center(), radius=(radio or self.radio) * 2.1,
                   color=color, fill_opacity=0.0, stroke_width=2.4,
                   stroke_opacity=1.0)

    def ventana(self, a, b, color=C_CALCULO, opacidad=0.14):
        x0 = self.en(self.n0 + a - 0.5, 0)[0]
        x1 = self.en(self.n0 + b + 0.5, 0)[0]
        r = Rectangle(width=abs(x1 - x0), height=self.alto, stroke_width=1.4,
                      stroke_color=color, fill_color=color,
                      fill_opacity=opacidad)
        r.move_to(np.array([(x0 + x1) / 2.0,
                            self.en(self.n0, (self.y0 + self.y1) / 2)[1],
                            0.0]))
        return r

    def curva_de(self, t, y, color=C_SENAL, grosor=2.2, fs=None):
        """Una curva continua sobre la MISMA caja. `t` va en muestras
        (n) salvo que se de `fs`, en cuyo caso va en segundos."""
        t = np.asarray(t, float)
        n = t * float(fs) if fs else t
        c = VMobject(color=color, stroke_width=grosor)
        c.set_points_as_corners([self.en(a, b) for a, b in zip(n, y)])
        return c

    def vertical_en(self, n, color=C_CALCULO):
        return DashedLine(self.en(n, self.y0), self.en(n, self.y1),
                          color=color, stroke_width=1.6, dash_length=0.07)

    def horizontal_en(self, y, color=C_CALCULO):
        return DashedLine(self.en(self.nmin, y), self.en(self.nmax, y),
                          color=color, stroke_width=1.6, dash_length=0.07)

    def con_valores(self, y2, color=None):
        """GEMELA: misma caja, mismo numero de tallos, otros valores."""
        y2 = np.asarray(y2, float)
        if len(y2) != len(self.x):
            raise ValueError("la gemela necesita el MISMO numero de muestras")
        o = Secuencia(y2, self.n0, (self.y0, self.y1), self.ancho, self.alto,
                      color or self.color, self.radio, self.grosor,
                      self.eje_y)
        o.shift(self._origen() - o._origen())
        return o


def secuencia(x, n0=0, rango_y=None, ancho=8.0, alto=2.4, color=C_MUESTRA,
              radio=0.055, grosor=2.4, eje_y=True):
    """Ver `Secuencia`."""
    return Secuencia(x, n0, rango_y, ancho, alto, color, radio, grosor,
                     eje_y)


class Escalera(_Anclada):
    """La senal, su version cuantizada en escalones y el error debajo.

    .curva   .pasos   .error_caja   .en(t, y)   .con_bits(bits) GEMELA
    """

    def __init__(self, t, x, bits, ancho=7.6, alto=2.2, alto_err=1.0,
                 x_min=-1.0, x_max=1.0, paso_ref=None, **kwargs):
        super().__init__(**kwargs)
        self.t = np.asarray(t, float)
        self.x = np.asarray(x, float)
        self.bits = int(bits)
        self.ancho, self.alto, self.alto_err = (float(ancho), float(alto),
                                                float(alto_err))
        self.x_min, self.x_max = float(x_min), float(x_max)
        self._poner_ancla(ORIGIN)
        xq, err, self.paso = escalones(self.x, self.bits, x_min, x_max)
        self.xq, self.err = xq, err
        # La escala del carril de error es FIJA (la del paso de referencia).
        # Si cada version se normalizara por SU paso, la gemela de 8 bits
        # dibujaria su error a la misma altura que la de 4 y el momento
        # "el error se encoge" quedaria mudo: medido en el lote 1.
        self.paso_ref = float(paso_ref) if paso_ref else self.paso
        ex = Line(self.en(self.t[0], 0.0), self.en(self.t[-1], 0.0),
                  color=C_EJE, stroke_width=1.6)
        ey = Line(self.en(self.t[0], x_min), self.en(self.t[0], x_max),
                  color=C_EJE, stroke_width=1.6)
        self.ejes = VGroup(ex, ey)
        self.curva = self._poli(self.x, C_SENAL, 3.0)
        self.pasos = self._escalones(xq)
        self.error_caja = self._error(err)
        self.add(self.ejes, self.pasos, self.curva, self.error_caja)

    def en(self, t, y):
        fx = ((float(t) - self.t[0]) / (self.t[-1] - self.t[0]))
        fy = ((float(np.clip(y, self.x_min, self.x_max)) - self.x_min)
              / (self.x_max - self.x_min))
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (fy - 0.5) * self.alto, 0.0]))

    def en_error(self, t, e):
        base = self._origen() + np.array([0.0,
                                          -self.alto / 2 - self.alto_err, 0.0])
        fx = (float(t) - self.t[0]) / (self.t[-1] - self.t[0])
        fy = (float(np.clip(e, -self.paso_ref, self.paso_ref))
              / (2 * self.paso_ref))
        return base + np.array([(fx - 0.5) * self.ancho,
                                fy * self.alto_err, 0.0])

    def _poli(self, y, color, grosor):
        c = VMobject(color=color, stroke_width=grosor)
        c.set_points_as_corners([self.en(a, b) for a, b in zip(self.t, y)])
        return c

    def _escalones(self, xq):
        pts = []
        for i in range(len(self.t)):
            pts.append(self.en(self.t[i], xq[i]))
            if i + 1 < len(self.t):
                pts.append(self.en(self.t[i + 1], xq[i]))
        c = VMobject(color=C_MUESTRA, stroke_width=2.2)
        c.set_points_as_corners(pts)
        return c

    def _error(self, err):
        eje = Line(self.en_error(self.t[0], 0.0),
                   self.en_error(self.t[-1], 0.0), color=C_EJE,
                   stroke_width=1.2)
        c = VMobject(color=C_RUIDO, stroke_width=2.0)
        c.set_points_as_corners([self.en_error(a, b)
                                 for a, b in zip(self.t, err)])
        return VGroup(eje, c)

    def con_bits(self, bits):
        """GEMELA con otra resolucion (misma caja, misma estructura).

        Hereda `paso_ref`, asi que su carril de error se dibuja en la
        MISMA escala: mas bits = error visiblemente mas chico.
        """
        o = Escalera(self.t, self.x, int(bits), self.ancho, self.alto,
                     self.alto_err, self.x_min, self.x_max, self.paso_ref)
        o.shift(self._origen() - o._origen())
        return o


def escalera(t, x, bits, ancho=7.6, alto=2.2, alto_err=1.0, paso_ref=None):
    """Ver `Escalera`."""
    return Escalera(t, x, bits, ancho, alto, alto_err, paso_ref=paso_ref)


class Deslizador(VGroup):
    """La convolucion EN MARCHA, en cuatro carriles alineados:

        x[n]        azul     (fijo)
        h volteada  ambar    (se desliza: .colocar(n) / .paso_a(n))
        productos   cian     (x[k]*h[n-k] en su sitio; GEMELA por n)
        y[n]        verde    (crece; GEMELA por n)

    Los carriles de productos y de salida tienen SIEMPRE el mismo numero
    de tallos, asi que `Transform` entre pasos es seguro (la trampa de
    las gemelas de estructura distinta).

    Uso tipico:
        d = deslizador(x, h)
        self.add(d)
        for n in range(len(d.y)):
            self.play(d.sh.animate.shift(d.paso_a(n)),
                      Transform(d.sp, d.productos_en(n)),
                      Transform(d.sy, d.salida_hasta(n)), run_time=0.5)
    """

    def __init__(self, x, h, ancho=8.4, alto=1.15, separacion=1.45,
                 **kwargs):
        super().__init__(**kwargs)
        self.x = np.asarray(x, float)
        self.h = np.asarray(h, float)
        self.pasos = pasos_convolucion(self.x, self.h)
        self.y = convolucion(self.x, self.h)
        self.ancho, self.alto = float(ancho), float(alto)
        mx = float(np.max(np.abs(self.x))) * 1.3
        mh = float(np.max(np.abs(self.h))) * 1.3
        mp = max([abs(v) for p in self.pasos for v in p["productos"]] or [1.0])
        my = float(np.max(np.abs(self.y))) * 1.3
        # el paso de rejilla lo fija x: h se dibuja con el MISMO paso para
        # que al deslizar caiga sobre las muestras, no entre ellas.
        self._paso = ancho / len(self.x)
        self.sx = Secuencia(self.x, 0, (-mx, mx), ancho, alto, C_SENAL,
                            eje_y=False)
        self.sh = Secuencia(self.h[::-1], 0, (-mh, mh),
                            self._paso * len(self.h), alto * 0.86,
                            C_MUESTRA, eje_y=False)
        self.sp = Secuencia(np.zeros(len(self.x)), 0, (-mp * 1.3, mp * 1.3),
                            ancho, alto * 0.86, C_CALCULO, eje_y=False)
        self.sy = Secuencia(np.zeros(len(self.y)), 0, (-my, my), ancho, alto,
                            C_SALIDA, eje_y=False)
        self.sx.move_to(np.array([0.0, 1.5 * separacion, 0.0]))
        self.sp.move_to(np.array([0.0, -0.5 * separacion, 0.0]))
        self.sy.move_to(np.array([0.0, -1.5 * separacion, 0.0]))
        self._y_h = 0.5 * separacion
        self.n_actual = None
        self.colocar(0)
        self.add(self.sx, self.sh, self.sp, self.sy)

    # -- posicion de h ------------------------------------------------
    def _x_de(self, n):
        """Donde tiene que caer la ULTIMA muestra de h volteada (h[0])
        para calcular y[n]: sobre la columna de x[n]."""
        return self.sx.en(n, 0.0)[0]

    def colocar(self, n):
        """Salto directo a la posicion n (sin animar)."""
        actual = self.sh.en(len(self.h) - 1, 0.0)[0]
        self.sh.shift(np.array([self._x_de(int(n)) - actual,
                                self._y_h - self.sh.en(0, 0.0)[1], 0.0]))
        self.n_actual = int(n)
        return self.sh

    def paso_a(self, n):
        """El vector que hay que .animate.shift() para ir a la posicion n
        desde donde este ahora."""
        actual = self.sh.en(len(self.h) - 1, 0.0)[0]
        d = np.array([self._x_de(int(n)) - actual, 0.0, 0.0])
        self.n_actual = int(n)
        return d

    # -- carriles gemelos ---------------------------------------------
    def productos_en(self, n):
        """GEMELA del carril de productos con los de la salida n."""
        vals = np.zeros(len(self.x))
        p = self.pasos[int(n)]
        for k, pr in zip(p["k"], p["productos"]):
            vals[k] = pr
        return self.sp.con_valores(vals)

    def salida_hasta(self, n):
        """GEMELA del carril de salida con y[0..n] y el resto a cero."""
        vals = np.zeros(len(self.y))
        vals[:int(n) + 1] = self.y[:int(n) + 1]
        return self.sy.con_valores(vals)

    def resalte(self, n, color=C_CALCULO, opacidad=0.12):
        """Rectangulo sobre las muestras de x que participan en y[n]."""
        p = self.pasos[int(n)]
        if not p["k"]:
            return VGroup()
        return self.sx.ventana(min(p["k"]), max(p["k"]), color=color,
                               opacidad=opacidad)

    def marca_salida(self, n, color=C_CALCULO):
        """Circulo sobre la muestra y[n] que se acaba de calcular."""
        return self.sy.marcar(int(n), color=color)


def deslizador(x, h, ancho=8.4, alto=1.15, separacion=1.45):
    """Ver `Deslizador`."""
    return Deslizador(x, h, ancho, alto, separacion)


class Barras(_Anclada):
    """Valores como barras verticales (coeficientes, SQNR por bits...).

    .barra(i)  .etiqueta(i, texto)  .con_valores(v2) GEMELA
    """

    def __init__(self, valores, ancho=6.0, alto=2.4, color=C_CALCULO,
                 rango_y=None, hueco=0.28, **kwargs):
        super().__init__(**kwargs)
        self.v = np.asarray(valores, float)
        self.ancho, self.alto = float(ancho), float(alto)
        self.color, self.hueco = color, float(hueco)
        if rango_y is None:
            lo = min(0.0, float(self.v.min()) * 1.15)
            hi = max(0.0, float(self.v.max()) * 1.15)
            rango_y = (lo, hi if hi > lo else lo + 1.0)
        self.y0, self.y1 = float(rango_y[0]), float(rango_y[1])
        self._poner_ancla(ORIGIN)
        n = len(self.v)
        w = self.ancho / n
        eje = Line(self._en(0, self.y0), self._en(n, self.y0), color=C_EJE,
                   stroke_width=1.6)
        self.ejes = VGroup(eje)
        self.barras = VGroup()
        for i, v in enumerate(self.v):
            h = (float(np.clip(v, self.y0, self.y1)) - self.y0) \
                / (self.y1 - self.y0) * self.alto
            h = max(h, 0.004)
            r = Rectangle(width=w * (1 - hueco), height=h, stroke_width=1.2,
                          stroke_color=color, fill_color=color,
                          fill_opacity=0.45)
            r.move_to(self._en(i + 0.5, self.y0) + np.array([0, h / 2, 0]))
            self.barras.add(r)
        self.add(self.ejes, self.barras)

    def _en(self, i, y):
        fx = float(i) / len(self.v)
        fy = (float(np.clip(y, self.y0, self.y1)) - self.y0) \
            / (self.y1 - self.y0)
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (fy - 0.5) * self.alto, 0.0]))

    def barra(self, i):
        return self.barras[int(i)]

    def cima(self, i):
        return self.barras[int(i)].get_top()

    def con_valores(self, v2, color=None):
        if len(v2) != len(self.v):
            raise ValueError("la gemela necesita el MISMO numero de barras")
        o = Barras(v2, self.ancho, self.alto, color or self.color,
                   (self.y0, self.y1), self.hueco)
        o.shift(self._origen() - o._origen())
        return o


def barras(valores, ancho=6.0, alto=2.4, color=C_CALCULO, rango_y=None,
           hueco=0.28):
    """Ver `Barras`."""
    return Barras(valores, ancho, alto, color, rango_y, hueco)


class EspectroDoble(_Anclada):
    """Espectro BILATERAL (para las replicas): eje de -f a +f, area
    rellena, marcas en los multiplos de fs.

    .en(f, db)  .marca_f(f)  .banda(a, b)  .con_db(db2) GEMELA
    """

    def __init__(self, f, db, piso_db=-60.0, ancho=9.0, alto=2.3,
                 color=C_BANDA, **kwargs):
        super().__init__(**kwargs)
        self.f = np.asarray(f, float)
        self.db = np.asarray(db, float)
        self.piso = float(piso_db)
        self.ancho, self.alto = float(ancho), float(alto)
        self.color = color
        self._poner_ancla(ORIGIN)
        ex = Line(self.en(self.f[0], self.piso),
                  self.en(self.f[-1], self.piso), color=C_EJE,
                  stroke_width=1.6)
        self.ejes = VGroup(ex)
        pts = [self.en(a, b) for a, b in zip(self.f, self.db)]
        self.curva = VMobject(color=color, stroke_width=2.2)
        self.curva.set_points_as_corners(pts)
        self.area = Polygon(self.en(self.f[0], self.piso), *pts,
                            self.en(self.f[-1], self.piso), stroke_width=0,
                            fill_color=color, fill_opacity=0.20)
        self.add(self.ejes, self.area, self.curva)

    def en(self, f, db):
        fx = (float(f) - self.f[0]) / (self.f[-1] - self.f[0])
        fy = (float(np.clip(db, self.piso, 0.0)) - self.piso) / (0.0 -
                                                                 self.piso)
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (fy - 0.5) * self.alto, 0.0]))

    def marca_f(self, f, color=C_CALCULO, dash=0.07):
        return DashedLine(self.en(f, self.piso), self.en(f, 0.0), color=color,
                          stroke_width=1.6, dash_length=dash)

    def banda(self, a, b, color=C_CALCULO, opacidad=0.16):
        x0, x1 = self.en(a, 0)[0], self.en(b, 0)[0]
        r = Rectangle(width=abs(x1 - x0), height=self.alto, stroke_width=0,
                      fill_color=color, fill_opacity=opacidad)
        r.move_to(np.array([(x0 + x1) / 2.0, self.en(0, self.piso / 2)[1],
                            0.0]))
        return r

    def con_db(self, db2, color=None):
        if len(db2) != len(self.db):
            raise ValueError("la gemela necesita el MISMO eje de frecuencia")
        o = EspectroDoble(self.f, db2, self.piso, self.ancho, self.alto,
                          color or self.color)
        o.shift(self._origen() - o._origen())
        return o


def espectro_doble(f, db, piso_db=-60.0, ancho=9.0, alto=2.3,
                   color=C_BANDA):
    """Ver `EspectroDoble`."""
    return EspectroDoble(f, db, piso_db, ancho, alto, color)

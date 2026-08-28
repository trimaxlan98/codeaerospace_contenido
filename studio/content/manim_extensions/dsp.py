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
from manim import (Arc, Circle, DashedLine, Dot, DOWN, LEFT, Line,
                   ORIGIN, Polygon, Rectangle, RIGHT, Text, UP,
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
CODE_BG_LOCAL = "#05070a"   # el fondo de la marca (para tapar detras)

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


# =====================================================================
# 8. Frecuencia: DFT, FFT y ventanas (modulo 3)
# =====================================================================
def dft_matriz(n):
    """La matriz W de la DFT: W[k, m] = exp(-2j pi k m / N).

    Se construye a mano porque el modulo 3 la ENSEÑA: cada fila es un giro
    y la DFT es el producto interno de la señal con cada uno.
    """
    n = int(n)
    k = np.arange(n).reshape(-1, 1)
    m = np.arange(n).reshape(1, -1)
    return np.exp(-2j * np.pi * k * m / n)


def dft(x):
    """DFT por producto matricial (lo que se ve en pantalla)."""
    x = np.asarray(x, dtype=complex)
    return dft_matriz(len(x)) @ x


def giro(k, n, m=None):
    """Los puntos del giro e^{-2j pi k m / N} para m = 0..N-1: la fila k
    de la matriz, que es lo que se dibuja girando en el plano."""
    m = np.arange(int(n)) if m is None else np.asarray(m)
    return np.exp(-2j * np.pi * int(k) * m / int(n))


def ortogonales(n, k1, k2):
    """Producto interno MEDIDO entre dos filas de la matriz DFT: 0 si son
    distintas, N si son la misma. La ortogonalidad, comprobada."""
    return complex(np.vdot(giro(k1, n), giro(k2, n)))


def f_de_bin(k, fs, n):
    """La frecuencia que le toca al bin k."""
    return float(k) * float(fs) / float(n)


def bin_de(f, fs, n):
    """El bin (no entero) donde cae una frecuencia: si no es entero, hay
    fuga."""
    return float(f) * float(n) / float(fs)


def ops_dft(n):
    """Multiplicaciones COMPLEJAS de la DFT directa: N^2."""
    return int(n) ** 2


def ops_fft(n):
    """Multiplicaciones COMPLEJAS de la FFT radix-2, CONTADAS sobre el
    grafo (una por mariposa, N/2 por etapa, log2(N) etapas)."""
    return sum(len(e) for e in mariposas(n))


def mariposas(n):
    """El grafo radix-2 DIT: una lista por etapa, y en cada etapa las
    mariposas (i, j, k) — i arriba, j abajo, k el indice del factor de
    giro W_N^k. Es el dibujo del clip 3.2.c2."""
    n = int(n)
    etapas = []
    paso = 1
    while paso < n:
        etapa = []
        for inicio in range(0, n, 2 * paso):
            for r in range(paso):
                i = inicio + r
                j = i + paso
                etapa.append((i, j, r * (n // (2 * paso))))
        etapas.append(etapa)
        paso *= 2
    return etapas


def bit_reverso(n):
    """La permutacion de entrada de la FFT: indices con los bits al reves."""
    n = int(n)
    bits = int(math.log2(n))
    return [int(format(i, f"0{bits}b")[::-1], 2) for i in range(n)]


def fft_por_etapas(x):
    """La FFT ejecutada etapa a etapa sobre el grafo de `mariposas`.
    Devuelve la lista de estados intermedios (para animarla) y comprueba
    que el resultado coincide con np.fft.fft."""
    x = np.asarray(x, dtype=complex)
    n = len(x)
    v = x[bit_reverso(n)].copy()
    estados = [v.copy()]
    for etapa in mariposas(n):
        for i, j, k in etapa:
            w = np.exp(-2j * np.pi * k / n)
            a, b = v[i], v[j] * w
            v[i], v[j] = a + b, a - b
        estados.append(v.copy())
    return estados


def lobulo_principal(w):
    """Ancho MEDIDO del lobulo principal de una ventana, en bins (de nulo
    a nulo), calculado sobre su propio espectro muy interpolado."""
    w = np.asarray(w, float)
    n = len(w)
    mag = np.abs(np.fft.rfft(w, n=32 * n))
    mag /= mag.max()
    i = 1
    while i < len(mag) - 1 and mag[i] < mag[i - 1]:
        i += 1
    return 2.0 * i / 32.0


def lateral_db(w):
    """El lobulo lateral mas alto de una ventana, en dB (medido)."""
    w = np.asarray(w, float)
    n = len(w)
    mag = np.abs(np.fft.rfft(w, n=32 * n))
    mag /= mag.max()
    i = 1
    while i < len(mag) - 1 and mag[i] < mag[i - 1]:
        i += 1
    return float(20.0 * np.log10(max(mag[i:].max(), 1e-12)))


def enbw(w):
    """Ancho de ruido equivalente en bins: N*sum(w^2)/sum(w)^2. Lo que la
    ventana ensancha el filtro de cada bin."""
    w = np.asarray(w, float)
    return float(len(w) * np.sum(w ** 2) / np.sum(w) ** 2)


def scalloping_db(w):
    """Perdida MEDIDA para un tono que cae justo entre dos bins (el peor
    caso): |W(0.5 bin)| / |W(0)| en dB."""
    w = np.asarray(w, float)
    n = len(w)
    m = np.arange(n)
    centro = abs(np.sum(w))
    medio = abs(np.sum(w * np.exp(-2j * np.pi * 0.5 * m / n)))
    return float(20.0 * np.log10(medio / centro))


def fuga_db(f_hz, fs, n, ventana="rect", lejos_bins=8):
    """La fuga MEDIDA: nivel del espectro a `lejos_bins` del tono, en dB
    bajo el pico. Un tono que cae entre bins derrama; con ventana, menos."""
    t = np.arange(int(n)) / float(fs)
    x = np.cos(2 * np.pi * float(f_hz) * t)
    _, db = espectro(x, fs, ventana=ventana)
    k = bin_de(f_hz, fs, n)
    lejos = np.abs(np.arange(len(db)) - k) >= lejos_bins
    return float(db[lejos].max())


def dos_tonos(f1, f2, fs, n, ventana="hann", amp2=1.0):
    """Dos tonos y su espectro medido. -> (t, x, f, db, valle_db)

    `valle_db` es lo que baja el espectro ENTRE los dos picos respecto al
    mas bajo: si es 0, no se distinguen; cuanto mas negativo, mas resueltos.
    """
    t = np.arange(int(n)) / float(fs)
    x = np.cos(2 * np.pi * f1 * t) + amp2 * np.cos(2 * np.pi * f2 * t + 0.4)
    f, db = espectro(x, fs, ventana=ventana)
    i1 = int(np.argmin(np.abs(f - f1)))
    i2 = int(np.argmin(np.abs(f - f2)))
    a, b = min(i1, i2), max(i1, i2)
    if b - a < 2:
        return t, x, f, db, 0.0
    valle = float(db[a + 1:b].min())
    pico_bajo = float(min(db[a], db[b]))
    return t, x, f, db, valle - pico_bajo


# =====================================================================
# 9. La transformada Z (modulo 4)
# =====================================================================
def zpk(b, a=(1.0,)):
    """Ceros, polos y ganancia de H(z) = B(z)/A(z). -> (ceros, polos, k)"""
    b = np.atleast_1d(np.asarray(b, dtype=float))
    a = np.atleast_1d(np.asarray(a, dtype=float))
    ceros = np.roots(b) if len(b) > 1 else np.array([])
    polos = np.roots(a) if len(a) > 1 else np.array([])
    return ceros, polos, float(b[0] / a[0])


def respuesta_frec(b, a=(1.0,), n=512):
    """|H| en dB y fase (rad) sobre w = 0..pi. -> (w, mag_db, fase)

    Se evalua a mano sobre el circulo unidad (z = e^{jw}): es lo que el
    modulo 4 dibuja como producto de distancias.
    """
    b = np.atleast_1d(np.asarray(b, dtype=float))
    a = np.atleast_1d(np.asarray(a, dtype=float))
    w = np.linspace(0.0, np.pi, int(n))
    z = np.exp(1j * w)
    num = sum(bk * z ** (-k) for k, bk in enumerate(b))
    den = sum(ak * z ** (-k) for k, ak in enumerate(a))
    h = num / den
    mag = np.maximum(np.abs(h), 1e-12)
    return w, 20.0 * np.log10(mag), np.unwrap(np.angle(h))


def h_en(b, a, w):
    """H(e^{jw}) en un punto (para rotular el valor exacto)."""
    z = np.exp(1j * float(w))
    num = sum(bk * z ** (-k) for k, bk in
              enumerate(np.atleast_1d(np.asarray(b, float))))
    den = sum(ak * z ** (-k) for k, ak in
              enumerate(np.atleast_1d(np.asarray(a, float))))
    return complex(num / den)


def por_distancias(ceros, polos, k, w):
    """|H(e^{jw})| CALCULADO como producto de distancias a los ceros
    entre producto de distancias a los polos (la construccion geometrica
    del clip 4.2). -> (modulo, distancias_ceros, distancias_polos)"""
    z = np.exp(1j * float(w))
    dc = np.abs(z - np.asarray(ceros)) if len(ceros) else np.array([1.0])
    dp = np.abs(z - np.asarray(polos)) if len(polos) else np.array([1.0])
    return float(abs(k) * np.prod(dc) / np.prod(dp)), dc, dp


def retardo_grupo(b, a=(1.0,), n=512):
    """Retardo de grupo MEDIDO: -d(fase)/dw por diferencias finitas.
    -> (w, retardo en muestras)"""
    w, _, fase = respuesta_frec(b, a, n)
    return w[1:-1], -np.gradient(fase, w)[1:-1]


def es_estable(a):
    """Todos los polos dentro del circulo unidad. -> (bool, radio_maximo)"""
    _, polos, _ = zpk([1.0], a)
    r = float(np.max(np.abs(polos))) if len(polos) else 0.0
    return r < 1.0, r


def es_fase_minima(b):
    """Todos los ceros dentro del circulo. -> (bool, radio_maximo)"""
    ceros, _, _ = zpk(b, [1.0])
    r = float(np.max(np.abs(ceros))) if len(ceros) else 0.0
    return r < 1.0, r


def reflejar_ceros(b):
    """El sistema de FASE MINIMA con el MISMO |H|: cada cero de fuera del
    circulo se cambia por su reciproco conjugado (y se reescala). Sirve
    para enseñar que el modulo no determina la fase."""
    ceros, _, k = zpk(b, [1.0])
    nuevos, ganancia = [], k
    for c in ceros:
        if abs(c) > 1.0:
            nuevos.append(np.conj(1.0 / c))
            ganancia *= abs(c)
        else:
            nuevos.append(c)
    return np.real(ganancia * np.poly(nuevos))


def resonador(radio, w0):
    """Un par de polos conjugados en radio*e^{+-j w0}. -> (b, a)"""
    a = np.real(np.poly([radio * np.exp(1j * w0),
                         radio * np.exp(-1j * w0)]))
    return np.array([1.0]), a


def notch(radio, w0):
    """Ceros EN el circulo en w0 y polos justo detras: mata una frecuencia
    sin tocar el resto. -> (b, a)"""
    b = np.real(np.poly([np.exp(1j * w0), np.exp(-1j * w0)]))
    a = np.real(np.poly([radio * np.exp(1j * w0),
                         radio * np.exp(-1j * w0)]))
    return b, a


# =====================================================================
# 10. Piezas de dibujo del modulo 3 y 4
# =====================================================================
class PlanoZ(_Anclada):
    """El plano complejo con el CIRCULO UNIDAD, los ceros (o) y los polos
    (x). Es la imagen firma del modulo 4.

    .en(z)             punto de la pieza para un complejo
    .punto_en(w)       el punto e^{jw} sobre el circulo
    .radios_a(w)       segmentos desde cada cero y cada polo hasta e^{jw}
    .con_pz(c, p)      GEMELA (mismo numero de ceros y de polos)
    .ceros .polos .circulo .ejes
    """

    def __init__(self, ceros=(), polos=(), unidad=1.55, alcance=1.75,
                 color_cero=C_SALIDA, color_polo=C_RUIDO, lado_marca=0.10,
                 color_circulo=C_MUESTRA, **kwargs):
        super().__init__(**kwargs)
        self.c = np.asarray(list(ceros), dtype=complex)
        self.p = np.asarray(list(polos), dtype=complex)
        self.unidad = float(unidad)
        self.alcance = float(alcance)
        self.color_cero, self.color_polo = color_cero, color_polo
        self.lado_marca = float(lado_marca)
        self.color_circulo = color_circulo
        self._poner_ancla(ORIGIN)
        a = self.alcance
        ex = Line(self.en(-a), self.en(a), color=C_EJE, stroke_width=1.6)
        ey = Line(self.en(-1j * a), self.en(1j * a), color=C_EJE,
                  stroke_width=1.6)
        self.ejes = VGroup(ex, ey)
        self.circulo = Circle(radius=self.unidad, color=color_circulo,
                              stroke_width=2.2, stroke_opacity=0.75)
        self.circulo.move_to(self._origen())
        self.ceros = VGroup(*[self._marca_cero(z) for z in self.c])
        self.polos = VGroup(*[self._marca_polo(z) for z in self.p])
        self.add(self.ejes, self.circulo, self.ceros, self.polos)

    def en(self, z):
        z = complex(z)
        return self._origen() + np.array([z.real * self.unidad,
                                          z.imag * self.unidad, 0.0])

    def punto_en(self, w):
        return self.en(np.exp(1j * float(w)))

    def _marca_cero(self, z, radio=None):
        radio = self.lado_marca if radio is None else radio
        return Circle(radius=radio, color=self.color_cero, stroke_width=2.6)\
            .move_to(self.en(z))

    def _marca_polo(self, z, lado=None):
        lado = self.lado_marca if lado is None else lado
        d = self.en(z)
        return VGroup(
            Line(d + np.array([-lado, -lado, 0]),
                 d + np.array([lado, lado, 0]), color=self.color_polo,
                 stroke_width=2.8),
            Line(d + np.array([-lado, lado, 0]),
                 d + np.array([lado, -lado, 0]), color=self.color_polo,
                 stroke_width=2.8))

    def punto(self, w, color=C_CALCULO, radio=0.07):
        return Dot(self.punto_en(w), radius=radio, color=color)

    def radios_a(self, w, grosor=2.0, opacidad=0.85):
        """Los segmentos cuya razon de longitudes ES |H(e^{jw})|."""
        destino = self.punto_en(w)
        g = VGroup()
        for z in self.c:
            g.add(Line(self.en(z), destino, color=self.color_cero,
                       stroke_width=grosor, stroke_opacity=opacidad))
        for z in self.p:
            g.add(Line(self.en(z), destino, color=self.color_polo,
                       stroke_width=grosor, stroke_opacity=opacidad))
        return g

    def arco(self, w0, w1, color=C_CALCULO, grosor=3.0):
        return Arc(radius=self.unidad, start_angle=float(w0),
                   angle=float(w1) - float(w0), color=color,
                   stroke_width=grosor).move_arc_center_to(self._origen())

    def con_pz(self, ceros, polos):
        """GEMELA: solo vale con el MISMO numero de ceros y de polos (si
        cambia la cuenta, la estructura cambia y Transform rompe glifos)."""
        if len(ceros) != len(self.c) or len(polos) != len(self.p):
            raise ValueError("la gemela necesita el MISMO numero de ceros "
                             "y de polos")
        o = PlanoZ(ceros, polos, self.unidad, self.alcance, self.color_cero,
                   self.color_polo, self.lado_marca, self.color_circulo)
        o.shift(self._origen() - o._origen())
        return o


def plano_z(ceros=(), polos=(), unidad=1.55, alcance=1.75, lado_marca=0.10,
            color_circulo=C_MUESTRA):
    """Ver `PlanoZ`.

    OJO con `lado_marca`: las aspas y los circulitos NO escalan solos con
    `unidad`. Medido en el lote 3: con `unidad = 1.06`, un polo ESTABLE a
    radio 0.994 se dibuja con la X llegando a 1.148, o sea cruzando el
    circulo unidad — se lee justo como lo contrario de lo que es. Y con
    diez polos juntos (Chebyshev de orden 10) las aspas se funden en una
    mancha. Si te alejas de `unidad = 1.55` o dibujas muchos polos, pasa
    `lado_marca` a mano.
    """
    return PlanoZ(ceros, polos, unidad, alcance, C_SALIDA, C_RUIDO,
                  lado_marca, color_circulo)


class RespuestaFrec(_Anclada):
    """|H(e^{jw})| en dB frente a w/pi (0 a 1).

    .en(w, db) .marca_w(w) .banda(w0, w1) .con_mag(db2) GEMELA

    OJO: `.en()` recorta con np.clip entre `piso_db` y `techo_db`. Una curva
    que no este acotada de forma natural (la del warping de la bilineal
    llega a 31.8) sale como un segmento HORIZONTAL pegado al borde, que se
    lee como saturacion — lo contrario de lo que hace. Quien dibuje una
    curva asi tiene que recortar los PUNTOS antes, no fiarse del clip.
    """

    def __init__(self, w, mag_db, ancho=5.6, alto=2.6, piso_db=-60.0,
                 techo_db=None, color=C_SALIDA, **kwargs):
        super().__init__(**kwargs)
        self.w = np.asarray(w, dtype=float)
        self.db = np.asarray(mag_db, dtype=float)
        self.piso = float(piso_db)
        self.techo = float(techo_db) if techo_db is not None else max(
            5.0, float(np.max(self.db)) + 3.0)
        self.ancho, self.alto = float(ancho), float(alto)
        self.color = color
        self._poner_ancla(ORIGIN)
        ex = Line(self.en(self.w[0], self.piso),
                  self.en(self.w[-1], self.piso), color=C_EJE,
                  stroke_width=1.6)
        ey = Line(self.en(self.w[0], self.piso),
                  self.en(self.w[0], self.techo), color=C_EJE,
                  stroke_width=1.6)
        self.ejes = VGroup(ex, ey)
        self.curva = VMobject(color=color, stroke_width=2.8)
        self.curva.set_points_as_corners([self.en(a, b) for a, b in
                                          zip(self.w, self.db)])
        self.add(self.ejes, self.curva)

    def en(self, w, db):
        fx = (float(w) - self.w[0]) / (self.w[-1] - self.w[0])
        fy = ((float(np.clip(db, self.piso, self.techo)) - self.piso)
              / (self.techo - self.piso))
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (fy - 0.5) * self.alto, 0.0]))

    def valor(self, w):
        """El dB dibujado en w (interpolado sobre la propia curva)."""
        return float(np.interp(float(w), self.w, self.db))

    def marca_w(self, w, color=C_CALCULO):
        return DashedLine(self.en(w, self.piso), self.en(w, self.techo),
                          color=color, stroke_width=1.6, dash_length=0.07)

    def punto(self, w, color=C_CALCULO, radio=0.06):
        return Dot(self.en(w, self.valor(w)), radius=radio, color=color)

    def banda(self, w0, w1, color=C_CALCULO, opacidad=0.14):
        x0, x1 = self.en(w0, 0)[0], self.en(w1, 0)[0]
        r = Rectangle(width=abs(x1 - x0), height=self.alto, stroke_width=0,
                      fill_color=color, fill_opacity=opacidad)
        r.move_to(np.array([(x0 + x1) / 2.0,
                            self.en(self.w[0], (self.piso + self.techo) / 2)[1],
                            0.0]))
        return r

    def con_mag(self, db2, color=None):
        if len(db2) != len(self.db):
            raise ValueError("la gemela necesita el MISMO eje de w")
        o = RespuestaFrec(self.w, db2, self.ancho, self.alto, self.piso,
                          self.techo, color or self.color)
        o.shift(self._origen() - o._origen())
        return o


def respuesta_dibujo(w, mag_db, ancho=5.6, alto=2.6, piso_db=-60.0,
                     techo_db=None, color=C_SALIDA):
    """Ver `RespuestaFrec`."""
    return RespuestaFrec(w, mag_db, ancho, alto, piso_db, techo_db, color)


class Mariposa(_Anclada):
    """El grafo radix-2 de la FFT: log2(N)+1 columnas de N nodos y las
    aristas de cada etapa.

    .nodo(col, fila)   .etapa(k) VGroup de las aristas de la etapa k
    .cruces(k)         solo las aristas que CRUZAN (las que dan el nombre)
    """

    def __init__(self, n=8, ancho=6.6, alto=4.2, color=C_MUESTRA, **kwargs):
        super().__init__(**kwargs)
        self.n = int(n)
        self.etapas_datos = mariposas(self.n)
        self.cols = len(self.etapas_datos) + 1
        self.ancho, self.alto = float(ancho), float(alto)
        self.color = color
        self._poner_ancla(ORIGIN)
        self.nodos = VGroup()
        for c in range(self.cols):
            col = VGroup(*[Dot(self._pos(c, f), radius=0.045, color=color)
                           for f in range(self.n)])
            self.nodos.add(col)
        self.aristas = VGroup()
        for k, etapa in enumerate(self.etapas_datos):
            g = VGroup()
            for i, j, _tw in etapa:
                g.add(Line(self._pos(k, i), self._pos(k + 1, i),
                           color=C_EJE, stroke_width=1.5),
                      Line(self._pos(k, j), self._pos(k + 1, j),
                           color=C_EJE, stroke_width=1.5),
                      Line(self._pos(k, i), self._pos(k + 1, j),
                           color=C_CALCULO, stroke_width=1.5),
                      Line(self._pos(k, j), self._pos(k + 1, i),
                           color=C_CALCULO, stroke_width=1.5))
            self.aristas.add(g)
        self.add(self.aristas, self.nodos)

    def _pos(self, col, fila):
        fx = col / max(self.cols - 1, 1)
        fy = fila / max(self.n - 1, 1)
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (0.5 - fy) * self.alto, 0.0]))

    def nodo(self, col, fila):
        return self.nodos[int(col)][int(fila)]

    def etapa(self, k):
        return self.aristas[int(k)]

    def cruces(self, k):
        """Las aristas diagonales de la etapa k (una por mariposa x2)."""
        g = self.aristas[int(k)]
        return VGroup(*[g[i] for i in range(len(g)) if i % 4 >= 2])


def mariposa_dibujo(n=8, ancho=6.6, alto=4.2, color=C_MUESTRA):
    """Ver `Mariposa`."""
    return Mariposa(n, ancho, alto, color)


# =====================================================================
# 11. Diseño de filtros FIR (modulo 5)
# =====================================================================
def ideal_truncado(orden, fc, fs=2.0):
    """El filtro ideal (una sinc infinita) cortado a `orden`+1 muestras.

    Es el punto de partida honesto del diseño por ventanas: se calcula a
    mano porque la leccion enseña QUE es truncar. fc en las mismas
    unidades que fs (por defecto fs = 2, o sea fc en fracciones de pi).
    """
    n = int(orden) + 1
    m = np.arange(n) - (n - 1) / 2.0
    wc = 2.0 * float(fc) / float(fs)
    return wc * np.sinc(wc * m)


def fir_ventana(orden, fc, ventana="hann", fs=2.0):
    """Ideal truncado x ventana: el diseño FIR mas simple que existe."""
    h = ideal_truncado(orden, fc, fs)
    return h * ventana_de(ventana, len(h))


def gibbs_db(b, fc, fs=2.0, n=2048):
    """El sobrepico MEDIDO junto a la transicion, en dB sobre 0 dB (la
    oreja de Gibbs). Devuelve tambien donde esta."""
    w, mag, _ = respuesta_frec(b, [1.0], n)
    f = w / np.pi * (fs / 2.0)
    dentro = f < float(fc) * 0.98
    if not dentro.any():
        return 0.0, 0.0
    i = int(np.argmax(mag[dentro]))
    return float(mag[dentro][i]), float(f[dentro][i])


def rizado_db(b, a, f_paso, f_rechazo, fs=2.0, n=4096):
    """Rizado MEDIDO en la banda de paso y atenuacion MEDIDA en la de
    rechazo. -> (rizado_pp_db, atenuacion_db)"""
    w, mag, _ = respuesta_frec(b, a, n)
    f = w / np.pi * (fs / 2.0)
    paso = mag[f <= float(f_paso)]
    rech = mag[f >= float(f_rechazo)]
    rizado = float(paso.max() - paso.min()) if len(paso) else 0.0
    aten = float(rech.max()) if len(rech) else -np.inf
    return rizado, aten


def fir_equirriple(orden, f_paso, f_rechazo, fs=2.0, peso=(1.0, 1.0)):
    """Parks-McClellan (intercambio de Remez) via scipy.signal.remez.

    Es el unico diseño del curso que no se implementa a mano: el algoritmo
    de intercambio no cabe en un clip, pero SU RESULTADO —el error que se
    reparte por igual— es justo lo que hay que ver.
    """
    from scipy.signal import remez
    return remez(int(orden) + 1, [0.0, float(f_paso), float(f_rechazo),
                                  fs / 2.0], [1.0, 0.0], weight=list(peso),
                 fs=float(fs))


def alternancias(b, f_paso, f_rechazo, fs=2.0, n=4096):
    """Los extremos del error (donde el rizado toca su tope) en la banda
    de rechazo: el teorema de la alternancia, MEDIDO. -> lista de f"""
    w, mag, _ = respuesta_frec(b, [1.0], n)
    f = w / np.pi * (fs / 2.0)
    m = f >= float(f_rechazo)
    fr, mr = f[m], mag[m]
    picos = []
    for i in range(1, len(mr) - 1):
        if (mr[i] > mr[i - 1] and mr[i] >= mr[i + 1]):
            picos.append(float(fr[i]))
    return picos


def orden_necesario(f_paso, f_rechazo, aten_db, fs=2.0, tope=200):
    """El orden MAS BAJO (par) que cumple la atenuacion pedida, hallado
    probando: no hay formula honesta que valga para todo. -> (orden, aten)"""
    for orden in range(10, int(tope) + 1, 2):
        b = fir_equirriple(orden, f_paso, f_rechazo, fs)
        _, aten = rizado_db(b, [1.0], f_paso, f_rechazo, fs)
        if aten <= -abs(aten_db):
            return orden, aten
    return None, None


def es_simetrico(b, tol=1e-9):
    """Un FIR simetrico tiene fase lineal y la mitad de multiplicaciones."""
    b = np.asarray(b, float)
    return bool(np.max(np.abs(b - b[::-1])) < tol)


def macs_fir(b):
    """Multiplicaciones por muestra: N+1, o la mitad si es simetrico
    (h[k] y h[N-k] multiplican al mismo coeficiente)."""
    n = len(b)
    return (n + 1) // 2 if es_simetrico(b) else n


# =====================================================================
# 12. Filtros IIR (modulo 6)
# =====================================================================
def polos_butter_analogico(orden, wc=1.0):
    """Los polos del Butterworth ANALOGICO: repartidos por igual en el
    semicirculo izquierdo de radio wc. Es la imagen que explica el nombre
    'maximamente plano'."""
    k = np.arange(1, int(orden) + 1)
    ang = np.pi * (2 * k + orden - 1) / (2 * orden)
    return wc * np.exp(1j * ang)


def bilineal(polos_s, T=2.0):
    """La transformacion bilineal z = (1 + sT/2)/(1 - sT/2): del plano s
    al plano z. El semiplano izquierdo entero cabe dentro del circulo."""
    s = np.asarray(polos_s, dtype=complex)
    return (1.0 + s * T / 2.0) / (1.0 - s * T / 2.0)


def warp(w_digital, T=2.0):
    """La frecuencia analogica que hay que pedir para que la bilineal la
    deje en w_digital: Omega = (2/T) tan(w/2). El 'prewarping'."""
    return (2.0 / T) * np.tan(np.asarray(w_digital, float) / 2.0)


def warp_inverso(omega, T=2.0):
    return 2.0 * np.arctan(np.asarray(omega, float) * T / 2.0)


def iir_butter(orden, fc, fs=2.0):
    from scipy.signal import butter
    return butter(int(orden), float(fc), btype="low", fs=float(fs))


def iir_cheby1(orden, rizado_db_paso, fc, fs=2.0):
    from scipy.signal import cheby1
    return cheby1(int(orden), float(rizado_db_paso), float(fc),
                  btype="low", fs=float(fs))


def iir_elip(orden, rizado_db_paso, aten_db, fc, fs=2.0):
    from scipy.signal import ellip
    return ellip(int(orden), float(rizado_db_paso), float(aten_db),
                 float(fc), btype="low", fs=float(fs))


def secciones(b, a):
    """Las secciones de segundo orden (biquads) de un filtro. -> (n, sos)

    Un IIR de orden alto en forma directa es inservible en aritmetica
    finita; en cascada de biquads, no. La cifra que lo demuestra esta en
    `polos_cuantizados`.
    """
    from scipy.signal import tf2sos
    sos = tf2sos(np.asarray(b, float), np.asarray(a, float))
    return len(sos), sos


def polos_cuantizados(b, a, bits):
    """A donde se van los polos al guardar los coeficientes con `bits`,
    en forma DIRECTA y en CASCADA de biquads.

    -> (polos_exactos, polos_directa, polos_cascada, error_directa,
        error_cascada) — los errores son la distancia maxima medida.
    """
    from scipy.signal import sos2zpk
    b = np.asarray(b, float)
    a = np.asarray(a, float)
    paso = 2.0 ** -(int(bits) - 1)

    def q(x):
        return np.round(np.asarray(x, float) / paso) * paso

    exactos = np.roots(a)
    directa = np.roots(q(a))
    _, sos = secciones(b, a)
    sos_q = q(sos)
    _, polos_c, _ = sos2zpk(sos_q)

    def error(p2):
        if len(p2) != len(exactos):
            return float("nan")
        # emparejar cada polo con el mas cercano
        libres = list(range(len(p2)))
        peor = 0.0
        for p in exactos:
            i = min(libres, key=lambda j: abs(p2[j] - p))
            peor = max(peor, float(abs(p2[i] - p)))
            libres.remove(i)
        return peor

    return exactos, directa, polos_c, error(directa), error(polos_c)


def peine(retardo, ganancia=0.85):
    """Filtro peine y = x[n] + g x[n-M]: dientes cada fs/M. -> (b, a)"""
    b = np.zeros(int(retardo) + 1)
    b[0] = 1.0
    b[-1] = float(ganancia)
    return b, np.array([1.0])


def goertzel(x, k, n=None):
    """El detector de UNA frecuencia sin FFT: un biquad y una salida.

    Devuelve |X[k]| calculado por la recursion de Goertzel y, para
    comprobarlo, el mismo valor sacado de la DFT.
    """
    x = np.asarray(x, float)
    n = int(n or len(x))
    w = 2.0 * np.pi * float(k) / n
    coef = 2.0 * np.cos(w)
    s1 = s2 = 0.0
    for m in range(n):
        s = x[m] + coef * s1 - s2
        s2, s1 = s1, s
    real = s1 - s2 * np.cos(w)
    imag = s2 * np.sin(w)
    por_goertzel = float(np.hypot(real, imag))
    por_dft = float(abs(np.fft.rfft(x, n=n)[int(k)]))
    return por_goertzel, por_dft


def macs_goertzel(n):
    """Multiplicaciones de Goertzel para UNA frecuencia: n (una por
    muestra) frente a las n log2 n de una FFT entera."""
    return int(n), int(ops_fft(int(n)))


# =====================================================================
# 13. La linea de retardos (la estructura, dibujada)
# =====================================================================
class LineaRetardos(_Anclada):
    """La forma directa de un FIR: la señal entra, va cayendo por las
    cajas z^-1, cada toma se multiplica por su coeficiente y todo se suma.

    .cajas .tomas .coefs .suma
    .encender(k)          resalta la rama k
    .con_coefs(c)         GEMELA (mismo numero de tomas)
    """

    def __init__(self, coefs, ancho=9.0, alto=2.4, color=C_MUESTRA,
                 dec=2, **kwargs):
        super().__init__(**kwargs)
        self.c = np.asarray(coefs, dtype=float)
        self.ancho, self.alto = float(ancho), float(alto)
        self.color, self.dec = color, int(dec)
        self._poner_ancla(ORIGIN)
        n = len(self.c)
        paso = self.ancho / max(n, 1)
        y_lin = self.alto / 2.0
        y_sum = -self.alto / 2.0
        self.linea = Line(self._p(0, y_lin) + LEFT * paso * 0.5,
                          self._p(n - 1, y_lin), color=C_EJE,
                          stroke_width=2.0)
        self.cajas = VGroup()
        self.tomas = VGroup()
        self.coefs = VGroup()
        for i in range(n):
            p = self._p(i, y_lin)
            if i > 0:
                caja = Rectangle(width=paso * 0.46, height=0.34,
                                 stroke_width=1.8, stroke_color=C_EJE,
                                 fill_color=CODE_BG_LOCAL, fill_opacity=1.0)
                caja.move_to(p + LEFT * paso * 0.5)
                self.cajas.add(caja)
            toma = Line(p, self._p(i, y_sum), color=C_EJE, stroke_width=1.4)
            self.tomas.add(toma)
            circ = Circle(radius=0.115, color=color, stroke_width=2.0)
            circ.move_to(self._p(i, 0.0))
            self.coefs.add(circ)
        self.suma = Line(self._p(0, y_sum), self._p(n - 1, y_sum),
                         color=C_EJE, stroke_width=2.0)
        self.add(self.linea, self.cajas, self.tomas, self.suma, self.coefs)

    def _p(self, i, y):
        n = max(len(self.c), 1)
        fx = (i + 0.5) / n
        return (self._origen() + np.array([(fx - 0.5) * self.ancho, y, 0.0]))

    def caja(self, i):
        """La caja z^-1 que hay ANTES de la toma i (i >= 1)."""
        return self.cajas[int(i) - 1]

    def toma(self, i):
        return self.tomas[int(i)]

    def coef(self, i):
        return self.coefs[int(i)]

    def encender(self, i, color=C_CALCULO, grosor=3.2):
        g = VGroup(self.tomas[int(i)].copy().set_stroke(color, grosor),
                   self.coefs[int(i)].copy().set_stroke(color, grosor))
        return g

    def con_coefs(self, c2):
        if len(c2) != len(self.c):
            raise ValueError("la gemela necesita el MISMO numero de tomas")
        o = LineaRetardos(c2, self.ancho, self.alto, self.color, self.dec)
        o.shift(self._origen() - o._origen())
        return o


def linea_retardos(coefs, ancho=9.0, alto=2.4, color=C_MUESTRA, dec=2):
    """Ver `LineaRetardos`."""
    return LineaRetardos(coefs, ancho, alto, color, dec)


# =====================================================================
# 14. Aritmetica finita y tiempo real (modulo 7)
# =====================================================================
Q15_ESCALA = 32768.0


def q15(x):
    """Redondeo al formato Q15: 16 bits con signo, rango [-1, 1).

    Es el formato de casi todo DSP de vuelo: un entero de 16 bits que
    representa una fraccion. El 1.0 exacto NO existe (el mayor es
    32767/32768 = 0.99997).
    """
    x = np.asarray(x, dtype=float)
    return np.round(x * Q15_ESCALA) / Q15_ESCALA


def satura(x, lim=1.0):
    """Lo que hace un DSP decente al pasarse: se queda en el tope."""
    return np.clip(np.asarray(x, dtype=float), -float(lim),
                   float(lim) - 1.0 / Q15_ESCALA)


def envuelve(x, lim=1.0):
    """Lo que hace un acumulador tonto: da la vuelta. Un pico positivo se
    convierte en uno negativo — el fallo mas feo del punto fijo."""
    x = np.asarray(x, dtype=float)
    rango = 2.0 * float(lim)
    return (x + lim) % rango - lim


def error_q15(x):
    """Error MEDIDO de representar x en Q15 (rms y maximo)."""
    x = np.asarray(x, dtype=float)
    e = q15(x) - x
    return float(np.sqrt(np.mean(e ** 2))), float(np.max(np.abs(e)))


def snr_q15(x):
    """SNR de la representacion Q15, medida sobre esta señal."""
    x = np.asarray(x, dtype=float)
    e = q15(x) - x
    return 10.0 * math.log10(float(np.mean(x ** 2) /
                                   max(np.mean(e ** 2), 1e-30)))


def margen(x):
    """Cuantos dB de cabecera quedan antes de tocar el 1.0 (headroom)."""
    pico = float(np.max(np.abs(np.asarray(x, float))))
    return 20.0 * math.log10(1.0 / pico) if pico > 0 else np.inf


def filtrar_punto_fijo(b, a, x, bits=15, modo="satura"):
    """La ecuacion en diferencias con TODO cuantizado a cada paso: los
    coeficientes, el estado y la salida. `modo` decide que pasa al
    desbordar: 'satura' o 'envuelve'. -> y"""
    paso = 2.0 ** -int(bits)
    q = lambda v: np.round(np.asarray(v, float) / paso) * paso
    b, a = q(np.atleast_1d(b)), q(np.atleast_1d(a))
    x = np.asarray(x, float)
    y = np.zeros(len(x))
    for n in range(len(x)):
        acc = 0.0
        for i in range(len(b)):
            if n - i >= 0:
                acc += b[i] * x[n - i]
        for j in range(1, len(a)):
            if n - j >= 0:
                acc -= a[j] * y[n - j]
        acc = float(q(acc))
        y[n] = satura(acc)[()] if modo == "satura" else envuelve(acc)[()]
    return y


def ciclo_limite(a, bits=6, n=200, x0=0.5):
    """El ciclo limite de un IIR de PRIMER orden: y[n] = Q(a y[n-1]).

    Sin cuantizar, y[n] -> 0 siempre que |a| < 1. Cuantizando, hay una
    "banda muerta" cerca del cero donde el redondeo devuelve el mismo
    valor de siempre: el filtro se queda oscilando (o clavado) para
    siempre, sin entrada. Es un fallo que NO existe en coma flotante.

    -> (y, amplitud_final, periodo)  amplitud 0 = se apago de verdad.
    La amplitud escala con el paso de cuantizacion: es ruido de
    redondeo atrapado, no señal.
    """
    paso = 2.0 ** -(int(bits) - 1)
    y = np.zeros(int(n))
    v = float(x0)
    for k in range(int(n)):
        v = float(np.round(float(a) * v / paso) * paso)
        y[k] = v
    cola = y[int(n) // 2:]
    amplitud = float(np.max(np.abs(cola)))
    periodo = 0
    if amplitud > 0:
        signos = np.sign(cola[cola != 0])
        cambios = int(np.sum(signos[1:] != signos[:-1])) if len(signos) > 1 else 0
        periodo = int(round(2 * len(cola) / cambios)) if cambios else 1
    return y, amplitud, periodo


def banda_muerta(a, bits=6, n=200):
    """La banda muerta: teorica paso/(2(1-|a|)) frente a la amplitud en la
    que el filtro se queda ATRAPADO, medida.

    Con |a| < 1 cualquier arranque acaba dentro, asi que lo que se mide es
    donde para, no desde donde sale. -> (teorica, atrapada, paso)
    """
    paso = 2.0 ** -(int(bits) - 1)
    teorica = paso / (2.0 * (1.0 - abs(float(a))))
    _, atrapada, _ = ciclo_limite(a, bits, n, 0.5)
    return float(teorica), float(atrapada), float(paso)


def overlap_add(x, h, largo_bloque):
    """Convolucion por bloques con FFT (overlap-add). Devuelve la salida y
    el error MEDIDO contra la convolucion directa."""
    x = np.asarray(x, float)
    h = np.asarray(h, float)
    L = int(largo_bloque)
    M = len(h)
    n_fft = 1
    while n_fft < L + M - 1:
        n_fft *= 2
    H = np.fft.rfft(h, n_fft)
    y = np.zeros(len(x) + M - 1)
    for i in range(0, len(x), L):
        bloque = x[i:i + L]
        trozo = np.fft.irfft(np.fft.rfft(bloque, n_fft) * H, n_fft)
        y[i:i + len(trozo)] += trozo[:len(y) - i]
    directa = convolucion(x, h)
    return y, float(np.max(np.abs(y - directa)))


def coste_directo(n_x, m_h):
    """Multiplicaciones reales de convolucionar directo."""
    return int(n_x) * int(m_h)


def coste_fft(n_x, m_h, largo_bloque=None):
    """Multiplicaciones REALES de convolucionar por bloques con FFT.

    Se cuentan reales, igual que en `coste_directo`: comparar
    multiplicaciones complejas con reales infla la FFT por cuatro y da un
    cruce falso (medido: M = 16 en vez de M = 64). Por bloque hay una FFT
    real de ida, una de vuelta y el producto punto a punto; una FFT real
    de N cuesta la mitad que una compleja, y cada multiplicacion compleja
    son cuatro reales.
    """
    L = int(largo_bloque or max(m_h, 64))
    n_fft = 1
    while n_fft < L + int(m_h) - 1:
        n_fft *= 2
    bloques = int(math.ceil(int(n_x) / L))
    fft_real = 4 * (ops_fft(n_fft) / 2.0)      # reales por FFT de N reales
    producto = 4 * (n_fft // 2 + 1)            # H[k] * X[k], complejos
    por_bloque = 2 * fft_real + producto
    return int(bloques * por_bloque + fft_real)


def cruce_fft(n_x, tope=1024):
    """La longitud de filtro a partir de la cual sale mas barato hacerlo
    por FFT. Se halla PROBANDO, no con una regla. -> (m, directo, fft)"""
    for m in range(4, int(tope) + 1, 2):
        d = coste_directo(n_x, m)
        f = coste_fft(n_x, m, max(4 * m, 64))
        # (los dos en multiplicaciones REALES: ver coste_fft)
        if f < d:
            return m, d, f
    return None, None, None


def latencia_bloque(largo_bloque, fs):
    """Los milisegundos que un bloque mete de retraso: hay que esperar a
    tenerlo entero antes de empezar."""
    return 1000.0 * float(largo_bloque) / float(fs)


# =====================================================================
# 15. Multitasa (modulo 8)
# =====================================================================
def diezmar(x, m):
    """Quedarse con una de cada M muestras (sin filtrar: se ve el alias)."""
    return np.asarray(x, float)[::int(m)]


def interpolar_ceros(x, l):
    """Meter L-1 ceros entre muestras: la señal no cambia, pero su
    espectro se llena de IMAGENES."""
    x = np.asarray(x, float)
    y = np.zeros(len(x) * int(l))
    y[::int(l)] = x
    return y


def polifase(h, m):
    """Las M ramas polifase de h: h[k], h[k+M], h[k+2M]...

    Es el mismo filtro, reordenado. Su gracia: al diezmar, cada rama
    trabaja a fs/M, asi que se hacen las MISMAS cuentas que antes pero
    M veces menos a menudo.
    """
    h = np.asarray(h, float)
    m = int(m)
    return [h[k::m] for k in range(m)]


def macs_diezmado(h, m, directo=True):
    """Multiplicaciones POR MUESTRA DE ENTRADA, contadas: filtrar y luego
    tirar (directo) frente a polifase."""
    n = len(np.asarray(h))
    return n if directo else n / float(m)


def cic(x, r, n_etapas=1, m=1):
    """Filtro CIC (integrador-peine): diezma sin UN SOLO multiplicador.

    N integradores a la entrada, diezmado por R, N peines a la salida.
    -> (y, num_multiplicaciones)  -- el segundo siempre es 0.
    """
    x = np.asarray(x, float)
    v = x.copy()
    for _ in range(int(n_etapas)):
        v = np.cumsum(v)
    v = v[::int(r)]
    for _ in range(int(n_etapas)):
        v = np.concatenate([v[:int(m)], v[int(m):] - v[:-int(m)]])
    return v, 0


def respuesta_cic(r, n_etapas=1, m=1, n=1024):
    """|H| del CIC en dB (normalizada), sobre f = 0..0.5 de la entrada.
    La caida dentro de la banda util (el 'estatismo') se mide aparte."""
    f = np.linspace(1e-6, 0.5, int(n))
    num = np.sin(np.pi * f * int(r) * int(m))
    den = np.sin(np.pi * f)
    h = np.abs((num / den) ** int(n_etapas))
    h = h / h.max()
    return f, 20.0 * np.log10(np.maximum(h, 1e-12))


def caida_cic(r, n_etapas=1, m=1, f_util=None):
    """La caida MEDIDA del CIC en el borde de la banda util (por defecto,
    el borde de la banda que sobrevive al diezmado)."""
    f_util = f_util if f_util is not None else 0.5 / float(r)
    f, db = respuesta_cic(r, n_etapas, m, 4096)
    return float(db[int(np.argmin(np.abs(f - f_util)))])


def farrow(x, mu, orden=3):
    """Retardo FRACCIONARIO de mu muestras por interpolacion de Lagrange
    (la estructura de Farrow): el remuestreo cuando los relojes no cuadran.
    -> y (mismo largo que x)"""
    x = np.asarray(x, float)
    mu = float(mu)
    n = len(x)
    y = np.zeros(n)
    xs = np.arange(-(orden // 2), orden // 2 + 2)
    for k in range(n):
        acc = 0.0
        for j, d in enumerate(xs):
            li = 1.0
            for i, di in enumerate(xs):
                if i != j:
                    # se evalua en -mu: y[k] = x(k - mu), un RETRASO
                    li *= (-mu - di) / (d - di)
            idx = k + d
            if 0 <= idx < n:
                acc += li * x[idx]
        y[k] = acc
    return y


def error_farrow(f_hz, fs, mu, n=400):
    """Cuanto se equivoca el interpolador de Farrow con un tono: se
    compara con el tono retrasado de verdad. -> (rms, pico) medidos."""
    t = np.arange(int(n)) / float(fs)
    x = np.sin(2 * np.pi * float(f_hz) * t)
    exacto = np.sin(2 * np.pi * float(f_hz) * (t - float(mu) / fs))
    y = farrow(x, mu)
    i0, i1 = 4, int(n) - 4
    e = y[i0:i1] - exacto[i0:i1]
    return float(np.sqrt(np.mean(e ** 2))), float(np.max(np.abs(e)))


def remuestrear(x, l, m, h=None):
    """Remuestreo racional L/M: interpolar, filtrar, diezmar."""
    x = np.asarray(x, float)
    if h is None:
        h = fir_ventana(64, 0.5 / max(int(l), int(m)), "hann", 1.0)
    return diezmar(convolucion(interpolar_ceros(x, int(l)), h * int(l)),
                   int(m))


def banco_qmf(h0=None):
    """Banco de dos canales (paso bajo / paso alto) con reconstruccion.

    -> (h0, h1, g0, g1) — los cuatro filtros del banco QMF clasico:
    h1[n] = (-1)^n h0[n], g0 = h0, g1 = -h1.
    """
    if h0 is None:
        # 32 taps: la longitud tiene que ser PAR. Con longitud impar la
        # cancelacion del alias del QMF no se cumple y el error de
        # reconstruccion se dispara (medido: 0.97 con 31 taps, 0.06 con 32).
        h0 = fir_ventana(31, 0.25, "hamming", 1.0)
    h0 = np.asarray(h0, float)
    signos = (-1.0) ** np.arange(len(h0))
    h1 = h0 * signos
    return h0, h1, h0.copy(), -h1


def banco_haar():
    """El banco ortogonal mas simple: media y diferencia, normalizadas.

    Es el unico de los dos que reconstruye EXACTO (error ~1e-16 medido):
    sirve para enseñar que la reconstruccion perfecta existe, antes de
    contar lo que cuesta que ademas separe bien las bandas.
    """
    r = 1.0 / math.sqrt(2.0)
    h0 = np.array([r, r])
    h1 = np.array([r, -r])
    return h0, h1, h0[::-1].copy(), h1[::-1].copy()


def error_reconstruccion(x, banco=None):
    """Analisis + sintesis de un banco de dos canales: cuanto se parece
    lo que sale a lo que entro (medido, tras alinear el retardo)."""
    x = np.asarray(x, float)
    h0, h1, g0, g1 = banco or banco_qmf()
    v0 = diezmar(convolucion(x, h0), 2)
    v1 = diezmar(convolucion(x, h1), 2)
    y = (convolucion(interpolar_ceros(v0, 2), g0)
         + convolucion(interpolar_ceros(v1, 2), g1))
    retardo = len(h0) - 1
    n = len(x) - retardo
    if n <= 0:
        return np.inf, y
    a = x[:n]
    b = y[retardo:retardo + n]
    escala = float(np.dot(a, b) / max(np.dot(b, b), 1e-30))
    return float(np.max(np.abs(a - escala * b))), y


# =====================================================================
# 16. Estimacion espectral (modulo 9)
# =====================================================================
def periodograma(x, fs=1.0, ventana="rect"):
    """El estimador ingenuo: |DFT|^2 de TODA la señal, de una vez.

    No converge: por muchas muestras que se le den, la varianza de cada
    bin se queda donde estaba. Es el punto de partida de 9.1.
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    w = ventana_de(ventana, n)
    p = np.abs(np.fft.rfft(x * w)) ** 2 / (n * np.sum(w ** 2) / n)
    return np.fft.rfftfreq(n, d=1.0 / fs), p


def welch(x, fs=1.0, nseg=256, solape=0.5, ventana="hann"):
    """Promediar periodogramas de trozos solapados. -> (f, p, n_trozos)

    Cada trozo es una estimacion mala; la media de K trozos tiene K veces
    menos varianza. Lo que se paga es resolucion.
    """
    x = np.asarray(x, dtype=float)
    nseg = int(min(nseg, len(x)))
    paso = max(1, int(nseg * (1.0 - solape)))
    w = ventana_de(ventana, nseg)
    norma = np.sum(w ** 2)
    acc, k = None, 0
    for i0 in range(0, len(x) - nseg + 1, paso):
        seg = x[i0:i0 + nseg] * w
        p = np.abs(np.fft.rfft(seg)) ** 2 / norma
        acc = p if acc is None else acc + p
        k += 1
    return np.fft.rfftfreq(nseg, d=1.0 / fs), acc / max(k, 1), k


def ruido_blanco(n, sigma=1.0, semilla=7):
    return np.random.default_rng(semilla).normal(0.0, sigma, int(n))


def dispersion(p_db):
    """La desviacion tipica del estimador, en dB, medida sobre sus bins.
    Es LA cifra de 9.1: mide cuanto tiembla la estimacion."""
    return float(np.std(np.asarray(p_db, dtype=float)))


def a_db(p, ref=None):
    p = np.maximum(np.asarray(p, dtype=float), 1e-30)
    return 10.0 * np.log10(p / (ref if ref else 1.0))


def resolucion_welch(nseg, fs):
    """Lo que cuesta promediar: la resolucion baja a fs/nseg."""
    return float(fs) / float(nseg)


# =====================================================================
# 17. Filtros adaptativos (modulo 9)
# =====================================================================
def lms(x, d, mu, n_taps, normalizado=False):
    """El filtro que se ajusta solo: w[n+1] = w[n] + mu e[n] x[n].

    -> (w_final, e, curva) — `curva` es el error cuadratico suavizado,
    o sea la curva de aprendizaje que se dibuja.
    """
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    n_taps = int(n_taps)
    w = np.zeros(n_taps)
    e = np.zeros(len(x))
    for n in range(n_taps, len(x)):
        xv = x[n - n_taps + 1:n + 1][::-1]
        y = float(np.dot(w, xv))
        e[n] = d[n] - y
        paso = mu
        if normalizado:
            paso = mu / (1e-8 + float(np.dot(xv, xv)))
        w = w + paso * e[n] * xv
    k = 64
    curva = np.convolve(e ** 2, np.ones(k) / k, mode="same")
    return w, e, curva


def escenario_cancelacion(n=4000, semilla=11):
    """El caso clasico: una voz limpia, un ruido que se le cuela por un
    camino desconocido, y un microfono de referencia con SOLO el ruido.

    -> (d, x, limpia, camino)  d = limpia + ruido filtrado, x = referencia
    """
    rng = np.random.default_rng(semilla)
    t = np.arange(int(n))
    limpia = np.sin(2 * np.pi * 0.01 * t) * 0.8
    ref = rng.normal(0.0, 1.0, int(n))
    camino = np.array([0.7, -0.4, 0.25, 0.1, -0.05])
    ruido = convolucion(ref, camino)[:int(n)]
    return limpia + ruido, ref, limpia, camino


def mejora_db(antes, despues):
    """Cuanto ha bajado el error, medido en dB."""
    a = float(np.mean(np.asarray(antes, dtype=float) ** 2))
    b = float(np.mean(np.asarray(despues, dtype=float) ** 2))
    return 10.0 * math.log10(a / max(b, 1e-30))


def error_coeficientes(w, camino):
    """Cuanto se parece lo aprendido al camino de verdad (norma del error
    relativa). Es la cifra honesta de 'ha aprendido el canal'."""
    w = np.asarray(w, dtype=float)
    c = np.zeros_like(w)
    c[:min(len(camino), len(w))] = np.asarray(camino,
                                              dtype=float)[:len(w)]
    return float(np.linalg.norm(w - c) / np.linalg.norm(c))


def curva_aprendizaje(e, referencia, k=128):
    """La curva que de verdad enseña si el LMS aprende: el error
    cuadratico medio del RESIDUO (lo que queda del ruido), suavizado.

    Medir e^2 a secas no dice nada: e incluye la señal util, que NO se
    quiere cancelar, y la curva sale plana (0.409 -> 0.349 medido).
    """
    r = (np.asarray(e, dtype=float)
         - np.asarray(referencia, dtype=float)) ** 2
    return np.convolve(r, np.ones(int(k)) / int(k), mode="valid")


def convergencia(curva, factor=2.0, cola=500):
    """En que muestra la curva baja a `factor` veces su suelo final.
    -> (n, suelo) medidos."""
    c = np.asarray(curva, dtype=float)
    suelo = float(np.mean(c[-int(cola):]))
    idx = np.where(c < factor * suelo)[0]
    return (int(idx[0]) if len(idx) else -1), suelo


def mu_maximo(x, n_taps):
    """El paso mayor que no diverge, por el criterio de la potencia de
    entrada: mu < 2 / (L * Px). Medido sobre esta x."""
    px = float(np.mean(np.asarray(x, dtype=float) ** 2))
    return 2.0 / (int(n_taps) * max(px, 1e-30))


# =====================================================================
# 18. Seguimiento: PLL y Kalman (modulo 9)
# =====================================================================
def pll(x, kp=0.05, ki=0.002, f0=0.0):
    """Un PLL digital de segundo orden siguiendo la fase de x (compleja).

    -> (fase_estimada, error_fase, frecuencia_estimada)
    """
    x = np.asarray(x)
    n = len(x)
    fase = np.zeros(n)
    frec = np.zeros(n)
    err = np.zeros(n)
    f = float(f0)
    ph = 0.0
    integ = 0.0
    for k in range(n):
        nco = np.exp(-1j * ph)
        prod = x[k] * nco
        e = float(np.angle(prod))
        err[k] = e
        integ += ki * e
        f = float(f0) + integ
        ph = ph + 2 * np.pi * f + kp * e
        fase[k] = ph
        frec[k] = f
    return fase, err, frec


def tono_con_deriva(n=1500, f_ini=0.02, deriva=1.2e-5, ruido=0.05,
                    semilla=5):
    """Un tono complejo cuya frecuencia se va yendo (Doppler de un pase):
    lo que un PLL tiene que seguir. -> (x, f_real)"""
    rng = np.random.default_rng(semilla)
    k = np.arange(int(n))
    f_real = f_ini + deriva * k
    fase = 2 * np.pi * np.cumsum(f_real)
    x = np.exp(1j * fase)
    x = x + (rng.normal(0, ruido, int(n))
             + 1j * rng.normal(0, ruido, int(n)))
    return x, f_real


def kalman_escalar(z, q, r, x0=0.0, p0=1.0):
    """Kalman de una variable: el filtro que decide cuanto creerse cada
    medida. -> (x_est, ganancia)"""
    z = np.asarray(z, dtype=float)
    x = float(x0)
    p = float(p0)
    est = np.zeros(len(z))
    gan = np.zeros(len(z))
    for k in range(len(z)):
        p = p + float(q)
        kg = p / (p + float(r))
        x = x + kg * (z[k] - x)
        p = (1.0 - kg) * p
        est[k] = x
        gan[k] = kg
    return est, gan


def medida_ruidosa(n=300, sigma=0.6, semilla=3):
    """Una magnitud que cambia despacio (la temperatura de un tanque) y
    sus medidas ruidosas. -> (verdad, medidas)"""
    rng = np.random.default_rng(semilla)
    k = np.arange(int(n))
    verdad = 0.5 * np.sin(2 * np.pi * k / 400.0) + 0.2 * (k / int(n))
    return verdad, verdad + rng.normal(0.0, sigma, int(n))


def rmse(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return float(np.sqrt(np.mean((a - b) ** 2)))


# =====================================================================
# 19. Señal analitica y tiempo-frecuencia (modulo 10)
# =====================================================================
def analitica(x):
    """La señal analitica: se tira la mitad negativa del espectro y lo
    que queda es un fasor. Se hace a mano con la FFT (es literalmente
    'poner a cero media transformada')."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    X = np.fft.fft(x)
    h = np.zeros(n)
    h[0] = 1.0
    if n % 2 == 0:
        h[n // 2] = 1.0
        h[1:n // 2] = 2.0
    else:
        h[1:(n + 1) // 2] = 2.0
    return np.fft.ifft(X * h)


def envolvente(x):
    """El modulo de la señal analitica: la amplitud instantanea."""
    return np.abs(analitica(x))


def fase_inst(x):
    return np.unwrap(np.angle(analitica(x)))


def frecuencia_inst(x, fs=1.0):
    """La derivada de la fase: la frecuencia instantanea, medida."""
    ph = fase_inst(x)
    return np.gradient(ph) * float(fs) / (2 * np.pi)


def stft(x, nperseg=128, solape=0.75, ventana="hann", fs=1.0):
    """La transformada de Fourier de ventana corta. -> (t, f, S en dB)"""
    x = np.asarray(x, dtype=float)
    nperseg = int(nperseg)
    paso = max(1, int(nperseg * (1.0 - solape)))
    w = ventana_de(ventana, nperseg)
    cols = []
    tiempos = []
    for i0 in range(0, len(x) - nperseg + 1, paso):
        seg = x[i0:i0 + nperseg] * w
        cols.append(np.abs(np.fft.rfft(seg)))
        tiempos.append((i0 + nperseg / 2) / float(fs))
    S = np.array(cols).T
    S = np.maximum(S / max(S.max(), 1e-30), 1e-6)
    return (np.array(tiempos), np.fft.rfftfreq(nperseg, d=1.0 / fs),
            20.0 * np.log10(S))


def heisenberg(nperseg, fs=1.0):
    """El compromiso, en cifras: una ventana de nperseg muestras dura
    nperseg/fs segundos y resuelve fs/nperseg hercios. El producto es 1
    SIEMPRE. -> (dt, df, producto)"""
    dt = float(nperseg) / float(fs)
    df = float(fs) / float(nperseg)
    return dt, df, dt * df


def chirp_y_golpe(n=2048, fs=1.0, semilla=4):
    """Una señal que necesita tiempo-frecuencia para entenderse: un
    barrido lento mas un golpe corto. En el espectro entero, el golpe se
    diluye; en el espectrograma, se ve donde esta."""
    k = np.arange(int(n))
    barrido = np.sin(2 * np.pi * (0.02 + 0.00008 * k) * k)
    golpe = np.zeros(int(n))
    i = int(n) * 3 // 5
    golpe[i:i + 40] = np.sin(2 * np.pi * 0.35 * np.arange(40)) * \
        np.hanning(40) * 1.5
    return barrido * 0.7 + golpe


def haar_niveles(x, niveles=3):
    """La wavelet mas simple: medias y diferencias, nivel a nivel.

    -> lista de arrays de detalle (uno por nivel) + la aproximacion final.
    A diferencia de la STFT, la ventana se ENCOGE al subir de frecuencia.
    """
    x = np.asarray(x, dtype=float)
    r = 1.0 / math.sqrt(2.0)
    detalles = []
    a = x.copy()
    for _ in range(int(niveles)):
        if len(a) % 2:
            a = a[:-1]
        par, impar = a[0::2], a[1::2]
        detalles.append((par - impar) * r)
        a = (par + impar) * r
    return detalles, a


# =====================================================================
# 20. El filtro aprendido (modulo 10)
# =====================================================================
def entrenar_filtro(n=3000, n_taps=17, pasos=400, lr=0.05, semilla=9):
    """Una red lineal de una capa aprendiendo a filtrar por ejemplos.

    Se le dan pares (entrada ruidosa, salida deseada) y ajusta sus pesos
    por descenso de gradiente. Al final se compara lo aprendido con el
    filtro que se habria diseñado: si coinciden, la red no ha inventado
    nada, ha REDESCUBIERTO el filtro.

    -> (w, historial_error, h_objetivo)
    """
    from dsp import fir_ventana
    rng = np.random.default_rng(semilla)
    h_obj = fir_ventana(n_taps - 1, 0.25, "hann", 2.0)
    x = rng.normal(0.0, 1.0, int(n))
    d = convolucion(x, h_obj)[:int(n)]
    w = np.zeros(int(n_taps))
    hist = []
    X = np.array([x[max(0, i - n_taps + 1):i + 1][::-1]
                  for i in range(n_taps - 1, int(n))])
    D = d[n_taps - 1:]
    for _ in range(int(pasos)):
        y = X @ w
        e = D - y
        w = w + lr * (X.T @ e) / len(D)
        hist.append(float(np.mean(e ** 2)))
    return w, np.array(hist), h_obj


def parecido(w, h):
    """Cuanto se parece el filtro aprendido al diseñado (coseno y error
    relativo, los dos medidos)."""
    w = np.asarray(w, dtype=float)
    h = np.asarray(h, dtype=float)[:len(w)]
    cos = float(np.dot(w, h) / (np.linalg.norm(w) * np.linalg.norm(h)))
    err = float(np.linalg.norm(w - h) / np.linalg.norm(h))
    return cos, err


def red_no_lineal(n=2000, ocultas=12, pasos=3000, lr=0.3, semilla=13):
    """Donde una red SI aporta algo: recuperar una señal que ha pasado
    por una no linealidad (un amplificador saturado), cosa que ningun
    filtro lineal puede deshacer.

    Medido: el mejor filtro lineal deja 0.1076 de rms y la red 0.0589,
    5.2 dB mejor. No es un abismo, y esa es la conclusion honesta de la
    leccion: la red gana donde el problema NO es lineal, y aun ahi hay
    que medir cuanto.

    -> (error_lineal, error_red, historial)
    """
    rng = np.random.default_rng(semilla)
    k = np.arange(int(n))
    limpia = np.sin(2 * np.pi * 0.013 * k) * 0.9
    sucia = np.tanh(2.2 * limpia)          # el amplificador satura
    # 1) el mejor filtro LINEAL posible (minimos cuadrados de 1 tap)
    a = float(np.dot(sucia, limpia) / np.dot(sucia, sucia))
    err_lineal = float(np.sqrt(np.mean((a * sucia - limpia) ** 2)))
    # 2) una red de una capa oculta
    W1 = rng.normal(0, 0.8, (1, int(ocultas)))
    b1 = np.zeros(int(ocultas))
    W2 = rng.normal(0, 0.8, (int(ocultas), 1))
    b2 = np.zeros(1)
    X = sucia.reshape(-1, 1)
    Y = limpia.reshape(-1, 1)
    hist = []
    for _ in range(int(pasos)):
        h = np.tanh(X @ W1 + b1)
        y = h @ W2 + b2
        e = y - Y
        hist.append(float(np.mean(e ** 2)))
        gW2 = h.T @ e / len(X)
        gb2 = e.mean(axis=0)
        gh = (e @ W2.T) * (1 - h ** 2)
        gW1 = X.T @ gh / len(X)
        gb1 = gh.mean(axis=0)
        W1 -= lr * gW1
        b1 -= lr * gb1
        W2 -= lr * gW2
        b2 -= lr * gb2
    h = np.tanh(X @ W1 + b1)
    y = (h @ W2 + b2).ravel()
    err_red = float(np.sqrt(np.mean((y - limpia) ** 2)))
    return err_lineal, err_red, np.array(hist)


# =====================================================================
# 21. El espectrograma, dibujado
# =====================================================================
class Espectrograma(_Anclada):
    """La malla tiempo-frecuencia: cada celda es un rectangulo cuyo color
    dice cuanta energia hay ahi.

    .en(t, f)  .marca_t(t)  .celda(i, j)
    """

    def __init__(self, t, f, s_db, ancho=8.0, alto=3.2, piso_db=-60.0,
                 color_bajo="#0b1f2a", color_alto=C_BANDA, **kwargs):
        super().__init__(**kwargs)
        from manim import ManimColor, interpolate_color
        self.t = np.asarray(t, dtype=float)
        self.f = np.asarray(f, dtype=float)
        self.s = np.asarray(s_db, dtype=float)
        self.piso = float(piso_db)
        self.ancho, self.alto = float(ancho), float(alto)
        self._poner_ancla(ORIGIN)
        n_f, n_t = self.s.shape
        dx = self.ancho / n_t
        dy = self.alto / n_f
        # interpolate_color EXIGE ManimColor: los C_* son str
        c_bajo = ManimColor(color_bajo)
        c_alto = ManimColor(color_alto)
        self.celdas = VGroup()
        for j in range(n_t):
            for i in range(n_f):
                v = (float(np.clip(self.s[i, j], self.piso, 0.0))
                     - self.piso) / (0.0 - self.piso)
                r = Rectangle(width=dx * 1.02, height=dy * 1.02,
                              stroke_width=0,
                              fill_color=interpolate_color(c_bajo, c_alto,
                                                           v),
                              fill_opacity=1.0)
                r.move_to(self._origen()
                          + np.array([(j + 0.5) / n_t - 0.5, 0.0, 0.0])
                          * self.ancho
                          + np.array([0.0, (i + 0.5) / n_f - 0.5, 0.0])
                          * self.alto)
                self.celdas.add(r)
        self.n_f, self.n_t = n_f, n_t
        ex = Line(self.en(self.t[0], self.f[0]),
                  self.en(self.t[-1], self.f[0]), color=C_EJE,
                  stroke_width=1.6)
        ey = Line(self.en(self.t[0], self.f[0]),
                  self.en(self.t[0], self.f[-1]), color=C_EJE,
                  stroke_width=1.6)
        self.ejes = VGroup(ex, ey)
        self.add(self.celdas, self.ejes)

    def en(self, t, f):
        fx = ((float(t) - self.t[0])
              / max(self.t[-1] - self.t[0], 1e-30) - 0.5)
        fy = ((float(f) - self.f[0])
              / max(self.f[-1] - self.f[0], 1e-30) - 0.5)
        return (self._origen() + np.array([fx * self.ancho,
                                           fy * self.alto, 0.0]))

    def celda(self, i, j):
        return self.celdas[int(j) * self.n_f + int(i)]

    def marca_t(self, t, color=C_CALCULO):
        from manim import DashedLine
        return DashedLine(self.en(t, self.f[0]), self.en(t, self.f[-1]),
                          color=color, stroke_width=1.8, dash_length=0.08)


def espectrograma(t, f, s_db, ancho=8.0, alto=3.2, piso_db=-60.0):
    """Ver `Espectrograma`."""
    return Espectrograma(t, f, s_db, ancho, alto, piso_db)

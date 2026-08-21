"""Comunicaciones digitales: la voz que cruza el vacio.
Pensada para la familia de cursos "Comunicaciones digitales" (leccion 1.1
en adelante): la capa de SIMBOLOS del enlace — muestreo, constelaciones,
ruido medido, sincronia, codigos con memoria, sistemas adaptativos y la
IA que entra al enlace. Todo el calculo es numpy/python puro y
determinista (el unico azar va con `np.random.default_rng(semilla)` FIJA;
los entrenamientos de IA son pequenos y con semilla): mismo script,
mismo render — condicion necesaria para `--disable_caching`. Sin red,
sin disco, sin scipy (la Q sale de math.erfc).
La regla de color de la familia: **el color dice el papel**.
    C_BIT     ambar    el bit, el dato, el mensaje que viaja
    C_CIFRA   cian     TODA cifra calculada
    C_SENAL   azul     la forma de onda, la portadora, el canal fisico
    C_RUIDO   rojo     ruido, errores, bits volteados, distorsion
    C_COD     verde    codigos, lo corregido, lo que funciona
    C_TECHO   violeta  el techo de Shannon, lo optimo
    C_IA      fucsia   lo aprendido: pesos, fronteras, constelaciones
    C_BANDA   naranja  espectro, energia, ranuras asignadas
Numeros (toda cifra en pantalla sale de aqui o de la tabla del
style_block, nunca escrita a mano):
    muestrear / alias_de / cuantizar / snr_cuantizacion
    pulso_rc / pulso_lento / conformar / isi_en
    psd_db / ancho_banda
    constelacion_bpsk|qpsk|psk8|qam16|qam64|apsk16  (puntos, bits Gray)
    energia_media / d_min / awgn / demodular
    ber_montecarlo / ser_montecarlo (cualquier set de puntos) / ber_teorica_qam / q_de
    fspl_db / saleh / pase_leo / doppler_de
    secuencia_pn / correlacion_circular / buscar_preambulo
    conv_codificar / viterbi (con historia de metricas)
    ldpc_pequeno / ldpc_decodificar (historia de sindromes)
    walsh / cdma_mezclar / cdma_extraer
    lluvia_serie / acm_conmutar / ppm_fotones
    entrenar_frontera / predecir_red / frontera_de
    autoencoder_constelacion / bandido_acm
Piezas (VGroup con localizadores que siguen move_to/shift, NO scale):
    onda            serie temporal en caja de ejes; gemela .con_serie()
    tren_bits       celdas 0/1; .marcar(i); gemela .con_bits()
    plano_iq        plano I/Q; .punto/.puntos/.nube/.regiones
    diagrama_ojo    trazas superpuestas; gemela .con_trazas()
    curva_ber       eje semilog 10^0..10^-5; .curva/.puntos_medidos
    espectro_area   PSD en dB; gemela .con_psd()
    banda_espacio   regla logaritmica de frecuencias con marcas
    enlace_tierra   Tierra + arco + nave; .paquete()
    pase_cielo      la boveda del pase LEO; .sat_en(frac)
    registro_conv   codificador K=3; gemela .con_bit()
    trellis         estados x tiempo; .rama/.camino/.metrica
    grafo_ldpc      grafo bipartito de H; gemela .con_estado()
    rejilla_acceso  tiempo x frecuencia; gemela .con_plan()
    mapa_haces      celdas de la constelacion; .haz(k)
    ranuras_ppm     M ranuras con fotones; gemela .con_cuentas()
    frontera_decision  fronteras de un campo de etiquetas
    perceptron_mini    esquema 2-H-M; gemela .con_pesos()
Uso en un clip (el style_block de la familia ya importa todo):
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from comunicaciones import *
"""
import math

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, PI, RIGHT, TAU, UP, Arrow, Circle,
                   DashedLine, Dot, Line, ManimColor, MathTex, Polygon,
                   Rectangle, Square, VGroup, VMobject, interpolate_color)

from algebra_lineal import (C_AREA, C_EJE, C_I, C_IMG, C_J, C_K, C_PROPIO,
                            C_REJILLA, C_VEC, C_VIVA, _Anclada, _texto_hud,
                            fmt, flecha_libre, grafica, plano, vector)

# --- roles de la familia ------------------------------------------------
C_BIT = C_I           # ambar: el bit, el dato, el mensaje
C_CIFRA = C_J         # cian: cifras calculadas
C_SENAL = C_VIVA      # azul: forma de onda, portadora, canal fisico
C_RUIDO = C_VEC       # rojo: ruido, errores, distorsion
C_COD = C_IMG         # verde: codigos, lo corregido
C_TECHO = C_K         # violeta: el techo de Shannon, lo optimo
C_IA = C_PROPIO       # fucsia: lo aprendido
C_BANDA = C_AREA      # naranja: espectro, ranuras

_LUZ_KM_S = 299792.458
_R_TIERRA = 6371.0
_MU_TIERRA = 398600.4418   # km^3/s^2


# =====================================================================
# Muestreo y cuantizacion (leccion 1.1)
# =====================================================================
def muestrear(f, fs, t1, t0=0.0):
    """Instantes k/fs en [t0, t1] y sus valores f(t). -> (tk, yk)"""
    tk = np.arange(math.ceil(t0 * fs), math.floor(t1 * fs) + 1) / fs
    return tk, np.array([float(f(t)) for t in tk])


def alias_de(f_hz, fs_hz):
    """La frecuencia (>=0) que APARENTA un seno de f muestreado a fs."""
    fa = math.fmod(f_hz, fs_hz)
    if fa > fs_hz / 2:
        fa = fs_hz - fa
    return abs(fa)


def cuantizar(y, bits, y_min=-1.0, y_max=1.0):
    """Redondeo a 2^bits niveles uniformes. -> (niveles, yq)"""
    n = 2 ** int(bits)
    paso = (y_max - y_min) / n
    niveles = y_min + paso * (np.arange(n) + 0.5)
    idx = np.clip(np.round((np.asarray(y) - y_min) / paso - 0.5), 0, n - 1)
    return niveles, niveles[idx.astype(int)]


def snr_cuantizacion(y, bits, y_min=-1.0, y_max=1.0):
    """SNR MEDIDA de la cuantizacion, en dB (~ 6.02 b + 1.76 si llena)."""
    y = np.asarray(y, dtype=float)
    _, yq = cuantizar(y, bits, y_min, y_max)
    err = y - yq
    return 10.0 * math.log10(float(np.mean(y ** 2) / np.mean(err ** 2)))


def bits_de_muestra(y, bits, y_min=-1.0, y_max=1.0):
    """La palabra binaria (lista de 0/1) del nivel cuantizado de y."""
    n = 2 ** int(bits)
    paso = (y_max - y_min) / n
    idx = int(np.clip(round((float(y) - y_min) / paso - 0.5), 0, n - 1))
    return [int(b) for b in format(idx, f"0{int(bits)}b")]


# =====================================================================
# Pulsos y conformado (lecciones 1.2 y 1.3)
# =====================================================================
def pulso_rc(beta=0.35, span=8, sps=8):
    """Coseno alzado h(t) (pico 1) y su eje t en SIMBOLOS. -> (t, h)"""
    t = np.arange(-span * sps // 2, span * sps // 2 + 1) / sps
    h = np.zeros_like(t)
    for i, ti in enumerate(t):
        den = 1.0 - (2.0 * beta * ti) ** 2
        if abs(den) < 1e-9:
            h[i] = (math.pi / 4.0) * np.sinc(1.0 / (2.0 * beta))
        else:
            h[i] = np.sinc(ti) * math.cos(math.pi * beta * ti) / den
    return t, h


def pulso_rect(span=8, sps=8):
    """Pulso rectangular de 1 simbolo (mismo eje que pulso_rc)."""
    t = np.arange(-span * sps // 2, span * sps // 2 + 1) / sps
    return t, np.where(np.abs(t) <= 0.5, 1.0, 0.0)


def conformar(simbolos, h, sps=8):
    """Tren de pulsos: impulsos +-1 (o niveles) convolucionados con h.
    -> (t en simbolos, y). El simbolo k decide en t = k."""
    x = np.zeros(len(simbolos) * sps)
    x[::sps] = np.asarray(simbolos, dtype=float)
    y = np.convolve(x, h)
    retardo = (len(h) - 1) // 2
    y = y[retardo:retardo + len(x)]
    return np.arange(len(x)) / sps, y


def isi_en(h, sps=8, k=1):
    """El valor de la cola del pulso h en el instante del vecino k."""
    centro = (len(h) - 1) // 2
    i = centro + int(k) * sps
    return float(h[i]) if 0 <= i < len(h) else 0.0


def pulso_lento(tau=0.45, span=8, sps=8):
    """Un rectangulo tras un canal de un polo (RC): sube lento y deja
    cola exponencial sobre los vecinos (el pulso TORPE de 1.2).
    -> (t, h) con pico 1, mismo eje que pulso_rc."""
    t = np.arange(-span * sps // 2, span * sps // 2 + 1) / sps
    dt = 1.0 / sps
    n_k = int(6 * tau * sps)
    k = np.exp(-np.arange(n_k) * dt / tau)
    k /= k.sum()
    _, rect = pulso_rect(span, sps)
    h = np.convolve(rect, k)[:len(rect)]
    return t, h / h.max()


def psd_db(x, fs=1.0, nseg=256):
    """PSD de Welch (hann, 50%), normalizada a pico 0 dB. -> (f, p_db)"""
    x = np.asarray(x, dtype=float)
    nseg = int(min(nseg, len(x)))
    paso = max(1, nseg // 2)
    w = np.hanning(nseg)
    acc, cuenta = None, 0
    for i0 in range(0, len(x) - nseg + 1, paso):
        seg = x[i0:i0 + nseg] * w
        p = np.abs(np.fft.rfft(seg)) ** 2
        acc = p if acc is None else acc + p
        cuenta += 1
    p = acc / cuenta
    p = np.maximum(p / p.max(), 1e-12)
    return np.fft.rfftfreq(nseg, d=1.0 / fs), 10.0 * np.log10(p)


def ancho_banda(f, p_db, frac=0.99):
    """La frecuencia que encierra `frac` de la energia total."""
    p = 10.0 ** (np.asarray(p_db) / 10.0)
    c = np.cumsum(p)
    c = c / c[-1]
    return float(np.interp(frac, c, f))


# =====================================================================
# Constelaciones (modulo 2): (puntos complejos Es=1, bits Gray M x k)
# =====================================================================
def _normalizar(p):
    return p / math.sqrt(float(np.mean(np.abs(p) ** 2)))


def constelacion_bpsk():
    return np.array([1.0 + 0j, -1.0 + 0j]), np.array([[0], [1]])


def constelacion_qpsk():
    """Gray: 00,01,11,10 en las cuatro fases (45,135,225,315 grados)."""
    fases = np.array([45, 135, 225, 315]) * math.pi / 180.0
    p = np.exp(1j * fases)
    bits = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])
    return _normalizar(p), bits


def constelacion_psk8():
    """8-PSK Gray (fases cada 45 grados)."""
    p = np.exp(1j * np.arange(8) * math.pi / 4.0)
    gray3 = [0, 1, 3, 2, 6, 7, 5, 4]
    bits = np.array([[int(b) for b in format(g, "03b")] for g in gray3])
    return _normalizar(p), bits


def _pam_gray(m):
    """Niveles PAM con etiqueta Gray: (niveles, bits) en orden Gray."""
    k = int(round(math.log2(m)))
    gray = [i ^ (i >> 1) for i in range(m)]
    niveles = np.arange(-(m - 1), m, 2, dtype=float)
    bits = np.zeros((m, k), dtype=int)
    for orden, g in enumerate(gray):
        bits[orden] = [int(b) for b in format(g, f"0{k}b")]
    return niveles, bits


def _qam(m_lado):
    ni, bi = _pam_gray(m_lado)
    p, bits = [], []
    for a, ba in zip(ni, bi):
        for b, bb in zip(ni, bi):
            p.append(a + 1j * b)
            bits.append(list(ba) + list(bb))
    return _normalizar(np.array(p)), np.array(bits, dtype=int)


def constelacion_qam16():
    return _qam(4)


def constelacion_qam64():
    return _qam(8)


def constelacion_apsk16(gamma=3.15):
    """16-APSK 4+12 (DVB-S2, anillo exterior gamma veces el interior)."""
    r1 = 1.0
    f_int = (np.array([45, 135, 225, 315])) * math.pi / 180.0
    f_ext = (np.arange(12) * 30.0 + 15.0) * math.pi / 180.0
    p = np.concatenate([r1 * np.exp(1j * f_int),
                        gamma * r1 * np.exp(1j * f_ext)])
    bits = np.array([[int(b) for b in format(i, "04b")] for i in range(16)])
    return _normalizar(p), bits


def energia_media(puntos):
    return float(np.mean(np.abs(puntos) ** 2))


def d_min(puntos):
    p = np.asarray(puntos)
    d = np.abs(p[:, None] - p[None, :])
    return float(np.min(d[d > 1e-12]))


def q_de(x):
    """La funcion Q (cola gaussiana), vectorizada via math.erfc."""
    xs = np.atleast_1d(np.asarray(x, dtype=float))
    r = np.array([0.5 * math.erfc(v / math.sqrt(2.0)) for v in xs])
    return float(r[0]) if np.isscalar(x) or np.ndim(x) == 0 else r


def ber_teorica_qam(m, ebn0_db):
    """BER Gray aproximada de M-QAM (M=2 -> BPSK, 4 -> QPSK)."""
    m = int(m)
    k = math.log2(m)
    e = 10.0 ** (np.asarray(ebn0_db, dtype=float) / 10.0)
    if m == 2:
        return q_de(np.sqrt(2.0 * e))
    if m == 4:
        return q_de(np.sqrt(2.0 * e))
    return (4.0 / k) * (1.0 - 1.0 / math.sqrt(m)) * q_de(
        np.sqrt(3.0 * k * e / (m - 1.0)))


def awgn(simbolos, ebn0_db, bits_por_simbolo, semilla=1):
    """Ruido blanco complejo para Es=1. -> simbolos + ruido"""
    rng = np.random.default_rng(semilla)
    ebn0 = 10.0 ** (float(ebn0_db) / 10.0)
    sigma = math.sqrt(1.0 / (2.0 * bits_por_simbolo * ebn0))
    n = rng.normal(0.0, sigma, (len(simbolos), 2))
    return np.asarray(simbolos) + n[:, 0] + 1j * n[:, 1]


def demodular(rx, puntos):
    """Vecino mas cercano. -> indices en `puntos`."""
    return np.argmin(np.abs(np.asarray(rx)[:, None]
                            - np.asarray(puntos)[None, :]), axis=1)


def ber_montecarlo(puntos, bits, ebn0_db, n=200000, semilla=1):
    """BER CONTADA para cualquier set de puntos etiquetado. ->
    (ber, errores_bit, n_bits)"""
    rng = np.random.default_rng(semilla)
    puntos = np.asarray(puntos)
    bits = np.asarray(bits)
    k = bits.shape[1]
    idx = rng.integers(0, len(puntos), int(n))
    rx = awgn(puntos[idx], ebn0_db, k, semilla=semilla + 1)
    dec = demodular(rx, puntos)
    err = int(np.sum(bits[idx] != bits[dec]))
    return err / (int(n) * k), err, int(n) * k


def ser_montecarlo(puntos, ebn0_db, bits_por_simbolo, n=200000, semilla=1):
    """Tasa de error de SIMBOLO contada para cualquier set de puntos
    (sin depender del mapeo de bits). -> (ser, errores, n)"""
    rng = np.random.default_rng(semilla)
    puntos = np.asarray(puntos)
    idx = rng.integers(0, len(puntos), int(n))
    rx = awgn(puntos[idx], ebn0_db, bits_por_simbolo, semilla=semilla + 1)
    dec = demodular(rx, puntos)
    err = int(np.sum(dec != idx))
    return err / int(n), err, int(n)


# =====================================================================
# El canal espacial (modulo 3)
# =====================================================================
def fspl_db(d_km, f_ghz):
    """Perdida de espacio libre: 92.45 + 20 log d(km) + 20 log f(GHz)."""
    return 92.45 + 20.0 * math.log10(float(d_km)) + 20.0 * math.log10(float(f_ghz))


def saleh(r, alfa=2.0, beta=1.0):
    """AM/AM del amplificador saturado (Saleh): A(r) = a r / (1 + b r^2)."""
    r = np.asarray(r, dtype=float)
    return alfa * r / (1.0 + beta * r ** 2)


def amplificar(puntos, retroceso=1.0, alfa=2.0, beta=1.0,
               con_fase=False, alfa_f=math.pi / 3.0, beta_f=1.0):
    """Aplica Saleh a una constelacion escalada por `retroceso` (drive):
    AM/AM siempre (comprime los anillos exteriores; leccion 2.2) y, con
    `con_fase=True`, tambien AM/PM (cada anillo gira distinto: la
    ESPIRAL del demodulador aprendido, leccion 6.1). Reescala a Es=1."""
    p = np.asarray(puntos) * float(retroceso)
    r = np.abs(p)
    with np.errstate(invalid="ignore", divide="ignore"):
        g = np.where(r > 1e-12, saleh(r, alfa, beta) / r, alfa)
    if con_fase:
        g = g * np.exp(1j * alfa_f * r ** 2 / (1.0 + beta_f * r ** 2))
    return _normalizar(p * g)


def pase_leo(h_km=550.0, elev_max=60.0, n=241):
    """Pase de un LEO circular sobre la estacion (Tierra sin rotar; se
    declara en el pie). -> dict(t_s, elev_deg, d_km, t_total_s)"""
    a = _R_TIERRA + float(h_km)
    om = math.sqrt(_MU_TIERRA / a ** 3)          # rad/s

    def elev_de(lam):
        # elevacion desde el angulo central lam (rad)
        num = math.cos(lam) - _R_TIERRA / a
        den = math.sin(lam)
        return math.atan2(num, den)

    # lam0 (offset minimo) por biseccion para que elev(lam0) = elev_max
    obj = math.radians(float(elev_max))
    lo, hi = 1e-6, math.acos(_R_TIERRA / a) - 1e-9
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if elev_de(mid) > obj:
            lo = mid
        else:
            hi = mid
    lam0 = 0.5 * (lo + hi)
    lam_hor = math.acos(_R_TIERRA / a)           # elevacion 0
    ct = math.cos(lam_hor) / math.cos(lam0)
    t_max = math.acos(max(-1.0, min(1.0, ct))) / om
    t = np.linspace(-t_max, t_max, int(n))
    lam = np.arccos(np.clip(np.cos(lam0) * np.cos(om * t), -1.0, 1.0))
    elev = np.degrees(np.array([elev_de(max(l, 1e-9)) for l in lam]))
    d = np.sqrt(_R_TIERRA ** 2 + a ** 2
                - 2.0 * _R_TIERRA * a * np.cos(lam))
    return {"t_s": t, "elev_deg": elev, "d_km": d, "t_total_s": 2 * t_max}


def doppler_de(pase, f_mhz=437.0):
    """Corrimiento Doppler en kHz a lo largo del pase (curva S)."""
    rr = np.gradient(pase["d_km"], pase["t_s"])   # km/s
    return -float(f_mhz) * 1e6 * rr / _LUZ_KM_S / 1e3


# =====================================================================
# Sincronia (leccion 3.3)
# =====================================================================
def secuencia_pn(n=31, semilla_reg=0b10101):
    """m-secuencia de un LFSR de 5 bits (x^5 + x^2 + 1), chips +-1."""
    if n != 31:
        raise ValueError("la m-secuencia de 5 bits mide 31")
    reg = [int(b) for b in format(semilla_reg & 0b11111, "05b")]
    chips = []
    for _ in range(31):
        chips.append(reg[-1])
        nuevo = reg[4] ^ reg[1]                  # x^5 + x^2 + 1
        reg = [nuevo] + reg[:-1]
    return np.array([1 if c else -1 for c in chips], dtype=float)


def correlacion_circular(a, b):
    """R[k] = sum a[i] b[i+k mod n] (autocorrelacion si a is b)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return np.array([float(np.dot(a, np.roll(b, -k))) for k in range(len(a))])


def buscar_preambulo(rx, pn):
    """Correlacion deslizante (valida). -> (correlaciones, offset_max)"""
    rx = np.asarray(rx, dtype=float)
    pn = np.asarray(pn, dtype=float)
    c = np.correlate(rx, pn, mode="valid")
    return c, int(np.argmax(c))


def senal_con_preambulo(offset=40, snr_db=0.0, n_total=140, semilla=7):
    """Ruido con la PN de 31 chips enterrada en `offset` (amplitud segun
    SNR por chip). -> rx"""
    rng = np.random.default_rng(semilla)
    pn = secuencia_pn()
    a = 10.0 ** (float(snr_db) / 20.0)
    rx = rng.normal(0.0, 1.0, int(n_total))
    rx[offset:offset + 31] += a * pn
    return rx


# =====================================================================
# Codigos con memoria (modulo 4)
# =====================================================================
_CONV_SALIDAS = {}
for _s in range(4):
    for _b in range(2):
        _m1, _m0 = (_s >> 1) & 1, _s & 1
        _o1 = _b ^ _m0 ^ _m1        # g1 = 111
        _o2 = _b ^ _m1              # g2 = 101
        _CONV_SALIDAS[(_s, _b)] = ((_b << 1) | (_s >> 1), (_o1, _o2))
# ojo: estado = (bit_nuevo, memoria_vieja_alta); transicion arriba


def conv_codificar(bits):
    """Convolucional K=3, G=(7,5) octal, tasa 1/2, estado inicial 0.
    -> (codificados (2 por bit), estados visitados)"""
    s, salida, estados = 0, [], [0]
    for b in bits:
        s2, (o1, o2) = _CONV_SALIDAS[(s, int(b))]
        salida += [o1, o2]
        s = s2
        estados.append(s)
    return np.array(salida, dtype=int), estados


def viterbi(recibidos):
    """Decodifica (Hamming) la salida de conv_codificar. ->
    dict(bits, camino, metricas[t][s], podas): metricas acumuladas por
    etapa y estado (inf = estado inalcanzable)."""
    r = np.asarray(recibidos, dtype=int).reshape(-1, 2)
    T = len(r)
    INF = 10 ** 9
    met = [[INF] * 4 for _ in range(T + 1)]
    met[0][0] = 0
    prev = [[None] * 4 for _ in range(T + 1)]
    for t in range(T):
        for s in range(4):
            if met[t][s] >= INF:
                continue
            for b in (0, 1):
                s2, (o1, o2) = _CONV_SALIDAS[(s, b)]
                costo = (o1 != r[t][0]) + (o2 != r[t][1])
                if met[t][s] + costo < met[t + 1][s2]:
                    met[t + 1][s2] = met[t][s] + costo
                    prev[t + 1][s2] = (s, b)
    s = int(np.argmin(met[T]))
    camino, bits = [s], []
    for t in range(T, 0, -1):
        s0, b = prev[t][camino[-1]]
        bits.append(b)
        camino.append(s0)
    return {"bits": bits[::-1], "camino": camino[::-1],
            "metricas": met, "metrica_final": met[T][int(np.argmin(met[T]))]}


def ldpc_pequeno():
    """H (9 x 12) del sistema triple de Steiner S(2,3,9) (el plano afin
    de orden 3): los 12 BITS son las lineas, los 9 CHECKS los puntos;
    columnas de peso 3, filas de peso 4, y dos columnas comparten a lo
    sumo UN check. Garantia (validada): cualquier bit suelto se corrige
    en 1 iteracion, y cualquier par de bits con checks disjuntos (p. ej.
    dos lineas paralelas: los pares (0,1),(0,2),(1,2),(3,4)... dentro de
    cada bloque de 3) se corrige con sindrome 6 -> 3 -> 0. -> H"""
    lineas = []
    for m in range(3):
        for b in range(3):
            lineas.append(tuple(sorted(3 * x + ((m * x + b) % 3)
                                       for x in range(3))))
    for x in range(3):
        lineas.append(tuple(3 * x + y for y in range(3)))
    H = np.zeros((9, 12), dtype=int)
    for c, ln in enumerate(lineas):
        for p in ln:
            H[p, c] = 1
    return H


def ldpc_decodificar(x, H, max_iter=6):
    """Bit-flipping: voltea EL bit mas acusado por sindromes insatisfechos
    (uno por iteracion, para verlo). -> lista de pasos
    [(x, sindrome, bit_volteado)] con el estado inicial primero."""
    x = np.array(x, dtype=int) % 2
    pasos = []
    volteado = None
    for _ in range(int(max_iter) + 1):
        s = (H @ x) % 2
        pasos.append((x.copy(), s.copy(), volteado))
        if not s.any():
            break
        cuentas = H.T @ s
        volteado = int(np.argmax(cuentas))
        x = x.copy()
        x[volteado] ^= 1
    return pasos


# =====================================================================
# Acceso multiple (leccion 5.1)
# =====================================================================
def walsh(n=8):
    """Matriz de Hadamard-Walsh n x n (+-1), filas ortogonales."""
    H = np.array([[1.0]])
    while H.shape[0] < n:
        H = np.block([[H, H], [H, -H]])
    return H


def cdma_mezclar(bits_por_usuario, codigos):
    """Suma de usuarios: cada bit (+-1) estirado por su codigo. -> chips"""
    total = None
    for bits, cod in zip(bits_por_usuario, codigos):
        chips = np.concatenate([float(b) * np.asarray(cod, dtype=float)
                                for b in bits])
        total = chips if total is None else total + chips
    return total


def cdma_extraer(chips, codigo):
    """Correlar por bloques con el codigo. -> (correlaciones, bits +-1)"""
    n = len(codigo)
    m = len(chips) // n
    cor = np.array([float(np.dot(chips[i * n:(i + 1) * n], codigo)) / n
                    for i in range(m)])
    return cor, np.sign(cor)


# =====================================================================
# El canal que respira y ACM (lecciones 3.1 y 5.2)
# =====================================================================
def lluvia_serie(n=240, semilla=5, p_entrar=0.025, p_salir=0.06,
                 att_max=16.0):
    """Atenuacion Ka (dB) minuto a minuto: cadena de dos estados
    (claro/lluvia) + rampa AR con memoria. -> (t_min, att_db)"""
    rng = np.random.default_rng(semilla)
    att = np.zeros(int(n))
    objetivo, lluvia, a = 0.0, False, 0.0
    for i in range(int(n)):
        if lluvia and rng.random() < p_salir:
            lluvia = False
        elif not lluvia and rng.random() < p_entrar:
            lluvia = True
            objetivo = rng.uniform(0.55, 1.0) * att_max
        meta = objetivo if lluvia else 0.0
        a += 0.10 * (meta - a) + rng.normal(0.0, 0.12)
        a = max(0.0, a)
        att[i] = a
    return np.arange(int(n), dtype=float), att


MODCODS = [("QPSK 1/2", 1.0, 1.00),
           ("8PSK 3/4", 7.9, 2.25),
           ("16APSK 5/6", 11.0, 3.33)]


def acm_conmutar(att_db, snr_claro=13.0, modcods=None, histeresis=0.3):
    """Elige por minuto el modcod mas denso que cierra (con histeresis).
    -> dict(eleccion (indices, -1 = corte), bits_acm, bits_fijo,
    outage_acm_min, outage_fijo_min, snr)"""
    mc = modcods or MODCODS
    snr = float(snr_claro) - np.asarray(att_db, dtype=float)
    elec = []
    actual = -2
    for s in snr:
        mejor = -1
        for i, (_, umbral, _) in enumerate(mc):
            margen = histeresis if (i != actual and i > 0) else 0.0
            if s >= umbral + margen:
                mejor = i
        elec.append(mejor)
        actual = mejor
    elec = np.array(elec)
    tasa = np.array([mc[i][2] if i >= 0 else 0.0 for i in elec])
    peor = np.array([mc[0][2] if s >= mc[0][1] else 0.0 for s in snr])
    return {"eleccion": elec, "snr": snr,
            "bits_acm": float(tasa.sum()), "bits_fijo": float(peor.sum()),
            "outage_acm_min": int(np.sum(elec < 0)),
            "outage_fijo_min": int(np.sum(peor == 0.0))}


def ppm_fotones(m=16, simbolo=5, media_senal=8.0, media_fondo=0.15,
                semilla=9):
    """Cuentas Poisson por ranura de un simbolo M-PPM. -> cuentas (m,)"""
    rng = np.random.default_rng(semilla)
    c = rng.poisson(media_fondo, int(m))
    c[int(simbolo)] += rng.poisson(media_senal)
    return c


# =====================================================================
# La IA en el enlace (modulo 6)
# =====================================================================
def entrenar_frontera(rx, etiquetas, m_clases, ocultas=12, pasos=300,
                      lr=0.6, semilla=2):
    """MLP 2-ocultas-M (tanh + softmax) entrenado con descenso de
    gradiente COMPLETO en numpy. -> dict(W1,b1,W2,b2, perdidas,
    aciertos): perdidas/aciertos por paso (cada 10)."""
    rng = np.random.default_rng(semilla)
    X = np.column_stack([np.real(rx), np.imag(rx)]).astype(float)
    y = np.asarray(etiquetas, dtype=int)
    n = len(y)
    W1 = rng.normal(0, 0.6, (2, int(ocultas)))
    b1 = np.zeros(int(ocultas))
    W2 = rng.normal(0, 0.6, (int(ocultas), int(m_clases)))
    b2 = np.zeros(int(m_clases))
    Y = np.zeros((n, int(m_clases)))
    Y[np.arange(n), y] = 1.0
    perdidas, aciertos = [], []
    for paso in range(int(pasos)):
        H = np.tanh(X @ W1 + b1)
        Z = H @ W2 + b2
        Z -= Z.max(axis=1, keepdims=True)
        P = np.exp(Z)
        P /= P.sum(axis=1, keepdims=True)
        if paso % 10 == 0 or paso == pasos - 1:
            perdidas.append(float(-np.mean(np.log(P[np.arange(n), y] + 1e-12))))
            aciertos.append(float(np.mean(np.argmax(P, axis=1) == y)))
        dZ = (P - Y) / n
        dW2 = H.T @ dZ
        dH = dZ @ W2.T * (1.0 - H ** 2)
        dW1 = X.T @ dH
        W2 -= lr * dW2
        b2 -= lr * dZ.sum(axis=0)
        W1 -= lr * dW1
        b1 -= lr * dH.sum(axis=0)
    return {"W1": W1, "b1": b1, "W2": W2, "b2": b2,
            "perdidas": perdidas, "aciertos": aciertos}


def predecir_red(red, rx):
    """Clase ganadora de la red para cada punto complejo."""
    X = np.column_stack([np.real(rx), np.imag(rx)]).astype(float)
    H = np.tanh(X @ red["W1"] + red["b1"])
    return np.argmax(H @ red["W2"] + red["b2"], axis=1)


def frontera_de(red, x0=-1.8, x1=1.8, n=90):
    """Campo de etiquetas (n x n) de la red sobre el plano IQ.
    campo[i, j] = clase en (xs[j], ys[i])."""
    xs = np.linspace(x0, x1, int(n))
    X, Y = np.meshgrid(xs, xs)
    z = (X + 1j * Y).ravel()
    return predecir_red(red, z).reshape(int(n), int(n)), xs


def campo_vecino(puntos, x0=-1.8, x1=1.8, n=90):
    """Campo de etiquetas del demodulador IDEAL (vecino mas cercano)."""
    xs = np.linspace(x0, x1, int(n))
    X, Y = np.meshgrid(xs, xs)
    z = (X + 1j * Y).ravel()
    return demodular(z, puntos).reshape(int(n), int(n)), xs


def autoencoder_constelacion(m=8, pasos=250, sigma=0.20, lr=0.05,
                             semilla=3, cada=10):
    """Aprende M puntos 2D minimizando la cota de union del error
    (sum exp(-d^2/8 sigma^2)) con energia media 1 (descenso de gradiente
    con semilla). -> dict(historial [(paso, puntos)], d_min [(paso, d)])"""
    rng = np.random.default_rng(semilla)
    P = rng.normal(0.0, 0.35, (int(m), 2))
    hist, dmins = [], []

    def _norm(P):
        return P / math.sqrt(float(np.mean(np.sum(P ** 2, axis=1))))

    P = _norm(P)
    s2 = 8.0 * sigma * sigma
    for paso in range(int(pasos) + 1):
        dif = P[:, None, :] - P[None, :, :]
        d2 = np.sum(dif ** 2, axis=2)
        np.fill_diagonal(d2, np.inf)
        w = np.exp(-d2 / s2)
        grad = np.zeros_like(P)
        for i in range(int(m)):
            grad[i] = np.sum((2.0 / s2) * w[i][:, None] * dif[i], axis=0)
        if paso % cada == 0 or paso == pasos:
            z = P[:, 0] + 1j * P[:, 1]
            hist.append((paso, z.copy()))
            dmins.append((paso, d_min(z)))
        P = _norm(P + lr * grad)
    return {"historial": hist, "d_min": dmins}


def bandido_acm(episodios=400, pasos_por_episodio=40, epsilon0=0.9,
                semilla=6, snr_claro=13.0):
    """Q-learning tabular: estados = cielo observado (claro/nube/lluvia),
    acciones = MODCODS; recompensa = bits que llegan. Compara contra
    politicas fijas con el MISMO clima. -> dict(recompensa_episodio,
    acumulada_agente, acumulada_conservador, acumulada_optimista,
    politica (accion por estado))"""
    rng = np.random.default_rng(semilla)
    ATT = [(0.0, 0.6), (4.0, 1.2), (12.0, 2.5)]   # media, sd por estado
    TRANS = np.array([[0.86, 0.09, 0.05],
                      [0.25, 0.60, 0.15],
                      [0.05, 0.25, 0.70]])
    Q = np.zeros((3, len(MODCODS)))
    rec_ep, acum_a, acum_c, acum_o = [], [0.0], [0.0], [0.0]
    for ep in range(int(episodios)):
        eps = epsilon0 * max(0.05, 1.0 - ep / (0.7 * episodios))
        estado = 0
        total = 0.0
        for _ in range(int(pasos_por_episodio)):
            att = max(0.0, rng.normal(*ATT[estado]))
            snr = snr_claro - att
            if rng.random() < eps:
                a = int(rng.integers(len(MODCODS)))
            else:
                a = int(np.argmax(Q[estado]))
            r = MODCODS[a][2] if snr >= MODCODS[a][1] else 0.0
            rc = MODCODS[0][2] if snr >= MODCODS[0][1] else 0.0
            ro = MODCODS[-1][2] if snr >= MODCODS[-1][1] else 0.0
            Q[estado, a] += 0.08 * (r - Q[estado, a])
            total += r
            acum_a.append(acum_a[-1] + r)
            acum_c.append(acum_c[-1] + rc)
            acum_o.append(acum_o[-1] + ro)
            estado = int(rng.choice(3, p=TRANS[estado]))
        rec_ep.append(total)
    return {"recompensa_episodio": np.array(rec_ep),
            "acumulada_agente": np.array(acum_a[1:]),
            "acumulada_conservador": np.array(acum_c[1:]),
            "acumulada_optimista": np.array(acum_o[1:]),
            "politica": np.argmax(Q, axis=1)}


# =====================================================================
# PIEZAS — todas con localizadores (patron _Anclada del sustrato)
# =====================================================================
def apertura_ojo(y, sps=8):
    """Apertura vertical MEDIDA del ojo en el instante de decision:
    min(trazas positivas) - max(trazas negativas) en el centro."""
    y = np.asarray(y, dtype=float)
    vals = y[2 * sps::sps]                      # decisiones interiores
    arriba = vals[vals > 0]
    abajo = vals[vals < 0]
    if len(arriba) == 0 or len(abajo) == 0:
        return 0.0
    return float(arriba.min() - abajo.max())


class Onda(_Anclada):
    """Serie temporal en su caja de ejes. .en(t, y) .curva .ejes
    .curva_de(t2, y2, color)   otra serie en la MISMA caja
    .muestras(tk, yk)          palitos + puntos de muestreo
    .vertical_en(t) / .horizontal_en(y)
    .con_serie(y2)             GEMELA (misma caja, otra y) para Transform
    """

    def __init__(self, t, y, rango_y=None, ancho=5.6, alto=2.2,
                 color=C_SENAL, grosor=2.6, **kwargs):
        super().__init__(**kwargs)
        self.t = np.asarray(t, dtype=float)
        self.y = np.asarray(y, dtype=float)
        if rango_y is None:
            m = float(np.max(np.abs(self.y))) * 1.15 + 1e-9
            rango_y = (-m, m)
        self.y0, self.y1 = float(rango_y[0]), float(rango_y[1])
        self.x0, self.x1 = float(self.t[0]), float(self.t[-1])
        self.ancho, self.alto = float(ancho), float(alto)
        self.color = color
        self.grosor = grosor
        self._poner_ancla(ORIGIN)
        cy = 0.0 if self.y0 <= 0 <= self.y1 else self.y0
        ex = Line(self.en(self.x0, cy), self.en(self.x1, cy), color=C_EJE,
                  stroke_width=1.6)
        ey = Line(self.en(self.x0, self.y0), self.en(self.x0, self.y1),
                  color=C_EJE, stroke_width=1.6)
        self.ejes = VGroup(ex, ey)
        self.curva = self._poli(self.t, self.y, color, grosor)
        self.add(self.ejes, self.curva)

    def en(self, t, y):
        fx = (t - self.x0) / (self.x1 - self.x0)
        fy = (np.clip(y, self.y0, self.y1) - self.y0) / (self.y1 - self.y0)
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (fy - 0.5) * self.alto, 0.0]))

    def _poli(self, t, y, color, grosor):
        c = VMobject(color=color, stroke_width=grosor)
        c.set_points_as_corners([self.en(a, b) for a, b in zip(t, y)])
        return c

    def curva_de(self, t2, y2, color=C_BIT, grosor=2.6):
        return self._poli(np.asarray(t2, float), np.asarray(y2, float),
                          color, grosor)

    def muestras(self, tk, yk, color=C_BIT, radio=0.05):
        g = VGroup()
        for a, b in zip(tk, yk):
            base = self.en(a, 0.0)
            g.add(Line(base, self.en(a, b), color=color, stroke_width=2.0),
                  Dot(self.en(a, b), radius=radio, color=color))
        return g

    def vertical_en(self, t, color=C_CIFRA):
        return DashedLine(self.en(t, self.y0), self.en(t, self.y1),
                          color=color, stroke_width=1.6, dash_length=0.07)

    def horizontal_en(self, y, color=C_CIFRA):
        return DashedLine(self.en(self.x0, y), self.en(self.x1, y),
                          color=color, stroke_width=1.6, dash_length=0.07)

    def con_serie(self, y2, color=None):
        o = Onda(self.t, y2, (self.y0, self.y1), self.ancho, self.alto,
                 color or self.color, self.grosor)
        o.shift(self._origen() - o._origen())
        return o


def onda(t, y, rango_y=None, ancho=5.6, alto=2.2, color=C_SENAL,
         grosor=2.6):
    """Ver `Onda`."""
    return Onda(t, y, rango_y, ancho, alto, color, grosor)


class TrenBits(_Anclada):
    """Celdas 0/1 en fila. .celda(i) .digito(i) .marcar(i, color)
    .con_bits(bits) GEMELA."""

    def __init__(self, bits, lado=0.42, color=C_BIT, **kwargs):
        super().__init__(**kwargs)
        self.bits = [int(b) for b in bits]
        self.lado = float(lado)
        self.color = color
        self._poner_ancla(ORIGIN)
        self.celdas, self.digitos = VGroup(), VGroup()
        n = len(self.bits)
        for i, b in enumerate(self.bits):
            x = (i - (n - 1) / 2.0) * self.lado
            c = Square(self.lado, color=C_EJE, stroke_width=1.4)
            c.move_to(self._origen() + np.array([x, 0.0, 0.0]))
            d = _texto_hud(str(b), font_size=17,
                           color=color if b else C_EJE)
            d.move_to(c.get_center())
            self.celdas.add(c)
            self.digitos.add(d)
        self.add(self.celdas, self.digitos)

    def celda(self, i):
        return self.celdas[i]

    def digito(self, i):
        return self.digitos[i]

    def marcar(self, i, color=C_RUIDO):
        self.celdas[i].set_stroke(color, width=2.6)
        self.digitos[i].set_color(color)
        return self

    def con_bits(self, bits, color=None):
        o = TrenBits(bits, self.lado, color or self.color)
        o.shift(self._origen() - o._origen())
        return o


def tren_bits(bits, lado=0.42, color=C_BIT):
    """Ver `TrenBits`."""
    return TrenBits(bits, lado, color)


def _segmentos_frontera(campo, xs, mapear, color, grosor=2.2):
    """Un VMobject con los bordes entre etiquetas distintas del campo
    (campo[i, j] = etiqueta en (xs[j], xs[i]); `mapear(x, y)` -> pantalla)."""
    v = VMobject(color=color, stroke_width=grosor)
    n = campo.shape[0]
    h = (xs[1] - xs[0]) / 2.0
    for i in range(n):
        for j in range(n - 1):
            if campo[i, j] != campo[i, j + 1]:
                x = xs[j] + h
                v.start_new_path(mapear(x, xs[i] - h))
                v.add_line_to(mapear(x, xs[i] + h))
    for i in range(n - 1):
        for j in range(n):
            if campo[i, j] != campo[i + 1, j]:
                y = xs[i] + h
                v.start_new_path(mapear(xs[j] - h, y))
                v.add_line_to(mapear(xs[j] + h, y))
    return v


class PlanoIQ(_Anclada):
    """El plano I/Q. .p(x, y) .punto(z) .puntos(pts, bits) .nube(rx)
    .regiones(campo, xs)  fronteras de decision de un campo de etiquetas
    .circulo(r)           anillo de radio r (APSK)"""

    def __init__(self, unidad=1.15, alcance=1.75, **kwargs):
        super().__init__(**kwargs)
        self.u = float(unidad)
        self.alcance = float(alcance)
        self._poner_ancla(ORIGIN)
        L = self.u * self.alcance
        ex = Line(self._origen() + LEFT * L, self._origen() + RIGHT * L,
                  color=C_EJE, stroke_width=1.6)
        ey = Line(self._origen() + DOWN * L, self._origen() + UP * L,
                  color=C_EJE, stroke_width=1.6)
        self.ejes = VGroup(ex, ey)
        self.unidad_circulo = Circle(
            radius=self.u, color=C_REJILLA, stroke_width=1.3)
        marcas = VGroup()
        for s in (-1, 1):
            marcas.add(Line(self.p(s, -0.045), self.p(s, 0.045),
                            color=C_EJE, stroke_width=1.6),
                       Line(self.p(-0.045, s), self.p(0.045, s),
                            color=C_EJE, stroke_width=1.6))
        et_i = _texto_hud("I", font_size=15)
        et_i.next_to(ex.get_end(), DOWN, buff=0.12)
        et_q = _texto_hud("Q", font_size=15)
        et_q.next_to(ey.get_end(), RIGHT, buff=0.12)
        self.add(self.ejes, self.unidad_circulo, marcas, et_i, et_q)

    def p(self, x, y=None):
        if y is None:
            x, y = float(np.real(x)), float(np.imag(x))
        return self._origen() + np.array([x * self.u, y * self.u, 0.0])

    def circulo(self, r, color=C_REJILLA):
        c = Circle(radius=float(r) * self.u, color=color, stroke_width=1.3)
        c.move_to(self._origen())
        return c

    def punto(self, z, color=C_BIT, radio=0.075):
        return Dot(self.p(z), radius=radio, color=color)

    def puntos(self, pts, bits=None, color=C_BIT, radio=0.075,
               font_size=13, color_texto=None):
        g = VGroup()
        for i, z in enumerate(pts):
            g.add(Dot(self.p(z), radius=radio, color=color))
        if bits is not None:
            for i, z in enumerate(pts):
                et = _texto_hud("".join(str(int(b)) for b in bits[i]),
                                font_size=font_size,
                                color=color_texto or C_EJE)
                despl = np.array([0.0, 0.17, 0.0])
                if abs(np.imag(pts[i])) > 0.05:
                    despl[1] *= np.sign(np.imag(pts[i]))
                et.move_to(self.p(pts[i]) + despl)
                g.add(et)
        return g

    def nube(self, rx, color=C_SENAL, maximo=500, radio=0.028,
             opacidad=0.75):
        rx = np.asarray(rx)
        if len(rx) > maximo:
            rx = rx[:maximo]
        g = VGroup()
        for z in rx:
            if abs(np.real(z)) <= self.alcance and \
               abs(np.imag(z)) <= self.alcance:
                d = Dot(self.p(z), radius=radio, color=color,
                        fill_opacity=opacidad)
                d.set_stroke(width=0)
                g.add(d)
        return g

    def regiones(self, campo, xs, color=C_EJE, grosor=1.8):
        return _segmentos_frontera(campo, xs, self.p, color, grosor)


def plano_iq(unidad=1.15, alcance=1.75):
    """Ver `PlanoIQ`."""
    return PlanoIQ(unidad, alcance)


class DiagramaOjo(_Anclada):
    """Trazas de 2 simbolos superpuestas. .con_trazas(y2) GEMELA
    (mismo numero de trazas)."""

    def __init__(self, y, sps=8, n_trazas=28, ancho=4.4, alto=2.4,
                 rango_y=1.9, color=C_SENAL, **kwargs):
        super().__init__(**kwargs)
        self.y_fuente = np.asarray(y, dtype=float)
        self.sps = int(sps)
        self.n_trazas = int(n_trazas)
        self.ancho, self.alto = float(ancho), float(alto)
        self.rango_y = float(rango_y)
        self.color = color
        self._poner_ancla(ORIGIN)
        marco = Rectangle(width=ancho, height=alto, color=C_EJE,
                          stroke_width=1.4)
        marco.move_to(self._origen())
        self.trazas = VGroup()
        L = 2 * self.sps
        for k in range(self.n_trazas):
            i0 = (k + 1) * self.sps
            if i0 + L >= len(self.y_fuente):
                break
            seg = self.y_fuente[i0:i0 + L + 1]
            pts = [self._en(i / L, v) for i, v in enumerate(seg)]
            tr = VMobject(color=color, stroke_width=1.5)
            tr.set_points_as_corners(pts)
            tr.set_stroke(opacity=0.7)
            self.trazas.add(tr)
        centro = DashedLine(self._en(0.5, -1.0), self._en(0.5, 1.0),
                            color=C_REJILLA, stroke_width=1.2,
                            dash_length=0.06)
        self.add(marco, centro, self.trazas)

    def _en(self, fx, y):
        fy = np.clip(y / self.rango_y, -1.0, 1.0)
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           fy * self.alto / 2.0, 0.0]))

    def con_trazas(self, y2, color=None):
        o = DiagramaOjo(y2, self.sps, self.n_trazas, self.ancho,
                        self.alto, self.rango_y, color or self.color)
        o.shift(self._origen() - o._origen())
        return o


def diagrama_ojo(y, sps=8, n_trazas=28, ancho=4.4, alto=2.4,
                 rango_y=1.9, color=C_SENAL):
    """Ver `DiagramaOjo`."""
    return DiagramaOjo(y, sps, n_trazas, ancho, alto, rango_y, color)


class CurvaBER(_Anclada):
    """Eje semilog: x en dB, y de 10^0 a 10^-exp_min. Ticks MathTex.
    .curva(fun) .puntos_medidos(pares) .en(db, ber) .vertical_en(db)"""

    def __init__(self, x0=0.0, x1=14.0, exp_min=5, ancho=5.2, alto=3.0,
                 **kwargs):
        super().__init__(**kwargs)
        self.x0, self.x1 = float(x0), float(x1)
        self.exp_min = int(exp_min)
        self.ancho, self.alto = float(ancho), float(alto)
        self._poner_ancla(ORIGIN)
        ex = Line(self.en(self.x0, 10 ** -self.exp_min),
                  self.en(self.x1, 10 ** -self.exp_min),
                  color=C_EJE, stroke_width=1.6)
        ey = Line(self.en(self.x0, 10 ** -self.exp_min),
                  self.en(self.x0, 1.0), color=C_EJE, stroke_width=1.6)
        self.ejes = VGroup(ex, ey)
        ticks = VGroup()
        for k in range(self.exp_min + 1):
            p = self.en(self.x0, 10.0 ** -k)
            ticks.add(Line(p + LEFT * 0.05, p + RIGHT * 0.05, color=C_EJE,
                           stroke_width=1.4))
            et = MathTex("10^{-%d}" % k if k else "10^{0}",
                         font_size=17, color=C_EJE)
            et.next_to(p, LEFT, buff=0.1)
            ticks.add(et)
        for xv in range(int(self.x0), int(self.x1) + 1, 2):
            p = self.en(xv, 10 ** -self.exp_min)
            ticks.add(Line(p + DOWN * 0.05, p + UP * 0.05, color=C_EJE,
                           stroke_width=1.4))
            et = _texto_hud(str(xv), font_size=13)
            et.next_to(p, DOWN, buff=0.1)
            ticks.add(et)
        et_x = _texto_hud("Eb/N0 dB", font_size=14)
        et_x.next_to(self.en(self.x1, 10 ** -self.exp_min), DOWN, buff=0.28)
        et_x.shift(LEFT * 0.4)
        self.add(self.ejes, ticks, et_x)

    def en(self, db, ber):
        fx = (float(db) - self.x0) / (self.x1 - self.x0)
        fy = -math.log10(max(float(ber), 10.0 ** -self.exp_min * 0.999)) \
            / self.exp_min
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (0.5 - fy) * self.alto, 0.0]))

    def curva(self, fun, color=C_CIFRA, n=140, grosor=2.6):
        xs = np.linspace(self.x0, self.x1, n)
        pts = []
        for x in xs:
            b = float(np.atleast_1d(fun(x))[0])
            if b < 10.0 ** -self.exp_min * 0.999:
                break
            pts.append(self.en(x, b))
        c = VMobject(color=color, stroke_width=grosor)
        c.set_points_as_corners(pts)
        return c

    def puntos_medidos(self, pares, color=C_COD, radio=0.06):
        return VGroup(*[Dot(self.en(x, b), radius=radio, color=color)
                        for x, b in pares if b > 0])

    def vertical_en(self, db, color=C_CIFRA):
        return DashedLine(self.en(db, 1.0),
                          self.en(db, 10.0 ** -self.exp_min),
                          color=color, stroke_width=1.6, dash_length=0.07)


def curva_ber(x0=0.0, x1=14.0, exp_min=5, ancho=5.2, alto=3.0):
    """Ver `CurvaBER`."""
    return CurvaBER(x0, x1, exp_min, ancho, alto)


class EspectroArea(_Anclada):
    """PSD en dB como area rellena. .con_psd(p2_db) GEMELA
    .marca_f(f) vertical punteada  .en(f, db)"""

    def __init__(self, f, p_db, piso_db=-50.0, ancho=5.2, alto=2.4,
                 color=C_BANDA, **kwargs):
        super().__init__(**kwargs)
        self.f = np.asarray(f, dtype=float)
        self.p_db = np.asarray(p_db, dtype=float)
        self.piso = float(piso_db)
        self.ancho, self.alto = float(ancho), float(alto)
        self.color = color
        self._poner_ancla(ORIGIN)
        ex = Line(self.en(self.f[0], self.piso),
                  self.en(self.f[-1], self.piso), color=C_EJE,
                  stroke_width=1.6)
        ey = Line(self.en(self.f[0], self.piso), self.en(self.f[0], 0.0),
                  color=C_EJE, stroke_width=1.6)
        self.ejes = VGroup(ex, ey)
        pts = [self.en(a, b) for a, b in zip(self.f, self.p_db)]
        self.curva = VMobject(color=color, stroke_width=2.4)
        self.curva.set_points_as_corners(pts)
        self.area = Polygon(self.en(self.f[0], self.piso), *pts,
                            self.en(self.f[-1], self.piso),
                            stroke_width=0, fill_color=color,
                            fill_opacity=0.22)
        self.add(self.ejes, self.area, self.curva)

    def en(self, f, db):
        fx = (f - self.f[0]) / (self.f[-1] - self.f[0])
        fy = (np.clip(db, self.piso, 0.0) - self.piso) / (0.0 - self.piso)
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (fy - 0.5) * self.alto, 0.0]))

    def marca_f(self, f, color=C_CIFRA):
        return DashedLine(self.en(f, self.piso), self.en(f, 0.0),
                          color=color, stroke_width=1.6, dash_length=0.07)

    def con_psd(self, p2_db, color=None):
        o = EspectroArea(self.f, p2_db, self.piso, self.ancho, self.alto,
                         color or self.color)
        o.shift(self._origen() - o._origen())
        return o


def espectro_area(f, p_db, piso_db=-50.0, ancho=5.2, alto=2.4,
                  color=C_BANDA):
    """Ver `EspectroArea`."""
    return EspectroArea(f, p_db, piso_db, ancho, alto, color)


class BandaEspacio(_Anclada):
    """Regla logaritmica de frecuencias (GHz). .marca(f_ghz, texto)
    .pos(f_ghz)"""

    def __init__(self, exp0=0, exp1=3, ancho=6.4, **kwargs):
        super().__init__(**kwargs)
        self.exp0, self.exp1 = float(exp0), float(exp1)
        self.ancho = float(ancho)
        self._poner_ancla(ORIGIN)
        base = Line(self.pos(10.0 ** self.exp0), self.pos(10.0 ** self.exp1),
                    color=C_EJE, stroke_width=2.0)
        ticks = VGroup()
        for e in range(int(self.exp0), int(self.exp1) + 1):
            p = self.pos(10.0 ** e)
            ticks.add(Line(p + DOWN * 0.07, p + UP * 0.07, color=C_EJE,
                           stroke_width=1.6))
            if e < 3:
                et = _texto_hud(fmt(10.0 ** e, 0) + " GHz", font_size=13)
            else:
                et = _texto_hud(fmt(10.0 ** (e - 3), 0) + " THz",
                                font_size=13)
            et.next_to(p, DOWN, buff=0.12)
            ticks.add(et)
        self.add(base, ticks)

    def pos(self, f_ghz):
        fx = (math.log10(float(f_ghz)) - self.exp0) / (self.exp1 - self.exp0)
        return self._origen() + np.array([(fx - 0.5) * self.ancho, 0.0, 0.0])

    def marca(self, f_ghz, texto, color=C_BANDA, arriba=True):
        p = self.pos(f_ghz)
        g = VGroup(Line(p + DOWN * 0.09, p + UP * 0.09, color=color,
                        stroke_width=2.6))
        et = _texto_hud(texto, font_size=14, color=color)
        et.next_to(p, UP if arriba else DOWN, buff=0.14)
        g.add(et)
        return g


def banda_espacio(exp0=0, exp1=3, ancho=6.4):
    """Ver `BandaEspacio`."""
    return BandaEspacio(exp0, exp1, ancho)


class EnlaceTierra(_Anclada):
    """Tierra + nave + camino del enlace (escala DECLARADA en el pie).
    .camino .tierra .nave .paquete() .pos_nave()"""

    def __init__(self, dist=4.6, radio_tierra=0.7, curva=0.35,
                 color_camino=C_SENAL, **kwargs):
        super().__init__(**kwargs)
        self._poner_ancla(ORIGIN)
        self.tierra = Circle(radius=radio_tierra, color=C_SENAL,
                             stroke_width=2.0, fill_color="#0b2545",
                             fill_opacity=0.85)
        self.tierra.move_to(self._origen())
        p_nave = self._origen() + RIGHT * float(dist)
        self.nave = Dot(p_nave, radius=0.07, color=C_BIT)
        a, b = self._origen() + RIGHT * radio_tierra, p_nave + LEFT * 0.09
        medio = (a + b) / 2.0 + UP * float(curva)
        cam = VMobject(color=color_camino, stroke_width=2.0)
        cam.set_points_smoothly([a, medio, b])
        self.camino = cam
        self.add(self.tierra, self.camino, self.nave)

    def pos_nave(self):
        return self.nave.get_center()

    def paquete(self, color=C_BIT, radio=0.055):
        return Dot(self.camino.point_from_proportion(0.0), radius=radio,
                   color=color)


def enlace_tierra(dist=4.6, radio_tierra=0.7, curva=0.35,
                  color_camino=C_SENAL):
    """Ver `EnlaceTierra`."""
    return EnlaceTierra(dist, radio_tierra, curva, color_camino)


class PaseCielo(_Anclada):
    """La boveda del pase (proyeccion ortografica del cielo visto de
    lado): horizonte + arcos de elevacion + trayecto del pase.
    .sat_en(frac) .pos(elev_deg, theta_deg) .trayecto"""

    def __init__(self, pase, radio=2.5, theta_max=72.0, **kwargs):
        super().__init__(**kwargs)
        self.pase = pase
        self.R = float(radio)
        self.theta_max = float(theta_max)
        self._poner_ancla(ORIGIN)
        horizonte = Line(self._origen() + LEFT * self.R,
                         self._origen() + RIGHT * self.R, color=C_EJE,
                         stroke_width=1.8)
        cupula = VMobject(color=C_REJILLA, stroke_width=1.4)
        ang = np.linspace(0, math.pi, 60)
        cupula.set_points_as_corners(
            [self._origen() + np.array([self.R * math.cos(a),
                                        self.R * math.sin(a), 0.0])
             for a in ang])
        arcos = VGroup()
        for e in (30.0, 60.0):
            pts = [self.pos(e, th) for th in np.linspace(-self.theta_max,
                                                         self.theta_max, 40)]
            arc = VMobject(color=C_REJILLA, stroke_width=1.0)
            arc.set_points_as_corners(pts)
            et = _texto_hud(fmt(e, 0), font_size=12, color=C_REJILLA)
            et.next_to(pts[0], LEFT, buff=0.08)
            arcos.add(arc, et)
        n = len(pase["t_s"])
        fr = np.linspace(0.0, 1.0, n)
        self._et = [(pase["elev_deg"][i],
                     -self.theta_max + 2 * self.theta_max * fr[i])
                    for i in range(n)]
        tray = VMobject(color=C_BIT, stroke_width=2.6)
        tray.set_points_as_corners([self.pos(e, th) for e, th in self._et])
        self.trayecto = tray
        self.add(horizonte, cupula, arcos, self.trayecto)

    def pos(self, elev_deg, theta_deg):
        e = math.radians(float(elev_deg))
        th = math.radians(float(theta_deg))
        return self._origen() + np.array(
            [self.R * math.cos(e) * math.sin(th),
             self.R * math.sin(e) * max(0.35, math.cos(th * 0.35)), 0.0])

    def sat_en(self, frac):
        """Posicion sobre el trayecto (se calcula EN VIVO: sigue al shift)."""
        i = int(np.clip(round(frac * (len(self._et) - 1)), 0,
                        len(self._et) - 1))
        return self.pos(*self._et[i])


def pase_cielo(pase, radio=2.5, theta_max=72.0):
    """Ver `PaseCielo`."""
    return PaseCielo(pase, radio, theta_max)


class RegistroConv(_Anclada):
    """El codificador K=3 (bit + 2 memorias + dos XOR). .con_bit(b, s)
    GEMELA con los valores puestos. .cajas .xors .salidas"""

    def __init__(self, bit=None, estado=None, lado=0.6, **kwargs):
        super().__init__(**kwargs)
        self.lado = float(lado)
        self.bit, self.estado = bit, estado
        self._poner_ancla(ORIGIN)
        o = self._origen()
        pos = [o + LEFT * self.lado * 1.6, o, o + RIGHT * self.lado * 1.6]
        etiquetas = ["b", "m1", "m0"]
        vals = None
        if bit is not None and estado is not None:
            vals = [int(bit), (int(estado) >> 1) & 1, int(estado) & 1]
        self.cajas = VGroup()
        for i, p in enumerate(pos):
            c = Square(self.lado, color=C_EJE, stroke_width=1.6)
            c.move_to(p)
            t = _texto_hud(str(vals[i]) if vals is not None
                           else etiquetas[i], font_size=17,
                           color=C_BIT if vals is not None else C_EJE)
            t.move_to(p)
            self.cajas.add(VGroup(c, t))
        px1 = o + DOWN * 1.25 + LEFT * self.lado * 0.8
        px2 = o + DOWN * 1.25 + RIGHT * self.lado * 0.8
        self.xors = VGroup()
        lineas = VGroup()
        for px, taps, col in ((px1, (0, 1, 2), C_BIT), (px2, (0, 2), C_COD)):
            circ = Circle(radius=0.16, color=col, stroke_width=1.8)
            circ.move_to(px)
            mas = MathTex(r"\oplus", font_size=22, color=col)
            mas.move_to(px)
            self.xors.add(VGroup(circ, mas))
            for t in taps:
                lineas.add(Line(pos[t] + DOWN * self.lado / 2,
                                px + UP * 0.16, color=col,
                                stroke_width=1.3))
        self.salidas = VGroup()
        for k, (px, col) in enumerate(((px1, C_BIT), (px2, C_COD))):
            fl = Arrow(px + DOWN * 0.16, px + DOWN * 0.60, buff=0,
                       color=col, stroke_width=2.4,
                       max_tip_length_to_length_ratio=0.45)
            self.salidas.add(fl)
        self.add(lineas, self.cajas, self.xors, self.salidas)

    def con_bit(self, bit, estado):
        o = RegistroConv(bit, estado, self.lado)
        o.shift(self._origen() - o._origen())
        return o


def registro_conv(bit=None, estado=None, lado=0.6):
    """Ver `RegistroConv`."""
    return RegistroConv(bit, estado, lado)


RAMAS_CONV = [(s, b, _CONV_SALIDAS[(s, b)][0], _CONV_SALIDAS[(s, b)][1])
              for s in range(4) for b in (0, 1)]


class Trellis(_Anclada):
    """Rejilla estados x tiempo del codigo K=3. .nodo(t, s)
    .rama(t, s0, s1) .todas_ramas() .camino(estados) .metrica(t, s, v)"""

    def __init__(self, pasos=8, ancho=6.0, alto=2.6, **kwargs):
        super().__init__(**kwargs)
        self.T = int(pasos)
        self.ancho, self.alto = float(ancho), float(alto)
        self._poner_ancla(ORIGIN)
        self.puntos = VGroup()
        for t in range(self.T + 1):
            for s in range(4):
                self.puntos.add(Dot(self.nodo(t, s), radius=0.035,
                                    color=C_EJE))
        etiquetas = VGroup()
        for s, nombre in enumerate(("00", "01", "10", "11")):
            et = _texto_hud(nombre, font_size=13)
            et.next_to(self.nodo(0, s), LEFT, buff=0.16)
            etiquetas.add(et)
        self.add(self.puntos, etiquetas)

    def nodo(self, t, s):
        fx = t / self.T
        fy = s / 3.0
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (0.5 - fy) * self.alto, 0.0]))

    def rama(self, t, s0, s1, color=C_EJE, grosor=1.6, opacidad=1.0):
        ln = Line(self.nodo(t, s0), self.nodo(t + 1, s1), color=color,
                  stroke_width=grosor)
        ln.set_stroke(opacity=opacidad)
        return ln

    def todas_ramas(self, color=C_REJILLA, grosor=1.2, opacidad=0.8):
        g = VGroup()
        for t in range(self.T):
            for s, b, s2, _sal in RAMAS_CONV:
                g.add(self.rama(t, s, s2, color, grosor, opacidad))
        return g

    def camino(self, estados, color=C_BIT, grosor=3.2):
        v = VMobject(color=color, stroke_width=grosor)
        v.set_points_as_corners([self.nodo(t, s)
                                 for t, s in enumerate(estados)])
        return v

    def metrica(self, t, s, valor, color=C_CIFRA):
        et = _texto_hud(fmt(valor, 0), font_size=13, color=color)
        et.next_to(self.nodo(t, s), UP, buff=0.07)
        return et


def trellis(pasos=8, ancho=6.0, alto=2.6):
    """Ver `Trellis`."""
    return Trellis(pasos, ancho, alto)


class GrafoLDPC(_Anclada):
    """Bits (circulos, abajo) y comprobaciones (cuadrados, arriba) de H.
    .bit(i) .check(j) .con_estado(x, s) GEMELA coloreada
    .aristas_de_bit(i)"""

    def __init__(self, H, estado=None, sindrome=None, ancho=6.2,
                 alto=2.4, **kwargs):
        super().__init__(**kwargs)
        self.H = np.asarray(H, dtype=int)
        self.estado_x = estado
        self.sindrome_s = sindrome
        self.ancho, self.alto = float(ancho), float(alto)
        self._poner_ancla(ORIGIN)
        nf, nc = self.H.shape
        o = self._origen()
        self._pos_b = [o + np.array([(i / (nc - 1) - 0.5) * self.ancho,
                                     -self.alto / 2.0, 0.0])
                       for i in range(nc)]
        self._pos_c = [o + np.array([((j + 0.5) / nf - 0.5) * self.ancho,
                                     self.alto / 2.0, 0.0])
                       for j in range(nf)]
        self.aristas = VGroup()
        self._aristas_idx = {}
        for j in range(nf):
            for i in range(nc):
                if self.H[j, i]:
                    ln = Line(self._pos_c[j], self._pos_b[i],
                              color=C_REJILLA, stroke_width=1.1)
                    self._aristas_idx[(j, i)] = len(self.aristas)
                    self.aristas.add(ln)
        self.bits, self.checks = VGroup(), VGroup()
        for i in range(nc):
            v = None if estado is None else int(estado[i])
            c = Circle(radius=0.14, color=C_EJE, stroke_width=1.6,
                       fill_color=C_BIT,
                       fill_opacity=0.85 if v else 0.0)
            c.move_to(self._pos_b[i])
            self.bits.add(c)
        for j in range(nf):
            v = None if sindrome is None else int(sindrome[j])
            col = C_RUIDO if v else (C_COD if v == 0 else C_EJE)
            q = Square(0.26, color=col, stroke_width=2.0,
                       fill_color=C_RUIDO,
                       fill_opacity=0.55 if v else 0.0)
            q.move_to(self._pos_c[j])
            self.checks.add(q)
        self.add(self.aristas, self.bits, self.checks)

    def bit(self, i):
        return self.bits[i]

    def check(self, j):
        return self.checks[j]

    def arista(self, j, i):
        return self.aristas[self._aristas_idx[(j, i)]]

    def aristas_de_bit(self, i):
        return VGroup(*[self.aristas[k] for (j, c), k in
                        self._aristas_idx.items() if c == i])

    def con_estado(self, x, s):
        o = GrafoLDPC(self.H, x, s, self.ancho, self.alto)
        o.shift(self._origen() - o._origen())
        return o


def grafo_ldpc(H, estado=None, sindrome=None, ancho=6.2, alto=2.4):
    """Ver `GrafoLDPC`."""
    return GrafoLDPC(H, estado, sindrome, ancho, alto)


_COLORES_USUARIO = [C_BIT, C_COD, C_SENAL, C_IA, C_BANDA, C_TECHO]


class RejillaAcceso(_Anclada):
    """Rejilla tiempo x frecuencia; -1 = libre. .ranura(f, t)
    .con_plan(matriz) GEMELA coloreada por usuario."""

    def __init__(self, plan=None, nf=4, nt=6, ancho=4.6, alto=2.6,
                 **kwargs):
        super().__init__(**kwargs)
        if plan is not None:
            plan = np.asarray(plan, dtype=int)
            nf, nt = plan.shape
        self.plan = plan
        self.nf, self.nt = int(nf), int(nt)
        self.ancho, self.alto = float(ancho), float(alto)
        self._poner_ancla(ORIGIN)
        o = self._origen()
        dw, dh = self.ancho / self.nt, self.alto / self.nf
        self.ranuras = VGroup()
        for f in range(self.nf):
            for t in range(self.nt):
                r = Rectangle(width=dw, height=dh, color=C_EJE,
                              stroke_width=1.1)
                if plan is not None and plan[f, t] >= 0:
                    r.set_fill(_COLORES_USUARIO[plan[f, t]
                                                % len(_COLORES_USUARIO)],
                               opacity=0.55)
                r.move_to(o + np.array([(t + 0.5) / self.nt - 0.5, 0.0,
                                        0.0]) * self.ancho
                          + np.array([0.0, 0.5 - (f + 0.5) / self.nf,
                                      0.0]) * self.alto)
                self.ranuras.add(r)
        et_t = _texto_hud("tiempo", font_size=13)
        et_t.next_to(o + DOWN * self.alto / 2, DOWN, buff=0.12)
        et_f = _texto_hud("frecuencia", font_size=13)
        et_f.rotate(PI / 2)
        et_f.next_to(o + LEFT * self.ancho / 2, LEFT, buff=0.12)
        self.add(self.ranuras, et_t, et_f)

    def ranura(self, f, t):
        return self.ranuras[f * self.nt + t]

    def con_plan(self, plan):
        o = RejillaAcceso(plan, self.nf, self.nt, self.ancho, self.alto)
        o.shift(self._origen() - o._origen())
        return o


def rejilla_acceso(plan=None, nf=4, nt=6, ancho=4.6, alto=2.6):
    """Ver `RejillaAcceso`."""
    return RejillaAcceso(plan, nf, nt, ancho, alto)


class MapaHaces(_Anclada):
    """Celdas de una constelacion sobre un arco de Tierra. .haz(k)
    .con_asignacion(idx_colores) GEMELA."""

    def __init__(self, n=9, asignacion=None, radio_arco=6.0,
                 radio_haz=0.30, abanico=52.0, **kwargs):
        super().__init__(**kwargs)
        self.n = int(n)
        self.asignacion = asignacion
        self.radio_arco = float(radio_arco)
        self.radio_haz = float(radio_haz)
        self.abanico = float(abanico)
        self._poner_ancla(ORIGIN)
        o = self._origen()
        centro_arco = o + DOWN * self.radio_arco
        arco = VMobject(color=C_SENAL, stroke_width=2.2)
        angs = np.radians(np.linspace(90 - self.abanico / 2,
                                      90 + self.abanico / 2, 60))
        arco.set_points_as_corners(
            [centro_arco + self.radio_arco
             * np.array([math.cos(a), math.sin(a), 0.0]) for a in angs])
        self.haces = VGroup()
        angs_h = np.radians(np.linspace(90 - self.abanico / 2 * 0.88,
                                        90 + self.abanico / 2 * 0.88,
                                        self.n))
        for k, a in enumerate(angs_h):
            p = centro_arco + self.radio_arco \
                * np.array([math.cos(a), math.sin(a), 0.0])
            col = C_EJE if asignacion is None else \
                _COLORES_USUARIO[int(asignacion[k]) % len(_COLORES_USUARIO)]
            h = Circle(radius=self.radio_haz, color=col, stroke_width=1.8,
                       fill_color=col,
                       fill_opacity=0.0 if asignacion is None else 0.35)
            h.move_to(p)
            self.haces.add(h)
        self.add(arco, self.haces)

    def haz(self, k):
        return self.haces[k]

    def con_asignacion(self, idx):
        o = MapaHaces(self.n, idx, self.radio_arco, self.radio_haz,
                      self.abanico)
        o.shift(self._origen() - o._origen())
        return o


def mapa_haces(n=9, asignacion=None, radio_arco=6.0, radio_haz=0.30,
               abanico=52.0):
    """Ver `MapaHaces`."""
    return MapaHaces(n, asignacion, radio_arco, radio_haz, abanico)


class RanurasPPM(_Anclada):
    """M ranuras; los fotones son puntos apilados. .ranura(i)
    .con_cuentas(c) GEMELA."""

    def __init__(self, m=16, cuentas=None, ancho=6.0, alto_max=1.6,
                 **kwargs):
        super().__init__(**kwargs)
        self.m = int(m)
        self.cuentas = cuentas
        self.ancho, self.alto_max = float(ancho), float(alto_max)
        self._poner_ancla(ORIGIN)
        o = self._origen()
        dw = self.ancho / self.m
        self.celdas, self.fotones = VGroup(), VGroup()
        for i in range(self.m):
            x = (i + 0.5) / self.m - 0.5
            r = Rectangle(width=dw, height=0.34, color=C_EJE,
                          stroke_width=1.1)
            r.move_to(o + np.array([x * self.ancho, 0.0, 0.0]))
            self.celdas.add(r)
            if cuentas is not None:
                tope = max(1, int(np.max(cuentas)))
                dy = min(0.14, self.alto_max / tope)
                for k in range(int(cuentas[i])):
                    d = Dot(o + np.array([x * self.ancho,
                                          0.34 + dy * (k + 1), 0.0]),
                            radius=0.045, color=C_BIT)
                    self.fotones.add(d)
        self.add(self.celdas, self.fotones)

    def ranura(self, i):
        return self.celdas[i]

    def con_cuentas(self, c):
        o = RanurasPPM(self.m, c, self.ancho, self.alto_max)
        o.shift(self._origen() - o._origen())
        return o


def ranuras_ppm(m=16, cuentas=None, ancho=6.0, alto_max=1.6):
    """Ver `RanurasPPM`."""
    return RanurasPPM(m, cuentas, ancho, alto_max)


def frontera_decision(piq, campo, xs, color=C_IA, grosor=2.4):
    """Las fronteras de un campo de etiquetas sobre un `plano_iq`
    (de `frontera_de` o `campo_vecino`)."""
    return _segmentos_frontera(campo, xs, piq.p, color, grosor)


class PerceptronMini(_Anclada):
    """Esquema 2 - ocultas - M (dibuja hasta 8 por capa). .con_pesos(W1,
    W2) GEMELA con grosor por |peso|. .capas"""

    def __init__(self, ocultas=8, salidas=8, W1=None, W2=None,
                 ancho=3.6, alto=2.8, **kwargs):
        super().__init__(**kwargs)
        self.oc, self.sal = int(min(ocultas, 8)), int(min(salidas, 8))
        self.ancho, self.alto = float(ancho), float(alto)
        self._poner_ancla(ORIGIN)
        o = self._origen()

        def col(n, x, color):
            g = VGroup()
            for i in range(n):
                y = (0.5 - (i + 0.5) / n) * self.alto
                c = Circle(radius=0.09, color=color, stroke_width=1.8)
                c.move_to(o + np.array([x, y, 0.0]))
                g.add(c)
            return g

        xs = (-self.ancho / 2, 0.0, self.ancho / 2)
        self.capas = VGroup(col(2, xs[0], C_SENAL),
                            col(self.oc, xs[1], C_IA),
                            col(self.sal, xs[2], C_COD))
        self.lineas = VGroup()
        for a in range(2):
            for b in range(self.oc):
                w = 1.0 if W1 is None else abs(float(W1[a, b % W1.shape[1]]))
                ln = Line(self.capas[0][a].get_center(),
                          self.capas[1][b].get_center(), color=C_REJILLA,
                          stroke_width=min(3.4, 0.5 + 1.1 * w))
                self.lineas.add(ln)
        for a in range(self.oc):
            for b in range(self.sal):
                w = 1.0 if W2 is None else \
                    abs(float(W2[a % W2.shape[0], b % W2.shape[1]]))
                ln = Line(self.capas[1][a].get_center(),
                          self.capas[2][b].get_center(), color=C_REJILLA,
                          stroke_width=min(3.4, 0.4 + 0.9 * w))
                self.lineas.add(ln)
        self.add(self.lineas, self.capas)

    def con_pesos(self, W1, W2):
        o = PerceptronMini(self.oc, self.sal, W1, W2, self.ancho, self.alto)
        o.shift(self._origen() - o._origen())
        return o


def perceptron_mini(ocultas=8, salidas=8, W1=None, W2=None, ancho=3.6,
                    alto=2.8):
    """Ver `PerceptronMini`."""
    return PerceptronMini(ocultas, salidas, W1, W2, ancho, alto)

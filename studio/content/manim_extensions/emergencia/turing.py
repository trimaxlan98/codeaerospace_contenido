# =====================================================================
# emergencia/turing.py — clip 05 "manchas y rayas".
#
# Que simula: reaccion-difusion de Gray-Scott en la malla 270x480 ENTERA
# (una celda = un pixel; no hay reescalado). De una unica semilla central
# nace un frente de manchas que se come el lienzo; a mitad de pelicula los
# parametros (f, k) se deslizan de forma CONTINUA de los de MANCHAS a los
# de RAYAS/LABERINTO y el patron ya formado se reorganiza en dedos y lazos
# sin volver a empezar. La misma quimica, otra regla.
#
# Reglas (las que el clip pone como HUD):
#   U + 2V -> 3V (autocatalisis); V -> P (se va)
#   dU/dt = Du*lap(U) - U*V^2 + f*(1-U)
#   dV/dt = Dv*lap(V) + U*V^2 - (f+k)*V
#   Du=0.2097, Dv=0.1050, dt=1, frontera periodica (Pearson 1993).
#
# Reutiliza los valores YA MEDIDOS de `naturaleza.py` de este mismo repo
# (`TURING_MANCHAS`, `TURING_RAYAS`, Du/Dv/dt y la normalizacion V/0.40).
# NO se importa naturaleza.py porque ese modulo importa manim en su cabecera
# y un simulador de `emergencia` tiene que correr sin manim (la sonda no lo
# tiene). Las constantes van copiadas con su procedencia; el integrador es
# el mismo laplaciano de 5 puntos con np.roll.
#
# Diferencia deliberada con naturaleza.py: alli el estado inicial son 24
# parches repartidos (para llenar el lienzo rapido); aqui es UNA semilla
# central, porque el clip quiere ver el frente creciendo.
#
# Color: LUT "orden" (violeta) sobre `C_FONDO`, con un smoothstep de
# contraste; el rango es FIJO (V/0.40) para que el color no palpite entre
# frames.
#
# Coste medido en el contenedor (2026-08-28): T=800 frames x 40 pasos de
# integracion = 32.000 pasos, 45 s (con U,V en float32; en float64 eran
# 100 s y no cabia en el presupuesto). La pila pesa 311 MB (800,480,270,3).
#
# Cifras (medidas sobre lo simulado):
#   lambda_manchas_celdas / _px   longitud de onda del patron al final de la
#                                 fase de manchas, por el pico del espectro
#                                 radial (FFT 2D). Celdas y pixeles COINCIDEN
#                                 porque la malla es la imagen.
#   lambda_rayas_celdas / _px     idem al final de la fase de rayas
#   n_manchas                     componentes conexas de V por encima del
#                                 umbral al final de la fase 1
#
# Valores con los parametros por defecto (semilla=1): lambda_manchas =
# 15.32 px, lambda_rayas = 13.34 px, n_manchas = 186. Comprobado en el
# espacio real: la mediana de la distancia al vecino mas cercano entre
# los 186 centroides es 15.58 px (1.7 % del valor de la FFT).
# =====================================================================
import numpy as np

from . import LUTS, colorear, validar_pila

# --- constantes medidas, copiadas de studio/content/manim_extensions/naturaleza.py
DU, DV, DT = 0.2097, 0.1050, 1.0          # Pearson 1993, en unidades de malla
TURING_MANCHAS = (0.0367, 0.0649)         # (f, k): leopardo
TURING_RAYAS = (0.0300, 0.0570)           # (f, k): laberinto / cebra
V_REF = 0.40                              # normalizador de V (naturaleza.py)

LAMBDA_MIN, LAMBDA_MAX = 3.0, 60.0        # ventana de busqueda del pico, celdas


def _laplaciano(Z):
    return (np.roll(Z, 1, 0) + np.roll(Z, -1, 0)
            + np.roll(Z, 1, 1) + np.roll(Z, -1, 1) - 4.0 * Z)


def _avanza(U, V, f, k, pasos):
    for _ in range(int(pasos)):
        UVV = U * V * V
        U = U + DT * (DU * _laplaciano(U) - UVV + f * (1.0 - U))
        V = V + DT * (DV * _laplaciano(V) + UVV - (f + k) * V)
    return U, V


def _semilla_central(H, W, radio, semilla):
    """U=1, V=0 en todo el lienzo salvo un cuadrado central sembrado.

    El ruido en U es global y minusculo (rompe la simetria exacta cuando el
    frente llega); el ruido en V va SOLO dentro de la semilla, porque V!=0
    en cualquier sitio nuclearia el patron alli y el frente dejaria de
    nacer del centro.
    """
    rng = np.random.default_rng(int(semilla))
    U = np.ones((H, W), dtype=np.float32)
    V = np.zeros((H, W), dtype=np.float32)
    r = int(radio)
    cy, cx = H // 2, W // 2
    U[cy - r:cy + r, cx - r:cx + r] = 0.50
    V[cy - r:cy + r, cx - r:cx + r] = 0.25
    U += rng.normal(0, 0.01, U.shape).astype(np.float32)
    V[cy - r:cy + r, cx - r:cx + r] += rng.normal(
        0, 0.02, (2 * r, 2 * r)).astype(np.float32)
    # float32: 3x mas rapido que float64 en el contenedor (1.4 vs 4.2 ms
    # por paso) y el patron es un atractor, no una trayectoria: la
    # precision no cambia ni la longitud de onda ni la cuenta de manchas.
    return np.clip(U, 0, 1.2), np.clip(V, 0, 1.0)


def _suave(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _fk_por_frame(T, frame_cambio, transicion, manchas, rayas):
    """(T,2) con (f,k) de cada frame: rampa smoothstep entre los dos juegos."""
    i = np.arange(T, dtype=np.float64)
    s = _suave((i - frame_cambio) / max(int(transicion), 1))
    f = manchas[0] + (rayas[0] - manchas[0]) * s
    k = manchas[1] + (rayas[1] - manchas[1]) * s
    return np.stack([f, k], axis=1)


def _lambda_pico(V):
    """Longitud de onda dominante (celdas) por el pico del espectro radial.

    Se le quita la media y se le aplica una ventana de Hann 2D (el patron
    puede no llegar a los bordes; sin ventana el borde del frente mete una
    raya falsa en el espectro). La potencia se acumula en anillos de
    frecuencia radial y el pico se refina con el centroide de sus 5 bins.
    La busqueda se limita a longitudes de onda de 3 a 60 celdas: por debajo
    es la malla, por encima es el tamaño del frente, no el patron.
    """
    H, W = V.shape
    a = np.asarray(V, dtype=np.float64)
    a = a - a.mean()
    a = a * np.hanning(H)[:, None] * np.hanning(W)[None, :]
    P = np.abs(np.fft.fft2(a)) ** 2
    qy = np.fft.fftfreq(H)[:, None]
    qx = np.fft.fftfreq(W)[None, :]
    q = np.sqrt(qy ** 2 + qx ** 2)
    paso = 1.0 / max(H, W)
    idx = np.round(q / paso).astype(np.int64)
    nb = idx.max() + 1
    pot = np.bincount(idx.ravel(), weights=P.ravel(), minlength=nb)
    qs = np.arange(nb) * paso
    ok = (qs >= 1.0 / LAMBDA_MAX) & (qs <= 1.0 / LAMBDA_MIN)
    if not ok.any() or pot[ok].max() <= 0:
        return float("nan")
    j = int(np.argmax(np.where(ok, pot, -np.inf)))
    lo, hi = max(j - 2, 1), min(j + 3, nb)
    w = pot[lo:hi]
    q_pico = float((qs[lo:hi] * w).sum() / w.sum()) if w.sum() > 0 else qs[j]
    return float(1.0 / q_pico) if q_pico > 0 else float("nan")


def _contar_manchas(V, area_min=4):
    """Componentes conexas de V por encima del umbral (scipy si esta;
    si no, un etiquetado por union de vecinos con np.minimum.at).

    Umbral = mitad del percentil 99 de V: separa las manchas del medio
    saturado sin depender de la escala absoluta."""
    umbral = 0.5 * float(np.percentile(V, 99.0))
    if umbral <= 1e-6:
        return 0, umbral
    m = V > umbral
    if not m.any():
        return 0, umbral
    try:
        from scipy import ndimage
        etq, n = ndimage.label(m)
        if n == 0:
            return 0, umbral
        areas = np.bincount(etq.ravel())[1:]
        return int((areas >= area_min).sum()), umbral
    except ImportError:
        pass
    # Reserva: propagacion iterativa de etiquetas (sin scipy).
    etq = np.where(m, np.arange(m.size).reshape(m.shape), -1)
    for _ in range(4 * max(m.shape)):
        v = etq.copy()
        for eje, giro in ((0, 1), (0, -1), (1, 1), (1, -1)):
            v = np.maximum(v, np.where(m, np.roll(etq, giro, eje), -1))
        v = np.where(m, v, -1)
        if np.array_equal(v, etq):
            break
        etq = v
    vals, cuenta = np.unique(etq[m], return_counts=True)
    return int((cuenta >= area_min).sum()), umbral


def _pintar(V, lo, hi):
    t = _suave((np.clip(V / V_REF, 0.0, 1.0) - lo) / max(hi - lo, 1e-6))
    return colorear(t, LUTS["orden"], vmin=0.0, vmax=1.0)


def _correr(pasos, res, semilla, pasos_por_frame, manchas, rayas,
            frames_transicion, radio_semilla, contraste, con_frames):
    W, H = int(res[0]), int(res[1])
    if H * 9 != W * 16:
        raise ValueError(f"res {res} no es 9:16 (H*9 tiene que ser W*16)")
    T = int(pasos)
    frame_cambio = T // 2
    fk = _fk_por_frame(T, frame_cambio, frames_transicion, manchas, rayas)
    U, V = _semilla_central(H, W, radio_semilla, semilla)
    lo, hi = float(contraste[0]), float(contraste[1])

    frames = (np.empty((T, H, W, 3), dtype=np.uint8) if con_frames else None)
    v_media = np.empty(T, dtype=np.float64)
    lam_manchas = n_manchas = umbral = None
    for k in range(T):
        if con_frames:
            frames[k] = _pintar(V, lo, hi)
        v_media[k] = float(V.mean())
        if k == frame_cambio - 1:
            lam_manchas = _lambda_pico(V)
            n_manchas, umbral = _contar_manchas(V)
        U, V = _avanza(U, V, float(fk[k, 0]), float(fk[k, 1]),
                       pasos_por_frame)
    lam_rayas = _lambda_pico(V)

    return dict(frames=frames, fk=fk, v_media=v_media,
                frame_cambio=frame_cambio,
                frame_fin_transicion=min(frame_cambio + int(frames_transicion),
                                         T - 1),
                lam_manchas=lam_manchas, lam_rayas=lam_rayas,
                n_manchas=n_manchas, umbral=umbral,
                centro_semilla=(W / 2.0, H / 2.0))


def _cifras(d):
    return {
        "lambda_manchas_celdas": d["lam_manchas"],
        "lambda_manchas_px": d["lam_manchas"],
        "lambda_rayas_celdas": d["lam_rayas"],
        "lambda_rayas_px": d["lam_rayas"],
        "n_manchas": d["n_manchas"],
    }


def simular(semilla=1, pasos=800, res=(270, 480), pasos_por_frame=40,
            manchas=TURING_MANCHAS, rayas=TURING_RAYAS,
            frames_transicion=60, radio_semilla=12, contraste=(0.12, 0.62)):
    """Gray-Scott de manchas a rayas. T = `pasos` frames (800 por defecto),
    `pasos_por_frame` pasos de integracion en cada uno (40 -> 32.000 pasos).

    La mitad de la pelicula corre con `manchas` (f,k); a partir del frame
    T//2 los parametros se deslizan con un smoothstep de `frames_transicion`
    hasta `rayas` y siguen alli hasta el final.

    Devuelve dict(frames, cifras, extra).

    extra:
      frame_cambio           frame en que empiezan a moverse (f, k)
      frame_fin_transicion   frame en que ya son los de rayas
      fk_por_frame           (T,2) el par (f,k) de cada frame: el HUD de la regla
      pasos_por_frame        pasos de integracion por frame
      centro_semilla         (x,y) px de la semilla inicial
      v_media_por_frame      (T,) media de V: la curva de cuanto se ha llenado
      umbral_manchas         umbral de V con que se contaron las manchas
    """
    d = _correr(pasos, res, semilla, int(pasos_por_frame), manchas, rayas,
                frames_transicion, radio_semilla, contraste, True)
    return dict(
        frames=validar_pila(d["frames"]),
        cifras=_cifras(d),
        extra={
            "frame_cambio": d["frame_cambio"],
            "frame_fin_transicion": d["frame_fin_transicion"],
            "fk_por_frame": d["fk"],
            "pasos_por_frame": int(pasos_por_frame),
            "centro_semilla": d["centro_semilla"],
            "v_media_por_frame": d["v_media"],
            "umbral_manchas": d["umbral"],
        },
    )


def medir(semilla=1, pasos=800, res=(270, 480), pasos_por_frame=40,
          manchas=TURING_MANCHAS, rayas=TURING_RAYAS,
          frames_transicion=60, radio_semilla=12, contraste=(0.12, 0.62)):
    """Solo las cifras (sin pintar frames), para la sonda."""
    d = _correr(pasos, res, semilla, int(pasos_por_frame), manchas, rayas,
                frames_transicion, radio_semilla, contraste, False)
    return _cifras(d)

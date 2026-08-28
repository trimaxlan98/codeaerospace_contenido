# =====================================================================
# emergencia/bandada.py — clip 01 "la bandada" (curso 29, vertical).
#
# QUE SIMULA
# 2500 boids (Reynolds 1986) en un lienzo 9:16. Cada agente solo mira a los
# vecinos que caen dentro de su radio de percepcion; no hay ninguna regla
# global, ningun lider y ninguna trayectoria escrita a mano. Del ruido
# inicial (posiciones y rumbos al azar) nace una bandada coherente que
# ondula, se estira en filamentos y gira contra los bordes.
#
# LAS REGLAS (las tres que el clip pone como HUD)
#   SEPARACION  apartate del vecino que tienes encima      (radio 3 px)
#   ALINEACION  apunta a donde apunta tu vecindario        (radio 15 px)
#   COHESION    ve hacia el centro de tu vecindario        (radio 15 px)
# Mas dos terminos de ambiente que NO son reglas del modelo: ruido de rumbo
# (la temperatura del enjambre) y repulsion suave de los bordes.
#
# BORDES: repulsion suave, no periodicos. Con toroide la bandada se parte al
# cruzar el borde y la trayectoria del agente seguido SALTA (la camara daria
# un tiron); con repulsion suave la bandada rebota, ondula y la trayectoria
# es continua. Mejor imagen y mejor camara.
#
# VECINOS POR REJILLA ESPACIAL, O(n)
# Dos rejillas (una por radio). En cada una: `np.bincount` cuenta por celda,
# un `argsort` estable ordena los agentes por celda y se arma una tabla
# (celda, K) con los ids; despues se recorren las 3x3 celdas de alrededor,
# nueve desplazamientos vectorizados sobre esa tabla. Ningun bucle Python
# por agente y ninguna matriz n x n.
#
# Se probaron antes las sumas por celda directas (bincount de x, y, vx, vy y
# caja 3x3, sin listas de pares). Son mas baratas pero MIENTEN en la imagen:
#   - la lectura por celda hace que la fuerza salte al cruzar una frontera y
#     los agentes se ordenan en filas: sale un "peine" de una celda de paso,
#     bien visible a 270x480 (se arregla con deposito/lectura bilineales);
#   - el vecindario deja de ser un circulo y pasa a ser un cuadrado de tres
#     celdas: la bandada acaba con bordes RECTOS y esquinas;
#   - y sobre todo, sin distancias no hay separacion 1/d: con la direccion
#     normalizada cualquier asimetria minuscula da fuerza plena y el enjambre
#     CRISTALIZA en una malla hexagonal que viaja en bloque. Bonita, pero no
#     es una bandada.
# Con pares exactos (distancia real, separacion 1/d) sale la murmuracion.
# El tope K por celda trunca los vecindarios muy densos; por eso la rejilla
# de separacion usa celdas del tamaño de su radio (1-2 agentes por celda) y
# la de percepcion promedia (media, no suma: truncar no la sesga).
#
# COLOR POR ROL: los 2500 agentes en verde C_VIVO (lo vivo) con estela corta
# (decaimiento 0.62) para que se lea el rumbo; UN agente en ambar C_REGLA
# (el que sigue la camara), mas grande.
#
# PARAMETROS
#   simular(semilla=1, pasos=900, res=(270, 480), agentes=2500)
# `res` admite (270,480) por defecto y (360,640) si el clip hace zoom. La
# simulacion vive en unidades de mundo (ancho 1, alto 16/9) y solo el
# pintado depende de `res`: las cifras NO cambian con la resolucion.
# T = 900 frames = 30 pasos/s x 30 s simulados (la pieza dura 30 s).
#
# COSTE medido en el contenedor (2026-08-28, 2500 agentes, 900 pasos):
#   res (270,480): 31 s de CPU, pila de 350 MB   (presupuesto: 90 s / 1 GB)
#   res (360,640): 39 s de CPU, pila de 622 MB
#   medir() (sin pintar): 18 s
#
# CIFRAS (medidas sobre lo simulado)
#   polarizacion_inicial  |<v_hat>| en el primer frame
#   polarizacion_final    |<v_hat>| en el ultimo frame
#   frame_umbral_0_8      primer frame con polarizacion > 0.8 (-1 si nunca)
#   segundos_umbral_0_8   ese frame en segundos simulados
#   agentes               2500
# Con semilla=1: 0.032 -> 0.931, umbral 0.8 en el frame 351 (11.7 s), y la
# media de los ultimos 30 frames es 0.931 (el final no es un pico suelto).
#
# OJO CON LA SEMILLA: en una caja cerrada el orden es TRANSITORIO. La
# bandada se ordena, choca con un borde, se parte y se vuelve a ordenar, asi
# que la polarizacion oscila entre ~0.2 y ~0.95 despues de nacer y el valor
# del ultimo frame depende de la semilla. Medido a 900 pasos: semillas 1, 2
# y 4 cruzan 0.8 (frames 351, 382, 304) y la 3 no lo cruza; terminan en
# 0.93, 0.06, 0.31 y 0.95. La 1 (la de por defecto) da la pieza completa:
# nace a los 11.7 s y termina ordenada.
#
# EXTRA
#   seguido        (T,2) float32, trayectoria del agente ambar EN PIXELES
#                  (x, y) del frame; lista para `seguir(...)` del nucleo.
#   polarizacion   (T,) float32, la cifra frame a frame (para el HUD vivo).
#   indice_seguido int, quien es el agente ambar.
#   res            (W, H) con la que se pinto.
#   pasos_por_segundo  30 (para pasar de frames a segundos simulados).
# =====================================================================
import numpy as np

from . import (C_REGLA, C_VIVO, a_uint8, estela, mezclar_capas,
               salpicar, validar_pila)

PASOS_POR_SEGUNDO = 30

# --- Parametros del modelo, en unidades de mundo (ancho = 1) --------------
R_PERCEPCION = 0.055      # radio de alineacion y cohesion (~15 px)
R_SEPARACION = 0.012      # radio de separacion (~3 px)
RAPIDEZ = 0.0060          # modulo de la velocidad, constante (mundo/paso)
GIRO = 0.115              # cuanto puede torcer el rumbo en un paso

W_SEPARACION = 1.00
W_ALINEACION = 4.50
W_COHESION = 0.30
W_BORDE = 12.00
W_RUIDO = 1.20            # temperatura: sin ella el enjambre cristaliza
TOPE_SEPARACION = 3.0     # tope del modulo de la separacion (1/d diverge)

MARGEN = 0.20             # franja donde el borde empuja hacia dentro
K_PERCEPCION = 24         # agentes por celda que caben en la tabla
K_SEPARACION = 8

# --- Pintado --------------------------------------------------------------
DECAIMIENTO = 0.62        # estela corta: se lee el rumbo, no se emborrona
DECAIMIENTO_SEGUIDO = 0.86
PESO_AGENTE = 0.60
RADIO_AGENTE = 1.0
PESO_SEGUIDO = 1.10
RADIO_SEGUIDO = 2.2


def _tono(lienzo):
    """Recorta el brillo SIN cambiar el tono: divide por el canal mas alto
    solo cuando pasa de 1. Con el recorte plano de `a_uint8` (canal a canal)
    los nucleos densos de la bandada saturan los tres canales y salen
    BLANCOS tirando a cian — y el cian es el rol de "lo medido": el color
    mentiria. Asi el nucleo denso queda en verde puro a pleno brillo y lo
    que no llega a saturar no se toca."""
    m = lienzo.max(axis=2, keepdims=True)
    return lienzo / np.maximum(1.0, m)


def _tabla_celdas(pos, celda, nx, ny, K):
    """Rejilla espacial: celda de cada agente y tabla (celdas, K) de ids.

    `np.bincount` da los agentes por celda y un `argsort` estable los ordena
    por celda, asi que el puesto de cada uno dentro de su celda sale de una
    resta. La rejilla lleva un borde de una celda para que los nueve
    desplazamientos 3x3 nunca se salgan. O(n log n) por el argsort, sin
    ningun bucle por agente.
    """
    ancho, alto = nx + 2, ny + 2
    ix = np.clip((pos[:, 0] / celda).astype(np.int64), 0, nx - 1) + 1
    iy = np.clip((pos[:, 1] / celda).astype(np.int64), 0, ny - 1) + 1
    cid = iy * ancho + ix
    orden = np.argsort(cid, kind="stable")
    cuenta = np.bincount(cid, minlength=ancho * alto)
    inicio = np.concatenate([[0], np.cumsum(cuenta)[:-1]])
    puesto = np.arange(len(orden)) - inicio[cid[orden]]
    tabla = np.full((ancho * alto, K), -1, dtype=np.int64)
    cabe = puesto < K
    tabla[cid[orden][cabe], puesto[cabe]] = orden[cabe]
    return cid, tabla, ancho


def _normalizar(v):
    """(n,2) -> vectores unitarios; el vector nulo se queda nulo."""
    n = np.sqrt(v[:, 0] ** 2 + v[:, 1] ** 2)[:, None]
    return np.divide(v, n, out=np.zeros_like(v), where=n > 1e-9)


def _topar(v, tope):
    """Acorta los vectores mas largos que `tope`, deja los demas igual."""
    n = np.sqrt(v[:, 0] ** 2 + v[:, 1] ** 2)[:, None]
    return v * np.where(n > tope, tope / np.maximum(n, 1e-12), 1.0)


def _paso(pos, vel, rng, alto_mundo):
    """Un paso del modelo. Modifica `pos` y `vel` en sitio."""
    n = pos.shape[0]

    # --- vecindario de percepcion: alineacion y cohesion ------------------
    r = R_PERCEPCION
    cid, tabla, ancho = _tabla_celdas(
        pos, r, max(3, int(np.ceil(1.0 / r))),
        max(3, int(np.ceil(alto_mundo / r))), K_PERCEPCION)
    cnt = np.zeros(n, dtype=np.float32)
    suma = np.zeros((n, 4), dtype=np.float32)   # dx, dy, vx, vy
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            j = tabla[cid + dy * ancho + dx]
            jj = np.where(j >= 0, j, 0)
            ddx = pos[jj, 0] - pos[:, 0, None]
            ddy = pos[jj, 1] - pos[:, 1, None]
            d2 = ddx * ddx + ddy * ddy
            m = (j >= 0) & (d2 < r * r) & (d2 > 1e-12)
            cnt += m.sum(1)
            suma[:, 0] += (ddx * m).sum(1)
            suma[:, 1] += (ddy * m).sum(1)
            suma[:, 2] += (vel[jj, 0] * m).sum(1)
            suma[:, 3] += (vel[jj, 1] * m).sum(1)
    hay = cnt > 0.5
    c = np.where(hay, cnt, np.float32(1.0))[:, None]
    # cohesion: hacia el centro del vecindario, SIN normalizar (solo topada).
    # Normalizada convierte cualquier asimetria minuscula en fuerza plena.
    cohesion = _topar(suma[:, :2] / c / r, 1.0) * hay[:, None]
    alineacion = _normalizar(suma[:, 2:] / c) * hay[:, None]

    # --- vecindario de separacion: 1/d, celdas del tamaño del radio -------
    rs = R_SEPARACION
    cid2, tabla2, ancho2 = _tabla_celdas(
        pos, rs, max(3, int(np.ceil(1.0 / rs))),
        max(3, int(np.ceil(alto_mundo / rs))), K_SEPARACION)
    sep = np.zeros((n, 2), dtype=np.float32)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            j = tabla2[cid2 + dy * ancho2 + dx]
            jj = np.where(j >= 0, j, 0)
            ddx = pos[jj, 0] - pos[:, 0, None]
            ddy = pos[jj, 1] - pos[:, 1, None]
            d2 = ddx * ddx + ddy * ddy
            m = (j >= 0) & (d2 < rs * rs) & (d2 > 1e-12)
            inv = np.where(m, 1.0 / np.maximum(d2, np.float32(1e-9)),
                           np.float32(0.0))
            sep[:, 0] -= (ddx * inv).sum(1)
            sep[:, 1] -= (ddy * inv).sum(1)
    separacion = _topar(sep * rs, TOPE_SEPARACION)

    # --- borde blando: empuja hacia dentro dentro de la franja MARGEN -----
    borde = np.empty_like(pos)
    borde[:, 0] = (np.maximum(0.0, MARGEN - pos[:, 0])
                   - np.maximum(0.0, pos[:, 0] - (1.0 - MARGEN))) / MARGEN
    borde[:, 1] = (np.maximum(0.0, MARGEN - pos[:, 1])
                   - np.maximum(0.0,
                                pos[:, 1] - (alto_mundo - MARGEN))) / MARGEN

    acc = (W_SEPARACION * separacion + W_ALINEACION * alineacion
           + W_COHESION * cohesion + W_BORDE * borde
           + W_RUIDO * rng.normal(size=(n, 2)).astype(np.float32))
    vel += GIRO * RAPIDEZ * acc
    vel[:] = _normalizar(vel) * RAPIDEZ
    pos += vel
    np.clip(pos[:, 0], 0.0, 1.0, out=pos[:, 0])
    np.clip(pos[:, 1], 0.0, alto_mundo, out=pos[:, 1])


def _polarizacion(vel):
    """|<v_hat>|: 0 = rumbos al azar, 1 = todos apuntan igual."""
    m = _normalizar(vel).mean(axis=0)
    return float(np.sqrt(m[0] ** 2 + m[1] ** 2))


def _arranque(rng, n, alto_mundo):
    # float32 a proposito: el paso es memoria pura (tablas (n,K) de vecinos)
    # y en float64 cuesta casi el doble. Con pasos de 0.006 en un mundo de
    # 1.0, el error acumulado en 900 pasos es ~1e-5 px: invisible.
    pos = np.empty((n, 2), dtype=np.float32)
    pos[:, 0] = rng.uniform(0.06, 0.94, size=n)
    pos[:, 1] = rng.uniform(0.06, alto_mundo - 0.06, size=n)
    ang = rng.uniform(0.0, 2 * np.pi, size=n)
    vel = (np.stack([np.cos(ang), np.sin(ang)], axis=1)
           * RAPIDEZ).astype(np.float32)
    return pos, vel


def _recorrer(semilla, pasos, agentes, pintar):
    """Motor comun de `simular` y `medir`. `pintar(k, pos, seguido)` o None."""
    rng = np.random.default_rng(semilla)
    alto_mundo = 16.0 / 9.0
    pos, vel = _arranque(rng, agentes, alto_mundo)
    pol = np.empty(pasos, dtype=np.float32)
    traza = np.empty((pasos, 2), dtype=np.float64)
    seguido = 0
    for k in range(pasos):
        pol[k] = _polarizacion(vel)
        traza[k] = pos[seguido]
        if pintar is not None:
            pintar(k, pos, seguido)
        _paso(pos, vel, rng, alto_mundo)
    return pol, traza, seguido


def _cifras(pol, agentes):
    umbral = np.nonzero(pol > 0.8)[0]
    fu = int(umbral[0]) if umbral.size else -1
    return {
        "polarizacion_inicial": round(float(pol[0]), 3),
        "polarizacion_final": round(float(pol[-1]), 3),
        "frame_umbral_0_8": fu,
        "segundos_umbral_0_8": (round(fu / PASOS_POR_SEGUNDO, 1)
                                if fu >= 0 else -1.0),
        "agentes": int(agentes),
    }


def simular(semilla=1, pasos=900, res=(270, 480), agentes=2500):
    """Boids: del ruido nace una bandada. frames + cifras + extra.

    frames: uint8 (T, H, W, 3), agentes verdes con estela, el seguido ambar.
    """
    W, H = int(res[0]), int(res[1])
    if abs(H / W - 16.0 / 9.0) > 1e-6:
        raise ValueError(f"res tiene que ser 9:16; llego {res}")
    frames = np.empty((pasos, H, W, 3), dtype=np.uint8)
    lienzo = np.zeros((H, W, 3), dtype=np.float32)
    lienzo_ambar = np.zeros((H, W, 3), dtype=np.float32)

    def pintar(k, pos, seguido):
        # dos capas: el enjambre verde (que se comprime) y el agente ambar
        # (que no, para que no se lo trague la bandada cuando esta encima).
        estela(lienzo, DECAIMIENTO)
        estela(lienzo_ambar, DECAIMIENTO_SEGUIDO)
        px = pos * W                      # mundo (ancho 1) -> pixeles
        salpicar(lienzo, px, C_VIVO, peso=PESO_AGENTE, radio=RADIO_AGENTE)
        salpicar(lienzo_ambar, px[seguido:seguido + 1], C_REGLA,
                 peso=PESO_SEGUIDO, radio=RADIO_SEGUIDO)
        frames[k] = mezclar_capas(a_uint8(_tono(lienzo)),
                                  a_uint8(lienzo_ambar))

    pol, traza, seguido = _recorrer(semilla, pasos, agentes, pintar)
    extra = {
        "seguido": (traza * W).astype(np.float32),
        "polarizacion": pol,
        "indice_seguido": int(seguido),
        "res": (W, H),
        "pasos_por_segundo": PASOS_POR_SEGUNDO,
    }
    return {"frames": validar_pila(frames),
            "cifras": _cifras(pol, agentes), "extra": extra}


def medir(semilla=1, pasos=900, res=(270, 480), agentes=2500):
    """Solo las cifras (sin pintar), para la sonda. Mismos parametros."""
    pol, _, _ = _recorrer(semilla, pasos, agentes, None)
    return _cifras(pol, agentes)

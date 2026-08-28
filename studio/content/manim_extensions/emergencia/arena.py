# =====================================================================
# emergencia/arena.py — la pila de arena abeliana (Bak-Tang-Wiesenfeld, 1987).
#
# QUE SIMULA
#   Una rejilla cuadrada donde solo caen granos, siempre en la misma celda
#   del centro. Cuando una celda junta 4 granos, se derrumba y le da uno a
#   cada vecino; el vecino puede derrumbarse tambien, y asi. Nadie coordina
#   nada y sin embargo la pila se organiza sola: se estabiliza en una
#   MANDALA fractal, y las avalanchas no tienen un tamaño tipico — las hay
#   de 1 celda y las hay de decenas de miles, con una ley de potencias.
#   Es el ejemplo canonico de criticalidad autoorganizada.
#
# REGLAS (las tres lineas del HUD)
#   1. Cae un grano en el centro.
#   2. Toda celda con 4 o mas granos reparte 1 a cada vecino (y en el borde
#      se pierde).
#   3. Se repite hasta que nadie tiene 4. El orden no importa: el resultado
#      final es el mismo (por eso "abeliana").
#
# IMAGEN
#   Rejilla 179x179 centrada en el lienzo 9:16 (x2 = 358 px de ancho: llena
#   el ancho), el resto `C_FONDO`. Alturas 0/1/2/3 en cuatro tonos de la LUT
#   "orden" (violeta = lo ordenado que emerge): 0 = fondo, 1 = violeta
#   oscuro, 2 = violeta, 3 = violeta claro. Encima, en NARANJA `C_ENERGIA`
#   (energia / lo que escapa), destella el CONTORNO de la mayor avalancha
#   de ese frame (interior a un 22 %, cola de 3-4 frames): un anillo que se
#   abre y dice hasta donde llego el derrumbe. Marco fino en
#   `C_MOBILIARIO` para que se lea el tablero.
#
# CIFRAS (medidas sobre lo simulado)
#   granos                 granos anadidos en total (el numero real, no un
#                          "un millon" de adorno).
#   avalancha_mayor        celdas distintas que volcaron en la avalancha mas
#                          grande (una sola de esas la desata UN grano).
#   exponente              pendiente de la recta (negativa); `tau` es la
#                          misma con el signo cambiado.
#   exponente_tau_medido   pendiente (cambiada de signo) del ajuste por
#                          minimos cuadrados de log10 P(s) contra log10 s,
#                          con binning logaritmico, sobre el tramo con
#                          estadistica. `ajuste_r2` dice como de recta es.
#   avalanchas             cuantas avalanchas hubo (= granos).
#   altura_media           granos por celda dentro de la pila al final.
#   radio_final            radio de la mandala en celdas.
#
# EXTRA
#   tamanos                (granos,) int32: el tamaño de CADA avalancha.
#   avalancha_max_por_frame (T,) int32: la mayor de cada frame (es la que
#                          destella en naranja: sirve para sincronizar).
#   volcadas_por_frame     (T,) int32: celdas que volcaron en cada frame.
#   granos_por_frame       (T,) int64: granos acumulados (para el contador).
#   radio_por_frame        (T,) float32: radio de la pila en celdas.
#   alturas_final          (N,N) uint8.
#   caja                   (x0, y0, lado) de la rejilla en PIXELES del frame:
#                          para poner el marco/zoom con vectores encima.
#   centro_px              (x, y) en pixeles del punto donde caen los granos.
#   escala, N              px por celda y lado de la rejilla.
#   res                    (W, H).
#   histograma             dict(centros, densidad, mascara_ajuste, recta):
#                          la distribucion log-log ya lista para dibujarla.
#
# COSTE MEDIDO (contenedor codeaerospace_contenido-manim, 2026-08-28)
#   simular() con los valores por defecto = 59.7 y 66.2 s en dos
#   corridas (tope 90 s);
#   T = 750 frames a 360x640, pila 518.4 MB uint8 (tope 1 GB).
#   medir() (sin pintar) = 64.9 y 68.4 s en dos corridas: el coste NO esta
#   en pintar, esta en las 50 000 avalanchas relajadas UNA A UNA.
#
#   Cuanto cuesta cada tamaño (medido, medir(), mismo contenedor):
#       N=179, 25 000 granos ->  19.8 s   radio 58 de 89
#       N=179, 50 000 granos ->  68.4 s   radio 83 de 89   <- por defecto
#       N=249, 100 000 granos-> no termino en 800 s
#   El coste va como granos^1.8 (las avalanchas grandes se comen todo), asi
#   que el millon de granos del plan NO cabe: ni en 90 s ni en la rejilla
#   (haria falta radio 122, o sea N >= 249). Si hiciera falta mas holgura,
#   `granos=40000` baja a ~45 s y deja la mandala en radio 74.
#   La cifra que va en pantalla es 50 000, la real.
#
# VALORES MEDIDOS con los valores por defecto
#   granos = 50000            avalancha_mayor = 21533 celdas
#   exponente_tau_medido = 1.279   ajuste_r2 = 0.993 (22 bins log)
#   altura_media = 2.478      radio_final = 83 celdas
#   El 75 % de los granos (37 500) no derrumba nada; la mayor avalancha
#   toca 21 533 celdas: cinco ordenes de magnitud sin tamaño tipico.
# =====================================================================
import numpy as np

from . import (C_ENERGIA, C_FONDO, C_MOBILIARIO, C_ORDEN, hex_a_rgb, lut,
               validar_pila)

# Cuatro tonos de la LUT "orden": una altura, un tono.
_L = lut(C_FONDO, C_ORDEN, "#d8c7ff")
TABLA_ALTURA = np.stack([_L[0], _L[85], _L[170], _L[255]]).astype(np.float32)
NARANJA = hex_a_rgb(C_ENERGIA)


# --------------------------------------------------------------------
# Nucleo numerico
# --------------------------------------------------------------------
def _avalancha(h, marca, cy, cx, N):
    """Deja caer un grano en (cy,cx) y relaja hasta estabilizar.

    Trabaja en una VENTANA que crece 1 celda por barrido. Es correcto y es
    lo que hace que esto quepa en el presupuesto: una avalancha es causal,
    en el barrido t solo puede haber celdas inestables a distancia < t del
    grano, asi que la ventana (2t+1)^2 las contiene todas. Relajar la
    rejilla entera en cada barrido cuesta ~40x mas.

    Marca en `marca` las celdas que volcaron y devuelve la ventana final
    (y0, y1, x0, x1): quien llama cuenta ahi el tamaño y la limpia.
    """
    h[cy, cx] += 1
    y0, y1, x0, x1 = cy, cy + 1, cx, cx + 1
    while True:
        y0 = max(y0 - 1, 0)
        y1 = min(y1 + 1, N)
        x0 = max(x0 - 1, 0)
        x1 = min(x1 + 1, N)
        sub = h[y0:y1, x0:x1]
        un = sub >= 4
        if not un.any():
            break
        marca[y0:y1, x0:x1] |= un
        sub -= 4 * un
        # reparto a los cuatro vecinos; lo que cae fuera de la rejilla se
        # pierde (borde abierto) y por eso la pila alcanza un estado estable
        sub[1:, :] += un[:-1, :]
        sub[:-1, :] += un[1:, :]
        sub[:, 1:] += un[:, :-1]
        sub[:, :-1] += un[:, 1:]
    return y0, y1, x0, x1


def _ley_de_potencias(tamanos, bins=26, minimo=4, cuenta_min=8):
    """Distribucion log-log de los tamaños y ajuste de la pendiente.

    Binning logaritmico (obligatorio: con bins lineales la cola manda y la
    pendiente sale falsa). Se ajusta solo donde hay estadistica: bins con
    >= `cuenta_min` avalanchas y centro >= `minimo`.
    """
    s = np.asarray(tamanos, dtype=np.float64)
    s = s[s >= 1]
    if len(s) < 50:
        return {"centros": np.zeros(0), "densidad": np.zeros(0),
                "mascara_ajuste": np.zeros(0, bool), "recta": (0.0, 0.0)}, \
               0.0, 0.0
    bordes = np.logspace(0.0, np.log10(s.max()) + 1e-9, bins + 1)
    conteo, bordes = np.histogram(s, bins=bordes)
    ancho = np.diff(bordes)
    centros = np.sqrt(bordes[:-1] * bordes[1:])
    dens = conteo / (ancho * len(s))
    ok = (conteo >= cuenta_min) & (centros >= minimo) & (dens > 0)
    if ok.sum() < 4:
        ok = (conteo > 0) & (dens > 0)
    lx, ly = np.log10(centros[ok]), np.log10(dens[ok])
    m, b = np.polyfit(lx, ly, 1)
    pred = m * lx + b
    ss = float(np.sum((ly - pred) ** 2))
    st = float(np.sum((ly - ly.mean()) ** 2))
    r2 = 1.0 - ss / st if st > 0 else 0.0
    hist = {"centros": centros, "densidad": dens, "conteo": conteo,
            "mascara_ajuste": ok, "recta": (float(m), float(b))}
    return hist, float(-m), float(r2)


def _correr(N, granos, semilla, pasos, res, escala, marco, guardar_frames):
    W, H = int(res[0]), int(res[1])
    if abs(H / W - 16.0 / 9.0) > 1e-6:
        raise ValueError(f"res debe ser 9:16; llego {res}")
    if N % 2 == 0:
        raise ValueError("N tiene que ser impar (hay una celda central)")
    esc = int(escala) if escala else max(1, min(W, H) // N)
    if N * esc > W or N * esc > H:
        raise ValueError(f"la rejilla {N}x{N} a escala {esc} no cabe en {res}")
    # `semilla` se acepta por contrato pero NO se usa: la pila abeliana es
    # completamente determinista (todos los granos caen en la misma celda y
    # el orden de los vuelcos no altera el resultado). Dos corridas con
    # semillas distintas dan cifras identicas: es una propiedad, no un fallo.
    _ = semilla

    h = np.zeros((N, N), dtype=np.int32)
    marca = np.zeros((N, N), dtype=bool)
    cy = cx = N // 2

    # granos acumulados ~ t^2  =>  radio ~ t: la mandala crece a ritmo
    # constante en pantalla (la superficie de la pila va como el radio^2).
    acum = np.round(granos * (np.arange(1, pasos + 1) / pasos) ** 2)
    acum = acum.astype(np.int64)
    por_frame = np.diff(np.concatenate([[0], acum]))
    granos = int(acum[-1])

    tamanos = np.empty(granos, dtype=np.int32)
    av_max = np.zeros(pasos, dtype=np.int32)
    volcadas = np.zeros(pasos, dtype=np.int32)
    radio = np.zeros(pasos, dtype=np.float32)

    lado = N * esc
    px0 = (W - lado) // 2
    py0 = (H - lado) // 2
    if guardar_frames:
        frames = np.empty((pasos, H, W, 3), dtype=np.uint8)
        plantilla = np.empty((H, W, 3), dtype=np.uint8)
        plantilla[:] = hex_a_rgb(C_FONDO).astype(np.uint8)
        if marco and px0 >= 1 and py0 >= 1:
            m = hex_a_rgb(C_MOBILIARIO).astype(np.uint8)
            plantilla[py0 - 1, px0 - 1:px0 + lado + 1] = m
            plantilla[py0 + lado, px0 - 1:px0 + lado + 1] = m
            plantilla[py0 - 1:py0 + lado + 1, px0 - 1] = m
            plantilla[py0 - 1:py0 + lado + 1, px0 + lado] = m
        brillo = np.zeros((N, N), dtype=np.float32)
    else:
        frames = None

    g = 0
    for k in range(pasos):
        mayor = 0
        vol = 0
        mejor = None
        for _ in range(int(por_frame[k])):
            y0, y1, x0, x1 = _avalancha(h, marca, cy, cx, N)
            vent = marca[y0:y1, x0:x1]
            tam = int(vent.sum())
            tamanos[g] = tam
            g += 1
            vol += tam
            if tam > mayor:
                mayor = tam
                # solo destella la MAYOR del frame: la union de las ~130
                # avalanchas de un frame tardio cubre media mandala y la
                # taparia entera de naranja.
                mejor = (y0, y1, x0, x1, vent.copy()) if guardar_frames \
                    else None
            vent[:] = False
        av_max[k] = mayor
        volcadas[k] = vol

        ocupado = h > 0
        fy = np.flatnonzero(ocupado.any(axis=1))
        if len(fy):
            fx = np.flatnonzero(ocupado.any(axis=0))
            radio[k] = max(abs(fy[0] - cy), abs(fy[-1] - cy),
                           abs(fx[0] - cx), abs(fx[-1] - cx))

        if guardar_frames:
            brillo *= 0.55
            if mejor is not None:
                y0, y1, x0, x1, msk = mejor
                # El CONTORNO de la avalancha a tope y el interior en un
                # velo del 22 %. Rellenarla entera de naranja borra la
                # mandala: la mayor del ultimo frame toca 21533 de las
                # ~21600 celdas de la pila (medido) y el frame sale liso.
                pad = np.zeros((msk.shape[0] + 2, msk.shape[1] + 2), bool)
                pad[1:-1, 1:-1] = msk
                dentro = (msk & pad[:-2, 1:-1] & pad[2:, 1:-1]
                          & pad[1:-1, :-2] & pad[1:-1, 2:])
                v = np.where(msk & ~dentro, 1.0,
                             np.where(msk, 0.22, 0.0)).astype(np.float32)
                sl = brillo[y0:y1, x0:x1]
                np.maximum(sl, v, out=sl)
            rej = TABLA_ALTURA[np.minimum(h, 3)]
            b = brillo[..., None]
            rej = rej * (1.0 - b) + NARANJA[None, None, :] * b
            bloque = np.repeat(np.repeat(
                np.clip(rej, 0, 255).astype(np.uint8), esc, axis=0), esc,
                axis=1)
            frames[k] = plantilla
            frames[k, py0:py0 + lado, px0:px0 + lado] = bloque

    hist, tau, r2 = _ley_de_potencias(tamanos)
    dentro = h > 0
    cifras = {
        "granos": int(granos),
        "avalancha_mayor": int(tamanos.max()),
        "exponente_tau_medido": tau,
        # el mismo numero con el signo de la recta (pendiente de log10 P(s)
        # contra log10 s): tau = -exponente. Se devuelven los dos porque en
        # pantalla se dice "tau" y en el ajuste se ve la pendiente.
        "exponente": -tau,
        "ajuste_r2": r2,
        "avalanchas": int(granos),
        "altura_media": float(h[dentro].mean()) if dentro.any() else 0.0,
        "radio_final": float(radio[-1]),
        "rejilla": int(N),
    }
    extra = {
        "tamanos": tamanos,
        "avalancha_max_por_frame": av_max,
        "volcadas_por_frame": volcadas,
        "granos_por_frame": acum,
        "radio_por_frame": radio,
        "alturas_final": h.astype(np.uint8),
        "caja": (int(px0), int(py0), int(lado)),
        "centro_px": (float(px0 + (cx + 0.5) * esc),
                      float(py0 + (cy + 0.5) * esc)),
        "escala": esc,
        "N": int(N),
        "histograma": hist,
        "res": (W, H),
    }
    return frames, cifras, extra


# --------------------------------------------------------------------
# Interfaz publica
# --------------------------------------------------------------------
PAR = dict(N=179, granos=50000, semilla=1, pasos=750, res=(360, 640),
           escala=None, marco=True)


def simular(N=179, granos=50000, semilla=1, pasos=750, res=(360, 640),
            escala=None, marco=True):
    """La pila de arena abeliana creciendo desde el centro.

    T = `pasos` (750 por defecto: un frame por lote de granos). Los granos
    se reparten como t^2 sobre los frames para que el RADIO de la mandala
    crezca a ritmo constante y termine rozando el borde de la rejilla.

    `res=(360,640)` por defecto (el clip hace zoom); `res=(270,480)` tambien
    vale y entonces `escala` cae a 1. `escala=None` la calcula para llenar
    el ancho con un factor entero (nada de reescalado no entero: esto es un
    automata, cada celda tiene que ser un bloque exacto).

    Devuelve dict(frames uint8 (T,H,W,3), cifras, extra); ver el docstring
    del modulo.
    """
    frames, cifras, extra = _correr(N, granos, semilla, pasos, res, escala,
                                    marco, True)
    return {"frames": validar_pila(frames), "cifras": cifras, "extra": extra}


def medir(N=179, granos=50000, semilla=1, pasos=750, res=(360, 640),
          escala=None, marco=True):
    """Solo las cifras (sin pila de frames), para la sonda."""
    _, cifras, _ = _correr(N, granos, semilla, pasos, res, escala, marco,
                           False)
    return cifras


__all__ = ["simular", "medir", "TABLA_ALTURA", "PAR"]

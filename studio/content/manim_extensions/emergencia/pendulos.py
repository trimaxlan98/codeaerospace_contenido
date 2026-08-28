# =====================================================================
# emergencia/pendulos.py — clip 09 "doscientos pendulos".
#
# QUE SIMULA
#   200 pendulos DOBLES (m1=m2, l1=l2) soltados desde el mismo sitio:
#   theta1=theta2=120 grados, quietos. Lo unico que los distingue es que
#   el angulo de arriba del pendulo n empieza 1e-6 rad (0.00006 grados)
#   mas abierto que el del n-1: una escalera de una millonesima de radian
#   entre el primero y el ultimo. Al principio son un punto; a los pocos
#   segundos son un abanico de colores. Eso es el caos: no es que la
#   simulacion falle, es que la fisica amplifica lo que no se midio.
#
# REGLAS (las tres lineas del HUD)
#   1. dos varillas iguales, sin rozamiento; solo gravedad
#   2. los 200 arrancan igual salvo 1e-6 rad en el angulo de arriba
#   3. el error se multiplica por e cada 1/lambda segundos
#
# COMO
#   Estado (200, 4) = (theta1, theta2, omega1, omega2). RK4 vectorizado:
#   los 200 pendulos avanzan en las MISMAS operaciones numpy, no hay
#   bucle por pendulo. Paso dt = 1/600 s con 20 subpasos por frame de
#   1/30 s. Ecuaciones con m1=m2=m y l1=l2=l (la masa se cancela):
#     den = l*(3 - cos(2*(th1-th2)))
#     a1  = (-3*g*sin(th1) - g*sin(th1-2*th2)
#            - 2*sin(th1-th2)*l*(w2^2 + w1^2*cos(th1-th2))) / den
#     a2  = (2*sin(th1-th2)*(2*l*w1^2 + 2*g*cos(th1)
#            + l*w2^2*cos(th1-th2))) / den
#
# IMAGEN
#   Los 200 comparten el pivote, en el centro-alto del lienzo. Se pinta
#   con `salpicar` el SEGUNDO bob de cada uno, con color por indice sobre
#   el arcoiris de marca ambar C_REGLA -> naranja C_ENERGIA -> violeta
#   C_ORDEN (20 bandas de 10 pendulos: 200 llamadas a salpicar por frame
#   costarian mas que la fisica entera). Estela corta: la capa persistente
#   se multiplica por 0.88 en cada frame (a los 18 frames, 0.6 s, queda el
#   10 %) y en cada frame se sueltan 8 posiciones interpoladas entre la
#   anterior y la actual, para que la estela sea una curva y no un collar
#   de puntos sueltos. Encima, las varillas de solo 3 pendulos (0, 100 y
#   199) en gris C_EXTERNO, para que se vea la maquina que produce el
#   abanico.
#   La longitud de varilla la manda el ANCHO: el bob 2 puede llegar a 2*l
#   del pivote en horizontal, asi que l = (W/2 - 4)/2 = 66 px y nada se
#   sale del lienzo (comprobado: min/max de las posiciones dentro).
#
# COSTE MEDIDO (contenedor codeaerospace_contenido-manim, 2026-08-28)
#   simular(pasos=900): 23-29 s de CPU segun carga (18 000 pasos de RK4 +
#   900 frames pintados), pila de 350 MB (900 frames de 480x270x3, 30 s a
#   30 fps). medir(): 7 s (misma fisica, sin pintar): pintar es el 70 %
#   del coste; la fisica de los 200 pendulos no llega a 8 s.
#
# CIFRAS (todas medidas sobre lo simulado)
#   t_separacion_1rad ... s hasta que la separacion angular maxima entre
#                         dos pendulos cualesquiera (diferencia de theta1
#                         envuelta a [-pi,pi]) pasa de 1 rad
#   t_dispersion_10pct .. s hasta que la desviacion tipica de las
#                         posiciones del bob 2 pasa del 10 % de 2*l
#   lyapunov_medido ..... 1/s, pendiente de log(separacion entre el
#                         pendulo 0 y el 1) antes de saturar
#   t_duplicar_error .... ln(2)/lyapunov, s
#   deriva_energia_pct .. maxima deriva relativa de la energia total
#                         (RK4 no es simplectico: hay que vigilarla).
#                         Medida: 4.9e-6 %, o sea 20 000 veces por debajo
#                         del 0.1 % que se pedia.
# =====================================================================
import time

import numpy as np

from . import (C_ENERGIA, C_EXTERNO, C_FONDO, C_ORDEN, C_REGLA, RES_BASE,
               a_uint8, estela, hex_a_rgb, lut, salpicar, validar_pila)

G = 9.81            # m/s^2
LONGITUD = 1.0      # l1 = l2 = l (la masa se cancela y no hace falta)


def _derivada(y, g=G, l=LONGITUD):
    """y (n,4) = (th1, th2, w1, w2) -> dy/dt (n,4). Vectorizado en n."""
    th1, th2, w1, w2 = y[:, 0], y[:, 1], y[:, 2], y[:, 3]
    d = th1 - th2
    sd, cd = np.sin(d), np.cos(d)
    den = l * (3.0 - np.cos(2.0 * d))
    a1 = (-3.0 * g * np.sin(th1) - g * np.sin(th1 - 2.0 * th2)
          - 2.0 * sd * l * (w2 * w2 + w1 * w1 * cd)) / den
    a2 = (2.0 * sd * (2.0 * l * w1 * w1 + 2.0 * g * np.cos(th1)
                      + l * w2 * w2 * cd)) / den
    return np.stack([w1, w2, a1, a2], axis=1)


def _rk4(y, dt, g=G, l=LONGITUD):
    k1 = _derivada(y, g, l)
    k2 = _derivada(y + 0.5 * dt * k1, g, l)
    k3 = _derivada(y + 0.5 * dt * k2, g, l)
    k4 = _derivada(y + dt * k3, g, l)
    return y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def _energia(y, g=G, l=LONGITUD, m=1.0):
    """Energia total por pendulo (n,), con el cero de potencial en el pivote."""
    th1, th2, w1, w2 = y[:, 0], y[:, 1], y[:, 2], y[:, 3]
    cin = 0.5 * m * l * l * (2.0 * w1 * w1 + w2 * w2
                             + 2.0 * w1 * w2 * np.cos(th1 - th2))
    pot = -m * g * l * (2.0 * np.cos(th1) + np.cos(th2))
    return cin + pot


def _envolver(a):
    """Diferencia angular llevada a [-pi, pi)."""
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def _bobs(y, l=LONGITUD):
    """(n,4) -> (x1,y1,x2,y2) en unidades de longitud, y hacia ARRIBA."""
    th1, th2 = y[:, 0], y[:, 1]
    x1 = l * np.sin(th1)
    y1 = -l * np.cos(th1)
    return x1, y1, x1 + l * np.sin(th2), y1 - l * np.cos(th2)


def _hex(rgb):
    r, g, b = (int(round(float(v))) for v in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def _puntos_barra(pivote, b1, b2, muestras=70):
    """Puntos (2*muestras*k, 2) de las varillas pivote->bob1->bob2."""
    t = np.linspace(0.0, 1.0, muestras)[:, None, None]
    p = pivote[None, None, :]
    alto = p + t * (b1[None] - p)
    bajo = b1[None] + t * (b2[None] - b1[None])
    return np.concatenate([alto.reshape(-1, 2), bajo.reshape(-1, 2)], axis=0)


def _correr(semilla=1, pasos=900, res=RES_BASE, n=200, delta=1e-6,
            theta0_grados=120.0, subpasos=20, fps=30, bandas=20,
            barras=(0, 100, 199), decaimiento=0.88, submuestras=8,
            pintar=True):
    """Nucleo compartido por `simular` y `medir`."""
    W, H = int(res[0]), int(res[1])
    if abs(H / W - 16 / 9) > 1e-6:
        raise ValueError(f"res tiene que ser 9:16; llego {W}x{H}")
    n = int(n)
    dt = 1.0 / (fps * subpasos)

    # --- condicion inicial: escalera de `delta` rad en theta1 -----------
    th0 = np.deg2rad(theta0_grados)
    y = np.zeros((n, 4), dtype=np.float64)
    y[:, 0] = th0 + delta * np.arange(n)
    y[:, 1] = th0

    # --- geometria del dibujo -------------------------------------------
    L = (W * 0.5 - 4.0) / 2.0                 # px por unidad de longitud
    cx, cy = W * 0.5, H * 0.40                # pivote: centro-alto
    pivote = np.array([cx, cy], dtype=np.float64)

    rampa = lut(C_REGLA, C_ENERGIA, C_ORDEN, n=bandas)
    colores = [_hex(rampa[b]) for b in range(bandas)]
    banda_de = (np.arange(n) * bandas) // n
    grupos = [np.where(banda_de == b)[0] for b in range(bandas)]
    sel = np.array(sorted(set(int(i) % n for i in barras)), dtype=np.int64) \
        if barras else np.zeros(0, dtype=np.int64)

    fondo = (hex_a_rgb(C_FONDO) / 255.0).astype(np.float32)
    lienzo = np.zeros((H, W, 3), dtype=np.float32)
    capa_barras = np.zeros((H, W, 3), dtype=np.float32)
    # techo de la capa de varillas: `salpicar` es aditivo y tres varillas
    # encimadas (al principio los 200 pendulos van juntos) se irian a
    # blanco. Se pintan aparte y se recortan al color de UNA varilla.
    techo = (hex_a_rgb(C_EXTERNO) / 255.0 * 0.42).astype(np.float32)
    fracs = (np.arange(1, submuestras + 1) / submuestras)[:, None, None]
    xy_previo = None
    frames = np.empty((pasos, H, W, 3), dtype=np.uint8) if pintar else None

    pos_px = np.empty((pasos, n, 2), dtype=np.float32)
    sep_max = np.empty(pasos, dtype=np.float32)
    sep01 = np.empty(pasos, dtype=np.float64)
    disp = np.empty(pasos, dtype=np.float32)
    energia = np.empty(pasos, dtype=np.float64)
    tiempo = np.arange(pasos, dtype=np.float64) / fps

    t0 = time.perf_counter()
    for f in range(pasos):
        # --- medidas del estado actual (el frame 0 es t=0) --------------
        x1, y1, x2, y2 = _bobs(y)
        px = cx + L * x2
        py = cy - L * y2
        pos_px[f, :, 0] = px
        pos_px[f, :, 1] = py
        d = _envolver(y[:, 0][:, None] - y[:, 0][None, :])
        sep_max[f] = np.abs(d).max()
        dif = np.array([_envolver(y[0, 0] - y[1, 0]),
                        _envolver(y[0, 1] - y[1, 1]),
                        y[0, 2] - y[1, 2], y[0, 3] - y[1, 3]])
        sep01[f] = np.sqrt(float((dif * dif).sum()))
        disp[f] = np.sqrt(float(x2.var() + y2.var()))
        energia[f] = float(_energia(y).mean())

        # --- pintar -----------------------------------------------------
        if pintar:
            estela(lienzo, decaimiento)
            xy = np.stack([px, py], axis=1)
            # estela continua: el bob 2 se mueve hasta 13 px por frame, asi
            # que soltar un punto por frame deja un collar de puntos. Se
            # interpolan `submuestras` posiciones entre el frame anterior y
            # este; van en la MISMA llamada a salpicar (mas puntos, no mas
            # llamadas), que es donde estaba el coste.
            rastro = (xy if xy_previo is None
                      else (xy_previo[None] + fracs * (xy - xy_previo)[None]))
            for b, g in enumerate(grupos):
                salpicar(lienzo, rastro[..., g, :].reshape(-1, 2), colores[b],
                         peso=0.16, radio=1.0)
            xy_previo = xy
            capa = lienzo.copy()
            if len(sel):
                b1 = np.stack([cx + L * x1[sel], cy - L * y1[sel]], axis=1)
                capa_barras[:] = 0.0
                salpicar(capa_barras, _puntos_barra(pivote, b1, xy[sel]),
                         C_EXTERNO, peso=0.55, radio=0.6)
                np.minimum(capa_barras, techo, out=capa_barras)
                capa += capa_barras
            for b, g in enumerate(grupos):
                salpicar(capa, xy[g], colores[b], peso=0.95, radio=1.4)
            frames[f] = a_uint8(capa + fondo)

        # --- avanzar un frame -------------------------------------------
        for _ in range(subpasos):
            y = _rk4(y, dt)
    coste = time.perf_counter() - t0

    # --- cifras -----------------------------------------------------------
    def cruce(serie, umbral, persistencia=15):
        """Primer frame que pasa `umbral` y AGUANTA `persistencia` frames.

        Sin la condicion de aguante, `dispersion` (que sube y baja con el
        vaiven: los bobs se abren y se vuelven a juntar en el punto de
        retorno) cruza el umbral medio segundo antes en un pico que se
        deshace, y la cifra no seria la del fenomeno.
        """
        arriba = (serie >= umbral).astype(np.int64)
        if not arriba.any():
            return -1, float("nan")
        p = min(int(persistencia), len(serie))
        acum = np.concatenate([[0], np.cumsum(arriba)])
        ventana = acum[p:] - acum[:-p]          # frames >= umbral en [k, k+p)
        buenos = np.where(ventana >= p)[0]
        k = int(buenos[0]) if len(buenos) else int(np.argmax(arriba))
        if k == 0:
            return 0, 0.0
        s0, s1 = float(serie[k - 1]), float(serie[k])
        fr = (umbral - s0) / max(s1 - s0, 1e-12)
        return k, float(tiempo[k - 1] + fr * (tiempo[k] - tiempo[k - 1]))

    f_sep, t_sep = cruce(sep_max, 1.0)
    f_dis, t_dis = cruce(disp, 0.10 * 2.0 * LONGITUD)

    # Lyapunov: pendiente de log(sep01) entre 20*delta y 0.05, o sea
    # despues del transitorio y antes de que la separacion sature (el
    # atractor tiene tamaño finito: sep01 no puede pasar de ~2*pi).
    lo, hi = 20.0 * delta, 0.05
    dentro = np.where((sep01 > lo) & (sep01 < hi))[0]
    lyap, r2, ventana = float("nan"), float("nan"), (-1, -1)
    if len(dentro) >= 5:
        a, b = int(dentro[0]), int(dentro[-1])
        tt = tiempo[a:b + 1]
        ll = np.log(sep01[a:b + 1])
        A = np.vstack([tt, np.ones_like(tt)]).T
        (m, c), *_ = np.linalg.lstsq(A, ll, rcond=None)
        pred = m * tt + c
        ss = float(((ll - pred) ** 2).sum())
        st = float(((ll - ll.mean()) ** 2).sum())
        lyap, r2, ventana = float(m), 1.0 - ss / max(st, 1e-12), (a, b)

    e0 = float(energia[0])
    deriva = float(np.max(np.abs(energia - e0)) / abs(e0) * 100.0)

    cifras = {
        "pendulos": n,
        "delta_inicial_rad": delta,
        "t_separacion_1rad": round(t_sep, 3),
        "t_dispersion_10pct": round(t_dis, 3),
        "lyapunov_medido": round(lyap, 3),
        "t_duplicar_error": round(float(np.log(2.0) / lyap), 4),
        "ajuste_r2": round(r2, 5),
        "deriva_energia_pct": float(f"{deriva:.3g}"),
        "energia_total": round(e0, 4),
        "separacion_final_rad": round(float(sep_max[-1]), 3),
        "segundos_simulados": round(float(tiempo[-1]), 2),
        "segundos_cpu": round(coste, 1),
    }
    extra = {
        "tiempo": tiempo.astype(np.float32),
        "separacion_max": sep_max,
        "separacion_0_1": sep01.astype(np.float32),
        "dispersion": disp,
        "energia_total": energia.astype(np.float32),
        "posiciones_bob2_px": pos_px,
        "frame_separacion_1rad": f_sep,
        "frame_dispersion_10pct": f_dis,
        "ventana_lyapunov": ventana,
        "pivote_px": (float(cx), float(cy)),
        "longitud_px": float(L),
        "colores_banda": colores,
        "banda_de_pendulo": banda_de,
    }
    return frames, cifras, extra


def simular(semilla=1, pasos=900, res=RES_BASE, n=200, delta=1e-6,
            theta0_grados=120.0, subpasos=20, fps=30, bandas=20,
            barras=(0, 100, 199), decaimiento=0.88, submuestras=8):
    """200 pendulos dobles con 1e-6 rad de diferencia. 900 frames = 30 s.

    semilla ....... no interviene: la condicion inicial es determinista
                    (la escalera de `delta`). Se acepta por la interfaz.
    pasos ......... frames a 30 fps (900 = 30 s simulados)
    res ........... (W, H) 9:16; 270x480 por defecto
    n ............. pendulos
    delta ......... diferencia de theta1 entre vecinos, rad
    theta0_grados . angulo inicial de las dos varillas (120 = energia alta)
    subpasos ...... pasos de RK4 por frame (20 -> dt = 1/600 s)
    bandas ........ cortes de color del arcoiris ambar->naranja->violeta
    barras ........ indices cuyas varillas se dibujan en gris (o ())
    decaimiento ... cuanto sobrevive la estela de un frame al siguiente
    submuestras ... puntos interpolados de estela entre frame y frame

    Devuelve dict(frames=uint8 (T,H,W,3), cifras={...}, extra={...}).
    `extra` trae `tiempo` (T,), `separacion_max` (T,) rad,
    `separacion_0_1` (T,) (la que mide el Lyapunov), `dispersion` (T,) en
    unidades de longitud, `energia_total` (T,), `posiciones_bob2_px`
    (T,n,2) float32 en pixeles del lienzo (para dibujar vectorial
    encima), los frames de los dos cruces, `pivote_px`, `longitud_px`,
    `colores_banda` y `banda_de_pendulo` (n,).
    """
    frames, cifras, extra = _correr(semilla, pasos, res, n, delta,
                                    theta0_grados, subpasos, fps, bandas,
                                    barras, decaimiento, submuestras,
                                    pintar=True)
    return {"frames": validar_pila(frames), "cifras": cifras, "extra": extra}


def medir(semilla=1, pasos=900, res=RES_BASE, n=200, delta=1e-6,
          theta0_grados=120.0, subpasos=20, fps=30, bandas=20,
          barras=(0, 100, 199), decaimiento=0.88, submuestras=8):
    """Solo las cifras (misma fisica, sin pintar)."""
    _, cifras, _ = _correr(semilla, pasos, res, n, delta, theta0_grados,
                           subpasos, fps, bandas, barras, decaimiento,
                           submuestras, pintar=False)
    return cifras

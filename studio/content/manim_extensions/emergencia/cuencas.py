# =====================================================================
# emergencia/cuencas.py — clip 10 "las cuencas" (curso 29, vertical).
#
# QUE SIMULA
# Un pendulo magnetico: una masa colgada sobre tres imanes puestos en
# triangulo equilatero. Se integra UN pendulo POR PIXEL del lienzo: cada
# pixel es una condicion inicial distinta, soltada en reposo. El color del
# pixel es el iman al que ese pendulo se acerca mas EN ESE INSTANTE, asi
# que el mapa se ve nacer: sectores limpios -> revoltijo -> la frontera
# fractal donde tres cuencas se tocan en todas partes.
#
# REGLAS (las tres lineas del HUD)
#   1. cada pixel = un pendulo soltado en reposo ahi
#   2. resorte -k r, friccion -mu v, tres imanes que tiran como 1/(d^2+h^2)^(3/2)
#   3. el color dice a que iman se acerca mas AHORA
#
# COLORES POR ROL: los tres imanes son violeta (C_ORDEN), ambar (C_REGLA) y
# verde (C_VIVO) — tres dominios, tres roles. El brillo baja mientras el
# pendulo corre y sube cuando se para: el mapa "cuaja".
#
# PARAMETROS: res (W,H) 9:16 (por defecto 360x640, admite 270x480), pasos
# = numero de frames T, subpasos por frame, dt, k, mu, h, fuerza, radio del
# triangulo, semilla (no hay azar: se acepta por contrato y fija el pixel
# de la trayectoria de ejemplo).
#
# COSTE MEDIDO (contenedor, 2026-08-28): res=(360,640), T=600, 10 subpasos
# de dt=0.013 (6000 pasos, t_final=78): 22-33 s de CPU (segun carga
# de la maquina) y 414.7 MB de pila.
# A res=(270,480): 12.6 s y 233.3 MB. Tope del contrato: 90 s / 1 GB.
#
# CIFRAS (todas medidas sobre lo simulado)
#   fraccion_iman_violeta / _ambar / _verde : reparto final (suman 1)
#   dimension_frontera : conteo de cajas sobre los pixeles cuyo vecino
#       acaba en otro iman (escalas 1..32 px, ajuste por minimos cuadrados
#       de log N frente a log 1/s). OJO: las cajas se cuentan en PIXELES,
#       asi que la cifra depende de `res`: 1.626 a (360,640) y 1.672 a
#       (270,480). La del clip es la de (360,640).
#   pixeles_sin_converger : los que al final siguen lejos de todo iman o
#       aun se mueven
#   frame_mitad_convergida : primer frame con la mitad de los pendulos ya
#       quietos junto a un iman (mide 477 de 600: la convergencia llega en
#       el ultimo cuarto, que es lo que el clip necesita)
#   pixeles_frontera : cuantos pixeles tienen un vecino de otra cuenca
#
# EXTRA
#   imanes_px      (3,2) float  posicion de los imanes en pixeles
#   colores        (3,)  str    hex de cada iman, en el mismo orden
#   trayectoria    (T,2) float  camino en pixeles de UN pendulo que arranca
#                               pegado a la frontera (para dibujarlo vectorial)
#   trayectoria_px (2,)  int    el pixel (x,y) del que sale esa trayectoria
#   trayectoria_iman int        en que iman acaba ese pendulo
#   convergidos    (T,) float   fraccion convergida en cada frame (curva HUD)
#   dominio        (4,) float   (x0, x1, y0, y1) fisicos del lienzo
#   zoom_frontera  (2,) float   (cx, cy) en fraccion 0-1 de un punto de la
#                               frontera "gorda" (donde hacer zoom)
# =====================================================================
import numpy as np

from . import (C_ORDEN, C_REGLA, C_VIVO, C_TINTA, hex_a_rgb, salpicar,
               validar_pila)

COLORES_IMAN = (C_ORDEN, C_REGLA, C_VIVO)


def _malla(res, radio_triangulo):
    """Dominio fisico y condiciones iniciales, una por pixel."""
    W, H = res
    if abs(H / W - 16.0 / 9.0) > 1e-6:
        raise ValueError(f"res {res} no es 9:16 (H/W = {H / W:.4f})")
    lx = 1.15 * radio_triangulo
    ly = lx * H / W
    xs = np.linspace(-lx, lx, W, dtype=np.float32)
    ys = np.linspace(ly, -ly, H, dtype=np.float32)      # fila 0 = arriba
    x = np.repeat(xs[None, :], H, axis=0).ravel().copy()
    y = np.repeat(ys[:, None], W, axis=1).ravel().copy()
    return x, y, (-lx, lx, -ly, ly)


def _imanes(radio_triangulo):
    ang = np.array([np.pi / 2, np.pi / 2 + 2 * np.pi / 3,
                    np.pi / 2 - 2 * np.pi / 3], dtype=np.float32)
    return (radio_triangulo * np.cos(ang), radio_triangulo * np.sin(ang))


def _a_pixeles(x, y, dominio, res):
    x0, x1, y0, y1 = dominio
    W, H = res
    px = (np.asarray(x) - x0) / (x1 - x0) * (W - 1)
    py = (y1 - np.asarray(y)) / (y1 - y0) * (H - 1)
    return px, py


def _dimension_cajas(mascara, escalas=(1, 2, 4, 8, 16, 32)):
    """Dimension por conteo de cajas de una mascara booleana (H,W)."""
    H, W = mascara.shape
    logs, logn = [], []
    for s in escalas:
        h = (H // s) * s
        w = (W // s) * s
        if h == 0 or w == 0:
            continue
        bloques = mascara[:h, :w].reshape(h // s, s, w // s, s)
        n = int(bloques.any(axis=(1, 3)).sum())
        if n == 0:
            continue
        logs.append(np.log(1.0 / s))
        logn.append(np.log(n))
    if len(logs) < 3:
        return float("nan")
    pend, _ = np.polyfit(np.array(logs), np.array(logn), 1)
    return float(pend)


def _trayectoria_de(x0, y0, imx, imy, dt, subpasos, T, k, mu, fuerza, h):
    """Camino (T,2) fisico de UN pendulo, muestreado una vez por frame."""
    x = np.float64(x0); y = np.float64(y0)
    vx = np.float64(0.0); vy = np.float64(0.0)
    h2 = h * h
    amort = 1.0 / (1.0 + mu * dt)
    cam = np.empty((T, 2), dtype=np.float64)
    for t in range(T):
        cam[t] = (x, y)
        for _ in range(subpasos):
            ax = -k * x; ay = -k * y
            for i in range(3):
                dx = imx[i] - x; dy = imy[i] - y
                d2 = dx * dx + dy * dy + h2
                inv = fuerza / (d2 * np.sqrt(d2))
                ax += dx * inv; ay += dy * inv
            vx = (vx + ax * dt) * amort
            vy = (vy + ay * dt) * amort
            x += vx * dt; y += vy * dt
    return cam


def _correr(res=(360, 640), pasos=600, subpasos=10, dt=0.013, k=0.28,
            mu=0.12, fuerza=1.0, h=0.26, radio_triangulo=1.0, semilla=1,
            con_frames=True):
    W, H = res
    n = W * H
    x, y, dominio = _malla(res, radio_triangulo)
    imx, imy = _imanes(radio_triangulo)
    vx = np.zeros(n, dtype=np.float32)
    vy = np.zeros(n, dtype=np.float32)

    # buffers reutilizados: cero asignaciones dentro del bucle caliente
    ax = np.empty(n, np.float32); ay = np.empty(n, np.float32)
    dx = np.empty(n, np.float32); dy = np.empty(n, np.float32)
    d2 = np.empty(n, np.float32); tmp = np.empty(n, np.float32)
    dmin = np.empty(n, np.float32)
    etiqueta = np.zeros(n, np.int8)

    h2 = np.float32(h * h)
    amort = np.float32(1.0 / (1.0 + mu * dt))
    dtf = np.float32(dt)
    kf = np.float32(-k)
    fz = np.float32(fuerza)

    colores = np.stack([hex_a_rgb(c) for c in COLORES_IMAN])   # (3,3) 0-255
    frames = (np.empty((pasos, H, W, 3), dtype=np.uint8)
              if con_frames else None)
    lienzo = np.empty((H, W, 3), np.float32) if con_frames else None
    plano = lienzo.reshape(n, 3) if con_frames else None
    convergidos = np.empty(pasos, dtype=np.float32)
    imx_px, imy_px = _a_pixeles(imx, imy, dominio, res)
    imanes_px = np.stack([imx_px, imy_px], axis=1)

    def campo():
        """Distancia al iman mas cercano + etiqueta, en dmin/etiqueta."""
        dmin[:] = np.inf
        for i in range(3):
            np.subtract(imx[i], x, out=dx)
            np.subtract(imy[i], y, out=dy)
            np.multiply(dx, dx, out=d2)
            np.multiply(dy, dy, out=tmp)
            np.add(d2, tmp, out=d2)
            mejor = d2 < dmin
            dmin[mejor] = d2[mejor]
            etiqueta[mejor] = i
        np.sqrt(dmin, out=dmin)

    for t in range(pasos):
        campo()
        # velocidad^2 -> brillo: corriendo = apagado, parado = encendido
        np.multiply(vx, vx, out=d2)
        np.multiply(vy, vy, out=tmp)
        np.add(d2, tmp, out=d2)
        quieto = (d2 < 0.0025) & (dmin < 0.10)
        convergidos[t] = quieto.mean()
        if con_frames:
            # brillo = 0.12 + 0.88/(1 + v^2/0.10): corriendo casi negro
            # (queda el fondo), parado a pleno color.
            np.multiply(d2, np.float32(1.0 / 0.10), out=tmp)
            np.add(tmp, np.float32(1.0), out=tmp)
            np.divide(np.float32(0.88), tmp, out=tmp)
            np.add(tmp, np.float32(0.12), out=tmp)
            np.take(colores, etiqueta, axis=0, out=plano)
            np.multiply(plano, tmp[:, None], out=plano)
            salpicar(lienzo, imanes_px, C_TINTA, peso=255.0, radio=1.4)
            np.clip(lienzo, 0.0, 255.0, out=lienzo)
            frames[t] = lienzo

        for _ in range(subpasos):
            np.multiply(x, kf, out=ax)
            np.multiply(y, kf, out=ay)
            for i in range(3):
                np.subtract(imx[i], x, out=dx)
                np.subtract(imy[i], y, out=dy)
                np.multiply(dx, dx, out=d2)
                np.multiply(dy, dy, out=tmp)
                np.add(d2, tmp, out=d2)
                np.add(d2, h2, out=d2)
                np.sqrt(d2, out=tmp)
                np.multiply(d2, tmp, out=d2)
                np.divide(fz, d2, out=tmp)
                np.multiply(dx, tmp, out=dx); np.add(ax, dx, out=ax)
                np.multiply(dy, tmp, out=dy); np.add(ay, dy, out=ay)
            np.multiply(ax, dtf, out=ax); np.add(vx, ax, out=vx)
            np.multiply(vx, amort, out=vx)
            np.multiply(ay, dtf, out=ay); np.add(vy, ay, out=vy)
            np.multiply(vy, amort, out=vy)
            np.multiply(vx, dtf, out=dx); np.add(x, dx, out=x)
            np.multiply(vy, dtf, out=dy); np.add(y, dy, out=y)

    # --- estado final ----------------------------------------------------
    campo()
    np.multiply(vx, vx, out=d2)
    np.multiply(vy, vy, out=tmp)
    np.add(d2, tmp, out=d2)
    sin_converger = int((~((d2 < 0.0025) & (dmin < 0.10))).sum())
    etq = etiqueta.reshape(H, W)

    frac = [float((etq == i).mean()) for i in range(3)]
    borde = np.zeros((H, W), dtype=bool)
    borde[:, :-1] |= etq[:, :-1] != etq[:, 1:]
    borde[:-1, :] |= etq[:-1, :] != etq[1:, :]
    dim = _dimension_cajas(borde)

    med = np.where(convergidos >= 0.5)[0]
    frame_mitad = int(med[0]) if med.size else -1

    cifras = {
        "fraccion_iman_violeta": round(frac[0], 4),
        "fraccion_iman_ambar": round(frac[1], 4),
        "fraccion_iman_verde": round(frac[2], 4),
        "dimension_frontera": round(dim, 3),
        "pixeles_frontera": int(borde.sum()),
        "pixeles_sin_converger": sin_converger,
        "frame_mitad_convergida": frame_mitad,
        "pendulos": n,
        "pasos_integrados": pasos * subpasos,
        "tiempo_simulado": round(pasos * subpasos * dt, 2),
    }

    # --- un pendulo pegado a la frontera, para dibujarlo vectorial -------
    #   se elige el pixel de frontera mas cercano al centro del lienzo
    #   entre los que tienen los tres imanes a menos de 3 px (frontera
    #   "gorda": donde las tres cuencas se tocan).
    rng = np.random.default_rng(semilla)
    ys, xs = np.nonzero(borde)
    vecinos3 = np.zeros(borde.shape, dtype=np.int16)
    for i in range(3):
        m = (etq == i).astype(np.int16)
        acc = np.zeros_like(m)
        for dyi in (-3, 0, 3):
            for dxi in (-3, 0, 3):
                acc |= np.roll(np.roll(m, dyi, axis=0), dxi, axis=1)
        vecinos3 += acc
    triple = borde & (vecinos3 == 3)
    if triple.any():
        ys3, xs3 = np.nonzero(triple)
    else:
        ys3, xs3 = ys, xs
    d_centro = (xs3 - W / 2) ** 2 + (ys3 - H * 0.42) ** 2
    orden = np.argsort(d_centro)
    elegido = orden[min(len(orden) - 1, int(rng.integers(0, 8)))]
    pxq, pyq = int(xs3[elegido]), int(ys3[elegido])

    x0, x1, y0, y1 = dominio
    xq = x0 + (x1 - x0) * pxq / (W - 1)
    yq = y1 - (y1 - y0) * pyq / (H - 1)
    cam = _trayectoria_de(xq, yq, imx.astype(np.float64), imy.astype(np.float64),
                          dt, subpasos, pasos, k, mu, fuerza, h)
    tpx, tpy = _a_pixeles(cam[:, 0], cam[:, 1], dominio, res)
    trayectoria = np.stack([tpx, tpy], axis=1).astype(np.float32)

    extra = {
        "imanes_px": imanes_px.astype(np.float32),
        "colores": np.array(COLORES_IMAN, dtype=object),
        "trayectoria": trayectoria,
        "trayectoria_px": np.array([pxq, pyq], dtype=np.int32),
        "trayectoria_iman": int(etq[pyq, pxq]),
        "convergidos": convergidos,
        "dominio": np.array(dominio, dtype=np.float32),
        "zoom_frontera": np.array([pxq / (W - 1), pyq / (H - 1)],
                                  dtype=np.float32),
    }
    return frames, cifras, extra


def simular(res=(360, 640), pasos=600, subpasos=10, dt=0.013, k=0.28,
            mu=0.12, fuerza=1.0, h=0.26, radio_triangulo=1.0, semilla=1):
    """Pila (T,H,W,3) del mapa de cuencas naciendo. T = `pasos` (600).

    Cada frame pinta cada pixel con el iman al que su pendulo esta mas
    cerca en ese instante; el brillo cae con la velocidad, asi que el mapa
    hierve mientras corren y cuaja cuando se paran.
    """
    frames, cifras, extra = _correr(res=res, pasos=pasos, subpasos=subpasos,
                                    dt=dt, k=k, mu=mu, fuerza=fuerza, h=h,
                                    radio_triangulo=radio_triangulo,
                                    semilla=semilla, con_frames=True)
    return {"frames": validar_pila(frames), "cifras": cifras, "extra": extra}


def medir(res=(360, 640), pasos=600, subpasos=10, dt=0.013, k=0.28, mu=0.12,
          fuerza=1.0, h=0.26, radio_triangulo=1.0, semilla=1):
    """Solo las cifras (sin pila de frames), para la sonda."""
    _, cifras, _ = _correr(res=res, pasos=pasos, subpasos=subpasos, dt=dt,
                           k=k, mu=mu, fuerza=fuerza, h=h,
                           radio_triangulo=radio_triangulo, semilla=semilla,
                           con_frames=False)
    return cifras


__all__ = ["simular", "medir", "COLORES_IMAN"]

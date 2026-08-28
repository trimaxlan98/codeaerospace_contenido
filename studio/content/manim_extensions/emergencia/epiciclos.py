# =====================================================================
# emergencia/epiciclos.py — clip 11 "los epiciclos" (curso 29, vertical).
#
# QUE SIMULA
# La silueta de la palabra CO.DE como UN SOLO contorno cerrado, su
# transformada de Fourier discreta, y la reconstruccion con N circulos que
# giran uno sobre la punta del anterior. Cada "vuelta" de la animacion usa
# mas circulos: con 1 sale una circunferencia, con 2 una elipse torcida,
# con 100 ya se lee la marca.
#
# REGLAS (las tres lineas del HUD)
#   1. el contorno es una funcion compleja z(t) con t = 0..1
#   2. su DFT da un radio y una velocidad por circulo
#   3. N circulos encadenados: el error cae, el dibujo aparece
#
# EL CONTORNO (decision, sin fuentes ni PIL)
# Las letras se construyen a mano en pixeles: C, O y D son el "ribete"
# (offset a izquierda y derecha con casquetes) de una polilinea de arcos
# —la O y la D llevan una rendija de ~3 px que los casquetes tapan, para
# que cada letra sea UN contorno cerrado sin agujero—; el punto es una
# circunferencia y la E un poligono de 12 vertices. Las cinco letras se
# encadenan en un unico contorno cerrado con puentes por debajo: los
# cuatro puentes de ida quedan a y_puente y el de vuelta 7 px mas abajo,
# asi que el trazo remata con un doble subrayado (es deliberado: no hay
# forma de cerrar una palabra sin volver). NO se usa PIL ni ninguna fuente
# externa: `_contorno_code()` es geometria pura.
#
# COLORES POR ROL: cian (C_MEDIDO) el trazo reconstruido —es lo medido—,
# ambar (C_REGLA) los circulos y los radios —son la regla en accion—,
# violeta (C_ORDEN) el contorno objetivo de fondo, sobre C_FONDO.
#
# COSTE MEDIDO (contenedor, 2026-08-28): res=(270,480), T=800, 8 vueltas
# (1,2,5,10,25,50,100,200 circulos), M=2048 puntos: 5.6 s de CPU y
# 311.0 MB de pila. `medir()` solo, 0.3 s. Tope del contrato: 90 s / 1 GB.
#
# CIFRAS (medidas sobre la reconstruccion, en pixeles del lienzo 270x480)
#   error_rms_px_con_N para cada N de la secuencia (1,2,5,10,25,50,100,200)
#   circulos_para_1px : minimo N con error RMS < 1 px (medido barriendo
#       N = 1..512). Con este contorno da 100 justos.
#   error_rms_px_final, puntos_contorno (2048),
#   longitud_contorno_px (1689.7), circulos_barridos
#   Valores medidos: 53.9 / 41.5 / 29.8 / 19.5 / 8.48 / 2.50 / 0.991 /
#   0.325 px para 1, 2, 5, 10, 25, 50, 100 y 200 circulos.
#
# EXTRA (para dibujar los circulos VECTORIALES encima, mas nitidos)
#   centros     (T, Nmax, 2) float32  centro de cada circulo por frame, en
#                                     pixeles; NaN en los circulos que esa
#                                     vuelta no usa
#   radios      (Nmax,) float32       radio de cada circulo (fijo)
#   frecuencias (Nmax,) int32         vueltas por recorrido de cada circulo
#   punta       (T, 2) float32        punta del ultimo circulo (el lapiz)
#   circulos_activos (T,) int32       cuantos circulos hay vivos en el frame
#   contorno    (M, 2) float32        el objetivo en pixeles
#   secuencia   (V,) int32            los N de cada vuelta
#   vuelta_de_frame (T,) int32        que vuelta esta corriendo cada frame
#   error_por_vuelta (V,) float32     error RMS de cada vuelta
#   traza_de_vuelta (V, M, 2) float32 el trazo completo de cada vuelta
# =====================================================================
import numpy as np

from . import (C_FONDO, C_MEDIDO, C_ORDEN, C_REGLA, hex_a_rgb, salpicar,
               estela, a_uint8, validar_pila)

SECUENCIA = (1, 2, 5, 10, 25, 50, 100, 200)


# --- geometria de la palabra ---------------------------------------------
def _densificar(pts, paso=0.8):
    """Polilinea (m,2) -> polilinea con vertices a <= `paso` px."""
    pts = np.asarray(pts, dtype=np.float64)
    salida = []
    for a, b in zip(pts[:-1], pts[1:]):
        d = float(np.hypot(*(b - a)))
        n = max(1, int(np.ceil(d / paso)))
        s = np.linspace(0.0, 1.0, n, endpoint=False)[:, None]
        salida.append(a + (b - a) * s)
    salida.append(pts[-1:])
    return np.concatenate(salida, axis=0)


def _arco(cx, cy, rx, ry, g0, g1, paso=0.8):
    """Arco de elipse de g0 a g1 grados (sentido creciente)."""
    n = max(8, int(np.ceil(abs(g1 - g0) / 360.0 * 2 * np.pi
                           * max(rx, ry) / paso)))
    a = np.radians(np.linspace(g0, g1, n))
    return np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], axis=1)


def _ribete(centro, semiancho, paso=0.8):
    """Contorno cerrado alrededor de una polilinea abierta (el "trazo")."""
    P = _densificar(centro, paso)
    d = np.diff(P, axis=0)
    largo = np.hypot(d[:, 0], d[:, 1])[:, None]
    largo[largo < 1e-9] = 1e-9
    t = d / largo
    tv = np.empty_like(P)
    tv[0] = t[0]
    tv[-1] = t[-1]
    tv[1:-1] = t[:-1] + t[1:]
    nrm = np.hypot(tv[:, 0], tv[:, 1])[:, None]
    nrm[nrm < 1e-9] = 1e-9
    tv /= nrm
    nv = np.stack([-tv[:, 1], tv[:, 0]], axis=1)
    izq = P + semiancho * nv
    der = P - semiancho * nv
    a_fin = np.arctan2(nv[-1, 1], nv[-1, 0])
    a_ini = np.arctan2(nv[0, 1], nv[0, 0])
    cap_fin = _arco(P[-1, 0], P[-1, 1], semiancho, semiancho,
                    np.degrees(a_fin), np.degrees(a_fin) - 180.0, paso)
    cap_ini = _arco(P[0, 0], P[0, 1], semiancho, semiancho,
                    np.degrees(a_ini) + 180.0, np.degrees(a_ini), paso)
    return np.concatenate([izq, cap_fin, der[::-1], cap_ini], axis=0)


def _glifos(alto=62.0, grosor=4.6):
    """Las cinco letras de CO.DE como contornos cerrados, en coordenadas
    matematicas (y hacia arriba) centradas en el origen de cada caja."""
    hh = alto / 2 - grosor                   # semialto de la linea media
    cajas = [(27.0, 44.0), (77.0, 46.0), (129.0, 16.0),
             (151.0, 46.0), (203.0, 40.0)]
    g = []

    # C: arco abierto a la derecha
    x0, w = cajas[0]
    g.append(_ribete(_arco(x0 + w / 2, 0.0, w / 2 - grosor, hh, 56, 304),
                     grosor))

    # O: elipse casi cerrada (rendija de 10 grados abajo, tapada por los caps)
    x0, w = cajas[1]
    g.append(_ribete(_arco(x0 + w / 2, 0.0, w / 2 - grosor, hh, -85, 265),
                     grosor))

    # punto: circunferencia
    x0, w = cajas[2]
    g.append(_arco(x0 + w / 2, -alto / 2 + 5.5, 5.5, 5.5, 0, 360))

    # D: barra izquierda + panza, con rendija abajo a la izquierda
    x0, w = cajas[3]
    xi = x0 + grosor
    xq = x0 + 20.0
    d = [np.array([[xi, -hh]]),
         np.array([[xi, hh], [xq, hh]]),
         _arco(xq, 0.0, x0 + w - grosor - xq, hh, 90, -90),
         np.array([[xi + 3.6, -hh]])]
    g.append(_ribete(np.concatenate(d, axis=0), grosor))

    # E: poligono de 12 vertices
    x0, w = cajas[4]
    s = 2 * grosor
    H2 = alto / 2
    e = [(x0, H2), (x0 + w, H2), (x0 + w, H2 - s), (x0 + s, H2 - s),
         (x0 + s, s / 2), (x0 + w * 0.84, s / 2), (x0 + w * 0.84, -s / 2),
         (x0 + s, -s / 2), (x0 + s, -H2 + s), (x0 + w, -H2 + s),
         (x0 + w, -H2), (x0, -H2), (x0, H2)]
    g.append(_densificar(np.array(e, dtype=np.float64)))
    return g, cajas


def _contorno_code(res=(270, 480), alto=62.0, grosor=4.6, cy=232.0):
    """Un unico contorno cerrado con la palabra CO.DE, en pixeles."""
    W, H = res
    glifos, cajas = _glifos(alto, grosor)
    y_puente = -alto / 2 - 11.0
    y_vuelta = y_puente - 7.0

    anclas = []
    rotados = []
    for (x0, w), c in zip(cajas, glifos):
        obj = np.array([x0 + w / 2, -alto / 2 - 4.0])
        i = int(np.argmin(((c - obj) ** 2).sum(axis=1)))
        rotados.append(np.roll(c, -i, axis=0))
        anclas.append(rotados[-1][0].copy())

    trozos = []
    for i, c in enumerate(rotados):
        trozos.append(c)
        trozos.append(c[:1])                            # cerrar el glifo
        if i < len(rotados) - 1:
            a, b = anclas[i], anclas[i + 1]
            trozos.append(_densificar(np.array(
                [a, [a[0], y_puente], [b[0], y_puente], b])))
        else:
            a, b = anclas[i], anclas[0]
            trozos.append(_densificar(np.array(
                [a, [a[0], y_vuelta], [b[0], y_vuelta], b])))
    camino = np.concatenate(trozos, axis=0)
    camino[:, 1] = cy - camino[:, 1]                    # a pixeles (y abajo)
    dx = (W - 270.0) / 2.0
    camino[:, 0] += dx
    return camino


def _remuestrear(camino, M):
    """Remuestreo uniforme por longitud de arco de un contorno cerrado."""
    c = np.concatenate([camino, camino[:1]], axis=0)
    d = np.hypot(np.diff(c[:, 0]), np.diff(c[:, 1]))
    s = np.concatenate([[0.0], np.cumsum(d)])
    total = s[-1]
    u = np.linspace(0.0, total, M, endpoint=False)
    return np.stack([np.interp(u, s, c[:, 0]), np.interp(u, s, c[:, 1])],
                    axis=1), float(total)


# --- Fourier --------------------------------------------------------------
def _serie(contorno):
    """Coeficientes DFT ordenados: continua, +1, -1, +2, -2, ..."""
    M = len(contorno)
    z = contorno[:, 0] + 1j * contorno[:, 1]
    c = np.fft.fft(z) / M
    k = np.fft.fftfreq(M, d=1.0 / M).astype(np.int64)
    orden = np.argsort(np.abs(k) * 2 + (k < 0).astype(np.int64))
    return c[orden], k[orden], z


def _errores(coef, frec, z, hasta):
    """RMS (px) de la reconstruccion con 1..hasta circulos, en los mismos
    M instantes del contorno."""
    M = len(z)
    t = np.arange(M) / M
    rec = np.full(M, coef[0], dtype=np.complex128)
    err = np.empty(hasta + 1, dtype=np.float64)
    err[0] = float(np.sqrt(np.mean(np.abs(rec - z) ** 2)))
    for m in range(1, hasta + 1):
        rec = rec + coef[m] * np.exp(2j * np.pi * frec[m] * t)
        err[m] = float(np.sqrt(np.mean(np.abs(rec - z) ** 2)))
    return err


def _cadena(coef, frec, n, t):
    """Centros (len(t), n, 2) de los n circulos y punta (len(t), 2)."""
    t = np.atleast_1d(np.asarray(t, dtype=np.float64))
    fases = np.exp(2j * np.pi * np.outer(t, frec[1:n + 1]))
    terminos = fases * coef[1:n + 1][None, :]
    p = np.empty((len(t), n + 1), dtype=np.complex128)
    p[:, 0] = coef[0]
    np.cumsum(terminos, axis=1, out=p[:, 1:])
    p[:, 1:] += coef[0]
    return p


def _correr(res=(270, 480), pasos=800, secuencia=SECUENCIA, M=2048,
            semilla=1, con_frames=True, barrido=512):
    W, H = res
    if abs(H / W - 16.0 / 9.0) > 1e-6:
        raise ValueError(f"res {res} no es 9:16 (H/W = {H / W:.4f})")
    secuencia = tuple(int(s) for s in secuencia)
    nmax = max(secuencia)

    camino = _contorno_code(res=res)
    contorno, largo = _remuestrear(camino, M)
    coef, frec, z = _serie(contorno)
    barrido = int(min(barrido, M // 2 - 1))
    err = _errores(coef, frec, z, max(barrido, nmax))
    bajo = np.where(err[1:] < 1.0)[0]
    circulos_1px = int(bajo[0] + 1) if bajo.size else -1

    cifras = {("error_rms_px_con_%d" % n): round(float(err[n]), 3)
              for n in secuencia}
    cifras.update({
        "circulos_para_1px": circulos_1px,
        "n_para_1px": circulos_1px,       # el nombre que usa la sonda
        "error_rms_px_final": round(float(err[nmax]), 3),
        "puntos_contorno": int(M),
        "longitud_contorno_px": round(largo, 1),
        "circulos_barridos": int(max(barrido, nmax)),
    })

    # reparto de frames por vuelta: las ultimas duran mas
    peso = np.linspace(0.8, 2.2, len(secuencia)) ** 1.15
    cuota = np.maximum(12, np.round(peso / peso.sum() * pasos).astype(int))
    cuota[-1] += pasos - int(cuota.sum())
    if cuota[-1] < 12:                                   # reparto de rescate
        cuota = np.full(len(secuencia), pasos // len(secuencia))
        cuota[-1] += pasos - int(cuota.sum())

    centros = np.full((pasos, nmax, 2), np.nan, dtype=np.float32)
    punta = np.empty((pasos, 2), dtype=np.float32)
    activos = np.empty(pasos, dtype=np.int32)
    vuelta_de_frame = np.empty(pasos, dtype=np.int32)
    trazas = np.empty((len(secuencia), M, 2), dtype=np.float32)

    frames = (np.empty((pasos, H, W, 3), dtype=np.uint8)
              if con_frames else None)
    if con_frames:
        base = np.empty((H, W, 3), np.float32)
        base[:] = hex_a_rgb(C_FONDO) / 255.0
        salpicar(base, contorno, C_ORDEN, peso=0.34, radio=0.9)
        np.clip(base, 0.0, 1.0, out=base)
        traza = np.zeros((H, W, 3), np.float32)
        lienzo = np.empty((H, W, 3), np.float32)

    tt = np.arange(M) / M
    k = 0
    for v, n in enumerate(secuencia):
        cad = _cadena(coef, frec, n, tt)
        trazas[v] = np.stack([cad[:, n].real, cad[:, n].imag], axis=1)
        nf = int(cuota[v])
        # subpasos por frame para que el lapiz deje trazo continuo (<0.7 px)
        largo_v = float(np.hypot(*np.diff(np.concatenate(
            [trazas[v], trazas[v][:1]]), axis=0).T).sum())
        sub = int(np.clip(np.ceil(largo_v / nf / 0.7), 4, 96))
        for j in range(nf):
            t0 = j / nf
            t1 = (j + 1) / nf
            ts = np.linspace(t0, t1, sub, endpoint=False)
            c = _cadena(coef, frec, n, ts)
            centros[k, :n] = np.stack([c[-1, :n].real, c[-1, :n].imag],
                                      axis=1)
            punta[k] = (c[-1, n].real, c[-1, n].imag)
            activos[k] = n
            vuelta_de_frame[k] = v
            if con_frames:
                if j < 10:
                    estela(traza, 0.68)
                pts = np.stack([c[:, n].real, c[:, n].imag], axis=1)
                salpicar(traza, pts, C_MEDIDO, peso=0.30, radio=1.0)
                np.clip(traza, 0.0, 1.0, out=traza)
                np.copyto(lienzo, base)
                np.add(lienzo, traza, out=lienzo)
                ejes = np.stack([c[-1].real, c[-1].imag], axis=1)
                salpicar(lienzo, _densificar(ejes, 1.1), C_REGLA,
                         peso=0.75, radio=0.8)
                aro = _aros(ejes, np.abs(coef[1:n + 1]))
                if len(aro):
                    salpicar(lienzo, aro, C_REGLA, peso=0.42, radio=0.8)
                salpicar(lienzo, ejes[-1:], C_MEDIDO, peso=1.8, radio=2.2)
                frames[k] = a_uint8(lienzo)
            k += 1

    extra = {
        "centros": centros,
        "radios": np.abs(coef[1:nmax + 1]).astype(np.float32),
        "frecuencias": frec[1:nmax + 1].astype(np.int32),
        "punta": punta,
        "circulos_activos": activos,
        "contorno": contorno.astype(np.float32),
        "secuencia": np.array(secuencia, dtype=np.int32),
        "vuelta_de_frame": vuelta_de_frame,
        "error_por_vuelta": np.array([err[n] for n in secuencia],
                                     dtype=np.float32),
        "traza_de_vuelta": trazas,
        "frames_por_vuelta": cuota.astype(np.int32),
        "error_por_circulos": err.astype(np.float32),
    }
    return frames, cifras, extra


def _aros(centros, radios, paso=1.6):
    """Puntos de las circunferencias que valen la pena dibujar (r > 1.5 px)."""
    sel = np.nonzero(radios > 1.5)[0]
    if not len(sel):
        return np.zeros((0, 2))
    trozos = []
    for i in sel:
        r = float(radios[i])
        n = max(10, int(2 * np.pi * r / paso))
        a = np.linspace(0.0, 2 * np.pi, n, endpoint=False)
        trozos.append(np.stack([centros[i, 0] + r * np.cos(a),
                                centros[i, 1] + r * np.sin(a)], axis=1))
    return np.concatenate(trozos, axis=0)


def simular(res=(270, 480), pasos=800, secuencia=SECUENCIA, M=2048,
            semilla=1):
    """Pila (T,H,W,3) de los epiciclos dibujando CO.DE. T = `pasos` (800),
    repartidos en una vuelta por cada N de `secuencia` (las ultimas duran
    mas). El trazo cian se borra con estela al empezar cada vuelta."""
    frames, cifras, extra = _correr(res=res, pasos=pasos,
                                    secuencia=secuencia, M=M,
                                    semilla=semilla, con_frames=True)
    return {"frames": validar_pila(frames), "cifras": cifras, "extra": extra}


def medir(res=(270, 480), pasos=800, secuencia=SECUENCIA, M=2048, semilla=1):
    """Solo las cifras (sin pila de frames), para la sonda."""
    _, cifras, _ = _correr(res=res, pasos=pasos, secuencia=secuencia, M=M,
                           semilla=semilla, con_frames=False)
    return cifras


__all__ = ["simular", "medir", "SECUENCIA"]

# =====================================================================
# ondas — clip 06 "el tanque de ondas".
#
# Que simula: la ecuacion de onda 2D  u_tt = c^2 (u_xx + u_yy)  por
# diferencias finitas (leapfrog de segundo orden, 5 puntos), sobre una
# malla el DOBLE de fina que el lienzo (540x960 celdas utiles para
# 270x480) que se submuestrea 2x2 al pintar. Una fuente puntual senoidal
# abajo emite frentes circulares; a un tercio de la altura hay una pared
# opaca (Dirichlet u=0) con dos rendijas; alrededor, FUERA del encuadre,
# hay un marco amortiguador que se traga las ondas sin rebotarlas.
#
# Reglas (las tres lineas del HUD):
#   1. cada celda tira de sus cuatro vecinas, con inercia;
#   2. la pared no deja pasar nada salvo por las dos rendijas;
#   3. los bordes se tragan la onda: no hay eco.
#
# Guion: fase 1 (28 % de la pieza) la fuente sola, frentes circulares
# limpios; en el frame `frame_pared` entra la pared y del otro lado nacen
# las franjas de interferencia, que se miden en el ultimo tercio con un
# detector sincrono (lock-in) a la frecuencia de la fuente.
#
# Coste medido en el contenedor (2026-08-28), simular() por defecto:
#   T = 750 frames, res 270x480, malla 660x1080 (marco incluido),
#   2250 pasos -> 23-31 s de CPU segun carga, pila de 291.6 MB.
#   medir() (sin pintar): 11-19 s.
#
# Cifras (medidas sobre lo simulado):
#   franjas_medido_px        46.12  (5 franjas detectadas en la linea
#                                     lejana, por deteccion sincrona)
#   franjas_teorico_px       44.55  (lambda_medida * L / d)
#   franjas_fresnel_px       45.56  (condicion exacta r1 - r2 = m*lambda)
#   longitud_onda_medida_px  13.98  (crestas del campo, por FFT)
#
# La medida sale un 3.5 % por encima de la formula de libro y NO es un
# error de la simulacion: lambda*L/d es la aproximacion PARAXIAL, y aqui
# sin(theta_1) = lambda/d = 0.146 con L = 306 px < d^2/lambda = 659 px
# (zona de Fresnel). Resolviendo la condicion exacta de camino,
# r1 - r2 = m*lambda, salen 45.56 px, a 0.6 px de lo medido: la fisica
# esta bien y lo que se queda corto es la formula. Las cuatro cifras van
# juntas a proposito; el clip puede enseñar dos y dejar la tercera de
# nota al pie.
#
# Las longitudes por defecto (lambda, d, marco) estan en pixeles del
# lienzo de (270, 480). Medido tambien a (360, 640) con pasos=750:
# 35.7 s, pila de 518 MB, 5 franjas, medido 61.62 / teorico 59.41 /
# Fresnel 62.49 px. Como las longitudes NO se reescalan con el lienzo, el
# encuadre no es el mismo: para reproducirlo hay que pasar lam_px=18.7 y
# sep_px=128. Ojo tambien con `pasos`: cuanto mas alto es el lienzo, mas
# tarda el frente en llegar a la linea; por debajo del minimo el modulo
# aborta con un ValueError en vez de devolver un nan.
#
# Notas de imagen: el campo se pinta con la LUT divergente "vorticidad"
# (violeta lo negativo, naranja lo positivo, fondo el cero). Antes de
# colorear se compensa la divergencia cilindrica (la amplitud de una onda
# circular cae como 1/sqrt(r)) con una ganancia sqrt(r/r0) topada a 3, y
# se comprime con gamma 0.55: es maquillaje de VISUALIZACION, no toca la
# fisica ni las cifras. La pared va en gris C_MOBILIARIO y la linea de
# medicion en cian punteado (C_MEDIDO: lo unico medido en pantalla).
# =====================================================================
import numpy as np

from . import (C_FONDO, C_MEDIDO, C_MOBILIARIO, C_TINTA, LUTS, RES_BASE,
               colorear, hex_a_rgb, validar_pila)

# Geometria en fracciones de la altura del lienzo.
F_FUENTE = 0.9167          # fuente puntual (y = 440 si H = 480)
F_PARED = 0.7208           # pared con rendijas (y = 346): ~1/3 desde abajo
F_LINEA = 0.0833           # linea donde se mide la intensidad (y = 40)

SIGMA_MAX = 0.35           # amortiguacion maxima del marco absorbente


def _geometria(res, escala, lam_px, sep_px, ancho_px, marco_px, grosor_px):
    """Toda la geometria, en pixeles del LIENZO y en celdas de la malla.

    La malla es mas grande que el encuadre: `marco_px` de margen por los
    cuatro lados, ocupado entero por la capa absorbente, de modo que el
    espectador nunca ve la esponja. La coordenada de canto de un pixel
    visible v es  v*escala + o  en la malla, con o = marco_px*escala.
    """
    W, H = int(res[0]), int(res[1])
    if abs(H / W - 16.0 / 9.0) > 1e-6:
        raise ValueError(f"la resolucion {res} no es 9:16")
    f = int(escala)
    o = int(round(marco_px * f))
    g = {
        "W": W, "H": H, "f": f, "o": o,
        "Wf": W * f + 2 * o, "Hf": H * f + 2 * o,
        "y_fuente": int(round(F_FUENTE * H)),
        "y_pared": int(round(F_PARED * H)),
        "y_linea": int(round(F_LINEA * H)),
        "x_centro": W / 2.0,
        "lam_px": float(lam_px), "sep_px": float(sep_px),
        "ancho_px": float(ancho_px), "marco_px": float(marco_px),
        "grosor_px": float(grosor_px),
    }
    g["x_rendija_1"] = g["x_centro"] - sep_px / 2.0
    g["x_rendija_2"] = g["x_centro"] + sep_px / 2.0
    g["L_px"] = float(g["y_pared"] - g["y_linea"])
    return g


def _mascaras(g):
    """(libre, sigma) sobre la malla fina.

    `libre` vale 0 dentro de la pared y 1 fuera (Dirichlet u = 0: pared
    opaca). `sigma` es el perfil de la esponja: 0 en el encuadre y
    creciente al cubo hacia los cantos de la malla.
    """
    f, o, Wf, Hf = g["f"], g["o"], g["Wf"], g["Hf"]

    # --- pared con dos rendijas (comparaciones simetricas) -----------
    cx = np.arange(Wf) + 0.5
    cy = np.arange(Hf) + 0.5
    grosor_f = max(2.0, g["grosor_px"] * f)
    fila = np.abs(cy - (g["y_pared"] * f + o)) < grosor_f / 2.0
    med = g["ancho_px"] * f / 2.0
    hueco = np.zeros(Wf, dtype=bool)
    for xc in (g["x_rendija_1"], g["x_rendija_2"]):
        hueco |= np.abs(cx - (xc * f + o)) <= med
    solido = fila[:, None] & (~hueco)[None, :]
    libre = (~solido).astype(np.float32)

    # --- esponja: solo en el margen, rampa cubica --------------------
    dx = np.minimum(np.arange(Wf), Wf - 1 - np.arange(Wf))
    dy = np.minimum(np.arange(Hf), Hf - 1 - np.arange(Hf))
    dist = np.minimum(dx[None, :], dy[:, None]).astype(np.float32)
    n = max(float(o), 1.0)
    sigma = (np.clip((n - dist) / n, 0.0, 1.0) ** 3).astype(np.float32)
    return libre, solido, sigma


def _lambda_por_fft(perfil):
    """Longitud de onda (en celdas) de un corte 1D, por FFT con relleno de
    ceros e interpolacion parabolica del pico."""
    v = np.asarray(perfil, dtype=np.float64)
    v = (v - v.mean()) * np.hanning(len(v))
    N = 4096
    esp = np.abs(np.fft.rfft(v, N))
    esp[0] = 0.0
    k = int(np.argmax(esp))
    if 0 < k < len(esp) - 1:
        a, b, c = esp[k - 1], esp[k], esp[k + 1]
        den = a - 2 * b + c
        k = k + (0.5 * (a - c) / den if abs(den) > 1e-12 else 0.0)
    return float(N / k) if k > 0 else float("nan")


def _picos(perfil, x0, x1, umbral=0.06, dmin=1):
    """Maximos locales de `perfil` en [x0, x1) por encima de `umbral` veces
    el maximo del tramo, con supresion de no maximos a menos de `dmin`
    muestras (una franja cuenta una sola vez aunque su cresta ondule)."""
    v = np.asarray(perfil, dtype=np.float64)
    tramo = v[x0:x1]
    if tramo.size == 0 or tramo.max() <= 0:
        return np.array([], dtype=int)
    lim = umbral * tramo.max()
    interior = v[1:-1]
    es = (interior > v[:-2]) & (interior >= v[2:]) & (interior > lim)
    idx = np.nonzero(es)[0] + 1
    idx = idx[(idx >= x0) & (idx < x1)]
    if len(idx) < 2 or dmin <= 1:
        return idx
    guardados = []
    for i in idx[np.argsort(-v[idx])]:
        if all(abs(int(i) - j) >= dmin for j in guardados):
            guardados.append(int(i))
    return np.array(sorted(guardados), dtype=int)


def _suavizar(v, sigma):
    """Convolucion gaussiana 1D con cantos replicados."""
    r = max(1, int(round(3 * sigma)))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    return np.convolve(np.pad(v, r, mode="edge"), k, mode="valid")


def _franjas_fresnel(lam, d, L, x_c, limite):
    """Posiciones exactas de los maximos de dos rendijas, resolviendo la
    condicion de camino r1 - r2 = m*lambda (sin aproximar angulos), en la
    mitad derecha; devuelve las posiciones simetricas dentro de
    |x - x_c| <= limite."""
    x = np.linspace(x_c, x_c + 4 * limite + 4 * L, 20000)
    r1 = np.hypot(x - (x_c - d / 2.0), L)
    r2 = np.hypot(x - (x_c + d / 2.0), L)
    delta = r1 - r2                       # crece de 0 a d, monotona
    pos = [x_c]
    m = 1
    while m * lam < delta[-1]:
        xm = float(np.interp(m * lam, delta, x))
        if xm - x_c > limite:
            break
        pos = [2 * x_c - xm] + pos + [xm]
        m += 1
    return np.array(sorted(pos))


def _correr(pasos, res, lam_px, sep_px, ancho_px, marco_px, grosor_px,
            escala, subpasos, cfl, amplitud, gamma, guardar):
    g = _geometria(res, escala, lam_px, sep_px, ancho_px, marco_px,
                   grosor_px)
    W, H, f, o = g["W"], g["H"], g["f"], g["o"]
    Wf, Hf = g["Wf"], g["Hf"]
    T = int(pasos)
    frame_pared = int(round(0.28 * T))

    libre, solido, sigma = _mascaras(g)
    dt = float(cfl)                     # c = 1, dx = 1  =>  dt = CFL
    if dt > 0.70:
        raise ValueError("CFL > 1/sqrt(2): el leapfrog 2D explota")
    C2 = np.float32(dt * dt)
    sd = (sigma * (SIGMA_MAX * dt)).astype(np.float32)
    A = (1.0 / (1.0 + sd)).astype(np.float32)
    B = (1.0 - sd).astype(np.float32)
    vel_px = subpasos * dt / f          # avance del frente, px de lienzo

    # --- fuente: blob gaussiano subcelda, fuente blanda (aditiva) ----
    om = 2.0 * np.pi / (g["lam_px"] * f)
    cxf = g["x_centro"] * f + o         # coordenada de canto en la malla
    cyf = g["y_fuente"] * f + o
    ix0, iy0 = int(np.floor(cxf)), int(np.floor(cyf))
    fx, fy = cxf - (ix0 + 0.5), cyf - (iy0 + 0.5)
    rr = 3
    yy, xx = np.mgrid[-rr:rr + 1, -rr:rr + 1]
    blob = np.exp(-((xx - fx) ** 2 + (yy - fy) ** 2)
                  / (2.0 * 1.5 ** 2)).astype(np.float32)
    blob /= blob.max()
    rampa = 2.0 * g["lam_px"] * f       # 2 periodos de encendido suave

    u = np.zeros((Hf, Wf), dtype=np.float32)
    up = np.zeros_like(u)
    un = np.zeros_like(u)
    lap = np.zeros((Hf - 2, Wf - 2), dtype=np.float32)

    # --- ventanas de medicion ----------------------------------------
    y_linea_f = int(g["y_linea"] * f + o)
    # el promedio no arranca hasta que el patron nuevo ha llegado a la
    # linea Y el campo viejo de la fase 1 ha salido del encuadre
    k_medir = frame_pared + int(g["L_px"] / vel_px) + 30
    if T - k_medir < 40:
        raise ValueError(
            f"pasos={T} no da: el frente tarda {k_medir} frames en llegar "
            f"a la linea de medicion y hacen falta 40 mas para promediar; "
            f"sube pasos a {k_medir + 40} o mas, o sube subpasos")
    k_lambda = max(10, frame_pared - 15)
    acc_c = np.zeros(Wf, dtype=np.float64)   # deteccion sincrona: separa
    acc_s = np.zeros(Wf, dtype=np.float64)   # la amplitud estacionaria
    n_acum = 0
    corte_lambda = None

    # --- pintado ------------------------------------------------------
    if guardar:
        frames = np.empty((T, H, W, 3), dtype=np.uint8)
        ys, xs = np.mgrid[0:H, 0:W]
        r = np.sqrt((xs + 0.5 - g["x_centro"]) ** 2
                    + (ys + 0.5 - g["y_fuente"]) ** 2).astype(np.float32)
        ganancia = np.clip(np.sqrt(r / 40.0), 0.25, 3.0).astype(np.float32)
        gris, cian = hex_a_rgb(C_MOBILIARIO), hex_a_rgb(C_MEDIDO)
        fondo, tinta = hex_a_rgb(C_FONDO), hex_a_rgb(C_TINTA)
        vis = solido[o:o + H * f, o:o + W * f]
        pared_coarse = vis.reshape(H, f, W, f).any(axis=(1, 3))
        # canto superior de la pared, un tono mas claro: sin el, el gris
        # oscuro se pierde contra el naranja saturado del campo
        canto = pared_coarse & ~np.roll(pared_coarse, 1, axis=0)
        gris_canto = gris + (tinta - gris) * 0.45
        raya = (np.arange(W) % 9) < 5
        escala_vis = 1e-6
    else:
        frames = None

    t = 0.0
    for k in range(T):
        pared_on = k >= frame_pared
        if k == frame_pared:
            u *= libre
            up *= libre
        for _ in range(subpasos):
            np.add(u[:-2, 1:-1], u[2:, 1:-1], out=lap)
            lap += u[1:-1, :-2]
            lap += u[1:-1, 2:]
            lap -= 4.0 * u[1:-1, 1:-1]
            un[1:-1, 1:-1] = A[1:-1, 1:-1] * (
                2.0 * u[1:-1, 1:-1] - B[1:-1, 1:-1] * up[1:-1, 1:-1]
                + C2 * lap)
            un[0, :] = 0.0
            un[-1, :] = 0.0
            un[:, 0] = 0.0
            un[:, -1] = 0.0
            t += dt
            amp = amplitud * min(1.0, t / rampa) * np.sin(om * t)
            un[iy0 - rr:iy0 + rr + 1, ix0 - rr:ix0 + rr + 1] += amp * blob
            if pared_on:
                un *= libre
            up, u, un = u, un, up

        if k == k_lambda:
            a = int(g["y_pared"] * f + o) + 16
            b = int(g["y_fuente"] * f + o) - 30
            corte_lambda = u[a:b, ix0].copy()
        if k >= k_medir:
            fila = u[y_linea_f, :].astype(np.float64)
            acc_c += fila * np.cos(om * t)
            acc_s += fila * np.sin(om * t)
            n_acum += 1

        if guardar:
            uc = u[o:o + H * f, o:o + W * f].reshape(
                H, f, W, f).mean(axis=(1, 3))
            comp = uc * ganancia
            if k % 5 == 0 or k < 5:
                escala_vis = max(escala_vis,
                                 float(np.quantile(np.abs(comp), 0.995)))
            v = np.abs(comp) / escala_vis
            np.clip(v, 0.0, 1.0, out=v)
            img = colorear(np.sign(comp) * (v ** gamma), LUTS["vorticidad"],
                           vmin=-1.0, vmax=1.0)
            if pared_on:
                fade = min(1.0, (k - frame_pared + 1) / 12.0)
                img[pared_coarse] = (fondo + (gris - fondo)
                                     * fade).astype(np.uint8)
                img[canto] = (fondo + (gris_canto - fondo)
                              * fade).astype(np.uint8)
            if k >= k_medir:
                # la linea solo se enciende cuando de verdad se esta
                # midiendo: el cian no miente
                fade = min(1.0, (k - k_medir + 1) / 10.0)
                fila = img[g["y_linea"], :].astype(np.float32)
                img[g["y_linea"], raya] = (
                    fila[raya] + (cian - fila[raya])
                    * 0.55 * fade).astype(np.uint8)
            frames[k] = img

    # --- cifras -------------------------------------------------------
    lam_med_px = _lambda_por_fft(corte_lambda) / f

    n = max(n_acum, 1)
    perfil = (acc_c / n) ** 2 + (acc_s / n) ** 2
    perfil_s = _suavizar(perfil, sigma=max(2.0, g["lam_px"] * f / 4.0))
    perfil_vis = perfil_s[o:o + W * f]
    sep_ref = g["lam_px"] * g["L_px"] / g["sep_px"]
    borde = int(4 * f)
    idx = _picos(perfil_vis, borde, W * f - borde,
                 dmin=max(2, int(0.55 * sep_ref * f)))
    picos_px = idx / f
    sep_med = (float(np.mean(np.diff(picos_px))) if len(picos_px) >= 2
               else float("nan"))

    L, d = g["L_px"], g["sep_px"]
    sep_teo = lam_med_px * L / d
    lim = (picos_px.max() - g["x_centro"]) + 2.0 if len(picos_px) else 0.0
    fres = _franjas_fresnel(lam_med_px, d, L, g["x_centro"], lim)
    sep_fres = (float(np.mean(np.diff(fres))) if len(fres) >= 2
                else float(sep_teo))

    # los nombres son los que lee studio/tools/sonda_emergencia.py
    cifras = {
        "franjas_medido_px": round(sep_med, 2),
        "franjas_teorico_px": round(float(sep_teo), 2),
        "franjas_fresnel_px": round(sep_fres, 2),
        "longitud_onda_medida_px": round(float(lam_med_px), 2),
        "franjas_detectadas": int(len(picos_px)),
    }
    extra = {
        "rendijas_px": np.array([[g["x_rendija_1"], g["y_pared"]],
                                 [g["x_rendija_2"], g["y_pared"]]],
                                dtype=np.float64),
        "fuente_px": np.array([g["x_centro"], g["y_fuente"]],
                              dtype=np.float64),
        "linea_medicion_y_px": g["y_linea"],
        "pared_y_px": g["y_pared"],
        "pared_grosor_px": g["grosor_px"],
        "separacion_rendijas_px": d,
        "ancho_rendija_px": g["ancho_px"],
        "L_px": L,
        "marco_px": g["marco_px"],
        "frame_pared": frame_pared,
        "frame_medicion": k_medir,
        "frame_frente_pared": int((g["y_fuente"] - g["y_pared"]) / vel_px),
        "picos_px": picos_px,
        "franjas_fresnel_px": fres,
        "perfil_intensidad": perfil_vis / max(perfil_vis.max(), 1e-30),
        "velocidad_frente_px_frame": vel_px,
        "frames_por_periodo": g["lam_px"] / vel_px,
    }
    return frames, cifras, extra


def simular(semilla=1, pasos=750, res=RES_BASE, lam_px=14.0, sep_px=96.0,
            ancho_px=7.0, marco_px=30.0, grosor_px=4.0, escala=2,
            subpasos=3, cfl=0.6, amplitud=1.0, gamma=0.55):
    """El tanque de ondas: fuente puntual, pared con dos rendijas, franjas.

    Parametros (las longitudes, en pixeles del LIENZO, no de la malla):
      pasos      numero de frames T (750: 12.5 s a 60 fps; la Pelicula los
                 estira a los 30-45 s de la pieza).
      res        (W, H), 9:16 exacto: (270, 480) o (360, 640).
      lam_px     longitud de onda nominal de la fuente (14 px).
      sep_px     separacion entre rendijas, d (96 px).
      ancho_px   ancho de cada rendija (7 px = lambda/2).
      marco_px   margen absorbente FUERA del encuadre (30 px por lado).
      grosor_px  grosor de la pared (4 px).
      escala     finura de la malla: 2 = medio pixel por celda.
      subpasos   pasos de integracion por frame (3).
      cfl        c*dt/dx; el limite 2D es 1/sqrt(2) = 0.707, aqui 0.6.
      gamma      compresion de contraste al pintar (solo visual).
      semilla    sin efecto: aqui no hay azar. Esta por contrato de
                 interfaz con el resto de simuladores.

    Devuelve dict(frames uint8 (T,H,W,3), cifras, extra).

    `extra` trae, en pixeles del lienzo: `rendijas_px` (2,2), `fuente_px`,
    `linea_medicion_y_px`, `pared_y_px`, `pared_grosor_px`,
    `separacion_rendijas_px`, `ancho_rendija_px`, `L_px`, `frame_pared`
    (frame en que aparece la pared), `frame_medicion` (frame en que
    empieza el promedio), `picos_px` (x de las franjas medidas),
    `franjas_fresnel_px` (x de las franjas por geometria exacta),
    `perfil_intensidad` (W*escala,) normalizado 0-1 para dibujar la curva
    encima, `velocidad_frente_px_frame` y `frames_por_periodo`.
    """
    frames, cifras, extra = _correr(
        pasos, res, lam_px, sep_px, ancho_px, marco_px, grosor_px, escala,
        subpasos, cfl, amplitud, gamma, guardar=True)
    return {"frames": validar_pila(frames), "cifras": cifras, "extra": extra}


def medir(semilla=1, pasos=750, res=RES_BASE, lam_px=14.0, sep_px=96.0,
          ancho_px=7.0, marco_px=30.0, grosor_px=4.0, escala=2,
          subpasos=3, cfl=0.6, amplitud=1.0, gamma=0.55):
    """Solo las cifras (misma fisica, sin pintar ni guardar frames)."""
    _, cifras, _ = _correr(
        pasos, res, lam_px, sep_px, ancho_px, marco_px, grosor_px, escala,
        subpasos, cfl, amplitud, gamma, guardar=False)
    return cifras

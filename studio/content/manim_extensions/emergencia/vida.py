# =====================================================================
# emergencia/vida.py — clip 04 "el cañon".
#
# Que simula: el Juego de la Vida de Conway sobre una rejilla de 90x160
# celdas visibles (celda = 3x3 px -> 270x480 px, pixel duro) con el CAÑON
# DE GOSPER arriba a la izquierda. El cañon dispara un planeador cada 30
# generaciones hacia el sur-este; el borde izquierdo/derecho es periodico
# (cilindro) y el de arriba/abajo es muerto, asi que la lluvia de
# planeadores cruza la pantalla en diagonal, envuelve por los lados y baja
# hasta salir por abajo. La rejilla simulada tiene 48 filas de mas por
# debajo de la vista: ningun planeador llega al borde muerto durante la
# simulacion, asi que no hay escombros ni explosiones parasitas.
#
# Reglas (las que el clip pone como HUD):
#   B3/S23 — nace con 3 vecinos vivos, sigue viva con 2 o 3.
#   Vecindad de Moore (8), conteo vectorizado con np.roll.
#   El cañon de Gosper es periodico: se repite cada 30 pasos y escupe un
#   planeador (5 celdas) que viaja 1 celda en diagonal cada 4 pasos.
#
# Colores por rol: verde `C_VIVO` lo vivo; el tono claro del extremo de la
# LUT "vivo" para lo que ACABA de nacer; violeta `C_ORDEN` para el rastro
# de lo que acaba de morir (se apaga en ~4 pasos, es lo que hace legible el
# movimiento). Fondo `C_FONDO`.
#
# Ritmo: 1 paso de Life por frame (no 1 cada 2). Con 1 cada 2 solo caben 11
# planeadores en T=700 y el chorro se ve ralo; con 1 por frame caben 22 y
# la diagonal se lee entera. A la velocidad de reproduccion por defecto
# (`pasos_por_s`=15) el cañon dispara cada 2 s = 30 planeadores por minuto.
#
# Coste medido en el contenedor (2026-08-28): simular() con T=700 tarda
# 1.6 s y medir() 0.3 s; la pila pesa 272 MB (700, 480, 270, 3).
#
# Cifras (medidas sobre lo simulado, no sobre la teoria):
#   periodo_canon_pasos      pasos entre planeadores nuevos (mediana) = 30
#   planeadores_emitidos     planeadores que cruzaron la linea de conteo
#   planeadores_por_minuto   60 * pasos_por_s / periodo
#   poblacion_final          celdas vivas en el ultimo frame
#
# Valores por defecto: periodo 30 pasos EXACTO (los 21 intervalos entre
# los 22 disparos valen 30, dispersion 0), 22 planeadores emitidos,
# 30.0 planeadores por minuto y 157 celdas vivas al final.
# =====================================================================
import numpy as np

from . import C_FONDO, C_ORDEN, C_VIVO, LUTS, hex_a_rgb, validar_pila

# El cañon de Gosper (Bill Gosper, 1970), 36x9, periodo 30. Dispara hacia
# el sur-este desde su esquina inferior derecha.
CANON_GOSPER = """\
........................O...........
......................O.O...........
............OO......OO............OO
...........O...O....OO............OO
OO........O.....O...OO..............
OO........O...O.OO....O.O...........
..........O.....O.......O...........
...........O...O....................
............OO......................"""

CELDAS_PLANEADOR = 5          # un planeador son 5 celdas en cualquier fase
PERIODO_TEORICO = 30          # el del cañon de Gosper, para comparar


def _patron(texto):
    filas = texto.splitlines()
    ancho = max(len(f) for f in filas)
    g = np.zeros((len(filas), ancho), dtype=np.uint8)
    for y, fila in enumerate(filas):
        for x, c in enumerate(fila):
            if c == "O":
                g[y, x] = 1
    return g


def _vecinos(g):
    """Cuenta de vecinos de Moore. x periodico (cilindro), y muerto."""
    izq = np.roll(g, 1, 1)
    der = np.roll(g, -1, 1)
    n = izq + der
    for base in (g, izq, der):
        arr = np.roll(base, 1, 0)
        arr[0] = 0                      # nada entra por arriba
        n += arr
        arr = np.roll(base, -1, 0)
        arr[-1] = 0                     # nada entra por abajo
        n += arr
    return n


def _paso(g):
    n = _vecinos(g)
    return (((n == 3) | ((g == 1) & (n == 2)))).astype(np.uint8)


def _dx_ciclico(x, x0, ancho):
    """Diferencia x - x0 llevada a (-ancho/2, ancho/2]: el cilindro."""
    return (x - x0 + ancho // 2) % ancho - ancho // 2


def _correr(pasos, res, celda, fila_canon, col_canon, filas_extra,
            decaimiento_rastro, brillo_rastro, con_frames):
    W, H = int(res[0]), int(res[1])
    if H * 9 != W * 16:
        raise ValueError(f"res {res} no es 9:16 (H*9 tiene que ser W*16)")
    if W % celda or H % celda:
        raise ValueError(f"res {res} no es multiplo de celda={celda}")
    cols = W // celda
    filas_vista = H // celda

    canon = _patron(CANON_GOSPER)
    # Un planeador baja 1 fila cada 4 pasos: con estas filas de sobra
    # ninguno alcanza el borde muerto de abajo en `pasos` pasos. Si
    # alguno saliera, la cuenta de emitidos (poblacion del chorro / 5)
    # dejaria de ser acumulada y mediria solo los presentes.
    filas_min = fila_canon + canon.shape[0] + 4 + (pasos + 3) // 4 + 4
    filas = max(filas_vista + int(filas_extra), filas_min)
    if canon.shape[1] + col_canon > cols or canon.shape[0] + fila_canon > filas:
        raise ValueError("el cañon no cabe en la rejilla")

    g = np.zeros((filas, cols), dtype=np.uint8)
    g[fila_canon:fila_canon + canon.shape[0],
      col_canon:col_canon + canon.shape[1]] = canon

    # Linea de conteo: por debajo del cañon (9 filas) con margen. Todo lo
    # vivo por debajo de ella es chorro de planeadores enteros.
    fila_corte = fila_canon + canon.shape[0] + 5

    rastro = np.zeros((filas, cols), dtype=np.float32)
    c_fondo = hex_a_rgb(C_FONDO)
    c_vivo = hex_a_rgb(C_VIVO)
    c_nuevo = LUTS["vivo"][-1]                 # el extremo claro de la LUT
    c_rastro = hex_a_rgb(C_ORDEN) * float(brillo_rastro)

    frames = (np.empty((pasos, H, W, 3), dtype=np.uint8)
              if con_frames else None)
    pila_viva = []          # (paso, mascara) solo del ultimo frame util
    emitidos = np.empty(pasos, dtype=np.int64)
    poblacion = np.empty(pasos, dtype=np.int64)
    estados = []            # coordenadas del chorro, para seguir un planeador

    nacida = np.zeros_like(g, dtype=bool)
    for k in range(pasos):
        viva = g.astype(bool)
        if k:
            rastro *= decaimiento_rastro
            rastro[muerta] = 1.0
        if con_frames:
            v = viva[:filas_vista]
            nb = nacida[:filas_vista]
            rs = rastro[:filas_vista, :, None]
            lienzo = c_fondo + rs * (c_rastro - c_fondo)
            lienzo = np.where(v[:, :, None],
                              np.where(nb[:, :, None], c_nuevo, c_vivo),
                              lienzo)
            celdas = np.clip(lienzo, 0, 255).astype(np.uint8)
            frames[k] = np.repeat(np.repeat(celdas, celda, 0), celda, 1)
        poblacion[k] = int(viva.sum())
        chorro = viva[fila_corte:]
        emitidos[k] = int(chorro.sum()) // CELDAS_PLANEADOR
        ys, xs = np.nonzero(chorro)
        estados.append((ys + fila_corte, xs))
        if k == pasos - 1:
            pila_viva = viva
            break
        anterior = viva
        g = _paso(g)
        viva = g.astype(bool)
        nacida = viva & ~anterior
        muerta = anterior & ~viva

    # --- cifras medidas ---------------------------------------------------
    if int(pila_viva[-4:].sum()):
        raise RuntimeError("un planeador llego al borde muerto de abajo: "
                           "la cuenta de emitidos ya no seria acumulada")
    nacimientos = np.nonzero(np.diff(emitidos) > 0)[0] + 1
    if len(nacimientos) >= 2:
        difs = np.diff(nacimientos)
        periodo = float(np.median(difs))
        periodo_disp = int(difs.max() - difs.min())
    else:
        periodo, periodo_disp = float("nan"), -1

    return dict(
        frames=frames, emitidos=emitidos, poblacion=poblacion,
        nacimientos=nacimientos, periodo=periodo, periodo_disp=periodo_disp,
        estados=estados, cols=cols, filas=filas, filas_vista=filas_vista,
        fila_corte=fila_corte, viva_final=pila_viva,
        centro_canon=((col_canon + canon.shape[1] / 2) * celda,
                      (fila_canon + canon.shape[0] / 2) * celda),
    )


def _seguir_planeador(datos, k0, celda, cols):
    """Trayectoria (T,2) en pixeles del planeador nacido en el frame `k0`.

    Se localiza como el grupo de celdas de menor fila por debajo de la
    linea de conteo (el mas nuevo del chorro) y se sigue hacia adelante por
    cercania (los planeadores van a >10 celdas unos de otros y nunca chocan,
    asi que un radio de 3 celdas basta). Antes de `k0` la posicion se
    congela en la de nacimiento para que la pila sea (T,2) entera.
    """
    estados = datos["estados"]
    T = len(estados)
    pos = np.zeros((T, 2), dtype=np.float64)
    ys, xs = estados[k0]
    if len(ys) == 0:
        return pos, False
    i = int(np.argmin(ys))
    y0, x0 = float(ys[i]), float(xs[i])
    cerca = (np.abs(ys - y0) <= 3) & (np.abs(_dx_ciclico(xs, x0, cols)) <= 3)
    cy = float(ys[cerca].mean())
    cx = (x0 + _dx_ciclico(xs[cerca], x0, cols).mean()) % cols
    for k in range(k0, T):
        ys, xs = estados[k]
        if len(ys):
            dx = _dx_ciclico(xs, cx, cols)
            cerca = (np.abs(ys - cy) <= 3.5) & (np.abs(dx) <= 3.5)
            if cerca.any():
                cy = float(ys[cerca].mean())
                cx = float((cx + dx[cerca].mean()) % cols)
        pos[k] = ((cx + 0.5) * celda, (cy + 0.5) * celda)
    pos[:k0] = pos[k0]
    return pos, True


def _cifras(datos, pasos_por_s):
    periodo = datos["periodo"]
    return {
        "periodo_canon_pasos": periodo,
        "periodo_canon_teorico": float(PERIODO_TEORICO),
        "planeadores_emitidos": int(datos["emitidos"][-1]),
        "planeadores_por_minuto": (60.0 * float(pasos_por_s) / periodo
                                   if periodo == periodo else float("nan")),
        "poblacion_final": int(datos["poblacion"][-1]),
    }


def simular(semilla=1, pasos=700, res=(270, 480), celda=3, pasos_por_s=15.0,
            fila_canon=6, col_canon=8, filas_extra=48,
            decaimiento_rastro=0.66, brillo_rastro=0.45):
    """Life + cañon de Gosper. T = `pasos` frames, 1 paso de Life por frame.

    `semilla` no interviene (el cañon es deterministico); se acepta por la
    interfaz comun del paquete. `pasos_por_s` es la velocidad de
    REPRODUCCION supuesta y solo entra en la cifra de planeadores/minuto.

    Devuelve dict(frames, cifras, extra).

    extra:
      pos_ultimo_planeador   (T,2) px del ULTIMO planeador emitido; antes de
                             nacer, congelada en su punto de nacimiento
      frame_nacimiento_ultimo  frame en que ese planeador cruzo la linea
      pos_planeador_seguido  (T,2) px del planeador nacido mas cerca del 20 %
                             de la pelicula: el util para que la camara lo
                             siga durante casi todo el clip
      frame_nacimiento_seguido  su frame de nacimiento
      nacimientos            (n,) frames de nacimiento de todos
      planeadores_por_frame  (T,) cuenta acumulada
      poblacion_por_frame    (T,) celdas vivas
      centro_canon           (x,y) px del centro del cañon
      rejilla                (cols, filas_simuladas, filas_visibles, celda);
                             filas_simuladas crece sola con `pasos` para que
                             ningun planeador toque el borde muerto
      dispersion_periodo     max-min de los intervalos entre disparos (0 = reloj)
    """
    datos = _correr(int(pasos), res, int(celda), int(fila_canon),
                    int(col_canon), int(filas_extra), float(decaimiento_rastro),
                    float(brillo_rastro), True)
    T = int(pasos)
    nac = datos["nacimientos"]
    cols, cel = datos["cols"], int(celda)
    if len(nac):
        k_ult = int(nac[-1])
        k_seg = int(nac[int(np.argmin(np.abs(nac - 0.20 * T)))])
    else:
        k_ult = k_seg = 0
    pos_ult, _ = _seguir_planeador(datos, k_ult, cel, cols)
    pos_seg, _ = _seguir_planeador(datos, k_seg, cel, cols)
    frames = validar_pila(datos["frames"])
    return dict(
        frames=frames,
        cifras=_cifras(datos, pasos_por_s),
        extra={
            "pos_ultimo_planeador": pos_ult,
            "frame_nacimiento_ultimo": k_ult,
            "pos_planeador_seguido": pos_seg,
            "frame_nacimiento_seguido": k_seg,
            "nacimientos": nac,
            "planeadores_por_frame": datos["emitidos"],
            "poblacion_por_frame": datos["poblacion"],
            "centro_canon": datos["centro_canon"],
            "rejilla": (cols, datos["filas"], datos["filas_vista"], cel),
            "dispersion_periodo": datos["periodo_disp"],
        },
    )


def medir(semilla=1, pasos=700, res=(270, 480), celda=3, pasos_por_s=15.0,
          fila_canon=6, col_canon=8, filas_extra=48,
          decaimiento_rastro=0.66, brillo_rastro=0.45):
    """Solo las cifras (sin pintar frames), para la sonda."""
    datos = _correr(int(pasos), res, int(celda), int(fila_canon),
                    int(col_canon), int(filas_extra), float(decaimiento_rastro),
                    float(brillo_rastro), False)
    return _cifras(datos, pasos_por_s)

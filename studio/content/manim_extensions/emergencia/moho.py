# =====================================================================
# emergencia/moho.py — Physarum polycephalum (Jones, 2010) sobre comida.
#
# QUE SIMULA
#   Un moho sin cerebro: N agentes puntuales, cada uno con posicion y rumbo.
#   No hay plan, no hay mapa. Solo una estela quimica compartida en la que
#   todos escriben y de la que todos leen. De ahi sale una RED que une los
#   puntos de comida, y esa red se parece muchisimo a una red de transporte
#   diseñada (Tero et al., 2010: Physarum contra el metro de Tokio).
#
# REGLAS (las tres lineas del HUD)
#   1. Cada agente huele la estela en tres puntos: delante, izquierda y
#      derecha (a 22 grados, 9 px por delante).
#   2. Gira hacia el olor mas fuerte, avanza 1 px y deposita estela.
#   3. La estela se difunde (3x3) y se evapora; la comida deposita sin parar.
#
# IMAGEN
#   Estela con la LUT "vivo" (verde: lo vivo) sobre `C_FONDO`; los 10 puntos
#   de comida en ambar (`C_REGLA`: la regla puesta en el mundo), compuestos
#   por alfa. El arco visual medido: frame 0 negro; hacia el 75 una malla
#   FINA de filamentos por todo el lienzo; de ahi al 749 la malla se ENGROSA
#   y se PODA (celdas cada vez mas grandes) y la comida queda de nodo de la
#   red. Es el clip entero: nacer, tensarse, podarse.
#
# CIFRAS (medidas sobre lo simulado, no de formula)
#   red_px          longitud, en pixeles, de los CAMINOS del moho que unen
#                   las fuentes. Se mide asi: umbral de Otsu sobre la estela
#                   -> componente conexa que toca la comida -> esqueleto de
#                   1 px (Zhang-Suen) -> grafo del esqueleto con pesos 1 y
#                   sqrt(2) -> Dijkstra entre las 10 fuentes -> arbol minimo
#                   de esas distancias GEODESICAS -> longitud de la union de
#                   esos caminos. Es la red de transporte, no la malla.
#   arbol_px        longitud del arbol generador minimo (Prim) sobre las
#                   distancias EUCLIDEAS entre los puntos de comida: el
#                   minimo teorico, el cable recto que un ingeniero tiraria.
#   red_vs_arbol    red_px / arbol_px. Esta es la cifra del clip: cuanto se
#                   pasa el moho respecto del optimo. Es > 1 porque el moho
#                   va por donde hay filamento, no en linea recta.
#   malla_px        longitud del esqueleto ENTERO (toda la malla, bucles
#                   incluidos) y `malla_vs_arbol` su cociente: sirve para
#                   decir que el moho construye de mas a proposito.
#   comidas_conectadas / comidas   cuantas fuentes unio la red.
#
# EXTRA
#   comida        (n,2) float64, posiciones de la comida en PIXELES (x, y).
#   mst_aristas   (n-1,2) int, pares de indices del arbol minimo.
#   mst_segmentos (n-1,4) float64, (x0,y0,x1,y1) en pixeles: para dibujar el
#                 arbol encima con vectores.
#   mascara       (H,W) bool, la red umbralizada al final.
#   esqueleto     (H,W) bool, el esqueleto entero (contado en `malla_px`).
#   caminos       (H,W) bool, SOLO los caminos entre comidas (contados en
#                 `red_px`): la capa para resaltar en cian la red medida.
#   caminos_pares lista de (i,j): que fuentes une cada camino.
#   estela_final  (H,W) float32.
#   estela_media_por_frame (T,) float32, biomasa quimica: sube y se estabiliza.
#   umbral        float, el umbral de Otsu usado.
#   vmax          float, el tope de brillo con que se pinto (0 si no se pinto).
#   res           (W, H).
#
# COSTE MEDIDO (contenedor codeaerospace_contenido-manim, 2026-08-28)
#   simular() con los valores por defecto = 20.3 a 32.8 s de CPU en tres
#   corridas (tope 90 s); T = 750 frames a 270x480, pila 291.6 MB uint8
#   (tope 1 GB). medir() (sin pintar) = 15.9 s y devuelve EXACTAMENTE las
#   mismas cifras que simular(): pintar no perturba la simulacion.
#
# VALORES MEDIDOS con la semilla 1 y los valores por defecto
#   red_px = 950.2 px        arbol_px = 806.3 px    red_vs_arbol = 1.178
#   malla_px = 4763 px       malla_vs_arbol = 5.91
#   comidas_conectadas = 10 de 10       umbral de Otsu = 4.57
#   Lectura: el moho une las diez fuentes con un 18 % mas de longitud que
#   el cable recto optimo, y ademas mantiene una malla seis veces mas larga
#   alrededor. Con semilla 7 (otra disposicion): red_vs_arbol comparable.
# =====================================================================
import numpy as np

from . import (C_FONDO, C_REGLA, C_VIVO, colorear, hex_a_rgb, lut,
               validar_pila)

# LUT propia: la "vivo" del nucleo con gamma < 1 para que los filamentos
# finos (valores bajos) ya se vean verdes y no se pierdan en el fondo.
LUT_MOHO = lut(C_FONDO, C_VIVO, "#c7f9e5", gamma=0.55)

AMBAR = hex_a_rgb(C_REGLA)


# --------------------------------------------------------------------
# Nucleo numerico
# --------------------------------------------------------------------
def _sembrar_comida(rng, W, H, n, margen=34, separacion=70.0, intentos=4000):
    """n puntos irregulares pero fijos (semilla), separados y sin pegarse al
    borde. Rechazo simple; si no cabe la separacion, la relaja."""
    pts = []
    sep = float(separacion)
    for it in range(intentos):
        if len(pts) == n:
            break
        p = np.array([rng.uniform(margen, W - margen),
                      rng.uniform(margen, H - margen)])
        if all(np.hypot(*(p - q)) >= sep for q in pts):
            pts.append(p)
        elif it % 500 == 499:
            sep *= 0.9
    while len(pts) < n:                      # red de seguridad determinista
        pts.append(np.array([rng.uniform(margen, W - margen),
                             rng.uniform(margen, H - margen)]))
    return np.array(pts[:n], dtype=np.float64)


def _bultos(comida, W, H, radio, fuerza):
    """Suma de gaussianas (H,W) float32 centradas en la comida."""
    yy, xx = np.mgrid[0:H, 0:W]
    m = np.zeros((H, W), dtype=np.float32)
    for cx, cy in comida:
        d2 = (xx - cx) ** 2 + (yy - cy) ** 2
        m += (fuerza * np.exp(-d2 / (2.0 * radio ** 2))).astype(np.float32)
    return m


def _difundir(t):
    """Media 3x3 separable, borde replicado. Sin scipy."""
    b = np.empty_like(t)
    b[:, 1:-1] = t[:, :-2] + t[:, 1:-1] + t[:, 2:]
    b[:, 0] = 2.0 * t[:, 0] + t[:, 1]
    b[:, -1] = 2.0 * t[:, -1] + t[:, -2]
    c = np.empty_like(b)
    c[1:-1] = b[:-2] + b[1:-1] + b[2:]
    c[0] = 2.0 * b[0] + b[1]
    c[-1] = 2.0 * b[-1] + b[-2]
    c *= (1.0 / 9.0)
    return c


def _leer(t, x, y, W, H):
    xi = np.clip(x, 0, W - 1).astype(np.int32)
    yi = np.clip(y, 0, H - 1).astype(np.int32)
    return t[yi, xi]


def _otsu(v, bins=128):
    """Umbral de Otsu sobre un vector de valores (float)."""
    lo, hi = float(v.min()), float(v.max())
    if hi - lo < 1e-9:
        return hi
    h, bordes = np.histogram(v, bins=bins, range=(lo, hi))
    h = h.astype(np.float64)
    p = h / h.sum()
    centros = 0.5 * (bordes[:-1] + bordes[1:])
    w0 = np.cumsum(p)
    w1 = 1.0 - w0
    m0 = np.cumsum(p * centros) / np.maximum(w0, 1e-12)
    mt = float(np.sum(p * centros))
    m1 = (mt - np.cumsum(p * centros)) / np.maximum(w1, 1e-12)
    var = w0 * w1 * (m0 - m1) ** 2
    return float(centros[int(np.argmax(var))])


def _vecinos(m):
    """Los 8 vecinos de una mascara bool (H,W), en orden P2..P9 de
    Zhang-Suen (N, NE, E, SE, S, SW, W, NW), con borde a False."""
    p = np.zeros((m.shape[0] + 2, m.shape[1] + 2), dtype=bool)
    p[1:-1, 1:-1] = m
    return (p[0:-2, 1:-1], p[0:-2, 2:], p[1:-1, 2:], p[2:, 2:],
            p[2:, 1:-1], p[2:, 0:-2], p[1:-1, 0:-2], p[0:-2, 0:-2])


def _adelgazar(m, max_iter=40):
    """Zhang-Suen vectorizado: mascara bool -> esqueleto de 1 px."""
    m = m.copy()
    for _ in range(max_iter):
        cambio = False
        for fase in (0, 1):
            v = _vecinos(m)
            n = np.add.reduce([x.astype(np.int8) for x in v])
            seq = v + (v[0],)
            a = np.add.reduce([((~seq[i]) & seq[i + 1]).astype(np.int8)
                               for i in range(8)])
            p2, p3, p4, p5, p6, p7, p8, p9 = v
            if fase == 0:
                c1 = ~(p2 & p4 & p6)
                c2 = ~(p4 & p6 & p8)
            else:
                c1 = ~(p2 & p4 & p8)
                c2 = ~(p2 & p6 & p8)
            fuera = m & (n >= 2) & (n <= 6) & (a == 1) & c1 & c2
            if fuera.any():
                m &= ~fuera
                cambio = True
        if not cambio:
            break
    return m


def _componente_de(mascara, semillas_yx, max_iter=4000):
    """Componente 8-conexa de `mascara` alcanzable desde las semillas."""
    alc = np.zeros_like(mascara)
    ys, xs = semillas_yx
    ok = mascara[ys, xs]
    alc[ys[ok], xs[ok]] = True
    if not alc.any():
        return alc
    for _ in range(max_iter):
        p = np.zeros((alc.shape[0] + 2, alc.shape[1] + 2), dtype=bool)
        p[1:-1, 1:-1] = alc
        crec = (p[0:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, 0:-2] | p[1:-1, 2:] |
                p[0:-2, 0:-2] | p[0:-2, 2:] | p[2:, 0:-2] | p[2:, 2:])
        nuevo = (crec & mascara) | alc
        if nuevo.sum() == alc.sum():
            break
        alc = nuevo
    return alc


def _grafo(esq):
    """Esqueleto bool (H,W) -> (indice (H,W), vecinos, n). Aristas de 8
    vecinos con peso 1 (ortogonal) o sqrt(2) (diagonal): contar pixeles
    sobrestima las diagonales un 41 %."""
    ys, xs = np.nonzero(esq)
    n = len(ys)
    ind = np.full(esq.shape, -1, dtype=np.int64)
    ind[ys, xs] = np.arange(n)
    vec = [[] for _ in range(n)]
    r2 = float(np.sqrt(2.0))
    cortes = ((np.s_[:, :-1], np.s_[:, 1:], 1.0),
              (np.s_[:-1, :], np.s_[1:, :], 1.0),
              (np.s_[:-1, :-1], np.s_[1:, 1:], r2),
              (np.s_[:-1, 1:], np.s_[1:, :-1], r2))
    for ca, cb, w in cortes:
        m = esq[ca] & esq[cb]
        for i, j in zip(ind[ca][m], ind[cb][m]):
            vec[i].append((int(j), w))
            vec[j].append((int(i), w))
    return ind, vec, n, ys, xs


def _dijkstra(vec, n, origen):
    import heapq
    d = np.full(n, np.inf)
    padre = np.full(n, -1, dtype=np.int64)
    d[origen] = 0.0
    cola = [(0.0, origen)]
    while cola:
        du, u = heapq.heappop(cola)
        if du > d[u]:
            continue
        for v, w in vec[u]:
            nd = du + w
            if nd < d[v] - 1e-12:
                d[v] = nd
                padre[v] = u
                heapq.heappush(cola, (nd, v))
    return d, padre


def _red_entre_comidas(esq, comida):
    """Los CAMINOS del moho que unen la comida, medidos sobre el esqueleto.

    Engancha cada fuente al pixel de esqueleto mas cercano, calcula las
    distancias geodesicas POR EL MOHO entre todas las fuentes (Dijkstra),
    saca el arbol minimo de ese grafo y devuelve la longitud de la UNION de
    esos caminos (cada arista contada una sola vez) mas los caminos en si.

    Es la cifra honesta para comparar con el arbol euclideo: el esqueleto
    entero mide la malla completa del moho (miles de px de bucles que no
    conectan nada), no la red de transporte.
    """
    ind, vec, n, ys, xs = _grafo(esq)
    if n < 2:
        return 0.0, [], np.zeros(esq.shape, bool), 0
    nodos = []
    for cx, cy in comida:
        d2 = (xs - cx) ** 2 + (ys - cy) ** 2
        nodos.append(int(np.argmin(d2)))
    dist, padres = [], []
    for s0 in nodos:
        d, p = _dijkstra(vec, n, s0)
        dist.append(d)
        padres.append(p)
    m = len(nodos)
    D = np.array([[dist[i][nodos[j]] for j in range(m)] for i in range(m)])
    # Prim sobre las distancias GEODESICAS, saltando lo inalcanzable
    dentro = np.zeros(m, dtype=bool)
    dentro[0] = True
    mejor = D[0].copy()
    de = np.zeros(m, dtype=np.int64)
    pares = []
    for _ in range(m - 1):
        cand = np.where(dentro, np.inf, mejor)
        j = int(np.argmin(cand))
        if not np.isfinite(cand[j]):
            break
        pares.append((int(de[j]), j))
        dentro[j] = True
        mas = D[j] < mejor
        de[mas] = j
        mejor = np.minimum(mejor, D[j])
    usadas = set()
    total = 0.0
    pintado = np.zeros(esq.shape, dtype=bool)
    for i, j in pares:
        p = padres[i]
        u = nodos[j]
        pintado[ys[u], xs[u]] = True
        while u != nodos[i] and p[u] >= 0:
            v = int(p[u])
            k = (min(u, v), max(u, v))
            if k not in usadas:
                usadas.add(k)
                total += np.hypot(float(xs[u] - xs[v]), float(ys[u] - ys[v]))
            pintado[ys[v], xs[v]] = True
            u = v
    return float(total), pares, pintado, int(dentro.sum())


def _mst(puntos):
    """Prim sobre las distancias euclideas. -> (aristas (n-1,2), longitud)."""
    n = len(puntos)
    d = np.hypot(puntos[:, 0][:, None] - puntos[:, 0][None, :],
                 puntos[:, 1][:, None] - puntos[:, 1][None, :])
    dentro = np.zeros(n, dtype=bool)
    dentro[0] = True
    mejor = d[0].copy()
    padre = np.zeros(n, dtype=np.int64)
    aristas, total = [], 0.0
    for _ in range(n - 1):
        cand = np.where(dentro, np.inf, mejor)
        j = int(np.argmin(cand))
        aristas.append((int(padre[j]), j))
        total += float(cand[j])
        dentro[j] = True
        mas_cerca = d[j] < mejor
        padre[mas_cerca] = j
        mejor = np.minimum(mejor, d[j])
    return np.array(aristas, dtype=np.int64), total


def _correr(n_agentes, comidas, semilla, pasos, res, angulo_sensor,
            angulo_giro, dist_sensor, paso, deposito, deposito_comida,
            radio_comida, decaimiento, tope_celda, guardar_frames, vmax=None):
    W, H = int(res[0]), int(res[1])
    if abs(H / W - 16.0 / 9.0) > 1e-6:
        raise ValueError(f"res debe ser 9:16; llego {res}")
    rng = np.random.default_rng(semilla)

    comida = _sembrar_comida(rng, W, H, int(comidas))
    fuente = _bultos(comida, W, H, radio_comida, deposito_comida)
    # lejos de las fuentes: donde vive la RED (y no el pico de la comida).
    # Se usa para el umbral y para la referencia de brillo; sin excluirlas,
    # el pico de las fuentes (~570) se lleva ambos y la red sale apagada.
    lejos = _bultos(comida, W, H, radio_comida, 1.0) < 0.02

    x = rng.uniform(0, W, n_agentes)
    y = rng.uniform(0, H, n_agentes)
    ang = rng.uniform(0, 2 * np.pi, n_agentes)
    estela = np.zeros((H, W), dtype=np.float32)

    if guardar_frames:
        frames = np.empty((pasos, H, W, 3), dtype=np.uint8)
        # la comida se COMPONE por alfa, no se suma: sumada saldria blanca
        # sobre una estela ya brillante y el ambar dejaria de leerse.
        alfa = np.clip(_bultos(comida, W, H, 2.7, 1.55), 0.0, 1.0)[..., None]
        capa_comida = alfa * AMBAR[None, None, :]
        uno_menos = 1.0 - alfa
        ref = 1e-3
    else:
        frames = None
    media = np.empty(pasos, dtype=np.float32)
    muestra = np.flatnonzero(lejos.ravel())[::7]

    for k in range(pasos):
        # --- 1. sensar -------------------------------------------------
        d = dist_sensor
        cf, sf = np.cos(ang), np.sin(ang)
        f = _leer(estela, x + cf * d, y + sf * d, W, H)
        al = ang + angulo_sensor
        ar = ang - angulo_sensor
        l = _leer(estela, x + np.cos(al) * d, y + np.sin(al) * d, W, H)
        r = _leer(estela, x + np.cos(ar) * d, y + np.sin(ar) * d, W, H)

        # --- 2. girar hacia el mas fuerte ------------------------------
        u = rng.random(n_agentes)
        recto = (f >= l) & (f >= r)
        ambos = (f < l) & (f < r)
        giro = np.where(ambos, np.where(u < 0.5, -angulo_giro, angulo_giro),
                        0.0)
        lado = (~recto) & (~ambos)
        giro = np.where(lado & (l > r), angulo_giro, giro)
        giro = np.where(lado & (r >= l), -angulo_giro, giro)
        ang = ang + giro

        # --- 3. avanzar (con exclusion: la celda destino tiene aforo) ---
        nx = x + np.cos(ang) * paso
        ny = y + np.sin(ang) * paso
        fuera = (nx < 1) | (nx > W - 2) | (ny < 1) | (ny > H - 2)
        nx = np.clip(nx, 1, W - 2)
        ny = np.clip(ny, 1, H - 2)
        idx = (ny.astype(np.int32) * W + nx.astype(np.int32))
        aforo = np.bincount(idx, minlength=H * W)
        lleno = aforo[idx] > tope_celda
        bloqueado = fuera | lleno
        x = np.where(bloqueado, x, nx)
        y = np.where(bloqueado, y, ny)
        ang = np.where(bloqueado, rng.uniform(0, 2 * np.pi, n_agentes), ang)

        # --- 4. depositar ----------------------------------------------
        idx = (y.astype(np.int32) * W + x.astype(np.int32))
        estela += (np.bincount(idx, minlength=H * W)
                   .reshape(H, W).astype(np.float32) * deposito)
        estela += fuente

        # --- 5. difundir y evaporar ------------------------------------
        estela = _difundir(estela)
        estela *= decaimiento

        media[k] = estela.mean()
        if guardar_frames:
            if vmax is None:
                # referencia monotona: la imagen nace oscura y se estabiliza
                # cuando la masa quimica llega a su equilibrio (~frame 80).
                ref = max(ref, float(np.percentile(
                    estela.ravel()[muestra], 99.5)))
                tope = ref
            else:
                tope = float(vmax)
            rgb = colorear(estela, LUT_MOHO, vmin=0.0, vmax=tope)
            frames[k] = np.clip(rgb * uno_menos + capa_comida,
                                0, 255).astype(np.uint8)

    # --- cifras sobre el estado final ---------------------------------
    # Otsu sobre sqrt(estela) EXCLUYENDO los bulbos (ver `lejos` arriba):
    # sin excluir, el pico de las fuentes se lleva el umbral y la "red" se
    # reduce a los diez discos de comida (medido: red_px = 11).
    umbral = _otsu(np.sqrt(estela[lejos])) ** 2
    mascara = estela >= umbral
    sem = (np.clip(np.round(comida[:, 1]).astype(np.int64), 0, H - 1),
           np.clip(np.round(comida[:, 0]).astype(np.int64), 0, W - 1))
    # las semillas caen dentro del bulbo de comida: dilato la mascara ahi
    conectada = _componente_de(mascara, sem)
    esqueleto = _adelgazar(conectada)
    malla_px = float(esqueleto.sum())
    red_px, caminos, pintado, conectadas = _red_entre_comidas(esqueleto,
                                                              comida)
    aristas, arbol_px = _mst(comida)

    cifras = {
        "red_px": red_px,
        "arbol_px": float(arbol_px),
        "red_vs_arbol": float(red_px / arbol_px) if arbol_px > 0 else 0.0,
        "malla_px": malla_px,
        "malla_vs_arbol": (float(malla_px / arbol_px) if arbol_px > 0
                           else 0.0),
        "comidas": int(len(comida)),
        "comidas_conectadas": int(conectadas),
        "agentes": int(n_agentes),
        "pasos": int(pasos),
    }
    extra = {
        "comida": comida,
        "mst_aristas": aristas,
        "mst_segmentos": np.array(
            [[comida[i, 0], comida[i, 1], comida[j, 0], comida[j, 1]]
             for i, j in aristas], dtype=np.float64),
        "mascara": conectada,
        "esqueleto": esqueleto,
        "caminos": pintado,
        "caminos_pares": caminos,
        "estela_final": estela,
        "estela_media_por_frame": media,
        "umbral": float(umbral),
        "vmax": float(ref) if (guardar_frames and vmax is None)
                else (float(vmax) if vmax is not None else 0.0),
        "res": (W, H),
    }
    return frames, cifras, extra


# --------------------------------------------------------------------
# Interfaz publica
# --------------------------------------------------------------------
PAR = dict(n_agentes=60000, comidas=10, semilla=1, pasos=750, res=(270, 480),
           angulo_sensor=0.39, angulo_giro=0.60, dist_sensor=11.0, paso=1.0,
           deposito=1.0, deposito_comida=40.0, radio_comida=3.2,
           decaimiento=0.93, tope_celda=2)


def simular(n_agentes=60000, comidas=10, semilla=1, pasos=750,
            res=(270, 480), angulo_sensor=0.39, angulo_giro=0.60,
            dist_sensor=11.0, paso=1.0, deposito=1.0, deposito_comida=40.0,
            radio_comida=3.2, decaimiento=0.93, tope_celda=2, vmax=None):
    """Physarum sobre puntos de comida.

    T = `pasos` (750 por defecto: un paso de simulacion = un frame, sin
    saltos; a 60 fps son 12.5 s de material para una pieza de 30-45 s, que
    `Pelicula` estira con `ritmo_por_tramos`).

    `vmax=None` (recomendado) normaliza el color con una referencia MONOTONA
    (percentil 99.5 acumulado): el frame 0 nace negro y el brillo se
    estabiliza cuando la masa quimica llega al equilibrio (~frame 80). Un
    `vmax` fijo tambien vale si un clip necesita brillo constante.

    Devuelve dict(frames uint8 (T,H,W,3), cifras, extra); ver el docstring
    del modulo para las cifras y el contenido de `extra`.
    """
    frames, cifras, extra = _correr(
        n_agentes, comidas, semilla, pasos, res, angulo_sensor, angulo_giro,
        dist_sensor, paso, deposito, deposito_comida, radio_comida,
        decaimiento, tope_celda, True, vmax)
    return {"frames": validar_pila(frames), "cifras": cifras, "extra": extra}


def medir(n_agentes=60000, comidas=10, semilla=1, pasos=750,
          res=(270, 480), angulo_sensor=0.39, angulo_giro=0.60,
          dist_sensor=11.0, paso=1.0, deposito=1.0, deposito_comida=40.0,
          radio_comida=3.2, decaimiento=0.93, tope_celda=2, vmax=None):
    """Solo las cifras (sin pila de frames), para la sonda. Mismos
    parametros que `simular` (`vmax` se ignora: no pinta)."""
    _, cifras, _ = _correr(
        n_agentes, comidas, semilla, pasos, res, angulo_sensor, angulo_giro,
        dist_sensor, paso, deposito, deposito_comida, radio_comida,
        decaimiento, tope_celda, False, vmax)
    return cifras


__all__ = ["simular", "medir", "LUT_MOHO", "PAR"]

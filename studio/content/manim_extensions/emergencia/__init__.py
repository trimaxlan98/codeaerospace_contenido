# =====================================================================
# emergencia — nucleo del curso 29 (vertical, experimental).
#
# La idea tecnologica del curso: el fotograma entero es una SIMULACION.
# Un simulador (numpy puro, un modulo por sistema en este paquete) produce
# una pila de frames uint8 (T, H, W, 3); `Pelicula` la presenta en manim
# como un ImageMobject a pantalla completa y la anima intercambiando el
# `pixel_array` dentro de un UpdateFromAlphaFunc, con camara (recorte que
# sigue a un agente o hace zoom) y ritmo (camara lenta en el instante en
# que nace el patron).
#
# Medido en el contenedor (2026-08-28): 0.10 s/frame en ql y 0.29 s/frame
# en qh a 1080x1920. Una pieza de 35 s cuesta ~2 min en ql y ~10 en qh.
#
# Reglas:
#   - los simuladores NO importan manim (la sonda corre sin el);
#   - la pila se guarda en RGB y el alfa se pega al vuelo: manim exige RGBA
#     en `pixel_array` ("buffer is not large enough" si se le da RGB);
#   - tope de memoria de una pila: 1 GB (se comprueba, no se confia).
# =====================================================================
import numpy as np

# --- Paleta por ROL (la misma del style_block; aqui para las LUT) --------
C_FONDO = "#0b0f14"
C_MEDIDO = "#22d3ee"      # cian: medido en este render
C_REGLA = "#f59e0b"       # ambar: la regla / el instrumento / el seguido
C_ORDEN = "#7c3aed"       # violeta: lo ordenado, el dominio, la cuenca
C_ENERGIA = "#ea580c"     # naranja: energia, vorticidad, lo que escapa
C_VIVO = "#34d399"        # verde: lo vivo
C_MOBILIARIO = "#31414f"
C_EXTERNO = "#94a0b0"
C_TINTA = "#e6edf3"

MEMORIA_MAX = 1_000_000_000          # bytes de una pila de frames
RES_BASE = (270, 480)                # (W, H): 9:16 exacto
RES_ZOOM = (360, 640)


def hex_a_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def lut(*colores, n=256, gamma=1.0):
    """Tabla (n,3) float32 0-255 que interpola los colores dados, en orden.

    `lut(C_FONDO, C_VIVO)` es la rampa tipica "nada -> vivo"; con tres o mas
    colores se reparten a partes iguales. `gamma` < 1 aclara los valores
    bajos (util para densidades con mucha cola).
    """
    if len(colores) < 2:
        raise ValueError("una LUT necesita al menos dos colores")
    puntos = np.stack([hex_a_rgb(c) for c in colores])
    x = np.linspace(0.0, 1.0, n) ** gamma
    xs = np.linspace(0.0, 1.0, len(colores))
    return np.stack([np.interp(x, xs, puntos[:, i]) for i in range(3)],
                    axis=1).astype(np.float32)


LUTS = {
    "vivo": lut(C_FONDO, C_VIVO, "#c7f9e5"),
    "orden": lut(C_FONDO, C_ORDEN, "#d8c7ff"),
    "energia": lut(C_FONDO, C_ENERGIA, "#ffd7a8"),
    "medido": lut(C_FONDO, C_MEDIDO, "#e0fbff"),
    "regla": lut(C_FONDO, C_REGLA, "#fff1c2"),
    # divergente: negativo violeta, cero fondo, positivo naranja
    "vorticidad": lut(C_ORDEN, C_FONDO, C_ENERGIA),
    "gris": lut(C_FONDO, C_EXTERNO, C_TINTA),
}


def colorear(campo, tabla, vmin=None, vmax=None):
    """Campo float (..., H, W) -> uint8 (..., H, W, 3) por la LUT."""
    campo = np.asarray(campo, dtype=np.float32)
    lo = float(np.min(campo)) if vmin is None else float(vmin)
    hi = float(np.max(campo)) if vmax is None else float(vmax)
    if hi - lo < 1e-12:
        hi = lo + 1e-12
    idx = np.clip((campo - lo) / (hi - lo), 0.0, 1.0)
    idx = (idx * (len(tabla) - 1)).astype(np.int32)
    return np.clip(tabla[idx], 0, 255).astype(np.uint8)


def mezclar_capas(*capas):
    """Suma aditiva de capas uint8 (H,W,3) con saturacion: luz sobre luz."""
    acc = np.zeros(capas[0].shape, dtype=np.uint16)
    for c in capas:
        acc += c
    return np.clip(acc, 0, 255).astype(np.uint8)


# --- Dibujo de agentes sobre un lienzo de pixeles --------------------------
def _nucleo(radio):
    r = int(radio)
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    k = np.exp(-(x ** 2 + y ** 2) / (2.0 * max(radio, 0.6) ** 2 / 2.2))
    return (k / k.max()).astype(np.float32)


def salpicar(lienzo, xy, color, peso=1.0, radio=1.0):
    """Pinta puntos (n,2) en pixeles sobre `lienzo` float32 (H,W,3), con un
    nucleo gaussiano de `radio`. Aditivo: donde se juntan muchos, brilla."""
    H, W = lienzo.shape[:2]
    rgb = hex_a_rgb(color) / 255.0 * peso
    k = _nucleo(radio)
    r = k.shape[0] // 2
    xi = np.round(xy[:, 0]).astype(np.int64)
    yi = np.round(xy[:, 1]).astype(np.int64)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            w = k[dy + r, dx + r]
            if w < 0.02:
                continue
            xs, ys = xi + dx, yi + dy
            ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
            np.add.at(lienzo, (ys[ok], xs[ok]), rgb * w)
    return lienzo


def a_uint8(lienzo, ganancia=255.0):
    return np.clip(lienzo * ganancia, 0, 255).astype(np.uint8)


def estela(lienzo, decaimiento=0.90):
    """Multiplica en sitio: lo pintado en frames anteriores se apaga."""
    lienzo *= decaimiento
    return lienzo


# --- La pila de frames ----------------------------------------------------
def validar_pila(frames):
    frames = np.asarray(frames)
    if frames.ndim != 4 or frames.shape[-1] != 3 or frames.dtype != np.uint8:
        raise ValueError("la pila tiene que ser uint8 (T, H, W, 3); llego "
                         f"{frames.dtype} {frames.shape}")
    if frames.nbytes > MEMORIA_MAX:
        raise MemoryError(f"la pila pesa {frames.nbytes / 1e6:.0f} MB y el "
                          f"tope es {MEMORIA_MAX / 1e6:.0f} MB: baja la "
                          "resolucion o los pasos")
    return frames


def recortar(frame, cx, cy, zoom):
    """Ventana de la MISMA proporcion centrada en (cx, cy) en fraccion 0-1
    del frame, `zoom` veces mas chica. Devuelve una vista (sin copiar)."""
    H, W = frame.shape[:2]
    if zoom <= 1.0 + 1e-9:
        return frame
    w = max(8, int(round(W / zoom)))
    h = max(8, int(round(w * H / W)))
    x0 = int(round(cx * W - w / 2))
    y0 = int(round(cy * H - h / 2))
    x0 = min(max(x0, 0), W - w)
    y0 = min(max(y0, 0), H - h)
    return frame[y0:y0 + h, x0:x0 + w]


def ritmo_por_tramos(tramos):
    """Remapea alpha -> fraccion de pelicula por tramos lineales.

    `tramos` es una lista de (alpha, fraccion) crecientes en ambos ejes,
    p. ej. [(0, 0), (0.4, 0.5), (0.7, 0.55), (1, 1)]: entre alpha 0.4 y
    0.7 la pelicula avanza solo el 5 %: camara lenta.
    """
    a = np.array([t[0] for t in tramos], dtype=np.float64)
    f = np.array([t[1] for t in tramos], dtype=np.float64)
    if np.any(np.diff(a) < 0) or np.any(np.diff(f) < 0):
        raise ValueError("los tramos tienen que ser crecientes")
    return lambda alpha: float(np.interp(alpha, a, f))


def seguir(posiciones, zoom, suavizado=15):
    """Encuadre que sigue una trayectoria (T,2) en pixeles. Devuelve
    encuadre(fraccion) -> (cx, cy, zoom) con la trayectoria suavizada."""
    pos = np.asarray(posiciones, dtype=np.float64)

    def suave(v):
        k = np.ones(suavizado) / suavizado
        return np.convolve(np.pad(v, (suavizado // 2, suavizado - 1
                                      - suavizado // 2), mode="edge"), k,
                           mode="valid")
    sx, sy = suave(pos[:, 0]), suave(pos[:, 1])

    def encuadre(frac, W, H):
        i = int(round(frac * (len(pos) - 1)))
        return sx[i] / W, sy[i] / H, zoom
    return encuadre


def zoom_hacia(cx, cy, zoom_final, desde=1.0):
    """Encuadre de zoom continuo (geometrico) hacia un punto fijo."""
    def encuadre(frac, W, H):
        z = desde * (zoom_final / desde) ** frac
        return cx, cy, z
    return encuadre


class Pelicula:
    """Una pila de frames como ImageMobject a pantalla completa.

    Se construye DENTRO de `construct` (necesita manim). `frames` es la pila
    uint8 (T,H,W,3). `nearest=True` para automatas (pixel duro), bicubico
    para campos.
    """

    def __init__(self, frames, alto=None, y=0.0, nearest=False, z=-500,
                 opacidad=1.0):
        from manim import ImageMobject, UP
        self.frames = validar_pila(frames)
        self.T, self.H, self.W = self.frames.shape[:3]
        self._alfa = np.full((self.H, self.W, 1), 255, dtype=np.uint8)
        self.mob = ImageMobject(self._rgba(self.frames[0]))
        self.mob.set_resampling_algorithm(0 if nearest else 3)
        if alto is None:
            from manim import config
            alto = config.frame_height
        self.mob.height = alto
        self.mob.move_to(UP * y)
        self.mob.set_z_index(z)
        self.mob.set_opacity(opacidad)
        self.k = 0

    def _rgba(self, frame):
        if frame.shape[:2] != self._alfa.shape[:2]:
            alfa = np.full(frame.shape[:2] + (1,), 255, dtype=np.uint8)
        else:
            alfa = self._alfa
        return np.concatenate([frame, alfa], axis=2)

    def mostrar(self, k, encuadre=None, frac=0.0):
        k = int(min(max(k, 0), self.T - 1))
        frame = self.frames[k]
        if encuadre is not None:
            cx, cy, z = encuadre(frac, self.W, self.H)
            frame = recortar(frame, cx, cy, z)
        self.mob.pixel_array = self._rgba(np.ascontiguousarray(frame))
        # manim captura `orig_alpha_pixel_array` al construir el ImageMobject
        # con la forma COMPLETA y `set_opacity` (lo que usa FadeOut) lo
        # multiplica sobre el alfa actual: si la pelicula acaba recortada
        # por un zoom, el FadeOut de cierre revienta ("could not broadcast")
        # y el contenedor se queda colgado sin escribir el mp4 (cazado en el
        # clip 10). Se mantiene siempre a la forma del frame mostrado.
        if (getattr(self.mob, "orig_alpha_pixel_array", None) is None
                or self.mob.orig_alpha_pixel_array.shape != frame.shape[:2]):
            self.mob.orig_alpha_pixel_array = np.full(frame.shape[:2], 255,
                                                      dtype=np.uint8)
        self.k = k
        return self

    def animacion(self, run_time, desde=0, hasta=None, ritmo=None,
                  encuadre=None, rate_func=None):
        """UpdateFromAlphaFunc que recorre los frames [desde, hasta].

        `ritmo(alpha)` -> fraccion 0-1 del tramo (ver `ritmo_por_tramos`);
        `encuadre(frac, W, H)` -> (cx, cy, zoom) (ver `seguir`, `zoom_hacia`).
        """
        from manim import UpdateFromAlphaFunc, linear
        hasta = self.T - 1 if hasta is None else int(hasta)
        desde = int(desde)
        peli = self

        def paso(_m, alpha):
            f = ritmo(alpha) if ritmo else alpha
            k = desde + f * (hasta - desde)
            peli.mostrar(int(round(k)), encuadre, f)
        return UpdateFromAlphaFunc(self.mob, paso, run_time=run_time,
                                   rate_func=rate_func or linear)

    def reproducir(self, escena, run_time, **kw):
        escena.play(self.animacion(run_time, **kw))
        return self


def converger(objetivos, W, H, n=None, T=150, semilla=1, color=C_VIVO,
              color_final=C_TINTA, vuelo=0.45, decaimiento=0.80,
              radio=0.9):
    """Un enjambre que vuela y se posa sobre unos puntos objetivo.

    `objetivos` (m,2) en pixeles del lienzo WxH (p. ej. el contorno de un
    titulo). Devuelve una pila uint8 (T,H,W,3): la primera fraccion
    `vuelo` del tiempo los agentes vuelan como bandada suelta (rumbo con
    ruido, cohesion debil), despues cada uno va a su objetivo con un
    resorte amortiguado y se queda. El color pasa de `color` a
    `color_final` conforme se posan. Para la intro: el titulo nace de una
    bandada.
    """
    rng = np.random.default_rng(semilla)
    obj = np.asarray(objetivos, dtype=np.float64)
    m = len(obj)
    n = m if n is None else int(n)
    idx = rng.permutation(m)[:n] if n <= m else rng.integers(0, m, n)
    meta = obj[idx]
    pos = np.column_stack([rng.random(n) * W, rng.random(n) * H])
    ang = rng.random(n) * 2 * np.pi
    vel = np.column_stack([np.cos(ang), np.sin(ang)]) * 2.2
    lienzo = np.zeros((H, W, 3), dtype=np.float32)
    frames = np.empty((T, H, W, 3), dtype=np.uint8)
    c0, c1 = hex_a_rgb(color) / 255.0, hex_a_rgb(color_final) / 255.0
    T_vuelo = int(T * vuelo)
    for t in range(T):
        if t < T_vuelo:
            centro = pos.mean(axis=0)
            vel += 0.004 * (centro - pos)
            ang = np.arctan2(vel[:, 1], vel[:, 0]) + rng.normal(0, 0.25, n)
            rap = np.linalg.norm(vel, axis=1)
            vel = np.column_stack([np.cos(ang), np.sin(ang)]) * rap[:, None]
            vel *= np.clip(2.2 / np.maximum(rap, 1e-9), 0.8, 1.2)[:, None]
            pos += vel
            pos[:, 0] = np.mod(pos[:, 0], W)
            pos[:, 1] = np.mod(pos[:, 1], H)
            f = 0.0
        else:
            u = (t - T_vuelo) / max(1, T - 1 - T_vuelo)
            k = 0.06 + 0.30 * u
            vel += k * (meta - pos) - (0.25 + 0.5 * u) * vel
            pos += vel
            f = min(1.0, u * 1.4)
        estela(lienzo, decaimiento if f < 1.0 else 0.6)
        rgb = c0 * (1 - f) + c1 * f
        hexc = "#%02x%02x%02x" % tuple(int(v * 255) for v in rgb)
        salpicar(lienzo, pos, hexc, 0.9, radio=radio)
        frames[t] = a_uint8(lienzo)
    return validar_pila(frames)


def mosaico(pilas, columnas, W, H, borde=2, fondo=C_FONDO):
    """Junta varias pilas (T_i,h_i,w_i,3) en una sola (T,H,W,3) por celdas
    iguales; cada pila se repite ciclicamente si es mas corta. Reescala
    por vecino mas cercano (numpy puro, sin PIL)."""
    n = len(pilas)
    filas = int(np.ceil(n / columnas))
    cw, ch = W // columnas, H // filas
    T = max(p.shape[0] for p in pilas)
    salida = np.empty((T, H, W, 3), dtype=np.uint8)
    salida[:] = hex_a_rgb(fondo).astype(np.uint8)
    for i, p in enumerate(pilas):
        r, c = divmod(i, columnas)
        h, w = p.shape[1:3]
        ys = (np.arange(ch - 2 * borde) * h / (ch - 2 * borde)).astype(int)
        xs = (np.arange(cw - 2 * borde) * w / (cw - 2 * borde)).astype(int)
        ts = np.arange(T) % p.shape[0]
        celda = p[ts][:, ys][:, :, xs]
        y0, x0 = r * ch + borde, c * cw + borde
        salida[:, y0:y0 + ch - 2 * borde, x0:x0 + cw - 2 * borde] = celda
    return validar_pila(salida)


__all__ = [
    "C_FONDO", "C_MEDIDO", "C_REGLA", "C_ORDEN", "C_ENERGIA", "C_VIVO",
    "C_MOBILIARIO", "C_EXTERNO", "C_TINTA", "RES_BASE", "RES_ZOOM",
    "hex_a_rgb", "lut", "LUTS", "colorear", "mezclar_capas", "salpicar",
    "a_uint8", "estela", "validar_pila", "recortar", "ritmo_por_tramos",
    "seguir", "zoom_hacia", "Pelicula", "mosaico", "converger",
]


# --- Submodulos bajo demanda (PEP 562) -------------------------------------
# `em.bandada.simular(...)` desde un clip sin tener que importar cada
# simulador en el style_block; los que no se usan no se cargan.
SIMULADORES = ("bandada", "moho", "arena", "vida", "turing", "ondas",
               "chladni", "ising", "pendulos", "cuencas", "epiciclos", "rio",
               "galaxias")


def __getattr__(nombre):
    if nombre in SIMULADORES:
        import importlib
        return importlib.import_module(f"{__name__}.{nombre}")
    raise AttributeError(f"module 'emergencia' has no attribute '{nombre}'")

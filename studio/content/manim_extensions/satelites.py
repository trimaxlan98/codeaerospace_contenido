"""Satelites, constelaciones NTN y visuales de IA para Manim CE, aptos para VPS.

Misma disciplina que fractales.py: todo el computo pesado es numpy
vectorizado y el resultado llega a la escena como ImageMobject o como POCOS
VMobjects con updaters sobre datos PREcalculados. Sin matplotlib, sin datos
externos (los continentes son poligonos propios), determinista (mismo
script -> mismo render, importante para --disable_caching).

Piezas:
  - ConstelacionWalker: constelacion Walker-delta real (planos con RAAN
    repartido, fase inter-plano) propagada en lote y proyectada en
    ortografica con inclinacion de camara; los satelites son Dots que un
    AnimarWalker mueve leyendo la trayectoria precalculada, con oclusion
    tras el disco terrestre. enlaces_walker() anade ISL dinamicos.
  - mapa_tierra() / imagen_mapa(): mapa equirrectangular estilizado
    rasterizado por ray-casting de poligonos lon/lat incluidos aqui.
  - subsatelites_walker() + animar_cobertura(): huellas de cobertura como
    casquetes esfericos (conteo de satelites visibles por celda) animadas
    mutando pixel_array con un lote de frames RGBA (patron morph_julia).
  - traza_terrestre() + puntos_en_mapa(): ground tracks sobre el mapa.
  - ventana_visibilidad(): elevacion vs tiempo desde una estacion.
  - IA: curva_aprendizaje() (recompensa RL sintetica determinista),
    heatmap_q() (raster pixelado de una tabla Q / politica).

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from satelites import (ConstelacionWalker, AnimarWalker, enlaces_walker,
                           imagen_mapa, subsatelites_walker, animar_cobertura,
                           traza_terrestre, puntos_en_mapa,
                           ventana_visibilidad, curva_aprendizaje, heatmap_q)
"""

import numpy as np

from manim import Animation, Circle, Dot, ImageMobject, Line, VGroup, VMobject

# Topes duros para no castigar el VPS (render capado a ~1.5 vCPU / 2 GB).
SATS_MAX = 240
FRAMES_MAX = 260          # frames precalculados por animacion (orbitas o cobertura)
RES_MAX_MAPA = 1920

R_TIERRA_KM = 6371.0
OMEGA_TIERRA = 2.0 * np.pi / 86164.0     # rad/s (dia sidereo)
_LUT_N = 512

# Paleta base del mapa y de la cobertura (hex sin dependencia de matplotlib).
COLORES_MAPA = {
    "oceano":    "#0a1428",
    "tierra":    "#233f54",
    "reticula":  "#1b2a44",
    "cobertura": "#4dd8e6",   # 1 satelite visible
    "solape":    "#ffd27d",   # 2+ satelites visibles
}


def _hex_a_rgb(hexcolor):
    h = hexcolor.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def _lut_puntos(puntos):
    """LUT (N,3) 0..255 interpolada de [(pos, hex), ...]."""
    pos = np.array([p for p, _ in puntos])
    cols = np.stack([_hex_a_rgb(c) for _, c in puntos])
    x = np.linspace(0.0, 1.0, _LUT_N)
    return np.stack([np.interp(x, pos, cols[:, k]) for k in range(3)], axis=1)


# ── continentes estilizados (lon, lat), rasterizados por ray-casting ─────────
# Silvetas gruesas pero reconocibles; el mapa es escenografia, no cartografia.
_CONTINENTES = [
    # Norteamerica (con Centroamerica hasta Panama)
    [(-166, 68), (-140, 71), (-118, 72), (-98, 73), (-84, 69), (-70, 62),
     (-53, 49), (-65, 44), (-76, 36), (-81, 28), (-90, 29), (-97, 26),
     (-92, 18), (-88, 21), (-86, 16), (-83, 12), (-79, 9), (-77, 7),
     (-80, 8), (-85, 12), (-92, 15), (-96, 16), (-105, 20), (-110, 24),
     (-118, 33), (-122, 38), (-124, 44), (-128, 50), (-136, 58), (-152, 59),
     (-166, 62)],
    # Sudamerica
    [(-77, 7), (-70, 11), (-62, 10), (-52, 4), (-44, -3), (-35, -7),
     (-39, -15), (-41, -22), (-48, -28), (-53, -34), (-58, -39), (-65, -45),
     (-69, -52), (-72, -54), (-74, -46), (-73, -37), (-71, -30), (-70, -18),
     (-76, -14), (-81, -6), (-80, 1)],
    # Groenlandia
    [(-58, 64), (-52, 60), (-43, 60), (-38, 65), (-22, 70), (-20, 76),
     (-30, 82), (-55, 82), (-68, 78), (-60, 70)],
    # Eurasia (Iberia -> Siberia -> India/Indochina -> Arabia -> Mediterraneo)
    [(-9, 37), (-9, 43), (-2, 48), (2, 51), (8, 54), (18, 56), (28, 60),
     (30, 70), (40, 68), (60, 69), (75, 73), (95, 76), (110, 74), (130, 72),
     (150, 70), (170, 67), (179, 65), (179, 62), (160, 60), (155, 52),
     (142, 54), (135, 44), (122, 30), (110, 20), (105, 9), (98, 8),
     (92, 21), (88, 22), (80, 8), (77, 8), (72, 20), (67, 24), (60, 25),
     (58, 22), (55, 17), (45, 12), (43, 15), (39, 20), (34, 28), (36, 36),
     (27, 36), (22, 38), (15, 38), (10, 38), (3, 36), (-6, 36)],
    # Africa (+ Madagascar aparte)
    [(-6, 35), (-10, 31), (-17, 21), (-17, 15), (-8, 5), (8, 4), (9, -1),
     (12, -13), (14, -22), (17, -29), (19, -34), (25, -34), (31, -29),
     (35, -22), (40, -15), (40, -5), (42, 0), (48, 5), (51, 11), (43, 11),
     (38, 18), (33, 28), (32, 31), (23, 33), (10, 34), (0, 36)],
    [(43, -25), (48, -25), (50, -13), (45, -15)],                # Madagascar
    # Australia
    [(114, -22), (114, -34), (118, -35), (125, -32), (136, -35), (140, -38),
     (146, -39), (150, -37), (153, -30), (153, -25), (147, -19), (142, -11),
     (136, -12), (132, -11), (126, -14), (122, -18)],
    # Reino Unido y Japon, como blobs minimos
    [(-5, 50), (-6, 56), (-3, 59), (0, 53), (1, 51)],
    [(130, 31), (133, 34), (139, 36), (142, 40), (145, 44), (141, 44),
     (136, 36), (131, 33)],
    # Antartida (banda)
    [(-180, -71), (180, -71), (180, -90), (-180, -90)],
]


def _mascara_poligono(lon_g, lat_g, poligono):
    """Ray-casting even-odd vectorizado sobre la malla lon/lat."""
    dentro = np.zeros(lon_g.shape, dtype=bool)
    n = len(poligono)
    for k in range(n):
        x1, y1 = poligono[k]
        x2, y2 = poligono[(k + 1) % n]
        if y1 == y2:
            continue
        cruza = (lat_g < y1) != (lat_g < y2)
        x_corte = x1 + (lat_g - y1) * (x2 - x1) / (y2 - y1)
        dentro ^= cruza & (lon_g < x_corte)
    return dentro


def mascara_tierra(res=(960, 480)):
    """Mascara booleana (res_y, res_x) de tierra firme; lat +90 arriba."""
    res_x = int(min(res[0], RES_MAX_MAPA))
    res_y = int(min(res[1], RES_MAX_MAPA))
    lons = np.linspace(-180.0, 180.0, res_x)
    lats = np.linspace(90.0, -90.0, res_y)          # fila 0 = polo norte
    lon_g, lat_g = np.meshgrid(lons, lats)
    mask = np.zeros((res_y, res_x), dtype=bool)
    for poli in _CONTINENTES:
        mask |= _mascara_poligono(lon_g, lat_g, poli)
    return mask


def mapa_tierra(res=(960, 480), reticula=True, colores=COLORES_MAPA):
    """RGBA uint8 del mapa equirrectangular estilizado."""
    mask = mascara_tierra(res)
    res_y, res_x = mask.shape
    rgba = np.empty((res_y, res_x, 4), dtype=np.uint8)
    oceano = _hex_a_rgb(colores["oceano"])
    tierra = _hex_a_rgb(colores["tierra"])
    rgba[..., :3] = np.where(mask[..., None], tierra, oceano).astype(np.uint8)
    rgba[..., 3] = 255
    if reticula:
        ret = _hex_a_rgb(colores["reticula"]).astype(np.uint8)
        for lon in range(-150, 180, 30):
            x = int((lon + 180.0) / 360.0 * (res_x - 1))
            rgba[:, x, :3] = ret
        for lat in range(-60, 90, 30):
            y = int((90.0 - lat) / 180.0 * (res_y - 1))
            rgba[y, :, :3] = ret
    return rgba


def _imagen(rgba, alto_escena, pixelado=False):
    img = ImageMobject(rgba)
    # 3=BICUBIC (suave) para mapas/cobertura; 0=NEAREST para heatmaps pixelados
    img.set_resampling_algorithm(0 if pixelado else 3)
    if alto_escena is not None:
        img.height = alto_escena
    return img


def imagen_mapa(res=(960, 480), alto_escena=6.0, reticula=True):
    """ImageMobject del mapa estilizado listo para la escena."""
    return _imagen(mapa_tierra(res, reticula), alto_escena)


def puntos_en_mapa(mapa, lonlat):
    """Coordenadas de escena (N,3) para (lon,lat) sobre un ImageMobject mapa."""
    lonlat = np.atleast_2d(np.asarray(lonlat, dtype=np.float64))
    c = mapa.get_center()
    w, h = mapa.width, mapa.height
    x = c[0] + (lonlat[:, 0] / 360.0) * w
    y = c[1] + (lonlat[:, 1] / 180.0) * h
    return np.stack([x, y, np.zeros_like(x)], axis=1)


# ── propagacion Walker-delta (orbitas circulares, unidades = radios ──────────
# terrestres) y proyeccion ortografica de camara ─────────────────────────────

def _rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def posiciones_walker(frames, planos, sats_por_plano, inclinacion_deg=53.0,
                      altitud_km=550.0, f_walker=1, vueltas=1.0, fase0=0.0):
    """Posiciones ECI (frames, N, 3) de una Walker-delta; radio orbital en
    radios terrestres. `vueltas` = orbitas completadas a lo largo de la
    animacion; `fase0` desplaza todas las fases (0..1)."""
    frames = int(min(frames, FRAMES_MAX))
    n_sats = planos * sats_por_plano
    if n_sats > SATS_MAX:
        raise ValueError(f"{n_sats} satelites supera SATS_MAX={SATS_MAX}")
    r = 1.0 + altitud_km / R_TIERRA_KM
    inc = np.radians(inclinacion_deg)
    t = np.linspace(0.0, 1.0, frames)[:, None]              # (T,1)
    p_idx = np.repeat(np.arange(planos), sats_por_plano)    # (N,)
    j_idx = np.tile(np.arange(sats_por_plano), planos)
    u = 2.0 * np.pi * (j_idx / sats_por_plano
                       + f_walker * p_idx / (planos * sats_por_plano)
                       + fase0 + vueltas * t)               # (T,N)
    en_plano = np.stack([np.cos(u), np.sin(u), np.zeros_like(u)],
                        axis=-1) * r                        # (T,N,3)
    pos = np.empty_like(en_plano)
    for p in range(planos):
        m = _rot_z(2.0 * np.pi * p / planos) @ _rot_x(inc)
        cols = p_idx == p
        pos[:, cols, :] = en_plano[:, cols, :] @ m.T
    return pos


def proyectar(puntos, tilt_deg=20.0, giro_deg=0.0):
    """Ortografica: devuelve (..., 3) = (x_pantalla, y_pantalla, profundidad).

    Eje z ECI = polo norte, que en pantalla apunta hacia arriba; `tilt`
    inclina la camara para mirar el globo un poco desde arriba y `giro` lo
    rota sobre su eje. profundidad > 0 = hacia el espectador.
    """
    m = _rot_x(np.radians(tilt_deg)) @ _rot_z(np.radians(giro_deg))
    q = puntos @ m.T
    return np.stack([q[..., 0], q[..., 2], -q[..., 1]], axis=-1)


class ConstelacionWalker(VGroup):
    """Constelacion Walker-delta proyectada, con oclusion tras la Tierra.

    Los Dots NO llevan updaters: AnimarWalker los mueve leyendo
    `self.trayectoria` (frames, N, 3 ya proyectada y escalada). Las orbitas
    son polilineas estaticas (la camara no se mueve durante la animacion).
    """

    def __init__(self, planos=5, sats_por_plano=8, inclinacion_deg=53.0,
                 altitud_km=550.0, f_walker=1, frames=200, vueltas=0.35,
                 tilt_deg=20.0, giro_deg=0.0, escala=1.15, radio_sat=0.045,
                 color_tierra="#123c63", color_orbita="#33415e",
                 color_sat="#ffd27d", opacidad_oculto=0.12, **kwargs):
        super().__init__(**kwargs)
        self.escala = escala
        self.opacidad_oculto = opacidad_oculto
        pos = posiciones_walker(frames, planos, sats_por_plano,
                                inclinacion_deg, altitud_km, f_walker, vueltas)
        self.trayectoria = proyectar(pos, tilt_deg, giro_deg) * escala

        self.tierra = Circle(radius=escala, color=color_tierra,
                             fill_color=color_tierra, fill_opacity=0.85,
                             stroke_width=2.5, stroke_opacity=0.9)
        self.add(self.tierra)

        self.orbitas = VGroup()
        r = 1.0 + altitud_km / R_TIERRA_KM
        fino = np.linspace(0.0, 2.0 * np.pi, 120)
        anillo = np.stack([np.cos(fino), np.sin(fino),
                           np.zeros_like(fino)], axis=-1) * r
        for p in range(planos):
            m = _rot_z(2.0 * np.pi * p / planos) @ _rot_x(
                np.radians(inclinacion_deg))
            proy = proyectar(anillo @ m.T, tilt_deg, giro_deg) * escala
            cam = VMobject(stroke_color=color_orbita, stroke_width=1.4,
                           stroke_opacity=0.65)
            cam.set_points_smoothly(
                [np.array([q[0], q[1], 0.0]) for q in proy] +
                [np.array([proy[0][0], proy[0][1], 0.0])])
            self.orbitas.add(cam)
        self.add(self.orbitas)

        self.sats = VGroup()
        for k in range(self.trayectoria.shape[1]):
            x, y, _ = self.trayectoria[0, k]
            self.sats.add(Dot([x, y, 0.0], radius=radio_sat, color=color_sat))
        self.add(self.sats)
        self._colocar(0)

    def _colocar(self, frame):
        centro = self.tierra.get_center()
        pts = self.trayectoria[frame]
        for dot, (x, y, z) in zip(self.sats, pts):
            dot.move_to(centro + np.array([x, y, 0.0]))
            oculto = z < 0 and (x * x + y * y) < self.escala ** 2
            dot.set_opacity(self.opacidad_oculto if oculto else 1.0)

    def frame_de_alpha(self, alpha):
        return int(round(alpha * (self.trayectoria.shape[0] - 1)))


class AnimarWalker(Animation):
    """Recorre la trayectoria precalculada de la constelacion."""

    def __init__(self, constelacion: ConstelacionWalker, **kwargs):
        kwargs.setdefault("rate_func", lambda a: a)
        super().__init__(constelacion, **kwargs)

    def interpolate_mobject(self, alpha):
        self.mobject._colocar(self.mobject.frame_de_alpha(alpha))


def enlaces_walker(cons: ConstelacionWalker, entre_planos=True,
                   color="#4dd8e6", ancho=1.6, opacidad=0.55):
    """ISL como Lines con updater sobre los Dots (se ocultan con ellos).

    Enlaza cada satelite con el siguiente de su plano y, si `entre_planos`,
    con su homologo del plano vecino. Llamar clear_updaters() al terminar.
    """
    n = len(cons.sats)
    planos = len(cons.orbitas)
    spp = n // planos
    pares = []
    for p in range(planos):
        for j in range(spp):
            a = p * spp + j
            pares.append((a, p * spp + (j + 1) % spp))
            if entre_planos:
                pares.append((a, ((p + 1) % planos) * spp + j))
    enlaces = VGroup()
    for a, b in pares:
        linea = Line(cons.sats[a].get_center(), cons.sats[b].get_center(),
                     stroke_color=color, stroke_width=ancho,
                     stroke_opacity=opacidad)

        def _seguir(mob, a=a, b=b):
            da, db = cons.sats[a], cons.sats[b]
            mob.put_start_and_end_on(da.get_center(), db.get_center())
            visibles = min(da.get_fill_opacity(), db.get_fill_opacity())
            mob.set_stroke(opacity=opacidad if visibles > 0.5 else 0.0)

        linea.add_updater(_seguir)
        enlaces.add(linea)
    return enlaces


# ── subsatelites, cobertura y ground tracks ──────────────────────────────────

def subsatelites_walker(frames, planos, sats_por_plano, inclinacion_deg=53.0,
                        altitud_km=550.0, f_walker=1, vueltas=1.0,
                        duracion_s=None, fase0=0.0):
    """(frames, N, 2) = (lon, lat) del punto subsatelital, con rotacion
    terrestre si `duracion_s` (segundos simulados totales) se indica."""
    pos = posiciones_walker(frames, planos, sats_por_plano, inclinacion_deg,
                            altitud_km, f_walker, vueltas, fase0)
    lat = np.degrees(np.arcsin(np.clip(pos[..., 2] /
                                       np.linalg.norm(pos, axis=-1), -1, 1)))
    lon = np.degrees(np.arctan2(pos[..., 1], pos[..., 0]))
    if duracion_s:
        t = np.linspace(0.0, duracion_s, pos.shape[0])[:, None]
        lon = lon - np.degrees(OMEGA_TIERRA * t)
    lon = (lon + 180.0) % 360.0 - 180.0
    return np.stack([lon, lat], axis=-1)


def angulo_cobertura(altitud_km, elevacion_min_deg=10.0):
    """Radio angular (grados de arco terrestre) del casquete de cobertura."""
    e = np.radians(elevacion_min_deg)
    rho = R_TIERRA_KM / (R_TIERRA_KM + altitud_km)
    return np.degrees(np.arccos(rho * np.cos(e)) - e)


def conteo_cobertura(res, lonlat_sats, psi_deg):
    """(res_y, res_x) uint8: cuantos satelites ven cada celda del mapa."""
    res_x, res_y = int(res[0]), int(res[1])
    lons = np.radians(np.linspace(-180.0, 180.0, res_x))
    lats = np.radians(np.linspace(90.0, -90.0, res_y))
    sin_lat = np.sin(lats)[:, None]
    cos_lat = np.cos(lats)[:, None]
    cos_psi = np.cos(np.radians(psi_deg))
    total = np.zeros((res_y, res_x), dtype=np.uint8)
    for lon_s, lat_s in np.atleast_2d(lonlat_sats):
        ls, cs = np.radians(lat_s), np.radians(lon_s)
        cos_c = (sin_lat * np.sin(ls)
                 + cos_lat * np.cos(ls) * np.cos(lons[None, :] - cs))
        total += (cos_c >= cos_psi).astype(np.uint8)
    return total


def colorear_cobertura(base_rgba, conteo, colores=COLORES_MAPA,
                       alpha1=0.5, alpha2=0.75):
    """Mezcla la capa de cobertura (1 sat / 2+ sats) sobre el mapa base."""
    rgba = base_rgba.copy()
    c1 = _hex_a_rgb(colores["cobertura"])
    c2 = _hex_a_rgb(colores["solape"])
    piso = rgba[..., :3].astype(np.float64)
    m1 = conteo == 1
    m2 = conteo >= 2
    piso[m1] = piso[m1] * (1 - alpha1) + c1 * alpha1
    piso[m2] = piso[m2] * (1 - alpha2) + c2 * alpha2
    rgba[..., :3] = np.clip(piso, 0, 255).astype(np.uint8)
    return rgba


def animar_cobertura(escena, trazas_lonlat, altitud_km, duracion=8.0,
                     res=(640, 320), elevacion_min_deg=10.0, alto_escena=6.0,
                     reticula=True, imagen=None):
    """Cobertura animada sobre el mapa mutando pixel_array (lote de frames).

    `trazas_lonlat` es (T, N, 2) de subsatelites_walker (T <= FRAMES_MAX).
    Devuelve el ImageMobject (queda en escena con el ultimo frame). Si
    `imagen` (de una llamada previa con MISMA res) se pasa, se reutiliza.
    """
    trazas = np.asarray(trazas_lonlat)[:FRAMES_MAX]
    base = mapa_tierra(res, reticula)
    psi = angulo_cobertura(altitud_km, elevacion_min_deg)
    lote = [np.ascontiguousarray(
        colorear_cobertura(base, conteo_cobertura(res, trazas[k], psi)))
        for k in range(trazas.shape[0])]
    if imagen is None:
        imagen = _imagen(lote[0], alto_escena)
        escena.add(imagen)
    frames = len(lote)

    def actualizar(mob, alpha):
        mob.pixel_array = lote[int(round(alpha * (frames - 1)))]

    from manim import UpdateFromAlphaFunc
    escena.play(UpdateFromAlphaFunc(imagen, actualizar), run_time=duracion,
                rate_func=lambda a: a)
    return imagen


def traza_terrestre(lonlat, mapa, color="#ffd27d", ancho=2.2, opacidad=0.9):
    """Ground track de UN satelite como VGroup de polilineas sobre `mapa`.

    `lonlat` es (T, 2); se parte donde cruza el antimeridiano.
    """
    lonlat = np.asarray(lonlat)
    saltos = np.where(np.abs(np.diff(lonlat[:, 0])) > 180.0)[0] + 1
    grupos = np.split(lonlat, saltos)
    trazo = VGroup()
    for g in grupos:
        if len(g) < 2:
            continue
        pts = puntos_en_mapa(mapa, g)
        v = VMobject(stroke_color=color, stroke_width=ancho,
                     stroke_opacity=opacidad)
        v.set_points_smoothly(list(pts))
        trazo.add(v)
    return trazo


def ventana_visibilidad(lat_est, lon_est, lonlat_sat, altitud_km):
    """Elevacion (grados) del satelite visto desde la estacion, por frame.

    `lonlat_sat` es (T, 2). Devuelve (t 0..1, elevacion_deg) — para Axes.
    Elevaciones bajo el horizonte quedan negativas (recortar al plotear).
    """
    lonlat_sat = np.asarray(lonlat_sat)
    le, ce = np.radians(lat_est), np.radians(lon_est)
    ls = np.radians(lonlat_sat[:, 1])
    cs = np.radians(lonlat_sat[:, 0])
    cos_c = (np.sin(le) * np.sin(ls)
             + np.cos(le) * np.cos(ls) * np.cos(cs - ce))
    cos_c = np.clip(cos_c, -1.0, 1.0)
    sin_c = np.sqrt(1.0 - cos_c ** 2)
    rho = R_TIERRA_KM / (R_TIERRA_KM + altitud_km)
    with np.errstate(divide="ignore", invalid="ignore"):
        elev = np.degrees(np.arctan2(cos_c - rho, sin_c))
    t = np.linspace(0.0, 1.0, len(elev))
    return t, elev


# ── visuales de IA (deterministas) ───────────────────────────────────────────

def curva_aprendizaje(semilla=7, n=240, r_inicial=-75.0, r_final=-12.0,
                      ruido=5.0, caidas=(0.35, 0.62), suavizado=9):
    """Curva de recompensa RL sintetica y reproducible: mejora sigmoidea +
    ruido suavizado + caidas transitorias (exploracion). Devuelve (x, y)."""
    rng = np.random.default_rng(semilla)
    x = np.arange(n, dtype=np.float64)
    forma = 1.0 / (1.0 + np.exp(-(x / n - 0.42) * 9.0))
    y = r_inicial + (r_final - r_inicial) * forma
    y += rng.normal(0.0, ruido, n)
    for pos in caidas:
        k = int(pos * n)
        prof = (0.25 + 0.35 * rng.random()) * (r_final - r_inicial)
        ancho = max(4, n // 24)
        caida = -prof * np.exp(-0.5 * ((x - k) / ancho) ** 2)
        y += caida
    # Media movil con relleno de borde: sin el pad, los extremos de la curva
    # se hunden hacia 0 (ventana medio vacia) y el arranque queda falseado.
    nucleo = np.ones(suavizado) / suavizado
    borde = suavizado // 2
    y = np.convolve(np.pad(y, borde, mode="edge"), nucleo,
                    mode="same")[borde:-borde]
    return x, y


def heatmap_q(matriz, paleta=None, alto_escena=3.0):
    """ImageMobject pixelado (NEAREST) de una tabla Q / politica pequena.

    `matriz` se normaliza a 0..1 y se colorea con una LUT azul->cian->dorado
    (o `paleta` = [(pos, hex), ...] propia).
    """
    m = np.asarray(matriz, dtype=np.float64)
    rango = m.max() - m.min()
    t = (m - m.min()) / rango if rango > 0 else np.zeros_like(m)
    lut = _lut_puntos(paleta or [(0.0, "#101a38"), (0.45, "#1b6b8f"),
                                 (0.75, "#4dd8e6"), (1.0, "#ffd27d")])
    idx = np.clip((t * (_LUT_N - 1)).astype(np.int32), 0, _LUT_N - 1)
    rgba = np.empty(m.shape + (4,), dtype=np.uint8)
    rgba[..., :3] = lut[idx].astype(np.uint8)
    rgba[..., 3] = 255
    return _imagen(rgba, alto_escena, pixelado=True)


# =============================================================================
# Ampliacion para el curso 27 "Satelites: la maquina que no se cae" (VERTICAL)
#
# Todo lo de abajo se añade SIN tocar nada de arriba: los clips del curso 2 y
# del 9, que ya estan en la DB de produccion, siguen valiendo igual.
#
# Disciplina de la casa: numpy puro, determinista, sin red ni disco, y **cero
# cifras inventadas** — lo que sale en pantalla lo calcula una de estas
# funciones durante el render. Las constantes fisicas (MU_TIERRA, R_TIERRA_KM,
# el dia sidereo) NO son cifras medidas aqui: en pantalla van en gris.
# =============================================================================

MU_TIERRA = 398600.4418          # km^3/s^2, WGS-84 (constante: en pantalla, gris)
C_LUZ_KM_S = 299792.458          # km/s (constante)
KM_POR_GRADO = 2.0 * np.pi * R_TIERRA_KM / 360.0     # 111.19 km/grado de arco

# Margen sobre la superficie para dar por buena una linea de vista entre dos
# satelites: por debajo de ~80 km el rayo rasa la atmosfera densa y no sirve.
H_ATMOSFERA_KM = 80.0


# ── M1 · caerse sin llegar al suelo ──────────────────────────────────────────

def velocidad_circular(altitud_km):
    """Rapidez (km/s) de una orbita circular a esa altura."""
    r = R_TIERRA_KM + float(altitud_km)
    return float(np.sqrt(MU_TIERRA / r))


def periodo_orbital(altitud_km):
    """Periodo (3a de Kepler) de una orbita circular, en varias unidades."""
    r = R_TIERRA_KM + float(altitud_km)
    seg = 2.0 * np.pi * np.sqrt(r ** 3 / MU_TIERRA)
    return {"segundos": float(seg), "minutos": float(seg / 60.0),
            "horas": float(seg / 3600.0), "radio_km": float(r),
            "velocidad_km_s": velocidad_circular(altitud_km)}


def caida_vs_curvatura(altitud_km=400.0, t_s=1.0):
    """La cuenta de Newton: en `t_s` el satelite CAE tanto como se aleja el
    suelo por la curvatura de la Tierra. Por eso no llega nunca.

    Devuelve la caida en metros, la distancia recorrida en ese tiempo a la
    velocidad circular, y cuanto se hunde la superficie esferica bajo esa
    cuerda (la "curvatura"). Las dos ultimas cifras tienen que coincidir:
    eso ES la orbita.
    """
    r = R_TIERRA_KM + float(altitud_km)
    g = MU_TIERRA / r ** 2                      # km/s^2 a esa altura
    v = velocidad_circular(altitud_km)
    d = v * float(t_s)                          # km recorridos
    caida_km = 0.5 * g * float(t_s) ** 2
    # Cuanto baja la circunferencia de radio r bajo una cuerda de largo d.
    curva_km = r - np.sqrt(max(r ** 2 - d ** 2, 0.0))
    return {"altitud_km": float(altitud_km), "t_s": float(t_s),
            "velocidad_km_s": float(v), "distancia_km": float(d),
            "caida_m": float(caida_km * 1000.0),
            "curvatura_m": float(curva_km * 1000.0),
            "g_m_s2": float(g * 1000.0)}


def canon_newton(v0_km_s, altitud_km=300.0, dt_s=2.0, pasos=6000,
                 vueltas_max=1.02):
    """El cañon de Newton: dispara HORIZONTAL desde una montaña y deja que la
    gravedad haga el resto (dos cuerpos, integrado con RK4).

    Devuelve la trayectoria en RADIOS TERRESTRES (para dibujarla sobre un
    circulo de radio 1) y si acabo en el suelo o dio la vuelta entera.
    """
    r0 = R_TIERRA_KM + float(altitud_km)
    y = np.array([r0, 0.0, 0.0, float(v0_km_s)])       # x, y, vx, vy

    def deriv(s):
        rr = np.hypot(s[0], s[1])
        a = -MU_TIERRA / rr ** 3
        return np.array([s[2], s[3], a * s[0], a * s[1]])

    pts = [y[:2].copy()]
    impacto = False
    ang = 0.0
    pasos = int(min(pasos, 20000))
    for _ in range(pasos):
        k1 = deriv(y)
        k2 = deriv(y + 0.5 * dt_s * k1)
        k3 = deriv(y + 0.5 * dt_s * k2)
        k4 = deriv(y + dt_s * k3)
        nuevo = y + (dt_s / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        # angulo recorrido (para cortar cuando cierra la vuelta)
        a0 = np.arctan2(y[1], y[0])
        a1 = np.arctan2(nuevo[1], nuevo[0])
        d = (a1 - a0 + np.pi) % (2 * np.pi) - np.pi
        ang += d
        y = nuevo
        pts.append(y[:2].copy())
        if np.hypot(y[0], y[1]) <= R_TIERRA_KM:
            impacto = True
            break
        if abs(ang) >= 2.0 * np.pi * vueltas_max:
            break
    pts = np.array(pts) / R_TIERRA_KM
    return {"puntos": pts, "impacto": bool(impacto),
            "v0_km_s": float(v0_km_s),
            "altitud_km": float(altitud_km),
            "vueltas": float(abs(ang) / (2.0 * np.pi)),
            "alcance_grados": float(np.degrees(abs(ang))),
            "r_min_km": float(np.hypot(pts[:, 0], pts[:, 1]).min()
                              * R_TIERRA_KM),
            "r_max_km": float(np.hypot(pts[:, 0], pts[:, 1]).max()
                              * R_TIERRA_KM)}


def _kepler_E(M, e, iteraciones=60, tol=1e-13):
    """Resuelve M = E - e sen E por Newton-Raphson (vectorizado)."""
    M = np.asarray(M, dtype=np.float64)
    E = M + e * np.sin(M)
    for _ in range(iteraciones):
        f = E - e * np.sin(E) - M
        paso = f / (1.0 - e * np.cos(E))
        E = E - paso
        if np.max(np.abs(paso)) < tol:
            break
    return E


def elipse_kepler(a_km, e, muestras=720, t0_s=0.0, fraccion=1.0):
    """Orbita eliptica muestreada en TIEMPOS IGUALES (no en angulos iguales).

    Esa es toda la gracia: al repartir los puntos por tiempo, se ven juntos
    en el apogeo (va lento) y separados en el perigeo (va rapido).

    Devuelve puntos (n,2) en km, rapidez por punto, radio y el tiempo.
    """
    a = float(a_km)
    e = float(e)
    if not 0.0 <= e < 1.0:
        raise ValueError(f"excentricidad {e} fuera de [0,1)")
    T = 2.0 * np.pi * np.sqrt(a ** 3 / MU_TIERRA)
    t = t0_s + np.linspace(0.0, fraccion * T, int(muestras))
    M = 2.0 * np.pi * t / T
    E = _kepler_E(M, e)
    x = a * (np.cos(E) - e)
    y = a * np.sqrt(1.0 - e ** 2) * np.sin(E)
    r = np.hypot(x, y)
    v = np.sqrt(MU_TIERRA * (2.0 / r - 1.0 / a))
    return {"puntos": np.stack([x, y], axis=1), "r_km": r, "v_km_s": v,
            "t_s": t, "periodo_s": float(T), "a_km": a, "e": e,
            "perigeo_km": float(a * (1 - e) - R_TIERRA_KM),
            "apogeo_km": float(a * (1 + e) - R_TIERRA_KM)}


def _area_barrida(puntos):
    """Area del sector barrido: triangulos desde el foco (formula del cordon)."""
    x, y = puntos[:, 0], puntos[:, 1]
    return float(0.5 * np.abs(np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])))


def areas_barridas(a_km, e, ventana=0.06, muestras=4000):
    """La 2a de Kepler MEDIDA, no supuesta.

    Toma la MISMA fraccion de periodo en el perigeo y en el apogeo, e integra
    el area de los dos sectores sobre la trayectoria dibujada. El cociente
    tiene que dar 1.000: areas iguales en tiempos iguales.
    """
    # Una muestra de mas y se descarta la ultima: linspace(0,T,n) repite el
    # perigeo en los dos extremos, y con el duplicado el `roll` de abajo
    # dejaria dos puntos identicos dentro de la ventana.
    orb = elipse_kepler(a_km, e, muestras=muestras + 1)
    pts = orb["puntos"][:-1]
    n = len(pts)
    ancho = max(3, int(ventana * n))
    # El perigeo cae en t=0, o sea en el BORDE del muestreo: hay que envolver
    # para tomar media ventana de antes y media de despues. Si se toman los
    # primeros `ancho` puntos a secas, la ventana del perigeo es media
    # ventana y la del apogeo entera, y el cociente sale 0.4% corto sin que
    # nada este mal en la fisica.
    peri = np.roll(pts, ancho // 2, axis=0)[:ancho]
    k = n // 2
    apo = pts[k - ancho // 2: k - ancho // 2 + ancho]
    a_peri, a_apo = _area_barrida(peri), _area_barrida(apo)
    v_peri = float(orb["v_km_s"][0])
    v_apo = float(orb["v_km_s"][k])
    return {"area_perigeo_km2": a_peri, "area_apogeo_km2": a_apo,
            "cociente_areas": float(a_peri / a_apo) if a_apo else float("nan"),
            "v_perigeo_km_s": v_peri, "v_apogeo_km_s": v_apo,
            "cociente_v": float(v_peri / v_apo),
            "cociente_v_teorico": float((1 + e) / (1 - e)),
            "ventana_s": float(ventana * orb["periodo_s"]),
            "periodo_s": orb["periodo_s"]}


# ── M2 · la Tierra gira debajo ───────────────────────────────────────────────

def radio_huella_km(altitud_km, elevacion_min_deg=10.0):
    """Radio de la huella MEDIDO SOBRE LA SUPERFICIE (arco, no cuerda)."""
    psi = angulo_cobertura(altitud_km, elevacion_min_deg)
    return float(np.radians(psi) * R_TIERRA_KM)


def fraccion_visible(altitud_km, elevacion_min_deg=10.0):
    """Fraccion de la ESFERA que ve un solo satelite: (1 - cos psi)/2.

    Se calcula sobre la esfera a proposito: contar celdas del mapa
    equirrectangular sin pesar por cos(lat) infla los casquetes polares.
    """
    psi = np.radians(angulo_cobertura(altitud_km, elevacion_min_deg))
    return float((1.0 - np.cos(psi)) / 2.0)


def corrimiento_traza(altitud_km):
    """Cuanto se corre la traza hacia el OESTE en cada vuelta.

    La Tierra no espera: mientras el satelite da una vuelta, el planeta ha
    girado bajo el. Por eso la traza nunca cierra sobre si misma.
    """
    per = periodo_orbital(altitud_km)
    grados = float(np.degrees(OMEGA_TIERRA * per["segundos"]))
    return {"periodo_min": per["minutos"], "grados_por_vuelta": grados,
            "km_ecuador": float(grados * KM_POR_GRADO),
            "vueltas_por_dia": float(86164.0 / per["segundos"])}


def _subsat_uno(t_s, altitud_km=550.0, inclinacion_deg=53.0, raan_deg=0.0,
                fase0=0.0, con_rotacion=True):
    """Punto subsatelital (T,2) lon/lat de UN satelite en los tiempos `t_s`.

    Propagador propio, sin el tope de FRAMES_MAX de `posiciones_walker`: ese
    cap protege las ANIMACIONES (memoria), pero una cifra medida necesita
    resolucion temporal fina (un pase dura 9 min de una orbita de 95).
    """
    t = np.asarray(t_s, dtype=np.float64)
    r = 1.0 + float(altitud_km) / R_TIERRA_KM
    per = periodo_orbital(altitud_km)["segundos"]
    u = 2.0 * np.pi * (t / per + float(fase0))
    en_plano = np.stack([np.cos(u), np.sin(u), np.zeros_like(u)], axis=-1) * r
    m = _rot_z(np.radians(raan_deg)) @ _rot_x(np.radians(inclinacion_deg))
    pos = en_plano @ m.T
    lat = np.degrees(np.arcsin(np.clip(pos[:, 2] / np.linalg.norm(pos, axis=1),
                                       -1, 1)))
    lon = np.degrees(np.arctan2(pos[:, 1], pos[:, 0]))
    if con_rotacion:
        lon = lon - np.degrees(OMEGA_TIERRA * t)
    lon = (lon + 180.0) % 360.0 - 180.0
    return np.stack([lon, lat], axis=1)


def azimut(lat_est, lon_est, lonlat_sat):
    """Azimut (grados desde el norte, horario) del satelite desde la estacion.

    Con la elevacion de `ventana_visibilidad` completa la coordenada del
    cielo: (azimut, elevacion) es lo que apunta una antena y lo que dibuja
    una boveda polar.
    """
    lonlat_sat = np.atleast_2d(np.asarray(lonlat_sat, dtype=np.float64))
    la, lo = np.radians(lat_est), np.radians(lon_est)
    ls, cs = np.radians(lonlat_sat[:, 1]), np.radians(lonlat_sat[:, 0])
    y = np.sin(cs - lo) * np.cos(ls)
    x = np.cos(la) * np.sin(ls) - np.sin(la) * np.cos(ls) * np.cos(cs - lo)
    return (np.degrees(np.arctan2(y, x)) + 360.0) % 360.0


def pase(lat_est, lon_est, altitud_km=550.0, inclinacion_deg=53.0,
         elevacion_min_deg=10.0, raan_deg=None, muestras=4000, fase0=0.0):
    """El pase visto desde una estacion: cuanto dura y cuanto sube.

    Con `raan_deg=None` barre el NODO del plano orbital (grueso y luego fino)
    y se queda con el pase MAS ALTO, el que un espectador reconoceria como
    "el bueno". Devuelve tambien la traza para dibujarla.

    Ojo: el knob es el RAAN, **no la fase**. Desplazar `fase0` recorre la
    MISMA traza desde otro punto de partida (la rotacion terrestre se resta
    desde el instante inicial), asi que no acerca ni aleja el satelite de la
    estacion: se midio y la latitud sobre el meridiano de la estacion no se
    movia ni un grado en 72 fases. Lo que decide si te pasa por encima es
    por donde cruza el ecuador su plano.
    """
    per = periodo_orbital(altitud_km)["segundos"]
    t = np.linspace(0.0, per, int(muestras))
    if raan_deg is not None:
        nodos = [float(raan_deg)]
    else:
        grueso = np.linspace(0.0, 360.0, 72, endpoint=False)
        alturas = []
        for r in grueso:
            ll = _subsat_uno(t, altitud_km, inclinacion_deg, r, fase0)
            _, e = ventana_visibilidad(lat_est, lon_est, ll, altitud_km)
            alturas.append(e.max())
        centro = float(grueso[int(np.argmax(alturas))])
        nodos = list(np.linspace(centro - 5.0, centro + 5.0, 41))
    mejor = None
    for r in nodos:
        lonlat = _subsat_uno(t, altitud_km, inclinacion_deg, r, fase0)
        _, elev = ventana_visibilidad(lat_est, lon_est, lonlat, altitud_km)
        visible = elev >= elevacion_min_deg
        if not visible.any():
            continue
        # segmento contiguo que contiene el maximo
        k = int(np.argmax(elev))
        if not visible[k]:
            continue
        i = k
        while i > 0 and visible[i - 1]:
            i -= 1
        j = k
        while j < len(visible) - 1 and visible[j + 1]:
            j += 1
        cand = {"raan_deg": float(r), "fase0": float(fase0),
                "duracion_s": float(t[j] - t[i]),
                "el_max_deg": float(elev[k]), "t_entrada_s": float(t[i]),
                "t_salida_s": float(t[j]), "t_culminacion_s": float(t[k]),
                "elevacion": elev, "t_s": t, "lonlat": lonlat,
                "indices": (i, j, k)}
        if mejor is None or cand["el_max_deg"] > mejor["el_max_deg"]:
            mejor = cand
    if mejor is None:
        raise ValueError("ningun pase sobre esa estacion con esos parametros")
    mejor["duracion_min"] = mejor["duracion_s"] / 60.0
    mejor["periodo_s"] = float(per)
    mejor["azimut"] = azimut(lat_est, lon_est, mejor["lonlat"])
    mejor["fraccion_del_periodo"] = float(mejor["duracion_s"] / per)
    return mejor


# ── M3 · por eso son muchos ──────────────────────────────────────────────────

def _pesos_area(res_y):
    """Peso de cada FILA del mapa equirrectangular: cos(lat).

    Sin esto, una celda junto al polo pesa lo mismo que una del ecuador y
    cualquier porcentaje de cobertura sale mal. Es la trampa numero uno de
    trabajar sobre un mapa plano.
    """
    lats = np.radians(np.linspace(90.0, -90.0, int(res_y)))
    w = np.cos(lats)
    return w / w.sum()


def fraccion_cubierta(conteo, minimo=1):
    """Fraccion de la SUPERFICIE terrestre con al menos `minimo` satelites."""
    conteo = np.asarray(conteo)
    w = _pesos_area(conteo.shape[0])[:, None]
    cubierto = (conteo >= minimo).astype(np.float64)
    return float((cubierto * w).sum() / (np.ones_like(cubierto) * w).sum())


def cobertura_vs_n(configuraciones, altitud_km=550.0, elevacion_min_deg=10.0,
                   inclinacion_deg=53.0, res=(480, 240), instantes=8):
    """% de la Tierra cubierta por cada constelacion de la lista.

    `configuraciones` = [(planos, sats_por_plano), ...]. Se promedia sobre
    varios instantes de una orbita: una foto sola puede pillar la
    constelacion en su mejor o su peor momento.
    """
    psi = angulo_cobertura(altitud_km, elevacion_min_deg)
    salida = []
    for planos, por_plano in configuraciones:
        fracs = []
        for k in range(int(instantes)):
            lonlat = subsatelites_walker(2, planos, por_plano, inclinacion_deg,
                                         altitud_km, vueltas=0.0,
                                         fase0=k / float(instantes))[0]
            fracs.append(fraccion_cubierta(conteo_cobertura(res, lonlat, psi)))
        salida.append({"n": planos * por_plano, "planos": planos,
                       "por_plano": por_plano,
                       "fraccion": float(np.mean(fracs)),
                       "fraccion_min": float(np.min(fracs)),
                       "fraccion_max": float(np.max(fracs))})
    return salida


def latitud_maxima_cubierta(inclinacion_deg=53.0, altitud_km=550.0,
                            elevacion_min_deg=10.0):
    """Hasta que latitud llega una constelacion inclinada: incl + psi.

    Un satelite a 53 grados nunca pasa por encima de los 53: lo que salva a
    las latitudes altas es su huella. Por encima de esa suma, nada.
    """
    psi = angulo_cobertura(altitud_km, elevacion_min_deg)
    return {"inclinacion_deg": float(inclinacion_deg), "psi_deg": float(psi),
            "lat_max_deg": float(min(90.0, inclinacion_deg + psi)),
            "cubre_polo": bool(inclinacion_deg + psi >= 90.0)}


def relevos(lat_est, lon_est, planos=6, por_plano=11, altitud_km=550.0,
            inclinacion_deg=53.0, elevacion_min_deg=25.0, duracion_s=5400.0,
            muestras=1200):
    """Cuantas veces salta el enlace de un satelite a otro en `duracion_s`.

    Se mira, instante a instante, cual es el satelite MAS ALTO sobre la
    estacion: cada vez que cambia, hay un relevo. Los huecos (ningun
    satelite por encima del minimo) se cuentan aparte y se declaran.
    """
    t = np.linspace(0.0, float(duracion_s), int(muestras))
    per = periodo_orbital(altitud_km)["segundos"]
    n = planos * por_plano
    elevs = np.empty((len(t), n))
    col = 0
    for p in range(planos):
        for j in range(por_plano):
            fase = j / por_plano + p / float(n)
            lonlat = _subsat_uno(t, altitud_km, inclinacion_deg,
                                 360.0 * p / planos, fase)
            _, e = ventana_visibilidad(lat_est, lon_est, lonlat, altitud_km)
            elevs[:, col] = e
            col += 1
    mejor = np.argmax(elevs, axis=1)
    el_max = elevs[np.arange(len(t)), mejor]
    hay = el_max >= elevacion_min_deg
    servidor = np.where(hay, mejor, -1)
    cambios = int(np.sum(servidor[1:] != servidor[:-1]))
    huecos = float(np.mean(~hay))
    return {"n_satelites": n, "relevos": cambios,
            "duracion_s": float(duracion_s),
            "intervalo_medio_s": float(duracion_s / cambios) if cambios else
            float("nan"),
            "fraccion_sin_servicio": huecos,
            "periodo_orbital_s": float(per),
            "elevacion_min_deg": float(elevacion_min_deg),
            "servidor": servidor, "el_max": el_max, "t_s": t}


def _eci_de_lonlat(lonlat, altitud_km):
    """(N,2) lon/lat -> (N,3) km en un marco fijo a la Tierra."""
    lonlat = np.atleast_2d(np.asarray(lonlat, dtype=np.float64))
    r = R_TIERRA_KM + float(altitud_km)
    lo, la = np.radians(lonlat[:, 0]), np.radians(lonlat[:, 1])
    return np.stack([r * np.cos(la) * np.cos(lo),
                     r * np.cos(la) * np.sin(lo),
                     r * np.sin(la)], axis=1)


def _linea_de_vista(p, q, radio_bloqueo):
    """True si el segmento p-q no atraviesa la esfera de `radio_bloqueo`."""
    d = q - p
    dd = float(d @ d)
    if dd == 0.0:
        return True
    s = float(np.clip(-(p @ d) / dd, 0.0, 1.0))       # punto mas cercano al centro
    return bool(np.linalg.norm(p + s * d) >= radio_bloqueo)


def ruta_malla(origen_lonlat, destino_lonlat, lonlat_sats, altitud_km=550.0,
               elevacion_min_deg=25.0, isl_max_km=5000.0):
    """El camino mas corto de un punto del suelo a otro SALTANDO por la malla.

    Grafo: suelo -> satelites visibles (elevacion suficiente) -> satelites
    entre si (si el rayo no roza la atmosfera y el salto cabe en `isl_max_km`)
    -> suelo. Dijkstra sobre distancias reales en km.
    """
    sats = _eci_de_lonlat(lonlat_sats, altitud_km)
    a = _eci_de_lonlat(origen_lonlat, 0.0)[0]
    b = _eci_de_lonlat(destino_lonlat, 0.0)[0]
    n = len(sats)
    bloqueo = R_TIERRA_KM + H_ATMOSFERA_KM

    def visible_desde_suelo(estacion, lonlat_est):
        _, e = ventana_visibilidad(lonlat_est[1], lonlat_est[0],
                                   np.atleast_2d(lonlat_sats), altitud_km)
        return np.where(e >= elevacion_min_deg)[0]

    ini = visible_desde_suelo(a, np.asarray(origen_lonlat, dtype=float))
    fin = visible_desde_suelo(b, np.asarray(destino_lonlat, dtype=float))
    if len(ini) == 0 or len(fin) == 0:
        raise ValueError("el origen o el destino no ven ningun satelite")

    INF = float("inf")
    dist = np.full(n + 2, INF)          # n = origen, n+1 = destino
    prev = np.full(n + 2, -1, dtype=int)
    dist[n] = 0.0
    for k in ini:
        d = float(np.linalg.norm(sats[k] - a))
        if d < dist[k]:
            dist[k], prev[k] = d, n
    visto = np.zeros(n + 2, dtype=bool)
    visto[n] = True
    fin_set = set(int(k) for k in fin)
    for _ in range(n + 1):
        cand = np.where(~visto & np.isfinite(dist))[0]
        if len(cand) == 0:
            break
        u = int(cand[np.argmin(dist[cand])])
        visto[u] = True
        if u == n + 1:
            break
        if u < n:
            if u in fin_set:
                d = dist[u] + float(np.linalg.norm(b - sats[u]))
                if d < dist[n + 1]:
                    dist[n + 1], prev[n + 1] = d, u
            for v in range(n):
                if visto[v] or v == u:
                    continue
                salto = float(np.linalg.norm(sats[v] - sats[u]))
                if salto > isl_max_km:
                    continue
                if not _linea_de_vista(sats[u], sats[v], bloqueo):
                    continue
                if dist[u] + salto < dist[v]:
                    dist[v], prev[v] = dist[u] + salto, u
    if not np.isfinite(dist[n + 1]):
        raise ValueError("la malla no conecta origen y destino")
    camino = []
    k = n + 1
    while k != n:
        camino.append(k)
        k = int(prev[k])
    camino = list(reversed(camino))[:-1]        # indices de satelite del camino
    km = float(dist[n + 1])
    return {"saltos": len(camino) + 1, "satelites": camino, "km": km,
            "latencia_ms": float(km / C_LUZ_KM_S * 1000.0),
            "puntos_eci": np.array([a] + [sats[k] for k in camino] + [b]),
            "lonlat_saltos": np.atleast_2d(lonlat_sats)[camino]}


def gran_circulo_km(origen_lonlat, destino_lonlat):
    """Distancia sobre la superficie entre dos puntos (haversine)."""
    lo1, la1 = np.radians(origen_lonlat)
    lo2, la2 = np.radians(destino_lonlat)
    h = (np.sin((la2 - la1) / 2) ** 2
         + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2)
    return float(2 * R_TIERRA_KM * np.arcsin(np.sqrt(h)))


def latencia_fibra(origen_lonlat, destino_lonlat, rodeo=1.4,
                   fraccion_c=2.0 / 3.0):
    """Latencia por fibra: el cable no va en linea recta y la luz va lenta.

    `rodeo` (el cable mide mas que el gran circulo) y `fraccion_c` (indice
    de refraccion ~1.47) son SUPUESTOS de ingenieria, no medidas: quien use
    esta cifra en pantalla tiene que declararlos.
    """
    gc = gran_circulo_km(origen_lonlat, destino_lonlat)
    km = gc * float(rodeo)
    return {"gran_circulo_km": gc, "km": float(km), "rodeo": float(rodeo),
            "fraccion_c": float(fraccion_c),
            "latencia_ms": float(km / (C_LUZ_KM_S * fraccion_c) * 1000.0)}


def fspl_db(d_km, f_ghz):
    """Perdida de camino en espacio libre (dB). Misma formula que enlace.py."""
    return float(92.45 + 20.0 * np.log10(float(d_km))
                 + 20.0 * np.log10(float(f_ghz)))


# ── M4 · la red que se gobierna sola ─────────────────────────────────────────

def tiempo_sobre_mar(planos=6, por_plano=11, altitud_km=550.0,
                     inclinacion_deg=53.0, instantes=64, res=(480, 240)):
    """Que fraccion del tiempo-satelite se pasa el enjambre sobre el agua.

    Se cuenta con la mascara de continentes de esta misma libreria (poligonos
    propios, no datos externos), muestreando el punto subsatelital de todos
    los satelites en varios instantes de una orbita.
    """
    mask = mascara_tierra(res)
    res_y, res_x = mask.shape
    total = 0
    en_tierra = 0
    for k in range(int(instantes)):
        lonlat = subsatelites_walker(2, planos, por_plano, inclinacion_deg,
                                     altitud_km, vueltas=0.0,
                                     fase0=k / float(instantes))[0]
        ix = np.clip(((lonlat[:, 0] + 180.0) / 360.0 * (res_x - 1)).astype(int),
                     0, res_x - 1)
        iy = np.clip(((90.0 - lonlat[:, 1]) / 180.0 * (res_y - 1)).astype(int),
                     0, res_y - 1)
        en_tierra += int(mask[iy, ix].sum())
        total += len(lonlat)
    return {"muestras": total, "sobre_tierra": en_tierra,
            "fraccion_mar": float(1.0 - en_tierra / total),
            "fraccion_tierra": float(en_tierra / total)}


def demanda_por_celda(res=(96, 48), semilla=11, focos=9, fondo=0.04):
    """Mapa de demanda SINTETICO (declarado): nucleos de trafico sobre tierra.

    NO es un dato real de mercado. Se construye con semilla fija colocando
    focos gaussianos sobre celdas de tierra firme de la mascara propia. Lo
    que el curso mide con esto no es "cuanta demanda hay" sino **cuanto
    mejora** un asignador frente a otro sobre la MISMA demanda.
    """
    rng = np.random.default_rng(int(semilla))
    mask = mascara_tierra(res)
    res_y, res_x = mask.shape
    d = np.full((res_y, res_x), float(fondo))
    tierra = np.argwhere(mask)
    if len(tierra) == 0:
        return d
    elegidos = tierra[rng.choice(len(tierra), size=int(focos), replace=False)]
    yy, xx = np.mgrid[0:res_y, 0:res_x]
    for (cy, cx) in elegidos:
        sigma = 2.0 + 4.0 * rng.random()
        peso = 0.5 + rng.random()
        d += peso * np.exp(-0.5 * (((yy - cy) / sigma) ** 2
                                   + ((xx - cx) / sigma) ** 2))
    d *= _pesos_area(res_y)[:, None] * res_y      # celdas polares pesan menos
    return d / d.max()


def asignar_haces(conteo, demanda, n_haces, modo="fijo", semilla=5,
                  pasos=400):
    """Reparte `n_haces` haces por satelite entre las celdas que ve.

    - `fijo`: los haces apuntan a celdas repartidas por igual (rejilla), sin
      mirar la demanda. Es lo que hace un satelite de haces fijos.
    - `demanda`: apunta a las celdas de mas demanda que tenga a la vista.
    - `aprendido`: parte del reparto ciego y va moviendo haces a la celda
      vecina que mas sube la demanda servida (ascenso por coordenadas con
      semilla fija). Devuelve ademas la curva de mejora, MEDIDA.

    La cifra que devuelve es demanda servida (0..1 del total posible).
    """
    conteo = np.asarray(conteo)
    demanda = np.asarray(demanda, dtype=np.float64)
    if conteo.shape != demanda.shape:
        raise ValueError(f"conteo {conteo.shape} y demanda {demanda.shape} "
                         "tienen que ser del mismo tamaño")
    visible = conteo > 0
    capacidad = int(n_haces) * int(conteo.max()) if conteo.max() else 0
    total = float(demanda.sum())
    celdas = np.argwhere(visible)
    if len(celdas) == 0 or capacidad == 0:
        return {"servida": 0.0, "curva": np.array([0.0])}
    valor = demanda[visible]
    orden = np.argsort(valor)[::-1]
    k = min(capacidad, len(celdas))

    if modo == "demanda":
        servida = float(valor[orden[:k]].sum())
        return {"servida": servida / total, "haces": k, "capacidad": capacidad,
                "curva": np.array([servida / total])}

    rng = np.random.default_rng(int(semilla))
    elegidas = rng.choice(len(celdas), size=k, replace=False)
    servida = float(valor[elegidas].sum())
    curva = [servida / total]
    if modo == "fijo":
        return {"servida": servida / total, "haces": k,
                "capacidad": capacidad, "curva": np.array(curva)}
    if modo != "aprendido":
        raise ValueError(f"modo desconocido: {modo}")

    dentro = set(int(i) for i in elegidas)
    fuera = [i for i in range(len(celdas)) if i not in dentro]
    for _ in range(int(pasos)):
        if not fuera:
            break
        peor = min(dentro, key=lambda i: valor[i])
        mejor = max(fuera, key=lambda i: valor[i])
        if valor[mejor] <= valor[peor]:
            break
        dentro.remove(peor)
        fuera.remove(mejor)
        fuera.append(peor)
        dentro.add(mejor)
        curva.append(float(valor[list(dentro)].sum()) / total)
    return {"servida": curva[-1], "haces": k, "capacidad": capacidad,
            "curva": np.array(curva), "pasos": len(curva) - 1}


def sobre_el_horizonte(lat_est, lon_est, planos=24, por_plano=10,
                       altitud_km=550.0, inclinacion_deg=53.0,
                       elevacion_min_deg=10.0, fase0=0.0):
    """Cuantos satelites del enjambre estan AHORA sobre tu horizonte.

    Devuelve tambien sus elevaciones y azimuts, para dibujar el cielo del
    patio en una vista polar.
    """
    lonlat = subsatelites_walker(2, planos, por_plano, inclinacion_deg,
                                 altitud_km, vueltas=0.0, fase0=fase0)[0]
    _, elev = ventana_visibilidad(lat_est, lon_est, lonlat, altitud_km)
    arriba = elev >= float(elevacion_min_deg)
    la, lo = np.radians(lat_est), np.radians(lon_est)
    ls, cs = np.radians(lonlat[:, 1]), np.radians(lonlat[:, 0])
    y = np.sin(cs - lo) * np.cos(ls)
    x = np.cos(la) * np.sin(ls) - np.sin(la) * np.cos(ls) * np.cos(cs - lo)
    azim = (np.degrees(np.arctan2(y, x)) + 360.0) % 360.0
    return {"n_total": int(len(lonlat)), "n_visibles": int(arriba.sum()),
            "elevaciones": elev[arriba], "azimuts": azim[arriba],
            "lonlat": lonlat[arriba], "indices": np.where(arriba)[0],
            "elevacion_min_deg": float(elevacion_min_deg)}

"""Estilo de los reels de divulgación: fondo MÍNIMO y tema intercambiable.

El dueño (2026-10-06) pidió limpiar el fondo de los reels: las órbitas gigantes y el satélite de `fondo_reel`
competían con el diagrama y «se perdía la información». Aquí el fondo es el color del tema y, en los temas
oscuros, unas pocas estrellas tenues que titilan con ciclos enteros por periodo (loop perfecto). Nada más.

Cada reel toma un tema del registro de las presentaciones (animaciones/temas_espaciales.py): paleta y
tipografías de título y cuerpo. `REEL_TEMA=<id>` en el entorno fuerza otro tema para experimentar.

    est = Estilo.de("marte")
    fondo_minimo(escena, est, T)
    cabecera(escena, est, reloj, "Kicker", "Título\\nen dos líneas")
    leyenda(escena, est, reloj, "Frase", "línea técnica", t0, t1, y)
"""
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import DOWN, RIGHT, UP, Dot, RoundedRectangle, Text, VGroup, VMobject, config, interpolate_color, ManimColor

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "animaciones"))

from marca_aerospace import LogoCoDe
from reels_promo import ventana_texto

_SUPER = 4


@dataclass
class Estilo:
    id: str
    fondo: str
    tinta: str
    tenue: str
    acento: str
    acento2: str
    calido: str
    claro: bool
    f_titulo: str
    f_cuerpo: str
    f_cifra: str

    @classmethod
    def de(cls, tema):
        import temas_espaciales as TE
        tema = os.environ.get("REEL_TEMA") or tema
        t = TE.TEMAS[tema]
        c = t.color
        fondo = (t.manim or {}).get("FONDO") or c["panel"]
        r, g, b = (int(fondo.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
        claro = 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.5
        return cls(tema, fondo, c["tinta"], c["tenue"], c["acento"], c["acento2"], c["calido"], claro,
                   t.fuentes["titulo"], t.fuentes["cuerpo"], t.fuentes.get("display") or t.fuentes["titulo"])

    def mezcla(self, a, b, f):
        return interpolate_color(ManimColor(a), ManimColor(b), f)

    AZUL_TIERRA = "#3B8FD9"                 # la Tierra es azul en todos los temas (con acento cálido salía café)

    @property
    def tierra(self):
        return self.mezcla(self.fondo, self.AZUL_TIERRA, 0.20 if not self.claro else 0.12)

    @property
    def tierra_borde(self):
        return self.mezcla(self.fondo, self.AZUL_TIERRA, 0.65)

    @property
    def linea(self):
        return self.mezcla(self.fondo, self.tenue, 0.45)


def texto(est, s, tam, color=None, rol="cuerpo", peso="MEDIUM", ancho_max=None, tracking=0.0):
    """Text del tema a 4× y reducido, con el lienzo de Pango ancho (si no, Manim parte la línea)."""
    fuente = {"titulo": est.f_titulo, "cuerpo": est.f_cuerpo, "cifra": est.f_cifra}[rol]
    ancho = config.pixel_width
    config.pixel_width = 20000
    try:
        t = Text(s, font=fuente, weight=peso, font_size=tam * _SUPER, color=color or est.tinta)
    finally:
        config.pixel_width = ancho
    if tracking:
        paso = tracking * t.height / 0.72 if t.height else 0
        glifos = iter(t.submobjects)
        for i, ch in enumerate(s):
            if ch.isspace():
                continue
            g = next(glifos, None)
            if g is None:
                break
            g.shift(RIGHT * paso * i)
    t.scale(1 / _SUPER)
    if ancho_max and t.width > ancho_max:
        t.scale_to_fit_width(ancho_max)
    return t


def lineas(est, s, tam, color=None, rol="cuerpo", peso="MEDIUM", ancho_max=12.8):
    g = VGroup(*[texto(est, l, tam, color, rol, peso, ancho_max) for l in s.split("\n")])
    g.arrange(DOWN, buff=tam * 0.006)
    if g.width > ancho_max:
        g.scale_to_fit_width(ancho_max)
    return g


def fondo_minimo(escena, est, T, n=46, semilla=11):
    """Color del tema + (solo en oscuros) n estrellas chicas y tenues, periódicas en T."""
    escena.camera.background_color = est.fondo
    if est.claro:
        return VGroup()
    W, H = escena.camera.frame_width, escena.camera.frame_height
    rng = np.random.default_rng(semilla)
    estrellas = []
    for _ in range(n):
        d = Dot([rng.uniform(-W / 2, W / 2), rng.uniform(-H / 2, H / 2), 0], radius=rng.choice([0.014, 0.02, 0.028], p=[.5, .35, .15]),
                color=est.tenue)
        estrellas.append((d, rng.uniform(0.12, 0.38), rng.uniform(0, 6.28), 2 * np.pi * rng.integers(1, 3) / T))
    grupo = VGroup(*[e[0] for e in estrellas]).set_z_index(-10)
    reloj = [0.0]

    def titilar(_m, dt):
        reloj[0] += dt
        for d, base, fase, vel in estrellas:
            d.set_fill(opacity=base * (0.65 + 0.35 * np.sin(vel * reloj[0] + fase)))
    grupo.add_updater(titilar)
    titilar(grupo, 0)
    escena.add(grupo)
    return grupo


def cabecera(escena, est, kicker, titulo, tam=86):
    """Emblema + kicker en acento y título del tema. Fijo: no rota (es la portada del loop)."""
    W = escena.camera.frame_width
    emblema = LogoCoDe(altura=1.05, aerospace=False, contorno=True, color=est.tinta if est.claro else "plata")
    emblema.move_to([-W / 2 + 1.0, 9.5, 0])
    k = texto(est, kicker.upper(), 28, est.acento, "cuerpo", "MEDIUM", W * 0.72, tracking=0.18)
    k.next_to(emblema, RIGHT, buff=0.32)
    t = lineas(est, titulo, tam, est.tinta, "titulo", "SEMIBOLD", W * 0.88)
    t.move_to([0, 0, 0])
    t.shift(UP * (8.75 - t.get_top()[1]))                  # el título cuelga de y = 8.75: deja el resto del cuadro al diagrama
    g = VGroup(emblema, k, t).set_z_index(20)
    escena.add(g)
    return g


def chip(est, s, color=None, tam=24):
    color = color or est.calido
    t = texto(est, s, tam, color, "cuerpo", "MEDIUM")
    caja = RoundedRectangle(corner_radius=0.22, width=t.width + 0.7, height=t.height + 0.42, stroke_width=2.2,
                            stroke_color=color, fill_color=est.fondo, fill_opacity=0.9)
    t.move_to(caja)
    return VGroup(caja, t).set_z_index(30)


def chip_arriba(escena, est, s, color=None):
    W = escena.camera.frame_width
    c = chip(est, s, color, 22)
    c.move_to([W / 2 - c.width / 2 - 0.45, 5.85, 0])
    escena.add(c)
    return c


def leyenda(escena, est, reloj, grande, pequena, t0, t1, y=-7.1, f=0.5):
    W = escena.camera.frame_width
    g = lineas(est, grande, 56, est.tinta, "titulo", "SEMIBOLD", W * 0.9)
    p = lineas(est, pequena, 32, est.acento, "cuerpo", "MEDIUM", W * 0.9)
    grupo = VGroup(g, p).arrange(DOWN, buff=0.3).move_to([0, y, 0]).set_z_index(25)
    base = grupo.get_center().copy()

    def actualizar(m):
        o = ventana_texto(reloj.t, t0, t1, f, 1e9)
        m.set_opacity(o)
        m.move_to(base + UP * 0.35 * (1 - o))
    grupo.add_updater(actualizar)
    actualizar(grupo)
    escena.add(grupo)
    return grupo


class Viva(VGroup):
    """Texto que cambia por cuadro, con caché por cadena."""

    def __init__(self, est, f_texto, pos, tam=40, color=None, rol="cifra", peso="SEMIBOLD", f_op=None, z=12):
        super().__init__()
        cache, ultimo = {}, [None, None]

        def act(m):
            s = f_texto()
            p = pos() if callable(pos) else pos
            if s not in cache:
                cache[s] = texto(est, s, tam, color or est.tinta, rol, peso)
            clave = (s, tuple(np.round(p, 3)))
            if ultimo[0] != clave:                                   # copiar un Text es caro: solo si cambió
                ultimo[0] = clave
                ultimo[1] = cache[s].copy().move_to(p)
                m.become(VGroup(ultimo[1])).set_z_index(z)
            if f_op:
                m.set_opacity(f_op())
        self.add_updater(act)
        act(self)


# ── Bordes (2026-10-06, ronda 3): entorno de las presentaciones en las franjas libres + marco geométrico ──
# El diagrama ocupa la zona central (y ∈ [Y_BAJO, Y_ALTO]); arriba y abajo quedan franjas que Instagram tapa en
# parte con su interfaz. Ahí se ve el entorno del tema (el mismo de las diapositivas y del logo en entornos),
# y la zona central se funde hacia el color del tema para que la información no compita con el fondo.

Y_ALTO, Y_BAJO = 9.05, -7.75          # bordes del marco (unidades de escena; el cuadro mide 14.22 × 25.28)
_CACHE_BORDES = Path(__file__).resolve().parents[3] / "exports" / "estudio" / "_fondos" / "reels_bordes"


def _imagen_bordes(est, var, oscuro_centro=0.88, piso=0.18, rampa=1.7):
    from PIL import Image
    import fondos_a_medida as FM
    _CACHE_BORDES.mkdir(parents=True, exist_ok=True)
    ruta = _CACHE_BORDES / f"{est.id}_{var}_{int(oscuro_centro * 100)}_{int(piso * 100)}.png"
    if ruta.exists():
        return ruta
    img = np.asarray(Image.open(FM.fondo_a_medida(est.id, "portada", var, 1080, 1920)).convert("RGB")).astype(float)
    H = img.shape[0]
    y = 12.64 - (np.arange(H) + 0.5) / H * 25.28                       # fila → unidades de escena
    dentro = np.clip(np.minimum((Y_ALTO - y) / rampa + 1, (y - Y_BAJO) / rampa + 1), 0, 1)
    dentro = dentro * dentro * (3 - 2 * dentro)
    a = (piso + (oscuro_centro - piso) * dentro)[:, None, None]
    base = np.array([int(est.fondo.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], float)
    out = img * (1 - a) + base * a
    tmp = ruta.with_suffix(f".{os.getpid()}.tmp.png")                  # escritura atómica: varios renders a la vez
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(tmp)
    tmp.replace(ruta)
    return ruta


def fondo_bordes(escena, est, T, var=0):
    """Entorno del tema visible en las franjas de arriba y abajo, fundido en el centro, + marco geométrico."""
    from manim import ImageMobject, Line
    escena.camera.background_color = est.fondo
    W, H = escena.camera.frame_width, escena.camera.frame_height
    im = ImageMobject(str(_imagen_bordes(est, var))).set_z_index(-20)
    im.stretch_to_fit_width(W).stretch_to_fit_height(H)
    escena.add(im)
    escena.add(marco_geometrico(escena, est))
    return im


def marco_geometrico(escena, est, op=0.55):
    """Escuadras en las esquinas de la zona de contenido y reglas finas en los costados (tipo instrumento)."""
    from manim import Line
    W = escena.camera.frame_width
    x = W / 2 - 0.42
    g = VGroup()
    brazo = 0.75
    for sx in (-1, 1):
        for y0, sy in ((Y_ALTO, -1), (Y_BAJO, 1)):
            esquina = np.array([sx * x, y0, 0])
            g.add(Line(esquina, esquina + np.array([-sx * brazo, 0, 0]), stroke_width=2.6, color=est.acento).set_opacity(op))
            g.add(Line(esquina, esquina + np.array([0, sy * brazo, 0]), stroke_width=2.6, color=est.acento).set_opacity(op))
        for k, yy in enumerate(np.arange(Y_BAJO + 1.2, Y_ALTO - 1.1, 0.4)):  # regla: marca larga cada 2 unidades
            largo = 0.2 if k % 5 == 0 else 0.09
            g.add(Line([sx * x, yy, 0], [sx * (x - largo), yy, 0], stroke_width=1.6, color=est.tenue).set_opacity(0.32 if k % 5 == 0 else 0.2))
    sitio = texto(est, "CODEAEROSPACE.COM", 20, est.tenue, "cuerpo", "MEDIUM", tracking=0.3).set_opacity(0.7)
    sitio.move_to([0, Y_BAJO, 0])
    g.add(sitio)
    return g.set_z_index(-5)


# ── Ronda 4 (2026-10-06): estrellas en capas + tema Órbita, SIN marco de esquinas ───────────────────────
# El dueño: las esquinas «agregan ruido», prefería el fondo con estrellas, el tema orbital y que la animación use
# TODO el cuadro. Tres capas de estrellas (lejanas, medias, cercanas con destello) que titilan con ciclos enteros por
# periodo y se mueven apenas (paralaje senoidal): loop perfecto. Debajo, el entorno Órbita de las presentaciones, tenue.
ZONA_Y1, ZONA_Y0 = 5.2, -5.6           # zona útil del diagrama (el título cuelga de 8.75 y la leyenda va hacia −7.1)


def fondo_orbital(escena, est, T, var=0, semilla=7, tiempo=None, centro=0.74, fondo=None):
    """`fondo="reel"`: fondo vertical compuesto para el reel (fondos_reel.py), SIN atenuar el centro."""
    from manim import ImageMobject, Line
    escena.camera.background_color = est.fondo
    W, H = escena.camera.frame_width, escena.camera.frame_height
    if fondo == "reel":
        import fondos_reel as FR
        ruta = FR.fondo_reel(est.id, var, "cuerpo")
    else:
        ruta = _imagen_bordes(est, var, centro, 0.10)
    im = ImageMobject(str(ruta)).set_z_index(-20)
    im.stretch_to_fit_width(W).stretch_to_fit_height(H)
    escena.add(im)
    rng = np.random.default_rng(semilla + var)
    capas = ((120, (0.010, 0.016), (0.10, 0.28), 0.10, 1), (46, (0.018, 0.028), (0.22, 0.50), 0.26, 2), (14, (0.032, 0.048), (0.40, 0.75), 0.55, 3))
    estrellas = []
    for n, (r0, r1), (o0, o1), amp, ciclos in capas:
        for _ in range(n):
            col = est.acento if rng.random() < 0.14 else est.tinta
            d = Dot([rng.uniform(-W / 2, W / 2), rng.uniform(-7.4 if fondo == "reel" else -H / 2, H / 2), 0], radius=rng.uniform(r0, r1), color=col)
            estrellas.append([d, d.get_center().copy(), rng.uniform(o0, o1), rng.uniform(0, 6.28), int(rng.integers(1, 3)) * ciclos, amp, rng.uniform(0, 6.28)])
    grupo = VGroup(*[e[0] for e in estrellas]).set_z_index(-10)
    destellos = []
    for e in estrellas[-14:-4]:                                          # 10 estrellas cercanas con destello en cruz
        for ang in (0, 90):
            ln = Line([-0.2, 0, 0], [0.2, 0, 0], stroke_width=1.6, color=est.tinta).rotate(np.deg2rad(ang))
            destellos.append((ln, e))
    gl = VGroup(*[d[0] for d in destellos]).set_z_index(-9)
    reloj = [0.0]

    def titilar(_m, dt):
        reloj[0] += dt
        f = 2 * np.pi * (tiempo() if tiempo else reloj[0]) / T
        for d, c0, base, fase, k, amp, fx in estrellas:
            d.set_fill(opacity=base * (0.62 + 0.38 * np.sin(k * f + fase)))
            d.move_to(c0 + RIGHT * amp * np.sin(f + fx) * 0.45)          # paralaje: la capa cercana se mueve más
        for ln, e in destellos:
            o = max(0.0, np.sin(e[4] * f + e[3])) ** 6
            ln.move_to(e[0].get_center()).set_stroke(opacity=0.8 * o)
    grupo.add_updater(titilar)
    titilar(grupo, 0)
    escena.add(grupo, gl)
    return grupo


# ══ Ronda 5 (2026-10-07): película con título → cuerpo → cierre con logo → disolución al inicio ═════════════════════════
import divulgacion_fisica as _F


def _suave(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


class Pelicula:
    """Reloj de un reel con cierre. `v` = tiempo del video; `t` = reloj del CUERPO (0 durante el título y bajo el logo).

    Al final el logo se disuelve en el título del inicio: el último cuadro es igual al primero (loop sin corte) y la
    animación vuelve a empezar justo después de que se pueda leer el título.
    """

    def __init__(self, escena, cuerpo):
        self.TB = cuerpo
        self.a = _F.H0 + cuerpo                      # aquí empieza el cierre
        self.V = self.a + _F.LOGO_TOTAL
        self.T = 1e9                                 # compatibilidad: las leyendas ya no son periódicas
        self._escena = escena

    @property
    def v(self):
        """Tiempo del video = cuadros escritos / fps (acumular dt pierde un cuadro en cada play/wait)."""
        return self._escena.renderer.time

    @property
    def t(self):
        if self.v < _F.H0 or self.v >= self.a + _F.LOGO_FADE_IN:
            return 0.0
        return self.v - _F.H0

    @property
    def opacidad_logo(self):
        """Opacidad del fondo Órbita del cierre: aparece en LOGO_FADE_IN y se disuelve en LOGO_FADE_OUT."""
        a, v = self.a, self.v
        sube = _suave((v - a) / _F.LOGO_FADE_IN)
        baja = 1 - _suave((v - (self.V - _F.LOGO_FADE_OUT - 0.1)) / _F.LOGO_FADE_OUT)           # llega a 0 un poco antes del final
        return min(sube, baja)

    @property
    def opacidad_marca(self):
        """Opacidad del logo ya dibujado y del sitio: se apagan con la disolución final."""
        return 1 - _suave((self.v - (self.V - _F.LOGO_FADE_OUT - 0.1)) / _F.LOGO_FADE_OUT)


def cierre_logo(escena, est, pel, var=0, tema=None, fondo=None):
    """Cierre del reel: el logo de Co.De se traza sobre el entorno Órbita de las presentaciones y se disuelve en el título.
    Llamar al final de construct(), tras `escena.wait(H0 + TB)`."""
    from manim import Circle, ImageMobject
    from fondos_a_medida import fondo_a_medida
    from marca_aerospace import LogoCoDe, animar_entrada
    W, H = escena.camera.frame_width, escena.camera.frame_height
    if fondo == "reel":
        import fondos_reel as FR
        img = ImageMobject(str(FR.fondo_reel(tema, var, "cierre")))
    else:
        img = ImageMobject(str(fondo_a_medida(tema or "orbita", "portada", var, 1080, 1920)))
    img.stretch_to_fit_width(W).stretch_to_fit_height(H)
    base = img.copy()
    img.set_z_index(100)

    def fondo_vivo(m):
        k = 1.0 + 0.04 * min(max(pel.v - pel.a, 0) / 5.0, 1.0)             # el fondo «respira»
        m.become(base.copy().scale(k).set_z_index(100))
        m.set_opacity(pel.opacidad_logo)
    img.add_updater(fondo_vivo)
    halo = VGroup(*[Circle(radius=r).set_stroke(width=0).set_fill(est.fondo, 0.07) for r in np.linspace(3.2, 7.4, 10)])
    halo.move_to([0, 1.6, 0]).set_z_index(101)
    halo.add_updater(lambda m: [c.set_fill(est.fondo, 0.07 * pel.opacidad_logo) for c in m])
    sitio = texto(est, "codeaerospace.com", 48, est.acento, "cuerpo", "MEDIUM", ancho_max=W * 0.8, tracking=0.08).move_to([0, -5.0, 0])
    sitio.set_z_index(103)
    sitio.add_updater(lambda m: m.set_opacity(_suave((pel.v - (pel.a + 2.6)) / 0.6) * pel.opacidad_marca))
    escena.add(img, halo, sitio)
    logo = LogoCoDe(altura=W * 0.86 / 1.05, color="plata").mover_a(UP * 1.6)
    logo.set_z_index(102)
    logo.orbitas_contorno.set_z_index(102)                                  # el contorno final no es hijo hasta el cambio
    escena.wait(_F.LOGO_RETRASO)                                            # el fondo Órbita ya cubre antes de trazar el logo
    animar_entrada(escena, logo, estilo="trazo", acento=est.acento)          # LOGO_ANIM = 2.6 s
    logo.add_updater(lambda m: m.set_opacity(pel.opacidad_marca))
    escena.wait(_F.LOGO_HOLD + _F.LOGO_FADE_OUT - _F.LOGO_RETRASO)


# ══ Helpers compartidos por las series de reels (copiados de 37-reels-divulgacion.py) ═════════════════════════════════
def punto(color, r=0.12):
    from manim import Dot
    return VGroup(Dot(radius=r * 2.6, color=color).set_opacity(0.16), Dot(radius=r, color=color)).set_z_index(9)


def miles(x):
    return f"{x:,.0f}".replace(",", " ")


def cola(escena, objeto, color, n=26, ancho=6.0, z=8, salto=2.5):
    """Estela de cometa detrás de `objeto` (un `punto`); se borra si el objeto salta (el reloj se reinicia bajo el logo)."""
    from manim import Line, ORIGIN, RIGHT
    hist = []
    tramos = VGroup(*[Line(ORIGIN, RIGHT * 0.01) for _ in range(n)]).set_z_index(z)

    def actualizar(m):
        c = objeto.get_center().copy()
        if hist and np.linalg.norm(c - hist[-1]) > salto:
            hist.clear()
        if not hist or np.linalg.norm(c - hist[-1]) > 1e-3:
            hist.append(c)
        del hist[:-n - 1]
        vivo = objeto[1].get_fill_opacity()
        for i, ln in enumerate(m):
            j = len(hist) - n + i
            if j < 1 or j >= len(hist):
                ln.set_stroke(opacity=0)
                continue
            f = (i + 1) / n
            ln.put_start_and_end_on(hist[j - 1], hist[j])
            ln.set_stroke(color=color, width=ancho * f, opacity=0.65 * f ** 1.6 * vivo)
    tramos.add_updater(actualizar)
    escena.add(tramos)
    return tramos


def preparar_serie(escena, tb, kicker, titulo, var=0, tema="orbita", chip_txt="Simulación · ROS 2", centro=0.74, fondo=None):
    """Fondo del tema + estrellas + cabecera + chip de aclaración (por omisión «Simulación · ROS 2», serie Estación ATP)."""
    est = Estilo.de(tema)
    pel = Pelicula(escena, tb)
    fondo_orbital(escena, est, pel.V, var, tiempo=lambda: pel.v, centro=centro, fondo=fondo)
    est.fondo_reel = fondo
    cabecera(escena, est, kicker, titulo)
    if chip_txt:
        chip_arriba(escena, est, chip_txt, est.calido)
    return est, pel


def cerrar_serie(escena, est, pel, var=0):
    """Cierre con el logo sobre el entorno del MISMO tema del reel (Órbita en ATP, Espectro en Triage)."""
    escena.wait(_F.H0 + pel.TB)
    cierre_logo(escena, est, pel, var, tema=est.id, fondo=getattr(est, "fondo_reel", None))

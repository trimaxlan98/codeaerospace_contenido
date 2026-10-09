import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *

import datos_em as DE
from estilo_reel import Viva, cerrar_serie, cola, leyenda, punto, preparar_serie, texto
from reels_promo import polilinea, suave

# SERIE «ELECTROMAGNETISMO EN EL ESPACIO» — física de base (campos, ondas, antenas, plasma) aplicada a sistemas espaciales.
# Divulgación con cálculos de electromagnetismo.py (supuestos en datos_em.py y en el ⚠️ de los pies); no hay mediciones propias.
# Tema ELECTROMAGNETISMO con fondo vertical propio (fondos_reel.electromagnetismo: limbo de la Tierra, aurora y líneas de campo).
# Formato película: título → cuerpo → logo → loop. Pocas cifras, cada una con una comparación cotidiana.

FIN = 3.0
KICKER = "Electromagnetismo"
SERIE = dict(tema="electromagnetismo", fondo="reel")
VERDE, ROJO, VIOLETA, AZUL = "#3DFF9A", "#FF5A6E", "#B07CFF", "#3B8FD9"


def leyendas(escena, est, pel, nombre, textos):
    ts = list(DE.LEYENDAS[nombre]) + [DE.CUERPO[nombre] + FIN]
    for (g, p), a, b in zip(textos, ts[:-1], ts[1:]):
        leyenda(escena, est, pel, g, p, a, b)


def rampa(t, a, d=0.6):
    return suave((t - a) / d)


def fundir(m, k):
    """set_opacity(k) relativo al relleno y trazo originales (no vuelve opacos los rellenos transparentes)."""
    if not hasattr(m, "_base_op"):
        m._base_op = [(x, x.get_fill_opacity(), x.get_stroke_opacity()) for x in m.get_family() if isinstance(x, VMobject)]
    for x, f, s_ in m._base_op:
        x.set_fill(opacity=f * k, family=False).set_stroke(opacity=s_ * k, family=False)
    return m


def aparece(m, pel, t0, d=0.6, hasta=None):
    m.add_updater(lambda x: fundir(x, rampa(pel.t, t0, d) * ((1 - rampa(pel.t, hasta, d)) if hasta else 1)))
    fundir(m, 0)
    return m


def tierra(est, c, r):
    return VGroup(Circle(radius=r * 1.06).set_fill(AZUL, 0.18).set_stroke(width=0),
                  Circle(radius=r).set_fill(est.mezcla(est.fondo, AZUL, 0.75), 1).set_stroke("#8FD8FF", 3)).move_to(c).set_z_index(8)


def linea_dipolo(c, L, r_tierra, lado=1, eje=UP, n=120):
    """Línea del campo dipolar r = L·sen²θ (en radios terrestres) desde la superficie hasta la superficie."""
    th0 = np.arcsin(np.sqrt(1.0 / L))
    th = np.linspace(th0, np.pi - th0, n)
    r = L * np.sin(th) ** 2 * r_tierra
    if np.allclose(eje, UP):
        pts = np.stack([lado * r * np.sin(th), r * np.cos(th), 0 * th], 1)
    else:                                                     # eje horizontal (el norte a la derecha)
        pts = np.stack([r * np.cos(th), lado * r * np.sin(th), 0 * th], 1)
    return pts + np.asarray(c)


def recorrer(pts, u):
    """Punto a la fracción u ∈ [0, 1] de la longitud de la polilínea."""
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    x = float(np.clip(u, 0, 1)) * s[-1]
    i = int(np.clip(np.searchsorted(s, x) - 1, 0, len(seg) - 1))
    f = (x - s[i]) / max(seg[i], 1e-9)
    return pts[i] * (1 - f) + pts[i + 1] * f


def sen(t):
    return float(np.sin(t))


# ══ 1 · La Tierra es un imán (escudo) ═══════════════════════════════════════════════════════════════════════════════════

class ReelEMEscudo(Scene):
    VAR = 0

    def construct(self):
        n = "ReelEMEscudo"; TB = DE.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "La Tierra es\nun imán gigante", self.VAR, chip_txt="Ilustración", **SERIE)
        C, RT = np.array([1.4, 0.3, 0]), 1.15
        self.add(aparece(tierra(est, C, RT), pel, 0.2))
        for k, L in enumerate((1.6, 2.2, 2.9, 3.8)):
            for lado in (-1, 1):
                ln = polilinea(linea_dipolo(C, L, RT, lado), color=est.acento, width=4, opacity=0.85 - 0.12 * k).set_z_index(5)
                self.add(aparece(ln, pel, 0.6 + 0.5 * k, 0.8))
        self.add(aparece(VGroup(texto(est, "N", 40, est.tinta, "titulo", "BOLD").move_to(C + UP * (RT + 0.45)),
                                texto(est, "S", 40, est.tinta, "titulo", "BOLD").move_to(C + DOWN * (RT + 0.45))).set_z_index(9), pel, 1.0))
        # viento solar: flujo alrededor de un obstáculo (cilindro de radio A): ψ = y (1 − A²/r²)
        A = 4.9
        X = np.linspace(-6.8, 6.8, 160)

        def corriente(y0):
            from scipy.optimize import brentq
            sg, ys = np.sign(y0), []
            for x in X - C[0]:
                lo = sg * (np.sqrt(max(A * A - x * x, 0.0)) + 1e-6)
                f = lambda y: y * (1 - A * A / (x * x + y * y)) - y0
                ys.append(brentq(f, lo, sg * (abs(y0) + A + 1.0)))
            return np.stack([X, np.array(ys) + C[1], 0 * X], 1)
        sendas = [corriente(y0) for y0 in (-3.2, -2.0, -1.0, -0.3, 0.3, 1.0, 2.0, 3.2)]
        for j, s in enumerate(sendas):
            for q in range(3):
                p = punto(est.calido, 0.09)

                def fluir(m, s=s, q=q, j=j):
                    u = ((pel.t - 6.0) * 0.16 + q / 3 + 0.07 * j) % 1.0
                    p_ = recorrer(s, u)
                    vivo = rampa(pel.t, 6.0, 0.5) * min(u / 0.08, 1, (1 - u) / 0.08) * float(-5.6 < p_[1] < 5.4)
                    fundir(m.move_to(p_), vivo)
                p.add_updater(fluir)
                fundir(p, 0)
                self.add(p)
        burbuja = DashedVMobject(Arc(radius=A, start_angle=PI / 2, angle=PI, arc_center=C).set_stroke(est.calido, 3), num_dashes=28).set_z_index(4)
        self.add(aparece(burbuja, pel, 7.0))
        self.add(aparece(texto(est, "viento solar", 40, est.calido, "cuerpo", "SEMIBOLD").move_to([-4.6, 4.7, 0]).set_z_index(9), pel, 6.2))
        self.add(aparece(Arrow([-6.4, 4.0, 0], [-4.0, 4.0, 0], buff=0, stroke_width=6, color=est.calido).set_z_index(9), pel, 6.2))
        imanes = VGroup(texto(est, "un imán de refri:", 38, est.tenue, ancho_max=6.0),
                        texto(est, "≈ 150 veces más fuerte", 46, est.acento2, "cuerpo", "SEMIBOLD", ancho_max=7.0)).arrange(DOWN, buff=0.2)
        imanes.move_to([-1.6, -4.5, 0]).set_z_index(11)
        self.add(aparece(VGroup(BackgroundRectangle(imanes, color=est.fondo, fill_opacity=0.85, buff=0.25).set_z_index(10), imanes), pel, 13.0))

        leyendas(self, est, pel, n, [
            ("La Tierra se comporta como un imán", "su núcleo de hierro fundido, en movimiento, crea el campo"),
            ("Ese campo desvía el viento del Sol", "las partículas cargadas rodean la burbuja magnética"),
            ("Es débil, pero enorme", "y protege a los satélites y a la atmósfera")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 2 · Atrapadas en espiral (cinturones de Van Allen) ═══════════════════════════════════════════════════════════════════

class ReelEMEspiral(Scene):
    VAR = 1

    def construct(self):
        n = "ReelEMEspiral"; TB = DE.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Atrapadas\nen espiral", self.VAR, chip_txt="Cámara lenta", **SERIE)
        YC, X0 = 1.6, 6.3
        aprieta = lambda: 0.55 * rampa(pel.t, 5.0, 1.4)
        ancho = lambda x: 2.6 * (1 - aprieta() * (x / X0) ** 2)
        fuera = lambda: 1 - rampa(pel.t, 12.3, 0.8)
        for k, f in enumerate((-1.0, -0.62, -0.25, 0.25, 0.62, 1.0)):
            ln = VMobject().set_z_index(4)
            ln.add_updater(lambda m, f=f: m.set_points_smoothly([[x, YC + f * ancho(x), 0] for x in np.linspace(-X0 - 0.3, X0 + 0.3, 40)])
                           .set_stroke(est.acento, 4, 0.7 * rampa(pel.t, 0.3) * fuera()).set_fill(opacity=0))
            self.add(ln)
        self.add(aparece(texto(est, "campo magnético", 36, est.acento, "cuerpo", "SEMIBOLD").move_to([-3.4, YC + 3.3, 0]).set_z_index(9), pel, 0.5, hasta=12.3))
        # centro guía: avanza y, con el campo apretado, rebota entre los extremos (continuidad en t = 6)
        Aw, w = 4.29, TAU / 5.0
        phi = np.arctan2(4.1, 1.27)
        xg = lambda: (-5.5 + 1.6 * pel.t) if pel.t < 6.0 else Aw * np.sin(w * (pel.t - 6.0) + phi)
        e = punto(est.calido, 0.13)

        def girar(m):
            x = xg()
            r = 0.75 * ancho(x) / 2.6
            ph = TAU * 2.2 * pel.t
            m.move_to([x, YC + r * np.cos(ph), 0])
            fundir(m, rampa(pel.t, 0.6, 0.3) * fuera() * (0.55 + 0.45 * (np.sin(ph) > 0)))
        e.add_updater(girar)
        fundir(e, 0)
        self.add(e)
        cola(self, e, est.calido, n=30, ancho=5.0)
        self.add(aparece(texto(est, "electrón", 36, est.calido, "cuerpo", "SEMIBOLD").move_to([-4.6, YC - 3.3, 0]).set_z_index(9), pel, 0.8, hasta=5.5))
        self.add(aparece(VGroup(texto(est, "en realidad gira", 34, est.tenue),
                                texto(est, "≈ 840 000 veces por segundo", 42, est.tinta, "cifra", "SEMIBOLD", ancho_max=12.0)).arrange(DOWN, buff=0.15)
                         .move_to([0, -2.6, 0]).set_z_index(9), pel, 2.0, hasta=12.3))
        for x in (-X0 + 0.4, X0 - 0.4):
            self.add(aparece(texto(est, "rebota", 34, est.acento2, "cuerpo", "SEMIBOLD").move_to([x * 0.92, YC + 1.8, 0]).set_z_index(9), pel, 7.0, hasta=12.3))
        # la Tierra y los cinturones: la misma idea, a escala del planeta
        CT, RT = np.array([0, 0.6, 0]), 1.15
        self.add(aparece(tierra(est, CT, RT), pel, 12.8))
        for L0, L1, nombre in ((1.5, 2.3, "interior"), (3.2, 5.0, "exterior")):
            for lado in (-1, 1):
                a, b = linea_dipolo(CT, L0, RT, lado), linea_dipolo(CT, L1, RT, lado)
                cin = Polygon(*a, *b[::-1]).set_fill(est.acento2 if L0 > 3 else est.acento, 0.22).set_stroke(width=0).set_z_index(3)
                self.add(aparece(cin, pel, 13.0))
            pos = CT + (np.array([1.9, 1.35, 0]) if L0 < 3 else np.array([3.7, 2.55, 0]))
            self.add(aparece(texto(est, nombre, 36, est.tinta, "cuerpo", "SEMIBOLD").move_to(pos).set_z_index(9), pel, 13.6))
        senda = linea_dipolo(CT, 4.1, RT, 1)
        mid = len(senda) // 2
        tramo = senda[mid - 32:mid + 33]
        q = punto(est.calido, 0.11)
        q.add_updater(lambda m: fundir(m.move_to(recorrer(tramo, 0.5 + 0.5 * np.sin(TAU * (pel.t - 13.0) / 2.2))), rampa(pel.t, 13.4)))
        fundir(q, 0)
        self.add(q)

        leyendas(self, est, pel, n, [
            ("Una carga no puede cruzar el campo", "lo rodea en espiral, sin gastar energía"),
            ("Donde el campo se aprieta, rebota", "como una pelota entre dos espejos magnéticos"),
            ("Así quedan atrapadas alrededor de la Tierra", "son los cinturones de Van Allen")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 3 · ¿De dónde sale la aurora? ═════════════════════════════════════════════════════════════════════════════════════════

class ReelEMAurora(Scene):
    VAR = 2

    def construct(self):
        n = "ReelEMAurora"; TB = DE.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿De dónde sale\nla aurora?", self.VAR, chip_txt="Ilustración", **SERIE)
        CT, RT = np.array([-2.2, 3.3, 0]), 1.05
        self.add(aparece(tierra(est, CT, RT), pel, 0.2))
        lineas_ = []
        for L in (2.2, 3.0, 4.0):
            pts = linea_dipolo(CT, L, RT, 1)
            lineas_.append(pts)
            self.add(aparece(polilinea(pts, color=est.acento, width=3.5, opacity=0.6).set_z_index(4), pel, 0.4))
        # partículas que bajan por las líneas hacia el polo norte (primera mitad de cada línea, de afuera hacia el polo)
        for j, pts in enumerate(lineas_):
            mitad = pts[: len(pts) // 2][::-1]
            for q in range(3):
                p = punto(est.calido, 0.09)
                p.add_updater(lambda m, mitad=mitad, q=q, j=j: fundir(m.move_to(recorrer(mitad, ((pel.t * 0.33 + q / 3 + 0.2 * j) % 1.0))), rampa(pel.t, 0.8)))
                fundir(p, 0)
                self.add(p)
        polo = CT + UP * RT
        brillo = VGroup(*[Circle(radius=0.25 + 0.18 * k).set_fill(VERDE, 0.2 - 0.04 * k).set_stroke(width=0) for k in range(4)]).move_to(polo + UP * 0.12).set_z_index(9)
        brillo.add_updater(lambda m: fundir(m, rampa(pel.t, 1.6) * (0.75 + 0.25 * np.sin(5 * pel.t))))
        fundir(brillo, 0)
        self.add(brillo)
        self.add(aparece(texto(est, "partículas del Sol", 38, est.calido, "cuerpo", "SEMIBOLD").move_to([3.9, 4.6, 0]).set_z_index(9), pel, 0.8))
        # cortina vista de lado: regla de altura y franjas de color
        Y0, K = -5.2, 1.95                                           # y de 0 km y unidades por 100 km
        yk = lambda km: Y0 + K * km / 100
        X0, X1 = -3.9, 6.4
        panel_ = RoundedRectangle(corner_radius=0.2, width=X1 - X0 + 2.4, height=yk(330) - Y0 + 0.4).set_fill(est.fondo, 0.85).set_stroke(est.tenue, 1.6)
        self.add(aparece(panel_.move_to([(X0 - 2.2 + X1) / 2, (Y0 + yk(330)) / 2, 0]).set_z_index(2), pel, 5.8))
        for km in (0, 100, 200, 300):
            self.add(aparece(VGroup(Line([X0 - 0.3, yk(km), 0], [X0, yk(km), 0], stroke_width=3, color=est.tenue),
                                    texto(est, f"{km} km", 34, est.tenue).move_to([X0 - 1.45, yk(km), 0])).set_z_index(9), pel, 6.0))
        self.add(aparece(Line([X0, Y0, 0], [X0, yk(320), 0], stroke_width=3, color=est.tenue).set_z_index(9), pel, 6.0))
        rng = np.random.default_rng(4)
        xs = np.linspace(X0 + 0.4, X1 - 0.3, 46)
        for j, x in enumerate(xs):
            base = 100 + 12 * np.sin(j * 0.5) + rng.uniform(-4, 4)
            for a, b, col, op in ((base, 230, VERDE, 0.5), (230, 300, ROJO, 0.28), (base - 6, base + 6, VIOLETA, 0.45)):
                ray = Line([x, yk(a), 0], [x, yk(b), 0], stroke_width=7, color=col).set_z_index(5)
                ray.add_updater(lambda m, j=j, op=op: m.set_stroke(opacity=op * rampa(pel.t, 6.4 + 0.02 * j, 0.5) * (0.55 + 0.45 * np.sin(2.3 * pel.t + 0.7 * j) ** 2)))
                ray.set_stroke(opacity=0)
                self.add(ray)
        for txt, col, y in (("oxígeno: verde", VERDE, 160), ("oxígeno: rojo", ROJO, 265), ("nitrógeno: violeta", VIOLETA, 62)):
            et = texto(est, txt, 40, col, "cuerpo", "SEMIBOLD").set_z_index(10)
            caja = BackgroundRectangle(et, color=est.fondo, fill_opacity=0.8, buff=0.12).set_z_index(9)
            self.add(aparece(VGroup(caja, et).move_to([2.6, yk(y), 0]), pel, 12.8))

        leyendas(self, est, pel, n, [
            ("Partículas del Sol siguen el campo", "y bajan hacia los polos, donde entran las líneas"),
            ("A 100–300 km chocan con el aire", "cada choque enciende un átomo, como un tubo de neón"),
            ("Cada color es un tipo de átomo", "oxígeno: verde y rojo · nitrógeno: azul y violeta")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 4 · Girar un satélite sin combustible (magnetotorque) ═══════════════════════════════════════════════════════════════

class ReelEMTorque(Scene):
    VAR = 0

    def construct(self):
        n = "ReelEMTorque"; TB = DE.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Girar un satélite\nsin combustible", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        C = np.array([0, 1.6, 0])
        for y in np.linspace(-1.9, 4.9, 6):
            self.add(aparece(Arrow([-6.6, y, 0], [6.6, y, 0], buff=0, stroke_width=3, color=est.acento, max_tip_length_to_length_ratio=0.03).set_opacity(0.45).set_z_index(3), pel, 0.3, hasta=12.4))
        self.add(aparece(texto(est, "campo de la Tierra", 34, est.acento, "cuerpo", "SEMIBOLD").move_to([-3.6, 5.5, 0]).set_z_index(9), pel, 0.3, hasta=12.4))
        # ángulo: de 90° a 0° como un péndulo amortiguado (par m×B), desde t = 2 s
        def ang():
            u = max(pel.t - 2.0, 0.0)
            return PI / 2 * np.exp(-0.32 * u) * np.cos(0.9 * u) if pel.t > 2.0 else PI / 2

        def sat():
            a = ang()
            cubo = Square(2.6).set_fill(est.mezcla(est.fondo, est.tinta, 0.12), 1).set_stroke(est.tinta, 4)
            panel = VGroup(Rectangle(width=1.6, height=0.9).set_fill("#1E3A8A", 1).set_stroke(est.tenue, 2).shift(LEFT * 2.15),
                           Rectangle(width=1.6, height=0.9).set_fill("#1E3A8A", 1).set_stroke(est.tenue, 2).shift(RIGHT * 2.15))
            bobina = VGroup(*[Ellipse(width=0.5, height=2.0 - 0.06 * k).set_stroke(est.calido, 4).shift(RIGHT * (-0.18 + 0.09 * k)) for k in range(5)])
            corr = rampa(pel.t, 1.0, 0.4)
            m_ = Arrow(ORIGIN, RIGHT * 2.9, buff=0, stroke_width=9, color=est.acento2, max_tip_length_to_length_ratio=0.18).set_opacity(corr)
            return VGroup(panel, cubo, bobina.set_opacity(0.4 + 0.6 * corr), m_).rotate(a, about_point=ORIGIN).shift(C).set_z_index(8)
        s = sat()
        s.add_updater(lambda m: m.become(sat()).set_opacity(1 - rampa(pel.t, 12.4, 0.8)) if pel.t < 13.4 else m.set_opacity(0))
        self.add(s)
        self.add(aparece(texto(est, "bobina con corriente = imán", 36, est.calido, "cuerpo", "SEMIBOLD", ancho_max=11).move_to([0, -2.8, 0]).set_z_index(9), pel, 1.2, hasta=6.0))
        self.add(aparece(texto(est, "se alinea con el campo, como una brújula", 36, est.tinta, "cuerpo", "SEMIBOLD", ancho_max=12).move_to([0, -2.8, 0]).set_z_index(9), pel, 6.2, hasta=12.4))
        self.add(Viva(est, lambda: f"{int(round(np.degrees(abs(ang()))))}°", C + RIGHT * 4.6 + DOWN * 2.9, 54, est.acento2, f_op=lambda: rampa(pel.t, 2.0) * (1 - rampa(pel.t, 12.4))))
        # comparación: cerca de la Tierra vs. órbita geoestacionaria (misma escala de tiempo)
        W = 11.0
        for k, (nombre, seg, txt, col) in enumerate((("a 550 km", DE.TORQ_LEO_S, "≈ 36 s", VERDE), ("órbita geoestacionaria", DE.TORQ_GEO_S, "≈ 9 min", ROJO))):
            y = 3.6 - 3.0 * k
            ancho = W * seg / DE.TORQ_GEO_S
            self.add(aparece(texto(est, nombre, 40, col, "cuerpo", "SEMIBOLD").move_to([-6.2, y + 0.8, 0], aligned_edge=LEFT).set_z_index(9), pel, 13.2))
            barra = Rectangle(width=0.01, height=0.7).set_z_index(6)
            barra.add_updater(lambda m, ancho=ancho, col=col, y=y: m.become(Rectangle(width=max(ancho * rampa(pel.t, 13.6, 2.4), 0.01), height=0.7).set_fill(col, 0.9 * rampa(pel.t, 13.4)).set_stroke(width=0).move_to([-6.2, y - 0.2, 0], aligned_edge=LEFT).set_z_index(6)))
            self.add(barra)
            self.add(aparece(texto(est, txt, 46, est.tinta, "cifra", "SEMIBOLD").move_to([max(-6.2 + ancho + 1.0, -4.0), y - 0.2, 0]).set_z_index(9), pel, 15.6))
        self.add(aparece(texto(est, "girar 90° un cubo de 10 cm", 38, est.tenue, ancho_max=11).move_to([0, -3.4, 0]).set_z_index(9), pel, 13.2))

        leyendas(self, est, pel, n, [
            ("Una bobina con corriente se vuelve imán", "y, como una brújula, busca el campo de la Tierra"),
            ("Así se orienta un satélite pequeño", "sin combustible: solo electricidad de sus paneles"),
            ("Lejos de la Tierra, el campo es débil", "en geoestacionaria tardaría unas 15 veces más")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 5 · Maxwell encontró la luz (c = 1/√(μ0 ε0)) ═════════════════════════════════════════════════════════════════════════

class ReelEMLuz(Scene):
    VAR = 1

    def construct(self):
        n = "ReelEMLuz"; TB = DE.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "La luz estaba\nescondida en un imán", self.VAR, chip_txt="Historia de la física", **SERIE)
        fuera = lambda: 1 - rampa(pel.t, 12.2, 0.7)
        # dos experimentos de mesa: una bobina con un imán y un condensador con una batería
        bob = VGroup(*[Ellipse(width=1.0, height=2.8).set_stroke(est.acento, 6).shift(RIGHT * 0.42 * k) for k in range(6)],
                     Rectangle(width=2.0, height=0.7).set_fill(ROJO, 1).set_stroke(width=0).shift(LEFT * 1.9)).move_to([-3.4, 3.2, 0]).set_z_index(8)
        cond = VGroup(Line([-1.3, 1.2, 0], [1.3, 1.2, 0], stroke_width=11, color=est.acento2), Line([-1.3, -1.2, 0], [1.3, -1.2, 0], stroke_width=11, color=est.acento2),
                      *[Arrow([x, 1.0, 0], [x, -1.0, 0], buff=0, stroke_width=5, color=est.acento2, max_tip_length_to_length_ratio=0.18).set_opacity(0.6) for x in (-0.9, 0, 0.9)]).move_to([3.6, 3.2, 0]).set_z_index(8)
        self.add(aparece(bob, pel, 0.4, hasta=12.2), aparece(cond, pel, 1.0, hasta=12.2))
        self.add(aparece(texto(est, "magnetismo", 46, est.acento, "cuerpo", "SEMIBOLD").move_to([-3.4, 1.0, 0]).set_z_index(9), pel, 0.6, hasta=12.2))
        self.add(aparece(texto(est, "electricidad", 46, est.acento2, "cuerpo", "SEMIBOLD").move_to([3.6, 1.0, 0]).set_z_index(9), pel, 1.2, hasta=12.2))
        self.add(aparece(texto(est, "μ₀", 84, est.acento, "titulo", "BOLD").move_to([-3.4, -0.4, 0]).set_z_index(9), pel, 2.0, hasta=12.2))
        self.add(aparece(texto(est, "ε₀", 84, est.acento2, "titulo", "BOLD").move_to([3.6, -0.4, 0]).set_z_index(9), pel, 2.4, hasta=12.2))
        formula = texto(est, "1 / √(μ₀ · ε₀)", 76, est.tinta, "titulo", "SEMIBOLD").move_to([0, -2.6, 0]).set_z_index(9)
        self.add(aparece(formula, pel, 6.0, hasta=12.2))
        for x in (-3.6, 3.6):
            self.add(aparece(Arrow([x * 0.8, -1.2, 0], [x * 0.3, -2.0, 0], buff=0, stroke_width=5, color=est.tenue).set_z_index(7), pel, 6.0, hasta=12.2))
        vel = lambda: DE.C_KM_S * rampa(pel.t, 7.4, 2.4)
        self.add(Viva(est, lambda: f"{vel():,.0f} km/s".replace(",", " "), [0, -4.5, 0], 84, est.calido, f_op=lambda: rampa(pel.t, 7.2) * fuera()))
        # la onda: E (vertical) y B (en perspectiva), viajando
        X0, X1, YO = -6.4, 6.4, 2.2
        xs = np.linspace(X0, X1, 160)
        k_ = TAU / 4.2
        ondaE, ondaB = VMobject().set_z_index(7), VMobject().set_z_index(6)
        ondaE.add_updater(lambda m: m.set_points_smoothly([[x, YO + 1.7 * np.sin(k_ * x - 3.0 * pel.t), 0] for x in xs]).set_stroke(est.acento2, 6, rampa(pel.t, 12.6)).set_fill(opacity=0))
        ondaB.add_updater(lambda m: m.set_points_smoothly([[x + 0.55 * np.sin(k_ * x - 3.0 * pel.t), YO - 0.55 * np.sin(k_ * x - 3.0 * pel.t), 0] for x in xs]).set_stroke(est.acento, 6, rampa(pel.t, 12.6)).set_fill(opacity=0))
        self.add(ondaB, ondaE, aparece(Line([X0, YO, 0], [X1, YO, 0], stroke_width=2, color=est.tenue).set_z_index(5), pel, 12.6))
        self.add(aparece(texto(est, "eléctrico", 36, est.acento2, "cuerpo", "SEMIBOLD").move_to([-4.6, YO + 2.5, 0]).set_z_index(9), pel, 12.9))
        self.add(aparece(texto(est, "magnético", 36, est.acento, "cuerpo", "SEMIBOLD").move_to([4.6, YO - 2.4, 0]).set_z_index(9), pel, 12.9))
        CT = np.array([0, -3.0, 0])
        self.add(aparece(tierra(est, CT, 1.3), pel, 13.2))
        rayo = punto(est.calido, 0.12)
        rayo.add_updater(lambda m: fundir(m.move_to(CT + 1.7 * np.array([np.cos(TAU * 7.5 * (pel.t - 13.5) / 6.0), np.sin(TAU * 7.5 * (pel.t - 13.5) / 6.0), 0])), rampa(pel.t, 13.5)))
        fundir(rayo, 0)
        self.add(rayo)
        cola(self, rayo, est.calido, n=22, ancho=6.0)
        self.add(aparece(texto(est, "7 vueltas y media\nen un segundo", 40, est.tinta, "cuerpo", "SEMIBOLD", ancho_max=5.6).move_to([4.2, -3.0, 0]).set_z_index(9), pel, 13.6))
        self.add(aparece(texto(est, "(en cámara lenta)", 32, est.tenue).move_to([-4.3, -3.0, 0]).set_z_index(9), pel, 13.6))

        leyendas(self, est, pel, n, [
            ("Dos números medidos en una mesa", "uno con imanes, otro con cargas eléctricas"),
            ("Maxwell los combinó: salió una velocidad", "la misma que ya se había medido para la luz"),
            ("La luz es electricidad y magnetismo", "viajando juntos, sin necesitar nada que los cargue")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 6 · Mismo fenómeno, otro tamaño (bandas) ═══════════════════════════════════════════════════════════════════════════

class ReelEMBandas(Scene):
    VAR = 2

    def construct(self):
        n = "ReelEMBandas"; TB = DE.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Mismo fenómeno,\notro tamaño", self.VAR, chip_txt="A escala", **SERIE)
        X0, X1 = -6.2, 6.4
        cm = (X1 - X0) / 80.0                                         # 80 cm a lo ancho
        objetos = {"UHF": "como un brazo", "S": "como un lápiz", "X": "como un dedo", "Ka": "como una uña"}
        cols = [est.acento, est.acento2, est.calido, VERDE]
        for k, ((nombre, f, uso), col) in enumerate(zip(DE.BANDAS, cols)):
            y = 4.4 - 2.5 * k
            lam = DE.LAMBDAS_CM[nombre] * cm
            t0 = 0.5 + 1.2 * k
            xs = np.linspace(X0, X1, max(200, int(30 * (X1 - X0) / lam)))
            onda = VMobject().set_z_index(6)
            onda.add_updater(lambda m, lam=lam, y=y, t0=t0, col=col, xs=xs: m.set_points_smoothly(
                [[x, y + 0.42 * np.sin(TAU * (x - X0) / lam - 4.0 * pel.t), 0] for x in xs]).set_stroke(col, 4, rampa(pel.t, t0) * (1 - 0.6 * rampa(pel.t, 12.4))).set_fill(opacity=0))
            self.add(onda)
            et = VGroup(texto(est, nombre, 44, col, "titulo", "BOLD"), texto(est, f"{DE.LAMBDAS_CM[nombre]:.0f} cm · {uso}", 34, est.tinta, "cuerpo", "SEMIBOLD"))
            et.arrange(RIGHT, buff=0.35).move_to([X0, y + 0.95, 0], aligned_edge=LEFT).set_z_index(9)
            self.add(aparece(et, pel, t0))
            self.add(aparece(texto(est, objetos[nombre], 32, est.tenue).move_to([X1, y + 0.95, 0], aligned_edge=RIGHT).set_z_index(9), pel, 6.2))
            self.add(aparece(BackgroundRectangle(et, color=est.fondo, fill_opacity=0.75, buff=0.08).set_z_index(8), pel, t0))
        regla = VGroup(Line([X0, -4.6, 0], [X1, -4.6, 0], stroke_width=3, color=est.tenue),
                       *[Line([X0 + c * cm, -4.6, 0], [X0 + c * cm, -4.6 + (0.3 if c % 10 == 0 else 0.14), 0], stroke_width=3, color=est.tenue) for c in range(0, 81, 2)],
                       texto(est, "80 cm", 30, est.tenue).move_to([X1 - 0.6, -5.15, 0])).set_z_index(9)
        self.add(aparece(regla, pel, 0.3, hasta=12.4))
        self.add(aparece(VGroup(texto(est, "luz visible: medio micrómetro", 42, est.tinta, "cuerpo", "SEMIBOLD", ancho_max=12.4),
                                texto(est, "≈ 100 veces más fina que un cabello", 38, est.calido, "cuerpo", "SEMIBOLD", ancho_max=12.4)).arrange(DOWN, buff=0.25)
                         .move_to([0, -4.4, 0]).set_z_index(10), pel, 13.0))
        self.add(aparece(Rectangle(width=13.4, height=2.2).set_fill(est.fondo, 0.85).set_stroke(width=0).move_to([0, -4.4, 0]).set_z_index(9), pel, 12.8))

        leyendas(self, est, pel, n, [
            ("Radio, microondas y luz: lo mismo", "ondas electromagnéticas de distinto tamaño"),
            ("Cada satélite elige un tamaño de onda", "más pequeña: más datos, pero la lluvia la frena más"),
            ("La luz visible es diminuta", "y aun así es la misma física que la radio")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 7 · ¿Cómo una antena lanza ondas? (dipolo) ═══════════════════════════════════════════════════════════════════════════

class ReelEMAntena(Scene):
    VAR = 0

    def construct(self):
        n = "ReelEMAntena"; TB = DE.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Cómo una antena\nlanza ondas?", self.VAR, chip_txt="Cámara lenta", **SERIE)
        C = np.array([-3.6, 1.4, 0])
        brazo = 2.0
        self.add(aparece(VGroup(Line(C + UP * 0.15, C + UP * (0.15 + brazo), stroke_width=10, color=est.tinta),
                                Line(C + DOWN * 0.15, C + DOWN * (0.15 + brazo), stroke_width=10, color=est.tinta),
                                Dot(C, radius=0.12, color=est.calido)).set_z_index(9), pel, 0.2))
        w = TAU / 2.0
        for signo, col in ((1, est.acento2), (-1, est.acento)):
            q = VGroup(Circle(radius=0.26).set_fill(col, 1).set_stroke(width=0), texto(est, "+" if signo > 0 else "−", 34, est.fondo, "titulo", "BOLD")).set_z_index(10)
            q.add_updater(lambda m, signo=signo: fundir(m.move_to(C + UP * signo * (0.15 + brazo * (0.5 + 0.45 * np.sin(w * pel.t)))), rampa(pel.t, 0.5)))
            fundir(q, 0)
            self.add(q)
        # frentes de onda: anillos que salen con brillo ∝ sen θ (el «donut»: nada por las puntas)
        R_MAX, V = 9.0, 1.3
        for j in range(7):
            frente = VGroup(*[Arc(radius=1, start_angle=a, angle=TAU / 48) for a in np.linspace(0, TAU, 48, endpoint=False)]).set_z_index(5)

            def crecer(m, j=j):
                edad = (pel.t - 1.0 - j * 1.0) % 7.0
                r = 0.3 + V * edad
                vivo = rampa(pel.t, 1.0 + j * 1.0, 0.2) * max(0.0, 1 - r / R_MAX)
                for k, a in enumerate(m):
                    th = (k + 0.5) * TAU / 48
                    s_ = abs(np.cos(th))                                # θ medido desde el eje vertical: |sen θ| = |cos(ángulo)|
                    a.become(Arc(radius=r, start_angle=k * TAU / 48, angle=TAU / 48, arc_center=C).set_stroke(est.calido, 5, 0.9 * vivo * s_ ** 1.5))
            frente.add_updater(crecer)
            self.add(frente)
        self.add(aparece(texto(est, "fuerte hacia los lados", 36, est.calido, "cuerpo", "SEMIBOLD").move_to([3.2, 1.2, 0]).set_z_index(9), pel, 7.0, hasta=12.4))
        self.add(aparece(texto(est, "casi nada por las puntas", 36, est.tenue, "cuerpo", "SEMIBOLD").move_to([-3.4, 5.0, 0]).set_z_index(9), pel, 8.0, hasta=12.4))
        # tamaño real para 437 MHz
        largo = 34.3 / 30.0 * 6.0
        tapa = Rectangle(width=13.6, height=4.0).set_fill(est.fondo, 0.9).set_stroke(width=0).move_to([0, -3.6, 0]).set_z_index(10)
        self.add(aparece(tapa, pel, 12.6))
        self.add(aparece(VGroup(Line([-largo / 2, -3.0, 0], [largo / 2, -3.0, 0], stroke_width=12, color=est.tinta),
                                texto(est, "antena de 34 cm (437 MHz)", 38, est.tinta, "cuerpo", "SEMIBOLD").move_to([0, -2.2, 0])).set_z_index(11), pel, 12.8))
        regla = VGroup(Rectangle(width=6.0, height=0.7).set_fill(est.calido, 0.85).set_stroke(width=0),
                       *[Line([-3.0 + 0.2 * c, 0.35, 0], [-3.0 + 0.2 * c, 0.35 - (0.3 if c % 5 == 0 else 0.15), 0], stroke_width=2, color=est.fondo) for c in range(31)])
        self.add(aparece(VGroup(regla.move_to([-largo / 2 + 3.0, -4.2, 0]), texto(est, "regla de 30 cm", 32, est.tenue).move_to([0, -5.1, 0])).set_z_index(11), pel, 13.6))

        leyendas(self, est, pel, n, [
            ("Cargas que suben y bajan muy rápido", "437 millones de veces por segundo en un cubesat"),
            ("Cada vaivén suelta una onda que se aleja", "sale hacia los lados, casi nada por las puntas"),
            ("Su tamaño depende de la onda", "media onda: un poco más que una regla escolar")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 8 · Un espejo en el cielo (ionosfera) ════════════════════════════════════════════════════════════════════════════════

class ReelEMIonosfera(Scene):
    VAR = 1

    def construct(self):
        n = "ReelEMIonosfera"; TB = DE.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Un espejo\nen el cielo", self.VAR, chip_txt="Ilustración", **SERIE)
        RS = 30.0                                                     # suelo: arco de un círculo grande
        CS = np.array([0, -4.6 - RS, 0])
        suelo_y = lambda x: CS[1] + np.sqrt(RS * RS - x * x)
        self.add(aparece(Polygon(*[[x, suelo_y(x), 0] for x in np.linspace(-7.2, 7.2, 80)], [7.2, -5.6, 0], [-7.2, -5.6, 0]).set_fill(est.mezcla(est.fondo, AZUL, 0.55), 1).set_stroke("#8FD8FF", 3).set_z_index(4), pel, 0.1))
        H_I = 4.4
        capa = VGroup(*[Line([x, suelo_y(x) + H_I, 0], [x + 0.3, suelo_y(x + 0.3) + H_I, 0]) for x in np.linspace(-7.2, 6.9, 48)])
        banda = Polygon(*[[x, suelo_y(x) + H_I - 0.4, 0] for x in np.linspace(-7.2, 7.2, 60)], *[[x, suelo_y(x) + H_I + 0.9, 0] for x in np.linspace(7.2, -7.2, 60)]).set_fill(VIOLETA, 0.22).set_stroke(width=0).set_z_index(3)
        self.add(aparece(banda, pel, 0.4))
        rng = np.random.default_rng(8)
        for j in range(60):
            x = rng.uniform(-6.8, 6.8); dy = rng.uniform(-0.3, 0.8)
            e = Dot(radius=0.05, color=VIOLETA).set_z_index(4)
            e.add_updater(lambda m, x=x, dy=dy, j=j: fundir(m.move_to([x + 0.08 * np.sin(3 * pel.t + j), suelo_y(x) + H_I + dy, 0]), rampa(pel.t, 0.6) * 0.9))
            fundir(e, 0)
            self.add(e)
        self.add(aparece(texto(est, "ionosfera", 40, VIOLETA, "cuerpo", "SEMIBOLD").move_to([4.6, suelo_y(4.6) + H_I + 1.5, 0]).set_z_index(9), pel, 0.8))
        # rayo bajo (onda corta): rebota dos veces
        A_ = np.array([-6.0, suelo_y(-6.0), 0])
        pts_bajo = [A_]
        for k in range(2):
            x0 = -6.0 + 6.0 * k
            pts_bajo += [np.array([x0 + 3.0, suelo_y(x0 + 3.0) + H_I - 0.2, 0]), np.array([x0 + 6.0, suelo_y(x0 + 6.0), 0])]
        pts_bajo = np.array(pts_bajo)
        dens = np.concatenate([np.linspace(pts_bajo[i], pts_bajo[i + 1], 40, endpoint=False) for i in range(len(pts_bajo) - 1)] + [pts_bajo[-1:]])
        bajo = VMobject().set_z_index(6)
        bajo.add_updater(lambda m: m.set_points_as_corners(dens[: max(2, int(len(dens) * rampa(pel.t, 6.0, 5.0)))]).set_stroke(est.calido, 6, 0.95).set_fill(opacity=0))
        self.add(bajo)
        cabeza = punto(est.calido, 0.12)
        cabeza.add_updater(lambda m: fundir(m.move_to(dens[max(1, int(len(dens) * rampa(pel.t, 6.0, 5.0))) - 1]), rampa(pel.t, 6.0, 0.2)))
        fundir(cabeza, 0)
        self.add(cabeza)
        self.add(aparece(texto(est, "onda corta: rebota", 42, est.calido, "cuerpo", "SEMIBOLD").move_to([-3.2, 2.2, 0]).set_z_index(9), pel, 7.0))
        # rayo alto: cruza hacia el satélite
        S_ = np.array([3.6, 4.6, 0])
        sat = VGroup(Square(0.5).set_fill(est.tinta, 1).set_stroke(width=0), Rectangle(width=0.9, height=0.3).set_fill("#1E3A8A", 1).set_stroke(est.tenue, 2).shift(LEFT * 0.75),
                     Rectangle(width=0.9, height=0.3).set_fill("#1E3A8A", 1).set_stroke(est.tenue, 2).shift(RIGHT * 0.75)).move_to(S_).set_z_index(9)
        self.add(aparece(sat, pel, 12.4))
        B_ = np.array([0.6, suelo_y(0.6), 0])
        alto = Line(B_, B_ + RIGHT * 0.001).set_z_index(6)
        alto.add_updater(lambda m: m.put_start_and_end_on(B_, B_ + (S_ - B_) * max(rampa(pel.t, 12.8, 2.5), 0.001)).set_stroke(est.acento, 6, 0.95 * rampa(pel.t, 12.8, 0.2)))
        self.add(alto)
        self.add(aparece(texto(est, "más de ~9 MHz:\ncruza al espacio", 42, est.acento, "cuerpo", "SEMIBOLD", ancho_max=6.0).move_to([-3.2, 4.3, 0]).set_z_index(9), pel, 13.4))

        leyendas(self, est, pel, n, [
            ("Allá arriba hay electrones sueltos", "la ionosfera: aire que la luz del Sol electrifica"),
            ("La radio de onda corta rebota en ella", "así puede darle la vuelta al mundo"),
            ("Las frecuencias altas la atraviesan", "por eso los satélites usan frecuencias altas")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 9 · Un cable que genera electricidad en órbita (amarra electrodinámica) ═════════════════════════════════════════════

class ReelEMCable(Scene):
    VAR = 2

    def construct(self):
        n = "ReelEMCable"; TB = DE.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Un cable que genera\nelectricidad en órbita", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        for x in np.linspace(-6.0, 6.0, 7):
            for y in np.linspace(-4.6, 4.6, 7):
                self.add(aparece(VGroup(Circle(radius=0.17).set_stroke("#6FB6FF", 2.5, 0.55), Dot(radius=0.055, color="#6FB6FF").set_opacity(0.55)).move_to([x, y, 0]).set_z_index(3), pel, 0.3))
        self.add(aparece(texto(est, "campo de la Tierra: sale de la pantalla", 32, "#6FB6FF", ancho_max=8.4).move_to([-2.2, 5.3, 0]).set_z_index(9), pel, 0.3))
        X = lambda: -4.8 + 6.4 * rampa(pel.t, 0.5, 11.5) + 0.0
        TOP, BOT = 3.4, -3.6

        def nave():
            x = X()
            return VGroup(Square(0.9).set_fill(est.tinta, 1).set_stroke(width=0), Rectangle(width=1.6, height=0.45).set_fill("#1E3A8A", 1).set_stroke(est.tenue, 2).shift(LEFT * 1.3),
                          Rectangle(width=1.6, height=0.45).set_fill("#1E3A8A", 1).set_stroke(est.tenue, 2).shift(RIGHT * 1.3)).move_to([x, TOP + 0.45, 0]).set_z_index(9)
        sat = nave()
        sat.add_updater(lambda m: m.become(nave()))
        cable = Line(UP, DOWN).set_z_index(8)
        cable.add_updater(lambda m: m.put_start_and_end_on([X(), TOP, 0], [X(), BOT, 0]).set_stroke(est.calido, 5, rampa(pel.t, 0.4)))
        peso = Square(0.4).set_z_index(9)
        peso.add_updater(lambda m: m.become(Square(0.4).set_fill(est.calido, 1).set_stroke(width=0).move_to([X(), BOT, 0])).set_opacity(rampa(pel.t, 0.4)))
        self.add(cable, sat, peso)
        self.add(Viva(est, lambda: "→ 7.6 km/s", lambda: [X() + 3.2, TOP + 0.45, 0], 38, est.tinta, rol="cuerpo", f_op=lambda: rampa(pel.t, 1.0) * (1 - rampa(pel.t, 12.3))))
        # cargas que se separan: + arriba, − abajo
        for j in range(8):
            for signo, col in ((1, est.acento2), (-1, est.acento)):
                q = VGroup(Circle(radius=0.17).set_fill(col, 1).set_stroke(width=0), texto(est, "+" if signo > 0 else "−", 24, est.fondo, "titulo", "BOLD")).set_z_index(10)

                def mover(m, j=j, signo=signo):
                    u = rampa(pel.t, 5.5 + 0.12 * j, 2.0)
                    y0 = (TOP + BOT) / 2 + (j - 3.5) * 0.35
                    y1 = (TOP - 0.4 - 0.4 * j) if signo > 0 else (BOT + 0.5 + 0.4 * j)
                    fundir(m.move_to([X() + 0.4 * signo, y0 + (y1 - y0) * u, 0]), rampa(pel.t, 5.0, 0.4))
                q.add_updater(mover)
                fundir(q, 0)
                self.add(q)
        self.add(aparece(VGroup(texto(est, "≈ 185 V", 64, est.calido, "cifra", "SEMIBOLD"), texto(est, "por cada km de cable", 34, est.tinta)).arrange(DOWN, buff=0.2)
                         .move_to([-3.6, -4.9, 0]).set_z_index(11), pel, 8.0))
        self.add(aparece(BackgroundRectangle(VGroup(Square(1)).move_to([-3.6, -4.9, 0]).scale([4.6, 1.8, 1]), color=est.fondo, fill_opacity=0.8).set_z_index(10), pel, 8.0))
        freno = Arrow(ORIGIN, LEFT * 2.6, buff=0, stroke_width=10, color=ROJO).set_z_index(11)
        freno.add_updater(lambda m: m.become(Arrow([X() - 1.9, TOP - 1.0, 0], [X() - 4.4, TOP - 1.0, 0], buff=0, stroke_width=10, color=ROJO)).set_z_index(11).set_opacity(rampa(pel.t, 12.8)))
        self.add(freno)
        self.add(aparece(texto(est, "y lo frena", 44, ROJO, "cuerpo", "SEMIBOLD").move_to([-2.6, 1.3, 0]).set_z_index(11), pel, 13.2))

        leyendas(self, est, pel, n, [
            ("Un cable largo que cruza el campo", "a 7.6 km por segundo, funciona como un generador"),
            ("Entre sus puntas aparece voltaje", "unos 185 voltios por cada kilómetro de cable"),
            ("Esa corriente también lo frena", "una idea para bajar satélites viejos sin combustible")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 10 · La señal llega casi apagada (cuadrado inverso) ═══════════════════════════════════════════════════════════════════

class ReelEMSenal(Scene):
    VAR = 0

    def construct(self):
        n = "ReelEMSenal"; TB = DE.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "La señal llega\ncasi apagada", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        F0 = np.array([-6.0, 1.6, 0])
        self.add(aparece(VGroup(Square(0.6).set_fill(est.tinta, 1).set_stroke(width=0), Rectangle(width=0.3, height=1.2).set_fill("#1E3A8A", 1).set_stroke(est.tenue, 2).shift(UP * 0.95),
                                Rectangle(width=0.3, height=1.2).set_fill("#1E3A8A", 1).set_stroke(est.tenue, 2).shift(DOWN * 0.95)).move_to(F0).set_z_index(9), pel, 0.2))
        # el haz de una pirámide: a distancia d, 2d, 3d el mismo «chorro» cubre 1, 4 y 9 cuadros
        D, LADO = 4.0, 1.45
        for k in (1, 2, 3):
            x = F0[0] + D * k
            t0 = 1.0 + 1.6 * (k - 1)
            lado = LADO * k
            g = VGroup()
            for i in range(k):
                for j in range(k):
                    g.add(Square(LADO * 0.94).move_to([x - LADO / 2, F0[1] + (i - (k - 1) / 2) * LADO, 0]).set_fill(est.calido, 0.85 / (k * k) + 0.06).set_stroke(est.calido, 2.5))
            g.set_z_index(6)
            self.add(aparece(g, pel, t0))
            self.add(aparece(texto(est, ("1 ×", "2 ×", "3 ×")[k - 1], 40, est.tinta, "cifra", "SEMIBOLD").move_to([x - LADO / 2, F0[1] + lado / 2 + 0.6, 0]).set_z_index(9), pel, t0))
            self.add(aparece(texto(est, ("toda\nla señal", "¼ en cada\ncuadro", "⅑ en cada\ncuadro")[k - 1], 36, est.calido, "cuerpo", "SEMIBOLD", ancho_max=3.5)
                             .move_to([x - LADO / 2, F0[1] - lado / 2 - 0.8, 0]).set_z_index(9), pel, t0 + 0.6))
        for s in (1, -1):
            self.add(aparece(DashedLine(F0, F0 + np.array([3 * D, s * 3 * LADO / 2 * 1.08, 0]), stroke_width=3, color=est.tenue, dash_length=0.18).set_z_index(4), pel, 0.6))
        # 1 W a 1000 km
        exp_ = lambda: -15 * rampa(pel.t, 13.0, 3.0)
        self.add(aparece(texto(est, "distancia", 34, est.tenue).move_to([0.0, F0[1] + 3 * LADO / 2 + 1.4, 0]).set_z_index(9), pel, 1.0))
        self.add(aparece(texto(est, "1 watt a 1000 km", 48, est.tinta, "cuerpo", "SEMIBOLD").move_to([0, -3.4, 0]).set_z_index(9), pel, 12.6))
        self.add(Viva(est, lambda: "llegan ≈ 0.000 000 000 000 003 W" if pel.t > 15.8 else "llega…", [0, -4.4, 0], 44, est.calido, f_op=lambda: rampa(pel.t, 12.9)))
        self.add(aparece(texto(est, "3 milbillonésimas de watt", 40, est.tenue).move_to([0, -5.3, 0]).set_z_index(9), pel, 16.0))

        leyendas(self, est, pel, n, [
            ("La señal se reparte al alejarse", "al doble de distancia, cuatro veces más débil"),
            ("Y sigue repartiéndose sin parar", "al triple, nueve veces más débil"),
            ("Por eso las antenas concentran la señal", "y los receptores escuchan casi en silencio")])
        cerrar_serie(self, est, pel, self.VAR)

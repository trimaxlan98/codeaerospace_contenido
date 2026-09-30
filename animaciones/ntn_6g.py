"""Redes No Terrestres (NTN) y 6G: enlaces de comunicación. Co.De Aerospace."""
from code_lib import *
import numpy as np


# ---------------------------------------------------------------- base -----
class PiezaN(Pieza):
    def cierre(self, t=0.6):
        if os.environ.get("CODE_FOTO"):
            return
        self.wait(1.2)
        for m in self.mobjects:
            for s in m.get_family():
                s.clear_updaters()
        trk = [m for m in self.mobjects if isinstance(m, ValueTracker)]
        self.remove(*trk)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=t)
        self.wait(0.3)


# ------------------------------------------------------------- helpers -----
def unit(v):
    v = np.array(v, dtype=float)
    return v / np.linalg.norm(v)


def borde(p, q, r):
    """Punto a distancia r de p en dirección a q."""
    return np.array(p, dtype=float) + r * unit(np.array(q) - np.array(p))


def elipse_pts(cx, cy, w, h, n=60, mitad=False):
    tt = np.linspace(0, PI if mitad else TAU, n, endpoint=not mitad is False)
    return [np.array([cx + w / 2 * np.cos(t), cy + h / 2 * np.sin(t), 0]) for t in tt]


def corriente(escena, pts, color, n=4, periodo=4.0, invertir=False, radio=0.09):
    """Flujo continuo de pulsos a lo largo de una polilínea."""
    camino = VMobject().set_points_as_corners([np.array(p, dtype=float) for p in pts])
    T = ValueTracker(0)
    T.add_updater(lambda m, dt: m.increment_value(dt))
    escena.add(T)
    g = VGroup()
    for k in range(n):
        d = Dot(radius=radio, color=color)

        def act(m, k=k):
            a = (T.get_value() / periodo + k / n) % 1
            pos = 1 - a if invertir else a
            m.move_to(camino.point_from_proportion(pos))
            m.set_opacity(min(1, 8 * a, 8 * (1 - a)))
        d.add_updater(act)
        act(d)
        g.add(d)
    escena.add(g)
    return g


def telefono(alto=0.6, color=None):
    c = color or TINTA
    cu = RoundedRectangle(corner_radius=alto * 0.12, width=alto * 0.55, height=alto, color=c,
                          stroke_width=2.5, fill_color=FONDO, fill_opacity=1)
    pa = RoundedRectangle(corner_radius=alto * 0.04, width=alto * 0.43, height=alto * 0.72,
                          color=C_ANT, fill_color=C_ANT, fill_opacity=0.35, stroke_width=0)
    pa.shift(UP * alto * 0.03)
    bo = Dot(cu.get_bottom() + UP * alto * 0.07, radius=alto * 0.025, color=c)
    return VGroup(cu, pa, bo)


def persona(alto=0.55, color=None):
    c = color or TINTA
    r = alto * 0.32
    cuerpo = Sector(radius=r, angle=PI, start_angle=0, fill_color=c, fill_opacity=1, stroke_width=0)
    cab = Circle(radius=alto * 0.17, color=c, fill_color=c, fill_opacity=1, stroke_width=0)
    cab.next_to(cuerpo, UP, buff=alto * 0.04)
    g = VGroup(cuerpo, cab)
    return g


def torre(alto=1.4, color=None, ondas=True):
    c = color or C_ANT
    w = alto * 0.34
    g = VGroup(Line([-w / 2, 0, 0], [0, alto, 0], color=c, stroke_width=3),
               Line([w / 2, 0, 0], [0, alto, 0], color=c, stroke_width=3))
    for f in (0.25, 0.5, 0.75):
        hw = w / 2 * (1 - f)
        g.add(Line([-hw, alto * f, 0], [hw, alto * f, 0], color=c, stroke_width=2))
    top = np.array([0, alto, 0])
    g.add(Dot(top, radius=0.06, color=c))
    if ondas:
        for r in (0.2, 0.36):
            g.add(Arc(radius=r, start_angle=-40 * DEGREES, angle=80 * DEGREES, arc_center=top,
                      color=c, stroke_width=2.5))
            g.add(Arc(radius=r, start_angle=140 * DEGREES, angle=80 * DEGREES, arc_center=top,
                      color=c, stroke_width=2.5))
    return g


def ciudad(ancho=2.2):
    alturas = [0.8, 1.3, 1.0, 1.6, 0.9, 1.35, 0.7]
    n = len(alturas)
    bw = ancho / n
    g = VGroup()
    for i, h in enumerate(alturas):
        r = Rectangle(width=bw * 0.92, height=h, color=TENUE, stroke_width=1.5,
                      fill_color=C_EJE, fill_opacity=0.75)
        r.move_to([-ancho / 2 + bw * (i + 0.5), h / 2, 0])
        g.add(r)
        for j in range(int(h / 0.32)):
            v = Square(bw * 0.16, stroke_width=0, fill_color=C_SAT, fill_opacity=0.75 if (i + j) % 2 == 0 else 0.25)
            v.move_to([-ancho / 2 + bw * (i + 0.5), 0.2 + 0.3 * j, 0])
            g.add(v)
    return g


def servidor(ancho=0.8, color=None):
    c = color or C_ANT
    g = VGroup()
    for i in range(3):
        r = RoundedRectangle(corner_radius=0.05, width=ancho, height=ancho * 0.28, color=c,
                             stroke_width=2.5, fill_color=c, fill_opacity=0.25)
        r.move_to([0, (1 - i) * ancho * 0.34, 0])
        d = Dot(r.get_left() + RIGHT * ancho * 0.14, radius=0.04, color=C_OK)
        g.add(r, d)
    return g


def dirigible(ancho=1.0, color=None):
    c = color or C_CIELO
    cu = Ellipse(width=ancho, height=ancho * 0.36, color=c, fill_color=c, fill_opacity=0.35, stroke_width=2.5)
    pan = Rectangle(width=ancho * 0.5, height=ancho * 0.05, stroke_width=0, fill_color=C_SAT, fill_opacity=0.9)
    pan.move_to(cu.get_top() + DOWN * ancho * 0.03)
    cola = Polygon(cu.get_left() + RIGHT * 0.02, cu.get_left() + LEFT * ancho * 0.12 + UP * ancho * 0.15,
                   cu.get_left() + LEFT * ancho * 0.12 + DOWN * ancho * 0.15,
                   color=c, stroke_width=2, fill_color=c, fill_opacity=0.5)
    gon = Rectangle(width=ancho * 0.16, height=ancho * 0.07, color=c, stroke_width=2,
                    fill_color=c, fill_opacity=0.6).next_to(cu, DOWN, buff=-0.01)
    return VGroup(cu, pan, cola, gon)


def dron(tam=0.5, color=None):
    c = color or C_CIELO
    g = VGroup(Square(tam * 0.3, color=c, fill_color=c, fill_opacity=0.6, stroke_width=2))
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = np.array([sx * tam * 0.42, sy * tam * 0.2, 0])
            g.add(Line(ORIGIN, p, color=c, stroke_width=2))
            g.add(Ellipse(width=tam * 0.4, height=tam * 0.07, color=c, stroke_width=2,
                          fill_color=c, fill_opacity=0.5).move_to(p + UP * tam * 0.05))
    return g


def coche(esc=1.0, color=None):
    c = color or TINTA
    cu = RoundedRectangle(corner_radius=0.08, width=0.9, height=0.28, color=c, stroke_width=2.5,
                          fill_color=C_PANEL, fill_opacity=1)
    ca = Polygon([-0.25, 0, 0], [-0.15, 0.24, 0], [0.2, 0.24, 0], [0.32, 0, 0], color=c, stroke_width=2.5,
                 fill_color=C_PANEL, fill_opacity=1).next_to(cu, UP, buff=-0.01)
    ru = VGroup(*[Circle(radius=0.1, color=c, stroke_width=2.5, fill_color=FONDO, fill_opacity=1)
                  .move_to(cu.get_bottom() + np.array([sx * 0.27, 0.02, 0])) for sx in (-1, 1)])
    return VGroup(ca, cu, ru).scale(esc)


def barras_senal(n_act, x, y, n=5, ancho=0.14, sep=0.2, color=None):
    g = VGroup()
    for i in range(n):
        h = 0.14 + 0.1 * i
        on = i < n_act
        col = color if on else C_EJE
        r = Rectangle(width=ancho, height=h, stroke_width=0, fill_color=col, fill_opacity=1 if on else 0.6)
        r.move_to([x + i * sep, y - 0.3 + h / 2, 0])
        g.add(r)
    return g


# ===========================================================================
# 1. ARQUITECTURA NTN
# ===========================================================================
class ArquitecturaNTN(PiezaN):
    def construct(self):
        p_ue = np.array([-5.6, -2.0, 0]); p_sat = np.array([-1.6, 2.0, 0])
        p_gw = np.array([1.5, -2.0, 0]); p_nu = np.array([3.9, -2.0, 0]); p_in = np.array([6.2, -2.0, 0])
        estrellas_bg = estrellas(60, 4, op=0.5)
        self.add(estrellas_bg)

        ue = telefono(0.85).move_to(p_ue)
        sat = satelite(0.42).move_to(p_sat)
        gw = estacion(1.0).move_to(p_gw)
        nu = servidor(0.95).move_to(p_nu)
        net = tierra(0.5).move_to(p_in)
        l_ue = et_junto("Terminal UE", ue)
        l_sat = et_junto("Satélite", sat, UP)
        l_gw = et_junto("Gateway", gw)
        l_nu = et_junto("Núcleo", nu)
        l_net = et_junto("Internet", net)
        nodos = [(ue, l_ue), (sat, l_sat), (gw, l_gw), (nu, l_nu), (net, l_net)]
        self.play(LaggedStart(*[AnimationGroup(GrowFromCenter(n), FadeIn(l, shift=UP * 0.1))
                                for n, l in nodos], lag_ratio=0.3), run_time=3)

        a1, b1 = borde(p_ue, p_sat, 0.65), borde(p_sat, p_ue, 0.8)
        a2, b2 = borde(p_sat, p_gw, 0.75), borde(p_gw, p_sat, 0.75)
        a3, b3 = p_gw + RIGHT * 0.65, p_nu + LEFT * 0.6
        a4, b4 = p_nu + RIGHT * 0.6, p_in + LEFT * 0.6

        def enlace(a, b, col, ancho=4):
            return VGroup(Line(a, b, color=col, stroke_width=ancho * 3, stroke_opacity=0.15),
                          Line(a, b, color=col, stroke_width=ancho))
        e_serv = enlace(a1, b1, C_ANT)
        e_alim = enlace(a2, b2, C_CIELO)
        e_bh = VGroup(enlace(a3, b3, TENUE, 3), enlace(a4, b4, TENUE, 3))
        t_serv = et("servicio", 24, C_ANT).move_to((a1 + b1) / 2 + np.array([-0.95, 0.5, 0]))
        t_alim = et("alimentador", 24, C_CIELO).move_to((a2 + b2) / 2 + np.array([1.15, 0.45, 0]))
        self.play(Create(e_serv), run_time=1.0)
        self.play(FadeIn(t_serv, shift=RIGHT * 0.1), Create(e_alim), run_time=1.0)
        self.play(FadeIn(t_alim, shift=RIGHT * 0.1), Create(e_bh), run_time=1.2)

        ruta = [a1, b1, a2, b2, p_gw, b3 - RIGHT * 0.0, a4, b4]
        ruta = [a1, b1, a2, b2, a3, b3, a4, b4]
        corriente(self, ruta, C_OK, n=5, periodo=5.0)
        corriente(self, ruta, C_SAT, n=5, periodo=5.0, invertir=True)
        tag1 = et("Repetidor", 24, C_SAT).next_to(sat, RIGHT, buff=0.3)
        self.play(FadeIn(tag1), run_time=0.6)
        self.wait(4.5)

        chip = VGroup(Square(0.2, color=C_ANT, fill_color=C_ANT, fill_opacity=0.9, stroke_width=1.5))
        for k in (-1, 0, 1):
            chip.add(Line([k * 0.07, 0.1, 0], [k * 0.07, 0.16, 0], color=C_ANT, stroke_width=2))
            chip.add(Line([k * 0.07, -0.1, 0], [k * 0.07, -0.16, 0], color=C_ANT, stroke_width=2))
        chip.move_to(p_sat).set_z_index(3)
        tag2 = et("Regenerativo", 24, C_ANT).next_to(sat, RIGHT, buff=0.3)
        self.play(ReplacementTransform(tag1, tag2), FadeIn(chip, scale=0.5), run_time=1.0)
        self.play(Indicate(chip, color=C_ANT, scale_factor=1.5), run_time=1.0)
        self.wait(4.5)
        self.cierre()


# ===========================================================================
# 2. ZOOLÓGICO ORBITAL
# ===========================================================================
class ZoologicoOrbital(PiezaN):
    def construct(self):
        def Y(h):
            return -3.1 + (np.log10(h) - 1) * 6.3 / 3.7
        ex = -5.75
        suelo = Rectangle(width=14.3, height=0.55, stroke_width=0, fill_color=C_TIERRA_2, fill_opacity=1)
        suelo.move_to([0, -3.85, 0])
        borde_s = Line([-7.15, -3.575, 0], [7.15, -3.575, 0], color=C_TIERRA, stroke_width=3)
        eje = Line([ex, -3.5, 0], [ex, 3.35, 0], color=C_EJE, stroke_width=3)
        ticks = VGroup()
        for h, tx in ((10, "10"), (100, "100"), (1000, "1 000"), (10000, "10 000")):
            ticks.add(Line([ex - 0.09, Y(h), 0], [ex + 0.09, Y(h), 0], color=C_EJE, stroke_width=3))
            ticks.add(et(tx, 20, TENUE).next_to([ex - 0.13, Y(h), 0], LEFT, buff=0.06))
        unidad = et("km", 22, TENUE).move_to([ex, 3.75, 0])
        self.play(FadeIn(suelo), Create(borde_s), Create(eje), run_time=1.3)
        self.play(FadeIn(ticks), FadeIn(unidad), run_time=1.0)

        capas = [
            ("HAPS", 20, "20 km", "0,13 ms", -1.6, C_OK, lambda: dirigible(1.2)),
            ("LEO", 550, "550 km", "3,7 ms", -0.5, C_OK, lambda: satelite(0.34)),
            ("MEO", 20200, "20 200 km", "135 ms", 0.6, C_SAT, lambda: satelite(0.4)),
            ("GEO", 35786, "35 786 km", "239 ms", 1.7, C_MAL, lambda: satelite(0.46)),
        ]
        cab = et("Ida-vuelta al satélite", 22, TENUE).move_to([5.2, 3.7, 0])
        self.play(FadeIn(cab), run_time=0.5)
        dur_ping = {"HAPS": 0.5, "LEO": 0.9, "MEO": 1.8, "GEO": 2.4}
        for nom, h, alt, rtt, xi, col, icono in capas:
            y = Y(h)
            linea = DashedLine([-3.1, y, 0], [4.6, y, 0], color=C_EJE, stroke_width=2, dash_length=0.12)
            tick = Line([ex - 0.09, y, 0], [ex + 0.09, y, 0], color=TINTA, stroke_width=4)
            n = et(nom, 28, TINTA)
            n.move_to([-5.4 + n.width / 2, y, 0])
            a = et(alt, 20, TENUE)
            a.move_to([-4.3 + a.width / 2, y, 0])
            ic = icono().move_to([xi, y, 0]).set_z_index(3)
            self.play(Create(linea), FadeIn(tick), FadeIn(n), FadeIn(a), FadeIn(ic, scale=0.6), run_time=1.0)
            g0 = np.array([xi, -3.5, 0]); top = np.array([xi, y - 0.25, 0])
            punto = Dot(g0, radius=0.08, color=C_ANT).set_z_index(4)
            rastro = Line(g0, top, color=C_ANT, stroke_width=3, stroke_opacity=0.6)
            d = dur_ping[nom]
            self.add(punto)
            self.play(MoveAlongPath(punto, Line(g0, top)), Create(rastro), run_time=d / 2, rate_func=linear)
            self.play(MoveAlongPath(punto, Line(top, g0)), run_time=d / 2, rate_func=linear)
            self.play(FadeOut(punto), FadeOut(rastro), run_time=0.15)
            t = et(rtt, 30, col)
            t.move_to([6.05 - t.width / 2 - 0.0, y, 0]).shift(LEFT * 0.0)
            self.play(FadeIn(t, scale=1.2), run_time=0.5)
            self.wait(0.3)
        self.cierre()


# ===========================================================================
# 3. ESPACIO - AIRE - TIERRA
# ===========================================================================
class EspacioAireTierra(PiezaN):
    def construct(self):
        def banda(y0, y1, color, op):
            return Rectangle(width=14.3, height=y1 - y0, stroke_width=0, fill_color=color,
                             fill_opacity=op).move_to([0, (y0 + y1) / 2, 0])
        b1 = banda(1.85, 4.0, C_CIELO, 0.12)
        b2 = banda(-0.35, 1.85, C_ANT, 0.07)
        b3 = banda(-4.0, -0.35, C_TIERRA, 0.18)
        d1 = DashedLine([-7.1, 1.85, 0], [7.1, 1.85, 0], color=C_EJE, stroke_width=2)
        d2 = DashedLine([-7.1, -0.35, 0], [7.1, -0.35, 0], color=C_EJE, stroke_width=2)
        self.play(FadeIn(b1), FadeIn(b2), FadeIn(b3), Create(d1), Create(d2), run_time=1.2)
        ls = []
        for txt, y, col in (("Espacio", 3.6, C_CIELO), ("Aire", 1.45, C_ANT), ("Tierra", -0.7, TENUE)):
            t = et(txt, 24, col)
            t.move_to([-6.9 + t.width / 2, y, 0])
            ls.append(t)
        self.play(FadeIn(VGroup(*ls)), run_time=0.6)

        p_s = [np.array([-4.4, 3.0, 0]), np.array([0, 3.0, 0]), np.array([4.4, 3.0, 0])]
        sats = VGroup(*[satelite(0.3).move_to(p) for p in p_s])
        p_h = np.array([2.6, 0.85, 0]); p_d = np.array([-0.6, 0.75, 0])
        haps = dirigible(1.0).move_to(p_h)
        drn = dron(0.6).move_to(p_d)
        x_t = -3.0
        tor = torre(1.5).move_to([x_t, -2.55 + 0.75, 0])
        top_t = np.array([x_t, -1.0, 0])
        ciu = ciudad(2.0).move_to([-0.9, -2.55 + 0.75, 0])
        ciu.shift(UP * (-2.55 - ciu.get_bottom()[1]))
        self.play(LaggedStart(*[FadeIn(s, scale=0.6) for s in sats], lag_ratio=0.3), run_time=1.5)
        self.play(FadeIn(haps, shift=DOWN * 0.2), FadeIn(drn, shift=DOWN * 0.2), run_time=1.0)
        self.play(FadeIn(tor, shift=UP * 0.2), FadeIn(ciu, shift=UP * 0.2), run_time=1.0)

        # cobertura
        f_t = Polygon(*elipse_pts(x_t, -3.45, 5.4, 0.55), color=C_ANT, stroke_width=1.5,
                      fill_color=C_ANT, fill_opacity=0.22)
        f_h = Polygon(*elipse_pts(2.6, -3.45, 5.2, 0.55), color=C_CIELO, stroke_width=1.5,
                      fill_color=C_CIELO, fill_opacity=0.22)
        cono = Polygon([2.6, 0.55, 0], [0.0, -3.45, 0], [5.2, -3.45, 0], stroke_width=0,
                       fill_color=C_CIELO, fill_opacity=0.09)
        self.play(FadeIn(f_t), FadeIn(f_h), FadeIn(cono), run_time=1.0)

        enl = [
            (np.array([-3.65, 3.0, 0]), np.array([-0.75, 3.0, 0]), C_CIELO),
            (np.array([0.75, 3.0, 0]), np.array([3.65, 3.0, 0]), C_CIELO),
            (np.array([-4.3, 2.72, 0]), np.array([-3.05, -0.75, 0]), C_ANT),
            (np.array([4.3, 2.72, 0]), np.array([2.85, 1.15, 0]), C_ANT),
            (np.array([2.05, 0.85, 0]), np.array([-0.1, 0.75, 0]), C_ANT),
            (np.array([-1.1, 0.65, 0]), np.array([-2.85, -0.75, 0]), C_ANT),
            (np.array([-2.75, -1.05, 0]), np.array([-1.25, -1.5, 0]), C_ANT),
        ]
        base = VGroup(*[DashedLine(a, b, color=C_EJE, stroke_width=2, dash_length=0.1, stroke_opacity=0.6)
                        for a, b, c in enl])
        self.play(Create(base), run_time=1.0)
        for i, (a, b, c) in enumerate(enl):
            viva = Line(a, b, color=c, stroke_width=5)
            self.play(Create(viva), ShowPassingFlash(Line(a, b, color=TINTA, stroke_width=8), time_width=0.6),
                      run_time=0.55)
        self.wait(0.4)

        # usuario
        u = persona(0.85).move_to([-2.0, -3.15, 0])
        obj = [np.array([x_t, -0.95, 0]), np.array([2.6, 0.55, 0]), np.array([4.4, 2.75, 0])]
        obj_col = [C_OK, C_OK, C_OK]

        def sel():
            x = u.get_center()[0]
            return 0 if x < -0.15 else (1 if x < 5.3 else 2)
        enlace_u = always_redraw(lambda: DashedLine(u.get_center() + UP * 0.35, obj[sel()], color=C_OK,
                                                    stroke_width=4, dash_length=0.14))
        self.play(FadeIn(u, scale=0.5), run_time=0.6)
        self.add(enlace_u)
        self.play(FadeIn(enlace_u), run_time=0.4)
        self.wait(1.5)
        self.play(u.animate.move_to([2.6, -3.15, 0]), run_time=3.2, rate_func=smooth)
        self.wait(1.3)
        self.play(u.animate.move_to([5.9, -3.15, 0]), run_time=2.8, rate_func=smooth)
        self.wait(1.5)
        self.cierre()


# ===========================================================================
# 4. BEAMFORMING
# ===========================================================================
class Beamforming(PiezaN):
    def construct(self):
        W, H = 284, 160
        xs = np.linspace(-7.1, 7.1, W)
        ys = np.linspace(4, -4, H)
        X, Y = np.meshgrid(xs, ys)
        N = 8
        lam = 0.62
        k = TAU / lam
        d = lam / 2
        ex = (np.arange(N) - (N - 1) / 2) * d
        ay = 2.75
        Ri = [np.sqrt((X - x) ** 2 + (Y - ay) ** 2) for x in ex]
        inv = [(1 / np.sqrt(np.maximum(r, 0.35))) * np.clip((ay - Y) / np.maximum(r, 1e-3), 0, 1) ** 1.5 for r in Ri]
        mask = (Y < ay - 0.05).astype(float)
        near = np.clip((np.minimum.reduce(Ri) - 0.15) / 0.5, 0, 1)
        c1 = np.array(ManimColor(C_ANT).to_rgb()) * 255
        c2 = np.array(ManimColor(C_CIELO).to_rgb()) * 255

        ang = ValueTracker(0.0)      # rad, respecto a la vertical hacia abajo
        gain = ValueTracker(0.0)
        est = {"t": 0.0}

        def campo():
            th = ang.get_value()
            f = np.zeros_like(X)
            for i in range(N):
                f += np.cos(k * Ri[i] - 5.0 * est["t"] + k * ex[i] * np.sin(th)) * inv[i]
            f = f / N * 3.4
            a = np.clip(np.abs(f), 0, 1) ** 1.9 * 1.0 * mask * near * gain.get_value()
            arr = np.zeros((H, W, 4))
            pos = (f > 0)[..., None]
            arr[..., :3] = np.where(pos, c1, c2)
            arr[..., 3] = a * 255
            return arr.astype(np.uint8)

        img = ImageMobject(campo())
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
        img.stretch_to_fit_width(14.2).stretch_to_fit_height(8).move_to(ORIGIN).set_z_index(-2)

        def upd(m, dt):
            est["t"] += dt
            m.pixel_array = campo()
        img.add_updater(upd)
        self.add(img)

        suelo = Rectangle(width=14.3, height=0.45, stroke_width=0, fill_color=C_TIERRA_2, fill_opacity=0.9)
        suelo.move_to([0, -3.85, 0])
        linea_s = Line([-7.15, -3.625, 0], [7.15, -3.625, 0], color=C_TIERRA, stroke_width=3)
        elem = VGroup(*[VGroup(Line([x, ay, 0], [x, ay + 0.2, 0], color=C_ANT, stroke_width=3),
                               Dot([x, ay, 0], radius=0.08, color=C_ANT)) for x in ex])
        base_arr = Line([ex[0] - 0.25, ay + 0.2, 0], [ex[-1] + 0.25, ay + 0.2, 0], color=C_ANT, stroke_width=4)
        ux = [-4.6, 0.0, 4.6]
        uy = -3.05
        th_u = [np.arctan2(x, ay - uy) for x in ux]
        users = []
        for x, tu in zip(ux, th_u):
            u = persona(0.8, TENUE).move_to([x, uy, 0])

            def col(m, tu=tu):
                m.set_color(C_OK if abs(ang.get_value() - tu) < 7 * DEGREES else TENUE)
            u.add_updater(col)
            users.append(u)
        self.play(FadeIn(suelo), Create(linea_s), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(e, shift=DOWN * 0.15) for e in elem], lag_ratio=0.12), Create(base_arr),
                  run_time=1.6)
        self.play(*[FadeIn(u, shift=UP * 0.15) for u in users], run_time=0.8)

        barras = always_redraw(lambda: VGroup(*[
            Line([x, ay + 0.32, 0], [x, ay + 0.32 + 0.28 + 0.24 * (x * np.sin(ang.get_value()) / ex[-1]), 0],
                 color=C_CIELO, stroke_width=6) for x in ex]))
        self.play(FadeIn(barras), run_time=0.5)

        # patrón polar
        cp = np.array([5.4, 3.05, 0])
        rp = 1.2
        panel = Sector(radius=rp + 0.15, start_angle=PI, angle=PI, fill_color=FONDO, fill_opacity=0.9,
                       stroke_color=C_EJE, stroke_width=2).move_to(cp, aligned_edge=UP).set_z_index(1)
        panel.shift(np.array([0, 0, 0]))
        panel.move_to([cp[0], cp[1] - (rp + 0.15) / 2, 0])
        anillos = VGroup(*[Arc(radius=rp * f, start_angle=PI, angle=PI, arc_center=cp, color=C_EJE, stroke_width=1.5)
                           for f in (0.5, 1.0)]).set_z_index(2)

        def lobulo():
            th = ang.get_value()
            ph = np.linspace(-PI / 2, PI / 2, 181)
            psi = k * d * (np.sin(ph) - np.sin(th))
            den = N * np.sin(psi / 2)
            af = np.where(np.abs(den) < 1e-6, 1.0, np.abs(np.sin(N * psi / 2) / np.where(np.abs(den) < 1e-6, 1, den)))
            pts = [cp + rp * a * np.array([np.sin(p), -np.cos(p), 0]) for a, p in zip(af, ph)]
            return Polygon(*pts, color=C_ANT, stroke_width=3, fill_color=C_ANT, fill_opacity=0.35).set_z_index(3)
        lob = always_redraw(lobulo)
        self.play(FadeIn(panel), FadeIn(anillos), run_time=0.6)
        self.add(lob)
        self.play(gain.animate.set_value(1.0), run_time=1.5)
        self.wait(2.0)
        for objetivo in (th_u[0], th_u[2], th_u[1]):
            self.play(ang.animate.set_value(objetivo), run_time=2.6, rate_func=smooth)
            self.wait(1.4)
        self.play(gain.animate.set_value(0.0), run_time=0.6)
        self.remove(img)
        self.cierre()


# ===========================================================================
# 5. PRESUPUESTO DE ENLACE
# ===========================================================================
class PresupuestoEnlace(PiezaN):
    def construct(self):
        self.add(et("Ejemplo Ka LEO", 20, TENUE).to_corner(UR, buff=0.4))
        def Y(L):
            return 1.1 + 0.03 * L
        xs = [-4.8, -2.4, 0.0, 2.4, 4.8]
        bw = 1.3
        base = DashedLine([-6.6, Y(0), 0], [6.6, Y(0), 0], color=C_EJE, stroke_width=2)
        l0 = et("0 dBW", 20, TENUE).move_to([-6.05, Y(0) + 0.22, 0])
        self.play(Create(base), FadeIn(l0), run_time=1.0)

        def fmt(v):
            r = int(round(abs(v)))
            return ("+" if v >= 0 else "−") + str(r) + " dB"

        tramos = [("PIRE", 0, 50, C_SAT), ("Espacio libre", 50, -124, C_MAL),
                  ("Atmósfera", -124, -126, C_MAL), ("Ganancia Rx", -126, -91, C_ANT)]
        for i, (nom, a, b, col) in enumerate(tramos):
            s = ValueTracker(0)

            def rect(i=i, a=a, b=b, col=col, s=s):
                e = a + (b - a) * s.get_value()
                y0, y1 = Y(a), Y(e)
                h = max(abs(y1 - y0), 0.02)
                return Rectangle(width=bw, height=h, fill_color=col, fill_opacity=0.85, stroke_color=col,
                                 stroke_width=3).move_to([xs[i], (y0 + y1) / 2, 0])

            def num(i=i, a=a, b=b, col=col, s=s):
                if s.get_value() < 0.03:
                    return VMobject()
                e = a + (b - a) * s.get_value()
                t = et(fmt((b - a) * s.get_value()), 26, col)
                yy = Y(e) + (0.3 if b > a else -0.3)
                return t.move_to([xs[i], yy, 0])
            r = always_redraw(rect)
            n = always_redraw(num)
            nombre = et(nom, 22, TINTA).move_to([xs[i], -3.55, 0])
            self.add(r, n)
            self.play(FadeIn(nombre, shift=UP * 0.1), s.animate.set_value(1.0),
                      run_time=1.6 if i != 2 else 1.0, rate_func=smooth)
            if i < 3:
                self.play(Create(DashedLine([xs[i] + bw / 2, Y(b), 0], [xs[i + 1] - bw / 2, Y(b), 0],
                                            color=TENUE, stroke_width=2)), run_time=0.4)
            self.wait(0.3)

        # ruido y margen
        self.play(Create(DashedLine([xs[3] + bw / 2, Y(-91), 0], [xs[4] - bw / 2, Y(-91), 0], color=TENUE,
                                    stroke_width=2)), run_time=0.4)
        ruido = DashedLine([-6.6, Y(-122), 0], [6.6, Y(-122), 0], color=C_MAL, stroke_width=3)
        l_r = et("Ruido", 22, C_MAL).move_to([6.2, Y(-122) - 0.28, 0])
        self.play(Create(ruido), FadeIn(l_r), run_time=1.5)
        umbral = Rectangle(width=bw, height=Y(-112) - Y(-122), stroke_width=0, fill_color=C_MAL,
                           fill_opacity=0.35).move_to([xs[4], (Y(-112) + Y(-122)) / 2, 0])
        margen = Rectangle(width=bw, height=Y(-91) - Y(-112), stroke_color=C_OK, stroke_width=3,
                           fill_color=C_OK, fill_opacity=0.85).move_to([xs[4], (Y(-91) + Y(-112)) / 2, 0])
        nom5 = et("Margen", 22, TINTA).move_to([xs[4], -3.55, 0])
        val = et("21 dB", 30, C_OK).move_to([xs[4], Y(-91) + 0.32, 0])
        self.play(FadeIn(umbral), GrowFromEdge(margen, DOWN), FadeIn(nom5), run_time=1.3)
        self.play(FadeIn(val, scale=1.3), run_time=0.6)
        self.play(Indicate(margen, color=C_OK, scale_factor=1.08), run_time=1.0)
        self.cierre()


# ===========================================================================
# 6. PÉRDIDA EN ESPACIO LIBRE
# ===========================================================================
class PerdidaEspacioLibre(PiezaN):
    def construct(self):
        src = np.array([-6.0, 1.6, 0])
        dd = 1.4
        ang = 16 * DEGREES
        sat = satelite(0.28).move_to(src + LEFT * 0.0).set_z_index(4)
        sat.move_to(src)
        c1 = Line(src, src + 4.6 * np.array([np.cos(ang), np.sin(ang), 0]), color=C_SAT, stroke_width=2, stroke_opacity=0.7)
        c2 = Line(src, src + 4.6 * np.array([np.cos(ang), -np.sin(ang), 0]), color=C_SAT, stroke_width=2, stroke_opacity=0.7)
        self.play(FadeIn(sat, scale=0.6), Create(c1), Create(c2), run_time=1.2)

        T = ValueTracker(0)
        T.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(T)
        Rmax = 4.5

        def ondas():
            g = VGroup()
            for j in range(6):
                r = (T.get_value() * 1.1 + j * Rmax / 6) % Rmax
                if r < 0.5:
                    continue
                op = min(1, (r - 0.5) * 2) * (1 - r / Rmax) ** 0.5
                g.add(Arc(radius=r, start_angle=-ang, angle=2 * ang, arc_center=src, color=C_SAT,
                          stroke_width=3, stroke_opacity=op))
            return g
        self.add(always_redraw(ondas))
        self.wait(1.5)

        # cáscaras
        pos = []
        for m in (1, 2, 3):
            arco = Arc(radius=dd * m, start_angle=-ang, angle=2 * ang, arc_center=src, color=C_CIELO,
                       stroke_width=4)
            pos.append(arco)
        etq = []
        for m, arco in zip((1, 2, 3), pos):
            t = et("d" if m == 1 else f"{m}d", 22, C_CIELO)
            t.move_to(arco.get_bottom() + DOWN * 0.3)
            etq.append(t)
        self.play(LaggedStart(*[AnimationGroup(Create(a), FadeIn(t)) for a, t in zip(pos, etq)],
                              lag_ratio=0.5), run_time=2.5)

        # parches
        lado = 0.8
        yc = -1.5
        centros = [-5.2, -3.3, -1.15]
        ops = [0.95, 0.4, 0.2]
        parches = []
        for m, cx, op in zip((1, 2, 3), centros, ops):
            gr = VGroup()
            for i in range(m):
                for j in range(m):
                    c = Square(lado, stroke_color=TINTA, stroke_width=1.5, stroke_opacity=0.5,
                               fill_color=C_SAT, fill_opacity=op)
                    c.move_to([cx + (i - (m - 1) / 2) * lado, yc + (j - (m - 1) / 2) * lado, 0])
                    gr.add(c)
            parches.append(gr)
        guias = VGroup(*[DashedLine(a.get_bottom() + DOWN * 0.7 if False else a.get_top() * 0 + np.array([a.get_center()[0] if False else 0, 0, 0]), ORIGIN)
                         for a in []])
        for m, (arco, cx, gr, op) in enumerate(zip(pos, centros, parches, ops)):
            gu = DashedLine(etq[m].get_bottom() + DOWN * 0.05, [cx, yc + lado * (m + 1) / 2 + 0.05, 0],
                            color=C_EJE, stroke_width=2, dash_length=0.1)
            factor = et(f"×{(m + 1) ** 2}", 26, TINTA).move_to([cx, -3.35, 0])
            self.play(Create(gu), FadeIn(gr, scale=0.85), FadeIn(factor), run_time=1.3)
        self.wait(1.0)

        # panel derecho: curva de pérdida
        ox, oy = 1.6, -2.8
        def PX(lg):
            return ox + (lg - 2) / 3 * 4.6

        def PY(L):
            return oy + (L - 110) / 90 * 5.6
        ejex = Line([ox, oy, 0], [6.3, oy, 0], color=C_EJE, stroke_width=3)
        ejey = Line([ox, oy, 0], [ox, 3.1, 0], color=C_EJE, stroke_width=3)
        ticks = VGroup()
        for lg, tx in ((2, "100"), (3, "1 000"), (4, "10 000"), (5, "100 000")):
            ticks.add(et(tx, 20, TENUE).move_to([PX(lg), oy - 0.3, 0]))
            ticks.add(Line([PX(lg), oy, 0], [PX(lg), oy + 0.09, 0], color=C_EJE, stroke_width=3))
        for L in (120, 160, 200):
            ticks.add(et(str(L), 20, TENUE).next_to([ox - 0.05, PY(L), 0], LEFT, buff=0.1))
            ticks.add(Line([ox, PY(L), 0], [ox + 0.09, PY(L), 0], color=C_EJE, stroke_width=3))
        u1 = et("km", 22, TENUE).move_to([6.55, oy + 0.0, 0])
        u2 = et("dB", 22, TENUE).move_to([ox + 0.05, 3.4, 0])
        u3 = et("2 GHz", 22, C_ANT).move_to([3.0, 2.6, 0])
        self.play(Create(ejex), Create(ejey), FadeIn(ticks), FadeIn(u1), FadeIn(u2), FadeIn(u3), run_time=1.5)

        def fspl(dkm):
            return 98.47 + 20 * np.log10(dkm)
        curva = ParametricFunction(lambda t: np.array([PX(t), PY(fspl(10 ** t)), 0]), t_range=[2, 4.7],
                                   color=C_MAL, stroke_width=5)
        self.play(Create(curva), run_time=2.5, rate_func=smooth)
        puntos = [("LEO", 550, "153 dB", (0.55, -0.35)), ("MEO", 20200, "185 dB", (-0.95, 0.0)),
                  ("GEO", 35786, "190 dB", (0.0, 0.5))]
        for nom, dkm, txt, off in puntos:
            p = np.array([PX(np.log10(dkm)), PY(fspl(dkm)), 0])
            dot = Dot(p, radius=0.11, color=C_SAT).set_z_index(5)
            gv = DashedLine([p[0], oy, 0], p, color=C_EJE, stroke_width=2, dash_length=0.1)
            gh = DashedLine([ox, p[1], 0], p, color=C_EJE, stroke_width=2, dash_length=0.1)
            t = et(f"{nom} {txt}", 24, TINTA)
            if nom == "LEO":
                t.move_to(p + np.array([t.width / 2 + 0.25, -0.35, 0]))
            elif nom == "MEO":
                t.move_to(p + np.array([-t.width / 2 - 0.25, -0.15, 0]))
            else:
                t.move_to(p + np.array([-0.1, 0.5, 0]))
            self.play(Create(gv), Create(gh), FadeIn(dot, scale=2), FadeIn(t), run_time=1.0)
        self.cierre()


# ===========================================================================
# 7. HANDOVER TERRESTRE - NTN
# ===========================================================================
class HandoverTerrestreNTN(PiezaN):
    def construct(self):
        self.add(estrellas(40, 9, op=0.4))
        y_suelo = -2.55
        xA, xB = -4.2, 4.2
        R = 3.0
        carretera = VGroup(Rectangle(width=14.3, height=0.5, stroke_width=0, fill_color=C_EJE, fill_opacity=0.9)
                           .move_to([0, -2.95, 0]),
                           DashedLine([-7.1, -2.95, 0], [7.1, -2.95, 0], color=TINTA, stroke_width=2,
                                      dash_length=0.25, stroke_opacity=0.6))
        base_t = Rectangle(width=14.3, height=1.0, stroke_width=0, fill_color=C_TIERRA_2, fill_opacity=0.9)
        base_t.move_to([0, -3.5, 0]).set_z_index(-1)
        tA = torre(1.5).move_to([xA, y_suelo + 0.75, 0])
        tB = torre(1.5).move_to([xB, y_suelo + 0.75, 0])
        domA = Polygon(*elipse_pts(xA, y_suelo, 2 * R, 2.3, 80, mitad=True), color=C_ANT, stroke_width=2,
                       stroke_opacity=0.6, fill_color=C_ANT, fill_opacity=0.10)
        domB = Polygon(*elipse_pts(xB, y_suelo, 2 * R, 2.3, 80, mitad=True), color=C_ANT, stroke_width=2,
                       stroke_opacity=0.6, fill_color=C_ANT, fill_opacity=0.10)
        self.play(FadeIn(base_t), FadeIn(carretera), run_time=0.8)
        self.play(FadeIn(tA, shift=UP * 0.2), FadeIn(tB, shift=UP * 0.2), FadeIn(domA), FadeIn(domB), run_time=1.4)

        xv = ValueTracker(-6.2)
        sat_x = lambda: 0.2 * xv.get_value()
        y_sat = 2.3
        sat = satelite(0.34).set_z_index(4)
        sat.add_updater(lambda m: m.move_to([sat_x(), y_sat, 0]))
        cono = always_redraw(lambda: Polygon(
            [sat_x(), y_sat - 0.25, 0], [sat_x() - R, -2.85, 0], [sat_x() + R, -2.85, 0],
            stroke_width=0, fill_color=C_SAT, fill_opacity=0.08))
        huella = always_redraw(lambda: Polygon(*elipse_pts(sat_x(), -2.85, 2 * R, 0.5), color=C_SAT,
                                               stroke_width=2, stroke_opacity=0.6, fill_color=C_SAT,
                                               fill_opacity=0.15))
        self.play(FadeIn(sat, shift=DOWN * 0.3), run_time=0.6)
        self.play(FadeIn(cono), FadeIn(huella), run_time=0.8)

        car = coche(1.35)
        car.add_updater(lambda m: m.move_to([xv.get_value(), -2.5, 0]).set_z_index(5))
        self.play(FadeIn(car, shift=RIGHT * 0.3), run_time=0.6)

        def ss(a, b, x):
            t = np.clip((x - a) / (b - a), 0, 1)
            return t * t * (3 - 2 * t)

        def pesos(x):
            w1 = ss(-2.7, -2.1, x)
            w2 = ss(2.1, 2.7, x)
            return 1 - w1, w1 * (1 - w2), w2

        def senal(x):
            sA = max(0, 1 - abs(x - xA) / R)
            sS = max(0, 1 - abs(x - sat_x()) / R)
            sB = max(0, 1 - abs(x - xB) / R)
            wa, ws, wb = pesos(x)
            return wa * sA + ws * sS + wb * sB

        def enlaces():
            x = xv.get_value()
            wa, ws, wb = pesos(x)
            o = np.array([x, -2.1, 0])
            g = VGroup()
            for w, p, c in ((wa, np.array([xA, -1.05, 0]), C_ANT), (ws, np.array([sat_x(), y_sat - 0.25, 0]), C_SAT),
                            (wb, np.array([xB, -1.05, 0]), C_ANT)):
                if w > 0.03:
                    g.add(DashedLine(o, p, color=c, stroke_width=5, dash_length=0.16, stroke_opacity=min(1, w * 1.3)))
            return g
        self.add(always_redraw(enlaces))

        # indicador
        panel = RoundedRectangle(corner_radius=0.15, width=3.5, height=1.2, color=C_EJE, stroke_width=2,
                                 fill_color=C_PANEL, fill_opacity=0.9).move_to([-5.15, 3.2, 0])
        self.play(FadeIn(panel), run_time=0.5)

        def bars():
            s = senal(xv.get_value())
            n = int(np.ceil(s * 5 - 1e-6))
            col = C_OK if s > 0.5 else C_SAT
            return barras_senal(n, -6.5, 3.2, color=col)
        self.add(always_redraw(bars))

        def luces():
            s = senal(xv.get_value())
            act = 2 if s > 0.5 else (1 if s > 0.22 else 0)
            g = VGroup()
            for i, c in enumerate((C_MAL, C_SAT, C_OK)):
                g.add(Circle(radius=0.17, color=c, stroke_width=2, fill_color=c,
                             fill_opacity=1 if i == act else 0.12).move_to([-4.85 + 0.48 * i, 3.2, 0]))
            return g
        self.add(always_redraw(luces))

        self.play(xv.animate.set_value(6.2), run_time=17, rate_func=linear)
        self.cierre()


# ===========================================================================
# 8. MODULACIÓN
# ===========================================================================
class Modulacion(PiezaN):
    def construct(self):
        bits = [1, 0, 1, 1, 0]
        x0, bw = -6.4, 1.72
        cpb = 3
        yc, yb, ym = 2.3, 0.1, -2.3
        amp = 0.6
        npt = 90

        def seg(k, y, a, fase):
            tt = np.linspace(0, bw, npt)
            pts = [np.array([x0 + k * bw + t, y + a * np.cos(TAU * cpb * t / bw + fase), 0]) for t in tt]
            return VMobject(color=C_ANT, stroke_width=4).set_points_smoothly(pts)

        # portadora
        l_p = et("portadora", 24, TENUE).move_to([x0 + 0.65, yc + 0.95, 0])
        port = ParametricFunction(lambda t: np.array([x0 + t, yc + amp * np.cos(TAU * cpb * t / bw), 0]),
                                  t_range=[0, 5 * bw, 0.02], color=C_ANT, stroke_width=4)
        self.play(FadeIn(l_p), Create(port), run_time=3, rate_func=linear)
        self.wait(0.5)

        # bits
        l_b = et("bits", 24, TENUE).move_to([x0 + 0.3, yb + 0.9, 0])
        hi, lo = yb + 0.4, yb - 0.4
        guias = VGroup(*[DashedLine([x0 + k * bw, yc + 0.85, 0], [x0 + k * bw, ym - 0.7, 0], color=C_EJE,
                                    stroke_width=1.5, dash_length=0.1, stroke_opacity=0.7) for k in range(1, 6)])
        self.play(FadeIn(l_b), FadeIn(guias), run_time=0.8)
        pts = []
        nivel = lambda b: hi if b else lo
        pts.append(np.array([x0, nivel(bits[0]), 0]))
        for k, b in enumerate(bits):
            if k > 0 and bits[k - 1] != b:
                pts.append(np.array([x0 + k * bw, nivel(bits[k - 1]), 0]))
            pts.append(np.array([x0 + k * bw, nivel(b), 0]))
            pts.append(np.array([x0 + (k + 1) * bw, nivel(b), 0]))
        pts = [pts[0]] + [p for i, p in enumerate(pts[1:], 1) if not np.allclose(p, pts[i - 1])]
        onda_b = VMobject(color=C_SAT, stroke_width=5).set_points_as_corners(pts)
        digs = VGroup(*[et(str(b), 30, C_SAT).move_to([x0 + (k + 0.5) * bw, yb - 0.85, 0]) for k, b in enumerate(bits)])
        self.play(Create(onda_b), LaggedStart(*[FadeIn(dg, shift=UP * 0.1) for dg in digs], lag_ratio=0.8),
                  run_time=3.5, rate_func=linear)
        self.wait(0.4)

        # ASK
        cursor = Rectangle(width=bw, height=6.6, stroke_width=0, fill_color=C_PANEL, fill_opacity=0.55)
        cursor.move_to([x0 + bw / 2, 0, 0]).set_z_index(-1)
        l_m = et("ASK", 24, TENUE).move_to([x0 + 0.4, ym + 0.95, 0])
        ask = [seg(k, ym, amp if b else 0.18, 0) for k, b in enumerate(bits)]
        self.play(FadeIn(cursor), FadeIn(l_m), run_time=0.4)
        for k in range(5):
            anims = [Create(ask[k], rate_func=linear)]
            if k > 0:
                anims.append(cursor.animate.move_to([x0 + (k + 0.5) * bw, 0, 0]))
            self.play(*anims, run_time=0.85)
        self.play(FadeOut(cursor), run_time=0.4)
        self.wait(0.5)

        # PSK
        psk = [seg(k, ym, amp, 0 if b else PI) for k, b in enumerate(bits)]
        l_m2 = et("PSK", 24, TENUE).move_to(l_m)
        self.play(ReplacementTransform(l_m, l_m2), *[Transform(a, p) for a, p in zip(ask, psk)], run_time=2.5)
        self.wait(1.0)

        # constelación QPSK
        cx, cy, rr = 4.85, 0.0, 1.25
        ejeI = Arrow([cx - 1.75, cy, 0], [cx + 1.75, cy, 0], buff=0, color=C_EJE, stroke_width=3,
                     tip_length=0.18)
        ejeQ = Arrow([cx, cy - 1.75, 0], [cx, cy + 1.75, 0], buff=0, color=C_EJE, stroke_width=3, tip_length=0.18)
        lI = et("I", 26, TINTA).move_to([cx + 2.05, cy, 0])
        lQ = et("Q", 26, TINTA).move_to([cx, cy + 2.05, 0])
        circ = DashedVMobject(Circle(radius=rr, color=C_EJE, stroke_width=2).move_to([cx, cy, 0]), num_dashes=40)
        self.play(Create(ejeI), Create(ejeQ), FadeIn(lI), FadeIn(lQ), Create(circ), run_time=1.5)
        s2 = rr / np.sqrt(2)
        simb = [("00", (1, 1)), ("01", (-1, 1)), ("11", (-1, -1)), ("10", (1, -1))]
        pd = {}
        for nom, (sx, sy) in simb:
            p = np.array([cx + sx * s2, cy + sy * s2, 0])
            dot = Dot(p, radius=0.12, color=C_SAT).set_z_index(3)
            rad = Line([cx, cy, 0], p, color=C_SAT, stroke_width=3, stroke_opacity=0.6)
            t = et(nom, 22, TENUE).move_to(p + np.array([sx * 0.42, sy * 0.3, 0]))
            pd[nom] = dot
            self.play(Create(rad), FadeIn(dot, scale=2), FadeIn(t), run_time=0.8)
        for nom in ("10", "11", "00"):
            self.play(Indicate(pd[nom], color=C_OK, scale_factor=2.2), run_time=0.9)
        self.cierre()


# ===========================================================================
# 9. INTERFERENCIA
# ===========================================================================
class Interferencia(PiezaN):
    def construct(self):
        self.add(estrellas(50, 3, op=0.45))
        yg = -3.05
        hg = 0.7
        sA = np.array([-3.1, 2.6, 0]); sB = np.array([3.1, 2.6, 0])
        suelo = Rectangle(width=14.3, height=1.0, stroke_width=0, fill_color=C_TIERRA_2, fill_opacity=0.9)
        suelo.move_to([0, -3.5, 0]).set_z_index(-2)
        linea_s = Line([-7.15, -3.0, 0], [7.15, -3.0, 0], color=C_TIERRA, stroke_width=0)
        cA = ValueTracker(-3.0); cB = ValueTracker(3.0)
        wA = ValueTracker(4.8); wB = ValueTracker(4.8)
        gB = ValueTracker(0.5)     # separación de arcos (longitud de onda) de B
        T = ValueTracker(0)
        T.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(T)

        def semi(c, w, x):
            u = np.clip(1 - ((x - c) / (w / 2)) ** 2, 0, 1)
            return hg / 2 * np.sqrt(u)

        satA = satelite(0.3, color=C_SAT).move_to(sA).set_z_index(4)
        satB = satelite(0.3, color=C_CIELO).move_to(sB).set_z_index(4)
        self.play(FadeIn(suelo), FadeIn(satA, shift=DOWN * 0.3), FadeIn(satB, shift=DOWN * 0.3), run_time=1.2)

        def huella(c, w, col):
            return Polygon(*elipse_pts(c.get_value(), yg, w.get_value(), hg), color=col, stroke_width=2.5,
                           fill_color=col, fill_opacity=0.22)

        def cono(s, c, w, col):
            return Polygon(s + DOWN * 0.25, [c.get_value() - w.get_value() / 2, yg, 0],
                           [c.get_value() + w.get_value() / 2, yg, 0], stroke_width=0, fill_color=col,
                           fill_opacity=0.08)

        def ondas(s, c, w, col, gap):
            g = VGroup()
            centro = np.array([c.get_value(), yg, 0])
            dist = np.linalg.norm(centro - s)
            aL = np.arctan2(*(np.array([c.get_value() - w.get_value() / 2, yg]) - s[:2])[::-1])
            aR = np.arctan2(*(np.array([c.get_value() + w.get_value() / 2, yg]) - s[:2])[::-1])
            a0, a1 = min(aL, aR), max(aL, aR)
            L = dist + 0.3
            gp = gap()
            n = int(L / gp) + 1
            for j in range(n):
                r = (T.get_value() * 1.0 + j * gp) % (n * gp)
                if r < 0.4 or r > L:
                    continue
                op = min(1, (r - 0.4) * 2) * (1 - 0.5 * r / L)
                g.add(Arc(radius=r, start_angle=a0, angle=a1 - a0, arc_center=s, color=col, stroke_width=3,
                          stroke_opacity=op))
            return g

        hA = always_redraw(lambda: huella(cA, wA, C_SAT))
        hB = always_redraw(lambda: huella(cB, wB, C_CIELO))
        kA = always_redraw(lambda: cono(sA, cA, wA, C_SAT))
        kB = always_redraw(lambda: cono(sB, cB, wB, C_CIELO))
        oA = always_redraw(lambda: ondas(sA, cA, wA, C_SAT, lambda: 0.5))
        oB = always_redraw(lambda: ondas(sB, cB, wB, C_CIELO, lambda: gB.get_value()))

        def overlap_pts():
            l = max(cA.get_value() - wA.get_value() / 2, cB.get_value() - wB.get_value() / 2)
            r = min(cA.get_value() + wA.get_value() / 2, cB.get_value() + wB.get_value() / 2)
            return l, r

        def lente():
            l, r = overlap_pts()
            if r - l < 0.08:
                return VMobject()
            xs = np.linspace(l, r, 40)
            hh = [min(semi(cA.get_value(), wA.get_value(), x), semi(cB.get_value(), wB.get_value(), x)) for x in xs]
            top = [np.array([x, yg + h, 0]) for x, h in zip(xs, hh)]
            bot = [np.array([x, yg - h, 0]) for x, h in zip(xs[::-1], hh[::-1])]
            op = 0.55 + 0.2 * np.sin(T.get_value() * 6)
            return Polygon(*(top + bot), stroke_width=0, fill_color=C_MAL, fill_opacity=op).set_z_index(2)

        def hexa():
            l, r = overlap_pts()
            malo = (r - l) > 0.6
            c = C_MAL if malo else C_OK
            h = RegularPolygon(6, color=c, stroke_width=5, fill_color=c, fill_opacity=0.3)
            h.stretch_to_fit_width(1.5).stretch_to_fit_height(0.62).move_to([0, yg, 0]).set_z_index(3)
            return h
        celda = always_redraw(hexa)
        usuario = persona(0.5, TINTA).move_to([0, yg + 0.3, 0]).set_z_index(5)

        self.play(FadeIn(celda), FadeIn(usuario, scale=0.6), run_time=0.8)
        self.add(kA, kB, oA, oB)
        self.play(FadeIn(hA), FadeIn(hB), run_time=1.0)
        self.wait(2.0)
        # los haces se acercan y se solapan sobre la celda
        lz = always_redraw(lente)
        self.play(cA.animate.set_value(-1.1), cB.animate.set_value(1.1), run_time=3.0, rate_func=smooth)
        self.add(lz)
        self.wait(3.2)
        # coordinación
        arco = ArcBetweenPoints(sA + UP * 0.35 + RIGHT * 0.3, sB + UP * 0.35 + LEFT * 0.3, angle=-PI / 6)
        coord = DashedVMobject(arco, num_dashes=24).set_color(C_OK)
        coord.set_stroke(width=4)
        self.play(Create(coord), run_time=1.2)
        corriente(self, [arco.point_from_proportion(t) for t in np.linspace(0, 1, 30)], C_OK, n=3, periodo=2.0)
        self.play(cA.animate.set_value(-1.0), cB.animate.set_value(3.3), wA.animate.set_value(3.6),
                  wB.animate.set_value(3.6), gB.animate.set_value(0.8), run_time=3.5, rate_func=smooth)
        self.wait(3.5)
        self.cierre()

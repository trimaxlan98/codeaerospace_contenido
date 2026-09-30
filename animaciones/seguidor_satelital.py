"""Seguidor satelital (sistema ATP) - piezas ilustrativas Co.De Aerospace.

Escenas: VistaPolarPase, CadenaTLEaAntena, AntenaSiguiendo, MontajeAzEl,
LazoPID, Keyhole, DopplerEnS, GemeloDigitalATP, NochePases.
"""
from types import SimpleNamespace
from code_lib import *

ROSA = "#F472B6" if OSCURO else "#DB2777"
AZUL = "#60A5FA" if OSCURO else "#2563EB"

MU = 398600.4418   # km^3/s^2
RT = 6371.0        # km


# =====================================================================
#  Geometría de pases (esfera terrestre, órbita circular)
# =====================================================================
def _beta(elmax, alt):
    r = RT + alt

    def em(b):
        up = r * np.cos(b) - RT
        d = np.sqrt(r * r + RT * RT - 2 * r * RT * np.cos(b))
        return np.degrees(np.arcsin(up / d))
    if elmax >= 89.99:
        return 0.0
    lo, hi = 0.0, np.arccos(RT / r) - 1e-6
    for _ in range(60):
        mid = (lo + hi) / 2
        if em(mid) > elmax:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def pase(elmax, az0=0.0, lado=1, alt=550.0, n=500, inv=False, ventana=None):
    """Pase de un LEO circular. az/el en grados, t en s desde el inicio."""
    r = RT + alt
    b = _beta(elmax, alt) * lado
    w = np.sqrt(MU / r ** 3)
    if ventana:
        th = np.linspace(-ventana * w, ventana * w, n)
    else:
        th0 = np.arccos(RT / (r * np.cos(b)))
        th = np.linspace(-th0, th0, n)
    e = r * np.sin(th)
    nn = -r * np.sin(b) * np.cos(th)
    up = r * np.cos(th) * np.cos(b) - RT
    el = np.degrees(np.arctan2(up, np.hypot(e, nn)))
    az = np.degrees(np.unwrap(np.arctan2(e, nn))) + az0
    t = (th - th[0]) / w
    if inv:
        az, el, t = az[::-1], el[::-1], t[-1] - t[::-1]
    return SimpleNamespace(az=az, el=el, t=t, tca=int(np.argmax(el)), w=w,
                           dur=t[-1])


class Polar:
    """Gráfico polar de cielo: cenit al centro, horizonte en el anillo."""

    def __init__(self, centro, R):
        self.c = np.array([centro[0], centro[1], 0.0])
        self.R = R

    def p(self, az, el):
        r = self.R * (90 - el) / 90
        a = np.radians(az)
        return self.c + np.array([r * np.sin(a), r * np.cos(a), 0.0])

    def pts(self, az, el):
        r = self.R * (90 - np.asarray(el)) / 90
        a = np.radians(np.asarray(az))
        return np.stack([self.c[0] + r * np.sin(a), self.c[1] + r * np.cos(a),
                         np.zeros_like(r)], axis=1)

    def fondo(self, etiquetas_anillo=True, tam=26, ang_lbl=315):
        R = self.R
        disco = Circle(radius=R, color=C_EJE, stroke_width=3, fill_color=C_PANEL,
                       fill_opacity=0.45).move_to(self.c)
        anillos = VGroup(*[
            Circle(radius=R * (90 - e) / 90, color=C_EJE, stroke_width=1.6,
                   stroke_opacity=0.9).move_to(self.c) for e in (30, 60)])
        radios = VGroup(
            Line(self.p(0, 0), self.p(180, 0), color=C_EJE, stroke_width=1.3),
            Line(self.p(90, 0), self.p(270, 0), color=C_EJE, stroke_width=1.3))
        radios.set_stroke(opacity=0.8)
        centro = Dot(self.c, radius=0.045, color=TENUE)
        lbl = VGroup()
        for az, tx in ((0, "N"), (90, "E"), (180, "S"), (270, "O")):
            lbl.add(et(tx, tam, TINTA).move_to(self.p(az, 0) + (self.p(az, 0) - self.c) / R * 0.36))
        if etiquetas_anillo:
            for e in (30, 60):
                t = et(f"{e}°", 20, TENUE).move_to(self.p(ang_lbl, e) + LEFT * 0.02)
                t.set_stroke(FONDO, 5, background=True)
                lbl.add(t)
        return SimpleNamespace(disco=disco, anillos=anillos, radios=radios,
                               centro=centro, lbl=lbl,
                               todo=VGroup(disco, anillos, radios, centro, lbl))


def polilinea(pts, color, w=4, op=1.0):
    m = VMobject()
    pts = np.asarray(pts, dtype=float)
    if len(pts) < 2:
        pts = np.vstack([pts[0], pts[0] + 1e-4])
    m.set_points_as_corners(pts)
    m.set_stroke(color, w, op)
    m.set_fill(opacity=0)
    return m


def tramo(pts, k):
    """Puntos desde 0 hasta el índice real k (interpolado)."""
    n = len(pts)
    k = float(np.clip(k, 0, n - 1))
    i = min(int(np.floor(k)), n - 2)
    f = k - i
    corte = pts[i] + (pts[i + 1] - pts[i]) * f
    return np.vstack([pts[:i + 1], corte])


def punto_en(pts, k):
    n = len(pts)
    k = float(np.clip(k, 0, n - 1))
    i = min(int(np.floor(k)), n - 2)
    return pts[i] + (pts[i + 1] - pts[i]) * (k - i)


def val_en(arr, k):
    return float(np.interp(k, np.arange(len(arr)), arr))


# ---------- textos vivos ----------------------------------------------------
_tc = {}


def _txt(s, tam, color):
    k = (s, tam, color)
    if k not in _tc:
        _tc[k] = Text(s, font=FUENTE, font_size=tam, color=color)
    return _tc[k].copy()


def cifra_viva(fn, unidad="°", tam=44, color=None, dec=0, ancla=ORIGIN,
               borde=LEFT, signo=False):
    color = color or C_ANT

    def build():
        v = fn()
        col_ = color() if callable(color) else color
        s = f"{v:+.{dec}f}" if signo else f"{v:.{dec}f}"
        s = s.replace("-", "−")
        g = VGroup(_txt(s, tam, col_))
        if unidad:
            g.add(_txt(unidad, max(int(tam * 0.6), 20), TENUE))
            g.arrange(RIGHT, buff=0.07, aligned_edge=UP if unidad == "°" else DOWN)
        g.move_to(ancla, aligned_edge=borde)
        return g
    return always_redraw(build)


# ---------- dibujo de antena y escena lateral -------------------------------
def plato(pos, ang, tam=0.55, color=None, ancho=5, dash=False):
    """Plato parabólico que gira sobre `pos` y apunta hacia `ang` (rad)."""
    c = color or C_ANT
    R = tam * 1.5
    arco = Arc(radius=R, start_angle=PI - 0.75, angle=1.5,
               arc_center=np.array([R, 0, 0]), color=c, stroke_width=ancho)
    e1, e2 = arco.get_start(), arco.get_end()
    foco = np.array([R * 0.5, 0, 0])
    st = VGroup(Line(e1, foco), Line(e2, foco)).set_stroke(c, max(ancho - 3, 1.5), 0.8)
    feed = Dot(foco, radius=0.055, color=c)
    if dash:
        arco = DashedVMobject(arco, num_dashes=16)
        st.set_stroke(opacity=0.5)
    piv = Dot(ORIGIN, radius=0.06, color=TENUE)
    g = VGroup(arco, st, feed, piv)
    g.rotate(ang, about_point=ORIGIN)
    g.shift(np.asarray(pos, dtype=float))
    return g


class Lateral:
    """Vista lateral: estación en `base` y satélite en arco parabólico."""

    def __init__(self, base, semiancho, alto, alt_mont=0.8):
        self.base = np.array([base[0], base[1], 0.0])
        self.sa, self.alto = semiancho, alto
        self.mont = self.base + UP * alt_mont

    def sat(self, u):
        x = (2 * u - 1) * self.sa
        return self.mont + np.array([x, self.alto * (1 - (x / self.sa) ** 2), 0])

    def ang(self, u):
        v = self.sat(u) - self.mont
        return np.arctan2(v[1], v[0])

    def el(self, u):
        v = self.sat(u) - self.mont
        return np.degrees(np.arctan2(v[1], abs(v[0])))

    def orbita_pts(self, n=90):
        return np.array([self.sat(u) for u in np.linspace(0, 1, n)])

    def mastil(self, color=None):
        c = color or C_ANT
        base = Polygon(self.base + LEFT * 0.42, self.base + RIGHT * 0.42,
                       self.base + RIGHT * 0.12 + UP * 0.28,
                       self.base + LEFT * 0.12 + UP * 0.28, color=c,
                       fill_color=c, fill_opacity=0.3, stroke_width=2)
        mast = Line(self.base + UP * 0.28, self.mont, color=c, stroke_width=5)
        return VGroup(base, mast)


def arco_flecha(centro, radio, a0, a1, color, ancho=4, rx=None, ry=None, tip=0.16):
    """Arco con punta de flecha (ángulos en rad, matemático)."""
    rx = rx or radio
    ry = ry or radio
    ts = np.linspace(a0, a1, 40)
    pts = np.array([[centro[0] + rx * np.cos(t), centro[1] + ry * np.sin(t), 0] for t in ts])
    m = polilinea(pts, color, ancho)
    d = pts[-1] - pts[-3]
    d = d / (np.linalg.norm(d) + 1e-9)
    n = np.array([-d[1], d[0], 0])
    tri = Polygon(pts[-1] + d * tip * 0.6, pts[-1] - d * tip * 0.6 + n * tip * 0.5,
                  pts[-1] - d * tip * 0.6 - n * tip * 0.5, color=color,
                  fill_color=color, fill_opacity=1, stroke_width=0)
    return VGroup(m, tri)


# =====================================================================
# 1. VistaPolarPase
# =====================================================================
class VistaPolarPase(Pieza):
    def construct(self):
        P = pase(68, az0=-35, n=420)
        pol = Polar((-2.7, -0.1), 3.05)
        f = pol.fondo()
        pts = pol.pts(P.az, P.el)
        N = len(pts)
        s = ValueTracker(0)
        K = lambda: s.get_value() * (N - 1)

        # panel derecho: cifra + perfil de elevación
        ax = Axes(x_range=[0, P.dur], y_range=[0, 90], x_length=4.5, y_length=2.4,
                  axis_config=dict(color=C_EJE, stroke_width=2.5, include_tip=False,
                                   include_ticks=False)).move_to([4.3, -1.55, 0])
        sub = list(range(0, N, 3)) + [N - 1]
        perfil = polilinea([ax.c2p(P.t[i], P.el[i]) for i in sub], C_SAT, 3, 0.3)
        perfil_v = always_redraw(lambda: polilinea(
            [ax.c2p(P.t[i], P.el[i]) for i in sub if i <= K()] +
            [ax.c2p(np.interp(K(), np.arange(N), P.t), val_en(P.el, K()))],
            C_SAT, 4.5))
        punto_g = always_redraw(lambda: Dot(ax.c2p(np.interp(K(), np.arange(N), P.t),
                                                    val_en(P.el, K())),
                                            radius=0.09, color=C_SAT))
        l_t = et("Tiempo", 20, TENUE).next_to(ax, DOWN, buff=0.12)
        l90 = et("90°", 20, TENUE).next_to(ax.c2p(0, 90), LEFT, buff=0.1)
        l0 = et("0°", 20, TENUE).next_to(ax.c2p(0, 0), LEFT, buff=0.1)
        l_el = et("Elevación", 26, TENUE).move_to([3.35, 2.75, 0])
        c_el = cifra_viva(lambda: val_en(P.el, K()), "°", 78, C_SAT, 0,
                          ancla=np.array([2.35, 1.7, 0]))

        # trayectoria
        pred = DashedVMobject(polilinea(pts, C_CIELO, 3, 0.65), num_dashes=80)
        trail = always_redraw(lambda: VGroup(
            polilinea(tramo(pts, K()), C_SAT, 11, 0.2),
            polilinea(tramo(pts, K()), C_SAT, 4.5, 1)))
        sat = always_redraw(lambda: satelite(0.14).move_to(punto_en(pts, K())))

        def marca(k, texto, off=0.46):
            p = pts[k]
            d = (p - pol.c) / np.linalg.norm(p - pol.c)
            r = Circle(radius=0.11, color=TINTA, stroke_width=3).move_to(p)
            t = et(texto, 26, TINTA).move_to(p + d * off)
            return VGroup(r, t)

        m_aos, m_tca, m_los = marca(0, "AOS"), marca(P.tca, "TCA", 0.42), marca(N - 1, "LOS")

        self.play(FadeIn(f.disco), Create(f.anillos), Create(f.radios), run_time=1.6)
        self.play(FadeIn(f.lbl), FadeIn(f.centro), run_time=0.8)
        self.play(FadeIn(l_el), FadeIn(ax), FadeIn(perfil), FadeIn(l_t), FadeIn(l90),
                  FadeIn(l0), run_time=0.9)
        self.add(c_el)
        self.play(Create(pred), run_time=1.6)
        self.add(trail, sat, perfil_v, punto_g)
        self.play(FadeIn(m_aos, scale=0.6), run_time=0.6)
        self.play(s.animate.set_value(P.tca / (N - 1)), run_time=4.6, rate_func=linear)
        self.play(FadeIn(m_tca, scale=0.6), run_time=0.4)
        self.play(s.animate.set_value(1), run_time=4.6, rate_func=linear)
        self.play(FadeIn(m_los, scale=0.6), FadeOut(sat), run_time=0.6)
        self.cierre()


# =====================================================================
# 2. CadenaTLEaAntena
# =====================================================================
class CadenaTLEaAntena(Pieza):
    def construct(self):
        nombres = ["TLE", "SGP4", "Coordenadas", "Az/El", "Controlador", "Motores", "Antena"]
        cols = [C_CIELO, C_CIELO, C_CIELO, C_ANT, C_ANT, C_ANT, C_ANT]
        anchos = [1.3, 1.3, 1.95, 1.3, 1.95, 1.5, 1.5]
        gap = 0.36
        tot = sum(anchos) + gap * 6
        xs, xa = [], -tot / 2
        for a in anchos:
            xs.append(xa + a / 2)
            xa += a + gap
        xs = np.array(xs)
        y0 = 2.65
        cajas = [caja(n, a, 0.85, c, 21, 0.16).move_to([x, y0, 0])
                 for n, x, c, a in zip(nombres, xs, cols, anchos)]
        flechas = [flecha([xs[i] + anchos[i] / 2, y0, 0], [xs[i + 1] - anchos[i + 1] / 2, y0, 0],
                          TENUE, 2.5, 0.14) for i in range(6)]

        # escena inferior
        L = Lateral((0, -3.25), 6.0, 2.7, 0.85)
        panel = RoundedRectangle(corner_radius=0.2, width=13.2, height=4.75, color=C_EJE,
                                 stroke_width=2).move_to([0, -1.5, 0])
        suelo = Line([-6.6, -3.25, 0], [6.6, -3.25, 0], color=C_EJE, stroke_width=3)
        orb = DashedVMobject(polilinea(L.orbita_pts(), C_SAT, 2.5, 0.5), num_dashes=70)
        est = L.mastil()
        u = ValueTracker(0)
        dish = always_redraw(lambda: plato(L.mont, L.ang(u.get_value()), 0.62, C_ANT, 6))
        sat = always_redraw(lambda: satelite(0.15).move_to(L.sat(u.get_value())))
        haz_m = always_redraw(lambda: VGroup(
            Line(L.mont, L.sat(u.get_value()), color=C_ANT, stroke_width=9, stroke_opacity=0.18),
            Line(L.mont, L.sat(u.get_value()), color=C_ANT, stroke_width=3)))
        conector = flecha([xs[6], y0 - 0.45, 0], [xs[6], -0.05, 0], C_ANT, 3, 0.16)

        # construcción progresiva
        self.play(FadeIn(panel), Create(suelo), run_time=0.6)
        self.play(FadeIn(est), Create(orb), FadeIn(dish), FadeIn(sat), run_time=0.8)
        for i in range(7):
            anims = [FadeIn(cajas[i], shift=DOWN * 0.15)]
            if i > 0:
                anims.append(GrowArrow(flechas[i - 1]))
            self.play(*anims, run_time=0.38)
        self.play(GrowArrow(conector), run_time=0.4)
        self.respiro(0.3)

        # pulso ámbar recorre la cadena
        ruta = polilinea([[xs[0], y0, 0], [xs[6], y0, 0], [xs[6], 0.0, 0]], C_SAT, 1, 0)
        long_tot = xs[6] - xs[0] + (y0 - 0.0)
        pulso_g = VGroup(Circle(radius=0.24, stroke_width=0, fill_color=C_SAT, fill_opacity=0.3),
                         Dot(radius=0.11, color=C_SAT)).move_to([xs[0], y0, 0])
        hitos = [(x - xs[0]) / long_tot for x in xs]
        prend = [False] * 7

        def avanzar(m, a):
            m.move_to(ruta.point_from_proportion(min(a, 1)))
            for i in range(7):
                if a >= hitos[i] - 0.004 and not prend[i]:
                    prend[i] = True
                    cajas[i][0].set_fill(cols[i], 0.75).set_stroke(width=4.5)
        self.add(pulso_g)
        self.play(UpdateFromAlphaFunc(pulso_g, avanzar), run_time=5.2, rate_func=linear)
        self.play(FadeOut(pulso_g), run_time=0.3)

        # la antena gira siguiendo al satélite; pulsos continuos en la cadena
        cad = polilinea([[xs[0], y0, 0], [xs[6], y0, 0]], C_SAT, 1, 0)
        p2 = VGroup(Circle(radius=0.2, stroke_width=0, fill_color=C_SAT, fill_opacity=0.3),
                    Dot(radius=0.09, color=C_SAT)).move_to([xs[0], y0, 0])
        ph = [0.0]

        def cicla(m, dt):
            ph[0] = (ph[0] + dt / 2.6) % 1.0
            m.move_to(cad.point_from_proportion(ph[0]))
        p2.add_updater(cicla)
        self.add(haz_m, p2)
        self.bring_to_front(dish, sat)
        self.play(u.animate.set_value(1), run_time=9, rate_func=linear)
        p2.clear_updaters()
        self.cierre()


# =====================================================================
# 3. AntenaSiguiendo
# =====================================================================
class AntenaSiguiendo(Pieza):
    def construct(self):
        L = Lateral((0, -3.0), 6.4, 5.2, 0.8)
        m = L.mont
        u = ValueTracker(0)
        U = lambda: u.get_value()
        MASC = 10.0

        suelo = VGroup(
            Rectangle(width=14.2, height=0.9, fill_color=C_EJE, fill_opacity=0.35,
                      stroke_width=0).move_to([0, -3.45, 0]),
            Line([-7.1, -3.0, 0], [7.1, -3.0, 0], color=C_EJE, stroke_width=3))
        horiz = DashedLine([-7.0, m[1], 0], [7.0, m[1], 0], color=C_CIELO, stroke_width=2,
                           dash_length=0.14, stroke_opacity=0.8)
        tm = np.tan(np.radians(MASC))
        cuñas = VGroup()
        for sgn in (-1, 1):
            cuñas.add(Polygon(m, m + np.array([sgn * 6.6, 0, 0]),
                              m + np.array([sgn * 6.6, 6.6 * tm, 0]),
                              fill_color=C_MAL, fill_opacity=0.16, stroke_width=0))
            cuñas.add(DashedLine(m, m + np.array([sgn * 6.6, 6.6 * tm, 0]), color=C_MAL,
                                 stroke_width=2.5, dash_length=0.12))
        l_h = et("Horizonte", 22, C_CIELO).move_to([-3.4, m[1] - 0.36, 0])
        l_m = et("Máscara 10°", 22, C_MAL).move_to([3.5, m[1] - 0.36, 0])
        est = L.mastil()
        orb = DashedVMobject(polilinea(L.orbita_pts(), C_SAT, 2.5, 0.45), num_dashes=80)
        pts = L.orbita_pts(200)

        dish = always_redraw(lambda: plato(m, max(L.ang(min(max(U(), 0), 1)),
                                                  0) if L.el(U()) >= MASC else
                                           (np.radians(MASC) if L.sat(U())[0] > 0
                                            else PI - np.radians(MASC)),
                                           0.66, C_ANT, 6))
        sat = always_redraw(lambda: satelite(0.16).move_to(L.sat(U())))
        trail = always_redraw(lambda: VGroup(
            polilinea(tramo(pts, U() * 199), C_SAT, 9, 0.18),
            polilinea(tramo(pts, U() * 199), C_SAT, 4, 0.95)))

        def beam():
            a, b = m, L.sat(U())
            if L.el(U()) >= MASC:
                return VGroup(Line(a, b, color=C_ANT, stroke_width=11, stroke_opacity=0.16),
                              Line(a, b, color=C_ANT, stroke_width=3.5))
            return DashedLine(a, b, color=C_MAL, stroke_width=2, dash_length=0.12,
                              stroke_opacity=0.55)
        haz_m = always_redraw(beam)

        def arco_el():
            e = np.radians(L.el(U()))
            sg = 1 if L.sat(U())[0] >= 0 else -1
            a0, a1 = (0, e) if sg > 0 else (PI, PI - e)
            col = C_ANT if L.el(U()) >= MASC else C_MAL
            ts = np.linspace(a0, a1, 30)
            r = 1.15
            return polilinea([m + np.array([r * np.cos(t), r * np.sin(t), 0]) for t in ts],
                             col, 3.5, 0.95)
        arco_m = always_redraw(arco_el)
        c_el = cifra_viva(lambda: L.el(U()), "°", 64, C_SAT, 0, ancla=np.array([-6.3, 2.75, 0]))
        l_el = et("Elevación", 26, TENUE).move_to([-5.45, 3.5, 0])

        self.play(FadeIn(suelo), Create(horiz), run_time=1.0)
        self.play(FadeIn(est), FadeIn(dish), FadeIn(l_h), run_time=0.8)
        self.play(FadeIn(cuñas), FadeIn(l_m), run_time=1.0)
        self.play(Create(orb), run_time=1.4)
        self.add(trail, haz_m, arco_m, sat, dish)
        self.play(FadeIn(l_el), run_time=0.4)
        self.add(c_el)
        self.play(u.animate.set_value(1), run_time=15, rate_func=linear)
        self.play(FadeOut(sat), run_time=0.4)
        self.cierre()


# =====================================================================
# 4. MontajeAzEl
# =====================================================================
class MontajeAzEl(Pieza):
    def construct(self):
        cp = np.array([-3.5, 0.55, 0.0])      # planta
        RP = 2.3
        piv = np.array([3.5, -0.35, 0.0])     # perfil: pivote de elevación
        suelo_y = -1.95
        u = ValueTracker(0)
        AZ0, AZ1 = 25.0, 205.0
        az = lambda: AZ0 + (AZ1 - AZ0) * u.get_value()
        el = lambda: 12 + 62 * np.sin(PI * u.get_value())

        # --- planta
        aro = Circle(radius=RP, color=C_EJE, stroke_width=3, fill_color=C_PANEL,
                     fill_opacity=0.4).move_to(cp)
        marcas = VGroup(*[Line(cp + RP * np.array([np.sin(a), np.cos(a), 0]) * 0.93,
                               cp + RP * np.array([np.sin(a), np.cos(a), 0]),
                               color=C_EJE, stroke_width=2)
                          for a in np.radians(np.arange(0, 360, 30))])
        ln_n = DashedLine(cp, cp + UP * RP, color=C_CIELO, stroke_width=2, dash_length=0.1)
        l_n = et("N", 26, TINTA).move_to(cp + UP * (RP + 0.36))
        eje_v = VGroup(Circle(radius=0.17, color=C_CIELO, stroke_width=3).move_to(cp),
                       Dot(cp, radius=0.05, color=C_CIELO))

        def planta():
            a = np.radians(az())
            e = np.radians(el())
            d = np.array([np.sin(a), np.cos(a), 0])
            perp = np.array([np.cos(a), -np.sin(a), 0])
            L = 0.55 + 1.25 * np.cos(e)
            fin = cp + d * L
            brazo = Line(cp, fin, color=C_ANT, stroke_width=6)
            D = 1.15
            elip = Ellipse(width=D, height=max(D * np.sin(e), 0.1), color=C_ANT,
                           stroke_width=5, fill_color=C_ANT, fill_opacity=0.22)
            elip.rotate(np.arctan2(perp[1], perp[0])).move_to(fin)
            eje_e = DashedLine(cp - perp * 1.45, cp + perp * 1.45, color=C_CIELO,
                               stroke_width=2.5, dash_length=0.1)
            return VGroup(eje_e, brazo, elip)
        planta_m = always_redraw(planta)
        arco_az = always_redraw(lambda: arco_flecha(
            cp, 1.05, PI / 2, PI / 2 - np.radians(az()), C_SAT, 4.5))

        # --- perfil
        suelo = VGroup(
            Line([0.9, suelo_y, 0], [6.3, suelo_y, 0], color=C_EJE, stroke_width=3),
            Polygon([2.9, suelo_y, 0], [4.1, suelo_y, 0], [3.85, suelo_y + 0.22, 0],
                    [3.15, suelo_y + 0.22, 0], color=C_ANT, fill_color=C_ANT,
                    fill_opacity=0.3, stroke_width=2))
        pilar = Rectangle(width=0.36, height=piv[1] - suelo_y - 0.22, color=C_ANT,
                          fill_color=C_ANT, fill_opacity=0.3, stroke_width=2.5)
        pilar.move_to([piv[0], (piv[1] + suelo_y + 0.22) / 2, 0])
        eje_az = DashedLine([piv[0], suelo_y + 0.3, 0], [piv[0], piv[1] + 2.65, 0],
                            color=C_CIELO, stroke_width=2.5, dash_length=0.1)
        eje_el = VGroup(Circle(radius=0.17, color=C_CIELO, stroke_width=3).move_to(piv),
                        Dot(piv, radius=0.05, color=C_CIELO))
        hor = DashedLine(piv, piv + RIGHT * 2.7, color=C_CIELO, stroke_width=2, dash_length=0.1,
                         stroke_opacity=0.6)
        flecha_az = arco_flecha([piv[0], suelo_y + 0.55, 0], 0, 0.5 * PI + 0.35,
                                0.5 * PI + 0.35 + 4.4, C_SAT, 3.5, rx=0.85, ry=0.24)
        perfil_m = always_redraw(lambda: plato(piv, np.radians(el()), 0.9, C_ANT, 6))
        arco_el = always_redraw(lambda: arco_flecha(piv, 1.4, 0, np.radians(el()), C_SAT, 4.5))
        haz_el = always_redraw(lambda: DashedLine(
            piv, piv + 2.5 * np.array([np.cos(np.radians(el())), np.sin(np.radians(el())), 0]),
            color=C_ANT, stroke_width=2.5, dash_length=0.12, stroke_opacity=0.8))

        # cifras
        l_pl = et("Planta", 24, TENUE).move_to([-3.5, -2.55, 0])
        l_pf = et("Perfil", 24, TENUE).move_to([3.5, -2.55, 0])
        l_az = et("Az", 28, TENUE).move_to([-4.6, -3.3, 0])
        l_el = et("El", 28, TENUE).move_to([2.4, -3.3, 0])
        c_az = cifra_viva(az, "°", 56, C_SAT, 0, ancla=np.array([-4.15, -3.3, 0]))
        c_el = cifra_viva(el, "°", 56, C_SAT, 0, ancla=np.array([2.85, -3.3, 0]))

        self.play(FadeIn(aro), Create(marcas), FadeIn(l_n), Create(ln_n), FadeIn(eje_v),
                  run_time=1.5)
        self.play(FadeIn(suelo), FadeIn(pilar), FadeIn(eje_el), Create(eje_az), Create(hor),
                  run_time=1.5)
        self.play(FadeIn(l_pl), FadeIn(l_pf), run_time=0.4)
        self.add(planta_m, perfil_m, haz_el)
        self.play(FadeIn(planta_m), FadeIn(perfil_m), FadeIn(flecha_az), run_time=0.8)
        self.add(arco_az, arco_el, c_az, c_el)
        self.play(FadeIn(l_az), FadeIn(l_el), run_time=0.4)
        self.play(u.animate.set_value(1), run_time=11, rate_func=smooth)
        self.cierre()


# =====================================================================
# 5. LazoPID
# =====================================================================
def _simular_pid(T=10.0, dt=0.005):
    kp, ki, kd, tau = 2.2, 1.4, 0.35, 0.7
    ref = lambda t: 1.0 + 0.5 * t
    x, v, integ, prev_e = 0.0, 0.0, 0.0, ref(0.0)
    ts, rs, xs = [], [], []
    for i in range(int(T / dt) + 1):
        t = i * dt
        r = ref(t)
        e = r - x
        integ += e * dt
        u = kp * e + ki * integ + kd * (e - prev_e) / dt
        prev_e = e
        v += (u - v) / tau * dt
        x += v * dt
        ts.append(t)
        rs.append(r)
        xs.append(x)
    return np.array(ts), np.array(rs), np.array(xs)


class LazoPID(Pieza):
    def construct(self):
        ts, rs, xs = _simular_pid()
        N = len(ts)
        T = ts[-1]
        tr = ValueTracker(0)
        K = lambda: tr.get_value() * (N - 1)

        # ---- diagrama
        y = 2.55
        yf = 1.35
        mas = et("+", 24, TINTA).move_to([-4.98, y + 0.3, 0])
        menos = et("−", 26, TINTA).move_to([-4.27, yf + 0.28, 0])
        pid = caja("PID", 1.7, 0.9, C_ANT, 26, 0.18).move_to([-2.0, y, 0])
        motor = caja("Motor", 1.7, 0.9, C_ANT, 26, 0.18).move_to([1.3, y, 0])
        sensor = caja("Sensor", 1.7, 0.8, C_CIELO, 24, 0.18).move_to([0.0, yf, 0])
        pos_d = np.array([4.75, y, 0])
        a_in = flecha([-6.45, y, 0], [-4.86, y, 0], C_SAT, 3)
        l_ref = et("Referencia", 22, C_SAT).move_to([-5.85, y + 0.42, 0])
        a1 = flecha([-4.25, y, 0], [-2.87, y, 0], TENUE, 3)
        a2 = flecha([-1.13, y, 0], [0.43, y, 0], TENUE, 3)
        a3 = flecha([2.17, y, 0], [3.95, y, 0], TENUE, 3)
        fb = VGroup(
            Line([3.35, y, 0], [3.35, yf, 0], color=TENUE, stroke_width=3),
            Line([3.35, yf, 0], [0.85, yf, 0], color=TENUE, stroke_width=3),
            Line([-0.85, yf, 0], [-4.55, yf, 0], color=TENUE, stroke_width=3),
            Arrow([-4.55, yf, 0], [-4.55, y - 0.3, 0], buff=0, color=TENUE,
                  stroke_width=3, tip_length=0.16))
        base_d = Dot([3.35, y, 0], radius=0.07, color=TENUE)

        # antena del diagrama: apunta a ángulo derivado de la posición; rayo de referencia
        ang = lambda v: np.radians(15 + 11 * v)
        dish = always_redraw(lambda: plato(pos_d + DOWN * 0.15, ang(val_en(xs, K())), 0.45,
                                            C_ANT, 5))
        rayo = always_redraw(lambda: DashedLine(
            pos_d + DOWN * 0.15,
            pos_d + DOWN * 0.15 + 1.25 * np.array([np.cos(ang(val_en(rs, K()))),
                                                    np.sin(ang(val_en(rs, K()))), 0]),
            color=C_SAT, stroke_width=3, dash_length=0.1))

        col_err = lambda: interpolate_color(ManimColor(C_OK), ManimColor(C_MAL),
                                            float(np.clip(abs(val_en(rs - xs, K())) / 1.0, 0, 1)))
        suma_c = always_redraw(lambda: Circle(radius=0.3, color=TINTA, stroke_width=3,
                                              fill_color=col_err(), fill_opacity=0.92
                                              ).move_to([-4.55, y, 0]))
        l_err = et("Error", 22, TENUE).move_to([-3.5, y + 0.55, 0])

        # ---- gráfica
        ax = Axes(x_range=[0, T], y_range=[0, 6.5], x_length=9.2, y_length=3.55,
                  axis_config=dict(color=C_EJE, stroke_width=2.5, include_tip=False,
                                   include_ticks=False)).move_to([-1.75, -1.85, 0])
        l_x = et("Tiempo", 20, TENUE).next_to(ax, DOWN, buff=0.12)
        l_y = et("Ángulo", 20, TENUE).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        idx = list(range(0, N, 5))
        curva = lambda arr, c, w, k: polilinea(
            [ax.c2p(ts[i], arr[i]) for i in idx if i <= k] +
            [ax.c2p(np.interp(k, np.arange(N), ts), val_en(arr, k))], c, w)
        c_ref = always_redraw(lambda: curva(rs, C_SAT, 4.5, K()))
        c_pos = always_redraw(lambda: curva(xs, C_ANT, 4.5, K()))

        def conector():
            k = K()
            tt = np.interp(k, np.arange(N), ts)
            a = ax.c2p(tt, val_en(rs, k))
            b = ax.c2p(tt, val_en(xs, k))
            col = col_err()
            return VGroup(Line(a, b, color=col, stroke_width=6),
                          Dot(a, radius=0.08, color=C_SAT), Dot(b, radius=0.08, color=C_ANT))
        con = always_redraw(conector)
        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=C_SAT, stroke_width=5),
                   et("Referencia", 22, TINTA)).arrange(RIGHT, buff=0.15),
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=C_ANT, stroke_width=5),
                   et("Antena", 22, TINTA)).arrange(RIGHT, buff=0.15),
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=C_MAL, stroke_width=6),
                   et("Error", 22, TINTA)).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([5.75, -1.0, 0])
        sombra = always_redraw(lambda: VGroup(*[
            Line(ax.c2p(ts[i], rs[i]), ax.c2p(ts[i], xs[i]), stroke_width=3.5,
                 stroke_opacity=0.55,
                 color=interpolate_color(ManimColor(C_OK), ManimColor(C_MAL),
                                         float(np.clip(abs(rs[i] - xs[i]), 0, 1))))
            for i in range(0, N, 12) if i <= K()]))

        # ---- secuencia
        self.play(GrowArrow(a_in), FadeIn(l_ref), FadeIn(suma_c), FadeIn(mas), FadeIn(menos),
                  run_time=1.0)
        self.play(GrowArrow(a1), FadeIn(pid), run_time=0.6)
        self.play(GrowArrow(a2), FadeIn(motor), run_time=0.6)
        self.play(GrowArrow(a3), FadeIn(dish), FadeIn(base_d), run_time=0.6)
        self.play(Create(fb), FadeIn(sensor), FadeIn(l_err), run_time=1.4)
        self.play(FadeIn(ax), FadeIn(l_x), FadeIn(l_y), FadeIn(leg), run_time=0.9)
        self.add(sombra, c_ref, c_pos, con, rayo)
        self.play(tr.animate.set_value(1), run_time=11, rate_func=linear)
        self.cierre()


# =====================================================================
# 6. Keyhole
# =====================================================================
def _seguir(target, dt, vmax):
    a = np.zeros_like(target)
    a[0] = target[0]
    for i in range(1, len(target)):
        d = target[i] - a[i - 1]
        a[i] = a[i - 1] + np.clip(d, -vmax * dt, vmax * dt)
    return a


class Keyhole(Pieza):
    VMAX = 5.0    # °/s, límite del motor de azimut

    def construct(self):
        pol = Polar((-3.05, 0.05), 3.05)
        f = pol.fondo(True, ang_lbl=225)
        ax = Axes(x_range=[-45, 45], y_range=[60, 300], x_length=4.9, y_length=4.0,
                  axis_config=dict(color=C_EJE, stroke_width=2.5, include_tip=False,
                                   include_ticks=False)).move_to([4.2, 0.35, 0])
        l_x = et("Tiempo", 20, TENUE).next_to(ax, DOWN, buff=0.12)
        l_y = et("Azimut", 20, TENUE).next_to(ax, UP, buff=0.1).align_to(ax, LEFT)
        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=C_CIELO, stroke_width=5),
                   et("Necesario", 22, TINTA)).arrange(RIGHT, buff=0.15),
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=C_ANT, stroke_width=5),
                   et("Antena", 22, TINTA)).arrange(RIGHT, buff=0.15),
        ).arrange(RIGHT, buff=0.5).move_to([4.2, 3.35, 0])
        lamp_pos = np.array([2.2, -3.05, 0])
        l_er = et("Error", 24, TENUE).move_to([3.05, -3.05, 0])

        self.play(FadeIn(f.disco), Create(f.anillos), Create(f.radios), run_time=1.3)
        self.play(FadeIn(f.lbl), FadeIn(f.centro), FadeIn(ax), FadeIn(l_x), FadeIn(l_y),
                  FadeIn(leg), FadeIn(l_er), run_time=0.9)

        for fase_i, (elmax, dur) in enumerate(((88.0, 9.0), (35.0, 8.0))):
            P = pase(elmax, az0=360, lado=1, n=901, ventana=45)
            full = pase(elmax, az0=360, lado=1, n=400)
            dt = P.t[1] - P.t[0]
            aa = _seguir(P.az, dt, self.VMAX)
            N = len(P.t)
            tr = ValueTracker(0)
            K = lambda tr=tr, N=N: tr.get_value() * (N - 1)
            pts_full = pol.pts(full.az, full.el)
            pts = pol.pts(P.az, P.el)
            pred = DashedVMobject(polilinea(pts_full, C_CIELO, 3, 0.6), num_dashes=70)
            trail = always_redraw(lambda pts=pts, K=K: VGroup(
                polilinea(tramo(pts, K()), C_SAT, 10, 0.2),
                polilinea(tramo(pts, K()), C_SAT, 4.5, 1)))
            sat = always_redraw(lambda pts=pts, K=K: satelite(0.14).move_to(punto_en(pts, K())))

            def aguja(P=P, aa=aa, K=K):
                a_a = val_en(aa, K())
                a_t = val_en(P.az, K())
                el_t = val_en(P.el, K())
                fin = pol.p(a_a, 0)
                dif = a_t - a_a
                g = VGroup()
                if abs(dif) > 0.5:
                    r = 1.35
                    ang = np.radians(np.linspace(a_a, a_t, 30))
                    poli = [pol.c] + [pol.c + r * np.array([np.sin(x), np.cos(x), 0]) for x in ang]
                    g.add(Polygon(*poli, fill_color=C_MAL, fill_opacity=0.4, stroke_width=0))
                g.add(DashedLine(pol.c, pol.p(a_t, 0), color=C_SAT, stroke_width=2,
                                 dash_length=0.1, stroke_opacity=0.7))
                g.add(Line(pol.c, fin, color=C_ANT, stroke_width=5))
                g.add(Dot(fin, radius=0.09, color=C_ANT))
                return g
            ag = always_redraw(aguja)

            idx = list(range(0, N, 3))
            gr = lambda arr, c, K=K, P=P: polilinea(
                [ax.c2p(P.t[i] - P.t[len(P.t) // 2], arr[i]) for i in idx if i <= K()] +
                [ax.c2p(np.interp(K(), np.arange(N), P.t) - P.t[len(P.t) // 2], val_en(arr, K()))],
                c, 4.5)
            g_t = always_redraw(lambda gr=gr, P=P: gr(P.az, C_CIELO))
            g_a = always_redraw(lambda gr=gr, aa=aa: gr(aa, C_ANT))
            err = lambda P=P, aa=aa, K=K: abs(val_en(P.az, K()) - val_en(aa, K()))
            col = lambda err=err: interpolate_color(ManimColor(C_OK), ManimColor(C_MAL),
                                                    float(np.clip(err() / 12, 0, 1)))
            lamp = always_redraw(lambda col=col: VGroup(
                Circle(radius=0.3, color=col(), stroke_width=0, fill_color=col(), fill_opacity=0.25).scale(1.5),
                Circle(radius=0.3, color=TINTA, stroke_width=0, fill_color=col(), fill_opacity=1)
            ).move_to(lamp_pos))
            c_err = cifra_viva(err, "°", 44, col, 0, ancla=np.array([3.7, -3.05, 0]))

            self.play(Create(pred), run_time=1.0)
            self.add(trail, sat, ag, g_t, g_a, lamp, c_err)
            self.play(tr.animate.set_value(1), run_time=dur, rate_func=linear)
            self.wait(1.0)
            if fase_i == 0:
                self.play(*[FadeOut(m) for m in (pred, trail, sat, ag, g_t, g_a)], run_time=0.8)
                self.remove(lamp, c_err)
        self.cierre()


# =====================================================================
# 7. DopplerEnS
# =====================================================================
def _recortar(cx, cy, r, caja_xy, n=110):
    """Círculo recortado a una caja (x0,x1,y0,y1): devuelve VMobject."""
    x0, x1, y0, y1 = caja_xy
    a = np.linspace(0, TAU, n)
    xs_, ys_ = cx + r * np.cos(a), cy + r * np.sin(a)
    dentro = (xs_ >= x0) & (xs_ <= x1) & (ys_ >= y0) & (ys_ <= y1)
    m = VMobject()
    trozos = []
    cur = []
    for i in range(n):
        if dentro[i]:
            cur.append([xs_[i], ys_[i], 0])
        elif cur:
            trozos.append(cur)
            cur = []
    if cur:
        trozos.append(cur)
    first = True
    for tz in trozos:
        if len(tz) < 2:
            continue
        if first:
            m.set_points_as_corners(np.array(tz))
            first = False
        else:
            sub = VMobject()
            sub.set_points_as_corners(np.array(tz))
            m.append_points(sub.points)
    return m, not first


class DopplerEnS(Pieza):
    def construct(self):
        # panel de geometría
        xc = -3.65
        x0, x1, ysup, yinf = -6.9, -0.4, 3.0, -3.0
        sky = (x0 + 0.03, x1 - 0.03, -2.2, ysup - 0.03)
        marco = RoundedRectangle(corner_radius=0.2, width=x1 - x0, height=ysup - yinf,
                                 color=C_EJE, stroke_width=2).move_to([(x0 + x1) / 2, (ysup + yinf) / 2, 0])
        suelo = Rectangle(width=x1 - x0 - 0.06, height=0.75, fill_color=C_EJE, fill_opacity=0.35,
                          stroke_width=0).move_to([(x0 + x1) / 2, -2.2 - 0.375 + 0.0, 0])
        suelo_l = Line([x0 + 0.03, -2.2, 0], [x1 - 0.03, -2.2, 0], color=C_EJE, stroke_width=3)
        mont = np.array([xc, -1.5, 0])
        base = np.array([xc, -2.2, 0])
        est = VGroup(
            Polygon(base + LEFT * 0.4, base + RIGHT * 0.4, base + RIGHT * 0.1 + UP * 0.25,
                    base + LEFT * 0.1 + UP * 0.25, color=C_ANT, fill_color=C_ANT,
                    fill_opacity=0.3, stroke_width=2),
            Line(base + UP * 0.25, mont, color=C_ANT, stroke_width=5))
        ysat = 0.1
        half = 2.6
        s = ValueTracker(-1)
        S = lambda: s.get_value()
        xs_sat = lambda: xc + S() * half
        DUR = 13.0
        c_v, v_sat, dT = 1.0, 2 * half / DUR, 0.28

        # ondas emitidas por el satélite (frentes de onda recortados al panel)
        ph = {"t": 0.0}
        ondas = VGroup()

        def actualiza(m, dt):
            ph["t"] += dt
            t = ph["t"]
            m.submobjects = []
            kmax = int(t / dT)
            for k in range(kmax, max(kmax - 16, -1), -1):
                te = k * dT
                r = c_v * (t - te)
                if r <= 0.02 or r > 3.3:
                    continue
                xe = xc - half + v_sat * te   # posición de emisión (parte de x=-1)
                if te * v_sat > 2 * half + 0.01:
                    continue
                circ, ok = _recortar(xe, ysat, r, sky)
                if not ok:
                    continue
                circ.set_stroke(C_SAT, 2.2, opacity=float(np.clip(0.85 * (1 - r / 3.3), 0, 1)))
                m.add(circ)
        ondas.add_updater(actualiza)

        sat = always_redraw(lambda: satelite(0.18).move_to([xs_sat(), ysat, 0]))
        dish = always_redraw(lambda: plato(mont, np.arctan2(ysat - mont[1], xs_sat() - mont[0]),
                                           0.5, C_ANT, 5))
        pista = DashedLine([xc - half, ysat, 0], [xc + half, ysat, 0], color=C_SAT,
                           stroke_width=2, dash_length=0.14, stroke_opacity=0.35)

        # gráfica
        gax = Axes(x_range=[-1, 1], y_range=[-3.6, 3.6], x_length=5.0, y_length=4.3,
                   axis_config=dict(color=C_EJE, stroke_width=2.5, include_tip=False,
                                    include_ticks=False)).move_to([4.15, 0.15, 0])
        A = 3.4
        hh = 1.6
        fd = lambda sv: -A * (sv * half) / np.sqrt((sv * half) ** 2 + hh ** 2)
        nominal = DashedLine(gax.c2p(-1, 0), gax.c2p(1, 0), color=C_CIELO, stroke_width=2.5,
                             dash_length=0.14)
        l_nom = et("137 MHz", 22, C_CIELO).next_to(gax.c2p(1, 0), UP, buff=0.14).shift(LEFT * 0.55)
        l_pos = et("+3 kHz", 24, TINTA).next_to(gax.c2p(-1, 3.0), LEFT, buff=0.1)
        l_neg = et("−3 kHz", 24, TINTA).next_to(gax.c2p(-1, -3.0), LEFT, buff=0.1)
        l_f = et("Frecuencia", 20, TENUE).next_to(gax, UP, buff=0.1).align_to(gax, LEFT)
        l_t = et("Tiempo", 20, TENUE).next_to(gax, DOWN, buff=0.12)
        tks = np.linspace(-1, 1, 160)
        curva = always_redraw(lambda: polilinea(
            [gax.c2p(x, fd(x)) for x in tks if x <= S()] + [gax.c2p(S(), fd(S()))],
            C_ANT, 5))
        punto = always_redraw(lambda: VGroup(
            Dot(gax.c2p(S(), fd(S())), radius=0.2, color=C_SAT).set_opacity(0.3),
            Dot(gax.c2p(S(), fd(S())), radius=0.09, color=C_SAT)))

        self.play(FadeIn(marco), FadeIn(suelo), Create(suelo_l), FadeIn(est), run_time=1.0)
        self.play(FadeIn(dish), FadeIn(gax), FadeIn(l_t), FadeIn(l_f), Create(nominal),
                  FadeIn(l_nom), run_time=1.0)
        self.play(FadeIn(l_pos), FadeIn(l_neg), Create(pista), run_time=0.7)
        self.add(ondas, curva, punto, sat)
        self.bring_to_front(dish)
        self.play(s.animate.set_value(1), run_time=DUR, rate_func=linear)
        ondas.clear_updaters()
        self.play(FadeOut(ondas), FadeOut(sat), run_time=0.4)
        self.cierre()


# =====================================================================
# 8. GemeloDigitalATP
# =====================================================================
class GemeloDigitalATP(Pieza):
    def construct(self):
        cx = -1.7
        SA, ALTO = 4.5, 2.05
        Lr = Lateral((cx, 0.75), SA, ALTO, 0.55)
        Ld = Lateral((cx, -3.4), SA, ALTO, 0.55)
        w, hgt = 10.0, 3.4
        marco_r = RoundedRectangle(corner_radius=0.2, width=w, height=hgt, color=C_EJE,
                                   stroke_width=2).move_to([cx, 2.05, 0])
        marco_d = DashedVMobject(RoundedRectangle(corner_radius=0.2, width=w, height=hgt,
                                                  color=C_CIELO, stroke_width=2.5
                                                  ).move_to([cx, -2.05, 0]), num_dashes=70)
        suelo_r = Line([cx - w / 2 + 0.1, 0.75, 0], [cx + w / 2 - 0.1, 0.75, 0], color=C_EJE, stroke_width=3)
        suelo_d = DashedLine([cx - w / 2 + 0.1, -3.4, 0], [cx + w / 2 - 0.1, -3.4, 0], color=C_EJE,
                             stroke_width=3, dash_length=0.15)
        l_r = et("Real", 26, TENUE).move_to([cx - w / 2 + 0.75, 3.45, 0])
        l_d = et("Gemelo", 26, C_CIELO).move_to([cx - w / 2 + 0.95, -0.7, 0])

        tau = ValueTracker(0)
        T = lambda: tau.get_value()
        s_r = lambda: 0.14 + 0.72 * T()
        off = lambda: 0.16 * np.exp(-4.2 * T()) * np.cos(6.0 * T())
        s_d = lambda: min(max(s_r() - off(), 0), 1)

        est_r = Lr.mastil()
        est_d = Ld.mastil().set_stroke(opacity=0.65).set_fill(opacity=0.15)
        orb_r = DashedVMobject(polilinea(Lr.orbita_pts(), C_SAT, 2.5, 0.4), num_dashes=70)
        orb_d = DashedVMobject(polilinea(Ld.orbita_pts(), C_SAT, 2.5, 0.35), num_dashes=40)

        sat_r = always_redraw(lambda: satelite(0.15).move_to(Lr.sat(s_r())))
        sat_d = always_redraw(lambda: satelite(0.15).move_to(Ld.sat(s_d())).set_opacity(0.55))
        dish_r = always_redraw(lambda: plato(Lr.mont, Lr.ang(s_r()), 0.55, C_ANT, 5))
        dish_d = always_redraw(lambda: plato(Ld.mont, Ld.ang(s_d()), 0.55, C_ANT, 5, dash=True))
        haz_r = always_redraw(lambda: VGroup(
            Line(Lr.mont, Lr.sat(s_r()), color=C_ANT, stroke_width=8, stroke_opacity=0.16),
            Line(Lr.mont, Lr.sat(s_r()), color=C_ANT, stroke_width=3)))
        haz_d = always_redraw(lambda: DashedLine(Ld.mont, Ld.sat(s_d()), color=C_ANT,
                                                 stroke_width=2.5, dash_length=0.12,
                                                 stroke_opacity=0.75))
        enlace = always_redraw(lambda: DashedLine(Lr.sat(s_r()), Ld.sat(s_d()), color=C_CIELO,
                                                  stroke_width=2, dash_length=0.1,
                                                  stroke_opacity=0.5))
        # barrido holográfico en el gemelo
        barrido = Rectangle(width=w - 0.3, height=0.035, fill_color=C_ANT, fill_opacity=0.13,
                            stroke_width=0).move_to([cx, -3.7, 0])
        fase = {"t": 0.0}

        def mueve_barrido(m, dt):
            fase["t"] = (fase["t"] + dt / 2.6) % 1
            m.move_to([cx, -3.7 + fase["t"] * (hgt - 0.3), 0])
        barrido.add_updater(mueve_barrido)

        # flechas de datos (entre los dos paneles) con pulsos que circulan
        a_dn = flecha([cx - 2.6, 0.27, 0], [cx - 2.6, -0.27, 0], C_CIELO, 3.5, 0.15)
        a_up = flecha([cx + 2.6, -0.27, 0], [cx + 2.6, 0.27, 0], C_CIELO, 3.5, 0.15)
        pd = always_redraw(lambda: Dot([cx - 2.6, 0.27 - 0.54 * ((T() * 9) % 1), 0],
                                       radius=0.06, color=C_SAT))
        pu = always_redraw(lambda: Dot([cx + 2.6, -0.27 + 0.54 * ((T() * 9 + 0.5) % 1), 0],
                                       radius=0.06, color=C_SAT))

        # barra de error
        BX, BY0, BH = 5.55, -2.75, 5.3
        marco_b = RoundedRectangle(corner_radius=0.1, width=0.55, height=BH, color=C_EJE,
                                   stroke_width=2.5).move_to([BX, BY0 + BH / 2, 0])
        e_deg = lambda: abs(np.degrees(Lr.ang(s_r()) - Ld.ang(s_d())))
        col = lambda: interpolate_color(ManimColor(C_OK), ManimColor(C_MAL),
                                        float(np.clip(e_deg() / 5.0, 0, 1)))
        barra = always_redraw(lambda: Rectangle(
            width=0.45, height=max(BH * 0.96 * min(e_deg() / 9.0, 1), 0.05),
            fill_color=col(), fill_opacity=0.95, stroke_width=0
        ).move_to([BX, BY0 + 0.1 + max(BH * 0.96 * min(e_deg() / 9.0, 1), 0.05) / 2, 0]))
        l_e = et("Error", 26, TENUE).move_to([BX, 3.4, 0])
        c_e = cifra_viva(e_deg, "°", 38, col, 1, ancla=np.array([BX - 0.5, 3.0, 0]))

        self.play(FadeIn(marco_r), Create(suelo_r), FadeIn(est_r), FadeIn(l_r), run_time=1.0)
        self.play(Create(orb_r), FadeIn(dish_r), FadeIn(sat_r), run_time=1.0)
        self.add(haz_r)
        self.play(FadeIn(marco_d), Create(suelo_d), FadeIn(est_d), FadeIn(l_d), run_time=0.9)
        self.play(Create(orb_d), FadeIn(dish_d), FadeIn(sat_d), FadeIn(marco_b), FadeIn(l_e),
                  GrowArrow(a_dn), GrowArrow(a_up), run_time=1.0)
        self.add(haz_d, enlace, barra, c_e, pd, pu, barrido)
        self.bring_to_front(sat_r, sat_d)
        self.play(tau.animate.set_value(1), run_time=12.5, rate_func=linear)
        barrido.clear_updaters()
        self.cierre()


# =====================================================================
# 9. NochePases
# =====================================================================
class NochePases(Pieza):
    def construct(self):
        pol = Polar((0, 0.9), 2.55)
        f = pol.fondo(True, tam=26, ang_lbl=315)
        MASC = 10.0
        anillo_m = DashedVMobject(Circle(radius=pol.R * (90 - MASC) / 90, color=C_MAL,
                                         stroke_width=2.5).move_to(pol.c), num_dashes=60)
        l_m = et("Máscara 10°", 22, C_MAL).move_to(pol.p(135, 0) + np.array([1.05, -0.5, 0]))

        # línea de tiempo (21:00 -> 02:00)
        TX0, TX1, TY = -6.0, 6.0, -3.35
        span = 300.0    # min
        xm = lambda m: TX0 + (TX1 - TX0) * m / span
        base_t = Line([TX0, TY, 0], [TX1, TY, 0], color=C_EJE, stroke_width=3)
        ticks = VGroup(*[Line([xm(60 * h), TY, 0], [xm(60 * h), TY - 0.12, 0], color=C_EJE,
                              stroke_width=2.5) for h in range(6)])
        horas = VGroup(*[et(tx, 20, TENUE).move_to([xm(60 * h), TY - 0.36, 0])
                         for h, tx in ((0, "21:00"), (2, "23:00"), (4, "01:00"))])

        defs = [
            dict(elmax=62, az0=-25, lado=1, col=C_SAT, ini=14),
            dict(elmax=26, az0=150, lado=-1, col=C_ANT, ini=66),
            dict(elmax=84, az0=70, lado=1, col=C_CIELO, ini=124),
            dict(elmax=6, az0=-95, lado=1, col=ROSA, ini=182),
            dict(elmax=47, az0=205, lado=-1, col=AZUL, ini=232),
            dict(elmax=33, az0=100, lado=1, col=TINTA, ini=277),
        ]
        self.play(FadeIn(f.disco), Create(f.anillos), Create(f.radios), Create(base_t),
                  run_time=1.4)
        self.play(FadeIn(f.lbl), FadeIn(f.centro), FadeIn(ticks), FadeIn(horas), run_time=0.7)
        self.play(Create(anillo_m), FadeIn(l_m), run_time=0.8)

        for d in defs:
            P = pase(d["elmax"], az0=d["az0"], lado=d["lado"], n=260)
            pts = pol.pts(P.az, P.el)
            N = len(pts)
            tr = ValueTracker(0)
            K = lambda tr=tr, N=N: tr.get_value() * (N - 1)
            col = d["col"]
            trail = always_redraw(lambda pts=pts, K=K, col=col: VGroup(
                polilinea(tramo(pts, K()), col, 9, 0.2),
                polilinea(tramo(pts, K()), col, 4, 1)))
            sat = always_redraw(lambda pts=pts, K=K, col=col:
                                satelite(0.13, color=col).move_to(punto_en(pts, K())))
            # ventana útil (el > máscara)
            util = np.where(P.el >= MASC)[0]
            mala = len(util) == 0
            if mala:
                i0, i1 = 0, N - 1
            else:
                i0, i1 = util[0], util[-1]
            x_a = xm(d["ini"] + P.t[i0] / 60)
            x_b = xm(d["ini"] + P.t[i1] / 60)
            ancho = max(x_b - x_a, 0.12)
            if mala:
                ventana = Rectangle(width=ancho, height=0.55, fill_color=C_MAL, fill_opacity=0.5,
                                    stroke_color=C_MAL, stroke_width=2.5)
            else:
                ventana = Rectangle(width=ancho, height=0.55, fill_color=C_OK, fill_opacity=0.6,
                                    stroke_color=C_OK, stroke_width=2.5)
            ventana.move_to([(x_a + x_b) / 2 if not mala else xm(d["ini"] + P.t[N // 2] / 60),
                             TY + 0.275 + 0.02, 0])
            punto_c = Dot([ventana.get_center()[0], TY + 0.55 + 0.25, 0], radius=0.09, color=col)
            self.add(trail, sat)
            self.play(tr.animate.set_value(1), FadeIn(ventana, scale=0.5), FadeIn(punto_c),
                      run_time=2.4, rate_func=linear)
            trail.clear_updaters()
            sat.clear_updaters()
            if mala:
                cruz = VGroup(Line(UL, DR), Line(UR, DL)).scale(0.13).set_stroke(C_MAL, 4)
                cruz.move_to(punto_c.get_center())
                self.play(FadeOut(sat), trail[0].animate.set_stroke(C_MAL, opacity=0.25),
                          trail[1].animate.set_stroke(C_MAL, opacity=0.95),
                          Transform(punto_c, cruz), run_time=0.7)
            else:
                self.play(FadeOut(sat), run_time=0.3)
        self.cierre()

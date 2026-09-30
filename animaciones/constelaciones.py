"""Constelaciones satelitales: 9 piezas ilustrativas Co.De Aerospace."""
import heapq
from code_lib import *


# ---------------------------------------------------------------- helpers ---
def sat_mini(tam=0.1, color=None):
    c = color or C_SAT
    cuerpo = Square(tam, color=c, fill_color=c, fill_opacity=0.95, stroke_width=1.2)
    g = VGroup(cuerpo)
    for s in (-1, 1):
        p = Rectangle(width=tam * 1.5, height=tam * 0.75, color=c, fill_color=C_CIELO,
                      fill_opacity=0.6, stroke_width=1.2)
        p.next_to(cuerpo, RIGHT * s, buff=tam * 0.1)
        g.add(p)
    fijar_op(g, 1)
    return g


def fijar_op(g, op):
    """Opacidad global que respeta las opacidades base de cada pieza."""
    for m in g.family_members_with_points():
        if not hasattr(m, "_fo"):
            m._fo = m.get_fill_opacity()
            m._so = m.get_stroke_opacity()
        m.set_fill(opacity=m._fo * op)
        m.set_stroke(opacity=m._so * op)


def suave(x, a, b):
    return float(np.clip((x - a) / (b - a), 0, 1))


def contador(unidad, pos, color=None, tam=44, dec=0, sufijo=""):
    """Número vivo (Text, fuente de la librería) anclado a su unidad."""
    col = [color or C_ANT]
    u = Text(unidad, font=FUENTE, font_size=tam * 0.5, color=TENUE).move_to(pos)
    n0 = Text("0" + sufijo, font=FUENTE, font_size=tam, color=col[0])
    n0.next_to(u, LEFT, buff=0.14, aligned_edge=DOWN)
    g = VGroup(n0, u)

    def fijar(v, c=None):
        if c is not None:
            col[0] = c
        txt = (f"{v:.{dec}f}" if dec else f"{int(round(v))}") + sufijo
        n = Text(txt, font=FUENTE, font_size=tam, color=col[0])
        n.next_to(u, LEFT, buff=0.14, aligned_edge=DOWN)
        g[0].become(n)
    return g, fijar


def controlador(scene, fn):
    c = Mobject()
    c.add_updater(lambda m, dt: fn(dt))
    scene.add(c)
    return c


def sat3d(scene, radio=0.1):
    """Satélite 3D barato: disco orientado a cámara con halo."""
    g = VGroup(Dot(radius=radio * 2.1, color=C_SAT).set_fill(opacity=0.25),
               Dot(radius=radio, color=C_SAT))
    g.set_stroke(width=0)
    fijar_op(g, 1)
    scene.add_fixed_orientation_mobjects(g)
    return g


def dir_camara(scene):
    ph, th = scene.camera.get_phi(), scene.camera.get_theta()
    return np.array([np.sin(ph) * np.cos(th), np.sin(ph) * np.sin(th), np.cos(ph)])


def oculto(p, d, Re, minimo=0.15):
    """Factor de visibilidad (1 visible, minimo tras la Tierra)."""
    s = float(p @ d)
    if s >= 0:
        return 1.0
    perp = np.linalg.norm(p - s * d)
    return minimo + (1 - minimo) * suave(perp, Re * 1.0, Re * 1.25)


def dist_seg_origen(a, b):
    ab = b - a
    t = np.clip(-(a @ ab) / (ab @ ab + 1e-9), 0, 1)
    return np.linalg.norm(a + t * ab)


# ======================================================= 1. WalkerDelta3D ===
class WalkerDelta3D(Pieza3D):
    def construct(self):
        Re, R = 1.5, 3.3
        incl = 55 * DEGREES
        P, S = 3, 6
        self.set_camera_orientation(phi=66 * DEGREES, theta=-55 * DEGREES)

        T = ValueTracker(0)
        T.add_updater(lambda m, dt: m.increment_value(dt * 0.42))
        self.add(T)

        tierra3 = esfera_tierra(Re, res=(10, 20))
        ecuador = orbita3d(R, 0, 0, color=C_EJE, ancho=1.5, op=0.6)
        lab_i = et("i = 55°", 26, C_CIELO).to_corner(UL, buff=0.7)
        lab_n = et("3 × 6", 26, C_SAT).next_to(lab_i, DOWN, buff=0.25, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(lab_i, lab_n)
        self.remove(lab_i, lab_n)

        self.begin_ambient_camera_rotation(rate=0.09)
        self.play(FadeIn(tierra3), run_time=1.5)
        self.play(Create(ecuador), FadeIn(lab_i), run_time=1.2)

        vis = [ValueTracker(0) for _ in range(P)]
        sats = []
        for p in range(P):
            raan = p * TAU / P
            for j in range(S):
                ph = j * TAU / S + p * TAU / (P * S)
                d = sat3d(self, 0.1)
                sats.append((d, p, ph, raan))
                fijar_op(d, 0)

        def actualizar(dt):
            cam = dir_camara(self)
            for d, p, ph, raan in sats:
                pos = punto_orbita3d(R, ph + T.get_value(), incl, raan)
                d.move_to(pos)
                fijar_op(d, vis[p].get_value() * oculto(pos, cam, Re))
        ctrl = controlador(self, actualizar)

        anillos = []
        for p in range(P):
            raan = p * TAU / P
            o = orbita3d(R, incl, raan, color=C_CIELO, ancho=2.5, op=0.7)
            anillos.append(o)
            self.play(Create(o), run_time=1.3)
            self.play(vis[p].animate.set_value(1), run_time=0.9)
            if p == 0:
                self.play(FadeIn(lab_n), run_time=0.5)
            self.wait(1.0)
        self.wait(7.0)
        self.remove(T)
        ctrl.clear_updaters()
        self.remove(ctrl)
        self.cierre()


# ====================================================== 2. PlanosOrbitales ===
class PlanosOrbitales(Pieza):
    def construct(self):
        Re, R = 1.45, 3.5
        incl = 55 * DEGREES
        P, S = 6, 6
        theta_c = 30 * DEGREES

        tierra_g = VGroup(Circle(radius=Re, color=C_TIERRA, fill_color=C_TIERRA_2,
                                 fill_opacity=1, stroke_width=2.5))
        for lat in (30, 60):
            tierra_g.add(Circle(radius=Re * np.cos(lat * DEGREES), color=C_EJE,
                                stroke_width=1, stroke_opacity=0.7))
        for lon in range(0, 180, 30):
            a = lon * DEGREES
            tierra_g.add(Line(Re * np.array([np.cos(a), np.sin(a), 0]),
                              -Re * np.array([np.cos(a), np.sin(a), 0]),
                              color=C_EJE, stroke_width=1, stroke_opacity=0.7))

        # puntos de superficie (hemisferio visible desde el polo)
        pts = []
        for lat in (10, 24, 38, 52, 66, 80, 90):
            la = lat * DEGREES
            n = max(1, int(round(28 * np.cos(la))))
            for k in range(n):
                lo = k * TAU / n + (lat % 20) * 0.05
                pts.append(np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]))
        pts = np.array(pts)
        puntos = VGroup(*[Dot(np.array([Re * p[0], Re * p[1], 0]), radius=0.05, color=C_EJE) for p in pts])
        for d in puntos:
            d.set_fill(C_EJE, opacity=0.6)
        nivel = np.zeros(len(pts))

        cont_sat, fijar_sat = contador("satélites", np.array([5.6, 0.0, 0]), C_SAT)
        cont_cob, fijar_cob = contador("cobertura", np.array([-4.9, 0.0, 0]), C_OK, sufijo=" %")

        self.play(FadeIn(tierra_g), FadeIn(puntos), run_time=1.5)
        self.play(FadeIn(cont_sat), FadeIn(cont_cob), run_time=0.6)

        T = [0.0]
        vis = [ValueTracker(0) for _ in range(P)]
        activo = [False] * P
        sats = []
        for p in range(P):
            raan = p * TAU / P
            for j in range(S):
                ph = j * TAU / S + p * (20 * DEGREES)
                g = VGroup(Dot(radius=0.19, color=C_SAT).set_fill(opacity=0.22),
                           Dot(radius=0.095, color=C_SAT))
                fijar_op(g, 1)
                fijar_op(g, 0)
                self.add(g)
                sats.append((g, p, ph, raan))

        def upd(dt):
            T[0] += dt * 0.5
            unit = []
            for g, p, ph, raan in sats:
                pos = punto_orbita3d(R, ph + T[0], incl, raan)
                g.move_to([pos[0], pos[1], 0])
                z = pos[2]
                fijar_op(g, vis[p].get_value() * (1.0 if z > 0 else 0.4))
                g.set_z_index(3 if z > 0 else 1)
                if activo[p] and z > -0.9:
                    unit.append(pos / R)
            if unit:
                U = np.array(unit)
                cubierto = ((pts @ U.T) > np.cos(theta_c)).any(axis=1)
            else:
                cubierto = np.zeros(len(pts), bool)
            for i in range(len(pts)):
                objetivo = 1.0 if cubierto[i] else 0.0
                nivel[i] += np.clip(objetivo - nivel[i], -dt * 2.0, dt * 4.0)
                col = interpolate_color(ManimColor(C_EJE), ManimColor(C_OK), nivel[i])
                puntos[i].set_fill(col, opacity=0.6 + 0.4 * nivel[i])
                puntos[i].set_stroke(width=0)
            fijar_cob(100 * float(np.mean(nivel)))
        ctrl = controlador(self, upd)

        for p in range(P):
            raan = p * TAU / P
            anillo = ParametricFunction(
                lambda t, ra=raan: np.array([*punto_orbita3d(R, t, incl, ra)[:2], 0]),
                t_range=[0, TAU], color=C_CIELO, stroke_width=2.5, stroke_opacity=0.65)
            anillo.set_z_index(0)
            self.play(Create(anillo), run_time=1.0)
            self.play(vis[p].animate.set_value(1), run_time=0.8)
            activo[p] = True
            fijar_sat(S * (p + 1))
            self.wait(0.9)
        self.wait(3.0)
        ctrl.clear_updaters()
        self.remove(ctrl)
        self.cierre()


# =================================================== 3. EnjambreDespliegue ===
class EnjambreDespliegue(Pieza):
    def construct(self):
        Re, R = 1.5, 3.6
        incl = 45 * DEGREES
        P, N = 5, 10
        s0, s1 = 7 * DEGREES, 36 * DEGREES

        tierra_g = tierra(Re)
        T = ValueTracker(0)
        T.add_updater(lambda m, dt: m.increment_value(dt * 0.35))
        self.add(T)

        planos = []
        for p in range(P):
            raan = p * TAU / P
            spread = ValueTracker(s0)
            vis = ValueTracker(0)
            base = 100 * DEGREES + p * 0.9
            sats = VGroup(*[sat_mini(0.14) for _ in range(N)])
            fijar_op(sats, 0)
            anillo = ParametricFunction(
                lambda t, ra=raan: np.array([*punto_orbita3d(R, t, incl, ra)[:2], 0]),
                t_range=[0, TAU], color=C_CIELO, stroke_width=2.2, stroke_opacity=0.6)
            planos.append(dict(raan=raan, spread=spread, vis=vis, base=base, sats=sats,
                               anillo=anillo))
            self.add(sats)

        def upd(dt):
            for pl in planos:
                for k, g in enumerate(pl["sats"]):
                    u = pl["base"] + (k - (N - 1) / 2) * pl["spread"].get_value() + T.get_value()
                    pos = punto_orbita3d(R, u, incl, pl["raan"])
                    g.move_to([pos[0], pos[1], 0])
                    fijar_op(g, pl["vis"].get_value() * (1.0 if pos[2] > 0 else 0.4))
                    g.set_z_index(3 if pos[2] > 0 else 1)
        ctrl = controlador(self, upd)

        self.play(FadeIn(tierra_g), run_time=1.0)
        # primer plano: tren compacto
        pl0 = planos[0]
        self.play(Create(pl0["anillo"]), run_time=1.0)
        self.play(pl0["vis"].animate.set_value(1), run_time=1.0)
        self.wait(1.2)
        self.play(pl0["spread"].animate.set_value(s1), run_time=4.0, rate_func=smooth)
        self.wait(0.5)
        # réplica en más planos
        for pl in planos[1:]:
            self.play(Create(pl["anillo"]), run_time=0.6)
            self.play(pl["vis"].animate.set_value(1), run_time=0.5)
            self.play(pl["spread"].animate.set_value(s1), run_time=2.2, rate_func=smooth)
        self.wait(2.5)
        ctrl.clear_updaters()
        self.remove(ctrl, T)
        self.cierre()


# ==================================================== 4. HandoverSatelital ===
class HandoverSatelital(Pieza):
    def construct(self):
        C = np.array([0, -8.0, 0])
        Re, Ro = 7.2, 9.6
        U = C + np.array([0, Re, 0])
        MASK = 25 * DEGREES
        SP = 30.0
        V = 6.5  # grados/s

        superficie = Circle(radius=Re, color=C_TIERRA, fill_color=C_TIERRA_2,
                            fill_opacity=1, stroke_width=3).move_to(C)
        atm = Circle(radius=Re + 0.18, color=C_TIERRA, stroke_width=1.5,
                     stroke_opacity=0.35).move_to(C)
        orbita = Arc(radius=Ro, start_angle=90 * DEGREES - 55 * DEGREES, angle=110 * DEGREES,
                     arc_center=C, color=C_CIELO, stroke_width=2, stroke_opacity=0.5)
        est = estacion(0.8).move_to(U + UP * 0.34)
        est.set_z_index(5)

        # cono de visibilidad por elevación mínima (hasta la órbita)
        def elev_th(th):
            p = C + Ro * np.array([np.sin(th), np.cos(th), 0])
            v = p - U
            return np.arctan2(v[1], abs(v[0]))
        lo, hi = 0.0, 60 * DEGREES
        for _ in range(60):
            mid_ = (lo + hi) / 2
            if elev_th(mid_) > MASK:
                lo = mid_
            else:
                hi = mid_
        thm = lo
        pd = C + Ro * np.array([np.sin(thm), np.cos(thm), 0])
        pi_ = C + Ro * np.array([-np.sin(thm), np.cos(thm), 0])
        arco_o = [C + Ro * np.array([np.sin(t), np.cos(t), 0]) for t in np.linspace(thm, -thm, 30)]
        cono = Polygon(U, *arco_o, stroke_width=0, fill_color=C_CIELO, fill_opacity=0.10)
        lin_d = DashedLine(U, pd, color=C_CIELO, stroke_width=2.5, dash_length=0.15, stroke_opacity=0.8)
        lin_i = DashedLine(U, pi_, color=C_CIELO, stroke_width=2.5, dash_length=0.15, stroke_opacity=0.8)
        arco = Arc(radius=1.5, start_angle=0, angle=MASK, arc_center=U, color=C_CIELO, stroke_width=3.5)
        lab = et("25° mín", 24, C_CIELO).move_to(U + np.array([2.55, 0.62, 0]))

        self.play(FadeIn(superficie), FadeIn(atm), Create(orbita), run_time=1.5)
        self.play(FadeIn(est), FadeIn(cono), Create(lin_d), Create(lin_i), run_time=1.2)
        self.play(Create(arco), FadeIn(lab), run_time=0.8)

        K = 8
        sats = []
        for k in range(K):
            g = sat_mini(0.24)
            ring = Circle(radius=0.52, color=C_OK, stroke_width=3)
            ring.set_stroke(opacity=0)
            g2 = VGroup(g, ring)
            sats.append(g2)
            self.add(g2)
            g2.set_z_index(4)
            g2.set_opacity(0)

        st = dict(t=0.0, activo=None, previo=None, t_cambio=-9.0, go=False)

        def theta_k(k, t):
            return (-70 + k * SP + V * t) * DEGREES

        def pos_sat(th):
            return C + Ro * np.array([np.sin(th), np.cos(th), 0])

        def elev(p):
            v = p - U
            return np.arctan2(v[1], abs(v[0]))

        haz_a = DashedLine(U, U + UP, color=C_ANT, stroke_width=3.5, dash_length=0.14)
        haz_p = DashedLine(U, U + UP, color=C_ANT, stroke_width=3, dash_length=0.14)
        haz_a.set_z_index(3)
        haz_p.set_z_index(3)
        haz_a.set_stroke(opacity=0)
        haz_p.set_stroke(opacity=0)
        self.add(haz_p, haz_a)

        def upd(dt):
            if not st["go"]:
                return
            st["t"] += dt
            t = st["t"]
            mejor, me = None, -9
            for k, g2 in enumerate(sats):
                th = theta_k(k, t)
                p = pos_sat(th)
                e = elev(p)
                if e > MASK and p[1] > U[1] and e > me:
                    mejor, me = k, e
                g2.move_to(p)
                g2.rotate(0)
            if mejor != st["activo"]:
                st["previo"] = st["activo"]
                st["activo"] = mejor
                st["t_cambio"] = t
            for k, g2 in enumerate(sats):
                p = pos_sat(theta_k(k, t))
                borde = suave(7.0 - abs(p[0]), 0, 1.3)
                g = g2[0]
                act = (k == st["activo"])
                col = C_OK if act else C_SAT
                g[0].set_fill(col, opacity=0.95 * borde)
                g[0].set_stroke(col, opacity=borde)
                for pn in g[1:]:
                    pn.set_fill(C_CIELO, opacity=0.6 * borde)
                    pn.set_stroke(col, opacity=borde)
                g2[1].set_stroke(C_OK, opacity=(borde if act else 0))
                g2[1].move_to(p)
            # haces
            def poner(h, k, op):
                if k is None or op <= 0.01:
                    h.set_stroke(opacity=0)
                    return
                p = pos_sat(theta_k(k, t))
                h.become(DashedLine(U + UP * 0.85, p, color=C_ANT, stroke_width=h.get_stroke_width(),
                                    dash_length=0.14).set_z_index(3))
                h.set_stroke(opacity=op)
            poner(haz_a, st["activo"], 0.95)
            fade = 1 - suave(t - st["t_cambio"], 0, 0.9)
            poner(haz_p, st["previo"], 0.7 * fade)
        ctrl = controlador(self, upd)
        st["go"] = True
        self.wait(20.0)
        st["go"] = False
        ctrl.clear_updaters()
        self.remove(ctrl)
        self.cierre()


# ============================================================== 5. MallaISL ===
class MallaISL(Pieza3D):
    def construct(self):
        Re, R = 1.5, 3.3
        incl = 55 * DEGREES
        P, S = 4, 6
        self.set_camera_orientation(phi=66 * DEGREES, theta=-40 * DEGREES)
        T = ValueTracker(0)
        T.add_updater(lambda m, dt: m.increment_value(dt * 0.3))
        self.add(T)

        def posn(p, j):
            ph = j * TAU / S + p * TAU / (P * S)
            return punto_orbita3d(R, ph + T.get_value(), incl, p * TAU / P)

        tierra3 = esfera_tierra(Re, res=(10, 20))
        vis = ValueTracker(0)
        sats = [[sat3d(self, 0.085) for _ in range(S)] for _ in range(P)]
        for fila in sats:
            for d in fila:
                fijar_op(d, 0)

        g_in, g_out = ValueTracker(0), ValueTracker(0)
        enlaces = []

        def nuevo_enlace(a, b, k, n, g, grosor, base):
            ln = Line(ORIGIN, RIGHT, color=C_ANT, stroke_width=grosor)
            ln.set_stroke(opacity=0)
            self.add(ln)
            enlaces.append((ln, a, b, k, n, g, base))

        k = 0
        for p in range(P):
            for j in range(S):
                nuevo_enlace((p, j), (p, (j + 1) % S), k, P * S, g_in, 3.2, 0.95)
                k += 1
        k = 0
        for p in range(P):
            for j in range(S):
                nuevo_enlace((p, j), ((p + 1) % P, j), k, P * S, g_out, 2.6, 0.8)
                k += 1

        def upd(dt):
            cam = dir_camara(self)
            for p in range(P):
                for j in range(S):
                    pos = posn(p, j)
                    d = sats[p][j]
                    d.move_to(pos)
                    fijar_op(d, vis.get_value() * oculto(pos, cam, Re))
            for ln, a, b, k, n, g, base in enlaces:
                pa, pb = posn(*a), posn(*b)
                r = float(np.clip(g.get_value() * (n + 6) - k, 0, 1))
                if r < 0.01:
                    ln.set_stroke(opacity=0)
                    continue
                end = pa + r * (pb - pa)
                ln.put_start_and_end_on(pa, end)
                dm = dist_seg_origen(pa, pb)
                fac = suave(dm, Re, Re + 0.5)
                op = base * oculto((pa + pb) / 2, cam, Re, 0.12) * (0.1 + 0.9 * fac)
                ln.set_stroke(opacity=op)
        ctrl = controlador(self, upd)

        self.begin_ambient_camera_rotation(rate=0.07)
        self.play(FadeIn(tierra3), run_time=1.3)
        orbs = [orbita3d(R, incl, p * TAU / P, color=C_CIELO, ancho=1.8, op=0.4) for p in range(P)]
        self.play(*[Create(o) for o in orbs], run_time=1.5)
        self.play(vis.animate.set_value(1), run_time=1.0)
        self.wait(0.5)
        self.play(g_in.animate.set_value(1), run_time=5.0, rate_func=linear)
        self.wait(0.4)
        self.play(g_out.animate.set_value(1), run_time=5.0, rate_func=linear)
        self.wait(5.0)
        ctrl.clear_updaters()
        self.remove(ctrl, T)
        self.cierre()


# ======================================================= 6. EnrutamientoMalla ===
class EnrutamientoMalla(Pieza):
    def construct(self):
        NC, NR = 7, 4
        X0, DX, Y0, DY = -5.4, 1.8, 2.9, -1.0

        def P(i, j):
            return np.array([X0 + i * DX, Y0 + j * DY, 0])

        # Tierra (arco) y ciudades
        cy = -32.6
        suelo = Circle(radius=30, color=C_TIERRA, fill_color=C_TIERRA_2, fill_opacity=1,
                       stroke_width=3).move_to([0, cy, 0])

        def sobre_suelo(x):
            return np.array([x, cy + np.sqrt(30 ** 2 - x ** 2), 0])
        ca = sobre_suelo(-5.4) + UP * 0.4
        cb = sobre_suelo(5.4) + UP * 0.4
        icono_a = estacion(0.75).move_to(ca)
        icono_b = estacion(0.75).move_to(cb)
        lab_a = et("Bogotá", 24, TINTA).move_to(sobre_suelo(-5.4) + DOWN * 0.45)
        lab_b = et("Madrid", 24, TINTA).move_to(sobre_suelo(5.4) + DOWN * 0.45)

        nodos = {(i, j): satelite(0.14).move_to(P(i, j)) for i in range(NC) for j in range(NR)}
        aristas = {}
        lineas = {}
        for i in range(NC):
            for j in range(NR):
                for (di, dj) in ((1, 0), (0, 1)):
                    a, b = (i, j), (i + di, j + dj)
                    if b in nodos:
                        w = 1.8 if di else 1.0
                        aristas[frozenset((a, b))] = w
                        lineas[frozenset((a, b))] = Line(P(*a), P(*b), color=C_ANT,
                                                         stroke_width=2.5, stroke_opacity=0.55)

        def vecinos(n, prohibidas):
            i, j = n
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                m = (i + di, j + dj)
                e = frozenset((n, m))
                if m in nodos and e not in prohibidas:
                    yield m, aristas[e]

        def dijkstra(ini, fin, prohibidas=()):
            dist, prev, cola = {ini: 0}, {}, [(0, ini)]
            while cola:
                d, n = heapq.heappop(cola)
                if n == fin:
                    break
                if d > dist[n]:
                    continue
                for m, w in vecinos(n, prohibidas):
                    nd = d + w + 0.001 * (NR - m[1]) * 0
                    if nd < dist.get(m, 1e9) - 1e-9:
                        dist[m], prev[m] = nd, n
                        heapq.heappush(cola, (nd, m))
            ruta, n = [fin], fin
            while n != ini:
                n = prev[n]
                ruta.append(n)
            return ruta[::-1]

        def poli(ruta, color, ancho=6):
            v = VMobject(color=color, stroke_width=ancho)
            v.set_points_as_corners([P(*n) for n in ruta])
            return v

        self.play(FadeIn(suelo), FadeIn(icono_a), FadeIn(icono_b), FadeIn(lab_a), FadeIn(lab_b),
                  run_time=1.0)
        self.play(LaggedStart(*[FadeIn(n, scale=0.5) for n in nodos.values()], lag_ratio=0.03),
                  run_time=1.5)
        self.play(LaggedStart(*[Create(l) for l in lineas.values()], lag_ratio=0.04), run_time=2.0)

        ini, fin = (0, NR - 1), (NC - 1, NR - 1)
        ruta = dijkstra(ini, fin)
        # enlace de subida
        sube = DashedLine(ca + UP * 0.3, P(*ini), color=C_ANT, stroke_width=3.5, dash_length=0.13)
        baja = DashedLine(P(*fin), cb + UP * 0.3, color=C_ANT, stroke_width=3.5, dash_length=0.13)
        paquete = Dot(ca + UP * 0.3, radius=0.14, color=C_SAT)
        halo = Dot(radius=0.28, color=C_SAT).set_fill(opacity=0.3)
        halo.add_updater(lambda m: m.move_to(paquete))
        paquete.set_z_index(6)
        halo.set_z_index(5)

        r_tot = poli(ruta, C_ANT, 6)
        self.play(Create(sube), run_time=0.6)
        self.play(Create(r_tot), run_time=1.6)
        self.add(halo)
        self.play(FadeIn(paquete), run_time=0.3)
        self.play(paquete.animate.move_to(P(*ini)), run_time=0.7, rate_func=linear)

        vel = 3.0

        def viaje(puntos):
            for a, b in zip(puntos[:-1], puntos[1:]):
                d = np.linalg.norm(P(*b) - P(*a))
                self.play(paquete.animate.move_to(P(*b)), run_time=d / vel, rate_func=linear)

        falla_a, falla_b = (3, NR - 1), (4, NR - 1)
        falla = frozenset((falla_a, falla_b))
        idx = ruta.index(falla_a)
        viaje(ruta[:idx + 1])
        # el enlace falla
        mid = (P(*falla_a) + P(*falla_b)) / 2
        cruz = VGroup(Line(mid + 0.22 * (UL), mid + 0.22 * DR, color=C_MAL, stroke_width=6),
                      Line(mid + 0.22 * (UR), mid + 0.22 * DL, color=C_MAL, stroke_width=6))
        cruz.set_z_index(7)
        self.play(lineas[falla].animate.set_color(C_MAL).set_stroke(width=5, opacity=1),
                  Create(cruz), run_time=0.5)
        self.play(Indicate(cruz, color=C_MAL, scale_factor=1.3), run_time=0.7)
        restante = poli(ruta[idx:], C_ANT, 6)
        hecho = poli(ruta[:idx + 1], C_ANT, 6)
        self.remove(r_tot)
        self.add(hecho, restante)
        nueva = dijkstra(falla_a, fin, prohibidas={falla})
        r_new = poli(nueva, C_ANT, 6)
        self.play(FadeOut(restante), run_time=0.5)
        self.play(Create(r_new), run_time=1.6)
        viaje(nueva)
        self.play(Create(baja), run_time=0.5)
        self.play(paquete.animate.move_to(cb + UP * 0.3), run_time=0.7, rate_func=linear)
        self.play(hecho.animate.set_color(C_OK), r_new.animate.set_color(C_OK),
                  sube.animate.set_color(C_OK), baja.animate.set_color(C_OK),
                  paquete.animate.set_color(C_OK), run_time=0.8)
        halo.clear_updaters()
        self.play(Indicate(icono_b, color=C_OK, scale_factor=1.25), run_time=0.8)
        self.cierre()


# ================================================== 7. CoberturaHexagonal ===
class CoberturaHexagonal(Pieza):
    def construct(self):
        Rh, sq, gy = 0.62, 0.62, -1.0
        cols = [C_ANT, C_CIELO, C_OK]
        celdas = []
        for q in range(-10, 11):
            for r in range(-10, 11):
                x = 1.5 * Rh * q
                y = np.sqrt(3) * Rh * (r + q / 2) * sq + gy
                if abs(x) <= 6.4 and -3.2 <= y <= 1.6:
                    verts = [[x + Rh * np.cos(k * PI / 3), y + Rh * sq * np.sin(k * PI / 3), 0]
                             for k in range(6)]
                    h = Polygon(*verts, color=C_EJE, stroke_width=1.6, stroke_opacity=0.6,
                                fill_color=cols[(q - r) % 3], fill_opacity=0)
                    celdas.append((h, x, y, (q - r) % 3))
        nivel = np.zeros(len(celdas))
        grupo = VGroup(*[c[0] for c in celdas])

        fx = ValueTracker(-5.0)
        onda = ValueTracker(-0.3)
        RX, RY = 2.5, 2.5 * sq
        sat = sat_mini(0.24).move_to([-5.0, 3.0, 0])
        sat.add_updater(lambda m: m.move_to([fx.get_value(), 3.0, 0]))
        modo = dict(go=False)

        def cono_f():
            x = fx.get_value()
            return Polygon([x, 2.75, 0], [x - RX, gy, 0], [x + RX, gy, 0], stroke_width=0,
                           fill_color=C_ANT, fill_opacity=0.10)

        def huella_f():
            return Ellipse(width=2 * RX, height=2 * RY, color=C_ANT, stroke_width=3,
                           fill_color=C_ANT, fill_opacity=0.06).move_to([fx.get_value(), gy, 0])
        cono = always_redraw(cono_f)
        huella = always_redraw(huella_f)
        for m in (cono, huella):
            m.set_z_index(2)
        sat.set_z_index(6)
        vis_sat = ValueTracker(0)

        def upd(dt):
            x0 = fx.get_value()
            w = onda.get_value()
            for i, (h, x, y, ci) in enumerate(celdas):
                d = np.sqrt(((x - x0) / RX) ** 2 + ((y - gy) / RY) ** 2)
                a = suave(1 - d, 0, 0.25) if modo["go"] else 0.0
                b = suave(w - np.hypot(x / 6.5, (y - gy) / 2.5), 0, 0.3)
                objetivo = max(a, b)
                if objetivo > nivel[i]:
                    nivel[i] = objetivo
                else:
                    nivel[i] = max(objetivo, nivel[i] - dt * 0.9)
                h.set_fill(cols[ci], opacity=0.62 * nivel[i])
                h.set_stroke(cols[ci] if nivel[i] > 0.05 else C_EJE,
                             opacity=0.6 + 0.4 * nivel[i])
            fijar_op(sat, vis_sat.get_value())
        ctrl = controlador(self, upd)

        self.play(LaggedStart(*[FadeIn(c[0]) for c in celdas], lag_ratio=0.008), run_time=2.4)
        self.add(cono, huella, sat)
        self.play(vis_sat.animate.set_value(1), run_time=0.8)
        modo["go"] = True
        self.play(fx.animate.set_value(5.0), run_time=11.0, rate_func=linear)
        modo["go"] = False
        self.play(vis_sat.animate.set_value(0), FadeOut(cono), FadeOut(huella), run_time=0.8)
        self.play(onda.animate.set_value(1.7), run_time=2.6, rate_func=smooth)
        self.wait(0.5)
        ctrl.clear_updaters()
        sat.clear_updaters()
        self.remove(ctrl, sat)
        self.cierre()


# ================================================== 8. ComparaLatencia ===
class ComparaLatencia(Pieza):
    def construct(self):
        self.add(et("Solo propagación", 20, TENUE).to_corner(UL, buff=0.4))
        suelo_y = -3.0
        lanes = [
            ("LEO", "550 km", 0.9, 7, -4.6),
            ("MEO", "8 000 km", 2.6, 107, 0.0),
            ("GEO", "35 786 km", 5.0, 477, 4.6),
        ]
        vel = 2.3
        linea = Line([-7.0, suelo_y, 0], [7.0, suelo_y, 0], color=C_TIERRA, stroke_width=6)
        self.play(Create(linea), run_time=0.8)

        trackers, elems = [], []
        anims_in = []
        for nombre, alt, h, ms, x in lanes:
            u = np.array([x - 1.35, suelo_y, 0])
            g = np.array([x + 1.35, suelo_y, 0])
            s = np.array([x, suelo_y + h, 0])
            ic_u = estacion(0.4).move_to(u + UP * 0.28)
            ic_g = estacion(0.4, C_CIELO).move_to(g + UP * 0.28)
            sat = satelite(0.26).move_to(s)
            eti = et(nombre, 28, TINTA).next_to(sat, UP, buff=0.28)
            eti_alt = et(alt, 20, TENUE).next_to(sat, RIGHT, buff=0.55)
            guia = DashedLine(s + DOWN * 0.3, u + UP * 0.02, color=C_EJE, stroke_width=1.5,
                              stroke_opacity=0.0)
            camino = VMobject()
            pu, pg = u + UP * 0.55, g + UP * 0.55
            camino.set_points_as_corners([pu, s, pg, s, pu])
            fondo = VMobject(color=C_EJE, stroke_width=1.6, stroke_opacity=0.5)
            fondo.set_points_as_corners([pu, s, pg])
            longitud = 4 * np.linalg.norm(s - pu)
            anims_in += [FadeIn(ic_u), FadeIn(ic_g), FadeIn(sat), FadeIn(eti), FadeIn(eti_alt),
                         Create(fondo)]
            p = ValueTracker(0)
            trackers.append((p, longitud))
            elems.append((camino, sat, ms, x))
        self.play(*anims_in, run_time=1.5)

        contadores = []
        objetos = []
        for (camino, sat, ms, x), (p, longitud) in zip(elems, trackers):
            traza = always_redraw(lambda c=camino, p=p: VMobject(color=C_ANT, stroke_width=4.5).pointwise_become_partial(
                c, 0, max(p.get_value(), 1e-3)))
            punto = Dot(radius=0.13, color=C_ANT)
            halo = Dot(radius=0.26, color=C_ANT).set_fill(opacity=0.28)
            punto.set_z_index(6)
            halo.set_z_index(5)
            punto.add_updater(lambda m, c=camino, p=p: m.move_to(c.point_from_proportion(min(p.get_value(), 0.999))))
            halo.add_updater(lambda m, q=punto: m.move_to(q))
            cont, fijar = contador("ms", np.array([x + 0.9, -3.62, 0]), TINTA, tam=40)
            aprox = et("≈", 32, TENUE).next_to(cont[0], LEFT, buff=0.2)
            fijar(0)
            cont.set_opacity(1)
            aprox.move_to([x - 0.6, -3.6, 0])
            contadores.append((cont, fijar, aprox, ms))
            objetos += [traza, punto, halo, cont, aprox]
        self.add(*objetos)
        self.wait(0.4)

        durs = [lg / vel for (_, lg) in trackers]
        reloj = [0.0]

        def upd(dt):
            reloj[0] += dt
            for k, ((p, lg), (cont, fijar, aprox, ms)) in enumerate(zip(trackers, contadores)):
                d = durs[k]
                if k < 2:
                    ph = reloj[0] % (d + 0.7)
                else:
                    ph = min(reloj[0], d)
                v = min(ph / d, 1.0)
                p.set_value(v)
                fijar(ms * v, C_OK if v >= 1 else TINTA)
        ctrl = controlador(self, upd)
        self.wait(durs[2] + 0.2)
        ctrl.clear_updaters()
        self.remove(ctrl)
        for (p, lg), (cont, fijar, aprox, ms) in zip(trackers, contadores):
            p.set_value(1)
            fijar(ms, C_OK)
        for (camino, sat, _, x) in elems:
            sat[0].set_color(C_OK)
        self.wait(0.3)
        self.cierre()


# ================================================= 9. TopologiaRespira ===
class TopologiaRespira(Pieza):
    def construct(self):
        anillos = [(1.9, 5, 0.45), (2.7, 6, -0.30), (3.3, 7, 0.20)]
        XS = 1.7
        THR, MAR = 1.9, 0.3
        nodos = []
        for a, n, w in anillos:
            for k in range(n):
                nodos.append((a, k * TAU / n + a, w))
        N = len(nodos)
        T = [0.0]

        def pos(i):
            a, ph, w = nodos[i]
            ang = ph + w * T[0]
            return np.array([a * XS * np.cos(ang), a * np.sin(ang), 0])

        guias = VGroup(*[Ellipse(width=2 * a * XS, height=2 * a, color=C_EJE, stroke_width=1.3,
                                 stroke_opacity=0.55) for a, _, _ in anillos])
        tierra_g = tierra(0.85)
        pares = [(i, j) for i in range(N) for j in range(i + 1, N)]
        lineas = {}
        for (i, j) in pares:
            l = Line(ORIGIN, RIGHT, color=C_ANT, stroke_width=3)
            l.set_stroke(opacity=0)
            lineas[(i, j)] = l
        puntos = VGroup(*[Dot(radius=0.13, color=C_SAT) for _ in range(N)])
        halos = VGroup(*[Dot(radius=0.26, color=C_SAT).set_fill(opacity=0.2) for _ in range(N)])
        for l in lineas.values():
            l.set_z_index(1)
        puntos.set_z_index(3)
        halos.set_z_index(2)

        cont, fijar = contador("enlaces activos", np.array([5.0, 3.5, 0]), C_ANT, tam=50)
        marca = ValueTracker(0)

        def upd(dt):
            T[0] += dt
            P = [pos(i) for i in range(N)]
            activos = 0
            for i in range(N):
                puntos[i].move_to(P[i])
                halos[i].move_to(P[i])
            for (i, j), l in lineas.items():
                d = np.linalg.norm(P[i] - P[j])
                op = suave(THR + MAR - d, 0, MAR) * marca.get_value()
                if op < 0.02:
                    l.set_stroke(opacity=0)
                    continue
                l.put_start_and_end_on(P[i], P[j])
                l.set_stroke(color=C_ANT, opacity=0.9 * op)
                if d < THR:
                    activos += 1
            if marca.get_value() > 0.99:
                fijar(activos)
        ctrl = controlador(self, upd)
        # posiciones iniciales
        for i in range(N):
            puntos[i].move_to(pos(i))
            halos[i].move_to(pos(i))
        for l in lineas.values():
            self.add(l)

        self.play(FadeIn(tierra_g), Create(guias), run_time=1.2)
        self.play(FadeIn(halos), FadeIn(puntos), run_time=1.0)
        self.play(FadeIn(cont), run_time=0.5)
        self.play(marca.animate.set_value(1), run_time=1.0)
        self.wait(19.0)
        ctrl.clear_updaters()
        self.remove(ctrl)
        self.cierre()

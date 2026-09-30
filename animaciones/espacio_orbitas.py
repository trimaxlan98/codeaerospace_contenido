"""Espacio y órbitas — escenas Manim para Co.De Aerospace.

Cada clase = un video independiente, sin narración ni títulos.
Uso: manim render -ql espacio_orbitas.py NombreClase
"""
from code_lib import *

MU_TIERRA = 398600.0      # km^3/s^2
R_TIERRA = 6371.0         # km


# ----------------------------------------------------------------------------
# helpers comunes
# ----------------------------------------------------------------------------
def dv(n, tam=30, color=None):
    """Etiqueta Δv con subíndice (una sola etiqueta)."""
    a = Text("Δv", font=FUENTE, font_size=tam, color=color or TINTA)
    b = Text(str(n), font=FUENTE, font_size=tam * 0.6, color=color or TINTA)
    b.next_to(a, RIGHT, buff=0.03).shift(DOWN * 0.09)
    return VGroup(a, b)


def kepler_E(M, e):
    """Anomalía excéntrica por Newton-Raphson."""
    E = M + e * np.sin(M)
    for _ in range(40):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E


def suave(x):
    x = float(np.clip(x, 0, 1))
    return x * x * (3 - 2 * x)


def polilinea(pts, **kw):
    m = VMobject(**kw)
    m.set_points_as_corners([np.array([p[0], p[1], 0.0]) for p in pts])
    return m


def flama(pos, u, largo=0.55, ancho=0.13):
    """Llama de propulsión detrás del punto `pos`, con dirección de avance `u`."""
    u = np.array(u, dtype=float)
    u = u / np.linalg.norm(u)
    n = np.array([-u[1], u[0], 0])
    base = pos - u * largo
    ext = Polygon(pos - u * 0.04 + n * ancho, pos - u * 0.04 - n * ancho, base,
                  color=C_SAT, fill_color=C_SAT, fill_opacity=0.95, stroke_width=0)
    base2 = pos - u * largo * 0.55
    inte = Polygon(pos - u * 0.04 + n * ancho * 0.5, pos - u * 0.04 - n * ancho * 0.5, base2,
                   color=TINTA, fill_color=TINTA, fill_opacity=0.9, stroke_width=0)
    return VGroup(ext, inte)


# ----------------------------------------------------------------------------
# 1. Cañón de Newton
# ----------------------------------------------------------------------------
def _newton(v_km, r0, n_max=240):
    """Integra (leapfrog) una trayectoria. Unidades: R=1, GM=1 (vc(R)=7.91 km/s)."""
    v = v_km / 7.8 / np.sqrt(r0)   # 7.8 km/s = velocidad circular a r0
    dt = 0.0005
    p = np.array([0.0, r0])
    w = np.array([v, 0.0])
    inv_a = 2 / r0 - v * v
    a = 1 / inv_a
    T = 2 * np.pi * a ** 1.5
    orbita = (2 * a - r0) > 1.0 and v_km > 7.7
    ts, ps = [0.0], [p.copy()]
    t = 0.0
    aterriza = False
    while t < T * 1.0005:
        acc = -p / np.linalg.norm(p) ** 3
        w = w + acc * dt * 0.5
        p_new = p + w * dt
        acc2 = -p_new / np.linalg.norm(p_new) ** 3
        w = w + acc2 * dt * 0.5
        t += dt
        if np.linalg.norm(p_new) < 1.0:
            # interpola hasta r = 1
            r_a, r_b = np.linalg.norm(p), np.linalg.norm(p_new)
            f = (r_a - 1.0) / max(r_a - r_b, 1e-12)
            p_new = p + (p_new - p) * f
            t = t - dt + dt * f
            ts.append(t)
            ps.append(p_new / np.linalg.norm(p_new))
            aterriza = True
            break
        p = p_new
        ts.append(t)
        ps.append(p.copy())
    ts = np.array(ts)
    ps = np.array(ps)
    n = min(n_max, len(ts))
    tt = np.linspace(0, ts[-1], n)
    xs = np.interp(tt, ts, ps[:, 0])
    ys = np.interp(tt, ts, ps[:, 1])
    m = np.stack([xs, ys], axis=1)
    if orbita and not aterriza:
        m[-1] = m[0]
    return m, aterriza, ts[-1]


class CaidaLibreNewton(Pieza):
    def construct(self):
        R = 2.75
        r0 = 1.12
        self.add(estrellas(60, 11))

        globo = tierra(R)
        atm = Circle(radius=R * 1.035, color=C_ANT, stroke_width=7, stroke_opacity=0.22)
        # montaña y cañón
        cima = np.array([0, R * r0, 0])
        yb = lambda x: np.sqrt(R ** 2 - x ** 2)
        monte = Polygon([-0.45, yb(0.45) - 0.05, 0], [0.45, yb(0.45) - 0.05, 0], cima,
                        color=TENUE, fill_color=C_EJE, fill_opacity=1, stroke_width=2)
        canon = VGroup(
            RoundedRectangle(corner_radius=0.04, width=0.46, height=0.15, color=TINTA,
                             fill_color=TENUE, fill_opacity=1, stroke_width=1.5),
            Dot(radius=0.07, color=TINTA),
        )
        canon[0].move_to(cima + np.array([-0.16, 0.1, 0]))
        canon[1].move_to(cima + np.array([-0.28, 0.06, 0]))

        self.play(FadeIn(globo), FadeIn(atm), run_time=1.0)
        self.play(FadeIn(monte), FadeIn(canon), run_time=0.7)
        self.respiro(0.3)

        colores = [TENUE, C_CIELO, C_ANT, C_SAT]
        velocidades = [3, 5, 7, 7.8]
        duraciones = [2.0, 2.6, 3.4, 5.2]
        pos_lab = np.array([-4.3, 3.5, 0.0])
        anterior = None
        trazos = []

        for k, (v, col, dur) in enumerate(zip(velocidades, colores, duraciones)):
            muestras, aterriza, _ = _newton(v, r0)
            pts = np.array([[m[0] * R, m[1] * R, 0.0] for m in muestras])
            N = len(pts)

            # indicador de velocidad: flecha + cifra
            flecha_v = flecha(np.array([-5.5, 2.95, 0]),
                              np.array([-5.5 + v * 0.3, 2.95, 0]), color=col, ancho=5, punta=0.22)
            num = cifra(v, "km/s", tam=34, color=col, decimales=1 if v % 1 else 0)
            num.move_to(pos_lab)
            grupo_v = VGroup(flecha_v, num)
            if anterior is None:
                self.play(FadeIn(grupo_v), run_time=0.5)
            else:
                self.play(ReplacementTransform(anterior, grupo_v), run_time=0.5)
            anterior = grupo_v

            bola = Dot(pts[0], radius=0.09, color=col)
            bola.set_z_index(5)
            trazo = VMobject(color=col, stroke_width=4.5, stroke_opacity=0.95)
            trazo.set_points_as_corners(pts[:2])
            trazo.set_z_index(3)
            self.add(trazo)

            def act(m, a, pts=pts, N=N, bola=bola, trazo=trazo):
                i = int(round(a * (N - 1)))
                i = max(1, min(N - 1, i))
                bola.move_to(pts[i])
                trazo.set_points_as_corners(pts[:i + 1])

            self.add(bola)
            if k < 3:
                self.play(UpdateFromAlphaFunc(bola, act, rate_func=linear, run_time=dur))
                self.play(Flash(pts[-1], color=col, line_length=0.18, flash_radius=0.22,
                                num_lines=9, run_time=0.5),
                          trazo.animate.set_stroke(opacity=0.8), FadeOut(bola))
            else:
                # primera vuelta
                self.play(UpdateFromAlphaFunc(bola, act, rate_func=linear, run_time=dur))
                self.play(Flash(pts[0], color=C_SAT, line_length=0.2, flash_radius=0.3,
                                num_lines=10, run_time=0.5))
                # el proyectil se convierte en satélite y sigue orbitando
                sat = satelite(0.2)
                sat.set_z_index(6)
                sat.move_to(pts[-1])
                self.play(FadeOut(bola, run_time=0.3), FadeIn(sat, run_time=0.3))

                def vuelta(m, a, pts=pts, N=N):
                    i = int(a * (N - 1)) % N
                    m.move_to(pts[i])

                self.play(UpdateFromAlphaFunc(sat, vuelta, rate_func=linear, run_time=3.6))
            self.respiro(0.15)

        self.cierre()


# ----------------------------------------------------------------------------
# 2. LEO / MEO / GEO
# ----------------------------------------------------------------------------
class OrbitasLEOMEOGEO(Pieza):
    def construct(self):
        C = np.array([-2.4, 0, 0])
        Re = 0.55
        self.add(estrellas(60, 5))
        globo = tierra(Re)
        globo.move_to(C)
        atm = Circle(radius=Re * 1.06, color=C_ANT, stroke_width=5, stroke_opacity=0.25).move_to(C)

        # (nombre, radio en pantalla, color, altitud, periodo real min, nº sats)
        capas = [
            ("LEO", 0.95, C_ANT, "550 km", "95 min", 95.5, 3),
            ("MEO", 2.30, C_CIELO, "20 200 km", "12 h", 717.9, 3),
            ("GEO", 3.62, C_OK, "35 786 km", "24 h", 1436.1, 3),
        ]
        T_GEO = 20.0  # segundos de animación por vuelta GEO
        reloj = ValueTracker(0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))

        self.play(FadeIn(globo), FadeIn(atm), run_time=0.9)
        self.add(reloj)

        # estación terrena que gira con la Tierra (periodo GEO)
        w_geo = TAU / T_GEO
        est = Dot(radius=0.07, color=C_ANT)
        est.set_z_index(5)
        est.add_updater(lambda m: m.move_to(C + Re * np.array(
            [np.cos(1.2 + w_geo * reloj.get_value()), np.sin(1.2 + w_geo * reloj.get_value()), 0])))
        globo_rot = globo  # la malla es simétrica: la estación marca el giro

        filas = VGroup()
        satelites = {}
        y_fila = [1.7, 0.0, -1.7]
        for (nombre, rad, col, alt, per, Tmin, ns), y in zip(capas, y_fila):
            T_anim = T_GEO * Tmin / 1436.1
            w = TAU / T_anim
            anillo = Circle(radius=rad, color=col, stroke_width=2.6, stroke_opacity=0.9).move_to(C)
            sats = VGroup()
            for j in range(ns):
                a0 = 0.5 + j * TAU / ns + (0.0 if nombre != "MEO" else 0.7)
                s = satelite(0.15 if nombre != "GEO" else 0.17)
                s.set_z_index(6)
                s.add_updater(lambda m, a0=a0, w=w, rad=rad: m.move_to(
                    C + rad * np.array([np.cos(a0 + w * reloj.get_value()),
                                        np.sin(a0 + w * reloj.get_value()), 0])))
                s.move_to(C + rad * np.array([np.cos(a0), np.sin(a0), 0]))
                sats.add(s)
            satelites[nombre] = sats

            # fila del panel
            icono = Circle(radius=0.22, color=col, stroke_width=3).move_to([3.05, y, 0])
            pto = Dot(icono.get_center() + np.array([0.22, 0, 0]), radius=0.06, color=C_SAT)
            n_t = et(nombre, 32, col, weight=BOLD).next_to(icono, RIGHT, buff=0.3)
            v_alt = et(alt, 28, TINTA)
            v_per = et(per, 28, TENUE)
            v_alt.move_to([5.55, y + 0.22, 0]); v_alt.align_to([4.75, 0, 0], LEFT)
            v_per.move_to([5.55, y - 0.24, 0]); v_per.align_to([4.75, 0, 0], LEFT)
            fila = VGroup(icono, pto, n_t, v_alt, v_per)
            filas.add(fila)

            self.play(Create(anillo), run_time=1.1)
            self.play(FadeIn(sats, suspend_mobject_updating=False),
                      FadeIn(fila, shift=LEFT * 0.3), run_time=0.7)
            self.add(*sats)
            if nombre == "LEO":
                self.play(FadeIn(est), run_time=0.3)
            self.wait(0.5)

        # línea que muestra el satélite geoestacionario fijo sobre la estación
        geo0 = satelites["GEO"][0]
        enlace = always_redraw(lambda: DashedLine(est.get_center(), geo0.get_center(),
                                                  color=C_ANT, stroke_width=2.2,
                                                  dash_length=0.1, stroke_opacity=0.9))
        self.play(FadeIn(enlace), run_time=0.6)
        # deja correr para ver la diferencia de velocidades angulares
        self.wait(9.0)
        self.cierre()


# ----------------------------------------------------------------------------
# 3. Leyes de Kepler
# ----------------------------------------------------------------------------
class LeyesKepler(Pieza):
    def construct(self):
        self.add(estrellas(50, 3))
        a, e = 4.0, 0.55
        b = a * np.sqrt(1 - e * e)
        F = np.array([1.2, 0.0, 0.0])
        # semieje real para las cifras (perigeo 600 km de altitud)
        rp_km = R_TIERRA + 600.0
        a_km = rp_km / (1 - e)

        def pos(M):
            E = kepler_E(M, e)
            return F + np.array([a * (np.cos(E) - e), b * np.sin(E), 0.0])

        def vel_km(M):
            E = kepler_E(M, e)
            r_km = a_km * (1 - e * np.cos(E))
            return np.sqrt(MU_TIERRA * (2 / r_km - 1 / a_km))

        def dir_vel(M):
            E = kepler_E(M, e)
            d = np.array([-a * np.sin(E), b * np.cos(E), 0.0])
            return d / np.linalg.norm(d)

        elipse = ParametricFunction(
            lambda E: F + np.array([a * (np.cos(E) - e), b * np.sin(E), 0.0]),
            t_range=[0, TAU, 0.02], color=C_CIELO, stroke_width=3, stroke_opacity=0.85)
        globo = tierra(0.55).move_to(F)
        globo.set_z_index(4)
        foco2 = Dot(F - np.array([2 * a * e, 0, 0]), radius=0.05, color=C_EJE)

        self.play(FadeIn(globo), run_time=0.7)
        self.play(Create(elipse), run_time=1.6)
        self.play(FadeIn(foco2, scale=0.5), run_time=0.3)

        M0 = -0.9
        Mtrk = ValueTracker(M0)
        sat = satelite(0.24)
        sat.set_z_index(6)
        sat.add_updater(lambda m: m.move_to(pos(Mtrk.get_value())))
        sat.move_to(pos(M0))

        VMAX = vel_km(0.0)

        def flecha_vel():
            M = Mtrk.get_value()
            p = pos(M)
            L = 0.24 * vel_km(M)
            return Arrow(p, p + dir_vel(M) * L, buff=0, color=C_ANT, stroke_width=5,
                         tip_length=0.2, max_tip_length_to_length_ratio=0.35)

        fl = always_redraw(flecha_vel)

        # indicador de velocidad (cifra + barra)
        cx = 5.75
        borde = Rectangle(width=0.5, height=5.0, color=C_EJE, stroke_width=2).move_to([cx, -0.7, 0])
        def barra():
            frac = vel_km(Mtrk.get_value()) / (VMAX * 1.02)
            h = 5.0 * frac
            col = interpolate_color(ManimColor(C_ANT), ManimColor(C_SAT), frac)
            r = Rectangle(width=0.5, height=max(h, 0.02), color=col, fill_color=col,
                          fill_opacity=0.9, stroke_width=0)
            r.move_to([cx, -0.7 - 2.5, 0], aligned_edge=DOWN)
            return r
        barra_m = always_redraw(barra)
        num = cifra(vel_km(M0), "km/s", tam=40, color=C_ANT, decimales=1)
        n_dec = num[0]
        num.move_to([cx, 2.75, 0])
        def act_num(m):
            v = vel_km(Mtrk.get_value())
            n_dec.set_value(v)
            frac = v / (VMAX * 1.02)
            n_dec.set_color(interpolate_color(ManimColor(C_ANT), ManimColor(C_SAT), frac))
            num.arrange(RIGHT, buff=0.12, aligned_edge=DOWN).move_to([cx, 2.75, 0])
        num.add_updater(act_num)

        # cuñas de áreas iguales: mismo intervalo de tiempo (ΔM) en perigeo y apogeo
        dM = 0.9
        def cuna(Ma, Mb, color):
            def f():
                M = Mtrk.get_value()
                hasta = min(M, Mb)
                if hasta <= Ma + 1e-3:
                    return VMobject()
                ms = np.linspace(Ma, hasta, 36)
                pts = [F] + [pos(m) for m in ms]
                return Polygon(*pts, color=color, fill_color=color, fill_opacity=0.38,
                               stroke_width=1.5, stroke_opacity=0.9)
            return always_redraw(f)

        cuna_p = cuna(-dM / 2, dM / 2, C_SAT)
        cuna_a = cuna(PI - dM / 2, PI + dM / 2, C_CIELO)

        self.add(cuna_p, cuna_a, barra_m, fl, sat)
        self.play(FadeIn(borde), FadeIn(num), run_time=0.5)
        T_orb = 15.0
        self.play(Mtrk.animate.set_value(M0 + TAU), run_time=T_orb, rate_func=linear)
        sat.clear_updaters(); num.clear_updaters()
        self.cierre()


# ----------------------------------------------------------------------------
# 4. Transferencia de Hohmann
# ----------------------------------------------------------------------------
class TransferenciaHohmann(Pieza):
    def construct(self):
        self.add(estrellas(55, 8))
        C = np.array([-1.3, 0.0, 0.0])
        r1, r2 = 1.65, 3.35
        a = (r1 + r2) / 2
        e = (r2 - r1) / (r2 + r1)
        b = a * np.sqrt(1 - e * e)
        mu = r1 ** 3 * (2.55 ** 2) / 1.0   # ω1 ≈ 2.55 rad/s
        w1 = np.sqrt(mu / r1 ** 3)
        w2 = np.sqrt(mu / r2 ** 3)
        t_tr = np.pi * np.sqrt(a ** 3 / mu)

        globo = tierra(0.72).move_to(C)
        atm = Circle(radius=0.75, color=C_ANT, stroke_width=5, stroke_opacity=0.25).move_to(C)
        orb1 = Circle(radius=r1, color=C_ANT, stroke_width=3).move_to(C)
        orb2 = DashedVMobject(Circle(radius=r2, color=C_CIELO, stroke_width=3), num_dashes=70).move_to(C)
        orb2.set_stroke(opacity=0.8)

        def pos1(th):
            return C + r1 * np.array([np.cos(th), np.sin(th), 0])

        def pos2(th):
            return C + r2 * np.array([np.cos(th), np.sin(th), 0])

        def pos_tr(al):  # al en [0,1] tiempo uniforme (M/π)
            E = kepler_E(np.pi * al, e)
            loc = np.array([a * (np.cos(E) - e), b * np.sin(E), 0.0])
            # perigeo en ángulo π
            return C + np.array([-loc[0], -loc[1], 0.0])

        sat = satelite(0.24)
        sat.set_z_index(6)
        th0 = 0.45 * np.pi
        sat.move_to(pos1(th0))

        self.play(FadeIn(globo), FadeIn(atm), run_time=0.8)
        self.play(Create(orb1), run_time=1.0)
        self.play(Create(orb2), run_time=1.2)
        self.play(FadeIn(sat, scale=0.5), run_time=0.4)

        # fase 1: vuelta y cuarto en órbita baja
        d1 = 2.6 * np.pi
        self.play(UpdateFromAlphaFunc(
            sat, lambda m, al: m.move_to(pos1(th0 + d1 * al)),
            rate_func=linear, run_time=d1 / w1))

        # panel de cifras
        px = 4.9
        fila1 = VGroup(dv(1, 36), cifra(2.4, "km/s", tam=36, color=C_SAT, decimales=1))
        fila2 = VGroup(dv(2, 36), cifra(1.5, "km/s", tam=36, color=C_SAT, decimales=1))
        for f, y in ((fila1, 1.0), (fila2, -0.4)):
            f.arrange(RIGHT, buff=0.35)
            f.move_to([px + 0.9, y, 0])
        fila1.align_to([4.2, 0, 0], LEFT)
        fila2.align_to([4.2, 0, 0], LEFT)

        def quemada(punto, u, fila, dur=1.0):
            fl = flama(punto, -u * 0)  # se recalcula abajo
            return None

        # --- quemada 1 (en el perigeo, ángulo π; velocidad hacia -y)
        p = pos1(3 * np.pi)
        u1 = np.array([0.0, -1.0, 0.0])
        llama = flama(p, u1)
        f_dv = flecha(p, p + u1 * 0.95, color=C_ANT, ancho=6, punta=0.25)
        f_dv.set_z_index(7)
        self.add(llama)
        self.play(FadeIn(llama, scale=0.6), GrowArrow(f_dv),
                  Flash(p, color=C_SAT, line_length=0.25, flash_radius=0.35, num_lines=10),
                  FadeIn(fila1, shift=LEFT * 0.3), run_time=0.9)
        self.play(FadeOut(llama), FadeOut(f_dv), run_time=0.4)

        # fase 2: elipse de transferencia
        trazo = VMobject(color=C_SAT, stroke_width=4)
        trazo.set_points_as_corners([pos_tr(0), pos_tr(0.01)])
        trazo.set_z_index(2)
        self.add(trazo)

        def viaje(m, al):
            m.move_to(pos_tr(al))
            n = max(2, int(80 * al) + 2)
            trazo.set_points_smoothly([pos_tr(al * k / (n - 1)) for k in range(n)])
        self.play(UpdateFromAlphaFunc(sat, viaje, rate_func=linear, run_time=t_tr))

        # --- quemada 2 (apogeo, ángulo 0; velocidad hacia +y)
        p2 = pos2(0.0)
        u2 = np.array([0.0, 1.0, 0.0])
        llama2 = flama(p2, u2)
        f_dv2 = flecha(p2, p2 + u2 * 0.8, color=C_ANT, ancho=6, punta=0.25)
        f_dv2.set_z_index(7)
        self.add(llama2)
        self.play(FadeIn(llama2, scale=0.6), GrowArrow(f_dv2),
                  Flash(p2, color=C_SAT, line_length=0.25, flash_radius=0.35, num_lines=10),
                  FadeIn(fila2, shift=LEFT * 0.3), run_time=0.9)
        self.play(FadeOut(llama2), FadeOut(f_dv2), run_time=0.4)

        # fase 3: órbita alta (queda circularizada)
        orb2_ok = Circle(radius=r2, color=C_OK, stroke_width=4).move_to(C)
        self.play(orb2.animate.set_stroke(opacity=0.0), FadeIn(orb2_ok), run_time=0.8)
        d3 = w2 * 5.2
        self.play(UpdateFromAlphaFunc(
            sat, lambda m, al: m.move_to(pos2(d3 * al)), rate_func=linear, run_time=5.2))
        self.cierre()


# ----------------------------------------------------------------------------
# 5. Puntos de Lagrange
# ----------------------------------------------------------------------------
def _contornos(Z, xs, ys, nivel):
    """Marching squares con encadenado. Devuelve lista de polilíneas (x,y)."""
    ny, nx = Z.shape
    S = Z > nivel
    aristas = {}

    def interp(id_, i, j):
        kind = id_
        if kind == "h":  # arista horizontal entre (i,j) y (i+1,j)
            z0, z1 = Z[j, i], Z[j, i + 1]
            t = (nivel - z0) / (z1 - z0)
            return (xs[i] + t * (xs[i + 1] - xs[i]), ys[j])
        z0, z1 = Z[j, i], Z[j + 1, i]
        t = (nivel - z0) / (z1 - z0)
        return (xs[i], ys[j] + t * (ys[j + 1] - ys[j]))

    grafo = {}
    posic = {}

    def add(e1, e2):
        grafo.setdefault(e1, []).append(e2)
        grafo.setdefault(e2, []).append(e1)

    for j in range(ny - 1):
        for i in range(nx - 1):
            c = (S[j, i] << 0) | (S[j, i + 1] << 1) | (S[j + 1, i + 1] << 2) | (S[j + 1, i] << 3)
            if c in (0, 15):
                continue
            bot = ("h", i, j)
            top = ("h", i, j + 1)
            lef = ("v", i, j)
            rig = ("v", i + 1, j)
            for e_ in (bot, top, lef, rig):
                if e_ not in posic:
                    posic[e_] = None
            tabla = {1: [(lef, bot)], 14: [(lef, bot)], 2: [(bot, rig)], 13: [(bot, rig)],
                     4: [(rig, top)], 11: [(rig, top)], 8: [(lef, top)], 7: [(lef, top)],
                     3: [(lef, rig)], 12: [(lef, rig)], 6: [(bot, top)], 9: [(bot, top)],
                     5: [(lef, top), (bot, rig)], 10: [(lef, bot), (rig, top)]}
            for (e1, e2) in tabla[c]:
                add(e1, e2)
    for e_ in grafo:
        posic[e_] = interp(e_[0], e_[1], e_[2])
    visitado = set()
    lineas = []
    # abiertas primero
    orden = sorted(grafo, key=lambda k: len(grafo[k]))
    for s in orden:
        if s in visitado:
            continue
        cadena = [s]
        visitado.add(s)
        cur = s
        while True:
            sig = [n for n in grafo[cur] if n not in visitado]
            if not sig:
                break
            cur = sig[0]
            visitado.add(cur)
            cadena.append(cur)
        # si es cerrada (grado 2 en el inicio), cerrar
        if len(cadena) > 2 and cadena[0] in grafo[cadena[-1]]:
            cadena.append(cadena[0])
        lineas.append([posic[k] for k in cadena])
    return lineas


class PuntosLagrange(Pieza):
    def construct(self):
        self.add(estrellas(55, 21))
        MU, D = 0.04, 4.3

        def omega(x, y):
            r1 = np.hypot(x + MU, y)
            r2 = np.hypot(x - 1 + MU, y)
            return (x * x + y * y) / 2 + (1 - MU) / r1 + MU / r2

        def f_col(x):
            return (x - (1 - MU) * (x + MU) / abs(x + MU) ** 3
                    - MU * (x - 1 + MU) / abs(x - 1 + MU) ** 3)

        def raiz(lo, hi):
            flo = f_col(lo)
            for _ in range(80):
                mid = 0.5 * (lo + hi)
                fm = f_col(mid)
                if np.sign(fm) == np.sign(flo):
                    lo, flo = mid, fm
                else:
                    hi = mid
            return 0.5 * (lo + hi)

        xL1 = raiz(-MU + 0.05, 1 - MU - 0.02)
        xL2 = raiz(1 - MU + 0.02, 2.0)
        xL3 = raiz(-2.0, -MU - 0.05)
        L = {
            "L1": (xL1, 0.0), "L2": (xL2, 0.0), "L3": (xL3, 0.0),
            "L4": (0.5 - MU, np.sqrt(3) / 2), "L5": (0.5 - MU, -np.sqrt(3) / 2),
        }
        X0 = -D * (xL3 + xL2) / 2

        def P(x, y):
            return np.array([X0 + D * x, D * y, 0.0])

        # rejilla de potencial en coordenadas de pantalla
        gx = np.linspace(-6.9, 6.9, 330)
        gy = np.linspace(-3.9, 3.9, 190)
        XX, YY = np.meshgrid((gx - X0) / D, gy / D)
        Z = omega(XX, YY)
        Z = np.where(np.isfinite(Z), Z, 1e6)
        niveles = [
            (omega(*L["L4"]) + 0.012, 1.8, 0.55), (omega(*L["L3"]), 2.6, 0.7),
            (omega(*L["L2"]), 2.8, 0.85), (omega(*L["L1"]), 3.4, 1.0),
            (1.9, 1.6, 0.35), (2.3, 1.6, 0.35), (3.0, 1.6, 0.35), (4.2, 1.6, 0.35),
        ]
        curvas = VGroup()
        for nv, ancho, op in niveles:
            for ln in _contornos(Z, gx, gy, nv):
                if len(ln) < 4:
                    continue
                m = polilinea(ln, color=C_CIELO)
                m.set_stroke(color=C_CIELO, width=ancho, opacity=op)
                curvas.add(m)

        pT = P(-MU, 0)
        pL = P(1 - MU, 0)
        tierra_m = tierra(0.52).move_to(pT)
        luna = Circle(radius=0.2, color=TENUE, fill_color=TENUE, fill_opacity=0.9,
                      stroke_width=1.5).move_to(pL)
        luna.set_z_index(4)
        arco = ParametricFunction(
            lambda t: pT + D * np.array([np.cos(t), np.sin(t), 0]),
            t_range=[-1.08, 1.08], color=C_EJE, stroke_width=2.2, stroke_opacity=0.9)
        arco = DashedVMobject(arco, num_dashes=32)

        self.play(FadeIn(tierra_m), FadeIn(luna), run_time=0.8)
        self.play(Create(arco), run_time=1.0)
        self.play(LaggedStart(*[Create(c) for c in curvas], lag_ratio=0.12), run_time=3.0)

        # puntos de Lagrange
        marcas = {}
        for nombre, (x, y) in L.items():
            p = P(x, y)
            d = Dot(p, radius=0.09, color=C_OK)
            d.set_z_index(6)
            t = et(nombre, 26, C_OK, weight=BOLD)
            if nombre in ("L4", "L5"):
                t.next_to(d, RIGHT, buff=0.18)
            else:
                t.next_to(d, UP, buff=0.18)
            marcas[nombre] = VGroup(d, t)
            self.play(FadeIn(d, scale=2.2), FadeIn(t), run_time=0.45)
        self.respiro(0.2)

        # satélite en órbita halo alrededor de L2
        c2 = P(*L["L2"])
        rx, ry = 0.52, 0.95
        halo = ParametricFunction(
            lambda t: c2 + np.array([rx * np.cos(t), ry * np.sin(t), 0]),
            t_range=[0, TAU], color=C_SAT, stroke_width=3, stroke_opacity=0.8)
        sat = satelite(0.2)
        sat.set_z_index(7)
        sat.move_to(halo.point_from_proportion(0))
        self.play(Create(halo), FadeIn(sat), run_time=1.2)
        enlace = always_redraw(lambda: DashedLine(pT + RIGHT * 0.05, sat.get_center(),
                                                  color=C_ANT, stroke_width=1.8,
                                                  dash_length=0.1, stroke_opacity=0.5))

        # nubes troyanas alrededor de L4 y L5 (pequeñas oscilaciones)
        rng = np.random.default_rng(4)
        troy = VGroup()
        info = []
        for nm in ("L4", "L5"):
            c = P(*L[nm])
            for _ in range(7):
                d = Dot(c, radius=0.04, color=TENUE)
                d.set_fill(opacity=0.85)
                info.append((d, c, rng.uniform(0.15, 0.4), rng.uniform(0.15, 0.4),
                             rng.uniform(0, TAU), rng.uniform(0.6, 1.2)))
                troy.add(d)
        tt = ValueTracker(0)

        def mover_troy(m):
            t = tt.get_value()
            for d, c, ax, ay, ph, wv in info:
                d.move_to(c + np.array([ax * np.cos(wv * t + ph), ay * np.sin(wv * t + ph), 0]))
        troy.add_updater(mover_troy)
        mover_troy(troy)
        self.add(troy)
        self.play(FadeIn(troy), run_time=0.5)
        self.add(enlace)
        self.play(
            MoveAlongPath(sat, halo, rate_func=linear, run_time=6.5),
            tt.animate.set_value(6.5 * 1.0), run_time=6.5, rate_func=linear)
        self.cierre()


# ----------------------------------------------------------------------------
# 6. Huella de cobertura
# ----------------------------------------------------------------------------
class HuellaCobertura(Pieza):
    def construct(self):
        self.add(estrellas(50, 14))
        R = 0.95
        Ce = np.array([0.0, -2.9, 0.0])
        globo = tierra(R).move_to(Ce)
        atm = Circle(radius=R * 1.04, color=C_ANT, stroke_width=5, stroke_opacity=0.22).move_to(Ce)

        def y_de(h):
            return Ce[1] + R * (1 + h / R_TIERRA)

        # eje de altitudes a la izquierda
        ax_x = -3.3
        eje = Line([ax_x, Ce[1] + R, 0], [ax_x, y_de(35786) + 0.35, 0], color=C_EJE, stroke_width=3)
        hitos = [("LEO", 550, "550 km", C_ANT), ("MEO", 20200, "20 200 km", C_CIELO),
                 ("GEO", 35786, "35 786 km", C_OK)]
        ticks = VGroup()
        for nombre, h, txt, col in hitos:
            y = y_de(h)
            tk = Line([ax_x - 0.14, y, 0], [ax_x + 0.14, y, 0], color=col, stroke_width=4)
            n = et(nombre, 28, col, weight=BOLD).next_to(tk, LEFT, buff=0.3).shift(UP * 0.18)
            a_ = et(txt, 22, TENUE).next_to(tk, LEFT, buff=0.3).shift(DOWN * 0.2)
            ticks.add(VGroup(tk, n, a_))

        H = ValueTracker(550)

        def alfa():
            return np.arccos(R_TIERRA / (R_TIERRA + H.get_value()))

        def sat_pos():
            return np.array([0.0, y_de(H.get_value()), 0.0])

        sat = satelite(0.3)
        sat.set_z_index(8)
        sat.add_updater(lambda m: m.move_to(sat_pos()))
        sat.move_to(sat_pos())

        def on_sphere(phi, k=1.0):
            return Ce + R * k * np.array([np.sin(phi), np.cos(phi), 0.0])

        def cono():
            al = alfa()
            s = sat_pos()
            fase = np.linspace(-al, al, 60)
            pts = [s] + [on_sphere(p) for p in fase]
            cuerpo = Polygon(*pts, color=C_ANT, fill_color=C_ANT, fill_opacity=0.16, stroke_width=0)
            l1 = Line(s, on_sphere(al), color=C_ANT, stroke_width=2.2)
            l2 = Line(s, on_sphere(-al), color=C_ANT, stroke_width=2.2)
            return VGroup(cuerpo, l1, l2)

        def arco_vivo():
            al = alfa()
            k = float(np.interp(H.get_value(), [550, 20200, 35786], [1.06, 1.14, 1.22]))
            fase = np.linspace(-al, al, 80)
            return polilinea([on_sphere(p, k) for p in fase], color=C_OK).set_stroke(
                color=C_OK, width=7, opacity=1)

        def guia():
            y = y_de(H.get_value())
            return DashedLine([ax_x, y, 0], [-0.3, y, 0], color=C_EJE, stroke_width=1.6,
                              dash_length=0.1, stroke_opacity=0.8)

        cono_m = always_redraw(cono)
        arco_m = always_redraw(arco_vivo)
        guia_m = always_redraw(guia)

        pct_fn = lambda: 100 * (1 - np.cos(alfa())) / 2
        pct = cifra(pct_fn(), "%", tam=76, color=C_OK, decimales=0)
        n_dec = pct[0]
        pct.move_to([4.9, 0.2, 0])

        def act_pct(m):
            n_dec.set_value(pct_fn())
            m.arrange(RIGHT, buff=0.15, aligned_edge=DOWN).move_to([4.9, 0.2, 0])
        pct.add_updater(act_pct)

        # medidor visual: barra hasta 50 % (hemisferio máximo teórico)
        marco = Rectangle(width=2.4, height=0.28, color=C_EJE, stroke_width=2).move_to([4.9, -1.0, 0])
        def relleno():
            fr = pct_fn() / 50.0
            r = Rectangle(width=max(2.4 * fr, 0.02), height=0.28, color=C_OK, fill_color=C_OK,
                          fill_opacity=0.85, stroke_width=0)
            r.move_to(marco.get_left(), aligned_edge=LEFT)
            return r
        rell = always_redraw(relleno)

        self.play(FadeIn(globo), FadeIn(atm), FadeIn(eje), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.2) for t in ticks], lag_ratio=0.3), run_time=1.3)
        self.add(guia_m, cono_m, arco_m)
        self.play(FadeIn(sat, scale=0.5), FadeIn(pct), FadeIn(marco), run_time=0.7)
        self.add(rell)
        self.wait(1.6)

        fantasmas = VGroup()
        for destino in (20200, 35786):
            # deja rastro del arco alcanzado
            ghost = arco_vivo().set_stroke(opacity=0.5)
            fantasmas.add(ghost)
            self.add(ghost)
            self.play(H.animate.set_value(destino), run_time=3.4, rate_func=smooth)
            self.wait(1.4)
        ghost = arco_vivo().set_stroke(opacity=1)
        self.wait(0.3)
        pct.clear_updaters()
        self.cierre()


# ----------------------------------------------------------------------------
# 7. Traza terrestre
# ----------------------------------------------------------------------------
CONTINENTES = {
    "NA": [(-168, 66), (-156, 71), (-128, 70), (-95, 72), (-80, 70), (-62, 60), (-56, 52), (-66, 45),
           (-70, 42), (-76, 35), (-81, 31), (-80, 25), (-83, 29), (-90, 30), (-97, 26), (-97, 21),
           (-88, 21), (-88, 16), (-83, 10), (-77, 8), (-86, 12), (-92, 15), (-105, 20), (-110, 24),
           (-115, 30), (-118, 34), (-124, 40), (-124, 48), (-135, 58), (-148, 60), (-158, 57),
           (-165, 60)],
    "SA": [(-77, 8), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-35, -6), (-39, -15), (-48, -26),
           (-58, -38), (-65, -42), (-68, -52), (-73, -52), (-75, -45), (-72, -30), (-70, -18),
           (-76, -14), (-81, -5), (-80, 0)],
    "AF": [(-17, 21), (-10, 30), (-6, 36), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12),
           (51, 12), (40, -3), (40, -15), (35, -24), (28, -33), (18, -34), (12, -18), (9, -1),
           (9, 4), (-8, 4), (-17, 14)],
    "EU": [(-9, 37), (-9, 43), (-1, 46), (-4, 48), (2, 51), (8, 54), (10, 58), (5, 61), (15, 68),
           (25, 71), (40, 68), (60, 70), (80, 73), (105, 77), (130, 72), (160, 70), (180, 68),
           (180, 65), (170, 60), (160, 55), (156, 51), (142, 46), (135, 43), (130, 35), (126, 38),
           (122, 30), (120, 24), (110, 20), (108, 12), (105, 9), (100, 13), (98, 8), (100, 2),
           (98, 16), (92, 22), (88, 22), (80, 15), (77, 8), (73, 16), (70, 22), (62, 25),
           (57, 25), (56, 27), (50, 30), (48, 29), (52, 24), (56, 24), (59, 22), (52, 16),
           (43, 13), (39, 21), (35, 28), (32, 31), (35, 36), (28, 36), (26, 40), (23, 38),
           (20, 40), (13, 45), (18, 40), (16, 38), (12, 42), (8, 44), (3, 43), (-1, 37)],
    "AU": [(114, -22), (122, -18), (130, -12), (137, -12), (142, -11), (146, -19), (153, -27),
           (150, -37), (141, -38), (135, -34), (129, -32), (115, -34)],
    "GR": [(-73, 78), (-55, 82), (-25, 83), (-20, 72), (-40, 65), (-50, 68), (-58, 75)],
    "UK": [(-5, 50), (1, 51), (-2, 55), (-3, 58), (-6, 56), (-3, 53)],
    "JP": [(130, 32), (135, 34), (140, 36), (142, 43), (140, 40), (136, 36), (131, 34)],
    "MG": [(44, -25), (47, -25), (50, -15), (49, -12), (44, -17)],
    "ID": [(95, 5), (105, -6), (102, -4), (98, 0)],
    "BO": [(109, 1), (118, 6), (119, 0), (116, -4), (110, -3)],
    "NZ": [(172, -41), (176, -38), (178, -39), (174, -46), (167, -46)],
    "AN": [(-180, -72), (-140, -75), (-100, -73), (-60, -72), (-20, -70), (30, -68), (80, -66),
           (130, -66), (180, -70), (180, -90), (-180, -90)],
}


class TrazaTerrestre(Pieza):
    def construct(self):
        AN, AL = 6.2, 3.1   # media anchura, media altura del mapa

        def M(lon, lat):
            return np.array([lon / 180 * AN, lat / 90 * AL, 0.0])

        # rejilla
        rejilla = VGroup()
        for lon in range(-180, 181, 30):
            rejilla.add(Line(M(lon, -90), M(lon, 90), color=C_EJE, stroke_width=1.2, stroke_opacity=0.7))
        for lat in range(-90, 91, 30):
            rejilla.add(Line(M(-180, lat), M(180, lat), color=C_EJE, stroke_width=1.2, stroke_opacity=0.7))
        ecuador = Line(M(-180, 0), M(180, 0), color=TENUE, stroke_width=2, stroke_opacity=0.8)
        marco = Rectangle(width=2 * AN, height=2 * AL, color=C_EJE, stroke_width=2.5)
        cont = VGroup()
        for nombre, pts in CONTINENTES.items():
            pl = Polygon(*[M(x, y) for x, y in pts], color=TENUE, fill_color=C_EJE,
                         fill_opacity=0.55, stroke_width=1.2)
            pl.set_stroke(opacity=0.75)
            cont.add(pl)

        self.play(Create(marco), Create(rejilla), run_time=1.2)
        self.play(FadeIn(cont), Create(ecuador), run_time=1.0)

        # órbita tipo ISS
        inc = np.radians(51.6)
        T = 92.7                          # min
        wE = 360.0 / 1436.07              # °/min
        lon0 = -40.0
        n_orb = 3
        N = 420
        us = np.linspace(0, TAU * n_orb, N * n_orb + 1)
        lons, lats = [], []
        for u in us:
            t = T * u / TAU
            lat = np.degrees(np.arcsin(np.sin(inc) * np.sin(u)))
            lo = np.degrees(np.arctan2(np.cos(inc) * np.sin(u), np.cos(u))) + lon0 - wE * t
            lo = (lo + 180) % 360 - 180
            lons.append(lo); lats.append(lat)
        lons = np.array(lons); lats = np.array(lats)
        pts = np.array([M(x, y) for x, y in zip(lons, lats)])

        def trazo_hasta(i0, i1, op):
            """Polilínea(s) entre índices i0..i1 rompiendo en el borde del mapa."""
            m = VMobject()
            m.set_stroke(color=C_SAT, width=4, opacity=op)
            ini = True
            seg = [i0]
            trozos = []
            for i in range(i0 + 1, i1 + 1):
                if abs(lons[i] - lons[i - 1]) > 180:
                    trozos.append(seg); seg = [i]
                else:
                    seg.append(i)
            trozos.append(seg)
            for tr in trozos:
                if len(tr) < 2:
                    continue
                if ini:
                    m.set_points_as_corners(pts[tr])
                    ini = False
                else:
                    m.start_new_path(pts[tr[0]])
                    m.add_points_as_corners(pts[tr[1:]])
            return m

        s = ValueTracker(0.0)   # índice fraccional
        sat = satelite(0.2)
        sat.set_z_index(9)
        halo = Circle(radius=0.2, color=C_SAT, stroke_width=2, stroke_opacity=0.5)
        halo.set_z_index(8)

        def traza():
            i = int(s.get_value())
            g = VGroup()
            for k in range(n_orb):
                a, b = k * N, min((k + 1) * N, i)
                if b - a >= 2:
                    ops = 1.0 if (k == i // N or b == i) else 0.5
                    if k < (i - 1) // N:
                        ops = 0.5
                    g.add(trazo_hasta(a, b, ops))
            return g

        traza_m = always_redraw(traza)
        sat.add_updater(lambda m: m.move_to(pts[min(int(s.get_value()), len(pts) - 1)]))
        halo.add_updater(lambda m: m.move_to(pts[min(int(s.get_value()), len(pts) - 1)]))
        sat.move_to(pts[0]); halo.move_to(pts[0])
        self.add(traza_m, halo, sat)

        # marcas de nodo ascendente
        def nodo_marca(k):
            p = pts[k * N]
            d = Dot(p, radius=0.09, color=C_OK)
            d.set_z_index(8)
            return d

        self.play(FadeIn(sat), FadeIn(halo), run_time=0.4)
        n0 = nodo_marca(0)
        self.add(n0)
        dur_orb = 5.6
        # órbita 1
        self.play(s.animate.set_value(N), run_time=dur_orb, rate_func=linear)
        n1 = nodo_marca(1)
        self.play(FadeIn(n1, scale=2), run_time=0.3)
        # etiqueta de desplazamiento bajo el mapa
        x0, x1 = pts[0][0], pts[N][0]
        yb = -AL - 0.24
        lin_a = DashedLine([x0, 0, 0], [x0, yb, 0], color=C_OK, stroke_width=2, dash_length=0.08)
        lin_b = DashedLine([x1, 0, 0], [x1, yb, 0], color=C_OK, stroke_width=2, dash_length=0.08)
        puente = DoubleArrow([x1, yb, 0], [x0, yb, 0], buff=0, color=C_OK, stroke_width=3,
                             tip_length=0.12)
        num = cifra(23, "°", tam=34, color=C_OK)
        num.next_to(puente, DOWN, buff=0.0)
        self.play(Create(lin_a), Create(lin_b), Create(puente), FadeIn(num), run_time=0.9)
        # órbita 2 y 3
        self.play(s.animate.set_value(2 * N), run_time=dur_orb, rate_func=linear)
        n2 = nodo_marca(2)
        self.play(FadeIn(n2, scale=2), run_time=0.3)
        self.play(s.animate.set_value(3 * N), run_time=dur_orb, rate_func=linear)
        sat.clear_updaters(); halo.clear_updaters()
        self.cierre()


# ----------------------------------------------------------------------------
# 8. Basura espacial (síndrome de Kessler)
# ----------------------------------------------------------------------------
class BasuraEspacial(Pieza):
    def construct(self):
        rng = np.random.default_rng(7)
        W0 = 0.8
        om = lambda r: W0 * (r / 2.4) ** -1.5
        self.add(estrellas(55, 2))
        C0 = np.array([-0.9, -0.1, 0.0])
        globo = tierra(1.6).move_to(C0)
        atm = Circle(radius=1.66, color=C_ANT, stroke_width=6, stroke_opacity=0.22).move_to(C0)

        # ---- escenario de eventos (todo determinista)
        FRAG = 26
        parts = []      # cada partícula: dict(r_f, dir, th_e, r_e, te, kill)
        eventos = []    # dict(t, th, r, gen)
        objetivos = []  # satélites amarillos: (r, th0, kill_t)

        def nuevo_evento(t, th, r, gen):
            ev = dict(t=t, th=th, r=r, gen=gen, idx=[])
            eventos.append(ev)
            first = len(parts)
            for k in range(FRAG):
                rf = float(np.clip(r + rng.normal(0, 0.32), 2.0, 3.15))
                dr = int(rng.choice([-1, 1]))
                parts.append(dict(rf=rf, dir=dr, th_e=th, r_e=r, te=t, kill=1e9))
                ev["idx"].append(first + k)
            return ev

        tc, thc = 2.6, 0.62
        # objeto A (satélite) y B (fragmento viejo) en rumbo de colisión frontal
        A = dict(r=2.4, th0=thc - om(2.4) * tc, dir=+1)
        B = dict(r=2.4, th0=thc + om(2.4) * tc, dir=-1)
        ev0 = nuevo_evento(tc, thc, 2.4, 1)

        def ramificar(ev, gen_max=4):
            if ev["gen"] >= gen_max:
                return
            for h in range(2):
                pid = ev["idx"][h]
                rh = 2.15 + 0.55 * h + rng.uniform(0, 0.25)
                p = parts[pid]
                p["rf"], p["dir"] = rh, -1
                dt_h = rng.uniform(1.15, 1.7)
                t_h = ev["t"] + dt_h
                phi = ev["th"] - om(rh) * dt_h
                th0 = phi - om(rh) * t_h
                # el objetivo (prograde) y el proyectil se destruyen al chocar
                p["kill"] = t_h
                objetivos.append(dict(r=rh, th0=th0, kill=t_h))
                nuevo = nuevo_evento(t_h, phi, rh, ev["gen"] + 1)
                ramificar(nuevo, gen_max)

        ramificar(ev0)

        # ---- fondo de escombros
        NB = 210
        bg_r = rng.uniform(2.05, 3.1, NB)
        bg_th = rng.uniform(0, TAU, NB)
        bg_dir = rng.choice([-1, 1], NB, p=[0.3, 0.7])
        fondo = VGroup(*[Dot(radius=0.028, color=TENUE).set_fill(opacity=0.65) for _ in range(NB)])

        sat_ob = VGroup(*[satelite(0.15) for _ in objetivos])
        for s in sat_ob:
            s.set_z_index(6)
        a_m = satelite(0.19); a_m.set_z_index(7)
        b_m = Dot(radius=0.075, color=TINTA); b_m.set_z_index(7)
        frag_m = VGroup(*[Dot(radius=0.032, color=C_MAL) for _ in parts])
        for d in frag_m:
            d.set_fill(opacity=0.0)
            d.set_z_index(5)

        anillos = VGroup(*[Circle(radius=0.1, color=TINTA, stroke_width=3) for _ in eventos])
        for r_ in anillos:
            r_.set_stroke(opacity=0.0)
            r_.set_z_index(8)

        def pol(r, th):
            return C0 + r * np.array([np.cos(th), np.sin(th), 0.0])

        base = 34000
        inc = 2600
        reloj = ValueTracker(0.0)
        cache_op = [None] * len(parts)

        def actualizar(_m=None):
            t = reloj.get_value()
            for d, r, th0, di in zip(fondo, bg_r, bg_th, bg_dir):
                d.move_to(pol(r, th0 + di * om(r) * t))
            a_m.move_to(pol(A["r"], A["th0"] + om(A["r"]) * t))
            b_m.move_to(pol(B["r"], B["th0"] - om(B["r"]) * t))
            if t >= tc:
                a_m.set_opacity(0); b_m.set_opacity(0)
            for s, ob in zip(sat_ob, objetivos):
                s.move_to(pol(ob["r"], ob["th0"] + om(ob["r"]) * t))
                if t >= ob["kill"]:
                    s.set_opacity(0)
            for i, (d, p) in enumerate(zip(frag_m, parts)):
                vivo = p["te"] <= t < p["kill"]
                if vivo:
                    dtt = t - p["te"]
                    r = p["rf"] + (p["r_e"] - p["rf"]) * np.exp(-4.0 * dtt)
                    d.move_to(pol(r, p["th_e"] + p["dir"] * om(p["rf"]) * dtt))
                if cache_op[i] != vivo:
                    d.set_fill(opacity=1.0 if vivo else 0.0)
                    cache_op[i] = vivo
            for an, ev in zip(anillos, eventos):
                dtt = t - ev["t"]
                if 0 <= dtt < 0.75:
                    an.move_to(pol(ev["r"], ev["th"]))
                    an.set_width(2 * (0.12 + 0.95 * dtt ** 0.6))
                    an.set_stroke(opacity=max(0.0, 1 - dtt / 0.75))
                else:
                    an.set_stroke(opacity=0.0)

        def valor():
            t = reloj.get_value()
            n = base
            for ev in eventos:
                n += inc * suave((t - ev["t"]) / 0.6)
            return int(round(n / 10.0) * 10)

        def texto_cont():
            n = valor()
            frac = (n - base) / (inc * len(eventos))
            col = interpolate_color(ManimColor(TINTA), ManimColor(C_MAL), min(1, frac * 1.4))
            t = Text(f"{n:,}".replace(",", " "), font=FUENTE, font_size=54, color=col)
            t.move_to([5.05, 0.6, 0], aligned_edge=RIGHT) if False else None
            t.move_to([5.35, 0.7, 0])
            return t

        contador = always_redraw(texto_cont)
        unidad = et("objetos", 26, TENUE).move_to([5.35, 0.0, 0])

        motor = Mobject()
        motor.add_updater(lambda m: actualizar())
        actualizar()
        self.add(motor)
        self.add(fondo, sat_ob, a_m, b_m, frag_m, anillos)
        self.play(FadeIn(globo), FadeIn(atm), FadeIn(fondo), FadeIn(sat_ob), FadeIn(a_m), FadeIn(b_m),
                  run_time=1.2)
        self.play(FadeIn(contador), FadeIn(unidad), run_time=0.6)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)
        t_fin = max(ev["t"] for ev in eventos) + 3.4
        self.wait(t_fin)
        reloj.clear_updaters()
        self.cierre()


# ----------------------------------------------------------------------------
# 9. Tierra 3D con satélites
# ----------------------------------------------------------------------------
class Tierra3DSatelites(Pieza3D):
    def construct(self):
        self.set_camera_orientation(phi=66 * DEGREES, theta=-55 * DEGREES, zoom=1.25)
        estr = estrellas(80, 31)
        self.add_fixed_in_frame_mobjects(estr)
        self.add(estr)

        globo = esfera_tierra(1.5)
        planos = [
            # radio, incl, raan, color, nº sats, fase
            (3.35, 0.0, 0.0, C_CIELO, 3, 0.4),
            (2.65, np.radians(55), np.radians(25), C_ANT, 4, 1.0),
            (3.0, np.radians(98), np.radians(110), C_OK, 3, 2.2),
        ]

        def orbita_seg(radio, incl, raan, color, n=28):
            g = VGroup()
            for k in range(n):
                a, b = TAU * k / n, TAU * (k + 1) / n
                g.add(ParametricFunction(
                    lambda t, r=radio: punto_orbita3d(r, t, incl, raan),
                    t_range=[a, b + 0.02], color=color, stroke_width=3, stroke_opacity=0.85))
            return g

        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        globo.add_updater(lambda m, dt: m.rotate(0.28 * dt, axis=OUT, about_point=ORIGIN))

        self.play(FadeIn(globo), run_time=1.0)
        self.add(reloj)
        self.begin_ambient_camera_rotation(rate=0.09)

        todos_sats = []
        for radio, incl, raan, col, ns, fase in planos:
            orb = orbita_seg(radio, incl, raan, col)
            self.play(Create(orb, lag_ratio=1.0), run_time=1.6, rate_func=linear)
            w = 0.95 * (2.65 / radio) ** 1.5
            sats = []
            for j in range(ns):
                a0 = fase + j * TAU / ns
                s = Dot3D(radius=0.085, color=C_SAT)
                s.move_to(punto_orbita3d(radio, a0, incl, raan))
                s.add_updater(lambda m, a0=a0, w=w, radio=radio, incl=incl, raan=raan: m.move_to(
                    punto_orbita3d(radio, a0 + w * reloj.get_value(), incl, raan)))
                sats.append(s)
            self.play(*[FadeIn(s, scale=0.3, suspend_mobject_updating=False) for s in sats], run_time=0.6)
            self.add(*sats)
            todos_sats += sats
        self.wait(8.5)
        self.stop_ambient_camera_rotation()
        globo.clear_updaters()
        for s in todos_sats:
            s.clear_updaters()
        self.cierre()

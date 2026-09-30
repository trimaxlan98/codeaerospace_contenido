"""Antenas, robots y radio definida por software - 10 piezas Co.De Aerospace."""
from code_lib import *
import numpy as np
from scipy.optimize import linear_sum_assignment


# ---------------------------------------------------------------- helpers
def suave(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def polilinea(pts, color, ancho=3, op=1.0, relleno=0.0, cerrar=False):
    pts = np.array(pts, dtype=float)
    if pts.shape[1] == 2:
        pts = np.hstack([pts, np.zeros((len(pts), 1))])
    if cerrar:
        pts = np.vstack([pts, pts[:1]])
    m = VMobject()
    m.set_points_as_corners(pts)
    m.set_stroke(color, ancho, opacity=op)
    m.set_fill(color, opacity=relleno)
    return m


def cifra_signo(valor, unidad="°", tam=28, color=None):
    n = DecimalNumber(valor, num_decimal_places=0, include_sign=False, font_size=tam,
                      color=color or C_ANT)
    n.set_stroke(width=0)
    g = VGroup(n)
    if unidad:
        g.add(Text(unidad, font=FUENTE, font_size=tam * 0.8, color=color or TENUE))
        g.arrange(RIGHT, buff=0.04, aligned_edge=UP)
    return g


def plato_pts(f, H, n=60):
    ys = np.linspace(-H, H, n)
    return np.stack([ys ** 2 / (4 * f), ys, np.zeros(n)], axis=1)


def arco_recortado(centro, R, a0, a1, caja, color, ancho=2.0, op=1.0, n=90):
    """Arco circular recortado a una caja (x0,x1,y0,y1); un VMobject con subtrayectos."""
    x0, x1, y0, y1 = caja
    a = np.linspace(a0, a1, n)
    p = np.stack([centro[0] + R * np.cos(a), centro[1] + R * np.sin(a)], axis=1)
    dentro = (p[:, 0] > x0) & (p[:, 0] < x1) & (p[:, 1] > y0) & (p[:, 1] < y1)
    m = VMobject()
    m.set_stroke(color, ancho, opacity=op)
    m.set_fill(opacity=0)
    i = 0
    hay = False
    while i < n:
        if dentro[i]:
            j = i
            while j + 1 < n and dentro[j + 1]:
                j += 1
            if j > i:
                q = np.hstack([p[i:j + 1], np.zeros((j - i + 1, 1))])
                m.start_new_path(q[0])
                m.add_points_as_corners(q[1:])
                hay = True
            i = j + 1
        else:
            i += 1
    if not hay:
        m.set_points(np.array([[9, 9, 0]] * 4, dtype=float))
        m.set_stroke(opacity=0)
    return m


# ------------------------------------------------------ 1. PatronRadiacion
class PatronRadiacion(Pieza):
    def construct(self):
        R = 3.0
        th = np.linspace(0, TAU, 721)

        def dip(a):
            return np.abs(np.cos(a))

        def dirf(a):
            return np.abs(np.sinc(3 * np.sin(a))) * np.where(np.cos(a) >= 0, 1.0, 0.15)

        # semiancho de haz a -3 dB
        aa = np.linspace(0, 0.5, 5001)
        hp = aa[np.argmax(dirf(aa) < 0.70710678)]
        bw = int(round(np.degrees(2 * hp)))

        # rejilla polar
        rej = VGroup()
        for k in (0.25, 0.5, 0.75, 1.0):
            rej.add(Circle(radius=R * k, color=C_EJE, stroke_width=1.5 if k < 1 else 2.5,
                           stroke_opacity=0.7))
        for d in range(0, 180, 30):
            a = d * DEGREES
            rej.add(Line(-R * 1.03 * np.array([np.cos(a), np.sin(a), 0]),
                         R * 1.03 * np.array([np.cos(a), np.sin(a), 0]),
                         color=C_EJE, stroke_width=1, stroke_opacity=0.6))

        m = ValueTracker(0)      # 0 dipolo -> 1 directiva
        f = ValueTracker(0)      # fracción dibujada
        q = ValueTracker(0)      # relleno
        t0 = ValueTracker(0)     # rotación
        ov = ValueTracker(0)     # marcas -3 dB

        def patron():
            mm = m.get_value()
            r = (1 - mm) * dip(th - t0.get_value()) + mm * dirf(th - t0.get_value())
            pts = R * np.stack([r * np.cos(th), r * np.sin(th)], axis=1)
            n = max(3, int(f.get_value() * len(th)))
            return polilinea(pts[:n], C_ANT, 4, relleno=q.get_value())

        pat = always_redraw(patron)

        def icono():
            a = t0.get_value()
            mm = m.get_value()
            g = VGroup()
            if mm < 0.5:
                g.add(Line(DOWN * 0.42, UP * 0.42, color=C_SAT, stroke_width=6),
                      Dot(ORIGIN, radius=0.06, color=TINTA))
                g.set_opacity(1 - 2 * mm)
            else:
                pl = polilinea(plato_pts(0.3, 0.42, 30) + np.array([-0.2, 0, 0]), C_SAT, 6)
                pl.rotate(a, about_point=ORIGIN)
                g.add(pl, Dot(ORIGIN, radius=0.05, color=C_SAT))
                g.set_opacity(2 * mm - 1)
            return g

        ic = always_redraw(icono)

        def marcas():
            a = t0.get_value()
            o = ov.get_value()
            g = VGroup()
            g.add(Circle(radius=R * 0.7071, color=C_CIELO, stroke_width=2.5,
                         stroke_opacity=0.9 * o).set_fill(opacity=0))
            for s in (-1, 1):
                d = a + s * hp
                g.add(Line(ORIGIN, R * 1.12 * np.array([np.cos(d), np.sin(d), 0]),
                           color=C_SAT, stroke_width=3, stroke_opacity=o))
            g.add(Arc(radius=R * 1.12, start_angle=a - hp, angle=2 * hp, color=C_SAT,
                      stroke_width=5, stroke_opacity=o))
            return g

        mk = always_redraw(marcas)
        lb_bw = cifra_signo(bw, "°", 32, C_SAT)
        lb_bw.add_updater(lambda g: g.move_to((R + 0.55) * np.array(
            [np.cos(t0.get_value()), np.sin(t0.get_value()), 0])).set_opacity(ov.get_value()))
        lb_bw[0].set_opacity(0)
        lb_bw[1].set_opacity(0)
        lb3 = et("−3 dB", 24, C_CIELO).move_to(R * 0.7071 * np.array([np.cos(2.2), np.sin(2.2), 0])
                                              + np.array([-0.75, 0.45, 0])).set_opacity(0)

        self.play(FadeIn(rej, run_time=1.0), FadeIn(ic))
        self.add(pat)
        self.play(f.animate.set_value(1), run_time=2.2, rate_func=smooth)
        self.play(q.animate.set_value(0.25), run_time=0.6)
        eti = et("Dipolo", 26, C_ANT).move_to(LEFT * 5.2 + UP * 2.5)
        self.play(FadeIn(eti))
        self.wait(1.0)
        eti2 = et("Directiva", 26, C_ANT).move_to(eti)
        self.play(m.animate.set_value(1), Transform(eti, eti2), run_time=2.5,
                  rate_func=smooth)
        self.wait(0.4)
        self.add(mk, lb_bw)
        self.play(ov.animate.set_value(1), lb3.animate.set_opacity(1), run_time=1.2)
        lb_bw.set_opacity(1)
        lb_bw.add_updater(lambda g: g.set_opacity(ov.get_value()))
        self.wait(0.8)
        self.play(t0.animate.set_value(55 * DEGREES), run_time=2.4, rate_func=smooth)
        self.play(t0.animate.set_value(-40 * DEGREES), run_time=3.0, rate_func=smooth)
        self.play(t0.animate.set_value(0), run_time=2.0, rate_func=smooth)
        self.cierre()


# -------------------------------------------------------- 2. ParabolaFoco
class ParabolaFoco(Pieza):
    def construct(self):
        f, H = 1.7, 2.3
        V = np.array([-4.2, 0.0, 0.0])
        P = V + LEFT * 0.45
        pts = plato_pts(f, H) + V
        foco = V + RIGHT * f

        # pedestal
        base = Polygon(P + DOWN * 3.35 + LEFT * 0.8, P + DOWN * 3.35 + RIGHT * 0.8,
                       P + DOWN * 2.85 + RIGHT * 0.45, P + DOWN * 2.85 + LEFT * 0.45,
                       color=C_EJE, fill_color=C_EJE, fill_opacity=0.5, stroke_width=2)
        tallo = Line(P, P + DOWN * 2.85, color=C_EJE, stroke_width=8)
        piv = Dot(P, radius=0.11, color=C_EJE)

        plato = polilinea(pts, C_ANT, 7)
        mastil = Line(V, foco, color=C_ANT, stroke_width=2.5)
        cuello = Line(V, P, color=C_ANT, stroke_width=4)
        feed = Dot(foco, radius=0.13, color=C_SAT)
        dish = VGroup(cuello, mastil, plato, feed)

        ys = np.array([-1.8, -1.2, -0.6, 0.6, 1.2, 1.8])
        xs = ys ** 2 / (4 * f) + V[0]
        XS = 5.6
        inc = VGroup(*[Line([XS, y, 0], [x, y, 0], color=C_CIELO, stroke_width=2.5)
                       for x, y in zip(xs, ys)])
        ref = VGroup(*[Line([x, y, 0], foco, color=C_ANT, stroke_width=2.5)
                       for x, y in zip(xs, ys)])
        LT = 9.5
        sal = VGroup(*[Line([x, y, 0], [x + LT, y, 0], color=C_ANT, stroke_width=2.5)
                       for x, y in zip(xs, ys)])

        def viaje(listas, color, run=1.6):
            anims = []
            dots = VGroup()
            for l in listas:
                d = Dot(l[0], radius=0.085, color=color)
                dots.add(d)
                anims.append(MoveAlongPath(d, polilinea(l, color, 0), rate_func=linear))
            return dots, AnimationGroup(*anims, run_time=run)

        self.play(FadeIn(base), Create(tallo), FadeIn(piv), run_time=0.8)
        self.play(Create(plato), Create(cuello), Create(mastil), FadeIn(feed, scale=0.3),
                  run_time=1.8)
        lb_foco = et("Foco", 22, C_SAT).next_to(feed, UP, buff=0.35)
        rx = et("RX", 30, C_CIELO).move_to(UP * 3.3 + RIGHT * 4.6)
        self.play(FadeIn(lb_foco), FadeIn(rx), LaggedStart(*[Create(l) for l in inc],
                                                           lag_ratio=0.12, run_time=1.6))
        for _ in range(2):
            dots, an = viaje([[[XS, y, 0], [x, y, 0], foco] for x, y in zip(xs, ys)],
                             C_SAT, 2.6)
            self.add(dots)
            self.play(an)
            self.play(Flash(feed, color=C_SAT, line_length=0.18, flash_radius=0.3,
                            run_time=0.5), FadeOut(dots, run_time=0.3))
        self.play(Create(ref, lag_ratio=0.0, run_time=0.7))
        self.wait(0.4)
        self.play(FadeOut(inc), FadeOut(ref), FadeOut(rx), run_time=0.6)
        tx = et("TX", 30, C_ANT).move_to(UP * 3.3 + RIGHT * 4.6)
        self.play(FadeIn(tx), Create(ref, lag_ratio=0.0, run_time=0.5))
        dots, an = viaje([[foco, [x, y, 0], [x + LT, y, 0]] for x, y in zip(xs, ys)],
                         C_SAT, 3.4)
        self.add(dots)
        self.play(an, FadeIn(sal, run_time=2.4))
        self.play(FadeOut(dots, run_time=0.3), FadeOut(ref, run_time=0.5))
        # inclinación del plato: el haz sigue
        todo = VGroup(dish, sal)
        self.play(Rotate(todo, 11 * DEGREES, about_point=P), FadeOut(lb_foco),
                  run_time=2.0, rate_func=smooth)
        self.play(Rotate(todo, -22 * DEGREES, about_point=P), run_time=3.0, rate_func=smooth)
        self.play(Rotate(todo, 11 * DEGREES, about_point=P), run_time=1.8, rate_func=smooth)
        self.cierre()


# --------------------------------------------------------- 3. ArregloFases
class ArregloFases(Pieza):
    def construct(self):
        N, d, xe = 8, 0.55, -5.6
        ys = (np.arange(N) - (N - 1) / 2) * d
        c, T = 2.0, 1.0
        caja = (-6.9, 6.9, -3.75, 3.75)
        RM = 13.0
        t = ValueTracker(0)
        DUR = 22.0

        def theta(tt):
            k = [0, 5, 8.5, 12.5, 16.5, 20, 22]
            v = [0, 0, 32, 32, -24, 0, 0]
            out = 0.0
            for i in range(len(k) - 1):
                if k[i] <= tt <= k[i + 1]:
                    out = v[i] + (v[i + 1] - v[i]) * suave((tt - k[i]) / (k[i + 1] - k[i]))
            return np.radians(out)

        def retardos(tt):
            return (ys - ys[0]) * np.sin(theta(tt)) / c

        def ondas():
            tt = t.get_value()
            tk = retardos(tt)
            g = VGroup()
            for k in range(N):
                nmax = int(np.floor((tt - tk[k]) / T))
                for n in range(max(0, nmax - 7), nmax + 1):
                    R = c * (tt - tk[k] - n * T)
                    if 0.05 < R < RM:
                        g.add(arco_recortado([xe, ys[k]], R, -PI / 2, PI / 2, caja, C_ANT,
                                             1.8, 0.5 * (1 - R / RM) ** 1.3, 70))
            return g

        def frentes():
            tt = t.get_value()
            th_ = theta(tt)
            u = np.array([np.cos(th_), np.sin(th_)])
            tk = retardos(tt)
            g = VGroup()
            nmax = int(np.floor((tt - tk[0]) / T))
            for n in range(max(0, nmax - 6), nmax + 1):
                R0 = c * (tt - tk[0] - n * T)
                R7 = c * (tt - tk[-1] - n * T)
                if R0 > 0.15 and R7 > 0.15:
                    a = np.array([xe, ys[0]]) + R0 * u
                    b = np.array([xe, ys[-1]]) + R7 * u
                    ss = np.linspace(0, 1, 30)[:, None]
                    q = a + (b - a) * ss
                    ok = (np.abs(q[:, 0]) < 6.7) & (np.abs(q[:, 1]) < 3.65)
                    if ok.sum() > 2:
                        g.add(polilinea(q[ok], C_SAT, 5, op=max(0.2, 1 - R0 / 13)))
            return g

        def elementos():
            tt = t.get_value()
            tk = retardos(tt)
            g = VGroup()
            for k in range(N):
                g.add(Line([xe - 0.15 - 1.1 * tk[k], ys[k], 0], [xe - 0.15, ys[k], 0],
                           color=C_ANT, stroke_width=4, stroke_opacity=0.9))
                g.add(Dot([xe, ys[k], 0], radius=0.12, color=C_ANT))
            return g

        def flecha_haz():
            th_ = theta(t.get_value())
            o = suave((t.get_value() - 4.2) / 1.2)
            a = np.array([xe + 0.4, 0, 0])
            u = np.array([np.cos(th_), np.sin(th_), 0])
            fl = Arrow(a, a + 4.2 * u, buff=0, color=C_OK, stroke_width=7, tip_length=0.3,
                       max_tip_length_to_length_ratio=0.3)
            fl.set_opacity(o)
            return fl

        ang_lb = cifra_signo(0, "°", 34, C_OK)
        ang_lb.move_to([-3.6, 3.3, 0])
        ang_num = ang_lb[0]
        ang_lb.set_opacity(0)
        ang_txt = et("Haz", 24, TENUE).next_to(ang_lb, LEFT, buff=0.3)

        marco = always_redraw(elementos)
        self.play(FadeIn(marco, run_time=1.0))
        self.add(always_redraw(ondas), always_redraw(frentes), always_redraw(flecha_haz))

        ult = [None]

        def actualiza(_):
            v = int(round(np.degrees(theta(t.get_value()))))
            if ult[0] != abs(v):
                ult[0] = abs(v)
                ang_num.set_value(abs(v))
            ang_lb[1].next_to(ang_num, RIGHT, buff=0.04).align_to(ang_num, UP)
            o = suave((t.get_value() - 4.5) / 1.2)
            ang_lb.set_opacity(o)
            ang_txt.set_opacity(o)
        ang_lb.add_updater(actualiza)
        ang_txt.set_opacity(0)
        self.add(ang_lb, ang_txt)
        self.play(t.animate.set_value(DUR), run_time=DUR, rate_func=linear)
        self.cierre()


# ------------------------------------------------- 4. PolarizacionCircular
class PolarizacionCircular(Pieza3D):
    def construct(self):
        self.set_camera_orientation(phi=66 * DEGREES, theta=-62 * DEGREES, zoom=0.95)
        X0, X1, A = -3.0, 5.4, 1.25
        K = TAU / 3.0
        W = TAU / 2.4
        t = ValueTracker(0)
        t.add_updater(lambda tr, dt: tr.increment_value(dt))
        m = ValueTracker(0)
        xs = np.linspace(X0, X1, 220)
        idx = np.arange(0, 220, 6)

        def campo_vals():
            tt = t.get_value()
            mm = m.get_value()
            fase = K * (xs - X0) - W * tt
            frente = X0 + (W / K) * tt
            g = suave((xs - X0) / 0.8) * suave((frente - xs) / 0.8)
            ey = -mm * A * np.sin(fase) * g
            ez = A * np.cos(fase) * g
            return ey, ez

        def vectores():
            ey, ez = campo_vals()
            g = VGroup()
            for i in idx:
                if abs(ey[i]) + abs(ez[i]) > 0.02:
                    g.add(Line([xs[i], 0, 0], [xs[i], ey[i], ez[i]], color=C_CIELO,
                               stroke_width=2.5, stroke_opacity=0.75))
            if not len(g):
                g.add(Dot([X0, 0, 0], radius=0.001, fill_opacity=0))
            return g

        def curva():
            ey, ez = campo_vals()
            fr = X0 + (W / K) * t.get_value()
            k = max(3, int((xs < fr).sum()))
            return polilinea(np.stack([xs, ey, ez], axis=1)[:k], C_SAT, 5)

        eje = Arrow([X0 - 0.4, 0, 0], [X1 + 0.5, 0, 0], color=C_EJE, buff=0, stroke_width=3,
                    tip_length=0.25)
        dip = Line([X0 - 0.9, 0, -0.6], [X0 - 0.9, 0, 0.6], color=C_ANT, stroke_width=8)
        ali = Line([X0 - 0.9, 0, 0], [X0 - 0.4, 0, 0], color=C_EJE, stroke_width=3)
        hel = ParametricFunction(
            lambda u: np.array([X0 - 2.2 + 1.5 * u / (5 * TAU), 0.42 * np.cos(u), 0.42 * np.sin(u)]),
            t_range=[0, 5 * TAU], color=C_ANT, stroke_width=5)
        hel_ali = Line([X0 - 0.7, 0.42, 0], [X0 - 0.3, 0, 0], color=C_EJE, stroke_width=3)
        suelo = Circle(radius=0.75, color=C_EJE, stroke_width=2).rotate(PI / 2, axis=UP) \
            .move_to([X0 - 2.2, 0, 0])
        hel.set_stroke(opacity=0)
        suelo.set_stroke(opacity=0).set_fill(opacity=0)

        # inserto: vista de frente del vector E
        RI = 0.8
        cx = np.array([5.5, 2.6, 0])
        ins_ejes = VGroup(Line(cx + LEFT * 1.0, cx + RIGHT * 1.0, color=C_EJE, stroke_width=1.5),
                          Line(cx + DOWN * 1.0, cx + UP * 1.0, color=C_EJE, stroke_width=1.5))
        ins_el = Ellipse(width=2 * RI, height=2 * RI, color=C_EJE, stroke_width=2).move_to(cx)
        ins_pt = Dot(cx, radius=0.09, color=C_SAT)
        ins_vec = Line(cx, cx, color=C_SAT, stroke_width=4)

        def act_ins(_):
            fase = K * (1.0 - X0) - W * t.get_value()
            mm = m.get_value()
            ey, ez = -mm * A * np.sin(fase), A * np.cos(fase)
            p = cx + np.array([ey, ez, 0]) * RI / A
            ins_pt.move_to(p)
            ins_vec.put_start_and_end_on(cx, p)
            h = max(2 * RI * mm, 0.02)
            ins_el.become(Ellipse(width=2 * RI, height=h, color=C_EJE, stroke_width=2).move_to(cx))
        ins_pt.add_updater(act_ins)

        lb1 = et("Lineal", 30, C_ANT).move_to([-5.4, 3.2, 0])
        lb2 = et("Circular", 30, C_ANT).move_to(lb1)
        self.add_fixed_in_frame_mobjects(ins_ejes, ins_el, ins_pt, ins_vec, lb1)
        lb1.set_opacity(0)
        for x in (ins_ejes, ins_el, ins_pt, ins_vec):
            x.set_opacity(0)
        self.begin_ambient_camera_rotation(rate=0.015)
        self.add(t)
        self.play(FadeIn(eje), FadeIn(dip), FadeIn(ali), run_time=1.0)
        cam = always_redraw(vectores)
        cur = always_redraw(curva)
        self.add(cam, cur)
        self.play(*[x.animate.set_opacity(1) for x in (ins_ejes, ins_el, ins_pt, ins_vec, lb1)],
                  run_time=1.0)
        ins_ejes.set_opacity(1); ins_el.set_opacity(1)
        ins_pt.set_opacity(1); ins_vec.set_opacity(1)
        self.wait(7.5)
        self.add_fixed_in_frame_mobjects(lb2)
        lb2.set_opacity(0)
        self.add(hel_ali)
        hel_ali.set_opacity(0)
        self.add(hel, suelo)
        self.play(m.animate.set_value(1), FadeOut(dip), FadeOut(ali),
                  hel.animate.set_stroke(opacity=1), suelo.animate.set_stroke(opacity=1), hel_ali.animate.set_opacity(1),
                  lb1.animate.set_opacity(0), lb2.animate.set_opacity(1), run_time=3.5, rate_func=smooth)
        self.wait(7.0)
        self.cierre()


# --------------------------------------------------------- 5. BrazoRoboticoIK
class BrazoRoboticoIK(Pieza):
    def construct(self):
        L = [2.6, 2.2, 1.5]
        B = np.array([-3.0, -3.0])
        cen, amp = np.array([-0.9, 0.3]), np.array([1.9, 1.0])
        col = [C_SAT, C_OK, C_CIELO]

        def objetivo(s):
            return cen + amp * np.array([np.sin(s), np.sin(2 * s)])

        def ik(tg, s):
            v = tg - B
            phi = np.arctan2(v[1], v[0]) + 0.35 * np.sin(s)
            w = tg - L[2] * np.array([np.cos(phi), np.sin(phi)])
            vw = w - B
            dw = np.clip(np.hypot(*vw), abs(L[0] - L[1]) + 1e-3, L[0] + L[1] - 1e-3)
            c2 = (dw ** 2 - L[0] ** 2 - L[1] ** 2) / (2 * L[0] * L[1])
            best = None
            for sg in (-1,):
                t2 = sg * np.arccos(np.clip(c2, -1, 1))
                t1 = np.arctan2(vw[1], vw[0]) - np.arctan2(L[1] * np.sin(t2), L[0] + L[1] * np.cos(t2))
                el = B + L[0] * np.array([np.cos(t1), np.sin(t1)])
                best = (el[1], t1, t2)
            _, t1, t2 = best
            return t1, t2, phi - t1 - t2

        s = ValueTracker(0.0)
        b = ValueTracker(0.0)   # construcción 0..3
        va = ValueTracker(0.0)  # visibilidad arcos

        def poses():
            sv = s.get_value()
            tg = objetivo(sv)
            t1, t2, t3 = ik(tg, sv)
            j0 = B
            j1 = j0 + L[0] * np.array([np.cos(t1), np.sin(t1)])
            j2 = j1 + L[1] * np.array([np.cos(t1 + t2), np.sin(t1 + t2)])
            j3 = j2 + L[2] * np.array([np.cos(t1 + t2 + t3), np.sin(t1 + t2 + t3)])
            return (t1, t2, t3), tuple(np.append(j, 0) for j in (j0, j1, j2, j3))

        def brazo():
            (t1, t2, t3), J = poses()
            bv = b.get_value()
            g = VGroup()
            for i in range(3):
                fr = np.clip(bv - i, 0, 1)
                if fr > 0.01:
                    a, c = J[i], J[i + 1]
                    g.add(Line(a, a + (c - a) * fr, color=TINTA, stroke_width=13))
                    g.add(Line(a, a + (c - a) * fr, color=FONDO, stroke_width=5))
            for i in range(3):
                if bv > i:
                    g.add(Dot(J[i], radius=0.2, color=C_ANT), Dot(J[i], radius=0.09, color=FONDO))
            if bv >= 3:
                d = (J[3] - J[2]) / L[2]
                n = np.array([-d[1], d[0], 0])
                for sg in (-1, 1):
                    g.add(polilinea([J[3] - 0.05 * d + n * sg * 0.05 + d * 0.0,
                                     J[3] + d * 0.16 + n * sg * 0.17,
                                     J[3] + d * 0.42 + n * sg * 0.11], C_SAT, 5))
                g.add(Dot(J[3], radius=0.1, color=C_SAT))
            return g

        def arcos():
            (t1, t2, t3), J = poses()
            v = va.get_value()
            g = VGroup()
            refs = [0, t1, t1 + t2]
            angs = [t1, t2, t3]
            rad = [0.85, 0.6, 0.5]
            for i in range(3):
                p = J[i]
                r0 = refs[i]
                g.add(DashedLine(p, p + 1.15 * np.array([np.cos(r0), np.sin(r0), 0]),
                                 color=col[i], stroke_width=2, stroke_opacity=0.7 * v,
                                 dash_length=0.08))
                if abs(angs[i]) > 0.02:
                    g.add(Arc(radius=rad[i], start_angle=r0, angle=angs[i], arc_center=np.append(p[:2], 0),
                              color=col[i], stroke_width=6, stroke_opacity=v))
            return g

        # base
        pb = np.append(B, 0)
        base = Polygon(pb + LEFT * 0.8 + DOWN * 0.35, pb + RIGHT * 0.8 + DOWN * 0.35,
                       pb + RIGHT * 0.45 + DOWN * 0.0, pb + LEFT * 0.45 + DOWN * 0.0,
                       color=C_EJE, fill_color=C_EJE, fill_opacity=0.6, stroke_width=2)
        suelo = Line(pb + LEFT * 1.4 + DOWN * 0.35, pb + RIGHT * 1.4 + DOWN * 0.35,
                     color=C_EJE, stroke_width=3)

        tgt = VGroup(Circle(radius=0.2, color=TINTA, stroke_width=3),
                     Line(LEFT * 0.32, RIGHT * 0.32, color=TINTA, stroke_width=2),
                     Line(DOWN * 0.32, UP * 0.32, color=TINTA, stroke_width=2))
        tgt.move_to(np.append(objetivo(0), 0))
        tgt.add_updater(lambda g: g.move_to(np.append(objetivo(s.get_value()), 0)))
        centro_tgt = Dot(radius=0.001)
        centro_tgt.add_updater(lambda d: d.move_to(np.append(objetivo(s.get_value()), 0)))
        traza = TracedPath(centro_tgt.get_center, stroke_color=C_ANT, stroke_width=4,
                           stroke_opacity=0.75)

        # panel de ángulos
        filas = VGroup()
        nums = []
        for i, nm in enumerate(("θ1", "θ2", "θ3")):
            pt = Arc(radius=0.3, angle=1.6, color=col[i], stroke_width=6)
            lab = et(nm, 28, col[i])
            num = DecimalNumber(0, num_decimal_places=0, include_sign=True, font_size=44, color=col[i])
            num.set_stroke(width=0)
            gr = Text("°", font=FUENTE, font_size=36, color=TENUE)
            fila = VGroup(pt, lab, num, gr).arrange(RIGHT, buff=0.25)
            filas.add(fila)
            nums.append((num, gr))
        filas.arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to(np.array([4.7, 0.4, 0]))
        marco = RoundedRectangle(corner_radius=0.2, width=filas.width + 1.3, height=filas.height + 0.7,
                                 color=C_EJE, stroke_width=2, fill_color=C_PANEL, fill_opacity=0.35)
        marco.move_to(filas.get_center()).align_to(filas.get_left() + LEFT * 0.35, LEFT)
        ultimo = [None, None, None]

        def act_nums(_):
            (t1, t2, t3), _J = poses()
            for i, a in enumerate((t1, t2, t3)):
                v = int(round(np.degrees(a)))
                if ultimo[i] != v:
                    ultimo[i] = v
                    nums[i][0].set_value(v)
                    nums[i][0].set_color(col[i])
                    nums[i][1].next_to(nums[i][0], RIGHT, buff=0.08)
        va_o = lambda: va.get_value()

        # ---- secuencia
        self.play(FadeIn(base), Create(suelo), run_time=0.8)
        self.add(always_redraw(brazo))
        self.play(b.animate.set_value(3), run_time=2.6, rate_func=linear)
        self.play(FadeIn(tgt, scale=0.4), run_time=0.6)
        self.add(centro_tgt, traza, always_redraw(arcos))
        act_nums(None)
        self.play(FadeIn(marco), FadeIn(filas), va.animate.set_value(1), run_time=1.0)
        filas.add_updater(act_nums)
        self.play(s.animate.set_value(TAU), run_time=14, rate_func=smooth)
        self.wait(0.3)
        self.cierre()


# --------------------------------------------------- 6. ServicioEnOrbita
class ServicioEnOrbita(Pieza):
    def construct(self):
        RT = 7.6
        CT = np.array([0.0, -10.4, 0.0])
        fondo_est = estrellas(90, 6, 14, 6.5, 0.7).shift(UP * 0.7)
        # Tierra curva
        tie = VGroup()
        for k, (dr, op) in enumerate(((0.28, 0.06), (0.16, 0.12), (0.07, 0.22))):
            tie.add(Circle(radius=RT + dr, color=C_ANT, stroke_width=3, stroke_opacity=op)
                    .set_fill(opacity=0).move_to(CT))
        tie.add(Circle(radius=RT, color=C_TIERRA, fill_color=C_TIERRA_2, fill_opacity=1,
                       stroke_width=3).move_to(CT))
        rng = np.random.default_rng(11)
        cont = VGroup()
        for _ in range(46):
            a = rng.uniform(0, TAU)
            r = RT - rng.uniform(0.15, 1.2)
            w, h = rng.uniform(0.5, 1.5), rng.uniform(0.15, 0.5)
            e = Ellipse(width=w, height=h, color=C_TIERRA, fill_color=C_TIERRA, fill_opacity=0.5,
                        stroke_width=0)
            e.rotate(a + PI / 2).move_to(CT + r * np.array([np.cos(a), np.sin(a), 0]))
            cont.add(e)
        cont.add_updater(lambda g, dt: g.rotate(1.5 * DEGREES * dt, about_point=CT))

        def ala(w, h):
            return Rectangle(width=w, height=h, color=C_SAT, fill_color=C_CIELO,
                             fill_opacity=0.55, stroke_width=2)

        # cliente
        cb = Rectangle(width=0.9, height=0.8, color=C_SAT, fill_color=C_SAT, fill_opacity=0.85,
                       stroke_width=2)
        cw1 = ala(0.3, 1.0).next_to(cb, UP, buff=0.04)
        cw2 = ala(0.3, 1.0).next_to(cb, DOWN, buff=0.04)
        stub = Line(cb.get_left(), cb.get_left() + LEFT * 0.32, color=TINTA, stroke_width=4)
        ring = Circle(radius=0.11, color=TINTA, stroke_width=3).move_to(cb.get_left() + LEFT * 0.32)
        led = Dot(cb.get_corner(UR) + LEFT * 0.2 + DOWN * 0.2, radius=0.07, color=C_MAL)
        cli = VGroup(cb, cw1, cw2, stub, ring, led)
        # servidor
        sb = Rectangle(width=1.4, height=1.0, color=C_SAT, fill_color=C_SAT, fill_opacity=0.85,
                       stroke_width=2)
        sw1 = ala(0.36, 1.3).next_to(sb, UP, buff=0.04)
        sw2 = ala(0.36, 1.3).next_to(sb, DOWN, buff=0.04)
        raya = Rectangle(width=1.4, height=0.14, color=C_ANT, fill_color=C_ANT, fill_opacity=1,
                         stroke_width=0).move_to(sb.get_center() + UP * 0.28)
        bahia = Rectangle(width=0.2, height=0.3, color=TINTA, fill_color=FONDO, fill_opacity=1,
                          stroke_width=2).move_to(sb.get_right() + LEFT * 0.1)
        srv = VGroup(sb, sw1, sw2, raya, bahia)

        XC0, YS = 2.7, 0.55
        cli.move_to([XC0, YS, 0])
        LA, LB = 1.4, 1.4
        srv_final = np.array([-1.5, YS, 0])
        srv.move_to([-9.5, YS - 0.9, 0]).rotate(16 * DEGREES)

        e = ValueTracker(0.0)       # extensión del brazo
        gr = ValueTracker(1.0)      # apertura de la pinza
        armvis = ValueTracker(0.0)
        cliente_fijo = {"x": XC0}

        def grapple():
            return cb.get_left() + LEFT * 0.32

        def base():
            return sb.get_center() + RIGHT * 0.7

        def brazo():
            v = armvis.get_value()
            if v < 0.01:
                return VGroup(Dot(radius=0.001, fill_opacity=0))
            B0 = base()
            S = B0 + np.array([1.55, 0.45, 0])
            G = grapple()
            tip = S + e.get_value() * (G - S)
            vv = tip - B0
            d = np.clip(np.hypot(vv[0], vv[1]), 0.05, LA + LB - 1e-3)
            c2 = np.clip((d ** 2 - LA ** 2 - LB ** 2) / (2 * LA * LB), -1, 1)
            best = None
            for sg in (1, -1):
                t2 = sg * np.arccos(c2)
                t1 = np.arctan2(vv[1], vv[0]) - np.arctan2(LB * np.sin(t2), LA + LB * np.cos(t2))
                el = B0 + LA * np.array([np.cos(t1), np.sin(t1), 0])
                if best is None or el[1] > best[0][1]:
                    best = (el, t1, t2)
            el, t1, t2 = best
            wr = el + LB * np.array([np.cos(t1 + t2), np.sin(t1 + t2), 0])
            ang = t1 + t2
            dvec = np.array([np.cos(ang), np.sin(ang), 0])
            nvec = np.array([-dvec[1], dvec[0], 0])
            g = VGroup()
            for a, b_ in ((B0, el), (el, wr)):
                g.add(Line(a, b_, color=C_ANT, stroke_width=9, stroke_opacity=v))
            for p, r in ((B0, 0.13), (el, 0.13), (wr, 0.1)):
                g.add(Dot(p, radius=r, color=C_ANT, fill_opacity=v),
                      Dot(p, radius=r * 0.45, color=FONDO, fill_opacity=v))
            ap = 0.75 * gr.get_value() + 0.12
            for sg in (-1, 1):
                q0 = wr + dvec * 0.02
                q1 = wr + dvec * 0.2 + nvec * sg * 0.22 * ap
                q2 = wr + dvec * 0.38 + nvec * sg * 0.15 * ap
                g.add(polilinea([q0, q1, q2], C_SAT, 5, op=v))
            return g

        arm = always_redraw(brazo)

        lb_s = et("Servidor", 24, TENUE)
        lb_c = et("Cliente", 24, TENUE)
        lb_s.add_updater(lambda m: m.next_to(sw1, UP, buff=0.2))
        lb_c.add_updater(lambda m: m.next_to(cw1, UP, buff=0.25))

        self.add(fondo_est)
        self.play(FadeIn(tie), FadeIn(cont), FadeIn(cli), run_time=1.3)
        self.add(cont)
        self.add(srv)
        self.play(FadeIn(lb_c), run_time=0.4)
        # aproximación: traslación + alineación
        self.play(srv.animate.move_to(srv_final).rotate(-16 * DEGREES),
                  run_time=6.5, rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(lb_s), run_time=0.4)
        self.play(Flash(led, color=C_MAL, flash_radius=0.3, line_length=0.1, run_time=0.8))
        # brazo
        self.add(arm)
        self.play(armvis.animate.set_value(1), run_time=0.7)
        self.play(FadeOut(lb_s), FadeOut(lb_c), run_time=0.4)
        self.play(e.animate.set_value(1), run_time=2.6, rate_func=smooth)
        self.play(gr.animate.set_value(0), run_time=0.7, rate_func=smooth)
        self.wait(0.3)
        # arrastre: el cliente sigue a la punta
        XD = sb.get_right()[0] + 0.05 + 0.45 + 0.0
        XD += 0.0
        cli.generate_target()
        self.play(cli.animate.move_to([XD + 0.0, YS, 0]), run_time=3.2, rate_func=smooth,
                  suspend_mobject_updating=False)
        self.play(FadeOut(arm, run_time=0.6))
        cierres = VGroup(*[Rectangle(width=0.1, height=0.2, color=C_OK, fill_color=C_OK,
                                     fill_opacity=1, stroke_width=0)
                           .move_to([sb.get_right()[0] + 0.02, YS + dy, 0]) for dy in (0.3, -0.3)])
        self.play(FadeIn(cierres), led.animate.set_color(C_OK), run_time=0.6)
        ok = et("Acoplado", 30, C_OK).next_to(VGroup(srv, cli), UP, buff=0.25)
        self.play(FadeIn(ok, shift=UP * 0.15), Flash(led, color=C_OK, flash_radius=0.35,
                                                     line_length=0.12, run_time=0.9))
        self.cierre()


# ------------------------------------------------------ 7. EnjambreRobots
class EnjambreRobots(Pieza):
    def construct(self):
        N, dt, TT = 26, 1 / 60, 19.0
        rng = np.random.default_rng(7)
        pos = rng.uniform([-5.5, -3.0], [5.5, 3.0], (N, 2))
        ang0 = rng.uniform(0, TAU, N)
        vel = 1.2 * np.stack([np.cos(ang0), np.sin(ang0)], axis=1)
        hd = ang0.copy()

        # formas objetivo
        RR = 2.6
        ring = np.stack([RR * np.cos(np.linspace(0, TAU, N, endpoint=False) + 0.3),
                         RR * np.sin(np.linspace(0, TAU, N, endpoint=False) + 0.3)], axis=1)
        vert = []
        for k in range(10):
            r = 3.15 if k % 2 == 0 else 1.3
            a = PI / 2 + k * PI / 5
            vert.append([r * np.cos(a), r * np.sin(a)])
        vert = np.array(vert)
        seg = np.diff(np.vstack([vert, vert[:1]]), axis=0)
        ls = np.hypot(seg[:, 0], seg[:, 1])
        cum = np.concatenate([[0], np.cumsum(ls)])
        star = []
        for s_ in np.linspace(0, cum[-1], N, endpoint=False):
            i = np.searchsorted(cum, s_, side="right") - 1
            f = (s_ - cum[i]) / ls[i]
            star.append(vert[i] + seg[i] * f)
        star = np.array(star)

        def asigna(p, objetivos):
            D = np.linalg.norm(p[:, None, :] - objetivos[None, :, :], axis=2)
            r_, c_ = linear_sum_assignment(D)
            t = np.zeros_like(objetivos)
            t[r_] = objetivos[c_]
            return t

        nsteps = int(TT / dt) + 1
        P = np.zeros((nsteps, N, 2))
        H = np.zeros((nsteps, N))
        tgt = None
        for i in range(nsteps):
            tt = i * dt
            P[i], H[i] = pos, hd
            fase = 0 if tt < 6 else (1 if tt < 11 else 2)
            if fase == 1 and (tgt is None or tgt is star):
                tgt = asigna(pos, ring)
            if fase == 2 and tgt is not star and (tgt is None or not np.allclose(tgt, star)):
                tgt = asigna(pos, star)
            d = np.linalg.norm(pos[:, None] - pos[None], axis=2) + np.eye(N) * 99
            acc = np.zeros_like(pos)
            if fase == 0:
                vecino = d < 2.2
                nn = vecino.sum(1, keepdims=True).clip(1)
                vm = (vecino[:, :, None] * vel[None]).sum(1) / nn
                pm = (vecino[:, :, None] * pos[None]).sum(1) / nn
                acc += 1.6 * (vm - vel) + 0.9 * (pm - pos)
                cerca = d < 0.75
                acc += 3.5 * (cerca[:, :, None] * (pos[:, None] - pos[None]) / (d[:, :, None] ** 2 + 0.05)).sum(1)
                wall = np.zeros_like(pos)
                wall[:, 0] = np.where(pos[:, 0] > 5.3, -1, 0) + np.where(pos[:, 0] < -5.3, 1, 0)
                wall[:, 1] = np.where(pos[:, 1] > 2.8, -1, 0) + np.where(pos[:, 1] < -2.8, 1, 0)
                acc += 4.0 * wall
                vel += acc * dt
                sp = np.linalg.norm(vel, axis=1, keepdims=True)
                vel = vel / sp * np.clip(sp, 0.9, 1.7)
            else:
                vd = (tgt - pos) * 1.5
                nv = np.linalg.norm(vd, axis=1, keepdims=True)
                vd = vd / np.maximum(nv, 1e-6) * np.minimum(nv, 2.6)
                acc += 5.0 * (vd - vel)
                lejos = (np.linalg.norm(tgt - pos, axis=1) > 0.8)[:, None]
                cerca = d < 0.5
                acc += lejos * 1.5 * (cerca[:, :, None] * (pos[:, None] - pos[None]) / (d[:, :, None] ** 2 + 0.05)).sum(1)
                vel += acc * dt
            pos = pos + vel * dt
            sp = np.linalg.norm(vel, axis=1)
            des = np.arctan2(vel[:, 1], vel[:, 0])
            if fase > 0:
                fuera = np.arctan2(tgt[:, 1], tgt[:, 0])
                dcen = np.linalg.norm(tgt - pos, axis=1)
                w = np.clip((0.6 - dcen) / 0.4, 0, 1)
                des = np.where(sp < 0.35, fuera, des)
                des = des + (1 - w) * 0  # rumbo por velocidad al viajar
                des = np.where(w > 0, np.arctan2((1 - w) * np.sin(des) + w * np.sin(fuera),
                                                 (1 - w) * np.cos(des) + w * np.cos(fuera)), des)
            dif = (des - hd + PI) % TAU - PI
            hd = hd + dif * min(1.0, 7 * dt)

        tr = ValueTracker(0)
        cols = [C_SAT if k % 2 == 0 else C_ANT for k in range(N)]
        ags = VGroup(*[VMobject() for _ in range(N)])
        trs = VGroup(*[VMobject() for _ in range(N)])
        for k in range(N):
            ags[k].set_points_as_corners(np.zeros((4, 3)))
            trs[k].set_points_as_corners(np.zeros((3, 3)))

        def act(_):
            tt = min(tr.get_value(), TT)
            i = min(int(tt / dt), nsteps - 1)
            for k in range(N):
                p, h = P[i, k], H[i, k]
                u = np.array([np.cos(h), np.sin(h)])
                nrm = np.array([-u[1], u[0]])
                v0 = p + u * 0.24
                v1 = p - u * 0.15 + nrm * 0.15
                v2 = p - u * 0.15 - nrm * 0.15
                ags[k].set_points_as_corners([[*v0, 0], [*v1, 0], [*v2, 0], [*v0, 0]])
                ags[k].set_stroke(cols[k], 2, opacity=1).set_fill(cols[k], opacity=0.85)
                j = np.arange(max(0, i - 48), i + 1, 6)
                if len(j) >= 2:
                    trs[k].set_points_as_corners(np.hstack([P[j, k], np.zeros((len(j), 1))]))
                    trs[k].set_stroke(cols[k], 2, opacity=0.35)
        ags.add_updater(act)
        ags.add_updater(lambda g: None)

        star_poly = Polygon(*[[*v, 0] for v in vert], color=C_CIELO, stroke_width=2.5)
        star_poly.set_stroke(opacity=0)
        ring_c = Circle(radius=RR, color=C_CIELO, stroke_width=2, stroke_opacity=0)
        ring_c.rotate(0)
        aro = ValueTracker(0)

        def act_fig(_):
            t_ = tr.get_value()
            o_r = suave((t_ - 8.0) / 1.5) * (1 - suave((t_ - 11.0) / 1.0))
            o_s = suave((t_ - 15.0) / 1.5)
            ring_c.set_stroke(opacity=0.5 * o_r)
            star_poly.set_stroke(opacity=0.8 * o_s)
        ring_c.add_updater(act_fig)

        act(None)
        self.add(ring_c, star_poly, trs, ags)
        self.play(FadeIn(ags, run_time=1.0), FadeIn(trs, run_time=1.0))
        self.play(tr.animate.set_value(TT), run_time=TT, rate_func=linear)
        self.cierre()


# ----------------------------------------------------------- 8. RoverLunar
class RoverLunar(Pieza):
    def construct(self):
        cr = [(3.5, 1.5, 0.62), (10.5, 2.0, 0.85), (17.5, 1.4, 0.55), (24.5, 1.8, 0.75),
              (31.0, 1.3, 0.5)]

        def terr(x):
            y = -2.1 + 0.06 * np.sin(0.9 * x) + 0.04 * np.sin(2.3 * x + 1)
            for c, w, d in cr:
                u = (x - c) / w
                y = y - d * np.exp(-u * u) + 0.35 * d * np.exp(-((abs(u) - 1.35) / 0.35) ** 2)
            return y

        def cresta(x):
            return -1.55 + 0.35 * np.sin(0.45 * x) + 0.18 * np.sin(1.3 * x + 2)

        F = 1.45
        s = ValueTracker(0.0)
        V = 1.05
        XR = -3.4
        EARTH = np.array([4.6, 2.55, 0.0])
        xs = np.linspace(-7.4, 7.4, 150)

        def suelo():
            sv = s.get_value()
            pts = [[x, terr(x + sv), 0] for x in xs]
            pts = [[xs[0], -4.3, 0]] + pts + [[xs[-1], -4.3, 0]]
            m = polilinea(pts, TENUE, 3, relleno=0.0, cerrar=True)
            m.set_fill(C_EJE, opacity=0.45)
            top = polilinea(pts[1:-1], TENUE, 3.5)
            return VGroup(m.set_stroke(width=0), top)

        def lejos():
            sv = s.get_value() * 0.35
            pts = [[x, cresta(x + sv), 0] for x in xs]
            pts = [[xs[0], -4.3, 0]] + pts + [[xs[-1], -4.3, 0]]
            m = polilinea(pts, C_EJE, 2, cerrar=True)
            m.set_fill(C_PANEL, opacity=0.35).set_stroke(C_EJE, 2, opacity=0.6)
            return m

        # Tierra creciente
        RE = 0.55
        disco = Circle(radius=RE, color=C_TIERRA_2, fill_color=C_TIERRA_2, fill_opacity=0.35,
                       stroke_width=1).move_to(EARTH)
        aa = np.linspace(0, PI, 40)
        k_ = 0.35
        cre = [[RE * np.sin(a), RE * np.cos(a)] for a in aa] + \
              [[k_ * RE * np.sin(a), RE * np.cos(a)] for a in aa[::-1]]
        creciente = polilinea(np.array(cre) + EARTH[:2], C_TIERRA, 1, relleno=1.0, cerrar=True)
        creciente.set_stroke(C_TIERRA, 1).set_fill(C_TIERRA, 1)
        tierra_g = VGroup(disco, creciente)

        estr = estrellas(70, 3, 14, 6.5, 0.7).shift(UP * 1.2)
        F = 1.45
        RW = 0.21 * F
        off = np.array([-0.95, -0.32, 0.32, 0.95]) * F

        def pose():
            sv = s.get_value()
            cen, nor = [], []
            for o in off:
                x = XR + o
                y = terr(x + sv)
                sl = (terr(x + sv + 0.02) - terr(x + sv - 0.02)) / 0.04
                n = np.array([-sl, 1.0]) / np.hypot(sl, 1.0)
                cen.append(np.array([x, y]) + RW * n)
            ang = np.arctan2(cen[3][1] - cen[0][1], cen[3][0] - cen[0][0])
            mid = (cen[0] + cen[3]) / 2
            return cen, ang, mid

        def rover():
            sv = s.get_value()
            cen, ang, mid = pose()
            g = VGroup()
            u = np.array([np.cos(ang), np.sin(ang)])
            n = np.array([-u[1], u[0]])
            c0 = mid + n * 0.5 * F
            # chasis
            def rect(cx, w, h, col, fill, op, sw=2):
                p = [cx + u * (-w / 2) + n * (-h / 2), cx + u * (w / 2) + n * (-h / 2),
                     cx + u * (w / 2) + n * (h / 2), cx + u * (-w / 2) + n * (h / 2)]
                return polilinea(p, col, sw, relleno=op, cerrar=True).set_fill(fill, op)
            for c in cen:
                g.add(Line([*(c), 0], [*(mid + n * 0.28 * F), 0], color=C_EJE, stroke_width=3))
            g.add(rect(c0, 1.9 * F, 0.42 * F, TINTA, C_SAT, 0.9))
            g.add(rect(c0 + (n * 0.28 - u * 0.1) * F, 1.5 * F, 0.07 * F, C_SAT, C_CIELO, 0.9, 2))
            g.add(rect(c0 + (u * 0.55 + n * 0.1) * F, 0.3 * F, 0.14 * F, TINTA, C_ANT, 0.9, 1.5))
            # ruedas
            for c in cen:
                g.add(Circle(radius=RW, color=TINTA, stroke_width=4, fill_color=FONDO,
                             fill_opacity=1).move_to([*c, 0]))
                for k in range(3):
                    a = -sv / RW + k * PI / 3
                    d = np.array([np.cos(a), np.sin(a)]) * RW * 0.95
                    g.add(Line([*(c - d), 0], [*(c + d), 0], color=TINTA, stroke_width=2))
            # mástil y plato
            mb = c0 + (-u * 0.55 + n * 0.21) * F
            mt = mb + n * 0.85 * F
            g.add(Line([*mb, 0], [*mt, 0], color=TINTA, stroke_width=4))
            dirE = EARTH[:2] - mt
            aE = np.arctan2(dirE[1], dirE[0])
            pl = polilinea(plato_pts(0.16 * F, 0.34 * F, 24), C_ANT, 5)
            pl.rotate(aE, about_point=ORIGIN).shift([*(mt), 0])
            fe = mt + 0.16 * F * np.array([np.cos(aE), np.sin(aE)])
            g.add(pl, Dot([*fe, 0], radius=0.05, color=C_SAT))
            self.fe = fe
            return g

        def enlace():
            cen, ang, mid = pose()
            u = np.array([np.cos(ang), np.sin(ang)])
            n = np.array([-u[1], u[0]])
            c0 = mid + n * 0.5 * F
            mt = c0 + (-u * 0.55 + n * 0.21) * F + n * 0.85 * F
            dirE = EARTH[:2] - mt
            aE = np.arctan2(dirE[1], dirE[0])
            a = mt + 0.2 * np.array([np.cos(aE), np.sin(aE)])
            b = EARTH[:2] - RE * 1.25 * np.array([np.cos(aE), np.sin(aE)])
            g = VGroup(DashedLine([*a, 0], [*b, 0], color=C_ANT, stroke_width=2.5,
                                  dash_length=0.14, stroke_opacity=0.8))
            for k in range(3):
                ph = (tr_t.get_value() * 0.45 + k / 3) % 1
                g.add(Dot([*(a + (b - a) * ph), 0], radius=0.07, color=C_SAT))
            return g

        tr_t = ValueTracker(0)
        self.add(estr)
        far = always_redraw(lejos)
        terreno = always_redraw(suelo)
        self.play(FadeIn(far), FadeIn(terreno), FadeIn(tierra_g), run_time=1.2)
        rv = always_redraw(rover)
        en = always_redraw(enlace)
        self.add(rv, en)
        TD = 18.0
        self.play(s.animate.set_value(V * TD), tr_t.animate.set_value(TD), run_time=TD,
                  rate_func=linear)
        self.cierre()


# ---------------------------------------------------- 9. SDRAntenaANumero
class SDRAntenaANumero(Pieza):
    def construct(self):
        rng = np.random.default_rng(5)
        N = 64
        # ---- datos: señal compleja en banda base y espectros por fila
        NF = 100
        kk = np.arange(N)
        win = np.hanning(N)
        Sp = np.zeros((NF, N))
        x0 = None
        for r in range(NF):
            f2 = -13 + 0.27 * r
            x = 0.6 * np.exp(2j * np.pi * 4 * kk / N) + 0.42 * np.exp(2j * np.pi * f2 * kk / N)
            x = x + 0.03 * (rng.standard_normal(N) + 1j * rng.standard_normal(N))
            if x0 is None:
                x0 = x
            X = np.fft.fftshift(np.abs(np.fft.fft(x * win)))
            db = 20 * np.log10(X / (0.6 * N / 2) + 1e-4)
            Sp[r] = np.clip((db + 50) / 50, 0, 1)
        xnum = 0.6 * np.exp(2j * np.pi * 4 * np.arange(60) / 64) + \
            0.42 * np.exp(2j * np.pi * -6 * np.arange(60) / 64)

        # ---- cadena de bloques
        nombres = ["Antena", "LNA/Filtro", "Mezclador", "ADC", "FFT"]
        xs = [-5.5, -2.75, 0.0, 2.75, 5.5]
        bl = [caja(n, 2.0, 0.8, C_EJE, 22, 0.10).move_to([x, 2.5, 0]) for n, x in zip(nombres, xs)]
        fl = [flecha([xs[i] + 1.05, 2.5, 0], [xs[i + 1] - 1.05, 2.5, 0], TENUE, 3, 0.14)
              for i in range(4)]

        def luz(i):
            return bl[i][0].animate.set_stroke(C_ANT).set_fill(C_ANT, 0.3)

        def panel(cx, w):
            return RoundedRectangle(corner_radius=0.15, width=w, height=4.6, color=C_EJE,
                                    stroke_width=2, fill_color=C_PANEL, fill_opacity=0.25) \
                .move_to([cx, -1.1, 0])

        pA, pB, pC = panel(-4.7, 3.8), panel(-0.6, 3.6), panel(4.2, 4.9)

        # ---- panel A: señal analógica y muestras
        xa0, xa1, ya = -6.3, -3.1, -1.2
        tt = np.linspace(0, 1, 300)

        def sen(t):
            return 0.55 * np.sin(2 * PI * 2 * t) + 0.4 * np.sin(2 * PI * 5 * t + 0.6)
        ana = polilinea(np.stack([xa0 + (xa1 - xa0) * tt, ya + 1.25 * sen(tt)], axis=1), C_ANT, 4)
        base_a = Line([xa0 - 0.1, ya, 0], [xa1 + 0.1, ya, 0], color=C_EJE, stroke_width=2)
        ns = 24
        tk = (np.arange(ns) + 0.5) / ns
        stems = VGroup()
        for t_ in tk:
            xx = xa0 + (xa1 - xa0) * t_
            yy = ya + 1.25 * sen(t_)
            stems.add(VGroup(Line([xx, ya, 0], [xx, yy, 0], color=C_SAT, stroke_width=3),
                             Dot([xx, yy, 0], radius=0.065, color=C_SAT)))

        # ---- panel B: flujo de números I/Q
        hi = et("I", 26, C_ANT).move_to([-1.35, 0.55, 0])
        hq = et("Q", 26, C_SAT).move_to([0.15, 0.55, 0])
        nfil = 40
        rows = VGroup()
        for k in range(nfil):
            zi = xnum[k].real
            zq = xnum[k].imag
            ti = Text(f"{zi:+.2f}".replace("-", "−"), font=FUENTE, font_size=22, color=C_ANT)
            tq = Text(f"{zq:+.2f}".replace("-", "−"), font=FUENTE, font_size=22, color=C_SAT)
            ti.move_to([-1.35, 0, 0])
            tq.move_to([0.15, 0, 0])
            rows.add(VGroup(ti, tq).shift(DOWN * 0.36 * k))
        rows.shift(UP * (-3.45 - rows[0].get_center()[1] + 0.0))
        ytop, ybot = 0.25, -3.1

        def act_rows(m, dt):
            m.shift(UP * 1.25 * dt)
            for r in m:
                y = r.get_center()[1]
                o = float(np.clip(min((y - ybot) / 0.45, (ytop - y) / 0.45), 0, 1))
                r.set_opacity(o)
        for r in rows:
            r.set_opacity(0)

        # ---- panel C: espectro + cascada
        xc0, xc1 = 1.95, 6.45
        yb = -0.6
        xb = np.linspace(xc0, xc1, N)
        tr = ValueTracker(0)
        sf = ValueTracker(0)
        ow = ValueTracker(0)

        def fila_actual():
            return int(min(tr.get_value() * 4, NF - 1))

        def espectro():
            v = Sp[fila_actual()]
            n = max(2, int(sf.get_value() * N))
            pts = np.stack([xb, yb + 1.35 * v], axis=1)[:n]
            g = VGroup()
            area = np.vstack([[pts[0, 0], yb], pts, [pts[-1, 0], yb]])
            g.add(polilinea(area, C_ANT, 0, relleno=0.22, cerrar=True).set_stroke(width=0))
            g.add(polilinea(pts, C_ANT, 3))
            for i in range(1, n - 1):
                if v[i] > 0.78 and v[i] >= v[i - 1] and v[i] >= v[i + 1]:
                    g.add(Dot([pts[i, 0], pts[i, 1], 0], radius=0.075, color=C_SAT))
            return g

        stops = [0.0, 0.5, 0.8, 1.0]
        cols = [C_PANEL, C_CIELO, C_ANT, C_SAT]
        pal = np.zeros((256, 3))
        for i in range(256):
            u = i / 255
            j = max(0, min(2, int(np.searchsorted(stops, u, side="right") - 1)))
            f = (u - stops[j]) / (stops[j + 1] - stops[j])
            pal[i] = color_to_rgb(interpolate_color(ManimColor(cols[j]), ManimColor(cols[j + 1]), f))
        RW = 26

        def cascada():
            r0 = fila_actual()
            idx = np.clip(np.arange(r0, r0 - RW, -1), 0, NF - 1)
            v = Sp[idx]
            rgb = pal[(v * 255).astype(int)]
            a = np.full(v.shape + (1,), ow.get_value())
            arr = (np.concatenate([rgb, a], axis=2) * 255).astype(np.uint8)
            im = ImageMobject(arr)
            im.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
            im.stretch_to_fit_width(xc1 - xc0).stretch_to_fit_height(2.3)
            im.move_to([(xc0 + xc1) / 2, -2.05, 0])
            return im

        # ---- secuencia
        self.play(LaggedStart(*[AnimationGroup(FadeIn(b, shift=UP * 0.15)) for b in bl],
                              lag_ratio=0.3, run_time=2.0))
        self.play(LaggedStart(*[GrowArrow(f) for f in fl], lag_ratio=0.3, run_time=1.2))
        self.play(FadeIn(pA), luz(0), run_time=0.6)
        pulso_ = Dot([xs[0] - 1.0, 2.5, 0], radius=0.11, color=C_SAT)
        self.add(pulso_)
        self.play(FadeIn(base_a), Create(ana, run_time=2.4, rate_func=linear),
                  pulso_.animate.move_to([xs[1] - 1.05, 2.5, 0]), luz(1), run_time=2.4)
        self.play(pulso_.animate.move_to([xs[2] - 1.05, 2.5, 0]), luz(2), run_time=0.7)
        self.play(pulso_.animate.move_to([xs[3] - 1.05, 2.5, 0]), luz(3), run_time=0.7)
        # muestreo
        self.play(LaggedStart(*[FadeIn(s_, shift=DOWN * 0.0) for s_ in stems], lag_ratio=0.18,
                              run_time=3.0), ana.animate.set_stroke(opacity=0.3))
        # números
        self.play(FadeIn(pB), FadeIn(hi), FadeIn(hq), run_time=0.6)
        self.add(rows)
        rows.add_updater(act_rows)
        self.play(pulso_.animate.move_to([xs[4] - 1.05, 2.5, 0]), luz(4), run_time=0.8)
        self.wait(2.2)
        # espectro
        self.play(FadeIn(pC), run_time=0.5)
        esp = always_redraw(espectro)
        wf = always_redraw(cascada)
        self.add(esp, wf)
        self.play(sf.animate.set_value(1), run_time=1.6, rate_func=linear)
        tr.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(tr)
        self.play(ow.animate.set_value(1), run_time=1.2)
        self.play(FadeOut(pulso_, run_time=0.3))
        self.wait(6.0)
        rows.remove_updater(act_rows)
        self.cierre()


# ----------------------------------------------------- 10. EspectroFourier
class EspectroFourier(Pieza):
    def construct(self):
        R1, cx, x0, xw = 1.3, -4.3, -1.7, 4.2
        hs = [1, 3, 5, 7, 9, 11, 13]
        an = [R1 / n for n in hs]
        tk = [1.0 + 2.1 * i for i in range(7)]
        t = ValueTracker(0)
        t.add_updater(lambda m, dt: m.increment_value(dt))
        PER = 5.0
        nivel = R1 * PI / 4

        def w(i):
            return suave((t.get_value() - tk[i]) / 0.9)

        def theta():
            return TAU * t.get_value() / PER

        def cadena():
            g = VGroup()
            c = np.array([cx, 0.0])
            th = theta()
            for i, n in enumerate(hs):
                r = an[i] * w(i)
                if r < 0.01:
                    continue
                g.add(Circle(radius=r, color=C_ANT, stroke_width=2, stroke_opacity=0.65)
                      .move_to([*c, 0]))
                tip = c + r * np.array([np.cos(n * th), np.sin(n * th)])
                g.add(Line([*c, 0], [*tip, 0], color=TINTA, stroke_width=2, stroke_opacity=0.8))
                c = tip
            g.add(Dot([*c, 0], radius=0.09, color=C_SAT))
            g.add(DashedLine([*c, 0], [x0, c[1], 0], color=C_SAT, stroke_width=2,
                             stroke_opacity=0.55, dash_length=0.12))
            return g

        xw_ = np.linspace(0, xw, 320)
        kx = TAU * 2 / xw

        def onda():
            th = theta() - kx * xw_
            y = np.zeros_like(xw_)
            for i, n in enumerate(hs):
                y += w(i) * an[i] * np.sin(n * th)
            fade = suave(xw_ / 0.3)
            return polilinea(np.stack([x0 + xw_, y * 1.0], axis=1), C_SAT, 4.5)

        def objetivo():
            th = theta() - kx * xw_
            y = nivel * np.sign(np.sin(th))
            return polilinea(np.stack([x0 + xw_, y], axis=1), TENUE, 2, op=0.5)

        # espectro
        bx0, dxb, yb, esc = 3.55, 0.52, -1.45, 2.9
        eje = Line([bx0 - 0.4, yb, 0], [bx0 + 6 * dxb + 0.4, yb, 0], color=C_EJE, stroke_width=2.5)
        marc = VGroup(*[et(str(n), 20, TENUE).move_to([bx0 + i * dxb, yb - 0.3, 0])
                        for i, n in enumerate(hs)])
        lf = et("Frecuencia", 22, TENUE).move_to([bx0 + 3 * dxb, yb - 0.85, 0])

        def barras():
            g = VGroup()
            for i, n in enumerate(hs):
                h = esc * w(i) / n
                if h > 0.02:
                    g.add(Rectangle(width=0.3, height=h, color=C_CIELO, fill_color=C_CIELO,
                                    fill_opacity=0.85, stroke_width=1)
                          .move_to([bx0 + i * dxb, yb + h / 2, 0]))
            return g

        self.play(FadeIn(eje), FadeIn(marc), FadeIn(lf), run_time=0.8)
        self.add(t)
        obj = always_redraw(objetivo)
        self.add(obj, always_redraw(onda), always_redraw(cadena), always_redraw(barras))
        self.wait(tk[-1] + 1.0 + 3.6 - 0.8)
        self.cierre()

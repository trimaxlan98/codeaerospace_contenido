"""Bancos de prueba y gemelos digitales para satélites (Co.De Aerospace)."""
from code_lib import *
import numpy as np

SOMBRA = "#0B1F3A"


# ---------------------------------------------------------------- helpers ---
def suave(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def trazo(xs, ys, color, ancho=3, op=1.0):
    m = VMobject()
    m.set_points_as_corners(np.column_stack([xs, ys, np.zeros_like(xs)]))
    m.set_fill(opacity=0)
    m.set_stroke(color, width=ancho, opacity=op)
    return m


def cifra_viva(fn, unidad="", tam=26, color=None, dec=0, centro=ORIGIN, borde=ORIGIN):
    """Cifra que se actualiza sola con fn() (Carlito, sin LaTeX)."""
    col = color or C_ANT
    g = VGroup(Text("0", font=FUENTE, font_size=tam, color=col))
    if unidad:
        g.add(Text(unidad, font=FUENTE, font_size=tam * 0.7, color=TENUE))

    def act(m):
        v = fn()
        txt = f"{v:.{dec}f}".replace("-", "\u2212")
        m[0].become(Text(txt, font=FUENTE, font_size=tam, color=col))
        if len(m) > 1:
            m.arrange(RIGHT, buff=0.1, aligned_edge=DOWN)
        m.move_to(centro, aligned_edge=borde)
    g.add_updater(act)
    act(g)
    return g


def holograma(tam=0.32, color=None):
    c = color or C_CIELO
    base = satelite(tam, c, True)
    g = VGroup()
    for p in base:
        f = p.copy().set_stroke(width=0).set_fill(c, opacity=0.16)
        o = DashedVMobject(p.copy().set_fill(opacity=0), num_dashes=18)
        o.set_stroke(c, width=2.2)
        g.add(f, o)
    return g


def resorte(p0, p1, n=6, ancho=0.16, color=None, w=2.5):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d)
    u = d / L
    nrm = np.array([-u[1], u[0], 0])
    pts = [p0, p0 + u * L * 0.12]
    for i in range(n):
        t = 0.12 + 0.76 * (i + 0.5) / n
        pts.append(p0 + u * L * t + nrm * ancho * (1 if i % 2 == 0 else -1))
    pts += [p0 + u * L * 0.88, p1]
    m = VMobject()
    m.set_points_as_corners(pts)
    m.set_stroke(color or TENUE, width=w)
    return m


# =================================================================== 1 ======
def placa_obc(w=2.6, h=2.0, c=None):
    c = c or C_SAT
    base = RoundedRectangle(corner_radius=0.12, width=w, height=h, color=c,
                            fill_color=c, fill_opacity=0.10, stroke_width=3)
    cpu = Square(0.8, color=c, fill_color=c, fill_opacity=0.5, stroke_width=2).move_to([-0.4, 0.15, 0])
    pins = VGroup()
    for i in range(5):
        x = -0.4 - 0.28 + i * 0.14
        pins.add(Line([x, 0.55, 0], [x, 0.66, 0]), Line([x, -0.25, 0], [x, -0.36, 0]))
    pins.set_stroke(c, 2)
    mem = VGroup(*[Rectangle(width=0.5, height=0.2, color=c, fill_color=c, fill_opacity=0.35,
                             stroke_width=1.5).move_to([0.75, 0.55 - i * 0.3, 0]) for i in range(3)])
    tr = VGroup()
    for pts in ([[-0.05, 0.15, 0], [0.3, 0.15, 0], [0.3, 0.55, 0], [0.5, 0.55, 0]],
                [[-0.05, 0.0, 0], [0.4, 0.0, 0], [0.4, 0.25, 0], [0.5, 0.25, 0]],
                [[-0.4, -0.4, 0], [-0.4, -0.7, 0], [0.5, -0.7, 0]]):
        m = VMobject()
        m.set_points_as_corners(pts)
        m.set_stroke(c, width=1.5, opacity=0.6)
        tr.add(m)
    conn = VGroup(*[Rectangle(width=0.16, height=0.1, color=c, fill_color=c, fill_opacity=0.8,
                              stroke_width=0).move_to([w / 2 - 0.08, -0.55 + i * 0.22, 0]) for i in range(6)])
    leds = VGroup(*[Dot([-1.0 + i * 0.2, -0.78, 0], radius=0.05, color=C_OK) for i in range(3)])
    g = VGroup(base, cpu, pins, mem, tr, conn, leds)
    return g, leds


class BancoHardwareEnLaLazo(Pieza):
    def construct(self):
        y1 = 0.7
        obc, leds = placa_obc()
        obc.move_to(LEFT * 4.9)
        canal = RoundedRectangle(corner_radius=0.15, width=2.6, height=2.6, color=C_ANT,
                                 fill_color=C_ANT, fill_opacity=0.10, stroke_width=3)
        sim_box = RoundedRectangle(corner_radius=0.15, width=2.8, height=3.0, color=C_CIELO,
                                   fill_color=C_CIELO, fill_opacity=0.08, stroke_width=0)
        sim_box.move_to(RIGHT * 4.95)
        sim_borde = DashedVMobject(RoundedRectangle(corner_radius=0.15, width=2.8, height=3.0,
                                   color=C_CIELO, stroke_width=3), num_dashes=46).move_to(sim_box)
        elipse = Ellipse(width=1.6, height=1.3, color=C_CIELO, stroke_width=2, stroke_opacity=0.6).move_to(RIGHT * 5.08)
        mundo = Circle(radius=0.2, color=C_TIERRA, fill_color=C_TIERRA_2, fill_opacity=1,
                       stroke_width=2).move_to(elipse)
        gem = holograma(0.24, C_CIELO)
        gem_tr = ValueTracker(0)

        def orb(m):
            a = gem_tr.get_value()
            m.move_to(elipse.get_center() + np.array([0.8 * np.cos(a), 0.65 * np.sin(a), 0]))
        gem.add_updater(orb)
        orb(gem)

        onda = VMobject()
        wave_tr = ValueTracker(0)

        def w(m):
            x = np.linspace(-0.95, 0.95, 80)
            y = 0.32 * np.sin(2 * PI * x * 1.4 - wave_tr.get_value() * 6) * np.exp(-(x / 1.3) ** 2 * 0.3)
            m.set_points_as_corners(np.column_stack([x, y, np.zeros_like(x)]))
            m.set_stroke(C_ANT, width=3)
            m.set_fill(opacity=0)
        onda.add_updater(w)
        w(onda)

        l_obc = et("OBC", 26, C_SAT).next_to(obc, DOWN, buff=0.4)
        l_can = et("Canal", 26, C_ANT).next_to(canal, DOWN, buff=0.4)
        l_sim = et("Simulador", 26, C_CIELO).next_to(sim_box, DOWN, buff=0.4)

        arr = VGroup(
            flecha([-3.6, y1, 0], [-1.3, y1, 0], C_SAT), flecha([1.3, y1, 0], [3.55, y1, 0], C_SAT),
            flecha([3.55, -y1, 0], [1.3, -y1, 0], C_CIELO), flecha([-1.3, -y1, 0], [-3.6, -y1, 0], C_CIELO))

        path = VMobject()
        path.set_points_as_corners([[-3.6, y1, 0], [3.9, y1, 0], [3.9, -y1, 0], [-3.95, -y1, 0],
                                    [-3.95, y1, 0], [-3.6, y1, 0]])
        path.set_stroke(TENUE, width=2, opacity=0.35)
        tr = ValueTracker(0)
        dots = VGroup(*[Dot(radius=0.1) for _ in range(3)])
        for i, d in enumerate(dots):
            def f(m, off=i / 3):
                a = (tr.get_value() + off) % 1
                m.move_to(path.point_from_proportion(a))
                m.set_color(C_SAT if m.get_center()[1] > 0 else C_CIELO)
            d.add_updater(f)
            f(d)
        glow_o = RoundedRectangle(corner_radius=0.2, width=2.9, height=2.3, color=C_SAT).move_to(obc)
        glow_s = RoundedRectangle(corner_radius=0.2, width=3.1, height=3.3, color=C_CIELO).move_to(sim_box)

        def beat(pt):
            def f(m):
                s = sum(np.exp(-(np.linalg.norm(d.get_center() - pt) / 0.55) ** 2) for d in dots)
                s = min(1, s)
                m.set_stroke(width=2 + 6 * s, opacity=0.15 + 0.85 * s)
            return f
        glow_o.add_updater(beat(np.array([-3.7, 0, 0])))
        glow_s.add_updater(beat(np.array([3.7, 0, 0])))

        def led(m):
            t = tr.get_value() * 30
            for i, d in enumerate(m):
                d.set_fill(C_OK if np.sin(t + i * 2.1) > -0.2 else C_EJE, opacity=1)
        leds.add_updater(led)

        self.play(Create(obc, lag_ratio=0.08), run_time=2)
        self.play(Write(l_obc), run_time=0.5)
        self.play(FadeIn(sim_box), Create(sim_borde), run_time=1.2)
        self.play(Create(elipse), FadeIn(mundo), FadeIn(gem), Write(l_sim), run_time=1.2)
        self.add(gem_tr)
        gem.add_updater(lambda m: None)
        self.play(Create(canal), Write(l_can), run_time=1)
        self.play(FadeIn(onda), run_time=0.4)
        self.play(LaggedStart(*[GrowArrow(a) for a in arr], lag_ratio=0.3), Create(path), run_time=1.6)
        self.add(glow_o, glow_s)
        self.play(FadeIn(dots), run_time=0.5)
        self.play(tr.animate.set_value(3), gem_tr.animate.set_value(3 * TAU * 1.3),
                  wave_tr.animate.set_value(12), run_time=12, rate_func=linear)
        leds.clear_updaters()
        self.cierre()


# =================================================================== 2 ======
class GemeloDigitalSync(Pieza):
    def construct(self):
        tm, tc, TF = 4.0, 6.4, 13.5
        dt = 0.01
        ts = np.arange(0, TF + dt, dt)
        v1, v2, k = 0.2, 0.5, 0.7
        xr = np.zeros_like(ts)
        xg = np.zeros_like(ts)
        xr[0] = xg[0] = -5.2
        for i in range(1, len(ts)):
            t = ts[i - 1]
            xr[i] = xr[i - 1] + (v1 if t < tm else v2) * dt
            vg = v1 if t < tc else v2 + k * (xr[i - 1] - xg[i - 1])
            xg[i] = xg[i - 1] + vg * dt
        err = xr - xg
        yr, yg = 2.0, -0.9
        T = ValueTracker(0)
        Xr = lambda: np.interp(T.get_value(), ts, xr)
        Xg = lambda: np.interp(T.get_value(), ts, xg)

        # pistas
        pista_r = DashedLine([-6.0, yr, 0], [0.5, yr, 0], color=C_EJE, stroke_width=2, dash_length=0.1)
        pista_g = DashedLine([-6.0, yg, 0], [0.5, yg, 0], color=C_EJE, stroke_width=2, dash_length=0.1)
        real = satelite(0.42, C_SAT)
        gem = holograma(0.42, C_CIELO)
        real.add_updater(lambda m: m.move_to([Xr(), yr, 0]))
        gem.add_updater(lambda m: m.move_to([Xg(), yg, 0]))
        real.move_to([xr[0], yr, 0])
        gem.move_to([xg[0], yg, 0])
        l_real = et("Real", 26, C_SAT).move_to([-5.8, yr + 0.85, 0])
        l_gem = et("Gemelo", 26, C_CIELO).move_to([-5.6, yg + 0.85, 0])

        # llama del propulsor
        llama = Polygon([0, 0.09, 0], [-0.5, 0, 0], [0, -0.09, 0], color=C_MAL, fill_color=C_MAL,
                        fill_opacity=0.9, stroke_width=0)

        def fl(m):
            t = T.get_value()
            o = float(suave((t - tm) / 0.15) * (1 - suave((t - tm - 1.6) / 0.8)))
            m.set_fill(opacity=o)
            m.move_to([Xr() - 1.05 - 0.25 * o, yr, 0])
        llama.add_updater(fl)
        fl(llama)

        # enlace de telemetría
        enlace = DashedLine([0, 0, 0], [0, -1, 0], color=C_ANT, stroke_width=2, stroke_opacity=0.6)

        def en(m):
            a = np.array([Xr(), yr - 0.5, 0])
            b = np.array([Xg(), yg + 0.5, 0])
            m.become(DashedLine(a, b, color=C_ANT, stroke_width=2, stroke_opacity=0.55, dash_length=0.1))
        enlace.add_updater(en)
        en(enlace)
        pul = Dot(radius=0.1, color=C_ANT)

        def pu(m):
            t = T.get_value()
            a = np.array([Xr(), yr - 0.5, 0])
            b = np.array([Xg(), yg + 0.5, 0])
            f = (t * 0.8) % 1
            m.move_to(a + (b - a) * f)
            m.set_fill(C_OK if t > tc else C_ANT)
            m.set_opacity(min(1, T.get_value() * 3))
        pul.add_updater(pu)
        pu(pul)

        # marcas de error en la pista del gemelo
        barra = Line(ORIGIN, RIGHT, color=C_MAL, stroke_width=6)
        fantasma = DashedLine([0, 0, 0], [0, -1, 0], color=C_MAL, stroke_width=2, stroke_opacity=0.6)

        def ba(m):
            a, b = Xg(), Xr()
            e = abs(b - a)
            o = float(suave(e / 0.05))
            col = C_MAL if T.get_value() < tc + 0.6 else interpolate_color(ManimColor(C_MAL), ManimColor(C_OK), suave((T.get_value() - tc - 0.6) / 3))
            m.put_start_and_end_on([a, yg - 0.75, 0], [b + 1e-4, yg - 0.75, 0])
            m.set_stroke(col, width=6, opacity=o)
        barra.add_updater(ba)
        ba(barra)

        def fa(m):
            e = abs(Xr() - Xg())
            m.become(DashedLine([Xr(), yr - 0.5, 0], [Xr(), yg - 0.75, 0], color=C_MAL, stroke_width=2,
                                stroke_opacity=0.55 * float(suave(e / 0.05)), dash_length=0.1))
        fantasma.add_updater(fa)
        fa(fantasma)

        # onda de corrección
        anillo = Circle(radius=0.3, color=C_OK, stroke_width=4)

        def an(m):
            u = (T.get_value() - tc) / 1.0
            o = float(suave(u * 8) * (1 - suave(u))) if 0 <= u <= 1 else 0
            m.become(Circle(radius=0.4 + 0.9 * suave(u), color=C_OK, stroke_width=4, stroke_opacity=o).move_to([Xg(), yg, 0]))
        anillo.add_updater(an)
        an(anillo)

        # gráfica de error
        ox, oy, ax_w, esc = 2.3, -2.5, 4.3, 4.4
        ejex = Arrow([ox, oy, 0], [ox + ax_w + 0.3, oy, 0], buff=0, color=TENUE, stroke_width=3, tip_length=0.15)
        ejey = Arrow([ox, oy, 0], [ox, oy + 5.0, 0], buff=0, color=TENUE, stroke_width=3, tip_length=0.15)
        l_err = et("Error", 24, TINTA).next_to(ejey, UP, buff=0.12)
        l_t = et("Tiempo", 22, TENUE).next_to(ejex, DOWN, buff=0.12, aligned_edge=RIGHT)
        cero = DashedLine([ox, oy, 0], [ox + ax_w, oy, 0], color=C_OK, stroke_width=1.5, stroke_opacity=0.4)
        gx = lambda t: ox + ax_w * t / TF
        gy = lambda e: oy + esc * e
        curva_a = VMobject()
        curva_b = VMobject()
        punta = Dot(radius=0.09, color=C_MAL)

        def cur(m, lo, hi, col):
            t = T.get_value()
            mask = (ts >= lo) & (ts <= min(hi, t))
            if mask.sum() < 2:
                m.set_points([ORIGIN]); m.set_stroke(opacity=0); return
            xs = gx(ts[mask]); ys = gy(np.abs(err[mask]))
            m.set_points_as_corners(np.column_stack([xs, ys, np.zeros_like(xs)]))
            m.set_stroke(col, width=4, opacity=1); m.set_fill(opacity=0)
        curva_a.add_updater(lambda m: cur(m, 0, tc, C_MAL))
        curva_b.add_updater(lambda m: cur(m, tc, TF, C_OK))

        def pt(m):
            t = min(T.get_value(), TF)
            e = abs(np.interp(t, ts, err))
            m.move_to([gx(t), gy(e), 0])
            m.set_fill(C_MAL if t < tc else C_OK)
            m.set_opacity(min(1, t * 3))
        punta.add_updater(pt)
        pt(punta)

        self.play(Create(pista_r), FadeIn(real, scale=0.6), Write(l_real), run_time=1.2)
        self.play(Create(pista_g), FadeIn(gem, scale=0.6), Write(l_gem), run_time=1.2)
        self.play(FadeIn(enlace), FadeIn(pul), run_time=0.6)
        self.play(Create(ejex), Create(ejey), Write(l_err), Write(l_t), FadeIn(cero), run_time=1.2)
        self.add(llama, barra, fantasma, anillo, curva_a, curva_b, punta)
        self.play(T.animate.set_value(TF), run_time=TF, rate_func=linear)
        for m in (real, gem, llama, enlace, pul, barra, fantasma, anillo, curva_a, curva_b, punta):
            m.clear_updaters()
        self.cierre()


# =================================================================== 3 ======
class EmuladorCanal(Pieza):
    def construct(self):
        tt = np.linspace(0, 1, 260)
        rng = np.random.default_rng(7)
        ruido = rng.normal(0, 1, tt.size)

        def rafaga(c=0.3, f=7, a=1.0, sig=0.0):
            env = np.exp(-((tt - c) / 0.11) ** 2)
            y = a * env * np.sin(2 * PI * f * (tt - c))
            return y + sig * ruido

        formas = [rafaga(), rafaga(c=0.62), rafaga(c=0.62, f=10.5),
                  rafaga(c=0.62, f=10.5, a=0.4), rafaga(c=0.62, f=10.5, a=0.4, sig=0.13)]
        colores = [C_OK, C_ANT, C_ANT, C_ANT, C_MAL]
        xs_c = [-5.4 + 2.7 * i for i in range(5)]
        yc = -1.0
        sw, sh = 2.1, 2.1
        scopes = VGroup()
        ondas = []
        refs = []
        for i, xc in enumerate(xs_c):
            r = RoundedRectangle(corner_radius=0.1, width=sw, height=sh, color=C_EJE, stroke_width=2.5,
                                 fill_color=C_PANEL, fill_opacity=0.55).move_to([xc, yc, 0])
            eje = Line([xc - sw / 2 + 0.08, yc, 0], [xc + sw / 2 - 0.08, yc, 0], color=C_EJE, stroke_width=1.5, stroke_opacity=0.7)
            scopes.add(VGroup(r, eje))
            X = xc - sw / 2 + 0.12 + (sw - 0.24) * tt
            ondas.append(trazo(X, yc + 0.78 * formas[i], colores[i], 3))
            refs.append(trazo(X, yc + 0.78 * formas[0], TENUE, 1.5, 0.35))
        flechas = VGroup(*[flecha([xs_c[i] + sw / 2 + 0.05, yc, 0], [xs_c[i + 1] - sw / 2 - 0.05, yc, 0], TENUE, 3, 0.14)
                           for i in range(4)])

        bloques = []
        trs = []
        nombres = ["Retardo", "Doppler", "Atenuación", "Ruido"]
        valores = [(1.8, "ms", 1), (300, "kHz", 0), (169, "dB", 0), (5, "dB", 0)]
        tipos = ["slider", "perilla", "perilla", "slider"]
        for i in range(4):
            cx = (xs_c[i] + xs_c[i + 1]) / 2
            cy = 1.95
            caja_b = RoundedRectangle(corner_radius=0.14, width=2.45, height=1.55, color=C_ANT,
                                      fill_color=C_ANT, fill_opacity=0.10, stroke_width=2.5).move_to([cx, cy, 0])
            nom = et(nombres[i], 22, TINTA).move_to([cx, cy + 0.42, 0])
            tr = ValueTracker(0)
            trs.append(tr)
            ctl = VGroup()
            px, py = cx - 0.75, cy - 0.28
            if tipos[i] == "perilla":
                cir = Circle(radius=0.24, color=C_ANT, stroke_width=3, fill_color=C_PANEL, fill_opacity=1).move_to([px, py, 0])
                marca = Line(ORIGIN, UP * 0.2, color=C_SAT, stroke_width=4).move_to([px, py + 0.1, 0])
                marca.move_to([px, py, 0], aligned_edge=DOWN)

                def rot(m, tr=tr, px=px, py=py):
                    m.become(Line([px, py, 0], [px, py + 0.2, 0], color=C_SAT, stroke_width=4)
                             .rotate(-(-2.2 + 4.4 * tr.get_value()) * -1 * -1 + 0, about_point=[px, py, 0]))
                marca.add_updater(rot)
                rot(marca)
                ctl.add(cir, marca)
            else:
                pista = Line([px - 0.3, py, 0], [px + 0.3, py, 0], color=C_EJE, stroke_width=5)
                pom = Dot(radius=0.11, color=C_SAT)
                pom.add_updater(lambda m, tr=tr, px=px, py=py: m.move_to([px - 0.3 + 0.6 * tr.get_value(), py, 0]))
                pom.move_to([px - 0.3, py, 0])
                ctl.add(pista, pom)
            v, u, d = valores[i]
            cv = cifra_viva(lambda tr=tr, v=v: v * tr.get_value(), u, 22, C_SAT, d,
                            centro=[cx + 0.15, py - 0.02, 0], borde=LEFT)
            cv.move_to([cx + 0.02, py, 0], aligned_edge=LEFT)
            bloques.append(VGroup(caja_b, nom, ctl, cv))
        conex = VGroup(*[DashedLine([(xs_c[i] + xs_c[i + 1]) / 2, 1.15, 0], [(xs_c[i] + xs_c[i + 1]) / 2, yc + 0.2, 0],
                                    color=C_ANT, stroke_width=2, dash_length=0.1) for i in range(4)])
        l0 = et("Limpia", 22, C_OK).next_to(scopes[0], DOWN, buff=0.25)
        l4 = et("Degradada", 22, C_MAL).next_to(scopes[4], DOWN, buff=0.25)

        self.play(LaggedStart(*[FadeIn(s) for s in scopes], lag_ratio=0.15), run_time=1.8)
        self.play(Create(ondas[0]), Write(l0), run_time=1.4)
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.2) for b in bloques], lag_ratio=0.2),
                  Create(conex), Create(flechas), run_time=1.8)
        self.wait(0.4)
        for i in range(4):
            self.add(refs[i + 1])
            self.play(Indicate(bloques[i][0], color=C_SAT, scale_factor=1.05),
                      run_time=0.6)
            self.play(trs[i].animate.set_value(1), TransformFromCopy(ondas[i], ondas[i + 1]),
                      run_time=2.2, rate_func=smooth)
            if i == 3:
                self.play(Write(l4), run_time=0.5)
            else:
                self.wait(0.2)
        self.cierre()


# =================================================================== 4 ======
_KT = [0, 4.5, 6, 12.5, 14, 19]
_KV = [20, 120, 120, -150, -150, 120]


def temp_termo(t):
    t = min(max(t, 0), _KT[-1] - 1e-6)
    i = max(j for j in range(len(_KT) - 1) if t >= _KT[j])
    f = (t - _KT[i]) / (_KT[i + 1] - _KT[i])
    return _KV[i] + (_KV[i + 1] - _KV[i]) * (0.5 - 0.5 * np.cos(np.pi * f))


class CamaraTermoVacio(Pieza):
    def construct(self):
        cc = np.array([-3.2, -0.2, 0])
        TF = _KT[-1]
        T = ValueTracker(0)
        on = lambda: float(np.clip(1 - suave((T.get_value() - 6) / 0.7) + suave((T.get_value() - 13.7) / 0.7), 0, 1))
        frio = lambda: float(suave((T.get_value() - 6.3) / 1.0) * (1 - suave((T.get_value() - 13.7) / 0.7)))
        temp = lambda: temp_termo(T.get_value())
        frac = lambda: (temp() + 150) / 270
        col_t = lambda: interpolate_color(ManimColor(C_ANT), ManimColor(C_MAL), frac())

        camara = RoundedRectangle(corner_radius=0.35, width=7.2, height=5.6, color=TENUE, stroke_width=5,
                                  fill_color=C_PANEL, fill_opacity=0.35).move_to(cc)
        interior = RoundedRectangle(corner_radius=0.25, width=6.9, height=5.3, color=C_EJE, stroke_width=1.5).move_to(cc)
        sat = satelite(0.7, C_SAT).move_to(cc)
        halo = Circle(radius=1.35, stroke_width=0, fill_opacity=0.3).move_to(cc)
        halo.add_updater(lambda m: m.set_fill(col_t(), opacity=0.10 + 0.30 * abs(2 * frac() - 1) ** 0.8))

        # lámparas
        lamparas = VGroup()
        ys = [cc[1] + 1.5, cc[1], cc[1] - 1.5]
        for y in ys:
            refl = Polygon([-6.7, y + 0.16, 0], [-6.2, y + 0.5, 0], [-6.2, y - 0.5, 0], [-6.7, y - 0.16, 0],
                           color=C_SAT, stroke_width=3, fill_color=C_SAT, fill_opacity=0.25)
            bulbo = Dot([-6.45, y, 0], radius=0.11, color=C_SAT)
            lamparas.add(VGroup(refl, bulbo))
        halos_l = VGroup(*[Circle(radius=0.55, stroke_width=0, fill_color=C_SAT, fill_opacity=0.0).move_to([-6.2, y, 0]) for y in ys])
        for h in halos_l:
            h.add_updater(lambda m: m.set_fill(C_SAT, opacity=0.35 * on()))
        haces = VGroup(*[Polygon([-6.2, y + 0.45, 0], [-4.7, y * 0.35 + cc[1] * 0.65 + 0.5, 0],
                                 [-4.7, y * 0.35 + cc[1] * 0.65 - 0.5, 0], [-6.2, y - 0.45, 0],
                                 stroke_width=0, fill_color=C_SAT, fill_opacity=0) for y in ys])
        for h in haces:
            h.add_updater(lambda m: m.set_fill(C_SAT, opacity=0.13 * on()))
        ondas_c = VGroup(*[VMobject() for _ in range(6)])
        for k, m in enumerate(ondas_c):
            y0 = ys[k // 2] + (0.2 if k % 2 == 0 else -0.2)
            yt = y0 * 0.4 + cc[1] * 0.6

            def f(m, y0=y0, yt=yt):
                x = np.linspace(-6.0, -4.75, 60)
                a = (x - x[0]) / (x[-1] - x[0])
                y = y0 + (yt - y0) * a + 0.07 * np.sin(2 * PI * (x * 2.4) - T.get_value() * 9)
                m.set_points_as_corners(np.column_stack([x, y, np.zeros_like(x)]))
                m.set_stroke(C_SAT, width=3, opacity=0.9 * on())
                m.set_fill(opacity=0)
            m.add_updater(f)
            f(m)

        # panel frío
        panel = Rectangle(width=0.32, height=4.7, color=C_ANT, stroke_width=3, fill_color=C_ANT, fill_opacity=0.3).move_to([-0.3, cc[1], 0])
        escarcha = VGroup(*[Line([-0.3 - 0.16, cc[1] - 2.2 + i * 0.4, 0], [-0.3 + 0.16, cc[1] - 2.0 + i * 0.4, 0],
                                 color=C_ANT, stroke_width=1.5, stroke_opacity=0.6) for i in range(11)])
        panel.add_updater(lambda m: m.set_fill(C_ANT, opacity=0.10 + 0.5 * frio()))
        escarcha.add_updater(lambda m: m.set_stroke(opacity=0.15 + 0.7 * frio()))
        anillos = VGroup(*[VMobject() for _ in range(4)])
        for k, m in enumerate(anillos):
            def f(m, k=k):
                u = (T.get_value() * 0.45 + k / 4) % 1
                r = 1.55 + 1.3 * u
                a = Arc(radius=r, start_angle=-38 * DEGREES, angle=76 * DEGREES, arc_center=cc)
                m.become(a)
                m.set_stroke(interpolate_color(ManimColor(C_MAL), ManimColor(C_ANT), frio()), width=3.5,
                             opacity=(0.15 + 0.85 * frio()) * (1 - u) ** 1.2 * float(suave(u * 6)))
            m.add_updater(f)
            f(m)

        l_lamp = et("Lámparas solares", 22, C_SAT).move_to([-5.15, -3.45, 0])
        l_pan = et("Panel frío", 22, C_ANT).move_to([-0.75, -3.45, 0])
        l_vac = et("Vacío", 20, TENUE).move_to([cc[0], 2.2, 0])

        # termómetro y curva
        y0, y1 = -2.55, 2.15
        tubo = RoundedRectangle(corner_radius=0.2, width=0.44, height=5.0, color=TENUE, stroke_width=3).move_to([1.35, -0.1, 0])
        bulbo = Circle(radius=0.42, color=TENUE, stroke_width=3).move_to([1.35, -3.0, 0])
        nivel = Rectangle(width=0.24, height=0.1, stroke_width=0, fill_opacity=1)
        bulbo_f = Circle(radius=0.33, stroke_width=0, fill_opacity=1).move_to(bulbo)

        def niv(m):
            h = 0.05 + (y1 - y0) * frac()
            m.become(Rectangle(width=0.24, height=h, stroke_width=0, fill_color=col_t(), fill_opacity=1)
                     .move_to([1.35, y0 + h / 2 - 0.3, 0]))
            bulbo_f.set_fill(col_t(), opacity=1)
        nivel.add_updater(niv)
        niv(nivel)
        l_hot = et("+120 °C", 22, C_MAL).move_to([2.35, y1, 0])
        l_cold = et("−150 °C", 22, C_ANT).move_to([2.35, y0, 0])
        g_hot = DashedLine([1.75, y1, 0], [6.8, y1, 0], color=C_MAL, stroke_width=1.5, stroke_opacity=0.4)
        g_cold = DashedLine([1.75, y0, 0], [6.8, y0, 0], color=C_ANT, stroke_width=1.5, stroke_opacity=0.4)
        ox, wx = 3.2, 3.6
        ejey = Line([ox, -2.75, 0], [ox, 2.4, 0], color=TENUE, stroke_width=2)
        curva = VMobject()
        punta = Dot(radius=0.11)
        ts = np.linspace(0, TF, 300)
        Ts = np.array([temp_termo(t) for t in ts])
        gy = lambda v: y0 + (y1 - y0) * (v + 150) / 270

        def cur(m):
            t = T.get_value()
            k = int(np.searchsorted(ts, t)) + 1
            k = max(2, min(k, len(ts)))
            xs = ox + wx * ts[:k] / TF
            ys_ = gy(Ts[:k])
            m.set_points_as_corners(np.column_stack([xs, ys_, np.zeros_like(xs)]))
            m.set_stroke(col_t(), width=4)
            m.set_fill(opacity=0)
            punta.move_to([xs[-1], ys_[-1], 0]).set_fill(col_t(), opacity=1)
        curva.add_updater(cur)
        cur(curva)
        lect = cifra_viva(lambda: temp(), "°C", 46, None, 0, centro=[4.7, 3.15, 0])
        lect.add_updater(lambda m: m[0].set_color(col_t()))

        self.play(Create(camara), Create(interior), run_time=1.5)
        self.play(FadeIn(sat, scale=0.7), FadeIn(halo), Write(l_vac), run_time=1.2)
        self.play(FadeIn(lamparas, shift=RIGHT * 0.3), FadeIn(panel), FadeIn(escarcha),
                  Write(l_lamp), Write(l_pan), run_time=1.5)
        self.add(halos_l, haces, ondas_c, anillos)
        self.play(Create(tubo), Create(bulbo), Create(ejey), FadeIn(g_hot), FadeIn(g_cold),
                  Write(l_hot), Write(l_cold), run_time=1.5)
        self.add(nivel, bulbo_f, curva, punta, lect)
        self.play(T.animate.set_value(TF), run_time=TF, rate_func=linear)
        self.add(T)
        for m in (halo, halos_l, haces, ondas_c, panel, escarcha, anillos, nivel, curva, lect):
            m.clear_updaters()
        self.cierre()


# =================================================================== 5 ======
class MesaVibracion(Pieza):
    def construct(self):
        fn = 120.0
        a_tab = 0.045
        st = {"z": 0.05, "D": 9.0, "m": 1}
        s = ValueTracker(0)
        Tr = lambda f, z: np.sqrt(1 + (2 * z * f / fn) ** 2) / np.sqrt((1 - (f / fn) ** 2) ** 2 + (2 * z * f / fn) ** 2)
        ph = lambda f, z: np.arctan2(2 * z * (f / fn) ** 3, 1 - (f / fn) ** 2 + (2 * z * f / fn) ** 2)
        F = lambda x: 20 * 100 ** x
        fase = lambda: 2 * PI * st["D"] * (1.0 * s.get_value() + 2.25 * s.get_value() ** 2)
        y_tab = lambda: a_tab * np.sin(fase())
        y_sat = lambda: a_tab * Tr(F(s.get_value()), st["z"]) * np.sin(fase() - ph(F(s.get_value()), st["z"]))
        s_pk = np.log(fn / 20) / np.log(100)

        xc = -3.6
        cuerpo = Rectangle(width=3.4, height=1.6, color=TENUE, stroke_width=3, fill_color=C_EJE, fill_opacity=0.55).move_to([xc, -2.8, 0])
        bobinas = VGroup(*[Line([xc - 1.5, -2.8 + d, 0], [xc + 1.5, -2.8 + d, 0], color=TENUE, stroke_width=1.5, stroke_opacity=0.6)
                           for d in (-0.4, 0, 0.4)])
        mesa_r = Rectangle(width=3.0, height=0.28, color=C_ANT, stroke_width=3, fill_color=C_ANT, fill_opacity=0.5)
        adap = VGroup(*[Rectangle(width=0.5, height=0.25, color=C_ANT, stroke_width=2, fill_color=C_ANT, fill_opacity=0.5)
                        .move_to([dx, 0.265, 0]) for dx in (-0.7, 0.7)])
        mesa = VGroup(mesa_r, adap).move_to([xc, -1.86, 0])   # cara inferior en -2.0
        mesa_rest = mesa.get_center().copy()

        cuerpo_s = Rectangle(width=1.2, height=1.7, color=C_SAT, stroke_width=3, fill_color=C_SAT, fill_opacity=0.85)
        mastil = Line(UP * 0.85, UP * 1.7, color=C_SAT, stroke_width=3)
        plato = Arc(radius=0.25, start_angle=200 * DEGREES, angle=140 * DEGREES, color=C_SAT, stroke_width=4).move_to(UP * 1.75)
        alas = VGroup(*[Rectangle(width=1.05, height=0.62, color=C_SAT, stroke_width=2, fill_color=C_CIELO, fill_opacity=0.55)
                        .move_to([sg * 1.2, 0.05, 0]) for sg in (-1, 1)])
        uniones = VGroup(*[Line([sg * 0.6, 0.05, 0], [sg * 0.67, 0.05, 0], color=C_SAT, stroke_width=3) for sg in (-1, 1)])
        sat = VGroup(alas, uniones, cuerpo_s, mastil, plato).move_to([xc, 0.05 + 0.2, 0])
        sat_rest = sat.get_center().copy()
        fantasmas = VGroup(*[sat.copy().set_opacity(0.0) for _ in range(2)])

        def m_upd(m):
            m.move_to(mesa_rest + [0, y_tab(), 0])
        mesa.add_updater(m_upd)
        col_s = lambda: interpolate_color(ManimColor(C_SAT), ManimColor(C_MAL),
                                          float(np.clip((abs(y_sat()) / a_tab - 2.5) / 5.0, 0, 1)) if False else
                                          float(np.clip((Tr(F(s.get_value()), st["z"]) - 3) / 5.0, 0, 1)))

        def s_upd(m):
            m.move_to(sat_rest + [0, y_sat(), 0])
            cuerpo_s.set_fill(col_s(), opacity=0.85).set_stroke(col_s())
        sat.add_updater(s_upd)

        def g_upd(m):
            a = a_tab * Tr(F(s.get_value()), st["z"])
            for i, g in enumerate(m):
                g.move_to(sat_rest + [0, (1 if i == 0 else -1) * a * 1.0, 0])
                g.set_opacity(min(0.16, a * 0.9))
        fantasmas.add_updater(g_upd)
        ref = DashedLine([xc - 2.4, sat_rest[1], 0], [xc + 2.4, sat_rest[1], 0], color=TENUE, stroke_width=1, stroke_opacity=0.3, dash_length=0.1)

        muelles = VGroup(*[VMobject() for _ in range(2)])
        col_mu = {"c": TENUE}

        def mu(m, dx):
            p0 = mesa[1][0 if dx < 0 else 1].get_top()
            p1 = np.array([xc + dx, sat.get_center()[1] - 1.0 - 0.15 + 0.0, 0])
            p1[1] = cuerpo_s.get_bottom()[1]
            r = resorte(p0, p1, 5, 0.13, col_mu["c"], 3)
            m.become(r)
        for m, dx in zip(muelles, (-0.7, 0.7)):
            m.add_updater(lambda mm, dx=dx: mu(mm, dx))
        amort = VGroup(Rectangle(width=0.28, height=0.28, color=C_OK, stroke_width=3, fill_color=C_OK, fill_opacity=0.4),
                       Line(ORIGIN, UP * 0.3, color=C_OK, stroke_width=4))
        amort.set_opacity(0)

        def am(m):
            b = np.array([xc, mesa[0].get_top()[1] + 0.22, 0])
            t = np.array([xc, cuerpo_s.get_bottom()[1], 0])
            m[0].move_to(b)
            m[1].put_start_and_end_on(b + UP * 0.14, t)
        amort.add_updater(am)

        # gráfica
        ox, oy, wx, esc = 0.9, -3.0, 5.7, 0.5
        ejex = Arrow([ox, oy, 0], [ox + wx + 0.3, oy, 0], buff=0, color=TENUE, stroke_width=3, tip_length=0.15)
        ejey = Arrow([ox, oy, 0], [ox, oy + 5.6, 0], buff=0, color=TENUE, stroke_width=3, tip_length=0.15)
        l_f = et("Frecuencia", 22, TENUE).next_to(ejex, DOWN, buff=0.1, aligned_edge=RIGHT)
        l_r = et("Respuesta", 22, TINTA).next_to(ejey, UP, buff=0.1).shift(RIGHT * 0.6)
        base1 = DashedLine([ox, oy + esc, 0], [ox + wx, oy + esc, 0], color=C_EJE, stroke_width=1.5, dash_length=0.1)
        N = 300
        xs_ = np.linspace(0, 1, N)
        pts = {1: (ox + wx * xs_, oy + esc * Tr(F(xs_), 0.05)), 2: (ox + wx * xs_, oy + esc * Tr(F(xs_), 0.25))}

        def curva(mode, col):
            m = VMobject()

            def f(mm):
                cur = st["m"]
                if cur == mode:
                    k = int(s.get_value() * N)
                    op = 1
                elif cur > mode:
                    k, op = N, 0.35
                else:
                    k, op = 0, 0
                if k < 2:
                    mm.set_points_as_corners([ORIGIN, ORIGIN + RIGHT * 1e-3]); mm.set_stroke(col, opacity=0); return
                X, Y = pts[mode]
                mm.set_points_as_corners(np.column_stack([X[:k], Y[:k], np.zeros(k)]))
                mm.set_stroke(col, width=4, opacity=op); mm.set_fill(opacity=0)
            m.add_updater(f)
            return m
        c1, c2 = curva(1, C_MAL), curva(2, C_OK)
        pk_x = ox + wx * s_pk
        pk_y = oy + esc * Tr(fn, 0.05)
        marca = VGroup(Dot([pk_x, pk_y, 0], radius=0.13, color=C_MAL),
                       DashedLine([pk_x, oy, 0], [pk_x, pk_y, 0], color=C_MAL, stroke_width=2, dash_length=0.1))
        l_res = et("Resonancia", 26, C_MAL).next_to(marca[0], RIGHT, buff=0.3)
        marca.add_updater(lambda m: m.set_opacity(float(suave((s.get_value() - s_pk) / 0.02)) if st["m"] == 1 else 0.4))
        l_res.add_updater(lambda m: m.set_opacity(float(suave((s.get_value() - s_pk) / 0.02)) if st["m"] == 1 else 0.0))
        cursor = Dot(radius=0.1)

        def cu(m):
            x = s.get_value()
            z = st["z"]
            m.move_to([ox + wx * x, oy + esc * Tr(F(x), z), 0])
            m.set_fill(C_MAL if st["m"] == 1 else C_OK, opacity=min(1, x * 10))
        cursor.add_updater(cu)
        hz = cifra_viva(lambda: F(s.get_value()), "Hz", 34, C_ANT, 0, centro=[6.6, 3.4, 0], borde=RIGHT)

        self.play(Create(cuerpo), Create(bobinas), run_time=1.2)
        self.play(FadeIn(mesa, shift=DOWN * 0.3), run_time=0.8)
        self.play(FadeIn(sat, shift=DOWN * 0.3), Create(ref), run_time=1.0)
        self.add(muelles, fantasmas)
        self.wait(0.5)
        self.play(Create(ejex), Create(ejey), Write(l_f), Write(l_r), FadeIn(base1), run_time=1.2)
        self.add(c1, c2, marca, l_res, cursor, hz)
        self.play(s.animate.set_value(1), run_time=9, rate_func=linear)
        self.wait(0.8)
        # amortiguador
        am(amort)
        self.play(amort.animate.set_opacity(1), run_time=0.8)
        col_mu["c"] = C_OK
        self.wait(0.4)
        st.update(z=0.25, D=6.0, m=2)
        s.set_value(0)
        self.play(s.animate.set_value(1), run_time=6, rate_func=linear)
        for m in (mesa, sat, fantasmas, muelles, amort, c1, c2, marca, l_res, cursor, hz):
            m.clear_updaters()
        self.cierre()


# =================================================================== 6 ======
U = 0.72
C30 = np.sqrt(3) / 2


def iso(x, y, z):
    return np.array([(x - y) * C30 * U, (-(x + y) * 0.5 + z) * U, 0.0])


def cara(pts, col, op=0.95, ancho=1.6, borde=None):
    return Polygon(*[iso(*p) for p in pts], stroke_color=borde or col, stroke_width=ancho,
                   fill_color=col, fill_opacity=op)


def caja_iso(x0, x1, y0, y1, z0, z1, c, op=0.95):
    top = [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    der = [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]
    izq = [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]
    cd = interpolate_color(ManimColor(c), ManimColor(SOMBRA), 0.30)
    ci = interpolate_color(ManimColor(c), ManimColor(SOMBRA), 0.50)
    return VGroup(cara(izq, ci, op, borde=c), cara(der, cd, op, borde=c), cara(top, c, op, borde=c))


def linea_iso(a, b, col, ancho=3, op=1.0):
    return Line(iso(*a), iso(*b), color=col, stroke_width=ancho, stroke_opacity=op)


class CubeSatDespiece(Pieza):
    def construct(self):
        O_asm = np.array([0, -1.2, 0])
        O_exp = np.array([0, -3.0, 0])

        # estructura (marco 3U)
        h = 3.0
        rieles_f = VGroup(*[linea_iso((x, y, 0), (x, y, h), TENUE, 4) for x, y in ((.5, .5), (.5, -.5), (-.5, .5))])
        aros = VGroup(*[linea_iso(a, b, TENUE, 2.5, 0.8) for z in (1, 2)
                        for a, b in (((.5, -.5, z), (.5, .5, z)), ((-.5, .5, z), (.5, .5, z)))])
        base_f = VGroup(linea_iso((.5, -.5, 0), (.5, .5, 0), TENUE, 4), linea_iso((-.5, .5, 0), (.5, .5, 0), TENUE, 4))
        tapa = VGroup(*[linea_iso(a, b, TENUE, 4) for a, b in
                        (((-.5, -.5, h), (.5, -.5, h)), ((.5, -.5, h), (.5, .5, h)),
                         ((.5, .5, h), (-.5, .5, h)), ((-.5, .5, h), (-.5, -.5, h)))])
        rieles_b = VGroup(linea_iso((-.5, -.5, 0), (-.5, -.5, h), TENUE, 2, 0.35),
                          linea_iso((-.5, -.5, 0), (.5, -.5, 0), TENUE, 2, 0.35),
                          linea_iso((-.5, -.5, 0), (-.5, .5, 0), TENUE, 2, 0.35))
        marco_b = rieles_b.set_z_index(0)
        marco_f = VGroup(rieles_f, aros, base_f, tapa).set_z_index(3)
        estructura = VGroup(marco_b, marco_f)

        # paneles solares
        def panel(cara_pts, filas=8, cols=3, fijo=None):
            (a, b, c_, d) = cara_pts
            g = VGroup(cara(cara_pts, C_CIELO, 1.0, 2.2))
            for i in range(1, cols):
                f = i / cols
                p0 = tuple(a[k] + (b[k] - a[k]) * f for k in range(3))
                p1 = tuple(d[k] + (c_[k] - d[k]) * f for k in range(3))
                g.add(linea_iso(p0, p1, SOMBRA, 1.5, 0.55))
            for j in range(1, filas):
                f = j / filas
                p0 = tuple(a[k] + (d[k] - a[k]) * f for k in range(3))
                p1 = tuple(b[k] + (c_[k] - b[k]) * f for k in range(3))
                g.add(linea_iso(p0, p1, SOMBRA, 1.5, 0.55))
            return g.set_z_index(4)
        pan_r = panel([(0.5, -.5, .08), (0.5, .5, .08), (0.5, .5, 2.92), (0.5, -.5, 2.92)])
        pan_l = panel([(-.5, 0.5, .08), (.5, 0.5, .08), (.5, 0.5, 2.92), (-.5, 0.5, 2.92)])

        # electrónica
        bateria = caja_iso(-.4, .4, -.4, .4, 0.1, 0.6, C_SAT)
        for i in range(1, 4):
            x = -.4 + 0.8 * i / 4
            bateria.add(linea_iso((x, -.4, .6), (x, .4, .6), SOMBRA, 1.5, 0.6))
        obc = caja_iso(-.44, .44, -.44, .44, 1.1, 1.2, C_OK)
        obc.add(caja_iso(-.25, .05, -.25, .05, 1.2, 1.28, TINTA, 0.9), caja_iso(.15, .35, -.05, .3, 1.2, 1.25, TINTA, 0.7))
        radio = caja_iso(-.44, .44, -.44, .44, 1.6, 1.7, C_ANT)
        radio.add(caja_iso(-.3, .3, -.3, .0, 1.7, 1.85, TENUE, 0.9))
        camara = caja_iso(-.3, .3, -.3, .3, 2.05, 2.75, TENUE)
        lente = Ellipse(width=2 * 1.2247 * 0.19 * U, height=2 * 0.7071 * 0.19 * U, color=C_CIELO, stroke_width=3,
                        fill_color=SOMBRA, fill_opacity=1).move_to(iso(0, 0, 2.76))
        camara.add(lente)
        placa_a = caja_iso(-.15, .15, -.15, .15, 3.0, 3.05, C_ANT)
        antena = VGroup(placa_a, linea_iso((0, 0, 3.05), (0, 0, 3.9), C_ANT, 3.5),
                        Dot(iso(0, 0, 3.9), radius=0.06, color=C_ANT))
        internos = [(bateria, 0.1, -0.1, "Batería"), (obc, 1.1, 0.6, "OBC"), (radio, 1.6, 1.2, "Radio"),
                    (camara, 2.05, 1.85, "Cámara"), (antena, 3.0, 2.85, "Antena")]

        todo = VGroup(estructura, pan_r, pan_l, *[g for g, *_ in internos])
        todo.shift(O_asm)
        for g, *_ in internos:
            g.set_z_index(1)

        # vectores de explosión
        d_marco = O_exp - O_asm
        d_int = []
        for g, z0, B, _ in internos:
            d_int.append(np.array([0, B - (O_asm[1] + z0 * U), 0]))
        d_pr = d_marco + RIGHT * 3.4 + DOWN * 0.3
        d_pl = d_marco + LEFT * 3.4 + DOWN * 0.3

        eje = DashedLine([0, -0.7, 0], [0, 3.7, 0], color=C_EJE, stroke_width=2, dash_length=0.12).set_z_index(0)
        # etiquetas y guías
        etiquetas = VGroup()
        guias = VGroup()
        flechas_m = VGroup()
        cols = [C_SAT, C_OK, C_ANT, TINTA, C_ANT]
        for (g, z0, B, nombre), d, col in zip(internos, d_int, cols):
            centro = g.get_center() + d
            l = et(nombre, 24, col).move_to([2.6, centro[1], 0], aligned_edge=LEFT)
            etiquetas.add(l)
            guias.add(Line([centro[0] + 0.75, centro[1], 0], [2.45, centro[1], 0], color=TENUE, stroke_width=1.5, stroke_opacity=0.6))
            flechas_m.add(flecha([-1.2, centro[1] - 0.2, 0], [-1.2, centro[1] + 0.25, 0], TENUE, 3, 0.14))
        cm = estructura.get_center() + d_marco
        l_est = et("Estructura", 24, TENUE).move_to([0, -3.75, 0])
        l_pan = et("Paneles", 24, C_CIELO).move_to(pan_r.get_center() + d_pr + DOWN * 1.75)
        flechas_m.add(flecha([-1.2, -1.9, 0], [-1.2, -2.4, 0], TENUE, 3, 0.14),
                      flecha(pan_r.get_center() + d_pr + RIGHT * 0.85, pan_r.get_center() + d_pr + RIGHT * 1.35, TENUE, 3, 0.14),
                      flecha(pan_l.get_center() + d_pl + LEFT * 0.85, pan_l.get_center() + d_pl + LEFT * 1.35, TENUE, 3, 0.14))

        self.play(FadeIn(estructura, shift=UP * 0.2), FadeIn(pan_r), FadeIn(pan_l), run_time=1.4)
        for g, *_ in internos:
            self.add(g)
        self.wait(1.2)
        self.play(Create(eje), run_time=0.6)
        anims = [estructura.animate.shift(d_marco), pan_r.animate.shift(d_pr), pan_l.animate.shift(d_pl)]
        anims += [g.animate.shift(d) for (g, *_), d in zip(internos, d_int)]
        self.play(LaggedStart(*anims, lag_ratio=0.12), run_time=2.8, rate_func=smooth)
        self.play(LaggedStart(*[GrowArrow(f) for f in flechas_m], lag_ratio=0.1),
                  LaggedStart(*[Write(l) for l in etiquetas], lag_ratio=0.15),
                  Create(guias), Write(l_est), Write(l_pan), run_time=1.6)
        self.play(*[g.animate(rate_func=there_and_back).shift(UP * 0.12) for g, *_ in internos], run_time=2.2)
        self.wait(1.0)
        self.play(FadeOut(etiquetas), FadeOut(guias), FadeOut(flechas_m), FadeOut(l_est), FadeOut(l_pan), run_time=0.6)
        anims = [estructura.animate.shift(-d_marco), pan_r.animate.shift(-d_pr), pan_l.animate.shift(-d_pl)]
        anims += [g.animate.shift(-d) for (g, *_), d in zip(internos, d_int)]
        self.play(LaggedStart(*anims, lag_ratio=0.08), FadeOut(eje), run_time=2.6, rate_func=smooth)
        cuerpo = VGroup(estructura, pan_r, pan_l, *[g for g, *_ in internos])
        self.play(cuerpo.animate.scale(1.6).move_to(ORIGIN), run_time=1.4)
        self.cierre()


# =================================================================== 7 ======
class PipelineCompuertas(Pieza):
    def construct(self):
        self.add(et("Ilustrativo", 20, TENUE).to_corner(DR, buff=0.4))
        rng = np.random.default_rng(11)
        N = 54
        ok = rng.random(N) < 0.27
        ok[:3] = [False, True, False]
        K = int(ok.sum())

        # embudo
        pared_s = VMobject()
        pared_s.set_points_as_corners([[-3.7, 2.8, 0], [-0.3, 0.5, 0]])
        pared_i = VMobject()
        pared_i.set_points_as_corners([[-3.7, -2.8, 0], [-1.45, -0.98, 0]])
        for p in (pared_s, pared_i):
            p.set_stroke(C_EJE, width=4)
        tubo_s = Line([0.1, 0.42, 0], [3.3, 0.42, 0], color=C_EJE, stroke_width=4)
        tubo_i = Line([-0.2, -0.42, 0], [3.3, -0.42, 0], color=C_EJE, stroke_width=4)
        pilar_s = Rectangle(width=0.2, height=1.4, color=C_ANT, stroke_width=2, fill_color=C_ANT, fill_opacity=0.6).move_to([0, 1.2, 0])
        pilar_i = Rectangle(width=0.2, height=1.4, color=C_ANT, stroke_width=2, fill_color=C_ANT, fill_opacity=0.6).move_to([0, -1.2, 0])
        rayo = Rectangle(width=0.1, height=0.5, stroke_width=0, fill_color=C_ANT, fill_opacity=0.5).move_to([0, 0, 0])
        rt = ValueTracker(0)
        rayo.add_updater(lambda m: m.set_fill(C_ANT, opacity=0.25 + 0.3 * np.sin(rt.get_value() * 12) ** 2))
        l_gate = et("Validación", 26, C_ANT).move_to([0, 2.3, 0])

        caja_ev = RoundedRectangle(corner_radius=0.2, width=3.0, height=3.4, color=C_OK, stroke_width=3,
                                   fill_color=C_OK, fill_opacity=0.07).move_to([5.0, 0, 0])
        l_ev = et("Evaluación", 26, C_OK).next_to(caja_ev, DOWN, buff=0.25)
        cubo = Rectangle(width=2.6, height=0.9, color=C_MAL, stroke_width=3, fill_color=C_MAL, fill_opacity=0.10).move_to([-0.3, -3.0, 0])
        l_cu = et("Descarte", 24, C_MAL).next_to(cubo, DOWN, buff=0.2)
        l_ca = et("Candidatas", 26, C_CIELO).move_to([-5.5, -2.7, 0])

        # candidatas
        ini = []
        for i in range(N):
            r = np.sqrt(rng.random())
            a = rng.random() * TAU
            ini.append(np.array([-5.5 + 1.15 * r * np.cos(a), 0.0 + 1.9 * r * np.sin(a), 0]))
        dots = VGroup(*[Dot(p, radius=0.09, color=C_CIELO) for p in ini])

        # posiciones finales
        cols_g, filas_g = 4, 5
        slots = [np.array([5.0 - 0.9 + 0.6 * (j % cols_g), 1.15 - 0.55 * (j // cols_g), 0]) for j in range(K)]
        si = 0
        d1, d2 = 2.6, 1.7
        lag = 0.035
        anims = []
        tiempos_ok, tiempos_mal = [], []
        for i, d in enumerate(dots):
            p0 = ini[i]
            y = p0[1]
            pts_a = [p0, np.array([-2.9, y * 0.55 + rng.normal(0, .05), 0]), np.array([-1.3, y * 0.15, 0]), np.array([-0.55, 0, 0])]
            a = VMobject().set_points_smoothly(pts_a)
            if ok[i]:
                fin = slots[si]
                si += 1
                pts_b = [np.array([-0.55, 0, 0]), np.array([0.4, 0, 0]), np.array([2.4, fin[1] * 0.3, 0]), fin]
                col = C_OK
            else:
                fin = np.array([rng.uniform(-1.45, 0.85), rng.uniform(-3.3, -2.75), 0])
                pts_b = [np.array([-0.55, 0, 0]), np.array([-0.62, -0.6, 0]), np.array([-0.6, -1.9, 0]), fin]
                col = C_MAL
            b = VMobject().set_points_smoothly(pts_b)
            anims.append(Succession(MoveAlongPath(d, a, run_time=d1, rate_func=smooth),
                                    d.animate(run_time=0.18).set_color(col),
                                    MoveAlongPath(d, b, run_time=d2, rate_func=smooth)))
            (tiempos_ok if ok[i] else tiempos_mal).append(i * lag * (d1 + 0.18 + d2) + d1)
        total = (d1 + 0.18 + d2) * (1 + (N - 1) * lag)
        clk = ValueTracker(0)
        c_ok = cifra_viva(lambda: sum(t <= clk.get_value() for t in tiempos_ok), "", 40, C_OK, 0, centro=[5.0, 2.55, 0])
        c_mal = cifra_viva(lambda: sum(t <= clk.get_value() for t in tiempos_mal), "", 40, C_MAL, 0, centro=[2.1, -3.0, 0])

        self.play(Create(pared_s), Create(pared_i), Create(tubo_s), Create(tubo_i), run_time=1.2)
        self.play(FadeIn(pilar_s), FadeIn(pilar_i), FadeIn(rayo), Write(l_gate), run_time=1.0)
        self.play(FadeIn(caja_ev), Write(l_ev), FadeIn(cubo), Write(l_cu), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.02), Write(l_ca), run_time=1.4)
        self.add(c_ok, c_mal)
        self.play(LaggedStart(*anims, lag_ratio=lag), clk.animate.set_value(total), rt.animate.set_value(total),
                  run_time=total, rate_func=linear)
        # mejor candidata
        mejor = [dots[i] for i in range(N) if ok[i]][K // 2]
        anillo = Circle(radius=0.28, color=C_OK, stroke_width=4).move_to(mejor)
        self.play(Create(anillo), Indicate(mejor, color=C_OK, scale_factor=1.6), run_time=1.2)
        rayo.clear_updaters()
        c_ok.clear_updaters()
        c_mal.clear_updaters()
        self.cierre()


# =================================================================== 8 ======
def semaforo(pos):
    lamps = VGroup(*[Circle(radius=0.11, stroke_width=0, fill_opacity=1).move_to(pos + RIGHT * 0.3 * (i - 1))
                     for i in range(3)])
    return lamps


class TelemetriaEnVivo(Pieza):
    def construct(self):
        rng = np.random.default_rng(5)
        N = 400
        ts = np.linspace(0, 10, N)
        anom = lambda t, a, b, c: np.where(t < b, suave((t - a) / (b - a)), 1 - suave((t - b) / (c - b))) * ((t > a) & (t < c))
        pico = anom(ts, 5.2, 6.4, 8.6)
        ruido = lambda s: np.convolve(rng.normal(0, 1, N + 10), np.ones(6) / 6, mode="same")[5:N + 5] * s
        volt = 7.9 + 0.3 * np.sin(2 * PI * ts / 3.3 + 0.6) + ruido(0.04) - 0.42 * anom(ts, 5.6, 6.3, 7.4)
        pico_t = suave((ts - 5.2) / 0.8) * (1 - suave((ts - 7.0) / 1.7))
        temp = 24 + 3 * np.sin(2 * PI * ts / 3.3) + ruido(0.6) + 52 * pico_t
        act = 0.5 * np.sin(2 * PI * ts / 2.1) * 0.6 + ruido(0.35) + 2.6 * anom(ts, 5.4, 6.2, 7.6)
        sen = 18 + 1.2 * np.sin(2 * PI * ts / 4.1) + ruido(0.7) - 9 * anom(ts, 5.6, 6.6, 8.2)
        series = {
            "Batería": dict(v=volt, rango=(7.2, 8.6), unidad="V", dec=2, warn=lambda v: v < 7.6, alarm=lambda v: v < 7.3),
            "Temperatura": dict(v=temp, rango=(10, 85), unidad="°C", dec=0, warn=lambda v: v > 45, alarm=lambda v: v > 60),
            "Actitud": dict(v=act, rango=(-1.5, 3.5), unidad="°", dec=1, warn=lambda v: abs(v) > 1.6, alarm=lambda v: abs(v) > 4),
            "Señal": dict(v=sen, rango=(4, 22), unidad="dB", dec=0, warn=lambda v: v < 13, alarm=lambda v: v < 6),
        }
        centros = {"Batería": (-3.35, 1.85), "Temperatura": (3.35, 1.85), "Actitud": (-3.35, -1.85), "Señal": (3.35, -1.85)}
        pw, ph = 6.3, 3.3
        T = ValueTracker(0)
        paneles = VGroup()
        objetos_vivos = []
        hoy = lambda: T.get_value()

        def estado(nombre, t):
            d = series[nombre]
            v = np.interp(t, ts, d["v"])
            return 2 if d["alarm"](v) else (1 if d["warn"](v) else 0)
        col_est = [C_OK, C_SAT, C_MAL]

        for nombre, (cx, cy) in centros.items():
            d = series[nombre]
            marco = RoundedRectangle(corner_radius=0.18, width=pw, height=ph, color=C_EJE, stroke_width=2.5,
                                     fill_color=C_PANEL, fill_opacity=0.45).move_to([cx, cy, 0])
            titulo = et(nombre, 24, TINTA).move_to([cx - pw / 2 + 0.25, cy + ph / 2 - 0.38, 0], aligned_edge=LEFT)
            lect = cifra_viva(lambda d=d: np.interp(hoy(), ts, d["v"]), d["unidad"], 26, C_ANT, d["dec"],
                              centro=[cx + 0.35, cy + ph / 2 - 0.4, 0], borde=RIGHT)
            lect.add_updater(lambda m, n=nombre: m[0].set_color(col_est[estado(n, hoy())]))
            sem = semaforo(np.array([cx + pw / 2 - 1.05, cy + ph / 2 - 0.4, 0]))

            def sm(m, n=nombre):
                e = estado(n, hoy())
                for i, l in enumerate(m):
                    lit = (e == 2 and i == 0) or (e == 1 and i == 1) or (e == 0 and i == 2)
                    l.set_fill([C_MAL, C_SAT, C_OK][i], opacity=1 if lit else 0.15)
            sem.add_updater(sm)
            sm(sem)
            x0, x1 = cx - pw / 2 + 0.35, cx + pw / 2 - 0.3
            y0, y1 = cy - ph / 2 + 0.3, cy + ph / 2 - 0.95
            rejilla = VGroup(*[Line([x0, y0 + (y1 - y0) * f, 0], [x1, y0 + (y1 - y0) * f, 0], color=C_EJE,
                                    stroke_width=1, stroke_opacity=0.45) for f in (0, 0.5, 1)])
            lo, hi = d["rango"]
            gx = lambda t, x0=x0, x1=x1: x0 + (x1 - x0) * t / 10
            gy = lambda v, y0=y0, y1=y1, lo=lo, hi=hi: y0 + (y1 - y0) * (np.clip(v, lo, hi) - lo) / (hi - lo)
            linea = VMobject()
            roja = VMobject()
            punta = Dot(radius=0.09)

            def dib(m, d=d, gx=gx, gy=gy, roja=roja, punta=punta, n=nombre):
                t = hoy()
                k = max(2, min(N, int(np.searchsorted(ts, t)) + 1))
                xs, ys = gx(ts[:k]), gy(d["v"][:k])
                m.set_points_as_corners(np.column_stack([xs, ys, np.zeros(k)]))
                m.set_stroke(C_ANT, width=3.5); m.set_fill(opacity=0)
                mask = np.array([d["alarm"](v) for v in d["v"][:k]])
                if mask.sum() >= 2:
                    idx = np.where(mask)[0]
                    roja.set_points_as_corners(np.column_stack([xs[idx[0]:idx[-1] + 1], ys[idx[0]:idx[-1] + 1], np.zeros(idx[-1] - idx[0] + 1)]))
                    roja.set_stroke(C_MAL, width=5, opacity=1)
                else:
                    roja.set_points_as_corners([[x0, y0, 0], [x0 + 1e-3, y0, 0]]); roja.set_stroke(opacity=0)
                roja.set_fill(opacity=0)
                punta.move_to([xs[-1], ys[-1], 0]).set_fill(col_est[estado(n, t)], opacity=1)
            linea.add_updater(dib)
            paneles.add(VGroup(marco, titulo, rejilla))
            objetos_vivos.append((marco, nombre, lect, sem, linea, roja, punta))
            paneles[-1].add(VGroup())
            if nombre == "Temperatura":
                umbral = DashedLine([x0, gy(60), 0], [x1, gy(60), 0], color=C_MAL, stroke_width=2, stroke_opacity=0.6, dash_length=0.12)
                paneles[-1].add(umbral)

        # borde de alarma
        borde_a = RoundedRectangle(corner_radius=0.18, width=pw + 0.1, height=ph + 0.1, color=C_MAL, stroke_width=0).move_to([3.35, 1.85, 0])
        borde_a.add_updater(lambda m: m.set_stroke(C_MAL if estado("Temperatura", hoy()) == 2 else C_OK,
                                                   width=(3 + 5 * abs(np.sin(hoy() * 8)) if estado("Temperatura", hoy()) == 2 else 0),
                                                   opacity=1))
        # destello verde de resolución
        destello = RoundedRectangle(corner_radius=0.18, width=pw + 0.1, height=ph + 0.1, color=C_OK, stroke_width=0).move_to([3.35, 1.85, 0])

        def dest(m):
            u = (hoy() - 8.0) / 0.9
            m.set_stroke(C_OK, width=6 * float(np.sin(np.clip(u, 0, 1) * PI)), opacity=1)
        destello.add_updater(dest)

        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.15) for p in paneles], lag_ratio=0.2), run_time=2.0)
        vivos = VGroup()
        for marco, nombre, lect, sem, linea, roja, punta in objetos_vivos:
            vivos.add(lect, sem, linea, roja, punta)
        self.play(FadeIn(VGroup(*[o[2] for o in objetos_vivos])), FadeIn(VGroup(*[o[3] for o in objetos_vivos])), run_time=0.8)
        self.add(*[o[4] for o in objetos_vivos], *[o[5] for o in objetos_vivos], *[o[6] for o in objetos_vivos], borde_a, destello)
        self.play(T.animate.set_value(10), run_time=17, rate_func=linear)
        for o in objetos_vivos:
            for m in o[2:5]:
                m.clear_updaters()
        borde_a.clear_updaters()
        destello.clear_updaters()
        self.cierre()


# =================================================================== 9 ======
class RuedasReaccionActitud(Pieza):
    def construct(self):
        dt = 0.005
        Kp, Kd, rel = 3.0, 1.6, 8.0
        TF = 16.0
        objetivo = lambda t: np.radians(60) if t < 8.5 else np.radians(-25)
        n = int(TF / dt) + 1
        tt = np.linspace(0, TF, n)
        th = np.zeros(n); w = np.zeros(n); tg = np.zeros(n)
        for i in range(1, n):
            t = tt[i - 1]
            tg[i - 1] = objetivo(max(t - 0.6, 0))
            a = Kp * (tg[i - 1] - th[i - 1]) - Kd * w[i - 1]
            w[i] = w[i - 1] + a * dt
            th[i] = th[i - 1] + w[i] * dt
        tg[-1] = tg[-2]
        T = ValueTracker(0)
        ang = lambda: float(np.interp(T.get_value(), tt, th))
        tgt = lambda: float(np.interp(T.get_value(), tt, tg))
        vel = lambda: float(np.interp(T.get_value(), tt, w))

        c = np.array([-3.4, 0.1, 0])
        # cojinete de aire
        pedestal = Circle(radius=0.85, color=TENUE, stroke_width=3, fill_color=C_EJE, fill_opacity=0.7).move_to(c)
        pedestal.set_z_index(0)
        aire = VGroup(*[Circle(radius=1.0 + 0.3 * k, color=C_ANT, stroke_width=2).move_to(c) for k in range(3)])
        aire.add_updater(lambda m: [x.set_stroke(C_ANT, opacity=0.5 * (1 - ((T.get_value() * 0.6 + i / 3) % 1)) * 0.9, width=2) or
                                    x.set_width(2 * (0.95 + 0.6 * ((T.get_value() * 0.6 + i / 3) % 1))) for i, x in enumerate(m)])
        aire.set_z_index(0)

        # satélite (vista superior)
        cuerpo = Square(2.0, color=C_SAT, stroke_width=4, fill_color=C_SAT, fill_opacity=0.28).move_to(c)
        nariz = Polygon(c + [1.0, 0.35, 0], c + [1.35, 0, 0], c + [1.0, -0.35, 0], color=C_SAT, stroke_width=3,
                        fill_color=C_SAT, fill_opacity=0.9)
        alas = VGroup(*[Rectangle(width=1.35, height=0.75, color=C_SAT, stroke_width=3, fill_color=C_CIELO, fill_opacity=0.55)
                        .move_to(c + [0, sg * 1.62, 0]) for sg in (-1, 1)])
        cables = VGroup(*[Line(c + [0, sg * 1.0, 0], c + [0, sg * 1.25, 0], color=C_SAT, stroke_width=3) for sg in (-1, 1)])
        rx = Rectangle(width=0.95, height=0.2, color=TENUE, stroke_width=2, fill_color=TENUE, fill_opacity=0.5).move_to(c + [0, 0.78, 0])
        ry = Rectangle(width=0.2, height=0.95, color=TENUE, stroke_width=2, fill_color=TENUE, fill_opacity=0.5).move_to(c + [-0.78, 0, 0])
        disco = VGroup(Circle(radius=0.52, color=C_ANT, stroke_width=4, fill_color=C_ANT, fill_opacity=0.35),
                       *[Line(ORIGIN, 0.5 * np.array([np.cos(a), np.sin(a), 0]), color=C_ANT, stroke_width=3) for a in np.arange(0, TAU, TAU / 6)],
                       Line(ORIGIN, RIGHT * 0.5, color=C_SAT, stroke_width=6),
                       Dot(radius=0.08, color=C_ANT)).move_to(c)
        sat = VGroup(alas, cables, cuerpo, nariz, rx, ry, disco).set_z_index(2)
        est = {"a": 0.0, "d": 0.0}

        def rot(m):
            a = ang()
            m.rotate(a - est["a"], about_point=c)
            est["a"] = a
            # rueda: momento angular  I_s*w + I_w*W = 0  ->  giro inercial = -rel*theta
            d_rel = -rel * a - a
            disco.rotate(d_rel - est["d"], about_point=c)
            est["d"] = d_rel
            act = min(1, abs(vel()) * 1.2)
            disco[0].set_fill(C_ANT, opacity=0.25 + 0.5 * act).set_stroke(interpolate_color(ManimColor(C_ANT), ManimColor(TINTA), act * 0.5))
        sat.add_updater(rot)

        # objetivo
        R = 3.15
        guia = DashedLine(c, c + [R, 0, 0], color=C_OK, stroke_width=3, dash_length=0.14).set_z_index(1)
        objm = Dot(radius=0.13, color=C_OK).set_z_index(3)
        arco = VMobject()
        ref0 = DashedLine(c, c + [R, 0, 0], color=C_EJE, stroke_width=1.5, stroke_opacity=0.6, dash_length=0.1).set_z_index(0)
        anillo_r = Circle(radius=R, color=C_EJE, stroke_width=1, stroke_opacity=0.35).move_to(c).set_z_index(0)

        def upd_obj(m):
            a = tgt()
            m.become(DashedLine(c, c + R * np.array([np.cos(a), np.sin(a), 0]), color=C_OK, stroke_width=3, dash_length=0.14))
            objm.move_to(c + R * np.array([np.cos(a), np.sin(a), 0]))
        guia.add_updater(upd_obj)
        upd_obj(guia)

        def upd_arco(m):
            a = ang()
            if abs(a) < 0.02:
                m.set_points([ORIGIN]); m.set_stroke(opacity=0); return
            m.become(Arc(radius=2.55, start_angle=0, angle=a, arc_center=c, color=C_SAT, stroke_width=4))
        arco.add_updater(upd_arco)
        arco.set_z_index(1)

        l_air = et("Cojinete de aire", 22, C_ANT).move_to(c + [0, -3.2, 0])
        l_rue = et("Ruedas de reacción", 22, C_ANT).move_to(c + [0, 3.35, 0])
        lead = Line(c + [0, 3.05, 0], c + [0, 0.7, 0], color=C_ANT, stroke_width=1.5, stroke_opacity=0.5).set_z_index(1)

        # gráfica
        ox, oy, wx, hy = 1.5, -2.7, 5.1, 5.0
        lo, hi = -40, 90
        gx = lambda t: ox + wx * t / TF
        gy = lambda a: oy + hy * (np.degrees(a) - lo) / (hi - lo)
        ejex = Arrow([ox, oy, 0], [ox + wx + 0.35, oy, 0], buff=0, color=TENUE, stroke_width=3, tip_length=0.15)
        ejey = Arrow([ox, oy, 0], [ox, oy + hy + 0.4, 0], buff=0, color=TENUE, stroke_width=3, tip_length=0.15)
        cero = DashedLine([ox, gy(0), 0], [ox + wx, gy(0), 0], color=C_EJE, stroke_width=1.5, dash_length=0.1)
        l_t = et("Tiempo", 22, TENUE).next_to(ejex, DOWN, buff=0.1, aligned_edge=RIGHT)
        l_a = et("Ángulo", 22, TINTA).next_to(ejey, UP, buff=0.08).shift(RIGHT * 0.5)
        escalon = VMobject()
        xs_e = np.array([0, 0.6, 0.6, 9.1, 9.1, TF])
        ys_e = np.radians(np.array([0, 0, 60, 60, -25, -25]))
        escalon.set_points_as_corners(np.column_stack([gx(xs_e), gy(ys_e), np.zeros(6)]))
        escalon.set_stroke(C_OK, width=2.5, opacity=0.8)
        escalon = DashedVMobject(escalon, num_dashes=90)
        curva = VMobject()
        punta = Dot(radius=0.1, color=C_SAT)

        def cur(m):
            t = T.get_value()
            k = max(2, int(t / dt) + 1)
            step = 5
            idx = np.arange(0, k, step)
            if idx[-1] != k - 1:
                idx = np.append(idx, k - 1)
            m.set_points_as_corners(np.column_stack([gx(tt[idx]), gy(th[idx]), np.zeros(len(idx))]))
            m.set_stroke(C_SAT, width=4.5); m.set_fill(opacity=0)
            punta.move_to([gx(tt[k - 1]), gy(th[k - 1]), 0])
        curva.add_updater(cur)
        cur(curva)
        lect = cifra_viva(lambda: np.degrees(ang()), "°", 40, C_SAT, 0, centro=[6.6, 3.3, 0], borde=RIGHT)

        self.play(FadeIn(pedestal), Create(anillo_r), Create(ref0), run_time=1.2)
        self.add(aire)
        self.play(FadeIn(sat, scale=0.85), Write(l_air), run_time=1.4)
        self.play(Create(lead), Write(l_rue), run_time=1.0)
        self.play(Create(ejex), Create(ejey), FadeIn(cero), Write(l_t), Write(l_a), run_time=1.2)
        self.play(Create(escalon), FadeIn(guia), FadeIn(objm), run_time=1.2)
        self.add(arco, curva, punta, lect)
        self.play(T.animate.set_value(TF), run_time=TF, rate_func=linear)
        for m in (aire, sat, guia, arco, curva, lect):
            m.clear_updaters()
        self.cierre()

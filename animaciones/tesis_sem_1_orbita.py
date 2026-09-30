"""Seminario de divulgación, bloques 1 y 2: agentes en órbita, escala y estándares (7 piezas)."""
from tesis_lib import *
import numpy as np


# =============================================================================
# helpers propios de este archivo
# =============================================================================
def texto_vivo(fn, tam=40, color=None, pos=ORIGIN, borde=ORIGIN, color_fn=None):
    """Texto (Carlito) que se reconstruye cada fotograma con fn() -> str."""
    def _col():
        return color_fn() if color_fn else (color or TINTA)

    m = Text(fn(), font=FUENTE, font_size=tam, color=_col())

    def act(mm):
        nuevo = Text(fn(), font=FUENTE, font_size=tam, color=_col())
        nuevo.move_to(pos() if callable(pos) else pos, aligned_edge=borde)
        mm.become(nuevo)
    act(m)
    m.add_updater(act)
    return m


def flecha_punteada(a, b, color=None, ancho=3, punta=0.2):
    c = color or TENUE
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    d = b - a
    ang = np.arctan2(d[1], d[0])
    u = d / np.linalg.norm(d)
    linea = DashedLine(a, b - u * punta * 0.8, color=c, stroke_width=ancho, dash_length=0.14)
    tip = Triangle(color=c, fill_color=c, fill_opacity=1, stroke_width=0).scale(punta * 0.62)
    tip.rotate(ang - PI / 2).move_to(b - u * punta * 0.35)
    return VGroup(linea, tip)


def iss(s=1.0):
    """Estación Espacial esquemática (vista lateral). Devuelve (grupo, carga_util)."""
    g = VGroup()
    truss = Rectangle(width=5 * s, height=0.09 * s, color=C_SAT, fill_color=C_SAT, fill_opacity=0.9,
                      stroke_width=1.5)
    paneles = VGroup()
    for x in (-2.1, -1.55, 1.55, 2.1):
        for sy in (1, -1):
            p = Rectangle(width=0.42 * s, height=0.95 * s, color=C_SAT, fill_color=C_CIELO,
                          fill_opacity=0.55, stroke_width=1.5)
            p.move_to([x * s, sy * (0.045 + 0.06 + 0.475) * s, 0])
            paneles.add(p)
    modulo = Rectangle(width=0.34 * s, height=1.5 * s, color=C_SAT, fill_color=C_SAT, fill_opacity=0.35,
                       stroke_width=1.5).move_to([0, -0.2 * s, 0])
    nodo_ = Rectangle(width=1.1 * s, height=0.3 * s, color=C_SAT, fill_color=C_SAT, fill_opacity=0.35,
                      stroke_width=1.5).move_to([0, -0.55 * s, 0])
    carga = Square(0.2 * s, color=C_SAT, fill_color=C_SAT, fill_opacity=1, stroke_width=1.5)
    carga.next_to(nodo_, LEFT, buff=0.02 * s)
    g.add(paneles, truss, modulo, nodo_, carga)
    return g, carga


def cubesat(tam=0.5, color=None, punteado=False, op=1.0):
    """CubeSat 6U con paneles desplegados."""
    c = color or C_SAT
    cuerpo = Rectangle(width=tam, height=tam * 0.72, color=c, fill_color=c,
                       fill_opacity=0.0 if punteado else 0.3, stroke_width=2)
    pan = [Rectangle(width=tam * 0.85, height=tam * 0.42, color=c, fill_color=C_CIELO,
                     fill_opacity=0.0 if punteado else 0.5, stroke_width=1.5) for _ in range(2)]
    pan[0].next_to(cuerpo, LEFT, buff=tam * 0.08)
    pan[1].next_to(cuerpo, RIGHT, buff=tam * 0.08)
    if punteado:
        caja_p = DashedVMobject(cuerpo, num_dashes=8, dashed_ratio=0.55).set_stroke(c, width=1.8, opacity=op)
        for p in pan:
            p.set_stroke(c, width=1.5, opacity=0.7 * op)
        return VGroup(caja_p, *pan)
    fondo = VGroup(*[m.copy().set_fill(FONDO, opacity=1).set_stroke(width=0) for m in (cuerpo, *pan)])
    rejilla = VGroup(Line(cuerpo.get_top(), cuerpo.get_bottom()),
                     Line(cuerpo.get_left(), cuerpo.get_right())).set_stroke(c, width=1.2, opacity=0.8)
    antena_ = VGroup(Line(cuerpo.get_top(), cuerpo.get_top() + UP * tam * 0.3, color=c, stroke_width=2),
                     Dot(cuerpo.get_top() + UP * tam * 0.34, radius=tam * 0.07, color=c))
    return VGroup(fondo, cuerpo, rejilla, *pan, antena_)


def engrane(r=0.18, color=None, dientes=8):
    c = color or C_CIELO
    pts = []
    for k in range(dientes * 4):
        a = TAU * k / (dientes * 4)
        rr = r if (k % 4) in (0, 1) else r * 0.72
        pts.append([rr * np.cos(a), rr * np.sin(a), 0])
    g = Polygon(*pts, color=c, stroke_width=2, fill_color=c, fill_opacity=0.25)
    return VGroup(g, Circle(radius=r * 0.3, color=c, stroke_width=2))


def rombo_si(tam=0.3, color=None):
    """Rombo de decisión de diagrama de flujo (si → entonces) con sus dos salidas."""
    c = color or C_CIELO
    r = Square(tam, color=c, stroke_width=2, fill_color=c, fill_opacity=0.2).rotate(PI / 4)
    h = tam / np.sqrt(2)
    s1 = Arrow(r.get_right(), r.get_right() + RIGHT * 0.28, buff=0, color=c, stroke_width=2,
               tip_length=0.09, max_tip_length_to_length_ratio=0.5)
    s2 = Arrow(r.get_bottom(), r.get_bottom() + DOWN * 0.28, buff=0, color=c, stroke_width=2,
               tip_length=0.09, max_tip_length_to_length_ratio=0.5)
    return VGroup(r, s1, s2)


def documento(ancho=3.0, alto=4.0, color=None, doblez=0.45, relleno=0.1, ancho_trazo=2.5):
    c = color or TENUE
    w, h, d = ancho / 2, alto / 2, doblez
    cuerpo = Polygon([-w, h, 0], [w - d, h, 0], [w, h - d, 0], [w, -h, 0], [-w, -h, 0],
                     color=c, stroke_width=ancho_trazo, fill_color=c, fill_opacity=relleno)
    oreja = VMobject().set_points_as_corners([[w - d, h, 0], [w - d, h - d, 0], [w, h - d, 0]])
    oreja.set_stroke(c, width=ancho_trazo * 0.8)
    return VGroup(cuerpo, oreja)


def lupa(r=0.42, color=None):
    c = color or TINTA
    aro = Circle(radius=r, color=c, stroke_width=5, fill_color=C_ANT, fill_opacity=0.1)
    mango = Line(r * np.array([np.cos(-PI / 4), np.sin(-PI / 4), 0]),
                 1.9 * r * np.array([np.cos(-PI / 4), np.sin(-PI / 4), 0]), color=c, stroke_width=9)
    return VGroup(aro, mango)


def persona(alto=0.9, color=None):
    c = color or C_ANT
    cabeza = Circle(radius=alto * 0.17, color=c, fill_color=c, fill_opacity=0.35, stroke_width=2.5)
    cuerpo = Arc(radius=alto * 0.36, start_angle=0, angle=PI, color=c, stroke_width=2.5)
    cuerpo.add_line_to(cuerpo.get_start())
    cuerpo.set_fill(c, opacity=0.35)
    cabeza.next_to(cuerpo, UP, buff=alto * 0.06)
    return VGroup(cuerpo, cabeza)


def rgba(hex_, a=1.0):
    r, g, b = color_to_rgb(hex_)
    return np.array([r * 255, g * 255, b * 255, a * 255], dtype=float)


# =============================================================================
# 1. ASTREA: el modelo aconseja, el controlador decide
# =============================================================================
class AstreaAconseja(Pieza):
    def construct(self):
        chip_t = chip_tercero("ASTREA 2025")
        estacion_, carga = iss(0.72)
        estacion_.move_to([0, 2.8, 0])
        panel = RoundedRectangle(corner_radius=0.25, width=12.8, height=4.4, color=C_EJE,
                                 stroke_width=2).move_to([0, -0.7, 0])
        zoom = VGroup(*[DashedLine(carga.get_bottom(), panel.get_corner(v), color=TENUE, stroke_width=1.5,
                                   dash_length=0.1, stroke_opacity=0.6) for v in (UL, UR)])
        zoom.set_z_index(-2)
        estacion_.set_z_index(1)

        self.play(FadeIn(estacion_, lag_ratio=0.05), FadeIn(chip_t), run_time=1.3)
        self.play(Indicate(carga, scale_factor=1.8, color=C_SAT), run_time=0.8)
        self.play(Create(zoom), Create(panel), run_time=1.1)

        # --- lazo cerrado: controlador ⇄ térmico ---
        ctrl = caja("Controlador", 2.7, 0.9, C_ANT, 26).move_to([0, -0.55, 0])
        term = caja("Térmico", 2.3, 0.9, TENUE, 26).move_to([4.4, -0.55, 0])
        perilla_c = np.array([0, 0.72, 0])
        aro = Circle(radius=0.3, color=C_ANT, stroke_width=3, fill_color=C_ANT, fill_opacity=0.15).move_to(perilla_c)
        marcas = VGroup(*[Line(perilla_c + 0.38 * np.array([np.cos(a), np.sin(a), 0]),
                               perilla_c + 0.46 * np.array([np.cos(a), np.sin(a), 0]),
                               color=C_ANT, stroke_width=2)
                          for a in np.linspace(225, -45, 7) * DEGREES])
        aguja = Line(perilla_c, perilla_c + 0.27 * np.array([np.cos(120 * DEGREES), np.sin(120 * DEGREES), 0]),
                     color=TINTA, stroke_width=4)
        tallo = Line(perilla_c + DOWN * 0.3, ctrl.get_top(), color=C_ANT, stroke_width=3)
        perilla = VGroup(tallo, aro, marcas, aguja)

        # mini gráfica de temperatura con banda segura
        gc = np.array([4.4, 0.72, 0])
        marco = Rectangle(width=2.3, height=1.0, color=C_EJE, stroke_width=1.5).move_to(gc)
        banda = Rectangle(width=2.3, height=0.5, stroke_width=0, fill_color=C_OK, fill_opacity=0.2).move_to(gc)
        bordes = VGroup(*[DashedLine(gc + [-1.15, s * 0.25, 0], gc + [1.15, s * 0.25, 0], color=C_OK,
                                     stroke_width=1.5, dash_length=0.08) for s in (1, -1)])
        reloj = ValueTracker(0.0)
        amp = ValueTracker(1.0)

        def curva():
            t0 = reloj.get_value()
            xs = np.linspace(-1.1, 1.1, 90)
            tt = t0 * 1.3 + xs * 2.2
            ys = amp.get_value() * (0.12 * np.sin(1.7 * tt) + 0.06 * np.sin(4.3 * tt + 1.0))
            return trazo(gc[0] + xs, gc[1] + ys, TINTA, 2.5)
        traza = always_redraw(curva)

        ida = Arrow(ctrl.get_right(), term.get_left(), buff=0.1, color=C_ANT, stroke_width=5,
                    max_tip_length_to_length_ratio=0.15)
        vuelta = CurvedArrow(term.get_bottom() + DOWN * 0.08, ctrl.get_bottom() + DOWN * 0.08,
                             angle=-1.7, color=C_ANT, stroke_width=5)
        decide = et("Decide", 30, C_ANT).move_to([2.2, -2.45, 0])

        self.play(FadeIn(ctrl, shift=UP * 0.2), FadeIn(term, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(perilla), Create(marco), FadeIn(banda), Create(bordes), run_time=0.8)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj, traza)
        self.play(GrowArrow(ida), Create(vuelta), run_time=1.0)

        # pulsos que recorren el lazo sin parar
        tramo_ida = Line(ida.get_start(), ida.get_end())
        tramo_vuelta = vuelta.copy()

        def pos_lazo(u):
            u = u % 1.0
            if u < 0.35:
                return tramo_ida.point_from_proportion(u / 0.35)
            return tramo_vuelta.point_from_proportion((u - 0.35) / 0.65)
        pulsos = VGroup(*[Dot(radius=0.08, color=TINTA) for _ in range(3)])

        def mover(g):
            for k, d in enumerate(g):
                d.move_to(pos_lazo(reloj.get_value() * 0.35 + k / 3))
        pulsos.add_updater(mover)
        mover(pulsos)
        self.play(FadeIn(pulsos), Write(decide), run_time=0.7)
        self.wait(1.8)

        # --- el modelo pequeño: fuera del lazo, solo aconseja ---
        mc = np.array([-4.5, 0.25, 0])
        cuerpo = RoundedRectangle(corner_radius=0.12, width=1.4, height=1.05, color=C_SAT, fill_color=C_SAT,
                                  fill_opacity=0.15, stroke_width=3).move_to(mc)
        patas = VGroup()
        for x in np.linspace(-0.45, 0.45, 4):
            patas.add(Line(mc + [x, 0.525, 0], mc + [x, 0.68, 0]), Line(mc + [x, -0.525, 0], mc + [x, -0.68, 0]))
        patas.set_stroke(C_SAT, width=2.5)
        params = et("1.54 B", 32, C_SAT).move_to(mc)
        lab_m = et("Modelo pequeño", 24, TINTA).next_to(patas, DOWN, buff=0.2)
        modelo = VGroup(patas, cuerpo, params)
        self.play(FadeIn(modelo, scale=0.8), FadeIn(lab_m, shift=UP * 0.1), run_time=0.9)

        consejo = flecha_punteada(cuerpo.get_right() + RIGHT * 0.12 + UP * 0.25, aro.get_left() + LEFT * 0.1,
                                  C_SAT, 3.5)
        aconseja = et("Aconseja", 28, C_SAT).next_to(consejo, UP, buff=0.18)
        self.play(Indicate(cuerpo, color=C_SAT, scale_factor=1.06), run_time=0.7)
        self.play(Create(consejo), FadeIn(aconseja, shift=DOWN * 0.1), run_time=1.0)

        def aconsejar(giro):
            chispa = Dot(consejo[0].get_start(), radius=0.09, color=C_SAT)
            self.add(chispa)
            self.play(MoveAlongPath(chispa, Line(consejo[0].get_start(), consejo[1].get_center())),
                      run_time=0.8, rate_func=smooth)
            self.remove(chispa)
            self.play(Rotate(aguja, giro, about_point=perilla_c), Flash(aro, color=C_SAT, flash_radius=0.5),
                      amp.animate.set_value(amp.get_value() * 0.8), run_time=0.7)

        aconsejar(-40 * DEGREES)
        self.wait(1.2)
        # el lazo sigue decidiendo solo
        self.play(Indicate(VGroup(ida, vuelta, decide), color=C_ANT, scale_factor=1.04), run_time=1.0)
        aconsejar(20 * DEGREES)
        self.wait(1.6)
        self.cierre()


# =============================================================================
# 2. ASTREA: el ritmo equivocado
# =============================================================================
class AstreaRitmoOrbita(Pieza):
    T_TOT = 180.0  # minutos que muestra la gráfica (dos vueltas)

    @staticmethod
    def _curva_a(t):
        y = 0.3 * np.sin(TAU * t / 90 + PI / 2)
        for k in range(1, 12):
            tk = 15.0 * k
            d = t - tk
            on = d > 0
            y = y + np.where(on, 0.62 * (-1) ** k * np.exp(-np.clip(d, 0, None) / 20.0)
                             * np.sin(TAU * np.clip(d, 0, None) / 26.0), 0.0)
        return y

    @staticmethod
    def _curva_b(t):
        base = 0.64 * np.sin(TAU * t / 90 + PI / 2)
        atenua = 1 - 0.62 * suave((t - 3.0) / 10.0)
        return base * atenua + 0.05 * np.sin(TAU * t / 23.0)

    def construct(self):
        chip_t = chip_tercero("Preprint, n pequeño")
        # --- órbita ---
        oc, R = np.array([-4.6, 0.35, 0]), 1.6
        planeta = tierra(0.7).move_to(oc)
        anillo = Circle(radius=R, color=TENUE, stroke_width=3).move_to(oc)
        lab90 = et("90 min", 28, TINTA).move_to(oc + DOWN * (R + 0.45))

        def en_anillo(ang, r=R):
            return oc + r * np.array([np.cos(ang), np.sin(ang), 0])

        angs = [PI / 2 + k * TAU / 6 for k in range(6)]
        ticks = VGroup(*[Line(en_anillo(a, R - 0.18), en_anillo(a, R + 0.18), color=C_SAT, stroke_width=5)
                         for a in angs])
        corchete = Arc(radius=R + 0.38, start_angle=PI / 2, angle=TAU / 6, color=C_SAT, stroke_width=2.5).shift(oc)
        lab15 = et("15 min", 26, C_SAT).move_to(en_anillo(PI / 2 + TAU / 12, R + 0.95))

        # --- gráfica de temperatura ---
        x0, x1, yc, H = -1.5, 3.3, 0.35, 1.5
        banda_h = 0.55
        ejes = VGroup(Line([x0, yc - H, 0], [x1, yc - H, 0]), Line([x0, yc - H, 0], [x0, yc + H, 0]))
        ejes.set_stroke(C_EJE, width=2)
        banda = Rectangle(width=x1 - x0, height=2 * banda_h, stroke_width=0, fill_color=C_OK,
                          fill_opacity=0.18).move_to([(x0 + x1) / 2, yc, 0])
        bordes = VGroup(*[DashedLine([x0, yc + s * banda_h, 0], [x1, yc + s * banda_h, 0], color=C_OK,
                                     stroke_width=1.5, dash_length=0.1) for s in (1, -1)])
        lab_t = et("Temperatura", 22, TENUE).next_to([x0, yc + H, 0], UP, buff=0.18, aligned_edge=LEFT)

        def xmap(t):
            return x0 + (x1 - x0) * t / self.T_TOT

        # --- barra de violaciones vs referencia ---
        bx, yb, H0 = 5.7, yc - H, 1.5
        ref = DashedLine([bx - 0.65, yb + H0, 0], [bx + 0.65, yb + H0, 0], color=TENUE, stroke_width=2.5,
                         dash_length=0.1)
        lab_ref = et("Referencia", 20, TENUE).next_to(ref, LEFT, buff=0.12)
        piso = Line([bx - 0.65, yb, 0], [bx + 0.65, yb, 0], color=C_EJE, stroke_width=2)
        fase = {"n": "A"}
        prog = ValueTracker(0.0)

        def factor():
            p = prog.get_value()
            return 1 + 0.242 * p if fase["n"] == "A" else 1 - 0.662 * p

        def col_barra():
            p = prog.get_value()
            return interpolate_color(ManimColor(TENUE), ManimColor(C_MAL if fase["n"] == "A" else C_OK), min(1, p * 3))

        barra_v = always_redraw(lambda: barra(bx, yb, H0 * factor(), 0.8, col_barra(), 0.8))

        def pct():
            v = (factor() - 1) * 100
            s = f"{abs(v):.0f}"
            return ("+" if v >= 0 else "−") + s + " %"
        pct_m = texto_vivo(pct, 34, color_fn=col_barra, pos=lambda: [bx, yb + H0 * factor() + 0.35, 0])

        self.play(FadeIn(planeta), Create(anillo), FadeIn(chip_t), run_time=1.0)
        self.play(FadeIn(lab90), Create(ejes), FadeIn(banda), Create(bordes), FadeIn(lab_t), run_time=1.0)
        self.play(Create(piso), Create(ref), FadeIn(lab_ref), FadeIn(barra_v), FadeIn(pct_m), run_time=0.8)
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.15), Create(corchete), FadeIn(lab15),
                  run_time=1.0)

        # --- simulación de una fase ---
        t_min = ValueTracker(0.0)
        sat = satelite(0.16)
        sat.add_updater(lambda m: m.move_to(en_anillo(PI / 2 + TAU * t_min.get_value() / 90)))

        def construir_fase(fn, consejos):
            def dibujar():
                t = t_min.get_value()
                n = max(2, int(t / self.T_TOT * 360))
                ts = np.linspace(0, t, n)
                ys = fn(ts)
                g = VGroup(trazo(xmap(ts), yc + ys, TINTA, 3))
                fuera = np.abs(ys) > banda_h
                i = 0
                while i < n:
                    if fuera[i]:
                        j = i
                        while j + 1 < n and fuera[j + 1]:
                            j += 1
                        if j > i:
                            g.add(trazo(xmap(ts[i:j + 1]), yc + ys[i:j + 1], C_MAL, 5))
                        else:
                            g.add(Dot([xmap(ts[i]), yc + ys[i], 0], radius=0.04, color=C_MAL))
                        i = j + 1
                    else:
                        i += 1
                return g
            linea = always_redraw(dibujar)
            marcas = VGroup(*[DashedLine([xmap(tc), yc - H, 0], [xmap(tc), yc + H, 0], color=C_SAT,
                                         stroke_width=1.5, dash_length=0.08) for tc in consejos])
            for m, tc in zip(marcas, consejos):
                m.add_updater(lambda mm, tc=tc: mm.set_stroke(opacity=0.7 if t_min.get_value() >= tc else 0))
            return linea, marcas

        def brillo_ticks(periodo_ticks):
            def act(g):
                t = t_min.get_value()
                for k, tk in enumerate(g):
                    if periodo_ticks == 15 or k == 0:
                        d = (t - 15.0 * k) % 90 if periodo_ticks == 15 else t % 90
                        if t < 15.0 * k and periodo_ticks == 15:
                            d = 99
                        h = np.exp(-d / 5.0)
                        tk.set_stroke(width=5 + 9 * h)
            return act

        # Fase A: consejo cada 15 min
        linea_a, marcas_a = construir_fase(self._curva_a, [15.0 * k for k in range(1, 12)])
        ticks.add_updater(brillo_ticks(15))
        self.add(marcas_a, linea_a)
        self.play(FadeIn(sat), run_time=0.4)
        self.play(t_min.animate.set_value(self.T_TOT), prog.animate.set_value(1.0), run_time=6.5, rate_func=linear)
        ticks.clear_updaters()
        self.wait(1.0)

        # transición: se quita el consejo frecuente, queda uno por vuelta
        linea_a.clear_updaters()
        self.play(FadeOut(linea_a), FadeOut(marcas_a), FadeOut(ticks[1:]), FadeOut(corchete), FadeOut(lab15),
                  run_time=0.9)
        fase["n"] = "B"
        prog.set_value(0.0)
        t_min.set_value(0.0)
        self.play(Indicate(lab90, color=C_OK, scale_factor=1.25),
                  ShowPassingFlash(anillo.copy().set_stroke(C_OK, width=8), time_width=0.6), run_time=1.1)

        # Fase B: consejo alineado a la órbita
        linea_b, marcas_b = construir_fase(self._curva_b, [3.0, 93.0])
        ticks[0].add_updater(lambda m: m.set_stroke(width=5 + 9 * np.exp(-((t_min.get_value() - 3) % 90) / 5.0)))
        self.add(marcas_b, linea_b)
        self.play(t_min.animate.set_value(self.T_TOT), prog.animate.set_value(1.0), run_time=6.5, rate_func=linear)
        ticks[0].clear_updaters()
        sat.clear_updaters()
        self.play(Indicate(pct_m, color=C_OK, scale_factor=1.15), run_time=0.8)
        self.wait(0.8)
        self.cierre()


# =============================================================================
# 3. NASA Starling: cuatro naves coordinadas con reglas
# =============================================================================
class StarlingCuatroNaves(Pieza):
    def construct(self):
        chip_t = chip_tercero("NASA 2023-24")
        pos = [np.array(p) for p in ([-2.3, 1.1, 0], [-0.8, -0.8, 0], [0.9, 1.3, 0], [2.4, -0.55, 0])]
        naves = VGroup(*[cubesat(0.5).move_to(p) for p in pos])
        lab4 = et("4 CubeSats", 28, TINTA).move_to([0.05, -2.2, 0])
        self.play(LaggedStart(*[FadeIn(n, scale=0.6) for n in naves], lag_ratio=0.2), FadeIn(chip_t), run_time=1.4)
        self.play(FadeIn(lab4, shift=UP * 0.1), run_time=0.5)

        def cen(n):
            return n[1].get_center()

        pares = [(i, j) for i in range(4) for j in range(i + 1, 4)]
        enlaces = VGroup(*[DashedLine(cen(naves[i]), cen(naves[j]), color=C_ANT, stroke_width=2,
                                      dash_length=0.1, stroke_opacity=0.75) for i, j in pares])
        enlaces.set_z_index(-1)
        self.play(LaggedStart(*[Create(e) for e in enlaces], lag_ratio=0.12), run_time=1.3)

        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)
        # mensajes entre pares, en ambos sentidos (nadie es el centro)
        mens = VGroup()
        for k, (i, j) in enumerate(pares):
            for s in (0, 1):
                d = Dot(radius=0.06, color=C_ANT)
                a, b = (naves[i], naves[j]) if s == 0 else (naves[j], naves[i])

                def act(m, a=a, b=b, ph=(k * 0.37 + s * 0.5) % 1):
                    u = (reloj.get_value() * 0.55 + ph) % 1
                    m.move_to(interpolate(cen(a), cen(b), u))
                    m.set_opacity(np.sin(PI * u) ** 0.6)
                d.add_updater(act)
                mens.add(d)
        mens.set_z_index(-1)
        self.add(mens)
        self.wait(1.6)

        # reglas explícitas junto a cada nave (engrane + rombo «si → entonces»)
        reglas = VGroup()
        for n in naves:
            e = engrane(0.17).move_to(cen(n) + [0.05, 0.72, 0])
            r = rombo_si(0.26).move_to(cen(n) + [0.6, 0.66, 0])
            reglas.add(VGroup(e, r))
        lab_r = et("Reglas", 26, C_CIELO).next_to(reglas[2], UP, buff=0.18)
        self.play(LaggedStart(*[FadeIn(r, scale=0.6) for r in reglas], lag_ratio=0.15), FadeIn(lab_r), run_time=1.1)
        for r in reglas:
            r[0].add_updater(lambda m, dt: m.rotate(-1.6 * dt))
        # cada nave evalúa su regla (el rombo se enciende) ...
        self.play(LaggedStart(*[Indicate(r[1][0], color=C_OK, scale_factor=1.3) for r in reglas], lag_ratio=0.25),
                  run_time=1.8)
        # ... y todas apuntan juntas al mismo objetivo
        objetivo = VGroup(Circle(radius=0.22, color=C_CIELO, stroke_width=2.5),
                          Dot(radius=0.06, color=C_CIELO)).move_to([4.6, 2.2, 0])
        self.play(FadeIn(objetivo, scale=0.5), run_time=0.5)
        giros, haces = [], VGroup()
        for n in naves:
            v = objetivo.get_center() - cen(n)
            u = v / np.linalg.norm(v)
            giros.append(Rotate(n, np.arctan2(v[1], v[0]) - PI / 2, about_point=cen(n)))
            haces.add(haz(cen(n) + u * 0.45, objetivo.get_center() - u * 0.28, C_SAT, 2, 0.8))
        self.play(*giros, run_time=1.0)
        self.play(Create(haces), *[r[1][0].animate.set_fill(C_OK, opacity=0.6).set_stroke(C_OK) for r in reglas],
                  run_time=0.8)
        self.wait(0.8)

        # --- lo que voló (izquierda) frente a lo simulado (derecha) ---
        for r in reglas:
            r[0].clear_updaters()
        mens.clear_updaters()
        vuelo = VGroup(naves, enlaces, reglas, objetivo, haces)
        self.play(FadeOut(mens), FadeOut(lab_r), run_time=0.4)
        self.play(vuelo.animate.scale(0.5).move_to([-4.5, 0.45, 0]),
                  lab4.animate.move_to([-4.5, -1.15, 0]), run_time=1.3)

        caja_sim = DashedVMobject(RoundedRectangle(corner_radius=0.25, width=7.6, height=5.0), num_dashes=70)
        caja_sim.set_stroke(C_CIELO, width=2, opacity=0.8).move_to([2.85, 0.1, 0])
        lab_sim = et("Solo simulación", 26, C_CIELO).next_to(caja_sim, UP, buff=0.12)
        fantasmas = VGroup()
        for fila in range(6):
            for col in range(10):
                p = [2.85 + (col - 4.5) * 0.72, 0.1 + (2.5 - fila) * 0.76, 0]
                fantasmas.add(cubesat(0.22, C_SAT, punteado=True, op=0.85).move_to(p))
        lab60 = et("60 naves", 28, TINTA).next_to(caja_sim, DOWN, buff=0.15)
        self.play(Create(caja_sim), FadeIn(lab_sim), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(f, scale=0.5) for f in fantasmas], lag_ratio=0.03), run_time=2.4)
        self.play(FadeIn(lab60, shift=UP * 0.1), run_time=0.6)
        self.wait(1.6)
        self.cierre()


# =============================================================================
# 4. La aritmética de la escala
# =============================================================================
class AritmeticaDeLaEscala(Pieza):
    FILAS, COLS, CEL = 100, 163, 6
    N, N_STAR = 16279, 10742

    def construct(self):
        rng = np.random.default_rng(42)
        chip_t = chip_tercero("McDowell ago-2026")
        F, C, S = self.FILAS, self.COLS, self.CEL
        n_man = int(round(0.868 * self.N))
        # índice en orden columna-mayor: celda i -> (fila i % F, columna i // F)
        orden_llenado = np.empty(self.N, dtype=int)
        orden_llenado[rng.permutation(self.N)] = np.arange(self.N)   # rango de aparición de cada celda
        maniobra = np.zeros(self.N, dtype=bool)
        maniobra[rng.choice(self.N, n_man, replace=False)] = True
        # onda que recorre el enjambre (columna) + un poco de azar: se ve «moverse»
        fase_p = -(np.arange(self.N) // F) * 0.22 + rng.uniform(0, 1.2, self.N)

        mascara = np.zeros((S, S), dtype=float)
        mascara[1:5, 1:5] = 1.0
        mascara[1, 1] = mascara[1, 4] = mascara[4, 1] = mascara[4, 4] = 0.35
        mascara_t = np.tile(mascara, (F, C))[..., None]

        c_vacio, c_sat, c_star = rgba(C_EJE, 0.35), rgba(TENUE, 0.95), rgba(C_SAT, 1.0)
        llen = ValueTracker(0.0)   # celdas visibles
        star = ValueTracker(0.0)   # celdas Starlink pintadas
        puls = ValueTracker(0.0)   # amplitud del pulso de maniobra
        reloj = ValueTracker(0.0)
        self._opac = opac = ValueTracker(1.0)

        idx = np.arange(F * C)
        es_sat = idx < self.N

        def lienzo():
            cel = np.tile(c_vacio, (F * C, 1))
            vis = np.zeros(F * C, dtype=bool)
            vis[:self.N] = orden_llenado < llen.get_value()
            cel[vis] = c_sat
            st = np.zeros(F * C, dtype=bool)
            st[:self.N] = idx[:self.N] < star.get_value()
            cel[st & vis] = c_star
            a = puls.get_value()
            if a > 0:
                fac = np.ones(F * C)
                osc = 0.5 + 0.5 * np.sin(reloj.get_value() * 3.2 + fase_p)
                fac[:self.N][maniobra] = 1 - a * 0.65 * osc[maniobra]
                cel[:, 3] = cel[:, 3] * np.where(vis, fac, 1.0)
            # columna-mayor -> imagen (fila, col)
            rej = cel.reshape(C, F, 4).transpose(1, 0, 2)
            img = np.repeat(np.repeat(rej, S, axis=0), S, axis=1) * mascara_t
            img[..., 3] *= opac.get_value()
            return img.astype(np.uint8)

        imagen = ImageMobject(lienzo())
        imagen.width = 8.0
        imagen.move_to([-2.3, -0.05, 0])
        imagen.add_updater(lambda m: setattr(m, "pixel_array", lienzo()))
        self._imagen = imagen
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)

        cont = texto_vivo(lambda: f"{llen.get_value():,.0f}", 64, TINTA, pos=[4.6, 2.35, 0])
        lab_act = et("Activos", 22, TENUE).move_to([4.6, 1.72, 0])
        self.play(FadeIn(imagen), FadeIn(cont), FadeIn(lab_act), FadeIn(chip_t), run_time=0.8)
        self.play(llen.animate.set_value(self.N), run_time=5.0, rate_func=smooth)
        cont.clear_updaters()
        cont.become(Text("16,279", font=FUENTE, font_size=64, color=TINTA).move_to([4.6, 2.35, 0]))
        self.wait(0.5)

        # Starlink: dos de cada tres
        cont_s = texto_vivo(lambda: f"{star.get_value():,.0f}", 46, C_SAT, pos=[4.6, 0.85, 0])
        lab_s = VGroup(et("Starlink", 24, C_SAT), et("66 %", 30, C_SAT)).arrange(RIGHT, buff=0.3)
        lab_s.move_to([4.6, 0.3, 0])
        self.add(cont_s)
        self.play(star.animate.set_value(self.N_STAR), run_time=3.0, rate_func=smooth)
        cont_s.clear_updaters()
        cont_s.become(Text("10,742", font=FUENTE, font_size=46, color=C_SAT).move_to([4.6, 0.85, 0]))
        self.play(FadeIn(lab_s, shift=UP * 0.1), run_time=0.6)
        self.wait(0.4)

        # 86.8 % maniobrables: se mueven a propósito
        man = VGroup(et("86.8 %", 42, TINTA), et("Maniobrables", 22, TENUE)).arrange(DOWN, buff=0.1)
        man.move_to([4.6, -0.75, 0])
        self.play(puls.animate.set_value(1.0), FadeIn(man, shift=UP * 0.1), run_time=1.2)
        self.wait(1.4)

        # un operador humano: su alcance es un círculo diminuto
        op = persona(0.8, C_ANT).move_to([3.55, -2.45, 0])
        lab_op = et("Un operador", 24, C_ANT).next_to(op, RIGHT, buff=0.25)
        alcance = Circle(radius=0.18, color=C_ANT, stroke_width=3.5, fill_color=C_ANT,
                         fill_opacity=0.15).move_to([1.05, -2.0, 0])
        hilo = DashedLine(op.get_left() + LEFT * 0.08, alcance.get_right(), color=C_ANT, stroke_width=2,
                          dash_length=0.08)
        self.play(FadeIn(op, shift=UP * 0.1), FadeIn(lab_op), run_time=0.7)
        self.play(Create(hilo), GrowFromCenter(alcance), run_time=0.9)
        self.play(Flash(alcance, color=C_ANT, flash_radius=0.4), run_time=0.7)
        self.wait(2.0)
        self.cierre()

    def cierre(self, t=0.6):
        """Como Pieza.cierre, pero la imagen (que se redibuja cada fotograma) se funde con su propio tracker."""
        if os.environ.get("CODE_FOTO"):
            return
        self.wait(1.2)
        otros = [m for m in self.mobjects if m is not self._imagen and not isinstance(m, ValueTracker)]
        self.play(self._opac.animate.set_value(0.0), *[FadeOut(m) for m in otros], run_time=t)
        self.wait(0.3)


# =============================================================================
# 5. La norma europea no nombra a la IA
# =============================================================================
class NormaSinIA(Pieza):
    def construct(self):
        rng = np.random.default_rng(43)
        chip_t = chip_tercero("ECSS oct-2025")
        dc = np.array([-4.45, 0.05, 0])
        doc = documento(3.3, 5.3, C_CIELO, 0.5, 0.08).move_to(dc)
        tit = et("ECSS-E-ST-70-11C", 22, C_CIELO).move_to(dc + [-0.15, 2.2, 0])
        rev = et("Rev.1", 20, TENUE).move_to(dc + [-0.15, 1.85, 0])
        lineas = VGroup()
        ys = np.linspace(1.45, -2.3, 20)
        xs0 = dc[0] - 1.35
        for k, y in enumerate(ys):
            w = rng.uniform(2.0, 2.7) if k % 6 != 5 else rng.uniform(0.9, 1.6)
            lineas.add(Line([xs0, dc[1] + y, 0], [xs0 + w, dc[1] + y, 0], color=TENUE, stroke_width=3,
                            stroke_opacity=0.45))
        # 81 apariciones de «autonomía» repartidas por el documento
        marcas = VGroup()
        for _ in range(81):
            k = rng.integers(0, 20)
            ln = lineas[k]
            x = rng.uniform(ln.get_start()[0] + 0.1, max(ln.get_end()[0] - 0.1, ln.get_start()[0] + 0.12))
            marcas.add(Rectangle(width=0.2, height=0.1, stroke_width=0, fill_color=C_ANT, fill_opacity=0.95)
                       .move_to([x, ln.get_start()[1], 0]))

        self.play(FadeIn(doc, shift=UP * 0.2), FadeIn(tit), FadeIn(rev), FadeIn(chip_t), run_time=1.0)
        self.play(LaggedStart(*[Create(l) for l in lineas], lag_ratio=0.05), run_time=1.0)

        # --- conteos ---
        filas = [("Autonomía", C_ANT), ("Inteligencia artificial", TINTA), ("Aprendizaje automático", TINTA),
                 ("Constelación", TINTA)]
        yf = [1.55, 0.45, -0.65, -1.75]
        xb0, L = 0.95, 4.2
        pistas, rotulos, conteos = VGroup(), VGroup(), []
        barrido = ValueTracker(0.0)   # 0 arriba … 1 abajo
        y_top, y_bot = dc[1] + 1.65, dc[1] - 2.5

        def y_barrido():
            return interpolate(y_top, y_bot, barrido.get_value())

        def n_auto():
            yb = y_barrido()
            return int(sum(1 for m in marcas if m.get_center()[1] >= yb))

        for (txt, col), y in zip(filas, yf):
            p = RoundedRectangle(corner_radius=0.1, width=L, height=0.5, color=C_EJE, stroke_width=2)
            p.move_to([xb0 + L / 2, y, 0])
            pistas.add(p)
            rotulos.add(et(txt, 24, col).next_to([xb0, y, 0], LEFT, buff=0.2))
        barra_a = always_redraw(lambda: Rectangle(
            width=max(1e-3, L * n_auto() / 81), height=0.5, stroke_width=0, fill_color=C_ANT,
            fill_opacity=0.85).move_to([xb0, yf[0], 0], aligned_edge=LEFT))
        cont_a = texto_vivo(lambda: f"{n_auto()}", 38, C_ANT, pos=[xb0 + L + 0.2, yf[0], 0], borde=LEFT)
        ceros = VGroup(*[et("0", 38, TINTA).next_to([xb0 + L + 0.2, y, 0], RIGHT, buff=0).shift(LEFT * 0.0)
                         for y in yf[1:]])
        for c0, y in zip(ceros, yf[1:]):
            c0.move_to([xb0 + L + 0.2, y, 0], aligned_edge=LEFT)

        self.play(LaggedStart(*[FadeIn(VGroup(r, p), shift=LEFT * 0.2) for r, p in zip(rotulos, pistas)],
                              lag_ratio=0.15), run_time=1.2)
        self.add(barra_a, cont_a)
        self.play(FadeIn(ceros), run_time=0.4)

        # barrido del documento: cada «autonomía» se enciende y suma
        linea_b = always_redraw(lambda: Line([dc[0] - 1.6, y_barrido(), 0], [dc[0] + 1.6, y_barrido(), 0],
                                             color=C_ANT, stroke_width=4))
        for m in marcas:
            m.add_updater(lambda mm: mm.set_fill(opacity=0.95 if mm.get_center()[1] >= y_barrido() else 0))
        self.add(marcas, linea_b)
        self.play(barrido.animate.set_value(1.0), run_time=6.5, rate_func=linear)
        self.play(FadeOut(linea_b), run_time=0.3)
        cont_a.clear_updaters()
        barra_a.clear_updaters()
        for m in marcas:
            m.clear_updaters()

        # las tres pistas vacías: cero
        self.play(*[p.animate.set_stroke(C_MAL, width=3) for p in pistas[1:]],
                  *[c0.animate.set_color(C_MAL).scale(1.35, about_edge=LEFT) for c0 in ceros], run_time=0.9)
        self.play(LaggedStart(*[Indicate(c0, color=C_MAL, scale_factor=1.3) for c0 in ceros], lag_ratio=0.25),
                  run_time=1.3)
        self.wait(1.6)
        self.cierre()


# =============================================================================
# 6. Los estándares se escriben ahora
# =============================================================================
class EstandaresEscribenAhora(Pieza):
    def construct(self):
        chip_t = chip_tercero("IETF, 3GPP, ETSI")

        def xm(anio):
            return -4.2 + (anio - 2026) * 3.0

        carriles = [("IETF", 1.35), ("3GPP", 0.05), ("ETSI", -1.25)]
        y_eje = -2.2
        rieles = VGroup(*[Line([-4.45, y, 0], [6.5, y, 0], color=C_EJE, stroke_width=2) for _, y in carriles])
        rot = VGroup(*[et(n, 28, C_ANT).move_to([-5.7, y, 0]) for n, y in carriles])
        eje = Line([-4.45, y_eje, 0], [6.5, y_eje, 0], color=TENUE, stroke_width=2)
        anios = VGroup()
        for a in range(2026, 2030):
            anios.add(Line([xm(a), y_eje - 0.08, 0], [xm(a), y_eje + 0.08, 0], color=TENUE, stroke_width=2),
                      et(str(a), 22, TENUE).move_to([xm(a), y_eje - 0.35, 0]))
        self.play(Create(rieles), FadeIn(rot), Create(eje), FadeIn(anios), FadeIn(chip_t), run_time=1.3)

        # etiqueta de tema con glifo de agente
        def glifo(c, r=0.09):
            g = VGroup(Dot(radius=r, color=c))
            for a in (90, 210, 330):
                v = np.array([np.cos(a * DEGREES), np.sin(a * DEGREES), 0])
                g.add(Line(v * r, v * r * 2.3, color=c, stroke_width=2), Dot(v * r * 2.6, radius=r * 0.45, color=c))
            return g
        tag_t = et("Agentes de red", 26, TINTA)
        tag = VGroup(glifo(C_ANT, 0.08), tag_t).arrange(RIGHT, buff=0.2)
        tag_caja = SurroundingRectangle(tag, buff=0.14, corner_radius=0.12, color=C_ANT, stroke_width=2,
                                        fill_color=C_ANT, fill_opacity=0.1)
        tag_g = VGroup(tag_caja, tag).move_to([-4.3, 2.75, 0])
        self.play(FadeIn(tag_g, shift=DOWN * 0.1), run_time=0.7)

        # documentos: año y carril
        hoy = 2026.74
        docs_def = {0: [2026.08, 2026.22, 2026.36, 2026.5, 2026.64, 2027.2, 2027.9, 2028.6],
                    1: [2026.15, 2026.5, 2027.25, 2027.85, 2028.45],
                    2: [2026.28, 2026.6, 2027.5, 2028.3]}
        cursor = ValueTracker(2025.9)
        bloques = VGroup()
        for k, (_, y) in enumerate(carriles):
            for a in docs_def[k]:
                futuro = a > hoy
                base = documento(0.42, 0.54, C_ANT if not futuro else TENUE, 0.13,
                                 0.3 if not futuro else 0.0, 2).move_to([xm(a), y, 0])
                tapa = base[0].copy().set_fill(FONDO, opacity=1).set_stroke(width=0)
                if futuro:
                    base = VGroup(*[DashedVMobject(p, num_dashes=12) for p in base])
                    base.set_stroke(TENUE, width=2)
                gl = glifo(C_ANT if not futuro else TENUE, 0.045).move_to([xm(a), y - 0.05, 0])
                d = VGroup(tapa, base, gl)
                d.anio, d.relleno = a, (0.0 if futuro else 0.3)
                d.puntos = [s for s in gl if isinstance(s, Dot)]
                bloques.add(d)

        def aparecer(m):
            v = float(np.clip((cursor.get_value() - m.anio) / 0.08, 0, 1))
            m.set_stroke(opacity=v)
            m[0].set_fill(opacity=v)
            m[1][0].set_fill(opacity=m.relleno * v)
            for p in m.puntos:
                p.set_fill(opacity=v)
        for b in bloques:
            aparecer(b)
            b.add_updater(aparecer)
        self.add(bloques)
        linea_c = always_redraw(lambda: Line([xm(cursor.get_value()), y_eje, 0], [xm(cursor.get_value()), 2.0, 0],
                                             color=C_SAT, stroke_width=3, stroke_opacity=0.9))
        self.play(FadeIn(linea_c), run_time=0.3)
        self.play(cursor.animate.set_value(hoy), run_time=4.0, rate_func=linear)

        # «Ahora»
        ahora = et("Ahora", 28, C_SAT).move_to([xm(hoy), 2.35, 0])
        punto = Dot([xm(hoy), y_eje, 0], radius=0.09, color=C_SAT)
        lab_b = et("Borradores", 20, TENUE).move_to([xm(2026.36), 1.35 + 0.5, 0])
        lab_e = et("Estudios", 20, TENUE).move_to([xm(2026.32), 0.05 + 0.5, 0])
        self.play(FadeIn(ahora, shift=DOWN * 0.15), GrowFromCenter(punto), FadeIn(lab_b), FadeIn(lab_e),
                  run_time=0.8)
        self.wait(0.8)

        # proyección hacia 2029 (punteada: aún no existe)
        linea_c.clear_updaters()
        fija = Line([xm(hoy), y_eje, 0], [xm(hoy), 2.0, 0], color=C_SAT, stroke_width=3)
        self.remove(linea_c)
        self.add(fija)
        fantasma = always_redraw(lambda: DashedLine([xm(cursor.get_value()), y_eje, 0],
                                                    [xm(cursor.get_value()), 2.0, 0], color=TENUE,
                                                    stroke_width=2, dash_length=0.1))
        self.add(fantasma)
        self.play(cursor.animate.set_value(2029.05), run_time=3.0, rate_func=smooth)
        self.remove(fantasma)
        for b in bloques:
            b.clear_updaters()
        lab_s = et("Especificaciones", 20, TENUE).move_to([xm(2027.85), 0.05 + 0.5, 0])

        xg = xm(2029.1)
        meta = DashedLine([xg, y_eje, 0], [xg, 2.0, 0], color=C_CIELO, stroke_width=3, dash_length=0.12)
        bandera = Polygon([xg, 2.0, 0], [xg + 0.75, 1.78, 0], [xg, 1.56, 0], color=C_CIELO, fill_color=C_CIELO,
                          fill_opacity=0.5, stroke_width=2)
        lab6 = et("6G", 20, TINTA).move_to([xg + 0.27, 1.78, 0])
        lab29 = et("2029", 30, C_CIELO).move_to([xg + 0.1, 2.35, 0])
        self.play(FadeIn(lab_s), Create(meta), FadeIn(bandera), FadeIn(lab6), FadeIn(lab29, shift=DOWN * 0.1),
                  run_time=1.0)
        # lo que se escribe hoy fija el vocabulario de mañana
        flechas = VGroup(*[Arrow([xm(hoy) + 0.35, y, 0], [xg - 0.2, y, 0], buff=0.05,
                                 color=C_SAT, stroke_width=2.5, max_tip_length_to_length_ratio=0.04,
                                 stroke_opacity=0.7)
                           for _, y in carriles])
        flechas.set_z_index(-1)
        actuales = VGroup(*[b for b in bloques if b.anio <= hoy])
        self.play(LaggedStart(*[GrowArrow(f) for f in flechas], lag_ratio=0.2),
                  Indicate(actuales, color=C_SAT, scale_factor=1.12), run_time=1.6)
        self.wait(1.8)
        self.cierre()


# =============================================================================
# 7. Busqué «satélite» en el borrador: cero
# =============================================================================
class BuscarSatelite(Pieza):
    def construct(self):
        rng = np.random.default_rng(44)
        chip_t = chip_tercero("IETF 2026")
        dc = np.array([-2.85, 0.25, 0])
        W, Hd = 5.5, 6.2
        doc = documento(W, Hd, TENUE, 0.55, 0.06).move_to(dc)
        tit = et("Borrador IETF", 26, TINTA).move_to(dc + [-0.3, Hd / 2 - 0.42, 0])
        xl, xr = dc[0] - W / 2 + 0.35, dc[0] + W / 2 - 0.35
        ys = np.linspace(dc[1] + Hd / 2 - 0.95, dc[1] - Hd / 2 + 0.35, 25)
        # palabras normativas reales del borrador (MUST / MUST NOT), en posiciones fijas
        normativas = {(3, 1): "DEBE", (8, 2): "NO DEBE", (14, 0): "NO DEBE", (19, 3): "DEBE", (23, 1): "DEBE"}
        palabras = VGroup()
        especiales = []
        for k, y in enumerate(ys):
            fin = xr if k % 6 != 5 else xl + rng.uniform(1.5, 3.0)
            x, j = xl, 0
            while x < fin - 0.25:
                if (k, j) in normativas:
                    txt = normativas[(k, j)]
                    t = Text(txt, font=FUENTE, font_size=21, color=C_CIELO, weight=BOLD)
                    w = t.width
                    blq = Rectangle(width=w, height=0.09, stroke_width=0, fill_color=TENUE, fill_opacity=0.5)
                    blq.move_to([x + w / 2, y, 0])
                    t.move_to(blq)
                    fondo = SurroundingRectangle(t, buff=0.04, stroke_width=0, fill_color=C_CIELO, fill_opacity=0.18)
                    especiales.append((blq, VGroup(fondo, t)))
                    palabras.add(blq)
                    x += w + 0.1
                else:
                    w = min(rng.uniform(0.2, 0.75), fin - x)
                    palabras.add(Rectangle(width=w, height=0.09, stroke_width=0, fill_color=TENUE,
                                           fill_opacity=0.5).move_to([x + w / 2, y, 0]))
                    x += w + 0.1
                j += 1

        self.play(FadeIn(doc, shift=UP * 0.2), FadeIn(tit), FadeIn(chip_t), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(p) for p in palabras], lag_ratio=0.002), run_time=1.0)

        # --- panel de búsqueda ---
        def buscador(texto, y):
            caja_ = RoundedRectangle(corner_radius=0.2, width=3.3, height=0.8, color=C_ANT, stroke_width=2.5,
                                     fill_color=C_ANT, fill_opacity=0.08).move_to([3.5, y, 0])
            ic = lupa(0.13, C_ANT).move_to(caja_.get_left() + RIGHT * 0.42)
            t = et(texto, 30, TINTA).next_to(ic, RIGHT, buff=0.28)
            return VGroup(caja_, ic, t)
        b1 = buscador("satélite", 2.35)
        b2 = buscador("NTN", 1.2)
        c1 = et("0", 46, TINTA).move_to([5.85, 2.35, 0])
        c2 = et("0", 46, TINTA).move_to([5.85, 1.2, 0])
        prog_marco = RoundedRectangle(corner_radius=0.06, width=4.6, height=0.14, color=C_EJE, stroke_width=1.5)
        prog_marco.move_to([4.05, 0.3, 0])
        s = ValueTracker(0.0)
        prog = always_redraw(lambda: Rectangle(width=max(1e-3, 4.6 * s.get_value()), height=0.14, stroke_width=0,
                                               fill_color=C_ANT, fill_opacity=0.8)
                             .move_to(prog_marco.get_left(), aligned_edge=LEFT))
        self.play(FadeIn(b1, shift=LEFT * 0.2), FadeIn(c1), run_time=0.6)
        self.play(FadeIn(b2, shift=LEFT * 0.2), FadeIn(c2), FadeIn(prog_marco), FadeIn(prog), run_time=0.6)

        # --- la lupa recorre el documento en zigzag ---
        filas_l = ys[1::3]
        pts = []
        for i, y in enumerate(filas_l):
            a, b = (xl + 0.3, xr - 0.3) if i % 2 == 0 else (xr - 0.3, xl + 0.3)
            pts += [[a, y, 0], [b, y, 0]]
        ruta = VMobject().set_points_as_corners(pts)
        lente = lupa(0.45, TINTA)
        desf = lente[0].get_center() - lente.get_center()
        lente.add_updater(lambda m: m.move_to(ruta.point_from_proportion(s.get_value()) - desf))
        lente.set_z_index(3)
        revelados = set()

        def revisar(_):
            c = ruta.point_from_proportion(s.get_value())
            for i, (blq, etq) in enumerate(especiales):
                if i not in revelados and np.linalg.norm(blq.get_center() - c) < 0.55:
                    revelados.add(i)
                    blq.set_fill(opacity=0)
                    self.add(etq)
        vigia = Mobject()
        vigia.add_updater(revisar)
        self.add(vigia)
        self.play(FadeIn(lente), run_time=0.4)
        self.add(lente)
        self.play(s.animate.set_value(1.0), run_time=8.5, rate_func=linear)
        vigia.clear_updaters()
        lente.clear_updaters()
        prog.clear_updaters()
        self.play(FadeOut(lente), run_time=0.4)

        # cero, en grande
        gran = Text("0", font=FUENTE, font_size=150, color=C_MAL).move_to([4.05, -1.75, 0])
        self.play(ReplacementTransform(c1.copy(), gran), c1.animate.set_color(C_MAL), c2.animate.set_color(C_MAL),
                  run_time=1.0)
        self.play(Indicate(c2, color=C_MAL, scale_factor=1.3), run_time=0.7)
        self.wait(1.8)
        self.cierre()

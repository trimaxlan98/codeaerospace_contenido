"""Comité tutorial, bloques 7–8: alcance del banco, supuesto A0, plan G3, cronograma, contribuciones y cierre."""
from tesis_lib import *
import numpy as np


# ---------- helpers propios de este archivo ----------
def punteado(m, n=None, color=None, ancho=2.5, op=1.0, ratio=0.55):
    """Versión punteada de un VMobject (pendiente / planeado / propuesto)."""
    if n is None:
        n = max(12, int(m.get_arc_length() / 0.16)) if hasattr(m, "get_arc_length") else 40
    d = DashedVMobject(m, num_dashes=n, dashed_ratio=ratio)
    d.set_stroke(color or TENUE, width=ancho, opacity=op)
    return d


def marco_punteado(ancho, alto, color=None, ancho_trazo=2.5, radio=0.12, op=1.0):
    r = RoundedRectangle(corner_radius=radio, width=ancho, height=alto)
    n = int(2 * (ancho + alto) / 0.17)
    return punteado(r, n, color, ancho_trazo, op)


def pastilla(texto, color, tam=20, relleno=0.14, pad=(0.36, 0.22), texto_color=None):
    t = et(texto, tam, texto_color or TINTA)
    r = RoundedRectangle(corner_radius=0.12, width=t.width + 2 * pad[0], height=t.height + 2 * pad[1],
                         color=color, fill_color=color, fill_opacity=relleno, stroke_width=2.2)
    t.move_to(r)
    return VGroup(r, t)


def pastilla_punteada(texto, color, tam=20, pad=(0.36, 0.22), texto_color=None, alto=None):
    t = et(texto, tam, texto_color or color)
    h = alto or (t.height + 2 * pad[1])
    r = marco_punteado(t.width + 2 * pad[0], h, color, 2.2)
    t.move_to(r)
    return VGroup(r, t)


def sello(texto, color, tam=44, ang=10):
    """Sello de goma: doble marco + texto, girado."""
    t = et(texto, tam, color)
    r1 = RoundedRectangle(corner_radius=0.1, width=t.width + 0.6, height=t.height + 0.46,
                          color=color, stroke_width=5, fill_color=color, fill_opacity=0.06)
    r2 = RoundedRectangle(corner_radius=0.07, width=t.width + 0.38, height=t.height + 0.24,
                          color=color, stroke_width=2)
    g = VGroup(r1, r2, t.move_to(r1))
    return g.rotate(ang * DEGREES)


def documento(ancho=0.75, alto=0.95, color=None, lineas=3):
    c = color or TINTA
    hoja = Polygon([-ancho / 2, -alto / 2, 0], [ancho / 2, -alto / 2, 0], [ancho / 2, alto / 2 - 0.2, 0],
                   [ancho / 2 - 0.2, alto / 2, 0], [-ancho / 2, alto / 2, 0],
                   color=c, stroke_width=2.2, fill_color=c, fill_opacity=0.08)
    g = VGroup(hoja)
    for k in range(lineas):
        y = alto / 2 - 0.32 - k * 0.2
        g.add(Line([-ancho / 2 + 0.13, y, 0], [ancho / 2 - 0.16, y, 0], color=c, stroke_width=2, stroke_opacity=0.7))
    return g


def reloj_icono(r=0.2, color=None):
    c = color or TENUE
    return VGroup(Circle(radius=r, color=c, stroke_width=2.5),
                  Line(ORIGIN, UP * r * 0.7, color=c, stroke_width=2.5),
                  Line(ORIGIN, RIGHT * r * 0.55, color=c, stroke_width=2.5))


def rombo(pos, tam=0.13, color=None, relleno=0.9):
    c = color or C_OK
    return Square(tam * 1.414, color=c, fill_color=c, fill_opacity=relleno, stroke_width=1.5).rotate(PI / 4).move_to(pos)


def insignia_ok(pos=ORIGIN, r=0.2, color=None):
    """Marca de compuerta: círculo verde con ✓."""
    c = color or C_OK
    circ = Circle(radius=r, color=c, fill_color=FONDO, fill_opacity=1, stroke_width=3).move_to(pos)
    return VGroup(circ, marca_ok(pos + RIGHT * 0.01, tam=r * 1.15, color=c))


# =============================================================================
# 1. Alcance del banco: instancia mínima + comparador que falta
# =============================================================================
class AlcanceDelBanco(Pieza):
    def construct(self):
        GW = np.array([-2.0, -2.3, 0])
        TOPE_GW = GW + UP * 0.5
        R = 4.0

        def pos(th):
            return GW + R * np.array([np.cos(th * DEGREES), np.sin(th * DEGREES), 0])

        th_a = ValueTracker(118)   # ángulo del satélite A
        cg = ValueTracker(0.0)     # nivel de congestión del gateway (0..1)
        ch = ValueTracker(0.0)     # canal degradado: 0 → canal 0, 1 → canal 1

        def vis(th):
            return 1 - 0.78 * suave((th - 136) / 16)

        hor = Line([-6.4, GW[1], 0], [1.3, GW[1], 0], color=C_EJE, stroke_width=2.5)
        orb = punteado(Arc(radius=R, start_angle=36 * DEGREES, angle=128 * DEGREES, arc_center=GW),
                       70, C_EJE, 1.6, 0.9)
        zona = AnnularSector(inner_radius=R - 0.45, outer_radius=R + 0.45, angle=26 * DEGREES,
                             start_angle=140 * DEGREES, arc_center=GW,
                             fill_color=C_EJE, fill_opacity=0.7 if OSCURO else 0.45, stroke_width=0).set_z_index(-2)

        gw = estacion(0.62, C_ANT).move_to(GW, aligned_edge=DOWN)
        sat_a = satelite(0.24, C_SAT).move_to(pos(118))
        sat_b = satelite(0.24, C_SAT).move_to(pos(60))
        sat_a.add_updater(lambda m: m.move_to(pos(th_a.get_value())))

        # --- dos canales por satélite; el degradado rota entre ellos ---
        def enlaces(fuente, fvis):
            def f():
                a = fuente.get_center()
                b = TOPE_GW
                d = b - a
                n = np.array([-d[1], d[0], 0]) / (np.linalg.norm(d) + 1e-9)
                v = fvis()
                g = VGroup()
                for k, s in enumerate((-1, 1)):
                    w_deg = (1 - ch.get_value()) if k == 0 else ch.get_value()
                    col = interpolate_color(ManimColor(C_ANT), ManimColor(C_MAL), w_deg)
                    op = (0.95 - 0.3 * w_deg) * v
                    g.add(Line(a + n * 0.075 * s + d * 0.08, b + n * 0.075 * s, color=col,
                               stroke_width=3.2 - 1.4 * w_deg, stroke_opacity=op))
                return g
            return f

        enl_a = always_redraw(enlaces(sat_a, lambda: vis(th_a.get_value())))
        enl_b = always_redraw(enlaces(sat_b, lambda: 1.0))

        # --- 3 acciones por agente (una elegida) ---
        def ranuras(color):
            g = VGroup(*[Square(0.2, color=color, stroke_width=2, fill_color=color, fill_opacity=0.08)
                         for _ in range(3)]).arrange(RIGHT, buff=0.08)
            return g

        r_a = ranuras(C_SAT)
        r_a.add_updater(lambda m: m.move_to(sat_a.get_center() + DOWN * 0.42))
        r_b = ranuras(C_SAT).move_to(sat_b.get_center() + DOWN * 0.42)
        r_g = ranuras(C_ANT).move_to(GW + np.array([-0.95, 0.22, 0]))

        def elige(r, k, color):
            return [sq.animate.set_fill(color, opacity=0.85 if i == k else 0.08) for i, sq in enumerate(r)]

        # --- congestión del gateway: medidor vertical ---
        med_marco = Rectangle(width=0.22, height=0.85, color=C_EJE, stroke_width=2).move_to(GW + np.array([0.62, 0.43, 0]))

        def med_f():
            v = cg.get_value()
            h = 0.08 + 0.75 * v
            col = interpolate_color(ManimColor(C_ANT), ManimColor(C_MAL), suave((v - 0.3) / 0.4))
            return Rectangle(width=0.16, height=h, stroke_width=0, fill_color=col, fill_opacity=0.9).move_to(
                med_marco.get_bottom() + UP * (h / 2 + 0.03))
        med = always_redraw(med_f)

        l_sats = et("2 satélites", 24, C_SAT).move_to([-2.0, 2.4, 0])
        l_gw = et("1 gateway", 22, C_ANT).move_to([-2.45, -2.72, 0])
        l_acc = et("3 acciones", 22, TENUE).next_to(r_g, LEFT, buff=0.3)
        l_vis = et("Visibilidad", 22, TINTA).move_to([-5.45, 0.8, 0])
        l_cg = et("Congestión", 22, TINTA).move_to([-0.75, -2.72, 0])
        l_ch = et("Canal rotante", 22, TINTA).move_to([0.2, -0.45, 0])

        chip_d = chip_desarrollo()
        self.play(Create(hor), FadeIn(gw, shift=UP * 0.2), FadeIn(chip_d), run_time=0.9)
        self.play(Create(orb), FadeIn(sat_a, scale=0.6), FadeIn(sat_b, scale=0.6), run_time=1.0)
        self.add(enl_a, enl_b)
        self.play(FadeIn(l_sats, shift=DOWN * 0.1), FadeIn(l_gw, shift=UP * 0.1), run_time=0.7)
        self.play(LaggedStart(FadeIn(r_a), FadeIn(r_b), FadeIn(r_g), lag_ratio=0.25),
                  FadeIn(l_acc), run_time=0.9)
        self.play(*elige(r_a, 0, C_SAT), *elige(r_b, 1, C_SAT), *elige(r_g, 0, C_ANT), run_time=0.5)
        self.respiro(0.3)

        # Mecanismo 1: ventana de visibilidad
        self.play(FadeIn(zona), run_time=0.5)
        self.play(th_a.animate.set_value(158), run_time=2.2, rate_func=smooth)
        self.play(*elige(r_a, 2, C_SAT), FadeIn(l_vis, shift=RIGHT * 0.1), run_time=0.6)
        self.respiro(0.3)

        # Mecanismo 2: congestión variable del gateway
        self.play(FadeIn(med_marco), FadeIn(med), run_time=0.4)
        self.play(cg.animate.set_value(1.0), FadeIn(l_cg, shift=UP * 0.1), run_time=1.3, rate_func=smooth)
        self.play(*elige(r_g, 1, C_ANT), run_time=0.4)
        self.play(cg.animate.set_value(0.25), run_time=0.8, rate_func=smooth)

        # Mecanismo 3: canal degradado rotante
        self.play(ch.animate.set_value(1.0), FadeIn(l_ch, shift=LEFT * 0.1), run_time=1.5, rate_func=smooth)
        self.play(*elige(r_b, 0, C_SAT), run_time=0.4)

        # Encuadre: instancia mínima (no gemelo de alta fidelidad)
        caja_inst = marco_punteado(8.0, 6.05, TENUE, 2).move_to([-2.55, -0.2, 0])
        l_inst = et("Instancia mínima", 22, TENUE).next_to(caja_inst, UP, buff=0.12).align_to(caja_inst, LEFT).shift(RIGHT * 0.1)
        self.play(Create(caja_inst), FadeIn(l_inst), cg.animate.set_value(0.9),
                  ch.animate.set_value(0.0), run_time=1.6, rate_func=smooth)
        self.play(*elige(r_b, 1, C_SAT), *elige(r_g, 0, C_ANT), cg.animate.set_value(0.35), run_time=0.7)

        # Comparadores del brazo de G3 (pendiente) y la ranura vacía
        cont = marco_punteado(4.4, 5.75, TENUE, 2).move_to([4.25, 0.05, 0])
        l_g3 = et("Brazo G3", 22, TENUE).move_to([4.25, 2.5, 0])
        filas = VGroup(
            caja("QMIX", 3.2, 0.6, C_SAT, 22),
            caja("DTDE", 3.2, 0.6, C_ANT, 22),
            caja("Heurística", 3.2, 0.6, C_ANT, 22),
            caja("Estática", 3.2, 0.6, TENUE, 22),
        ).arrange(DOWN, buff=0.2).move_to([4.25, 0.5, 0])
        hueco = marco_punteado(3.2, 0.6, C_MAL, 2.6).next_to(filas, DOWN, buff=0.2)
        l_falta = et("Falta MAPPO", 22, C_MAL).move_to(hueco)
        tab = pastilla("Propuesto", C_CIELO, 18, 0.14, (0.25, 0.1), C_CIELO).next_to(hueco, DOWN, buff=0.12)

        self.play(Create(cont), FadeIn(l_g3), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(f, shift=LEFT * 0.2) for f in filas], lag_ratio=0.2), run_time=1.3)
        self.play(Create(hueco), run_time=0.7)
        self.play(FadeIn(l_falta, scale=0.9), run_time=0.5)
        self.play(Indicate(VGroup(hueco, l_falta), color=C_MAL, scale_factor=1.06), run_time=0.9)
        self.play(FadeIn(tab, shift=UP * 0.15), run_time=0.6)
        self.wait(0.9)
        self.cierre()


# =============================================================================
# 2. Supuesto A0: una autoridad (Dec-POMDP) vs dos operadores (POSG)
# =============================================================================
class SupuestoA0(Pieza):
    def construct(self):
        fase = ValueTracker(0.0)
        reloj = Mobject()
        reloj.add_updater(lambda m, dt: fase.increment_value(dt))
        self.add(reloj)

        R = 1.3
        CL = np.array([-3.7, 0.95, 0])
        C1 = np.array([2.65, 0.95, 0])
        C2 = np.array([4.45, 0.95, 0])
        N = 6

        def pos(c, k, sentido=1, off=0.0, vel=0.35):
            a = off + sentido * vel * fase.get_value() + TAU * k / N
            return c + R * np.array([np.cos(a), np.sin(a), 0])

        def constelacion(c, color, sentido, off):
            anillo = Circle(radius=R, color=color, stroke_width=1.6, stroke_opacity=0.5).move_to(c)
            sats = VGroup()
            for k in range(N):
                s = satelite(0.13, color)
                s.add_updater(lambda m, k=k: m.move_to(pos(c, k, sentido, off)))
                sats.add(s)
            aut = VGroup(RegularPolygon(6, color=color, fill_color=color, fill_opacity=0.85, stroke_width=2).scale(0.2),
                         Circle(radius=0.32, color=color, stroke_width=2)).move_to(c)
            rayos = always_redraw(lambda: VGroup(*[Line(c, pos(c, k, sentido, off), color=color,
                                                         stroke_width=1.3, stroke_opacity=0.45).set_z_index(-1)
                                                    for k in range(N)]))
            return anillo, sats, aut, rayos

        # ---- lado izquierdo: una autoridad ----
        an, ss, aut, ray = constelacion(CL, C_SAT, 1, 0.0)
        l_una = et("Una autoridad", 24, C_SAT).move_to([-3.7, 2.8, 0])
        dec = caja("Dec-POMDP", 2.6, 0.66, C_SAT, 24).move_to([-3.7, -2.3, 0])
        fl_dec = flecha(CL + DOWN * (R + 0.25), dec.get_top() + UP * 0.05, C_SAT, 3)
        l_a0 = pastilla("Supuesto A0", C_SAT, 20, 0.12, (0.22, 0.1), C_SAT).next_to(fl_dec, LEFT, buff=0.18)

        chip_s = chip("Supuesto declarado", C_SAT)
        self.play(Create(an), FadeIn(aut, scale=0.5), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in ss], lag_ratio=0.12), run_time=1.0)
        self.add(ray)
        self.play(FadeIn(l_una, shift=DOWN * 0.1), run_time=0.6)
        self.play(GrowArrow(fl_dec), FadeIn(dec, shift=UP * 0.15), run_time=1.0)
        self.play(FadeIn(l_a0, shift=RIGHT * 0.1), FadeIn(chip_s), run_time=0.8)
        self.respiro(0.4)

        # ---- lado derecho: dos operadores que se solapan ----
        an1, ss1, au1, ra1 = constelacion(C1, C_SAT, 1, 0.3)
        an2, ss2, au2, ra2 = constelacion(C2, C_CIELO, -1, 0.0)
        l_dos = et("Dos operadores", 24, TINTA).move_to([3.55, 2.8, 0])

        def interferencia():
            g = VGroup()
            for a in ss1:
                for b in ss2:
                    pa, pb = a.get_center(), b.get_center()
                    d = np.linalg.norm(pa - pb)
                    if d < 1.05:
                        k = 1 - d / 1.05
                        m = (pa + pb) / 2
                        v = (pb - pa) / (d + 1e-9)
                        n = np.array([-v[1], v[0], 0])
                        zz = [pa + v * 0.18]
                        for j in range(1, 6):
                            zz.append(pa + v * (0.18 + (d - 0.36) * j / 6) + n * 0.11 * (-1) ** j)
                        zz.append(pb - v * 0.18)
                        z = VMobject().set_points_as_corners(zz)
                        z.set_stroke(C_MAL, width=2.5 + 3 * k, opacity=0.45 + 0.55 * k)
                        g.add(z, Dot(m, radius=0.06 + 0.16 * k, color=C_MAL, fill_opacity=0.45 * k))
            return g
        intf = always_redraw(interferencia)

        self.play(Create(an1), Create(an2), FadeIn(au1, scale=0.5), FadeIn(au2, scale=0.5), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in list(ss1) + list(ss2)], lag_ratio=0.06), run_time=1.1)
        self.add(ra1, ra2, intf)
        self.play(FadeIn(l_dos, shift=DOWN * 0.1), run_time=0.6)
        self.wait(2.6)

        posg = caja("POSG", 2.0, 0.66, C_CIELO, 24).move_to([3.55, -2.3, 0])
        fl_cl = flecha(dec.get_right() + RIGHT * 0.15, posg.get_left() + LEFT * 0.15, TENUE, 3)
        l_sin = et("Sin A0", 20, TENUE).next_to(fl_cl, UP, buff=0.1)
        self.play(GrowArrow(fl_cl), FadeIn(l_sin), run_time=0.9)
        self.play(FadeIn(posg, shift=LEFT * 0.15), run_time=0.6)

        # ---- banda compartida: degradación, umbral y reparto impuesto ----
        X0, X1, YB, HB = 1.55, 5.55, -1.1, 0.3
        dg = ValueTracker(0.0)
        xm = (X0 + X1) / 2

        def banda():
            d = dg.get_value()
            w = (X1 - X0)
            solape = 0.15 + 1.25 * d
            a_fin = xm + solape / 2
            b_ini = xm - solape / 2
            g = VGroup(
                Rectangle(width=a_fin - X0, height=HB, stroke_width=0, fill_color=C_SAT, fill_opacity=0.9)
                .move_to([(X0 + a_fin) / 2, YB, 0]),
                Rectangle(width=X1 - b_ini, height=HB, stroke_width=0, fill_color=C_CIELO, fill_opacity=0.9)
                .move_to([(b_ini + X1) / 2, YB, 0]),
                Rectangle(width=solape, height=HB + 0.08, stroke_width=0, fill_color=C_MAL, fill_opacity=0.95)
                .move_to([xm, YB, 0]),
            )
            return g
        bnd = always_redraw(banda)
        UMB = 0.5
        tk = VGroup(*[DashedLine([xm + s * UMB, YB - 0.3, 0], [xm + s * UMB, YB + 0.3, 0], color=TINTA,
                                 stroke_width=2.5, dash_length=0.06) for s in (-1, 1)]).set_z_index(3)
        l_umb = et("Umbral", 20, TENUE).move_to([xm, YB - 0.48, 0])
        self.play(FadeIn(bnd), run_time=0.6)
        self.play(Create(tk), FadeIn(l_umb), run_time=0.6)
        self.play(dg.animate.set_value(1.0), run_time=2.0, rate_func=smooth)

        # el regulador supone rivales: impone el reparto
        chip_r = chip_tercero("47 CFR 25.261")
        self.play(FadeIn(chip_r, shift=UP * 0.15), Flash(np.array([xm, YB, 0]), color=C_MAL, line_length=0.25), run_time=0.7)
        izq = Rectangle(width=(X1 - X0) / 2 - 0.08, height=HB, stroke_width=0, fill_color=C_SAT,
                        fill_opacity=0.9).move_to([(X0 + xm) / 2 - 0.04, YB, 0])
        der = Rectangle(width=(X1 - X0) / 2 - 0.08, height=HB, stroke_width=0, fill_color=C_CIELO,
                        fill_opacity=0.9).move_to([(xm + X1) / 2 + 0.04, YB, 0])
        corte = Line([xm, YB - 0.28, 0], [xm, YB + 0.28, 0], color=TINTA, stroke_width=3)
        l_rep = et("Reparto", 20, TINTA).move_to(l_umb)
        bnd.clear_updaters()
        rojo_fin = Rectangle(width=0.01, height=HB, stroke_width=0, fill_color=C_MAL, fill_opacity=0).move_to([xm, YB, 0])
        self.play(Transform(bnd, VGroup(izq, der, rojo_fin)),
                  FadeOut(tk), Create(corte), ReplacementTransform(l_umb, l_rep), run_time=1.2)
        self.wait(2.4)
        self.cierre()


# =============================================================================
# 3. Plan G3 reforzada (propuesto)
# =============================================================================
class PlanG3Reforzada(Pieza):
    def construct(self):
        Y = 1.95
        chip_p = chip("Propuesto", C_CIELO)
        self.add(chip_p)

        # pre-registro fechado (va antes de correr)
        doc = documento(0.78, 0.98, TINTA).move_to([-5.55, Y, 0])
        l_pre = et("Pre-registro", 20, TINTA).next_to(doc, DOWN, buff=0.18)
        estampa = VGroup(Circle(radius=0.26, color=C_OK, stroke_width=3.5, fill_color=FONDO, fill_opacity=0.9),
                         marca_ok(ORIGIN, 0.3, C_OK)).move_to(doc.get_corner(DR) + np.array([0.02, 0.1, 0]))

        g3 = VGroup(marco_punteado(2.35, 0.9, C_SAT, 2.8),
                    et("G3 reforzada", 22, TINTA)).move_to([-2.75, Y, 0])
        g3[1].move_to(g3[0])
        v3 = VGroup(marco_punteado(2.1, 0.9, C_CIELO, 2.8), et("NTNEnv-v3", 22, TINTA)).move_to([0.2, Y, 0])
        v3[1].move_to(v3[0])
        m4 = VGroup(marco_punteado(1.55, 0.9, TENUE, 2.4), et("MVP4", 22, TENUE)).move_to([2.95, Y, 0])
        m4[1].move_to(m4[0])
        m5 = VGroup(marco_punteado(1.55, 0.9, TENUE, 2.4), et("MVP5", 22, TENUE)).move_to([5.3, Y, 0])
        m5[1].move_to(m5[0])
        t_v3 = et("2027-H1", 20, C_CIELO).next_to(v3, UP, buff=0.18)
        t_m4 = et("2027", 20, TENUE).next_to(m4, UP, buff=0.18)
        t_m5 = et("2028", 20, TENUE).next_to(m5, UP, buff=0.18)
        f1p = et("F1′", 22, C_CIELO).next_to(v3, DOWN, buff=0.15)

        def fl(a, b):
            return flecha(a.get_right() + RIGHT * 0.1, b.get_left() + LEFT * 0.1, TENUE, 2.5, 0.16)

        f0 = flecha(doc.get_right() + RIGHT * 0.32, g3.get_left() + LEFT * 0.1, TENUE, 2.5, 0.16)
        f1, f2, f3 = fl(g3, v3), fl(v3, m4), fl(m4, m5)

        # 1) el pre-registro se sella primero
        self.play(FadeIn(doc, shift=UP * 0.15), FadeIn(l_pre), run_time=0.8)
        estampa.scale(1.8).set_opacity(0)
        self.play(estampa.animate.scale(1 / 1.8).set_opacity(1), run_time=0.45, rate_func=rush_into)
        self.play(Flash(estampa, color=C_OK, line_length=0.18, flash_radius=0.35), run_time=0.5)
        # 2) después, G3
        self.play(GrowArrow(f0), run_time=0.5)
        self.play(FadeIn(g3, shift=DOWN * 0.2), run_time=0.7)

        # detalle de G3 (callout)
        PX = -1.7
        panel = RoundedRectangle(corner_radius=0.16, width=9.4, height=3.35, color=C_SAT, stroke_width=1.8,
                                 fill_color=C_PANEL, fill_opacity=0.45).move_to([PX, -1.28, 0])
        guia = VGroup(DashedLine(g3.get_corner(DL), panel.get_corner(UL) + RIGHT * 0.9, color=C_SAT,
                                 stroke_width=1.6, dash_length=0.08),
                      DashedLine(g3.get_corner(DR), panel.get_corner(UR) + LEFT * 2.6, color=C_SAT,
                                 stroke_width=1.6, dash_length=0.08))
        pd = (0.26, 0.2)
        fila1 = VGroup(pastilla("30k pasos", C_SAT, 20, pad=pd), pastilla("10 semillas", C_SAT, 20, pad=pd),
                       pastilla("IPPO/MAPPO", C_CIELO, 20, pad=pd), pastilla("Heurística en malla", C_ANT, 20, pad=pd)
                       ).arrange(RIGHT, buff=0.18).move_to([PX, -0.1, 0])
        prim = VGroup(*[pastilla(t, C_ANT, 20, 0.3) for t in ("Throughput", "p99", "SLA", "Jain")]).arrange(RIGHT, buff=0.16)
        sec = pastilla("Recompensa", TENUE, 18, 0.08, texto_color=TENUE)
        fila2 = VGroup(prim, sec).arrange(RIGHT, buff=0.55).move_to([PX, -1.08, 0])
        l_prim = et("Primarias", 18, C_ANT).next_to(prim, DOWN, buff=0.12)
        l_sec = et("Secundaria", 18, TENUE).next_to(sec, DOWN, buff=0.12)
        reloj = reloj_icono(0.24, TINTA)
        l_h = et("55–110 h", 24, TINTA)
        fila3 = VGroup(reloj, l_h).arrange(RIGHT, buff=0.2).move_to([PX, -2.45, 0])

        self.play(Create(guia), FadeIn(panel), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.15) for p in fila1], lag_ratio=0.35), run_time=2.2)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.15) for p in prim], lag_ratio=0.2),
                  FadeIn(l_prim), run_time=1.3)
        self.play(FadeIn(sec, shift=UP * 0.1), FadeIn(l_sec), run_time=0.7)
        self.play(FadeIn(reloj, scale=0.6), FadeIn(l_h, shift=LEFT * 0.1), run_time=1.0)
        self.respiro(0.9)

        # 3) NTNEnv-v3 (2027-H1, F1′) y después MVP4–MVP5
        self.play(GrowArrow(f1), run_time=0.5)
        self.play(FadeIn(v3, shift=DOWN * 0.2), FadeIn(t_v3), run_time=0.7)
        self.play(FadeIn(f1p, shift=UP * 0.1), run_time=0.5)
        self.respiro(0.6)
        self.play(GrowArrow(f2), FadeIn(m4, shift=DOWN * 0.2), FadeIn(t_m4), run_time=0.8)
        self.play(GrowArrow(f3), FadeIn(m5, shift=DOWN * 0.2), FadeIn(t_m5), run_time=0.8)

        # 4) sello permanente
        s = sello("Propuesto", C_CIELO, 46, 9).move_to([4.9, -1.25, 0])
        self.play(FadeIn(s, scale=1.7), run_time=0.45, rate_func=rush_into)
        self.play(s.animate.shift(DOWN * 0.03), run_time=0.15)
        self.wait(3.2)
        self.cierre()


# =============================================================================
# 4. Cronograma doctoral feb-2026 → feb-2030
# =============================================================================
class CronogramaDoctoral(Pieza):
    def construct(self):
        X0, X1 = -5.2, 6.4
        MES = (X1 - X0) / 48.0

        def xm(m):
            return X0 + m * MES

        filas = ["MVP1", "MVP2", "MVP3", "MVP4", "MVP5", "Defensa"]
        ys = [2.2, 1.3, 0.4, -0.5, -1.4, -2.3]
        H = 0.42
        Y_EJE = -2.85
        HOY = 7.93      # 29-sep-2026 (feb-2026 = 0)
        WIT = 9.1       # 2–6 nov 2026

        chip_p = chip("Plan propuesto", C_CIELO, esquina=UR)

        # ejes: rejilla por año y semestres
        eje = Line([X0, Y_EJE, 0], [X1, Y_EJE, 0], color=C_EJE, stroke_width=2.5)
        rej = VGroup()
        for m in (11, 23, 35, 47):
            rej.add(DashedLine([xm(m), Y_EJE, 0], [xm(m), 2.75, 0], color=C_EJE, stroke_width=1.2,
                               dash_length=0.08, stroke_opacity=0.8))
        sem = VGroup(*[Line([xm(m), Y_EJE - 0.08, 0], [xm(m), Y_EJE + 0.08, 0], color=C_EJE, stroke_width=2)
                       for m in range(0, 49, 6)])
        anios = VGroup()
        for a, (m0, m1) in zip(("2026", "2027", "2028", "2029"), ((0, 11), (11, 23), (23, 35), (35, 47))):
            anios.add(et(a, 20, TENUE).move_to([xm((m0 + m1) / 2), Y_EJE - 0.3, 0]))
        etqs = VGroup(*[et(f, 22, TINTA).move_to([X0 - 0.2, y, 0], aligned_edge=RIGHT) for f, y in zip(filas, ys)])

        self.play(Create(eje), FadeIn(sem), FadeIn(anios), FadeIn(chip_p), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(e, shift=RIGHT * 0.1) for e in etqs], lag_ratio=0.12),
                  FadeIn(rej), run_time=1.0)

        def barra_h(m0, m1, y, color, op=0.75):
            return Rectangle(width=(m1 - m0) * MES, height=H, stroke_width=2, color=color,
                             fill_color=color, fill_opacity=op).move_to([(xm(m0) + xm(m1)) / 2, y, 0])

        # barras completadas y en curso se «rellenan» al pasar la línea de progreso
        tr = ValueTracker(0.0)
        hechas = [(0, 4, ys[0], C_OK), (3, 5, ys[1], C_OK), (4, HOY, ys[2], C_ANT)]

        def relleno():
            g = VGroup()
            t = tr.get_value()
            for m0, m1, y, c in hechas:
                if t > m0:
                    g.add(barra_h(m0, min(t, m1), y, c))
            return g
        rel = always_redraw(relleno)
        linea = always_redraw(lambda: Line([xm(tr.get_value()), Y_EJE, 0], [xm(tr.get_value()), 2.75, 0],
                                           color=C_SAT, stroke_width=3))
        self.add(rel, linea)
        self.play(tr.animate.set_value(HOY), run_time=4.0, rate_func=smooth)

        oks = VGroup(marca_ok(np.array([xm(4) + 0.3, ys[0], 0]), 0.3), marca_ok(np.array([xm(5) + 0.3, ys[1], 0]), 0.3))
        # compuertas G0–G2b dentro de MVP3 (jun–jul 2026)
        gates = VGroup(*[rombo([xm(m), ys[2], 0], 0.12, C_OK).set_stroke(FONDO, 1.5) for m in (4.3, 4.37, 5.73)])
        l_gates = et("G0–G2b", 18, C_OK).move_to([xm(5.0), ys[2] + H / 2 + 0.2, 0])
        self.play(LaggedStart(*[Create(o) for o in oks], lag_ratio=0.4),
                  LaggedStart(*[FadeIn(g, scale=0.4) for g in gates], lag_ratio=0.3), run_time=1.0)
        self.play(FadeIn(l_gates, shift=DOWN * 0.08), run_time=0.5)
        self.respiro(0.5)

        # «Hoy» fijo
        hoy_l = et("Hoy", 22, C_SAT).move_to([xm(HOY), 3.05, 0])
        self.play(FadeIn(hoy_l, shift=DOWN * 0.1), run_time=0.5)

        # resto planeado: punteado
        def barra_p(m0, m1, y, color):
            r = Rectangle(width=(m1 - m0) * MES, height=H).move_to([(xm(m0) + xm(m1)) / 2, y, 0])
            return punteado(r, int(2 * ((m1 - m0) * MES + H) / 0.16), color, 2.2)

        mvp3_rest = barra_p(HOY, 17, ys[2], C_ANT)
        l_g3 = et("G3 pendiente", 18, C_ANT).move_to([(xm(HOY) + xm(17)) / 2, ys[2], 0])
        plan = [barra_p(11, 23, ys[3], C_CIELO), barra_p(23, 35, ys[4], C_CIELO), barra_p(35, 48, ys[5], C_CIELO)]
        bandera = VGroup(Line([0, 0, 0], [0, 0.5, 0], color=C_CIELO, stroke_width=3),
                         Polygon([0, 0.5, 0], [-0.32, 0.4, 0], [0, 0.3, 0], color=C_CIELO,
                                 fill_color=C_CIELO, fill_opacity=0.7, stroke_width=1.5)
                         ).move_to([xm(48) - 0.1, ys[5] + H / 2, 0], aligned_edge=DOWN + RIGHT)

        self.play(Create(mvp3_rest), FadeIn(l_g3), run_time=1.0)
        self.respiro(0.4)
        self.play(LaggedStart(*[Create(p) for p in plan], lag_ratio=0.35), run_time=1.8)
        self.play(FadeIn(bandera, shift=UP * 0.1), run_time=0.5)

        # WITCOM: ponencia 2–6 nov 2026 (del paper de MVP1)
        est = Star(5, outer_radius=0.17, inner_radius=0.075, color=C_OK, fill_color=C_OK, fill_opacity=0.9,
                   stroke_width=1.5).move_to([xm(WIT), ys[0], 0])
        con = DashedLine([xm(4) + 0.55, ys[0], 0], est.get_left() + LEFT * 0.05, color=C_OK,
                         stroke_width=1.8, dash_length=0.07)
        l_wit = et("WITCOM", 20, C_OK).next_to(est, RIGHT, buff=0.15)
        self.play(Create(con), FadeIn(est, scale=0.4), FadeIn(l_wit), run_time=0.9)

        l_sem = et("Semestre 2/8", 20, TENUE).next_to(hoy_l, RIGHT, buff=0.35)
        self.play(FadeIn(l_sem), Indicate(hoy_l, color=C_SAT, scale_factor=1.15), run_time=0.9)
        self.wait(3.2)
        self.cierre()


# =============================================================================
# 5. Cuatro contribuciones que encajan
# =============================================================================
def pieza_rompecabezas(cx, cy, L, lados, color, r=0.33, sale=0.2):
    """Pieza cuadrada con pestañas (+1) o huecos (−1) en lados {'R','L','T','B'}."""
    base = Square(L).move_to([cx, cy, 0])
    dirs = {"R": RIGHT, "L": LEFT, "T": UP, "B": DOWN}
    forma = base
    for lado, s in lados.items():
        d = dirs[lado]
        c = Circle(radius=r)
        if s > 0:
            c.move_to(np.array([cx, cy, 0]) + d * (L / 2 + sale))
            forma = Union(forma, c)
        else:
            c.move_to(np.array([cx, cy, 0]) + d * (L / 2 - sale))
            forma = Difference(forma, c)
    forma.set_stroke(color, width=3).set_fill(color, opacity=0.2)
    return forma


class CuatroContribuciones(Pieza):
    def construct(self):
        L = 2.6
        C = np.array([0, 0.4, 0])
        o = L / 2
        spec = [
            ("Marco", C_ANT, (-o, o), {"R": 1, "B": -1}, UL, "1"),
            ("Protocolo", C_SAT, (o, o), {"L": -1, "B": 1}, UR, "2"),
            ("Evidencia", C_OK, (-o, -o), {"T": 1, "R": -1}, DL, "3"),
            ("Mapeo", C_CIELO, (o, -o), {"L": 1, "T": -1}, DR, "4"),
        ]
        chip_d = chip_desarrollo()
        self.add(chip_d)

        def icono(nombre, color):
            if nombre == "Marco":
                # documento con un hueco declarado (dashed) sobre el que se sitúa el marco
                d = documento(0.62, 0.78, TENUE, 1)
                gap = DashedLine([-0.18, -0.12, 0], [0.16, -0.12, 0], color=color, stroke_width=3, dash_length=0.05)
                gap2 = Rectangle(width=0.42, height=0.16, color=color, stroke_width=2).move_to([-0.01, -0.12, 0])
                return VGroup(d, punteado(gap2, 10, color, 2)).scale(1.0)
            if nombre == "Protocolo":
                u = DashedLine([-0.55, 0.05, 0], [0.55, 0.05, 0], color=C_CIELO, stroke_width=2.5, dash_length=0.07)
                b = barra(-0.1, -0.35, 0.62, 0.3, color, 0.8)
                post = VGroup(Line([0.3, -0.35, 0], [0.3, 0.3, 0], color=TINTA, stroke_width=3),
                              Line([0.55, -0.35, 0], [0.55, 0.3, 0], color=TINTA, stroke_width=3),
                              Line([0.3, 0.3, 0], [0.55, 0.3, 0], color=TINTA, stroke_width=3))
                return VGroup(u, b, post)
            if nombre == "Evidencia":
                base = Line([-0.55, 0, 0], [0.55, 0, 0], color=TENUE, stroke_width=2)
                bs = VGroup(barra(-0.35, 0, 0.42, 0.22, color), barra(0.0, 0, 0.22, 0.22, color),
                            barra(0.35, 0, -0.3, 0.22, C_MAL))
                return VGroup(base, bs)
            # Mapeo: nodo del marco → dos puntos de extensión; uno verificado, uno pendiente
            n = Dot([-0.45, 0, 0], radius=0.1, color=color)
            a = Square(0.26, color=TINTA, stroke_width=2).move_to([0.45, 0.25, 0])
            b = Square(0.26, color=TINTA, stroke_width=2).move_to([0.45, -0.25, 0])
            e1 = Line(n.get_center(), a.get_left(), color=color, stroke_width=2.5)
            e2 = DashedLine(n.get_center(), b.get_left(), color=color, stroke_width=2.5, dash_length=0.06)
            return VGroup(n, a, b, e1, e2)

        piezas, destinos = [], []
        for nombre, col, (dx, dy), lados, esq, num in spec:
            cx, cy = C[0] + dx, C[1] + dy
            f = pieza_rompecabezas(cx, cy, L, lados, col)
            centro = np.array([cx, cy, 0])
            ic = icono(nombre, col).move_to(centro + UP * 0.28)
            tx = et(nombre, 24, TINTA).move_to(centro + DOWN * 0.5)
            nu = et(num, 18, TENUE).move_to(centro + esq * 0.97)
            g = VGroup(f, ic, tx, nu)
            destinos.append(g.copy())
            piezas.append(g)

        # entran desde fuera, separadas y giradas; encajan una a una
        desde = [np.array([-4.6, 1.6, 0]), np.array([4.6, 1.6, 0]), np.array([-4.6, -1.8, 0]), np.array([4.6, -1.8, 0])]
        giros = [-14, 12, 10, -12]
        for g, p, a in zip(piezas, desde, giros):
            g.rotate(a * DEGREES).move_to(p).scale(0.9)

        self.play(LaggedStart(*[FadeIn(g, scale=0.8) for g in piezas], lag_ratio=0.3), run_time=1.8)
        self.respiro(0.5)
        for g, dst in zip(piezas, destinos):
            self.play(Transform(g, dst), run_time=1.3, rate_func=smooth)
            brillo = dst[0].copy().set_fill(opacity=0).set_stroke(TINTA, width=6)
            self.play(ShowPassingFlash(brillo, time_width=0.5), run_time=0.6)
            self.respiro(0.35)

        contorno = Square(2 * L + 0.18).move_to(C).set_stroke(TINTA, 2.5).set_fill(opacity=0)
        l_tesis = et("Tesis", 30, TINTA).next_to(contorno, DOWN, buff=0.3)
        self.play(Create(contorno), FadeIn(l_tesis, shift=UP * 0.12), run_time=1.1)
        self.play(*[g[0].animate.set_fill(opacity=0.32) for g in piezas], run_time=0.6)
        self.wait(3.0)
        self.cierre()


# =============================================================================
# 6. Cierre: gane o pierda, la medición significa algo
# =============================================================================
class CierreMedicionSignifica(Pieza):
    def construct(self):
        chip_d = chip_desarrollo()
        self.add(chip_d)

        def tarjeta(alt_alg, gana):
            fondo = RoundedRectangle(corner_radius=0.14, width=2.5, height=1.9, color=TENUE, stroke_width=2,
                                     fill_color=C_PANEL, fill_opacity=0.6)
            base = Line([-0.85, -0.6, 0], [0.85, -0.6, 0], color=TENUE, stroke_width=2)
            ref_h = 0.85
            b_ref = barra(0.42, -0.6, ref_h, 0.5, TENUE, 0.55)
            b_alg = barra(-0.42, -0.6, alt_alg, 0.5, C_SAT, 0.9)
            nivel = DashedLine([-0.95, -0.6 + ref_h, 0], [0.95, -0.6 + ref_h, 0], color=TENUE,
                               stroke_width=1.6, dash_length=0.06)
            return VGroup(fondo, base, b_ref, b_alg, nivel)

        t_g = tarjeta(1.25, True).move_to([-4.3, 0.55, 0])
        t_p = tarjeta(0.5, False).move_to([4.3, 0.55, 0])
        l_g = et("Gana", 26, C_OK).next_to(t_g, UP, buff=0.18)
        l_p = et("Pierde", 26, C_MAL).next_to(t_p, UP, buff=0.18)

        self.play(FadeIn(t_g, shift=RIGHT * 0.2), FadeIn(t_p, shift=LEFT * 0.2), run_time=0.9)
        self.play(GrowFromEdge(t_g[3], DOWN), GrowFromEdge(t_p[3], DOWN), run_time=0.8)
        self.play(FadeIn(l_g), FadeIn(l_p), run_time=0.5)
        self.respiro(0.3)

        # instrumento certificado (medidor calibrado + marca de compuerta)
        CD = np.array([0, 1.5, 0])
        RD = 1.2
        arco = Arc(radius=RD, start_angle=0, angle=PI, arc_center=CD, color=TINTA, stroke_width=3)
        ticks = VGroup(*[Line(CD + RD * np.array([np.cos(a), np.sin(a), 0]),
                              CD + (RD - 0.14) * np.array([np.cos(a), np.sin(a), 0]),
                              color=TINTA, stroke_width=2) for a in np.linspace(0, PI, 9)])
        a_um = PI * 0.62
        umbral = Line(CD + (RD - 0.32) * np.array([np.cos(a_um), np.sin(a_um), 0]),
                      CD + (RD + 0.14) * np.array([np.cos(a_um), np.sin(a_um), 0]),
                      color=C_CIELO, stroke_width=5)
        base_d = Line(CD + LEFT * (RD + 0.1), CD + RIGHT * (RD + 0.1), color=TINTA, stroke_width=2)
        ang = ValueTracker(PI / 2)
        aguja = always_redraw(lambda: Line(CD, CD + (RD - 0.18) * np.array([np.cos(ang.get_value()),
                                                                              np.sin(ang.get_value()), 0]),
                                           color=C_SAT, stroke_width=4))
        pivote = Dot(CD, radius=0.07, color=C_SAT)
        insig = insignia_ok(CD + np.array([RD + 0.25, 0.22, 0]), 0.22)
        l_mide = et("Mide", 24, TINTA).next_to(base_d, DOWN, buff=0.2)
        medidor = VGroup(arco, ticks, umbral, base_d)

        self.play(Create(arco), FadeIn(ticks), FadeIn(base_d), run_time=0.9)
        self.add(aguja, pivote)
        self.play(Create(umbral), FadeIn(l_mide), run_time=0.6)
        self.play(FadeIn(insig, scale=1.6), run_time=0.5)
        self.play(Flash(insig, color=C_OK, line_length=0.15, flash_radius=0.32), run_time=0.4)

        # mide ambos escenarios con el mismo instrumento
        for tj, a_obj in ((t_g, PI * 0.85), (t_p, PI * 0.22)):
            h = haz(tj.get_center() + UP * 0.2, CD + DOWN * 0.02, C_ANT, 2.2)
            self.play(Create(h), ang.animate.set_value(a_obj), run_time=0.9, rate_func=smooth)
            ok = insignia_ok(tj[0].get_corner(UR) + np.array([-0.05, -0.05, 0]), 0.2)
            tj.add(ok)
            self.play(FadeIn(ok, scale=1.5), FadeOut(h), run_time=0.5)
        self.play(ang.animate.set_value(PI / 2), run_time=0.5)

        # vitrina: ambos resultados se archivan como producto
        YS = -1.85
        estante = VGroup(Line([-3.7, YS, 0], [3.7, YS, 0], color=TINTA, stroke_width=4),
                         Line([-3.5, YS, 0], [-3.5, YS - 0.3, 0], color=TINTA, stroke_width=3),
                         Line([3.5, YS, 0], [3.5, YS - 0.3, 0], color=TINTA, stroke_width=3))
        bote = VGroup(Polygon([-0.3, 0.35, 0], [0.3, 0.35, 0], [0.22, -0.35, 0], [-0.22, -0.35, 0],
                              color=C_MAL, stroke_width=2.5),
                      Line([-0.38, 0.42, 0], [0.38, 0.42, 0], color=C_MAL, stroke_width=3),
                      *[Line([x, 0.22, 0], [x * 0.75, -0.25, 0], color=C_MAL, stroke_width=1.6) for x in (-0.12, 0, 0.12)]
                      ).set_opacity(0.8).scale(1.15).move_to([5.55, -2.35, 0])

        self.play(Create(estante), run_time=0.6)
        g_g = VGroup(t_g, l_g)
        self.play(g_g.animate.scale(0.85).move_to([-2.1, YS + 1.12, 0]), run_time=1.0, rate_func=smooth)
        # el negativo no se tira...
        g_p = VGroup(t_p, l_p)
        self.play(FadeIn(bote), run_time=0.4)
        self.play(g_p.animate.scale(0.85).move_to([4.75, -0.35, 0]).rotate(-12 * DEGREES), run_time=0.8)
        tache = marca_no(bote.get_center(), 0.9)
        self.play(Create(tache), run_time=0.4)
        # ...se archiva igual
        self.play(g_p.animate.rotate(12 * DEGREES).move_to([2.1, YS + 1.12, 0]),
                  FadeOut(bote), FadeOut(tache), run_time=1.1, rate_func=smooth)
        l_sig = et("Significa algo", 30, C_OK).move_to([0, YS - 0.65, 0])
        self.play(FadeIn(l_sig, shift=UP * 0.12), run_time=0.7)
        self.play(Indicate(VGroup(medidor, insig), color=C_OK, scale_factor=1.05), run_time=0.9)
        self.wait(2.0)
        self.cierre()

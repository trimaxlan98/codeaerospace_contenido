"""Piezas del comité tutorial (bloques 4–6): brecha, marco PADA/O-RAN, Dec-POMDP, compuertas, reclamo, par MA y sensibilidad."""
from tesis_lib import *
import numpy as np


# ---------------------------------------------------------------- helpers locales
def mezcla(a, b, t):
    return interpolate_color(ManimColor(a), ManimColor(b), t)


def banda_vertical(x0, x1, y0, alto, color, pasos=26, op0=0.32):
    """Banda que se desvanece hacia arriba: sin borde superior (sin techo)."""
    g = VGroup()
    h = alto / pasos
    for i in range(pasos):
        op = op0 * (1 - i / pasos) ** 1.3
        g.add(Rectangle(width=x1 - x0, height=h * 1.02, stroke_width=0, fill_color=color,
                        fill_opacity=op).move_to([(x0 + x1) / 2, y0 + h * (i + 0.5), 0]))
    return g


def rayo_abierto(x0, largo, y, color, pasos=22, alto=0.1, op0=0.9):
    """Segmento horizontal que se desvanece hacia la derecha (intervalo abierto)."""
    g = VGroup()
    w = largo / pasos
    for i in range(pasos):
        op = op0 * (1 - i / pasos) ** 1.2
        g.add(Rectangle(width=w * 1.02, height=alto, stroke_width=0, fill_color=color,
                        fill_opacity=op).move_to([x0 + w * (i + 0.5), y, 0]))
    return g


def puntos_separados(rng, n, x0, x1, y0, y1, dmin=0.36):
    pts = []
    intentos = 0
    while len(pts) < n and intentos < 5000:
        intentos += 1
        p = np.array([rng.uniform(x0, x1), rng.uniform(y0, y1), 0])
        if all(np.linalg.norm(p - q) >= dmin for q in pts):
            pts.append(p)
    return pts


# =============================================================================
# 1. El hueco, en una figura (diapositiva 9)
# =============================================================================
class CuadranteVacio(Pieza):
    def construct(self):
        cx, cy, W, H = 0.6, 0.15, 4.6, 2.6
        x0, x1, y0, y1 = cx - W, cx + W, cy - H, cy + H
        marco = Rectangle(width=2 * W, height=2 * H, color=C_EJE, stroke_width=2.5).move_to([cx, cy, 0])
        cruz_v = Line([cx, y0, 0], [cx, y1, 0], color=C_EJE, stroke_width=2.5)
        cruz_h = Line([x0, cy, 0], [x1, cy, 0], color=C_EJE, stroke_width=2.5)
        eje_x = DoubleArrow([x0, y0 - 0.3, 0], [x1, y0 - 0.3, 0], buff=0, color=TENUE, stroke_width=2.5,
                            tip_length=0.16, max_tip_length_to_length_ratio=0.05)
        eje_y = DoubleArrow([x0 - 0.3, y0, 0], [x0 - 0.3, y1, 0], buff=0, color=TENUE, stroke_width=2.5,
                            tip_length=0.16, max_tip_length_to_length_ratio=0.05)
        l_ter = et("Terrestre", 26, TINTA).move_to([cx - W / 2, y0 - 0.72, 0])
        l_nt = et("No terrestre", 26, TINTA).move_to([cx + W / 2, y0 - 0.72, 0])
        l_alg = et("Algoritmo", 26, TINTA)
        l_alg.move_to([x0 - 0.55 - l_alg.width / 2, cy - H / 2, 0])
        l_ins = et("Instrumento", 26, TINTA)
        l_ins.move_to([x0 - 0.55 - l_ins.width / 2, cy + H / 2, 0])

        self.play(Create(marco), Create(cruz_v), Create(cruz_h), run_time=1.2)
        self.play(GrowFromCenter(eje_x), GrowFromCenter(eje_y),
                  LaggedStart(FadeIn(l_ter), FadeIn(l_nt), FadeIn(l_alg), FadeIn(l_ins), lag_ratio=0.15),
                  run_time=1.3)

        rng = np.random.default_rng(42)
        m = 0.38
        cuad = {
            "BL": puntos_separados(rng, 24, x0 + m, cx - m, y0 + m, cy - m),
            "BR": puntos_separados(rng, 12, cx + m, x1 - m, y0 + m, cy - m),
            "TL": puntos_separados(rng, 5, x0 + m, cx - m, cy + m, y1 - m, dmin=0.8),
        }
        busca = chip("Mi búsqueda", TENUE)
        self.add(chip_ilustrativo(DL))
        t_inf, t_sup = ValueTracker(x0 - 0.2), ValueTracker(x0 - 0.2)

        def puntos(lista, tr):
            g = VGroup()
            for p in lista:
                d = Dot(p, radius=0.085, color=C_CIELO).set_opacity(0)
                d.add_updater(lambda mob, x=p[0], tr=tr: mob.set_opacity(suave((tr.get_value() - x) / 0.25)))
                g.add(d)
            return g

        d_inf = puntos(cuad["BL"] + cuad["BR"], t_inf)
        d_sup = puntos(cuad["TL"], t_sup)

        def barredor(tr, yc):
            ln = Line([0, -H / 2 + 0.06, 0], [0, H / 2 - 0.06, 0], color=C_SAT, stroke_width=4)
            ln.add_updater(lambda mob: mob.move_to([np.clip(tr.get_value(), x0, x1), yc, 0]))
            return ln

        b_inf = barredor(t_inf, cy - H / 2)
        self.add(d_inf, d_sup)
        self.play(FadeIn(b_inf), FadeIn(busca), run_time=0.4)
        self.play(t_inf.animate.set_value(x1 + 0.2), run_time=3.2, rate_func=linear)
        self.play(FadeOut(b_inf), run_time=0.3)
        b_sup = barredor(t_sup, cy + H / 2)
        self.play(FadeIn(b_sup), run_time=0.3)
        self.play(t_sup.animate.set_value(cx), run_time=1.6, rate_func=linear)
        # entra al cuarto cuadrante: más despacio, no aparece nada
        self.play(t_sup.animate.set_value(x1 + 0.2), run_time=2.6, rate_func=linear)
        self.play(FadeOut(b_sup), run_time=0.3)
        for g in (d_inf, d_sup):
            for d in g:
                d.clear_updaters()

        hueco = DashedVMobject(Rectangle(width=W - 0.3, height=H - 0.3, color=C_SAT, stroke_width=3),
                               num_dashes=46).move_to([cx + W / 2, cy + H / 2, 0])
        relleno = Rectangle(width=W - 0.3, height=H - 0.3, stroke_width=0, fill_color=C_SAT,
                            fill_opacity=0.08).move_to(hueco)
        l_hueco = et("No localicé trabajo", 30, TINTA).move_to(hueco)
        self.play(Create(hueco), FadeIn(relleno), run_time=1.2)
        self.play(FadeIn(l_hueco, shift=UP * 0.15), run_time=0.9)
        self.play(relleno.animate.set_fill(opacity=0.16), rate_func=there_and_back, run_time=1.2)
        self.respiro(1.0)
        self.cierre()


# =============================================================================
# 2. PADA y la partición que O-RAN induce (diapositiva 10)
# =============================================================================
class PadaYOran(Pieza):
    def construct(self):
        # --- PADA: columna de cuatro módulos con puertos (interfaces programables)
        px = -5.2
        defs = [("Percepción", C_ANT), ("Análisis", C_CIELO), ("Decisión", C_SAT), ("Acción", C_OK)]
        ys = [2.3, 0.8, -0.7, -2.2]
        bloques, puertos, flechas = [], VGroup(), VGroup()
        for (txt, col), y in zip(defs, ys):
            r = RoundedRectangle(corner_radius=0.12, width=2.3, height=0.72, color=col, fill_color=col,
                                 fill_opacity=0.15, stroke_width=2.5).move_to([px, y, 0])
            bloques.append(VGroup(r, et(txt, 24, TINTA).move_to(r)))
            for s in (-1, 1):
                puertos.add(Square(0.14, color=col, fill_color=col, fill_opacity=0.9, stroke_width=1)
                            .move_to([px + s * 1.15, y, 0]))
        for a, b in zip(ys[:-1], ys[1:]):
            flechas.add(flecha([px, a - 0.38, 0], [px, b + 0.38, 0], TENUE, 2.5, 0.14))
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2) for b in bloques], lag_ratio=0.2),
                  run_time=1.4)
        self.play(LaggedStart(*[GrowFromCenter(f) for f in flechas], lag_ratio=0.2),
                  FadeIn(puertos, scale=0.4), run_time=0.9)

        # --- CTDE del marco: nace de Decisión
        mx = -2.15
        ent = VGroup(RoundedRectangle(corner_radius=0.12, width=1.9, height=0.66, color=C_SAT, fill_color=C_SAT,
                                      fill_opacity=0.22, stroke_width=2.5), et("Entrenar", 24, TINTA))
        ent[1].move_to(ent[0])
        ent.move_to([mx, 1.6, 0])
        ag = VGroup(*[Circle(radius=0.17, color=C_SAT, fill_color=C_SAT, fill_opacity=0.4, stroke_width=2.5)
                      .move_to([mx + dx, -1.55, 0]) for dx in (-0.6, 0, 0.6)])
        inf = et("Inferir", 24, TINTA).move_to([mx, -2.2, 0])
        f_mini = flecha(ent.get_bottom() + DOWN * 0.08, [mx, -1.2, 0], C_SAT, 3, 0.16)
        par_m = DashedLine([mx - 1.05, 0, 0], [mx + 1.05, 0, 0], color=C_SAT, stroke_width=4, dash_length=0.12)
        self.play(bloques[2][0].animate.set_fill(C_SAT, opacity=0.5), run_time=0.4)
        copia = bloques[2].copy()
        self.play(FadeTransform(copia, VGroup(ent, ag)), run_time=1.1)
        self.play(GrowArrow(f_mini), FadeIn(inf), Create(par_m), bloques[2][0].animate.set_fill(C_SAT, opacity=0.15),
                  run_time=0.9)
        self.respiro(0.3)

        # --- Arquitectura de referencia O-RAN (de terceros)
        ox0, ox1 = 0.3, 6.4
        oc = (ox0 + ox1) / 2
        nrt = RoundedRectangle(corner_radius=0.16, width=ox1 - ox0, height=2.55, color=C_CIELO, fill_color=C_CIELO,
                               fill_opacity=0.07, stroke_width=2.5).move_to([oc, 1.68, 0])
        near = RoundedRectangle(corner_radius=0.16, width=ox1 - ox0, height=2.55, color=C_CIELO, fill_color=C_CIELO,
                                fill_opacity=0.07, stroke_width=2.5).move_to([oc, -1.68, 0])
        l_nrt = et("Non-RT RIC", 24, C_CIELO).next_to(nrt.get_corner(UL), DR, buff=0.18)
        l_near = et("Near-RT RIC", 24, C_CIELO).next_to(near.get_corner(DL), UR, buff=0.18)
        sx = 3.9
        zocalo = DashedVMobject(RoundedRectangle(corner_radius=0.12, width=2.05, height=0.8, color=C_CIELO,
                                                 stroke_width=2.5), num_dashes=30).move_to([sx, 1.6, 0])
        r1_bus = Line([1.05, 1.6, 0], [sx - 1.03, 1.6, 0], color=C_CIELO, stroke_width=3)
        r1_tap = Square(0.16, color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.9, stroke_width=1).move_to([1.05, 1.6, 0])
        l_r1 = et("R1", 24, C_CIELO).next_to(r1_bus, UP, buff=0.12)
        xs_app = [sx - 1.25, sx, sx + 1.25]
        ranuras = VGroup()
        l_xapp = VGroup()
        for x in xs_app:
            ranuras.add(DashedVMobject(RoundedRectangle(corner_radius=0.1, width=1.05, height=1.0, color=C_CIELO,
                                                        stroke_width=2.2), num_dashes=24).move_to([x, -1.45, 0]))
            l_xapp.add(et("xApp", 20, C_CIELO).move_to([x, -1.2, 0]))
        a1 = flecha([sx, 1.18, 0], [sx, -0.97, 0], C_CIELO, 3.5, 0.18)
        l_a1 = et("A1", 24, C_CIELO).next_to(a1, RIGHT, buff=0.15).shift(UP * 0.55)
        frontera = Line([ox0, 0, 0], [ox1, 0, 0], color=C_CIELO, stroke_width=2.5)
        tercero = chip_tercero("O-RAN")
        self.play(FadeIn(nrt), FadeIn(near), FadeIn(l_nrt), FadeIn(l_near), FadeIn(tercero), run_time=1.0)
        self.play(Create(r1_bus), FadeIn(r1_tap), FadeIn(l_r1), Create(zocalo), run_time=0.9)
        self.play(LaggedStart(*[Create(r) for r in ranuras], lag_ratio=0.15), FadeIn(l_xapp),
                  GrowArrow(a1), FadeIn(l_a1), Create(frontera), run_time=1.2)
        self.respiro(0.4)

        # --- encaje: la partición del marco cae sobre la que O-RAN induce
        ent_d = ent.copy().move_to(zocalo)
        ag_d = VGroup(*[a.copy().move_to([x, -1.62, 0]) for a, x in zip(ag, xs_app)])
        inf_d = inf.copy().move_to([sx, -2.28, 0])
        f_d = flecha([sx, 1.18, 0], [sx, -0.97, 0], C_SAT, 3.5, 0.18)
        par_d = DashedLine([ox0, 0, 0], [ox1, 0, 0], color=C_SAT, stroke_width=4.5, dash_length=0.12)
        self.play(Transform(ent, ent_d), Transform(ag, ag_d), Transform(inf, inf_d),
                  Transform(f_mini, f_d), Transform(par_m, par_d), run_time=1.8)
        guia = DashedLine(puertos[5].get_right() + RIGHT * 0.05, [ox0 - 0.05, 0, 0], color=C_SAT, stroke_width=2,
                          dash_length=0.1, stroke_opacity=0.6)
        self.play(FadeOut(zocalo), Create(guia), run_time=0.6)
        self.play(ShowPassingFlash(Line([ox0, 0, 0], [ox1, 0, 0], color=C_SAT, stroke_width=10),
                                   time_width=0.4), run_time=0.9)

        # --- ejecución: el modelo baja por A1 a cada xApp
        for _ in range(2):
            ds = [Dot([sx, 1.18, 0], radius=0.09, color=C_SAT).set_z_index(5) for _ in xs_app]
            self.add(*ds)
            self.play(*[d.animate.move_to([x, -1.62, 0]) for d, x in zip(ds, xs_app)], run_time=0.9,
                      rate_func=smooth)
            self.remove(*ds)
            self.play(*[a.animate.set_fill(C_OK, opacity=0.85).set_stroke(C_OK) for a in ag],
                      rate_func=there_and_back, run_time=0.5)
        self.play(*[a.animate.set_fill(C_OK, opacity=0.8).set_stroke(C_OK) for a in ag],
                  FadeIn(chip_desarrollo()), run_time=0.6)
        self.respiro(0.8)
        self.cierre()


# =============================================================================
# 3. Dec-POMDP cross-layer unificado (diapositiva 11)
# =============================================================================
class DecPomdpUnificado(Pieza):
    def construct(self):
        cen = np.array([0, -0.2, 0])
        Wl, Hl = 6.0, 2.5
        losa = RoundedRectangle(corner_radius=0.18, width=Wl, height=Hl, color=C_EJE, stroke_width=2.5,
                                fill_color=C_PANEL, fill_opacity=0.35).move_to(cen)
        capas = VGroup(*[Rectangle(width=Wl - 0.2, height=Hl / 3 - 0.12, stroke_width=0, fill_color=c,
                                   fill_opacity=0.12).move_to(cen + UP * (Hl / 3) * k)
                         for c, k in ((C_ANT, 1), (C_CIELO, 0), (C_SAT, -1))])
        rng = np.random.default_rng(42)
        pts = puntos_separados(rng, 14, -Wl / 2 + 0.35, Wl / 2 - 0.35, cen[1] - Hl / 2 + 0.3, cen[1] + Hl / 2 - 0.3, 0.55)
        vars_ = VGroup(*[Dot(p, radius=0.08, color=TINTA).set_opacity(0.85) for p in pts])
        l_est = et("Estado cross-layer", 24, TINTA).next_to(losa, LEFT, buff=0.3).shift(DOWN * 0.55)

        sat_a = satelite(0.3).move_to([-5.0, 2.45, 0])
        sat_b = satelite(0.3).move_to([5.0, 2.45, 0])
        gw = estacion(0.55).move_to([0, -3.05, 0])
        l_a = et_junto("Sat A", sat_a, DOWN, 24, TINTA)
        l_b = et_junto("Sat B", sat_b, DOWN, 24, TINTA)
        l_g = et_junto("Gateway", gw, RIGHT, 24, TINTA)

        self.play(FadeIn(losa), FadeIn(capas), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(v, scale=0.4) for v in vars_], lag_ratio=0.05), FadeIn(l_est), run_time=1.0)
        self.play(LaggedStart(FadeIn(sat_a, scale=0.6), FadeIn(sat_b, scale=0.6), FadeIn(gw, scale=0.6),
                              lag_ratio=0.2), FadeIn(l_a), FadeIn(l_b), FadeIn(l_g), run_time=1.0)

        # observaciones parciales (cono + óvalo)
        ovs = [Ellipse(width=2.6, height=1.35).move_to(cen + np.array([-1.6, 0.4, 0])),
               Ellipse(width=2.4, height=1.35).move_to(cen + np.array([1.7, 0.35, 0])),
               Ellipse(width=2.2, height=0.95).move_to(cen + np.array([0.15, -0.72, 0]))]
        origenes = [l_a.get_bottom() + DOWN * 0.05, l_b.get_bottom() + DOWN * 0.05, gw.get_top()]
        conos = VGroup()
        for ov, o in zip(ovs, origenes):
            ov.set_stroke(C_ANT, 2.5).set_fill(C_ANT, 0.1)
            if o[1] < 0:  # gateway, mira hacia arriba
                a, b = ov.get_left(), ov.get_right()
            else:
                a, b = ov.point_from_proportion(0.5), ov.point_from_proportion(0.0)
                a, b = ov.get_left() + UP * 0.2, ov.get_right() + UP * 0.2
            conos.add(VGroup(Polygon(o, a, b, stroke_width=0, fill_color=C_ANT, fill_opacity=0.15),
                             Line(o, a, color=C_ANT, stroke_width=1.5, stroke_opacity=0.5),
                             Line(o, b, color=C_ANT, stroke_width=1.5, stroke_opacity=0.5)))
        l_obs = et("Observación parcial", 24, C_ANT).move_to([-5.0, 0.85, 0])
        self.play(LaggedStart(*[AnimationGroup(FadeIn(c), Create(o)) for c, o in zip(conos, ovs)], lag_ratio=0.3),
                  run_time=1.6)
        self.play(FadeIn(l_obs, shift=RIGHT * 0.15), run_time=0.6)
        # lo que cae fuera de todo óvalo: nadie lo ve
        fuera = [v for v in vars_ if not any(
            ((v.get_center()[0] - o.get_center()[0]) / (o.width / 2)) ** 2 +
            ((v.get_center()[1] - o.get_center()[1]) / (o.height / 2)) ** 2 <= 1 for o in ovs)]
        self.play(*[v.animate.set_opacity(0.3) for v in fuera], run_time=0.6)

        # acción conjunta
        ranuras = VGroup(*[Square(0.34, color=TENUE, stroke_width=2).move_to([dx, 2.6, 0]) for dx in (-0.48, 0, 0.48)])
        corch = VGroup(et("(", 34, TENUE).next_to(ranuras, LEFT, buff=0.08),
                       et(")", 34, TENUE).next_to(ranuras, RIGHT, buff=0.08))
        l_acc = et("Acción conjunta", 24, TINTA).next_to(ranuras, UP, buff=0.22)
        self.play(FadeIn(ranuras), FadeIn(corch), FadeIn(l_acc), run_time=0.6)
        acciones = [Square(0.24, stroke_width=0, fill_color=C_SAT, fill_opacity=1).move_to(o)
                    for o in (sat_a.get_center(), sat_b.get_center(), gw.get_top())]
        rutas = [Line(sat_a.get_center(), ranuras[0].get_center()),
                 Line(sat_b.get_center(), ranuras[1].get_center()),
                 VMobject().set_points_smoothly([origenes[2], [3.3, -2.2, 0], [3.3, 1.5, 0], ranuras[2].get_center()])]
        self.add(*acciones)
        self.play(*[MoveAlongPath(a, r, rate_func=smooth) for a, r in zip(acciones, rutas)], run_time=1.4)
        f_t = flecha([0, 2.32, 0], [0, cen[1] + Hl / 2 + 0.05, 0], C_SAT, 3, 0.16)
        self.play(GrowArrow(f_t), run_time=0.5)
        # transición del estado
        nuevos = [v.get_center() + np.array([rng.uniform(-0.25, 0.25), rng.uniform(-0.12, 0.12), 0]) for v in vars_]
        self.play(*[v.animate.move_to(p) for v, p in zip(vars_, nuevos)],
                  Flash(cen, color=C_SAT, flash_radius=1.25, line_length=0.18), run_time=1.0)

        # una sola recompensa, la misma para los tres
        rw = Star(n=5, outer_radius=0.26, inner_radius=0.12, color=C_OK, fill_color=C_OK, fill_opacity=1,
                  stroke_width=1).move_to(cen + DOWN * 0.05).set_z_index(6)
        fondo_rw = Circle(radius=0.42, stroke_width=0, fill_color=FONDO, fill_opacity=0.85).move_to(rw).set_z_index(5)
        l_rw = et("Recompensa común", 24, C_OK).next_to(losa, RIGHT, buff=0.3).shift(DOWN * 0.55)
        self.play(FadeIn(fondo_rw), GrowFromCenter(rw), FadeIn(l_rw), run_time=0.7)
        destinos = [sat_a.get_center() + DOWN * 0.05 + RIGHT * 0.75, sat_b.get_center() + LEFT * 0.75,
                    gw.get_center() + LEFT * 0.75]
        copias = [rw.copy() for _ in destinos]
        self.play(*[c.animate.move_to(d).scale(0.85) for c, d in zip(copias, destinos)], run_time=1.3)
        self.play(*[Indicate(c, color=C_OK, scale_factor=1.3) for c in copias], run_time=0.7)
        self.play(FadeIn(chip_tercero("Oliehoek 2008")), FadeIn(chip_desarrollo()), run_time=0.6)
        self.respiro(1.2)
        self.cierre()


# =============================================================================
# 4. Protocolo de compuertas como esclusas (diapositiva 12)
# =============================================================================
class ProtocoloCompuertas(Pieza):
    def construct(self):
        gx = [-4.5, -2.7, -0.9, 0.9, 2.7, 4.5]
        nombres = ["G0", "G1", "G2a", "G2b", "G3", "G4"]
        L = [-0.95 + 0.3 * k for k in range(7)]  # nivel del agua por cámara (0 = entrada, 6 = salida)
        bordes = [-6.3] + gx + [6.3]
        prof = 0.72
        agua_c = mezcla(C_EJE, C_ANT, 0.35)

        agua, lecho = VGroup(), VMobject()
        pts = []
        for k in range(7):
            xa, xb, fl = bordes[k], bordes[k + 1], L[k] - prof
            agua.add(Rectangle(width=xb - xa, height=prof, stroke_width=0, fill_color=agua_c, fill_opacity=0.5)
                     .move_to([(xa + xb) / 2, L[k] - prof / 2, 0]))
            pts += [[xa, fl, 0], [xb, fl, 0]]
        lecho.set_points_as_corners(pts).set_stroke(C_EJE, 3)
        # rama lateral: el entorno que no pasa sale del canal
        rama_pts = [[-3.75, L[1] - prof, 0], [-3.35, -2.35, 0], [-2.55, -2.8, 0], [0.4, -2.8, 0]]
        rama = VMobject().set_points_smoothly(rama_pts).set_stroke(agua_c, 24, opacity=0.4)
        rama_borde = DashedVMobject(VMobject().set_points_smoothly(rama_pts).set_stroke(C_EJE, 2), num_dashes=26)

        puertas, etiquetas = [], VGroup()
        for k, x in enumerate(gx):
            base, top = L[k] - prof, L[k + 1] + 0.35
            p = Rectangle(width=0.18, height=top - base, stroke_width=2, color=TENUE, fill_color=TENUE,
                          fill_opacity=0.55).move_to([x, (base + top) / 2, 0]).set_z_index(3)
            if k >= 4:  # G3, G4: pendientes
                p = DashedVMobject(Rectangle(width=0.18, height=top - base, stroke_width=2, color=TENUE),
                                   num_dashes=16).move_to([x, (base + top) / 2, 0]).set_stroke(TENUE, 2.5, opacity=0.8)
            puertas.append(p)
            etiquetas.add(et(nombres[k], 28, TINTA if k < 4 else TENUE).move_to([x, L[k + 1] + 1.3, 0]))
        pend = et("Pendiente", 22, TENUE).move_to([(gx[4] + gx[5]) / 2, L[6] + 1.97, 0])
        llave = Line([gx[4], L[6] + 1.7, 0], [gx[5], L[6] + 1.7, 0], color=TENUE, stroke_width=2)

        self.play(Create(lecho), FadeIn(agua), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.2) for p in puertas], lag_ratio=0.12),
                  LaggedStart(*[FadeIn(e) for e in etiquetas], lag_ratio=0.12), run_time=1.3)
        self.play(FadeIn(pend), Create(llave), FadeIn(rama), Create(rama_borde), run_time=0.8)

        def barco(color_c, op=1.0):
            casco = Polygon([-0.5, 0.1, 0], [0.5, 0.1, 0], [0.36, -0.16, 0], [-0.36, -0.16, 0],
                            color=TINTA, fill_color=TINTA, fill_opacity=0.85 * op, stroke_width=1.5)
            carga = VGroup(*[Rectangle(width=0.15, height=h, stroke_width=0, fill_color=c, fill_opacity=op)
                             .move_to([dx, 0.1 + h / 2, 0])
                             for dx, h, c in ((-0.22, 0.26, C_CIELO), (0, 0.4, C_SAT), (0.22, 0.32, color_c))])
            return VGroup(casco, carga).scale(1.3)

        def en(k, x):
            return np.array([x, L[k] + 0.02, 0])

        # --- 1) un entorno que no pasa: sus comparaciones no se reportan
        fant = barco(C_ANT, 0.9).move_to(en(0, -5.6)).set_z_index(4)
        self.play(FadeIn(fant, shift=RIGHT * 0.4), run_time=0.6)
        self.play(puertas[0].animate.shift(UP * 0.6), run_time=0.4)
        self.play(fant.animate.move_to(en(1, -3.6)), run_time=0.9)
        self.play(puertas[0].animate.shift(DOWN * 0.6), run_time=0.3)
        self.play(fant.animate.move_to(en(1, -3.25)), run_time=0.4)
        no = marca_no(np.array([gx[1], L[2] + 0.68, 0]), 0.24)
        self.play(puertas[1].animate.set_color(C_MAL).set_fill(C_MAL, 0.6), FadeIn(no, scale=0.5), run_time=0.4)
        camino = VMobject().set_points_smoothly([fant[0].get_top() + DOWN * 0.12] +
                                                [np.array(p) for p in rama_pts[1:]])
        l_nr = et("No se reporta", 24, C_MAL).move_to([2.3, -2.8, 0])
        def deriva(m, a):
            m.shift(camino.point_from_proportion(smooth(a)) + UP * 0.12 - m[0].get_top())
            m[1].set_fill(opacity=0.9 * (1 - suave(a / 0.8)))
            m[0].set_fill(opacity=0.77 - 0.5 * a).set_stroke(opacity=1 - 0.6 * a)

        self.play(UpdateFromAlphaFunc(fant, deriva), run_time=2.2)
        self.play(FadeIn(l_nr, shift=RIGHT * 0.2), puertas[1].animate.set_color(TENUE).set_fill(TENUE, 0.55),
                  FadeOut(no), run_time=0.6)

        # --- 2) el entorno que sí pasa: G0 → G2b
        b = barco(C_OK).move_to(en(0, -5.6)).set_z_index(4)
        self.play(FadeIn(b, shift=RIGHT * 0.4), run_time=0.5)
        centros = [-3.6, -1.8, 0.0, 1.8]
        for k in range(4):
            extra = []
            if k == 1:
                extra = [FadeIn(et("MA 0.318", 22, C_OK).move_to([gx[1], L[2] + 1.75, 0]), shift=UP * 0.1)]
            self.play(puertas[k].animate.shift(UP * 0.6).set_color(C_OK).set_fill(C_OK, 0.6),
                      etiquetas[k].animate.set_color(C_OK), *extra, run_time=0.45)
            self.play(b.animate.move_to(en(k + 1, centros[k])), run_time=0.75)
        # G3: sin lanzar, el barco espera
        self.play(b.animate.move_to(en(4, 1.95)), run_time=0.4)
        for _ in range(2):
            self.play(puertas[4].animate.set_opacity(1), rate_func=there_and_back, run_time=0.7)
        self.play(FadeIn(chip_desarrollo()), run_time=0.4)
        self.respiro(1.0)
        self.cierre()


# =============================================================================
# 5. El reclamo, con precisión (diapositiva 13)
# =============================================================================
class ReclamoEstrecho(Pieza):
    def construct(self):
        suelo_y = -1.9
        suelo = Line([-6.6, suelo_y, 0], [6.6, suelo_y, 0], color=C_EJE, stroke_width=3)
        # afirmación ancha: losa baja y extensa sobre dos apoyos
        xa, xb = -6.4, -0.3
        yl, esp = -0.55, 0.6
        pie = yl - esp / 2
        apoyos = VGroup(*[Rectangle(width=0.32, height=pie - suelo_y, color=TENUE, fill_color=TENUE,
                                    fill_opacity=0.4, stroke_width=2).move_to([x, (suelo_y + pie) / 2, 0])
                          for x in (xa + 0.5, xb - 0.5)])
        izq = Rectangle(width=(xb - xa) / 2, height=esp, color=TENUE, fill_color=C_PANEL, fill_opacity=0.9,
                        stroke_width=2.5).move_to([xa + (xb - xa) / 4, yl, 0])
        der = izq.copy().move_to([xb - (xb - xa) / 4, yl, 0])
        l_ancha = et("Nadie valida entornos", 28, TINTA).move_to([(xa + xb) / 2, (suelo_y + pie) / 2, 0])
        # afirmación estrecha: pilar alto
        px = 3.7
        pilar = Rectangle(width=2.6, height=3.8, color=C_SAT, fill_color=C_SAT, fill_opacity=0.14,
                          stroke_width=3).move_to([px, suelo_y + 1.9, 0])
        l_est = VGroup(et("Margen como", 26, TINTA), et("compuerta", 26, TINTA)).arrange(DOWN, buff=0.12).move_to(pilar)

        self.play(Create(suelo), run_time=0.6)
        self.play(FadeIn(apoyos), FadeIn(izq), FadeIn(der), FadeIn(l_ancha), run_time=1.0)
        self.play(FadeIn(pilar, shift=UP * 0.3), FadeIn(l_est), run_time=0.9)
        self.respiro(0.6)

        precedentes = ["Xu 2021", "Furuta 2021", "Oller 2020", "Tao 2026"]
        xs = list(np.linspace(xa + 0.8, xb - 0.8, 4))
        bloques = []
        for t, x in zip(precedentes, xs):
            r = RoundedRectangle(corner_radius=0.08, width=1.42, height=0.56, color=C_CIELO, fill_color=C_CIELO,
                                 fill_opacity=0.25, stroke_width=2.5)
            g = VGroup(r, et(t, 20, TINTA).move_to(r)).move_to([x, 4.2, 0])
            bloques.append(g)
        self.play(FadeIn(chip_tercero("Precedentes 2020-26")), run_time=0.4)
        grietas = VGroup()
        top_losa = yl + esp / 2
        for k, g in enumerate(bloques):
            self.add(g)
            self.play(g.animate.move_to([xs[k], top_losa + 0.28, 0]), run_time=0.6,
                      rate_func=rate_functions.ease_in_quad)
            gx_ = xs[k] + 0.75 if k < 3 else xs[k] - 0.3
            gr = VMobject().set_points_as_corners([[gx_, top_losa, 0], [gx_ + 0.14, top_losa - 0.18, 0],
                                                   [gx_ - 0.1, top_losa - 0.36, 0], [gx_ + 0.06, top_losa - esp, 0]])
            gr.set_stroke(C_MAL, 4).set_z_index(2)
            grietas.add(gr)
            self.play(Create(gr), izq.animate.set_stroke(mezcla(TENUE, C_MAL, (k + 1) / 4)),
                      der.animate.set_stroke(mezcla(TENUE, C_MAL, (k + 1) / 4)),
                      Wiggle(VGroup(izq, der), scale_value=1.0, rotation_angle=0.006 * TAU, n_wiggles=3),
                      run_time=0.45)
        # colapso de la afirmación ancha
        caida = [Rotate(izq, angle=-0.35, about_point=izq.get_left()), Rotate(der, angle=0.35, about_point=der.get_right())]
        self.play(*caida, FadeOut(grietas), *[g.animate.shift(DOWN * 0.35) for g in bloques], run_time=0.5,
                  rate_func=rate_functions.ease_in_quad)
        self.play(izq.animate.rotate(0.35).move_to([xa + (xb - xa) / 4, suelo_y + esp / 2, 0]).set_opacity(0.35),
                  der.animate.rotate(-0.35).move_to([xb - (xb - xa) / 4, suelo_y + esp / 2, 0]).set_opacity(0.35),
                  FadeOut(apoyos),
                  *[g.animate.move_to([xs[k], suelo_y + esp + 0.28, 0]) for k, g in enumerate(bloques)],
                  l_ancha.animate.set_color(C_MAL).move_to([(xa + xb) / 2, 1.2, 0]),
                  run_time=0.8, rate_func=rate_functions.ease_in_quad)
        tacha = Line(l_ancha.get_left() + LEFT * 0.1, l_ancha.get_right() + RIGHT * 0.1, color=C_MAL, stroke_width=4)
        self.play(Create(tacha), run_time=0.5)
        self.respiro(0.4)

        # la misma búsqueda sobre el reclamo estrecho: no cae nada
        sonda = DashedLine([px, 3.7, 0], [px, pilar.get_top()[1] + 0.12, 0], color=C_CIELO, stroke_width=3,
                           dash_length=0.12)
        self.play(Create(sonda), run_time=1.0)
        self.play(FadeOut(sonda), run_time=0.4)
        ok = marca_ok(np.array([px, pilar.get_top()[1] + 0.5, 0]), 0.4)
        self.play(pilar.animate.set_color(C_OK).set_fill(C_OK, 0.16), Create(ok), FadeIn(chip_desarrollo()),
                  run_time=0.8)
        self.respiro(1.8)
        self.cierre()


# =============================================================================
# 6. El margen como par [0.095, 0.318] (diapositiva 14)
# =============================================================================
class ParMargenAdaptativo(Pieza):
    def construct(self):
        yl = -0.9
        xa, xb = -5.6, 5.6

        def X(v):
            return xa + (xb - xa) * v / 0.5

        recta = Line([xa, yl, 0], [xb + 0.3, yl, 0], color=C_EJE, stroke_width=3.5)
        ticks = VGroup(*[Line([X(v), yl - 0.1, 0], [X(v), yl + 0.1, 0], color=C_EJE, stroke_width=3)
                         for v in np.arange(0, 0.51, 0.05)])
        for k, t in enumerate(ticks):
            if k % 2:
                t.scale(0.55)
        l0 = et("0", 22, TENUE).next_to(ticks[0], DOWN, buff=0.15)
        l5 = et("0.5", 22, TENUE).next_to(ticks[-1], DOWN, buff=0.15)
        self.play(Create(recta), LaggedStart(*[FadeIn(t) for t in ticks], lag_ratio=0.05), FadeIn(l0), FadeIn(l5),
                  run_time=1.2)

        # umbral pre-registrado (lado superior: gobierna a G1)
        xu = X(0.25)
        umbral = DashedLine([xu, yl, 0], [xu, 2.25, 0], color=C_CIELO, stroke_width=3, dash_length=0.12)
        l_um = et("Umbral 0.25", 24, C_CIELO).next_to(umbral, UP, buff=0.12)
        self.play(Create(umbral), FadeIn(l_um), run_time=0.9)

        # tramo 1: G1 mide la envolvente; el estimador es cota inferior → abierto a la derecha
        x1 = X(0.318)
        yg = 1.05
        v1 = ValueTracker(0)
        poste1 = Line([x1, yl, 0], [x1, yg, 0], color=C_OK, stroke_width=4)
        cab1 = Dot([x1, yg, 0], radius=0.11, color=C_OK)
        num1 = DecimalNumber(0, num_decimal_places=3, font_size=34, color=C_OK)
        num1.set_stroke(width=0)
        num1.add_updater(lambda m: m.set_value(v1.get_value()).next_to(cab1, UL, buff=0.08))
        l_g1 = et("G1", 26, C_OK).next_to(cab1, DL, buff=0.1).shift(LEFT * 0.02)
        l_g1.next_to(num1, DOWN, buff=0.08).align_to(num1, RIGHT)
        marcador = Dot([X(0), yg, 0], radius=0.11, color=C_OK)
        marcador.add_updater(lambda m: m.move_to([X(v1.get_value()), yg, 0]))
        pista1 = DashedLine([xa, yg, 0], [xb, yg, 0], color=C_EJE, stroke_width=2, dash_length=0.08)
        self.play(Create(pista1), run_time=0.5)
        self.add(marcador, num1)
        self.play(v1.animate.set_value(0.318), run_time=1.6, rate_func=smooth)
        marcador.clear_updaters()
        self.remove(marcador)
        self.add(cab1)
        self.play(Create(poste1), run_time=0.4)
        num1.clear_updaters()
        l_g1 = et("G1", 26, C_OK).move_to([x1 + 0.5, yg + 0.33, 0])
        abierto = rayo_abierto(x1, xb - x1 + 0.3, yg, C_OK, alto=0.09)
        self.play(FadeIn(l_g1), LaggedStart(*[FadeIn(r) for r in abierto], lag_ratio=0.04), run_time=1.1)
        self.respiro(0.4)

        # la holgura del lema: no acotada (banda abierta, sin techo)
        x0 = X(0.095)
        holgura = banda_vertical(x0, x1, yl + 0.02, 3.6, TENUE, op0=0.34)
        l_hol = et("Holgura no acotada", 24, TINTA).move_to([(x0 + xu) / 2, 0.15, 0])
        self.play(LaggedStart(*[FadeIn(r) for r in holgura], lag_ratio=0.03), run_time=1.6)
        self.play(FadeIn(l_hol, shift=UP * 0.1), run_time=0.6)
        self.respiro(0.5)

        # tramo 2: G2b lo establece construyendo una política → margen alcanzable ≥ 0.095
        yb = -2.25
        v2 = ValueTracker(0)
        barra2 = always_redraw(lambda: Rectangle(width=max(X(v2.get_value()) - xa, 0.001), height=0.22, stroke_width=0,
                                                 fill_color=C_OK, fill_opacity=0.75)
                               .move_to([(xa + X(v2.get_value())) / 2, yb, 0]))
        poste2 = Line([x0, yb, 0], [x0, yl, 0], color=C_OK, stroke_width=4)
        num2 = DecimalNumber(0.095, num_decimal_places=3, font_size=34, color=C_OK)
        num2.set_stroke(width=0)
        num2.next_to([x0, yb - 0.32, 0], RIGHT, buff=0.25)
        l_g2 = et("G2b", 26, C_OK).next_to(num2, RIGHT, buff=0.25)
        pista2 = DashedLine([xa, yb, 0], [xb, yb, 0], color=C_EJE, stroke_width=2, dash_length=0.08)
        self.play(Create(pista2), run_time=0.5)
        self.add(barra2)
        self.play(v2.animate.set_value(0.095), run_time=1.4, rate_func=smooth)
        self.play(Create(poste2), FadeIn(num2), FadeIn(l_g2), run_time=0.7)
        self.respiro(0.4)

        # el par: dos tramos, no un número
        par = Line([x0, yl, 0], [x1, yl, 0], color=C_OK, stroke_width=10)
        cor_i = VGroup(Line([x0, yl - 0.28, 0], [x0, yl + 0.28, 0]), Line([x0, yl - 0.28, 0], [x0 + 0.16, yl - 0.28, 0]),
                       Line([x0, yl + 0.28, 0], [x0 + 0.16, yl + 0.28, 0])).set_stroke(C_OK, 5)
        cor_d = VGroup(Line([x1, yl - 0.28, 0], [x1, yl + 0.28, 0]), Line([x1, yl - 0.28, 0], [x1 - 0.16, yl - 0.28, 0]),
                       Line([x1, yl + 0.28, 0], [x1 - 0.16, yl + 0.28, 0])).set_stroke(C_OK, 5)
        self.play(Create(cor_d), run_time=0.4)
        self.play(Create(cor_i), run_time=0.4)
        self.play(Create(par), run_time=0.9)
        self.play(FadeIn(chip_desarrollo()), Indicate(num1, color=C_OK, scale_factor=1.12),
                  Indicate(num2, color=C_OK, scale_factor=1.12), run_time=0.8)
        self.respiro(1.2)
        self.cierre()


# =============================================================================
# 7. Sensibilidad de MA al número de episodios (diapositiva 14)
# =============================================================================
class SensibilidadEpisodios(Pieza):
    def construct(self):
        ax = Axes(x_range=[0, 32, 1], y_range=[0, 0.35, 0.05], x_length=9.4, y_length=5.3, tips=False,
                  axis_config={"color": C_EJE, "stroke_width": 2.5, "include_ticks": False}).move_to([-0.6, -0.1, 0])
        ep = [1, 5, 10, 30]
        ma = [0.199, 0.288, 0.307, 0.318]
        tx = VGroup()
        for e in ep + [20]:
            p = ax.c2p(e, 0)
            tx.add(Line(p + DOWN * 0.1, p + UP * 0.1, color=C_EJE, stroke_width=2.5))
        lx = VGroup(*[et(str(e), 22, TENUE).next_to(ax.c2p(e, 0), DOWN, buff=0.2) for e in ep])
        ty, ly = VGroup(), VGroup()
        for v in (0.1, 0.2, 0.3):
            p = ax.c2p(0, v)
            ty.add(Line(p + LEFT * 0.1, p + RIGHT * 0.1, color=C_EJE, stroke_width=2.5))
            ly.add(et(f"{v:.1f}", 20, TENUE).next_to(p, LEFT, buff=0.2))
        l_ex = et("Episodios", 22, TENUE).next_to(ax.x_axis.get_end(), RIGHT, buff=0.25)
        l_ey = et("MA", 24, TENUE).next_to(ax.y_axis.get_end(), UP, buff=0.18)
        self.play(Create(ax), run_time=0.9)
        self.play(FadeIn(tx), FadeIn(lx), FadeIn(ty), FadeIn(ly), FadeIn(l_ex), FadeIn(l_ey), run_time=0.8)

        umb = DashedLine(ax.c2p(0, 0.25), ax.c2p(32, 0.25), color=C_CIELO, stroke_width=3, dash_length=0.14)
        l_umb = et("Umbral 0.25", 22, C_CIELO).next_to(ax.c2p(32, 0.25), RIGHT, buff=0.15)
        self.play(Create(umb), FadeIn(l_umb), run_time=0.9)

        # zona convergida (se sombrea al final)
        z0, z1 = ax.c2p(10, 0), ax.c2p(30, 0.35)
        zona = Rectangle(width=z1[0] - z0[0], height=z1[1] - z0[1], stroke_width=0, fill_color=C_OK,
                         fill_opacity=0.1).move_to((z0 + z1) / 2)

        puntos = [ax.c2p(e, v) for e, v in zip(ep, ma)]
        desp = [DR * 0.35 + RIGHT * 0.25, UL * 0.3 + LEFT * 0.2 + UP * 0.05, UP * 0.42, UP * 0.42]
        tramos, marcas, cifras = [], [], []
        for k, (p, v) in enumerate(zip(puntos, ma)):
            d = Dot(p, radius=0.1, color=C_ANT).set_z_index(3)
            n = DecimalNumber(v, num_decimal_places=3, font_size=26, color=TINTA)
            n.set_stroke(width=0)
            n.move_to(p + desp[k])
            if k:
                tr_ = Line(puntos[k - 1], p, color=C_ANT, stroke_width=4)
                self.play(Create(tr_), run_time=1.0 if k < 3 else 1.6, rate_func=linear)
                tramos.append(tr_)
            if k == 1:
                # el cruce del umbral ocurre entre 1 y 5 episodios
                t = (0.25 - ma[0]) / (ma[1] - ma[0])
                xc = ep[0] + t * (ep[1] - ep[0])
                anillo = Circle(radius=0.2, color=C_CIELO, stroke_width=3).move_to(ax.c2p(xc, 0.25))
                self.play(Create(anillo), Flash(ax.c2p(xc, 0.25), color=C_CIELO, flash_radius=0.35,
                                                  line_length=0.12), run_time=0.6)
            self.play(FadeIn(d, scale=0.4), FadeIn(n, shift=UP * 0.1), run_time=0.5)
            marcas.append(d)
            cifras.append(n)
        l_conv = et("Convergida", 24, C_OK).move_to(ax.c2p(20, 0.335))
        self.play(FadeIn(zona), FadeIn(l_conv), *[m.animate.set_color(C_OK) for m in marcas[2:]], run_time=1.0)
        self.play(Indicate(cifras[3], color=C_OK, scale_factor=1.15), run_time=0.7)
        self.play(FadeIn(chip_desarrollo()), run_time=0.4)
        self.respiro(2.2)
        self.cierre()

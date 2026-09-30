"""Seminario de divulgación, bloques 4–6: margen adaptativo, compuerta, recorrido 1.7 %→31.8 %, resultados y prisa."""
from tesis_lib import *
import numpy as np


# ---------------------------------------------------------------------------
# helpers locales
# ---------------------------------------------------------------------------
def mezcla(a, b, t):
    """interpolate_color que acepta los colores de la paleta (cadenas hex)."""
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(t, 0, 1)))


def sello(texto, color, tam=30, ang=10 * DEGREES):
    """Sello de goma: texto en marco doble, girado."""
    t = et(texto, tam, color, weight=BOLD)
    r1 = RoundedRectangle(corner_radius=0.1, width=t.width + 0.5, height=t.height + 0.36,
                          stroke_color=color, stroke_width=4, fill_color=FONDO, fill_opacity=0.9)
    r2 = RoundedRectangle(corner_radius=0.07, width=t.width + 0.34, height=t.height + 0.2,
                          stroke_color=color, stroke_width=1.5, fill_opacity=0)
    t.move_to(r1)
    return VGroup(r1, r2, t).rotate(ang)


def estampar(m, t=0.45):
    """Animación de sello que cae y se clava."""
    return FadeIn(m, scale=1.8, rate_func=rush_into, run_time=t)


def reloj(radio=0.42, color=None):
    c = color or TENUE
    aro = Circle(radius=radio, color=c, stroke_width=3, fill_color=C_PANEL, fill_opacity=0.6)
    marcas = VGroup(*[Line(radio * 0.78 * np.array([np.cos(a), np.sin(a), 0]),
                           radio * 0.95 * np.array([np.cos(a), np.sin(a), 0]), color=c, stroke_width=2)
                      for a in np.linspace(0, TAU, 12, endpoint=False)])
    aguja = Line(ORIGIN, UP * radio * 0.7, color=TINTA, stroke_width=4)
    eje = Dot(radius=0.04, color=TINTA)
    return VGroup(aro, marcas, aguja, eje)


def red_mezcla(ancho=2.0, alto=1.5, color=None):
    """Caja con red densa (mezclador no lineal)."""
    c = color or C_ANT
    caja_ = RoundedRectangle(corner_radius=0.14, width=ancho, height=alto, color=c,
                             fill_color=c, fill_opacity=0.10, stroke_width=2.5)
    capas = [4, 5, 5, 3]
    xs = np.linspace(-ancho * 0.36, ancho * 0.36, len(capas))
    nodos = []
    for x, n in zip(xs, capas):
        ys = np.linspace(-alto * 0.34, alto * 0.34, n)
        nodos.append([np.array([x, y, 0]) for y in ys])
    aristas = VGroup()
    for a, b in zip(nodos[:-1], nodos[1:]):
        for p in a:
            for q in b:
                aristas.add(Line(p, q, color=c, stroke_width=1.2, stroke_opacity=0.6))
    puntos = VGroup(*[Dot(p, radius=0.055, color=c) for capa in nodos for p in capa])
    return VGroup(caja_, aristas, puntos)


# =============================================================================
# 1. La idea sin fórmulas: terreno con relieve vs. terreno llano
# =============================================================================
class MargenAdaptativoIdea(Pieza):
    """MA (TEOREMA_MARGEN_ADAPTATIVO §1–2.2): cuánto gana la mejor política que se adapta frente a la
    mejor fija. Metáfora: carrera sobre un terreno. Con relieve, la ruta que rodea las colinas llega mucho
    antes que la recta (margen grande ✓). En llano, ambas llegan juntas (margen cero ✗)."""

    def construct(self):
        CA, CB = np.array([-3.55, 0.25, 0]), np.array([3.55, 0.25, 0])
        W, H = 6.2, 4.1
        C_TER = mezcla(C_EJE, TENUE, 0.35)
        C_FIJA, C_ADA = TENUE, C_CIELO

        # colinas (x, y, amplitud, sigma) en coordenadas locales del panel
        colinas = [(-1.2, 0.0, 1.0, 0.45), (1.1, 0.0, 1.0, 0.45),
                   (-0.05, 1.35, 0.7, 0.3), (0.0, -1.35, 0.7, 0.3), (-2.2, 1.35, 0.6, 0.28),
                   (2.25, -1.35, 0.6, 0.28)]

        def h(p):
            return sum(a * np.exp(-((p[0] - cx) ** 2 + (p[1] - cy) ** 2) / (2 * s * s)) for cx, cy, a, s in colinas)

        def panel(centro):
            return RoundedRectangle(corner_radius=0.2, width=W, height=H, color=C_EJE, stroke_width=2,
                                    fill_color=C_PANEL, fill_opacity=0.35).move_to(centro)

        def relieve(centro):
            g = VGroup()
            for cx, cy, a, s in colinas:
                for k, f in enumerate((2.0, 1.4, 0.8)):
                    g.add(Circle(radius=s * f, color=C_TER, stroke_width=1.6,
                                 stroke_opacity=0.9, fill_color=C_TER, fill_opacity=0.10 + 0.06 * k)
                          .move_to(centro + np.array([cx, cy, 0])))
            return g

        S, G = np.array([-2.65, 0, 0]), np.array([2.65, 0, 0])

        def meta(centro):
            return VGroup(Dot(centro + S, radius=0.09, color=TINTA),
                          Line(centro + G + UP * 0.45, centro + G + DOWN * 0.45, color=TINTA, stroke_width=5))

        # rutas (locales)
        recta_l = Line(S, G)
        ada_l = VMobject().set_points_smoothly([S, np.array([-1.9, -0.45, 0]), np.array([-1.2, -0.95, 0]),
                                                np.array([-0.05, 0.0, 0]), np.array([1.1, 0.95, 0]),
                                                np.array([1.9, 0.45, 0]), G])

        def cronometro(ruta_l, relieve_on=True, n=500):
            ps = np.array([ruta_l.point_from_proportion(u) for u in np.linspace(0, 1, n)])
            ds = np.linalg.norm(np.diff(ps, axis=0), axis=1)
            mid = 0.5 * (ps[1:] + ps[:-1])
            v = np.array([1.0 / (1.0 + 8.0 * h(p)) if relieve_on else 1.0 for p in mid])
            t = np.concatenate([[0], np.cumsum(ds / v)])
            return ps, t

        def en(ps, t, tau, centro, dy=0.0):
            tau = min(tau, t[-1])
            x = np.interp(tau, t, ps[:, 0])
            y = np.interp(tau, t, ps[:, 1])
            return centro + np.array([x, y + dy, 0])

        # ---- leyenda
        ley = VGroup(
            VGroup(Line(LEFT * 0.3, RIGHT * 0.3, color=C_FIJA, stroke_width=6), et("Mejor fija", 24, TINTA)).arrange(RIGHT, buff=0.18),
            VGroup(Line(LEFT * 0.3, RIGHT * 0.3, color=C_ADA, stroke_width=6), et("Mejor adaptable", 24, TINTA)).arrange(RIGHT, buff=0.18),
        ).arrange(RIGHT, buff=0.9).move_to([0, 3.25, 0])

        # ---- panel A (con relieve)
        pA, rA, mA = panel(CA), relieve(CA), meta(CA)
        self.play(FadeIn(pA), FadeIn(mA), LaggedStart(*[FadeIn(c, scale=0.6) for c in rA], lag_ratio=0.04),
                  run_time=1.6)
        rectaA = recta_l.copy().shift(CA).set_stroke(C_FIJA, 5)
        adaA = ada_l.copy().shift(CA).set_stroke(C_ADA, 5).set_fill(opacity=0)
        self.play(FadeIn(ley[0]), Create(rectaA), run_time=1.0)
        self.play(FadeIn(ley[1]), Create(adaA), run_time=1.2)

        psF, tF = cronometro(recta_l)
        psA, tA = cronometro(ada_l)
        tau = ValueTracker(0)
        dF = Dot(radius=0.13, color=C_FIJA).set_z_index(5)
        dA = Dot(radius=0.13, color=C_ADA).set_z_index(5)
        dF.add_updater(lambda m: m.move_to(en(psF, tF, tau.get_value(), CA)))
        dA.add_updater(lambda m: m.move_to(en(psA, tA, tau.get_value(), CA)))
        self.add(dF, dA)
        self.play(tau.animate.set_value(tA[-1]), run_time=3.6, rate_func=linear)
        dF.clear_updaters()
        dA.clear_updaters()
        # brecha: lo que le falta a la fija cuando la adaptable ya llegó
        brecha = Line(dF.get_center(), CA + G, color=C_OK, stroke_width=12, stroke_opacity=0.85).set_z_index(4)
        self.play(Create(brecha), Flash(CA + G, color=C_ADA, flash_radius=0.35), run_time=0.8)
        resA = VGroup(marca_ok(tam=0.34), et("Margen grande", 28, C_OK)).arrange(RIGHT, buff=0.22)
        resA.move_to([CA[0], -2.35, 0])
        self.play(FadeIn(resA, shift=UP * 0.2), Indicate(brecha, color=C_OK, scale_factor=1.05), run_time=1.0)
        self.respiro(0.8)

        # ---- panel B (llano)
        pB, mB = panel(CB), meta(CB)
        rejilla = VGroup(*[Dot(CB + np.array([x, y, 0]), radius=0.022, color=C_TER)
                           for x in np.linspace(-2.7, 2.7, 13) for y in np.linspace(-1.75, 1.75, 8)])
        self.play(FadeIn(pB), FadeIn(rejilla), FadeIn(mB), run_time=1.0)
        rectaB = recta_l.copy().shift(CB + UP * 0.07).set_stroke(C_FIJA, 5)
        adaB = ada_l.copy().shift(CB).set_stroke(C_ADA, 5).set_fill(opacity=0)
        adaB_rect = recta_l.copy().shift(CB + DOWN * 0.07).set_stroke(C_ADA, 5)
        self.play(Create(rectaB), Create(adaB), run_time=1.0)
        # sin relieve, lo mejor que puede hacer la adaptable es ir recto
        self.play(Transform(adaB, adaB_rect), run_time=1.0)

        psB, tB = cronometro(recta_l, relieve_on=False)
        tau2 = ValueTracker(0)
        eF = Dot(radius=0.13, color=C_FIJA).set_z_index(5)
        eA = Dot(radius=0.13, color=C_ADA).set_z_index(5)
        eF.add_updater(lambda m: m.move_to(en(psB, tB, tau2.get_value(), CB, 0.07)))
        eA.add_updater(lambda m: m.move_to(en(psB, tB, tau2.get_value(), CB, -0.07)))
        self.add(eF, eA)
        self.play(tau2.animate.set_value(tB[-1]), run_time=2.4, rate_func=linear)
        eF.clear_updaters()
        eA.clear_updaters()
        self.play(Flash(CB + G, color=TENUE, flash_radius=0.35), run_time=0.5)
        resB = VGroup(marca_no(tam=0.3), et("Margen cero", 28, C_MAL)).arrange(RIGHT, buff=0.22)
        resB.move_to([CB[0], -2.35, 0])
        self.play(FadeIn(resB, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(chip_desarrollo()), run_time=0.5)
        self.respiro(1.2)
        self.cierre()


# =============================================================================
# 2. La compuerta se fija ANTES de correr
# =============================================================================
class CompuertaAntesDeCorrer(Pieza):
    """Protocolo de la tesis: umbral de MA (25 %) pre-registrado antes de correr. Dos entornos: el que pasa
    abre su barrera y sus resultados salen; el que no pasa: sus resultados se desvanecen (no se reportan)."""

    def construct(self):
        Y = [1.05, -1.45]
        X0, XU, XG = -5.1, -1.9, 1.35       # inicio de barra, umbral, barrera
        largo = [1.5 + (XU - X0), 0.62 * (XU - X0)]  # A pasa; B se queda corto
        self.add(chip_desarrollo())

        # ---- entornos, pistas y barreras
        filas = []
        for k, y in enumerate(Y):
            icono = RoundedRectangle(corner_radius=0.12, width=0.9, height=0.9, color=C_ANT,
                                     fill_color=C_ANT, fill_opacity=0.12, stroke_width=2.5).move_to([-6.05, y, 0])
            sat = satelite(0.14).move_to(icono.get_center() + UP * 0.14)
            est = estacion(0.26).move_to(icono.get_center() + DOWN * 0.22)
            pista = Rectangle(width=XG - 0.35 - X0, height=0.5, color=C_EJE, stroke_width=2,
                              fill_color=C_PANEL, fill_opacity=0.5)
            pista.move_to([X0 + pista.width / 2, y, 0])
            poste = RoundedRectangle(corner_radius=0.05, width=0.2, height=0.34, color=TENUE,
                                     fill_color=TENUE, fill_opacity=0.8, stroke_width=1.5).move_to([XG, y + 0.72, 0])
            brazo = Rectangle(width=0.14, height=1.25, color=TINTA, fill_color=TINTA, fill_opacity=0.85,
                              stroke_width=1.5).move_to([XG, y, 0])
            rayas = VGroup(*[Rectangle(width=0.14, height=0.16, stroke_width=0, fill_color=C_MAL, fill_opacity=0.9)
                             .move_to([XG, y + 0.42 - 0.28 * j, 0]) for j in range(4)])
            barrera = VGroup(brazo, rayas)
            filas.append(dict(y=y, icono=VGroup(icono, sat, est), pista=pista, poste=poste, barrera=barrera))
        self.play(LaggedStart(*[AnimationGroup(FadeIn(f["icono"]), FadeIn(f["pista"]), FadeIn(f["poste"]),
                                               FadeIn(f["barrera"])) for f in filas], lag_ratio=0.3), run_time=1.4)

        # ---- primero: el umbral se clava (reloj en las 12)
        rl = reloj().move_to([-6.05, 3.05, 0])
        linea = DashedLine([XU, -2.35, 0], [XU, 2.05, 0], color=C_CIELO, stroke_width=5, dash_length=0.16)
        clavos = VGroup(Dot([XU, -2.35, 0], radius=0.09, color=C_CIELO), Dot([XU, 2.05, 0], radius=0.09, color=C_CIELO))
        l_umb = et("Umbral 25 %", 26, C_CIELO).move_to([XU, -2.75, 0])
        sel = sello("Pre-registrado", C_CIELO, 30, ang=6 * DEGREES).move_to([XU + 0.2, 2.75, 0])
        self.play(FadeIn(rl), run_time=0.5)
        self.play(Create(linea), FadeIn(l_umb), run_time=1.0)
        self.play(estampar(sel), run_time=0.45)
        self.play(FadeIn(clavos, scale=2), Wiggle(sel, scale_value=1.04, rotation_angle=0.01 * TAU), run_time=0.7)
        self.respiro(0.4)

        # ---- después: pasa el tiempo, se mide cada entorno y aparecen sus resultados
        barras = []
        for k, f in enumerate(filas):
            b = Rectangle(width=0.001, height=0.36, stroke_width=0, fill_color=C_ANT, fill_opacity=0.85)
            b.move_to([X0, f["y"], 0], aligned_edge=LEFT)
            barras.append(b)
        self.add(*barras)
        tr = ValueTracker(0)

        def crecer(k):
            def act(m):
                w = max(1e-3, largo[k] * tr.get_value())
                m.stretch_to_fit_width(w).move_to([X0, filas[k]["y"], 0], aligned_edge=LEFT)
                m.set_fill(C_OK if X0 + w >= XU else (C_ANT if k == 0 else mezcla(C_ANT, C_MAL, tr.get_value())))
            return act
        for k, b in enumerate(barras):
            b.add_updater(crecer(k))

        def tarjeta(pos, semilla):
            rng = np.random.default_rng(semilla)
            r = RoundedRectangle(corner_radius=0.06, width=0.62, height=0.46, color=TENUE, stroke_width=1.5,
                                 fill_color=C_PANEL, fill_opacity=0.9)
            xs = np.linspace(-0.22, 0.22, 7)
            ys = np.clip(-0.13 + 0.05 * np.arange(7) + rng.normal(0, 0.03, 7), -0.17, 0.17)
            return VGroup(r, trazo(xs, ys, C_SAT, 2.5)).move_to(pos)

        cartas = [VGroup(*[tarjeta([XG - 1.2 + 0.1 * j, f["y"] + 0.07 * (1 - j), 0], 42 + 3 * k + j)
                           for j in range(3)]) for k, f in enumerate(filas)]
        self.play(Rotate(rl[2], angle=-1.25 * TAU, about_point=rl[3].get_center()),
                  tr.animate.set_value(1), LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in cartas[0]],
                                                       *[FadeIn(c, shift=RIGHT * 0.2) for c in cartas[1]], lag_ratio=0.25),
                  run_time=3.4, rate_func=smooth)
        for b in barras:
            b.clear_updaters()
        self.play(Flash([XU, Y[0], 0], color=C_OK, flash_radius=0.45), run_time=0.6)

        # ---- A: pasa -> la barrera se levanta y salen los resultados
        fa = filas[0]
        pivote = fa["barrera"].get_top()
        fa["barrera"][1].set_fill(C_OK)
        self.play(Rotate(fa["barrera"], angle=80 * DEGREES, about_point=pivote), run_time=0.8)
        destinos = [[3.05 + 0.85 * j, fa["y"], 0] for j in range(3)]
        self.play(LaggedStart(*[c.animate.move_to(d) for c, d in zip(cartas[0], destinos)], lag_ratio=0.2),
                  run_time=1.3)
        okA = VGroup(marca_ok(tam=0.34), et("Pasa", 28, C_OK)).arrange(RIGHT, buff=0.2).next_to(cartas[0], RIGHT, buff=0.3)
        self.play(FadeIn(okA, shift=LEFT * 0.2), run_time=0.6)

        # ---- B: no pasa -> barrera cerrada, sus resultados se desvanecen
        fb = filas[1]
        self.play(Wiggle(fb["barrera"], scale_value=1.06, rotation_angle=0.02 * TAU),
                  fb["barrera"][0].animate.set_fill(C_MAL).set_stroke(C_MAL), run_time=0.8)
        self.play(LaggedStart(*[c.animate.shift(DOWN * 0.35).set_opacity(0) for c in cartas[1]], lag_ratio=0.2),
                  run_time=1.4)
        noB = VGroup(marca_no(tam=0.3), et("No se reportan", 28, C_MAL)).arrange(RIGHT, buff=0.2)
        noB.move_to([4.2, fb["y"], 0])
        self.play(FadeIn(noB, shift=LEFT * 0.2), run_time=0.6)
        self.respiro(1.4)
        self.cierre()


# =============================================================================
# 3. Recorrido del margen: v1 1.7 % -> mock anulado -> v2 31.8 % (alcanzable 9.5 %)
# =============================================================================
class RecorridoDelMargen(Pieza):
    """Figura central. MA de NTNEnv-v1 (G0) = 0.0171 = 1.7 %; MA de NTNEnv-v2 (G1) = 0.318 frente al
    umbral pre-registrado 0.25, con el margen alcanzable medido en G2b = 0.095 (par [0.095, 0.318]);
    remate: banco mock (SimplifiedNTNEnv) con recompensas imposibles, anulado por el protocolo (regla R5)."""

    def construct(self):
        Y0, K = -2.3, 0.13          # base y unidades por punto porcentual
        XV1, XV2, XM = -4.6, -0.9, 3.75       # orden cronológico: v1 -> v2 (+G2b) -> mock
        ANCHO = 1.25
        MA1, MA2, MADEC, UMB = 1.71, 31.8, 9.5, 25.0

        def y(p):
            return Y0 + K * p

        eje = Arrow([-6.5, Y0, 0], [6.6, Y0, 0], buff=0, color=C_EJE, stroke_width=4, tip_length=0.22,
                    max_tip_length_to_length_ratio=0.05)
        hitos = VGroup(*[Dot([x, Y0, 0], radius=0.09, color=TENUE) for x in (XV1, XM, XV2)]).set_z_index(-1)
        umb = DashedLine([-6.5, y(UMB), 0], [6.5, y(UMB), 0], color=C_CIELO, stroke_width=4, dash_length=0.16)
        l_umb = et("Umbral 25 %", 24, C_CIELO).next_to(umb, UP, buff=0.1).align_to([6.5, 0, 0], RIGHT)
        self.add(chip_desarrollo())
        self.play(GrowArrow(eje), FadeIn(hitos), run_time=0.9)
        self.play(Create(umb), FadeIn(l_umb), run_time=0.9)

        cursor = Triangle(color=TINTA, fill_color=TINTA, fill_opacity=1, stroke_width=0).scale(0.12)
        cursor.rotate(PI).move_to([-6.3, Y0 + 0.2, 0])

        def barra_viva(x, valor_max, nombre, color_fn):
            t = ValueTracker(0)
            b = Rectangle(width=ANCHO, height=0.001, stroke_width=2, fill_opacity=0.85)

            def act(m):
                v = t.get_value()
                c = color_fn(v)
                m.become(Rectangle(width=ANCHO, height=max(1e-3, K * v), stroke_width=2, color=c,
                                   fill_color=c, fill_opacity=1).move_to([x, Y0, 0], aligned_edge=DOWN))
                m.set_z_index(2)
            b.add_updater(act)
            num = DecimalNumber(0, num_decimal_places=1, font_size=30, color=TINTA)
            num.set_stroke(width=0)
            nom = et(nombre, 30, TINTA)
            pct = et("%", 30, TENUE)
            lab = VGroup(nom, num, pct)

            def act_lab(m):
                v = t.get_value()
                num.set_value(v)
                c = color_fn(v)
                num.set_color(c)
                nom.set_color(c)
                m.arrange(RIGHT, buff=0.12, aligned_edge=DOWN).move_to([x, Y0 - 0.5, 0])
            lab.add_updater(act_lab)
            return t, b, lab

        # ---- hito 1: banco v1
        self.play(cursor.animate.move_to([XV1, Y0 + 0.2, 0]), FadeIn(cursor), run_time=0.8)
        t1, b1, lab1 = barra_viva(XV1, MA1, "v1", lambda v: C_MAL)
        self.add(b1, lab1)
        self.play(t1.animate.set_value(MA1), run_time=1.2)
        x1 = marca_no(pos=np.array([XV1, y(MA1) + 0.55, 0]), tam=0.36)
        self.play(FadeIn(x1, scale=0.5), Indicate(lab1, color=C_MAL, scale_factor=1.1), run_time=0.8)
        b1.clear_updaters()
        lab1.clear_updaters()
        self.respiro(0.6)

        # ---- hito 2: banco v2 — cruza el umbral; luego, lo alcanzable medido en G2b
        self.play(cursor.animate.move_to([XV2, Y0 + 0.2, 0]), run_time=0.8)
        t2, b2, lab2 = barra_viva(XV2, MA2, "v2", lambda v: C_OK if v >= UMB else mezcla(C_MAL, C_SAT, v / UMB))
        self.add(b2, lab2)
        self.play(t2.animate.set_value(MA2), run_time=2.4, rate_func=smooth)
        b2.clear_updaters()
        lab2.clear_updaters()
        ok2 = marca_ok(pos=np.array([XV2, y(MA2) + 0.45, 0]), tam=0.38)
        self.play(Flash([XV2, y(UMB), 0], color=C_OK, flash_radius=0.5), FadeIn(ok2, scale=0.5), run_time=0.7)

        # muesca: lo alcanzable medido (G2b) dentro de la envolvente
        base_dec = Rectangle(width=ANCHO, height=K * MADEC, stroke_width=0, fill_color=C_OK,
                             fill_opacity=1).move_to([XV2, Y0, 0], aligned_edge=DOWN).set_z_index(3)
        tope = Line([XV2 - ANCHO / 2 - 0.12, y(MADEC), 0], [XV2 + ANCHO / 2 + 0.12, y(MADEC), 0],
                    color=TINTA, stroke_width=5).set_z_index(4)
        l_dec = et("Alcanzable 9.5 %", 24, TINTA).next_to(tope, RIGHT, buff=0.15)
        self.play(b2.animate.set_fill(opacity=0.4), FadeIn(base_dec), run_time=0.6)
        self.play(Create(tope), FadeIn(l_dec, shift=LEFT * 0.2), run_time=0.8)
        self.respiro(0.8)
        # ---- hito 3: banco mock — resultados espectaculares que el protocolo anula (remate)
        self.play(cursor.animate.move_to([XM, Y0 + 0.2, 0]), run_time=0.8)
        tarj = RoundedRectangle(corner_radius=0.12, width=2.3, height=2.1, color=TENUE, stroke_width=2,
                                fill_color=FONDO, fill_opacity=1).move_to([XM, Y0 + 1.45, 0]).set_z_index(2)
        esq = tarj.get_corner(DL) + np.array([0.3, 0.3, 0])
        ejes_m = VGroup(Line(esq, esq + RIGHT * 1.75, color=C_EJE, stroke_width=2.5),
                        Line(esq, esq + UP * 1.55, color=C_EJE, stroke_width=2.5)).set_z_index(3)
        us = np.linspace(0, 1, 60)
        xs = esq[0] + 0.05 + 1.65 * us
        ys = esq[1] + 0.1 + 0.25 * us + 3.4 * us ** 4          # se dispara fuera de su propio marco
        curva_m = trazo(xs, ys, C_SAT, 5).set_z_index(4)
        l_mock = et("Mock", 30, TENUE).move_to([XM, Y0 - 0.5, 0])
        self.play(FadeIn(tarj), Create(ejes_m), FadeIn(l_mock), run_time=0.7)
        self.play(Create(curva_m), run_time=1.3, rate_func=rush_into)
        self.play(Flash(curva_m.get_end(), color=C_SAT, flash_radius=0.35), run_time=0.4)
        anul = sello("Anulado", C_MAL, 34, ang=14 * DEGREES).move_to([XM, Y0 + 1.5, 0]).set_z_index(6)
        self.play(estampar(anul), run_time=0.45)
        self.play(curva_m.animate.set_stroke(TENUE, opacity=0.35), ejes_m.animate.set_opacity(0.35),
                  tarj.animate.set_stroke(opacity=0.4), run_time=0.7)
        self.play(FadeOut(cursor), Wiggle(anul, scale_value=1.05, rotation_angle=0.01 * TAU), run_time=0.7)
        self.respiro(1.4)

        self.cierre()


# =============================================================================
# 4. Con el instrumento certificado: QMIX frente a la mejor estática (G2b, 3 semillas)
# =============================================================================
# Datos de 03_IMPLEMENTACION/results/gates/G2B_RECUALIFICACION_v7.json (per_seed):
#   seed, best_static, reward_mean (QMIX), oracle, mejora_vs_static_pct, frac_oracle
G2B_V7 = [
    (42, 9504.431498297055, 11056.394813330173, 12757.823030853271, 16.328838976967617, 0.8666364776021428),
    (43, 9865.560092918078, 11016.560312862099, 12975.667002487182, 11.666851239092434, 0.8490168798837423),
    (44, 9989.518851058681, 10943.052587216198, 12943.57089176178, 9.545341976670496, 0.8454430913018868),
]


class AlgoritmoVsEstatica(Pieza):
    """G2b (2026-07-23): QMIX supera a la mejor política estática en 3/3 semillas (+9.5 % a +16.3 %) y
    alcanza 84–87 % de la política con información privilegiada (cota inferior del óptimo).
    Barras desde cero; la semilla 43 se dibuja con su dato pero sin cifra (no está en la tabla de cifras)."""

    def construct(self):
        Y0 = -2.35
        ESC = 4.55 / 13000.0            # unidades por punto de recompensa (barras desde cero)
        GX = [-4.7, -1.75, 1.2]
        AB, SEP = 0.82, 0.47
        C_EST = TENUE
        self.add(chip_desarrollo())

        base = Line([-6.2, Y0, 0], [2.6, Y0, 0], color=C_EJE, stroke_width=3)
        ley = VGroup(
            VGroup(Square(0.26, color=C_EST, fill_color=C_EST, fill_opacity=0.85), et("Mejor estática", 24, TINTA)).arrange(RIGHT, buff=0.15),
            VGroup(Square(0.26, color=C_OK, fill_color=C_OK, fill_opacity=0.85), et("QMIX", 24, TINTA)).arrange(RIGHT, buff=0.15),
            VGroup(DashedLine(LEFT * 0.3, RIGHT * 0.3, color=C_CIELO, stroke_width=5, dash_length=0.1),
                   et("Información privilegiada", 24, TINTA)).arrange(RIGHT, buff=0.15),
        ).arrange(RIGHT, buff=0.6).move_to([-0.55, 3.3, 0])
        semillas = VGroup(*[et(f"Semilla {s}", 22, TENUE).move_to([x, Y0 - 0.38, 0]) for x, (s, *_ ) in zip(GX, G2B_V7)])
        self.play(Create(base), FadeIn(semillas), FadeIn(ley[0]), run_time=1.0)

        est = [barra(x - SEP, Y0, ESC * d[1], AB, C_EST) for x, d in zip(GX, G2B_V7)]
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in est], lag_ratio=0.25), run_time=1.6)
        # guía: altura de la estática prolongada hacia QMIX
        guias = VGroup(*[DashedLine([x - SEP - AB / 2, Y0 + ESC * d[1], 0], [x + SEP + AB / 2, Y0 + ESC * d[1], 0],
                                    color=C_EST, stroke_width=2, dash_length=0.08)
                         for x, d in zip(GX, G2B_V7)])
        self.play(FadeIn(guias), run_time=0.4)

        qm = [barra(x + SEP, Y0, ESC * d[2], AB, C_OK) for x, d in zip(GX, G2B_V7)]
        self.play(FadeIn(ley[1]), LaggedStart(*[GrowFromEdge(b, DOWN) for b in qm], lag_ratio=0.25), run_time=1.8)

        # ganancia de cada semilla: franja sobre la altura de la estática
        ganancias = VGroup()
        etiquetas = VGroup()
        for x, d in zip(GX, G2B_V7):
            y_est, y_q = Y0 + ESC * d[1], Y0 + ESC * d[2]
            g = Rectangle(width=AB, height=y_q - y_est, stroke_width=2.5, stroke_color=TINTA,
                          fill_color=mezcla(C_OK, TINTA, 0.35), fill_opacity=1)
            g.move_to([x + SEP, (y_est + y_q) / 2, 0])
            ganancias.add(g)
            if d[0] in (42, 44):
                txt = f"+{d[4]:.1f} %"   # 16.3 / 9.5 (redondeo del JSON)
                etiquetas.add(et(txt, 24, C_OK).next_to(g, UP, buff=0.08))
        self.play(LaggedStart(*[FadeIn(g, scale=1.15) for g in ganancias], lag_ratio=0.2),
                  LaggedStart(*[FadeIn(e, shift=UP * 0.15) for e in etiquetas], lag_ratio=0.3), run_time=1.4)
        self.respiro(0.6)

        # techo: política con información privilegiada (por semilla)
        techos = VGroup(*[DashedLine([x - SEP - AB / 2 - 0.1, Y0 + ESC * d[3], 0], [x + SEP + AB / 2 + 0.1, Y0 + ESC * d[3], 0],
                                     color=C_CIELO, stroke_width=5, dash_length=0.12) for x, d in zip(GX, G2B_V7)])
        self.play(FadeIn(ley[2]), LaggedStart(*[Create(t) for t in techos], lag_ratio=0.2), run_time=1.3)
        self.respiro(0.5)

        # medidor: fracción del techo que alcanza QMIX (84–87 %)
        MX, MH, MW = 4.3, 4.3, 0.75
        marco = Rectangle(width=MW, height=MH, color=C_EJE, stroke_width=2.5, fill_color=C_PANEL,
                          fill_opacity=0.5).move_to([MX, Y0, 0], aligned_edge=DOWN)
        tapa = DashedLine([MX - MW / 2 - 0.15, Y0 + MH, 0], [MX + MW / 2 + 0.15, Y0 + MH, 0], color=C_CIELO,
                          stroke_width=5, dash_length=0.12)
        fmin = min(d[5] for d in G2B_V7)
        fmax = max(d[5] for d in G2B_V7)
        tf = ValueTracker(0)
        relleno = always_redraw(lambda: Rectangle(width=MW - 0.08, height=max(1e-3, MH * tf.get_value()), stroke_width=0,
                                                  fill_color=C_OK, fill_opacity=0.85).move_to([MX, Y0 + 0.04, 0], aligned_edge=DOWN))
        rango = Rectangle(width=MW + 0.3, height=MH * (fmax - fmin), stroke_width=0, fill_color=C_OK,
                          fill_opacity=0.45).move_to([MX, Y0 + MH * (fmin + fmax) / 2, 0])
        marcas_r = VGroup(*[Line([MX - MW / 2 - 0.15, Y0 + MH * f, 0], [MX + MW / 2 + 0.15, Y0 + MH * f, 0],
                                 color=C_OK, stroke_width=3) for f in (fmin, fmax)])
        l_frac = et("84–87 %", 30, C_OK).next_to(rango, RIGHT, buff=0.18)
        self.play(FadeIn(marco), Create(tapa), run_time=0.6)
        self.add(relleno)
        self.play(tf.animate.set_value(fmin), run_time=1.5)
        self.play(FadeIn(rango), Create(marcas_r), FadeIn(l_frac, shift=LEFT * 0.2), run_time=0.8)
        self.respiro(1.6)
        self.cierre()


# =============================================================================
# 5. La variante simple no empeora (diagnóstico, n = 3)
# =============================================================================
class VarianteSimpleNoEmpeora(Pieza):
    """Mixer: quitar la mezcla no lineal (QMIX -> suma, tipo VDN) ni arregla el colapso modal ni daña el
    rendimiento; n = 3 semillas, sin potencia estadística para equivalencia -> «diagnóstico».
    Sin cifras: las dos barras se dibujan prácticamente iguales."""

    def construct(self):
        Y = [1.35, -1.55]
        XIN, XMIX, XB0 = -6.1, -3.6, -1.75
        LB = [4.9, 4.84]
        self.add(chip_desarrollo())

        def entradas(y):
            cols = [C_SAT, C_SAT, C_ANT]
            return VGroup(*[Dot([XIN, y + 0.45 - 0.45 * j, 0], radius=0.11, color=c) for j, c in enumerate(cols)])

        ins = [entradas(y) for y in Y]
        red = red_mezcla(2.1, 1.6).move_to([XMIX, Y[0], 0])
        suma = VGroup(Circle(radius=0.5, color=C_ANT, fill_color=C_ANT, fill_opacity=0.12, stroke_width=2.5),
                      Text("+", font=FUENTE, font_size=56, color=C_ANT)).move_to([XMIX, Y[1], 0])
        mezcladores = [red, suma]
        l_red = et("Mezcla no lineal", 24, TINTA).next_to(red, DOWN, buff=0.18)
        l_suma = et("Suma simple", 24, TINTA).next_to(suma, DOWN, buff=0.18)

        cables = []
        for k in range(2):
            m = mezcladores[k]
            g = VGroup(*[Line(d.get_center(), m.get_left() + UP * (0.3 - 0.3 * j) * (1 if k == 0 else 0.7),
                              color=TENUE, stroke_width=2) for j, d in enumerate(ins[k])])
            g.add(Line(m.get_right(), [XB0 - 0.1, Y[k], 0], color=TENUE, stroke_width=2))
            cables.append(g)

        self.play(FadeIn(ins[0]), FadeIn(ins[1]), run_time=0.6)
        self.play(FadeIn(red[0]), LaggedStart(*[Create(a) for a in red[1]], lag_ratio=0.01),
                  FadeIn(red[2]), FadeIn(l_red), Create(cables[0]), run_time=2.0)
        self.play(FadeIn(suma, scale=0.8), FadeIn(l_suma), Create(cables[1]), run_time=1.0)

        # pulsos de decisión que entran y salen de cada mezclador
        pulsos = []
        for k in range(2):
            for j in range(3):
                seg = cables[k][j]
                p = Dot(seg.get_start(), radius=0.07, color=ins[k][j].get_color()).set_z_index(5)
                pulsos.append((p, seg))
        self.play(*[MoveAlongPath(p, s) for p, s in pulsos], run_time=1.0, rate_func=smooth)
        self.play(*[FadeOut(p) for p, _ in pulsos],
                  Indicate(red[2], color=C_ANT, scale_factor=1.08),
                  Indicate(suma, color=C_ANT, scale_factor=1.1), run_time=0.6)

        # rendimiento: las dos barras crecen al mismo ritmo y acaban empatadas
        pistas = VGroup(*[Rectangle(width=5.2, height=0.62, color=C_EJE, stroke_width=1.5, fill_color=C_PANEL,
                                    fill_opacity=0.4).move_to([XB0, y, 0], aligned_edge=LEFT) for y in Y])
        self.play(FadeIn(pistas), run_time=0.4)
        tb = ValueTracker(0)
        barras = [always_redraw(lambda k=k: Rectangle(width=max(1e-3, LB[k] * tb.get_value()), height=0.46,
                                                      stroke_width=0, fill_color=C_ANT, fill_opacity=0.85)
                                .move_to([XB0 + 0.08, Y[k], 0], aligned_edge=LEFT)) for k in range(2)]
        self.add(*barras)
        self.play(tb.animate.set_value(1), run_time=3.0, rate_func=smooth)
        fin = DashedLine([XB0 + 0.08 + LB[0], Y[0] + 0.6, 0], [XB0 + 0.08 + LB[0], Y[1] - 0.6, 0],
                         color=TINTA, stroke_width=3, dash_length=0.1)
        casi = Text("≈", font=FUENTE, font_size=72, color=TINTA).move_to([XB0 + 0.08 + LB[0] + 0.55, (Y[0] + Y[1]) / 2, 0])
        self.play(Create(fin), FadeIn(casi, scale=0.6), run_time=0.8)
        # la complejidad extra no se gana su sitio
        self.play(red[1].animate.set_stroke(opacity=0.12), red[2].animate.set_opacity(0.3),
                  suma[0].animate.set_stroke(width=4.5), run_time=1.2)

        # cautela honesta
        n3 = et("n = 3", 30, C_SAT)
        diag = chip("Diagnóstico", C_SAT, tam=24)
        cautela = VGroup(n3, diag).arrange(DOWN, buff=0.22).move_to([XB0 + 2.4, (Y[0] + Y[1]) / 2, 0])
        self.play(FadeIn(cautela, shift=UP * 0.2), run_time=0.8)
        self.respiro(2.4)
        self.cierre()


# =============================================================================
# 6. Siguiente paso propuesto: ¿sobrevive el margen al aumento de realismo?
# =============================================================================
class SimuladorMasReal(Pieza):
    """NTNEnv-v3 (propuesta, 2027-H1, sujeta a ratificación): de la instancia mínima (2 satélites,
    1 gateway) a órbitas reales + enlaces inter-satelitales + latencias medidas. Pregunta pre-registrada:
    ¿sobrevive el margen? Dos finales, ambos resultado. Curvas ilustrativas."""

    def construct(self):
        self.add(chip_ilustrativo(), chip("Propuesto", C_CIELO, esquina=DL))

        # ---- banco actual: mínimo
        gw = estacion(0.5).move_to([-4.6, 1.65, 0])
        s1 = satelite(0.18).move_to([-5.35, 2.95, 0])
        s2 = satelite(0.18).move_to([-3.85, 2.95, 0])
        enl = VGroup(haz(s1.get_bottom(), gw.get_top(), C_ANT), haz(s2.get_bottom(), gw.get_top(), C_ANT))
        l_2 = et("2 satélites", 24, TINTA).move_to([-4.6, 1.1, 0])
        self.play(FadeIn(gw), FadeIn(s1), FadeIn(s2), Create(enl), FadeIn(l_2), run_time=1.2)

        # ---- simulador más real: órbitas, enlaces entre satélites, latencias
        CT = np.array([4.55, 2.2, 0])
        tie = tierra(0.55, meridianos=False).move_to(CT)
        radios = [0.95, 1.3]
        orbs = VGroup(*[Circle(radius=r, color=C_SAT, stroke_width=1.6, stroke_opacity=0.5).move_to(CT) for r in radios])
        fase = ValueTracker(0)
        N = [6, 8]

        def pos(i, j):
            w = 1.0 if i == 0 else -0.75
            a = TAU * j / N[i] + w * fase.get_value() + 0.3 * i
            return CT + radios[i] * np.array([np.cos(a), np.sin(a), 0])

        sats = VGroup(*[Dot(radius=0.075, color=C_SAT).add_updater(lambda m, i=i, j=j: m.move_to(pos(i, j)))
                        for i in range(2) for j in range(N[i])])
        isl = always_redraw(lambda: VGroup(
            *[Line(pos(i, j), pos(i, (j + 1) % N[i]), color=C_ANT, stroke_width=1.8, stroke_opacity=0.8)
              for i in range(2) for j in range(N[i])],
            *[Line(pos(0, j), pos(1, (j * 8) // 6), color=C_ANT, stroke_width=1.2, stroke_opacity=0.5)
              for j in range(0, N[0], 2)]))
        fle = Arrow([-3.1, 2.3, 0], [2.7, 2.3, 0], buff=0, color=TENUE, stroke_width=4, tip_length=0.22,
                    max_tip_length_to_length_ratio=0.06)
        l_real = et("Órbitas reales", 24, TINTA).move_to([1.95, 1.35, 0])
        self.play(GrowArrow(fle), run_time=0.9)
        self.play(FadeIn(tie), Create(orbs), FadeIn(sats), FadeIn(l_real), run_time=1.2)
        self.add(isl)
        self.play(fase.animate.set_value(0.8), run_time=1.6, rate_func=linear)
        sats.suspend_updating()
        isl.suspend_updating()

        # ---- la pregunta: margen frente a realismo
        OX, OY, LX, LY = -5.6, -2.85, 11.0, 3.65
        MAXM = 0.45

        def p(u, m):
            return np.array([OX + LX * u, OY + LY * m / MAXM, 0])
        ejes = VGroup(Arrow(p(0, 0), p(1.0, 0), buff=0, color=C_EJE, stroke_width=3, tip_length=0.18,
                            max_tip_length_to_length_ratio=0.05),
                      Arrow(p(0, 0), p(0, MAXM), buff=0, color=C_EJE, stroke_width=3, tip_length=0.18,
                            max_tip_length_to_length_ratio=0.1))
        umb = DashedLine(p(0, 0.25), p(0.98, 0.25), color=C_CIELO, stroke_width=4, dash_length=0.15)
        l_umb = et("Umbral 25 %", 22, C_CIELO).next_to(p(0.03, 0.25), DOWN, buff=0.12, aligned_edge=LEFT)
        self.play(Create(ejes), Create(umb), FadeIn(l_umb), run_time=1.0)

        # tramo conocido (ilustrativo): la instancia mínima sobre el umbral
        UF = 0.42
        us = np.linspace(0.03, UF, 40)
        ms = 0.315 + 0.004 * np.sin(9 * us)
        pts = np.array([p(u, m) for u, m in zip(us, ms)])
        tramo = trazo(pts[:, 0], pts[:, 1], C_OK, 5)
        self.play(Create(tramo), run_time=1.4)
        bif = pts[-1]
        preg = et("¿Sobrevive?", 28, TINTA).move_to(bif + np.array([0.2, 0.62, 0]))
        anillo = Circle(radius=0.16, color=TINTA, stroke_width=3).move_to(bif)
        self.play(FadeIn(preg, shift=DOWN * 0.15), Create(anillo), run_time=0.8)
        self.play(anillo.animate.scale(1.6).set_stroke(opacity=0), run_time=0.7)

        # dos finales posibles, mismo peso: los dos son resultado
        uu = np.linspace(UF, 0.93, 50)
        s_ = suave((uu - UF) / (0.93 - UF))
        m_arriba = ms[-1] + 0.05 * s_
        m_abajo = ms[-1] - 0.21 * s_
        ra = np.array([p(u, m) for u, m in zip(uu, m_arriba)])
        rb = np.array([p(u, m) for u, m in zip(uu, m_abajo)])
        ca = DashedVMobject(trazo(ra[:, 0], ra[:, 1], C_CIELO, 5), num_dashes=26)
        cb = DashedVMobject(trazo(rb[:, 0], rb[:, 1], C_CIELO, 5), num_dashes=26)
        self.play(Create(ca), Create(cb), run_time=2.0)

        def final(pt):
            aro = Circle(radius=0.26, color=TINTA, stroke_width=3, fill_color=C_PANEL, fill_opacity=1).move_to(pt)
            return VGroup(aro, marca_ok(pos=pt, tam=0.26, color=TINTA))
        fa, fb = final(ra[-1]), final(rb[-1])
        self.play(FadeIn(fa, scale=0.5), FadeIn(fb, scale=0.5), run_time=0.7)
        self.play(Indicate(fa, color=C_CIELO, scale_factor=1.2), Indicate(fb, color=C_CIELO, scale_factor=1.2),
                  run_time=0.9)
        self.respiro(1.6)
        self.cierre()


# =============================================================================
# 7. Por qué corre prisa: el freeze de 6G cae antes de la defensa
# =============================================================================
class PrisaDosMilVeintinueve(Pieza):
    """Doctorado feb-2026 → feb-2030 (8 semestres; hoy en el 2.º). 3GPP: freeze de la primera release 6G
    «potencialmente a inicios de 2029». El vocabulario se fija antes; la defensa cae después."""

    def construct(self):
        T0, T1 = 2026 + 1 / 12, 2030 + 1 / 12        # feb-2026, feb-2030
        X0, X1 = -5.4, 5.3
        HOY = 2026 + 8.95 / 12                         # fin de sep-2026: semestre 2 de 8
        FZ0, FZ1 = 2029.0, 2029.25                     # «inicios de 2029» (potencialmente)
        YD, YV = -0.95, 1.05                           # carril doctorado / carril 3GPP

        def x(t):
            return X0 + (X1 - X0) * (t - T0) / (T1 - T0)

        self.add(chip_tercero("3GPP"))

        # ---- regla de tiempo
        eje = Line([X0 - 0.3, -2.1, 0], [X1 + 0.5, -2.1, 0], color=C_EJE, stroke_width=3)
        anios = VGroup(*[VGroup(Line([x(a), -2.2, 0], [x(a), -2.0, 0], color=C_EJE, stroke_width=3),
                                et(str(a), 20, TENUE).move_to([x(a), -2.45, 0])) for a in (2027, 2028, 2029)])
        # ---- el doctorado: 8 semestres
        sems = VGroup(*[Rectangle(width=(X1 - X0) / 8 - 0.04, height=0.55, color=C_ANT, stroke_width=2,
                                  fill_color=C_ANT, fill_opacity=0.08)
                        .move_to([X0 + (X1 - X0) * (k + 0.5) / 8, YD, 0]) for k in range(8)])
        l_ini = et("Feb 2026", 22, TENUE).move_to([X0, YD - 0.6, 0])
        l_fin = et("Feb 2030", 22, TENUE).move_to([X1, YD - 0.6, 0])
        self.play(Create(eje), FadeIn(anios), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(s, shift=RIGHT * 0.1) for s in sems], lag_ratio=0.1),
                  FadeIn(l_ini), FadeIn(l_fin), run_time=1.4)

        tp = ValueTracker(T0)
        avance = always_redraw(lambda: Rectangle(width=max(1e-3, x(tp.get_value()) - X0 - 0.02), height=0.47,
                                                 stroke_width=0, fill_color=C_ANT, fill_opacity=0.75)
                               .move_to([X0 + 0.02, YD, 0], aligned_edge=LEFT))
        self.add(avance)
        self.play(tp.animate.set_value(HOY), run_time=1.3)
        hoy_l = DashedLine([x(HOY), YD - 0.35, 0], [x(HOY), 2.2, 0], color=TINTA, stroke_width=3, dash_length=0.1)
        hoy_t = et("Hoy", 26, TINTA).move_to([x(HOY), 2.5, 0])
        punta = Triangle(color=TINTA, fill_color=TINTA, fill_opacity=1, stroke_width=0).scale(0.1).rotate(PI)
        punta.next_to(hoy_l, UP, buff=0)
        self.play(Create(hoy_l), FadeIn(hoy_t, shift=DOWN * 0.15), FadeIn(punta), run_time=0.8)
        self.respiro(0.5)

        # ---- 3GPP: el vocabulario se va fijando hasta el freeze
        n = 40
        xa, xb = x(HOY) + 0.08, x(FZ0)
        franja = VGroup(*[Rectangle(width=(xb - xa) / n + 0.005, height=0.62, stroke_width=0,
                                    fill_color=C_CIELO, fill_opacity=0.08 + 0.6 * (k / (n - 1)) ** 1.5)
                          .move_to([xa + (xb - xa) * (k + 0.5) / n, YV, 0]) for k in range(n)])
        l_voc = et("Vocabulario se fija", 24, TINTA).move_to([(xa + xb) / 2 - 0.3, YV + 0.62, 0])
        self.play(LaggedStart(*[FadeIn(r) for r in franja], lag_ratio=0.03), FadeIn(l_voc), run_time=2.2)

        # freeze: pared difusa (fecha «potencial») a inicios de 2029
        capas = VGroup(*[Rectangle(width=(x(FZ1) - x(FZ0)) * f, height=4.0, stroke_width=0, fill_color=C_CIELO,
                                   fill_opacity=0.22).move_to([x(FZ0) + (x(FZ1) - x(FZ0)) * 0.5, 0.05, 0])
                         for f in (1.6, 1.0, 0.45)])
        l_fz = et("Freeze 6G", 28, C_CIELO).move_to([x(FZ0) + (x(FZ1) - x(FZ0)) * 0.5, 2.5, 0])
        self.play(FadeIn(capas, shift=DOWN * 0.3), FadeIn(l_fz, shift=DOWN * 0.15), run_time=1.0)
        self.play(Indicate(l_fz, color=C_CIELO, scale_factor=1.12), run_time=0.7)

        # ---- la defensa: del otro lado de la frontera
        pd = np.array([X1, YD, 0])
        estrella = Star(n=5, outer_radius=0.3, inner_radius=0.13, color=C_SAT, fill_color=C_SAT,
                        fill_opacity=1, stroke_width=2).move_to(pd + UP * 0.72)
        l_def = et("Defensa", 28, C_SAT).next_to(estrella, UP, buff=0.12)
        self.play(FadeIn(estrella, scale=0.4), FadeIn(l_def, shift=DOWN * 0.15), run_time=0.8)
        salto = CurvedArrow(np.array([x(HOY), YD + 0.4, 0]), estrella.get_left() + LEFT * 0.08, angle=-0.55,
                            color=C_SAT, stroke_width=3, tip_length=0.18)
        salto.set_stroke(opacity=0.8)
        self.play(Create(salto), run_time=1.8)
        self.play(Indicate(estrella, color=C_SAT, scale_factor=1.3), run_time=0.8)
        self.respiro(1.6)
        self.cierre()

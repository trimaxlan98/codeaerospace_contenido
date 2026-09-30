"""Seminario S2 (bloques 3–4 y escalado): el examen mal hecho y lo que se construye encima."""
from tesis_lib import *
import numpy as np


# ---------- helpers locales ----------
def _mezcla(a, b, u):
    return interpolate_color(ManimColor(a), ManimColor(b), float(np.clip(u, 0, 1)))


def _persona(color, alto=1.3, relleno=0.3, ancho=3):
    cab = Circle(radius=alto * 0.19, color=color, fill_color=color, fill_opacity=relleno, stroke_width=ancho)
    cuerpo = RoundedRectangle(corner_radius=alto * 0.18, width=alto * 0.62, height=alto * 0.5, color=color,
                              fill_color=color, fill_opacity=relleno, stroke_width=ancho)
    cuerpo.move_to([0, -alto * 0.25, 0])
    cab.move_to([0, alto * 0.25, 0])
    return VGroup(cuerpo, cab)


def _sobre(puntos, d):
    """Punto a distancia d a lo largo de una polilínea (lista de np.array)."""
    for a, b in zip(puntos[:-1], puntos[1:]):
        l_ = np.linalg.norm(b - a)
        if d <= l_:
            return a + (b - a) * (d / l_)
        d -= l_
    return puntos[-1]


def _largo(puntos):
    return sum(np.linalg.norm(b - a) for a, b in zip(puntos[:-1], puntos[1:]))


def _candado(color, tam=0.4):
    cuerpo = RoundedRectangle(corner_radius=tam * 0.1, width=tam, height=tam * 0.78, color=color,
                              fill_color=color, fill_opacity=0.35, stroke_width=3)
    arco = Arc(radius=tam * 0.3, start_angle=0, angle=PI, color=color, stroke_width=4)
    arco.next_to(cuerpo, UP, buff=0).shift(DOWN * 0.02)
    ojo = Dot(cuerpo.get_center(), radius=tam * 0.08, color=color)
    return VGroup(arco, cuerpo, ojo)


# =============================================================================
# 1. Termómetro roto — la analogía de los dos médicos
# =============================================================================
class TermometroRoto(Pieza):
    def construct(self):
        TX = -2.3

        def ty(T):
            return -1.95 + (T - 34.0) * 0.5

        def col_temp(T):
            u = (T - 35.0) / 6.0
            return _mezcla(C_ANT, C_SAT, u * 2) if u < 0.5 else _mezcla(C_SAT, C_MAL, (u - 0.5) * 2)

        # termómetro (el mismo para los dos)
        tubo = RoundedRectangle(corner_radius=0.2, width=0.4, height=4.5, color=TENUE, fill_color=C_PANEL,
                                fill_opacity=0.8, stroke_width=3).move_to([TX, 0.1, 0])
        bulbo = Circle(radius=0.36, color=TENUE, fill_color=TENUE, fill_opacity=0.9, stroke_width=3).move_to([TX, -2.35, 0])
        merc = Rectangle(width=0.18, height=ty(37) + 2.2, stroke_width=0, fill_color=TENUE, fill_opacity=0.95)
        merc.move_to([TX, (ty(37) - 2.2) / 2, 0])
        marcas = VGroup(*[Line([TX + 0.2, ty(T), 0], [TX + 0.2 + (0.24 if T == 37 else 0.12), ty(T), 0],
                               color=TENUE, stroke_width=2) for T in range(35, 42)])
        lectura = et("37°", 34, TINTA).next_to([TX - 0.2, ty(37), 0], LEFT, buff=0.18)
        termo = VGroup(tubo, merc, bulbo, marcas, lectura)

        # médicos
        def medico(col):
            p = _persona(col, 1.3, 0.25)
            cz = VGroup(Rectangle(width=0.26, height=0.08), Rectangle(width=0.08, height=0.26))
            cz.set_fill(col, 1).set_stroke(width=0).move_to(p[0].get_center() + UP * 0.02)
            return VGroup(p, cz)

        mA = medico(C_ANT).move_to([-5.5, 1.45, 0])
        mB = medico(C_CIELO).move_to([-5.5, -1.25, 0])
        lA = et_junto("Médico A", mA, DOWN, 22, TINTA)
        lB = et_junto("Médico B", mB, DOWN, 22, TINTA)

        # barras de aciertos
        va, vb = ValueTracker(0), ValueTracker(0)
        ESC, BY = 0.042, -2.3
        XA, XB = 2.8, 4.8
        barA = always_redraw(lambda: barra(XA, BY, max(va.get_value() * ESC, 0.002), 1.1, C_ANT, 0.8))
        barB = always_redraw(lambda: barra(XB, BY, max(vb.get_value() * ESC, 0.002), 1.1, C_CIELO, 0.8))

        def numero(tr, x, col):
            g = cifra(0, "%", 30, col)

            def act(m):
                m[0].set_value(tr.get_value())
                m[0].set_stroke(width=0)
                m.arrange(RIGHT, buff=0.1, aligned_edge=DOWN)
                m.move_to([x, BY + tr.get_value() * ESC + 0.32, 0])
            g.add_updater(act)
            act(g)
            return g

        nA, nB = numero(va, XA, C_ANT), numero(vb, XB, C_CIELO)
        base = Line([1.9, BY, 0], [5.7, BY, 0], color=C_EJE, stroke_width=3)
        letras = VGroup(et("A", 22, TENUE).move_to([XA, BY - 0.35, 0]), et("B", 22, TENUE).move_to([XB, BY - 0.35, 0]))

        PAC = np.array([-0.7, -0.35, 0])

        def rayos():
            return [DashedLine(m.get_right() + RIGHT * 0.1, lectura.get_left() + LEFT * 0.08, color=c,
                               stroke_width=2.5, dash_length=0.1) for m, c in ((mA, C_ANT), (mB, C_CIELO))]

        self.add(chip_ilustrativo())
        self.play(FadeIn(mA, shift=RIGHT * 0.3), FadeIn(mB, shift=RIGHT * 0.3), FadeIn(lA), FadeIn(lB), run_time=0.8)
        self.play(FadeIn(termo, shift=UP * 0.2), run_time=0.8)
        self.play(Create(base), FadeIn(letras), run_time=0.6)
        self.add(barA, barB, nA, nB)

        # diagnostican: las barras suben
        for T, a, b in [(38.5, 24, 25), (36.0, 47, 49), (39.5, 70, 72)]:
            p = _persona(col_temp(T), 1.6, 0.45).move_to(PAC)
            rA, rB = rayos()
            self.play(FadeIn(p, shift=UP * 0.4), run_time=0.45)
            self.play(Create(rA), Create(rB), va.animate.set_value(a), vb.animate.set_value(b), run_time=0.9)
            self.play(FadeOut(p, shift=UP * 0.4), FadeOut(rA), FadeOut(rB), run_time=0.45)

        topA = BY + 70 * ESC
        ref = DashedLine([XA - 0.55, topA, 0], [XB + 0.55, topA, 0], color=TENUE, stroke_width=2, dash_length=0.1)
        tajada = Rectangle(width=1.1, height=2 * ESC, fill_color=C_OK, fill_opacity=1, stroke_width=0)
        tajada.move_to([XB, topA + ESC, 0])
        gana = et("Gana B", 28, C_OK).move_to([XB, BY + 72 * ESC + 0.95, 0])
        self.play(Create(ref), FadeIn(tajada), FadeIn(gana, shift=DOWN * 0.2), run_time=0.8)
        self.respiro(0.5)

        # revelación: el termómetro no se mueve
        marco = SurroundingRectangle(VGroup(tubo, bulbo, lectura), color=C_MAL, buff=0.2, corner_radius=0.15,
                                     stroke_width=3)
        self.play(Create(marco), lectura.animate.set_color(C_MAL), run_time=0.8)
        for T in (41.0, 35.0, 40.0):
            col = col_temp(T)
            p = _persona(col, 1.6, 0.45).move_to(PAC)
            fant = Rectangle(width=0.16, height=ty(T) + 2.2, stroke_color=col, stroke_width=2, fill_color=col,
                             fill_opacity=0.5).move_to([TX + 0.7, (ty(T) - 2.2) / 2, 0])
            self.play(FadeIn(p, shift=UP * 0.4), GrowFromEdge(fant, DOWN), run_time=0.8)
            self.play(Indicate(lectura, color=C_MAL, scale_factor=1.15), run_time=0.5)
            self.play(FadeOut(p, shift=UP * 0.4), FadeOut(fant), run_time=0.4)

        # las barras pierden sentido
        for m in (barA, barB, nA, nB):
            m.clear_updaters()
        tacha = Line(gana.get_left() + LEFT * 0.1, gana.get_right() + RIGHT * 0.1, color=C_MAL, stroke_width=4)
        self.play(Create(tacha), run_time=0.5)
        self.play(FadeOut(tajada), FadeOut(ref), FadeOut(gana), FadeOut(tacha),
                  barA.animate.set_fill(TENUE, opacity=0.12).set_stroke(TENUE, opacity=0.6),
                  barB.animate.set_fill(TENUE, opacity=0.12).set_stroke(TENUE, opacity=0.6),
                  nA.animate.set_opacity(0.3), nB.animate.set_opacity(0.3), run_time=1.4)
        self.play(Indicate(lectura, color=C_MAL, scale_factor=1.2), run_time=0.8)
        self.cierre()


# =============================================================================
# 2. La política que no mira (Ellis et al., SMACv2, NeurIPS 2023)
# =============================================================================
class PoliticaQueNoMira(Pieza):
    def construct(self):
        PA, PB = np.array([-5.4, 1.4, 0]), np.array([-5.4, -1.0, 0])
        cabA = Circle(radius=0.5, color=C_ANT, fill_color=C_ANT, fill_opacity=0.18, stroke_width=3).move_to(PA)
        ojo = VGroup(Ellipse(width=0.56, height=0.3, color=C_ANT, stroke_width=3),
                     Dot(radius=0.08, color=C_ANT)).move_to(PA + UP * 0.05)
        agA = VGroup(cabA, ojo)
        cabB = Circle(radius=0.5, color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.18, stroke_width=3).move_to(PB)
        venda = Rectangle(width=1.06, height=0.26, fill_color=C_EJE, fill_opacity=1, stroke_color=TENUE,
                          stroke_width=2).move_to(PB + UP * 0.05)
        nudo = VGroup(Line(PB + np.array([0.53, 0.05, 0]), PB + np.array([0.8, -0.18, 0])),
                      Line(PB + np.array([0.53, 0.05, 0]), PB + np.array([0.78, 0.26, 0]))).set_stroke(TENUE, 3)
        agB = VGroup(cabB, venda, nudo)
        lObs = et_junto("Observa", cabA, DOWN, 22, TINTA)
        lSin = et_junto("Sin observar", cabB, DOWN, 22, TINTA)

        CR = PB + DOWN * 1.6
        esfera = Circle(radius=0.3, color=C_CIELO, stroke_width=3).move_to(CR)
        pts = VGroup(*[Dot(CR + 0.22 * np.array([np.cos(a), np.sin(a), 0]), radius=0.03, color=C_CIELO)
                       for a in np.arange(4) * PI / 2])
        aguja = Line(CR, CR + UP * 0.22, color=TINTA, stroke_width=3)
        reloj = VGroup(esfera, pts, aguja)
        lRel = et("Reloj", 20, TENUE).next_to(esfera, RIGHT, buff=0.2)

        XS = [-2.4, -0.5, 1.4, 3.3]
        YA, YB, L = 1.4, -1.0, 1.6
        casillas = VGroup(*[Square(L, color=C_EJE, fill_color=C_PANEL, fill_opacity=0.4, stroke_width=2)
                            .move_to([x, y, 0]) for y in (YA, YB) for x in XS])
        OFF = [np.array(o + (0,)) for o in [(0.42, 0.38), (-0.4, 0.4), (0.4, -0.4), (-0.42, -0.36)]]
        SEQ = [RIGHT, UP, RIGHT, UP]  # secuencia fija, solo depende del paso del reloj

        def diana(pos):
            return VGroup(Circle(radius=0.15, color=TINTA, stroke_width=2.5), Dot(radius=0.05, color=TINTA)).move_to(pos)

        cA, cB = ValueTracker(0), ValueTracker(0)
        XT = 4.45

        def total(tr, y, col):
            def f():
                w = max(tr.get_value() * 0.42, 0.002)
                return Rectangle(width=w, height=0.34, stroke_width=0, fill_color=col, fill_opacity=0.85
                                 ).move_to([XT + w / 2, y, 0])
            return always_redraw(f)

        tA, tB = total(cA, YA, C_ANT), total(cB, YB, C_CIELO)

        self.add(chip_tercero("Ellis 2023"))
        self.play(FadeIn(agA, scale=0.8), FadeIn(agB, scale=0.8), FadeIn(lObs), FadeIn(lSin), run_time=0.8)
        self.play(FadeIn(reloj), FadeIn(lRel), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(c, scale=0.9) for c in casillas], lag_ratio=0.06), run_time=1.0)
        self.add(tA, tB)

        restos = VGroup()
        for k in range(4):
            x = XS[k]
            dA, dB = diana([x, YA, 0] + OFF[k]), diana([x, YB, 0] + OFF[k])
            self.play(FadeIn(dA, scale=0.5), FadeIn(dB, scale=0.5), run_time=0.4)
            mir = DashedVMobject(ArcBetweenPoints(ojo.get_right() + RIGHT * 0.05, dA.get_center(), angle=-0.5),
                                 num_dashes=28).set_stroke(C_ANT, 2.5)
            fA = Arrow([x, YA, 0], dA.get_center(), buff=0.17, color=C_ANT, stroke_width=6, tip_length=0.18,
                       max_tip_length_to_length_ratio=0.45, max_stroke_width_to_length_ratio=30)
            cB_ = np.array([x, YB, 0])
            fB = Arrow(cB_, cB_ + SEQ[k] * 0.58, buff=0, color=C_CIELO, stroke_width=6, tip_length=0.18,
                       max_tip_length_to_length_ratio=0.45, max_stroke_width_to_length_ratio=30)
            self.play(Create(mir), Rotate(aguja, -PI / 2, about_point=CR), run_time=0.6)
            self.play(GrowArrow(fA), GrowArrow(fB), run_time=0.5)
            okA = marca_ok(np.array([x, YA - L / 2 - 0.25, 0]), 0.28)
            okB = marca_ok(np.array([x, YB - L / 2 - 0.25, 0]), 0.28)
            self.play(Create(okA), Create(okB), cA.animate.set_value(k + 1), cB.animate.set_value(k + 1),
                      FadeOut(mir), run_time=0.55)
            restos.add(dA, dB, fA, fB, okA, okB)

        igual = et("=", 44, TENUE).move_to([XT + 0.84, (YA + YB) / 2, 0])
        gana = et("Gana", 24, C_OK).next_to([XT + 0.84, YB, 0], DOWN, buff=0.35)
        self.play(FadeIn(igual, scale=0.6), FadeIn(gana, shift=UP * 0.2), run_time=0.7)
        self.respiro(0.6)

        # el tablero no premia adaptarse: gane quien gane, cualquier acción cae en la zona verde
        zonas = VGroup(*[RoundedRectangle(corner_radius=0.1, width=L - 0.14, height=L - 0.14, stroke_width=0,
                                          fill_color=C_OK, fill_opacity=0.22).move_to(c) for c in casillas])
        for m in (tA, tB):
            m.clear_updaters()
        self.play(LaggedStart(*[FadeIn(z) for z in zonas], lag_ratio=0.05),
                  tA.animate.set_fill(TENUE), tB.animate.set_fill(TENUE),
                  ojo.animate.set_opacity(0.35), run_time=1.6)
        self.play(Indicate(igual, color=TINTA, scale_factor=1.3), run_time=0.8)
        self.cierre()


# =============================================================================
# 3. Semillas que invierten (Yılmaz & Çelikcan 2026; Google Research Football)
# =============================================================================
class SemillasQueInvierten(Pieza):
    def construct(self):
        def sy(s):
            return -2.4 + (s - 0.2) / 0.62 * 4.9

        XA, XB = -2.6, 0.1
        Y0 = -2.6
        eje = Line([-4.3, Y0, 0], [-4.3, 2.7, 0], color=C_EJE, stroke_width=3)
        base = Line([-4.3, Y0, 0], [1.6, Y0, 0], color=C_EJE, stroke_width=3)
        letras = VGroup(et("A", 28, C_ANT).move_to([XA, Y0 - 0.38, 0]), et("B", 28, C_SAT).move_to([XB, Y0 - 0.38, 0]))

        A1 = [0.62, 0.70, 0.55, 0.66, 0.60]
        B1 = [0.52, 0.58, 0.49, 0.60, 0.55]
        A2 = [0.30, 0.42, 0.35, 0.48, 0.38]
        B2 = [0.68, 0.62, 0.72, 0.58, 0.66]
        rng = np.random.default_rng(42)

        def semillas(vals, x, col):
            g = VGroup()
            for v in vals:
                d = Dot([x + rng.uniform(-0.45, 0.45), sy(v), 0], radius=0.11, color=col)
                d.set_stroke(FONDO, 1.5)
                g.add(d)
            return g

        sA1, sB1 = semillas(A1, XA, C_ANT), semillas(B1, XB, C_SAT)
        sA2, sB2 = semillas(A2, XA, C_ANT), semillas(B2, XB, C_SAT)

        mA, mB = ValueTracker(np.mean(A1)), ValueTracker(np.mean(B1))
        medA = always_redraw(lambda: Line([XA - 0.72, sy(mA.get_value()), 0], [XA + 0.72, sy(mA.get_value()), 0],
                                          color=C_ANT, stroke_width=8))
        medB = always_redraw(lambda: Line([XB - 0.72, sy(mB.get_value()), 0], [XB + 0.72, sy(mB.get_value()), 0],
                                          color=C_SAT, stroke_width=8))

        cont = et("5 semillas", 34, TINTA).move_to([4.4, 2.3, 0])
        cont2 = et("10 semillas", 34, TINTA).move_to(cont)
        comp = VGroup(et("A", 64, C_ANT), et(">", 64, TINTA), et("B", 64, C_SAT)).arrange(RIGHT, buff=0.35)
        comp.move_to([4.4, 0.9, 0])
        menor = et("<", 64, TINTA).move_to(comp[1])

        def caer(g, lag=0.15):
            anims = []
            for d in g:
                fin = d.get_center()
                d.move_to([fin[0], 3.3, 0]).set_opacity(0)
                anims.append(d.animate.move_to(fin).set_opacity(1))
            return LaggedStart(*anims, lag_ratio=lag)

        self.add(chip_tercero("Yılmaz 2026"), chip("Fútbol, no NTN", TENUE, esquina=DR), chip_ilustrativo(esquina=UR))
        self.play(Create(eje), Create(base), FadeIn(letras), run_time=0.9)
        self.play(FadeIn(cont, shift=DOWN * 0.2), run_time=0.5)
        self.add(sA1, sB1)
        self.play(caer(sA1), caer(sB1), run_time=1.8)
        self.play(Create(medA), Create(medB), run_time=0.7)
        self.play(FadeIn(comp, scale=0.8), run_time=0.6)
        self.respiro(1.2)

        # llegan 5 semillas más: la diferencia se invierte
        self.play(FadeTransform(cont, cont2), run_time=0.6)
        self.add(sA2, sB2)
        self.play(caer(sA2), caer(sB2), run_time=1.9)
        self.play(mA.animate.set_value(np.mean(A1 + A2)), mB.animate.set_value(np.mean(B1 + B2)), run_time=1.4)
        self.play(Transform(comp[1], menor), Indicate(comp[2], color=C_SAT, scale_factor=1.2), run_time=0.9)
        self.respiro(0.8)

        # una política aleatoria cae dentro del rango de las entrenadas
        banda = Rectangle(width=5.6, height=sy(0.52) - sy(0.40), stroke_width=0, fill_color=TENUE,
                          fill_opacity=0.42).move_to([-1.45, (sy(0.52) + sy(0.40)) / 2, 0])
        banda.set_z_index(-1)
        bordes = VGroup(DashedLine(banda.get_corner(UL), banda.get_corner(UR), color=TENUE, stroke_width=2),
                        DashedLine(banda.get_corner(DL), banda.get_corner(DR), color=TENUE, stroke_width=2))
        lAl = et("Aleatoria", 24, TENUE).next_to(banda, RIGHT, buff=0.25)
        self.play(GrowFromEdge(banda, LEFT), Create(bordes), run_time=1.2)
        self.play(FadeIn(lAl, shift=LEFT * 0.2), comp.animate.set_opacity(0.35), run_time=0.7)
        self.respiro(1.0)
        self.cierre()


# =============================================================================
# 4. Modelo de lenguaje arriba, aprendizaje por refuerzo abajo
# =============================================================================
class ModeloArribaRLAbajo(Pieza):
    def construct(self):
        T = ValueTracker(0)
        rng = np.random.default_rng(42)
        T_CORTE, T_FIN = 7.5, 15.5

        # capas
        capa_lenta = RoundedRectangle(corner_radius=0.2, width=9.0, height=2.4, color=C_CIELO, fill_color=C_CIELO,
                                      fill_opacity=0.06, stroke_width=2.5).move_to([1.9, 1.9, 0])
        capa_rapida = RoundedRectangle(corner_radius=0.2, width=9.0, height=2.4, color=C_SAT, fill_color=C_SAT,
                                       fill_opacity=0.06, stroke_width=2.5).move_to([1.9, -1.8, 0])

        # fuente de telemetría (una red)
        SRC = np.array([-5.6, 0.05, 0])
        pn = [SRC + np.array(v) for v in [(-0.45, 0.4, 0), (0.35, 0.5, 0), (-0.35, -0.45, 0), (0.45, -0.3, 0), (0, 0.02, 0)]]
        red = VGroup(*[Line(pn[i], pn[j], color=C_EJE, stroke_width=2) for i, j in [(0, 4), (1, 4), (2, 4), (3, 4), (0, 1), (2, 3)]],
                     *[Dot(p, radius=0.09, color=C_ANT) for p in pn])
        lTel = et("Telemetría", 22, TENUE).next_to(red, DOWN, buff=0.25)

        # ventana del modelo de lenguaje
        VC = np.array([0.0, 2.2, 0])
        ventana = Square(1.1, color=C_CIELO, stroke_width=4, fill_color=C_CIELO, fill_opacity=0.08).move_to(VC)
        lVen = et("Ventana limitada", 20, TENUE).next_to(ventana, DOWN, buff=0.18)
        LLM = np.array([2.5, 2.0, 0])
        burbuja = RoundedRectangle(corner_radius=0.2, width=1.1, height=0.72, color=C_CIELO, fill_color=C_CIELO,
                                   fill_opacity=0.2, stroke_width=3).move_to(LLM)
        cola = Polygon(LLM + np.array([-0.3, -0.34, 0]), LLM + np.array([-0.05, -0.34, 0]), LLM + np.array([-0.4, -0.62, 0]),
                       color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.2, stroke_width=3)
        puntos = VGroup(*[Dot(LLM + RIGHT * dx, radius=0.06, color=C_CIELO) for dx in (-0.25, 0, 0.25)])
        llm = VGroup(cola, burbuja, puntos)
        lTrad = et("Traduce intención", 24, TINTA).next_to(burbuja, RIGHT, buff=0.35)

        # agente rápido
        AG = np.array([0.0, -1.8, 0])
        agente = Circle(radius=0.4, color=C_SAT, fill_color=C_SAT, fill_opacity=0.15, stroke_width=3.5).move_to(AG)
        nucleo = Dot(AG, radius=0.14, color=C_SAT)
        NODOS = [np.array([2.5, y, 0]) for y in (-1.2, -1.8, -2.4)]
        destinos = VGroup(*[Dot(p, radius=0.1, color=C_ANT) for p in NODOS])
        lDec = et("Decide rápido", 24, TINTA).next_to(destinos, RIGHT, buff=0.45)

        # ---- partículas (todo es función de T) ----
        ruta_arr = [SRC + np.array([0.35, 0.25, 0]), np.array([-2.6, VC[1], 0]), np.array([-0.62, VC[1], 0])]
        ruta_aba = [SRC + np.array([0.35, -0.25, 0]), np.array([-2.6, AG[1], 0]), np.array([-0.45, AG[1], 0])]
        la, lb = _largo(ruta_arr), _largo(ruta_aba)
        V = 3.2
        CAP = 12
        slots = [VC + np.array([-0.39 + 0.26 * (i % 4), 0.28 - 0.28 * (i // 4), 0]) for i in range(CAP)]
        T_VACIA = T_CORTE + la / V + 0.2

        parts = []  # (dot, fn(t) -> (pos, color, op) | None)
        # corriente hacia arriba
        t_arr = np.arange(0.0, T_CORTE, 0.2)
        for i, t0 in enumerate(t_arr):
            dy = rng.uniform(-0.1, 0.1)
            ta = t0 + la / V

            def f(t, t0=t0, ta=ta, i=i, dy=dy):
                if t < t0:
                    return None
                if t < ta:
                    return _sobre(ruta_arr, (t - t0) * V) + UP * dy, C_ANT, 1.0
                if i < CAP:  # cabe: se acomoda en la ventana
                    tv = T_VACIA + 0.12 * i
                    if t < ta + 0.25:
                        u = (t - ta) / 0.25
                        return ruta_arr[-1] * (1 - u) + slots[i] * u, C_ANT, 1.0
                    if t < tv:
                        return slots[i], C_ANT, 1.0
                    if t < tv + 0.5:
                        u = suave((t - tv) / 0.5)
                        return slots[i] * (1 - u) + LLM * u, C_CIELO, 1 - 0.6 * u
                    return None
                tau = t - ta  # desborda: rebota y cae
                if tau > 1.1:
                    return None
                p = ruta_arr[-1] + np.array([-0.15 - 0.7 * tau, dy + 1.0 * tau - 3.6 * tau ** 2, 0])
                return p, C_MAL, 1 - 0.8 * tau / 1.1
            parts.append(f)

        # corriente hacia abajo
        t_aba = np.arange(0.0, T_FIN, 0.1)
        for t0 in t_aba:
            dy = rng.uniform(-0.1, 0.1)
            ta = t0 + lb / V

            def f(t, t0=t0, ta=ta, dy=dy):
                if t < t0 or t > ta:
                    return None
                return _sobre(ruta_aba, (t - t0) * V) + UP * dy, C_ANT, 1.0
            parts.append(f)
        llegadas = t_aba + lb / V

        # decisiones que salen del agente
        for k, t0 in enumerate(llegadas[::2]):
            dst = NODOS[k % 3]
            ini = AG + RIGHT * 0.45

            def f(t, t0=t0 + 0.05, dst=dst, ini=ini):
                u = (t - t0) / 0.45
                if u < 0 or u > 1:
                    return None
                return ini * (1 - u) + dst * u, C_SAT, 1.0
            parts.append(f)

        # tras el corte: resúmenes suben, intención baja
        SUBE = [AG + UP * 0.45, VC + DOWN * 0.1]
        for t0 in np.arange(T_VACIA + 0.2, T_FIN, 1.3):
            def f(t, t0=t0):
                tau = t - t0
                if tau < 0:
                    return None
                if tau < 1.4:
                    return SUBE[0] * (1 - suave(tau / 1.4)) + SUBE[1] * suave(tau / 1.4), C_SAT, 1.0
                if tau < 1.9:
                    return SUBE[1], C_SAT, 1.0
                if tau < 2.3:
                    u = suave((tau - 1.9) / 0.4)
                    return SUBE[1] * (1 - u) + LLM * u, C_CIELO, 1 - 0.6 * u
                return None
            parts.append(f)
        BAJA = [LLM + np.array([0.1, -0.45, 0]), AG + np.array([0.35, 0.35, 0])]
        for t0 in np.arange(T_VACIA + 0.6, T_FIN, 3.0):
            def f(t, t0=t0):
                u = (t - t0) / 1.8
                if u < 0 or u > 1:
                    return None
                return BAJA[0] * (1 - suave(u)) + BAJA[1] * suave(u), C_CIELO, 1.0
            parts.append(f)

        pool = VGroup(*[Dot(radius=0.075) for _ in parts])

        def act_pool(g):
            t = T.get_value()
            for d, f in zip(g, parts):
                r = f(t)
                if r is None:
                    d.set_opacity(0)
                else:
                    d.move_to(r[0]).set_color(r[1]).set_opacity(r[2])
        pool.add_updater(act_pool)
        act_pool(pool)

        t_llena = t_arr[CAP - 1] + la / V

        def act_ven(m):
            t = T.get_value()
            c = C_MAL if t_llena <= t < T_VACIA else (C_OK if t >= T_VACIA else C_CIELO)
            m.set_stroke(c)
        ventana.add_updater(act_ven)

        def act_nuc(m):
            t = T.get_value()
            prev = llegadas[llegadas <= t]
            fl = np.exp(-(t - prev[-1]) * 14) if len(prev) else 0
            m.set_width(0.28 + 0.2 * fl)
            m.move_to(AG)
        nucleo.add_updater(act_nuc)

        guia_sube = DashedLine(SUBE[0], VC + DOWN * 0.55, color=C_SAT, stroke_width=2, dash_length=0.1,
                               stroke_opacity=0.6)
        guia_baja = DashedLine(BAJA[0], BAJA[1], color=C_CIELO, stroke_width=2, dash_length=0.1, stroke_opacity=0.6)

        self.add(chip_tercero("IETF 2026"))
        self.play(FadeIn(capa_lenta), FadeIn(capa_rapida), run_time=0.7)
        self.play(FadeIn(red, scale=0.8), FadeIn(lTel), run_time=0.6)
        self.play(FadeIn(ventana), FadeIn(lVen), FadeIn(llm, scale=0.8), FadeIn(lTrad), run_time=0.8)
        self.play(FadeIn(agente), FadeIn(nucleo), FadeIn(destinos), FadeIn(lDec), run_time=0.8)
        self.add(pool)
        self.bring_to_front(nucleo)
        self.play(T.animate.set_value(T_CORTE), run_time=T_CORTE, rate_func=linear)
        self.play(T.animate.set_value(T_CORTE + 1.2), Create(guia_sube), Create(guia_baja),
                  run_time=1.2, rate_func=linear)
        self.play(T.animate.set_value(T_FIN), run_time=T_FIN - T_CORTE - 1.2, rate_func=linear)
        self.cierre()


# =============================================================================
# 5. PADA como cuatro cajas enchufables, con dos ritmos
# =============================================================================
class PadaCuatroCajas(Pieza):
    def construct(self):
        XS = [-4.95, -1.65, 1.65, 4.95]
        YC, W, H = 0.35, 2.5, 1.15
        nombres = ["Percepción", "Análisis", "Decisión", "Acción"]
        reloj = ValueTracker(0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        F_LENTO, F_RAPIDO = 0.3, 1.5
        estado = {"falla": None}

        cajas = []
        for x, n in zip(XS, nombres):
            r = RoundedRectangle(corner_radius=0.14, width=W, height=H, color=C_ANT, fill_color=C_ANT,
                                 fill_opacity=0.12, stroke_width=3)
            cajas.append(VGroup(r, et(n, 26, TINTA)).move_to([x, YC, 0]))

        # enchufes entre cajas
        enchufes, clavijas = VGroup(), []
        for i in range(3):
            x0, x1 = XS[i] + W / 2, XS[i + 1] - W / 2
            toma = RoundedRectangle(corner_radius=0.04, width=0.13, height=0.5, color=TENUE, fill_color=C_EJE,
                                    fill_opacity=1, stroke_width=2).move_to([x1 - 0.065, YC, 0])
            pines = VGroup(*[Line([x0, YC + s * 0.11, 0], [x1 - 0.13, YC + s * 0.11, 0], color=TENUE, stroke_width=6)
                             for s in (-1, 1)])
            enchufes.add(toma)
            clavijas.append(pines)

        # red de satélites abajo
        SX = [-4.95, -2.95, -0.95, 0.95, 2.95, 4.95]
        SY = -2.35
        sats = VGroup(*[satelite(0.24).move_to([x, SY, 0]) for x in SX])
        enl = VGroup(*[DashedLine([SX[i] + 0.5, SY, 0], [SX[i + 1] - 0.5, SY, 0], color=TENUE, stroke_width=2,
                                  dash_length=0.1) for i in range(5)])

        def meneo(m):
            t = reloj.get_value()
            for k, s in enumerate(m):
                s.move_to([SX[k], SY + 0.05 * np.sin(1.3 * t + k), 0])
        sats.add_updater(meneo)

        # metrónomos sobre Análisis (lento) y Decisión (rápido)
        def metronomo(x, f, idx):
            cuerpo = Polygon([x - 0.45, 1.15, 0], [x + 0.45, 1.15, 0], [x + 0.18, 2.55, 0], [x - 0.18, 2.55, 0],
                             color=TENUE, fill_color=C_PANEL, fill_opacity=0.7, stroke_width=2.5)
            piv = np.array([x, 1.35, 0])
            varilla = Line(piv, piv + UP * 1.05, color=TINTA, stroke_width=4)
            pesa = Square(0.16, color=TINTA, fill_color=TINTA, fill_opacity=1, stroke_width=0)
            brazo = VGroup(varilla, pesa)

            def act(m):
                t = reloj.get_value()
                if estado["falla"] is not None and idx == 1:
                    t = estado["falla"]
                ang = 0.42 * np.sin(TAU * f * t)
                d = np.array([-np.sin(ang), np.cos(ang), 0])
                m[0].put_start_and_end_on(piv, piv + d * 1.05)
                m[1].move_to(piv + d * 0.72)
            brazo.add_updater(act)
            act(brazo)
            return VGroup(cuerpo, brazo)

        metL = metronomo(XS[1], F_LENTO, 1)
        metR = metronomo(XS[2], F_RAPIDO, 2)
        lLen = et("Lento", 22, TENUE).next_to(metL[0], RIGHT, buff=0.2).shift(UP * 0.3)
        lRap = et("Rápido", 22, TENUE).next_to(metR[0], RIGHT, buff=0.2).shift(UP * 0.3)

        def pulso(f, t):
            return np.exp(-((2 * f * t) % 1) * 7)

        def act_caja_lenta(m):
            if estado["falla"] is None:
                m[0].set_fill(opacity=0.12 + 0.45 * pulso(F_LENTO, reloj.get_value()))

        def act_caja_rapida(m):
            m[0].set_fill(opacity=0.12 + 0.4 * pulso(F_RAPIDO, reloj.get_value()))

        # flujos de datos
        P_SUBE = [np.array([XS[0], SY + 0.3, 0]), np.array([XS[0], YC - H / 2 - 0.05, 0])]
        P_BAJA = [np.array([XS[3], YC - H / 2 - 0.05, 0]), np.array([XS[3], SY + 0.3, 0])]
        P_PA = [np.array([XS[0] + W / 2, YC, 0]), np.array([XS[1] - W / 2, YC, 0])]
        P_AD = [np.array([XS[1] + W / 2, YC, 0]), np.array([XS[2] - W / 2, YC, 0])]
        P_DA = [np.array([XS[2] + W / 2, YC, 0]), np.array([XS[3] - W / 2, YC, 0])]
        tubos = VGroup(Line(*P_SUBE, color=C_EJE, stroke_width=2), Line(*P_BAJA, color=C_EJE, stroke_width=2))

        def continuo(ruta, n, per, col):
            g = VGroup(*[Dot(radius=0.07, color=col) for _ in range(n)])

            def act(m):
                t = reloj.get_value()
                for j, d in enumerate(m):
                    u = ((t / per) + j / n) % 1
                    d.move_to(ruta[0] * (1 - u) + ruta[1] * u)
                    d.set_opacity(0 if t < 0.05 else 1)
            g.add_updater(act)
            return g

        def por_tic(ruta, f, col, idx, dur=0.3, r=0.08):
            d = Dot(radius=r, color=col)

            def act(m):
                t = reloj.get_value()
                if estado["falla"] is not None and idx == 1:
                    m.set_opacity(0)
                    return
                tau = ((2 * f * t) % 1) / (2 * f)
                u = tau / dur
                if u > 1:
                    m.set_opacity(0)
                else:
                    m.set_opacity(1).move_to(ruta[0] * (1 - u) + ruta[1] * u)
            d.add_updater(act)
            return d

        self.add(chip_desarrollo())
        self.play(FadeIn(sats, lag_ratio=0.1), Create(enl), run_time=0.9)
        self.add(reloj)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.5) for c in cajas], lag_ratio=0.2), FadeIn(enchufes),
                  run_time=1.3)
        self.play(LaggedStart(*[GrowFromEdge(p, LEFT) for p in clavijas], lag_ratio=0.3), run_time=1.0)
        self.play(*[Flash(e.get_center(), color=C_ANT, flash_radius=0.3, line_length=0.12, num_lines=8)
                    for e in enchufes], run_time=0.5)
        self.play(FadeIn(metL), FadeIn(metR), FadeIn(lLen), FadeIn(lRap), Create(tubos), run_time=0.8)

        flujos = VGroup(continuo(P_SUBE, 4, 1.4, C_SAT), continuo(P_PA, 2, 0.7, C_ANT),
                        por_tic(P_AD, F_LENTO, C_CIELO, 1, 0.5, 0.1), por_tic(P_DA, F_RAPIDO, C_ANT, 2),
                        por_tic(P_BAJA, F_RAPIDO, C_SAT, 2, 0.3))
        cajas[1].add_updater(act_caja_lenta)
        cajas[2].add_updater(act_caja_rapida)
        cajas[3].add_updater(act_caja_rapida)
        self.add(flujos)
        self.wait(7.5)

        # falla localizada: se sabe qué caja falló
        estado["falla"] = reloj.get_value()
        for c in cajas:
            c.clear_updaters()
        mal = cajas[1]
        mNo = marca_no(mal.get_corner(UR) + np.array([-0.3, 0.32, 0]), 0.3)
        oks = VGroup(*[marca_ok(c.get_corner(UR) + np.array([-0.3, 0.32, 0]), 0.3) for c in (cajas[0], cajas[2], cajas[3])])
        fondo_m = VGroup(*[Circle(radius=0.24, stroke_width=0, fill_color=FONDO, fill_opacity=1).move_to(m.get_center())
                           for m in [mNo, *oks]])
        self.play(mal[0].animate.set_stroke(C_MAL, width=5).set_fill(C_MAL, opacity=0.35),
                  *[c[0].animate.set_stroke(C_OK).set_fill(C_OK, opacity=0.15) for c in (cajas[0], cajas[2], cajas[3])],
                  metL[1][0].animate.set_color(C_MAL), run_time=1.0)
        self.play(FadeIn(fondo_m), Create(mNo), *[Create(o) for o in oks], run_time=0.6)
        self.play(Indicate(mal, color=C_MAL, scale_factor=1.06), run_time=0.8)
        self.wait(2.0)
        self.cierre()


# =============================================================================
# 6. Una sola decisión conjunta entre capas
# =============================================================================
class DecisionConjunta(Pieza):
    def construct(self):
        YS = [1.9, 0.0, -1.9]  # núcleo, transporte, radio
        nombres = ["Núcleo", "Transporte", "Capa radio"]
        X0, X1, HB = -6.5, 4.2, 1.7
        XAG = -4.1
        reloj = ValueTracker(0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))

        bandas = VGroup(*[RoundedRectangle(corner_radius=0.15, width=X1 - X0, height=HB, color=C_EJE,
                                           fill_color=C_PANEL, fill_opacity=0.35, stroke_width=2)
                          .move_to([(X0 + X1) / 2, y, 0]) for y in YS])
        etiquetas = VGroup(*[et(n, 22, TINTA).move_to([-5.55, y, 0]) for n, y in zip(nombres, YS)])
        agentes = VGroup(*[Circle(radius=0.26, color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.35, stroke_width=3)
                           .move_to([XAG, y, 0]) for y in YS])
        conos = VGroup(*[Polygon([XAG + 0.28, y, 0], [3.3, y + 0.72, 0], [3.3, y - 0.72, 0], stroke_width=0,
                                 fill_color=C_CIELO, fill_opacity=0.1) for y in YS])

        # medidor global
        MX, MY0, MH = 5.5, -2.4, 4.6
        g = ValueTracker(0.55)
        marco = Rectangle(width=0.7, height=MH, color=TENUE, stroke_width=2.5).move_to([MX, MY0 + MH / 2, 0])
        lleno = always_redraw(lambda: Rectangle(width=0.62, height=max(MH * g.get_value() - 0.08, 0.01), stroke_width=0,
                                                fill_color=_mezcla(C_MAL, C_OK, (g.get_value() - 0.2) / 0.6),
                                                fill_opacity=0.85).move_to([MX, MY0 + 0.04 + (MH * g.get_value() - 0.08) / 2, 0]))
        lRec = et("Recompensa común", 20, TINTA).next_to(marco, UP, buff=0.22)

        # carriles: cada capa elige dónde pasa el flujo
        xs = [ValueTracker(1.1) for _ in range(3)]  # núcleo, transporte, radio
        J = [0.95, -0.95]  # fronteras núcleo|transporte y transporte|radio

        def ruta():
            xn, xt, xr = [v.get_value() for v in xs]
            return [np.array(p + (0,)) for p in [(xr, -2.75), (xr, J[1]), (xt, J[1]), (xt, J[0]), (xn, J[0]), (xn, 2.75)]]

        visible = ValueTracker(0)

        def dibujar():
            pts = ruta()
            op = visible.get_value()
            gr = VGroup()
            for a, b in zip(pts[:-1], pts[1:]):
                horiz = abs(a[1] - b[1]) < 1e-6
                if horiz:
                    if abs(a[0] - b[0]) > 0.05:
                        gr.add(DashedLine(a, b, color=C_MAL, stroke_width=4, dash_length=0.08).set_stroke(opacity=op))
                        for p in (a, b):
                            gr.add(Star(n=6, outer_radius=0.17, inner_radius=0.07, color=C_MAL, fill_color=C_MAL,
                                        fill_opacity=op, stroke_width=0).move_to(p))
                else:
                    gr.add(Line(a, b, color=C_ANT, stroke_width=6).set_stroke(opacity=op))
            return gr
        camino = always_redraw(dibujar)

        N = 9

        def act_paq(m):
            pts = ruta()
            L = _largo(pts)
            # primer corte (si lo hay)
            s_corte, acc = None, 0.0
            for a, b in zip(pts[:-1], pts[1:]):
                l_ = np.linalg.norm(b - a)
                if abs(a[1] - b[1]) < 1e-6 and l_ > 0.05:
                    s_corte = acc
                    break
                acc += l_
            t = reloj.get_value()
            op = visible.get_value()
            for j, d in enumerate(m):
                s = ((t * 1.6 / L) + j / N) % 1 * L
                if s_corte is not None and s > s_corte:
                    if s < s_corte + 0.6:
                        d.move_to(_sobre(pts, s_corte)).set_color(C_MAL).set_opacity(op * (1 - (s - s_corte) / 0.6))
                    else:
                        d.set_opacity(0)
                else:
                    d.move_to(_sobre(pts, s)).set_color(TINTA).set_opacity(op)
        paquetes = VGroup(*[Dot(radius=0.08) for _ in range(N)])
        paquetes.add_updater(act_paq)

        # medidores locales (cada capa optimiza lo suyo)
        locales = VGroup(*[Rectangle(width=0.26, height=1.2, stroke_width=0, fill_color=C_OK, fill_opacity=0.8)
                           .move_to([3.8, y - 0.1, 0]) for y in YS])

        self.add(chip_desarrollo())
        self.add(reloj)
        self.play(LaggedStart(*[FadeIn(b) for b in bandas], lag_ratio=0.15), FadeIn(etiquetas), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(a, scale=0.6) for a in agentes], lag_ratio=0.15),
                  LaggedStart(*[FadeIn(c) for c in conos], lag_ratio=0.15), run_time=1.0)
        self.play(Create(marco), FadeIn(lRec), run_time=0.6)
        self.add(lleno)

        # controladores separados: cada uno elige su carril (orden: núcleo, transporte, radio)
        xs[0].set_value(-0.2)
        xs[1].set_value(2.4)
        xs[2].set_value(1.1)
        self.add(camino, paquetes)
        self.play(visible.animate.set_value(1), *[Indicate(a, color=C_CIELO, scale_factor=1.3) for a in agentes],
                  LaggedStart(*[GrowFromEdge(r, DOWN) for r in locales], lag_ratio=0.2), run_time=1.5)
        self.play(g.animate.set_value(0.2), run_time=1.5)
        self.wait(2.2)

        # una sola decisión conjunta con recompensa común
        enlace = Line(agentes[0].get_bottom(), agentes[2].get_top(), color=C_OK, stroke_width=5)
        ramas = VGroup(*[DashedLine([MX - 0.4, y, 0], [X1 + 0.05, y, 0], color=C_OK, stroke_width=2.5, dash_length=0.1)
                         for y in YS])
        self.play(Create(enlace), Create(ramas),
                  *[a.animate.set_color(C_OK).set_fill(C_OK, opacity=0.5) for a in agentes],
                  *[c.animate.set_fill(C_OK, opacity=0.1) for c in conos],
                  FadeOut(locales), run_time=1.2)
        self.play(*[v.animate.set_value(1.1) for v in xs], run_time=1.5)
        self.play(g.animate.set_value(0.85), run_time=1.5)
        self.wait(2.5)
        self.cierre()


# =============================================================================
# 7. El agente dentro del satélite: tres restricciones que en tierra no existen
# =============================================================================
class SateliteDeviceAgent(Pieza):
    def construct(self):
        CT = np.array([0.0, -19.0, 0])
        RT, RO = 16.0, 20.2
        fase = ValueTracker(0.06)
        PH0, PH1 = 106.0, 74.0
        PH_EST = 100.0
        ZONA = (80.0, 86.0)

        def polar(r, ang_deg):
            a = np.radians(ang_deg)
            return CT + r * np.array([np.cos(a), np.sin(a), 0])

        def phi():
            u = fase.get_value() % 1
            return PH0 + (PH1 - PH0) * u, u

        tierra_ = Circle(radius=RT, color=C_TIERRA, fill_color=C_TIERRA_2, fill_opacity=1, stroke_width=3,
                         num_components=120).move_to(CT)
        orbita = DashedVMobject(Arc(radius=RO, start_angle=np.radians(PH1 - 4), angle=np.radians(PH0 - PH1 + 8),
                                    arc_center=CT), num_dashes=60).set_stroke(C_EJE, 2)
        # sombra (eclipse) a la izquierda, sol a la derecha
        C_SOL = _mezcla(C_SAT, TINTA, 0.2)
        sombra = Polygon([-7.3, 4.2, 0], [-0.6, 4.2, 0], [-1.6, -4.2, 0], [-7.3, -4.2, 0], stroke_width=0,
                         fill_color=_mezcla(FONDO, "#000000", 0.45) if OSCURO else C_EJE,
                         fill_opacity=1 if OSCURO else 0.35)
        luz = Polygon([-0.6, 4.2, 0], [7.3, 4.2, 0], [7.3, -4.2, 0], [-1.6, -4.2, 0], stroke_width=0,
                      fill_color=C_SOL, fill_opacity=0.06)
        sombra = VGroup(sombra, luz).set_z_index(-2)
        SOL = np.array([5.9, 2.95, 0])
        sol = VGroup(Circle(radius=0.34, color=C_SOL, fill_color=C_SOL, fill_opacity=0.9, stroke_width=2).move_to(SOL),
                     *[Line(SOL + 0.46 * np.array([np.cos(a), np.sin(a), 0]), SOL + 0.66 * np.array([np.cos(a), np.sin(a), 0]),
                            color=C_SOL, stroke_width=3) for a in np.arange(8) * PI / 4])

        # batería
        BAT = np.array([-5.3, 2.8, 0])
        caja_b = RoundedRectangle(corner_radius=0.08, width=1.2, height=0.52, color=TINTA, stroke_width=3).move_to(BAT)
        borne = Rectangle(width=0.1, height=0.2, color=TINTA, fill_color=TINTA, fill_opacity=1, stroke_width=0
                          ).next_to(caja_b, RIGHT, buff=0.02)
        lEn = et("Energía finita", 22, TINTA).next_to(caja_b, DOWN, buff=0.2)

        def nivel():
            u = fase.get_value() % 1
            return 0.85 - 1.3 * u if u < 0.41 else 0.317 + 0.92 * (u - 0.41)

        def carga():
            lv = float(np.clip(nivel(), 0.05, 1))
            c = C_MAL if lv < 0.4 else (C_SAT if lv < 0.6 else C_OK)
            return Rectangle(width=1.06 * lv, height=0.38, stroke_width=0, fill_color=c, fill_opacity=0.9
                             ).move_to(BAT + LEFT * 0.53 + RIGHT * 0.53 * lv)
        relleno = always_redraw(carga)

        # estación en tierra
        pe = polar(RT, PH_EST)
        est = estacion(0.55).move_to(pe, aligned_edge=DOWN).shift(DOWN * 0.05)
        lCon = et("Contacto intermitente", 22, TINTA).move_to([-4.75, -2.75, 0])

        # zona regulada
        zona = AnnularSector(inner_radius=RT, outer_radius=RT + 1.4, angle=np.radians(ZONA[1] - ZONA[0]),
                             start_angle=np.radians(ZONA[0]), arc_center=CT, stroke_color=C_MAL, stroke_width=2,
                             fill_color=C_MAL, fill_opacity=0.28)
        cand = _candado(C_MAL, 0.38).move_to(polar(RT + 0.72, np.mean(ZONA)))
        lReg = et("Límites regulatorios", 22, TINTA).next_to(polar(RT + 1.1, ZONA[0]), RIGHT, buff=0.3)

        # satélite con su agente
        sat = satelite(0.34)
        agente = Dot(radius=0.1, color=C_CIELO)
        halo = Circle(radius=0.62, color=C_CIELO, stroke_width=2.5)
        nave = VGroup(sat, agente, halo)

        def act_nave(m):
            ph, u = phi()
            op = float(np.clip(min(u, 1 - u) / 0.05, 0, 1))
            m.move_to(polar(RO, ph))
            sol_ = m.get_center()[0] > -1.1
            m[0][0].set_fill(opacity=0.9 * op).set_stroke(opacity=op)
            for p in m[0][1:]:
                p.set_fill(opacity=(0.85 if sol_ else 0.25) * op).set_stroke(opacity=op)
            m[1].set_opacity(op)
            pul = 0.5 + 0.5 * np.sin(fase.get_value() * TAU * 3)
            m[2].set_stroke(opacity=op * (0.35 + 0.5 * pul))
        nave.add_updater(act_nave)

        def haz_():
            ph, u = phi()
            op = float(np.clip(min(u, 1 - u) / 0.05, 0, 1))
            dentro = ZONA[0] - 1.5 <= ph <= ZONA[1] + 1.5
            p = polar(RO, ph) + DOWN * 0.25
            if dentro:  # emisión bloqueada: el haz se corta sobre la zona
                return Polygon(p, polar(RT + 1.45, ph - 1.9), polar(RT + 1.45, ph + 1.9), stroke_color=C_MAL,
                               stroke_width=2, stroke_opacity=0.8 * op, fill_color=C_MAL, fill_opacity=0.12 * op)
            return Polygon(p, polar(RT, ph - 2.2), polar(RT, ph + 2.2), stroke_width=0,
                           fill_color=C_SAT, fill_opacity=0.25 * op)
        cono = always_redraw(haz_)

        def enlace_():
            ph, u = phi()
            vis = abs(ph - PH_EST) < 6
            parp = 0.5 + 0.5 * np.sign(np.sin(fase.get_value() * TAU * 9))
            borde = abs(abs(ph - PH_EST) - 6) < 1.2
            op = (parp if borde else 1.0) if vis else 0.0
            return DashedLine(est.get_top(), polar(RO, ph) + DOWN * 0.2, color=C_ANT, stroke_width=3,
                              dash_length=0.12).set_stroke(opacity=op)
        enlace = always_redraw(enlace_)

        def act_cand(m):
            ph, u = phi()
            dentro = ZONA[0] - 1.5 <= ph <= ZONA[1] + 1.5
            m.set_opacity(1.0 if dentro else 0.6)
            m.set_fill(opacity=0.8 if dentro else 0.35)
            m[2].set_fill(opacity=1)

        self.add(chip("Hueco abierto", C_CIELO))
        self.play(FadeIn(sombra), FadeIn(tierra_, shift=UP * 0.3), Create(orbita), FadeIn(sol, scale=0.6), run_time=1.2)
        self.play(FadeIn(nave, scale=0.5), run_time=0.8)
        act_nave(nave)
        self.play(Flash(nave.get_center(), color=C_CIELO, flash_radius=0.8, line_length=0.2), run_time=0.6)
        self.add(cono)
        self.bring_to_front(nave)
        self.play(FadeIn(caja_b), FadeIn(borne), FadeIn(relleno), FadeIn(lEn), run_time=0.6)
        self.play(FadeIn(est, shift=UP * 0.2), FadeIn(lCon), run_time=0.6)
        self.play(FadeIn(zona), FadeIn(cand, scale=0.6), FadeIn(lReg), run_time=0.6)
        cand.add_updater(act_cand)
        self.add(enlace)
        self.bring_to_front(nave)
        self.play(fase.animate.set_value(2.62), run_time=15.5, rate_func=linear)
        self.cierre()

"""Piezas del comité tutorial (bloques 1-4): el campo mide mal, problema, hipótesis y brecha."""
from tesis_lib import *
from code_lib import _vigilar
import numpy as np


# ---------- helpers locales ----------
def simbolo(txt, tam=30, color=None, **kw):
    """Símbolo corto (π(t), A − B…) en Carlito, sin LaTeX."""
    return Text(txt, font=FUENTE, font_size=tam, color=color or TINTA, **kw)


def chip_libre(texto, color=None, tam=18, esquina=DL, buff=0.35):
    """Como chip(), pero admite separadores «·» (no cuentan como palabra)."""
    _vigilar(texto.replace("·", " "))
    c = color or C_CIELO
    t = Text(texto, font=FUENTE, font_size=tam, color=c)
    caja_ = RoundedRectangle(corner_radius=0.14, width=t.width + 0.5, height=t.height + 0.3, color=c,
                             fill_color=c, fill_opacity=0.12, stroke_width=2)
    t.move_to(caja_)
    return VGroup(caja_, t).to_corner(esquina, buff=buff)


def losa(ancho, alto, color, relleno=0.18, trazo_=2.5, radio=0.1):
    return RoundedRectangle(corner_radius=radio, width=ancho, height=alto, color=color,
                            fill_color=color, fill_opacity=relleno, stroke_width=trazo_)


# =============================================================================
# 1. Lazo abierto gana (Ellis et al., SMACv2, NeurIPS 2023)
# =============================================================================
class LazoAbiertoGana(Pieza):
    def construct(self):
        rng = np.random.default_rng(42)

        def entorno(pos):
            r = losa(1.5, 1.15, C_EJE, 0.35).set_fill(C_PANEL, 0.7).move_to(pos)
            pts = VGroup(*[Dot(pos + np.array([rng.uniform(-0.55, 0.55), rng.uniform(-0.4, 0.4), 0]),
                               radius=0.05, color=TENUE) for _ in range(7)])
            return VGroup(r, pts)

        def politica(txt, pos, col):
            b = losa(1.55, 0.95, col, 0.15).move_to(pos)
            return VGroup(b, simbolo(txt, 32, col).move_to(pos))

        Y1, Y2 = 1.75, -0.75
        XE, XP = -5.9, -3.1
        env1, env2 = entorno(np.array([XE, Y1, 0])), entorno(np.array([XE, Y2, 0]))
        pt = politica("π(t)", np.array([XP, Y1, 0]), TENUE)
        po = politica("π(o)", np.array([XP, Y2, 0]), C_ANT)

        def lazo(env, pol, col, abierto):
            a = env[0].get_right() + UP * 0.22
            b = pol[0].get_left() + UP * 0.22
            if abierto:
                obs = DashedLine(a, b, color=TENUE, stroke_width=2, dash_length=0.1, stroke_opacity=0.5)
            else:
                obs = flecha(a, b, col, 3, 0.16)
            acc = flecha(pol[0].get_left() + DOWN * 0.22, env[0].get_right() + DOWN * 0.22, col, 3, 0.16)
            return obs, acc

        obs1, acc1 = lazo(env1, pt, TENUE, True)
        obs2, acc2 = lazo(env2, po, C_ANT, False)
        corte = marca_no(obs1.get_center(), 0.24)

        # reloj: la única entrada de π(t)
        reloj_c = np.array([XP, Y1 + 1.35, 0])
        reloj = Circle(radius=0.27, color=TENUE, stroke_width=2.5).move_to(reloj_c)
        manecilla = Line(reloj_c, reloj_c + UP * 0.2, color=TINTA, stroke_width=3)
        fase = ValueTracker(0)
        manecilla.add_updater(lambda m: m.put_start_and_end_on(
            reloj_c, reloj_c + 0.2 * np.array([np.sin(fase.get_value()), np.cos(fase.get_value()), 0])))
        f_reloj = flecha(reloj.get_bottom(), pt[0].get_top(), TENUE, 3, 0.14)
        fase.add_updater(lambda m, dt: m.increment_value(dt * 2.2))
        self.add(fase)

        l_t = et("Solo el tiempo", 22, TENUE).move_to([(XE + XP) / 2, Y1 - 0.95, 0])
        l_o = et("Observa estado", 22, C_ANT).move_to([(XE + XP) / 2, Y2 - 0.95, 0])

        self.play(FadeIn(env1), FadeIn(env2), FadeIn(pt), FadeIn(po), run_time=1.0)
        self.play(FadeIn(reloj), Create(manecilla), GrowArrow(f_reloj), Create(obs1), GrowArrow(acc1),
                  run_time=1.0)
        self.play(Create(corte), FadeIn(l_t, shift=UP * 0.1), run_time=0.7)
        viaje = Dot(obs2.get_start(), radius=0.07, color=C_ANT)
        self.play(GrowArrow(obs2), GrowArrow(acc2), run_time=0.8)
        self.play(MoveAlongPath(viaje, Line(obs2.get_start(), obs2.get_end())), FadeIn(l_o, shift=UP * 0.1),
                  run_time=0.8)
        self.remove(viaje)
        self.respiro(0.4)

        # tablero de escenarios del banco canónico
        filas, cols, cw, ch, gap = 4, 5, 0.95, 0.72, 0.1
        c0 = np.array([3.55, 1.25, 0])
        celdas = {}
        tablero = VGroup()
        for i in range(filas):
            for j in range(cols):
                p = c0 + np.array([(j - (cols - 1) / 2) * (cw + gap), ((filas - 1) / 2 - i) * (ch + gap), 0])
                r = Rectangle(width=cw, height=ch, color=C_EJE, stroke_width=2, fill_color=C_PANEL,
                              fill_opacity=0.45).move_to(p)
                celdas[(i, j)] = r
                tablero.add(r)
        self.play(LaggedStart(*[FadeIn(r, scale=0.8) for r in tablero], lag_ratio=0.03), run_time=1.0)

        gana = sorted(rng.choice(filas * cols, size=9, replace=False))
        encender = []
        for k in gana:
            r = celdas[(k // cols, k % cols)]
            encender.append(AnimationGroup(r.animate.set_fill(C_MAL, 0.3).set_stroke(C_MAL, 2.5),
                                           FadeIn(simbolo("π(t)", 20, C_MAL).move_to(r))))
        ley = VGroup(Square(0.26, color=C_MAL, fill_color=C_MAL, fill_opacity=0.3, stroke_width=2.5),
                     et("Gana", 22, C_MAL)).arrange(RIGHT, buff=0.15)
        ley.next_to(tablero, DOWN, buff=0.25).align_to(tablero, LEFT)
        self.play(LaggedStart(*encender, lag_ratio=0.28), FadeIn(ley), run_time=3.0)
        self.respiro(0.4)

        # margen: π(o) y π(t) casi iguales
        xb0, yb = 1.55, (-1.75, -2.35)
        largo = ValueTracker(0)
        eo = simbolo("π(o)", 22, C_ANT).move_to([xb0 - 0.45, yb[0], 0])
        etp = simbolo("π(t)", 22, TENUE).move_to([xb0 - 0.45, yb[1], 0])

        def barra_h(y, fr, col):
            return always_redraw(lambda: Rectangle(
                width=max(1e-3, 3.2 * fr * largo.get_value()), height=0.36, color=col, fill_color=col,
                fill_opacity=0.75, stroke_width=0).move_to([xb0, y, 0], aligned_edge=LEFT))

        bo, bt = barra_h(yb[0], 1.0, C_ANT), barra_h(yb[1], 0.985, TENUE)
        self.play(FadeIn(eo), FadeIn(etp), run_time=0.4)
        self.add(bo, bt)
        self.play(largo.animate.set_value(1), run_time=1.8)
        xf = xb0 + 3.2
        guia = DashedLine([xf, yb[0] + 0.3, 0], [xf, yb[1] - 0.3, 0], color=TINTA, stroke_width=2,
                          dash_length=0.08)
        l_m = et("Margen ≈ 0", 26, TINTA).next_to(guia, RIGHT, buff=0.2)
        self.play(Create(guia), FadeIn(l_m, shift=LEFT * 0.1), run_time=0.8)
        self.play(Indicate(l_m, color=C_MAL, scale_factor=1.1), run_time=0.8)

        self.play(FadeIn(chip_tercero("Ellis 2023")), FadeIn(chip_ilustrativo()), run_time=0.5)
        self.respiro(1.5)
        fase.clear_updaters()
        self.cierre()


# =============================================================================
# 2. El signo que se invierte (Yılmaz & Çelikcan, Applied Sciences 2026)
# =============================================================================
class SignoQueInvierte(Pieza):
    def construct(self):
        # --- zona A: diferencia A − B con IC
        Y0, ESC = 0.1, 1.0
        eje = Line([-5.9, -2.1, 0], [-5.9, 2.4, 0], color=C_EJE, stroke_width=3)
        cero = DashedLine([-5.9, Y0, 0], [-2.2, Y0, 0], color=TENUE, stroke_width=2, dash_length=0.1)
        l0 = simbolo("0", 22, TENUE).next_to(cero, LEFT, buff=0.12).shift(LEFT * 0.05)
        lab = simbolo("A − B", 26, TINTA).next_to(eje, UP, buff=0.15)
        mas = simbolo("+", 30, TENUE).move_to([-6.25, Y0 + 1.2, 0])
        menos = simbolo("−", 30, TENUE).move_to([-6.25, Y0 - 1.2, 0])
        X5, X10 = -4.7, -3.1
        l5 = et("5 semillas", 22, TENUE).move_to([X5, -2.55, 0])
        l10 = et("10 semillas", 22, TENUE).move_to([X10, -2.55, 0])
        self.play(Create(eje), Create(cero), FadeIn(l0), FadeIn(lab), FadeIn(mas), FadeIn(menos), run_time=1.0)

        def estimacion(x, centro, semi, col):
            a, b = [x, Y0 + (centro - semi) * ESC, 0], [x, Y0 + (centro + semi) * ESC, 0]
            return VGroup(Line(a, b, color=col, stroke_width=4),
                          Line(np.array(a) + LEFT * 0.16, np.array(a) + RIGHT * 0.16, color=col, stroke_width=4),
                          Line(np.array(b) + LEFT * 0.16, np.array(b) + RIGHT * 0.16, color=col, stroke_width=4),
                          Dot([x, Y0 + centro * ESC, 0], radius=0.1, color=col))

        e5 = estimacion(X5, 1.15, 0.55, C_ANT)
        self.play(GrowFromCenter(e5), FadeIn(l5), run_time=1.0)
        self.play(Indicate(mas, color=C_ANT, scale_factor=1.3), run_time=0.6)
        e10 = e5.copy()
        self.add(e10)
        self.play(e10.animate.move_to([X10, e5.get_center()[1], 0]), FadeIn(l10), run_time=0.7)
        self.play(Transform(e10, estimacion(X10, -0.75, 0.6, C_MAL)), run_time=1.4)
        self.play(Indicate(menos, color=C_MAL, scale_factor=1.3), run_time=0.6)

        # --- zona R: la política aleatoria cae dentro del rango de las entrenadas
        XR = -0.6
        ejer = Line([XR, -2.1, 0], [XR, 2.4, 0], color=C_EJE, stroke_width=3)
        banda = Rectangle(width=0.9, height=1.6, color=C_ANT, fill_color=C_ANT, fill_opacity=0.18,
                          stroke_width=2).move_to([XR, 0.6, 0])
        marcas = VGroup(*[Line([XR - 0.3, y, 0], [XR + 0.3, y, 0], color=C_ANT, stroke_width=4)
                          for y in (0.05, 0.3, 1.0, 1.2)])
        l_ent = et("Entrenadas", 20, C_ANT).next_to(ejer, UP, buff=0.15)
        dia = Square(0.26, color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.9).rotate(PI / 4)
        dia.move_to([XR, 2.9, 0])
        l_al = VGroup(Square(0.2, color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.9).rotate(PI / 4),
                      et("Aleatoria", 22, C_CIELO)).arrange(RIGHT, buff=0.12).move_to([XR, -2.55, 0])
        self.play(Create(ejer), FadeIn(banda), LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.2),
                  FadeIn(l_ent), run_time=1.0)
        self.play(dia.animate.move_to([XR, 0.55, 0]), FadeIn(l_al), rate_func=smooth, run_time=1.0)
        self.play(Flash(dia, color=C_CIELO, flash_radius=0.35), run_time=0.5)

        # --- zona B: valores p frente al umbral, antes y después de corregir
        XB0, YB = 1.4, -2.1
        ejb = VGroup(Line([XB0, YB, 0], [6.4, YB, 0], color=C_EJE, stroke_width=3),
                     Line([XB0, YB, 0], [XB0, 0.4, 0], color=C_EJE, stroke_width=3))
        lp = simbolo("p", 26, TENUE).next_to(ejb[1], UP, buff=0.12)
        alturas = [0.55, 1.5, 0.35, 0.8, 1.9, 0.45]
        U0, U1 = 1.0, 1.0 / len(alturas)
        barras = VGroup(*[barra(XB0 + 0.6 + 0.78 * k, YB, h, 0.46, C_OK if h < U0 else TENUE, 0.8)
                          for k, h in enumerate(alturas)])
        umbral = DashedLine([XB0, YB + U0, 0], [6.4, YB + U0, 0], color=TINTA, stroke_width=3, dash_length=0.12)

        def muestra(linea, txt, col, y):
            return VGroup(linea, et(txt, 22, col)).arrange(RIGHT, buff=0.2).move_to([XB0, y, 0], aligned_edge=LEFT)

        ley_s = muestra(DashedLine(LEFT * 0.3, RIGHT * 0.3, color=TINTA, stroke_width=3, dash_length=0.1),
                        "Sin corrección", TINTA, 2.35)
        ley_c = muestra(Line(LEFT * 0.3, RIGHT * 0.3, color=C_CIELO, stroke_width=4),
                        "Con corrección", C_CIELO, 1.7)
        self.play(Create(ejb), FadeIn(lp), LaggedStart(*[GrowFromEdge(b, DOWN) for b in barras], lag_ratio=0.12),
                  run_time=1.2)
        self.play(Create(umbral), FadeIn(ley_s), run_time=0.8)
        self.respiro(0.5)
        umbral_c = Line([XB0, YB + U1, 0], [6.4, YB + U1, 0], color=C_CIELO, stroke_width=4)
        self.play(ReplacementTransform(umbral.copy(), umbral_c), umbral.animate.set_stroke(opacity=0.35),
                  FadeIn(ley_c), run_time=1.5)
        self.play(*[b.animate.set_fill(C_MAL, 0.55).set_stroke(C_MAL) for b in barras], run_time=0.8)
        cruces = VGroup(*[marca_no(b.get_top() + UP * 0.25, 0.2) for b in barras])
        self.play(LaggedStart(*[Create(c) for c in cruces], lag_ratio=0.1), run_time=0.8)

        self.play(FadeIn(chip_tercero("Yılmaz 2026")), FadeIn(chip("Fútbol, no NTN", TENUE, esquina=DR)),
                  FadeIn(chip_ilustrativo(esquina=UR)), run_time=0.5)
        self.respiro(1.6)
        self.cierre()


# =============================================================================
# 3. La escala, en cien cuadros (McDowell, corte 13-ago-2026)
# =============================================================================
class EscalaEnCien(Pieza):
    def construct(self):
        N, PASO, LADO = 10, 0.5, 0.42
        c0 = np.array([-3.35, 0.15, 0])
        cuadros = VGroup()
        for k in range(N * N):
            i, j = divmod(k, N)
            p = c0 + np.array([(j - (N - 1) / 2) * PASO, ((N - 1) / 2 - i) * PASO, 0])
            cuadros.add(Square(LADO, color=C_EJE, stroke_width=1.5, fill_color=C_EJE, fill_opacity=0.5).move_to(p))

        # contador de satélites activos
        total = ValueTracker(0)
        num = DecimalNumber(0, num_decimal_places=0, font_size=110, color=TINTA)
        num.set_stroke(width=0)
        pos_num = np.array([3.55, 1.85, 0])
        num.add_updater(lambda m: m.set_value(total.get_value()).move_to(pos_num))
        l_act = et("Satélites activos", 24, TENUE).move_to(pos_num + DOWN * 0.95)
        self.add(num)
        self.play(total.animate.set_value(16279),
                  LaggedStart(*[FadeIn(q, scale=0.6) for q in cuadros], lag_ratio=0.04),
                  rate_func=linear, run_time=4.0)
        self.play(FadeIn(l_act), Indicate(num, color=TINTA, scale_factor=1.05), run_time=0.8)
        num.clear_updaters()

        # Starlink 66 % y el resto
        ley_s = VGroup(Square(0.34, color=C_SAT, fill_color=C_SAT, fill_opacity=0.9),
                       et("Starlink 66 %", 26, C_SAT)).arrange(RIGHT, buff=0.2)
        ley_s.move_to([2.2, -0.2, 0], aligned_edge=LEFT)
        self.play(LaggedStart(*[cuadros[k].animate.set_fill(C_SAT, 0.9).set_stroke(C_SAT) for k in range(66)],
                              lag_ratio=0.03),
                  LaggedStart(*[cuadros[k].animate.set_fill(C_ANT, 0.55).set_stroke(C_ANT) for k in range(66, 100)],
                              lag_ratio=0.03),
                  FadeIn(ley_s), run_time=2.6)
        self.respiro(0.5)

        # 86.8 % maniobrables: barrido de anillo; el último cuadro, parcial (0.8)
        halos = VGroup()
        maniobra = np.random.default_rng(42).permutation(N * N)[:87]   # sin orden por color
        for k, idx in enumerate(maniobra):
            ang = TAU if k < 86 else 0.8 * TAU
            h = Arc(radius=0.12, start_angle=PI / 2, angle=-ang, color=FONDO, stroke_width=4)
            halos.add(h.move_arc_center_to(cuadros[int(idx)].get_center()))
        pct = ValueTracker(0)
        n_pct = DecimalNumber(0, num_decimal_places=1, font_size=40, color=TINTA)
        n_pct.set_stroke(width=0)
        anillo = VGroup(Square(0.36, color=TENUE, fill_color=TENUE, fill_opacity=0.6, stroke_width=0),
                        Circle(radius=0.11, color=FONDO, stroke_width=4))
        u_pct = Text("%", font=FUENTE, font_size=28, color=TENUE)
        pos_p = np.array([2.2, -1.1, 0])

        def acomoda(m):
            m.set_value(pct.get_value())
            m.next_to(anillo, RIGHT, buff=0.22)
            u_pct.next_to(m, RIGHT, buff=0.1, aligned_edge=DOWN)
        anillo.move_to(pos_p, aligned_edge=LEFT)
        n_pct.add_updater(acomoda)
        acomoda(n_pct)
        l_man = et("Maniobrables", 24, TENUE).next_to(anillo, DOWN, buff=0.3).align_to(anillo, LEFT)
        self.play(FadeIn(anillo), FadeIn(n_pct), FadeIn(u_pct), run_time=0.4)
        self.play(LaggedStart(*[Create(h) for h in halos], lag_ratio=0.08),
                  pct.animate.set_value(86.8), rate_func=linear, run_time=3.4)
        n_pct.clear_updaters()
        self.play(FadeIn(l_man, shift=UP * 0.1), run_time=0.5)

        # pulso continuo: el sistema se mueve por construcción
        reloj = ValueTracker(0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)
        orden = np.arange(87)

        def late(g):
            t = reloj.get_value()
            for k, h in enumerate(g):
                a = 0.35 + 0.65 * (0.5 + 0.5 * np.cos(3.0 * t - 0.35 * orden[k]))
                h.set_stroke(opacity=a)
        halos.add_updater(late)
        self.play(FadeIn(chip_tercero("McDowell ago-2026")), run_time=0.5)
        self.wait(3.2)
        halos.clear_updaters()
        reloj.clear_updaters()
        self.cierre()


# =============================================================================
# 4. Capas y dominios: las propiedades emergen del acoplamiento
# =============================================================================
class CapasYDominios(Pieza):
    def construct(self):
        capas = ["Aplicación", "Núcleo", "Red", "Radio"]
        dominios = ["Tierra", "Aire", "Espacio"]
        c_aire = interpolate_color(ManimColor(C_ANT), ManimColor(C_CIELO), 0.5)
        col_dom = [C_ANT, c_aire, C_SAT]
        XS = [-2.75, -0.35, 2.05]
        YS = [1.75, 0.6, -0.55, -1.7]
        CW, CH = 2.1, 0.9
        cel = {}
        matriz = VGroup()
        for i, y in enumerate(YS):
            for j, x in enumerate(XS):
                r = losa(CW, CH, C_EJE, 0.0, 2).set_fill(C_PANEL, 0.55).move_to([x, y, 0])
                cel[(i, j)] = r
                matriz.add(r)
        l_capas = VGroup(*[et(c, 24, TINTA).move_to([-4.2, y, 0], aligned_edge=RIGHT) for c, y in zip(capas, YS)])
        l_dom = VGroup(*[et(d, 24, c).move_to([x, 2.75, 0]) for d, x, c in zip(dominios, XS, col_dom)])
        self.play(LaggedStart(*[FadeIn(r, scale=0.9) for r in matriz], lag_ratio=0.05),
                  LaggedStart(*[FadeIn(l, shift=RIGHT * 0.2) for l in l_capas], lag_ratio=0.15),
                  LaggedStart(*[FadeIn(l, shift=DOWN * 0.2) for l in l_dom], lag_ratio=0.15), run_time=1.8)
        self.respiro(0.4)

        # acoplamientos entre (capa, dominio): líneas que aparecen y se cruzan
        pares = [((3, 2), (2, 0)), ((2, 1), (1, 2)), ((1, 0), (0, 2)), ((3, 0), (0, 1)),
                 ((2, 2), (0, 0)), ((3, 1), (1, 0)), ((1, 1), (3, 2))]
        rng = np.random.default_rng(44)
        lineas, nodos, anims = VGroup(), VGroup(), []
        for a, b in pares:
            pa, pb = cel[a].get_center(), cel[b].get_center()
            ang = float(rng.choice([-1, 1])) * rng.uniform(0.35, 0.7)
            l = ArcBetweenPoints(pa, pb, angle=ang, color=C_CIELO, stroke_width=3.5, stroke_opacity=0.9)
            da, db = Dot(pa, radius=0.08, color=C_CIELO), Dot(pb, radius=0.08, color=C_CIELO)
            lineas.add(l)
            nodos.add(da, db)
            ca, cb = col_dom[a[1]], col_dom[b[1]]
            anims.append(AnimationGroup(
                cel[a].animate.set_stroke(ca, 3).set_fill(ca, 0.22),
                cel[b].animate.set_stroke(cb, 3).set_fill(cb, 0.22),
                FadeIn(da, scale=0.5), FadeIn(db, scale=0.5), Create(l)))
        self.play(LaggedStart(*anims, lag_ratio=0.45), run_time=5.0)

        # propiedades emergentes: la envolvente de todo el acoplamiento
        env = DashedVMobject(RoundedRectangle(corner_radius=0.3, width=matriz.width + 0.5,
                                              height=matriz.height + 0.45).move_to(matriz),
                             num_dashes=70).set_stroke(TINTA, 2.5)
        l_em = et("Propiedades emergentes", 26, TINTA).next_to(env, DOWN, buff=0.22)
        fase = ValueTracker(0)
        fase.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(fase)
        lineas.add_updater(lambda g: [l.set_stroke(opacity=0.45 + 0.5 * (0.5 + 0.5 * np.sin(3.2 * fase.get_value() + 1.7 * k)))
                                      for k, l in enumerate(g)])
        self.play(Create(env), FadeIn(l_em, shift=UP * 0.1), run_time=1.4)
        self.respiro(0.6)

        # un volante que solo mueve una capa
        cv = np.array([5.35, YS[2], 0])
        aro = Circle(radius=0.62, color=TENUE, stroke_width=5).move_to(cv)
        rayos = VGroup(*[Line(cv, cv + 0.62 * np.array([np.cos(a), np.sin(a), 0]), color=TENUE, stroke_width=4)
                         for a in (PI / 2, PI / 2 + 2 * PI / 3, PI / 2 + 4 * PI / 3)])
        cubo = Dot(cv, radius=0.12, color=TENUE)
        volante = VGroup(aro, rayos, cubo)
        mando = DashedLine(cel[(2, 2)].get_right(), aro.get_left(), color=TENUE, stroke_width=2.5, dash_length=0.1)
        self.play(FadeIn(volante, scale=0.8), Create(mando), run_time=0.8)
        fila_red = VGroup(*[cel[(2, j)] for j in range(3)])
        marco_red = SurroundingRectangle(fila_red, color=TINTA, buff=0.08, stroke_width=4)
        self.play(Rotate(volante, 0.6, about_point=cv), ShowPassingFlash(marco_red, time_width=0.6),
                  run_time=0.8)
        self.play(Rotate(volante, -1.2, about_point=cv), run_time=0.9)
        preg = Text("¿?", font=FUENTE, font_size=56, color=TINTA).move_to(cv)
        self.play(FadeOut(rayos), FadeOut(cubo), mando.animate.set_stroke(opacity=0.3),
                  aro.animate.set_stroke(TINTA), FadeIn(preg, scale=0.6), run_time=0.9)
        self.respiro(1.8)
        lineas.clear_updaters()
        fase.clear_updaters()
        self.cierre()


# =============================================================================
# 5. Hipótesis central y sus falsadores
# =============================================================================
class HipotesisYFalsadores(Pieza):
    def construct(self):
        YP = -0.95                                   # piso
        YL0, YL1 = 1.1, 1.55                         # losa
        piso = Line([-4.65, YP, 0], [4.65, YP, 0], color=C_EJE, stroke_width=5)
        muros = VGroup(*[Rectangle(width=0.6, height=YL0 - YP, color=TENUE, fill_color=C_PANEL, fill_opacity=0.9,
                                   stroke_width=2.5).move_to([s * 4.1, (YL0 + YP) / 2, 0]) for s in (-1, 1)])
        losa_ = Rectangle(width=9.2, height=YL1 - YL0, color=TINTA, fill_color=C_PANEL, fill_opacity=0.9,
                          stroke_width=2.5).move_to([0, (YL0 + YL1) / 2, 0])
        fronton = Polygon([-4.6, YL1, 0], [4.6, YL1, 0], [0, 3.3, 0], color=TINTA, fill_color=C_PANEL,
                          fill_opacity=0.9, stroke_width=2.5)
        l_hc = simbolo("HC", 46, TINTA).move_to([0, 2.15, 0])
        techo = VGroup(losa_, fronton, l_hc)
        self.play(Create(piso), FadeIn(muros, shift=UP * 0.2), run_time=1.0)
        self.play(FadeIn(techo, shift=DOWN * 0.3), run_time=1.1)

        pilares, ghosts = VGroup(), VGroup()
        for k, x in enumerate((-2.05, 0.0, 2.05)):
            r = Rectangle(width=0.62, height=YL0 - YP, color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.25,
                          stroke_width=2.5).move_to([x, (YL0 + YP) / 2, 0])
            pilares.add(VGroup(r, simbolo(f"SH{k + 1}", 22, C_CIELO).move_to(r)))
            ghosts.add(DashedVMobject(r.copy(), num_dashes=30).set_stroke(C_CIELO, 1.5, opacity=0.6))
        self.play(LaggedStart(*[GrowFromEdge(p, DOWN) for p in pilares], lag_ratio=0.2), run_time=1.0)

        # cables trampa F1-F3
        YW = [-1.55, -2.15, -2.75]
        cables, postes, sensores, l_f = VGroup(), VGroup(), VGroup(), VGroup()
        for k, y in enumerate(YW):
            cables.add(Line([-4.1, y, 0], [4.1, y, 0], color=TENUE, stroke_width=2.5))
            postes.add(Line([-4.1, YP, 0], [-4.1, y, 0], color=C_EJE, stroke_width=2),
                       Line([4.1, YP, 0], [4.1, y, 0], color=C_EJE, stroke_width=2))
            sensores.add(Circle(radius=0.13, color=TENUE, stroke_width=3).move_to([4.4, y, 0]))
            l_f.add(simbolo(f"F{k + 1}", 24, TINTA).move_to([-4.5, y, 0]))
        self.play(Create(postes), LaggedStart(*[Create(c) for c in cables], lag_ratio=0.2),
                  FadeIn(sensores), FadeIn(l_f), run_time=1.2)
        self.respiro(0.4)

        # las SH pueden caer sin tirar la HC
        for p in pilares:
            p.save_state()
        self.add(ghosts)
        self.play(LaggedStart(*[p.animate.stretch(0.06, 1, about_edge=DOWN).set_opacity(0.25) for p in pilares],
                              lag_ratio=0.25), run_time=1.8)
        ok_hc = marca_ok(np.array([0.9, 2.2, 0]), 0.34)
        self.play(Create(ok_hc), Indicate(l_hc, color=C_OK, scale_factor=1.12), run_time=0.9)
        self.respiro(0.4)
        self.play(*[Restore(p) for p in pilares], FadeOut(ok_hc), run_time=1.0)
        self.remove(ghosts)

        # prueba de cada falsador
        estados = [("Superada", "G1", None), ("Demo favorable", "G2b", "G3 pendiente"),
                   ("No se dispara", "Mapeo documentado", None)]
        for k, (y, (est, tag, pend)) in enumerate(zip(YW, estados)):
            punto = Dot([-4.1, y, 0], radius=0.08, color=C_OK)
            self.add(punto)
            anims = [punto.animate.move_to([4.27, y, 0])]
            self.play(*anims, rate_func=smooth, run_time=0.8)
            self.remove(punto)
            l_e = et(est, 21, C_OK).next_to(sensores[k], RIGHT, buff=0.18)
            t_ = et(tag, 18, TENUE).move_to([3.6, y + 0.24, 0], aligned_edge=RIGHT)
            extra = []
            if pend:
                pz = et(pend, 18, TENUE)
                cz = DashedVMobject(RoundedRectangle(corner_radius=0.1, width=pz.width + 0.3,
                                                     height=pz.height + 0.18), num_dashes=24).set_stroke(TENUE, 1.5)
                pend_g = VGroup(cz, pz.move_to(cz)).next_to(t_, LEFT, buff=0.2)
                extra.append(FadeIn(pend_g))
            self.play(sensores[k].animate.set_fill(C_OK, 0.9).set_stroke(C_OK), cables[k].animate.set_stroke(C_OK, 2.5, 0.8),
                      FadeIn(l_e, shift=LEFT * 0.1), FadeIn(t_), *extra, run_time=0.6)
        self.play(FadeIn(chip_desarrollo()), run_time=0.5)
        self.respiro(1.8)
        self.cierre()


# =============================================================================
# 6. Los organismos declaran el vacío por escrito
# =============================================================================
def documento(ancho=2.5, alto=3.1, color=None, hueco=(4, 5), semilla=0):
    """Hoja con esquina doblada y renglones; los renglones del intervalo `hueco` quedan libres."""
    c = color or TENUE
    d = 0.35
    w, h = ancho / 2, alto / 2
    hoja = Polygon([-w, -h, 0], [w, -h, 0], [w, h - d, 0], [w - d, h, 0], [-w, h, 0], color=c,
                   fill_color=C_PANEL, fill_opacity=0.8, stroke_width=2.5)
    pliegue = Polygon([w - d, h, 0], [w - d, h - d, 0], [w, h - d, 0], color=c, fill_color=c,
                      fill_opacity=0.35, stroke_width=2)
    rng = np.random.default_rng(semilla)
    ren = VGroup()
    n = 9
    ys = np.linspace(h - 0.55, -h + 0.35, n)
    for k, y in enumerate(ys):
        if hueco[0] <= k <= hueco[1]:
            continue
        lg = (ancho - 0.5) * rng.uniform(0.55, 1.0)
        ren.add(Line([-w + 0.25, y, 0], [-w + 0.25 + lg, y, 0], color=TENUE, stroke_width=4, stroke_opacity=0.45))
    yc = (ys[hueco[0]] + ys[hueco[1]]) / 2
    alto_h = abs(ys[hueco[0]] - ys[hueco[1]]) + 0.32
    zona = RoundedRectangle(corner_radius=0.08, width=ancho - 0.3, height=alto_h).move_to([0, yc, 0])
    return VGroup(hoja, pliegue, ren), zona


class VacioPorEscrito(Pieza):
    def construct(self):
        XS = [-5.3, -2.55, 0.2]
        Y = 0.6
        cabeceras = ["O-RAN TR", "Inter-RIC", "ETSI ZSM"]
        huecos = [("Sin trabajo NTN", {}), ("Identified as gap", {"slant": ITALIC}), ("Un solo objetivo", {})]
        docs, zonas, heads = VGroup(), [], VGroup()
        for k, x in enumerate(XS):
            dcm, zona = documento(semilla=k + 1)
            VGroup(dcm, zona).move_to([x, Y, 0])
            docs.add(dcm)
            zonas.append(zona)
            heads.add(et(cabeceras[k], 24, TINTA).next_to(dcm, UP, buff=0.2))
        punteados = [DashedVMobject(z, num_dashes=34).set_stroke(TENUE, 2) for z in zonas]
        self.play(LaggedStart(*[FadeIn(VGroup(d, p, h), shift=UP * 0.2)
                                for d, p, h in zip(docs, punteados, heads)], lag_ratio=0.25), run_time=1.6)
        self.respiro(0.3)

        for k, (txt, kw) in enumerate(huecos):
            d = docs[k][0]
            barrido = Line(d.get_corner(UL) + RIGHT * 0.1, d.get_corner(UR) + LEFT * 0.1, color=C_MAL,
                           stroke_width=3, stroke_opacity=0.8)
            self.add(barrido)
            self.play(barrido.animate.move_to(zonas[k].get_center()), rate_func=smooth, run_time=0.7)
            luz = zonas[k].copy().set_stroke(C_MAL, 3).set_fill(C_MAL, 0.2)
            etq = Text(txt, font=FUENTE, font_size=20, color=C_MAL, **kw)
            _vigilar(txt)
            etq.move_to(zonas[k])
            self.play(FadeOut(barrido), FadeIn(luz), FadeOut(punteados[k]), FadeIn(etq, scale=0.9), run_time=0.6)
            self.respiro(0.35)

        # UCDS v20.00: el banco de pruebas pasa a ser requisito externo
        XU = 4.35
        du, zu = documento(color=C_ANT, hueco=(5, 6), semilla=9)
        VGroup(du, zu).move_to([XU, Y, 0])
        hu = et("UCDS v20.00", 24, C_ANT).next_to(du, UP, buff=0.2)
        self.play(FadeIn(du, shift=UP * 0.2), FadeIn(hu), run_time=0.8)
        req = zu.copy().set_stroke(C_ANT, 3).set_fill(C_ANT, 0.25)
        l_req = et("Exige gemelo NTN", 20, TINTA).move_to(zu)
        self.play(FadeIn(req), FadeIn(l_req, scale=0.9), run_time=0.7)

        cb = np.array([XU, -2.4, 0])
        marco = RoundedRectangle(corner_radius=0.12, width=2.2, height=1.05).move_to(cb)
        marco_p = DashedVMobject(marco, num_dashes=36).set_stroke(TENUE, 2)
        orb = Ellipse(width=1.6, height=0.5, color=C_SAT, stroke_width=2).move_to(cb + UP * 0.12)
        sats = VGroup(*[satelite(0.1).move_to(orb.point_from_proportion(p)) for p in (0.12, 0.62)])
        gw = Triangle(color=C_ANT, fill_color=C_ANT, fill_opacity=0.5).scale(0.09).move_to(cb + DOWN * 0.3)
        banco = VGroup(orb, sats, gw)
        l_b = et("Banco de pruebas", 20, TENUE).next_to(marco, LEFT, buff=0.25)
        self.play(Create(marco_p), FadeIn(banco), FadeIn(l_b), run_time=0.8)
        fl = flecha(du.get_bottom() + DOWN * 0.05, marco.get_top() + UP * 0.05, C_ANT, 4, 0.2)
        self.play(GrowArrow(fl), run_time=0.7)
        marco_s = marco.copy().set_stroke(C_ANT, 3.5).set_fill(C_ANT, 0.1)
        self.play(ReplacementTransform(marco_p, marco_s), l_b.animate.set_color(C_ANT),
                  Flash(marco.get_top(), color=C_ANT, flash_radius=0.45), run_time=0.8)
        self.play(FadeIn(chip_tercero("Texto normativo")), run_time=0.5)
        self.respiro(1.8)
        self.cierre()


# =============================================================================
# 7. La arquitectura de agentes ya está ocupada
# =============================================================================
class ArquitecturaOcupada(Pieza):
    def construct(self):
        XC, AW, AH = -2.35, 5.4, 0.95
        YS = [-1.85, -0.7, 0.45, 1.6]
        orgs = [("IETF", "3 capas"), ("IETF", "MCP"), ("3GPP", "TR 22.870"), ("ETSI", "ZSM agente")]
        capas = VGroup()
        for (org, tag), y in zip(orgs, YS):
            base = losa(AW, AH, TENUE, 0.0).set_fill(C_PANEL, 0.9).move_to([XC, y, 0])
            l_o = et(org, 26, TINTA).move_to([XC - AW / 2 + 0.25, y, 0], aligned_edge=LEFT)
            l_t = et(tag, 20, TENUE).move_to([XC + AW / 2 - 0.25, y, 0], aligned_edge=RIGHT)
            capas.add(VGroup(base, l_o, l_t))
        # glifo de la capa IETF: agentes en tres niveles hasta el dispositivo
        g = VGroup()
        for n, dy in zip((1, 2, 4), (0.28, 0.0, -0.28)):
            for k in range(n):
                g.add(Dot([XC - 0.05 + (k - (n - 1) / 2) * 0.3, YS[0] + dy, 0], radius=0.065, color=C_ANT))
        capas[0].add(g)
        herr = VGroup(*[Square(0.2, color=C_ANT, stroke_width=2).move_to([XC - 0.5 + 0.33 * k, YS[1], 0])
                        for k in range(4)])
        capas[1].add(herr)

        for c in capas:
            c.save_state()
            c.shift(UP * 4.5).set_opacity(0)
        self.play(LaggedStart(*[Restore(c) for c in capas], lag_ratio=0.35), rate_func=smooth, run_time=3.0)
        llave = Brace(VGroup(*[c[0] for c in capas]), UP, color=TENUE, buff=0.12)
        l_oc = et("Ya ocupado", 26, TENUE).next_to(llave, UP, buff=0.12)
        self.play(GrowFromCenter(llave), FadeIn(l_oc), run_time=0.8)
        self.respiro(0.5)

        # dos ranuras vacías
        XR, RW = 4.45, 3.6
        ran_n = RoundedRectangle(corner_radius=0.1, width=RW, height=AH).move_to([XR, 1.0, 0])
        ran_v = RoundedRectangle(corner_radius=0.1, width=RW, height=AH).move_to([XR, -0.9, 0])
        p_n = DashedVMobject(ran_n, num_dashes=44).set_stroke(C_SAT, 2.5)
        p_v = DashedVMobject(ran_v, num_dashes=44).set_stroke(C_CIELO, 2.5)
        l_ntn = et("NTN:", 26, C_SAT)
        cero = simbolo("0", 26, C_SAT)
        VGroup(l_ntn, cero).arrange(RIGHT, buff=0.15).move_to(ran_n)
        l_val = et("Validación: vacío", 24, C_CIELO).move_to(ran_v)
        self.play(Create(p_n), Create(p_v), run_time=0.9)

        # barrido del borrador IETF: 0 menciones de «satellite» / «NTN»
        b0 = capas[0][0]
        barr = Line(b0.get_corner(UL) + DOWN * 0.05, b0.get_corner(DL) + UP * 0.05, color=C_SAT, stroke_width=4)
        luz = Rectangle(width=0.35, height=AH - 0.1, stroke_width=0, fill_color=C_SAT,
                        fill_opacity=0.25).move_to(barr)
        scan = VGroup(barr, luz)
        self.add(scan)
        self.play(scan.animate.shift(RIGHT * (AW - 0.1)), rate_func=smooth, run_time=1.6)
        cero_v = simbolo("0", 30, C_SAT).move_to(b0.get_right() + RIGHT * 0.35)
        self.play(FadeOut(scan), FadeIn(cero_v, scale=1.4), run_time=0.5)
        self.play(FadeIn(l_ntn), ReplacementTransform(cero_v, cero), run_time=0.9)
        self.play(FadeIn(l_val), run_time=0.6)

        # lo no cubierto: NTN y la validación del instrumento
        atenua = []
        for c in capas:
            atenua.append(c[0].animate.set_stroke(opacity=0.45).set_fill(opacity=0.45))
            atenua += [m.animate.set_opacity(0.5) for m in c[1:3]]
        atenua += [d.animate.set_opacity(0.5) for d in capas[0][3]]
        atenua += [q.animate.set_stroke(opacity=0.5) for q in capas[1][3]]
        self.play(*atenua, llave.animate.set_opacity(0.45),
                  p_n.animate.set_stroke(width=4), p_v.animate.set_stroke(width=4), run_time=0.8)
        self.play(Indicate(VGroup(l_ntn, cero), color=C_SAT, scale_factor=1.08),
                  Indicate(l_val, color=C_CIELO, scale_factor=1.08), run_time=0.9)
        self.play(FadeIn(chip_libre("IETF · 3GPP · ETSI")), run_time=0.5)
        self.respiro(1.8)
        self.cierre()

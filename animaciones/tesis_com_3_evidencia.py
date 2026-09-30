"""Comité tutorial, bloques 6–7: evidencia G2b, descriptores, negativos, mapeo F3, circularidad de F1 y F1′."""
from tesis_lib import *
import numpy as np

# Datos de G2B_RECUALIFICACION_v7.json (per_seed): (best_static, reward_mean QMIX, oracle)
G2B_V7 = {
    42: (9504.431498297055, 11056.394813330173, 12757.823030853271),
    43: (9865.560092918078, 11016.560312862099, 12975.667002487182),
    44: (9989.518851058681, 10943.052587216198, 12943.57089176178),
}
# mi_p_value por semilla (v7): canales con p ≈ 0.005 → 2, 2, 1 de 3
G2B_MI_SIGNIF = {42: 2, 43: 2, 44: 1}
# frac_oracle por semilla: QMIX (v7, compuerta) y VDN (v6, ablación del mixer, brazo 3)
FRAC_QMIX = {42: 0.8666364776021428, 43: 0.8490168798837423, 44: 0.8454430913018868}
FRAC_VDN = {42: 0.867, 43: 0.827, 44: 0.840}


def _col(a, b, t):
    return interpolate_color(ManimColor(a), ManimColor(b), t)


C_ADV = _col(C_SAT, C_MAL, 0.5)          # tono de advertencia
C_VDN = _col(C_ANT, TINTA, 0.5)          # variante de QMIX (ablación)
C_STAT = _col(TENUE, FONDO, 0.15)        # política estática


def punteado(mob, n=48, color=None, ancho=2.5, op=1.0):
    m = mob.copy().set_fill(opacity=0)
    if color is not None:
        m.set_stroke(color, width=ancho, opacity=op)
    return DashedVMobject(m, num_dashes=n)


def pip(lleno, color, r=0.13):
    return Circle(radius=r, color=color, stroke_width=2.5,
                  fill_color=color, fill_opacity=0.9 if lleno else 0)


def sello(texto, color, tam=30, ang=8):
    t = et(texto, tam, color)
    r = RoundedRectangle(corner_radius=0.08, width=t.width + 0.45, height=t.height + 0.3,
                         color=color, stroke_width=4, fill_color=FONDO, fill_opacity=0.9)
    t.move_to(r)
    return VGroup(r, t).rotate(ang * DEGREES)


def muestra(color, texto, tam=20, op=0.85):
    s = Square(0.26, color=color, fill_color=color, fill_opacity=op, stroke_width=2)
    return VGroup(s, et(texto, tam, TINTA)).arrange(RIGHT, buff=0.14)


# =============================================================================
# 1. G2b en tres semillas
# =============================================================================
class G2bTresSemillas(Pieza):
    def construct(self):
        self.add(chip_desarrollo())
        y0, k = -2.05, 3.95 / 13000
        xs = {42: -4.6, 43: -1.3, 44: 2.0}
        dx, w = 0.8, 0.66

        base = Line([-6.4, y0, 0], [3.3, y0, 0], color=C_EJE, stroke_width=3)
        leg = VGroup(muestra(C_STAT, "best_static"), muestra(C_ANT, "QMIX"),
                     muestra(C_CIELO, "Oráculo", op=0.3)).arrange(RIGHT, buff=0.7)
        leg.move_to([-1.55, 3.3, 0])
        cota = et("cota inferior", 18, TENUE).next_to(leg[2], DOWN, buff=0.1).align_to(leg[2][1], LEFT)
        self.play(FadeIn(leg, shift=DOWN * 0.2), Create(base), run_time=0.9)
        self.play(FadeIn(cota), run_time=0.4)

        l_sem = et("Semilla", 20, TENUE).move_to([-6.2, y0 - 0.38, 0])
        barras, gan, lineas, fantasmas = {}, [], [], []
        for s, (st, q, o) in G2B_V7.items():
            x = xs[s]
            b_st = barra(x - dx, y0, st * k, w, C_STAT, 0.85)
            b_q = barra(x, y0, q * k, w, C_ANT, 0.85)
            b_o = barra(x + dx, y0, o * k, w, C_CIELO, 0.3)
            barras[s] = (b_st, b_q, b_o)
            lab = et(str(s), 26, TINTA).move_to([x, y0 - 0.38, 0])
            anims = [GrowFromEdge(b, DOWN) for b in (b_st, b_q, b_o)]
            extra = [FadeIn(lab)] + ([FadeIn(l_sem)] if s == 42 else [])
            self.play(LaggedStart(*anims, lag_ratio=0.3), *extra, run_time=1.3)
            # ganancia sobre best_static (tramo verde del QMIX)
            h = (q - st) * k
            g = Rectangle(width=w, height=h, stroke_width=0, fill_color=C_OK, fill_opacity=0.9)
            g.move_to([x, y0 + st * k + h / 2, 0])
            gan.append(g)
            lineas.append(DashedLine([x - dx - w / 2, y0 + st * k, 0], [x + w / 2, y0 + st * k, 0],
                                     color=TINTA, stroke_width=2, dash_length=0.08))
            f = punteado(Rectangle(width=w, height=o * k), 26, C_CIELO, 2.5)
            f.move_to([x, y0 + o * k / 2, 0])
            fantasmas.append(f)
        self.respiro(0.4)

        self.play(LaggedStart(*[Create(l) for l in lineas], lag_ratio=0.2), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(g) for g in gan], lag_ratio=0.2), run_time=1.0)
        etiquetas = VGroup()
        for s, txt in ((42, "+16.3 %"), (43, None), (44, "+9.5 %")):
            ok = marca_ok(ORIGIN, 0.26)
            it = VGroup(ok, et(txt, 24, C_OK)).arrange(RIGHT, buff=0.12) if txt else VGroup(ok)
            it.move_to([xs[s], y0 - 0.9, 0])
            etiquetas.add(it)
        self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.15) for e in etiquetas], lag_ratio=0.25), run_time=1.0)

        t33 = et("3/3", 46, C_OK)
        s33 = et("QMIX > best_static", 20, TENUE)
        g33 = VGroup(t33, s33).arrange(DOWN, buff=0.1).move_to([5.3, 1.55, 0])
        self.play(FadeIn(g33, shift=LEFT * 0.2), run_time=0.8)
        self.respiro(0.6)

        # el oráculo se superpone al QMIX: 84–87 % de una política con información privilegiada
        self.play(LaggedStart(*[TransformFromCopy(barras[s][2], f) for s, f in zip(G2B_V7, fantasmas)],
                              lag_ratio=0.2), run_time=1.6)
        t84 = et("84–87 %", 46, C_CIELO)
        s84 = et("del oráculo", 20, TENUE)
        g84 = VGroup(t84, s84).arrange(DOWN, buff=0.1).move_to([5.3, -0.25, 0])
        self.play(FadeIn(g84, shift=LEFT * 0.2), run_time=0.8)
        self.respiro(2.4)
        self.cierre()


# =============================================================================
# 2. Descriptores, no compuertas
# =============================================================================
class DescriptoresNoCompuertas(Pieza):
    def construct(self):
        self.add(chip_desarrollo())
        yp = -0.3
        z_c = Rectangle(width=3.3, height=5.9, color=TINTA, stroke_width=3).move_to([-3.75, 0.62, 0])
        z_d = punteado(Rectangle(width=8.2, height=5.9), 70, TENUE, 2.5).move_to([2.55, 0.62, 0])
        l_c = et("Compuerta", 28, TINTA).move_to([-3.75, 3.2, 0])
        l_d = et("Descriptor", 28, TENUE).move_to([2.55, 3.2, 0])
        via = Arrow([-6.7, yp, 0], [6.65, yp, 0], buff=0, color=C_EJE, stroke_width=5,
                    max_tip_length_to_length_ratio=0.03, tip_length=0.25)
        self.play(Create(z_c), FadeIn(l_c), run_time=0.8)
        self.play(Create(z_d), FadeIn(l_d), run_time=0.8)
        self.play(GrowArrow(via), run_time=0.7)

        # la compuerta c1: una barrera que corta la vía
        gx = -3.6
        pivote = [gx, yp - 1.0, 0]
        brazo = Line(pivote, [gx, yp + 1.0, 0], color=C_SAT, stroke_width=12)
        eje = Dot(pivote, radius=0.11, color=TINTA)
        l_c1 = VGroup(et("c1", 34, TINTA), et("reward > best_static", 20, TENUE)).arrange(DOWN, buff=0.1)
        l_c1.move_to([-3.75, 2.2, 0])
        self.play(Create(brazo), FadeIn(eje), FadeIn(l_c1), run_time=0.7)

        ficha = VGroup(Circle(radius=0.3, color=C_ANT, fill_color=C_ANT, fill_opacity=0.35, stroke_width=3),
                       et("G2b", 18, TINTA)).move_to([-6.2, yp, 0])
        self.play(FadeIn(ficha, scale=0.6), run_time=0.4)
        self.play(ficha.animate.move_to([gx - 0.55, yp, 0]), run_time=0.9, rate_func=smooth)

        ticks = VGroup(*[marca_ok(ORIGIN, 0.24) for _ in range(3)]).arrange(RIGHT, buff=0.18)
        t33 = VGroup(ticks, et("3/3", 24, C_OK)).arrange(RIGHT, buff=0.2).move_to([-3.75, yp - 1.6, 0])
        self.play(LaggedStart(*[Create(t) for t in ticks], lag_ratio=0.35), run_time=0.8)
        self.play(FadeIn(t33[1]), brazo.animate.set_color(C_OK), run_time=0.4)
        self.play(Rotate(brazo, PI / 2, about_point=np.array(pivote)), run_time=0.7)
        self.play(ficha.animate.move_to([-0.1, yp, 0]), run_time=1.0, rate_func=smooth)

        # descriptores: se leen sin tocar la vía
        def panel(x0, x1):
            return RoundedRectangle(corner_radius=0.12, width=x1 - x0, height=2.3, color=TENUE,
                                    stroke_width=2, fill_color=C_PANEL, fill_opacity=0.35).move_to([(x0 + x1) / 2, 1.75, 0])

        p2, p3 = panel(-1.35, 1.35), panel(1.75, 6.35)
        sonda2 = DashedLine(p2.get_bottom(), [0, yp + 0.35, 0], color=TENUE, stroke_width=2, dash_length=0.07)
        sonda3 = DashedLine(p3.get_bottom(), [4.05, yp + 0.35, 0], color=TENUE, stroke_width=2, dash_length=0.07)

        h2 = et("c2 modal", 22, TINTA).move_to([0, 2.62, 0])
        filas2 = VGroup()
        for i, s in enumerate((42, 43, 44)):
            filas2.add(VGroup(et(str(s), 20, TENUE), marca_no(ORIGIN, 0.2)).arrange(DOWN, buff=0.14))
        filas2.arrange(RIGHT, buff=0.42).move_to([0, 1.72, 0])
        f2 = et("No se cumple", 20, C_MAL).move_to([0, 0.86, 0])
        self.play(Create(p2), Create(sonda2), run_time=0.6)
        self.play(FadeIn(h2), LaggedStart(*[FadeIn(f) for f in filas2], lag_ratio=0.2), run_time=0.8)
        self.play(FadeIn(f2), run_time=0.4)
        self.play(ficha.animate.move_to([4.05, yp, 0]), run_time=1.0, rate_func=smooth)

        h3 = VGroup(et("c3 MI", 22, TINTA), et("p ≈ 0.005", 20, TENUE)).arrange(RIGHT, buff=0.35).move_to([4.05, 2.62, 0])
        filas3, pips = VGroup(), []
        for j, s in enumerate((42, 43, 44)):
            n = G2B_MI_SIGNIF[s]
            ps = VGroup(*[pip(False, C_OK) for _ in range(3)]).arrange(RIGHT, buff=0.14)
            fila = VGroup(et(str(s), 20, TENUE), ps, et(f"{n} de 3", 22, TINTA)).arrange(RIGHT, buff=0.35)
            fila.move_to([4.05, 2.17 - 0.38 * j, 0])
            filas3.add(fila)
            pips.append((ps, n))
        f3 = et("No se cumple", 20, C_MAL).move_to([4.05, 0.86, 0])
        self.play(Create(p3), Create(sonda3), FadeIn(h3), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(VGroup(f[0], f[1])) for f in filas3], lag_ratio=0.15), run_time=0.6)
        llenar = []
        for ps, n in pips:
            llenar += [ps[i].animate.set_fill(C_OK, opacity=0.9) for i in range(n)]
        self.play(LaggedStart(*llenar, lag_ratio=0.15),
                  LaggedStart(*[FadeIn(f[2]) for f in filas3], lag_ratio=0.3), run_time=1.3)
        self.play(FadeIn(f3), run_time=0.4)

        # la ficha sigue: los descriptores no bloquean
        nb = et("Reportado, no bloquea", 24, TENUE).move_to([2.55, yp - 1.1, 0])
        self.play(ficha.animate.move_to([6.0, yp, 0]), FadeIn(nb, shift=UP * 0.15), run_time=1.1, rate_func=smooth)
        self.respiro(2.6)
        self.cierre()


# =============================================================================
# 3. Negativos como producto
# =============================================================================
class NegativosComoProducto(Pieza):
    def construct(self):
        self.add(chip_desarrollo())
        pa = RoundedRectangle(corner_radius=0.15, width=6.45, height=6.3, color=C_EJE, stroke_width=2,
                              fill_color=C_PANEL, fill_opacity=0.25).move_to([-3.5, 0.3, 0])
        pb = pa.copy().move_to([3.5, 0.3, 0])
        self.play(FadeIn(pa), FadeIn(pb), run_time=0.6)

        # ---------- (a) ablación del mixer: QMIX vs VDN, fracción del oráculo ----------
        y0, H = -1.25, 3.2
        orac = DashedLine([-6.35, y0 + H, 0], [-0.75, y0 + H, 0], color=C_CIELO, stroke_width=2.5, dash_length=0.12)
        l_or = et("Oráculo", 18, C_CIELO).next_to(orac, UP, buff=0.06).align_to(orac, RIGHT)
        base = Line([-6.35, y0, 0], [-0.75, y0, 0], color=C_EJE, stroke_width=3)
        self.play(Create(base), Create(orac), FadeIn(l_or), run_time=0.8)
        xs = {42: -5.0, 43: -3.5, 44: -2.0}
        bq, bv, labs = [], [], []
        for s in (42, 43, 44):
            bq.append(barra(xs[s] - 0.29, y0, FRAC_QMIX[s] * H, 0.52, C_ANT, 0.85))
            bv.append(barra(xs[s] + 0.29, y0, FRAC_VDN[s] * H, 0.52, C_VDN, 0.85))
            labs.append(et(str(s), 22, TINTA).move_to([xs[s], y0 - 0.33, 0]))
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bq], lag_ratio=0.15),
                  *[FadeIn(l) for l in labs], run_time=1.0)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bv], lag_ratio=0.15), run_time=1.0)

        fila = VGroup(et("c2 modal", 20, TENUE),
                      VGroup(muestra(C_ANT, "QMIX"), marca_no(ORIGIN, 0.2)).arrange(RIGHT, buff=0.18),
                      VGroup(muestra(C_VDN, "VDN"), marca_no(ORIGIN, 0.2)).arrange(RIGHT, buff=0.18))
        fila.arrange(RIGHT, buff=0.45).move_to([-3.5, y0 - 1.0, 0])
        self.play(FadeIn(fila, shift=UP * 0.15), run_time=0.8)

        def insignia(txt, col):
            t = et(txt, 20, col)
            r = RoundedRectangle(corner_radius=0.1, width=t.width + 0.35, height=t.height + 0.22, color=col,
                                 stroke_width=2, fill_color=col, fill_opacity=0.1)
            return VGroup(r, t.move_to(r))

        i_n = insignia("n = 3", TINTA)
        i_p = insignia("Sin potencia", TENUE)
        ins = VGroup(i_n, i_p).arrange(RIGHT, buff=0.2).move_to([-5.0, 2.9, 0]).align_to(pa, LEFT).shift(RIGHT * 0.3)
        self.play(FadeIn(ins, shift=DOWN * 0.15), run_time=0.6)
        s_d = sello("Diagnóstico", C_SAT, 26, 6).move_to([-1.9, 2.92, 0])
        self.play(FadeIn(s_d, scale=1.4), run_time=0.5)
        self.respiro(0.8)

        # ---------- (b) banco mock: sube demasiado y el protocolo lo anula ----------
        ax = Axes(x_range=[0, 1, 1], y_range=[0, 1, 1], x_length=5.2, y_length=4.4, tips=False,
                  axis_config={"color": C_EJE, "stroke_width": 2.5, "include_ticks": False}).move_to([3.55, 0.35, 0])
        r5 = DashedLine(ax.c2p(0, 0.42), ax.c2p(1, 0.42), color=C_OK, stroke_width=3, dash_length=0.13)
        l_r5 = et("Test R5", 20, C_OK).next_to(r5, DOWN, buff=0.08).align_to(r5, RIGHT)
        self.play(Create(ax), run_time=0.7)
        self.play(Create(r5), FadeIn(l_r5), run_time=0.6)

        xx = np.linspace(0, 1, 90)
        y_real = 0.05 + 0.28 * (1 - np.exp(-xx / 0.25))
        y_mock = 0.05 + 0.9 * suave(xx / 0.95) ** 1.3
        def curva(ys, col, anc):
            p = np.array([ax.c2p(a, b) for a, b in zip(xx, ys)])
            return trazo(p[:, 0], p[:, 1], col, anc)

        real = curva(y_real, C_ANT, 4)
        mock = curva(y_mock, C_SAT, 5)
        l_real = et("NTNEnv-v2", 20, C_ANT).next_to(ax.c2p(1, y_real[-1]), DOWN, buff=0.12).align_to(real, RIGHT)
        l_mock = et("Banco mock", 22, C_SAT).next_to(ax.c2p(0.62, 0.86), LEFT, buff=0.1)
        self.play(Create(real), FadeIn(l_real), run_time=1.1)
        self.play(Create(mock, rate_func=lambda t: t ** 1.4), run_time=1.8)
        self.play(FadeIn(l_mock, shift=RIGHT * 0.1), run_time=0.4)
        ic = int(np.argmax(y_mock > 0.42))
        pc = ax.c2p(xx[ic], 0.42)
        self.play(Flash(pc, color=C_MAL, flash_radius=0.35, line_length=0.2), run_time=0.6)
        self.play(mock.animate.set_stroke(C_MAL, opacity=0.4), l_mock.animate.set_color(C_MAL).set_opacity(0.6),
                  run_time=0.5)
        s_a = sello("Anulado", C_MAL, 36, -10).move_to(ax.c2p(0.66, 0.66))
        self.play(FadeIn(s_a, scale=1.6), run_time=0.45)
        esq = et("Curva esquemática", 18, TENUE).next_to(ax.x_axis, DOWN, buff=0.18)
        self.play(FadeIn(esq), run_time=0.4)
        self.respiro(2.6)
        self.cierre()


# =============================================================================
# 4. Puntos de extensión (F3 no se dispara)
# =============================================================================
class PuntosDeExtension(Pieza):
    def construct(self):
        self.add(chip_desarrollo(), chip_tercero("3GPP · O-RAN"))
        ys = [1.75, 0.55, -0.65, -1.85]
        mods = ["Percepción", "Análisis", "Decisión", "Acción"]
        g3 = ["TS 28.552", "TS 28.104", "TS 28.100", "TS 28.531"]      # COMPATIBILIDAD_PROTOCOLAR §2
        orn = ["E2 · REPORT", "Y1", "A1 · R1", "E2 · CONTROL"]          # §3.2 / §3.3
        pend = ["Leer texto normativo", "MDA ↔ NWDAF", "Interfaz inter-RIC", "Leer TR RIC4NTN"]  # §5, §8, §2.2, §3.4e
        xp, x3, xo = -2.4, -5.35, 0.75

        bloques = [caja(m, 2.3, 0.78, C_ANT, 22) for m in mods]
        for b, y in zip(bloques, ys):
            b.move_to([xp, y, 0])
        flechas = [flecha(bloques[i].get_bottom(), bloques[i + 1].get_top(), C_ANT, 3, 0.14) for i in range(3)]
        h_p = et("PADA", 24, C_ANT).move_to([xp, 2.62, 0])
        self.play(FadeIn(h_p), LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2) for b in bloques], lag_ratio=0.2),
                  run_time=1.2)
        self.play(*[GrowArrow(f) for f in flechas], run_time=0.6)

        def ancla(txt, x, y):
            t = et(txt, 20, TINTA)
            r = RoundedRectangle(corner_radius=0.1, width=2.1, height=0.56, color=C_CIELO, stroke_width=2,
                                 fill_color=C_CIELO, fill_opacity=0.12)
            return VGroup(r, t).move_to([x, y, 0])

        a3 = [ancla(t, x3, y) for t, y in zip(g3, ys)]
        ao = [ancla(t, xo, y) for t, y in zip(orn, ys)]
        h3 = et("3GPP SA5", 22, C_CIELO).move_to([x3, 2.62, 0])
        ho = et("O-RAN", 22, C_CIELO).move_to([xo, 2.62, 0])
        l3 = [Line(b.get_left(), a.get_right(), color=TENUE, stroke_width=2.5) for b, a in zip(bloques, a3)]
        lo = [Line(b.get_right(), a.get_left(), color=TENUE, stroke_width=2.5) for b, a in zip(bloques, ao)]
        self.play(FadeIn(h3), LaggedStart(*[AnimationGroup(Create(l), FadeIn(a, shift=LEFT * 0.15))
                                            for l, a in zip(l3, a3)], lag_ratio=0.25), run_time=1.8)
        self.play(FadeIn(ho), LaggedStart(*[AnimationGroup(Create(l), FadeIn(a, shift=RIGHT * 0.15))
                                            for l, a in zip(lo, ao)], lag_ratio=0.25), run_time=1.8)

        izq, der = a3[0].get_left()[0], ao[0].get_right()[0]
        cor = VGroup(Line([izq, 3.0, 0], [der, 3.0, 0]), Line([izq, 3.0, 0], [izq, 2.88, 0]),
                     Line([der, 3.0, 0], [der, 2.88, 0])).set_stroke(TINTA, 2)
        l_map = et("Mapeo documentado", 26, TINTA).next_to(cor, UP, buff=0.1)
        self.play(Create(cor), FadeIn(l_map, shift=DOWN * 0.1), run_time=0.9)
        self.respiro(0.6)

        # sección punteada: lo que el propio documento declara pendiente o sin interfaz
        caja_p = punteado(RoundedRectangle(corner_radius=0.15, width=4.05, height=5.95), 80, TENUE, 2.5)
        caja_p.move_to([4.6, 0.55, 0])
        l_pen = et("Verificaciones pendientes", 24, TENUE).move_to([4.6, 3.1, 0])
        self.play(Create(caja_p), FadeIn(l_pen), run_time=1.0)
        items = []
        for t, y in zip(pend, ys):
            bul = Circle(radius=0.1, color=TENUE, stroke_width=2.5)
            it = VGroup(bul, et(t, 20, TINTA)).arrange(RIGHT, buff=0.16)
            it.move_to([4.75, y, 0]).align_to(caja_p, LEFT).shift(RIGHT * 0.3)
            items.append(it)
        # dos huecos sin interfaz normalizada salen punteados de su fila
        h1 = DashedLine(ao[1].get_right(), items[1][0].get_left(), color=TENUE, stroke_width=2, dash_length=0.08)
        h2 = DashedLine(ao[2].get_right(), items[2][0].get_left(), color=TENUE, stroke_width=2, dash_length=0.08)
        self.play(LaggedStart(*[FadeIn(i, shift=LEFT * 0.15) for i in items], lag_ratio=0.25), run_time=1.4)
        self.play(Create(h1), Create(h2), run_time=0.8)

        f3 = VGroup(et("F3:", 24, TINTA), et("no dispara", 24, TENUE)).arrange(RIGHT, buff=0.15).move_to([xp, -2.85, 0])
        self.play(FadeIn(f3, shift=UP * 0.1), run_time=0.6)
        self.respiro(3.4)
        self.cierre()


# =============================================================================
# 5. Circularidad de F1
# =============================================================================
class CircularidadDeF1(Pieza):
    def construct(self):
        self.add(chip_desarrollo(), chip("Propuesto", C_CIELO, esquina=DL))
        c = np.array([-2.9, 0.15, 0])
        R = 2.2

        def nodo_(txt, pos, ancho=2.3):
            return caja(txt, ancho, 0.72, C_ANT, 22).move_to(pos)

        n_c = nodo_("Yo construyo", c + UP * R)
        n_u = nodo_("Umbral 0.25", c + RIGHT * R, 2.15)
        n_m = nodo_("Yo mido", c + DOWN * R)
        n_p = nodo_("Pasa", c + LEFT * R, 1.5)
        ok = marca_ok(ORIGIN, 0.24).next_to(n_p[1], RIGHT, buff=0.12)
        n_p[1].shift(LEFT * 0.18)
        ok.next_to(n_p[1], RIGHT, buff=0.12)
        nodos = [n_c, n_u, n_m, n_p]

        def arco(a, b):
            m = ArcBetweenPoints(a, b, angle=-PI / 2.6).set_stroke(TENUE, 3.5)
            m.add_tip(tip_length=0.18)
            return m

        arcos = [arco(n_c.get_right() + RIGHT * 0.05, n_u.get_top() + UP * 0.06),
                 arco(n_u.get_bottom() + DOWN * 0.06, n_m.get_right() + RIGHT * 0.05),
                 arco(n_m.get_left() + LEFT * 0.05, n_p.get_bottom() + DOWN * 0.06),
                 arco(n_p.get_top() + UP * 0.06, n_c.get_left() + LEFT * 0.05)]
        for n in nodos:
            self.play(FadeIn(n, scale=0.9), run_time=0.35)
        self.play(FadeIn(ok), LaggedStart(*[Create(a) for a in arcos], lag_ratio=0.25), run_time=1.4)

        # el circuito se recorre dos veces
        fic = Dot(radius=0.1, color=C_SAT).move_to(arcos[0].get_start())
        self.add(fic)
        for vuelta in range(2):
            for i, a in enumerate(arcos):
                camino = VMobject().set_points(a.get_all_points()[: len(a.points)])
                self.play(MoveAlongPath(fic, camino), Indicate(nodos[(i + 1) % 4][0], color=C_SAT, scale_factor=1.04),
                          run_time=0.55 if vuelta == 0 else 0.45, rate_func=linear)
        self.play(FadeOut(fic), run_time=0.2)

        # advertencia: calibración, no falsación
        adv = [a.animate.set_color(C_ADV).set_stroke(width=4.5) for a in arcos]
        adv += [n[0].animate.set_stroke(C_ADV).set_fill(C_ADV, 0.14) for n in nodos]
        cal = et("Calibración", 27, C_ADV).move_to(c + UP * 0.22 + LEFT * 0.1)
        nof = et("No falsación", 23, C_ADV).move_to(c + DOWN * 0.28 + LEFT * 0.1)
        self.play(*adv, FadeIn(cal), FadeIn(nof), run_time=1.1)
        self.respiro(1.2)

        # ruptura: el umbral queda intacto; lo demás se vuelve tenue
        a0 = arcos[0]
        cuerpo = VMobject().set_points(a0.points.copy()).set_stroke(C_ADV, 4.5).set_fill(opacity=0)
        mitad1 = cuerpo.copy().pointwise_become_partial(cuerpo, 0, 0.42)
        mitad2 = VGroup(cuerpo.copy().pointwise_become_partial(cuerpo, 0.58, 1), a0.tip.copy())
        self.remove(a0)
        self.add(mitad1, mitad2)

        def tenue_(m):
            return m.animate.set_stroke(opacity=0.25).set_fill(opacity=0.25).set_fill(opacity=0, family=False)

        self.play(mitad1.animate.shift(LEFT * 0.25 + UP * 0.25).set_stroke(opacity=0.25),
                  mitad2.animate.shift(RIGHT * 0.25 + DOWN * 0.1).set_stroke(opacity=0.25).set_fill(opacity=0.25),
                  *[tenue_(a) for a in arcos[1:]],
                  *[n[0].animate.set_fill(opacity=0.04).set_stroke(opacity=0.3) for n in (n_c, n_m, n_p)],
                  *[n[1].animate.set_opacity(0.35) for n in (n_c, n_m, n_p)], ok.animate.set_opacity(0.3),
                  cal.animate.set_opacity(0.45), nof.animate.set_opacity(0.45),
                  n_u[0].animate.set_stroke(C_ANT).set_fill(C_ANT, 0.2), run_time=1.1)

        # pieza externa, fuera del círculo
        emu_c = np.array([4.45, 1.45, 0])
        emu = punteado(RoundedRectangle(corner_radius=0.15, width=4.1, height=2.75), 64, C_CIELO, 2.5).move_to(emu_c)
        l_emu = et("Emulador externo", 26, C_CIELO).move_to(emu_c + UP * 0.95)
        # íconos: órbita real · enlace inter-satelital · latencias medidas
        orb = VGroup(Ellipse(width=0.8, height=0.4, color=C_SAT, stroke_width=2),
                     Dot(radius=0.06, color=C_SAT).move_to([0.4, 0, 0]))
        isl = VGroup(satelite(0.12), satelite(0.12)).arrange(RIGHT, buff=0.35)
        isl.add(DashedLine(isl[0].get_right(), isl[1].get_left(), color=C_ANT, stroke_width=2, dash_length=0.05))
        lat = VGroup(*[Line(ORIGIN, UP * h, color=C_ANT, stroke_width=4) for h in (0.22, 0.34, 0.27, 0.4)]).arrange(
            RIGHT, buff=0.1, aligned_edge=DOWN)
        filas = VGroup()
        for ic, txt in ((orb, "Órbitas reales"), (isl, "ISL"), (lat, "Latencias medidas")):
            ic_ = VGroup(ic).scale_to_fit_width(0.8) if ic.width > 0.8 else VGroup(ic)
            f = VGroup(ic_, et(txt, 20, TINTA)).arrange(RIGHT, buff=0.25)
            filas.add(f)
        filas.arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to(emu_c + DOWN * 0.3)
        for f in filas:
            f[0].move_to([emu_c[0] - 1.35, f.get_center()[1], 0])
            f[1].next_to(f[0], RIGHT, buff=0.25).align_to(emu_c + LEFT * 0.85, LEFT)
        self.play(FadeIn(VGroup(emu, l_emu), shift=LEFT * 0.6), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(f, shift=LEFT * 0.15) for f in filas], lag_ratio=0.3), run_time=1.2)

        f1 = VGroup(RoundedRectangle(corner_radius=0.14, width=2.3, height=1.05, color=C_OK, stroke_width=3,
                                     fill_color=C_OK, fill_opacity=0.14),
                    VGroup(et("F1′", 30, C_OK), et("MA′ ≥ 0.25", 20, TINTA)).arrange(DOWN, buff=0.08))
        f1[1].move_to(f1[0])
        f1.move_to([4.45, -1.75, 0])
        a_e = flecha(emu.get_bottom(), f1.get_top(), C_CIELO, 3.5, 0.18)
        a_u = flecha(n_u.get_right() + DOWN * 0.1, f1.get_left() + UP * 0.1, C_ANT, 3.5, 0.18)
        l_int = et("Intacto", 20, C_ANT).next_to(a_u.get_center(), DOWN, buff=0.12).shift(LEFT * 0.2)
        self.play(GrowArrow(a_e), GrowArrow(a_u), FadeIn(l_int), run_time=0.9)
        self.play(FadeIn(f1, scale=0.85), run_time=0.7)
        self.respiro(2.4)
        self.cierre()


# =============================================================================
# 6. Margen vs fidelidad (experimento pre-registrado F1′)
# =============================================================================
class MargenVsFidelidad(Pieza):
    def construct(self):
        self.add(chip_ilustrativo(), chip("Propuesto", C_CIELO, esquina=DL), chip_desarrollo(esquina=UR))
        XM, YM = 1.35, 0.4
        ax = Axes(x_range=[0, XM, 1], y_range=[0, YM, 0.1], x_length=8.6, y_length=4.8, tips=False,
                  axis_config={"color": C_EJE, "stroke_width": 2.5, "include_ticks": False})
        ax.shift(np.array([-4.4, -2.1, 0]) - ax.c2p(0, 0))
        l_x = et("Fidelidad", 22, TENUE).move_to([ax.c2p(0.62, 0)[0], -2.5, 0])
        l_y = et("Margen", 22, TENUE).next_to(ax.c2p(0, YM), UP, buff=0.15)
        self.play(Create(ax), FadeIn(l_x), FadeIn(l_y), run_time=1.0)

        x3 = ax.c2p(1, 0)[0]
        v3l = DashedLine(ax.c2p(1, 0), ax.c2p(1, YM), color=TENUE, stroke_width=2, dash_length=0.1)
        t2 = VGroup(et("v2", 24, TINTA), et("mínimo", 18, TENUE)).arrange(DOWN, buff=0.04)
        t2.next_to(ax.c2p(0, 0), DOWN, buff=0.12)
        t3 = VGroup(et("v3", 24, TINTA), et("emulador", 18, TENUE)).arrange(DOWN, buff=0.04)
        t3.move_to([x3, t2.get_center()[1], 0])
        mas = Rectangle(width=ax.c2p(XM, 0)[0] - x3, height=4.8, stroke_width=0, fill_color=C_PANEL,
                        fill_opacity=0.35).move_to([(ax.c2p(XM, 0)[0] + x3) / 2, ax.c2p(0, YM / 2)[1], 0])
        self.play(FadeIn(t2), FadeIn(t3), Create(v3l), FadeIn(mas), run_time=0.9)

        umb = DashedLine(ax.c2p(0, 0.25), ax.c2p(XM, 0.25), color=C_CIELO, stroke_width=3.5, dash_length=0.15)
        l_umb = et("Umbral 0.25", 22, C_CIELO).next_to(ax.c2p(0, 0.25), LEFT, buff=0.15)
        self.play(Create(umb), FadeIn(l_umb), run_time=0.9)
        p0 = Dot(ax.c2p(0, 0.318), radius=0.1, color=C_ANT)
        l0 = et("0.318", 22, C_ANT).next_to(ax.c2p(0, 0.318), LEFT, buff=0.15)
        self.play(FadeIn(p0, scale=0.5), FadeIn(l0), run_time=0.6)
        self.respiro(0.4)

        # tres trayectorias posibles (ilustrativas), ninguna elegida
        xx = np.linspace(0, XM, 120)
        fA = lambda x: 0.318 - 0.012 * x - 0.004 * np.sin(4 * x)
        fB = lambda x: 0.318 - 0.045 * x - 0.012 * x ** 2
        fC = lambda x: 0.318 - 0.12 * x - 0.03 * x ** 2
        curvas = []
        for f in (fA, fB, fC):
            pts = np.array([ax.c2p(a, f(a)) for a in xx])
            m = VMobject().set_points_smoothly(pts)
            m.set_stroke(TENUE, 3.5, opacity=0.9)
            curvas.append(DashedVMobject(m, num_dashes=46))
        cursor = DashedLine(ax.c2p(0, 0), ax.c2p(0, YM), color=C_SAT, stroke_width=2.5, dash_length=0.08)
        T = ValueTracker(0)
        cursor.add_updater(lambda m: m.put_start_and_end_on(ax.c2p(T.get_value(), 0), ax.c2p(T.get_value(), YM)))
        self.add(cursor)
        self.play(T.animate.set_value(XM), *[Create(cv) for cv in curvas], run_time=3.6, rate_func=linear)
        cursor.clear_updaters()
        self.play(FadeOut(cursor), run_time=0.3)

        lA = et("Sobrevive", 20, TINTA).next_to(ax.c2p(XM, fA(XM)), RIGHT, buff=0.15)
        lB = et("Cruza más allá", 20, TINTA).next_to(ax.c2p(XM, fB(XM)), RIGHT, buff=0.15)
        self.play(FadeIn(lA, shift=LEFT * 0.1), run_time=0.6)
        xB = xx[np.argmax(fB(xx) < 0.25)]
        self.play(FadeIn(lB, shift=LEFT * 0.1), Flash(ax.c2p(xB, 0.25), color=TENUE, flash_radius=0.25,
                                                       line_length=0.12), run_time=0.8)

        xC = xx[np.argmax(fC(xx) < 0.25)]
        pc = ax.c2p(xC, 0.25)
        mk = Circle(radius=0.14, color=C_SAT, stroke_width=4).move_to(pc)
        l_f1 = et("F1′ se dispara", 24, C_SAT)
        l_rd = et("Resultado doctoral", 22, TINTA)
        g_f = VGroup(l_f1, l_rd).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        g_f.move_to(ax.c2p(0.22, 0.135))
        guia = Line(pc + DL * 0.1, g_f.get_top() + UP * 0.06 + RIGHT * 0.4, color=C_SAT, stroke_width=2)
        self.play(Create(mk), Flash(pc, color=C_SAT, flash_radius=0.35, line_length=0.18), run_time=0.7)
        self.play(Create(guia), FadeIn(l_f1, shift=UP * 0.1), run_time=0.7)
        self.play(FadeIn(l_rd, shift=UP * 0.1), run_time=0.6)
        self.respiro(2.8)
        self.cierre()

"""IA en satélites y gobernanza autónoma (Co.De Aerospace): 10 piezas."""
from code_lib import *

RNG_BASE = 20260928


def poli(*pts):
    m = VMobject()
    m.set_points_as_corners([np.array([p[0], p[1], 0.0]) for p in pts])
    return m


def cmap(v):
    """Embedding escalar 0..1 -> color (cian -> violeta -> ámbar)."""
    g = color_gradient([C_ANT, C_CIELO, C_SAT], 101)
    return g[int(np.clip(v, 0, 1) * 100)]


def visto(color=None, s=0.2, ancho=5):
    c = color or C_OK
    return VGroup(Line([-s, 0, 0], [-s * 0.3, -s * 0.8, 0], color=c, stroke_width=ancho),
                  Line([-s * 0.3, -s * 0.8, 0], [s * 1.1, s * 0.9, 0], color=c, stroke_width=ancho))


def cruz(color=None, s=0.18, ancho=5):
    c = color or C_MAL
    return VGroup(Line([-s, -s, 0], [s, s, 0], color=c, stroke_width=ancho),
                  Line([-s, s, 0], [s, -s, 0], color=c, stroke_width=ancho))


# =============================================================================
# 1. Red neuronal
# =============================================================================
class RedNeuronalPropaga(Pieza):
    def construct(self):
        rng = np.random.default_rng(RNG_BASE + 1)
        sizes = [4, 6, 6, 3]
        xs = [-4.8, -1.6, 1.6, 4.8]
        capas = []
        for x, n in zip(xs, sizes):
            ys = np.linspace((n - 1) / 2, -(n - 1) / 2, n) * 0.95
            capas.append([Circle(radius=0.24, color=C_ANT, fill_color=C_ANT,
                                 fill_opacity=0.15, stroke_width=2.5).move_to([x, y, 0]) for y in ys])
        W = [rng.normal(0, 1, (sizes[i], sizes[i + 1])) for i in range(3)]
        aristas = []
        for l in range(3):
            wmax = np.abs(W[l]).max()
            g = {}
            for i, a in enumerate(capas[l]):
                for j, b in enumerate(capas[l + 1]):
                    w = W[l][i, j]
                    k = abs(w) / wmax
                    g[(i, j)] = Line(a.get_center(), b.get_center(),
                                     color=C_CIELO if w < 0 else C_ANT,
                                     stroke_width=0.5 + 3.6 * k, stroke_opacity=0.08 + 0.55 * k)
            aristas.append(g)

        for l in range(3):
            self.play(LaggedStart(*[FadeIn(n, scale=0.6) for n in capas[l]], lag_ratio=0.1),
                      run_time=0.6)
            self.play(LaggedStart(*[Create(e) for e in aristas[l].values()], lag_ratio=0.01),
                      run_time=0.9)
        self.play(LaggedStart(*[FadeIn(n, scale=0.6) for n in capas[3]], lag_ratio=0.1), run_time=0.6)
        for l in range(3):
            for e in aristas[l].values():
                e.set_z_index(0)
        for c in capas:
            for n in c:
                n.set_z_index(2)
        self.respiro(0.4)

        entradas = [np.array([0.9, 0.1, 0.8, 0.2]), np.array([0.1, 0.9, 0.2, 0.9]),
                    np.array([0.8, 0.8, 0.1, 0.3])]

        def sig(z):
            return 1 / (1 + np.exp(-z))

        for x in entradas:
            acts = [x]
            for l in range(3):
                z = acts[-1] @ W[l]
                if l == 2:
                    z = z * 2.0
                    e = np.exp(z - z.max())
                    acts.append(e / e.sum())
                else:
                    acts.append(sig(z * 1.6))
            # entrada
            self.play(*[n.animate.set_fill(C_SAT, opacity=0.15 + 0.8 * a).set_stroke(C_SAT)
                        for n, a in zip(capas[0], acts[0])], run_time=0.35)
            for l in range(3):
                flashes = []
                for (i, j), e in aristas[l].items():
                    if acts[l][i] > 0.35:
                        f = e.copy().set_color(C_SAT).set_stroke(
                            width=e.stroke_width + 1.5, opacity=min(1, 0.4 + acts[l][i]))
                        flashes.append(ShowPassingFlash(f, time_width=0.5))
                self.play(*flashes, run_time=0.75, rate_func=linear)
                ult = l == 2
                anims = []
                for k, (n, a) in enumerate(zip(capas[l + 1], acts[l + 1])):
                    gana = ult and a == acts[3].max()
                    col = C_OK if gana else C_SAT
                    anims.append(n.animate.set_fill(col, opacity=0.15 + 0.8 * a).set_stroke(col))
                self.play(*anims, run_time=0.35)
            self.wait(0.5)
            self.play(*[n.animate.set_fill(C_ANT, opacity=0.15).set_stroke(C_ANT)
                        for c in capas for n in c], run_time=0.5)
        self.cierre()


# =============================================================================
# 2. Agente aprende
# =============================================================================
class AgenteAprende(Pieza):
    def construct(self):
        rng = np.random.default_rng(RNG_BASE + 2)
        ag = caja("Agente", 2.6, 0.95, C_SAT, 28).move_to([-3.6, 2.15, 0])
        en = caja("Entorno", 2.6, 0.95, C_ANT, 28).move_to([3.6, 2.15, 0])
        self.play(FadeIn(ag, shift=RIGHT * 0.3), FadeIn(en, shift=LEFT * 0.3), run_time=0.8)

        a_top = ArcBetweenPoints(ag.get_top() + RIGHT * 0.5, en.get_top() + LEFT * 0.5, angle=-PI / 3.2)
        a_top.set_color(C_SAT).set_stroke(width=3.5)
        a_top.add_tip(tip_length=0.2)
        a_mid = flecha(en.get_left() + UP * 0.0, ag.get_right(), C_ANT, 3.5, 0.2)
        a_bot = ArcBetweenPoints(en.get_bottom() + LEFT * 0.5, ag.get_bottom() + RIGHT * 0.5, angle=-PI / 3.2)
        a_bot.set_color(C_OK).set_stroke(width=3.5)
        a_bot.add_tip(tip_length=0.2)
        l_top = et("acción", 24, C_SAT).next_to(a_top, UP, buff=0.1)
        l_mid = et("estado", 24, C_ANT).next_to(a_mid, UP, buff=0.1)
        l_bot = et("recompensa", 24, C_OK).next_to(a_bot, DOWN, buff=0.1)
        self.play(Create(a_top), FadeIn(l_top), run_time=0.7)
        self.play(Create(a_mid), FadeIn(l_mid), run_time=0.7)
        self.play(Create(a_bot), FadeIn(l_bot), run_time=0.7)

        ax = Axes(x_range=[0, 10, 1], y_range=[0, 1, 0.25], x_length=9.4, y_length=2.7,
                  tips=False, axis_config={"color": C_EJE, "stroke_width": 2.5,
                                           "include_ticks": False}).move_to([0.3, -1.9, 0])
        ex = et("Episodios", 22, TENUE).next_to(ax.x_axis, DOWN, buff=0.15)
        ey = et("Recompensa", 22, TENUE).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(ex), FadeIn(ey), run_time=0.9)

        ts = np.linspace(0, 10, 81)
        ruido = rng.normal(0, 1, len(ts))
        ruido = np.convolve(ruido, [0.4, 0.6, 0.4], mode="same")
        ys = 0.08 + 0.82 * (1 - np.exp(-ts / 2.8)) + 0.16 * np.exp(-ts / 3.0) * ruido
        ys = np.clip(ys, 0.02, 0.98)
        cuatro = np.array_split(np.arange(len(ts)), 4)
        solape = 0
        segs = []
        for k, idx in enumerate(cuatro):
            if k > 0:
                idx = np.concatenate([[cuatro[k - 1][-1]], idx])
            pts = [ax.c2p(ts[i], ys[i]) for i in idx]
            s = VMobject(color=C_OK, stroke_width=4).set_points_smoothly(pts)
            segs.append(s)
        punta = Dot(ax.c2p(ts[0], ys[0]), radius=0.08, color=C_OK)
        self.add(punta)

        for k in range(4):
            d1 = Dot(a_top.get_start(), radius=0.09, color=C_SAT)
            d2 = Dot(a_mid.get_start(), radius=0.09, color=C_ANT)
            d3 = Dot(a_bot.get_start(), radius=0.09, color=C_OK)
            self.add(d1)
            self.play(MoveAlongPath(d1, a_top), run_time=0.7, rate_func=smooth)
            self.remove(d1)
            self.play(en[0].animate.set_fill(C_ANT, opacity=0.5), run_time=0.15)
            self.add(d2, d3)
            self.play(MoveAlongPath(d2, a_mid), MoveAlongPath(d3, a_bot),
                      en[0].animate.set_fill(C_ANT, opacity=0.18),
                      run_time=0.8, rate_func=smooth)
            self.remove(d2, d3)
            self.play(ag[0].animate.set_fill(C_OK, opacity=0.2 + 0.15 * k),
                      Create(segs[k], rate_func=smooth), MoveAlongPath(punta, segs[k], rate_func=smooth),
                      run_time=1.6)
        self.cierre()


# =============================================================================
# 3. Ciclo PADA
# =============================================================================
class CicloPADA(Pieza):
    def construct(self):
        A, B = 4.3, 2.75

        def el(t):
            return np.array([A * np.cos(t), B * np.sin(t), 0])

        def icono_ojo(c):
            return VGroup(Ellipse(width=0.75, height=0.4, color=c, stroke_width=3),
                          Dot(radius=0.09, color=c))

        def icono_lupa(c):
            return VGroup(Circle(radius=0.17, color=c, stroke_width=3).shift(UL * 0.08),
                          Line(UL * 0.08 + DR * 0.12, DR * 0.3, color=c, stroke_width=4))

        def icono_rama(c):
            return VGroup(Line([-0.3, 0, 0], [0, 0, 0], color=c, stroke_width=3),
                          Line([0, 0, 0], [0.3, 0.2, 0], color=c, stroke_width=3),
                          Line([0, 0, 0], [0.3, -0.2, 0], color=c, stroke_width=3),
                          Dot([0.3, 0.2, 0], radius=0.06, color=c), Dot([0.3, -0.2, 0], radius=0.06, color=c),
                          Dot([-0.3, 0, 0], radius=0.06, color=c))

        def icono_gear(c):
            return VGroup(Star(n=8, outer_radius=0.3, inner_radius=0.23, color=c, stroke_width=3),
                          Circle(radius=0.1, color=c, stroke_width=3))

        defs = [("Percepción", C_ANT, icono_ojo, 90),
                ("Análisis", C_CIELO, icono_lupa, 0),
                ("Decisión", C_SAT, icono_rama, -90),
                ("Acción", C_OK, icono_gear, 180)]
        bloques = []
        for txt, col, ic, ang in defs:
            r = RoundedRectangle(corner_radius=0.14, width=3.0, height=1.1, color=col,
                                 fill_color=col, fill_opacity=0.15, stroke_width=3)
            i = ic(col).move_to(r.get_left() + RIGHT * 0.55)
            t = et(txt, 28, TINTA).move_to(r.get_center() + RIGHT * 0.35)
            g = VGroup(r, i, t).move_to(el(np.radians(ang)))
            bloques.append(g)

        # centro: satélite y red
        anillo = Circle(radius=1.15, color=C_EJE, stroke_width=2)
        nodos_c = VGroup(*[Dot(1.15 * np.array([np.cos(a), np.sin(a), 0]), radius=0.07, color=C_ANT)
                           for a in np.linspace(0, TAU, 7)[:-1] + 0.3])
        sat = satelite(0.42).scale(1.15)
        centro = VGroup(anillo, nodos_c, sat)
        segs = [(68, 20), (-20, -68), (-112, -160), (160, 112)]
        arcos = []
        for a0, a1 in segs:
            p = ParametricFunction(lambda u, a0=a0, a1=a1: el(np.radians(a0 + (a1 - a0) * u)), t_range=[0, 1],
                                   color=TENUE, stroke_width=3.5)
            fin = p.get_end()
            tang = fin - p.point_from_proportion(0.96)
            tip = Triangle(color=TENUE, fill_color=TENUE, fill_opacity=1, stroke_width=0).scale(0.13)
            tip.rotate(angle_of_vector(tang) - PI / 2).move_to(fin)
            p.tip_ = tip
            arcos.append(p)

        self.play(FadeIn(centro, scale=0.7), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(b, scale=0.85) for b in bloques], lag_ratio=0.3), run_time=1.6)
        self.play(LaggedStart(*[AnimationGroup(Create(a), FadeIn(a.tip_)) for a in arcos], lag_ratio=0.25), run_time=1.2)
        self.respiro(0.3)

        def brillar(k, col):
            return bloques[k][0].animate.set_fill(col, opacity=0.6)

        def apagar(k, col):
            return bloques[k][0].animate.set_fill(col, opacity=0.15)

        cols = [d[1] for d in defs]
        pulso_ = Dot(el(np.radians(90)) + DOWN * 0.7, radius=0.11, color=C_SAT)
        pulso_.set_z_index(5)
        self.add(pulso_)
        for vuelta in range(2):
            for k in range(4):
                self.play(brillar(k, cols[k]), run_time=0.35)
                onda = Circle(radius=0.3, color=cols[k], stroke_width=3).move_to(ORIGIN)
                self.play(MoveAlongPath(pulso_, arcos[k], rate_func=smooth),
                          apagar(k, cols[k]),
                          Succession(Wait(0.1), AnimationGroup(
                              onda.animate.scale(3.5).set_stroke(opacity=0), run_time=0.9)),
                          run_time=1.0)
        self.play(brillar(0, cols[0]), FadeOut(pulso_), run_time=0.3)
        self.play(*[brillar(k, cols[k]) for k in range(1, 4)], run_time=0.5)
        self.cierre()


# =============================================================================
# 4. Muchos agentes CTDE
# =============================================================================
class MuchosAgentesCTDE(Pieza):
    def construct(self):
        cen = np.array([0, -0.35, 0])
        pos = [cen + np.array([4.7 * np.cos(a), 2.4 * np.sin(a), 0])
               for a in np.radians([150, 30, 270])]
        sats = [satelite(0.24).move_to(pos[0]), satelite(0.24).move_to(pos[1]), estacion(0.4).move_to(pos[2])]
        nombres = VGroup(et_junto("Sat A", sats[0], UP, 22, TINTA), et_junto("Sat B", sats[1], UP, 22, TINTA),
                         et_junto("Gateway", sats[2], LEFT, 22, TINTA))
        agentes = [Circle(radius=0.15, color=C_CIELO, fill_color=TENUE, fill_opacity=0.4,
                          stroke_width=2.5).move_to(p + DOWN * 0.5) for p in pos]
        coord = Circle(radius=0.82, color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.3,
                       stroke_width=3).move_to(cen)
        coord_ic = et("Mezclador", 20, TINTA).move_to(cen)
        coord_g = VGroup(coord, coord_ic)
        coord_l = VGroup()

        self.play(LaggedStart(*[FadeIn(s, scale=0.6) for s in sats], lag_ratio=0.1), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(a, scale=0.6) for a in agentes], lag_ratio=0.1), FadeIn(nombres), run_time=0.8)

        lab1 = et("Entrenamiento", 30, C_CIELO).move_to([0, 3.45, 0])
        self.play(FadeIn(lab1, shift=DOWN * 0.2), FadeIn(coord_g, scale=0.6), FadeIn(coord_l), run_time=0.8)
        lineas = [haz(p, cen, C_CIELO, 2, 0.5) for p in pos]
        for l, p in zip(lineas, pos):
            v = (cen - p) / np.linalg.norm(cen - p)
            l.put_start_and_end_on(p + v * 0.55, cen - v * 0.85)
        self.play(LaggedStart(*[Create(l) for l in lineas], lag_ratio=0.08), run_time=1.0)

        for ronda in range(2):
            ent = [Dot(l.get_start(), radius=0.08, color=C_SAT) for l in lineas]
            self.add(*ent)
            self.play(*[d.animate.move_to(l.get_end()) for d, l in zip(ent, lineas)],
                      run_time=1.0, rate_func=smooth)
            self.remove(*ent)
            self.play(Flash(cen, color=C_CIELO, flash_radius=1.0, line_length=0.15, run_time=0.5))
            sal = [Dot(l.get_end(), radius=0.08, color=C_CIELO) for l in lineas]
            self.add(*sal)
            self.play(*[d.animate.move_to(l.get_start()) for d, l in zip(sal, lineas)],
                      *[a.animate.set_fill(C_CIELO, opacity=0.4 + 0.3 * (ronda + 1))
                        for a in agentes],
                      run_time=1.0, rate_func=smooth)
            self.remove(*sal)
        self.respiro(0.2)

        # ejecución
        lab2 = et("Ejecución", 30, C_OK).move_to(lab1)
        self.play(FadeOut(VGroup(*lineas)), FadeOut(coord_g), FadeOut(coord_l),
                  FadeTransform(lab1, lab2), run_time=1.0)
        enl = []
        for i in range(3):
            for j in (i + 1,):
                j %= 3
                a, b = pos[i], pos[j]
                v = (b - a) / np.linalg.norm(b - a)
                enl.append((i, j, Line(a + v * 0.55, b - v * 0.55, color=C_OK, stroke_width=2,
                                       stroke_opacity=0.55)))
        self.play(LaggedStart(*[Create(e[2]) for e in enl], lag_ratio=0.03),
                  *[a.animate.set_fill(C_OK, opacity=0.9).set_stroke(C_OK) for a in agentes],
                  run_time=1.2)
        for ronda in range(2):
            dots = []
            anims = []
            for i, j, e in enl:
                d = Dot(e.get_start(), radius=0.06, color=C_OK)
                dots.append(d)
                anims.append(d.animate.move_to(e.get_end()))
            self.add(*dots)
            self.play(*anims, run_time=0.9, rate_func=smooth)
            self.remove(*dots)
            self.play(*[Flash(a, color=C_OK, flash_radius=0.35, line_length=0.1, num_lines=8,
                              run_time=0.5) for a in agentes])
        self.cierre()


# =============================================================================
# 5. Satélite miente (consenso bizantino)
# =============================================================================
class SateliteMiente(Pieza):
    def construct(self):
        C = np.array([-1.7, -0.1, 0])
        R = 2.75
        n = 7
        pos = [C + R * np.array([np.cos(np.radians(90 + k * 360 / n)),
                                 np.sin(np.radians(90 + k * 360 / n)), 0]) for k in range(n)]
        nod = []
        for k in range(n):
            col = C_MAL if k == 0 else C_ANT
            nod.append(Circle(radius=0.34, color=col, fill_color=col, fill_opacity=0.25,
                              stroke_width=3).move_to(pos[k]).set_z_index(3))
        pares = sorted({tuple(sorted((k, (k + d) % n))) for k in range(n) for d in (1, 2)})
        enl = {}
        for a, b in pares:
            v = (pos[b] - pos[a]) / np.linalg.norm(pos[b] - pos[a])
            enl[(a, b)] = Line(pos[a] + v * 0.36, pos[b] - v * 0.36, color=C_EJE, stroke_width=2.2,
                               stroke_opacity=0.8)

        def L(a, b):
            return enl[tuple(sorted((a, b)))]

        self.play(LaggedStart(*[FadeIn(x, scale=0.6) for x in nod], lag_ratio=0.1), run_time=1.0)
        self.play(LaggedStart(*[Create(e) for e in enl.values()], lag_ratio=0.03), run_time=1.0)

        # contador
        cont_v = ValueTracker(0)
        num = DecimalNumber(0, num_decimal_places=0, font_size=96, color=C_MAL)
        cx = np.array([4.6, 0.7, 0])
        num.add_updater(lambda m: m.set_value(cont_v.get_value()).set_color(
            C_OK if cont_v.get_value() >= 5 else C_MAL).move_to(cx))
        num.set_stroke(width=0)
        et_v = et("Votos", 26, TENUE).move_to(cx + UP * 1.1)
        et_q = et("≥ 2f+1", 30, C_CIELO).move_to(cx + DOWN * 1.0)
        et_n = et("n=7 f=2", 22, TENUE).move_to(cx + DOWN * 1.55)
        self.play(FadeIn(num), FadeIn(et_v), FadeIn(et_q), FadeIn(et_n), run_time=0.6)

        def pulso_a(a, b, col, r=0.09):
            d = Dot(pos[a], radius=r, color=col).set_z_index(4)
            return d, pos[b]

        # ronda 1: votos
        dots, anims = [], []
        for k in range(1, n):
            for d in (1, 2):
                for j in ((k + d) % n, (k - d) % n):
                    if j != 0 and k != 0 and tuple(sorted((k, j))) in enl:
                        pass
        # honestos envían A a sus vecinos honestos (una sola tanda visual)
        vecinos = {k: [j for j in range(n) if tuple(sorted((k, j))) in enl] for k in range(n)}
        for k in range(1, n):
            for j in vecinos[k]:
                if j == 0:
                    continue
                d, t = pulso_a(k, j, C_ANT, 0.07)
                dots.append(d)
                anims.append(d.animate.move_to(t))
        self.add(*dots)
        self.play(*anims, run_time=1.0, rate_func=smooth)
        self.remove(*dots)
        # bizantino miente
        enviados = {}
        dots, anims = [], []
        for j in vecinos[0]:
            valor = C_ANT if j in (1, 2) else C_SAT
            enviados[j] = valor
            d, t = pulso_a(0, j, valor, 0.11)
            dots.append(d)
            anims.append(d.animate.move_to(pos[j] + (pos[0] - pos[j]) * 0.0))
        self.add(*dots)
        self.play(*anims, run_time=1.0, rate_func=smooth)
        self.remove(*dots)
        fichas = VGroup()
        for j, col in enviados.items():
            out = (pos[j] - C) / np.linalg.norm(pos[j] - C)
            fichas.add(Dot(pos[j] + out * 0.6, radius=0.11, color=col))
        self.play(FadeIn(fichas, scale=0.4), run_time=0.5)

        # ronda 2: comparación entre honestos que recibieron
        rec = list(enviados.keys())
        dots, anims = [], []
        for j in rec:
            for m in vecinos[j]:
                if m == 0:
                    continue
                d = Dot(pos[j], radius=0.07, color=enviados[j]).set_z_index(4)
                dots.append(d)
                anims.append(d.animate.move_to(pos[m]))
        self.add(*dots)
        self.play(*anims, run_time=1.1, rate_func=smooth)
        self.remove(*dots)
        dif = et("≠", 44, C_MAL).move_to(pos[0] + RIGHT * 0.95 + UP * 0.1)
        halo = Circle(radius=0.5, color=C_MAL, stroke_width=4).move_to(pos[0])
        self.play(FadeIn(dif, scale=1.6), Create(halo),
                  *[Indicate(nod[j], color=C_MAL, scale_factor=1.2) for j in rec], run_time=1.0)
        self.respiro(0.2)
        # aislar
        cortes = [L(0, j) for j in vecinos[0]]
        self.play(*[e.animate.set_color(C_MAL).set_stroke(width=4, opacity=1) for e in cortes], run_time=0.4)
        marcas = VGroup(*[cruz(C_MAL, 0.13, 4).move_to(e.get_center()) for e in cortes])
        self.play(FadeIn(marcas, scale=0.5), run_time=0.3)
        self.play(*[FadeOut(e) for e in cortes], FadeOut(marcas), FadeOut(fichas), FadeOut(dif),
                  nod[0].animate.set_opacity(0.4).shift((pos[0] - C) / R * 0.45),
                  halo.animate.shift((pos[0] - C) / R * 0.45).set_stroke(opacity=0.5), run_time=1.0)
        # consenso entre honestos
        dots, anims = [], []
        for (a, b), e in enl.items():
            if a == 0 or b == 0:
                continue
            for s, t in ((a, b), (b, a)):
                d = Dot(pos[s], radius=0.07, color=C_OK).set_z_index(4)
                dots.append(d)
                anims.append(d.animate.move_to(pos[t]))
        self.add(*dots)
        self.play(*anims, run_time=1.0, rate_func=smooth)
        self.remove(*dots)
        self.play(LaggedStart(*[nod[k].animate.set_color(C_OK).set_fill(C_OK, opacity=0.6)
                                for k in range(1, n)], lag_ratio=0.25),
                  cont_v.animate.set_value(6).set_rate_func(linear),
                  *[e.animate.set_color(C_OK).set_stroke(opacity=0.6) for (a, b), e in enl.items()
                    if a != 0 and b != 0], run_time=2.2)
        self.play(Indicate(num, color=C_OK, scale_factor=1.15), run_time=0.7)
        self.cierre()


# =============================================================================
# 6. Margen adaptativo
# =============================================================================
class MargenAdaptativo(Pieza):
    """MA = (V_oráculo - V_estática) / V_estática: propiedad del BANCO, no del algoritmo.
    Cifras de la tesis: NTNEnv v1 (G0) MA = 1.7 %; NTNEnv-v2 (G1) MA = 31.8 %;
    la heurística rinde por debajo de la mejor estática; QMIX (G2b) llega a +9.5..+16.3 %."""

    def construct(self):
        ax = Axes(x_range=[0, 10, 1], y_range=[0, 0.8, 0.2], x_length=7.6, y_length=5.0,
                  tips=False, axis_config={"color": C_EJE, "stroke_width": 2.5,
                                           "include_ticks": False}).move_to([-2.6, -0.35, 0])
        ex = et("Tiempo", 22, TENUE).next_to(ax.x_axis, DOWN, buff=0.15).align_to(ax.x_axis, RIGHT)
        ey = et("Valor", 22, TENUE).next_to(ax.y_axis, UP, buff=0.15).align_to(ax.y_axis, LEFT)
        self.play(Create(ax), FadeIn(ex), FadeIn(ey), run_time=1.0)

        EST = 0.45
        UMB = EST * 1.25
        MA1, MA2 = 0.017, 0.318
        Q_MA = 0.12

        def curva(techo, tau=2.6, fase=0.0, amp=0.005):
            return lambda t: 0.25 + (techo - 0.25) * (1 - np.exp(-t / tau)) + amp * np.sin(2.6 * t + fase)

        g_est = ax.plot(lambda t: EST, x_range=[0, 10], color=TENUE, stroke_width=4)
        g_h = ax.plot(curva(EST * 0.78, 2.5, 1.0), x_range=[0, 10], color=C_ANT, stroke_width=4)
        umbral = DashedLine(ax.c2p(0, UMB), ax.c2p(10, UMB), color=C_CIELO, stroke_width=3,
                            dash_length=0.15)
        l_umb = et("Umbral 25 %", 22, C_CIELO).next_to(umbral, UP, buff=0.08).align_to(umbral, LEFT).shift(RIGHT * 0.1)

        def ley(txt, col, y):
            return VGroup(Line(LEFT * 0.3, RIGHT * 0.3, color=col, stroke_width=5),
                          et(txt, 24, TINTA)).arrange(RIGHT, buff=0.2).move_to([5.7, y, 0], aligned_edge=LEFT)

        lg = VGroup(ley("Estática", TENUE, 2.9), ley("Heurística", C_ANT, 2.4),
                    ley("Oráculo", C_SAT, 1.9), ley("QMIX", C_OK, 1.4))
        for g_ in lg:
            g_.align_to(lg[0], LEFT)
        lg.move_to([4.6, 2.15, 0])

        self.play(Create(g_est), FadeIn(lg[0]), run_time=0.8)
        self.play(Create(umbral), FadeIn(l_umb), run_time=0.8)
        self.play(Create(g_h), FadeIn(lg[1]), run_time=1.0)

        def armar(ma, col):
            techo = EST * (1 + ma)
            go = ax.plot(curva(techo, 2.0), x_range=[0, 10], color=C_SAT, stroke_width=5)
            f = curva(techo, 2.0)
            x0 = next((t for t in np.linspace(0, 10, 2000) if f(t) > EST + 0.0005), 4)
            area = ax.get_area(go, x_range=[x0, 10], bounded_graph=g_est, color=col, opacity=0.45)
            y1 = f(10)
            p0, p1 = ax.c2p(10.35, EST), ax.c2p(10.35, y1)
            if np.linalg.norm(p1 - p0) > 0.5:
                marca = DoubleArrow(p0, p1, buff=0, color=col, stroke_width=4, tip_length=0.14,
                                    max_tip_length_to_length_ratio=0.5)
            else:
                marca = Line(p0 + DOWN * 0.03, p1 + UP * 0.03, color=col, stroke_width=8)
            return go, area, marca

        go, area, fm = armar(MA1, C_MAL)
        t_ma = ValueTracker(0)
        pct = et("%", 44, TENUE).move_to([5.9, -0.5, 0])
        lab_ma = et("MA", 40, TENUE).move_to([3.3, -0.5, 0])
        num = DecimalNumber(0, num_decimal_places=1, font_size=72, color=C_MAL)
        num.set_stroke(width=0)
        num.add_updater(lambda m: m.set_value(t_ma.get_value()).set_color(
            C_OK if t_ma.get_value() >= 25 else C_MAL).next_to(pct, LEFT, buff=0.12))
        tag1 = VGroup(VGroup(cruz(C_MAL, 0.14, 5), et("Banco inválido", 26, C_MAL)).arrange(RIGHT, buff=0.2),
                      et("NTNEnv v1", 22, TENUE)).arrange(DOWN, buff=0.12).move_to([4.7, -1.75, 0])
        tag2 = VGroup(VGroup(visto(C_OK, 0.14, 5), et("Banco válido", 26, C_OK)).arrange(RIGHT, buff=0.2),
                      et("NTNEnv v2", 22, TENUE)).arrange(DOWN, buff=0.12).move_to([4.7, -1.75, 0])

        self.play(Create(go), FadeIn(lg[2]), run_time=2.0)
        self.play(FadeIn(area), Create(fm), FadeIn(lab_ma), FadeIn(pct), FadeIn(num), FadeIn(tag1),
                  run_time=0.8)
        self.play(t_ma.animate.set_value(MA1 * 100), run_time=1.0)
        self.respiro(1.6)

        go2, area2, fm2 = armar(MA2, C_OK)
        self.play(Transform(go, go2), Transform(area, area2), Transform(fm, fm2),
                  t_ma.animate.set_value(MA2 * 100), ReplacementTransform(tag1, tag2), run_time=2.2)
        self.play(Flash(ax.c2p(10.35, UMB), color=C_OK, flash_radius=0.4, run_time=0.6),
                  Indicate(num, color=C_OK, scale_factor=1.12))
        # el aprendiz (QMIX) queda por debajo del techo del oráculo
        gq = ax.plot(curva(EST * (1 + Q_MA), 3.0, 2.0, 0.006), x_range=[0, 10], color=C_OK, stroke_width=5)
        self.play(Create(gq), FadeIn(lg[3]), run_time=2.0)
        self.cierre()


# =============================================================================
# 7. IA a bordo
# =============================================================================
class IAaBordo(Pieza):
    def construct(self):
        rng = np.random.default_rng(RNG_BASE + 7)
        cols, filas = 8, 5
        cw, ch = 0.9, 0.8
        gc = np.array([-2.5, -0.55, 0])
        rel = {(1, 3), (2, 3), (5, 1), (6, 1)}
        cel = {}
        grupo = VGroup()
        for i in range(cols):
            for j in range(filas):
                p = gc + np.array([(i - (cols - 1) / 2) * cw, ((filas - 1) / 2 - j) * ch, 0])
                r = Rectangle(width=cw, height=ch, color=C_EJE, stroke_width=1.2,
                              fill_color=C_TIERRA_2, fill_opacity=float(rng.uniform(0.45, 0.85))).move_to(p)
                cel[(i, j)] = r
                grupo.add(r)
        fuegos = VGroup()
        for (i, j) in rel:
            p = cel[(i, j)].get_center()
            fuegos.add(Dot(p, radius=0.11, color=C_MAL), Dot(p + [0.15, -0.1, 0], radius=0.06, color=C_SAT),
                       Dot(p + [-0.15, 0.12, 0], radius=0.05, color=C_MAL))
        self.play(FadeIn(grupo, lag_ratio=0.02), run_time=1.2)
        self.play(FadeIn(fuegos, scale=0.5), run_time=0.5)

        est = estacion(0.8).move_to([4.3, -1.6, 0])
        bar_marco = Rectangle(width=0.7, height=3.0, color=C_EJE, stroke_width=3).move_to([6.2, 0.55, 0])
        lab_d = et("Datos", 22, TENUE).next_to(bar_marco, DOWN, buff=0.15)
        nivel = ValueTracker(1.0)
        bar = always_redraw(lambda: Rectangle(
            width=0.7, height=max(0.001, 3.0 * nivel.get_value()), color=C_SAT, fill_color=C_SAT,
            fill_opacity=0.8, stroke_width=0).move_to(bar_marco.get_bottom() + UP * 1.5 * nivel.get_value(), )
            .align_to(bar_marco, DOWN))
        self.play(FadeIn(est), Create(bar_marco), FadeIn(bar), FadeIn(lab_d), run_time=0.8)

        xs = [gc[0] + (i - (cols - 1) / 2) * cw for i in range(cols)]
        xt = ValueTracker(xs[0])
        sat = satelite(0.28)
        sat.add_updater(lambda m: m.move_to([xt.get_value(), 2.85, 0]))
        gtop = gc[1] + filas * ch / 2
        gbot = gc[1] - filas * ch / 2

        def haz_():
            x = xt.get_value()
            return Polygon([x, 2.6, 0], [x - cw / 2, gbot, 0], [x + cw / 2, gbot, 0], stroke_width=0,
                           fill_color=C_SAT, fill_opacity=0.16)
        beam = always_redraw(haz_)
        self.play(FadeIn(sat, shift=DOWN * 0.3), FadeIn(beam), run_time=0.6)

        cajas = VGroup()
        descartadas = 0
        for i in range(cols):
            anims = [xt.animate.set_value(xs[i])]
            nuevos = []
            for j in range(filas):
                if (i, j) in rel:
                    b = SurroundingRectangle(cel[(i, j)], color=C_OK, buff=0.0, stroke_width=5)
                    nuevos.append(Create(b))
                    cajas.add(b)
                else:
                    anims.append(cel[(i, j)].animate.set_fill(opacity=0.12).set_stroke(opacity=0.35))
                    descartadas += 1
            anims.append(nivel.animate.set_value(1 - descartadas / (cols * filas)))
            self.play(*anims, *nuevos, run_time=0.65, rate_func=linear)
        self.play(FadeOut(beam), run_time=0.3)
        cifra_ahorro = VGroup(et("Menos", 40, C_OK), et("datos", 22, TENUE)).arrange(DOWN, buff=0.05).move_to([5.7, 2.85, 0])
        self.play(FadeIn(cifra_ahorro, shift=DOWN * 0.2), run_time=0.5)

        # enlace de bajada de los recortes
        enlace = haz(sat.get_center() + DOWN * 0.3, est.get_top() + UP * 0.1, C_ANT, 2.5, 0.9)
        self.play(Create(enlace), run_time=0.5)
        crops = []
        for (i, j) in sorted(rel):
            c = cel[(i, j)]
            crop = VGroup(Square(0.34, color=C_OK, stroke_width=3, fill_color=C_OK, fill_opacity=0.25),
                          Dot(radius=0.06, color=C_MAL)).move_to(c.get_center())
            crops.append(crop)
        self.add(*crops)
        rutas = [poli(c.get_center(), [xt.get_value(), 2.5, 0], est.get_top() + UP * 0.1) for c in crops]
        self.play(LaggedStart(*[MoveAlongPath(c, r, rate_func=smooth) for c, r in zip(crops, rutas)],
                              lag_ratio=0.25), run_time=3.0)
        self.play(*[FadeOut(c, scale=0.3) for c in crops], Flash(est.get_top(), color=C_OK,
                                                                 flash_radius=0.5, run_time=0.6))
        self.cierre()


# =============================================================================
# 8. GNN
# =============================================================================
class GrafoGNN(Pieza):
    def construct(self):
        P0 = np.array([(-5.6, 1.2), (-4.2, -1.2), (-3.9, 2.4), (-2.2, 0.4), (-1.6, -2.3), (-0.6, 2.0),
                       (0.6, -0.6), (1.9, 1.3), (2.8, -2.1), (4.2, 0.3), (5.4, 2.0), (5.3, -1.5)])
        P0 = np.hstack([P0, np.zeros((len(P0), 1))])
        desp = np.array([(0.3, -0.2), (-0.1, 0.3), (0.2, 0.1), (0.1, -0.3), (0.3, 0.2), (-0.2, -0.3),
                         (-0.2, 0.3), (0.3, -0.2), (-0.3, -0.1), (0.2, 0.3), (-0.3, -0.2), (0.0, 0.3)])
        P1 = P0 + np.hstack([desp, np.zeros((len(P0), 1))])
        n = len(P0)
        UM = 3.3

        def vec(P):
            return {i: [j for j in range(n) if j != i and np.linalg.norm(P[i] - P[j]) < UM]
                    for i in range(n)}
        vec0, vec1 = vec(P0), vec(P1)
        assert all(len(v) > 0 for v in vec1.values()), vec1
        pares = sorted({tuple(sorted((i, j))) for i in range(n) for j in range(n)
                        if i != j and (np.linalg.norm(P0[i] - P1[j]) < 4.6 or np.linalg.norm(P0[i] - P0[j]) < UM
                                       or np.linalg.norm(P1[i] - P1[j]) < UM)
                        and (np.linalg.norm(P0[i] - P0[j]) < UM or np.linalg.norm(P1[i] - P1[j]) < UM)})

        rng = np.random.default_rng(RNG_BASE + 8)
        v = rng.uniform(0, 1, n)
        nodos = [Circle(radius=0.3, color=cmap(v[i]), fill_color=cmap(v[i]), fill_opacity=0.8,
                        stroke_width=3).move_to(P0[i]).set_z_index(3) for i in range(n)]

        def mk_edge(i, j):
            def f():
                a, b = nodos[i].get_center(), nodos[j].get_center()
                d = np.linalg.norm(a - b)
                op = 0.7 if d < UM else 0.0
                u = (b - a) / max(d, 1e-6)
                return Line(a + u * 0.3, b - u * 0.3, color=C_EJE, stroke_width=2.5, stroke_opacity=op)
            return always_redraw(f)
        aristas = [mk_edge(i, j) for i, j in pares]

        self.play(LaggedStart(*[FadeIn(x, scale=0.5) for x in nodos], lag_ratio=0.08), run_time=1.2)
        self.add(*aristas)
        for a in aristas:
            a.set_z_index(1)
        self.play(FadeIn(VGroup(*aristas)), run_time=0.6)
        # topología dinámica: los satélites se desplazan
        self.play(*[nodos[i].animate.move_to(P1[i]) for i in range(n)], run_time=2.0, rate_func=smooth)
        self.respiro(0.2)

        def nuevos_valores(vv, vecs):
            return np.array([(vv[i] + sum(vv[j] for j in vecs[i])) / (1 + len(vecs[i])) for i in range(n)])

        def recolor(vv):
            return [nodos[i].animate.set_color(cmap(vv[i])).set_fill(cmap(vv[i]), opacity=0.8)
                    for i in range(n)]

        def mensajes(objetivos, vv, dur=1.0):
            pts, anims = [], []
            for i in objetivos:
                for j in vec1[i]:
                    d = Dot(P1[j], radius=0.09, color=cmap(vv[j])).set_z_index(4)
                    pts.append(d)
                    anims.append(d.animate.move_to(P1[i]))
            self.add(*pts)
            self.play(*anims, run_time=dur, rate_func=smooth)
            self.remove(*pts)

        # demostración con tres nodos
        for f in (3, 6, 9):
            aro = Circle(radius=0.5, color=TINTA, stroke_width=3).move_to(P1[f])
            self.play(Create(aro), run_time=0.35)
            mensajes([f], v, 0.8)
            nv = v.copy()
            nv[f] = (v[f] + sum(v[j] for j in vec1[f])) / (1 + len(vec1[f]))
            v = nv
            self.play(*recolor(v)[f:f + 1], FadeOut(aro), run_time=0.5)
        # capa completa
        et1 = et("Capa 1", 26, TENUE).move_to([-5.9, 3.5, 0])
        self.play(FadeIn(et1), run_time=0.3)
        mensajes(range(n), v, 1.1)
        v = nuevos_valores(v, vec1)
        self.play(*recolor(v), run_time=0.8)
        et2 = et("Capa 2", 26, TENUE).move_to(et1)
        self.play(FadeTransform(et1, et2), run_time=0.3)
        mensajes(range(n), v, 1.1)
        v = nuevos_valores(v, vec1)
        self.play(*recolor(v), run_time=0.8)
        self.cierre()


# =============================================================================
# 9. Política enruta tráfico
# =============================================================================
class PoliticaEnrutaTrafico(Pieza):
    def construct(self):
        S = np.array([-5.6, 0, 0])
        D = np.array([3.4, 0, 0])
        t1, t2 = np.array([-2.6, 2.1, 0]), np.array([0.4, 2.1, 0])
        m1, m2 = np.array([-2.6, 0, 0]), np.array([0.4, 0, 0])
        b1, b2 = np.array([-2.6, -2.1, 0]), np.array([0.4, -2.1, 0])
        puntos = {"S": S, "D": D, "t1": t1, "t2": t2, "m1": m1, "m2": m2, "b1": b1, "b2": b2}
        pares = [("S", "t1"), ("S", "m1"), ("S", "b1"), ("t1", "t2"), ("m1", "m2"), ("b1", "b2"),
                 ("t2", "D"), ("m2", "D"), ("b2", "D"), ("t1", "m1"), ("m1", "b1"), ("t2", "m2"), ("m2", "b2")]
        lin = {}
        for a, b in pares:
            lin[(a, b)] = Line(puntos[a], puntos[b], color=C_EJE, stroke_width=3)
        nod = {}
        for k, p in puntos.items():
            if k in ("S", "D"):
                nod[k] = VGroup(Circle(radius=0.42, color=C_ANT, fill_color=C_ANT, fill_opacity=0.3,
                                       stroke_width=3)).move_to(p)
            else:
                nod[k] = satelite(0.16).move_to(p)
            nod[k].set_z_index(3)
        self.play(LaggedStart(*[Create(l) for l in lin.values()], lag_ratio=0.05), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(x, scale=0.6) for x in nod.values()], lag_ratio=0.06), run_time=1.0)
        et_s = et("Origen", 20, TENUE).next_to(nod["S"], DOWN, buff=0.15)
        et_d = et("Destino", 20, TENUE).next_to(nod["D"], DOWN, buff=0.15)
        self.play(FadeIn(et_s), FadeIn(et_d), run_time=0.4)

        # indicador de retardo
        ret = ValueTracker(45)
        marco = Rectangle(width=0.6, height=3.4, color=C_EJE, stroke_width=3).move_to([5.9, 0.2, 0])

        def col_ret():
            return interpolate_color(ManimColor(C_OK), ManimColor(C_MAL),
                                     float(np.clip((ret.get_value() - 45) / 165, 0, 1)))
        barra = always_redraw(lambda: Rectangle(
            width=0.6, height=max(0.01, 3.4 * ret.get_value() / 220), stroke_width=0,
            fill_color=col_ret(), fill_opacity=0.85).align_to(marco, DOWN).align_to(marco, LEFT))
        num = DecimalNumber(45, num_decimal_places=0, font_size=44)
        num.set_stroke(width=0)
        num.add_updater(lambda m: m.set_value(ret.get_value()).set_color(col_ret()))
        ms = et("ms", 24, TENUE).move_to([6.55, 2.65, 0])
        num.add_updater(lambda m: m.move_to([5.6, 2.7, 0]))
        lab_r = et("Retardo relativo", 22, TENUE).next_to(marco, DOWN, buff=0.15)
        ilus = et("Ilustrativo", 20, TENUE).move_to([5.3, 2.7, 0])
        self.play(Create(marco), FadeIn(barra), FadeIn(ilus), FadeIn(lab_r), run_time=0.8)

        # fase estática
        pol1 = et("Estática", 30, C_MAL).move_to([-5.6, 3.5, 0])
        self.play(FadeIn(pol1, shift=DOWN * 0.2), run_time=0.4)
        # enlace congestionado
        rojo = Line(m1, m2, color=C_MAL, stroke_width=8, stroke_opacity=0.9)
        self.play(Transform(lin[("m1", "m2")], rojo), run_time=0.6)
        slots = [m1 + LEFT * (0.42 + 0.3 * k) for k in range(8)]
        paquetes = []
        anims = []
        for k in range(8):
            d = Dot(S, radius=0.1, color=C_SAT).set_z_index(4)
            d.set_opacity(0)
            paquetes.append(d)
            ruta = poli(S, slots[k])
            anims.append(Succession(d.animate(run_time=0.01).set_opacity(1),
                                    MoveAlongPath(d, ruta, run_time=1.1 + 0.05 * (7 - k), rate_func=linear)))
        self.add(*paquetes)
        self.play(LaggedStart(*anims, lag_ratio=0.45), ret.animate.set_value(210).set_rate_func(smooth),
                  run_time=5.5)
        # un paquete cruza lentamente el enlace rojo
        self.play(Flash(m1, color=C_MAL, flash_radius=0.5, run_time=0.6))
        self.respiro(0.4)

        # fase adaptativa
        pol2 = et("Adaptativa", 30, C_OK).move_to(pol1)
        verdes = [Line(puntos[a], puntos[b], color=C_OK, stroke_width=5, stroke_opacity=0.9)
                  for a, b in [("S", "t1"), ("t1", "t2"), ("t2", "D"), ("S", "b1"), ("b1", "b2"), ("b2", "D")]]
        self.play(FadeTransform(pol1, pol2),
                  *[Create(g) for g in verdes], run_time=1.0)
        rutas_t = [poli(m1, t1, t2, D), poli(m1, b1, b2, D)]
        salida = []
        for k, d in enumerate(paquetes):
            r = rutas_t[k % 2]
            salida.append(MoveAlongPath(d, poli(d.get_center(), *[tuple(p[:2]) for p in
                                                                  ([m1, t1, t2, D] if k % 2 == 0 else [m1, b1, b2, D])]),
                                        run_time=2.4, rate_func=linear))
        nuevos = []
        anims2 = []
        for k in range(8):
            d = Dot(S, radius=0.1, color=C_OK).set_z_index(4)
            d.set_opacity(0)
            nuevos.append(d)
            via = [t1, t2, D] if k % 2 == 0 else [b1, b2, D]
            anims2.append(Succession(d.animate(run_time=0.01).set_opacity(1),
                                     MoveAlongPath(d, poli(S, *[tuple(p[:2]) for p in via]),
                                                   run_time=2.6, rate_func=linear),
                                     FadeOut(d, run_time=0.1)))
        self.add(*nuevos)
        self.play(LaggedStart(*salida, lag_ratio=0.12),
                  LaggedStart(*anims2, lag_ratio=0.3),
                  ret.animate.set_value(55).set_rate_func(smooth), run_time=5.0)
        self.remove(*paquetes)
        self.play(Transform(lin[("m1", "m2")], Line(m1, m2, color=C_EJE, stroke_width=3)), run_time=0.5)
        self.cierre()


# =============================================================================
# 10. Compuertas de validación
# =============================================================================
class CompuertasValidacion(Pieza):
    """Compuertas de la tesis: G0 control negativo, G1 MA >= 25 %, G2a/G2b reward > estática,
    G3 (corrida completa) pendiente, sin lanzar."""

    def construct(self):
        gx = [-5.0, -2.8, -0.6, 1.6, 3.8]
        nombres = ["G0", "G1", "G2a", "G2b", "G3"]
        subs = ["control negativo", "MA≥25 %", "reward > estática", "recualificación", "pendiente"]
        camino = Line([-6.6, 0, 0], [6.0, 0, 0], color=C_EJE, stroke_width=3)
        puertas = []
        for k, x in enumerate(gx):
            pil_i = Rectangle(width=0.22, height=2.4, color=TENUE, fill_color=TENUE,
                              fill_opacity=0.5, stroke_width=1.5).move_to([x - 0.6, 0, 0])
            pil_d = pil_i.copy().move_to([x + 0.6, 0, 0])
            dintel = Rectangle(width=1.42, height=0.2, color=TENUE, fill_color=TENUE,
                               fill_opacity=0.5, stroke_width=1.5).move_to([x, 1.3, 0])
            hoja = Rectangle(width=0.98, height=2.2, color=TENUE, fill_color=TENUE,
                             fill_opacity=0.35, stroke_width=3).move_to([x, 0.0, 0])
            hoja.set_z_index(2)
            lab = VGroup(et(nombres[k], 30, TINTA),
                         et(subs[k], 18, TENUE)).arrange(DOWN, buff=0.08).move_to([x, -2.05, 0])
            puertas.append({"pil": VGroup(pil_i, pil_d, dintel), "hoja": hoja, "lab": lab, "x": x})
        # G3: sin lanzar -> hoja punteada, sin relleno
        p3 = puertas[4]
        p3["hoja"].set_fill(opacity=0).set_stroke(opacity=0)
        p3["punteada"] = DashedVMobject(Rectangle(width=0.98, height=2.2, color=TENUE, stroke_width=3),
                                        num_dashes=28).move_to([p3["x"], 0, 0])
        ia = VGroup(Circle(radius=0.5, color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.2, stroke_width=3),
                    *[Dot(0.22 * np.array([np.cos(a), np.sin(a), 0]), radius=0.055, color=C_CIELO)
                      for a in np.linspace(0, TAU, 6)[:-1]], Dot(radius=0.06, color=C_CIELO)).move_to([6.1, 0, 0])
        ia.set_opacity(0.35)
        ia_l = et("IA", 26, TENUE).move_to([6.1, -2.05, 0])
        self.play(Create(camino), run_time=0.8)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(p["pil"]), FadeIn(p["hoja"], scale=0.9),
                                               FadeIn(p["lab"])) for p in puertas], lag_ratio=0.2),
                  FadeIn(p3["punteada"]), FadeIn(ia), FadeIn(ia_l), run_time=1.8)

        señal = Dot([-6.6, 0, 0], radius=0.14, color=C_SAT).set_z_index(5)
        self.play(FadeIn(señal, scale=0.5), run_time=0.3)

        def ir(x, t=0.8):
            self.play(señal.animate.move_to([x, 0, 0]), run_time=t, rate_func=smooth)

        def abrir(k):
            p = puertas[k]
            v = visto(C_OK, 0.17, 5).move_to([p["x"], 1.95, 0])
            self.play(p["hoja"].animate.set_color(C_OK).set_fill(C_OK, opacity=0.3), run_time=0.3)
            self.play(p["hoja"].animate.shift(UP * 2.1).set_opacity(0),
                      FadeIn(v, scale=0.5), run_time=0.6)

        for k in (0, 1):
            ir(puertas[k]["x"] - 0.85)
            abrir(k)
            ir(puertas[k]["x"] + 0.85, 0.7)

        # G2a: el primer intento falla y regresa
        p2 = puertas[2]
        ir(p2["x"] - 0.85)
        x_mal = cruz(C_MAL, 0.17, 5).move_to([p2["x"], 1.95, 0])
        self.play(p2["hoja"].animate.set_color(C_MAL).set_fill(C_MAL, opacity=0.45), FadeIn(x_mal, scale=0.5),
                  run_time=0.3)
        self.play(Wiggle(p2["hoja"], scale_value=1.05, rotation_angle=0.03 * TAU), señal.animate.set_color(C_MAL),
                  run_time=0.7)
        self.play(señal.animate.move_to([-3.6, 0, 0]), run_time=1.3, rate_func=smooth)
        rev = Arc(radius=0.4, start_angle=PI / 2, angle=1.6 * PI, color=C_SAT, stroke_width=4)
        rev.add_tip(tip_length=0.16)
        rev.move_to([-3.6, 0.95, 0])
        self.play(Create(rev), señal.animate.set_color(C_SAT), run_time=0.5)
        self.play(Rotate(rev, angle=-2 * TAU, about_point=rev.get_center(), rate_func=smooth), run_time=1.6)
        self.play(FadeOut(rev), run_time=0.2)
        ir(p2["x"] - 0.85, 1.3)
        self.play(FadeOut(x_mal), run_time=0.2)
        abrir(2)
        ir(p2["x"] + 0.85, 0.7)
        # G2b
        p2b = puertas[3]
        ir(p2b["x"] - 0.85)
        abrir(3)
        ir(p2b["x"] + 0.85, 0.7)
        # G3: aún sin lanzar -> la señal espera ante la puerta punteada
        for _ in range(2):
            self.play(señal.animate.scale(1.7).set_opacity(0.5), rate_func=there_and_back, run_time=0.9)
        self.cierre()

import heapq
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *

import datos_rob as DR
from estilo_reel import Viva, cerrar_serie, chip, leyenda, punto, preparar_serie, texto
from reels_promo import polilinea, suave

# SERIE «ROBÓTICA» — divulgación de la robótica aplicada a partir del rover planetario y la plataforma ROS 2 del ros2-workspace
# (Estación ATP). Todo SIMULADO (chip en pantalla), nada medido con hardware. Tema ROBÓTICA con fondo vertical propio
# (fondos_reel.robotica: hilera de engranes como horizonte, resplandor naranja de seguridad). Formato película: título → cuerpo → logo → loop.
# Pocas cifras, cada una con comparación cotidiana; los números salen de datos_rob.py (con su sección de docs/ROVER.md).

FIN = 3.0
KICKER = "Robótica"
SERIE = dict(tema="robotica", fondo="reel")
VERDE, ROJO, AZUL = "#4ADE80", "#F87171", "#3B8FD9"


def leyendas(escena, est, pel, nombre, textos):
    ts = list(DR.LEYENDAS[nombre]) + [DR.CUERPO[nombre] + FIN]
    for (g, p), a, b in zip(textos, ts[:-1], ts[1:]):
        leyenda(escena, est, pel, g, p, a, b)


def rampa(t, a, d=0.6):
    return suave((t - a) / d)


def fundir(m, k):
    """set_opacity(k) relativo al relleno y trazo originales (no vuelve opacos los rellenos transparentes)."""
    if not hasattr(m, "_base_op"):
        m._base_op = [(x, x.get_fill_opacity(), x.get_stroke_opacity()) for x in m.get_family() if isinstance(x, VMobject)]
    for x, f, s_ in m._base_op:
        x.set_fill(opacity=f * k, family=False).set_stroke(opacity=s_ * k, family=False)
    return m


def aparece(m, pel, t0, d=0.6, hasta=None):
    m.add_updater(lambda x: fundir(x, rampa(pel.t, t0, d) * ((1 - rampa(pel.t, hasta, d)) if hasta else 1)))
    fundir(m, 0)
    return m


def panel(est, x0, x1, y0, y1, op=0.8):
    return RoundedRectangle(corner_radius=0.2, width=x1 - x0, height=y1 - y0, stroke_width=1.6, stroke_color=est.linea,
                            fill_color=est.fondo, fill_opacity=op).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0]).set_z_index(2)


def rueda(est, c, r, ang=0.0, color=None):
    color = color or est.tinta
    g = VGroup(Circle(radius=r).set_fill(est.fondo, 1).set_stroke(color, 4))
    for k in range(3):
        g.add(Line([-r * 0.85, 0, 0], [r * 0.85, 0, 0], stroke_width=3, color=color).rotate(k * PI / 3))
    g.add(Dot(radius=r * 0.16, color=color))
    g.rotate(ang).move_to(c)
    return g.set_z_index(8)


# ══ 1 · ¿Por qué seis ruedas? (rocker-bogie) ════════════════════════════════════════════════════════════════════════════

class ReelRobBogie(Scene):
    VAR = 0

    def construct(self):
        n = "ReelRobBogie"; TB = DR.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Por qué seis ruedas\ny no cuatro?", self.VAR, chip_txt="Ilustración", **SERIE)
        YG, R = -2.0, DR.RADIO_RUEDA
        xs = np.linspace(-7.2, 7.2, 300)
        suelo = lambda x: float((0.55 if x > 5.0 else 0.0) + 1.05 * np.exp(-((x) / 0.9) ** 2))

        def centro(xw):
            dx = np.linspace(-R, R, 25)
            return max(suelo(xw + d) + np.sqrt(R * R - d * d) for d in dx)
        self.add(Polygon(*[[x, YG + suelo(x), 0] for x in xs], [7.2, YG - 1.4, 0], [-7.2, YG - 1.4, 0]).set_fill(est.linea, 0.8).set_stroke(est.tenue, 3).set_z_index(3))
        u = lambda: float(np.clip((pel.t - 1.2) / 13.0, 0, 1))
        xc = lambda: -4.2 + 7.4 * u()
        pts = lambda: [np.array([xc() + dx, YG + centro(xc() + dx), 0]) for dx in (-DR.BASE_RUEDAS[2], 0.0, DR.BASE_RUEDAS[2])]
        ruedas = [rueda(est, ORIGIN, R) for _ in range(3)]
        rocker, bogie, chasis, cuello = (Line(ORIGIN, RIGHT, stroke_width=7, color=est.acento2).set_z_index(7), Line(ORIGIN, RIGHT, stroke_width=7, color=est.acento2).set_z_index(7),
                                         Rectangle(width=3.8, height=0.8).set_fill(est.acento, 0.95).set_stroke(est.tinta, 3).set_z_index(9), Line(ORIGIN, UP, stroke_width=6, color=est.tinta).set_z_index(8))
        mastil = VGroup(Line(ORIGIN, UP * 0.9, stroke_width=5, color=est.tinta), Circle(radius=0.17).set_fill(est.calido, 1).set_stroke(width=0).shift(UP * 0.95)).set_z_index(9)

        def armar(_m):
            tr, me, de = pts()
            pb = (tr + me) / 2
            P = (de + 2 * pb) / 3
            for w, p, k in zip(ruedas, (tr, me, de), (0, 1, 2)):
                w.move_to(p)
            bogie.put_start_and_end_on(tr, me); rocker.put_start_and_end_on(de, pb)
            ang = 0.5 * np.arctan2(de[1] - tr[1], de[0] - tr[0])
            chasis.become(Rectangle(width=3.8, height=0.8).set_fill(est.acento, 0.95).set_stroke(est.tinta, 3).rotate(ang).move_to(P + UP * 1.0).set_z_index(9))
            cuello.put_start_and_end_on(P, P + UP * 0.6)
            mastil.move_to(P + UP * 1.0 + RIGHT * 1.2 + UP * 0.8 * np.cos(ang))
        rocker.add_updater(armar)
        self.add(*ruedas, rocker, bogie, chasis, cuello, mastil)
        giro = lambda: xc() / R
        for w in ruedas:
            w.add_updater(lambda m: m.become(rueda(est, m.get_center(), R, -giro())))
        # medidor: cuánto sube la rueda y cuánto sube el cuerpo (misma escala, ×2.5 para verlo)
        BX, BY, KB = 5.3, 1.4, 2.5
        self.add(aparece(Line([BX - 1.4, BY, 0], [BX + 1.4, BY, 0], stroke_width=3, color=est.tenue).set_z_index(5), pel, 5.0))
        barra_r, barra_c = Rectangle(width=0.55, height=0.01).set_z_index(6), Rectangle(width=0.55, height=0.01).set_z_index(6)

        def medir(m):
            tr, me, de = pts()
            sube_r = max(max(p[1] for p in (tr, me, de)) - (YG + R), 0.0)
            P = (de + 2 * (tr + me) / 2) / 3
            sube_c = max(P[1] - (YG + R), 0.0)
            k = rampa(pel.t, 5.0)
            barra_r.become(Rectangle(width=0.55, height=max(sube_r * KB, 0.01)).set_fill(est.acento, 0.95 * k).set_stroke(width=0).move_to([BX - 0.7, BY + max(sube_r * KB, 0.01) / 2, 0]).set_z_index(6))
            barra_c.become(Rectangle(width=0.55, height=max(sube_c * KB, 0.01)).set_fill(est.acento2, 0.95 * k).set_stroke(width=0).move_to([BX + 0.7, BY + max(sube_c * KB, 0.01) / 2, 0]).set_z_index(6))
        barra_r.add_updater(medir)
        self.add(barra_r, barra_c)
        self.add(aparece(texto(est, "rueda", 32, est.acento, "cuerpo", "SEMIBOLD").move_to([BX - 0.7, BY - 0.45, 0]).set_z_index(9), pel, 5.0))
        self.add(aparece(texto(est, "cuerpo", 32, est.acento2, "cuerpo", "SEMIBOLD").move_to([BX + 0.7, BY - 0.45, 0]).set_z_index(9), pel, 5.0))
        self.add(aparece(texto(est, "lo que sube", 34, est.tenue).move_to([BX, BY + 3.55, 0]).set_z_index(9), pel, 5.0))
        # el peso se reparte en seis partes iguales
        pastel = VGroup(*[Sector(radius=1.35, angle=TAU / 6 - 0.06, start_angle=k * TAU / 6).set_fill(est.acento2, 0.85).set_stroke(est.fondo, 3) for k in range(6)]).move_to([-4.7, 3.4, 0]).set_z_index(6)
        self.add(aparece(pastel, pel, 12.8))
        self.add(aparece(texto(est, "el peso, en\n6 partes iguales", 40, est.tinta, "cuerpo", "SEMIBOLD", ancho_max=4.8).move_to([-0.55, 3.4, 0]).set_z_index(9), pel, 13.2))

        leyendas(self, est, pel, n, [
            ("Una suspensión que se adapta a las rocas", "balancines que giran: cada rueda sube sola"),
            ("Si una rueda sube 3, el cuerpo sube solo 1", "el robot sigue casi nivelado y no vuelca"),
            ("Seis ruedas, el peso en seis partes iguales", "así ninguna rueda se hunde ni se despega")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 2 · Gira igual, avanza menos (deslizamiento) ════════════════════════════════════════════════════════════════════════

class ReelRobPatina(Scene):
    VAR = 1

    def construct(self):
        n = "ReelRobPatina"; TB = DR.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Gira igual,\navanza menos", self.VAR, chip_txt="Ilustración", **SERIE)
        R, X0, VUELTAS = 0.85, -5.3, 2.0
        D = 2 * PI * R * VUELTAS
        T0, T1 = 1.2, 11.0
        th = lambda: VUELTAS * TAU * float(np.clip((pel.t - T0) / (T1 - T0), 0, 1))
        carriles = [(2.9, "suelo firme", 0.96, est.acento2), (-2.3, "arena suelta", 0.62, est.calido)]
        for k, (y, nombre, f, col) in enumerate(carriles):
            self.add(Line([-6.5, y - R, 0], [6.5, y - R, 0], stroke_width=5, color=est.tenue).set_z_index(4))
            for m_ in range(0, 14):
                self.add(Line([-6.5 + m_, y - R, 0], [-6.5 + m_, y - R - 0.2, 0], stroke_width=3, color=est.tenue).set_z_index(4))
            self.add(aparece(texto(est, nombre, 40, col, "cuerpo", "SEMIBOLD").move_to([-3.6, y + 1.75, 0]).set_z_index(9), pel, 0.5))
            w = rueda(est, [X0, y, 0], R, 0, col)
            w.add_updater(lambda m, y=y, f=f, col=col: m.become(rueda(est, [X0 + f * R * th(), y, 0], R, -th(), col)))
            self.add(w)
            meta = VGroup(Line([X0 + D, y - R, 0], [X0 + D, y + 1.3, 0], stroke_width=3, color=est.tinta), Triangle().scale(0.2).rotate(-PI / 2).set_fill(est.tinta, 1).set_stroke(width=0).move_to([X0 + D + 0.2, y + 1.15, 0])).set_z_index(5)
            self.add(aparece(meta, pel, 0.8))
            marca = Dot([X0, y + 0.0, 0], radius=0.0)
            if f < 0.9:                                                 # arena: la rueda lanza partículas hacia atrás
                for j in range(14):
                    d_ = punto(col, 0.045)

                    def volar(m, j=j, y=y, f=f):
                        e = ((pel.t - T0) * 1.6 + j / 14) % 1.0
                        activo = rampa(pel.t, T0 + 0.3, 0.3) * (1 - rampa(pel.t, T1, 0.4))
                        x = X0 + f * R * th() - 0.2 - 1.6 * e
                        yy = y - R + 0.15 + 1.1 * e - 1.4 * e * e
                        fundir(m.move_to([x, yy, 0]), activo * (1 - e))
                    d_.add_updater(volar)
                    self.add(d_)
        self.add(Viva(est, lambda: f"{th() / TAU:.1f} vueltas", [3.5, 4.3, 0], 52, est.tinta, f_op=lambda: rampa(pel.t, 1.0)))
        self.add(aparece(texto(est, "las dos ruedas giran lo mismo", 36, est.tenue, ancho_max=11.5).move_to([0, 5.1, 0]).set_z_index(9), pel, 1.0))
        self.add(aparece(texto(est, "≈ 10 de 10 m", 50, est.acento2, "cuerpo", "SEMIBOLD").move_to([1.0, 0.5, 0]).set_z_index(9), pel, 11.0))
        self.add(aparece(texto(est, "6 de 10 m", 50, est.calido, "cuerpo", "SEMIBOLD").move_to([1.0, -4.5, 0]).set_z_index(9), pel, 11.0))

        leyendas(self, est, pel, n, [
            ("La rueda gira… pero el suelo cede", "en arena suelta se hunde y resbala"),
            ("Gira lo mismo, pero avanza menos", "a esa diferencia se le llama deslizamiento"),
            ("Medirlo le dice al robot cuánto agarre hay", "y le avisa cuándo está por atascarse")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 3 · La misma orden en cinco mundos ════════════════════════════════════════════════════════════════════════════════

class ReelRobMundos(Scene):
    VAR = 2

    def construct(self):
        n = "ReelRobMundos"; TB = DR.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Misma orden,\ncinco mundos", self.VAR, chip_txt="En simulación", **SERIE)
        colores = {"Luna": "#C9CED6", "Marte": "#E2603B", "Tierra": AZUL, "Titán": "#E8B25A", "Ceres": "#9A8F86"}
        X0, X1 = -2.8, 4.4
        ancho = X1 - X0
        for k, (nombre, m_, g) in enumerate(DR.MUNDOS):
            y = 3.9 - 1.8 * k
            t0 = 0.6 + 0.35 * k
            planeta = Circle(radius=0.55).set_fill(colores[nombre], 1).set_stroke(width=0).move_to([-5.6, y, 0]).set_z_index(8)
            self.add(aparece(planeta, pel, t0))
            self.add(aparece(texto(est, nombre, 38, est.tinta, "cuerpo", "SEMIBOLD").move_to([-4.85, y, 0], aligned_edge=LEFT).set_z_index(9), pel, t0))
            self.add(Rectangle(width=ancho, height=0.62).set_fill(est.linea, 0.5).set_stroke(width=0).move_to([X0 + ancho / 2, y, 0]).set_z_index(3))
            b = Rectangle(width=0.01, height=0.62).set_z_index(5)
            b.add_updater(lambda m, y=y, m_=m_, nombre=nombre: m.become(
                Rectangle(width=max(ancho * m_ / DR.DISTANCIA_IDEAL * rampa(pel.t, 2.0, 3.2), 0.01), height=0.62)
                .set_fill(ROJO if nombre == "Ceres" else est.acento, 0.95 * rampa(pel.t, 1.8)).set_stroke(width=0)
                .move_to([X0, y, 0], aligned_edge=LEFT).set_z_index(5)))
            self.add(b)
            self.add(aparece(texto(est, f"{m_ + 1e-9:.1f} m", 38, est.tinta, "cifra", "SEMIBOLD").move_to([X1 + 0.3, y, 0], aligned_edge=LEFT).set_z_index(9), pel, 5.2))
        self.add(aparece(DashedLine([X1, 4.7, 0], [X1, -3.7, 0], stroke_width=3, color=est.tinta, dash_length=0.18).set_z_index(6), pel, 1.0))
        self.add(aparece(texto(est, "10 m: lo pedido", 32, est.tenue).move_to([X1 - 1.1, -4.3, 0]).set_z_index(9), pel, 1.0))
        self.add(aparece(texto(est, "poca gravedad: casi sin agarre", 34, ROJO, "cuerpo", "SEMIBOLD", ancho_max=8.0).move_to([-0.3, -5.1, 0]).set_z_index(9), pel, 12.6))

        leyendas(self, est, pel, n, [
            ("La orden es la misma: avanzar 10 metros", "el mismo robot en la Luna, Marte, la Tierra…"),
            ("Pero en cada mundo avanza distinto", "el suelo y la gravedad cambian el agarre"),
            ("Ceres apenas avanza 4 de 10 metros", "con tan poca gravedad, las ruedas casi no agarran")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 4 · ¿Cómo elige un robot por dónde ir? (planificación de ruta) ═══════════════════════════════════════════════════════

def buscar_ruta(costo, inicio, meta):
    """A* de 8 vecinos sobre `costo` (inf = intransitable). Devuelve (orden_de_expansion, ruta)."""
    h = lambda a: np.hypot(a[0] - meta[0], a[1] - meta[1])
    abierto = [(h(inicio), 0.0, inicio)]
    g = {inicio: 0.0}; padre = {}; orden = []; cerrado = set()
    while abierto:
        _, gc, c = heapq.heappop(abierto)
        if c in cerrado:
            continue
        cerrado.add(c); orden.append(c)
        if c == meta:
            break
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                v = (c[0] + dx, c[1] + dy)
                if not (0 <= v[0] < costo.shape[0] and 0 <= v[1] < costo.shape[1]) or not np.isfinite(costo[v]):
                    continue
                gn = gc + np.hypot(dx, dy) * costo[v]
                if gn < g.get(v, 1e9):
                    g[v] = gn; padre[v] = c
                    heapq.heappush(abierto, (gn + h(v), gn, v))
    ruta, c = [meta], meta
    while c in padre:
        c = padre[c]; ruta.append(c)
    return orden, ruta[::-1]


class ReelRobRuta(Scene):
    VAR = 0

    def construct(self):
        n = "ReelRobRuta"; TB = DR.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Por dónde\nse va?", self.VAR, chip_txt="Ilustración", **SERIE)
        NX, NY, L = 20, 15, 0.66
        X0, Y0 = -NX * L / 2, -4.9
        costo = np.ones((NX, NY))
        ix, iy = np.mgrid[0:NX, 0:NY]
        d_colina = np.hypot(ix - 10.0, iy - 7.0)
        costo += np.clip(5.2 - d_colina, 0, None) * 1.1
        costo[d_colina < 3.1] = np.inf
        rng = np.random.default_rng(5)
        for _ in range(9):
            r = (int(rng.integers(0, NX)), int(rng.integers(0, NY)))
            if np.hypot(r[0] - 10, r[1] - 7) > 4.2 and r not in ((1, 1), (18, 13)):
                costo[r] = np.inf
        inicio, meta = (1, 1), (18, 13)
        orden, ruta = buscar_ruta(costo, inicio, meta)
        cel = lambda c: np.array([X0 + (c[0] + 0.5) * L, Y0 + (c[1] + 0.5) * L, 0])
        self.add(panel(est, X0 - 0.2, -X0 + 0.2, Y0 - 0.2, Y0 + NY * L + 0.2, 0.85))
        suma = VGroup()
        for i in range(NX):
            for j in range(NY):
                c = costo[i, j]
                if np.isfinite(c):
                    op = 0.05 + 0.22 * min(c - 1, 5) / 5
                    col = est.acento
                else:
                    op, col = 0.85, est.tenue
                sq = Square(L * 0.96).set_fill(col, op).set_stroke(width=0).move_to(cel((i, j))).set_z_index(3)
                suma.add(sq)
        self.add(aparece(suma, pel, 0.4))
        self.add(aparece(texto(est, "colina", 34, est.tinta, "cuerpo", "SEMIBOLD").move_to(cel((10, 7))).set_z_index(9), pel, 1.0))
        # exploración
        T0, T1 = 3.5, 9.5
        pos = {c: k for k, c in enumerate(orden)}
        for k, c in enumerate(orden):
            sq = Square(L * 0.96).set_fill(est.acento2, 0.0).set_stroke(width=0).move_to(cel(c)).set_z_index(4)
            t_k = T0 + (T1 - T0) * k / max(len(orden) - 1, 1)
            sq.add_updater(lambda m, t_k=t_k: m.set_fill(est.acento2, 0.5 * rampa(pel.t, t_k, 0.25) * (1 - 0.6 * rampa(pel.t, T1 + 0.5, 0.8))))
            self.add(sq)
        recta = DashedLine(cel(inicio), cel(meta), stroke_width=4, color=ROJO, dash_length=0.2).set_z_index(6)
        self.add(aparece(recta, pel, 1.8, hasta=3.8))
        self.add(aparece(texto(est, "el camino recto: imposible", 34, ROJO, "cuerpo", "SEMIBOLD").move_to([-1.6, 5.5, 0]).set_z_index(9), pel, 2.0, hasta=3.8))
        camino = polilinea([cel(c) for c in ruta], color=est.calido, width=7, opacity=0.95).set_z_index(7)
        self.add(aparece(camino, pel, T1 + 0.5, 0.8))
        self.add(aparece(VGroup(Circle(radius=0.3).set_fill(VERDE, 0.85).set_stroke(est.tinta, 3), texto(est, "meta", 30, est.fondo, "cuerpo", "SEMIBOLD")).move_to(cel(meta)).set_z_index(9), pel, 0.6))
        rover = VGroup(Square(0.55).set_fill(est.acento, 1).set_stroke(est.tinta, 3), Triangle().scale(0.17).rotate(-PI / 2).set_fill(est.tinta, 1).set_stroke(width=0).shift(RIGHT * 0.1)).set_z_index(10)
        seg = np.cumsum([0] + [np.linalg.norm(cel(ruta[i + 1]) - cel(ruta[i])) for i in range(len(ruta) - 1)])

        def andar(m):
            u = float(np.clip((pel.t - 12.8) / 5.5, 0, 1)) * seg[-1]
            i = int(np.clip(np.searchsorted(seg, u) - 1, 0, len(ruta) - 2))
            f = (u - seg[i]) / max(seg[i + 1] - seg[i], 1e-6)
            m.move_to(cel(ruta[i]) * (1 - f) + cel(ruta[i + 1]) * f)
            fundir(m, rampa(pel.t, 12.6, 0.3))
        rover.add_updater(andar)
        fundir(rover, 0)
        self.add(rover)

        leyendas(self, est, pel, n, [
            ("Antes de moverse, el robot piensa la ruta", "el mapa tiene colinas, rocas y pendientes"),
            ("Prueba caminos y los va descartando", "cada cuadro tiene un costo: subir cansa más"),
            ("Elige el más barato que no sea peligroso", "rodea la colina en vez de cruzarla")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 5 · Un robot que sabe cuándo parar (alarmas) ═══════════════════════════════════════════════════════════════════════

class ReelRobAlarmas(Scene):
    VAR = 1

    def construct(self):
        n = "ReelRobAlarmas"; TB = DR.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Un robot que sabe\ncuándo parar", self.VAR, chip_txt="En simulación", **SERIE)
        ang = lambda: 38.0 * float(np.clip((pel.t - 1.5) / 9.0, 0, 1))          # inclinación de la rampa (°)
        alarma = lambda: ang() >= DR.ALARMA_PENDIENTE_DEG
        sale = lambda: 1 - rampa(pel.t, 13.0, 0.5)                              # el reloj se retira para dar paso a la comparación
        C, RD = np.array([0.0, 2.0, 0]), 2.5
        a2s = lambda a: PI - (a / 40.0) * PI                                      # 0° a la izquierda, 40° a la derecha (radianes)
        dial = VGroup()
        for a0, a1, col in ((0, DR.ALARMA_PENDIENTE_DEG, VERDE), (DR.ALARMA_PENDIENTE_DEG, DR.ALARMA_VUELCO_DEG, est.calido), (DR.ALARMA_VUELCO_DEG, 40, ROJO)):
            dial.add(Arc(radius=RD, start_angle=a2s(a1), angle=a2s(a0) - a2s(a1), stroke_width=22, color=col, arc_center=C).set_z_index(4))
        for a in (0, 10, 20, 30, 40):
            dial.add(texto(est, f"{a}°", 30, est.tenue).move_to(C + (RD + 0.55) * np.array([np.cos(a2s(a)), np.sin(a2s(a)), 0])).set_z_index(9))
        dial.add(Dot(C, radius=0.2, color=est.tinta).set_z_index(9))
        self.add(aparece(dial, pel, 0.4, hasta=13.0))
        aguja = Line(C, C + RD * 0.85 * RIGHT, stroke_width=8, color=est.tinta).set_z_index(8)
        aguja.add_updater(lambda m: m.put_start_and_end_on(C, C + RD * 0.85 * np.array([np.cos(a2s(ang())), np.sin(a2s(ang())), 0])).set_stroke(opacity=rampa(pel.t, 0.6) * sale()))
        self.add(aguja)
        self.add(Viva(est, lambda: f"{ang():.0f}°", [0, 0.55, 0], 80, est.tinta, f_op=lambda: rampa(pel.t, 1.0) * sale()))
        etq = texto(est, "¡PARAR!", 54, ROJO, "titulo", "BOLD").move_to([-4.9, 3.0, 0]).set_z_index(10)
        etq.add_updater(lambda m: fundir(m, (rampa(pel.t, 8.6, 0.2) * (0.6 + 0.4 * np.sin(8 * pel.t)) if alarma() else 0) * sale()))
        fundir(etq, 0)
        self.add(etq)
        # rampa y robot (la rampa gira alrededor de su extremo izquierdo)
        PX, PY, LR = -6.3, -4.9, 9.4
        rampa_m = Polygon(ORIGIN, RIGHT, UP).set_z_index(3)
        rampa_m.add_updater(lambda m: m.become(Polygon([PX, PY, 0], [PX + LR * np.cos(np.radians(ang())), PY + LR * np.sin(np.radians(ang())), 0], [PX + LR * np.cos(np.radians(ang())), PY, 0])
                                               .set_fill(est.linea, 0.9).set_stroke(est.tenue, 4).set_z_index(3)))
        self.add(rampa_m)
        rv = VGroup(Rectangle(width=1.6, height=0.55).set_fill(est.acento, 1).set_stroke(est.tinta, 3), *[Circle(radius=0.22).set_fill(est.fondo, 1).set_stroke(est.tinta, 3).move_to([x, -0.45, 0]) for x in (-0.55, 0, 0.55)]).set_z_index(9)
        robot = VGroup().set_z_index(9)

        def colocar(m):
            a = np.radians(ang())
            avance = 1.2 + 5.2 * float(np.clip((min(pel.t, 8.3) - 1.5) / 6.8, 0, 1))
            g = rv.copy().rotate(a)
            g.move_to(np.array([PX + avance * np.cos(a), PY + avance * np.sin(a), 0]) + np.array([-np.sin(a), np.cos(a), 0]) * 0.7)
            m.become(g.set_z_index(9))
            fundir(m, rampa(pel.t, 0.8))
        robot.add_updater(colocar)
        self.add(robot)
        # comparación final: distancia con y sin alarmas locales (misma escala)
        W = 7.0
        w_sin = W * DR.SIN_ALARMAS_MARTE / DR.OPERACION_MARTE["plan de sol"]
        comp = VGroup(texto(est, "con alarmas locales", 40, VERDE, "cuerpo", "SEMIBOLD").move_to([-6.4, 4.7, 0], aligned_edge=LEFT),
                      Rectangle(width=W, height=0.6).set_fill(VERDE, 0.9).set_stroke(width=0).move_to([-6.4 + W / 2, 3.85, 0]),
                      texto(est, "sin alarmas", 40, ROJO, "cuerpo", "SEMIBOLD").move_to([-6.4, 2.75, 0], aligned_edge=LEFT),
                      Rectangle(width=w_sin, height=0.6).set_fill(ROJO, 0.9).set_stroke(width=0).move_to([-6.4 + w_sin / 2, 1.9, 0]),
                      texto(est, "≈ 6 veces más lejos", 40, est.tinta, "cuerpo", "SEMIBOLD").move_to([-6.4 + W + 0.1, 3.85, 0], aligned_edge=LEFT)).set_z_index(9)
        comp[4].scale_to_fit_width(min(comp[4].width, 5.8)).move_to([6.6 - comp[4].width / 2, 2.1, 0])
        self.add(aparece(comp, pel, 13.5))

        leyendas(self, est, pel, n, [
            ("Mide su propia inclinación", "si sube un cerro, sabe cuánto se inclina"),
            ("Pasado el límite, se detiene sola", "antes de volcar, sin esperar órdenes de la Tierra"),
            ("Con alarmas avanza unas 6 veces más lejos", "parar a tiempo vale más que decidir bien")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 6 · ¿Por qué no se maneja con joystick? (retardo de la luz) ═════════════════════════════════════════════════════════

class ReelRobRetardo(Scene):
    VAR = 2

    def construct(self):
        n = "ReelRobRetardo"; TB = DR.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Por qué no se maneja\ncon joystick?", self.VAR, chip_txt="Escala de tiempo exagerada", **SERIE)
        XT, XL, XM = -5.4, 0.8, 5.4
        Y1, Y2 = 3.0, -1.4
        tierra = lambda y: VGroup(Circle(radius=0.75).set_fill(est.mezcla(est.fondo, AZUL, 0.62), 1).set_stroke(AZUL, 4), texto(est, "Tierra", 28, est.tinta, "cuerpo", "SEMIBOLD").shift(DOWN * 1.2)).move_to([XT, y, 0]).set_z_index(8)
        luna = VGroup(Circle(radius=0.5).set_fill("#C9CED6", 1).set_stroke(width=0), texto(est, "Luna", 28, est.tinta, "cuerpo", "SEMIBOLD").shift(DOWN * 0.95)).move_to([XL, Y1, 0]).set_z_index(8)
        marte = VGroup(Circle(radius=0.6).set_fill("#E2603B", 1).set_stroke(width=0), texto(est, "Marte", 28, est.tinta, "cuerpo", "SEMIBOLD").shift(DOWN * 1.05)).move_to([XM, Y2, 0]).set_z_index(8)
        self.add(aparece(tierra(Y1), pel, 0.3), aparece(tierra(Y2), pel, 0.3), aparece(luna, pel, 0.3), aparece(marte, pel, 0.3))
        for (x0, x1, y) in ((XT + 0.9, XL - 0.7, Y1), (XT + 0.9, XM - 0.8, Y2)):
            self.add(DashedLine([x0, y, 0], [x1, y, 0], stroke_width=3, color=est.tenue, dash_length=0.2).set_z_index(3))
        pulso = lambda y, x0, x1, ta, tb, col: self._pulso(est, pel, y, x0, x1, ta, tb, col)
        self.add(pulso(Y1, XT + 0.9, XL - 0.6, 1.2, 2.4, est.acento))
        self.add(pulso(Y1, XL - 0.6, XT + 0.9, 3.0, 4.2, est.acento2))
        self.add(Viva(est, lambda: "ida: 1 segundo" if pel.t > 2.4 else " ", [XL - 0.8, Y1 + 1.15, 0], 42, est.acento, f_op=lambda: rampa(pel.t, 2.4)))
        self.add(pulso(Y2, XT + 0.9, XM - 0.8, 6.0, 13.0, est.acento))
        reloj = lambda: int(round(11 * float(np.clip((pel.t - 6.0) / 7.0, 0, 1)))) if pel.t < 13.0 else 11
        self.add(Viva(est, lambda: f"{reloj()} min" if pel.t > 6.0 else " ", [0.3, Y2 + 1.25, 0], 64, est.calido, f_op=lambda: rampa(pel.t, 6.0)))
        self.add(aparece(texto(est, "una orden tarda en llegar", 34, est.tenue, ancho_max=9.0).move_to([0.3, Y2 + 2.05, 0]).set_z_index(9), pel, 6.2))
        self.add(pulso(Y2, XM - 0.8, XT + 0.9, 14.0, 21.0, est.acento2))
        self.add(Viva(est, lambda: "otros 11 min de vuelta" if pel.t > 14.0 else " ", [0.3, Y2 - 1.75, 0], 40, est.acento2, rol="cuerpo", f_op=lambda: rampa(pel.t, 14.0)))
        joy = VGroup(Rectangle(width=1.6, height=0.4).set_fill(est.linea, 1).set_stroke(est.tinta, 3), Line(ORIGIN, UP * 0.8, stroke_width=8, color=est.tinta).shift(UP * 0.2), Circle(radius=0.2).set_fill(ROJO, 1).set_stroke(width=0).shift(UP * 1.1)).move_to([XT, -4.4, 0]).set_z_index(8)
        self.add(aparece(joy, pel, 12.6))
        self.add(aparece(VGroup(Line([-0.9, -0.9, 0], [0.9, 0.9, 0], stroke_width=9, color=ROJO), Line([-0.9, 0.9, 0], [0.9, -0.9, 0], stroke_width=9, color=ROJO)).move_to([XT, -4.2, 0]).set_z_index(10), pel, 13.0))
        self.add(aparece(texto(est, "no se puede manejar en vivo", 36, est.tinta, "cuerpo", "SEMIBOLD", ancho_max=9.0).move_to([1.4, -4.4, 0]).set_z_index(9), pel, 13.0))

        leyendas(self, est, pel, n, [
            ("A la Luna, una orden tarda 1 segundo", "la luz viaja muy rápido, pero no es infinita"),
            ("A Marte tarda minutos: de 3 a 22", "en esta fecha, unos 11 minutos de ida"),
            ("Un joystick no sirve con tanta espera", "el robot tiene que decidir solo")])
        cerrar_serie(self, est, pel, self.VAR)

    def _pulso(self, est, pel, y, x0, x1, ta, tb, col):
        p = punto(col, 0.13)
        p.add_updater(lambda m: fundir(m.move_to([x0 + (x1 - x0) * float(np.clip((pel.t - ta) / (tb - ta), 0, 1)), y, 0]), rampa(pel.t, ta, 0.1) * (1 - rampa(pel.t, tb, 0.2))))
        fundir(p, 0)
        return p


# ══ 7 · Autonomía: cuánto avanza en un día ═══════════════════════════════════════════════════════════════════════════════

class ReelRobAutonomo(Scene):
    VAR = 0

    def construct(self):
        n = "ReelRobAutonomo"; TB = DR.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Cuánto avanza\nen un día?", self.VAR, chip_txt="Simulación · Marte", **SERIE)
        X0, X1 = -2.4, 6.2
        carriles = [("manejado desde\nla Tierra", DR.OPERACION_MARTE["teleoperado"], "≈ 10 m", est.tenue),
                    ("por metas", DR.OPERACION_MARTE["por metas"], "≈ 80 m", est.acento2),
                    ("solo,\nsin alarmas", DR.SIN_ALARMAS_MARTE, "≈ 300 m", est.calido),
                    ("solo,\ncon alarmas", DR.OPERACION_MARTE["plan de sol"], "≈ 2 km", VERDE)]
        orden_t = [1.0, 3.2, 8.2, 5.4]
        T0, T1 = 2.0, 13.0
        for k, ((nombre, m_, et, col), tl) in enumerate(zip(carriles, orden_t)):
            y = 3.8 - 2.4 * k
            self.add(aparece(texto(est, nombre, 36, col, "cuerpo", "SEMIBOLD", ancho_max=3.9).move_to([-6.5, y, 0], aligned_edge=LEFT).set_z_index(9), pel, tl))
            self.add(aparece(Line([X0, y - 0.45, 0], [X1, y - 0.45, 0], stroke_width=4, color=est.linea).set_z_index(3), pel, tl))
            tope = X0 + (X1 - X0) * m_ / DR.OPERACION_MARTE["plan de sol"]
            d = Dot(radius=0.2, color=col).set_z_index(9)
            d.add_updater(lambda m, y=y, tope=tope, tl=tl: fundir(m.move_to([X0 + (tope - X0) * float(np.clip((pel.t - T0) / (T1 - T0), 0, 1)), y - 0.2, 0]), rampa(pel.t, tl, 0.4)))
            fundir(d, 0)
            estela = Line(LEFT, RIGHT, stroke_width=9, color=col).set_z_index(5)
            estela.add_updater(lambda m, y=y, tope=tope, col=col, tl=tl: m.put_start_and_end_on([X0, y - 0.2, 0], [X0 + max(tope - X0, 0.0) * float(np.clip((pel.t - T0) / (T1 - T0), 0, 1)) + 0.001, y - 0.2, 0]).set_stroke(opacity=0.8 * rampa(pel.t, tl, 0.4)))
            self.add(estela, d)
            self.add(aparece(texto(est, et, 44, col, "cifra", "SEMIBOLD").move_to([X0 + max(tope - X0, 0) + 0.45, y + 0.4, 0], aligned_edge=LEFT if tope < 4 else RIGHT).set_z_index(9), pel, T1 - 0.5))
        self.add(aparece(texto(est, "en un día marciano", 40, est.tenue).move_to([0.2, -5.2, 0]).set_z_index(9), pel, 1.0))

        leyendas(self, est, pel, n, [
            ("Manejarlo desde la Tierra: unos metros", "cada orden espera al satélite y a la luz"),
            ("Decidir solo cambia el día por completo", "pero sin cuidarse, se atasca o vuelca"),
            ("Solo y con alarmas: unos 2 kilómetros", "autonomía, más sentido común de seguridad")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 8 · Mejoró… hasta que lo probamos con casos nuevos ═════════════════════════════════════════════════════════════════

class ReelRobValidacion(Scene):
    VAR = 1

    def construct(self):
        n = "ReelRobValidacion"; TB = DR.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Mejoró, hasta que\nlo pusimos a prueba", self.VAR, chip_txt="En simulación", **SERIE)
        rng = np.random.default_rng(11)
        rango = rng.permutation(100)
        cuentas = {"izq": (87, 94, 94), "der": (83, 69, 93)}               # casos conocidos · casos nuevos · corregida (por 100)
        T = (0.0, 6.5, 13.0)                                               # instantes de cambio de fase
        fase = lambda: sum(pel.t >= x for x in T[1:])
        for lado, x0, nombre, col in (("izq", -3.4, "versión simple", est.acento2), ("der", 3.4, "versión «afinada»", est.acento)):
            self.add(aparece(texto(est, nombre, 36, col, "cuerpo", "SEMIBOLD", ancho_max=5.6).move_to([x0, 4.9, 0]).set_z_index(9), pel, 0.4))
            for k in range(100):
                i, j = divmod(k, 10)
                p = np.array([x0 - 2.25 + 0.5 * j, 3.8 - 0.5 * i, 0])
                d = Circle(radius=0.19).set_z_index(8)
                d.add_updater(lambda m, k=k, lado=lado, p=p: m.become(Circle(radius=0.19).move_to(p).set_fill(VERDE if rango[k] < cuentas[lado][fase()] else ROJO, 1).set_stroke(width=0).set_opacity(rampa(pel.t, 0.5 + 0.008 * k, 0.3)).set_z_index(8)))
                self.add(d)
            self.add(Viva(est, lambda lado=lado: f"{cuentas[lado][fase()]} de 100", [x0, -1.9, 0], 62, VERDE if lado == "izq" else (est.tinta), f_op=lambda: rampa(pel.t, 1.5)))
        etiquetas = ["casos conocidos", "casos nuevos", "se corrigió la causa"]
        self.add(Viva(est, lambda: etiquetas[fase()], [0, -3.2, 0], 46, est.calido, rol="cuerpo", f_op=lambda: rampa(pel.t, 1.5)))
        self.add(aparece(texto(est, "una alarma demasiado nerviosa:\nse detenía ante cualquier borde", 40, est.tinta, "cuerpo", "MEDIUM", ancho_max=11.5).move_to([0, -4.6, 0]).set_z_index(9), pel, 13.5))
        for x in (-3.4, 3.4):
            self.add(aparece(Rectangle(width=5.4, height=5.4).set_fill(est.fondo, 0.5).set_stroke(est.linea, 2).move_to([x, 1.55, 0]).set_z_index(2), pel, 0.3))

        leyendas(self, est, pel, n, [
            ("Con los casos de siempre, casi igual", "la versión «afinada» y la simple rinden parecido"),
            ("Con casos nuevos, empeoró: de 94 a 69", "lo afinado solo funcionaba donde se afinó"),
            ("Encontramos la causa y quedó en 93", "probar con casos nuevos evitó una falsa mejora")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 9 · Un robot es una conversación (ROS 2) ═════════════════════════════════════════════════════════════════════════════

class ReelRobROS(Scene):
    VAR = 2

    def construct(self):
        n = "ReelRobROS"; TB = DR.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Un robot es\nuna conversación", self.VAR, chip_txt="Cómo funciona", **SERIE)
        nodos = {"cuerpo": (np.array([-3.6, 3.6, 0]), "el cuerpo", "rover_dinamica", est.acento), "cerebro": (np.array([3.6, 3.6, 0]), "el cerebro", "rover_navegador", est.acento2),
                 "radio": (np.array([3.6, -0.9, 0]), "la radio", "rover_enlace", est.calido), "tierra": (np.array([-3.6, -0.9, 0]), "la Tierra", "operador", VERDE)}
        t_nodo = {"cuerpo": 0.6, "cerebro": 1.6, "radio": 7.0, "tierra": 7.6}
        cajas = {}
        for k, (p, nombre, tecnico, col) in nodos.items():
            g = VGroup(RoundedRectangle(corner_radius=0.3, width=5.2, height=2.6).set_fill(col, 0.14).set_stroke(col, 4),
                       texto(est, nombre, 56, est.tinta, "cuerpo", "SEMIBOLD").shift(UP * 0.35), texto(est, tecnico, 32, est.tenue, "cuerpo", "MEDIUM").shift(DOWN * 0.7)).move_to(p).set_z_index(8)
            cajas[k] = g
            self.add(aparece(g, pel, t_nodo[k]))
        flechas = [("cuerpo", "cerebro", 0.6, "estado", 3.0, est.acento), ("cerebro", "cuerpo", 0.6, "orden", 4.6, est.acento2),
                   ("tierra", "radio", 0.0, "órdenes", 8.6, VERDE), ("radio", "cerebro", 0.0, "", 9.4, est.calido)]
        for a, b, off, rot, t0, col in flechas:
            pa, pb = nodos[a][0], nodos[b][0]
            d = (pb - pa); d = d / np.linalg.norm(d)
            perp = np.array([-d[1], d[0], 0]) * off
            s, e = pa + d * 2.65 + perp, pb - d * 2.65 + perp
            if abs(d[0]) < 0.1:
                s, e = pa + d * 1.45 + perp, pb - d * 1.45 + perp
            self.add(aparece(Arrow(s, e, buff=0, stroke_width=6, color=col, max_tip_length_to_length_ratio=0.12).set_z_index(6), pel, t0))
            if rot:
                self.add(aparece(texto(est, rot, 34, col, "cuerpo", "SEMIBOLD").move_to((s + e) / 2 + (perp / max(np.linalg.norm(perp), 1e-9) if off else UP) * 0.55).set_z_index(9), pel, t0))
            p = punto(col, 0.11)
            p.add_updater(lambda m, s=s, e=e, t0=t0, col=col: fundir(m.move_to(s + (e - s) * (((pel.t - t0) % 1.8) / 1.8)), rampa(pel.t, t0 + 0.2, 0.3)))
            fundir(p, 0)
            self.add(p)
        # reloj común
        RC = np.array([-4.2, -4.3, 0])
        reloj = VGroup(Circle(radius=1.1).set_fill(est.fondo, 1).set_stroke(est.tinta, 4), Dot(radius=0.07, color=est.tinta)).move_to(RC).set_z_index(8)
        mano = Line(ORIGIN, UP * 0.8, stroke_width=7, color=est.calido).set_z_index(9)
        mano.add_updater(lambda m: m.put_start_and_end_on(RC, RC + 0.8 * np.array([np.sin(TAU * pel.t / 2.0), np.cos(TAU * pel.t / 2.0), 0])))
        self.add(aparece(reloj, pel, 13.5), aparece(mano, pel, 13.5))
        self.add(aparece(texto(est, "un reloj común:\nmismo resultado, siempre", 40, est.tinta, "cuerpo", "SEMIBOLD", ancho_max=7.6).move_to(RC + RIGHT * 5.0).set_z_index(9), pel, 14.0))

        leyendas(self, est, pel, n, [
            ("Un robot no es un solo programa", "es un cuerpo, un cerebro y una radio que se hablan"),
            ("Se mandan mensajes: «estado» y «orden»", "así cada pieza puede cambiarse sin romper las demás"),
            ("Esto es ROS 2, el idioma común de los robots", "con y sin ROS, el resultado fue idéntico, byte a byte")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 10 · El mismo cerebro, otro cuerpo (ros2_control) ═══════════════════════════════════════════════════════════════════

class ReelRobCerebro(Scene):
    VAR = 0

    def construct(self):
        n = "ReelRobCerebro"; TB = DR.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "El mismo cerebro,\notro cuerpo", self.VAR, chip_txt="Hardware real: pendiente", **SERIE)
        cerebro = VGroup(RoundedRectangle(corner_radius=0.3, width=7.2, height=1.7).set_fill(est.acento, 0.16).set_stroke(est.acento, 4),
                         texto(est, "controlador", 48, est.tinta, "cuerpo", "SEMIBOLD").shift(UP * 0.25), texto(est, "decide cómo mover la antena", 30, est.tenue).shift(DOWN * 0.5)).move_to([0, 3.6, 0]).set_z_index(8)
        self.add(aparece(cerebro, pel, 0.4))
        XS = (-4.5, 0.0, 4.5)
        nombres = (("simulación", est.acento2, True), ("simulador 3D", est.calido, True), ("montura real", est.tenue, False))
        fases = ((1.0, 6.2), (6.2, 12.0), (12.0, 17.0))
        for x, (nom, col, real), (a, b) in zip(XS, nombres, fases):
            base = VGroup(Polygon([-1.35, -1.05, 0], [1.35, -1.05, 0], [0.8, 0.08, 0], [-0.8, 0.08, 0]).set_fill(est.linea, 1).set_stroke(col, 5), Line([0, 0.08, 0], [0, 0.85, 0], stroke_width=9, color=col)).move_to([x, -0.9, 0]).set_z_index(7)
            plato = Arc(radius=1.25, start_angle=PI * 0.15, angle=PI * 0.7, stroke_width=11, color=col, arc_center=[x, 0.2, 0]).set_z_index(8)
            plato.add_updater(lambda m, x=x, a=a, b=b, col=col: m.become(Arc(radius=1.25, start_angle=PI * 0.15 + (0.7 * np.sin(1.4 * pel.t) if a <= pel.t < b else 0.0), angle=PI * 0.7, stroke_width=11, color=col, arc_center=[x, 0.2, 0]).set_z_index(8)))
            if not real:
                base.set_stroke(opacity=0.5)
                self.add(aparece(DashedVMobject(RoundedRectangle(corner_radius=0.3, width=4.2, height=4.4).move_to([x, -0.45, 0]).set_stroke(col, 4), num_dashes=44).set_z_index(5), pel, 0.8))
            self.add(aparece(base, pel, 0.8), aparece(plato, pel, 0.8))
            self.add(aparece(texto(est, nom, 40, col, "cuerpo", "SEMIBOLD").move_to([x, -3.3, 0]).set_z_index(9), pel, 0.8))
        # enchufe: se conecta a un cuerpo a la vez
        xp = lambda: (XS[0] if pel.t < 5.6 else XS[0] + (XS[1] - XS[0]) * suave((pel.t - 5.6) / 0.9)) if pel.t < 11.4 else XS[1] + (XS[2] - XS[1]) * suave((pel.t - 11.4) / 0.9)
        enchufe = VGroup(Rectangle(width=0.7, height=0.55).set_fill(est.acento, 1).set_stroke(est.tinta, 3), Line([-0.18, 0.27, 0], [-0.18, 0.55, 0], stroke_width=6, color=est.tinta), Line([0.18, 0.27, 0], [0.18, 0.55, 0], stroke_width=6, color=est.tinta)).set_z_index(10)
        cable = VMobject().set_z_index(6)

        def conectar(m):
            x = xp()
            enchufe.become(VGroup(Rectangle(width=0.7, height=0.55).set_fill(est.acento, 1).set_stroke(est.tinta, 3), Line([-0.18, 0.27, 0], [-0.18, 0.55, 0], stroke_width=6, color=est.tinta),
                                  Line([0.18, 0.27, 0], [0.18, 0.55, 0], stroke_width=6, color=est.tinta)).rotate(PI).move_to([x, 2.15, 0]).set_z_index(10))
            m.set_points_as_corners([[0, 2.75, 0], [0, 2.5, 0], [x, 2.5, 0], [x, 2.4, 0]]).set_stroke(est.acento, 6, 0.95 * rampa(pel.t, 0.9)).set_fill(opacity=0)
            fundir(enchufe, rampa(pel.t, 0.9, 0.4))
        cable.add_updater(conectar)
        conectar(cable)
        self.add(cable, enchufe)
        self.add(aparece(texto(est, "se cambia el enchufe,\nno el cerebro", 44, est.tinta, "cuerpo", "SEMIBOLD", ancho_max=8.0).move_to([-2.2, -4.9, 0]).set_z_index(9), pel, 6.4))
        self.add(aparece(texto(est, "aún sin probar\ncon hardware", 36, est.tenue, "cuerpo", "SEMIBOLD", ancho_max=3.8).move_to([4.7, -4.7, 0]).set_z_index(9), pel, 12.2))

        leyendas(self, est, pel, n, [
            ("Un cerebro puede mover cuerpos distintos", "primero, una montura de antena simulada"),
            ("Pasa al simulador 3D sin reescribir nada", "solo se cambia una línea: el «enchufe»"),
            ("Y después, la montura real", "es el siguiente paso: aún no se ha probado")])
        cerrar_serie(self, est, pel, self.VAR)

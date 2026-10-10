import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *

import caos_gravedad as G
import datos_co as DO
from estilo_reel import Viva, cerrar_serie, cola, leyenda, punto, preparar_serie, texto
from reels_promo import polilinea, suave

# SERIE «CAOS Y GRAVEDAD» — lo que la gravedad hace cuando hay más de dos cuerpos: tres cuerpos sin fórmula, efecto mariposa,
# puntos de Lagrange, lunas que cambian de órbita, una luna que da tumbos, huecos en el cinturón de asteroides, la honda
# gravitatoria, la cascada de Kessler, el horizonte de predicción y los atajos de baja energía.
# Casi todo es SIMULACIÓN real (caos_gravedad.py, congelada en studio/content/datos_caos/) o dato real (JPL SBDB); supuestos y
# fuentes en datos_co.py y en el ⚠️ de los pies. Tema CAOS con fondo vertical propio (diagrama de bifurcación como horizonte).
# Formato película: título → cuerpo → logo → loop. Pocas cifras, cada una con una comparación cotidiana.

FIN = 3.0
KICKER = "Caos y gravedad"
SERIE = dict(tema="caos", fondo="reel")
CIAN, VIOLETA, VERDE, AZUL, ROJO = "#5EEAD4", "#A78BFA", "#4ADE80", "#3B8FD9", "#FF5A6E"


def leyendas(escena, est, pel, nombre, textos):
    ts = list(DO.LEYENDAS[nombre]) + [DO.CUERPO[nombre] + FIN]
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


def vive(m, f):
    m.add_updater(lambda x: fundir(x, f()))
    fundir(m, f())
    return m


def aparece(m, pel, t0, d=0.6, hasta=None):
    return vive(m, lambda: rampa(pel.t, t0, d) * ((1 - rampa(pel.t, hasta, d)) if hasta else 1))


def zona(p, y0=-5.6, y1=5.3):
    return float(y0 < p[1] < y1 and -7.0 < p[0] < 7.0)


def dibujo(pel, f_puntos, t0, color, ancho=6, z=9, hasta=None, opacidad=1.0):
    """Curva que se redibuja cada cuadro con f_puntos() (si hay < 2 puntos, no se ve)."""
    m = VMobject().set_z_index(z)

    def act(x):
        pts = np.asarray(f_puntos())
        k = rampa(pel.t, t0, 0.3) * ((1 - rampa(pel.t, hasta)) if hasta else 1)
        if len(pts) < 2:
            pts, k = np.zeros((2, 3)), 0.0
        x.become(polilinea(pts, color=color, width=ancho, opacity=opacidad).set_z_index(z))
        fundir(x, k)
    m.add_updater(act)
    act(m)
    return m


def u_de(pel, t0, t1):
    return float(np.clip((pel.t - t0) / (t1 - t0), 0, 1))


def en(T, X, t):
    """X (n, ..., 2) muestreado en T, interpolado en t (por componente)."""
    t = float(np.clip(t, T[0], T[-1]))
    i = int(np.clip(np.searchsorted(T, t) - 1, 0, len(T) - 2))
    f = (t - T[i]) / (T[i + 1] - T[i])
    return X[i] * (1 - f) + X[i + 1] * f


def a3(xy, c=ORIGIN, s=1.0):
    xy = np.asarray(xy, float)
    return np.asarray(c, float) + s * np.array([xy[0], xy[1], 0.0])


def cuerpo(color, r):
    return VGroup(Circle(radius=r * 2.4).set_fill(color, 0.16).set_stroke(width=0),
                  Circle(radius=r).set_fill(color, 1).set_stroke(width=0)).set_z_index(12)


def ejes(est, x0, x1, y0, y1, tx, ty):
    return VGroup(Arrow([x0, y0, 0], [x1 + 0.3, y0, 0], buff=0, stroke_width=4, color=est.tenue, max_tip_length_to_length_ratio=0.03),
                  Arrow([x0, y0, 0], [x0, y1 + 0.3, 0], buff=0, stroke_width=4, color=est.tenue, max_tip_length_to_length_ratio=0.05),
                  texto(est, tx, 30, est.tenue).next_to([x1 + 0.3, y0, 0], DOWN, buff=0.15).align_to([x1 + 0.3, 0, 0], RIGHT),
                  texto(est, ty, 30, est.tenue).next_to([x0 + 0.2, y1 + 0.3, 0], RIGHT, buff=0.1)).set_z_index(8)


def miles(x):
    return f"{x:,.0f}".replace(",", " ")


# ══ 1 · Tres cuerpos, ninguna fórmula (figura ocho y problema pitagórico) ═══════════════════════════════════════════════

class ReelCOOcho(Scene):
    VAR = 0

    def construct(self):
        n = "ReelCOOcho"; TB = DO.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Tres cuerpos,\nninguna fórmula", self.VAR, chip_txt="Simulación", **SERIE)
        cols = (est.acento, est.acento2, VIOLETA)
        # la figura ocho: un periodo = 4 s
        C1, S1 = np.array([0, 1.8, 0]), 6.3
        XO = DO.OCHO["X"]
        self.add(aparece(polilinea([a3(p, C1, S1) for p in XO[:, 0]], color=est.tenue, width=3, opacity=0.5).set_z_index(8), pel, 0.3, hasta=6.0))
        for k in range(3):
            b = cuerpo(cols[k], 0.16)
            b.add_updater(lambda m, k=k: m.move_to(a3(en(np.linspace(0, 1, len(XO)), XO[:, k], (pel.t / 4.0) % 1.0), C1, S1)))
            self.add(aparece(b, pel, 0.3, hasta=6.0))
        self.add(aparece(texto(est, "la «figura ocho»", 56, est.tinta, "titulo", "SEMIBOLD").move_to([0, -2.4, 0]).set_z_index(10), pel, 1.0, hasta=6.0))
        self.add(aparece(texto(est, "se repite para siempre", 40, est.tenue).move_to([0, -3.2, 0]).set_z_index(10), pel, 1.4, hasta=6.0))
        # el problema pitagórico (Burrau, 1913): masas 3, 4 y 5 en reposo
        C2, S2 = np.array([0.4, -0.5, 0]), 1.55
        T, A, M = DO.PIT_T, DO.PIT_A, DO.PIT_M
        ts = lambda: float(np.clip((pel.t - 7.0) * 72.0 / 10.8, 0, 72))
        tri = Polygon(*[a3(p, C2, S2) for p in A[0]]).set_stroke(est.tenue, 2, 0.6).set_fill(opacity=0)
        lados = VGroup(*[texto(est, str(L), 36, est.tenue).move_to(a3((A[0][i] + A[0][j]) / 2, C2, S2) + d)
                         for (i, j, L, d) in ((0, 1, 5, LEFT * 0.45 + UP * 0.2), (1, 2, 3, DOWN * 0.4), (0, 2, 4, RIGHT * 0.45))])
        self.add(aparece(VGroup(tri, lados).set_z_index(8), pel, 6.4, hasta=7.6))
        for k in range(3):
            def rastro(k=k):
                t = ts()
                sel = (T <= t) & (T >= t - 9)
                return [a3(p, C2, S2) for p in A[sel, k] if zona(a3(p, C2, S2))]
            self.add(dibujo(pel, rastro, 6.6, cols[k], 3, 9, opacidad=0.65))
            b = cuerpo(cols[k], 0.13 * M[k] ** (1 / 3))
            b.add_updater(lambda m, k=k: fundir(m.move_to(a3(en(T, A[:, k], ts()), C2, S2)), rampa(pel.t, 6.4) * zona(m.get_center())))
            self.add(b)
            self.add(aparece(texto(est, f"{M[k]:.0f}", 40, cols[k], "cifra", "BOLD").move_to(a3(A[0, k], C2, S2) + UP * 0.6).set_z_index(13), pel, 6.4, hasta=7.8))
        leyendas(self, est, pel, n, [
            ("Tres cuerpos casi nunca se repiten", "esta «figura ocho» es una rara excepción (1993)"),
            ("Tres masas quietas: 3, 4 y 5", "el «problema pitagórico», planteado en 1913"),
            ("Bailan sin patrón… y uno sale disparado", "no hay fórmula: solo se puede simular")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 2 · Una millonésima cambia el final (efecto mariposa) ══════════════════════════════════════════════════════════════

class ReelCOMariposa(Scene):
    VAR = 1

    def construct(self):
        n = "ReelCOMariposa"; TB = DO.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Una millonésima\ncambia el final", self.VAR, chip_txt="Simulación", **SERIE)
        C, S = np.array([0.4, 2.2, 0]), 1.2
        T, A, B, M = DO.PIT_T, DO.PIT_A, DO.PIT_B, DO.PIT_M
        TS0, TS1 = 0.6, 17.6
        ts = lambda: float(np.clip((pel.t - TS0) * 72.0 / (TS1 - TS0), 0, 72))
        zz = lambda p: zona(p, -0.4, 4.7)
        for X, col, z in ((A, est.acento, 10), (B, CIAN, 11)):
            for k in range(3):
                def rastro(X=X, k=k):
                    t = ts(); sel = (T <= t) & (T >= t - 7)
                    return [a3(p, C, S) for p in X[sel, k] if zz(a3(p, C, S))]
                self.add(dibujo(pel, rastro, 0.6, col, 3, z - 2, opacidad=0.6))
                b = cuerpo(col, 0.11 * M[k] ** (1 / 3)).set_z_index(z + 2)
                b.add_updater(lambda m, X=X, k=k: fundir(m.move_to(a3(en(T, X[:, k], ts()), C, S)), rampa(pel.t, 0.4) * zz(m.get_center())))
                self.add(b)
        self.add(aparece(VGroup(Dot(radius=0.12, color=est.acento), texto(est, "copia A", 36, est.acento),
                                Dot(radius=0.12, color=CIAN), texto(est, "copia B: movida 0.000001", 36, CIAN)).arrange(RIGHT, buff=0.25)
                         .move_to([0, 5.0, 0]).set_z_index(13), pel, 0.6))
        # separación en escala logarítmica
        X0, X1, Y0, Y1 = -6.0, 6.0, -5.3, -2.1
        self.add(aparece(ejes(est, X0, X1, Y0, Y1, "tiempo", "diferencia"), pel, 1.0))
        ly = lambda s: Y0 + (Y1 - Y0) * (np.log10(max(s, 1e-7)) + 7) / 8.0
        for e, txt in ((-6, "una millonésima"), (-3, "una milésima"), (0, "tamaño del baile")):
            y = Y0 + (Y1 - Y0) * (e + 7) / 8.0
            self.add(aparece(VGroup(DashedLine([X0, y, 0], [X1, y, 0], dash_length=0.15, stroke_width=1.5, color=est.tenue).set_opacity(0.45),
                                    texto(est, txt, 28, est.tenue).next_to([X1, y + 0.05, 0], UP, buff=0.05).align_to([X1, 0, 0], RIGHT)).set_z_index(8), pel, 1.2))
        sep = np.maximum(DO.PIT_SEP, 1e-6)
        self.add(dibujo(pel, lambda: [[X0 + (X1 - X0) * t / 72, ly(s), 0] for t, s in zip(T, sep) if t <= ts()], 1.0, est.acento2, 6, 10))
        self.add(Viva(est, lambda: f"la diferencia creció × {miles(max(1, en(T, sep, ts()) / 1e-6))}", [0.6, -1.05, 0], 48, est.acento2, rol="titulo",
                      f_op=lambda: rampa(pel.t, 6.4)))
        leyendas(self, est, pel, n, [
            ("Dos copias del mismo baile", "una empieza movida una millonésima"),
            ("Un rato idénticas… luego ya no", "la diferencia se multiplica sin parar"),
            ("Al final, otro destino", "es el efecto mariposa de la gravedad")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 3 · Cinco lugares para quedarse quieto (puntos de Lagrange) ═══════════════════════════════════════════════════════

class ReelCOLagrange(Scene):
    VAR = 2

    def construct(self):
        from skimage.measure import find_contours
        n = "ReelCOLagrange"; TB = DO.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Cinco lugares para\nquedarse quieto", self.VAR, chip_txt="Simulación", **SERIE)
        mu = DO.MU_DIBUJO
        Lp = DO.L_DIBUJO
        C, S = np.array([0, 1.4, 0]), 4.1
        xs = np.linspace(-1.6, 1.6, 420); ys = np.linspace(-1.05, 1.05, 280)
        XX, YY = np.meshgrid(xs, ys)
        Om = G.potencial(XX, YY, mu)
        crit = sorted(G.potencial(np.array([p[0]]), np.array([p[1]]), mu)[0] for k, p in Lp.items() if k in ("L1", "L2", "L3"))
        niveles = list(np.linspace(1.47, crit[0] - 0.01, 3)) + [crit[2] - 0.005, crit[1] + 0.005, crit[0] + 0.01] + list(np.linspace(crit[0] + 0.06, 2.6, 4))
        lineas = VGroup()
        for j, nv in enumerate(niveles):
            for cnt in find_contours(Om, nv):
                if len(cnt) < 8:
                    continue
                pts = [a3((np.interp(c[1], np.arange(len(xs)), xs), np.interp(c[0], np.arange(len(ys)), ys)), C, S) for c in cnt[::2]]
                lineas.add(polilinea(pts, color=VIOLETA if j < 3 or j > 5 else est.acento2, width=2 if j < 3 or j > 5 else 3,
                                     opacity=0.45 if j < 3 or j > 5 else 0.75))
        self.add(aparece(lineas.set_z_index(7), pel, 0.3, 1.2))
        self.add(aparece(cuerpo(est.acento, 0.42).move_to(a3((-mu, 0), C, S)), pel, 0.2))
        self.add(aparece(cuerpo(AZUL, 0.2).move_to(a3((1 - mu, 0), C, S)), pel, 0.2))
        self.add(aparece(VGroup(texto(est, "Sol", 34, est.acento).move_to(a3((-mu, 0), C, S) + DOWN * 0.8),
                                texto(est, "Tierra", 34, "#8FD8FF").move_to(a3((1 - mu, 0), C, S) + DOWN * 0.65)).set_z_index(12), pel, 0.4))
        for k, (x, y) in Lp.items():
            p = a3((x, y), C, S)
            marca = VGroup(Line(p + LEFT * 0.16 + UP * 0.16, p + RIGHT * 0.16 + DOWN * 0.16, stroke_width=5, color=est.tinta),
                           Line(p + LEFT * 0.16 + DOWN * 0.16, p + RIGHT * 0.16 + UP * 0.16, stroke_width=5, color=est.tinta),
                           texto(est, k, 34, est.tinta, "cifra", "SEMIBOLD").move_to(p + UP * 0.45 + (RIGHT * 0.35 if k == "L2" else 0)))
            self.add(aparece(marca.set_z_index(12), pel, 1.6 + 0.4 * int(k[1])))
        self.add(aparece(VGroup(texto(est, "curvas de nivel de gravedad + giro", 40, est.tinta, "titulo", "SEMIBOLD"),
                                texto(est, "dibujo con la masa del planeta exagerada", 34, est.tenue)).arrange(DOWN, buff=0.25)
                         .move_to([0, -3.7, 0]).set_z_index(12), pel, 1.2, hasta=6.4))
        # L2: el telescopio Webb
        p2 = a3(Lp["L2"], C, S)
        self.add(vive(Circle(radius=0.55).move_to(p2).set_stroke(est.acento, 5).set_z_index(12),
                      lambda: rampa(pel.t, 6.4) * (1 - rampa(pel.t, 12.4)) * (0.6 + 0.4 * np.sin(2 * np.pi * pel.t / 1.5))))
        self.add(aparece(VGroup(texto(est, "Webb, en L2:", 44, est.acento, "titulo", "SEMIBOLD"),
                                texto(est, f"{DO.L2_KM / 1e6:.1f} millones de km", 52, est.tinta, "cifra", "SEMIBOLD"),
                                texto(est, f"≈ {DO.L2_VECES_LUNA:.0f} veces la distancia a la Luna", 38, est.tenue)).arrange(DOWN, buff=0.25)
                         .move_to([0, -3.7, 0]).set_z_index(12), pel, 7.0, hasta=12.4))
        # L4 y L5: troyanos (órbitas de renacuajo simuladas)
        rng = np.random.default_rng(4)
        for k in ("L4", "L5"):
            x0, y0 = Lp[k]
            for q in range(7):
                s0 = [x0 + rng.normal(0, 0.035), y0 + rng.normal(0, 0.035), 0.0, 0.0]
                t, Sx = G.cr3bp(s0, mu, 70.0, 900, rtol=1e-9)
                pts = [a3(p[:2], C, S) for p in Sx]
                self.add(aparece(polilinea(pts, color=est.acento2, width=1.6, opacity=0.35).set_z_index(9), pel, 12.8 + 0.1 * q))
                d = punto(est.acento2, 0.06)
                d.add_updater(lambda m, pts=pts, q=q: m.move_to(pts[int(((pel.t - 12.8) * 40 + 120 * q)) % len(pts)]))
                self.add(aparece(d, pel, 12.8))
        self.add(aparece(VGroup(texto(est, "en L4 y L5 de Júpiter:", 40, est.acento2, "titulo", "SEMIBOLD"),
                                texto(est, f"{miles(DO.TROYANOS)} asteroides troyanos", 50, est.tinta, "cifra", "SEMIBOLD")).arrange(DOWN, buff=0.25)
                         .move_to([0, -3.7, 0]).set_z_index(12), pel, 13.4))
        leyendas(self, est, pel, n, [
            ("Donde las fuerzas se equilibran", "en el marco que gira con la Tierra hay 5 puntos"),
            ("El telescopio Webb vive en L2", "ahí la Tierra y el Sol quedan siempre del mismo lado"),
            ("En L4 y L5 se juntan asteroides", "los troyanos de Júpiter, contados por la NASA")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 4 · Dos lunas que cambian de lugar (Jano y Epimeteo) ═════════════════════════════════════════════════════════════

class ReelCOHerradura(Scene):
    VAR = 0

    def construct(self):
        n = "ReelCOHerradura"; TB = DO.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Dos lunas que\ncambian de lugar", self.VAR, chip_txt="Simulación", **SERIE)
        C, R = np.array([0, 0.9, 0]), 4.1
        K = 0.75 / DO.DA_KM                                              # 50 km → 0.75 unidades (exagerado ~400 veces)
        self.add(aparece(VGroup(Circle(radius=0.95).set_fill("#C9A86A", 1).set_stroke(width=0),
                                Ellipse(width=3.3, height=0.75).set_stroke("#E8D6A8", 4, 0.8),
                                Ellipse(width=2.7, height=0.58).set_stroke("#E8D6A8", 2, 0.5)).rotate(-0.25).move_to(C).set_z_index(8), pel, 0.2))
        self.add(aparece(texto(est, "Saturno", 34, est.tenue).move_to(C + DOWN * 1.3).set_z_index(9), pel, 0.4))
        self.add(aparece(DashedVMobject(Circle(radius=R).move_to(C).set_stroke(est.tenue, 2), num_dashes=70).set_z_index(7), pel, 0.3))
        T, ANG, DR = DO.CO_T, DO.CO_ANG, DO.CO_DR
        anio = lambda: float(np.clip((pel.t - 0.6) * 9.0 / 17.0, 0, 9.0))
        P = lambda a, d: C + (R + K * d) * np.array([np.cos(np.pi / 2 + a), np.sin(np.pi / 2 + a), 0])
        jano = cuerpo(est.acento, 0.17).move_to(P(0, 0))
        self.add(aparece(jano, pel, 0.4))
        self.add(aparece(texto(est, "Jano", 38, est.acento, "titulo", "SEMIBOLD").move_to(P(0, 0) + UP * 0.55 + RIGHT * 0.9).set_z_index(13), pel, 0.6))
        self.add(dibujo(pel, lambda: [P(a, d) for t, a, d in zip(T[::3], ANG[::3], DR[::3]) if t <= anio()], 0.6, est.acento2, 4, 10, opacidad=0.8))
        epi = cuerpo(est.acento2, 0.13)
        epi.add_updater(lambda m: m.move_to(P(en(T, ANG, anio()), en(T, DR, anio()))))
        self.add(aparece(epi, pel, 0.4))
        self.add(Viva(est, lambda: "Epimeteo", lambda: epi.get_center() + DOWN * 0.55, 34, est.acento2, rol="titulo", f_op=lambda: rampa(pel.t, 0.6) * (1 - rampa(pel.t, 5.0))))
        self.add(Viva(est, lambda: f"año {anio():.1f}", [4.9, 5.0, 0], 46, est.tinta, rol="cifra", f_op=lambda: rampa(pel.t, 0.6)))
        self.add(aparece(texto(est, "marco que gira con Jano · diferencia de órbitas exagerada ~400 veces", 30, est.tenue, ancho_max=12.8)
                         .move_to([0, -4.6, 0]).set_z_index(12), pel, 1.0, hasta=12.6))
        cambio = lambda: max([max(0.0, 1 - abs(anio() - c) / 0.35) for c in DO.CO_CAMBIOS] + [0.0])
        self.add(Viva(est, lambda: "¡cambian de órbita!", [0, -1.4, 0], 48, est.acento, rol="titulo", f_op=lambda: min(1.0, 2 * cambio())))
        self.add(aparece(VGroup(texto(est, f"un cambio cada {DO.CO_PERIODO_ANIOS:.1f} años", 48, est.tinta, "cifra", "SEMIBOLD"),
                                texto(est, f"en la simulación, nunca a menos de {miles(round(DO.CO_MIN_KM, -3))} km", 36, est.tenue)).arrange(DOWN, buff=0.25)
                         .move_to([0, -4.5, 0]).set_z_index(12), pel, 13.0))
        leyendas(self, est, pel, n, [
            ("Jano y Epimeteo, lunas de Saturno", "sus órbitas se separan apenas 50 km"),
            ("Cuando una alcanza a la otra…", "se jalan y cambian de órbita, sin tocarse"),
            ("Se turnan cada 4 años", "simulado con sus masas reales: igual que en la realidad")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 5 · La luna que da tumbos (Hiperión) ═══════════════════════════════════════════════════════════════════════════════

class ReelCOHiperion(Scene):
    VAR = 1

    def construct(self):
        n = "ReelCOHiperion"; TB = DO.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "La luna que\nda tumbos", self.VAR, chip_txt="Simulación", **SERIE)
        orbs = lambda: max(pel.t - 0.6, 0) * 40.0 / 12.0                # 40 órbitas en 12 s del cuerpo
        for k, (cx, e, TH, nombre, col, larga) in enumerate(((-3.4, 0.0549, DO.LUNA_TH, "nuestra Luna", "#C9CED6", 0.78),
                                                             (3.4, DO.HIP_E, DO.HIP_TH, "Hiperión", est.acento2, 0.55))):
            c = np.array([cx, 2.4, 0]); a = 2.0
            foco = c + RIGHT * a * e
            self.add(aparece(VGroup(Ellipse(width=2 * a, height=2 * a * np.sqrt(1 - e * e)).move_to(c).set_stroke(est.tenue, 2, 0.5),
                                    cuerpo(est.acento, 0.22).move_to(foco)).set_z_index(8), pel, 0.3 + 0.3 * k))
            self.add(aparece(texto(est, nombre, 42, col, "titulo", "SEMIBOLD").move_to(c + UP * 2.4).set_z_index(10), pel, 0.5 + 0.3 * k))
            T = DO.HIP_T

            def act(m, c=c, a=a, e=e, TH=TH, col=col, larga=larga, foco=foco):
                o = orbs() * 0.12                                         # se dibuja la órbita a 0.12 del ritmo del giro (cámara lenta)
                f, r = G.kepler_f_r(np.array([2 * np.pi * (o % 1.0)]), e)
                pos = foco + a * r[0] * np.array([np.cos(f[0]), np.sin(f[0]), 0])
                f_sim, _ = G.kepler_f_r(np.array([2 * np.pi * (orbs() % 1.0)]), e)
                th = en(T, TH, orbs()) - f_sim[0] + f[0]                  # orientación respecto del planeta, puesta en la órbita lenta
                cuerpo_ = Ellipse(width=0.95, height=0.95 * larga).set_fill(col, 1).set_stroke("#FFFFFF", 1.5, 0.5)
                cara = Dot([0.47, 0, 0], radius=0.09, color=ROJO)
                m.become(VGroup(cuerpo_, cara).rotate(th, about_point=ORIGIN).move_to(pos).set_z_index(12))
            luna = VGroup(); luna.add_updater(act); act(luna)
            self.add(aparece(luna, pel, 0.4 + 0.3 * k))
        # una «foto» por vuelta (en el periapsis): ¿hacia dónde apunta el lado largo? (sección de Poincaré)
        X0, X1, Y0, Y1 = -6.0, 6.0, -5.3, -1.3
        self.add(aparece(ejes(est, X0, X1, Y0, Y1, "vueltas", "hacia dónde apunta, una foto por vuelta"), pel, 1.0))
        gy = lambda grados: (Y0 + Y1) / 2 + (Y1 - Y0) / 2 * grados / 90.0
        self.add(aparece(VGroup(DashedLine([X0, gy(0), 0], [X1, gy(0), 0], dash_length=0.15, stroke_width=1.5, color=est.tenue).set_opacity(0.5),
                                texto(est, "mira al planeta", 28, est.tenue).next_to([X1, gy(0) + 0.05, 0], UP, buff=0.05).align_to([X1, 0, 0], RIGHT)).set_z_index(8), pel, 1.2))
        T = DO.HIP_T
        paso = int(round(len(T) / 40))
        for TH, col, r in ((DO.LUNA_TH, "#C9CED6", 0.11), (DO.HIP_TH, est.acento2, 0.11)):
            fotos = VGroup()
            for k in range(1, 41):
                i_ = min(k * paso, len(T) - 1)
                g = np.degrees((TH[i_] + np.pi / 2) % np.pi - np.pi / 2)
                d = Dot([X0 + (X1 - X0) * k / 40, gy(g), 0], radius=r, color=col)
                d.k = k
                fotos.add(d)
            fotos.set_z_index(10)
            fotos.add_updater(lambda m: [fundir(d, float(d.k <= orbs())) for d in m])
            self.add(fotos)
        self.add(aparece(VGroup(texto(est, "1984: caótica", 40, est.acento2, "titulo", "SEMIBOLD"), texto(est, "·", 40, est.tenue),
                                texto(est, "2024: ¿casi regular?", 40, est.acento, "titulo", "SEMIBOLD")).arrange(RIGHT, buff=0.3)
                         .move_to([0, -0.1, 0]).set_z_index(12), pel, 13.0))
        leyendas(self, est, pel, n, [
            ("La Luna siempre nos da la misma cara", "gira al mismo ritmo que da la vuelta"),
            ("Hiperión, luna de Saturno, no", "alargada y en órbita ovalada: su giro cambia sin parar"),
            ("Así lo predijo un modelo en 1984", "un estudio de 2024 lo discute: la ciencia sigue")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 6 · Huecos en el cinturón de asteroides (datos reales de la JPL) ═════════════════════════════════════════════════

class ReelCOKirkwood(Scene):
    VAR = 2

    def construct(self):
        n = "ReelCOKirkwood"; TB = DO.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Huecos en el cinturón\nde asteroides", self.VAR, chip_txt="Datos NASA/JPL", **SERIE)
        bordes, cuenta = DO.KIRK_BORDES, DO.KIRK_CUENTA
        cent = (bordes[:-1] + bordes[1:]) / 2
        # el cinturón visto inclinado: 1 800 asteroides sorteados con la distribución REAL de distancias
        Cb, SX, SY = np.array([0, 2.5, 0]), 1.72, 0.62
        rng = np.random.default_rng(12)
        a = rng.choice(cent, 1800, p=cuenta / cuenta.sum()) + rng.uniform(-0.0025, 0.0025, 1800)
        fi = rng.uniform(0, 2 * np.pi, 1800)
        w = 0.25 * (2.2 / a) ** 1.5
        cin = VGroup(*[Dot(radius=0.026, color=VIOLETA if ai > 2.9 else est.acento2) for ai in a]).set_z_index(9)

        def girar(m):
            ang = fi + w * pel.v
            xs, ys = Cb[0] + SX * a * np.cos(ang), Cb[1] + SY * a * np.sin(ang)
            for d, x, y in zip(m, xs, ys):
                d.move_to([x, y, 0])
        cin.add_updater(girar); girar(cin)
        self.add(aparece(cin, pel, 0.3, 1.2))
        self.add(aparece(cuerpo(est.acento, 0.2).move_to(Cb), pel, 0.2))
        self.add(aparece(VGroup(Ellipse(width=2 * SX * 1.524, height=2 * SY * 1.524).move_to(Cb).set_stroke(ROJO, 2, 0.6),
                                texto(est, "Marte", 30, ROJO).move_to(Cb + DOWN * (SY * 1.524 + 0.25))).set_z_index(8), pel, 0.6))
        self.add(aparece(VGroup(Arrow([5.2, 4.95, 0], [6.6, 4.95, 0], buff=0, stroke_width=6, color=est.calido),
                                texto(est, "Júpiter", 34, est.calido).move_to([5.0, 4.95, 0]).align_to([4.95, 0, 0], RIGHT)).set_z_index(10), pel, 7.0))
        # histograma real
        X0, X1, Y0, Y1 = -6.2, 6.2, -5.2, -1.2
        ax = lambda av: X0 + (X1 - X0) * (av - 2.0) / 1.7
        c2 = cuenta.reshape(-1, 2).sum(1); b2 = bordes[::2]
        h = c2 / c2.max() * (Y1 - Y0)
        barras = VGroup(*[Rectangle(width=(X1 - X0) / len(c2) * 0.92, height=max(hh, 0.005)).set_fill(VIOLETA if b2[i] > 2.9 else est.acento2, 0.9)
                          .set_stroke(width=0).move_to([ax(b2[i] + 0.005), Y0 + hh / 2, 0]) for i, hh in enumerate(h)]).set_z_index(9)
        barras.add_updater(lambda m: [fundir(b, float(i < len(m) * u_de(pel, 0.8, 4.0))) for i, b in enumerate(m)])
        self.add(barras)
        self.add(aparece(VGroup(Line([X0, Y0, 0], [X1, Y0, 0], stroke_width=3, color=est.tenue),
                                *[texto(est, f"{v:.1f}", 30, est.tenue).move_to([ax(v), Y0 - 0.32, 0]) for v in (2.0, 2.5, 3.0, 3.5)],
                                texto(est, "distancia al Sol (en distancias Tierra–Sol)", 28, est.tenue).move_to([0, Y0 - 0.78, 0])).set_z_index(8), pel, 0.8))
        for j, (nom, av) in enumerate(DO.RESONANCIAS.items()):
            t0 = 6.6 + 0.9 * j
            self.add(aparece(VGroup(DashedLine([ax(av), Y0, 0], [ax(av), Y1 + 0.25, 0], dash_length=0.12, stroke_width=3, color=est.acento),
                                    texto(est, nom, 36, est.acento, "cifra", "SEMIBOLD").move_to([ax(av), Y1 + 0.55, 0])).set_z_index(10), pel, t0))
            self.add(aparece(DashedVMobject(Ellipse(width=2 * SX * av, height=2 * SY * av).move_to(Cb).set_stroke(est.acento, 3), num_dashes=60).set_z_index(10), pel, t0))
        self.add(aparece(VGroup(texto(est, miles(DO.ASTEROIDES), 52, est.tinta, "cifra", "SEMIBOLD"), texto(est, "asteroides", 40, est.tinta),
                                texto(est, f"NASA/JPL, {DO.FECHA_JPL}", 28, est.tenue)).arrange(DOWN, buff=0.15)
                         .move_to([4.75, -2.7, 0]).set_z_index(12), pel, 13.0))
        leyendas(self, est, pel, n, [
            ("Entre Marte y Júpiter: el cinturón", "cada barra cuenta asteroides reales por distancia"),
            ("Pero hay huecos", "donde darían 3 vueltas por cada 1 de Júpiter, y otras"),
            ("Júpiter los jala siempre en el mismo punto", "y con el tiempo los saca: huecos de Kirkwood")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 7 · Robar velocidad a Júpiter (asistencia gravitatoria) ══════════════════════════════════════════════════════════

class ReelCOHonda(Scene):
    VAR = 0

    def construct(self):
        n = "ReelCOHonda"; TB = DO.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Robarle velocidad\na Júpiter", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        CJ = np.array([0.6, 2.4, 0])
        self.add(aparece(VGroup(Circle(radius=0.85).set_fill("#C99A6B", 1).set_stroke(width=0),
                                *[Line([-0.8 * np.sqrt(1 - yy * yy), 0.85 * yy, 0], [0.8 * np.sqrt(1 - yy * yy), 0.85 * yy, 0], stroke_width=5, color="#8E5B3A").set_opacity(0.7)
                                  for yy in (-0.5, -0.15, 0.25, 0.55)]).move_to(CJ).set_z_index(9), pel, 0.2, hasta=12.4))
        self.add(aparece(texto(est, "Júpiter", 34, est.tenue).move_to(CJ + DOWN * 1.15 + RIGHT * 0.4).set_z_index(10), pel, 0.4, hasta=12.4))
        # la hipérbola en el marco de Júpiter (v∞ entra y sale igual)
        e = 1 + DO.RP * DO.V_INF ** 2 / G.MU_JUPITER
        vin = DO.V_IN_REL / DO.V_INF; vout = DO.V_OUT_REL / DO.V_INF
        Pd = (vin - vout) / np.linalg.norm(vin - vout); Qd = (vin + vout) / np.linalg.norm(vin + vout)
        sc = 1.6 / DO.RP
        f_inf = np.arccos(-1 / e)
        fs = np.linspace(-f_inf + 0.06, f_inf - 0.06, 400)
        pp = DO.RP * (1 + e) / (1 + e * np.cos(fs))
        hip = [CJ + sc * r * np.array([*(np.cos(f) * Pd + np.sin(f) * Qd), 0]) for r, f in zip(pp, fs)]
        hip = [p for p in hip if zona(p, -0.8, 5.3)]
        self.add(aparece(polilinea(hip, color=CIAN, width=4, opacity=0.8).set_z_index(10), pel, 0.6, 1.0, hasta=12.4))
        nave = punto(est.tinta, 0.1).set_z_index(13)
        nave.add_updater(lambda m: fundir(m.move_to(hip[int(len(hip) * ((pel.t * 0.22) % 1.0))]), rampa(pel.t, 0.8) * (1 - rampa(pel.t, 12.2))))
        self.add(nave)
        cola(self, nave, CIAN, n=24, ancho=6, z=12)
        for p, d, txt in ((hip[8], vin, "entra: 10 km/s"), (hip[-8], vout, "sale: 10 km/s")):
            ar = Arrow(p, p + np.array([*d, 0]) * 1.3, buff=0, stroke_width=6, color=CIAN, max_tip_length_to_length_ratio=0.3)
            self.add(aparece(VGroup(ar, texto(est, txt, 34, CIAN).next_to(p + np.array([*d, 0]) * 0.65, LEFT if d[0] < 0.3 else UP, buff=0.25)).set_z_index(12), pel, 2.0, hasta=12.4))
        # en el marco del Sol: sumar la velocidad de Júpiter (dos diagramas apilados)
        k = 0.24
        for j, (O, vrel, vsol, txt) in enumerate(((np.array([-6.0, -1.5, 0]), DO.V_IN_REL, DO.V_IN_SOL, f"llega: {DO.VEL_IN:.1f} km/s"),
                                                (np.array([-6.0, -4.9, 0]), DO.V_OUT_REL, DO.V_OUT_SOL, f"sale: {DO.VEL_OUT:.1f} km/s"))):
            t0 = 6.6 + 2.2 * j
            off = np.array([0, -0.32, 0]) if j == 1 else ORIGIN               # la resultante va un poco abajo si es colineal
            pj = O + k * np.array([*DO.VJ, 0]); pr = pj + k * np.array([*vrel, 0]); ps = O + k * np.array([*vsol, 0])
            g = VGroup(Arrow(O, pj, buff=0, stroke_width=7, color=est.calido, max_tip_length_to_length_ratio=0.15),
                       Arrow(pj, pr, buff=0, stroke_width=7, color=CIAN, max_tip_length_to_length_ratio=0.2),
                       Arrow(O + off, ps + off, buff=0, stroke_width=8, color=est.tinta, max_tip_length_to_length_ratio=0.1),
                       texto(est, txt, 44, est.tinta, "titulo", "SEMIBOLD").next_to(ps + off, RIGHT, buff=0.3))
            self.add(aparece(g.set_z_index(12), pel, t0))
        self.add(aparece(VGroup(Line([-6.2, -0.7, 0], [-5.5, -0.7, 0], stroke_width=7, color=est.calido), texto(est, "Júpiter: 13 km/s", 32, est.calido),
                                Line([0, 0, 0], [0.7, 0, 0], stroke_width=7, color=CIAN), texto(est, "la nave vista desde Júpiter", 32, CIAN)).arrange(RIGHT, buff=0.2)
                         .move_to([0, -0.5, 0]).set_z_index(12), pel, 6.4, hasta=12.4))
        self.add(aparece(texto(est, f"+ {DO.GANANCIA_KMS:.1f} km/s", 72, est.acento, "cifra", "BOLD").move_to([3.9, -2.6, 0]).set_z_index(12), pel, 10.2))
        # Voyager 2: de planeta en planeta (esquema; distancias en raíz cuadrada)
        Sol = np.array([-6.6, -0.1, 0]); KS = 2.2
        self.add(aparece(cuerpo(est.acento, 0.2).move_to(Sol), pel, 12.8))
        for nom, au, ang in (("Júpiter", 5.2, 0.62), ("Saturno", 9.5, 0.42), ("Urano", 19.2, 0.22), ("Neptuno", 30.1, 0.05)):
            r = KS * np.sqrt(au)
            arco = [Sol + r * np.array([np.cos(a_), np.sin(a_), 0]) for a_ in np.linspace(-0.05, 1.0, 60)]
            arco = [p for p in arco if p[1] < 4.6 and p[0] < 6.8]
            p = Sol + r * np.array([np.cos(ang), np.sin(ang), 0])
            self.add(aparece(VGroup(polilinea(arco, color=est.tenue, width=2, opacity=0.5), Dot(p, radius=0.15, color=est.calido),
                                    texto(est, nom, 32, est.tinta).next_to(p, UP, buff=0.15)).set_z_index(9), pel, 12.8))
        ruta = [Sol + KS * np.sqrt(au) * np.array([np.cos(an), np.sin(an), 0]) for au, an in ((1.0, 1.1), (5.2, 0.62), (9.5, 0.42), (19.2, 0.22), (30.1, 0.05))]
        curva = VMobject().set_points_smoothly(ruta).set_stroke(CIAN, 5)
        self.add(aparece(curva.set_z_index(10), pel, 13.4, 1.6))
        self.add(aparece(texto(est, "Voyager 2 · 1977–1989", 46, CIAN, "titulo", "SEMIBOLD").move_to([2.4, 4.9, 0]).set_z_index(12), pel, 13.6))
        leyendas(self, est, pel, n, [
            ("Vista desde Júpiter, entra y sale igual de rápido", "la gravedad solo le cambia la dirección"),
            ("Vista desde el Sol, sale más rápido", "le «roba» un poco de su velocidad a Júpiter"),
            ("Así saltó la Voyager 2 de planeta en planeta", "una alineación que se repite cada ~175 años")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 8 · Choques que fabrican choques (síndrome de Kessler) ═════════════════════════════════════════════════════════════

class ReelCOKessler(Scene):
    VAR = 1

    def construct(self):
        n = "ReelCOKessler"; TB = DO.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Choques que\nfabrican choques", self.VAR, chip_txt="Modelo de juguete", **SERIE)
        C = np.array([0, 1.7, 0])
        self.add(aparece(VGroup(Circle(radius=1.35).set_fill(est.mezcla(est.fondo, AZUL, 0.75), 1).set_stroke("#8FD8FF", 3),
                                Circle(radius=1.45).set_fill(AZUL, 0.15).set_stroke(width=0)).move_to(C).set_z_index(8), pel, 0.2))
        rng = np.random.default_rng(21)
        # choques (tiempo, radio, ángulo) y satélites: los primeros dos se encuentran en el choque 1
        choques = [(2.6, 2.5, 0.9), (8.0, 3.0, 2.6), (9.4, 2.2, 4.2), (10.6, 3.3, 5.6), (11.4, 2.7, 3.4)]
        sats = []
        for (tc, r, a) in choques:
            for sgn in (1, -1):
                w = sgn * rng.uniform(0.35, 0.55)
                sats.append((r, a - w * tc, w, tc))
        for _ in range(26):
            sats.append((rng.uniform(1.9, 3.5), rng.uniform(0, 2 * np.pi), rng.choice([-1, 1]) * rng.uniform(0.25, 0.5), 99))
        for (r, a0, w, tc) in sats:
            s = punto(est.tinta, 0.07)
            s.add_updater(lambda m, r=r, a0=a0, w=w, tc=tc: fundir(m.move_to(C + r * np.array([np.cos(a0 + w * pel.t), np.sin(a0 + w * pel.t) * 0.92, 0])),
                                                                    rampa(pel.t, 0.4) * float(pel.t < tc)))
            fundir(s, 0); self.add(s)
        for j, (tc, r, a) in enumerate(choques):
            pc = C + r * np.array([np.cos(a), np.sin(a) * 0.92, 0])
            self.add(vive(Circle(radius=0.6).move_to(pc).set_fill(est.acento, 0.6).set_stroke(width=0).set_z_index(13),
                          lambda tc=tc: max(0.0, 1 - abs(pel.t - tc - 0.1) / 0.35)))
            nfr = 22 if j == 0 else 14
            for q in range(nfr):
                da, dr_ = rng.normal(0, 0.18), rng.normal(0, 0.12)
                wq = rng.uniform(0.3, 0.55) * rng.choice([-1, 1])
                f = punto(est.acento2, 0.045)

                def mover(m, tc=tc, r=r, a=a, da=da, dr_=dr_, wq=wq):
                    u = max(pel.t - tc, 0)
                    ang = a + wq * u + da * min(u, 1.5)
                    rr = r + dr_ * min(u, 1.5)
                    m.move_to(C + rr * np.array([np.cos(ang), np.sin(ang) * 0.92, 0]))
                    fundir(m, float(pel.t >= tc) * zona(m.get_center()))
                f.add_updater(mover); fundir(f, 0); self.add(f)
        self.add(Viva(est, lambda: f"choques: {sum(1 for c in choques if pel.t >= c[0])}", [4.9, 4.4, 0], 52, est.acento, rol="cifra",
                      f_op=lambda: rampa(pel.t, 2.6)))
        self.add(aparece(VGroup(texto(est, "Iridium 33 + Cosmos 2251 (2009):", 36, est.tenue),
                                texto(est, "más de 2 000 fragmentos", 48, est.acento2, "cifra", "SEMIBOLD"),
                                texto(est, "prueba antisatélite Fengyun-1C (2007):", 36, est.tenue),
                                texto(est, "más de 3 000", 48, est.acento2, "cifra", "SEMIBOLD")).arrange(DOWN, buff=0.18)
                         .move_to([0, -3.3, 0]).set_z_index(12), pel, 3.4, hasta=12.4))
        # el modelo de juguete: debajo o encima del umbral
        X0, X1, Y0, Y1 = -6.0, 6.0, -5.3, -1.0
        self.add(aparece(ejes(est, X0, X1, Y0, Y1, "tiempo", "objetos en órbita"), pel, 12.8))
        gy = lambda nn: Y0 + (Y1 - Y0) * np.clip(nn / 260.0, 0, 1)
        yu = gy(DO.K_UMBRAL)
        self.add(aparece(VGroup(DashedLine([X0, yu, 0], [X1, yu, 0], dash_length=0.15, stroke_width=3, color=est.acento),
                                texto(est, "umbral", 32, est.acento).next_to([X1, yu + 0.05, 0], UP, buff=0.05).align_to([X1, 0, 0], RIGHT)).set_z_index(9), pel, 13.0))
        for Y, col in ((DO.K_BAJO, VERDE), (DO.K_ALTO, ROJO)):
            pts = [[X0 + (X1 - X0) * t / 40, gy(y), 0] for t, y in zip(DO.K_T, Y) if np.isfinite(y) and y < 262]
            self.add(dibujo(pel, lambda pts=pts: pts[:max(2, int(len(pts) * u_de(pel, 13.4, 17.0)))], 13.4, col, 6, 10))
        leyendas(self, est, pel, n, [
            ("En 2009 chocaron dos satélites", "y uno fue destruido a propósito en 2007"),
            ("Cada fragmento puede romper a otro", "y cada choque fabrica más fragmentos"),
            ("Pasado un umbral, la cascada sigue sola", "es el síndrome de Kessler (1978): hay que evitarlo")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 9 · Hasta dónde se puede predecir (horizonte de Lyapunov) ═══════════════════════════════════════════════════════

class ReelCOPrediccion(Scene):
    VAR = 2

    def construct(self):
        n = "ReelCOPrediccion"; TB = DO.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Hasta cuándo se\npuede predecir?", self.VAR, chip_txt="Datos públicos", **SERIE)
        C, R = np.array([0, 1.75, 0]), 3.3
        self.add(aparece(cuerpo(est.acento, 0.38).move_to(C), pel, 0.2))
        self.add(aparece(Circle(radius=R).move_to(C).set_stroke(est.tenue, 2, 0.5).set_z_index(7), pel, 0.3))
        myr = lambda: float(np.clip((pel.t - 6.6) * 120.0 / 9.0, 0, 120))
        err_m = lambda: DO.ERR0_M * np.exp(myr() / DO.LYAP_MYR)
        z = np.random.default_rng(3).normal(0, 1, 70)
        fantasmas = VGroup(*[Dot(radius=0.11, color=AZUL).set_opacity(0.55) for _ in z]).set_z_index(10)

        def act(m):
            dis = err_m() / 1.496e11 * np.pi                              # fracción de la órbita
            base = 0.6 * pel.v
            for d, zi in zip(m, z):
                ang = base + zi * dis
                d.move_to(C + R * np.array([np.cos(ang), np.sin(ang), 0]))
        fantasmas.add_updater(act); act(fantasmas)
        self.add(aparece(fantasmas, pel, 0.6))
        self.add(aparece(texto(est, "Tierra", 34, "#8FD8FF").move_to(C + DOWN * (R + 0.45)).set_z_index(10), pel, 0.6, hasta=6.4))
        # el clima: dos semanas
        self.add(aparece(VGroup(texto(est, "el clima:", 40, est.tenue), texto(est, "unas 2 semanas", 56, est.tinta, "cifra", "SEMIBOLD"))
                         .arrange(DOWN, buff=0.2).move_to([0, -3.4, 0]).set_z_index(12), pel, 1.2, hasta=6.2))

        def leer():
            e = err_m()
            if e < 1e3:
                return f"error: {e:.0f} m"
            if e < 1e9:
                return f"error: {miles(e / 1e3)} km"
            return f"error: {e / 1e9:.0f} millones de km"
        self.add(Viva(est, lambda: f"dentro de {myr():.0f} millones de años", [0, -2.7, 0], 44, est.tinta, rol="titulo",
                      f_op=lambda: rampa(pel.t, 6.6)))
        self.add(Viva(est, leer, [0, -3.6, 0], 52, est.acento2, rol="cifra", f_op=lambda: rampa(pel.t, 6.6)))
        self.add(aparece(texto(est, f"se duplica cada ~{DO.DUPLICA_MYR:.1f} millones de años", 36, est.tenue).move_to([0, -4.5, 0]).set_z_index(12), pel, 7.6))
        leyendas(self, est, pel, n, [
            ("El clima se predice unas dos semanas", "los errores pequeños se duplican en pocos días"),
            ("Los planetas, millones de años", "pero un error de 15 metros también crece"),
            ("En 100 millones de años, ya no se sabe", "dónde estará la Tierra en su órbita")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 10 · El camino largo gasta menos (transferencias de baja energía) ══════════════════════════════════════════════

class ReelCOAtajo(Scene):
    VAR = 0

    def construct(self):
        n = "ReelCOAtajo"; TB = DO.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "El camino largo\ngasta menos", self.VAR, chip_txt="Ilustración", **SERIE)
        E, RL = np.array([0, -2.75, 0]), 1.6
        L1 = E + UP * RL * DO.GRAIL_LEJOS_KM / DO.LUNA_KM                # 1.5 millones de km ≈ 3.9 distancias lunares
        self.add(aparece(VGroup(Circle(radius=0.42).set_fill(est.mezcla(est.fondo, AZUL, 0.75), 1).set_stroke("#8FD8FF", 3),
                                Circle(radius=0.5).set_fill(AZUL, 0.18).set_stroke(width=0)).move_to(E).set_z_index(9), pel, 0.2))
        self.add(aparece(DashedVMobject(Circle(radius=RL).move_to(E).set_stroke(est.tenue, 2), num_dashes=40).set_z_index(8), pel, 0.3))
        luna_ang = lambda: -0.3 + 0.08 * pel.t
        luna = cuerpo("#C9CED6", 0.13)
        luna.add_updater(lambda m: m.move_to(E + RL * np.array([np.cos(luna_ang()), np.sin(luna_ang()), 0])))
        self.add(aparece(luna, pel, 0.3))
        self.add(aparece(VGroup(Arrow([0, 4.3, 0], [0, 5.2, 0], buff=0, stroke_width=6, color=est.acento),
                                texto(est, "hacia el Sol", 32, est.acento).move_to([1.6, 4.8, 0])).set_z_index(10), pel, 0.6))
        self.add(aparece(VGroup(Dot(L1, radius=0.1, color=est.tinta), texto(est, "1.5 millones de km", 32, est.tenue).next_to(L1, LEFT, buff=0.25)).set_z_index(10), pel, 6.4))
        # Apolo: directo, 3 días
        dest = lambda t: E + RL * np.array([np.cos(-0.3 + 0.08 * t), np.sin(-0.3 + 0.08 * t), 0])
        ap = [E + RIGHT * 0.45, E + np.array([1.2, 0.6, 0]), dest(4.0)]
        apolo = VMobject().set_points_smoothly(ap).set_stroke(est.calido, 5)
        self.add(aparece(apolo.set_z_index(10), pel, 1.0, 1.0, hasta=12.4))
        nav_a = punto(est.calido, 0.09)
        nav_a.add_updater(lambda m: fundir(m.move_to(apolo.point_from_proportion(u_de(pel, 1.0, 4.0))), rampa(pel.t, 1.0) * (1 - rampa(pel.t, 12.2))))
        self.add(nav_a)
        self.add(Viva(est, lambda: f"Apolo: día {3 * u_de(pel, 1.0, 4.0):.0f}", [-3.6, 0.2, 0], 44, est.calido, rol="titulo",
                      f_op=lambda: rampa(pel.t, 1.0) * (1 - rampa(pel.t, 12.4))))
        # GRAIL: sale hacia el Sol–Tierra L1 y regresa (trazo ilustrativo)
        T0, T1 = 6.6, 12.2
        ruta = [E + LEFT * 0.4, E + np.array([-1.4, 1.6, 0]), L1 + np.array([-1.3, -0.6, 0]), L1 + np.array([-0.4, 0.5, 0]),
                L1 + np.array([0.9, 0.1, 0]), L1 + np.array([1.6, -1.6, 0]), E + np.array([2.2, 1.0, 0]), dest(T1)]
        grail = VMobject().set_points_smoothly(ruta).set_stroke(CIAN, 6)
        self.add(aparece(grail.set_z_index(10), pel, T0, 1.0))
        nav_g = punto(CIAN, 0.1)
        nav_g.add_updater(lambda m: fundir(m.move_to(grail.point_from_proportion(u_de(pel, T0, T1))), rampa(pel.t, T0)))
        self.add(nav_g)
        cola(self, nav_g, CIAN, n=22, ancho=6, z=11)
        self.add(Viva(est, lambda: f"GRAIL: día {112 * u_de(pel, T0, T1):.0f}", [4.5, 0.2, 0], 44, CIAN, rol="titulo",
                      f_op=lambda: rampa(pel.t, T0)))
        self.add(aparece(VGroup(texto(est, f"≈ {DO.GRAIL_AHORRO_MS} m/s menos de combustible", 46, est.acento, "cifra", "SEMIBOLD"),
                                texto(est, "CAPSTONE (2022) usó la misma idea", 36, est.tenue)).arrange(DOWN, buff=0.25)
                         .move_to([0, -5.0, 0]).set_z_index(12), pel, 13.2))
        leyendas(self, est, pel, n, [
            ("Apolo llegó a la Luna en 3 días", "camino directo, con mucho combustible"),
            ("GRAIL tardó tres meses y medio", "se alejó 1.5 millones de km y dejó que el Sol la regresara"),
            ("Más lento, pero más barato", "aprovechar la gravedad de todos ahorra combustible")])
        cerrar_serie(self, est, pel, self.VAR)

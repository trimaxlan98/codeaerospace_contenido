import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *

import datos_ca as DC
from estilo_reel import Viva, cerrar_serie, cola, leyenda, punto, preparar_serie, texto
from reels_promo import polilinea, suave

# SERIE «CÁLCULO EN EL ESPACIO» — una idea del cálculo por reel (derivada, integral, máximo, pasos numéricos, aceleración
# centrípeta, tasas, exponencial, aproximación, ecuación diferencial) con una aplicación espacial. Cuentas de calculo_espacio.py
# (supuestos en datos_ca.py y en el ⚠️ de los pies); sin mediciones propias.
# Tema CÁLCULO con fondo vertical propio (fondos_reel.calculo: la gráfica de una función como horizonte, con Riemann y tangente).
# Formato película: título → cuerpo → logo → loop. Pocas cifras, cada una con una comparación cotidiana.

FIN = 3.0
KICKER = "Cálculo en el espacio"
SERIE = dict(tema="calculo", fondo="reel")
AZUL, ROJO = "#3B8FD9", "#FF6B6B"


def leyendas(escena, est, pel, nombre, textos):
    ts = list(DC.LEYENDAS[nombre]) + [DC.CUERPO[nombre] + FIN]
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


def zona(p):
    return float(-5.6 < p[1] < 5.3 and -7.0 < p[0] < 7.0)


def dibujo(pel, f_puntos, t0, color, ancho=6, z=9, hasta=None):
    """Curva que se redibuja cada cuadro con los puntos de f_puntos() (VMobject vacío si hay < 2 puntos)."""
    m = VMobject().set_z_index(z)

    def act(x):
        pts = f_puntos()
        if len(pts) < 2:
            pts = np.zeros((2, 3))
        x.become(polilinea(pts, color=color, width=ancho).set_z_index(z))
        fundir(x, rampa(pel.t, t0, 0.3) * ((1 - rampa(pel.t, hasta)) if hasta else 1))
    m.add_updater(act)
    act(m)
    return m


def ejes(est, x0, x1, y0, y1, tx, ty, t_x=None):
    g = VGroup(Arrow([x0, y0, 0], [x1 + 0.3, y0, 0], buff=0, stroke_width=4, color=est.tenue, max_tip_length_to_length_ratio=0.03),
               Arrow([x0, y0, 0], [x0, y1 + 0.3, 0], buff=0, stroke_width=4, color=est.tenue, max_tip_length_to_length_ratio=0.05),
               texto(est, tx, 32, est.tenue).next_to([x1 + 0.3, y0 - 0.15, 0], DOWN, buff=0.1).align_to([x1 + 0.3, 0, 0], RIGHT),
               texto(est, ty, 32, est.tenue).next_to([x0 + 0.2, y1 + 0.3, 0], RIGHT, buff=0.1))
    return g.set_z_index(8)


def tierra(est, c, r):
    return VGroup(Circle(radius=r * 1.06).set_fill(AZUL, 0.18).set_stroke(width=0),
                  Circle(radius=r).set_fill(est.mezcla(est.fondo, AZUL, 0.75), 1).set_stroke("#8FD8FF", 3)).move_to(c).set_z_index(8)


def u_de(pel, t0, t1):
    return float(np.clip((pel.t - t0) / (t1 - t0), 0, 1))


# ══ 1 · La derivada: qué tan rápido cambia (la ISS cruza México) ══════════════════════════════════════════════════════════

class ReelCADerivada(Scene):
    VAR = 0

    def construct(self):
        n = "ReelCADerivada"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "La derivada:\nqué tan rápido cambia", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        X0, X1, Y0, Y1 = -6.0, 6.0, -0.4, 4.6
        self.add(aparece(ejes(est, X0, X1, Y0, Y1, "tiempo", "distancia"), pel, 0.2))
        KM = 80.0                                                    # un auto que recorre 80 km en una hora, sin velocidad constante
        s_ = lambda u: (u + 0.1 * np.sin(2 * np.pi * u))
        P = lambda u: np.array([X0 + (X1 - X0) * u, Y0 + (Y1 - Y0 - 0.3) * s_(u), 0])
        us = np.linspace(0, 1, 120)
        self.add(aparece(polilinea([P(u) for u in us], color=est.acento2, width=6).set_z_index(9), pel, 0.4))
        uu = lambda: 0.08 + 0.84 * (0.5 - 0.5 * np.cos(np.pi * u_de(pel, 1.0, 11.5)))
        pend = lambda u: (1 + 0.2 * np.pi * np.cos(2 * np.pi * u))     # ds/du, en «80 km por hora»

        def tangente(m):
            u = uu(); p = P(u)
            d = np.array([X1 - X0, (Y1 - Y0 - 0.3) * pend(u), 0]); d /= np.linalg.norm(d)
            m.become(Line(p - d * 1.8, p + d * 1.8, stroke_width=6, color=est.acento).set_z_index(10))
        tg = Line(ORIGIN, RIGHT).set_z_index(10); tg.add_updater(tangente); tangente(tg)
        self.add(aparece(tg, pel, 1.0, hasta=12.4))
        bola = punto(est.acento, 0.12).set_z_index(11)
        bola.add_updater(lambda m: m.move_to(P(uu())))
        self.add(aparece(bola, pel, 1.0, hasta=12.4))
        self.add(Viva(est, lambda: f"auto: {KM * pend(uu()):.0f} km/h", [3.6, Y1 + 0.35, 0], 44, est.acento, rol="titulo",
                      f_op=lambda: rampa(pel.t, 1.2) * (1 - rampa(pel.t, 12.4))))
        # la ISS: casi vertical en la misma gráfica (260 veces más pendiente)
        self.add(aparece(VGroup(Line([X0, Y0, 0], [X0 + (Y1 - Y0) / 3.0 * 0.05 * 3, Y1, 0], stroke_width=7, color=est.calido),
                                texto(est, "ISS", 44, est.calido, "titulo", "SEMIBOLD").move_to([X0 + 1.1, Y1 - 0.9, 0])).set_z_index(10), pel, 13.0))
        # mapa: Tijuana → Cancún
        ym = -2.95
        self.add(aparece(VGroup(Line([-6.0, ym, 0], [6.0, ym, 0], stroke_width=5, color=est.tenue),
                                Dot([-6.0, ym, 0], radius=0.12, color=est.tinta), Dot([6.0, ym, 0], radius=0.12, color=est.tinta),
                                texto(est, "Tijuana", 38, est.tinta).move_to([-5.0, ym - 0.6, 0]),
                                texto(est, "Cancún", 38, est.tinta).move_to([5.0, ym - 0.6, 0]),
                                texto(est, f"{DC.MEXICO_KM:,.0f} km".replace(",", " "), 38, est.tenue).move_to([0, ym - 0.6, 0])).set_z_index(8), pel, 6.2))
        cruce = lambda: u_de(pel, 7.2, 11.8)
        iss = punto(est.calido, 0.16).set_z_index(11)
        iss.add_updater(lambda m: m.move_to([-6.0 + 12.0 * cruce(), ym, 0]))
        self.add(aparece(iss, pel, 7.0))
        cola(self, iss, est.calido, n=24, ancho=8, z=10)
        self.add(Viva(est, lambda: f"{DC.MEXICO_MIN * cruce():.1f} min", [0, ym + 1.0, 0], 64, est.calido,
                      f_op=lambda: rampa(pel.t, 7.0)))
        self.add(aparece(VGroup(texto(est, "≈ 26 000 km/h", 64, est.acento, "cifra", "SEMIBOLD"),
                                texto(est, "auto en carretera: 100 km/h", 38, est.tenue)).arrange(DOWN, buff=0.3)
                         .move_to([0, -4.75, 0]).set_z_index(9), pel, 13.2))
        leyendas(self, est, pel, n, [
            ("La derivada es la pendiente", "de la gráfica de distancia sale la velocidad"),
            ("La ISS cruza México en 7 minutos y medio", "su sombra avanza 7 km cada segundo"),
            ("Su pendiente es 260 veces la de un auto", "en la misma gráfica, la línea es casi vertical")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 2 · La integral: sumar rebanadas (1 minuto de ISS) ═════════════════════════════════════════════════════════════════

class ReelCAIntegral(Scene):
    VAR = 1

    def construct(self):
        n = "ReelCAIntegral"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "La integral:\nsumar rebanadas", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        X0, X1, Y0, Y1 = -6.0, 6.0, -0.5, 4.6
        self.add(aparece(ejes(est, X0, X1, Y0, Y1, "tiempo", "velocidad"), pel, 0.2))
        v = lambda x: Y0 + 0.7 + 3.6 * (1 - np.exp(-(x - X0) / 3.5)) + 0.3 * np.sin(1.3 * x)
        xs = np.linspace(X0, X1, 160)
        self.add(aparece(polilinea([[x, v(x), 0] for x in xs], color=est.acento2, width=6).set_z_index(10), pel, 0.4))
        for j, (nb, t0, t1) in enumerate(((4, 1.0, 2.6), (8, 2.6, 4.2), (16, 4.2, 5.8), (48, 5.8, 12.4))):
            w = (X1 - X0) / nb
            barras = VGroup(*[Rectangle(width=w, height=max(v(X0 + (k + 0.5) * w) - Y0, 0.01)).set_fill(est.acento, 0.35)
                              .set_stroke(est.acento, 2 if nb < 40 else 0.8).move_to([X0 + (k + 0.5) * w, (v(X0 + (k + 0.5) * w) + Y0) / 2, 0])
                              for k in range(nb)]).set_z_index(9)
            self.add(aparece(barras, pel, t0, 0.4, hasta=t1 if j < 3 else None))
        self.add(aparece(texto(est, "área = distancia", 52, est.tinta, "titulo", "SEMIBOLD").move_to([1.2, 1.2, 0]).set_z_index(11), pel, 5.2))
        # un minuto: ISS vs. auto, sobre una regla de CDMX a Guadalajara
        y1, y2 = -2.3, -4.5
        L = 12.0
        self.add(aparece(VGroup(texto(est, "1 minuto de la ISS", 44, est.tinta).next_to([-6.0, y1 + 0.6, 0], RIGHT, buff=0),
                                texto(est, "1 minuto en auto", 44, est.tinta).next_to([-6.0, y2 + 0.6, 0], RIGHT, buff=0)).set_z_index(9), pel, 6.4))
        for y, frac, col, t0 in ((y1, 1.0, est.calido, 7.0), (y2, DC.AUTO_1MIN_KM / DC.ISS_1MIN_KM, est.acento2, 13.0)):
            b = Rectangle(width=L, height=0.65).set_fill(col, 0.9).set_stroke(width=0).set_z_index(9)
            b.add_updater(lambda m, y=y, frac=frac, t0=t0: m.stretch_to_fit_width(max(0.04, L * frac * rampa(pel.t, t0, 2.0))).move_to([-6.0, y - 0.15, 0], aligned_edge=LEFT))
            self.add(aparece(b, pel, t0, 0.3))
        self.add(aparece(texto(est, f"≈ {DC.ISS_1MIN_KM:.0f} km", 52, est.calido, "cifra", "SEMIBOLD").move_to([4.4, y1 + 0.62, 0]).set_z_index(10), pel, 8.8))
        self.add(aparece(VGroup(texto(est, "CDMX", 38, est.tenue).move_to([-5.4, y1 - 0.95, 0]),
                                texto(est, "Guadalajara", 38, est.tenue).move_to([4.7, y1 - 0.95, 0])).set_z_index(9), pel, 9.4))
        self.add(aparece(texto(est, f"≈ {DC.AUTO_1MIN_KM:.1f} km", 52, est.acento2, "cifra", "SEMIBOLD").move_to([-4.2, y2 - 0.95, 0]).set_z_index(10), pel, 14.5))
        leyendas(self, est, pel, n, [
            ("Área bajo la velocidad = distancia", "se suma en rebanadas cada vez más finas"),
            ("Un minuto de la ISS: 460 km", "como de la CDMX a Guadalajara, en línea recta"),
            ("Un auto, en ese minuto: 1.7 km", "integrar es sumar todo lo que se avanzó")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 3 · El máximo: saltar en la Luna ═══════════════════════════════════════════════════════════════════════════════════

class ReelCAMaximo(Scene):
    VAR = 2

    def construct(self):
        n = "ReelCAMaximo"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Saltar en\nla Luna", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        X0, X1, Y0, Y1 = -6.0, 6.0, -4.8, 3.8
        TMAX, HMAX = 4.2, 3.4
        self.add(aparece(ejes(est, X0, X1, Y0, Y1, "tiempo (s)", "altura (m)"), pel, 0.2))
        for k in range(1, 4):
            y = Y0 + (Y1 - Y0) * k / HMAX
            self.add(aparece(VGroup(DashedLine([X0, y, 0], [X1, y, 0], dash_length=0.15, stroke_width=1.5, color=est.tenue).set_opacity(0.4),
                                    texto(est, f"{k} m", 30, est.tenue).next_to([X0, y, 0], LEFT, buff=0.12)).set_z_index(7), pel, 0.3))
        P = lambda t, h: np.array([X0 + (X1 - X0) * t / TMAX, Y0 + (Y1 - Y0) * h / HMAX, 0])
        V0 = DC.V_SALTO

        def arco(g, dur, t_ini):
            def pts():
                tt = np.linspace(0, min(max(pel.t - t_ini, 0) * 1.0, dur), 60)
                return np.array([P(t, max(V0 * t - g * t * t / 2, 0)) for t in tt])
            return pts
        # Tierra: tres saltos rápidos (0.64 s cada uno, en tiempo real)
        for j in range(3):
            t_ini = 0.8 + 1.4 * j
            self.add(dibujo(pel, arco(9.80665, DC.T_AIRE_TIERRA_S, t_ini), t_ini, est.acento2, 6, 9))
        tope_t = P(V0 / 9.80665, DC.SALTO_TIERRA_M)
        self.add(aparece(VGroup(Line(tope_t + LEFT * 0.9, tope_t + RIGHT * 0.9, stroke_width=5, color=est.acento),
                                texto(est, "Tierra: 0.5 m", 36, est.acento2).next_to(tope_t + UP * 0.25, RIGHT, buff=0.6)).set_z_index(10), pel, 4.4))
        # Luna: un salto lento (3.9 s en el aire, en tiempo real)
        T_L = 6.6
        self.add(dibujo(pel, arco(1.62, DC.T_AIRE_LUNA_S, T_L), T_L, est.acento, 7, 10))
        astro = punto(est.tinta, 0.15).set_z_index(12)

        def mover(m):
            t = float(np.clip(pel.t - T_L, 0, DC.T_AIRE_LUNA_S))
            m.move_to(P(t, max(V0 * t - 1.62 * t * t / 2, 0)))
        astro.add_updater(mover); mover(astro)
        self.add(aparece(astro, pel, T_L - 0.3))
        tope = P(V0 / 1.62, DC.SALTO_LUNA_M)
        self.add(aparece(VGroup(Line(tope + LEFT * 1.8, tope + RIGHT * 1.8, stroke_width=6, color=est.acento),
                                texto(est, "pendiente = 0", 40, est.acento, "titulo", "SEMIBOLD").move_to(tope + UP * 0.6)).set_z_index(11), pel, T_L + V0 / 1.62))
        self.add(aparece(texto(est, f"Luna: {DC.SALTO_LUNA_M:.0f} m", 52, est.acento, "titulo", "SEMIBOLD").next_to(tope + RIGHT * 2.0, RIGHT, buff=0.2).set_z_index(11), pel, 9.4))
        self.add(aparece(VGroup(texto(est, f"en el aire: {DC.T_AIRE_LUNA_S:.1f} s en la Luna", 40, est.acento),
                                texto(est, f"{DC.T_AIRE_TIERRA_S:.1f} s en la Tierra", 40, est.acento2)).arrange(DOWN, buff=0.25)
                         .move_to([-0.3, -2.2, 0]).set_z_index(11), pel, 12.8))
        leyendas(self, est, pel, n, [
            ("Arriba, la velocidad vale cero", "la derivada se anula: ahí está el máximo"),
            ("En la Luna, el mismo salto sube 3 m", "la gravedad allá es 6 veces menor"),
            ("Y dura casi 4 segundos en el aire", "en la Tierra, dos tercios de segundo")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 4 · Una órbita a pasitos (método de Euler) ═════════════════════════════════════════════════════════════════════════

class ReelCAPasos(Scene):
    VAR = 0

    def construct(self):
        n = "ReelCAPasos"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Una órbita\na pasitos", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        C, R = np.array([0, 0.9, 0]), 3.2
        self.add(aparece(tierra(est, C, 1.0), pel, 0.2))
        self.add(aparece(DashedVMobject(Circle(radius=R).move_to(C).set_stroke(est.tenue, 3), num_dashes=60).set_z_index(7), pel, 0.4))
        self.add(aparece(texto(est, "órbita real", 38, est.tenue).move_to(C + np.array([R * 0.95, -R * 0.95, 0])).set_z_index(8), pel, 0.6))
        mal = C + np.column_stack([DC.PTS_MAL * R, np.zeros(len(DC.PTS_MAL))])
        bien = C + np.column_stack([DC.PTS_BIEN * R, np.zeros(len(DC.PTS_BIEN))])
        k_mal = lambda: int(round(DC.PASOS_MAL * u_de(pel, 0.8, 9.0)))

        def puntos_mal():
            k = k_mal() + 1
            return np.array([p for p in mal[:k] if zona(p)])
        self.add(dibujo(pel, puntos_mal, 0.8, ROJO, 6, 10, hasta=12.4))
        flecha = Arrow(ORIGIN, RIGHT).set_z_index(11)

        def act(m):
            k = min(k_mal(), DC.PASOS_MAL - 1)
            a, b = mal[k], mal[k + 1]
            m.become(Arrow(a, b, buff=0, stroke_width=6, color=ROJO, max_tip_length_to_length_ratio=0.2).set_z_index(11))
            fundir(m, rampa(pel.t, 0.8) * (1 - rampa(pel.t, 12.0)) * zona(b))
        flecha.add_updater(act); act(flecha); self.add(flecha)
        puntos = VGroup(*[Dot(p, radius=0.08, color=ROJO) for p in mal]).set_z_index(11)
        puntos.add_updater(lambda m: [fundir(d, float(i <= k_mal()) * zona(d.get_center()) * (1 - rampa(pel.t, 12.4))) for i, d in enumerate(m)])
        self.add(puntos)
        self.add(aparece(texto(est, "20 pasos por vuelta", 48, ROJO, "titulo", "SEMIBOLD").move_to([0, -4.0, 0]).set_z_index(11), pel, 1.0, hasta=12.4))
        # 2000 pasos: casi cierra
        kb = lambda: int(len(bien) * u_de(pel, 12.8, 16.0))
        self.add(dibujo(pel, lambda: bien[:max(kb(), 2)], 12.8, est.acento, 7, 10))
        self.add(aparece(VGroup(texto(est, "2 000 pasos: error 4 %", 48, est.acento, "titulo", "SEMIBOLD"),
                                texto(est, "20 000 pasos: error 0.4 %", 48, est.acento2, "titulo", "SEMIBOLD")).arrange(DOWN, buff=0.3)
                         .move_to([0, -4.3, 0]).set_z_index(11), pel, 15.6))
        leyendas(self, est, pel, n, [
            ("La computadora avanza a pasitos", "sigue la flecha un momento y vuelve a calcular"),
            ("Con pasos grandes, el error crece", "con 20 pasos por vuelta, el satélite «se escapa»"),
            ("10 veces más pasos, 10 veces menos error", "por eso los simuladores usan métodos más finos")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 5 · Gravedad de carrusel (a = ω²r) ═════════════════════════════════════════════════════════════════════════════════

class ReelCAGiro(Scene):
    VAR = 1

    def construct(self):
        n = "ReelCAGiro"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Gravedad\nde carrusel", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        C, R = np.array([0, 1.1, 0]), 3.6
        ang = lambda: 2 * np.pi * pel.v / DC.SEG_VUELTA                # 3 vueltas por minuto, en tiempo real
        anillo = VGroup(Annulus(inner_radius=R - 0.25, outer_radius=R + 0.25).set_fill("#2A3050", 1).set_stroke(est.tenue, 2),
                        Circle(radius=0.5).set_fill("#2A3050", 1).set_stroke(est.tenue, 2),
                        *[Line([0.5, 0, 0], [R - 0.25, 0, 0], stroke_width=8, color="#3A4170").rotate(k * PI / 2, about_point=ORIGIN) for k in range(4)])
        anillo.move_to(C).set_z_index(7)
        anillo.add_updater(lambda m: m.become(VGroup(
            Annulus(inner_radius=R - 0.25, outer_radius=R + 0.25).set_fill("#2A3050", 1).set_stroke(est.tenue, 2),
            Circle(radius=0.5).set_fill("#2A3050", 1).set_stroke(est.tenue, 2),
            *[Line([0.5, 0, 0], [R - 0.25, 0, 0], stroke_width=8, color="#3A4170").rotate(k * PI / 2 + ang(), about_point=ORIGIN) for k in range(4)])
            .shift(C).set_z_index(7)))
        self.add(aparece(anillo, pel, 0.2))
        pos = lambda: C + (R - 0.25) * np.array([np.cos(ang() - PI / 4), np.sin(ang() - PI / 4), 0])
        persona = VGroup(Dot(radius=0.16, color=est.tinta), Line(ORIGIN, UP * 0.7, stroke_width=6, color=est.tinta)).set_z_index(12)

        def act_p(m):
            p = pos(); dentro = (C - p) / np.linalg.norm(C - p)
            m.become(VGroup(Dot(p + dentro * 0.75, radius=0.16, color=est.tinta),
                            Line(p, p + dentro * 0.6, stroke_width=7, color=est.tinta)).set_z_index(12))
        persona.add_updater(act_p); act_p(persona)
        self.add(aparece(persona, pel, 0.6))

        def vec(tipo):
            def act(m):
                p = pos(); r = (p - C) / np.linalg.norm(p - C)
                d = np.array([-r[1], r[0], 0]) if tipo == "v" else -r
                col, L = (est.acento, 2.0) if tipo == "v" else (est.acento2, 1.7)
                m.become(Arrow(p, p + d * L, buff=0, stroke_width=7, color=col, max_tip_length_to_length_ratio=0.25).set_z_index(13))
            a = Arrow(ORIGIN, RIGHT).set_z_index(13); a.add_updater(act); act(a)
            return a
        self.add(aparece(vec("v"), pel, 1.6), aparece(vec("a"), pel, 3.4))
        self.add(aparece(VGroup(Line([-6.2, -3.4, 0], [-5.4, -3.4, 0], stroke_width=7, color=est.acento),
                                texto(est, "velocidad", 36, est.acento).next_to([-5.3, -3.4, 0], RIGHT, buff=0.15),
                                Line([-1.2, -3.4, 0], [-0.4, -3.4, 0], stroke_width=7, color=est.acento2),
                                texto(est, "su derivada: aceleración", 36, est.acento2).next_to([-0.3, -3.4, 0], RIGHT, buff=0.15)).set_z_index(11), pel, 3.4))
        self.add(aparece(texto(est, "radio: 100 m", 36, est.tinta).move_to(C + DOWN * 1.05).set_z_index(9), pel, 6.4))
        self.add(aparece(VGroup(texto(est, "1 g", 72, est.acento, "cifra", "BOLD"),
                                texto(est, f"≈ {DC.RPM_1G:.0f} vueltas por minuto", 44, est.tinta, "titulo", "SEMIBOLD")).arrange(RIGHT, buff=0.5)
                         .move_to([0, -4.75, 0]).set_z_index(11), pel, 7.0, hasta=12.4))
        self.add(aparece(VGroup(texto(est, "10 m de radio:", 40, est.tenue),
                                texto(est, f"{DC.RPM_10M:.1f} vueltas por minuto", 48, est.calido, "titulo", "SEMIBOLD")).arrange(RIGHT, buff=0.3)
                         .move_to([0, -4.75, 0]).set_z_index(11), pel, 13.0))
        leyendas(self, est, pel, n, [
            ("Girar es cambiar de dirección", "esa derivada es una aceleración hacia el centro"),
            ("100 m de radio y 3 vueltas por minuto", "los pies sentirían el peso de la Tierra"),
            ("Más chico, más rápido: mareo", "por eso las estaciones que giran serían enormes")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 6 · Marte cada 26 meses (tasas que se restan) ═════════════════════════════════════════════════════════════════════

class ReelCATasas(Scene):
    VAR = 2

    def construct(self):
        n = "ReelCATasas"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Marte cada\n26 meses", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        C, RE, RM = np.array([0, 0.9, 0]), 2.4, 4.0
        TE = 3.6                                                    # segundos de video por año terrestre
        TM = TE * DC.T_MARTE_D / DC.T_TIERRA_D
        T_AL = 1.0                                                   # alineados en t = 1 s
        S = 1 / (1 / TE - 1 / TM)
        self.add(aparece(VGroup(Circle(radius=0.45).set_fill(est.acento, 1).set_stroke(width=0),
                                Circle(radius=0.75).set_fill(est.acento, 0.18).set_stroke(width=0)).move_to(C).set_z_index(8), pel, 0.2))
        for r in (RE, RM):
            self.add(aparece(Circle(radius=r).move_to(C).set_stroke(est.tenue, 2, 0.5).set_z_index(7), pel, 0.3))
        th = lambda T: 2 * np.pi * (pel.t - T_AL) / T + PI / 6
        PE = lambda: C + RE * np.array([np.cos(th(TE)), np.sin(th(TE)), 0])
        PM = lambda: C + RM * np.array([np.cos(th(TM)), np.sin(th(TM)), 0])
        enlace = Line(ORIGIN, RIGHT).set_z_index(9)
        alineado = lambda: max(0.0, 1 - abs(((th(TE) - th(TM) + PI) % (2 * PI)) - PI) / 0.35)
        enlace.add_updater(lambda m: fundir(m.become(Line(C, PM(), stroke_width=5, color=est.calido).set_z_index(9)), alineado() * rampa(pel.t, 0.4)))
        self.add(enlace)
        e = punto(AZUL, 0.18); e.add_updater(lambda m: m.move_to(PE())); self.add(aparece(e, pel, 0.4))
        m_ = punto(ROJO, 0.16); m_.add_updater(lambda m: m.move_to(PM())); self.add(aparece(m_, pel, 0.4))
        cola(self, e, AZUL, n=30, ancho=6); cola(self, m_, ROJO, n=30, ancho=6)
        self.add(aparece(VGroup(texto(est, "Tierra", 34, "#8FD8FF"), texto(est, "Marte", 34, ROJO)).arrange(RIGHT, buff=0.6)
                         .move_to([-4.6, 4.9, 0]).set_z_index(9), pel, 0.6))
        self.add(Viva(est, lambda: f"mes {max(0.0, (pel.t - T_AL) * 12 / TE):.0f}", [4.8, 4.9, 0], 44, est.tinta, rol="titulo",
                      f_op=lambda: rampa(pel.t, 0.8)))
        self.add(Viva(est, lambda: "¡alineados!" if alineado() > 0.2 else " ", [4.6, 4.15, 0], 48, est.calido, rol="titulo",
                      f_op=lambda: rampa(pel.t, 0.8) * min(1.0, alineado() * 2)))
        self.add(aparece(VGroup(texto(est, "1/12 − 1/22.6 = 1/25.6", 52, est.acento, "cifra", "SEMIBOLD"),
                                texto(est, "vueltas por mes que se restan", 36, est.tenue)).arrange(DOWN, buff=0.25)
                         .move_to([0, -4.7, 0]).set_z_index(10), pel, 7.5))
        leyendas(self, est, pel, n, [
            ("Cada planeta gira a su ritmo", "la Tierra en 12 meses, Marte en casi 23"),
            ("La Tierra alcanza a Marte cada 26 meses", "sus velocidades de giro se restan"),
            ("Por eso hay misiones a Marte cada 26 meses", "si se pierde la ventana, toca esperar otra vuelta")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 7 · La mitad cada 88 años (el plutonio del Voyager) ════════════════════════════════════════════════════════════════

class ReelCAPlutonio(Scene):
    VAR = 0

    def construct(self):
        n = "ReelCAPlutonio"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "La mitad\ncada 88 años", self.VAR, chip_txt="Datos públicos", **SERIE)
        X0, X1, Y0, Y1 = -6.0, 6.0, -1.2, 4.4
        AN = 300.0
        self.add(aparece(ejes(est, X0, X1, Y0, Y1, "años", "calor"), pel, 0.2))
        P = lambda a: np.array([X0 + (X1 - X0) * a / AN, Y0 + (Y1 - Y0 - 0.2) * 2 ** (-a / DC.PU_MITAD_ANIOS), 0])
        self.add(dibujo(pel, lambda: np.array([P(a) for a in np.linspace(0, AN * u_de(pel, 0.6, 5.0) + 1e-3, 120)]), 0.6, est.acento, 7, 10))
        for k in range(1, 4):
            a = k * DC.PU_MITAD_ANIOS
            p = P(a)
            g = VGroup(DashedLine([p[0], Y0, 0], p, dash_length=0.12, stroke_width=2, color=est.tenue),
                       DashedLine([X0, p[1], 0], p, dash_length=0.12, stroke_width=2, color=est.tenue),
                       texto(est, f"1/{2 ** k}", 34, est.acento2).move_to(p + UP * 0.45 + RIGHT * 0.35),
                       texto(est, f"{a:.0f}", 30, est.tenue).move_to([p[0], Y0 - 0.4, 0])).set_z_index(9)
            self.add(aparece(g, pel, 1.6 + 1.0 * k))
        pv = P(DC.VOYAGER_ANIOS)
        self.add(aparece(VGroup(Dot(pv, radius=0.16, color=est.calido),
                                texto(est, f"Voyager, {DC.VOYAGER_ANIOS} años: {100 * DC.CALOR_RESTANTE:.0f} %", 44, est.calido, "titulo", "SEMIBOLD")
                                .next_to(pv + RIGHT * 0.3 + UP * 0.55, RIGHT, buff=0.2)).set_z_index(11), pel, 7.0))
        # electricidad: 470 W → 230 W
        L = 12.0
        filas = [("calor del plutonio", DC.CALOR_RESTANTE, est.acento, -2.6, 8.4), ("electricidad", DC.VOYAGER_W_HOY / DC.VOYAGER_W0, est.calido, -4.4, 13.2)]
        for txt, frac, col, y, t0 in filas:
            self.add(aparece(VGroup(Rectangle(width=L, height=0.55).set_fill(col, 0.12).set_stroke(col, 2).move_to([0, y - 0.55, 0]),
                                    texto(est, txt, 40, est.tinta).next_to([-6.0, y + 0.1, 0], RIGHT, buff=0)).set_z_index(9), pel, t0))
            b = Rectangle(width=L, height=0.55).set_fill(col, 0.85).set_stroke(width=0).set_z_index(10)
            b.add_updater(lambda m, frac=frac, t0=t0, y=y: m.stretch_to_fit_width(max(0.04, L * (1 - (1 - frac) * rampa(pel.t, t0 + 0.4, 1.6)))).move_to([-6.0, y - 0.55, 0], aligned_edge=LEFT))
            self.add(aparece(b, pel, t0))
        self.add(aparece(texto(est, f"{DC.VOYAGER_W0} W → {DC.VOYAGER_W_HOY} W", 40, est.calido, "cifra", "SEMIBOLD").move_to([3.4, -4.3, 0]).set_z_index(11), pel, 14.6))
        leyendas(self, est, pel, n, [
            ("El plutonio pierde la mitad cada 88 años", "siempre la misma fracción: eso es una exponencial"),
            ("El Voyager lleva 49 años viajando", "su plutonio aún da 68 % del calor"),
            ("Pero su electricidad ya cayó a la mitad", "las piezas que convierten el calor también se gastan")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 8 · Cada 5.5 km, la mitad del aire ════════════════════════════════════════════════════════════════════════════════

class ReelCAAire(Scene):
    VAR = 1

    def construct(self):
        n = "ReelCAAire"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Cada 5.5 km,\nla mitad del aire", self.VAR, chip_txt="Datos públicos", **SERIE)
        Y0, Y1, KM = -5.3, 4.9, 30.0
        Yk = lambda km: Y0 + (Y1 - Y0) * km / KM
        XC0, XC1 = -0.6, 2.8
        self.add(aparece(VGroup(Line([XC0 - 0.2, Y0, 0], [XC0 - 0.2, Y1, 0], stroke_width=4, color=est.tenue),
                                texto(est, "altura", 32, est.tenue).move_to([XC0 - 0.2, Y1 + 0.35, 0])).set_z_index(8), pel, 0.2))
        rng = np.random.default_rng(8)
        mol = []
        for _ in range(900):
            h = rng.exponential(DC.MITAD_AIRE_KM / np.log(2))
            if h < KM:
                mol.append((rng.uniform(XC0, XC1), Yk(h), rng.uniform(0, 2 * np.pi)))
        puntos = VGroup(*[Dot([x, y, 0], radius=0.045, color="#8FD8FF") for x, y, _ in mol]).set_z_index(9)
        fases = [f for _, _, f in mol]
        base = [np.array([x, y, 0]) for x, y, _ in mol]

        def agitar(m):
            for d, b, f in zip(m, base, fases):
                d.move_to(b + 0.05 * np.array([np.sin(3 * pel.v + f), np.cos(2.3 * pel.v + 2 * f), 0]))
        puntos.add_updater(agitar)
        self.add(aparece(puntos, pel, 0.4, 1.2))
        for k in range(1, 6):
            km = k * DC.MITAD_AIRE_KM
            y = Yk(km)
            self.add(aparece(VGroup(DashedLine([XC0 - 0.2, y, 0], [XC1 + 0.1, y, 0], dash_length=0.15, stroke_width=2, color=est.acento),
                                    VGroup(texto(est, f"{km:g} km", 32, est.tenue), texto(est, f"1/{2 ** k}", 40, est.acento, "cifra", "SEMIBOLD"))
                                    .arrange(RIGHT, buff=0.25).next_to([XC0 - 0.35, y, 0], LEFT, buff=0)).set_z_index(10),
                             pel, 1.6 + 0.8 * k))
        ye, ya = Yk(DC.EVEREST_KM), Yk(10.5)
        self.add(aparece(VGroup(polilinea([[-6.8, Y0, 0], [-6.0, ye - 1.1, 0], [-5.4, ye, 0], [-4.9, ye - 0.8, 0], [-4.2, Y0, 0]],
                                          color=est.tinta, width=4),
                                texto(est, "Everest", 36, est.tinta).move_to([-5.4, ye + 0.95, 0]),
                                texto(est, "≈ 1/3", 40, est.calido, "cifra", "SEMIBOLD").move_to([-5.4, ye + 0.4, 0])).set_z_index(10), pel, 7.0))
        self.add(aparece(VGroup(polilinea([[3.7, ya, 0], [5.6, ya, 0]], color=est.tinta, width=6),
                                polilinea([[4.0, ya, 0], [3.7, ya + 0.4, 0]], color=est.tinta, width=5),
                                polilinea([[4.8, ya, 0], [4.4, ya - 0.45, 0]], color=est.tinta, width=5),
                                DashedLine([XC1 + 0.1, ya, 0], [3.6, ya, 0], dash_length=0.1, stroke_width=2, color=est.calido),
                                texto(est, "avión ≈ 1/4", 38, est.calido, "titulo", "SEMIBOLD").move_to([4.8, ya - 0.85, 0])).set_z_index(10), pel, 9.0))
        self.add(aparece(VGroup(Arrow([5.0, 1.6, 0], [5.0, 4.9, 0], buff=0, stroke_width=7, color=est.acento2),
                                texto(est, "100 km:", 44, est.acento2, "titulo", "SEMIBOLD").move_to([5.0, 1.0, 0]),
                                texto(est, "menos de una", 36, est.tinta).move_to([5.0, 0.35, 0]),
                                texto(est, "millonésima", 36, est.tinta).move_to([5.0, -0.15, 0])).set_z_index(10), pel, 13.0))
        leyendas(self, est, pel, n, [
            ("Subes 5.5 km y queda la mitad", "cada tramo igual pierde la misma fracción"),
            ("En el Everest respiras un tercio", "y los aviones vuelan con un cuarto del aire"),
            ("A 100 km: menos de una millonésima", "ahí se dice que empieza el espacio")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 9 · ¿Hasta dónde se ve? (aproximación d ≈ √(2Rh)) ════════════════════════════════════════════════════════════════

class ReelCAHorizonte(Scene):
    VAR = 2

    def construct(self):
        n = "ReelCAHorizonte"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Hasta dónde\nse ve?", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        R = 9.0
        C = np.array([0, -1.2 - R, 0])                               # la cima de la Tierra en y = −1.2
        A_ = 0.92
        arco = [C + R * np.array([np.cos(PI / 2 + a), np.sin(PI / 2 + a), 0]) for a in np.linspace(-A_, A_, 90)]
        relleno = Polygon(*arco, [arco[-1][0], -5.6, 0], [arco[0][0], -5.6, 0]).set_fill(AZUL, 0.30).set_stroke(width=0)
        self.add(aparece(VGroup(relleno, polilinea(arco, color="#8FD8FF", width=5)).set_z_index(7), pel, 0.2))
        etapas = [(0.0, 0.15, "playa · 2 m", DC.HORIZONTE_PLAYA_KM), (6.0, 1.3, "avión · 10 km", DC.HORIZONTE_AVION_KM),
                  (12.5, 4.6, "ISS · 420 km", DC.HORIZONTE_ISS_KM)]

        def h_pant():
            h = etapas[0][1]
            for t0, hh, _, _ in etapas[1:]:
                h += (hh - h) * rampa(pel.t, t0, 1.6)
            return h

        def act(m):
            h = h_pant()
            o = C + UP * (R + h)
            th = np.arccos(R / (R + h))
            izq = C + R * np.array([-np.sin(th), np.cos(th), 0]); der = C + R * np.array([np.sin(th), np.cos(th), 0])
            visto = Arc(radius=R, start_angle=PI / 2 - th, angle=2 * th, arc_center=C).set_stroke(est.acento, 12)
            m.become(VGroup(Line(o, izq, stroke_width=4, color=est.acento), Line(o, der, stroke_width=4, color=est.acento), visto,
                            Dot(o, radius=0.16, color=est.tinta), Dot(izq, radius=0.1, color=est.acento), Dot(der, radius=0.1, color=est.acento)).set_z_index(10))
        g = VGroup(); g.add_updater(act); act(g)
        self.add(aparece(g, pel, 0.6))
        for k, (t0, _, txt, km) in enumerate(etapas):
            hasta = etapas[k + 1][0] - 0.2 if k < 2 else None
            self.add(aparece(VGroup(texto(est, txt, 42, est.tinta, "titulo", "SEMIBOLD"),
                                    texto(est, f"horizonte a {km:,.0f} km".replace(",", " "), 52, est.acento, "cifra", "SEMIBOLD")).arrange(DOWN, buff=0.25)
                             .move_to([0, 4.4, 0]).set_z_index(11), pel, t0 + 0.8, hasta=hasta))
        self.add(aparece(texto(est, "d ≈ √(2 · R · h)", 48, est.acento2, "cifra", "SEMIBOLD").move_to([0, -4.6, 0]).set_z_index(11), pel, 7.6))
        leyendas(self, est, pel, n, [
            ("En la playa, el horizonte está a 5 km", "la Tierra se curva y esconde lo demás"),
            ("Desde un avión, a unos 360 km", "la raíz crece despacio: d ≈ √(2·R·h)"),
            ("Desde la ISS, a 2 350 km", "como de Tijuana a la Ciudad de México")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 10 · Un túnel que atraviesa la Tierra (x'' = −k·x) ═══════════════════════════════════════════════════════════════

class ReelCATunel(Scene):
    VAR = 0

    def construct(self):
        n = "ReelCATunel"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Un túnel que\natraviesa la Tierra", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        C, R = np.array([0, 0.3, 0]), 4.4
        PER = 8.0                                                     # segundos de video por ida y vuelta (84 min reales)
        T0 = 1.0
        self.add(aparece(VGroup(Circle(radius=R * 1.04).set_fill(AZUL, 0.15).set_stroke(width=0),
                                Circle(radius=R).set_fill(est.mezcla(est.fondo, AZUL, 0.55), 1).set_stroke("#8FD8FF", 3),
                                Circle(radius=R * 0.55).set_fill(est.mezcla(est.fondo, est.calido, 0.25), 1).set_stroke(width=0),
                                Circle(radius=R * 0.2).set_fill(est.mezcla(est.fondo, est.calido, 0.45), 1).set_stroke(width=0)).move_to(C).set_z_index(7), pel, 0.2))
        self.add(aparece(Rectangle(width=0.5, height=2 * R).set_fill(est.fondo, 1).set_stroke(est.tenue, 2).move_to(C).set_z_index(8), pel, 0.5))
        fase = lambda: 2 * np.pi * max(pel.t - T0, 0) / PER
        y_bola = lambda: C[1] + R * 0.97 * np.cos(fase())
        bola = punto(est.acento, 0.17).set_z_index(12)
        bola.add_updater(lambda m: m.move_to([C[0], y_bola(), 0]))
        self.add(aparece(bola, pel, 0.6))

        def acel(m):
            y = y_bola() - C[1]
            m.become(Arrow([C[0] + 0.55, y_bola(), 0], [C[0] + 0.55, y_bola() - 0.55 * y, 0], buff=0, stroke_width=7,
                           color=est.acento2, max_tip_length_to_length_ratio=0.3).set_z_index(12))
            fundir(m, rampa(pel.t, 2.0) * min(1.0, abs(y) / 0.6))
        fa = Arrow(ORIGIN, RIGHT); fa.add_updater(acel); acel(fa); self.add(fa)
        self.add(aparece(texto(est, "x'' = −k · x", 48, est.acento2, "cifra", "SEMIBOLD").move_to([-4.2, 4.85, 0]).set_z_index(11), pel, 2.4))
        self.add(Viva(est, lambda: f"{min(max(pel.t - T0, 0) / (PER / 2), 1.0) * DC.TUNEL_MIN:.0f} min", [4.4, 4.85, 0], 56, est.acento,
                      f_op=lambda: rampa(pel.t, 1.0) * (1 - rampa(pel.t, 12.4))))
        self.add(aparece(texto(est, "al otro lado: 42 min", 52, est.acento, "titulo", "SEMIBOLD").move_to([0, -4.75, 0]).set_z_index(11), pel, T0 + PER / 2 + 0.2, hasta=12.4))
        # la sombra de un satélite que gira a ras del suelo: mismo ritmo
        sat = punto(est.calido, 0.16).set_z_index(12)
        sat.add_updater(lambda m: m.move_to(C + R * 1.04 * np.array([np.sin(fase()), np.cos(fase()), 0])))
        self.add(aparece(sat, pel, 12.8))
        cola(self, sat, est.calido, n=28, ancho=7, z=11)
        guia = Line(ORIGIN, RIGHT).set_z_index(11)
        guia.add_updater(lambda m: fundir(m.become(Line(sat.get_center(), [C[0] + 1e-3, y_bola(), 0], stroke_width=3, color=est.calido).set_z_index(11)),
                                          rampa(pel.t, 13.2)))
        self.add(guia)
        self.add(aparece(texto(est, f"órbita a ras del suelo: {DC.ORBITA_RAS_MIN:.0f} min", 44, est.calido, "titulo", "SEMIBOLD").move_to([0, -4.75, 0]).set_z_index(11), pel, 13.4))
        leyendas(self, est, pel, n, [
            ("Cae hacia el centro, cada vez más rápido", "la fuerza crece con la distancia al centro"),
            ("Llega al otro lado en 42 minutos", "y regresa: oscila para siempre, si no hay aire"),
            ("Es el ritmo de una órbita a ras del suelo", "la sombra de un satélite que gira")])
        cerrar_serie(self, est, pel, self.VAR)

import sys
from pathlib import Path

sys.path.insert(0, "/workspace/studio/content/manim_extensions")
_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *

import divulgacion_fisica as F
from estilo_reel import (Estilo, Pelicula, Viva, cabecera, chip, chip_arriba, cierre_logo, fondo_orbital, leyenda, texto)
from reels_promo import polilinea, suave, ventana

# Reels de DIVULGACIÓN (9:16), solo física de libro: nada de la tesis ni de clientes. Cada cifra en pantalla se calcula
# en divulgacion_fisica.py (el audio usa la misma línea de tiempo).
#
# RONDA 5 (2026-10-07) — estructura de cada reel: título (H0) → CUERPO a ritmo de lectura que termina en una PAUSA con el
# mensaje → cierre con el LOGO de Co.De sobre el fondo Órbita → el logo se DISUELVE en el título del inicio, así el último
# cuadro es igual al primero y el loop no se corta. El reloj `pel.t` del cuerpo vale 0 durante el título y bajo el logo.
# Fondo: tema Órbita, estrellas en capas, sin marco; la animación usa todo el cuadro (x ±6.6, y −5.6…5.2).


def preparar(escena, tema, tb, kicker, titulo, var=0):
    est = Estilo.de(tema)
    pel = Pelicula(escena, tb)
    fondo_orbital(escena, est, pel.V, var, tiempo=lambda: pel.v)
    cabecera(escena, est, kicker, titulo)
    return est, pel


def cerrar(escena, est, pel, var=0):
    """Fin de construct(): sostiene el cuerpo y encadena el logo (que luego se disuelve en el título)."""
    escena.wait(F.H0 + pel.TB)
    cierre_logo(escena, est, pel, var)


def tierra(est, radio, centro):
    disco = Circle(radius=radio, stroke_width=2.5, stroke_color=est.tierra_borde, fill_color=est.tierra, fill_opacity=1)
    g = VGroup(disco)
    if not est.claro:
        g.add_to_back(Circle(radius=radio * 1.035, stroke_width=6, stroke_color=est.acento).set_stroke(opacity=0.12))
    return g.move_to(centro).set_z_index(3)


def punto(color, r=0.12):
    return VGroup(Dot(radius=r * 2.6, color=color).set_opacity(0.16), Dot(radius=r, color=color)).set_z_index(9)


def cola(escena, objeto, color, n=26, ancho=6.0, z=8, salto=2.5):
    """Estela de cometa detrás de `objeto` (un `punto`): n tramos que se desvanecen. Si el objeto salta (el reloj se
    reinicia bajo el logo) la estela se borra en vez de dibujar una línea larga."""
    hist = []
    tramos = VGroup(*[Line(ORIGIN, RIGHT * 0.01) for _ in range(n)]).set_z_index(z)

    def actualizar(m):
        c = objeto.get_center().copy()
        if hist and np.linalg.norm(c - hist[-1]) > salto:
            hist.clear()
        if not hist or np.linalg.norm(c - hist[-1]) > 1e-3:
            hist.append(c)
        del hist[:-n - 1]
        vivo = objeto[1].get_fill_opacity()
        for i, ln in enumerate(m):
            j = len(hist) - n + i
            if j < 1 or j >= len(hist):
                ln.set_stroke(opacity=0)
                continue
            f = (i + 1) / n
            ln.put_start_and_end_on(hist[j - 1], hist[j])
            ln.set_stroke(color=color, width=ancho * f, opacity=0.65 * f ** 1.6 * vivo)
    tramos.add_updater(actualizar)
    escena.add(tramos)
    return tramos


def miles(x):
    return f"{x:,.0f}".replace(",", " ")


def antena(est, x, y, escala=0.16, color=None):
    return Triangle(fill_color=color or est.tinta, fill_opacity=1, stroke_width=0).scale(escala).move_to([x, y, 0]).set_z_index(6)


FIN = 3.0          # las leyendas finales llegan hasta TB + FIN: se sostienen hasta que el logo las cubre


# ══ 1 · ¿Por qué un satélite no se cae? (cañón de Newton) ═════════════════════════════════════════

class ReelNoSeCae(Scene):
    TEMA = "orbita"
    VAR = 0

    def construct(self):
        TB = F.NEWTON_T
        est, pel = preparar(self, self.TEMA, TB, "Física orbital", "¿Por qué un satélite\nno se cae?", self.VAR)
        chip_arriba(self, est, "Sin aire · experimento de Newton")

        R, C = 4.7, np.array([0.0, -0.65, 0.0])
        pos = lambda th, r: C + R * r * np.array([np.sin(th), np.cos(th), 0])
        self.add(tierra(est, R, C))
        cima = pos(0, F.N_R0)
        monte = Polygon(pos(-0.2, 0.99), cima + DOWN * 0.04, pos(0.2, 0.99), stroke_width=0, fill_color=est.tierra_borde,
                        fill_opacity=1).set_z_index(4)
        canon = RoundedRectangle(corner_radius=0.07, width=0.8, height=0.26, stroke_width=0, fill_color=est.tinta,
                                 fill_opacity=1).move_to(cima + RIGHT * 0.22 + UP * 0.08).set_z_index(6)
        self.add(monte, canon)

        tiros = []
        for k, t0, dur in F.NEWTON_PLAN:
            ts, th, r = F.newton_tiro(k)
            pts = np.array([pos(a, b) for a, b in zip(th, r)])
            color = est.acento if k == 1.0 else est.tenue
            traza, bala = VMobject().set_z_index(7), punto(color, 0.1)
            impacto = Dot(pts[-1], radius=0.09, color=est.calido).set_z_index(8)
            self.add(traza, bala, impacto)
            cola(self, bala, color)
            tiros.append((k, t0, dur, ts, pts, color, traza, bala, impacto))

        def mover(_m):
            t = pel.t
            for k, t0, dur, ts, pts, color, traza, bala, impacto in tiros:
                u = t - t0
                if u <= 0:
                    traza.clear_points(); bala.set_opacity(0); impacto.set_opacity(0)
                    continue
                vuela = u < dur
                i = max(1, min(int(np.searchsorted(ts, min(u, dur))), len(pts) - 1))
                traza.set_points_as_corners(pts[: i + 1])
                traza.set_stroke(color=color, width=4 if vuela else 3, opacity=0.95 if vuela else 0.45).set_fill(opacity=0)
                if k == 1.0 and not vuela:                           # ya en órbita: sigue dando vueltas, sin parar
                    i = max(1, min(int(np.searchsorted(ts, (u - dur) % dur)), len(pts) - 1))
                    visible = True
                else:
                    visible = vuela
                bala.move_to(pts[i])
                bala[0].set_opacity(0.16 if visible else 0)
                bala[1].set_opacity(1 if visible else 0)
                impacto.set_opacity(1 if (not vuela and k < 1) else 0)
        canon.add_updater(mover)

        def rapidez():
            k = F.N_K[0]
            for kk, t0, _ in F.NEWTON_PLAN:
                if pel.t >= t0 - 0.3:
                    k = kk
            return f"{k * F.N_V_SUP:.1f} km/s"
        self.add(Viva(est, rapidez, cima + LEFT * 2.6 + DOWN * 0.1, 56, est.acento))

        t_orb = F.NEWTON_PLAN[-1][1]
        leyenda(self, est, pel, "Más rápido, cae más lejos", "pero igual termina en el suelo", 0.0, t_orb - 0.4)
        leyenda(self, est, pel, f"A {F.N_V_SUP:.1f} km/s ya no toca el suelo", "la Tierra se curva tan rápido como cae", t_orb - 0.4, t_orb + 5.6)
        leyenda(self, est, pel, "Un satélite siempre está cayendo", "…y nunca llega al suelo", t_orb + 5.6, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 2 · Tres alturas, a escala (LEO · MEO · GEO) ══════════════════════════════════════════════════

class ReelTresAlturas(Scene):
    TEMA = "orbita"
    VAR = 1

    def construct(self):
        T, TB = F.ALT_T, F.ALT_TB
        est, pel = preparar(self, self.TEMA, TB, "Órbitas a escala", "¿A qué altura\nvuelan los satélites?", self.VAR)
        chip_arriba(self, est, "Distancias a escala", est.acento)

        C = np.array([0.0, -0.3, 0.0])
        s = 5.3 / F.ALT_A["GEO"]
        self.add(tierra(est, F.R_T * s, C))
        colores = {"LEO": est.acento, "MEO": est.tinta, "GEO": est.calido}
        anillos, sats = {}, {}
        for n, a in F.ALT_A.items():
            anillos[n] = Circle(radius=a * s, stroke_width=2.5, stroke_color=colores[n]).move_to(C).set_z_index(4)
            sats[n] = punto(colores[n], 0.11 if n != "LEO" else 0.08)
            self.add(anillos[n], sats[n])
            cola(self, sats[n], colores[n], n=22 if n == "GEO" else 26, ancho=5.0)
        for n, ang in (("MEO", 205), ("GEO", 215)):
            p = C + F.ALT_A[n] * s * np.array([np.cos(np.deg2rad(ang)), np.sin(np.deg2rad(ang)), 0])
            self.add(texto(est, n, 36, colores[n], "cuerpo", "SEMIBOLD").next_to(p, LEFT, buff=0.18).set_z_index(10))
        lleo = texto(est, "LEO", 36, est.acento, "cuerpo", "SEMIBOLD").move_to(C + np.array([2.2, -1.25, 0])).set_z_index(10)
        self.add(lleo, Line(lleo.get_left() + LEFT * 0.08, C + F.ALT_A["LEO"] * s * np.array([0.8, -0.6, 0]), stroke_width=2.2,
                            color=est.acento).set_opacity(0.7).set_z_index(10))

        estacion = VMobject().set_z_index(8)
        enlace = DashedLine(ORIGIN, RIGHT, stroke_width=2, color=est.calido, dash_length=0.12).set_z_index(5)
        self.add(estacion, enlace)
        ventanas = dict(zip(("LEO", "MEO", "GEO"), F.ALT_VENTANAS))

        def mover(_m):
            t = pel.t
            for n, vueltas in F.ALT_VUELTAS.items():
                th = np.pi / 2 + 2 * np.pi * vueltas * t / T
                sats[n].move_to(C + F.ALT_A[n] * s * np.array([np.cos(th), np.sin(th), 0]))
            fin = suave((t - ventanas["GEO"][1]) / 0.6)                  # al final: las tres alturas resaltan juntas
            for n, (a, b) in ventanas.items():
                o = max(ventana(t, a, b, 0.6, 1e9), 0.55 * fin)
                anillos[n].set_stroke(width=2.2 + 2.6 * o, opacity=0.3 + 0.7 * o)
            th = np.pi / 2 + 2 * np.pi * t / T                           # la Tierra gira una vez por día sidéreo
            u = np.array([np.cos(th), np.sin(th), 0])
            estacion.become(Triangle(fill_color=est.tinta, fill_opacity=1, stroke_width=0).scale(0.11)
                            .rotate(th - np.pi / 2).move_to(C + u * (F.R_T * s + 0.07))).set_z_index(8)
            enlace.put_start_and_end_on(C + u * (F.R_T * s + 0.18), C + u * (F.ALT_A["GEO"] * s - 0.2))
        estacion.add_updater(mover)

        def reloj_txt():
            h = (pel.t % T) / T * 24
            return f"{int(h):02d}:{int((h % 1) * 6) * 10:02d} h"
        self.add(Viva(est, reloj_txt, [-5.0, 4.75, 0], 44))
        self.add(texto(est, "1 día = 16 s", 28, est.tenue).move_to([-5.0, 4.05, 0]).set_z_index(10))

        d = {n: F.ALT_A[n] - F.R_T for n in F.ALT_A}
        (a0, a1), (b0, b1), (c0, c1) = F.ALT_VENTANAS
        leyenda(self, est, pel, f"LEO: una vuelta en {F.hm(F.periodo(F.ALT_A['LEO']))}",
                f"≈ {miles(round(d['LEO'], -1))} km · {F.v_circular(F.ALT_A['LEO']):.1f} km/s · 15 vueltas al día", a0, a1)
        leyenda(self, est, pel, "MEO (como GPS): 2 vueltas al día",
                f"≈ {miles(round(d['MEO'], -2))} km · {F.v_circular(F.ALT_A['MEO']):.1f} km/s", b0, b1)
        leyenda(self, est, pel, "GEO: gira junto con la Tierra",
                f"≈ {miles(round(d['GEO'], -2))} km · siempre sobre el mismo punto", c0, c1)
        leyenda(self, est, pel, "Cada altura es un trabajo distinto", "más alto ve más, pero está más lejos", c1, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 3 · Subir de órbita con dos encendidos (Hohmann) ══════════════════════════════════════════════

class ReelHohmann(Scene):
    TEMA = "orbita"
    VAR = 2

    def construct(self):
        TB = F.HOH_TB
        est, pel = preparar(self, self.TEMA, TB, "Maniobra de Hohmann", "Subir de órbita\ncon dos encendidos", self.VAR)
        chip_arriba(self, est, "A escala · tiempo acelerado")

        C = np.array([0.0, -0.3, 0.0])
        s = 5.3 / F.HOH_R2
        xy = lambda p: C + np.array([p[0] * s, p[1] * s, 0])
        self.add(tierra(est, F.R_T * s, C))
        self.add(Circle(radius=F.HOH_R1 * s, stroke_width=2.5, stroke_color=est.acento).set_stroke(opacity=0.85).move_to(C).set_z_index(4))
        self.add(DashedVMobject(Circle(radius=F.HOH_R2 * s, stroke_width=2.5, stroke_color=est.calido).move_to(C), num_dashes=90)
                 .set_stroke(opacity=0.65).set_z_index(4))
        q = np.cumsum([d for _, d in F.HOH_SEG])
        for a, b, col in ((q[0], q[1], est.acento), (q[2], q[3], est.calido)):
            pts = [xy(F.hohmann_pos(t)) for t in np.linspace(a, b - 1e-6, 160)]
            self.add(DashedVMobject(polilinea(pts, color=col, width=2.2, opacity=0.45), num_dashes=40).set_z_index(4))
        self.add(texto(est, "LEO 400 km", 32, est.acento, "cuerpo", "SEMIBOLD").move_to(C + np.array([-2.3, -1.2, 0])).set_z_index(10))
        self.add(texto(est, "GEO", 38, est.calido, "cuerpo", "SEMIBOLD").move_to(C + np.array([-4.3, 3.5, 0])).set_z_index(10))

        sat = punto(est.tinta, 0.12)
        self.add(sat)
        cola(self, sat, est.tinta, n=34, ancho=7.0)

        def mover(_m):
            sat.move_to(xy(F.hohmann_pos(pel.t)))
        sat.add_updater(mover)

        etiquetas = (f"+{F.HOH_DV1:.1f} km/s", f"+{F.HOH_DV2:.1f} km/s", f"−{F.HOH_DV2:.1f} km/s", f"−{F.HOH_DV1:.1f} km/s")
        for tq, txt in zip(F.HOH_QUEMAS, etiquetas):
            p = xy(F.hohmann_pos(tq))
            col = est.calido if not txt.startswith("−") else est.acento2
            anillo = Circle(radius=0.25, stroke_width=4, stroke_color=col).move_to(p).set_z_index(11)
            rot = texto(est, txt, 42, col, "cifra", "SEMIBOLD").next_to(p, LEFT if p[1] > 2.5 else RIGHT, buff=0.4).set_z_index(12)
            self.add(anillo, rot)

            def destello(m, tq=tq, p=p, col=col):
                u = pel.t - tq
                f = suave(u / 0.7) if 0 <= u < 0.7 else 1.0
                m.become(Circle(radius=0.15 + 0.9 * f, stroke_width=4, stroke_color=col).move_to(p))
                m.set_stroke(opacity=(1 - f) if 0 <= u < 0.7 else 0).set_z_index(11)
            anillo.add_updater(destello)
            rot.add_updater(lambda m, tq=tq: m.set_opacity(ventana(pel.t, tq - 0.1, tq + 2.2, 0.4, 1e9)))

        q0, q1, q2, q3 = F.HOH_QUEMAS
        leyenda(self, est, pel, "Un satélite en órbita baja", "a 400 km da una vuelta cada 92 minutos", 0.0, q0 - 0.2)
        leyenda(self, est, pel, "1 · Acelera abajo y sube", f"media elipse: {F.hm(F.HOH_VIAJE)} de viaje", q0 - 0.2, q1 - 0.2)
        leyenda(self, est, pel, "2 · Acelera otra vez arriba", "y queda en órbita geoestacionaria", q1 - 0.2, q2 - 0.2)
        leyenda(self, est, pel, "Para volver: frenar dos veces", "el mismo truco, al revés", q2 - 0.2, q3 - 0.2)
        leyenda(self, est, pel, "Dos encendidos bastan", f"en total, ≈ {F.HOH_DV1 + F.HOH_DV2:.1f} km/s de cambio de velocidad", q3 - 0.2, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 4 · La luz también tarda (latencia mínima LEO vs GEO) ═════════════════════════════════════════

class ReelLatencia(Scene):
    TEMA = "orbita"
    VAR = 0

    def construct(self):
        TB = F.LAT_TB
        est, pel = preparar(self, self.TEMA, TB, "Latencia", "La luz también\ntarda en llegar", self.VAR)
        chip_arriba(self, est, "Cámara lenta ×25")

        Y0, Y1, XG = -5.0, 4.4, 3.7
        s = (Y1 - Y0) / F.LAT_GEO_H
        self.add(Rectangle(width=12.8, height=0.55, stroke_width=0, fill_color=est.tierra, fill_opacity=1).move_to([0, Y0 - 0.29, 0]).set_z_index(3))
        self.add(Line([-6.4, Y0, 0], [6.4, Y0, 0], stroke_width=4, color=est.tierra_borde).set_z_index(4))
        self.add(antena(est, XG, Y0 + 0.12), punto(est.calido, 0.14).move_to([XG, Y1, 0]))
        self.add(DashedLine([XG, Y0, 0], [XG, Y1, 0], stroke_width=1.6, color=est.tenue, dash_length=0.15).set_opacity(0.5).set_z_index(4))
        self.add(texto(est, f"GEO · {miles(F.LAT_GEO_H)} km", 34, est.calido, "cuerpo", "SEMIBOLD").move_to([XG - 0.3, Y1 + 0.6, 0]).set_z_index(10))

        XL = -4.3                                                # LEO a escala: 550 km quedan pegados al suelo → lupa
        y_leo = Y0 + F.LAT_LEO_H * s
        self.add(antena(est, XL, Y0 + 0.12), Dot([XL, y_leo, 0], radius=0.05, color=est.acento).set_z_index(9))
        L = np.array([-3.2, 0.9, 0.0])
        self.add(Circle(radius=2.5, stroke_width=3, stroke_color=est.acento, fill_color=est.fondo, fill_opacity=0.95).move_to(L).set_z_index(5))
        self.add(Line([XL, y_leo + 0.12, 0], L + np.array([-0.6, -2.42, 0]), stroke_width=2.4, color=est.acento).set_opacity(0.6).set_z_index(5))
        self.add(Circle(radius=0.3, stroke_width=2, stroke_color=est.acento).move_to([XL, Y0 + 0.05, 0]).set_stroke(opacity=0.6).set_z_index(5))
        ls, ll = L + DOWN * 1.4, L + UP * 1.3
        self.add(Line(ls + LEFT * 1.8, ls + RIGHT * 1.8, stroke_width=3, color=est.tierra_borde).set_z_index(6))
        self.add(antena(est, ls[0], ls[1] + 0.1, 0.14).set_z_index(7), punto(est.acento, 0.13).move_to(ll))
        self.add(texto(est, f"LEO · {miles(F.LAT_LEO_H)} km", 32, est.acento, "cuerpo", "SEMIBOLD").move_to(L + UP * 3.0).set_z_index(10))
        pulso_l, pulso_g = punto(est.tinta, 0.11), punto(est.tinta, 0.15)
        estela_g = Line([XG, Y0, 0], [XG, Y0 + 0.01, 0]).set_z_index(7)
        self.add(pulso_l, pulso_g, estela_g)

        def mover(_m):
            ms = F.lat_ms(pel.t)
            vivo = 0 < ms < F.LAT_GEO_MS
            h = 1 - abs(2 * ((ms / F.LAT_LEO_MS) % 1.0) - 1)       # LEO: ida y vuelta cada 3.67 ms
            pulso_l.move_to(ls + (ll - ls) * (0.1 + 0.8 * h))
            pulso_l[1].set_opacity(1 if vivo else 0); pulso_l[0].set_opacity(0.16 if vivo else 0)
            u = ms / F.LAT_GEO_MS
            yg = Y0 + (Y1 - Y0) * (1 - abs(2 * u - 1))
            pulso_g.move_to([XG, yg, 0])
            pulso_g[1].set_opacity(1 if vivo else 0); pulso_g[0].set_opacity(0.16 if vivo else 0)
            tope = Y1 if u >= 0.5 else yg                          # el camino recorrido (sube y baja por la misma línea)
            estela_g.put_start_and_end_on([XG, Y0, 0], [XG, max(tope, Y0 + 0.001), 0])
            estela_g.set_stroke(color=est.tinta, width=3, opacity=0.5 if ms > 0 else 0)
        pulso_g.add_updater(mover)
        cola(self, pulso_g, est.tinta, n=14, ancho=7.0)

        self.add(Viva(est, lambda: f"{F.lat_ms(pel.t):.0f} ms", [XG - 2.0, 0.1, 0], 78))
        self.add(Viva(est, lambda: f"{int(F.lat_ms(pel.t) // F.LAT_LEO_MS)} viajes", [-1.0, -2.45, 0], 56, est.acento))
        self.add(texto(est, f"cada uno: {F.LAT_LEO_MS:.1f} ms", 30, est.tenue).move_to([-1.0, -3.15, 0]).set_z_index(10))

        t_llega = F.LAT_IDA + 6.0
        leyenda(self, est, pel, "Subir y bajar, a la velocidad de la luz", "de la antena al satélite y de vuelta", 0.0, t_llega + 0.4)
        leyenda(self, est, pel, f"GEO: {F.LAT_GEO_MS:.0f} ms como mínimo", f"en ese tiempo, en LEO cabe {F.LAT_VIAJES} veces", t_llega + 0.4, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 5 · Más cerca, más rápido (2.ª ley de Kepler, órbita tipo Molniya) ════════════════════════════

class ReelAreasIguales(Scene):
    TEMA = "orbita"
    VAR = 1

    def construct(self):
        T, TB = F.MOL_T, F.MOL_TB
        est, pel = preparar(self, self.TEMA, TB, "Segunda ley de Kepler", "Más cerca,\nmás rápido", self.VAR)
        chip_arriba(self, est, "A escala · 1 s ≈ 45 min")

        ytop, ybot = 4.9, -5.4
        s = (ytop - ybot) / (F.MOL_RP + F.MOL_RA)
        foco = np.array([0.0, ybot + F.MOL_RP * s, 0.0])
        xy = lambda p: foco + np.array([p[0] * s, p[1] * s, 0])
        self.add(polilinea([xy(p) for p in F.mol_pos(np.linspace(0, T, 400))], color=est.tenue, width=2.2, opacity=0.5).set_z_index(4),
                 tierra(est, F.R_T * s, foco))
        franjas = []
        for k in range(F.MOL_N):
            a = k * T / F.MOL_N
            f = VMobject().set_z_index(2)
            self.add(f)
            franjas.append((a, [xy(p) for p in F.mol_pos(np.linspace(a, a + T / F.MOL_N, 40))], est.acento if k % 2 == 0 else est.calido, f))
        sat, radio = punto(est.tinta, 0.12), Line(foco, foco + UP).set_z_index(5)
        self.add(radio, sat)
        cola(self, sat, est.tinta, n=24, ancho=6.0)
        paso = T / F.MOL_N

        def mover(_m):
            t = pel.t
            p = xy(F.mol_pos(t))
            sat.move_to(p)
            radio.put_start_and_end_on(foco, p).set_stroke(color=est.tinta, width=2, opacity=0.6)
            for a, arco, col, f in franjas:
                u = t - a                                              # edad de la franja
                if u <= 0:
                    f.clear_points()
                    continue
                if u < paso:
                    pts = [foco] + arco[:max(2, int(u / paso * 39) + 1)] + [p]
                else:
                    pts = [foco] + arco
                f.set_points_as_corners(pts + [foco]).set_fill(color=col, opacity=0.32).set_stroke(color=col, width=1.2, opacity=0.5)
        sat.add_updater(mover)

        def rapidez():
            return f"{F.v_visviva(np.linalg.norm(F.mol_pos(pel.t)), F.MOL_A):.1f} km/s"
        self.add(Viva(est, rapidez, lambda: sat.get_center() + (RIGHT if sat.get_center()[0] >= foco[0] else LEFT) * 1.75 + UP * 0.05, 44))
        self.add(texto(est, "perigeo", 30, est.tenue).move_to(foco + np.array([-2.4, -F.MOL_RP * s - 0.05, 0])).set_z_index(10))
        self.add(texto(est, "apogeo", 30, est.tenue).move_to([-2.0, ytop + 0.1, 0]).set_z_index(10))
        GX, GY0, GY1 = 5.9, ybot + 0.3, ytop - 0.2                                 # velocímetro: más alto = más rápido
        self.add(Line([GX, GY0, 0], [GX, GY1, 0], stroke_width=8, color=est.linea).set_z_index(6))
        marca_v = Dot(radius=0.2, color=est.calido).set_z_index(9)
        marca_v.add_updater(lambda m: m.move_to([GX, GY0 + (GY1 - GY0) * (F.v_visviva(np.linalg.norm(F.mol_pos(pel.t)), F.MOL_A) - F.MOL_VA)
                                                 / (F.MOL_VP - F.MOL_VA), 0]))
        self.add(marca_v, texto(est, "rápido", 26, est.calido).move_to([GX - 0.05, GY1 + 0.35, 0]).set_z_index(10),
                 texto(est, "lento", 26, est.tenue).move_to([GX - 0.05, GY0 - 0.35, 0]).set_z_index(10))

        leyenda(self, est, pel, "Cerca de la Tierra: rapidísimo", f"en el perigeo, {F.MOL_VP:.1f} km/s", 0.0, 4.2)
        leyenda(self, est, pel, "Cada franja dura 1 hora", "y todas tienen la misma área", 4.2, 8.0)
        leyenda(self, est, pel, "Lejos: lento", f"en el apogeo, {F.MOL_VA:.1f} km/s", 8.0, 12.2)
        leyenda(self, est, pel, "Kepler lo escribió en 1609", f"órbita tipo Molniya: {F.hm(F.MOL_T_REAL)} por vuelta", 12.2, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 6 · Ventana de contacto (¿cuánto tiempo ves pasar un satélite?) ═══════════════════════════════

class ReelVentanaContacto(Scene):
    TEMA = "orbita"
    VAR = 2

    def construct(self):
        T, TB = F.VEN_T, F.VEN_TB
        est, pel = preparar(self, self.TEMA, TB, "Ventana de contacto", "¿Cuánto tiempo\nlo ves pasar?", self.VAR)
        chip_arriba(self, est, "A escala · sin girar la Tierra", est.acento2)

        R, C = 4.3, np.array([0.0, 0.2, 0.0])
        ro = R * (F.R_T + F.VEN_H) / F.R_T
        pos = lambda a, r: C + r * np.array([np.sin(a), np.cos(a), 0])
        self.add(tierra(est, R, C))
        self.add(Circle(radius=ro, stroke_width=2.2, stroke_color=est.tenue).set_stroke(opacity=0.45).move_to(C).set_z_index(4))
        lam = F.VEN_LAMBDA
        self.add(Arc(radius=ro, start_angle=np.pi / 2 - lam, angle=2 * lam, stroke_width=7, stroke_color=est.acento).move_arc_center_to(C).set_z_index(5))
        e = pos(0, R)
        self.add(VGroup(*[DashedLine(e, pos(sg * lam, ro) + (pos(sg * lam, ro) - e) * 0.25, stroke_width=2, color=est.tenue,
                                     dash_length=0.14).set_opacity(0.75) for sg in (-1, 1)]).set_z_index(5))
        self.add(antena(est, e[0], e[1] + 0.12, 0.17).set_z_index(8))
        self.add(texto(est, f"{F.VEN_MASCARA:.0f}°", 30, est.tenue, "cifra").move_to(e + np.array([1.9, 0.06, 0])).set_z_index(10))
        sat, haz = punto(est.tinta, 0.13), Line(e, e + UP * 0.01).set_z_index(6)
        contacto = chip(est, "EN CONTACTO", est.acento, 32).move_to(C + UP * 1.6)
        self.add(haz, sat, contacto)
        cola(self, sat, est.tinta, n=28, ancho=6.0)

        X0, X1, YB = -6.0, 6.0, -5.3                             # una vuelta completa con la ventana marcada
        self.add(Line([X0, YB, 0], [X1, YB, 0], stroke_width=8, color=est.linea).set_z_index(8))
        xa, xb = X0 + (X1 - X0) * F.VEN_AOS / T, X0 + (X1 - X0) * F.VEN_LOS / T
        self.add(Line([xa, YB, 0], [xb, YB, 0], stroke_width=8, color=est.acento).set_z_index(9))
        self.add(texto(est, "0", 26, est.tenue).move_to([X0, YB - 0.42, 0]).set_z_index(10))
        self.add(texto(est, F.hm(F.VEN_P), 26, est.tenue).move_to([X1 - 0.5, YB - 0.42, 0]).set_z_index(10))
        cursor = Triangle(fill_color=est.tinta, fill_opacity=1, stroke_width=0).scale(0.12).rotate(np.pi).set_z_index(10)
        self.add(cursor)

        def mover(_m):
            t = pel.t
            p = pos(F.ven_angulo(t), ro)
            sat.move_to(p)
            v = ventana(t, F.VEN_AOS, F.VEN_LOS, 0.12, 1e9)
            haz.put_start_and_end_on(e + UP * 0.2, p).set_stroke(color=est.acento, width=3, opacity=0.85 * v)
            contacto.set_opacity(v)
            sat[1].set_color(est.acento if v > 0.5 else est.tinta)
            cursor.move_to([X0 + (X1 - X0) * (min(t, T) / T), YB + 0.3, 0])
        sat.add_updater(mover)

        leyenda(self, est, pel, "A 550 km, una vuelta tarda", F.hm(F.VEN_P), 0.0, 7.0, y=-7.4)
        leyenda(self, est, pel, f"Desde tu antena lo ves ≈ {F.VEN_VISIBLE / 60:.0f} min", "en el mejor pase, justo sobre ti", 7.0, 13.5, y=-7.4)
        leyenda(self, est, pel, "Por eso hacen falta muchos satélites", "para estar siempre conectado", 13.5, TB + FIN, y=-7.4)
        cerrar(self, est, pel, self.VAR)


# ══ 7 · Velocidad de escape (círculo → elipse → parábola → hipérbola) ═════════════════════════════

class ReelVelocidadEscape(Scene):
    TEMA = "orbita"
    VAR = 0

    def construct(self):
        TB = F.ESC_TB
        est, pel = preparar(self, self.TEMA, TB, "Velocidad de escape", "¿Qué tan rápido\npara no volver?", self.VAR)
        chip_arriba(self, est, "Tierra a escala · tiempo acelerado")

        C, r0 = np.array([-0.6, -3.9, 0.0]), 1.8
        self.add(tierra(est, r0 * F.R_T / F.ESC_R0, C))
        pos = lambda th, rho: C + r0 * rho * np.array([np.sin(th), -np.cos(th), 0])
        colores = (est.acento, est.tinta, est.calido, est.acento2)
        tiros = []
        for (k, t0), col in zip(F.ESC_PLAN, colores):
            u, th, r = F.escape_tiro(k)
            pts = np.array([pos(a, b) for a, b in zip(th, r)])
            traza, bala = VMobject().set_z_index(7), punto(col, 0.13)
            self.add(traza, bala)
            cola(self, bala, col, n=22, ancho=7.0)
            tiros.append((t0, u, pts, col, traza, bala))
        self.add(Dot(pos(0, 1), radius=0.07, color=est.tinta).set_z_index(8))

        def mover(_m):
            t = pel.t
            for t0, u, pts, col, traza, bala in tiros:
                x = (t - t0) / F.ESC_D
                if x <= 0:
                    traza.clear_points(); bala.set_opacity(0)
                    continue
                i = max(1, min(int(np.searchsorted(u, min(x, 1.0))), len(pts) - 1))
                traza.set_points_as_corners(pts[: i + 1])
                vuela = x < 1
                traza.set_stroke(color=col, width=4 if vuela else 3, opacity=0.95 if vuela else 0.5).set_fill(opacity=0)
                bala.move_to(pts[i])
                bala[1].set_opacity(1 if vuela else 0); bala[0].set_opacity(0.16 if vuela else 0)
        self.add(VMobject().add_updater(mover))

        def rapidez():
            k = F.ESC_K[0]
            for kk, t0 in F.ESC_PLAN:
                if pel.t >= t0 - 0.2:
                    k = kk
            return f"{k * F.ESC_VC:.1f} km/s"
        self.add(Viva(est, rapidez, pos(0, 1) + LEFT * 2.3 + UP * 0.15, 54, est.acento))

        t2, t3 = F.ESC_PLAN[2][1], F.ESC_PLAN[3][1]
        leyenda(self, est, pel, "Más rápido: la órbita se estira", f"a 400 km, la circular va a {F.ESC_VC:.1f} km/s", 0.0, t2 - 0.2)
        leyenda(self, est, pel, f"A {F.ESC_VE:.1f} km/s ya no vuelve", "√2 veces la velocidad orbital: escape", t2 - 0.2, t3 - 0.2)
        leyenda(self, est, pel, "Círculo, elipse, parábola, hipérbola", "la misma gravedad, distinta velocidad", t3 - 0.2, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 8 · ¿Cuánto de la Tierra ve un satélite? ═════════════════════════════════════════════════════

class ReelCobertura(Scene):
    TEMA = "orbita"
    VAR = 1

    def construct(self):
        TB = F.COB_TB
        est, pel = preparar(self, self.TEMA, TB, "Cobertura", "¿Cuánto de la Tierra\nve un satélite?", self.VAR)
        chip_arriba(self, est, "A escala · hasta el horizonte", est.acento)

        C, Rs = np.array([0.0, -4.2, 0.0]), 1.3
        self.add(tierra(est, Rs, C))
        cono, casquete, sat = VMobject().set_z_index(2), VMobject().set_z_index(5), punto(est.acento2, 0.13)
        rectas = VGroup(Line(ORIGIN, RIGHT), Line(ORIGIN, RIGHT)).set_z_index(4)
        self.add(cono, rectas, casquete, sat)
        cola(self, sat, est.acento2, n=18, ancho=6.0)

        def geom():
            h = F.cob_altura(pel.t)
            return h, C + UP * Rs * (F.R_T + h) / F.R_T, F.cob_semiangulo(h)

        def mover(_m):
            h, p, lam = geom()
            sat.move_to(p)
            tp = [C + Rs * np.array([sg * np.sin(lam), np.cos(lam), 0]) for sg in (-1, 1)]
            arco = [C + Rs * np.array([np.sin(a), np.cos(a), 0]) for a in np.linspace(-lam, lam, 50)]
            cono.set_points_as_corners([p, *arco, p]).set_fill(color=est.acento, opacity=0.13).set_stroke(width=0)
            for l, q in zip(rectas, tp):
                l.put_start_and_end_on(p, q).set_stroke(color=est.acento, width=2.2, opacity=0.8)
            casquete.set_points_as_corners(arco).set_stroke(color=est.acento, width=8).set_fill(opacity=0)
        sat.add_updater(mover)

        self.add(Viva(est, lambda: f"{100 * F.cob_fraccion(F.cob_altura(pel.t)):.0f} %", [-3.7, 0.9, 0], 150, est.acento))
        self.add(texto(est, "de la Tierra a la vista", 32, est.tenue).move_to([-3.7, -0.6, 0]).set_z_index(10))
        self.add(Viva(est, lambda: f"{miles(round(F.cob_altura(pel.t), -1))} km", lambda: geom()[1] + RIGHT * 2.1, 40, est.tinta, rol="cuerpo"))

        g, l = F.cob_fraccion(F.COB_H[1]) * 100, F.cob_fraccion(F.COB_H[0]) * 100
        a0, a1 = F.COB_SUBE
        leyenda(self, est, pel, "En órbita baja ves poco", f"a 550 km: el {l:.0f} % de la Tierra", 0.0, a0 + 0.2)
        leyenda(self, est, pel, "Más alto, más ves", "pero más lejos y con más retraso", a0 + 0.2, a1 + 0.2)
        leyenda(self, est, pel, "Desde GEO: casi la mitad", f"{g:.0f} % · el límite sería 50 %", a1 + 0.2, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 9 · 16 amaneceres al día (ISS) ═══════════════════════════════════════════════════════════════

class ReelAmaneceres(Scene):
    TEMA = "orbita"
    VAR = 2

    def construct(self):
        T, TB = F.AMA_T, F.AMA_TB
        est, pel = preparar(self, self.TEMA, TB, "Día y noche en órbita", "¿Cuántas veces\namanece en la ISS?", self.VAR)
        chip_arriba(self, est, "A escala · sombra simplificada")

        R, C = 4.4, np.array([0.0, -0.3, 0.0])
        ro = R * F.AMA_A / F.R_T
        self.add(Rectangle(width=9.0, height=2 * R, stroke_width=0, fill_color=BLACK, fill_opacity=0.35).move_to(C + RIGHT * 4.5).set_z_index(1))
        self.add(VGroup(*[DashedLine(C + np.array([0, sg * R, 0]), C + np.array([7.2, sg * R, 0]), stroke_width=1.6, color=est.tenue,
                                     dash_length=0.15).set_opacity(0.5) for sg in (-1, 1)]).set_z_index(1))
        self.add(VGroup(*[Line([-7.1, C[1] + y, 0], [(-np.sqrt(R ** 2 - y ** 2) - 0.15) if abs(y) < R else 7.1, C[1] + y, 0], stroke_width=1.6,
                               color=est.acento2).set_opacity(0.35) for y in np.linspace(-5.4, 5.4, 11)]).set_z_index(1))
        self.add(texto(est, "luz del Sol →", 30, est.acento2).move_to([-4.6, 5.25, 0]).set_z_index(10))
        self.add(tierra(est, R, C))
        self.add(AnnularSector(inner_radius=0, outer_radius=R, angle=PI, start_angle=PI / 2, fill_color="#8CC8F5", fill_opacity=0.30,
                               stroke_width=0).move_arc_center_to(C).set_z_index(4))
        self.add(Circle(radius=ro, stroke_width=2, stroke_color=est.tenue).set_stroke(opacity=0.5).move_to(C).set_z_index(4))
        th_s = np.arcsin(F.R_T / F.AMA_A)
        q = C + ro * np.array([np.cos(th_s), np.sin(th_s), 0])
        sat, destello = punto(est.calido, 0.17), Circle(radius=0.25, stroke_width=4, stroke_color=est.calido).set_z_index(11)
        self.add(sat, destello)
        cola(self, sat, est.calido, n=26, ancho=7.0)

        def mover(_m):
            t = pel.t
            a = th_s + 2 * np.pi * (t % T) / T                   # antihorario; la vuelta empieza al salir de la sombra
            sat.move_to(C + ro * np.array([np.cos(a), np.sin(a), 0]))
            en_sombra = np.cos(a) > 0 and abs(np.sin(a)) * ro < R
            sat[1].set_color(est.tenue if en_sombra else est.calido)
            sat[0].set_opacity(0.0 if en_sombra else 0.22)
            u = t % T
            f = suave(u / 0.8) if (u < 0.8 and t > 0.05) else 1.0
            destello.become(Circle(radius=0.15 + 1.3 * f, stroke_width=4, stroke_color=est.calido).move_to(q))
            destello.set_stroke(opacity=(1 - f) if f < 1 else 0).set_z_index(11)
        sat.add_updater(mover)
        self.add(texto(est, "amanecer", 34, est.calido, "cuerpo", "SEMIBOLD").move_to(q + np.array([0.5, 0.7, 0])).set_z_index(10))
        self.add(texto(est, "noche", 34, est.tenue).move_to(C + np.array([ro - 0.2, -R - 0.5, 0])).set_z_index(10))

        noche = F.AMA_P * F.AMA_SOMBRA
        leyenda(self, est, pel, f"En la ISS amanece cada {F.hm(F.AMA_P)}", f"≈ {F.AMA_POR_DIA:.1f} amaneceres al día", 0.0, 5.8)
        leyenda(self, est, pel, f"{F.hm(noche)} de noche, {F.hm(F.AMA_P - noche)} de día", "la sombra de la Tierra tapa parte de la vuelta", 5.8, 11.8)
        leyenda(self, est, pel, "Cada vuelta: un amanecer y un atardecer", "unos 16 de cada uno, todos los días", 11.8, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 10 · Un cohete es casi todo combustible (Tsiolkovsky) ═════════════════════════════════════════

class ReelCohete(Scene):
    TEMA = "orbita"
    VAR = 0

    def construct(self):
        TB = F.COH_TB
        est, pel = preparar(self, self.TEMA, TB, "Ecuación del cohete", "¿Por qué un cohete\nes casi todo combustible?", self.VAR)
        chip_arriba(self, est, "Una etapa ideal · ilustración")

        X, Y0, H, Wc = -3.3, -5.0, 8.8, 2.5
        cuerpo = Rectangle(width=Wc, height=H, stroke_width=3, stroke_color=est.tinta).move_to([X, Y0 + H / 2, 0]).set_z_index(6)
        nariz = Polygon([X - Wc / 2, Y0 + H, 0], [X, Y0 + H + 1.3, 0], [X + Wc / 2, Y0 + H, 0], stroke_width=3, stroke_color=est.tinta,
                        fill_color=est.tinta, fill_opacity=0.2).set_z_index(6)
        aletas = VGroup(*[Polygon([X + sg * Wc / 2, Y0 + 1.6, 0], [X + sg * (Wc / 2 + 0.9), Y0 - 0.2, 0], [X + sg * Wc / 2, Y0, 0],
                                  stroke_width=3, stroke_color=est.tinta, fill_color=est.tinta, fill_opacity=0.2) for sg in (-1, 1)]).set_z_index(6)
        h_seca = H * (1 - F.COH_FRAC)
        seca = Rectangle(width=Wc - 0.12, height=h_seca, stroke_width=0, fill_color=est.calido, fill_opacity=0.9)
        seca.move_to([X, Y0 + H - h_seca / 2 - 0.06, 0]).set_z_index(5)
        tanque, llama = VMobject().set_z_index(5), VMobject().set_z_index(4)
        self.add(tanque, llama, cuerpo, nariz, aletas, seca)
        self.add(texto(est, f"todo lo demás: {100 * (1 - F.COH_FRAC):.0f} %", 32, est.calido, "cuerpo", "SEMIBOLD")
                 .next_to(seca, RIGHT, buff=0.5).set_z_index(10))
        self.add(texto(est, f"combustible: {100 * F.COH_FRAC:.0f} %", 34, est.acento, "cuerpo", "SEMIBOLD")
                 .move_to([X + Wc / 2 + 1.25, Y0 + 1.1, 0], aligned_edge=LEFT).set_z_index(10))

        def mover(_m):
            t = pel.t
            queda, _ = F.coh_estado(t)
            h = max(0.001, (H - h_seca - 0.12) * queda)
            tanque.become(Rectangle(width=Wc - 0.12, height=h, stroke_width=0, fill_color=est.acento, fill_opacity=0.75)
                          .move_to([X, Y0 + 0.06 + h / 2, 0])).set_z_index(5)
            quema = F.COH_LLENA <= t < F.COH_QUEMA
            largo = (1.5 + 0.3 * np.sin(2 * np.pi * 9 * t)) if quema else 0.0
            if largo:
                llama.set_points_as_corners([[X - 0.8, Y0, 0], [X, Y0 - largo, 0], [X + 0.8, Y0, 0], [X - 0.8, Y0, 0]])
                llama.set_fill(color=est.calido, opacity=0.85).set_stroke(width=0)
            else:
                llama.clear_points()
        tanque.add_updater(mover)

        BX0, BX1, BY = 0.6, 6.3, -1.0
        self.add(Line([BX0, BY, 0], [BX1, BY, 0], stroke_width=10, color=est.linea).set_z_index(6))
        barra = Line([BX0, BY, 0], [BX0 + 0.01, BY, 0]).set_z_index(7)
        self.add(barra)
        barra.add_updater(lambda m: m.put_start_and_end_on([BX0, BY, 0], [BX0 + 0.001 + (BX1 - BX0) * F.coh_estado(pel.t)[1] / F.COH_DV, BY, 0])
                          .set_stroke(color=est.acento, width=10))
        self.add(Viva(est, lambda: f"{F.coh_estado(pel.t)[1]:.1f} km/s", [(BX0 + BX1) / 2 - 0.1, BY + 1.5, 0], 88))
        self.add(texto(est, "velocidad ganada (Δv)", 32, est.tenue).move_to([(BX0 + BX1) / 2, BY - 0.7, 0]).set_z_index(10))

        leyenda(self, est, pel, f"Llegar a órbita pide ≈ {F.COH_DV:.1f} km/s", "todo ese impulso sale de quemar masa", 0.0, 6.2)
        leyenda(self, est, pel, "Cada km/s cuesta más que el anterior", "la masa crece exponencial (Tsiolkovsky, 1903)", 6.2, F.COH_QUEMA + 1.0)
        leyenda(self, est, pel, "Un cohete es casi todo combustible", f"≈ {100 * F.COH_FRAC:.0f} % de su masa al despegar", F.COH_QUEMA + 1.0, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 11 · ¿No hay gravedad en la ISS? ═════════════════════════════════════════════════════════════

class ReelGravedadISS(Scene):
    TEMA = "orbita"
    VAR = 1

    def construct(self):
        T, TB = F.GRA_T, F.GRA_TB
        est, pel = preparar(self, self.TEMA, TB, "Mito orbital", "¿En el espacio\nno hay gravedad?", self.VAR)
        chip_arriba(self, est, "A escala")

        R, C = 3.9, np.array([0.0, 0.5, 0.0])
        ro = R * (F.R_T + 420) / F.R_T
        self.add(tierra(est, R, C), Circle(radius=ro, stroke_width=2, stroke_color=est.tenue).set_stroke(opacity=0.5).move_to(C).set_z_index(4))
        iss = punto(est.tinta, 0.12)
        g_vec, v_vec = VMobject().set_z_index(8), VMobject().set_z_index(8)
        self.add(g_vec, v_vec, iss)
        cola(self, iss, est.tinta, n=28, ancho=6.0)

        def mover(_m):
            a = np.pi / 2 + 2 * np.pi * (pel.t % T) / T
            u = np.array([np.cos(a), np.sin(a), 0])
            p = C + ro * u
            iss.move_to(p)
            g_vec.become(Arrow(p, p - u * 1.7, buff=0, stroke_width=8, max_tip_length_to_length_ratio=0.3, color=est.acento2)).set_z_index(8)
            v_vec.become(Arrow(p, p + np.array([-u[1], u[0], 0]) * 2.0, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.25,
                               color=est.tenue)).set_z_index(8)
        iss.add_updater(mover)
        self.add(texto(est, "gravedad", 28, est.acento2, "cuerpo", "SEMIBOLD").move_to([-4.9, 4.9, 0]).set_z_index(10),
                 texto(est, "velocidad", 28, est.tenue, "cuerpo", "SEMIBOLD").move_to([-4.9, 4.25, 0]).set_z_index(10))

        X0, X1 = -5.6, 5.4
        for y, val, lab, col in ((-4.55, F.GRA_G0, "En el suelo", est.tinta), (-5.5, F.GRA_GISS, "En la ISS (420 km)", est.acento2)):
            ancho = (X1 - X0) * val / F.GRA_G0 * 0.8
            barra = Rectangle(width=ancho, height=0.62, stroke_width=0, fill_color=col, fill_opacity=0.9).set_z_index(6)
            barra.move_to([X0 + ancho / 2, y, 0])

            def crecer(m, ancho=ancho, y=y, col=col):               # las barras se llenan al empezar
                g = max(suave((pel.t - 0.8) / 1.6), 0.001)
                m.become(Rectangle(width=ancho * g, height=0.62, stroke_width=0, fill_color=col, fill_opacity=0.9)
                         .move_to([X0 + ancho * g / 2, y, 0])).set_z_index(6)
            barra.add_updater(crecer)
            self.add(barra)
            self.add(texto(est, lab, 28, est.fondo, "cuerpo", "SEMIBOLD").move_to([X0 + 0.2, y, 0], aligned_edge=LEFT).set_z_index(7))
            val_txt = texto(est, f"{val:.1f} m/s²", 34, col, "cifra", "SEMIBOLD").next_to([X0 + ancho, y, 0], RIGHT, buff=0.25).set_z_index(7)
            val_txt.add_updater(lambda m: m.set_opacity(suave((pel.t - 2.0) / 0.6)))
            self.add(val_txt)

        leyenda(self, est, pel, "A 420 km sí hay gravedad", f"el {100 * F.GRA_FRAC:.0f} % de la que sientes en el suelo", 0.0, 7.2)
        leyenda(self, est, pel, "Flotan porque están cayendo", "la estación y ellos caen juntos, sin parar", 7.2, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 12 · ¿Cuánto tarda un mensaje a Marte? ═══════════════════════════════════════════════════════

class ReelMensajeMarte(Scene):
    TEMA = "orbita"
    VAR = 2

    def construct(self):
        T, TB = F.MAR_T, F.MAR_TB
        est, pel = preparar(self, self.TEMA, TB, "Comunicaciones", "¿Cuánto tarda\nun mensaje a Marte?", self.VAR)
        chip_arriba(self, est, "Órbitas circulares · ilustración")

        C, r1 = np.array([0.0, -0.3, 0.0]), 3.2
        r2 = r1 * F.MAR_A
        self.add(Circle(radius=r1, stroke_width=2, stroke_color=est.acento2).set_stroke(opacity=0.5).move_to(C).set_z_index(3),
                 Circle(radius=r2, stroke_width=2, stroke_color=est.acento).set_stroke(opacity=0.5).move_to(C).set_z_index(3),
                 punto(est.calido, 0.4).move_to(C))
        tierra_p = C + UP * r1
        self.add(punto(est.acento2, 0.2).move_to(tierra_p), texto(est, "Tierra", 34, est.acento2, "cuerpo", "SEMIBOLD")
                 .move_to(tierra_p + LEFT * 1.3).set_z_index(10))
        marte, haz, pulso = punto(est.acento, 0.2), Line(ORIGIN, RIGHT).set_z_index(5), punto(est.tinta, 0.1)
        etq = texto(est, "Marte", 34, est.acento, "cuerpo", "SEMIBOLD").set_z_index(10)
        self.add(haz, marte, pulso, etq)
        cola(self, marte, est.acento, n=24, ancho=6.0, salto=4.0)

        def pos_m(t):
            a = np.pi / 2 - 2 * np.pi * t / T
            return C + r2 * np.array([np.cos(a), np.sin(a), 0])

        def mover(_m):
            t = pel.t
            p = pos_m(t)
            marte.move_to(p)
            etq.move_to(p + (p - C) / np.linalg.norm(p - C) * 0.75)
            d = p - tierra_p
            w = (C - tierra_p) @ d / (d @ d)                       # ¿el Sol queda entre los dos?
            tapado = 0 < w < 1 and np.linalg.norm(tierra_p + w * d - C) < 0.45
            haz.put_start_and_end_on(tierra_p, p).set_stroke(color=est.tinta, width=2, opacity=0.2 if tapado else 0.6)
            pulso.move_to(tierra_p + d * ((t * F.MAR_PULSOS / T) % 1.0)).set_opacity(0 if tapado else 1)
        marte.add_updater(mover)
        self.add(Viva(est, lambda: f"{F.mar_minutos(pel.t):.1f} min", [-4.0, 5.15, 0], 70))
        self.add(texto(est, "luz Tierra → Marte", 30, est.tenue).move_to([-4.0, 4.5, 0]).set_z_index(10))
        self.add(texto(est, "1 ciclo ≈ 2 años y 2 meses", 28, est.tenue).move_to([3.9, 4.95, 0]).set_z_index(10))

        leyenda(self, est, pel, f"Lo más cerca: {F.MAR_MIN:.1f} min", "cada mensaje, solo de ida", 0.0, 5.6)
        leyenda(self, est, pel, f"Lo más lejos: {F.MAR_MAX:.0f} min", "y a veces el Sol queda en medio", 5.6, 11.6)
        leyenda(self, est, pel, "Un rover no se maneja con joystick", "recibe un plan y lo ejecuta solo", 11.6, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 13 · Tres satélites para todo el planeta (Clarke, 1945) ═══════════════════════════════════════

class ReelClarke(Scene):
    TEMA = "orbita"
    VAR = 0

    def construct(self):
        T, TB = F.CLA_T, F.CLA_TB
        est, pel = preparar(self, self.TEMA, TB, "Idea de 1945", "Tres satélites\npara todo el planeta", self.VAR)
        chip_arriba(self, est, "A escala · vista desde el polo", est.acento)

        C, rg = np.array([0.0, -0.2, 0.0]), 5.3
        Rs = rg * F.R_T / F.CLA_R
        self.add(tierra(est, Rs, C), DashedVMobject(Circle(radius=rg, stroke_width=2, stroke_color=est.tenue).move_to(C), num_dashes=80)
                 .set_stroke(opacity=0.55).set_z_index(3))
        cols = (est.acento, est.acento2, est.calido)
        conos = [VMobject().set_z_index(2) for _ in range(3)]
        arcos = [VMobject().set_z_index(5) for _ in range(3)]
        sats = [punto(c, 0.17) for c in cols]
        estacion = Dot(radius=0.1, color=est.tinta).set_z_index(9)                  # una estación en tierra: el satélite no se le mueve
        enlace = DashedLine(ORIGIN, RIGHT, stroke_width=2, color=est.tinta, dash_length=0.12).set_z_index(5)
        self.add(*conos, *arcos, *sats, estacion, enlace)
        for sa, c in zip(sats, cols):
            cola(self, sa, c, n=14, ancho=5.0, salto=6.0)
        lam = F.CLA_SEMI

        def mover(_m):
            base = np.pi / 2 + 2 * np.pi * pel.t / T                               # un día = 12 s: todo gira junto (geoestacionarios)
            for k in range(3):
                o = suave((pel.t - F.CLA_APARECE[k]) / 0.9)
                a = base + 2 * np.pi * k / 3
                p = C + rg * np.array([np.cos(a), np.sin(a), 0])
                sats[k].move_to(p)
                sats[k][0].set_opacity(0.16 * o); sats[k][1].set_opacity(o)
                arco = [C + Rs * np.array([np.cos(a + d), np.sin(a + d), 0]) for d in np.linspace(-lam, lam, 40)]
                conos[k].set_points_as_corners([p, *arco, p]).set_fill(color=cols[k], opacity=0.12 * o).set_stroke(color=cols[k], width=1.5, opacity=0.55 * o)
                arcos[k].set_points_as_corners([C + (Rs + 0.09 + 0.07 * k) * np.array([np.cos(a + d), np.sin(a + d), 0])
                                                for d in np.linspace(-lam, lam, 40)]).set_stroke(color=cols[k], width=5, opacity=o).set_fill(opacity=0)
            q = C + Rs * np.array([np.cos(base), np.sin(base), 0])
            estacion.move_to(q)
            enlace.put_start_and_end_on(q, C + rg * np.array([np.cos(base), np.sin(base), 0]) * 0.97).set_stroke(opacity=0.5)
        sats[0].add_updater(mover)

        leyenda(self, est, pel, "Un satélite geoestacionario ve el 42 %", "casi la mitad, pero nunca los polos", 0.0, 5.4)
        leyenda(self, est, pel, "Tres, a 120°, ven casi todo el planeta", f"menos los polos: más allá de {F.CLA_LAT:.0f}° de latitud", 5.4, 11.8)
        leyenda(self, est, pel, "Arthur C. Clarke lo propuso en 1945", "12 años antes del primer satélite", 11.8, TB + FIN)
        cerrar(self, est, pel, self.VAR)


# ══ 14 · Láser a la Luna, en tiempo real ═════════════════════════════════════════════════════════

class ReelLaserLuna(Scene):
    TEMA = "orbita"
    VAR = 1

    def construct(self):
        TB = F.LUN_TB
        est, pel = preparar(self, self.TEMA, TB, "Tiempo real", "¿Cuánto tarda la luz\nen llegar a la Luna?", self.VAR)
        chip_arriba(self, est, "Distancia a escala · tamaños ×6")

        X, Y0, Y1 = -1.2, -4.0, 4.6
        s = (Y1 - Y0) / F.LUN_D
        self.add(tierra(est, 6 * F.R_T * s, [X, Y0, 0]))
        self.add(Circle(radius=6 * 1737.4 * s, stroke_width=1.5, stroke_color=est.tinta, fill_color=est.tenue, fill_opacity=1).move_to([X, Y1, 0]).set_z_index(3))
        self.add(texto(est, "Tierra", 34, est.tinta, "cuerpo", "SEMIBOLD").move_to([X + 1.7, Y0, 0]).set_z_index(10),
                 texto(est, "Luna", 34, est.tinta, "cuerpo", "SEMIBOLD").move_to([X + 1.1, Y1, 0]).set_z_index(10))
        self.add(DashedLine([X, Y0, 0], [X, Y1, 0], stroke_width=1.5, color=est.tenue, dash_length=0.15).set_opacity(0.45).set_z_index(2))
        self.add(texto(est, f"{miles(F.LUN_D)} km", 32, est.tenue, "cifra").rotate(PI / 2).move_to([X - 0.7, (Y0 + Y1) / 2, 0]).set_z_index(10))
        laser = VMobject().set_z_index(6)
        self.add(laser)

        def fase(t):
            """Segundos desde el último disparo (o −1 si aún no hay)."""
            ult = [d for d in F.LUN_DISPAROS if t >= d]
            return t - ult[-1] if ult else -1.0

        def mover(_m):
            u = fase(pel.t)
            if 0 <= u < 2 * F.LUN_IDA:
                y = Y0 + (Y1 - Y0) * (u / F.LUN_IDA if u < F.LUN_IDA else 2 - u / F.LUN_IDA)
                cola_ = 0.9 * (1 if u < F.LUN_IDA else -1)
                laser.set_points_as_corners([[X, y, 0], [X, np.clip(y - cola_, Y0, Y1), 0]]).set_stroke(color=est.calido, width=12, opacity=1)
            else:
                laser.set_stroke(opacity=0)
        laser.add_updater(mover)
        self.add(Viva(est, lambda: f"{max(0.0, min(fase(pel.t), 2 * F.LUN_IDA)):.2f} s", [3.0, 0.4, 0], 124, est.calido))
        self.add(texto(est, "reloj real", 34, est.tenue).move_to([3.0, -1.1, 0]).set_z_index(10))

        t_med = F.LUN_DISPAROS[1]
        leyenda(self, est, pel, "Esto es en tiempo real", f"la luz tarda {F.LUN_IDA:.1f} s en llegar a la Luna", 0.0, t_med)
        leyenda(self, est, pel, f"Ida y vuelta: {2 * F.LUN_IDA:.1f} s", "se mide con espejos que dejó el Apolo 11 (1969)", t_med, TB + FIN)
        cerrar(self, est, pel, self.VAR)

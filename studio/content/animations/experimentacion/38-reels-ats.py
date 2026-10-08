import sys
from pathlib import Path

sys.path.insert(0, "/workspace/studio/content/manim_extensions")
_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *

import datos_ats as DA
import divulgacion_fisica as F
from estilo_reel import Viva, cerrar_serie, chip, cola, leyenda, miles, preparar_serie, punto, texto
from reels_promo import polilinea, suave, ventana

# SERIE «ESTACIÓN ATP» — reels de divulgación con CIFRAS DE LA SIMULACIÓN de la Estación ATP (ros2-workspace, ROS 2 Jazzy).
# Mismo formato que la serie de física (37-…): título → cuerpo a ritmo de lectura → logo de Co.De → disolución al inicio (loop).
# Honestidad: todo es simulación (chip «Simulación · ROS 2» en cada reel); cada cifra viene de datos_ats.py (archivo de origen
# en sus comentarios). Nada de la tesis doctoral ni de clientes. Sin voz: solo texto y sonido sintético.

FIN = 3.0
KICKER = "Estación ATP"


def leyendas(escena, est, pel, nombre, textos):
    """`textos` = [(grande, pequeña), …] una por ventana de DA.LEYENDAS[nombre]; la última llega hasta el logo."""
    ts = list(DA.LEYENDAS[nombre]) + [DA.CUERPO[nombre] + FIN]
    for (g, p), a, b in zip(textos, ts[:-1], ts[1:]):
        leyenda(escena, est, pel, g, p, a, b)


def panel(est, x0, x1, y0, y1, op=0.35, pel=None, t0=None):
    """Recuadro del diagrama; con `pel` y `t0` aparece en t0 (así no se ve vacío antes de llenarse)."""
    r = RoundedRectangle(corner_radius=0.2, width=x1 - x0, height=y1 - y0, stroke_width=1.6, stroke_color=est.linea,
                         fill_color=est.fondo, fill_opacity=op).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0]).set_z_index(2)
    if pel is not None and t0 is not None:
        r.add_updater(lambda m: m.set_stroke(opacity=rampa(pel.t, t0 - 0.2)).set_fill(opacity=op * rampa(pel.t, t0 - 0.2)))
    return r


def rampa(t, a, d=0.6):
    return suave((t - a) / d)


# ══ 1 · ¿Qué tan fino apunta una antena? (pase simulado de ~10 min, datos del lazo ROS) ═════════════════════════════════

class ReelAtpPase(Scene):
    VAR = 0

    def construct(self):
        n = "ReelAtpPase"; TB = DA.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Qué tan fino\napunta una antena?", self.VAR)
        p = DA.pase("demo-pase"); S, M = p["series"], p["metricas"]["pointing"]
        t, az, el, ep = S["t"], S["az"], S["el"], S["e_pt"]
        Tp = t[-1]
        C, R = np.array([0.0, 2.4, 0.0]), 2.95
        polar = lambda a, e: C + R * (90 - e) / 90 * np.array([np.sin(np.radians(a)), np.cos(np.radians(a)), 0])
        for e0, op in ((0, 0.6), (30, 0.3), (60, 0.3)):
            self.add(Circle(radius=R * (90 - e0) / 90, stroke_width=2.2, stroke_color=est.tenue).set_stroke(opacity=op).move_to(C).set_z_index(3))
        self.add(DashedVMobject(Circle(radius=R * 85 / 90, stroke_width=1.8, stroke_color=est.tenue).move_to(C), num_dashes=60).set_stroke(opacity=0.4).set_z_index(3))
        for a, l in ((0, "N"), (90, "E"), (180, "S"), (270, "O")):
            self.add(texto(est, l, 28, est.tenue).move_to(polar(a, -9)).set_z_index(4))
        traza = polilinea([polar(a, e) for a, e in zip(az, el)], color=est.acento, width=3.5, opacity=0.3).set_z_index(5)
        viva = VMobject().set_z_index(6)
        sat = punto(est.calido, 0.13)
        mira = Circle(radius=0.26, stroke_width=4, stroke_color=est.acento).set_z_index(10)
        self.add(traza, viva, sat, mira)
        cola(self, sat, est.calido, n=20, ancho=6.0)

        X0, X1, Y0, Y1 = -4.5, 5.7, -5.3, -1.9                 # error en escala logarítmica (1e-4 … 1 °)
        fy = lambda e: Y0 + (np.log10(np.clip(e, 1e-4, 1.0)) + 4) / 4 * (Y1 - Y0)
        fx = lambda tt: X0 + tt / Tp * (X1 - X0)
        self.add(panel(est, X0 - 1.5, X1 + 0.3, Y0 - 0.45, Y1 + 0.5))
        for v, l in ((1e-3, "0.001°"), (1e-2, "0.01°"), (1e-1, "0.1°"), (1.0, "1°")):
            self.add(Line([X0, fy(v), 0], [X1, fy(v), 0], stroke_width=1.2, color=est.tenue).set_opacity(0.25).set_z_index(3))
            self.add(texto(est, l, 24, est.tenue).move_to([X0 - 0.75, fy(v), 0]).set_z_index(4))
        self.add(DashedLine([X0, fy(0.1), 0], [X1, fy(0.1), 0], stroke_width=3, color=est.acento, dash_length=0.18).set_z_index(5))
        self.add(texto(est, "objetivo 0.1°", 26, est.acento, "cuerpo", "SEMIBOLD").move_to([X1 - 1.2, fy(0.1) + 0.32, 0]).set_z_index(6))
        err = VMobject().set_z_index(6)
        punta = Dot(radius=0.11, color=est.calido).set_z_index(8)
        self.add(err, punta)

        def avanzar(_m):
            tp = float(np.clip((pel.t - DA.PASE_T0) / (DA.PASE_T1 - DA.PASE_T0), 0, 1)) * Tp
            i = int(np.searchsorted(t, tp))
            i = max(2, min(i, len(t)))
            viva.set_points_as_corners([polar(a, e) for a, e in zip(az[:i], el[:i])]).set_stroke(color=est.acento, width=5.5, opacity=0.95).set_fill(opacity=0)
            sat.move_to(polar(az[i - 1], el[i - 1])); mira.move_to(sat.get_center())
            pts = [[fx(t[k]), fy(ep[k]), 0] for k in range(i)]
            err.set_points_as_corners(pts).set_stroke(color=est.calido, width=5, opacity=1).set_fill(opacity=0)
            punta.move_to(pts[-1])
        sat.add_updater(avanzar)
        self.add(Viva(est, lambda: f"error {np.interp(np.clip((pel.t - DA.PASE_T0) / (DA.PASE_T1 - DA.PASE_T0), 0, 1) * Tp, t, ep):.4f}°", [-4.0, 5.0, 0], 40, est.calido))
        self.add(Viva(est, lambda: f"pase: {int(np.clip((pel.t - DA.PASE_T0) / (DA.PASE_T1 - DA.PASE_T0), 0, 1) * Tp // 60)}:{int(np.clip((pel.t - DA.PASE_T0) / (DA.PASE_T1 - DA.PASE_T0), 0, 1) * Tp % 60):02d} min", [4.2, 5.0, 0], 34, est.tenue, rol="cuerpo"))
        res = texto(est, f"rms {M['rms']:.4f}° · p95 {M['p95']:.4f}° · máx {M['max']:.4f}°", 32, est.tinta, "cuerpo", "SEMIBOLD").move_to([0.4, -0.95, 0]).set_z_index(9)
        res.add_updater(lambda m: m.set_opacity(rampa(pel.t, DA.PASE_T1 - 0.2, 0.8)))
        self.add(res)

        leyendas(self, est, pel, n, [
            ("Un pase de casi 10 minutos", "la antena sigue al satélite de horizonte a horizonte"),
            ("El error se mide en milésimas de grado", f"p95 {M['p95']:.4f}° · el objetivo era 0.1°"),
            (f"{M['rms']:.4f}° rms: {0.1 / M['rms']:.0f} veces mejor", "que el objetivo · 0.1° ≈ 1.7 cm a 10 metros")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 2 · El punto ciego sobre tu cabeza (keyhole) ══════════════════════════════════════════════════════════════════════

class ReelAtpKeyhole(Scene):
    VAR = 1

    def construct(self):
        n = "ReelAtpKeyhole"; TB = DA.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "El punto ciego\nsobre tu cabeza", self.VAR)
        chip_x = chip(est, "Pase a cámara rápida ×3", est.acento, 24).move_to([-3.5, 5.85, 0])
        self.add(chip_x)
        ts, sat, ant, az, aza = DA.keyhole_sim()
        dt = ts[1] - ts[0]
        err = np.linalg.norm(sat - ant, axis=1)
        fuera = np.cumsum(err > DA.KH_SEMIHAZ_S) * dt
        C = np.array([0.0, 1.9, 0.0])
        RS = 3.3
        zeta = np.hypot(sat[:, 0], sat[:, 1])
        vista = np.maximum.accumulate(np.maximum(7.0, 1.18 * zeta))                      # grados visibles: crece con el satélite
        vista = np.maximum.accumulate(np.convolve(vista, np.ones(60) / 60, mode="same"))
        idx = lambda: int(np.clip((DA.KH_SIM_X * (pel.t - DA.KH_T0) - 6.0 - ts[0]) / dt, 0, len(ts) - 1)) if pel.t > 0 else int((-6.0 - ts[0]) / dt)
        kk = lambda: RS / vista[idx()]
        P = lambda xy: C + kk() * np.array([xy[0], xy[1], 0])
        self.add(Circle(radius=RS, stroke_width=2.2, stroke_color=est.tenue).set_stroke(opacity=0.5).move_to(C).set_z_index(3))
        anillos = []
        for r in (5, 10, 20):
            a_ = Circle(radius=1.0, stroke_width=1.6, stroke_color=est.tenue).set_z_index(3)
            l_ = texto(est, f"{r}°", 22, est.tenue).set_z_index(4)
            anillos.append((r, a_, l_))
            self.add(a_, l_)
        trayecto = Line(ORIGIN, RIGHT, stroke_width=1.4, color=est.calido).set_z_index(3)
        self.add(trayecto, Dot(C, radius=0.05, color=est.tinta).set_z_index(5), texto(est, "cenit", 22, est.tenue).move_to(C + UP * 0.32).set_z_index(5))

        def zoom(_m):
            k_ = kk(); V = vista[idx()]
            for r, a_, l_ in anillos:
                visible = r < V * 0.98
                a_.become(Circle(radius=max(r * k_, 0.01), stroke_width=1.6, stroke_color=est.tenue).move_to(C)).set_stroke(opacity=0.28 if visible else 0).set_z_index(3)
                l_.move_to(C + np.array([r * k_ + 0.5, -0.18, 0])).set_opacity(0.8 if visible else 0)
            trayecto.put_start_and_end_on(C + k_ * np.array([-V, DA.KH_M, 0]), C + k_ * np.array([V, DA.KH_M, 0])).set_stroke(opacity=0.3)
        trayecto.add_updater(zoom)
        haz = Circle(radius=0.3, stroke_width=4, stroke_color=est.acento, fill_color=est.acento, fill_opacity=0.2).set_z_index(8)
        sat_p = punto(est.calido, 0.12)
        union = DashedLine(ORIGIN, RIGHT, stroke_width=2.5, color="#FF6B6B", dash_length=0.12).set_z_index(7)
        self.add(union, haz, sat_p)
        cola(self, sat_p, est.calido, n=22, ancho=6.0, salto=4.0)
        # brújula: acimut pedido (ámbar) frente al real (cian)
        BC, BR = np.array([-4.7, 4.1, 0.0]), 0.85
        self.add(Circle(radius=BR, stroke_width=2, stroke_color=est.tenue).set_stroke(opacity=0.6).move_to(BC).set_z_index(4),
                 texto(est, "acimut", 22, est.tenue).move_to(BC + DOWN * 1.2).set_z_index(4))
        aguja_p, aguja_r = Line(ORIGIN, UP), Line(ORIGIN, UP)
        self.add(aguja_p.set_z_index(6), aguja_r.set_z_index(6))
        self.add(texto(est, "pedido", 22, est.calido).move_to(BC + LEFT * 1.5 + UP * 0.3).set_z_index(4),
                 texto(est, "real", 22, est.acento).move_to(BC + LEFT * 1.5 + DOWN * 0.1).set_z_index(4))

        def mover(_m):
            i = idx()
            s, a = P(sat[i]), P(ant[i])
            vis = np.linalg.norm(s - C) < RS + 0.05
            sat_p.move_to(s); sat_p[1].set_opacity(1 if vis else 0); sat_p[0].set_opacity(0.16 if vis else 0)
            haz.become(Circle(radius=max(DA.KH_SEMIHAZ_S * kk(), 0.08), stroke_width=4, stroke_color=est.acento, fill_color=est.acento, fill_opacity=0.2).move_to(a)).set_z_index(8)
            union.put_start_and_end_on(a, s).set_stroke(opacity=0.9 if (err[i] > DA.KH_SEMIHAZ_S and vis) else 0)
            for ag, ang, col in ((aguja_p, az[i], est.calido), (aguja_r, aza[i], est.acento)):
                ag.put_start_and_end_on(BC, BC + BR * np.array([np.sin(np.radians(ang)), np.cos(np.radians(ang)), 0])).set_stroke(color=col, width=5)
        sat_p.add_updater(mover)
        self.add(Viva(est, lambda: f"fuera del haz: {fuera[idx()]:.0f} s", [3.7, 4.2, 0], 34, est.calido, rol="cuerpo"))

        # barras de error máximo a 89.9° (docs/SEGUIDOR.md §4.2)
        etiquetas = (("sigue y satura", DA.KH_ERR_MAX_89_9["ingenua"], est.calido, 15.5), ("se anticipa", DA.KH_ERR_MAX_89_9["anticipada"], est.acento2, 16.6),
                     ("pasa por encima", DA.KH_ERR_MAX_89_9["sobre_cenit"], est.acento, 17.7))
        self.add(texto(est, "error máximo a 89.9° de elevación", 28, est.tenue).move_to([0, -1.55, 0]).set_z_index(9).add_updater(lambda m: m.set_opacity(rampa(pel.t, 15.3))))
        for j, (lab, v, col, t0) in enumerate(etiquetas):
            y = -2.55 - 1.05 * j
            ancho = 6.2 * v / DA.KH_ERR_MAX_89_9["ingenua"]
            self.add(texto(est, lab, 28, col, "cuerpo", "SEMIBOLD").move_to([-6.2, y, 0], aligned_edge=LEFT).set_z_index(9).add_updater(lambda m, t0=t0: m.set_opacity(rampa(pel.t, t0))))
            barra = Rectangle(width=0.02, height=0.5, stroke_width=0, fill_color=col, fill_opacity=0.9).set_z_index(8)
            barra.add_updater(lambda m, ancho=ancho, y=y, col=col, t0=t0: m.become(
                Rectangle(width=max(ancho * suave((pel.t - t0) / 1.0), 0.02), height=0.5, stroke_width=0, fill_color=col, fill_opacity=0.9)
                .move_to([-2.2 + max(ancho * suave((pel.t - t0) / 1.0), 0.02) / 2, y, 0])).set_z_index(8))
            self.add(barra)
            self.add(texto(est, f"{v:.2f}°", 32, col, "cifra", "SEMIBOLD").move_to([-2.2 + ancho + 1.0, y, 0]).set_z_index(9).add_updater(lambda m, t0=t0: m.set_opacity(rampa(pel.t, t0 + 0.8))))

        leyendas(self, est, pel, n, [
            ("Un satélite pasa casi sobre tu antena", "a solo 0.1° del cenit: el caso más difícil"),
            (f"El acimut tendría que girar ≈ {np.degrees(np.radians(DA.KH_OMEGA) / np.radians(DA.KH_M)):.0f} °/s", f"el motor solo puede {DA.KH_ROTOR:.0f} °/s: se queda atrás"),
            ("El satélite se sale del haz", f"≈ {DA.KH_FUERA_S_89_9['ingenua']:.0f} s fuera · error máximo {DA.KH_ERR_MAX_89_9['ingenua']:.2f}°"),
            ("Con motor de 90°, ni el mejor programa basta", "girar la elevación hasta 180° baja el error a 0.16°")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 3 · Cuando el haz es más fino que el error (autotrack en banda Ka) ════════════════════════════════════════════════

class ReelAtpAutotrack(Scene):
    VAR = 2

    def construct(self):
        n = "ReelAtpAutotrack"; TB = DA.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "El haz es más fino\nque el error", self.VAR)
        paneles = (("solo efeméride", "demo-n5a", 2.65, "#FF6B6B"), ("con autotrack", "demo-n5b", -2.75, est.acento))
        semi = DA.KA_HAZ / 2
        s = 1.55 / semi
        for nombre, ds, cy, col in paneles:
            p = DA.pase(ds); S, M = p["series"], p["metricas"]["pointing"]
            t, e_az, e_el, el, ep = S["t"], S["e_az"], S["e_el"], S["el"], S["e_pt"]
            Tp = t[-1]
            cx = -3.7
            self.add(panel(est, -6.4, 6.4, cy - 2.45, cy + 2.45))
            self.add(Circle(radius=1.55, stroke_width=4, stroke_color=est.acento).move_to([cx, cy, 0]).set_z_index(5),
                     DashedVMobject(Circle(radius=0.1 * s, stroke_width=2.5, stroke_color=est.tinta).move_to([cx, cy, 0]), num_dashes=30).set_stroke(opacity=0.6).set_z_index(5),
                     Line([cx - 1.7, cy, 0], [cx + 1.7, cy, 0], stroke_width=1.2, color=est.tenue).set_opacity(0.4).set_z_index(4),
                     Line([cx, cy - 1.7, 0], [cx, cy + 1.7, 0], stroke_width=1.2, color=est.tenue).set_opacity(0.4).set_z_index(4))
            self.add(texto(est, nombre, 30, col, "cuerpo", "SEMIBOLD").move_to([cx, cy + 2.05, 0]).set_z_index(9))
            sat = punto(est.calido, 0.1)
            self.add(sat)
            X0, X1, Yb, Yt = -1.2, 6.0, cy - 1.6, cy + 1.45
            fy = lambda e, Yb=Yb, Yt=Yt: Yb + np.clip(e, 0, 0.26) / 0.26 * (Yt - Yb)
            fx = lambda tt, Tp=Tp: X0 + tt / Tp * (X1 - X0)
            self.add(DashedLine([X0, fy(0.1), 0], [X1, fy(0.1), 0], stroke_width=3, color=est.acento, dash_length=0.18).set_z_index(5))
            self.add(texto(est, "0.1°", 24, est.acento).move_to([X1 + 0.1, fy(0.1) + 0.28, 0]).set_z_index(6))
            self.add(Line([X0, Yb, 0], [X1, Yb, 0], stroke_width=1.5, color=est.tenue).set_opacity(0.5).set_z_index(4))
            traza = VMobject().set_z_index(6)
            self.add(traza)

            def avanzar(m, t=t, e_az=e_az, e_el=e_el, el=el, ep=ep, Tp=Tp, cx=cx, cy=cy, fx=fx, fy=fy, sat=sat, col=col):
                tp = float(np.clip((pel.t - DA.AT_T0) / (DA.AT_T1 - DA.AT_T0), 0, 1)) * Tp
                i = max(2, min(int(np.searchsorted(t, tp)), len(t)))
                off = np.array([e_az[i - 1] * np.cos(np.radians(el[i - 1])), e_el[i - 1]]) * s
                nrm = np.linalg.norm(off)
                if nrm > 2.35:
                    off = off / nrm * 2.35
                sat.move_to([cx + off[0], cy + off[1], 0])
                m.set_points_as_corners([[fx(t[k]), fy(ep[k]), 0] for k in range(i)]).set_stroke(color=col, width=5, opacity=1).set_fill(opacity=0)
            traza.add_updater(avanzar)
            cola(self, sat, est.calido, n=14, ancho=5.0, salto=3.0)
            fin = texto(est, f"{M['rms']:.4f}° rms", 36, col, "cifra", "SEMIBOLD").move_to([2.9, cy + 2.05, 0]).set_z_index(9)
            fin.add_updater(lambda m: m.set_opacity(rampa(pel.t, DA.AT_T1 - 0.4, 0.8)))
            self.add(fin)

        leyendas(self, est, pel, n, [
            (f"El haz de Ka mide {DA.KA_HAZ:.2f}°", "menos de la mitad de la Luna llena"),
            ("Solo con la efeméride, se sale del haz", "0.157° rms · 0 % del tiempo dentro de 0.1°"),
            ("Con autotrack, se queda adentro", "0.0042° rms · 100 % dentro de 0.1°")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 4 · Medir en vez de asumir (Doppler del receptor) ═════════════════════════════════════════════════════════════════

class ReelAtpDoppler(Scene):
    VAR = 0

    def construct(self):
        n = "ReelAtpDoppler"; TB = DA.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Sirve afinar\nel receptor?", self.VAR)
        p = DA.pase("demo-pase"); S = p["series"]
        t, d = S["t"], S["doppler_hz"] / 1e3
        Tp = t[-1]
        X0, X1, Yc, H = -5.0, 5.3, 2.35, 2.45
        fy = lambda kh: Yc + kh / 65.0 * H
        fx = lambda tt: X0 + tt / Tp * (X1 - X0)
        self.add(panel(est, X0 - 1.5, X1 + 0.5, Yc - H - 0.4, Yc + H + 0.4))
        self.add(Line([X0, Yc, 0], [X1, Yc, 0], stroke_width=1.6, color=est.tenue).set_opacity(0.5).set_z_index(3))
        for kh in (-50, 50):
            self.add(texto(est, f"{kh:+d}", 22, est.tenue).move_to([X0 - 0.5, fy(kh), 0]).set_z_index(4))
        self.add(texto(est, "kHz", 22, est.tenue).move_to([X0 - 0.5, Yc + H + 0.15, 0]).set_z_index(4))
        puntos = [[fx(a), fy(b), 0] for a, b in zip(t, d)]
        curva = VMobject().set_z_index(7)
        sat = punto(est.acento, 0.1)
        self.add(curva, sat)
        banda_ancha = Rectangle(width=X1 - X0, height=2 * 60.1 / 65.0 * H, stroke_width=3, stroke_color=est.calido, fill_color=est.calido, fill_opacity=0.14).move_to([(X0 + X1) / 2, Yc, 0]).set_z_index(5)
        banda_fina = VMobject().set_z_index(6)
        self.add(banda_ancha, banda_fina)

        def dibujar(_m):
            u = float(np.clip((pel.t - DA.DOP_T0) / (DA.DOP_T1 - DA.DOP_T0), 0, 1))
            i = max(2, int(u * (len(t) - 1)) + 1)
            curva.set_points_as_corners(puntos[:i]).set_stroke(color=est.acento, width=6, opacity=1).set_fill(opacity=0)
            sat.move_to(puntos[i - 1])
            a = rampa(pel.t, 6.0, 0.6)
            sh = suave((pel.t - 8.8) / 2.0)                       # la ventana se encoge de ±60 a ±3 kHz
            half = (60.1 + (3.0 - 60.1) * sh)
            banda_ancha.set_stroke(opacity=a * (1 - sh)); banda_ancha.set_fill(opacity=0.14 * a * (1 - sh))
            if sh > 0:
                alto = [[fx(tt), fy(dd + half), 0] for tt, dd in zip(t, d)]
                bajo = [[fx(tt), fy(dd - half), 0] for tt, dd in zip(t, d)]
                banda_fina.set_points_as_corners(alto + bajo[::-1] + [alto[0]]).set_fill(color=est.acento, opacity=0.3 * sh).set_stroke(color=est.acento, width=1.5, opacity=0.8 * sh)
            else:
                banda_fina.clear_points()
        curva.add_updater(dibujar)
        self.add(texto(est, "busca en ±60 kHz", 30, est.calido, "cuerpo", "SEMIBOLD").move_to([0.4, Yc + H + 0.1, 0]).set_z_index(9).add_updater(
            lambda m: m.set_opacity(rampa(pel.t, 6.0) * (1 - suave((pel.t - 8.8) / 1.0)))))
        self.add(texto(est, "busca en ±3 kHz", 30, est.acento, "cuerpo", "SEMIBOLD").move_to([0.4, Yc + H + 0.1, 0]).set_z_index(9).add_updater(
            lambda m: m.set_opacity(suave((pel.t - 9.6) / 1.0))))
        self.add(texto(est, f"muestreo: {DA.DOP_MUESTREO_S[0]} → {DA.DOP_MUESTREO_S[1]} kHz", 28, est.tinta).move_to([0.4, Yc - H - 0.1, 0]).set_z_index(9).add_updater(
            lambda m: m.set_opacity(suave((pel.t - 10.4) / 0.8))))

        # ¿se engancha más tiempo? (§5.3: 62–69 % en las cuatro configuraciones a 25 dB-Hz)
        BX0, BX1, BY = -5.6, 5.6, -3.6
        self.add(panel(est, BX0 - 0.4, BX1 + 0.4, BY - 1.5, BY + 1.5, pel=pel, t0=11.7))
        self.add(Line([BX0, BY, 0], [BX1, BY, 0], stroke_width=10, color=est.linea).set_z_index(5))
        px = lambda pc: BX0 + pc / 100 * (BX1 - BX0)
        rango = Rectangle(width=px(DA.DOP_ENGANCHE[1]) - px(DA.DOP_ENGANCHE[0]), height=0.55, stroke_width=0, fill_color=est.acento2, fill_opacity=0.95)
        rango.move_to([(px(DA.DOP_ENGANCHE[0]) + px(DA.DOP_ENGANCHE[1])) / 2, BY, 0]).set_z_index(7)
        for pc in (0, 50, 100):
            self.add(texto(est, f"{pc} %", 24, est.tenue).move_to([px(pc), BY - 0.55, 0]).set_z_index(6))
        etq = texto(est, f"las 4 configuraciones: {DA.DOP_ENGANCHE[0]}–{DA.DOP_ENGANCHE[1]} %", 30, est.acento2, "cuerpo", "SEMIBOLD").move_to([0, BY + 0.85, 0]).set_z_index(9)
        sub = texto(est, "del pase enganchado", 26, est.tenue).move_to([0, BY - 1.05, 0]).set_z_index(9)
        for m_, ts_ in ((rango, 11.7), (etq, 11.7), (sub, 11.7)):
            m_.add_updater(lambda m, ts_=ts_: m.set_opacity(rampa(pel.t, ts_, 0.7)))
        self.add(rango, etq, sub)

        leyendas(self, est, pel, n, [
            ("El satélite pasa y su tono cambia", "±50 kHz de Doppler en banda S"),
            ("Sin predecir, el receptor busca en ±60 kHz", "con la órbita bien medida, solo en ±3 kHz"),
            ("¿Se engancha más tiempo? No", f"{DA.DOP_ENGANCHE[0]}–{DA.DOP_ENGANCHE[1]} % del pase en las cuatro configuraciones"),
            ("Medimos en vez de asumir", "la ventaja es ancho de banda y cómputo, no el enganche")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 5 · El TLE envejece (determinación de órbita) ═════════════════════════════════════════════════════════════════════

class ReelAtpOrbita(Scene):
    VAR = 1

    def construct(self):
        n = "ReelAtpOrbita"; TB = DA.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Dónde está\nel satélite?", self.VAR)
        cy = 2.35
        xs = np.linspace(-5.8, 5.8, 80)
        arco = lambda x: cy + 1.0 + 0.85 * np.cos(x / 5.8 * 1.25)
        sep = lambda km: 0.42 * np.sqrt(max(km, 0.0))                          # separación exagerada (raíz del km) para que se vea
        self.add(panel(est, -6.4, 6.4, cy - 3.0, cy + 2.55))
        real = polilinea([[x, arco(x), 0] for x in xs], color=est.calido, width=6, opacity=0.95).set_z_index(6)
        pred = VMobject().set_z_index(7)
        self.add(real, pred)
        pasos = [(t0, km) for t0, (dias, km) in zip(DA.OD_PASOS, DA.OD_TLE_KM)]
        etiqueta = {0.5: "medio día", 1.0: "1 día", 2.0: "2 días", 3.0: "3 días", 5.0: "5 días"}

        def offset_km(t):
            """km de diferencia del TLE en el instante t (escalones suaves) y, tras corregir, ≈ 0."""
            v = 0.0
            for t0, km in pasos:
                v = v + (km - v) * suave((t - t0) / 0.9) if t >= t0 - 0.01 else v
            return v * (1 - suave((t - 12.8) / 1.0))

        pred.add_updater(lambda m: m.set_points_as_corners([[x, arco(x) - sep(offset_km(pel.t)) - (0.0 if offset_km(pel.t) > 0.3 else 0.06), 0] for x in xs])
                         .set_stroke(color=est.acento, width=6, opacity=1).set_fill(opacity=0))
        self.add(texto(est, "órbita real", 26, est.calido, "cuerpo", "SEMIBOLD").move_to([-4.6, cy + 2.2, 0]).set_z_index(9))
        etq_tle = texto(est, "órbita del TLE", 26, est.acento, "cuerpo", "SEMIBOLD").set_z_index(9)
        etq_tle.add_updater(lambda m: m.move_to([-4.2, arco(-4.2) - sep(offset_km(pel.t)) - 0.55, 0]))
        self.add(etq_tle)

        def edad():
            ok = [dias for (t0, _), (dias, _) in zip(pasos, DA.OD_TLE_KM) if pel.t >= t0 - 0.01]
            return etiqueta[ok[-1]] if ok else "recién medido"
        self.add(Viva(est, lambda: f"edad del TLE: {edad()}" if pel.t < 12.6 else "órbita ajustada con 3 pases", [1.2, cy + 2.2, 0], 34, est.tinta, rol="cuerpo"))
        self.add(Viva(est, lambda: f"diferencia: {offset_km(pel.t):.1f} km" if pel.t < 12.6 else "error ≈ 0.02° al siguiente pase", [2.2, cy - 2.55, 0], 38, est.acento, rol="cifra"))
        self.add(texto(est, "separación exagerada", 22, est.tenue).move_to([-4.4, cy - 2.55, 0]).set_z_index(9))

        # al final: porcentaje de pases dentro del haz de Ka (docs/OD.md §4)
        BX0, BX1 = -5.2, 5.4
        pc = lambda v: BX0 + v / 100 * (BX1 - BX0)
        for j, (lab, v, col, y) in enumerate((("TLE", DA.OD_AOS_PCT[0], est.calido, -2.6), ("órbita ajustada con 3 pases", DA.OD_AOS_PCT[1], est.acento, -4.2))):
            self.add(texto(est, lab, 28, col, "cuerpo", "SEMIBOLD").move_to([BX0 - 0.1, y + 0.62, 0], aligned_edge=LEFT).set_z_index(9).add_updater(lambda m: m.set_opacity(rampa(pel.t, 13.0))))
            self.add(Line([BX0, y, 0], [BX1, y, 0], stroke_width=9, color=est.linea).set_z_index(5))
            barra = Rectangle(width=0.02, height=0.42, stroke_width=0, fill_color=col, fill_opacity=0.95).set_z_index(7)
            barra.add_updater(lambda m, v=v, y=y, col=col: m.become(Rectangle(width=max(pc(v) - BX0, 0.02) * suave((pel.t - 13.2) / 1.4), height=0.42, stroke_width=0, fill_color=col, fill_opacity=0.95)
                                                              .move_to([BX0 + max(pc(v) - BX0, 0.02) * suave((pel.t - 13.2) / 1.4) / 2, y, 0])).set_z_index(7))
            self.add(barra)
            self.add(texto(est, f"{v} %", 34, col, "cifra", "SEMIBOLD").move_to([BX1 - 0.3 if v > 50 else pc(v) + 0.9, y + 0.62, 0]).set_z_index(9).add_updater(lambda m: m.set_opacity(rampa(pel.t, 14.4))))
        self.add(texto(est, f"de los pases quedan dentro del haz de Ka ({DA.OD_HAZ_KA}°)", 26, est.tenue).move_to([0, -5.15, 0]).set_z_index(9).add_updater(lambda m: m.set_opacity(rampa(pel.t, 13.4))))

        leyendas(self, est, pel, n, [
            ("Un TLE envejece", "su órbita se aleja de la real: 2 km en 1 día, 40 km en 5"),
            ("La estación puede corregirlo ella misma", "ajusta la órbita con lo que midió en 3 pases"),
            (f"{DA.OD_MEJORA[0]} a {DA.OD_MEJORA[1]} veces mejor al siguiente pase", f"de {DA.OD_AOS_PCT[0]} % a {DA.OD_AOS_PCT[1]} % de pases dentro del haz de Ka")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 6 · Calibrar una antena con el Sol ════════════════════════════════════════════════════════════════════════════════

class ReelAtpSol(Scene):
    VAR = 2

    def construct(self):
        n = "ReelAtpSol"; TB = DA.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Cómo se calibra\nuna antena?", self.VAR)
        C, k = np.array([0.0, 1.95, 0.0]), 1.0                    # el cielo se ve ±3° (1 unidad = 1°)
        self.add(Circle(radius=3.05, stroke_width=2.2, stroke_color=est.tenue).set_stroke(opacity=0.5).move_to(C).set_z_index(3))
        for v in (-2, -1, 1, 2):
            self.add(Line(C + np.array([v, -2.9, 0]), C + np.array([v, 2.9, 0]), stroke_width=1, color=est.tenue).set_opacity(0.15).set_z_index(3),
                     Line(C + np.array([-2.9, v, 0]), C + np.array([2.9, v, 0]), stroke_width=1, color=est.tenue).set_opacity(0.15).set_z_index(3))
        sol_xy = np.array([0.36, 0.38])                           # el Sol «verdadero» respecto del cero de la montura: |r| ≈ 0.52°
        sol = VGroup(Circle(radius=DA.SOL_DIAMETRO / 2, stroke_width=0, fill_color=est.calido, fill_opacity=1),
                     Circle(radius=DA.SOL_DIAMETRO, stroke_width=0, fill_color=est.calido, fill_opacity=0.18)).move_to(C + np.array([*sol_xy, 0])).set_z_index(6)
        self.add(sol, texto(est, "Sol (0.53°)", 26, est.calido, "cuerpo", "SEMIBOLD").move_to(C + np.array([2.0, 2.6, 0])).set_z_index(9))
        cero = Dot(C, radius=0.07, color=est.tinta).set_z_index(7)
        self.add(cero, texto(est, "donde cree apuntar", 22, est.tenue).move_to(C + np.array([-1.4, -0.45, 0])).set_z_index(9))
        haz = Circle(radius=1.59, stroke_width=4, stroke_color=est.acento, fill_color=est.acento, fill_opacity=0.12).set_z_index(5)
        rastro = VMobject().set_z_index(5)
        self.add(haz, rastro)
        a0, a1 = DA.SOL_BARRIDO_AZ; e0, e1 = DA.SOL_BARRIDO_EL
        sx = float(sol_xy[0])
        nodos = [(0.0, (-2.0, 0.0)), (a0, (-2.0, 0.0)), (a1, (2.0, 0.0)), (e0, (sx, -2.0)), (e1, (sx, 2.0)), (DA.SOL_CORRIGE, (sx, 2.0)),
                 (DA.SOL_CORRIGE + 1.4, (float(sol_xy[0]), float(sol_xy[1])))]

        def pos_haz(t):
            for (t1, p1), (t2, p2) in zip(nodos[:-1], nodos[1:]):
                if t <= t2:
                    u = 0.0 if t2 == t1 else (t - t1) / (t2 - t1)
                    u = u if (t1, t2) in ((a0, a1), (e0, e1)) else suave(u)         # los barridos son lineales; el resto, suave
                    return np.array([p1[0] + (p2[0] - p1[0]) * u, p1[1] + (p2[1] - p1[1]) * u])
            return np.array(nodos[-1][1])

        def potencia(xy):                                        # lóbulo gaussiano de 3.18° a −3 dB
            d2 = np.sum((np.asarray(xy) - sol_xy) ** 2)
            return float(np.exp(-4 * np.log(2) * d2 / 3.18 ** 2))

        def mover(m):
            t = pel.t
            q = pos_haz(t)
            haz.move_to(C + np.array([q[0], q[1], 0]))
            if a0 <= t < a1 or e0 <= t < e1:
                ini = np.array(nodos[1][1]) if t < e0 else np.array(nodos[3][1])
                m.set_points_as_corners([C + np.array([ini[0], ini[1], 0]), C + np.array([q[0], q[1], 0])]).set_stroke(color=est.acento, width=3, opacity=0.8)
            else:
                m.clear_points()
        rastro.add_updater(mover)
        # medidor de potencia
        MX, MY = 4.9, 1.95
        self.add(Line([MX, MY - 1.5, 0], [MX, MY + 1.5, 0], stroke_width=8, color=est.linea).set_z_index(5),
                 texto(est, "potencia", 22, est.tenue).move_to([MX, MY + 1.85, 0]).set_z_index(9))
        nivel = Dot(radius=0.2, color=est.acento2).set_z_index(8)
        nivel.add_updater(lambda m: m.move_to([MX, MY - 1.5 + 3.0 * potencia(pos_haz(pel.t)), 0]))
        self.add(nivel)

        # resultados (docs/PUESTA_EN_MARCHA.md §7)
        filas = (("error de la montura", f"{DA.SOL_RESIDUO[0]:.4f}° → {DA.SOL_RESIDUO[1]:.4f}°", est.acento, 9.8),
                 ("dentro de 0.1°", f"{DA.SOL_DENTRO[0]:.0f} % → {DA.SOL_DENTRO[1]:.0f} %", est.acento2, 11.0),
                 ("error de la órbita", f"{DA.SOL_OD_KM[0]:.1f} km → {DA.SOL_OD_KM[1]:.2f} km", est.calido, 14.4))
        self.add(panel(est, -6.4, 6.4, -5.5, -1.55, pel=pel, t0=filas[0][3]))
        for j, (a, b, col, t0) in enumerate(filas):
            y = -2.3 - 1.05 * j
            self.add(texto(est, a, 28, est.tenue).move_to([-6.0, y, 0], aligned_edge=LEFT).set_z_index(9).add_updater(lambda m, t0=t0: m.set_opacity(rampa(pel.t, t0))))
            self.add(texto(est, b, 36, col, "cifra", "SEMIBOLD").move_to([6.0, y, 0], aligned_edge=RIGHT).set_z_index(9).add_updater(lambda m, t0=t0: m.set_opacity(rampa(pel.t, t0 + 0.3))))

        leyendas(self, est, pel, n, [
            ("La montura apunta 0.52° desviada", "y el Sol, de 0.53°, es una referencia perfecta"),
            ("Barridos en cruz sobre el Sol", "la potencia dice dónde está el centro"),
            (f"Después de calibrar: {DA.SOL_RESIDUO[1]:.4f}°", f"{DA.SOL_RESIDUO[0] / DA.SOL_RESIDUO[1]:.0f} veces mejor · 100 % dentro de 0.1°"),
            ("Y la órbita estimada mejora", f"error de posición: de {DA.SOL_OD_KM[0]:.1f} km a {DA.SOL_OD_KM[1]:.2f} km")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 7 · Ubicarte con el Doppler de los satélites (LEO-PNT) ════════════════════════════════════════════════════════════

class ReelAtpPnt(Scene):
    VAR = 0

    def construct(self):
        n = "ReelAtpPnt"; TB = DA.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Ubicarte con el\nDoppler de satélites", self.VAR)
        C = np.array([-1.6, 1.0, 0.0])
        cep = DA.pnt_cep()
        rad = lambda m: 0.55 + 0.9 * np.log10(max(m, 4.0) / 4.0)
        cols = (est.acento2, est.acento, est.acento, est.calido, "#FF6B6B")
        t0s = (6.2, 8.4, 12.2, 14.6, 17.0)
        # 1) satélites que pasan: su Doppler «canta»
        sats = []
        for j, (R, v, ph) in enumerate(((2.4, 1.0, 0.0), (3.2, -0.7, 2.1), (2.9, 0.5, 4.2))):
            self.add(Circle(radius=R, stroke_width=1.5, stroke_color=est.tenue).set_stroke(opacity=0.2).move_to(C).set_z_index(2))
            sp = punto(est.calido, 0.1)
            enlace = DashedLine(ORIGIN, RIGHT, stroke_width=2, color=est.tinta, dash_length=0.1).set_z_index(4)
            self.add(sp, enlace)
            cola(self, sp, est.calido, n=16, ancho=5.0)
            sp.add_updater(lambda m, R=R, v=v, ph=ph, enlace=enlace: (m.move_to(C + R * np.array([np.cos(ph + v * pel.t * 0.55), np.sin(ph + v * pel.t * 0.55), 0])),
                                                                        enlace.put_start_and_end_on(C, m.get_center()).set_stroke(opacity=0.55 * (1 - suave((pel.t - 6.0) / 0.8)))))
        self.add(Dot(C, radius=0.11, color=est.tinta).set_z_index(8), texto(est, "estación", 26, est.tenue).move_to(C + DOWN * 0.45 + LEFT * 0.0).set_z_index(9))
        # 2) círculos de incertidumbre (CEP50) con escala logarítmica
        rng = np.random.default_rng(5)
        for j, ((lab, v), col, t0) in enumerate(zip(cep, cols, t0s)):
            r = rad(v)
            circ = Circle(radius=r, stroke_width=4.5, stroke_color=col).move_to(C).set_z_index(5)
            circ.add_updater(lambda m, t0=t0, j=j: m.set_stroke(opacity=rampa(pel.t, t0, 0.7) * (1.0 if (j == len(t0s) - 1 or pel.t < t0s[min(j + 1, 4)] - 0.01) else 0.38)))
            self.add(circ)
            nube = VGroup(*[Dot(radius=0.045, color=col) for _ in range(34)]).set_z_index(6)
            for d in nube:
                ang = rng.uniform(0, 2 * np.pi); rr = r * np.sqrt(-2 * np.log(1 - rng.uniform(0, 0.97))) / np.sqrt(2 * np.log(2))
                d.move_to(C + min(rr, r * 1.7) * np.array([np.cos(ang), np.sin(ang), 0]))
            nube.add_updater(lambda m, t0=t0, j=j: m.set_opacity(rampa(pel.t, t0 + 0.2, 0.8) * (1.0 if (j == len(t0s) - 1 or pel.t < t0s[min(j + 1, 4)] - 0.01) else 0.0)))
            self.add(nube)
            y = 4.6 - 0.98 * j
            val = f"{v:.0f} m" if v < 100 else (f"{v / 1000:.1f} km".replace(".", ".") if v >= 1000 else f"{v:.0f} m")
            self.add(texto(est, lab, 26, col, "cuerpo", "SEMIBOLD").move_to([6.3, y + 0.2, 0], aligned_edge=RIGHT).set_z_index(9).add_updater(lambda m, t0=t0: m.set_opacity(rampa(pel.t, t0 + 0.3))))
            self.add(texto(est, val, 34, col, "cifra", "SEMIBOLD").move_to([6.3, y - 0.2, 0], aligned_edge=RIGHT).set_z_index(9).add_updater(lambda m, t0=t0: m.set_opacity(rampa(pel.t, t0 + 0.3))))
        self.add(texto(est, "error típico (CEP50)", 24, est.tenue).move_to([-4.4, -2.2, 0]).set_z_index(9).add_updater(lambda m: m.set_opacity(rampa(pel.t, 6.4))))
        self.add(texto(est, "escala logarítmica · constelación de 72 satélites", 24, est.tenue).move_to([0, -5.2, 0]).set_z_index(9).add_updater(lambda m: m.set_opacity(rampa(pel.t, 6.4))))

        leyendas(self, est, pel, n, [
            ("Cada satélite que pasa «canta» su Doppler", "con varios pases, la estación puede ubicarse sola"),
            ("Con la órbita exacta: error de 4 metros", "mediana (CEP50) · simulación"),
            ("Con una órbita vieja, el error crece", "TLE de 1 día: 1.1 km · de 7 días: 6.7 km"),
            ("Manda la efeméride, no la antena", "con TLE gratuitos el método da kilómetros: no sustituye al GPS")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 8 · Encontrar a otro satélite con un haz láser ════════════════════════════════════════════════════════════════════

class ReelAtpLaser(Scene):
    VAR = 1

    def construct(self):
        n = "ReelAtpLaser"; TB = DA.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Dos satélites\nse buscan con un láser", self.VAR)
        chip_x = chip(est, "Cámara lenta ×6", est.acento, 24).move_to([-3.9, 5.85, 0])
        self.add(chip_x)
        C, R = np.array([0.0, 1.35, 0.0]), 3.5
        giros, th_max = 7, 14 * np.pi
        r_haz = 0.3
        self.add(Circle(radius=R + 0.3, stroke_width=2.2, stroke_color=est.tenue).set_stroke(opacity=0.45).move_to(C).set_z_index(3))
        self.add(texto(est, "zona de incertidumbre", 24, est.tenue).move_to(C + UP * (R + 0.7)).set_z_index(4))
        espiral = lambda th: C + R * (th / th_max) * np.array([np.cos(th), np.sin(th), 0])
        fantasma = polilinea([espiral(th) for th in np.linspace(0, th_max, 500)], color=est.acento, width=1.6, opacity=0.18).set_z_index(3)
        meta = C + R * 0.95 * np.array([np.cos(0.95 * th_max), np.sin(0.95 * th_max), 0])
        objetivo = punto(est.calido, 0.1).move_to(meta)
        self.add(fantasma, objetivo, Dot(C, radius=0.07, color=est.tinta).set_z_index(6))
        s0, s1 = DA.LASER_BUSCA[0], DA.LASER_ENCUENTRA

        def th_de(t):
            u = np.clip((t - s0) / (s1 - s0), 0, 1)
            return th_max * np.sqrt(u) * 0.95 if u < 1 else 0.95 * th_max

        haz = Circle(radius=r_haz, stroke_width=4, stroke_color=est.acento, fill_color=est.acento, fill_opacity=0.25).set_z_index(8)
        traza = VMobject().set_z_index(7)
        halo = Circle(radius=0.2, stroke_width=4, stroke_color=est.acento2).set_z_index(9)
        self.add(traza, haz, halo)

        def mover(m):
            t = pel.t
            th = th_de(t)
            haz.move_to(espiral(th)).set_opacity(1 if t > 0.1 else 0)
            haz.set_stroke(opacity=1 if t >= s0 - 0.2 else 0).set_fill(opacity=0.25 if t >= s0 - 0.2 else 0)
            ths = np.linspace(0, th, max(int(th / th_max * 400), 2))
            m.set_points_as_corners([espiral(a) for a in ths]).set_stroke(color=est.acento, width=4, opacity=0.9 if t >= s0 else 0).set_fill(opacity=0)
            f = (t - s1) / 1.0
            halo.move_to(meta).become(Circle(radius=0.2 + 0.9 * suave(f), stroke_width=4, stroke_color=est.acento2).move_to(meta)).set_stroke(opacity=(1 - suave(f)) if 0 <= f < 1 else 0).set_z_index(9)
        traza.add_updater(mover)
        self.add(Viva(est, lambda: f"{max(0.0, min(pel.t - s0, s1 - s0)) / 6.0:.2f} s", [-4.4, 4.9, 0], 56, est.acento))
        self.add(texto(est, "tiempo real", 22, est.tenue).move_to([-4.4, 4.2, 0]).set_z_index(9))
        enc = texto(est, "¡enlace!", 40, est.acento2, "cuerpo", "SEMIBOLD").move_to([4.1, 4.7, 0]).set_z_index(9)
        enc.add_updater(lambda m: m.set_opacity(rampa(pel.t, s1 + 0.2, 0.5)))
        self.add(enc)

        # seguimiento fino (src/sat_isl/README.md): ruido de µrad con rms medido
        X0, X1, YC = -5.4, 5.6, -3.7
        self.add(panel(est, X0 - 0.7, X1 + 0.5, -5.45, -1.95, 0.4, pel=pel, t0=9.5))
        rngl = np.random.default_rng(11)
        ruido = rngl.standard_normal(260); ruido = ruido / ruido.std() * DA.ISL_FINO_URAD
        self.add(Line([X0, YC, 0], [X1, YC, 0], stroke_width=1.5, color=est.tenue).set_opacity(0.5).set_z_index(3))
        fino = VMobject().set_z_index(6)
        fino.add_updater(lambda m: (m.set_points_as_corners([[X0 + i / 259 * (X1 - X0), YC + 0.62 * ruido[i] / 1.18, 0] for i in range(max(2, int(260 * np.clip((pel.t - 9.5) / 3.0, 0, 1))))])
                                    .set_stroke(color=est.acento2, width=4, opacity=rampa(pel.t, 9.5)).set_fill(opacity=0)))
        self.add(fino)
        self.add(texto(est, f"{DA.ISL_FINO_URAD:.2f} µrad rms · enlace cerrado {DA.ISL_CERRADO_PCT} % · {miles(DA.ISL_MBPS)} Mb/s", 28, est.acento2, "cuerpo", "SEMIBOLD").move_to([0.2, -2.45, 0]).set_z_index(9).add_updater(
            lambda m: m.set_opacity(rampa(pel.t, 12.3))))

        ancho_m = 2 * DA.ISL_SEMIHAZ_URAD * 1e-6 * DA.ISL_CUERDA_KM * 1000
        leyendas(self, est, pel, n, [
            (f"Dos satélites a {miles(DA.ISL_CUERDA_KM)} km", f"su haz mide apenas ≈ {ancho_m:.0f} m: acertar es difícil"),
            ("Se busca en espiral hasta encontrarse", f"mediana de {DA.ISL_ADQ_MEDIANA_S} s (aquí, cámara lenta ×6)"),
            (f"Después se sigue: {DA.ISL_FINO_URAD:.2f} µrad rms", f"enlace cerrado {DA.ISL_CERRADO_PCT} % · {miles(DA.ISL_MBPS)} Mb/s")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 9 · Un seguidor que mira el futuro (MPC) ══════════════════════════════════════════════════════════════════════════

class ReelAtpMpc(Scene):
    VAR = 2

    def construct(self):
        n = "ReelAtpMpc"; TB = DA.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Qué hace\ninteligente a un seguidor?", self.VAR)
        mp = DA.mpc_keyhole_89_9()
        # eje del tiempo: cuánto futuro conoce el controlador
        X0, X1, Y = -5.4, 5.4, 2.6
        tx = lambda s: X0 + s / 40.0 * (X1 - X0)
        self.add(panel(est, -6.4, 6.4, 0.55, 5.1))
        self.add(Line([X0, Y, 0], [X1, Y, 0], stroke_width=8, color=est.linea).set_z_index(4))
        for s in (0, 10, 20, 30, 40):
            self.add(Line([tx(s), Y - 0.18, 0], [tx(s), Y + 0.18, 0], stroke_width=2, color=est.tenue).set_z_index(4),
                     texto(est, f"{s} s", 22, est.tenue).move_to([tx(s), Y - 0.5, 0]).set_z_index(4))
        ahora = Triangle(fill_color=est.tinta, fill_opacity=1, stroke_width=0).scale(0.16).rotate(PI).move_to([tx(0), Y + 0.55, 0]).set_z_index(8)
        self.add(ahora, texto(est, "ahora", 26, est.tinta).move_to([tx(0) + 0.1, Y + 1.15, 0]).set_z_index(8))
        futuro = Rectangle(width=0.05, height=0.45, stroke_width=0, fill_color=est.acento, fill_opacity=0.85).set_z_index(6)

        def horizonte(t):
            if t < 6.5:
                return 0.0
            if t < 7.5:
                return 2.0 * suave(t - 6.5)
            if t < 13.0:
                return 2.0
            return 2.0 + 34.0 * suave((t - 13.0) / 3.0)
        futuro.add_updater(lambda m: m.become(Rectangle(width=max(tx(horizonte(pel.t)) - tx(0), 0.04), height=0.45, stroke_width=0, fill_color=est.acento, fill_opacity=0.85)
                                              .move_to([tx(0) + max(tx(horizonte(pel.t)) - tx(0), 0.04) / 2, Y, 0])).set_z_index(6))
        self.add(futuro)
        self.add(Viva(est, lambda: f"ve {horizonte(pel.t):.0f} s del futuro" if horizonte(pel.t) > 0.5 else "ve solo el error de ahora", [0, Y + 1.5, 0], 36, est.acento, rol="cuerpo"))

        # barras de error máximo a 89.9° (docs/mpc_resultados/keyhole.json)
        orden = (("reactivo (PID)", est.calido, 2.0), ("MPC, mira 2 s", "#FF6B6B", 8.2), ("MPC, mira 36 s", est.acento, 15.3), ("planificador (LP)", est.acento2, 15.3))
        vmax = max(mp.values())
        self.add(panel(est, -6.4, 6.4, -5.5, -0.2))
        self.add(texto(est, "error máximo a 89.9° de elevación", 26, est.tenue).move_to([0, -0.75, 0]).set_z_index(9).add_updater(lambda m: m.set_opacity(rampa(pel.t, 1.0))))
        for j, (lab, col, t0) in enumerate(orden):
            y = -1.55 - 0.95 * j
            v = mp[lab]
            ancho = 6.2 * v / vmax
            self.add(texto(est, lab, 26, col, "cuerpo", "SEMIBOLD").move_to([-6.1, y, 0], aligned_edge=LEFT).set_z_index(9).add_updater(lambda m, t0=t0: m.set_opacity(rampa(pel.t, t0 - 0.2))))
            barra = Rectangle(width=0.02, height=0.46, stroke_width=0, fill_color=col, fill_opacity=0.9).set_z_index(8)
            barra.add_updater(lambda m, ancho=ancho, y=y, col=col, t0=t0: m.become(Rectangle(width=max(ancho * suave((pel.t - t0) / 1.0), 0.02), height=0.46, stroke_width=0, fill_color=col, fill_opacity=0.9)
                                                                                    .move_to([-2.3 + max(ancho * suave((pel.t - t0) / 1.0), 0.02) / 2, y, 0])).set_z_index(8))
            self.add(barra)
            self.add(texto(est, f"{v:.1f}°", 30, col, "cifra", "SEMIBOLD").move_to([-2.3 + ancho + 0.9, y, 0]).set_z_index(9).add_updater(lambda m, t0=t0: m.set_opacity(rampa(pel.t, t0 + 0.8))))

        leyendas(self, est, pel, n, [
            ("Un seguidor reactivo llega tarde", f"solo ve el error de ahora: {mp['reactivo (PID)']:.1f}° a 89.9° de elevación"),
            ("Otro mira el futuro de la órbita", f"con solo 2 s de futuro no mejora: {mp['MPC, mira 2 s']:.1f}°"),
            (f"Con 36 s de futuro: {mp['MPC, mira 36 s']:.1f}°", "igual que el planificador: lo «inteligente» es conocer el futuro")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 10 · Mismo experimento, mismo resultado (lockstep) ════════════════════════════════════════════════════════════════

class ReelAtpLockstep(Scene):
    VAR = 0

    def construct(self):
        n = "ReelAtpLockstep"; TB = DA.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Se puede repetir\nun experimento?", self.VAR)
        chip_x = chip(est, "Trazas ilustrativas", est.acento, 24).move_to([-3.9, 5.85, 0])
        self.add(chip_x)
        X0, X1, Yc, H = -5.2, 5.4, 2.1, 2.3
        self.add(panel(est, -6.4, 6.4, Yc - H - 0.3, Yc + H + 0.5))
        self.add(Line([X0, Yc, 0], [X1, Yc, 0], stroke_width=1.5, color=est.tenue).set_opacity(0.45).set_z_index(3))
        xs = np.linspace(X0, X1, 160)
        rng = np.random.default_rng(3)
        base = 0.55 * np.sin(xs * 1.4) + 0.25 * np.sin(xs * 3.1 + 1.0)
        corridas = [base + 0.35 * np.sin(xs * (2.3 + 0.7 * j) + j) * (0.4 + 0.6 * j / 3) + 0.05 * rng.standard_normal(160) for j in range(4)]
        cols = (est.calido, est.acento, est.acento2, "#FF6B6B")
        trazas = []
        for j, (c, col) in enumerate(zip(corridas, cols)):
            tr = VMobject().set_z_index(6)
            trazas.append(tr)
            self.add(tr)

            def act(m, c=c, col=col, j=j):
                u = float(np.clip((pel.t - 1.0) / 4.5, 0, 1))
                conv = suave((pel.t - 9.0) / 2.5)                   # tras el protocolo de reloj, todas coinciden
                i = max(2, int(160 * u))
                y = c[:i] * (1 - conv) + base[:i] * conv
                m.set_points_as_corners([[xs[k], Yc + H * 0.8 * y[k], 0] for k in range(i)]).set_stroke(color=col, width=5 if conv < 0.99 else 4, opacity=1.0 if (conv < 0.99 or j == 0) else 0.0).set_fill(opacity=0)
            tr.add_updater(act)
        self.add(texto(est, "4 corridas, mismo experimento", 28, est.tenue).move_to([0, Yc + H + 0.05, 0]).set_z_index(9).add_updater(lambda m: m.set_opacity(rampa(pel.t, 1.0))))
        self.add(Viva(est, lambda: (f"{DA.LOCK_RMS_ANTES[0]:.4f} – {DA.LOCK_RMS_ANTES[1]:.4f}° rms" if pel.t < 9.0 else f"{DA.LOCK_FILAS:,} filas idénticas".replace(",", " ")), [0, -1.25, 0], 48,
                      None, f_op=lambda: rampa(pel.t, 5.4)))
        # el reloj que espera: cada paso avanza solo cuando la antena confirma
        self.add(texto(est, "el reloj espera la confirmación", 28, est.tinta, "cuerpo", "SEMIBOLD").move_to([0, -2.35, 0]).set_z_index(9).add_updater(lambda m: m.set_opacity(rampa(pel.t, 6.0))))
        paso = Dot(radius=0.14, color=est.acento).set_z_index(8)
        self.add(Line([-5.0, -3.5, 0], [5.0, -3.5, 0], stroke_width=6, color=est.linea).set_z_index(4), paso)
        marcas = VGroup(*[Line([-5.0 + 10.0 * i / 10, -3.35, 0], [-5.0 + 10.0 * i / 10, -3.65, 0], stroke_width=2.5, color=est.tenue) for i in range(11)]).set_z_index(4)
        self.add(marcas)

        def mover_paso(m):
            u = (pel.t - 6.0) / 6.0
            k = np.clip(int(u * 10) , 0, 9) + suave(((u * 10) % 1.0) / 0.35) if 0 <= u < 1 else (10 if u >= 1 else 0)
            m.move_to([-5.0 + 10.0 * k / 10, -3.5, 0]).set_opacity(rampa(pel.t, 6.0))
        paso.add_updater(mover_paso)
        self.add(texto(est, "paso", 22, est.tenue).move_to([-5.0, -4.05, 0]).set_z_index(9),
                 texto(est, "confirmación → siguiente paso", 22, est.tenue).move_to([2.2, -4.05, 0]).set_z_index(9))
        self.add(texto(est, "se puede citar y comparar", 30, est.acento2, "cuerpo", "SEMIBOLD").move_to([0, -5.0, 0]).set_z_index(9).add_updater(lambda m: m.set_opacity(rampa(pel.t, 12.8))))

        leyendas(self, est, pel, n, [
            ("Misma simulación, cuatro corridas", f"cuatro resultados distintos: {DA.LOCK_RMS_ANTES[0]:.4f} a {DA.LOCK_RMS_ANTES[1]:.4f}° rms"),
            ("El reloj espera a la antena", "avanza solo cuando el mando llegó (lockstep)"),
            ("Ahora: idénticas, bit por bit", f"{DA.LOCK_FILAS:,} filas iguales: un resultado se puede citar".replace(",", " "))])
        cerrar_serie(self, est, pel, self.VAR)

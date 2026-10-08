import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *

import datos_triage as DT
from estilo_reel import Viva, cerrar_serie, chip, leyenda, miles, preparar_serie, punto, texto
from reels_promo import polilinea, suave

# SERIE «CO.DE TRIAGE» — divulgación de la ciencia detrás del clasificador de grabaciones de satélites (code-triage) y de
# cómo funciona la plataforma. Tema ESPECTRO. Mismo formato de película que 37-/38-: título → cuerpo → logo → loop.
# Pedido del dueño (2026-10-07): explicar la ciencia de base con lenguaje llano y POCAS cifras, todas traducidas
# («95 de cada 100», «casi el doble»). Las cascadas son ilustraciones (chip «Ilustración»); las cifras salen de datos_triage.py.

FIN = 3.0
KICKER = "CO.DE Triage"
SERIE = dict(tema="espectro", fondo="reel")         # fondo vertical propio (fondos_reel.espectro): sin sombra en el centro
ROJO = "#F87171"


def leyendas(escena, est, pel, nombre, textos):
    ts = list(DT.LEYENDAS[nombre]) + [DT.CUERPO[nombre] + FIN]
    for (g, p), a, b in zip(textos, ts[:-1], ts[1:]):
        leyenda(escena, est, pel, g, p, a, b)


def rampa(t, a, d=0.6):
    return suave((t - a) / d)


def fundir(m, k):
    """Como set_opacity(k) pero relativo al relleno y trazo originales de cada pieza (guardados la primera vez)."""
    if not hasattr(m, "_base_op"):
        m._base_op = [(x, x.get_fill_opacity(), x.get_stroke_opacity()) for x in m.get_family() if isinstance(x, VMobject)]
    for x, f, s_ in m._base_op:
        x.set_fill(opacity=f * k, family=False).set_stroke(opacity=s_ * k, family=False)
    return m


def aparece(m, pel, t0, d=0.6, op=1.0):
    """Opacidad que sube en t0 (función del reloj del cuerpo: bajo el logo vuelve a 0). Respeta el relleno y el trazo
    originales de cada pieza (set_opacity a secas volvía opacos los rellenos transparentes)."""
    base = [(x, x.get_fill_opacity(), x.get_stroke_opacity()) for x in m.get_family() if isinstance(x, VMobject)]

    def act(_x):
        k = op * rampa(pel.t, t0, d)
        for x, f, s_ in base:
            x.set_fill(opacity=f * k, family=False).set_stroke(opacity=s_ * k, family=False)
    m.add_updater(act)
    act(m)
    return m


def panel(est, x0, x1, y0, y1, op=0.85, pel=None, t0=None):
    r = RoundedRectangle(corner_radius=0.2, width=x1 - x0, height=y1 - y0, stroke_width=1.6, stroke_color=est.linea,
                         fill_color=est.fondo, fill_opacity=op).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0]).set_z_index(2)
    if pel is not None and t0 is not None:
        r.add_updater(lambda m: m.set_stroke(opacity=rampa(pel.t, t0 - 0.2)).set_fill(opacity=op * rampa(pel.t, t0 - 0.2)))
    return r


def imagen(rgb, w, h, z=4):
    im = ImageMobject(np.ascontiguousarray(rgb)).set_z_index(z)
    im.stretch_to_fit_width(w).stretch_to_fit_height(h)
    return im


def cascada_img(M, w, h, z=4):
    return imagen(DT.viridis(M), w, h, z)


def tinte(est, v, color=None):
    """Matriz 0–1 → imagen del color de fondo al `color` (mapas de rasgos de la red)."""
    a = np.array(ManimColor(est.fondo).to_rgb()) * 255
    b = np.array(ManimColor(color or est.acento).to_rgb()) * 255
    v = np.clip(v, 0, 1)[..., None]
    return (a * (1 - v) + b * v).astype(np.uint8)


def cubierta(escena, est, x0, x1, y_tope, y_piso, f_y, z=5):
    """Tapa del color de fondo desde f_y() hasta y_piso: lo que está debajo aún no se dibuja."""
    r = Rectangle(width=x1 - x0, height=0.01).set_fill(est.fondo, 1).set_stroke(width=0).set_z_index(z)

    def act(m):
        y = float(np.clip(f_y(), y_piso, y_tope))
        alto = max(y - y_piso, 0.001)
        m.become(Rectangle(width=x1 - x0 + 0.02, height=alto).set_fill(est.fondo, 1).set_stroke(width=0)
                 .move_to([(x0 + x1) / 2, y_piso + alto / 2, 0]).set_z_index(z))
    r.add_updater(act)
    act(r)
    escena.add(r)
    return r


def antena(est, pos, s=1.0, color=None):
    color = color or est.tinta
    plato = Arc(radius=0.55 * s, start_angle=PI + 0.5, angle=PI - 1.0, stroke_width=5, color=color)
    plato.move_to(pos + UP * 0.55 * s)
    pie = Line(pos, pos + UP * 0.45 * s, stroke_width=5, color=color)
    base = Line(pos + LEFT * 0.35 * s, pos + RIGHT * 0.35 * s, stroke_width=5, color=color)
    return VGroup(plato, pie, base).set_z_index(8)


def sol(est, pos, r=0.32):
    g = VGroup(Circle(radius=r).set_fill(est.calido, 1).set_stroke(width=0))
    for k in range(8):
        a = k * PI / 4
        g.add(Line(r * 1.35 * np.array([np.cos(a), np.sin(a), 0]), r * 1.8 * np.array([np.cos(a), np.sin(a), 0]), stroke_width=4, color=est.calido))
    return g.move_to(pos).set_z_index(8)


def luna(est, pos, r=0.32):
    c = Circle(radius=r).set_fill(est.tinta, 1).set_stroke(width=0).move_to(pos)
    tapa = Circle(radius=r).set_fill(est.fondo, 1).set_stroke(width=0).move_to(pos + np.array([r * 0.55, r * 0.3, 0]))
    return VGroup(c, tapa).set_z_index(8)


# ══ 1 · ¿Cómo se ve una señal de radio? (espectro → cascada) ═══════════════════════════════════════════════════════════

class ReelTriCascada(Scene):
    VAR = 0

    def construct(self):
        n = "ReelTriCascada"; TB = DT.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Cómo se ve\nuna señal de radio?", self.VAR, chip_txt="Ilustración", **SERIE)
        M, cx = DT.cascada(filas=150, cols=220, semilla=5, curva=0.26)
        F_, C_ = M.shape
        X0, X1 = -6.0, 6.0
        SY0, SY1 = 1.7, 4.8
        WY0, WY1 = -5.4, 0.7
        T0, T1 = 1.0, 15.0
        self.add(panel(est, X0 - 0.35, X1 + 0.35, SY0 - 0.35, SY1 + 0.35), panel(est, X0 - 0.35, X1 + 0.35, WY0 - 0.25, WY1 + 0.25))
        self.add(texto(est, "lo que suena ahora", 26, est.tenue).next_to([X0, SY0 - 0.05, 0], RIGHT, buff=0.05).set_z_index(9))
        self.add(texto(est, "frecuencia", 26, est.tenue).move_to([X1 - 1.0, SY0 - 0.05, 0]).set_z_index(9))
        self.add(Arrow([X1 - 2.6, SY0 - 0.05, 0], [X1 - 1.95, SY0 - 0.05, 0], buff=0, stroke_width=3, color=est.tenue,
                       max_tip_length_to_length_ratio=0.35).set_z_index(9))
        im = cascada_img(M, X1 - X0, WY1 - WY0).move_to([0, (WY0 + WY1) / 2, 0])
        self.add(im)
        fila = lambda: float(np.clip((pel.t - T0) / (T1 - T0), 0, 1)) * F_
        y_fila = lambda: WY1 - fila() / F_ * (WY1 - WY0)
        cubierta(self, est, X0, X1, WY1, WY0, y_fila)
        ahora = Line([X0, 0, 0], [X1, 0, 0], stroke_width=4, color=est.acento).set_z_index(7)
        ahora.add_updater(lambda m: m.put_start_and_end_on([X0, y_fila(), 0], [X1, y_fila(), 0]).set_opacity(rampa(pel.t, T0 - 0.4) * (1 - rampa(pel.t, T1 + 0.2))))
        self.add(ahora)
        tl = texto(est, "el tiempo corre hacia abajo", 26, est.tenue).rotate(PI / 2).move_to([X0 - 0.12, (WY0 + WY1) / 2, 0]).set_z_index(9)
        self.add(aparece(tl, pel, 5.0))
        xs = np.linspace(X0, X1, C_)
        espectro = VMobject().set_z_index(8)

        def dibujar(m):
            i = int(np.clip(fila(), 1, F_ - 1))
            r = M[max(i - 2, 0):i + 1].mean(0)
            r = np.convolve(r, np.ones(3) / 3, mode="same")
            ys = SY0 + 0.15 + (r - 0.15) / 0.95 * (SY1 - SY0 - 0.3)
            m.set_points_as_corners(np.stack([xs, np.clip(ys, SY0, SY1), np.zeros_like(xs)], 1))
            m.set_stroke(color=est.acento, width=3.5, opacity=rampa(pel.t, 0.3))
        espectro.add_updater(dibujar)
        dibujar(espectro)
        self.add(espectro)
        senal = texto(est, "¡una señal!", 32, est.calido, "cuerpo", "SEMIBOLD").set_z_index(10)

        def marcar(m):
            i = int(np.clip(fila(), 1, F_ - 1))
            amp = float(np.exp(-((i / F_ - 0.5) / 0.33) ** 2))
            m.move_to([X0 + cx[i] * (X1 - X0), SY1 + 0.0, 0])
            m.set_opacity(rampa(pel.t, 3.0) * (1 - rampa(pel.t, T1)) * float(np.clip((amp - 0.25) / 0.3, 0, 1)))
        senal.add_updater(marcar)
        self.add(senal)
        circ = Circle(radius=0.75, stroke_width=4, color=est.calido).set_z_index(10)
        circ.add_updater(lambda m: m.move_to([X0 + cx[int(F_ * 0.5)] * (X1 - X0), WY1 - 0.5 * (WY1 - WY0), 0]).stretch_to_fit_height(2.6)
                         .set_stroke(opacity=rampa(pel.t, 13.0) * 0.9))
        self.add(circ)

        leyendas(self, est, pel, n, [
            ("La radio no se ve…\npero se puede dibujar", "arriba: qué frecuencias suenan en este instante"),
            ("Fila tras fila, se forma una cascada", "cada fila nueva se apila debajo de la anterior"),
            ("Una línea brillante = una señal", "lo demás es ruido: el «siseo» de fondo")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 2 · ¿Por qué la línea se curva? (efecto Doppler) ═════════════════════════════════════════════════════════════════

class ReelTriDoppler(Scene):
    VAR = 1

    def construct(self):
        n = "ReelTriDoppler"; TB = DT.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Por qué la\nlínea se curva?", self.VAR, chip_txt="Ilustración", **SERIE)
        T0, T1 = 1.0, 14.0
        G = 0.9
        self.add(Line([-6.4, G, 0], [6.4, G, 0], stroke_width=2, color=est.tenue).set_opacity(0.6).set_z_index(3))
        self.add(antena(est, np.array([0, G, 0]), 1.0))
        u = lambda: float(np.clip((pel.t - T0) / (T1 - T0), 0, 1))
        pos = lambda uu: np.array([-6.0 + 12.0 * uu, G + 3.2 - 1.3 * (2 * uu - 1) ** 2, 0])
        sat = punto(est.calido, 0.15)
        sat.add_updater(lambda m: fundir(m.move_to(pos(u())), rampa(pel.t, 0.4)))
        self.add(sat)
        ondas = []
        PERIODO, VEL, VIDA = 0.26, 1.6, 1.5
        for k in range(int((T1 - T0) / PERIODO) + 1):
            te = T0 + k * PERIODO
            c = Circle(radius=0.05, stroke_width=3, color=est.acento).set_z_index(6)

            def act(m, te=te):
                edad = pel.t - te
                if edad <= 0 or edad > VIDA or pel.t > T1 + VIDA:
                    m.set_stroke(opacity=0)
                    return
                p0 = pos(np.clip((te - T0) / (T1 - T0), 0, 1))
                m.become(Circle(radius=0.08 + VEL * edad, stroke_width=3, color=est.acento).move_to(p0).set_z_index(6))
                m.set_stroke(opacity=0.85 * (1 - edad / VIDA))
            c.add_updater(act)
            ondas.append(c)
        self.add(*ondas)

        def tono():
            if pel.t < T0 + 0.3 or pel.t > T1:
                return " "
            return "se acerca: más agudo" if u() < 0.47 else ("justo encima" if u() < 0.53 else "se aleja: más grave")
        self.add(Viva(est, tono, [0, G - 0.65, 0], 34, est.calido, rol="cuerpo"))
        # cascada: la S del Doppler se dibuja al mismo tiempo que pasa el satélite
        M, cx = DT.cascada(filas=150, cols=200, semilla=8, curva=0.30, ancho=0.012)
        X0, X1, WY0, WY1 = -6.0, 6.0, -5.4, -0.9
        self.add(panel(est, X0 - 0.3, X1 + 0.3, WY0 - 0.25, WY1 + 0.25, pel=pel, t0=T0))
        im = cascada_img(M, X1 - X0, WY1 - WY0).move_to([0, (WY0 + WY1) / 2, 0])
        im.add_updater(lambda m: m.set_opacity(rampa(pel.t, T0 - 0.2)))
        self.add(im)
        y_f = lambda: WY1 - u() * (WY1 - WY0)
        cubierta(self, est, X0, X1, WY1, WY0, y_f)
        cab = Dot(radius=0.12, color=est.calido).set_z_index(9)
        cab.add_updater(lambda m: m.move_to([X0 + np.interp(u(), np.linspace(0, 1, len(cx)), cx) * (X1 - X0), y_f(), 0])
                        .set_opacity(rampa(pel.t, T0) * (1 - rampa(pel.t, T1 + 0.3))))
        self.add(cab)
        for s, x in (("grave", X0 + 0.7), ("agudo", X1 - 0.7)):
            self.add(aparece(texto(est, s, 28, est.tinta, "cuerpo", "SEMIBOLD").move_to([x, WY1 + 0.6, 0]).set_z_index(9), pel, T0))

        leyendas(self, est, pel, n, [
            ("Como la sirena de una ambulancia", "al acercarse suena más aguda; al alejarse, más grave"),
            ("Un satélite hace lo mismo", "pasa a más de 27 000 km/h sobre la antena"),
            ("Por eso la señal dibuja una S", "es la huella de un satélite que pasa: efecto Doppler")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 3 · ¿Señal o ruido? (tres grabaciones de la red SatNOGS, ilustradas) ═════════════════════════════════════════════

class ReelTriRuido(Scene):
    VAR = 2

    def construct(self):
        n = "ReelTriRuido"; TB = DT.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Señal o ruido?", self.VAR, chip_txt="Ilustración", **SERIE)
        tipos = [("con señal", est.acento, dict(semilla=11)), ("solo ruido", est.tenue, dict(semilla=12, senal=False)),
                 ("falló", ROJO, dict(semilla=13, falla=True))]
        W_, H_ = 3.9, 7.4
        Y1, Y0 = 4.3, 4.3 - H_
        for k, (nombre, color, kw) in enumerate(tipos):
            x = -4.35 + 4.35 * k
            t0 = 1.0 + 2.2 * k
            M, _ = DT.cascada(filas=170, cols=110, curva=0.32, ancho=0.022, **kw)
            self.add(panel(est, x - W_ / 2 - 0.15, x + W_ / 2 + 0.15, Y0 - 0.15, Y1 + 0.15, pel=pel, t0=t0))
            im = cascada_img(M, W_, H_).move_to([x, (Y0 + Y1) / 2, 0])
            im.add_updater(lambda m, t0=t0: m.set_opacity(rampa(pel.t, t0 - 0.2)))
            self.add(im)
            cubierta(self, est, x - W_ / 2, x + W_ / 2, Y1, Y0, lambda t0=t0: Y1 - float(np.clip((pel.t - t0) / 2.4, 0, 1)) * H_)
            et = chip(est, nombre, color, 30).move_to([x, Y0 - 0.75, 0])
            self.add(aparece(et, pel, 5.6 + 0.5 * k))
        # el volumen: miles de grabaciones al día que pasan por debajo
        miniaturas = []
        for j in range(9):
            nombre, color, kw = tipos[j % 3]
            M, _ = DT.cascada(filas=60, cols=44, curva=0.32, ancho=0.03, **{**kw, "semilla": 40 + j})
            mi = cascada_img(M, 1.15, 1.25, z=6)
            mi.add_updater(lambda m, j=j: m.move_to([7.9 - ((pel.t - 11.0) * 1.1 + j * 1.55) % 15.8, -5.25, 0])
                           .set_opacity(rampa(pel.t, 11.0, 0.8)))
            miniaturas.append(mi)
        self.add(*miniaturas)

        leyendas(self, est, pel, n, [
            ("Cada pase deja una grabación", "estaciones de aficionados de todo el mundo · red abierta SatNOGS"),
            ("No todas traen una señal", "a veces solo hay ruido, o el equipo falla"),
            ("Revisarlas a ojo no alcanza", "llegan miles de grabaciones cada día")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 4 · ¿Cómo «ve» una IA? (red neuronal convolucional, ilustrada) ═══════════════════════════════════════════════════

class ReelTriRedNeuronal(Scene):
    VAR = 0

    def construct(self):
        n = "ReelTriRedNeuronal"; TB = DT.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Cómo «ve»\nuna IA una imagen?", self.VAR, chip_txt="Ilustración", **SERIE)
        M, _ = DT.cascada(filas=120, cols=180, semilla=21, curva=0.28, ancho=0.016)
        X0, X1, Y0, Y1 = -5.2, 5.2, 0.6, 4.9
        self.add(panel(est, X0 - 0.2, X1 + 0.2, Y0 - 0.2, Y1 + 0.2))
        self.add(cascada_img(M, X1 - X0, Y1 - Y0).move_to([0, (Y0 + Y1) / 2, 0]))
        L = 1.1                                                      # la «lupa» (filtro) recorre la imagen
        lupa = Square(side_length=L, stroke_width=5, color=est.calido).set_z_index(9)
        S0, S1, FILAS = 1.0, 6.5, 4

        def barrer(m):
            u = float(np.clip((pel.t - S0) / (S1 - S0), 0, 0.9999))
            f = int(u * FILAS); c = (u * FILAS) % 1.0
            x = X0 + L / 2 + c * (X1 - X0 - L)
            y = Y1 - L / 2 - f * (Y1 - Y0 - L) / (FILAS - 1)
            m.move_to([x, y, 0]).set_stroke(opacity=rampa(pel.t, S0 - 0.3) * (1 - rampa(pel.t, S1 + 0.1)))
        lupa.add_updater(barrer)
        self.add(lupa)
        # mapas de rasgos: bordes en distintas direcciones (convoluciones reales sobre la ilustración)
        def conv(A, k):
            from numpy.lib.stride_tricks import sliding_window_view
            v = np.abs((sliding_window_view(A, k.shape) * k).sum(axis=(-1, -2)))
            return v / (np.percentile(v, 99.5) + 1e-9)
        kernels = [np.array([[-1, 0, 1]] * 3), np.array([[-1, 0, 1]] * 3).T, np.eye(3) * 2 - 0.67, np.fliplr(np.eye(3)) * 2 - 0.67,
                   np.ones((3, 3)) / 9 - 0.11, np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])]
        rasgos = [conv(M, k) for k in kernels]
        grupos = []
        # capa 1: seis mapas · capa 2: tres mapas más pequeños · capa 3: uno
        c1 = [(rasgos[i], -5.1 + 2.45 * (i % 3), -0.75 - 1.7 * (i // 3)) for i in range(6)]
        for A, x, y in c1:
            grupos.append((imagen(tinte(est, A), 2.25, 1.45, 6).move_to([x, y, 0]), 3.2))
        p2 = [np.maximum(rasgos[0], rasgos[2])[::3, ::3], np.maximum(rasgos[1], rasgos[3])[::3, ::3], rasgos[5][::3, ::3]]
        for k, A in enumerate(p2):
            grupos.append((imagen(tinte(est, np.clip(A * 1.4, 0, 1), est.calido), 1.5, 1.0, 6).move_to([2.6, -0.5 - 1.15 * k, 0]), 7.0 + 0.4 * k))
        p3 = np.clip(sum(p2) / 2, 0, 1)[::2, ::2]
        grupos.append((imagen(tinte(est, p3, est.tinta), 1.55, 1.55, 6).move_to([5.45, -1.65, 0]), 9.4))
        for im, t0 in grupos:
            im.add_updater(lambda m, t0=t0: m.set_opacity(rampa(pel.t, t0)))
            self.add(im)
        for s, x, t0 in (("rasgos simples", -2.65, 3.2), ("formas", 2.6, 7.0), ("una idea", 5.45, 9.4)):
            self.add(aparece(texto(est, s, 26, est.tenue).move_to([x, -3.85, 0]).set_z_index(9), pel, t0))
        self.add(aparece(Arrow([0, 0.25, 0], [0, -0.15, 0], buff=0, stroke_width=5, color=est.tenue).set_z_index(9), pel, 3.0))
        for a, b, t0 in (([1.2, -1.65, 0], [1.8, -1.65, 0], 7.0), ([3.4, -1.65, 0], [4.6, -1.65, 0], 9.4)):
            self.add(aparece(Arrow(a, b, buff=0, stroke_width=4, color=est.tenue, max_tip_length_to_length_ratio=0.3).set_z_index(9), pel, t0))
        # decisión
        D = 11.8
        for k, (s, v, color) in enumerate((("señal", 0.94, est.acento), ("ruido", 0.06, est.tenue))):
            y = -4.75 - 0.75 * k
            self.add(aparece(texto(est, s, 32, est.tinta, "cuerpo", "SEMIBOLD").move_to([-4.6, y, 0]).set_z_index(9), pel, D))
            fondo_b = Rectangle(width=8.0, height=0.42).set_fill(est.linea, 0.6).set_stroke(width=0).move_to([0.75, y, 0]).set_z_index(5)
            self.add(aparece(fondo_b, pel, D))
            barra = Rectangle(width=0.01, height=0.42).set_fill(color, 1).set_stroke(width=0).set_z_index(6)
            barra.add_updater(lambda m, v=v, y=y, color=color: m.become(
                Rectangle(width=max(8.0 * v * rampa(pel.t, D + 0.3, 1.4), 0.01), height=0.42).set_fill(color, rampa(pel.t, D)).set_stroke(width=0)
                .move_to([-3.25, y, 0], aligned_edge=LEFT).set_z_index(6)))
            self.add(barra)

        leyendas(self, est, pel, n, [
            ("Primero busca rasgos pequeños", "una «lupa» recorre la imagen: bordes, líneas, manchas"),
            ("Luego los junta en formas", "una línea + una curva = la huella de un satélite"),
            ("Al final, decide: ¿señal o ruido?", "así trabaja una red neuronal convolucional")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 5 · Aprender con ejemplos (7 499 grabaciones etiquetadas; examen con las que nunca vio) ═══════════════════════════

class ReelTriAprender(Scene):
    VAR = 1

    def construct(self):
        n = "ReelTriAprender"; TB = DT.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Cómo aprende\nuna IA?", self.VAR, chip_txt="Cifras de CO.DE Triage", **SERIE)
        CO, FI = 125, 60                                             # 7 500 casillas: una por grabación (la última, vacía)
        rng = np.random.default_rng(4)
        clase = rng.choice(3, size=CO * FI, p=[0.45, 0.42, 0.13])
        cols = np.array([ManimColor(c).to_rgb() for c in (est.acento, est.tenue, ROJO)]) * 255
        fondo = np.array(ManimColor(est.fondo).to_rgb()) * 255
        rgb = cols[clase].reshape(FI, CO, 3)
        rgb = rgb * rng.uniform(0.55, 1.0, (FI, CO, 1))
        rgb[-1, -1] = fondo
        celda = 7                                                    # cada casilla con su borde oscuro
        big = np.repeat(np.repeat(rgb, celda, 0), celda, 1)
        big[celda - 1::celda] = fondo
        big[:, celda - 1::celda] = fondo
        X0, X1, Y1 = -5.75, 5.75, 4.9
        Y0 = Y1 - (X1 - X0) * FI / CO
        self.add(imagen(big.astype(np.uint8), X1 - X0, Y1 - Y0).move_to([0, (Y0 + Y1) / 2, 0]))
        R0, R1 = 0.8, 5.0
        llenas = lambda: float(np.clip((pel.t - R0) / (R1 - R0), 0, 1))
        cubierta(self, est, X0, X1, Y1, Y0, lambda: Y1 - llenas() * (Y1 - Y0))
        self.add(Viva(est, lambda: f"{miles(round(llenas() * DT.N_GRABACIONES))} ejemplos", [-2.4, Y0 - 0.6, 0], 40, est.calido, f_op=lambda: rampa(pel.t, 0.5)))
        for k, (s, c) in enumerate((("con señal", est.acento), ("sin señal", est.tenue), ("falló", ROJO))):
            g = VGroup(Square(0.26).set_fill(c, 1).set_stroke(width=0), texto(est, s, 24, est.tenue)).arrange(RIGHT, buff=0.15)
            self.add(aparece(g.move_to([1.6 + 1.85 * k, Y0 - 0.6, 0]).set_z_index(9), pel, 1.5))
        # examen: unas casillas se apartan desde el principio y nunca se usan para aprender
        h_ex = (Y1 - Y0) * 6 / FI
        caja = Rectangle(width=X1 - X0 + 0.2, height=h_ex + 0.12).set_fill(est.fondo, 0.0).set_stroke(est.calido, 5).move_to([0, Y0 + h_ex / 2, 0]).set_z_index(8)
        self.add(aparece(caja, pel, 6.3))
        velo = Rectangle(width=X1 - X0, height=h_ex).set_fill(est.fondo, 0.55).set_stroke(width=0).move_to([0, Y0 + h_ex / 2, 0]).set_z_index(7)
        self.add(aparece(velo, pel, 6.3))
        et = chip(est, "examen: nunca las vio al aprender", est.calido, 26).move_to([0, Y0 + h_ex / 2, 0]).set_z_index(9)
        self.add(aparece(et, pel, 6.8))
        # 95 de cada 100
        A = 12.5
        malos = set(np.random.default_rng(9).choice(100, 100 - DT.de_cada(DT.AUC_CLASIFICADOR), replace=False))
        orden = np.random.default_rng(10).permutation(100)
        for k in range(100):
            i, j = divmod(k, 10)
            p = np.array([-5.7 + j * 0.56, -1.95 - i * 0.42, 0])
            c = ROJO if k in malos else est.acento
            d = Circle(radius=0.17).set_fill(c, 1).set_stroke(width=0).move_to(p).set_z_index(8)
            t_k = A + 0.25 + orden[k] / 100 * 2.2
            d.add_updater(lambda m, t_k=t_k: m.set_opacity(rampa(pel.t, t_k, 0.3)))
            self.add(d)
        self.add(Viva(est, lambda: f"{int(round(DT.de_cada(DT.AUC_CLASIFICADOR) * rampa(pel.t, A + 0.25, 2.3)))} de 100", [2.6, -3.3, 0], 72, est.acento,
                      f_op=lambda: rampa(pel.t, A, 0.4)))
        self.add(aparece(texto(est, "veces bien elegidas", 32, est.tinta).move_to([2.6, -4.3, 0]).set_z_index(9), pel, A + 1.0))

        leyendas(self, est, pel, n, [
            ("Aprende con ejemplos", "miles de grabaciones, cada una con su respuesta correcta"),
            ("Y luego presenta un examen", "con grabaciones que nunca vio al aprender"),
            ("Elige bien 95 de cada 100 veces", "si le das una grabación con señal y otra sin señal")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 6 · ¿Qué hace bueno un pase? (estudio de causas con las grabaciones) ═════════════════════════════════════════════

class ReelTriBuenPase(Scene):
    VAR = 2

    def construct(self):
        n = "ReelTriBuenPase"; TB = DT.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Qué hace\nbueno un pase?", self.VAR, chip_txt="Estudio de CO.DE Triage", **SERIE)
        G = 0.9
        self.add(Line([-6.4, G, 0], [6.4, G, 0], stroke_width=2, color=est.tenue).set_opacity(0.6).set_z_index(3))
        self.add(antena(est, np.array([0, G, 0]), 0.9))
        P0, P1 = 0.8, 6.0
        for alto, color, nombre, xe in ((1.25, est.tenue, "pase bajo", -4.9), (4.0, est.acento, "pase alto", -2.1)):
            arco = lambda uu, alto=alto: np.array([-6.0 + 12 * uu, G + alto * (1 - (2 * uu - 1) ** 2), 0])
            camino = polilinea([arco(x) for x in np.linspace(0, 1, 60)], color=color, width=2.5, opacity=0.5).set_z_index(4)
            self.add(aparece(camino, pel, 0.4))
            s = punto(est.calido if alto > 2 else est.tenue, 0.13)
            s.add_updater(lambda m, arco=arco: fundir(m.move_to(arco(((pel.t - P0) / (P1 - P0)) % 1.0)), rampa(pel.t, 0.4)))
            haz = Line(ORIGIN, RIGHT, stroke_width=4 if alto > 2 else 2, color=color).set_z_index(5)
            haz.add_updater(lambda m, arco=arco, alto=alto: m.put_start_and_end_on(np.array([0, G + 0.9, 0]), arco(((pel.t - P0) / (P1 - P0)) % 1.0))
                            .set_opacity(rampa(pel.t, 0.6) * (0.9 if alto > 2 else 0.35)))
            self.add(haz, s)
            self.add(aparece(texto(est, nombre, 28, color, "cuerpo", "SEMIBOLD").move_to([xe, G + alto * 0.62, 0]).set_z_index(9), pel, 0.6))
        # barras: momios de éxito frente a un pase típico (=1)
        filas = [("Pase alto (más de 40° sobre el horizonte)", DT.OR_ELEVACION, "casi el doble", est.acento, 5.6),
                 ("Pase largo (más de 10 minutos)", DT.OR_DURACION, "1.6 veces", est.acento, 8.8),
                 ("Antena en una montaña", DT.OR_ALTITUD_ESTACION, "da igual", est.tenue, 12.2)]
        XB, K = -5.9, 4.2                                              # x del cero y unidades por «vez»
        for k, (s, v, rot, color, t0) in enumerate(filas):
            y = -0.55 - 1.65 * k
            self.add(aparece(texto(est, s, 30, est.tinta, "cuerpo", "MEDIUM").move_to([XB, y + 0.42, 0], aligned_edge=LEFT).set_z_index(9), pel, t0))
            b = Rectangle(width=0.01, height=0.5).set_z_index(6)
            b.add_updater(lambda m, v=v, y=y, color=color, t0=t0: m.become(
                Rectangle(width=max(K * v * rampa(pel.t, t0 + 0.2, 1.2), 0.01), height=0.5).set_fill(color, 0.9 * rampa(pel.t, t0)).set_stroke(width=0)
                .move_to([XB, y - 0.25, 0], aligned_edge=LEFT).set_z_index(6)))
            self.add(b)
            self.add(aparece(texto(est, rot, 32, est.calido if v > 1.2 else est.tinta, "cuerpo", "SEMIBOLD")
                             .move_to([XB + K * v + 0.25, y - 0.25, 0], aligned_edge=LEFT).set_z_index(9), pel, t0 + 1.2))
        ref = DashedLine([XB + K, -0.15, 0], [XB + K, -4.6, 0], stroke_width=3, color=est.tinta, dash_length=0.15).set_z_index(7)
        self.add(aparece(ref, pel, 5.6, op=0.8))
        self.add(aparece(texto(est, "pase típico", 26, est.tinta).move_to([XB + K, -4.95, 0]).set_z_index(9), pel, 5.6))

        leyendas(self, est, pel, n, [
            ("Un pase alto se escucha mejor", "el satélite pasa más cerca y cruza menos aire"),
            ("Y uno largo da más tiempo", "más minutos de señal, más chances de captarla"),
            ("Lo que no importó también cuenta", "la altura de la estación no cambió nada")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 7 · Un efecto que no era real (prueba de placebo) ════════════════════════════════════════════════════════════════

class ReelTriPlacebo(Scene):
    VAR = 0

    def construct(self):
        n = "ReelTriPlacebo"; TB = DT.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Un efecto\nque no era real", self.VAR, chip_txt="Estudio de CO.DE Triage", **SERIE)
        # 40 pases: 20 de día (9 con señal) y 20 de noche (14 con señal) — ilustración del patrón que parecía haber
        exito = np.array([1] * 9 + [0] * 11 + [1] * 14 + [0] * 6)
        rng = np.random.default_rng(3)
        exito = np.concatenate([rng.permutation(exito[:20]), rng.permutation(exito[20:])])
        CX = (-3.35, 3.35)

        def lugar(slot):
            col, k = divmod(slot, 20)
            i, j = divmod(k, 5)
            return np.array([CX[col] - 1.9 + 0.95 * j, 3.55 - 0.85 * i, 0])
        # rondas de barajado: elegimos permutaciones en las que la diferencia «sigue apareciendo», como pasó en los datos
        rondas, r = [], np.random.default_rng(17)
        while len(rondas) < DT.PLACEBO_REPETICIONES:
            p = r.permutation(40)                                      # p[slot] = pase en ese lugar
            if exito[p[20:]].sum() - exito[p[:20]].sum() >= 3:
                rondas.append(p)
        T_R = (6.6, 8.6, 10.6)
        ident = np.arange(40)

        def slot_de(pase, t):
            """Posición del pase `pase` en el instante t (interpola entre rondas)."""
            ords = [ident] + rondas
            k = sum(t >= x for x in T_R)
            a = int(np.where(ords[k] == pase)[0][0])
            if k >= 1 and t < T_R[k - 1] + 0.8:
                a0 = int(np.where(ords[k - 1] == pase)[0][0])
                f = suave((t - T_R[k - 1]) / 0.8)
                return lugar(a0) * (1 - f) + lugar(a) * f
            return lugar(a)
        for p in range(40):
            c = Circle(radius=0.31).set_z_index(8)
            col = est.acento if exito[p] else est.tenue
            c.set_fill(col, 1 if exito[p] else 0.0).set_stroke(col, 3)
            c.add_updater(lambda m, p=p: fundir(m.move_to(slot_de(p, pel.t)), rampa(pel.t, 0.5 + 0.02 * p, 0.3)))
            self.add(c)
        self.add(sol(est, [CX[0] - 1.25, 4.45, 0], 0.26), luna(est, [CX[1] - 1.25, 4.45, 0], 0.28))
        self.add(texto(est, "de día", 32, est.tinta, "cuerpo", "SEMIBOLD").move_to([CX[0] + 0.2, 4.45, 0]).set_z_index(9))
        self.add(texto(est, "de noche", 32, est.tinta, "cuerpo", "SEMIBOLD").move_to([CX[1] + 0.35, 4.45, 0]).set_z_index(9))
        ords = [ident] + rondas

        def tasa(col):
            k = sum(pel.t >= x for x in T_R)
            return exito[ords[k][20 * col:20 * col + 20]].sum() / 20
        for col in (0, 1):
            y = -0.25
            self.add(Rectangle(width=4.0, height=0.45).set_fill(est.linea, 0.5).set_stroke(width=0).move_to([CX[col], y, 0]).set_z_index(5))
            b = Rectangle(width=0.01, height=0.45).set_z_index(6)
            b.add_updater(lambda m, col=col, y=y: m.become(Rectangle(width=max(4.0 * tasa(col) * rampa(pel.t, 1.6, 0.8), 0.01), height=0.45)
                                                           .set_fill(est.acento, 1).set_stroke(width=0).move_to([CX[col] - 2.0, y, 0], aligned_edge=LEFT).set_z_index(6)))
            self.add(b)
            self.add(Viva(est, lambda col=col: f"{int(round(tasa(col) * 20))} de 20 con señal", [CX[col], -0.95, 0], 30, est.tinta, rol="cuerpo",
                          f_op=lambda: rampa(pel.t, 1.6)))
        # la prueba: revolver las horas al azar, tres veces
        for k, t0 in enumerate(T_R):
            x = -3.6 + 3.6 * k
            caja = RoundedRectangle(corner_radius=0.18, width=3.2, height=1.7).set_fill(est.fondo, 0.6).set_stroke(est.linea, 2).move_to([x, -2.75, 0]).set_z_index(5)
            self.add(aparece(caja, pel, t0 - 0.6))
            self.add(aparece(texto(est, f"revuelto {k + 1}", 28, est.tenue).move_to([x, -2.35, 0]).set_z_index(9), pel, t0 - 0.6))
            self.add(aparece(texto(est, "sigue ahí", 32, est.calido, "cuerpo", "SEMIBOLD").move_to([x, -3.1, 0]).set_z_index(9), pel, t0 + 1.0))
        sello = chip(est, "no era la hora: era un espejismo", ROJO, 34).move_to([0, -4.75, 0]).set_z_index(10)
        self.add(aparece(sello, pel, 12.4))

        leyendas(self, est, pel, n, [
            ("Parecía: de día se escucha peor", "los pases de día salían peor en los datos"),
            ("Prueba: revolver las horas al azar", "si el efecto no es real, debería desaparecer"),
            ("No desapareció: era un espejismo", "descartar una idea falsa también es ciencia")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 8 · «Mi IA hacía trampa» (fuga de información: la fecha de recolección) ════════════════════════════════════════════

class ReelTriTrampa(Scene):
    VAR = 1

    def construct(self):
        n = "ReelTriTrampa"; TB = DT.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Mi IA\nhacía trampa", self.VAR, chip_txt="Estudio de CO.DE Triage", **SERIE)
        self.add(texto(est, "¿En qué se fijaba para pronosticar?", 32, est.tinta, "cuerpo", "SEMIBOLD").move_to([0, 4.7, 0]).set_z_index(9))
        X0, X1, Y = -6.0, 6.0, 3.7
        xf = X0 + (X1 - X0) * DT.PRON_FECHA_GAIN
        Q = 9.0                                                     # se quita la fecha
        fecha = Rectangle(width=xf - X0, height=0.85).set_fill(ROJO, 0.85).set_stroke(width=0).move_to([(X0 + xf) / 2, Y, 0]).set_z_index(6)
        fecha.add_updater(lambda m: m.set_opacity(rampa(pel.t, 0.6) * (0.85 + 0.15 * np.sin(8 * pel.t) * rampa(pel.t, 5.5) * (1 - rampa(pel.t, Q))) * (1 - rampa(pel.t, Q, 0.8))))
        resto = Rectangle(width=X1 - xf, height=0.85).set_fill(est.acento, 0.7).set_stroke(width=0).move_to([(xf + X1) / 2, Y, 0]).set_z_index(6)
        self.add(aparece(resto, pel, 0.6), fecha)
        tf = texto(est, "la fecha: más de la mitad", 28, est.tinta, "cuerpo", "SEMIBOLD").move_to([(X0 + xf) / 2, Y, 0]).set_z_index(9)
        tf.add_updater(lambda m: m.set_opacity(rampa(pel.t, 1.0) * (1 - rampa(pel.t, Q, 0.8))))
        self.add(tf)
        self.add(aparece(texto(est, "el satélite, la altura, la duración…", 26, est.fondo, "cuerpo", "SEMIBOLD")
                         .scale_to_fit_width(X1 - xf - 0.4).move_to([(xf + X1) / 2, Y, 0]).set_z_index(9), pel, 1.0))
        # el calendario: la pista tramposa
        cal = VGroup(RoundedRectangle(corner_radius=0.15, width=2.6, height=2.3).set_fill(est.fondo, 0.8).set_stroke(ROJO, 4),
                     Rectangle(width=2.6, height=0.55).set_fill(ROJO, 0.9).set_stroke(width=0).shift(UP * 0.875))
        for i in range(3):
            for j in range(5):
                cal.add(Square(0.3).set_fill(est.tinta, 0.5).set_stroke(width=0).move_to([-0.92 + 0.46 * j, 0.25 - 0.45 * i, 0]))
        cal.move_to([-3.9, 1.0, 0]).set_z_index(8)
        self.add(aparece(cal, pel, 5.5))
        expl = VGroup(texto(est, "Los datos se juntaron en tandas.", 28, est.tinta),
                      texto(est, "Saber la fecha daba pistas de la respuesta,", 28, est.tinta),
                      texto(est, "sin entender nada del pase.", 28, est.tinta)).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        self.add(aparece(expl.move_to([2.15, 1.0, 0]).set_z_index(9), pel, 6.0))
        tache = VGroup(Line([-1.4, -1.25, 0], [1.4, 1.25, 0], stroke_width=9, color=ROJO), Line([-1.4, 1.25, 0], [1.4, -1.25, 0], stroke_width=9, color=ROJO))
        self.add(aparece(tache.move_to(cal).set_z_index(9), pel, Q, op=0.95))
        # aciertos: casi 9 de 10 con trampa → 8 de 10 sin trampa, en estaciones que nunca vio
        nivel = lambda: 10 * (DT.PRON_APARENTE + (DT.PRON_HONESTO - DT.PRON_APARENTE) * rampa(pel.t, Q + 1.5, 1.5))
        for k in range(10):
            x = -5.4 + 1.2 * k
            c = Circle(radius=0.42).set_stroke(est.linea, 3).move_to([x, -2.4, 0]).set_z_index(7)
            self.add(aparece(c, pel, 1.6))
            f = Circle(radius=0.42).set_stroke(width=0).move_to([x, -2.4, 0]).set_z_index(8)
            f.add_updater(lambda m, k=k: m.set_fill(ROJO if pel.t < Q + 1.0 else est.acento,
                                                    float(np.clip(nivel() - k, 0, 1)) * rampa(pel.t, 1.6 + 0.1 * k, 0.3)))
            self.add(f)

        def frase():
            return "casi 9 de cada 10… con trampa" if pel.t < Q + 1.5 else "8 de cada 10, sin trampa"
        self.add(Viva(est, frase, [0, -3.55, 0], 40, est.calido, f_op=lambda: rampa(pel.t, 2.0)))
        self.add(aparece(texto(est, "en estaciones que nunca había visto", 30, est.tinta).move_to([0, -4.4, 0]).set_z_index(9), pel, Q + 3.0))

        leyendas(self, est, pel, n, [
            ("Parecía muy buena para pronosticar", "si un pase iba a salir bien o mal"),
            ("Pero se fijaba en la fecha", "una pista que no explica nada del pase"),
            ("Sin la trampa: 8 de cada 10", "un número menor, pero honesto")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 9 · Así funciona CO.DE Triage (la plataforma) ════════════════════════════════════════════════════════════════════

class ReelTriPlataforma(Scene):
    VAR = 2

    def construct(self):
        n = "ReelTriPlataforma"; TB = DT.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Así funciona\nCO.DE Triage", self.VAR, chip_txt="Cómo funciona", **SERIE)
        GC, GR = np.array([-3.9, 3.35, 0]), 1.7
        globo = VGroup(Circle(radius=GR).set_fill(est.tierra, 1).set_stroke(est.tierra_borde, 3))
        for a in (-0.5, 0, 0.5):
            globo.add(Ellipse(width=2 * GR * abs(np.cos(a * 2.2)) + 0.01, height=2 * GR).set_stroke(est.tierra_borde, 1.5, 0.6))
        for yy in (-0.6, 0, 0.6):
            w = 2 * np.sqrt(max(GR ** 2 - (yy * GR) ** 2, 0))
            globo.add(Line([-w / 2, yy * GR, 0], [w / 2, yy * GR, 0], stroke_width=1.5, color=est.tierra_borde).set_opacity(0.6))
        globo.move_to(GC).set_z_index(5)
        self.add(globo)
        rng = np.random.default_rng(6)
        for k in range(26):
            r, a = GR * np.sqrt(rng.uniform(0.05, 0.85)), rng.uniform(0, TAU)
            d = Dot(GC + r * np.array([np.cos(a), np.sin(a), 0]), radius=0.06, color=est.calido).set_z_index(6)
            fase = rng.uniform(0, 1)
            d.add_updater(lambda m, fase=fase: m.set_opacity(0.45 + 0.55 * max(0, np.sin(2 * PI * (pel.v * 0.5 + fase))) ** 2))
            self.add(d)
        self.add(texto(est, "estaciones de la", 32, est.tenue).move_to([1.3, 3.75, 0]).set_z_index(9))
        self.add(texto(est, "red SatNOGS", 42, est.tinta, "cuerpo", "SEMIBOLD").move_to([1.3, 3.1, 0]).set_z_index(9))
        reloj = VGroup(Circle(radius=0.5).set_stroke(est.acento, 3)).move_to([4.95, 3.65, 0]).set_z_index(8)
        manecilla = Line(ORIGIN, UP * 0.4, stroke_width=4, color=est.acento).set_z_index(9)
        manecilla.add_updater(lambda m: m.put_start_and_end_on(np.array([4.95, 3.65, 0]), np.array([4.95, 3.65, 0]) + 0.4 * np.array([np.sin(PI * pel.t), np.cos(PI * pel.t), 0])))
        self.add(reloj, manecilla, texto(est, "cada 30 min", 26, est.acento).move_to([4.95, 2.85, 0]).set_z_index(9))
        # la IA
        IA = np.array([0, 0.15, 0])
        chip_ia = VGroup(RoundedRectangle(corner_radius=0.12, width=1.5, height=1.5).set_fill(est.fondo, 1).set_stroke(est.acento, 4))
        for k in range(4):
            for s in (-1, 1):
                chip_ia.add(Line([-0.45 + 0.3 * k, s * 0.75, 0], [-0.45 + 0.3 * k, s * 0.98, 0], stroke_width=4, color=est.acento))
                chip_ia.add(Line([s * 0.75, -0.45 + 0.3 * k, 0], [s * 0.98, -0.45 + 0.3 * k, 0], stroke_width=4, color=est.acento))
        chip_ia.add(texto(est, "IA", 40, est.acento, "titulo", "BOLD"))
        chip_ia.scale(1.35).move_to(IA + LEFT * 2.4).set_z_index(8)
        self.add(aparece(chip_ia, pel, 5.6))
        self.add(aparece(VGroup(texto(est, "en una computadora", 32, est.tinta), texto(est, "normal, sin tarjeta", 32, est.tinta),
                                texto(est, "gráfica", 32, est.tinta)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(chip_ia, RIGHT, buff=0.6).set_z_index(9), pel, 6.0))
        # cajones
        CAJ = [("con señal", est.acento, -4.35), ("sin señal", est.tenue, 0.0), ("dudosas:\nrevisión", est.calido, 4.35)]
        for s, c, x in CAJ:
            caja = RoundedRectangle(corner_radius=0.2, width=4.0, height=3.1).set_fill(est.fondo, 0.6).set_stroke(c, 3).move_to([x, -3.75, 0]).set_z_index(5)
            self.add(aparece(caja, pel, 6.4))
            et = VGroup(*[texto(est, l, 32, c, "cuerpo", "SEMIBOLD") for l in s.split("\n")]).arrange(DOWN, buff=0.08).move_to([x, -1.85, 0]).set_z_index(9)
            if "\n" in s:
                et.move_to([x, -1.6, 0])
            self.add(aparece(et, pel, 6.4))
        # grabaciones que fluyen: del mundo → a la IA (a partir de 6 s) → a su cajón
        rng = np.random.default_rng(14)
        P_IA = IA + LEFT * 2.4
        miniat = {}
        for k, kw in enumerate((dict(semilla=50), dict(semilla=51, senal=False), dict(semilla=52, debil=0.35))):
            M, _ = DT.cascada(filas=50, cols=40, curva=0.32, ancho=0.03, **kw)
            miniat[k] = DT.viridis(M)
        destinos = rng.choice(3, size=24, p=[0.42, 0.45, 0.13])
        for j, dest in enumerate(destinos):
            t0 = 6.0 + 0.45 * j
            im = imagen(miniat[int(dest)], 1.0, 1.15, 7)
            fin = np.array([CAJ[dest][2] - 1.2 + 0.6 * (j % 5), -3.35 - 0.75 * ((j // 5) % 2), 0])

            def mover(m, t0=t0, fin=fin):
                e = pel.t - t0
                if e < 0:
                    m.set_opacity(0)
                    return
                if e < 0.9:                                         # del mundo a la IA
                    f = suave(e / 0.9); p = GC * (1 - f) + P_IA * f
                else:                                               # de la IA a su cajón
                    f = suave((e - 0.9) / 0.9); p = P_IA * (1 - f) + fin * f
                m.move_to(p).set_opacity(rampa(pel.t, t0, 0.25))
            im.add_updater(mover)
            self.add(im)

        leyendas(self, est, pel, n, [
            ("Estaciones de todo el mundo graban", "red abierta SatNOGS · llegan grabaciones nuevas cada 30 min"),
            ("Una IA las separa sola", "corre en una computadora normal, sin tarjeta gráfica"),
            ("Tú revisas solo lo que vale la pena", "lo dudoso se marca para que lo vea una persona")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 10 · ¿Saldrá bien tu próximo pase? (pronóstico que ordena la agenda, en el navegador) ═══════════════════════════════

class ReelTriPronostico(Scene):
    VAR = 0

    def construct(self):
        n = "ReelTriPronostico"; TB = DT.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Saldrá bien\ntu próximo pase?", self.VAR, chip_txt="Cómo funciona", **SERIE)
        pases = [("19:05", 18, 5), ("20:40", 72, 11), ("21:15", 33, 7), ("22:50", 12, 4), ("23:30", 47, 9)]
        score = [0.18 + 0.55 * (e / 90) + 0.25 * (d / 12) for _, e, d in pases]          # ilustración: sube con altura y duración
        orden = list(np.argsort(score)[::-1])
        Y0, PASO = 4.0, 1.55
        R0, R1 = 6.0, 7.6                                                  # se reordena la agenda
        self.add(texto(est, "tus próximos pases", 32, est.tenue).move_to([-6.2, Y0 + 0.95, 0], aligned_edge=LEFT).set_z_index(9))
        for i, (h, e, d) in enumerate(pases):
            rango = orden.index(i)
            y_ini, y_fin = Y0 - PASO * i, Y0 - PASO * rango
            g = VGroup()
            g.add(RoundedRectangle(corner_radius=0.15, width=12.8, height=1.32).set_fill(est.fondo, 0.7).set_stroke(est.linea, 2))
            g.add(texto(est, h, 42, est.tinta, "cifra", "SEMIBOLD").move_to([-5.2, 0, 0]))
            alto = 0.75 * e / 90
            g.add(polilinea([np.array([-3.85 + 1.1 * x, -0.3 + alto * 4 * x * (1 - x) + 0.0, 0]) for x in np.linspace(0, 1, 30)], color=est.acento, width=3, opacity=0.9))
            g.add(Line([-3.95, -0.32, 0], [-2.65, -0.32, 0], stroke_width=2, color=est.tenue))
            g.add(texto(est, f"{e}° · {d} min", 34, est.tinta).move_to([-0.85, 0, 0]))
            g.add(Rectangle(width=4.0, height=0.46).set_fill(est.linea, 0.5).set_stroke(width=0).move_to([3.95, 0, 0]))
            g.set_z_index(6)
            barra = Rectangle(width=0.01, height=0.46).set_z_index(7)
            t0 = 1.0 + 0.5 * i

            def pos_y(y_ini=y_ini, y_fin=y_fin):
                return y_ini + (y_fin - y_ini) * rampa(pel.t, R0, R1 - R0)
            g.add_updater(lambda m, pos_y=pos_y, t0=t0: fundir(m.move_to([0, pos_y(), 0]), rampa(pel.t, t0, 0.4)))
            barra.add_updater(lambda m, s=score[i], pos_y=pos_y, t0=t0, rango=rango: m.become(
                Rectangle(width=max(4.0 * s * rampa(pel.t, t0 + 1.4, 1.2), 0.01), height=0.46)
                .set_fill(est.calido if (rango == 0 and pel.t > R1) else est.acento, rampa(pel.t, t0 + 1.2)).set_stroke(width=0)
                .move_to([1.95, pos_y(), 0], aligned_edge=LEFT).set_z_index(7)))
            self.add(g, barra)
        mejor = chip(est, "primero este", est.calido, 26).set_z_index(10)
        mejor.add_updater(lambda m: m.move_to([4.6, Y0 + 0.95, 0]).set_opacity(rampa(pel.t, R1 + 0.2)))
        self.add(mejor)
        # el navegador
        B = 12.0
        nav = VGroup(RoundedRectangle(corner_radius=0.2, width=9.0, height=2.6).set_fill(est.fondo, 0.85).set_stroke(est.acento, 3),
                     Line([-4.5, 0.75, 0], [4.5, 0.75, 0], stroke_width=2, color=est.acento))
        for k in range(3):
            nav.add(Dot([-4.15 + 0.3 * k, 1.03, 0], radius=0.08, color=est.acento))
        nav.add(texto(est, "corre en tu navegador", 34, est.tinta, "cuerpo", "SEMIBOLD").move_to([0, 0.15, 0]))
        nav.add(texto(est, "sin instalar nada", 28, est.tenue).move_to([0, -0.55, 0]))
        nav.move_to([0, -4.35, 0]).set_z_index(8)
        self.add(aparece(nav, pel, B))

        leyendas(self, est, pel, n, [
            ("Antes de que el satélite salga", "un modelo estima qué pases valen la pena"),
            ("Y ordena tu agenda", "los más altos y largos suben primero"),
            ("Es un orden, no una promesa", "una ayuda para decidir a qué pase apuntar")])
        cerrar_serie(self, est, pel, self.VAR)

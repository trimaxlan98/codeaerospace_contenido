"""Plataformas Co.De Aerospace - ilustraciones (stickers) de las plataformas sin imagen propia.

Escenas: BusNexus (CODE-Nexus), TriageCascadas (CO.DE Triage), RielTelemetria (PiStation),
UnPaseCincoPlataformas (cadena de plataformas de un pase).
Fuente de fidelidad: redes/fuentes/codeaerospace_plataformas_2026-10-01.txt. Sin cifras.
"""
from code_lib import *

C_BUS = C_OK  # eventos firmados / lo que fluye


# ---------------------------------------------------------------- helpers
def sobre(tam=0.5, color=None):
    """Sobre con candado: evento firmado."""
    c = color or C_SAT
    w, h = tam * 1.5, tam
    cuerpo = RoundedRectangle(corner_radius=tam * 0.1, width=w, height=h, color=c,
                              fill_color=FONDO, fill_opacity=1, stroke_width=2.2)
    solapa = VMobject().set_points_as_corners(
        [cuerpo.get_corner(UL) + DR * 0.02, cuerpo.get_center() + UP * h * 0.05,
         cuerpo.get_corner(UR) + DL * 0.02]).set_stroke(c, 2, 0.9)
    cand = VGroup(
        Arc(radius=tam * 0.13, start_angle=0, angle=PI, color=C_OK, stroke_width=2.2)
        .move_to(cuerpo.get_bottom() + UP * h * 0.62 + RIGHT * w * 0.3),
        RoundedRectangle(corner_radius=0.02, width=tam * 0.3, height=tam * 0.22, color=C_OK,
                         fill_color=C_OK, fill_opacity=1, stroke_width=0)
        .move_to(cuerpo.get_bottom() + UP * h * 0.38 + RIGHT * w * 0.3))
    cand[0].align_to(cand[1], DOWN).shift(UP * tam * 0.18)
    cand.move_to(cuerpo.get_corner(DR) + UL * tam * 0.2)
    return VGroup(cuerpo, solapa, cand)


def cuadro_cascada(ancho=1.25, alto=1.6, senal=True, semilla=0, filas=36, cols=28):
    """Waterfall: espectrograma con ruido y, si hay señal, la S del Doppler."""
    rng = np.random.default_rng(semilla)
    img = rng.random((filas, cols)) ** 2 * 0.45
    if senal:
        for r in range(filas):
            x = r / (filas - 1)
            c = cols * (0.5 + 0.28 * np.tanh(3.2 * (0.5 - x)))
            for dc in (-1, 0, 1):
                j = int(round(c)) + dc
                if 0 <= j < cols:
                    img[r, j] = max(img[r, j], 0.95 if dc == 0 else 0.7)
    pal = np.array([[10, 14, 39], [26, 40, 110], [0, 150, 210], [0, 217, 255], [250, 240, 160]], float)
    idx = np.clip(img, 0, 1) * (len(pal) - 1)
    i0 = np.floor(idx).astype(int).clip(0, len(pal) - 2)
    f = (idx - i0)[..., None]
    rgb = (pal[i0] * (1 - f) + pal[i0 + 1] * f).astype(np.uint8)
    rgba = np.dstack([rgb, np.full(rgb.shape[:2], 255, np.uint8)])
    im = ImageMobject(rgba, resampling_algorithm=RESAMPLING_ALGORITHMS["nearest"])
    im.stretch_to_fit_height(alto * 0.84)
    im.stretch_to_fit_width(ancho * 0.88)
    marco = RoundedRectangle(corner_radius=0.08, width=ancho, height=alto, color=C_ANT if senal else TENUE,
                             fill_color=C_PANEL, fill_opacity=1, stroke_width=2.2)
    im.move_to(marco.get_center())
    return Group(marco, im)


def pi_placa(ancho=3.4, alto=2.2, color=None):
    """Raspberry Pi: placa con chip, conectores USB/Ethernet y cabecera GPIO."""
    c = color or C_OK
    placa = RoundedRectangle(corner_radius=0.14, width=ancho, height=alto, color=c,
                             fill_color=C_PANEL, fill_opacity=1, stroke_width=3)
    g = VGroup(placa)
    soc = Square(alto * 0.34, color=TENUE, fill_color=C_EJE, fill_opacity=1, stroke_width=1.5)
    soc.move_to(placa.get_center() + LEFT * ancho * 0.12 + DOWN * alto * 0.02)
    ram = Rectangle(width=alto * 0.28, height=alto * 0.2, color=TENUE, fill_color=C_EJE,
                    fill_opacity=0.9, stroke_width=1.5).next_to(soc, RIGHT, buff=0.2)
    g.add(soc, ram)
    # GPIO: dos filas de pines arriba
    pines = VGroup(*[Square(0.07, stroke_width=0, fill_color=C_SAT, fill_opacity=1) for _ in range(20)])
    pines.arrange_in_grid(2, 10, buff=0.05)
    pines.move_to(placa.get_top() + DOWN * 0.26)
    g.add(pines)
    # conectores del borde derecho: 2 USB + Ethernet
    for k, col in enumerate((C_ANT, C_ANT, C_CIELO)):
        h = alto * (0.24 if k < 2 else 0.3)
        con = Rectangle(width=0.5, height=h, color=col, fill_color=col, fill_opacity=0.35, stroke_width=2.2)
        con.move_to(placa.get_right() + LEFT * 0.27 + UP * (alto * 0.3 - k * alto * 0.3 - (0.04 if k == 2 else 0)))
        g.add(con)
    # conectores del borde izquierdo: alimentación y micro-HDMI
    for k in range(2):
        con = Rectangle(width=0.32, height=alto * 0.16, color=C_EJE, fill_color=TENUE,
                        fill_opacity=0.6, stroke_width=1.8)
        con.move_to(placa.get_left() + RIGHT * 0.2 + UP * (-alto * 0.1 - k * alto * 0.22))
        g.add(con)
    g.add(Dot(placa.get_corner(DR) + UL * 0.2, radius=0.06, color=C_OK))  # LED
    return g


# ===================================================================
#  1. CODE-Nexus: hub, seis servicios en anillo y bus de eventos firmados
# ===================================================================
class BusNexus(Pieza):
    def construct(self):
        R = 2.55
        c0 = ORIGIN
        angulos = [90 + 60 * k for k in range(6)]
        pos = [c0 + R * np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0]) for a in angulos]

        hub = VGroup(
            Circle(radius=0.95, color=C_ANT, fill_color=FONDO, fill_opacity=1, stroke_width=4),
            Circle(radius=0.72, color=C_ANT, stroke_width=1.6, stroke_opacity=0.7),
            et("CODE-Nexus", 24, TINTA))
        hub.set_z_index(5)
        anillo = Circle(radius=R, color=C_EJE, stroke_width=2.5, stroke_opacity=0.9)
        espigas = VGroup(*[Line(c0, p, color=C_EJE, stroke_width=2.5) for p in pos])
        # servicios (iconos propios)
        def ic_estacion():
            return estacion(0.55, C_ANT)

        def ic_gemelo(color):
            g = VGroup(Circle(radius=0.26, color=color, fill_color=color, fill_opacity=0.3, stroke_width=2.2),
                       Ellipse(width=0.52, height=0.17, color=color, stroke_width=1.5))
            g.add(Circle(radius=0.42, color=C_SAT, stroke_width=1.2, stroke_opacity=0.9).stretch(1.0, 1))
            g.add(Dot(g[2].point_at_angle(0.6), radius=0.045, color=C_SAT))
            return g

        def ic_clasif():
            g = VGroup(*[Rectangle(width=0.14, height=h, color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.5,
                                   stroke_width=1.5) for h in (0.5, 0.34, 0.22)])
            g.arrange(RIGHT, buff=0.08)
            return g

        def ic_gob():
            esc = Polygon([-0.3, 0.3, 0], [0.3, 0.3, 0], [0.3, -0.05, 0], [0, -0.34, 0], [-0.3, -0.05, 0],
                          color=C_OK, fill_color=C_OK, fill_opacity=0.28, stroke_width=2.4)
            chk = VMobject().set_points_as_corners([[-0.13, 0.0, 0], [-0.03, -0.1, 0], [0.15, 0.13, 0]])
            chk.set_stroke(C_OK, 3.5)
            return VGroup(esc, chk)

        def ic_lab():
            fr = Polygon([-0.08, 0.34, 0], [0.08, 0.34, 0], [0.08, 0.08, 0], [0.3, -0.3, 0], [-0.3, -0.3, 0],
                         [-0.08, 0.08, 0], color=C_SAT, fill_color=C_SAT, fill_opacity=0.3, stroke_width=2.4)
            bur = VGroup(Dot([-0.05, -0.15, 0], 0.04, color=C_SAT), Dot([0.08, -0.08, 0], 0.03, color=C_SAT))
            return VGroup(fr, bur)

        iconos = [ic_estacion(), ic_gemelo(C_ANT), ic_gemelo(C_CIELO), ic_clasif(), ic_gob(), ic_lab()]
        textos = ["Estación terrena", "Gemelo SAT-DT", "Gemelo ATP-DT", "Clasificador", "Gobernanza", "Laboratorio"]
        colores = [C_ANT, C_ANT, C_CIELO, C_CIELO, C_OK, C_SAT]
        nodos = VGroup()
        etqs = VGroup()
        for p, ic, tx, col in zip(pos, iconos, textos, colores):
            disco = Circle(radius=0.62, color=col, fill_color=FONDO, fill_opacity=1, stroke_width=3.2).move_to(p)
            ic.set_height(min(ic.height, 0.62)) if ic.height > 0.62 else None
            ic.move_to(p)
            nodos.add(VGroup(disco, ic))
        # etiquetas fuera del anillo
        for p, tx, a in zip(pos, textos, angulos):
            u = np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0])
            t = et(tx, 22, TINTA)
            sg = -1 if u[0] < -0.2 else 1
            t.move_to(p + RIGHT * sg * (0.62 + 0.2 + t.width / 2))
            etqs.add(t)

        self.play(FadeIn(hub, scale=0.7), Create(anillo), run_time=1.0)
        self.play(LaggedStart(*[Create(e) for e in espigas], lag_ratio=0.1), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(n, scale=0.6) for n in nodos], lag_ratio=0.12),
                  LaggedStart(*[FadeIn(t) for t in etqs], lag_ratio=0.12), run_time=1.4)

        # eventos firmados viajando: nodo -> hub y hub -> nodo, por las espigas
        def viaje(i, ida=True, col=None):
            s = sobre(0.4, col or C_SAT)
            a, b = (pos[i], c0) if ida else (c0, pos[i])
            u = (b - a) / np.linalg.norm(b - a)
            a2, b2 = a + u * 0.66, b - u * (0.95 if ida else 0.66)
            if not ida:
                a2, b2 = c0 + u * 0.97, pos[i] - u * 0.66
            s.move_to(a2)
            return s, a2, b2

        sobres = []
        for i, ida in ((0, True), (3, True), (1, False), (4, True), (5, False), (2, True)):
            s, a2, b2 = viaje(i, ida)
            sobres.append((s, a2, b2))
        # primera oleada animada
        self.add(*[s for s, _, _ in sobres])
        self.play(*[s.animate.move_to(b2) for s, a2, b2 in sobres[:3]],
                  FadeIn(sobres[3][0]), FadeIn(sobres[4][0]), FadeIn(sobres[5][0]), run_time=2.2)
        # estado final: sobres repartidos sobre las espigas, bien legibles
        finales = [(0, 0.5), (3, 0.5), (1, 0.55), (4, 0.5), (5, 0.55), (2, 0.5)]
        anim = []
        for (s, a2, b2), (i, f) in zip(sobres, finales):
            anim.append(s.animate.move_to(c0 + (pos[i] - c0) * (0.62 if f == 0.5 else 0.66)))
        self.play(*anim, run_time=1.4)
        # latido del hub
        self.play(Indicate(hub[0], color=C_ANT, scale_factor=1.06), run_time=0.9)
        self.wait(3.0)
        self.cierre()


# ===================================================================
#  2. CO.DE Triage: waterfalls -> CNN -> con señal / sin señal
# ===================================================================
class TriageCascadas(Pieza):
    def construct(self):
        entrada = Group(*[cuadro_cascada(senal=s, semilla=k) for k, s in enumerate((False, True, False, True))])
        # pila de entrada, ligeramente escalonada
        for k, c in enumerate(entrada):
            c.move_to(np.array([-5.1 + 0.28 * k, 0.9 - 0.28 * k, 0]))
        cnn = VGroup(
            RoundedRectangle(corner_radius=0.16, width=2.3, height=2.7, color=C_CIELO,
                             fill_color=C_CIELO, fill_opacity=0.14, stroke_width=3.2))
        capas = VGroup(*[Rectangle(width=0.22, height=h, color=C_CIELO, fill_color=C_CIELO, fill_opacity=0.55,
                                   stroke_width=1.6) for h in (1.5, 1.15, 0.85, 0.55)])
        capas.arrange(RIGHT, buff=0.14).move_to(cnn.get_center() + UP * 0.2)
        cnn_et = et("CNN", 26, TINTA).move_to(cnn.get_bottom() + UP * 0.36)
        cnn.add(capas, cnn_et)
        cnn.move_to(LEFT * 0.4)

        arriba = Group(cuadro_cascada(senal=True, semilla=11), cuadro_cascada(senal=True, semilla=12))
        abajo = Group(cuadro_cascada(senal=False, semilla=21), cuadro_cascada(senal=False, semilla=22))
        for g, y in ((arriba, 1.75), (abajo, -1.75)):
            for j, c in enumerate(g):
                c.move_to(np.array([3.4 + 1.55 * j, y, 0]))
        carril_ok = RoundedRectangle(corner_radius=0.2, width=3.7, height=2.3, color=C_OK, stroke_width=2.5,
                                     fill_color=C_OK, fill_opacity=0.1).move_to(np.array([3.95, 1.75, 0]))
        carril_no = RoundedRectangle(corner_radius=0.2, width=3.7, height=2.3, color=C_MAL, stroke_width=2.5,
                                     fill_color=C_MAL, fill_opacity=0.08).move_to(np.array([3.95, -1.75, 0]))
        t_ok = et("Con señal", 24, C_OK).next_to(carril_ok, UP, buff=0.12)
        t_no = et("Sin señal", 24, C_MAL).next_to(carril_no, DOWN, buff=0.12)
        marca_ok = VGroup(Circle(radius=0.2, color=C_OK, fill_color=C_OK, fill_opacity=1, stroke_width=0),
                          VMobject().set_points_as_corners([[-0.09, 0, 0], [-0.02, -0.08, 0], [0.1, 0.09, 0]])
                          .set_stroke(FONDO, 3.5)).move_to(carril_ok.get_corner(UL) + DR * 0.0)
        marca_no = VGroup(Circle(radius=0.2, color=C_MAL, fill_color=C_MAL, fill_opacity=1, stroke_width=0),
                          VGroup(Line([-0.08, -0.08, 0], [0.08, 0.08, 0]), Line([-0.08, 0.08, 0], [0.08, -0.08, 0]))
                          .set_stroke(FONDO, 3.5)).move_to(carril_no.get_corner(UL))
        f_in = flecha(np.array([-3.25, 0, 0]), cnn.get_left() + LEFT * 0.08, C_ANT)
        f_ok = flecha(cnn.get_right() + RIGHT * 0.08 + UP * 0.35, np.array([1.95, 1.75, 0]), C_OK)
        f_no = flecha(cnn.get_right() + RIGHT * 0.08 + DOWN * 0.35, np.array([1.95, -1.75, 0]), C_MAL)

        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in entrada], lag_ratio=0.2), run_time=1.4)
        self.play(FadeIn(cnn, scale=0.8), GrowArrow(f_in), run_time=1.0)
        self.play(Indicate(capas, color=C_CIELO, scale_factor=1.08), run_time=0.9)
        self.play(GrowArrow(f_ok), GrowArrow(f_no), FadeIn(carril_ok), FadeIn(carril_no), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.4) for c in arriba], lag_ratio=0.3),
                  LaggedStart(*[FadeIn(c, shift=RIGHT * 0.4) for c in abajo], lag_ratio=0.3), run_time=1.4)
        for c in abajo:
            c[0].set_stroke(C_MAL, opacity=0.8)
        self.play(*[c[1].animate.set_opacity(0.35) for c in abajo], FadeIn(t_ok), FadeIn(t_no),
                  FadeIn(marca_ok), FadeIn(marca_no), run_time=0.9)
        self.wait(3.0)
        self.cierre()


# ===================================================================
#  3. PiStation: Raspberry Pi -> telemetría con banda ±3σ y una anomalía
# ===================================================================
class RielTelemetria(Pieza):
    def construct(self):
        pi = pi_placa().move_to(np.array([-4.9, 0.1, 0]))
        etq_pi = et("Raspberry Pi", 24, TINTA).next_to(pi, DOWN, buff=0.3)

        # eje del gráfico
        x0, x1, yb, yt = -1.7, 6.3, -2.4, 2.6
        ejes = VGroup(Line([x0, yb, 0], [x1, yb, 0], color=C_EJE, stroke_width=2.5),
                      Line([x0, yb, 0], [x0, yt, 0], color=C_EJE, stroke_width=2.5))
        rng = np.random.default_rng(3)
        n = 90
        ruido = rng.normal(0, 1, n)
        ruido = np.clip(ruido, -2.2, 2.2) * 0.1
        tendencia = 0.18 * np.sin(np.linspace(0, 4.2 * np.pi, n))
        base = 0.1
        serie = base + tendencia + ruido
        k_an = 66
        sigma = 0.2
        media = base
        serie[k_an] = media + 5.2 * sigma
        xs = np.linspace(x0 + 0.2, x1 - 0.2, n)
        ymed = 0.0
        esc = 2.9

        def Y(v):
            return ymed + (v - media) * esc

        banda_s, banda_i = Y(media + 3 * sigma), Y(media - 3 * sigma)
        banda = Polygon([x0, banda_s, 0], [x1, banda_s, 0], [x1, banda_i, 0], [x0, banda_i, 0],
                        color=C_ANT, stroke_width=0, fill_color=C_ANT, fill_opacity=0.14)
        l_s = DashedLine([x0, banda_s, 0], [x1, banda_s, 0], color=C_ANT, stroke_width=2, dash_length=0.14)
        l_i = DashedLine([x0, banda_i, 0], [x1, banda_i, 0], color=C_ANT, stroke_width=2, dash_length=0.14)
        l_m = Line([x0, Y(media), 0], [x1, Y(media), 0], color=C_EJE, stroke_width=1.5)
        t_band = et("±3σ", 22, C_ANT).move_to([x1 - 0.35, banda_s + 0.3, 0])

        pts = np.array([[x, Y(v), 0] for x, v in zip(xs, serie)])
        traza = VMobject().set_points_as_corners(pts).set_stroke(C_OK, 3.5)
        punto = Dot(pts[k_an], radius=0.12, color=C_MAL)
        anillo = Circle(radius=0.3, color=C_MAL, stroke_width=3).move_to(pts[k_an])
        t_an = et("Anomalía", 24, C_MAL).next_to(anillo, LEFT, buff=0.2)
        t_an.shift(UP * 0.1)
        t_tel = et("Telemetría", 22, TENUE).next_to(ejes[0], DOWN, buff=0.18).align_to(ejes[0], RIGHT)

        # rail: de la Pi a la gráfica
        rail = flecha(pi.get_right() + RIGHT * 0.15, np.array([x0 - 0.2, 0.1, 0]), C_OK)
        pq = VGroup(*[Rectangle(width=0.2, height=0.14, color=C_SAT, fill_color=C_SAT, fill_opacity=0.9,
                                stroke_width=0) for _ in range(3)])
        pq.arrange(RIGHT, buff=0.12).move_to(rail.get_center() + UP * 0.28)

        self.play(FadeIn(pi, scale=0.85), FadeIn(etq_pi), run_time=1.2)
        self.play(Create(ejes), FadeIn(banda), Create(l_s), Create(l_i), Create(l_m), FadeIn(t_band), run_time=1.3)
        self.play(GrowArrow(rail), FadeIn(pq, lag_ratio=0.3), run_time=0.8)
        self.play(Create(traza, rate_func=linear), run_time=3.2)
        self.play(FadeIn(punto, scale=2.5), Create(anillo), FadeIn(t_an), FadeIn(t_tel), run_time=0.9)
        self.play(Indicate(punto, color=C_MAL, scale_factor=1.6), run_time=0.8)
        self.wait(3.0)
        self.cierre()


# ===================================================================
#  4. Un pase, cinco plataformas
# ===================================================================
class UnPaseCincoPlataformas(Pieza):
    def construct(self):
        horizonte_y = 0.6
        suelo = Line([-6.4, horizonte_y, 0], [6.4, horizonte_y, 0], color=C_EJE, stroke_width=2.5)
        est = estacion(0.8, C_ANT).move_to([0, horizonte_y + 0.5, 0])
        # trayectoria del pase: arco sobre la estación
        arco = ArcBetweenPoints([-5.8, horizonte_y + 0.9, 0], [5.8, horizonte_y + 0.9, 0], angle=-1.05,
                                color=C_CIELO, stroke_width=2.5, stroke_opacity=0.9)
        arco_p = DashedVMobject(arco, num_dashes=40, dashed_ratio=0.55)
        sat = satelite(0.34, C_SAT)
        t_aos = et("AOS", 20, TENUE).move_to([-5.8, horizonte_y + 0.45, 0])
        t_los = et("LOS", 20, TENUE).move_to([5.8, horizonte_y + 0.45, 0])
        sat.move_to(arco.point_from_proportion(0.5))
        haz1 = haz(est.get_top() + UP * 0.1, sat.get_bottom() + DOWN * 0.08, C_ANT, 2.5)
        cono = Polygon(est.get_top() + UP * 0.15, sat.get_bottom() + DL * 0.9, sat.get_bottom() + DR * 0.9,
                       color=C_ANT, stroke_width=0, fill_color=C_ANT, fill_opacity=0.1)

        # cadena de 5 etapas
        nombres = ["Rastreo", "Recepción", "Clasificación", "Bus", "Gemelo"]
        cols = [C_ANT, C_ANT, C_CIELO, C_OK, C_SAT]
        W, H, G = 2.25, 1.45, 0.38
        x_ini = -(5 * W + 4 * G) / 2 + W / 2
        y_c = -1.75
        etapas = VGroup()
        for i, (nm, col) in enumerate(zip(nombres, cols)):
            r = RoundedRectangle(corner_radius=0.16, width=W, height=H, color=col, fill_color=col,
                                 fill_opacity=0.14, stroke_width=3)
            t = et(nm, 22, TINTA).move_to(r.get_bottom() + UP * 0.32)
            c = r.get_center() + UP * 0.28
            if i == 0:   # rastreo: retícula y punto
                ic = VGroup(Circle(radius=0.27, color=col, stroke_width=2.4),
                            Line(c + LEFT * 0.38, c + RIGHT * 0.38, color=col, stroke_width=2),
                            Line(c + DOWN * 0.38, c + UP * 0.38, color=col, stroke_width=2),
                            Dot(c + UR * 0.12, radius=0.06, color=C_SAT))
                ic.scale(0.8).move_to(c)
            elif i == 1:  # recepción: ondas
                ic = VGroup(Dot(ORIGIN, radius=0.06, color=col),
                            *[Arc(radius=0.14 + 0.13 * k, start_angle=-0.7, angle=1.4, color=col, stroke_width=2.6)
                              for k in range(3)])
                ic.move_to(c)
            elif i == 2:  # clasificación: capas de CNN
                ic = VGroup(*[Rectangle(width=0.13, height=h, color=col, fill_color=col, fill_opacity=0.55,
                                        stroke_width=1.5) for h in (0.5, 0.36, 0.24)])
                ic.arrange(RIGHT, buff=0.08).move_to(c)
            elif i == 3:  # bus: sobre firmado
                ic = sobre(0.46, C_SAT).move_to(c)
            else:         # gemelo: esfera con órbita
                ic = VGroup(Circle(radius=0.2, color=col, fill_color=col, fill_opacity=0.3, stroke_width=2.2),
                            Ellipse(width=0.74, height=0.28, color=col, stroke_width=1.8)).move_to(c)
            etapas.add(VGroup(r, ic, t).move_to([x_ini + i * (W + G), y_c, 0]))
        flechas = VGroup(*[flecha(etapas[i][0].get_right() + RIGHT * 0.02, etapas[i + 1][0].get_left() + LEFT * 0.02,
                                  TENUE, 3.5, 0.17) for i in range(4)])
        # bajada de la estación a la cadena
        bajada = DashedLine(est.get_bottom() + DOWN * 0.04, [0, y_c + H / 2 + 0.05, 0], color=C_EJE, stroke_width=2)
        bajada.set_opacity(0.0)

        self.play(Create(suelo), FadeIn(est, scale=0.8), FadeIn(t_aos), FadeIn(t_los), run_time=1.0)
        sat.move_to(arco.point_from_proportion(0.0))
        self.add(arco_p)
        self.play(FadeIn(sat), run_time=0.4)
        self.play(UpdateFromAlphaFunc(sat, lambda m, a: m.move_to(arco.point_from_proportion(0.5 * a)), rate_func=linear), run_time=2.0)
        # estado final del pase: satélite sobre la estación con haz
        self.play(FadeIn(haz1), FadeIn(cono), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in etapas], lag_ratio=0.2),
                  LaggedStart(*[GrowArrow(f) for f in flechas], lag_ratio=0.2), run_time=2.4)
        # un pulso recorre la cadena
        pul = Dot(etapas[0].get_left() + LEFT * 0.0, radius=0.09, color=C_SAT).move_to(etapas[0][0].get_top() + UP * 0.12)
        self.add(pul)
        for i in range(1, 5):
            self.play(pul.animate.move_to(etapas[i][0].get_top() + UP * 0.12), run_time=0.45)
        self.play(FadeOut(pul), run_time=0.2)
        self.wait(3.0)
        self.cierre()

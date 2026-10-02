import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from scipy.ndimage import gaussian_filter

from marca_aerospace import AMBAR, CIAN, FONDO, PLATA, PLATA_MEDIA, LogoCoDe
from marca_vertical import _texto, bloque, fondo_reel, marco
from reels_promo import (Reloj, cabecera, chip, leyenda, linea_ciclica, polilinea, suave, ventana)
from rotulos_aerospace import TENUE

# Reels promocionales de Co.De Aerospace en LOOP PERFECTO (9:16). Cada uno es una función periódica del
# reloj: el último cuadro empalma con el primero. Las tecnologías y cifras salen de
# codeaerospace.com/plataformas (consultado 2026-10-01). Ver reels_promo.py.

LINEA = "#2A3742"


# ══ 1 · La cascada (CO.DE Orbit Eye) ══════════════════════════════════════════════════════════════

T1 = 12.0
K1, WC1 = 960, 540            # filas por periodo (80 filas/s) y columnas de frecuencia


def doppler_d(tau, T=T1):
    """Desplazamiento Doppler (fracción del ancho): + al acercarse, − al alejarse (la «S»)."""
    return -0.27 * np.tanh((tau - T / 2) / (0.11 * T))


def doppler_amp(tau, T=T1):
    """Intensidad de la portadora: máxima al cenit del pase, casi nula en los extremos (empalme)."""
    return np.exp(-((tau - T / 2) / (0.27 * T)) ** 2)


def tabla_cascada(T=T1, K=K1, Wc=WC1):
    rng = np.random.default_rng(5)
    tab = np.abs(0.12 + 0.075 * rng.standard_normal((K, Wc)))
    x = np.linspace(0, 1, Wc)
    tau = np.arange(K) / K * T
    for xs, a in ((0.12, .20), (0.83, .16), (0.31, .09)):                  # espurias fijas
        tab += a * np.exp(-((x - xs) / 0.0025) ** 2)[None, :] * (0.6 + 0.4 * rng.random((K, 1)))
    amp, cx = doppler_amp(tau, T), 0.5 + doppler_d(tau, T)
    g = lambda c, w: np.exp(-((x[None, :] - c[:, None]) / w) ** 2)
    tab += amp[:, None] * g(cx, 0.0042)
    for off, a in ((-0.035, .26), (0.035, .26), (-0.07, .11), (0.07, .11)):  # bandas laterales
        tab += a * amp[:, None] * g(cx + off, 0.003)
    s = K / T
    for k in range(8):                                                       # ráfagas FSK de dos tonos
        r0 = int((0.17 + 0.085 * k) * K)
        bit = 0
        for r in range(r0, min(r0 + int(0.32 * s), K)):
            if r % 4 == 0:
                bit = rng.integers(0, 2)
            tab[r] += 0.85 * amp[r] * g(np.array([cx[r] + (0.05 if bit else 0.064)]), 0.0032)[0]
    tab = gaussian_filter(tab, (0.7, 0.9), mode=("wrap", "nearest"))
    return np.clip(tab / 1.0, 0, 1)


def paleta():
    stops = [(0.0, (8, 15, 21)), (0.22, (10, 44, 74)), (0.5, (0, 140, 190)), (0.78, (0, 217, 255)), (1.0, (242, 243, 244))]
    xs = np.linspace(0, 1, 256)
    return np.stack([np.interp(xs, [s[0] for s in stops], [s[1][c] for s in stops]) for c in range(3)], 1).astype(np.uint8)


class ReelOrbitEye(Scene):
    """Cascada de espectro con la S del Doppler que fluye sin fin; un VFO la sigue (≈12 s, loop)."""

    def construct(self):
        self.camera.background_color = FONDO
        W, H = marco(self)
        reloj = Reloj(self, T1)
        fondo_reel(self, entrada=False, periodo=T1)
        tab, lut = tabla_cascada(), paleta()
        K, s = K1, K1 / T1
        PT, PB = 4.7, -5.0
        alfa = np.ones((K, 1, 1))
        alfa[int(K * 0.86):, 0, 0] = np.linspace(1, 0, K - int(K * 0.86)) ** 1.5

        def fotograma(t):
            pos = s * t
            i0 = int(np.floor(pos)); f = pos - i0
            idx = (i0 - np.arange(K)) % K
            img = ((1 - f) * tab[idx] + f * tab[(idx + 1) % K]) ** 0.85
            rgb = lut[(img * 255).astype(np.uint8)]
            return np.concatenate([rgb, (alfa * 255 * np.ones((K, WC1, 1))).astype(np.uint8)], 2)

        panel = ImageMobject(fotograma(0.0))
        panel.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
        panel.stretch_to_fit_width(W).stretch_to_fit_height(PT - PB).move_to([0, (PT + PB) / 2, 0]).set_z_index(5)
        panel.add_updater(lambda m: setattr(m, "pixel_array", fotograma(reloj.t)))
        self.add(panel)

        # Espectro instantáneo (FFT) sobre la fila más nueva, con su halo.
        xs = np.linspace(-W / 2, W / 2, WC1 // 2)
        pico = polilinea([[0, 0, 0], [1, 0, 0]], color=CIAN, width=3.4).set_z_index(8)
        halo = polilinea([[0, 0, 0], [1, 0, 0]], color=CIAN, width=11, opacity=0.2).set_z_index(7)

        def espectro(m):
            i0 = int(np.floor(s * reloj.t)) % K
            ys = PT + 1.15 * tab[i0][::2]
            pts = np.column_stack([xs, ys, np.zeros_like(xs)])
            pico.set_points_as_corners(pts)
            halo.set_points_as_corners(pts)
        pico.add_updater(espectro)
        self.add(halo, pico)

        # VFO: marco que se engancha a la portadora (solo durante el pase).
        vfo = VGroup(Rectangle(width=0.95, height=0.62, stroke_width=4, stroke_color=CIAN),
                     _texto("VFO", 24, "SEMIBOLD", CIAN)).set_z_index(9)
        vfo[1].next_to(vfo[0], UP, buff=0.12)

        def seguir(m):
            tau = reloj.t % T1
            a = doppler_amp(tau)
            m.move_to([-W / 2 + (0.5 + doppler_d(tau)) * W, PT - 0.42, 0])
            m.set_opacity(min(1.0, a * 2.6))
        vfo.add_updater(seguir)
        self.add(vfo)

        cab = cabecera(self, "CO.DE Orbit Eye", "Estación terrena\ndefinida por software")
        etiquetas = [
            ("El Doppler dibuja una S", "Rastreo SGP4 y corrección por Hamlib"),
            ("FFT y cascada en vivo", "Varios VFO por receptor, cada uno demodula"),
            ("Siete decodificadores", "SSTV · AFSK · FSK · GFSK · GMSK · BPSK · Morse"),
            ("Graba y reproduce IQ", "Formato SigMF · TLE de CelesTrak y TinyGS"),
        ]
        for i, (g, p) in enumerate(etiquetas):
            leyenda(self, reloj, g, p, 3 * i - 1.5, 3 * i + 1.5, -6.45, f=0.35, tam_p=31)
        c = chip("Demo con grabación IQ", CIAN, 24)
        c.move_to([-W / 2 + c.width / 2 + 0.55, PB + 0.55, 0])
        self.add(c)
        self.wait(T1)


# ══ 2 · ¿0.1° alcanza? (ATP-DT) ═══════════════════════════════════════════════════════════════════

T2 = 12.0
CONTROLADORES = [("PD", 11.5, 2.2, "Reacciona rápido al error", 1.35),
                 ("PID", 2.2, 4.4, "Acumula el error pasado", 0.95),
                 ("LQR", 4.4, 6.6, "Minimiza un costo óptimo", 0.50),
                 ("H∞", 6.6, 8.8, "Robusto a las perturbaciones", 0.30),
                 ("Lazo abierto", 8.8, 11.0, "Sin realimentación: la referencia", 0.0)]


def error_banda(t, T=T2):
    """Error de apuntamiento ILUSTRATIVO en unidades de la banda (1 = ±0.1°). Periódico en T."""
    w = 2 * np.pi * t / T
    base = (1.0 * np.sin(5 * w + 0.3) + 0.6 * np.sin(11 * w + 1.7) + 0.4 * np.sin(17 * w + 4.1)) / 1.35
    e = 0.0
    for nombre, a, b, _, amp in CONTROLADORES:
        wc = ventana(t % T, a, b, 0.5, T)
        e += wc * (amp * base if nombre != "Lazo abierto" else 2.2 * np.sin(w + 0.8) + 0.4 * base)
    return e


class ReelATP(Scene):
    """Una antena persigue al satélite mientras cinco controladores pelean por la banda de ±0.1° (≈12 s)."""

    def construct(self):
        self.camera.background_color = FONDO
        W, H = marco(self)
        reloj = Reloj(self, T2, desfase=4.0)
        fondo_reel(self, entrada=False, periodo=T2)
        cabecera(self, "CO.DE ATP-DT · gemelo digital", "¿Puede una antena\napuntar a 0.1°?")

        P = np.array([0.0, 0.1, 0.0])
        pos = lambda th: P + np.array([5.6 * np.cos(th), 4.4 * np.sin(th), 0])
        d2r = np.pi / 180
        # Cielo: horizonte, máscara de elevación de 15° y la traza del pase (AOS → LOS).
        suelo = Line([-W / 2 + 0.5, P[1], 0], [W / 2 - 0.5, P[1], 0], stroke_width=3, color=TENUE).set_opacity(0.6)
        mascara = VGroup(*[DashedLine(P, pos(a * d2r), stroke_width=2, color=TENUE, dash_length=0.18).set_opacity(0.45)
                           for a in (15, 165)])
        ths = np.linspace(165 * d2r, 15 * d2r, 90)
        traza = DashedVMobject(polilinea([pos(a) for a in ths], color=CIAN, width=3, opacity=0.5), num_dashes=46)
        pedestal = VGroup(Line(P, P + DOWN * 0.95, stroke_width=9, color=PLATA_MEDIA),
                          Rectangle(width=1.5, height=0.2, stroke_width=0, fill_color=PLATA_MEDIA, fill_opacity=1)
                          .move_to(P + DOWN * 1.05))
        eje = Dot(P, radius=0.17, color=CIAN).set_z_index(12)
        etq = _texto("Montura de 2 GDL · SGP4 → acimut/elevación", 24, "MEDIUM", TENUE, ancho_max=W * 0.6)
        etq.move_to([-W / 2 + etq.width / 2 + 0.55, 3.95, 0])
        self.add(suelo, mascara, traza, pedestal, eje, etq)

        sat = LogoCoDe(altura=8, aerospace=False).satelite.copy()
        sat.scale_to_fit_width(1.7).set_z_index(11)
        plato = VMobject().set_z_index(10)
        antena = VGroup(plato, Line(ORIGIN, ORIGIN), Line(ORIGIN, ORIGIN), Dot(radius=0.1, color=CIAN)).set_z_index(10)
        haz = VMobject().set_z_index(6)
        self.add(haz, antena, sat)

        def theta(t):
            if t < 11:
                return (165 - 150 * t / 11) * d2r
            return (15 + 150 * suave(t - 11)) * d2r

        def actualizar_antena(_m):
            t = reloj.t % T2
            th = theta(t)
            v = pos(th) - P
            ang = np.arctan2(v[1], v[0]) + (error_banda(reloj.t) * 2.5) * d2r
            u, n = np.array([np.cos(ang), np.sin(ang), 0]), np.array([-np.sin(ang), np.cos(ang), 0])
            s_ = np.linspace(-1, 1, 36)
            borde = [P - u * 0.3 + u * 0.8 * k * k + n * 1.65 * k for k in s_]
            plato.set_points_as_corners(borde).set_stroke(color=PLATA[0], width=7).set_fill(opacity=0)
            feed = P - u * 0.3 + u * 1.65
            antena[1].put_start_and_end_on(borde[0], feed).set_stroke(color=PLATA_MEDIA, width=2.5)
            antena[2].put_start_and_end_on(borde[-1], feed).set_stroke(color=PLATA_MEDIA, width=2.5)
            antena[3].move_to(feed)
            op = suave(t / 0.6) * (1 - suave((t - 10.4) / 0.6)) if t < 11 else 0.0
            sat.move_to(pos(th))
            sat.set_opacity(op)
            sat.set_z_index(11)
            if op > 0.02:
                sp, nn = pos(th), np.array([-np.sin(ang), np.cos(ang), 0])
                haz.set_points_as_corners([feed, sp + nn * 0.45, sp - nn * 0.45, feed])
                haz.set_stroke(width=0).set_fill(color=CIAN, opacity=0.13 * op)
            else:
                haz.set_fill(opacity=0).set_stroke(opacity=0)
        antena.add_updater(actualizar_antena)
        self.add(antena)

        # Osciloscopio de error con la banda de ±0.1°.
        SX0, SX1, SC, ESC = -W / 2 + 0.6, W / 2 - 0.6, -3.7, 0.55
        marco_s = Rectangle(width=SX1 - SX0, height=3.4, stroke_width=2.2, stroke_color=LINEA, fill_color=FONDO,
                            fill_opacity=0.65).move_to([(SX0 + SX1) / 2, SC, 0]).set_z_index(3)
        banda = Rectangle(width=SX1 - SX0, height=2 * ESC, stroke_width=0, fill_color=CIAN, fill_opacity=0.13)
        banda.move_to([(SX0 + SX1) / 2, SC, 0]).set_z_index(4)
        bordes = VGroup(*[DashedLine([SX0, SC + sg * ESC, 0], [SX1, SC + sg * ESC, 0], stroke_width=2.4, color=CIAN,
                                     dash_length=0.2).set_opacity(0.8) for sg in (-1, 1)]).set_z_index(4)
        cero = Line([SX0, SC, 0], [SX1, SC, 0], stroke_width=1.5, color=TENUE).set_opacity(0.4).set_z_index(4)
        l1 = _texto("±0.1°", 28, "SEMIBOLD", CIAN).move_to([SX0 + 0.75, SC + ESC + 0.34, 0]).set_z_index(6)
        l2 = _texto("ERROR DE APUNTAMIENTO", 24, "MEDIUM", TENUE).set_z_index(6)
        l2.move_to([SX0 + l2.width / 2, -1.55, 0])
        c = chip("Trazas ilustrativas", AMBAR, 22)
        c.move_to([SX1 - c.width / 2, -1.55, 0])
        self.add(marco_s, banda, bordes, cero, l1, l2, c)

        VENT = 4.0
        traza_ok = polilinea([[0, 0, 0], [1, 0, 0]], color=CIAN, width=5).set_z_index(8)
        traza_mal = VMobject().set_z_index(9)

        def osciloscopio(_m):
            ts = reloj.t - VENT + np.linspace(0, VENT, 220)
            e = np.array([error_banda(v) for v in ts])
            x = SX0 + (ts - ts[0]) / VENT * (SX1 - SX0)
            y = SC + np.clip(e, -3.0, 3.0) * ESC
            traza_ok.set_points_as_corners(np.column_stack([x, y, np.zeros_like(x)]))
            fuera = np.abs(e) > 1.0
            traza_mal.clear_points()
            i = 0
            while i < len(e):
                if fuera[i]:
                    j = i
                    while j + 1 < len(e) and fuera[j + 1]:
                        j += 1
                    seg = np.column_stack([x[i:j + 1], y[i:j + 1], np.zeros(j - i + 1)])
                    if len(seg) > 1:
                        traza_mal.start_new_path(seg[0])
                        traza_mal.add_points_as_corners(seg[1:])
                    i = j + 1
                else:
                    i += 1
            traza_mal.set_stroke(color=AMBAR, width=5.5).set_fill(opacity=0)
        traza_ok.add_updater(osciloscopio)
        self.add(traza_ok, traza_mal)

        # Chips de controlador y su explicación.
        chips = VGroup()
        for nombre, *_ in CONTROLADORES:
            t = _texto(nombre, 30, "SEMIBOLD", TENUE)
            caja = RoundedRectangle(corner_radius=0.25, width=max(t.width + 0.7, 1.6), height=0.78, stroke_width=2.6,
                                    stroke_color=LINEA, fill_color=CIAN, fill_opacity=0)
            t.move_to(caja)
            chips.add(VGroup(caja, t))
        chips.arrange(RIGHT, buff=0.22)
        if chips.width > W - 1.2:
            chips.scale_to_fit_width(W - 1.2)
        chips.move_to([0, -6.1, 0]).set_z_index(25)

        def iluminar(_m):
            for ch, (nombre, a, b, *_r) in zip(chips, CONTROLADORES):
                w = ventana(reloj.t, a, b, 0.5, T2)
                ch[0].set_fill(color=CIAN, opacity=0.95 * w)
                ch[0].set_stroke(color=interpolate_color(ManimColor(LINEA), ManimColor(CIAN), w))
                ch[1].set_fill(color=interpolate_color(ManimColor(TENUE), ManimColor(FONDO), suave((w - 0.3) / 0.4)))
        chips.add_updater(iluminar)
        self.add(chips)
        for nombre, a, b, texto, _ in CONTROLADORES:
            linea_ciclica(self, reloj, texto, a, b, -7.05, f=0.35, tam=44)
        self.wait(T2)


# ══ 7 · El modelo se financia solo (CO.DE Strategy → Aerospace → Plataformas) ══════════════════════

T7 = 12.0


class ReelModelo(Scene):
    """Tres nodos en anillo y un pulso que los recorre: el ciclo es el modelo de negocio (≈12 s)."""

    def construct(self):
        self.camera.background_color = FONDO
        W, H = marco(self)
        reloj = Reloj(self, T7)
        fondo_reel(self, entrada=False, periodo=T7)
        cabecera(self, "El modelo CO.DE", "Cada proyecto digital\nfinancia investigación\naeroespacial", n=20, tam=84)

        C, R = np.array([0.0, -2.3, 0.0]), 4.3
        d2r = np.pi / 180
        en_anillo = lambda ang: C + R * np.array([np.cos(ang), np.sin(ang), 0])
        anillo = Circle(radius=R, stroke_width=3.5, color=CIAN).set_fill(opacity=0).set_stroke(opacity=0.3).move_to(C).set_z_index(2)
        emblema = LogoCoDe(altura=3.1, aerospace=False, contorno=True).move_to(C).set_z_index(3)
        self.add(anillo, emblema)

        datos = [("CO.DE Strategy", "Proyectos digitales", 90),
                 ("CO.DE Aerospace", "Investigación espacial", -30),
                 ("Plataformas", "En línea, no maquetas", 210)]
        nodos = VGroup()
        for tit, sub, ang in datos:
            caja = RoundedRectangle(corner_radius=0.35, width=5.5, height=1.95, stroke_width=3, stroke_color=LINEA,
                                    fill_color=FONDO, fill_opacity=0.88)
            a = _texto(tit, 44, "SEMIBOLD", PLATA[0], ancho_max=5.0)
            b = _texto(sub, 30, "NORMAL", TENUE, ancho_max=5.0)
            VGroup(a, b).arrange(DOWN, buff=0.18).move_to(caja)
            g = VGroup(caja, a, b).move_to(en_anillo(ang * d2r)).set_z_index(10)
            nodos.add(g)

        def encender(_m):
            for i, g in enumerate(nodos):
                w = ventana(reloj.t, 4 * i - 2, 4 * i + 2, 0.6, T7)
                g[0].set_stroke(color=interpolate_color(ManimColor(LINEA), ManimColor(CIAN), w), width=3 + 4 * w)
                g[0].set_fill(color=interpolate_color(ManimColor(FONDO), ManimColor("#0B3A4A"), w), opacity=0.92)
        nodos.add_updater(encender)
        self.add(nodos)

        for txt, ang in (("financian", 30), ("construye", 270), ("demuestran", 150)):
            e = _texto(txt, 34, "MEDIUM", CIAN, ancho_max=3.4).set_opacity(0.85).set_z_index(6)
            e.move_to(C + 3.15 * np.array([np.cos(ang * d2r), np.sin(ang * d2r), 0]))
            self.add(e)

        # Pulso con estela dando la vuelta al anillo (sentido horario): llega a cada nodo cada 4 s.
        cola = VGroup(*[Dot(radius=0.2 * (1 - k / 16) + 0.04, color=CIAN) for k in range(16)]).set_z_index(9)

        def pulso(m):
            th = (90 - 360 * reloj.t / T7) * d2r
            for k, d in enumerate(m):
                d.move_to(en_anillo(th + k * 0.075))
                d.set_opacity((1 - k / 16) ** 1.6)
        cola.add_updater(pulso)
        self.add(cola)

        textos = [("Proyectos digitales a la medida", "Web · IA agéntica · Apps · RV · IoT"),
                  ("Investigación espacial real", "Constelaciones NGSO · espectro · WRC-27"),
                  ("Plataformas en línea, no maquetas", "Estación terrena · gemelos digitales · IA")]
        for i, (g, p) in enumerate(textos):
            leyenda(self, reloj, g, p, 4 * i - 2, 4 * i + 2, -6.75, f=0.35, tam_g=52, tam_p=32)
        self.wait(T7)

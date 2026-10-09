import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *

import datos_el as DL
from estilo_reel import Viva, cerrar_serie, cola, leyenda, punto, preparar_serie, texto
from reels_promo import polilinea, suave

# SERIE «ELECTRÓNICA ESPACIAL» — qué le pasa a la electrónica en órbita y cómo se defiende: radiación (bit volteado, latch-up,
# dosis), protección (voto triple, código de Hamming), energía (panel, batería en eclipse), calor sin aire, enlace de bajada y
# computadoras de vuelo. Cuentas de electronica_espacio.py (supuestos en datos_el.py y en el ⚠️ de los pies); sin mediciones propias.
# Tema ELECTRÓNICA con fondo vertical propio (fondos_reel.electronica: canto de una placa con conector, pistas y un chip).
# Formato película: título → cuerpo → logo → loop. Pocas cifras, cada una con una comparación cotidiana.

FIN = 3.0
KICKER = "Electrónica espacial"
SERIE = dict(tema="electronica", fondo="reel")
ROJO, AZUL, CELDA = "#FF5A5F", "#3B8FD9", "#1B2C6B"


def leyendas(escena, est, pel, nombre, textos):
    ts = list(DL.LEYENDAS[nombre]) + [DL.CUERPO[nombre] + FIN]
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
    """Opacidad = f() en cada cuadro."""
    m.add_updater(lambda x: fundir(x, f()))
    fundir(m, f())
    return m


def aparece(m, pel, t0, d=0.6, hasta=None):
    return vive(m, lambda: rampa(pel.t, t0, d) * ((1 - rampa(pel.t, hasta, d)) if hasta else 1))


def zona(p):
    return float(-5.6 < p[1] < 5.3 and -7.0 < p[0] < 7.0)


def caja(est, w, h, color, op=0.85, borde=3):
    return RoundedRectangle(corner_radius=0.18, width=w, height=h).set_fill(est.fondo, op).set_stroke(color, borde)


def chip_ic(est, c, lado, color, patas=6):
    """Chip QFP visto desde arriba: cuerpo negro, patas de cobre en los cuatro lados y la marca del pin 1."""
    g = VGroup()
    paso = lado / (patas + 1)
    for k in range(patas):
        u = -lado / 2 + paso * (k + 1)
        for a, b in (([u, lado / 2, 0], [u, lado / 2 + 0.22, 0]), ([u, -lado / 2, 0], [u, -lado / 2 - 0.22, 0]),
                     ([lado / 2, u, 0], [lado / 2 + 0.22, u, 0]), ([-lado / 2, u, 0], [-lado / 2 - 0.22, u, 0])):
            g.add(Line(a, b, stroke_width=5, color="#E0A84A"))
    g.add(Square(lado).set_fill("#111614", 1).set_stroke(color, 2.5))
    g.add(Dot([-lado / 2 + 0.25, lado / 2 - 0.25, 0], radius=0.07, color="#3A4540"))
    return g.move_to(c)


def marca_ok(c, color, s=0.35):
    return polilinea([c + np.array([-s, 0, 0]), c + np.array([-0.3 * s, -0.7 * s, 0]), c + np.array([s, 0.8 * s, 0])],
                     color=color, width=8)


def marca_mal(c, color, s=0.32):
    return VGroup(Line(c + np.array([-s, -s, 0]), c + np.array([s, s, 0]), stroke_width=8, color=color),
                  Line(c + np.array([-s, s, 0]), c + np.array([s, -s, 0]), stroke_width=8, color=color))


def ion(escena, est, pel, blanco, t_golpe, dire=(1.0, -0.75), largo=9.0, dur=1.0, color=None):
    """Partícula que cruza la pantalla en línea recta y pasa por `blanco` en t_golpe (con estela)."""
    color = color or ROJO
    d = np.array([*dire, 0.0]); d /= np.linalg.norm(d)
    b = np.asarray(blanco, float)
    p = punto(color, 0.11).set_z_index(20)

    def mover(m):
        u = (pel.t - t_golpe) / dur
        m.move_to(b + d * largo * u)
        fundir(m, float(-1 < u < 1) * zona(m.get_center()) * min(1.0, (1 - abs(u)) / 0.15))
    p.add_updater(mover)
    mover(p)
    escena.add(p)
    cola(escena, p, color, n=22, ancho=7.0, z=19)
    return p


def destello(c, color, r=0.9):
    return VGroup(Circle(radius=r).set_fill(color, 0.35).set_stroke(width=0),
                  Circle(radius=r * 0.45).set_fill(color, 0.7).set_stroke(width=0)).move_to(c).set_z_index(18)


def pulso(pel, t0, ancho=0.5):
    return lambda: max(0.0, 1 - abs(pel.t - t0) / ancho)


# ══ 1 · Un rayo cósmico cambia un 0 por un 1 (SEU) ═════════════════════════════════════════════════════════════════════

class ReelELBit(Scene):
    VAR = 0

    def construct(self):
        n = "ReelELBit"; TB = DL.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Un rayo cósmico\ncambia un 0 por un 1", self.VAR, chip_txt="Ilustración", **SERIE)
        cols, filas, d = 8, 5, 1.55
        x0, y0 = -(cols - 1) / 2 * d, 4.45
        bits = np.random.default_rng(3).integers(0, 2, (filas, cols))
        golpes = {(2, 5): 3.2, (3, 1): 15.0}
        bits[2, 5], bits[3, 1] = 0, 1
        for i in range(filas):
            for j in range(cols):
                c = np.array([x0 + j * d, y0 - i * d, 0])
                self.add(aparece(caja(est, d * 0.86, d * 0.86, est.acento, 0.85, 2.5).move_to(c).set_z_index(6), pel, 0.2 + 0.03 * (i * cols + j), 0.5))
                v = int(bits[i, j])
                antes = texto(est, str(v), 50, est.tinta, "cifra", "BOLD").move_to(c).set_z_index(7)
                if (i, j) not in golpes:
                    self.add(aparece(antes, pel, 0.4 + 0.03 * (i * cols + j), 0.5))
                    continue
                tg = golpes[(i, j)]
                despues = texto(est, str(1 - v), 50, ROJO, "cifra", "BOLD").move_to(c).set_z_index(7)
                self.add(vive(antes, lambda tg=tg, k=i * cols + j: rampa(pel.t, 0.4 + 0.03 * k, 0.5) * (1 - rampa(pel.t, tg + 0.05, 0.2))))
                self.add(vive(despues, lambda tg=tg: rampa(pel.t, tg + 0.05, 0.2)))
                marco = Square(d * 0.86).set_fill(ROJO, 0.12).set_stroke(ROJO, 5).move_to(c).set_z_index(6)
                self.add(vive(marco, lambda tg=tg: rampa(pel.t, tg, 0.2)))
                self.add(vive(destello(c, ROJO, 1.0), pulso(pel, tg + 0.1, 0.6)))
                ion(self, est, pel, c, tg, dire=(1.0, -0.8 if j > 3 else 0.9), largo=10.0, dur=1.2)
        # cuánta carga deja el ion vs. cuánta voltea un bit (escala lineal: la segunda casi no se ve)
        L = 12.8
        filas_c = [("lo que deja el ion", est.calido, 1.0, -3.05), ("lo que basta para voltear un bit", est.acento, 1 / DL.VECES_BIT, -4.45)]
        for k, (txt, col, frac, y) in enumerate(filas_c):
            t0 = 7.0 + 1.2 * k
            self.add(aparece(texto(est, txt, 42, est.tinta, ancho_max=12.6).next_to([-6.4, y, 0], RIGHT, buff=0).set_z_index(9), pel, t0, hasta=12.4))
            barra = Rectangle(width=L, height=0.5).set_fill(col, 0.9).set_stroke(width=0).set_z_index(9)
            barra.add_updater(lambda m, t0=t0, frac=frac, y=y: m.stretch_to_fit_width(max(L * frac * rampa(pel.t, t0 + 0.2, 1.4), 0.04)).move_to([-6.4, y - 0.75, 0], aligned_edge=LEFT))
            self.add(aparece(barra, pel, t0, 0.3, hasta=12.4))
        self.add(aparece(texto(est, "× 100", 72, est.calido, "cifra", "BOLD").move_to([4.6, -5.0, 0]).set_z_index(9), pel, 10.0, hasta=12.4))
        self.add(aparece(VGroup(texto(est, "el chip sigue sano", 50, est.acento, "titulo", "SEMIBOLD"),
                                texto(est, "pero el dato quedó mal", 50, ROJO, "titulo", "SEMIBOLD")).arrange(DOWN, buff=0.35)
                         .move_to([0, -3.9, 0]).set_z_index(9), pel, 13.2))
        leyendas(self, est, pel, n, [
            ("Una partícula del espacio cruza un chip", "rayos cósmicos y partículas del Sol"),
            ("Deja una chispa de carga eléctrica", "unas 100 veces lo que basta para voltear un bit"),
            ("No rompe el chip: cambia un dato", "y pasa una y otra vez en órbita")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 2 · Tres computadoras que votan (TMR) ══════════════════════════════════════════════════════════════════════════════

class ReelELVoto(Scene):
    VAR = 1

    def construct(self):
        n = "ReelELVoto"; TB = DL.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Tres computadoras\nque votan", self.VAR, chip_txt="Ilustración", **SERIE)
        xs, yb, yv = (-4.6, 0.0, 4.6), 3.3, -0.5
        T_ION, T_SANA = 7.0, 13.6
        votante = VGroup(caja(est, 5.4, 2.5, est.calido, 0.9, 4), texto(est, "voto", 44, est.calido, "titulo", "SEMIBOLD").move_to([0, yv + 0.62, 0]))
        votante[0].move_to([0, yv, 0])
        self.add(aparece(votante.set_z_index(8), pel, 1.6))
        self.add(aparece(texto(est, "7", 80, est.tinta, "cifra", "BOLD").move_to([0, yv - 0.4, 0]).set_z_index(9), pel, 2.6))
        for k, x in enumerate(xs):
            self.add(aparece(VGroup(caja(est, 4.0, 2.9, est.acento, 0.9, 3).move_to([x, yb, 0]),
                                    texto(est, "computadora " + "ABC"[k], 36, est.tenue).move_to([x, yb + 0.85, 0])).set_z_index(8), pel, 0.3 + 0.3 * k))
            siete = texto(est, "7", 80, est.tinta, "cifra", "BOLD").move_to([x, yb - 0.35, 0]).set_z_index(9)
            linea = Line([x, yb - 1.45, 0], [x * 0.35, yv + 1.25, 0], stroke_width=4, color=est.acento).set_z_index(7)
            if k != 1:
                self.add(aparece(siete, pel, 0.9 + 0.3 * k), aparece(linea, pel, 1.6))
            else:
                cinco = texto(est, "5", 80, ROJO, "cifra", "BOLD").move_to([x, yb - 0.35, 0]).set_z_index(9)
                malo = lambda: rampa(pel.t, T_ION + 0.05, 0.2) * (1 - rampa(pel.t, T_SANA, 0.4))
                self.add(vive(siete, lambda: rampa(pel.t, 1.2) * (1 - malo())), vive(cinco, malo))
                self.add(aparece(linea, pel, 1.6))
                roja = Line([x, yb - 1.45, 0], [x * 0.35, yv + 1.25, 0], stroke_width=6, color=ROJO).set_z_index(7)
                self.add(vive(roja, malo))
                self.add(vive(Square(4.0).stretch_to_fit_height(2.9).set_fill(ROJO, 0.1).set_stroke(ROJO, 5).move_to([x, yb, 0]).set_z_index(8), malo))
                self.add(vive(destello([x, yb, 0], ROJO, 1.4), pulso(pel, T_ION + 0.1, 0.6)))
                self.add(vive(destello([x, yb, 0], est.acento, 1.4), pulso(pel, T_SANA + 0.1, 0.6)))
                self.add(aparece(texto(est, "se reinicia", 38, est.acento).move_to([x, yb + 1.85, 0]).set_z_index(9), pel, T_SANA))
                ion(self, est, pel, [x, yb, 0], T_ION, dire=(1.0, -0.6), largo=9.0, dur=1.1)
            for q in range(3):                                         # los datos viajan al voto
                p = punto(ROJO if k == 1 else est.acento, 0.09)
                a, b = np.array([x, yb - 1.45, 0]), np.array([x * 0.35, yv + 1.25, 0])

                def fluir(m, a=a, b=b, q=q):
                    u = (pel.t * 0.5 + q / 3) % 1.0
                    vivo = rampa(pel.t, 2.0)
                    fundir(m.move_to(a + (b - a) * u), vivo * min(1, u / 0.1, (1 - u) / 0.1))
                p.add_updater(fluir); fundir(p, 0); self.add(p)
        self.add(aparece(Arrow([0, yv - 1.25, 0], [0, -2.6, 0], buff=0, stroke_width=6, color=est.calido).set_z_index(8), pel, 2.8))
        self.add(aparece(texto(est, "resultado: 7", 56, est.calido, "titulo", "SEMIBOLD").move_to([0, -3.15, 0]).set_z_index(9), pel, 3.0))
        for k, (a, b, col) in enumerate((("una sola:", "falla 1 de cada 1 000", est.tinta), ("las tres votando:", "≈ 3 de cada 1 000 000", est.acento))):
            g = VGroup(texto(est, a, 40, est.tenue), texto(est, b, 48, col, "cifra", "SEMIBOLD")).arrange(RIGHT, buff=0.3).move_to([0, -4.25 - 0.95 * k, 0])
            self.add(aparece(g.set_z_index(9), pel, 8.8 + 1.4 * k))
        leyendas(self, est, pel, n, [
            ("Tres copias hacen la misma cuenta", "y una cuarta pieza compara los resultados"),
            ("Si una se equivoca, gana la mayoría", "tendrían que fallar dos al mismo tiempo"),
            ("Unas 300 veces menos errores", "se llama «triple redundancia modular»")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 3 · Un código que encuentra el error (Hamming 7,4) ════════════════════════════════════════════════════════════════

class ReelELHamming(Scene):
    VAR = 2

    def construct(self):
        n = "ReelELHamming"; TB = DL.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Un código que\nencuentra el error", self.VAR, chip_txt="Ilustración", **SERIE)
        X = lambda pos: -0.5 + (pos - 4) * 1.85
        Y, s = 3.3, 1.6
        T_ION, T_FIX = 6.6, 13.2
        orden = {3: 0, 5: 1, 6: 2, 7: 3, 1: 4, 2: 5, 4: 6}
        for pos in range(1, 8):
            ctrl = pos in (1, 2, 4)
            col = est.calido if ctrl else est.acento
            t0 = 0.4 + 0.45 * orden[pos] + (0.8 if ctrl else 0)
            c = np.array([X(pos), Y, 0])
            self.add(aparece(caja(est, s, s, col, 0.88, 4).move_to(c).set_z_index(6), pel, t0))
            self.add(aparece(texto(est, str(pos), 34, est.tenue).move_to(c + UP * 1.2).set_z_index(7), pel, t0))
            v = DL.PALABRA[pos - 1]
            bit = texto(est, str(v), 56, est.tinta, "cifra", "BOLD").move_to(c).set_z_index(7)
            if pos != DL.BIT_MALO:
                self.add(aparece(bit, pel, t0 + 0.1))
                continue
            malo = lambda: rampa(pel.t, T_ION + 0.05, 0.2) * (1 - rampa(pel.t, T_FIX, 0.3))
            otro = texto(est, str(1 - v), 56, ROJO, "cifra", "BOLD").move_to(c).set_z_index(7)
            self.add(vive(bit, lambda t0=t0: rampa(pel.t, t0 + 0.1) * (1 - malo())), vive(otro, malo))
            self.add(vive(Square(s).set_fill(ROJO, 0.12).set_stroke(ROJO, 6).move_to(c).set_z_index(6), malo))
            self.add(vive(destello(c, ROJO, 1.1), pulso(pel, T_ION + 0.1, 0.6)))
            self.add(vive(destello(c, est.acento, 1.1), pulso(pel, T_FIX + 0.1, 0.6)))
            ion(self, est, pel, c, T_ION, dire=(-0.7, -1.0), largo=9.0, dur=1.1)
        clave = VGroup(Square(0.34).set_fill(est.acento, 0.9).set_stroke(width=0), texto(est, "dato", 34, est.tinta),
                       Square(0.34).set_fill(est.calido, 0.9).set_stroke(width=0), texto(est, "control", 34, est.tinta)).arrange(RIGHT, buff=0.25)
        clave[2].shift(RIGHT * 0.5); clave[3].shift(RIGHT * 0.5)
        self.add(aparece(clave.move_to([-0.3, 1.6, 0]).set_z_index(8), pel, 3.6, hasta=6.2))
        # tres revisiones: el control k mira las posiciones con el bit k encendido
        for r, k in enumerate((1, 2, 4)):
            y = 0.6 - 1.9 * r
            t0 = 8.0 + 1.0 * r
            ok = sum(DL.RECIBIDA[p - 1] for p in range(1, 8) if p & k) % 2 == 0
            g = VGroup(Line([X(1) - 0.8, y, 0], [X(7) + 0.8, y, 0], stroke_width=2, color=est.tenue).set_opacity(0.5))
            for p in range(1, 8):
                if p & k:
                    g.add(Dot([X(p), y, 0], radius=0.22, color=est.calido if p == k else est.acento))
            g.add(texto(est, f"revisión {r + 1}", 38, est.tinta).next_to([X(1) - 0.8, y + 0.55, 0], RIGHT, buff=0))
            self.add(aparece(g.set_z_index(8), pel, t0, 0.4))
            c_m = np.array([6.25, y, 0])
            if ok:
                self.add(aparece(marca_ok(c_m, est.acento, 0.4).set_z_index(9), pel, t0, 0.4))
            else:
                self.add(aparece(marca_mal(c_m, ROJO, 0.36).set_z_index(9), pel, t0, 0.4, hasta=T_FIX))
                self.add(aparece(marca_ok(c_m, est.acento, 0.4).set_z_index(9), pel, T_FIX + 0.4, 0.4))
        self.add(aparece(texto(est, "fallan la 2 y la 3 → el bit 6", 50, est.calido, "titulo", "SEMIBOLD", ancho_max=12.8)
                         .move_to([0, -5.0, 0]).set_z_index(9), pel, 11.0, hasta=12.6))
        self.add(aparece(texto(est, "bit 6 corregido", 56, est.acento, "titulo", "SEMIBOLD").move_to([0, -5.0, 0]).set_z_index(9), pel, T_FIX + 0.4))
        leyendas(self, est, pel, n, [
            ("4 bits de dato + 3 de control", "cada control resume a algunos de los datos"),
            ("Un bit cambia en el camino", "las revisiones que fallan señalan cuál fue"),
            ("El error se corrige solo", "así se protege la memoria de muchos satélites")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 4 · La radiación que se acumula (dosis total) ═════════════════════════════════════════════════════════════════════

class ReelELDosis(Scene):
    VAR = 0

    def construct(self):
        n = "ReelELDosis"; TB = DL.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "La radiación\nque se acumula", self.VAR, chip_txt="Orden de magnitud", **SERIE)
        C = np.array([-2.0, 2.7, 0])
        self.add(aparece(chip_ic(est, C, 3.4, est.acento, 8).set_z_index(8), pel, 0.2))
        rng = np.random.default_rng(11)
        for q in range(16):                                           # lluvia de partículas sobre el chip
            x0, dx = rng.uniform(-6.5, 3.0), rng.uniform(0.4, 1.4)
            fase, vel = rng.uniform(0, 1), rng.uniform(0.35, 0.55)
            p = punto(est.calido if q % 3 else ROJO, 0.07)

            def caer(m, x0=x0, dx=dx, fase=fase, vel=vel):
                u = (pel.t * vel + fase) % 1.0
                pos = np.array([x0 + dx * u * 3, 5.4 - 5.6 * u, 0])
                fundir(m.move_to(pos), rampa(pel.t, 0.6) * (1 - rampa(pel.t, 12.0)) * min(1, u / 0.1, (1 - u) / 0.1) * zona(pos))
            p.add_updater(caer); fundir(p, 0); self.add(p)
        # medidor de dosis a la derecha del chip
        mx, my0, mh = 3.6, 0.9, 4.0
        self.add(aparece(VGroup(RoundedRectangle(corner_radius=0.2, width=1.4, height=mh).set_fill(est.fondo, 0.85).set_stroke(est.tenue, 3)
                                .move_to([mx, my0 + mh / 2, 0]),
                                texto(est, "dosis", 40, est.tenue).move_to([mx, my0 - 0.5, 0])).set_z_index(8), pel, 0.6, hasta=12.4))
        nivel = Rectangle(width=1.05, height=mh).set_fill(est.calido, 0.85).set_stroke(width=0).set_z_index(9)
        nivel.add_updater(lambda m: m.stretch_to_fit_height(max(0.02, (mh - 0.3) * rampa(pel.t, 1.0, 10.0))).move_to([mx, my0 + 0.15, 0], aligned_edge=DOWN))
        self.add(aparece(nivel, pel, 1.0, 0.4, hasta=12.4))
        # escala logarítmica: persona, chip común, chip endurecido
        Xd = lambda D: -6.4 + 12.8 * np.log10(D / 0.1) / 4.0
        renglones = [("dosis que mataría a una persona", DL.DOSIS_HUMANO_KRAD, est.tinta, None),
                     ("lo que aguanta un chip común: ~10 veces más", DL.DOSIS_COMERCIAL_KRAD, est.calido, None),
                     ("un chip endurecido: cientos de veces más", DL.DOSIS_ENDURECIDO_KRAD, est.acento, 1000.0)]
        for k, (txt, D, col, D2) in enumerate(renglones):
            y = -0.75 - 1.65 * k
            t0 = 6.6 + 1.6 * k
            self.add(aparece(texto(est, txt, 40, est.tinta, ancho_max=12.8).next_to([-6.4, y, 0], RIGHT, buff=0).set_z_index(9), pel, t0))
            w = Xd(D) + 6.4
            barra = Rectangle(width=w, height=0.6).set_fill(col, 0.9).set_stroke(width=0).set_z_index(9)
            barra.add_updater(lambda m, t0=t0, w=w, y=y: m.stretch_to_fit_width(max(0.04, w * rampa(pel.t, t0 + 0.2, 1.2))).move_to([-6.4, y - 0.75, 0], aligned_edge=LEFT))
            self.add(aparece(barra, pel, t0, 0.3))
            if D2:
                banda = Rectangle(width=Xd(D2) - Xd(100), height=0.6).set_fill(col, 0.25).set_stroke(col, 2).move_to([(Xd(100) + Xd(D2)) / 2, y - 0.75, 0]).set_z_index(8)
                self.add(aparece(banda, pel, t0 + 1.2))
                brillo = Rectangle(width=w + 0.3, height=1.0).set_fill(col, 0.0).set_stroke(col, 4).move_to([-6.4 + w / 2, y - 0.75, 0]).set_z_index(10)
                self.add(vive(brillo, lambda: rampa(pel.t, 13.2) * (0.55 + 0.45 * np.sin(2 * np.pi * pel.t / 2.0))))
        self.add(aparece(texto(est, "escala: ×10 en cada paso", 32, est.tenue).move_to([3.4, -5.6, 0]).set_z_index(9), pel, 7.0))
        leyendas(self, est, pel, n, [
            ("Cada partícula deja un poco de daño", "se suma año tras año: la «dosis total»"),
            ("Un chip común aguanta más que tú", "unas 10 veces la dosis que mataría a una persona"),
            ("Los endurecidos aguantan muchísimo más", "se diseñan y se prueban para eso; y se blindan")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 5 · El cortocircuito que se dispara solo (latch-up) ═════════════════════════════════════════════════════════════════

class ReelELLatch(Scene):
    VAR = 1

    def construct(self):
        n = "ReelELLatch"; TB = DL.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "El cortocircuito\nque se dispara solo", self.VAR, chip_txt="Ilustración", **SERIE)
        T_ION, T_CORTE, T_VUELVE, T_FIN = 3.6, 7.2, 8.6, 13.0
        CH, LIM = np.array([-3.2, 3.5, 0]), np.array([3.4, 3.5, 0])
        self.add(aparece(chip_ic(est, CH, 2.5, est.acento, 6).set_z_index(8), pel, 0.2))
        self.add(aparece(texto(est, "chip", 38, est.tenue).next_to(CH + LEFT * 1.65, LEFT, buff=0.15).set_z_index(9), pel, 0.4))
        caliente = lambda: rampa(pel.t, T_ION + 0.1, 0.4) * (1 - rampa(pel.t, T_CORTE, 0.3))
        self.add(vive(VGroup(*[Circle(radius=r).set_fill(ROJO, a).set_stroke(width=0) for r, a in ((2.2, 0.12), (1.6, 0.18))]).move_to(CH).set_z_index(7), caliente))
        ion(self, est, pel, CH, T_ION, dire=(1.0, -0.7), largo=9.0, dur=1.1)
        # limitador: un interruptor que se abre
        self.add(aparece(caja(est, 3.4, 2.4, est.calido, 0.9, 3).move_to(LIM).set_z_index(8), pel, 0.6))
        self.add(aparece(texto(est, "limitador", 38, est.calido).move_to(LIM + DOWN * 1.65).set_z_index(9), pel, 0.6))
        a, b = LIM + LEFT * 0.9 + DOWN * 0.2, LIM + RIGHT * 0.9 + DOWN * 0.2
        self.add(aparece(VGroup(Dot(a, radius=0.1, color=est.tinta), Dot(b, radius=0.1, color=est.tinta)).set_z_index(9), pel, 0.6))
        palanca = Line(a, b, stroke_width=7, color=est.tinta).set_z_index(9)
        abierto = lambda: rampa(pel.t, T_CORTE, 0.2) * (1 - rampa(pel.t, T_VUELVE, 0.3))
        palanca.add_updater(lambda m: m.become(Line(a, a + rotate_vector(b - a, 0.6 * abierto()), stroke_width=7, color=est.tinta).set_z_index(9)))
        self.add(aparece(palanca, pel, 0.6))
        self.add(aparece(Line(CH + RIGHT * 1.45, LIM + LEFT * 1.5, stroke_width=4, color=est.acento).set_z_index(7), pel, 0.8))
        # corriente en el tiempo
        X0, X1, Y0 = -6.2, 6.2, -5.2
        y_base, y_alta = -4.3, 0.4
        self.add(aparece(VGroup(Arrow([X0, Y0, 0], [X0, 1.5, 0], buff=0, stroke_width=4, color=est.tenue),
                                Arrow([X0, Y0, 0], [X1 + 0.3, Y0, 0], buff=0, stroke_width=4, color=est.tenue),
                                texto(est, "corriente", 36, est.tenue).next_to([X0 + 0.35, 1.3, 0], RIGHT, buff=0),
                                texto(est, "tiempo", 30, est.tenue).move_to([X1 - 0.6, Y0 - 0.4, 0])).set_z_index(8), pel, 1.0))
        lim = DashedLine([X0, -1.4, 0], [X1, -1.4, 0], dash_length=0.25, stroke_width=3, color=est.calido).set_z_index(8)
        self.add(aparece(lim, pel, 5.6), aparece(texto(est, "límite", 36, est.calido).move_to([X1 - 0.9, -0.95, 0]).set_z_index(9), pel, 5.6))

        def i_de(s):
            ruido = 0.07 * np.sin(7.1 * s) + 0.05 * np.sin(12.7 * s + 1)
            if s < T_ION:
                return y_base + ruido
            if s < T_CORTE:
                return y_base + (y_alta - y_base) * suave((s - T_ION) / 0.15) + ruido * 0.6
            if s < T_VUELVE:
                return Y0 + 0.02
            return y_base + ruido
        curva = VMobject().set_z_index(9)

        def trazar(m):
            s1 = float(np.clip(pel.t, 0.0, T_FIN))
            ss = np.linspace(0.0, max(s1, 0.02), max(int(s1 * 40), 2))
            pts = np.stack([X0 + (X1 - X0) * ss / T_FIN, [i_de(s) for s in ss], 0 * ss], 1)
            col = ROJO if T_ION < pel.t < T_CORTE else est.acento
            m.become(polilinea(pts, color=col, width=6).set_z_index(9))
        curva.add_updater(trazar)
        self.add(aparece(curva, pel, 0.9, 0.3))
        self.add(aparece(texto(est, "corte", 32, est.acento).move_to([X0 + (X1 - X0) * (T_CORTE + 0.7) / T_FIN, Y0 + 0.55, 0]).set_z_index(9), pel, T_CORTE + 0.2))
        leyendas(self, est, pel, n, [
            ("Una partícula abre un camino de corriente", "dentro del chip, como un cortocircuito que no se apaga"),
            ("Un vigilante corta la energía", "si la corriente pasa del límite, apaga y vuelve a encender"),
            ("Si nadie lo corta, el chip se quema", "por eso los circuitos llevan su limitador")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 6 · Un satélite con menos que un cargador (panel solar de 1U) ═════════════════════════════════════════════════════

class ReelELPanel(Scene):
    VAR = 2

    def construct(self):
        n = "ReelELPanel"; TB = DL.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Menos energía que\nun cargador de celular", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        C, L = np.array([-2.0, 2.1, 0]), 5.6
        cara = Square(L).set_fill("#2A3532", 1).set_stroke("#9AA8A2", 4).move_to(C).set_z_index(6)
        self.add(aparece(cara, pel, 0.2))
        for k in (-1, 1):
            cc = C + RIGHT * k * L * 0.235
            celda = VGroup(Rectangle(width=L * 0.42, height=L * 0.86).set_fill(CELDA, 1).set_stroke("#6F7FB8", 2))
            for j in range(1, 10):
                yj = -L * 0.43 + j * L * 0.86 / 10
                celda.add(Line([-L * 0.21, yj, 0], [L * 0.21, yj, 0], stroke_width=1.4, color="#AEB8D8").set_opacity(0.55))
            celda.add(Line([0, -L * 0.43, 0], [0, L * 0.43, 0], stroke_width=3, color="#AEB8D8").set_opacity(0.7))
            self.add(aparece(celda.move_to(cc).set_z_index(7), pel, 0.6 + 0.4 * (k + 1)))
        brillo = Square(L).set_fill(est.calido, 0.10).set_stroke(width=0).move_to(C).set_z_index(8)
        self.add(vive(brillo, lambda: rampa(pel.t, 2.4) * (0.7 + 0.3 * np.sin(2 * np.pi * pel.t / 2.5))))
        cota = VGroup(Line(C + np.array([-L / 2, -L / 2 - 0.45, 0]), C + np.array([L / 2, -L / 2 - 0.45, 0]), stroke_width=3, color=est.tenue),
                      texto(est, "10 cm", 36, est.tenue).move_to(C + DOWN * (L / 2 + 0.95)))
        self.add(aparece(cota.set_z_index(8), pel, 1.6))
        d = np.array([0.55, -1.0, 0]); d /= np.linalg.norm(d)
        for q in range(7):                                           # rayos del Sol que llegan a la cara
            meta = C + np.array([-L * 0.38 + L * 0.76 * q / 6, L * (0.3 - 0.1 * (q % 3)), 0])

            def rayo(m, meta=meta, q=q):
                u = (pel.t * 0.7 + q * 0.37) % 1.0
                a = meta - d * 5.0 * (1 - u)
                m.put_start_and_end_on(a - d * 1.0, a)
                fundir(m, rampa(pel.t, 1.8) * min(1, u / 0.2, (1 - u) / 0.08) * zona(a))
            r = Line(ORIGIN, RIGHT, stroke_width=5, color=est.calido).set_z_index(9)
            r.add_updater(rayo); fundir(r, 0); self.add(r)
        self.add(aparece(VGroup(texto(est, f"≈ {DL.PANEL_W:.0f} W", 120, est.calido, "cifra", "BOLD"),
                                texto(est, "por cara", 40, est.tenue)).arrange(DOWN, buff=0.3).move_to([4.4, 2.3, 0]).set_z_index(9), pel, 6.4))
        for k, (txt, w, col) in enumerate((("una cara del satélite", DL.PANEL_W, est.calido), ("un cargador de celular", DL.CARGADOR_W, est.acento))):
            y = -2.75 - 1.55 * k
            t0 = 8.0 + 1.0 * k
            self.add(aparece(texto(est, txt, 42, est.tinta).next_to([-6.4, y, 0], RIGHT, buff=0).set_z_index(9), pel, t0))
            ww = 11.0 * w / 5.0
            barra = Rectangle(width=ww, height=0.6).set_fill(col, 0.9).set_stroke(width=0).set_z_index(9)
            barra.add_updater(lambda m, t0=t0, ww=ww, y=y: m.stretch_to_fit_width(max(0.04, ww * rampa(pel.t, t0 + 0.2, 1.0))).move_to([-6.4, y - 0.75, 0], aligned_edge=LEFT))
            self.add(aparece(barra, pel, t0, 0.3))
            self.add(aparece(texto(est, f"{w:.0f} W", 44, col, "cifra", "SEMIBOLD").next_to([-6.4 + ww, y - 0.75, 0], RIGHT, buff=0.3).set_z_index(9), pel, t0 + 1.0))
        leyendas(self, est, pel, n, [
            ("Cada cara lleva celdas solares", "convierten en electricidad ~28 % de la luz"),
            ("Una cara da unos 2 watts", "menos que un cargador de celular"),
            ("Con eso vive todo el satélite", "radio, computadora y sensores, con cada watt contado")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 7 · 15 noches cada día (batería en eclipse) ════════════════════════════════════════════════════════════════════════

class ReelELBateria(Scene):
    VAR = 0

    def construct(self):
        n = "ReelELBateria"; TB = DL.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "15 noches\ncada día", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        C, RT, RO, PER = np.array([0, 1.7, 0]), 2.9, 3.4, 4.0
        sombra = Rectangle(width=7.2, height=2 * RT).set_fill("#000000", 0.45).set_stroke(width=0).move_to(C + RIGHT * 3.6).set_z_index(5)
        self.add(aparece(sombra, pel, 0.3))
        tierra = VGroup(Circle(radius=RT * 1.05).set_fill(AZUL, 0.18).set_stroke(width=0),
                        Circle(radius=RT).set_fill(est.mezcla(est.fondo, AZUL, 0.75), 1).set_stroke("#8FD8FF", 3),
                        AnnularSector(inner_radius=0, outer_radius=RT, angle=PI, start_angle=-PI / 2).set_fill("#000000", 0.45).set_stroke(width=0))
        self.add(aparece(tierra.move_to(C).set_z_index(6), pel, 0.2))
        self.add(aparece(Circle(radius=RO).set_stroke(est.tenue, 2, 0.6).move_to(C).set_z_index(7), pel, 0.5))
        for k in range(5):
            y = C[1] + (k - 2) * 1.3
            self.add(aparece(Arrow([-6.6, y, 0], [-5.0, y, 0], buff=0, stroke_width=5, color=est.calido).set_z_index(7), pel, 0.6))
        self.add(aparece(texto(est, "Sol", 36, est.calido, "titulo", "SEMIBOLD").move_to([-5.8, C[1] + 3.6, 0]).set_z_index(8), pel, 0.6))
        th_s = np.arcsin(RT / RO)
        a0, a1 = 0.75 - th_s / (2 * np.pi), 0.75 + th_s / (2 * np.pi)      # fase de la noche (el satélite sale de arriba, antihorario)
        fr = a1 - a0

        def fase():
            return (pel.t / PER) % 1.0

        def nivel():
            f = fase()
            if f < a0:
                return 0.65 + 0.30 * f / (1 - fr)
            if f < a1:
                return 0.95 - 0.30 * (f - a0) / fr
            return 0.65 + 0.30 * (f - a1) / (1 - fr)

        noche = lambda: float(a0 <= fase() < a1)
        sat = punto(est.calido, 0.14).set_z_index(10)
        sat.add_updater(lambda m: fundir(m.move_to(C + RO * np.array([np.cos(np.pi / 2 + 2 * np.pi * fase()), np.sin(np.pi / 2 + 2 * np.pi * fase()), 0])),
                                         rampa(pel.t, 0.8) * (1 - 0.6 * noche())))
        fundir(sat, 0); self.add(sat)
        # batería
        B = np.array([-1.4, -3.5, 0])
        cuerpo = VGroup(RoundedRectangle(corner_radius=0.18, width=6.0, height=1.9).set_stroke(est.tinta, 5).set_fill(est.fondo, 0.85),
                        Rectangle(width=0.3, height=0.8).set_fill(est.tinta, 1).set_stroke(width=0).shift(RIGHT * 3.15)).move_to(B).set_z_index(8)
        self.add(aparece(cuerpo, pel, 1.0))
        carga = Rectangle(width=5.6, height=1.5).set_fill(est.acento, 0.85).set_stroke(width=0).set_z_index(9)
        carga.add_updater(lambda m: m.stretch_to_fit_width(5.6 * nivel()).move_to(B + LEFT * 2.8, aligned_edge=LEFT)
                          .set_fill(est.acento if not noche() else est.calido))
        self.add(aparece(carga, pel, 1.2))
        self.add(Viva(est, lambda: "descarga" if noche() else "carga", [4.6, B[1], 0], 48, rol="titulo",
                      f_op=lambda: rampa(pel.t, 1.4)))
        self.add(aparece(texto(est, "noche: hasta 36 min de cada 95", 40, est.calido, "titulo", "SEMIBOLD", ancho_max=12.8)
                         .move_to([0, -5.05, 0]).set_z_index(9), pel, 7.0, hasta=12.4))
        self.add(aparece(texto(est, f"≈ {DL.CICLOS_ANIO:,.0f} ciclos al año · celular ≈ 365".replace(",", " "), 40, est.acento, "titulo", "SEMIBOLD", ancho_max=12.8)
                         .move_to([0, -5.05, 0]).set_z_index(9), pel, 13.0))
        leyendas(self, est, pel, n, [
            ("Una vuelta a la Tierra en hora y media", "a 550 km de altura: unas 15 vueltas al día"),
            ("Cada vuelta tiene su noche", "a oscuras, todo funciona con la batería"),
            ("15 veces más ciclos que tu celular", "cargar y descargar, miles de veces al año")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 8 · Sin aire, el calor no tiene a dónde ir ══════════════════════════════════════════════════════════════════════════

class ReelELCalor(Scene):
    VAR = 1

    def construct(self):
        n = "ReelELCalor"; TB = DL.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Sin aire, el calor\nno tiene a dónde ir", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        I, D = np.array([-3.4, 2.4, 0]), np.array([3.4, 2.4, 0])
        for c, tit in ((I, "en la Tierra"), (D, "en órbita")):
            self.add(aparece(VGroup(caja(est, 6.3, 5.6, est.tenue, 0.75, 2).move_to(c + UP * 0.1),
                                    texto(est, tit, 44, est.tinta, "titulo", "SEMIBOLD").move_to(c + UP * 2.3)).set_z_index(6), pel, 0.2, hasta=12.4))
            self.add(aparece(chip_ic(est, c + DOWN * 0.5, 2.0, est.acento, 5).set_z_index(8), pel, 0.5, hasta=12.4))
        rng = np.random.default_rng(5)
        for q in range(10):                                          # aire que sube y se lleva el calor
            x, fase = I[0] + (-2.5, -1.9, 1.9, 2.5, -2.2, 2.2, -1.5, 1.5, -2.7, 2.7)[q], q / 10

            def subir(m, x=x, fase=fase):
                u = (pel.t * 0.45 + fase) % 1.0
                y = I[1] - 2.3 + 3.6 * u
                m.become(polilinea([[x + 0.15 * np.sin(5 * yy + 3 * u), yy, 0] for yy in np.linspace(y, y + 1.0, 14)], color="#8FD8FF", width=7).set_z_index(9))
                fundir(m, rampa(pel.t, 1.0) * (1 - rampa(pel.t, 12.0)) * min(1, u / 0.2, (1 - u) / 0.2))
            a = VMobject(); a.add_updater(subir); self.add(a)
        calor = lambda: rampa(pel.t, 1.0, 5.0) * (1 - rampa(pel.t, 12.0))
        self.add(vive(VGroup(*[Circle(radius=r).set_fill(ROJO, op).set_stroke(width=0) for r, op in ((1.7, 0.10), (1.25, 0.16))]).move_to(D + DOWN * 0.5).set_z_index(7), calor))
        self.add(aparece(texto(est, "sin aire", 40, est.calido).move_to(D + UP * 1.4).set_z_index(9), pel, 2.0, hasta=12.4))
        self.add(aparece(texto(est, "el aire se lleva el calor", 32, "#8FD8FF").move_to(I + DOWN * 2.2).set_z_index(9), pel, 2.0, hasta=12.4))
        # placa al Sol y termómetro
        P = np.array([-3.0, -2.8, 0])
        placa = Rectangle(width=3.6, height=0.35).set_fill("#151A18", 1).set_stroke("#9AA8A2", 3).move_to(P).set_z_index(8)
        self.add(aparece(placa, pel, 6.4, hasta=12.4))
        for q in range(5):
            x = P[0] - 1.4 + 0.7 * q
            self.add(aparece(Arrow([x - 0.9, P[1] + 2.0, 0], [x, P[1] + 0.3, 0], buff=0, stroke_width=5, color=est.calido).set_z_index(8), pel, 6.6, hasta=12.4))
        self.add(aparece(texto(est, "placa al Sol", 34, est.tenue).move_to(P + DOWN * 0.8).set_z_index(9), pel, 6.6, hasta=12.4))
        T = np.array([3.6, -2.9, 0])
        tubo = VGroup(RoundedRectangle(corner_radius=0.3, width=0.6, height=4.2).set_fill(est.fondo, 0.85).set_stroke(est.tinta, 3).move_to(T),
                      Circle(radius=0.5).set_fill(ROJO, 1).set_stroke(est.tinta, 3).move_to(T + DOWN * 2.3)).set_z_index(8)
        self.add(aparece(tubo, pel, 6.6, hasta=12.4))
        sube = lambda: rampa(pel.t, 7.2, 3.0)
        mercurio = Rectangle(width=0.32, height=4.0).set_fill(ROJO, 1).set_stroke(width=0).set_z_index(9)
        mercurio.add_updater(lambda m: m.stretch_to_fit_height(0.4 + 3.4 * sube()).move_to(T + DOWN * 2.0, aligned_edge=DOWN))
        self.add(aparece(mercurio, pel, 6.6, hasta=12.4))
        self.add(Viva(est, lambda: f"{20 + (DL.T_PLACA_SOL_C - 20) * sube():.0f} °C", [T[0] + 1.9, T[1] + 0.3, 0], 56, est.calido,
                      f_op=lambda: rampa(pel.t, 7.0) * (1 - rampa(pel.t, 12.4))))
        # radiador: 1 W → ~5 × 5 cm
        R, lado = np.array([-2.2, -1.6, 0]), 3.8
        self.add(aparece(VGroup(Square(lado).set_fill("#1E2623", 1).set_stroke("#C9D6D0", 3).move_to(R),
                                *[Line(R + np.array([-lado / 2 + 0.3, -lado / 2 + 0.4 * j, 0]), R + np.array([lado / 2 - 0.3, -lado / 2 + 0.4 * j, 0]),
                                       stroke_width=2, color="#55615C") for j in range(1, 8)]).set_z_index(8), pel, 13.0))
        self.add(aparece(texto(est, "≈ 5 × 5 cm", 44, est.tinta, "cifra", "SEMIBOLD").move_to(R + DOWN * (lado / 2 + 0.6)).set_z_index(9), pel, 13.4))
        self.add(aparece(VGroup(chip_ic(est, [3.6, R[1], 0], 1.8, est.acento, 5),
                                texto(est, "1 W", 56, est.calido, "cifra", "BOLD").move_to([3.6, R[1] - 1.75, 0])).set_z_index(8), pel, 13.0))
        self.add(aparece(Line([2.5, R[1], 0], [R[0] + lado / 2, R[1], 0], stroke_width=8, color=est.calido).set_z_index(7), pel, 13.2))
        for q in range(6):                                           # infrarrojo: ondas que salen del radiador
            ang = np.pi / 2 + (q - 2.5) * 0.38

            def onda(m, ang=ang, q=q):
                u = (pel.t * 0.5 + q / 6) % 1.0
                d = np.array([np.cos(ang), np.sin(ang), 0])
                ppal = R + d * (lado * 0.6 + 3.6 * u)
                nrm = np.array([-d[1], d[0], 0])
                m.become(polilinea([ppal + d * s + nrm * 0.15 * np.sin(12 * s) for s in np.linspace(0, 1.2, 20)], color=ROJO, width=6).set_z_index(9))
                fundir(m, rampa(pel.t, 13.6) * min(1, u / 0.2, (1 - u) / 0.2) * zona(ppal))
            w = VMobject(); w.add_updater(onda); self.add(w)
        leyendas(self, est, pel, n, [
            ("Aquí el aire enfría los chips", "en el vacío no hay aire que se lleve el calor"),
            ("Al Sol, una placa llega a 120 °C", "y en la sombra se enfría muchísimo"),
            ("El calor se tira como luz infrarroja", "cada watt pide un radiador de unos 5 × 5 cm")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 9 · Bajar una foto toma varios pases ═══════════════════════════════════════════════════════════════════════════════

class ReelELBajada(Scene):
    VAR = 2

    def construct(self):
        n = "ReelELBajada"; TB = DL.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Bajar una foto toma\nvarios pases", self.VAR, chip_txt="Cálculo ilustrativo", **SERIE)
        T0, VIS, CIC, NP = 0.8, 3.4, 4.4, 4
        ANT = np.array([-4.6, -4.0, 0])

        def en_pase():
            u = pel.t - T0
            k = int(np.floor(u / CIC))
            return (0 <= k < NP and (u - k * CIC) < VIS), (u - k * CIC) / VIS, k

        def enviado():
            u = float(np.clip(pel.t - T0, 0, NP * CIC))
            k = int(min(u // CIC, NP))
            return min((k * VIS + min(u - k * CIC, VIS)) / (NP * VIS), 1.0)

        def pos_sat():
            ok, f, _ = en_pase()
            x = -6.9 + 13.8 * np.clip(f, 0, 1)
            return np.array([x, 4.6 - 4.4 * (x / 6.9) ** 2, 0])

        self.add(aparece(DashedVMobject(polilinea([[x, 4.6 - 4.4 * (x / 6.9) ** 2, 0] for x in np.linspace(-6.6, 6.6, 80)],
                                                  color=est.tenue, width=2, opacity=0.5), num_dashes=40).set_z_index(5), pel, 0.3))
        sat = VGroup(Rectangle(width=2.4, height=0.4).set_fill(CELDA, 1).set_stroke("#6F7FB8", 2),
                     Square(0.7).set_fill(est.tinta, 1).set_stroke(width=0)).set_z_index(10)
        sat.add_updater(lambda m: fundir(m.move_to(pos_sat()), rampa(pel.t, 0.5) * float(en_pase()[0]) * min(1, en_pase()[1] / 0.05, (1 - en_pase()[1]) / 0.05)))
        fundir(sat, 0); self.add(sat)
        antena = VGroup(Line(ANT + DOWN * 1.3, ANT, stroke_width=8, color=est.tinta),
                        Line(ANT + DOWN * 1.3 + LEFT * 0.7, ANT + DOWN * 1.3 + RIGHT * 0.7, stroke_width=8, color=est.tinta),
                        Arc(radius=1.4, start_angle=PI + 0.5, angle=PI - 1.0, arc_center=ANT + UP * 1.6).set_stroke(est.tinta, 8)).set_z_index(9)
        self.add(aparece(antena, pel, 0.2))
        haz = DashedLine(ANT + UP * 0.4, ANT + UP * 2, dash_length=0.2, stroke_width=4, color=est.acento).set_z_index(8)
        haz.add_updater(lambda m: fundir(m.become(DashedLine(ANT + UP * 0.4, pos_sat(), dash_length=0.22, stroke_width=4, color=est.acento).set_z_index(8)),
                                         rampa(pel.t, 0.5) * float(en_pase()[0])))
        self.add(haz)
        # la foto: se llena por renglones solo durante los pases
        nx, ny, px = 16, 12, 0.41
        F0 = np.array([-0.2, -5.4, 0])
        rng = np.random.default_rng(7)
        yy, xx = np.mgrid[0:ny, 0:nx]
        tierra = np.sin(xx * 0.5 + 1.3) + np.cos(yy * 0.6) * 0.8 + rng.normal(0, 0.35, (ny, nx))
        nube = rng.random((ny, nx))
        fotos = VGroup()
        for i in range(ny):
            for j in range(nx):
                col = "#E8F0F2" if nube[i, j] > 0.86 else ("#3C7A3A" if tierra[i, j] > 0.7 else ("#7A6A3A" if tierra[i, j] > 0.4 else "#1F4F8F"))
                q = Square(px).set_fill(col, 1).set_stroke(width=0).move_to(F0 + np.array([(j + 0.5) * px, (ny - i - 0.5) * px, 0]))
                q.idx = i * nx + j
                fotos.add(q)
        fotos.set_z_index(8)
        fotos.add_updater(lambda m: [fundir(q, rampa(pel.t, 0.6) * float(q.idx < enviado() * nx * ny)) for q in m])
        self.add(fotos)
        self.add(aparece(Rectangle(width=nx * px, height=ny * px).set_fill(est.fondo, 0.6).set_stroke(est.tinta, 3)
                         .move_to(F0 + np.array([nx * px / 2, ny * px / 2, 0])).set_z_index(7), pel, 0.6))
        self.add(Viva(est, lambda: f"foto · {100 * enviado():.0f} %", [F0[0] + nx * px / 2, F0[1] + ny * px + 0.6, 0], 48, est.acento, rol="titulo",
                      f_op=lambda: rampa(pel.t, 0.8)))
        self.add(Viva(est, lambda: f"pase {min(en_pase()[2] + 1, NP) if pel.t > T0 else 1}", [ANT[0], ANT[1] + 3.0, 0], 48, est.calido, rol="titulo",
                      f_op=lambda: rampa(pel.t, 0.8)))
        leyendas(self, est, pel, n, [
            ("El satélite pasa unos minutos", "y solo entonces puede hablar con la antena"),
            ("Una foto de 3 MB: 42 minutos", "a 9 600 bits por segundo, radio típico de cubesat"),
            ("Necesita unos 4 pases", "por eso a bordo se elige qué vale la pena bajar")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 10 · Computadoras lentas a propósito ═══════════════════════════════════════════════════════════════════════════════

class ReelELLento(Scene):
    VAR = 0

    def construct(self):
        n = "ReelELLento"; TB = DL.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Computadoras lentas\na propósito", self.VAR, chip_txt="Datos públicos", **SERIE)
        X0, X1 = -6.2, 6.2
        filas = [("rover de Marte · RAD750 · 200 MHz", 1, 4.7, est.acento), ("celular · ~3 GHz por núcleo", DL.VECES_RELOJ, 1.0, est.calido)]
        for k, (tit, ciclos, y, col) in enumerate(filas):
            t0 = 0.3 + 1.0 * k
            self.add(aparece(texto(est, tit, 42, est.tinta, "titulo", "SEMIBOLD", ancho_max=12.6).next_to([X0, y, 0], RIGHT, buff=0).set_z_index(9), pel, t0))
            yb, amp = y - 2.0, 0.7

            def onda(m, ciclos=ciclos, yb=yb, col=col):
                fase = 0.12 * pel.t
                xs = np.linspace(X0, X1, int(60 * ciclos) + 2)
                u = ((xs - X0) / (X1 - X0) * ciclos * 1.5 - fase * 1.5) % 1.0
                ys = yb + np.where(u < 0.5, amp, -amp)
                m.become(polilinea(np.stack([xs, ys, 0 * xs], 1), color=col, width=4).set_z_index(9))
            w = VMobject(); w.add_updater(onda); self.add(aparece(w, pel, t0 + 0.2))
            self.add(aparece(Line([X0, yb - amp - 0.25, 0], [X1, yb - amp - 0.25, 0], stroke_width=2, color=est.tenue).set_opacity(0.5).set_z_index(8), pel, t0))
        self.add(aparece(VGroup(marca_ok(np.array([0, 0, 0]), est.acento, 0.3), texto(est, "aguanta radiación", 34, est.acento),
                                marca_ok(np.array([0, 0, 0]), est.acento, 0.3), texto(est, "años de pruebas", 34, est.acento))
                         .arrange(RIGHT, buff=0.25).move_to([0, 3.85, 0]).set_z_index(9), pel, 8.0))
        self.add(aparece(texto(est, "× 15", 72, est.calido, "cifra", "BOLD").move_to([5.2, 1.05, 0]).set_z_index(9), pel, 7.0))
        # Ingenuity: un procesador de celular en Marte
        H = np.array([-4.4, -4.0, 0])
        heli = VGroup(Circle(radius=0.75).set_fill("#2A3532", 1).set_stroke(est.tinta, 3).move_to(H),
                      Line(H + UP * 0.75, H + UP * 1.75, stroke_width=6, color=est.tinta),
                      Line(H + DOWN * 0.55 + LEFT * 0.45, H + DOWN * 1.45 + LEFT * 1.1, stroke_width=5, color=est.tinta),
                      Line(H + DOWN * 0.55 + RIGHT * 0.45, H + DOWN * 1.45 + RIGHT * 1.1, stroke_width=5, color=est.tinta),
                      Rectangle(width=1.5, height=0.16).set_fill(CELDA, 1).set_stroke("#6F7FB8", 2).move_to(H + UP * 1.85)).set_z_index(9)
        self.add(aparece(heli, pel, 13.0))
        for k, y in enumerate((1.15, 1.5)):
            aspa = Line(LEFT, RIGHT, stroke_width=7, color=est.tinta).set_z_index(10)
            aspa.add_updater(lambda m, k=k, y=y: m.become(Line(H + np.array([-1.9 * abs(np.cos(9 * pel.t + 1.3 * k)), y, 0]),
                                                                  H + np.array([1.9 * abs(np.cos(9 * pel.t + 1.3 * k)) + 0.01, y, 0]), stroke_width=7, color=est.tinta).set_z_index(10)))
            self.add(aparece(aspa, pel, 13.0))
        self.add(aparece(VGroup(texto(est, "Ingenuity, helicóptero", 44, est.tinta, "titulo", "SEMIBOLD"),
                                texto(est, "chip de celular", 44, est.calido, "titulo", "SEMIBOLD"),
                                texto(est, "72 vuelos en Marte", 44, est.acento, "titulo", "SEMIBOLD"))
                         .arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to([-2.3, -3.9, 0], RIGHT, buff=0).set_z_index(9), pel, 13.4))
        leyendas(self, est, pel, n, [
            ("El rover de Marte piensa a 200 MHz", "un procesador RAD750, como el de Perseverance"),
            ("Tu celular es ~15 veces más rápido", "pero el RAD750 aguanta la radiación por años"),
            ("Ingenuity voló con un chip de celular", "y funcionó: el riesgo también se elige")])
        cerrar_serie(self, est, pel, self.VAR)

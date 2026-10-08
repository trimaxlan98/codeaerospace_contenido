import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *

import atencion as AT
import datos_ia as DI
from estilo_reel import Viva, cerrar_serie, chip, leyenda, preparar_serie, punto, texto
from reels_promo import polilinea, suave

# SERIE «INTELIGENCIA ARTIFICIAL» — divulgación de las ideas de base de la IA y un caso espacial real.
# Tema NEURONAL con fondo vertical propio (fondos_reel.neuronal: horizonte = capa de entrada de una red, resplandor violeta).
# Mismo formato de película: título → cuerpo → logo → loop exacto. Pocas cifras, todas cotidianas; lo numérico es ilustrativo.
# Embeddings y atención: los vectores 2D escritos a mano de atencion.py (mismo cálculo softmax(q·k)).

FIN = 3.0
KICKER = "Inteligencia artificial"
SERIE = dict(tema="neuronal", fondo="reel")
POS, NEG, ROJO, VERDE = "#2DD4BF", "#C084FC", "#F87171", "#4ADE80"


def leyendas(escena, est, pel, nombre, textos):
    ts = list(DI.LEYENDAS[nombre]) + [DI.CUERPO[nombre] + FIN]
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


def ficha(est, s, color, tam=34):
    t = texto(est, s, tam, est.tinta, "cuerpo", "MEDIUM")
    c = RoundedRectangle(corner_radius=0.16, width=t.width + 0.45, height=t.height + 0.42).set_fill(color, 0.16).set_stroke(color, 2.5)
    t.move_to(c)
    return VGroup(c, t).set_z_index(8)


def burbuja(est, lineas, color, ancho=10.4, tam=32, derecha=False):
    ts = VGroup(*[texto(est, l, tam, est.tinta, "cuerpo", "MEDIUM", ancho_max=ancho - 0.8) for l in lineas]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    c = RoundedRectangle(corner_radius=0.3, width=ancho, height=ts.height + 0.7).set_fill(color, 0.16).set_stroke(color, 2.5)
    ts.move_to(c).align_to(c, LEFT).shift(RIGHT * 0.4)
    return VGroup(c, ts).set_z_index(8)


def gato(color, s=1.0):
    cabeza = Circle(radius=0.42 * s).set_fill(color, 1).set_stroke(width=0)
    o1 = Triangle().scale(0.2 * s).set_fill(color, 1).set_stroke(width=0).move_to([-0.27 * s, 0.4 * s, 0])
    o2 = o1.copy().move_to([0.27 * s, 0.4 * s, 0])
    ojos = VGroup(*[Dot([x * s, 0.05 * s, 0], radius=0.055 * s, color="#FFF8D0") for x in (-0.15, 0.15)])
    return VGroup(o1, o2, cabeza, ojos).set_z_index(8)


# ══ 1 · ¿Qué es una neurona artificial? ══════════════════════════════════════════════════════════════════════════════

class ReelIaNeurona(Scene):
    VAR = 0

    def construct(self):
        n = "ReelIaNeurona"; TB = DI.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Qué es una\nneurona artificial?", self.VAR, chip_txt="Ilustración", **SERIE)
        N = np.array([0.9, 1.6, 0]); RN = 1.0
        ent = [np.array([-4.9, y, 0]) for y in (3.9, 1.6, -0.7)]
        z, sal = DI.neurona()
        for k, (p, x, w) in enumerate(zip(ent, DI.NEURONA_X, DI.NEURONA_W)):
            col = POS if w > 0 else NEG
            ln = Line(p + RIGHT * 0.55, N + LEFT * RN, stroke_width=3 + 9 * abs(w), color=col).set_z_index(4)
            self.add(aparece(ln, pel, 5.0 + 0.3 * k))
            c = VGroup(Circle(radius=0.55).set_fill(est.fondo, 1).set_stroke(est.tinta, 3), texto(est, f"{x:.1f}", 34, est.tinta, "cifra", "SEMIBOLD")).move_to(p).set_z_index(8)
            self.add(aparece(c, pel, 0.6 + 0.5 * k))
            mid = (p + RIGHT * 0.55) * 0.45 + (N + LEFT * RN) * 0.55
            et = texto(est, f"{w:+.1f}".replace("-", "−"), 32, col, "cifra", "SEMIBOLD").move_to(mid + UP * 0.42).set_z_index(9)
            self.add(aparece(et, pel, 5.4 + 0.3 * k))
            pulso = punto(col, 0.1)
            pulso.add_updater(lambda m, p=p, k=k: fundir(m.move_to((p + RIGHT * 0.55) + ((N + LEFT * RN) - (p + RIGHT * 0.55)) * (((pel.t - 7.0 - 0.2 * k) % 1.6) / 1.6)),
                                                        rampa(pel.t, 7.0, 0.3) * (1 - rampa(pel.t, 11.5, 0.4))))
            self.add(pulso)
        self.add(aparece(texto(est, "entradas", 30, est.tenue).move_to([-4.9, 5.0, 0]).set_z_index(9), pel, 0.6))
        self.add(aparece(texto(est, "pesos", 30, est.tenue).move_to([-1.8, 4.3, 0]).set_z_index(9), pel, 5.2))
        nucleo = VGroup(Circle(radius=RN).set_fill(NEG, 0.25).set_stroke(NEG, 4), texto(est, "Σ", 64, est.tinta, "cuerpo", "SEMIBOLD")).move_to(N).set_z_index(8)
        nucleo.add_updater(lambda m: fundir(m, rampa(pel.t, 1.2) * (1 + 0.0)))
        fundir(nucleo, 0)
        self.add(nucleo)
        brillo = Circle(radius=RN * 1.35).set_fill(POS, 0.22).set_stroke(width=0).move_to(N).set_z_index(7)
        brillo.add_updater(lambda m: fundir(m, rampa(pel.t, 12.6, 0.8) * (0.75 + 0.25 * np.sin(5 * pel.t))))
        fundir(brillo, 0)
        self.add(brillo)
        S = np.array([5.2, 1.6, 0])
        self.add(aparece(Arrow(N + RIGHT * RN, S + LEFT * 0.6, buff=0, stroke_width=6, color=POS).set_z_index(6), pel, 12.6))
        self.add(aparece(VGroup(Circle(radius=0.6).set_fill(POS, 0.25).set_stroke(POS, 4), texto(est, f"{sal:.2f}", 34, est.tinta, "cifra", "SEMIBOLD")).move_to(S).set_z_index(8), pel, 13.0))
        self.add(aparece(texto(est, "respuesta", 30, est.tenue).move_to(S + DOWN * 0.95).set_z_index(9), pel, 13.0))
        # la suma, término a término
        terminos = " + ".join(f"{x:.1f}×{w:.1f}".replace("-", "−") for x, w in zip(DI.NEURONA_X, DI.NEURONA_W))
        self.add(aparece(texto(est, terminos, 30, est.tinta, "cifra", "MEDIUM").move_to([0, -2.6, 0]).set_z_index(9), pel, 8.0))
        self.add(aparece(texto(est, f"− 0.3 (sesgo) = {z:.2f}", 30, est.tinta, "cifra", "MEDIUM").move_to([0, -3.4, 0]).set_z_index(9), pel, 9.0))
        self.add(aparece(texto(est, "si la suma es alta, responde fuerte", 32, POS, "cuerpo", "SEMIBOLD").move_to([0, -4.5, 0]).set_z_index(9), pel, 13.4))

        leyendas(self, est, pel, n, [
            ("Recibe números de entrada", "como los votos de varios amigos"),
            ("Cada voto tiene un peso", "a unos les hace más caso; otros restan"),
            ("Suma y decide qué tan fuerte responder", "millones de estas, conectadas, son una red neuronal")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 2 · ¿Cómo aprende una IA? (bajar la colina del error) ════════════════════════════════════════════════════════════

class ReelIaAprende(Scene):
    VAR = 1

    def construct(self):
        n = "ReelIaAprende"; TB = DI.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Cómo aprende\nuna IA?", self.VAR, chip_txt="Ilustración", **SERIE)
        X0, X1, Y0, Y1 = -6.2, 6.2, -4.6, 3.6
        fx = lambda x: X0 + (x + 2.6) / 5.2 * (X1 - X0)
        e_min, e_max = float(DI.error(np.linspace(-2.6, 2.6, 300)).min()), 3.4
        fy = lambda e: Y0 + (np.clip(e, e_min, e_max) - e_min) / (e_max - e_min) * (Y1 - Y0)
        xs = np.linspace(-2.6, 2.6, 200)
        colina = polilinea([[fx(x), fy(DI.error(x)), 0] for x in xs], color=NEG, width=5, opacity=0.9).set_z_index(5)
        self.add(aparece(colina, pel, 0.4))
        relleno = Polygon(*[[fx(x), fy(DI.error(x)), 0] for x in xs], [X1, Y0 - 0.3, 0], [X0, Y0 - 0.3, 0]).set_fill(NEG, 0.10).set_stroke(width=0).set_z_index(3)
        self.add(aparece(relleno, pel, 0.4))
        self.add(aparece(texto(est, "error", 30, est.tenue).move_to([X0 + 0.6, Y1 + 0.5, 0]).set_z_index(9), pel, 0.6))
        self.add(aparece(texto(est, "ajuste de los pesos", 28, est.tenue).move_to([X1 - 2.0, Y0 - 0.6, 0]).set_z_index(9), pel, 0.6))
        ruta = DI.descenso(x0=0.05, paso=0.12, n=40)
        T0, T1 = 5.5, 14.0
        idx = lambda: (pel.t - T0) / (T1 - T0) * (len(ruta) - 1)

        def x_actual():
            i = float(np.clip(idx(), 0, len(ruta) - 1))
            a = int(i); b = min(a + 1, len(ruta) - 1)
            return ruta[a] + (ruta[b] - ruta[a]) * suave(i - a)
        bola = punto(est.calido, 0.2)
        bola.add_updater(lambda m: fundir(m.move_to([fx(x_actual()), fy(DI.error(x_actual())) + 0.22, 0]), rampa(pel.t, 1.0, 0.5)))
        self.add(bola)
        tang = Line(LEFT, RIGHT, stroke_width=4, color=est.calido).set_z_index(6)

        def tg(m):
            x = x_actual(); d = DI.derivada(x)
            p = np.array([fx(x), fy(DI.error(x)), 0])
            esc = (Y1 - Y0) / (e_max - e_min) / ((X1 - X0) / 5.2)
            v = np.array([1, d * esc, 0]); v = v / np.linalg.norm(v) * 1.3
            m.put_start_and_end_on(p - v, p + v).set_stroke(opacity=0.85 * rampa(pel.t, 3.0) * (1 - rampa(pel.t, T1, 0.6)))
        tang.add_updater(tg)
        self.add(tang)
        self.add(Viva(est, lambda: f"error: {DI.error(x_actual()):.2f}", [3.6, 4.6, 0], 44, est.calido, f_op=lambda: rampa(pel.t, 1.0)))
        self.add(Viva(est, lambda: f"paso {int(np.clip(idx(), 0, len(ruta) - 1))}", [-3.6, 4.6, 0], 38, est.tinta, rol="cuerpo", f_op=lambda: rampa(pel.t, T0)))
        self.add(aparece(texto(est, "¡mínimo!", 36, POS, "cuerpo", "SEMIBOLD").move_to([fx(ruta[-1]), fy(DI.error(ruta[-1])) - 0.6, 0]).set_z_index(9), pel, T1))

        leyendas(self, est, pel, n, [
            ("Empieza adivinando… y se equivoca", "medimos qué tan grande es su error"),
            ("Ajusta sus pesos cuesta abajo", "como bajar una colina con niebla: paso a paso"),
            ("Repetirlo millones de veces es entrenar", "cada paso, un poco menos de error")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 3 · Las palabras como puntos en un mapa (embeddings) ═════════════════════════════════════════════════════════════

class ReelIaPalabras(Scene):
    VAR = 2

    def construct(self):
        n = "ReelIaPalabras"; TB = DI.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Las palabras como\npuntos en un mapa", self.VAR, chip_txt="Mapa ilustrativo", **SERIE)
        C = np.array([0.0, -0.2, 0]); K = 2.55
        P = lambda w: C + K * np.array([*AT.vector(w), 0])
        grupos = {"animales": (["gato", "perro", "felino", "pez"], POS), "personas": (["hombre", "mujer", "rey", "reina"], est.calido),
                  "cielo": (["sol", "luna"], "#FDE68A"), "dinero": (["dinero", "cliente", "comisiones"], NEG), "afuera": (["parque"], est.tenue)}
        k = 0
        for nombre, (pal, col) in grupos.items():
            for w in pal:
                t0 = 0.8 + 0.28 * k; k += 1
                g = VGroup(Dot(P(w), radius=0.11, color=col), texto(est, w, 30, col, "cuerpo", "SEMIBOLD").next_to(P(w), DOWN if w in ("felino", "reina", "luna") else UP, buff=0.12)).set_z_index(8)
                self.add(aparece(g, pel, t0))
        for nombre, (pal, col) in list(grupos.items())[:4]:
            pts = np.array([P(w) for w in pal])
            c = pts.mean(0); r = max(np.linalg.norm(pts - c, axis=1).max() + 0.7, 0.9)
            self.add(aparece(Circle(radius=r).move_to(c).set_stroke(col, 2.5).set_fill(col, 0.06).set_z_index(4), pel, 6.3))
        A1 = Arrow(P("hombre"), P("rey"), buff=0.12, stroke_width=6, color=est.calido, max_tip_length_to_length_ratio=0.25).set_z_index(9)
        A2 = Arrow(P("mujer"), P("mujer") + (P("rey") - P("hombre")), buff=0.12, stroke_width=6, color=POS, max_tip_length_to_length_ratio=0.25).set_z_index(9)
        self.add(aparece(A1, pel, 12.6), aparece(A2, pel, 13.6))
        anillo = Circle(radius=0.45).move_to(P("reina")).set_stroke(POS, 5).set_z_index(9)
        self.add(aparece(anillo, pel, 14.4))
        self.add(aparece(texto(est, "misma dirección: «realeza»", 30, est.tinta).move_to([0, -4.9, 0]).set_z_index(9), pel, 13.6))

        leyendas(self, est, pel, n, [
            ("Para una IA, cada palabra es un punto", "las parecidas quedan cerca"),
            ("El significado se vuelve geometría", "gato y perro juntos; sol y luna en otro barrio"),
            ("rey, menos hombre, más mujer: reina", "las relaciones son direcciones en el mapa")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 4 · ¿Cómo lee un modelo de lenguaje? (atención) ══════════════════════════════════════════════════════════════════

class ReelIaAtencion(Scene):
    VAR = 0

    def construct(self):
        n = "ReelIaAtencion"; TB = DI.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Cómo lee un modelo\nde lenguaje?", self.VAR, chip_txt="Ilustración", **SERIE)
        frases = [("el banco cobra comisiones al cliente", 1, 3.0, NEG, 1.0), ("me siento en el banco del parque", 4, -2.4, POS, 9.5)]
        for frase, iq, y, col, t0 in frases:
            pal = frase.split()
            fichas = VGroup(*[ficha(est, w, est.calido if i == iq else est.linea, 32) for i, w in enumerate(pal)]).arrange(RIGHT, buff=0.18)
            if fichas.width > 13.4:
                fichas.scale_to_fit_width(13.4)
            fichas.move_to([0, y, 0])
            self.add(aparece(fichas, pel, t0))
            pesos = AT.pesos_atencion(frase, iq)
            q = fichas[iq].get_top()
            for i, w in enumerate(pesos):
                if i == iq:
                    continue
                arco = ArcBetweenPoints(q + UP * 0.05, fichas[i].get_top() + UP * 0.05, angle=-PI * 0.55 if i > iq else PI * 0.55)
                arco.set_stroke(col, 2 + 22 * w, 0.25 + 0.75 * min(1, w * 3)).set_z_index(6)
                self.add(aparece(arco, pel, t0 + 1.5 + 0.15 * i))
                et = texto(est, f"{w * 100:.0f} %", 28, col if w > 0.15 else est.tenue, "cifra", "SEMIBOLD").next_to(fichas[i], DOWN, buff=0.22).set_z_index(9)
                self.add(aparece(et, pel, t0 + 2.6))
        self.add(aparece(texto(est, "banco = dinero", 40, NEG, "cuerpo", "SEMIBOLD").move_to([0, 0.6, 0]).set_z_index(9), pel, 6.0))
        self.add(aparece(texto(est, "banco = asiento", 40, POS, "cuerpo", "SEMIBOLD").move_to([0, -4.8, 0]).set_z_index(9), pel, 14.0))

        leyendas(self, est, pel, n, [
            ("Cada palabra mira a las demás", "y decide en cuáles fijarse: eso es «atención»"),
            ("«banco» con «cobra» y «comisiones»…", "…es el banco del dinero"),
            ("«banco» con «siento» y «parque»…", "…es el banco para sentarse")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 5 · Adivinar la siguiente palabra ════════════════════════════════════════════════════════════════════════════════

class ReelIaSiguiente(Scene):
    VAR = 1

    def construct(self):
        n = "ReelIaSiguiente"; TB = DI.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Adivinar la\nsiguiente palabra", self.VAR, chip_txt="Ilustración", **SERIE)
        frase = texto(est, DI.FRASE_SIG, 44, est.tinta, "cuerpo", "SEMIBOLD", ancho_max=11.0).move_to([-0.9, 4.2, 0]).set_z_index(9)
        self.add(aparece(frase, pel, 0.6))
        cursor = Rectangle(width=0.12, height=0.75).set_fill(est.calido, 1).set_stroke(width=0).next_to(frase, RIGHT, buff=0.2).set_z_index(9)
        cursor.add_updater(lambda m: fundir(m, rampa(pel.t, 0.6) * (1 - rampa(pel.t, 7.0, 0.2)) * (0.5 + 0.5 * np.sign(np.sin(6 * pel.v)))))
        fundir(cursor, 0)
        self.add(cursor)
        X0, BW = -2.2, 7.4
        for k, (w, p) in enumerate(DI.OPCIONES_SIG):
            y = 2.0 - 1.15 * k
            t0 = 2.0 + 0.4 * k
            col = POS if k == 0 else est.tenue
            self.add(aparece(texto(est, w, 36, est.tinta, "cuerpo", "SEMIBOLD").move_to([X0 - 0.35, y, 0], aligned_edge=RIGHT).set_z_index(9), pel, t0))
            self.add(aparece(Rectangle(width=BW, height=0.55).set_fill(est.linea, 0.5).set_stroke(width=0).move_to([X0 + BW / 2, y, 0]).set_z_index(5), pel, t0))
            b = Rectangle(width=0.01, height=0.55).set_z_index(6)
            b.add_updater(lambda m, p=p, y=y, t0=t0, col=col: m.become(Rectangle(width=max(BW * p * rampa(pel.t, t0 + 0.2, 1.2), 0.01), height=0.55)
                                                                         .set_fill(col, rampa(pel.t, t0)).set_stroke(width=0).move_to([X0, y, 0], aligned_edge=LEFT).set_z_index(6)))
            self.add(b)
            self.add(aparece(texto(est, f"{p * 100:.0f} %", 30, est.tinta, "cifra", "SEMIBOLD").move_to([X0 + BW * p + 0.75, y, 0]).set_z_index(9), pel, t0 + 1.2))
        elegida = ficha(est, "Tierra", POS, 44).set_z_index(10)
        destino = frase.get_right() + RIGHT * 1.35
        origen = np.array([X0 - 1.5, 2.0, 0])
        elegida.add_updater(lambda m: fundir(m.move_to(origen + (destino - origen) * suave((pel.t - 7.0) / 1.2)), rampa(pel.t, 6.6, 0.4)))
        fundir(elegida, 0)
        self.add(elegida)
        bucle = VGroup(Arc(radius=0.8, start_angle=0.3, angle=TAU - 0.9, stroke_width=6, color=est.calido).add_tip(tip_length=0.3),
                       ).move_to([0, -4.2, 0]).set_z_index(8)
        self.add(aparece(bucle, pel, 10.5))
        self.add(aparece(texto(est, "y otra vez, palabra por palabra", 32, est.tinta).move_to([0, -5.4, 0]).set_z_index(9), pel, 10.8))

        leyendas(self, est, pel, n, [
            ("Un chatbot no «sabe» la respuesta", "calcula qué palabra es más probable después"),
            ("Elige una y la agrega", "luego repite, palabra por palabra"),
            ("Por eso suena tan natural", "aprendió de muchísimos textos cómo seguimos una frase")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 6 · Para una IA, una foto son números ════════════════════════════════════════════════════════════════════════════

class ReelIaPixeles(Scene):
    VAR = 2

    def construct(self):
        n = "ReelIaPixeles"; TB = DI.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Para una IA, una\nfoto son números", self.VAR, chip_txt="Ilustración", **SERIE)
        Nn = 10
        yy, xx = np.mgrid[0:Nn, 0:Nn]
        img = np.clip(60 + 150 * np.exp(-((xx - 3.2) ** 2 + (yy - 3.0) ** 2) / 6) + 90 * np.exp(-((xx - 7) ** 2 + (yy - 6.5) ** 2) / 4) + 15 * np.sin(xx + 2 * yy), 0, 255).astype(int)
        L = 0.52; G0 = np.array([-5.6, 4.9, 0])
        celdas = VGroup()
        for i in range(Nn):
            for j in range(Nn):
                v = img[i, j] / 255
                celdas.add(Square(L).set_fill(interpolate_color(ManimColor("#0B0620"), ManimColor("#E9D5FF"), v), 1).set_stroke(est.fondo, 1.2)
                           .move_to(G0 + np.array([L * (j + 0.5), -L * (i + 0.5), 0])))
        celdas.set_z_index(6)
        self.add(aparece(celdas, pel, 0.5, 1.0))
        rejilla = VGroup(*[Line(G0 + RIGHT * L * k, G0 + RIGHT * L * k + DOWN * L * Nn) for k in range(Nn + 1)],
                         *[Line(G0 + DOWN * L * k, G0 + DOWN * L * k + RIGHT * L * Nn) for k in range(Nn + 1)]).set_stroke(est.tinta, 1.5).set_z_index(7)
        self.add(aparece(rejilla, pel, 3.0))
        Z = (3, 2)                                                         # ventana de 4×4 que se amplía
        marco = Square(4 * L).set_stroke(est.calido, 5).move_to(G0 + np.array([L * (Z[1] + 2), -L * (Z[0] + 2), 0])).set_z_index(8)
        self.add(aparece(marco, pel, 5.5))
        LZ = 0.98; Z0 = np.array([1.75, 4.9, 0])
        for i in range(4):
            for j in range(4):
                v = img[Z[0] + i, Z[1] + j]
                p = Z0 + np.array([LZ * (j + 0.5), -LZ * (i + 0.5), 0])
                sq = Square(LZ).set_fill(interpolate_color(ManimColor("#0B0620"), ManimColor("#E9D5FF"), v / 255), 1).set_stroke(est.calido, 2).move_to(p).set_z_index(6)
                num = texto(est, str(v), 30, est.tinta if v < 140 else "#120C24", "cifra", "SEMIBOLD").move_to(p).set_z_index(8)
                self.add(aparece(sq, pel, 6.2 + 0.05 * (i * 4 + j)), aparece(num, pel, 7.0 + 0.08 * (i * 4 + j)))
        self.add(aparece(DashedLine(marco.get_corner(UR), Z0, stroke_width=2.5, color=est.calido).set_z_index(7), pel, 6.0))
        self.add(aparece(DashedLine(marco.get_corner(DR), Z0 + DOWN * 4 * LZ, stroke_width=2.5, color=est.calido).set_z_index(7), pel, 6.0))
        self.add(aparece(texto(est, "0 = negro · 255 = blanco", 28, est.tenue).move_to([3.7, 0.4, 0]).set_z_index(9), pel, 7.8))
        cuenta = lambda: int(36_000_000 * rampa(pel.t, 11.8, 2.4))
        self.add(Viva(est, lambda: f"{cuenta():,}".replace(",", " "), [0, -2.4, 0], 96, est.calido, f_op=lambda: rampa(pel.t, 11.5)))
        self.add(aparece(texto(est, "números en una foto de celular", 34, est.tinta).move_to([0, -3.6, 0]).set_z_index(9), pel, 11.8))
        self.add(aparece(texto(est, "12 millones de píxeles × 3 colores", 30, est.tenue).move_to([0, -4.4, 0]).set_z_index(9), pel, 12.4))

        leyendas(self, est, pel, n, [
            ("Una imagen es una cuadrícula", "cada cuadrito es un píxel"),
            ("Cada píxel es un número", "uno por cada color: rojo, verde y azul"),
            ("Una foto: decenas de millones de números", "la IA busca patrones en todos ellos")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 7 · Memorizar no es aprender (sobreajuste) ═══════════════════════════════════════════════════════════════════════

class ReelIaMemoriza(Scene):
    VAR = 0

    def construct(self):
        n = "ReelIaMemoriza"; TB = DI.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Memorizar\nno es aprender", self.VAR, chip_txt="Ilustración", **SERIE)
        rng = np.random.default_rng(7)
        verdad = lambda x: 0.55 * np.sin(1.1 * x) + 0.12 * x
        xt = np.sort(rng.uniform(-2.8, 2.8, 11)); yt = verdad(xt) + rng.normal(0, 0.22, len(xt))
        xe = np.array([-2.45, -1.2, 0.35, 1.55, 2.6]); ye = verdad(xe) + rng.normal(0, 0.12, len(xe))
        X0, X1, Y0, Y1 = -6.1, 6.1, -4.7, 4.0
        fx = lambda x: X0 + (x + 3.1) / 6.2 * (X1 - X0)
        fy = lambda y: (Y0 + Y1) / 2 + np.clip(y, -1.6, 1.6) / 1.6 * (Y1 - Y0) / 2
        self.add(aparece(panel(est, X0 - 0.2, X1 + 0.2, Y0 - 0.3, Y1 + 0.3, 0.6), pel, 0.3))
        for k, (x, y) in enumerate(zip(xt, yt)):
            self.add(aparece(Dot([fx(x), fy(y), 0], radius=0.13, color=est.tinta).set_z_index(8), pel, 0.6 + 0.12 * k))
        xs = np.linspace(-3.0, 3.0, 300)
        suave_c = np.polyval(np.polyfit(xt, yt, 3), xs)
        memo = np.polyval(np.polyfit(xt, yt, len(xt) - 1), xs)
        for curva, col, t0, nombre, yl in ((suave_c, POS, 4.0, "entendió la tendencia", 4.55), (memo, est.calido, 6.5, "memorizó cada punto", 4.55)):
            c = VMobject().set_z_index(6)

            def dibujar(m, curva=curva, col=col, t0=t0):
                f = rampa(pel.t, t0, 1.8); k = max(int(len(xs) * f), 2)
                m.set_points_as_corners([[fx(x), fy(y), 0] for x, y in zip(xs[:k], curva[:k])]).set_stroke(col, 5, rampa(pel.t, t0, 0.2)).set_fill(opacity=0)
            c.add_updater(dibujar)
            dibujar(c)
            self.add(c)
        self.add(aparece(texto(est, "entendió la tendencia", 30, POS, "cuerpo", "SEMIBOLD").move_to([-3.3, Y1 + 0.75, 0]).set_z_index(9), pel, 4.0))
        self.add(aparece(texto(est, "memorizó cada punto", 30, est.calido, "cuerpo", "SEMIBOLD").move_to([3.3, Y1 + 0.75, 0]).set_z_index(9), pel, 6.5))
        for k, (x, y) in enumerate(zip(xe, ye)):
            g = VGroup(Square(0.3).rotate(PI / 4).set_fill("#FDE68A", 1).set_stroke(width=0).move_to([fx(x), fy(y), 0]))
            ym = float(np.polyval(np.polyfit(xt, yt, len(xt) - 1), x))
            g.add(DashedLine([fx(x), fy(y), 0], [fx(x), fy(ym), 0], stroke_width=3, color=ROJO))
            self.add(aparece(g.set_z_index(8), pel, 12.6 + 0.25 * k))
        self.add(aparece(texto(est, "examen: datos nuevos", 30, "#FDE68A", "cuerpo", "SEMIBOLD").move_to([0, Y0 - 0.85, 0]).set_z_index(9), pel, 12.6))

        leyendas(self, est, pel, n, [
            ("Dos alumnos estudian los mismos ejercicios", "uno entiende la idea; el otro memoriza"),
            ("En la práctica, los dos aciertan", "el que memoriza, incluso «mejor»"),
            ("En el examen, solo uno sale bien", "a eso se le llama sobreajuste")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 8 · Basura entra, basura sale (sesgo en los datos) ═══════════════════════════════════════════════════════════════

class ReelIaSesgo(Scene):
    VAR = 1

    def construct(self):
        n = "ReelIaSesgo"; TB = DI.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Basura entra,\nbasura sale", self.VAR, chip_txt="Ilustración", **SERIE)
        self.add(aparece(texto(est, "ejemplos para entrenar", 32, est.tenue).move_to([0, 4.9, 0]).set_z_index(9), pel, 0.5))
        for k in range(12):
            i, j = divmod(k, 6)
            g = gato("#FB923C" if k % 4 else "#F59E0B", 0.85).move_to([-5.4 + 2.15 * j, 3.6 - 1.5 * i, 0])
            self.add(aparece(g, pel, 0.6 + 0.15 * k))
        self.add(aparece(texto(est, "todos naranjas", 32, est.calido, "cuerpo", "SEMIBOLD").move_to([0, 1.5, 0]).set_z_index(9), pel, 3.2))
        caja = VGroup(RoundedRectangle(corner_radius=0.25, width=2.6, height=1.4).set_fill(NEG, 0.2).set_stroke(NEG, 3),
                      texto(est, "IA", 44, est.tinta, "titulo", "BOLD")).move_to([0, -0.4, 0]).set_z_index(8)
        self.add(aparece(caja, pel, 4.0))
        g_ok = gato("#FB923C", 1.1).move_to([-4.0, -3.0, 0]); g_mal = gato("#26262E", 1.1).move_to([4.0, -3.0, 0])
        g_mal[2].set_stroke("#9CA3AF", 2)
        self.add(aparece(g_ok, pel, 6.5), aparece(g_mal, pel, 9.5))
        self.add(aparece(texto(est, "gato: 98 %", 34, POS, "cuerpo", "SEMIBOLD").move_to([-4.0, -4.5, 0]).set_z_index(9), pel, 7.3))
        self.add(aparece(texto(est, "¿gato? 12 %", 34, ROJO, "cuerpo", "SEMIBOLD").move_to([4.0, -4.5, 0]).set_z_index(9), pel, 10.3))
        for p, t0 in (([-4.0, -1.9, 0], 6.8), ([4.0, -1.9, 0], 9.8)):
            self.add(aparece(Arrow(caja.get_bottom(), p, buff=0.15, stroke_width=4, color=est.tenue).set_z_index(7), pel, t0))

        leyendas(self, est, pel, n, [
            ("Una IA aprende de sus ejemplos", "si solo ve gatos naranjas…"),
            ("…un gato negro la confunde", "no es maldad: nunca vio uno"),
            ("Datos sesgados, respuestas sesgadas", "importa mucho con qué datos se entrena")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 9 · Cuando la IA inventa (alucinaciones) ═════════════════════════════════════════════════════════════════════════

class ReelIaInventa(Scene):
    VAR = 2

    def construct(self):
        n = "ReelIaInventa"; TB = DI.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Cuando la IA\ninventa", self.VAR, chip_txt="Ejemplo ilustrativo", **SERIE)
        q = burbuja(est, ["¿Quién fue el primer mexicano", "en el espacio?"], est.tenue, 9.6).move_to([1.6, 4.0, 0])
        self.add(aparece(q, pel, 0.5))
        r_lineas = ["Fue en 1969: viajó con Neil Armstrong", "a bordo del Apolo 11."]
        r = burbuja(est, r_lineas, NEG, 11.0).move_to([-0.9, 1.4, 0])
        texto_r = r[1]
        r[0].add_updater(lambda m: fundir(m, rampa(pel.t, 2.0)))
        fundir(r[0], 0)
        self.add(r[0])
        letras = [g for linea in texto_r for g in linea]
        for i, g in enumerate(letras):
            t_i = 2.3 + 2.6 * i / len(letras)
            g.add_updater(lambda m, t_i=t_i: m.set_opacity(rampa(pel.t, t_i, 0.05)))
            g.set_opacity(0)
        self.add(texto_r)
        sello = VGroup(RoundedRectangle(corner_radius=0.15, width=4.6, height=1.0).set_fill(est.fondo, 0.85).set_stroke(ROJO, 5),
                       texto(est, "INVENTADO", 44, ROJO, "titulo", "BOLD")).rotate(0.12).move_to([3.4, 0.2, 0]).set_z_index(10)
        self.add(aparece(sello, pel, 6.6, 0.3))
        v = burbuja(est, ["Verificado: Rodolfo Neri Vela, en 1985,", "a bordo del transbordador Atlantis."], POS, 11.4).move_to([0, -2.6, 0])
        self.add(aparece(v, pel, 12.6))
        palomita = VGroup(Line([-0.3, 0, 0], [-0.05, -0.28, 0], stroke_width=8, color=POS), Line([-0.05, -0.28, 0], [0.42, 0.3, 0], stroke_width=8, color=POS)).move_to([5.1, -1.35, 0]).set_z_index(10)
        self.add(aparece(palomita, pel, 13.2))
        self.add(aparece(texto(est, "fuente: NASA · Agencia Espacial Mexicana", 26, est.tenue).move_to([0, -4.4, 0]).set_z_index(9), pel, 13.4))

        leyendas(self, est, pel, n, [
            ("Suena seguro… y está mal", "eligió palabras probables, no verdaderas"),
            ("A esto se le llama «alucinación»", "no miente a propósito: no sabe que no sabe"),
            ("Verifica con fuentes confiables", "sobre todo nombres, fechas y cifras")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 10 · IA a bordo de un satélite (Φ-sat-1, ESA 2020) ═══════════════════════════════════════════════════════════════

class ReelIaEspacio(Scene):
    VAR = 0

    def construct(self):
        n = "ReelIaEspacio"; TB = DI.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "IA a bordo de\nun satélite", self.VAR, chip_txt="Hecho real · ESA 2020", **SERIE)
        SAT = np.array([0.0, 3.6, 0])
        sat = VGroup(Square(0.9).set_fill(est.fondo, 1).set_stroke(est.tinta, 3),
                     Rectangle(width=1.6, height=0.6).set_fill("#3B8FD9", 0.6).set_stroke(est.tinta, 2).shift(LEFT * 1.35),
                     Rectangle(width=1.6, height=0.6).set_fill("#3B8FD9", 0.6).set_stroke(est.tinta, 2).shift(RIGHT * 1.35),
                     texto(est, "IA", 30, NEG, "titulo", "BOLD")).move_to(SAT).set_z_index(9)
        self.add(aparece(sat, pel, 0.4))
        cuerpo_ia = Square(0.9).move_to(SAT).set_stroke(NEG, 5).set_fill(opacity=0).set_z_index(10)
        cuerpo_ia.add_updater(lambda m: m.set_stroke(opacity=rampa(pel.t, 6.5) * (0.6 + 0.4 * np.sin(6 * pel.t))))
        self.add(cuerpo_ia)
        EST_P = np.array([0.0, -4.6, 0])
        antena = VGroup(Arc(radius=0.6, start_angle=PI + 0.5, angle=PI - 1.0, stroke_width=5, color=est.tinta).move_to(EST_P + UP * 0.5),
                        Line(EST_P, EST_P + UP * 0.45, stroke_width=5, color=est.tinta)).set_z_index(8)
        self.add(aparece(antena, pel, 0.6), aparece(texto(est, "estación en tierra", 28, est.tenue).move_to(EST_P + RIGHT * 2.6 + UP * 0.3).set_z_index(9), pel, 0.8))
        rng = np.random.default_rng(31)

        def foto(nublada, sem):
            r = np.random.default_rng(sem)
            yy, xx = np.mgrid[0:40, 0:40] / 40
            from scipy.ndimage import gaussian_filter
            tierra_ = gaussian_filter(r.random((40, 40)), 3); tierra_ = (tierra_ - tierra_.min()) / (np.ptp(tierra_) + 1e-9)
            rgb = np.stack([60 + 90 * tierra_, 90 + 80 * tierra_, 50 + 30 * tierra_], -1)
            if nublada:
                nube = gaussian_filter(r.random((40, 40)), 4); nube = np.clip((nube - nube.mean()) / nube.std() * 0.6 + 0.85, 0, 1)
                rgb = rgb * (1 - nube[..., None]) + 245 * nube[..., None]
            im = ImageMobject(rgb.astype(np.uint8)).set_z_index(7)
            im.stretch_to_fit_width(1.1).stretch_to_fit_height(1.1)
            return im
        nub = [True, True, False, True, True, False, True, True, True, False, True, False]
        for k, nb in enumerate(nub):
            im = foto(nb, 100 + k)
            t0 = 1.0 + 1.05 * k
            lado = (-1, 1)[k % 2]

            def mover(m, t0=t0, nb=nb, lado=lado):
                e = pel.t - t0
                if e < 0 or pel.t <= 0:
                    m.set_opacity(0); return
                inicio = np.array([lado * 5.6, 0.6, 0])
                if e < 0.8:
                    p = inicio + (SAT - inicio) * suave(e / 0.8); op = 1.0
                elif pel.t < 6.5 or not nb:
                    if pel.t < 6.5:                                      # antes de la IA: todo se manda a tierra
                        f = suave((e - 0.8) / 1.0); p = SAT + (EST_P + UP * 1.2 - SAT) * f; op = 1 - max(0, (e - 1.6) / 0.3)
                    else:
                        f = suave((e - 0.8) / 1.0); p = SAT + (EST_P + UP * 1.2 - SAT) * f; op = 1 - max(0, (e - 1.6) / 0.3)
                else:                                                    # nublada con la IA activa: se descarta
                    f = suave((e - 0.8) / 0.8); p = SAT + np.array([lado * 3.4 * f, 1.0 * f, 0]); op = 1 - f
                m.move_to(p).set_opacity(max(0, min(1, op)))
            im.add_updater(mover)
            self.add(im)
        self.add(aparece(texto(est, "nubladas: a la basura", 32, ROJO, "cuerpo", "SEMIBOLD").move_to([-3.9, 5.15, 0]).set_z_index(9), pel, 7.5))
        self.add(aparece(texto(est, "despejadas: a tierra", 32, VERDE, "cuerpo", "SEMIBOLD").move_to([0, -2.4, 0]).set_z_index(9), pel, 9.0))
        self.add(aparece(texto(est, "2 de cada 3 lugares, bajo nubes", 30, est.tinta).move_to([0, 1.2 - 0.0, 0]).set_z_index(9), pel, 1.6, hasta=6.3))

        leyendas(self, est, pel, n, [
            ("Dos tercios de la Tierra están bajo nubes", "muchas fotos desde el espacio salen blancas"),
            ("Una IA a bordo las revisa", "y descarta las nubladas antes de enviarlas"),
            ("Menos datos inútiles por la antena", "lo hizo el satélite Φ-sat-1 de la ESA en 2020")])
        cerrar_serie(self, est, pel, self.VAR)

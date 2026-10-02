import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from marca_aerospace import (CIAN, FONDO, PAPEL, LogoCoDe, animar_entrada, animar_salida,
                             marca_agua_aerospace, sting_logo)
from marca_vertical import (AZUL_CLARO, capitulo_vertical, cierre_vertical, cortinilla_vertical,
                            entrar_tarjeta_vertical, fondo_reel, marco, tarjeta_vertical, tercio_vertical)
from marca_vertical import _texto
from rotulos_aerospace import (animar_cierre, entrar_capitulo, entrar_tercio, salir_tercio)

# Reels 9:16 (renderizar con -r 1080,1920). Mismos tiempos que los videos horizontales de la marca:
# el audio de sonido_marca.py sirve igual. Ver marca_vertical.py para el porqué de cada decisión.

Y_LOGO = 1.6          # centro del logo: un poco sobre el centro, deja sitio al sitio web en la zona segura


def _logo(escena, color="plata", y=Y_LOGO, ancho=0.86):
    W, _ = marco(escena)
    return LogoCoDe(altura=W * ancho / 1.05, color=color).mover_a(UP * y)


def _sitio(escena, color=CIAN, y=6.4):
    W, _ = marco(escena)
    t = _texto("codeaerospace.com", 44, "MEDIUM", color, tracking=0.08, ancho_max=W * 0.8)
    return t.move_to(DOWN * y)


class ReelIntro(Scene):
    """Entrada orbital a pantalla completa: tres órbitas gigantes se dibujan con cometa de arriba abajo
    mientras el logo se arma al centro; al final aparece el sitio (≈9.3 s)."""

    def construct(self):
        self.camera.background_color = FONDO
        fondo_reel(self)
        logo = _logo(self)
        animar_entrada(self, logo, estilo="orbital")
        sitio = _sitio(self)
        self.play(FadeIn(sitio, shift=0.2 * UP), run_time=0.7)
        self.wait(1.6)


class ReelIntroClaro(Scene):
    def construct(self):
        self.camera.background_color = PAPEL
        fondo_reel(self, claro=True)
        logo = _logo(self, color="negro")
        animar_entrada(self, logo, estilo="orbital", acento=AZUL_CLARO)
        sitio = _sitio(self, color=AZUL_CLARO)
        self.play(FadeIn(sitio, shift=0.2 * UP), run_time=0.7)
        self.wait(1.6)


class ReelTrazo(Scene):
    """Todo se traza y se rellena a la vez (≈2.6 s) sobre las órbitas gigantes."""

    def construct(self):
        self.camera.background_color = FONDO
        fondo_reel(self)
        logo = _logo(self)
        animar_entrada(self, logo, estilo="trazo")
        self.wait(1.2)


class ReelEnsamble(Scene):
    """Las partes llegan desde los bordes de la pantalla (arriba, abajo y los lados) y encajan (≈2.4 s)."""

    def construct(self):
        self.camera.background_color = FONDO
        fondo_reel(self)
        logo = _logo(self)
        W, H = marco(self)
        partes = [(logo.orbitas, UP * 0.55 + LEFT * 0.4), (logo.luna, UP * 0.6 + RIGHT * 0.7), (logo.satelite, UP * 0.7),
                  (logo.co, LEFT * 1.1), (logo.punto, DOWN * 0.5 + RIGHT * 0.3), (logo.de, RIGHT * 1.1),
                  (logo.aerospace, DOWN * 0.7)]
        anims = []
        for p, d in partes:
            lejos = np.array([d[0] * W, d[1] * H, 0]) * 0.9
            anims.append(FadeIn(p, target_position=p.get_center() + lejos, scale=0.6))
        self.play(LaggedStart(*anims, lag_ratio=0.12, run_time=2.4, rate_func=rate_functions.ease_out_cubic))
        from marca_aerospace import _fijar_contorno
        _fijar_contorno(self, logo)
        self.wait(1.2)


class ReelSting(Scene):
    """Ultra corto (≈2 s) para abrir o cortar un reel."""

    def construct(self):
        self.camera.background_color = FONDO
        fondo_reel(self, entrada=False)
        logo = _logo(self)
        sting_logo(self, logo)
        self.wait(0.4)


class ReelCierre(Scene):
    """Cierre de reel: el logo grande con el sitio debajo, y la salida (≈6.2 s)."""

    def construct(self):
        self.camera.background_color = FONDO
        fondo_reel(self)
        t = cierre_vertical(self)
        animar_entrada(self, t.logo, estilo="trazo", ritmo=0.8)
        self.play(FadeIn(t.textos[0], shift=0.2 * UP), run_time=0.7)
        self.wait(1.6)
        animar_salida(self, t.logo)
        self.play(FadeOut(t.textos), run_time=0.4)
        self.wait(0.3)


class ReelMarcaDeAgua(Scene):
    """La marca de agua sobre contenido vertical: chica, arriba a la izquierda (dentro de la zona segura,
    lejos de los botones) y por encima de todo; el satélite da una vuelta por una órbita de todo el alto."""

    def construct(self):
        self.camera.background_color = FONDO
        W, H = marco(self)
        orbita = Ellipse(width=W * 0.86, height=H * 0.72, color=BLUE_D, stroke_width=3)
        sat = Dot(color=CIAN, radius=0.14).move_to(orbita.point_from_proportion(0))
        marca = marca_agua_aerospace(altura=1.5)
        marca.move_to([-W / 2 + 0.7 + marca.width / 2, H / 2 - 3.3 - marca.height / 2, 0])
        self.add(fondo_reel(self, entrada=False), orbita, sat, marca)
        self.play(MoveAlongPath(sat, orbita), run_time=4, rate_func=linear)


class ReelRotulos(Scene):
    """El juego de rótulos en vertical (≈14.3 s, mismos tiempos que el horizontal): portada con el emblema
    arriba, tercio inferior ancho, cortinilla que cruza todo el alto, capítulo con numeral enorme y cierre."""

    def construct(self):
        self.camera.background_color = FONDO
        fondo_reel(self)
        portada = tarjeta_vertical(self, "Redes no terrestres", "Satélites, 6G y la ventana de contacto",
                                   antetitulo="Seminario · Co.De Aerospace")
        entrar_tarjeta_vertical(self, portada)
        self.wait(1.0)
        quien = tercio_vertical(self, "Alan Rosas Palacios", "Co.De Aerospace")
        entrar_tercio(self, quien)
        self.wait(1.4)
        salir_tercio(self, quien)
        cortinilla_vertical(self, portada, VGroup())
        cap = capitulo_vertical(self, 1, "La órbita baja")
        entrar_capitulo(self, cap)
        self.wait(1.0)
        self.play(FadeOut(cap), run_time=0.5)
        animar_cierre(self, cierre_vertical(self), espera=1.2)

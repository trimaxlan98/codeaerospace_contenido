import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from code_brand import registrar_fuentes
from marca_aerospace import (CIAN, FONDO, PAPEL, LogoCoDe, animar_entrada, animar_salida,
                             marca_agua_aerospace, sting_logo)

registrar_fuentes()          # Montserrat (LogoCoDeCierre) está en manim_extensions/fonts, no en el sistema


class LogoCoDeIntro(Scene):
    """Demo de marca_aerospace.py: la entrada «orbital» del logo de Co.De Aerospace.

    Las seis órbitas se dibujan con un cometa cian en la punta (estelas.dibujar_con_cometa), la luna
    sube por su órbita y el satélite entra plegado por la órbita plana y despliega los paneles. CO.DE
    se traza y se rellena, el punto cae con rebote y AEROSPACE se abre hasta su tracking. Un destello
    recorre las órbitas y las letras. Al final las órbitas de trazo se cambian por su contorno exacto:
    el último cuadro es el logo oficial (IoU ≥ 0.95 con el PNG, lo mide la sonda de la marca).
    """

    def construct(self):
        self.camera.background_color = FONDO
        logo = LogoCoDe(altura=6.4)
        animar_entrada(self, logo, estilo="orbital")
        self.wait(1.6)


class LogoCoDeIntroClaro(Scene):
    """La misma entrada sobre papel, con el logo en una tinta (fondos claros, documentos)."""

    def construct(self):
        self.camera.background_color = PAPEL
        logo = LogoCoDe(altura=6.4, color="negro")
        animar_entrada(self, logo, estilo="orbital", acento="#0A84C6")
        self.wait(1.6)


class LogoCoDeTrazo(Scene):
    """Estilo «trazo»: todo se traza y se rellena a la vez, con desfase (≈2.6 s)."""

    def construct(self):
        self.camera.background_color = FONDO
        logo = LogoCoDe(altura=6.4)
        animar_entrada(self, logo, estilo="trazo")
        self.wait(1.2)


class LogoCoDeEnsamble(Scene):
    """Estilo «ensamble»: cada parte llega desde fuera y encaja en su lugar (≈2.4 s)."""

    def construct(self):
        self.camera.background_color = FONDO
        logo = LogoCoDe(altura=6.4)
        animar_entrada(self, logo, estilo="ensamble")
        self.wait(1.2)


class LogoCoDeSting(Scene):
    """Versión ultra corta para empezar o cortar un video (≈2 s)."""

    def construct(self):
        self.camera.background_color = FONDO
        logo = LogoCoDe(altura=6.4)
        sting_logo(self, logo)
        self.wait(0.4)


class LogoCoDeCierre(Scene):
    """Cierre de video: el logo con el sitio debajo, y la salida."""

    def construct(self):
        self.camera.background_color = FONDO
        logo = LogoCoDe(altura=5.2).shift(0.45 * UP)
        animar_entrada(self, logo, estilo="trazo", ritmo=0.8)
        sitio = Text("codeaerospace.com", font="Montserrat", weight=MEDIUM, font_size=26, color=CIAN)
        sitio.next_to(logo, DOWN, buff=0.35)
        self.play(FadeIn(sitio, shift=0.12 * UP), run_time=0.7)
        self.wait(1.6)
        animar_salida(self, logo)
        self.play(FadeOut(sitio), run_time=0.4)
        self.wait(0.3)


class LogoCoDeVertical(Scene):
    """Entrada orbital para 9:16 (renderizar con -r 1080,1920): el logo ocupa el 86 % del ancho.

    Con -r, Manim conserva el ANCHO del cuadro (14.2 unidades) y estira el alto de la CÁMARA
    (config.frame_height se queda en 8): el tamaño sale del lado corto de la cámara para que la
    misma escena sirva en cualquier proporción.
    """

    def construct(self):
        self.camera.background_color = FONDO
        lado = min(self.camera.frame_width, self.camera.frame_height)
        logo = LogoCoDe(altura=lado * 0.86 / 1.05)
        animar_entrada(self, logo, estilo="orbital")
        self.wait(1.6)


class LogoCoDeMarcaDeAgua(Scene):
    """La marca de agua sobre contenido: chica, en la esquina y por encima de todo."""

    def construct(self):
        self.camera.background_color = FONDO
        orbita = Ellipse(width=9, height=3.4, color=BLUE_D, stroke_width=3)
        sat = Dot(color=CIAN).move_to(orbita.point_from_proportion(0))
        self.add(orbita, sat, marca_agua_aerospace())
        self.play(MoveAlongPath(sat, orbita), run_time=4, rate_func=linear)

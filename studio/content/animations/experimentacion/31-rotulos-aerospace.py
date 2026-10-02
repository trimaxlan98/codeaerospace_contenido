import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from marca_aerospace import FONDO
from rotulos_aerospace import (animar_cierre, capitulo, cierre_marca, cortinilla_orbital,
                               entrar_capitulo, entrar_tarjeta, entrar_tercio, salir_tercio,
                               tarjeta_titulo, tercio_inferior)


class DemoRotulosAerospace(Scene):
    """Demo de rotulos_aerospace.py: el juego completo de rótulos de Co.De Aerospace en un video.

    Portada (antetítulo cian, título plata, regla orbital que se dibuja con cometa), tercio inferior
    con el emblema, cortinilla orbital hacia un capítulo y el cierre con el logo y el sitio. Todo
    sale del logo: Montserrat, plata sobre #080F15 y el cian de codeaerospace.com como único acento.
    """

    def construct(self):
        self.camera.background_color = FONDO
        portada = tarjeta_titulo("Redes no terrestres", "Satélites, 6G y la ventana de contacto",
                                 antetitulo="Seminario · Co.De Aerospace")
        entrar_tarjeta(self, portada)
        self.wait(1.0)
        quien = tercio_inferior("Alan Rosas Palacios", "Co.De Aerospace")
        entrar_tercio(self, quien)
        self.wait(1.4)
        salir_tercio(self, quien)
        cortinilla_orbital(self, portada, VGroup())
        cap = capitulo(1, "La órbita baja")
        entrar_capitulo(self, cap)
        self.wait(1.0)
        self.play(FadeOut(cap), run_time=0.5)
        animar_cierre(self, cierre_marca(), espera=1.2)

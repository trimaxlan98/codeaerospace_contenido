import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from code_brand import (CODE_ACCENT, CODE_INK, CODE_MUTED, aplicar_marca,
                        etiqueta_hud, registrar_fuentes, titulo_marca)
from transiciones import DESCRIPCIONES, TRANSICIONES, transicion


class DemoTransiciones(Scene):
    """Demo de transiciones.py: las DIEZ transiciones del catalogo, una tras
    otra, sobre el mismo par de bloques.

    Cada pase enseña el nombre de la transicion y su linea de `DESCRIPCIONES`,
    asi que el video sirve de catalogo: se mira una vez y se sabe cual pedir.
    El orden va de la mas sutil (deslizar) a la mas invasiva (fundido_negro) y
    termina con las dos que trabajan sobre el contenido mismo.

    Detalle que no se ve pero decide: `conmutar` es un `Transform`, y Transform
    deja el objeto SALIENTE convertido en el destino. Por eso, tras ese pase,
    se sigue con el mismo objeto en vez de con el entrante — usar el entrante
    dejaria en escena un bloque que nunca se anadio.
    """

    # El orden del demo, no el del diccionario: de sutil a invasiva.
    ORDEN = ["deslizar", "empujar", "zoom", "difuminar", "persiana",
             "rejilla", "barrido", "fundido_negro", "conmutar", "trazar"]

    def bloque(self, n, color):
        """Una 'diapositiva' reconocible: un numero grande y su marco."""
        marco = RoundedRectangle(width=6.4, height=3.4, corner_radius=0.18,
                                 stroke_color=color, stroke_width=3,
                                 fill_opacity=0)
        num = titulo_marca(str(n), font_size=96, color=color)
        return VGroup(marco, num).move_to(ORIGIN)

    def pie(self, clave):
        """Nombre en ambar + para que sirve, abajo del cuadro."""
        n = etiqueta_hud(clave.replace("_", " "), font_size=17,
                         color=CODE_ACCENT)
        d = Text(DESCRIPCIONES[clave], color=CODE_MUTED, font_size=22)
        return VGroup(n, d).arrange(DOWN, buff=0.16).to_edge(DOWN, buff=0.5)

    def construct(self):
        registrar_fuentes()
        aplicar_marca(self)

        titulo = titulo_marca("Transiciones", font_size=40, color=CODE_INK)
        titulo.to_edge(UP, buff=0.45)
        self.add(titulo)

        actual = self.bloque(1, CODE_ACCENT)
        pie = self.pie(self.ORDEN[0])
        self.play(FadeIn(actual), FadeIn(pie), run_time=0.6)
        self.wait(0.4)

        for k, clave in enumerate(self.ORDEN):
            i = k + 2
            if k > 0:
                # El rotulo se releva ANTES del pase: durante la transicion ya
                # tiene que decir cual es. Se sustituye entero (no se anima uno
                # encima del otro) para que nunca se lean dos a la vez.
                nuevo_pie = self.pie(clave)
                self.play(FadeOut(pie, run_time=0.12))
                self.remove(pie)
                pie = nuevo_pie
                self.play(FadeIn(pie, run_time=0.12))

            entrante = self.bloque(i, CODE_ACCENT if i % 2 == 0 else CODE_INK)
            self.play(transicion(clave, actual, entrante), run_time=0.9)
            if clave != "conmutar":
                actual = entrante
            self.wait(0.35)

        cierre = etiqueta_hud(f"{len(TRANSICIONES)} transiciones", font_size=18,
                              color=CODE_ACCENT)
        cierre.next_to(actual, DOWN, buff=0.55)
        self.play(FadeOut(pie), FadeIn(cierre, shift=UP * 0.2), run_time=0.5)
        self.wait(1)

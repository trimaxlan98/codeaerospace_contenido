"""Transiciones de escena para encadenar "diapositivas" dentro de una Scene.

Manim no trae transiciones entre bloques de contenido; estas tres cubren el
90% de un video educativo. Todas reciben el grupo saliente y el entrante y
devuelven UNA animación para self.play(...); el entrante no necesita estar
añadido a la escena (la animación lo añade).

Uso:
    from transiciones import (transicion_deslizar, transicion_zoom,
                              transicion_persiana)
    self.play(transicion_deslizar(bloque1, bloque2, direccion=LEFT))
"""

from manim import (AnimationGroup, FadeIn, FadeOut, Rectangle, Succession,
                   config, LEFT, BLACK)


def transicion_deslizar(saliente, entrante, direccion=LEFT, distancia=1.6,
                        solape=0.15):
    """El contenido viejo sale empujado y el nuevo entra desde el lado
    opuesto, con un pequeño solape temporal."""
    return AnimationGroup(
        FadeOut(saliente, shift=direccion * distancia),
        FadeIn(entrante, shift=direccion * distancia),
        lag_ratio=solape,
    )


def transicion_zoom(saliente, entrante, factor=2.2):
    """El viejo 'atraviesa la cámara' (crece y se funde) y el nuevo emerge
    desde el fondo (nace pequeño)."""
    return AnimationGroup(
        FadeOut(saliente, scale=factor),
        FadeIn(entrante, scale=1 / factor),
        lag_ratio=0.2,
    )


def transicion_persiana(saliente, entrante, franjas=8, color=BLACK,
                        duracion_lado=0.6):
    """Franjas horizontales cubren la pantalla, el contenido se permuta
    detrás, y las franjas se retiran (persiana veneciana)."""
    alto = config.frame_height / franjas
    tiras = []
    for i in range(franjas):
        y = config.frame_height / 2 - alto * (i + 0.5)
        tira = Rectangle(width=config.frame_width + 0.2, height=alto + 0.02,
                         fill_color=color, fill_opacity=1, stroke_width=0)
        tira.move_to([0, y, 0]).stretch(0.001, dim=1)
        tira.set_z_index(50)
        tiras.append(tira)

    cubrir = AnimationGroup(
        *[t.animate.stretch_to_fit_height(alto + 0.02) for t in tiras],
        lag_ratio=0.07, run_time=duracion_lado)
    permutar = AnimationGroup(FadeOut(saliente), FadeIn(entrante),
                              run_time=0.05)
    descubrir = AnimationGroup(
        *[t.animate.stretch(0.001, dim=1).set_opacity(0) for t in tiras],
        lag_ratio=0.07, run_time=duracion_lado)
    return Succession(cubrir, permutar, descubrir)

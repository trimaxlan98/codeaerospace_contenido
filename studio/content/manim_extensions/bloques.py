"""Diagramas de bloques con flujo animado (pipelines, arquitecturas).

Bloques etiquetados + conectores que eligen solos el lado de salida/entrada
+ un flujo (destello) que recorre las conexiones en orden. Pensado para
diagramas de sistemas: sensor -> ADC -> DSP -> TX, capas de una red, etc.

Uso:
    from bloques import bloque, conectar, flujo
    b1, b2 = bloque("Sensor"), bloque("ADC", color=TEAL_B)
    b2.next_to(b1, RIGHT, buff=1.2)
    c = conectar(b1, b2)
    self.play(flujo([c]))
"""

from manim import (AnimationGroup, Arrow, RoundedRectangle, ShowPassingFlash,
                   Succession, Text, VGroup, BLUE_B, GREY_B, WHITE, YELLOW)


def bloque(texto, ancho=2.1, alto=0.85, color=BLUE_B, color_texto=WHITE,
           tamano=22, opacidad_relleno=0.12):
    """VGroup(caja, etiqueta) listo para next_to/shift como una unidad."""
    caja = RoundedRectangle(corner_radius=0.12, width=ancho, height=alto,
                            color=color, fill_color=color,
                            fill_opacity=opacidad_relleno, stroke_width=2.5)
    etiqueta = Text(texto, font_size=tamano, color=color_texto)
    if etiqueta.width > ancho * 0.86:
        etiqueta.scale_to_fit_width(ancho * 0.86)
    etiqueta.move_to(caja.get_center())
    return VGroup(caja, etiqueta)


def conectar(a, b, color=GREY_B, grosor=2.5, margen=0.12):
    """Flecha de `a` hacia `b` saliendo por el lado dominante (auto)."""
    delta = b.get_center() - a.get_center()
    if abs(delta[0]) >= abs(delta[1]):
        inicio, fin = (a.get_right(), b.get_left()) if delta[0] > 0 \
            else (a.get_left(), b.get_right())
    else:
        inicio, fin = (a.get_top(), b.get_bottom()) if delta[1] > 0 \
            else (a.get_bottom(), b.get_top())
    return Arrow(inicio, fin, buff=margen, color=color, stroke_width=grosor,
                 max_tip_length_to_length_ratio=0.14)


def flujo(conexiones, color=YELLOW, ancho=5, cola=0.45, por_conexion=0.55):
    """El destello recorre las conexiones EN ORDEN (Succession).

    `conexiones` es una lista de flechas/lineas (lo que devuelve conectar).
    Combina bien con Indicate sobre el bloque de llegada.
    """
    pasos = []
    for conexion in conexiones:
        copia = conexion.copy().set_fill(opacity=0).set_stroke(
            color=color, width=ancho, opacity=1)
        pasos.append(ShowPassingFlash(copia, time_width=cola,
                                      run_time=por_conexion))
    return Succession(*pasos)

"""Brillo y halos falsos para Manim CE (que no trae glow nativo en Cairo).

El truco: capas concéntricas del mismo trazo con ancho creciente y opacidad
decreciente. Barato de renderizar (pocas capas, sin shaders) y funciona con
cualquier VMobject: texto, órbitas, flechas.

Uso:
    from brillo import con_brillo, punto_brillante
    titulo = con_brillo(Text("SATCOM"), color=BLUE_B)
    sat = punto_brillante(color=YELLOW)
"""

from manim import VGroup, Circle, Dot, WHITE

CAPAS_DEFECTO = 5


def con_brillo(vmobject, color=None, capas=CAPAS_DEFECTO, ancho_max=14,
               opacidad=0.35):
    """Devuelve VGroup(halo..., vmobject): el objeto con un halo de su forma.

    `color` por defecto toma el color del propio objeto. `ancho_max` es el
    grosor de la capa más externa en unidades de stroke de Manim.
    """
    base = color if color is not None else vmobject.get_color()
    halo = VGroup()
    for i in range(capas, 0, -1):
        capa = vmobject.copy()
        capa.set_fill(opacity=0)
        capa.set_stroke(color=base, width=ancho_max * i / capas,
                        opacity=opacidad * (1 - (i - 1) / capas) ** 2)
        halo.add(capa)
    return VGroup(halo, vmobject)


def punto_brillante(punto=None, color=WHITE, radio=0.09, capas=6,
                    alcance=3.2, opacidad=0.6):
    """Un punto con halo radial (estrella, satélite, nodo activo).

    Devuelve VGroup(halos..., nucleo); el halo más externo llega a
    radio*alcance. Mover el grupo completo mueve el halo con el núcleo.
    """
    grupo = VGroup()
    for i in range(capas, 0, -1):
        r = radio * (1 + (alcance - 1) * i / capas)
        grupo.add(Circle(radius=r, stroke_width=0, fill_color=color,
                         fill_opacity=opacidad * (1 - i / (capas + 1)) ** 3))
    nucleo = Dot(radius=radio, color=color)
    grupo.add(nucleo)
    if punto is not None:
        grupo.move_to(punto)
    return grupo

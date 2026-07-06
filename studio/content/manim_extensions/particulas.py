"""Desintegración y materialización en partículas para Manim CE.

Las partículas se muestrean del contorno real del objeto (no de su caja),
con RNG de semilla fija: el mismo script produce siempre el mismo render
(importante para --disable_caching y para revisar diffs de video).

Uso:
    from particulas import Desintegrar, materializar
    self.play(Desintegrar(texto))            # texto -> polvo que se dispersa
    self.play(materializar(logo))            # polvo que converge -> logo
"""

import numpy as np

from manim import Dot, ReplacementTransform, Transform, VGroup

N_DEFECTO = 200


def particulas_de(mobject, n=N_DEFECTO, dispersion=1.4, semilla=7,
                  opacidad=0.0, radio=0.025):
    """VGroup de n puntos muestreados del contorno de `mobject`, desplazados
    radialmente al azar hasta `dispersion` unidades, con la opacidad dada."""
    rng = np.random.default_rng(semilla)
    familia = [m for m in mobject.family_members_with_points()]
    if not familia:
        familia = [mobject]
    centro = mobject.get_center()
    puntos = VGroup()
    for i in range(n):
        miembro = familia[i % len(familia)]
        base = miembro.point_from_proportion(float(rng.random()))
        direccion = base - centro
        norma = np.linalg.norm(direccion)
        unidad = direccion / norma if norma > 1e-6 else rng.normal(size=3) * [1, 1, 0]
        destino = base + unidad * dispersion * float(rng.random())
        color = miembro.get_color()
        puntos.add(Dot(destino, radius=radio, color=color,
                       fill_opacity=opacidad, stroke_width=0))
    return puntos


class Desintegrar(Transform):
    """El objeto se disuelve en partículas que se dispersan y desvanecen.

    Tras la animación el mobject queda en escena con apariencia invisible
    (polvo con opacidad 0); hacerle FadeOut/remove si estorba.
    """

    def __init__(self, mobject, n=N_DEFECTO, dispersion=1.4, semilla=7,
                 **kwargs):
        objetivo = particulas_de(mobject, n=n, dispersion=dispersion,
                                 semilla=semilla, opacidad=0.0)
        super().__init__(mobject, objetivo, **kwargs)


def materializar(mobject, n=N_DEFECTO, dispersion=1.4, semilla=7, **kwargs):
    """Animación: polvo visible que converge y se convierte en `mobject`.

    Devuelve un ReplacementTransform listo para self.play(...); no hace
    falta añadir nada a la escena antes.
    """
    origen = particulas_de(mobject, n=n, dispersion=dispersion,
                           semilla=semilla, opacidad=0.85)
    return ReplacementTransform(origen, mobject, **kwargs)

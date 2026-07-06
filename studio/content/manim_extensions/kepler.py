"""Órbitas keplerianas físicamente correctas para Manim CE.

MoveAlongPath recorre una elipse a rapidez constante de arco — un satélite
real NO hace eso: acelera en el perigeo y frena en el apogeo (2ª ley de
Kepler). Aquí se resuelve la ecuación de Kepler (M = E - e·sen E) por
Newton-Raphson en cada frame, así que el movimiento sí barre áreas iguales
en tiempos iguales.

Uso:
    from kepler import OrbitaKepler, MoverKepler
    orbita = OrbitaKepler(a=3.0, e=0.65)
    self.add(orbita, sat)
    self.play(MoverKepler(sat, orbita, vueltas=1), run_time=8)
"""

import numpy as np

from manim import (Animation, Dot, Ellipse, VGroup, YELLOW, BLUE_B,
                   linear)


class OrbitaKepler(VGroup):
    """Elipse orbital con el cuerpo central en el foco (origen del grupo).

    a = semieje mayor (unidades de escena), e = excentricidad [0, 1).
    El perigeo queda a la derecha del foco (+X); `posicion(f)` devuelve el
    punto de la órbita en la fracción f del período (f=0 -> perigeo).
    """

    def __init__(self, a=3.0, e=0.6, color=BLUE_B, color_foco=YELLOW,
                 mostrar_foco=True, **kwargs):
        super().__init__(**kwargs)
        if not 0 <= e < 1:
            raise ValueError("la excentricidad debe estar en [0, 1)")
        self.a = a
        self.e = e
        self.b = a * np.sqrt(1 - e * e)
        self.trayectoria = Ellipse(width=2 * a, height=2 * self.b,
                                   color=color).shift(np.array([-a * e, 0, 0]))
        self.add(self.trayectoria)
        if mostrar_foco:
            self.foco = Dot(radius=0.07, color=color_foco)
            self.add(self.foco)

    def posicion(self, fraccion_periodo):
        """Punto (relativo al centro del grupo) en la fracción del período."""
        M = 2 * np.pi * (fraccion_periodo % 1.0)  # anomalia media
        E = M if self.e < 0.8 else np.pi          # anomalia excentrica
        for _ in range(12):
            E -= (E - self.e * np.sin(E) - M) / (1 - self.e * np.cos(E))
        local = np.array([self.a * (np.cos(E) - self.e),
                          self.b * np.sin(E), 0.0])
        return self._foco_absoluto() + local

    def _foco_absoluto(self):
        """El foco vive en el centro de la elipse + a·e en +X del grupo."""
        return self.trayectoria.get_center() + np.array([self.a * self.e, 0, 0])


class MoverKepler(Animation):
    """Mueve un mobject por la órbita a velocidad kepleriana real."""

    def __init__(self, mobject, orbita: OrbitaKepler, vueltas=1.0,
                 fase_inicial=0.0, **kwargs):
        self.orbita = orbita
        self.vueltas = vueltas
        self.fase_inicial = fase_inicial
        kwargs.setdefault("rate_func", linear)
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        f = self.fase_inicial + self.rate_func(alpha) * self.vueltas
        self.mobject.move_to(self.orbita.posicion(f))

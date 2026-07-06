"""Figuras "3D" dibujadas en 2D, como un profesor en el pizarrón.

NO usa ThreeDScene ni renderizado 3D: es proyección oblicua (cabinet) sobre
VMobjects planos. Convención: x -> derecha, z -> arriba, y -> profundidad
(se dibuja en diagonal). Ideal para superficies de pérdida (ML), campos,
sólidos geométricos y cualquier boceto técnico.

Uso:
    from pizarra3d import (proyectar, ejes_pizarra, malla_superficie,
                           curva_3d, cubo_pizarra, esfera_pizarra)
    ejes = ejes_pizarra()
    silla = malla_superficie(lambda x, y: 0.3 * (x * x - y * y))
    self.play(Create(ejes), Create(silla, run_time=3))
"""

import numpy as np

from manim import (Arrow, DashedVMobject, Text, VGroup, VMobject,
                   interpolate_color, BLUE_B, GREY_B, WHITE, YELLOW, DEGREES)

ANGULO_PROF = 38 * DEGREES   # direccion en pantalla del eje de profundidad
FACTOR_PROF = 0.55           # acortamiento del eje de profundidad (cabinet)


def proyectar(punto, angulo=ANGULO_PROF, factor=FACTOR_PROF):
    """(x, y, z) del mundo -> punto 2D de pantalla. y es la profundidad."""
    x, y, z = float(punto[0]), float(punto[1]), float(punto[2])
    return np.array([x + factor * np.cos(angulo) * y,
                     z + factor * np.sin(angulo) * y, 0.0])


def curva_3d(fn, t_min=0.0, t_max=1.0, muestras=64, color=WHITE, grosor=2.5,
             suave=True, **kwargs):
    """VMobject con la proyección de la curva paramétrica fn(t)->(x,y,z)."""
    puntos = [proyectar(fn(t))
              for t in np.linspace(t_min, t_max, muestras)]
    curva = VMobject(color=color, stroke_width=grosor, **kwargs)
    if suave:
        curva.set_points_smoothly(puntos)
    else:
        curva.set_points_as_corners(puntos)
    return curva


def ejes_pizarra(longitud=2.6, color=GREY_B, etiquetas=("x", "y", "z"),
                 tamano=22):
    """Tres flechas desde el origen: x (derecha), y (diagonal), z (arriba)."""
    origen = np.zeros(3)
    destinos = [(longitud, 0, 0), (0, longitud, 0), (0, 0, longitud)]
    grupo = VGroup()
    for destino, nombre in zip(destinos, etiquetas):
        punta = proyectar(destino)
        flecha = Arrow(origen, punta, buff=0, color=color, stroke_width=2.5,
                       max_tip_length_to_length_ratio=0.08)
        tag = Text(nombre, font_size=tamano, color=color)
        tag.move_to(punta * 1.12 + np.array([0.05, 0.12, 0]))
        grupo.add(flecha, tag)
    return grupo


def malla_superficie(f, x_range=(-2.0, 2.0), y_range=(-2.0, 2.0),
                     lineas=9, muestras=28, color_bajo=BLUE_B,
                     color_alto=YELLOW, grosor=1.8):
    """Malla de la superficie z = f(x, y) proyectada al plano.

    Devuelve VGroup de polilíneas (const-y y const-x) ordenadas de atrás
    hacia adelante, coloreadas por altura media (bajo->alto).
    """
    xs = np.linspace(*x_range, muestras)
    ys = np.linspace(*y_range, muestras)
    zs = [[f(x, y) for x in xs] for y in ys]
    z_min = min(min(fila) for fila in zs)
    z_max = max(max(fila) for fila in zs)
    rango = (z_max - z_min) or 1.0

    def color_de(z_medio):
        return interpolate_color(color_bajo, color_alto,
                                 (z_medio - z_min) / rango)

    malla = VGroup()
    # Lineas de y constante (de la mas lejana a la mas cercana)
    for y in reversed(np.linspace(*y_range, lineas)):
        pts = [proyectar((x, y, f(x, y))) for x in xs]
        z_medio = float(np.mean([f(x, y) for x in xs]))
        linea = VMobject(stroke_width=grosor, color=color_de(z_medio))
        linea.set_points_smoothly(pts)
        malla.add(linea)
    # Lineas de x constante
    for x in np.linspace(*x_range, lineas):
        pts = [proyectar((x, y, f(x, y))) for y in reversed(ys)]
        z_medio = float(np.mean([f(x, y) for y in ys]))
        linea = VMobject(stroke_width=grosor, color=color_de(z_medio))
        linea.set_points_smoothly(pts)
        malla.add(linea)
    return malla


def cubo_pizarra(lado=1.8, color=WHITE, grosor=2.2, trazos_ocultos=9):
    """Cubo alámbrico: aristas visibles sólidas, ocultas discontinuas."""
    h = lado / 2
    v = {s: proyectar(p) for s, p in {
        "abd": (-h, -h, -h), "abt": (-h, h, -h), "adb": (h, -h, -h),
        "adt": (h, h, -h), "arf": (-h, -h, h), "art": (-h, h, h),
        "arg": (h, -h, h), "arh": (h, h, h)}.items()}

    def arista(a, b, oculta=False):
        seg = VMobject(color=color, stroke_width=grosor)
        seg.set_points_as_corners([v[a], v[b]])
        if oculta:
            return DashedVMobject(seg, num_dashes=trazos_ocultos)
        return seg

    visibles = [("abd", "adb"), ("abd", "arf"), ("adb", "arg"),
                ("arf", "arg"), ("arf", "art"), ("arg", "arh"),
                ("art", "arh"), ("adb", "adt"), ("adt", "arh")]
    ocultas = [("abd", "abt"), ("abt", "adt"), ("abt", "art")]
    return VGroup(*[arista(a, b) for a, b in visibles],
                  *[arista(a, b, oculta=True) for a, b in ocultas])


def esfera_pizarra(radio=1.3, color=WHITE, grosor=2.2, trazos=12):
    """Esfera de pizarrón: contorno + ecuador (mitad trasera discontinua)."""
    contorno = curva_3d(
        lambda t: (radio * np.cos(t), 0, radio * np.sin(t)),
        0, 2 * np.pi, color=color, grosor=grosor)
    # Ecuador en el plano z=0: la mitad cercana (y<0) solida, lejana dashed
    cercana = curva_3d(
        lambda t: (radio * np.cos(t), radio * np.sin(t), 0),
        np.pi, 2 * np.pi, color=color, grosor=grosor * 0.8)
    lejana = DashedVMobject(curva_3d(
        lambda t: (radio * np.cos(t), radio * np.sin(t), 0),
        0, np.pi, color=color, grosor=grosor * 0.7), num_dashes=trazos)
    return VGroup(contorno, cercana, lejana)

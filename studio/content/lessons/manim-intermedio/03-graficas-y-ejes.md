---
title: Gráficas y ejes
level: medio
summary: Axes y NumberPlane para graficar funciones y datos — el pan de cada día en ciencia de datos y telecomunicaciones — con etiquetas, áreas y puntos móviles.
tags: [axes, plot, graficas, datos]
minutes: 10
order: 3
---

## Axes: el sistema de coordenadas

```python
ejes = Axes(
    x_range=[0, 10, 2],        # min, max, paso de marcas
    y_range=[0, 1.2, 0.5],
    x_length=8, y_length=4,    # tamaño EN PANTALLA (unidades manim)
    axis_config={"color": GREY_B, "include_tip": True},
).shift(DOWN * 0.4)
etiq_x = ejes.get_x_axis_label(Text("t (ms)", font_size=20))
etiq_y = ejes.get_y_axis_label(Text("amplitud", font_size=20))
self.play(Create(ejes), FadeIn(etiq_x), FadeIn(etiq_y), run_time=1.5)
```

Clave: `x_range` habla en unidades **de datos**; `x_length` en unidades **de pantalla**. `ejes.c2p(x, y)` (coords→punto) convierte de datos a pantalla — es el pegamento con el resto de Manim:

```python
marcador = Dot(ejes.c2p(3, 0.8), color=YELLOW)
```

## Graficar funciones

```python
senal = ejes.plot(lambda t: np.exp(-t / 4) * np.sin(3 * t) * 0.5 + 0.5,
                  x_range=[0, 10], color=TEAL_B)
self.play(Create(senal), run_time=2)

area = ejes.get_area(senal, x_range=[2, 6], color=BLUE_B, opacity=0.3)
self.play(FadeIn(area))
```

Para datos discretos (puntos medidos), dibuja `Dot`s con `c2p` y únelos con una `VMobject`:

```python
puntos = [(0, 0.1), (2, 0.5), (4, 0.42), (6, 0.8), (8, 0.75)]
linea = VMobject(color=YELLOW).set_points_as_corners(
    [ejes.c2p(x, y) for x, y in puntos])
marcas = VGroup(*[Dot(ejes.c2p(x, y), radius=0.05) for x, y in puntos])
```

## Punto que recorre una curva + lectura en vivo

```python
x = ValueTracker(0)
punto = always_redraw(lambda: Dot(
    ejes.c2p(x.get_value(), f(x.get_value())), color=YELLOW))
lectura = always_redraw(lambda: DecimalNumber(
    f(x.get_value()), num_decimal_places=2, font_size=30
).next_to(punto, UR, buff=0.15))
self.add(punto, lectura)
self.play(x.animate.set_value(10), run_time=4, rate_func=linear)
```

Este trío (Axes + ValueTracker + always_redraw) cubre la mayoría de las visualizaciones de ciencia de datos: curvas de entrenamiento, señales, distribuciones que evolucionan.

## NumberPlane

`NumberPlane()` es un plano cuadriculado completo (fondo tipo "papel milimetrado") — útil para geometría y campos vectoriales. Baja la opacidad de la rejilla para que no compita con el contenido: `NumberPlane(background_line_style={"stroke_opacity": 0.25})`.

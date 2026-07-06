---
title: Mobjects y posicionamiento
level: intro
summary: Las figuras y textos básicos, el sistema de coordenadas de la pantalla y las cuatro herramientas de posicionamiento que resuelven casi cualquier layout.
tags: [mobjects, posicionamiento, coordenadas, text]
minutes: 10
order: 2
---

## El lienzo

La pantalla mide ~14.2 unidades de ancho por 8 de alto, con el origen `ORIGIN` al centro. Las constantes `UP`, `DOWN`, `LEFT`, `RIGHT` son vectores unitarios; se combinan y escalan: `UP * 2 + RIGHT * 3` es el punto (3, 2).

## Los mobjects que más vas a usar

```python
Text("Título", font_size=34, color=GOLD)      # texto plano (fuente del sistema)
MathTex(r"E = mc^2", font_size=48)            # fórmula LaTeX (usa r"...")
Circle(radius=1, color=BLUE)                  # también Square, Rectangle, Ellipse
Line(ORIGIN, RIGHT * 3)                       # y DashedLine, Arrow
Dot([1, 2, 0], radius=0.06, color=YELLOW)     # un punto
Arc(radius=2, start_angle=0, angle=PI / 2)    # arco de circunferencia
Star(n=5, outer_radius=1)                     # estrella
```

Estilo: casi todos aceptan `color`, `fill_color` + `fill_opacity` (relleno) y `stroke_width` + `stroke_opacity` (trazo). Un `Circle` sin `fill_opacity` es solo contorno.

## Las cuatro herramientas de posicionamiento

```python
titulo.to_edge(UP)                 # 1. pegar a un borde de pantalla
caja.move_to([2, -1, 0])           # 2. posición absoluta (o al centro de otro mobject)
etiqueta.next_to(caja, DOWN, buff=0.3)   # 3. relativo a otro mobject
figura.shift(RIGHT * 0.5)          # 4. desplazamiento relativo a donde está
```

Con `to_edge` para el título, `next_to` para etiquetas y `move_to`/`shift` para el resto, se resuelve el 95% de los layouts. También útiles: `to_corner(UR)`, `align_to(otro, LEFT)`, `get_center()`, `get_top()`, `get_right()`… (devuelven puntos que puedes usar en `Line`, `Arrow`, etc.).

## Tamaño

```python
logo.scale(1.5)                        # multiplicativo
etiqueta.scale_to_fit_width(2.0)       # ajustar a un ancho concreto
```

`mobject.width` y `mobject.height` se leen — útil para decidir si algo cabe.

## Patrón de escena típico del canal

```python
from manim import *


class Ejemplo(Scene):
    def construct(self):
        titulo = Text("Tema de hoy", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        figura = Circle(radius=1.4, color=BLUE_B).shift(DOWN * 0.4)
        etiqueta = Text("una órbita", font_size=20, color=GREY_B)
        etiqueta.next_to(figura, DOWN, buff=0.3)
        self.play(Create(figura), FadeIn(etiqueta), run_time=1.5)
        self.wait(1)
```

Convenciones del canal: título en `GOLD` a 34 px arriba, cuerpos en `BLUE_B`/`TEAL_B`, notas en `GREY_B` a 18–22 px. Mantener esa paleta hace que todos los videos se vean de la misma serie.

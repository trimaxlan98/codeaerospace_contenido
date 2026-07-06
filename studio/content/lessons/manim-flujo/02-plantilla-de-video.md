---
title: Plantilla de video del canal
level: intro
summary: La estructura estándar de una escena del canal — título, construcción, fenómeno, cierre — con la plantilla copiable y las convenciones de estilo que mantienen la serie coherente.
tags: [plantilla, estilo, guion]
minutes: 7
order: 2
---

## La estructura de 4 actos (10–20 s)

1. **Título** (1 s): `Text` en `GOLD`, 30–36 px, `to_edge(UP)`, entra con `FadeIn(shift=DOWN * 0.3)`. Subtítulo opcional en `GREY_B` 19–20 px debajo.
2. **Construcción** (3–5 s): el escenario aparece por partes (`Create` órbitas, `LaggedStart` para grupos, `GrowArrow` conexiones). El espectador debe ver *cómo* se arma.
3. **Fenómeno** (5–8 s): UNA cosa protagonista — el satélite recorre la órbita, la señal cruza el sistema, la red se activa. Es el motivo del video; dale la mayor parte del tiempo.
4. **Cierre** (1–2 s): `Indicate` sobre el resultado, o una etiqueta conclusiva, y `self.wait(1)` final (deja aire para el corte en edición).

## Plantilla copiable

```python
import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from brillo import punto_brillante


class MiEscena(Scene):
    def construct(self):
        # 1 · titulo
        titulo = Text("Tema de hoy", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # 2 · construccion
        orbita = Circle(radius=2.2, color=BLUE_B).shift(DOWN * 0.5)
        sat = punto_brillante(color=YELLOW, radio=0.08)
        sat.move_to(orbita.point_from_proportion(0))
        self.play(Create(orbita), FadeIn(sat), run_time=1.5)

        # 3 · fenomeno
        self.play(MoveAlongPath(sat, orbita), run_time=5, rate_func=linear)

        # 4 · cierre
        self.play(Indicate(sat, color=YELLOW), run_time=0.8)
        self.wait(1)
```

## Convenciones que mantienen la serie coherente

- **Paleta**: títulos `GOLD`; contenido `BLUE_B`/`TEAL_B`; energía `YELLOW`; alerta `RED_B`; secundario `GREY_B`. Fondo negro por defecto.
- **Tipografía**: 30–36 título, 22–26 cuerpo, 17–20 etiquetas. Nunca más de ~12 palabras en pantalla a la vez.
- **Glow**: solo en los actores (satélites, nodos activos, paquetes). El decorado no brilla.
- **Español**: todo texto visible con tildes correctas (`Text` las soporta directo).
- **Una escena, una idea**: si el guion pide dos ideas, son dos escenas (o una transición de `transiciones.py` entre dos VGroups).
- **Nombres**: clase `PascalCase` descriptiva (`OrbitaGeo`, `HandshakeTcp`); el nombre aparece en la Biblioteca de renders.

## De la idea al video

1. Escribe la frase que la animación debe demostrar ("el satélite acelera en el perigeo").
2. Elige protagonista y primitiva (ver *Recetas por dominio*).
3. Plantilla + fenómeno + `ql` hasta que cuadre el ritmo.
4. Render final en `qh` y descarga desde la Biblioteca.

---
title: Qué es Manim y el flujo del Estudio
level: intro
summary: Qué es Manim Community Edition, cómo se estructura un script de animación y cuál es el ciclo completo dentro de ManimStudio, del editor al video.
tags: [manim, estudio, flujo, escena]
minutes: 8
order: 1
---

## Qué es Manim

Manim (Math Animation Engine) es una librería de Python para crear animaciones vectoriales programáticas. Este proyecto usa **Manim Community Edition v0.20** — cuando busques documentación o ejemplos, verifica que sean de la *Community Edition* (docs.manim.community) y no del Manim original de 3Blue1Brown, porque las APIs difieren.

Todo video de Manim nace de un script con esta estructura mínima:

```python
from manim import *


class MiEscena(Scene):
    def construct(self):
        texto = Text("Hola Manim", font_size=48)
        self.play(Write(texto), run_time=2)
        self.wait(1)
```

Las tres piezas:

- **`Scene`**: una clase por escena. `construct()` es el guion — se ejecuta de arriba a abajo y cada `self.play(...)` produce segundos de video.
- **Mobjects** (*math objects*): todo lo que se dibuja — `Text`, `Circle`, `Arrow`, `Axes`… Existen en memoria pero no aparecen hasta que los añades (`self.add`) o los animas (`self.play`).
- **Animaciones**: transformaciones de mobjects a lo largo del tiempo — `Write`, `FadeIn`, `Transform`. Se ejecutan con `self.play(animacion, run_time=segundos)`.

## El flujo dentro de ManimStudio

1. **Pestaña Studio**: escribe el script en el editor. El backend detecta las clases `Scene` automáticamente (analiza el código sin ejecutarlo) y te deja elegir cuál renderizar.
2. **Calidad**: usa `ql` (480p, 15 fps) para iterar — renderiza en segundos. Reserva `qh` (1080p, 60 fps) para el render final: tarda ~8× más.
3. **Render**: el trabajo entra a una cola (uno a la vez) y corre en un contenedor aislado sin red. El log aparece en vivo; el video queda en la Biblioteca.
4. **Pestaña Animaciones**: ejemplos curados listos para abrir en el editor — la categoría *Experimentación* muestra cada primitiva especial del proyecto en acción.
5. **Asistente IA**: puede explicar un error, corregir un script fallido o generar uno desde una descripción. Conoce las primitivas del proyecto y estas lecciones.

## Reglas del sandbox de render

El contenedor de render monta el repositorio **en modo solo lectura**: tu script puede leer (por ejemplo, importar las primitivas del proyecto) pero no escribir fuera de su propio directorio de trabajo. No hay red. Si un script intenta escribir en disco o descargar algo, fallará — es intencional.

## Qué sigue

Las lecciones de esta categoría cubren los mobjects y animaciones esenciales. Las de *Manim intermedio* entran a updaters, animaciones propias y gráficas. Las de *Primitivas del Estudio* documentan la biblioteca `manim_extensions` creada para este canal. Y *Flujo de trabajo* recopila los errores típicos y el checklist antes de renderizar.

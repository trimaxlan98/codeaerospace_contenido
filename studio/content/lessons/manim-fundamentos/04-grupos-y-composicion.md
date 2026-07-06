---
title: Grupos y composición
level: intro
summary: VGroup como unidad de trabajo — agrupar, distribuir con arrange, animar en bloque — y el orden de dibujado con z_index.
tags: [vgroup, arrange, composicion, z-index]
minutes: 8
order: 4
---

## VGroup: la unidad de composición

Un `VGroup` agrupa mobjects para tratarlos como uno: moverlos, escalarlos, animarlos y organizarlos juntos.

```python
tarjeta = VGroup(caja, titulo, icono)
tarjeta.shift(LEFT * 3)          # se mueve todo junto
tarjeta.scale(0.8)               # se escala todo junto
self.play(FadeIn(tarjeta))       # entra todo junto
```

Los miembros se indexan (`tarjeta[0]` es la caja) y se puede iterar: `for m in tarjeta:`.

## arrange: distribuir sin calcular posiciones

```python
fila = VGroup(b1, b2, b3).arrange(RIGHT, buff=1.0)     # en fila
columna = VGroup(x1, x2, x3).arrange(DOWN, buff=0.4)   # en columna
malla = VGroup(*celdas).arrange_in_grid(rows=3, buff=0.3)
```

`arrange` coloca los miembros uno tras otro en la dirección dada — es la forma sana de construir filas de bloques, listas de bullets o tablas pequeñas. Después mueves el grupo completo a su lugar (`fila.shift(UP * 0.6)`).

## Construir grupos por comprensión

```python
estrellas = VGroup(*[
    Dot([x, y, 0], radius=0.04, color=WHITE)
    for x, y in posiciones
])
self.play(LaggedStart(*[FadeIn(e, scale=0.3) for e in estrellas],
                      lag_ratio=0.1), run_time=2)
```

Este par (VGroup por comprensión + LaggedStart) aparece en casi todas las animaciones del canal: cielos de estrellas, constelaciones, listas.

## Orden de dibujado

Lo añadido después se dibuja encima. Dentro de un VGroup, el orden de los argumentos es el orden de pintado — por eso `RedNeuronal` añade las conexiones antes que las neuronas. Para forzar capas entre mobjects sueltos:

```python
fondo.set_z_index(-1)
franja_transicion.set_z_index(50)   # siempre encima
```

## Copias

`mobject.copy()` clona con estilo y posición — útil para transformar sin perder el original, o para los "fantasmas" de las primitivas de brillo:

```python
eco = titulo.copy().set_stroke(YELLOW, width=8, opacity=0.3)
```

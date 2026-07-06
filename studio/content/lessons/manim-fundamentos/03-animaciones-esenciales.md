---
title: Animaciones esenciales
level: intro
summary: El vocabulario básico de self.play — crear, desvanecer, transformar, mover — más run_time, rate_func y cómo combinar animaciones simultáneas y escalonadas.
tags: [animaciones, play, transform, rate_func]
minutes: 10
order: 3
---

## Entrar y salir

```python
self.play(Create(circulo))            # dibuja el trazo progresivamente
self.play(Write(texto))               # como Create pero para texto
self.play(FadeIn(caja, shift=DOWN * 0.3))   # aparece (con deslizamiento opcional)
self.play(FadeIn(logo, scale=0.5))    # aparece creciendo desde la mitad de tamaño
self.play(FadeOut(caja, shift=UP))    # desaparece
self.play(GrowArrow(flecha))          # específica para flechas
```

## Transformar y mover

```python
self.play(Transform(a, b))            # 'a' se convierte en la forma de 'b' (b no entra a escena)
self.play(ReplacementTransform(a, b)) # 'a' desaparece y 'b' queda en escena — suele ser lo que quieres
self.play(caja.animate.shift(RIGHT * 2).scale(1.3))   # anima métodos encadenados
self.play(MoveAlongPath(punto, curva), run_time=3)     # recorre cualquier trazo
self.play(Rotate(rueda, angle=TAU / 4))
self.play(Indicate(bloque, color=YELLOW, scale_factor=1.2))  # resaltar sin mover
```

La distinción `Transform` vs `ReplacementTransform` causa errores sutiles: tras `Transform(a, b)`, el objeto en escena sigue siendo `a` (con la pinta de `b`); si después animas `b`, no pasa nada visible. Regla práctica: usa `ReplacementTransform` salvo que sepas por qué no.

## Tiempo y aceleración

```python
self.play(Create(orbita), run_time=2.5)          # duración en segundos
self.play(MoverSat(...), rate_func=linear)       # velocidad constante
self.play(caja.animate.shift(UP), rate_func=there_and_back)  # va y vuelve
self.wait(1)                                     # pausa (también cuenta como video)
```

`rate_func` por defecto es `smooth` (arranca y frena suave). Otros útiles: `linear` (movimiento mecánico/orbital), `there_and_back` (pulsos), `rush_into`, `rush_from`.

## Simultáneo y escalonado

```python
self.play(Create(orbita), FadeIn(sat), run_time=1.5)   # a la vez

self.play(LaggedStart(                                  # en cascada
    *[FadeIn(estrella, scale=0.3) for estrella in estrellas],
    lag_ratio=0.15), run_time=2)

self.play(Succession(paso1, paso2, paso3))              # en secuencia dentro de un play
self.play(AnimationGroup(anim1, anim2, lag_ratio=0.2))  # solape parcial
```

`LaggedStart` con una list comprehension es el patrón estrella para grupos: constelaciones, listas de bloques, bullets.

## Presupuesto de duración

Un video educativo del canal apunta a escenas de 10–20 s. Suma de `run_time` + `wait`: título (1 s) + construcción (3–5 s) + fenómeno principal (5–8 s) + cierre (1–2 s). Si el guion pide más, parte en varias escenas y únelas al editar (o usa las transiciones de la primitiva `transiciones.py`).

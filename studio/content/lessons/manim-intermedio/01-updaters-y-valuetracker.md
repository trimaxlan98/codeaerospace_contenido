---
title: Updaters y ValueTracker
level: medio
summary: Lógica por frame — mobjects que siguen a otros, contadores animados y relojes internos — y la disciplina de limpiar updaters para no pagar su costo para siempre.
tags: [updaters, valuetracker, always-redraw]
minutes: 10
order: 1
---

## Qué es un updater

Un updater es una función que se ejecuta **en cada frame** sobre un mobject, mientras esté añadida. Sirve para relaciones que deben mantenerse durante otras animaciones: una etiqueta que sigue a su figura, una línea que une dos puntos móviles.

```python
etiqueta.add_updater(lambda e: e.next_to(satelite, UP, buff=0.2))
self.add(etiqueta)
self.play(MoveAlongPath(satelite, orbita), run_time=4)  # la etiqueta lo sigue
etiqueta.clear_updaters()   # ¡SIEMPRE al terminar!
```

Así funcionan los enlaces ISL de `constelacion.py`: cada línea lleva un updater que la re-tiende entre sus dos satélites.

**El error clásico de las lambdas en un bucle**: capturan la última variable. Fíjala como argumento por defecto:

```python
for a, b in pares:
    linea.add_updater(lambda l, a=a, b=b: l.put_start_and_end_on(
        a.get_center(), b.get_center()))
```

## ValueTracker: animar un número

`ValueTracker` guarda un valor animable; con `always_redraw` reconstruyes un mobject en función de él:

```python
angulo = ValueTracker(0)
aguja = always_redraw(lambda: Line(
    ORIGIN, 2 * np.array([np.cos(angulo.get_value()),
                          np.sin(angulo.get_value()), 0]),
    color=YELLOW))
self.add(aguja)
self.play(angulo.animate.set_value(PI), run_time=3)
```

Contador numérico en pantalla:

```python
valor = ValueTracker(0)
contador = always_redraw(lambda: DecimalNumber(
    valor.get_value(), num_decimal_places=0, font_size=40).to_corner(UR))
self.add(contador)
self.play(valor.animate.set_value(7500), run_time=3)   # "altitud: 0 → 7500"
```

## Estela con TracedPath

```python
estela = TracedPath(satelite.get_center, dissipating_time=1.0,
                    stroke_color=YELLOW, stroke_width=3)
self.add(estela, satelite)
```

`dissipating_time` hace que la cola se desvanezca — es la estela de la demo *Órbita kepleriana real*.

## Disciplina de updaters

- Cada updater corre en **todos** los frames de **todas** las animaciones siguientes: acumular updaters degrada el render sin que se note en el código.
- `clear_updaters()` cuando la relación deja de necesitarse.
- Si algo puede resolverse con una animación normal (posición conocida de antemano), no uses updater: una `Animation` personalizada (siguiente lección) es más barata y determinista.

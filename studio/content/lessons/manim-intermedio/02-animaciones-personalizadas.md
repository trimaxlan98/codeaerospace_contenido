---
title: Animaciones personalizadas
level: medio
summary: Cómo escribir tu propia Animation con interpolate_mobject — el patrón detrás de MoverKepler, PulsoDeSenal y AnimarConstelacion — y cuándo preferirla a un updater.
tags: [animation, interpolate, subclase]
minutes: 10
order: 2
---

## El patrón

Cuando ninguna animación de catálogo hace lo que quieres (movimiento con física, trayectorias calculadas, muchos objetos coordinados), subclasea `Animation`:

```python
class MoverConFisica(Animation):
    def __init__(self, mobject, camino, **kwargs):
        self.camino = camino
        kwargs.setdefault("rate_func", linear)
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        t = self.rate_func(alpha)          # aplica la curva de aceleración
        self.mobject.move_to(self.camino.point_from_proportion(t))
```

Contrato de `interpolate_mobject`:

- Recibe `alpha` ∈ [0, 1]: la fracción **de tiempo** transcurrida del `run_time`.
- Aplica tú `self.rate_func(alpha)` si quieres respetar el parámetro (las de catálogo lo hacen).
- Modifica `self.mobject` al estado que corresponde a ese instante — sin acumular: calcula el estado absoluto desde alpha, no "un pasito más" (la función puede llamarse con alphas no consecutivos).
- `self.starting_mobject` es una copia del estado inicial, por si necesitas partir de él (`self.mobject.become(self.starting_mobject.copy().scale(s))`).

## Ejemplos reales del proyecto

Las tres primitivas de movimiento del proyecto son exactamente este patrón:

- `MoverKepler` (kepler.py): en cada frame resuelve la ecuación de Kepler para el alpha recibido y hace `move_to` — así la velocidad varía físicamente.
- `PulsoDeSenal` (senal.py): mapea alpha a `point_from_proportion` del camino, con el pliegue `1 - abs(2t - 1)` para ida y vuelta.
- `AnimarConstelacion` (constelacion.py): un solo `Animation` mueve decenas de satélites — mucho más barato que un updater por satélite.

## Animation vs updater

| | Animation propia | Updater |
|---|---|---|
| Duración | Acotada por `run_time` | Corre hasta `clear_updaters()` |
| Estado | Función pura de alpha (reproducible) | Acumulativo (depende del frame rate) |
| Uso típico | Movimiento principal de la escena | Relaciones que siguen a otro objeto |

Regla: el fenómeno protagonista, como `Animation`; los acompañantes (etiquetas, enlaces), como updaters mientras dure el fenómeno.

## Composición sin subclasear

Muchas veces no hace falta ni la subclase: una función que devuelve `Succession`/`AnimationGroup` ya es una "animación con receta". Así están hechas `disparo()` (laser.py), `flujo()` (bloques.py) y las transiciones. Es la opción más simple y componible:

```python
def entrada_doble(titulo, cuerpo):
    return AnimationGroup(FadeIn(titulo, shift=DOWN * 0.3),
                          FadeIn(cuerpo, shift=UP * 0.2), lag_ratio=0.3)
```

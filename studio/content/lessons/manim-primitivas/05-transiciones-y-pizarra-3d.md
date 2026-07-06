---
title: Transiciones y pizarra 3D
level: medio
summary: API de transiciones.py (deslizar, zoom, persiana) y pizarra3d.py (superficies y sólidos "3D" dibujados en 2D, sin ThreeDScene), con el caso estrella de la superficie de pérdida.
tags: [transiciones, pizarra3d, superficies, primitivas]
minutes: 9
order: 5
---

## transiciones.py — encadenar diapositivas

Agrupa cada "diapositiva" en un `VGroup` y encadena:

```python
from transiciones import (transicion_deslizar, transicion_zoom,
                          transicion_persiana)

self.play(transicion_deslizar(bloque1, bloque2, direccion=LEFT), run_time=1.4)
self.play(transicion_zoom(bloque2, bloque3), run_time=1.5)
self.play(transicion_persiana(bloque3, cierre, franjas=9))
```

- El **entrante NO necesita `self.add` previo** — la animación lo añade.
- `deslizar`: el viejo sale empujado, el nuevo entra del lado opuesto. Neutral, sirve siempre.
- `zoom`: el viejo "atraviesa la cámara". Para pasar de lo general al detalle.
- `persiana(franjas=8, color=BLACK)`: franjas cubren, el contenido permuta detrás, franjas se retiran. La más cinematográfica; no la repitas dos veces seguidas.

## pizarra3d.py — 3D de pizarrón (sin ThreeDScene)

Proyección oblicua tipo "cabinet": x → derecha, z → arriba, y → profundidad en diagonal. Todo son VMobjects 2D baratos; nada de cámaras 3D.

```python
from pizarra3d import (proyectar, ejes_pizarra, malla_superficie,
                       curva_3d, cubo_pizarra, esfera_pizarra)

ejes = ejes_pizarra(longitud=2.2)
silla = malla_superficie(lambda x, y: 0.3 * (x*x - y*y))
self.play(Create(ejes), Create(silla, run_time=3))
```

- `proyectar((x, y, z))` — el conversor crudo: úsalo para colocar CUALQUIER cosa en el "espacio" del boceto.
- `ejes_pizarra(longitud, etiquetas=("x","y","z"))` — el trío de flechas.
- `malla_superficie(f, x_range, y_range, lineas=9)` — malla de `z = f(x, y)` coloreada por altura (azul abajo → amarillo arriba), ordenada de atrás hacia adelante.
- `curva_3d(fn, t_min, t_max)` — proyecta una curva paramétrica `t -> (x, y, z)`; con ella se dibujan trayectorias SOBRE la superficie.
- `cubo_pizarra(lado)` / `esfera_pizarra(radio)` — sólidos alámbricos con aristas ocultas discontinuas, como en el pizarrón.

## El caso estrella: descenso por gradiente (demo 10)

```python
def perdida(x, y):
    return 0.28 * (x*x + y*y)

cuenco = malla_superficie(perdida, lineas=8)

def descenso(t):                       # espiral que cae al mínimo
    r, ang = 1.8 * (1 - t), 4.5 * t
    x, y = r * np.cos(ang), r * np.sin(ang)
    return (x, y, perdida(x, y) + 0.03)

camino = curva_3d(descenso, 0, 1, color=RED_B)
bola = punto_brillante(color=RED_B, radio=0.07)
bola.move_to(camino.get_start())
self.play(Create(camino), MoveAlongPath(bola, camino), run_time=3.5)
```

El mismo esquema sirve para sillas de montar (mínimos locales), campos de potencial gravitatorio, y cualquier "paisaje" que un profesor dibujaría en el pizarrón. Si mueves la malla (`shift`), mueve TAMBIÉN el camino con el mismo vector — ambos viven en coordenadas proyectadas.

---
title: Señales, láser y diagramas
level: medio
summary: API de senal.py (paquetes que viajan), laser.py (haces y disparos) y bloques.py (diagramas con flujo) — las tres primitivas de "cosas que se mueven por enlaces".
tags: [senal, laser, bloques, telecom, primitivas]
minutes: 9
order: 4
---

## senal.py — paquetes por cualquier camino

```python
from senal import PulsoDeSenal, destello

enlace = ArcBetweenPoints(tierra.get_center(), sat.get_center(), angle=-0.35)
paquete = punto_brillante(color=WHITE, radio=0.05)
self.add(paquete)
self.play(PulsoDeSenal(paquete, enlace), destello(enlace, YELLOW),
          run_time=1.4)
```

- `PulsoDeSenal(mobject, camino, ida_y_vuelta=False)` — mueve lo que sea por cualquier `VMobject` con puntos (líneas, arcos, órbitas). `ida_y_vuelta=True` hace el eco/ACK en una sola animación (demo 04).
- `destello(camino, color=YELLOW, ancho=5, cola=0.35)` — `ShowPassingFlash` preconfigurado; lanzado JUNTO al pulso en el mismo `self.play` vende la idea de energía recorriendo el enlace.

## laser.py — haces con impacto

```python
from laser import disparo, rafaga

self.play(disparo(canon, objetivo, color=RED, duracion=1.2))
self.play(rafaga(sat_a, sat_b, color=TEAL_B, pulsos=4, duracion=2.4))
```

- `disparo(origen, destino, color, duracion=1.2, radio_impacto=0.45)` — haz que crece (núcleo blanco + halo del color), `Flash` al impactar, y desvanecimiento. Origen/destino son puntos (`mobject.get_center()`).
- `rafaga(origen, destino, pulsos=3)` — enlace óptico con tráfico: guía tenue fija + pulsos blancos que la recorren. Para comunicación láser inter-satelital sostenida.
- `rayo(origen, destino)` — el haz crudo por si quieres coreografía propia.

Usos del canal: uplink óptico, laser ranging de basura espacial, LiDAR, ataques/interferencia (en rojo).

## bloques.py — diagramas de sistema con flujo

```python
from bloques import bloque, conectar, flujo

b1, b2, b3 = bloque("Sensor", color=TEAL_B), bloque("ADC"), bloque("DSP")
VGroup(b1, b2, b3).arrange(RIGHT, buff=1.1)
conexiones = [conectar(b1, b2), conectar(b2, b3)]
self.play(*[FadeIn(b) for b in (b1, b2, b3)])
self.play(*[GrowArrow(c) for c in conexiones])
self.play(flujo(conexiones))                     # la señal recorre el pipeline
```

- `bloque(texto, ancho=2.1, alto=0.85, color=BLUE_B)` — caja redondeada + etiqueta autoajustada; muévela como unidad.
- `conectar(a, b)` — flecha que elige sola el lado de salida/entrada según la posición relativa (horizontal o vertical).
- `flujo(conexiones, color=YELLOW, por_conexion=0.55)` — destello que recorre las conexiones EN ORDEN (es un `Succession`). Remata con `Indicate(bloque_final)` para marcar la llegada (demo 07).

Layout: construye las filas con `arrange`, cuelga ramas con `next_to`, y conecta al final (las flechas leen posiciones actuales).

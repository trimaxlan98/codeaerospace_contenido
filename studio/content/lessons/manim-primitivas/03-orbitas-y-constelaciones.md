---
title: Órbitas y constelaciones
level: medio
summary: API de kepler.py (movimiento orbital físicamente correcto) y constelacion.py (shells LEO con enlaces ISL), y por qué MoveAlongPath miente sobre las órbitas.
tags: [kepler, orbitas, constelacion, leo, primitivas]
minutes: 9
order: 3
---

## kepler.py — la física de verdad

`MoveAlongPath` sobre una elipse recorre el trazo a rapidez constante — un satélite real acelera en el perigeo y frena en el apogeo (2ª ley de Kepler). `MoverKepler` resuelve la ecuación de Kepler (M = E − e·sen E, por Newton-Raphson) en cada frame, así que el movimiento es el físico:

```python
from kepler import OrbitaKepler, MoverKepler

orbita = OrbitaKepler(a=3.0, e=0.65, color=BLUE_B)   # foco en el origen del grupo
sat = punto_brillante(color=YELLOW, radio=0.07)
sat.move_to(orbita.posicion(0))                       # f=0 es el perigeo
self.add(orbita, sat)
self.play(MoverKepler(sat, orbita, vueltas=2), run_time=9)
```

- `OrbitaKepler(a, e, color, mostrar_foco=True)` — `a` semieje mayor en unidades de escena, `e` excentricidad [0,1). El cuerpo central va en el foco (`orbita._foco_absoluto()` o el `Dot` `orbita.foco`).
- `orbita.posicion(f)` — punto de la órbita en la fracción `f` del período; sirve para colocar etiquetas ("perigeo" en `posicion(0)`, "apogeo" en `posicion(0.5)`).
- `MoverKepler(mobject, orbita, vueltas=1, fase_inicial=0)` — `rate_func=linear` por defecto (¡no lo cambies: la física YA pone la aceleración!).

Estela: `TracedPath(sat.get_center, dissipating_time=1.1, stroke_color=YELLOW)` añadida ANTES del play (demo 03).

Con `e=0` tienes una órbita circular correcta; sube `e` para el drama visual (0.6–0.75 se lee muy bien).

## constelacion.py — shells LEO en 2D

La vista clásica "Starlink": planos orbitales como elipses rotadas, satélites con fases repartidas y sentidos alternos:

```python
from constelacion import ConstelacionLEO, AnimarConstelacion, enlaces_isl

cons = ConstelacionLEO(planos=4, sats_por_plano=9, radio=2.7)
enlaces = enlaces_isl(cons)             # líneas ISL con updaters
self.add(cons, enlaces)
self.play(AnimarConstelacion(cons, vueltas=0.8), run_time=7)
enlaces.clear_updaters()                # SIEMPRE al terminar
```

- `ConstelacionLEO(planos, sats_por_plano, radio, achatamiento=0.35, mostrar_tierra=True)` — expone `cons.tierra` y `cons.planos_orbitales` (lista de dicts con `camino`, `sats`, `fases`) por si quieres construir la entrada por partes (demo 06 hace `Create` plano por plano con `LaggedStart`).
- `AnimarConstelacion(cons, vueltas)` — UNA animación mueve todos los satélites; barata aunque haya 50.
- `enlaces_isl(cons)` — enlaces intra-plano que siguen a los satélites vía updaters. No olvides `clear_updaters()`.

Escala: 4–5 planos × 8–10 sats es el punto dulce visual; más se vuelve ruido en 480p.

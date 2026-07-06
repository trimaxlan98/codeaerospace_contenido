---
title: Brillo y partículas
level: medio
summary: API completa de brillo.py (glow por capas) y particulas.py (desintegrar y materializar), con los parámetros que importan y sus valores sensatos.
tags: [brillo, glow, particulas, primitivas]
minutes: 8
order: 2
---

## brillo.py — glow sin shaders

El renderer Cairo no tiene glow; el truco es apilar copias con trazo cada vez más ancho y tenue. Dos funciones:

```python
from brillo import con_brillo, punto_brillante

titulo = con_brillo(Text("SATCOM", color=BLUE_B), ancho_max=12)
sat = punto_brillante([2, 1, 0], color=YELLOW, radio=0.1, alcance=3.5)
```

- `con_brillo(vmobject, color=None, capas=5, ancho_max=14, opacidad=0.35)` — envuelve CUALQUIER trazo (texto, órbita, flecha). Devuelve `VGroup(halo, original)`: muévelo como unidad. `color=None` toma el del objeto.
- `punto_brillante(punto=None, color=WHITE, radio=0.09, capas=6, alcance=3.2, opacidad=0.6)` — el "actor" estándar del canal para satélites, estrellas y nodos. `alcance` controla hasta dónde llega el halo (en radios).

Trucos:

- Halo que respira: `self.play(sat.animate.scale(1.3), rate_func=there_and_back)`.
- No abuses: glow en 1–3 protagonistas; si todo brilla, nada brilla.
- Calibrado sobre fondo negro (el del canal); sobre fondos claros baja `opacidad`.

## particulas.py — desintegrar y materializar

```python
from particulas import Desintegrar, materializar

self.play(Desintegrar(texto, n=260, dispersion=1.8), run_time=1.8)
self.remove(texto)              # queda invisible en escena; límpialo
self.play(materializar(logo, n=260, dispersion=2.2), run_time=1.8)
```

- `Desintegrar(mobject, n=200, dispersion=1.4, semilla=7)` — el objeto se disuelve en `n` puntos muestreados de su contorno real que se dispersan y desvanecen. Es un `Transform`: tras la animación haz `self.remove(mobject)`.
- `materializar(mobject, ...)` — la inversa: polvo visible converge y se convierte en el objeto. Devuelve la animación lista para `self.play`; no añadas el objeto antes.
- `particulas_de(mobject, ...)` — el generador de polvo crudo, por si quieres coreografías propias.

Parámetros que importan:

- `n`: 150–300 se ve bien; >500 encarece el render sin ganancia visual.
- `dispersion`: radio de dispersión en unidades de escena (1.4–2.5 típico).
- `semilla`: misma semilla = mismas partículas en cada render (¡déjala fija!). Para encadenar desintegrar→materializar de forma coherente, usa la MISMA semilla en ambas.

El combo narrativo clásico (demo 02): concepto viejo se desintegra → concepto nuevo se materializa del mismo polvo. Funciona para "la señal analógica se convierte en bits", "el monolito se vuelve microservicios", etc.

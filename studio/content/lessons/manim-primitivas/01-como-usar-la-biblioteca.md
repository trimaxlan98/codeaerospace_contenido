---
title: Cómo usar la biblioteca del proyecto
level: intro
summary: Qué es manim_extensions, cómo importar las primitivas desde cualquier script del Estudio y el mapa completo de los 10 módulos disponibles.
tags: [primitivas, biblioteca, imports]
minutes: 6
order: 1
---

## Qué es

`studio/content/manim_extensions/` es la biblioteca de primitivas curadas del proyecto: efectos que Manim CE no trae, escritos y verificados para este canal. Está versionada en git — cada módulo es un archivo pequeño, autocontenido y documentado en su docstring.

## Cómo importar (las 2 líneas mágicas)

El contenedor de render monta el repositorio en `/workspace` (solo lectura). Cualquier script del Estudio puede usar las primitivas añadiendo al principio:

```python
import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from brillo import punto_brillante          # y ya
```

Todas las demos de la categoría **Experimentación** (pestaña Animaciones) empiezan así — ábrelas en el editor y tendrás una plantilla funcionando.

## Mapa de la biblioteca

| Módulo | Qué da | Demo |
|---|---|---|
| `brillo` | `con_brillo`, `punto_brillante` — glow/halos | 01 |
| `particulas` | `Desintegrar`, `materializar` — polvo determinista | 02 |
| `kepler` | `OrbitaKepler`, `MoverKepler` — órbitas físicas | 03 |
| `senal` | `PulsoDeSenal`, `destello` — paquetes por caminos | 04 |
| `neuronal` | `RedNeuronal` + `.activacion()` — forward pass | 05 |
| `constelacion` | `ConstelacionLEO`, `AnimarConstelacion`, `enlaces_isl` | 06 |
| `bloques` | `bloque`, `conectar`, `flujo` — diagramas | 07 |
| `transiciones` | `transicion_deslizar` / `_zoom` / `_persiana` | 08 |
| `laser` | `rayo`, `disparo`, `rafaga` — enlaces ópticos | 09 |
| `pizarra3d` | `proyectar`, `malla_superficie`, `cubo/esfera_pizarra` | 10 |

## Reglas para ampliar la biblioteca

Si escribes una primitiva nueva (o se la pides al asistente IA):

1. Un archivo = un tema; docstring con ejemplo de uso arriba.
2. Sin dependencias fuera de `manim`/`numpy`, sin red, sin escribir archivos.
3. Aleatoriedad SIEMPRE con semilla fija (`np.random.default_rng(semilla)`): renders reproducibles.
4. Conteos acotados por defecto (partículas, capas de glow, líneas de malla).
5. Crea su demo en `studio/content/animations/experimentacion/` y renderízala en `ql` antes de commitear.

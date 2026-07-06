---
title: Recetas por dominio del canal
level: medio
summary: Patrones concretos para los temas del canal — satélites y órbitas, telecomunicaciones, IA y ciencia de datos — combinando Manim base con las primitivas del proyecto.
tags: [satelites, telecom, ia, ciencia-datos, recetas]
minutes: 12
order: 4
---

## Satélites y órbitas

- **Órbita simple (velocidad constante)**: `Circle`/`Ellipse` + `MoveAlongPath` con `rate_func=linear`.
- **Órbita física (acelera en perigeo)**: `OrbitaKepler` + `MoverKepler` (primitiva `kepler.py`). Añade `TracedPath(sat.get_center, dissipating_time=1)` para la estela.
- **Constelación completa**: `ConstelacionLEO` + `AnimarConstelacion` + `enlaces_isl` (primitiva `constelacion.py`).
- **Cuerpos**: la Tierra como `Circle` con `fill_opacity` 0.5; satélites como `punto_brillante` (primitiva `brillo.py`) para que "vivan" sobre el fondo negro.
- **Cobertura**: un haz de antena es un `Sector`/`AnnularSector` semitransparente anclado al satélite con updater.

## Telecomunicaciones

- **Enlaces**: `ArcBetweenPoints` entre estaciones (queda más orgánico que `Line`); el tráfico con `PulsoDeSenal` + `destello` (primitiva `senal.py`).
- **Enlaces ópticos/láser**: `disparo` y `rafaga` (primitiva `laser.py`).
- **Señales en el tiempo**: `Axes` + `plot` de senos amortiguados; la modulación se cuenta bien graficando portadora y moduladora en dos ejes apilados (`VGroup(ejes1, ejes2).arrange(DOWN)`).
- **Diagramas de sistema**: `bloque` + `conectar` + `flujo` (primitiva `bloques.py`) — cadena TX/RX, protocolos por capas.
- **Espectro**: barras como `Rectangle`s sobre ejes, animadas con `stretch_to_fit_height`.

## IA y ciencia de datos

- **Redes neuronales**: `RedNeuronal(capas=(4, 6, 6, 2))` + `.activacion()` (primitiva `neuronal.py`).
- **Descenso por gradiente / superficies de pérdida**: `malla_superficie` + `curva_3d` en proyección de pizarrón (primitiva `pizarra3d.py`) — sin ThreeDScene.
- **Curvas de entrenamiento**: `Axes` + dos `plot` (train/val) + `Create` escalonado con `LaggedStart`.
- **Embeddings/clusters**: nubes de `Dot`s por comprensión, coloreadas por grupo, que se reagrupan con `dot.animate.move_to(...)` dentro de un `AnimationGroup`.
- **Atención/transformers**: matriz de `Square`s (`arrange_in_grid`) con `set_fill(color, opacity=peso)`; las conexiones entre tokens como líneas con opacidad proporcional al peso.

## Transiciones entre ideas

Dentro de una misma escena, agrupa cada "diapositiva" en un `VGroup` y encadénalas con `transicion_deslizar` / `transicion_zoom` / `transicion_persiana` (primitiva `transiciones.py`) — evita el corte seco de FadeOut/FadeIn total.

## El principio general

Primero decide el fenómeno protagonista (la física, el flujo de datos, la activación) y resuélvelo con UNA primitiva o animación custom; después viste la escena: título arriba, etiquetas `GREY_B`, glow solo en los actores importantes. Las escenas del canal que mejor funcionan tienen un solo protagonista y menos de 6 elementos simultáneos en pantalla.

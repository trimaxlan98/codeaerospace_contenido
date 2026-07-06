---
title: Rendimiento del render
level: medio
summary: Qué hace lento un render y qué no — mediciones reales del servidor — y las palancas concretas: calidad, conteo de objetos, updaters, LaTeX y el renderer OpenGL.
tags: [rendimiento, calidad, opengl, optimizacion]
minutes: 9
order: 5
---

## Mediciones reales (este servidor, contenedor sin GPU)

La misma escena (órbita kepleriana con glow y estela):

| Calidad | Cairo (defecto) | OpenGL |
|---|---|---|
| `ql` 480p15 | **6.9 s** | 10.1 s |
| `qh` 1080p60 | 56.0 s | **38.9 s** |

Conclusiones prácticas:

1. **Itera SIEMPRE en `ql`**: es ~8× más rápido que `qh`. El salto a `qh` es solo para el render final.
2. El renderer OpenGL (disponible en la imagen, requiere `--write_to_movie`) gana ~30% en calidad alta, pero pierde en `ql`. Hoy la UI usa Cairo; OpenGL es una palanca para renders finales largos si algún día se expone en el pipeline.

## Qué encarece un frame

- **Cantidad de puntos vectoriales**, no de "objetos": un `Text` largo tiene cientos de curvas; una malla de superficie, miles de puntos. Las primitivas del proyecto ya vienen acotadas (partículas ~200, glow 5–6 capas, malla 9 líneas por dirección) — mantén esos órdenes de magnitud.
- **Updaters acumulados**: corren en cada frame de cada `play` posterior. `clear_updaters()` religiosamente.
- **LaTeX**: cada `MathTex` distinto compila la primera vez (~1–3 s). Diez fórmulas = decenas de segundos solo de compilación. Reutiliza mobjects de fórmula en lugar de crear variantes.
- **`wait` largos**: cada segundo de `wait` son frames que también se rasterizan. En `qh` a 60 fps, 5 s de espera = 300 frames.

## Qué NO ayuda

- Reducir `run_time` no reduce el trabajo por frame, solo la cantidad de frames.
- El caché de Manim está deshabilitado a propósito en este pipeline (`--disable_caching`): los renders son reproducibles y el sandbox es de un solo uso; no intentes "aprovechar caché".

## Presupuesto orientativo

Una escena del canal (10–15 s, 1 protagonista + título + etiquetas) debe renderizar en `ql` en **menos de 30 s**; si tarda minutos, algo está desbocado (updaters sin limpiar, mallas densísimas, cientos de mobjects individuales). Divide la escena o baja los conteos.

## El truco de los grupos para animar N objetos

Mover 50 satélites con 50 animaciones es caro de coordinar; una sola `Animation` que recorra todos (patrón `AnimarConstelacion`) rinde mejor y el código queda más claro. Igual con `LaggedStart` sobre un `VGroup` en vez de 50 `self.play` consecutivos — cada `self.play` tiene un costo fijo de arranque.

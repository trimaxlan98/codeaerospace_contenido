# Fractales: librería y curso (2026-08-05)

## Librería `studio/content/manim_extensions/fractales.py`

Fractales de escape (Mandelbrot/Julia) para Manim CE pensados para el VPS
(render capado a 1.5 vCPU / 2 GB): todo el cómputo es numpy vectorizado con
máscara de puntos activos y el resultado se muestra como `ImageMobject`
—nunca un mobject por píxel—. Sin dependencia de matplotlib (paletas por LUT
propia) y determinista (mismo script → mismo render).

API principal (docstrings en el propio módulo):

- `imagen_mandelbrot(...)` / `imagen_julia(c, ...)` / `miniatura_julia(c, ...)`
- `zoom_fractal(escena, imagen, centro, factor_total, ...)` — zoom continuo
  SIN recalcular por frame: pocas imágenes clave sobremuestreadas, escaladas
  con `rate_func` exponencial y reemplazadas en el empalme. El coloreado es
  cíclico sobre el conteo suavizado (no depende de `max_iter`), por eso los
  tramos empalman sin salto de color.
- `morph_julia(escena, camino_c, ...)` — fotogramas precalculados en lote que
  se intercambian mutando `pixel_array` en un updater (coste de vídeo constante).
- `orbita(c, ...)`, `camino_cardioide(alpha)`, `PALETAS` (nebulosa/fuego/
  oceano/aurora).
- Topes de seguridad: `RES_MAX=2200` px, `ITER_MAX=4000`, `FRAMES_MORPH_MAX=220`.

Demo en Animaciones: `experimentacion/11-fractales-de-escape.py`.

## Curso "Fractales: la belleza de los números complejos"

Proyecto en la pestaña Proyectos (calidad `qm`, 1280x720@30), 8 clips:
fórmula-gancho → plano complejo → multiplicar-es-girar → iteración/órbitas →
Mandelbrot (malla didáctica → imagen real → anatomía) → zoom de 177 000
aumentos hasta un minibrot (`-0.743643887+0.131825904i`) → morph de Julia
(conejo → cardioide → dendrita) → el Mandelbrot como mapa de Julias + mosaico.

El estilo compuesto del proyecto define la paleta (C_TITULO dorado, C_ACENTO
magenta, C_CIAN, fondo `#08060f` igual al interior de los fractales) y los
helpers `titulo_curso`/`pie_curso`; los clips no llevan imports propios.

## Gotcha: bounding box de `Text` con espacios (Manim 0.20.1)

El glifo vacío del espacio de un `Text` NO se mueve con el resto del mobject:
queda anclado donde el texto nació, y cualquier movimiento posterior infla el
bounding box (rompe `BackgroundRectangle`, `SurroundingRectangle`, `next_to`
contra ese texto…). `MathTex` no está afectado. El estilo compuesto del curso
lo corrige con una sombra global de `Text` que elimina los submobjects sin
puntos tras construir. Verificado empíricamente con renders de prueba
(`h=0.28` → `h=1.64` tras `move_to`; con la sombra, `h=0.28` estable).

## Presupuesto de render (medido)

- El cuello de botella NO es numpy (keyframe 2048x1152 con 1350 iter: ~2 s);
  es Cairo componiendo la imagen a pantalla completa: ~2.5 fps de vídeo.
- Con `--disable_caching` los `self.wait` sobre una imagen cuestan lo mismo
  que la animación: recortar esperas en clips con imagen llena.
- Regla rápida: segundos de vídeo con imagen a pantalla completa × 12 ≈
  segundos de render. Un clip de ~50 s cabe en el timeout de 1200 s
  (`MS_DEFAULT_TIMEOUT`, ver README § Operación).

---
title: Errores comunes y cómo leerlos
level: intro
summary: Los fallos que más se repiten en el Estudio — LaTeX, imports, escena no encontrada, sandbox — cómo se ven en el log y su arreglo en una línea.
tags: [errores, debug, log, sandbox]
minutes: 8
order: 1
---

## Cómo leer un log de render

El log aparece en vivo bajo el editor. Ante un fallo, ve al FINAL: el traceback de Python termina con la línea útil (`XxxError: mensaje`). Los errores de LaTeX quedan un poco antes, marcados con `!`. El botón **Explicar** del asistente IA hace esta lectura por ti; **Corregir** devuelve el script arreglado.

## El top de errores

**1. LaTeX roto** — `LaTeX Error` o `Undefined control sequence`:

```python
MathTex("\frac{a}{b}")     # MAL: \f es un escape de Python
MathTex(r"\frac{a}{b}")    # BIEN: raw string SIEMPRE
```

**2. Escena no detectada** — "el script no define escenas": la clase no hereda de `Scene` (o el método se llama distinto a `construct`). La detección es por análisis estático; la clase debe ser `class Algo(Scene):` (o `ThreeDScene`, `MovingCameraScene`).

**3. Import de primitivas falla** — `ModuleNotFoundError: No module named 'brillo'`: faltan las 2 líneas de bootstrap ANTES del import:

```python
import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")
```

**4. `AttributeError: 'VGroup' object has no attribute ...`** — llamaste un método de mobject concreto sobre un grupo (p. ej. `get_stroke_color` de las primitivas devueltas como VGroup). Accede al miembro: `grupo[0]`.

**5. Transform vs escena** — animaste `b` después de `Transform(a, b)` y "no pasa nada": en escena sigue estando `a`. Usa `ReplacementTransform(a, b)`.

**6. Nada aparece** — creaste el mobject pero nunca hiciste `self.add(...)` ni lo animaste con un introductor (`FadeIn`, `Create`...).

**7. Updater con lambda en bucle** — todas las líneas siguen al MISMO satélite: captura las variables como defaults (`lambda l, a=a, b=b: ...`).

**8. Sandbox** — `PermissionError`/`Read-only file system` al abrir archivos, o cuelgues al intentar red: el contenedor no tiene red y el repo es solo lectura. Los scripts no deben leer ni escribir archivos (todo el contenido va embebido en el script).

**9. Timeout** — el job termina en `timeout`: la escena es demasiado larga o hay updaters desbocados. Revisa la lección de *Rendimiento*.

## Método general

Reproduce en `ql` (rápido), arregla UNA cosa, re-renderiza. Si el error es críptico, recorta la escena a la mitad que falla (comenta la otra) y bisecta. El asistente IA con el log completo acierta la causa en la gran mayoría de los casos.

---
title: Color, estilo y LaTeX
level: intro
summary: La paleta de Manim y la del canal, relleno vs trazo, gradientes, y cómo escribir fórmulas con MathTex sin pelearse con LaTeX.
tags: [color, estilo, latex, mathtex]
minutes: 9
order: 5
---

## Colores

Manim trae constantes con variantes de intensidad: `BLUE_A` (claro) … `BLUE_E` (oscuro), y lo mismo para `RED`, `GREEN`, `YELLOW`, `TEAL`, `GOLD`, `GREY`… También acepta hex: `color="#1f8fff"`.

Paleta del canal (para que todos los videos se vean de la misma serie):

- Títulos: `GOLD`, 30–36 px, `to_edge(UP)`.
- Contenido principal: `BLUE_B`, `TEAL_B`.
- Acentos/energía: `YELLOW`; alertas/objetivos: `RED_B`.
- Texto secundario: `GREY_B`, 18–22 px.
- Fondo: el negro por defecto (no lo cambies; el glow de las primitivas está calibrado sobre negro).

## Relleno y trazo son independientes

```python
Circle(color=BLUE)                                  # solo contorno azul
Circle(color=BLUE, fill_color=BLUE, fill_opacity=0.3)  # contorno + relleno
figura.set_fill(TEAL_B, opacity=0.5)
figura.set_stroke(WHITE, width=1.5, opacity=0.8)
```

`set_fill` / `set_stroke` funcionan sobre cualquier mobject o VGroup ya creado. Un gradiente se logra con `set_color_by_gradient(BLUE, TEAL, YELLOW)` (útil en textos y mallas).

## Fórmulas con MathTex

```python
formula = MathTex(r"\Delta v = v_e \ln\frac{m_0}{m_f}", font_size=48)
```

Reglas que evitan el 90% de los errores de LaTeX:

1. **Siempre raw string** (`r"..."`): sin la `r`, `\f` o `\n` se interpretan como escapes de Python y LaTeX recibe basura.
2. `MathTex` ya está en modo matemático — no pongas `$...$`.
3. Texto dentro de una fórmula: `\text{...}` → `r"v_{\text{orbital}}"`.
4. Si LaTeX falla, el log del render muestra el error real al final (`! Undefined control sequence` y la línea). El botón *Corregir* del asistente IA resuelve estos casos bien.
5. El contenedor tiene `texlive` completo: `\frac`, `\vec`, `\hat`, matrices (`\begin{pmatrix}`), alineación (`&`) funcionan.

Colorear partes de una fórmula:

```python
formula = MathTex(r"F", r"=", r"G\frac{m_1 m_2}{r^2}")
formula[2].set_color(YELLOW)          # cada argumento es un submobject
```

## Texto plano vs LaTeX

`Text` usa fuentes del sistema (rápido, acepta tildes y cualquier Unicode directamente) — para títulos y etiquetas. `MathTex`/`Tex` compilan LaTeX (más lento, ~1–3 s extra por fórmula la primera vez) — solo para matemáticas. Si una escena tiene 10 fórmulas, espera un render notablemente más lento en `ql`; es normal.

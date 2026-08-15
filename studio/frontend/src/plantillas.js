// Plantillas de curso: el punto de partida de un proyecto nuevo.
//
// Por que existen: crear un curso "en blanco" deja el estilo compartido vacio,
// y sin el los clips no heredan la identidad CO.DE Academy, la tipografia ni
// los helpers de rotulo. Ese bloque son ~90 lineas que TODOS los cursos del
// repo repiten palabra por palabra (comparese cualquier
// `studio/content/cursos/*/style_block.py`), incluida la sombra de `Text` que
// arregla una trampa real de Manim 0.20. Nadie deberia tener que reescribirlo,
// sepa Python o no.
//
// Lo que la plantilla NO puede poner es la parte propia del curso: su libreria
// de piezas y sus numeros. Eso se marca con un hueco senalado.
//
// "En blanco" es la opcion por defecto: quien ya sabe lo que hace no pierde ni
// un clic (el dialogo se comporta exactamente como antes de existir esto).

// Cabecera comun: imports, marca, sombra de Text y fondo.
const BASE = `# =====================================================================
# CO.DE Academy - "%NOMBRE%"
# Bloque de estilo del proyecto. Se antepone al script de CADA clip; los
# clips NO repiten imports: solo definen su clase ClipN(Scene).
# =====================================================================
import math
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
from code_brand import (CODE_ACCENT, CODE_ACCENT_2, CODE_BG, CODE_INK,
                        CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD, Rotulos,
                        esquinas_hud, etiqueta_hud, marca_agua,
                        registrar_fuentes, titulo_marca)
%LECCION%
# --- Tipografia de marca ---------------------------------------------
registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

_TextBase = Text


class Text(_TextBase):
    """Sombra de Text que descarta los glifos vacios (espacios).

    Manim 0.20.1 deja el glifo del espacio anclado donde nacio el texto:
    al mover el mobject, el bounding box se infla y rompe next_to / Brace.
    Filtrarlos tras construir lo deja estable.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


_code_brand.Text = Text

# --- Libreria propia del curso ----------------------------------------
# Aqui van las piezas y los numeros de ESTE curso, en un modulo de
# studio/content/manim_extensions/ (p. ej. relatividad.py). Regla del
# pipeline: todo valor que se rotule sale calculado o medido de la
# libreria, nunca escrito a mano en el clip.
#
#     import mi_libreria as _mi_libreria
#     from mi_libreria import (pieza_uno, pieza_dos, VALOR_MEDIDO)
#
#     _mi_libreria.Text = Text   # que la libreria use la sombra, no el
#                                # Text de manim que reintrodujo import *

config.background_color = CODE_BG

# --- Paleta del curso -------------------------------------------------
# Un color = un ROL, y el mismo rol conserva su color en los 8 clips.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_ACENTO = CODE_ACCENT
C_ACENTO_2 = CODE_ACCENT_2
C_EJE = "#31414f"            # gris azulado de mobiliario

MARGEN_PIE = 0.68


# --- Rotulos ----------------------------------------------------------
def titulo_curso(texto, font_size=34, color=None):
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
    if t.width > config.frame_width - 2.0:
        t.scale_to_fit_width(config.frame_width - 2.0)
    t.to_edge(UP, buff=0.52)
    return t


def pie_curso(texto, font_size=25, color=None):
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return t


def formula_pie(tex, font_size=34, color=None):
    m = MathTex(tex, font_size=font_size,
                color=C_ACENTO if color is None else color)
    if m.width > config.frame_width - 3.0:
        m.scale_to_fit_width(config.frame_width - 3.0)
    m.to_edge(DOWN, buff=MARGEN_PIE)
    return m


def hud_modulo(texto):
    t = etiqueta_hud(texto)
    t.to_corner(UL, buff=0.5)
    return t


def tag_junto(mobjeto, texto, direccion=DOWN, buff=0.16, font_size=18,
              color=None):
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    t.set_opacity(0.85)
    t.next_to(mobjeto, direccion, buff=buff)
    return t


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
`

// Clip de arranque: renderiza y ya trae la marca puesta, para que el primer
// render funcione antes de escribir nada. Dura ~4 s: el distintivo de
// duracion lo marcara en ambar hasta que crezca a los 28-45 s del formato.
function clipInicial(n, titulo) {
  return `class Clip${n}(Scene):
    def construct(self):
        titulo = titulo_curso("${titulo}")
        pie = pie_curso("Una frase que resuma la idea de este clip.")

        self.play(FadeIn(titulo), run_time=0.8)
        self.play(FadeIn(pie), run_time=0.6)
        self.wait(2)
`
}

function clips(n) {
  return Array.from({ length: n }, (_, i) => ({
    title: `${i + 1} · Sin título`,
    scene: `Clip${i + 1}`,
    script: clipInicial(i + 1, `Clip ${i + 1}`),
  }))
}

function styleBlock(nombre, leccion) {
  return BASE
    .replace('%NOMBRE%', nombre || 'Curso nuevo')
    .replace('%LECCION%', leccion ? `\nLECCION = "${leccion}"\n` : '')
}

export const PLANTILLAS = [
  {
    id: 'blanco',
    nombre: 'En blanco',
    resumen: 'Proyecto vacío, sin estilo ni clips. El comportamiento de siempre.',
    quality: 'qm',
    clips: 0,
    build: () => ({ styleBlock: '', clips: [] }),
  },
  {
    id: 'monografico',
    nombre: 'Curso monográfico',
    resumen: '8 clips a 1080p con el tema oficial CO.DE Academy y un clip de arranque que ya renderiza.',
    quality: 'qh',
    clips: 8,
    build: ({ nombre }) => ({ styleBlock: styleBlock(nombre), clips: clips(8) }),
  },
  {
    id: 'leccion',
    nombre: 'Lección de una familia',
    resumen: '4 clips a 1080p. Para una lección «Familia · N.M Título»; añade la constante LECCION al estilo.',
    quality: 'qh',
    clips: 4,
    // La leccion sale del propio nombre: "Metrología óptica · 1.1 La luz…"
    build: ({ nombre }) => ({
      styleBlock: styleBlock(nombre, leccionDe(nombre)),
      clips: clips(4),
    }),
  },
]

/** "Familia · 1.1 Título" → "1.1" (vacio si el nombre no lo trae). */
export function leccionDe(nombre) {
  const m = /·\s*(\d+\.\d+)/.exec(nombre || '')
  return m ? m[1] : ''
}

export function plantillaPorId(id) {
  return PLANTILLAS.find((p) => p.id === id) || PLANTILLAS[0]
}

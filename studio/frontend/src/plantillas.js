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

// ── promo de redes ─────────────────────────────────────────────────────────
//
// Un promo no es una leccion, y su plantilla tampoco: el lienzo lo elige el
// PROYECTO (Formato: vertical/cuadrado/horizontal) y la escena lo aplica con
// `promo.formato()`, que lee lo que el backend le pasa al contenedor. Por eso
// el mismo codigo sale en 9:16 y en 16:9 sin tocar una linea.
const PROMO = `# =====================================================================
# CO.DE Academy - promo "%NOMBRE%"
# Bloque de estilo de un PROMO de redes. Un promo no es un clip de curso:
#   - dura 8-15 s y se ve EN BUCLE: el ultimo frame tiene que ser el primero;
#   - no lleva subtitulos (solo imagen y sonido);
#   - la app se come los bordes de la pantalla: nada que importe puede caer
#     fuera de la zona segura (FMT.tope / FMT.suelo / FMT.centro_util).
# El lienzo NO se escribe aqui: lo elige el proyecto y lo aplica formato().
# =====================================================================
import math
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
import promo as _promo
from code_brand import (CODE_ACCENT, CODE_ACCENT_2, CODE_BG, CODE_INK,
                        CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD, aplicar_marca,
                        etiqueta_hud, registrar_fuentes)

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

config.background_color = CODE_BG

# --- El lienzo, tal como lo pidio el proyecto -------------------------
# Vertical: 1080x1920. Horizontal: 1920x1080. La escala del mundo es la
# misma en los dos (135 px por unidad), asi que una escena bien compuesta
# solo necesita RECOLOCAR piezas, nunca re-dimensionarlas.
FMT = _promo.formato()

# --- Paleta del promo -------------------------------------------------
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_CIFRA = CODE_ACCENT
C_PIEZA = CODE_ACCENT_2

# --- Libreria propia del promo ----------------------------------------
# Regla del pipeline: toda cifra que se rotule sale CALCULADA de una
# libreria de studio/content/manim_extensions/, nunca escrita a mano.


def cifra(valor, decimales=2, font_size=64):
    """El numero grande, en monoespaciada para que no baile al cambiar."""
    return Text(f"{valor:.{decimales}f}", font=FUENTE_HUD,
                font_size=font_size, color=C_CIFRA)


def rotulo(texto, font_size=18, color=None):
    return etiqueta_hud(texto, font_size=font_size,
                        color=C_TENUE if color is None else color)


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        # marca=False: la marca de agua de fabrica va a la esquina inferior
        # derecha, que en vertical es la columna de botones de la app.
        # marca_promo() la coloca donde SI se ve.
        aplicar_marca(self, esquinas=True, marca=False, fondo=True)
        self.add(_promo.fondo_seguro(FMT), _promo.marca_promo(FMT))
`

// Clip de arranque de un promo: renderiza, cabe en la zona segura y CIERRA
// EL BUCLE (termina en el mismo estado en que empieza). ~10.7 s.
const PROMO_CLIP = `class Promo(Scene):
    def construct(self):
        fmt = FMT
        centro = fmt.centro_util
        r0, r1 = 0.35, fmt.radio_max()

        titulo = rotulo("CAMBIA ESTE ROTULO", font_size=20)
        # La marca vive en el borde de arriba (marca_promo): el rotulo baja
        # para no pegarse a ella.
        titulo.move_to(UP * (fmt.tope - 0.95))
        anillo = Circle(radius=r0, stroke_color=C_PIEZA, stroke_width=4)
        anillo.move_to(centro)
        lectura = VGroup(cifra(r0).move_to(UP * (fmt.suelo + 1.05)))

        # --- estado 0: es el arranque Y el cierre --------------------
        self.add(titulo, anillo, lectura)
        self.wait(0.35)

        # Todo lo que cambia frame a frame va DENTRO del play: un updater
        # sobre un mobject que no participa de la animacion se ejecuta,
        # pero manim cachea el frame estatico y NO se ve.
        vivo = VGroup(anillo, lectura)

        def respirar(m, alpha, ida=True):
            t = alpha if ida else 1.0 - alpha
            r = r0 + (r1 - r0) * t
            anillo.become(Circle(radius=r, stroke_color=C_PIEZA,
                                 stroke_width=4).move_to(centro))
            lectura.become(VGroup(cifra(r).move_to(UP * (fmt.suelo + 1.05))))

        self.play(UpdateFromAlphaFunc(vivo, respirar),
                  run_time=5.0, rate_func=smooth)
        self.play(UpdateFromAlphaFunc(vivo, lambda m, a: respirar(m, a, False)),
                  run_time=5.0, rate_func=smooth)
        self.wait(0.35)
`

export const PLANTILLAS = [
  {
    id: 'blanco',
    nombre: 'En blanco',
    resumen: 'Proyecto vacío, sin estilo ni clips. El comportamiento de siempre.',
    quality: 'qm',
    formato: 'horizontal',
    tipo: 'curso',
    clips: 0,
    build: () => ({ styleBlock: '', clips: [] }),
  },
  {
    id: 'monografico',
    nombre: 'Curso monográfico',
    resumen: '8 clips a 1080p con el tema oficial CO.DE Academy y un clip de arranque que ya renderiza.',
    quality: 'qh',
    formato: 'horizontal',
    tipo: 'curso',
    clips: 8,
    build: ({ nombre }) => ({ styleBlock: styleBlock(nombre), clips: clips(8) }),
  },
  {
    id: 'leccion',
    nombre: 'Lección de una familia',
    resumen: '4 clips a 1080p. Para una lección «Familia · N.M Título»; añade la constante LECCION al estilo.',
    quality: 'qh',
    formato: 'horizontal',
    tipo: 'curso',
    clips: 4,
    // La leccion sale del propio nombre: "Metrología óptica · 1.1 La luz…"
    build: ({ nombre }) => ({
      styleBlock: styleBlock(nombre, leccionDe(nombre)),
      clips: clips(4),
    }),
  },
  {
    id: 'promo',
    nombre: 'Promo de redes',
    resumen: '1 clip vertical (1080×1920) en bucle, con la marca donde la app no la tapa. Para Instagram/TikTok/Shorts.',
    quality: 'qh',
    formato: 'vertical',
    tipo: 'promo',
    clips: 1,
    build: ({ nombre }) => ({
      styleBlock: PROMO.replace('%NOMBRE%', nombre || 'Promo nuevo'),
      clips: [{ title: '1 · Promo', scene: 'Promo', script: PROMO_CLIP }],
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

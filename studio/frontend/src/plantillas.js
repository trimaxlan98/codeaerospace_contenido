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

// --- Pieza de simulacion (paquete `emergencia`) -----------------------
// Aqui el fondo NO es un fondo: es el sistema. Un simulador de numpy produce
// una pila de fotogramas y `emergencia.Pelicula` la presenta a pantalla
// completa; los mobjects de manim quedan para la cifra, el HUD y el enfasis.
// Documentacion: studio/docs/EMERGENCIA.md
const SIMULACION = `# =====================================================================
# CO.DE Academy - "%NOMBRE%"
# Bloque de estilo de una PIEZA DE SIMULACION.
#
# El fotograma entero lo calcula numpy en el render (paquete emergencia):
# miles de agentes o una malla de cientos de miles de celdas, presentados
# como un ImageMobject que cambia frame a frame. Manim pone encima la CIFRA
# medida, el HUD y las reglas del sistema.
#
# Reglas: toda cifra en pantalla sale de la simulacion de ESTE render (cian);
# lo que venga de literatura va en gris. El lienzo lo elige el PROYECTO
# (Formato: vertical / cuadrado / horizontal).
# =====================================================================
import os
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
import emergencia as em
import promo as _promo
from code_brand import (CODE_BG, CODE_INK, CODE_MUTED, FUENTE_DISPLAY,
                        FUENTE_HUD, esquinas_hud, registrar_fuentes)

registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

FMT = _promo.formato()
config.background_color = CODE_BG

# --- Renglones (todo lo que importa cae en la zona que la app no tapa) ---
Y_HUD = FMT.tope - 0.78
Y_REGLAS = Y_HUD - 0.62
PASO_REGLAS = 0.40
Y_ETIQUETA = FMT.suelo + 1.72
Y_NUMERO = FMT.suelo + 1.05
Y_SUB = FMT.suelo + 0.25
ANCHO_SEGURO = 2.0 * min(FMT.ancho / 2 - FMT.margen["izq"],
                         FMT.ancho / 2 - FMT.margen["der"])

# --- Paleta por ROL (un color = un significado) -------------------------
C_MEDIDO = em.C_MEDIDO      # cian: TODA cifra calculada aqui
C_REGLA = em.C_REGLA        # ambar: la regla, el agente que sigue la camara
C_ORDEN = em.C_ORDEN        # violeta: lo ordenado
C_ENERGIA = em.C_ENERGIA    # naranja: energia, lo que escapa
C_VIVO = em.C_VIVO          # verde: lo vivo
C_EXTERNO = CODE_MUTED      # gris: lo que NO se mide aqui


def cabe(mob, que="texto"):
    """Aborta el render si el rotulo se sale de la zona segura."""
    if mob.width > ANCHO_SEGURO + 1e-6:
        raise ValueError(f"{que} mide {mob.width:.2f} y caben "
                         f"{ANCHO_SEGURO:.2f}: acortalo")
    return mob


def hud(texto, font_size=19, color=CODE_MUTED):
    t = Text(" ".join(str(texto).upper()), font=FUENTE_HUD,
             font_size=font_size, color=color)
    return cabe(t, f'HUD "{texto}"')


def hud_pieza(texto, color=CODE_MUTED):
    t = hud(texto, font_size=19, color=color)
    t.move_to(UP * Y_HUD)
    t.set_z_index(900)
    return t


def reglas(textos, color=C_REGLA, font_size=17):
    """Las 2-3 reglas del sistema, en columna bajo el HUD."""
    g = VGroup()
    for i, t in enumerate(textos):
        et = hud(t, font_size=font_size, color=color)
        et.move_to(UP * (Y_REGLAS - i * PASO_REGLAS))
        et.set_z_index(850)
        g.add(et)
    return g


def cifra(texto, font_size=104, color=C_MEDIDO):
    t = Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)
    return cabe(t, f'cifra "{texto}"')


def medida(valor, etiqueta=None, sub=None, color=C_MEDIDO,
           color_sub=C_REGLA, font_size=104):
    """El pie: etiqueta / CIFRA / condicion, en renglones fijos."""
    g = VGroup()
    num = cifra(valor, font_size=font_size, color=color)
    num.move_to(UP * Y_NUMERO)
    g.numero, g.etiqueta, g.sub = num, None, None
    g.add(num)
    if etiqueta is not None:
        et = hud(etiqueta, font_size=20, color=CODE_MUTED)
        et.move_to(UP * Y_ETIQUETA)
        g.etiqueta = et
        g.add(et)
    if sub is not None:
        sb = hud(sub, font_size=18, color=color_sub)
        sb.move_to(UP * Y_SUB)
        g.sub = sb
        g.add(sb)
    g.set_z_index(800)
    return g


def velos_de_contraste(opacidad=0.66, transicion=1.4, z=-450):
    """Banda oscura + degradado detras del texto: cuando la simulacion es
    CLARA (un laberinto, una mandala) el HUD gris desaparece sin esto."""
    borde = FMT.alto / 2 + 0.3
    y_arriba = Y_REGLAS - 3 * PASO_REGLAS - 0.30
    y_abajo = Y_ETIQUETA + 0.42
    ancho = FMT.ancho + 0.4
    piezas = []
    for y, sentido in ((y_arriba, UP), (y_abajo, DOWN)):
        alto = (borde - y) if sentido is UP else (y + borde)
        banda = Rectangle(width=ancho, height=alto, stroke_width=0,
                          fill_color=CODE_BG, fill_opacity=opacidad)
        banda.move_to(UP * ((borde + y) / 2 if sentido is UP
                            else (y - borde) / 2))
        deg = Rectangle(width=ancho, height=transicion, stroke_width=0)
        deg.set_fill(color=CODE_BG, opacity=[0.0, opacidad])
        deg.set_sheen_direction(sentido)
        deg.move_to(UP * (y - transicion / 2 if sentido is UP
                          else y + transicion / 2))
        piezas += [banda, deg]
    for v in piezas:
        v.set_z_index(z)
    return piezas


def pelicula(frames, nearest=False, y=0.0, z=-500):
    """La simulacion como fondo a pantalla completa."""
    return em.Pelicula(frames, alto=FMT.alto, y=y, nearest=nearest, z=z)


def px_a_escena(xy, pieza, W, H):
    """Pixeles de la pila -> coordenadas de escena sobre la pelicula, para
    dibujar enfasis vectorial EXACTAMENTE encima de un agente."""
    xy = np.asarray(xy, dtype=np.float64)
    if xy.ndim == 1:
        xy = xy[None, :]
    c = pieza.get_center()
    x = c[0] - pieza.width / 2 + (xy[:, 0] + 0.5) / W * pieza.width
    y = c[1] + pieza.height / 2 - (xy[:, 1] + 0.5) / H * pieza.height
    return np.column_stack([x, y, np.zeros(len(x))])


def cerrar_pieza(escena, run_time=0.9, cola=0.4):
    for mob in escena.mobjects:
        mob.clear_updaters()
    escena.play(*[FadeOut(m) for m in escena.mobjects], run_time=run_time)
    escena.remove(*escena.mobjects)
    escena.wait(cola)


_SceneBase = Scene


class Scene(_SceneBase):
    """Fondo de marca + esquinas + marca de agua + velos de contraste."""

    marca_chica = True
    esquinas = True
    velos = True

    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(_promo.fondo_seguro(FMT))
        if self.velos:
            self.add(*velos_de_contraste())
        if self.esquinas:
            self.add(esquinas_hud(opacidad=0.14))
        if self.marca_chica:
            self.add(_promo.marca_promo(FMT, opacidad=0.34))
`

const SIMULACION_CLIP = `class Clip(Scene):
    """Tres reglas, 1200 agentes, ningun jefe.

    Cambia \`em.bandada\` por cualquiera de los trece simuladores del paquete
    (moho, arena, vida, turing, ondas, chladni, ising, pendulos, cuencas,
    epiciclos, rio, galaxias): todos devuelven lo mismo — \`frames\`, \`cifras\`
    y \`extra\` —, asi que el resto del clip no cambia.
    Ver studio/docs/EMERGENCIA.md.
    """

    def construct(self):
        # 1. Medir ANTES de dibujar: una sola llamada, al principio.
        #    (pasos=420 para que la vista previa sea rapida; sube a 900
        #     cuando la pieza este lista)
        r = em.bandada.simular(semilla=1, pasos=420, agentes=1200)
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        pol = np.asarray(extra["polarizacion"], dtype=np.float64)
        T = len(F)

        # 2. La simulacion es el fondo, desde el primer frame.
        peli = pelicula(F)
        self.add(peli.mob)

        marca = hud_pieza("simulacion")
        regs = reglas(["1 . separarse", "2 . alinearse", "3 . juntarse"])
        pie = medida("0.00", "polarizacion", f"{cifras['agentes']} agentes",
                     color_sub=C_VIVO)

        # 3. El contador se pre-renderiza y se cambia con become DENTRO de
        #    la animacion (nunca always_redraw con Text).
        cache = {}

        def texto(k):
            v = round(float(pol[min(k, T - 1)]), 2)
            if v not in cache:
                t = cifra(f"{v:.2f}")
                t.move_to(UP * Y_NUMERO)
                cache[v] = t
            return cache[v]

        contador = VGroup(pie.numero)
        contador.set_z_index(800)

        def tramo(run_time, desde, hasta, *otras, ritmo=None, encuadre=None):
            def cuenta(_m, alpha):
                f = ritmo(alpha) if ritmo else alpha
                contador[0].become(texto(int(round(desde + f * (hasta - desde)))))
            self.play(peli.animacion(run_time, desde=desde, hasta=hasta,
                                     ritmo=ritmo, encuadre=encuadre),
                      UpdateFromAlphaFunc(contador, cuenta, run_time=run_time,
                                          rate_func=linear),
                      *otras, run_time=run_time)

        pie.remove(pie.numero)
        self.add(contador)
        self.play(FadeIn(marca, shift=DOWN * 0.16), FadeIn(pie.etiqueta),
                  FadeIn(pie.sub), peli.animacion(0.6, desde=0, hasta=18),
                  run_time=0.6)
        for i, et in enumerate(regs):
            tramo(1.2, 18 + i * 36, 54 + i * 36, FadeIn(et, shift=RIGHT * 0.15))

        # 4. La camara se pega al agente ambar (la trayectoria la da el
        #    simulador, en pixeles) y se abre al final.
        seguido = np.asarray(extra["seguido"], dtype=np.float64)
        sig = em.seguir(seguido, 2.0)
        f0, f1 = 126, min(300, T - 1)

        def acercar(frac, W, H):
            k = f0 + frac * (f1 - f0)
            cx, cy, _ = sig(k / (T - 1), W, H)
            return cx, cy, 1.0 + 1.0 * frac
        tramo(2.4, f0, f1, encuadre=acercar)
        tramo(max(0.8, (T - 1 - f1) / 30.0), f1, T - 1)
        self.wait(0.8)

        cerrar_pieza(self)
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
{
    id: 'simulacion',
    nombre: 'Pieza de simulación',
    resumen: '1 clip donde el fotograma ENTERO es una simulación numpy (paquete emergencia): miles de agentes o una malla, con cámara y cifra medida. Vertical por defecto; sirve igual en 16:9.',
    quality: 'qh',
    formato: 'vertical',
    tipo: 'curso',
    clips: 1,
    build: ({ nombre }) => ({
      styleBlock: SIMULACION.replace('%NOMBRE%', nombre || 'Pieza de simulación'),
      clips: [{ title: '1 · Simulación', scene: 'Clip', script: SIMULACION_CLIP }],
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
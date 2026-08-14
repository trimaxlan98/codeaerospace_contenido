# =====================================================================
# CO.DE Academy - "Sistemas distribuidos: la nube por dentro"
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

import distribuido as _distribuido  # noqa: E402  (tras definir la sombra)
from distribuido import (CIUDADES, P_MAQUINA, V_FIBRA_KMS,  # noqa: E402
                         anillo_hash, asignacion_anillo, corona,
                         curva_caidas, diagrama_lamport,
                         disponibilidad_replicas, distancia_km,
                         fraccion_movida, indices_caidos,
                         interseccion_quorum, linea_latencia,
                         nodos_quorum, par_centros, prob_alguna_caida,
                         rejilla_nodos, relojes_lamport, rondas_eleccion,
                         rtt_ms)

_distribuido.Text = Text

_RotulosBase = Rotulos


class Rotulos(_RotulosBase):
    """Relevo SECUENCIAL por zona: el rotulo anterior sale ANTES de que
    entre el nuevo (el original los cruza ~0.5 s)."""

    def mostrar(self, mobjeto, zona="abajo", run_time=0.45, salida=0.25,
                **kwargs):
        if self._zonas.get(zona) is not None:
            self.limpiar(zona, run_time=salida)
        return super().mostrar(mobjeto, zona=zona, run_time=run_time,
                               **kwargs)

config.background_color = CODE_BG

# --- Paleta del curso -------------------------------------------------
# Regla: los MENSAJES (datos viajando) son ambar; los NODOS (replicas,
# lo medido) cian; la MAYORIA y lo disponible verde; las CAIDAS y la
# particion rojo; el TIEMPO LOGICO y el anillo de hash violeta.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_ACENTO = CODE_ACCENT
C_ACENTO_2 = CODE_ACCENT_2
C_MENSAJE = "#f59e0b"        # ambar: mensajes, datos viajando
C_NODO = "#22d3ee"           # cian: nodos, replicas, lo medido
C_OK = "#34d399"             # verde: mayoria, quorum, disponible
C_FALLO = "#f43f5e"          # rojo: caidas, particion, split-brain
C_TIEMPO = "#a78bfa"         # violeta: relojes logicos, el anillo
C_EJE = "#31414f"            # gris azulado de mobiliario

MARGEN_PIE = 0.68

# --- Numeros del curso ------------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria (calculado o
# medido sobre el dibujo), nunca escrito a mano en el clip.
P_CAIDA_10 = prob_alguna_caida(10)          # 1.0 %
P_CAIDA_100 = prob_alguna_caida(100)        # 9.5 %
P_CAIDA_1000 = prob_alguna_caida(1000)      # 63.2 %
NUEVE_NUEVES = disponibilidad_replicas(3)   # 0.999999999
RTT_NY = rtt_ms("CDMX", "Nueva York")       # 33.6 ms (piso fisico)
RTT_MADRID = rtt_ms("CDMX", "Madrid")       # 90.6 ms
RTT_TOKIO = rtt_ms("CDMX", "Tokio")         # 113.1 ms
DIST_TOKIO = distancia_km("CDMX", "Tokio")  # 11 307 km
N_QUORUM, W_QUORUM, R_QUORUM = 5, 3, 3
INTERSECCION = interseccion_quorum(N_QUORUM, W_QUORUM, R_QUORUM)  # 1
IDX_W, IDX_R = (0, 1, 2), (2, 3, 4)         # los conjuntos del clip 5
# Eleccion (clip 6): semilla validada en contenedor -> termino 1 elige
# al nodo 3, muere, termino 2 empata (candidatos 0/2/4), termino 3
# elige al nodo 2. Ver rondas_eleccion(SEMILLA_ELECCION).
SEMILLA_ELECCION = 4
# Anillo (clip 7): nombre validado -> su arco reubica ~29 % (7 de 24
# claves), del orden del 1/(n+1) teorico.
NODO_NUEVO = "nodo-nuevo-0"
SEMILLA_CAIDOS = 11                          # los caidos del clip 1


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


def tag_hud(texto, font_size=15, color=None):
    """Cifra medida (Space Mono) SIN posicion: el clip la coloca."""
    t = Text(texto, font=FUENTE_HUD, font_size=font_size,
             color=C_NODO if color is None else color)
    return t


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())

# =====================================================================
# CO.DE Academy - "Electromagnetismo · 3.2 La reflexión y la onda
# estacionaria". Bloque de estilo del proyecto. Se antepone al script de
# CADA clip; los clips NO repiten imports: solo definen su ClipN(Scene).
#
# Este bloque es el MOLDE de la familia "Electromagnetismo": las 11
# lecciones restantes copian este archivo y solo cambian la cabecera y
# la tabla de numeros de su leccion. Por eso la paleta, los rotulos y
# los helpers viven aqui y no en un clip.
# =====================================================================
import math
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import bloques as _bloques
import code_brand as _code_brand
from bloques import bloque, conectar, flujo
from brillo import con_brillo, punto_brillante
from code_brand import (CODE_ACCENT, CODE_ACCENT_2, CODE_BG, CODE_INK,
                        CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD, Rotulos,
                        esquinas_hud, etiqueta_hud, marca_agua,
                        registrar_fuentes, titulo_marca)
from senal import destello
from transiciones import (transicion_deslizar, transicion_persiana,
                          transicion_zoom)

# --- Tipografia de marca ---------------------------------------------
# El default se fija sobre el Text ORIGINAL de Manim (antes de la sombra)
# para que tambien lo hereden los helpers de bloques.py / code_brand.py.
registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

_TextBase = Text


class Text(_TextBase):
    """Sombra de Text que descarta los glifos vacios (espacios).

    Manim 0.20.1 deja el glifo del espacio anclado donde nacio el texto: al
    mover el mobject, el bounding box se infla y rompe next_to / Brace /
    SurroundingRectangle. Filtrarlos tras construir lo deja estable sin
    alterar la posicion de las letras (ya esta horneada).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


# Los helpers de las librerias tambien deben usar la sombra.
_bloques.Text = Text
_code_brand.Text = Text

import electromagnetismo as _em  # noqa: E402  (tras definir la sombra)
from electromagnetismo import (BANDAS, B_TIERRA_EC, C_LUZ,  # noqa: E402
                               EPS0, K_BOLTZMANN, K_COULOMB, MU0,
                               MU_TIERRA, M_ELECTRON, Q_E, R_TIERRA,
                               R_TIERRA_EQ, T_SIDERAL, alternador,
                               angulo_apuntado, arco_familia, array_fases,
                               atenuacion_lluvia, b_hilo, b_solenoide,
                               b_tierra, banda_de, banda_espectro_em,
                               barras_retardo, c_de_constantes, cable_onda,
                               caja_gauss, campo_de_flujo,
                               campo_dipolo_eje, campo_puntual,
                               capas_ionosfera, carga, cielo_ruido,
                               condensador_ampere, corte_coaxial,
                               corte_microstrip, coulomb, cubesat_torquer,
                               curvas_flujo_fem, db_de, dipolo_radiante,
                               directividad, equipotenciales,
                               esfera_reparto, espejo_magnetico,
                               espira_iman, f_de, factor_array, fc_te10,
                               fem_espira, flujo_isotropo,
                               frecuencia_giro, frecuencia_plasma,
                               frontera_z, fspl_db, gamma_de,
                               ganancia_apertura, giro_larmor, guia_te10,
                               haz_curvas, hilo_corriente,
                               impedancia_vacio, lambda_de, linea_cuartos,
                               linea_lc, lineas_campo, mapa_orbitas,
                               margen_enlace, onda_em, onda_estacionaria,
                               par_torquer, parabola_foco, pase_leo,
                               pase_leo_geometria, patron_dipolo_corto,
                               patron_dipolo_medio, patron_polar,
                               radio_geo, radio_larmor, rebote_hf,
                               retardo_iono, ruido_dbw, solenoide_corte,
                               swr_de, t_orbital, tiempo_giro_torquer,
                               tierra_iman, transformador,
                               traza_polarizacion, tubo_ondas, v_orbital,
                               ventana_iono, z0_coaxial, z_cuarto)

_em.Text = Text

_RotulosBase = Rotulos


class Rotulos(_RotulosBase):
    """Relevo SECUENCIAL por zona: el rotulo anterior sale ANTES de que
    entre el nuevo.

    El original cruza ambos en la misma animacion y durante ~0.5 s se ven
    superpuestos (dos frases a la vez en el pie). Aqui nunca coinciden.
    """

    def mostrar(self, mobjeto, zona="abajo", run_time=0.45, salida=0.25,
                **kwargs):
        if self._zonas.get(zona) is not None:
            self.limpiar(zona, run_time=salida)
        return super().mostrar(mobjeto, zona=zona, run_time=run_time,
                               **kwargs)


config.background_color = CODE_BG

# --- Paleta del curso -------------------------------------------------
# Regla: EL COLOR DICE QUIEN ACTUA. Rojo la fuente (cargas, corrientes,
# el emisor); ambar el campo electrico; verde el magnetico; violeta los
# dos casados y viajando (la onda, la señal); cian lo que se CALCULA.
C_TITULO = CODE_INK          # #e8edf3 titulos
C_TENUE = CODE_MUTED         # #94a0b0 pies y elementos secundarios
C_ACENTO = CODE_ACCENT       # #f59e0b ambar
C_ACENTO_2 = CODE_ACCENT_2   # #ea580c naranja de cierre
C_CARGA = "#f43f5e"          # rojo: las fuentes (cargas, corrientes)
C_E = "#f59e0b"              # ambar: campo electrico
C_B = "#34d399"              # verde: campo magnetico
C_ONDA = "#a78bfa"           # violeta: la onda, la señal radiada
C_CALCULO = "#22d3ee"        # cian: umbrales, cifras, resultados
C_EJE = "#31414f"            # gris azulado de mobiliario

MARGEN_PIE = 0.68            # separacion del pie al borde inferior

# --- Numeros de la leccion --------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria, nunca escrito a
# mano en el clip: la curva dibujada y la cifra escrita no pueden
# discrepar.
Z_LINEA = 50.0                            # ohm: la linea que trae la onda
Z_CARGA = 75.0                            # ohm: lo que hay al otro lado
GAMMA_SALTO = gamma_de(Z_CARGA, Z_LINEA)  # 0.2 en el salto 50 -> 75
GAMMA_ADAPTADO = gamma_de(Z_LINEA, Z_LINEA)      # 0: no vuelve nada
GAMMA_CORTO = gamma_de(0.0, Z_LINEA)             # -1: vuelve TODO, invertida
GAMMA_ABIERTO = gamma_de(float("inf"), Z_LINEA)  # +1: vuelve TODO
SWR_SALTO = swr_de(GAMMA_SALTO)           # 1.5: el que mide el instalador
Z_ADAPTA = z_cuarto(Z_LINEA, Z_CARGA)     # 61.2 ohm = sqrt(Z1 Z2)
A_WR90 = 0.02286                          # m: ancho de la guia WR-90
FC_WR90 = fc_te10(A_WR90)                 # 6.557 GHz: corte del TE10
F_GUIA_LEJOS = 10e9                       # Hz: lejos del corte, avanza
F_GUIA_CERCA = 7e9                        # Hz: casi en el corte, se empina


# --- Rotulos ----------------------------------------------------------
def titulo_curso(texto, font_size=34, color=None):
    """Titulo de clip (Rajdhani) anclado arriba. Zona 'arriba' de Rotulos."""
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
    if t.width > config.frame_width - 2.0:
        t.scale_to_fit_width(config.frame_width - 2.0)
    t.to_edge(UP, buff=0.52)
    return t


def pie_curso(texto, font_size=25, color=None):
    """Pie narrativo anclado abajo. Zona 'abajo' de Rotulos."""
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return t


def formula_pie(tex, font_size=34, color=None):
    """MathTex corto que ocupa la MISMA zona que el pie (nunca se suman)."""
    m = MathTex(tex, font_size=font_size,
                color=C_CALCULO if color is None else color)
    if m.width > config.frame_width - 3.0:
        m.scale_to_fit_width(config.frame_width - 3.0)
    m.to_edge(DOWN, buff=MARGEN_PIE)
    return m


def hud_modulo(texto):
    """Etiqueta de telemetria del modulo, esquina superior izquierda."""
    t = etiqueta_hud(texto)
    t.to_corner(UL, buff=0.5)
    return t


def tag_junto(mobjeto, texto, direccion=DOWN, buff=0.16, font_size=18,
              color=None):
    """Etiqueta corta de mobiliario pegada a un mobject (no narrativa)."""
    t = Text(texto, font_size=font_size,
             color=C_TENUE if color is None else color)
    t.set_opacity(0.85)
    t.next_to(mobjeto, direccion, buff=buff)
    return t


def tag_hud(texto, font_size=17, color=None):
    """Cifra o etiqueta tecnica en Space Mono (SOLO ASCII: sin acentos ni
    superindices — Space Mono no los trae)."""
    t = Text(texto, font=FUENTE_HUD, font_size=font_size,
             color=C_CALCULO if color is None else color)
    return t


def llave(mobjeto, texto=None, direccion=UP, font_size=22, color=None,
          buff=0.12):
    """Brace opcionalmente etiquetado (etiquetas de 1-2 palabras)."""
    col = C_CALCULO if color is None else color
    b = Brace(mobjeto, direction=direccion, color=col)
    if texto is None:
        return VGroup(b)
    t = Text(texto, font_size=font_size, color=col)
    t.next_to(b, direccion, buff=buff)
    return VGroup(b, t)


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())

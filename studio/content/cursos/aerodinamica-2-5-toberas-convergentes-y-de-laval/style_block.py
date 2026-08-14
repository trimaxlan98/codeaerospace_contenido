# =====================================================================
# CO.DE Academy - "Aerodinámica · 2.5 Toberas convergentes y De Laval".
# Bloque de estilo del proyecto. Se antepone al script de CADA
# clip; los clips NO repiten imports: solo definen su clase ClipN(Scene).
#
# Este bloque es el MOLDE de la familia "Aerodinámica": las 19 lecciones
# restantes del documento maestro copian este archivo y solo cambian la
# tabla de numeros de su leccion. Por eso la paleta, los rotulos y el
# mobiliario (siluetas) viven aqui y no en un clip.
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

import aerodinamica as _aero  # noqa: E402  (tras definir la sombra)
from aerodinamica import (COMPRESION_MAXIMA, GAMMA,  # noqa: E402
                          NU_MAXIMO, REGIMENES, REGIMENES_TOBERA, R_AIRE,
                          abanico_expansion, angulo_mach, balanza_energias,
                          banda_regimenes, barras_calores, barras_entalpia,
                          choque_normal, choque_oblicuo, conducto, criticas,
                          curva_anemometro, curva_area_mach, curva_mu,
                          curva_nu, curva_sonido, curvas_choque,
                          curvas_isentropicas, diagrama_theta_beta,
                          diagrama_ts, diagrama_xt, error_anemometro,
                          error_incompresible, escalera_velocidades,
                          esquema_schlieren, expansion, fraccion_cinetica,
                          frentes_moviles, interseccion_choques, isa,
                          mach_de_area, mach_de_error, mach_de_nu,
                          onda_oblicua, perfil_choque, perfil_isa,
                          perfil_rombico, perfil_supersonico, perfil_tobera,
                          piston_gas, placa_plana, prandtl_meyer,
                          pulso_conducto, rayleigh_pitot, razon_area,
                          razon_densidad, razon_energias, razon_presion,
                          razon_temperatura, reflexion_onda, remanso,
                          tabla_isentropica, theta_de_beta, theta_maximo,
                          velocidad_sonido, volumen_control, zona_de)

_aero.Text = Text

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
# Regla: EL COLOR DICE A QUE VELOCIDAD SE VUELA. Cuanto mas rapido, mas
# caliente. El cian queda para lo que se CALCULA (umbrales, resultados,
# energia termica) y el gris azulado para el mobiliario.
C_TITULO = CODE_INK          # #e8edf3 titulos
C_TENUE = CODE_MUTED         # #94a0b0 pies y elementos secundarios
C_ACENTO = CODE_ACCENT       # #f59e0b ambar
C_ACENTO_2 = CODE_ACCENT_2   # #ea580c naranja de cierre
C_SUB = "#34d399"            # verde: subsonico, el aire se aparta a tiempo
C_TRANS = "#f59e0b"          # ambar: transonico, conviven sub y supersonico
C_SUPER = "#f43f5e"          # rojo: supersonico, choques
C_HIPER = "#a78bfa"          # violeta: hipersonico, calor y quimica
C_CALCULO = "#22d3ee"        # cian: umbrales, resultados, energia termica
C_EJE = "#31414f"            # gris azulado de mobiliario

MARGEN_PIE = 0.68            # separacion del pie al borde inferior

# --- Numeros de la leccion --------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria, nunca escrito a
# mano en el clip: la curva dibujada y la cifra escrita no pueden discrepar.
AREA_GARGANTA = 0.42                 # area minima relativa del De Laval
X_CHOQUE = 0.74                      # estacion del choque interno del clip 3
P_CRITICA = criticas()["p*/p0"]      # 0.5283 — la presion que bloquea
ORDEN_REGIMENES = ("venturi", "bloqueo", "choque", "diseno")
M_SALIDA_DISENO = mach_de_area(1.0 / AREA_GARGANTA, "super")   # 2.39

# La flota de la familia: (nombre, Mach de operacion, silueta, altitud m).
# Mach reales de crucero (o de reentrada, en la capsula); la altitud solo se
# usa para convertir a km/h cuando el clip lo pide.
FLOTA = (("Cessna 172", 0.20, "recta", 2500.0),
         ("Boeing 787", 0.85, "flecha", 11000.0),
         ("Concorde", 2.02, "delta", 16000.0),
         ("X-43A", 9.60, "waverider", 20000.0),
         ("Apollo", 25.0, "capsula", 20000.0))


def km_h(mach, altitud_m):
    """Velocidad real en km/h de ese Mach a esa altitud (ISA)."""
    return float(mach) * isa(float(altitud_m))[3] * 3.6


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


# --- Mobiliario: las siluetas -----------------------------------------
# Viven en el style_block y no en la libreria porque son puro mobiliario
# narrativo (el "quien vuela"), no piezas que calculen nada. Todas miran a
# la DERECHA, la misma direccion de marcha que usa `frentes_moviles`, y se
# normalizan a ancho 1 para que `escala` sea directamente su ancho en
# unidades de escena.
_PLANTAS = {
    # Ala recta y fuselaje largo: aviacion general, bien lejos del sonido.
    "recta": ([(0.52, 0.00), (0.18, 0.06), (-0.46, 0.05), (-0.52, 0.00),
               (-0.46, -0.05), (0.18, -0.06)],
              [[(0.16, 0.05), (0.02, 0.44), (-0.06, 0.44), (-0.02, 0.05)],
               [(0.16, -0.05), (0.02, -0.44), (-0.06, -0.44), (-0.02, -0.05)],
               [(-0.40, 0.04), (-0.48, 0.20), (-0.54, 0.20), (-0.52, 0.04)],
               [(-0.40, -0.04), (-0.48, -0.20), (-0.54, -0.20),
                (-0.52, -0.04)]]),
    # Ala en flecha: la solucion transonica (el Mach normal efectivo baja).
    "flecha": ([(0.56, 0.00), (0.20, 0.07), (-0.48, 0.06), (-0.54, 0.00),
                (-0.48, -0.06), (0.20, -0.07)],
               [[(0.20, 0.06), (-0.30, 0.46), (-0.44, 0.46), (-0.16, 0.06)],
                [(0.20, -0.06), (-0.30, -0.46), (-0.44, -0.46),
                 (-0.16, -0.06)],
                [(-0.42, 0.05), (-0.56, 0.22), (-0.62, 0.22), (-0.54, 0.05)],
                [(-0.42, -0.05), (-0.56, -0.22), (-0.62, -0.22),
                 (-0.54, -0.05)]]),
    # Delta pura: borde de ataque muy en flecha, dentro del cono de Mach.
    "delta": ([(0.62, 0.00), (0.24, 0.05), (-0.52, 0.05), (-0.58, 0.00),
               (-0.52, -0.05), (0.24, -0.05)],
              [[(0.34, 0.02), (-0.50, 0.42), (-0.58, 0.42), (-0.58, 0.02)],
               [(0.34, -0.02), (-0.50, -0.42), (-0.58, -0.42),
                (-0.58, -0.02)]]),
    # Waverider: cuerpo sustentador, casi todo morro. Hipersonico.
    "waverider": ([(0.66, 0.00), (0.10, 0.10), (-0.50, 0.16), (-0.56, 0.16),
                   (-0.56, -0.16), (-0.50, -0.16), (0.10, -0.10)],
                  [[(-0.30, 0.14), (-0.52, 0.34), (-0.60, 0.34),
                    (-0.56, 0.14)],
                   [(-0.30, -0.14), (-0.52, -0.34), (-0.60, -0.34),
                    (-0.56, -0.14)]]),
    # Capsula de reentrada, de perfil: el escudo romo va POR DELANTE. Es la
    # forma que a M 25 conviene — un morro afilado se derretiria.
    "capsula": ([(0.30, 0.40), (0.44, 0.22), (0.46, 0.00), (0.44, -0.22),
                 (0.30, -0.40), (-0.34, -0.24), (-0.40, 0.00),
                 (-0.34, 0.24)],
                []),
}


def silueta(tipo, escala=0.62, color=None, opacidad=0.9):
    """Silueta esquematica de una aeronave, mirando a la DERECHA.

    `tipo` es una clave de `_PLANTAS` ('recta', 'flecha', 'delta',
    'waverider', 'capsula'). Se normaliza a ancho 1 antes de aplicar
    `escala`, asi que dos siluetas con la misma escala ocupan lo mismo en
    pantalla aunque sus poligonos originales midan distinto.
    """
    if tipo not in _PLANTAS:
        raise ValueError(f"silueta: tipo '{tipo}' desconocido "
                         f"({', '.join(sorted(_PLANTAS))})")
    col = C_TENUE if color is None else color
    cuerpo_pts, extras = _PLANTAS[tipo]

    partes = VGroup()
    for pts in [cuerpo_pts, *extras]:
        partes.add(Polygon(*[(x, y, 0) for x, y in pts], stroke_width=1.6,
                           color=col, fill_color=col, fill_opacity=0.55))
    partes.scale_to_fit_width(1.0).scale(escala)
    partes.set_opacity(opacidad)
    return partes


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())

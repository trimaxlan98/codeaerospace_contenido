# =====================================================================
# CO.DE Academy - promo.py
# Formato y mobiliario de los clips de PROMOCION para redes sociales.
#
# Un promo no es una leccion:
#   - dura 8-15 s, no 28-45;
#   - no lleva subtitulos (solo imagen y sonido);
#   - se ve dentro de una app que se COME los bordes de la pantalla;
#   - y termina en el MISMO estado en el que empieza, para que el bucle
#     sea invisible y el video se repita solo.
#
# El formato se elige por variable de entorno (PROMO_FORMATO) para que la
# MISMA escena salga en 9:16 y en 16:9 sin tocar el codigo:
#
#     import promo
#     FMT = promo.formato()          # vertical por defecto
#
# La escala del mundo esta elegida a proposito para que **1 unidad = la
# misma cantidad de pixeles en los dos formatos** (16:9 -> 1920/14.222;
# 9:16 -> 1080/8.0 -> 135 px/unidad en ambos). Es decir: un font_size de 40
# se ve igual de grande en vertical que en horizontal, y una escena bien
# compuesta solo necesita RECOLOCAR piezas, no re-dimensionarlas.
# =====================================================================
import os

from manim import (DOWN, DR, RIGHT, UP, DashedVMobject, Dot, Rectangle,
                   VGroup, config)

import code_brand
from code_brand import CODE_ACCENT, CODE_MUTED, etiqueta_hud

# Los dos lados del mundo de manim, tal cual vienen de fabrica en 16:9.
# Intercambiarlos (y NO tocarlos) es lo que mantiene los 135 px/unidad.
LADO_MAYOR = 14.222222222222221
LADO_MENOR = 8.0

# La calidad fija el LADO CORTO en pixeles, no el alto: 1080 de lado corto
# son 1080x1920 en vertical y 1920x1080 en horizontal. Fijar el alto daria
# un 16:9 de 3413x1920, que no es "calidad alta" sino otro formato.
LADO_CORTO = {"ql": 540, "qm": 720, "qh": 1080}
FPS = {"ql": 30, "qm": 30, "qh": 60}

# Proporciones de la zona que la app NO tapa, como fraccion del lado.
# Instagram/TikTok/Shorts se comen la franja de abajo (autor, texto, CTA) y
# la columna de la derecha (corazon, comentarios, compartir). Medidas con
# margen: si algo IMPORTA, tiene que caber aqui dentro.
SEGURA = {
    "vertical": {"arriba": 0.10, "abajo": 0.20, "izq": 0.05, "der": 0.14},
    "cuadrado": {"arriba": 0.06, "abajo": 0.12, "izq": 0.05, "der": 0.05},
    "horizontal": {"arriba": 0.05, "abajo": 0.08, "izq": 0.04, "der": 0.04},
}

PROPORCIONES = {
    "vertical": (LADO_MENOR, LADO_MAYOR),
    "horizontal": (LADO_MAYOR, LADO_MENOR),
    "cuadrado": (LADO_MENOR, LADO_MENOR),
}


class Formato:
    """El lienzo del promo: mundo, pixeles y zona util de la app."""

    def __init__(self, nombre, ancho, alto, px_ancho, px_alto, fps):
        self.nombre = nombre
        self.ancho = ancho              # unidades de mundo
        self.alto = alto
        self.px_ancho = px_ancho
        self.px_alto = px_alto
        self.fps = fps
        self.es_vertical = alto > ancho
        m = SEGURA[nombre]
        self.margen = {"arriba": m["arriba"] * alto, "abajo": m["abajo"] * alto,
                       "izq": m["izq"] * ancho, "der": m["der"] * ancho}

    # --- bordes reales del lienzo -----------------------------------
    @property
    def borde_arriba(self):
        return self.alto / 2

    @property
    def borde_abajo(self):
        return -self.alto / 2

    # --- bordes de lo que la app NO tapa ----------------------------
    @property
    def tope(self):
        return self.borde_arriba - self.margen["arriba"]

    @property
    def suelo(self):
        return self.borde_abajo + self.margen["abajo"]

    @property
    def alto_util(self):
        return self.tope - self.suelo

    @property
    def centro_util(self):
        """Centro VERTICAL de la zona util. La x se deja en 0 a proposito:
        una composicion simetrica se centra, y el margen derecho solo manda
        sobre el texto y las piezas que se salen de la simetria."""
        return UP * (self.tope + self.suelo) / 2

    def radio_max(self, holgura=0.72):
        """Radio de la pieza redonda mas grande que cabe centrada."""
        return holgura * min(self.ancho, self.alto_util) / 2

    def __repr__(self):
        return (f"<Formato {self.nombre} {self.px_ancho}x{self.px_alto} "
                f"mundo {self.ancho:.2f}x{self.alto:.2f} @{self.fps}fps>")


def formato(nombre=None, calidad=None, corto_px=None, fps=None):
    """Configura manim para el formato pedido y devuelve el `Formato`.

    Se llama UNA vez, a nivel de modulo, antes de que exista la escena:
    manim importa el archivo entero antes de instanciarla, asi que aqui
    todavia se puede cambiar el lienzo.

    Sin argumentos lee el entorno (lo que pone `render_promo.py`):
    PROMO_FORMATO, PROMO_CALIDAD.
    """
    nombre = nombre or os.environ.get("PROMO_FORMATO", "vertical")
    if nombre not in PROPORCIONES:
        raise ValueError(f"formato desconocido: {nombre}")
    calidad = calidad or os.environ.get("PROMO_CALIDAD", "qh")
    corto_px = int(corto_px or os.environ.get("PROMO_CORTO")
                   or LADO_CORTO[calidad])
    fps = int(fps or os.environ.get("PROMO_FPS") or FPS[calidad])

    ancho, alto = PROPORCIONES[nombre]
    corto = corto_px - (corto_px % 2)
    largo = int(round(corto * max(ancho, alto) / min(ancho, alto)))
    largo -= largo % 2                            # libx264 exige pares
    px_ancho, px_alto = (corto, largo) if alto > ancho else (largo, corto)
    if alto == ancho:
        px_ancho = px_alto = corto

    # ORDEN OBLIGATORIO: al fijar frame_height, manim copia el valor a las
    # DOS dimensiones; frame_width tiene que ir despues o el mundo se queda
    # en 16:9 y el contenido sale encajonado en una isla con bandas negras.
    config.pixel_width = px_ancho
    config.pixel_height = px_alto
    config.frame_height = alto
    config.frame_width = ancho
    config.frame_rate = fps

    if abs(config.frame_width - ancho) > 1e-6:
        raise RuntimeError("el mundo no quedo en el formato pedido: "
                           f"{config.frame_width} != {ancho}")
    return Formato(nombre, ancho, alto, px_ancho, px_alto, fps)


def marca_promo(fmt, opacidad=0.38):
    """La marca de agua, colocada donde la app NO la tapa.

    En vertical la esquina inferior derecha es justo la columna de botones
    de Instagram: la marca sube al centro del borde superior, dentro de la
    zona util. En horizontal se queda donde siempre.
    """
    marca = code_brand.marca_agua()
    marca.set_opacity(opacidad)
    if fmt.es_vertical:
        marca.move_to(UP * (fmt.tope - marca.height / 2 - 0.12))
    else:
        marca.to_corner(DR, buff=0.28)
    marca.set_z_index(1000)
    return marca


def guias(fmt):
    """Guias de validacion (solo con --guias): el rectangulo de lo que la
    app NO tapa y el centro util. No van en el render final."""
    util = Rectangle(width=fmt.ancho - fmt.margen["izq"] - fmt.margen["der"],
                     height=fmt.alto_util, stroke_width=2,
                     stroke_color=CODE_ACCENT, stroke_opacity=0.55)
    util.move_to(fmt.centro_util
                 + RIGHT * (fmt.margen["izq"] - fmt.margen["der"]) / 2)
    borde = Rectangle(width=fmt.ancho, height=fmt.alto, stroke_width=2,
                      stroke_color=CODE_MUTED, stroke_opacity=0.4)
    etiqueta = etiqueta_hud(f"{fmt.nombre} {fmt.px_ancho}x{fmt.px_alto}",
                            font_size=18, color=CODE_ACCENT)
    etiqueta.next_to(util, DOWN, buff=0.14)
    centro = VGroup(Dot(fmt.centro_util, radius=0.05, color=CODE_ACCENT))
    g = VGroup(DashedVMobject(util, num_dashes=48), borde, etiqueta, centro)
    g.set_z_index(2000)
    return g


def fondo_seguro(fmt):
    """Rectangulo opaco del color de marca que cubre TODO el lienzo.

    Manim pinta el fondo de la camara, pero un promo se exporta a apps que
    a veces re-encodean con margenes: un fondo explicito garantiza que no
    aparezca ni una linea negra en los bordes.
    """
    r = Rectangle(width=fmt.ancho + 0.4, height=fmt.alto + 0.4,
                  stroke_width=0, fill_color=code_brand.CODE_BG,
                  fill_opacity=1.0)
    r.set_z_index(-1000)
    return r


__all__ = ["Formato", "formato", "marca_promo", "guias", "fondo_seguro",
           "ALTURAS", "FPS", "SEGURA", "PROPORCIONES"]

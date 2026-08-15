# =====================================================================
# CO.DE Academy - "Criptografia: el arte de guardar secretos"
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

import cripto as _cripto  # noqa: E402  (tras definir la sombra)
from cripto import (ALFABETO, A_DH, B_DH, DESPLAZAMIENTO,  # noqa: E402
                    DIGITOS_RSA_2048, E_RSA, G_DH, MENSAJE_CESAR,
                    MENSAJE_HASH, MENSAJE_HASH_2, MENSAJE_OTP,
                    MENSAJE_OTP_2, M_RSA, N_BITS_OTP, P_DH, P_RSA, Q_RSA,
                    SEMILLA_OTP, TEXTO_ES, alterar_bit, bits_a_texto,
                    bits_distintos, caja_numero, candado, cesar,
                    curva_divisiones, desplazamiento_estimado,
                    diffie_hellman, divisiones_estimadas, exponente_divisiones,
                    divisiones_hasta_factor, esquema_dh, firmar, flujo,
                    frecuencias, grafo_llaves, hash_reducido,
                    histograma_frecuencias, llave_otp, llave_que_da,
                    llaves_por_pares, normalizar, potencia_mod,
                    rejilla_hash, rsa_cifrar, rsa_descifrar, rsa_juguete,
                    rueda_cesar, sha256_bits, sha256_hex, texto_a_bits,
                    tira_bits, tira_letras, verificar, xor_bits)

_cripto.Text = Text

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
# Regla: lo CLARO (el mensaje, el secreto, lo privado) es ambar; lo
# CIFRADO y lo publico (lo que viaja por el canal) cian; las LLAVES y lo
# que verifica bien verde; Eva, la fuerza bruta y lo que falla rojo; el
# HASH, la firma y la integridad violeta.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_ACENTO = CODE_ACCENT
C_ACENTO_2 = CODE_ACCENT_2
C_CLARO = "#f59e0b"          # ambar: mensaje en claro, secreto, privado
C_CIFRADO = "#22d3ee"        # cian: cifrado, publico, el canal
C_LLAVE = "#34d399"          # verde: llaves, verificacion correcta
C_ATAQUE = "#f43f5e"         # rojo: Eva, fuerza bruta, alteracion, fallo
C_HUELLA = "#a78bfa"         # violeta: hash, firma, integridad
C_EJE = "#31414f"            # gris azulado de mobiliario

MARGEN_PIE = 0.68

# --- Numeros del curso ------------------------------------------------
# Todo valor que se rotule sale de aqui o de la libreria (calculado o
# medido sobre los datos), nunca escrito a mano en el clip.
N_LLAVES_CESAR = len(ALFABETO) - 1                      # 25 utiles
CIFRADO_CESAR = cesar(MENSAJE_CESAR, DESPLAZAMIENTO)    # "QRV YHPRV ..."
FREC_ES = frecuencias(TEXTO_ES)                         # medidas
CIFRADO_ES = cesar(TEXTO_ES, DESPLAZAMIENTO)
FREC_CIFRADO = frecuencias(CIFRADO_ES)
K_ESTIMADO = desplazamiento_estimado(CIFRADO_ES)        # 3 (chi-cuadrado)
LETRA_TOP = max(FREC_ES, key=FREC_ES.get)               # "E"
BITS_OTP = texto_a_bits(MENSAJE_OTP)                    # 24 bits de "MAR"
LLAVE_OTP = llave_otp(N_BITS_OTP, SEMILLA_OTP)
CIFRADO_OTP = xor_bits(BITS_OTP, LLAVE_OTP)
LLAVE_OTP_2 = llave_que_da(CIFRADO_OTP, texto_a_bits(MENSAJE_OTP_2))  # da "SOL"
N_LLAVES_OTP = 2 ** N_BITS_OTP                          # 16 777 216
LLAVES_10, LLAVES_100, LLAVES_1000 = (llaves_por_pares(10),
                                      llaves_por_pares(100),
                                      llaves_por_pares(1000))  # 45/4950/499500
DH = diffie_hellman(P_DH, G_DH, A_DH, B_DH)             # A=8, B=19, s=2
RSA = rsa_juguete(P_RSA, Q_RSA, E_RSA)                  # n=3233, phi=3120, d=2753
N_RSA, D_RSA = RSA["n"], RSA["d"]
C_RSA = rsa_cifrar(M_RSA, E_RSA, N_RSA)                 # 2790
M_RSA_VUELTA = rsa_descifrar(C_RSA, D_RSA, N_RSA)       # 65
DIVISIONES_3233 = divisiones_hasta_factor(N_RSA)        # 16 primos probados (medido)
# 10^(617/2) no cabe en un float (divisiones_estimadas da inf): se rotula
# el exponente, 308 (MathTex 10^{308}), nunca el numero en crudo.
EXP_2048 = exponente_divisiones(DIGITOS_RSA_2048)       # 308.5
BITS_HASH = sha256_bits(MENSAJE_HASH)
BITS_HASH_2 = sha256_bits(MENSAJE_HASH_2)
N_BITS_CAMBIAN = bits_distintos(BITS_HASH, BITS_HASH_2)  # ~128 (medido)
H_FIRMA = hash_reducido(MENSAJE_HASH, N_RSA)            # huella mod n (juguete)
S_FIRMA = firmar(H_FIRMA, D_RSA, N_RSA)
FIRMA_OK = verificar(S_FIRMA, E_RSA, N_RSA, H_FIRMA)    # True
MENSAJE_ALTERADO = alterar_bit(MENSAJE_HASH, 0)
H_ALTERADA = hash_reducido(MENSAJE_ALTERADO, N_RSA)
FIRMA_ALTERADA_OK = verificar(S_FIRMA, E_RSA, N_RSA, H_ALTERADA)  # False


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
    """Cifra medida (Space Mono, ASCII puro) SIN posicion: el clip la
    coloca."""
    t = Text(texto, font=FUENTE_HUD, font_size=font_size,
             color=C_CIFRADO if color is None else color)
    return t


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())

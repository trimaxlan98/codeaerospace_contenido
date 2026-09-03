# =====================================================================
# CO.DE Academy - lienzo.py
# El estilo LIENZO: una superficie lisa azul marino con UNA cosa y UN dato.
#
# Es un lenguaje visual distinto al de los tres verticales anteriores (26,
# 28, 29), que usan la estetica de consola de vuelo de la marca: fondo casi
# negro, escuadras HUD en las esquinas y telemetria por todas partes. Aqui
# se va al reves y la regla es "menos es mas":
#
#   1. FONDO LISO. Azul marino plano, sin degradado ni textura. Cuando no
#      hay nada en pantalla, el fotograma es ese color y nada mas.
#   2. CUATRO CARRILES. numero (arriba izq), escena (centro-alto), dato
#      (cifra + etiqueta, abajo) y marca (pie). Cada carril admite UN solo
#      ocupante: `poner()` apaga primero lo que hubiera. Nada se encima
#      porque no hay donde encimarlo.
#   3. CUATRO COLORES. Fondo, tinta, apagado y un acento ambar. El cian es
#      el quinto y solo aparece cuando hay que distinguir DOS señales a la
#      vez.
#   4. ESCALA CERRADA. 128 / 46 / 30 / 22 / 18. Si algo no cabe se acorta
#      el texto; no hay tamaños intermedios.
#   5. LA MARCA NO INVADE. Wordmark en minusculas en el pie, opacidad 0.30,
#      y el numero de modulo arriba a la izquierda, apagado. Nada mas.
#
# Provenencia de las cifras (honestidad de la casa, resuelta sin gastar un
# color): la CIFRA siempre es tinta. La ETIQUETA de debajo es AMBAR si el
# numero lo calcula la libreria durante el render, y APAGADA si viene de la
# hoja de datos del fabricante.
#
# Tipografia: los numeros y las etiquetas van en Space Mono. No es capricho
# — Rajdhani tiene dos defectos medidos (parte palabras a 16-17 px y las
# JUNTA por debajo de 22) y ademas no es monoespaciada, asi que un contador
# baila al cambiar de digito. Space Mono no tiene ninguno de los dos
# problemas. Rajdhani se reserva para el display grande de intro y cierre,
# siempre por encima de 40 px.
# =====================================================================
import os

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Create, Dot, FadeIn, FadeOut,
                   Line, Rectangle, Text, UpdateFromAlphaFunc, VGroup,
                   config, linear)

import code_brand
import promo

# --- Paleta -----------------------------------------------------------
AZUL = "#0B1B33"        # el fondo: azul marino, plano, el 100 % del frame
TINTA = "#EAF1F8"       # el texto principal y la cifra
APAGADO = "#7C8FA6"     # etiquetas, mobiliario, lo que no es protagonista
AMBAR = "#F5A31B"       # EL acento. Uno solo.
CIAN = "#5AC8D8"        # el quinto color: solo para distinguir dos señales
LINEA = "#1B3253"       # rejillas y ejes: azul un paso por encima del fondo

# --- Escala tipografica (cerrada a proposito) -------------------------
CIFRA = 128             # el dato grande
DISPLAY = 46            # titulo de intro/cierre (Rajdhani, nunca menos)
UNIDAD = 30             # la unidad debajo de la cifra
ROTULO = 22             # etiquetas dentro del dibujo
MICRO = 18              # el minimo absoluto: una palabra suelta, o la marca

FUENTE_NUM = code_brand.FUENTE_HUD        # Space Mono
FUENTE_DISPLAY = code_brand.FUENTE_DISPLAY  # Rajdhani

# --- El lienzo --------------------------------------------------------
FMT = None              # lo rellena formato()

# Renglones de la composicion (unidades de mundo, 9:16 con lado 8.0).
Y_TECHO = Y_SUELO = Y_NUMERO = Y_MARCA = Y_CIFRA = 0.0
BANDA = (0.0, 0.0)      # (abajo, arriba) de la franja donde vive el dibujo
ANCHO_SEGURO = 0.0
X_IZQ = 0.0


def formato(nombre=None, calidad=None, **kw):
    """Configura el lienzo 9:16 y calcula los renglones. Se llama UNA vez,
    a nivel de modulo del style_block: manim importa el archivo entero
    antes de instanciar la escena, asi que aqui todavia se puede cambiar
    el mundo."""
    global FMT, Y_TECHO, Y_SUELO, Y_NUMERO, Y_MARCA, Y_CIFRA, BANDA
    global ANCHO_SEGURO, X_IZQ

    FMT = promo.formato(nombre or "vertical", calidad, **kw)
    config.background_color = AZUL

    Y_TECHO = FMT.tope                      #  5.69 borde util de arriba
    Y_SUELO = FMT.suelo                     # -4.27 borde util de abajo
    Y_NUMERO = Y_TECHO - 0.32               #  el "01" de modulo
    Y_MARCA = Y_SUELO + 0.30                #  el wordmark, sobre el suelo
    Y_CIFRA = -2.30                         #  centro de la cifra grande
    # La franja del dibujo: por debajo del numero y por encima de la cifra.
    # El 1.55 de holgura sobre la cifra no es de adorno: con 1.35 un dibujo
    # de borde recto apoyado en el suelo de la franja quedaba a 0.70 de la
    # cifra y las dos cosas se leian pegadas.
    BANDA = (Y_CIFRA + 1.55, Y_TECHO - 1.05)

    # Un objeto centrado no puede ser mas ancho que el doble del margen mas
    # estrecho: la columna de botones de la app se come 14 % por la derecha.
    ANCHO_SEGURO = 2.0 * min(FMT.ancho / 2 - FMT.margen["izq"],
                             FMT.ancho / 2 - FMT.margen["der"])   # 5.76
    X_IZQ = -FMT.ancho / 2 + FMT.margen["izq"]                    # -3.60
    return FMT


def alto_banda():
    return BANDA[1] - BANDA[0]


def centro_banda():
    return np.array([0.0, (BANDA[0] + BANDA[1]) / 2, 0.0])


# --- Guardianes -------------------------------------------------------
class FueraDelLienzo(ValueError):
    """El render se aborta antes que publicar algo tapado o ilegible."""


def cabe(mob, que="pieza"):
    """Aborta el render si la pieza se sale de lo que la app NO tapa.

    En vertical la columna derecha se la comen los botones de Instagram, y
    un rotulo de 6.7 unidades centrado se mete ahi sin que se note en el
    frame de validacion. Mejor que el render falle con el ancho medido."""
    if mob.width > ANCHO_SEGURO + 1e-6:
        raise FueraDelLienzo(
            f"{que} mide {mob.width:.2f} de ancho y la zona segura son "
            f"{ANCHO_SEGURO:.2f}: acorta el texto o simplifica el dibujo")
    return mob


def _minimo_legible(mob):
    """El alto del ROTULO mas pequeño que quedaria en pantalla.

    Un `scale()` sobre el grupo entero encoge tambien las etiquetas, y una
    etiqueta de 22 px reducida a la mitad es ilegible en un telefono.

    Dos errores en este guardian, los dos medidos, y merece la pena
    dejarlos escritos porque son la misma clase de error:

    1. La primera version filtraba con `t.has_points()` y el guardian
       estuvo MUERTO medio curso: un `Text` de manim no tiene puntos
       propios (los glifos son sus hijos), asi que ninguno pasaba el
       filtro y `ALTO_MINIMO` no se comprobaba jamas.
    2. La segunda version media Text por Text, y como `espaciado()`
       construye UN Text por caracter, lo que media era la altura de cada
       GLIFO. El guion de "WI-FI" mide 0.018 a cuerpo completo y el
       guardian abortaba el molde del curso. Una `i` o un punto habrian
       hecho lo mismo.

    Lo que hay que medir es la altura de la LINEA de texto, no la del
    glifo mas bajo. Por eso `espaciado()` devuelve un `Rotulo` (cuya
    altura es la del glifo mas alto, o sea la de la caja tipografica) y
    aqui se miden los `Rotulo`, saltandose los Text que viven dentro de
    uno."""
    altos = []
    for m in mob.get_family():
        if isinstance(m, Rotulo):
            if m.height > 1e-6:
                altos.append(m.height)
        elif (isinstance(m, Text) and not getattr(m, "_en_rotulo", False)
                and m.height > 1e-6 and m.family_members_with_points()):
            altos.append(m.height)
    return min(altos) if altos else None


# Alto minimo de un glifo en pantalla, en unidades de mundo. 0.18 unidades
# a 135 px/unidad son 24 px de alto real en el 1080x1920 final.
ALTO_MINIMO = 0.155

# Fraccion minima de la franja que tiene que ocupar un dibujo.
#
# El aviso llevaba escrito en LIENZO.md desde el curso 31 ("un dibujo que
# ocupa menos del 60 % del alto de la franja se lee como un error, no como
# minimalismo") y en el 32 hubo que corregirlo en TODAS las piezas que
# escribieron los subagentes: dibujos de 1.5 unidades en una franja de
# 5.59, con el fotograma medio vacio. Un consejo que hay que recordar no
# sobrevive a dieciocho piezas y a trece autores distintos, asi que pasa a
# ser guardian. El umbral es 0.45 y no 0.60 para dejar sitio a los dibujos
# que de verdad son bajos (una sola fila de tallos, un panel unico).
FRACCION_MINIMA = 0.45


def encajar(mob, margen=0.0, que="escena", anclaje="abajo", bajo=False):
    """Coloca el dibujo en su franja, escalandolo solo si hace falta.

    No escala hacia arriba: una pieza pequeña se queda pequeña (el vacio es
    parte del estilo). Si para caber hubiera que encoger tanto que un
    rotulo baje de ALTO_MINIMO, aborta: eso no se arregla escalando, se
    arregla quitando cosas del dibujo."""
    disp_ancho = min(ANCHO_SEGURO, FMT.ancho - 1.8) - 2 * margen
    disp_alto = alto_banda() - 2 * margen
    if mob.width > disp_ancho or mob.height > disp_alto:
        k = min(disp_ancho / max(mob.width, 1e-9),
                disp_alto / max(mob.height, 1e-9))
        mob.scale(k)
    mob.move_to(centro_banda())
    if anclaje == "abajo":
        mob.shift(UP * (BANDA[0] + margen - mob.get_bottom()[1]))
    elif anclaje == "arriba":
        mob.shift(UP * (BANDA[1] - margen - mob.get_top()[1]))
    elif anclaje != "centro":
        raise FueraDelLienzo(f"anclaje desconocido: {anclaje}")
    minimo = _minimo_legible(mob)
    if minimo is not None and minimo < ALTO_MINIMO:
        raise FueraDelLienzo(
            f"{que}: tras encajarla, el rotulo mas pequeño mide "
            f"{minimo:.3f} de alto y el minimo legible es {ALTO_MINIMO}: "
            f"quita elementos del dibujo en vez de encogerlo")
    ocupa = mob.height / max(alto_banda(), 1e-9)
    if not bajo and ocupa < FRACCION_MINIMA:
        raise FueraDelLienzo(
            f"{que} mide {mob.height:.2f} de alto y ocupa el "
            f"{ocupa * 100:.0f} % de la franja ({alto_banda():.2f}): por "
            f"debajo del {FRACCION_MINIMA * 100:.0f} % el fotograma se lee "
            f"como un error de maquetacion. Sube el `alto` del dibujo a "
            f"2.4-3.0, o pasa bajo=True si de verdad tiene que ser bajo")
    return cabe(mob, que)


# --- Piezas de texto --------------------------------------------------
def _texto(cadena, font, font_size, color, weight="MEDIUM"):
    t = Text(cadena, font=font, font_size=font_size, color=color,
             weight=weight)
    t.submobjects = [s for s in t.submobjects if s.has_points()]
    return t


class Rotulo(VGroup):
    """Una linea de texto en versalitas espaciadas.

    Existe como CLASE y no como VGroup pelado para que el guardian de
    legibilidad pueda medir la linea entera en vez de sus glifos sueltos
    (ver `_minimo_legible`)."""


def espaciado(cadena, font_size=ROTULO, color=APAGADO, tracking=0.34,
              font=None, mayusculas=True):
    """Etiqueta en versalitas espaciadas, construida CARACTER A CARACTER.

    Dos motivos, los dos medidos: (1) Space Mono es monoespaciada, asi que
    repartir los glifos a paso fijo es exactamente lo que la fuente ya
    hace, y añadir tracking es lo unico que le falta al estilo; (2)
    construir cada letra por separado esquiva de raiz el defecto de las
    fuentes de la casa que junta palabras a cuerpos pequeños, porque cada
    glifo lleva su posicion puesta a mano."""
    font = font or FUENTE_NUM
    if mayusculas:
        cadena = cadena.upper()
    # Cada glifo se construye JUNTO A UNA "H" y se alinea por la linea de
    # base de esa H. Sin esto, `move_to` centra cada caracter por su propia
    # caja y la puntuacion se va a media altura: "0.5" salia "0·5" (leido
    # como dos numeros), la coma de una enumeracion flotaba, y un guion
    # quedaba mas alto de lo que le toca. Con mayusculas solas no se nota
    # porque todas miden igual — por eso el defecto sobrevivio un curso
    # entero.
    referencia = _texto("H", font, font_size, color)
    base = referencia.get_bottom()[1]
    paso = None
    grupo = Rotulo()
    x = 0.0
    for ch in cadena:
        if ch == " ":
            if paso is None:
                paso = _texto("M", font, font_size, color).width
            x += paso * (1.0 + tracking)
            continue
        par = _texto("H" + ch, font, font_size, color)
        if len(par) < 2:            # el caracter no pinta nada
            continue
        h, g = par[0], par[1]
        alto_sobre_base = g.get_center()[1] - h.get_bottom()[1]
        if paso is None:
            paso = g.width
        g.move_to([x, base + alto_sobre_base, 0])
        g._en_rotulo = True
        grupo.add(g)
        x += paso * (1.0 + tracking)
    if len(grupo) == 0:
        return grupo
    grupo.move_to([0, 0, 0])
    return grupo


def numero_modulo(n):
    """El "01" de arriba a la izquierda. Un token, sin espacios."""
    t = espaciado(f"{int(n):02d}", font_size=UNIDAD, color=APAGADO,
                  tracking=0.20)
    t.set_opacity(0.55)
    t.move_to([X_IZQ + t.width / 2, Y_NUMERO - t.height / 2, 0])
    t.set_z_index(900)
    return t


def marca_agua():
    """`co.de academy` en el pie, centrado, discreto.

    Va en DOS Text, no en uno: Rajdhani junta las palabras por debajo de
    22 px y este wordmark va a 18, asi que un unico `Text("co.de academy")`
    saldria "co.deacademy". Cada token va suelto y con su sitio puesto.

    Y se alinean por ARRIBA, no por abajo: "academy" lleva una 'y' con
    descendente y "co.de" no, asi que igualar los bordes inferiores sube la
    segunda palabra media equis (se vio en el primer frame). Las dos
    palabras tienen la 'd' ascendente, de modo que igualar los bordes
    SUPERIORES si deja las dos sobre la misma linea de base."""
    code_brand.registrar_fuentes()
    codes = _texto("co.de", FUENTE_DISPLAY, MICRO, TINTA, weight="SEMIBOLD")
    # El punto de la marca es lo unico ambar del pie. Los glifos vacios ya
    # estan filtrados, asi que el indice 2 es el punto: c-o-.-d-e.
    codes[2].set_color(AMBAR)
    aca = _texto("academy", FUENTE_DISPLAY, MICRO, TINTA, weight="SEMIBOLD")
    marca = VGroup(codes, aca).arrange(RIGHT, buff=0.14, aligned_edge=UP)
    marca.set_opacity(0.32)
    marca.move_to([0, Y_MARCA, 0])
    marca.set_z_index(900)
    return marca


# Los peldaños de la cifra y de la etiqueta. Medidos en el contenedor a
# 1080x1920 (Space Mono, ancho seguro 5.76 unidades):
#
#   cuerpo  ancho/caracter   caracteres que caben
#     128       1.061                 5
#     112       0.919                 6
#      96       0.776                 7
#      80       0.673                 8
#      72       0.582                 9
#      64       0.531                10
#      56       0.479                12
#
# La escala sigue siendo CERRADA: no hay cuerpos intermedios. Lo que hace
# `cifra()` es bajar de peldaño hasta que la cadena entra, en vez de
# escalar el mobject (escalar rompe el paso monoespaciado entre estados de
# un contador, y deja cuerpos que no estan en la escala).
ESCALA_CIFRA = (128, 112, 96, 80, 72, 64, 56)
ESCALA_ETIQUETA = (30, 26, 22, 18)


def _mayor_que_entra(cadena, escala, constructor, ancho=None, que="texto"):
    ancho = ancho if ancho is not None else ANCHO_SEGURO
    for fs in escala:
        pieza = constructor(cadena, fs)
        if pieza.width <= ancho + 1e-6:
            return pieza, fs
    raise FueraDelLienzo(
        f"{que} '{cadena}' no entra ni al cuerpo minimo {escala[-1]} "
        f"({pieza.width:.2f} > {ancho:.2f}): acorta la cadena")


# Hueco del separador de miles, en anchos de caracter. El espacio de una
# monoespaciada mide un caracter entero y abre un abismo: "7 200" se leia
# como dos numeros distintos. 0.42 separa los grupos sin romper la cifra.
HUECO_MILES = 0.34


def _cifra_en(cadena, font_size, color):
    """Un numero, con sus grupos de miles separados a mano.

    Los grupos van en Text SUELTOS y colocados por su ancho, no dentro de
    un unico Text con espacios: asi el hueco es el que se decide aqui y no
    el paso completo de la monoespaciada."""
    grupos = str(cadena).split(" ")
    piezas = [_texto(g, FUENTE_NUM, font_size, color, weight="BOLD")
              for g in grupos]
    if len(piezas) == 1:
        return piezas[0]
    paso = piezas[0].width / max(len(grupos[0]), 1)
    fila = VGroup(*piezas).arrange(RIGHT, buff=paso * HUECO_MILES,
                                   aligned_edge=DOWN)
    return fila


def cifra(valor, color=TINTA, font_size=None):
    """El dato grande. Space Mono: los digitos ocupan lo mismo, asi que un
    contador no baila al pasar de 1 a 8.

    Sin `font_size` baja por la escala hasta el mayor cuerpo en el que la
    cadena entra en la zona segura."""
    cadena = str(valor)
    if font_size is not None:
        return cabe(_cifra_en(cadena, font_size, color), f"cifra '{cadena}'")
    pieza, _ = _mayor_que_entra(
        cadena, ESCALA_CIFRA,
        lambda c, fs: _cifra_en(c, fs, color), que="cifra")
    return pieza


def cuerpo_cifra(valores):
    """El cuerpo comun para una serie de valores (contadores y relevos).

    Todos los estados de un contador tienen que compartir cuerpo, o el
    numero cambia de tamaño al pasar de 999 a 1000. Se elige por el estado
    mas ancho."""
    mas_larga = max((str(v) for v in valores), key=len)
    _, fs = _mayor_que_entra(
        mas_larga, ESCALA_CIFRA,
        lambda c, f: _cifra_en(c, f, TINTA), que="contador")
    return fs


def etiqueta(texto, medido=True, font_size=None):
    """La linea de debajo de la cifra. AMBAR si el numero lo calcula la
    libreria en el render; APAGADA si viene de la hoja de datos.

    La linea que separa los dos colores es "¿lo calculo la libreria en
    este render?", no "¿es de Espressif?". Asi que va en APAGADO todo lo
    DADO: la hoja de datos, la literatura y tambien los PARAMETROS de una
    simulacion (el periodo de 10 ms de un bucle, la constante dielectrica
    del FR4). Y en AMBAR solo lo que sale de medir o de calcular aqui. Un
    parametro elegido no es una medida por mucho que este en el codigo.

    Va en VERSALITAS, asi que las unidades se escriben con todas sus
    letras: "megahercios", no "MHz". Un simbolo de unidad en mayusculas
    deja de ser el simbolo — "MHZ", "MS" y "UA" no significan nada, y en
    el caso de "mV"/"MV" significan cosas distintas. Ademas la palabra
    entera queda mejor debajo de un numero grande, que es de lo que va
    este estilo."""
    color = AMBAR if medido else APAGADO
    if font_size is not None:
        return cabe(espaciado(texto, font_size=font_size, color=color,
                              tracking=0.30), f"etiqueta '{texto}'")
    pieza, _ = _mayor_que_entra(
        texto, ESCALA_ETIQUETA,
        lambda c, fs: espaciado(c, font_size=fs, color=color, tracking=0.30),
        que="etiqueta")
    return pieza


def dato(valor, texto, medido=True, font_size=None, color=TINTA):
    """La pareja completa: cifra grande + etiqueta, colocada en su carril."""
    num = cifra(valor, color=color, font_size=font_size)
    eti = etiqueta(texto, medido=medido)
    grupo = VGroup(num, eti)
    num.move_to([0, Y_CIFRA, 0])
    eti.next_to(num, DOWN, buff=0.30)
    cabe(num, f"cifra '{valor}'")
    cabe(eti, f"etiqueta '{texto}'")
    tope_marca = Y_MARCA + 0.22
    if eti.get_bottom()[1] < tope_marca:
        raise FueraDelLienzo(
            f"el dato baja hasta {eti.get_bottom()[1]:.2f} y la marca "
            f"empieza en {tope_marca:.2f}: acorta la etiqueta o baja la "
            f"cifra de cuerpo")
    return grupo


def rotulo(texto, color=APAGADO, font_size=ROTULO):
    """Etiqueta que nombra una parte del dibujo. Va DENTRO de la escena, no
    en un carril propio: se mueve y se escala con ella."""
    return espaciado(texto, font_size=font_size, color=color, tracking=0.26)


def titulo_display(texto, color=TINTA, font_size=DISPLAY):
    """Solo para intro y cierre. Rajdhani, nunca por debajo de 40."""
    if font_size < 40:
        raise FueraDelLienzo(
            f"titulo_display a {font_size}: Rajdhani junta las palabras "
            f"por debajo de 22 y parte glifos a 16-17. Minimo 40.")
    code_brand.registrar_fuentes()
    t = _texto(texto, FUENTE_DISPLAY, font_size, color, weight="SEMIBOLD")
    return cabe(t, f"titulo '{texto}'")


# --- Mobiliario minimo ------------------------------------------------
def filete(ancho=1.2, color=AMBAR, grosor=3.0):
    """Un trazo corto. El unico adorno permitido."""
    return Line(LEFT * ancho / 2, RIGHT * ancho / 2,
                stroke_width=grosor, color=color)


def regla(y, ancho=None, color=LINEA, grosor=1.5):
    """Linea de base horizontal, del color del fondo un paso mas claro."""
    ancho = ancho or (ANCHO_SEGURO - 0.4)
    return Line([-ancho / 2, y, 0], [ancho / 2, y, 0],
                stroke_width=grosor, color=color)


def guias():
    """Dibuja la zona que la app NO tapa. Solo con PROMO_GUIAS=1."""
    caja = Rectangle(width=ANCHO_SEGURO, height=Y_TECHO - Y_SUELO,
                     stroke_color=AMBAR, stroke_width=1.2,
                     stroke_opacity=0.35)
    caja.move_to([0, (Y_TECHO + Y_SUELO) / 2, 0])
    banda = Rectangle(width=ANCHO_SEGURO, height=alto_banda(),
                      stroke_color=CIAN, stroke_width=1.0,
                      stroke_opacity=0.30)
    banda.move_to(centro_banda())
    return VGroup(caja, banda, Dot([0, Y_CIFRA, 0], radius=0.04,
                                   color=CIAN))


# --- La portada -------------------------------------------------------
# El curso 32 se publica SIN VOZ, con musica encima. Eso deja la
# explicacion sin sitio: no hay narrador y el estilo prohibe la frase en
# pantalla. La solucion es concentrarla en una portada de tres segundos —
# el nombre de la pieza y QUE VUELVE FACIL— y que el resto del clip sea
# solo el dibujo y su cifra. Un sitio donde se explica, y ninguno mas.
PORTADA = 64            # el nombre, en Rajdhani (por encima del minimo 40)
MAX_PALABRAS_TESIS = 5


def portada(nombre, tesis=None):
    """El nombre de la pieza sobre un filete ambar, y su tesis debajo.

    Guardias: el nombre baja de cuerpo hasta caber (hay transformadas con
    nombres largos, KARHUNEN-LOEVE mide 12 caracteres) y la tesis no
    puede pasar de cinco palabras. Ese tope es el que impide que la
    portada se convierta en el subtitulo que este estilo no quiere: si no
    cabe en cinco palabras, el verbo visual de la pieza esta mal elegido
    y lo que hay que cambiar es el dibujo."""
    code_brand.registrar_fuentes()
    piezas = []
    titulo, _ = _mayor_que_entra(
        str(nombre).upper(), (PORTADA, 56, 50, 44, 40),
        lambda c, fs: _texto(c, FUENTE_DISPLAY, fs, TINTA, weight="SEMIBOLD"),
        ancho=ANCHO_SEGURO - 0.2, que="nombre de la portada")
    piezas.append(titulo)
    raya = filete(ancho=min(titulo.width * 0.55, ANCHO_SEGURO - 1.0))
    raya.next_to(titulo, DOWN, buff=0.34)
    piezas.append(raya)
    if tesis:
        if len(str(tesis).split()) > MAX_PALABRAS_TESIS:
            raise FueraDelLienzo(
                f"la tesis '{tesis}' tiene {len(str(tesis).split())} "
                f"palabras y el tope son {MAX_PALABRAS_TESIS}: no es un "
                f"subtitulo, es lo que la pieza vuelve facil")
        sub = etiqueta(str(tesis), medido=False)
        sub.next_to(raya, DOWN, buff=0.34)
        piezas.append(sub)
    grupo = VGroup(*piezas)
    grupo.move_to([0, (Y_TECHO + Y_SUELO) / 2, 0])
    return cabe(grupo, "portada")


# --- El panel partido -------------------------------------------------
def dos_dominios(arriba, abajo, rotulo_arriba=None, rotulo_abajo=None,
                 hueco=0.55, ancho=None):
    """Dos dibujos, uno sobre otro, con su nombre.

    Es la gramatica de media docena de piezas: aqui esta el problema y
    ahi esta resuelto. Los dos paneles se escalan al MISMO ancho para que
    la comparacion sea honrada (uno mas ancho que el otro sugiere que
    tiene mas de algo), y cada uno lleva su rotulo pegado.

    El separador no es una linea: es el hueco. Una raya entre los dos
    paneles añade tinta sin añadir informacion."""
    ancho = ancho or (ANCHO_SEGURO - 0.3)
    paneles = []
    for dibujo, texto in ((arriba, rotulo_arriba), (abajo, rotulo_abajo)):
        if dibujo.width > ancho:
            dibujo.scale(ancho / dibujo.width)
        if texto:
            rot = rotulo(texto)
            rot.next_to(dibujo, DOWN, buff=0.20)
            paneles.append(VGroup(dibujo, rot))
        else:
            paneles.append(VGroup(dibujo))
    return VGroup(*paneles).arrange(DOWN, buff=hueco)


# --- Los carriles -----------------------------------------------------
class _Igual:
    """Centinela: "este carril se queda como esta".

    Hace falta porque `None` ya significa algo distinto en `relevo()`:
    vaciar el carril. Sin el centinela no habria forma de decir "cambia el
    dibujo y deja la cifra donde estaba"."""

    def __repr__(self):
        return "IGUAL"


IGUAL = _Igual()


class Lienzo:
    """El estado de la pantalla. Un carril, un ocupante.

    No es azucar: es la garantia estructural de que nada se encima. Meter
    algo en un carril ocupado APAGA primero lo que habia, y no hay forma de
    poner dos cosas en el mismo sitio sin pasar por aqui."""

    CARRILES = ("numero", "escena", "dato", "marca")

    def __init__(self, escena, modulo=None):
        self.e = escena
        self.modulo = modulo
        self.ocupantes = {c: None for c in self.CARRILES}
        self._contadores = []

    # --- capa fija ----------------------------------------------------
    def montar(self, t=0.7):
        """Enciende numero de modulo y marca de agua. Toda pieza empieza en
        azul limpio y los trae con un fundido: asi la costura con la pieza
        anterior es exactamente cero."""
        piezas = [marca_agua()]
        if self.modulo is not None:
            piezas.insert(0, numero_modulo(self.modulo))
        for p, carril in zip(piezas, ("numero", "marca")[-len(piezas):]):
            self.ocupantes[carril] = p
        if os.environ.get("PROMO_GUIAS") == "1":
            self.e.add(guias())
        self.e.play(*[FadeIn(p, run_time=t) for p in piezas])

    # --- portada ------------------------------------------------------
    def portada(self, nombre, tesis=None, entra=0.7, quieto=1.5,
                sale=0.55):
        """Enseña el nombre de la pieza y lo apaga. No ocupa carril.

        Es un COMPAS, no un estado: aparece, se sostiene el tiempo que se
        tarda en leerlo sin prisa y se va, dejando el lienzo limpio para
        que empiece el dibujo. Sin voz, `quieto` es lo unico que garantiza
        que da tiempo a leerlo, asi que no baja de 1.2 s."""
        if quieto < 1.2:
            raise FueraDelLienzo(
                f"la portada se sostiene {quieto} s y el minimo es 1.2: sin "
                f"voz, nadie avisa de cuando hay que mirar")
        tarjeta = portada(nombre, tesis)
        self.e.play(FadeIn(tarjeta[0], run_time=entra))
        self.e.play(Create(tarjeta[1], run_time=0.45))
        if len(tarjeta) > 2:
            self.e.play(FadeIn(tarjeta[2], shift=UP * 0.12, run_time=0.5))
        self.e.wait(quieto)
        self.e.play(FadeOut(tarjeta, run_time=sale))
        return tarjeta

    # --- carriles -----------------------------------------------------
    def poner(self, carril, mob, t=0.6, salida=0.4, animacion=None):
        """Ocupa un carril. Si estaba ocupado, apaga primero al anterior."""
        if carril not in self.CARRILES:
            raise FueraDelLienzo(f"carril desconocido: {carril}")
        self.quitar(carril, t=salida)
        self.ocupantes[carril] = mob
        self.e.play(animacion if animacion is not None
                    else FadeIn(mob, run_time=t))
        return mob

    def quitar(self, carril, t=0.4):
        viejo = self.ocupantes.get(carril)
        if viejo is None:
            return
        self.ocupantes[carril] = None
        self.e.play(FadeOut(viejo, run_time=t))

    def dato(self, valor, texto, medido=True, t=0.6, salida=0.4, **kw):
        """Atajo: construye el dato y lo mete en su carril."""
        return self.poner("dato", dato(valor, texto, medido=medido, **kw),
                          t=t, salida=salida)

    def dato_animado(self, valores, texto, duracion, medido=True, t=0.6,
                     salida=0.4, ritmo=None, color=TINTA):
        """Una cifra que corre. Ocupa el carril del dato como cualquier otra.

        Los estados se cocinan ANTES y se intercambian con `become` dentro
        de un `UpdateFromAlphaFunc`: `always_redraw` con Text recrea el
        mobject en cada frame y parpadea. Todos comparten cuerpo (lo elige
        `cuerpo_cifra` por el estado mas ancho) para que el numero no
        cambie de tamaño al pasar de 999 a 1000, y la etiqueta se ancla a
        una altura FIJA, no al numero: si colgara de el, subiria y bajaria
        con cada digito que aparece."""
        valores = [str(v) for v in valores]
        fs = cuerpo_cifra(valores)
        estados = [cifra(v, color=color, font_size=fs) for v in valores]
        alto = max(e.height for e in estados)
        for est in estados:
            est.move_to([0, Y_CIFRA, 0])
        eti = etiqueta(texto, medido=medido)
        eti.move_to([0, Y_CIFRA - alto / 2 - 0.30 - eti.height / 2, 0])
        tope_marca = Y_MARCA + 0.22
        if eti.get_bottom()[1] < tope_marca:
            raise FueraDelLienzo(
                f"el dato animado baja hasta {eti.get_bottom()[1]:.2f} y la "
                f"marca empieza en {tope_marca:.2f}: acorta la etiqueta")
        num = estados[0].copy()
        grupo = VGroup(num, eti)
        self.quitar("dato", t=salida)
        self.ocupantes["dato"] = grupo
        self.e.play(FadeIn(grupo, run_time=t))

        def _paso(mob, alpha):
            i = min(int(alpha * len(estados)), len(estados) - 1)
            mob.become(estados[i])

        self.e.play(UpdateFromAlphaFunc(num, _paso), run_time=duracion,
                    rate_func=ritmo or linear)
        return grupo

    def contador_vivo(self, texto, valor_en, t_final, paso=0.25,
                      medido=True, t=0.6, salida=0.4, color=TINTA):
        """Una cifra que sigue corriendo mientras pasan OTRAS animaciones.

        `dato_animado` gasta un `play` entero, asi que el dibujo no puede
        cambiar mientras el numero sube. Este va con un updater, que
        sobrevive a los `play` siguientes.

        Y no cuenta su propio `dt` acumulado: lee el reloj de la escena
        (`renderer.time`) y llama a `valor_en(t)`. Asi el numero que se ve
        es exactamente el que corresponde al segundo de video en el que se
        ve — si un `play` cambia de duracion al ajustar el ritmo, la cifra
        se corrige sola en vez de mentir."""
        tiempos = np.arange(0.0, float(t_final) + float(paso), float(paso))
        valores = [str(valor_en(float(ti))) for ti in tiempos]
        fs = cuerpo_cifra(valores)
        estados = [cifra(v, color=color, font_size=fs) for v in valores]
        alto = max(e.height for e in estados)
        for est in estados:
            est.move_to([0, Y_CIFRA, 0])
        eti = etiqueta(texto, medido=medido)
        eti.move_to([0, Y_CIFRA - alto / 2 - 0.30 - eti.height / 2, 0])
        num = estados[0].copy()
        grupo = VGroup(num, eti)
        self.quitar("dato", t=salida)
        self.ocupantes["dato"] = grupo
        # El FadeIn va ANTES de colgar el updater: si no, el updater
        # repinta el numero a opacidad 1 en cada frame y la cifra aparece
        # de golpe mientras la etiqueta si se funde.
        self.e.play(FadeIn(grupo, run_time=t))

        def _tic(mob, dt):
            i = int(round(self.e.renderer.time / float(paso)))
            mob.become(estados[min(max(i, 0), len(estados) - 1)])

        num.add_updater(_tic)
        self._contadores.append(num)
        return grupo

    def parar_contadores(self):
        """Congela las cifras vivas. Se llama sola antes del fundido: un
        updater que sigue repintando durante el FadeOut le devuelve la
        opacidad al numero y la pieza no termina en azul limpio."""
        for num in self._contadores:
            num.clear_updaters()
        self._contadores = []

    def escena(self, mob, t=0.8, salida=0.45, animacion=None, margen=0.0,
               anclaje="abajo", bajo=False):
        """Atajo: encaja el dibujo en su franja y lo mete en su carril.

        Por defecto lo apoya en el SUELO de la franja, junto a la cifra.
        Centrarlo parecia lo natural y esta medido que no lo es: un dibujo
        mas bajo que la franja se queda a dos unidades de su numero, la
        composicion se parte en dos mitades sin relacion y el hueco se lee
        como un error de maquetacion, no como aire. Apoyado abajo, dibujo y
        dato bajan juntos y el vacio se acumula arriba, que es donde vive
        el numero de pieza y donde el vacio SI es aire.

        `anclaje="centro"` sigue disponible para una pieza que de verdad
        quiera flotar."""
        encajar(mob, margen=margen, anclaje=anclaje, bajo=bajo)
        return self.poner("escena", mob, t=t, salida=salida,
                          animacion=animacion)

    def relevo(self, escena=IGUAL, dato=IGUAL, t=0.8, salida=0.45,
               animacion=None, anclaje="abajo", bajo=False):
        """Cambia dibujo y cifra A LA VEZ, en un solo movimiento.

        Los tres primeros clips del curso tropezaron con lo mismo: relevar
        primero el dibujo y despues la cifra deja uno o dos segundos con el
        dibujo nuevo y el numero viejo debajo. Nadie lo nota en el frame de
        validacion y sin embargo es una mentira — la cifra esta hablando de
        algo que ya no esta en pantalla.

        Un argumento que no se pasa deja su carril COMO ESTA; pasar `None`
        lo VACIA (un hueco sin cifra es un estado valido del lienzo; una
        cifra que no corresponde, no). `dato` admite el mobject ya hecho o
        la tupla de argumentos de `dato()`."""
        if dato is not IGUAL and isinstance(dato, (tuple, list)):
            dato = globals()["dato"](*dato)
        cambios = [("escena", escena), ("dato", dato)]
        salidas, entradas = [], []
        for carril, pieza in cambios:
            if pieza is IGUAL:
                continue
            viejo = self.ocupantes.get(carril)
            if viejo is not None:
                salidas.append(FadeOut(viejo, run_time=salida))
            self.ocupantes[carril] = None
            if pieza is None:
                continue
            if carril == "escena":
                encajar(pieza, anclaje=anclaje, bajo=bajo)
                entradas.append(animacion if animacion is not None
                                else FadeIn(pieza, run_time=t))
            else:
                entradas.append(FadeIn(pieza, run_time=t))
            self.ocupantes[carril] = pieza
        if salidas:
            self.e.play(*salidas)
        if entradas:
            self.e.play(*entradas)
        return escena, dato

    # --- cierre -------------------------------------------------------
    def fundido(self, t=0.9):
        """Deja el fotograma en azul limpio y NADA mas.

        Apaga TODO lo que hay en escena, incluida la capa fija: asi la
        pieza termina en el mismo color exacto con el que empieza la
        siguiente, y el montaje no parpadea en las costuras. (En el curso
        28 el fundido se llevaba el HUD y la marca por un `FadeOut` sobre
        `self.mobjects`, y la siguiente pieza los encendia de golpe.)"""
        self.parar_contadores()
        vivos = [m for m in self.e.mobjects if m.get_num_points() > 0
                 or len(m.family_members_with_points()) > 0]
        for c in self.CARRILES:
            self.ocupantes[c] = None
        if vivos:
            self.e.play(*[FadeOut(m, run_time=t) for m in vivos])
        else:
            self.e.wait(t)


# --- Contadores -------------------------------------------------------
def contador(valores, font_size=None, color=TINTA):
    """Pre-renderiza los estados de un numero que cambia.

    Nada de `always_redraw` con Text (recrea el mobject en cada frame y
    parpadea): se cocinan los valores una vez y se intercambian con
    `become` dentro de un `UpdateFromAlphaFunc`. Space Mono los deja
    perfectamente alineados porque todos los digitos miden igual."""
    font_size = font_size or cuerpo_cifra(valores)
    estados = [cifra(v, color=color, font_size=font_size) for v in valores]
    for est in estados:
        est.move_to([0, Y_CIFRA, 0])
    return estados


def miles(n, sep=" "):
    """7200000000 -> '7 200 000 000'. Con espacio fino, no con coma: el
    punto y la coma cambian de significado segun el pais."""
    return f"{int(n):,}".replace(",", sep)

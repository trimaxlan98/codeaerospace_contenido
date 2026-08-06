"""Agentes de IA animables: el lazo, las herramientas, ReAct y la autonomia.

Pensado para el curso "Agentes de IA: maquinas que operan el mundo". Todo es
determinista y puramente geometrico: no hay `random`, ni red, ni disco, ni
updaters residuales (las animaciones devuelven `Succession` de
`ShowPassingFlash` sobre COPIAS, nunca sobre los mobjects de la escena). Mismo
script -> mismo render, condicion necesaria para trabajar con
`--disable_caching`.

La regla de color del curso: el AGENTE es cian, el MUNDO violeta, la ACCION
ambar, lo PERMITIDO verde, lo PELIGROSO rojo. Las cajas (`burbuja`,
`tarjeta_json`, `catalogo_herramientas`) hablan el mismo lenguaje visual que
`bloques.bloque`: esquina redondeada de radio 0.10-0.12, stroke fino (1.6-2.5)
y relleno muy bajo (8-12 %) del propio color.

Piezas y para que sirve cada una:

    lazo_agente()            el ciclo percibir -> razonar -> actuar
    girar_lazo(lazo)         un pulso recorre el ciclo N vueltas
    burbuja(texto, tipo)     un mensaje: pensamiento / accion / observacion
    traza_react(pasos)       la columna de burbujas de una traza ReAct
    catalogo_herramientas()  el grid cerrado de herramientas disponibles
    tarjeta_json(lineas)     la llamada a herramienta, validada o rechazada
    escudo()                 el guardia que filtra lo que entra
    escala_autonomia(nivel)  L0..L5 con el marcador donde toque

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render): `PASOS_MAX`,
`HERRAMIENTAS_MAX` y `LINEAS_MAX` recortan en silencio, como hace fractales.py.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from agentes import lazo_agente, girar_lazo, traza_react, tarjeta_json

    lazo = lazo_agente()
    self.play(Create(lazo))
    self.play(girar_lazo(lazo, vueltas=2, run_time=2.2))
"""

import numpy as np

from manim import (Arc, Circle, DashedVMobject, DOWN, LEFT, Line, ORIGIN, PI,
                   RIGHT, RoundedRectangle, ShowPassingFlash, Succession, Text,
                   Triangle, UP, VGroup, VMobject, Wait)

from code_brand import (CODE_BG, CODE_INK, CODE_MUTED, FUENTE_HUD,
                        registrar_fuentes)

# Limites duros: se recortan en silencio (patron de fractales.py).
PASOS_MAX = 12          # pasos maximos de una traza ReAct
HERRAMIENTAS_MAX = 9    # herramientas maximas de un catalogo (grid 3x3)
LINEAS_MAX = 8          # lineas maximas de una tarjeta JSON

# Paleta propia de la libreria (coincide con la del curso).
COLOR_AGENTE = "#22d3ee"     # el agente, sus pensamientos
COLOR_MUNDO = "#a78bfa"      # el mundo/entorno: datos, resultados
COLOR_ACCION = "#f59e0b"     # ACCIONES: llamadas a herramientas, el lazo
COLOR_OK = "#34d399"         # validacion correcta, accion permitida
COLOR_PELIGRO = "#f43f5e"    # error, inyeccion, accion bloqueada
COLOR_EJE = "#31414f"        # mobiliario
COLOR_TENUE = CODE_MUTED     # lo que queda en segundo plano
COLOR_TEXTO = CODE_INK       # texto de marca (titulos, nombres de cajas)
FONDO = CODE_BG              # fondo de marca

# Alias cortos con los nombres que usa la tabla de paleta del curso, para que
# el style_block de los clips pueda escribir `color=C_ACENTO` tal cual.
C_AGENTE, C_MUNDO, C_ACENTO = COLOR_AGENTE, COLOR_MUNDO, COLOR_ACCION
C_OK, C_PELIGRO, C_EJE, C_TENUE = COLOR_OK, COLOR_PELIGRO, COLOR_EJE, COLOR_TENUE

_EPS = 1e-9

# Estilo por tipo de burbuja: (color, borde punteado, stroke, relleno).
# El punteado distingue lo que el agente PIENSA (interno, no verificable) de
# lo que HACE u OBSERVA (solido, comprobable).
_ESTILOS = {
    "pensamiento": (COLOR_AGENTE, True, 2.2, 0.10),
    "accion": (COLOR_ACCION, False, 2.5, 0.12),
    "observacion": (COLOR_MUNDO, False, 1.6, 0.08),
    "peligro": (COLOR_PELIGRO, False, 2.5, 0.12),
}


# --- utilidades internas ----------------------------------------------
def _hud(texto, font_size=16, color=COLOR_TENUE):
    """Text en Space Mono (la fuente de telemetria de la marca).

    Registra las fuentes en la PRIMERA LLAMADA, nunca al importar el modulo
    (patron de `atencion.bloque_transformer`). Si el registro fallara cae al
    Text por defecto en vez de reventar el render. Una cadena vacia se
    sustituye por un espacio: Manim no sabe rasterizar texto sin glifos.
    """
    texto = str(texto) if str(texto).strip() else " "
    try:
        registrar_fuentes()
        return Text(texto, font=FUENTE_HUD, font_size=float(font_size),
                    color=color)
    except Exception:                      # sin fuentes de marca disponibles
        return Text(texto, font_size=float(font_size), color=color)


def _sangria(linea):
    """(espacios_iniciales, contenido_sin_ellos) de una linea de JSON.

    La sangria NO se puede dejar dentro del Text: un espacio no pinta tinta,
    asi que no entra en la caja envolvente y cualquier alineado a la izquierda
    (el de `arrange(aligned_edge=LEFT)`) se la come. Se cuenta aqui y se
    aplica despues como un desplazamiento explicito de n anchos de caracter,
    que en una fuente monoespaciada es exactamente la sangria original.
    """
    texto = str(linea)
    n = len(texto) - len(texto.lstrip(" "))
    return n, texto[n:]


def _envolver(texto, chars=30):
    """Parte `texto` en lineas de ~`chars` caracteres respetando los '\\n'.

    Corta solo entre palabras: una palabra mas larga que `chars` se deja
    entera (mejor una linea larga que una palabra partida). Los saltos que
    ya trae el texto se respetan como separadores de parrafo.
    """
    chars = int(max(8, chars))
    lineas = []
    for parrafo in str(texto).split("\n"):
        palabras = parrafo.split()
        if not palabras:
            lineas.append("")
            continue
        actual = palabras[0]
        for palabra in palabras[1:]:
            if len(actual) + 1 + len(palabra) <= chars:
                actual += " " + palabra
            else:
                lineas.append(actual)
                actual = palabra
        lineas.append(actual)
    return "\n".join(lineas)


def _marca_ok(tam=0.30, color=COLOR_OK, grosor=3.2):
    """Palomita como VGroup de 2 Lines (nunca un glifo: no depende de fuente).

    El trazo corto baja y el largo sube, con la union en el vertice; el grupo
    entero queda centrado en el origen y mide `tam` de ancho.
    """
    corto = Line(np.array([-0.45, 0.05, 0.0]), np.array([-0.12, -0.32, 0.0]))
    largo = Line(np.array([-0.12, -0.32, 0.0]), np.array([0.48, 0.36, 0.0]))
    marca = VGroup(corto, largo)
    marca.set_stroke(color=color, width=float(grosor))
    marca.scale_to_fit_width(float(tam))
    marca.move_to(ORIGIN)
    return marca


def _marca_mal(tam=0.26, color=COLOR_PELIGRO, grosor=3.2):
    """Tache como VGroup de 2 Lines cruzadas, centrado en el origen."""
    a = Line(np.array([-0.5, -0.5, 0.0]), np.array([0.5, 0.5, 0.0]))
    b = Line(np.array([-0.5, 0.5, 0.0]), np.array([0.5, -0.5, 0.0]))
    marca = VGroup(a, b)
    marca.set_stroke(color=color, width=float(grosor))
    marca.scale_to_fit_width(float(tam))
    marca.move_to(ORIGIN)
    return marca


def _caja(ancho, alto, color, stroke=2.5, relleno=0.12, radio=0.12):
    """RoundedRectangle con el lenguaje visual de `bloques.bloque`."""
    return RoundedRectangle(corner_radius=float(radio), width=float(ancho),
                            height=float(alto), color=color, fill_color=color,
                            fill_opacity=float(relleno),
                            stroke_width=float(stroke))


# --- el lazo del agente ------------------------------------------------
def lazo_agente(radio=1.55, etiquetas=("PERCIBIR", "RAZONAR", "ACTUAR"),
                color=COLOR_ACCION, font_size=15, color_nodo=None):
    """El ciclo del agente: 3 nodos sobre un anillo y flechas de arco entre si.

    Los nodos son circulos equiespaciados a 120 grados (el primero arriba, y
    el ciclo avanza en SENTIDO HORARIO, que es como se lee un reloj), con su
    etiqueta HUD DENTRO del circulo: el radio del nodo se calcula a partir de
    la etiqueta mas ancha, asi que ninguna etiqueta se sale ni pisa el anillo.

    Las flechas son arcos sobre el mismo anillo, recortados en los dos
    extremos por el semiangulo que ocupa el nodo mas un margen: NO tocan los
    circulos, se ve aire entre la punta y el nodo de llegada. El ultimo arco
    cierra el ciclo (actuar -> percibir).

    Expone `.nodos` (lista de VGroup(circulo, etiqueta), cada uno con
    `.circulo` y `.texto`) y `.flechas` (lista de Arc con punta, en el orden
    del ciclo: la flecha k sale del nodo k).
    """
    radio = float(max(0.6, radio))
    color_nodo = color if color_nodo is None else color_nodo
    textos = [_hud(str(e), font_size=font_size, color=color_nodo)
              for e in list(etiquetas)[:3]]
    while len(textos) < 3:                 # menos de 3 etiquetas: se rellena
        textos.append(_hud("", font_size=font_size, color=color_nodo))

    # Radio del nodo: cabe la etiqueta mas ancha con 0.12 de aire a cada lado,
    # con un techo relativo al anillo para que los circulos no se toquen.
    mas_ancha = max((float(t.width) for t in textos), default=0.0)
    r_nodo = float(np.clip(mas_ancha / 2.0 + 0.12, 0.28, radio * 0.44))

    grupo = VGroup()
    grupo.nodos, grupo.flechas = [], []
    grupo.color = color

    angulos = [PI / 2.0 - k * 2.0 * PI / 3.0 for k in range(3)]
    for ang, texto in zip(angulos, textos):
        centro = np.array([radio * np.cos(ang), radio * np.sin(ang), 0.0])
        circulo = Circle(radius=r_nodo, color=color_nodo,
                         fill_color=color_nodo, fill_opacity=0.12,
                         stroke_width=2.5)
        circulo.move_to(centro)
        if texto.width > r_nodo * 1.68:
            texto.scale_to_fit_width(r_nodo * 1.68)
        texto.move_to(centro)
        nodo = VGroup(circulo, texto)
        nodo.circulo, nodo.texto = circulo, texto
        grupo.nodos.append(nodo)
        grupo.add(nodo)

    # Recorte angular: lo que tapa el nodo (asin(r_nodo/radio)) mas 0.11 rad
    # de aire. Con los valores por defecto el arco barre ~58 de los 120 grados.
    tapado = float(np.arcsin(np.clip(r_nodo / radio, 0.0, 0.99)))
    margen = tapado + 0.11
    barrido = 2.0 * PI / 3.0 - 2.0 * margen
    for k in range(3):
        inicio = angulos[k] - margen
        if barrido <= 0.05:                # nodos gigantes: no cabe el arco
            continue
        trazo = Arc(radius=radio, start_angle=inicio, angle=-barrido,
                    arc_center=ORIGIN)
        trazo.set_stroke(color=color, width=3.2, opacity=1.0)
        trazo.set_fill(opacity=0.0)
        try:
            trazo.add_tip(tip_length=0.22, tip_width=0.20)
        except TypeError:                  # firma antigua de add_tip
            trazo.add_tip(tip_length=0.22)
        grupo.flechas.append(trazo)
        grupo.add(trazo)
    return grupo


def girar_lazo(lazo, vueltas=1.0, color=None, run_time=None, por_tramo=0.7,
               cola=0.5, ancho=6.0):
    """Un pulso recorre las flechas del lazo `vueltas` veces, EN ORDEN.

    `vueltas` puede ser fraccionario: cada vuelta son 3 tramos, asi que
    `vueltas=0.34` recorre solo la primera flecha (0.34*3 = 1.02 tramos) y
    `vueltas=2` da dos vueltas completas. El tramo final incompleto se anima
    como un arco PARCIAL (`pointwise_become_partial`), no como uno entero: el
    pulso se detiene de verdad a media flecha.

    Si `run_time` es None cada tramo dura `por_tramo`; si se da, ese tiempo se
    REPARTE entre los tramos en proporcion a su longitud, de modo que la
    velocidad angular del pulso es constante.

    Devuelve una `Succession` sobre COPIAS de los arcos: no deja updaters ni
    modifica el lazo de la escena. Las copias se toman en el MOMENTO de la
    llamada y se les quita la punta (`pop_tips`), de modo que el pulso sigue
    la posicion y la escala ACTUALES del lazo — no las que tenia al crearse —
    y se detiene donde empieza la cabeza de la flecha.
    """
    trazos = []
    for flecha in list(getattr(lazo, "flechas", []) or []):
        limpio = flecha.copy()
        if hasattr(limpio, "pop_tips"):
            limpio.pop_tips()
        trazos.append(limpio)
    tono = getattr(lazo, "color", COLOR_ACCION) if color is None else color
    n = len(trazos)
    total = float(vueltas) * n if n else 0.0
    if n == 0 or total <= 0.05:
        return Wait(float(run_time) if run_time else 0.1)

    enteros = int(np.floor(total + 1e-9))
    resto = total - enteros
    # Fracciones de tramo a recorrer, en orden ciclico.
    fracciones = [1.0] * enteros
    if resto > 0.06:
        fracciones.append(resto)
    if not fracciones:                     # vueltas muy pequenas: un tramo minimo
        fracciones = [max(0.06, resto)]

    suma = sum(fracciones)
    pasos = []
    for i, frac in enumerate(fracciones):
        base = trazos[i % n]
        copia = base.copy()
        if frac < 0.999:
            copia.pointwise_become_partial(base, 0.0, float(frac))
        copia.set_fill(opacity=0.0)
        copia.set_stroke(color=tono, width=float(ancho), opacity=1.0)
        dur = (float(run_time) * frac / suma) if run_time else \
            float(por_tramo) * frac
        pasos.append(ShowPassingFlash(copia, time_width=float(cola),
                                      run_time=max(0.05, dur)))
    return Succession(*pasos)


# --- mensajes y trazas (ReAct) ----------------------------------------
def burbuja(texto, tipo="pensamiento", ancho_max=4.6, font_size=19,
            chars=30, color=None):
    """Caja redondeada + texto multilinea: un mensaje del agente.

    `tipo` elige el estilo (un tipo desconocido cae en "pensamiento"):

        pensamiento  cian,    borde PUNTEADO  (lo interno, no verificable)
        accion       ambar,   borde solido    (una llamada a herramienta)
        observacion  violeta, borde fino      (lo que devuelve el mundo)
        peligro      rojo,    borde solido    (error o inyeccion)

    El texto se envuelve a ~`chars` caracteres por linea respetando los
    '\\n' que ya traiga, y si aun asi excede `ancho_max` se reescala entero.
    El borde punteado se dibuja como un `DashedVMobject` ENCIMA de la caja de
    relleno, de modo que el relleno tenue se conserva igual que en los tipos
    solidos.

    Expone `.texto` (el Text), `.caja` (el RoundedRectangle de relleno) y
    `.borde` (lo que hay que recolorear: el punteado si lo hay, si no la caja).
    """
    estilo = _ESTILOS.get(str(tipo), _ESTILOS["pensamiento"])
    tono, punteado, stroke, relleno = estilo
    if color is not None:
        tono = color

    cuerpo = Text(_envolver(texto, chars) or " ", font_size=float(font_size),
                  color=tono, line_spacing=0.7)
    tope = float(ancho_max) - 0.44
    if cuerpo.width > tope > _EPS:
        cuerpo.scale_to_fit_width(tope)

    caja = _caja(float(cuerpo.width) + 0.44, float(cuerpo.height) + 0.36,
                 tono, stroke=stroke if not punteado else 0.0,
                 relleno=relleno, radio=0.12)
    cuerpo.move_to(caja.get_center())

    grupo = VGroup(caja)
    borde = caja
    if punteado:
        contorno = _caja(caja.width, caja.height, tono, stroke=stroke,
                         relleno=0.0, radio=0.12)
        contorno.move_to(caja.get_center())
        borde = DashedVMobject(contorno, num_dashes=34, dashed_ratio=0.55)
        borde.set_stroke(color=tono, width=float(stroke))
        grupo.add(borde)
    grupo.add(cuerpo)
    grupo.caja, grupo.borde, grupo.texto = caja, borde, cuerpo
    grupo.tipo = str(tipo)
    return grupo


def traza_react(pasos, ancho_max=5.2, buff=0.32, font_size=17, alto_max=5.2,
                chars=34):
    """Columna de burbujas: la traza de razonamiento de un agente ReAct.

    `pasos` es una lista de `(tipo, texto)` (tambien acepta strings sueltos,
    que se toman como "pensamiento"). Las burbujas se apilan hacia abajo
    alineadas por la IZQUIERDA — asi la columna se lee como un log — y si la
    pila supera `alto_max` se reescala ENTERA (nunca burbuja a burbuja: los
    tamanos de fuente distintos delatarian el truco). Recorta en silencio a
    `PASOS_MAX` pasos.

    Expone `.burbujas` (lista, en el mismo orden que `pasos`).
    """
    grupo = VGroup()
    grupo.burbujas = []
    for paso in list(pasos)[:PASOS_MAX]:
        if isinstance(paso, (tuple, list)) and len(paso) >= 2:
            tipo, texto = paso[0], paso[1]
        else:
            tipo, texto = "pensamiento", paso
        globo = burbuja(texto, tipo=tipo, ancho_max=ancho_max,
                        font_size=font_size, chars=chars)
        grupo.burbujas.append(globo)
        grupo.add(globo)
    if not grupo.burbujas:
        return grupo
    grupo.arrange(DOWN, buff=float(buff), aligned_edge=LEFT)
    if grupo.height > float(alto_max):
        grupo.scale_to_fit_height(float(alto_max))
    return grupo


# --- herramientas ------------------------------------------------------
def catalogo_herramientas(nombres, columnas=3, ancho=2.0, alto=0.62,
                          color=COLOR_EJE, font_size=15, color_texto=None):
    """Grid de mini-cajas estilo `bloque()`: el catalogo CERRADO del agente.

    Se rellena por filas de izquierda a derecha con `columnas` por fila (la
    ultima fila puede quedar incompleta). Recorta en silencio a
    `HERRAMIENTAS_MAX` nombres, que con el valor por defecto es exactamente
    un grid 3x3.

    `color` pinta la caja y `color_texto` el nombre; por defecto el nombre va
    en la tinta de marca, porque el color de mobiliario (`COLOR_EJE`) es
    demasiado oscuro para leerse sobre el fondo.

    Expone `.cajas` {nombre: VGroup(caja, etiqueta)} para poder `Indicate`
    una herramienta concreta por su nombre.
    """
    color_texto = COLOR_TEXTO if color_texto is None else color_texto
    ancho, alto = float(ancho), float(alto)
    grupo = VGroup()
    grupo.cajas = {}
    lista = [str(n) for n in list(nombres)[:HERRAMIENTAS_MAX]]
    for nombre in lista:
        caja = _caja(ancho, alto, color, stroke=2.5, relleno=0.12, radio=0.10)
        etiqueta = Text(nombre, font_size=float(font_size), color=color_texto)
        if etiqueta.width > ancho * 0.86:
            etiqueta.scale_to_fit_width(ancho * 0.86)
        etiqueta.move_to(caja.get_center())
        celda = VGroup(caja, etiqueta)
        celda.caja, celda.texto = caja, etiqueta
        grupo.add(celda)
        grupo.cajas[nombre] = celda
    if not lista:
        return grupo
    grupo.arrange_in_grid(cols=int(max(1, columnas)), buff=(0.26, 0.26),
                          flow_order="rd")
    return grupo


def tarjeta_json(lineas, ancho=3.6, font_size=16, color=COLOR_ACCION,
                 valida=None):
    """Caja con lineas monoespaciadas: la llamada a herramienta, y su veredicto.

    Las lineas van en Space Mono (`FUENTE_HUD`) alineadas a la IZQUIERDA, que
    es como se lee un JSON: la sangria de las lineas interiores se conserva
    (los espacios iniciales pasan por `_sangria`, porque Pango se los come).
    `lineas` puede ser una lista de strings o un unico string con '\\n'.
    Recorta en silencio a `LINEAS_MAX`.

    El veredicto: `valida=True` pinta el borde verde y pega una PALOMITA
    (dos Lines, jamas un glifo tipografico) como insignia sobre la esquina
    superior derecha; `valida=False` pinta el borde rojo y un TACHE; `None`
    deja el borde gris neutro y ninguna marca. La insignia va sobre la
    esquina con un disco de fondo, para no chocar nunca con el texto.

    Expone `.caja`, `.lineas` (lista de Text) y `.marca` (la insignia o None).
    """
    if isinstance(lineas, str):
        lineas = lineas.split("\n")
    lineas = [str(l) for l in list(lineas)[:LINEAS_MAX]] or [""]

    if valida is True:
        tono = COLOR_OK
    elif valida is False:
        tono = COLOR_PELIGRO
    else:
        tono = COLOR_TENUE

    sangrias = [_sangria(l) for l in lineas]
    textos = VGroup(*[_hud(contenido, font_size=font_size, color=color)
                      for _, contenido in sangrias])
    textos.arrange(DOWN, buff=0.10, aligned_edge=LEFT)
    # Ancho de un caracter, medido sobre la linea mas larga (Space Mono es
    # monoespaciada): con el se reinyecta la sangria que el alineado quito.
    ref = max(zip(textos, sangrias), key=lambda par: len(par[1][1]))
    largo = len(ref[1][1].rstrip())
    ancho_char = (float(ref[0].width) / largo) if largo else 0.0
    for texto, (n, _) in zip(textos, sangrias):
        if n:
            texto.shift(RIGHT * (n * ancho_char))
    ancho = float(ancho)
    if textos.width > ancho * 0.88:
        textos.scale_to_fit_width(ancho * 0.88)

    caja = _caja(ancho, float(textos.height) + 0.44, tono, stroke=2.5,
                 relleno=0.10, radio=0.12)
    textos.move_to(caja.get_center())
    # Alineacion a la izquierda dentro de la caja (arrange solo alinea entre
    # si). Una tarjeta de lineas en blanco no tiene geometria que alinear:
    # `align_to` reventaria sobre una familia sin puntos.
    if textos.family_members_with_points():
        textos.align_to(caja, LEFT)
        textos.shift(RIGHT * 0.22)

    grupo = VGroup(caja, textos)
    marca = None
    if valida is not None:
        disco = Circle(radius=0.17, color=tono, fill_color=FONDO,
                       fill_opacity=1.0, stroke_width=2.2)
        signo = _marca_ok(0.17, tono) if valida else _marca_mal(0.15, tono)
        marca = VGroup(disco, signo)
        signo.move_to(disco.get_center())
        marca.move_to(caja.get_corner(UP + RIGHT))
        marca.set_z_index(3)
        grupo.add(marca)
    grupo.caja, grupo.lineas, grupo.marca = caja, list(textos), marca
    grupo.valida = valida
    return grupo


# --- seguridad y autonomia ---------------------------------------------
def escudo(radio=0.55, color=COLOR_OK, relleno=0.12):
    """Escudo minimalista: contorno cerrado y suave + palomita dentro.

    El contorno es un `VMobject` con `set_points_smoothly` sobre un perfil
    escrito a mano: hombros anchos arriba, lados que se estrechan y una punta
    inferior (los tres puntos de la punta van muy juntos para que el suavizado
    la deje afilada en vez de redonda). Todo escala con `radio`.

    Expone `.contorno` y `.marca`.
    """
    r = float(max(0.15, radio))
    perfil = [(-1.00, 0.78), (0.00, 0.98), (1.00, 0.78), (0.94, -0.02),
              (0.60, -0.72), (0.26, -1.02), (0.00, -1.15), (-0.26, -1.02),
              (-0.60, -0.72), (-0.94, -0.02)]
    puntos = [np.array([x * r, y * r, 0.0]) for x, y in perfil]
    contorno = VMobject()
    contorno.set_points_smoothly(puntos + [puntos[0]])
    contorno.set_stroke(color=color, width=2.8, opacity=1.0)
    contorno.set_fill(color=color, opacity=float(relleno))

    marca = _marca_ok(r * 0.92, color, grosor=max(2.0, 5.0 * r))
    marca.move_to(np.array([0.0, -0.02 * r, 0.0]))
    grupo = VGroup(contorno, marca)
    grupo.contorno, grupo.marca = contorno, marca
    return grupo


def escala_autonomia(nivel=2, etiquetas=("L0", "L1", "L2", "L3", "L4", "L5"),
                     largo=6.2, color=COLOR_ACCION, font_size=16,
                     color_eje=COLOR_EJE):
    """Regla horizontal L0..L5 con un marcador triangular sobre un nivel.

    La linea y las muescas son mobiliario (`color_eje`); las etiquetas van
    DEBAJO de cada muesca en Space Mono tenue, y el marcador —un triangulo
    que apunta hacia abajo, en `color`— queda ENCIMA de la muesca de `nivel`,
    sin taparla.

    `pos_nivel(n)` devuelve el np.array donde debe quedar el CENTRO del
    marcador para el nivel n, calculado a partir de la posicion ACTUAL de las
    muescas: sigue siendo correcto despues de mover o escalar el grupo, que
    es justo lo que hace falta para animar `marcador.animate.move_to(
    escala.pos_nivel(4))`.

    Expone `.linea`, `.muescas`, `.etiquetas`, `.marcador` y `.pos_nivel`.
    """
    etiquetas = [str(e) for e in list(etiquetas)] or ["L0"]
    n_pasos = max(2, len(etiquetas))
    largo = float(max(1.0, largo))
    x0, x1 = -largo / 2.0, largo / 2.0

    linea = Line(np.array([x0, 0.0, 0.0]), np.array([x1, 0.0, 0.0]),
                 color=color_eje, stroke_width=3.0)
    grupo = VGroup(linea)
    grupo.linea = linea
    grupo.muescas, grupo.etiquetas = [], []

    for i, nombre in enumerate(etiquetas):
        x = x0 + largo * i / (n_pasos - 1)
        muesca = Line(np.array([x, -0.13, 0.0]), np.array([x, 0.13, 0.0]),
                      color=color_eje, stroke_width=3.0)
        texto = _hud(nombre, font_size=font_size, color=COLOR_TENUE)
        texto.next_to(muesca, DOWN, buff=0.16)
        grupo.muescas.append(muesca)
        grupo.etiquetas.append(texto)
        grupo.add(muesca, texto)

    marcador = Triangle(color=color, fill_color=color, fill_opacity=1.0,
                        stroke_width=1.5)
    marcador.scale_to_fit_width(0.30).rotate(PI)     # punta hacia abajo
    grupo.marcador = marcador
    grupo.add(marcador)

    _buff = 0.12

    def pos_nivel(n, _g=grupo, _buff=_buff):
        """Centro del marcador para el nivel `n` (se recorta al rango valido)."""
        i = int(np.clip(int(n), 0, len(_g.muescas) - 1))
        return (np.asarray(_g.muescas[i].get_top(), dtype=np.float64)
                + np.array([0.0, _buff + float(_g.marcador.height) / 2.0, 0.0]))

    grupo.pos_nivel = pos_nivel
    marcador.move_to(pos_nivel(nivel))
    grupo.nivel = int(np.clip(int(nivel), 0, len(grupo.muescas) - 1))
    return grupo

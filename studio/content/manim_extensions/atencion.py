"""Embeddings y atencion animables: tokens, mapa semantico y softmax(Q.K).

Pensado para el curso "De la palabra al vector: embeddings y atencion". Todo
es determinista y sin entrenar: `EMBEDDINGS` es un diccionario de vectores 2D
ESCRITOS A MANO, y los pesos de atencion salen de un softmax de productos
punto sobre esos mismos vectores. Mismo script -> mismo render, condicion
necesaria para trabajar con `--disable_caching`. Nada de `random`, nada de
red, nada de disco.

La regla de color del curso: el TEXTO es cian, el SIGNIFICADO violeta, el
MECANISMO (atencion, pesos, Q/K/V) ambar, la PROBABILIDAD verde, el FALLO
rojo. Las cajas (`ficha_token`, `bloque_transformer`) usan el mismo lenguaje
visual que `bloques.bloque`: esquina redondeada, stroke fino y relleno muy
bajo del propio color.

El mapa semantico esta calibrado para que la geometria cuente la historia:

    rey - hombre + mujer  ->  a 0.07 de reina
    cos(gato, felino) = 0.994      cos(gato, luna) = -0.033
    'banco' equidista de 'dinero' y de 'parque' (1.06 de cada uno)
    atencion desde 'banco' en "el banco cobra comisiones al cliente":
        cobra 0.32 > comisiones 0.24 > cliente 0.10 > el = al 0.03

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render): `TOKENS_MAX`
y `PALABRAS_MAX` recortan en silencio, como hace fractales.py.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from atencion import (fila_tokens, pesos_atencion, abanico_atencion,
                          mapa_embeddings, distribucion_siguiente)

    frase = "el banco cobra comisiones al cliente"
    fila = fila_tokens(frase)
    pesos = pesos_atencion(frase, 1)          # query = 'banco'
    self.add(fila, abanico_atencion(fila, 1, pesos))
"""

import unicodedata

import numpy as np

from manim import (Angle, ArcBetweenPoints, Arrow, Dot, Line, ORIGIN,
                   Rectangle, RoundedRectangle, Text, UR, VGroup)

from code_brand import CODE_BG, CODE_INK, CODE_MUTED, etiqueta_hud

# Limites duros: se recortan en silencio (patron de fractales.py).
TOKENS_MAX = 12         # fichas maximas de una fila de tokens
PALABRAS_MAX = 24       # palabras maximas de cualquier calculo de atencion

# Paleta propia de la libreria (coincide con la del curso).
COLOR_TOKEN = "#22d3ee"       # tokens, texto crudo
COLOR_VECTOR = "#a78bfa"      # vectores/embeddings, significado
COLOR_MECANISMO = "#f59e0b"   # el mecanismo: atencion, pesos, Q/K/V
COLOR_PROB = "#34d399"        # probabilidades, la palabra elegida
COLOR_MAL = "#f43f5e"         # ambiguedad, el embedding que falla
COLOR_EJE = "#31414f"         # ejes y mobiliario
COLOR_TENUE = CODE_MUTED      # lo que queda en segundo plano
FONDO = CODE_BG               # fondo de marca

# Alias cortos con los nombres que usa la tabla de paleta del curso, para que
# el style_block de los clips pueda escribir `color=C_ACENTO` tal cual.
C_TOKEN, C_VECTOR, C_ACENTO = COLOR_TOKEN, COLOR_VECTOR, COLOR_MECANISMO
C_PROB, C_MAL, C_EJE, C_TENUE = COLOR_PROB, COLOR_MAL, COLOR_EJE, COLOR_TENUE

_EPS = 1e-9

# --- vocabulario de demo ----------------------------------------------
# Embeddings 2D fijos en [-2, 2]^2, puestos a mano por sectores angulares
# para que la geometria sea legible en pantalla y coherente al medirla:
#
#   ~ 60..115 grados  animales (gato, perro, felino, pez) y sus acciones
#   ~  13..33 grados  personas y realeza (hombre, mujer, rey, reina)
#   ~ 175..191 grados cielo (sol, luna)
#   ~ 218..229 grados exterior (parque, siento)
#   ~ -64..-28 grados finanzas (dinero, cobra, comisiones, cliente)
#   ~ -94 grados      'banco', a MEDIO CAMINO entre parque y dinero
#
# El eje "realeza" (hombre->rey) y el eje "genero" (hombre->mujer) son
# perpendiculares y constantes: por eso rey - hombre + mujer cae sobre reina.
# Las palabras funcionales (el, la, en, me, al...) se dejan FUERA a proposito:
# fuera del vocabulario -> vector (0, 0) -> producto punto nulo -> peso bajo.
EMBEDDINGS = {
    # animales
    "gato": (-0.25, 1.62),
    "felino": (-0.42, 1.55),
    "perro": (-0.05, 1.70),
    "pez": (-0.62, 1.28),
    # acciones cotidianas, junto a los animales
    "dormir": (0.35, 1.55),
    "comer": (0.72, 1.28),
    # personas y realeza
    "hombre": (1.50, 0.35),
    "mujer": (1.50, 0.95),
    "rey": (1.95, 0.45),
    "reina": (2.00, 1.00),
    # cielo
    "sol": (-1.72, 0.15),
    "luna": (-1.60, -0.30),
    # exterior
    "parque": (-1.15, -1.30),
    "siento": (-1.05, -1.05),
    # finanzas
    "dinero": (0.95, -1.55),
    "cobra": (0.80, -1.62),
    "comisiones": (1.10, -1.42),
    "cliente": (1.62, -0.85),
    # la palabra ambigua: punto medio exacto de parque y dinero
    "banco": (-0.10, -1.42),
}


# --- utilidades internas ----------------------------------------------
def _normalizar(palabra):
    """Clave de vocabulario: minusculas, sin acentos y sin puntuacion.

    Asi 'Banco,' y 'BANCO' encuentran el mismo vector, y las palabras con
    tilde de las frases del curso ('subio') no fallan por la tilde.
    """
    texto = unicodedata.normalize("NFD", str(palabra).strip().lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.strip(".,;:!?¡¿()[]\"'«»…-")


def _palabras(frase, tope):
    """Lista de palabras de `frase` (str o iterable), recortada a `tope`."""
    if isinstance(frase, str):
        crudas = frase.split()
    else:
        crudas = [str(p) for p in frase]
    return crudas[:int(max(1, tope))]


def vector(palabra):
    """Embedding de `palabra` como np.array (2,).

    Acepta tambien una tupla/lista (x, y) y la devuelve tal cual: los
    helpers geometricos aceptan indistintamente nombres y coordenadas. Una
    palabra fuera del vocabulario vale (0, 0).
    """
    if isinstance(palabra, (tuple, list, np.ndarray)):
        return np.asarray(palabra, dtype=np.float64).ravel()[:2]
    return np.asarray(EMBEDDINGS.get(_normalizar(palabra), (0.0, 0.0)),
                      dtype=np.float64)


def _matriz(palabras):
    """Matriz (n, 2) con el embedding de cada palabra de la lista."""
    return np.stack([vector(p) for p in palabras]) if palabras \
        else np.zeros((0, 2))


def _softmax(logits):
    """Softmax estable (resta el maximo antes de exponenciar). Suma 1."""
    logits = np.asarray(logits, dtype=np.float64).ravel()
    if logits.size == 0:
        return logits
    e = np.exp(logits - float(np.max(logits)))
    return e / max(float(np.sum(e)), _EPS)


def _alto_ficha(font_size):
    """Alto uniforme de una ficha para un tamano de fuente dado.

    Fijo a proposito (no depende de si la palabra tiene tildes o rabos): las
    fichas de una fila deben tener EXACTAMENTE el mismo alto para que los
    arcos del abanico salgan todos de la misma altura.
    """
    return max(0.34, float(font_size) * 0.0235)


# --- tokens ------------------------------------------------------------
def ficha_token(texto, color=COLOR_TOKEN, font_size=24, ancho_min=0.72):
    """VGroup(caja redondeada, Text) compacto: un token en pantalla.

    Mismo lenguaje visual que `bloques.bloque` (esquina redondeada, stroke
    2.5, relleno del propio color al 12 %) pero en formato pastilla: el ancho
    se ajusta al texto con un margen, nunca por debajo de `ancho_min`.

    Expone `.texto` (el Text) y `.caja` (el RoundedRectangle) por comodidad,
    para poder recolorear o `Indicate` solo una parte.
    """
    etiqueta = Text(str(texto), font_size=font_size, color=color)
    alto = _alto_ficha(font_size)
    ancho = max(float(ancho_min), float(etiqueta.width) + 0.34)
    caja = RoundedRectangle(corner_radius=0.10, width=ancho, height=alto,
                            color=color, fill_color=color,
                            fill_opacity=0.12, stroke_width=2.5)
    if etiqueta.width > ancho * 0.88:
        etiqueta.scale_to_fit_width(ancho * 0.88)
    etiqueta.move_to(caja.get_center())
    ficha = VGroup(caja, etiqueta)
    ficha.caja = caja
    ficha.texto = etiqueta
    return ficha


def fila_tokens(frase, color=COLOR_TOKEN, font_size=24, buff=0.18,
                ancho_max=11.5):
    """Fila de fichas, una por palabra de `frase`, ordenadas a la derecha.

    `frase` puede ser un string (se parte por espacios) o una lista de
    palabras ya tokenizada. Si la fila supera `ancho_max` se reescala entera
    (las fichas siguen alineadas y con el mismo alto). Recorta en silencio a
    `TOKENS_MAX` palabras.

    Expone `.fichas` (lista de fichas, misma que el VGroup) y `.palabras`
    (los strings mostrados), utiles para `barras_pesos` y `abanico_atencion`.
    """
    palabras = _palabras(frase, TOKENS_MAX)
    fila = VGroup(*[ficha_token(p, color=color, font_size=font_size)
                    for p in palabras])
    fila.arrange(buff=float(buff))
    if fila.width > float(ancho_max):
        fila.scale_to_fit_width(float(ancho_max))
    fila.fichas = list(fila)
    fila.palabras = palabras
    return fila


# --- mapa semantico ----------------------------------------------------
def mapa_embeddings(ejes, palabras, colores=None, font_size=17,
                    direcciones=None):
    """Nube de puntos etiquetados sobre `ejes`, usando `EMBEDDINGS`.

    `colores` puede ser None (todo violeta), un color unico, una lista en el
    orden de `palabras` o un dict {palabra: color}. `direcciones` es un dict
    opcional {palabra: direccion} para el `next_to` de la etiqueta (por
    defecto UR), que es como se evita que dos etiquetas vecinas se pisen.

    Expone `.puntos` {palabra: Dot} y `.etiquetas` {palabra: Text}.
    """
    palabras = _palabras(palabras, PALABRAS_MAX)
    direcciones = dict(direcciones or {})
    grupo = VGroup()
    grupo.puntos, grupo.etiquetas = {}, {}

    for i, palabra in enumerate(palabras):
        if colores is None:
            color = COLOR_VECTOR
        elif isinstance(colores, dict):
            color = colores.get(palabra, COLOR_VECTOR)
        elif isinstance(colores, (list, tuple)):
            color = colores[i % len(colores)]
        else:
            color = colores
        x, y = vector(palabra)
        punto = Dot(ejes.c2p(float(x), float(y)), radius=0.062, color=color,
                    fill_opacity=1.0)
        punto.set_z_index(2)
        texto = Text(str(palabra), font_size=font_size, color=color)
        texto.next_to(punto, direcciones.get(palabra, UR), buff=0.08)
        texto.set_z_index(2)
        grupo.add(VGroup(punto, texto))
        grupo.puntos[palabra] = punto
        grupo.etiquetas[palabra] = texto
    return grupo


def flecha_vector(ejes, desde, hasta, color=COLOR_VECTOR, grosor=5.0):
    """Arrow entre dos posiciones del plano de `ejes`.

    `desde` y `hasta` pueden ser tuplas (x, y) o nombres de palabra (se leen
    de `EMBEDDINGS`); asi `flecha_vector(ejes, (0, 0), "rey")` dibuja el
    vector de 'rey' desde el origen sin repetir coordenadas.
    """
    a, b = vector(desde), vector(hasta)
    return Arrow(ejes.c2p(float(a[0]), float(a[1])),
                 ejes.c2p(float(b[0]), float(b[1])),
                 buff=0.0, color=color, stroke_width=float(grosor),
                 max_tip_length_to_length_ratio=0.16)


def arco_similitud(ejes, palabra_a, palabra_b, color=COLOR_MECANISMO,
                   radio=0.55):
    """Angle entre los vectores origen->a y origen->b sobre `ejes`.

    Es la lectura visual de `similitud_coseno`: angulo pequeno = coseno alto.
    """
    origen = ejes.c2p(0.0, 0.0)
    a, b = vector(palabra_a), vector(palabra_b)
    l1 = Line(origen, ejes.c2p(float(a[0]), float(a[1])))
    l2 = Line(origen, ejes.c2p(float(b[0]), float(b[1])))
    return Angle(l1, l2, radius=float(radio), color=color, stroke_width=3.0)


def similitud_coseno(a, b):
    """Coseno del angulo entre dos embeddings, en [-1, 1].

    `a` y `b` son nombres de palabra o tuplas (x, y). Un vector nulo (palabra
    fuera del vocabulario) da 0.0 en vez de dividir por cero.
    """
    va, vb = vector(a), vector(b)
    na, nb = float(np.linalg.norm(va)), float(np.linalg.norm(vb))
    if na < _EPS or nb < _EPS:
        return 0.0
    return float(np.dot(va, vb) / (na * nb))


# --- atencion ----------------------------------------------------------
def pesos_atencion(frase, idx_query, temperatura=1.0):
    """softmax(q . k / T) de la palabra `idx_query` sobre toda la frase.

    Atencion de un solo cabezal con Q = K = el propio embedding: el producto
    punto mide a la vez direccion y magnitud, asi que una palabra funcional
    (fuera del vocabulario -> (0, 0)) recibe logit 0 y queda naturalmente
    abajo. `temperatura` < 1 afila la distribucion, > 1 la aplana. Devuelve
    un np.ndarray de la longitud de la frase que suma 1 (incluye el peso de
    la propia query). Recorta en silencio a `PALABRAS_MAX` palabras.
    """
    palabras = _palabras(frase, PALABRAS_MAX)
    V = _matriz(palabras)
    if V.shape[0] == 0:
        return np.zeros(0)
    idx = int(np.clip(int(idx_query), 0, V.shape[0] - 1))
    t = float(temperatura)
    t = t if abs(t) > _EPS else 1.0
    return _softmax((V @ V[idx]) / t)


def abanico_atencion(fila, idx_query, pesos, color=COLOR_MECANISMO,
                     altura=1.1):
    """Arcos desde la ficha query hacia las demas, POR ENCIMA de la fila.

    Cada arco va del borde superior de la ficha query al borde superior de
    otra ficha y se comba hacia arriba, asi que jamas cruza las fichas ni el
    texto. El grosor y la opacidad codifican el peso:

        stroke_width   = 1.0 + 7.0 * peso
        stroke_opacity = 0.35 + 0.65 * peso

    La flecha mas lejana sube hasta `altura`; las cercanas suben menos, de
    modo que los arcos quedan anidados en abanico y no se solapan. El arco de
    la propia query se omite. `fila` es lo que devuelve `fila_tokens`.
    """
    fichas = list(getattr(fila, "fichas", fila))
    pesos = np.asarray(pesos, dtype=np.float64).ravel()
    grupo = VGroup()
    if len(fichas) < 2 or pesos.size == 0:
        return grupo

    idx = int(np.clip(int(idx_query), 0, len(fichas) - 1))
    origen = fichas[idx].get_top()
    distancias = [abs(float(f.get_top()[0] - origen[0]))
                  for k, f in enumerate(fichas) if k != idx]
    lejos = max(distancias) if distancias else 1.0

    for k, ficha in enumerate(fichas):
        if k == idx or k >= pesos.size:
            continue
        destino = ficha.get_top()
        # Cuerda horizontal a la altura del borde superior mas alto: el arco
        # se comba hacia arriba desde ahi y nunca baja sobre las fichas.
        y = max(float(origen[1]), float(destino[1]))
        p1 = np.array([float(origen[0]), y, 0.0])
        p2 = np.array([float(destino[0]), y, 0.0])
        cuerda = abs(p2[0] - p1[0])
        if cuerda < 1e-6:
            continue
        # Flecha (sagita) proporcional a la distancia: h = (L/2) tan(ang/4).
        h = float(altura) * (0.45 + 0.55 * cuerda / max(lejos, _EPS))
        ang = 4.0 * float(np.arctan(2.0 * h / cuerda))
        # Izquierda -> derecha con angulo negativo = arco combado hacia UP.
        izq, der = (p1, p2) if p1[0] < p2[0] else (p2, p1)
        peso = float(np.clip(pesos[k], 0.0, 1.0))
        arco = ArcBetweenPoints(izq, der, angle=-ang)
        arco.set_stroke(color=color, width=1.0 + 7.0 * peso,
                        opacity=0.35 + 0.65 * peso)
        arco.set_fill(opacity=0.0)
        grupo.add(arco)
    return grupo


def barras_pesos(pesos, etiquetas, origen=ORIGIN, ancho=0.5, alto_max=1.5,
                 color=COLOR_MECANISMO, font_size=16):
    """Barras verticales (una por peso) con su etiqueta debajo.

    La barra mas alta mide `alto_max`; el resto va en proporcion a su peso,
    de modo que la lectura no depende de lo afilada que este la distribucion.
    El grupo entero queda centrado en `origen`. Recorta a `PALABRAS_MAX`.
    """
    pesos = np.asarray(pesos, dtype=np.float64).ravel()[:PALABRAS_MAX]
    etiquetas = _palabras(etiquetas, PALABRAS_MAX)
    grupo = VGroup()
    if pesos.size == 0:
        return grupo

    pico = float(np.max(np.abs(pesos)))
    pico = pico if pico > _EPS else 1.0
    paso = float(ancho) * 1.55
    x0 = -paso * (pesos.size - 1) / 2.0

    # Las etiquetas se encogen TODAS con el mismo factor (el que exija la
    # mas ancha): encoger solo la larga ("comisiones") dejaba una fuente
    # visiblemente menor que sus vecinas y rompia la consistencia.
    textos = [Text(str(e), font_size=font_size, color=COLOR_TENUE)
              for e in etiquetas[:pesos.size]]
    tope = float(ancho) * 1.35
    mas_ancha = max((t.width for t in textos), default=0.0)
    factor = min(1.0, tope / mas_ancha) if mas_ancha > _EPS else 1.0

    for i in range(pesos.size):
        alto = max(0.04, float(alto_max) * float(pesos[i]) / pico)
        barra = Rectangle(width=float(ancho), height=alto, color=color,
                          fill_color=color, fill_opacity=0.85,
                          stroke_width=1.2)
        barra.move_to(np.array([x0 + paso * i, alto / 2.0, 0.0]))
        columna = VGroup(barra)
        if i < len(textos):
            texto = textos[i]
            texto.scale(factor)
            texto.next_to(barra, np.array([0.0, -1.0, 0.0]), buff=0.12)
            texto.set_y(-0.18 - texto.height / 2.0)
            columna.add(texto)
        grupo.add(columna)
    grupo.move_to(origen)
    return grupo


def mezcla_ponderada(frase, idx_query, pesos=None):
    """(x, y): el 'nuevo vector' de la query tras atender a la frase.

    Suma ponderada de los embeddings de la frase con `pesos`. Si `pesos` es
    None se calculan con `pesos_atencion(frase, idx_query)`, que es el caso
    de uso normal. Es el punto donde acaba la ficha 'banco (dinero)' del
    clip 5: el mismo token, movido hacia lo que atendio.
    """
    palabras = _palabras(frase, PALABRAS_MAX)
    if pesos is None:
        pesos = pesos_atencion(palabras, idx_query)
    pesos = np.asarray(pesos, dtype=np.float64).ravel()
    V = _matriz(palabras)
    n = min(V.shape[0], pesos.size)
    if n == 0:
        return (0.0, 0.0)
    mezcla = pesos[:n] @ V[:n]
    return (float(mezcla[0]), float(mezcla[1]))


# --- transformer y generacion -----------------------------------------
def bloque_transformer(etiqueta="ATENCION + MLP", ancho=3.4, alto=1.0,
                       color=COLOR_MECANISMO):
    """Caja estilo `bloques.bloque` con la etiqueta HUD del canal dentro.

    La etiqueta usa `code_brand.etiqueta_hud` (Space Mono, MAYUSCULAS con
    aire entre letras), que registra las fuentes en la PRIMERA LLAMADA, no al
    importar este modulo. Si el registro fallara, cae al Text por defecto.

    Expone `.caja` y `.texto`.
    """
    caja = RoundedRectangle(corner_radius=0.12, width=float(ancho),
                            height=float(alto), color=color, fill_color=color,
                            fill_opacity=0.10, stroke_width=2.5)
    try:
        texto = etiqueta_hud(str(etiqueta), font_size=16, color=color)
    except Exception:                      # sin fuentes de marca disponibles
        texto = Text(str(etiqueta).upper(), font_size=16, color=color)
    if texto.width > float(ancho) * 0.86:
        texto.scale_to_fit_width(float(ancho) * 0.86)
    texto.move_to(caja.get_center())
    bloque = VGroup(caja, texto)
    bloque.caja = caja
    bloque.texto = texto
    return bloque


def distribucion_siguiente(opciones, probs, ancho_max=4.6, color=COLOR_PROB,
                           font_size=19, resaltar=None):
    """Barras HORIZONTALES 'palabra | barra | porcentaje', de mayor a menor.

    Las barras son proporcionales a la probabilidad (la mayor mide
    `ancho_max`) y las palabras quedan alineadas a la derecha en una columna
    propia, asi que todas las barras arrancan en la misma x. `resaltar` es la
    opcion elegida: se pinta en `color` y el resto queda en `COLOR_TENUE`.

    Expone `.filas` {opcion: VGroup(palabra, barra, porcentaje)} y `.orden`
    (las opciones ya ordenadas), para poder animar la elegida por separado.
    """
    opciones = [str(o) for o in list(opciones)[:PALABRAS_MAX]]
    probs = np.asarray(probs, dtype=np.float64).ravel()[:len(opciones)]
    grupo = VGroup()
    grupo.filas, grupo.orden = {}, []
    if probs.size == 0:
        return grupo

    orden = sorted(range(probs.size), key=lambda i: -float(probs[i]))
    pico = float(np.max(np.abs(probs)))
    pico = pico if pico > _EPS else 1.0
    resalte = _normalizar(resaltar) if resaltar is not None else None

    alto_barra = max(0.18, float(font_size) * 0.0135)
    paso = alto_barra + 0.30

    palabras = []
    for i in orden:
        activa = resalte is None or _normalizar(opciones[i]) == resalte
        palabras.append(Text(opciones[i], font_size=font_size,
                             color=color if activa else COLOR_TENUE))
    x_texto = max(float(t.width) for t in palabras)

    for fila, i in enumerate(orden):
        activa = resalte is None or _normalizar(opciones[i]) == resalte
        tono = color if activa else COLOR_TENUE
        y = -paso * fila
        texto = palabras[fila]
        texto.move_to(np.array([x_texto - texto.width / 2.0, y, 0.0]))

        largo = max(0.05, float(ancho_max) * float(probs[i]) / pico)
        barra = Rectangle(width=largo, height=alto_barra, color=tono,
                          fill_color=tono, fill_opacity=0.9 if activa else 0.5,
                          stroke_width=1.0)
        barra.move_to(np.array([x_texto + 0.22 + largo / 2.0, y, 0.0]))

        pct = Text(f"{float(probs[i]) * 100:.0f}%",
                   font_size=max(10, int(font_size * 0.78)),
                   color=tono if activa else COLOR_TENUE)
        pct.move_to(np.array([x_texto + 0.36 + largo + pct.width / 2.0,
                              y, 0.0]))

        linea = VGroup(texto, barra, pct)
        grupo.add(linea)
        grupo.filas[opciones[i]] = linea
        grupo.orden.append(opciones[i])

    grupo.move_to(ORIGIN)
    return grupo


# Se reexporta para que los clips puedan pintar texto de marca sin importar
# code_brand aparte (el titulo va en CODE_INK, no en la paleta del curso).
COLOR_TEXTO = CODE_INK

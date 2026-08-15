"""Teoria de la informacion: sorpresa, entropia, Huffman, ruido y el techo.

Pensado para el curso "Teoria de la informacion: los bits de Shannon". Todo
el calculo es python/numpy puro y determinista (el unico azar va con
`np.random.default_rng(semilla)`): mismo script -> mismo render, condicion
necesaria para `--disable_caching`. Nada de red, nada de disco.

La regla de color del curso, que es tambien la de esta libreria: el BIT (la
informacion, la sorpresa, lo que se mide) es ambar; la FUENTE (los
simbolos, las probabilidades, el mensaje) cian; los CODIGOS (compresion,
correccion, lo que funciona) verde; el RUIDO (los bits volteados, la
perdida, el error) rojo; y la ENTROPIA, la capacidad y el techo de Shannon
violeta. Mobiliario en `COLOR_EJE`.

Piezas:
    icono_fuente            moneda / dado / baraja; `.tag`, `.n`
    curva_sorpresa          -log2 p; `.en(p)`
    arbol_preguntas         arbol binario de si/no; `.camino(bits)`
    histograma_simbolos     27 barras; `.linea_uniforme()`
    curva_entropia_binaria  h(p); `.en(p)`
    arbol_huffman           el arbol construido; `.paso(k)`, `.codigo(sim)`
    tira_codigo             el mensaje por segmentos; `.segmento(i)`
    imagen_gris             rejilla 0..255; `.con_matriz(m)`
    imagen_bits             rejilla 0/1; `.con_matriz(m)`
    esquema_bsc             el canal binario simetrico y sus 4 flechas
    tira_bits               celdas 0/1; `.marcar_distintos()` CUENTA
    curva_capacidad_bsc     1 - h(p); `.en(p)`
    curva_shannon_hartley   B log2(1+S/N); `.con_ancho(b_hz)`
    plano_shannon           SNR vs eficiencia; `.prohibido`, `.marca(...)`
    venn_hamming            los 7 bits en tres circulos; `.colorear_paridad()`
    caja_numero             caja rotulada con un numero; `.actualizar(v)`
    linea_tiempo            hitos con anio y texto; `.hito(k)`
    flujo                   cajas encadenadas con flechas

Los NUMEROS que se rotulan salen de funciones (`sorpresa`, `entropia`,
`entropia_texto`, `redundancia`, `huffman`, `longitud_media`, `bits_rle`,
`simular_bsc`, `capacidad_bsc`, `capacidad_shannon`, `eficiencia_espectral`,
`snr_para_eficiencia`, `hamming_sindrome`, `simular_codigos`, `ber_bpsk`),
nunca a mano. La entropia del espanol, los bits del RLE, los volteos del
canal y las BER de los codigos se MIDEN contando o simulando.

Topes duros para no castigar el VPS: `BITS_MAX`, `PIXELES_MAX`,
`SIMBOLOS_MAX`, `BLOQUES_MAX`, `PROFUNDIDAD_MAX` levantan ValueError.

Uso:
    import sys
    sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from informacion import curva_sorpresa, TEXTO_ES, entropia_texto

    curva = curva_sorpresa()
    self.add(curva, Dot(curva.en(0.5), color=C_BIT))
"""

import math

import numpy as np

from manim import (Arrow, Circle, DashedLine, Dot, Line, Polygon, Rectangle,
                   RoundedRectangle, Square, Text, VGroup, VMobject, DOWN,
                   LEFT, ORIGIN, RIGHT, UP)

from code_brand import CODE_BG, CODE_MUTED, FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
BITS_MAX = 512         # bits dibujados en una tira
PIXELES_MAX = 4096     # pixeles de una imagen (24x16 = 384)
SIMBOLOS_MAX = 64      # simbolos de una fuente / hojas de un Huffman
BLOQUES_MAX = 20000    # bloques de una simulacion de codigos
PROFUNDIDAD_MAX = 6    # niveles del arbol de preguntas (2^6 = 64 hojas)

# Paleta propia de la libreria (coincide con la del curso).
COLOR_BIT = "#f59e0b"      # ambar: el bit, la informacion, la sorpresa
COLOR_FUENTE = "#22d3ee"   # cian: la fuente, los simbolos, el mensaje
COLOR_CODIGO = "#34d399"   # verde: codigos, compresion, correccion
COLOR_RUIDO = "#f43f5e"    # rojo: ruido, bits volteados, perdida, error
COLOR_LIMITE = "#a78bfa"   # violeta: entropia, capacidad, techo de Shannon
COLOR_EJE = "#31414f"      # mobiliario

C_BIT, C_FUENTE, C_CODIGO = COLOR_BIT, COLOR_FUENTE, COLOR_CODIGO
C_RUIDO, C_LIMITE, C_EJE = COLOR_RUIDO, COLOR_LIMITE, COLOR_EJE

# --- Los datos del curso ---------------------------------------------
ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ESPACIO = " "
SIMBOLOS = ALFABETO + ESPACIO          # 27 simbolos: 26 letras + el espacio

TEXTO_ES = (
    "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha "
    "mucho tiempo que vivia un hidalgo de los de lanza en astillero, adarga "
    "antigua, rocin flaco y galgo corredor. Una olla de algo mas vaca que "
    "carnero, salpicon las mas noches, duelos y quebrantos los sabados, "
    "lentejas los viernes, algun palomino de anadidura los domingos, "
    "consumian las tres partes de su hacienda. El resto della concluian sayo "
    "de velarte, calzas de velludo para las fiestas, con sus pantuflos de lo "
    "mesmo, y los dias de entresemana se honraba con su vellori de lo mas "
    "fino. Tenia en su casa una ama que pasaba de los cuarenta, y una "
    "sobrina que no llegaba a los veinte, y un mozo de campo y plaza, que "
    "asi ensillaba el rocin como tomaba la podadera.")
"""Texto de muestra del curso: Miguel de Cervantes, "El ingenioso hidalgo
don Quijote de la Mancha", primera parte, CAPITULO I (1605) — la apertura
del libro, DOMINIO PUBLICO. Transcrito sin tildes (el modulo normaliza a
los 27 simbolos ASCII: 26 letras + espacio; la enie pasa a N).

Las frecuencias del curso son las MEDIDAS en este texto, no las de una
tabla: `frecuencias(TEXTO_ES)` y `entropia_texto(TEXTO_ES)`. Es una
entropia de ORDEN 0 (simbolos independientes), que es exactamente lo que
el curso dice medir."""

MENSAJE_HUFFMAN = "ABRACADABRA"
FRASE_REDUNDANTE = "LA INFORMACION SE MIDE"
P_MONEDA_TRUCADA = 0.9
N_PREGUNTAS = 20
REDUNDANCIA_SHANNON_1951 = 0.75    # cita: Shannon 1951, ingles, con contexto
P_BSC = 0.1
N_BITS_CANAL = 64
SEMILLA_CANAL = 3
B_TRANSPONDEDOR_HZ = 36e6          # ancho clasico de un transpondedor Ku
CN_DB_1, CN_DB_2 = 10, 20
DATOS_HAMMING = [1, 0, 1, 1]
POS_ERROR_HAMMING = 5              # 1-based
P_CODIGOS = 0.05
N_BLOQUES = 4000
SEMILLA_CODIGOS = 11
TASA_REP3 = 1 / 3
TASA_HAMMING = 4 / 7
NIVELES_JPG = 4
ANCHO_IMG, ALTO_IMG = 24, 16

MODCODS_DVBS2 = [
    ("QPSK 1/2", 0.989, 1.00),
    ("8PSK 3/4", 2.228, 7.91),
    ("16APSK 3/4", 2.967, 10.21),
    ("32APSK 9/10", 4.453, 16.05),
]
"""(nombre, eficiencia b/s/Hz, Es/N0 ideal en dB) — ETSI EN 302 307-1,
tabla 13. Son valores PUBLICADOS de la norma: se rotulan como cita. La
distancia al techo se CALCULA con `snr_para_eficiencia`."""

HITOS = [
    (1948, "Shannon: el teorema"),
    (1950, "Hamming"),
    (1993, "turbo codigos"),
    (2003, "LDPC en DVB-S2"),
    (2018, "LDPC y polares en 5G"),
]

VOCALES = "AEIOU"

_EPS = 1e-12

# Tildes y diereses del espanol -> ASCII; la enie se vuelve N.
_ACENTOS = {"Á": "A", "À": "A", "Ä": "A", "Â": "A",
            "É": "E", "È": "E", "Ë": "E", "Ê": "E",
            "Í": "I", "Ì": "I", "Ï": "I", "Î": "I",
            "Ó": "O", "Ò": "O", "Ö": "O", "Ô": "O",
            "Ú": "U", "Ù": "U", "Ü": "U", "Û": "U",
            "Ñ": "N", "Ç": "C"}


# --- utilidades internas ----------------------------------------------
def _validar(nombre, valor, tope):
    valor = int(valor)
    if valor < 1 or valor > tope:
        raise ValueError(f"{nombre}: {valor} fuera de rango (1..{tope})")
    return valor


def _texto_hud(texto, font_size=15, color=CODE_MUTED):
    """Texto de telemetria: Space Mono, ASCII puro (sin tildes ni signos
    raros: la fuente HUD no los tiene). Para exponentes, MathTex."""
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


def _poligonal(puntos, color, grosor=2.0):
    pts = np.asarray(puntos, dtype=np.float64)
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    linea = VMobject(color=color, stroke_width=grosor)
    linea.set_points_as_corners(pts)
    return linea


def _ancla(punto=ORIGIN):
    """Dot invisible que viaja con la pieza: localizador inmune a move_to."""
    p = np.asarray(punto, dtype=np.float64)
    if p.shape == (2,):
        p = np.append(p, 0.0)
    return Dot(p, radius=0.001, fill_opacity=0.0, stroke_opacity=0.0)


class _Alineable(VGroup):
    """Pieza con dos anclas invisibles (izquierda y derecha) que permiten
    fabricar una GEMELA ya escalada y colocada donde esta la original —
    justo lo que necesita `Transform` cuando la pieza fue movida o
    escalada por el clip."""

    def _escala_actual(self):
        d = float(np.linalg.norm(self._ancla_b.get_center()
                                 - self._ancla_a.get_center()))
        return d / max(self._largo_ref, _EPS)

    def _alinear(self, otra):
        otra.scale(self._escala_actual())
        otra.shift(self._ancla_a.get_center() - otra._ancla_a.get_center())
        return otra


# =====================================================================
# Nucleo: la sorpresa y la entropia
# =====================================================================
def sorpresa(p):
    """La sorpresa de un suceso de probabilidad p, en BITS: -log2 p.

    Es la definicion de "un bit": la sorpresa de una moneda justa
    (`sorpresa(0.5)` = 1). Lo seguro no informa (`sorpresa(1)` = 0) y lo
    improbable informa mucho (`sorpresa(1/52)` = 5.70).
    """
    p = float(p)
    if not 0.0 < p <= 1.0:
        raise ValueError(f"sorpresa: p={p} fuera de (0, 1]")
    return -math.log2(p)


def bits_para(n):
    """Bits para distinguir n posibilidades EQUIPROBABLES: log2 n.

    Un dado da `bits_para(6)` = 2.585, una carta `bits_para(52)` = 5.700.
    No tiene por que ser entero: es una media, no un contador de casillas.
    """
    n = float(n)
    if n <= 0.0:
        raise ValueError(f"bits_para: n={n} no es positivo")
    return math.log2(n)


def preguntas_para(n):
    """Preguntas de si/no que hacen falta para n objetos: ceil(log2 n).

    Exacto en enteros (sin pasar por floats): `preguntas_para(2**20)` = 20,
    `preguntas_para(1000)` = 10.
    """
    if float(n) <= 0.0:
        raise ValueError(f"preguntas_para: n={n} no es positivo")
    if float(n) == int(n):
        return int(max(int(n) - 1, 0).bit_length())
    return int(math.ceil(math.log2(float(n))))


def entropia(probs):
    """Entropia de Shannon en bits: H = -sum p log2 p.

    Acepta dict (simbolo -> peso), lista o np.array; IGNORA los ceros (el
    limite de p log2 p en 0 es 0) y normaliza por la suma, asi que tambien
    admite cuentas en vez de fracciones. `entropia([0.25]*4)` = 2.
    """
    if isinstance(probs, dict):
        valores = [float(v) for v in probs.values()]
    else:
        valores = [float(v) for v in np.asarray(probs, dtype=float).ravel()]
    if any(v < 0.0 for v in valores):
        raise ValueError("entropia: hay pesos negativos")
    total = float(sum(valores))
    if total <= 0.0:
        raise ValueError("entropia: la distribucion suma 0")
    h = 0.0
    for v in valores:
        q = v / total
        if q > 0.0:
            h -= q * math.log2(q)
    return h


def entropia_binaria(p):
    """h(p) = -p log2 p - (1-p) log2(1-p), con h(0) = h(1) = 0.

    Es la entropia de una moneda de sesgo p: maxima (1 bit) en p = 0.5,
    0.469 en p = 0.9 y 0 en los extremos — una moneda que siempre sale
    cara no dice nada.
    """
    p = float(p)
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"entropia_binaria: p={p} fuera de [0, 1]")
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)


# =====================================================================
# Nucleo: la fuente de texto
# =====================================================================
def normalizar(texto):
    """Texto -> los 27 `SIMBOLOS`: 26 letras MAYUSCULAS y el espacio.

    Quita tildes (A con acento -> A), la enie pasa a N y todo lo demas
    (comas, puntos, digitos) se DESCARTA sin dejar hueco; los espacios
    multiples se colapsan en uno y los de los extremos se recortan. Asi
    "Mancha, de" da "MANCHA DE" (un solo espacio).
    """
    salida = []
    for ch in str(texto).upper():
        ch = _ACENTOS.get(ch, ch)
        if ch in ALFABETO:
            salida.append(ch)
        elif ch.isspace():
            if salida and salida[-1] != ESPACIO:
                salida.append(ESPACIO)
    while salida and salida[-1] == ESPACIO:
        salida.pop()
    return "".join(salida)


def frecuencias(texto):
    """Fraccion de cada simbolo en el texto: dict con las 27 claves (las
    que no aparecen valen 0.0) y suma 1.0.

    A diferencia de `cripto.frecuencias`, el ESPACIO cuenta como simbolo:
    es el mas frecuente del espanol y sin el la entropia por simbolo no
    seria la de la fuente que se dibuja.
    """
    limpio = normalizar(texto)
    if not limpio:
        raise ValueError("frecuencias: el texto no tiene simbolos")
    cuenta = {s: 0 for s in SIMBOLOS}
    for c in limpio:
        cuenta[c] += 1
    total = float(len(limpio))
    return {s: cuenta[s] / total for s in SIMBOLOS}


def entropia_texto(texto):
    """Entropia de ORDEN 0 del texto, en bits por simbolo: MEDIDA sobre
    sus propias frecuencias. Para `TEXTO_ES` sale ~4.1, frente a los
    log2 27 = 4.75 de una fuente uniforme de 27 simbolos."""
    return entropia(frecuencias(texto))


def redundancia(h, n_simbolos):
    """Redundancia de la fuente: 1 - H / log2 n.

    Cuanto del maximo teorico se esta desperdiciando por lo predecible
    que es el idioma. Con H_ES ~4.1 y 27 simbolos da ~13 % — y eso solo
    contando frecuencias, sin mirar el contexto.
    """
    return 1.0 - float(h) / bits_para(n_simbolos)


def sin_vocales(texto):
    """El texto normalizado sin A, E, I, O, U (los espacios se
    conservan). "LA INFORMACION SE MIDE" -> "L NFRMCN S MD": se sigue
    leyendo, que es la definicion practica de redundancia."""
    return "".join(c for c in normalizar(texto) if c not in VOCALES)


# =====================================================================
# Nucleo: Huffman
# =====================================================================
def _clave_huffman(nodo):
    """Orden determinista de la cola: por peso y, en EMPATE, por orden
    alfabetico de la etiqueta. El peso se redondea a 1e-12 para que dos
    sumas de fracciones que valen lo mismo empaten de verdad."""
    return (round(nodo["peso"], 12), nodo["etiqueta"])


def _arbol_huffman_nucleo(frecs):
    """Construye el arbol y devuelve (hojas, fusiones, raiz).

    Determinista: en cada paso se funden los DOS pesos menores (empate
    por orden alfabetico) y el hijo de MENOR peso recibe el bit "0". Las
    etiquetas de los nodos internos son la concatenacion ORDENADA de sus
    simbolos ("CD", "BCD", ...).
    """
    if isinstance(frecs, dict):
        items = [(float(f), str(s)) for s, f in frecs.items() if float(f) > 0]
    else:
        raise ValueError("huffman: se espera un dict simbolo -> peso")
    if not items:
        raise ValueError("huffman: no hay simbolos con peso positivo")
    _validar("huffman.simbolos", len(items), SIMBOLOS_MAX)
    total = float(sum(f for f, _ in items))
    if total <= 0.0:
        raise ValueError("huffman: los pesos suman 0")

    hojas = {}
    vivos = []
    for f, s in items:
        nodo = {"peso": f / total, "etiqueta": s, "hijos": None,
                "padre": None, "idx": None}
        hojas[s] = nodo
        vivos.append(nodo)

    fusiones = []
    while len(vivos) > 1:
        vivos.sort(key=_clave_huffman)
        a, b = vivos.pop(0), vivos.pop(0)
        nodo = {"peso": a["peso"] + b["peso"],
                "etiqueta": "".join(sorted(a["etiqueta"] + b["etiqueta"])),
                "hijos": (a, b), "padre": None, "idx": len(fusiones)}
        a["padre"] = (nodo["idx"], 0)
        b["padre"] = (nodo["idx"], 1)
        fusiones.append(nodo)
        vivos.append(nodo)
    return hojas, fusiones, vivos[0]


def huffman(frecs):
    """Codigo de Huffman: dict simbolo -> str de "0"/"1".

    Solo reciben codigo los simbolos con frecuencia POSITIVA (un dict de
    27 claves con ceros devuelve menos de 27 codigos). Es prefijo y
    optimo simbolo a simbolo; su longitud media nunca baja de la
    entropia. Con "ABRACADABRA": A=0, R=10, B=110, C=1110, D=1111.
    """
    hojas, _fusiones, raiz = _arbol_huffman_nucleo(frecs)
    codigos = {}

    def caminar(nodo, prefijo):
        if nodo["hijos"] is None:
            codigos[nodo["etiqueta"]] = prefijo if prefijo else "0"
            return
        izq, der = nodo["hijos"]
        caminar(izq, prefijo + "0")
        caminar(der, prefijo + "1")

    caminar(raiz, "")
    return {s: codigos[s] for s in sorted(hojas)}


def pasos_huffman(frecs):
    """Las fusiones en orden: lista de (izq, der, peso).

    `izq` es el hijo que recibe el "0" (el de menor peso) y `der` el del
    "1"; las etiquetas son el simbolo o la concatenacion ordenada de los
    simbolos del subarbol. Para n simbolos hay n-1 fusiones — con esto se
    anima la construccion del arbol fusion a fusion.
    """
    _hojas, fusiones, _raiz = _arbol_huffman_nucleo(frecs)
    return [(n["hijos"][0]["etiqueta"], n["hijos"][1]["etiqueta"], n["peso"])
            for n in fusiones]


def longitud_media(codigo, frecs):
    """Bits por simbolo que gasta ese codigo: sum f(s) len(codigo[s]).

    Se normaliza sobre los simbolos que TIENEN codigo, asi que sirve
    igual con un dict de 27 claves lleno de ceros.
    """
    pesos = [float(frecs[s]) for s in codigo if s in frecs]
    total = float(sum(pesos))
    if total <= 0.0:
        raise ValueError("longitud_media: los simbolos del codigo pesan 0")
    return sum(float(frecs[s]) / total * len(codigo[s])
               for s in codigo if s in frecs)


def codificar(texto, codigo):
    """El texto normalizado como cadena de "0"/"1" concatenando codigos."""
    limpio = normalizar(texto)
    faltan = sorted({c for c in limpio if c not in codigo})
    if faltan:
        raise ValueError(f"codificar: sin codigo para {faltan}")
    return "".join(codigo[c] for c in limpio)


def bits_codificados(texto, codigo):
    """Bits que ocupa el texto con ese codigo. "ABRACADABRA" con Huffman:
    23 bits, frente a los 33 de 3 bits fijos."""
    return len(codificar(texto, codigo))


def bits_fijos(n_simbolos):
    """Bits por simbolo de un codigo de longitud FIJA: ceil(log2 n).
    5 simbolos -> 3 bits; 27 -> 5 bits (y ASCII gasta 8)."""
    return preguntas_para(n_simbolos)


# =====================================================================
# Nucleo: imagenes, cuantizacion y RLE
# =====================================================================
_LUZ = np.array([-0.35, -0.35, 0.868])   # desde arriba-izquierda, casi frontal
_LIMBO = 1.2                             # oscurecimiento del borde (z^_LIMBO)


def imagen_esfera(ancho=ANCHO_IMG, alto=ALTO_IMG):
    """Una esfera iluminada desde arriba-izquierda: np.array uint8
    (0..255) de forma (alto, ancho) — FILAS x COLUMNAS.

    El fondo es 0 exacto. El brillo es el coseno del angulo con la luz
    por el escorzo del borde (z), asi que el centro pasa de 180 y el
    limbo se apaga: se ve una bola, no un disco plano.
    """
    ancho = _validar("imagen_esfera.ancho", ancho, 256)
    alto = _validar("imagen_esfera.alto", alto, 256)
    _validar("imagen_esfera.pixeles", ancho * alto, PIXELES_MAX)

    cx, cy = (ancho - 1) / 2.0, (alto - 1) / 2.0
    radio = 0.42 * min(ancho, alto)
    xs = (np.arange(ancho) - cx) / radio
    ys = (np.arange(alto) - cy) / radio
    dx, dy = np.meshgrid(xs, ys)
    d2 = dx * dx + dy * dy
    dentro = d2 <= 1.0
    z = np.sqrt(np.clip(1.0 - d2, 0.0, 1.0))
    ndotl = dx * _LUZ[0] + dy * _LUZ[1] + z * _LUZ[2]
    valor = np.clip(ndotl, 0.0, 1.0) * z ** _LIMBO
    valor = np.where(dentro, valor, 0.0)
    return np.rint(255.0 * valor).astype(np.uint8)


def cuantizar(imagen, niveles=NIVELES_JPG):
    """La imagen con solo `niveles` valores distintos (cuantizacion
    uniforme, representantes repartidos por igual entre 0 y 255).

    Es "el principio de un jpg": tirar precision que el ojo no echa de
    menos. No es la DCT — se rotula como principio, no como formato.
    """
    niveles = int(niveles)
    if niveles < 2 or niveles > 256:
        raise ValueError(f"cuantizar: niveles={niveles} fuera de 2..256")
    img = np.asarray(imagen, dtype=float)
    q = np.clip(np.floor(img / 256.0 * niveles), 0, niveles - 1)
    return np.rint(q * (255.0 / (niveles - 1))).astype(np.uint8)


def bits_imagen(imagen, bits_por_pixel):
    """Bits crudos de la imagen: ancho x alto x bits_por_pixel.
    24x16 a 8 bits son 3072; a 2 bits, 768 (la cuarta parte)."""
    img = np.asarray(imagen)
    b = int(bits_por_pixel)
    if b < 1:
        raise ValueError(f"bits_imagen: bits_por_pixel={b} < 1")
    return int(img.size * b)


def icono_bits(ancho=ANCHO_IMG, alto=ALTO_IMG):
    """Un planeta con anillo en 0/1: np.array de forma (alto, ancho).

    El disco es un circulo y el anillo una elipse fina que lo cruza por
    el ecuador y se sale por los lados. Esta dibujado a proposito con
    TRAMOS LARGOS (el anillo va en las mismas filas que el ecuador, asi
    que no parte ninguna fila en tres): por eso `bits_rle` baja de la
    mitad de los bits crudos, que es lo que el clip quiere mostrar.
    """
    ancho = _validar("icono_bits.ancho", ancho, 256)
    alto = _validar("icono_bits.alto", alto, 256)
    _validar("icono_bits.pixeles", ancho * alto, PIXELES_MAX)

    cx, cy = (ancho - 1) / 2.0, (alto - 1) / 2.0
    xs = np.arange(ancho) - cx
    ys = np.arange(alto) - cy
    dx, dy = np.meshgrid(xs, ys)

    r_planeta = 0.375 * min(ancho, alto)
    planeta = (dx * dx + dy * dy) <= r_planeta * r_planeta

    a_anillo = 0.46 * ancho
    b_anillo = 0.081 * alto
    anillo = ((dx / a_anillo) ** 2 + (dy / b_anillo) ** 2) <= 1.0

    return (planeta | anillo).astype(int)


def rle(bits_1d):
    """Codificacion por tramos: lista de (valor, largo) en orden.

    Reconstruye el original exactamente (es SIN perdida: "el principio de
    un zip"). Sobre el icono binario, los tramos largos de fondo son
    justo la redundancia que el compresor se lleva.
    """
    b = np.asarray(bits_1d, dtype=int).ravel()
    _validar("rle.bits", b.size, PIXELES_MAX)
    tramos = []
    actual, largo = int(b[0]), 1
    for v in b[1:]:
        v = int(v)
        if v == actual:
            largo += 1
        else:
            tramos.append((actual, largo))
            actual, largo = v, 1
    tramos.append((actual, largo))
    return tramos


def bits_rle(bits):
    """Bits que ocupa la version por tramos, con el criterio HONESTO:

        n_tramos * (1 + ceil(log2(largo_max + 1)))

    es decir, un bit para el valor y los que hagan falta para escribir el
    largo mas largo (campo de ancho fijo, sin trampas de entropia). Para
    el icono 24x16 baja de 384 a menos de la mitad.
    """
    tramos = rle(bits)
    largo_max = max(l for _v, l in tramos)
    return int(len(tramos) * (1 + int(largo_max).bit_length()))


# =====================================================================
# Nucleo: el canal con ruido
# =====================================================================
def simular_bsc(bits, p=P_BSC, semilla=SEMILLA_CANAL):
    """Pasa los bits por un canal binario simetrico de probabilidad p.

    Devuelve `(recibidos, n_volteados)`: el array de la MISMA longitud y
    cuantos bits cambiaron, CONTADOS (no estimados). El azar va con
    `default_rng(semilla)`: mismo render siempre.
    """
    b = np.asarray(bits, dtype=int).ravel()
    if b.size == 0:
        raise ValueError("simular_bsc: no hay bits")
    p = float(p)
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"simular_bsc: p={p} fuera de [0, 1]")
    rng = np.random.default_rng(int(semilla))
    volteos = rng.random(b.size) < p
    recibidos = np.where(volteos, 1 - b, b).astype(int)
    return recibidos, int(np.count_nonzero(recibidos != b))


def capacidad_bsc(p):
    """Capacidad del BSC con entrada uniforme: C = 1 - h(p) bits por uso.

    p=0 -> 1 bit; p=0.1 -> 0.531; p=0.5 -> 0 (el canal es puro azar y no
    dice nada). Es un techo: hasta ahi se puede transmitir con tan pocos
    errores como se quiera, codificando.
    """
    return 1.0 - entropia_binaria(p)


def informacion_mutua_bsc(p):
    """Alias de `capacidad_bsc`: con entrada uniforme, la informacion
    mutua I(X;Y) del BSC ES su capacidad."""
    return capacidad_bsc(p)


# =====================================================================
# Nucleo: dB, Shannon-Hartley y el limite
# =====================================================================
def db_a_lineal(db):
    """dB -> razon lineal: 10^(dB/10). 10 dB = 10, 20 dB = 100."""
    return 10.0 ** (float(db) / 10.0)


def lineal_a_db(x):
    """Razon lineal -> dB: 10 log10 x. 100 = 20 dB."""
    x = float(x)
    if x <= 0.0:
        raise ValueError(f"lineal_a_db: x={x} no es positivo")
    return 10.0 * math.log10(x)


def capacidad_shannon(b_hz, snr_lineal):
    """Shannon-Hartley: C = B log2(1 + S/N), en bit/s.

    Con B = 36 MHz (transpondedor Ku) y C/N = 10 dB salen 124.5 Mb/s; con
    20 dB, 239.7: diez veces la potencia y ni el doble de capacidad. Es
    un TECHO teorico, no lo que da un modem real.
    """
    b = float(b_hz)
    snr = float(snr_lineal)
    if b < 0.0:
        raise ValueError(f"capacidad_shannon: B={b} < 0")
    if snr < 0.0:
        raise ValueError(f"capacidad_shannon: SNR={snr} < 0")
    return b * math.log2(1.0 + snr)


def eficiencia_espectral(snr_db):
    """Eficiencia espectral maxima en b/s/Hz: log2(1 + SNR).
    10 dB -> 3.459; 13 dB -> 4.389 (+3 dB suma ~1 bit/s/Hz)."""
    return math.log2(1.0 + db_a_lineal(snr_db))


def snr_para_eficiencia(eta):
    """El SNR (dB) que hace falta para esa eficiencia: 10 log10(2^eta - 1).

    Es la inversa de `eficiencia_espectral`, y con ella se MIDE la
    distancia al techo de un MODCOD real (su Es/N0 publicado menos este).
    """
    eta = float(eta)
    if eta <= 0.0:
        raise ValueError(f"snr_para_eficiencia: eta={eta} no es positiva")
    return lineal_a_db(2.0 ** eta - 1.0)


def ebn0_minimo_db():
    """El limite de Shannon con ancho de banda INFINITO:
    Eb/N0 = 10 log10(ln 2) = -1.5917 dB. Por debajo de ahi no hay codigo
    que valga, ni ahora ni nunca."""
    return 10.0 * math.log10(math.log(2.0))


def cn0_desde_cn(cn_db, b_hz):
    """Puente con "Cerrar el enlace": C/N0 = C/N + 10 log10 B, en dBHz.
    10 dB en 36 MHz son 85.56 dBHz."""
    return float(cn_db) + lineal_a_db(b_hz)


def ber_bpsk(ebn0_db):
    """BER de BPSK sin codificar: Q(sqrt(2 Eb/N0)) = 0.5 erfc(sqrt(Eb/N0)).
    0 dB -> 0.079; 4 dB -> 0.0125; 8 dB -> 1.9e-4."""
    return 0.5 * math.erfc(math.sqrt(db_a_lineal(ebn0_db)))


# =====================================================================
# Nucleo: Hamming(7,4) y la repeticion
# =====================================================================
# Regiones del Venn: posicion (1-based) -> circulos que la contienen.
REGIONES_HAMMING = {1: "A", 2: "B", 3: "AB", 4: "C", 5: "AC", 6: "BC",
                    7: "ABC"}
_CIRCULOS_HAMMING = {"A": (1, 3, 5, 7), "B": (2, 3, 6, 7), "C": (4, 5, 6, 7)}
POSICIONES_DATOS = (3, 5, 6, 7)      # d1 d2 d3 d4, 1-based
POSICIONES_PARIDAD = (1, 2, 4)       # p1 p2 p3, 1-based


def _palabra7(palabra):
    w = [int(x) & 1 for x in np.asarray(palabra, dtype=int).ravel()]
    if len(w) != 7:
        raise ValueError(f"Hamming: la palabra tiene {len(w)} bits, no 7")
    return w


def hamming_codificar(datos4):
    """4 bits de datos -> 7 bits, en el orden ESTANDAR p1 p2 d1 p3 d2 d3 d4.

    p1 = d1^d2^d4, p2 = d1^d3^d4, p3 = d2^d3^d4: cada paridad cubre un
    circulo del Venn y por eso el sindrome sale igual a la POSICION del
    bit volteado. [1,0,1,1] -> [0,1,1,0,0,1,1].
    """
    d = [int(x) & 1 for x in np.asarray(datos4, dtype=int).ravel()]
    if len(d) != 4:
        raise ValueError(f"hamming_codificar: {len(d)} datos, no 4")
    d1, d2, d3, d4 = d
    return [d1 ^ d2 ^ d4, d1 ^ d3 ^ d4, d1, d2 ^ d3 ^ d4, d2, d3, d4]


def hamming_sindrome(palabra7):
    """Sindrome 0..7: 0 si la palabra es valida, y si no la POSICION
    (1-based) del bit volteado. Ese es todo el truco de 1950."""
    w = _palabra7(palabra7)
    a = w[0] ^ w[2] ^ w[4] ^ w[6]          # circulo A: 1,3,5,7
    b = w[1] ^ w[2] ^ w[5] ^ w[6]          # circulo B: 2,3,6,7
    c = w[3] ^ w[4] ^ w[5] ^ w[6]          # circulo C: 4,5,6,7
    return int(a + 2 * b + 4 * c)


def paridades(palabra7):
    """(A, B, C): True si ese circulo del Venn tiene un numero PAR de unos.

    En una palabra correcta los tres son True. Con el bit 5 volteado (que
    esta en A y en C) quedan (False, True, False): la interseccion de los
    dos circulos impares delata la posicion.
    """
    w = _palabra7(palabra7)
    return tuple(sum(w[i - 1] for i in _CIRCULOS_HAMMING[k]) % 2 == 0
                 for k in ("A", "B", "C"))


def voltear(bits, pos_1based):
    """Voltea el bit en esa posicion (1-based) y devuelve una COPIA del
    mismo tipo que la entrada (lista o np.array)."""
    i = int(pos_1based) - 1
    es_array = isinstance(bits, np.ndarray)
    w = [int(x) for x in np.asarray(bits, dtype=int).ravel()]
    if not 0 <= i < len(w):
        raise ValueError(f"voltear: posicion {pos_1based} fuera de "
                         f"1..{len(w)}")
    w[i] = 1 - w[i]
    return np.array(w, dtype=int) if es_array else w


def hamming_corregir(palabra7):
    """Devuelve (corregida, pos): la palabra con su unico error arreglado
    y la posicion 1-based (0 si no habia error).

    Corrige UN error por bloque; con dos, "corrige" mal y mete un tercero
    — se dice en el clip.
    """
    w = _palabra7(palabra7)
    pos = hamming_sindrome(w)
    if pos:
        w = voltear(w, pos)
    return w, int(pos)


def hamming_decodificar(palabra7):
    """Corrige y devuelve los 4 datos (posiciones 3, 5, 6, 7)."""
    w, _pos = hamming_corregir(palabra7)
    return [w[i - 1] for i in POSICIONES_DATOS]


def repeticion_codificar(bits, n=3):
    """Cada bit repetido n veces: [1,0] -> [1,1,1,0,0,0]. Corrige, pero
    gasta n veces mas (tasa 1/n)."""
    n = _validar("repeticion_codificar.n", n, 9)
    b = [int(x) & 1 for x in np.asarray(bits, dtype=int).ravel()]
    return [v for v in b for _ in range(n)]


def repeticion_decodificar(bits, n=3):
    """Decodifica por MAYORIA cada bloque de n bits."""
    n = _validar("repeticion_decodificar.n", n, 9)
    b = [int(x) & 1 for x in np.asarray(bits, dtype=int).ravel()]
    if len(b) % n != 0:
        raise ValueError(f"repeticion_decodificar: {len(b)} bits no son "
                         f"multiplo de {n}")
    return [1 if sum(b[i:i + n]) * 2 > n else 0
            for i in range(0, len(b), n)]


def simular_codigos(p=P_CODIGOS, n_bloques=N_BLOQUES, semilla=SEMILLA_CODIGOS):
    """BER MEDIDA de tres esquemas por el MISMO canal BSC de parametro p.

    Cada bloque son 4 bits de datos que viajan como 4 bits (sin codigo),
    12 (repeticion x3) o 7 (Hamming(7,4)); la BER se mide siempre sobre
    los 4 bits de DATOS. Devuelve {"sin", "rep3", "hamming"}.

    La comparacion es a igual p del canal, NO a igual energia por bit: la
    justa es por Eb/N0, y ahi es donde Shannon puso el techo (clip 8).
    """
    p = float(p)
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"simular_codigos: p={p} fuera de [0, 1]")
    n = _validar("simular_codigos.n_bloques", n_bloques, BLOQUES_MAX)
    rng = np.random.default_rng(int(semilla))
    datos = rng.integers(0, 2, size=(n, 4)).astype(int)

    sin = datos ^ (rng.random((n, 4)) < p).astype(int)
    ber_sin = float(np.mean(sin != datos))

    rep = np.repeat(datos, 3, axis=1)
    rep = rep ^ (rng.random(rep.shape) < p).astype(int)
    votos = (rep.reshape(n, 4, 3).sum(axis=2) >= 2).astype(int)
    ber_rep = float(np.mean(votos != datos))

    d1, d2, d3, d4 = datos[:, 0], datos[:, 1], datos[:, 2], datos[:, 3]
    pal = np.column_stack([d1 ^ d2 ^ d4, d1 ^ d3 ^ d4, d1,
                           d2 ^ d3 ^ d4, d2, d3, d4])
    rec = pal ^ (rng.random(pal.shape) < p).astype(int)
    sa = rec[:, 0] ^ rec[:, 2] ^ rec[:, 4] ^ rec[:, 6]
    sb = rec[:, 1] ^ rec[:, 2] ^ rec[:, 5] ^ rec[:, 6]
    sc = rec[:, 3] ^ rec[:, 4] ^ rec[:, 5] ^ rec[:, 6]
    sind = sa + 2 * sb + 4 * sc
    corr = rec.copy()
    hay = sind > 0
    corr[np.nonzero(hay)[0], sind[hay] - 1] ^= 1
    dec = corr[:, [2, 4, 5, 6]]
    ber_ham = float(np.mean(dec != datos))

    return {"sin": ber_sin, "rep3": ber_rep, "hamming": ber_ham}


# =====================================================================
# Las curvas (ejes propios, localizador sobre la geometria ACTUAL)
# =====================================================================
class _CurvaXY(_Alineable):
    """Base de todas las curvas: dos ejes gris, una poligonal y ticks.

    `.en(x)` y `.punto(x, y)` devuelven puntos de ESCENA calculados sobre
    la geometria actual, asi que sobreviven a `.scale()`, `.shift()` y
    `.move_to()`. Los valores fuera de rango se recortan a la caja.
    """

    def __init__(self, ancla_a, ancla_b, ejes, curva, ticks, etiqueta_x,
                 etiqueta_y, params, **kwargs):
        super().__init__(ancla_a, ancla_b, ejes, curva, ticks, etiqueta_x,
                         etiqueta_y, **kwargs)
        self._ancla_a = ancla_a             # origen de los ejes
        self._ancla_b = ancla_b             # extremo derecho del eje x
        self._largo_ref = params["ancho"]
        self.ejes = ejes
        self.curva = curva
        self.ticks = ticks
        self.etiqueta_x = etiqueta_x
        self.etiqueta_y = etiqueta_y
        self._params = params

    def punto(self, x, y):
        """Punto de escena de las coordenadas (x, y) del plano."""
        p = self._params
        esc = self._escala_actual()
        fx = min(max((float(x) - p["x0"]) / (p["x1"] - p["x0"]), 0.0), 1.0)
        fy = min(max((float(y) - p["y0"]) / (p["y1"] - p["y0"]), 0.0), 1.0)
        return (self._ancla_a.get_center() + RIGHT * fx * p["ancho"] * esc
                + UP * fy * p["alto"] * esc)

    def en(self, x):
        """Punto de escena SOBRE la curva para esa x."""
        return self.punto(x, self._params["f"](x))


def _marco_curva(ancho, alto, ticks_x, ticks_y, etiqueta_x, etiqueta_y,
                 font_size=12):
    """Ejes, ticks y etiquetas cortas. Los ticks llegan como (frac, texto)
    con frac en 0..1 sobre el eje."""
    origen = np.array([-ancho / 2.0, -alto / 2.0, 0.0])
    ejes = VGroup(
        Line(origen, origen + RIGHT * ancho, stroke_width=2.0,
             color=COLOR_EJE),
        Line(origen, origen + UP * alto, stroke_width=2.0, color=COLOR_EJE))

    ticks = VGroup()
    for frac, txt in ticks_x:
        t = _texto_hud(txt, font_size=font_size)
        t.set_opacity(0.85)
        t.next_to(origen + RIGHT * float(frac) * ancho, DOWN, buff=0.12)
        ticks.add(t)
    for frac, txt in ticks_y:
        t = _texto_hud(txt, font_size=font_size)
        t.set_opacity(0.85)
        t.next_to(origen + UP * float(frac) * alto, LEFT, buff=0.12)
        ticks.add(t)

    ex = _texto_hud(etiqueta_x, font_size=font_size)
    ex.set_opacity(0.9)
    ex.move_to(origen + RIGHT * ancho / 2.0 + DOWN * 0.52)
    ey = _texto_hud(etiqueta_y, font_size=font_size)
    ey.set_opacity(0.9)
    ey.move_to(origen + UP * (alto + 0.26) + RIGHT * ey.width / 2.0)
    return ejes, origen, ticks, ex, ey


def _anclas_curva(origen, ancho):
    return _ancla(origen), _ancla(origen + RIGHT * ancho)


def curva_sorpresa(ancho=4.6, alto=2.8, color=COLOR_BIT, muestras=200):
    """La sorpresa -log2 p contra la probabilidad: lo improbable informa.

    El eje x va de 0 a 1 y el y de 0 a 6.5 bits; la curva se dibuja desde
    p = 0.012 (por debajo se dispara al infinito), lo bastante a la
    izquierda para que quepan la carta (1/52 -> 5.70) y el dado
    (1/6 -> 2.585). `.en(p)` da el punto sobre la curva.
    """
    ancho, alto = float(ancho), float(alto)
    x0, x1, y0, y1 = 0.0, 1.0, 0.0, 6.5
    p_min = 0.012

    ticks_x = [(0.0, "0"), (0.5, "0.5"), (1.0, "1")]
    ticks_y = [(v / y1, str(v)) for v in (0, 2, 4, 6)]
    ejes, origen, ticks, ex, ey = _marco_curva(ancho, alto, ticks_x, ticks_y,
                                               "p", "bits")

    # Muestreo logaritmico: la rama de la izquierda es la interesante.
    ts = np.linspace(0.0, 1.0, int(muestras))
    ps = p_min * (1.0 / p_min) ** ts
    pts = [origen + RIGHT * ((p - x0) / (x1 - x0)) * ancho
           + UP * min(sorpresa(p) / y1, 1.0) * alto for p in ps]
    curva = _poligonal(pts, color, 3.0)

    def f(p):
        return sorpresa(min(max(float(p), p_min), 1.0))

    params = {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "ancho": ancho,
              "alto": alto, "f": f, "muestras": int(muestras)}
    a, b = _anclas_curva(origen, ancho)
    return _CurvaXY(a, b, ejes, curva, ticks, ex, ey, params)


def curva_entropia_binaria(ancho=4.2, alto=2.6, color=COLOR_LIMITE,
                           muestras=200):
    """h(p) de la moneda: 0 en los extremos, 1 bit justo en p = 0.5.

    La campana dice que la incertidumbre es maxima cuando no se sabe
    nada, y que una moneda trucada (p = 0.9) ya solo pesa 0.469 bits.
    """
    ancho, alto = float(ancho), float(alto)
    x0, x1, y0, y1 = 0.0, 1.0, 0.0, 1.0
    ticks_x = [(0.0, "0"), (0.5, "0.5"), (1.0, "1")]
    ticks_y = [(0.0, "0"), (0.5, "0.5"), (1.0, "1")]
    ejes, origen, ticks, ex, ey = _marco_curva(ancho, alto, ticks_x, ticks_y,
                                               "p", "bits")
    ps = np.linspace(0.0, 1.0, int(muestras))
    pts = [origen + RIGHT * p * ancho + UP * entropia_binaria(p) * alto
           for p in ps]
    curva = _poligonal(pts, color, 3.0)
    params = {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "ancho": ancho,
              "alto": alto, "f": entropia_binaria, "muestras": int(muestras)}
    a, b = _anclas_curva(origen, ancho)
    return _CurvaXY(a, b, ejes, curva, ticks, ex, ey, params)


def curva_capacidad_bsc(ancho=4.2, alto=2.6, color=COLOR_LIMITE,
                        muestras=200):
    """C = 1 - h(p) del canal binario simetrico, de p = 0 a p = 0.5.

    En p = 0 el canal entrega 1 bit por uso; en 0.1, 0.531; en 0.5, nada:
    el canal es puro azar. `.en(p)` da el punto sobre la curva.
    """
    ancho, alto = float(ancho), float(alto)
    x0, x1, y0, y1 = 0.0, 0.5, 0.0, 1.0
    ticks_x = [(0.0, "0"), (0.5, "0.25"), (1.0, "0.5")]
    ticks_y = [(0.0, "0"), (0.5, "0.5"), (1.0, "1")]
    ejes, origen, ticks, ex, ey = _marco_curva(ancho, alto, ticks_x, ticks_y,
                                               "p", "bits/uso")
    ps = np.linspace(x0, x1, int(muestras))
    pts = [origen + RIGHT * ((p - x0) / (x1 - x0)) * ancho
           + UP * capacidad_bsc(p) * alto for p in ps]
    curva = _poligonal(pts, color, 3.0)
    params = {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "ancho": ancho,
              "alto": alto, "f": capacidad_bsc, "muestras": int(muestras)}
    a, b = _anclas_curva(origen, ancho)
    return _CurvaXY(a, b, ejes, curva, ticks, ex, ey, params)


class CurvaShannonHartley(_CurvaXY):
    """C = B log2(1 + S/N) contra C/N en dB, con el eje y en Mb/s."""

    def con_ancho(self, b_hz, color=COLOR_CODIGO):
        """La MISMA curva para otro ancho de banda, ya colocada sobre
        estos ejes (un VMobject suelto, listo para `Create`/`Transform`).

        OJO: si el nuevo B se sale por arriba (72 MHz contra unos ejes de
        36 MHz) la curva se RECORTA al techo de los ejes y se ve pegada a
        el — no se reescala el eje y, para que las dos curvas sigan
        siendo comparables a simple vista.
        """
        p = self._params
        pts = [self.punto(db, capacidad_shannon(float(b_hz), db_a_lineal(db))
                          / 1e6)
               for db in np.linspace(p["x0"], p["x1"], p["muestras"])]
        return _poligonal(pts, color, 2.6 * self._escala_actual())


def curva_shannon_hartley(b_hz=B_TRANSPONDEDOR_HZ, db_max=25, ancho=5.0,
                          alto=2.8, color=COLOR_LIMITE, muestras=200):
    """El techo del enlace: C = B log2(1 + S/N), en Mb/s contra C/N.

    Con B = 36 MHz el eje y llega a 300 Mb/s. Diez veces la potencia (10
    -> 20 dB) no llega a doblar la capacidad: la curva es logaritmica, y
    ahi vive toda la ingenieria de un enlace.
    """
    ancho, alto = float(ancho), float(alto)
    b_hz, db_max = float(b_hz), float(db_max)
    x0, x1 = 0.0, db_max
    y_tope = capacidad_shannon(b_hz, db_a_lineal(db_max)) / 1e6
    y1 = float(math.ceil(y_tope / 50.0) * 50.0)
    y0 = 0.0

    ticks_x = [(v / db_max, str(int(v))) for v in (0, 10, 20) if v <= db_max]
    ticks_y = [(0.0, "0"), (0.5, f"{y1 / 2:.0f}"), (1.0, f"{y1:.0f}")]
    ejes, origen, ticks, ex, ey = _marco_curva(ancho, alto, ticks_x, ticks_y,
                                               "C/N (dB)", "Mb/s")

    def f(db):
        return capacidad_shannon(b_hz, db_a_lineal(db)) / 1e6

    dbs = np.linspace(x0, x1, int(muestras))
    pts = [origen + RIGHT * ((db - x0) / (x1 - x0)) * ancho
           + UP * min(f(db) / y1, 1.0) * alto for db in dbs]
    curva = _poligonal(pts, color, 3.0)

    params = {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "ancho": ancho,
              "alto": alto, "f": f, "muestras": int(muestras), "b_hz": b_hz}
    a, b = _anclas_curva(origen, ancho)
    return CurvaShannonHartley(a, b, ejes, curva, ticks, ex, ey, params)


class PlanoShannon(_CurvaXY):
    """El plano SNR (dB) vs eficiencia (b/s/Hz) con el techo de Shannon
    y la region que nadie alcanza."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prohibido = None

    def marca(self, db, eta, color=COLOR_CODIGO, radio=0.07):
        """Un MODCOD real como punto YA colocado (Dot listo para `add`).

        Si la eficiencia pedida se pasa del techo, se recorta a el: por
        encima de la curva no hay nada, y eso es lo que se dibuja.
        """
        techo = self._params["f"](db)
        p = self.punto(db, min(float(eta), techo))
        return Dot(p, radius=float(radio) * self._escala_actual(),
                   color=color)


def plano_shannon(db_min=-2, db_max=18, eta_max=5, ancho=5.6, alto=3.0,
                  color=COLOR_LIMITE, color_prohibido=COLOR_RUIDO,
                  muestras=200):
    """El techo de Shannon: eficiencia maxima log2(1 + SNR) y la region
    imposible sombreada por encima.

    Los MODCOD de DVB-S2 se marcan con `.marca(db, eta, color)` y su
    distancia al techo se CALCULA con `snr_para_eficiencia`.
    """
    ancho, alto = float(ancho), float(alto)
    x0, x1 = float(db_min), float(db_max)
    y0, y1 = 0.0, float(eta_max)

    ticks_x = [((v - x0) / (x1 - x0), str(v)) for v in (0, 6, 12, 18)
               if x0 <= v <= x1]
    ticks_y = [(v / y1, str(v)) for v in (0, 2, 4) if v <= y1]
    ejes, origen, ticks, ex, ey = _marco_curva(ancho, alto, ticks_x, ticks_y,
                                               "SNR (dB)", "b/s/Hz")

    def f(db):
        return min(eficiencia_espectral(db), y1)

    dbs = np.linspace(x0, x1, int(muestras))
    pts = [origen + RIGHT * ((db - x0) / (x1 - x0)) * ancho
           + UP * min(max(f(db) / y1, 0.0), 1.0) * alto for db in dbs]
    curva = _poligonal(pts, color, 3.0)

    borde = list(pts) + [origen + RIGHT * ancho + UP * alto,
                         origen + UP * alto]
    prohibido = Polygon(*borde, stroke_width=0, fill_color=color_prohibido,
                        fill_opacity=0.07)

    params = {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "ancho": ancho,
              "alto": alto, "f": f, "muestras": int(muestras)}
    a, b = _anclas_curva(origen, ancho)
    pieza = PlanoShannon(a, b, ejes, curva, ticks, ex, ey, params)
    pieza.prohibido = prohibido
    pieza.add_to_back(prohibido)
    return pieza


# =====================================================================
# Los iconos de fuente: moneda, dado, baraja
# =====================================================================
class IconoFuente(VGroup):
    """Una fuente de informacion con su probabilidad debajo."""

    def __init__(self, ancla, forma, tag, params, **kwargs):
        super().__init__(ancla, forma, tag, **kwargs)
        self._ancla = ancla                 # el centro de la forma
        self.forma = forma
        self.tag = tag                      # el texto HUD de la probabilidad
        self._params = params
        self.n = params["n"]                # 2, 6 o 52 resultados
        self.nombre = params["nombre"]

    def centro(self):
        return self._ancla.get_center()


def icono_fuente(nombre, color=COLOR_FUENTE, alto=1.1):
    """"moneda" (2), "dado" (6) o "baraja" (52), con su probabilidad
    HUD colocada DEBAJO (`.tag`) y el numero de resultados en `.n`.

    Las tres van con el tag abajo a proposito: asi las tres se alinean en
    fila y el clip puede animar solo la cifra.
    """
    clave = str(nombre).strip().lower()
    alto = float(alto)
    r = 0.34 * alto

    if clave.startswith("mon"):
        n, prob = 2, "1/2"
        cuerpo = Circle(radius=r, stroke_width=2.4, color=color)
        cuerpo.set_fill(color, opacity=0.10)
        adorno = Circle(radius=r * 0.68, stroke_width=1.2, color=color)
        adorno.set_stroke(opacity=0.55)
        adorno.set_fill(opacity=0.0)
        forma = VGroup(cuerpo, adorno)
    elif clave.startswith("dad"):
        n, prob = 6, "1/6"
        cuerpo = RoundedRectangle(width=2 * r, height=2 * r,
                                  corner_radius=0.22 * r, stroke_width=2.4,
                                  color=color)
        cuerpo.set_fill(color, opacity=0.10)
        puntos = VGroup()
        for sx in (-1, 1):
            for sy in (-1, 0, 1):
                puntos.add(Dot(np.array([sx * 0.42 * r, sy * 0.50 * r, 0.0]),
                               radius=0.10 * r, color=color))
        forma = VGroup(cuerpo, puntos)
    elif clave.startswith("bar"):
        n, prob = 52, "1/52"
        cuerpo = RoundedRectangle(width=1.5 * r, height=2.2 * r,
                                  corner_radius=0.14 * r, stroke_width=2.4,
                                  color=color)
        cuerpo.set_fill(color, opacity=0.10)
        esquina = Square(side_length=0.34 * r, stroke_width=1.6, color=color)
        esquina.set_fill(color, opacity=0.45)
        esquina.move_to(np.array([-0.45 * r, 0.75 * r, 0.0]))
        forma = VGroup(cuerpo, esquina)
    else:
        raise ValueError(f"icono_fuente: '{nombre}' no es moneda/dado/baraja")

    tag = _texto_hud(prob, font_size=16, color=color)
    tag.next_to(forma, DOWN, buff=0.16)

    params = {"nombre": clave, "n": n, "prob": prob, "alto": alto}
    return IconoFuente(_ancla(forma.get_center()), forma, tag, params)


# =====================================================================
# El arbol de las 20 preguntas
# =====================================================================
class ArbolPreguntas(VGroup):
    """Arbol binario de si/no: cada pregunta parte el mundo en dos."""

    def __init__(self, ancla, ramas, nodos, etiquetas, params, **kwargs):
        super().__init__(ancla, ramas, nodos, etiquetas, **kwargs)
        self._ancla = ancla                 # la raiz
        self.ramas = ramas
        self.nodos = nodos                  # VGroup de VGroup por nivel
        self.etiquetas = etiquetas          # "si" / "no" del primer nivel
        self._params = params
        self.profundidad = params["profundidad"]
        self.n_hojas = params["n_hojas"]

    def nivel(self, k):
        """VGroup con los nodos del nivel k (0 = la raiz)."""
        return self.nodos[int(k)]

    def hoja(self, i):
        """La i-esima hoja de izquierda a derecha."""
        return self.nodos[self.profundidad][int(i)]

    def rama(self, k, j, lado):
        """La rama que baja del nodo j del nivel k por ese lado
        (0 = izquierda = "si")."""
        return self._params["ramas"][(int(k), int(j), int(lado))]

    def camino(self, bits):
        """Las ramas del camino que marcan esos bits (0 = izquierda).

        Para resaltar: `self.play(*[r.animate.set_color(C_BIT) for r in
        arbol.camino([0,1,1,0])])`. Devuelve un VGroup con REFERENCIAS a
        las ramas del arbol, no copias.
        """
        b = [int(x) & 1 for x in bits]
        if len(b) > self.profundidad:
            raise ValueError(f"camino: {len(b)} bits para profundidad "
                             f"{self.profundidad}")
        grupo, j = VGroup(), 0
        for k, lado in enumerate(b):
            grupo.add(self.rama(k, j, lado))
            j = 2 * j + lado
        return grupo


def arbol_preguntas(profundidad=4, ancho=5.4, alto=2.6, color=COLOR_FUENTE,
                    color_rama=COLOR_EJE):
    """El arbol de las preguntas de si/no: 2^profundidad hojas abajo.

    Cada nivel duplica las hojas; por eso 20 preguntas distinguen
    2^20 = 1 048 576 objetos. Solo el PRIMER nivel lleva los rotulos
    "si"/"no" (los demas se entienden y encimarian el dibujo).
    """
    profundidad = _validar("arbol_preguntas.profundidad", profundidad,
                           PROFUNDIDAD_MAX)
    ancho, alto = float(ancho), float(alto)
    paso_y = alto / profundidad

    def pos(k, j):
        return np.array([-ancho / 2.0 + (j + 0.5) * ancho / (2 ** k),
                         alto / 2.0 - k * paso_y, 0.0])

    ramas, mapa = VGroup(), {}
    for k in range(profundidad):
        for j in range(2 ** k):
            for lado in (0, 1):
                linea = Line(pos(k, j), pos(k + 1, 2 * j + lado),
                             stroke_width=1.4, color=color_rama)
                linea.set_stroke(opacity=0.8)
                mapa[(k, j, lado)] = linea
                ramas.add(linea)

    nodos = VGroup()
    for k in range(profundidad + 1):
        nivel = VGroup()
        r = 0.055 if k < profundidad else 0.045
        for j in range(2 ** k):
            nivel.add(Dot(pos(k, j), radius=r, color=color))
        nodos.add(nivel)

    etiquetas = VGroup()
    for lado, txt in ((0, "si"), (1, "no")):
        t = _texto_hud(txt, font_size=13, color=CODE_MUTED)
        medio = (pos(0, 0) + pos(1, lado)) / 2.0
        t.move_to(medio + (LEFT if lado == 0 else RIGHT) * 0.24)
        etiquetas.add(t)

    params = {"profundidad": profundidad, "n_hojas": 2 ** profundidad,
              "ancho": ancho, "alto": alto, "ramas": mapa}
    return ArbolPreguntas(_ancla(pos(0, 0)), ramas, nodos, etiquetas, params)


# =====================================================================
# El histograma de los 27 simbolos
# =====================================================================
def _rotulo_simbolo(sim):
    """El espacio se rotula "_" (en la fuente HUD un espacio no se ve)."""
    return "_" if sim == ESPACIO else sim


class HistogramaSimbolos(_Alineable):
    """27 barras con su simbolo debajo; la mas alta mide `alto`."""

    def __init__(self, ancla_a, ancla_b, linea_base, barras, etiquetas,
                 params, **kwargs):
        super().__init__(ancla_a, ancla_b, linea_base, barras, etiquetas,
                         **kwargs)
        self._ancla_a = ancla_a             # base izquierda
        self._ancla_b = ancla_b             # base derecha
        self._largo_ref = params["ancho"]
        self.linea_base = linea_base
        self.barras = barras
        self.etiquetas = etiquetas
        self._params = params
        self.frecuencias = params["frecs"]
        self.escala_max = params["escala_max"]   # frecuencia que mide `alto`

    def barra(self, sim):
        return self.barras[SIMBOLOS.index(sim)]

    def etiqueta(self, sim):
        return self.etiquetas[SIMBOLOS.index(sim)]

    def con_frecuencias(self, frecs):
        """Pieza GEMELA con otras alturas, ya escalada y colocada encima
        (para `Transform`). Conserva `escala_max`: las dos son
        comparables."""
        p = self._params
        otra = histograma_simbolos(frecs, p["color"], alto=p["alto"],
                                   ancho=p["ancho"],
                                   escala_max=p["escala_max"])
        return self._alinear(otra)

    def linea_uniforme(self, color=COLOR_LIMITE):
        """Punteada a la altura de 1/27: la fuente UNIFORME de 27
        simbolos, la que gastaria log2 27 = 4.75 bits. Se calcula con la
        escala ACTUAL de la pieza, asi que cae donde debe aunque el clip
        la haya escalado."""
        esc = self._escala_actual()
        h = ((1.0 / len(SIMBOLOS)) / max(self.escala_max, _EPS)
             * self._params["alto"] * esc)
        a = self._ancla_a.get_center() + UP * h
        b = self._ancla_b.get_center() + UP * h
        linea = DashedLine(a, b, stroke_width=1.8, color=color,
                           dash_length=0.10 * esc)
        linea.set_stroke(opacity=0.85)
        return linea


def histograma_simbolos(frecs, color=COLOR_FUENTE, alto=1.6, ancho=6.0,
                        escala_max=None):
    """El perfil de la fuente: 27 barras en el orden de `SIMBOLOS`.

    El espacio va el ultimo y se rotula "_" — y suele ser la barra mas
    alta del espanol. `escala_max` fija que frecuencia mide `alto`: dos
    histogramas con la misma escala se comparan honestamente.
    """
    alto, ancho = float(alto), float(ancho)
    frecs = {s: float(frecs.get(s, 0.0)) for s in SIMBOLOS}
    tope = float(escala_max) if escala_max else max(frecs.values())
    tope = max(tope, _EPS)

    paso = ancho / len(SIMBOLOS)
    ancho_barra = paso * 0.70
    x0 = -ancho / 2.0

    linea_base = Line(np.array([x0, 0.0, 0.0]),
                      np.array([x0 + ancho, 0.0, 0.0]),
                      stroke_width=1.6, color=COLOR_EJE)

    barras, etiquetas = VGroup(), VGroup()
    for i, sim in enumerate(SIMBOLOS):
        h = max(frecs[sim] / tope * alto, 0.004)
        x = x0 + (i + 0.5) * paso
        b = Rectangle(width=ancho_barra, height=h, stroke_width=0.8,
                      color=color)
        b.set_fill(color, opacity=0.85)
        b.move_to(np.array([x, h / 2.0, 0.0]))
        barras.add(b)
        e = _texto_hud(_rotulo_simbolo(sim), font_size=10, color=CODE_MUTED)
        e.move_to(np.array([x, -0.16, 0.0]))
        etiquetas.add(e)

    params = {"frecs": frecs, "color": color, "alto": alto, "ancho": ancho,
              "escala_max": tope}
    return HistogramaSimbolos(_ancla(np.array([x0, 0.0, 0.0])),
                              _ancla(np.array([x0 + ancho, 0.0, 0.0])),
                              linea_base, barras, etiquetas, params)


# =====================================================================
# El arbol de Huffman
# =====================================================================
def _lado_indice(lado):
    """0/"0"/"izq" -> 0 (el bit "0"); 1/"1"/"der" -> 1."""
    if isinstance(lado, str):
        clave = lado.strip().lower()
        if clave in ("0", "izq", "izquierda", "i"):
            return 0
        if clave in ("1", "der", "derecha", "d"):
            return 1
        raise ValueError(f"lado: '{lado}' no es izq/der")
    return 1 if int(lado) else 0


class ArbolHuffman(_Alineable):
    """El arbol construido de verdad: hojas abajo en fila, una fusion por
    nivel y las ramas rotuladas 0 (izquierda) / 1 (derecha)."""

    def __init__(self, ancla_a, ancla_b, ramas, etiquetas_bit, nodos, hojas,
                 params, **kwargs):
        super().__init__(ancla_a, ancla_b, ramas, etiquetas_bit, nodos,
                         hojas, **kwargs)
        self._ancla_a = ancla_a             # hoja de mas a la izquierda
        self._ancla_b = ancla_b             # hoja de mas a la derecha
        self._largo_ref = params["largo_ref"]
        self.ramas = ramas
        self.etiquetas_bit = etiquetas_bit
        self.nodos = nodos                  # VGroup de los nodos internos
        self.hojas = hojas                  # VGroup de las hojas
        self._params = params
        self.codigos = params["codigos"]
        self.n_fusiones = params["n_fusiones"]

    def hoja(self, sim):
        return self._params["hojas"][sim]

    def nodo(self, k):
        """El nodo de la k-esima fusion (k = 0 es la primera)."""
        return self._params["nodos"][int(k)]

    def rama(self, k, lado):
        return self._params["ramas"][(int(k), _lado_indice(lado))]

    def etiqueta_bit(self, k, lado):
        return self._params["bits"][(int(k), _lado_indice(lado))]

    def paso(self, k):
        """VGroup del nodo k con sus dos ramas y sus dos etiquetas: la
        unidad de animacion de la construccion (`FadeIn(arbol.paso(0))`).

        Son REFERENCIAS: para animar fusion a fusion, anade primero solo
        `arbol.hojas` a la escena (no el arbol entero) y ve haciendo
        FadeIn de cada `paso(k)`.
        """
        k = int(k)
        return VGroup(self.nodo(k), self.rama(k, 0), self.rama(k, 1),
                      self.etiqueta_bit(k, 0), self.etiqueta_bit(k, 1))

    def codigo(self, sim):
        """Las ramas del camino raiz -> hoja de ese simbolo (para
        resaltar como se lee el codigo). VGroup de referencias."""
        nodo = self._params["nucleo_hojas"][sim]
        camino = []
        while nodo["padre"] is not None:
            k, lado = nodo["padre"]
            camino.append(self._params["ramas"][(k, lado)])
            nodo = self._params["nucleo_nodos"][k]
        return VGroup(*reversed(camino))


def arbol_huffman(frecs, colores=None, pesos=None, ancho=5.5, alto=3.2,
                  color_hoja=COLOR_FUENTE, color_rama=COLOR_EJE):
    """El arbol de Huffman de esas frecuencias, dibujado sin cruces.

    Las hojas van abajo EN EL ORDEN DEL RECORRIDO del arbol (primero el
    subarbol del "0"), asi que ninguna rama cruza a otra; los nodos
    internos suben una fusion por nivel, de modo que `.paso(k)` deja ver
    la construccion en el mismo orden en que la hizo el algoritmo.

    `colores`: dict simbolo -> color para las hojas (por omision, todas
    `color_hoja`). `pesos`: dict simbolo -> int para rotular con enteros
    (A 5, B 2, ...); si es None se rotula la fraccion con 2 decimales.
    """
    hojas_nucleo, fusiones, raiz = _arbol_huffman_nucleo(frecs)
    n = len(hojas_nucleo)
    if n < 2:
        raise ValueError("arbol_huffman: hacen falta al menos 2 simbolos")
    ancho, alto = float(ancho), float(alto)
    colores = dict(colores or {})

    orden = []

    def recorrer(nodo):
        if nodo["hijos"] is None:
            orden.append(nodo["etiqueta"])
            return
        recorrer(nodo["hijos"][0])
        recorrer(nodo["hijos"][1])

    recorrer(raiz)

    y_hoja = -alto / 2.0
    paso_x = ancho / n
    x_hoja = {s: -ancho / 2.0 + (i + 0.5) * paso_x
              for i, s in enumerate(orden)}
    paso_y = alto / max(len(fusiones), 1)

    def peso_rotulo(nodo):
        if pesos is None:
            return f"{nodo['peso']:.2f}"
        return str(int(sum(int(pesos[s]) for s in nodo["etiqueta"])))

    centro = {}
    for s in orden:
        centro[id(hojas_nucleo[s])] = np.array([x_hoja[s], y_hoja, 0.0])

    hojas = VGroup()
    hojas_mob = {}
    for s in orden:
        t = _texto_hud(_rotulo_simbolo(s), font_size=20,
                       color=colores.get(s, color_hoja))
        t.move_to(np.array([x_hoja[s], y_hoja, 0.0]))
        w = _texto_hud(peso_rotulo(hojas_nucleo[s]), font_size=11,
                       color=CODE_MUTED)
        w.next_to(t, DOWN, buff=0.08)
        hoja = VGroup(t, w)
        hojas_mob[s] = hoja
        hojas.add(hoja)

    radio_nodo = 0.17
    nodos, ramas, bits = VGroup(), VGroup(), VGroup()
    mapa_nodos, mapa_ramas, mapa_bits = {}, {}, {}
    for k, nodo in enumerate(fusiones):
        izq, der = nodo["hijos"]
        c = np.array([(centro[id(izq)][0] + centro[id(der)][0]) / 2.0,
                      y_hoja + (k + 1) * paso_y, 0.0])
        centro[id(nodo)] = c

        circulo = Circle(radius=radio_nodo, stroke_width=1.8,
                         color=COLOR_LIMITE)
        circulo.set_fill(CODE_BG, opacity=1.0)
        circulo.move_to(c)
        txt = _texto_hud(peso_rotulo(nodo), font_size=11, color=COLOR_LIMITE)
        if txt.width > 1.7 * radio_nodo:
            txt.scale_to_fit_width(1.7 * radio_nodo)
        txt.move_to(c)
        mob_nodo = VGroup(circulo, txt)
        mapa_nodos[k] = mob_nodo
        nodos.add(mob_nodo)

        for lado, hijo in ((0, izq), (1, der)):
            destino = centro[id(hijo)]
            direccion = destino - c
            largo = float(np.linalg.norm(direccion))
            u = direccion / max(largo, _EPS)
            corte = 0.20 if hijo["hijos"] is None else radio_nodo
            linea = Line(c + u * radio_nodo, destino - u * corte,
                         stroke_width=1.6, color=color_rama)
            linea.set_stroke(opacity=0.9)
            mapa_ramas[(k, lado)] = linea
            ramas.add(linea)

            t = _texto_hud(str(lado), font_size=12, color=CODE_MUTED)
            medio = (c + destino) / 2.0
            t.move_to(medio + (LEFT if lado == 0 else RIGHT) * 0.16)
            mapa_bits[(k, lado)] = t
            bits.add(t)

    params = {"codigos": huffman(frecs), "n_fusiones": len(fusiones),
              "hojas": hojas_mob, "nodos": mapa_nodos, "ramas": mapa_ramas,
              "bits": mapa_bits, "nucleo_hojas": hojas_nucleo,
              "nucleo_nodos": fusiones, "orden": orden, "ancho": ancho,
              "alto": alto, "largo_ref": max((n - 1) * paso_x, paso_x)}
    a = _ancla(np.array([x_hoja[orden[0]], y_hoja, 0.0]))
    b = _ancla(np.array([x_hoja[orden[-1]], y_hoja, 0.0]))
    return ArbolHuffman(a, b, ramas, bits, nodos, hojas, params)


# =====================================================================
# La tira del mensaje codificado
# =====================================================================
class TiraCodigo(_Alineable):
    """El mensaje codificado: un rectangulo por SIMBOLO, de ancho
    proporcional a los bits que gasta."""

    def __init__(self, ancla_a, ancla_b, segmentos, params, **kwargs):
        super().__init__(ancla_a, ancla_b, segmentos, **kwargs)
        self._ancla_a = ancla_a             # extremo izquierdo
        self._ancla_b = ancla_b             # extremo derecho
        self._largo_ref = params["ancho"]
        self.segmentos = segmentos
        self._params = params
        self.texto = params["texto"]
        self.bits = params["bits"]          # la cadena de 0/1 completa
        self.n_bits = params["n_bits"]

    def segmento(self, i):
        """El i-esimo segmento (rectangulo + simbolo)."""
        return self.segmentos[int(i)]

    def marco(self, i):
        return self.segmentos[int(i)][0]


def tira_codigo(texto, codigo, colores=None, ancho=6.0, alto=0.42):
    """El mensaje codificado como segmentos contiguos, uno por simbolo.

    El ancho de cada segmento es proporcional a los BITS que gasta ese
    simbolo: se ve de un vistazo que la A (1 bit) ocupa la cuarta parte
    que la D (4 bits). Para "ABRACADABRA" son 11 segmentos y 23 bits.
    """
    limpio = normalizar(texto)
    if not limpio:
        raise ValueError("tira_codigo: el texto no tiene simbolos")
    faltan = sorted({c for c in limpio if c not in codigo})
    if faltan:
        raise ValueError(f"tira_codigo: sin codigo para {faltan}")
    _validar("tira_codigo.simbolos", len(limpio), 240)

    ancho, alto = float(ancho), float(alto)
    colores = dict(colores or {})
    bits = "".join(codigo[c] for c in limpio)
    n_bits = len(bits)

    segmentos = VGroup()
    x = -ancho / 2.0
    for c in limpio:
        w = ancho * len(codigo[c]) / n_bits
        col = colores.get(c, COLOR_FUENTE)
        marco = Rectangle(width=w, height=alto, stroke_width=1.0,
                          color=COLOR_EJE)
        marco.set_fill(col, opacity=0.80)
        marco.move_to(np.array([x + w / 2.0, 0.0, 0.0]))
        t = _texto_hud(_rotulo_simbolo(c), font_size=12, color=CODE_BG)
        if t.width > w - 0.05:
            t.scale_to_fit_width(max(w - 0.05, 0.02))
        t.move_to(marco.get_center())
        segmentos.add(VGroup(marco, t))
        x += w

    params = {"texto": limpio, "bits": bits, "n_bits": n_bits,
              "ancho": ancho, "alto": alto, "codigo": dict(codigo),
              "colores": colores}
    return TiraCodigo(_ancla(np.array([-ancho / 2.0, 0.0, 0.0])),
                      _ancla(np.array([ancho / 2.0, 0.0, 0.0])),
                      segmentos, params)


# =====================================================================
# Las imagenes: gris y binaria
# =====================================================================
class _Rejilla(_Alineable):
    """Base de `imagen_gris` / `imagen_bits`: celdas en filas x columnas."""

    def __init__(self, ancla_a, ancla_b, celdas, params, **kwargs):
        super().__init__(ancla_a, ancla_b, celdas, **kwargs)
        self._ancla_a = ancla_a             # centro de la celda (0, 0)
        self._ancla_b = ancla_b             # centro de la celda (0, ultima)
        self._largo_ref = params["largo_ref"]
        self.celdas = celdas
        self._params = params
        self.matriz = params["matriz"]
        self.filas = params["filas"]
        self.columnas = params["columnas"]

    def celda(self, f, c):
        """La celda de la fila f y la columna c (f = 0 es la de arriba)."""
        return self.celdas[int(f) * self.columnas + int(c)]


def _geometria_rejilla(matriz, celda):
    m = np.asarray(matriz)
    if m.ndim != 2:
        raise ValueError(f"imagen: la matriz tiene {m.ndim} dimensiones")
    filas, columnas = m.shape
    _validar("imagen.pixeles", filas * columnas, PIXELES_MAX)
    celda = float(celda)
    x0 = -(columnas - 1) * celda / 2.0
    y0 = (filas - 1) * celda / 2.0
    return m, filas, columnas, celda, x0, y0


class ImagenGris(_Rejilla):
    def con_matriz(self, matriz):
        """Pieza GEMELA con otra matriz, ya escalada y encima de esta
        (para `Transform`: la esfera cuantizada sobre la esfera)."""
        return self._alinear(imagen_gris(matriz, celda=self._params["celda"]))


def imagen_gris(matriz, celda=0.16, color=None):
    """Rejilla de celdas con relleno proporcional al valor 0..255.

    Sobre el fondo casi negro de la marca, la opacidad ES el gris: 0 se
    funde con el fondo y 255 queda blanco. `.celda(f, c)` con f = 0
    arriba, como en la matriz.
    """
    m, filas, columnas, celda, x0, y0 = _geometria_rejilla(matriz, celda)
    valores = np.clip(np.asarray(m, dtype=float), 0.0, 255.0)
    tinta = "#ffffff" if color is None else color
    lado = celda * 0.94

    celdas = VGroup()
    for f in range(filas):
        for c in range(columnas):
            q = Square(side_length=lado, stroke_width=0.0)
            q.set_fill(tinta, opacity=float(valores[f, c]) / 255.0)
            q.move_to(np.array([x0 + c * celda, y0 - f * celda, 0.0]))
            celdas.add(q)

    params = {"matriz": np.asarray(m).copy(), "filas": filas,
              "columnas": columnas, "celda": celda, "color": color,
              "largo_ref": max((columnas - 1) * celda, celda)}
    return ImagenGris(_ancla(np.array([x0, y0, 0.0])),
                      _ancla(np.array([x0 + (columnas - 1) * celda, y0, 0.0])),
                      celdas, params)


class ImagenBits(_Rejilla):
    def con_matriz(self, matriz):
        """Pieza GEMELA con otra matriz 0/1, ya escalada y encima."""
        return self._alinear(imagen_bits(matriz, self._params["color"],
                                         celda=self._params["celda"]))


def imagen_bits(matriz, color=COLOR_BIT, celda=0.16):
    """Rejilla binaria: la celda del 1 encendida, la del 0 apenas visible.

    Es el icono que se comprime con `rle` en el clip 4: los tramos largos
    de ceros son la redundancia que se va sin perder nada.
    """
    m, filas, columnas, celda, x0, y0 = _geometria_rejilla(matriz, celda)
    bits = (np.asarray(m) != 0)
    lado = celda * 0.94

    celdas = VGroup()
    for f in range(filas):
        for c in range(columnas):
            q = Square(side_length=lado, stroke_width=0.0)
            q.set_fill(color, opacity=0.9 if bits[f, c] else 0.06)
            q.move_to(np.array([x0 + c * celda, y0 - f * celda, 0.0]))
            celdas.add(q)

    params = {"matriz": np.asarray(m).copy(), "filas": filas,
              "columnas": columnas, "celda": celda, "color": color,
              "largo_ref": max((columnas - 1) * celda, celda)}
    return ImagenBits(_ancla(np.array([x0, y0, 0.0])),
                      _ancla(np.array([x0 + (columnas - 1) * celda, y0, 0.0])),
                      celdas, params)


# =====================================================================
# El esquema del canal binario simetrico
# =====================================================================
class EsquemaBSC(VGroup):
    """El BSC con sus cuatro caminos: dos que respetan el bit y dos que
    lo voltean."""

    def __init__(self, ancla, flechas, nodos, etiquetas, params, **kwargs):
        super().__init__(ancla, flechas, nodos, etiquetas, **kwargs)
        self._ancla = ancla                 # el centro del esquema
        self.flechas = flechas
        self.nodos = nodos
        self.etiquetas = etiquetas
        self._params = params
        self.p = params["p"]

    def entrada(self, b):
        return self._params["entradas"][int(b) & 1]

    def salida(self, b):
        return self._params["salidas"][int(b) & 1]

    def flecha(self, a, b):
        """La flecha del bit a de entrada al bit b de salida."""
        return self._params["flechas"][(int(a) & 1, int(b) & 1)]

    def etiqueta(self, a, b):
        """Su probabilidad: 1-p si a == b, p si el bit se voltea."""
        return self._params["etiquetas"][(int(a) & 1, int(b) & 1)]


def esquema_bsc(p=P_BSC, color_recto=COLOR_FUENTE, color_cruz=COLOR_RUIDO,
                sep_x=1.6, sep_y=0.7, radio=0.20):
    """El canal binario simetrico: entra un bit y sale el mismo con
    probabilidad 1-p, o el contrario con probabilidad p.

    Las cuatro etiquetas se colocan separadas a proposito (las rectas por
    fuera, las cruzadas junto a su salida) para que no se pisen.
    """
    p = float(p)
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"esquema_bsc: p={p} fuera de [0, 1]")
    sep_x, sep_y, radio = float(sep_x), float(sep_y), float(radio)

    def nodo(x, y, bit, color):
        c = Circle(radius=radio, stroke_width=2.0, color=color)
        c.set_fill(color, opacity=0.10)
        c.move_to(np.array([x, y, 0.0]))
        t = _texto_hud(str(bit), font_size=16, color=color)
        t.move_to(c.get_center())
        return VGroup(c, t)

    entradas = {0: nodo(-sep_x, sep_y, 0, COLOR_FUENTE),
                1: nodo(-sep_x, -sep_y, 1, COLOR_FUENTE)}
    salidas = {0: nodo(sep_x, sep_y, 0, COLOR_FUENTE),
               1: nodo(sep_x, -sep_y, 1, COLOR_FUENTE)}
    nodos = VGroup(entradas[0], entradas[1], salidas[0], salidas[1])

    def y_de(bit):
        return sep_y if bit == 0 else -sep_y

    flechas, etiquetas = VGroup(), VGroup()
    mapa_f, mapa_e = {}, {}
    for a in (0, 1):
        for b in (0, 1):
            recto = a == b
            color = color_recto if recto else color_cruz
            ini = np.array([-sep_x, y_de(a), 0.0])
            fin = np.array([sep_x, y_de(b), 0.0])
            f = Arrow(ini, fin, buff=radio + 0.06, stroke_width=2.2,
                      color=color, max_tip_length_to_length_ratio=0.06)
            f.set_opacity(0.9 if recto else 0.95)
            mapa_f[(a, b)] = f
            flechas.add(f)

            txt = f"{1 - p:.1f}" if recto else f"{p:.1f}"
            t = _texto_hud(txt, font_size=13, color=color)
            if recto:
                # Por FUERA: encima de la de arriba, debajo de la de abajo.
                t.move_to(np.array([0.0, y_de(a) + (0.22 if a == 0 else -0.22),
                                    0.0]))
            else:
                # Cerca del extremo de salida, apartada de la recta vecina.
                q = ini + 0.20 * (fin - ini)
                t.move_to(q + UP * (0.26 if a == 1 else -0.26))
            mapa_e[(a, b)] = t
            etiquetas.add(t)

    params = {"p": p, "entradas": entradas, "salidas": salidas,
              "flechas": mapa_f, "etiquetas": mapa_e, "sep_x": sep_x,
              "sep_y": sep_y}
    return EsquemaBSC(_ancla(ORIGIN), flechas, nodos, etiquetas, params)


# =====================================================================
# La tira de bits
# =====================================================================
class TiraBits(_Alineable):
    """Celdas 0/1: encendidas si el bit es 1, apenas visibles si es 0."""

    def __init__(self, ancla_a, ancla_b, celdas, params, **kwargs):
        super().__init__(ancla_a, ancla_b, celdas, **kwargs)
        self._ancla_a = ancla_a             # centro de la primera celda
        self._ancla_b = ancla_b             # centro de la ultima de la fila 0
        self._largo_ref = params["largo_ref"]
        self.celdas = celdas                # VGroup de VGroup(cuadro, digito)
        self._params = params
        self.bits = params["bits"]
        self.n_bits = len(params["bits"])
        self.filas = params["filas"]

    def celda(self, i):
        """La i-esima celda en orden de lectura (fila a fila)."""
        return self.celdas[int(i)]

    def cuadro(self, i):
        return self.celdas[int(i)][0]

    def con_bits(self, bits):
        """Tira GEMELA con otros bits, ya escalada y encima de esta."""
        p = self._params
        otra = tira_bits(bits, p["color"], celda=p["celda"],
                         filas=p["filas"])
        return self._alinear(otra)

    def marcar_distintos(self, otros_bits, color=COLOR_RUIDO):
        """Recolorea EN SITIO las celdas cuyo bit difiere y devuelve
        cuantas son: los bits que volteo el canal, CONTADOS sobre el
        dibujo. MUTA la pieza (no devuelve una copia)."""
        otros = np.asarray(otros_bits, dtype=int).ravel()
        if len(otros) != len(self.bits):
            raise ValueError(f"marcar_distintos: {len(otros)} bits contra "
                             f"{len(self.bits)}")
        cuenta = 0
        for i, (b, o) in enumerate(zip(self.bits, otros)):
            if int(b) != int(o):
                cuadro = self.celdas[i][0]
                cuadro.set_stroke(color, width=1.4, opacity=1.0)
                cuadro.set_fill(color, opacity=0.85 if int(b) else 0.18)
                cuenta += 1
        return int(cuenta)


def tira_bits(bits, color=COLOR_FUENTE, celda=0.26, filas=1):
    """Los bits como celdas: 1 encendido, 0 apagado, con su digito.

    `filas=2` parte la tira en dos mitades iguales (64 bits = 2 x 32), que
    es como caben los 64 del canal sin achicar la celda.
    """
    bits = np.asarray(bits, dtype=int).ravel()
    n = _validar("tira_bits.bits", len(bits), BITS_MAX)
    filas = _validar("tira_bits.filas", filas, 8)
    if n % filas != 0:
        raise ValueError(f"tira_bits: {n} bits no se parten en {filas} filas")
    celda = float(celda)
    por_fila = n // filas
    lado = celda * 0.92
    x0 = -(por_fila - 1) * celda / 2.0
    sep_y = celda * 1.22
    y0 = (filas - 1) * sep_y / 2.0

    grupo = VGroup()
    for i, b in enumerate(bits):
        f, c = divmod(i, por_fila)
        cuadro = Square(side_length=lado, stroke_width=1.1, color=COLOR_EJE)
        cuadro.set_fill(color, opacity=0.85 if b else 0.10)
        cuadro.move_to(np.array([x0 + c * celda, y0 - f * sep_y, 0.0]))
        # El digito del 1 va en el color del FONDO (sobre la celda
        # encendida) y el del 0 en gris: asi los dos se leen.
        digito = _texto_hud("1" if b else "0", font_size=12,
                            color=CODE_BG if b else CODE_MUTED)
        if not b:
            digito.set_opacity(0.75)
        digito.move_to(cuadro.get_center())
        grupo.add(VGroup(cuadro, digito))

    params = {"bits": bits.copy(), "color": color, "celda": celda,
              "filas": filas, "por_fila": por_fila,
              "largo_ref": max((por_fila - 1) * celda, celda)}
    return TiraBits(_ancla(np.array([x0, y0, 0.0])),
                    _ancla(np.array([x0 + (por_fila - 1) * celda, y0, 0.0])),
                    grupo, params)


# =====================================================================
# El diagrama de Venn de Hamming(7,4)
# =====================================================================
_ORDEN_VENN = ("A", "B", "C")


class VennHamming(_Alineable):
    """Los 7 bits de Hamming(7,4) repartidos en tres circulos: cada
    circulo debe tener un numero PAR de unos."""

    def __init__(self, ancla_a, ancla_b, circulos, letras, textos, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, circulos, letras, textos, **kwargs)
        self._ancla_a = ancla_a             # centro del circulo A
        self._ancla_b = ancla_b             # centro del circulo B
        self._largo_ref = params["largo_ref"]
        self.circulos = circulos
        self.letras = letras
        self.textos = textos
        self._params = params
        self.bits = params["bits"]

    def region(self, i):
        """El Text del bit de la posicion i (1..7)."""
        return self._params["regiones"][int(i)]

    def circulo(self, k):
        """El circulo "A", "B" o "C"."""
        return self._params["circulos"][str(k).upper()]

    def con_bits(self, palabra7):
        """Pieza GEMELA con otra palabra, ya escalada y encima (para
        `Transform`: la palabra con error sobre la correcta)."""
        p = self._params
        otra = venn_hamming(palabra7, radio=p["radio"], sep=p["sep"],
                            color_dato=p["color_dato"],
                            color_paridad=p["color_paridad"],
                            color_circulo=p["color_circulo"])
        return self._alinear(otra)

    def colorear_paridad(self, color_par=COLOR_CODIGO,
                         color_impar=COLOR_RUIDO):
        """Pinta el borde de cada circulo segun su paridad (verde si tiene
        un numero par de unos, rojo si impar) y devuelve la tupla de
        `paridades`. MUTA la pieza: los tres circulos cambian de color."""
        pars = paridades(self.bits)
        for k, par in zip(_ORDEN_VENN, pars):
            self.circulo(k).set_stroke(color_par if par else color_impar,
                                       width=2.8, opacity=1.0)
        return pars


def venn_hamming(palabra7, radio=1.05, sep=0.62, color_dato=COLOR_BIT,
                 color_paridad=COLOR_CODIGO, color_circulo=COLOR_EJE):
    """Hamming(7,4) en tres circulos: A arriba-izquierda, B
    arriba-derecha, C abajo.

    Las posiciones 1..7 caen en las regiones del contrato: p1 solo en A,
    p2 solo en B, d1 en A y B, p3 solo en C, d2 en A y C, d3 en B y C, d4
    en las tres. Los datos van en ambar y las paridades en verde.
    """
    w = _palabra7(palabra7)
    radio, sep = float(radio), float(sep)

    centros = {
        "A": np.array([-sep * math.cos(math.pi / 6.0), sep * 0.5, 0.0]),
        "B": np.array([sep * math.cos(math.pi / 6.0), sep * 0.5, 0.0]),
        "C": np.array([0.0, -sep, 0.0]),
    }

    circulos, mapa_circulos = VGroup(), {}
    for k in _ORDEN_VENN:
        c = Circle(radius=radio, stroke_width=2.2, color=color_circulo)
        c.set_fill(opacity=0.0)
        c.move_to(centros[k])
        mapa_circulos[k] = c
        circulos.add(c)

    letras = VGroup()
    for k in _ORDEN_VENN:
        u = centros[k] / max(float(np.linalg.norm(centros[k])), _EPS)
        t = _texto_hud(k, font_size=15, color=CODE_MUTED)
        t.move_to(centros[k] + u * (radio + 0.22))
        letras.add(t)

    def solo(k):
        u = centros[k] / max(float(np.linalg.norm(centros[k])), _EPS)
        return centros[k] + u * (radio * 0.52)

    def par(k1, k2):
        medio = (centros[k1] + centros[k2]) / 2.0
        k3 = [k for k in _ORDEN_VENN if k not in (k1, k2)][0]
        d = medio - centros[k3]
        u = d / max(float(np.linalg.norm(d)), _EPS)
        return medio + u * (radio * 0.40)

    lugares = {1: solo("A"), 2: solo("B"), 3: par("A", "B"), 4: solo("C"),
               5: par("A", "C"), 6: par("B", "C"),
               7: np.array([0.0, 0.0, 0.0])}

    textos, regiones = VGroup(), {}
    for i in range(1, 8):
        color = color_dato if i in POSICIONES_DATOS else color_paridad
        t = _texto_hud(str(w[i - 1]), font_size=22, color=color)
        t.move_to(lugares[i])
        regiones[i] = t
        textos.add(t)

    params = {"bits": list(w), "radio": radio, "sep": sep,
              "regiones": regiones, "circulos": mapa_circulos,
              "color_dato": color_dato, "color_paridad": color_paridad,
              "color_circulo": color_circulo,
              "largo_ref": float(np.linalg.norm(centros["B"] - centros["A"]))}
    return VennHamming(_ancla(centros["A"]), _ancla(centros["B"]), circulos,
                       letras, textos, params)


# =====================================================================
# La caja con un numero
# =====================================================================
class CajaNumero(_Alineable):
    """Caja rotulada con un numero grande: la unidad de rotulacion del
    curso (bits, longitud media, capacidad, BER...)."""

    def __init__(self, ancla_a, ancla_b, marco, etiqueta, valor, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, marco, etiqueta, valor, **kwargs)
        self._ancla_a = ancla_a             # izquierda de la caja
        self._ancla_b = ancla_b             # derecha de la caja
        self._largo_ref = params["ancho"]
        self.marco = marco
        self.etiqueta = etiqueta
        self.valor = valor
        self._params = params

    def _nuevo_valor(self, valor):
        p = self._params
        t = _texto_hud(valor, font_size=26, color=p["color"])
        t.scale(self._escala_actual())
        if t.width > (p["ancho"] - 0.24) * self._escala_actual():
            t.scale_to_fit_width((p["ancho"] - 0.24) * self._escala_actual())
        t.move_to(self.valor.get_center())
        return t

    def actualizar(self, valor):
        """Cambia el numero EN SITIO (misma posicion, misma escala) y
        devuelve el mobject nuevo; el viejo sale del grupo. MUTA la
        pieza."""
        nuevo = self._nuevo_valor(valor)
        self.remove(self.valor)
        self.add(nuevo)
        self.valor = nuevo
        self._params["valor"] = valor
        return nuevo


def caja_numero(etiqueta, valor, color=COLOR_BIT, ancho=1.9, alto=1.05):
    """Caja redondeada con una etiqueta chica arriba y el numero grande
    abajo. La etiqueta va en gris para que el protagonista sea la cifra."""
    ancho, alto = float(ancho), float(alto)
    marco = RoundedRectangle(width=ancho, height=alto, corner_radius=0.12,
                             stroke_width=2.2, color=color)
    marco.set_fill(color, opacity=0.05)

    t_et = _texto_hud(etiqueta, font_size=15, color=CODE_MUTED)
    if t_et.width > ancho - 0.20:
        t_et.scale_to_fit_width(ancho - 0.20)
    t_et.move_to(np.array([0.0, alto / 2.0 - 0.20, 0.0]))

    t_val = _texto_hud(valor, font_size=26, color=color)
    if t_val.width > ancho - 0.24:
        t_val.scale_to_fit_width(ancho - 0.24)
    t_val.move_to(np.array([0.0, -alto / 2.0 + 0.32, 0.0]))

    params = {"ancho": ancho, "alto": alto, "color": color,
              "etiqueta": etiqueta, "valor": valor}
    return CajaNumero(_ancla(np.array([-ancho / 2.0, 0.0, 0.0])),
                      _ancla(np.array([ancho / 2.0, 0.0, 0.0])),
                      marco, t_et, t_val, params)


# =====================================================================
# La linea de tiempo
# =====================================================================
class LineaTiempo(_Alineable):
    """Los hitos del cincuentenario que hizo falta para rozar el techo."""

    def __init__(self, ancla_a, ancla_b, linea, hitos, params, **kwargs):
        super().__init__(ancla_a, ancla_b, linea, hitos, **kwargs)
        self._ancla_a = ancla_a             # extremo izquierdo
        self._ancla_b = ancla_b             # extremo derecho
        self._largo_ref = params["ancho"]
        self.linea = linea
        self.hitos = hitos
        self._params = params

    def hito(self, k):
        """El k-esimo hito completo (marca + anio + texto)."""
        return self.hitos[int(k)]

    def marca(self, k):
        """Su rayita vertical sobre la linea."""
        return self.hitos[int(k)][0]

    def anio(self, k):
        return self.hitos[int(k)][1]

    def texto(self, k):
        return self.hitos[int(k)][2]


def linea_tiempo(hitos=None, ancho=9.0, color=COLOR_EJE,
                 color_marca=COLOR_LIMITE):
    """Linea horizontal con una marca por hito: el anio en HUD debajo y
    el texto alternando arriba/abajo para que no se pisen.

    Las marcas van EQUIESPACIADAS, no a escala de anios: 1948 y 1950
    quedarian encimados y el clip habla de la SECUENCIA, no del ritmo.
    """
    hitos = list(HITOS if hitos is None else hitos)
    n = _validar("linea_tiempo.hitos", len(hitos), 8)
    ancho = float(ancho)
    x0 = -ancho / 2.0
    paso = ancho / max(n - 1, 1)

    linea = Line(np.array([x0, 0.0, 0.0]), np.array([x0 + ancho, 0.0, 0.0]),
                 stroke_width=2.0, color=color)

    grupo = VGroup()
    for k, (anio, texto) in enumerate(hitos):
        x = x0 + k * paso
        marca = Line(np.array([x, -0.14, 0.0]), np.array([x, 0.14, 0.0]),
                     stroke_width=2.2, color=color_marca)
        t_anio = _texto_hud(str(anio), font_size=12, color=CODE_MUTED)
        t_anio.move_to(np.array([x, -0.34, 0.0]))
        t_txt = Text(str(texto), font_size=16, color=CODE_MUTED)
        if t_txt.width > paso * 1.05:
            t_txt.scale_to_fit_width(paso * 1.05)
        y = 0.40 if k % 2 == 0 else -0.66
        t_txt.move_to(np.array([x, y, 0.0]))
        grupo.add(VGroup(marca, t_anio, t_txt))

    params = {"hitos": hitos, "ancho": ancho}
    return LineaTiempo(_ancla(np.array([x0, 0.0, 0.0])),
                       _ancla(np.array([x0 + ancho, 0.0, 0.0])),
                       linea, grupo, params)


# =====================================================================
# El flujo de cajas
# =====================================================================
class Flujo(VGroup):
    """Cajas encadenadas por flechas: fuente -> codigo -> canal ->
    decodificador."""

    def __init__(self, ancla, flechas, cajas, params, **kwargs):
        super().__init__(ancla, flechas, cajas, **kwargs)
        self._ancla = ancla                 # el centro
        self.flechas = flechas
        self.cajas = cajas
        self._params = params

    def caja(self, i):
        return self.cajas[int(i)]

    def flecha(self, i):
        """La flecha que sale de la caja i (hacia la i+1)."""
        return self.flechas[int(i)]

    def texto(self, i):
        return self.cajas[int(i)][1]


def flujo(pasos, colores=None, ancho_caja=2.1, alto_caja=0.8, sep=0.62,
          font_size=20):
    """La cadena del sistema de comunicacion de Shannon: cada caja es un
    paso y la flecha es "de aqui sale aquello".

    `pasos` son los rotulos (fuente display, se admiten tildes) y
    `colores` uno por caja (por omision, todos cian).
    """
    pasos = [str(p) for p in pasos]
    n = _validar("flujo.pasos", len(pasos), 6)
    if colores is None:
        colores = [COLOR_FUENTE] * n
    colores = list(colores)
    if len(colores) != n:
        raise ValueError(f"flujo: {len(colores)} colores para {n} pasos")

    ancho_caja = float(ancho_caja)
    alto_caja, sep = float(alto_caja), float(sep)
    paso = ancho_caja + sep
    x0 = -((n - 1) * paso) / 2.0

    cajas = VGroup()
    for i, (p, col) in enumerate(zip(pasos, colores)):
        marco = RoundedRectangle(width=ancho_caja, height=alto_caja,
                                 corner_radius=0.10, stroke_width=2.2,
                                 color=col)
        marco.set_fill(col, opacity=0.07)
        t = Text(p, font_size=font_size, color=col)
        if t.width > ancho_caja - 0.24:
            t.scale_to_fit_width(ancho_caja - 0.24)
        caja = VGroup(marco, t)
        caja.move_to(np.array([x0 + i * paso, 0.0, 0.0]))
        t.move_to(marco.get_center())
        cajas.add(caja)

    flechas = VGroup()
    for i in range(n - 1):
        f = Arrow(cajas[i][0].get_right(), cajas[i + 1][0].get_left(),
                  buff=0.06, stroke_width=2.4, color=CODE_MUTED,
                  max_tip_length_to_length_ratio=0.22)
        f.set_opacity(0.75)
        flechas.add(f)

    params = {"pasos": pasos, "colores": colores, "ancho_caja": ancho_caja}
    return Flujo(_ancla(ORIGIN), flechas, cajas, params)

"""Criptografia: Cesar, la llave perfecta, Diffie-Hellman, RSA, hash y firma.

Pensado para el curso "Criptografia: el arte de guardar secretos". Todo el
calculo es python/numpy puro y determinista (el unico azar va con semilla;
SHA-256 es hashlib, determinista por definicion): mismo script -> mismo
render, condicion necesaria para `--disable_caching`. Nada de red, nada de
disco.

La regla de color del curso, que es tambien la de esta libreria: el texto
CLARO (el mensaje, el secreto, lo privado) es ambar, lo CIFRADO y lo publico
(lo que viaja por el canal) cian, las LLAVES y lo que verifica bien verde,
Eva / la fuerza bruta / lo que falla rojo, y el HASH, la firma y la
integridad violeta. Mobiliario en `COLOR_EJE`.

Piezas:
    rueda_cesar             dos anillos de letras; `.girar(k)` -> animacion
    tira_letras             el mensaje letra a letra; `.letra(i)`
    histograma_frecuencias  26 barras; `.desplazado(k)`, `.con_frecuencias()`
    tira_bits               celdas 0/1; `.con_bits(bits)`
    grafo_llaves            n(n-1)/2 aristas; `.n_aristas` MEDIDO
    esquema_dh              Ana, Beto, el canal publico y Eva debajo
    caja_numero             caja rotulada con un numero; `.actualizar(v)`
    curva_divisiones        10^(d/2) contra digitos; `.en(digitos)`
    rejilla_hash            16x16 bits; `.marcar_distintos()` CUENTA
    candado                 icono; `.abierto()` / `.cerrado()`
    flujo                   cajas encadenadas con flechas

Los NUMEROS que se rotulan salen de funciones (`cesar`, `frecuencias`,
`desplazamiento_estimado`, `llaves_por_pares`, `potencia_mod`,
`diffie_hellman`, `rsa_juguete`, `divisiones_hasta_factor`,
`sha256_bits`, `bits_distintos`, `firmar`, `verificar`), nunca a mano. La
avalancha del hash y las divisiones hasta el factor se MIDEN contando.

Topes duros para no castigar el VPS: `LETRAS_MAX`, `BITS_MAX`, `NODOS_MAX`
levantan ValueError.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from cripto import rueda_cesar, diffie_hellman

    rueda = rueda_cesar()
    self.play(rueda.girar(3), run_time=1.2)
"""

import hashlib
import math

import numpy as np

from manim import (Arc, Arrow, Circle, DashedLine, Dot, DoubleArrow, Line,
                   MathTex, Rectangle, Rotate, RoundedRectangle, Square,
                   Text, VGroup, VMobject, DOWN, LEFT, ORIGIN, PI, RIGHT,
                   TAU, UP)

from code_brand import CODE_BG, CODE_MUTED, FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
LETRAS_MAX = 600       # letras dibujadas en una tira
BITS_MAX = 512         # bits de una tira / de una llave
NODOS_MAX = 40         # nodos del grafo de llaves (100 y 1000 solo se rotulan)

# Paleta propia de la libreria (coincide con la del curso).
COLOR_CLARO = "#f59e0b"     # ambar: el mensaje en claro, lo secreto, lo privado
COLOR_CIFRADO = "#22d3ee"   # cian: lo cifrado, lo publico, el canal
COLOR_LLAVE = "#34d399"     # verde: las llaves, la verificacion correcta
COLOR_ATAQUE = "#f43f5e"    # rojo: Eva, la fuerza bruta, lo alterado, el fallo
COLOR_HUELLA = "#a78bfa"    # violeta: el hash, la firma, la integridad
COLOR_EJE = "#31414f"       # mobiliario

C_CLARO, C_CIFRADO, C_LLAVE = COLOR_CLARO, COLOR_CIFRADO, COLOR_LLAVE
C_ATAQUE, C_HUELLA, C_EJE = COLOR_ATAQUE, COLOR_HUELLA, COLOR_EJE

# --- Los datos del curso ---------------------------------------------
ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

TEXTO_ES = (
    "En esto, descubrieron treinta o cuarenta molinos de viento que hay en "
    "aquel campo, y asi como don Quijote los vio, dijo a su escudero: la "
    "ventura va guiando nuestras cosas mejor de lo que acertaramos a desear; "
    "porque ves alli, amigo Sancho Panza, donde se descubren treinta o pocos "
    "mas desaforados gigantes, con quien pienso hacer batalla y quitarles a "
    "todos las vidas, con cuyos despojos comenzaremos a enriquecer, que esta "
    "es buena guerra, y es gran servicio de Dios quitar tan mala simiente de "
    "sobre la faz de la tierra. Bien parece, respondio don Quijote, que no "
    "estas cursado en esto de las aventuras: ellos son gigantes.")
"""Texto de muestra del curso: Miguel de Cervantes, "El ingenioso hidalgo
don Quijote de la Mancha", primera parte, capitulo VIII (1605) — DOMINIO
PUBLICO. Transcrito sin tildes (el modulo normaliza a 26 letras ASCII).
502 letras: la E sale la mas frecuente (13.5 %), luego A, O, S — que es lo
que dice el espanol real. Las frecuencias del curso son las MEDIDAS en este
texto, no las de una tabla."""

MENSAJE_CESAR = "NOS VEMOS AL AMANECER"
DESPLAZAMIENTO = 3
P_DH, G_DH, A_DH, B_DH = 23, 5, 6, 15
P_RSA, Q_RSA, E_RSA = 61, 53, 17
M_RSA = 65
DIGITOS_RSA_2048 = 617          # digitos decimales de un modulo de 2048 bits
MENSAJE_HASH = "hola"
MENSAJE_HASH_2 = "Hola"
MENSAJE_OTP = "MAR"
MENSAJE_OTP_2 = "SOL"
SEMILLA_OTP = 7
N_BITS_OTP = 24

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


def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    """Texto de telemetria: Space Mono, ASCII puro (sin tildes ni signos
    raros: la fuente HUD no los tiene)."""
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
# Nucleo: el alfabeto y Cesar
# =====================================================================
def normalizar(texto):
    """Texto -> MAYUSCULAS de las 26 letras ASCII, espacios conservados.

    Quita tildes (A con acento -> A), la enie pasa a N y todo lo demas
    (comas, puntos, digitos) se descarta. Los espacios se mantienen tal
    cual para que el mensaje siga siendo legible en pantalla.
    """
    salida = []
    for ch in str(texto).upper():
        ch = _ACENTOS.get(ch, ch)
        if ch in ALFABETO:
            salida.append(ch)
        elif ch.isspace():
            salida.append(" ")
    return "".join(salida)


def cesar(texto, k):
    """Cifrado de Cesar: cada letra corre k posiciones en el alfabeto.

    `cesar(texto, 26 - k)` deshace `cesar(texto, k)` (el desplazamiento es
    un grupo ciclico de 26). Los espacios se conservan: por eso el cifrado
    de Cesar delata la forma de las palabras.
    """
    k = int(k) % len(ALFABETO)
    salida = []
    for ch in normalizar(texto):
        if ch == " ":
            salida.append(" ")
        else:
            salida.append(ALFABETO[(ALFABETO.index(ch) + k) % len(ALFABETO)])
    return "".join(salida)


def frecuencias(texto):
    """Fraccion de cada letra en el texto: dict con las 26 claves (las que
    no aparecen valen 0.0) y suma 1.0. Los espacios no cuentan."""
    limpio = [c for c in normalizar(texto) if c != " "]
    total = len(limpio)
    if total == 0:
        raise ValueError("frecuencias: el texto no tiene letras")
    cuenta = {ch: 0 for ch in ALFABETO}
    for c in limpio:
        cuenta[c] += 1
    return {ch: cuenta[ch] / float(total) for ch in ALFABETO}


def chi_cuadrado(frecs, referencia, total=1.0):
    """Distancia chi-cuadrado entre dos perfiles de frecuencia.

    sum (obs - esp)^2 / esp sobre las 26 letras, con `total` letras
    observadas. Las letras ausentes de la referencia (K, W, X en el texto
    de muestra) llevan un piso `_EPS` para no dividir entre cero: si el
    candidato las produce, el castigo es enorme, que es justo lo que se
    quiere.
    """
    s = 0.0
    for ch in ALFABETO:
        esp = max(referencia[ch] * float(total), _EPS)
        obs = frecs[ch] * float(total)
        s += (obs - esp) ** 2 / esp
    return s


def desplazamiento_estimado(cifrado, referencia=None):
    """El k que mejor explica el cifrado: chi-cuadrado MINIMO contra el
    perfil del espanol medido en `TEXTO_ES`.

    Se prueban los 26 descifrados posibles y gana el que mas se parece al
    idioma. No hace falta ingenio: la estadistica sola rompe a Cesar.
    """
    ref = frecuencias(TEXTO_ES) if referencia is None else referencia
    limpio = [c for c in normalizar(cifrado) if c != " "]
    total = len(limpio)
    mejor_k, mejor_chi = 0, None
    for k in range(len(ALFABETO)):
        frecs = frecuencias(cesar(cifrado, -k))
        chi = chi_cuadrado(frecs, ref, total)
        if mejor_chi is None or chi < mejor_chi:
            mejor_k, mejor_chi = k, chi
    return mejor_k


# =====================================================================
# Nucleo: bits, XOR y la llave perfecta
# =====================================================================
def texto_a_bits(texto):
    """Texto ASCII -> np.array de bits (8 por caracter, el mas alto
    primero). "MAR" da 24 bits."""
    texto = str(texto)
    _validar("texto_a_bits.bits", 8 * max(len(texto), 1), BITS_MAX)
    bits = []
    for ch in texto:
        v = ord(ch)
        if v > 255:
            raise ValueError(f"texto_a_bits: '{ch}' no es ASCII/latin-1")
        bits.extend((v >> i) & 1 for i in range(7, -1, -1))
    return np.array(bits, dtype=int)


def bits_a_texto(bits):
    """Inverso de `texto_a_bits`: 8 bits -> un caracter."""
    bits = np.asarray(bits, dtype=int).ravel()
    if len(bits) % 8 != 0:
        raise ValueError(f"bits_a_texto: {len(bits)} bits no son multiplo de 8")
    chars = []
    for i in range(0, len(bits), 8):
        v = 0
        for b in bits[i:i + 8]:
            v = (v << 1) | int(b)
        chars.append(chr(v))
    return "".join(chars)


def llave_otp(n_bits=N_BITS_OTP, semilla=SEMILLA_OTP):
    """Llave aleatoria de un solo uso, SEMBRADA (mismo render siempre)."""
    n_bits = _validar("llave_otp.n_bits", n_bits, BITS_MAX)
    rng = np.random.default_rng(int(semilla))
    return rng.integers(0, 2, size=n_bits, dtype=np.int64).astype(int)


def xor_bits(a, b):
    """XOR bit a bit. Es involutivo: (m XOR k) XOR k = m. Ahi vive todo el
    one-time pad."""
    a = np.asarray(a, dtype=int).ravel()
    b = np.asarray(b, dtype=int).ravel()
    if len(a) != len(b):
        raise ValueError(f"xor_bits: longitudes {len(a)} y {len(b)}")
    return (a ^ b).astype(int)


def llave_que_da(cifrado, mensaje_deseado):
    """La demostracion de Shannon (1949): dado un cifrado, SIEMPRE existe
    una llave que lo convierte en el mensaje que uno quiera — es
    `cifrado XOR deseado`. Por eso el pad perfecto no filtra nada: el
    atacante no puede distinguir "MAR" de "SOL"."""
    return xor_bits(cifrado, mensaje_deseado)


def llaves_por_pares(n):
    """Llaves secretas distintas que necesitan n personas para hablar por
    pares: n(n-1)/2. 10 -> 45, 100 -> 4950, 1000 -> 499500."""
    n = int(n)
    if n < 0:
        raise ValueError(f"llaves_por_pares: n={n} < 0")
    return n * (n - 1) // 2


# =====================================================================
# Nucleo: Diffie-Hellman y RSA
# =====================================================================
def potencia_mod(base, exp, mod):
    """base^exp mod m por cuadrados sucesivos, en enteros exactos."""
    base, exp, mod = int(base), int(exp), int(mod)
    if mod < 1:
        raise ValueError(f"potencia_mod: mod={mod} < 1")
    if exp < 0:
        raise ValueError(f"potencia_mod: exp={exp} < 0")
    acumulado, b = 1, base % mod
    while exp > 0:
        if exp & 1:
            acumulado = (acumulado * b) % mod
        b = (b * b) % mod
        exp >>= 1
    return acumulado


def pasos_potencia_mod(base, exp, mod):
    """Los pasos del cuadrado sucesivo, para animar la cuenta: lista de
    (bit, acumulado) del bit menos significativo al mas significativo."""
    base, exp, mod = int(base), int(exp), int(mod)
    acumulado, b, pasos = 1, base % mod, []
    while exp > 0:
        bit = exp & 1
        if bit:
            acumulado = (acumulado * b) % mod
        pasos.append((bit, acumulado))
        b = (b * b) % mod
        exp >>= 1
    return pasos


def diffie_hellman(p=P_DH, g=G_DH, a=A_DH, b=B_DH):
    """El acuerdo de 1976: Ana y Beto gritan en publico y acaban con un
    secreto comun que nunca viajo.

    Publico: p y g. Ana grita A = g^a mod p, Beto grita B = g^b mod p.
    Cada uno eleva lo que oyo a su exponente privado y les sale el MISMO
    numero, porque (g^a)^b = (g^b)^a. Devuelve {A, B, s_ana, s_beto}.
    """
    p = int(p)
    if p < 2:
        raise ValueError(f"diffie_hellman: p={p} < 2")
    pub_a = potencia_mod(g, a, p)
    pub_b = potencia_mod(g, b, p)
    return {"A": pub_a, "B": pub_b,
            "s_ana": potencia_mod(pub_b, a, p),
            "s_beto": potencia_mod(pub_a, b, p)}


def _inverso_mod(e, m):
    """Inverso multiplicativo por Euclides extendido (sin fuerza bruta)."""
    e, m = int(e) % int(m), int(m)
    r0, r1, s0, s1 = m, e, 0, 1
    while r1 != 0:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    if r0 != 1:
        raise ValueError(f"_inverso_mod: {e} no es invertible modulo {m}")
    return s0 % m


def rsa_juguete(p=P_RSA, q=Q_RSA, e=E_RSA):
    """RSA con numeros de JUGUETE (los reales tienen 2048 bits).

    n = p*q es publico; phi = (p-1)(q-1) solo lo sabe quien conoce p y q;
    d = e^-1 mod phi es la llave privada. Con 61 y 53: n=3233, phi=3120,
    d=2753. Devuelve {n, phi, d}.
    """
    p, q, e = int(p), int(q), int(e)
    n, phi = p * q, (p - 1) * (q - 1)
    return {"n": n, "phi": phi, "d": _inverso_mod(e, phi)}


def rsa_cifrar(m, e, n):
    """c = m^e mod n con la llave PUBLICA (cualquiera puede cerrar)."""
    if int(m) >= int(n):
        raise ValueError(f"rsa_cifrar: m={m} no cabe en n={n}")
    return potencia_mod(m, e, n)


def rsa_descifrar(c, d, n):
    """m = c^d mod n con la llave PRIVADA (solo Ana puede abrir)."""
    return potencia_mod(c, d, n)


def _primos_hasta(limite):
    """Criba de Eratostenes hasta `limite` inclusive."""
    limite = int(limite)
    if limite < 2:
        return []
    criba = np.ones(limite + 1, dtype=bool)
    criba[:2] = False
    for i in range(2, int(math.isqrt(limite)) + 1):
        if criba[i]:
            criba[i * i::i] = False
    return [int(i) for i in np.nonzero(criba)[0]]


def divisiones_hasta_factor(n):
    """Primos PROBADOS por fuerza bruta hasta dar con un factor de n.

    MEDIDO contando: se prueban 2, 3, 5, 7, ... hasta la raiz. El conteo
    INCLUYE el primo que si divide (es una division mas que hay que
    hacer): para n = 3233 = 53 x 61 son los 16 primos de 2 a 53. Si n es
    primo devuelve cuantos se probaron sin exito.
    """
    n = int(n)
    if n < 2:
        raise ValueError(f"divisiones_hasta_factor: n={n} < 2")
    probados = 0
    for p in _primos_hasta(int(math.isqrt(n))):
        probados += 1
        if n % p == 0:
            return probados
    return probados


def exponente_divisiones(digitos):
    """El exponente de la cuenta: log10(10^(d/2)) = d/2. Es lo que se
    ROTULA (10^308 para 617 digitos), porque el numero en si no cabe en un
    float de 64 bits."""
    return float(digitos) / 2.0


def divisiones_estimadas(digitos):
    """Divisiones de prueba para factorizar un n de `digitos` digitos:
    ~10^(d/2), porque hay que llegar hasta la raiz.

    Devuelve float. OJO: el float64 se acaba en 1.8e308, asi que a partir
    de 617 digitos (RSA-2048) el valor real —10^308.5— ya no es
    representable y esta funcion devuelve `math.inf`. Para rotular la
    cifra usa `exponente_divisiones(d)` y escribela como potencia con
    MathTex (10^{308}); asi tambien se lee mejor en pantalla.
    """
    try:
        return 10.0 ** (float(digitos) / 2.0)
    except OverflowError:
        return math.inf


# =====================================================================
# Nucleo: hash y firma
# =====================================================================
def sha256_hex(texto):
    """SHA-256 real (hashlib) en hexadecimal: 64 digitos, 256 bits."""
    return hashlib.sha256(str(texto).encode("utf-8")).hexdigest()


def sha256_bits(texto):
    """SHA-256 como np.array de 256 bits 0/1 (el mas alto primero)."""
    entero = int(sha256_hex(texto), 16)
    return np.array([(entero >> i) & 1 for i in range(255, -1, -1)],
                    dtype=int)


def bits_distintos(a, b):
    """Bits en que difieren dos huellas: la AVALANCHA, contada (no citada)."""
    a = np.asarray(a, dtype=int).ravel()
    b = np.asarray(b, dtype=int).ravel()
    if len(a) != len(b):
        raise ValueError(f"bits_distintos: longitudes {len(a)} y {len(b)}")
    return int(np.count_nonzero(a != b))


def hash_reducido(texto, n):
    """La huella llevada al rango del RSA de juguete: sha256 mod n. Se
    rotula como reduccion — la firma real usa relleno (PSS), no el hash
    pelado."""
    return int(sha256_hex(texto), 16) % int(n)


def firmar(h, d, n):
    """Firma = huella elevada a la llave PRIVADA: s = h^d mod n."""
    return potencia_mod(h, d, n)


def verificar(s, e, n, h):
    """Cualquiera con la llave publica comprueba s^e mod n == h."""
    return potencia_mod(s, e, n) == int(h) % int(n)


def alterar_bit(texto, indice=0):
    """Voltea un bit del mensaje y devuelve el texto alterado.

    `indice` es sobre los bits del texto (8 por caracter, el mas alto
    primero). Si voltear ESE bit deja un caracter no imprimible, avanza al
    siguiente bit hasta que lo sea — asi la alteracion se puede mostrar en
    pantalla. Ejemplo del curso: "hola" con indice 0 pediria el bit mas
    alto de la 'h' (0x68 -> 0xE8, no imprimible), asi que cae en el
    siguiente y sale "(ola": un solo bit de diferencia.
    """
    texto = str(texto)
    bits = texto_a_bits(texto)
    n = len(bits)
    for salto in range(n):
        i = (int(indice) + salto) % n
        otro = bits.copy()
        otro[i] = 1 - otro[i]
        cand = bits_a_texto(otro)
        if all(32 <= ord(c) <= 126 for c in cand):
            return cand
    raise ValueError("alterar_bit: ningun bit deja un texto imprimible")


# =====================================================================
# La rueda de Cesar
# =====================================================================
class RuedaCesar(VGroup):
    """Dos anillos de letras: el exterior (claro, ambar) gira sobre el
    interior (cifrado, cian). `.girar(k)` devuelve la ANIMACION."""

    def __init__(self, ancla, circulo_ext, circulo_int, exterior, interior,
                 params, **kwargs):
        super().__init__(ancla, circulo_ext, circulo_int, exterior, interior,
                         **kwargs)
        self._ancla = ancla                 # el centro de la rueda
        self.circulo_ext = circulo_ext
        self.circulo_int = circulo_int
        self.exterior = exterior            # VGroup de 26 Text ambar
        self.interior = interior            # VGroup de 26 Text cian
        self._params = params
        self._ext = params["ext"]           # dict letra -> Text
        self._int = params["int"]
        self.paso_angulo = TAU / len(ALFABETO)

    def centro(self):
        """El centro de la rueda sobre la geometria ACTUAL."""
        return self._ancla.get_center()

    def letra_exterior(self, ch):
        """El Text ambar de esa letra, donde este AHORA."""
        return self._ext[normalizar(ch)[0]]

    def letra_interior(self, ch):
        """El Text cian de esa letra, donde este AHORA."""
        return self._int[normalizar(ch)[0]]

    def girar(self, k, **kwargs):
        """Animacion: el anillo exterior corre k posiciones (relativo al
        estado actual; k negativo gira al reves). Tras `girar(3)` la 'A'
        de fuera queda frente a la 'D' de dentro, que es justo lo que hace
        `cesar(texto, 3)`. Las letras giran CON la rueda: es una rueda
        fisica, se inclinan.
        """
        return Rotate(self.exterior, angle=-float(k) * self.paso_angulo,
                      about_point=self.centro(), **kwargs)

    def poner(self, k):
        """El mismo giro pero sin animar (para el estado inicial de un
        clip). Devuelve self."""
        self.exterior.rotate(-float(k) * self.paso_angulo,
                             about_point=self.centro())
        return self


def rueda_cesar(radio=1.6, color_ext=COLOR_CLARO, color_int=COLOR_CIFRADO):
    """La rueda de Cesar: 26 letras claras fuera, 26 cifradas dentro.

    El anillo exterior es el texto EN CLARO (ambar) y el interior el
    CIFRADO (cian); girar el exterior k posiciones es el cifrado de Cesar
    de llave k. Con 26 posiciones y una trivial, quedan 25 llaves utiles:
    una llave que se puede enumerar no es una llave.
    """
    radio = float(radio)
    r_int, r_ext = radio, radio + 0.45
    n = len(ALFABETO)

    circulo_int = Circle(radius=r_int + 0.22, stroke_width=1.4,
                         color=COLOR_EJE)
    circulo_ext = Circle(radius=r_ext + 0.26, stroke_width=1.4,
                         color=COLOR_EJE)
    circulo_int.set_fill(opacity=0.0)
    circulo_ext.set_fill(opacity=0.0)

    def punto(i, r):
        ang = 0.25 * TAU - i * TAU / n
        return r * np.array([math.cos(ang), math.sin(ang), 0.0])

    # Las letras crecen con la rueda: 26 en un circulo pequeno se tocan.
    esc = radio / 1.6
    ext_g, int_g = VGroup(), VGroup()
    ext_d, int_d = {}, {}
    for i, ch in enumerate(ALFABETO):
        t_e = _texto_hud(ch, font_size=20 * esc, color=color_ext)
        t_e.move_to(punto(i, r_ext))
        ext_d[ch] = t_e
        ext_g.add(t_e)
        t_i = _texto_hud(ch, font_size=18 * esc, color=color_int)
        t_i.move_to(punto(i, r_int))
        int_d[ch] = t_i
        int_g.add(t_i)

    params = {"radio": radio, "ext": ext_d, "int": int_d}
    return RuedaCesar(_ancla(ORIGIN), circulo_ext, circulo_int, ext_g, int_g,
                      params)


# =====================================================================
# La tira de letras
# =====================================================================
_ANCHO_GLIFO = {}


def _ancho_glifo(font_size):
    """Ancho del glifo mas ancho del alfabeto en la fuente HUD, medido una
    sola vez por tamano (Space Mono es monoespaciada, pero la caja de
    tinta de cada letra no)."""
    clave = round(float(font_size), 3)
    if clave not in _ANCHO_GLIFO:
        probe = _texto_hud(ALFABETO, font_size=font_size)
        _ANCHO_GLIFO[clave] = float(max(g.width for g in probe.submobjects))
    return _ANCHO_GLIFO[clave]


class TiraLetras(VGroup):
    """El mensaje letra a letra; `.letra(i)` es la i-esima letra que NO es
    espacio (los espacios son huecos, no mobjects)."""

    def __init__(self, ancla, letras, params, **kwargs):
        super().__init__(ancla, letras, **kwargs)
        self._ancla = ancla                 # extremo izquierdo de la tira
        self.letras = letras                # VGroup en orden de lectura
        self._params = params
        self.texto = params["texto"]
        self.n_letras = params["n_letras"]

    def letra(self, i):
        """La i-esima letra (los espacios no cuentan)."""
        return self.letras[int(i)]

    def indice_de(self, i_texto):
        """Indice de letra que corresponde a la posicion `i_texto` del
        texto normalizado (o None si ahi hay un espacio)."""
        return self._params["mapa"].get(int(i_texto))


def tira_letras(texto, color=COLOR_CLARO, font_size=30):
    """Las letras del mensaje en fila, con los espacios como hueco.

    Space Mono: todas las letras ocupan lo mismo, asi que dos tiras del
    mismo texto (claro y cifrado) quedan alineadas columna a columna.
    """
    texto = normalizar(texto)
    letras_reales = [c for c in texto if c != " "]
    _validar("tira_letras.letras", max(len(letras_reales), 1), LETRAS_MAX)

    escala = float(font_size) / 30.0
    paso = _ancho_glifo(font_size) + 0.16 * escala
    hueco = 0.35 * escala

    grupo, mapa = VGroup(), {}
    x = 0.0
    for i, ch in enumerate(texto):
        if ch == " ":
            x += hueco
            continue
        t = _texto_hud(ch, font_size=font_size, color=color)
        t.move_to(np.array([x + paso / 2.0, 0.0, 0.0]))
        mapa[i] = len(grupo)
        grupo.add(t)
        x += paso

    params = {"texto": texto, "n_letras": len(letras_reales), "mapa": mapa,
              "paso": paso, "hueco": hueco}
    pieza = TiraLetras(_ancla(ORIGIN), grupo, params)
    pieza.shift(LEFT * x / 2.0)
    return pieza


# =====================================================================
# El histograma de frecuencias
# =====================================================================
class HistogramaFrecuencias(_Alineable):
    """26 barras con su letra debajo. La altura es proporcional a la
    frecuencia y la barra mas alta mide `alto`."""

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

    def barra(self, ch):
        """La barra de esa letra, donde este AHORA."""
        return self.barras[ALFABETO.index(normalizar(ch)[0])]

    def etiqueta(self, ch):
        return self.etiquetas[ALFABETO.index(normalizar(ch)[0])]

    def con_frecuencias(self, frecs):
        """Una pieza GEMELA con otras alturas, ya escalada y colocada
        encima de esta: `Transform(hist, hist.con_frecuencias(otras))`.
        Conserva `escala_max`, asi que las dos son comparables."""
        p = self._params
        otra = histograma_frecuencias(frecs, p["color"], alto=p["alto"],
                                      ancho=p["ancho"],
                                      escala_max=p["escala_max"])
        return self._alinear(otra)

    def desplazado(self, k):
        """La misma silueta corrida k posiciones: la barra de la letra L
        toma la frecuencia de la letra L-k. Es lo que hace el ataque del
        clip 2 — deslizar el histograma cifrado hasta que encaje."""
        k = int(k) % len(ALFABETO)
        frecs = {ALFABETO[(i) % 26]:
                 self.frecuencias[ALFABETO[(i - k) % 26]]
                 for i in range(len(ALFABETO))}
        return self.con_frecuencias(frecs)


def histograma_frecuencias(frecs, color=COLOR_CLARO, alto=1.6, ancho=5.2,
                           escala_max=None):
    """El perfil del idioma: 26 barras con la letra debajo.

    `escala_max` fija que frecuencia mide `alto` (por omision, la maxima
    del propio perfil). Pasarla explicitamente deja dos histogramas a la
    MISMA escala, que es como se comparan honestamente.
    """
    alto, ancho = float(alto), float(ancho)
    frecs = {ch: float(frecs[ch]) for ch in ALFABETO}
    tope = float(escala_max) if escala_max else max(frecs.values())
    tope = max(tope, _EPS)

    paso = ancho / len(ALFABETO)
    ancho_barra = paso * 0.70
    x0 = -ancho / 2.0

    linea_base = Line(np.array([x0, 0.0, 0.0]),
                      np.array([x0 + ancho, 0.0, 0.0]),
                      stroke_width=1.6, color=COLOR_EJE)

    barras, etiquetas = VGroup(), VGroup()
    for i, ch in enumerate(ALFABETO):
        h = max(frecs[ch] / tope * alto, 0.004)
        x = x0 + (i + 0.5) * paso
        b = Rectangle(width=ancho_barra, height=h, stroke_width=0.8,
                      color=color)
        b.set_fill(color, opacity=0.85)
        b.move_to(np.array([x, h / 2.0, 0.0]))
        barras.add(b)
        e = _texto_hud(ch, font_size=11, color=CODE_MUTED)
        e.move_to(np.array([x, -0.16, 0.0]))
        etiquetas.add(e)

    params = {"frecs": frecs, "color": color, "alto": alto, "ancho": ancho,
              "escala_max": tope}
    return HistogramaFrecuencias(_ancla(np.array([x0, 0.0, 0.0])),
                                 _ancla(np.array([x0 + ancho, 0.0, 0.0])),
                                 linea_base, barras, etiquetas, params)


# =====================================================================
# La tira de bits
# =====================================================================
class TiraBits(_Alineable):
    """Celdas 0/1: encendidas si el bit es 1, apenas visibles si es 0."""

    def __init__(self, ancla_a, ancla_b, celdas, params, **kwargs):
        super().__init__(ancla_a, ancla_b, celdas, **kwargs)
        self._ancla_a = ancla_a             # centro de la primera celda
        self._ancla_b = ancla_b             # centro de la ultima celda
        self._largo_ref = params["largo_ref"]
        self.celdas = celdas                # VGroup de VGroup(cuadro, digito)
        self._params = params
        self.bits = params["bits"]
        self.n_bits = len(params["bits"])

    def celda(self, i):
        """La i-esima celda (cuadro + digito), donde este AHORA."""
        return self.celdas[int(i)]

    def cuadro(self, i):
        return self.celdas[int(i)][0]

    def con_bits(self, bits):
        """Una tira GEMELA con otros bits, ya escalada y encima de esta
        (para `Transform`)."""
        p = self._params
        otra = tira_bits(bits, p["color"], celda=p["celda"])
        return self._alinear(otra)


def tira_bits(bits, color=COLOR_CLARO, celda=0.28):
    """Los bits del mensaje como celdas: 1 encendido, 0 apagado.

    Cada celda lleva su digito para que no haya que adivinar: el cifrado
    del one-time pad tiene que PARECER ruido, y solo se ve que lo parece
    si se leen los bits.
    """
    bits = np.asarray(bits, dtype=int).ravel()
    n = _validar("tira_bits.bits", len(bits), BITS_MAX)
    celda = float(celda)
    lado = celda * 0.92
    x0 = -(n - 1) * celda / 2.0

    grupo = VGroup()
    for i, b in enumerate(bits):
        x = x0 + i * celda
        cuadro = Square(side_length=lado, stroke_width=1.1, color=COLOR_EJE)
        cuadro.set_fill(color, opacity=0.85 if b else 0.10)
        cuadro.move_to(np.array([x, 0.0, 0.0]))
        # El digito del 1 va en el color del FONDO (sobre la celda
        # encendida) y el del 0 en gris: asi los dos se leen.
        digito = _texto_hud("1" if b else "0", font_size=12,
                            color=CODE_BG if b else CODE_MUTED)
        if not b:
            digito.set_opacity(0.75)
        digito.move_to(cuadro.get_center())
        grupo.add(VGroup(cuadro, digito))

    params = {"bits": bits.copy(), "color": color, "celda": celda,
              "largo_ref": max((n - 1) * celda, celda)}
    return TiraBits(_ancla(np.array([x0, 0.0, 0.0])),
                    _ancla(np.array([x0 + (n - 1) * celda, 0.0, 0.0])),
                    grupo, params)


# =====================================================================
# El grafo de llaves
# =====================================================================
class GrafoLlaves(VGroup):
    """n personas y TODAS las llaves secretas que necesitan por pares."""

    def __init__(self, ancla, aristas, nodos, params, **kwargs):
        super().__init__(ancla, aristas, nodos, **kwargs)
        self._ancla = ancla                 # el centro
        self.aristas = aristas
        self.nodos = nodos
        self._params = params
        self.n = params["n"]
        self.n_aristas = params["n_aristas"]

    def nodo(self, i):
        return self.nodos[int(i)]

    def arista(self, i):
        return self.aristas[int(i)]


def grafo_llaves(n=10, radio=1.4, color_nodo=COLOR_LLAVE,
                 color_arista=COLOR_LLAVE):
    """El grafo completo de las llaves: n(n-1)/2 aristas, dibujadas de
    verdad (el numero se cuenta, no se afirma).

    Tope `NODOS_MAX`: con 100 o 1000 personas el dibujo no cabe ni ayuda —
    ahi el clip solo rotula la cifra de `llaves_por_pares`.
    """
    n = _validar("grafo_llaves.n", n, NODOS_MAX)
    radio = float(radio)

    puntos = [radio * np.array([math.cos(0.25 * TAU + i * TAU / n),
                                math.sin(0.25 * TAU + i * TAU / n), 0.0])
              for i in range(n)]
    aristas = VGroup()
    for i in range(n):
        for j in range(i + 1, n):
            l = Line(puntos[i], puntos[j], stroke_width=1.1,
                     color=color_arista)
            l.set_stroke(opacity=0.45)
            aristas.add(l)
    nodos = VGroup(*[Dot(p, radius=0.075, color=color_nodo) for p in puntos])

    params = {"n": n, "radio": radio, "n_aristas": llaves_por_pares(n)}
    pieza = GrafoLlaves(_ancla(ORIGIN), aristas, nodos, params)
    return pieza


# =====================================================================
# El esquema de Diffie-Hellman
# =====================================================================
class EsquemaDH(VGroup):
    """Ana y Beto a los lados, el canal PUBLICO en medio y Eva debajo
    oyendolo todo."""

    def __init__(self, ancla, canal, ana, beto, eva, eva_linea, punto_ana,
                 punto_beto, params, **kwargs):
        super().__init__(ancla, canal, ana, beto, eva_linea, eva, punto_ana,
                         punto_beto, **kwargs)
        self._ancla = ancla                 # el centro del canal
        self.canal = canal
        self.ana = ana
        self.beto = beto
        self.eva = eva                      # circulo + "E"
        self.eva_linea = eva_linea          # punteada roja hasta el canal
        self.punto_ana = punto_ana          # sobre el canal, junto a Ana
        self.punto_beto = punto_beto
        self._params = params

    def _escala_actual(self):
        return self.canal.get_length() / max(self._params["largo_canal"],
                                             _EPS)

    def mensaje(self, texto, desde="ana"):
        """Lo que se grita en publico: Text HUD sobre el canal, junto al
        extremo de quien lo dice (el clip lo mueve/anima)."""
        p = (self.punto_ana if str(desde).lower().startswith("a")
             else self.punto_beto)
        esc = self._escala_actual()
        t = _texto_hud(texto, font_size=22, color=self._params["color_canal"])
        t.scale(esc)
        t.move_to(p.get_center() + UP * 0.35 * esc)
        return t


def esquema_dh(sep=4.2, radio=0.42, color_canal=COLOR_CIFRADO,
               color_persona=COLOR_CLARO, color_eva=COLOR_ATAQUE):
    """El dibujo del clip 4: dos personas gritando por un canal que
    cualquiera oye.

    Todo lo que viaja por el canal es PUBLICO (cian) y Eva lo escucha
    entero; lo unico ambar —privado— vive dentro de cada cabeza.
    """
    sep = float(sep)
    izq, der = LEFT * sep, RIGHT * sep

    def persona(centro, inicial):
        c = Circle(radius=float(radio), stroke_width=2.4,
                   color=color_persona)
        c.set_fill(color_persona, opacity=0.10)
        c.move_to(centro)
        t = _texto_hud(inicial, font_size=24, color=color_persona)
        t.move_to(centro)
        return VGroup(c, t)

    ana = persona(izq, "A")
    beto = persona(der, "B")

    x_canal = sep - float(radio) - 0.22
    canal = DoubleArrow(LEFT * x_canal, RIGHT * x_canal, buff=0.0,
                        stroke_width=2.4, color=color_canal,
                        tip_length=0.18)

    c_eva = Circle(radius=float(radio) * 0.82, stroke_width=2.4,
                   color=color_eva)
    c_eva.set_fill(color_eva, opacity=0.10)
    c_eva.move_to(DOWN * 1.6)
    t_eva = _texto_hud("E", font_size=22, color=color_eva)
    t_eva.move_to(c_eva.get_center())
    eva = VGroup(c_eva, t_eva)
    eva_linea = DashedLine(c_eva.get_top(), ORIGIN, stroke_width=1.8,
                           color=color_eva, dash_length=0.10)
    eva_linea.set_stroke(opacity=0.6)

    punto_ana = _ancla(LEFT * (x_canal - 0.75))
    punto_beto = _ancla(RIGHT * (x_canal - 0.75))

    params = {"sep": sep, "largo_canal": 2.0 * x_canal,
              "color_canal": color_canal}
    return EsquemaDH(_ancla(ORIGIN), canal, ana, beto, eva, eva_linea,
                     punto_ana, punto_beto, params)


# =====================================================================
# La caja con un numero
# =====================================================================
class CajaNumero(_Alineable):
    """Caja rotulada con un numero grande: la unidad de rotulacion del
    curso (n, phi, d, A, B, el secreto...)."""

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
        t.move_to(self.valor.get_center())
        return t

    def actualizar(self, valor):
        """Cambia el numero EN SITIO (misma posicion, misma escala) y
        devuelve el mobject nuevo; el viejo sale del grupo."""
        nuevo = self._nuevo_valor(valor)
        self.remove(self.valor)
        self.add(nuevo)
        self.valor = nuevo
        self._params["valor"] = valor
        return nuevo


def caja_numero(etiqueta, valor, color=COLOR_CIFRADO, ancho=1.9, alto=1.05):
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
# La curva de las divisiones
# =====================================================================
class CurvaDivisiones(VGroup):
    """Cuantas divisiones cuesta factorizar contra los digitos del numero,
    con el eje y en log10; `.en(d)` sobre geometria ACTUAL."""

    def __init__(self, ancla, ejes, curva, ticks, etiquetas_x, params,
                 **kwargs):
        super().__init__(ancla, ejes, curva, ticks, etiquetas_x, **kwargs)
        self._ancla = ancla                 # origen de los ejes
        self.ejes = ejes
        self.curva = curva
        self.ticks = ticks
        self.etiquetas_x = etiquetas_x
        self._params = params

    def _escala_actual(self):
        return self.ejes[0].get_length() / max(self._params["ancho"], _EPS)

    def en(self, digitos):
        """Punto de escena sobre la curva para un n de `digitos` digitos."""
        p = self._params
        esc = self._escala_actual()
        fx = min(max(float(digitos) / p["d_max"], 0.0), 1.0)
        fy = min(max(exponente_divisiones(digitos) / p["y_max"], 0.0), 1.0)
        return (self._ancla.get_center() + RIGHT * fx * p["ancho"] * esc
                + UP * fy * p["alto"] * esc)


def curva_divisiones(d_max=620, ancho=5.0, alto=2.6):
    """La cuenta que no perdona: para factorizar un n de d digitos por
    fuerza bruta hay que dividir hasta la raiz, ~10^(d/2).

    El eje y ya es logaritmico (por eso la curva sale recta): cada 100
    digitos del modulo son 50 ordenes de magnitud mas de trabajo. Un RSA
    de 2048 bits tiene 617 digitos: 10^308 divisiones, mas que atomos hay
    en el universo observable.
    """
    d_max, ancho, alto = float(d_max), float(ancho), float(alto)
    y_max = exponente_divisiones(d_max)
    origen = np.array([-ancho / 2.0, -alto / 2.0, 0.0])

    ejes = VGroup(
        Line(origen, origen + RIGHT * ancho, stroke_width=2.0,
             color=COLOR_EJE),
        Line(origen, origen + UP * alto, stroke_width=2.0, color=COLOR_EJE))

    pts = []
    for i in range(61):
        d = d_max * i / 60.0
        pts.append(origen + RIGHT * (d / d_max) * ancho
                   + UP * (exponente_divisiones(d) / y_max) * alto)
    curva = _poligonal(pts, COLOR_CLARO, 3.0)
    # Ambar abajo (numeros de juguete) -> rojo arriba (RSA de verdad).
    curva.set_stroke(color=[COLOR_CLARO, COLOR_ATAQUE])

    ticks = VGroup()
    for exp in (0, 100, 200, 300):
        m = MathTex(r"10^{%d}" % exp, font_size=20, color=CODE_MUTED)
        m.next_to(origen + UP * (exp / y_max) * alto, LEFT, buff=0.14)
        ticks.add(m)

    etiquetas_x = VGroup()
    for d in (0, 300, 600):
        t = _texto_hud(str(d), font_size=14, color=CODE_MUTED)
        t.next_to(origen + RIGHT * (d / d_max) * ancho, DOWN, buff=0.14)
        etiquetas_x.add(t)

    params = {"d_max": d_max, "y_max": y_max, "ancho": ancho, "alto": alto}
    return CurvaDivisiones(_ancla(origen), ejes, curva, ticks, etiquetas_x,
                           params)


# =====================================================================
# La rejilla del hash
# =====================================================================
class RejillaHash(VGroup):
    """Los 256 bits de SHA-256 en 16x16: la huella que se puede mirar."""

    def __init__(self, ancla, celdas, params, **kwargs):
        super().__init__(ancla, celdas, **kwargs)
        self._ancla = ancla                 # el centro
        self.celdas = celdas
        self._params = params
        self.bits = params["bits"]

    def celda(self, i):
        """La celda del bit i (fila = i // 16, columna = i % 16)."""
        return self.celdas[int(i)]

    def marcar_distintos(self, otros_bits, color=COLOR_ATAQUE):
        """Recolorea EN SITIO las celdas cuyo bit difiere de `otros_bits` y
        devuelve cuantas son (el mismo entero que `bits_distintos`): la
        avalancha, contada sobre el dibujo."""
        otros = np.asarray(otros_bits, dtype=int).ravel()
        if len(otros) != len(self.bits):
            raise ValueError(
                f"marcar_distintos: {len(otros)} bits contra "
                f"{len(self.bits)}")
        cuenta = 0
        for i, (b, o) in enumerate(zip(self.bits, otros)):
            if int(b) != int(o):
                c = self.celdas[i]
                c.set_stroke(color, width=1.0, opacity=1.0)
                c.set_fill(color, opacity=0.9 if int(b) else 0.20)
                cuenta += 1
        return int(cuenta)


def rejilla_hash(bits, color=COLOR_HUELLA, celda=0.17, lado=16):
    """SHA-256 dibujado: 16x16 celdas, una por bit, en orden de lectura.

    De aqui no se vuelve: la huella no guarda el mensaje. Y cambiar una
    sola letra reparte de nuevo la mitad de las celdas (avalancha).
    """
    bits = np.asarray(bits, dtype=int).ravel()
    lado = int(lado)
    if len(bits) != lado * lado:
        raise ValueError(f"rejilla_hash: {len(bits)} bits no forman "
                         f"{lado}x{lado}")
    celda = float(celda)
    l_cuadro = celda * 0.90
    x0 = -(lado - 1) * celda / 2.0
    y0 = (lado - 1) * celda / 2.0

    celdas = VGroup()
    for i, b in enumerate(bits):
        f, c = divmod(i, lado)
        q = Square(side_length=l_cuadro, stroke_width=0.8, color=COLOR_EJE)
        q.set_fill(color, opacity=0.9 if b else 0.08)
        q.move_to(np.array([x0 + c * celda, y0 - f * celda, 0.0]))
        celdas.add(q)

    params = {"bits": bits.copy(), "color": color, "celda": celda,
              "lado": lado}
    return RejillaHash(_ancla(ORIGIN), celdas, params)


# =====================================================================
# El candado
# =====================================================================
class Candado(VGroup):
    """Icono de candado; `.abierto()` / `.cerrado()` mueven el arco."""

    def __init__(self, ancla, arco, cuerpo, params, **kwargs):
        super().__init__(ancla, arco, cuerpo, **kwargs)
        self._ancla = ancla                 # el centro del cuerpo
        self.arco = arco
        self.cuerpo = cuerpo
        self._params = params

    def _escala_actual(self):
        return self.cuerpo.width / max(self._params["ancho_cuerpo"], _EPS)

    def _punto_cerrado(self):
        esc = self._escala_actual()
        return (self.cuerpo.get_top()
                + UP * (self.arco.height / 2.0 - 0.04 * esc))

    def cerrado(self):
        """El arco baja y se asienta sobre el cuerpo. Devuelve self."""
        self.arco.move_to(self._punto_cerrado())
        return self

    def abierto(self):
        """El arco se levanta y se corre: el candado esta abierto.
        Devuelve self."""
        esc = self._escala_actual()
        self.arco.move_to(self._punto_cerrado()
                          + UP * 0.20 * esc + RIGHT * 0.30 * esc)
        return self


def candado(color=COLOR_LLAVE, alto=1.0):
    """El candado del navegador, dibujado a mano: cuerpo redondeado y
    arco. Verde cuando cierra bien, rojo cuando algo falla."""
    alto = float(alto)
    ancho_cuerpo = 0.86 * alto
    alto_cuerpo = 0.56 * alto
    radio_arco = 0.27 * alto

    cuerpo = RoundedRectangle(width=ancho_cuerpo, height=alto_cuerpo,
                              corner_radius=0.09 * alto, stroke_width=2.6,
                              color=color)
    cuerpo.set_fill(color, opacity=0.14)
    cuerpo.move_to(np.array([0.0, -0.12 * alto, 0.0]))

    arco = Arc(radius=radio_arco, start_angle=0.0, angle=PI,
               stroke_width=2.6, color=color)
    arco.move_to(cuerpo.get_top() + UP * (arco.height / 2.0 - 0.04 * alto))

    params = {"ancho_cuerpo": ancho_cuerpo, "alto": alto, "color": color}
    return Candado(_ancla(cuerpo.get_center()), arco, cuerpo, params)


# =====================================================================
# El flujo de cajas
# =====================================================================
class Flujo(VGroup):
    """Cajas encadenadas por flechas: mensaje -> huella -> firma."""

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
    """La cadena del clip 7: cada caja es un paso y la flecha es "de aqui
    sale aquello".

    `pasos` son los rotulos (fuente display, se admiten tildes) y
    `colores` uno por caja (por omision, todos ambar).
    """
    pasos = [str(p) for p in pasos]
    n = _validar("flujo.pasos", len(pasos), 6)
    if colores is None:
        colores = [COLOR_CLARO] * n
    colores = list(colores)
    if len(colores) != n:
        raise ValueError(f"flujo: {len(colores)} colores para {n} pasos")

    ancho_caja, alto_caja, sep = float(ancho_caja), float(alto_caja), float(sep)
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

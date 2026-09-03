# =====================================================================
# CO.DE Academy - sistemas.py
# La libreria del curso 33: "Señales y sistemas", en estilo LIENZO y MUDO.
#
# Dos mitades, como en toda la casa:
#
#   1. NUMERICA. numpy puro, sin manim, determinista. Aqui viven TODAS las
#      cifras que salen en pantalla. Se importa sin manim, que es lo que
#      permite que `studio/tools/sonda_sistemas.py` la verifique.
#   2. DE DIBUJO. Piezas centradas en el origen; NO animan y NO deciden
#      donde van (de eso se encarga `lienzo.encajar`).
#
# QUE CAPA OCUPA, que es la decision editorial del curso: aqui NO se
# explican las transformadas. El curso 32 ya lo hizo. Este cuenta que le
# hace un SISTEMA a una señal, y las transformadas aparecen solo como
# herramienta — la respuesta en frecuencia se calcula con una FFT sin
# volver a contar que es una FFT. La bisagra entre los dos cursos es
# `autovalor()`: una exponencial compleja entra en un sistema lineal y sale
# igual salvo un numero, y ESA es la razon de que las transformadas sirvan
# para algo.
#
# Honestidad: la CIFRA es lo que este render calcula. Un parametro elegido
# (el orden de un filtro, la constante de un polo, el numero de muestras)
# va con etiqueta APAGADA por mucho que este escrito aqui.
# =====================================================================
import numpy as np

SEMILLA = 33              # el numero del curso, para no elegirlo dos veces

try:
    from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Circle, DashedVMobject,
                       Dot, Line, Polygon, Rectangle, RoundedRectangle,
                       VGroup, VMobject)

    import lienzo as _lz
    _HAY_MANIM = True
except Exception:          # la sonda corre sin manim
    _HAY_MANIM = False


# =====================================================================
#  MITAD NUMERICA
# =====================================================================

# --- 01 · El impulso ---------------------------------------------------
def impulso(N=64, n0=0):
    """Delta discreta: vale 1 en n0 y 0 en todo lo demas."""
    x = np.zeros(int(N))
    x[int(n0)] = 1.0
    return x


def pulso_de_area(ancho, N=1024, T=4.0):
    """Un rectangulo de anchura `ancho` cuya AREA DIBUJADA vale 1.

    Es la pieza 01 entera: al estrechar el pulso su altura sube en la
    misma proporcion y el area no se mueve. El impulso es el limite de
    esa familia, no una señal infinitamente alta porque si.

    La altura NO es 1/ancho, y esa es la unica sutileza: sobre una malla
    discreta el rectangulo se queda en el numero ENTERO de muestras que
    caben dentro, asi que un pulso de 0.1 con paso 0.0039 mide en
    realidad 0.0977 de ancho y con altura 1/0.1 su area sale 0.9766. Lo
    cazo la sonda. La altura se calcula contra las muestras que de verdad
    se dibujan, de modo que lo que se mide en pantalla es exactamente 1 —
    que es lo que la pieza afirma."""
    t = np.linspace(-T / 2, T / 2, int(N), endpoint=False)
    dentro = np.abs(t) < float(ancho) / 2
    cuantas = int(np.sum(dentro))
    if cuantas == 0:
        raise ValueError(
            f"un pulso de {ancho} no coge ni una muestra con N={N} y "
            f"T={T}: sube N o ensancha el pulso")
    dt = float(t[1] - t[0])
    x = np.where(dentro, 1.0 / (cuantas * dt), 0.0)
    return t, x


def area(t, x):
    """Integral por rectangulos. Se MIDE sobre lo que se dibuja."""
    t = np.asarray(t, dtype=float)
    return float(np.sum(np.asarray(x, dtype=float)) * (t[1] - t[0]))


# --- 02 · La respuesta al impulso --------------------------------------
def h_amortiguada(N=48, tau=9.0, f=0.11, retardo=0):
    """Una respuesta al impulso tipica: oscila y se apaga.

    `tau`, `f` y el retardo son parametros ELEGIDOS (etiqueta apagada).
    Lo que se mide sobre ella —cuanto dura, cuanto suma, que hace en
    frecuencia— si es medida."""
    n = np.arange(int(N))
    h = np.exp(-(n - retardo) / float(tau)) * np.cos(2 * np.pi * f
                                                     * (n - retardo))
    h[n < retardo] = 0.0
    return h


def cola(h, umbral=0.01):
    """Cuantas muestras tarda la respuesta en caer por debajo del
    `umbral` de su maximo y no volver a subir. Es "cuanto dura el eco"."""
    h = np.abs(np.asarray(h, dtype=float))
    grande = np.where(h > float(umbral) * np.max(h))[0]
    return int(grande[-1] + 1) if grande.size else 0


def duracion(x, umbral=0.01):
    """CUANTAS muestras valen algo. No es lo mismo que `cola`.

    `cola` mide DONDE se acaba la senal contando desde el origen, asi que
    incluye los ceros de delante: un impulso colocado en la muestra 20
    tiene cola 21 y dura 1. Las dos cifras son utiles y son distintas, y
    confundirlas pone en pantalla un numero falso — paso en la pieza 01,
    que rotulaba "muestra que dura" sobre un 21."""
    x = np.abs(np.asarray(x, dtype=float))
    pico = np.max(x)
    if pico <= 0:
        return 0
    return int(np.sum(x > float(umbral) * pico))


# --- 03 · La convolucion -----------------------------------------------
def convolucion(x, h):
    """Convolucion completa, escrita a mano.

    Se implementa sumando en vez de llamar a `np.convolve` a proposito:
    es la operacion que la pieza DIBUJA (deslizar, multiplicar, sumar), y
    la sonda comprueba que coincide con numpy. Si algun dia divergen, es
    que el dibujo esta contando otra cosa que la cuenta."""
    x = np.asarray(x, dtype=float)
    h = np.asarray(h, dtype=float)
    y = np.zeros(x.size + h.size - 1)
    for k in range(h.size):
        y[k:k + x.size] += h[k] * x
    return y


def solape(x, h, k):
    """El producto punto a punto en el instante `k` del deslizamiento.

    Devuelve (indices, producto, suma): lo que hay que dibujar en ese
    fotograma de la animacion y el valor que va a la salida."""
    x = np.asarray(x, dtype=float)
    h = np.asarray(h, dtype=float)
    prod = np.zeros(x.size)
    for i in range(x.size):
        j = int(k) - i
        if 0 <= j < h.size:
            prod[i] = x[i] * h[j]
    return np.arange(x.size), prod, float(np.sum(prod))


def largo_convolucion(n, m):
    """N + M - 1. La salida dura mas que cualquiera de las dos entradas,
    y eso es medio curso de senales."""
    return int(n) + int(m) - 1


# --- 04 · El escalon ---------------------------------------------------
def escalon(N=64, n0=0):
    x = np.zeros(int(N))
    x[int(n0):] = 1.0
    return x


def respuesta_escalon(h):
    """La respuesta al escalon es la suma acumulada de la respuesta al
    impulso. No hace falta volver a medir el sistema: se deduce."""
    return np.cumsum(np.asarray(h, dtype=float))


def valor_final(h):
    """A donde se asienta la respuesta al escalon: la suma de h."""
    return float(np.sum(np.asarray(h, dtype=float)))


# --- 05 · Linealidad ---------------------------------------------------
def error_superposicion(h, x1, x2, a=1.0, b=1.0):
    """Cuanto se aparta el sistema de la superposicion, en % del pico.

    En un sistema LINEAL sale cero (redondeo del coma flotante). Es la
    misma cuenta que en la pieza 18 da un numero enorme, y por eso la
    pieza 05 y la 18 son la misma medida con dos sistemas distintos."""
    juntas = convolucion(a * np.asarray(x1) + b * np.asarray(x2), h)
    sueltas = a * convolucion(x1, h) + b * convolucion(x2, h)
    pico = max(float(np.max(np.abs(sueltas))), 1e-18)
    return float(np.max(np.abs(juntas - sueltas)) / pico * 100.0)


def error_superposicion_saturado(umbral, x1, x2, a=1.0, b=1.0):
    """Lo mismo, con una caja que satura. Aqui NO sale cero."""
    juntas = saturar(a * np.asarray(x1) + b * np.asarray(x2), umbral)
    sueltas = (a * saturar(x1, umbral) + b * saturar(x2, umbral))
    pico = max(float(np.max(np.abs(sueltas))), 1e-18)
    return float(np.max(np.abs(juntas - sueltas)) / pico * 100.0)


# --- 06 · Invarianza en el tiempo --------------------------------------
def error_invarianza(h, x, retardo):
    """Retrasar la entrada tiene que retrasar la salida y NADA MAS.

    Se comparan las dos senales en la zona donde las dos existen, para no
    medir el efecto del borde en vez del del sistema."""
    x = np.asarray(x, dtype=float)
    d = int(retardo)
    y = convolucion(x, h)
    y_retrasada = convolucion(np.concatenate([np.zeros(d), x]), h)
    a, b = y[:y.size - d], y_retrasada[d:d + y.size - d]
    pico = max(float(np.max(np.abs(a))), 1e-18)
    return float(np.max(np.abs(a - b)) / pico * 100.0)


# --- 07 · Causalidad ---------------------------------------------------
def muestras_antes_de_cero(h, n0):
    """Cuantas muestras de la respuesta caen ANTES del golpe.

    Un sistema causal no puede tener ninguna: responder antes de que
    llegue la causa es adivinar el futuro."""
    h = np.asarray(h, dtype=float)
    return int(np.sum(np.abs(h[:int(n0)]) > 1e-12))


def h_no_causal(N=48, centro=16, ancho=5.0):
    """Una campana centrada: preciosa, util en diferido... e imposible en
    tiempo real, porque empieza antes del instante cero."""
    n = np.arange(int(N))
    return np.exp(-((n - centro) / float(ancho)) ** 2)


# --- 08 · Estabilidad --------------------------------------------------
def suma_absoluta(h):
    """La suma de |h[n]|. Si es finita, el sistema es estable BIBO:
    entrada acotada, salida acotada. Es el criterio entero."""
    return float(np.sum(np.abs(np.asarray(h, dtype=float))))


def h_geometrica(a, N=60):
    """h[n] = a^n. Con |a| < 1 se apaga y suma 1/(1-a); con |a| > 1 no."""
    return np.power(float(a), np.arange(int(N)))


def cota_salida(h, amplitud=1.0):
    """La salida no puede pasar de amplitud * suma|h|, y esa cota SE
    ALCANZA con la entrada que copia el signo de h."""
    return float(amplitud) * suma_absoluta(h)


def peor_entrada(h, N=None):
    """La entrada acotada que mas estira la salida: sign(h) del reves."""
    h = np.asarray(h, dtype=float)
    x = np.sign(h[::-1])
    x[x == 0] = 1.0
    return x if N is None else x[:int(N)]


# --- 09 · En cascada ---------------------------------------------------
def cascada(h1, h2):
    """Dos sistemas encadenados son UNO, cuya respuesta al impulso es la
    convolucion de las dos."""
    return convolucion(h1, h2)


def error_conmutar(h1, h2, x):
    """Cambiar el orden de dos cajas no cambia la salida. Sale cero, y no
    es evidente: es que la convolucion conmuta."""
    a = convolucion(convolucion(x, h1), h2)
    b = convolucion(convolucion(x, h2), h1)
    pico = max(float(np.max(np.abs(a))), 1e-18)
    return float(np.max(np.abs(a - b)) / pico * 100.0)


# --- 10 · Realimentacion -----------------------------------------------
def lazo_cerrado(k, N=60, polo=0.6):
    """Respuesta al impulso del lazo y[n] = x[n] + k*polo*y[n-1].

    Cerrar el lazo cambia DONDE esta el polo: pasa de `polo` a k*polo. Con
    k grande el sistema deja de apagarse. `polo` y `k` son parametros
    elegidos; lo que se mide es que le pasa a la respuesta."""
    y = np.zeros(int(N))
    y[0] = 1.0
    for n in range(1, int(N)):
        y[n] = float(k) * float(polo) * y[n - 1]
    return y


def ganancia_lazo(k, polo=0.6):
    """El polo del lazo cerrado. Cruza 1 y el sistema se va."""
    return float(k) * float(polo)


# --- 11 · La ecuacion en diferencias -----------------------------------
def filtrar(b, a, x):
    """y[n] = sum b[i] x[n-i] - sum a[j] y[n-j], con a[0] = 1.

    La receta recursiva: cada muestra de salida se construye con las
    entradas recientes y con las SALIDAS anteriores. Escrita a mano
    porque es lo que la pieza dibuja."""
    b = np.asarray(b, dtype=float)
    a = np.asarray(a, dtype=float)
    x = np.asarray(x, dtype=float)
    if not np.isclose(a[0], 1.0):
        b, a = b / a[0], a / a[0]
    y = np.zeros(x.size)
    for n in range(x.size):
        acc = 0.0
        for i in range(b.size):
            if n - i >= 0:
                acc += b[i] * x[n - i]
        for j in range(1, a.size):
            if n - j >= 0:
                acc -= a[j] * y[n - j]
        y[n] = acc
    return y


def h_de_ecuacion(b, a, N=60):
    """La respuesta al impulso que sale de la receta. Une la pieza 11 con
    la 02: son dos formas de decir lo mismo."""
    return filtrar(b, a, impulso(N))


# --- 12 · Autofunciones (la bisagra con el curso 32) -------------------
def exponencial(w, N=64):
    """exp(j w n): la señal que un sistema lineal NO deforma."""
    return np.exp(1j * float(w) * np.arange(int(N)))


def autovalor(h, w):
    """H(e^{jw}) = sum h[n] e^{-jwn}: el numero por el que el sistema
    multiplica a esa exponencial.

    Esta funcion ES la razon de ser del curso 32. La exponencial entra y
    sale igual salvo este factor; por eso descomponer una señal en
    exponenciales convierte un sistema entero en una multiplicacion."""
    h = np.asarray(h, dtype=float)
    n = np.arange(h.size)
    return complex(np.sum(h * np.exp(-1j * float(w) * n)))


def error_autofuncion(h, w, N=200):
    """Cuanto se aparta la salida de ser la entrada por el autovalor.

    Se mide en el TRAMO ESTACIONARIO (a partir de la longitud de h): al
    principio la convolucion todavia esta llenandose y la igualdad no
    puede cumplirse. Medir ahi daria un error grande y falso."""
    h = np.asarray(h, dtype=float)
    x = exponencial(w, N)
    y = np.convolve(x, h)[:N]
    esperada = autovalor(h, w) * x
    desde = h.size
    d = np.abs(y[desde:] - esperada[desde:])
    return float(np.max(d) / max(np.max(np.abs(esperada[desde:])), 1e-18)
                 * 100.0)


# --- 13 · La respuesta en frecuencia -----------------------------------
def respuesta_frecuencia(h, N=1024):
    """(w, |H|, fase) sobre media circunferencia."""
    h = np.asarray(h, dtype=float)
    H = np.fft.rfft(h, n=int(N))
    w = np.fft.rfftfreq(int(N), d=1.0 / (2 * np.pi))
    return w, np.abs(H), np.unwrap(np.angle(H))


def ganancia_medida(h, w, N=400):
    """La ganancia MEDIDA metiendo un tono y midiendo lo que sale.

    Es la comprobacion honrada de la pieza 13: se mete un coseno, se mira
    la amplitud de la salida ya asentada y se compara con |H(w)|. Que
    coincidan no es trivial — es la definicion de respuesta en frecuencia
    ganandose el nombre."""
    h = np.asarray(h, dtype=float)
    n = np.arange(int(N))
    x = np.cos(float(w) * n)
    y = np.convolve(x, h)[:int(N)]
    tramo = y[h.size + 20:]
    return float((np.max(tramo) - np.min(tramo)) / 2.0)


# --- 14 · Fase y retardo de grupo --------------------------------------
def retardo_grupo(h, N=1024):
    """-d(fase)/dw, en muestras. Es cuanto se retrasa la ENVOLVENTE."""
    w, _, fase = respuesta_frecuencia(h, N)
    return w[:-1], -np.diff(fase) / np.diff(w)


def deformar_fases(x, giro):
    """La misma señal con las MISMAS amplitudes y las fases movidas.

    Es la pieza 14: el espectro de amplitud no cambia ni un poco y la
    señal deja de parecerse a si misma. Lo que se ve no lo dice el modulo
    del espectro.

    Los extremos NO se giran, y ahi estaba el fallo. Para que la salida
    sea real, el bin 0 y el de Nyquist tienen que ser reales; `irfft` los
    fuerza tirando su parte imaginaria, asi que girarlos CAMBIA su modulo
    y la pieza afirmaria en pantalla algo falso. Medido con dos tonos y
    giro 6: el bin de Nyquist pasaba de 0.4857 a 0.1014 mientras el rotulo
    decia "las mismas amplitudes". Dejandolos quietos, el espectro de
    amplitud se conserva hasta el ultimo bit."""
    x = np.asarray(x, dtype=float)
    X = np.fft.rfft(x)
    k = np.arange(X.size)
    giros = np.exp(1j * float(giro) * k * k / X.size)
    giros[0] = 1.0
    if x.size % 2 == 0:
        giros[-1] = 1.0        # el bin de Nyquist solo existe si N es par
    return np.fft.irfft(X * giros, n=x.size)


# --- 15 · Resonancia ---------------------------------------------------
def resonador(f0, Q, N=400):
    """Respuesta al impulso de un resonador de frecuencia f0 y calidad Q.

    f0 en ciclos por muestra. `f0` y `Q` son parametros ELEGIDOS."""
    w0 = 2 * np.pi * float(f0)
    r = np.exp(-w0 / (2.0 * float(Q)))
    b = np.array([1.0 - r])
    a = np.array([1.0, -2 * r * np.cos(w0), r * r])
    return h_de_ecuacion(b, a, N)


def amplificacion(h, f0, fuera=None, N=1024):
    """Cuantas veces mas responde el sistema en f0 que fuera de ella."""
    w, mag, _ = respuesta_frecuencia(h, N)
    en = float(np.interp(2 * np.pi * float(f0), w, mag))
    ref = float(np.interp(2 * np.pi * float(fuera if fuera is not None
                                            else f0 / 3.0), w, mag))
    return en / max(ref, 1e-18)


# --- 16 · Transitorio y permanente -------------------------------------
def tiempo_asentamiento(y, tolerancia=0.02):
    """Cuantas muestras tarda la salida en quedarse dentro de la banda de
    tolerancia alrededor de su valor final y NO volver a salir."""
    y = np.asarray(y, dtype=float)
    final = float(y[-1])
    fuera = np.where(np.abs(y - final) > abs(final) * float(tolerancia))[0]
    return int(fuera[-1] + 1) if fuera.size else 0


def parte_permanente(h, w, N=400):
    """La salida que quedaria si el transitorio ya se hubiera ido: la
    entrada por el autovalor."""
    A = autovalor(h, w)
    n = np.arange(int(N))
    return np.real(A * np.exp(1j * float(w) * n))


# --- 17 · Un filtro ----------------------------------------------------
def paso_bajo(fc, M=61):
    """Sinc enventanado con Hamming. `fc` en ciclos por muestra."""
    M = int(M) | 1                       # impar: fase lineal exacta
    n = np.arange(M) - (M - 1) / 2.0
    h = 2 * float(fc) * np.sinc(2 * float(fc) * n)
    h *= np.hamming(M)
    return h / np.sum(h)


def atenuacion_db(h, w, N=4096):
    """Cuantos decibelios se lleva el filtro a esa frecuencia.

    Se rotula la ATENUACION A UNA FRECUENCIA CONCRETA y no la profundidad
    del rizado: lo que depende de la malla no se rotula (leccion del
    curso 27)."""
    ws, mag, _ = respuesta_frecuencia(h, N)
    g = float(np.interp(float(w), ws, mag))
    return float(20.0 * np.log10(max(g, 1e-18)))


def dos_tonos(f1, f2, N=400, a1=1.0, a2=1.0):
    n = np.arange(int(N))
    return (a1 * np.cos(2 * np.pi * float(f1) * n)
            + a2 * np.cos(2 * np.pi * float(f2) * n))


def amplitud_de_tono(x, f, desde=0):
    """La amplitud de la componente de frecuencia `f` en la señal.

    Se mide con el producto interno contra el tono, que es exacto cuando
    la frecuencia cae en la malla y honrado cuando no."""
    x = np.asarray(x, dtype=float)[int(desde):]
    n = np.arange(x.size)
    c = np.sum(x * np.exp(-2j * np.pi * float(f) * n))
    return float(2.0 * np.abs(c) / x.size)


# --- 18 · Cuando deja de ser lineal ------------------------------------
def saturar(x, umbral=0.7):
    """La caja que recorta. Es el sistema no lineal mas comun del mundo:
    todo amplificador lo hace cuando se le pide demasiado."""
    return np.clip(np.asarray(x, dtype=float), -float(umbral),
                   float(umbral))


def armonicos(x, f0, cuantos=6):
    """La amplitud de f0 y de sus primeros armonicos."""
    return np.array([amplitud_de_tono(x, float(f0) * k)
                     for k in range(1, int(cuantos) + 1)])


def distorsion_armonica(x, f0, cuantos=8):
    """THD en %: cuanta señal hay en los armonicos que NO entraron.

    Un tono entra solo, y salen tonos a 2f0, 3f0... que nadie metio. Esa
    es la definicion operativa de "no lineal", y es medible."""
    a = armonicos(x, f0, cuantos)
    return float(np.sqrt(np.sum(a[1:] ** 2)) / max(a[0], 1e-18) * 100.0)


# =====================================================================
#  MITAD DE DIBUJO
# =====================================================================

def _exige_manim():
    if not _HAY_MANIM:
        raise RuntimeError(
            "las piezas de dibujo de sistemas.py necesitan manim y lienzo; "
            "la mitad numerica se importa sin ellos a proposito")


TRAZO = 3.0
TRAZO_FINO = 1.6
TRAZO_PELO = 1.0


def caja(texto="h", ancho=1.5, alto=0.95, color=None, acento=True):
    """EL dibujo de este curso: el sistema como una caja con un nombre.

    Relleno del color del FONDO y opaco, no transparente: asi tapa lo que
    pase por detras y las flechas no se ven cruzarla. (El ambar traslucido
    sobre este azul da verde oliva — medido en el curso 31.)"""
    _exige_manim()
    color = color or (_lz.AMBAR if acento else _lz.APAGADO)
    marco = RoundedRectangle(width=ancho, height=alto, corner_radius=0.10,
                             stroke_color=color, stroke_width=TRAZO,
                             fill_color=_lz.AZUL, fill_opacity=1.0)
    rot = _lz.rotulo(texto, color=color, font_size=_lz.ROTULO)
    if rot.width > ancho - 0.22:
        rot.scale((ancho - 0.22) / rot.width)
    rot.move_to(marco.get_center())
    return VGroup(marco, rot)


def flecha(desde, hasta, color=None, grosor=TRAZO_FINO):
    """Una flecha de senal entre dos puntos."""
    _exige_manim()
    return Arrow(desde, hasta, buff=0.0, stroke_width=grosor,
                 color=color or _lz.APAGADO,
                 max_tip_length_to_length_ratio=0.16)


def cadena(cajas, largo=0.85, color=None):
    """Cajas en fila unidas por flechas, con entrada y salida.

    Devuelve (grupo, entrada, salida): los dos puntos de los extremos, que
    es lo que hacen falta para colgar de ahi las señales."""
    _exige_manim()
    fila = VGroup(*cajas).arrange(RIGHT, buff=largo)
    piezas = VGroup(fila)
    p_ini = fila[0].get_left() + LEFT * largo
    p_fin = fila[-1].get_right() + RIGHT * largo
    piezas.add(flecha(p_ini, fila[0].get_left(), color))
    for a, b in zip(cajas, cajas[1:]):
        piezas.add(flecha(a.get_right(), b.get_left(), color))
    piezas.add(flecha(fila[-1].get_right(), p_fin, color))
    return piezas, p_ini, p_fin


def lazo(caja_directa, caja_vuelta=None, ancho=3.2, alto=1.5, color=None):
    """El diagrama del lazo cerrado: la salida vuelve a la entrada.

    Es el unico dibujo del curso con una linea que se muerde la cola, y
    esa forma ES la pieza 10."""
    _exige_manim()
    color = color or _lz.APAGADO
    g = VGroup(caja_directa)
    izq = caja_directa.get_left() + LEFT * ancho / 3
    der = caja_directa.get_right() + RIGHT * ancho / 3
    abajo = -alto / 2 + caja_directa.get_bottom()[1]
    nodo = Circle(radius=0.11, stroke_color=color, stroke_width=TRAZO_FINO,
                  fill_color=_lz.AZUL, fill_opacity=1.0)
    nodo.move_to(izq)
    g.add(nodo)
    g.add(flecha(izq + LEFT * 0.75, izq + LEFT * 0.11, color))
    g.add(flecha(izq + RIGHT * 0.11, caja_directa.get_left(), color))
    g.add(flecha(caja_directa.get_right(), der, color))
    vuelta = VMobject(stroke_color=color, stroke_width=TRAZO_FINO)
    vuelta.set_points_as_corners([
        der, [der[0], abajo, 0], [izq[0], abajo, 0], izq + DOWN * 0.11])
    g.add(vuelta)
    if caja_vuelta is not None:
        caja_vuelta.move_to([(der[0] + izq[0]) / 2, abajo, 0])
        g.add(caja_vuelta)
    return g


def tallos(valores, ancho=4.8, alto=2.4, color=None, grosor=TRAZO_FINO,
           punta=0.045, rango_y=None):
    """Una secuencia discreta: una raya por muestra y su punto.

    Unir las muestras con una curva sugiere que hay algo entre ellas, y en
    una senal discreta no lo hay."""
    _exige_manim()
    v = np.asarray(valores, dtype=float)
    n = v.size
    y0, y1 = rango_y if rango_y else (min(0.0, float(v.min())),
                                      float(v.max()) or 1.0)
    dy = (y1 - y0) or 1.0
    paso = ancho / max(n - 1, 1)
    g = VGroup()
    base = -alto / 2 + (0.0 - y0) / dy * alto
    for i, vi in enumerate(v):
        x = -ancho / 2 + i * paso
        y = -alto / 2 + (vi - y0) / dy * alto
        g.add(Line([x, base, 0], [x, y, 0],
                   stroke_color=color or _lz.TINTA, stroke_width=grosor))
        if punta:
            g.add(Dot([x, y, 0], radius=punta, color=color or _lz.TINTA))
    return g


def traza(x, y, ancho=4.8, alto=2.4, color=None, grosor=TRAZO,
          rango_y=None, rango_x=None, escalones=False):
    """Una serie continua dentro de una caja. Devuelve (mobject, punto)."""
    _exige_manim()
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x0, x1 = rango_x if rango_x else (float(x.min()), float(x.max()))
    y0, y1 = rango_y if rango_y else (float(y.min()), float(y.max()))
    dx = (x1 - x0) or 1.0
    dy = (y1 - y0) or 1.0

    def punto(xi, yi):
        return np.array([(float(xi) - x0) / dx * ancho - ancho / 2,
                         (float(yi) - y0) / dy * alto - alto / 2, 0.0])

    if escalones:
        puntos = []
        for i in range(len(x)):
            puntos.append(punto(x[i], y[i]))
            if i + 1 < len(x):
                puntos.append(punto(x[i + 1], y[i]))
    else:
        puntos = [punto(x[i], y[i]) for i in range(len(x))]
    linea = VMobject(stroke_color=color or _lz.TINTA, stroke_width=grosor)
    linea.set_points_as_corners(puntos)
    return linea, punto


def cero(ancho=4.8, y=0.0, color=None, grosor=TRAZO_PELO):
    _exige_manim()
    return Line([-ancho / 2, y, 0], [ancho / 2, y, 0],
                stroke_color=color or _lz.LINEA, stroke_width=grosor)


def banda(y_centro, semiancho, punto, ancho=4.8, color=None):
    """La banda de tolerancia de la pieza 16: dos discontinuas."""
    _exige_manim()
    g = VGroup()
    for v in (y_centro - semiancho, y_centro + semiancho):
        y = punto(0, v)[1]
        ln = Line([-ancho / 2, y, 0], [ancho / 2, y, 0],
                  stroke_color=color or _lz.LINEA, stroke_width=TRAZO_PELO)
        g.add(DashedVMobject(ln, num_dashes=30, dashed_ratio=0.45))
    return g

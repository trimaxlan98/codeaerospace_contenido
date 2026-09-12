# =====================================================================
# CO.DE Academy - especiales.py
# La libreria del curso 34: "Funciones con nombre propio", VERTICAL 9:16
# en estilo LIENZO.
#
# Dos mitades, como en toda la casa:
#
#   1. NUMERICA. numpy puro, sin manim, determinista. Aqui viven TODAS
#      las cifras que salen en pantalla. Se importa sin manim, que es lo
#      que permite que `studio/tools/sonda_especiales.py` la verifique.
#   2. DE DIBUJO. Piezas centradas en el origen; NO animan y NO deciden
#      donde van (de eso se encarga `lienzo.encajar`).
#
# QUE CAPA OCUPA, que es la decision editorial del curso:
#
#   El curso 11 (naturaleza) cuenta que patron sale de repetir una regla.
#   El 12 (caos) cuenta cuando esa iteracion deja de ser predecible.
#   El 26 (fractales) cuenta la autosemejanza y la dimension.
#   El 32 cuenta como se cambia de dominio, y el 33 que hace un sistema.
#
#   Este cuenta LAS FUNCIONES: las que tienen nombre propio porque
#   ninguna combinacion de las elementales hacia su trabajo. Cada pieza
#   presenta UNA, con el problema que la obligo a existir y UNA cifra que
#   solo ella sabe dar. No se explica caos, ni fractales, ni
#   transformadas: se citan.
#
# POR QUE NO HAY scipy AQUI, que es la pregunta obvia:
#
#   La imagen de render no lo trae (ver requirements.txt), asi que gamma,
#   Bessel, Airy, las elipticas y zeta se implementan a mano con numpy.
#   Eso no es un apano: es lo que hace que la sonda tenga algo que
#   demostrar. Cada una se verifica contra su valor conocido y contra la
#   ecuacion que la define (Ai'' = x*Ai, la recurrencia de Bessel, la
#   reflexion de Euler), que es justo lo que un `import scipy` te ahorra
#   comprobar y por tanto te ahorra entender.
#
# Honestidad: la CIFRA es lo que este render calcula. Un parametro
# elegido (el numero de terminos, la semilla, el achatamiento de la
# Tierra que viene de WGS84) va con etiqueta APAGADA por mucho que este
# escrito aqui.
# =====================================================================
import numpy as np

SEMILLA = 34              # el numero del curso, para no elegirlo dos veces

try:
    from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Circle, DashedVMobject,
                       Dot, Line, VGroup, VMobject)

    import lienzo as _lz
    _HAY_MANIM = True
except Exception:          # la sonda corre sin manim
    _HAY_MANIM = False


# =====================================================================
#  MITAD NUMERICA
# =====================================================================

# --- 01 · GAMMA -------------------------------------------------------
# Aproximacion de Lanczos (g=7, n=9). Da ~15 cifras en el semiplano
# derecho y la formula de reflexion cubre el izquierdo, que es donde
# estan los polos y donde esta la gracia de la pieza.
_LANCZOS = np.array([
    0.99999999999980993, 676.5203681218851, -1259.1392167224028,
    771.32342877765313, -176.61502916214059, 12.507343278686905,
    -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7])


def gamma(x):
    """Gamma de Euler para reales. Vectorizada. Infinito en los polos.

    En 0, -1, -2, ... la funcion NO vale nada: el limite es +inf por un
    lado y -inf por el otro. Se devuelve `nan` en el entero exacto para
    que quien dibuje tenga que partir la curva en ramas en vez de unir
    dos infinitos con una raya (que es la forma clasica de dibujar una
    mentira: parece que gamma pasa por ahi)."""
    x = np.asarray(x, dtype=float)
    escalar = x.ndim == 0
    x = np.atleast_1d(x).astype(float)
    y = np.empty_like(x)
    polo = (x <= 0) & (np.abs(x - np.round(x)) < 1e-12)
    izq = (x < 0.5) & ~polo
    der = ~izq & ~polo
    if np.any(der):
        z = x[der] - 1.0
        s = np.full_like(z, _LANCZOS[0])
        for i in range(1, 9):
            s = s + _LANCZOS[i] / (z + i)
        t = z + 7.5
        y[der] = (np.sqrt(2 * np.pi) * t ** (z + 0.5) * np.exp(-t) * s)
    if np.any(izq):
        # Reflexion de Euler: G(x)G(1-x) = pi / sin(pi x)
        y[izq] = np.pi / (np.sin(np.pi * x[izq]) * gamma(1.0 - x[izq]))
    y[polo] = np.nan
    return float(y[0]) if escalar else y


def factorial(n):
    """n! calculado como producto, para comparar con gamma(n+1)."""
    n = int(n)
    r = 1.0
    for k in range(2, n + 1):
        r *= k
    return r


def curva_gamma(x0=-3.6, x1=4.3, N=4000, recorte=14.0, piso=None):
    """Gamma partida en RAMAS por sus polos, ya recortada en altura.

    Devuelve una lista de (x, y). Recortar los PUNTOS antes de dibujar,
    y no fiar el recorte al `rango_y` de la caja: una rama que se va a
    1e12 manda la polilinea kilometros fuera del cuadro y el guardian de
    legibilidad aborta con un mensaje que no señala la causa (cazado en
    el curso 32).

    `piso` recorta por abajo con un valor DISTINTO del de arriba, y hace
    falta: gamma es asimetrica (sube a 6 en x=4 y su rama negativa solo
    baja a -3.54), asi que un recorte simetrico obliga a un cuadro el
    doble de alto de lo necesario. Con el recorte simetrico a 4.0, la
    curva se cortaba por debajo del punto de 3! y el dibujo afirmaba que
    la curva NO pasa por el factorial que dice enhebrar."""
    ramas = []
    techo = float(recorte)
    suelo = -techo if piso is None else float(piso)
    cortes = [c for c in np.arange(np.ceil(x0), 0.5, 1.0)]
    bordes = [x0] + [float(c) for c in cortes] + [x1]
    for a, b in zip(bordes[:-1], bordes[1:]):
        if b - a < 1e-6:
            continue
        eps = min(0.012, (b - a) / 40.0)
        xs = np.linspace(a + eps, b - eps, max(int(N * (b - a) / (x1 - x0)), 40))
        ys = gamma(xs)
        dentro = (ys <= techo) & (ys >= suelo)
        if not np.any(dentro):
            continue
        # Un solo tramo contiguo por rama: los extremos se recortan, no
        # se agujerea el medio (gamma no tiene huecos dentro de una rama).
        i0, i1 = np.argmax(dentro), len(dentro) - np.argmax(dentro[::-1])
        ramas.append((xs[i0:i1], ys[i0:i1]))
    return ramas


# --- 02 · LAMBERT W ---------------------------------------------------
def lambert_w(y, iteraciones=60):
    """Rama principal de W: el x que cumple x*e^x = y. Vectorizada.

    Halley desde una semilla logaritmica. Definida para y >= -1/e; por
    debajo no hay solucion real y se devuelve nan en vez de un numero
    plausible."""
    y = np.asarray(y, dtype=float)
    escalar = y.ndim == 0
    y = np.atleast_1d(y).astype(float)
    w = np.where(y > 1.0, np.log(np.maximum(y, 1e-300)), y * 0.6)
    w = np.where(y < 0, -0.5, w)
    malo = y < -np.exp(-1.0)
    for _ in range(iteraciones):
        e = np.exp(w)
        f = w * e - y
        dw = f / (e * (w + 1.0) - (w + 2.0) * f / (2.0 * w + 2.0))
        w = w - dw
    w = np.where(malo, np.nan, w)
    return float(w[0]) if escalar else w


def omega():
    """La constante omega: W(1) = 0.567143..., el x con x*e^x = 1.

    Es el unico numero que cumple x = e^-x, o sea el punto fijo de la
    exponencial decreciente. De ahi sale el verbo visual de la pieza."""
    return lambert_w(1.0)


def iteracion_punto_fijo(x0=0.05, pasos=18):
    """La sucesion x -> e^-x, que converge a omega desde CUALQUIER x0.

    Devuelve la lista de valores. Sirve para la telaraña de la pieza: es
    la misma maquina que el curso 12 uso con el mapa logistico, aqui
    apuntada a una funcion que converge en vez de estallar."""
    xs = [float(x0)]
    for _ in range(int(pasos)):
        xs.append(float(np.exp(-xs[-1])))
    return np.array(xs)


# --- 03 · INTEGRAL ELIPTICA K ----------------------------------------
def K_completa(m, iteraciones=40):
    """K(m) por la media aritmetico-geometrica. m = k^2 (convenio de m).

    La AGM converge cuadraticamente: seis vueltas dan ya el doble
    precision. Es la forma correcta de calcular K sin scipy, y ademas
    demuestra por que la elliptica no es elemental: el valor sale de un
    LIMITE, no de una formula cerrada."""
    m = np.asarray(m, dtype=float)
    escalar = m.ndim == 0
    m = np.atleast_1d(m).astype(float)
    a = np.ones_like(m)
    b = np.sqrt(np.maximum(1.0 - m, 0.0))
    for _ in range(int(iteraciones)):
        a, b = 0.5 * (a + b), np.sqrt(a * b)
    k = np.pi / (2.0 * a)
    return float(k[0]) if escalar else k


def periodo_pendulo(theta0_grados, L=1.0, g=9.80665):
    """El periodo EXACTO de un pendulo simple de amplitud theta0.

    T = 4 sqrt(L/g) K(sin^2(theta0/2)). La formula de los libros
    (2 pi sqrt(L/g)) es el limite de esta cuando theta0 -> 0."""
    th = np.radians(np.asarray(theta0_grados, dtype=float))
    return 4.0 * np.sqrt(L / g) * K_completa(np.sin(th / 2.0) ** 2)


def periodo_pequeno(L=1.0, g=9.80665):
    """El de los libros: 2 pi sqrt(L/g). No depende de la amplitud."""
    return 2.0 * np.pi * np.sqrt(L / g)


def exceso_de_periodo(theta0_grados, L=1.0, g=9.80665):
    """Cuanto por ciento se pasa el periodo real del de los libros."""
    return float((periodo_pendulo(theta0_grados, L, g)
                  / periodo_pequeno(L, g) - 1.0) * 100.0)


def pendulo(theta0_grados, T, dt=0.0005, L=1.0, g=9.80665):
    """Integra el pendulo REAL (sin aproximar el seno) con RK4.

    Existe para que la pieza no se crea su propia formula: el periodo se
    MIDE sobre esta trayectoria y se compara con `periodo_pendulo`. Si
    K(m) estuviera mal, los dos numeros no coincidirian."""
    th = np.radians(float(theta0_grados))
    w = 0.0
    n = int(round(float(T) / dt))
    ths = np.empty(n + 1)
    ts = np.arange(n + 1) * dt
    ths[0] = th
    k = g / L

    def deriv(s):
        return np.array([s[1], -k * np.sin(s[0])])

    s = np.array([th, w])
    for i in range(1, n + 1):
        k1 = deriv(s)
        k2 = deriv(s + dt / 2 * k1)
        k3 = deriv(s + dt / 2 * k2)
        k4 = deriv(s + dt * k3)
        s = s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        ths[i] = s[0]
    return ts, ths


def periodo_medido(ts, ths):
    """Periodo leido de una trayectoria: dos pasos por cero hacia arriba.

    Interpola linealmente el cruce, que es lo que separa una medida de
    una cuantizacion al paso de integracion."""
    cruces = []
    for i in range(1, len(ths)):
        if ths[i - 1] < 0.0 <= ths[i]:
            f = -ths[i - 1] / (ths[i] - ths[i - 1])
            cruces.append(ts[i - 1] + f * (ts[i] - ts[i - 1]))
        if len(cruces) == 3:
            break
    if len(cruces) < 2:
        return float("nan")
    return float(cruces[1] - cruces[0])


# --- 04 · FRESNEL y la clotoide ---------------------------------------
def fresnel(t, N=20000):
    """C(t) y S(t): las integrales de Fresnel, por Simpson acumulado.

    Son la definicion misma de "no elemental": el integrando es
    cos(pi u^2/2), y no hay primitiva en terminos de funciones
    elementales. Se devuelven las dos curvas muestreadas en `t`."""
    t = np.asarray(t, dtype=float)
    tmax = float(np.max(np.abs(t)))
    u = np.linspace(0.0, tmax, int(N) + 1)
    du = u[1] - u[0] if len(u) > 1 else 0.0
    c = np.cos(np.pi * u ** 2 / 2.0)
    s = np.sin(np.pi * u ** 2 / 2.0)
    # Trapecio acumulado: exacto a O(du^2) y monotono en el sentido de
    # que cada punto solo suma el tramo nuevo.
    C = np.concatenate(([0.0], np.cumsum((c[1:] + c[:-1]) / 2.0) * du))
    S = np.concatenate(([0.0], np.cumsum((s[1:] + s[:-1]) / 2.0) * du))
    signo = np.sign(t)
    Ci = np.interp(np.abs(t), u, C) * signo
    Si = np.interp(np.abs(t), u, S) * signo
    return Ci, Si


def clotoide(smax=5.0, N=3000):
    """La espiral de Cornu: la curva cuya CURVATURA crece con el camino.

    Es la razon de que exista: entre una recta (curvatura 0) y una curva
    circular (curvatura 1/R) hace falta un tramo donde la curvatura suba
    poco a poco, o el volante habria que girarlo de golpe. Toda carretera
    y toda via de tren llevan este trozo."""
    s = np.linspace(-float(smax), float(smax), int(N))
    x, y = fresnel(s)
    return s, x, y


def curvatura(x, y, s):
    """Curvatura medida sobre los PUNTOS dibujados, por diferencias."""
    dx, dy = np.gradient(x, s), np.gradient(y, s)
    ddx, ddy = np.gradient(dx, s), np.gradient(dy, s)
    num = dx * ddy - dy * ddx
    den = (dx ** 2 + dy ** 2) ** 1.5
    return num / np.maximum(den, 1e-18)


def ojo_de_la_espiral(smax=8.0, N=40000):
    """A que distancia del centro (0.5, 0.5) se queda la espiral en smax.

    La espiral NUNCA llega: da vueltas infinitas acercandose. La cifra
    de la pieza es el punto al que tiende, y esta es su prueba."""
    x, y = fresnel(np.array([float(smax)]), N=N)
    return float(np.hypot(x[0] - 0.5, y[0] - 0.5))


# --- 05 · CHEBYSHEV ---------------------------------------------------
def runge(x):
    """La funcion de Runge, 1/(1+25x^2). Mansa, suave, y un campo de
    minas para la interpolacion equiespaciada."""
    x = np.asarray(x, dtype=float)
    return 1.0 / (1.0 + 25.0 * x ** 2)


def nodos_equiespaciados(n):
    """n+1 nodos repartidos por igual en [-1, 1]."""
    return np.linspace(-1.0, 1.0, int(n) + 1)


def nodos_chebyshev(n):
    """n+1 nodos de Chebyshev: las proyecciones de puntos repartidos por
    igual sobre una CIRCUNFERENCIA. Se apiñan en los bordes, que es
    exactamente donde la equiespaciada se descontrola."""
    k = np.arange(int(n) + 1)
    return np.cos(np.pi * k / max(int(n), 1))[::-1]


def interpola(nodos, valores, xs):
    """Interpolacion polinomica por la forma baricentrica de segunda
    especie: el unico algoritmo estable para grados altos. Con la
    formula de Lagrange directa, el grado 20 se hunde en errores de
    redondeo y el desastre del dibujo seria del ALGORITMO, no de los
    nodos, que es lo que la pieza quiere enseñar."""
    nodos = np.asarray(nodos, dtype=float)
    valores = np.asarray(valores, dtype=float)
    xs = np.asarray(xs, dtype=float)
    n = len(nodos)
    w = np.ones(n)
    for j in range(n):
        d = nodos[j] - nodos
        d[j] = 1.0
        w[j] = 1.0 / np.prod(d)
    num = np.zeros_like(xs)
    den = np.zeros_like(xs)
    exacto = np.full(xs.shape, -1, dtype=int)
    for j in range(n):
        dif = xs - nodos[j]
        coincide = np.abs(dif) < 1e-14
        exacto[coincide] = j
        dif = np.where(coincide, 1.0, dif)
        t = w[j] / dif
        num += t * valores[j]
        den += t
    y = num / den
    for j in range(n):
        y[exacto == j] = valores[j]
    return y


def error_interpolacion(nodos, f=runge, N=4001):
    """El error maximo en TODO el intervalo, no solo en los nodos.

    En los nodos el error es cero por construccion: medirlo ahi seria
    medir la definicion. Se mide sobre una malla fina, y por eso la
    cifra hay que comprobarla con dos mallas distintas (lo hace la
    sonda): si se mueve, es de la malla y no del metodo."""
    nodos = np.asarray(nodos, dtype=float)
    xs = np.linspace(-1.0, 1.0, int(N))
    return float(np.max(np.abs(interpola(nodos, f(nodos), xs) - f(xs))))


def chebyshev_T(n, x):
    """T_n por la definicion trigonometrica dentro de [-1,1]."""
    x = np.clip(np.asarray(x, dtype=float), -1.0, 1.0)
    return np.cos(int(n) * np.arccos(x))


def extremos_equioscilantes(n):
    """Los n+1 puntos donde T_n vale exactamente +-1, alternando.

    ESA es la propiedad: el error no se hace pequeño en un sitio a costa
    de otro, se reparte a partes iguales. El dibujo de la pieza es esa
    alternancia."""
    k = np.arange(int(n) + 1)
    return np.cos(np.pi * k / max(int(n), 1))[::-1]


# --- 06 · BESSEL ------------------------------------------------------
def bessel_J(n, x, M=2000):
    """J_n(x) por la integral de Bessel, (1/pi) int_0^pi cos(n t - x sin t) dt.

    Sin scipy y sin series: la cuadratura del trapecio sobre un
    integrando PERIODICO converge exponencialmente, asi que con unos
    pocos miles de puntos da precision de maquina en el rango del curso.
    Y de paso es la definicion que explica la pieza: Bessel salio de un
    problema de mecanica celeste (el movimiento de Kepler), no de un
    tambor."""
    x = np.asarray(x, dtype=float)
    escalar = x.ndim == 0
    forma = x.shape
    x = np.atleast_1d(x).astype(float).ravel()
    t = np.linspace(0.0, np.pi, int(M) + 1)
    peso = np.full_like(t, 1.0)
    peso[0] = peso[-1] = 0.5
    sen = np.sin(t)
    # POR TROZOS. La matriz intermedia es (puntos x M): el modo de un
    # tambor sobre una malla de 140x140 son 15 400 puntos dentro del
    # circulo, que con M=2000 pedirian 246 MB de una sentada. En trozos de
    # 4096 el pico se queda en 65 MB y el resultado es identico.
    y = np.empty_like(x)
    paso = 4096
    for i in range(0, len(x), paso):
        trozo = x[i:i + paso]
        arg = int(n) * t[None, :] - trozo[:, None] * sen[None, :]
        y[i:i + paso] = ((np.cos(arg) * peso[None, :]).sum(axis=1)
                         * (np.pi / int(M)) / np.pi)
    return float(y[0]) if escalar else y.reshape(forma)


def ceros_J(n, cuantos=4, xmax=30.0, N=4000):
    """Los primeros ceros de J_n, por cambio de signo y biseccion.

    No se busca con un umbral absoluto: en una malla discreta el cero
    casi nunca cae sobre una muestra (trampa del curso 32). Se localiza
    el cambio de SIGNO y se afina con biseccion."""
    xs = np.linspace(0.1, float(xmax), int(N))
    ys = bessel_J(n, xs)
    raices = []
    for i in range(len(xs) - 1):
        if ys[i] == 0.0:
            raices.append(float(xs[i]))
        elif ys[i] * ys[i + 1] < 0:
            a, b = xs[i], xs[i + 1]
            for _ in range(80):
                c = 0.5 * (a + b)
                if bessel_J(n, a) * bessel_J(n, c) <= 0:
                    b = c
                else:
                    a = c
            raices.append(0.5 * (a + b))
        if len(raices) >= int(cuantos):
            break
    return np.array(raices)


def modo_tambor(m, k, radio=1.0, N=220, M=400):
    """El modo (m, k) de una membrana circular sobre una malla cuadrada.

    Devuelve (X, Y, U) con U = J_m(alpha r) cos(m theta) dentro del
    circulo y nan fuera, para que quien dibuje no invente valores donde
    no hay tambor."""
    alpha = float(ceros_J(m, cuantos=int(k))[int(k) - 1])
    ejes = np.linspace(-radio, radio, int(N))
    X, Y = np.meshgrid(ejes, ejes)
    R = np.hypot(X, Y)
    TH = np.arctan2(Y, X)
    U = np.full_like(R, np.nan)
    dentro = R <= radio
    U[dentro] = (bessel_J(m, alpha * R[dentro] / radio, M=M)
                 * np.cos(int(m) * TH[dentro]))
    return X, Y, U


def razon_de_modos():
    """El segundo modo de un tambor redondo entre el primero.

    En una cuerda los modos van 1, 2, 3: por eso una cuerda suena a
    NOTA. En un tambor van 1, 1.593, 2.136...: por eso un tambor suena a
    golpe. El numero sale de los ceros de J0 y J1, no de una tabla."""
    return float(ceros_J(1, 1)[0] / ceros_J(0, 1)[0])


def portadora_fm(beta):
    """La amplitud de la portadora de una FM con indice de modulacion
    beta. Es J_0(beta), y por eso se APAGA en el primer cero de J0.

    Es el remate de la pieza: el mismo numero que da el primer circulo
    quieto de un tambor es el ajuste con el que una emisora de FM
    desaparece de su propia frecuencia."""
    return bessel_J(0, beta)


# --- 07 · CHLADNI -----------------------------------------------------
def modo_cuadrado(m, n, N=400):
    """El modo (m, n) de una membrana cuadrada: sin(m pi x) sin(n pi y)."""
    e = np.linspace(0.0, 1.0, int(N))
    X, Y = np.meshgrid(e, e)
    return X, Y, np.sin(m * np.pi * X) * np.sin(n * np.pi * Y)


def chladni(m, n, mezcla=1.0, N=400):
    """La combinacion DEGENERADA: u_mn - u_nm.

    (m,n) y (n,m) tienen exactamente la misma frecuencia, asi que
    cualquier mezcla de las dos tambien es un modo. Ahi esta el truco:
    las figuras de Chladni no son un modo, son la INTERFERENCIA de dos
    modos que suenan igual, y por eso salen curvas donde uno esperaria
    una rejilla."""
    X, Y, a = modo_cuadrado(m, n, N)
    _, _, b = modo_cuadrado(n, m, N)
    return X, Y, a - float(mezcla) * b


def arena(U, X, Y, cuantos=2600, semilla=SEMILLA, umbral=0.035):
    """Los granos que se quedan quietos: donde la placa no se mueve.

    Se siembran puntos al azar (semilla fija) y se queda con los que
    caen sobre una linea nodal. Es lo que hace Chladni de verdad —la
    arena huye de donde vibra y se acumula donde no—, no un contorno
    dibujado con una regla."""
    rng = np.random.default_rng(int(semilla))
    idx = np.flatnonzero(np.abs(U) < float(umbral))
    if len(idx) == 0:
        return np.empty((0, 2))
    elegidos = rng.choice(idx, size=min(int(cuantos), len(idx)),
                          replace=False)
    return np.column_stack([X.ravel()[elegidos], Y.ravel()[elegidos]])


def lineas_nodales(m, n):
    """Cuantas lineas rectas interiores tiene el modo (m, n) puro.

    m-1 verticales y n-1 horizontales. Es la cifra CONTABLE de la pieza:
    la figura de Chladni de la mezcla ya no son rectas, y eso es
    justamente lo que hay que ver."""
    return int(m - 1 + n - 1)


def frecuencia_modo(m, n):
    """La frecuencia relativa del modo (m,n): sqrt(m^2+n^2)."""
    return float(np.hypot(m, n))


# --- 08 · AIRY --------------------------------------------------------
_AI_C1 = 0.355028053887817239
_AI_C2 = 0.258819403792806798


def airy_Ai(x, terminos=60):
    """Ai(x) por su serie de potencias. Vectorizada.

    Se usa la serie y no una cuadratura porque la serie ES la solucion
    de y'' = x y: la sonda comprueba justo eso, que la funcion cumple su
    ecuacion diferencial. Converge en todo el eje real; por debajo de
    x = -9 la cancelacion entre terminos empieza a comerse las cifras,
    asi que el curso no dibuja mas alla."""
    x = np.asarray(x, dtype=float)
    escalar = x.ndim == 0
    x = np.atleast_1d(x).astype(float)
    f = np.ones_like(x)
    g = x.copy()
    tf = np.ones_like(x)
    tg = x.copy()
    for k in range(int(terminos)):
        tf = tf * x ** 3 * (3 * k + 1) / ((3 * k + 1) * (3 * k + 2)
                                          * (3 * k + 3))
        tg = tg * x ** 3 * (3 * k + 2) / ((3 * k + 2) * (3 * k + 3)
                                          * (3 * k + 4))
        f = f + tf
        g = g + tg
    y = _AI_C1 * f - _AI_C2 * g
    return float(y[0]) if escalar else y


def ceros_Ai(cuantos=3, xmin=-9.0, N=6000):
    """Los primeros ceros de Ai, todos en el lado negativo.

    Ai no tiene ningun cero positivo: a la derecha se apaga sin cruzar
    nunca. Esa asimetria es la pieza entera."""
    xs = np.linspace(float(xmin), 0.0, int(N))
    ys = airy_Ai(xs)
    raices = []
    for i in range(len(xs) - 1, 0, -1):
        if ys[i] * ys[i - 1] < 0:
            a, b = xs[i - 1], xs[i]
            for _ in range(90):
                c = 0.5 * (a + b)
                if airy_Ai(a) * airy_Ai(c) <= 0:
                    b = c
                else:
                    a = c
            raices.append(0.5 * (a + b))
        if len(raices) >= int(cuantos):
            break
    return np.array(raices)


def residuo_airy(x0=-4.0, x1=4.0, N=2001):
    """Cuanto se aparta Ai de cumplir y'' = x y, medido en la malla.

    La cifra que demuestra que la implementacion es la funcion de Airy y
    no una curva parecida."""
    xs = np.linspace(x0, x1, int(N))
    y = airy_Ai(xs)
    h = xs[1] - xs[0]
    ypp = (y[2:] - 2 * y[1:-1] + y[:-2]) / h ** 2
    return float(np.max(np.abs(ypp - xs[1:-1] * y[1:-1])))


def borde_de_sombra(x0=-9.0, x1=3.0, N=2400):
    """El perfil de luz en el borde de una sombra: Ai(x)^2 normalizado.

    La optica geometrica dice que ahi hay un escalon: luz de un lado,
    nada del otro. Lo que hay de verdad es esto — franjas que se
    apagan hacia la luz y un desvanecimiento suave hacia la sombra."""
    xs = np.linspace(float(x0), float(x1), int(N))
    inten = airy_Ai(xs) ** 2
    return xs, inten / float(np.max(inten))


def pico_de_sombra(paso=0.02, xmin=-4.0):
    """Donde esta el punto MAS brillante del borde de una sombra.

    No cae en el borde geometrico sino DENTRO de la zona iluminada. Se
    busca por biseccion sobre la derivada, no por el maximo de una malla:
    el maximo de una malla es el punto mas alto de esa malla y cambiaria
    al afinarla.

    Y se BARRE desde el borde hacia dentro hasta el PRIMER cambio de
    signo, en vez de bisecar sobre un intervalo grande. La derivada de
    Ai^2 tiene varias raices ahi (los ceros de Ai y los de Ai'): una
    biseccion sobre (-6, 0) converge a una distinta que sobre (-4, 0), y
    las dos con toda la seguridad del mundo. Lo destapo la sonda al pedir
    el mismo numero con dos intervalos."""
    def d(x, h=1e-4):
        return float(airy_Ai(x + h) ** 2 - airy_Ai(x - h) ** 2)
    x = 0.0
    while x > float(xmin):
        a, b = x - float(paso), x
        if d(a) * d(b) <= 0:
            for _ in range(90):
                c = 0.5 * (a + b)
                if d(a) * d(c) <= 0:
                    b = c
                else:
                    a = c
            return 0.5 * (a + b)
        x = a
    return float("nan")


def luz_en_el_borde():
    """Que fraccion del maximo de luz hay JUSTO en el borde geometrico.

    La optica de rayos dice que ahi hay un escalon: todo de un lado, nada
    del otro. Lo que hay es esta fraccion, ni 1 ni 0 ni 1/2."""
    pico = pico_de_sombra()
    return float(airy_Ai(0.0) ** 2 / airy_Ai(pico) ** 2)


# --- 09 · LEGENDRE ----------------------------------------------------
def legendre_P(l, x):
    """P_l por la recurrencia de Bonnet. Vectorizada en x."""
    x = np.asarray(x, dtype=float)
    if int(l) == 0:
        return np.ones_like(x)
    p0, p1 = np.ones_like(x), x.copy()
    for n in range(1, int(l)):
        p0, p1 = p1, ((2 * n + 1) * x * p1 - n * p0) / (n + 1)
    return p1


def ortogonalidad(l, k, N=20001):
    """La integral de P_l P_k en [-1,1]. Vale 0 si l != k, y 2/(2l+1) si
    son iguales. Es LA propiedad de la familia: por eso sirve para
    descomponer el campo de gravedad de un planeta en capas que no se
    estorban."""
    x = np.linspace(-1.0, 1.0, int(N))
    y = legendre_P(l, x) * legendre_P(k, x)
    return float(np.trapezoid(y, x)) if hasattr(np, "trapezoid") \
        else float(np.trapz(y, x))


def perfil_armonico(l, eps=0.35, N=1200):
    """Una circunferencia deformada por P_l(cos theta): r = 1 + eps P_l.

    Es el corte de un armonico zonal, que es como se escribe la forma de
    un planeta. Para l=2 sale EXACTAMENTE el achatamiento de la Tierra;
    para l mas altos, las capas mas finas del mismo campo."""
    th = np.linspace(0.0, 2 * np.pi, int(N))
    r = 1.0 + float(eps) * legendre_P(int(l), np.cos(th))
    return th, r


def cruces_por_cero(l):
    """Cuantas veces cambia de signo P_l en [-1,1]: exactamente l.

    En el dibujo son los PARALELOS donde el armonico no deforma nada."""
    # Malla de numero PAR de puntos: con una impar, x=0 es una muestra
    # exacta, P_l(0) vale 0 para l impar, y el producto de signos da 0 en
    # vez de negativo — la cuenta se dejaba un cero en cada grado impar.
    x = np.linspace(-1.0, 1.0, 20000)
    y = legendre_P(int(l), x)
    return int(np.sum(np.sign(y[1:]) * np.sign(y[:-1]) < 0))


def cruces_perfil(l, N=8000):
    """Los angulos del PERFIL donde el armonico no deforma nada.

    Ojo con la cifra: en el corte de polo a polo que se dibuja son **2l**,
    no l. Cada paralelo nodal del armonico corta el meridiano DOS veces,
    una por hemisferio del dibujo. Rotular "l paralelos" junto a un dibujo
    donde se cuentan 2l es exactamente el error que el curso 33 cazo nueve
    veces: la cifra hablando del objeto y el dibujo enseñando el corte.

    Se devuelven los angulos para poder MARCARLOS, que es lo que convierte
    la cifra en algo que el espectador puede comprobar."""
    th = np.linspace(0.0, 2 * np.pi, int(N), endpoint=False)
    v = legendre_P(int(l), np.cos(th))
    sg = np.sign(v)
    idx = np.flatnonzero(sg * np.roll(sg, -1) < 0)
    raices = []
    for i in idx:
        a, b = th[i], th[(i + 1) % len(th)]
        if b < a:
            b += 2 * np.pi
        for _ in range(60):
            c = 0.5 * (a + b)
            if (legendre_P(int(l), np.cos(np.array([a])))[0]
                    * legendre_P(int(l), np.cos(np.array([c])))[0]) <= 0:
                b = c
            else:
                a = c
        raices.append(0.5 * (a + b) % (2 * np.pi))
    return np.array(sorted(raices))


# Datos DADOS (WGS84), no medidos aqui: van en gris en pantalla.
RADIO_ECUATORIAL_KM = 6378.137
ACHATAMIENTO = 1.0 / 298.257223563
J2_TIERRA = 1.08262668e-3


def abultamiento_km():
    """Cuantos kilometros mas mide el radio ecuatorial que el polar.

    Se CALCULA a partir del achatamiento dado: a - b = a * f."""
    return float(RADIO_ECUATORIAL_KM * ACHATAMIENTO)


# --- 10 · CATENARIA ---------------------------------------------------
def _a_de_catenaria(vano, flecha, iteraciones=200):
    """Resuelve el parametro a de la catenaria con ese vano y esa flecha.

    flecha = a (cosh(vano/2a) - 1). Biseccion: la ecuacion es monotona
    en a y no tiene forma cerrada — otra funcion que no se despeja."""
    lo, hi = 1e-6, 1e6
    for _ in range(int(iteraciones)):
        a = 0.5 * (lo + hi)
        f = a * (np.cosh(vano / (2 * a)) - 1.0)
        if f > flecha:
            lo = a
        else:
            hi = a
    return 0.5 * (lo + hi)


def catenaria(vano=2.0, flecha=0.6, N=801):
    """La curva que adopta una cadena colgada por su propio peso."""
    a = _a_de_catenaria(float(vano), float(flecha))
    x = np.linspace(-vano / 2, vano / 2, int(N))
    y = a * np.cosh(x / a) - a * np.cosh(vano / (2 * a))
    return x, y


def parabola_equivalente(vano=2.0, flecha=0.6, N=801):
    """La parabola con los MISMOS extremos y la MISMA flecha.

    Es la comparacion honrada: si se dejara libre un parametro, cualquier
    diferencia seria de la eleccion y no de las dos curvas.

    N impar a proposito: con un numero par de muestras el vertice no cae
    en ninguna, la flecha dibujada sale 1e-6 mas corta que la pedida y
    cualquier comprobacion estricta de "misma flecha" falla por una razon
    que no tiene nada que ver con las curvas."""
    x = np.linspace(-vano / 2, vano / 2, int(N))
    y = 4.0 * flecha * (x / vano) ** 2 - flecha
    return x, y


def longitud(x, y):
    """Longitud de arco de una polilinea: lo que mide el cable."""
    return float(np.sum(np.hypot(np.diff(x), np.diff(y))))


def exceso_de_cable(vano=2.0, flecha=0.6, N=4000):
    """Cuanto por ciento mas que el vano mide la cadena. La cifra que
    paga un proyectista: el cable no se compra por la distancia entre
    torres."""
    x, y = catenaria(vano, flecha, N)
    return float((longitud(x, y) / vano - 1.0) * 100.0)


def separacion_maxima(vano=2.0, flecha=0.6, N=4000):
    """La maxima diferencia vertical entre cadena y parabola, en tanto
    por ciento del vano. Es pequeña, y por eso la pieza la declara: la
    parabola no es una mala aproximacion, es una aproximacion."""
    _, yc = catenaria(vano, flecha, N)
    _, yp = parabola_equivalente(vano, flecha, N)
    return float(np.max(np.abs(yc - yp)) / vano * 100.0)


# --- 11 · WEIERSTRASS -------------------------------------------------
W_A = 0.5          # parametros ELEGIDOS (van en gris): a<1 y b impar con
W_B = 13           # a*b > 1 + 3pi/2 = 5.712, la condicion de Weierstrass


def weierstrass(x, a=W_A, b=W_B, terminos=None):
    """W(x) = suma a^k cos(b^k pi x): continua en todas partes y sin
    derivada en ninguna.

    `terminos` se elige por la PRECISION del dibujo, no a ojo: se suman
    los que aportan mas que medio pixel. Con a=0.5 la cola por debajo
    del termino k vale 2*a^k, asi que 30 terminos dan 1e-9."""
    x = np.asarray(x, dtype=float)
    if terminos is None:
        terminos = 30
    y = np.zeros_like(x)
    for k in range(int(terminos)):
        y = y + a ** k * np.cos((b ** k) * np.pi * x)
    return y


def ventana_zoom(centro, ancho, N=4000, **kw):
    """Un trozo de W centrado en `centro` y de anchura `ancho`.

    Cada zoom tiene que sumar MAS terminos que el anterior o el dibujo
    se alisa solo y la pieza demostraria lo contrario de lo que dice.
    Aqui se calculan los necesarios para que el termino mas fino siga
    teniendo mas de un pixel de periodo en la ventana."""
    ancho = float(ancho)
    necesarios = int(np.ceil(np.log(4000.0 / max(ancho, 1e-12))
                             / np.log(W_B))) + 6
    x = np.linspace(centro - ancho / 2, centro + ancho / 2, int(N))
    return x, weierstrass(x, terminos=max(necesarios, 20), **kw)


def cociente_incremental(x0=0.3, h=1e-3, **kw):
    """|W(x0+h) - W(x0)| / h: la pendiente que se le pide a la curva."""
    terminos = int(np.ceil(np.log(4000.0 / h) / np.log(W_B))) + 6
    a = weierstrass(np.array([x0]), terminos=terminos, **kw)[0]
    b = weierstrass(np.array([x0 + h]), terminos=terminos, **kw)[0]
    return float(abs(b - a) / h)


def pendientes_que_se_disparan(x0=0.3, cuantas=5, **kw):
    """La sucesion de pendientes al acercar el punto: NO converge.

    Eso es "no tiene derivada", dicho con numeros: en una curva normal
    esta lista se va quedando quieta en un valor."""
    return [cociente_incremental(x0, 1.0 / (W_B ** k), **kw)
            for k in range(1, int(cuantas) + 1)]


# --- 12 · CANTOR ------------------------------------------------------
def tramos_cantor(niveles=5):
    """Los intervalos que sobreviven en cada nivel, para dibujar el
    peine que construye la escalera."""
    tramos = [(0.0, 1.0)]
    salida = [list(tramos)]
    for _ in range(int(niveles)):
        nuevos = []
        for a, b in tramos:
            t = (b - a) / 3.0
            nuevos.append((a, a + t))
            nuevos.append((b - t, b))
        tramos = nuevos
        salida.append(list(tramos))
    return salida


def escalera_cantor(niveles=8, N=None):
    """La escalera del diablo como POLILINEA exacta, sin base 3.

    La forma "de libro" —expandir x en base 3 y traducir a binario— no
    sobrevive a los flotantes: `v = v*3 - d` acumula error, la funcion
    deja de ser monotona (medido: bajaba en 41 sitios) y en x=1 devolvia
    0 en vez de 1. Y una escalera que baja es exactamente lo contrario de
    lo que la pieza afirma.

    Se construye de la definicion geometrica, que ademas es la que se
    dibuja: en el nivel n quedan 2^n intervalos; sobre el k-esimo la
    funcion sube de k/2^n a (k+1)/2^n, y entre uno y el siguiente se
    queda QUIETA. Monotona por construccion, exacta en los extremos, y
    cada tramo horizontal del dibujo es un hueco de verdad del conjunto
    de Cantor.

    `N` se ignora (queda por compatibilidad de llamada): el numero de
    puntos lo fija el nivel, que es lo unico que tiene sentido aqui."""
    n = int(niveles)
    tramos = tramos_cantor(n)[-1]
    total = float(2 ** n)
    xs, ys = [0.0], [0.0]
    for k, (a, b) in enumerate(tramos):
        xs.append(a)
        ys.append(k / total)          # llega plano desde el hueco anterior
        xs.append(b)
        ys.append((k + 1) / total)    # y sube dentro del intervalo
    xs.append(1.0)
    ys.append(1.0)
    return np.array(xs), np.array(ys)


def mesetas(niveles=8):
    """La longitud total de los tramos PLANOS tras n niveles: 1-(2/3)^n.

    Tiende a 1: la escalera sube de 0 a 1 sin subir en casi ningun
    sitio."""
    return float(1.0 - (2.0 / 3.0) ** int(niveles))


def medida_cantor(niveles=8):
    """Lo que queda del segmento tras n cortes: (2/3)^n. Tiende a 0."""
    return float((2.0 / 3.0) ** int(niveles))


# --- 13 · CAUCHY ------------------------------------------------------
def muestras_gauss(n=20000, semilla=SEMILLA):
    rng = np.random.default_rng(int(semilla))
    return rng.standard_normal(int(n))


def muestras_cauchy(n=20000, semilla=SEMILLA):
    """Cauchy por el cociente de dos normales, que ES una Cauchy.

    Se genera asi y no con la tangente para que las dos muestras del
    dibujo salgan del mismo generador y la comparacion sea limpia."""
    rng = np.random.default_rng(int(semilla))
    a = rng.standard_normal(int(n))
    b = rng.standard_normal(int(n))
    return a / b


def media_corrida(x):
    """La media de las primeras k muestras, para todo k."""
    x = np.asarray(x, dtype=float)
    return np.cumsum(x) / np.arange(1, len(x) + 1)


def salto_maximo(media, desde=0.5):
    """El mayor salto de la media en la ULTIMA mitad del recorrido.

    En una distribucion con media, ese salto se apaga como 1/n. En la
    de Cauchy no se apaga: siempre queda por llegar una muestra lo
    bastante grande para mover el promedio entero."""
    m = np.asarray(media, dtype=float)
    i0 = int(len(m) * float(desde))
    return float(np.max(np.abs(np.diff(m[i0:]))))


def barrido_semillas(cuantas=20, n=20000):
    """Repite el experimento con `cuantas` semillas distintas.

    Una demo que solo funciona con tu semilla no es una demo: esta
    devuelve, para cada semilla, el salto final de la gaussiana y el de
    la Cauchy, y la sonda exige que NINGUNA semilla invierta la
    conclusion."""
    filas = []
    for s in range(int(cuantas)):
        g = salto_maximo(media_corrida(muestras_gauss(n, SEMILLA + s)))
        c = salto_maximo(media_corrida(muestras_cauchy(n, SEMILLA + s)))
        filas.append((SEMILLA + s, g, c))
    return filas


# --- 14 · LORENZ ------------------------------------------------------
LORENZ_SIGMA, LORENZ_RHO, LORENZ_BETA = 10.0, 28.0, 8.0 / 3.0


def _lorenz_deriv(s):
    x, y, z = s
    return np.array([LORENZ_SIGMA * (y - x),
                     x * (LORENZ_RHO - z) - y,
                     x * y - LORENZ_BETA * z])


def lorenz(x0=(1.0, 1.0, 20.0), n=12000, dt=0.004):
    """La trayectoria de Lorenz por RK4. Determinista.

    (Se implementa aqui y no se importa de `caos.py` porque aquel curso
    la dibuja con su HUD de consola; la materia es la misma y la cifra
    tambien, pero el lienzo es otro.)"""
    s = np.array(x0, dtype=float)
    pts = np.empty((int(n), 3))
    for i in range(int(n)):
        pts[i] = s
        k1 = _lorenz_deriv(s)
        k2 = _lorenz_deriv(s + dt / 2 * k1)
        k3 = _lorenz_deriv(s + dt / 2 * k2)
        k4 = _lorenz_deriv(s + dt * k3)
        s = s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return pts


def par_lorenz(eps=1e-9, x0=(1.0, 1.0, 20.0), n=12000, dt=0.004):
    """Dos trayectorias que empiezan separadas por `eps` en x."""
    a = lorenz(x0, n, dt)
    b = lorenz((x0[0] + eps, x0[1], x0[2]), n, dt)
    return a, b


def separacion(a, b):
    """La distancia entre las dos trayectorias, muestra a muestra."""
    return np.linalg.norm(np.asarray(a) - np.asarray(b), axis=1)


def factor_de_separacion(a, b, eps):
    """Por cuanto se ha multiplicado la diferencia inicial."""
    return float(separacion(a, b).max() / eps)


def tiempo_hasta(a, b, umbral, dt=0.004):
    """Cuanto tarda la diferencia en llegar a `umbral`."""
    d = separacion(a, b)
    i = np.argmax(d > umbral)
    return float(i * dt) if d[i] > umbral else float("nan")


def vueltas(pts):
    """Cuantas veces cambia de ala la trayectoria: el signo de x.

    Es la cifra CONTABLE de la mariposa — no se repite nunca el mismo
    numero de vueltas en cada ala, y eso se ve contando."""
    x = np.asarray(pts)[:, 0]
    return int(np.sum(np.sign(x[1:]) * np.sign(x[:-1]) < 0))


# --- 15 · CICLOIDE ----------------------------------------------------
GRAVEDAD = 9.80665        # m/s^2, dato DADO (van en gris)


def _theta_de_cicloide(dx, dy, iteraciones=200):
    """El angulo final de la cicloide que une (0,0) con (dx, -dy).

    x = r(t - sin t), y = -r(1 - cos t) => dx/dy = (t - sin t)/(1 - cos t),
    monotona en t: biseccion. Otra ecuacion que no se despeja."""
    obj = dx / dy
    lo, hi = 1e-9, 2 * np.pi - 1e-9
    for _ in range(int(iteraciones)):
        t = 0.5 * (lo + hi)
        v = (t - np.sin(t)) / (1.0 - np.cos(t))
        if v < obj:
            lo = t
        else:
            hi = t
    return 0.5 * (lo + hi)


def cicloide(dx=2.0, dy=1.0, N=900):
    """La braquistocrona entre (0,0) y (dx, -dy): la curva mas rapida."""
    t1 = _theta_de_cicloide(dx, dy)
    r = dy / (1.0 - np.cos(t1))
    t = np.linspace(0.0, t1, int(N))
    return r * (t - np.sin(t)), -r * (1.0 - np.cos(t))


def recta(dx=2.0, dy=1.0, N=900):
    x = np.linspace(0.0, dx, int(N))
    return x, -dy * x / dx


def arco_circular(dx=2.0, dy=1.0, N=901):
    """El arco de circunferencia de Galileo: el que ARRANCA vertical.

    Por los mismos dos puntos pasan infinitas circunferencias, y la
    eleccion cambia la carrera entera: la tangente a la HORIZONTAL sale
    del reposo sin pendiente y tarda 4.11 s —cinco veces mas que la
    cicloide—, lo que convertiria la comparacion en un espantapajaros.
    La honrada es esta, la que Galileo propuso como respuesta: cae a
    plomo al principio y pierde por poco. Que pierda por poco es la
    gracia de la pieza.

    Centro en (R, 0) con R = 1 / sin(theta1) y tan(theta1/2) = dx/dy."""
    th1 = 2.0 * np.arctan2(float(dx), float(dy))
    R = float(dy) / np.sin(th1)
    th = np.linspace(0.0, th1, int(N))
    return R * (1.0 - np.cos(th)), -R * np.sin(th)


def tiempo_descenso(x, y, g=GRAVEDAD):
    """El tiempo que tarda una cuenta en recorrer la curva sin rozamiento.

    Integra ds/v con v = sqrt(2 g h) por el punto MEDIO de cada tramo:
    en el primer punto v es cero y la integral es impropia, asi que
    evaluar en los extremos daria infinito o una division por cero segun
    el redondeo. El punto medio es lo que la hace converger."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ds = np.hypot(np.diff(x), np.diff(y))
    h = -(y[1:] + y[:-1]) / 2.0
    v = np.sqrt(np.maximum(2.0 * g * h, 1e-12))
    return float(np.sum(ds / v))


def tiempo_cicloide_teorico(dx=2.0, dy=1.0, g=GRAVEDAD):
    """El valor cerrado: t = theta1 * sqrt(r/g). La comprobacion de que
    la integral numerica de arriba mide lo que dice medir."""
    t1 = _theta_de_cicloide(dx, dy)
    r = dy / (1.0 - np.cos(t1))
    return float(t1 * np.sqrt(r / g))


def avance_en_tiempo(x, y, g=GRAVEDAD):
    """Para animar la carrera de verdad: devuelve (tiempos, fraccion de
    camino recorrida), que es la funcion de ritmo de cada cuenta.

    Sin esto, tres bolas moviendose a velocidad uniforme llegarian en el
    orden que decida el `run_time`, no el que decida la fisica."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ds = np.hypot(np.diff(x), np.diff(y))
    h = -(y[1:] + y[:-1]) / 2.0
    v = np.sqrt(np.maximum(2.0 * g * h, 1e-12))
    dt = ds / v
    t = np.concatenate(([0.0], np.cumsum(dt)))
    s = np.concatenate(([0.0], np.cumsum(ds)))
    return t, s / s[-1]


def tautocrona(alturas=(1.0, 0.6, 0.25), dx=2.0, dy=1.0, g=GRAVEDAD):
    """El otro milagro de la cicloide: sueltes donde sueltes, el tiempo
    hasta el fondo es el MISMO. Devuelve un tiempo por altura relativa."""
    t1 = _theta_de_cicloide(dx, dy)
    r = dy / (1.0 - np.cos(t1))
    tiempos = []
    for frac in alturas:
        t0 = np.arccos(np.clip(1.0 - 2.0 * float(frac) * dy / (2 * r),
                               -1.0, 1.0))
        t = np.linspace(t0, np.pi, 4000)
        xs, ys = r * (t - np.sin(t)), -r * (1.0 - np.cos(t))
        ys = ys - ys[0]
        tiempos.append(tiempo_descenso(xs, ys, g))
    return tiempos


# --- 16 · LISSAJOUS ---------------------------------------------------
def lissajous(a=3, b=2, delta=np.pi / 2, N=2400, vueltas_=1.0):
    """x = sin(a t + delta), y = sin(b t). La figura del osciloscopio."""
    t = np.linspace(0.0, 2 * np.pi * float(vueltas_), int(N))
    return np.sin(a * t + delta), np.sin(b * t)


def _mcd(a, b):
    while b:
        a, b = b, a % b
    return a


def cierra_en(a, b):
    """Cuantas vueltas de t hacen falta para que la curva se cierre.

    Si a/b es racional, 2pi/mcd. Si no lo fuera, no se cierra nunca y la
    figura acaba pintando el cuadrado entero."""
    return float(2 * np.pi / _mcd(int(a), int(b)))


def toques(a=3, b=2, N=200000):
    """Los toques de la curva con cada lado de la caja, CONTADOS sobre
    los puntos dibujados.

    Es la lectura del osciloscopio: tocar 3 veces arriba y 2 a un lado
    dice que la razon de frecuencias es 3:2 sin medir ninguna
    frecuencia.

    Devuelve (toques en el LADO, toques en el TECHO), en ese orden,
    porque asi se lee la razon tal cual: 3 y 2 es 3:2. El lado lo toca la
    x, que es la que lleva la frecuencia a.

    El conteo va con ENVOLTURA y sin repetir el punto final. Una curva
    cerrada muestreada con `linspace` trae el ultimo punto igual que el
    primero: si ese punto es un maximo (y en 3:2 lo es, la curva arranca
    tocando el lado), se cuenta dos veces y el osciloscopio lee 4:2, que
    no es ninguna razon."""
    T = cierra_en(int(a), int(b))
    t = np.linspace(0.0, T, int(N), endpoint=False)
    x, y = np.sin(a * t + np.pi / 2), np.sin(b * t)

    def picos(v):
        izq, der = np.roll(v, 1), np.roll(v, -1)
        return int(np.sum((v > izq) & (v >= der) & (v > 0.9999)))

    return picos(x), picos(y)


# --- 17 · ZETA --------------------------------------------------------
def zeta(s, N=48):
    """Zeta de Riemann por el algoritmo de Borwein (eta alternante).

    Converge en TODO el semiplano Re(s) > 0, incluida la recta critica,
    que es donde vive la pieza. Con N=48 da del orden de 1e-15 en el
    rango que se dibuja. Acepta complejos."""
    s = np.asarray(s, dtype=complex)
    escalar = s.ndim == 0
    s = np.atleast_1d(s)
    n = int(N)
    d = np.zeros(n + 1)
    d[0] = 1.0
    for k in range(1, n + 1):
        d[k] = d[k - 1] * (n + k - 1) * (n - k + 1) * 4.0 / \
            ((2 * k - 1) * 2.0 * k)
    dn = np.sum(d)
    acc = np.zeros_like(s)
    suma = 0.0
    for k in range(n):
        suma += d[k]
        acc = acc + ((-1) ** k) * (suma - dn) / (k + 1.0) ** s
    eta = -acc / dn
    y = eta / (1.0 - 2.0 ** (1.0 - s))
    return complex(y[0]) if escalar else y


def zeta_en_recta(t0=0.0, t1=32.0, N=1800):
    """zeta(1/2 + i t) sobre la recta critica: la curva que se dibuja."""
    t = np.linspace(float(t0), float(t1), int(N))
    z = zeta(0.5 + 1j * t)
    return t, z


def hardy_Z(t):
    """La funcion Z de Hardy: real sobre la recta critica y con el mismo
    modulo que zeta, asi que sus CEROS son los ceros de zeta.

    Se usa para buscar el primer cero por cambio de signo, que es una
    medida honrada; buscar un minimo de |zeta| sobre una malla no lo es
    (daria el punto mas bajo de la malla, no el cero)."""
    t = np.asarray(t, dtype=float)
    s = 0.5 + 1j * t
    theta = np.angle(gamma_compleja(0.25 + 0.5j * t)) - t / 2.0 * np.log(np.pi)
    return np.real(np.exp(1j * theta) * zeta(s))


def gamma_compleja(z, terminos=9):
    """Gamma de Lanczos para argumento complejo (la necesita Hardy Z)."""
    z = np.asarray(z, dtype=complex)
    escalar = z.ndim == 0
    z = np.atleast_1d(z)
    y = np.empty_like(z)
    izq = np.real(z) < 0.5
    if np.any(~izq):
        w = z[~izq] - 1.0
        s = np.full(w.shape, _LANCZOS[0], dtype=complex)
        for i in range(1, terminos):
            s = s + _LANCZOS[i] / (w + i)
        t = w + 7.5
        y[~izq] = np.sqrt(2 * np.pi) * t ** (w + 0.5) * np.exp(-t) * s
    if np.any(izq):
        y[izq] = np.pi / (np.sin(np.pi * z[izq])
                          * gamma_compleja(1.0 - z[izq]))
    return complex(y[0]) if escalar else y


def primer_cero_zeta(t0=10.0, t1=20.0, N=400):
    """El primer cero no trivial, por cambio de signo de Z y biseccion."""
    ts = np.linspace(t0, t1, int(N))
    zs = hardy_Z(ts)
    for i in range(len(ts) - 1):
        if zs[i] * zs[i + 1] < 0:
            a, b = ts[i], ts[i + 1]
            for _ in range(90):
                c = 0.5 * (a + b)
                if hardy_Z(np.array([a]))[0] * hardy_Z(np.array([c]))[0] <= 0:
                    b = c
                else:
                    a = c
            return float(0.5 * (a + b))
    return float("nan")


def basilea(terminos=200000):
    """La suma 1 + 1/4 + 1/9 + ... calculada a lo bruto, para enseñar a
    que se parece zeta(2) antes de decir que vale pi^2/6."""
    n = np.arange(1, int(terminos) + 1, dtype=float)
    return float(np.sum(1.0 / n ** 2))


# --- 18 · SUPERFORMULA ------------------------------------------------
def superformula(m=6, n1=1.0, n2=1.0, n3=1.0, a=1.0, b=1.0, N=2400):
    """La superformula de Gielis: r(phi), y con cuatro numeros salen
    estrellas de mar, flores, diatomeas y un cuadrado.

    Es la unica pieza del curso cuyo nombre no lleva el de un muerto
    ilustre: es de 2003. Sirve de cierre porque dice lo mismo que el
    curso entero al reves — a veces la funcion nueva no resuelve un
    problema, RESUME una familia de formas."""
    phi = np.linspace(0.0, 2 * np.pi, int(N))
    t1 = np.abs(np.cos(m * phi / 4.0) / a) ** n2
    t2 = np.abs(np.sin(m * phi / 4.0) / b) ** n3
    r = (t1 + t2) ** (-1.0 / n1)
    return phi, r


def lobulos(phi, r, tolerancia=1e-9):
    """Cuantos maximos locales tiene r(phi): los lobulos CONTADOS sobre
    la curva que se dibuja, no leidos del parametro m.

    No se cuenta comparando cada muestra con sus vecinas: un maximo que
    cae JUSTO entre dos muestras deja dos valores iguales, la comparacion
    estricta no lo ve, y la cuenta salia una corta en tres de las cinco
    formas del curso (m=6 daba 5, m=12 daba 11) — una cifra falsa en
    pantalla que ningun dibujo habria delatado, porque los lobulos que se
    ven SI son seis.

    Se cuenta lo que de verdad define un maximo: que la pendiente pase de
    subir a bajar. Las mesetas (pendiente nula) heredan el signo de la
    ultima pendiente que no lo era, con envoltura."""
    r = np.asarray(r, dtype=float)[:-1]          # sin el punto repetido
    d = np.diff(np.concatenate([r, r[:1]]))
    sg = np.sign(np.where(np.abs(d) < tolerancia, 0.0, d))
    # Arrastra el ultimo signo no nulo, dando la vuelta al cerrar.
    ultimo = 0.0
    for _ in range(2):                            # dos pasadas: envoltura
        for i in range(len(sg)):
            if sg[i] == 0.0:
                sg[i] = ultimo
            else:
                ultimo = sg[i]
    return int(np.sum((sg == 1.0) & (np.roll(sg, -1) == -1.0)))


FORMAS = {
    "estrella": dict(m=5, n1=0.30, n2=0.30, n3=0.30),
    "flor": dict(m=6, n1=1.00, n2=1.00, n3=1.00),
    "gota": dict(m=3, n1=4.50, n2=10.0, n3=10.0),
    "diatomea": dict(m=12, n1=0.40, n2=0.35, n3=0.35),
    "cuadrado": dict(m=4, n1=20.0, n2=20.0, n3=20.0),
}


# =====================================================================
#  MITAD DE DIBUJO
# =====================================================================

def _exige_manim():
    if not _HAY_MANIM:
        raise RuntimeError(
            "las piezas de dibujo de especiales.py necesitan manim y "
            "lienzo; la mitad numerica se importa sin ellos a proposito")


TRAZO = 3.0
TRAZO_FINO = 1.8
TRAZO_PELO = 1.0


def marco(rango_x, rango_y, ancho=5.2, alto=4.4):
    """La regla de tres de todo el curso: datos -> coordenadas de escena.

    Devuelve `punto(x, y)`, la funcion que coloca un par de datos dentro
    de una caja centrada en el origen. TODO lo que se dibuja en una
    pieza tiene que pasar por el MISMO `punto`, o dos curvas del mismo
    plano acabaran a escalas distintas sin que se note.

    No dibuja ejes: los ejes se piden aparte y solo si aportan."""
    _exige_manim()
    x0, x1 = float(rango_x[0]), float(rango_x[1])
    y0, y1 = float(rango_y[0]), float(rango_y[1])
    dx = (x1 - x0) or 1.0
    dy = (y1 - y0) or 1.0

    def punto(xi, yi):
        return np.array([(float(xi) - x0) / dx * ancho - ancho / 2.0,
                         (float(yi) - y0) / dy * alto - alto / 2.0, 0.0])

    punto.rango_x = (x0, x1)
    punto.rango_y = (y0, y1)
    punto.ancho = float(ancho)
    punto.alto = float(alto)
    return punto


def curva(x, y, punto, color=None, grosor=TRAZO, cerrada=False,
          a_trozos=False):
    """Una polilinea de datos dentro del marco.

    `a_trozos` para la curva que va ENCIMA de otra cuando las dos tienen
    que verse coincidir: dos trazos opacos superpuestos se funden en un
    color que no es ninguno de los dos (medido en el curso 33), y a
    trozos se ve el de abajo en cada hueco."""
    _exige_manim()
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    bueno = np.isfinite(x) & np.isfinite(y)
    x, y = x[bueno], y[bueno]
    pts = [punto(xi, yi) for xi, yi in zip(x, y)]
    if cerrada and len(pts) > 2:
        pts.append(pts[0])
    linea = VMobject(stroke_color=color or _lz.TINTA, stroke_width=grosor)
    linea.set_points_as_corners(pts)
    return DashedVMobject(linea, num_dashes=90) if a_trozos else linea


def eje_x(punto, color=None, grosor=TRAZO_PELO):
    """La linea y=0 del marco, y SOLO si el cero cae dentro.

    Si no cae, aborta: un eje de cero en un cuadro que no contiene el
    cero es una referencia que no existe, y el dibujo pasa a afirmar que
    unos valores son positivos cuando no lo son (cazado en el curso
    33)."""
    _exige_manim()
    y0, y1 = punto.rango_y
    if not (y0 <= 0.0 <= y1):
        raise _lz.FueraDelLienzo(
            f"el cero no cae en rango_y=({y0:.3g}, {y1:.3g}): no dibujes un "
            f"eje de cero en un cuadro que no lo contiene")
    a, b = punto(punto.rango_x[0], 0.0), punto(punto.rango_x[1], 0.0)
    return Line(a, b, stroke_color=color or _lz.LINEA, stroke_width=grosor)


def eje_y(punto, color=None, grosor=TRAZO_PELO):
    """La linea x=0, con la misma guarda que `eje_x`."""
    _exige_manim()
    x0, x1 = punto.rango_x
    if not (x0 <= 0.0 <= x1):
        raise _lz.FueraDelLienzo(
            f"el cero no cae en rango_x=({x0:.3g}, {x1:.3g})")
    a, b = punto(0.0, punto.rango_y[0]), punto(0.0, punto.rango_y[1])
    return Line(a, b, stroke_color=color or _lz.LINEA, stroke_width=grosor)


def recuadro(punto, color=None, grosor=TRAZO_PELO):
    """El borde del cuadro, para cuando el cero no cae dentro."""
    _exige_manim()
    x0, x1 = punto.rango_x
    y0, y1 = punto.rango_y
    esquinas = [punto(x0, y0), punto(x1, y0), punto(x1, y1), punto(x0, y1)]
    g = VMobject(stroke_color=color or _lz.LINEA, stroke_width=grosor)
    g.set_points_as_corners(esquinas + [esquinas[0]])
    return g


def marca_en(punto, x, y, color=None, radio=0.068):
    """Un punto sobre la curva: el sitio exacto del que habla la cifra.

    TINTA por defecto, y no ambar, aunque el ambar sea el acento del
    estilo: en este curso la curva YA es ambar, y un punto ambar encima de
    una curva ambar no existe — medido en el molde, la marca del ultimo
    plano era invisible sobre su propia rama. El punto que señala de donde
    sale la cifra se pinta del color de la cifra."""
    _exige_manim()
    return Dot(punto(x, y), radius=radio, color=color or _lz.TINTA)


def vertical(punto, x, color=None, grosor=TRAZO_PELO, a_trozos=True):
    """Una vertical en x que cruza todo el cuadro: señala un valor del
    eje sin escribir un numero encima del dibujo."""
    _exige_manim()
    y0, y1 = punto.rango_y
    ln = Line(punto(x, y0), punto(x, y1),
              stroke_color=color or _lz.APAGADO, stroke_width=grosor)
    return DashedVMobject(ln, num_dashes=18) if a_trozos else ln


def plomada(punto, x, y, color=None, grosor=TRAZO_PELO, trozos=10):
    """Una discontinua CORTA, del eje hasta el punto marcado.

    La vertical de cuadro entero (`vertical`) dice "este valor de x"; esta
    dice "este punto de la curva", que es lo que quiere una pieza cuando
    señala de donde sale su cifra. Y no compite con el dibujo: medido en
    el molde, la de cuadro entero se llevaba la mirada."""
    _exige_manim()
    ln = Line(punto(x, 0.0), punto(x, y),
              stroke_color=color or _lz.AMBAR, stroke_width=grosor)
    return DashedVMobject(ln, num_dashes=int(trozos))


def polar(phi, r, radio=2.2, color=None, grosor=TRAZO, referencia=False):
    """Una curva dada en polares, centrada en el origen.

    `referencia` añade la circunferencia r=1 en APAGADO opaco: sin ella,
    una deformacion del 35 % no se distingue de una circunferencia
    dibujada a pulso. Y en APAGADO OPACO, no en ambar traslucido, que
    sobre este azul da verde oliva (medido en el curso 31)."""
    _exige_manim()
    phi = np.asarray(phi, dtype=float)
    r = np.asarray(r, dtype=float)
    escala = radio / float(np.max(np.abs(r)))
    pts = [np.array([r[i] * escala * np.cos(phi[i]),
                     r[i] * escala * np.sin(phi[i]), 0.0])
           for i in range(len(phi))]
    linea = VMobject(stroke_color=color or _lz.TINTA, stroke_width=grosor)
    linea.set_points_as_corners(pts + [pts[0]])
    if not referencia:
        return linea
    base = Circle(radius=escala, stroke_color=_lz.APAGADO,
                  stroke_width=TRAZO_PELO, fill_opacity=0.0)
    return VGroup(base, linea)


def nube(pts, radio=2.2, color=None, grano=0.022, escala=None):
    """Una nube de puntos (la arena de Chladni) dentro de un cuadrado.

    Los granos van como `Dot`, que es VMobject: la nube entera sigue
    valiendo como hijo de un VGroup (`lz.agrupar` lo respeta igual)."""
    _exige_manim()
    pts = np.asarray(pts, dtype=float).reshape(-1, 2)
    esc = escala if escala is not None else 2.0 * radio
    g = VGroup()
    for px, py in pts:
        g.add(Dot([(px - 0.5) * esc, (py - 0.5) * esc, 0.0],
                  radius=grano, color=color or _lz.TINTA))
    return g


def campo_signo(X, Y, U, radio=2.2, paso=9, grano=0.030,
                color_mas=None, color_menos=None, recorte_circular=False):
    """El campo de una membrana como una rejilla de puntos con signo.

    Dos colores (el acento y el cian) y el TAMAÑO proporcional a la
    amplitud. Se dibuja asi y no como imagen por dos razones: una
    `ImageMobject` obliga a `Group` y arrastra la trampa de mezclar
    grupos (curso 32), y una rejilla de puntos enseña el CERO —los
    granos desaparecen— que es justo lo que la pieza quiere contar."""
    _exige_manim()
    U = np.asarray(U, dtype=float)
    n = U.shape[0]
    umax = float(np.nanmax(np.abs(U))) or 1.0
    g = VGroup()
    for i in range(0, n, int(paso)):
        for j in range(0, n, int(paso)):
            u = U[i, j]
            if not np.isfinite(u):
                continue
            px = (X[i, j] - np.nanmin(X)) / (np.nanmax(X) - np.nanmin(X))
            py = (Y[i, j] - np.nanmin(Y)) / (np.nanmax(Y) - np.nanmin(Y))
            ex, ey = (px - 0.5) * 2 * radio, (py - 0.5) * 2 * radio
            if recorte_circular and np.hypot(ex, ey) > radio:
                continue
            a = abs(u) / umax
            if a < 0.04:
                continue
            col = (color_mas or _lz.AMBAR) if u > 0 else \
                  (color_menos or _lz.CIAN)
            g.add(Dot([ex, ey, 0.0], radius=grano * (0.35 + 0.65 * a),
                      color=col))
    return g


def circunferencia(radio=2.2, color=None, grosor=TRAZO_FINO):
    _exige_manim()
    return Circle(radius=float(radio), stroke_color=color or _lz.APAGADO,
                  stroke_width=grosor, fill_opacity=0.0)


def recortar(x, y, rango_y):
    """Parte una curva en los TRAMOS que caben dentro de la ventana.

    Una polilinea con un solo valor fuera del cuadro se va kilometros
    fuera, el grupo pasa a medir el triple de la franja y el guardian de
    legibilidad aborta con un mensaje que no señala la causa (curso 32).
    Y `np.clip` es peor que el error: aplasta la curva contra el borde y
    dibuja una recta horizontal, que se lee como saturacion — justo lo
    contrario de "esto se dispara".

    Lo honrado es cortar: se devuelve una lista de (x, y) con los trozos
    que SI estan dentro, y la curva entra y sale del cuadro por el borde,
    que es lo que de verdad hace."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    y0, y1 = float(rango_y[0]), float(rango_y[1])
    dentro = (y >= y0) & (y <= y1) & np.isfinite(y)
    tramos, i = [], 0
    n = len(y)
    while i < n:
        if not dentro[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and dentro[j + 1]:
            j += 1
        if j > i:
            tramos.append((x[i:j + 1], y[i:j + 1]))
        i = j + 1
    return tramos


def telarana(f, x0, pasos, punto, color=None, grosor=TRAZO_FINO):
    """La telaraña de una iteracion x -> f(x), dentro de un marco.

    Sube en vertical hasta la curva y se mueve en horizontal hasta la
    diagonal, una y otra vez. Es el dibujo que convierte una sucesion de
    numeros en un GESTO: si el gesto se cierra hacia un punto, la
    iteracion converge, y se ve sin leer ni un numero.

    (La misma maquina que el curso 12 uso con el mapa logistico. Alli
    servia para enseñar que algo estalla; aqui, que algo se posa.)"""
    _exige_manim()
    pts = [punto(float(x0), 0.0)]
    x = float(x0)
    for _ in range(int(pasos)):
        y = float(f(x))
        pts.append(punto(x, y))       # sube a la curva
        pts.append(punto(y, y))       # se mueve a la diagonal
        x = y
    linea = VMobject(stroke_color=color or _lz.TINTA, stroke_width=grosor)
    linea.set_points_as_corners(pts)
    return linea


class Pendulo(VGroup):
    """Una varilla y su lenteja, colgadas del origen del grupo.

    `colocar(theta)` la pone en su angulo (radianes, 0 = abajo). Existe
    como pieza y no como dos mobjects sueltos porque el updater de una
    pieza de este curso tiene que mover las DOS cosas a la vez: con la
    varilla y la lenteja por separado, cualquier despiste deja la bola
    flotando fuera de su hilo y el fotograma miente sobre un pendulo."""

    def __init__(self, largo=2.4, color=None, radio=0.13, grosor=2.4):
        _exige_manim()
        color = color or _lz.AMBAR
        self.largo = float(largo)
        self.varilla = Line([0, 0, 0], [0, -self.largo, 0],
                            stroke_color=_lz.APAGADO, stroke_width=grosor)
        self.lenteja = Dot([0, -self.largo, 0], radius=radio, color=color)
        self.pivote = Dot([0, 0, 0], radius=0.045, color=_lz.APAGADO)
        super().__init__(self.pivote, self.varilla, self.lenteja)

    def colocar(self, theta):
        x = self.largo * np.sin(float(theta))
        y = -self.largo * np.cos(float(theta))
        origen = self.pivote.get_center()
        self.varilla.put_start_and_end_on(
            origen, origen + np.array([x, y, 0.0]))
        self.lenteja.move_to(origen + np.array([x, y, 0.0]))
        return self


def ritmo_fisico(tiempos, fracciones, total=None):
    """La funcion de ritmo de una animacion que tiene que ir a la
    velocidad de la FISICA, no a la del `run_time`.

    `MoveAlongPath` recorre el camino de forma uniforme en alpha. Si tres
    cuentas caen por tres curvas distintas con ritmo uniforme, llegan en
    el orden que decida el `run_time` de cada una — o sea, el orden lo
    pone quien anima, no la gravedad. Esto devuelve un `rate_func` que
    convierte alpha (tiempo de video) en fraccion de camino recorrido
    segun los tiempos REALES de caida.

    `total` es el tiempo comun a las tres curvas (el de la mas lenta), y
    ES el que hay que pasar: normalizar cada curva con el suyo es
    exactamente la forma de que las tres lleguen a la vez y la carrera no
    demuestre nada."""
    t = np.asarray(tiempos, dtype=float)
    f = np.asarray(fracciones, dtype=float)
    T = float(total if total is not None else t[-1])

    def rate(alpha):
        return float(np.interp(alpha * T, t, f))

    return rate

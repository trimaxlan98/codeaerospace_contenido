# =====================================================================
# CO.DE Academy - calculo.py
# La libreria del curso 35: "Calculo visible", VERTICAL 9:16, LIENZO.
#
# Dos mitades, como en toda la casa:
#
#   1. NUMERICA. numpy puro, sin manim, determinista. Aqui viven TODAS
#      las cifras que salen en pantalla, y es lo que verifica
#      `studio/tools/sonda_calculo.py` sin arrancar un render.
#   2. DE DIBUJO. Piezas centradas en el origen; NO animan y NO deciden
#      donde van (de eso se encarga `lienzo.encajar`).
#
# QUE CAPA OCUPA, que es la decision editorial del curso:
#
#   El curso 21 (calculo vectorial) cuenta el espacio que FLUYE: campos,
#   gradiente, divergencia, rotacional, Green y Stokes. Es multivariable
#   y es de operadores.
#   El 32 cuenta como se cambia de dominio, el 33 que hace un sistema y
#   el 34 las funciones que hubo que inventar.
#
#   Este cuenta el calculo DE UNA VARIABLE, y lo cuenta por el DIBUJO
#   QUE LO DEMUESTRA: cada pieza es una idea cuya prueba se puede mirar
#   —una secante que cae, un area que crece, una escalera que no adelgaza,
#   un anillo que no depende de su esfera— y termina en una cifra que el
#   render calcula.
#
#   Lo que NO se cuenta aqui porque ya tiene curso: los campos y sus
#   operadores (21), las transformadas (32), los sistemas (33) y las
#   funciones especiales (34). Si una pieza se pone a hablar de
#   gradientes o de dominios, se ha salido de su capa.
#
# POR QUE SE APOYA EN especiales.py:
#
#   Su mitad de dibujo (`marco`, `curva`, `eje_x`, `recuadro`,
#   `marca_en`, `vertical`, `plomada`, `circunferencia`, `recortar`) no
#   tiene nada de las funciones especiales: es el sustrato de dibujo del
#   estilo LIENZO en vertical, calibrado en 20 piezas y con los
#   guardianes ya puestos. Duplicarlo aqui seria mantener dos copias que
#   se desincronizan. Se importa y se re-exporta, igual que
#   `calculo_vectorial.py` se apoyo en `algebra_lineal.py`.
#
# POR QUE NO HAY scipy AQUI:
#
#   La imagen de render lo trae como dependencia de manim, pero lo que
#   se dibuja tiene que salir de codigo que se pueda leer y explicar.
#   scipy se usa SOLO en la sonda, como oraculo: dos implementaciones
#   independientes que coinciden es una prueba; un `import scipy` es una
#   promesa.
#
# Honestidad: la CIFRA es lo que este render calcula. Un parametro
# elegido (el volumen de la lata, las proporciones de una lata real, la
# tolerancia con la que se mide un alcance) va con etiqueta APAGADA por
# mucho que este escrito aqui.
# =====================================================================
import numpy as np

try:
    from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Arc, Circle,
                       DashedVMobject, Dot, Line, Polygon, VGroup, VMobject)

    import lienzo as _lz
    _HAY_MANIM = True
except Exception:          # la sonda corre sin manim
    _HAY_MANIM = False

# El sustrato de dibujo del estilo, tal cual. `especiales` se importa sin
# manim igual que este modulo: su mitad de dibujo aborta sola si falta.
from especiales import (TRAZO, TRAZO_FINO, TRAZO_PELO, circunferencia,  # noqa: F401,E501
                        curva, eje_x, eje_y, marca_en, marco, nube, plomada,
                        polar, recortar, recuadro, vertical)


# =====================================================================
#  MITAD NUMERICA
# =====================================================================

# --- 01 · SECANTE -----------------------------------------------------
# La cubica x^3 - 2x: tiene valle, sube y no es simetrica, asi que la
# secante se ve GIRAR al acercarse en vez de quedarse casi quieta como
# haria sobre una parabola.

def f_cubica(x):
    x = np.asarray(x, dtype=float)
    return x ** 3 - 2.0 * x


def df_cubica(x):
    x = np.asarray(x, dtype=float)
    return 3.0 * x ** 2 - 2.0


def secante(x0, h):
    """Pendiente del segmento entre x0 y x0+h. El cociente incremental.

    Es la definicion, sin limite: dos puntos y una division. Todo lo que
    hace la pieza 01 es enseñar que esa division se queda quieta."""
    x0, h = float(x0), float(h)
    if h == 0.0:
        raise ValueError("la secante con h=0 es el punto, no una recta")
    return float((f_cubica(x0 + h) - f_cubica(x0)) / h)


def pendientes_secantes(x0=1.0, hs=(1.0, 0.5, 0.25, 0.1)):
    return [secante(x0, h) for h in hs]


def error_de_secante(x0=1.0, h=0.1):
    """Cuanto se equivoca la secante respecto de la pendiente de verdad."""
    return abs(secante(x0, h) - float(df_cubica(x0)))


def recta_por(x0, y0, pendiente, xs):
    """La recta que pasa por un punto con una pendiente dada."""
    xs = np.asarray(xs, dtype=float)
    return y0 + float(pendiente) * (xs - float(x0))


# --- 02 · EPSILON-DELTA -----------------------------------------------
# f(x) = x^2 en x0 = 3, limite 9. La banda vertical NO es simetrica: el
# lado de arriba da menos margen que el de abajo porque la parabola
# empina. Se toma el MINIMO de los dos, que es lo que dice la definicion.

X0_EPS = 3.0


def limite_cuadrado(x0=X0_EPS):
    return float(x0) ** 2


def delta_para(eps, x0=X0_EPS):
    """El ancho de la banda vertical que responde a una tolerancia eps.

    Devuelve el MENOR de los dos lados: si se tomara el mayor, habria
    puntos dentro de la banda cuya imagen se sale, y la pieza estaria
    enseñando una respuesta que no responde."""
    eps, x0 = float(eps), float(x0)
    L = x0 ** 2
    if eps <= 0 or eps >= L:
        raise ValueError("eps tiene que caer entre 0 y el propio limite")
    derecha = np.sqrt(L + eps) - x0
    izquierda = x0 - np.sqrt(L - eps)
    return float(min(derecha, izquierda))


def cumple_la_banda(eps, x0=X0_EPS, N=4001):
    """El maximo de |f(x)-L| dentro de la banda que devuelve delta_para.

    Si esto se pasa de eps, la respuesta no valia. Es el invariante que
    define la pieza entera."""
    d = delta_para(eps, x0)
    xs = np.linspace(x0 - d, x0 + d, N)
    return float(np.max(np.abs(xs ** 2 - float(x0) ** 2)))


# --- 03 · RECTA ESCONDIDA ---------------------------------------------
# La linealidad local: de cerca, una curva y su tangente no se
# distinguen. Y no se distinguen a un ritmo MEDIBLE: el hueco se divide
# entre cuatro cada vez que se parte la distancia por dos, porque el
# primer termino que sobra es f''(x0)*h^2/2.

X0_ZOOM = 1.0


def f_zoom(x):
    return np.sin(np.asarray(x, dtype=float))


def df_zoom(x):
    return np.cos(np.asarray(x, dtype=float))


def despegue(h, x0=X0_ZOOM):
    """Lo que se separan curva y tangente a una distancia h del punto."""
    x0, h = float(x0), float(h)
    return float(abs(f_zoom(x0 + h) - (f_zoom(x0) + df_zoom(x0) * h)))


def despegues(x0=X0_ZOOM, hs=(0.8, 0.4, 0.2, 0.1)):
    return [despegue(h, x0) for h in hs]


def razon_de_despegue(x0=X0_ZOOM, hs=(0.8, 0.4, 0.2, 0.1)):
    """Cuantas veces se achica el hueco al partir la distancia por dos."""
    d = despegues(x0, hs)
    return [float(d[i] / d[i + 1]) for i in range(len(d) - 1)]


def ventana(x0=X0_ZOOM, semiancho=0.8, N=401):
    """Curva y tangente en una ventana centrada en el punto.

    Devuelve (xs, curva, tangente) para dibujar el mismo zoom cuatro
    veces con distinto semiancho: es el unico zoom del curso.

    La malla es IMPAR a proposito. Con un numero par de muestras el
    centro de la ventana NO es ninguna de ellas, y la curva dibujada no
    llega a tocar a su tangente justo en el punto del que habla la pieza:
    se cruzan medio pixel al lado. Es la misma trampa que en el curso 34
    dejo sin vertice a la parabola."""
    x0 = float(x0)
    N = int(N) | 1
    xs = np.linspace(x0 - semiancho, x0 + semiancho, N)
    return xs, f_zoom(xs), f_zoom(x0) + df_zoom(x0) * (xs - x0)


# --- 04 · NUMERO E ----------------------------------------------------
# La subtangente de e^x vale 1 en TODOS los puntos: la tangente en x0
# corta el eje exactamente en x0-1. Es la propiedad que define al numero,
# vista sin una sola formula.

def exp_(x):
    return np.exp(np.asarray(x, dtype=float))


def subtangente(x0):
    """Distancia horizontal del punto al corte de su tangente con y=0.

    Para e^x sale 1 en todos los puntos, y sale de dividir f entre f',
    que es justo la propiedad 'su pendiente es su altura'."""
    x0 = float(x0)
    y = float(np.exp(x0))
    m = float(np.exp(x0))            # la pendiente ES la altura
    return float(y / m)


def corte_de_tangente(x0):
    """Donde la tangente a e^x en x0 cruza el eje horizontal."""
    return float(x0) - subtangente(x0)


def tangente_exp(x0, xs):
    x0 = float(x0)
    return np.exp(x0) * (1.0 + (np.asarray(xs, dtype=float) - x0))


def numero_e():
    """e, calculado como la altura de la curva donde la pendiente es 1."""
    return float(np.exp(1.0))


# --- 05 · VALOR MEDIO -------------------------------------------------
# Un viaje de 2 h y 175 km. La posicion es un smoothstep: sale parado y
# llega parado, que es como se conduce de verdad y ademas garantiza que
# la velocidad media se alcanza DOS veces.

DISTANCIA_KM = 175.0
DURACION_H = 2.0


def posicion(t):
    """Kilometros recorridos a la hora t."""
    u = np.asarray(t, dtype=float) / DURACION_H
    return DISTANCIA_KM * (3.0 * u ** 2 - 2.0 * u ** 3)


def velocidad(t):
    """La derivada de la posicion, en km/h."""
    u = np.asarray(t, dtype=float) / DURACION_H
    return DISTANCIA_KM * (6.0 * u - 6.0 * u ** 2) / DURACION_H


def velocidad_media():
    return DISTANCIA_KM / DURACION_H


def instantes_de_la_media():
    """Los instantes en los que el velocimetro marca EXACTAMENTE la media.

    Salen de resolver u - u^2 = 1/6, que es el teorema del valor medio
    escrito para este viaje."""
    raiz = np.sqrt(1.0 - 2.0 / 3.0)
    us = ((1.0 - raiz) / 2.0, (1.0 + raiz) / 2.0)
    return tuple(float(u * DURACION_H) for u in us)


def velocidad_maxima():
    return float(np.max(velocidad(np.linspace(0.0, DURACION_H, 200001))))


# --- 06 · NEWTON ------------------------------------------------------
# x^3 - 2x - 5 = 0 es el ejemplo del propio Newton (1669). La raiz vale
# 2.0945514815423265 y los decimales correctos se DUPLICAN en cada paso.

def f_newton(x):
    x = np.asarray(x, dtype=float)
    return x ** 3 - 2.0 * x - 5.0


def df_newton(x):
    x = np.asarray(x, dtype=float)
    return 3.0 * x ** 2 - 2.0


def raiz_de_newton(x0=2.0, pasos=60):
    """La raiz, iterada hasta que deja de moverse."""
    x = float(x0)
    for _ in range(int(pasos)):
        x = x - float(f_newton(x)) / float(df_newton(x))
    return x


def newton_pasos(x0=2.0, pasos=4):
    """La sucesion completa, incluido el punto de partida."""
    xs = [float(x0)]
    for _ in range(int(pasos)):
        x = xs[-1]
        xs.append(x - float(f_newton(x)) / float(df_newton(x)))
    return xs


def digitos_correctos(x, raiz=None, tope=16):
    """Cuantos decimales correctos tiene una aproximacion.

    Se corta en 16 a proposito: por debajo de 1e-16 ya no se esta
    midiendo el metodo sino el float64, y rotular 17 decimales seria
    rotular una propiedad del ordenador."""
    r = raiz_de_newton() if raiz is None else float(raiz)
    err = abs(float(x) - r)
    if err == 0.0:
        return int(tope)
    return int(min(float(tope), np.floor(-np.log10(err))))


def camino_newton(x0=2.0, pasos=3):
    """Los vertices del zigzag: punto de la curva, bajada al eje, subida.

    Devuelve la poligonal (x, y) tal cual se dibuja: es el metodo entero
    sin una sola formula en pantalla."""
    xs = newton_pasos(x0, pasos)
    pts = []
    for i, x in enumerate(xs[:-1]):
        pts.append((x, float(f_newton(x))))
        pts.append((xs[i + 1], 0.0))
        pts.append((xs[i + 1], float(f_newton(xs[i + 1]))))
    return np.array(pts, dtype=float)


# --- 07 · LATA --------------------------------------------------------
# 330 ml. El minimo de aluminio esta en h = 2r (la lata cabe justo en un
# cuadrado) y ninguna lata real tiene esa forma. La pieza NO va de que la
# industria lo haga mal: va de que CERCA DEL MINIMO LA CURVA ES PLANA, que
# es la consecuencia visual de que la derivada valga cero.

VOLUMEN_LATA = 330.0          # cm^3, ELEGIDO (va en gris)
ESBELTEZ_REAL = 11.5 / 6.6    # alto/diametro de una lata de 33 cl, DADO


def superficie_lata(r, V=VOLUMEN_LATA):
    """Aluminio de un cilindro cerrado de radio r y volumen V."""
    r = np.asarray(r, dtype=float)
    return 2.0 * np.pi * r ** 2 + 2.0 * float(V) / r


def lata_optima(V=VOLUMEN_LATA):
    """(radio, altura, superficie) de la lata que menos gasta."""
    V = float(V)
    r = (V / (2.0 * np.pi)) ** (1.0 / 3.0)
    h = V / (np.pi * r ** 2)
    return float(r), float(h), float(superficie_lata(r, V))


def lata_de_esbeltez(s, V=VOLUMEN_LATA):
    """(radio, altura, superficie) de la lata con alto/diametro = s."""
    V, s = float(V), float(s)
    r = (V / (2.0 * s * np.pi)) ** (1.0 / 3.0)
    h = 2.0 * s * r
    return float(r), float(h), float(superficie_lata(r, V))


def exceso_de_la_real(V=VOLUMEN_LATA):
    """Cuanto por ciento de aluminio de mas gasta la forma real."""
    _, _, s_opt = lata_optima(V)
    _, _, s_real = lata_de_esbeltez(ESBELTEZ_REAL, V)
    return float((s_real / s_opt - 1.0) * 100.0)


def coste_de_fallar(fraccion=0.10, V=VOLUMEN_LATA):
    """Lo que cuesta equivocarse un 10 % en el radio, en por ciento.

    Es la cifra que hace la pieza: la derivada vale cero en el minimo, o
    sea que el primer termino del error es CUADRATICO y por eso un fallo
    del 10 % cuesta menos del 1 %."""
    r, _, s_opt = lata_optima(V)
    peor = max(float(superficie_lata(r * (1.0 + fraccion), V)),
               float(superficie_lata(r * (1.0 - fraccion), V)))
    return float((peor / s_opt - 1.0) * 100.0)


# --- 08 · RIEMANN -----------------------------------------------------
# El area bajo x^2 entre 0 y 1. Las dos sumas —la que se queda corta y la
# que se pasa— aprietan el numero entre ellas: eso es lo que hace que la
# respuesta exista, y es lo que se ve.

def f_riemann(x):
    x = np.asarray(x, dtype=float)
    return x ** 2


def suma_riemann(n, modo="inferior", a=0.0, b=1.0):
    """La suma de rectangulos. `modo`: inferior, superior o medio."""
    n = int(n)
    if n < 1:
        raise ValueError("hacen falta rectangulos para sumar")
    bordes = np.linspace(float(a), float(b), n + 1)
    ancho = (float(b) - float(a)) / n
    if modo == "inferior":
        alturas = f_riemann(bordes[:-1])
    elif modo == "superior":
        alturas = f_riemann(bordes[1:])
    elif modo == "medio":
        alturas = f_riemann((bordes[:-1] + bordes[1:]) / 2.0)
    else:
        raise ValueError(f"modo desconocido: {modo}")
    return float(np.sum(alturas) * ancho)


def area_riemann(a=0.0, b=1.0):
    """El valor exacto: b^3/3 - a^3/3."""
    return float((float(b) ** 3 - float(a) ** 3) / 3.0)


def pinza(n):
    """(inferior, superior, lo que las separa)."""
    lo = suma_riemann(n, "inferior")
    hi = suma_riemann(n, "superior")
    return lo, hi, hi - lo


def rectangulos(n, modo="inferior", a=0.0, b=1.0):
    """Los rectangulos como (x_izq, x_der, altura), para dibujarlos."""
    n = int(n)
    bordes = np.linspace(float(a), float(b), n + 1)
    if modo == "inferior":
        alturas = f_riemann(bordes[:-1])
    elif modo == "superior":
        alturas = f_riemann(bordes[1:])
    else:
        alturas = f_riemann((bordes[:-1] + bordes[1:]) / 2.0)
    return [(float(bordes[i]), float(bordes[i + 1]), float(alturas[i]))
            for i in range(n)]


# --- 09 · TEOREMA FUNDAMENTAL -----------------------------------------
# Arriba, una funcion y el area que se va llenando. Abajo, esa area
# dibujada segun crece. Y la pendiente de la de abajo es la ALTURA de la
# de arriba, en todos los puntos a la vez.

X_TFC = (0.0, 5.0)


def f_tfc(x):
    """Positiva en todo el tramo: el area solo crece, nunca se descuenta."""
    x = np.asarray(x, dtype=float)
    return 1.2 + np.sin(x)


def area_tfc(x):
    """El area acumulada desde 0, en forma cerrada: 1.2x + 1 - cos x."""
    x = np.asarray(x, dtype=float)
    return 1.2 * x + 1.0 - np.cos(x)


def area_acumulada(N=4001):
    """Lo mismo, sumando trapecios: el area que de verdad se dibuja."""
    xs = np.linspace(X_TFC[0], X_TFC[1], int(N))
    ys = f_tfc(xs)
    paso = xs[1] - xs[0]
    acum = np.concatenate(([0.0], np.cumsum((ys[:-1] + ys[1:]) / 2.0) * paso))
    return xs, acum


def ritmo_del_area(x0, h=1e-4):
    """La pendiente de la curva del area, medida sobre la curva dibujada.

    Diferencia CENTRADA: la de un lado se equivoca en h*f'/2, que a
    cuatro decimales se nota y convertiria la coincidencia de la pieza en
    un casi."""
    x0, h = float(x0), float(h)
    return float((area_tfc(x0 + h) - area_tfc(x0 - h)) / (2.0 * h))


def altura_y_ritmo(x0):
    """(altura de arriba, pendiente de abajo). La pieza entera."""
    return float(f_tfc(x0)), ritmo_del_area(x0)


# --- 10 · HIPERBOLA ---------------------------------------------------
# El area bajo 1/x entre 1 y 2 es la misma que entre 2 y 4, y que entre 4
# y 8: estirar al doble a lo ancho y encoger a la mitad a lo alto deja la
# franja con la misma area. Por eso ese area convierte productos en
# sumas, o sea, por eso es un logaritmo.

def hiperbola(x):
    return 1.0 / np.asarray(x, dtype=float)


def area_hiperbola(a, b, N=200001):
    """El area bajo 1/x, por trapecios. Nada de log() aqui dentro.

    Si se calculara con np.log, la pieza no estaria midiendo nada: el
    logaritmo es la CONCLUSION, no el metodo."""
    a, b = float(a), float(b)
    if a <= 0 or b <= a:
        raise ValueError("la franja va de a a b con 0 < a < b")
    xs = np.linspace(a, b, int(N))
    ys = hiperbola(xs)
    return float(np.trapezoid(ys, xs)) if hasattr(np, "trapezoid") \
        else float(np.trapz(ys, xs))


def franjas_que_doblan(cuantas=4, a=1.0):
    """[(1,2), (2,4), (4,8), ...] y el area de cada una."""
    tramos = []
    x = float(a)
    for _ in range(int(cuantas)):
        tramos.append((x, 2.0 * x, area_hiperbola(x, 2.0 * x)))
        x *= 2.0
    return tramos


def estirada(a, b, factor=2.0, N=400):
    """La franja (a,b) estirada a lo ancho y encogida a lo alto.

    Devuelve las dos curvas superiores: la original y la transformada.
    La segunda cae EXACTAMENTE sobre la hiperbola otra vez, que es lo
    que hace la demostracion."""
    xs = np.linspace(float(a), float(b), int(N))
    return xs, hiperbola(xs), xs * float(factor), hiperbola(xs) / float(factor)


def suma_de_areas(a=1.0, b=2.0, c=4.0):
    """area(a,b) + area(b,c) contra area(a,c): la propiedad del logaritmo."""
    return (area_hiperbola(a, b) + area_hiperbola(b, c),
            area_hiperbola(a, c))


# --- 11 · ESCALERA ----------------------------------------------------
# La escalera que rodea la circunferencia se le pega todo lo que se
# quiera y su perimetro NO baja de 4 diametros. Es la demostracion de que
# la longitud no se puede aproximar por escalones: hace falta la
# derivada, que es lo unico que sabe en que direccion va la curva.

RADIO = 0.5                # diametro 1: asi la escalera mide 4 y el
                           # circulo mide pi, que es la gracia


def escalera_circulo(n, r=RADIO):
    """La poligonal de escalones que envuelve la circunferencia.

    n escalones por cuadrante. Todos los tramos son horizontales o
    verticales y los vertices de dentro tocan la circunferencia."""
    n = int(n)
    if n < 1:
        raise ValueError("hace falta al menos un escalon por cuadrante")
    r = float(r)
    ang = np.linspace(0.0, np.pi / 2.0, n + 1)
    cx, cy = r * np.cos(ang), r * np.sin(ang)
    pts = [(cx[0], cy[0])]
    for i in range(n):
        pts.append((cx[i], cy[i + 1]))
        pts.append((cx[i + 1], cy[i + 1]))
    q = np.array(pts, dtype=float)
    # Los tres cuadrantes que faltan son el primero GIRADO, y girado sin
    # invertir el orden: al reves, el camino vuelve sobre sus pasos y
    # aparecen tramos en diagonal que no son escalones. Se noto porque la
    # escalera media 6.82 —la circunferencia— en vez de 4.
    giros = [q,
             np.column_stack((-q[:, 1], q[:, 0]))[1:],
             np.column_stack((-q[:, 0], -q[:, 1]))[1:],
             np.column_stack((q[:, 1], -q[:, 0]))[1:]]
    entera = np.vstack(giros)
    return np.vstack((entera, entera[:1]))


def longitud_poligonal(pts):
    """La suma de los tramos de una poligonal cerrada o abierta."""
    p = np.asarray(pts, dtype=float)
    return float(np.sum(np.hypot(np.diff(p[:, 0]), np.diff(p[:, 1]))))


def poligono_inscrito(n, r=RADIO):
    """El poligono de n lados con los vertices en la circunferencia."""
    n = int(n)
    ang = np.linspace(0.0, 2.0 * np.pi, n + 1)
    return np.column_stack((float(r) * np.cos(ang), float(r) * np.sin(ang)))


def longitud_circunferencia(r=RADIO):
    return float(2.0 * np.pi * float(r))


def longitud_por_la_derivada(f, df, a, b, N=200001):
    """La longitud de una curva y=f(x), integrando raiz(1+f'^2).

    Es lo que la escalera no sabe hacer: mirar HACIA DONDE va la curva
    en cada punto en vez de cuanto sube y cuanto avanza."""
    xs = np.linspace(float(a), float(b), int(N))
    g = np.sqrt(1.0 + np.asarray(df(xs), dtype=float) ** 2)
    return float(np.trapezoid(g, xs)) if hasattr(np, "trapezoid") \
        else float(np.trapz(g, xs))


def semicircunferencia_por_derivada(r=RADIO, recorte=1e-4, N=400001):
    """La mitad de arriba de la circunferencia, por la integral de arco.

    El recorte evita los dos extremos, donde la pendiente es infinita:
    se dice en pantalla y se cuenta lo que falta (menos de 1e-3)."""
    r, e = float(r), float(recorte)
    xs = np.linspace(-r + e, r - e, int(N))
    ys = np.sqrt(np.maximum(r ** 2 - xs ** 2, 0.0))
    dy = -xs / np.maximum(ys, 1e-300)
    g = np.sqrt(1.0 + dy ** 2)
    trapecio = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    cuerpo = float(trapecio(g, xs))
    puntas = 2.0 * float(r) * np.arcsin(np.sqrt(e / (2.0 * r)) * 2.0) \
        if e > 0 else 0.0
    return cuerpo, float(puntas)


# --- 12 · CAMPANA -----------------------------------------------------
# e^(-x^2) no tiene primitiva elemental: el area se puede MEDIR pero no
# despejar. Y sin embargo vale exactamente raiz de pi, y se ve por que:
# al girar la campana, el volumen se corta en anillos y el area de cada
# anillo trae el factor r que faltaba para poder integrar.

def campana(x):
    x = np.asarray(x, dtype=float)
    return np.exp(-x ** 2)


def area_campana(lim=6.0, N=200001):
    """El area bajo la campana, por trapecios."""
    xs = np.linspace(-float(lim), float(lim), int(N))
    trapecio = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return float(trapecio(campana(xs), xs))


def anillo(r):
    """El area de un anillo de radio r y grosor 1 bajo la campana girada.

    2*pi*r*e^(-r^2). Ese r de delante es el que lo cambia todo: la
    primitiva de r*e^(-r^2) SI es elemental."""
    r = np.asarray(r, dtype=float)
    return 2.0 * np.pi * r * np.exp(-r ** 2)


def volumen_campana(lim=8.0, N=200001):
    """El volumen de la campana girada, sumando anillos."""
    rs = np.linspace(0.0, float(lim), int(N))
    trapecio = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return float(trapecio(anillo(rs), rs))


def raiz_de_pi():
    """La raiz del volumen: el area de la campana, ahora exacta."""
    return float(np.sqrt(volumen_campana()))


def radios_de_anillos(cuantos=14, lim=2.4):
    """Los radios de los anillos que se dibujan, y su peso relativo."""
    rs = np.linspace(lim / cuantos, float(lim), int(cuantos))
    pesos = np.exp(-rs ** 2)
    return [(float(r), float(p)) for r, p in zip(rs, pesos)]


# --- 13 · CAVALIERI ---------------------------------------------------
# La esfera, los dos conos y el cilindro que los contiene: a cualquier
# altura, el circulo de la esfera y el del cono suman el del cilindro.
# Rebanada a rebanada. Arquimedes lo pidio en su tumba.

def radios_rebanada(y, R):
    """(radio de la esfera, radio del cono, radio del cilindro) a altura y."""
    y, R = float(y), float(R)
    if abs(y) > R:
        raise ValueError("la rebanada tiene que caer dentro del cilindro")
    return float(np.sqrt(R ** 2 - y ** 2)), abs(y), R


def areas_rebanada(y, R):
    """Las tres areas: esfera + cono contra cilindro."""
    re, rc, rl = radios_rebanada(y, R)
    return np.pi * re ** 2, np.pi * rc ** 2, np.pi * rl ** 2


def volumen_esfera(R, N=200001):
    """Por rebanadas, no por formula: es lo que enseña la pieza."""
    R = float(R)
    ys = np.linspace(-R, R, int(N))
    trapecio = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return float(trapecio(np.pi * (R ** 2 - ys ** 2), ys))


def volumen_cilindro(R):
    return float(2.0 * np.pi * float(R) ** 3)


def volumen_conos(R, N=200001):
    R = float(R)
    ys = np.linspace(-R, R, int(N))
    trapecio = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return float(trapecio(np.pi * ys ** 2, ys))


def razon_esfera_cilindro(R=5.0):
    return float(volumen_esfera(R) / volumen_cilindro(R))


# --- 14 · CEBOLLA -----------------------------------------------------
# Un circulo es una pila de anillos. Se desenrollan y se apilan: sale un
# triangulo de base 2*pi*R y altura R. Su area es pi*R^2, que es la del
# circulo, y ademas explica por que la derivada del area es el borde.

def area_circulo(R):
    return float(np.pi * float(R) ** 2)


def perimetro_circulo(R):
    return float(2.0 * np.pi * float(R))


def anillos_circulo(R, n):
    """[(radio interior, radio exterior, radio medio, grosor)] de n anillos."""
    R, n = float(R), int(n)
    bordes = np.linspace(0.0, R, n + 1)
    return [(float(bordes[i]), float(bordes[i + 1]),
             float((bordes[i] + bordes[i + 1]) / 2.0),
             float(bordes[i + 1] - bordes[i])) for i in range(n)]


def area_por_tiras(R, n):
    """El area del triangulo de tiras desenrolladas.

    Con el radio MEDIO de cada anillo sale exacta para cualquier n, y no
    es un truco: el area de verdad del anillo es pi(re^2-ri^2) =
    2*pi*rmedio*grosor. La tira desenrollada es un trapecio, y su area es
    la del anillo, sin aproximar."""
    return float(sum(2.0 * np.pi * rm * g
                     for _, _, rm, g in anillos_circulo(R, n)))


def derivada_del_area(R, h=1e-5):
    """d(area)/dR medido sobre el area: tiene que salir el perimetro."""
    R, h = float(R), float(h)
    return float((area_circulo(R + h) - area_circulo(R - h)) / (2.0 * h))


# --- 15 · ANILLO DE SERVILLETA ----------------------------------------
# Se taladra una esfera de lado a lado y queda un anillo de altura h. Su
# volumen es pi*h^3/6: NO depende del radio de la esfera. Una canica y un
# planeta, con el mismo agujero de 6 cm de alto, dejan el mismo anillo.

def radio_del_agujero(R, h):
    """El radio del taladro que deja un anillo de altura h."""
    R, h = float(R), float(h)
    if h > 2.0 * R:
        raise ValueError("el anillo no puede ser mas alto que la esfera")
    return float(np.sqrt(R ** 2 - (h / 2.0) ** 2))


def area_corona(y, R, h):
    """El area de la corona a altura y: circulo de la esfera menos taladro."""
    R, h, y = float(R), float(h), float(y)
    c = radio_del_agujero(R, h)
    return float(np.pi * ((R ** 2 - y ** 2) - c ** 2))


RADIO_MAXIMO = 1e5         # cm: el techo de float64 para esta resta


def volumen_anillo(R, h, N=200001):
    """El volumen del anillo, integrando coronas de verdad.

    R entra en la cuenta en dos sitios y se va solo: eso es lo que hay
    que ver, y por eso NO se usa la formula cerrada aqui.

    Y por eso mismo hay un techo. La corona es (R^2 - y^2) - c^2, o sea
    la resta de dos numeros que valen casi lo mismo: con R = 6.4e8 (un
    planeta en centimetros) los dos pasan de 4e17, la separacion entre
    dos float64 consecutivos ahi arriba es de 64, y una resta que vale 9
    sale CERO. Sin aviso.

    Y antes de llegar a cero pasa algo peor: con R = 1e6 devuelve
    113.0996 en vez de 113.0973. Un numero creible, con dos decimales,
    que nadie discutiria. El techo esta puesto en 1e5 cm —una esfera de
    un kilometro de radio, que ya es absurda de sobra para la pieza— y
    por encima aborta en vez de devolver eso."""
    R, h = float(R), float(h)
    if R > RADIO_MAXIMO:
        raise ValueError(
            f"radio {R:.3g} cm: por encima de {RADIO_MAXIMO:.0g} la resta "
            f"(R^2-y^2)-c^2 se pierde en el float64 y el volumen deja de "
            f"ser el volumen (primero se desvia, luego sale cero). "
            f"Para esferas mayores esta volumen_anillo_formula(h), que ya "
            f"tiene la resta hecha a mano")
    ys = np.linspace(-h / 2.0, h / 2.0, int(N))
    c = radio_del_agujero(R, h)
    areas = np.pi * ((R ** 2 - ys ** 2) - c ** 2)
    trapecio = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return float(trapecio(areas, ys))


def volumen_anillo_formula(h):
    """pi*h^3/6, para comprobar contra la integral."""
    return float(np.pi * float(h) ** 3 / 6.0)


# --- 16 · TROMPETA DE GABRIEL -----------------------------------------
# El solido de 1/x girado alrededor del eje, de 1 en adelante. El volumen
# converge a pi; la superficie crece como el logaritmo y no para. Se
# llena con pi de pintura y con esa pintura no se puede pintar por dentro.

def volumen_trompeta(X):
    """pi*(1 - 1/X). Converge a pi."""
    X = float(X)
    if X < 1.0:
        raise ValueError("la trompeta empieza en x=1")
    return float(np.pi * (1.0 - 1.0 / X))


def superficie_trompeta(X, N=200001):
    """2*pi * integral de (1/x)*raiz(1+1/x^4).

    Se integra en u = ln x: el integrando pasa a ser raiz(1+e^(-4u)), que
    es suave y acotado. Con malla lineal en x, X=1e6 necesitaria mil
    millones de puntos para que el trapecio valga algo."""
    X = float(X)
    if X < 1.0:
        raise ValueError("la trompeta empieza en x=1")
    us = np.linspace(0.0, np.log(X), int(N))
    trapecio = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return float(2.0 * np.pi * trapecio(np.sqrt(1.0 + np.exp(-4.0 * us)), us))


def perfil_trompeta(X=6.0, N=900):
    """El perfil y=1/x que se gira, y su reflejo."""
    xs = np.linspace(1.0, float(X), int(N))
    return xs, hiperbola(xs)


# --- 17 · TAYLOR ------------------------------------------------------
# El polinomio que se pega a la curva: cada grado que se añade la sigue
# un poco mas lejos. Lo que se mide es HASTA DONDE, que es lo unico que
# de verdad se ve.

GRADOS = (1, 3, 5, 7, 11)
TOLERANCIA = 0.01          # ELEGIDA (va en gris): un 1 % de la amplitud


def taylor_seno(x, grado):
    """La serie del seno truncada en `grado` (impar)."""
    x = np.asarray(x, dtype=float)
    grado = int(grado)
    if grado < 1 or grado % 2 == 0:
        raise ValueError("los terminos del seno son de grado impar")
    total = np.zeros_like(x)
    termino = x.copy()
    k = 1
    while k <= grado:
        total = total + termino
        termino = -termino * x ** 2 / ((k + 1) * (k + 2))
        k += 2
    return total


def error_taylor(x, grado):
    return float(np.max(np.abs(taylor_seno(np.atleast_1d(x), grado)
                               - np.sin(np.atleast_1d(x)))))


def alcance(grado, tol=TOLERANCIA, xmax=14.0, N=140001):
    """Hasta que x el polinomio se mantiene por debajo de la tolerancia.

    Se busca el PRIMER cruce desde el origen, no el ultimo punto bueno:
    mas alla el error vuelve a cruzar la tolerancia por casualidad varias
    veces y quedarse con el maximo daria un alcance que no lo es."""
    xs = np.linspace(0.0, float(xmax), int(N))
    err = np.abs(taylor_seno(xs, grado) - np.sin(xs))
    malos = np.nonzero(err > float(tol))[0]
    return float(xs[malos[0] - 1]) if len(malos) else float(xmax)


def alcances(grados=GRADOS, tol=TOLERANCIA):
    return [(int(g), alcance(g, tol)) for g in grados]


# --- 18 · ARMONICA ----------------------------------------------------
# 1 + 1/2 + 1/3 + ... crece para siempre, y tan despacio que con un millon
# de sumandos no llega a 15. Se ve apoyandola contra el area bajo 1/x: la
# suma va siempre por encima del logaritmo y por debajo de 1 + logaritmo.

def armonica(n):
    """La suma parcial H(n). Sin trucos: se suma."""
    n = int(n)
    if n < 1:
        raise ValueError("la serie empieza en el primer termino")
    return float(np.sum(1.0 / np.arange(1, n + 1, dtype=float)))


def sumas_parciales(n):
    """Todas las H(k) hasta n, para dibujar como crece."""
    return np.cumsum(1.0 / np.arange(1, int(n) + 1, dtype=float))


def gamma_de_euler(n=2000000):
    """H(n) - ln(n). Lo que le sobra a la suma sobre el area."""
    return float(armonica(n) - np.log(float(n)))


def encierra_al_logaritmo(n):
    """(ln n, H(n), 1 + ln n): la suma queda siempre en medio."""
    n = int(n)
    return float(np.log(n)), armonica(n), float(1.0 + np.log(n))


def terminos_para(objetivo, n_ref=2000000):
    """Cuantos sumandos hacen falta para pasar de `objetivo`.

    Se despeja de H(n) ~ ln n + gamma, con la gamma MEDIDA aqui arriba.
    Es una estimacion y se rotula como tal: sumar 1e43 terminos no lo
    hace ningun ordenador."""
    g = gamma_de_euler(n_ref)
    return float(np.exp(float(objetivo) - g))


def bloques(n):
    """Las alturas 1/k, para el dibujo de las columnas."""
    return 1.0 / np.arange(1, int(n) + 1, dtype=float)


# =====================================================================
#  MITAD DE DIBUJO
#
#  Lo generico (marco, curva, ejes, marcas) se importa de especiales.py.
#  Aqui solo esta lo que este curso necesita y aquel no: superficies
#  rellenas, bandas de tolerancia, escalas isotropas para que un circulo
#  salga redondo, y las cuatro piezas de mobiliario que se repiten.
# =====================================================================

def _exige_manim():
    if not _HAY_MANIM:
        raise RuntimeError(
            "las piezas de dibujo de calculo.py necesitan manim y lienzo; "
            "la mitad numerica se importa sin ellos a proposito")


RELLENO = 0.17             # el area pintada: se ve y no tapa la curva


def marco_igual(rango_x, rango_y, ancho=5.2, alto=4.4):
    """Como `marco`, pero con la MISMA escala en los dos ejes.

    Media docena de piezas de este curso dibujan circunferencias, y un
    marco que estira x y y por separado convierte cualquier circulo en
    una elipse sin avisar: la esfera de Cavalieri saldria achatada
    justo en la pieza que afirma que sus rebanadas son circulos.

    La caja resultante puede ser mas estrecha o mas baja que lo pedido
    —`punto.ancho` y `punto.alto` dicen lo que de verdad ocupa— y trae
    `punto.escala`, que es lo que necesita `circulo_en` para que un radio
    de datos se convierta en un radio de escena."""
    _exige_manim()
    x0, x1 = float(rango_x[0]), float(rango_x[1])
    y0, y1 = float(rango_y[0]), float(rango_y[1])
    dx, dy = (x1 - x0) or 1.0, (y1 - y0) or 1.0
    s = min(float(ancho) / dx, float(alto) / dy)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    def punto(xi, yi):
        return np.array([(float(xi) - cx) * s, (float(yi) - cy) * s, 0.0])

    punto.rango_x = (x0, x1)
    punto.rango_y = (y0, y1)
    punto.ancho = dx * s
    punto.alto = dy * s
    punto.escala = s
    return punto


def circulo_en(punto, cx, cy, r, color=None, grosor=TRAZO_FINO):
    """Una circunferencia de radio `r` EN DATOS, centrada en (cx, cy).

    Exige un marco isotropo: con `marco` normal el radio no significa
    nada porque x e y van a escalas distintas."""
    _exige_manim()
    if not hasattr(punto, "escala"):
        raise _lz.FueraDelLienzo(
            "circulo_en necesita un marco_igual: en un marco de escalas "
            "distintas un circulo de datos no es un circulo de pantalla")
    c = Circle(radius=float(r) * punto.escala,
               stroke_color=color or _lz.TINTA, stroke_width=grosor)
    c.set_fill(opacity=0.0)
    c.move_to(punto(cx, cy))
    return c


def region(x, y, punto, color=None, opacidad=RELLENO, base=0.0):
    """El area entre una curva y una horizontal, pintada.

    Medio curso habla de areas, asi que el area tiene que verse. Va sin
    trazo: el borde ya lo pone la curva, y repetirlo engorda la linea y
    la desplaza medio pixel."""
    _exige_manim()
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    bueno = np.isfinite(x) & np.isfinite(y)
    x, y = x[bueno], y[bueno]
    pts = [punto(xi, yi) for xi, yi in zip(x, y)]
    pts.append(punto(x[-1], base))
    pts.append(punto(x[0], base))
    g = VMobject(stroke_width=0.0, fill_color=color or _lz.AMBAR,
                 fill_opacity=float(opacidad))
    g.set_points_as_corners(pts + [pts[0]])
    return g


def rectangulos_dibujados(rects, punto, color=None, opacidad=RELLENO,
                          grosor=TRAZO_PELO):
    """Los rectangulos de una suma de Riemann, con su borde.

    El borde importa: sin el, cuarenta rectangulos pegados se ven como
    una mancha y la pieza deja de enseñar que son rectangulos."""
    _exige_manim()
    col = color or _lz.AMBAR
    grupo = VGroup()
    for xi, xf, alt in rects:
        esquinas = [punto(xi, 0.0), punto(xf, 0.0),
                    punto(xf, alt), punto(xi, alt)]
        r = VMobject(stroke_color=col, stroke_width=grosor,
                     fill_color=col, fill_opacity=float(opacidad))
        r.set_points_as_corners(esquinas + [esquinas[0]])
        grupo.add(r)
    return grupo


def banda(punto, desde, hasta, vertical_=False, color=None, opacidad=0.13):
    """La franja de tolerancia: horizontal (en y) o vertical (en x).

    Es el unico sitio del curso donde el color pinta una REGION que no
    es un area medida, asi que va mas apagada que `region` y sin borde:
    tiene que leerse como 'aqui dentro', no como 'esto vale tanto'."""
    _exige_manim()
    x0, x1 = punto.rango_x
    y0, y1 = punto.rango_y
    if vertical_:
        esquinas = [punto(desde, y0), punto(hasta, y0),
                    punto(hasta, y1), punto(desde, y1)]
    else:
        esquinas = [punto(x0, desde), punto(x1, desde),
                    punto(x1, hasta), punto(x0, hasta)]
    g = VMobject(stroke_width=0.0, fill_color=color or _lz.CIAN,
                 fill_opacity=float(opacidad))
    g.set_points_as_corners(esquinas + [esquinas[0]])
    return g


def silueta_lata(r, h, escala=1.0, color=None, grosor=TRAZO):
    """Una lata vista de lado: el cuerpo y la tapa insinuada.

    La tapa es media elipse a trozos y no una elipse entera: la mitad de
    abajo se veria a traves del metal, que es justo lo que un dibujo de
    una lata no debe sugerir."""
    _exige_manim()
    r, h, s = float(r) * escala, float(h) * escala, 1.0
    col = color or _lz.AMBAR
    tapa = float(r) * 0.30
    cuerpo = VMobject(stroke_color=col, stroke_width=grosor)
    cuerpo.set_points_as_corners([
        np.array([-r, h / 2.0, 0.0]), np.array([-r, -h / 2.0, 0.0]),
        np.array([r, -h / 2.0, 0.0]), np.array([r, h / 2.0, 0.0])])
    arco = Arc(radius=1.0, start_angle=0.0, angle=np.pi,
               stroke_color=col, stroke_width=grosor)
    arco.stretch_to_fit_width(2.0 * r)
    arco.stretch_to_fit_height(tapa)
    arco.move_to(np.array([0.0, h / 2.0 + tapa / 2.0, 0.0]))
    fondo = Arc(radius=1.0, start_angle=np.pi, angle=np.pi,
                stroke_color=col, stroke_width=grosor)
    fondo.stretch_to_fit_width(2.0 * r)
    fondo.stretch_to_fit_height(tapa)
    fondo.move_to(np.array([0.0, -h / 2.0 - tapa / 2.0 + 0.001, 0.0]))
    return VGroup(cuerpo, arco, fondo).scale(s)


def anillos_concentricos(radios, escala, color=None, grosor=TRAZO_FINO,
                         minimo=0.10):
    """Circunferencias concentricas con la opacidad de su peso.

    Es la campana girada, dibujada sin salir del plano: cada anillo se ve
    tanto como pesa. El suelo de opacidad evita que los de fuera
    desaparezcan del todo y el dibujo parezca recortado."""
    _exige_manim()
    col = color or _lz.AMBAR
    grupo = VGroup()
    for r, peso in radios:
        c = Circle(radius=float(r) * float(escala), stroke_color=col,
                   stroke_width=grosor)
        c.set_fill(opacity=0.0)
        c.set_stroke(opacity=float(max(minimo, min(1.0, peso))))
        grupo.add(c)
    return grupo


def barras(alturas, punto, color=None, hueco=0.18, grosor=TRAZO_PELO,
           opacidad=RELLENO):
    """Columnas de anchura uniforme apoyadas en y=0, una por altura.

    Las columnas van en coordenadas de datos: la k-esima ocupa de k a
    k+1, que es exactamente el rectangulo con el que se compara la serie
    con el area bajo la hiperbola."""
    _exige_manim()
    col = color or _lz.AMBAR
    grupo = VGroup()
    for k, alt in enumerate(np.asarray(alturas, dtype=float), start=1):
        xi, xf = k + float(hueco) / 2.0, k + 1.0 - float(hueco) / 2.0
        esquinas = [punto(xi, 0.0), punto(xf, 0.0),
                    punto(xf, alt), punto(xi, alt)]
        r = VMobject(stroke_color=col, stroke_width=grosor,
                     fill_color=col, fill_opacity=float(opacidad))
        r.set_points_as_corners(esquinas + [esquinas[0]])
        grupo.add(r)
    return grupo


def tiras(anillos, punto, color=None, grosor=TRAZO_PELO, opacidad=RELLENO):
    """Los anillos desenrollados: trapecios apilados que forman el triangulo.

    Cada anillo entra como el trapecio que de verdad es —base 2*pi*ri
    abajo y 2*pi*re arriba—, no como un rectangulo: apilar rectangulos
    dejaria escalones y la pieza afirma que sale un TRIANGULO."""
    _exige_manim()
    col = color or _lz.AMBAR
    grupo = VGroup()
    for ri, re, _rm, _g in anillos:
        b0, b1 = 2.0 * np.pi * ri, 2.0 * np.pi * re
        esquinas = [punto(-b1 / 2.0, re), punto(b1 / 2.0, re),
                    punto(b0 / 2.0, ri), punto(-b0 / 2.0, ri)]
        t = VMobject(stroke_color=col, stroke_width=grosor,
                     fill_color=col, fill_opacity=float(opacidad))
        t.set_points_as_corners(esquinas + [esquinas[0]])
        grupo.add(t)
    return grupo


def colgante(punto, x, y, color=None, grosor=TRAZO_PELO, trozos=10):
    """Una discontinua desde el SUELO DEL CUADRO hasta el punto marcado.

    `plomada` (de especiales.py) cuelga del CERO, que es lo que hay que
    hacer cuando el cero esta dentro del cuadro. Cuando no lo esta —una
    curva de coste que va de 250 a 322 cm2, por ejemplo— esa plomada se va
    siete unidades por debajo del dibujo: el grupo pasa a medir el triple
    de lo que se ve, `encajar` lo encoge todo para que quepa y el render
    aborta por el guardian de legibilidad con "el rotulo mas pequeño mide
    0.101". El sintoma no señala la causa, que es esta.

    Asi que cuando el cuadro no contiene el cero, la referencia es su
    suelo."""
    _exige_manim()
    y0 = punto.rango_y[0]
    ln = Line(punto(x, y0), punto(x, y),
              stroke_color=color or _lz.APAGADO, stroke_width=grosor)
    return DashedVMobject(ln, num_dashes=int(trozos))


def segmento(punto, x0, y0, x1, y1, color=None, grosor=TRAZO_FINO,
             a_trozos=False):
    """Un tramo recto entre dos puntos de datos."""
    _exige_manim()
    ln = Line(punto(x0, y0), punto(x1, y1),
              stroke_color=color or _lz.TINTA, stroke_width=grosor)
    return DashedVMobject(ln, num_dashes=14) if a_trozos else ln

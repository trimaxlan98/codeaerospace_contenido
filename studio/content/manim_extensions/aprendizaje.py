"""Aprendizaje automatico animable: datos, descenso de gradiente y fronteras.

Pensado para el curso "Redes neuronales: la maquina que aprende". Todo el
calculo es numpy puro y determinista (`np.random.default_rng(semilla)`, nunca
el `random` global): mismo script -> mismo render, condicion necesaria para
trabajar con `--disable_caching`. Nada de red ni de disco.

La parte visual sigue la regla de color del curso: los DATOS son cian y
violeta, el MODELO es ambar, la PERDIDA es roja. Las regiones de decision se
muestran como un unico ImageMobject (jamas un mobject por pixel), mezclado
contra el fondo de marca CODE_BG y con z_index bajo para quedar debajo de los
puntos.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render): `RES_MAX`,
`EPOCAS_MAX` y `PUNTOS_MAX` recortan en silencio, como hace fractales.py.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from aprendizaje import (datos_xor, entrenar_mlp, puntos_datos,
                             frontera_imagen, curva_perdida)

    X, y = datos_xor()
    ent = entrenar_mlp(X, y)              # converge: perdida final ~1e-3
    self.add(frontera_imagen(ejes, ent.modelos[-1]), puntos_datos(ejes, X, y))
"""

import numpy as np

from manim import (AnimationGroup, Dot, ImageMobject, Indicate, Line,
                   ShowPassingFlash, Succession, VGroup, VMobject)

from code_brand import CODE_BG

# Limites duros: se recortan en silencio (patron de fractales.py).
RES_MAX = 512           # lado maximo en pixeles de cualquier malla calculada
EPOCAS_MAX = 4000       # epocas maximas de cualquier entrenamiento
PUNTOS_MAX = 400        # puntos maximos de cualquier dataset

# Paleta propia de la libreria (coincide con la del curso).
COLOR_A = "#22d3ee"         # datos clase A / flujo hacia adelante
COLOR_B = "#a78bfa"         # datos clase B
COLOR_MODELO = "#f59e0b"    # el modelo: rectas, fronteras, bola de gradiente
COLOR_PERDIDA = "#f43f5e"   # error, perdida, divergencia
FONDO = CODE_BG             # fondo de marca contra el que se mezcla todo

_EPS = 1e-9


# --- utilidades internas ----------------------------------------------
def _hex_a_rgb(hexcolor):
    h = str(hexcolor).lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def _sigmoide(z):
    """Sigmoide estable: el clip evita overflow en exp con logits grandes."""
    return 1.0 / (1.0 + np.exp(-np.clip(z, -60.0, 60.0)))


def _rango(ejes, eje="x"):
    """(minimo, maximo) del rango de unos Axes, como floats."""
    r = ejes.x_range if eje == "x" else ejes.y_range
    return float(r[0]), float(r[1])


def _tope_puntos(n):
    return int(max(4, min(int(n), PUNTOS_MAX)))


# --- datasets ----------------------------------------------------------
# Todos devuelven (X, y) con X (n,2) recortada a [-2, 2]^2 e y en {0, 1}.
def datos_dos_nubes(n=60, separacion=1.5, semilla=7):
    """Dos nubes gaussianas linealmente separables, en diagonal.

    La clase 0 vive abajo-izquierda y la 1 arriba-derecha, a `separacion`
    del origen sobre la diagonal. Una sola recta basta para separarlas: es
    el dataset del clip de la neurona.
    """
    n = _tope_puntos(n)
    rng = np.random.default_rng(semilla)
    direccion = np.array([1.0, 1.0]) / np.sqrt(2.0)
    mitad = n // 2
    tam = (mitad, n - mitad)
    nubes, etiquetas = [], []
    for k, m in enumerate(tam):
        centro = direccion * separacion * (1.0 if k else -1.0)
        nubes.append(centro + rng.normal(0.0, 0.36, size=(m, 2)))
        etiquetas.append(np.full(m, float(k)))
    return _mezclar(np.concatenate(nubes), np.concatenate(etiquetas), rng)


def datos_circulos(n=90, radio=1.25, ruido=0.14, semilla=7):
    """Anillo (clase 1) rodeando un nucleo central (clase 0).

    No es separable por una recta pero si por una frontera curva: es el
    dataset del clip de sobreajuste.
    """
    n = _tope_puntos(n)
    rng = np.random.default_rng(semilla)
    n_anillo = n // 2
    n_centro = n - n_anillo

    ang = rng.uniform(0.0, 2.0 * np.pi, n_anillo)
    r = radio + rng.normal(0.0, ruido, n_anillo)
    anillo = np.stack([r * np.cos(ang), r * np.sin(ang)], axis=1)

    ang_c = rng.uniform(0.0, 2.0 * np.pi, n_centro)
    r_c = rng.uniform(0.0, 1.0, n_centro) ** 0.5 * (radio * 0.42)
    centro = np.stack([r_c * np.cos(ang_c), r_c * np.sin(ang_c)], axis=1)
    centro += rng.normal(0.0, ruido * 0.5, size=centro.shape)

    X = np.concatenate([centro, anillo])
    y = np.concatenate([np.zeros(n_centro), np.ones(n_anillo)])
    return _mezclar(X, y, rng)


def datos_xor(n=56, ruido=0.16, semilla=7):
    """Cuatro racimos alternos en las esquinas: el clasico problema XOR.

    Diagonal principal (--, ++) clase 0; anti-diagonal (-+, +-) clase 1.
    Ninguna recta los separa; hacen falta capas ocultas.
    """
    n = _tope_puntos(n)
    rng = np.random.default_rng(semilla)
    centros = np.array([[-1.0, -1.0], [1.0, 1.0], [-1.0, 1.0], [1.0, -1.0]])
    clases = np.array([0.0, 0.0, 1.0, 1.0])
    por_racimo = n // 4
    resto = n - por_racimo * 4
    nubes, etiquetas = [], []
    for k in range(4):
        m = por_racimo + (1 if k < resto else 0)
        nubes.append(centros[k] + rng.normal(0.0, ruido, size=(m, 2)))
        etiquetas.append(np.full(m, clases[k]))
    return _mezclar(np.concatenate(nubes), np.concatenate(etiquetas), rng)


def datos_recta(n=26, pendiente=0.55, ordenada=0.25, ruido=0.28, semilla=7):
    """Nube 1D alrededor de una recta: (xs, ys) para el clip de regresion.

    A diferencia de los demas datasets NO devuelve etiquetas: son dos
    arrays 1D de longitud n con xs repartidos en [-2, 2] e ys ruidosos.
    """
    n = _tope_puntos(n)
    rng = np.random.default_rng(semilla)
    xs = np.sort(rng.uniform(-1.9, 1.9, n))
    ys = pendiente * xs + ordenada + rng.normal(0.0, ruido, n)
    return xs, np.clip(ys, -2.0, 2.0)


def _mezclar(X, y, rng):
    """Recorta al cuadrado [-2,2]^2 y baraja con el rng ya sembrado."""
    X = np.clip(np.asarray(X, dtype=np.float64), -2.0, 2.0)
    y = np.asarray(y, dtype=np.float64)
    orden = rng.permutation(len(y))
    return X[orden], y[orden]


# --- calculo: perceptron multicapa ------------------------------------
class MLP:
    """Red 2 -> ocultas (tanh) -> 1 (sigmoide), en numpy puro.

    No entrena por si sola: la construye y la avanza `entrenar_mlp`. Es
    barata de copiar, que es lo que permite guardar instantaneas del
    entrenamiento y animar la frontera epoca a epoca.
    """

    def __init__(self, W1, b1, W2, b2):
        self.W1 = np.asarray(W1, dtype=np.float64)
        self.b1 = np.asarray(b1, dtype=np.float64)
        self.W2 = np.asarray(W2, dtype=np.float64)
        self.b2 = np.asarray(b2, dtype=np.float64)

    @property
    def ocultas(self):
        return int(self.W1.shape[1])

    def predecir(self, X):
        """Probabilidad de la clase 1 para cada fila de X (n,2) -> (n,)."""
        X = np.atleast_2d(np.asarray(X, dtype=np.float64))
        A1 = np.tanh(X @ self.W1 + self.b1)
        return _sigmoide(A1 @ self.W2 + self.b2).ravel()

    def copiar(self):
        return MLP(self.W1.copy(), self.b1.copy(),
                   self.W2.copy(), self.b2.copy())


class Entrenamiento:
    """Historial devuelto por `entrenar_mlp`.

    .perdidas  list[float], una entrada por epoca (BCE de todo el lote).
    .modelos   list[MLP], `instantaneas` copias espaciadas uniformemente;
               la primera es el modelo INICIAL (antes de entrenar) y la
               ultima el modelo FINAL.
    """

    def __init__(self, perdidas, modelos):
        self.perdidas = perdidas
        self.modelos = modelos

    @property
    def modelo(self):
        """Atajo al modelo final."""
        return self.modelos[-1]

    @property
    def perdida_final(self):
        return self.perdidas[-1] if self.perdidas else float("nan")


def _iniciar_mlp(ocultas, rng):
    """Pesos iniciales estilo Xavier: activaciones tanh sin saturar."""
    W1 = rng.normal(0.0, 1.0, (2, ocultas)) * np.sqrt(1.0 / 2.0)
    W2 = rng.normal(0.0, 1.0, (ocultas, 1)) * np.sqrt(1.0 / ocultas)
    return MLP(W1, np.zeros(ocultas), W2, np.zeros(1))


def entrenar_mlp(X, y, ocultas=4, epocas=1200, lr=0.9, semilla=3,
                 instantaneas=12):
    """Entrena el MLP por descenso de gradiente a lote completo sobre BCE.

    Gradiente analitico (nada de diferencias finitas). Los valores por
    defecto estan elegidos para que XOR converja de verdad: con
    `datos_xor()` la perdida final baja a ~1e-3 (< 0.1). Devuelve un
    `Entrenamiento` con el historial de perdidas y las instantaneas.
    """
    X = np.atleast_2d(np.asarray(X, dtype=np.float64))
    Y = np.asarray(y, dtype=np.float64).reshape(-1, 1)
    n = max(1, len(Y))
    epocas = int(max(1, min(int(epocas), EPOCAS_MAX)))
    instantaneas = int(max(2, min(int(instantaneas), epocas + 1)))

    rng = np.random.default_rng(semilla)
    red = _iniciar_mlp(int(max(1, ocultas)), rng)

    # Epocas en las que se guarda copia: 0 = modelo inicial, epocas = final.
    marcas = set(int(v) for v in
                 np.round(np.linspace(0, epocas, instantaneas)).astype(int))
    modelos = [red.copiar()]
    perdidas = []

    for epoca in range(1, epocas + 1):
        A1 = np.tanh(X @ red.W1 + red.b1)
        P = _sigmoide(A1 @ red.W2 + red.b2)
        perdidas.append(float(-np.mean(Y * np.log(P + _EPS) +
                                       (1.0 - Y) * np.log(1.0 - P + _EPS))))
        # Retropropagacion: dBCE/dZ2 = (P - Y)/n con la sigmoide ya dentro.
        dZ2 = (P - Y) / n
        dW2 = A1.T @ dZ2
        db2 = dZ2.sum(axis=0)
        dZ1 = (dZ2 @ red.W2.T) * (1.0 - A1 * A1)
        dW1 = X.T @ dZ1
        db1 = dZ1.sum(axis=0)
        red.W2 -= lr * dW2
        red.b2 -= lr * db2
        red.W1 -= lr * dW1
        red.b1 -= lr * db1
        if epoca in marcas:
            modelos.append(red.copiar())

    return Entrenamiento(perdidas, modelos)


def entrenar_regresion(xs, ys, epocas=60, lr=0.08, m0=-0.4, b0=-0.9):
    """Descenso de gradiente sobre el MSE de una recta y = m x + b.

    Devuelve `list[(m, b, mse)]` con una entrada por epoca (el estado ANTES
    de aplicar el paso, de modo que la primera es la recta inicial mala).
    `m0`/`b0` son la recta de partida del clip de regresion.
    """
    xs = np.asarray(xs, dtype=np.float64).ravel()
    ys = np.asarray(ys, dtype=np.float64).ravel()
    epocas = int(max(1, min(int(epocas), EPOCAS_MAX)))
    n = max(1, xs.size)
    m, b = float(m0), float(b0)
    historial = []
    for _ in range(epocas):
        residuo = ys - (m * xs + b)
        historial.append((m, b, float(np.mean(residuo * residuo))))
        m += lr * 2.0 * float(np.sum(xs * residuo)) / n
        b += lr * 2.0 * float(np.sum(residuo)) / n
    return historial


def descenso_1d(df, x0=1.8, lr=0.3, pasos=8):
    """Trayectoria x_k del descenso x_{k+1} = x_k - lr * df(x_k).

    `df` es la DERIVADA de la funcion de perdida. Devuelve pasos+1 floats
    (incluye x0). Se corta si la trayectoria diverge por encima de 1e6,
    para poder animar tambien el caso de lr demasiado grande sin desbordar.
    """
    xs = [float(x0)]
    x = float(x0)
    for _ in range(int(max(0, pasos))):
        x = x - lr * float(df(x))
        if not np.isfinite(x) or abs(x) > 1e6:
            break
        xs.append(x)
    return xs


# --- mobjects (siempre reciben los ejes y usan ejes.c2p) --------------
def puntos_datos(ejes, X, y, color_a=COLOR_A, color_b=COLOR_B, radio=0.055):
    """VGroup de Dots coloreados por clase sobre `ejes`.

    Clase 0 -> `color_a`, clase 1 -> `color_b`. Los puntos van con z_index
    alto para quedar por encima de cualquier `frontera_imagen`.
    """
    X = np.atleast_2d(np.asarray(X, dtype=np.float64))
    y = np.asarray(y, dtype=np.float64).ravel()
    grupo = VGroup()
    for (px, py), etiqueta in zip(X, y):
        color = color_b if etiqueta >= 0.5 else color_a
        punto = Dot(ejes.c2p(float(px), float(py)), radius=radio,
                    color=color, fill_opacity=1.0)
        punto.set_z_index(2)
        grupo.add(punto)
    return grupo


def _probabilidades(modelo, res_x, res_y, x0, x1, y0, y1):
    """Malla (res_y, res_x) con la probabilidad del modelo, fila 0 arriba."""
    xs = np.linspace(x0, x1, res_x)
    ys = np.linspace(y1, y0, res_y)      # filas de arriba a abajo (imagen)
    mx, my = np.meshgrid(xs, ys)
    malla = np.stack([mx.ravel(), my.ravel()], axis=1)
    predecir = getattr(modelo, "predecir", modelo)
    p = np.asarray(predecir(malla), dtype=np.float64).ravel()
    return np.clip(p, 0.0, 1.0).reshape(res_y, res_x)


def frontera_imagen(ejes, modelo, color_a=COLOR_A, color_b=COLOR_B,
                    res=(200, 200), opacidad=0.5):
    """Mapa de decision del modelo como ImageMobject encajado en `ejes`.

    Evalua `modelo.predecir` sobre la malla del rango de los ejes y mezcla
    `color_a` (probabilidad 0) y `color_b` (probabilidad 1) contra el FONDO
    de marca segun la confianza: la frontera queda oscura y las regiones
    seguras saturadas, asi que con `opacidad=0.5` se lee bien debajo de los
    puntos. La colocacion es la de fractales.imagen_mandelbrot pero
    estirada al area exacta de los ejes (esquina c2p(x0,y0) a c2p(x1,y1)),
    con z_index bajo.
    """
    res_x = int(max(2, min(int(res[0]), RES_MAX)))
    res_y = int(max(2, min(int(res[1]), RES_MAX)))
    x0, x1 = _rango(ejes, "x")
    y0, y1 = _rango(ejes, "y")

    p = _probabilidades(modelo, res_x, res_y, x0, x1, y0, y1)
    rgb_a = _hex_a_rgb(color_a)
    rgb_b = _hex_a_rgb(color_b)
    rgb_fondo = _hex_a_rgb(FONDO)

    color = rgb_a[None, None, :] + (rgb_b - rgb_a)[None, None, :] * p[..., None]
    # Confianza 0 justo en la frontera (p=0.5) y 1 en las esquinas seguras;
    # el exponente < 1 ensancha la transicion para que se vea suave.
    confianza = np.abs(2.0 * p - 1.0) ** 0.75
    peso = (0.22 + 0.78 * confianza)[..., None]
    mezcla = rgb_fondo[None, None, :] + (color - rgb_fondo) * peso

    rgba = np.empty((res_y, res_x, 4), dtype=np.uint8)
    rgba[..., :3] = np.clip(mezcla, 0, 255).astype(np.uint8)
    rgba[..., 3] = 255

    img = ImageMobject(np.ascontiguousarray(rgba))
    img.set_resampling_algorithm(3)      # BICUBIC: escala sin pixelado duro
    esquina_ii = ejes.c2p(x0, y0)
    esquina_sd = ejes.c2p(x1, y1)
    img.stretch_to_fit_width(abs(float(esquina_sd[0] - esquina_ii[0])))
    img.stretch_to_fit_height(abs(float(esquina_sd[1] - esquina_ii[1])))
    img.move_to((np.asarray(esquina_ii) + np.asarray(esquina_sd)) / 2.0)
    img.set_opacity(float(np.clip(opacidad, 0.0, 1.0)))
    img.set_z_index(-1)                  # siempre por debajo de los puntos
    return img


def recta_modelo(ejes, m, b, color=COLOR_MODELO, grosor=3.5):
    """Line y = m x + b recortada al rango x de `ejes`.

    Si la recta se sale por arriba o por abajo se recorta tambien contra el
    rango y, para que nunca invada el resto de la composicion. Si no cruza
    el area visible devuelve un segmento degenerado en el borde.
    """
    x0, x1 = _rango(ejes, "x")
    y0, y1 = _rango(ejes, "y")
    m, b = float(m), float(b)

    puntos = []
    for x in (x0, x1):                   # cortes con los bordes verticales
        y = m * x + b
        if y0 - 1e-9 <= y <= y1 + 1e-9:
            puntos.append((x, y))
    if abs(m) > 1e-12:                   # cortes con los bordes horizontales
        for y in (y0, y1):
            x = (y - b) / m
            if x0 - 1e-9 <= x <= x1 + 1e-9:
                puntos.append((x, y))
    if len(puntos) < 2:                  # recta fuera del area visible
        y = float(np.clip(m * x0 + b, y0, y1))
        puntos = [(x0, y), (x1, y)]
    puntos.sort()
    a, z = puntos[0], puntos[-1]
    return Line(ejes.c2p(a[0], a[1]), ejes.c2p(z[0], z[1]),
                color=color, stroke_width=grosor)


def curva_perdida(ejes, perdidas, color=COLOR_PERDIDA, grosor=3.0):
    """Curva de la perdida por esquinas, reescalada al area de `ejes`.

    x = epoca normalizada al rango x completo de los ejes; y = perdida
    normalizada por su maximo y llevada al y_max de los ejes. Asi la curva
    llena el mini-eje sea cual sea la escala real de la perdida.
    """
    valores = np.asarray(list(perdidas), dtype=np.float64).ravel()
    if valores.size == 0:
        return VMobject(color=color, stroke_width=grosor)
    if valores.size == 1:
        valores = np.repeat(valores, 2)

    x0, x1 = _rango(ejes, "x")
    y0, y1 = _rango(ejes, "y")
    pico = float(np.max(np.abs(valores)))
    escala = pico if pico > _EPS else 1.0

    t = np.linspace(0.0, 1.0, valores.size)
    xs = x0 + (x1 - x0) * t
    ys = y0 + (y1 - y0) * np.clip(valores / escala, 0.0, 1.0)

    curva = VMobject(color=color, stroke_width=grosor)
    curva.set_points_as_corners([ejes.c2p(float(a), float(b))
                                 for a, b in zip(xs, ys)])
    return curva


def _salto(p1, p2, curvatura, muestras=24):
    """Arco de salto entre dos puntos de escena, abombado hacia arriba."""
    p1 = np.asarray(p1, dtype=np.float64)
    p2 = np.asarray(p2, dtype=np.float64)
    alto = curvatura * float(np.linalg.norm(p2 - p1))
    t = np.linspace(0.0, 1.0, muestras)
    pts = p1[None, :] + (p2 - p1)[None, :] * t[:, None]
    pts[:, 1] += alto * np.sin(np.pi * t)
    return pts


def camino_descenso(ejes, f, xs, color=COLOR_MODELO, radio=0.09,
                    grosor=3.0, curvatura=0.22):
    """(bola, saltos) para animar una trayectoria de descenso sobre `ejes`.

    `f` es la funcion de perdida y `xs` la trayectoria de `descenso_1d`.
    `bola` es un Dot colocado en (xs[0], f(xs[0])); `saltos` es un VGroup
    con un arco por cada par consecutivo de la trayectoria, en orden, listo
    para animar hop a hop con `Create(saltos[k])` +
    `MoveAlongPath(bola, saltos[k])`.
    """
    xs = [float(v) for v in xs]
    puntos = [np.asarray(ejes.c2p(x, float(f(x))), dtype=np.float64)
              for x in xs]
    bola = Dot(puntos[0], radius=radio, color=color, fill_opacity=1.0)
    bola.set_z_index(3)

    saltos = VGroup()
    for a, z in zip(puntos, puntos[1:]):
        arco = VMobject(color=color, stroke_width=grosor)
        if float(np.linalg.norm(z - a)) < 1e-6:
            arco.set_points_as_corners([a, z])
        else:
            arco.set_points_smoothly(_salto(a, z, curvatura))
        saltos.add(arco)
    return bola, saltos


def retropropagacion(red, color=COLOR_PERDIDA, ancho=4.5, cola=0.5):
    """Pasada hacia atras sobre una `RedNeuronal` de neuronal.py.

    Misma mecanica que `RedNeuronal.activacion` pero recorriendo
    `red.conexiones` en orden INVERSO y con cada linea invertida, de modo
    que el destello viaja de la salida hacia la entrada y pulsa la capa que
    emite la culpa. Devuelve una `Succession` sin updaters residuales.
    """
    pasos = []
    for i in range(len(red.conexiones) - 1, -1, -1):
        grupo = red.conexiones[i]
        capa_destino = red.capas_neuronas[i]
        flashes = []
        for linea in grupo:
            invertida = Line(linea.get_end(), linea.get_start())
            invertida.set_stroke(color=color, width=ancho, opacity=1)
            flashes.append(ShowPassingFlash(invertida, time_width=cola))
        llegada = [Indicate(neurona, color=color, scale_factor=1.25)
                   for neurona in capa_destino]
        pasos.append(AnimationGroup(*flashes, run_time=0.7))
        pasos.append(AnimationGroup(*llegada, run_time=0.45))
    return Succession(*pasos)

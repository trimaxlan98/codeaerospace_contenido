"""Fractales de escape (Mandelbrot / Julia) para Manim CE, aptos para VPS.

Todo el computo es numpy vectorizado con mascara de puntos activos: los
pixeles que escapan salen del bucle y no se vuelven a iterar. El resultado
se muestra como ImageMobject (jamas un mobject por pixel). Sin matplotlib:
las paletas son tablas de interpolacion propias. Todo es determinista
(mismo script -> mismo render, importante para --disable_caching).

Trucos de coste bajo:
  - zoom_fractal(): el zoom NO recalcula por frame; precalcula pocas
    imagenes clave sobremuestreadas y anima su escala con tasa exponencial,
    de modo que cada tramo termina justo cuando la imagen siguiente (mas
    profunda) la reemplaza sin salto visible.
  - morph_julia(): precalcula un lote de fotogramas a resolucion moderada
    y los intercambia en un updater (mutando pixel_array), en vez de
    recalcular el fractal a cada frame del video.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from fractales import (imagen_mandelbrot, imagen_julia, zoom_fractal,
                           morph_julia, orbita, camino_cardioide, PALETAS)

    img = imagen_mandelbrot(alto_escena=8.0)      # llena el frame
    self.play(FadeIn(img))
    zoom_fractal(self, img, centro=-0.7435 + 0.1314j, factor_total=64)
"""

import numpy as np

from manim import ImageMobject, UpdateFromAlphaFunc

# Limites duros para no castigar el VPS (2 vCPU compartidas / 2 GB por render).
RES_MAX = 2200          # ancho maximo en pixeles de cualquier imagen calculada
ITER_MAX = 4000
FRAMES_MORPH_MAX = 220

RADIO_ESCAPE = 8.0      # radio de bailout amplio: suaviza el coloreado
_LUT_N = 1024

# Paletas como puntos de control (posicion 0..1, color hex). Se interpolan
# linealmente a una LUT ciclica de _LUT_N entradas.
PALETAS = {
    "nebulosa": [(0.00, "#050510"), (0.18, "#1b2a6b"), (0.42, "#5643a8"),
                 (0.62, "#c247a6"), (0.80, "#ffb45a"), (0.93, "#fff3d6"),
                 (1.00, "#050510")],
    "fuego":    [(0.00, "#0a0402"), (0.25, "#701606"), (0.50, "#d4441c"),
                 (0.72, "#ff9e2c"), (0.88, "#ffe9a8"), (1.00, "#0a0402")],
    "oceano":   [(0.00, "#03121f"), (0.30, "#0a4c6e"), (0.55, "#15a3b8"),
                 (0.75, "#7ce6d8"), (0.90, "#eafff8"), (1.00, "#03121f")],
    "aurora":   [(0.00, "#060a14"), (0.22, "#0e4d43"), (0.45, "#2fae6b"),
                 (0.65, "#59d4c8"), (0.82, "#9a6bd4"), (1.00, "#060a14")],
}
COLOR_INTERIOR = "#08060f"


def _hex_a_rgb(hexcolor):
    h = hexcolor.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def _lut(paleta):
    """LUT (N,3) float 0..255 interpolada de los puntos de control."""
    puntos = PALETAS[paleta] if isinstance(paleta, str) else paleta
    pos = np.array([p for p, _ in puntos])
    cols = np.stack([_hex_a_rgb(c) for _, c in puntos])
    x = np.linspace(0.0, 1.0, _LUT_N)
    canales = [np.interp(x, pos, cols[:, k]) for k in range(3)]
    return np.stack(canales, axis=1)


def campo_escape(res_x, res_y, centro, ancho, max_iter, c=None, exponente=2):
    """Iteraciones suavizadas de z -> z**exponente + c sobre una malla.

    `c=None` calcula Mandelbrot (c recorre la malla, z0=0); un complejo fijo
    calcula el Julia correspondiente (z0 recorre la malla). Devuelve un array
    (res_y, res_x) float32 con el conteo suavizado; NaN marca el interior.
    """
    res_x = int(min(res_x, RES_MAX))
    res_y = int(min(res_y, RES_MAX))
    max_iter = int(min(max_iter, ITER_MAX))
    alto = ancho * res_y / res_x
    xs = np.linspace(centro.real - ancho / 2, centro.real + ancho / 2,
                     res_x, dtype=np.float64)
    ys = np.linspace(centro.imag - alto / 2, centro.imag + alto / 2,
                     res_y, dtype=np.float64)
    malla = xs[None, :] + 1j * ys[:, None]

    n_px = res_x * res_y
    if c is None:
        c_flat = malla.ravel().astype(np.complex128)
        z = np.zeros(n_px, dtype=np.complex128)
    else:
        c_flat = np.full(n_px, complex(c), dtype=np.complex128)
        z = malla.ravel().astype(np.complex128)

    suave = np.full(n_px, np.nan, dtype=np.float32)
    vivos = np.arange(n_px)          # indices aun no escapados (se comprime)
    r2 = RADIO_ESCAPE * RADIO_ESCAPE
    for n in range(max_iter):
        if exponente == 2:
            z = z * z + c_flat
        else:
            z = z ** exponente + c_flat
        mod2 = z.real * z.real + z.imag * z.imag
        escapo = mod2 > r2
        if escapo.any():
            idx = vivos[escapo]
            # conteo suavizado clasico: n + 1 - log_e(ln|z|)/ln(exponente)
            mod = np.sqrt(mod2[escapo])
            suave[idx] = (n + 1 - np.log(np.log(mod)) /
                          np.log(max(exponente, 2))).astype(np.float32)
            quedan = ~escapo
            vivos = vivos[quedan]
            z = z[quedan]
            c_flat = c_flat[quedan]
        if vivos.size == 0:
            break
    return suave.reshape(res_y, res_x)


def colorear(campo, paleta="nebulosa", ciclo=28.0, desfase=0.0,
             interior=COLOR_INTERIOR):
    """RGBA uint8 a partir del campo suavizado, con paleta ciclica.

    El color depende de (valor % ciclo), no de max_iter: profundizar el
    calculo no cambia el color de los puntos ya escapados (clave para que
    los tramos de zoom_fractal empalmen sin saltos).
    """
    lut = _lut(paleta)
    interior_rgb = _hex_a_rgb(interior)
    dentro = np.isnan(campo)
    t = np.where(dentro, 0.0, ((campo + desfase) % ciclo) / ciclo)
    idx = np.clip((t * (_LUT_N - 1)).astype(np.int32), 0, _LUT_N - 1)
    rgb = lut[idx]
    rgb[dentro] = interior_rgb
    rgba = np.empty(campo.shape + (4,), dtype=np.uint8)
    rgba[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    rgba[..., 3] = 255
    return rgba


def _imagen(rgba, alto_escena):
    img = ImageMobject(rgba)
    img.set_resampling_algorithm(3)  # BICUBIC: escala sin pixelado duro
    if alto_escena is not None:
        img.height = alto_escena
    return img


def imagen_mandelbrot(centro=-0.6 + 0j, ancho=3.4, res=(1280, 720),
                      max_iter=250, paleta="nebulosa", ciclo=28.0,
                      alto_escena=8.0, interior=COLOR_INTERIOR, desfase=0.0):
    """ImageMobject del conjunto de Mandelbrot listo para la escena.

    `interior` pinta lo que NO escapa. En el curso 26 se le pasa el violeta
    del rol "atrapado": asi el conjunto se lee como una pieza solida y el
    color dice lo mismo que la cifra.
    """
    campo = campo_escape(res[0], res[1], centro, ancho, max_iter)
    return _imagen(colorear(campo, paleta, ciclo, desfase, interior),
                   alto_escena)


def imagen_julia(c, centro=0j, ancho=3.6, res=(1280, 720), max_iter=250,
                 paleta="nebulosa", ciclo=28.0, alto_escena=8.0,
                 interior=COLOR_INTERIOR, desfase=0.0):
    """ImageMobject del conjunto de Julia lleno de parametro `c`.

    `interior` pinta a los prisioneros (los que NO escapan).
    """
    campo = campo_escape(res[0], res[1], centro, ancho, max_iter, c=c)
    return _imagen(colorear(campo, paleta, ciclo, desfase, interior),
                   alto_escena)


def _tasa_exponencial(factor):
    """rate_func que hace el zoom geometrico: velocidad angular constante."""
    lf = np.log(factor)

    def tasa(alpha):
        return float((np.exp(lf * alpha) - 1.0) / (factor - 1.0))
    return tasa


def zoom_fractal(escena, imagen_inicial, centro, factor_total, c=None,
                 ancho_inicial=3.4, pasos=None, duracion_paso=3.0,
                 res=(1280, 720), max_iter=300, iter_extra_por_paso=150,
                 paleta="nebulosa", ciclo=28.0, alto_escena=8.0,
                 sobremuestreo=1.6):
    """Zoom continuo hacia `centro` SIN recalcular el fractal por frame.

    Precalcula una imagen clave por paso (cada una `factor_paso` veces mas
    profunda, sobremuestreada para que al escalarla siga nitida), la escala
    con tasa exponencial y la reemplaza por la siguiente en el empalme.
    `imagen_inicial` debe estar YA en escena, centrada en `centro` (usar
    imagen_mandelbrot/imagen_julia con ese centro). Devuelve la ultima
    imagen (ya en escena) por si el clip quiere seguir con ella.
    """
    if pasos is None:
        pasos = max(1, int(round(np.log(factor_total) / np.log(3.0))))
    factor_paso = factor_total ** (1.0 / pasos)
    # El tope RES_MAX debe preservar la relacion de aspecto (si no, el mapeo
    # complejo<->pantalla se deforma y los tramos del zoom no empalman).
    sx = min(res[0] * sobremuestreo, RES_MAX)
    res_calc = (int(round(sx)), int(round(sx * res[1] / res[0])))
    actual = imagen_inicial
    ancho = ancho_inicial
    for i in range(pasos):
        ancho_sig = ancho / factor_paso
        iters = int(max_iter + iter_extra_por_paso * (i + 1))
        campo = campo_escape(res_calc[0], res_calc[1], centro, ancho_sig,
                             iters, c=c)
        siguiente = _imagen(colorear(campo, paleta, ciclo), alto_escena)
        siguiente.move_to(actual.get_center())
        escena.play(actual.animate.scale(factor_paso),
                    run_time=duracion_paso,
                    rate_func=_tasa_exponencial(factor_paso))
        escena.remove(actual)
        escena.add(siguiente)
        actual = siguiente
        ancho = ancho_sig
    return actual


def camino_cardioide(alpha, radio=0.985):
    """Parametro c sobre el borde de la cardioide principal en alpha 0..1.

    c(t) = e^{it}/2 - e^{2it}/4 con t = 2*pi*alpha; `radio` un pelo < 1
    mantiene los Julia conexos pero con estructura visible.
    """
    t = 2.0 * np.pi * alpha
    e1 = radio * np.exp(1j * t)
    return complex(e1 / 2.0 - e1 * e1 / 4.0)


def morph_julia(escena, camino_c, duracion=8.0, frames=96, res=(640, 360),
                centro=0j, ancho=3.6, max_iter=180, paleta="nebulosa",
                ciclo=28.0, alto_escena=8.0, imagen=None,
                interior=COLOR_INTERIOR):
    """Julia cuyo parametro c recorre `camino_c` (callable alpha 0..1 -> c).

    Precalcula `frames` fotogramas RGBA (todos de la misma forma) y los
    intercambia mutando pixel_array en un updater: coste de video constante.
    Devuelve el ImageMobject (queda en escena mostrando el ultimo frame).
    Si `imagen` se pasa (de un morph previo con MISMA res), se reutiliza.
    """
    frames = int(min(frames, FRAMES_MORPH_MAX))
    lote = []
    for k in range(frames):
        c = camino_c(k / (frames - 1))
        campo = campo_escape(res[0], res[1], centro, ancho, max_iter, c=c)
        lote.append(np.ascontiguousarray(
            colorear(campo, paleta, ciclo, interior=interior)))
    if imagen is None:
        imagen = _imagen(lote[0], alto_escena)
        escena.add(imagen)

    def actualizar(mob, alpha):
        mob.pixel_array = lote[int(round(alpha * (frames - 1)))]

    escena.play(UpdateFromAlphaFunc(imagen, actualizar), run_time=duracion,
                rate_func=lambda a: a)
    return imagen


def orbita(c, z0=0j, n=12, exponente=2):
    """Lista de complejos [z0, z1, ...] de la orbita z -> z**exp + c.

    Para dibujar orbitas sobre un ComplexPlane (escapan o quedan atrapadas).
    Se corta si |z| supera 1e6 para no desbordar.
    """
    zs = [complex(z0)]
    z = complex(z0)
    for _ in range(n):
        z = z ** exponente + c
        if abs(z) > 1e6:
            break
        zs.append(z)
    return zs


def miniatura_julia(c, lado=200, ancho=3.4, max_iter=120, paleta="nebulosa",
                    ciclo=28.0, alto_escena=1.6, interior=COLOR_INTERIOR):
    """Julia pequenito y barato (para mosaicos 'el Mandelbrot como mapa')."""
    campo = campo_escape(lado, lado, 0j, ancho, max_iter, c=c)
    return _imagen(colorear(campo, paleta, ciclo, interior=interior),
                   alto_escena)


# =====================================================================
# AMPLIACION 2026-08-27 — curso 26 "Fractales: la forma del infinito"
# (formato vertical). Nada de lo anterior se toca: los clips del curso 1
# que viven en la DB de produccion siguen valiendo tal cual.
#
# Todo lo que sigue es determinista (default_rng con semilla explicita) y
# devuelve NUMEROS ademas de dibujos: la regla del proyecto es que ninguna
# cifra en pantalla se invente, asi que cada pieza trae su propia medida.
# =====================================================================
import math

from manim import Polygon, VGroup, VMobject

# --- Roles de color del curso (mismo idioma que naturaleza.py / caos.py)
COLOR_REGLA = "#f59e0b"      # la regla, el instrumento, el generador
COLOR_MEDIDO = "#22d3ee"     # TODA cifra calculada por esta libreria
COLOR_ESCAPA = "#ea580c"     # lo que se va al infinito
COLOR_ATRAPADO = "#7c3aed"   # lo que queda preso: el conjunto
COLOR_VIDA = "#34d399"       # lo vivo: costa, helecho, arbol, terreno
COLOR_EJE = "#31414f"        # mobiliario: ejes, reticula, cajas
COLOR_EXTERNO = "#94a0b0"    # dato de la literatura, NO medido aqui

# Topes duros: esto se renderiza en el contenedor local, pero un descuido
# (nivel 12 de Koch = 16 millones de segmentos) cuelga la maquina igual.
NIVEL_KOCH_MAX = 8
IFS_PUNTOS_MAX = 600_000
CAJAS_MIN_LADO_PX = 1


def _validar(nombre, valor, tope):
    v = int(valor)
    if v < 0 or v > tope:
        raise ValueError(f"{nombre}={valor} fuera de rango (0..{tope})")
    return v


def _ajuste_recta(x, y):
    """Pendiente y ordenada de la recta de minimos cuadrados (sin scipy)."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    n = x.size
    if n < 2:
        raise ValueError("hacen falta al menos dos puntos para ajustar")
    sx, sy = x.sum(), y.sum()
    sxx = float((x * x).sum())
    sxy = float((x * y).sum())
    den = n * sxx - sx * sx
    m = (n * sxy - sx * sy) / den
    b = (sy - m * sx) / n
    # R^2, para poder decir si el ajuste vale (una recta mala no da una D)
    pred = m * x + b
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return float(m), float(b), float(r2)


# =====================================================================
# 1. Curvas: costa modelo y copo de Koch
# =====================================================================
def costa(nivel=10, H=0.75, semilla=7, largo=10.0, amplitud=1.9):
    """Costa modelo por desplazamiento del punto medio (fBm 1D).

    Devuelve (2**nivel + 1, 2) puntos. `H` es el exponente de Hurst: la
    dimension teorica de la traza es **D = 2 - H** (H=0.75 -> D=1.25, que es
    lo que Richardson midio en la costa de Gran Bretaña). Cada nivel añade
    el punto medio de cada tramo y lo desplaza con una gaussiana cuya
    desviacion se divide por 2**H, asi que la rugosidad es la misma a todas
    las escalas: eso es lo que hace que la regla nunca converja.
    """
    nivel = _validar("costa.nivel", nivel, 14)
    rng = np.random.default_rng(int(semilla))
    ys = np.array([0.0, 0.0])
    escala = float(amplitud)
    for _ in range(nivel):
        medios = 0.5 * (ys[:-1] + ys[1:]) + rng.normal(0.0, escala,
                                                       size=ys.size - 1)
        nuevo = np.empty(ys.size * 2 - 1)
        nuevo[0::2] = ys
        nuevo[1::2] = medios
        ys = nuevo
        escala *= 0.5 ** float(H)
    xs = np.linspace(0.0, float(largo), ys.size)
    return np.stack([xs, ys], axis=1)


_ROT60 = np.array([[math.cos(math.radians(60.0)), -math.sin(math.radians(60.0))],
                   [math.sin(math.radians(60.0)), math.cos(math.radians(60.0))]])


def _koch_segmento(a, b, nivel, altura=1.0):
    """Los 4 hijos de un segmento, recursivamente hasta `nivel`.

    `altura` (0..1) escala el pico SOLO de la ultima subdivision, la que se
    acaba de aplicar: a 0 el pico esta aplanado sobre el segmento (misma
    figura que el nivel anterior, pero con el numero de puntos del nuevo) y
    a 1 esta en su sitio. Animar altura de 0 a 1 hace crecer los picos
    nuevos sin tocar los viejos — y como el numero de puntos NO cambia
    durante el barrido, la curva se puede reconstruir frame a frame sin que
    manim tenga que casar estructuras distintas.
    """
    if nivel == 0:
        return [a]
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    d = (b - a) / 3.0
    p1 = a + d
    p3 = a + 2.0 * d
    # el pico: girar d +60 grados alrededor de p1. Aplanado, el pico cae en
    # el punto medio del tercio central (p1 + d/2), o sea sobre el segmento.
    h = 1.0 if nivel > 1 else float(altura)
    p2 = p1 + (1.0 - h) * (0.5 * d) + h * (_ROT60 @ d)
    salida = []
    for u, v in ((a, p1), (p1, p2), (p2, p3), (p3, b)):
        salida.extend(_koch_segmento(u, v, nivel - 1, altura))
    return salida


def curva_koch(nivel=5, largo=8.0, inicio=(0.0, 0.0), altura=1.0):
    """Curva de Koch abierta: (4**nivel + 1, 2) puntos.

    El generador es siempre el mismo: partir en tres, levantar un pico
    equilatero en el tercio central. Repetirlo es TODA la instruccion.
    """
    nivel = _validar("curva_koch.nivel", nivel, NIVEL_KOCH_MAX)
    a = np.array([float(inicio[0]), float(inicio[1])])
    b = a + np.array([float(largo), 0.0])
    pts = _koch_segmento(a, b, nivel, altura)
    pts.append(b)
    return np.array(pts)


def copo_koch(nivel=4, radio=3.0, centro=(0.0, 0.0), altura=1.0):
    """Copo de nieve cerrado: Koch sobre los tres lados de un equilatero."""
    nivel = _validar("copo_koch.nivel", nivel, NIVEL_KOCH_MAX)
    c = np.array([float(centro[0]), float(centro[1])])
    # Vertices en sentido HORARIO (90 -> 330 -> 210). El generador levanta
    # el pico girando +60 grados, o sea hacia la IZQUIERDA de la marcha: en
    # un recorrido horario eso es hacia FUERA. Con el orden antihorario los
    # picos se meten hacia dentro y el area del copo baja en vez de subir
    # (lo caza `area_poligono` contra `koch_area`).
    angs = np.radians([90.0, 330.0, 210.0])
    v = c + float(radio) * np.stack([np.cos(angs), np.sin(angs)], axis=1)
    pts = []
    for i in range(3):
        pts.extend(_koch_segmento(v[i], v[(i + 1) % 3], nivel, altura))
    pts.append(v[0])
    return np.array(pts)


def koch_lado_inicial(radio=3.0):
    """Lado del triangulo equilatero inscrito en `radio` (el nivel 0)."""
    return float(radio) * math.sqrt(3.0)


def koch_perimetro(nivel, lado):
    """Perimetro EXACTO del copo tras `nivel` iteraciones: 3*lado*(4/3)^n."""
    return 3.0 * float(lado) * (4.0 / 3.0) ** int(nivel)


def koch_area(nivel, lado):
    """Area EXACTA del copo tras `nivel` iteraciones.

    A_n = A_0 * (1 + (3/5)*(1 - (4/9)^n)), con A_0 el triangulo inicial.
    El limite es 8/5 de A_0: el perimetro se dispara y el area no.
    """
    a0 = math.sqrt(3.0) / 4.0 * float(lado) ** 2
    return a0 * (1.0 + 0.6 * (1.0 - (4.0 / 9.0) ** int(nivel)))


def area_poligono(pts):
    """Area del poligono cerrado por la formula del zapatero (medida sobre
    los puntos DIBUJADOS, no sobre la formula: sirve de comprobacion)."""
    p = np.asarray(pts, dtype=np.float64)
    if np.allclose(p[0], p[-1]):
        p = p[:-1]
    x, y = p[:, 0], p[:, 1]
    return float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2.0)


def longitud_poligonal(pts):
    """Longitud de la poligonal tal cual esta dibujada."""
    p = np.asarray(pts, dtype=np.float64)
    return float(np.sqrt(((p[1:] - p[:-1]) ** 2).sum(axis=1)).sum())


# =====================================================================
# 2. Medir: el compas de Richardson y el conteo de cajas
# =====================================================================
def medir_con_regla(pts, paso):
    """El metodo del compas: caminar la curva a zancadas de largo `paso`.

    Desde el punto de apoyo se busca el PRIMER cruce de la curva con el
    circulo de radio `paso` (distancia en linea recta, no arco: es lo que
    hace un compas de verdad sobre un mapa) y se salta ahi.

    Devuelve dict(longitud, pasos, resto, vertices): `vertices` es la
    poligonal que el compas dibujo, lista para pintarla encima de la costa.
    `longitud = pasos*paso + resto`, con el resto en linea recta hasta el
    final (la convencion de Richardson).
    """
    p = np.asarray(pts, dtype=np.float64)
    paso = float(paso)
    if paso <= 0:
        raise ValueError("medir_con_regla: paso debe ser > 0")
    anclas = [p[0].copy()]
    ancla = p[0].copy()
    i = 0                       # indice del segmento donde esta el ancla
    t = 0.0                     # parametro dentro de ese segmento
    n_pasos = 0
    # Cota generosa pero finita: la poligonal no puede dar mas zancadas que
    # su propia longitud dividida por el paso (con holgura por los rodeos).
    limite = int(min(200_000, 4 * longitud_poligonal(p) / paso + 100))
    while n_pasos < limite:
        encontrado = False
        j = i
        tj = t
        while j < len(p) - 1:
            a = p[j] + tj * (p[j + 1] - p[j])
            d = p[j + 1] - a
            f = a - ancla
            aa = float(d @ d)
            if aa > 1e-18:
                bb = 2.0 * float(f @ d)
                cc = float(f @ f) - paso * paso
                disc = bb * bb - 4.0 * aa * cc
                if disc >= 0.0:
                    raiz = math.sqrt(disc)
                    for s in ((-bb + raiz) / (2 * aa), (-bb - raiz) / (2 * aa)):
                        if 0.0 <= s <= 1.0:
                            ancla = a + s * d
                            anclas.append(ancla.copy())
                            # reexpresar la posicion en el segmento j
                            largo = np.linalg.norm(p[j + 1] - p[j])
                            avance = np.linalg.norm(ancla - p[j])
                            i, t = j, float(avance / largo) if largo else 0.0
                            n_pasos += 1
                            encontrado = True
                            break
            if encontrado:
                break
            j += 1
            tj = 0.0
        if not encontrado:
            break
    resto = float(np.linalg.norm(p[-1] - ancla))
    anclas.append(p[-1].copy())
    return {"longitud": n_pasos * paso + resto, "pasos": n_pasos,
            "resto": resto, "vertices": np.array(anclas), "paso": paso}


def richardson(pts, pasos):
    """La grafica de Richardson: longitud medida frente a largo de la regla.

    Devuelve dict(pasos, longitudes, pendiente, D, r2). En log-log la nube
    cae sobre una recta de pendiente `1 - D`: por eso una costa con D=1.25
    crece un 19 % cada vez que la regla se parte por la mitad, y nunca para.
    """
    pasos = [float(s) for s in pasos]
    longitudes = [medir_con_regla(pts, s)["longitud"] for s in pasos]
    m, _, r2 = _ajuste_recta(np.log(pasos), np.log(longitudes))
    return {"pasos": pasos, "longitudes": longitudes, "pendiente": m,
            "D": 1.0 - m, "r2": r2}


def densificar(pts, paso):
    """Remuestrea la poligonal a puntos separados como mucho `paso`.

    Imprescindible antes de contar cajas: si la curva tiene tramos largos,
    el conteo se salta las cajas por las que la curva PASA sin tener un
    vertice dentro, y la dimension sale baja.
    """
    p = np.asarray(pts, dtype=np.float64)
    salida = [p[0]]
    for a, b in zip(p[:-1], p[1:]):
        d = float(np.linalg.norm(b - a))
        if d <= paso:
            salida.append(b)
            continue
        k = int(math.ceil(d / paso))
        for i in range(1, k + 1):
            salida.append(a + (b - a) * (i / k))
    return np.array(salida)


def conteo_cajas(pts, lados=None, densificar_a=None):
    """Dimension por conteo de cajas sobre una nube o una curva.

    `lados` en las MISMAS unidades que los puntos. Devuelve
    dict(lados, conteos, D, r2): D es menos la pendiente de log N frente a
    log lado. Si `densificar_a` no se pasa, la curva se remuestrea a un
    quinto del lado mas pequeño (para no perder cajas atravesadas).
    """
    p = np.asarray(pts, dtype=np.float64)
    x0, y0 = p[:, 0].min(), p[:, 1].min()
    x1, y1 = p[:, 0].max(), p[:, 1].max()
    extension = max(x1 - x0, y1 - y0)
    if lados is None:
        lados = [extension / (2 ** k) for k in range(2, 9)]
    lados = [float(s) for s in lados]
    fino = densificar_a if densificar_a is not None else min(lados) / 5.0
    q = densificar(p, fino) if len(p) > 1 else p
    conteos = []
    for s in lados:
        celdas = np.floor((q - np.array([x0, y0])) / s).astype(np.int64)
        # empaquetar (i,j) en un solo entero es mucho mas rapido que unique
        # sobre filas, y aqui hay millones de puntos
        clave = celdas[:, 0] * 1_000_003 + celdas[:, 1]
        conteos.append(int(np.unique(clave).size))
    m, _, r2 = _ajuste_recta(np.log(lados), np.log(conteos))
    return {"lados": lados, "conteos": conteos, "D": -m, "r2": r2,
            "extension": float(extension), "origen": (float(x0), float(y0))}


def rejilla_cajas(pts, lado, origen=None, color=COLOR_EJE, grosor=1.4,
                  opacidad=0.9, solo_ocupadas=True):
    """Las cajas OCUPADAS del conteo, como VGroup de cuadrados.

    Es la version dibujable de `conteo_cajas`: lo que se ve en pantalla es
    exactamente lo que la cifra cuenta.
    """
    p = np.asarray(pts, dtype=np.float64)
    if origen is None:
        origen = (p[:, 0].min(), p[:, 1].min())
    o = np.array([float(origen[0]), float(origen[1])])
    q = densificar(p, lado / 5.0) if len(p) > 1 else p
    celdas = np.floor((q - o) / lado).astype(np.int64)
    unicas = np.unique(celdas, axis=0)
    g = VGroup()
    for i, j in unicas:
        x = o[0] + i * lado
        y = o[1] + j * lado
        g.add(Polygon([x, y, 0], [x + lado, y, 0], [x + lado, y + lado, 0],
                      [x, y + lado, 0], stroke_width=grosor,
                      stroke_color=color, stroke_opacity=opacidad,
                      fill_opacity=0.0))
    return g


def poligonal(pts, color=COLOR_VIDA, grosor=2.6, opacidad=1.0):
    """VMobject de una curva (n,2) sin pasar por Polygon (que cierra)."""
    p = np.asarray(pts, dtype=np.float64)
    v = VMobject(stroke_color=color, stroke_width=grosor)
    v.set_points_as_corners([np.array([x, y, 0.0]) for x, y in p])
    v.set_stroke(opacity=opacidad)
    return v


# =====================================================================
# 3. IFS: el juego del caos
# =====================================================================
# Cada mapa es (matriz 2x2 aplanada por filas, traslacion, probabilidad).
MAPAS = {
    # Sierpinski: encoger a la mitad hacia cada vertice. Tres numeros por
    # mapa y ya esta el triangulo.
    "sierpinski": (
        ((0.5, 0.0, 0.0, 0.5), (0.00, 0.00), 1 / 3),
        ((0.5, 0.0, 0.0, 0.5), (1.00, 0.00), 1 / 3),
        ((0.5, 0.0, 0.0, 0.5), (0.50, 0.866025403784), 1 / 3),
    ),
    # Helecho de Barnsley (1988): 24 numeros, un helecho.
    "helecho": (
        ((0.00, 0.00, 0.00, 0.16), (0.0, 0.00), 0.01),
        ((0.85, 0.04, -0.04, 0.85), (0.0, 1.60), 0.85),
        ((0.20, -0.26, 0.23, 0.22), (0.0, 1.60), 0.07),
        ((-0.15, 0.28, 0.26, 0.24), (0.0, 0.44), 0.07),
    ),
    # Dragon de Heighway: dos mapas, giro de 45 grados y escala 1/raiz(2).
    "dragon": (
        ((0.5, -0.5, 0.5, 0.5), (0.0, 0.0), 0.5),
        ((-0.5, -0.5, 0.5, -0.5), (1.0, 0.0), 0.5),
    ),
    # Un arbol de tres ramas: tronco + dos copias giradas.
    "arbol": (
        ((0.00, 0.00, 0.00, 0.50), (0.0, 0.00), 0.05),
        ((0.42, -0.42, 0.42, 0.42), (0.0, 0.20), 0.40),
        ((0.42, 0.42, -0.42, 0.42), (0.0, 0.20), 0.40),
        ((0.10, 0.00, 0.00, 0.10), (0.0, 0.20), 0.15),
    ),
}

_ENJAMBRE = 500      # particulas que avanzan a la vez (prefijo estable)
_QUEMA = 20          # pasos de asentamiento antes de emitir


def _mapas(spec):
    if isinstance(spec, str):
        if spec not in MAPAS:
            raise ValueError(f"IFS desconocido: {spec}")
        spec = MAPAS[spec]
    mats = np.array([m for m, _, _ in spec], dtype=np.float64)
    mats = mats.reshape(len(spec), 2, 2)
    tras = np.array([t for _, t, _ in spec], dtype=np.float64)
    probs = np.array([p for _, _, p in spec], dtype=np.float64)
    return mats, tras, probs / probs.sum()


def ifs_puntos(spec, n=120_000, semilla=3, con_eleccion=False):
    """Juego del caos: (n,2) puntos del atractor del IFS.

    El orden de emision es (paso, particula), asi que **el prefijo es
    estable**: pedir 400 puntos y pedir 200 000 comparte los primeros 400.
    Eso es lo que permite animar la acumulacion relevando imagenes.

    Con `con_eleccion=True` devuelve tambien que mapa genero cada punto.
    """
    n = _validar("ifs_puntos.n", n, IFS_PUNTOS_MAX)
    mats, tras, probs = _mapas(spec)
    rng = np.random.default_rng(int(semilla))
    pts = np.zeros((_ENJAMBRE, 2))
    total = _QUEMA + math.ceil(n / _ENJAMBRE)
    emitidos, elegidos = [], []
    for paso in range(total):
        eleccion = rng.choice(len(probs), size=_ENJAMBRE, p=probs)
        pts = np.einsum("kij,kj->ki", mats[eleccion], pts) + tras[eleccion]
        if paso >= _QUEMA:
            emitidos.append(pts.copy())
            elegidos.append(eleccion.copy())
    salida = np.vstack(emitidos)[:n]
    if con_eleccion:
        return salida, np.concatenate(elegidos)[:n]
    return salida


def ifs_camino(spec, n=200_000, semilla=4, z0=(0.0, 0.0), quema=12):
    """El juego del caos TAL CUAL se juega: UN punto que salta, n veces.

    `ifs_puntos` mueve 500 particulas a la vez (es mas rapido y da un
    prefijo estable), pero eso no es lo que se enseña en pantalla: en el
    clip hay **un solo punto** dando saltos, y los primeros doce saltos
    tienen que ser los primeros doce de la nube que aparece despues. Por
    eso esta version es secuencial, y por eso los clips que muestran el
    juego usan `orden="camino"`.

    Devuelve (puntos (n,2), eleccion (n,)). El bucle es de floats sueltos,
    no de arrays de numpy: para 200 000 saltos sale ~10 veces mas rapido.
    """
    n = _validar("ifs_camino.n", n, IFS_PUNTOS_MAX)
    mats, tras, probs = _mapas(spec)
    rng = np.random.default_rng(int(semilla))
    total = int(quema) + n
    eleccion = rng.choice(len(probs), size=total, p=probs)
    m = [(float(M[0, 0]), float(M[0, 1]), float(M[1, 0]), float(M[1, 1]),
          float(t[0]), float(t[1])) for M, t in zip(mats, tras)]
    x, y = float(z0[0]), float(z0[1])
    xs = np.empty(n, dtype=np.float64)
    ys = np.empty(n, dtype=np.float64)
    for i, k in enumerate(eleccion):
        a, b, c, d, e, f = m[k]
        x, y = a * x + b * y + e, c * x + d * y + f
        j = i - quema
        if j >= 0:
            xs[j] = x
            ys[j] = y
    return np.stack([xs, ys], axis=1), eleccion[quema:]


def arbol_davinci(niveles=8, angulo_deg=30.0, razon=None, largo0=1.0,
                  grosor0=0.36, origen=(0.0, 0.0)):
    """Arbol binario con la regla de Leonardo: la seccion se conserva.

    Da Vinci anoto que el tronco de un arbol y la suma de sus ramas tienen
    la MISMA seccion. Con dos hijas por rama eso obliga a
    d_hija = d_madre / raiz(2), y esa es toda la regla de grosores. La misma
    razon se usa para el largo, que es lo que hace que el arbol se lea como
    un arbol y no como una escoba.

    Devuelve dict con:
      ramas       lista por generacion de (inicio, fin, grosor)
      seccion     seccion total por generacion (constante: LA cifra)
      largo       longitud total por generacion
      largo_total longitud acumulada / la del tronco
    """
    niveles = _validar("arbol_davinci.niveles", niveles, 12)
    razon = float(razon) if razon else 1.0 / math.sqrt(2.0)
    ang = math.radians(float(angulo_deg))
    frentes = [(np.array([float(origen[0]), float(origen[1])]),
                math.pi / 2.0, float(largo0), float(grosor0))]
    ramas, seccion, largo = [], [], []
    for _ in range(niveles + 1):
        capa, siguientes = [], []
        s = 0.0
        L = 0.0
        for base, rumbo, lar, gro in frentes:
            punta = base + lar * np.array([math.cos(rumbo), math.sin(rumbo)])
            capa.append((base, punta, gro))
            s += math.pi * (gro / 2.0) ** 2
            L += lar
            siguientes.append((punta, rumbo + ang, lar * razon, gro * razon))
            siguientes.append((punta, rumbo - ang, lar * razon, gro * razon))
        ramas.append(capa)
        seccion.append(s)
        largo.append(L)
        frentes = siguientes
    acumulado = np.cumsum(largo)
    return {"ramas": ramas, "seccion": seccion, "largo": largo,
            "seccion_relativa": [x / seccion[0] for x in seccion],
            "largo_total": [x / largo[0] for x in acumulado],
            "razon": razon, "angulo_deg": float(angulo_deg)}


def ifs_reparto(spec, n=120_000, semilla=3):
    """Cuantos puntos puso CADA mapa (contados, no las probabilidades).

    Devuelve dict(cuentas, fracciones, probabilidades): la comparacion
    honesta entre lo que el dado promete y lo que el dado dio.
    """
    _, eleccion = ifs_puntos(spec, n, semilla, con_eleccion=True)
    _, _, probs = _mapas(spec)
    cuentas = np.bincount(eleccion, minlength=len(probs))
    return {"cuentas": cuentas.tolist(),
            "fracciones": (cuentas / cuentas.sum()).tolist(),
            "probabilidades": probs.tolist()}


def caja_ifs(spec, semilla=3, n=60_000, holgura=0.04, orden="enjambre"):
    """Caja envolvente ESTABLE del atractor (x0, x1, y0, y1).

    Se calcula siempre con el mismo n y la misma semilla para que la imagen
    de 400 puntos y la de 200 000 compartan encuadre: si la caja se sacara
    de los puntos pedidos, el relevo de imagenes daria un salto.
    """
    p = (ifs_camino(spec, n, semilla)[0] if orden == "camino"
         else ifs_puntos(spec, n, semilla))
    x0, x1 = float(p[:, 0].min()), float(p[:, 0].max())
    y0, y1 = float(p[:, 1].min()), float(p[:, 1].max())
    mx, my = (x1 - x0) * holgura, (y1 - y0) * holgura
    return (x0 - mx, x1 + mx, y0 - my, y1 + my)


def imagen_nube(pts, caja, res=(720, 900), color=COLOR_VIDA,
                alto_escena=6.0, fondo=None, piso=0.55, ganancia=1.35):
    """Una nube de puntos como imagen por densidad (brillo logaritmico).

    Un mobject por punto es inviable (200 000 Dots cuelgan el render), asi
    que la nube se pinta en un histograma 2D y se muestra como imagen. La
    `caja` se pasa desde fuera a proposito: relevar imagenes con mas y mas
    puntos solo empalma sin saltos si TODAS comparten encuadre.
    """
    res_x, res_y = int(res[0]), int(res[1])
    if max(res_x, res_y) > RES_MAX:
        raise ValueError(f"imagen_nube: res {res} > {RES_MAX}")
    p = np.asarray(pts, dtype=np.float64)
    x0, x1, y0, y1 = caja
    hist, _, _ = np.histogram2d(p[:, 0], p[:, 1], bins=[res_x, res_y],
                                range=[[x0, x1], [y0, y1]])
    dens = np.log1p(hist.T[::-1])          # fila 0 = y alto (imagen)
    if dens.max() > 0:
        dens = dens / dens.max()
    # Con pocos puntos el log aplasta todo: garantiza que un pixel tocado
    # se vea (si no, la nube inicial es invisible y el clip parece roto).
    dens = np.where(dens > 0, np.maximum(dens, piso), 0.0)
    tinta = _hex_a_rgb(color)
    rgba = np.zeros((res_y, res_x, 4), dtype=np.uint8)
    if fondo is None:
        rgba[..., :3] = np.clip(tinta * dens[..., None] * ganancia, 0,
                                255).astype(np.uint8)
        rgba[..., 3] = np.clip(dens * 255 * 1.6, 0, 255).astype(np.uint8)
    else:
        base = _hex_a_rgb(fondo)
        rgb = base + (tinta - base) * dens[..., None]
        rgba[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        rgba[..., 3] = 255
    return _imagen(rgba, alto_escena)


def imagen_ifs(spec, puntos=120_000, res=(720, 900), color=COLOR_VIDA,
               alto_escena=6.0, semilla=3, caja=None, fondo=None,
               piso=0.55, ganancia=1.35, orden="enjambre"):
    """El atractor de un IFS como imagen por densidad.

    Con `puntos` chico (400, 4 000) sale la nube rala del MISMO prefijo:
    relevar imagenes con puntos crecientes ES la animacion del juego del
    caos. `orden="camino"` usa el juego secuencial (un punto que salta),
    que es el que se ve en pantalla en el clip 04.
    """
    pts = (ifs_camino(spec, puntos, semilla)[0] if orden == "camino"
           else ifs_puntos(spec, puntos, semilla))
    caja = caja if caja else caja_ifs(spec, semilla, orden=orden)
    return imagen_nube(pts, caja, res=res, color=color,
                       alto_escena=alto_escena, fondo=fondo, piso=piso,
                       ganancia=ganancia)


def marcos_ifs(spec, alto_escena=6.0, colores=None, caja=None, semilla=3,
               grosor=2.2, opacidad=0.9, orden="enjambre"):
    """Un marco por mapa: DONDE cada regla mete una copia entera del todo.

    Es la imagen que explica un IFS sin una sola palabra: la figura esta
    hecha de copias de si misma, y los marcos enseñan cuales.
    Escalado igual que `imagen_ifs(alto_escena=...)`, asi que superponer
    ambos con el mismo centro los alinea.
    """
    mats, tras, _ = _mapas(spec)
    x0, x1, y0, y1 = caja if caja else caja_ifs(spec, semilla, orden=orden)
    esquinas = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    escala = float(alto_escena) / (y1 - y0)
    centro = np.array([(x0 + x1) / 2.0, (y0 + y1) / 2.0])
    if colores is None:
        colores = (COLOR_REGLA, COLOR_MEDIDO, COLOR_ATRAPADO, COLOR_ESCAPA)
    g = VGroup()
    for k, (M, t) in enumerate(zip(mats, tras)):
        trans = (esquinas @ M.T) + t
        pts = (trans - centro) * escala
        g.add(Polygon(*[np.append(p, 0.0) for p in pts], stroke_width=grosor,
                      stroke_color=colores[k % len(colores)],
                      fill_opacity=0.0).set_stroke(opacity=opacidad))
    return g


def sierpinski_exacto(nivel=6, lado=6.0, centro=(0.0, 0.0)):
    """La version geometrica: los 3**nivel triangulos que quedan.

    Devuelve (3**nivel, 3, 2). Sirve para el borrado nivel a nivel (la
    version constructiva) frente al juego del caos (la version aleatoria):
    dan la MISMA figura, y ese es el golpe del clip.
    """
    nivel = _validar("sierpinski_exacto.nivel", nivel, 8)
    h = float(lado) * math.sqrt(3.0) / 2.0
    cx, cy = float(centro[0]), float(centro[1])
    base = np.array([[cx - lado / 2, cy - h / 2],
                     [cx + lado / 2, cy - h / 2],
                     [cx, cy + h / 2]])
    tris = [base]
    for _ in range(nivel):
        nuevos = []
        for t in tris:
            m01 = (t[0] + t[1]) / 2
            m12 = (t[1] + t[2]) / 2
            m20 = (t[2] + t[0]) / 2
            nuevos.append(np.array([t[0], m01, m20]))
            nuevos.append(np.array([m01, t[1], m12]))
            nuevos.append(np.array([m20, m12, t[2]]))
        tris = nuevos
    return np.array(tris)


def dimension_autosemejanza(copias, factor):
    """D = log(copias) / log(1/factor): la dimension de un autosemejante
    exacto. Koch: 4 copias a 1/3 -> 1.2619. Sierpinski: 3 a 1/2 -> 1.5850."""
    return math.log(float(copias)) / math.log(1.0 / float(factor))


# =====================================================================
# 4. Complejos: orbitas, prisioneros, frontera
# =====================================================================
def traza_orbita(c, z0=0j, n=14, exponente=2, corte=1e6):
    """La orbita como (m,2) lista para dibujarla sobre un plano complejo."""
    zs = orbita(c, z0=z0, n=n, exponente=exponente)
    return np.array([[z.real, z.imag] for z in zs if abs(z) <= corte])


def prisioneros(c, res=(420, 420), centro=0j, ancho=3.6, max_iter=250):
    """Fraccion de la malla que NO escapa para el Julia de parametro `c`.

    Es la cifra honesta de "cuanto queda atrapado": se cuenta sobre la
    malla que se dibuja, no sobre el conjunto ideal.
    """
    campo = campo_escape(res[0], res[1], centro, ancho, max_iter, c=c)
    dentro = int(np.isnan(campo).sum())
    total = int(campo.size)
    return {"atrapados": dentro, "total": total,
            "fraccion": dentro / total, "c": complex(c),
            "conexo": bool(en_mandelbrot(c, max_iter))}


def en_mandelbrot(c, max_iter=400):
    """True si la orbita de 0 no escapa para ese c (el criterio del mapa).

    Es LA definicion del conjunto de Mandelbrot, y tambien el teorema que
    ordena todo el curso: el Julia de c es conexo si y solo si c esta aqui.
    """
    z = 0j
    c = complex(c)
    for _ in range(int(max_iter)):
        z = z * z + c
        if z.real * z.real + z.imag * z.imag > 4.0:
            return False
    return True


def mascara_mandelbrot(res=(900, 900), centro=-0.6 + 0j, ancho=3.2,
                       max_iter=600):
    """Mascara booleana (res_y, res_x) del interior, y el paso de la malla."""
    campo = campo_escape(res[0], res[1], centro, ancho, max_iter)
    paso = float(ancho) / int(res[0])
    return np.isnan(campo), paso


def frontera_puntos(mascara, centro, paso):
    """Los pixeles de FRONTERA de una mascara, en coordenadas del plano.

    Frontera = pixel de dentro con al menos un vecino de fuera (4-vecindad).
    """
    m = np.asarray(mascara, dtype=bool)
    filas, cols = np.nonzero(frontera_mascara(m))
    res_y, res_x = m.shape
    x = complex(centro).real + (cols - res_x / 2.0 + 0.5) * paso
    y = complex(centro).imag + (filas - res_y / 2.0 + 0.5) * paso
    return np.stack([x, y], axis=1)


def distancia_mandelbrot(res=1400, centro=-0.75 + 0j, ancho=3.2,
                        max_iter=900, radio=1e6):
    """Distancia (estimada) de cada punto de la malla a la frontera de M.

    Metodo clasico del estimador de distancia: junto a la orbita se itera su
    derivada respecto a c (dz -> 2*z*dz + 1), y al escapar

        d ~ 2*|z|*ln|z| / |dz|

    aproxima la distancia del punto a la frontera. Los puntos de DENTRO se
    marcan con 0.0 (el estimador exterior no dice nada de ellos).

    Devuelve (mapa (res,res) float64, paso de la malla en unidades del
    plano). Es la pieza que permite MEDIR la frontera: contar los pixeles
    del borde de una mascara solo mide el contorno de la cardioide, porque
    los filamentos son mas finos que el pixel y no entran en la mascara.
    """
    res = int(min(res, RES_MAX))
    max_iter = int(min(max_iter, ITER_MAX))
    c0 = complex(centro)
    xs = np.linspace(c0.real - ancho / 2, c0.real + ancho / 2, res)
    ys = np.linspace(c0.imag - ancho / 2, c0.imag + ancho / 2, res)
    c = (xs[None, :] + 1j * ys[:, None]).ravel().astype(np.complex128)
    z = np.zeros_like(c)
    dz = np.zeros_like(c)
    dist = np.zeros(c.size, dtype=np.float64)
    vivos = np.arange(c.size)
    r2 = float(radio) * float(radio)
    for _ in range(max_iter):
        dz = 2.0 * z * dz + 1.0
        z = z * z + c
        m2 = z.real * z.real + z.imag * z.imag
        esc = m2 > r2
        if esc.any():
            idx = vivos[esc]
            mod = np.sqrt(m2[esc])
            dist[idx] = 2.0 * mod * np.log(mod) / np.abs(dz[esc])
            queda = ~esc
            vivos = vivos[queda]
            z = z[queda]
            dz = dz[queda]
            c = c[queda]
        if vivos.size == 0:
            break
    return dist.reshape(res, res), float(ancho) / res


def orla_frontera(dist, paso, epsilon):
    """Mascara de la orla: los puntos de FUERA a distancia <= epsilon."""
    d = np.asarray(dist)
    return (d > 0.0) & (d <= float(epsilon))


def imagen_orla(dist, paso, epsilon, color=COLOR_MEDIDO, alto_escena=8.0,
                interior=COLOR_ATRAPADO, opacidad_interior=1.0):
    """La orla de grosor epsilon dibujada: el halo que NO adelgaza.

    Es la imagen del clip 11: si la frontera fuera una curva normal, el area
    del halo se partiria por la mitad al partir epsilon por la mitad. Aqui
    apenas baja un 25 %, y esa terquedad ES la dimension.
    """
    d = np.asarray(dist)
    rgba = np.zeros(d.shape + (4,), dtype=np.uint8)
    dentro = d <= 0.0
    rgba[dentro, :3] = _hex_a_rgb(interior).astype(np.uint8)
    rgba[dentro, 3] = int(255 * opacidad_interior)
    halo = orla_frontera(d, paso, epsilon)
    rgba[halo, :3] = _hex_a_rgb(color).astype(np.uint8)
    rgba[halo, 3] = 255
    return _imagen(rgba, alto_escena)


def dimension_frontera(res=1400, centro=-0.75 + 0j, ancho=3.2, max_iter=900,
                       escalas=(2, 4, 8, 16), dist=None, paso=None):
    """Dimension de la frontera del Mandelbrot por el area de su orla.

    Para una curva normal (rectificable), el area de la orla de grosor eps
    vale ~2*L*eps: se parte por la mitad cuando eps se parte por la mitad.
    En general A(eps) ~ eps^(2-D), asi que **D = 2 - pendiente** del ajuste
    log-log.

    Las `escalas` van en PIXELES de la malla. El resultado SUBE cada vez que
    se afina la malla (1.60 a res 1000, 1.62 a 1600, 1.64 a 2200): no
    converge a 1 porque la frontera no es una curva. La teoria (Shishikura,
    1991) demuestra que su dimension de Hausdorff vale exactamente 2; un
    conteo finito nunca llega, y esa distancia SE DECLARA en pantalla.
    """
    if dist is None:
        dist, paso = distancia_mandelbrot(res, centro, ancho, max_iter)
    eps = [int(e) * paso for e in escalas]
    celda = paso * paso
    areas = [float(orla_frontera(dist, paso, e).sum()) * celda for e in eps]
    pend, _, r2 = _ajuste_recta(np.log(eps), np.log(areas))
    return {"epsilon": eps, "areas": areas, "escalas": list(escalas),
            "pendiente": pend, "D": 2.0 - pend, "r2": r2, "paso": paso,
            "cociente": [areas[i] / areas[i + 1]
                         for i in range(len(areas) - 1)]}


def frontera_mascara(m):
    """Version booleana de `frontera_puntos` (misma regla, sin coordenadas)."""
    m = np.asarray(m, dtype=bool)
    vecinos = np.ones_like(m)
    vecinos[1:, :] &= m[:-1, :]
    vecinos[:-1, :] &= m[1:, :]
    vecinos[:, 1:] &= m[:, :-1]
    vecinos[:, :-1] &= m[:, 1:]
    return m & ~vecinos


# =====================================================================
# 5. Newton: las cuencas de atraccion
# =====================================================================
RAICES_CUBICAS = (1 + 0j,
                  complex(-0.5, math.sqrt(3) / 2),
                  complex(-0.5, -math.sqrt(3) / 2))

COLORES_NEWTON = ("#f59e0b", "#22d3ee", "#7c3aed")


def _newton_campo(res, centro, ancho, raices, max_iter, tol):
    res_x, res_y = int(min(res[0], RES_MAX)), int(min(res[1], RES_MAX))
    alto = ancho * res_y / res_x
    xs = np.linspace(centro.real - ancho / 2, centro.real + ancho / 2, res_x)
    ys = np.linspace(centro.imag - alto / 2, centro.imag + alto / 2, res_y)
    z = (xs[None, :] + 1j * ys[:, None]).astype(np.complex128).ravel()
    raices = np.array([complex(r) for r in raices])
    cual = np.full(z.size, -1, dtype=np.int8)
    pasos = np.full(z.size, max_iter, dtype=np.int16)
    vivos = np.arange(z.size)
    for n in range(int(max_iter)):
        # p(z) = z^k - 1 con k = len(raices): p'/p se arma del producto
        k = len(raices)
        zk = z ** k
        deriv = k * z ** (k - 1)
        deriv = np.where(np.abs(deriv) < 1e-14, 1e-14, deriv)
        z = z - (zk - 1.0) / deriv
        d = np.abs(z[:, None] - raices[None, :])
        cerca = d.min(axis=1) < tol
        if cerca.any():
            idx = vivos[cerca]
            cual[idx] = np.argmin(d[cerca], axis=1).astype(np.int8)
            pasos[idx] = n + 1
            vivos = vivos[~cerca]
            z = z[~cerca]
        if vivos.size == 0:
            break
    return cual.reshape(res_y, res_x), pasos.reshape(res_y, res_x)


def imagen_newton(res=(720, 900), centro=0j, ancho=3.0,
                  raices=RAICES_CUBICAS, max_iter=40, tol=1e-6,
                  colores=COLORES_NEWTON, alto_escena=8.0, gamma=0.55):
    """Cuencas de Newton para z^k = 1: el color dice A QUE raiz cae cada
    punto de partida, y el brillo, cuantos pasos tardo.

    La frontera entre cuencas es el fractal: en cualquier punto de ella se
    tocan LAS TRES a la vez (propiedad de Wada). No hay una linea que
    separe dos: no existe tal linea.
    """
    cual, pasos = _newton_campo(res, complex(centro), float(ancho), raices,
                                max_iter, tol)
    brillo = 1.0 - (np.clip(pasos, 0, max_iter) / float(max_iter)) ** gamma
    brillo = 0.25 + 0.75 * brillo
    rgba = np.zeros(cual.shape + (4,), dtype=np.uint8)
    for k, col in enumerate(colores[:len(raices)]):
        sel = cual == k
        rgba[sel, :3] = np.clip(_hex_a_rgb(col) * brillo[sel][:, None],
                                0, 255).astype(np.uint8)
    rgba[..., 3] = 255
    return _imagen(rgba, alto_escena)


def newton_reparto(res=(400, 400), centro=0j, ancho=3.0,
                   raices=RAICES_CUBICAS, max_iter=40, tol=1e-6):
    """% de la malla que cae en cada cuenca y pasos medios (medidos)."""
    cual, pasos = _newton_campo(res, complex(centro), float(ancho), raices,
                                max_iter, tol)
    total = cual.size
    cuentas = [int((cual == k).sum()) for k in range(len(raices))]
    return {"cuentas": cuentas, "total": total,
            "fracciones": [c / total for c in cuentas],
            "sin_converger": int((cual < 0).sum()),
            "pasos_medios": float(pasos[cual >= 0].mean())}


def newton_orbita(z0, raices=RAICES_CUBICAS, n=12, tol=1e-9):
    """El camino de Newton desde z0: (m,2) para dibujarlo sobre el plano."""
    k = len(raices)
    z = complex(z0)
    pts = [[z.real, z.imag]]
    for _ in range(int(n)):
        deriv = k * z ** (k - 1)
        if abs(deriv) < 1e-14:
            break
        z = z - (z ** k - 1.0) / deriv
        pts.append([z.real, z.imag])
        if min(abs(z - complex(r)) for r in raices) < tol:
            break
    return np.array(pts)


# =====================================================================
# 6. Fractales que trabajan: antena y terreno
# =====================================================================
def antena_koch(nivel=4, ancho=4.0):
    """Una antena de hilo doblada segun Koch, y las dos cifras que importan.

    `longitud_hilo` es el hilo que hay que soldar; `ancho` es lo que ocupa
    en la placa. El cociente (4/3)^nivel es el factor de plegado: la MISMA
    longitud electrica en una fraccion del espacio. La resonancia de una
    antena de hilo la fija su longitud, no su envergadura — ese es el
    motivo por el que las antenas fractales existen (Cohen, 1995: dato de
    la literatura, no medido aqui).
    """
    nivel = _validar("antena_koch.nivel", nivel, 6)
    pts = curva_koch(nivel, largo=float(ancho))
    largo = longitud_poligonal(pts)
    return {"puntos": pts, "longitud_hilo": largo,
            "ancho_ocupado": float(ancho),
            "plegado": largo / float(ancho),
            "plegado_exacto": (4.0 / 3.0) ** nivel,
            "nivel": nivel}


def terreno(n=513, H=0.72, semilla=11, amplitud=1.0):
    """Perfil de montaña por desplazamiento del punto medio (fBm 1D).

    Mismo motor que `costa`: un terreno y una costa son el mismo programa
    con otra semilla. Devuelve (n,) alturas normalizadas a `amplitud`.
    """
    pts = costa(nivel=int(math.log2(max(n, 2) - 1)), H=H, semilla=semilla,
                largo=1.0, amplitud=1.0)
    ys = pts[:, 1]
    ys = ys - ys.min()
    if ys.max() > 0:
        ys = ys / ys.max()
    return ys * float(amplitud)


def perfil_terreno(alturas, ancho=7.0, base=-3.0, color=COLOR_VIDA,
                   grosor=2.4, relleno=0.22):
    """El perfil como poligono cerrado contra una base (silueta de montaña)."""
    ys = np.asarray(alturas, dtype=np.float64)
    xs = np.linspace(-ancho / 2, ancho / 2, ys.size)
    pts = [np.array([x, float(y) + base, 0.0]) for x, y in zip(xs, ys)]
    pts.append(np.array([xs[-1], base - 0.02, 0.0]))
    pts.append(np.array([xs[0], base - 0.02, 0.0]))
    p = Polygon(*pts, stroke_width=grosor, stroke_color=color,
                fill_color=color, fill_opacity=relleno)
    return p

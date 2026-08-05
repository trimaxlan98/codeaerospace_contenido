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
                      alto_escena=8.0):
    """ImageMobject del conjunto de Mandelbrot listo para la escena."""
    campo = campo_escape(res[0], res[1], centro, ancho, max_iter)
    return _imagen(colorear(campo, paleta, ciclo), alto_escena)


def imagen_julia(c, centro=0j, ancho=3.6, res=(1280, 720), max_iter=250,
                 paleta="nebulosa", ciclo=28.0, alto_escena=8.0):
    """ImageMobject del conjunto de Julia de parametro `c`."""
    campo = campo_escape(res[0], res[1], centro, ancho, max_iter, c=c)
    return _imagen(colorear(campo, paleta, ciclo), alto_escena)


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
                ciclo=28.0, alto_escena=8.0, imagen=None):
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
        lote.append(np.ascontiguousarray(colorear(campo, paleta, ciclo)))
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
                    ciclo=28.0, alto_escena=1.6):
    """Julia pequenito y barato (para mosaicos 'el Mandelbrot como mapa')."""
    campo = campo_escape(lado, lado, 0j, ancho, max_iter, c=c)
    return _imagen(colorear(campo, paleta, ciclo), alto_escena)

"""Estelas y cometas: dibujar una trayectoria con la punta encendida y mover objetos dejando rastro.

Manim CE dibuja un trazo con `Create`, pero la punta que avanza no se distingue del resto: en una
órbita, un enlace o un logo, el ojo no sabe hacia dónde va el trazo. Aquí la punta lleva un cometa
(núcleo y halo, como `brillo.punto_brillante`) que sigue EXACTAMENTE al trazo y se apaga al llegar.
Y para lo que se mueve (un satélite que entra por su órbita), una estela que se adelgaza y se
desvanece detrás, sin `TracedPath` (que depende del orden de los updaters y deja la estela pegada
al final de la escena).

Todo devuelve animaciones normales (`AnimationGroup`) que se pasan a `self.play`, se combinan con
`LaggedStart` y se pueden acelerar con `run_time`. La punta y la estela se quitan solas al terminar.

Uso:
    from estelas import dibujar_con_cometa, recorrer_con_estela, tramo
    orbita = Ellipse(width=6, height=2.4, color=BLUE_B)
    self.play(dibujar_con_cometa(orbita, color=BLUE_A, run_time=2))
    self.play(recorrer_con_estela(Dot(color=YELLOW), orbita, largo=0.18, run_time=3))

Detalle que decide: `Create` reparte el avance por CURVAS de Bézier, no por longitud de arco. Si la
punta se colocara con `point_from_proportion` (longitud de arco) se despegaría del trazo en las
curvas desiguales. `punto_de_trazo` reproduce la cuenta de `Create`; `remuestrear` iguala las curvas
de una trayectoria cuando además se quiere velocidad uniforme.
"""

import numpy as np
from manim import (AnimationGroup, Circle, Create, Dot, UpdateFromAlphaFunc, VGroup, VMobject,
                   WHITE, linear, smooth)
from manim.utils.bezier import bezier


def punto_de_trazo(vmob, t):
    """El extremo que dibuja `Create(vmob)` cuando su avance vale `t` (0..1).

    Reproduce `pointwise_become_partial(vmob, 0, t)`: el avance se reparte por número de curvas.
    """
    pts = vmob.points
    n = len(pts) // 4
    if n == 0:
        return vmob.get_center()
    if t >= 1:
        return pts[-1].copy()
    if t <= 0:
        return pts[0].copy()
    i = min(int(t * n), n - 1)
    return bezier(pts[4 * i:4 * i + 4])(t * n - i)


def _en_proporcion(vmob, a):
    """`point_from_proportion` sin su fallo de redondeo en los extremos (a=1 puede lanzar)."""
    if a <= 0:
        return vmob.get_start()
    if a >= 1:
        return vmob.get_end()
    return vmob.point_from_proportion(a)


def remuestrear(vmob, n=64):
    """Copia de `vmob` hecha de `n` curvas de igual longitud (velocidad uniforme al dibujarla).

    Mide la longitud de arco muestreando cada Bézier en 48 puntos (el `point_from_proportion` de
    Manim la aproxima y deja curvas hasta un 30 % desiguales), toma `n + 1` puntos equidistantes y
    los une con `set_points_smoothly`.
    """
    pts = vmob.points
    curvas = [pts[4 * i:4 * i + 4] for i in range(len(pts) // 4)]
    if not curvas:
        return vmob.copy()
    s = np.linspace(0, 1, 48)
    denso = np.vstack([np.array([bezier(c)(t) for t in s])
                       for c in curvas])
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(denso, axis=0), axis=1))]
    objetivo = np.linspace(0, d[-1], n + 1)
    puntos = np.c_[[np.interp(objetivo, d, denso[:, k]) for k in range(3)]].T
    nuevo = VMobject().set_points_smoothly(puntos)
    nuevo.match_style(vmob)
    return nuevo


def punta_cometa(color=WHITE, radio=0.045, capas=5, alcance=3.4, opacidad=0.55):
    """Núcleo con halo radial (VGroup). Sus capas guardan la opacidad base para poder apagarlo."""
    grupo = VGroup()
    for i in range(capas, 0, -1):
        r = radio * (1 + (alcance - 1) * i / capas)
        op = opacidad * (1 - i / (capas + 1)) ** 3
        capa = Circle(radius=r, stroke_width=0, fill_color=color, fill_opacity=op)
        capa.opacidad_base = op
        grupo.add(capa)
    nucleo = Dot(radius=radio, color=color)
    nucleo.opacidad_base = 1.0
    grupo.add(nucleo)
    return grupo


def _apagar(punta, factor):
    for capa in punta:
        capa.set_fill(opacity=capa.opacidad_base * factor)


def _rampa(t, apagado):
    """1 casi todo el recorrido; baja a 0 en el último `apagado` (fracción) del avance."""
    if apagado <= 0:
        return 1.0
    return float(np.clip((1 - t) / apagado, 0, 1))


def dibujar_con_cometa(trayecto, color=None, radio=0.045, run_time=1.6, rate_func=smooth,
                       apagado=0.12, alcance=3.4):
    """`Create(trayecto)` con un cometa en la punta que se apaga en el último `apagado` del trazo.

    `color` por defecto es el del trazo. El trayecto queda en escena; el cometa no.
    """
    referencia = trayecto.copy()               # Create va recortando `trayecto`: la punta se mide aquí
    color = color or trayecto.get_stroke_color()
    punta = punta_cometa(color=color, radio=radio, alcance=alcance)
    punta.move_to(referencia.get_start())
    _apagar(punta, 0)

    def mover(m, a):
        m.move_to(punto_de_trazo(referencia, a))
        _apagar(m, _rampa(a, apagado) * float(np.clip(a / 0.04, 0, 1)))

    return AnimationGroup(
        Create(trayecto, rate_func=rate_func, run_time=run_time),
        UpdateFromAlphaFunc(punta, mover, rate_func=rate_func, run_time=run_time, remover=True),
    )


def tramo(trayecto, desde, hasta, color=None, ancho=None, opacidad=1.0):
    """Copia del pedazo [desde, hasta] (fracciones por curvas, como `Create`) de un trayecto."""
    t = VMobject()
    if hasta > desde:
        t.pointwise_become_partial(trayecto, max(desde, 0), min(hasta, 1))
    t.set_fill(opacity=0)
    t.set_stroke(color=color or trayecto.get_stroke_color(),
                 width=trayecto.get_stroke_width() if ancho is None else ancho, opacity=opacidad)
    return t


def _llenar_estela(estela, ref, t, largo, color, ancho, opacidad):
    n = len(estela)
    for i, seg in enumerate(estela):
        a = t - largo * (1 - i / n)
        b = t - largo * (1 - (i + 1) / n)
        if b <= 0 or b <= a or a >= 1:
            seg.clear_points()
            continue
        seg.pointwise_become_partial(ref, max(a, 0), min(b, 1))
        k = (i + 1) / n                      # 0 cola → 1 junto al objeto
        seg.set_stroke(color=color, width=ancho * (0.25 + 0.75 * k), opacity=opacidad * k ** 1.6)


def recorrer_con_estela(mobject, trayecto, largo=0.2, color=None, ancho=4, opacidad=0.85,
                        segmentos=16, run_time=2.0, rate_func=smooth, orientar=False,
                        recoger_estela=True, aparecer=0.0):
    """Mueve `mobject` a lo largo de `trayecto` (por longitud de arco) con una estela detrás.

    `largo` es la fracción del trayecto que ocupa la estela. Con `recoger_estela` la cola alcanza al
    objeto en el tramo final, así no queda una línea colgando al detenerse. Con `orientar` el
    objeto gira para mirar en la dirección del movimiento (su «frente» es +x). Con `aparecer` > 0 el
    objeto entra desde opacidad 0 en esa fracción inicial (útil dentro de `Succession`, donde el
    objeto ya está en escena antes de que le toque moverse).
    """
    ref = remuestrear(trayecto, 96)            # curvas iguales: estela y objeto avanzan parejos
    color = color or trayecto.get_stroke_color()
    estela = VGroup(*[VMobject() for _ in range(segmentos)])
    angulo = [0.0]

    def mover(m, a):
        m.move_to(punto_de_trazo(ref, a))     # mismo reparto que la estela: van pegados
        if aparecer > 0:
            m.set_opacity(float(np.clip(a / aparecer, 0, 1)))
        if orientar:
            d = _en_proporcion(ref, a + 1e-3) - _en_proporcion(ref, a - 1e-3)
            nuevo = np.arctan2(d[1], d[0])
            m.rotate(nuevo - angulo[0])
            angulo[0] = nuevo

    def cola(e, a):
        l = largo * (_rampa(a, largo) if recoger_estela else 1.0)
        _llenar_estela(e, ref, a, l, color, ancho, opacidad)

    return AnimationGroup(
        UpdateFromAlphaFunc(mobject, mover, rate_func=rate_func, run_time=run_time),
        UpdateFromAlphaFunc(estela, cola, rate_func=rate_func, run_time=run_time, remover=True),
    )


def destello_en(trayecto, color=WHITE, largo=0.18, ancho=None, run_time=1.0, rate_func=linear):
    """Un pulso de luz que recorre un trayecto ya dibujado (como `ShowPassingFlash`, con cola
    degradada). El trayecto no cambia; el destello se quita al terminar."""
    ancho = trayecto.get_stroke_width() * 1.15 if ancho is None else ancho
    ref = trayecto.copy()
    estela = VGroup(*[VMobject() for _ in range(14)])

    def pasar(e, a):
        _llenar_estela(e, ref, a * (1 + largo), largo, color, ancho, 0.95)

    return UpdateFromAlphaFunc(estela, pasar, rate_func=rate_func, run_time=run_time, remover=True)

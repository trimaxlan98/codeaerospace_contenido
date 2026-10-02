"""Logo de Co.De Aerospace en Manim: el logo vectorial por partes y sus animaciones de marca.

El logo NO se dibuja a ojo: su geometría sale del PNG oficial (`marca/originales/`) por
`marca/vectorizar_logo.py` y vive en `marca_aerospace.json`, junto a este archivo. Ahí cada parte va
por separado, que es lo que permite animarlo:

    logo.orbitas            6 arcos como TRAZO (línea central + grosor): se dibujan con Create
    logo.orbitas_contorno   los mismos 6 arcos como relleno, fieles al pixel (IoU 0.99 con el PNG)
    logo.luna               el círculo sobre la órbita grande
    logo.satelite           VGroup(panel_1, cuerpo, panel_2)
    logo.letras             VGroup(C, O, punto, D, E)   (logo.co, logo.de, logo.punto)
    logo.aerospace          VGroup de las 9 letras de AEROSPACE

El trazo de las órbitas se parece al PNG en un 95 % (IoU); el contorno, en un 99 %. Por eso las
animaciones dibujan con el trazo y, al terminar, lo cambian por el contorno sin que se note: el
último cuadro es el logo exacto.

Colores: «plata» (degradado vertical medido en el PNG plata, para fondos oscuros), «negro» (fondos
claros) o cualquier color de Manim. La paleta de la marca está en las constantes de abajo.

Uso:
    import sys
    sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from marca_aerospace import LogoCoDe, animar_entrada, FONDO

    class Intro(Scene):
        def construct(self):
            self.camera.background_color = FONDO
            logo = LogoCoDe(altura=5.6)
            animar_entrada(self, logo, estilo="orbital")   # o "trazo", "ensamble"
            self.wait()

Para una marca de agua: `self.add(marca_agua_aerospace())`.
"""

import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from manim import (DOWN, DR, LEFT, RIGHT, UP, AnimationGroup, Circle, Create, DrawBorderThenFill,
                   FadeIn, FadeOut, LaggedStart, ManimColor, ShowPassingFlash, Succession, Transform,
                   UpdateFromAlphaFunc, VGroup, VMobject, Wait, interpolate_color, linear,
                   rate_functions, smooth)

from estelas import destello_en, dibujar_con_cometa, recorrer_con_estela

GEOMETRIA = Path(__file__).resolve().with_name("marca_aerospace.json")

# Paleta de la marca (medida en los PNG oficiales y en codeaerospace.com).
FONDO = "#080F15"          # fondo del logo oficial
MARINO = "#0A0E27"         # fondo de codeaerospace.com
PLATA = ("#F2F3F4", "#D3D5D8")   # degradado del logo plata, de arriba abajo
PLATA_MEDIA = "#E3E5E7"
TINTA = "#0A0D12"          # logo en una tinta sobre fondos claros
PAPEL = "#F7F8F9"          # fondo claro de la marca
CIAN = "#00D9FF"           # acento de codeaerospace.com
AMBAR = "#F59E0B"          # acento secundario (CO.DE Academy)

FUENTE = "Montserrat"      # la más cercana a las letras del logo (OFL, en fonts/)


@lru_cache(maxsize=1)
def geometria():
    """La geometría del logo (px del PNG oficial, y hacia abajo)."""
    return json.loads(GEOMETRIA.read_text(encoding="utf-8"))


def _vm_cubicas(subtrayectos, f):
    """Subtrayectos de cúbicas [[p0, c1, c2, p3], ...] → un VMobject relleno (regla nonzero)."""
    vm = VMobject()
    for cub in subtrayectos:
        vm.start_new_path(f(cub[0][0]))
        for c in cub:
            vm.add_cubic_bezier_curve_to(f(c[1]), f(c[2]), f(c[3]))
    vm.set_stroke(width=0)
    return vm


def _circulo(c, f, escala):
    return Circle(radius=c["radio"] * escala).move_to(f(c["centro"])).set_stroke(width=0)


class LogoCoDe(VGroup):
    """El logo de Co.De Aerospace como VGroup animable por partes.

    altura      alto total en unidades de Manim (el logo es casi cuadrado: ancho ≈ 1.05 × alto)
    color       "plata" (por defecto), "negro", "blanco", un color o una pareja (arriba, abajo)
    aerospace   False quita la palabra AEROSPACE (emblema)
    contorno    True arma las órbitas ya como contorno (logo estático exacto, sin animar)
    """

    def __init__(self, altura=5.0, color="plata", aerospace=True, contorno=False, **kwargs):
        super().__init__(**kwargs)
        g = geometria()
        x0, y0, x1, y1 = g["caja"]
        self._origen = np.zeros(3)        # dónde está el centro del logo (ver mover_a)
        self.escala = escala = altura / (y1 - y0)
        self._centro_px = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        f = self.px

        self.orbitas = VGroup()
        for o in g["orbitas"]:
            arco = VMobject().set_points_smoothly([f(p) for p in o["puntos"]])
            # Manim mide el trazo en centésimas de unidad: grosor_px · escala / 0.01.
            arco.set_stroke(width=100 * o["grosor"] * escala).set_fill(opacity=0)
            self.orbitas.add(arco)
        self.orbitas_contorno = _vm_cubicas(g["orbitas_contorno"], f)
        # El contorno no es hijo del grupo hasta el cambio: se guarda dónde estaba el trazo cuando
        # ambos coincidían para llevarlo, en `usar_contorno`, a donde el grupo se haya movido.
        self._caja_orbitas = (self.orbitas.get_center(), self.orbitas.width)
        self.luna = _circulo(g["luna"], f, escala)
        sat = g["satelite"]
        self.satelite = VGroup(*[_vm_cubicas(sat[k], f) for k in ("panel_1", "cuerpo", "panel_2")])
        self.panel_1, self.cuerpo, self.panel_2 = self.satelite
        letras = g["letras"]
        self.punto = _circulo(g["punto"], f, escala)
        self.co = VGroup(_vm_cubicas(letras["C"], f), _vm_cubicas(letras["O"], f))
        self.de = VGroup(_vm_cubicas(letras["D"], f), _vm_cubicas(letras["E"], f))
        self.letras = VGroup(*self.co, self.punto, *self.de)
        self.aerospace = VGroup(*[_vm_cubicas(l, f) for l in g["aerospace"]])

        self.add(self.orbitas_contorno if contorno else self.orbitas, self.luna, self.satelite, self.letras)
        if aerospace:
            self.add(self.aerospace)
        self.color_logo = color
        self.pintar(color)

    def px(self, p):
        """Punto en px del PNG oficial → coordenadas de escena (respecto al centro del logo)."""
        c = self._centro_px
        return np.array([(p[0] - c[0]) * self.escala, -(p[1] - c[1]) * self.escala, 0.0]) + self._origen

    def mover_a(self, punto):
        """Lleva el centro del logo a `punto` ANTES de animarlo (un shift suelto desalinearía los
        trayectos de la entrada orbital, que se calculan con `px`)."""
        punto = np.array([*punto, 0.0][:3], dtype=float)
        self.shift(punto - self._origen)
        self._origen = punto
        return self

    def _degradado(self, color):
        if color == "plata":
            return PLATA
        if color == "negro":
            return (TINTA, TINTA)
        if color == "blanco":
            return ("#FFFFFF", "#FFFFFF")
        if isinstance(color, (tuple, list)):
            return tuple(color)
        return (color, color)

    def pintar(self, color="plata"):
        """Aplica el color a todas las partes. Con degradado, cada parte toma el tramo del degradado
        GLOBAL que le corresponde por su altura (Manim degrada por objeto, no por grupo)."""
        arriba, abajo = (ManimColor(c) for c in self._degradado(color))
        partes = [*self.orbitas, self.orbitas_contorno, self.luna, *self.satelite, *self.letras,
                  *self.aerospace]
        ys = [p.get_top()[1] for p in partes] + [p.get_bottom()[1] for p in partes]
        tope, base = max(ys), min(ys)
        tono = lambda y: interpolate_color(arriba, abajo, float(np.clip((tope - y) / (tope - base), 0, 1)))
        for p in partes:
            c1, c2 = tono(p.get_top()[1]), tono(p.get_bottom()[1])
            if p in self.orbitas:
                p.set_stroke(color=[c1, c2]).set_sheen_direction(DOWN)
            else:
                # El trazo (ancho 0) toma el mismo color: DrawBorderThenFill dibuja el contorno con
                # el color de trazo, que por defecto es blanco (y rojo en Circle).
                p.set_fill(color=[c1, c2], opacity=1).set_stroke(color=[c1, c2], width=0)
                p.set_sheen_direction(DOWN)
        self.color_logo = color
        return self

    def usar_contorno(self):
        """Cambia las órbitas de trazo por el contorno exacto (mismo lugar, mismo color)."""
        if self.orbitas in self.submobjects:
            centro0, ancho0 = self._caja_orbitas
            k = self.orbitas.width / ancho0
            self.orbitas_contorno.scale(k, about_point=centro0).shift(self.orbitas.get_center() - centro0)
            self._caja_orbitas = (self.orbitas.get_center(), self.orbitas.width)
            i = self.submobjects.index(self.orbitas)
            self.submobjects[i] = self.orbitas_contorno
        return self


# ── Animaciones de marca ────────────────────────────────────────────────────────────

def _bajar_punto(logo, alto=1.4):
    """El punto de CO.DE cae desde arriba y rebota en su lugar."""
    destino = logo.punto.get_center()
    logo.punto.shift(alto * UP).set_opacity(0)

    def caer(m, a):
        y = rate_functions.ease_out_bounce(a)
        m.move_to(destino + (1 - y) * alto * UP)
        m.set_fill(opacity=min(1, a * 4))

    return UpdateFromAlphaFunc(logo.punto, caer, run_time=0.9, rate_func=linear)


def _abrir_tracking(logo, compresion=0.55, run_time=1.1):
    """AEROSPACE aparece con el espaciado cerrado y se abre hasta su tracking real."""
    centro = logo.aerospace.get_center()
    finales = [l.get_center() for l in logo.aerospace]
    for l, p in zip(logo.aerospace, finales):
        l.move_to(centro + (p - centro) * np.array([compresion, 1, 1])).set_opacity(0)

    def abrir(m, a):
        k = compresion + (1 - compresion) * a
        for l, p in zip(m, finales):
            l.move_to(centro + (p - centro) * np.array([k, 1, 1]))
            l.set_fill(opacity=min(1, a * 1.6))

    return UpdateFromAlphaFunc(logo.aerospace, abrir, run_time=run_time, rate_func=smooth)


def _plegar_paneles(logo, factor=0.08):
    """Pliega los paneles contra el cubo (para desplegarlos después). Devuelve la animación de
    despliegue."""
    centro = logo.cuerpo.get_center()
    objetivos = [logo.panel_1.copy(), logo.panel_2.copy()]
    for p in (logo.panel_1, logo.panel_2):
        eje = p.get_center() - centro
        ang = np.arctan2(eje[1], eje[0])
        p.rotate(-ang, about_point=centro).stretch(factor, 0, about_point=centro).rotate(ang, about_point=centro)
    return AnimationGroup(Transform(logo.panel_1, objetivos[0]), Transform(logo.panel_2, objetivos[1]),
                          run_time=0.8, rate_func=rate_functions.ease_out_back)


def _trayecto(logo, puntos_px, hasta_px=None, invertir=False):
    pts = [logo.px(p) for p in puntos_px]
    if invertir:
        pts = pts[::-1]
    if hasta_px is not None:
        fin = logo.px(hasta_px)
        pts += [pts[-1] + (fin - pts[-1]) * k for k in (0.5, 1.0)]
    return VMobject().set_points_smoothly(pts)


def animar_entrada(escena, logo, estilo="orbital", acento=CIAN, ritmo=1.0):
    """Hace entrar el logo en `escena` (llama a escena.play). Al terminar, el logo completo queda en
    escena con las órbitas como contorno exacto.

    estilo   "orbital"  órbitas con cometa, luna y satélite por sus órbitas, paneles que se
                        despliegan, CO.DE trazado, el punto que cae y AEROSPACE que se abre (≈5.5 s)
             "trazo"    todo se traza y se rellena a la vez, con desfase (≈2.6 s)
             "ensamble" las partes llegan desde fuera y encajan (≈2.4 s)
    ritmo    multiplica las duraciones (0.7 = más rápido)
    """
    r = ritmo
    if estilo == "trazo":
        partes = [*logo.orbitas, logo.luna, logo.satelite, *logo.letras]
        if logo.aerospace in logo.submobjects:
            partes.append(logo.aerospace)
        escena.play(LaggedStart(*[DrawBorderThenFill(p, stroke_width=1.5) if p not in logo.orbitas
                                  else Create(p) for p in partes], lag_ratio=0.08, run_time=2.6 * r))
        _fijar_contorno(escena, logo)
        return

    if estilo == "ensamble":
        destinos = {}
        for i, p in enumerate([logo.orbitas, logo.luna, logo.satelite, logo.co, logo.punto, logo.de,
                               logo.aerospace]):
            if p is logo.aerospace and p not in logo.submobjects:
                continue
            dirs = [LEFT + UP, RIGHT + UP, UP, LEFT, DOWN, RIGHT, DOWN]
            destinos[p] = dirs[i]
        escena.play(LaggedStart(*[FadeIn(p, target_position=p.get_center() + 3.2 * d, scale=0.6)
                                  for p, d in destinos.items()],
                                lag_ratio=0.12, run_time=2.4 * r, rate_func=rate_functions.ease_out_cubic))
        _fijar_contorno(escena, logo)
        return

    if estilo != "orbital":
        raise ValueError(f"estilo desconocido: {estilo!r} (orbital, trazo, ensamble)")

    g = geometria()
    orb = g["orbitas"]
    k = logo.escala / 0.0048           # 1 cuando el logo mide 4 unidades: tamaños de cometa y estela
    # 1 · Órbitas con cometa (cian), en el orden en que el ojo recorre el logo.
    dibujos = [dibujar_con_cometa(a, color=acento, run_time=1.5 * r, radio=0.035 * k) for a in logo.orbitas]
    # 2 · La luna llega por su órbita: el arco grande de arriba a la izquierda (orbitas[2]) termina
    #     junto a ella; se recorre de abajo hacia arriba y sigue hasta su centro.
    luna_tray = _trayecto(logo, orb[2]["puntos"], hasta_px=g["luna"]["centro"], invertir=True)
    luna_destino = logo.luna.get_center()
    logo.luna.move_to(luna_tray.get_start()).set_opacity(0)
    llega_luna = recorrer_con_estela(logo.luna, luna_tray, largo=0.22, color=acento, ancho=6 * k,
                                     run_time=1.9 * r, aparecer=0.1)
    # 3 · El satélite entra plegado por la órbita plana (orbitas[1]) desde su extremo derecho. Se
    #     pliega ANTES de medir su centro: así aterriza donde el despliegue lo deja exacto.
    desplegar = _plegar_paneles(logo)
    sat_destino = logo.satelite.get_center()
    sat_tray = _trayecto(logo, orb[1]["puntos"], invertir=True)
    sat_tray.shift(sat_destino - sat_tray.get_end())   # la órbita lo deja justo en su lugar
    logo.satelite.move_to(sat_tray.get_start()).set_opacity(0)
    llega_sat = recorrer_con_estela(logo.satelite, sat_tray, largo=0.25, color=acento, ancho=5 * k,
                                    run_time=1.7 * r, aparecer=0.12)

    escena.play(LaggedStart(*dibujos, lag_ratio=0.16),
                Succession(Wait(0.35 * r), llega_luna),
                Succession(Wait(0.6 * r), llega_sat))
    logo.luna.move_to(luna_destino)
    # 4 · Paneles que se despliegan + CO.DE que se traza y se rellena.
    escena.play(desplegar,
                LaggedStart(*[DrawBorderThenFill(l, stroke_width=1.6, run_time=1.3 * r)
                              for l in (*logo.co, *logo.de)], lag_ratio=0.18))
    # 5 · El punto cae y AEROSPACE se abre.
    animaciones = [_bajar_punto(logo)]
    if logo.aerospace in logo.submobjects:
        animaciones.append(Succession(Wait(0.25 * r), _abrir_tracking(logo, run_time=1.1 * r)))
    escena.play(*animaciones)
    # 6 · Destello: un pulso blanco recorre cada órbita y un brillo pasa por las letras.
    contornos = VGroup(*[l.copy().set_fill(opacity=0).set_stroke(color="#FFFFFF", width=2.2)
                         for l in (*logo.co, *logo.de)])
    escena.play(*[destello_en(a, color="#FFFFFF", run_time=0.9 * r) for a in logo.orbitas],
                ShowPassingFlash(contornos, time_width=0.35, run_time=0.9 * r))
    _fijar_contorno(escena, logo)


def _fijar_contorno(escena, logo):
    """Cambia, sin que se note, las órbitas de trazo por el contorno exacto y deja el logo como UN
    objeto en escena (las animaciones agregan sus partes sueltas; sin quitarlas se dibujarían dos
    veces y los bordes engordarían)."""
    familia = set(logo.get_family())
    escena.remove(*[m for m in escena.mobjects if m in familia])
    logo.usar_contorno()
    escena.add(logo)


def animar_salida(escena, logo, ritmo=1.0):
    """Las órbitas se borran en reversa, el satélite se va y las letras se desvanecen hacia abajo."""
    salen = [FadeOut(logo.letras, shift=0.15 * DOWN), FadeOut(logo.satelite, shift=0.5 * (RIGHT + UP)),
             FadeOut(logo.luna, scale=0.4)]
    if logo.aerospace in logo.submobjects:
        salen.append(FadeOut(logo.aerospace))
    orbitas = logo.orbitas_contorno if logo.orbitas_contorno in logo.submobjects else logo.orbitas
    escena.play(LaggedStart(FadeOut(orbitas, scale=1.08), *salen, lag_ratio=0.08), run_time=1.1 * ritmo)


def sting_logo(escena, logo, acento=CIAN):
    """Versión ultra corta (≈1.6 s): el logo aparece con un destello que recorre sus órbitas."""
    escena.play(FadeIn(logo, scale=0.94), run_time=0.6, rate_func=rate_functions.ease_out_cubic)
    escena.play(*[destello_en(a, color=acento, run_time=1.0) for a in logo.orbitas])
    _fijar_contorno(escena, logo)


def marca_agua_aerospace(altura=0.62, esquina=DR, opacidad=0.55, color="plata", buff=0.3):
    """El logo chico en una esquina, por encima de todo (z_index alto). Estático y exacto."""
    m = LogoCoDe(altura=altura, color=color, contorno=True)
    m.set_opacity(opacidad).to_corner(esquina, buff=buff)
    m.set_z_index(1000)
    return m

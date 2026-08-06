"""Identidad CO.DE Academy para los videos del canal (division de CO.DE
Aerospace): paleta oficial, tipografias propias (Rajdhani / Space Mono,
OFL, en fonts/), marca de agua sutil y rotulos que no se enciman.

La estetica es "HUD aeroespacial": fondo casi negro, acento ambar->naranja,
titulos Rajdhani, etiquetas de telemetria en Space Mono MAYUSCULAS. La marca
de agua es un wordmark chico en la esquina inferior derecha con el punto de
CO.DE en ambar (el rasgo distintivo del logotipo) — nunca tapa contenido.

Uso tipico en el bloque de estilo de un curso:
    import sys
    sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from code_brand import (registrar_fuentes, aplicar_marca, Rotulos,
                            titulo_marca, etiqueta_hud, CODE_ACCENT)
    registrar_fuentes()          # una vez por proceso, antes de crear Text

    class EscenaCurso(Scene):
        def setup(self):
            aplicar_marca(self)  # fondo + marca de agua + esquinas HUD

En las escenas, para textos que se reemplazan sin encimarse:
    rotulos = Rotulos(self)
    rotulos.mostrar(pie("Primera idea"), zona="abajo")
    rotulos.mostrar(pie("La segunda desvanece a la primera"), zona="abajo")
"""

from pathlib import Path

from manim import (DR, DOWN, FadeIn, FadeOut, Line, RIGHT, Text, UP, VGroup,
                   config)

# Paleta oficial CO.DE Academy (code-academy-platform/src/app/globals.css)
CODE_BG = "#05070a"        # fondo casi negro de la marca
CODE_INK = "#e8edf3"       # texto principal
CODE_MUTED = "#94a0b0"     # texto secundario
CODE_ACCENT = "#f59e0b"    # ambar de la division Academy
CODE_ACCENT_2 = "#ea580c"  # naranja: cierre del degradado del wordmark

FUENTE_DISPLAY = "Rajdhani"    # titulos y wordmark
FUENTE_HUD = "Space Mono"      # telemetria / etiquetas MAYUSCULAS

_FONTS_DIR = Path(__file__).resolve().parent / "fonts"
_registradas = False


def registrar_fuentes() -> None:
    """Registra las TTF del repo en Pango (idempotente). Funciona igual en el
    host y dentro del contenedor de render (ruta relativa a este archivo)."""
    global _registradas
    if _registradas:
        return
    import manimpango
    for ttf in sorted(_FONTS_DIR.glob("*.ttf")):
        manimpango.register_font(str(ttf))
    _registradas = True


def marca_agua(escala=1.0):
    """Wordmark "CO.DE ACADEMY" sutil: gris tenue con el punto en ambar.
    Pensada para la esquina inferior derecha, sin tapar contenido."""
    registrar_fuentes()
    co = Text("CO", font=FUENTE_DISPLAY, weight="SEMIBOLD", font_size=16)
    punto = Text(".", font=FUENTE_DISPLAY, weight="BOLD", font_size=16,
                 color=CODE_ACCENT)
    de = Text("DE", font=FUENTE_DISPLAY, weight="SEMIBOLD", font_size=16)
    academy = Text("ACADEMY", font=FUENTE_DISPLAY, weight="MEDIUM",
                   font_size=16, color=CODE_MUTED)
    marca = VGroup(co, punto, de, academy).arrange(buff=0.06)
    academy.shift(0.06 * RIGHT)
    marca.scale(escala).set_opacity(0.38)
    marca.to_corner(DR, buff=0.28)
    # Siempre por encima del contenido (incluidas imagenes a pantalla llena,
    # p. ej. fractales): Cairo ordena por z_index.
    marca.set_z_index(1000)
    return marca


def esquinas_hud(opacidad=0.16, largo=0.42, color=CODE_ACCENT):
    """Cuatro escuadras de esquina estilo HUD, casi imperceptibles: enmarcan
    sin distraer (estetica de consola de vuelo de la marca)."""
    ancho = config.frame_width / 2 - 0.18
    alto = config.frame_height / 2 - 0.18
    esquinas = VGroup()
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        x, y = sx * ancho, sy * alto
        h = Line((x - sx * largo, y, 0), (x, y, 0), stroke_width=1.6)
        v = Line((x, y - sy * largo, 0), (x, y, 0), stroke_width=1.6)
        esquinas.add(h, v)
    esquinas.set_color(color).set_opacity(opacidad)
    esquinas.set_z_index(999)
    return esquinas


def aplicar_marca(escena, esquinas=True, marca=True, fondo=True) -> None:
    """Fondo de marca + marca de agua + esquinas HUD como capa fija de la
    escena. Llamar en `setup()` para que quede debajo de todo lo demas."""
    if fondo:
        config.background_color = CODE_BG
        escena.camera.background_color = CODE_BG
    if esquinas:
        escena.add(esquinas_hud())
    if marca:
        escena.add(marca_agua())


def _fondo_propio() -> bool:
    """¿El script eligio su propio fondo? (si sigue en el negro por defecto
    de Manim, manda el de la marca)."""
    try:
        return config.background_color.to_hex().lower() not in ("#000000",
                                                                "#000")
    except Exception:
        return False


def _marcar_clase(cls, fondo: bool) -> None:
    setup_original = cls.setup

    def setup(self):
        setup_original(self)
        aplicar_marca(self, fondo=fondo)

    cls.setup = setup
    cls._code_brand = True


def marcar_escenas(ns: dict) -> None:
    """Aplica la identidad a todas las escenas definidas en `ns` (el
    `globals()` del script). ManimStudio anexa la llamada al FINAL de los
    scripts que no traen marca propia: la identidad es el minimo visual del
    canal, no una opcion del autor.

    Va al final a proposito — manim importa el modulo entero antes de
    instanciar la escena, asi que anexar (en vez de anteponer) deja intactos
    los numeros de linea que reporta un error.

    Idempotente: una clase ya marcada, o que hereda de una marcada, se salta;
    un curso con su propia base de marca no la duplica.
    """
    from manim import Scene as _Scene

    registrar_fuentes()
    fondo = not _fondo_propio()
    if fondo:
        config.background_color = CODE_BG
    modulo = ns.get("__name__")
    for obj in list(ns.values()):
        if (isinstance(obj, type) and issubclass(obj, _Scene)
                and obj.__module__ == modulo
                and not getattr(obj, "_code_brand", False)):
            _marcar_clase(obj, fondo)


def titulo_marca(texto, font_size=34, color=CODE_INK):
    """Titulo display en Rajdhani (tipografia propia del canal)."""
    registrar_fuentes()
    return Text(texto, font=FUENTE_DISPLAY, weight="SEMIBOLD",
                font_size=font_size, color=color)


def etiqueta_hud(texto, font_size=15, color=CODE_MUTED):
    """Etiqueta de telemetria: Space Mono, MAYUSCULAS con aire entre letras
    (convencion "MODULO_03" / "EN VIVO" de la marca)."""
    registrar_fuentes()
    espaciado = " ".join(texto.upper())
    return Text(espaciado, font=FUENTE_HUD, font_size=font_size, color=color)


class Rotulos:
    """Rotulos por zona que NO se enciman: mostrar uno nuevo desvanece al
    anterior de esa zona en la misma animacion.

    Zonas tipicas: "arriba" (titulos), "abajo" (pies), o cualquier clave
    propia. El posicionamiento del mobject es responsabilidad del que llama;
    la clase solo garantiza el relevo limpio.
    """

    def __init__(self, escena) -> None:
        self.escena = escena
        self._zonas: dict = {}

    def mostrar(self, mobjeto, zona="abajo", run_time=0.45, **kwargs):
        previo = self._zonas.get(zona)
        anims = [FadeIn(mobjeto, shift=0.12 * UP)]
        if previo is not None:
            anims.append(FadeOut(previo, shift=0.12 * DOWN))
        self.escena.play(*anims, run_time=run_time, **kwargs)
        self._zonas[zona] = mobjeto
        return mobjeto

    def limpiar(self, zona=None, run_time=0.35):
        objetivos = ([self._zonas.pop(zona)] if zona in self._zonas
                     else [self._zonas.pop(z) for z in list(self._zonas)]
                     if zona is None else [])
        if objetivos:
            self.escena.play(*[FadeOut(o) for o in objetivos],
                             run_time=run_time)

"""Figuras de paper: lienzo IEEE, tipografia medida en puntos y proveniencia.

Esta libreria NO es para el canal: es para la TESIS y para los papers. Lo que
cambia respecto del resto de manim_extensions es la disciplina, no el dibujo:

1. **El lienzo es fisico.** `Figura(columnas=1)` fija `config.pixel_width/height`
   a las pulgadas de una columna IEEE (3.5 in) por los puntos por pulgada que
   se declaren (300 por defecto), y fija `frame_width` y `frame_height` en la
   MISMA proporcion, con 4 unidades de escena por pulgada. Consecuencia util:
   una unidad de escena son 18 puntos tipograficos SIEMPRE, en una columna y en
   dos, asi que un `font_size` significa el mismo tamano fisico en las dos.
2. **La tipografia se mide, no se estima.** `alto_pt(mob)` devuelve el alto de
   TINTA de un mobject en puntos tipograficos de la figura impresa y
   `fs_para_pt(p)` es su inversa. `exigir_legible(grupo)` aborta el render si
   algo se pinta por debajo del suelo (4.5 pt): un guardian que se prueba con
   un contraejemplo (lo hace `studio/tools/sonda_figura.py`).
3. **Toda figura sale sellada.** `sello()` estampa commit, semilla, fecha y
   version de la libreria en gris chico abajo a la derecha. Sin commit dice
   `sin-commit`, que es una afirmacion honesta, no un hueco.
4. **Los datos entran, no se transcriben.** `leer_csv` / `leer_jsonl` leen de
   `MS_DATOS_DIR` (por defecto `datos/` relativo al cwd del render) y fallan
   con un mensaje que dice donde buscaron.

Dos fondos:
  - `paper`: blanco con tinta #111 y la paleta Okabe-Ito (segura para las tres
    formas de daltonismo y distinguible impresa en gris). Fuente por defecto de
    manim, que SI trae acentos.
  - `marca`: el tema oscuro de code_brand, para la misma figura dentro de un
    video del canal. Rajdhani / Space Mono: en este tema, sin acentos.

Uso (el lienzo se fija a nivel de MODULO: la camara se construye antes que
`construct`, asi que tocar `config` dentro de la escena llega tarde):

    import sys
    sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    import figura as fg

    fg.Figura(tema="paper", columnas=1)          # <- nivel de modulo

    class FiguraA(Scene):
        def construct(self):
            fg.fondo(self)
            ax = fg.ejes_paper((0, 60), (0, 400), "tiempo (s)", "RTT (ms)")
            self.add(ax, fg.curva(ax, t, rtt), fg.sello(semilla=42))

    fg.sellar_escenas(globals())   # <- ver «La marca del canal» abajo

Y para sacar el PNG a 300 dpi, `-s` (guarda el ultimo fotograma):

    manim render -s --media_dir <dir> figura_a.py FiguraA

La marca del canal
------------------
ManimStudio ANEXA `code_brand.marcar_escenas(globals())` a todo script que no
mencione `code_brand`, y eso le pondria la marca de agua ambar del canal a una
figura de paper. `sellar_escenas(globals())` marca las escenas como ya
atendidas (`_code_brand = True`, el mismo campo que la marca usa para ser
idempotente), asi que el bloque anexado las salta. En el tema `marca` NO se
llama: ahi la marca de agua es lo que se quiere.

El espacio infla la caja
------------------------
`Text.width`, `.height`, `.get_center()`, `next_to()` y `move_to()` MIENTEN en
cuanto el texto tiene un espacio y se mueve del origen. Medido en manim 0.20.1:
cada espacio es un submobject VACIO, y `Mobject.reduce_across_dimension`
devuelve **0** para un submobject sin puntos, asi que la caja del texto se come
siempre el origen. `Text("RTT (ms)")` mide 0.2539 de alto recien nacido y
**2.1270** despues de un `shift`; sin espacios (`Text("0")`) no pasa. Por eso
esta libreria posiciona y mide con `caja()` / `ancho()` / `alto()` / `poner()` /
`pegar()`, que leen los puntos de verdad, y no usa `next_to` ni lee `.width`.
"""

import csv
import datetime
import json
import os
from pathlib import Path

import numpy as np
from manim import (Axes, DashedLine, Dot, Line, Polygon, Rectangle, Text,
                   VGroup, VMobject, config)

VERSION = "1.0"

# ── el lienzo fisico ────────────────────────────────────────────────────────
# Anchos de columna de las plantillas IEEE (IEEEtran): una columna 3.5 in,
# doble columna 7.16 in. Son las medidas de la plantilla, no una eleccion.
ANCHO_COLUMNA_IN = {1: 3.5, 2: 7.16}
DPI_POR_DEFECTO = 300
# 4 unidades de escena por pulgada => 1 unidad = 0.25 in = 18 pt exactos.
UNIDADES_POR_PULGADA = 4.0
PUNTOS_POR_UNIDAD = 72.0 / UNIDADES_POR_PULGADA      # 18.0
ALTO_REL_POR_DEFECTO = 0.62      # proporcion agradable para una figura suelta

# Suelo de legibilidad: por debajo de 4.5 pt una etiqueta impresa deja de
# leerse. El sello de proveniencia es la unica excepcion, y esta declarada.
PT_MINIMO = 4.5
PT_MINIMO_SELLO = 3.4

IZQ = np.array([-1.0, 0.0, 0.0])
DER = np.array([1.0, 0.0, 0.0])
ARR = np.array([0.0, 1.0, 0.0])
ABJ = np.array([0.0, -1.0, 0.0])
CENTRO = np.array([0.0, 0.0, 0.0])

# ── temas ───────────────────────────────────────────────────────────────────
# Paleta de series Okabe-Ito: la referencia estandar para figuras cientificas,
# segura con las tres formas de daltonismo y distinguible al imprimir en escala
# de grises. No se cambia por gusto.
PAPER = {
    "nombre": "paper",
    "fondo": "#ffffff",
    "tinta": "#111111",
    "eje": "#111111",
    "rejilla": "#cccccc",
    "apagado": "#666666",
    "sello": "#8a8a8a",
    "series": ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#56B4E9"),
    "up": "#2e8b57",
    "down": "#c0392b",
    "hueco": "#d5d5d5",
    "fuente": None,          # la de manim: trae acentos
    "fuente_mono": None,
}

MARCA = {
    "nombre": "marca",
    "fondo": "#05070a",      # code_brand.CODE_BG
    "tinta": "#e8edf3",      # code_brand.CODE_INK
    "eje": "#5c6b7a",
    "rejilla": "#1B3253",
    "apagado": "#94a0b0",    # code_brand.CODE_MUTED
    "sello": "#5c6773",
    "series": ("#f59e0b", "#5AC8D8", "#34d399", "#a78bfa", "#f43f5e"),
    "up": "#34d399",
    "down": "#f43f5e",
    "hueco": "#31414f",
    "fuente": "Rajdhani",
    "fuente_mono": "Space Mono",
}

TEMAS = {"paper": PAPER, "marca": MARCA}


def _par(n):
    """El entero par mas cercano por arriba.

    H.264 no codifica un lado impar: una columna IEEE a 300 dpi da 3.5 x 2.17
    in = 1050 x 651 px, y el render de video moria con
    `avcodec_open2("libx264") -> Generic error in an external library`, sin
    decir en ningun sitio que el problema era el 651. El PNG de `-s` salia
    perfecto, asi que el fallo aparecia solo al pedir el clip. Se sube un pixel
    (651 -> 652): 1/300 de pulgada de mas en el alto, y el tamano fisico
    efectivo se recalcula desde el pixel, asi que la figura no se deforma.
    """
    n = int(n)
    return n if n % 2 == 0 else n + 1


class LienzoIlegible(ValueError):
    """Algo se pinta por debajo del suelo de legibilidad de la figura."""


class FueraDelLienzo(ValueError):
    """Algo se sale del cuadro: en el PNG saldria cortado, sin avisar."""


class DatosNoEncontrados(FileNotFoundError):
    """El archivo de datos que pide la figura no esta donde se busco."""


# =============================================================================
# Geometria honesta: la caja de TINTA
# =============================================================================

def caja(mob):
    """(minimo, maximo) de los puntos que de verdad pinta `mob`, o None.

    Ni `.width`, ni `.height`, ni `.get_center()`, ni `next_to` sirven aqui:
    ver «El espacio infla la caja» arriba.
    """
    familia = [m for m in mob.family_members_with_points()]
    if not familia:
        return None
    puntos = np.vstack([m.points for m in familia])
    return puntos.min(axis=0), puntos.max(axis=0)


def ancho(mob):
    c = caja(mob)
    return 0.0 if c is None else float(c[1][0] - c[0][0])


def alto(mob):
    c = caja(mob)
    return 0.0 if c is None else float(c[1][1] - c[0][1])


def centro(mob):
    c = caja(mob)
    return np.zeros(3) if c is None else (c[0] + c[1]) / 2.0


def borde(mob, direccion):
    """Punto del borde de la caja de tinta en esa direccion (IZQ, ARR, ...)."""
    c = caja(mob)
    if c is None:
        return np.zeros(3)
    mid = (c[0] + c[1]) / 2.0
    d = np.asarray(direccion, dtype=np.float64)
    return np.array([c[1][i] if d[i] > 0 else c[0][i] if d[i] < 0 else mid[i]
                     for i in range(3)])


def poner(mob, punto, anclaje=CENTRO):
    """Mueve `mob` para que su `anclaje` caiga en `punto`. Devuelve `mob`."""
    punto = np.asarray(punto, dtype=np.float64)
    if punto.shape == (2,):
        punto = np.array([punto[0], punto[1], 0.0])
    mob.shift(punto - borde(mob, anclaje))
    return mob


def pegar(mob, ancla, direccion, hueco=0.0):
    """Coloca `mob` junto a `ancla` (punto o mobject) en `direccion`.

    El equivalente honesto de `next_to`: usa la caja de tinta de los dos.
    """
    d = np.asarray(direccion, dtype=np.float64)
    if hasattr(ancla, "family_members_with_points"):
        destino = borde(ancla, d)
    else:
        destino = np.asarray(ancla, dtype=np.float64)
        if destino.shape == (2,):
            destino = np.array([destino[0], destino[1], 0.0])
    return poner(mob, destino + d * hueco, anclaje=-d)


# =============================================================================
# Figura: el lienzo activo
# =============================================================================

class Figura:
    """Lienzo de una figura: tema, tamano fisico y resolucion.

    Construirla a nivel de MODULO. Deja la figura como «activa», que es la que
    usan las funciones sueltas (`ejes_paper`, `curva`, `sello`...).

        fg.Figura(tema="paper", columnas=2, alto_in=2.6, dpi=300)

    `columnas` elige el ancho de la plantilla IEEE (1 -> 3.5 in, 2 -> 7.16 in);
    `ancho_in` lo sobreescribe si hace falta otra medida. El alto sale de
    `alto_in`, o de `ancho_in * 0.62`.
    """

    def __init__(self, tema="paper", columnas=1, ancho_in=None, alto_in=None,
                 dpi=DPI_POR_DEFECTO, aplicar=True):
        if tema not in TEMAS:
            raise ValueError(f"tema desconocido: {tema!r} (hay {sorted(TEMAS)})")
        if ancho_in is None:
            if columnas not in ANCHO_COLUMNA_IN:
                raise ValueError("columnas tiene que ser 1 o 2 (o pasa ancho_in)")
            ancho_in = ANCHO_COLUMNA_IN[columnas]
        ancho_in = float(ancho_in)
        alto_in = float(alto_in) if alto_in else ancho_in * ALTO_REL_POR_DEFECTO
        dpi = int(dpi)
        if min(ancho_in, alto_in) <= 0 or dpi <= 0:
            raise ValueError("ancho_in, alto_in y dpi tienen que ser > 0")

        self.tema = TEMAS[tema]
        self.columnas = columnas
        self.dpi = dpi
        # Los pixeles mandan: se redondean primero y el tamano fisico efectivo
        # se recalcula a partir de ellos. Al reves, la proporcion del frame y
        # la de la imagen no coincidirian y el render saldria estirado unos
        # pocos por mil, sin avisar.
        self.pixel_width = _par(round(ancho_in * dpi))
        self.pixel_height = _par(round(alto_in * dpi))
        self.ancho_in = self.pixel_width / dpi
        self.alto_in = self.pixel_height / dpi
        self.frame_width = self.ancho_in * UNIDADES_POR_PULGADA
        self.frame_height = self.alto_in * UNIDADES_POR_PULGADA

        if aplicar:
            self.aplicar()
        activar(self)

    def aplicar(self):
        """Escribe el lienzo en `config`. Idempotente."""
        if self.tema["fuente"] is not None:
            _registrar_fuentes_marca()
        config.pixel_width = self.pixel_width
        config.pixel_height = self.pixel_height
        # frame_width y frame_height son INDEPENDIENTES en manim 0.20.1: fijar
        # uno NO recalcula el otro (medido). Hay que escribir los dos o la
        # figura sale deformada respecto de la imagen.
        config.frame_width = self.frame_width
        config.frame_height = self.frame_height
        config.background_color = self.tema["fondo"]
        return self

    @classmethod
    def pantalla(cls, tema="marca", alto_unidades=8.0):
        """Lienzo de VIDEO, no de papel: respeta los pixeles que ya fijo la
        calidad del render (`-ql`, `-qh`) y solo declara el tamano fisico
        equivalente para que la tipografia se siga midiendo en puntos.

        Asi una figura de la tesis se puede meter en un clip del canal sin
        cambiar ni una linea del dibujo: lo unico que cambia es el lienzo, y
        una unidad de escena sigue siendo 18 pt. En video los cuerpos comodos
        son 10-16 pt (a 1080p, 7 pt serian 52 px de alto y 14 pt, 105).
        """
        pw, ph = int(config.pixel_width), int(config.pixel_height)
        alto_in = float(alto_unidades) / UNIDADES_POR_PULGADA
        dpi = int(round(ph / alto_in))
        fig = cls(tema=tema, ancho_in=pw / dpi, alto_in=alto_in, dpi=dpi)
        if (fig.pixel_width, fig.pixel_height) != (pw, ph):
            raise ValueError(
                f"Figura.pantalla: no puedo declarar {pw}x{ph} px sin "
                f"deformar (saldria {fig.pixel_width}x{fig.pixel_height})")
        return fig

    def resumen(self):
        """Las cifras del lienzo, para el log y para las sondas."""
        return {"tema": self.tema["nombre"], "columnas": self.columnas,
                "ancho_in": self.ancho_in, "alto_in": self.alto_in,
                "dpi": self.dpi, "pixel_width": self.pixel_width,
                "pixel_height": self.pixel_height,
                "frame_width": self.frame_width,
                "frame_height": self.frame_height,
                "puntos_por_unidad": self.puntos_por_unidad()}

    def puntos_por_unidad(self):
        """Puntos tipograficos por unidad de escena en la figura IMPRESA."""
        return 72.0 * self.ancho_in / self.frame_width

    def zona(self, margen_pt=6.0):
        """(ancho, alto) en unidades de escena dejando un margen en puntos."""
        m = margen_pt / self.puntos_por_unidad()
        return (self.frame_width - 2 * m, self.frame_height - 2 * m)


_ACTIVA = None


def activar(fig):
    global _ACTIVA
    _ACTIVA = fig
    return fig


def activa():
    """La figura activa; si no hay ninguna, crea una de una columna en paper."""
    if _ACTIVA is None:
        Figura()
    return _ACTIVA


def tema():
    return activa().tema


def color(i):
    """Color i-esimo de la paleta de series del tema activo (ciclica)."""
    s = tema()["series"]
    return s[int(i) % len(s)]


def _registrar_fuentes_marca():
    try:
        import code_brand
        code_brand.registrar_fuentes()
    except Exception as e:            # la figura no depende del canal
        print("[figura] fuentes de marca no registradas:", e)


# =============================================================================
# Tipografia medida
# =============================================================================

_MUESTRA = "Hxdp"          # ascendente + equis + descendente: la caja de tinta
_K_TINTA = None            # unidades de escena de tinta por unidad de font_size


def _texto_crudo(cadena, font_size, puntos=None, **kw):
    """`Text` con la fuente del tema, marcado con su tamano NOMINAL.

    Dos detalles medidos:

    - `font=None` NO vale: manim concatena el nombre de la fuente para el hash
      del SVG y revienta con `TypeError`.
    - El mobject se queda con `_fig_pt` (puntos nominales) y `_fig_alto0` (su
      alto de tinta recien nacido). Con esos dos, `exigir_legible` mide el
      tamano EFECTIVO despues de cualquier `scale()` sin depender de que
      glifos tenga la cadena: "0" y "tiempo (s)" al mismo cuerpo tienen tinta
      muy distinta, y compararlas contra el mismo suelo daria falsos positivos.
    """
    fuente = kw.pop("fuente", tema()["fuente"])
    if fuente is not None:
        kw["font"] = fuente
    t = Text(str(cadena), font_size=font_size, **kw)
    if puntos is not None:
        t._fig_pt = float(puntos)
        t._fig_alto0 = alto(t)
    return t


def _k_tinta():
    """Alto de tinta de `_MUESTRA` por unidad de `font_size`, MEDIDO.

    Es lineal en `font_size` (lo comprueba la sonda), asi que basta medirlo una
    vez por proceso y por fuente del tema.
    """
    global _K_TINTA
    clave = (tema()["nombre"], tema()["fuente"])
    if _K_TINTA is None or _K_TINTA[0] != clave:
        _K_TINTA = (clave, alto(_texto_crudo(_MUESTRA, 100)) / 100.0)
    return _K_TINTA[1]


def alto_pt(mob):
    """Alto de TINTA de un mobject en puntos tipograficos de la figura impresa.

    No es una estimacion: es la altura real de lo que pinta en unidades de
    escena por los puntos que mide una unidad en el papel.
    """
    return alto(mob) * activa().puntos_por_unidad()


def fs_para_pt(puntos, muestra=None):
    """`font_size` cuyo alto de tinta es `puntos` puntos en la figura impresa.

    La referencia es "Hxdp" (ascendente a descendente), o sea la caja completa
    de una linea. Es fija: el mismo `puntos` da el mismo cuerpo para "0" y para
    "tiempo (s)".
    """
    if muestra is None:
        k = _k_tinta()
    else:
        k = alto(_texto_crudo(muestra, 100)) / 100.0
    return float(puntos) / (k * activa().puntos_por_unidad())


def texto(cadena, puntos=7.0, color_=None, mono=False, peso="MEDIUM"):
    """Texto de la figura con el tamano pedido EN PUNTOS impresos."""
    th = tema()
    fuente = th["fuente_mono"] if mono else th["fuente"]
    kw = {"color": color_ or th["tinta"], "fuente": fuente}
    if fuente is not None:
        kw["weight"] = peso
    return _texto_crudo(cadena, fs_para_pt(puntos), puntos=puntos, **kw)


def puntos_efectivos(t):
    """Puntos impresos con los que se pinta ESTE `Text`, ya escalado.

    Si lo construyo `texto()`, se sabe su cuerpo nominal y cuanto media al
    nacer: el cociente de alturas de tinta da el factor de cualquier `scale()`
    que le hayan aplicado (directamente o a traves de su grupo). Si lo
    construyo otro, se mide su linea de tinta: conservador, pero honesto.
    """
    a = alto(t)
    if a <= 1e-9:
        return None
    ref = getattr(t, "_fig_alto0", None)
    if ref and ref > 1e-9 and getattr(t, "_fig_pt", None):
        return float(t._fig_pt) * a / ref
    return a * activa().puntos_por_unidad()


def exigir_legible(mob, minimo_pt=PT_MINIMO, que="figura"):
    """Aborta si algun rotulo de `mob` se pinta por debajo del suelo.

    Tres formas de escribir mal este guardian, las tres medidas aqui:

    1. Filtrar con `t.has_points()`: un `Text` de manim NO tiene puntos propios
       (los glifos son sus hijos) y el guardian queda muerto. Es el mismo fallo
       que estuvo medio curso vivo en `lienzo.py`.
    2. Medir GLIFO a glifo: manim parte cada contorno en un submobject, asi que
       el punto de la "i" o el hueco de un "0" se miden como rotulos aparte.
       Medido en `ejes_paper`: el glifo mas chico de unos ejes de 6 pt daba
       1.73 pt y el guardian abortaba unos ejes perfectamente legibles.
    3. Comparar la tinta del `Text` entero contra un suelo en puntos: "0" y
       "tiempo (s)" al MISMO cuerpo tienen tinta distinta (un digito no tiene
       descendente), asi que castiga a las etiquetas cortas.

    Lo que se mide aqui es el cuerpo EFECTIVO: el nominal por el factor de
    escala real. Devuelve el minimo medido, en puntos.
    """
    medidas = [(t, puntos_efectivos(t)) for t in _textos_de(mob)]
    medidas = [(t, p) for t, p in medidas if p is not None]
    if not medidas:
        return None
    peor_t, peor = min(medidas, key=lambda par: par[1])
    if peor < minimo_pt:
        raise LienzoIlegible(
            f"{que}: '{peor_t.text}' se pinta a {peor:.2f} pt, por debajo del "
            f"suelo de {minimo_pt:.2f} pt en un lienzo de "
            f"{activa().ancho_in:.2f} x {activa().alto_in:.2f} in")
    return peor


def _textos_de(mob):
    if isinstance(mob, Text):
        yield mob
        return
    for hijo in getattr(mob, "submobjects", []):
        yield from _textos_de(hijo)


# =============================================================================
# Fondo, marca y sello
# =============================================================================

def fondo(escena):
    """Pinta el fondo del tema en la escena. Devuelve la escena."""
    th = tema()
    config.background_color = th["fondo"]
    escena.camera.background_color = th["fondo"]
    return escena


def sellar_escenas(ns):
    """Marca las escenas de `ns` como «ya atendidas» por la marca del canal.

    ManimStudio anexa `code_brand.marcar_escenas(globals())` a todo script que
    no mencione `code_brand` (studio/backend/app/branding.py). Sin esto, una
    figura de paper saldria con la marca de agua ambar del canal encima.
    """
    from manim import Scene as _Scene
    modulo = ns.get("__name__")
    marcadas = []
    for obj in list(ns.values()):
        if (isinstance(obj, type) and issubclass(obj, _Scene)
                and obj.__module__ == modulo):
            obj._code_brand = True
            marcadas.append(obj.__name__)
    return marcadas


def _hoy():
    return datetime.date.today().isoformat()


def proveniencia(commit=None, semilla=None, extra=None, fecha=None):
    """Los campos del sello, ya resueltos contra el entorno."""
    if commit is None:
        commit = os.environ.get("MS_COMMIT") or ""
    commit = str(commit).strip() or "sin-commit"
    if commit != "sin-commit":
        commit = commit[:12]
    if semilla is None:
        semilla = os.environ.get("MS_SEMILLA")
    if fecha is None:
        fecha = os.environ.get("MS_FECHA") or _hoy()
    return {"commit": commit,
            "semilla": None if semilla in (None, "") else str(semilla),
            "fecha": str(fecha), "libreria": f"figura {VERSION}",
            "extra": None if not extra else str(extra)}


def texto_sello(commit=None, semilla=None, extra=None, fecha=None):
    """La cadena del sello, sin dibujar (la sonda la compara tal cual)."""
    p = proveniencia(commit, semilla, extra, fecha)
    campos = [f"commit {p['commit']}"]
    if p["semilla"] is not None:
        campos.append(f"semilla {p['semilla']}")
    campos += [p["fecha"], p["libreria"]]
    if p["extra"]:
        campos.append(p["extra"])
    return " | ".join(campos)


def sello(commit=None, semilla=None, extra=None, fecha=None, puntos=4.0,
          margen_pt=4.0):
    """Sello de proveniencia en gris chico, esquina inferior derecha.

    Lee `MS_COMMIT`, `MS_SEMILLA` y `MS_FECHA` del entorno cuando no se le
    pasan. Sin commit escribe `sin-commit`: la figura dice que no sabe de que
    arbol salio, en vez de callarselo. Sin `MS_FECHA` pone la fecha de HOY, que
    es la del render; una tuberia reproducible fija `MS_FECHA`.
    """
    th = tema()
    cadena = texto_sello(commit, semilla, extra, fecha)
    puntos = max(float(puntos), PT_MINIMO_SELLO)
    t = _texto_crudo(cadena, fs_para_pt(puntos), puntos=puntos,
                     color=th["sello"], fuente=th["fuente_mono"])
    fig = activa()
    m = margen_pt / fig.puntos_por_unidad()
    poner(t, [fig.frame_width / 2 - m, -fig.frame_height / 2 + m, 0.0],
          anclaje=DER + ABJ)
    t.set_z_index(500)
    return t


# =============================================================================
# Datos: entran, no se transcriben
# =============================================================================

def datos_dir():
    """Directorio de datos de la figura (`MS_DATOS_DIR`, si no `datos/`)."""
    return Path(os.environ.get("MS_DATOS_DIR", "datos"))


def ruta_datos(nombre):
    d = datos_dir()
    p = d / nombre
    if not p.is_file():
        disponibles = (sorted(x.name for x in d.iterdir())[:12]
                       if d.is_dir() else [])
        raise DatosNoEncontrados(
            f"figura: no encuentro '{nombre}'. Busque en "
            f"'{d.resolve() if d.exists() else d}' (MS_DATOS_DIR="
            f"{os.environ.get('MS_DATOS_DIR', '<sin fijar; por defecto datos/>')}"
            f", cwd={Path.cwd()})."
            + (f" Ahi hay: {', '.join(disponibles)}" if disponibles
               else " Ese directorio no existe o esta vacio."))
    return p


def leer_csv(nombre, numericas=None):
    """CSV con cabecera -> {columna: np.ndarray | list[str]}.

    Una columna pasa a numpy float si TODOS sus valores no vacios se leen como
    numero; si no, se queda como lista de cadenas. Los vacios de una columna
    numerica salen como `nan`, que es lo que son: un hueco, no un cero.
    """
    p = ruta_datos(nombre)
    with open(p, newline="", encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    if not filas:
        raise ValueError(f"figura: '{p}' no tiene filas")
    salida = {}
    for c in list(filas[0].keys()):
        crudo = [(f.get(c) or "").strip() for f in filas]
        pedida = numericas is None or c in numericas
        if pedida and _todo_numerico(crudo):
            salida[c] = np.array([float(v) if v else np.nan for v in crudo])
        else:
            salida[c] = crudo
    return salida


def _todo_numerico(valores):
    hubo = False
    for v in valores:
        if not v:
            continue
        try:
            float(v)
            hubo = True
        except ValueError:
            return False
    return hubo


def leer_jsonl(nombre):
    """JSONL -> lista de dicts. Una linea rota dice QUE linea es."""
    p = ruta_datos(nombre)
    salida = []
    with open(p, encoding="utf-8") as fh:
        for i, linea in enumerate(fh, 1):
            linea = linea.strip()
            if not linea:
                continue
            try:
                salida.append(json.loads(linea))
            except json.JSONDecodeError as e:
                raise ValueError(f"figura: '{p}' linea {i} no es JSON: {e}")
    if not salida:
        raise ValueError(f"figura: '{p}' no tiene ninguna linea util")
    return salida


# =============================================================================
# Ejes
# =============================================================================

def _paso_bonito(span, objetivo=5):
    """Paso de marcas «redondo» (1, 2, 2.5 o 5 por decada) para `objetivo`."""
    if span <= 0:
        return 1.0
    crudo = span / max(objetivo, 1)
    decada = 10.0 ** np.floor(np.log10(crudo))
    for m in (1.0, 2.0, 2.5, 5.0, 10.0):
        if crudo <= m * decada:
            return float(m * decada)
    return float(10.0 * decada)


def _marcas(rango, paso):
    lo, hi = float(rango[0]), float(rango[1])
    n0 = int(np.ceil(lo / paso - 1e-9))
    n1 = int(np.floor(hi / paso + 1e-9))
    return [round(n * paso, 10) for n in range(n0, n1 + 1)]


def _fmt(v, paso):
    dec = max(0, int(-np.floor(np.log10(paso)))) if paso < 1 else 0
    s = f"{v:.{dec}f}"
    return "0" if float(s) == 0.0 else s


def ejes_paper(x_rango, y_rango, xlabel="", ylabel="", ancho_=None, alto_=None,
               pasos=None, puntos_marca=6.0, puntos_titulo=7.0, rejilla=True,
               decimales=None, cero=True):
    """Ejes de figura con marcas numeradas y titulos, medidos en puntos.

    El marco se dibuja A MANO en el BORDE del cuadro (izquierda y abajo), no
    con los ejes de `Axes`. Motivo medido: `Axes` cruza por el origen y, cuando
    el rango no lo contiene, `Axes._origin_shift` pega el eje al borde que le
    toque — para un rango de fase de -190 a -85 el eje X sale ARRIBA, con sus
    numeros encima de la curva. Aqui el eje siempre esta abajo y a la
    izquierda, y el cero (si cae dentro) se dibuja como una raya de referencia
    aparte, para no confundir «el suelo del cuadro» con «el cero».

    Devuelve el `Axes` (que solo se usa como sistema de coordenadas, con sus
    propios ejes apagados) con `.marco`, `.marcas_x`, `.marcas_y`, `.rejilla`,
    `.linea_cero`, `.rotulo_x`, `.rotulo_y` colgados y anadidos.
    """
    fig = activa()
    th = tema()
    ppu = fig.puntos_por_unidad()
    ancho_util, alto_util = fig.zona(margen_pt=5.0)
    # Aire reservado para lo que vive FUERA del area de dibujo: a la izquierda
    # los numeros del eje Y y su titulo; abajo, los del eje X y el suyo.
    aire_izq = (puntos_titulo + puntos_marca * 3.2) / ppu
    aire_abajo = (puntos_titulo + puntos_marca * 2.4) / ppu
    an = float(ancho_) if ancho_ else max(0.6, ancho_util - aire_izq)
    al = float(alto_) if alto_ else max(0.4, alto_util - aire_abajo)

    x0, x1 = float(x_rango[0]), float(x_rango[1])
    y0, y1 = float(y_rango[0]), float(y_rango[1])
    if x1 <= x0 or y1 <= y0:
        raise ValueError(f"ejes_paper: rango vacio x={x_rango} y={y_rango}")
    px = float(pasos[0]) if pasos else _paso_bonito(x1 - x0, 5)
    py = float(pasos[1]) if pasos else _paso_bonito(y1 - y0, 4)
    marcas_x, marcas_y = _marcas((x0, x1), px), _marcas((y0, y1), py)

    ax = Axes(x_range=[x0, x1, px], y_range=[y0, y1, py],
              x_length=an, y_length=al, tips=False,
              axis_config={"stroke_opacity": 0.0, "include_ticks": False,
                           "include_numbers": False})

    largo_tick = 2.6 / ppu
    hueco = 2.0 / ppu
    ax.marco = VGroup(
        Line(ax.c2p(x0, y0), ax.c2p(x1, y0), stroke_width=1.3, color=th["eje"]),
        Line(ax.c2p(x0, y0), ax.c2p(x0, y1), stroke_width=1.3, color=th["eje"]))

    ax.marcas_x, ax.marcas_y = VGroup(), VGroup()
    for v in marcas_x:
        p = ax.c2p(v, y0)
        ax.marco.add(Line(p, p + ABJ * largo_tick, stroke_width=1.0,
                          color=th["eje"]))
        et = texto(_fmt(v, px) if decimales is None else
                   f"{v:.{int(decimales[0])}f}", puntos_marca, th["apagado"])
        ax.marcas_x.add(pegar(et, p + ABJ * largo_tick, ABJ, hueco))
    for v in marcas_y:
        p = ax.c2p(x0, v)
        ax.marco.add(Line(p, p + IZQ * largo_tick, stroke_width=1.0,
                          color=th["eje"]))
        et = texto(_fmt(v, py) if decimales is None else
                   f"{v:.{int(decimales[1])}f}", puntos_marca, th["apagado"])
        ax.marcas_y.add(pegar(et, p + IZQ * largo_tick, IZQ, hueco))

    ax.rejilla = VGroup()
    if rejilla:
        for v in marcas_y:
            ax.rejilla.add(Line(ax.c2p(x0, v), ax.c2p(x1, v),
                                stroke_width=0.6, color=th["rejilla"]))
        for v in marcas_x:
            ax.rejilla.add(Line(ax.c2p(v, y0), ax.c2p(v, y1),
                                stroke_width=0.6, color=th["rejilla"]))
        ax.rejilla.set_z_index(-10)

    # El suelo del cuadro NO es el cero salvo que el rango empiece en cero.
    ax.linea_cero = VGroup()
    if cero and y0 < 0.0 < y1:
        ax.linea_cero.add(DashedLine(ax.c2p(x0, 0.0), ax.c2p(x1, 0.0),
                                     stroke_width=0.9, color=th["apagado"],
                                     dash_length=0.05))

    ax.rotulo_x, ax.rotulo_y = VGroup(), VGroup()
    if xlabel:
        ax.rotulo_x = texto(xlabel, puntos_titulo, th["tinta"])
        pegar(ax.rotulo_x, ax.marcas_x, ABJ, 2.2 / ppu)
        poner(ax.rotulo_x,
              [ax.c2p((x0 + x1) / 2, y0)[0], centro(ax.rotulo_x)[1], 0.0])
    if ylabel:
        ax.rotulo_y = texto(ylabel, puntos_titulo, th["tinta"]).rotate(np.pi / 2)
        pegar(ax.rotulo_y, ax.marcas_y, IZQ, 2.2 / ppu)
        poner(ax.rotulo_y,
              [centro(ax.rotulo_y)[0], ax.c2p(x0, (y0 + y1) / 2)[1], 0.0])

    ax.add(ax.rejilla, ax.marco, ax.marcas_x, ax.marcas_y, ax.linea_cero,
           ax.rotulo_x, ax.rotulo_y)
    ax.zona_pt = min([puntos_efectivos(t) for t in
                      list(ax.marcas_x) + list(ax.marcas_y)] or [np.inf])
    return ax


# =============================================================================
# Trazos
# =============================================================================

def _tramos_dentro(ax, x, y):
    """Trozos contiguos de (x, y) que caben en el rango del eje.

    Recortar DESPUES (`np.clip`) dibuja un segmento horizontal pegado al borde
    que se lee como saturacion: lo contrario de lo que pasa. Aqui lo que sale
    del cuadro PARTE la curva, y el hueco se ve como hueco.
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.shape != y.shape:
        raise ValueError(f"figura: x tiene {x.shape} y y tiene {y.shape}")
    dentro = ((x >= ax.x_range[0]) & (x <= ax.x_range[1])
              & (y >= ax.y_range[0]) & (y <= ax.y_range[1])
              & np.isfinite(x) & np.isfinite(y))
    tramos, actual = [], []
    for i, ok in enumerate(dentro):
        if ok:
            actual.append(i)
        elif actual:
            tramos.append(np.array(actual))
            actual = []
    if actual:
        tramos.append(np.array(actual))
    return x, y, tramos


def curva(ax, x, y, color_=None, grosor=1.6, punteada=False, opacidad=1.0):
    """Polilinea de (x, y) sobre `ax`, recortada al cuadro POR TRAMOS."""
    col = color_ or tema()["series"][0]
    x, y, tramos = _tramos_dentro(ax, x, y)
    grupo = VGroup()
    for idx in tramos:
        if len(idx) < 2:
            continue
        v = VMobject()
        v.set_points_as_corners([ax.c2p(float(x[i]), float(y[i]))
                                 for i in idx])
        # `set_opacity` encenderia tambien el RELLENO y la curva se volveria
        # una mancha maciza. Se toca el trazo.
        v.set_stroke(color=col, width=grosor, opacity=opacidad)
        v.set_fill(opacity=0.0)
        if punteada:
            from manim import DashedVMobject
            v = DashedVMobject(v, num_dashes=max(12, len(idx) // 4))
            v.set_stroke(color=col, width=grosor, opacity=opacidad)
        grupo.add(v)
    grupo.color_serie = col
    return grupo


def serie_tiempo(ax, t, y, color_=None, grosor=1.6, marcadores=None,
                 radio_pt=1.6, color_marcador=None):
    """Serie temporal + puntos destacados sobre la propia curva.

    `marcadores` son indices enteros o instantes: los momentos en los que la
    serie dice algo (perdida total, salto). Van SOBRE la curva, no sobre el
    eje: en el eje se leerian como otra serie.
    """
    col = color_ or tema()["series"][0]
    grupo = VGroup(curva(ax, t, y, col, grosor))
    t = np.asarray(t, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if marcadores is not None and len(marcadores):
        r = radio_pt / activa().puntos_por_unidad()
        puntos = VGroup()
        for m in marcadores:
            i = int(m) if (float(m) == int(m) and 0 <= int(m) < len(t)) \
                else int(np.argmin(np.abs(t - float(m))))
            puntos.add(Dot(ax.c2p(float(t[i]), float(y[i])), radius=r,
                           color=color_marcador or tema()["down"]))
        grupo.add(puntos)
        grupo.marcadores = puntos
    return grupo


def banda_ic(ax, x, lo, hi, color_=None, opacidad=0.22):
    """Banda sombreada entre `lo` y `hi` (el IC95 % de una serie).

    Relleno sin trazo: con `set_opacity` se encenderia tambien el borde y la
    banda competiria con la curva que envuelve.
    """
    col = color_ or tema()["series"][0]
    x = np.asarray(x, dtype=np.float64)
    lo = np.clip(np.asarray(lo, dtype=np.float64), ax.y_range[0], ax.y_range[1])
    hi = np.clip(np.asarray(hi, dtype=np.float64), ax.y_range[0], ax.y_range[1])
    dentro = (x >= ax.x_range[0]) & (x <= ax.x_range[1])
    x, lo, hi = x[dentro], lo[dentro], hi[dentro]
    if len(x) < 2:
        raise ValueError("banda_ic: hacen falta al menos 2 puntos dentro del "
                         "rango del eje")
    contorno = ([ax.c2p(float(a), float(b)) for a, b in zip(x, lo)]
                + [ax.c2p(float(a), float(b))
                   for a, b in zip(x[::-1], hi[::-1])])
    p = Polygon(*contorno, stroke_width=0)
    p.set_fill(color=col, opacity=opacidad)
    p.set_stroke(opacity=0.0)
    p.set_z_index(-5)
    return p


def cdf(ax, muestras, color_=None, grosor=1.8, con_puntos=True, radio_pt=1.4):
    """CDF empirica de `muestras` como escalera.

    Devuelve el VGroup con `.x` y `.f` colgados: quien rotule un percentil lo
    toma de ahi en vez de volver a calcularlo con otro criterio.
    """
    col = color_ or tema()["series"][0]
    m = np.sort(np.asarray(muestras, dtype=np.float64))
    m = m[np.isfinite(m)]
    if m.size == 0:
        raise ValueError("cdf: no hay ninguna muestra finita")
    f = np.arange(1, m.size + 1) / m.size
    xs, fs = [float(m[0])], [0.0]
    for xi, fi in zip(m, f):
        xs += [float(xi), float(xi)]
        fs += [fs[-1], float(fi)]
    xs.append(float(ax.x_range[1]))
    fs.append(fs[-1])
    grupo = VGroup(curva(ax, xs, fs, col, grosor))
    if con_puntos:
        r = radio_pt / activa().puntos_por_unidad()
        grupo.add(VGroup(*[Dot(ax.c2p(float(xi), float(fi)), radius=r,
                               color=col)
                           for xi, fi in zip(m, f)
                           if ax.x_range[0] <= xi <= ax.x_range[1]]))
    grupo.x, grupo.f = m, f
    return grupo


def percentil(muestras, p):
    """Percentil empirico con el MISMO criterio que dibuja `cdf`: el escalon."""
    m = np.sort(np.asarray(muestras, dtype=np.float64))
    m = m[np.isfinite(m)]
    if m.size == 0:
        raise ValueError("percentil: no hay muestras")
    f = np.arange(1, m.size + 1) / m.size
    i = int(np.searchsorted(f, float(p) / 100.0, side="left"))
    return float(m[min(i, m.size - 1)])


# =============================================================================
# Gantt de disponibilidad
# =============================================================================

ESTADOS = ("up", "down", "hueco")


def gantt(filas, t_rango=None, eventos=None, ancho_=None, alto_fila_pt=9.0,
          puntos_fila=6.0, puntos_evento=5.0, xlabel="tiempo (s)",
          puntos_marca=6.0):
    """Gantt de disponibilidad: `filas = [(nombre, [(t0, t1, estado)]), ...]`.

    `estado` es "up", "down" o "hueco" (sin evidencia). Cada fila lleva SIEMPRE
    una banda de fondo "hueco" a lo largo de la ventana: lo que no se midio se
    ve como no medido, no como continuidad.

    `eventos = [(t, etiqueta)]` o `[(t, etiqueta, color)]` dibuja una vertical
    punteada por evento, con su rotulo arriba.

    Devuelve un VGroup con `.x(t)`, `.marco`, `.barras`, `.nombres`,
    `.eventos` y `.t_rango`.
    """
    fig, th = activa(), tema()
    filas = list(filas)
    if not filas:
        raise ValueError("gantt: no hay ninguna fila")
    tramos_todos = [tr for _, trs in filas for tr in trs]
    if t_rango is None:
        if not tramos_todos:
            raise ValueError("gantt: sin tramos no se deduce la ventana")
        t0 = min(float(a) for a, _, _ in tramos_todos)
        t1 = max(float(b) for _, b, _ in tramos_todos)
        for e in (eventos or []):
            t0, t1 = min(t0, float(e[0])), max(t1, float(e[0]))
    else:
        t0, t1 = float(t_rango[0]), float(t_rango[1])
    if t1 <= t0:
        raise ValueError(f"gantt: ventana vacia ({t0} .. {t1})")

    ppu = fig.puntos_por_unidad()
    alto_fila = alto_fila_pt / ppu
    paso_fila = alto_fila * 1.55
    ancho_util, _ = fig.zona(margen_pt=5.0)
    nombres = VGroup(*[texto(n, puntos_fila, th["tinta"]) for n, _ in filas])
    ancho_nombres = max(ancho(n) for n in nombres)
    hueco = 3.0 / ppu
    an = float(ancho_) if ancho_ else max(0.5, ancho_util - ancho_nombres
                                          - hueco)

    def x(t):
        return (float(t) - t0) / (t1 - t0) * an

    barras = VGroup()
    for i, (nombre, tramos) in enumerate(filas):
        y = -i * paso_fila
        base = Rectangle(width=an, height=alto_fila, stroke_width=0)
        base.set_fill(color=th["hueco"], opacity=0.45)
        base.move_to([an / 2, y, 0])
        barras.add(base)
        for a, b, estado in tramos:
            if estado not in ESTADOS:
                raise ValueError(f"gantt: estado {estado!r} desconocido "
                                 f"(hay {ESTADOS})")
            a, b = max(float(a), t0), min(float(b), t1)
            if b <= a:
                continue
            r = Rectangle(width=x(b) - x(a), height=alto_fila, stroke_width=0)
            r.set_fill(color=th[estado], opacity=1.0)
            r.move_to([(x(a) + x(b)) / 2, y, 0])
            barras.add(r)
        pegar(nombres[i], np.array([0.0, y, 0.0]), IZQ, hueco)

    y_min = -(len(filas) - 1) * paso_fila - alto_fila / 2
    y_max = alto_fila / 2
    largo_tick = 2.6 / ppu
    marco = VGroup(Line([0, y_min, 0], [an, y_min, 0], stroke_width=1.2,
                        color=th["eje"]))
    paso = _paso_bonito(t1 - t0, 5)
    marcas = VGroup()
    for v in _marcas((t0, t1), paso):
        p = np.array([x(v), y_min, 0.0])
        marco.add(Line(p, p + ABJ * largo_tick, stroke_width=1.0,
                       color=th["eje"]))
        marcas.add(pegar(texto(_fmt(v, paso), puntos_marca, th["apagado"]),
                         p + ABJ * largo_tick, ABJ, 2.0 / ppu))

    grupo = VGroup(barras, nombres, marco, marcas)
    if xlabel:
        tx = texto(xlabel, puntos_fila + 1.0, th["tinta"])
        pegar(tx, marcas, ABJ, 2.2 / ppu)
        poner(tx, [an / 2, centro(tx)[1], 0.0])
        grupo.add(tx)

    # Los rotulos de evento se reparten en NIVELES. Tres eventos a 52, 58 y 63
    # segundos de una ventana de 120 dibujaban sus tres etiquetas centradas en
    # la misma linea: "kill satellite", "policy pada" y "recuperado" salieron
    # encimadas y no se leia ninguna. Cada etiqueta se coloca en el primer
    # nivel donde no toca a la anterior, y su linea punteada sube hasta ahi.
    evs = VGroup()
    ocupado = []          # x derecha ya ocupada por nivel
    hueco_ev = 2.0 / ppu
    for e in sorted((e for e in (eventos or []) if t0 <= float(e[0]) <= t1),
                    key=lambda e: float(e[0])):
        t, etiqueta = float(e[0]), str(e[1])
        col = e[2] if len(e) > 2 else th["series"][1]
        et = texto(etiqueta, puntos_evento, col)
        medio = ancho(et) / 2.0
        # El rotulo se queda dentro del cuadro aunque el evento este al borde.
        cx = min(max(x(t), medio), max(an - medio, medio))
        nivel = next((i for i, borde_x in enumerate(ocupado)
                      if borde_x + hueco_ev <= cx - medio), len(ocupado))
        if nivel == len(ocupado):
            ocupado.append(-np.inf)
        ocupado[nivel] = cx + medio
        alto_ev = alto(et) * 1.7
        y_et = y_max + 0.06 + nivel * alto_ev
        evs.add(DashedLine([x(t), y_min, 0], [x(t), y_et, 0],
                           stroke_width=1.0, color=col, dash_length=0.035))
        poner(et, [cx, y_et + 1.5 / ppu, 0.0], anclaje=ABJ)
        evs.add(et)
    if len(evs):
        grupo.add(evs)

    grupo.x = x
    grupo.t_rango = (t0, t1)
    grupo.marco = marco
    grupo.barras = barras
    grupo.nombres = nombres
    grupo.eventos = evs
    grupo.ancho_util = an
    return grupo


def tramos_de_jsonl(registros, clave_fila="fila", clave_t0="t0",
                    clave_t1="t1", clave_estado="estado"):
    """Registros JSONL -> `filas` de `gantt`, en el orden de aparicion."""
    orden, acc = [], {}
    for r in registros:
        if clave_fila not in r:
            continue
        nombre = str(r[clave_fila])
        if nombre not in acc:
            orden.append(nombre)
            acc[nombre] = []
        acc[nombre].append((float(r[clave_t0]), float(r[clave_t1]),
                            str(r.get(clave_estado, "up"))))
    return [(n, acc[n]) for n in orden]


# =============================================================================
# Leyenda y composicion
# =============================================================================

def leyenda(entradas, puntos=6.0, columnas=1, hueco_pt=5.0, tipo="linea"):
    """Leyenda: `entradas = [(etiqueta, color)]` o `[(etiqueta, color, tipo)]`.

    `tipo` es "linea", "banda" (translucida, para un IC), "bloque" (maciza,
    para una barra) o "punto".
    """
    th = tema()
    ppu = activa().puntos_por_unidad()
    hueco = hueco_pt / ppu
    largo = 9.0 / ppu
    items = []
    for e in entradas:
        etiqueta, col = str(e[0]), e[1]
        clase = e[2] if len(e) > 2 else tipo
        if clase in ("banda", "bloque"):
            # "banda" es el sombreado de un IC (translucido, como se dibuja);
            # "bloque" es una barra maciza. Si una barra opaca del Gantt se
            # anuncia con un cuadro al 35 %, la leyenda ensena OTRO color que
            # el dibujo, que es la manera fina de mentir en una figura.
            marca = Rectangle(width=largo, height=largo * 0.42, stroke_width=0)
            marca.set_fill(color=col, opacity=0.35 if clase == "banda" else 1.0)
        elif clase == "punto":
            marca = Dot(radius=largo * 0.16, color=col)
        else:
            marca = Line([0, 0, 0], [largo, 0, 0], stroke_width=1.8, color=col)
        t = texto(etiqueta, puntos, th["tinta"])
        pegar(t, marca, DER, hueco * 0.45)
        items.append(VGroup(marca, t))
    filas = int(np.ceil(len(items) / max(1, int(columnas))))
    ancho_col = max(ancho(i) for i in items) + hueco
    alto_fila = max(alto(i) for i in items) * 1.9
    for i, it in enumerate(items):
        poner(it, [(i // filas) * ancho_col, -(i % filas) * alto_fila, 0.0],
              anclaje=IZQ)
    return VGroup(*items)


def encajar(mob, margen_pt=5.0, minimo_pt=PT_MINIMO, que="figura",
            reservar_abajo_pt=0.0, reservar_arriba_pt=0.0):
    """Escala `mob` para que quepa en el lienzo y COMPRUEBA que sigue legible.

    Escalar un grupo encoge tambien la letra: por eso el guardian va DESPUES
    del encaje, no antes.

    `reservar_abajo_pt` deja una franja libre en el pie para el sello (sin
    ella el titulo del eje X y el sello acaban a dos puntos uno de otro, y en
    el PNG impreso se leen como una sola linea) y `reservar_arriba_pt` hace lo
    mismo con el titulo de un clip de video.
    """
    fig = activa()
    an, al = fig.zona(margen_pt)
    ppu = fig.puntos_por_unidad()
    abajo = float(reservar_abajo_pt) / ppu
    arriba = float(reservar_arriba_pt) / ppu
    al -= abajo + arriba
    k = min(an / max(ancho(mob), 1e-9), al / max(alto(mob), 1e-9), 1.0)
    if k < 1.0:
        mob.scale(k)
    poner(mob, [0.0, (abajo - arriba) / 2.0, 0.0])
    exigir_legible(mob, minimo_pt, que)
    return mob


def exigir_dentro(mob, margen_pt=4.0, que="pieza"):
    """Aborta si `mob` se sale del lienzo. Devuelve `mob`.

    El render NO avisa de esto: un titulo mas ancho que el cuadro sale cortado
    por los dos lados y el mp4 se genera igual. Medido en la demo del pase
    LEO: "PASE LEO-600 SOBRE UNA ESTACION" a 15 pt mide 14.9 unidades en un
    frame de 14.23 y se publico con las dos primeras letras fuera.
    """
    fig = activa()
    m = float(margen_pt) / fig.puntos_por_unidad()
    c = caja(mob)
    if c is None:
        return mob
    lim_x, lim_y = fig.frame_width / 2 - m, fig.frame_height / 2 - m
    fuera = [n for n, v in (("izquierda", -lim_x - c[0][0]),
                            ("derecha", c[1][0] - lim_x),
                            ("abajo", -lim_y - c[0][1]),
                            ("arriba", c[1][1] - lim_y)) if v > 1e-6]
    if fuera:
        # Se comprueba la CAJA COLOCADA, no solo el tamano: un bloque de 11
        # unidades cabe de sobra en un frame de 14.23 y aun asi se sale por la
        # izquierda si se ancla a la derecha del cuadro de unos ejes. Medido en
        # la demo del pase LEO: las cifras cabian y salian cortadas igual.
        raise FueraDelLienzo(
            f"{que} se sale por {', '.join(fuera)}: caja "
            f"[{c[0][0]:.2f}, {c[1][0]:.2f}] x [{c[0][1]:.2f}, {c[1][1]:.2f}] "
            f"contra un lienzo de +-{lim_x:.2f} x +-{lim_y:.2f}")
    return mob


def encoger_a_ancho(mob, ancho_max=None, margen_pt=4.0, minimo_pt=PT_MINIMO,
                    que="texto"):
    """Escala `mob` hasta que quepa a lo ancho y comprueba que sigue legible."""
    fig = activa()
    if ancho_max is None:
        ancho_max, _ = fig.zona(margen_pt)
    a = ancho(mob)
    if a > ancho_max > 0:
        mob.scale(ancho_max / a)
    exigir_legible(mob, minimo_pt, que)
    return mob


def titulo(cadena, puntos=8.0, arriba_pt=4.0, margen_pt=4.0, minimo_pt=None):
    """Titulo de la figura, arriba, centrado y encogido si no cabe."""
    fig = activa()
    t = texto(cadena, puntos, tema()["tinta"], peso="SEMIBOLD")
    encoger_a_ancho(t, margen_pt=margen_pt,
                    minimo_pt=minimo_pt if minimo_pt is not None
                    else min(PT_MINIMO, puntos), que=f"titulo '{cadena}'")
    poner(t, [0.0, fig.frame_height / 2 - arriba_pt / fig.puntos_por_unidad(),
              0.0], anclaje=ARR)
    return t

"""Transiciones de escena para encadenar "diapositivas" dentro de una Scene.

Manim no trae transiciones entre bloques de contenido: lo unico que hay es
`FadeOut(viejo)` + `FadeIn(nuevo)`, que en un video educativo produce el mismo
parpadeo cincuenta veces. Estas diez cubren lo que la coleccion necesita, y
todas comparten el mismo contrato:

    reciben el grupo SALIENTE y el ENTRANTE y devuelven UNA animacion para
    self.play(...); el entrante no necesita estar anadido a la escena (la
    animacion lo anade).

Uso:
    from transiciones import transicion, TRANSICIONES

    self.play(transicion("barrido", bloque1, bloque2))
    self.play(transicion_deslizar(bloque2, bloque3, direccion=LEFT))

`TRANSICIONES` es el catalogo: nombre -> funcion. La demo
`animations/experimentacion/29-transiciones.py` las enseña las diez.

Cuando usar cual:
    deslizar / empujar   dos momentos del MISMO tema (la idea sigue)
    zoom                 entrar en un detalle, o salir a la vista general
    barrido              cambio de seccion (la banda ambar es la marca)
    fundido_negro        cambio de tema; el respiro mas fuerte que hay
    persiana / rejilla   cambio con textura, cuando el corte seco cansa
    difuminar            el contenido se "deshace" (ruido, perdida, olvido)
    conmutar             el saliente y el entrante son EL MISMO objeto en
                         otro estado (Transform de verdad, no dos fundidos)

Nota de duracion: casi todas devuelven una animacion sin `run_time` propio, asi
que manda el de `self.play(...)` (1 s por defecto). Las que si lo fijan por
dentro —persiana, barrido, rejilla, fundido_negro— lo dicen en su firma.
"""

from manim import (AnimationGroup, Create, FadeIn, FadeOut, Rectangle,
                   Succession, Transform, Uncreate, VGroup, config,
                   BLACK, LEFT, ORIGIN, RIGHT, UP)

# La marca da los colores: la banda del barrido es ambar y el respiro del
# fundido es el fondo del canal, no un negro cualquiera. Si code_brand no
# esta montado (uso de la libreria fuera del contenedor), se cae a valores
# equivalentes en vez de reventar el import.
try:
    from code_brand import CODE_ACCENT, CODE_BG
except ImportError:  # pragma: no cover - solo fuera del contenedor
    CODE_ACCENT, CODE_BG = "#f59e0b", "#05070a"


def _lienzo(color, opacidad=1.0):
    """Rectangulo que tapa el cuadro entero, por encima de todo."""
    r = Rectangle(width=config.frame_width + 0.4,
                  height=config.frame_height + 0.4,
                  fill_color=color, fill_opacity=opacidad, stroke_width=0)
    r.set_z_index(50)
    return r


# ── las que mueven el contenido ───────────────────────────────────────────────

def transicion_deslizar(saliente, entrante, direccion=LEFT, distancia=1.6,
                        solape=0.15):
    """El contenido viejo sale empujado y el nuevo entra desde el lado
    opuesto, con un pequeno solape temporal."""
    return AnimationGroup(
        FadeOut(saliente, shift=direccion * distancia),
        FadeIn(entrante, shift=direccion * distancia),
        lag_ratio=solape,
    )


def transicion_empujar(saliente, entrante, direccion=LEFT):
    """Como deslizar, pero el nuevo EMPUJA al viejo: los dos recorren el
    cuadro entero y en ningun momento se ven encimados.

    Se nota mucho mas que `deslizar` (que solo insinua el movimiento) y es la
    que mejor lee cuando los dos bloques son del mismo tamano.
    """
    ancho = config.frame_width if abs(direccion[0]) > 0 else config.frame_height
    entrante.shift(-direccion * ancho)
    return AnimationGroup(
        saliente.animate.shift(direccion * ancho),
        entrante.animate.shift(direccion * ancho),
        lag_ratio=0,
    )


def transicion_zoom(saliente, entrante, factor=2.2):
    """El viejo 'atraviesa la camara' (crece y se funde) y el nuevo emerge
    desde el fondo (nace pequeno)."""
    return AnimationGroup(
        FadeOut(saliente, scale=factor),
        FadeIn(entrante, scale=1 / factor),
        lag_ratio=0.2,
    )


# ── las que tapan y destapan ──────────────────────────────────────────────────

def transicion_persiana(saliente, entrante, franjas=8, color=BLACK,
                        duracion_lado=0.6):
    """Franjas horizontales cubren la pantalla, el contenido se permuta
    detras, y las franjas se retiran (persiana veneciana)."""
    alto = config.frame_height / franjas
    tiras = []
    for i in range(franjas):
        y = config.frame_height / 2 - alto * (i + 0.5)
        tira = Rectangle(width=config.frame_width + 0.2, height=alto + 0.02,
                         fill_color=color, fill_opacity=1, stroke_width=0)
        tira.move_to([0, y, 0]).stretch(0.001, dim=1)
        tira.set_z_index(50)
        tiras.append(tira)

    cubrir = AnimationGroup(
        *[t.animate.stretch_to_fit_height(alto + 0.02) for t in tiras],
        lag_ratio=0.07, run_time=duracion_lado)
    permutar = AnimationGroup(FadeOut(saliente), FadeIn(entrante),
                              run_time=0.05)
    descubrir = AnimationGroup(
        *[t.animate.stretch(0.001, dim=1).set_opacity(0) for t in tiras],
        lag_ratio=0.07, run_time=duracion_lado)
    return Succession(cubrir, permutar, descubrir)


def transicion_barrido(saliente, entrante, color=None, direccion=RIGHT,
                       duracion_lado=0.45):
    """Una banda AMBAR cruza el cuadro y deja el contenido nuevo detras.

    Es la transicion de marca: el color es el acento del canal, asi que un
    cambio de seccion se reconoce sin leer nada. La banda entra por un lado,
    el contenido se permuta cuando tapa, y sale por el otro.
    """
    banda = _lienzo(color or CODE_ACCENT)
    ancho = config.frame_width + 0.4
    banda.move_to(-direccion * ancho)
    # Destinos ABSOLUTOS (`move_to`), no relativos (`shift`): `.animate` copia
    # el mobject en el momento en que se construye la animacion, y las tres se
    # construyen antes de que se reproduzca ninguna. Con `shift`, el `salir`
    # se calcularia desde la posicion INICIAL y la banda se quedaria en el
    # centro tapando la escena.
    entrar = banda.animate.move_to(ORIGIN)
    permutar = AnimationGroup(FadeOut(saliente), FadeIn(entrante),
                              run_time=0.05)
    salir = banda.animate.move_to(direccion * ancho)
    # El FadeOut final saca la banda de la escena: dejarla fuera de cuadro
    # la mantiene viva y cada transicion sumaria un mobject mas.
    return Succession(entrar, permutar, salir, FadeOut(banda, run_time=0.01),
                      run_time=duracion_lado * 2)


def transicion_fundido_negro(saliente, entrante, color=None,
                             duracion_lado=0.4):
    """Todo se va al fondo del canal y vuelve con el contenido nuevo.

    El respiro mas fuerte del repertorio: usa esta cuando cambia el TEMA, no
    cuando cambia el ejemplo. El color por defecto es `CODE_BG`, no BLACK: el
    fondo del canal es #05070a y un negro puro se ve como un parpadeo.
    """
    velo = _lienzo(color or CODE_BG, opacidad=0)
    cubrir = velo.animate.set_opacity(1)
    permutar = AnimationGroup(FadeOut(saliente), FadeIn(entrante),
                              run_time=0.05)
    descubrir = velo.animate.set_opacity(0)
    return Succession(cubrir, permutar, descubrir,
                      FadeOut(velo, run_time=0.01),
                      run_time=duracion_lado * 2)


def transicion_rejilla(saliente, entrante, columnas=8, filas=5, color=None,
                       duracion_lado=0.5):
    """Una rejilla de celdas se cierra en diagonal, permuta y se abre.

    La persiana en dos dimensiones: el `lag_ratio` recorre las celdas por
    diagonales (de arriba-izquierda a abajo-derecha), que es lo que le da el
    aire de pantalla de control.
    """
    ancho = config.frame_width / columnas
    alto = config.frame_height / filas
    celdas = []
    for f in range(filas):
        for c in range(columnas):
            x = -config.frame_width / 2 + ancho * (c + 0.5)
            y = config.frame_height / 2 - alto * (f + 0.5)
            celda = Rectangle(width=ancho, height=alto,
                              fill_color=color or CODE_BG, fill_opacity=1,
                              stroke_width=0)
            celda.move_to([x, y, 0]).scale(0.001)
            celda.set_z_index(50)
            # El orden de la lista ES el orden del lag: por diagonales.
            celdas.append((f + c, celda))
    celdas.sort(key=lambda par: par[0])
    orden = [c for _, c in celdas]

    # Tamanos ABSOLUTOS por la misma razon que en `barrido`: con `scale(1000)`
    # y `scale(0.001)` la segunda animacion partiria del tamano original y no
    # del que dejo la primera.
    cubrir = AnimationGroup(*[c.animate.scale_to_fit_height(alto) for c in orden],
                            lag_ratio=0.02, run_time=duracion_lado)
    permutar = AnimationGroup(FadeOut(saliente), FadeIn(entrante),
                              run_time=0.05)
    descubrir = AnimationGroup(
        *[c.animate.scale_to_fit_height(alto * 0.001) for c in orden],
        lag_ratio=0.02, run_time=duracion_lado)
    return Succession(cubrir, permutar, descubrir,
                      FadeOut(VGroup(*orden), run_time=0.01))


# ── las que trabajan sobre el contenido mismo ─────────────────────────────────

def transicion_difuminar(saliente, entrante, dispersion=0.9):
    """El viejo se deshace hacia arriba y el nuevo se recompone desde abajo.

    Para cuando lo que se cuenta ES una perdida o una recomposicion (ruido que
    borra una senal, memoria que se olvida). En un cambio de tema normal
    resulta demasiado: usa `fundido_negro`.
    """
    return AnimationGroup(
        FadeOut(saliente, shift=UP * dispersion, scale=1.15),
        FadeIn(entrante, shift=UP * dispersion, scale=0.85),
        lag_ratio=0.35,
    )


def transicion_conmutar(saliente, entrante):
    """`Transform` de verdad: UN objeto que pasa a otro estado.

    No son dos fundidos. Usala cuando el entrante es el saliente en otra
    forma (la misma curva con otro parametro, el mismo diagrama con otra
    etiqueta): dos `FadeIn`/`FadeOut` solapados dejan DOS cosas en pantalla
    medio segundo, justo el que se usa para mirar.
    """
    return Transform(saliente, entrante)


def transicion_trazar(saliente, entrante, solape=0.4):
    """El viejo se destraza (`Uncreate`) y el nuevo se traza (`Create`).

    La unica que respeta el gesto de dibujo: para diagramas y ejes, donde ver
    aparecer el trazo cuenta algo. En texto queda mal — ahi usa `deslizar`.
    """
    return AnimationGroup(Uncreate(saliente), Create(entrante),
                          lag_ratio=solape)


# ── catalogo ──────────────────────────────────────────────────────────────────

TRANSICIONES = {
    "deslizar": transicion_deslizar,
    "empujar": transicion_empujar,
    "zoom": transicion_zoom,
    "persiana": transicion_persiana,
    "barrido": transicion_barrido,
    "fundido_negro": transicion_fundido_negro,
    "rejilla": transicion_rejilla,
    "difuminar": transicion_difuminar,
    "conmutar": transicion_conmutar,
    "trazar": transicion_trazar,
}

# Una linea por transicion: lo que la interfaz y el asistente enseñan sin
# tener que leer el codigo.
DESCRIPCIONES = {
    "deslizar": "el viejo sale y el nuevo entra por el lado opuesto",
    "empujar": "el nuevo empuja al viejo fuera del cuadro",
    "zoom": "el viejo atraviesa la camara, el nuevo emerge del fondo",
    "persiana": "franjas horizontales tapan, permutan y se retiran",
    "barrido": "una banda ambar cruza el cuadro: cambio de seccion",
    "fundido_negro": "todo va al fondo del canal y vuelve: cambio de tema",
    "rejilla": "celdas que se cierran en diagonal y se abren",
    "difuminar": "el viejo se deshace, el nuevo se recompone",
    "conmutar": "UN objeto que pasa a otro estado (Transform)",
    "trazar": "el viejo se destraza y el nuevo se traza",
}


def transicion(nombre, saliente, entrante, **kwargs):
    """Despacha por nombre. `KeyError` con el catalogo si el nombre no existe:
    un typo en un script de clip no debe fallar a mitad del render."""
    try:
        fn = TRANSICIONES[nombre]
    except KeyError:
        raise KeyError(
            f"transicion '{nombre}' no existe; hay "
            f"{', '.join(sorted(TRANSICIONES))}") from None
    return fn(saliente, entrante, **kwargs)

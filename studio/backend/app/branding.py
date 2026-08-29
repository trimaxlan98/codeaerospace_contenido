"""Identidad CO.DE Academy obligatoria en todo render.

La marca dejo de ser opcional: cualquier script que no la aplique por su
cuenta sale del render con ella igual, sea un clip de curso, un render suelto
de la Biblioteca o un re-render de codigo viejo. El minimo visual del canal
no depende de que el autor (humano o IA) se acuerde de pedirlo.

Como: se ANEXA un bloque al final del script, nunca al principio.

- Al final, porque manim importa el modulo entero antes de instanciar la
  escena: `marcar_escenas(globals())` alcanza a todas las clases ya
  definidas, y los numeros de linea que reporta un error siguen siendo los
  del codigo del autor (anteponer los correria).
- Solo si el script no menciona ya `code_brand`: los cursos que traen su
  propia base de marca en el style_block se respetan tal cual, sin duplicar
  la marca de agua.
- Dentro de try/except: si algun dia la extension no esta montada, el render
  sale sin marca con un aviso en el log, pero sale. La marca no puede ser un
  punto de fallo de la cola.
"""

import re

MODULO_MARCA = "code_brand"
# Una PRESENTACION trae su identidad en `presentacion.aplicar()`, con la paleta
# volteada al fondo del slide. Anexarle la marca del canal encima le repintaria
# el fondo de negro y le pondria una marca de agua clara sobre blanco:
# invisible. Por eso importar `presentacion` cuenta como traer marca propia.
#
# Se busca el IMPORT y no la palabra suelta: "presentacion" es una palabra
# comun en castellano, y un comentario cualquiera ("# presentacion de la idea")
# habria hecho creer que el script ya trae marca, dejando el render sin ella.
MODULOS_CON_MARCA = (MODULO_MARCA,)
RE_IMPORTA_PRESENTACION = re.compile(
    r"^[ \t]*(?:import[ \t]+presentacion\b|from[ \t]+presentacion[ \t]+import\b)",
    re.MULTILINE)
RUTA_EXTENSIONS = "/workspace/studio/content/manim_extensions"

MARCADOR = "# --- identidad CO.DE Academy (anexada por ManimStudio) ---"
MARCADOR_PRESENTACION = (
    "# --- lienzo de presentacion (anexado por ManimStudio) ---")

BLOQUE_MARCA = f"""{MARCADOR}
try:
    import sys
    if {RUTA_EXTENSIONS!r} not in sys.path:
        sys.path.insert(0, {RUTA_EXTENSIONS!r})
    from {MODULO_MARCA} import marcar_escenas as _code_marcar_escenas
    _code_marcar_escenas(globals())
except Exception as _code_brand_error:  # la marca nunca tumba un render
    print("[CO.DE Academy] marca no aplicada:", _code_brand_error)
"""


MODULO_PRESENTACION = "presentacion"

BLOQUE_PRESENTACION = f"""{MARCADOR_PRESENTACION}
try:
    import sys
    if {RUTA_EXTENSIONS!r} not in sys.path:
        sys.path.insert(0, {RUTA_EXTENSIONS!r})
    from {MODULO_PRESENTACION} import adaptar_escenas as _adaptar_escenas
    _adaptar_escenas(globals())
except Exception as _presentacion_error:  # nunca tumba un render
    print("[CO.DE Academy] lienzo de presentacion no aplicado:",
          _presentacion_error)
"""


def ya_marcado(script: str) -> bool:
    """¿El script ya aplica la identidad por su cuenta?"""
    return (any(m in script for m in MODULOS_CON_MARCA)
            or bool(RE_IMPORTA_PRESENTACION.search(script)))


def aplicar(script: str, tipo: str = "curso") -> str:
    """Script listo para renderizar, con la identidad garantizada.

    En un proyecto de tipo 'presentacion' lo que se garantiza es OTRA cosa: el
    lienzo (formato y fondo) que pidio el proyecto. Sin esto, cualquiera de las
    ~60 animaciones que ya viven en `studio/content/animations/` —escritas para
    un curso, sin llamar a `presentacion.lienzo()`— saldria en 16:9 sobre el
    negro de la marca aunque se hubiera pedido 4:3 sobre blanco, y sin decir
    nada. Un formato que se ignora en silencio es peor que no ofrecerlo.

    El bloque de presentacion ya aplica la identidad (con la paleta volteada al
    fondo), asi que los dos son excluyentes: nunca se anexan ambos.
    """
    if tipo == "presentacion":
        if RE_IMPORTA_PRESENTACION.search(script):
            return script      # el script pide su propio lienzo
        return f"{script.rstrip()}\n\n{BLOQUE_PRESENTACION}"
    if ya_marcado(script):
        return script
    return f"{script.rstrip()}\n\n{BLOQUE_MARCA}"

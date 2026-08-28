"""Catalogo de transiciones (sprint E2): las tres listas no pueden separarse.

`transiciones.py` importa manim, asi que aqui no se puede importar — se lee
con `ast`, igual que `test_audio_promo` hace con `sfx.py`. Lo que se comprueba
es exactamente lo que se rompe en silencio:

- una transicion nueva sin su linea en `DESCRIPCIONES` sale en la interfaz y
  en el prompt del asistente **sin decir para que sirve**;
- una transicion que el demo no enseña es una que nadie va a pedir, porque el
  catalogo en video es el unico sitio donde se ven;
- un nombre en `TRANSICIONES` que no corresponde a ninguna funcion revienta a
  mitad de un render, no al escribir el script.
"""

import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
LIB = RAIZ / "studio" / "content" / "manim_extensions" / "transiciones.py"
DEMO = (RAIZ / "studio" / "content" / "animations" / "experimentacion"
        / "29-transiciones.py")


def _modulo(path: Path) -> ast.Module:
    return ast.parse(path.read_text())


def _dict_de_nivel_superior(arbol: ast.Module, nombre: str) -> dict:
    for nodo in arbol.body:
        if (isinstance(nodo, ast.Assign)
                and any(getattr(t, "id", "") == nombre for t in nodo.targets)):
            claves = [k.value for k in nodo.value.keys]
            valores = [getattr(v, "id", None) if isinstance(v, ast.Name)
                       else getattr(v, "value", None) for v in nodo.value.values]
            return dict(zip(claves, valores))
    raise AssertionError(f"no se encontro {nombre} en {arbol}")


def _funciones(arbol: ast.Module) -> set[str]:
    return {n.name for n in arbol.body if isinstance(n, ast.FunctionDef)}


def test_cada_transicion_apunta_a_una_funcion_que_existe():
    arbol = _modulo(LIB)
    catalogo = _dict_de_nivel_superior(arbol, "TRANSICIONES")
    funciones = _funciones(arbol)
    faltan = {k: v for k, v in catalogo.items() if v not in funciones}
    assert not faltan, f"apuntan a funciones inexistentes: {faltan}"
    assert len(catalogo) >= 10


def test_cada_transicion_tiene_su_descripcion():
    arbol = _modulo(LIB)
    catalogo = _dict_de_nivel_superior(arbol, "TRANSICIONES")
    descripciones = _dict_de_nivel_superior(arbol, "DESCRIPCIONES")
    assert sorted(catalogo) == sorted(descripciones)
    assert all(d and len(d) > 15 for d in descripciones.values())


def test_el_demo_enseña_todas_las_transiciones():
    catalogo = _dict_de_nivel_superior(_modulo(LIB), "TRANSICIONES")
    arbol = _modulo(DEMO)
    orden = None
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Assign)
                and any(getattr(t, "id", "") == "ORDEN" for t in nodo.targets)):
            orden = [e.value for e in nodo.value.elts]
    assert orden, "el demo no declara ORDEN"
    assert sorted(orden) == sorted(catalogo)
    assert len(orden) == len(set(orden)), "una transicion se enseña dos veces"

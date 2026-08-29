"""Identidad CO.DE Academy obligatoria: todo render sale con la marca, el
script del autor no se altera y los cursos que la traen no la duplican."""

import ast

from app import branding

SCRIPT = ("from manim import *\n"
          "class Demo(Scene):\n"
          "    def construct(self):\n"
          "        self.play(Create(Circle()))\n")


def test_aplica_la_marca_sin_mover_las_lineas_del_autor():
    salida = branding.aplicar(SCRIPT)
    assert salida != SCRIPT
    assert "code_brand" in salida
    # Lo del autor queda arriba y en sus mismas lineas: un error en la linea 3
    # del script sigue siendo la linea 3 del archivo renderizado.
    assert salida.startswith(SCRIPT.rstrip())
    for n, linea in enumerate(SCRIPT.splitlines()):
        assert salida.splitlines()[n] == linea


def test_el_bloque_anexado_es_python_valido():
    ast.parse(branding.aplicar(SCRIPT))


def test_no_duplica_la_marca_de_un_curso_que_ya_la_trae():
    """Los style_block de los cursos importan code_brand por su cuenta: se
    respetan tal cual para no encimar dos marcas de agua."""
    propio = ("from code_brand import marca_agua\n" + SCRIPT)
    assert branding.aplicar(propio) == propio
    assert branding.ya_marcado(propio)
    # Idempotente: aplicar dos veces no anexa dos bloques
    una = branding.aplicar(SCRIPT)
    assert branding.aplicar(una) == una


def test_la_marca_no_puede_tumbar_un_render(capfd):
    """El bloque va en try/except: si la extension no estuviera montada, el
    render sale sin marca con un aviso en el log, pero sale."""
    salida = branding.aplicar(SCRIPT)
    assert "try:" in salida and "except Exception" in salida
    bloque = salida.split(branding.MARCADOR, 1)[1]
    # Sin la extension en sys.path (no existe en el host de tests), ejecutar
    # el bloque no debe propagar la excepcion
    exec(compile(bloque, "s", "exec"), {"__name__": "s"})
    assert "marca no aplicada" in capfd.readouterr().out


def _code_brand_con_manim_falso(monkeypatch):
    """Importa code_brand contra un manim minimo: el host de tests no tiene
    manim (los renders viven en el contenedor)."""
    import sys
    import types
    from pathlib import Path

    fake = types.ModuleType("manim")
    for nombre in ("DR", "DOWN", "RIGHT", "UP"):
        setattr(fake, nombre, object())
    for nombre in ("FadeIn", "FadeOut", "Line", "Text", "VGroup"):
        setattr(fake, nombre, type(nombre, (), {}))
    fake.config = types.SimpleNamespace(background_color=None)
    fake.Scene = type("Scene", (), {"setup": lambda self: None,
                                    "__module__": "manim.scene.scene"})
    monkeypatch.setitem(sys.modules, "manim", fake)
    monkeypatch.syspath_prepend(
        Path(__file__).resolve().parents[2] / "content" / "manim_extensions")
    monkeypatch.delitem(sys.modules, "code_brand", raising=False)
    import code_brand
    return code_brand, fake


def test_marcar_escenas_no_marca_dos_veces(monkeypatch):
    """`marcar_escenas` es idempotente y no vuelve a envolver una clase que
    hereda de una ya marcada (si no, doble marca de agua)."""
    code_brand, fake_manim = _code_brand_con_manim_falso(monkeypatch)

    aplicadas = []
    monkeypatch.setattr(code_brand, "registrar_fuentes", lambda: None)
    monkeypatch.setattr(code_brand, "aplicar_marca",
                        lambda esc, **kw: aplicadas.append(esc))
    monkeypatch.setattr(code_brand, "_fondo_propio", lambda: True)

    class Base(fake_manim.Scene):
        pass

    class Hija(Base):
        pass

    ns = {"__name__": __name__, "Base": Base, "Hija": Hija}
    code_brand.marcar_escenas(ns)
    code_brand.marcar_escenas(ns)  # segunda pasada: no debe re-envolver

    Hija().setup()
    assert len(aplicadas) == 1


def test_marcar_escenas_ignora_lo_que_no_es_del_script(monkeypatch):
    """Solo se marcan las clases definidas en el propio script: nunca la
    Scene importada de manim ni clases de las librerias del canal."""
    code_brand, fake_manim = _code_brand_con_manim_falso(monkeypatch)
    monkeypatch.setattr(code_brand, "registrar_fuentes", lambda: None)
    monkeypatch.setattr(code_brand, "_fondo_propio", lambda: True)

    class Ajena(fake_manim.Scene):
        pass

    Ajena.__module__ = "una_libreria"
    code_brand.marcar_escenas({"__name__": __name__, "Scene": fake_manim.Scene,
                               "Ajena": Ajena})
    assert not getattr(fake_manim.Scene, "_code_brand", False)
    assert not getattr(Ajena, "_code_brand", False)


def test_una_presentacion_trae_su_propia_identidad():
    """Una presentacion aplica la marca con `presentacion.aplicar()`, que
    voltea la paleta al fondo del slide. Anexarle encima la del canal le
    repintaria el fondo de negro y le pondria una marca de agua clara sobre
    blanco: invisible.
    """
    de_pres = ("import presentacion\n"
               "PRES = presentacion.lienzo()\n" + SCRIPT)
    assert branding.ya_marcado(de_pres)
    assert branding.aplicar(de_pres) == de_pres
    # La otra forma de importarlo cuenta igual.
    assert branding.ya_marcado("from presentacion import lienzo\n" + SCRIPT)


def test_la_palabra_presentacion_suelta_NO_cuenta_como_marca():
    """«presentacion» es una palabra comun en castellano. Si bastara con
    mencionarla, un comentario cualquiera dejaria el render sin la identidad
    del canal — y sin que nadie se enterase hasta ver el video."""
    con_comentario = "# presentacion de la idea principal\n" + SCRIPT
    assert not branding.ya_marcado(con_comentario)
    assert "code_brand" in branding.aplicar(con_comentario)
    # Ni una variable que se llame parecido.
    assert not branding.ya_marcado("presentacion_larga = True\n" + SCRIPT)


# ── el lienzo de una presentacion se garantiza como se garantiza la marca ────

SCRIPT_ANIMACION = ("import sys\n"
                    "sys.path.insert(0, '/workspace/studio/content/manim_extensions')\n"
                    "from manim import *\n"
                    "class Diagrama(Scene):\n"
                    "    def construct(self):\n"
                    "        self.play(Create(Circle()))\n")


def test_una_presentacion_recibe_el_lienzo_y_no_la_marca():
    """Las ~60 animaciones de content/animations/ se escribieron para un curso
    y no llaman a `presentacion.lienzo()`. Sin este bloque, el formato y el
    fondo que pide el proyecto se ignoran EN SILENCIO: el render sale 16:9
    sobre el negro de la marca aunque se haya pedido 4:3 sobre blanco.
    """
    salida = branding.aplicar(SCRIPT_ANIMACION, tipo="presentacion")
    assert "adaptar_escenas" in salida
    # Los dos bloques son excluyentes: el de presentacion ya aplica identidad.
    assert branding.MARCADOR not in salida
    # Y lo del autor sigue arriba, en sus mismas lineas.
    assert salida.startswith(SCRIPT_ANIMACION.rstrip())


def test_un_curso_sigue_recibiendo_la_marca_y_no_el_lienzo():
    salida = branding.aplicar(SCRIPT_ANIMACION)
    assert "code_brand" in salida
    assert "adaptar_escenas" not in salida


def test_una_presentacion_que_pide_su_lienzo_no_se_toca():
    propio = "import presentacion\nPRES = presentacion.lienzo()\n" + SCRIPT_ANIMACION
    assert branding.aplicar(propio, tipo="presentacion") == propio


def test_el_bloque_del_lienzo_es_python_valido_y_no_tumba_un_render(capfd):
    salida = branding.aplicar(SCRIPT_ANIMACION, tipo="presentacion")
    ast.parse(salida)
    bloque = salida.split(branding.MARCADOR_PRESENTACION, 1)[1]
    # Sin la extension en sys.path (no existe en el host de tests), ejecutar el
    # bloque no debe propagar la excepcion: el render sale, con un aviso.
    exec(compile(bloque, "s", "exec"), {"__name__": "s"})
    assert "lienzo de presentacion no aplicado" in capfd.readouterr().out

"""Pruebas de studio/tools/cortar_presentacion.py: el reparto en fragmentos.

Es la regla que define una presentacion de presentacion —donde cae cada clic del
ponente— y se decide sin tocar ffmpeg ni Docker: `cortes()` convierte los
instantes que anoto la escena en los tramos [inicio, fin] de cada slide.

Se prueba sobre `cortar_presentacion` y no sobre `empaquetar_presentacion` porque es ahi
donde vive: el mismo modulo que ejecuta el runner dentro del contenedor. La
herramienta de consola lo importa.
"""

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS))

import cortar_presentacion as cp  # noqa: E402


def test_cada_paso_cierra_un_fragmento():
    tramos = cp.cortes([{"t": 2.8, "etiqueta": "El escenario"},
                        {"t": 6.9, "etiqueta": "El paso"}], dur=6.9)
    assert [(t["inicio"], t["fin"]) for t in tramos] == [(0.0, 2.8), (2.8, 6.9)]
    assert [t["etiqueta"] for t in tramos] == ["El escenario", "El paso"]


def test_los_tramos_se_encadenan_sin_hueco_ni_solape():
    """El fin de un fragmento ES el inicio del siguiente: de ahi sale que el
    ultimo fotograma de uno sea el primero del otro y el salto no se vea."""
    tramos = cp.cortes([{"t": 1.5}, {"t": 4.0}, {"t": 7.25}], dur=7.25)
    for anterior, siguiente in zip(tramos, tramos[1:]):
        assert anterior["fin"] == siguiente["inicio"]
    assert tramos[0]["inicio"] == 0.0


def test_la_cola_corta_tras_el_ultimo_paso_se_descarta():
    """Casi toda escena termina con un `wait` de cortesia. Eso no es un paso
    mas: un slide de dos decimas en negro seria un parpadeo en la sala."""
    tramos = cp.cortes([{"t": 9.9}], dur=10.1)
    assert len(tramos) == 1
    assert tramos[0]["fin"] == 9.9


def test_una_cola_larga_si_es_un_fragmento():
    """Pero si despues del ultimo paso queda contenido de verdad, es un
    fragmento: perderlo dejaria al ponente sin su cierre."""
    tramos = cp.cortes([{"t": 4.0, "etiqueta": "La idea"}], dur=9.0)
    assert len(tramos) == 2
    assert (tramos[1]["inicio"], tramos[1]["fin"]) == (4.0, 9.0)
    assert tramos[1]["etiqueta"] == "Cierre"


def test_una_escena_sin_pasos_es_una_presentacion_de_una_sola_parte():
    tramos = cp.cortes([], dur=12.0)
    assert len(tramos) == 1
    assert (tramos[0]["inicio"], tramos[0]["fin"]) == (0.0, 12.0)


def test_un_paso_sin_etiqueta_recibe_una():
    """El nombre del paso acaba siendo el nombre del slide, que es lo que el
    ponente lee en el modo presentador: nunca puede quedar vacio."""
    tramos = cp.cortes([{"t": 1.0}, {"t": 2.0}], dur=2.0)
    assert [t["etiqueta"] for t in tramos] == ["Paso 1", "Paso 2"]


# ── el contrato con la interfaz ──────────────────────────────────────────────
#
# `presentacion.py` importa manim y no se puede ejecutar aqui (el venv del
# backend no lo tiene: manim vive en el contenedor). Lo que si se puede fijar
# es el CONTRATO que la interfaz promete, leyendo el fuente. Es poco, pero
# evita que se caiga en silencio lo unico que hace utilizable la adaptacion.

EXTENSIONS = Path(__file__).resolve().parents[3] / "studio" / "content" / "manim_extensions"


def test_adaptar_escenas_deja_usable_el_nombre_que_anuncia_la_interfaz():
    """El diálogo «Abrir como presentación» le dice al usuario que escriba
    `presentacion.paso(self, "...")`. Una animación de la Biblioteca nunca
    importó ese módulo, así que sin inyectarlo esa línea daría NameError y el
    consejo de la interfaz sería una trampa.
    """
    fuente = (EXTENSIONS / "presentacion.py").read_text(encoding="utf-8")
    cuerpo = fuente.split("def adaptar_escenas", 1)[1]
    for nombre in ('ns.setdefault("presentacion"', 'ns.setdefault("paso"',
                   'ns.setdefault("PRES"'):
        assert nombre in cuerpo, f"adaptar_escenas ya no inyecta {nombre}"
    # setdefault y no asignacion: jamas se pisa un nombre del autor.
    assert "ns[" not in cuerpo


def test_el_bloque_que_anexa_el_backend_llama_a_adaptar_escenas():
    """Las dos mitades tienen que seguir encajando: el backend anexa la
    llamada y el modulo la expone."""
    from app import branding
    assert "adaptar_escenas" in branding.BLOQUE_PRESENTACION
    fuente = (EXTENSIONS / "presentacion.py").read_text(encoding="utf-8")
    assert "def adaptar_escenas(" in fuente

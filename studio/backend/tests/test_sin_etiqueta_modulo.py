"""Ningún curso nuevo lleva la etiqueta «Modulo 0N» en pantalla.

Desde el curso 37 (2026-09-25) el dueño pidió quitarla: «me gustó mucho
más de esta manera, ya sin ese texto de modulo XX». Los cursos 1–36 ya
publicados la conservan y quedan congelados en LEGADO; cualquier curso
nuevo que llame a `hud_modulo(` en un clip hace fallar este test.
Ver .claude/skills/curso-de-video/SKILL.md, «SIN etiqueta Modulo 0N».
"""
from pathlib import Path

CURSOS = Path(__file__).resolve().parents[2] / "content" / "cursos"

# Prefijos de slug de los cursos publicados CON etiqueta (cursos 1-36).
# No se amplía: un curso nuevo no entra aquí.
LEGADO = (
    "aerodinamica", "agentes-de-ia-maquinas-que-operan-el-mun",
    "algebra-lineal", "apuntar-a-un-satelite-el-arte-del-seguim",
    "calculo-vectorial", "caos-el-orden-escondido",
    "cerrar-el-enlace-la-cuenta-en-decibelios", "comunicaciones-digitales",
    "control-domar-sistemas-que-se-resisten",
    "criptografia-el-arte-de-guardar-secretos",
    "de-la-palabra-al-vector-embeddings-y-ate", "electromagnetismo",
    "el-espectro-la-guerra-invisible-por-las", "matematicas-en-la-naturaleza",
    "materiales-que-van-al-espacio", "metrologia-optica",
    "procesamiento-senales", "protocolos-internet",
    "redes-neuronales-la-maquina-que-aprende", "relatividad-y-el-gps",
    "sdr-la-radio-hecha-software", "sistemas-atp",
    "sistemas-distribuidos-la-nube-por-dentro",
    "teoria-de-la-informacion-los-bits-de-shannon", "tesis6g",
    "tsiolkovsky-la-tirania-del-cohete",
)


def _es_legado(nombre: str) -> bool:
    return any(nombre == p or nombre.startswith(p + "-") for p in LEGADO)


def test_cursos_nuevos_sin_hud_modulo():
    culpables = []
    for curso in sorted(p for p in CURSOS.iterdir() if p.is_dir()):
        if _es_legado(curso.name):
            continue
        for clip in sorted((curso / "clips").glob("*.py")):
            if "hud_modulo(" in clip.read_text(encoding="utf-8"):
                culpables.append(f"{curso.name}/clips/{clip.name}")
    assert not culpables, (
        "Estos clips ponen la etiqueta 'Modulo 0N', que ya no se usa en "
        "cursos nuevos (pedido del dueño, curso 37): " + ", ".join(culpables))


def test_hay_cursos_sin_legado():
    """El test de arriba no es vacuo: al menos el curso 37 se revisa."""
    assert any(not _es_legado(p.name) for p in CURSOS.iterdir() if p.is_dir())

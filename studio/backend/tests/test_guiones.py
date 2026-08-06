"""Partes puras del generador de guiones (studio/tools/guiones.py):
parser de duracion mp4, hash de desactualizacion y seleccion de clips.
La generacion (Vertex) no se testea aqui: es el mismo cliente ya cubierto
por test_ai.py y el comando se prueba a mano contra un proyecto real."""

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from guiones import (cargar_secciones, duracion_mp4, hash_guion,
                     parse_clips_arg, slugify)


def _mp4(timescale: int, duration: int, version: int = 0) -> bytes:
    """mp4 minimo: ftyp + moov{mvhd} con la duracion dada."""
    if version == 0:
        body = bytes([0, 0, 0, 0]) + struct.pack(">IIII", 0, 0, timescale, duration)
    else:
        body = bytes([1, 0, 0, 0]) + struct.pack(">QQIQ", 0, 0, timescale, duration)
    mvhd = struct.pack(">I4s", 8 + len(body), b"mvhd") + body
    moov = struct.pack(">I4s", 8 + len(mvhd), b"moov") + mvhd
    ftyp = struct.pack(">I4s", 16, b"ftyp") + b"isom\x00\x00\x02\x00"
    return ftyp + moov


def test_duracion_mp4_version0(tmp_path):
    p = tmp_path / "v.mp4"
    p.write_bytes(_mp4(timescale=1000, duration=26200))
    assert duracion_mp4(p) == 26.2


def test_duracion_mp4_version1(tmp_path):
    p = tmp_path / "v.mp4"
    p.write_bytes(_mp4(timescale=600, duration=600 * 90, version=1))
    assert duracion_mp4(p) == 90.0


def test_duracion_mp4_corrupto_o_ausente(tmp_path):
    p = tmp_path / "v.mp4"
    p.write_bytes(b"no es un mp4")
    assert duracion_mp4(p) is None
    assert duracion_mp4(tmp_path / "no-existe.mp4") is None


def test_hash_guion_detecta_cambios():
    base = hash_guion("script", "Escena", 26.2, "Charon")
    assert base == hash_guion("script", "Escena", 26.2, "Charon")
    # La duracion se redondea al segundo: variaciones sub-segundo no ensucian
    assert base == hash_guion("script", "Escena", 26.4, "Charon")
    assert base != hash_guion("script2", "Escena", 26.2, "Charon")
    assert base != hash_guion("script", "Otra", 26.2, "Charon")
    assert base != hash_guion("script", "Escena", 30.0, "Charon")
    assert base != hash_guion("script", "Escena", 26.2, "Kore")
    assert base != hash_guion("script", "Escena", None, "Charon")


def test_parse_clips_arg():
    assert parse_clips_arg("1,3-5", 8) == {0, 2, 3, 4}
    assert parse_clips_arg("2", 8) == {1}
    # Fuera de rango se descarta en silencio
    assert parse_clips_arg("7-12", 8) == {6, 7}
    assert parse_clips_arg("9", 8) == set()


def test_cargar_secciones_desde_md(tmp_path):
    """Sin secciones.json, los tiempos se re-parsean de la tabla del .md
    (guiones previos a la alineacion por secciones)."""
    (tmp_path / "01-x.md").write_text(
        "# Titulo\n\n"
        "| Tiempo | Momento visual | Narración |\n"
        "|---|---|---|\n"
        "| 0–5 s | intro | Hola a todos. |\n"
        "| 6–12 s | formula | La barra \\| escapada. |\n")
    secciones = cargar_secciones(tmp_path, "01-x")
    assert secciones == [{"t_inicio": 0.0, "texto": "Hola a todos."},
                         {"t_inicio": 6.0, "texto": "La barra | escapada."}]


def test_cargar_secciones_prefiere_json(tmp_path):
    (tmp_path / "01-x.md").write_text("| 0–5 s | a | b |\n| 6–9 s | c | d |\n")
    (tmp_path / "01-x.secciones.json").write_text(
        '[{"t_inicio": 2.5, "texto": "exacto"}]')
    assert cargar_secciones(tmp_path, "01-x") == [
        {"t_inicio": 2.5, "texto": "exacto"}]
    # y sin nada, el .txt de corrido
    (tmp_path / "02-y.txt").write_text("uno\n\ndos\n")
    assert cargar_secciones(tmp_path, "02-y") == [
        {"texto": "uno"}, {"texto": "dos"}]


def test_slugify_sin_acentos():
    assert slugify("01 - El universo en una fórmula") == "01-el-universo-en-una-formula"
    assert slugify("¿Órbitas?") == "orbitas"
    assert slugify("***") == "clip"

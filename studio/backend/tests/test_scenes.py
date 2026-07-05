"""Deteccion estatica de escenas (nunca ejecuta el script)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app.scenes import detect_scenes


def test_basic_scene():
    src = "from manim import *\nclass Intro(Scene):\n    def construct(self): pass\n"
    assert detect_scenes(src) == ["Intro"]


def test_threed_and_inheritance_chain():
    src = (
        "from manim import *\n"
        "class Base(ThreeDScene): pass\n"
        "class Orbita(Base): pass\n"
        "class NoEscena: pass\n"
    )
    assert detect_scenes(src) == ["Base", "Orbita"]


def test_attribute_base():
    src = "import manim\nclass X(manim.Scene): pass\n"
    assert detect_scenes(src) == ["X"]


def test_syntax_error_raises():
    with pytest.raises(ValueError):
        detect_scenes("class X(Scene:\n")


def test_malicious_code_not_executed(tmp_path):
    canary = tmp_path / "canary.txt"
    src = (
        f"open({str(canary)!r}, 'w').write('ejecutado')\n"
        "from manim import *\n"
        "class Mala(Scene): pass\n"
    )
    assert detect_scenes(src) == ["Mala"]
    assert not canary.exists(), "detect_scenes ejecuto codigo del script!"


def test_circular_inheritance_no_crash():
    src = "class A(B): pass\nclass B(A): pass\n"
    assert detect_scenes(src) == []

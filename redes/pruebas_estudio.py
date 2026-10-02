#!/usr/bin/env python3
"""Pruebas del estudio de contenido (unittest; no requiere pytest).

    python3 redes/pruebas_estudio.py          # todas (~1 min)
    python3 redes/pruebas_estudio.py -k audio # solo las que contengan «audio»

Cubre: specs de carruseles válidos y sin material privado, variantes A/B, render mínimo (tamaño y número
de láminas), periodicidad de las ventanas de los loops, costura del audio circular de los reels y
fondos a medida (tamaño y ventana vertical).
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for p in ("redes/carruseles", "animaciones", "studio/content/manim_extensions", "studio/tools"):
    sys.path.insert(0, str(REPO / p))

import motor_carrusel as MC  # noqa: E402


def specs():
    return sorted((REPO / "redes/carruseles/specs").rglob("*.json"))


class Carruseles(unittest.TestCase):
    def test_specs_validos(self):
        for r in specs():
            base = json.loads(r.read_text(encoding="utf-8"))
            for s in MC.expandir_variantes(base):
                errores, _ = MC.validar(s)
                self.assertEqual(errores, [], f"{r.name} [{s['id']}]")

    def test_sin_material_privado(self):
        for r in specs():
            texto = r.read_text(encoding="utf-8")
            for prohibido in MC.PROHIBIDO_IMAGEN:
                self.assertNotIn(f"sticker:{prohibido}", texto, r.name)
                self.assertNotRegex(texto, rf'"sticker:[^"]*{prohibido}', r.name)

    def test_imagen_privada_rechazada(self):
        with self.assertRaises(ValueError):
            MC.cargar_imagen("sticker:tesis_sem_1_orbita/NormaSinIA")
        with self.assertRaises(ValueError):
            MC.cargar_imagen("sticker:../../../etc/passwd")
        with self.assertRaises(ValueError):
            MC.cargar_imagen("/etc/hosts")

    def test_variantes(self):
        base = {"id": "x", "serie": "s", "laminas": [{"tipo": "portada", "titulo": "A"}, {"tipo": "cierre", "titulo": "C"}],
                "variantes": [{"sufijo": "b", "portada": {"titulo": "B"}, "fondo": {"tema": "nebulosa"}}]}
        vs = MC.expandir_variantes(base)
        self.assertEqual([v["id"] for v in vs], ["x", "x-b"])
        self.assertEqual(vs[1]["laminas"][0]["titulo"], "B")
        self.assertEqual(vs[0]["laminas"][0]["titulo"], "A")           # la base no se toca
        self.assertEqual(vs[1]["fondo"]["tema"], "nebulosa")

    def test_render_minimo(self):
        spec = {"id": "prueba-min", "serie": "_pruebas", "fondo": {"tema": "orbita", "tipo": "contenido"},
                "laminas": [{"tipo": "portada", "titulo": "Hola órbita"},
                            {"tipo": "termino", "termino": "TLE", "definicion": "Dos líneas con los elementos orbitales."},
                            {"tipo": "formula", "formula": "λ = c / f", "resultado": "≈ 2.2 m", "nota": "137 MHz"},
                            {"tipo": "cierre", "titulo": "Fin"}],
                "fuentes": ["prueba"], "pie_texto": "prueba"}
        with tempfile.TemporaryDirectory() as tmp:
            rutas, _ = MC.renderizar(spec, tmp)
            self.assertEqual(len(rutas), 4)
            from PIL import Image
            for r in rutas:
                self.assertEqual(Image.open(r).size, (1080, 1350))
            self.assertTrue((Path(tmp) / "prueba-min_hoja.jpg").exists())


class Loops(unittest.TestCase):
    def test_ventanas_periodicas_y_crossfade(self):
        from reels_promo import ventana, ventana_texto
        T = 12.0
        for t in np.linspace(0, T, 97):
            self.assertAlmostEqual(ventana(t, 2, 5, 0.6, T), ventana(t + T, 2, 5, 0.6, T), places=9)
            # dos ventanas contiguas suman 1 (fundido cruzado exacto)
            s = ventana(t, 0, 6, 0.6, T) + ventana(t, 6, 12, 0.6, T)
            self.assertAlmostEqual(s, 1.0, places=9)
            # las de texto nunca se solapan
            self.assertLessEqual(min(ventana_texto(t, 0, 3, 0.35, T), ventana_texto(t, 3, 6, 0.35, T)), 1e-9)

    def test_audio_reels_sin_costura(self):
        import sonido_reels as SR
        for nombre, (f, T, desfase) in {**SR.REELS, **SR.REELS_VIVO}.items():
            SR.RNG = np.random.default_rng(1)
            SR.sm.RNG = np.random.default_rng(2)
            m = SR.Circular(T)
            f(m)
            x = SR.master(m, desfase)
            paso = np.percentile(np.abs(np.diff(x, axis=0)).max(1), 99)
            self.assertLessEqual(np.abs(x[0] - x[-1]).max(), paso, nombre)
            self.assertEqual(len(x), int(round(T * SR.SR)), nombre)


class Fondos(unittest.TestCase):
    def test_tamano_y_ventana(self):
        from PIL import Image
        import fondos_a_medida as FM
        with tempfile.TemporaryDirectory() as tmp:
            FM.CACHE = Path(tmp)
            r = FM.fondo_a_medida("orbita", "contenido", 0, 120, 150, ventana=None)
            self.assertEqual(Image.open(r).size, (120, 150))
            r = FM.fondo_a_medida("fisica", "portada", 0, 108, 192)          # vertical decorado → ventana
            self.assertEqual(Image.open(r).size, (108, 192))
            self.assertIn("_v72", r.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)

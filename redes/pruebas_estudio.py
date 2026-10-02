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


class CLI(unittest.TestCase):
    """codeae: el registro ve todas las piezas y la subida a Drive exige confirmación."""

    @classmethod
    def setUpClass(cls):
        import codeae
        cls.C = codeae

    def test_registro_completo_y_ids_unicos(self):
        vs, cs = self.C._videos(), self.C._specs()
        self.assertGreaterEqual(len(vs), 30)
        self.assertGreaterEqual(len(cs), 50)
        self.assertFalse(set(vs) & set(cs), "un id no puede ser de carrusel y de video a la vez")
        for v in vs.values():
            self.assertTrue((self.C.EXP / v.archivo).exists(), v.id)
            self.assertIsNotNone(v.audio_fn, v.id)

    def test_subir_sin_confirmar_nunca_llama_a_rclone(self):
        import argparse
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            self.C.EST = Path(tmp)
            (Path(tmp) / "paquetes" / "p").mkdir(parents=True)
            (Path(tmp) / "paquetes" / "p" / "a.txt").write_text("x")
            with mock.patch.object(self.C.subprocess, "run") as run:
                self.C.cmd_subir(argparse.Namespace(paquete="p", confirmo=False))
                run.assert_not_called()
                self.C.cmd_subir(argparse.Namespace(paquete="p", confirmo=True))
                self.assertEqual(run.call_count, 1)
                self.assertEqual(run.call_args[0][0][:2], ["rclone", "copy"])
        self.C.EST = REPO / "exports" / "estudio"

    def test_paquete_omite_no_publicar(self):
        import argparse
        cs = self.C._specs()
        self.assertEqual(cs["orbit-eye"][1].get("estado"), "no_publicar")
        with tempfile.TemporaryDirectory() as tmp:
            self.C.EST = Path(tmp)
            self.C.cmd_paquete(argparse.Namespace(ids=["orbit-eye"], nombre="t"))
            self.assertFalse(any((Path(tmp) / "paquetes" / "t").rglob("*.png")))
        self.C.EST = REPO / "exports" / "estudio"


class DatosOrbitales(unittest.TestCase):
    """Datos orbitales reales (muestra congelada de la ISS del 2026-10-02; sin red)."""

    @classmethod
    def setUpClass(cls):
        from datetime import timedelta  # noqa: F401
        import datos_orbitales as DO
        from datos_orbitales.fuentes import MUESTRAS
        cls.DO = DO
        cls.el = DO.cargar(MUESTRAS / "iss_2026-10-02.json")

    def test_geometria_de_la_iss(self):
        from datetime import timedelta
        ts = [self.el.epoca + timedelta(minutes=m) for m in range(0, 185)]
        lat, lon, h = self.DO.posicion_geodetica(self.el, ts)
        self.assertLess(abs(lat).max(), 51.9)                       # inclinación 51.63° + achatamiento
        self.assertTrue(((h > 400) & (h < 450)).all())              # la ISS orbita a ~420 km
        subidas = np.where((lat[:-1] < 0) & (lat[1:] >= 0))[0]
        self.assertAlmostEqual(float(np.diff(subidas).mean()), 92.0, delta=1.0)    # periodo ≈ 92 min

    def test_pases_bordes_y_duracion(self):
        from datos_orbitales.observador import topocentrico
        ps = self.DO.pases(self.el, self.DO.CDMX, self.el.epoca, dias=2, el_min=10)
        self.assertGreaterEqual(len(ps), 6)
        for p in ps:
            e = topocentrico(self.el, self.DO.CDMX, [p.aos.timestamp(), p.los.timestamp()])[1]
            self.assertTrue(np.allclose(e, 10.0, atol=0.1), e)       # el pase empieza y acaba en la máscara
            self.assertGreaterEqual(p.el_max, 10.0)
            self.assertTrue(60 < p.duracion_s < 660)                 # un pase de ISS dura de 1 a 11 min
            self.assertGreater(p.rango_min_km, 400)

    def test_doppler_orbita_circular_550km(self):
        from datos_orbitales.fuentes import Elementos
        a = 6378.137 + 550
        n = np.sqrt(398600.8 / a ** 3) * 86400 / (2 * np.pi)
        omm = dict(self.el.omm, MEAN_MOTION=n, ECCENTRICITY=0.0001, INCLINATION=53.0, BSTAR=0.0,
                   MEAN_MOTION_DOT=0.0, MEAN_MOTION_DDOT=0.0)
        c = Elementos(1, "CIRC550", self.el.epoca, omm, "celestrak", self.el.descargado)
        ps = self.DO.pases(c, self.DO.CDMX, c.epoca, dias=3, el_min=0.0)
        mx = max(self.DO.curva_doppler(c, self.DO.CDMX, p, 437e6)["df_max"] for p in ps)
        # Cota física: v·RT/(RT+h)·f0/c = 10.19 kHz (pase cenital sin rotación terrestre); la rotación la baja.
        self.assertLessEqual(mx, 10.2e3)
        self.assertGreater(mx, 9.3e3)

    def test_doppler_signo_y_cruce(self):
        p = self.DO.pases(self.el, self.DO.CDMX, self.el.epoca, dias=2, el_min=10)[2]
        d = self.DO.curva_doppler(self.el, self.DO.CDMX, p, 145.8e6)
        self.assertGreater(d["df"][0], 0)                            # se acerca: frecuencia sube
        self.assertLess(d["df"][-1], 0)                              # se aleja: frecuencia baja
        self.assertLess(abs(d["t_cruce"] - p.duracion_s / 2), 30)    # cruza por cero cerca del TCA

    def test_sello_y_epoca_caducada(self):
        from datetime import timedelta
        ahora = self.el.epoca + timedelta(days=1)
        self.assertEqual(self.DO.sello(self.el, 3, ahora)["rigor"], "dato")
        self.assertIn("época 2026-10-02", self.DO.sello(self.el, 3, ahora)["texto"])
        tarde = self.el.epoca + timedelta(days=4)
        self.assertEqual(self.DO.sello(self.el, 3, tarde)["rigor"], "simulacion")
        with self.assertRaises(self.DO.EpocaCaducada):
            self.DO.exigir_vigente(self.el, 3, tarde)

    def test_traza_corta_el_antimeridiano_y_privacidad(self):
        _, lat, lon = self.DO.traza_terrestre(self.el, self.el.epoca, minutos=180)
        self.assertTrue(np.isnan(lon).any())
        self.assertTrue((np.nanmax(np.abs(lon)) <= 180))
        o = self.DO.Observador(19.4326, -99.1332, 2240, redondeo_deg=0.1).publicable()
        self.assertEqual((o.lat, o.lon), (19.4, -99.1))


if __name__ == "__main__":
    unittest.main(verbosity=2)

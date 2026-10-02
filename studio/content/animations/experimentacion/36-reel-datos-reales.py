import sys
from pathlib import Path

sys.path.insert(0, "/workspace/studio/content/manim_extensions")
_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *
from datos_orbitales.ejemplos import pase_estrella
from marca_aerospace import AMBAR, CIAN, FONDO, PLATA, PLATA_MEDIA
from marca_vertical import _texto, fondo_reel, marco
from reels_promo import Reloj, cabecera, chip, suave
from rotulos_aerospace import TENUE

# Reel en LOOP con DATOS REALES: el pase más alto de la ISS sobre Ciudad de México en 3 días (SGP4 + elementos
# de CelesTrak congelados en studio/content/datos_orbitales/muestras). Arriba, el cielo visto desde el
# observador con la trayectoria verdadera (azimut/elevación); abajo, la curva en S del Doppler del mismo pase
# con la cifra viva. El pase de 6 min 44 s se comprime a T = 12 s; el marcador se desvanece al final del pase
# para que el empalme del loop sea limpio. La frecuencia (437 MHz) es un EJEMPLO y se dice en pantalla.

T = 12.0
DESFASE = 4.2            # el video empieza con el satélite a mitad del pase (la portada tiene marcador)
LINEA = "#2A3742"


class ReelDopplerReal(Scene):
    def construct(self):
        self.camera.background_color = FONDO
        W, H = marco(self)
        reloj = Reloj(self, T, desfase=DESFASE)
        fondo_reel(self, entrada=False, periodo=T)
        e = pase_estrella()
        tr, dp = e["tray"], e["doppler"]
        n = len(tr["t"])
        cabecera(self, "Datos reales · ISS", "La curva en S,\ncon un pase real", n=18, tam=92)

        # ── Cielo: círculo de elevación, puntos cardinales y la trayectoria real ─────────────────────────
        C, R = np.array([0.0, 1.45, 0.0]), 2.95
        polar = lambda az, el: C + (R * (90 - el) / 90) * np.array([np.sin(np.deg2rad(az)), np.cos(np.deg2rad(az)), 0])
        for el_, op in ((0, 0.55), (30, 0.28), (60, 0.28)):
            self.add(Circle(radius=R * (90 - el_) / 90, stroke_width=2.2, stroke_color=TENUE).set_stroke(opacity=op).move_to(C).set_z_index(2))
        for az_, lab in ((0, "N"), (90, "E"), (180, "S"), (270, "O")):
            self.add(_texto(lab, 28, "SEMIBOLD", TENUE).move_to(polar(az_, -9)).set_z_index(3))
        ruta = VMobject().set_points_as_corners([polar(a, el_) for a, el_ in zip(tr["az"], tr["el"])])
        ruta.set_stroke(color=CIAN, width=3.5, opacity=0.35).set_fill(opacity=0).set_z_index(4)
        self.add(ruta)
        ruta_viva = VMobject().set_z_index(5)
        sat = VGroup(Dot(radius=0.34, color=CIAN).set_opacity(0.18), Dot(radius=0.13, color=CIAN)).set_z_index(6)
        self.add(ruta_viva, sat)
        ec = chip("Dato real", AMBAR, 22).move_to([W / 2 - 1.7, 4.2, 0])
        self.add(ec)

        # ── Curva en S del Doppler ───────────────────────────────────────────────────────────────────────
        X0, X1, YC, HH = -W / 2 + 1.1, W / 2 - 0.7, -5.0, 1.2
        xs = np.asarray(dp["t"]) / dp["t"][-1]
        ys = np.asarray(dp["df"]) / np.abs(dp["df"]).max()
        px = lambda u: X0 + u * (X1 - X0)
        py = lambda v: YC + v * HH
        panel = RoundedRectangle(corner_radius=0.3, width=X1 - X0 + 1.5, height=2 * HH + 1.6, stroke_width=2, stroke_color=LINEA,
                                 fill_color=FONDO, fill_opacity=0.72).move_to([(X0 + X1) / 2, YC, 0]).set_z_index(2)
        cero = Line([X0, YC, 0], [X1, YC, 0], stroke_width=2, color=TENUE).set_opacity(0.5).set_z_index(3)
        for v in (-1, 1):
            self.add(DashedLine([X0, py(v), 0], [X1, py(v), 0], stroke_width=1.5, color=TENUE, dash_length=0.2).set_opacity(0.3).set_z_index(3))
        curva = VMobject().set_points_as_corners([[px(u), py(v), 0] for u, v in zip(xs, ys)])
        curva.set_stroke(color=CIAN, width=3.5, opacity=0.35).set_fill(opacity=0).set_z_index(4)
        eje = _texto("kHz", 24, "MEDIUM", TENUE).move_to([X0 - 0.45, py(1), 0]).set_z_index(3)
        et = _texto("frecuencia de ejemplo 437 MHz", 24, "MEDIUM", TENUE).move_to([(X0 + X1) / 2, YC - HH - 0.42, 0]).set_z_index(3)
        cur_viva, punto = VMobject().set_z_index(5), Dot(radius=0.16, color=CIAN).set_z_index(7)
        self.add(panel, cero, curva, eje, et, cur_viva, punto)

        # ── Cifra viva y pie con la época ────────────────────────────────────────────────────────────────
        cache = {}
        lectura = VGroup().set_z_index(8)
        self.add(lectura)

        def texto_en(cadena):
            if cadena not in cache:
                cache[cadena] = _texto(cadena, 64, "SEMIBOLD", PLATA[0]).move_to(ORIGIN)
            return cache[cadena]

        pie = _texto(f"{e['sello']['texto']} · cálculo SGP4 · CDMX", 22, "MEDIUM", TENUE, ancho_max=W * 0.9).move_to([0, -7.35, 0])
        self.add(pie.set_z_index(8))

        def mover(_m):
            u = (reloj.t % T) / T
            i = min(int(u * (n - 1) + 0.5), n - 1)
            o = min(suave(u / 0.07), suave((1 - u) / 0.07))
            sat.move_to(polar(tr["az"][i], tr["el"][i])).set_opacity(o)
            sat[0].set_opacity(0.18 * o)
            punto.move_to([px(xs[i]), py(ys[i]), 0]).set_opacity(o)
            if i > 1:
                ruta_viva.set_points_as_corners([polar(a, el_) for a, el_ in zip(tr["az"][:i + 1], tr["el"][:i + 1])])
                ruta_viva.set_stroke(color=CIAN, width=5, opacity=o).set_fill(opacity=0)
                cur_viva.set_points_as_corners([[px(a), py(b), 0] for a, b in zip(xs[:i + 1], ys[:i + 1])])
                cur_viva.set_stroke(color=CIAN, width=5.5, opacity=o).set_fill(opacity=0)
            else:
                ruta_viva.clear_points(); cur_viva.clear_points()
            df = dp["df"][i] / 1e3
            cad = f"{'+' if df >= 0 else '−'}{abs(df):.1f} kHz"
            t = texto_en(cad).copy().move_to([X1 - 1.9, py(0.62), 0])
            t.set_opacity(o if o > 0.02 else 0.0)
            lectura.become(VGroup(t))
            lectura.set_z_index(8)
        sat.add_updater(mover)
        self.wait(T)

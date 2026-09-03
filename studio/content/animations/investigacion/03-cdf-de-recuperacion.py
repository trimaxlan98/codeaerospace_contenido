"""Figura de paper: CDF empirica del tiempo de recuperacion, desde un CSV.

Una columna IEEE (3.5 in) a 300 dpi. Las 24 observaciones entran de
`studio/content/datos/ejemplo/recuperacion.csv` (tres semillas x ocho nodos);
DOS de ellas no llegaron a recuperarse y no se descartan: se cuentan en el pie,
porque una caida sin recuperacion es un hallazgo, no un dato que sobra.

    manim render -s --media_dir <dir> 03-cdf-de-recuperacion.py FiguraCDF
"""
import os
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import Scene, VGroup

import figura as fg

os.environ.setdefault("MS_DATOS_DIR",
                      "/workspace/studio/content/datos/ejemplo")

fg.Figura(tema="paper", columnas=1)


class FiguraCDF(Scene):
    def construct(self):
        fg.fondo(self)
        datos = fg.leer_csv("recuperacion.csv")
        crudo = datos["recovered_s"]
        muestras = crudo[np.isfinite(crudo)]
        sin_recuperar = int(np.sum(~np.isfinite(crudo)))

        techo = float(np.ceil(muestras.max() / 2.0) * 2.0)
        ax = fg.ejes_paper((0.0, techo), (0.0, 1.0),
                           "tiempo de recuperacion (s)", "F(x) empirica",
                           puntos_marca=5.5, decimales=(0, 2))
        curva = fg.cdf(ax, muestras, fg.color(0))

        ppu = fg.activa().puntos_por_unidad()
        grupo = VGroup(ax, curva)
        # Los percentiles se rotulan en un bloque arriba a la izquierda, que en
        # una CDF es la esquina vacia: colgados de su propia raya cruzaban la
        # escalera y se leian sobre ella.
        marcas = VGroup()
        for i, (p, col) in enumerate(((50, fg.color(1)), (95, fg.color(2)))):
            v = fg.percentil(muestras, p)
            grupo.add(fg.DashedLine(ax.c2p(v, 0.0), ax.c2p(v, p / 100.0),
                                    stroke_width=0.9, color=col,
                                    dash_length=0.05))
            marcas.add(fg.texto(f"p{p} = {v:.2f} s", 5.5, col))
        fg.pegar(marcas[1], marcas[0], fg.ABJ, 2.0 / ppu)
        fg.poner(marcas[1], [fg.caja(marcas[0])[0][0],
                             fg.centro(marcas[1])[1], 0.0], anclaje=fg.IZQ)
        fg.poner(marcas, ax.c2p(0.0, 1.0) + np.array([5.0 / ppu,
                                                      -4.0 / ppu, 0.0]),
                 anclaje=fg.IZQ + fg.ARR)
        grupo.add(marcas)

        pie = fg.texto(
            f"n = {muestras.size} recuperaciones de 3 semillas; "
            f"{sin_recuperar} caidas sin recuperar (no descartadas)",
            5.0, fg.tema()["apagado"])
        fg.pegar(pie, ax.rotulo_x, fg.ABJ, 2.0 / ppu)
        fg.poner(pie, [fg.centro(ax)[0], fg.centro(pie)[1], 0.0])

        todo = VGroup(grupo, pie)
        fg.encajar(todo, margen_pt=4.0, que="cdf", reservar_abajo_pt=8.0)
        self.add(todo, fg.sello(semilla="42/43/44",
                                extra="recuperacion.csv"))
        self.wait(1)


fg.sellar_escenas(globals())

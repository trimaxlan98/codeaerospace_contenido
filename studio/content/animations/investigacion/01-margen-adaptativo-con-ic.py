"""Figura de paper: margen adaptativo con IC95 % y sello de proveniencia.

Una columna IEEE (3.5 in) a 300 dpi. Sale como video en `ql` y como PNG con
`-s`; lo que se cita en el articulo es el PNG.

    manim render -s --media_dir <dir> 01-margen-adaptativo-con-ic.py FiguraMA

Todas las cifras se calculan aqui: la curva es
`ntn.margen_adaptativo(R_oraculo, R_best_const)` sobre recompensas sinteticas
deterministas de las tres semillas de la tesis (42/43/44), la banda es el
IC95 % por bootstrap SOBRE SEMILLAS (`ntn.banda_ic_por_x`) y el veredicto del
gate lo da `ntn.gate`, no una lectura a ojo de la curva.
"""
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import Scene, VGroup

import figura as fg
import ntn

fg.Figura(tema="paper", columnas=1)          # el lienzo se fija en el MODULO

SEMILLAS = ntn.SEMILLAS_TESIS                # (42, 43, 44)
CARGAS = np.arange(1, 11)                    # usuarios por celda


def _ma_por_semilla():
    """MA frente a la carga, una fila por semilla. Determinista.

    El oraculo (que ve el futuro) gana terreno segun sube la carga; la mejor
    politica constante se degrada. Las recompensas son NEGATIVAS —son coste—,
    que es justo el caso en el que el valor absoluto del denominador del MA
    decide el signo.
    """
    ma = np.zeros((len(SEMILLAS), CARGAS.size))
    for i, s in enumerate(SEMILLAS):
        rng = np.random.default_rng(s)
        r_best = -40.0 - 6.0 * CARGAS + rng.normal(0, 1.4, CARGAS.size)
        r_oraculo = (r_best * (1.0 - (0.06 + 0.028 * CARGAS))
                     + rng.normal(0, 1.1, CARGAS.size))
        ma[i] = ntn.margen_adaptativo(r_oraculo, r_best)
    return ma


class FiguraMA(Scene):
    def construct(self):
        fg.fondo(self)
        ma = _ma_por_semilla()
        media, lo, hi = ntn.banda_ic_por_x(ma, ci=0.95, semilla=42)

        figura_ma = ntn.curva_ma(CARGAS, media, umbral=ntn.UMBRAL_MA,
                                 ic=(lo, hi), xlabel="usuarios por celda",
                                 ylabel="margen adaptativo MA",
                                 puntos_marca=5.5)
        ax = figura_ma.ax
        ppu = fg.activa().puntos_por_unidad()

        g = ntn.gate({s: [float(ma[i, -1])] for i, s in enumerate(SEMILLAS)},
                     ntn.UMBRAL_MA, nombre="G3")
        rotulos = VGroup(
            fg.leyenda([("MA (media de 3 semillas)", fg.color(0)),
                        ("IC 95 % sobre semillas", fg.color(0), "banda")],
                       puntos=5.0),
            fg.texto(f"G3 con 10 usuarios: {g['veredicto']}   "
                     f"media {g['media']:.3f}   "
                     f"IC95 [{g['ic_lo']:.3f}, {g['ic_hi']:.3f}]",
                     5.0, fg.tema()["apagado"]))
        fg.pegar(rotulos[1], rotulos[0], fg.ABJ, 2.5 / ppu)
        fg.poner(rotulos[1], [fg.caja(rotulos[0])[0][0],
                              fg.centro(rotulos[1])[1], 0.0], anclaje=fg.IZQ)
        # Todo lo escrito vive DENTRO del cuadro: fuera compite con el sello.
        fg.poner(rotulos,
                 ax.c2p(float(CARGAS[0]), float(ax.y_range[1]))
                 + np.array([5.0 / ppu, -4.0 / ppu, 0.0]),
                 anclaje=fg.IZQ + fg.ARR)

        todo = VGroup(figura_ma, rotulos)
        fg.encajar(todo, margen_pt=4.0, que="figura MA",
                   reservar_abajo_pt=8.0)
        self.add(todo, fg.sello(semilla="42/43/44", extra="G3"))
        self.wait(1)


fg.sellar_escenas(globals())     # la marca de agua del canal NO va en un paper

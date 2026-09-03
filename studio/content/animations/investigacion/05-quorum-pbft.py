"""El quorum de PBFT: por que n=6 no compra nada y 2f+1 no siempre vale.

Demo de VIDEO (tema `marca`). Las tres fases, el numero de mensajes de cada
una y el quorum salen de `ntn.quorum_pbft(n)`; ninguna cifra esta escrita a
mano. La pieza cuenta las dos cosas que un diagrama tipico se salta:

  - `f = (n-1)//3` es DIVISION ENTERA: n=6 tolera lo mismo que n=4.
  - el quorum es ceil((n+f+1)/2), y solo vale 2f+1 cuando n = 3f+1. Con n=6,
    2f+1 = 3 no es ni mayoria: dos quorums de tres pueden no compartir ninguna
    replica correcta.
"""
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import FadeIn, FadeOut, Scene, VGroup

import figura as fg
import ntn

fg.Figura.pantalla(tema="marca")

N_REPLICAS = 7


class QuorumPbft(Scene):
    def construct(self):
        fg.fondo(self)
        ppu = fg.activa().puntos_por_unidad()
        titulo = fg.titulo(f"QUORUM PBFT CON {N_REPLICAS} REPLICAS",
                           puntos=15.0, arriba_pt=12.0)
        self.play(FadeIn(titulo, shift=0.15 * np.array([0.0, -1.0, 0.0])),
                  run_time=0.8)

        diag = ntn.diagrama_pbft(N_REPLICAS, puntos=11.0)
        fg.encajar(diag, margen_pt=10.0, que="diagrama PBFT",
                   reservar_arriba_pt=26.0, reservar_abajo_pt=6.0)
        fg.exigir_dentro(diag, margen_pt=6.0, que="diagrama PBFT")
        self.play(FadeIn(diag), run_time=1.2)
        self.wait(2.4)

        # El contraejemplo, con las cifras de la propia libreria.
        q6 = ntn.quorum_pbft(6)
        q4 = ntn.quorum_pbft(4)
        lineas = VGroup(*[
            fg.texto(t, 12.0, col) for t, col in (
                (f"n = 4  ->  f = {q4['f']}   quorum {q4['quorum']}   "
                 f"{q4['mensajes_total']} mensajes", fg.tema()["tinta"]),
                (f"n = 6  ->  f = {q6['f']}   quorum {q6['quorum']}   "
                 f"{q6['mensajes_total']} mensajes", fg.color(1)),
                ("dos replicas de mas no dan tolerancia",
                 fg.tema()["apagado"]),
                (f"y 2f+1 = {q6['quorum_2f1']} dejaria dos quorums",
                 fg.tema()["apagado"]),
                ("sin replica correcta en comun", fg.tema()["apagado"]))])
        for linea in lineas:
            fg.encoger_a_ancho(linea, margen_pt=12.0, minimo_pt=9.0,
                               que="linea del contraejemplo")
        for i in range(1, len(lineas)):
            fg.pegar(lineas[i], lineas[i - 1], fg.ABJ, 5.0 / ppu)
            fg.poner(lineas[i], [0.0, fg.centro(lineas[i])[1], 0.0])
        fg.poner(lineas, [0.0, -0.5, 0.0])
        fg.exigir_legible(lineas, minimo_pt=10.0, que="contraejemplo n=6")
        fg.exigir_dentro(lineas, margen_pt=8.0, que="contraejemplo n=6")

        self.play(FadeOut(diag), run_time=0.6)
        self.play(FadeIn(lineas), run_time=1.0)
        self.wait(2.6)
        self.play(FadeOut(lineas), FadeOut(titulo), run_time=0.8)
        self.wait(0.4)

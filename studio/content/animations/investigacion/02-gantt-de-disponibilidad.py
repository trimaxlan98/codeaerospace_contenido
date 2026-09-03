"""Figura de paper: Gantt de disponibilidad leido de un JSONL.

Doble columna IEEE (7.16 in) a 300 dpi. Los tramos y los eventos NO estan
escritos aqui: entran de `studio/content/datos/ejemplo/disponibilidad.jsonl`,
que es como llegara el `bus.jsonl` + `fault_log.jsonl` de una corrida del banco
(`pada-ntn-testbed`). Cambiar el archivo cambia la figura sin tocar el codigo.

    manim render -s --media_dir <dir> 02-gantt-de-disponibilidad.py FiguraGantt
"""
import os
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import Scene, VGroup

import figura as fg

# El directorio de datos se declara aqui, a la vista. En un proyecto de la app
# lo pone el runner (`MS_DATOS_DIR` -> `datos/` del job).
os.environ.setdefault("MS_DATOS_DIR",
                      "/workspace/studio/content/datos/ejemplo")

fg.Figura(tema="paper", columnas=2, alto_in=2.4)

COLOR_EVENTO = {"kill": "#CC79A7", "policy": "#0072B2", "clear": "#009E73"}


class FiguraGantt(Scene):
    def construct(self):
        fg.fondo(self)
        registros = fg.leer_jsonl("disponibilidad.jsonl")
        filas = fg.tramos_de_jsonl(registros)
        eventos = [(r["t"], r["etiqueta"],
                    COLOR_EVENTO.get(r["evento"], fg.color(1)))
                   for r in registros if "evento" in r]

        g = fg.gantt(filas, eventos=eventos, xlabel="tiempo de corrida (s)",
                     alto_fila_pt=10.0, puntos_fila=6.5, puntos_evento=5.5,
                     puntos_marca=6.0)

        # La cifra del pie se MIDE sobre los mismos tramos que se dibujan.
        t0, t1 = g.t_rango
        ventana = t1 - t0
        caido = sum(b - a for _, tramos in filas for a, b, e in tramos
                    if e == "down")
        sin_dato = sum(b - a for _, tramos in filas for a, b, e in tramos
                       if e == "hueco")
        disponible = 1.0 - (caido + sin_dato) / (ventana * len(filas))
        pie = fg.texto(
            f"ventana {ventana:.0f} s, {len(filas)} nodos: "
            f"{disponible * 100:.2f} % de nodo-segundo con evidencia de "
            f"servicio ({caido:.0f} s caido, {sin_dato:.0f} s sin dato)",
            5.5, fg.tema()["apagado"])

        leyenda = fg.leyenda([("up", fg.tema()["up"], "bloque"),
                              ("down", fg.tema()["down"], "bloque"),
                              ("sin evidencia", fg.tema()["hueco"], "bloque")],
                             puntos=5.5, columnas=3)
        fg.pegar(leyenda, g, fg.ABJ, 3.0 / fg.activa().puntos_por_unidad())
        fg.pegar(pie, leyenda, fg.ABJ, 2.5 / fg.activa().puntos_por_unidad())

        todo = VGroup(g, leyenda, pie)
        fg.encajar(todo, margen_pt=5.0, que="gantt", reservar_abajo_pt=8.0)
        self.add(todo, fg.sello(extra="disponibilidad.jsonl"))
        self.wait(1)


fg.sellar_escenas(globals())

"""Divulgacion (20-30 s), v2 -- casi sin texto: el ciclo PADA y el gate G1.

Rehecho a partir de PROMPT_MANIM_REHACER_VISUAL_2026-09-17.md (tesis-doctorado
-6g): la v1 (commit anterior de esta rama) tenia titulo, subtitulo, un
statement completo ("SE VALIDA EN UN GEMELO DIGITAL / antes de tocar la red
real"), dos lineas de formula/veredicto y un cierre de dos lineas -- "texto
de figura de paper, no de video" (feedback textual del doctorando). Esta
version NO tiene titulo, subtitulo NI statements: solo los rotulos que son el
CONTENIDO del propio dibujo (los cuatro nombres del lazo PADA, los numeros de
los ejes, "G1 PASA" como rotulo minimo en el punto que cruza el umbral) --
igual que los numeros de un eje no cuentan como "texto explicativo" en una
figura de paper.

Lo nuevo respecto de la v1, con primitivas que YA existian y no se habian
usado:

  - `particulas.materializar` / `Desintegrar`: los cuatro bloques del lazo
    aparecen como polvo que converge (no `FadeIn`) y el lazo entero se
    disuelve para dar paso a la curva de MA (no `FadeOut`).
  - `bloques.flujo()` recorre el ciclo TRES veces, con un SEGUNDO destello a
    medio ciclo del primero (`AnimationGroup(..., lag_ratio=0.5)` dentro del
    bucle): un lazo se siente ciclico cuando dos cosas lo recorren a la vez,
    no con una sola pasada.
  - Un punto brillante (`brillo.punto_brillante`) sube por la curva de MA
    mientras esta se traza (`Create`), en vez de aparecer ya dibujada con
    dos lineas de texto explicando el veredicto al lado.
  - Una fila de compuertas (G0-G3): circulos llenos para las que pasaron,
    uno solo con contorno para G3 (desbloqueada, sin correr) -- el estado se
    lee en el relleno, no en una frase.

Ninguna cifra cambio respecto de la v1 (ver GUIA_CIFRAS.md de esta carpeta,
esa tabla sigue valiendo): la sensibilidad 1/5/10/30 episodios -> MA
0.199/0.288/0.307/0.318 sigue citada de TEOREMA_MARGEN_ADAPTATIVO.md, el
umbral y el veredicto de G1 siguen citados de GATES.md, y el estado de
G0-G2b/G3 tambien. El par [0.095, 0.318] SI se quito de esta version (ya no
hay sitio para una cifra que necesita una frase para explicarse sin texto):
sigue documentado en GUIA_CIFRAS.md si se quiere recuperar como rotulo aparte.

    manim render -qh --media_dir media 07-pada-gemelo-digital.py PadaGemeloDigital
"""
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import (AnimationGroup, Circle, Create, FadeIn, FadeOut, Indicate,
                   Scene, UpdateFromAlphaFunc, VGroup, linear)

import bloques
import brillo
import figura as fg
import ntn
import particulas

fg.Figura.pantalla(tema="marca")

RADIO = 2.35
# 1/5/10/30 episodios -> MA, y el umbral de la compuerta G1 (citados, no
# recalculados: ver GUIA_CIFRAS.md).
EPISODIOS = np.array([1.0, 5.0, 10.0, 30.0])
MA_SENSIBILIDAD = np.array([0.199, 0.288, 0.307, 0.318])
UMBRAL_G1 = ntn.UMBRAL_MA               # 0.25
GATES = (("G0", True), ("G1", True), ("G2a", True), ("G2b", True), ("G3", False))


class PadaGemeloDigital(Scene):
    def construct(self):
        fg.fondo(self)
        ppu = fg.activa().puntos_por_unidad()

        # El chip de aviso editorial va PRIMERO y SOLO, en su propio respiro:
        # el lienzo de video es fisicamente chico (2 in de alto, fijo por
        # `Figura.pantalla`) y un chip fijo en una esquina durante todo el
        # clip se montaba sobre el lazo PADA y sobre la curva de MA (medido
        # en la v1, tres solapes distintos).
        chip = fg.etiqueta("EN DESARROLLO - TESIS DOCTORAL IPN", puntos=11.0)
        fg.poner(chip, [0.0, 0.0, 0.0])
        fg.exigir_dentro(chip, margen_pt=10.0, que="chip de desarrollo")
        self.play(FadeIn(chip, scale=1.05), run_time=0.6)
        self.wait(1.1)
        self.play(FadeOut(chip), run_time=0.5)

        # --- el lazo PADA: aparece como polvo, gira dos veces -------------
        colores = [fg.color(0), fg.color(1), fg.color(2), fg.color(3)]
        percibe = bloques.bloque("PERCEPCION", color=colores[0])
        analiza = bloques.bloque("ANALISIS", color=colores[1])
        decide = bloques.bloque("DECISION", color=colores[2])
        actua = bloques.bloque("ACCION", color=colores[3])
        percibe.move_to([0.0, RADIO, 0.0])
        analiza.move_to([RADIO, 0.0, 0.0])
        decide.move_to([0.0, -RADIO, 0.0])
        actua.move_to([-RADIO, 0.0, 0.0])
        bloques_pada = VGroup(percibe, analiza, decide, actua)

        self.play(particulas.materializar(percibe),
                  particulas.materializar(analiza),
                  particulas.materializar(decide),
                  particulas.materializar(actua), run_time=1.1)

        c_pa = bloques.conectar(percibe, analiza)
        c_ad = bloques.conectar(analiza, decide)
        c_da = bloques.conectar(decide, actua)
        c_ap = bloques.conectar(actua, percibe)
        conexiones = VGroup(c_pa, c_ad, c_da, c_ap)
        self.play(FadeIn(conexiones), run_time=0.5)

        # Dos destellos por vuelta, el segundo a medio ciclo del primero: asi
        # se ve un LAZO (algo que se persigue a si mismo), no un pipeline.
        for _ in range(3):
            self.play(AnimationGroup(
                bloques.flujo([c_pa, c_ad, c_da, c_ap], color=fg.color(0)),
                bloques.flujo([c_pa, c_ad, c_da, c_ap], color=fg.color(2)),
                lag_ratio=0.5))

        self.play(particulas.Desintegrar(bloques_pada, semilla=11),
                  FadeOut(conexiones), run_time=0.9)
        self.remove(bloques_pada, conexiones)

        # --- la curva de MA: un punto que sube mientras se traza ---------
        curva = ntn.curva_ma(EPISODIOS, MA_SENSIBILIDAD, umbral=UMBRAL_G1,
                             xlabel="episodios", ylabel="MA",
                             etiquetas=[int(e) for e in EPISODIOS],
                             puntos_marca=9.0, ancho_=9.8, alto_=3.6)
        fg.poner(curva, [0.0, 0.2, 0.0])
        fg.encajar(curva, margen_pt=10.0, que="curva MA",
                  reservar_arriba_pt=6.0, reservar_abajo_pt=6.0)
        fg.exigir_dentro(curva, margen_pt=6.0, que="curva MA")

        ax, linea_curva, linea_umbral, etiqueta_umbral = curva[0:4]
        self.play(Create(ax.marco, introducer=False),
                  FadeIn(ax.rejilla, ax.marcas_x, ax.marcas_y,
                         ax.rotulo_x, ax.rotulo_y), run_time=0.8)
        self.play(FadeIn(linea_umbral, etiqueta_umbral), run_time=0.4)

        xs_full = np.linspace(float(EPISODIOS[0]), float(EPISODIOS[-1]), 240)
        ys_full = np.interp(xs_full, EPISODIOS, MA_SENSIBILIDAD)
        puntos_curva = np.array([ax.c2p(float(x), float(y))
                                 for x, y in zip(xs_full, ys_full)])
        punto = brillo.punto_brillante(color=fg.color(1), radio=0.05)
        punto.move_to(puntos_curva[0])

        def _subir(mob, alpha):
            i = int(round(alpha * (len(puntos_curva) - 1)))
            mob.move_to(puntos_curva[i])

        self.add(punto)
        self.play(Create(linea_curva), UpdateFromAlphaFunc(punto, _subir),
                  run_time=3.0, rate_func=linear)

        etiqueta_g1 = fg.texto("G1 PASA", 11.0, fg.color(2))
        fg.poner(etiqueta_g1, puntos_curva[-1] + fg.ARR * (10.0 / ppu),
                anclaje=fg.DER + fg.ABJ)
        fg.exigir_dentro(etiqueta_g1, margen_pt=4.0, que="etiqueta G1")
        self.play(Indicate(punto, scale_factor=1.6, color=fg.color(2)),
                  FadeIn(etiqueta_g1), run_time=0.7)
        self.wait(1.3)
        self.play(FadeOut(curva), FadeOut(punto), FadeOut(etiqueta_g1),
                  run_time=0.7)

        # --- la fila de compuertas: el relleno ES el estado --------------
        paso = 1.55
        fichas = VGroup()
        for i, (nombre, pasada) in enumerate(GATES):
            x = (i - (len(GATES) - 1) / 2.0) * paso
            if pasada:
                circulo = Circle(radius=0.24, stroke_width=1.6,
                                 color=fg.color(0), fill_color=fg.color(0),
                                 fill_opacity=0.9)
            else:
                circulo = Circle(radius=0.24, stroke_width=1.6,
                                 color=fg.tema()["apagado"], fill_opacity=0.0)
            circulo.move_to([x, 0.5, 0.0])
            etiqueta_g = fg.texto(
                nombre, 8.0,
                fg.tema()["tinta"] if pasada else fg.tema()["apagado"])
            fg.pegar(etiqueta_g, circulo, fg.ABJ, 4.0 / ppu)
            fg.poner(etiqueta_g, [x, fg.centro(etiqueta_g)[1], 0.0])
            fichas.add(VGroup(circulo, etiqueta_g))
        fg.encajar(fichas, margen_pt=14.0, que="compuertas")
        fg.exigir_dentro(fichas, margen_pt=6.0, que="compuertas")
        halo_g3 = brillo.con_brillo(fichas[-1][0], color=fg.tema()["apagado"],
                                    capas=3, ancho_max=6, opacidad=0.18)

        self.play(AnimationGroup(*[FadeIn(f, scale=1.25) for f in fichas],
                                 lag_ratio=0.22), run_time=1.4)
        self.play(FadeIn(halo_g3), run_time=0.4)
        self.wait(1.4)
        self.play(FadeOut(fichas), FadeOut(halo_g3), run_time=0.6)

        self.wait(0.2)
        self.add(fg.sello(extra="MA citado de TEOREMA_MARGEN_ADAPTATIVO/GATES"))
        self.wait(1.3)

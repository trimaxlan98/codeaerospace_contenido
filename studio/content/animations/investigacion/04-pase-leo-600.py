"""El pase LEO-600 sobre una estacion: AOS, TCA, LOS, retardo y Doppler.

Demo de VIDEO (tema `marca`) de las mismas funciones que dibujan las figuras
del articulo: `Figura.pantalla()` cambia el lienzo de la columna IEEE a los
pixeles que pida la calidad del render, y el dibujo no se entera.

Ninguna cifra esta escrita: la geometria sale de `ntn.pase_leo` (orbita
circular a 600 km, inclinacion 53 grados, Tierra que gira) y el Doppler de
`ntn.resumen_doppler` sobre esa misma geometria.
"""
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import Create, FadeIn, FadeOut, Scene, VGroup

import figura as fg
import ntn

fg.Figura.pantalla(tema="marca")      # respeta -ql / -qh

ALTURA_KM = 600.0
INCLINACION_DEG = 53.0
LAT_GS, LON_GS = 19.43, -99.13        # Ciudad de Mexico
PORTADORA_HZ = 2.0e9                  # banda S


class PaseLeo600(Scene):
    def construct(self):
        fg.fondo(self)
        ppu = fg.activa().puntos_por_unidad()
        pase = ntn.pase_leo(ALTURA_KM, INCLINACION_DEG, LAT_GS, LON_GS)
        dop = ntn.resumen_doppler(pase, PORTADORA_HZ)

        titulo = fg.titulo("PASE LEO-600", puntos=16.0, arriba_pt=7.0)
        self.play(FadeIn(titulo, shift=0.15 * np.array([0.0, -1.0, 0.0])),
                  run_time=0.8)

        # --- momento 1: por donde pasa -------------------------------------
        mapa = ntn.traza_tierra(pase, alto_escena=fg.activa().frame_height * 0.6)
        fg.poner(mapa, [0.0, -0.4, 0.0])
        pie_mapa = fg.texto(
            f"h = {ALTURA_KM:.0f} km   i = {INCLINACION_DEG:.0f} grados   "
            f"estacion {LAT_GS:.2f} N  {abs(LON_GS):.2f} O",
            10.0, fg.tema()["apagado"])
        fg.encoger_a_ancho(pie_mapa, margen_pt=14.0, que="pie del mapa")
        fg.poner(pie_mapa, [0.0, -fg.activa().frame_height / 2
                            + 14.0 / ppu, 0.0], anclaje=fg.ABJ)
        self.play(FadeIn(mapa), FadeIn(pie_mapa), run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(mapa), FadeOut(pie_mapa), run_time=0.7)

        # --- momento 2: cuanto sube y cuanto dura --------------------------
        elev = ntn.curva_elevacion(pase, xlabel="tiempo desde AOS (s)",
                                   ylabel="elevacion (grados)",
                                   puntos_marca=10.0, ancho_=9.6, alto_=2.6)
        c = elev.cifras
        # Las cifras van DEBAJO del cuadro, en dos lineas cortas. Ancladas
        # dentro del cuadro (arriba a la derecha) cabian de sobra por ancho y
        # aun asi se salian por la izquierda: `exigir_dentro` mide la caja ya
        # COLOCADA, no solo su tamano.
        cifras = VGroup(*[
            fg.texto(t, 10.0, col) for t, col in (
                (f"elevacion maxima {c['elev_max_deg']:.1f} grados"
                 f"    duracion {c['duracion_s']:.0f} s", fg.color(1)),
                (f"AOS {pase['dist_aos_km']:.0f} km "
                 f"({c['retardo_aos_ms']:.2f} ms)    "
                 f"TCA {pase['dist_min_km']:.0f} km "
                 f"({c['retardo_min_ms']:.2f} ms)", fg.tema()["apagado"]))])
        for linea in cifras:
            fg.encoger_a_ancho(linea, margen_pt=10.0, minimo_pt=9.0,
                               que="cifra del pase")
        fg.pegar(cifras[1], cifras[0], fg.ABJ, 4.0 / ppu)
        fg.poner(cifras[1], [0.0, fg.centro(cifras[1])[1], 0.0])
        fg.pegar(cifras, elev, fg.ABJ, 5.0 / ppu)
        fg.poner(cifras, [0.0, fg.centro(cifras)[1], 0.0])

        bloque = VGroup(elev, cifras)
        fg.encajar(bloque, margen_pt=8.0, que="pase LEO",
                   reservar_arriba_pt=24.0, reservar_abajo_pt=4.0)
        fg.exigir_dentro(bloque, margen_pt=6.0, que="pase LEO")
        # `Create` sobre unos ejes enteros dibuja tambien los ROTULOS letra a
        # letra: a mitad de la animacion el eje X decia "tie". Se traza solo
        # el marco y lo escrito entra fundido.
        self.play(Create(elev.ax.marco, introducer=False),
                  FadeIn(elev.ax.rejilla, elev.ax.marcas_x, elev.ax.marcas_y,
                         elev.ax.rotulo_x, elev.ax.rotulo_y),
                  run_time=1.0)
        self.play(FadeIn(elev[1:]), run_time=1.2)
        # La pieza entro POR SUS HIJOS: hay que consolidarla antes de tratarla
        # como un solo mobject, o el FadeOut del grupo deja los hijos vivos.
        self.remove(*elev.get_family())
        self.add(elev)
        self.play(FadeIn(cifras), run_time=1.0)
        self.wait(2.0)

        # --- momento 3: el Doppler cambia de signo en el TCA ---------------
        self.play(FadeOut(cifras), FadeOut(elev), run_time=0.7)
        dopfig = ntn.curva_doppler(pase, PORTADORA_HZ,
                                   xlabel="tiempo desde AOS (s)",
                                   ylabel="Doppler (kilohercios)",
                                   puntos_marca=10.0, ancho_=9.6, alto_=2.6)
        # Dos lineas, no una: medido, la version de una sola linea pedia
        # 16.60 unidades en un frame de 14.23 y el guardian la encogia hasta
        # 7.6 pt, por debajo del suelo de este clip.
        pie_dop = VGroup(*[
            fg.texto(t_, 10.0, fg.color(2)) for t_ in (
                f"portadora {PORTADORA_HZ / 1e9:.0f} GHz    pico "
                f"{dop['df_max_hz'] / 1e3:.1f} kilohercios",
                f"es decir {dop['ppm_max']:.1f} partes por millon")])
        for linea in pie_dop:
            fg.encoger_a_ancho(linea, margen_pt=10.0, minimo_pt=9.0,
                               que="pie del Doppler")
        fg.pegar(pie_dop[1], pie_dop[0], fg.ABJ, 3.0 / ppu)
        fg.poner(pie_dop[1], [0.0, fg.centro(pie_dop[1])[1], 0.0])
        fg.pegar(pie_dop, dopfig, fg.ABJ, 4.0 / ppu)
        fg.poner(pie_dop, [0.0, fg.centro(pie_dop)[1], 0.0])
        bloque_dop = VGroup(dopfig, pie_dop)
        fg.encajar(bloque_dop, margen_pt=8.0, que="Doppler",
                   reservar_arriba_pt=24.0, reservar_abajo_pt=4.0)
        fg.exigir_dentro(bloque_dop, margen_pt=6.0, que="Doppler")

        self.play(Create(dopfig.ax.marco, introducer=False),
                  FadeIn(dopfig.ax.rejilla, dopfig.ax.marcas_x,
                         dopfig.ax.marcas_y, dopfig.ax.rotulo_x,
                         dopfig.ax.rotulo_y, dopfig.ax.linea_cero),
                  run_time=1.0)
        self.play(FadeIn(dopfig[1:]), run_time=1.0)
        self.remove(*dopfig.get_family())
        self.add(dopfig)
        self.play(FadeIn(pie_dop), run_time=0.8)
        self.wait(2.2)
        self.play(FadeOut(pie_dop), FadeOut(dopfig), FadeOut(titulo),
                  run_time=0.8)
        self.wait(0.4)

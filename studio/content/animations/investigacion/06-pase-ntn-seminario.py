"""Divulgacion (20-30 s): un pase LEO sobre una estacion, la red que no
siempre esta ahi.

Para el seminario de divulgacion de tesis (25-nov-2026), NO para el curso.
Version corta de `04-pase-leo-600.py`: mismo `ntn.pase_leo`, mismo tema
`marca`, pero sin el tramo de Doppler y con un cierre de una sola linea que
es el mensaje que pide el guion del seminario.

Escenario: LEO-600 (`ntn.ALTURA_LEO600_KM`, inclinacion 53 grados), el banco
de pruebas de la tesis (`pada-ntn-testbed`), NO la configuracion de
NTNEnv-v2 (que usa 550 km y no modela una orbita real: es un simulador
abstracto sin inclinacion, ver GUIA_CIFRAS.md de esta carpeta). Por eso se
rotula "escenario ilustrativo" en pantalla en vez de nombrar a NTNEnv-v2.

Ninguna cifra esta escrita a mano: la geometria del pase sale de
`ntn.pase_leo` y la fraccion de la orbita en contacto se calcula aqui mismo
como `duracion_s / periodo_s` del propio pase (no es el ~1 % medido con SGP4
real que reporta `visibility_omm.py` en el repo de tesis para un caso de
estudio a ~400 km: esa cifra vive en otro codigo, no se reproduce aqui).

    manim render -qh --media_dir media 06-pase-ntn-seminario.py PaseNtnSeminario
"""
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import Create, FadeIn, FadeOut, Scene, VGroup

import figura as fg
import ntn

fg.Figura.pantalla(tema="marca")      # 1920x1080 en -qh, respeta -ql al iterar

ALTURA_KM = ntn.ALTURA_LEO600_KM      # 600.0 -- banco de pruebas, no NTNEnv-v2
INCLINACION_DEG = 53.0
LAT_GS, LON_GS = 19.43, -99.13        # Ciudad de Mexico


class PaseNtnSeminario(Scene):
    def construct(self):
        fg.fondo(self)
        ppu = fg.activa().puntos_por_unidad()
        pase = ntn.pase_leo(ALTURA_KM, INCLINACION_DEG, LAT_GS, LON_GS)
        fraccion_orbita = pase["duracion_s"] / pase["periodo_s"]

        titulo = fg.titulo("UN PASE SOBRE LA ESTACION", puntos=17.0,
                           arriba_pt=8.0)
        subt = fg.texto("escenario ilustrativo: LEO-600, banco de pruebas "
                        "de la tesis (no NTNEnv-v2)", 9.0, fg.tema()["apagado"])
        fg.encoger_a_ancho(subt, margen_pt=14.0, que="subtitulo")
        fg.pegar(subt, titulo, fg.ABJ, 5.0 / ppu)
        self.play(FadeIn(titulo, shift=0.15 * np.array([0.0, -1.0, 0.0])),
                  FadeIn(subt), run_time=0.9)
        self.wait(0.5)

        # --- momento 1: por donde pasa (mapa) -------------------------------
        mapa = ntn.traza_tierra(pase, alto_escena=fg.activa().frame_height * 0.55)
        fg.poner(mapa, [0.0, -0.5, 0.0])
        pie_mapa = fg.texto(
            f"h = {ALTURA_KM:.0f} km   i = {INCLINACION_DEG:.0f} grados   "
            f"estacion {LAT_GS:.2f} N  {abs(LON_GS):.2f} O",
            10.5, fg.tema()["apagado"])
        fg.encoger_a_ancho(pie_mapa, margen_pt=14.0, que="pie del mapa")
        fg.poner(pie_mapa, [0.0, -fg.activa().frame_height / 2
                            + 16.0 / ppu, 0.0], anclaje=fg.ABJ)
        self.play(FadeIn(mapa), FadeIn(pie_mapa), run_time=1.1)
        self.wait(4.4)
        self.play(FadeOut(mapa), FadeOut(pie_mapa), run_time=0.6)

        # --- momento 2: cuanto sube y cuanto dura ---------------------------
        elev = ntn.curva_elevacion(pase, xlabel="tiempo desde AOS (s)",
                                   ylabel="elevacion (grados)",
                                   puntos_marca=11.0, ancho_=9.8, alto_=2.9)
        c = elev.cifras
        cifras = VGroup(*[
            fg.texto(t, 11.0, col) for t, col in (
                (f"elevacion maxima {c['elev_max_deg']:.1f} grados", fg.color(1)),
                (f"duracion del pase: {c['duracion_s']:.0f} s", fg.color(1)),
                (f"{100.0 * fraccion_orbita:.1f} % de una vuelta de "
                 f"{pase['periodo_s'] / 60.0:.0f} min", fg.tema()["apagado"]))])
        for linea in cifras:
            fg.encoger_a_ancho(linea, margen_pt=10.0, minimo_pt=9.0,
                               que="cifra del pase")
        for i in range(1, len(cifras)):
            fg.pegar(cifras[i], cifras[i - 1], fg.ABJ, 3.0 / ppu)
            fg.poner(cifras[i], [0.0, fg.centro(cifras[i])[1], 0.0])
        fg.pegar(cifras, elev, fg.ABJ, 5.0 / ppu)
        fg.poner(cifras, [0.0, fg.centro(cifras)[1], 0.0])

        bloque = VGroup(elev, cifras)
        fg.encajar(bloque, margen_pt=8.0, que="pase LEO",
                   reservar_arriba_pt=26.0, reservar_abajo_pt=4.0)
        fg.exigir_dentro(bloque, margen_pt=6.0, que="pase LEO")
        self.play(Create(elev.ax.marco, introducer=False),
                  FadeIn(elev.ax.rejilla, elev.ax.marcas_x, elev.ax.marcas_y,
                         elev.ax.rotulo_x, elev.ax.rotulo_y),
                  run_time=0.9)
        self.play(FadeIn(elev[1:]), run_time=1.1)
        self.remove(*elev.get_family())
        self.add(elev)
        self.play(FadeIn(cifras), run_time=0.9)
        self.wait(4.6)
        self.play(FadeOut(cifras), FadeOut(elev), run_time=0.6)

        # --- momento 3: el remate --------------------------------------
        remate = fg.texto("LA RED NO ESTA SIEMPRE AHI", 20.0, fg.color(0),
                          peso="BOLD")
        fg.encoger_a_ancho(remate, margen_pt=20.0, que="remate")
        fg.poner(remate, [0.0, 0.3, 0.0])
        pie_remate = fg.texto("ventana de contacto corta, geometria fija: "
                              "hay que planear alrededor de eso", 10.5,
                              fg.tema()["apagado"])
        fg.encoger_a_ancho(pie_remate, margen_pt=16.0, que="pie del remate")
        fg.pegar(pie_remate, remate, fg.ABJ, 10.0 / ppu)
        fg.exigir_dentro(VGroup(remate, pie_remate), margen_pt=8.0,
                         que="remate")
        self.play(FadeIn(remate, scale=1.05), run_time=0.8)
        self.play(FadeIn(pie_remate), run_time=0.6)
        self.wait(2.6)
        self.play(FadeOut(remate), FadeOut(pie_remate), FadeOut(titulo),
                  FadeOut(subt), run_time=0.7)
        self.wait(0.3)
        self.add(fg.sello(extra="LEO-600 ilustrativo, determinista"))
        self.wait(1.3)

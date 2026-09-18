"""Divulgacion (20-30 s): el ciclo PADA y el margen adaptativo que lo valida.

Para el seminario de divulgacion de tesis (25-nov-2026), NO para el curso.
Dos piezas encadenadas:

  1. El ciclo cognitivo PADA (Percepcion, Analisis, Decision, Accion) en
     cuatro bloques de `bloques.py`, dispuesto en rombo porque `bloques.py`
     esta pensado para pipelines lineales y no trae layout circular (se
     reviso antes de escribir uno nuevo, regla de la casa): un rombo con
     `conectar()` en las cuatro aristas ya cierra el lazo sin helper nuevo.
  2. El margen adaptativo (`ntn.margen_adaptativo` / gate G1) como el
     instrumento que valida esa gobernanza en un gemelo digital ANTES de
     tocar la red real.

Ninguna cifra de la curva de sensibilidad esta inventada: es la serie
1/5/10/30 episodios -> MA 0.199/0.288/0.307/0.318 de
`02_TEORIA/TEOREMA_MARGEN_ADAPTATIVO.md` (tesis-doctorado-6g), monotona
creciente, verificada contra el archivo fuente el 2026-09-17 -- ver
GUIA_CIFRAS.md en esta misma carpeta para la procedencia exacta de cada
numero y por que NO se llama al bootstrap de `ntn.gate()` aqui (no hay
desglose por semilla de este barrido en concreto en este repo: el veredicto
"pasa" que se rotula es el de G1 en GATES.md, citado, no recalculado).

PADA, el margen adaptativo y "NTNEnv-v2" son aportes de la tesis SIN
validar a escala (regla editorial del proyecto de curso "Satelites e IA",
que aplica aqui tal cual): el chip `fg.etiqueta()` se muestra al abrir el
clip, antes del rombo. NO queda pegado en pantalla durante todo el tramo:
el lienzo de video es fisicamente chico (2 in de alto, fijo por
`Figura.pantalla`) y un chip fijo en una esquina se montaba sobre el
titulo, sobre PERCEPCION y sobre la curva de MA en las tres etapas
siguientes (medido en el -ql, tres solapes distintos, corregido).

    manim render -qh --media_dir media 07-pada-gemelo-digital.py PadaGemeloDigital
"""
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import FadeIn, FadeOut, Scene, VGroup

import bloques
import figura as fg
import ntn

fg.Figura.pantalla(tema="marca")

RADIO = 2.35
# 1/5/10/30 episodios -> MA, y el umbral de la compuerta G1 (ambos citados,
# no recalculados: ver GUIA_CIFRAS.md).
EPISODIOS = np.array([1.0, 5.0, 10.0, 30.0])
MA_SENSIBILIDAD = np.array([0.199, 0.288, 0.307, 0.318])
UMBRAL_G1 = ntn.UMBRAL_MA               # 0.25
MA_PAR = (0.095, 0.318)                 # [MA_dec inferior, MA envolvente]


def _lineas(textos, puntos, color_, margen_pt=16.0, minimo_pt=9.0,
           hueco_pt=2.5):
    """Varias lineas CORTAS apiladas: el lienzo de video es fisicamente
    pequeno (2 in de alto, fijo por `Figura.pantalla`) y una sola frase larga
    se encoge por debajo del suelo de legibilidad antes de caber a lo ancho
    (medido: 'el margen adaptativo: cuanto...' a 9.5 pt bajaba a 4.4 pt)."""
    grupo = VGroup(*[fg.texto(t, puntos, color_) for t in textos])
    for linea in grupo:
        fg.encoger_a_ancho(linea, margen_pt=margen_pt, minimo_pt=minimo_pt,
                           que=f"linea '{linea.text}'")
    for i in range(1, len(grupo)):
        fg.pegar(grupo[i], grupo[i - 1], fg.ABJ, hueco_pt / fg.activa()
                .puntos_por_unidad())
        fg.poner(grupo[i], [0.0, fg.centro(grupo[i])[1], 0.0])
    return grupo


class PadaGemeloDigital(Scene):
    def construct(self):
        fg.fondo(self)
        ppu = fg.activa().puntos_por_unidad()

        titulo = fg.titulo("PADA", puntos=20.0, arriba_pt=8.0)
        subt = fg.texto("el ciclo cognitivo de la gobernanza autonoma",
                        10.0, fg.tema()["apagado"])
        fg.pegar(subt, titulo, fg.ABJ, 5.0 / ppu)
        self.play(FadeIn(titulo, shift=0.15 * np.array([0.0, -1.0, 0.0])),
                  FadeIn(subt), run_time=0.9)

        # El chip se muestra UNA vez, centrado, en su propio respiro: el
        # lienzo de video es fisicamente chico (2 in de alto, fijo) y
        # pegarlo arriba a la derecha lo montaba sobre el titulo y el
        # subtitulo (medido: se solapaban en el -ql). PADA y el margen
        # adaptativo son aportes sin validar a escala; este aviso cubre
        # las dos piezas del clip.
        chip = fg.etiqueta("EN DESARROLLO - TESIS DOCTORAL IPN", puntos=11.0)
        fg.poner(chip, [0.0, 0.0, 0.0])
        fg.exigir_dentro(chip, margen_pt=10.0, que="chip de desarrollo")
        self.play(FadeIn(chip, scale=1.05), run_time=0.6)
        self.wait(1.3)
        # El titulo, el subtitulo y el chip se despejan ANTES del rombo: se
        # quedaban en pantalla todo el clip y quedaban detras (y encima) de
        # PERCEPCION, del texto del gemelo digital y de la curva de MA —
        # medido en el -ql, tres solapes distintos. El aviso ya se dio.
        self.play(FadeOut(chip), FadeOut(titulo), FadeOut(subt), run_time=0.6)

        # --- el rombo PADA ---------------------------------------------
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

        c_pa = bloques.conectar(percibe, analiza)
        c_ad = bloques.conectar(analiza, decide)
        c_da = bloques.conectar(decide, actua)
        c_ap = bloques.conectar(actua, percibe)
        conexiones = VGroup(c_pa, c_ad, c_da, c_ap)

        self.play(FadeIn(bloques_pada), run_time=0.8)
        self.play(FadeIn(conexiones), run_time=0.5)
        for _ in range(2):
            self.play(bloques.flujo([c_pa, c_ad, c_da, c_ap]))
        self.wait(0.6)

        etiqueta_ciclo = _lineas(
            ("percibe la red, analiza el estado,",
             "decide una politica, actua -- y vuelve a percibir"),
            9.5, fg.tema()["apagado"], margen_pt=18.0)
        fg.poner(etiqueta_ciclo, [0.0, -fg.activa().frame_height / 2
                                  + 16.0 / ppu, 0.0], anclaje=fg.ABJ)
        self.play(FadeIn(etiqueta_ciclo), run_time=0.6)
        self.wait(1.1)
        self.play(FadeOut(bloques_pada), FadeOut(conexiones),
                  FadeOut(etiqueta_ciclo), run_time=0.6)

        # --- el gemelo digital -------------------------------------------
        gemelo = fg.texto("SE VALIDA EN UN GEMELO DIGITAL", 16.0, fg.color(0),
                          peso="BOLD")
        gemelo2 = fg.texto("antes de tocar la red real", 13.0,
                           fg.tema()["tinta"])
        fg.encoger_a_ancho(gemelo, margen_pt=18.0, que="gemelo digital")
        fg.encoger_a_ancho(gemelo2, margen_pt=18.0, que="gemelo digital (2)")
        fg.poner(gemelo, [0.0, 0.5, 0.0])
        fg.pegar(gemelo2, gemelo, fg.ABJ, 8.0 / ppu)
        self.play(FadeIn(gemelo, scale=1.05), run_time=0.7)
        self.play(FadeIn(gemelo2), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(gemelo), FadeOut(gemelo2), run_time=0.6)

        # --- el margen adaptativo: el instrumento de esa validacion ------
        # Las cuatro piezas se apilan relativas entre si y se ESCALAN juntas
        # con `encajar` (como en 01-margen-adaptativo-con-ic.py): apilarlas
        # con offsets en puntos desde un ancla absoluta, sin encajar, se salia
        # del lienzo por abajo -7.78 contra un limite de -3.56 (medido).
        pie2 = _lineas(("el margen adaptativo:",
                       "cuanto se gana, como maximo, por adaptarse"),
                      10.0, fg.tema()["apagado"])
        fg.poner(pie2, [0.0, 0.0, 0.0])

        curva = ntn.curva_ma(EPISODIOS, MA_SENSIBILIDAD, umbral=UMBRAL_G1,
                             xlabel="episodios (1 a 30)",
                             ylabel="margen adaptativo MA",
                             puntos_marca=11.0, ancho_=9.6, alto_=3.0)
        fg.pegar(curva, pie2, fg.ABJ, 10.0 / ppu)
        fg.poner(curva, [0.0, fg.centro(curva)[1], 0.0])

        veredicto = _lineas(
            ("G1 (IC95 % sobre semillas 42/43/44):",
             f"MA = {MA_SENSIBILIDAD[-1]:.3f} >= {UMBRAL_G1:.2f} -> PASA"),
            10.5, fg.color(1))
        fg.pegar(veredicto, curva, fg.ABJ, 12.0 / ppu)
        fg.poner(veredicto, [0.0, fg.centro(veredicto)[1], 0.0])

        par = _lineas(
            (f"se reporta el par [{MA_PAR[0]:.3f}, {MA_PAR[1]:.3f}]:",
             "minimo demostrado (G2b), envolvente estimada (G1)"),
            9.5, fg.tema()["apagado"])
        fg.pegar(par, veredicto, fg.ABJ, 8.0 / ppu)
        fg.poner(par, [0.0, fg.centro(par)[1], 0.0])

        bloque_ma = VGroup(pie2, curva, veredicto, par)
        fg.encajar(bloque_ma, margen_pt=10.0, que="bloque del margen",
                  reservar_arriba_pt=6.0, reservar_abajo_pt=6.0)
        fg.exigir_dentro(bloque_ma, margen_pt=6.0, que="bloque del margen")

        self.play(FadeIn(pie2), run_time=0.6)
        self.play(FadeIn(curva), run_time=1.1)
        self.wait(1.3)
        self.play(FadeIn(veredicto), run_time=0.7)
        self.wait(1.4)
        self.play(FadeIn(par), run_time=0.6)
        self.wait(1.6)
        self.play(FadeOut(pie2), FadeOut(curva), FadeOut(veredicto),
                  FadeOut(par), run_time=0.7)

        # --- cierre, sin sobreclaim --------------------------------------
        cierre = _lineas(("compuertas G0 a G2b: aprobadas",
                         "G3 (50k episodios): desbloqueada, sin correr"),
                        10.5, fg.tema()["apagado"], margen_pt=18.0)
        fg.poner(cierre, [0.0, 0.3, 0.0])
        self.play(FadeIn(cierre), run_time=0.7)
        self.wait(1.6)
        self.play(FadeOut(cierre), run_time=0.7)
        self.wait(0.3)
        self.add(fg.sello(extra="MA citado de TEOREMA_MARGEN_ADAPTATIVO/GATES"))
        self.wait(1.3)

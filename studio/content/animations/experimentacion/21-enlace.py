import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from enlace import (COLOR_GANANCIA, COLOR_MARGEN, COLOR_PERDIDA, COLOR_RUIDO,
                    COLOR_SENAL, barra_margen, cascada_db, curva_fspl,
                    curva_shannon, escalera_modcod, frente_esferico,
                    nube_simbolos, patron_ganancia, piso_ruido, regla_db,
                    termometro_ruido)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoEnlace(Scene):
    """Demo de enlace.py: el idioma del decibelio, la potencia que apunta, la
    esfera que crece, la FSPL, el ruido y su temperatura, la cascada del
    presupuesto, el techo de Shannon con sus constelaciones y el margen que se
    come la lluvia.

    Todo es geometrico y determinista: mismo script, mismo render. Los
    localizadores (.punto_de, .nivel, .centro_de, .cima, .punta,
    .origen_polar) se leen de la geometria actual, y los NUMEROS (.db,
    .acumulado, .eficiencia, .valor) salen de la misma fuente que el dibujo.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Cerrar el enlace", font_size=28, color=COLOR_MARGEN)
        titulo.to_edge(UP, buff=0.22)
        self.add(titulo)

        # --- acto 1: el idioma y la potencia que apunta ---
        regla = regla_db(ancho=5.6, alto=0.8).move_to(UP * 1.5)
        self.play(FadeIn(regla), run_time=0.6)
        self.play(Indicate(regla.par(2), color=COLOR_MARGEN), run_time=0.6)

        centro = LEFT * 3.4 + DOWN * 1.2
        patron = patron_ganancia(0.0, escala=0.8).anclar_en(centro)
        self.play(Create(patron), run_time=0.6)
        self.play(Transform(patron, patron.con_ganancia(30.0)), run_time=0.7)
        self.play(FadeOut(regla), FadeOut(patron), run_time=0.4)

        # --- acto 2: la esfera que crece y lo que cuesta ---
        frente = frente_esferico(radios=(0.4, 0.8, 1.2), puntos=28)
        frente.move_to(LEFT * 3.6 + DOWN * 0.6)
        self.play(FadeIn(frente), run_time=0.6)

        fspl = curva_fspl(ancho=3.6, alto=1.8).move_to(RIGHT * 1.6 + DOWN * 0.5)
        self.play(FadeIn(fspl.ejes), Create(fspl.curvas), run_time=0.8)
        self.play(FadeIn(fspl.etiquetas), run_time=0.4)
        marca = Dot(fspl.punto_de(36000, 12.0), radius=0.06,
                    color=COLOR_MARGEN)
        valor = Text(f"{fspl.db(36000, 12.0):.0f} dB", font=FUENTE_HUD,
                     font_size=16, color=COLOR_MARGEN)
        valor.next_to(marca, DOWN, buff=0.16)
        self.play(FadeIn(marca), FadeIn(valor), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(VGroup(frente, fspl, marca, valor)), run_time=0.4)

        # --- acto 3: el ruido y su temperatura ---
        piso = piso_ruido(ancho=4.0, alto=1.6).move_to(LEFT * 2.4 + DOWN * 0.3)
        self.play(FadeIn(piso), run_time=0.6)
        self.play(Transform(piso, piso.con_nivel(0.62)), run_time=0.7)

        termo = termometro_ruido(150.0, alto=1.6, ancho=0.34)
        termo.move_to(RIGHT * 2.2 + DOWN * 0.2)
        self.play(FadeIn(termo), run_time=0.5)
        self.play(termo.a_temperatura(420.0), run_time=0.7)
        self.play(FadeOut(piso), FadeOut(termo), run_time=0.4)

        # --- acto 4: la cascada del presupuesto ---
        casc = cascada_db([("PIRE", 58.0), ("FSPL", -205.2), ("G/T", 13.2),
                           ("-k", 228.6)], ancho=5.0, alto=2.0)
        casc.move_to(DOWN * 0.5)
        self.play(FadeIn(casc[0]), run_time=0.3)
        self.play(LaggedStart(*[casc.aparecer(i) for i in range(4)],
                              lag_ratio=0.5), run_time=1.6)
        self.play(casc.aparecer_saldo(), run_time=0.5)
        saldo = Text(f"{casc.acumulado(-1):.1f} dBHz", font=FUENTE_HUD,
                     font_size=17, color=COLOR_MARGEN)
        saldo.next_to(casc, UP, buff=0.20)
        self.play(FadeIn(saldo), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(casc), FadeOut(saldo), run_time=0.4)

        # --- acto 5: el techo y los peldaños ---
        sh = curva_shannon(ancho=3.4, alto=1.8).move_to(RIGHT * 2.0
                                                        + DOWN * 0.4)
        self.play(FadeIn(sh.ejes), Create(sh.curva), run_time=0.7)
        self.play(sh.revelar_prohibida(), run_time=0.4)
        modcods = (("QPSK 1/2", 1.0, 0.99), ("8PSK 3/4", 7.91, 2.23),
                   ("16APSK 3/4", 10.21, 2.97))
        puntos = VGroup(*[Dot(sh.punto_modcod(s, b), radius=0.05,
                              color=COLOR_SENAL) for _, s, b in modcods])
        self.play(FadeIn(puntos), run_time=0.4)

        nube = nube_simbolos(orden=4, dispersion=0.05, escala=0.6)
        nube.move_to(LEFT * 4.4 + DOWN * 0.3)
        self.play(FadeIn(nube), run_time=0.4)
        self.play(Transform(nube, nube.con_orden(16)), run_time=0.6)

        esc = escalera_modcod(list(modcods), ancho=2.2, alto=1.4)
        esc.move_to(LEFT * 1.4 + DOWN * 0.4)
        self.play(FadeIn(esc), run_time=0.5)
        self.play(esc.mover_a(2), run_time=0.4)
        self.play(FadeOut(VGroup(sh, puntos, nube)), run_time=0.4)

        # --- acto 6: el margen, y la lluvia ---
        margen = barra_margen(margen_db=6.0, alto=1.6, ancho=0.34)
        margen.move_to(RIGHT * 2.6 + DOWN * 0.3)
        self.play(FadeIn(margen), run_time=0.5)
        self.play(margen.comer(8.0), run_time=0.7)
        self.play(esc.mover_a(0), run_time=0.4)
        self.play(margen.devolver(6.9), run_time=0.6)
        self.wait(0.6)

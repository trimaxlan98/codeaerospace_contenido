import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from naturaleza import (ANGULO_AUREO_DEG, COLOR_CONSTANTE, COLOR_EJE,
                        COLOR_QUIMICA,
                        COLOR_REGLA, COLOR_VIDA, OMEGA_PI_DEG, PHI,
                        TURING_MANCHAS, TURING_RAYAS, arbol_fractal,
                        campo_turing, curva_crecimiento, escalera_compuesta,
                        espiral_log, filotaxis, gato_dormido, gato_sentado,
                        imagen_helecho, imagen_turing, panal,
                        perimetro_por_area, rectangulos_fibonacci,
                        red_micelio, rio_meandro, tesela_unidad)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoNaturaleza(Scene):
    """Demo de naturaleza.py: filotaxis con su parastica, los cuadrados de
    Fibonacci, la espiral autosemejante, el helecho acumulandose, arbol y
    micelio, Turing manchas->rayas con el gato vestido, el rio que mide su
    sinuosidad, la escalera compuesta hacia e y el panal contra el cuadrado.

    Todo es determinista: mismo script, mismo render. Los numeros que se
    rotulan (sinuosidad, (1+1/n)^n, perimetros) salen de las piezas.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Matematicas en la naturaleza", font_size=26,
                      color=COLOR_CONSTANTE)
        titulo.to_edge(UP, buff=0.22)
        self.add(titulo)

        # --- acto 1: filotaxis y Fibonacci ---
        disco = filotaxis(320, escala=1.5).move_to(LEFT * 3.6 + DOWN * 0.4)
        self.play(disco.aparecer(run_time=1.2))
        self.play(Create(disco.parastica(21)), run_time=0.6)
        self.play(Transform(disco, disco.con_angulo(90.0)), run_time=0.7)

        fib = rectangulos_fibonacci(6, lado=0.16).move_to(RIGHT * 3.4
                                                          + DOWN * 0.4)
        self.play(FadeIn(fib), run_time=0.5)
        esp = espiral_log(vueltas=2.5, escala=1.3).move_to(RIGHT * 3.4
                                                           + DOWN * 0.4)
        self.play(Create(esp), run_time=0.7)
        copia, ang = esp.autosemejante(PHI)
        copia.set_opacity(0.5)
        self.add(copia)
        self.play(Rotate(copia, ang, about_point=esp.polo()), run_time=0.7)
        self.play(*[FadeOut(m) for m in (disco, fib, esp, copia)],
                  run_time=0.4)

        # --- acto 2: fractales que crecen ---
        marcos = VGroup()
        for n in (2_000, 60_000):
            helecho = imagen_helecho(n, res=(280, 420), alto_escena=4.2)
            helecho.move_to(LEFT * 4.2 + DOWN * 0.3)
            self.add(helecho)
            self.wait(0.35)
            if n != 60_000:
                self.remove(helecho)
        arbol = arbol_fractal(6, escala=0.85).move_to(DOWN * 0.4)
        for i in range(6):
            self.play(FadeIn(arbol.nivel(i)), run_time=0.16)
        red = red_micelio(4, escala=0.8).move_to(RIGHT * 4.0 + DOWN * 0.4)
        for i in range(4):
            self.play(FadeIn(red.anillo(i)), run_time=0.14)
        self.play(FadeOut(helecho), FadeOut(arbol), FadeOut(red),
                  run_time=0.4)

        # --- acto 3: Turing viste al gato ---
        campo_m = campo_turing(*TURING_MANCHAS, pasos=4000)
        img = imagen_turing(campo_m, alto_escena=3.4).move_to(LEFT * 3.6
                                                              + DOWN * 0.4)
        self.play(FadeIn(img), run_time=0.5)
        gato = gato_sentado(escala=1.15).move_to(RIGHT * 3.4 + DOWN * 0.5)
        campo_r = campo_turing(*TURING_RAYAS, pasos=4000)
        pelaje = imagen_turing(campo_r, color_fondo="#d9a05a",
                               color_tinta="#20160c", silueta=gato)
        self.play(FadeIn(gato), run_time=0.4)
        self.add(pelaje)
        self.wait(0.5)
        ovillo = gato_dormido(escala=0.8).move_to(RIGHT * 0.2 + DOWN * 1.6)
        self.play(FadeIn(ovillo), run_time=0.4)
        self.play(FadeOut(img), FadeOut(gato), FadeOut(pelaje),
                  FadeOut(ovillo), run_time=0.4)

        # --- acto 4: el rio, e y el panal ---
        rio = rio_meandro(35.0, ancho=8.0).move_to(UP * 1.1)
        self.play(Create(rio), run_time=0.6)
        tag = Text(f"S = {rio.sinuosidad():.2f}", font=FUENTE_HUD,
                   font_size=16, color=COLOR_CONSTANTE)
        tag.next_to(rio, DOWN, buff=0.15)
        self.add(tag)
        rio2 = rio.con_omega(OMEGA_PI_DEG)
        tag2 = Text(f"S = {rio2.sinuosidad():.2f}", font=FUENTE_HUD,
                    font_size=16, color=COLOR_CONSTANTE)
        self.play(Transform(rio, rio2), run_time=0.8)
        tag2.next_to(rio, DOWN, buff=0.15)
        self.play(Transform(tag, tag2), run_time=0.3)

        curva = curva_crecimiento(ancho=3.6, alto=2.0)
        curva.move_to(LEFT * 3.8 + DOWN * 2.0)
        self.play(FadeIn(curva), run_time=0.4)
        for n in (1, 4, 12):
            esc = escalera_compuesta(n, curva)
            v = Text(f"(1+1/{n})^{n} = {esc.valor_final():.2f}",
                     font=FUENTE_HUD, font_size=14, color=COLOR_QUIMICA)
            v.next_to(curva, DOWN, buff=0.12)
            self.add(esc, v)
            self.wait(0.3)
            if n != 12:
                self.remove(esc, v)

        abejas = panal(3, 4, lado=0.26).move_to(RIGHT * 3.6 + DOWN * 2.0)
        self.play(abejas.aparecer(run_time=0.8))
        t6 = tesela_unidad(6, area=0.5, color=COLOR_REGLA)
        t4 = tesela_unidad(4, area=0.5, color=COLOR_EJE)
        par = VGroup(t4, t6).arrange(RIGHT, buff=0.3).move_to(RIGHT * 3.6
                                                              + UP * 0.0)
        peri = Text(f"{perimetro_por_area(4):.2f} vs "
                    f"{perimetro_por_area(6):.2f}", font=FUENTE_HUD,
                    font_size=14, color=COLOR_VIDA)
        peri.next_to(par, DOWN, buff=0.12)
        self.play(FadeIn(par), FadeIn(peri), run_time=0.5)
        self.wait(0.6)

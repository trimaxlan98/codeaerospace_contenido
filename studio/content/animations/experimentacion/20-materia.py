import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from materia import (COLOR_ATOMO, COLOR_FALLA, COLOR_MAT, COLOR_OK,
                     curva_esfuerzo, curva_sn, grieta, mapa_ashby, par_atomos,
                     placa_con_ciclos, pozo_lennard_jones, red_atomica)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoMateria(Scene):
    """Demo de materia.py: el pozo de Lennard-Jones con su fondo, el par de
    atomos que se separa y vuelve, la red que se cizalla, las curvas
    esfuerzo-deformacion de metal y ceramico sobre los mismos ejes, el mapa de
    Ashby con el barrio de los compuestos, la curva S-N y una grieta creciendo
    sobre una placa con carga ciclica.

    Todo es geometrico y determinista: mismo script, mismo render. Los
    localizadores (.punto_de, .fondo, .punto_en, .burbuja) se leen de la
    geometria actual, asi que los puntos y los tags caen solos donde deben.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("La materia", font_size=28, color=COLOR_ATOMO)
        titulo.to_edge(UP, buff=0.22)
        self.add(titulo)

        # --- acto 1: el enlace y el pozo ---
        par = par_atomos(separacion=1.6, radio=0.26).move_to(UP * 1.55)
        pozo = pozo_lennard_jones(ancho=4.6, alto=2.4).move_to(DOWN * 1.15)
        punto = Dot(pozo.fondo(), radius=0.075, color=COLOR_MAT)
        punto.set_z_index(6)
        # Colgado de la linea de r0 y NO del punto: el punto se mueve, y
        # debajo de el vive la etiqueta "r0" del propio pozo.
        tag_r0 = Text("equilibrio", font=FUENTE_HUD, font_size=14,
                      color=COLOR_MAT).next_to(pozo.r0_linea, UP, buff=0.06)
        tag_r0.shift(RIGHT * 0.5)

        self.play(FadeIn(par.a), FadeIn(par.b), Create(par.resorte),
                  run_time=0.6)
        self.play(Create(pozo.ejes), FadeIn(pozo.etiquetas), run_time=0.4)
        self.play(Create(pozo.curva), run_time=0.9)
        self.play(Create(pozo.r0_linea), FadeIn(punto), FadeIn(tag_r0),
                  run_time=0.4)

        # El atomo derecho se aleja mientras el punto trepa la pared derecha
        # del pozo: la misma alfa mueve las dos piezas.
        for _ in range(2):
            self.play(
                UpdateFromAlphaFunc(
                    par, lambda m, a: m.separar(1.6 + 0.85 * np.sin(np.pi * a))),
                UpdateFromAlphaFunc(
                    punto,
                    lambda m, a: m.move_to(
                        pozo.punto_de(1.0 + 0.42 * np.sin(np.pi * a)))),
                run_time=0.85, rate_func=linear)
        self.play(FadeOut(VGroup(par, pozo, punto, tag_r0)), run_time=0.35)

        # --- acto 2: la red que cizalla y las curvas de dos familias ---
        red = red_atomica(filas=4, columnas=6, paso=0.6)
        red.move_to(LEFT * 3.55 + DOWN * 0.35)
        metal = curva_esfuerzo("metal", ancho=4.2, alto=2.4)
        metal.move_to(RIGHT * 2.5 + DOWN * 0.35)
        tag_metal = Text("METAL", font=FUENTE_HUD, font_size=15,
                         color=COLOR_MAT).next_to(metal, UP, buff=0.10)

        self.play(FadeIn(red.atomos), Create(red.resortes), run_time=0.7)
        self.play(Create(metal.ejes), FadeIn(metal.etiquetas),
                  FadeIn(tag_metal), run_time=0.4)
        self.play(
            UpdateFromAlphaFunc(
                red, lambda m, a: m.cizallar(0.34 * np.sin(2.0 * np.pi * a))),
            Create(metal.curva), run_time=1.3, rate_func=linear)

        marca = Dot(metal.punto_en(0.0), radius=0.07, color=COLOR_ATOMO)
        marca.set_z_index(6)
        self.play(*metal.abrir_zona(), FadeIn(marca), run_time=0.5)
        self.play(UpdateFromAlphaFunc(
            marca, lambda m, a: m.move_to(metal.punto_en(a))),
            run_time=0.8, rate_func=linear)

        ceramico = curva_esfuerzo("ceramico", ancho=4.2, alto=2.4)
        ceramico.move_to(RIGHT * 2.5 + DOWN * 0.35)
        tag_ceramico = Text("CERAMICO", font=FUENTE_HUD, font_size=15,
                            color=COLOR_FALLA).next_to(ceramico, UP, buff=0.10)
        self.play(ReplacementTransform(metal, ceramico),
                  ReplacementTransform(tag_metal, tag_ceramico),
                  FadeOut(marca), run_time=0.7)
        self.play(Indicate(ceramico.marca_falla, color=COLOR_FALLA,
                           scale_factor=1.5), run_time=0.5)
        self.play(FadeOut(VGroup(red, ceramico, tag_ceramico)), run_time=0.35)

        # --- acto 3: el mapa de Ashby y la sentencia de la fatiga ---
        mapa = mapa_ashby(ancho=4.4, alto=2.8).move_to(LEFT * 3.3 + DOWN * 0.3)
        sn = curva_sn(ancho=3.9, alto=2.0).move_to(RIGHT * 3.0 + DOWN * 0.4)

        self.play(Create(mapa.ejes), FadeIn(mapa.etiquetas), run_time=0.35)
        self.play(LaggedStart(*[FadeIn(b) for b in mapa.grupo_burbujas],
                              lag_ratio=0.18), run_time=0.8)
        self.play(Create(mapa.diagonales), Create(sn.ejes),
                  FadeIn(sn.etiquetas), run_time=0.6)
        self.play(Indicate(mapa.burbuja("COMPUESTOS"), color=COLOR_MAT,
                           scale_factor=1.12), Create(sn.curva), run_time=0.8)

        vida = Dot(sn.punto_en(0.08), radius=0.07, color=COLOR_ATOMO)
        vida.set_z_index(6)
        self.play(FadeIn(vida), Create(sn.limite), run_time=0.4)
        self.play(UpdateFromAlphaFunc(
            vida, lambda m, a: m.move_to(sn.punto_en(0.08 + 0.9 * a))),
            Indicate(sn.limite, color=COLOR_OK, scale_factor=1.0),
            run_time=0.9, rate_func=linear)
        self.play(FadeOut(VGroup(mapa, sn, vida)), run_time=0.35)

        # --- acto 4: la placa que muere de mil ciclos ---
        placa = placa_con_ciclos(ancho=3.0, alto=1.7).move_to(DOWN * 0.5)
        self.play(FadeIn(placa.placa), GrowFromCenter(placa.flechas),
                  run_time=0.5)
        self.play(Indicate(placa.flechas, color=COLOR_FALLA,
                           scale_factor=1.12), run_time=0.5)

        fisura = grieta(largo=1.15, dientes=8).rotate(PI / 2.0)
        fisura.move_to(placa.placa.get_bottom() + UP * 0.575 + RIGHT * 0.35)
        fisura.set_z_index(5)
        tag_grieta = Text("grieta", font=FUENTE_HUD, font_size=14,
                          color=COLOR_FALLA).next_to(placa, RIGHT, buff=0.22)
        self.play(Create(fisura), FadeIn(tag_grieta), run_time=1.1)
        self.wait(0.6)

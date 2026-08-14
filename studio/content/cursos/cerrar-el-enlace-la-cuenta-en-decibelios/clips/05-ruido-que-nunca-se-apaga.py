class Clip5(Scene):
    """5 - El ruido que nunca se apaga. El piso de ruido sube hasta casi
    tapar una señal que no se mueve; el termometro de temperatura de sistema
    acompaña, y el clip cierra con la figura de merito G/T. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))

        titulo = titulo_curso("El ruido que nunca se apaga")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- momento: una señal comoda sobre el ruido ---------------------
        piso = piso_ruido(ancho=5.0, alto=2.0, nivel=0.22, cima_rel=0.86)
        piso.move_to(LEFT * 1.2 + UP * 0.15)
        self.play(FadeIn(piso.ejes), run_time=0.5)
        self.play(Create(piso.ruido), run_time=1.1)
        self.play(Create(piso.senal), run_time=0.9)
        self.wait(0.6)

        rot.mostrar(pie_curso("Todo lo que tiene temperatura emite ruido: tu "
                              "antena, el cielo, tu propio receptor."),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)

        # --- momento: sube el suelo, no baja la señal ---------------------
        # El pie entra ANTES del transform que ilustra.
        rot.mostrar(pie_curso("La señal no empeoró: subió el suelo."),
                    zona="abajo", run_time=0.5)

        alto = piso.con_nivel(0.70)
        self.play(Transform(piso, alto), run_time=1.6)
        self.wait(4.8)

        # --- momento: el ruido tiene temperatura --------------------------
        termo = termometro_ruido(T_SIS_K, t_max=600.0, alto=2.0, ancho=0.40)
        termo.move_to(RIGHT * 4.3 + UP * 0.25)
        self.play(FadeIn(termo, shift=0.15 * LEFT), run_time=0.8)
        self.wait(1.2)

        rot.mostrar(formula_pie(r"N_0 = k\,T"), zona="abajo", run_time=0.5)
        self.wait(3.0)

        self.play(termo.a_temperatura(400.0), run_time=1.2)
        self.wait(3.6)

        # --- momento: la figura de merito del receptor --------------------
        rot.mostrar(pie_curso("Por eso un receptor no se juzga por su "
                              "ganancia, sino por ganancia entre "
                              "temperatura."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        # G arriba en verde (suma), T abajo en violeta (ruido): la fraccion
        # dice visualmente de que lado esta cada cosa.
        arriba = Text("G", font=FUENTE_DISPLAY, font_size=34,
                      color=C_GANANCIA)
        raya = Line(LEFT * 0.28, RIGHT * 0.28, stroke_width=2.4, color=C_TENUE)
        abajo = Text("T", font=FUENTE_DISPLAY, font_size=34, color=C_RUIDO)
        cociente = VGroup(arriba, raya, abajo).arrange(DOWN, buff=0.12)
        valor = Text(f"= {GT_DB:.1f} dB/K", font=FUENTE_HUD, font_size=22,
                     color=C_MARGEN)
        valor.next_to(cociente, RIGHT, buff=0.28)
        grupo = VGroup(cociente, valor).move_to(DOWN * 1.9)

        self.play(FadeIn(cociente, scale=1.15), run_time=0.8)
        self.play(FadeIn(valor, shift=0.12 * LEFT), run_time=0.6)
        self.wait(4.8)

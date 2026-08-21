class Clip2(Scene):
    """5.1.2 - CDMA: los codigos de Walsh son ortogonales (producto
    punto 0 MEDIDO); dos usuarios suman sus 64 chips en el MISMO
    tiempo-frecuencia y la onda se ve caotica. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("CDMA: hablar a la vez")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: cada usuario tiene un codigo ------------------------
        rot.mostrar(pie_curso("¿Y si nadie separa ni el tiempo ni la "
                              "frecuencia? Cada usuario tiene, en "
                              "cambio, un CÓDIGO."),
                    zona="abajo", run_time=0.5)
        w1 = onda(T_W1, Y_W1, rango_y=(-1.5, 1.5), ancho=5.6, alto=1.1,
                  color=C_BIT)
        w1.move_to(UP * 2.35 + LEFT * 1.0)
        et_w1 = tag_junto(w1, "código 1, usuario 1", direccion=DOWN,
                          buff=0.12, font_size=17, color=C_BIT)
        w2 = onda(T_W2, Y_W2, rango_y=(-1.5, 1.5), ancho=5.6, alto=1.1,
                  color=C_COD)
        w2.move_to(UP * 0.45 + LEFT * 1.0)
        et_w2 = tag_junto(w2, "código 2, usuario 2", direccion=DOWN,
                          buff=0.12, font_size=17, color=C_COD)
        self.play(FadeIn(w1), FadeIn(et_w1), run_time=0.9)
        self.play(FadeIn(w2), FadeIn(et_w2), run_time=0.9)
        self.wait(4.4)

        # --- momento: ortogonalidad medida ---------------------------------
        rot.mostrar(pie_curso("Ocho chips, ±1: multiplicados y sumados, "
                              "los dos códigos dan CERO."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(
            tag_hud(f"W1 . W2 = {fmt(DOT_W1_W2, 1)}"),
            tag_hud(f"W1 . W1 = {fmt(DOT_W1_W1, 1)}"))
        self.play(FadeIn(panel, shift=0.2 * LEFT), run_time=0.7)
        self.wait(5.2)

        # --- momento: los chips se suman ------------------------------------
        rot.mostrar(pie_curso("Cada bit, ±1, se ESTIRA por su código; "
                              "los dos flujos de chips se SUMAN en el "
                              "mismo tiempo y la misma frecuencia."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(w1), FadeOut(et_w1), FadeOut(w2), FadeOut(et_w2),
                  FadeOut(panel), run_time=0.6)
        mezcla = onda(T_CHIPS, Y_CHIPS, rango_y=(-2.7, 2.7), ancho=10.6,
                      alto=2.7, color=C_SENAL)
        mezcla.move_to(DOWN * 0.35)
        et_mezcla = tag_hud(f"{len(CHIPS_MEZCLA)} chips sumados",
                            font_size=19, color=C_SENAL)
        et_mezcla.next_to(mezcla, UP, buff=0.16)
        self.play(FadeIn(mezcla.ejes), FadeIn(et_mezcla), run_time=0.5)
        self.play(Create(mezcla.curva), run_time=1.8)
        self.wait(4.6)

        # --- momento: se ve caotica, pero nada se perdio --------------------
        rot.mostrar(pie_curso("Se ve caótica. Pero los códigos eran "
                              "ortogonales: nada se perdió."),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)

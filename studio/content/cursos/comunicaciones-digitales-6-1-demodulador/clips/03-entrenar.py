class Clip3(Scene):
    """6.1.3 - Entrenar: un MLP 2-16-16 en numpy ve 2400 simbolos con su
    etiqueta, la perdida MEDIDA baja de 3.27 a 0.15 y la frontera que
    resulta es curva: abraza la espiral. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Entrenar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: una red diminuta ------------------------------------
        rot.mostrar(pie_curso("Otra idea: en vez de suponer la reticula, "
                              "aprenderla. Dos entradas (I y Q), dieciseis "
                              "salidas."),
                    zona="abajo", run_time=0.5)
        per = perceptron_mini(ocultas=N_OCULTAS, salidas=M_CLASES,
                              ancho=3.0, alto=2.4)
        per.move_to(LEFT * 3.4 + DOWN * 0.35)
        # la pieza dibuja hasta 8 neuronas por capa: se declara para que el
        # esquema no prometa mas nodos de los que se ven.
        et_per = tag_junto(per,
                           f"2 - {N_OCULTAS} - {M_CLASES}  "
                           f"(se dibujan {len(per.capas[1])} por capa)",
                           direccion=DOWN, buff=0.24, font_size=17)
        et_iq = tag_hud("I, Q", font_size=17, color=C_SENAL)
        et_iq.next_to(per.capas[0], LEFT, buff=0.18)
        et_sal = tag_hud("simbolo", font_size=17, color=C_COD)
        et_sal.next_to(per.capas[2], RIGHT, buff=0.18)
        self.play(FadeIn(per), run_time=0.9)
        self.play(FadeIn(et_per), FadeIn(et_iq), FadeIn(et_sal),
                  run_time=0.5)
        self.wait(4.0)

        # --- momento: la perdida baja de verdad ---------------------------
        rot.mostrar(pie_curso("Se le enseñan los 2400 simbolos con su "
                              "etiqueta; cada paso corrige los pesos."),
                    zona="abajo", run_time=0.5)
        on = onda(T_PERDIDAS, PERDIDAS, rango_y=(0.0, 3.5), ancho=4.2,
                  alto=2.3, color=C_IA)
        on.move_to(RIGHT * 2.6 + DOWN * 0.45)
        et_ejes = tag_junto(on, "pasos de entrenamiento", direccion=DOWN,
                            buff=0.2)
        et_ini = tag_hud(f"perdida = {fmt(PERDIDA_INI, 2)}", font_size=17)
        et_ini.next_to(on.en(T_PERDIDAS[0], PERDIDA_INI), UR, buff=0.10)
        self.play(FadeIn(on.ejes), FadeIn(et_ejes), FadeIn(et_ini),
                  run_time=0.7)
        self.play(Create(on.curva), run_time=2.6)
        et_fin = tag_hud(f"perdida = {fmt(PERDIDA_FIN, 2)}", font_size=17)
        et_fin.next_to(on.en(T_PERDIDAS[-1], PERDIDA_FIN), UP, buff=0.20)
        et_fin.shift(LEFT * 0.85)
        per2 = per.con_pesos(RED["W1"], RED["W2"])
        self.play(FadeIn(et_fin), Transform(per, per2), run_time=1.2)
        self.wait(4.0)

        # --- momento: la frontera aprendida -------------------------------
        rot.mostrar(pie_curso("Con esos pesos ya entrenados, esta es la "
                              "frontera que la red dibuja sobre el plano."),
                    zona="abajo", run_time=0.5)
        piq = plano_iq(unidad=1.15, alcance=ALCANCE)
        piq.move_to(LEFT * 2.5 + DOWN * 0.25)
        nube = piq.nube(RX_VIS, color=C_SENAL, maximo=N_VISIBLES,
                        radio=0.026, opacidad=0.65)
        et_nube = tag_hud(f"{N_VISIBLES} de {N_SIM} simbolos dibujados",
                          font_size=16, color=C_TENUE)
        et_nube.next_to(piq, DOWN, buff=0.16)
        self.play(FadeOut(per), FadeOut(et_per), FadeOut(et_iq),
                  FadeOut(et_sal), FadeOut(on.ejes), FadeOut(on.curva),
                  FadeOut(et_ejes), FadeOut(et_ini), FadeOut(et_fin),
                  run_time=0.7)
        self.play(FadeIn(piq), FadeIn(nube), FadeIn(et_nube), run_time=0.8)
        front = frontera_decision(piq, CAMPO_RED, XS_RED, color=C_IA,
                                  grosor=2.0)
        self.play(Create(front), run_time=2.8)
        self.wait(2.2)

        # --- momento: fronteras curvas ------------------------------------
        rot.mostrar(pie_curso("No son rectas: se doblan para abrazar la "
                              "espiral que dejo el amplificador."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(
            tag_hud("frontera aprendida", color=C_IA),
            tag_hud(f"{PASOS} pasos de ajuste"),
            tag_hud(f"acierto = {fmt(ACIERTO_FIN, 1)} %"))
        self.play(FadeIn(panel), run_time=0.5)
        self.wait(5.6)

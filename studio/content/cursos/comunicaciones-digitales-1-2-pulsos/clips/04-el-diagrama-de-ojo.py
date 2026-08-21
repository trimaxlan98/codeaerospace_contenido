class Clip4(Scene):
    """1.2.4 - El diagrama de ojo: la apertura MEDIDA se cierra cuando
    sube el ruido. Cierre de leccion. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El diagrama de ojo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el rio de simbolos ----------------------------------
        rot.mostrar(pie_curso("Treinta y un símbolos seguidos, ya con el "
                              "pulso de Nyquist."),
                    zona="abajo", run_time=0.5)
        on = onda(T_OJO, Y_OJO, rango_y=(-1.6, 1.6), ancho=9.4, alto=2.4,
                  color=C_SENAL, grosor=2.0)
        on.move_to(DOWN * 0.35)
        self.play(FadeIn(on.ejes), run_time=0.5)
        self.play(Create(on.curva), run_time=2.4)
        self.wait(3.0)

        # --- momento: doblar la onda y superponerla -----------------------
        rot.mostrar(pie_curso("Se corta cada dos tiempos de símbolo y se "
                              "superponen todos los trozos: eso es el ojo."),
                    zona="abajo", run_time=0.5)
        ojo = diagrama_ojo(Y_OJO, sps=SPS, n_trazas=N_TRAZAS, ancho=5.4,
                           alto=3.0, rango_y=RANGO_OJO, color=C_SENAL)
        ojo.move_to(DOWN * 0.35)
        self.play(FadeOut(on), run_time=0.5)
        self.play(FadeIn(ojo), run_time=1.2)
        # la barra se dibuja entre los DOS bordes que mide `apertura_ojo`
        barra = DoubleArrow(ojo._en(0.5, BORDES_LIMPIO[1]),
                            ojo._en(0.5, BORDES_LIMPIO[0]), buff=0.0,
                            color=C_CIFRA, stroke_width=3.5,
                            max_tip_length_to_length_ratio=0.13)
        et_ap = tag_hud(f"apertura = {fmt(APERTURA_LIMPIA, 2)}",
                        font_size=22)
        et_ap.next_to(ojo, UP, buff=0.24)
        et_ruido = tag_hud("sin ruido", font_size=20, color=C_TENUE)
        et_ruido.next_to(ojo, DOWN, buff=0.26)
        self.play(GrowFromCenter(barra), FadeIn(et_ap), FadeIn(et_ruido),
                  run_time=0.8)
        self.wait(3.4)

        # --- momento: entra el ruido --------------------------------------
        rot.mostrar(pie_curso("El receptor no recibe esto: recibe esto más "
                              "el ruido térmico de su propia electrónica."),
                    zona="abajo", run_time=0.5)
        ojo_1 = ojo.con_trazas(Y_OJO_1)
        barra_1 = DoubleArrow(ojo._en(0.5, BORDES_1[1]),
                              ojo._en(0.5, BORDES_1[0]), buff=0.0,
                              color=C_CIFRA, stroke_width=3.5,
                              max_tip_length_to_length_ratio=0.13)
        et_ap_1 = tag_hud(f"apertura = {fmt(APERTURA_1, 2)}", font_size=22)
        et_ap_1.move_to(et_ap)
        et_ruido_1 = tag_hud(f"SNR medida = {fmt(SNR_1, 1)} dB",
                             font_size=20, color=C_RUIDO)
        et_ruido_1.move_to(et_ruido)
        self.play(Transform(ojo.trazas, ojo_1.trazas),
                  Transform(barra, barra_1), Transform(et_ap, et_ap_1),
                  FadeOut(et_ruido), run_time=1.4)
        self.play(FadeIn(et_ruido_1), run_time=0.4)
        self.wait(3.4)

        # --- momento: el ojo se cierra ------------------------------------
        rot.mostrar(pie_curso("Con más ruido el ojo se cierra, y decidir "
                              "arriba o abajo se vuelve una apuesta."),
                    zona="abajo", run_time=0.5)
        ojo_2 = ojo.con_trazas(Y_OJO_2)
        barra_2 = DoubleArrow(ojo._en(0.5, BORDES_2[1]),
                              ojo._en(0.5, BORDES_2[0]), buff=0.0,
                              color=C_RUIDO, stroke_width=3.5,
                              max_tip_length_to_length_ratio=0.13)
        et_ap_2 = tag_hud(f"apertura = {fmt(APERTURA_2, 2)}", font_size=22,
                          color=C_RUIDO)
        et_ap_2.move_to(et_ap)
        et_ruido_2 = tag_hud(f"SNR medida = {fmt(SNR_2, 1)} dB",
                             font_size=20, color=C_RUIDO)
        et_ruido_2.move_to(et_ruido)
        self.play(Transform(ojo.trazas, ojo_2.trazas),
                  Transform(barra, barra_2), Transform(et_ap, et_ap_2),
                  FadeOut(et_ruido_1), run_time=1.4)
        self.play(FadeIn(et_ruido_2), run_time=0.4)
        self.wait(3.4)

        # --- cierre de leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "El símbolo perfecto no es el más cuadrado.",
            "Es el que calla cuando hablan los demás.",
            "Siguiente lección: el precio en hercios.",
            ojo, barra, et_ap, et_ruido_2)

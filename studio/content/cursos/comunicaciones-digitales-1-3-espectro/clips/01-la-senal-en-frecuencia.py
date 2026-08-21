class Clip1(Scene):
    """1.3.1 - La misma señal de bits, vista como onda y como PSD de
    Welch: el lóbulo sinc^2 y el ancho de banda medido al 90%. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La señal vista en frecuencia")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la señal, en el tiempo -------------------------------
        rot.mostrar(pie_curso("Cada símbolo es un pulso: la señal digital "
                              "también es una onda."),
                    zona="abajo", run_time=0.5)
        on = onda(T_VIS_1, Y_VIS_1, rango_y=(-1.3, 1.3), ancho=7.0, alto=1.7,
                 color=C_SENAL)
        on.move_to(UP * 1.6)
        et_on = tag_hud("y(t)", font_size=15)
        et_on.next_to(on, LEFT, buff=0.18)
        self.play(FadeIn(on.ejes), FadeIn(et_on), run_time=0.4)
        self.play(Create(on.curva), run_time=1.8)
        self.wait(3.2)

        # --- momento: la misma señal, en frecuencia -------------------------
        rot.mostrar(pie_curso("Esa misma señal, vista en frecuencia, "
                              "reparte su energía en el espectro."),
                    zona="abajo", run_time=0.5)
        esp = espectro_area(F_1, P_1_DB, piso_db=-40.0, ancho=7.0, alto=2.0,
                            color=C_BANDA)
        esp.move_to(DOWN * 1.55)
        et_esp = tag_hud("PSD(f), dB", font_size=15)
        et_esp.next_to(esp, LEFT, buff=0.18)
        self.play(FadeIn(esp.ejes), FadeIn(et_esp), run_time=0.4)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.8)
        self.wait(3.0)

        # --- momento: el lobulo sinc^2 --------------------------------------
        rot.mostrar(pie_curso("Tiene forma de sinc al cuadrado: casi toda "
                              "la energía cerca de cero, y colas que no "
                              "se acaban."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(esp.area, color=C_BANDA, scale_factor=1.03),
                  run_time=1.4)
        self.wait(4.0)

        # --- momento: el ancho de banda medido -------------------------------
        rot.mostrar(pie_curso("El 90% de esa energía cabe en un ancho "
                              "medido: el ancho de banda."),
                    zona="abajo", run_time=0.5)
        marca = esp.marca_f(BW_1_90, color=C_CIFRA)
        cifra = tag_hud(f"BW(90%) = {fmt(BW_1_90, 2)} Hz-eq", font_size=19)
        cifra.next_to(marca, UP, buff=0.1)
        self.play(Create(marca), FadeIn(cifra), run_time=1.0)
        self.wait(4.2)

        # --- cierre del clip --------------------------------------------------
        rot.mostrar(pie_curso("Toda señal ocupa un trozo de espectro."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

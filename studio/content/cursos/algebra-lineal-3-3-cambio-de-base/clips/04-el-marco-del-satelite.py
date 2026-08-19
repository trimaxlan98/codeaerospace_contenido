class Clip4(Scene):
    """3.3.4 - El caso real: marco cuerpo contra marco inercial. El vector
    Sol no se mueve; sus tres numeros, si. Cierra la leccion. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El marco del satélite")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el satelite alineado con el marco inercial -----------
        esp = espacio3(unidad=0.9, alcance=3)
        esp.move_to(LEFT * 1.0 + DOWN * 0.25)
        self.play(FadeIn(esp), run_time=0.9)
        rot.mostrar(pie_curso("Un cubesat. Sus ejes de cuerpo empiezan "
                              "alineados con el marco inercial."),
                    zona="abajo", run_time=0.5)
        sat = satelite3(esp, np.eye(3), tam=0.9)
        sat.eje_z.set_color(C_K)
        self.play(FadeIn(sat), run_time=0.8)
        self.wait(3.0)

        # --- momento: el Sol, en el marco inercial -------------------------
        rot.mostrar(pie_curso("El Sol se ve en una dirección fija. Esta es "
                              "su lista en el marco inercial."), zona="abajo",
                    run_time=0.5)
        sol = vector3(esp, S_INERCIAL, color=C_VEC, nombre=r"\vec s")
        col_i = vector_columna(S_INERCIAL, color=C_VEC, dec=DEC_SOL,
                               font_size=26)
        col_c = vector_columna(S_CUERPO, color=C_VEC, dec=DEC_SOL,
                               font_size=26)
        for col in (col_i, col_c):
            col.matriz.get_rows()[0].set_color(C_I)
            col.matriz.get_rows()[1].set_color(C_J)
            col.matriz.get_rows()[2].set_color(C_K)
        bloque_i = VGroup(tag_hud("inercial", font_size=15), col_i)
        bloque_i.arrange(DOWN, buff=0.14)
        bloque_c = VGroup(tag_hud("cuerpo", font_size=15), col_c)
        bloque_c.arrange(DOWN, buff=0.14)
        panel = panel_derecha(VGroup(bloque_i, bloque_c).arrange(RIGHT,
                                                                 buff=0.42))
        self.play(GrowArrow(sol.flecha), FadeIn(sol.etiqueta), run_time=0.9)
        self.play(FadeIn(panel[0]), FadeIn(bloque_i), run_time=0.6)
        self.wait(3.4)

        # --- momento: la maniobra ------------------------------------------
        rot.mostrar(pie_curso("El satélite maniobra: " + fmt(GUINADA, 0)
                              + " grados de guiñada y " + fmt(ALABEO, 0)
                              + " de alabeo."), zona="abajo", run_time=0.5)
        sat_girado = satelite3(esp, R_SAT, tam=0.9)
        sat_girado.eje_z.set_color(C_K)
        self.play(Transform(sat, sat_girado), *esp.anim_matriz(R_SAT),
                  run_time=2.4)
        self.wait(3.2)

        # --- momento: la misma flecha, otra lista --------------------------
        rot.mostrar(pie_curso("El Sol no se ha movido. La rejilla que lo "
                              "mide, sí."), zona="abajo", run_time=0.5)
        self.play(FadeIn(bloque_c, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.2)

        rot.mostrar(formula_pie(r"s_{\rm cuerpo} = R^{-1}\, s_{\rm inercial}"),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)

        # --- cierre de la leccion ------------------------------------------
        cierre_leccion(self, rot, "El vector no cambia.",
                       "Cambian sus números.",
                       "¿Y hay una base en la que TODA transformación sea "
                       "sencilla? Módulo 4.",
                       esp, sat, sol, panel[0], bloque_i, bloque_c)

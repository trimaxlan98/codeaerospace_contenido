class Clip4(Scene):
    """6.1.4 - El veredicto: la MISMA nube, dos demoduladores. El de libro
    yerra 1952 de 2400; el aprendido, 41. Cierre de leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El veredicto")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la misma nube, dos jueces ---------------------------
        rot.mostrar(pie_curso("La misma nube y los mismos 2400 simbolos, "
                              "puestos delante de dos demoduladores."),
                    zona="abajo", run_time=0.5)
        izq = plano_iq(unidad=0.9, alcance=ALCANCE)
        izq.move_to(LEFT * 3.35 + DOWN * 0.25)
        der = plano_iq(unidad=0.9, alcance=ALCANCE)
        der.move_to(RIGHT * 3.35 + DOWN * 0.25)
        nube_i = izq.nube(RX_VIS, color=C_SENAL, maximo=N_VISIBLES,
                          radio=0.022, opacidad=0.7)
        nube_d = der.nube(RX_VIS, color=C_SENAL, maximo=N_VISIBLES,
                          radio=0.022, opacidad=0.7)
        et_izq = tag_hud("demodulador de libro", font_size=19,
                         color=C_TENUE)
        et_izq.next_to(izq, UP, buff=0.22)
        et_der = tag_hud("demodulador aprendido", font_size=19, color=C_IA)
        et_der.next_to(der, UP, buff=0.22)
        # arriba, en el pasillo central: abajo la fila de cifras se
        # estrecha contra los dos rotulos de errores.
        et_muestra = tag_hud(f"{N_VISIBLES} de {N_SIM} dibujados",
                             font_size=16, color=C_TENUE)
        et_muestra.move_to(UP * 2.45)
        self.play(FadeIn(izq), FadeIn(der), run_time=0.7)
        self.play(FadeIn(nube_i), FadeIn(nube_d), FadeIn(et_izq),
                  FadeIn(et_der), FadeIn(et_muestra), run_time=1.0)
        self.wait(3.4)

        # --- momento: el de libro ------------------------------------------
        rot.mostrar(pie_curso("El de libro corta el plano por la reticula "
                              "ideal, y casi todo cae en region ajena."),
                    zona="abajo", run_time=0.5)
        ideal = izq.puntos(P16, color=C_BIT, radio=0.05)
        ideal.set_fill(opacity=0.55)
        ideal.set_stroke(opacity=0.0)
        reg_i = izq.regiones(CAMPO_LIBRO, XS_LIBRO, color=C_EJE, grosor=1.4)
        ok_i = izq.nube(RX_VIS_OK_LIBRO, color=C_SENAL, maximo=N_VISIBLES,
                        radio=0.022, opacidad=0.5)
        mal_i = izq.nube(RX_VIS_ERR_LIBRO, color=C_RUIDO, maximo=N_VISIBLES,
                         radio=0.026, opacidad=0.95)
        self.play(FadeIn(ideal), Create(reg_i), run_time=1.8)
        self.play(FadeOut(nube_i), FadeIn(ok_i), FadeIn(mal_i), run_time=0.9)
        cifra_i = tag_hud(f"{ERR_LIBRO} errores de {N_SIM}", font_size=22)
        cifra_i.next_to(izq, DOWN, buff=0.26)
        self.play(FadeIn(cifra_i, shift=0.15 * UP), run_time=0.5)
        self.wait(3.2)

        # --- momento: el aprendido -----------------------------------------
        rot.mostrar(pie_curso("El aprendido corta por donde los simbolos "
                              "REALMENTE caen."),
                    zona="abajo", run_time=0.5)
        front_d = frontera_decision(der, CAMPO_RED, XS_RED, color=C_IA,
                                    grosor=1.8)
        ok_d = der.nube(RX_VIS_OK_RED, color=C_SENAL, maximo=N_VISIBLES,
                        radio=0.022, opacidad=0.5)
        mal_d = der.nube(RX_VIS_ERR_RED, color=C_RUIDO, maximo=N_VISIBLES,
                         radio=0.030, opacidad=0.95)
        self.play(Create(front_d), run_time=2.0)
        self.play(FadeOut(nube_d), FadeIn(ok_d), FadeIn(mal_d), run_time=0.9)
        cifra_d = tag_hud(f"{ERR_RED} errores de {N_SIM}", font_size=22)
        cifra_d.next_to(der, DOWN, buff=0.26)
        self.play(FadeIn(cifra_d, shift=0.15 * UP), run_time=0.5)
        self.wait(3.4)

        # --- momento: la moraleja -------------------------------------------
        rot.mostrar(pie_curso("Misma antena, misma potencia, mismo ruido: "
                              "lo unico que cambio fue quien decide."),
                    zona="abajo", run_time=0.5)
        mejora = VGroup(tag_hud(f"{fmt(MEJORA, 0)}x", font_size=42),
                        tag_hud("menos errores", font_size=17))
        mejora.arrange(DOWN, buff=0.12)
        mejora.move_to(DOWN * 0.35)
        self.play(FadeIn(mejora, scale=0.7), run_time=0.6)
        self.wait(5.2)

        # --- cierre de leccion ----------------------------------------------
        cierre_leccion(
            self, rot,
            "La frontera de libro presume el canal.",
            "La aprendida lo escucha.",
            "Siguiente leccion: una constelacion que nadie diseño.",
            izq, der, ideal, reg_i, ok_i, mal_i, cifra_i, front_d, ok_d,
            mal_d, cifra_d, et_izq, et_der, et_muestra, mejora)

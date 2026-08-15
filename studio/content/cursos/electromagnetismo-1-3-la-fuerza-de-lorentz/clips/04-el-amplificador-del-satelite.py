class Clip4(Scene):
    """1.3.4 - El TWT del transpondedor: la helice frena la onda al paso
    del haz, el haz le cede energia y la señal sale mas alta que entro.
    Cierra el modulo 1 con el gancho hacia el 2. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El amplificador del satélite")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la señal agotada ------------------------------------
        twt = tubo_ondas()
        twt.move_to(UP * 0.15)
        et_in = tag_junto(twt.onda_entrada, "entrada", buff=0.22)
        et_out = tag_junto(twt.onda_salida, "salida", buff=0.22)
        rot.mostrar(pie_curso("La señal que llega al satélite viene "
                              "agotada: hay que amplificarla a bordo."),
                    zona="abajo", run_time=0.5)
        self.play(Create(twt.onda_entrada), FadeIn(et_in), run_time=0.8)
        self.wait(4.4)

        # --- momento: la helice que frena la onda -------------------------
        rot.mostrar(pie_curso("El tubo de ondas progresivas: una hélice "
                              "que obliga a la onda a avanzar despacio."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(twt.tubo), Create(twt.helice), run_time=1.6)
        self.wait(4.4)

        # --- momento: el haz de electrones --------------------------------
        rot.mostrar(pie_curso("Por el eje corre un haz de electrones, "
                              "apenas más rápido que la onda frenada."),
                    zona="abajo", run_time=0.5)
        self.play(LaggedStart(*[FadeIn(e, scale=1.6) for e in twt.haz],
                              lag_ratio=0.12), run_time=1.0)
        self.play(twt.haz.animate.shift(RIGHT * 0.28), run_time=2.0,
                  rate_func=linear)
        self.wait(2.2)

        # --- momento: la onda sale crecida --------------------------------
        rot.mostrar(pie_curso("Vuelta a vuelta el haz cede su energía: "
                              "la señal sale más alta de lo que entró."),
                    zona="abajo", run_time=0.5)
        self.play(Create(twt.onda_salida), FadeIn(et_out), run_time=1.0)
        self.wait(4.2)

        tag_g = tag_hud(f"+{twt.ganancia_db():.0f} dB", font_size=19)
        tag_g.next_to(twt.onda_salida, UP, buff=0.30)
        rot.mostrar(pie_curso(f"Aquí van {twt.ganancia_db():.0f} dB "
                              "dibujados; los TWT reales encadenan "
                              "etapas hasta 50 o 60 dB."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(tag_g, shift=0.15 * UP), run_time=0.5)
        self.wait(4.6)

        # --- cierre del modulo 1 ------------------------------------------
        self.play(FadeOut(twt), FadeOut(et_in), FadeOut(et_out),
                  FadeOut(tag_g), run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        linea1 = Text("Los campos quietos ya son tuyos.", font_size=40,
                      color=C_TITULO)
        linea2 = Text("Ahora vamos a moverlos.", font_size=40,
                      color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        rot.mostrar(pie_curso("Módulo 2: los campos en movimiento — y de "
                              "su matrimonio nace la onda."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(4.6)

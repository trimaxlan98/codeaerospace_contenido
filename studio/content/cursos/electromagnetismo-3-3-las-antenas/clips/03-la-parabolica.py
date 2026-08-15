class Clip3(Scene):
    """3.3.3 - La parabolica: cada rayo rebota con la ley de la reflexion
    de verdad y aun asi TODOS acaban en el foco. El plato de balcon de
    60 cm concentra 35.3 dBi. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La parabólica")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el plato ---------------------------------------------
        pf = parabola_foco()
        pf.move_to(DOWN * 0.2)
        self.play(Create(pf.plato), FadeIn(pf.brazo), run_time=0.9)
        rot.mostrar(pie_curso("Del satélite llega un frente plano: rayos "
                              "paralelos. El plato es su espejo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: la ley de la reflexion, rayo a rayo ------------------
        rot.mostrar(pie_curso("Cada rayo rebota con la ley de la "
                              "reflexión, sin trampa alguna."),
                    zona="abajo", run_time=0.5)
        self.play(LaggedStart(*[Create(pf.rayo(i)) for i in range(6)],
                              lag_ratio=0.18), run_time=2.6)
        self.wait(2.6)

        # --- momento: todos al foco ----------------------------------------
        rot.mostrar(pie_curso("Y la parábola está tallada para que TODOS "
                              "acaben en el mismo punto: el foco."),
                    zona="abajo", run_time=0.5)
        # El rotulo va en el color del foco (el receptor) para despegarse
        # de los rayos violetas que lo rodean.
        et_lnb = tag_junto(pf.foco_mob, "LNB", direccion=DOWN, buff=0.34,
                           color=C_CARGA)
        self.play(FadeIn(pf.foco_mob, scale=1.8), run_time=0.5)
        self.play(Flash(pf.foco(), color=C_CARGA, line_length=0.22),
                  FadeIn(et_lnb), run_time=0.7)
        self.wait(4.4)

        rot.mostrar(pie_curso("Por eso el receptor vive AHÍ, colgado del "
                              "brazo: donde cae toda la señal."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: la formula y la cifra del plato de balcon ------------
        rot.mostrar(formula_pie(r"G = \eta\,\left(\frac{\pi D}{\lambda}"
                                r"\right)^{2}"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("El plato de balcón, sesenta centímetros "
                              "en banda Ku: miles de veces la isótropa."),
                    zona="abajo", run_time=0.5)
        tag_g = tag_hud(f"{D_PLATO * 100:.0f} cm a "
                        f"{F_KU_TV / 1e9:.0f} GHz -> "
                        f"{G_PLATO_DBI:.1f} dBi", font_size=17)
        tag_g.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(tag_g, shift=0.1 * LEFT), run_time=0.6)
        self.wait(4.4)

        rot.mostrar(pie_curso("La ganancia crece con el cuadrado del "
                              "diámetro: al subir de banda, el plato "
                              "puede encoger."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

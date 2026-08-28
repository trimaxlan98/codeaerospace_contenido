class Clip4(Scene):
    """10.3.4 - Donde la red SI gana: deshacer un amplificador saturado,
    que ningun filtro lineal puede arreglar. Y cuanto gana, medido: 5.2 dB.
    Cierra la leccion y el curso entero. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("Donde si aporta"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        n_ver = 154                       # dos periodos de la senal
        caja = dict(ancho=9.4, alto=1.15, eje_y=False, radio=0.018,
                    grosor=1.5)
        rango = (-1.05, 1.05)

        # --- la senal que entra al amplificador ---------------------------
        sec_l = Secuencia(LIMPIA_SAT[:n_ver], 0, rango, color=C_SENAL,
                          **caja)
        sec_l.move_to(UP * 2.05 + RIGHT * 0.40)
        et_l = tag_hud("limpia", font_size=19, color=C_SENAL)
        et_l.next_to(sec_l, LEFT, buff=0.22)
        self.play(FadeIn(sec_l), FadeIn(et_l), run_time=1.0)
        self.wait(1.6)

        # --- lo que sale de el: los picos, aplastados ---------------------
        sec_s = Secuencia(SUCIA_SAT[:n_ver], 0, rango, color=C_RUIDO,
                          **caja)
        sec_s.move_to(UP * 0.42 + RIGHT * 0.40)
        et_s = tag_hud("saturada", font_size=19, color=C_RUIDO)
        et_s.next_to(sec_s, LEFT, buff=0.22)
        self.play(FadeIn(sec_s), FadeIn(et_s), run_time=1.0)
        self.wait(1.6)
        rot.mostrar(formula_pie(r"y = \tanh(2.2\,x)"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)

        # --- lo mejor que puede hacer un filtro LINEAL --------------------
        sec_m = Secuencia(MEJOR_LINEAL[:n_ver], 0, rango, color=C_SALIDA,
                          **caja)
        sec_m.move_to(DOWN * 1.20 + RIGHT * 0.40)
        et_m = tag_hud("mejor lineal", font_size=19, color=C_SALIDA)
        et_m.next_to(sec_m, LEFT, buff=0.22)
        self.play(FadeIn(sec_m), FadeIn(et_m), run_time=1.0)
        self.wait(1.8)
        rot.mostrar(cifra_pie(f"ganancia {fmt(GANANCIA_LIN, 4)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)
        rot.mostrar(cifra_pie(f"lineal: error {fmt(ERR_LINEAL, 4)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        senales = VGroup(sec_l, et_l, sec_s, et_s, sec_m, et_m)
        self.play(FadeOut(senales), run_time=0.8)

        # --- y lo que saca la red: mejor, no milagroso --------------------
        bar = Barras([ERR_LINEAL, ERR_RED], ancho=5.4, alto=3.0,
                     rango_y=(0.0, 0.13), color=C_CALCULO, hueco=0.42)
        bar.move_to(UP * 0.30)
        bar.barra(0).set_color(C_RUIDO)
        bar.barra(1).set_color(C_APREND)
        et_b0 = tag_hud(f"lineal {fmt(ERR_LINEAL, 4)}", font_size=18,
                        color=C_RUIDO)
        et_b0.next_to(bar.barra(0), DOWN, buff=0.26)
        et_b1 = tag_hud(f"red {fmt(ERR_RED, 4)}", font_size=18,
                        color=C_APREND)
        et_b1.next_to(bar.barra(1), DOWN, buff=0.26)
        self.play(FadeIn(bar), FadeIn(et_b0), FadeIn(et_b1), run_time=1.0)
        self.wait(1.8)
        rot.mostrar(cifra_pie(f"red: error {fmt(ERR_RED, 4)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        panel = panel_cifras((f"lineal {fmt(ERR_LINEAL, 4)}", C_RUIDO),
                             (f"red {fmt(ERR_RED, 4)}", C_APREND),
                             (f"mejora {fmt(MEJORA_RED, 1)} dB", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)
        rot.mostrar(cifra_pie(f"mejora {fmt(MEJORA_RED, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- y con esto se cierra el curso entero -------------------------
        cierre_leccion(self, rot, "Una señal es una lista de numeros.",
                       "Todo lo demas es que le haces.",
                       bar, et_b0, et_b1, panel)

class Clip2(Scene):
    """6.1.2 - El demodulador de libro decide por cercania a la reticula
    IDEAL: sobre la nube deformada casi todo cae en region ajena. Los
    errores se pintan rojos y se CUENTAN. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La frontera de libro falla")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la nube que hay que decidir -------------------------
        rot.mostrar(pie_curso("Vuelve la nube recibida. El receptor tiene "
                              "que decir, para cada punto, que simbolo era."),
                    zona="abajo", run_time=0.5)
        piq = plano_iq(unidad=1.15, alcance=ALCANCE)
        piq.move_to(LEFT * 2.5 + DOWN * 0.25)
        nube = piq.nube(RX_VIS, color=C_SENAL, maximo=N_VISIBLES,
                        radio=0.026, opacidad=0.8)
        et_nube = tag_hud(f"{N_VISIBLES} de {N_SIM} simbolos dibujados",
                          font_size=16, color=C_TENUE)
        et_nube.next_to(piq, DOWN, buff=0.16)
        self.play(FadeIn(piq), run_time=0.6)
        self.play(FadeIn(nube), FadeIn(et_nube), run_time=1.0)
        self.wait(3.6)

        # --- momento: la reticula ideal y sus regiones --------------------
        rot.mostrar(pie_curso("El demodulador de libro decide por cercania "
                              "a la reticula IDEAL: estas son sus regiones."),
                    zona="abajo", run_time=0.5)
        ideal = piq.puntos(P16, color=C_BIT, radio=0.06)
        ideal.set_fill(opacity=0.55)
        ideal.set_stroke(opacity=0.0)
        regiones = piq.regiones(CAMPO_LIBRO, XS_LIBRO, color=C_EJE,
                                grosor=1.6)
        self.play(FadeIn(ideal), run_time=0.6)
        self.play(Create(regiones), run_time=2.2)
        panel_reglas = panel_derecha(
            tag_hud("demodulador de libro", color=C_TENUE),
            tag_hud("vecino mas cercano", color=C_TENUE),
            tag_hud("sobre la reticula ideal", color=C_BIT))
        self.play(FadeIn(panel_reglas), run_time=0.5)
        self.wait(3.8)

        # --- momento: los errores, contados -------------------------------
        rot.mostrar(pie_curso("Cada simbolo que cae en region ajena es un "
                              "error. Se pintan en rojo."),
                    zona="abajo", run_time=0.5)
        ok = piq.nube(RX_VIS_OK_LIBRO, color=C_SENAL, maximo=N_VISIBLES,
                      radio=0.026, opacidad=0.55)
        mal = piq.nube(RX_VIS_ERR_LIBRO, color=C_RUIDO, maximo=N_VISIBLES,
                       radio=0.030, opacidad=0.95)
        self.play(FadeOut(nube), FadeIn(ok), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(d, scale=0.6) for d in mal],
                              lag_ratio=0.004), run_time=2.4)
        self.wait(2.4)

        # --- momento: la cifra ---------------------------------------------
        rot.mostrar(pie_curso("Contados sobre los 2400 simbolos medidos, "
                              "no sobre los dibujados."),
                    zona="abajo", run_time=0.5)
        panel_cuenta = panel_derecha(
            tag_hud("demodulador de libro", color=C_TENUE),
            tag_hud(f"errores = {ERR_LIBRO} de {N_SIM}"),
            tag_hud(f"tasa = {fmt(TASA_LIBRO, 1)} %"))
        self.play(FadeOut(panel_reglas), FadeIn(panel_cuenta), run_time=0.6)
        self.wait(4.6)

        # --- momento: la moraleja ------------------------------------------
        rot.mostrar(pie_curso("La frontera de libro no falla por ruido: "
                              "falla porque presume una reticula que el "
                              "canal ya movio."),
                    zona="abajo", run_time=0.5)
        self.wait(5.6)

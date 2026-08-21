class Clip3(Scene):
    """2.2.3 - El amplificador de a bordo (Saleh AM/AM): a retroceso 1.15
    comprime la reticula 16-QAM de verdad; d_min MEDIDA se hunde de
    0.632 a 0.107. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El amplificador de a bordo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la curva AM/AM del amplificador saturado -------------
        rot.mostrar(pie_curso("En un satélite la potencia es oro: el "
                              "amplificador trabaja cerca de saturarse."),
                    zona="abajo", run_time=0.5)
        graf = grafica(_saleh_f, (0.0, 1.8), (0.0, 1.05), ancho=6.6,
                      alto=3.0, color=C_SENAL)
        graf.move_to(DOWN * 0.35)
        et_ejes = VGroup(
            tag_hud("r (drive)", font_size=15).next_to(
                graf.ejes[0].get_end(), DOWN, buff=0.12),
            tag_hud("A(r)", font_size=15).next_to(
                graf.ejes[1].get_end(), UP, buff=0.1))
        self.play(FadeIn(graf.ejes), FadeIn(et_ejes), run_time=0.5)
        self.play(Create(graf.curva), run_time=1.6)
        self.wait(2.4)

        guia = graf.vertical_en(RETROCESO, color=C_CIFRA)
        punto = Dot(graf.punto_de(RETROCESO), color=C_CIFRA, radius=0.07)
        cifra_r = tag_hud(f"r = {fmt(RETROCESO, 2)}  ->  "
                          f"A(r) = {fmt(A_RETROCESO, 3)}", font_size=18)
        cifra_r.next_to(punto, UR, buff=0.18)
        self.play(Create(guia), FadeIn(punto), FadeIn(cifra_r),
                  run_time=0.9)
        self.wait(3.2)

        # --- momento: pasamos a la reticula --------------------------------
        rot.mostrar(pie_curso("A ese régimen, la retícula 16-QAM se "
                              "deforma de verdad."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(graf), FadeOut(et_ejes), FadeOut(guia),
                  FadeOut(punto), FadeOut(cifra_r), run_time=0.7)
        plano = plano_iq(unidad=1.7, alcance=1.75)
        plano.move_to(DOWN * 0.1)
        ideal = plano.puntos(QAM16, color=C_BIT, radio=0.07)
        ideal.set_fill(opacity=0.3)
        ideal.set_stroke(opacity=0.3)
        vivos = plano.puntos(QAM16, color=C_BIT, radio=0.07)
        self.play(FadeIn(plano), FadeIn(ideal), FadeIn(vivos), run_time=1.0)
        self.wait(3.5)

        # --- momento: el amplificador aprieta las esquinas ------------------
        rot.mostrar(pie_curso("Los puntos MÁS ALEJADOS del centro son "
                              "los que más se comprimen."), zona="abajo",
                    run_time=0.5)
        deformados = plano.puntos(QAM16_AMP, color=C_RUIDO, radio=0.07)
        flecha = flecha_libre(plano, QAM16[I_ESQUINA_QAM16],
                              QAM16_AMP[I_ESQUINA_QAM16], color=C_RUIDO,
                              grosor=3.0)
        self.play(Transform(vivos, deformados), run_time=1.6)
        self.play(Create(flecha), run_time=0.7)
        cifra_esq = tag_hud(f"{fmt(R_ESQUINA_QAM16, 3)}  ->  "
                            f"{fmt(R_ESQUINA_QAM16_AMP, 3)}", font_size=17,
                            color=C_RUIDO)
        cifra_esq.next_to(flecha, LEFT, buff=0.15)
        self.play(FadeIn(cifra_esq), run_time=0.4)
        self.wait(3.4)

        # --- momento: d_min se hunde ----------------------------------------
        rot.mostrar(pie_curso("d_min se hunde con el mismo retroceso: "
                              "el receptor pierde margen ante el ruido."),
                    zona="abajo", run_time=0.5)
        i2, j2 = PAR_QAM16_AMP
        seg_amp = Line(plano.p(QAM16_AMP[i2]), plano.p(QAM16_AMP[j2]),
                      color=C_CIFRA, stroke_width=3.0)
        cifra_d = tag_hud(f"d_min:  {fmt(D_QAM16, 3)}  ->  "
                          f"{fmt(D_QAM16_AMP, 3)}", font_size=19)
        cifra_d.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(Create(seg_amp), FadeIn(cifra_d), run_time=1.0)
        self.wait(6.0)

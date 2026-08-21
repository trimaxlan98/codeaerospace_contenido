class Clip4(Scene):
    """2.2.4 - 16-APSK (4+12, DVB-S2): mismos 4 bits/simbolo que 16-QAM,
    pero al mismo retroceso los anillos sufren MENOS la compresion del
    amplificador (d_min 0.107 vs 0.284). Cierre de leccion. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("APSK: anillos para el espacio")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: dos anillos en vez de una reticula --------------------
        rot.mostrar(pie_curso("16-APSK reparte los 16 puntos en dos "
                              "anillos: 4 adentro, 12 afuera."),
                    zona="abajo", run_time=0.5)
        plano = plano_iq(unidad=1.7, alcance=1.75)
        plano.move_to(DOWN * 0.1)
        self.play(FadeIn(plano), run_time=0.7)
        c_int = plano.circulo(R_INT_APSK16, color=C_REJILLA)
        c_ext = plano.circulo(R_EXT_APSK16, color=C_REJILLA)
        self.play(Create(c_int), Create(c_ext), run_time=1.0)
        ideal = plano.puntos(APSK16, color=C_BIT, radio=0.08)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in ideal],
                              lag_ratio=0.05), run_time=1.3)
        et = tag_hud("16-APSK (4+12) - la constelación de DVB-S2",
                    font_size=17)
        et.next_to(plano, DOWN, buff=0.55)
        self.play(FadeIn(et), run_time=0.5)
        self.wait(3.2)

        # --- momento: mismos bits, otra geometria ----------------------------
        rot.mostrar(pie_curso("Los mismos cuatro bits por símbolo que "
                              "16-QAM, pero repartidos en anillos."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: el mismo amplificador, el mismo retroceso -------------
        rot.mostrar(pie_curso("El mismo amplificador, el mismo retroceso: "
                              "los anillos sufren MENOS la compresión."),
                    zona="abajo", run_time=0.5)
        deformados = plano.puntos(APSK16_AMP, color=C_RUIDO, radio=0.08)
        c_int_amp = plano.circulo(R_INT_APSK16_AMP, color=C_RUIDO)
        c_ext_amp = plano.circulo(R_EXT_APSK16_AMP, color=C_RUIDO)
        self.play(Transform(ideal, deformados), Transform(c_int, c_int_amp),
                  Transform(c_ext, c_ext_amp), run_time=1.6)
        self.wait(3.2)

        # --- momento: la comparacion final -----------------------------------
        rot.mostrar(pie_curso("A la misma potencia, la 16-APSK pierde "
                              "menos margen que la retícula."),
                    zona="abajo", run_time=0.5)
        cifra_qam = tag_hud(f"16-QAM:  {fmt(D_QAM16, 3)} -> "
                            f"{fmt(D_QAM16_AMP, 3)}", font_size=18,
                            color=C_RUIDO)
        cifra_apsk = tag_hud(f"16-APSK:  {fmt(D_APSK16, 3)} -> "
                             f"{fmt(D_APSK16_AMP, 3)}", font_size=18,
                             color=C_COD)
        panel = panel_derecha(cifra_qam, cifra_apsk)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(5.0)

        # --- cierre de leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "En tierra, la retícula.",
            "En órbita, los anillos.",
            "Siguiente lección: el ruido decide, la curva BER.",
            plano, c_int, c_ext, ideal, et, panel)

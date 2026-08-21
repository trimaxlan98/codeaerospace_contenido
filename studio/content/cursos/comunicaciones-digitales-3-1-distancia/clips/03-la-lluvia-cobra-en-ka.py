class Clip3(Scene):
    """3.1.3 - La lluvia cobra en Ka: la MISMA serie con memoria, escalada
    a banda X y a banda Ka -- Ka paga hasta ~15 dB, X apenas los siente.
    (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La lluvia cobra en Ka")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: donde viven X y Ka en el espectro ----------------------
        rot.mostrar(pie_curso("Subir de banda da mas ancho... pero tambien "
                              "acerca la senal a la frecuencia que la "
                              "lluvia sabe absorber."),
                    zona="abajo", run_time=0.5)
        banda = banda_espacio(exp0=0, exp1=2, ancho=7.0)
        banda.move_to(UP * 1.9)
        m_x = banda.marca(F_MARTE, "banda X", color=C_SENAL, arriba=True)
        m_ka = banda.marca(F_KA, "banda Ka", color=C_BANDA, arriba=False)
        self.play(FadeIn(banda), run_time=0.8)
        self.play(FadeIn(m_x), FadeIn(m_ka), run_time=0.7)
        self.wait(4.0)

        # --- momento: la serie de lluvia con memoria ---------------------------
        rot.mostrar(pie_curso("El clima real: minutos de cielo claro y "
                              "rachas de lluvia, con memoria, medidas."),
                    zona="abajo", run_time=0.5)
        on = onda(T_LLUVIA, ATT_KA, rango_y=(0.0, 18.0), ancho=8.6,
                 alto=2.6, color=C_BANDA)
        on.move_to(DOWN * 1.3)
        margen = on.horizontal_en(MARGEN_ENLACE_DB, color=C_RUIDO)
        et_margen = tag_hud(f"margen = {fmt(MARGEN_ENLACE_DB, 0)} dB",
                            font_size=15, color=C_RUIDO)
        et_margen.next_to(on.en(on.x0, MARGEN_ENLACE_DB), LEFT, buff=0.14)
        self.play(FadeOut(banda), FadeOut(m_x), FadeOut(m_ka), run_time=0.5)
        self.play(FadeIn(on.ejes), Create(margen), FadeIn(et_margen),
                  run_time=0.6)
        self.play(Create(on.curva), run_time=2.0)
        panel_ka = panel_derecha(
            tag_hud(f"Ka: hasta {fmt(ATT_KA_MAX, 1)} dB", font_size=17,
                    color=C_BANDA))
        self.play(FadeIn(panel_ka), run_time=0.4)
        self.wait(3.4)

        # --- momento: la MISMA lluvia, en banda X ------------------------------
        rot.mostrar(pie_curso("La MISMA lluvia, escalada a banda X con el "
                              "cociente de frecuencias al cuadrado (aprox. "
                              "ITU-R P.838): apenas roza el margen."),
                    zona="abajo", run_time=0.5)
        curva_x = on.curva_de(T_LLUVIA, ATT_X, color=C_SENAL)
        panel_kax = panel_derecha(
            tag_hud(f"Ka: hasta {fmt(ATT_KA_MAX, 1)} dB", font_size=17,
                    color=C_BANDA),
            tag_hud(f"X: hasta {fmt(ATT_X_MAX, 1)} dB", font_size=17,
                    color=C_SENAL))
        self.play(Create(curva_x), FadeOut(panel_ka), FadeIn(panel_kax),
                  run_time=1.4)
        self.wait(4.0)

        # --- momento: la cuenta --------------------------------------------
        rot.mostrar(pie_curso(f"{MIN_FUERA_KA} de los {MIN_TOTAL} minutos, "
                              "Ka se cae del margen. X, ninguno: la altura "
                              "de banda tiene precio."),
                    zona="abajo", run_time=0.5)
        self.wait(7.8)

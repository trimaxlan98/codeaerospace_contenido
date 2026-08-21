class Clip1(Scene):
    """5.2.1 - El canal que respira: la serie Ka con memoria (lluvia_serie)
    convertida en Eb/N0 disponible; sube y baja mas de 14 dB en minutos, y
    cada modcod exige su propio piso de SNR para cerrar. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El canal que respira")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el enlace no vive en un valor fijo -------------------
        rot.mostrar(pie_curso("El vinculo con una sonda no vive en un "
                              "valor fijo: el clima decide cuanta senal "
                              "sobrevive, minuto a minuto."),
                    zona="abajo", run_time=0.5)
        on = onda(T_LLUVIA, SNR_DISPONIBLE, rango_y=(-4.0, 15.0), ancho=8.6,
                  alto=3.2, color=C_SENAL)
        on.move_to(DOWN * 0.2)
        self.play(FadeIn(on.ejes), run_time=0.5)
        self.play(Create(on.curva), run_time=2.4)
        self.wait(2.6)

        # --- momento: el techo de un dia despejado --------------------------
        rot.mostrar(pie_curso("En un dia despejado sobran mas de trece "
                              "decibeles de margen."), zona="abajo",
                    run_time=0.5)
        techo = on.horizontal_en(SNR_CLARO, color=C_CIFRA)
        et_techo = tag_hud(f"cielo despejado = {fmt(SNR_CLARO, 1)} dB",
                           font_size=17, color=C_CIFRA)
        et_techo.next_to(on.en(on.x0, SNR_CLARO), UP, buff=0.1)
        et_techo.shift(RIGHT * et_techo.width / 2)
        self.play(Create(techo), FadeIn(et_techo), run_time=0.8)
        self.wait(4.6)

        # --- momento: la lluvia se come mas de 14 dB de un tiron ------------
        rot.mostrar(pie_curso("Y una racha de lluvia se come mas de "
                              "catorce decibeles de un tiron."),
                    zona="abajo", run_time=0.5)
        p_min = on.en(T_SNR_MIN, SNR_MIN)
        dot_min = Dot(p_min, radius=0.08, color=C_RUIDO)
        et_min = tag_hud(f"minimo = {fmt(SNR_MIN, 1)} dB", font_size=18,
                         color=C_RUIDO)
        et_min.next_to(p_min, DOWN, buff=0.16)
        self.play(FadeIn(dot_min, scale=0.5), FadeIn(et_min), run_time=0.6)
        self.play(Indicate(dot_min, color=C_RUIDO, scale_factor=1.6),
                  run_time=0.8)
        self.wait(4.2)

        # --- momento: cada modcod exige su propio piso ----------------------
        rot.mostrar(pie_curso("Cada modcod necesita su propio piso de "
                              "SNR para cerrar el enlace."),
                    zona="abajo", run_time=0.5)
        umbrales = VGroup()
        etiquetas = VGroup()
        for nombre, umbral, color in zip(MODCOD_NOMBRES, MODCOD_UMBRALES,
                                         MODCOD_COLORES):
            linea = on.horizontal_en(umbral, color=color)
            et = tag_hud(f"{nombre} >= {fmt(umbral, 1)} dB", font_size=16,
                        color=color)
            et.next_to(on.en(on.x1, umbral), LEFT, buff=0.14)
            et.shift(UP * 0.15)
            umbrales.add(linea)
            etiquetas.add(et)
        self.play(FadeOut(dot_min), FadeOut(et_min), FadeOut(techo),
                  FadeOut(et_techo), run_time=0.5)
        self.play(LaggedStart(*[Create(u) for u in umbrales],
                              lag_ratio=0.3), run_time=1.4)
        self.play(LaggedStart(*[FadeIn(e) for e in etiquetas],
                              lag_ratio=0.3), run_time=1.2)
        self.wait(4.4)

        # --- momento: el canal respira ---------------------------------------
        rot.mostrar(pie_curso("El canal respira: sube, baja, y vuelve a "
                              "subir. El enlace tiene que seguirle el "
                              "paso."), zona="abajo", run_time=0.5)
        self.wait(5.4)

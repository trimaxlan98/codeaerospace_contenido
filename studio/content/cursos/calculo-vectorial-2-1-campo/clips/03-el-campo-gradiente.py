class Clip3(Scene):
    """2.1.3 - El gradiente del paisaje 1.1 ES un campo: apunta cuesta
    arriba y es grande donde el terreno empina. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El campo gradiente")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mapa de siempre, ahora tenue -----------------------
        pl = plano_leccion()
        mapa = curvas_nivel(pl, PAISAJE, niveles=NIVELES, n=100,
                            opacidad=0.35)
        self.play(FadeIn(pl), FadeIn(mapa), run_time=1.0)
        rot.mostrar(pie_curso("Recordemos el paisaje: sus curvas de "
                              "nivel, ahora tenues, de fondo."),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- momento: en cada punto, su gradiente -----------------------------
        rot.mostrar(pie_curso("¿Y si en cada punto dibujamos su "
                              "gradiente? Nace un campo."), zona="abajo",
                    run_time=0.5)
        panel_f = panel_derecha(MathTex(r"F = \nabla f", font_size=36,
                                        color=C_TITULO))
        self.play(FadeIn(panel_f, shift=0.15 * LEFT), run_time=0.6)
        campo = campo_flechas(pl, campo_gradiente(PAISAJE), paso=0.9,
                              escala=0.4)
        self.play(LaggedStart(*[FadeIn(f, scale=0.5) for f in campo.flechas],
                              lag_ratio=0.014), run_time=2.6)
        self.wait(2.8)

        # --- momento: apunta cuesta arriba, grande donde empina ---------------
        rot.mostrar(pie_curso("Cada flecha apunta cuesta arriba, hacia "
                              "la colina más cercana."), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(campo.en(*P_EMPINADO), color=C_GRAD,
                           scale_factor=1.25), run_time=0.9)
        self.wait(2.6)

        rot.mostrar(pie_curso("Y son grandes donde el terreno empina, "
                              "casi nulas donde es llano."), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(campo.en(*P_LLANO), color=C_GRAD,
                           scale_factor=1.25), run_time=0.9)
        self.wait(3.0)

        # --- momento: perpendicular a los niveles ------------------------------
        rot.mostrar(pie_curso("Y siempre corta las curvas de nivel en "
                              "ángulo recto: el camino más corto."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(mapa.curva(3), scale_factor=1.04), run_time=0.8)
        self.wait(3.2)

        # --- cierre de idea -------------------------------------------------------
        rot.mostrar(pie_curso("El gradiente de un paisaje ES un campo: "
                              "el mapa, hablando en flechas."),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

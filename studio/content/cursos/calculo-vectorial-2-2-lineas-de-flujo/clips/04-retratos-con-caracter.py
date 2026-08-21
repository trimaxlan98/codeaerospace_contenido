class Clip4(Scene):
    """2.2.4 - Tres campos, tres retratos de fase: el radial huye en
    rectas, el rotor gira en circulos, la silla escapa en hiperbolas.
    Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Retratos con carácter")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.7)
        rot.mostrar(pie_curso("Las líneas de flujo también retratan el "
                              "carácter de un campo."), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        # --- retrato 1: radial, rectas que huyen -----------------------------------
        rot.mostrar(pie_curso("El radial: F = (x, y). Sus líneas de "
                              "flujo son rectas que huyen del origen."),
                    zona="abajo", run_time=0.5)
        campo_r = campo_flechas(pl, campo_radial, paso=0.9, escala=0.4)
        panel_r = panel_derecha(MathTex(r"F = (x,\, y)", font_size=34,
                                        color=C_TITULO))
        self.play(FadeIn(campo_r), FadeIn(panel_r, shift=0.15 * LEFT),
                  run_time=0.8)
        lineas_r = [linea_flujo(pl, campo_radial, s, T=T_RADIAL)
                   for s in SEMILLAS_RADIAL]
        self.play(LaggedStart(*[Create(lf) for lf in lineas_r],
                              lag_ratio=0.15), run_time=2.6)
        self.wait(3.0)

        self.play(FadeOut(campo_r), FadeOut(panel_r),
                  *[FadeOut(lf) for lf in lineas_r], run_time=0.7)

        # --- retrato 2: rotor, circulos ---------------------------------------------
        rot.mostrar(pie_curso("El rotor: F = (−y, x). Sus líneas de "
                              "flujo son círculos perfectos."),
                    zona="abajo", run_time=0.5)
        campo_o = campo_flechas(pl, campo_rotor, paso=0.9, escala=0.4)
        panel_o = panel_derecha(MathTex(r"F = (-y,\, x)", font_size=34,
                                        color=C_TITULO))
        self.play(FadeIn(campo_o), FadeIn(panel_o, shift=0.15 * LEFT),
                  run_time=0.8)
        lineas_o = [linea_flujo(pl, campo_rotor, s, T=T_ROTOR)
                   for s in SEMILLAS_ROTOR]
        self.play(LaggedStart(*[Create(lf) for lf in lineas_o],
                              lag_ratio=0.15), run_time=2.6)
        self.wait(3.0)

        self.play(FadeOut(campo_o), FadeOut(panel_o),
                  *[FadeOut(lf) for lf in lineas_o], run_time=0.7)

        # --- retrato 3: silla, hiperbolas ---------------------------------------------
        rot.mostrar(pie_curso("La silla: F = (x, −y). Sus líneas de "
                              "flujo son hipérbolas que se abren en "
                              "cruz."), zona="abajo", run_time=0.5)
        campo_s = campo_flechas(pl, campo_silla, paso=0.9, escala=0.4)
        panel_s = panel_derecha(MathTex(r"F = (x,\, -y)", font_size=34,
                                        color=C_TITULO))
        self.play(FadeIn(campo_s), FadeIn(panel_s, shift=0.15 * LEFT),
                  run_time=0.8)
        lineas_s = [linea_flujo(pl, campo_silla, s, T=T_SILLA)
                   for s in SEMILLAS_SILLA]
        self.play(LaggedStart(*[Create(lf) for lf in lineas_s],
                              lag_ratio=0.15), run_time=2.6)
        self.wait(3.2)

        # --- cierre -----------------------------------------------------------------
        cierre_leccion(self, rot,
                       "El campo es un mapa de corrientes.",
                       "Las líneas de flujo son sus ríos.",
                       "Siguiente lección: el trabajo de un camino.",
                       pl, campo_s, panel_s, *lineas_s)

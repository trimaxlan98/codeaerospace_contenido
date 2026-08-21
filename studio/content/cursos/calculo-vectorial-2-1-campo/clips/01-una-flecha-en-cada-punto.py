class Clip1(Scene):
    """2.1.1 - Un campo asigna una flecha (no un numero) a cada punto del
    plano; se lee en cualquiera de ellos, con cifras. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Una flecha en cada punto")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el campo como funcion vectorial ----------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Un campo asigna, a cada punto del plano, "
                              "no un número: una FLECHA."), zona="abajo",
                    run_time=0.5)
        panel_f = panel_derecha(MathTex(r"F:\ \mathbb{R}^2 \to \mathbb{R}^2",
                                        font_size=36, color=C_TITULO))
        self.play(FadeIn(panel_f, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.0)

        # --- momento: el campo se llena de flechas --------------------------
        rot.mostrar(pie_curso("Muestreamos una malla regular y el campo "
                              "entero aparece de un golpe."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(panel_f), run_time=0.4)
        campo = campo_flechas(pl, CAMPO_VIENTO)
        self.play(LaggedStart(*[FadeIn(f, scale=0.5) for f in campo.flechas],
                              lag_ratio=0.015), run_time=2.6)
        self.wait(2.8)

        # --- momento: leer el campo en tres puntos --------------------------
        rot.mostrar(pie_curso("Podemos leer la flecha en CUALQUIER punto: "
                              "ahí está, ya calculada."), zona="abajo",
                    run_time=0.5)
        etiquetas = VGroup(*[
            tag_hud(f"F({fmt(p[0])}, {fmt(p[1])}) = "
                    f"({fmt(CAMPO_VIENTO(np.array(p))[0])}, "
                    f"{fmt(CAMPO_VIENTO(np.array(p))[1])})", font_size=16)
            for p in PUNTOS_LECTURA])
        etiquetas.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        etiquetas.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        fondo = BackgroundRectangle(etiquetas, color=CODE_BG,
                                    fill_opacity=0.82, buff=0.18)
        self.play(FadeIn(fondo), run_time=0.3)
        for p, cifra in zip(PUNTOS_LECTURA, etiquetas):
            fl = campo.en(*p)
            self.play(Indicate(fl, color=C_TITULO, scale_factor=1.2),
                      run_time=0.6)
            self.play(FadeIn(cifra), run_time=0.4)
            self.wait(1.8)

        # --- momento: cierre de idea ------------------------------------------
        rot.mostrar(pie_curso("El campo entero es esa malla de flechas: "
                              "el espacio, hablando."), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)

        rot.mostrar(pie_curso("Pero no todos los campos son iguales: "
                              "algunos tienen carácter propio."),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

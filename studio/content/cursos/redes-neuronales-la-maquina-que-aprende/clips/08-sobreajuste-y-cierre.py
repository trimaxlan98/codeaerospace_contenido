class Clip8(Scene):
    """8 - Aprender de memoria no es aprender. Un modelo sencillo capta la
    forma general de los datos; uno enorme memoriza hasta el ruido y
    fracasa con lo que nunca vio. Cierra el curso con la tarjeta de
    marca."""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ---------------------------------------------------
        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Aprender de memoria no es aprender")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)

        # --- Los datos: un anillo alrededor de un centro --------------------
        ejes = ejes_plano()
        self.play(Create(ejes), run_time=1.3)

        X, y = datos_circulos(n=90, radio=1.25, ruido=0.14, semilla=7)
        puntos = puntos_datos(ejes, X, y, color_a=C_DATO_A, color_b=C_DATO_B)
        self.play(FadeIn(puntos, lag_ratio=0.03), run_time=1.8)
        self.wait(0.7)

        # --- Dos modelos: uno sencillo, uno gigante que memoriza ------------
        entreno_suave = entrenar_mlp(X, y, ocultas=3, epocas=1200, semilla=3)
        entreno_duro = entrenar_mlp(X, y, ocultas=24, epocas=3000, semilla=3)
        modelo_suave = entreno_suave.modelos[-1]
        modelo_duro = entreno_duro.modelos[-1]

        # --- Acto 1: el modelo sencillo capta la forma general --------------
        frontera_suave = frontera_imagen(ejes, modelo_suave, color_a=C_DATO_A,
                                         color_b=C_DATO_B)
        self.play(FadeIn(frontera_suave), run_time=1.1)
        rot.mostrar(pie_curso("Un modelo sencillo captura la forma "
                              "general."), zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- Acto 2: el modelo gigante memoriza hasta el ruido ---------------
        frontera_dura = frontera_imagen(ejes, modelo_duro, color_a=C_DATO_A,
                                        color_b=C_DATO_B)
        self.play(FadeTransform(frontera_suave, frontera_dura), run_time=1.7)
        rot.mostrar(pie_curso("Uno enorme puede memorizar hasta el "
                              "ruido."), zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- Seis puntos de prueba, cerca de la frontera real ----------------
        # Verificadas contra los modelos reales: las de indice par las
        # clasifica MAL el modelo sobreajustado y BIEN el suave; las
        # impares las aciertan ambos. (Etiqueta real por radio 1.25.)
        posiciones = [(-0.02, 0.98), (1.52, -0.27), (0.55, -0.68),
                      (-1.52, 0.27), (-0.90, -0.25), (-0.27, -1.52)]
        pruebas = VGroup(*[
            Dot(ejes.c2p(px, py), radius=0.08, fill_color=C_TENUE,
               fill_opacity=0.9, stroke_color=WHITE, stroke_width=1.8)
            for px, py in posiciones
        ])
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in pruebas],
                              lag_ratio=0.12), run_time=1.6)

        # --- Con la frontera retorcida, tres quedan del lado equivocado -----
        # El pie entra ANTES del pulso rojo: lo que se ve y lo que se lee
        # deben coincidir en el tiempo.
        errados = [0, 2, 4]
        rot.mostrar(pie_curso("Y fracasa justo con lo que nunca vio."),
                   zona="abajo", run_time=0.5)
        self.play(*[Indicate(pruebas[i], color=C_PERDIDA, scale_factor=1.5)
                    for i in errados], run_time=1.5)
        self.wait(2.2)

        # --- Vuelve la frontera suave: ahora todos aciertan ------------------
        frontera_suave_2 = frontera_imagen(ejes, modelo_suave,
                                           color_a=C_DATO_A, color_b=C_DATO_B)
        self.play(FadeTransform(frontera_dura, frontera_suave_2),
                  run_time=1.7)
        rot.mostrar(pie_curso("Generalizar, no memorizar: esa es la "
                              "meta."), zona="abajo", run_time=0.5)
        self.play(*[Indicate(d, color=C_OK, scale_factor=1.5)
                    for d in pruebas], run_time=1.5)
        self.wait(2.2)

        # --- Pantalla limpia para la tarjeta de cierre del curso -------------
        rot.limpiar(run_time=0.5)
        # Group, no VGroup: frontera_suave_2 es un ImageMobject (raster).
        resto = Group(ejes, puntos, frontera_suave_2, pruebas, modulo)
        self.play(FadeOut(resto), run_time=1.1)

        # --- Tarjeta final: marca del curso con subrayado brillante ---------
        titulo_final = titulo_marca("Redes neuronales", font_size=46)
        subtitulo = Text("la máquina que aprende", font_size=25,
                         color=C_ACENTO)
        cuerpo = VGroup(titulo_final, subtitulo).arrange(DOWN, buff=0.26)

        subrayado = Line(LEFT, RIGHT, color=C_ACENTO)
        subrayado.set_width(subtitulo.width * 1.1)
        subrayado.next_to(subtitulo, DOWN, buff=0.16)
        brillo_subrayado = con_brillo(subrayado, color=C_ACENTO)

        tarjeta = VGroup(cuerpo, brillo_subrayado)
        tarjeta.move_to(ORIGIN)

        self.play(Write(titulo_final), run_time=1.7)
        self.play(FadeIn(subtitulo, shift=0.15 * UP), run_time=0.9)
        self.wait(0.6)
        self.play(Create(brillo_subrayado), run_time=1.3)
        self.wait(2)

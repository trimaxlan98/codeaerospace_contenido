class Clip1(Scene):
    """2.2.1 - Aplicar dos matrices, una tras otra, se ve como UN solo
    movimiento del plano: esa combinacion es el producto B A. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Primero uno, luego otro")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el plano y un vector cualquiera -----------------------
        pl = plano_leccion()
        v = vector(pl, V_DEMO, color=C_VEC, nombre=r"\vec v")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Ya sabes que una matriz mueve el plano "
                              "entero. ¿Y si aplicamos dos, una tras "
                              "otra?"), zona="abajo", run_time=0.5)
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.9)
        self.wait(3.6)

        # --- momento: primero A -----------------------------------------
        etiqueta_paso = tag_hud("A")
        etiqueta_paso.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        rot.mostrar(pie_curso("Primero A: una rotación de 30 grados."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(etiqueta_paso), run_time=0.3)
        self.wait(0.7)
        self.play(*pl.anim_matriz(A, v), run_time=2.0)
        self.wait(3.6)

        # --- momento: luego B --------------------------------------------
        nueva_etiqueta = tag_hud("B")
        nueva_etiqueta.move_to(etiqueta_paso)
        rot.mostrar(pie_curso("Luego B: una cizalla que desliza las "
                              "filas."), zona="abajo", run_time=0.5)
        self.play(Transform(etiqueta_paso, nueva_etiqueta), run_time=0.3)
        self.wait(0.7)
        # M es la transformacion TOTAL desde la identidad: v conserva sus
        # coords viejas (V_DEMO) porque nunca se reasigno tras el primer
        # play, asi que BA @ V_DEMO es exactamente el destino correcto.
        self.play(*pl.anim_matriz(BA, v), run_time=2.0)
        self.wait(3.8)

        # --- momento: una sola matriz --------------------------------------
        rot.mostrar(pie_curso("Dos movimientos, un solo resultado: esa "
                              "combinación es el producto B A."),
                    zona="abajo", run_time=0.5)
        fila = VGroup(MathTex(r"B\,A=", font_size=32, color=C_TENUE),
                     matriz_columnas(BA, font_size=36)).arrange(RIGHT,
                                                                buff=0.25)
        panel = panel_derecha(fila)
        self.play(FadeOut(etiqueta_paso), FadeIn(panel, shift=0.15 * LEFT),
                  run_time=0.7)
        self.wait(4.4)

        rot.mostrar(pie_curso("Multiplicar matrices ES componer "
                              "movimientos. ¿Cómo se calcula ese "
                              "producto?"), zona="abajo", run_time=0.5)
        self.wait(5.0)

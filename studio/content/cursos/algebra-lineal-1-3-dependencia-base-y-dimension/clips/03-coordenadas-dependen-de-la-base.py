class Clip3(Scene):
    """1.3.3 - Las coordenadas no son del vector: son del vector Y de la
    base. La rejilla de otra base, oblicua sobre la canonica, lee el mismo
    vector con otras cifras. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        # Titulo largo (45 caracteres): titulo_curso lo encoge al tope de
        # 7.6 u para no pisar el HUD de la esquina.
        titulo = titulo_curso("Coordenadas: números que dependen de la base")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el vector fijo, siempre el mismo -----------------------
        pl = plano_leccion(vivo=True)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Este vector no se mueve. Lo que va a "
                              "cambiar es la regla con la que lo "
                              "leemos."), zona="abajo", run_time=0.5)
        p = vector(pl, P2, color=C_VEC, nombre=r"\vec P")
        self.play(GrowArrow(p.flecha), FadeIn(p.etiqueta), run_time=0.9)
        self.wait(3.2)

        # --- momento: la matriz de la otra base -------------------------------
        rot.mostrar(pie_curso("Otra base B, con columnas b1 y b2, define "
                              "su propia rejilla."), zona="abajo",
                    run_time=0.5)
        mat = matriz_columnas(MATRIZ_B, colores=(C_I, C_J), font_size=32)
        panel_mat = panel_derecha(mat)
        self.play(FadeIn(panel_mat, shift=0.15 * LEFT), run_time=0.6)
        self.wait(2.6)

        # --- momento: la rejilla oblicua se despliega -------------------------
        rot.mostrar(pie_curso("La rejilla azul se dobla: sus líneas ya no "
                              "son horizontales y verticales, son b1 y "
                              "b2."), zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(MATRIZ_B), run_time=2.0)
        self.wait(3.2)

        # --- momento: las dos lecturas -----------------------------------
        rot.mostrar(pie_curso("La rejilla gris sigue ahí debajo: nada del "
                              "espacio cambió, solo la vara de medir."),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        rot.mostrar(pie_curso("En la rejilla gris, P es [3; 2]. En la "
                              "azul, se lee distinto."), zona="abajo",
                    run_time=0.5)
        coef_b = resolver(MATRIZ_B, P2)
        col_canonica = vector_columna(np.array(COEF_CANONICA), color=C_VEC,
                                      dec=0, font_size=32)
        cap1 = Text("Canónica", font_size=18, color=C_TENUE)
        grupo1 = VGroup(cap1, col_canonica).arrange(DOWN, buff=0.12)
        col_b = vector_columna(coef_b, color=C_VEC, dec=2, font_size=32)
        cap2 = Text("Base B", font_size=18, color=C_TENUE)
        grupo2 = VGroup(cap2, col_b).arrange(DOWN, buff=0.12)
        panel_lecturas = panel_derecha(grupo1, grupo2)
        self.play(Transform(panel_mat, panel_lecturas), run_time=0.8)
        self.play(Indicate(p.flecha, color=C_VEC, scale_factor=1.05),
                  run_time=0.8)
        self.wait(4.2)

        rot.mostrar(pie_curso("La flecha no cambió. Las coordenadas, sí: "
                              "dependen de la base."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

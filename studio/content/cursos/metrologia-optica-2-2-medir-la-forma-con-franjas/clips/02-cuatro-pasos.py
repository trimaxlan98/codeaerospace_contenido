class Clip2(Scene):
    """2 - Cuatro pasos. Cuatro tomas con las franjas corridas 90 grados
    cada vez; con las cuatro intensidades la fase de cada pixel sale de una
    arcotangente (fase_4_pasos: atan2(I4-I2, I1-I3)) sin saber ni la
    iluminacion ni el contraste. La quinta imagen es esa fase, envuelta
    entre -pi y +pi. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Cuatro pasos"), zona="arriba", run_time=0.6)

        # --- geometria: la fila de cinco imagenes en la banda alta ----------
        # cuatro_pasos trae un rotulo-cabecera que repite la formula que este
        # clip escribe en MathTex: se saca del VGroup vectorial (indice 10)
        # para no decir dos veces lo mismo ni robarle sitio al titulo.
        ESC, Y_FILA = 1.05, 0.85
        cp = cuatro_pasos(n_franjas=5, sag_ondas=4.0)
        cabecera = cp.vectorial[10]
        cp.vectorial.remove(cabecera)
        cp.scale(ESC)
        centro_fila = (cp.miniaturas[0].get_center() + cp.mapa.get_center()) / 2
        cp.shift(np.array([0.0, Y_FILA, 0.0]) - centro_fila)

        marcos = [cp.vectorial[2 * k] for k in range(4)]
        grados = [cp.vectorial[2 * k + 1] for k in range(4)]
        marco_fase, rot_fase = cp.vectorial[8], cp.vectorial[9]

        y_tags = grados[0].get_bottom()[1] - 0.34
        t_grados = tag_hud("desfase en grados", font_size=13, color=C_TENUE)
        t_grados.move_to(np.array([(marcos[0].get_center()[0]
                                    + marcos[3].get_center()[0]) / 2.0,
                                   y_tags, 0.0]))
        t_fase = tag_hud("fase envuelta", font_size=13, color=C_MEDIDA)
        t_fase.move_to(np.array([marco_fase.get_center()[0], y_tags, 0.0]))

        form = MathTex(r"\phi = \arctan\frac{I_4 - I_2}{I_1 - I_3}",
                       font_size=44, color=C_MEDIDA)
        form.move_to(np.array([0.0, -1.75, 0.0]))

        # --- momento: cuatro tomas con la referencia corrida ----------------
        rot.mostrar(pie_curso("Tomamos cuatro imágenes, corriendo las franjas "
                              "un cuarto de vuelta cada vez."), zona="abajo")
        tomas = [Group(cp.miniaturas[k], marcos[k], grados[k])
                 for k in range(4)]
        self.play(LaggedStart(*[FadeIn(g, shift=0.14 * UP) for g in tomas],
                              lag_ratio=0.45), run_time=2.4)
        self.play(FadeIn(t_grados), run_time=0.4)
        self.wait(5.2)

        # --- momento: la fase sale de una arcotangente ----------------------
        rot.mostrar(pie_curso("Con las cuatro intensidades, la fase de cada "
                              "píxel sale de una arcotangente."), zona="abajo")
        self.play(Write(form), run_time=1.4)
        self.wait(5.4)

        # --- momento: el mapa de fase envuelta ------------------------------
        rot.mostrar(pie_curso("El resultado es un mapa de fase: envuelto "
                              "entre menos pi y pi."), zona="abajo")
        self.play(FadeIn(cp.mapa, scale=0.92), Create(marco_fase),
                  FadeIn(rot_fase), run_time=1.2)
        self.play(FadeIn(t_fase), run_time=0.5)
        self.wait(5.2)

        # --- cierre ---------------------------------------------------------
        rot.mostrar(pie_curso("Cuatro fotos y una fórmula: la superficie "
                              "entera en fase."), zona="abajo")
        self.wait(6.0)

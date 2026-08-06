class Clip5(Scene):
    """5 - Atencion: mirar todo a la vez. Una fila de tokens que atiende a
    'banco': el abanico de pesos ambar por encima, las barras reales por
    debajo, y el nuevo vector violeta 'banco (dinero)' que nace como
    mezcla de lo que mas atendio."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo -------------------------------------------
        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Atención: mirar todo a la vez")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.4)

        # --- momento: una sola fila de tokens ---------------------------------
        frase = "el banco cobra comisiones al cliente"
        idx_banco = 1  # el(0) banco(1) cobra(2) comisiones(3) al(4) cliente(5)
        fila = fila_tokens(frase)
        fila.move_to(DOWN * 0.6)
        self.play(FadeIn(fila, lag_ratio=0.05), run_time=1.3)
        self.wait(1.8)

        # --- momento: el abanico de atencion desde 'banco', por encima --------
        pesos = pesos_atencion(frase, idx_banco)
        abanico = abanico_atencion(fila, idx_banco, pesos)
        self.play(Create(abanico), run_time=1.5)
        rot.mostrar(pie_curso("Cada palabra pregunta: ¿quién me importa "
                              "aquí?"), zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- momento: los pesos reales, como barras debajo de la fila ---------
        # origen y=-2.1 con alto_max=0.9: el bloque de barras+etiqueta queda
        # muy por encima del pie (que arranca en y=-3.32), sin tocarlo.
        etiquetas = frase.split()
        barras = barras_pesos(pesos, etiquetas,
                              origen=np.array([0.0, -2.1, 0.0]),
                              alto_max=0.9)
        self.play(FadeIn(barras, lag_ratio=0.05), run_time=1.1)
        orden = [i for i in np.argsort(pesos)[::-1] if i != idx_banco][:2]
        self.play(AnimationGroup(*[
            Indicate(fila.fichas[i], color=C_ACENTO, scale_factor=1.3)
            for i in orden]), run_time=0.9)
        rot.mostrar(pie_curso("'Cobra' y 'comisiones' pesan más: banco de "
                              "dinero."), zona="abajo", run_time=0.5)
        self.wait(3.6)

        # --- momento: 'banco' se tine de violeta -------------------------------
        banco_ficha = fila.fichas[idx_banco]
        self.play(banco_ficha.animate.set_color(C_VECTOR), run_time=0.7)
        self.wait(0.8)

        # --- momento: nace 'banco (dinero)' arriba de la fila -------------------
        nueva = ficha_token("banco (dinero)", color=C_VECTOR)
        nueva.move_to(np.array([banco_ficha.get_center()[0], 1.5, 0.0]))
        flecha = Arrow(banco_ficha.get_top(), nueva.get_bottom(), buff=0.1,
                      color=C_VECTOR, stroke_width=3,
                      max_tip_length_to_length_ratio=0.25)
        self.play(GrowArrow(flecha), FadeIn(nueva, scale=0.6), run_time=1.0)
        self.wait(0.6)

        # --- momento: destellos convergentes desde lo mas atendido --------------
        # Lines temporales e invisibles (solo camino para el destello);
        # nunca se agregan a la escena, se descartan tras el play().
        origenes = [i for i in np.argsort(pesos)[::-1] if i != idx_banco][:3]
        caminos = [Line(fila.fichas[i].get_top(), nueva.get_center(),
                        stroke_opacity=0) for i in origenes]
        self.play(*[destello(c, color=C_VECTOR, ancho=5, cola=0.4)
                   for c in caminos], run_time=1.0)
        rot.mostrar(pie_curso("Su nuevo vector: mezcla de lo que atendió."),
                   zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- momento: cierre -- se apaga el abanico, se retiran las barras ------
        self.play(FadeOut(barras), FadeOut(flecha),
                  abanico.animate.set_opacity(0.15), run_time=0.9)
        rot.mostrar(pie_curso("Eso es la atención: contexto a la medida."),
                   zona="abajo", run_time=0.5)
        self.wait(4.6)

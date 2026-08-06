class Clip6(Scene):
    """6 - Q, K, V: preguntar, etiquetar, responder. Tres bloques a la
    izquierda emiten la consulta, la llave y el valor de cada palabra; a
    la derecha, la consulta de 'banco' compara con cada llave, nacen los
    pesos reales y los valores se mezclan en un resultado."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo -------------------------------------------
        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Q, K, V: preguntar, etiquetar, responder")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.6)

        # --- momento: la columna Q / K / V a la izquierda ------------------------
        q = bloque("Q · consulta", ancho=2.4, color=C_ACENTO,
                  color_texto=C_TITULO)
        k = bloque("K · llave", ancho=2.4, color=C_TOKEN,
                  color_texto=C_TITULO)
        v = bloque("V · valor", ancho=2.4, color=C_VECTOR,
                  color_texto=C_TITULO)
        columna = VGroup(q, k, v).arrange(DOWN, buff=0.5)
        columna.move_to(np.array([-4.3, 0.0, 0.0]))
        self.play(FadeIn(columna, lag_ratio=0.15), run_time=1.6)
        rot.mostrar(pie_curso("Cada palabra emite tres versiones de sí "
                              "misma."), zona="abajo", run_time=0.5)
        self.wait(3.8)

        # --- momento: la mini fila de tokens a la derecha, sin tocar la columna --
        # columna ocupa hasta x=-3.1; la fila (escalada) queda con borde
        # izquierdo cerca de x=-0.3: mas de 0.5 de hueco entre ambas.
        frase = "el banco cobra comisiones"
        idx_banco = 1  # el(0) banco(1) cobra(2) comisiones(3)
        fila = fila_tokens(frase)
        fila.scale(0.85)
        fila.move_to(np.array([1.6, 1.0, 0.0]))
        self.play(FadeIn(fila, lag_ratio=0.05), run_time=1.3)
        self.wait(1.7)

        # --- momento: la Q toca la K (flecha corta, dentro del hueco) ------------
        flecha_qk = Arrow(q.get_bottom(), k.get_top(), buff=0.06,
                          color=C_ACENTO, stroke_width=3,
                          max_tip_length_to_length_ratio=0.3)
        self.play(GrowArrow(flecha_qk), run_time=0.6)
        self.wait(0.5)

        # --- momento: la consulta se compara con cada llave -----------------------
        # Lines temporales e invisibles desde K hacia la derecha (nunca
        # cruzan Q ni V, que quedan a su izquierda): solo camino del destello.
        caminos_k = [Line(k.get_right(), ficha.get_bottom(),
                          stroke_opacity=0) for ficha in fila.fichas]
        self.play(AnimationGroup(*[
            destello(c, color=C_TOKEN, ancho=5, cola=0.35)
            for c in caminos_k], lag_ratio=0.35), run_time=2.0)
        rot.mostrar(pie_curso("La consulta se compara con cada llave."),
                   zona="abajo", run_time=0.5)
        self.wait(3.6)

        # --- momento: nacen los pesos reales, bajo la fila -------------------------
        pesos = pesos_atencion(frase, idx_banco)
        etiquetas = frase.split()
        barras = barras_pesos(pesos, etiquetas,
                              origen=np.array([1.6, -1.1, 0.0]),
                              alto_max=0.9)
        self.play(FadeIn(barras, lag_ratio=0.05), run_time=1.3)
        rot.mostrar(formula_pie(r"\text{softmax}(Q \cdot K) \rightarrow "
                                r"\text{pesos}"), zona="abajo", run_time=0.5)
        self.wait(4.2)

        # --- momento: los valores se mezclan segun esos pesos -----------------------
        resultado = ficha_token("resultado", color=C_VECTOR)
        resultado.move_to(np.array([1.6, -2.3, 0.0]))
        conexion_v = conectar(v, resultado, color=C_VECTOR, grosor=2.5)
        self.play(FadeIn(resultado, scale=0.6), GrowArrow(conexion_v),
                  run_time=0.7)
        self.play(flujo([conexion_v], color=C_VECTOR, ancho=5, cola=0.4,
                        por_conexion=0.9), run_time=1.2)
        rot.mostrar(pie_curso("Y los valores se mezclan según esos pesos."),
                   zona="abajo", run_time=0.5)
        self.wait(3.8)

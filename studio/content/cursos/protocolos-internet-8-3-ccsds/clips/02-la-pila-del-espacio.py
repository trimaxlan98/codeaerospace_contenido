class Clip2(Scene):
    """8.3.2 - La pila de casa frente a la del espacio: sobrevive la idea
    de capas, casi ninguna pieza, y cada cambio tiene su porque. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La pila del espacio")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la pila de casa -------------------------------------
        rot.mostrar(pie_curso("Ocho modulos para armar esta torre: cada capa "
                              "resuelve un problema y nada mas."),
                    zona="abajo", run_time=0.5)
        p_casa = pila_desnuda(CAPAS_CASA, ancho=3.0, alto=0.50, fs=14)
        p_esp = pila_desnuda(CAPAS_ESPACIO, ancho=3.0, alto=0.50, fs=14)
        p_casa.move_to(np.array([-3.55, 0.92, 0.0]))
        p_esp.move_to(np.array([3.55, 0.92, 0.0]))
        # Alineadas por ARRIBA: las cuatro capas gemelas quedan a la misma
        # altura y el vinculo punteado entre ellas sale horizontal.
        p_esp.shift(UP * (p_casa.capa(0).get_top()[1] -
                          p_esp.capa(0).get_top()[1]))
        et_casa = tag_hud("en casa: TCP/IP", font_size=18, color=C_TENUE)
        et_casa.next_to(p_casa, UP, buff=0.26)
        et_esp = tag_hud("camino a Marte: CCSDS", font_size=18,
                         color=C_TENUE)
        et_esp.next_to(p_esp, UP, buff=0.26)
        self.play(FadeIn(p_casa), FadeIn(et_casa), run_time=0.9)
        self.wait(4.6)

        # --- momento: la pila del espacio ---------------------------------
        rot.mostrar(pie_curso("Fuera de la Tierra sobrevive la idea de "
                              "capas. Casi ninguna de las piezas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(p_esp), FadeIn(et_esp), run_time=0.9)
        vinculos = VGroup(*[
            DashedLine(p_casa.capa(i).get_right(),
                       p_esp.capa(j).get_left(), color=C_EJE,
                       stroke_width=1.6, dash_length=0.10)
            for i, j in PARES])
        self.play(LaggedStart(*[Create(v) for v in vinculos],
                              lag_ratio=0.30), run_time=1.2)
        self.wait(4.4)

        # --- momento: las tres que se caen, y por que ----------------------
        rot.mostrar(pie_curso("Tres capas se caen, y ninguna se cae por "
                              "falta de ancho de banda."),
                    zona="abajo", run_time=0.5)
        # Dos columnas de ancho fijo: rellenar con espacios no alinearia (la
        # sombra de Text descarta el glifo del espacio).
        col_que = VGroup(*[tag_hud(q, font_size=14, color=C_CAPA)
                           for q, _ in CAMBIOS])
        col_que.arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        col_por = VGroup(*[tag_hud(p, font_size=14, color=C_TENUE)
                           for _, p in CAMBIOS])
        col_por.arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        for a, b in zip(col_que, col_por):
            b.move_to(np.array([0.0, a.get_center()[1], 0.0]))
            b.align_to(col_que, LEFT)
            b.shift(RIGHT * 3.25)
        razones = VGroup(col_que, col_por)
        razones.move_to(DOWN * 1.95)
        lineas = [VGroup(col_que[k], col_por[k]) for k in range(len(CAMBIOS))]
        self.play(*[p_casa.capa(i).animate.set_stroke(C_PERDIDA, width=3.0)
                    for i in SE_VA],
                  *[vinculos[i].animate.set_stroke(C_PERDIDA)
                    for i in SE_VA],
                  run_time=0.8)
        self.play(LaggedStart(*[FadeIn(lineas[k], shift=0.10 * UP)
                                for k in CAMBIOS_IDA],
                              lag_ratio=0.55), run_time=1.8)
        self.wait(4.6)

        # --- momento: la capa que en casa no hace falta --------------------
        rot.mostrar(pie_curso("Y se anade una que en casa no hace falta: "
                              "aqui el ruido no se retransmite, se corrige."),
                    zona="abajo", run_time=0.5)
        et_nueva = tag_hud("no estaba en casa", font_size=16, color=C_OK)
        et_nueva.next_to(p_esp.capa(SE_ANADE), LEFT, buff=0.30)
        self.play(p_esp.capa(SE_ANADE).animate.set_stroke(C_OK, width=3.4),
                  p_esp.rotulo(SE_ANADE).animate.set_color(C_OK),
                  run_time=0.6)
        self.play(FadeIn(et_nueva),
                  FadeIn(lineas[CAMBIO_NUEVO], shift=0.10 * UP),
                  run_time=0.8)
        self.wait(5.2)

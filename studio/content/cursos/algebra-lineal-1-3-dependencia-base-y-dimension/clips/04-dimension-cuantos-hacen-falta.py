class Clip4(Scene):
    """1.3.4 - La dimension es cuantos vectores hacen falta para generarlo
    todo: uno para una recta, dos para un plano, tres para el espacio; ni
    uno mas, ni uno menos. Cierra la leccion. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Dimensión: cuántos hacen falta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: un vector, una recta -----------------------------------
        pl = plano_leccion(vivo=False)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Un solo vector. Su span es una recta: no "
                              "cubre el resto del plano."), zona="abajo",
                    run_time=0.5)
        w1 = vector(pl, W1_D, color=C_VEC, nombre=r"\vec w_1")
        linea1 = span_recta(pl, W1_D, color=C_IMG)
        self.play(Create(linea1), run_time=0.9)
        self.play(GrowArrow(w1.flecha), FadeIn(w1.etiqueta), run_time=0.8)
        dim1 = tag_hud("dimension = 1", font_size=20)
        panel = panel_derecha(dim1)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(2.6)

        # --- momento: dos vectores, el plano entero --------------------------
        rot.mostrar(pie_curso("Añadimos uno que no esté alineado: ya se "
                              "alcanza cualquier punto."), zona="abajo",
                    run_time=0.5)
        w2 = vector(pl, W2_D, color=C_VEC_2, nombre=r"\vec w_2")
        self.play(FadeOut(linea1), run_time=0.5)
        self.play(GrowArrow(w2.flecha), FadeIn(w2.etiqueta), run_time=0.8)
        self.play(Indicate(pl.fijo, color=C_IMG, scale_factor=1.02),
                  run_time=0.9)
        dim2 = tag_hud("dimension = 2", font_size=20)
        panel2 = panel_derecha(dim2)
        self.play(Transform(panel, panel2), run_time=0.6)
        self.wait(2.4)

        # --- momento: en el espacio hacen falta tres ---------------------------
        rot.mostrar(pie_curso("En el espacio, dos vectores solo generan "
                              "un plano dentro de él."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(pl), FadeOut(w1), FadeOut(w2), FadeOut(panel),
                  run_time=0.7)
        self.wait(0.3)

        es = espacio3()
        self.play(FadeIn(es), run_time=0.9)
        a3 = vector3(es, A3, color=C_I, nombre=r"\vec a")
        b3 = vector3(es, B3, color=C_J, nombre=r"\vec b")
        self.play(GrowArrow(a3.flecha), GrowArrow(b3.flecha), run_time=0.9)
        self.play(FadeIn(a3.etiqueta), FadeIn(b3.etiqueta), run_time=0.3)
        parche = plano_generado(es, A3, B3, color=C_IMG, opacidad=0.22)
        self.play(FadeIn(parche), run_time=1.0)
        self.wait(2.2)

        rot.mostrar(pie_curso("El tercero, fuera de ese plano, aporta la "
                              "dimensión que faltaba."), zona="abajo",
                    run_time=0.5)
        c3 = vector3(es, C3, color=C_K, nombre=r"\vec c")
        self.play(GrowArrow(c3.flecha), FadeIn(c3.etiqueta), run_time=1.0)
        dim3 = tag_hud("dimension = 3", font_size=20)
        panel3 = panel_derecha(dim3)
        self.play(FadeIn(panel3, shift=0.15 * LEFT), run_time=0.6)
        self.wait(2.8)

        # --- momento: triptico recta / plano / espacio -------------------------
        rot.mostrar(pie_curso("Uno, dos o tres: la dimensión es cuántos "
                              "hacen falta. Ni uno de más."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(es), FadeOut(a3), FadeOut(b3), FadeOut(c3),
                  FadeOut(parche), FadeOut(panel3), run_time=0.8)
        self.wait(0.2)

        centro = CENTRO_PLANO
        pl_r = plano(unidad=0.34, alcance=4, vivo=False)
        pl_r.move_to(LEFT * 4.6 + centro)
        v_r = vector(pl_r, W1_D, color=C_VEC, grosor=3.5)
        linea_r = span_recta(pl_r, W1_D, color=C_IMG, grosor=1.8, largo=4)
        cap_r = tag_hud("1 - recta", font_size=16)
        cap_r.next_to(pl_r, DOWN, buff=0.28)
        tri_r = VGroup(pl_r, linea_r, v_r, cap_r)

        pl_p = plano(unidad=0.34, alcance=4, vivo=False)
        pl_p.move_to(centro)
        v_p1 = vector(pl_p, W1_D, color=C_VEC, grosor=3.5)
        v_p2 = vector(pl_p, W2_D, color=C_VEC_2, grosor=3.5)
        cap_p = tag_hud("2 - plano", font_size=16)
        cap_p.next_to(pl_p, DOWN, buff=0.28)
        tri_p = VGroup(pl_p, v_p1, v_p2, cap_p)

        es_e = espacio3(unidad=0.34, alcance=3)
        es_e.move_to(RIGHT * 4.6 + centro)
        a_e = vector3(es_e, A3, color=C_I, grosor=3.0)
        b_e = vector3(es_e, B3, color=C_J, grosor=3.0)
        c_e = vector3(es_e, C3, color=C_K, grosor=3.0)
        cap_e = tag_hud("3 - espacio", font_size=16)
        cap_e.next_to(es_e, DOWN, buff=0.28)
        tri_e = VGroup(es_e, a_e, b_e, c_e, cap_e)

        self.play(FadeIn(tri_r), run_time=0.7)
        self.play(FadeIn(tri_p), run_time=0.7)
        self.play(FadeIn(tri_e), run_time=0.7)
        self.wait(3.4)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(self, rot, "Base: los justos.",
                       "Dimensión: cuántos son.",
                       "La próxima lección mueve el plano entero: nace "
                       "la matriz.", tri_r, tri_p, tri_e)

class Clip3(Scene):
    """2.2.3 - A B y B A no son la misma matriz: el orden en que se
    aplican dos movimientos SI importa. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El orden importa")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: dos rejillas identicas, lado a lado -------------------
        # plano_leccion() no acepta alcance; se usa plano(...) directo para
        # que la rejilla quepa en medio cuadro sin salirse. alcance=8 se
        # probo primero y, tras A B / B A (estiramiento maximo ~1.48x),
        # las dos rejillas se metian una en la otra por el centro: alcance=4
        # deja hueco de sobra incluso ya estiradas.
        pl_izq = plano(unidad=0.5, alcance=4, vivo=True)
        pl_izq.move_to(LEFT * 3.5 + CENTRO_PLANO)
        pl_der = plano(unidad=0.5, alcance=4, vivo=True)
        pl_der.move_to(RIGHT * 3.5 + CENTRO_PLANO)
        # Con fondo: sin el, el eje vertical de cada rejilla pasa justo por
        # el medio de la etiqueta (misma x que el centro del plano) y la
        # parte en dos.
        et_izq = _con_fondo(tag_hud("A B"), buff=0.1)
        et_izq.move_to(LEFT * 3.5 + UP * 2.7)
        et_der = _con_fondo(tag_hud("B A"), buff=0.1)
        et_der.move_to(RIGHT * 3.5 + UP * 2.7)
        self.play(FadeIn(pl_izq), FadeIn(pl_der), FadeIn(et_izq),
                  FadeIn(et_der), run_time=0.9)
        rot.mostrar(pie_curso("La misma rejilla, dos veces. A la "
                              "izquierda A B; a la derecha B A."),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- momento: se aplican en ordenes opuestos ------------------------
        rot.mostrar(pie_curso("Las mismas dos matrices, en el orden "
                              "opuesto. Observa."), zona="abajo",
                    run_time=0.5)
        self.wait(0.8)
        self.play(*pl_izq.anim_matriz(AB), *pl_der.anim_matriz(BA),
                  run_time=2.4)
        self.wait(3.8)

        # --- momento: dos matrices distintas ---------------------------------
        rot.mostrar(pie_curso("Dos rejillas, dos formas distintas: no es "
                              "el mismo movimiento."), zona="abajo",
                    run_time=0.5)
        # y = -1.9, no -2.5: mas abajo el corchete de la matriz entra en la
        # zona del pie (MARGEN_PIE) y se come palabras del texto.
        mat_ab = matriz_columnas(AB, font_size=30)
        mat_ba = matriz_columnas(BA, font_size=30)
        grupo_ab = _con_fondo(mat_ab, buff=0.16, opacidad=0.78)
        grupo_ab.move_to(LEFT * 3.5 + DOWN * 1.9)
        grupo_ba = _con_fondo(mat_ba, buff=0.16, opacidad=0.78)
        grupo_ba.move_to(RIGHT * 3.5 + DOWN * 1.9)
        self.play(FadeIn(grupo_ab, shift=0.1 * UP),
                  FadeIn(grupo_ba, shift=0.1 * UP), run_time=0.7)
        self.wait(4.2)

        # --- momento: la diagonal se intercambia ------------------------
        rot.mostrar(pie_curso(f"Esa esquina mide {fmt(AB[1, 1], 2)} en "
                              f"A B, y {fmt(BA[1, 1], 2)} en B A."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(mat_ab.entrada(1, 1), color=C_J,
                           scale_factor=1.3),
                  Indicate(mat_ba.entrada(1, 1), color=C_J,
                           scale_factor=1.3), run_time=1.0)
        self.wait(3.6)

        rot.mostrar(pie_curso("Multiplicar matrices no conmuta: el orden "
                              "es parte de la cuenta."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

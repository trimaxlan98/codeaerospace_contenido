class Clip1(Scene):
    """3.2.1 - La imagen de una matriz es el conjunto de sitios a los que
    puede llegar: con A todo el plano cae en una recta; con B la rejilla se
    deforma pero sigue llenando el plano. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La imagen: a dónde puede llegar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la pregunta -------------------------------------------
        rot.mostrar(pie_curso("Una matriz mueve todo el plano. ¿A qué "
                              "sitios puede llegar?"), zona="abajo",
                    run_time=0.5)
        pl = plano_leccion()
        v = vector(pl, V_STAR, color=C_VEC, nombre=r"\vec v",
                   etiqueta_dir=RIGHT)
        self.play(FadeIn(pl), run_time=0.9)
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.8)
        self.wait(1.5)
        panel_a = panel_derecha(matriz_columnas(A_PLANA),
                                tag_hud("det = " + fmt(DET_PLANA)))
        self.play(FadeIn(panel_a, shift=0.15 * LEFT), run_time=0.6)
        self.wait(1.2)

        # --- momento: A aplasta el plano sobre una recta --------------------
        rot.mostrar(pie_curso("Sus dos columnas caen en la misma recta: la "
                              "rejilla se aplasta."), zona="abajo",
                    run_time=0.5)
        self.play(*pl.anim_matriz(A_PLANA, v), run_time=2.0)
        self.wait(3.0)

        rot.mostrar(pie_curso("Ahí está todo destino posible: esa recta es "
                              "la imagen de A."), zona="abajo", run_time=0.5)
        # La imagen COINCIDE con la recta a la que se aplasto la rejilla, asi
        # que se pinta encima y OPACA: con opacidad < 1 el verde se mezcla
        # con el azul de la rejilla viva y sale un cian que no es ningun rol.
        recta_img = span_recta(pl, DIR_IMG, color=C_IMG, grosor=5.0,
                               opacidad=1.0)
        et_img = tag_hud("imagen de A", font_size=17, color=C_IMG)
        et_img.next_to(pl.p(-2.6 * DIR_IMG), UP + LEFT, buff=0.10)
        self.play(Create(recta_img), FadeIn(et_img), run_time=0.9)
        self.bring_to_front(v)
        self.wait(4.1)

        # --- momento: B no pierde nada --------------------------------------
        rot.mostrar(pie_curso("Cambiemos la segunda columna: ahora se sale "
                              "de la recta."), zona="abajo", run_time=0.5)
        panel_b = panel_derecha(matriz_columnas(A_LLENA),
                                tag_hud("det = " + fmt(DET_LLENA)))
        self.play(FadeOut(panel_a), FadeOut(recta_img), FadeOut(et_img),
                  run_time=0.4)
        self.play(FadeIn(panel_b, shift=0.15 * LEFT), run_time=0.6)
        self.wait(4.0)

        rot.mostrar(pie_curso("La rejilla se deforma, pero no se aplasta: "
                              "sigue llenando el plano."), zona="abajo",
                    run_time=0.5)
        self.play(*pl.anim_matriz(A_LLENA, v), run_time=2.0)
        self.wait(3.0)

        # --- momento: las dos imagenes, lado a lado -------------------------
        rot.mostrar(pie_curso("Las dos imágenes, lado a lado: una recta, o "
                              "el plano entero."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(pl), FadeOut(v), FadeOut(panel_b), run_time=0.6)
        mini_a = plano(unidad=MINI_UNIDAD, alcance=MINI_ALCANCE)
        mini_a.move_to(MINI_CENTROS[0])
        mini_b = plano(unidad=MINI_UNIDAD, alcance=MINI_ALCANCE)
        mini_b.move_to(MINI_CENTROS[1])
        self.play(FadeIn(mini_a), FadeIn(mini_b), run_time=0.7)
        self.play(*mini_a.anim_matriz(A_PLANA), *mini_b.anim_matriz(A_LLENA),
                  run_time=1.8)
        tag_a = tag_hud("imagen: una recta", font_size=18, color=C_IMG)
        tag_a.move_to(MINI_CENTROS[0] + UP * 2.4)
        tag_b = tag_hud("imagen: todo el plano", font_size=18, color=C_IMG)
        tag_b.move_to(MINI_CENTROS[1] + UP * 2.4)
        self.play(FadeIn(tag_a), FadeIn(tag_b), run_time=0.5)
        self.wait(2.2)

        rot.mostrar(pie_curso("¿Y cómo se mide esa diferencia? Con un "
                              "número: el rango."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

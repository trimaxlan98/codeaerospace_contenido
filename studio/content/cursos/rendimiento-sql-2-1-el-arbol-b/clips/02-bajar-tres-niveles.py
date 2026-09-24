class Clip2(Scene):
    """2.1.2 - Por que bastan tres niveles: una pagina intermedia guarda
    muchas entradas (llave -> pagina hija); por eso cada nivel multiplica
    el alcance. La ruta raiz - intermedio - hoja se enciende en verde y
    solo abre tres paginas. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Bajar tres niveles"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        q = S.codigo(["SELECT *", "FROM pedidos",
                      "WHERE id_pedido = 750000"], font_size=20)
        q.to_corner(UL, buff=0.6).shift(DOWN * 0.8)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(1.0)

        arbol = S.ArbolB(anchos=(1, 4, 12), ancho=6.2, alto=3.6, lado=0.4,
                         color=C_TENUE)
        arbol.move_to(RIGHT * 3.3 + DOWN * 0.45)
        self.play(FadeIn(arbol.niveles[0]), run_time=0.5)
        self.play(Create(arbol.aristas[:4]), FadeIn(arbol.niveles[1]), run_time=0.7)
        self.play(Create(arbol.aristas[4:]), FadeIn(arbol.niveles[2]), run_time=0.8)

        etq_raiz = tag_junto(arbol.niveles[0], "raiz", UP, buff=0.3)
        etq_hojas = tag_junto(arbol.niveles[2], "hojas", DOWN, buff=0.3)
        self.play(FadeIn(etq_raiz), FadeIn(etq_hojas), run_time=0.5)
        self.wait(1.0)

        ruta = arbol.ruta(8)

        # --- por que basta con tres niveles: se amplia una pagina --------
        nodo = arbol.niveles[1][0]
        grande = S.pagina(1.8, 1.4, renglones=0, color=C_INDICE, relleno=0.05,
                          grosor=2.0)
        grande.move_to(LEFT * 2.6 + DOWN * 0.5)
        guia = DashedLine(nodo.get_left(), grande.get_right(), dash_length=0.1,
                          stroke_color=C_INDICE, stroke_width=1.6)
        self.play(Create(guia), TransformFromCopy(nodo, grande), run_time=1.1)
        etiqueta = tag_junto(grande, "una pagina intermedia", UP, buff=0.25)
        self.play(FadeIn(etiqueta), run_time=0.5)
        self.wait(0.8)

        def entrada(ancho=0.45):
            flecha = Arrow(LEFT * ancho / 2, RIGHT * 0.04, buff=0,
                          stroke_width=2.0, color=C_INDICE,
                          max_tip_length_to_length_ratio=0.3)
            hija = Square(side_length=0.13, stroke_color=C_INDICE,
                         stroke_width=1.6, fill_color=C_INDICE,
                         fill_opacity=0.45)
            hija.next_to(flecha, RIGHT, buff=0.06)
            return VGroup(flecha, hija)

        filas_grande = VGroup()
        for y in (0.32, 0.0, -0.38):
            e = entrada()
            e.move_to(grande.get_center() + LEFT * 0.28 + UP * y)
            filas_grande.add(e)
        puntos = VGroup(*[Dot(radius=0.02, color=C_TENUE) for _ in range(3)])
        puntos.arrange(DOWN, buff=0.05)
        puntos.move_to(grande.get_center() + LEFT * 0.28 + UP * -0.19)
        filas_grande.add(puntos)
        self.play(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.1) for f in filas_grande],
                              lag_ratio=0.25), run_time=1.5)
        self.wait(1.2)

        fan_tag = tag_hud(f"{S.miles(FAN)} entradas por pagina", font_size=18)
        fan_tag.next_to(grande, DOWN, buff=0.25)
        self.play(FadeIn(fan_tag), run_time=0.5)
        self.wait(2.4)

        # --- la busqueda real: solo tres paginas ---------------------------
        cont = Contador(0, rotulo="lecturas", font_size=40, digitos=3)
        cont.next_to(q, DOWN, buff=0.7).align_to(q, LEFT)
        self.play(FadeIn(cont), run_time=0.4)
        self.wait(0.5)

        for k, pag in enumerate(ruta):
            self.play(pag[0].animate.set_fill(C_BUENO, 0.8).set_stroke(C_BUENO),
                      run_time=0.6)
            cont.fijar(k + 1)
            self.wait(1.0)
        self.wait(0.6)

        rot.mostrar(motor_pie(lecturas(M["pk_seek"])), zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"{PROF} niveles para bajar"), zona="abajo",
                    run_time=0.5)
        self.play(*[Indicate(p, color=C_BUENO, scale_factor=1.12) for p in ruta],
                  run_time=1.2)
        self.wait(5.5)

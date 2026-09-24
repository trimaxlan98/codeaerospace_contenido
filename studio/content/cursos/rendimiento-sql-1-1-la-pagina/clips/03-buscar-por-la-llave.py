class Clip3(Scene):
    """1.1.3 - Buscar un pedido por su llave: el motor baja por un arbol de
    tres niveles y abre tres paginas. El contador se queda en 3. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Buscar por la llave"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        q = S.codigo(["SELECT *", "FROM pedidos",
                      "WHERE id_pedido = 750000"], font_size=20)
        q.to_corner(UL, buff=0.6).shift(DOWN * 0.8)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(1.6)

        arbol = S.ArbolB(anchos=(1, 4, 12), ancho=6.8, alto=3.6, lado=0.4,
                         color=C_TENUE)
        arbol.move_to(RIGHT * 2.9 + DOWN * 0.45)
        self.play(FadeIn(arbol.niveles[0]), run_time=0.5)
        self.play(Create(arbol.aristas[:4]), FadeIn(arbol.niveles[1]), run_time=0.8)
        self.play(Create(arbol.aristas[4:]), FadeIn(arbol.niveles[2]), run_time=0.9)
        nombres = ["raiz", "intermedio", "hojas"]
        tags = VGroup()
        for fila, n in zip(arbol.niveles, nombres):
            t = tag_junto(fila, n, LEFT, buff=0.3)
            t.set_x(arbol.get_left()[0] - 0.35 - t.width / 2)
            tags.add(t)
        self.play(FadeIn(tags), run_time=0.5)
        self.wait(2.8)

        cont = Contador(0, rotulo="lecturas", font_size=40, digitos=3)
        cont.next_to(q, DOWN, buff=0.7).align_to(q, LEFT)
        self.play(FadeIn(cont), run_time=0.4)
        self.wait(0.6)

        ruta = arbol.ruta(8)
        for k, pag in enumerate(ruta):
            self.play(pag[0].animate.set_fill(C_BUENO, 0.8).set_stroke(C_BUENO),
                      run_time=0.6)
            cont.fijar(k + 1)
            self.wait(1.0)
        punto = Dot(ruta[-1].get_bottom() + DOWN * 0.25, radius=0.08, color=C_BUENO)
        fila = tag_junto(punto, "750000", DOWN, buff=0.1, color=C_BUENO)
        self.play(FadeIn(punto), FadeIn(fila), run_time=0.5)
        self.wait(1.6)

        rot.mostrar(motor_pie(lecturas(M["pk_seek"])), zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"{PROF} niveles para {S.miles(FILAS_PED)} filas"),
                    zona="abajo", run_time=0.5)
        self.play(*[Indicate(p, color=C_BUENO, scale_factor=1.12) for p in ruta],
                  run_time=1.2)
        self.wait(7.0)

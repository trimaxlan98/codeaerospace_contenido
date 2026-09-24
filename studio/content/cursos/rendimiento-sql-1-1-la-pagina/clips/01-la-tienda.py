class Clip1(Scene):
    """1.1.1 - La tienda: tres tablas con sus filas, una consulta, y la
    pregunta de como medir su costo. El tiempo cambia de maquina a maquina;
    las paginas leidas, no. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Una tienda en linea"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- tres tablas, alto proporcional a la raiz de sus filas -------
        datos = [("clientes", FILAS_CLI), ("pedidos", FILAS_PED),
                 ("detalle", FILAS_DET)]
        alto_max = 3.6
        tablas = VGroup()
        for i, (nombre, n) in enumerate(datos):
            h = alto_max * (n / FILAS_DET) ** 0.5
            caja = Rectangle(width=1.7, height=h, stroke_color=C_INDICE,
                             stroke_width=2, fill_color=C_INDICE,
                             fill_opacity=0.12)
            rayas = VGroup(*[Line(caja.get_left() + RIGHT * 0.15 + UP * y,
                                  caja.get_right() + LEFT * 0.15 + UP * y,
                                  stroke_color=C_INDICE, stroke_width=1,
                                  stroke_opacity=0.45)
                             for y in np.arange(-h / 2 + 0.18, h / 2 - 0.1, 0.18)])
            nom = Text(nombre, font_size=24, color=C_TITULO)
            num = tag_hud(S.miles(n), font_size=20)
            g = VGroup(caja, rayas)
            nom.next_to(caja, UP, buff=0.16)
            num.next_to(caja, DOWN, buff=0.16)
            tablas.add(VGroup(g, nom, num))
        tablas.arrange(RIGHT, buff=0.7, aligned_edge=DOWN)
        tablas.move_to(LEFT * 3.4 + DOWN * 0.3)
        for t in tablas:
            self.play(FadeIn(t[0], shift=UP * 0.2), FadeIn(t[1]), run_time=0.7)
            self.play(FadeIn(t[2]), run_time=0.4)
            self.wait(0.9)
        et = tag_junto(tablas, "filas por tabla", DOWN, buff=0.2)
        self.play(FadeIn(et), run_time=0.4)
        self.wait(3.0)

        # --- la consulta ---------------------------------------------------
        q = S.codigo(["SELECT id_pedido, fecha_pedido, total",
                      "FROM pedidos",
                      "WHERE id_cliente = 501"], font_size=20)
        q.move_to(RIGHT * 3.4 + UP * 1.3)
        self.play(FadeIn(q, shift=LEFT * 0.2), run_time=0.8)
        marca_from = SurroundingRectangle(q.lineas[1], color=C_TITULO, buff=0.06,
                                          stroke_width=2)
        self.play(Create(marca_from),
                  tablas[1][0][0].animate.set_stroke(C_TITULO, width=3).set_fill(C_INDICE, 0.3),
                  run_time=0.8)
        self.wait(3.4)

        # --- como se mide: el tiempo no, las paginas si -------------------
        reloj = VGroup(Circle(radius=0.42, stroke_color=C_TENUE, stroke_width=3),
                       Line(ORIGIN, UP * 0.3, stroke_color=C_TENUE, stroke_width=3),
                       Line(ORIGIN, RIGHT * 0.22, stroke_color=C_TENUE, stroke_width=3))
        reloj.move_to(RIGHT * 2.0 + DOWN * 1.2)
        t_reloj = Text("tiempo", font_size=26, color=C_TENUE)
        t_reloj.next_to(reloj, RIGHT, buff=0.3)
        self.play(FadeIn(reloj), FadeIn(t_reloj), run_time=0.6)
        self.play(Rotate(reloj[1], angle=-4 * PI, about_point=reloj[0].get_center()),
                  run_time=1.6)
        dep = tag_junto(t_reloj, "cambia cada vez", RIGHT, buff=0.3)
        self.play(FadeIn(dep), run_time=0.4)
        self.wait(1.6)
        tache = Line(t_reloj.get_left() + LEFT * 0.1,
                     t_reloj.get_right() + RIGHT * 0.1,
                     stroke_color=C_MALO, stroke_width=5)
        self.play(Create(tache), run_time=0.5)
        self.wait(0.8)

        hoja = S.pagina(0.64, 0.84, renglones=4, color=C_MOTOR, relleno=0.15)
        hoja.move_to(RIGHT * 2.0 + DOWN * 2.45)
        t_pag = Text("paginas leidas", font_size=26, color=C_MOTOR)
        t_pag.next_to(hoja, RIGHT, buff=0.3)
        self.play(FadeIn(hoja, shift=UP * 0.2), FadeIn(t_pag), run_time=0.7)
        self.play(Indicate(hoja, color=C_MOTOR, scale_factor=1.15), run_time=1.0)
        self.wait(6.6)

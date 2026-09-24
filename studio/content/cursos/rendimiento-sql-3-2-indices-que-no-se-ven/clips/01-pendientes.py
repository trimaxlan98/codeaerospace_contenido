class Clip1(Scene):
    """3.2.1 - Los pendientes son una fraccion minima de la tabla (2,791 de
    1.5 M): en un muro grande, solo unas pocas celdas tienen alguno, y
    todas caen al final (los pedidos recientes, por construccion de los
    datos: la tabla crece por fecha). Un panel los consulta todo el dia.
    (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Pocos pedidos pendientes"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        cols, fils = 32, 13
        total = cols * fils
        muro = S.MuroPaginas(columnas=cols, filas=fils, lado=0.185, sep=0.05,
                             color=C_TENUE, opacidad=0.14)
        muro.move_to(LEFT * 2.3 + DOWN * 0.5)
        nom = Text("pedidos", font_size=26, color=C_TITULO)
        nom.next_to(muro, UP, buff=0.22).align_to(muro, LEFT)
        self.play(FadeIn(nom), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in muro],
                              lag_ratio=0.0028), run_time=2.4)
        self.wait(1.4)

        # --- solo unas pocas celdas tienen algun pendiente, y al final ----
        indices = celdas_pendientes(total)
        self.play(LaggedStart(*muro.encender(indices, C_CALCULO, 0.9),
                              lag_ratio=0.08), run_time=1.6)
        self.wait(0.6)
        marca = SurroundingRectangle(
            VGroup(*[muro.celda(i) for i in indices]), color=C_CALCULO,
            buff=0.14, stroke_width=2.2)
        self.play(Create(marca), run_time=0.7)
        et = tag_junto(marca, "pedidos recientes", RIGHT, buff=0.3,
                       color=C_CALCULO)
        self.play(FadeIn(et), run_time=0.4)
        self.wait(2.6)

        rot.mostrar(cifra_pie(f"{S.miles(PENDIENTES)} pendientes"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)
        rot.mostrar(cifra_pie(f"{FRAC_PENDIENTES:.2f}% de la tabla"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- un panel que los consulta todo el dia -------------------------
        consulta = S.codigo(["WHERE estatus = 'pendiente'"], font_size=20)
        consulta.next_to(muro, RIGHT, buff=0.45).align_to(muro, UP)
        guia = DashedLine(marca.get_corner(UR), consulta.get_corner(DL),
                          dash_length=0.1, stroke_color=C_CALCULO,
                          stroke_width=1.6)
        self.play(Create(guia), run_time=0.9)
        self.play(FadeIn(consulta, shift=LEFT * 0.2), run_time=0.7)
        piloto = Dot(radius=0.07, color=C_BUENO)
        piloto.move_to(consulta.fondo.get_corner(UR) + LEFT * 0.2 + DOWN * 0.2)
        self.play(FadeIn(piloto), run_time=0.3)
        for _ in range(3):
            self.play(piloto.animate.set_opacity(0.2), run_time=0.4)
            self.play(piloto.animate.set_opacity(1.0), run_time=0.4)
        etp = tag_junto(consulta, "se consulta seguido", DOWN, buff=0.24)
        self.play(FadeIn(etp), run_time=0.4)
        self.wait(6.2)

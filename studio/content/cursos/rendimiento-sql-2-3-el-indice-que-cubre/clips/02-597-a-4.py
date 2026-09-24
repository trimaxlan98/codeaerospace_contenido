class Clip2(Scene):
    """2.3.2 - La ruta de tres niveles llega a la hoja ancha del clip 1: no
    hace falta volver al agrupado (el viaje del clip 2.2). Duelo 597 (el
    lookup) contra 4 (la hoja que ya trae todo). (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Sin viaje de vuelta"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        q = S.codigo(["SELECT fecha_pedido, total",
                      "FROM pedidos",
                      "WHERE id_cliente = 501"], font_size=19)
        q.to_corner(UL, buff=0.55).shift(DOWN * 0.6)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(0.8)

        arbol = S.ArbolB(anchos=(1, 4, 12), ancho=6.0, alto=2.6, lado=0.34,
                         color=C_TENUE)
        arbol.move_to(RIGHT * 2.4 + UP * 1.35)
        self.play(FadeIn(arbol.niveles[0]), run_time=0.4)
        self.play(Create(arbol.aristas[:4]), FadeIn(arbol.niveles[1]), run_time=0.6)
        self.play(Create(arbol.aristas[4:]), FadeIn(arbol.niveles[2]), run_time=0.7)
        self.wait(0.6)

        idx = 8
        ruta = arbol.ruta(idx)
        vecina = arbol.hojas[idx + 1]

        cont = Contador(0, rotulo="lecturas", font_size=36, digitos=3)
        cont.next_to(q, DOWN, buff=0.6).align_to(q, LEFT)
        self.play(FadeIn(cont), run_time=0.4)
        for k, pag in enumerate(ruta):
            self.play(pag[0].animate.set_fill(C_BUENO, 0.8).set_stroke(C_BUENO),
                      run_time=0.5)
            cont.fijar(k + 1)
            self.wait(0.5)
        self.play(vecina[0].animate.set_fill(C_BUENO, 0.8).set_stroke(C_BUENO),
                  run_time=0.5)
        cont.fijar(4)
        et_hojas = tag_junto(VGroup(ruta[-1], vecina), "dos hojas", DOWN,
                             buff=0.3, color=C_BUENO)
        self.play(FadeIn(et_hojas), run_time=0.4)
        self.wait(1.0)

        # --- la hoja ya trae todo: se amplia, sin viaje de vuelta --------
        hoja = fila_de([celda_campo(n, color=C_BUENO)
                        for n in ("id_cliente", "id_pedido", "fecha_pedido",
                                  "estatus", "total")], buff=0.14)
        hoja.move_to(DOWN * 2.15)
        origen = VGroup(ruta[-1], vecina).get_bottom()
        guia = DashedLine(origen, hoja.get_top(), dash_length=0.08,
                          stroke_color=C_BUENO, stroke_width=1.6)
        self.play(FadeOut(et_hojas), run_time=0.3)
        self.play(Create(guia), FadeIn(hoja, shift=UP * 0.15), run_time=0.9)
        self.wait(0.6)

        tabla = RoundedRectangle(width=1.5, height=1.0, corner_radius=0.1,
                                 stroke_color=C_TENUE, stroke_width=1.8,
                                 stroke_opacity=0.6)
        tabla.move_to(LEFT * 5.25 + DOWN * 2.15)
        t_tabla = Text("agrupado", font_size=20, color=C_TENUE)
        t_tabla.set_opacity(0.7)
        t_tabla.move_to(tabla)
        flecha = DashedLine(hoja.get_left(), tabla.get_right(), buff=0.15,
                            dash_length=0.08, stroke_color=C_TENUE,
                            stroke_width=1.6, stroke_opacity=0.6)
        cruz = VGroup(
            Line(flecha.get_center() + UP * 0.16 + LEFT * 0.16,
                flecha.get_center() + DOWN * 0.16 + RIGHT * 0.16,
                stroke_color=C_MALO, stroke_width=3.5),
            Line(flecha.get_center() + UP * 0.16 + RIGHT * 0.16,
                flecha.get_center() + DOWN * 0.16 + LEFT * 0.16,
                stroke_color=C_MALO, stroke_width=3.5))
        self.play(FadeIn(tabla, t_tabla, shift=LEFT * 0.1), run_time=0.6)
        self.play(Create(flecha), run_time=0.5)
        self.play(Create(cruz), run_time=0.4)
        et_sin = tag_junto(tabla, "sin viaje", DOWN, buff=0.24, color=C_BUENO)
        self.play(FadeIn(et_sin), run_time=0.4)
        rot.mostrar(motor_pie(lecturas(M["c501_cubriente"])), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- el duelo: 597 contra 4 ---------------------------------------
        primero = VGroup(q, cont, arbol, et_hojas, hoja, guia, tabla, t_tabla,
                         flecha, cruz, et_sin)
        self.play(FadeOut(primero), run_time=0.7)
        rot.limpiar(run_time=0.3)

        largo = 8.0
        maximo = M["c501_lookup"]
        base_x = LEFT * 4.6
        bar_rojo = S.barra_lecturas(M["c501_lookup"], maximo, largo=largo,
                                    alto=0.55, color=C_MALO, log=True)
        bar_rojo.shift(base_x + UP * 0.9)
        bar_verde = S.barra_lecturas(M["c501_cubriente"], maximo, largo=largo,
                                     alto=0.55, color=C_BUENO, log=True)
        bar_verde.shift(base_x + DOWN * 0.9)

        base = Line(base_x + UP * 1.7, base_x + DOWN * 1.7,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.5)

        lab_r = tag_junto(bar_rojo, "con lookup", LEFT, buff=0.3, color=C_MALO)
        lab_v = tag_junto(bar_verde, "con la hoja", LEFT, buff=0.3, color=C_BUENO)
        self.play(FadeIn(bar_rojo, shift=RIGHT * 0.2), FadeIn(lab_r), run_time=0.8)
        self.wait(0.4)
        self.play(FadeIn(bar_verde, shift=RIGHT * 0.2), FadeIn(lab_v), run_time=0.8)
        self.wait(1.0)

        tag_r = tag_motor(lecturas(M["c501_lookup"]))
        tag_r.next_to(bar_rojo, RIGHT, buff=0.2)
        tag_v = tag_motor(lecturas(M["c501_cubriente"]))
        tag_v.next_to(bar_verde, RIGHT, buff=0.2)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(0.6)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(2.4)

        razon = S.razon(M["c501_lookup"], M["c501_cubriente"])
        rot.mostrar(cifra_pie(f"{razon:.0f}x menos lecturas"), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(bar_rojo, color=C_MALO, scale_factor=1.03),
                  Indicate(bar_verde, color=C_BUENO, scale_factor=1.08),
                  run_time=1.0)
        self.wait(6.5)

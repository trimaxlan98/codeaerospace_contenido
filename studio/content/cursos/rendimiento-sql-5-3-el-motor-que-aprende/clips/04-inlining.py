class Clip4(Scene):
    """5.3.4 - SQL Server 2025 funde la funcion escalar dentro de la
    consulta (inlining): las dos piezas separadas (Select y la funcion)
    se vuelven una sola consulta, un solo plan. Duelo final: 17.6 s
    (rojo, antes) contra 0.85 s (verde, ahora), ambar en cada barra,
    20.7x menos tiempo en cian. Cierre de la leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Inlining"), zona="arriba", run_time=0.6)
        self.wait(0.6)

        # --- antes: dos piezas separadas ---------------------------------------
        sel_op = S.operador("Select", color=C_TITULO, ancho=2.3)
        fn_op = S.operador("fn_TotalCliente", color=C_TITULO, ancho=3.2)
        sel_op.move_to(LEFT * 3.4 + UP * 1.7)
        fn_op.move_to(RIGHT * 1.2 + UP * 1.7)
        flecha_ant = Arrow(fn_op.get_left(), sel_op.get_right(), buff=0.12,
                           color=C_TENUE, stroke_width=2.6,
                           max_tip_length_to_length_ratio=0.14)
        self.play(FadeIn(sel_op, shift=RIGHT * 0.15), run_time=0.5)
        self.play(Create(flecha_ant), FadeIn(fn_op, shift=LEFT * 0.15),
                  run_time=0.7)
        tag_ant = tag_junto(VGroup(sel_op, fn_op), "dos piezas separadas",
                            DOWN, buff=0.32)
        self.play(FadeIn(tag_ant), run_time=0.4)
        self.wait(1.8)

        grupo_ant = VGroup(sel_op, fn_op, flecha_ant, tag_ant)
        self.play(FadeOut(grupo_ant), run_time=0.6)

        # --- ahora: una sola consulta -------------------------------------------
        fusion = caja_tabla("SELECT + fn_TotalCliente", ancho=6.2, alto=1.35,
                           color=C_BUENO, font_size=23)
        fusion.move_to(UP * 1.6)
        self.play(FadeIn(fusion, shift=UP * 0.15), run_time=0.7)
        tag_fus = tag_junto(fusion, "una sola consulta", DOWN, buff=0.3,
                            color=C_BUENO)
        self.play(FadeIn(tag_fus), run_time=0.4)
        self.wait(2.2)

        grupo_fus = VGroup(fusion, tag_fus)
        self.play(FadeOut(grupo_fus), run_time=0.6)

        # --- el duelo de tiempos: lineal (como en la 5.3.2) ----------------------
        largo = 7.0
        maximo = UDF_140
        base_x = LEFT * 3.5

        bar_buena = S.barra_lecturas(UDF_170, maximo, largo=largo, alto=0.7,
                                     color=C_BUENO, log=False)
        bar_buena.shift(base_x + UP * 0.6)
        bar_mala = S.barra_lecturas(UDF_140, maximo, largo=largo, alto=0.7,
                                    color=C_MALO, log=False)
        bar_mala.shift(base_x + DOWN * 1.2)

        lab_b = tag_junto(bar_buena, "con inlining", LEFT, buff=0.3,
                          color=C_BUENO)
        self.play(GrowFromEdge(bar_buena, LEFT), FadeIn(lab_b), run_time=0.9)
        tag_b = tag_motor(tiempo(UDF_170))
        tag_b.next_to(bar_buena, RIGHT, buff=0.22)
        self.play(FadeIn(tag_b), run_time=0.4)
        self.wait(0.8)

        lab_m = tag_junto(bar_mala, "fila por fila", LEFT, buff=0.3,
                          color=C_MALO)
        self.play(GrowFromEdge(bar_mala, LEFT), FadeIn(lab_m), run_time=0.9)
        tag_m = tag_motor(tiempo(UDF_140))
        tag_m.next_to(bar_mala, RIGHT, buff=0.22)
        self.play(FadeIn(tag_m), run_time=0.4)
        self.wait(1.6)

        rot.mostrar(cifra_pie(f"{RAZON_UDF:.1f}x menos tiempo"),
                   zona="abajo", run_time=0.5)
        self.play(Indicate(bar_buena, color=C_BUENO, scale_factor=1.06),
                  Indicate(bar_mala, color=C_MALO, scale_factor=1.03),
                  run_time=1.0)
        self.wait(3.0)

        grupo_duelo = VGroup(bar_buena, lab_b, tag_b, bar_mala, lab_m, tag_m)
        cierre_leccion(self, rot, "Actualizar el motor",
                       "tambien es optimizar.", grupo_duelo, espera=9.0)

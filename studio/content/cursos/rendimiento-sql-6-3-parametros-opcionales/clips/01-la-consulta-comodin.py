class Clip1(Scene):
    """6.3.1 - El patron comodin: WHERE (@x IS NULL OR col = @x), igual
    para los 3 filtros opcionales del procedimiento. Tres llamadas MUY
    distintas (solo cliente, solo estatus, solo fecha) entran al MISMO
    procedimiento. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La consulta comodin"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el patron: una condicion opcional, su propio momento -------------
        patron = S.codigo(["WHERE (@id_cliente IS NULL",
                           "  OR id_cliente = @id_cliente)"], font_size=26)
        patron.move_to(UP * 0.3)
        self.play(FadeIn(patron, shift=DOWN * 0.2), run_time=0.8)
        self.wait(1.8)
        et_patron = tag_junto(patron, "igual para los 3", DOWN, buff=0.3)
        self.play(FadeIn(et_patron), run_time=0.4)
        self.wait(2.6)

        self.play(FadeOut(VGroup(patron, et_patron)), run_time=0.6)
        self.wait(0.2)

        # --- el mismo procedimiento -------------------------------------------
        proc = S.operador("buscar_pedidos", color=C_TITULO, ancho=3.6,
                          alto=1.0, font_size=23)
        proc.move_to(RIGHT * 3.3)
        self.play(FadeIn(proc, shift=LEFT * 0.2), run_time=0.6)
        self.wait(0.5)

        llamadas = tres_llamadas(font_size=22)
        llamadas.move_to(LEFT * 3.5)
        etiquetas = ["solo cliente", "solo estatus", "solo fecha"]
        for call, et in zip(llamadas, etiquetas):
            self.play(FadeIn(call, shift=RIGHT * 0.2), run_time=0.6)
            flecha = Arrow(call.get_right(), proc.get_left(), buff=0.18,
                          stroke_width=3.2, color=C_TENUE,
                          max_tip_length_to_length_ratio=0.1)
            lab = tag_junto(call, et, DOWN, buff=0.16)
            self.play(Create(flecha), FadeIn(lab), run_time=0.6)
            self.wait(0.9)

        self.play(Indicate(proc, color=C_TITULO, scale_factor=1.1), run_time=0.9)
        et_uno = tag_junto(proc, "un solo plan", UP, buff=0.26)
        self.play(FadeIn(et_uno), run_time=0.5)
        self.wait(11.9)

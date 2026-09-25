class Clip4(Scene):
    """7.1.4 - SQL Server 2025 puede matar una consulta danina en el acto:
    el hint ABORT_QUERY_EXECUTION la aborta con el error 8778 y el resto
    del servidor sigue. Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Abortar una consulta"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        cod = S.codigo(["SELECT * FROM pedidos",
                       "WHERE total > 1000000",
                       "OPTION (USE HINT('ABORT_QUERY_EXECUTION'))"],
                      font_size=17)
        cod.to_edge(UP, buff=1.15)
        self.play(FadeIn(cod, shift=DOWN * 0.2), run_time=0.8)
        marca = SurroundingRectangle(cod.lineas[2], color=C_MALO, buff=0.06,
                                     stroke_width=2.2)
        self.play(Create(marca), run_time=0.6)
        et_hint = tag_junto(cod, "un reporte pesado", DOWN, buff=0.25)
        self.play(FadeIn(et_hint), run_time=0.4)
        self.wait(1.8)

        # --- varias consultas: una se aborta, las demas pasan --------------
        fila_y = -0.9
        xs = np.linspace(-4.6, 4.6, 5)
        cajas = VGroup()
        for i, x in enumerate(xs):
            malo = (i == 2)
            color = C_MALO if malo else C_BUENO
            caja = RoundedRectangle(width=1.5, height=0.85, corner_radius=0.08,
                                    stroke_color=color, stroke_width=2.4,
                                    fill_color=color, fill_opacity=0.12)
            caja.move_to([x, fila_y, 0])
            cajas.add(caja)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cajas],
                              lag_ratio=0.12), run_time=1.6)
        self.wait(0.6)

        marcas_estado = VGroup()
        for i, x in enumerate(xs):
            if i == 2:
                m = VGroup(Line(UP * 0.16 + LEFT * 0.16,
                               DOWN * 0.16 + RIGHT * 0.16,
                               stroke_color=C_MALO, stroke_width=5),
                          Line(UP * 0.16 + RIGHT * 0.16,
                               DOWN * 0.16 + LEFT * 0.16,
                               stroke_color=C_MALO, stroke_width=5))
            else:
                m = VGroup(Line(LEFT * 0.16 + UP * 0.0,
                               RIGHT * 0.0 + DOWN * 0.14,
                               stroke_color=C_BUENO, stroke_width=5),
                          Line(RIGHT * 0.0 + DOWN * 0.14,
                               RIGHT * 0.2 + UP * 0.16,
                               stroke_color=C_BUENO, stroke_width=5))
            m.move_to([x, fila_y, 0])
            marcas_estado.add(m)
        self.play(LaggedStart(*[FadeIn(m, scale=1.3) for m in marcas_estado],
                              lag_ratio=0.12), run_time=1.4)
        self.wait(1.0)

        et_ok = tag_junto(cajas, "las demas siguen", UP, buff=0.4,
                          color=C_BUENO)
        self.play(FadeIn(et_ok), run_time=0.5)
        self.wait(1.2)

        rot.mostrar(motor_pie(f"error {ERROR_ABORT}"), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(cajas[2], color=C_MALO, scale_factor=1.1),
                  run_time=0.8)
        self.wait(6.0)

        cierre_leccion(self, rot, "Lo que no se registra",
                       "no se puede arreglar.",
                       cod, marca, et_hint, cajas, marcas_estado, et_ok,
                       espera=8.5)

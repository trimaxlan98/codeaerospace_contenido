class Clip4(Scene):
    """1.2.4 - Estimado contra real: un eje horizontal en escala log10 (1 a
    1,000,000) ES la regla de las diez veces: una franja gris (C_DATO) de
    real/10 a real*10 rodea el punto real (cian). Para 'pendiente' el motor
    no mide un estimado aparte: el punto violeta usa el MISMO
    S.filas_estatus("pendiente") y cae DENTRO de la franja. Para el cliente
    1 con variable, S.estimado_variable() (violeta) queda MUY fuera de la
    franja de S.filas_cliente(1) (cian) -- semilla del modulo 5. El mismo
    eje, los mismos puntos y la misma franja se REUSAN: solo se mueven de un
    caso al otro (nunca se recrean). Cierre de la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Estimado contra real"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- el eje log10, de 1 a 1,000,000: se dibuja UNA vez y se reusa ---
        eje_y = -1.15
        x0, x1 = -6.2, 6.2

        def x_de(v):
            v = max(v, 1)
            return x0 + (x1 - x0) * (math.log10(v) / 6.0)

        eje = Line(RIGHT * (x0 - 0.5) + UP * eje_y, RIGHT * (x1 + 0.5) + UP * eje_y,
                  stroke_color=C_TENUE, stroke_width=2)
        marcas = VGroup()
        for k in range(7):
            x = x_de(10 ** k)
            marca = Line(RIGHT * x + UP * (eje_y - 0.08),
                        RIGHT * x + UP * (eje_y + 0.08),
                        stroke_color=C_TENUE, stroke_width=2)
            etiqueta = MathTex(f"10^{{{k}}}", font_size=20, color=C_TENUE)
            etiqueta.next_to(marca, DOWN, buff=0.16)
            marcas.add(VGroup(marca, etiqueta))
        self.play(Create(eje), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(m) for m in marcas], lag_ratio=0.12),
                  run_time=1.0)
        self.wait(0.6)

        # --- pendientes: sin estimado medido aparte -> se usa el MISMO real -
        q1 = S.codigo(["SELECT id_pedido", "FROM pedidos",
                      "WHERE estatus = 'pendiente'"], font_size=20)
        q1.to_corner(UL, buff=0.6).shift(DOWN * 0.7)
        self.play(FadeIn(q1, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(1.0)

        # las dos marcas viven SIEMPRE por ENCIMA del eje (nunca debajo), para
        # que su rotulo no se encime con los numeros 10^k, que van debajo.
        DY_REAL, DY_EST = 0.22, 0.62
        pend = S.filas_estatus("pendiente")
        x_pend = x_de(pend)
        ancho_franja = x_de(100) - x_de(1)   # 2 decadas: SIEMPRE el mismo ancho
        franja = Rectangle(width=ancho_franja, height=0.95, stroke_width=1.2,
                           stroke_color=C_DATO, stroke_opacity=0.7,
                           fill_color=C_DATO, fill_opacity=0.14)
        franja.move_to(RIGHT * x_pend + UP * eje_y, aligned_edge=DOWN)
        real_dot = Dot(RIGHT * x_pend + UP * (eje_y + DY_REAL), radius=0.09,
                      color=C_CALCULO)
        est_dot = Dot(RIGHT * x_pend + UP * (eje_y + DY_EST), radius=0.09,
                     color=C_CREE)
        self.play(FadeIn(franja), run_time=0.6)
        et_franja = tag_junto(franja, "10 veces", UP, buff=0.25, color=C_DATO)
        self.play(FadeIn(et_franja), run_time=0.4)
        self.wait(0.6)
        self.play(FadeIn(real_dot), run_time=0.5)
        et_real = tag_junto(real_dot, "real", RIGHT, buff=0.2, color=C_CALCULO)
        self.play(FadeIn(et_real), run_time=0.4)
        self.play(FadeIn(est_dot), run_time=0.5)
        et_est = tag_junto(est_dot, "estimado", RIGHT, buff=0.2, color=C_CREE)
        self.play(FadeIn(et_est), run_time=0.4)
        rot.mostrar(cifra_pie(f"{S.miles(pend)} pendientes"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        self.play(FadeOut(q1), FadeOut(et_real), FadeOut(et_est),
                  run_time=0.5)

        # --- cliente 1 con variable: MISMOS eje/puntos/franja, se MUEVEN ----
        q2 = S.codigo(["DECLARE @c INT = 1", "SELECT total FROM pedidos",
                      "WHERE id_cliente = @c"], font_size=20)
        q2.to_corner(UL, buff=0.6).shift(DOWN * 0.7)
        self.play(FadeIn(q2, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(0.8)

        est_v = S.estimado_variable()
        llegan = S.filas_cliente(1)
        x_est2 = x_de(est_v)
        x_real2 = x_de(llegan)
        delta = x_real2 - x_pend
        self.play(
            franja.animate.move_to(RIGHT * x_real2 + UP * eje_y,
                                   aligned_edge=DOWN),
            et_franja.animate.shift(RIGHT * delta),
            real_dot.animate.move_to(RIGHT * x_real2 + UP * (eje_y + DY_REAL)),
            est_dot.animate.move_to(RIGHT * x_est2 + UP * (eje_y + DY_EST)),
            run_time=1.8,
        )
        et_real2 = tag_junto(real_dot, "real", RIGHT, buff=0.2, color=C_CALCULO)
        et_est2 = tag_junto(est_dot, "estimado", RIGHT, buff=0.2, color=C_CREE)
        self.play(FadeIn(et_real2), FadeIn(et_est2), run_time=0.5)
        rot.mostrar(cifra_pie(f"{fmt(est_v, 2)} filas cree"), zona="abajo",
                    run_time=0.5)
        self.wait(1.6)
        rot.mostrar(cifra_pie(f"{S.miles(llegan)} filas llegan"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        cierre_leccion(self, rot, "El plan se decide antes de leer.",
                       "Con lo que el motor cree.", q2, eje, marcas, franja,
                       real_dot, est_dot, et_franja, et_real2, et_est2)

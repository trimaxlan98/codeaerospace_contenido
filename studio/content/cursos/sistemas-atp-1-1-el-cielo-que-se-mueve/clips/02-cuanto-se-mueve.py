class Clip2(Scene):
    """1.1.2 - En el cenit la velocidad es perpendicular a la linea de
    vista: omega = v/h, y salen 0.79 grados por segundo. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Cuanto se mueve en tu cielo"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- la geometria del cenit --------------------------------------
        suelo = Line(LEFT * 3.4, RIGHT * 0.6, stroke_width=2.6, color=C_EJE)
        suelo.move_to(LEFT * 1.4 + DOWN * 2.15)
        est = Dot(suelo.get_center() + RIGHT * 0.4, radius=0.075,
                  color=C_CALCULO)
        t_est = tag_junto(est, "estacion", direccion=DOWN, buff=0.14)
        sat = Dot(est.get_center() + UP * 3.30, radius=0.085, color=C_SAT)
        # Se guarda la Line SOLIDA: un DashedVMobject es un contenedor de
        # rayitas y no tiene puntos propios, asi que RightAngle (que lee
        # get_start/get_end) revienta con "Mobject with no points".
        vista_solida = Line(est.get_center(), sat.get_center(),
                            stroke_width=2.2, color=C_CIELO)
        vista_l = DashedVMobject(vista_solida, num_dashes=22)
        self.play(Create(suelo), FadeIn(est), FadeIn(t_est), run_time=0.9)
        self.play(FadeIn(sat, scale=1.5), Create(vista_l), run_time=1.0)

        t_h = tag_hud(f"h = {fmt(H_LEO, 0)} km", font_size=20)
        t_h.next_to(vista_l, LEFT, buff=0.18)
        self.play(FadeIn(t_h), run_time=0.5)
        self.wait(0.9)

        # la velocidad, perpendicular a la linea de vista
        flecha_v = Arrow(sat.get_center(),
                         sat.get_center() + RIGHT * 1.55, buff=0.0,
                         color=C_SAT, stroke_width=5, max_tip_length_to_length_ratio=0.22)
        t_v = tag_hud(f"v = {fmt(V_LEO, 2)} km/s", font_size=20, color=C_SAT)
        t_v.next_to(flecha_v, UP, buff=0.14)
        angulo = RightAngle(vista_solida, flecha_v, length=0.26, color=C_TENUE,
                            stroke_width=2.0)
        self.play(GrowArrow(flecha_v), FadeIn(t_v), run_time=0.9)
        self.play(Create(angulo), run_time=0.5)
        self.wait(1.2)

        rot.mostrar(formula_pie(r"\omega = v / h"), zona="abajo")
        self.wait(2.4)

        # --- la aguja marca la velocidad angular -------------------------
        aguja = aguja_velocidad(maximo=1.4, valor=0.0, ancho=2.5,
                                color=C_CALCULO)
        aguja.move_to(RIGHT * 3.55 + UP * 0.55)
        self.play(FadeIn(aguja), run_time=0.6)
        # `a_valor` devuelve el ANGULO absoluto, no una animacion: animar
        # es siempre Rotate(aguja.aguja, a_valor(v) - angulo, about_point).
        self.play(Rotate(aguja.aguja, aguja.a_valor(W_LEO) - aguja.angulo,
                         about_point=aguja.pivote), run_time=1.6)
        t_w = tag_hud(f"{fmt(W_LEO, 2)} deg/s", font_size=24)
        t_w.next_to(aguja, DOWN, buff=0.24)
        self.play(FadeIn(t_w), run_time=0.6)
        self.wait(1.6)

        # --- dos lunas por segundo ---------------------------------------
        rot.mostrar(cifra_pie(f"{fmt(W_LEO, 2)} grados por segundo"),
                    zona="abajo")
        self.wait(1.8)

        lunas = VGroup(*[Circle(radius=0.17, color=C_DATO, stroke_width=2.0)
                         .set_fill(C_DATO, opacity=0.30) for _ in range(2)])
        lunas.arrange(RIGHT, buff=0.10)
        lunas.move_to(RIGHT * 3.55 + DOWN * 1.75)
        t_luna = tag_junto(lunas, "dos lunas", direccion=DOWN, buff=0.16)
        self.play(LaggedStart(*[FadeIn(l, scale=1.3) for l in lunas],
                              lag_ratio=0.25), FadeIn(t_luna), run_time=1.0)
        self.wait(3.2)

        # --- mas baja, mas rapida ----------------------------------------
        rot.mostrar(cifra_pie(f"a {fmt(H_BAJA, 0)} km: "
                              f"{fmt(W_BAJA, 2)} deg/s"), zona="abajo")
        self.play(Transform(t_h, tag_hud(f"h = {fmt(H_BAJA, 0)} km",
                                         font_size=20).move_to(t_h),
                            run_time=0.02),
                  Rotate(aguja.aguja, aguja.a_valor(W_BAJA) - aguja.angulo,
                         about_point=aguja.pivote), run_time=1.5)
        self.play(Transform(t_w, tag_hud(f"{fmt(W_BAJA, 2)} deg/s",
                                         font_size=24).move_to(t_w),
                            run_time=0.02), run_time=0.5)
        self.wait(5.0)

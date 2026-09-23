class Clip2(Scene):
    """1.1.2 - Un pase LEO a 600 km visto de lado, con la Tierra y la
    orbita a escala: el satelite asoma, pasa casi por el cenit y se va.
    (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Un pase LEO"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        v = vista_pase(y_sup=-2.0)
        tierra, orbita, cono, bordes, estacion = v
        self.play(FadeIn(tierra), Create(orbita), FadeIn(estacion), run_time=1.4)
        et_h = tag_hud(f"h = {fmt(H_KM, 0)} km", font_size=19, color=C_DATO)
        et_h.move_to(v.en(-22.0) + DOWN * 0.62)
        self.play(FadeIn(et_h), run_time=0.5)
        self.wait(2.2)
        self.play(FadeIn(cono), Create(bordes), run_time=1.0)
        et_min = tag_hud(f"elev > {fmt(EL_MIN, 0)} grados", font_size=19, color=C_ENLACE)
        et_min.next_to(v.en(LAMBDA), UP + RIGHT, buff=0.15)
        self.play(FadeIn(et_min), run_time=0.5)
        self.wait(2.4)

        borde = np.degrees(np.arcsin(7.4 / v.r_o))
        th = ValueTracker(-borde)
        dentro = lambda: abs(th.get_value()) <= LAMBDA
        sat_m = always_redraw(lambda: satelite_en(v.en(th.get_value())))
        enlace = always_redraw(lambda: Line(
            v.est + UP * 0.22, v.en(th.get_value()), stroke_color=C_ADAPTA,
            stroke_width=3, stroke_opacity=0.95 if dentro() else 0.0))

        self.play(FadeOut(et_min), run_time=0.3)
        self.add(enlace, sat_m)
        self.play(th.animate.set_value(-LAMBDA), run_time=2.0, rate_func=linear)
        aos = tag_junto(Dot(v.en(-LAMBDA)), "AOS", UP + LEFT, buff=0.1,
                        font_size=22, color=C_ENLACE)
        self.play(FadeIn(aos), run_time=0.3)
        self.play(th.animate.set_value(0.0), run_time=3.0, rate_func=linear)
        tca = tag_junto(Dot(v.en(0.0)), "TCA", UP, buff=0.3, font_size=22, color=C_ENLACE)
        self.play(FadeIn(tca), run_time=0.3)
        self.play(th.animate.set_value(LAMBDA), run_time=3.0, rate_func=linear)
        los = tag_junto(Dot(v.en(LAMBDA)), "LOS", UP + RIGHT, buff=0.1,
                        font_size=22, color=C_ENLACE)
        self.play(FadeIn(los), run_time=0.3)
        self.play(th.animate.set_value(borde), run_time=2.0, rate_func=linear)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"pase = {fmt(DUR_MIN, 1)} min"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)
        rot.mostrar(cifra_pie(f"elev max = {fmt(ELEV_MAX, 1)} grados"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)
        rot.mostrar(cifra_pie(f"retardo {fmt(RET_CENIT, 1)} a {fmt(RET_BORDE, 1)} ms"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

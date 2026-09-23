class Clip3(Scene):
    """1.1.3 - La vista se aleja: el pase era un arco pequeno de una vuelta
    entera. La estacion solo tiene enlace 1 de cada 11 minutos. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("La red que se va"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # la vuelta entera, a escala: Tierra y orbita casi se tocan
        c = np.array([-2.6, -0.45, 0.0])
        r_t = 2.3
        r_o = r_t * (R_T + H_KM) / R_T
        tierra = Circle(radius=r_t, stroke_color=C_TENUE, stroke_width=2.5,
                        fill_color=C_TIERRA, fill_opacity=1.0).move_to(c)
        orbita = Circle(radius=r_o, stroke_color=C_TENUE, stroke_width=1.5,
                        stroke_opacity=0.6).move_to(c)
        est = Square(side_length=0.16, stroke_width=0, fill_color=CODE_INK,
                     fill_opacity=1.0).move_to(c + UP * (r_t + 0.08))
        arco = Arc(radius=r_o, start_angle=np.radians(90 + LAMBDA),
                   angle=-np.radians(2 * LAMBDA), arc_center=c,
                   stroke_color=C_ENLACE, stroke_width=9)
        self.play(FadeIn(tierra), Create(orbita), FadeIn(est), run_time=1.2)
        self.play(Create(arco), run_time=0.8)
        self.wait(2.0)

        # la linea de tiempo de una vuelta, con el tramo de contacto
        x0, x1, yl = 1.3, 6.3, 1.4
        riel = Line([x0, yl, 0], [x1, yl, 0], stroke_color=C_TIERRA, stroke_width=12)
        l_pase = (x1 - x0) * FRAC_CONTACTO
        tramo = Line([x0, yl, 0], [x0 + l_pase, yl, 0], stroke_color=C_ENLACE,
                     stroke_width=12)
        et_v = tag_hud(f"1 vuelta = {fmt(PERIODO_MIN, 1)} min", font_size=18, color=C_TENUE)
        et_v.next_to(riel, UP, buff=0.22).align_to(riel, RIGHT)
        self.play(Create(riel), FadeIn(et_v), run_time=0.8)
        self.wait(1.2)

        ang = ValueTracker(90.0 + LAMBDA)
        pos = lambda: c + r_o * np.array([np.cos(np.radians(ang.get_value())),
                                          np.sin(np.radians(ang.get_value())), 0.0])
        s = always_redraw(lambda: satelite_en(pos()))
        frac = lambda: ((90.0 + LAMBDA - ang.get_value()) % 360.0) / 360.0
        cab = always_redraw(lambda: Dot([x0 + (x1 - x0) * frac(), yl, 0], radius=0.09,
                                        color=CODE_INK))
        enl = always_redraw(lambda: Line(
            est.get_center(), pos(), stroke_color=C_ADAPTA, stroke_width=2.5,
            stroke_opacity=0.95 if frac() * 360.0 <= 2 * LAMBDA else 0.0))
        self.add(enl, s, cab)
        # el pase: el tramo se enciende mientras dura el enlace
        self.play(ang.animate.set_value(90.0 - LAMBDA), Create(tramo), run_time=2.4,
                  rate_func=linear)
        self.wait(0.6)
        et_p = tag_hud(f"{fmt(DUR_MIN, 1)} min", font_size=19, color=C_ENLACE)
        et_p.next_to(tramo, DOWN, buff=0.2).align_to(tramo, LEFT)
        self.play(FadeIn(et_p), run_time=0.4)
        self.wait(1.4)
        # el resto de la vuelta: el satelite sigue, la estacion se queda sola
        self.play(ang.animate.set_value(90.0 + LAMBDA - 359.9), run_time=7.0,
                  rate_func=linear)
        self.wait(1.2)
        rot.mostrar(cifra_pie(f"contacto = {fmt(100 * FRAC_CONTACTO, 1)} % de la vuelta"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)
        rot.mostrar(cifra_pie(f"sin enlace = {fmt(PERIODO_MIN - DUR_MIN, 1)} min"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

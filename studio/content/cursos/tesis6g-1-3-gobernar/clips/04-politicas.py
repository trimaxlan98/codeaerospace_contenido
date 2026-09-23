class Clip4(Scene):
    """1.3.4 - En una arquitectura desacoplada la politica es un cartucho:
    el mismo zocalo recibe una estatica, una heuristica ingenua o una
    afinada. La compuerta G-H de la tesis midio las tres. Cierre. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Politicas como software"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # el zocalo: entra la observacion, sale la accion
        zocalo = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.5,
                                  stroke_color=CODE_INK, stroke_width=3).move_to([-3.2, 0.3, 0])
        f_in = Arrow([-6.0, 0.3, 0], zocalo.get_left(), buff=0.1, stroke_width=4, color=C_TENUE)
        f_out = Arrow(zocalo.get_right(), [-0.4, 0.3, 0], buff=0.1, stroke_width=4, color=C_TENUE)
        e_in = MathTex(r"o_i", color=C_TENUE, font_size=40).next_to(f_in, UP, buff=0.1)
        e_out = MathTex(r"a_i", color=C_TENUE, font_size=40).next_to(f_out, UP, buff=0.1)
        et_z = tag_hud("PolicyFn", font_size=19, color=CODE_INK).next_to(zocalo, DOWN, buff=0.2)
        self.play(Create(zocalo), GrowArrow(f_in), GrowArrow(f_out), FadeIn(e_in),
                  FadeIn(e_out), FadeIn(et_z), run_time=1.2)
        self.wait(1.6)

        # barras de la semilla 42 (G-H): recompensa por episodio, desde cero
        y0, alto = -2.3, 4.2
        vmax = max(GH["estatica"], GH["ingenua"], GH["afinada"])
        xs = [1.6, 3.4, 5.2]
        suelo = Line([0.8, y0, 0], [6.0, y0, 0], stroke_color=C_TENUE, stroke_width=2)
        self.play(FadeIn(suelo), run_time=0.4)

        def cartucho(color):
            return RoundedRectangle(corner_radius=0.1, width=1.9, height=1.0, stroke_width=0,
                                    fill_color=color, fill_opacity=0.9).move_to(zocalo)

        piezas = [("estatica", GH["estatica"], C_ESTATICA),
                  ("ingenua", GH["ingenua"], C_NO),
                  ("afinada", GH["afinada"], C_OK)]
        actual = None
        resto = VGroup()
        for (nombre, v, col), x in zip(piezas, xs):
            ca = cartucho(col).shift(UP * 2.3)
            self.play(FadeIn(ca), run_time=0.3)
            anim = [ca.animate.move_to(zocalo)]
            if actual is not None:
                anim.append(actual.animate.shift(DOWN * 2.3).set_opacity(0))
            self.play(*anim, run_time=0.8)
            if actual is not None:
                self.remove(actual)
            actual = ca
            h = alto * v / vmax
            b = Rectangle(width=1.0, height=h, stroke_width=0, fill_color=col, fill_opacity=1.0)
            b.move_to([x, y0 + h / 2, 0])
            et = tag_hud(nombre, font_size=18, color=col).move_to([x, y0 - 0.35, 0])
            val = tag_hud(f"{v:,.0f}".replace(",", " "), font_size=18, color=C_DATO)
            self.play(GrowFromEdge(b, DOWN), FadeIn(et), run_time=0.8)
            val.next_to(b, UP, buff=0.12)
            self.play(FadeIn(val), run_time=0.3)
            resto.add(b, et, val)
            self.wait(1.6)
        rot.mostrar(dato_pie(f"{N_CONFIGS} heuristicas probadas"), zona="abajo", run_time=0.5)
        self.wait(3.2)
        rot.mostrar(dato_pie(f"afinada: +{fmt(100 * GH_RANGO[0], 1)} a "
                             f"+{fmt(100 * GH_RANGO[1], 1)} %"), zona="abajo", run_time=0.5)
        self.wait(4.0)

        cierre_leccion(self, rot, "Separar al que piensa",
                       "del que actua.",
                       zocalo, f_in, f_out, e_in, e_out, et_z, actual, suelo, resto)

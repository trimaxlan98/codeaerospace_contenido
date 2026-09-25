def _tarjeta(icao, indicativo, color, ancho=4.7, alto=2.7):
    marco = Rectangle(width=ancho, height=alto, stroke_color=color,
                      stroke_width=2.2, fill_color=color, fill_opacity=0.06)
    et_icao = Text("ICAO", font_size=17, color=C_TENUE)
    v_icao = Text(icao, font=FUENTE_HUD, font_size=42, color=color)
    et_ind = Text("indicativo", font_size=17, color=C_TENUE)
    v_ind = Text(indicativo, font=FUENTE_HUD, font_size=38, color=color)
    contenido = VGroup(et_icao, v_icao, et_ind, v_ind)
    contenido.arrange(DOWN, buff=0.14)
    contenido.move_to(marco)
    return VGroup(marco, contenido), v_icao, v_ind


class Clip4(Scene):
    """6.1.4 - La tarjeta del avion ficticio (0D0C38 / CODE101) decodificada
    en verde; el mismo decodificador lee tambien un mensaje REAL (4840D6 /
    KLM1023). Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El avion"), zona="arriba", run_time=0.6)
        self.wait(0.5)

        tag_ok = tag_hud("decodificado aqui", font_size=19, color=C_CALCULO)
        tag_ok.to_edge(UP, buff=1.15)
        self.play(FadeIn(tag_ok), run_time=0.5)
        self.wait(0.6)

        # --- la tarjeta del avion ficticio --------------------------------
        icao1 = DEC["icao"]
        ind1 = DEC["indicativo"].strip()
        tarjeta1, v_icao1, v_ind1 = _tarjeta(icao1, ind1, C_OK)
        tarjeta1.move_to(LEFT * 3.35 + DOWN * 0.15)

        self.play(Create(tarjeta1[0]), run_time=0.8)
        self.wait(0.3)
        self.play(FadeIn(tarjeta1[1][0]), run_time=0.3)
        self.play(FadeIn(v_icao1, shift=UP * 0.1), run_time=0.6)
        self.wait(0.5)
        self.play(FadeIn(tarjeta1[1][2]), run_time=0.3)
        self.play(FadeIn(v_ind1, shift=UP * 0.1), run_time=0.6)
        self.wait(1.4)

        rot.mostrar(dato_pie("avion ficticio"), zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- el mismo decodificador lee un avion real ---------------------
        icao2 = KLM["icao"]
        ind2 = KLM["indicativo"].strip()
        tarjeta2, v_icao2, v_ind2 = _tarjeta(icao2, ind2, C_OK)
        tarjeta2.move_to(RIGHT * 3.35 + DOWN * 0.15)
        et_real = tag_junto(tarjeta2, "mensaje real", UP, buff=0.22,
                            font_size=18, color=C_DATO)

        self.play(Create(tarjeta2[0]), FadeIn(et_real), run_time=0.9)
        self.wait(0.3)
        self.play(FadeIn(tarjeta2[1][0]), run_time=0.3)
        self.play(FadeIn(v_icao2, shift=UP * 0.1), run_time=0.6)
        self.wait(0.4)
        self.play(FadeIn(tarjeta2[1][2]), run_time=0.3)
        self.play(FadeIn(v_ind2, shift=UP * 0.1), run_time=0.6)
        self.wait(1.6)

        rot.mostrar(dato_pie("mensaje real"), zona="abajo", run_time=0.5)
        self.wait(4.4)

        cierre_leccion(self, rot, "Cada avion dice quien es",
                       "un par de veces por segundo.", tag_ok, tarjeta1,
                       tarjeta2, et_real)

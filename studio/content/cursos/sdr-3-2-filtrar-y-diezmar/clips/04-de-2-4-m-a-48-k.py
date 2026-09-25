class Clip4(Scene):
    """3.2.4 - De 2.4 M a 48 k: la escalera de tasas que atraviesa el canal,
    del muestreo del RTL-SDR (dato) al canal recortado por el filtro
    (calculado) al audio que sale (dato). Cierre. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("De 2.4 M a 48 k"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        # --- la escalera de tasas: 2.4 M -> 240 k -> 48 k -------------------
        rate_canal = FS / 10.0
        rate_audio = 48000.0
        div_total = FS / rate_audio

        w0 = 10.4
        w1 = w0 * math.sqrt(rate_canal / FS)
        w2 = w0 * math.sqrt(rate_audio / FS)
        alto_barra = 0.6
        x0 = LEFT * 5.2

        b0 = Rectangle(width=w0, height=alto_barra, stroke_width=0,
                       fill_color=C_DATO, fill_opacity=0.75)
        b0.move_to(x0 + RIGHT * w0 / 2 + UP * 1.9)
        b1 = Rectangle(width=w1, height=alto_barra, stroke_width=0,
                       fill_color=C_CALCULO, fill_opacity=0.85)
        b1.move_to(x0 + RIGHT * w1 / 2 + UP * 0.0)
        b2 = Rectangle(width=w2, height=alto_barra, stroke_width=0,
                       fill_color=C_DATO, fill_opacity=0.75)
        b2.move_to(x0 + RIGHT * w2 / 2 + DOWN * 1.9)

        t0 = tag_dato("2.4 MS/s")
        t0.next_to(b0, UP, buff=0.14).align_to(b0, LEFT)
        t1 = tag_hud(f"{fmt(rate_canal / 1e3, 0)} kS/s")
        t1.next_to(b1, UP, buff=0.14).align_to(b1, LEFT)
        t2 = tag_dato("48 kS/s")
        t2.next_to(b2, UP, buff=0.14).align_to(b2, LEFT)

        d_exagerado = tag_dato("dibujo exagerado")
        d_exagerado.to_corner(UR, buff=0.5).shift(DOWN * 0.5 + LEFT * 0.3)

        self.play(GrowFromEdge(b0, LEFT), FadeIn(t0), FadeIn(d_exagerado),
                  run_time=1.1)
        self.wait(1.8)
        self.play(GrowFromEdge(b1, LEFT), FadeIn(t1), run_time=1.1)
        self.wait(1.8)
        self.play(GrowFromEdge(b2, LEFT), FadeIn(t2), run_time=1.1)
        self.wait(3.2)

        rot.mostrar(cifra_pie(f"2.4 M / 48 k = {fmt(div_total, 0)}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)
        rot.mostrar(cifra_pie(f"÷{fmt(div_total, 0)}"), zona="abajo",
                    run_time=0.5)
        self.wait(6.0)

        cierre_leccion(self, rot, "Primero se recorta,",
                       "despues se tira lo que sobra.", b0, b1, b2, t0, t1,
                       t2, d_exagerado)

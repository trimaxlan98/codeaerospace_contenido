class Clip4(Scene):
    """1.4.4 - Contar politicas descentralizadas: cada agente decide sobre su
    historia de observaciones, y el numero de politicas conjuntas explota
    con el horizonte. Pero coste de computo no es brecha de valor. Cierre.
    (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El coste de descentralizar"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # barras en escala logaritmica: log10 del numero de politicas
        x0, dx, y0 = -4.6, 2.2, -2.2
        esc = 4.4 / np.log10(LOG_POL[-1])          # el eje es log(log): se declara
        barras = VGroup()
        for i, (h, lp) in enumerate(zip(HORIZ, LOG_POL)):
            alto = max(esc * np.log10(max(lp, 1.0)) + 0.25, 0.25)
            b = Rectangle(width=1.1, height=alto, stroke_width=0, fill_color=C_PRIV,
                          fill_opacity=1.0).move_to([x0 + i * dx, y0 + alto / 2, 0])
            eh = tag_hud(f"T = {h}", font_size=18, color=C_TENUE).move_to([x0 + i * dx, y0 - 0.35, 0])
            v = MathTex(rf"10^{{{lp:.0f}}}", color=C_CALCULO, font_size=38).next_to(b, UP, buff=0.12)
            barras.add(VGroup(b, eh, v))
        suelo = Line([x0 - 0.9, y0, 0], [x0 + 4 * dx + 0.9, y0, 0], stroke_color=C_TENUE, stroke_width=2)
        self.play(FadeIn(suelo), run_time=0.4)
        for b in barras:
            self.play(GrowFromEdge(b[0], DOWN), FadeIn(b[1]), run_time=0.6)
            self.play(FadeIn(b[2]), run_time=0.3)
            self.wait(0.6)
        et = tag_hud("escala doble log", font_size=17, color=C_DATO).to_corner(UR, buff=0.6).shift(DOWN * 0.4)
        self.play(FadeIn(et), run_time=0.4)
        rot.mostrar(cifra_pie(f"politicas a T = {HORIZ[-1]}: 10^{LOG_POL[-1]:.0f}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)
        rot.mostrar(dato_pie("Dec-POMDP: NEXP completo"), zona="abajo", run_time=0.5)
        self.wait(3.4)

        # el aviso de la tesis: dificil de computar NO implica gran margen
        aviso = VGroup(MathTex(r"\text{coste}", color=C_PRIV, font_size=44),
                       MathTex(r"\neq", color=CODE_INK, font_size=52),
                       MathTex(r"\text{margen}", color=C_ADAPTA, font_size=44)).arrange(RIGHT, buff=0.4)
        aviso.move_to([0.9, 2.3, 0]).add_background_rectangle(color=CODE_BG, opacity=0.9, buff=0.15)
        self.play(FadeIn(aviso, shift=DOWN * 0.1), run_time=0.8)
        self.wait(4.4)

        cierre_leccion(self, rot, "Nadie ve el estado entero.",
                       "Y hay que decidir igual.",
                       barras, suelo, et, aviso)

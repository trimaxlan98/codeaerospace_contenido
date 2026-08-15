class Clip2(Scene):
    """2 - El metro lo define la luz. Desde 1983 c es exacta; el pulso
    cruza la barra de 1 m en 1/299 792 458 s y esa es la definicion.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El metro lo define la luz"),
                    zona="arriba", run_time=0.6)

        reloj = reloj_luz()
        reloj.shift(UP * 0.85)
        c_tag = tag_hud(f"c = {C_LUZ:,.0f} m/s".replace(",", " "),
                        font_size=18)
        c_tag.next_to(reloj.llave, DOWN, buff=0.32)

        # --- momento 1: la barra y c exacta --------------------------------------
        rot.mostrar(pie_curso("Desde 1983 la velocidad de la luz no se "
                              "mide: se define."), zona="abajo")
        self.play(FadeIn(reloj), run_time=1.0)
        self.play(FadeIn(c_tag, shift=0.10 * UP), run_time=0.5)
        self.wait(5.6)

        # --- momento 2: el pulso cruza la barra -----------------------------------
        rot.mostrar(pie_curso("El metro es lo que la luz recorre en "
                              "1/299 792 458 de segundo."), zona="abajo")
        formula = MathTex(r"1\,\text{m} = c \cdot \tfrac{1}{299\,792\,458}"
                          r"\,\text{s}", font_size=30, color=C_ACENTO)
        formula.next_to(c_tag, DOWN, buff=0.5)
        self.play(FadeIn(formula, shift=0.10 * UP), run_time=0.6)
        t_luz = ValueTracker(0.0)
        avanza = lambda o: o.a_t(t_luz.get_value())
        reloj.add_updater(avanza)
        self.play(t_luz.animate.set_value(1.0), run_time=2.2,
                  rate_func=linear)
        reloj.remove_updater(avanza)
        self.wait(5.0)

        # --- momento 3: hereda del reloj de cesio ----------------------------------
        rot.mostrar(pie_curso("Por eso toda regla de luz hereda la "
                              "exactitud del reloj."), zona="abajo")
        icono = tag_junto(reloj.barra, "reloj", RIGHT, buff=0.35,
                          font_size=17, color=C_MEDIDA)
        cesio = tag_hud("1 s = 9 192 631 770 periodos del cesio",
                        font_size=13)
        cesio.next_to(formula, DOWN, buff=0.42)
        cita = tag_hud("cita: definicion", font_size=12, color=C_TENUE)
        cita.next_to(cesio, DOWN, buff=0.08)
        self.play(FadeIn(icono, shift=0.10 * RIGHT), run_time=0.5)
        self.play(FadeIn(cesio), FadeIn(cita), run_time=0.5)
        self.wait(5.5)

        # --- cierre -----------------------------------------------------------------
        rot.mostrar(pie_curso("La longitud ya no es una vara: es un "
                              "tiempo multiplicado por c."), zona="abajo")
        self.wait(6.5)

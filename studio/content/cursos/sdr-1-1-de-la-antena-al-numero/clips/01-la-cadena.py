class Clip1(Scene):
    """1.1.1 - La cadena de un receptor SDR: todo lo que esta a la
    derecha del ADC es software. Hoja de datos del RTL-SDR en gris. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La cadena"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        cad = S.Cadena(("ANTENA", "LNA", "MEZCLADOR", "FILTRO", "ADC",
                        "USB", "SOFTWARE"), ancho_total=12.8, alto=1.05,
                       tamano=22)
        cad.move_to(UP * 0.35)
        # --- la senal entra eslabon a eslabon ---------------------------
        for i, b in enumerate(cad.bloques):
            anims = [FadeIn(b, shift=RIGHT * 0.15)]
            if i > 0:
                anims.append(GrowArrow(cad.flechas[i - 1]))
            if cad.nombres[i] == "MEZCLADOR":
                anims.append(FadeIn(cad.lo))
            self.play(*anims, run_time=0.55)
        self.wait(0.8)
        self.play(S.flujo(list(cad.flechas), color=C_SENAL,
                          por_conexion=0.4))
        self.wait(1.0)

        # --- el corte: el ADC ---------------------------------------------
        i_adc = cad.indice("ADC")
        adc = cad.bloques[i_adc]
        self.play(adc[0].animate.set_stroke(C_SENAL, width=3.5)
                  .set_fill(C_SENAL, opacity=0.18), run_time=0.7)
        self.wait(0.6)
        hw = VGroup(*cad.bloques[:i_adc + 1])
        sw = VGroup(*cad.bloques[i_adc + 1:])
        l_hw = Brace(hw, DOWN, buff=1.45, color=C_TENUE)
        l_sw = Brace(sw, DOWN, buff=1.45, color=C_CALCULO)
        t_hw = tag_junto(l_hw, "circuito", DOWN, buff=0.14, font_size=24)
        t_sw = tag_junto(l_sw, "numeros", DOWN, buff=0.14, font_size=24,
                         color=C_CALCULO)
        self.play(GrowFromCenter(l_hw), FadeIn(t_hw), run_time=0.8)
        self.wait(0.8)
        self.play(GrowFromCenter(l_sw), FadeIn(t_sw),
                  *[b[0].animate.set_stroke(C_CALCULO, width=3)
                    for b in sw], run_time=0.9)
        self.wait(2.6)

        # --- la hoja de datos (gris) --------------------------------------
        d_rango = tag_dato("24 - 1766 MHz", font_size=20)
        d_rango.next_to(cad.bloques[cad.indice("MEZCLADOR")], UP, buff=0.3)
        d_fs = tag_dato("2.4 MS/s", font_size=20)
        d_bits = tag_dato("8 bits", font_size=20)
        VGroup(d_fs, d_bits).arrange(DOWN, buff=0.14).next_to(adc, UP,
                                                              buff=0.3)
        self.play(FadeIn(d_rango, shift=DOWN * 0.1), run_time=0.6)
        self.wait(1.4)
        self.play(FadeIn(d_fs, shift=DOWN * 0.1), run_time=0.5)
        self.wait(0.8)
        self.play(FadeIn(d_bits, shift=DOWN * 0.1), run_time=0.5)
        self.wait(1.6)
        rot.mostrar(dato_pie("RTL-SDR: unos 30 dolares"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)
        self.play(S.flujo(list(cad.flechas), color=C_SENAL,
                          por_conexion=0.35))
        self.wait(3.0)

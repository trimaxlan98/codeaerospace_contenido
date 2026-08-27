class Clip2(Scene):
    """1.2.2 - Once resoluciones medidas sobre la misma senal: la SQNR
    sube en linea recta y el ajuste da 6.01 dB por bit. La ordenada
    medida es -1.82 dB porque esta senal no llena la escala. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Seis decibelios por bit"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        ba = Barras(SQNR_EJE, ancho=8.8, alto=3.6, color=C_CALCULO)
        ba.shift(DOWN * 0.35)
        et_bits = VGroup()
        for i, b in enumerate(BITS_EJE):
            t = tag_hud(f"{int(b)}", font_size=18, color=C_TENUE)
            t.move_to(ba._en(i + 0.5, ba.y0))
            t.shift(DOWN * 0.24)
            et_bits.add(t)
        et_eje = tag_junto(et_bits, "bits", RIGHT, buff=0.46, font_size=19)
        eje_y = Line(ba._en(0, ba.y0), ba._en(0, ba.y1), color=C_EJE,
                     stroke_width=1.6)
        et_db = tag_hud("dB", font_size=19, color=C_TENUE)
        et_db.next_to(eje_y.get_end(), UP, buff=0.14)

        self.play(FadeIn(ba.ejes), Create(eje_y), FadeIn(et_eje),
                  FadeIn(et_db),
                  LaggedStart(*[FadeIn(t) for t in et_bits], lag_ratio=0.06),
                  run_time=1.4)
        self.play(LaggedStart(*[GrowFromEdge(r, DOWN) for r in ba.barras],
                              lag_ratio=0.13), run_time=2.6)
        self.wait(1.4)

        panel = panel_cifras(
            (f"{int(BITS_EJE[0])} bits: {fmt(SQNR_EJE[0], 1)} dB", C_CALCULO),
            (f"{int(BITS_EJE[-1])} bits: {fmt(SQNR_EJE[-1], 1)} dB",
             C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.2)

        # --- el ajuste: una recta, no una casualidad ----------------------
        recta = VMobject(color=C_IDEAL, stroke_width=3.4)
        recta.set_points_as_corners([ba._en(i + 0.5, PENDIENTE * b + ORDENADA)
                                     for i, b in enumerate(BITS_EJE)])
        et_recta = tag_hud("ajuste", font_size=19, color=C_IDEAL)
        et_recta.next_to(ba._en(0.5, PENDIENTE * BITS_EJE[0] + ORDENADA),
                         UL, buff=0.16)
        self.play(Create(recta), FadeIn(et_recta), run_time=1.8)
        rot.mostrar(cifra_pie(f"ajuste = {fmt(PENDIENTE, 2)} dB/bit"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- un solo bit, medido en el propio ajuste ----------------------
        i_a, i_b = 9, 10
        y_a = PENDIENTE * BITS_EJE[i_a] + ORDENADA
        y_b = PENDIENTE * BITS_EJE[i_b] + ORDENADA
        p_a = ba._en(i_a + 0.5, y_a)
        p_b = ba._en(i_b + 0.5, y_b)
        codo = np.array([p_b[0], p_a[1], 0.0])
        paso_h = DashedLine(p_a, codo, color=C_SALIDA, stroke_width=2.2,
                            dash_length=0.08)
        paso_v = Line(codo, p_b, color=C_SALIDA, stroke_width=3.0)
        et_paso = tag_hud(f"+{fmt(PENDIENTE, 2)} dB", font_size=19,
                          color=C_SALIDA)
        et_paso.next_to(paso_v, RIGHT, buff=0.18)
        self.play(Create(paso_h), run_time=0.7)
        self.play(Create(paso_v), FadeIn(et_paso), run_time=0.9)
        self.wait(2.6)

        # --- la honestidad de la ordenada ---------------------------------
        rot.mostrar(formula_pie(r"\mathrm{SQNR} \approx 6.02\,b + 1.76"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(dato_pie("teoria +1.76 dB"), zona="abajo", run_time=0.5)
        self.wait(2.6)
        rot.mostrar(cifra_pie(f"ordenada = {fmt(ORDENADA, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        panel_2 = panel_cifras(
            (f"pendiente {fmt(PENDIENTE, 2)} dB/bit", C_SALIDA),
            (f"ordenada {fmt(ORDENADA, 2)} dB", C_CALCULO),
            (f"{len(BITS_EJE)} resoluciones medidas", C_TENUE))
        self.play(FadeOut(panel), run_time=0.45)
        self.play(FadeIn(panel_2), run_time=0.7)
        self.wait(2.4)

        rot.mostrar(cifra_pie(f"pendiente = {fmt(PENDIENTE, 2)} dB/bit"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

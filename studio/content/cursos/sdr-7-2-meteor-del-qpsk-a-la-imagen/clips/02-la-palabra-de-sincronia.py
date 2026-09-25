class Clip2(Scene):
    """7.2.2 - La palabra de sincronia 1ACFFC1D (norma, gris) resuelve la
    ambiguedad de fase de la QPSK: se correlaciona con los simbolos
    recibidos girados 0, 90, 180 y 270 grados (CORR_ASM de
    S.cadena_meteor). Una rotacion destaca (verde), la opuesta sale
    negativa (roja); cian la rotacion hallada (ROT x 90). (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La palabra de sincronia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- la palabra: hex y sus 32 bits (norma) -------------------------
        hexa = tag_dato("1ACFFC1D", font_size=36)
        hexa.move_to(UP * 2.4)
        bits = S._a_bits(S.ASM, 32)
        txt_bits = "  ".join("".join(str(b) for b in bits[i:i + 8])
                             for i in range(0, 32, 8))
        fila_bits = tag_dato(txt_bits, font_size=24)
        if fila_bits.width > 11.0:
            fila_bits.scale_to_fit_width(11.0)
        fila_bits.next_to(hexa, DOWN, buff=0.22)
        self.play(FadeIn(hexa, shift=DOWN * 0.1), run_time=0.6)
        self.wait(0.6)
        self.play(Write(fila_bits), run_time=1.6)
        rot.mostrar(dato_pie("ASM de 32 bits"), zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- cuatro rotaciones, cuatro correlaciones -----------------------
        x0 = 0.8                     # la linea del cero
        esc = 4.0                    # unidades por unidad de correlacion
        ys = [1.05, 0.15, -0.75, -1.65]
        cero = Line(np.array([x0, 1.5, 0]), np.array([x0, -2.05, 0]),
                    color=C_EJE, stroke_width=2)
        t_cero = Text("0", font=FUENTE_HUD, font_size=18, color=C_TENUE)
        t_cero.next_to(cero, DOWN, buff=0.08)
        cab = tag_junto(cero, "rotacion", LEFT, buff=0.0, font_size=22)
        cab.move_to(np.array([-5.6, 1.72, 0]))
        self.play(Create(cero), FadeIn(t_cero), FadeIn(cab), run_time=0.7)

        barras, valores, etiquetas = VGroup(), VGroup(), VGroup()
        for k, (y, c) in enumerate(zip(ys, CORR_ASM)):
            et = Text(f"{90 * k}", font=FUENTE_HUD, font_size=26,
                      color=C_TITULO)
            et.move_to(np.array([-5.6, y, 0]))
            largo = abs(c) * esc
            b = Rectangle(width=largo, height=0.55, stroke_width=0,
                          fill_color=C_EJE, fill_opacity=0.85)
            signo = 1 if c >= 0 else -1
            b.move_to(np.array([x0 + signo * largo / 2, y, 0]))
            v = tag_hud(fmt(c, 2), font_size=24)
            v.next_to(b, RIGHT if signo > 0 else LEFT, buff=0.2)
            etiquetas.add(et)
            barras.add(b)
            valores.add(v)
            self.play(FadeIn(et), run_time=0.35)
            self.play(GrowFromEdge(b, LEFT if signo > 0 else RIGHT),
                      run_time=0.9)
            self.play(FadeIn(v), run_time=0.35)
            self.wait(0.9)
        u_grados = tag_junto(etiquetas, "grados", DOWN, buff=0.2,
                             font_size=20)
        self.play(FadeIn(u_grados), run_time=0.4)
        self.wait(1.6)

        # --- una destaca, la opuesta sale negativa --------------------------
        k_op = (ROT + 2) % 4
        self.play(barras[ROT].animate.set_fill(C_OK, opacity=0.9),
                  etiquetas[ROT].animate.set_color(C_OK), run_time=0.8)
        marco = SurroundingRectangle(
            VGroup(etiquetas[ROT], barras[ROT], valores[ROT]),
            color=C_OK, buff=0.14, stroke_width=2.2)
        marco.stretch_to_fit_width(
            valores[ROT].get_right()[0] - etiquetas[ROT].get_left()[0]
            + 0.4)
        marco.align_to(etiquetas[ROT], LEFT).shift(LEFT * 0.2)
        self.play(Create(marco), run_time=0.7)
        self.wait(1.4)
        self.play(barras[k_op].animate.set_fill(C_RUIDO, opacity=0.9),
                  etiquetas[k_op].animate.set_color(C_RUIDO), run_time=0.8)
        self.wait(1.6)
        rot.mostrar(cifra_pie(f"rotacion: {90 * ROT} grados"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)
        self.play(Indicate(hexa, color=C_DATO, scale_factor=1.08),
                  run_time=1.0)
        self.play(Indicate(barras[ROT], color=C_OK, scale_factor=1.04),
                  run_time=1.0)
        self.wait(4.0)

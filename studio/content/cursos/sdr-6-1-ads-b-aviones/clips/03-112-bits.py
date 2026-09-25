from comunicaciones import TrenBits  # noqa: E402


def _fila_campo(n_bits, ancho, alto, color):
    """VGroup: un relleno + lineas finas que marcan cada una de las
    `n_bits` casillas dentro de un campo de `ancho` unidades."""
    fondo = Rectangle(width=ancho, height=alto, stroke_color=color,
                      stroke_width=1.6, fill_color=color, fill_opacity=0.5)
    marcas = VGroup()
    paso = ancho / n_bits
    for i in range(1, n_bits):
        x = -ancho / 2 + i * paso
        marcas.add(Line(np.array([x, -alto / 2, 0.0]),
                        np.array([x, alto / 2, 0.0]), color=CODE_BG,
                        stroke_width=0.9, stroke_opacity=0.55))
    return VGroup(fondo, marcas)


class Clip3(Scene):
    """6.1.3 - Los 112 bits del mensaje como fila de casillas coloreadas
    por campo: DF(5)+CA(3) gris (formato), ICAO(24)+datos(56) ambar (la
    carga aun sin decodificar), CRC(24) cian. Zoom a los 24 bits reales del
    CRC; el sindrome calculado da 0: el mensaje es valido. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("112 bits"), zona="arriba", run_time=0.6)
        self.wait(0.5)

        campos = [("DF 5 · CA 3", 8, C_DATO), ("ICAO 24", 24, C_SENAL),
                 ("datos 56", 56, C_SENAL), ("CRC 24", 24, C_CALCULO)]
        ancho_total, alto = 11.4, 1.7
        n_total = sum(n for _, n, _ in campos)

        fila = VGroup()
        for _, n, color in campos:
            w = ancho_total * n / n_total
            fila.add(_fila_campo(n, w, alto, color))
        fila.arrange(RIGHT, buff=0.0)
        fila.move_to(UP * 1.15)

        self.play(*[Create(seg[0]) for seg in fila], run_time=1.5)
        self.wait(0.6)
        self.play(*[FadeIn(seg[1]) for seg in fila], run_time=0.9)
        self.wait(2.4)

        etiquetas = VGroup()
        for (texto, n, color), seg in zip(campos, fila):
            et = tag_junto(seg, texto, UP, buff=0.4, font_size=18,
                           color=color)
            linea = Line(seg.get_top(), et.get_bottom() + UP * 0.02,
                        color=color, stroke_width=1.8)
            etiquetas.add(linea, et)
        self.play(FadeIn(etiquetas, lag_ratio=0.15), run_time=1.4)
        self.wait(3.2)

        # --- zoom: los 24 bits reales del campo CRC -----------------------
        seg_crc = fila[3]
        bits_crc = [int(b) for b in DEC["bits"][88:112]]
        tb = TrenBits(bits_crc, lado=0.47, color=C_CALCULO)
        tb.move_to(DOWN * 1.5)
        flecha = Arrow(seg_crc.get_bottom(), tb.get_top(), buff=0.1,
                       color=C_CALCULO, stroke_width=2.6,
                       max_tip_length_to_length_ratio=0.18)
        et_zoom = tag_junto(tb, "24 bits del CRC", DOWN, buff=0.22,
                            font_size=18, color=C_CALCULO)

        marco = SurroundingRectangle(seg_crc, color=C_CALCULO, buff=0.1,
                                     stroke_width=2.6)
        self.play(Create(marco), run_time=0.7)
        self.wait(0.5)
        self.play(GrowArrow(flecha), run_time=0.6)
        self.play(Create(tb.celdas), FadeIn(tb.digitos), run_time=1.3)
        self.wait(1.4)
        self.play(FadeIn(et_zoom), run_time=0.5)
        self.wait(3.0)

        rot.mostrar(cifra_pie(f"CRC: {DEC['sindrome']} errores"),
                   zona="abajo", run_time=0.5)
        self.wait(9.8)

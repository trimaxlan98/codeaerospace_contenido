from comunicaciones import TrenBits  # noqa: E402


class Clip2(Scene):
    """6.2.2 - La regla NRZI de HDLC sobre 10 bits reales de TRAMA: una
    fila de bits arriba, la fila de niveles (S.nrzi) debajo. Bit a bit se
    marca en fucsia el nivel cuando el bit es 0 (cambia); cuando el bit es
    1 el nivel se mantiene. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("NRZI"), zona="arriba", run_time=0.6)
        self.wait(0.5)

        i0, n = 60, 10
        lado = 0.66
        fila_bits = TrenBits(TRAMA[i0:i0 + n], lado=lado, color=C_TITULO)
        fila_niv = TrenBits(NIVELES[i0:i0 + n], lado=lado, color=C_SENAL)
        fila_bits.move_to(UP * 1.55)
        fila_niv.move_to(DOWN * 0.75)

        prev_cell = Square(lado, color=C_EJE, stroke_width=1.4)
        prev_digito = tag_hud(str(int(NIVELES[i0 - 1])), font_size=18,
                              color=C_TENUE)
        prev_digito.move_to(prev_cell.get_center())
        prev = VGroup(prev_cell, prev_digito)
        prev.next_to(fila_niv, LEFT, buff=0.6)

        et_bits = tag_junto(fila_bits, "bits", UP, buff=0.24, font_size=22,
                            color=C_TENUE)
        et_niv = tag_junto(fila_niv, "niveles", UP, buff=0.24, font_size=22,
                           color=C_SENAL)
        et_prev = tag_junto(prev, "antes", UP, buff=0.16, font_size=18,
                            color=C_TENUE)

        self.play(Create(fila_bits.celdas), run_time=0.9)
        self.wait(0.3)
        self.play(FadeIn(fila_bits.digitos), FadeIn(et_bits), run_time=0.6)
        self.wait(1.2)

        self.play(Create(prev_cell), FadeIn(prev_digito), FadeIn(et_prev),
                  run_time=0.6)
        self.wait(0.7)
        self.play(Create(fila_niv.celdas), FadeIn(et_niv), run_time=0.8)
        self.wait(0.5)

        # --- bit a bit: un 0 cambia el nivel, un 1 lo mantiene --------------
        cambio_hecho = igual_hecho = False
        for k in range(n):
            self.play(Indicate(fila_bits.celda(k), color=C_TITULO,
                               scale_factor=1.22), run_time=0.4)
            if TRAMA[i0 + k] == 0:
                fila_niv.celda(k).set_stroke(C_LO, width=2.8)
                fila_niv.digito(k).set_color(C_LO)
                self.play(FadeIn(fila_niv.digito(k)),
                          fila_niv.celda(k).animate.set_stroke(C_LO,
                                                                width=2.8),
                          run_time=0.45)
                if not cambio_hecho:
                    et_cambio = tag_junto(fila_niv.celda(k), "cambio", DOWN,
                                          buff=0.2, font_size=19,
                                          color=C_LO)
                    self.play(FadeIn(et_cambio), run_time=0.35)
                    self.wait(0.7)
                    cambio_hecho = True
            else:
                self.play(FadeIn(fila_niv.digito(k)), run_time=0.35)
                if not igual_hecho:
                    et_igual = tag_junto(fila_niv.celda(k), "igual", DOWN,
                                         buff=0.85, font_size=19,
                                         color=C_TENUE)
                    self.play(FadeIn(et_igual), run_time=0.35)
                    self.wait(0.7)
                    igual_hecho = True
            self.wait(0.45)

        self.wait(1.2)
        rot.mostrar(dato_pie("regla NRZI de HDLC"), zona="abajo",
                    run_time=0.5)
        self.wait(6.5)

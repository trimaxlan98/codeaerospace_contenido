class Clip3(Scene):
    """1.1.3 - Cuantizar: 2^b escalones; el error de redondeo es ruido y
    la SNR MEDIDA sigue la regla 6.02 b + 1.76 dB. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Cuantizar: cuántos escalones")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los niveles parten la vertical ----------------------
        rot.mostrar(pie_curso("El valor medido tambien hay que "
                              "redondearlo: la vertical se parte en "
                              "escalones."),
                    zona="abajo", run_time=0.5)
        on = onda(T_CURVA, Y_CURVA, rango_y=(-1.15, 1.15), ancho=8.2,
                  alto=3.3)
        on.move_to(DOWN * 0.2)
        self.play(FadeIn(on), run_time=0.8)
        niveles, yq3 = cuantizar(Y_CURVA, BITS_GRUESO)
        lineas = VGroup(*[on.horizontal_en(n, color=C_REJILLA)
                          for n in niveles])
        et_b = tag_hud(f"b = {BITS_GRUESO} bits -> "
                       f"{2 ** BITS_GRUESO} niveles",
                       font_size=19, color=C_BIT)
        et_b.next_to(on.en(1.98, 1.1), UP, buff=0.08)
        et_b.shift(LEFT * et_b.width / 2)
        self.play(LaggedStart(*[Create(x) for x in lineas],
                              lag_ratio=0.08), FadeIn(et_b), run_time=1.8)
        self.wait(3.2)

        # --- momento: la escalera gruesa y su SNR -------------------------
        rot.mostrar(pie_curso("Con 3 bits la copia es una escalera "
                              "aspera; la diferencia con la curva es "
                              "RUIDO."),
                    zona="abajo", run_time=0.5)
        esc3 = on.curva_de(T_CURVA, yq3, color=C_BIT)
        self.play(Create(esc3), run_time=1.8)
        snr3 = tag_hud(f"SNR medida = {fmt(SNR_GRUESO, 1)} dB",
                       font_size=20)
        snr3.next_to(on.en(1.0, -1.15), DOWN, buff=0.12)
        self.play(FadeIn(snr3), run_time=0.5)
        self.wait(4.4)

        # --- momento: 8 bits ----------------------------------------------
        rot.mostrar(pie_curso("Con 8 bits los escalones desaparecen a la "
                              "vista: la copia abraza la curva."),
                    zona="abajo", run_time=0.5)
        _, yq8 = cuantizar(Y_CURVA, BITS_FINO)
        esc8 = on.curva_de(T_CURVA, yq8, color=C_BIT)
        et_b8 = tag_hud(f"b = {BITS_FINO} bits -> "
                        f"{2 ** BITS_FINO} niveles",
                        font_size=19, color=C_BIT)
        et_b8.move_to(et_b)
        snr8 = tag_hud(f"SNR medida = {fmt(SNR_FINO, 1)} dB", font_size=20)
        snr8.move_to(snr3)
        self.play(FadeOut(lineas), Transform(esc3, esc8),
                  Transform(et_b, et_b8), Transform(snr3, snr8),
                  run_time=1.4)
        self.wait(5.3)

        # --- momento: la regla MEDIDA -------------------------------------
        rot.mostrar(pie_curso("La regla, comprobada en pantalla: cada bit "
                              "extra regala unos 6 dB de SNR."),
                    zona="abajo", run_time=0.5)
        por_bit = (SNR_FINO - SNR_GRUESO) / (BITS_FINO - BITS_GRUESO)
        cuenta = tag_hud(f"({fmt(SNR_FINO, 1)} - {fmt(SNR_GRUESO, 1)}) / "
                         f"{BITS_FINO - BITS_GRUESO} bits = "
                         f"{fmt(por_bit, 1)} dB por bit", font_size=20)
        cuenta.next_to(snr3, DOWN, buff=0.3)
        self.play(FadeIn(cuenta, shift=0.15 * UP), run_time=0.6)
        self.wait(5.3)

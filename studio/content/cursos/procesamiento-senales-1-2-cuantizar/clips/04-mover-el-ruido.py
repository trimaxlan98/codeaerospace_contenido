class Clip4(Scene):
    """1.2.4 - Sobremuestrear x8 y realimentar el error: el ruido de
    cuantizar no desaparece, se inclina y se marcha de la banda util.
    La SQNR en banda sube 29.9 dB medidos. Cierre de la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Mover el ruido"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        ea = EspectroArea(F_NS, DB_NS_PLANO, piso_db=-60.0, ancho=11.4,
                          alto=3.0, color=C_RUIDO)
        ea.shift(DOWN * 0.25)
        et_hz = tag_hud("Hz", font_size=19, color=C_TENUE)
        et_hz.next_to(ea.en(F_NS[-1], -60.0), DR, buff=0.10)
        et_cero = tag_hud("0", font_size=19, color=C_TENUE)
        et_cero.next_to(ea.en(0.0, -60.0), DOWN, buff=0.16)

        panel = panel_cifras(f"OSR = {OSR}",
                             f"bits = {BITS_NS}",
                             f"fs = {fmt(FS_OSR / 1000.0, 0)} kHz")
        self.play(FadeIn(ea.ejes), FadeIn(et_hz), FadeIn(et_cero),
                  FadeIn(panel), run_time=0.8)
        self.play(Create(ea.curva), FadeIn(ea.area), run_time=2.4)
        self.wait(1.4)

        # --- la rendija que de verdad importa -----------------------------
        x0 = ea.en(0.0, ea.piso)[0]
        x1 = ea.en(BANDA_UTIL, ea.piso)[0]
        banda = Rectangle(width=abs(x1 - x0), height=ea.alto,
                          stroke_width=1.8, stroke_color=C_CALCULO,
                          fill_color=C_CALCULO, fill_opacity=0.26)
        banda.move_to(np.array([(x0 + x1) / 2.0,
                                ea.en(0.0, ea.piso / 2.0)[1], 0.0]))
        et_banda = tag_hud(f"banda util {fmt(BANDA_UTIL, 0)} Hz",
                           font_size=19, color=C_CALCULO)
        et_banda.move_to(np.array([x0 + 1.55, ea.en(0.0, 0.0)[1] + 0.72,
                                   0.0]))
        flecha = Arrow(et_banda.get_bottom(), banda.get_top() + UP * 0.04,
                       buff=0.08, color=C_CALCULO, stroke_width=2.6,
                       max_tip_length_to_length_ratio=0.16)
        self.play(FadeIn(banda), FadeIn(et_banda), Create(flecha),
                  run_time=1.0)
        rot.mostrar(cifra_pie(f"SQNR en banda = {fmt(SQNR_PLANO, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- realimentar el error: el ruido se inclina --------------------
        gem = ea.con_psd(DB_NS_SHAPED)
        self.play(Transform(ea.curva, gem.curva),
                  Transform(ea.area, gem.area), run_time=2.8)
        self.wait(1.2)
        rot.mostrar(formula_pie(r"\mathrm{NTF}(z) = 1 - z^{-1}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        rot.mostrar(cifra_pie(f"SQNR {fmt(SQNR_PLANO, 1)} -> "
                              f"{fmt(SQNR_SHAPED, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        panel_2 = panel_cifras(
            (f"sin NS: {fmt(SQNR_PLANO, 1)} dB", C_RUIDO),
            (f"con NS: {fmt(SQNR_SHAPED, 1)} dB", C_SALIDA),
            (f"ganancia +{fmt(GANANCIA_NS, 1)} dB", C_CALCULO))
        self.play(FadeOut(panel), run_time=0.45)
        self.play(FadeIn(panel_2), run_time=0.7)
        self.wait(2.2)
        rot.mostrar(cifra_pie(f"ganancia = +{fmt(GANANCIA_NS, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        cierre_leccion(self, rot, "El ruido de cuantizar no se borra.",
                       "Se lleva donde no molesta.",
                       ea.ejes, ea.curva, ea.area, banda, et_banda, flecha,
                       et_hz, et_cero, panel_2)

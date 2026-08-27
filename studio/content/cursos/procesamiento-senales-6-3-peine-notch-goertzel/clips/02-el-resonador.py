class Clip2(Scene):
    """6.3.2 - El resonador: un par de polos a radio 0.95 amplifica una
    sola frecuencia, justo donde se pusieron. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("El resonador"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        _, polos, _ = zpk(B_RES, A_RES)
        pz = plano_z([], polos, unidad=1.75, alcance=1.3)
        pz.move_to(LEFT * 3.7 + UP * 0.1)
        et_pz = VGroup(tag_hud(f"r = {fmt(R_RES, 2)}", font_size=19,
                               color=C_MUESTRA),
                       tag_hud(f"w0 = {fmt(W0_RES / np.pi, 2)} pi",
                               font_size=19, color=C_MUESTRA))
        et_pz.arrange(DOWN, buff=0.14)
        et_pz.next_to(pz, DOWN, buff=0.22)
        radial = DashedLine(pz.en(0), pz.punto_en(W0_RES),
                            color=C_CALCULO, stroke_width=1.8,
                            dash_length=0.06)
        self.play(FadeIn(pz.ejes), FadeIn(pz.circulo), run_time=0.6)
        self.play(FadeIn(pz.polos), FadeIn(et_pz), run_time=0.7)
        self.wait(1.8)
        self.play(Create(radial), run_time=0.7)
        self.wait(2.0)

        # --- la respuesta: un solo pico ---------------------------------
        piso = float(MAG_RES.min()) - 3.0
        rf = respuesta_dibujo(W_RES, MAG_RES, ancho=5.4, alto=3.1,
                              piso_db=piso, color=C_SALIDA)
        rf.move_to(RIGHT * 3.7 + UP * 0.1)
        et_rf = tag_hud("|H| en dB", font_size=19, color=C_TENUE)
        et_rf.next_to(rf.ejes, DOWN, buff=0.26)
        self.play(FadeIn(rf.ejes), FadeIn(et_rf), run_time=0.5)
        self.play(Create(rf.curva), run_time=1.9)
        self.wait(1.8)

        marca = rf.marca_w(W_PICO_RES * np.pi)
        punto = rf.punto(W_PICO_RES * np.pi)
        self.play(FadeIn(marca), FadeIn(punto), run_time=0.6)
        rot.mostrar(cifra_pie(f"pico {fmt(PICO_RES, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        rot.mostrar(cifra_pie(f"en {fmt(W_PICO_RES, 3)} pi"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        panel = panel_cifras((f"r = {fmt(R_RES, 2)}", C_MUESTRA),
                             (f"pico {fmt(PICO_RES, 1)} dB", C_CALCULO),
                             (f"en {fmt(W_PICO_RES, 3)} pi", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(7.8)

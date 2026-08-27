class Clip3(Scene):
    """6.3.3 - El notch: un cero sobre el circulo mata una frecuencia
    entera sin tocar a la vecina, a 0.10 dB. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("El notch"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        ceros, polos, _ = zpk(B_NOTCH, A_NOTCH)
        pz = plano_z(ceros, polos, unidad=1.75, alcance=1.3)
        pz.move_to(LEFT * 3.7 + UP * 0.1)
        et_pz = VGroup(tag_hud(f"cero en {fmt(W0_NOTCH / np.pi, 2)} pi",
                               font_size=18, color=C_SALIDA),
                       tag_hud(f"polo r = {fmt(R_NOTCH, 2)}", font_size=18,
                               color=C_RUIDO))
        et_pz.arrange(DOWN, buff=0.14)
        et_pz.next_to(pz, DOWN, buff=0.22)
        self.play(FadeIn(pz.ejes), FadeIn(pz.circulo), run_time=0.6)
        self.play(FadeIn(pz.ceros), FadeIn(pz.polos), FadeIn(et_pz),
                  run_time=0.8)
        self.wait(3.0)

        # --- la respuesta: un agujero muy hondo ------------------------
        rf = respuesta_dibujo(W_N, MAG_N, ancho=5.4, alto=3.1, piso_db=-50.0,
                              techo_db=6.0, color=C_SALIDA)
        rf.move_to(RIGHT * 3.7 + UP * 0.1)
        et_rf = tag_hud("|H| en dB", font_size=19, color=C_TENUE)
        et_rf.next_to(rf.ejes, DOWN, buff=0.26)
        self.play(FadeIn(rf.ejes), FadeIn(et_rf), run_time=0.5)
        self.play(Create(rf.curva), run_time=2.0)
        self.wait(2.0)

        # El cero esta EXACTO sobre el circulo: el minimo real es -infinito
        # y solo se marca la POSICION (nunca su valor: depende de la malla).
        marca_0 = rf.marca_w(W0_NOTCH, color=C_RUIDO)
        self.play(Create(marca_0), run_time=0.6)
        rot.mostrar(cifra_pie(f"bajo -20dB {fmt(ANCHO_20DB * 100, 2)}%"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        marca_v = rf.marca_w(W_VECINO)
        punto_v = rf.punto(W_VECINO)
        self.play(FadeIn(marca_v), FadeIn(punto_v), run_time=0.6)
        rot.mostrar(cifra_pie(f"vecino {fmt(H_VECINO, 2)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.8)

        panel = panel_cifras((f"cero en {fmt(W0_NOTCH / np.pi, 2)} pi",
                              C_SALIDA),
                             (f"vecino {fmt(H_VECINO, 2)} dB", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(8.0)

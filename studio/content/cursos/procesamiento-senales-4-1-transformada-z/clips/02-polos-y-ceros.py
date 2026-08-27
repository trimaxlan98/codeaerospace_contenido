class Clip2(Scene):
    """4.1.2 - Las raices del polinomio son el filtro: los dos ceros
    conjugados hunden la respuesta justo en su angulo. (~29 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("Polos y ceros"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el plano con los dos ceros del FIR ----------------------------
        pz = plano_z(CEROS_FIR, [], unidad=1.55, alcance=1.75)
        pz.move_to(LEFT * 3.35 + DOWN * 0.35)
        self.play(FadeIn(pz.ejes), run_time=0.6)
        self.play(Create(pz.circulo), run_time=1.1)
        self.wait(0.8)

        radios = VGroup(*[Line(pz.en(0), pz.en(z), color=C_CALCULO,
                               stroke_width=1.8, stroke_opacity=0.7)
                          for z in CEROS_FIR])
        self.play(Create(radios), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in pz.ceros],
                              lag_ratio=0.35), run_time=1.0)
        self.wait(1.0)

        panel = panel_cifras((f"r = {fmt(R_CERO, 3)}", C_CALCULO),
                             (f"ang = {fmt(ANG_CERO, 1)} grad", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(5.5)

        # --- la respuesta en frecuencia, con el valle en W_CERO ------------
        resp = respuesta_dibujo(W_FIR, MAG_FIR, ancho=4.6, alto=2.6,
                                color=C_SALIDA)
        resp.move_to(RIGHT * 3.15 + DOWN * 0.2)
        et_resp = tag_hud("mag dB", font_size=17, color=C_TENUE)
        et_resp.next_to(resp, UP, buff=0.18)
        self.play(FadeIn(resp.ejes), FadeIn(et_resp), run_time=0.5)
        self.play(Create(resp.curva), run_time=2.4)
        self.wait(1.8)

        marca = resp.marca_w(W_CERO)
        punto = resp.punto(W_CERO)
        self.play(Create(marca), FadeIn(punto), run_time=0.8)
        rot.mostrar(cifra_pie(f"valle = {fmt(resp.valor(W_CERO), 1)} dB"),
                    zona="abajo", run_time=0.6)
        self.wait(10.5)

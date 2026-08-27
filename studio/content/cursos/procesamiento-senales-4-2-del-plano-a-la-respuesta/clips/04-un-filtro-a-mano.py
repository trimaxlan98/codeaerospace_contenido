class Clip4(Scene):
    """4.2.4 - Un notch dibujado a mano: un cero EN el circulo mata la
    frecuencia y un polo justo detras deja el resto intacto. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("Un filtro a mano"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        ceros_n, polos_n, k_n = zpk(B_NOTCH, A_NOTCH)
        pz = plano_z(ceros_n, polos_n, unidad=1.95, alcance=1.28)
        pz.move_to(LEFT * 3.95 + UP * 0.15)
        self.play(FadeIn(pz.ejes), FadeIn(pz.circulo), run_time=0.8)
        self.play(FadeIn(pz.ceros, scale=0.5), run_time=0.5)
        self.play(FadeIn(pz.polos, scale=0.5), run_time=0.5)
        self.wait(0.8)

        # --- el detalle: el par esta a 0.03 del circulo --------------------
        # A escala 1 el cero y el polo son el mismo pixel; ampliado diez
        # veces se ve que son dos cosas distintas.
        w_n = float(np.angle(ceros_n[0]))
        pz_det = plano_z(ceros_n, polos_n, unidad=10.0 * 1.95, alcance=1.02)
        pz_det.shift(ORIGIN - pz_det.punto_en(w_n))
        et_c = tag_hud("cero", font_size=19, color=C_SALIDA)
        et_c.next_to(pz_det.ceros[0], UP, buff=0.16)
        et_p = tag_hud("polo", font_size=19, color=C_RUIDO)
        et_p.next_to(pz_det.polos[0], DOWN, buff=0.16)
        det = VGroup(pz_det.arco(w_n - 0.028, w_n + 0.028, color=C_MUESTRA,
                                 grosor=2.4),
                     pz_det.ceros[0], pz_det.polos[0], et_c, et_p)
        marco = SurroundingRectangle(det, color=C_TENUE, stroke_width=1.2,
                                     buff=0.22)
        marco.set_stroke(opacity=0.55)
        lupa = VGroup(det, marco)
        lupa.move_to(LEFT * 0.05 + DOWN * 0.20)
        anillo = Circle(radius=0.30, color=C_TENUE, stroke_width=1.4)
        anillo.set_stroke(opacity=0.7)
        anillo.move_to(pz.en(ceros_n[0]))
        guia = DashedLine(anillo.get_right(), marco.get_left(),
                          color=C_TENUE, stroke_width=1.2, dash_length=0.08)
        guia.set_stroke(opacity=0.55)
        self.play(Create(anillo), Create(guia), run_time=0.6)
        self.play(FadeIn(lupa), run_time=0.8)
        self.wait(2.4)

        panel = panel_cifras((f"cero r = {fmt(abs(ceros_n[0]), 2)}",
                              C_SALIDA),
                             (f"polo r = {fmt(abs(polos_n[0]), 2)}",
                              C_RUIDO))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(2.4)

        # --- el agujero que eso abre en la respuesta -----------------------
        piso = MIN_NOTCH - 6.0
        techo = float(MAG_NOTCH.max()) + 4.0
        rf = respuesta_dibujo(W_NOTCH, MAG_NOTCH, ancho=5.0, alto=2.6,
                              piso_db=piso, techo_db=techo)
        rf.move_to(RIGHT * 4.0 + UP * 0.15)
        et_rf = tag_hud("|H| en dB", font_size=19, color=C_TENUE)
        et_rf.next_to(rf.ejes, DOWN, buff=0.26)
        self.play(FadeIn(rf.ejes), FadeIn(et_rf), run_time=0.5)
        self.play(Create(rf.curva), run_time=2.2)
        self.wait(1.0)

        marca = rf.marca_w(W_MIN_NOTCH)
        d_min = rf.punto(W_MIN_NOTCH)
        self.play(FadeIn(marca), FadeIn(d_min), run_time=0.6)
        rot.mostrar(cifra_pie(f"minimo = {fmt(MIN_NOTCH, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)
        rot.mostrar(cifra_pie(f"w = {fmt(W_MIN_NOTCH / np.pi, 3)} pi"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)
        rot.mostrar(formula_pie(
            r"z_0 = e^{j\omega_0} \;\Rightarrow\; H(z_0) = 0"),
            zona="abajo", run_time=0.5)
        self.wait(2.4)

        cierre_leccion(self, rot, "Diseñar un filtro",
                       "es colocar puntos en un plano.",
                       pz, lupa, guia, anillo, panel, rf.ejes, rf.curva,
                       et_rf, marca, d_min)

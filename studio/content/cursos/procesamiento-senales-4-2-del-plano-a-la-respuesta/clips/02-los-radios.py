class Clip2(Scene):
    """4.2.2 - |H| es el producto de las distancias a los ceros entre el
    de las distancias a los polos: la misma cifra que la formula. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("Las distancias"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        pz = plano_z(CEROS_D, POLOS_D, unidad=1.95, alcance=1.28)
        pz.move_to(LEFT * 3.95 + UP * 0.15)
        self.play(FadeIn(pz.ejes), FadeIn(pz.circulo), FadeIn(pz.polos),
                  run_time=0.9)
        self.wait(0.6)

        piso = float(MAG[R_DEMO].min()) - 4.0
        techo = PICO[R_DEMO] + 4.0
        rf = respuesta_dibujo(W_EJE[R_DEMO], MAG[R_DEMO], ancho=5.0,
                              alto=2.6, piso_db=piso, techo_db=techo)
        rf.move_to(RIGHT * 4.0 + UP * 0.15)
        et_rf = tag_hud("|H| en dB", font_size=19, color=C_TENUE)
        et_rf.next_to(rf.ejes, DOWN, buff=0.26)
        self.play(FadeIn(rf.ejes), FadeIn(et_rf), run_time=0.5)
        self.play(Create(rf.curva), run_time=1.8)
        self.wait(0.6)

        # --- un solo w: el punto y su valor --------------------------------
        wt = ValueTracker(W_DEMO)
        d_pz = Dot(pz.punto_en(W_DEMO), radius=0.06, color=C_CALCULO)
        d_pz.add_updater(lambda m: m.move_to(pz.punto_en(wt.get_value())))
        d_rf = Dot(rf.en(W_DEMO, rf.valor(W_DEMO)), radius=0.065,
                   color=C_CALCULO)
        d_rf.add_updater(
            lambda m: m.move_to(rf.en(wt.get_value(),
                                      rf.valor(wt.get_value()))))
        marca = rf.marca_w(W_DEMO)
        self.play(FadeIn(d_pz), FadeIn(d_rf), FadeIn(marca), run_time=0.6)
        rot.mostrar(cifra_pie("w = pi/4"), zona="abajo", run_time=0.5)
        self.wait(1.4)

        # --- los segmentos cuya razon de longitudes ES |H| -----------------
        radios = pz.radios_a(W_DEMO, grosor=2.4)
        self.play(Create(radios), run_time=1.4)
        self.wait(0.8)

        def _panel_d(w):
            d = por_distancias(CEROS_D, POLOS_D, K_D, w)[2]
            return panel_cifras((f"corta = {fmt(float(d.min()), 3)}",
                                 C_RUIDO),
                                (f"larga = {fmt(float(d.max()), 3)}",
                                 C_RUIDO))

        panel = _panel_d(W_DEMO)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(1.6)

        # --- el detalle: 0.08 es TODA la distancia al polo -----------------
        # Una copia del plano 6 veces mas grande, recentrada en el punto:
        # a escala 1 el segmento corto son nueve pixeles.
        i_cerca = int(np.argmin(DIST_POLOS))
        pz_det = plano_z(CEROS_D, POLOS_D, unidad=6.0 * 1.95, alcance=1.05)
        pz_det.shift(ORIGIN - pz_det.punto_en(W_DEMO))
        det = VGroup(
            pz_det.arco(W_DEMO - 0.052, W_DEMO + 0.052, color=C_MUESTRA,
                        grosor=2.4),
            pz_det.radios_a(W_DEMO, grosor=3.0)[i_cerca],
            pz_det.polos[i_cerca],
            Dot(pz_det.punto_en(W_DEMO), radius=0.075, color=C_CALCULO))
        et_det = tag_hud(fmt(D_POLO_CERCA, 3), font_size=20, color=C_RUIDO)
        et_det.next_to(det[1], LEFT, buff=0.16)
        marco = SurroundingRectangle(VGroup(det, et_det), color=C_TENUE,
                                     stroke_width=1.2, buff=0.20)
        marco.set_stroke(opacity=0.55)
        lupa = VGroup(det, et_det, marco)
        lupa.move_to(LEFT * 0.10 + DOWN * 0.30)
        anillo = Circle(radius=0.30, color=C_TENUE, stroke_width=1.4)
        anillo.set_stroke(opacity=0.7)
        anillo.move_to((pz.en(POLOS_D[i_cerca]) + pz.punto_en(W_DEMO)) / 2.0)
        guia = DashedLine(anillo.get_right(), marco.get_left(),
                          color=C_TENUE, stroke_width=1.2, dash_length=0.08)
        guia.set_stroke(opacity=0.55)
        self.play(Create(anillo), Create(guia), run_time=0.6)
        self.play(FadeIn(lupa), run_time=0.8)
        self.wait(2.2)

        def _tag_mod(m):
            t = tag_hud(f"|H| = {fmt(m, 3)}", font_size=22)
            t.next_to(pz, DOWN, buff=0.30)
            return t

        et_mod = _tag_mod(MOD_DIST)
        self.play(FadeIn(et_mod), run_time=0.5)
        self.wait(1.2)

        rot.mostrar(cifra_pie(f"por distancias = {fmt(MOD_DIST, 3)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)
        rot.mostrar(cifra_pie(f"por formula = {fmt(MOD_FORMULA, 3)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)
        rot.mostrar(formula_pie(
            r"\textstyle |H| = \prod_i |z - c_i| \;/\; \prod_k |z - p_k|"),
            zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- el mismo producto en seis angulos ------------------------------
        # Todo cuelga del tracker: los radios, la marca y los dos puntos se
        # redibujan solos y no hay dos versiones en pantalla.
        self.play(FadeOut(lupa), FadeOut(guia), FadeOut(anillo),
                  run_time=0.6)
        radios_vivos = always_redraw(
            lambda: pz.radios_a(wt.get_value(), grosor=2.4))
        marca_viva = always_redraw(lambda: rf.marca_w(wt.get_value()))
        self.remove(radios, marca)
        self.add(radios_vivos, marca_viva)
        # Las cifras NO se morfan durante el viaje (dejaria digitos a medio
        # transformar): saltan de golpe al llegar.
        for w, mod in zip(W_MUESTRA, MOD_EN):
            self.play(wt.animate.set_value(w), run_time=0.9)
            self.play(Transform(panel, _panel_d(w)),
                      Transform(et_mod, _tag_mod(mod)), run_time=0.02)
            self.wait(0.55)

        # De vuelta al pico: la cuenta que abrio el clip lo cierra.
        self.play(wt.animate.set_value(W_DEMO), run_time=1.1)
        self.play(Transform(panel, _panel_d(W_DEMO)),
                  Transform(et_mod, _tag_mod(MOD_DIST)), run_time=0.02)
        rot.mostrar(cifra_pie(f"por distancias = {fmt(MOD_DIST, 3)}"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)

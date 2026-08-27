class Clip2(Scene):
    """6.1.2 - La bilineal mete el semiplano izquierdo ENTERO dentro del
    circulo unidad; el precio es que el eje de frecuencias se dobla. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("La bilineal"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento 1: el semiplano entero cabe en el circulo -----------
        U, A = 1.24, 1.50
        pz = plano_z((), POLOS_S, unidad=U, alcance=A)
        pz.move_to(DOWN * 0.32)
        pz.circulo.set_stroke(color=C_DATO, opacity=0.50, width=1.8)

        semi = Rectangle(width=A * U, height=2 * A * U, stroke_width=0,
                         fill_color=C_SALIDA, fill_opacity=0.10)
        semi.move_to(pz.en(0) + LEFT * (A * U / 2.0))
        et_plano = tag_hud("plano s", font_size=22, color=C_DATO)
        et_plano.move_to(pz.en(1.05 + 1.30j))
        et_wc = tag_hud("radio wc", font_size=19, color=C_DATO)
        et_wc.move_to(pz.en(0.92 - 1.22j))

        self.play(FadeIn(semi), FadeIn(pz), FadeIn(et_plano), FadeIn(et_wc),
                  run_time=1.0)
        rot.mostrar(cifra_pie(f"polos en |p| = "
                              f"{fmt(np.abs(POLOS_S)[0], 2)}"), zona="abajo",
                    run_time=0.5)
        self.wait(1.9)

        # --- la bilineal: el semiplano se dobla dentro del circulo -------
        disco = Circle(radius=U, stroke_width=0, fill_color=C_SALIDA,
                       fill_opacity=0.14)
        disco.move_to(pz.en(0))
        gem = pz.con_pz((), POLOS_Z)
        et_plano_z = tag_hud("plano z", font_size=22, color=C_DATO)
        et_plano_z.move_to(et_plano.get_center())
        rot.mostrar(cifra_pie(f"|z| max = {fmt(RADIO_Z.max(), 3)}"),
                    zona="abajo", run_time=0.5)
        self.play(Transform(semi, disco),
                  Transform(pz.polos, gem.polos),
                  Transform(et_plano, et_plano_z), FadeOut(et_wc),
                  pz.circulo.animate.set_stroke(color=C_MUESTRA, opacity=0.95,
                                                width=2.6),
                  run_time=2.3)
        et_uni = tag_hud("circulo unidad", font_size=19, color=C_MUESTRA)
        et_uni.move_to(pz.en(1.22 - 1.30j))
        self.play(FadeIn(et_uni), run_time=0.4)
        self.wait(1.8)

        panel_r = panel_cifras(*[(f"|z| = {fmt(r, 3)}", C_RUIDO)
                                 for r in RADIO_Z[:2]],
                               ("todos < 1", C_MUESTRA))
        self.play(FadeIn(panel_r), run_time=0.7)
        self.wait(2.6)

        self.play(FadeOut(pz), FadeOut(semi), FadeOut(et_plano),
                  FadeOut(et_uni), FadeOut(panel_r), run_time=0.8)

        # --- momento 2: el precio, el warping ----------------------------
        rfw = respuesta_dibujo(W_WARP, OMEGA_WARP, ancho=8.8, alto=3.3,
                               piso_db=0.0, techo_db=8.0, color=C_CALCULO)
        rfw.move_to(DOWN * 0.55)
        # la curva se dibuja SOLO hasta el techo: pasado 8 sube sin fin y un
        # tramo horizontal pegado al borde mentiria (Omega llega a 31.8).
        _vis = OMEGA_WARP <= rfw.techo
        rfw.curva.set_points_as_corners(
            [rfw.en(a, b) for a, b in zip(W_WARP[_vis], OMEGA_WARP[_vis])])
        et_om = tag_hud("Omega", font_size=19, color=C_TENUE)
        et_om.next_to(rfw.en(W_WARP[0], 8.0), LEFT, buff=0.14)
        et_wpi = tag_hud("w / pi", font_size=19, color=C_TENUE)
        et_wpi.next_to(rfw.en(W_WARP[-1], 0.0), RIGHT, buff=0.26)
        self.play(FadeIn(rfw.ejes), FadeIn(et_om), FadeIn(et_wpi),
                  run_time=0.7)
        rot.limpiar("abajo", run_time=0.4)
        self.play(Create(rfw.curva), run_time=1.8)
        self.wait(1.0)

        # la tangente en el origen: al principio no se nota
        recta = rfw.con_mag(W_WARP / 2.0, color=C_DATO)
        lin = DashedVMobject(recta.curva, num_dashes=44)
        lin.set_stroke(color=C_DATO, width=2.0, opacity=0.65)
        et_lin = tag_hud("lineal", font_size=19, color=C_DATO)
        et_lin.next_to(rfw.en(W_WARP[-1], float(W_WARP[-1] / 2.0)), UP,
                       buff=0.12)
        self.play(Create(lin), FadeIn(et_lin), run_time=0.9)
        self.wait(1.1)

        # --- los tres puntos medidos --------------------------------------
        marcas, puntos, etiquetas = [], [], []
        for w, om in zip(W_EJEMPLOS, OMEGA_EJEMPLOS):
            m = rfw.marca_w(w, color=C_TENUE)
            d = Dot(rfw.en(w, om), radius=0.075, color=C_CALCULO)
            e = tag_hud(f"{fmt(w / np.pi, 2)} pi", font_size=19,
                        color=C_TENUE)
            e.next_to(rfw.en(w, 0.0), DOWN, buff=0.20)
            marcas.append(m)
            puntos.append(d)
            etiquetas.append(e)
            rot.mostrar(cifra_pie(f"{fmt(w / np.pi, 2)} pi -> "
                                  f"{fmt(om, 3)}"), zona="abajo",
                        run_time=0.45)
            self.play(Create(m), FadeIn(e), run_time=0.55)
            self.play(FadeIn(d, scale=1.8), run_time=0.4)
            self.wait(1.1)

        panel_w = panel_cifras(*[(f"{fmt(w / np.pi, 2)} pi -> {fmt(om, 3)}",
                                  C_CALCULO)
                                 for w, om in zip(W_EJEMPLOS,
                                                  OMEGA_EJEMPLOS)])
        self.play(FadeIn(panel_w), run_time=0.7)
        self.wait(1.8)

        # --- el que cuenta: 0.9 pi obliga a diseñar en 6.31 ---------------
        nivel = DashedLine(rfw.en(W_WARP[0], OMEGA_EJEMPLOS[2]),
                           rfw.en(W_EJEMPLOS[2], OMEGA_EJEMPLOS[2]),
                           color=C_RUIDO, stroke_width=2.0, dash_length=0.08)
        et_niv = tag_hud(f"{fmt(OMEGA_EJEMPLOS[2], 3)}", font_size=21,
                         color=C_RUIDO)
        et_niv.next_to(rfw.en(W_WARP[0], OMEGA_EJEMPLOS[2]), RIGHT,
                       buff=0.20).shift(UP * 0.24)
        self.play(Create(nivel), FadeIn(et_niv),
                  puntos[2].animate.set_color(C_RUIDO), run_time=0.9)
        rot.mostrar(cifra_pie(f"{fmt(W_EJEMPLOS[2] / np.pi, 1)} pi pide "
                              f"{fmt(OMEGA_EJEMPLOS[2], 3)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        rot.mostrar(formula_pie(
            r"\Omega = \frac{2}{T}\,\tan(\omega/2)"), zona="abajo",
            run_time=0.5)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"vuelta {fmt(VUELTA[2], 2)} pi"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

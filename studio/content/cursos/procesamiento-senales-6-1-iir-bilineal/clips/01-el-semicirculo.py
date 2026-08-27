class Clip1(Scene):
    """6.1.1 - El Butterworth analogico no es una formula: son cuatro polos
    repartidos por igual en el semicirculo IZQUIERDO del plano s. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("El semicirculo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el plano s (el circulo de plano_z aqui es el radio wc) ------
        U, A = 1.32, 1.50
        pz = plano_z((), POLOS_S, unidad=U, alcance=A)
        pz.move_to(DOWN * 0.28)
        pz.remove(pz.polos)
        pz.circulo.set_stroke(color=C_DATO, opacity=0.55, width=1.8)

        et_plano = tag_hud("plano s", font_size=22, color=C_DATO)
        et_plano.move_to(pz.en(1.02 + 1.30j))
        et_re = tag_hud("Re", font_size=18, color=C_TENUE)
        et_re.next_to(pz.en(A), DOWN, buff=0.12)
        et_im = tag_hud("Im", font_size=18, color=C_TENUE)
        et_im.next_to(pz.en(1j * A), RIGHT, buff=0.12)
        et_wc = tag_hud("radio wc", font_size=19, color=C_DATO)
        et_wc.move_to(pz.en(0.86 - 1.16j))

        self.play(FadeIn(pz), FadeIn(et_plano), FadeIn(et_re), FadeIn(et_im),
                  run_time=1.0)
        rot.mostrar(cifra_pie(f"orden = {ORDEN_ANALOGICO}"), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(et_wc), run_time=0.5)
        self.wait(1.8)

        # --- el semiplano izquierdo: ahi vive lo estable -----------------
        semi = Rectangle(width=A * U, height=2 * A * U, stroke_width=0,
                         fill_color=C_SALIDA, fill_opacity=0.10)
        semi.move_to(pz.en(0) + LEFT * (A * U / 2.0))
        et_semi = tag_hud("estable: Re s < 0", font_size=19, color=C_SALIDA)
        et_semi.next_to(semi, DOWN, buff=0.16)
        self.play(FadeIn(semi), FadeIn(et_semi), run_time=0.8)
        self.wait(2.0)

        # --- el semicirculo izquierdo de radio wc ------------------------
        arco = Arc(radius=U, start_angle=PI / 2.0, angle=PI,
                   color=C_MUESTRA, stroke_width=4.2)
        arco.move_arc_center_to(pz.en(0))
        self.play(Create(arco), run_time=1.4)
        self.wait(1.4)

        # --- los cuatro polos, repartidos por igual ----------------------
        marcas = [pz._marca_polo(p) for p in POLOS_S]
        radios = [DashedLine(pz.en(0), pz.en(p), color=C_TENUE,
                             stroke_width=1.4, dash_length=0.06)
                  for p in POLOS_S]
        self.play(LaggedStart(*[Create(r) for r in radios], lag_ratio=0.30),
                  run_time=1.5)
        self.play(LaggedStart(*[FadeIn(m, scale=1.6) for m in marcas],
                              lag_ratio=0.30), run_time=1.5)
        rot.mostrar(cifra_pie(f"|p| = {fmt(np.abs(POLOS_S)[0], 2)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)

        panel = panel_cifras(*[(f"{fmt(a, 1)} deg", C_RUIDO)
                               for a in ANG_POLOS],
                             (f"|p| = {fmt(np.abs(POLOS_S)[0], 2)}",
                              C_MUESTRA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)

        # --- el reparto: mismo angulo entre polos vecinos ----------------
        a0 = float(np.radians(ANG_POLOS[0]))
        a1 = float(np.radians(ANG_POLOS[1]))
        cuna = Arc(radius=0.55 * U, start_angle=a0, angle=a1 - a0,
                   color=C_CALCULO, stroke_width=3.2)
        cuna.move_arc_center_to(pz.en(0))
        med = (a0 + a1) / 2.0
        et_cuna = tag_hud(f"{fmt(ANG_POLOS[1] - ANG_POLOS[0], 1)} deg",
                          font_size=20)
        et_cuna.move_to(pz.en(0) + 1.68 * U * np.array(
            [np.cos(med), np.sin(med), 0.0]))
        self.play(Create(cuna), FadeIn(et_cuna), run_time=0.9)
        rot.mostrar(cifra_pie(f"reparto {fmt(ANG_POLOS[1] - ANG_POLOS[0], 1)}"
                              f" deg"), zona="abajo", run_time=0.5)
        self.wait(3.0)

        self.play(FadeOut(et_semi), run_time=0.4)
        rot.mostrar(formula_pie(
            r"|H(j\Omega)|^2 = \dfrac{1}{1 + (\Omega/\Omega_c)^{2N}}"),
            zona="abajo", run_time=0.5)
        self.wait(5.6)

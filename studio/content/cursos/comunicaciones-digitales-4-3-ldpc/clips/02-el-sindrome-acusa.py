class Clip2(Scene):
    """4.3.2 - El sindrome acusa: dos bits volteados encienden seis
    comprobaciones y las cuentas H^T s senalan a los sospechosos.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El síndrome acusa")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        g = grafo_ldpc(H_LDPC, X_LIMPIO, S_LIMPIO, ancho=ANCHO_GRAFO,
                       alto=ALTO_GRAFO)
        g.move_to(POS_GRAFO)

        def panel_sindrome(s):
            cab = tag_hud("sindrome  s = H x  (mod 2)", font_size=15,
                          color=C_TENUE)
            fila = tag_hud(" ".join(str(int(v)) for v in s), font_size=20)
            peso = tag_hud(f"peso = {int(s.sum())} de {N_CHECKS}",
                           font_size=18,
                           color=C_RUIDO if s.any() else C_COD)
            return panel_derecha(cab, fila, peso, buff=0.24)

        # --- momento: el mensaje que salio cumplia las nueve --------------
        rot.mostrar(pie_curso("El mensaje que salio cumplia las nueve "
                              "comprobaciones: todas daban par."),
                    zona="abajo", run_time=0.5)
        p_ok = panel_sindrome(S_LIMPIO)
        self.play(FadeIn(g), run_time=0.9)
        self.play(FadeIn(p_ok, shift=0.2 * LEFT), run_time=0.6)
        self.wait(4.4)

        # --- momento: el canal voltea dos bits ----------------------------
        rot.mostrar(pie_curso("El canal voltea dos bits en el camino. "
                              "Nadie avisa cuales."),
                    zona="abajo", run_time=0.5)
        g_volteado = g.con_estado(X_ERROR, None)
        self.play(FadeOut(p_ok), Transform(g, g_volteado), run_time=1.2)
        self.wait(4.2)

        # --- momento: se recalcula el sindrome ----------------------------
        rot.mostrar(pie_curso("El receptor no compara con nada: solo "
                              "vuelve a sumar cada vecindario."),
                    zona="abajo", run_time=0.5)
        g_acusa = g.con_estado(X_ERROR, S_ERROR)
        p_err = panel_sindrome(S_ERROR)
        self.play(Transform(g, g_acusa), run_time=1.2)
        self.play(FadeIn(p_err, shift=0.2 * LEFT), run_time=0.6)
        self.wait(4.4)

        # --- momento: las cuentas por bit ---------------------------------
        rot.mostrar(pie_curso("Cada bit cuenta cuantas comprobaciones "
                              "encendidas lo tocan."),
                    zona="abajo", run_time=0.5)
        cuentas = VGroup()
        for i in range(N_BITS):
            t = tag_hud(str(int(CUENTAS_0[i])), font_size=17)
            t.next_to(g.bit(i), DOWN, buff=0.22)
            cuentas.add(t)
        et_c = tag_junto(cuentas, "acusaciones por bit", direccion=DOWN,
                         buff=0.24)
        self.play(LaggedStart(*[FadeIn(t) for t in cuentas],
                              lag_ratio=0.08), run_time=1.5)
        self.play(FadeIn(et_c), run_time=0.4)
        self.wait(3.8)

        # --- momento: los sospechosos -------------------------------------
        rot.mostrar(pie_curso(f"Dos bits reciben las {CUENTA_MAX} "
                              f"acusaciones posibles. Ninguno mas pasa "
                              f"de {int(np.sort(CUENTAS_0)[-3])}."),
                    zona="abajo", run_time=0.5)
        marcas = VGroup(*[Circle(radius=0.24, color=C_RUIDO,
                                 stroke_width=2.4).move_to(g.bit(i))
                          for i in ACUSADOS])
        self.play(*[Indicate(cuentas[i], color=C_RUIDO, scale_factor=1.5)
                    for i in ACUSADOS],
                  LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.3),
                  run_time=1.4)
        self.wait(5.0)

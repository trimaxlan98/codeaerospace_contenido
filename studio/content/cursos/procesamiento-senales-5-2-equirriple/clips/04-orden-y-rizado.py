class Clip4(Scene):
    """5.2.4 - Cuanto cuesta cada decibelio: orden 40 da -45.4 dB, orden 56
    da -60.1. Y los dos se hallaron PROBANDO, no con una formula. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("Orden y rizado"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el filtro que cumple el pliego -------------------------------
        piso = -80.0
        rf = respuesta_dibujo(W_EQ, MAG_EQ, ancho=9.4, alto=3.6,
                              piso_db=piso, techo_db=8.0, color=C_CALCULO)
        rf.move_to(DOWN * 0.42)
        banda = rf.banda(F_RECHAZO * np.pi, np.pi, color=C_RUIDO,
                         opacidad=0.10)
        nivel_45 = DashedLine(rf.en(F_RECHAZO * np.pi, ATEN_45),
                              rf.en(np.pi, ATEN_45), color=C_CALCULO,
                              stroke_width=1.6, dash_length=0.07)
        t_n45 = tag_hud(f"{fmt(ATEN_45, 1)} dB", color=C_CALCULO)
        t_n45.next_to(nivel_45.get_end(), UR, buff=0.08)
        self.play(FadeIn(rf), FadeIn(banda), run_time=0.9)
        self.play(Create(nivel_45), FadeIn(t_n45), run_time=0.7)
        rot.mostrar(cifra_pie(f"orden {ORDEN_45} da {fmt(ATEN_45, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- pedir 15 dB mas: la gemela del mismo eje ---------------------
        gem = rf.con_mag(MAG_60, color=C_APREND)
        nivel_60 = DashedLine(rf.en(F_RECHAZO * np.pi, ATEN_60),
                              rf.en(np.pi, ATEN_60), color=C_APREND,
                              stroke_width=1.6, dash_length=0.07)
        t_n60 = tag_hud(f"{fmt(ATEN_60, 1)} dB", color=C_APREND)
        t_n60.next_to(nivel_60.get_end(), DR, buff=0.08)
        rot.mostrar(cifra_pie(f"orden {ORDEN_60} da {fmt(ATEN_60, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.play(Transform(rf.curva, gem.curva), run_time=1.6)
        self.play(Create(nivel_60), FadeIn(t_n60), run_time=0.7)
        self.wait(2.6)

        panel = panel_cifras((f"{ORDEN_45}: {fmt(ATEN_45, 1)} dB", C_CALCULO),
                             (f"{ORDEN_60}: {fmt(ATEN_60, 1)} dB", C_APREND),
                             (f"{fmt(ATEN_45 - ATEN_60, 1)} dB "
                              f"por {ORDEN_60 - ORDEN_45}", C_TENUE))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.0)

        # --- de donde salen esos dos ordenes: de probar -------------------
        self.play(FadeOut(rf), FadeOut(banda), FadeOut(nivel_45),
                  FadeOut(nivel_60), FadeOut(t_n45), FadeOut(t_n60),
                  FadeOut(panel), run_time=0.8)

        cache = {}

        def aten_de(orden):
            o = int(round(float(orden) / 2.0)) * 2
            if o not in cache:
                b = fir_equirriple(o, F_PASO, F_RECHAZO, FS_D)
                cache[o] = rizado_db(b, [1.0], F_PASO, F_RECHAZO, FS_D)[1]
            return cache[o]

        ordenes = list(range(ORDEN_45 - 20, ORDEN_60 + 6, 2))
        g = grafica(aten_de, (ordenes[0], ordenes[-1]),
                    (ATEN_60 - 6.0, MAX_V + 3.0), ancho=7.8, alto=3.0,
                    color=C_CALCULO, muestras=len(ordenes))
        g.move_to(DOWN * 0.55 + LEFT * 0.6)
        et_x = tag_hud("orden", font_size=18, color=C_TENUE)
        et_x.next_to(g.ejes[0].get_end(), DR, buff=0.12)
        et_y = tag_hud("dB", font_size=18, color=C_TENUE)
        et_y.next_to(g.ejes[1].get_end(), UP, buff=0.10)
        rot.mostrar(cifra_pie(f"{ORDEN_45} y {ORDEN_60} medidos"),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(g.ejes), FadeIn(et_x), FadeIn(et_y), run_time=0.7)

        pruebas = VGroup(*[Dot(g.punto_de(o), radius=0.055, color=C_MUESTRA)
                           for o in ordenes])
        self.play(LaggedStart(*[FadeIn(p, scale=0.4) for p in pruebas],
                              lag_ratio=0.20), run_time=3.0)
        self.play(Create(g.curva), run_time=1.2)
        self.add(g.curva)
        self.wait(1.6)

        cruce_45 = VGroup(
            g.horizontal_en(ATEN_45, color=C_TENUE),
            g.vertical_en(ORDEN_45, color=C_CALCULO),
            Dot(g.punto_de(ORDEN_45), radius=0.085, color=C_CALCULO))
        cruce_60 = VGroup(
            g.horizontal_en(ATEN_60, color=C_TENUE),
            g.vertical_en(ORDEN_60, color=C_APREND),
            Dot(g.punto_de(ORDEN_60), radius=0.085, color=C_APREND))
        t_45 = tag_hud(f"{ORDEN_45}", color=C_CALCULO)
        t_45.next_to(cruce_45[1].get_start(), DOWN, buff=0.12)
        t_60 = tag_hud(f"{ORDEN_60}", color=C_APREND)
        t_60.next_to(cruce_60[1].get_start(), DOWN, buff=0.12)
        t_a45 = tag_hud(f"{fmt(ATEN_45, 1)} dB", color=C_CALCULO)
        t_a45.next_to(cruce_45[0].get_end(), RIGHT, buff=0.14)
        t_a60 = tag_hud(f"{fmt(ATEN_60, 1)} dB", color=C_APREND)
        t_a60.next_to(cruce_60[0].get_end(), RIGHT, buff=0.14)
        self.play(Create(cruce_45), FadeIn(t_45), FadeIn(t_a45),
                  run_time=0.9)
        self.wait(1.6)
        self.play(Create(cruce_60), FadeIn(t_60), FadeIn(t_a60),
                  run_time=0.9)
        rot.mostrar(cifra_pie(f"{fmt(ATEN_45 - ATEN_60, 1)} dB cuestan "
                              f"{ORDEN_60 - ORDEN_45}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        cierre_leccion(self, rot, "Lo optimo no es lo mas plano.",
                       "Es lo que reparte el error.",
                       g.ejes, g.curva, pruebas, cruce_45, cruce_60,
                       t_45, t_60, t_a45, t_a60, et_x, et_y)

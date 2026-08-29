class Clip3(Scene):
    """2.2.3 - El reductor regala par y cobra velocidad: 0.183 N m en el
    eje de carga contra 0.26 mN m en el motor (N=1000, eta=0.7). Pero la
    velocidad se divide por N, y el keyhole pedia 9.04 deg/s. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("El reductor"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el diagrama: motor -> reductor -> carga -----------------------
        motor = Circle(radius=0.42, color=C_CALCULO, stroke_width=3.2)
        motor.move_to(LEFT * 4.4 + UP * 1.55)
        t_motor = tag_junto(motor, "motor", direccion=UP, buff=0.14)

        caja = RoundedRectangle(corner_radius=0.10, width=2.35, height=0.85,
                                color=C_EJE, stroke_width=3.0)
        caja.move_to(UP * 1.55)
        t_caja = tag_hud(f"N {fmt(N_RED, 0)}  eta {fmt(ETA_RED, 1)}",
                         font_size=15, color=C_TENUE)
        t_caja.move_to(caja)

        carga = Circle(radius=0.5, color=C_CALCULO, stroke_width=3.2)
        carga.move_to(RIGHT * 4.4 + UP * 1.55)
        t_carga = tag_junto(carga, "eje de carga", direccion=UP, buff=0.14)

        fl1 = Arrow(motor.get_right(), caja.get_left(), buff=0.14,
                   color=C_TENUE, stroke_width=3.5)
        fl2 = Arrow(caja.get_right(), carga.get_left(), buff=0.14,
                   color=C_TENUE, stroke_width=3.5)

        self.play(FadeIn(motor), FadeIn(t_motor), run_time=0.7)
        self.play(Create(fl1), FadeIn(caja), FadeIn(t_caja), run_time=0.9)
        self.play(Create(fl2), FadeIn(carga), FadeIn(t_carga), run_time=0.9)
        self.wait(0.6)

        # --- las dos cifras de par, cada una en SU lado --------------------
        tp_motor = tag_hud(f"{fmt(PAR_MOT_MNM, 2)} mN m", font_size=19,
                           color=C_CALCULO)
        tp_motor.next_to(motor, DOWN, buff=0.22)
        tp_carga = tag_hud(f"{fmt(PAR_TOTAL, 3)} N m", font_size=19,
                           color=C_CALCULO)
        tp_carga.next_to(carga, DOWN, buff=0.22)
        self.play(FadeIn(tp_motor), run_time=0.5)
        self.play(FadeIn(tp_carga), run_time=0.5)
        self.wait(1.0)

        rot.mostrar(formula_pie(r"\tau_{motor} = \tau_{carga} / (N\,\eta)"),
                    zona="abajo")
        self.wait(2.4)

        # --- la razon, en escala log: son lados DISTINTOS del reductor -----
        # Centrada mas ARRIBA que el carril de la cifra: a DOWN*1.55 la
        # etiqueta "motor" del pie de barra se comia la formula de abajo
        # (medido en el primer render).
        barras = barras_comparar(
            [PAR_TOTAL, PAR_MOT_MNM / 1000.0], ["carga", "motor"],
            ancho=4.2, alto=1.7, colores=[C_CALCULO, C_CALCULO],
            log=True, unidad="N m")
        barras.move_to(DOWN * 0.95)
        self.play(FadeOut(fl1), FadeOut(fl2), FadeOut(caja), FadeOut(t_caja),
                  run_time=0.5)
        self.play(FadeIn(barras), run_time=1.0)
        self.wait(2.6)

        # --- pero la velocidad se divide entre N ---------------------------
        self.play(FadeOut(barras), FadeOut(tp_motor), FadeOut(tp_carga),
                  run_time=0.6)
        rot.mostrar(formula_pie(r"\omega_{carga} = \omega_{motor} / N"),
                    zona="abajo")
        self.wait(2.2)

        t_key = tag_hud(f"keyhole pide {fmt(AZ_KEYHOLE, 2)} deg/s",
                        font_size=22, color=C_PELIGRO)
        t_key.move_to(RIGHT * 4.4 + DOWN * 0.9)
        self.play(carga.animate.set_color(C_PELIGRO),
                  t_carga.animate.set_color(C_PELIGRO), run_time=0.5)
        self.play(FadeIn(t_key), run_time=0.6)
        self.wait(1.6)

        rot.mostrar(cifra_pie(f"{fmt(AZ_KEYHOLE, 2)} deg/s en carga"),
                    zona="abajo")
        self.wait(1.8)

        # se limpia el diagrama: el panel final es el resumen, y a UR
        # se comia la etiqueta "eje de carga" (medido en el primer render)
        self.play(FadeOut(motor), FadeOut(t_motor), FadeOut(carga),
                  FadeOut(t_carga), FadeOut(t_key), run_time=0.6)

        panel = panel_cifras((f"carga {fmt(PAR_TOTAL, 3)} N m", C_CALCULO),
                             (f"motor {fmt(PAR_MOT_MNM, 2)} mN m",
                              C_CALCULO),
                             (f"keyhole {fmt(AZ_KEYHOLE, 2)} deg/s",
                              C_PELIGRO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(6.8)

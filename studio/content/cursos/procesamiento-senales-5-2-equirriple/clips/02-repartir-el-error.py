class Clip2(Scene):
    """5.2.2 - La idea de Remez, dibujada: bajar lo que sobra sube lo que
    falta, y al mismo orden 40 el peor punto pasa de -28.1 a -45.4. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("Repartir el error"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la de siempre: el diseño por ventanas ------------------------
        piso = -80.0
        rf = respuesta_dibujo(W_V, MAG_V, ancho=9.4, alto=3.6, piso_db=piso,
                              techo_db=8.0, color=C_MUESTRA)
        rf.move_to(DOWN * 0.42)
        et_w = tag_hud("w / pi", font_size=18, color=C_TENUE)
        et_w.next_to(rf.en(np.pi, piso), DR, buff=0.10)
        banda = rf.banda(F_RECHAZO * np.pi, np.pi, color=C_RUIDO,
                         opacidad=0.10)
        self.play(FadeIn(rf), FadeIn(et_w), FadeIn(banda), run_time=0.9)
        rot.mostrar(cifra_pie(f"ventana {fmt(MAX_V, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(1.8)

        w_peor = float(F_V[EN_RECHAZO][int(np.argmax(MAG_V[EN_RECHAZO]))])
        d_peor = rf.punto(w_peor * np.pi, color=C_RUIDO, radio=0.072)
        l_v = DashedLine(rf.en(F_RECHAZO * np.pi, MAX_V),
                         rf.en(np.pi, MAX_V), color=C_RUIDO,
                         stroke_width=1.6, dash_length=0.07)
        t_v = tag_hud(f"{fmt(MAX_V, 1)} dB", color=C_RUIDO)
        t_v.next_to(l_v.get_end(), UR, buff=0.08)
        self.play(FadeIn(d_peor, scale=0.4), Create(l_v), FadeIn(t_v),
                  run_time=0.8)
        self.wait(2.4)

        # --- la gemela: mismo orden, error repartido ----------------------
        gem = rf.con_mag(MAG_EQ, color=C_CALCULO)
        self.play(rf.curva.animate.set_stroke(opacity=0.32), run_time=0.5)
        self.play(Create(gem.curva), run_time=2.2)
        self.add(gem.curva)
        rot.mostrar(cifra_pie(f"equirriple {fmt(ATEN_EQ, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)

        l_e = DashedLine(rf.en(F_RECHAZO * np.pi, ATEN_EQ),
                         rf.en(np.pi, ATEN_EQ), color=C_CALCULO,
                         stroke_width=1.6, dash_length=0.07)
        t_e = tag_hud(f"{fmt(ATEN_EQ, 1)} dB", color=C_CALCULO)
        t_e.next_to(l_e.get_end(), DR, buff=0.08)
        self.play(Create(l_e), FadeIn(t_e), run_time=0.8)
        self.wait(2.6)

        # --- el intercambio: lo que sobra baja, lo que falta sube ---------
        f_baja = Arrow(rf.en(w_peor * np.pi, MAX_V),
                       rf.en(w_peor * np.pi, ATEN_EQ), color=C_RUIDO,
                       buff=0.0, stroke_width=3.4, tip_length=0.16,
                       max_tip_length_to_length_ratio=0.32)
        w_sobra = 0.62 * np.pi
        f_sube = Arrow(rf.en(w_sobra, rf.valor(w_sobra)),
                       rf.en(w_sobra, ATEN_EQ), color=C_CALCULO, buff=0.0,
                       stroke_width=3.4, tip_length=0.16,
                       max_tip_length_to_length_ratio=0.32)
        t_gana = _con_fondo(tag_hud(f"{fmt(MAX_V - ATEN_EQ, 1)} dB",
                                    color=C_RUIDO), buff=0.10,
                            opacidad=0.92)
        t_gana.next_to(f_baja, LEFT, buff=0.16)
        self.play(GrowArrow(f_baja), FadeIn(t_gana), run_time=0.8)
        self.wait(1.4)
        self.play(GrowArrow(f_sube), run_time=0.8)
        self.wait(2.2)

        panel = panel_cifras((f"ventana {fmt(MAX_V, 1)} dB", C_MUESTRA),
                             (f"equirriple {fmt(ATEN_EQ, 1)} dB", C_CALCULO),
                             (f"mismo orden {ORDEN}", C_TENUE))
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie(f"gana {fmt(MAX_V - ATEN_EQ, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)

        rot.mostrar(cifra_pie(f"rizado paso {fmt(RIZADO_EQ, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

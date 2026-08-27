class Clip1(Scene):
    """5.2.1 - El diseño por ventanas cumple de sobra casi en todas partes
    y falla justo al lado de la transicion: 27 dB de margen sobrante. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("El margen que sobra"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la respuesta del diseño por ventanas -------------------------
        piso = -125.0
        rf = respuesta_dibujo(W_V, MAG_V, ancho=9.4, alto=3.4, piso_db=piso,
                              techo_db=8.0, color=C_MUESTRA)
        rf.move_to(DOWN * 0.45)
        et_w = tag_hud("w / pi", font_size=18, color=C_TENUE)
        et_w.next_to(rf.en(np.pi, piso), DR, buff=0.10)
        self.play(FadeIn(rf), FadeIn(et_w), run_time=0.9)
        rot.mostrar(cifra_pie(f"hamming orden {ORDEN}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)

        # --- donde se juzga: la banda de rechazo --------------------------
        banda = rf.banda(F_RECHAZO * np.pi, np.pi, color=C_RUIDO,
                         opacidad=0.10)
        marca = rf.marca_w(F_RECHAZO * np.pi, color=C_TENUE)
        et_r = tag_hud(f"{fmt(F_RECHAZO, 2)} pi", font_size=18,
                       color=C_TENUE)
        et_r.next_to(rf.en(F_RECHAZO * np.pi, 8.0), UP, buff=0.10)
        self.play(FadeIn(banda), Create(marca), FadeIn(et_r), run_time=0.8)
        self.wait(2.0)

        # --- el peor punto, que es el que manda ---------------------------
        w_peor = float(F_V[EN_RECHAZO][int(np.argmax(MAG_V[EN_RECHAZO]))])
        # el lobulo MAS ALTO (no el nulo mas hondo: eso depende
        # de la malla y no significa nada del filtro)
        w_mejor = PICOS_LOBULO[int(np.argmax(ALTURAS_LOBULO))]
        d_peor = rf.punto(w_peor * np.pi, color=C_RUIDO, radio=0.075)
        t_peor = tag_hud(f"{fmt(MAX_V, 1)} dB", color=C_RUIDO)
        t_peor.next_to(d_peor, UR, buff=0.10)
        rot.mostrar(cifra_pie(f"peor punto {fmt(MAX_V, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(d_peor, scale=0.4), FadeIn(t_peor), run_time=0.7)
        self.wait(2.6)

        # --- y donde el filtro se pasa de bueno ---------------------------
        d_mejor = rf.punto(w_mejor * np.pi, color=C_CALCULO, radio=0.075)
        t_mejor = tag_hud(f"{fmt(NIVEL_SOSTENIDO, 1)} dB", color=C_CALCULO)
        t_mejor.next_to(d_mejor, DOWN, buff=0.16)
        rot.mostrar(cifra_pie(f"lobulos {fmt(NIVEL_SOSTENIDO, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(d_mejor, scale=0.4), FadeIn(t_mejor), run_time=0.7)
        self.wait(2.6)

        # --- lo que hay entre uno y otro: orden desperdiciado -------------
        l_peor = DashedLine(rf.en(F_RECHAZO * np.pi, MAX_V),
                            rf.en(np.pi, MAX_V), color=C_RUIDO,
                            stroke_width=1.5, dash_length=0.07)
        l_mejor = DashedLine(rf.en(F_RECHAZO * np.pi, NIVEL_SOSTENIDO),
                             rf.en(np.pi, NIVEL_SOSTENIDO), color=C_CALCULO,
                             stroke_width=1.5, dash_length=0.07)
        self.play(Create(l_peor), Create(l_mejor), run_time=0.9)
        self.wait(1.2)

        w_flecha = 0.90 * np.pi
        flecha = DoubleArrow(rf.en(w_flecha, NIVEL_SOSTENIDO),
                             rf.en(w_flecha, MAX_V),
                             color=C_CALCULO, buff=0.0, stroke_width=3.0,
                             tip_length=0.16)
        t_der = _con_fondo(tag_hud(f"{fmt(DERROCHE, 1)} dB de margen"),
                           buff=0.10, opacidad=0.92)
        t_der.next_to(flecha, UP, buff=0.12)
        self.play(GrowFromCenter(flecha), FadeIn(t_der), run_time=0.9)
        rot.mostrar(cifra_pie(f"margen {fmt(DERROCHE, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        panel = panel_cifras((f"peor {fmt(MAX_V, 1)} dB", C_RUIDO),
                             (f"lobulos {fmt(NIVEL_SOSTENIDO, 1)} dB", C_CALCULO),
                             (f"margen {fmt(DERROCHE, 1)} dB", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"{fmt(DERROCHE, 1)} dB sobrantes"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

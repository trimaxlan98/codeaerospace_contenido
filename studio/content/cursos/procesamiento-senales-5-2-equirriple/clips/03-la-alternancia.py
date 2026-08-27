class Clip3(Scene):
    """5.2.3 - Los 14 extremos del rizado, marcados uno a uno: todos miden
    lo mismo dentro de 0.055 dB. Ese es el teorema. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("La alternancia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la equirriple sola, con su banda de rechazo ------------------
        piso = -80.0
        rf = respuesta_dibujo(W_EQ, MAG_EQ, ancho=9.6, alto=3.6,
                              piso_db=piso, techo_db=8.0, color=C_CALCULO)
        rf.move_to(DOWN * 0.42)
        et_w = tag_hud("w / pi", font_size=18, color=C_TENUE)
        et_w.next_to(rf.en(np.pi, piso), DR, buff=0.10)
        banda = rf.banda(F_RECHAZO * np.pi, np.pi, color=C_RUIDO,
                         opacidad=0.10)
        self.play(FadeIn(rf), FadeIn(et_w), FadeIn(banda), run_time=0.9)
        rot.mostrar(cifra_pie(f"equirriple orden {ORDEN}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        # --- donde el error toca su tope ----------------------------------
        puntos = VGroup(*[rf.punto(f * np.pi, color=C_APREND, radio=0.068)
                          for f in ALT])
        rot.mostrar(cifra_pie(f"{len(ALT)} extremos"), zona="abajo",
                    run_time=0.5)
        self.play(LaggedStart(*[FadeIn(p, scale=0.35) for p in puntos],
                              lag_ratio=0.22), run_time=3.4)
        self.wait(2.2)

        # --- todos a la misma altura --------------------------------------
        nivel = DashedLine(rf.en(F_RECHAZO * np.pi, ATEN_EQ),
                           rf.en(np.pi, ATEN_EQ), color=C_APREND,
                           stroke_width=1.8, dash_length=0.07)
        t_niv = tag_hud(f"{fmt(ATEN_EQ, 1)} dB", color=C_APREND)
        t_niv.next_to(nivel.get_end(), DR, buff=0.08)
        self.play(Create(nivel), FadeIn(t_niv), run_time=1.0)
        self.wait(2.6)

        # --- el mayor y el menor de los catorce ---------------------------
        i_may = int(np.argmax(ALTURAS))
        i_men = int(np.argmin(ALTURAS))
        aro_may = Circle(radius=0.17, color=C_RUIDO, stroke_width=2.6)
        aro_may.move_to(puntos[i_may].get_center())
        aro_men = Circle(radius=0.17, color=C_MUESTRA, stroke_width=2.6)
        aro_men.move_to(puntos[i_men].get_center())
        self.play(Create(aro_may), run_time=0.6)
        self.play(Create(aro_men), run_time=0.6)
        rot.mostrar(cifra_pie(f"mayor {fmt(max(ALTURAS), 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)
        rot.mostrar(cifra_pie(f"menor {fmt(min(ALTURAS), 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)

        panel = panel_cifras((f"{len(ALT)} extremos", C_APREND),
                             (f"mayor {fmt(max(ALTURAS), 2)} dB", C_RUIDO),
                             (f"menor {fmt(min(ALTURAS), 2)} dB", C_MUESTRA),
                             (f"spread {fmt(SPREAD, 3)} dB", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie(f"spread {fmt(SPREAD, 3)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        rot.mostrar(cifra_pie(f"{len(ALT)} extremos iguales"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

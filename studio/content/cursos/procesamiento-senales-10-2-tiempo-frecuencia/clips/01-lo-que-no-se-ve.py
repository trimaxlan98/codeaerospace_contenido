class Clip1(Scene):
    """10.2.1 - Un barrido con un golpe corto metido en 3/5 de la señal.
    En el tiempo el golpe salta a la vista. En el espectro entero hay
    energia a su frecuencia... y ni una pista de CUANDO. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("Lo que el espectro no ve"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la señal en el tiempo ----------------------------------------
        # Los 2048 tallos, sin diezmar: pintar uno de cada dos alias el
        # barrido y le inventa una envolvente que no tiene.
        sec = Secuencia(X_TF, 0, None, ancho=9.0, alto=1.5,
                        color=C_SENAL, radio=0.008, grosor=1.0, eje_y=False)
        sec.move_to(UP * 1.78 + LEFT * 0.9)
        et_x = tag_hud("x[n]", font_size=19, color=C_SENAL)
        et_x.next_to(sec, LEFT, buff=0.24)
        self.play(FadeIn(sec), FadeIn(et_x), run_time=1.0)
        self.wait(1.5)

        # --- el golpe SI se ve en el tiempo -------------------------------
        vent = sec.ventana(POS_GOLPE - 18, POS_GOLPE + 58, color=C_CALCULO,
                           opacidad=0.18)
        et_g = tag_hud("golpe", font_size=19, color=C_CALCULO)
        et_g.next_to(vent, UP, buff=0.12)
        self.play(Create(vent), FadeIn(et_g), run_time=0.8)
        rot.mostrar(cifra_pie(f"golpe en n = {POS_GOLPE}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- y ahora el espectro de TODA la señal --------------------------
        piso = -70.0
        rf = respuesta_dibujo(F_TF, DB_TF, ancho=9.0, alto=2.7,
                              piso_db=piso, techo_db=3.0, color=C_BANDA)
        rf.move_to(DOWN * 1.42 + LEFT * 0.9)
        et_f = tag_hud("frecuencia", font_size=18, color=C_TENUE)
        et_f.next_to(rf.en(F_TF[-1], piso), DR, buff=0.10)
        self.play(Create(rf.ejes), run_time=0.5)
        self.play(Create(rf.curva), FadeIn(et_f), run_time=1.8)
        self.add(rf.curva)
        rot.mostrar(cifra_pie(f"{len(F_TF)} bins de frecuencia"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- la energia del golpe, medida en la malla tiempo-frecuencia ---
        n_v = NPER[1]
        j_g = int(np.argmin(np.abs(T_S[n_v] - T_GOLPE)))
        dif = S_DB[n_v][:, j_g] - S_DB[n_v][:, j_g - 3]
        i_f = int(np.argmax(dif))
        f_golpe = float(F_S[n_v][i_f])
        msk = np.nonzero(dif > dif[i_f] - 20.0)[0]
        banda = rf.banda(float(F_S[n_v][msk[0]]), float(F_S[n_v][msk[-1]]),
                         color=C_CALCULO, opacidad=0.16)
        pt = rf.punto(f_golpe, color=C_CALCULO)
        et_db = tag_hud(f"{fmt(rf.valor(f_golpe), 1)} dB", font_size=19,
                        color=C_CALCULO)
        et_db.next_to(pt, UR, buff=0.10)
        self.play(FadeIn(banda), run_time=0.6)
        self.play(FadeIn(pt), FadeIn(et_db), run_time=0.6)
        rot.mostrar(cifra_pie(f"energia en f = {fmt(f_golpe, 3)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- pero el eje de abajo no es el tiempo -------------------------
        flecha = Arrow(rf.en(F_TF[0], piso), rf.en(F_TF[-1], piso),
                       buff=0.0, color=C_RUIDO, stroke_width=3.0,
                       max_tip_length_to_length_ratio=0.05)
        self.play(Create(flecha), run_time=0.9)
        self.play(Indicate(et_f, color=C_RUIDO, scale_factor=1.25),
                  run_time=0.8)
        self.wait(0.6)

        panel = panel_cifras((f"N = {N_TF}", C_SENAL),
                             (f"golpe n = {POS_GOLPE}", C_CALCULO),
                             ("eje frecuencia", C_RUIDO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)
        rot.mostrar(cifra_pie("cero ejes de tiempo", color=C_RUIDO),
                    zona="abajo", run_time=0.5)
        self.wait(8.4)

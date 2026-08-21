class Clip2(Scene):
    """1.1.2 - Muestrear a fs suficiente reconstruye; muestrear poco crea
    un ALIAS: el seno de 7 Hz a 10 Hz se disfraza de 3 Hz. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Muestrear: cada cuánto preguntar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: las muestras caen sobre la telemetria ---------------
        rot.mostrar(pie_curso("Preguntamos 10 veces por segundo: la curva "
                              "se vuelve una lista de valores."),
                    zona="abajo", run_time=0.5)
        on = onda(T_CURVA, Y_CURVA, rango_y=(-1.15, 1.15), ancho=8.2,
                  alto=3.1)
        on.move_to(DOWN * 0.2)
        self.play(FadeIn(on), run_time=0.8)
        tk, yk = muestrear(SENAL_TELE, FS_BUENA, T_FIN)
        ms = on.muestras(tk, yk, radio=0.05)
        cifra_fs = tag_hud(f"fs = {fmt(FS_BUENA, 0)} Hz", font_size=19,
                           color=C_BIT)
        cifra_fs.next_to(on.en(1.85, 1.05), UP, buff=0.1)
        self.play(LaggedStart(*[FadeIn(m) for m in ms], lag_ratio=0.06),
                  FadeIn(cifra_fs), run_time=2.2)
        self.wait(2.6)

        # --- momento: con las muestras basta ------------------------------
        rot.mostrar(pie_curso("Si preguntamos lo bastante seguido, la "
                              "lista guarda TODA la curva."),
                    zona="abajo", run_time=0.5)
        curva_tenue = on.curva.copy()
        self.play(on.curva.animate.set_stroke(opacity=0.25), run_time=0.7)
        self.play(Create(curva_tenue), run_time=1.8)
        self.wait(2.2)

        # --- momento: el alias --------------------------------------------
        rot.mostrar(pie_curso("Pero si la señal es rapida y preguntamos "
                              "poco, la lista MIENTE."),
                    zona="abajo", run_time=0.5)
        y7 = np.array([math.sin(2 * math.pi * F_SENO_ALIAS * t)
                       for t in T_CURVA])
        on7 = on.con_serie(y7)
        self.play(FadeOut(ms), FadeOut(curva_tenue), FadeOut(cifra_fs),
                  Transform(on.curva, on7.curva), run_time=1.0)
        tk7, yk7 = muestrear(
            lambda t: math.sin(2 * math.pi * F_SENO_ALIAS * t),
            FS_ALIAS, T_FIN)
        ms7 = on.muestras(tk7, yk7, radio=0.05)
        et7 = tag_hud(f"{fmt(F_SENO_ALIAS, 0)} Hz medido a "
                      f"{fmt(FS_ALIAS, 0)} Hz", font_size=19, color=C_BIT)
        et7.next_to(on.en(1.0, 1.12), UP, buff=0.08)
        self.play(LaggedStart(*[FadeIn(m) for m in ms7], lag_ratio=0.05),
                  FadeIn(et7), run_time=1.8)
        self.wait(1.6)

        rot.mostrar(pie_curso("Otro seno, MAS LENTO, pasa por los mismos "
                              "puntos: el receptor no puede distinguirlos."),
                    zona="abajo", run_time=0.5)
        # 7 Hz a 10 Hz se pliega a fs - f = 3 Hz con la fase INVERTIDA:
        # el seno que pasa por las mismas muestras es -sin(2 pi 3 t).
        y3 = np.array([-math.sin(2 * math.pi * F_ALIAS * t)
                       for t in T_CURVA])
        alias = on.curva_de(T_CURVA, y3, color=C_RUIDO)
        et3 = tag_hud(f"parece de {fmt(F_ALIAS, 0)} Hz", font_size=19,
                      color=C_RUIDO)
        et3.next_to(on.en(1.62, -1.12), DOWN, buff=0.1)
        self.play(Create(alias), FadeIn(et3), run_time=2.0)
        self.wait(2.6)

        # --- momento: la regla de Nyquist ---------------------------------
        rot.mostrar(formula_pie(r"f_s > 2\, f_{\max}"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

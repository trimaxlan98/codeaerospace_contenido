class Clip2(Scene):
    """10.2.2 - La STFT: trocear, ventanear, una DFT por trozo y las
    columnas una al lado de otra. Sale la rampa del barrido y la columna
    del golpe, ahora SI en su instante. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("El espectrograma"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        n_v = NPER[1]

        # --- la misma señal de antes --------------------------------------
        sec = Secuencia(X_TF, 0, None, ancho=9.0, alto=1.1,
                        color=C_SENAL, radio=0.008, grosor=1.0, eje_y=False)
        sec.move_to(UP * 2.35 + LEFT * 0.9)
        self.play(FadeIn(sec), run_time=0.9)
        self.wait(1.2)

        # --- una ventana que recorre la señal ------------------------------
        vent = sec.ventana(0, n_v - 1, color=C_CALCULO, opacidad=0.20)
        et_v = tag_hud(f"ventana {n_v}", font_size=19, color=C_CALCULO)
        et_v.next_to(vent, DOWN, buff=0.14)   # ARRIBA cruza el titulo al deslizar
        movil = VGroup(vent, et_v)
        self.play(Create(vent), FadeIn(et_v), run_time=0.8)
        rot.mostrar(cifra_pie(f"ventana {n_v} muestras"), zona="abajo",
                    run_time=0.5)
        self.wait(1.8)

        # --- la malla tiempo-frecuencia, columna a columna -----------------
        # 129 x 29 rectangulos son demasiados: se pinta uno de cada dos en
        # los DOS ejes, que es lo unico que conserva la forma de la celda.
        k = 2
        esp = Espectrograma(T_S[n_v][::k], F_S[n_v][::k],
                            S_DB[n_v][::k, ::k], ancho=9.0, alto=3.0,
                            piso_db=-60.0)
        esp.move_to(DOWN * 0.85 + LEFT * 0.9)
        et_t = tag_hud("tiempo", font_size=18, color=C_TENUE)
        et_t.next_to(esp.en(esp.t[-1], esp.f[0]), DR, buff=0.12)
        et_fr = tag_hud("frecuencia", font_size=18, color=C_TENUE)
        et_fr.rotate(PI / 2)
        et_fr.next_to(esp.en(esp.t[0], esp.f[0]), LEFT, buff=0.16)
        et_fr.shift(UP * esp.alto * 0.5)
        self.play(FadeIn(esp.ejes), FadeIn(et_t), FadeIn(et_fr),
                  run_time=0.7)

        columnas = VGroup(*[VGroup(*[esp.celda(i, j)
                                     for i in range(esp.n_f)])
                            for j in range(esp.n_t)])
        dx = (sec.en(N_TF - n_v / 2, 0)[0] - sec.en(n_v / 2, 0)[0])
        self.play(movil.animate.shift(RIGHT * dx),
                  LaggedStart(*[FadeIn(c) for c in columnas],
                              lag_ratio=1.0 / esp.n_t),
                  run_time=4.6)
        self.add(esp.celdas)
        self.wait(1.6)

        # --- lo que la malla enseña: la rampa y el golpe --------------------
        marca = esp.marca_t(T_GOLPE, color=C_CALCULO)
        et_g = tag_hud("golpe", font_size=19, color=C_CALCULO)
        et_g.next_to(esp.en(T_GOLPE, esp.f[-1]), UP, buff=0.10)
        self.play(Create(marca), FadeIn(et_g), run_time=0.9)
        rot.mostrar(cifra_pie(f"golpe en t = {int(T_GOLPE)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        # la rampa: el rotulo se cuelga de la celda mas encendida de una
        # columna temprana, no de una posicion a ojo.
        j_r = esp.n_t // 3
        i_r = int(np.argmax(esp.s[:, j_r]))
        et_b = tag_hud("barrido", font_size=19, color=C_BANDA)
        et_b.move_to(esp.en(esp.t[j_r], esp.f[i_r]) + UP * 0.42)
        self.play(FadeIn(et_b), run_time=0.6)
        self.wait(2.2)

        self.play(FadeOut(movil), run_time=0.6)

        panel = panel_cifras((f"ventana {n_v}", C_CALCULO),
                             (f"golpe t = {int(T_GOLPE)}", C_CALCULO),
                             (f"N = {N_TF}", C_SENAL))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)
        rot.mostrar(
            formula_pie(r"X[m,k]=\sum_n x[n]\,w[n-m]\,e^{-j\omega_k n}"),
            zona="abajo", run_time=0.5)
        self.wait(7.0)

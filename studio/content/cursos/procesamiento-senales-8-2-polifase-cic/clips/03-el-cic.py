class Clip3(Scene):
    """8.2.3 - Integradores, diezmado y peines: diezmar sin UN SOLO
    multiplicador, con nulos justo donde caeria el alias. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("El CIC"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- la cadena: N acumuladores, el diezmado, N peines -------------
        acum = [bloque("acum", ancho=1.15, alto=0.66, color=C_SENAL,
                       tamano=18) for _ in range(N_CIC)]
        dec = bloque(f"baja {R_CIC}", ancho=1.3, alto=0.66, color=C_CALCULO,
                     tamano=18)
        pei = [bloque("resta", ancho=1.15, alto=0.66, color=C_SALIDA,
                      tamano=18) for _ in range(N_CIC)]
        cadena = VGroup(*acum, dec, *pei).arrange(RIGHT, buff=0.52)
        cadena.move_to(UP * 1.7)
        cx = [conectar(cadena[i], cadena[i + 1])
              for i in range(len(cadena) - 1)]

        self.play(LaggedStart(*[FadeIn(b) for b in cadena], lag_ratio=0.12),
                  run_time=1.8)
        self.play(LaggedStart(*[Create(c) for c in cx], lag_ratio=0.10),
                  run_time=1.0)

        lla_i = llave(VGroup(*acum), "integradores", direccion=UP,
                      font_size=20, color=C_SENAL)
        lla_p = llave(VGroup(*pei), "peines", direccion=UP, font_size=20,
                      color=C_SALIDA)
        self.play(Create(lla_i), Create(lla_p), run_time=0.9)
        rot.mostrar(cifra_pie(f"{N_CIC} etapas, R = {R_CIC}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)

        self.play(flujo(cx))
        rot.mostrar(cifra_pie(f"multiplicadores = {MULT_CIC}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- la señal recorriendo la cadena -------------------------------
        n_ver = 128
        x_ver = X_C[:n_ver]
        y_ver = Y_CIC[2:2 + n_ver // R_CIC]
        sx = Secuencia(x_ver, 0, (-1.55, 1.55), ancho=11.0, alto=1.5,
                       color=C_SENAL, radio=0.022, grosor=1.5, eje_y=False)
        sx.move_to(DOWN * 0.35)
        et_x = tag_hud("entrada", font_size=19, color=C_SENAL)
        et_x.next_to(sx, UP, buff=0.10).align_to(sx, LEFT)
        self.play(FadeIn(sx.ejes), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(sx.tallo(i)) for i in range(n_ver)],
                              lag_ratio=0.006),
                  LaggedStart(*[FadeIn(sx.punto(i)) for i in range(n_ver)],
                              lag_ratio=0.006), run_time=1.6)
        self.play(FadeIn(et_x), run_time=0.4)
        self.wait(1.4)

        y_n = y_ver / float(np.max(np.abs(y_ver)))
        sy = Secuencia(y_n, 0, (-1.25, 1.25), ancho=11.0, alto=1.2,
                       color=C_SALIDA, radio=0.055, eje_y=False)
        sy.move_to(DOWN * 2.05)
        et_y = tag_hud("salida", font_size=19, color=C_SALIDA)
        et_y.next_to(sy, UP, buff=0.10).align_to(sy, LEFT)
        self.play(FadeIn(sy), FadeIn(et_y), run_time=1.2)
        rot.mostrar(cifra_pie(f"{n_ver} entran {len(y_ver)} salen"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- su respuesta: nulos en los multiplos de 1/R ------------------
        self.play(FadeOut(sx), FadeOut(et_x), FadeOut(sy), FadeOut(et_y),
                  run_time=0.7)
        resp = respuesta_dibujo(F_CIC, DB_CIC, ancho=8.6, alto=2.4,
                                piso_db=-60.0, techo_db=5.0, color=C_SALIDA)
        resp.move_to(DOWN * 1.15)
        et_f = tag_hud("f / fs", font_size=18, color=C_TENUE)
        et_f.next_to(resp.ejes[0], DOWN, buff=0.28)
        et_f.align_to(resp, RIGHT)
        self.play(FadeIn(resp.ejes), FadeIn(et_f), run_time=0.5)
        self.play(Create(resp.curva), run_time=1.6)
        self.wait(1.0)

        marcas = VGroup(*[resp.marca_w(nu, color=C_RUIDO)
                          for nu in NULOS_CIC])
        ets = VGroup()
        for nu in NULOS_CIC:
            t = tag_hud(f"{fmt(nu, 3)}", font_size=18, color=C_RUIDO)
            t.move_to(resp.en(nu, 5.0)).shift(UP * 0.22)
            ets.add(t)
        self.play(LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.18),
                  run_time=1.2)
        self.play(LaggedStart(*[FadeIn(t) for t in ets], lag_ratio=0.18),
                  run_time=0.7)
        rot.mostrar(cifra_pie(f"nulos en multiplos de 1/{R_CIC}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        rot.mostrar(cifra_pie(f"multiplicadores = {MULT_CIC}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

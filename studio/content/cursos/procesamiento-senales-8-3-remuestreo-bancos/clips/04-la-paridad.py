class Clip4(Scene):
    """8.3.4 - Para separar bien hacen falta filtros mas largos, y su
    longitud tiene que ser PAR: con 31 taps la cancelacion del alias del
    QMF no se cumple y el error se multiplica por 49. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("La longitud importa"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- de dos taps a treinta y dos: la misma caja, otra curva -------
        resp = RespuestaFrec(W_H, MAG_H0, ancho=7.6, alto=3.0, piso_db=-80.0,
                             techo_db=6.0, color=C_SALIDA)
        resp.move_to(DOWN * 0.35)
        cur_h1 = resp.con_mag(MAG_H1, color=C_BANDA).curva
        et_w0 = tag_hud("0", font_size=17, color=C_TENUE)
        et_w0.next_to(resp.en(W_H[0], -80.0), DOWN, buff=0.18)
        et_w1 = tag_hud("pi", font_size=17, color=C_TENUE)
        et_w1.next_to(resp.en(W_H[-1], -80.0), DOWN, buff=0.18)
        et_0 = tag_hud("0 dB", font_size=17, color=C_TENUE)
        et_0.next_to(resp.en(W_H[0], 0.0), LEFT, buff=0.16)
        et_80 = tag_hud("-80 dB", font_size=17, color=C_TENUE)
        et_80.next_to(resp.en(W_H[0], -80.0), LEFT, buff=0.16)

        self.play(FadeIn(resp), FadeIn(cur_h1), FadeIn(et_w0), FadeIn(et_w1),
                  FadeIn(et_0), FadeIn(et_80), run_time=1.0)
        rot.mostrar(cifra_pie(f"{TAPS_HAAR} taps"), zona="abajo",
                    run_time=0.5)
        self.wait(1.8)

        w_ref = 0.75 * np.pi
        db_haar = float(np.interp(w_ref, W_H, MAG_H0))
        db_qmf = float(np.interp(w_ref, W_Q, MAG_Q0))
        marca = resp.marca_w(w_ref)
        punto = Dot(resp.en(w_ref, db_haar), radius=0.07, color=C_CALCULO)
        self.play(Create(marca), FadeIn(punto), run_time=0.6)
        rot.mostrar(cifra_pie(f"0.75 pi: {fmt(db_haar, 1)} dB"), zona="abajo",
                    run_time=0.45)
        self.wait(2.4)

        self.play(Transform(resp.curva, resp.con_mag(MAG_Q0).curva),
                  Transform(cur_h1, resp.con_mag(MAG_Q1,
                                                 color=C_BANDA).curva),
                  Transform(punto, Dot(resp.en(w_ref, db_qmf), radius=0.07,
                                       color=C_CALCULO)),
                  run_time=1.6)
        rot.mostrar(cifra_pie(f"{TAPS_QMF} taps"), zona="abajo",
                    run_time=0.45)
        self.wait(1.8)
        rot.mostrar(cifra_pie(f"0.75 pi: {fmt(db_qmf, 1)} dB"), zona="abajo",
                    run_time=0.45)
        self.wait(3.0)

        # el pie suelta la cifra de la respuesta ANTES de que la respuesta
        # se vaya: si no, se queda rotulando una curva que ya no esta.
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeOut(resp), FadeOut(cur_h1), FadeOut(marca),
                  FadeOut(punto), FadeOut(et_w0), FadeOut(et_w1),
                  FadeOut(et_0), FadeOut(et_80), run_time=0.7)

        # --- lo que sale al volver a juntar: par frente a impar -----------
        # el analisis + sintesis es el de error_reconstruccion; la escala
        # es la que esa misma funcion usa para comparar (el banco QMF
        # clasico tiene ganancia 2).
        def _reconstruir(banco):
            h0, h1, g0, g1 = banco
            v0 = diezmar(convolucion(X_B, h0), 2)
            v1 = diezmar(convolucion(X_B, h1), 2)
            y = (convolucion(interpolar_ceros(v0, 2), g0)
                 + convolucion(interpolar_ceros(v1, 2), g1))
            ret = len(h0) - 1
            n = len(X_B) - ret
            a, b = X_B[:n], y[ret:ret + n]
            return b * float(np.dot(a, b) / np.dot(b, b))

        rec_par = _reconstruir(BANCO_QMF)
        rec_impar = _reconstruir(banco_qmf(H_IMPAR))
        rango = (-1.95, 1.95)
        sec_r = Secuencia(rec_par[:64], 0, rango, ancho=9.6, alto=2.9,
                          color=C_SALIDA, radio=0.038)
        sec_r.move_to(DOWN * 0.10)
        curva_x = sec_r.curva_de(np.arange(64), X_B[:64], color=C_MUESTRA,
                                 grosor=2.4)
        et_ent = tag_hud("x[n]", font_size=19, color=C_MUESTRA)
        et_ent.next_to(sec_r, UP, buff=0.14).align_to(sec_r, LEFT)
        et_rec = tag_hud("reconstruida", font_size=19, color=C_SALIDA)
        et_rec.next_to(sec_r, UP, buff=0.14).align_to(sec_r, RIGHT)

        self.play(Create(curva_x), FadeIn(et_ent), run_time=1.0)
        self.play(FadeIn(sec_r), FadeIn(et_rec), run_time=0.9)
        rot.mostrar(cifra_pie(f"{TAPS_QMF} taps: {ERR_QMF:.2e}"),
                    zona="abajo", run_time=0.45)
        self.wait(3.0)

        # --- la paridad: 31 taps y el banco deja de cuadrar ---------------
        self.play(Transform(sec_r, sec_r.con_valores(rec_impar[:64],
                                                     color=C_RUIDO)),
                  Transform(et_rec, tag_hud("reconstruida", font_size=19,
                                            color=C_RUIDO)
                            .move_to(et_rec.get_center())),
                  run_time=1.4)
        rot.mostrar(cifra_pie(f"{len(H_IMPAR)} taps: {fmt(ERR_IMPAR, 3)}"),
                    zona="abajo", run_time=0.45)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"x{RAZON_PARIDAD:.0f} peor"), zona="abajo",
                    run_time=0.45)
        self.wait(3.2)

        cierre_leccion(self, rot, "Partir en bandas y volver a juntarlas",
                       "solo cuadra si los filtros encajan.",
                       sec_r, curva_x, et_ent, et_rec)

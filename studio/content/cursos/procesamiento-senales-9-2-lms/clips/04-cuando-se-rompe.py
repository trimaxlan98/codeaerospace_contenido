class Clip4(Scene):
    """9.2.4 - El limite: por encima de mu_max el lazo se realimenta a si
    mismo y el error se va al infinito. (~35 s)"""

    N_VER = 200          # muestras dibujadas de cada error
    N_ENV = 800          # ventana de la envolvente en dB
    K_ENV = 32           # suavizado de la envolvente

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("Cuando se rompe"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        rot.mostrar(formula_pie(r"\mu < \frac{2}{L\,P_x}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)
        rot.mostrar(cifra_pie(f"mu max {fmt(MU_MAX, 4)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        # --- los dos errores, en la MISMA escala -------------------------
        n = self.N_VER
        y_e = (-3.0, 3.0)
        bueno = Secuencia(E_LMS[MU_DEMO][:n], 0, y_e, ancho=8.0, alto=1.55,
                          color=C_SALIDA, radio=0.017, grosor=1.6,
                          eje_y=False)
        bueno.move_to(UP * 1.85 + RIGHT * 0.15)
        et_b = tag_hud(f"mu {fmt(MU_DEMO, 3)}", font_size=19, color=C_SALIDA)
        et_b.next_to(bueno, LEFT, buff=0.26)
        v_b = tag_hud(f"medio {fmt(E_BUENO_200, 2)}", font_size=18,
                      color=C_CALCULO)
        v_b.next_to(bueno, UP, buff=0.16)
        self.play(FadeIn(bueno), FadeIn(et_b), FadeIn(v_b), run_time=0.9)
        self.wait(1.8)

        # el malo se sale de la caja: los tallos topan con el borde, que es
        # exactamente lo que pasa (max 4486 en estas 200 muestras).
        malo = bueno.con_valores(E_MALO[:n], color=C_RUIDO)
        malo.move_to(DOWN * 0.55 + RIGHT * 0.15)
        et_m = tag_hud(f"mu {fmt(MU_MALO, 3)}", font_size=19, color=C_RUIDO)
        et_m.next_to(malo, LEFT, buff=0.26)
        v_m = tag_hud(f"medio {fmt(E_MALO_200, 0)}", font_size=18,
                      color=C_CALCULO)
        v_m.next_to(malo, DOWN, buff=0.16)
        self.play(FadeIn(malo), FadeIn(et_m), FadeIn(v_m), run_time=1.0)
        self.wait(2.4)

        panel = panel_cifras((f"mu max {fmt(MU_MAX, 4)}", C_DATO),
                             (f"bueno {fmt(E_BUENO_200, 2)}", C_SALIDA),
                             (f"malo {fmt(E_MALO_200, 0)}", C_RUIDO),
                             desplazar=DOWN * 2.30)
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)

        # --- y no para: la envolvente en dB ------------------------------
        self.play(FadeOut(bueno), FadeOut(et_b), FadeOut(v_b),
                  FadeOut(malo), FadeOut(et_m), FadeOut(v_m),
                  FadeOut(panel), run_time=0.7)

        k, ne = self.K_ENV, self.N_ENV
        nucleo = np.ones(k) / k

        def env_db(e):
            s = np.convolve(np.abs(np.asarray(e, float))[:ne], nucleo,
                            mode="valid")
            return 20.0 * np.log10(np.maximum(s, 1e-12))

        db_b, db_m = env_db(E_LMS[MU_DEMO]), env_db(E_MALO)
        w = np.arange(len(db_b), dtype=float)
        techo = float(np.ceil(db_m.max() / 20.0) * 20.0)
        rf = respuesta_dibujo(w, db_b, ancho=8.4, alto=3.6, piso_db=-20.0,
                              techo_db=techo, color=C_SALIDA)
        rf.move_to(LEFT * 1.30 + UP * 0.25)
        et_y = tag_hud("error en dB", font_size=18, color=C_DATO)
        et_y.next_to(rf.en(w[0], techo), UR, buff=0.10)
        et_x = tag_hud(f"{ne} muestras", font_size=18, color=C_DATO)
        et_x.next_to(rf.en(w[-1], -20.0), DOWN, buff=0.20)
        # el eje vertical va rotulado: sin las dos marcas, "dB" no dice
        # cuanto ha subido la curva roja.
        marcas_y = VGroup()
        for v in (techo, 0.0):
            p = rf.en(w[0], v)
            marcas_y.add(Line(p, p + LEFT * 0.13, color=C_EJE,
                              stroke_width=1.6))
            t = tag_hud(fmt(v, 0), font_size=17, color=C_DATO)
            t.next_to(p + LEFT * 0.13, LEFT, buff=0.07)
            marcas_y.add(t)
        self.play(FadeIn(rf.ejes), FadeIn(marcas_y), FadeIn(et_y),
                  FadeIn(et_x), run_time=0.6)
        t_b = tag_hud(f"mu {fmt(MU_DEMO, 3)}", font_size=19, color=C_SALIDA)
        t_b.next_to(rf.en(w[-1], float(db_b[-1])), RIGHT, buff=0.16)
        self.play(Create(rf.curva), FadeIn(t_b), run_time=1.4)
        self.wait(1.6)

        cur_m = rf.con_mag(db_m, C_RUIDO).curva
        t_m = tag_hud(f"mu {fmt(MU_MALO, 3)}", font_size=19, color=C_RUIDO)
        t_m.next_to(rf.en(w[-1], float(db_m[-1])), RIGHT, buff=0.16)
        self.play(Create(cur_m), FadeIn(t_m), run_time=1.8)
        self.wait(2.4)

        rot.mostrar(cifra_pie(f"{ne} muestras {fmt(db_m[-1], 0)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)

        cierre_leccion(self, rot, "No hace falta conocer el ruido.",
                       "Basta con oirlo aparte.",
                       rf, cur_m, t_b, t_m, et_y, et_x, marcas_y)

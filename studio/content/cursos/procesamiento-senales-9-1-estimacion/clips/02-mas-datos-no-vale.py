class Clip2(Scene):
    """9.1.2 - La sorpresa: cuadruplicar las muestras no calma el piso.
    El periodograma NO converge. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("Mas datos no bastan"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        piso = -25.0
        db4 = a_db(periodograma(ruido_blanco(N_E, 1.0, 7), FS_E)[1])
        f4 = periodograma(ruido_blanco(N_E, 1.0, 7), FS_E)[0]
        rf = respuesta_dibujo(f4, db4, ancho=10.2, alto=2.3, piso_db=piso,
                              techo_db=12.0, color=C_BANDA)
        rf.move_to(UP * 1.35)
        et_1 = tag_hud(f"N = {N_E}", font_size=19, color=C_BANDA)
        et_1.next_to(rf, LEFT, buff=0.24)
        self.play(FadeIn(rf), FadeIn(et_1), run_time=1.0)
        rot.mostrar(cifra_pie(f"dispersion {fmt(DISP_PER, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- cuatro veces mas muestras ------------------------------------
        rf2 = respuesta_dibujo(F_LARGO, a_db(P_LARGO), ancho=10.2, alto=2.3,
                               piso_db=piso, techo_db=12.0, color=C_RUIDO)
        rf2.move_to(DOWN * 1.65)
        et_2 = tag_hud(f"N = {N_LARGO}", font_size=19, color=C_RUIDO)
        et_2.next_to(rf2, LEFT, buff=0.24)
        self.play(FadeIn(rf2), FadeIn(et_2), run_time=1.2)
        self.wait(2.2)
        rot.mostrar(cifra_pie(f"dispersion {fmt(DISP_LARGO, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        panel = panel_cifras((f"{N_E}: {fmt(DISP_PER, 2)} dB", C_BANDA),
                             (f"{N_LARGO}: {fmt(DISP_LARGO, 2)} dB", C_RUIDO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.2)
        rot.mostrar(cifra_pie("cuatro veces mas datos"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)
        rot.mostrar(cifra_pie("el mismo temblor"), zona="abajo",
                    run_time=0.5)
        self.wait(8.2)

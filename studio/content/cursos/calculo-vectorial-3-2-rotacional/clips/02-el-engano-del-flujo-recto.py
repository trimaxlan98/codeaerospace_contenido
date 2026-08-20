class Clip2(Scene):
    """3.2.2 - En la cizalla F=(y,0) todo el campo es horizontal, y aun
    asi la ruedecita gira: arriba del eje el campo empuja mas fuerte que
    abajo, y ese desnivel es el giro. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El engaño del flujo recto")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: un campo perfectamente horizontal --------------------
        pl = plano_leccion()
        campo = campo_flechas(pl, CAMPO_CIZALLA)
        self.play(FadeIn(pl), run_time=0.7)
        rot.mostrar(pie_curso("Este campo es puro flujo horizontal: cada "
                              "flecha mira a la derecha o a la izquierda, "
                              "nunca sube ni baja."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(campo), run_time=1.0)
        self.wait(3.4)

        # --- momento: la misma ruedecita, y gira -----------------------------
        rot.mostrar(pie_curso("Soltemos la misma ruedecita aquí. Nada "
                              "sube ni baja... ¿girará?"), zona="abajo",
                    run_time=0.5)
        rd = rueda(pl, P_RUEDA_CIZALLA)
        self.play(FadeIn(rd, scale=0.6), run_time=0.6)
        self.wait(1.4)
        self.play(Rotate(rd.aspas, angle=VEL_CIZALLA * 4.0,
                         about_point=rd.centro()), run_time=4.0,
                  rate_func=linear)
        self.wait(1.0)

        # --- momento: arriba empuja mas que abajo -----------------------------
        rot.mostrar(pie_curso("¡Gira, y al revés que antes! Miremos justo "
                              "arriba y abajo de su eje."), zona="abajo",
                    run_time=0.5)
        x0 = P_RUEDA_CIZALLA[0]
        f_arriba = flecha_libre(
            pl, (x0, Y_ARRIBA_CIZALLA),
            (x0 + F_ARRIBA_CIZALLA, Y_ARRIBA_CIZALLA), color=C_CAMPO,
            grosor=5.0)
        t_arriba = tag_hud(f"Fx = {fmt(F_ARRIBA_CIZALLA)}", font_size=17,
                           color=C_CAMPO)
        t_arriba.next_to(f_arriba, UP, buff=0.1)
        f_abajo = flecha_libre(
            pl, (x0, Y_ABAJO_CIZALLA),
            (x0 + F_ABAJO_CIZALLA, Y_ABAJO_CIZALLA), color=C_CAMPO,
            grosor=5.0)
        t_abajo = tag_hud(f"Fx = {fmt(F_ABAJO_CIZALLA)}", font_size=17,
                          color=C_CAMPO)
        t_abajo.next_to(f_abajo, DOWN, buff=0.1)
        self.play(FadeIn(f_arriba, shift=0.1 * UP), FadeIn(t_arriba),
                  run_time=0.7)
        self.play(FadeIn(f_abajo, shift=0.1 * DOWN), FadeIn(t_abajo),
                  run_time=0.7)
        self.wait(3.2)

        rot.mostrar(pie_curso("Arriba empuja fuerte, abajo casi nada: ese "
                              "desnivel es lo que hace girar la rueda, en "
                              "sentido horario."), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)

        # --- momento: la cifra --------------------------------------------------
        rot.mostrar(pie_curso("Sí que gira, aunque el flujo vaya recto: "
                              "el rotacional también existe aquí."),
                    zona="abajo", run_time=0.5)
        cifra_rot = tag_hud(f"rot F = {fmt(ROT_CIZALLA)}", font_size=19,
                            color=C_RES)
        panel = panel_derecha(cifra_rot, buff=0.16)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.play(Rotate(rd.aspas, angle=VEL_CIZALLA * 3.0,
                         about_point=rd.centro()), run_time=3.0,
                  rate_func=linear)
        self.wait(3.0)

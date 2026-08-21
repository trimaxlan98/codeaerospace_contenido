class Clip1(Scene):
    """3.2.1 - Una ruedecita de paletas soltada en el rotor puro gira sin
    parar: su velocidad fisica de giro es rot/2, medida por la libreria.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La ruedecita")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el campo, lleno de remolino -------------------------
        pl = plano_leccion()
        campo = campo_flechas(pl, CAMPO_ROTOR)
        self.play(FadeIn(pl), run_time=0.7)
        rot.mostrar(pie_curso("Este campo gira en torno al origen: cada "
                              "flecha rodea el centro."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(campo), run_time=1.0)
        self.wait(3.4)

        # --- momento: soltamos la ruedecita --------------------------------
        rot.mostrar(pie_curso("Soltemos aquí una ruedecita de paletas: "
                              "libre de girar sobre su eje."), zona="abajo",
                    run_time=0.5)
        rd = rueda(pl, P_RUEDA_ROTOR)
        self.play(FadeIn(rd, scale=0.6), run_time=0.6)
        self.wait(3.0)

        # --- momento: gira, y no para ---------------------------------------
        rot.mostrar(pie_curso("Y gira: el campo la arrastra sin parar, "
                              "siempre en el mismo sentido."), zona="abajo",
                    run_time=0.5)
        self.play(Rotate(rd.aspas, angle=VEL_ROTOR * 4.0,
                         about_point=rd.centro()), run_time=4.0,
                  rate_func=linear)
        self.wait(1.8)

        # --- momento: la cifra del giro ---------------------------------------
        rot.mostrar(pie_curso("Esa velocidad de giro no es un capricho: "
                              "es la mitad del rotacional del campo."),
                    zona="abajo", run_time=0.5)
        cifra_rot = tag_hud(f"rot F = {fmt(ROT_ROTOR)}", font_size=19,
                            color=C_RES)
        cifra_vel = tag_hud(f"giro = rot/2 = {fmt(VEL_ROTOR)} rad/s",
                            font_size=19, color=C_RES)
        panel = panel_derecha(cifra_rot, cifra_vel, buff=0.16)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.play(Rotate(rd.aspas, angle=VEL_ROTOR * 3.0,
                         about_point=rd.centro()), run_time=3.0,
                  rate_func=linear)
        self.wait(2.8)

        rot.mostrar(pie_curso("A esta ruedecita la llamamos el "
                              "rotacional: mide el remolino local."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

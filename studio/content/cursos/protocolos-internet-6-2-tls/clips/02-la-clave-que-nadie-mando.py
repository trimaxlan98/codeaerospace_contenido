class Clip2(Scene):
    """6.2.2 - La clave que nadie mando (dh_pequeno): los dos llegan al
    MISMO numero sin que ese numero cruce nunca el cable. El curso 19 ya
    explico la matematica; aqui se ensena el gesto. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        rot.mostrar(titulo_curso("La clave que nadie mando"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        X, Y = 4.3, 1.20
        n_cli = nodo("host", tam=0.60).move_to(LEFT * X + UP * Y)
        n_srv = nodo("servidor", tam=0.60).move_to(RIGHT * X + UP * Y)
        cable = enlace(LEFT * X + UP * Y, RIGHT * X + UP * Y, buff=0.62)
        t_cli = tag_hud("cliente", font_size=17, color=C_RED)
        t_cli.move_to(LEFT * X + UP * 1.90)
        t_srv = tag_hud("servidor", font_size=17, color=C_RED)
        t_srv.move_to(RIGHT * X + UP * 1.90)

        publico = tag_hud("publico, a la vista de todos:   p = %d    g = %d"
                          % (DH_P, DH_G), font_size=18, color=C_EJE)
        publico.move_to(UP * 2.58)

        # --- momento: los dos empiezan sin nada en comun ------------------
        rot.mostrar(pie_curso("Cliente y sitio no comparten nada previo: "
                              "solo lo que digan en voz alta."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(n_cli), FadeIn(n_srv), FadeIn(t_cli), FadeIn(t_srv),
                  Create(cable), run_time=0.9)
        self.play(FadeIn(publico), run_time=0.5)
        self.wait(3.0)

        # --- momento: el numero privado de cada uno -----------------------
        rot.mostrar(pie_curso("Cada uno elige un numero privado que no "
                              "sale nunca de su maquina."),
                    zona="abajo", run_time=0.5)

        def privado(x, valor):
            a = tag_hud("privado: %d" % valor, font_size=19, color=C_CLAVE)
            a.move_to(RIGHT * x + UP * 0.10)
            b = tag_hud("no sale de aqui", font_size=16, color=C_CLAVE)
            b.set_opacity(0.80)
            b.move_to(RIGHT * x + DOWN * 0.42)
            return VGroup(a, b)

        pr_c, pr_s = privado(-X, DH_A), privado(X, DH_B)
        self.play(FadeIn(pr_c, shift=0.12 * UP),
                  FadeIn(pr_s, shift=0.12 * UP), run_time=0.6)
        self.wait(3.6)

        # --- momento: lo que si cruza el cable ----------------------------
        rot.mostrar(pie_curso("Cada uno grita un numero derivado del suyo. "
                              "El espia los oye enteros."),
                    zona="abajo", run_time=0.5)
        pincho = DashedLine(UP * Y, UP * 0.64, color=C_PERDIDA,
                            stroke_width=2.0, dash_length=0.10)
        n_esp = nodo("host", tam=0.36, color=C_PERDIDA).move_to(UP * 0.36)
        t_esp = tag_hud("espia", font_size=16, color=C_PERDIDA)
        t_esp.move_to(DOWN * 0.06)
        self.play(Create(pincho), FadeIn(n_esp), FadeIn(t_esp), run_time=0.5)

        f_c = ficha(str(DH_PUB_C), lado=0.80, fs=17)
        f_c.move_to(LEFT * 3.15 + UP * (Y + 0.45))
        f_s = ficha(str(DH_PUB_S), lado=0.80, fs=17)
        f_s.move_to(RIGHT * 3.15 + UP * (Y - 0.45))
        self.play(FadeIn(f_c), FadeIn(f_s), run_time=0.4)
        self.play(f_c.animate.move_to(RIGHT * 3.15 + UP * (Y + 0.45)),
                  f_s.animate.move_to(LEFT * 3.15 + UP * (Y - 0.45)),
                  run_time=1.4)
        oye = tag_hud("el espia oyo:  %d, %d, %d, %d" % DH_EN_EL_CABLE,
                      font_size=18, color=C_PERDIDA)
        oye.move_to(DOWN * 1.92)
        self.play(FadeIn(oye), run_time=0.5)
        self.wait(2.8)

        # --- momento: los dos aterrizan en el MISMO numero ----------------
        rot.mostrar(pie_curso("Mezclando lo que oyo con lo que nunca dijo, "
                              "cada lado llega al mismo numero."),
                    zona="abajo", run_time=0.5)

        def clave(x):
            t = tag_hud("clave = %d" % DH_SECRETO, font_size=21,
                        color=C_CIFRA)
            t.move_to(RIGHT * x + DOWN * 0.95)
            caja = SurroundingRectangle(t, color=C_CIFRA, buff=0.15,
                                        stroke_width=2.2)
            return VGroup(caja, t)

        cl_c, cl_s = clave(-X), clave(X)
        self.play(FadeIn(cl_c, shift=0.12 * UP),
                  FadeIn(cl_s, shift=0.12 * UP), run_time=0.7)
        igual = tag_hud("el mismo numero", font_size=18, color=C_OK)
        igual.move_to(DOWN * 0.95)
        self.play(FadeIn(igual), run_time=0.4)
        self.wait(3.6)

        # --- momento: y ese numero no viajo -------------------------------
        rot.mostrar(pie_curso("Ese numero es la clave del canal, y es el "
                              "unico que no viajo por el cable."),
                    zona="abajo", run_time=0.5)
        nunca = tag_hud("nunca viajaron:  %d, %d, %d" % DH_EN_CASA,
                        font_size=18, color=C_OK)
        nunca.move_to(DOWN * 2.42)
        self.play(FadeIn(nunca), run_time=0.5)
        self.play(Indicate(cl_c, color=C_CIFRA, scale_factor=1.10),
                  Indicate(cl_s, color=C_CIFRA, scale_factor=1.10),
                  run_time=0.8)
        self.wait(4.2)

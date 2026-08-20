class Clip1(Scene):
    """1.3.1 - Las dos parciales de un punto, puestas una tras otra, son
    las componentes de un vector: el gradiente. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Dos números, una flecha")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el punto y sus dos pendientes -----------------------
        pl = plano_leccion()
        mapa = curvas_nivel(pl, PAISAJE, niveles=NIVELES, n=100,
                            opacidad=0.35)
        self.play(FadeIn(pl), FadeIn(mapa), run_time=0.9)
        rot.mostrar(pie_curso("Volvemos al mapa. En este punto ya medimos "
                              "dos pendientes, una por cada eje."),
                    zona="abajo", run_time=0.5)
        dot = Dot(pl.p(P_G), radius=0.085, color=C_VEC)
        self.play(FadeIn(dot, scale=0.4), run_time=0.5)
        panel = panel_derecha(
            MathTex(r"\frac{\partial f}{\partial x} = " + fmt(GX, 2),
                    font_size=32, color=C_CIFRA),
            MathTex(r"\frac{\partial f}{\partial y} = " + fmt(GY, 2),
                    font_size=32, color=C_CIFRA), buff=0.26)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.8)

        # --- momento: las dos pendientes, una tras otra -------------------
        rot.mostrar(pie_curso("La de x empuja a la derecha; la de y, hacia "
                              "arriba. Pongámoslas una tras otra."),
                    zona="abajo", run_time=0.5)
        q1 = P_G + np.array([GX * ESC_GRAD, 0.0])
        q2 = P_G + G * ESC_GRAD
        fx = flecha_libre(pl, P_G, q1, color=C_CIFRA, grosor=4.0)
        fy = flecha_libre(pl, q1, q2, color=C_CIFRA, grosor=4.0)
        tx = tag_hud(fmt(GX, 2), font_size=20)
        tx.next_to(fx, DOWN, buff=0.16)
        ty = tag_hud(fmt(GY, 2), font_size=20)
        ty.next_to(fy, RIGHT, buff=0.16)
        self.play(GrowArrow(fx), run_time=0.7)
        self.play(FadeIn(tx), run_time=0.3)
        self.play(GrowArrow(fy), run_time=0.7)
        self.play(FadeIn(ty), run_time=0.3)
        self.wait(3.6)

        # --- momento: la flecha que cierra el paso -------------------------
        rot.mostrar(pie_curso("El paso que las junta es una flecha sola: "
                              "ya no son dos números sueltos."),
                    zona="abajo", run_time=0.5)
        gr = flecha_libre(pl, P_G, q2, color=C_GRAD, grosor=5.5,
                          punta_len=0.26)
        tg = tag_hud(f"largo = {fmt(G_MOD, 2)}", font_size=20, color=C_GRAD)
        tg.next_to(pl.p(q2), UL, buff=0.14)
        self.play(GrowArrow(gr), run_time=0.9)
        self.play(FadeIn(tg), run_time=0.4)
        self.wait(3.6)

        # --- momento: su nombre y su formula -------------------------------
        rot.mostrar(formula_pie(r"\nabla f = \left(\frac{\partial f}"
                                r"{\partial x},\ \frac{\partial f}"
                                r"{\partial y}\right)"),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(gr, color=C_GRAD, scale_factor=1.05),
                  run_time=0.8)
        self.wait(4.4)

        rot.mostrar(pie_curso("Se llama gradiente. Y esa flecha, sin que se "
                              "lo pidamos, ya apunta a alguna parte."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(VGroup(dot, gr), color=C_GRAD,
                           scale_factor=1.03), run_time=0.9)
        self.wait(4.2)

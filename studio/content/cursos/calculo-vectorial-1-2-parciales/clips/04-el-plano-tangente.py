class Clip4(Scene):
    """1.2.4 - Cerca de P0 la superficie real y el plano tangente casi
    coinciden; lejos, el plano se despega. Cierre de la leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El plano tangente")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: las dos pendientes arman un plano -----------------------
        esp = espacio_leccion()
        d = 1.0
        sup_cerca = superficie3(esp, PAISAJE, x0=X0 - d, x1=X0 + d,
                                y0=Y0 - d, y1=Y0 + d, n=11)
        self.play(FadeIn(esp), FadeIn(sup_cerca), run_time=1.0)
        rot.mostrar(pie_curso("Las dos pendientes, juntas, arman un "
                              "plano: el plano tangente en P0."),
                    zona="abajo", run_time=0.5)
        p0dot = Dot(esp.p(X0, Y0, F0), radius=0.07, color=C_VEC)
        self.play(FadeIn(p0dot, scale=0.4), run_time=0.5)
        self.wait(2.6)

        # --- momento: cerca, casi no se distinguen ------------------------------
        rot.mostrar(pie_curso("Cerca de P0, el plano y la superficie "
                              "casi no se distinguen."), zona="abajo",
                    run_time=0.5)
        tan_cerca = superficie3(esp, plano_tangente, x0=X0 - d, x1=X0 + d,
                                y0=Y0 - d, y1=Y0 + d, n=11, opacidad=0.6)
        self.play(FadeIn(tan_cerca), run_time=1.2)
        cifra_cerca = tag_hud(f"error = {fmt(ERROR_CERCA, 3)}",
                              font_size=18, color=C_RES)
        cifra_cerca.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(cifra_cerca), run_time=0.5)
        self.wait(3.4)

        # --- momento: lejos, el plano se despega --------------------------------
        rot.mostrar(pie_curso("Lejos de P0, en cambio, el plano se "
                              "despega del paisaje real."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(sup_cerca), FadeOut(tan_cerca),
                  FadeOut(cifra_cerca), run_time=0.6)
        sup_lejos = superficie3(esp, PAISAJE, n=15)
        tan_lejos = superficie3(esp, plano_tangente, n=15, opacidad=0.5)
        self.play(FadeIn(sup_lejos), FadeIn(tan_lejos), run_time=1.2)
        self.wait(1.6)

        real_lejos = Dot(esp.p(P_LEJOS[0], P_LEJOS[1],
                               float(PAISAJE(P_LEJOS))), radius=0.07,
                        color=C_VEC)
        aprox_lejos = Dot(esp.p(P_LEJOS[0], P_LEJOS[1],
                                plano_tangente(P_LEJOS)), radius=0.07,
                         color=C_GRAD)
        self.play(FadeIn(real_lejos, scale=0.4),
                  FadeIn(aprox_lejos, scale=0.4), run_time=0.6)
        brecha = DashedLine(real_lejos.get_center(), aprox_lejos.get_center(),
                            color=C_RES, stroke_width=2.4, dash_length=0.08)
        cifra_lejos = tag_hud(f"error = {fmt(ERROR_LEJOS, 2)}",
                              font_size=18, color=C_RES)
        cifra_lejos.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(Create(brecha), FadeIn(cifra_lejos), run_time=0.8)
        self.wait(3.2)

        rot.mostrar(pie_curso("El plano tangente es la MEJOR "
                              "aproximación lineal, solo cerca del "
                              "punto."), zona="abajo", run_time=0.5)
        self.wait(3.8)

        # --- cierre -------------------------------------------------------------
        cierre_leccion(self, rot,
                       "Derivar en 2D es cortar.",
                       "Dos cortes bastan.",
                       "Siguiente lección: el gradiente, la flecha que sube.",
                       esp, sup_lejos, tan_lejos, p0dot, real_lejos,
                       aprox_lejos, brecha, cifra_lejos)

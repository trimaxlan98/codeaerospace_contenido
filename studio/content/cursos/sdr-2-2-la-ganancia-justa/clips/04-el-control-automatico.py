class Clip4(Scene):
    """2.2.4 - El AGC sostiene una senal que se desvanece 30.7 dB (entrada,
    parametro elegido) y la deja en una franja de apenas 3.0 dB medidos
    tras enganchar. Cierre de la leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El control automatico"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- cuadro propio (a mano, con Lines): tiempo vs nivel ------------
        N = len(ENV)
        Y_LO = float(np.floor(min(ENV.min(), SAL.min())) - 2.0)
        Y_HI = float(np.ceil(max(ENV.max(), SAL.max())) + 2.0)
        ANCHO, ALTO = 10.8, 4.0
        ORIGEN = UP * 0.15

        def xy(i, v):
            fx = i / (N - 1)
            fy = (min(max(v, Y_LO), Y_HI) - Y_LO) / (Y_HI - Y_LO)
            return ORIGEN + np.array([(fx - 0.5) * ANCHO,
                                      (fy - 0.5) * ALTO, 0.0])

        esq = [xy(0, Y_LO), xy(N - 1, Y_LO), xy(N - 1, Y_HI), xy(0, Y_HI)]
        marco = VGroup(*[Line(esq[i], esq[(i + 1) % 4], color=S.C_EJE,
                              stroke_width=1.6) for i in range(4)])
        t_x = tag_junto(marco[0], "tiempo", DOWN, buff=0.22, font_size=19)
        t_y = tag_junto(marco[3], "dB", LEFT, buff=0.22, font_size=19)

        self.play(Create(marco), FadeIn(t_x), FadeIn(t_y), run_time=0.9)
        self.wait(0.6)

        # --- la envolvente que se desvanece (parametro elegido, gris) -----
        curva_env = VMobject(stroke_color=C_SENAL, stroke_width=2.4)
        curva_env.set_points_as_corners([xy(i, ENV[i]) for i in range(N)])
        t_env = tag_junto(curva_env, "entrada", UP, buff=0.18, font_size=19,
                          color=C_SENAL)
        t_env.move_to(xy(40, Y_HI - 1.0))

        self.play(Create(curva_env), run_time=2.2)
        self.play(FadeIn(t_env), run_time=0.5)
        self.wait(0.6)
        rot.mostrar(dato_pie(f"entrada {fmt(VAR_ENT, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        # --- la salida del AGC: una franja angosta -------------------------
        curva_sal = VMobject(stroke_color=C_OK, stroke_width=2.8)
        curva_sal.set_points_as_corners([xy(i, SAL[i]) for i in range(N)])
        t_sal = tag_junto(curva_sal, "salida", DOWN, buff=0.18, font_size=19,
                          color=C_OK)
        t_sal.move_to(xy(N - 60, Y_LO + 2.0))

        self.play(Create(curva_sal), run_time=2.2)
        self.play(FadeIn(t_sal), run_time=0.5)
        self.wait(1.2)

        # --- la ventana donde se mide la variacion de salida ---------------
        i0 = 150
        banda = Rectangle(width=abs(xy(N - 1, 0)[0] - xy(i0, 0)[0]),
                          height=ALTO, stroke_width=0, fill_color=C_CALCULO,
                          fill_opacity=0.12)
        banda.move_to((xy(i0, Y_LO) + xy(N - 1, Y_HI)) / 2)
        t_banda = tag_junto(banda, "medido aqui", UP, buff=0.18,
                            font_size=18, color=C_CALCULO)
        t_banda.move_to(xy((i0 + N - 1) / 2, Y_HI - 1.6))

        self.play(FadeIn(banda), FadeIn(t_banda), run_time=0.8)
        self.wait(1.4)

        rot.mostrar(cifra_pie(f"salida {fmt(VAR_SAL, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)

        cierre_leccion(self, rot, "Ni tanta que recorte,",
                       "ni tan poca que se hunda.", marco, t_x, t_y,
                       curva_env, t_env, curva_sal, t_sal, banda, t_banda,
                       espera=6.5)

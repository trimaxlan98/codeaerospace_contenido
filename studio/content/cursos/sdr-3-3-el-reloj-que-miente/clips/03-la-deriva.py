class Clip3(Scene):
    """3.3.3 - La deriva: un waterfall de 10 minutos (2.2 ppm a 437 MHz,
    parametros) donde la traza se inclina al calentarse el cristal; la
    deriva medida fila a fila llega a 926 Hz. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La deriva"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        ANCHO_WF, ALTO_WF = 10.4, 4.9
        FS_KHZ = 24.0
        T_MAX = float(T_WF[-1])
        F0_KHZ = -6.0

        img = S.waterfall(WF, ancho=ANCHO_WF, alto=ALTO_WF, piso=-40.0,
                          techo=0.0)
        img.move_to(UP * 0.02)

        def x_de(khz):
            return img.get_left()[0] + (khz + FS_KHZ) / (2 * FS_KHZ) * ANCHO_WF

        def y_de(minuto):
            return img.get_top()[1] - minuto / T_MAX * ALTO_WF

        marco = Rectangle(width=ANCHO_WF, height=ALTO_WF, stroke_color=C_EJE,
                          stroke_width=1.8, fill_opacity=0.0)
        marco.move_to(img.get_center())

        ticks_x = VGroup()
        for khz, txt in zip([-24, -12, 0, 12, 24],
                            ["-24", "-12", "0", "12", "24"]):
            xp = x_de(khz)
            yb = img.get_bottom()[1]
            t = Line(np.array([xp, yb, 0.0]), np.array([xp, yb - 0.1, 0.0]),
                     color=C_EJE, stroke_width=1.6)
            lbl = tag_hud(txt, font_size=16, color=C_TENUE)
            lbl.next_to(t, DOWN, buff=0.08)
            ticks_x.add(t, lbl)
        u_x = tag_junto(ticks_x[-1], "kHz", RIGHT, buff=0.14, font_size=18)

        ticks_y = VGroup()
        for m in [0, 5, 10]:
            yp = y_de(m)
            xl = img.get_left()[0]
            t = Line(np.array([xl - 0.1, yp, 0.0]), np.array([xl, yp, 0.0]),
                     color=C_EJE, stroke_width=1.6)
            lbl = tag_hud(str(m), font_size=16, color=C_TENUE)
            lbl.next_to(t, LEFT, buff=0.08)
            ticks_y.add(t, lbl)
        u_y = tag_junto(ticks_y[0], "min", UP, buff=0.14, font_size=18)

        panel = panel_cifras(("437 MHz", C_DATO), ("2.2 ppm", C_DATO))

        self.play(FadeIn(img), Create(marco), run_time=1.0)
        self.play(FadeIn(ticks_x), FadeIn(u_x), FadeIn(ticks_y), FadeIn(u_y),
                  FadeIn(panel), run_time=0.9)
        self.wait(5.5)

        # --- la traza medida, fila a fila -----------------------------------
        pts = [np.array([x_de(F0_KHZ + DERIVA_MED[k] / 1e3), y_de(T_WF[k]),
                        0.0]) for k in range(len(T_WF))]
        traza = VMobject(stroke_color=C_CALCULO, stroke_width=2.4,
                         stroke_opacity=0.9)
        traza.set_points_smoothly(pts)
        punto = Dot(pts[-1], radius=0.07, color=C_CALCULO)
        self.play(Create(traza), run_time=2.4)
        self.play(FadeIn(punto, scale=1.4), run_time=0.5)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"{fmt(DERIVA_MED[-1], 0)} Hz en 10 min"),
                   zona="abajo", run_time=0.5)
        self.wait(16.0)

class Clip4(Scene):
    """10.1.4 - Por que una radio guarda DOS numeros por muestra: un fasor
    que gira en un sentido y su espejo que gira en el otro proyectan la
    MISMA parte real. Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("IQ"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        centro = UP * 0.75
        eje_re = Line(centro + LEFT * 1.9, centro + RIGHT * 1.9,
                     color=C_TENUE, stroke_width=1.3)
        eje_im = Line(centro + DOWN * 1.9, centro + UP * 1.9,
                     color=C_TENUE, stroke_width=1.3)
        et_re = tag_hud("Re", font_size=17, color=C_TENUE)
        et_re.next_to(eje_re, RIGHT, buff=0.10)
        et_im = tag_hud("Im", font_size=17, color=C_TENUE)
        et_im.next_to(eje_im, UP, buff=0.10)
        self.play(FadeIn(eje_re), FadeIn(eje_im), FadeIn(et_re), FadeIn(et_im),
                  run_time=0.5)
        self.wait(0.4)

        # --- dos fasores, dos sentidos: RE_TONO/IM_TONO y su espejo ---------
        ESCALA = 1.6
        idx = np.arange(100, 181)
        pts_pos = [centro + ESCALA * np.array([RE_TONO[i], IM_TONO[i], 0.0])
                  for i in idx]
        pts_neg = [centro + ESCALA * np.array([RE_TONO[i], -IM_TONO[i], 0.0])
                  for i in idx]
        tray_pos = VMobject(color=C_CALCULO, stroke_width=1.2)
        tray_pos.set_points_smoothly(pts_pos)
        tray_neg = VMobject(color=C_IDEAL, stroke_width=1.2)
        tray_neg.set_points_smoothly(pts_neg)
        self.play(Create(tray_pos), Create(tray_neg), run_time=1.0)
        self.wait(0.5)

        punto_pos = Dot(pts_pos[0], radius=0.08, color=C_CALCULO)
        punto_neg = Dot(pts_neg[0], radius=0.08, color=C_IDEAL)
        et_pos = tag_hud(f"+{fmt(F_PORTADORA, 0)} Hz", font_size=16,
                         color=C_CALCULO)
        et_pos.next_to(punto_pos, UR, buff=0.12)
        et_neg = tag_hud(f"-{fmt(F_PORTADORA, 0)} Hz", font_size=16,
                         color=C_IDEAL)
        et_neg.next_to(punto_neg, DR, buff=0.12)
        self.play(FadeIn(punto_pos), FadeIn(punto_neg), FadeIn(et_pos),
                  FadeIn(et_neg), run_time=0.5)
        self.wait(0.4)

        # --- la proyeccion real, compartida por los dos ----------------------
        pista = Line(centro + DOWN * 2.55 + LEFT * 1.9,
                    centro + DOWN * 2.55 + RIGHT * 1.9, color=C_TENUE,
                    stroke_width=1.3)
        et_pista = tag_hud("Re x[n]", font_size=15, color=C_TENUE)
        et_pista.next_to(pista, DOWN, buff=0.12)
        proyeccion = Dot(radius=0.08, color=C_TITULO)
        proyeccion.move_to(np.array([pts_pos[0][0], pista.get_center()[1],
                                     0.0]))
        proyeccion.add_updater(lambda m: m.move_to(np.array(
            [punto_pos.get_center()[0], pista.get_center()[1], 0.0])))
        guia_pos = always_redraw(lambda: DashedLine(
            punto_pos.get_center(), proyeccion.get_center(), color=C_TENUE,
            stroke_width=1.1, dash_length=0.06))
        guia_neg = always_redraw(lambda: DashedLine(
            punto_neg.get_center(), proyeccion.get_center(), color=C_TENUE,
            stroke_width=1.1, dash_length=0.06))
        self.play(FadeIn(pista), FadeIn(et_pista), FadeIn(proyeccion),
                  FadeIn(guia_pos), FadeIn(guia_neg), run_time=0.6)
        self.wait(0.3)

        self.play(MoveAlongPath(punto_pos, tray_pos),
                  MoveAlongPath(punto_neg, tray_neg), run_time=6.0,
                  rate_func=linear)
        proyeccion.clear_updaters()
        guia_pos.clear_updaters()
        guia_neg.clear_updaters()
        rot.mostrar(cifra_pie("misma proyeccion real"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        rot.mostrar(formula_pie(r"\cos(\omega t) = \cos(-\omega t)"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        cierre_leccion(
            self, rot, "Una senal real esconde la mitad.",
            "La analitica la ensena.",
            eje_re, eje_im, et_re, et_im, tray_pos, tray_neg, punto_pos,
            punto_neg, et_pos, et_neg, pista, et_pista, proyeccion,
            guia_pos, guia_neg, espera=6.2)

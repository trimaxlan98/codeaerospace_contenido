class Clip4(Scene):
    """3.3.4 - La cadena entera del curso de un tiron, y el lazo que la
    cierra: el gemelo predice, la estacion mide, la diferencia reajusta
    el gemelo. Cierre de la leccion y del curso. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Gemelo y realidad"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # =================================================================
        # 1. La cadena entera del curso, eslabon a eslabon
        # =================================================================
        cad = cadena(etiquetas=("TLE", "pase", "Az/El", "lazo", "p95",
                                "dB"),
                     ancho_caja=1.30, alto_caja=0.62, buff=0.30,
                     font_size=17)
        cad.move_to(UP * 1.95)
        self.play(FadeIn(cad), run_time=0.9)
        self.wait(0.4)

        Y_ICO = 0.52

        def ico_tle():
            marco = RoundedRectangle(width=1.05, height=0.56,
                                     corner_radius=0.08, stroke_width=1.8,
                                     color=C_EJE)
            l1 = Line(LEFT * 0.38, RIGHT * 0.38, stroke_width=3.0,
                      color=C_CIELO)
            l2 = l1.copy()
            l1.shift(UP * 0.11)
            l2.shift(DOWN * 0.11)
            return VGroup(marco, l1, l2)

        def ico_pase():
            arco = Arc(radius=0.38, start_angle=0.0, angle=PI,
                       color=C_CIELO, stroke_width=3.0)
            suelo = Line(LEFT * 0.48, RIGHT * 0.48, stroke_width=2.2,
                         color=C_EJE)
            sat = Dot(arco.point_from_proportion(0.5), radius=0.055,
                      color=C_SAT)
            return VGroup(suelo, arco, sat)

        def ico_lazo():
            a = Arc(radius=0.30, start_angle=PI * 0.28, angle=PI * 1.5,
                    color=C_CALCULO, stroke_width=3.2)
            a.add_tip(tip_length=0.16)
            return VGroup(a)

        def ico_campana():
            alturas = (0.13, 0.31, 0.52, 0.29, 0.12)
            g = VGroup()
            for j, hh in enumerate(alturas):
                g.add(Rectangle(width=0.15, height=hh, stroke_width=0,
                                fill_color=C_SAT if j == 3 else C_TENUE,
                                fill_opacity=0.9))
            g.arrange(RIGHT, buff=0.05, aligned_edge=DOWN)
            return g

        def ico_haz():
            h = haz(TH3_S, error_deg=0.0, largo=0.90,
                    escala_ang=ESC_HAZ, color=C_OK)
            h.satelite.set_opacity(0.0)
            return h

        iconos = [ico_tle(), ico_pase(), montura(alto=0.85,
                                                 etiquetas=False),
                  ico_lazo(), ico_campana(), ico_haz()]
        for i, ic in enumerate(iconos):
            ic.move_to(np.array([cad.caja_en(i).get_center()[0], Y_ICO,
                                 0.0]))

        for i, ic in enumerate(iconos):
            # `encender` cambia el color al instante: es un corte, no una
            # animacion, y va JUSTO antes del play del icono que explica.
            cad.encender(i)
            self.play(FadeIn(ic, shift=0.18 * UP), run_time=0.55)
            self.wait(0.55)

        self.wait(0.4)
        rot.mostrar(cifra_pie(f"objetivo {fmt(OBJETIVO_DEG, 1)} grados"),
                    zona="abajo")
        self.wait(2.0)

        # =================================================================
        # 2. El lazo que no se cierra en el hardware, sino entre los dos
        # =================================================================
        rot.limpiar("abajo", run_time=0.35)
        self.play(FadeOut(cad), FadeOut(VGroup(*iconos)), run_time=0.8)

        def caja(texto, color, centro):
            r = RoundedRectangle(width=2.60, height=0.98,
                                 corner_radius=0.14, stroke_width=2.6,
                                 color=color)
            r.set_fill(color=color, opacity=0.10)
            r.move_to(centro)
            t = tag_hud(texto, font_size=22, color=color)
            t.move_to(centro)
            return VGroup(r, t)

        c_gem = caja("gemelo", C_CIELO, LEFT * 3.30 + UP * 0.80)
        c_est = caja("estacion", C_CALCULO, RIGHT * 3.30 + UP * 0.80)
        c_dif = caja("diferencia", C_SAT, DOWN * 1.55)
        self.play(FadeIn(c_gem), FadeIn(c_est), run_time=0.7)
        self.play(FadeIn(c_dif), run_time=0.5)

        # Las flechas se dibujan, pero el punto viaja por Lines aparte: una
        # Arrow lleva la punta como submobject y no es un camino limpio.
        tramos = [(c_gem[0].get_right() + RIGHT * 0.10,
                   c_est[0].get_left() + LEFT * 0.10),
                  (c_est[0].get_bottom() + DOWN * 0.08,
                   c_dif[0].get_right() + RIGHT * 0.08),
                  (c_dif[0].get_left() + LEFT * 0.08,
                   c_gem[0].get_bottom() + DOWN * 0.08)]
        colores = [C_CIELO, C_CALCULO, C_SAT]
        flechas = VGroup(*[
            Arrow(a, b, buff=0.0, color=col, stroke_width=3.6,
                  max_tip_length_to_length_ratio=0.09)
            for (a, b), col in zip(tramos, colores)])
        caminos = [Line(a, b) for a, b in tramos]

        # Los tres rotulos del lazo, en la MISMA fuente y tamano: uno en
        # Rajdhani 18 junto a dos en Space Mono 20 se leia como otra cosa.
        t_pred = tag_hud("predice", font_size=20, color=C_CIELO)
        t_pred.move_to(UP * 1.24)
        t_mide = tag_hud("mide", font_size=20, color=C_CALCULO)
        t_mide.move_to(RIGHT * 2.85 + DOWN * 0.72)
        t_reaj = tag_hud("reajusta", font_size=20, color=C_SAT)
        t_reaj.move_to(LEFT * 2.95 + DOWN * 0.78)

        self.play(LaggedStart(*[GrowArrow(f) for f in flechas],
                              lag_ratio=0.30), run_time=1.4)
        self.play(FadeIn(t_pred), FadeIn(t_mide), FadeIn(t_reaj),
                  run_time=0.6)
        self.wait(0.8)

        # dos vueltas al lazo: la correccion no es un paso, es un ciclo
        viajero = Dot(caminos[0].get_start(), radius=0.085,
                      color=C_CALCULO)
        self.play(FadeIn(viajero, scale=1.6), run_time=0.4)
        for _ in range(2):
            for cam, col in zip(caminos, colores):
                viajero.set_color(col)
                self.play(MoveAlongPath(viajero, cam), run_time=0.70,
                          rate_func=linear)
        self.play(FadeOut(viajero), run_time=0.4)

        rot.mostrar(cifra_pie(f"Ka {fmt(L_KA, 2)} dB", color=C_PELIGRO),
                    zona="abajo")
        self.wait(1.9)
        rot.mostrar(cifra_pie(f"margen {fmt(MARGEN_ENLACE, 1)} dB",
                              color=C_OK), zona="abajo")
        self.wait(1.9)

        panel = panel_cifras(f"S  {fmt(L_S, 3)} dB",
                             (f"Ka {fmt(L_KA, 2)} dB", C_PELIGRO),
                             (f"margen {fmt(MARGEN_ENLACE, 1)} dB", C_OK))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.2)

        # =================================================================
        # 3. El cierre de la leccion y del curso
        # =================================================================
        cierre_leccion(self, rot,
                       "Una decima de grado no describe una antena",
                       "describe una banda.",
                       VGroup(c_gem, c_est, c_dif, flechas, t_pred,
                              t_mide, t_reaj, panel),
                       espera=4.4)

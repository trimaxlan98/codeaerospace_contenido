class Clip2(Scene):
    """1.3.2 - El rango oblicuo: 550 km en el cenit y 2205 a 5 grados.
    Cuatro veces mas lejos son 12 dB de mas. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Elevacion y distancia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- geometria a escala ------------------------------------------
        # El radio terrestre se DEDUCE de la libreria (d(el=0)^2 = 2Rh+h^2)
        # para que el arco dibujado y las distancias rotuladas sean la
        # misma geometria; no hay ninguna cifra escrita a mano.
        R_T = float((rango_oblicuo(H_LEO, 0.0) ** 2 - H_LEO ** 2)
                    / (2.0 * H_LEO))
        R_U = 13.0                                  # unidades de escena
        K = R_U / R_T                               # unidades por km
        ORB_U = (R_T + H_LEO) * K
        CENTRO = np.array([-3.05, -R_U - 0.55, 0.0])
        ESTACION = CENTRO + UP * R_U

        def pos_sat(el_deg):
            lam = np.radians(float(angulo_central(H_LEO, el_deg)))
            return CENTRO + ORB_U * np.array([np.sin(lam), np.cos(lam), 0.0])

        tierra = Arc(radius=R_U, start_angle=np.radians(98.0),
                     angle=np.radians(-33.0), color=C_EJE, stroke_width=3.4)
        tierra.move_arc_center_to(CENTRO)
        orbita_solida = Arc(radius=ORB_U, start_angle=np.radians(96.0),
                            angle=np.radians(-29.0), color=C_CIELO,
                            stroke_width=2.4)
        orbita_solida.move_arc_center_to(CENTRO)
        orbita = DashedVMobject(orbita_solida, num_dashes=46)
        # El horizonte local es TANGENTE a la superficie en la estacion:
        # para que no se lean como una sola linea, va en gris de dato y a
        # trazos, y la superficie en el gris de mobiliario y solida.
        horizonte = DashedVMobject(
            Line(ESTACION + LEFT * 0.95, ESTACION + RIGHT * 5.75,
                 stroke_width=2.0, color=C_DATO).set_stroke(opacity=0.55),
            num_dashes=38)

        est = Dot(ESTACION, radius=0.08, color=C_CALCULO)
        t_est = tag_junto(est, "estacion", direccion=DL, buff=0.14)

        self.play(Create(tierra), run_time=1.1)
        self.play(FadeIn(est), FadeIn(t_est), Create(horizonte), run_time=0.9)
        self.play(Create(orbita), run_time=1.2)
        self.wait(0.5)

        # --- el satelite en el cenit --------------------------------------
        el_t = ValueTracker(90.0)
        rango_ini = Line(ESTACION, pos_sat(90.0), color=C_CALCULO,
                         stroke_width=3.6)
        sat = Dot(pos_sat(90.0), radius=0.09, color=C_SAT)
        self.play(FadeIn(sat, scale=1.5), Create(rango_ini), run_time=0.9)

        # el rango del cenit se queda de fantasma: al final los DOS
        # segmentos, el corto y el largo, tienen que verse juntos.
        fantasma = Line(ESTACION, pos_sat(90.0), color=C_CALCULO,
                        stroke_width=2.2).set_stroke(opacity=0.38)
        sat_cenit = Dot(pos_sat(90.0), radius=0.06,
                        color=C_SAT).set_opacity(0.38)
        self.add(fantasma, sat_cenit)
        self.remove(rango_ini)

        rango = always_redraw(
            lambda: Line(ESTACION, pos_sat(el_t.get_value()),
                         color=C_CALCULO, stroke_width=3.6))
        arco_el = always_redraw(
            lambda: Arc(radius=0.62, start_angle=0.0,
                        angle=np.radians(float(el_t.get_value())),
                        color=C_CALCULO, stroke_width=2.4)
            .move_arc_center_to(ESTACION).set_stroke(opacity=0.75))
        sat.add_updater(lambda m: m.move_to(pos_sat(el_t.get_value())))
        self.add(rango, arco_el)

        ANCLA = np.array([-4.60, 2.10, 0.0])

        def lectura():
            el = float(el_t.get_value())
            a = tag_hud(f"el {fmt(el, 0)} deg", font_size=26)
            b = tag_hud(f"d {fmt(float(rango_oblicuo(H_LEO, el)), 0)} km",
                        font_size=26)
            g = VGroup(a, b).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
            g.move_to(ANCLA)
            return g

        # Un always_redraw no admite FadeIn (cada frame se reconstruye y
        # pisa la opacidad): entra una copia estatica y se releva.
        lect_ini = lectura()
        self.play(FadeIn(lect_ini), run_time=0.6)
        self.remove(lect_ini)
        lect = always_redraw(lectura)
        self.add(lect)
        rot.mostrar(cifra_pie(f"cenit {fmt(D_CENIT, 0)} km"), zona="abajo")
        self.wait(1.8)

        # --- y el rango se estira hasta la mascara ------------------------
        for destino, dur in ((45.0, 1.7), (20.0, 1.5), (MASCARA, 1.8)):
            self.play(el_t.animate.set_value(destino), run_time=dur)
            self.wait(0.35)
        self.wait(0.6)

        rot.mostrar(cifra_pie(f"a {fmt(MASCARA, 0)} deg "
                              f"{fmt(D_HORIZ, 0)} km"), zona="abajo")
        self.wait(2.2)

        # --- lo que cuesta en decibelios ---------------------------------
        rot.mostrar(formula_pie(r"\Delta L = 20\log_{10}(d_2/d_1)"),
                    zona="abajo")
        barra = barras_comparar([ATEN_EXTRA], ["extra"], ancho=1.9, alto=2.25,
                                colores=[C_PELIGRO], unidad="dB", font_size=16)
        barra.move_to(RIGHT * 4.40 + DOWN * 1.25)
        self.play(FadeIn(barra.ejes), run_time=0.5)
        self.play(GrowFromEdge(barra.barras, DOWN), FadeIn(barra.rotulos),
                  run_time=1.1)
        # La cifra va al COSTADO de la barra: encima cae justo sobre la
        # etiqueta "dB" que la propia pieza pone en la cabeza del eje.
        t_aten = tag_hud(f"{fmt(ATEN_EXTRA, 2)} dB", font_size=24,
                         color=C_PELIGRO)
        t_aten.next_to(barra.barras[0], RIGHT, buff=0.26)
        self.play(FadeIn(t_aten), run_time=0.6)
        self.wait(2.4)

        rot.mostrar(cifra_pie(f"extra {fmt(ATEN_EXTRA, 2)} dB"), zona="abajo")
        self.wait(2.4)

        # --- las tres cifras juntas ---------------------------------------
        sat.clear_updaters()
        self.play(FadeOut(lect), run_time=0.4)
        panel = panel_cifras(f"cenit {fmt(D_CENIT, 0)} km",
                             (f"{fmt(MASCARA, 0)} deg {fmt(D_HORIZ, 0)} km",
                              C_SAT),
                             (f"extra {fmt(ATEN_EXTRA, 2)} dB", C_PELIGRO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.6)

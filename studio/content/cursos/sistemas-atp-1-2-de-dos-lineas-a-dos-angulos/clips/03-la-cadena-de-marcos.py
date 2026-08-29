class Clip3(Scene):
    """1.2.3 - La cadena de marcos: de TLE a Az/El, eslabon a eslabon.
    En ENU, el orden de atan2 es la trampa clasica del signo. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("La cadena de marcos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        cad = cadena(etiquetas=ESLABONES, font_size=17)
        cad.move_to(UP * 1.6)
        self.play(FadeIn(cad), run_time=1.1)
        self.wait(0.5)

        # --- se enciende un eslabon por vez: TLE, SGP4, ECI, ECEF ------------
        glosas = ("dos lineas", "propagador", "inercial", "fijo a tierra")
        rotulo = None
        for i, glosa in enumerate(glosas):
            self.play(cad.animate.encender(i), run_time=0.7)
            t = tag_junto(cad.caja_en(i), glosa, direccion=DOWN, buff=0.16,
                         font_size=15)
            if rotulo is not None:
                self.play(FadeOut(rotulo), run_time=0.2)
            self.play(FadeIn(t), run_time=0.4)
            rotulo = t
            self.wait(0.8)
        self.play(FadeOut(rotulo), run_time=0.3)

        # --- ECEF -> ENU: la estacion sobre el globo -------------------------
        self.play(cad.animate.encender(4), run_time=0.7)
        globo = Circle(radius=1.0, color=C_CIELO, stroke_width=2.0)
        globo.set_fill(C_CIELO, opacity=0.14)
        globo.move_to(LEFT * 3.15 + DOWN * 0.9)
        est = Dot(globo.get_top(), radius=0.06, color=C_CALCULO)
        self.play(FadeIn(globo), FadeIn(est, scale=1.6), run_time=0.9)
        self.wait(0.4)

        centro = est.get_center()
        ejes_enu, etiquetas_enu = VGroup(), VGroup()
        for nombre, direccion, color in (
            ("E", RIGHT, C_SAT), ("N", UP, C_OK), ("U", UR, C_CALCULO),
        ):
            vec = direccion / np.linalg.norm(direccion) * 0.78
            flecha = Arrow(centro, centro + vec, buff=0.0, color=color,
                          stroke_width=4,
                          max_tip_length_to_length_ratio=0.28)
            etiqueta = tag_hud(nombre, font_size=18, color=color)
            etiqueta.next_to(flecha.get_end(), direccion, buff=0.10)
            ejes_enu.add(flecha)
            etiquetas_enu.add(etiqueta)
        self.play(LaggedStart(*[GrowArrow(f) for f in ejes_enu],
                              lag_ratio=0.25),
                  run_time=1.3)
        self.play(LaggedStart(*[FadeIn(t) for t in etiquetas_enu],
                              lag_ratio=0.25), run_time=0.8)
        self.wait(1.4)

        # --- Az/El: el ejemplo resuelto y la trampa del orden ----------------
        self.play(cad.animate.encender(5), run_time=0.7)
        self.wait(0.5)

        rot.mostrar(formula_pie(r"\mathrm{Az} = \mathrm{atan2}(E,\,N)"),
                    zona="abajo")
        t_trampa = tag_junto(cad.caja_en(5), "ESTE primero", direccion=UP,
                             buff=0.20, color=C_PELIGRO)
        self.play(FadeIn(t_trampa), run_time=0.6)
        self.wait(1.8)

        panel = panel_cifras(f"Az {fmt(AZ_EJ, 2)}", f"El {fmt(EL_EJ, 2)}",
                             f"d {fmt(D_EJ, 1)} km")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.0)

        t_error = tag_hud(f"invertido {fmt(AZ_INVERTIDO, 2)}", font_size=17,
                          color=C_PELIGRO)
        t_error.next_to(panel, DOWN, buff=0.22)
        self.play(FadeIn(t_error), run_time=0.6)
        self.wait(4.6)

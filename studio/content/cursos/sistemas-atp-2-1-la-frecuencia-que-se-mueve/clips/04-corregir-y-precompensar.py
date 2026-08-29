class Clip4(Scene):
    """2.1.4 - Bajada se corrige en recepcion, subida se precompensa: dos
    flechas de signo opuesto que resuelven el mismo reloj. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Corregir y precompensar"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- bajada: se corrige en recepcion (f0 - fd) ---------------------
        sat_b = LEFT * 3.4 + UP * 1.55
        est_b = RIGHT * 1.2 + UP * 1.55
        d_sat_b = Dot(sat_b, radius=0.075, color=C_SAT)
        d_est_b = Dot(est_b, radius=0.075, color=C_CALCULO)
        flecha_b = Arrow(sat_b, est_b, buff=0.18, color=C_SAT,
                         stroke_width=5,
                         max_tip_length_to_length_ratio=0.10)
        t_bajada = tag_junto(flecha_b, "bajada", direccion=UP, buff=0.10)
        t_corrige = tag_hud("f0 - fd", font_size=20, color=C_CALCULO)
        t_corrige.next_to(d_est_b, DOWN, buff=0.16)
        self.play(FadeIn(d_sat_b, scale=1.4), FadeIn(d_est_b, scale=1.4),
                  run_time=0.7)
        self.play(GrowArrow(flecha_b), FadeIn(t_bajada), run_time=0.9)
        self.play(FadeIn(t_corrige), run_time=0.6)
        self.wait(1.3)

        # --- subida: se PREcompensa en transmision (f0 + fd) ---------------
        est_s = LEFT * 3.4 + DOWN * 1.35
        sat_s = RIGHT * 1.2 + DOWN * 1.35
        d_est_s = Dot(est_s, radius=0.075, color=C_CALCULO)
        d_sat_s = Dot(sat_s, radius=0.075, color=C_SAT)
        flecha_s = Arrow(est_s, sat_s, buff=0.18, color=C_CALCULO,
                         stroke_width=5,
                         max_tip_length_to_length_ratio=0.10)
        t_subida = tag_junto(flecha_s, "subida", direccion=DOWN, buff=0.10)
        t_precomp = tag_hud("f0 + fd", font_size=20, color=C_CALCULO)
        t_precomp.next_to(d_est_s, UP, buff=0.16)
        self.play(FadeIn(d_est_s, scale=1.4), FadeIn(d_sat_s, scale=1.4),
                  run_time=0.7)
        self.play(GrowArrow(flecha_s), FadeIn(t_subida), run_time=0.9)
        self.play(FadeIn(t_precomp), run_time=0.6)
        self.wait(1.5)

        rot.mostrar(formula_pie(
            r"f_{rx}=f_0-f_d \qquad f_{tx}=f_0+f_d"), zona="abajo")
        self.wait(2.8)

        # las dos flechas de signo opuesto dejan sitio a la señal en el
        # filtro del modem
        arriba = VGroup(d_sat_b, d_est_b, flecha_b, t_bajada, t_corrige)
        abajo = VGroup(d_est_s, d_sat_s, flecha_s, t_subida, t_precomp)
        self.play(FadeOut(arriba), FadeOut(abajo), run_time=0.8)

        # --- la señal deslizante se convierte en linea recta ---------------
        ancho_g, alto_g = 5.6, 2.2
        origen = np.array([-ancho_g / 2.0, -alto_g / 2.0, 0.0])
        filtro = Rectangle(width=ancho_g, height=alto_g * 0.30,
                           stroke_width=1.6, color=C_OK)
        filtro.set_fill(C_OK, opacity=0.14)
        filtro.set_stroke(color=C_OK, opacity=0.7)
        eje_t2 = Line(origen, origen + RIGHT * ancho_g, stroke_width=2.2,
                      color=C_EJE)
        t_filtro = tag_hud("filtro del modem", font_size=17, color=C_TENUE)
        t_filtro.next_to(filtro, UP, buff=0.12)
        self.play(FadeIn(filtro), Create(eje_t2), FadeIn(t_filtro),
                  run_time=1.2)
        self.wait(0.7)

        xs = PERFIL_D["t"] / PERFIL_D["duracion"]
        ymax = float(np.max(np.abs(CURVA_D)))
        deslizante = VMobject(stroke_color=C_PELIGRO, stroke_width=3.2)
        deslizante.set_points_as_corners([
            origen + np.array([x * ancho_g,
                               (0.5 + 0.46 * (y / ymax)) * alto_g, 0.0])
            for x, y in zip(xs, CURVA_D)
        ])
        recta = VMobject(stroke_color=C_OK, stroke_width=3.2)
        recta.set_points_as_corners([
            origen + np.array([x * ancho_g, 0.5 * alto_g, 0.0])
            for x in xs
        ])
        self.play(Create(deslizante), run_time=1.8)
        t_desliza = tag_hud("sin corregir", font_size=17, color=C_PELIGRO)
        t_desliza.next_to(deslizante, RIGHT, buff=0.16).shift(UP * 0.6)
        self.play(FadeIn(t_desliza), run_time=0.6)
        self.wait(1.6)

        self.play(Transform(deslizante, recta), FadeOut(t_desliza),
                  run_time=1.9)
        t_recta = tag_hud("centrada en el filtro", font_size=17,
                          color=C_OK)
        t_recta.next_to(filtro, DOWN, buff=0.14)
        self.play(FadeIn(t_recta), run_time=0.6)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"correccion {fmt(FD_UHF / 1000.0, 1)} kHz"),
                    zona="abajo")
        self.wait(2.6)

        # --- el cierre -------------------------------------------------------
        cierre_leccion(self, rot,
                       "La geometria y la frecuencia",
                       "beben del mismo reloj.",
                       filtro, eje_t2, t_filtro, deslizante, t_recta,
                       espera=4.4)

class Clip2(Scene):
    """1.2.2 - Kepler cierra el TLE: de n a T y de T a la altitud. Media
    revolucion menos son 150 km mas. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("De n a la altitud"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        rot.mostrar(cifra_pie(f"n = {fmt(N_REV_DIA, 1)} rev/dia"),
                    zona="abajo")
        self.wait(1.6)

        rot.mostrar(formula_pie(r"T = 86400 / n"), zona="abajo")
        self.wait(2.0)

        rot.mostrar(formula_pie(r"a = \left(\mu T^2 / 4\pi^2\right)^{1/3}"),
                    zona="abajo")
        self.wait(2.0)

        # --- la orbita a escala junto a la Tierra ---------------------------
        r_tierra = 1.3
        tierra = Circle(radius=r_tierra, color=C_CIELO, stroke_width=2.0)
        tierra.set_fill(C_CIELO, opacity=0.16)
        tierra.move_to(LEFT * 2.7 + DOWN * 0.15)
        radio_orb = r_tierra * A_TLE / (A_TLE - H_TLE)
        orbita = Circle(radius=radio_orb, color=C_CALCULO, stroke_width=2.4)
        orbita.move_to(tierra.get_center())
        self.play(FadeIn(tierra), run_time=0.8)
        self.play(Create(orbita), run_time=1.3)
        self.wait(0.4)

        sat = Dot(orbita.point_at_angle(0.6), radius=0.075, color=C_SAT)
        self.play(FadeIn(sat, scale=1.6), run_time=0.5)
        self.play(Rotate(sat, TAU, about_point=tierra.get_center()),
                  run_time=2.6, rate_func=linear)
        self.wait(0.4)

        t_h = tag_hud(f"h = {fmt(H_TLE, 0)} km", font_size=21)
        t_h.next_to(orbita, RIGHT, buff=0.28)
        self.play(FadeIn(t_h), run_time=0.6)
        self.wait(1.0)

        panel = panel_cifras(f"T = {fmt(T_TLE_MIN, 1)} min",
                             f"a = {fmt(A_TLE, 0)} km",
                             f"h = {fmt(H_TLE, 0)} km")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.6)

        # --- segundo caso: media revolucion menos, 150 km mas ---------------
        # La diferencia real (150 km sobre un radio de ~6800) es demasiado
        # fina para verse a esta escala: se declara "no a escala". Los
        # rotulos van en una columna FIJA (arrange) para que nunca se
        # encimen entre ellos ni con la flecha, que vive en otra zona.
        self.play(FadeOut(sat), FadeOut(t_h), run_time=0.4)

        angulo_flecha = -0.5
        direccion = np.array([np.cos(angulo_flecha), np.sin(angulo_flecha),
                              0.0])
        centro_t = tierra.get_center()
        inicio = centro_t + direccion * radio_orb
        fin = centro_t + direccion * radio_orb * 1.24
        flecha = Arrow(inicio, fin, buff=0.0, color=C_PELIGRO,
                       stroke_width=5, max_tip_length_to_length_ratio=0.28)
        self.play(GrowArrow(flecha), run_time=0.9)
        t_escala = tag_junto(flecha, "no a escala", direccion=RIGHT,
                             buff=0.22, font_size=14)
        self.play(FadeIn(t_escala), run_time=0.5)
        self.wait(1.0)

        columna = VGroup(
            tag_hud(f"n = {fmt(N_REV_2, 1)} rev/dia", font_size=19,
                   color=C_SAT),
            tag_hud(f"h = {fmt(H_TLE_2, 0)} km", font_size=19,
                   color=C_PELIGRO),
            tag_hud(f"+{fmt(DELTA_H, 0)} km", font_size=21,
                   color=C_PELIGRO),
        )
        columna.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        columna.next_to(orbita, RIGHT, buff=0.30).shift(UP * 0.55)
        self.play(FadeIn(columna[0]), run_time=0.5)
        self.wait(0.8)
        self.play(FadeIn(columna[1]), run_time=0.5)
        self.wait(0.8)
        self.play(FadeIn(columna[2]), run_time=0.6)
        self.wait(3.8)

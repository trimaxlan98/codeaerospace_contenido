class Clip2(Scene):
    """2.1.2 - El vector velocidad se descompone sobre la linea de vista:
    la parte radial es menor que la velocidad orbital entera. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Cuanta velocidad radial"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la geometria: estacion, linea de vista, satelite --------------
        estacion = LEFT * 3.1 + DOWN * 1.15
        sat = RIGHT * 2.05 + UP * 0.35
        est_dot = Dot(estacion, radius=0.075, color=C_CALCULO)
        sat_dot = Dot(sat, radius=0.085, color=C_SAT)
        t_est = tag_junto(est_dot, "estacion", direccion=DOWN, buff=0.14)
        t_sat = tag_junto(sat_dot, "satelite", direccion=LEFT, buff=0.16,
                          color=C_SAT)

        los_solida = Line(estacion, sat, stroke_width=2.2, color=C_CIELO)
        los_l = DashedVMobject(los_solida, num_dashes=24)
        self.play(FadeIn(est_dot), FadeIn(t_est), run_time=0.7)
        self.play(FadeIn(sat_dot, scale=1.5), FadeIn(t_sat), Create(los_l),
                  run_time=1.1)
        t_los = tag_hud("linea de vista", font_size=18, color=C_TENUE)
        t_los.move_to(los_solida.get_center() + DOWN * 0.34)
        self.play(FadeIn(t_los), run_time=0.6)
        self.wait(1.0)

        # --- el vector velocidad, tangencial a la orbita -------------------
        los_unit = (sat - estacion)
        los_unit = los_unit / np.linalg.norm(los_unit)
        perp_unit = np.array([-los_unit[1], los_unit[0], 0.0])
        lam = np.radians(LAM_HORIZ)
        v_dir = np.cos(lam) * los_unit + np.sin(lam) * perp_unit

        escala_v = 1.85 / V_ORBITAL
        v_end = sat + v_dir * escala_v * V_ORBITAL
        pie = sat + los_unit * escala_v * VR_MAX

        v_arrow = Arrow(sat, v_end, buff=0.0, color=C_CIELO, stroke_width=5,
                        max_tip_length_to_length_ratio=0.16)
        t_v = tag_hud(f"v = {fmt(V_ORBITAL, 2)} km/s", font_size=20,
                     color=C_CIELO)
        t_v.next_to(v_end, UP, buff=0.14)
        self.play(GrowArrow(v_arrow), FadeIn(t_v), run_time=1.0)
        self.wait(1.2)

        # el angulo entre la linea de vista y el vector es LAM_HORIZ: el
        # mismo angulo central del horizonte, ya calculado en la libreria
        los_ray = Line(sat, sat + los_unit * 1.3, stroke_width=0.01)
        v_ray = Line(sat, v_end, stroke_width=0.01)
        arco_lam = Angle(los_ray, v_ray, radius=0.55, color=C_TENUE,
                         stroke_width=2.2)
        t_lam = tag_hud(f"lam = {fmt(LAM_HORIZ, 1)} deg", font_size=18,
                       color=C_TENUE)
        t_lam.next_to(arco_lam, RIGHT, buff=0.16)
        self.play(Create(arco_lam), FadeIn(t_lam), run_time=0.9)
        self.wait(1.3)

        # --- la descomposicion: solo la componente radial cuenta -----------
        gota_solida = Line(v_end, pie, stroke_width=1.8, color=C_TENUE)
        gota_l = DashedVMobject(gota_solida, num_dashes=14)
        vr_arrow = Arrow(sat, pie, buff=0.0, color=C_CALCULO, stroke_width=6,
                         max_tip_length_to_length_ratio=0.18)
        angulo_recto = RightAngle(los_solida, gota_solida, length=0.16,
                                  color=C_TENUE, stroke_width=1.8)
        self.play(Create(gota_l), run_time=0.7)
        self.play(GrowArrow(vr_arrow), Create(angulo_recto), run_time=1.0)
        t_vr = tag_hud(f"vr = {fmt(VR_MAX, 2)} km/s", font_size=20,
                      color=C_CALCULO)
        t_vr.next_to(vr_arrow, DOWN, buff=0.16)
        self.play(FadeIn(t_vr), run_time=0.6)
        self.wait(1.4)

        # el vector completo no es la cifra que buscamos: se tacha
        cruz = Line(t_v.get_corner(DL), t_v.get_corner(UR), color=C_PELIGRO,
                   stroke_width=2.6)
        self.play(Create(cruz), run_time=0.6)
        self.wait(1.2)

        # el angulo ya cumplio su papel (justificar la formula): se apaga
        # para dejar sitio limpio al panel final
        self.play(FadeOut(arco_lam), FadeOut(t_lam), run_time=0.5)

        rot.mostrar(formula_pie(r"v_r = v \cos(\lambda)"), zona="abajo")
        self.wait(3.4)

        rot.mostrar(cifra_pie(f"vr max {fmt(VR_MAX, 2)} km/s horizonte"),
                    zona="abajo")
        self.wait(2.4)

        panel = panel_cifras((f"v = {fmt(V_ORBITAL, 2)} km/s", C_CIELO),
                             f"vr max = {fmt(VR_MAX, 2)} km/s",
                             f"lam = {fmt(LAM_HORIZ, 1)} deg",
                             desplazar=DOWN * 1.85)
        self.play(FadeIn(panel), run_time=0.8)
        self.wait(7.2)

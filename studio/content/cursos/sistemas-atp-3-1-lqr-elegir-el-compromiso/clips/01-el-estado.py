class Clip1(Scene):
    """3.1.1 - El eje no tiene mas memoria que dos numeros: angulo y
    velocidad. Con x = [theta, omega] la planta se escribe A, B, y la
    matriz de controlabilidad da el permiso para colocar los polos:
    det C = -0.25, rango 2. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("El estado del eje"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la montura, anclada por su pivote -----------------------------
        mont = montura(alto=2.3, font_size=16)
        destino = LEFT * 4.75 + DOWN * 0.15
        delta = destino - mont.pivote
        mont.shift(delta)
        # `pivote` y las bases son atributos FIJOS: si no se arrastran con
        # el shift, `apuntar` deja la marca del anillo donde nacio la pieza.
        mont.pivote = mont.pivote + delta
        mont.base_izq = mont.base_izq + delta
        mont.base_der = mont.base_der + delta
        piv = mont.pivote
        self.play(FadeIn(mont), run_time=0.9)

        # --- el eje siguiendo un pase real: los DOS numeros a la vez -------
        perfil = perfil_pase(H_LEO, el_max_deg=60.0, mascara_deg=MASCARA,
                             az_culminacion_deg=100.0, n=241)
        fracs = np.linspace(0.0, 1.0, len(perfil["el"]))

        def el_de(f):
            return float(np.interp(f, fracs, perfil["el"]))

        def elp_de(f):
            return float(np.interp(f, fracs, perfil["el_pto"]))

        f_t = ValueTracker(0.02)
        mont.apuntar(el_deg=el_de(0.02))
        mont.add_updater(lambda m: m.apuntar(el_deg=el_de(f_t.get_value())))

        p_ang = LEFT * 4.60 + DOWN * 1.90
        p_vel = LEFT * 4.60 + DOWN * 2.35
        lec_ang = always_redraw(
            lambda: tag_hud(f"ang {fmt(el_de(f_t.get_value()), 1)} deg",
                            font_size=21, color=C_CIELO).move_to(p_ang))
        lec_vel = always_redraw(
            lambda: tag_hud(f"vel {fmt(elp_de(f_t.get_value()), 2)} deg/s",
                            font_size=21, color=C_SAT).move_to(p_vel))
        self.play(FadeIn(lec_ang), FadeIn(lec_vel), run_time=0.5)
        self.play(f_t.animate.set_value(0.44), run_time=4.6,
                  rate_func=linear)
        mont.clear_updaters()
        lec_ang.clear_updaters()
        lec_vel.clear_updaters()
        self.wait(0.5)

        # --- se nombran los dos numeros sobre la propia montura ------------
        el_fin = el_de(0.44)
        horiz = DashedVMobject(
            Line(piv, piv + RIGHT * 1.15, stroke_width=2.2, color=C_EJE),
            num_dashes=12)
        arco = Arc(radius=0.66, start_angle=0.0,
                   angle=np.radians(el_fin), arc_center=piv,
                   color=C_CIELO, stroke_width=3.4)
        t_arco = tag_hud("ang", font_size=19, color=C_CIELO)
        t_arco.move_to(piv + RIGHT * 0.98 + UP * 0.34)
        giro = Arc(radius=1.72, start_angle=np.radians(el_fin - 6.0),
                   angle=np.radians(24.0), arc_center=piv, color=C_SAT,
                   stroke_width=3.4)
        giro.add_tip(tip_length=0.17)
        t_giro = tag_hud("vel", font_size=19, color=C_SAT)
        t_giro.next_to(giro, UP, buff=0.12)
        self.play(Create(horiz), Create(arco), FadeIn(t_arco), run_time=0.8)
        self.play(Create(giro), FadeIn(t_giro), run_time=0.8)
        self.wait(0.8)

        # --- el vector de estado -------------------------------------------
        x_vec = MathTex(r"x = \begin{bmatrix} \theta \\ \omega \end{bmatrix}",
                        font_size=52, color=C_TITULO)
        x_vec.move_to(RIGHT * 1.35 + UP * 0.95)
        self.play(Write(x_vec), run_time=1.1)
        self.wait(1.6)

        rot.mostrar(formula_pie(r"J\,\ddot{\theta} + b\,\dot{\theta} = u"),
                    zona="abajo")
        self.wait(2.2)
        rot.mostrar(cifra_pie(f"J = {fmt(J_EJE, 1)} kg m2"), zona="abajo")
        self.wait(2.0)
        rot.mostrar(cifra_pie(f"b = {fmt(B_EJE, 1)} N m s"), zona="abajo")
        self.wait(2.0)

        # --- la misma planta, en matrices ----------------------------------
        # Dos MathTex de distinta estructura NO son gemelos: se relevan por
        # fundido, en dos play seguidos.
        eq = MathTex(r"\dot x = ", _al.matriz_tex(A_M, 2), r"\,x + ",
                     _al.matriz_tex(B_M, 1), r"\,u",
                     font_size=38, color=C_TITULO)
        eq.move_to(RIGHT * 1.30 + UP * 0.95)
        eq[1].set_color(C_CALCULO)
        eq[3].set_color(C_CALCULO)
        self.play(FadeOut(x_vec), run_time=0.35)
        self.play(FadeIn(eq), run_time=0.6)
        self.wait(2.4)

        # --- el permiso matematico: la controlabilidad ---------------------
        matc = MathTex(r"C = \left[\, B \;\; AB \,\right] = "
                       + _al.matriz_tex(CTRL["matriz"], 3),
                       font_size=36, color=C_CALCULO)
        matc.move_to(RIGHT * 1.55 + DOWN * 1.30)
        self.play(Write(matc), run_time=1.4)
        self.wait(1.2)

        caja = SurroundingRectangle(matc, color=C_OK, stroke_width=2.4,
                                    buff=0.18)
        rot.mostrar(cifra_pie(f"det C = {fmt(DET_CTRL, 2)}"), zona="abajo")
        self.play(Create(caja), run_time=0.8)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"rango {RANGO_CTRL}: controlable"),
                    zona="abajo")
        self.wait(2.4)

        panel = panel_cifras(f"J = {fmt(J_EJE, 1)} kg m2",
                             f"b = {fmt(B_EJE, 1)} N m s",
                             (f"det C = {fmt(DET_CTRL, 2)}", C_OK),
                             (f"rango {RANGO_CTRL}", C_OK))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.6)

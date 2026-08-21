class Clip1(Scene):
    """2.3.1 - Un camino cruza el campo de viento. En cada tramito hay dos
    vectores, el campo F y el paso dr, y lo que se cobra depende del angulo
    que forman. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El campo cobra peaje")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el viento llena el plano ----------------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Un campo de viento: en cada punto del "
                              "plano, una flecha que empuja."),
                    zona="abajo", run_time=0.5)
        campo = campo_leccion(pl)
        self.play(LaggedStart(*[GrowArrow(f) for f in campo.flechas],
                              lag_ratio=0.012), run_time=1.9)
        self.wait(2.6)

        # --- momento: el camino que lo cruza ------------------------------
        rot.mostrar(pie_curso("Llevamos algo de A a B por este camino. "
                              "¿Cuánto trabaja el viento por nosotros?"),
                    zona="abajo", run_time=0.5)
        cam = camino(pl, R_CAM, flechas=3)
        pA = Dot(pl.p(A_CAM), radius=0.085, color=C_VEC)
        pB = Dot(pl.p(B_CAM), radius=0.085, color=C_VEC)
        eA = tag_hud("A", font_size=22, color=C_VEC).next_to(pA, DOWN,
                                                             buff=0.16)
        eB = tag_hud("B", font_size=22, color=C_VEC).next_to(pB, UP,
                                                            buff=0.18)
        self.play(FadeIn(pA, scale=0.5), FadeIn(eA), run_time=0.5)
        self.play(Create(cam.trazo), run_time=1.5)
        self.play(FadeIn(cam.marcas), FadeIn(pB, scale=0.5), FadeIn(eB),
                  run_time=0.6)
        self.wait(2.6)

        # --- momento: los dos vectores de un tramito ----------------------
        rot.mostrar(pie_curso("En cada tramito hay DOS vectores: el campo "
                              "F y el paso dr, que va por el camino."),
                    zona="abajo", run_time=0.5)
        par1 = par_F_dr(pl, cam, T_MUESTRA[0], angulo=True,
                        radio_angulo=0.46)
        rot_F = tag_hud("F", font_size=22, color=C_CAMPO)
        rot_F.next_to(par1.flecha_F.get_end(), DOWN, buff=0.16)
        rot_T = tag_hud("dr", font_size=22, color=C_CIFRA)
        # A la izquierda del PASO (normal a la tangente): justo ahi el
        # camino ya no pasa, y el rotulo no se monta sobre el trazo.
        rot_T.next_to(par1.flecha_T.get_end(),
                      np.array([-par1.T[1], par1.T[0], 0.0]), buff=0.14)
        self.play(FadeIn(par1.punto, scale=0.4), run_time=0.4)
        self.play(GrowArrow(par1.flecha_F), FadeIn(rot_F), run_time=0.7)
        self.play(GrowArrow(par1.flecha_T), FadeIn(rot_T), run_time=0.7)
        self.wait(3.4)

        # --- momento: aqui el viento va casi de lado ----------------------
        rot.mostrar(pie_curso("Aquí el viento sopla casi de lado: forma "
                              "un ángulo grande con el paso."),
                    zona="abajo", run_time=0.5)
        self.play(Create(par1.arco.arco), FadeIn(par1.arco.texto),
                  run_time=0.9)
        self.play(Indicate(par1.arco, color=C_GRAD, scale_factor=1.08),
                  run_time=0.8)
        self.wait(3.2)

        # --- momento: mas adelante el angulo se cierra --------------------
        rot.mostrar(pie_curso("Más adelante el ángulo se cierra: el viento "
                              "ya empuja hacia donde vamos."),
                    zona="abajo", run_time=0.5)
        # A y B ya hicieron su papel: se retiran para dejar sitio limpio a
        # las dos lecturas siguientes (la tercera cae justo sobre B).
        self.play(FadeOut(pB), FadeOut(eB), run_time=0.4)
        pares = VGroup()
        for t in T_MUESTRA[1:]:
            par = par_F_dr(pl, cam, t, angulo=True, radio_angulo=0.46)
            pares.add(par)
        for par in pares:
            self.play(FadeIn(par.punto, scale=0.4),
                      GrowArrow(par.flecha_F), GrowArrow(par.flecha_T),
                      run_time=0.7)
            self.play(Create(par.arco.arco), FadeIn(par.arco.texto),
                      run_time=0.6)
        self.wait(2.6)

        # --- momento: el producto punto es el peaje -----------------------
        rot.mostrar(pie_curso("Lo que el campo cobra —o paga— en ese "
                              "tramito es el producto punto."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(MathTex(r"\vec F \cdot d\vec r", font_size=42,
                                      color=C_CALCULO))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(4.4)

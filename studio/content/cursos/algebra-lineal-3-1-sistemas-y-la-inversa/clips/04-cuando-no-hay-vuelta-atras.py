class Clip4(Scene):
    """3.1.4 - Cuando det = 0 la rejilla se aplasta a una recta: dos x
    distintos caen en el mismo b, y hay b que no se alcanzan nunca. Cierra
    la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Cuando no hay vuelta atrás")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: una matriz que aplasta ---------------------------------
        pl = plano_leccion(vivo=True)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Pero no toda matriz se puede deshacer."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(A_SING), run_time=2.2)
        det_tag = tag_hud("det A = " + fmt(DET_SING, 0), font_size=20)
        panel_det = panel_derecha(det_tag)
        self.play(FadeIn(panel_det), run_time=0.4)
        self.wait(2.4)

        # --- momento: dos x, un solo destino ----------------------------------
        rot.mostrar(pie_curso("Volvamos a la rejilla original: aquí hay "
                              "dos x distintos."), zona="abajo",
                    run_time=0.5)
        self.play(*pl.anim_matriz(np.eye(2)), run_time=1.6)
        x1 = vector(pl, X1_SING, color=C_VEC, nombre=r"\vec x_1")
        x2 = vector(pl, X2_SING, color=C_VEC_2, nombre=r"\vec x_2")
        self.play(GrowArrow(x1.flecha), FadeIn(x1.etiqueta), run_time=0.8)
        self.play(GrowArrow(x2.flecha), FadeIn(x2.etiqueta), run_time=0.8)
        self.wait(2.2)

        rot.mostrar(pie_curso("Al aplicar A, los dos caen en el mismo "
                              "punto."), zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(A_SING, x1, x2), run_time=2.4)
        # OJO: no reasignar x1/x2 = x1.con_matriz(...) aqui. Transform ya
        # mutó los objetos EN SITIO (misma identidad); un con_matriz() crea
        # un gemelo nuevo que nunca se anadio a la escena, y el siguiente
        # play(Indicate(...)) lo anade por su cuenta -- queda un segundo
        # par de flechas fantasma que ni el fade del cierre limpia (porque
        # el cierre atrapa al gemelo, no al original mutado). Como no se
        # vuelven a usar las coordenadas de x1/x2, seguimos con los mismos
        # objetos.
        self.play(Indicate(x1.flecha, color=C_VEC, scale_factor=1.08),
                  Indicate(x2.flecha, color=C_VEC_2, scale_factor=1.08),
                  run_time=0.9)
        self.wait(2.4)

        # --- momento: un destino que nunca se alcanza ---------------------------
        rot.mostrar(pie_curso("Y un punto fuera de esa recta no se "
                              "alcanza jamás."), zona="abajo", run_time=0.5)
        b_fuera = flecha_libre(pl, (0, 0), B_FUERA, color=C_IMG,
                               opacidad=0.4)
        et_fuera = MathTex(r"\vec b\,'", font_size=28, color=C_IMG)
        et_fuera.set_opacity(0.7)
        et_fuera.next_to(pl.p(B_FUERA), UP, buff=0.16)
        self.play(FadeIn(b_fuera), FadeIn(et_fuera), run_time=0.8)
        self.wait(3.4)

        # --- cierre de la leccion --------------------------------------------
        cierre_leccion(self, rot, "Si el área sobrevive, hay inversa.",
                       "Si se aplasta, no.",
                       "Preguntar al revés: ¿a dónde llega todo? Siguiente "
                       "lección.", pl, panel_det, x1, x2, b_fuera, et_fuera)

class Clip3(Scene):
    """5.1.3 - Gram-Schmidt fabrica una base ortonormal desde cualquier par
    de vectores: normaliza el primero, y al segundo le resta su sombra
    sobre el primero antes de normalizar lo que queda. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Gram-Schmidt: restar sombras")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: dos vectores oblicuos, no perpendiculares ---------------
        pl = plano_leccion(vivo=False)
        v1 = vector(pl, V1_GS, color=C_VEC, nombre=r"\vec v_1")
        v2 = vector(pl, V2_GS, color=C_VEC_2, nombre=r"\vec v_2")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Dos vectores cualquiera, sin ningún ángulo "
                              "especial entre ellos."), zona="abajo",
                    run_time=0.5)
        self.play(GrowArrow(v1.flecha), GrowArrow(v2.flecha), run_time=0.9)
        self.play(FadeIn(v1.etiqueta), FadeIn(v2.etiqueta), run_time=0.3)
        ang = marca_angulo(pl, V1_GS, V2_GS, radio=0.6, color=C_CALCULO)
        self.play(Create(ang.arco), FadeIn(ang.texto), run_time=0.6)
        self.wait(2.8)

        # --- momento: normalizar v1 ---------------------------------------------
        rot.mostrar(pie_curso("Gram-Schmidt fabrica una base ortonormal a "
                              "partir de ellos. Primero: normaliza v1."),
                    zona="abajo", run_time=0.5)
        q1 = vector(pl, Q1_GS, color=C_I, nombre=r"\vec q_1", etiqueta_dir=DOWN)
        self.play(GrowArrow(q1.flecha), run_time=0.9)
        self.play(FadeIn(q1.etiqueta), run_time=0.3)
        self.play(v1.animate.set_opacity(0.4), FadeOut(ang), run_time=0.6)
        self.wait(2.6)

        # --- momento: la sombra de v2 sobre q1 ----------------------------------
        rot.mostrar(pie_curso("v2 no es perpendicular a q1: proyéctalo y "
                              "mira su sombra fantasma."), zona="abajo",
                    run_time=0.5)
        proy = proyeccion_dibujo(pl, V2_GS, Q1_GS, color=C_TENUE,
                                 color_guia=C_TENUE)
        proy.sombra.set_opacity(0.55)
        self.play(Create(proy.guia), run_time=0.6)
        self.play(GrowArrow(proy.sombra), run_time=0.7)
        self.wait(2.6)

        # --- momento: restar la sombra: el resto ---------------------------------
        rot.mostrar(pie_curso("Réstale a v2 esa sombra: lo que queda "
                              "apunta perpendicular a q1."), zona="abajo",
                    run_time=0.5)
        resto = flecha_libre(pl, SOMBRA_V2_Q1, V2_GS, color=C_IMG, grosor=5.0)
        self.play(GrowArrow(resto), run_time=0.8)
        self.wait(2.2)

        rot.mostrar(pie_curso("Ese resto, trasladado al origen, es un "
                              "vector con todo derecho propio."),
                    zona="abajo", run_time=0.5)
        resto_origen = flecha_libre(pl, (0, 0), RESTO_V2, color=C_IMG,
                                    grosor=5.0)
        self.play(Transform(resto, resto_origen), run_time=1.1)
        self.wait(2.4)

        # --- momento: normalizar el resto: q2 -------------------------------------
        rot.mostrar(pie_curso("Se normaliza igual que antes, y ya está: "
                              "q2."), zona="abajo", run_time=0.5)
        q2_flecha = flecha_libre(pl, (0, 0), Q2_GS, color=C_J, grosor=5.0)
        self.play(Transform(resto, q2_flecha), run_time=1.0)
        et_q2 = MathTex(r"\vec q_2", font_size=30, color=C_J)
        et_q2.next_to(pl.p(Q2_GS), LEFT, buff=0.2)
        self.play(FadeIn(et_q2), v2.animate.set_opacity(0.4), run_time=0.6)
        self.wait(2.6)

        # --- momento: el panel Q ------------------------------------------------
        rot.mostrar(pie_curso("gram_schmidt hace exactamente esto, paso a "
                              "paso, con cualquier lista de vectores."),
                    zona="abajo", run_time=0.5)
        panel_q = matriz_columnas(Q_GS, colores=(C_I, C_J), font_size=32)
        panel = panel_derecha(panel_q)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(3.4)

        # --- cierre del clip -------------------------------------------------------
        rot.mostrar(pie_curso("Ortonormalizar es solo esto: normalizar, y "
                              "restar sombras antes de seguir."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(panel, color=C_CALCULO, scale_factor=1.05),
                  run_time=0.8)
        self.wait(3.8)

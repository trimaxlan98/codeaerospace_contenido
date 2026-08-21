class Clip2(Scene):
    """2.2.2 - Como se calcula de verdad una linea de flujo: mirar la
    flecha, avanzar un poco, repetir. Un paso GRANDE (Euler, dt=0.7) da
    una poligonal angulosa; pasos MUY pequenos (RK4, misma libreria de
    clip 1) dan la curva de verdad. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Paso a paso")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mismo campo, la misma semilla --------------------------
        pl = plano_leccion()
        campo = campo_flechas(pl, CAMPO_VIENTO, paso=0.9, escala=0.42)
        self.play(FadeIn(pl), FadeIn(campo), run_time=0.9)
        rot.mostrar(pie_curso("Así se calcula de verdad: mira la flecha, "
                              "avanza un poco, repite."), zona="abajo",
                    run_time=0.5)
        p0 = P0_EULER
        semilla = Dot(pl.p(p0), radius=0.07, color=C_CALCULO)
        self.play(FadeIn(semilla, scale=0.5), run_time=0.4)
        self.wait(2.2)

        # --- momento: la formula del paso ----------------------------------------
        rot.mostrar(formula_pie(r"\vec p_{k+1} = \vec p_k + \Delta t\,"
                                r"F(\vec p_k)"), zona="abajo", run_time=0.5)
        etiqueta_dt = tag_hud(f"paso Euler: dt = {fmt(DT_EULER)}",
                              font_size=18, color=C_CALCULO)
        panel = panel_derecha(etiqueta_dt)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.5)
        self.wait(2.0)

        # --- momento: la poligonal de Euler, vertice a vertice ---------------------
        pts = euler_puntos(CAMPO_VIENTO, p0, DT_EULER, PASOS_EULER)
        poligonal = VGroup()
        for k in range(PASOS_EULER):
            seg = Line(pl.p(pts[k]), pl.p(pts[k + 1]), color=C_CALCULO,
                      stroke_width=3.0)
            vtx = Dot(pl.p(pts[k + 1]), radius=0.055, color=C_CALCULO)
            self.play(Create(seg), FadeIn(vtx, scale=0.5), run_time=0.38)
            poligonal.add(seg, vtx)
        self.wait(0.6)

        # --- momento: el paso grande se nota -------------------------------------
        rot.mostrar(pie_curso(f"Con un paso grande (dt = {fmt(DT_EULER)}), "
                              "la poligonal es angulosa: se aleja de la "
                              "curva real."), zona="abajo", run_time=0.5)
        self.play(Indicate(poligonal, color=C_CALCULO, scale_factor=1.03),
                  run_time=0.9)
        self.wait(3.2)

        # --- momento: la RK4 de la libreria, pasos muy pequenos --------------------
        rot.mostrar(pie_curso("La librería hace lo mismo con pasos MUY "
                              "pequeños (RK4): mira y compara."),
                    zona="abajo", run_time=0.5)
        dot = Dot(pl.p(p0), radius=0.09, color=C_VEC)
        lf = linea_flujo(pl, CAMPO_VIENTO, p0, T=T_COMPARA)
        self.play(FadeIn(dot, scale=0.5), run_time=0.4)
        self.play(Create(lf), MoveAlongPath(dot, lf), run_time=3.6,
                  rate_func=linear)
        self.wait(2.2)

        # --- cierre del clip: el mensaje ------------------------------------------
        rot.mostrar(pie_curso("Pasos pequeños y mejores: la curva "
                              "fucsia es la de verdad."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

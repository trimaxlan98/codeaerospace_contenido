class Clip4(Scene):
    """2.1.4 - Dos campos con sabor real: el viento sobre un perfil y la
    gravedad de un planeta. Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Campos de verdad")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el viento sobre un ala -----------------------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("El viento sobre un perfil: ondula, se "
                              "desvía, casi se enrosca."), zona="abajo",
                    run_time=0.5)
        campo_v = campo_flechas(pl, CAMPO_VIENTO, paso=0.85, escala=0.42)
        self.play(FadeIn(campo_v), run_time=1.2)
        self.wait(2.6)

        rot.mostrar(pie_curso("No es un dibujo suelto: es la misma "
                              "receta, otra fórmula debajo."), zona="abajo",
                    run_time=0.5)
        linea = linea_flujo(pl, CAMPO_VIENTO, (-3.6, -0.6), T=5.0)
        particula = Dot(pl.p(*linea.puntos[0]), radius=0.07, color=C_VEC)
        self.add(particula)
        self.play(Create(linea), run_time=1.4)
        self.play(MoveAlongPath(particula, linea), run_time=1.6,
                  rate_func=linear)
        self.wait(1.6)
        self.play(FadeOut(particula), run_time=0.3)

        # --- momento: la gravedad de un planeta ----------------------------------
        rot.mostrar(pie_curso("Ahora la gravedad: un planeta tira de "
                              "todo hacia su centro."), zona="abajo",
                    run_time=0.5)
        planeta = Circle(radius=0.32, color=C_GRAD, fill_color=C_GRAD,
                         fill_opacity=0.85, stroke_width=0).move_to(
            pl.p(0, 0))
        self.play(FadeOut(campo_v), FadeOut(linea), run_time=0.7)
        campo_g = campo_flechas(pl, campo_gravedad, paso=0.8, escala=0.45)
        self.play(FadeIn(campo_g), FadeIn(planeta), run_time=1.2)
        self.bring_to_front(planeta)
        self.wait(2.6)

        rot.mostrar(pie_curso("Todas las flechas apuntan al centro, y "
                              "son enormes cerca del planeta."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(campo_g.en(*P_CERCA_PLANETA), color=C_GRAD,
                           scale_factor=1.2), run_time=0.9)
        self.wait(3.2)

        # --- cierre --------------------------------------------------------------
        cierre_leccion(self, rot,
                       "Un campo es una flecha en cada punto.",
                       "El espacio entero, hablando.",
                       "Siguiente lección: seguir la corriente.",
                       pl, campo_g, planeta)

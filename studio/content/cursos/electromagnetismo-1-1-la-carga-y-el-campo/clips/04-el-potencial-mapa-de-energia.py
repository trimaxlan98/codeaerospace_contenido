class Clip4(Scene):
    """1.1.4 - El potencial: el otro mapa. Moverse por una equipotencial
    es gratis; cruzarlas cuesta energia — y esa cuenta por carga son los
    voltios. Cierra la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El potencial: el mapa de la energía")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el mapa de lineas, ya conocido, en tenue -------------
        cargas_mapa = [(1.0, -1.4, -0.1), (-1.0, 1.4, -0.1)]
        dipolo = lineas_campo(cargas_mapa, n_lineas=8)
        dipolo.lineas.set_stroke(opacity=0.35)
        dipolo.flechas.set_opacity(0.35)
        self.play(FadeIn(dipolo), run_time=0.9)
        rot.mostrar(pie_curso("El campo dice hacia dónde empuja. Falta "
                              "saber cuánto CUESTA moverse."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: las equipotenciales ----------------------------------
        niveles = equipotenciales(cargas_mapa, radios=(0.5, 0.85, 1.3))
        self.play(Create(niveles), run_time=1.8)
        rot.mostrar(pie_curso("Las curvas cian son alturas de energía: "
                              "las curvas de nivel del terreno."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: pasear gratis / cruzar cobrando ----------------------
        # La prueba viaja POR una equipotencial: el campo (la flecha) es
        # perpendicular al camino en todo momento, asi que no trabaja.
        prueba = Dot(niveles.curva_nivel(2).get_start(), radius=0.08,
                     color=C_CALCULO)
        rot.mostrar(pie_curso("Pasear por una curva de nivel es gratis: "
                              "el empuje queda de lado."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(prueba, scale=1.6), run_time=0.4)
        self.play(MoveAlongPath(prueba, niveles.curva_nivel(2)),
                  run_time=3.4, rate_func=linear)
        self.wait(1.2)

        salto = Arrow(niveles.curva_nivel(2).get_start(),
                      niveles.curva_nivel(0).get_start(), buff=0.05,
                      color=C_E, stroke_width=4.0, tip_length=0.16)
        rot.mostrar(pie_curso("Cruzar de una curva a otra, en cambio, se "
                              "paga. Esa tarifa por carga: voltios."),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(salto), run_time=0.7)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"V = \frac{\text{energía}}{\text{carga}}"
                                r"\qquad 1\,\text{V} = 1\,\text{J/C}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(dipolo), FadeOut(niveles), FadeOut(prueba),
                  FadeOut(salto), run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        linea1 = Text("El campo empuja.", font_size=40, color=C_TITULO)
        linea2 = Text("El potencial cobra.", font_size=40,
                      color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        rot.mostrar(pie_curso("Con los dos mapas en la mano, toca poner "
                              "las cargas a CORRER."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(4.6)

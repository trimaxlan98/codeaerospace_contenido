class Clip4(Scene):
    """4.2.4 - Iterar A sobre un vector cualquiera lo acerca, paso a paso,
    a la dirección propia dominante: el vector "se acuesta" sobre su eje.
    Cierra la lección. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Iterar y converger")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion()
        v = vector(pl, V_GEN, color=C_VEC, nombre=r"\vec v")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("¿Qué pasa si aplicamos A una y otra vez, "
                              "sin parar?"), zona="abajo", run_time=0.5)
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.8)
        self.wait(2.4)

        rot.mostrar(pie_curso("Cada paso lo acerca más a la dirección que "
                              "no gira: el eje propio dominante."),
                    zona="abajo", run_time=0.5)
        rastro = VGroup()
        for n in PASOS_ITERA:
            destino = potencia(A, n) @ V_GEN
            fantasma = flecha_libre(pl, (0, 0), destino, color=C_VEC,
                                    opacidad=0.3, grosor=3.0)
            self.play(*pl.anim_matriz(potencia(A, n), v), run_time=0.9)
            self.add(fantasma)
            rastro.add(fantasma)
        self.wait(1.6)

        rot.mostrar(pie_curso("Esa dirección es el vector propio de mayor "
                              "autovalor: nunca gira, siempre gana."),
                    zona="abajo", run_time=0.5)
        eje = span_recta(pl, U1, color=C_PROPIO, opacidad=0.55)
        self.play(Create(eje), run_time=1.2)
        self.wait(3.2)

        rot.mostrar(pie_curso("Su dirección ya casi no cambia: la razón "
                              "entre sus componentes tiende a uno."),
                    zona="abajo", run_time=0.5)
        razon = fmt(V_FINAL[1] / V_FINAL[0], 3)
        cifra = tag_hud("y / x -> " + razon, font_size=20, color=C_CALCULO)
        panel = panel_derecha(cifra)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.4)

        cierre_leccion(self, rot, "Repite un movimiento mil veces",
                       "y verás su eje.",
                       "La próxima lección mira lo que no cabe en el eje: "
                       "proyección y mínimos cuadrados.",
                       pl, v, rastro, eje, panel, espera=4.6)

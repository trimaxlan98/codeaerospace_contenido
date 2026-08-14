class Clip4(Scene):
    """2.3.4 - Velocidad indicada, calibrada, equivalente y verdadera.

    Cuatro numeros para la misma velocidad, y cada correccion quita un
    error: el de la toma, el de la compresibilidad y el de la densidad. El
    salto grande es el ultimo, y es el que explica por que un piloto vuela
    con la aguja quieta mientras el avion acelera. Cierre de la leccion.
    (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Cuatro velocidades para una")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        escalera = escalera_velocidades(tas=V_TAS, altitud=H_VUELO,
                                        ancho=5.4, alto=0.42,
                                        separacion=0.34)
        escalera.move_to(DOWN * 0.15)

        pies = ("IAS: lo que marca la aguja. Con el error de la toma "
                "incluido.",
                "CAS: la misma, ya corregida de dónde está el agujero.",
                "EAS: y ahora quitando lo que la compresibilidad infló.",
                "TAS: la de verdad, la que te lleva de un sitio a otro.")
        for barra, pie in zip(escalera.barras, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(barra, shift=0.14 * RIGHT), run_time=0.7)
            self.wait(4.4)

        # --- momento: el salto que importa ---------------------------------
        # El cociente sale de la propia pieza: EAS y TAS son sus barras 2 y 3.
        # La llave abraza las FILAS enteras, no solo sus rectangulos: medida
        # sobre las barras se planta justo encima de la cifra «250 m/s».
        llave = Brace(VGroup(escalera.barra(2), escalera.barra(3)),
                      direction=RIGHT, color=C_TRANS)
        factor = escalera.valor(3) / escalera.valor(2)
        tag = Text(f"×{factor:.2f}", font=FUENTE_HUD, font_size=24,
                   color=C_TRANS)
        tag.next_to(llave, RIGHT, buff=0.16)
        self.play(FadeIn(llave), FadeIn(tag), run_time=0.7)
        rot.mostrar(pie_curso("El salto grande es el último, y no es un "
                              "error del instrumento: es la altitud."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Arriba hay menos aire, así que la misma "
                              "presión dinámica sale de ir mucho más "
                              "rápido."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(escalera, llave, tag)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("El avión vuela con la indicada.", font_size=36,
                         color=C_TITULO),
            titulo_marca("El plan de vuelo, con la verdadera.", font_size=36,
                         color=C_TRANS)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)

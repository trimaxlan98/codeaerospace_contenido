class Clip2(Scene):
    """2.5.2 - Tobera convergente-divergente: regimenes de operacion.

    LA figura del modulo. La misma geometria y cuatro presiones de salida
    distintas: el tramo convergente es identico en las tres bloqueadas —
    aguas arriba de la garganta nadie se entera de lo de detras— y todo lo
    que cambia ocurre en el divergente. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Los regímenes de una De Laval")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        tobera = perfil_tobera(area_garganta=AREA_GARGANTA,
                               regimenes=ORDEN_REGIMENES, x_choque=X_CHOQUE,
                               ancho=6.2, alto_tubo=1.5, alto_grafico=2.1,
                               hueco=0.45)
        tobera.move_to(DOWN * 0.30)

        self.play(Create(tobera.tubo.paredes), FadeIn(tobera.tubo.eje),
                  run_time=1.1)
        self.play(FadeIn(tobera.ejes), run_time=0.6)
        rot.mostrar(pie_curso("La misma tobera, siempre. Lo único que cambia "
                              "es la presión que hay fuera."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- momento: las cuatro, de menos a mas exigente -----------------
        pies = ("Presión de fuera casi igual que dentro: ni se bloquea. Es "
                "un venturi.",
                "Bájala y llega el bloqueo: Mach 1 en la garganta, pero "
                "detrás vuelve a frenar.",
                "Más abajo, el aire acelera de verdad... y a mitad del "
                "divergente se encuentra un choque.",
                "Y con la presión justa, supersónico hasta la salida. Ahí "
                "está adaptada.")
        for clave, pie in zip(ORDEN_REGIMENES, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            partes = [Create(tobera.curva(clave))]
            if tobera.choque(clave) is not None:
                partes.append(Create(tobera.choque(clave)))
            self.play(*partes, run_time=0.9)
            self.wait(4.2)

        # --- momento: lo que comparten -------------------------------------
        # Las tres bloqueadas coinciden aguas arriba de la garganta: se
        # comprueba con la propia pieza, no de memoria.
        tramo = Line(tobera.punto_de("diseno", 0.06),
                     tobera.punto_de("diseno", 0.46), stroke_width=6.0,
                     color=C_CALCULO).set_opacity(0.35)
        self.play(Create(tramo), run_time=0.8)
        rot.mostrar(pie_curso("Fíjate en el convergente: tres de las cuatro "
                              "curvas van exactamente por el mismo sitio."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Están bloqueadas. Aguas arriba de la "
                              "garganta, nadie se entera de lo que pasa "
                              "detrás."), zona="abajo", run_time=0.5)
        self.wait(4.8)

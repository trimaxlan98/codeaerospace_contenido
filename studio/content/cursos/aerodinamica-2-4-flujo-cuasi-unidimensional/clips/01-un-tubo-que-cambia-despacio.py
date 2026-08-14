class Clip1(Scene):
    """2.4.1 - Hipotesis de area variable lentamente.

    Todo el modelo cuasi-unidimensional se sostiene en una condicion
    geometrica: que el tubo se ensanche despacio. Si la pared gira deprisa,
    el flujo se separa o aparecen ondas oblicuas, y ya no hay "un valor por
    seccion" que valga. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Un tubo que cambia despacio")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        bueno = conducto("delaval", area_garganta=AREA_GARGANTA, largo=5.4,
                         alto=1.9, color=C_TENUE)
        bueno.move_to(UP * 1.15)
        self.play(Create(bueno.paredes), FadeIn(bueno.eje), run_time=1.2)
        rot.mostrar(pie_curso("Este tubo cumple la hipótesis: la pared gira "
                              "poco a poco."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # La seccion se cuelga del localizador del conducto: su altura es la
        # del area en esa estacion, no un numero copiado.
        seccion = Line(bueno.punto_de(0.68, -1.0), bueno.punto_de(0.68, 1.0),
                       stroke_width=2.4, color=C_CALCULO)
        self.play(Create(seccion), run_time=0.6)
        rot.mostrar(pie_curso("Por eso vale decir «el Mach en esta sección», "
                              "en singular."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- momento: el tubo que no la cumple -----------------------------
        # Un divergente brusco: la pared abre de golpe y el flujo no la
        # sigue. Se dibuja a mano porque es justo la geometria que la
        # libreria NO modela.
        x0, ancho_malo, medio = -2.7, 5.4, 0.34
        quiebro, apertura = 0.30, 1.15
        malo = VGroup()
        esquinas = {}
        for signo in (1, -1):
            pts = [(x0, signo * medio, 0),
                   (x0 + ancho_malo * quiebro, signo * medio, 0),
                   (x0 + ancho_malo * (quiebro + 0.05), signo * apertura, 0),
                   (x0 + ancho_malo, signo * apertura, 0)]
            pared = VMobject(color=C_TENUE, stroke_width=2.6)
            pared.set_points_as_corners([np.array(p) for p in pts])
            malo.add(pared)
            esquinas[signo] = pts
        malo.move_to(DOWN * 1.35)

        self.play(FadeOut(seccion), run_time=0.3)
        self.play(Create(malo), run_time=1.1)
        rot.mostrar(pie_curso("Este no. La pared se abre de golpe y el aire "
                              "no la sigue."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        # El chorro sigue recto y estrecho mientras la pared se va: entre
        # los dos queda el hueco del remolino, que es lo que hay que ver.
        # Se sombrea, porque dos lineas paralelas no cuentan una separacion.
        chorro = VGroup()
        for signo in (1, -1):
            borde = [np.array([x0 + ancho_malo * 0.05, signo * medio, 0]),
                     np.array([x0 + ancho_malo * 0.55, signo * medio * 1.05,
                               0]),
                     np.array([x0 + ancho_malo, signo * medio * 1.15, 0])]
            traza = VMobject(color=C_TRANS, stroke_width=2.6)
            traza.set_points_smoothly(borde)
            pared = esquinas[signo]
            remolino = Polygon(borde[0], borde[-1],
                               np.array(pared[-1]), np.array(pared[2]),
                               stroke_width=0, fill_color=C_TRANS,
                               fill_opacity=0.16)
            chorro.add(remolino, traza)
        chorro.move_to(malo.get_center() + RIGHT * 0.05)
        # El rotulo va DENTRO del remolino de arriba: entre el tubo malo y
        # el pie no queda un renglon libre, y el hueco sombreado si es
        # ancho y esta vacio.
        tag_sep = Text("flujo separado", font_size=18, color=C_TRANS)
        tag_sep.move_to(chorro[0].get_center() + RIGHT * 0.35)

        self.play(Create(chorro), FadeIn(tag_sep), run_time=0.9)
        rot.mostrar(pie_curso("Se separa. En la misma sección hay chorro "
                              "rápido en el centro y remolino en los "
                              "bordes."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Y entonces «el Mach de la sección» ya no "
                              "significa nada."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Toda la lección vale para el de arriba. Para "
                              "el de abajo hace falta un modelo completo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

class Clip1(Scene):
    """1.2.1 - Un mensaje no baja de un salto: pasa por cuatro capas, cada
    una con un trabajo distinto y una manera propia de hacerlo. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Cuatro capas, cuatro trabajos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la pila completa -------------------------------------
        rot.mostrar(pie_curso("Un mensaje no baja de un salto: pasa por "
                              "cuatro capas antes de tocar el cable."),
                    zona="abajo", run_time=0.5)
        p = pila(datos=DATOS_CHICO, encapsulado=0, ancho=3.6)
        p.shift(RIGHT * 1.7)
        self.play(LaggedStart(*[
            FadeIn(VGroup(p.capa(i), p.rotulo(i), p.tamano(i)),
                  shift=0.14 * UP)
            for i in range(len(p.capas))], lag_ratio=0.28), run_time=1.4)
        self.wait(5.2)

        # --- momento: un trabajo por capa -----------------------------------
        rot.mostrar(pie_curso("Cada capa tiene un trabajo propio: pedir, "
                              "entregar sin perderse, elegir camino, "
                              "hablar con el cable de al lado."),
                    zona="abajo", run_time=0.5)
        for i, (nombre, proto, cab) in enumerate(p.capas):
            self.play(p.capa(i).animate.set_stroke(C_PAQUETE, width=3.2)
                      .set_fill(C_PAQUETE, opacity=0.20),
                      p.rotulo(i).animate.set_color(C_PAQUETE),
                      run_time=0.35)
            ej = tag_junto(p.capa(i), EJEMPLOS_CAPA[nombre], direccion=LEFT,
                          buff=0.30, font_size=18, color=C_PAQUETE)
            self.play(FadeIn(ej, shift=0.10 * RIGHT), run_time=0.35)
            self.wait(1.35)
            self.play(p.capa(i).animate.set_stroke(C_CAPA, width=2.4)
                      .set_fill(C_CAPA, opacity=0.06),
                      p.rotulo(i).animate.set_color(C_CAPA),
                      FadeOut(ej), run_time=0.35)
        self.wait(0.4)

        # --- momento: cada capa habla con su igual --------------------------
        rot.mostrar(pie_curso("Por eso dos capas iguales, en extremos "
                              "distintos, se entienden aunque el medio "
                              "cambie por completo."),
                    zona="abajo", run_time=0.5)
        emisor = pila(datos=DATOS_CHICO, encapsulado=0, ancho=2.6, fs=13)
        emisor.shift(LEFT * 3.35)
        emisor.tamanos.set_opacity(0.0)  # el peso ya se mostro; aqui solo
        # importa la pareja de capas, y su hueco lo ocupa la linea punteada
        receptor = pila(datos=DATOS_CHICO, encapsulado=0, ancho=2.6, fs=13)
        receptor.shift(RIGHT * 3.35)
        et_emisor = tag_hud("EMISOR", font_size=16, color=C_EJE)
        et_emisor.next_to(emisor, UP, buff=0.22)
        et_receptor = tag_hud("RECEPTOR", font_size=16, color=C_EJE)
        et_receptor.next_to(receptor, UP, buff=0.22)
        self.play(FadeOut(p), run_time=0.5)
        self.play(FadeIn(emisor), FadeIn(receptor), FadeIn(et_emisor),
                  FadeIn(et_receptor), run_time=0.7)
        puentes = lineas_pares(emisor, receptor)
        self.play(LaggedStart(*[Create(l) for l in puentes], lag_ratio=0.25),
                  run_time=1.2)
        self.wait(7.4)

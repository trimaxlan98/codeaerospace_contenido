class Clip2(Scene):
    """2.2.2 - Por cada fila que el seek encuentra en el indice, un viaje de
    vuelta al agrupado que abre tres paginas. Se dibujan cinco viajes y luego
    se acelera: el contador ambar sube hasta lo que midio el motor (597),
    casi lo mismo que predice el modelo (576). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso(f"{S.miles(C501)} viajes"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        # --- izquierda: las filas que ya encontro el seek en el indice -----
        cola = VGroup(*[Dot(radius=0.1, color=C_INDICE) for _ in range(5)])
        cola.arrange(DOWN, buff=0.4)
        cola.move_to(LEFT * 4.4 + UP * 0.75)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in cola],
                              lag_ratio=0.15), run_time=1.2)
        self.wait(1.0)

        # marcador que se queda: quedan muchas mas filas por procesar
        sigue = VGroup(*[Dot(radius=0.045, color=C_TENUE) for _ in range(3)])
        sigue.arrange(DOWN, buff=0.14)
        sigue.next_to(cola, DOWN, buff=0.22)
        et_cola = tag_hud(f"{S.miles(C501)} filas", font_size=20)
        et_cola.next_to(sigue, DOWN, buff=0.32)
        self.play(FadeIn(sigue), FadeIn(et_cola), run_time=0.5)
        self.wait(1.6)

        # --- derecha: el indice agrupado con sus tres niveles ---------------
        arbol = S.ArbolB(anchos=(1, 4, 10), ancho=5.4, alto=2.6, lado=0.32,
                         color=C_TENUE)
        arbol.move_to(RIGHT * 1.1 + DOWN * 0.3)
        self.play(FadeIn(arbol), run_time=0.8)
        tag_agr = tag_junto(arbol, "indice agrupado", UP, buff=0.3)
        self.play(FadeIn(tag_agr), run_time=0.4)
        modelo_tag = tag_junto(arbol, "modelo: 3 por fila", DOWN, buff=0.35,
                               color=C_CALCULO)
        self.play(FadeIn(modelo_tag), run_time=0.4)
        self.wait(2.0)

        # --- el contador de lecturas -----------------------------------------
        cont = Contador(0, rotulo="lecturas", font_size=36, digitos=3)
        cont.move_to(UP * 2.15 + LEFT * 1.4)
        self.play(FadeIn(cont), run_time=0.4)
        self.wait(1.0)

        # --- cinco viajes dibujados: cada uno abre tres paginas ---------------
        hojas_idx = [1, 4, 7, 2, 8]
        valor = 0
        for i, h in enumerate(hojas_idx):
            origen = cola[i]
            viajero = origen.copy().set_color(C_BUENO)
            self.add(viajero)
            ruta = arbol.ruta(h)
            self.play(FadeOut(origen),
                      viajero.animate.move_to(ruta[0].get_center()),
                      run_time=0.35)
            self.play(*[p[0].animate.set_fill(C_BUENO, 0.85).set_stroke(C_BUENO)
                        for p in ruta], run_time=0.35)
            valor += 3
            cont.fijar(valor)
            self.play(FadeOut(viajero),
                      *[p[0].animate.set_fill(C_BUENO, 0.3)
                        .set_stroke(C_BUENO, opacity=0.5) for p in ruta],
                      run_time=0.3)
        self.wait(1.0)

        # --- acelera: el resto de los viajes, sin dibujarlos uno a uno -------
        modelo_tag2 = tag_hud(f"modelo {S.miles(MODELO_501)}", font_size=20,
                              color=C_CALCULO)
        modelo_tag2.next_to(cont, RIGHT, buff=0.5)
        self.play(FadeIn(modelo_tag2), run_time=0.4)
        cont.anim(self, M["c501_lookup"], desde=valor, run_time=2.4,
                 extra=[LaggedStart(*[Indicate(h[0], color=C_MOTOR,
                                               scale_factor=1.05)
                                      for h in arbol.hojas], lag_ratio=0.06)])
        self.wait(1.8)

        rot.mostrar(motor_pie(lecturas(M["c501_lookup"])), zona="abajo",
                    run_time=0.5)
        self.wait(9.0)

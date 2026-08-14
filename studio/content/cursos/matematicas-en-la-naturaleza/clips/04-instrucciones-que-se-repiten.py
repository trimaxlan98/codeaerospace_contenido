class Clip4(Scene):
    """4 - Instrucciones que se repiten. Las cuatro reglas del helecho de
    Barnsley y su acumulacion punto a punto; el arbol crece nivel a nivel
    y el micelio anillo a anillo. Triptico final. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Instrucciones que se repiten")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: cuatro reglas y nada mas ----------------------------
        rot.mostrar(pie_curso("Cuatro reglas de copiar, encoger y girar. "
                              "Nada más."), zona="abajo", run_time=0.5)
        centro_helecho = LEFT * 3.9 + DOWN * 0.35
        marcos = mapas_helecho_marcos(alto_escena=5.0)
        marcos.move_to(centro_helecho)
        self.play(FadeIn(marcos), run_time=1.1)
        self.wait(4.6)

        # --- momento: el azar obedece y aparece el helecho ----------------
        rot.mostrar(pie_curso("Punto a punto, el azar obedece y aparece el "
                              "helecho."), zona="abajo", run_time=0.5)
        previo = None
        for n, pausa in ((300, 1.2), (3_000, 1.2), (30_000, 1.2),
                         (250_000, 0.5)):
            helecho = imagen_helecho(n, alto_escena=5.0)
            helecho.move_to(centro_helecho)
            self.add(helecho)
            if previo is not None:
                self.remove(previo)
            previo = helecho
            self.wait(pausa)
        self.play(FadeOut(marcos), run_time=0.6)
        self.wait(2.0)

        # --- momento: el arbol es una rama que se repite ------------------
        rot.mostrar(pie_curso("Un árbol es una rama que se repite; un "
                              "hongo, una red que se reparte."),
                    zona="abajo", run_time=0.5)
        arbol = arbol_fractal(7, escala=1.0)
        arbol.move_to(RIGHT * 0.7 + DOWN * 0.35)
        for i in range(7):
            self.play(FadeIn(arbol.nivel(i)), run_time=0.22)
        red = red_micelio(5, escala=1.05)
        red.move_to(RIGHT * 4.6 + DOWN * 0.35)
        for i in range(5):
            self.play(FadeIn(red.anillo(i)), run_time=0.2)
        self.wait(3.2)

        # --- momento: la instruccion, no el plano -------------------------
        rot.mostrar(pie_curso("El genoma no guarda el plano: guarda la "
                              "instrucción."), zona="abajo", run_time=0.5)
        self.wait(6.4)

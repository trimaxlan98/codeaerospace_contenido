class Clip1(Scene):
    """5.3.1 - Un satelite con tres estados; las flechas son probabilidades
    de pasar de uno a otro y T las guarda por columnas (columna = desde
    donde), cada columna sumando 1. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Estados y probabilidades")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los tres estados como nodos ---------------------------
        rot.mostrar(pie_curso("Un satélite vive siempre en uno de tres "
                              "estados. Nunca en dos a la vez."),
                    zona="abajo", run_time=0.5)
        circulos = []
        letras = VGroup()
        nombres = VGroup()
        for i in range(3):
            c = Circle(radius=R_NODO, color=COLORES_ESTADOS[i],
                      fill_color=COLORES_ESTADOS[i], fill_opacity=0.16,
                      stroke_width=3)
            c.move_to(POSICIONES[i])
            letra = Text(ESTADOS[i], font_size=26, color=COLORES_ESTADOS[i])
            letra.move_to(c.get_center() + UP * 0.12)
            nombre = tag_junto(c, NOMBRES_ESTADOS[i], DOWN, buff=0.18,
                               font_size=15)
            circulos.append(c)
            letras.add(letra)
            nombres.add(nombre)
        self.play(*[Create(c) for c in circulos], run_time=1.0)
        self.play(FadeIn(letras), FadeIn(nombres), run_time=0.6)
        self.wait(4.0)

        # --- momento: las flechas entre estados -----------------------------
        rot.mostrar(pie_curso("Cada día hay una probabilidad de quedarse, "
                              "o de pasar a otro estado."), zona="abajo",
                    run_time=0.5)
        pares = ((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1))
        arcos = VGroup()
        cifras_borde = VGroup()
        for j, i in pares:
            a, b = POSICIONES[j], POSICIONES[i]
            direccion = (b - a) / np.linalg.norm(b - a)
            p1 = a + direccion * R_NODO
            p2 = b - direccion * R_NODO
            arco = CurvedArrow(p1, p2, angle=0.45, color=COLORES_ESTADOS[j],
                               stroke_width=2.5, tip_length=0.14)
            medio = arco.point_from_proportion(0.5)
            afuera = medio - (a + b) / 2.0
            norma = np.linalg.norm(afuera)
            if norma > 1e-6:
                afuera = afuera / norma
            cifra = tag_hud(fmt(T[i, j], 2), font_size=14,
                            color=COLORES_ESTADOS[j])
            cifra.move_to(medio + afuera * 0.24)
            arcos.add(arco)
            cifras_borde.add(cifra)
        self.play(*[Create(a) for a in arcos], run_time=1.3)
        self.play(FadeIn(cifras_borde), run_time=0.5)
        self.wait(3.8)

        # --- momento: quedarse tambien es una probabilidad -------------------
        rot.mostrar(pie_curso("Y también hay probabilidad de quedarse: la "
                              "escribimos dentro de cada estado."),
                    zona="abajo", run_time=0.5)
        quedarse = VGroup()
        for i in range(3):
            b = tag_hud(fmt(T[i, i], 2), font_size=13, color=C_TENUE)
            b.move_to(POSICIONES[i] + DOWN * 0.16)
            quedarse.add(b)
        self.play(FadeIn(quedarse), run_time=0.6)
        self.wait(3.4)

        # --- momento: todo eso, en una matriz por columnas --------------------
        rot.mostrar(pie_curso("Todo eso vive en una matriz T: cada "
                              "columna es \"si hoy estás ahí\"."),
                    zona="abajo", run_time=0.5)
        mat = matriz_columnas(T, colores=COLORES_ESTADOS, font_size=32)
        panel = panel_derecha(mat)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(3.4)

        # --- momento: cada columna suma 1 --------------------------------------
        rot.mostrar(pie_curso("Y cada columna suma exactamente uno: toda "
                              "la probabilidad se va a alguna parte."),
                    zona="abajo", run_time=0.5)
        sumas = VGroup()
        for j in range(3):
            s = tag_hud(fmt(T[:, j].sum(), 1), font_size=16,
                       color=COLORES_ESTADOS[j])
            s.next_to(mat.columna(j), DOWN, buff=0.22)
            sumas.add(s)
        self.play(FadeIn(sumas), run_time=0.5)
        self.play(*[Indicate(mat.columna(j), color=COLORES_ESTADOS[j])
                   for j in range(3)], run_time=1.1)
        self.wait(4.6)

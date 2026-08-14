class Clip7(Scene):
    """7 - El ritmo de lo vivo. Capitalizar en saltos cada vez mas finos:
    la escalera (1+1/n)^n sube 2.00, 2.44, 2.61, 2.69... y se pega a la
    curva continua. El techo es e; el decaer usa el mismo ritmo. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El ritmo de lo vivo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: la bacteria no espera turno -------------------------
        rot.mostrar(pie_curso("Una bacteria no espera a fin de año para "
                              "dividirse: crece a cada instante."),
                    zona="abajo", run_time=0.5)
        curva = curva_crecimiento(ancho=6.0, alto=3.9)
        curva.move_to(LEFT * 1.6 + UP * 0.25)
        self.play(FadeIn(curva.ejes), run_time=0.8)

        escalera = escalera_compuesta(N_COMPUESTA[0], curva)
        valor = tag_hud(f"(1+1/{N_COMPUESTA[0]})^{N_COMPUESTA[0]} = "
                        f"{escalera.valor_final():.2f}", font_size=17,
                        color=C_QUIMICA)
        valor.move_to(RIGHT * 3.9 + UP * 1.9)
        self.play(Create(escalera.traza), run_time=1.2)
        rot.mostrar(valor, zona="valor", run_time=0.4)
        self.wait(3.2)

        # --- momento: capitalizar mas seguido rinde mas -------------------
        rot.mostrar(pie_curso("Capitalizar más seguido rinde más… pero con "
                              "un techo."), zona="abajo", run_time=0.5)
        for n in N_COMPUESTA[1:]:
            otra = escalera_compuesta(n, curva)
            nuevo = tag_hud(f"(1+1/{n})^{n} = {otra.valor_final():.2f}",
                            font_size=17, color=C_QUIMICA)
            nuevo.move_to(RIGHT * 3.9 + UP * 1.9)
            self.play(Transform(escalera.traza, otra.traza), run_time=0.9)
            rot.mostrar(nuevo, zona="valor", run_time=0.35)
            self.wait(0.7)
        self.play(Create(curva.curva), run_time=1.2)
        self.wait(1.4)

        # --- momento: el techo tiene nombre -------------------------------
        formula = formula_pie(r"\left(1+\tfrac{1}{n}\right)^{n}"
                              r"\ \xrightarrow{\ n\to\infty\ }\ e",
                              color=C_CONSTANTE)
        rot.mostrar(formula, zona="abajo", run_time=0.5)
        e_tag = tag_hud(f"e = {E:.5f}…", font_size=21, color=C_CONSTANTE)
        e_tag.move_to(RIGHT * 3.9 + UP * 1.9)
        rot.mostrar(e_tag, zona="valor", run_time=0.4)
        self.wait(5.0)

        # --- momento: el mismo ritmo para decaer --------------------------
        rot.mostrar(pie_curso("Ese techo es e: el número del crecimiento "
                              "continuo — y también del decaer."),
                    zona="abajo", run_time=0.5)
        caida = curva_crecimiento(tasa=-1.0, t_max=3.0, ancho=2.5,
                                  alto=1.7, color=C_QUIMICA, y_max=1.1)
        caida.move_to(RIGHT * 4.1 + DOWN * 1.3)
        etiqueta = tag_junto(caida, "decaer", DOWN, buff=0.16, font_size=16,
                             color=C_QUIMICA)
        self.play(FadeIn(caida), FadeIn(etiqueta), run_time=0.9)
        self.wait(5.2)

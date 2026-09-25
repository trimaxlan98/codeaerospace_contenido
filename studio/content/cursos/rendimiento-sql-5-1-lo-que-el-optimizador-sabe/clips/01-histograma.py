class Clip1(Scene):
    """5.1.1 - El optimizador no lee la tabla: guarda un histograma de hasta
    200 pasos por columna indexada. Se dibujan las 181 barras del modelo
    (escala LINEAL): casi todas parejas, salvo una que se recorta y sigue
    de largo (se revela en el clip siguiente). Un paso normal se nombra:
    RANGE_HI_KEY (donde termina) y EQ_ROWS (cuantas filas son ese valor
    exacto). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El resumen de una columna"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        base = Line(LEFT * 5.2 + DOWN * 2.1, RIGHT * 5.2 + DOWN * 2.1,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.6)
        self.wait(0.4)

        barras, quiebre = barras_histograma(HISTO, ancho=10.4, alto_pared=1.7,
                                            alto_recorte=3.1, base_y=-2.1,
                                            color=C_CREE,
                                            indice_recortado=IDX_C1)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in barras],
                              lag_ratio=0.012), run_time=3.4)
        self.wait(0.6)
        self.play(FadeIn(quiebre), run_time=0.5)
        sigue = tag_junto(quiebre, "sigue", UP, buff=0.16, color=C_CREE)
        self.play(FadeIn(sigue), run_time=0.4)
        self.wait(1.6)

        modelo = tag_junto(base, "modelo del histograma", DOWN, buff=0.3)
        self.play(FadeIn(modelo), run_time=0.5)
        self.wait(2.4)

        # --- un paso "normal": lo que termina en RANGE_HI_KEY y cuenta EQ_ROWS
        ejemplo = barras[IDX_EJEMPLO]
        marco = SurroundingRectangle(ejemplo, color=C_TITULO, buff=0.05,
                                     stroke_width=2.2)
        self.play(Create(marco), run_time=0.6)
        self.wait(0.6)
        et_hi = tag_junto(marco, "RANGE_HI_KEY", UP, buff=0.22)
        self.play(FadeIn(et_hi), run_time=0.5)
        self.wait(2.0)
        et_eq = tag_junto(et_hi, "EQ_ROWS", UP, buff=0.14)
        self.play(FadeIn(et_eq), run_time=0.5)
        self.wait(2.6)

        rot.mostrar(cifra_pie(f"{S.miles(N_PASOS)} pasos"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)
        rot.mostrar(dato_pie(f"maximo {S.miles(PASOS_MAX)} pasos"),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)

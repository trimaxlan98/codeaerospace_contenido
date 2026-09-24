class Clip1(Scene):
    """2.2.1 - Un indice no clona la tabla: guarda solo la llave de busqueda
    y un puntero a la fila real. A la izquierda el indice, delgado (cada
    hoja solo trae cliente y llave); a la derecha la tabla completa, con
    todas las columnas. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Un indice por cliente"), zona="arriba",
                    run_time=0.6)
        self.wait(1.0)

        q = S.codigo(["CREATE INDEX IX_cliente", "ON pedidos (id_cliente)"],
                     font_size=22)
        q.move_to(UP * 2.05)
        self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.7)
        self.wait(2.2)

        # --- izquierda: el indice, delgado ----------------------------------
        arbol = S.ArbolB(anchos=(1, 3, 7), ancho=4.4, alto=2.3, lado=0.32,
                         color=C_INDICE)
        arbol.move_to(LEFT * 3.4 + DOWN * 0.35)
        self.play(FadeIn(arbol.niveles[0]), run_time=0.4)
        self.play(Create(arbol.aristas[:3]), FadeIn(arbol.niveles[1]),
                  run_time=0.6)
        self.play(Create(arbol.aristas[3:]), FadeIn(arbol.niveles[2]),
                  run_time=0.7)
        tag_idx = tag_junto(arbol, "indice delgado", UP, buff=0.32,
                            color=C_INDICE)
        self.play(FadeIn(tag_idx), run_time=0.4)
        self.wait(1.8)

        hoja_idx = arbol.hojas[4]
        card_idx = S.pagina(1.3, 0.7, renglones=2, color=C_INDICE,
                            relleno=0.1, grosor=2.2)
        card_idx.move_to(LEFT * 3.4 + DOWN * 2.15)
        guia_idx = DashedLine(hoja_idx.get_bottom(), card_idx.get_top(),
                              dash_length=0.08, stroke_color=C_INDICE,
                              stroke_width=1.5)
        self.play(hoja_idx[0].animate.set_fill(C_INDICE, 0.7), run_time=0.3)
        self.play(Create(guia_idx), TransformFromCopy(hoja_idx, card_idx),
                  run_time=1.0)
        et_idx = tag_junto(card_idx, "cliente y llave", LEFT, buff=0.28,
                           color=C_INDICE)
        self.play(FadeIn(et_idx), run_time=0.4)
        self.wait(3.6)

        # --- derecha: la tabla completa, gruesa -----------------------------
        muro = S.MuroPaginas(columnas=14, filas=7, lado=0.26, sep=0.05,
                             color=C_TENUE, opacidad=0.16)
        muro.move_to(RIGHT * 3.4 + DOWN * 0.35)
        self.play(FadeIn(muro), run_time=0.8)
        tag_tab = tag_junto(muro, "tabla completa", UP, buff=0.32)
        self.play(FadeIn(tag_tab), run_time=0.4)
        self.wait(1.6)

        celda = muro.celda(3 * 14 + 12)
        card_tab = S.pagina(1.3, 0.7, renglones=6, color=C_TENUE,
                            relleno=0.1, grosor=2.2)
        card_tab.move_to(RIGHT * 3.4 + DOWN * 2.15)
        guia_tab = DashedLine(celda.get_bottom(), card_tab.get_top(),
                              dash_length=0.08, stroke_color=C_TENUE,
                              stroke_width=1.5)
        self.play(celda.animate.set_fill(C_TENUE, 0.7).set_stroke(C_TITULO),
                  run_time=0.3)
        self.play(Create(guia_tab), TransformFromCopy(celda, card_tab),
                  run_time=1.0)
        et_tab = tag_junto(card_tab, "todas las columnas", RIGHT, buff=0.28)
        self.play(FadeIn(et_tab), run_time=0.4)
        self.wait(11.0)

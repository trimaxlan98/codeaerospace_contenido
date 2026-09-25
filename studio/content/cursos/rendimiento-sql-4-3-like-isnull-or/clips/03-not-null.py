class Clip3(Scene):
    """4.3.3 - email NO admite nulos: mientras el ISNULL sigue escrito, el
    indice entero se ve amenazado (tenido de rojo, "parece un scan"). El
    ISNULL se desvanece del codigo (letra por letra) y el arbol vuelve a la
    normalidad: el optimizador lo quito solo. La ruta raiz-intermedio-hoja
    se enciende en verde nivel a nivel mientras el contador ambar sube de
    1 a 3, la misma medicion que un seek por email. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La columna NOT NULL"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- codigo grande, centrado arriba ---------------------------------
        q = S.codigo(["SELECT id_cliente", "FROM clientes",
                      "WHERE ISNULL(email, '')", "  = 'ana@correo.com'"],
                     font_size=22)
        q.move_to(UP * 1.7)
        self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.7)
        self.wait(1.2)

        marca = SurroundingRectangle(q.lineas[2][5:12], color=C_CREE,
                                     buff=0.05, stroke_width=2.4)
        self.play(Create(marca), run_time=0.5)
        self.wait(1.2)

        # --- el arbol del indice por email: GRANDE, a lo ancho --------------
        arbol = S.ArbolB(anchos=(1, 4, 12), ancho=9.4, alto=2.4, lado=0.36,
                         color=C_INDICE)
        arbol.move_to(DOWN * 1.05)
        todas_paginas = [p for fila in arbol.niveles for p in fila]
        self.play(FadeIn(arbol), run_time=0.8)
        self.wait(1.2)

        # --- la amenaza: con el ISNULL presente, PARECE un scan (sin cifra) -
        self.play(*[p[0].animate.set_fill(C_MALO, 0.4)
                    .set_stroke(C_MALO, opacity=0.75) for p in todas_paginas],
                  run_time=1.1)
        amenaza = tag_junto(arbol, "parece un scan", DOWN, buff=0.35,
                            color=C_MALO)
        self.play(FadeIn(amenaza), run_time=0.4)
        self.wait(3.2)

        # --- el ISNULL se desvanece del codigo (y el "email" se corre a la
        # izquierda para cerrar el hueco); el arbol vuelve a la normalidad --
        envoltura = q.lineas[2][5:12]      # "ISNULL("
        cola = q.lineas[2][17:21]          # ", ''" + ")"
        email_tok = q.lineas[2][12:17]     # "email"
        hueco = envoltura.get_width()
        self.play(FadeOut(marca), FadeOut(amenaza), run_time=0.4)
        self.play(envoltura.animate.set_opacity(0),
                  cola.animate.set_opacity(0),
                  email_tok.animate.shift(LEFT * hueco),
                  *[p[0].animate.set_fill(C_INDICE, 0.12)
                    .set_stroke(C_INDICE, opacity=0.5) for p in todas_paginas],
                  run_time=1.3)
        et_quita = tag_junto(arbol, "el optimizador lo quita", DOWN,
                             buff=0.35, color=C_CREE)
        self.play(FadeIn(et_quita), run_time=0.5)
        self.wait(2.2)

        # --- se enciende la ruta nivel a nivel; el contador ambar sube -----
        cont = Contador(0, rotulo="lecturas", font_size=36, digitos=1)
        cont.move_to(RIGHT * 5.35 + DOWN * 0.65)
        self.play(FadeIn(cont), run_time=0.4)
        ruta = arbol.ruta(6)
        for k, pag in enumerate(ruta):
            self.play(pag[0].animate.set_fill(C_BUENO, 0.85)
                      .set_stroke(C_BUENO), run_time=0.7)
            cont.fijar(k + 1)
            self.wait(1.0)
        self.wait(7.0)

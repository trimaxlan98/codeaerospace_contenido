class Clip2(Scene):
    """1.3.2 - Tres operadores, tres dibujos de paginas, a tamano grande y
    centrados: un Scan enciende el muro entero; un Seek baja tres paginas
    de un arbol; un Lookup baja las mismas tres Y vuelve a una pagina de
    datos aparte. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Scan, seek, lookup"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        cx1, cx2, cx3 = LEFT * 4.4, ORIGIN, RIGHT * 4.4
        y_centro = -0.05  # centro de la zona util (-2.7 a 2.6)

        # =====================================================================
        # 1) SCAN: el muro entero se enciende
        # =====================================================================
        muro = S.MuroPaginas(columnas=13, filas=10, lado=0.24, sep=0.05,
                             color=C_TENUE, opacidad=0.16)
        caja1 = S.operador("Scan", color=C_TITULO, ancho=2.6, font_size=24)
        et1 = tag_motor(lecturas(SCAN_PED), font_size=22)
        pila1 = VGroup(muro, caja1, et1)
        pila1.arrange(DOWN, buff=0.32)
        pila1.move_to(cx1 + UP * y_centro)

        self.play(FadeIn(caja1, shift=UP * 0.15), run_time=0.5)
        self.wait(0.3)
        self.play(FadeIn(muro), run_time=0.6)
        self.play(LaggedStart(*muro.encender(range(len(muro)), C_MALO, 0.85),
                              lag_ratio=0.015), run_time=1.5)
        self.play(FadeIn(et1), run_time=0.4)
        self.wait(2.6)

        # =====================================================================
        # 2) SEEK: tres paginas de un arbol, de arriba abajo
        # =====================================================================
        arbol1 = S.ArbolB(anchos=(1, 3, 6), ancho=3.6, alto=3.4, lado=0.32,
                          color=C_INDICE)
        caja2 = S.operador("Seek", color=C_TITULO, ancho=2.6, font_size=24)
        et2 = tag_motor(lecturas(PK_SEEK), font_size=22)
        pila2 = VGroup(arbol1, caja2, et2)
        pila2.arrange(DOWN, buff=0.32)
        pila2.move_to(cx2 + UP * y_centro)

        self.play(FadeIn(caja2, shift=UP * 0.15), run_time=0.5)
        self.wait(0.3)
        self.play(FadeIn(arbol1), run_time=0.6)
        ruta1 = arbol1.ruta(3)
        self.play(LaggedStart(*[p.marco.animate.set_fill(C_BUENO, 0.85)
                               .set_stroke(C_BUENO) for p in ruta1],
                              lag_ratio=0.35), run_time=1.1)
        self.play(FadeIn(et2), run_time=0.4)
        self.wait(2.6)

        # =====================================================================
        # 3) LOOKUP: las mismas tres paginas, MAS una que vuelve
        # =====================================================================
        arbol2 = S.ArbolB(anchos=(1, 3, 6), ancho=2.4, alto=3.2, lado=0.28,
                          color=C_INDICE)
        caja3 = S.operador("Lookup", color=C_TITULO, ancho=2.6, font_size=24)
        et3 = tag_motor(lecturas(C501_LOOKUP), font_size=22)

        # la pagina de datos aparte (heap) cuelga a la derecha de la hoja
        # mas a la derecha del arbol: ese hueco queda libre a proposito.
        arbol2.shift(LEFT * 0.55)
        ruta2 = arbol2.ruta(len(arbol2.hojas) - 1)
        hoja = ruta2[-1]
        heap = S.pagina(0.62, 0.9, renglones=4, color=C_MALO, relleno=0.2)
        heap.next_to(hoja, RIGHT, buff=0.55)
        vuelta = viaje_de_vuelta(hoja.get_right(), heap.get_left(), C_MALO,
                                 ancho=2.0)
        dibujo3 = VGroup(arbol2, heap, vuelta)
        pila3 = VGroup(dibujo3, caja3, et3)
        pila3.arrange(DOWN, buff=0.32)
        pila3.move_to(cx3 + UP * y_centro)

        self.play(FadeIn(caja3, shift=UP * 0.15), run_time=0.5)
        self.wait(0.3)
        self.play(FadeIn(arbol2), run_time=0.6)
        self.play(LaggedStart(*[p.marco.animate.set_fill(C_BUENO, 0.85)
                               .set_stroke(C_BUENO) for p in ruta2],
                              lag_ratio=0.35), run_time=1.0)
        self.play(FadeIn(heap), run_time=0.4)
        self.play(Create(vuelta), run_time=0.9)
        self.play(FadeIn(et3), run_time=0.4)
        self.wait(12.5)

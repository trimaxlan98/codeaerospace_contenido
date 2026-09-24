class Clip3(Scene):
    """2.3.3 - El mayorista tambien gana: el muro entero (scan) contra un
    tramo CONTIGUO de hojas del indice cubriente (el resto de la columna
    queda apagado: son otros clientes). Los dos contadores quedan a la
    MISMA altura, lejos del carril inferior. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El mayorista tambien"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        COMMON_Y = 2.35  # altura comun de los dos contadores (bajo cada dibujo)

        # --- izquierda: el muro entero (heap sin orden) -------------------
        muro = S.MuroPaginas(columnas=16, filas=10, lado=0.18, sep=0.05,
                             color=C_TENUE, opacidad=0.14)
        muro.move_to(LEFT * 3.7 + UP * 0.3)
        nom_muro = Text("pedidos", font_size=22, color=C_TITULO)
        nom_muro.next_to(muro, UP, buff=0.2)
        self.play(FadeIn(nom_muro), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in muro],
                              lag_ratio=0.006), run_time=1.8)
        self.wait(0.4)

        cont_muro = Contador(0, rotulo="lecturas", font_size=30, digitos=5)
        cont_muro.move_to(LEFT * 3.7 + DOWN * COMMON_Y)
        self.play(FadeIn(cont_muro), run_time=0.4)
        cont_muro.anim(self, M["c1_scan"], run_time=3.0,
                       extra=[LaggedStart(*muro.encender(range(len(muro)), C_MALO, 0.5),
                                          lag_ratio=0.0016)])
        et_muro = tag_junto(cont_muro, "muro entero", RIGHT, buff=0.5,
                            color=C_MALO)
        self.play(FadeIn(et_muro), run_time=0.4)
        self.wait(1.0)

        # --- derecha: la columna de hojas del indice, EN ORDEN, grandes ---
        col = S.MuroPaginas(columnas=1, filas=6, lado=0.5, sep=0.07,
                            color=C_TENUE, opacidad=0.14)
        col.move_to(RIGHT * 3.3 + UP * 0.3)
        nom_col = Text("indice cubriente", font_size=20, color=C_TITULO)
        nom_col.next_to(col, UP, buff=0.2)
        self.play(FadeIn(nom_col), run_time=0.4)
        self.play(FadeIn(col, shift=LEFT * 0.1), run_time=0.6)
        self.wait(0.4)

        tramo = range(1, 4)
        cont_col = Contador(0, rotulo="lecturas", font_size=30, digitos=3)
        cont_col.move_to(RIGHT * 3.3 + DOWN * COMMON_Y)
        self.play(FadeIn(cont_col), run_time=0.4)
        cont_col.anim(self, M["c1_cubriente"], run_time=0.8,
                     extra=[LaggedStart(*col.encender(tramo, C_BUENO, 0.85),
                                        lag_ratio=0.05)])
        et_col = tag_junto(col[tramo[0]], "tramo contiguo", LEFT, buff=0.3,
                           color=C_BUENO)
        self.play(FadeIn(et_col), run_time=0.4)
        et_resto = tag_junto(col[0], "otros clientes", LEFT, buff=0.3,
                             color=C_TENUE)
        self.play(FadeIn(et_resto), run_time=0.4)
        self.wait(2.6)

        # --- lo que hace posible el tramo corto: hojas densas -------------
        rot.mostrar(cifra_pie(f"{round(FILAS_POR_HOJA_C1)} filas por hoja"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"{S.miles(HOJAS_C1)} hojas leidas"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        razon = S.razon(M["c1_scan"], M["c1_cubriente"])
        rot.mostrar(cifra_pie(f"{razon:.0f}x menos lecturas"), zona="abajo",
                    run_time=0.5)
        self.wait(6.0)

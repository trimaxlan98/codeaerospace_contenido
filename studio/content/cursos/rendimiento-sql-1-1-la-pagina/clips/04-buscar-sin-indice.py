class Clip4(Scene):
    """1.1.4 - Buscar por cliente, una columna sin indice: el motor abre el
    muro entero para quedarse con 191 filas. Cierre. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Buscar sin indice"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        q = S.codigo(["SELECT id_pedido, total", "FROM pedidos",
                      "WHERE id_cliente = 501"], font_size=20)
        q.to_corner(UL, buff=0.6).shift(DOWN * 0.8)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        linea = q.lineas[2]
        marca = SurroundingRectangle(linea, color=C_MALO, buff=0.07,
                                     stroke_width=2.4)
        self.play(Create(marca), run_time=0.5)
        sin = tag_junto(q, "sin indice", DOWN, buff=0.18, color=C_MALO)
        self.play(FadeIn(sin), run_time=0.4)
        self.wait(1.8)

        cols, fils = 24, 12
        muro = S.MuroPaginas(columnas=cols, filas=fils, lado=0.17, sep=0.05,
                             color=C_TENUE, opacidad=0.14)
        muro.move_to(RIGHT * 2.9 + DOWN * 0.2)
        self.play(FadeIn(muro), run_time=0.8)
        self.wait(0.6)

        cont = Contador(0, rotulo="lecturas", font_size=40, digitos=6)
        cont.next_to(sin, DOWN, buff=0.7).align_to(q, LEFT)
        self.play(FadeIn(cont), run_time=0.4)
        cont.anim(self, M["scan_pedidos"], run_time=4.5,
                  extra=[LaggedStart(*muro.encender(range(len(muro)), C_MALO, 0.5),
                                     lag_ratio=0.004)])
        self.wait(1.0)
        rot.mostrar(motor_pie(lecturas(M["scan_pedidos"])), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- lo que servia: 191 filas, que caben en tres paginas --------
        caben = math.ceil(C501 / FPP)
        self.play(muro.animate.set_fill(C_TENUE, 0.1).set_stroke(C_TENUE, opacity=0.4),
                  run_time=0.8)
        tres = VGroup(*[S.pagina(0.5, 0.66, renglones=4, color=C_BUENO, relleno=0.3)
                        for _ in range(caben)]).arrange(RIGHT, buff=0.18)
        tres.next_to(cont, DOWN, buff=0.6).align_to(q, LEFT)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in tres],
                              lag_ratio=0.3), run_time=1.0)
        et = tag_junto(tres, f"caben en {caben} paginas", RIGHT, buff=0.3,
                       color=C_BUENO)
        self.play(FadeIn(et), run_time=0.4)
        rot.mostrar(cifra_pie(f"{C501} filas utiles"), zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"{PAG_POR_FILA:.0f} paginas por fila util"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

        cierre_leccion(self, rot, "El motor no lee filas: lee paginas.",
                       "Optimizar es leer menos.", q, marca, sin, muro, cont, tres, et)

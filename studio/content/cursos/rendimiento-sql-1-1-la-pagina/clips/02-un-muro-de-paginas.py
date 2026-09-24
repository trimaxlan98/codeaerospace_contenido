class Clip2(Scene):
    """1.1.2 - La tabla de pedidos se parte en paginas de 8 KB: un muro.
    Una pagina se amplia: sus filas. El contador da las paginas de la
    tabla segun el motor. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Un muro de paginas"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        cols, fils = 30, 12
        muro = S.MuroPaginas(columnas=cols, filas=fils, lado=0.17, sep=0.05,
                             color=C_TENUE, opacidad=0.14)
        muro.move_to(LEFT * 2.6 + DOWN * 0.2)
        nom = Text("pedidos", font_size=26, color=C_TITULO)
        nom.next_to(muro, UP, buff=0.22).align_to(muro, LEFT)
        self.play(FadeIn(nom), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in muro],
                              lag_ratio=0.004), run_time=2.6)
        por_celda = PAG_PED / len(muro)
        esc = tag_hud(f"1 cuadro = {por_celda:.0f} paginas", font_size=18)
        esc.next_to(muro, DOWN, buff=0.22).align_to(muro, LEFT)
        self.play(FadeIn(esc), run_time=0.4)
        self.wait(2.2)

        # --- una pagina ampliada -----------------------------------------
        elegida = muro.celda(fils // 2 * cols + cols - 1)
        self.play(elegida.animate.set_fill(C_INDICE, 0.9).set_stroke(C_INDICE),
                  run_time=0.5)
        grande = S.pagina(2.2, 2.9, renglones=9, color=C_INDICE, relleno=0.08,
                          grosor=2.4)
        grande.move_to(RIGHT * 4.3 + UP * 0.35)
        guia = DashedLine(elegida.get_right(), grande.get_left(),
                          dash_length=0.1, stroke_color=C_INDICE,
                          stroke_width=1.6)
        self.play(Create(guia), TransformFromCopy(elegida, grande), run_time=1.3)
        kb = Text("8 KB  · dato", font=FUENTE_HUD, font_size=20, color=C_DATO)
        kb.next_to(grande, UP, buff=0.18)
        self.play(FadeIn(kb), run_time=0.4)
        self.wait(2.0)
        self.play(LaggedStart(*[Indicate(r, color=C_TITULO, scale_factor=1.05)
                                for r in grande[2]], lag_ratio=0.12),
                  run_time=2.0)
        fpp = tag_hud(f"{FPP:.1f} filas por pagina", font_size=20)
        fpp.next_to(grande, DOWN, buff=0.22)
        self.play(FadeIn(fpp), run_time=0.5)
        self.wait(2.8)

        # --- el contador: paginas de la tabla ----------------------------
        cont = Contador(0, rotulo="paginas", font_size=36, digitos=6)
        cont.next_to(fpp, DOWN, buff=0.45)
        self.play(FadeIn(cont), run_time=0.4)
        cont.anim(self, PAG_PED, run_time=3.0,
                  extra=[LaggedStart(*muro.encender(range(len(muro)), C_MOTOR, 0.55),
                                     lag_ratio=0.003)])
        self.wait(1.2)
        rot.mostrar(motor_pie(f"{S.miles(PAG_PED)} paginas de 8 KB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)
        rot.mostrar(cifra_pie(f"{S.miles(FILAS_PED)} filas"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

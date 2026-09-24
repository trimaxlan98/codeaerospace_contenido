class Clip3(Scene):
    """2.2.3 - El mismo plan no sirve para todos: si el mayorista (cliente 1)
    usara el mismo seek + lookup, el modelo dispara las lecturas por las
    nubes. El optimizador no lo intenta: prefiere el scan completo, que aqui
    sale mas barato. Duelo en escala logaritmica. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El mayorista"), zona="arriba", run_time=0.6)
        self.wait(0.8)

        tarjeta = RoundedRectangle(width=2.4, height=0.7, corner_radius=0.1,
                                   stroke_color=C_TITULO, stroke_width=2,
                                   fill_color=C_TITULO, fill_opacity=0.06)
        tarjeta.move_to(UP * 2.0)
        nom = Text("cliente 1", font_size=24, color=C_TITULO)
        nom.move_to(tarjeta)
        self.play(FadeIn(tarjeta), FadeIn(nom), run_time=0.6)
        cif_c1 = tag_hud(f"{S.miles(C1)} filas", font_size=20)
        cif_c1.next_to(tarjeta, DOWN, buff=0.22)
        self.play(FadeIn(cif_c1), run_time=0.4)
        self.wait(2.0)

        # --- duelo: si usara el mismo plan (lookup) contra el scan real ------
        largo = 7.2
        maximo = MODELO_1
        base_x = LEFT * 3.8

        bar_rojo = S.barra_lecturas(MODELO_1, maximo, largo=largo, alto=0.55,
                                    color=C_MALO, log=True)
        bar_rojo.shift(base_x + UP * 0.35)
        bar_verde = S.barra_lecturas(M["c1_scan"], maximo, largo=largo,
                                     alto=0.55, color=C_BUENO, log=True)
        bar_verde.shift(base_x + DOWN * 1.45)

        base = Line(base_x + UP * 1.0, base_x + DOWN * 1.9,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.6)

        lab_r = tag_junto(bar_rojo, "camino del lookup", LEFT, buff=0.3,
                          color=C_MALO)
        self.play(GrowFromEdge(bar_rojo, LEFT), FadeIn(lab_r), run_time=0.9)
        tag_r = tag_hud(f"modelo: {S.miles(MODELO_1)}", font_size=19,
                        color=C_CALCULO)
        tag_r.next_to(bar_rojo, RIGHT, buff=0.22)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(1.6)

        lab_v = tag_junto(bar_verde, "el optimizador elige", LEFT, buff=0.3,
                          color=C_BUENO)
        self.play(GrowFromEdge(bar_verde, LEFT), FadeIn(lab_v), run_time=0.9)
        tag_v = tag_motor(lecturas(M["c1_scan"]))
        tag_v.next_to(bar_verde, RIGHT, buff=0.22)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(3.2)

        razon = S.razon(MODELO_1, M["c1_scan"])
        rot.mostrar(cifra_pie(f"{S.miles(round(razon))}x menos lecturas"),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(bar_rojo, color=C_MALO, scale_factor=1.03),
                  Indicate(bar_verde, color=C_BUENO, scale_factor=1.08),
                  run_time=1.0)
        self.wait(14.0)

class Clip2(Scene):
    """1.2.2 - Muchos planes, un costo: el optimizador arma varios planes
    candidatos con un costo estimado (violeta, sin cifra: nadie midio
    todavia nada) y elige el mas barato. Para esta consulta en concreto,
    los dos candidatos reales son "scan" y "seek + lookup", con sus
    lecturas medidas por el motor (ambar). (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Muchos planes, un costo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        q = S.codigo(["SELECT id_pedido, total", "FROM pedidos",
                      "WHERE id_cliente = 501"], font_size=20)
        q.to_corner(UL, buff=0.6).shift(DOWN * 0.7)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(1.2)

        # --- tres planes candidatos: costo estimado, SIN cifra -------------
        alturas = (2.3, 1.55, 0.95)
        candidatos = VGroup()
        for i, h in enumerate(alturas):
            caja = S.operador(f"plan {chr(65 + i)}", color=C_TENUE, ancho=1.9,
                              alto=0.7, font_size=20)
            caja.texto.set_color(C_TITULO)
            barra = Rectangle(width=0.5, height=h, stroke_width=0,
                              fill_color=C_CREE, fill_opacity=0.85)
            barra.next_to(caja, UP, buff=0.18, aligned_edge=ORIGIN)
            candidatos.add(VGroup(barra, caja))
        candidatos.arrange(RIGHT, buff=1.0, aligned_edge=DOWN)
        candidatos.move_to(RIGHT * 2.6 + DOWN * 0.2)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in candidatos],
                              lag_ratio=0.3), run_time=1.4)
        et_costo = tag_junto(candidatos, "costo estimado", UP, buff=0.3,
                             color=C_CREE)
        self.play(FadeIn(et_costo), run_time=0.4)
        self.wait(3.8)

        # --- elige el mas barato --------------------------------------------
        barato = candidatos[2]
        otros = VGroup(candidatos[0], candidatos[1])
        marco = SurroundingRectangle(barato, color=C_BUENO, buff=0.15,
                                     stroke_width=2.6)
        self.play(otros.animate.set_opacity(0.28), Create(marco), run_time=0.9)
        et_elige = tag_junto(marco, "elegido", DOWN, buff=0.2, color=C_BUENO)
        self.play(FadeIn(et_elige), run_time=0.4)
        self.wait(3.8)

        self.play(FadeOut(candidatos), FadeOut(et_costo), FadeOut(marco),
                  FadeOut(et_elige), run_time=0.7)

        # --- para ESTA consulta: scan contra seek + lookup, ya medidos -----
        scan_barra = S.barra_lecturas(M["scan_pedidos"], M["scan_pedidos"],
                                      largo=4.6, alto=0.42, color=C_MALO)
        lookup_barra = S.barra_lecturas(M["c501_lookup"], M["scan_pedidos"],
                                        largo=4.6, alto=0.42, color=C_BUENO)
        duelo = VGroup(scan_barra, lookup_barra).arrange(DOWN, buff=0.55,
                                                          aligned_edge=LEFT)
        duelo.move_to(LEFT * 0.4 + DOWN * 0.4)
        nom_scan = tag_junto(scan_barra, "scan", LEFT, buff=0.3, color=C_MALO)
        nom_lookup = tag_junto(lookup_barra, "seek + lookup", LEFT, buff=0.3,
                               color=C_BUENO)
        et_log = tag_junto(duelo, "escala logaritmica", UP, buff=0.4,
                           color=C_DATO)
        self.play(FadeIn(nom_scan), FadeIn(et_log),
                  GrowFromEdge(scan_barra, LEFT), run_time=0.8)
        cif_scan = tag_motor(lecturas(M["scan_pedidos"]))
        cif_scan.next_to(scan_barra, RIGHT, buff=0.25)
        self.play(FadeIn(cif_scan), run_time=0.4)
        self.wait(1.0)
        self.play(FadeIn(nom_lookup), GrowFromEdge(lookup_barra, LEFT),
                  run_time=0.8)
        cif_lookup = tag_motor(lecturas(M["c501_lookup"]))
        cif_lookup.next_to(lookup_barra, RIGHT, buff=0.25)
        self.play(FadeIn(cif_lookup), run_time=0.4)
        self.wait(1.2)

        marco2 = SurroundingRectangle(VGroup(nom_lookup, lookup_barra,
                                             cif_lookup), color=C_BUENO,
                                      buff=0.15, stroke_width=2.4)
        self.play(Create(marco2), run_time=0.6)
        et_gana = tag_junto(marco2, "gana el mas barato", DOWN, buff=0.22,
                            color=C_BUENO)
        self.play(FadeIn(et_gana), run_time=0.4)
        self.wait(8.0)

class Clip4(Scene):
    """2.2.4 - Grafica hecha a mano: lecturas del lookup (recta, 3 por fila)
    contra el scan (horizontal). Se cruzan muy pronto, en menos del 1% de la
    tabla. El 501 cae muy a la izquierda, sobre la propia recta; el
    mayorista queda tan fuera del cuadro que sale por una flecha. Cierre de
    la leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Punto de inflexion"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        caja = (-5.5, 5.5, -2.35, 2.15)
        rx, ry = (0, 12000), (0, 38000)
        cua = Cuadro(caja, rx, ry)

        eje_x = cua.suelo(y=0, color=C_TENUE)
        eje_y = Line(cua.p(0, 0), cua.p(0, ry[1]), stroke_color=C_TENUE,
                    stroke_width=2)
        self.play(Create(eje_x), Create(eje_y), run_time=0.7)
        rot_x = tag_junto(eje_x, "filas del cliente", DOWN, buff=0.3)
        rot_y = tag_junto(eje_y, "lecturas", UP, buff=0.25)
        self.play(FadeIn(rot_x), FadeIn(rot_y), run_time=0.5)
        self.wait(1.2)

        marcas = VGroup()
        for v in (4000, 8000, 12000):
            t = tag_hud(S.miles(v), font_size=16, color=C_TENUE)
            t.next_to(cua.p(v, 0), DOWN, buff=0.14)
            marcas.add(t)
        self.play(FadeIn(marcas), run_time=0.5)
        self.wait(1.4)

        # --- la recta del lookup: 3 lecturas por fila ---------------------------
        y0, y1 = S.lecturas_seek_lookup(rx[0]), S.lecturas_seek_lookup(rx[1])
        recta = cua.serie([rx[0], rx[1]], [y0, y1], C_CALCULO, ancho=4)
        self.play(Create(recta), run_time=1.2)
        et_look = tag_junto(recta.point_from_proportion(0.24), "lookup", UL,
                            buff=0.18, color=C_CALCULO)
        self.play(FadeIn(et_look), run_time=0.4)
        self.wait(1.4)

        # --- la horizontal del scan -----------------------------------------------
        scan_y = M["scan_pedidos"]
        horiz = cua.serie([rx[0], rx[1]], [scan_y, scan_y], C_MOTOR, ancho=4)
        self.play(Create(horiz), run_time=1.0)
        et_scan = tag_junto(horiz.point_from_proportion(0.85), "scan", DR,
                            buff=0.18, color=C_MOTOR)
        self.play(FadeIn(et_scan), run_time=0.4)
        self.wait(1.6)

        # --- el cruce -----------------------------------------------------------------
        px, py = PUNTO_FILAS, scan_y
        punto = Dot(cua.p(px, py), radius=0.09, color=C_CALCULO)
        guia_v = DashedLine(cua.p(px, ry[0]), cua.p(px, py), dash_length=0.08,
                            stroke_color=C_CALCULO, stroke_width=1.4)
        guia_h = DashedLine(cua.p(rx[0], py), cua.p(px, py), dash_length=0.08,
                            stroke_color=C_CALCULO, stroke_width=1.4)
        self.play(Create(guia_v), Create(guia_h), run_time=0.7)
        self.play(FadeIn(punto, scale=0.5), run_time=0.4)
        et_cruce = tag_hud(f"{S.miles(PUNTO_FILAS)} filas", font_size=18,
                           color=C_CALCULO)
        et_cruce.next_to(punto, DR, buff=0.32)
        self.play(FadeIn(et_cruce), run_time=0.5)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"{fmt(PUNTO_PCT, 2)} % de la tabla"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- el 501: muy a la izquierda, sobre la propia recta -------------------
        p501 = Dot(cua.p(C501, MODELO_501), radius=0.08, color=C_BUENO)
        et_501 = tag_junto(p501, "501", UR, buff=0.15, color=C_BUENO)
        self.play(FadeIn(p501, scale=0.5), FadeIn(et_501), run_time=0.6)
        self.wait(1.8)

        # --- el 1: tan fuera del cuadro que sale por una flecha -------------------
        borde = cua.p(rx[1], y1)
        flecha1 = Arrow(borde, borde + RIGHT * 0.4 + UP * 0.3, buff=0.02,
                        stroke_width=3.2, color=C_TITULO,
                        max_tip_length_to_length_ratio=0.4)
        et_c1 = tag_junto(flecha1, "cliente 1", DOWN, buff=0.18)
        cif_c1 = tag_hud(f"{S.miles(C1)} filas", font_size=17, color=C_CALCULO)
        cif_c1.next_to(et_c1, DOWN, buff=0.12)
        VGroup(et_c1, cif_c1).move_to(RIGHT * 4.6 + UP * 2.65)
        self.play(Create(flecha1), FadeIn(et_c1), FadeIn(cif_c1), run_time=0.8)
        self.wait(3.0)

        grupo = VGroup(eje_x, eje_y, rot_x, rot_y, marcas, recta, et_look,
                       horiz, et_scan, guia_v, guia_h, punto, et_cruce, p501,
                       et_501, flecha1, et_c1, cif_c1)
        cierre_leccion(self, rot, "Un lookup es barato.",
                       "Ciento cincuenta mil, no.", grupo, espera=5.5)

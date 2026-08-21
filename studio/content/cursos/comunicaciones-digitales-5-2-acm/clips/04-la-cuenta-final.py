class Clip4(Scene):
    """5.2.4 - La cuenta final: bits_acm vs bits_fijo (~2.4x MEDIDO), el
    mismo outage de 20 min para los dos -- el ACM no lo paga extra.
    Cierre de leccion. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La cuenta final")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: dos disenos, el mismo dia de lluvia --------------------
        rot.mostrar(pie_curso("Sumado minuto a minuto, en el MISMO dia de "
                              "lluvia: dos disenos, dos totales."),
                    zona="abajo", run_time=0.5)
        base_y = -1.7
        escala = 3.8 / BARRA_TOPE
        xs = [-2.2, 2.2]
        ancho_barra = 1.6
        eje = Line([-4.4, base_y, 0], [4.4, base_y, 0], color=C_EJE,
                  stroke_width=2.0)

        def hacer_barra(nombre, v, x, color):
            h = v * escala
            b = Rectangle(width=ancho_barra, height=h, stroke_color=color,
                         fill_color=color, fill_opacity=0.55,
                         stroke_width=2.0)
            b.move_to([x, base_y + h / 2, 0])
            et = tag_hud(nombre, font_size=17, color=C_TENUE)
            et.next_to(b, DOWN, buff=0.15)
            cif = tag_hud(f"{fmt(v, 0)}", font_size=22, color=color)
            cif.next_to(b, UP, buff=0.1)
            return VGroup(b, et, cif)

        self.play(FadeIn(eje), run_time=0.5)
        b_fijo = hacer_barra("fijo (QPSK 1/2)", BITS_FIJO, xs[0], C_BIT)
        b_acm = hacer_barra("ACM", BITS_ACM, xs[1], C_TECHO)
        self.play(GrowFromEdge(b_fijo[0], DOWN), FadeIn(b_fijo[1]),
                  FadeIn(b_fijo[2]), run_time=1.0)
        self.wait(1.6)
        self.play(GrowFromEdge(b_acm[0], DOWN), FadeIn(b_acm[1]),
                  FadeIn(b_acm[2]), run_time=1.0)
        unidad = tag_junto(eje, "unidades-simbolo acumuladas", font_size=17,
                           direccion=DOWN, buff=0.55)
        self.play(FadeIn(unidad), run_time=0.4)
        self.wait(3.4)

        # --- momento: el factor medido ----------------------------------------
        rot.mostrar(pie_curso("El ACM entrega mas del doble de datos el "
                              "mismo dia, con el mismo espectro."),
                    zona="abajo", run_time=0.5)
        factor = tag_hud(f"{fmt(BITS_ACM, 0)} / {fmt(BITS_FIJO, 0)} = "
                         f"x{fmt(FACTOR_ACM, 1)}", font_size=22,
                         color=C_CIFRA)
        # Encima de la cifra "527" que ya corona la barra ACM (bar mas alta
        # llega a y~2.1 con su propia cifra): despejado del titulo tambien.
        factor.move_to(UP * 2.75)
        self.play(FadeIn(factor, shift=0.15 * UP), run_time=0.6)
        self.wait(4.8)

        # --- momento: el mismo corte, sin pagar extra --------------------------
        rot.mostrar(pie_curso("Y el corte: exactamente el mismo. El ACM "
                              "no paga outage extra por adaptarse."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(
            tag_hud(f"outage ACM = {fmt(float(OUTAGE_ACM), 0)} min",
                   color=C_RUIDO),
            tag_hud(f"outage fijo = {fmt(float(OUTAGE_FIJO), 0)} min",
                   color=C_RUIDO))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(4.8)

        # --- momento: DVB-S2 lo hace en cada lluvia real ------------------------
        rot.mostrar(pie_curso("DVB-S2 hace exactamente esto en cada "
                              "lluvia real, en cada enlace con una "
                              "sonda."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- cierre de leccion --------------------------------------------------
        cierre_leccion(
            self, rot,
            "El enlace de antes aguantaba el clima.",
            "El de ahora lo aprovecha.",
            "Siguiente leccion: la luz que cruza el vacio.",
            eje, b_fijo, b_acm, unidad, factor, panel)

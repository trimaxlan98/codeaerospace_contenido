class Clip2(Scene):
    """2.1.2 - La cascada de Friis: las mismas tres cajas (CABLE, LNA,
    RECEPTOR) en distinto orden dan distinta NF total: 1.04 dB con el LNA
    primero, 3.91 dB con el cable primero, 9.00 dB sin LNA. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La cascada de Friis"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        ancho_caja, alto_caja = 2.3, 0.85

        def caja(nombre, color):
            return S.bloque(nombre, ancho=ancho_caja, alto=alto_caja,
                            color=color, color_texto=C_TITULO, tamano=21,
                            opacidad_relleno=0.1)

        def etiquetas(par):
            g, nf = par
            g_lbl = tag_dato(f"{fmt(g, 1)} dB gan", font_size=16)
            nf_lbl = tag_dato(f"NF {fmt(nf, 1)} dB", font_size=16)
            return VGroup(g_lbl, nf_lbl).arrange(DOWN, buff=0.08)

        b_lna, b_cable, b_recep = (caja("LNA", C_TENUE), caja("CABLE", C_TENUE),
                                   caja("RECEPTOR", C_TENUE))
        l_lna, l_cable, l_recep = (etiquetas(S.LNA), etiquetas(S.CABLE),
                                   etiquetas(S.RECEPTOR))

        fila = VGroup(b_lna, b_cable, b_recep).arrange(RIGHT, buff=0.9)
        fila.move_to(UP * 1.55)
        for b, l in ((b_lna, l_lna), (b_cable, l_cable), (b_recep, l_recep)):
            l.next_to(b, DOWN, buff=0.16)

        fl = VGroup(S.conectar(b_lna, b_cable, color=C_TENUE, grosor=2.2),
                   S.conectar(b_cable, b_recep, color=C_TENUE, grosor=2.2))

        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.15)
                                for m in (b_lna, b_cable, b_recep)],
                              lag_ratio=0.3), run_time=1.4)
        self.play(LaggedStart(*[FadeIn(m)
                                for m in (l_lna, l_cable, l_recep)],
                              lag_ratio=0.25), run_time=1.0)
        self.play(Create(fl), run_time=0.7)
        self.wait(2.6)

        # --- barras de NF total medida, tres casos -------------------------
        base_y, top_y = -2.35, -0.35
        escala = (top_y - base_y) / NF_SIN
        ancho_barra = 1.7
        xs = [-3.1, 0.0, 3.1]

        def barra(x, valor):
            h = max(escala * valor, 0.05)
            r = Rectangle(width=ancho_barra, height=h, stroke_width=0,
                         fill_color=C_CALCULO, fill_opacity=0.85)
            r.move_to(np.array([x, base_y + h / 2, 0.0]))
            return r

        # caso A: LNA primero (orden ya en pantalla) ------------------------
        barra1 = barra(xs[0], NF_ANT)
        cif1 = tag_hud(f"{fmt(NF_ANT, 2)} dB", font_size=20)
        cif1.next_to(barra1, UP, buff=0.14)
        caso1 = tag_junto(barra1, "LNA primero", DOWN, buff=0.16,
                          font_size=18)
        self.play(GrowFromEdge(barra1, DOWN), FadeIn(cif1), FadeIn(caso1),
                  run_time=1.0)
        rot.mostrar(cifra_pie(f"LNA primero: {fmt(NF_ANT, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # caso B: se reordena - el cable pasa primero (arco, sin choque) ----
        # la cifra vieja se apaga JUSTO cuando el orden deja de corresponder
        rot.limpiar(zona="abajo", run_time=0.3)
        # las etiquetas se ocultan ANTES del arco: moverlas junto a la caja
        # (grupo caja+etiqueta) hace que el arco cruce la etiqueta de la
        # otra caja a mitad de camino. Se arquean solo las cajas (compactas)
        # y las etiquetas reaparecen YA en su sitio nuevo.
        self.play(FadeOut(l_lna), FadeOut(l_cable), run_time=0.3)
        self.play(CyclicReplace(b_lna, b_cable, path_arc=120 * DEGREES),
                  run_time=1.5)
        l_lna.next_to(b_lna, DOWN, buff=0.16)
        l_cable.next_to(b_cable, DOWN, buff=0.16)
        fl2 = VGroup(S.conectar(b_cable, b_lna, color=C_TENUE, grosor=2.2),
                    S.conectar(b_lna, b_recep, color=C_TENUE, grosor=2.2))
        self.play(Transform(fl, fl2), FadeIn(l_lna), FadeIn(l_cable),
                  run_time=0.6)
        self.wait(1.4)

        barra2 = barra(xs[1], NF_ESC)
        cif2 = tag_hud(f"{fmt(NF_ESC, 2)} dB", font_size=20)
        cif2.next_to(barra2, UP, buff=0.14)
        caso2 = tag_junto(barra2, "cable primero", DOWN, buff=0.16,
                          font_size=18)
        self.play(GrowFromEdge(barra2, DOWN), FadeIn(cif2), FadeIn(caso2),
                  run_time=1.0)
        rot.mostrar(cifra_pie(f"cable primero: {fmt(NF_ESC, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # caso C: se quita el LNA --------------------------------------------
        rot.limpiar(zona="abajo", run_time=0.3)
        self.play(FadeOut(b_lna), FadeOut(l_lna), FadeOut(fl), run_time=0.7)
        fl3 = S.conectar(b_cable, b_recep, color=C_TENUE, grosor=2.2)
        self.play(Create(fl3), run_time=0.5)
        self.wait(1.2)

        barra3 = barra(xs[2], NF_SIN)
        cif3 = tag_hud(f"{fmt(NF_SIN, 2)} dB", font_size=20)
        cif3.next_to(barra3, UP, buff=0.14)
        caso3 = tag_junto(barra3, "sin LNA", DOWN, buff=0.16, font_size=18)
        self.play(GrowFromEdge(barra3, DOWN), FadeIn(cif3), FadeIn(caso3),
                  run_time=1.0)
        rot.mostrar(cifra_pie(f"sin LNA: {fmt(NF_SIN, 2)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

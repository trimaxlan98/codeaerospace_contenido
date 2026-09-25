class Clip4(Scene):
    """5.1.4 - Las estadisticas no se releen en cada consulta: se actualizan
    solas cuando cambian suficientes filas. El umbral NUEVO (RAIZ(1000n))
    llega mucho antes que el umbral VIEJO (500 + 20% de n): se dibuja como
    una barra que crece (gris, no es lectura del motor) y cruza dos marcas
    en escala LINEAL (la diferencia real se ve, no se comprime). Cierre de
    la leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Cuando se actualizan las estadisticas"),
                    zona="arriba", run_time=0.6)
        self.wait(0.7)

        maximo = UMBRAL_VIEJO * 1.15
        x0, x1 = -5.0, 5.0

        def x_de(v):
            return x0 + (x1 - x0) * (v / maximo)

        linea = Line([x0, -1.6, 0], [x1, -1.6, 0], stroke_color=C_TENUE,
                    stroke_width=2)
        self.play(Create(linea), run_time=0.6)
        et_linea = tag_junto(linea, "filas modificadas", DOWN, buff=0.24)
        self.play(FadeIn(et_linea), run_time=0.4)
        self.wait(1.4)

        xn, xv = x_de(UMBRAL_NUEVO), x_de(UMBRAL_VIEJO)
        marca_n = Line([xn, -1.85, 0], [xn, -1.35, 0], stroke_color=C_CALCULO,
                      stroke_width=3)
        marca_v = Line([xv, -1.85, 0], [xv, -1.35, 0], stroke_color=C_CALCULO,
                      stroke_width=3)
        self.play(Create(marca_n), Create(marca_v), run_time=0.6)

        form_n = MathTex(r"\sqrt{1000n}", font_size=30, color=C_CALCULO)
        form_n.next_to(marca_n, UP, buff=0.55)
        cif_n = tag_hud(f"{S.miles(UMBRAL_NUEVO)} cambios", font_size=22,
                        color=C_CALCULO)
        cif_n.next_to(marca_n, UP, buff=0.12)
        self.play(FadeIn(form_n), FadeIn(cif_n), run_time=0.6)
        self.wait(1.6)

        form_v = MathTex(r"500 + 0.2n", font_size=30, color=C_CALCULO)
        form_v.next_to(marca_v, UP, buff=0.55)
        cif_v = tag_hud(f"{S.miles(UMBRAL_VIEJO)} cambios", font_size=22,
                        color=C_CALCULO)
        cif_v.next_to(marca_v, UP, buff=0.12)
        self.play(FadeIn(form_v), FadeIn(cif_v), run_time=0.6)
        self.wait(1.8)

        etq_n = tag_junto(marca_n, "nuevo", DOWN, buff=0.18, color=C_CALCULO)
        etq_v = tag_junto(marca_v, "viejo", DOWN, buff=0.18, color=C_CALCULO)
        self.play(FadeIn(etq_n), FadeIn(etq_v), run_time=0.5)
        self.wait(1.2)

        # --- la barra de cambios: gris, NO es lectura del motor ------------
        relleno = Rectangle(width=0.001, height=0.5, stroke_width=0,
                            fill_color=C_TENUE, fill_opacity=0.85)
        relleno.move_to([x0, -1.6, 0], aligned_edge=LEFT)
        self.add(relleno)
        vt = ValueTracker(x0)
        relleno.add_updater(
            lambda m: m.become(Rectangle(
                width=max(vt.get_value() - x0, 0.001), height=0.5,
                stroke_width=0, fill_color=C_TENUE, fill_opacity=0.85)
                .move_to([x0, -1.6, 0], aligned_edge=LEFT)))
        self.play(vt.animate.set_value(xn), run_time=2.0, rate_func=linear)
        self.play(Flash(marca_n.get_center(), color=C_CALCULO, line_length=0.2,
                        flash_radius=0.35), run_time=0.5)
        self.wait(1.0)
        self.play(vt.animate.set_value(xv), run_time=3.0, rate_func=linear)
        self.play(Flash(marca_v.get_center(), color=C_CALCULO, line_length=0.2,
                        flash_radius=0.35), run_time=0.5)
        relleno.clear_updaters()
        self.wait(1.2)

        razon = S.razon(UMBRAL_VIEJO, UMBRAL_NUEVO)
        rot.mostrar(cifra_pie(f"{fmt(razon, 1)}x antes"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        grupo = VGroup(linea, et_linea, marca_n, marca_v, form_n, cif_n,
                       form_v, cif_v, etq_n, etq_v, relleno)
        cierre_leccion(self, rot, "El optimizador no lee la tabla:",
                       "lee su resumen.", grupo, espera=4.6)

class Clip4(Scene):
    """1.2.4 - El eslabon que mas sorprende no es la matematica: es el
    reloj. Un segundo de desfase cuesta ocho presupuestos. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El reloj manda"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        vista = vista_polar(radio=2.05, font_size=14)
        vista.move_to(LEFT * 3.2 + UP * 0.0)
        self.play(Create(vista), run_time=1.3)
        self.wait(0.3)

        traza = traza_pase(vista, el_max=80.0, az_culminacion=150.0,
                           muestras=120, color=C_CIELO)
        self.play(Create(traza), run_time=1.6)
        self.wait(0.5)

        p_nominal = Dot(traza.punto_en(0.5), radius=0.055, color=C_CIELO)
        self.play(FadeIn(p_nominal, scale=1.7), run_time=0.5)
        t_nom = tag_junto(p_nominal, "prediccion", direccion=LEFT,
                          buff=0.12, font_size=15, color=C_CIELO)
        self.play(FadeIn(t_nom), run_time=0.4)
        self.wait(0.8)

        # --- a esta escala 0.79 grados no se ve: se declara el zoom ---------
        lupa = Circle(radius=0.62, color=C_EJE, stroke_width=1.6)
        lupa.move_to(RIGHT * 1.15 + UP * 1.35)
        conector = DashedLine(p_nominal.get_center(), lupa.get_bottom(),
                              stroke_width=1.4, color=C_EJE)
        self.play(Create(conector), Create(lupa), run_time=0.9)
        t_zoom = tag_junto(lupa, "no a escala", direccion=UP, buff=0.12,
                           font_size=15)
        self.play(FadeIn(t_zoom), run_time=0.5)
        self.wait(0.5)

        p_nom2 = Dot(lupa.get_center() + LEFT * 0.20, radius=0.06,
                     color=C_CIELO)
        p_err2 = Dot(lupa.get_center() + RIGHT * 0.20, radius=0.06,
                     color=C_PELIGRO)
        segmento = Line(p_nom2.get_center(), p_err2.get_center(),
                        stroke_width=2.4, color=C_PELIGRO)
        self.play(FadeIn(p_nom2), run_time=0.4)
        self.play(Create(segmento), FadeIn(p_err2, scale=1.6), run_time=0.8)
        t_err = tag_hud(f"1 s reloj = {fmt(ERR_RELOJ, 2)} deg",
                        font_size=16, color=C_PELIGRO)
        t_err.next_to(lupa, DOWN, buff=0.34)
        self.play(FadeIn(t_err), run_time=0.5)
        self.wait(1.4)

        rot.mostrar(cifra_pie(f"reloj 1 s = {fmt(ERR_RELOJ, 2)} grados"),
                    zona="abajo")
        self.wait(2.0)

        # --- la banda de presupuesto cabe ocho veces en el error -------------
        escala = 3.4
        ancho_err = ERR_RELOJ * escala
        ancho_obj = OBJETIVO_DEG * escala
        n_bandas = int(math.ceil(VECES_PRESUPUESTO))

        marco = Rectangle(width=ancho_err, height=0.42, stroke_width=2.2,
                          color=C_PELIGRO)
        marco.move_to(RIGHT * 3.05 + DOWN * 1.35)
        self.play(Create(marco), run_time=0.9)
        t_marco = tag_hud(f"error {fmt(ERR_RELOJ, 2)} deg", font_size=17,
                          color=C_PELIGRO)
        t_marco.next_to(marco, UP, buff=0.16)
        self.play(FadeIn(t_marco), run_time=0.5)
        self.wait(0.7)

        bandas = VGroup()
        x0 = marco.get_left()[0]
        y0 = marco.get_center()[1]
        for k in range(n_bandas):
            b = Rectangle(width=ancho_obj * 0.90, height=0.28,
                         stroke_width=0, fill_color=C_CALCULO,
                         fill_opacity=0.85)
            b.move_to(np.array([x0 + ancho_obj * (k + 0.5), y0, 0.0]))
            bandas.add(b)
        self.play(LaggedStart(*[FadeIn(b, scale=0.6) for b in bandas],
                              lag_ratio=0.14), run_time=2.0)
        self.wait(0.6)

        t_veces = tag_hud(f"{fmt(VECES_PRESUPUESTO, 1)}x presupuesto",
                          font_size=19, color=C_CALCULO)
        t_veces.next_to(marco, DOWN, buff=0.36)
        self.play(FadeIn(t_veces), run_time=0.6)
        self.wait(3.0)

        # --- el cierre --------------------------------------------------------
        cierre_leccion(
            self, rot, "Un segundo de reloj", "cuesta ocho presupuestos.",
            vista, traza, p_nominal, t_nom, lupa, conector, t_zoom, p_nom2,
            p_err2, segmento, t_err, marco, t_marco, bandas, t_veces,
            espera=4.4)

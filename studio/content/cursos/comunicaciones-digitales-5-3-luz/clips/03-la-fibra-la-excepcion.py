class Clip3(Scene):
    """5.3.3 - La fibra: el mismo laser DENTRO del vidrio. WDM (varias
    lineas de color en un canal) con panel '80 colores x 100 Gb/s'
    (referencia declarada); amplificado cada 80 km (+16 dB MEDIDO =
    0.2 dB/km x 80 km). Pie: 99% de los bits del planeta bajo el mar
    (cita 3.1). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La fibra: la excepción terrestre")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mismo laser, dentro del vidrio ---------------------
        rot.mostrar(pie_curso("El mismo láser de hace un momento, ahora "
                              "encerrado DENTRO de un hilo de vidrio."),
                    zona="abajo", run_time=0.5)
        fibra_ancho, fibra_alto = 9.0, 1.1
        core = Rectangle(width=fibra_ancho, height=fibra_alto, color=C_EJE,
                         stroke_width=2.2)
        core.move_to(UP * 0.55)
        colores_wdm = [RED, ORANGE, YELLOW, GREEN, TEAL, BLUE, PURPLE]
        n_lineas = len(colores_wdm)
        half_w = fibra_ancho / 2 - 0.2
        lineas = VGroup()
        for i, col in enumerate(colores_wdm):
            y = (i - (n_lineas - 1) / 2) * (fibra_alto * 0.11)
            ln = Line(core.get_center() + LEFT * half_w + UP * y,
                     core.get_center() + RIGHT * half_w + UP * y,
                     color=col, stroke_width=2.0)
            lineas.add(ln)
        self.play(Create(core), run_time=0.9)
        self.play(LaggedStart(*[Create(ln) for ln in lineas],
                              lag_ratio=0.1), run_time=1.6)
        self.wait(4.0)

        # --- momento: 80 colores, cada uno su rio de bits -------------------
        rot.mostrar(pie_curso("Ochenta colores en el mismo vidrio, cada "
                              "uno su propio río de bits."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(
            tag_hud(f"{WDM_CANALES} colores", font_size=19,
                   color=C_BANDA),
            tag_hud(f"x {fmt(WDM_GBPS_CANAL, 0)} Gb/s", font_size=19),
            tag_hud(f"= {fmt(WDM_GBPS_TOTAL, 0)} Gb/s", font_size=19,
                   color=C_CIFRA))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.9)
        self.wait(4.3)

        # --- momento: amplificado cada 80 km ---------------------------------
        rot.mostrar(pie_curso("Pero la luz se apaga: cada ochenta "
                              "kilómetros hay que amplificarla."),
                    zona="abajo", run_time=0.5)
        reps_x = [-2.6, 0.3, 3.2]
        reps = VGroup()
        for x in reps_x:
            tri = Triangle(color=C_COD, fill_color=C_COD, fill_opacity=0.8,
                           stroke_width=1.4).scale(0.13)
            tri.move_to(core.get_bottom() + RIGHT * x + DOWN * 0.22)
            reps.add(tri)
        llave_repe = llave(Line(reps[0].get_center(), reps[1].get_center()),
                           f"{fmt(TRAMO_AMPLI_KM, 0)} km", direccion=DOWN)
        et_ganancia = tag_hud(f"+{fmt(GANANCIA_AMPLI_DB, 1)} dB",
                              font_size=19, color=C_CIFRA)
        et_ganancia.next_to(reps, DOWN, buff=0.75)
        self.play(LaggedStart(*[FadeIn(t, scale=0.6) for t in reps],
                              lag_ratio=0.25), run_time=1.0)
        self.play(FadeIn(llave_repe), FadeIn(et_ganancia), run_time=0.8)
        self.wait(4.8)

        # --- momento: el 99% de los bits van bajo el mar ---------------------
        rot.mostrar(pie_curso(
            f"El {PORC_BITS_SUBMARINOS}% de los bits del planeta van "
            f"bajo el mar, no por satélite: el canal que el espacio no "
            f"puede tener (visto en 3.1)."),
            zona="abajo", run_time=0.5)
        self.wait(9.0)

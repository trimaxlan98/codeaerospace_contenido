class Clip3(Scene):
    """2.1.3 - Doppler banda por banda: el ancho de un modem de 9600 bd
    se sale con la excursion en UHF y en las bandas mas altas. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Banda por banda"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- las cuatro bandas, en escala log (la razon pasa de 50) --------
        etiquetas = [row["nombre"].split()[0] for row in TABLA_D]
        valores = [row["fd_hz"] for row in TABLA_D]
        barras = barras_comparar(valores, etiquetas, ancho=5.6, alto=2.5,
                                 colores=[C_SAT] * len(valores), log=True,
                                 unidad="Hz")
        barras.move_to(LEFT * 0.55 + DOWN * 0.25)
        self.play(Create(barras.ejes), run_time=1.1)
        self.wait(0.4)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.25)
                               for b in barras.barras], lag_ratio=0.30),
                  FadeIn(barras.rotulos), run_time=2.0)
        self.play(FadeIn(barras.tag_log), run_time=0.5)
        self.wait(1.6)

        # --- el ancho del modem es un DATO publico, no una cifra medida ----
        rot.mostrar(dato_pie(f"modem {BAUDIOS} bd"), zona="abajo")
        self.wait(1.2)

        vals = np.asarray(valores, dtype=float)
        base = np.log10(np.maximum(vals, 1e-12))
        piso = float(base.min())
        top = float((base - piso + 0.35).max())
        h_modem = (np.log10(BAUDIOS) - piso + 0.35) / top * 2.5
        origen = np.asarray(barras.ejes[0].get_start(), dtype=np.float64)
        linea_modem = DashedLine(origen + UP * h_modem,
                                 origen + UP * h_modem + RIGHT * 5.6,
                                 stroke_width=2.2, color=C_TENUE)
        t_modem = tag_hud(f"modem {BAUDIOS} bd", font_size=17,
                          color=C_TENUE)
        t_modem.next_to(linea_modem, UP, buff=0.10).align_to(
            linea_modem, LEFT)
        self.play(Create(linea_modem), FadeIn(t_modem), run_time=1.3)
        self.wait(1.8)

        # --- VHF cabe; UHF (y las bandas mas altas) se salen ---------------
        t_dentro = tag_hud("dentro de banda", font_size=16, color=C_OK)
        t_dentro.next_to(barras.cima_de(0), UP, buff=0.16)
        self.play(FadeIn(t_dentro), run_time=0.7)
        self.wait(1.2)

        # se marca en S: por encima de la banda UHF hay margen de sobra
        # para que la etiqueta no se encime con la del modem
        t_fuera = tag_hud("fuera de banda", font_size=16, color=C_PELIGRO)
        t_fuera.next_to(barras.cima_de(2), UP, buff=0.14)
        flecha_fuera = Arrow(t_fuera.get_bottom() + DOWN * 0.02,
                             barras.cima_de(2) + UP * 0.06, buff=0.02,
                             color=C_PELIGRO, stroke_width=3.2,
                             max_tip_length_to_length_ratio=0.32)
        self.play(FadeIn(t_fuera), GrowArrow(flecha_fuera), run_time=1.0)
        self.wait(2.0)

        rot.mostrar(formula_pie(r"\Delta f = 2\, f_d"), zona="abajo")
        self.wait(3.0)

        rot.mostrar(cifra_pie(f"{fmt(TASA_UHF, 0)} Hz/s en culminacion"),
                    zona="abajo")
        self.wait(2.6)

        panel = panel_cifras(
            (f"VHF {fmt(TABLA_D[0]['fd_hz'] / 1000.0, 1)} kHz", C_SAT),
            f"UHF {fmt(FD_UHF / 1000.0, 1)} kHz",
            f"S {fmt(TABLA_D[2]['fd_hz'] / 1000.0, 1)} kHz",
            f"X {fmt(TABLA_D[3]['fd_hz'] / 1000.0, 1)} kHz")
        self.play(FadeIn(panel), run_time=0.8)
        self.wait(5.2)

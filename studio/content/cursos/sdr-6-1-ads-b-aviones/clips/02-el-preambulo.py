from comunicaciones import Onda  # noqa: E402


class Clip2(Scene):
    """6.1.2 - El patron del preambulo (4 pulsos, 8 us) se correlaciona con
    toda la captura. En esta captura (semilla 1) el pico MAS alto de la
    correlacion cae en un candidato falso (251) que el CRC rechaza; el
    offset verdadero (137, S.adsb_buscar) es el segundo pico. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El preambulo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        fs_mhz = 2.0
        patron = S.adsb_pulsos(np.array([], int))
        t_pat = np.arange(len(patron)) / fs_mhz
        pat = Onda(t_pat, patron, rango_y=(-0.15, 1.3), ancho=4.4, alto=1.0,
                   color=C_DATO, grosor=2.6)
        pat.move_to(UP * 2.55 + LEFT * 4.2)
        et_pat = tag_junto(pat, "patron", UP, buff=0.16, font_size=18,
                           color=C_DATO)
        self.play(Create(pat.ejes), run_time=0.4)
        self.play(Create(pat.curva), FadeIn(et_pat), run_time=1.1)
        self.wait(1.2)
        rot.mostrar(dato_pie("preambulo: 8 us"), zona="abajo", run_time=0.5)
        self.wait(1.6)

        # --- la correlacion sobre toda la captura -----------------------
        n = len(CORR)
        t_corr = np.arange(n)
        curva = Onda(t_corr, CORR, rango_y=(float(CORR.min()) * 1.1,
                                            float(CORR.max()) * 1.15),
                     ancho=11.6, alto=2.5, color=C_CALCULO, grosor=2.2)
        curva.move_to(DOWN * 1.15)
        et_corr = tag_junto(curva.ejes[0], "offset", RIGHT, buff=0.18,
                            font_size=18, color=C_TENUE)
        self.play(Create(curva.ejes), run_time=0.5)
        self.wait(0.2)
        self.play(Create(curva.curva), FadeIn(et_corr), run_time=2.0)
        self.wait(2.6)

        # --- el pico mas alto: un candidato falso, el CRC lo rechaza -----
        px, py = int(RECHAZADOS[0]), float(CORR[RECHAZADOS[0]])
        p_falso = Dot(curva.en(px, py), radius=0.09, color=C_RUIDO)
        cruz = Cross(p_falso, stroke_color=C_RUIDO, stroke_width=3.0)
        cruz.scale(0.7)
        et_falso = tag_junto(p_falso, "rechazado", UP, buff=0.18,
                             font_size=18, color=C_RUIDO)
        self.play(FadeIn(p_falso), run_time=0.5)
        self.wait(0.6)
        self.play(Create(cruz), FadeIn(et_falso), run_time=0.7)
        self.wait(2.4)

        # --- el offset verdadero: el CRC lo confirma ----------------------
        ox, oy = int(OFF), float(CORR[OFF])
        p_ok = Dot(curva.en(ox, oy), radius=0.1, color=C_OK)
        marco = SurroundingRectangle(p_ok, color=C_OK, buff=0.16,
                                     stroke_width=2.4)
        et_ok = tag_junto(marco, "aceptado", UP, buff=0.12, font_size=18,
                          color=C_OK)
        self.play(FadeIn(p_ok), run_time=0.5)
        self.wait(0.5)
        self.play(Create(marco), FadeIn(et_ok), run_time=0.7)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"offset: {OFF}"), zona="abajo", run_time=0.5)
        self.wait(3.4)

        n_rech = len(RECHAZADOS)
        rot.mostrar(cifra_pie(f"{n_rech} candidato falso", color=C_RUIDO),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

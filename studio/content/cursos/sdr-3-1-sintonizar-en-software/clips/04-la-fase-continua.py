class Clip4(Scene):
    """3.1.4 - El acumulador que se reinicia cada `bloque` muestras salta
    de fase en cada frontera (diagrama esquematico, geometria pura). El
    NCO real (S.nco_por_bloques con BLOQUE, continuo=False) hereda ese
    salto como rayas espurias cada fs/bloque = SEP_NCO Hz, medidas con
    S.espurio_nco_dbc -> ESP_NCO, ESP_NCO/SEP_NCO en el bloque de
    numeros. Cierre de la leccion. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La fase continua"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- diagrama esquematico: la fase que se reinicia ------------------
        bloque_il, n_bloques_il = 26, 3
        ancho_panel = 10.6
        base_y = -1.8
        altura_rampa = 3.6
        seg = ancho_panel / (bloque_il * n_bloques_il)

        eje_fase = Line(LEFT * ancho_panel / 2 + UP * base_y,
                        RIGHT * ancho_panel / 2 + UP * base_y, color=C_EJE,
                        stroke_width=1.6)
        etiqueta = tag_junto(eje_fase, "fase del acumulador", DOWN,
                             buff=0.3, font_size=22, color=C_LO)
        self.play(Create(eje_fase), FadeIn(etiqueta), run_time=0.6)
        self.wait(0.4)

        rampas = VGroup()
        saltos = VGroup()
        for b in range(n_bloques_il):
            x_inicio = LEFT * ancho_panel / 2 + RIGHT * (b * bloque_il * seg)
            x_fin = LEFT * ancho_panel / 2 + RIGHT * (
                (b * bloque_il + bloque_il - 1) * seg)
            inicio = x_inicio + UP * base_y
            fin = x_fin + UP * (base_y + altura_rampa)
            rampa = Line(inicio, fin, color=C_LO, stroke_width=3.2)
            rampas.add(rampa)
            self.play(Create(rampa), run_time=0.6)
            if b < n_bloques_il - 1:
                sig_x = LEFT * ancho_panel / 2 + RIGHT * (
                    (b + 1) * bloque_il * seg)
                salto = Line(fin, sig_x + UP * base_y, color=C_RUIDO,
                            stroke_width=2.8)
                saltos.add(salto)
                self.play(Create(salto), run_time=0.45)
        self.wait(0.6)

        salto_lbl = tag_junto(saltos[0], "salto", RIGHT, buff=0.15,
                              font_size=18, color=C_RUIDO)
        self.play(FadeIn(salto_lbl), run_time=0.4)
        self.wait(1.6)

        self.play(FadeOut(eje_fase), FadeOut(etiqueta), FadeOut(rampas),
                  FadeOut(saltos), FadeOut(salto_lbl), run_time=0.7)

        # --- el espectro del NCO real: reiniciado vs continuo ----------------
        n_esp = 24 * BLOQUE
        y_cont = S.nco_por_bloques(F_NCO, FS_NCO, n_esp, BLOQUE,
                                   continuo=True)
        y_reset = S.nco_por_bloques(F_NCO, FS_NCO, n_esp, BLOQUE,
                                    continuo=False)
        fc, dbc = S.espectro_db(y_cont, FS_NCO, nfft=n_esp,
                                ventana_nombre="rect")
        fr, dbr = S.espectro_db(y_reset, FS_NCO, nfft=n_esp,
                                ventana_nombre="rect")
        # S.nco devuelve exp(-j*fase): el tono del NCO cae en -F_NCO, no
        # +F_NCO. Se recentra sumando F_NCO para que la portadora quede
        # en 0 (banda base, eje relativo).
        fc_z, dbc_z = S.para_dibujar(fc + F_NCO, dbc, puntos=900,
                                     f_lo=-1200, f_hi=1200)
        fr_z, dbr_z = S.para_dibujar(fr + F_NCO, dbr, puntos=900,
                                     f_lo=-1200, f_hi=1200)

        esp = S.Espectro(fc_z, dbc_z, piso=-40.0, techo=2.0, ancho=11.5,
                         alto=3.8, color=C_LO)
        esp.move_to(ORIGIN)
        ticks = esp.marcas([-1200, -600, 0, 600, 1200],
                           ["-1200", "-600", "0", "600", "1200"])
        u = tag_junto(ticks[-1], "Hz", RIGHT, buff=0.2, font_size=20)
        etiq_modo = tag_junto(esp.ejes, "continuo", UP, buff=0.24,
                              font_size=20, color=C_LO)
        etiq_modo.move_to(UP * 2.15)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u),
                  FadeIn(etiq_modo), run_time=0.7)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.6)
        self.wait(1.6)

        d1 = tag_dato("240 kS/s, bloque 1000", font_size=19)
        d1.to_corner(UL, buff=0.7).shift(DOWN * 0.6 + RIGHT * 0.2)
        d2 = tag_dato(f"F = {fmt(F_NCO / 1e3, 1)} kHz", font_size=19)
        d2.next_to(d1, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(FadeIn(d1), run_time=0.5)
        self.wait(0.6)
        self.play(FadeIn(d2), run_time=0.5)
        self.wait(1.0)

        esp2 = esp.con_db(dbr_z, color=C_RUIDO)
        etiq_modo2 = tag_junto(esp.ejes, "reiniciado", UP, buff=0.24,
                               font_size=20, color=C_RUIDO)
        etiq_modo2.move_to(UP * 2.15)
        self.play(Transform(esp.curva, esp2.curva),
                  Transform(esp.area, esp2.area),
                  Transform(etiq_modo, etiq_modo2), run_time=1.8)
        self.wait(1.2)

        # las dos rayas mas altas del comb reiniciado: la portadora (no cae
        # exacto en 0, el bloque no es multiplo de un ciclo) y el espurio
        # a SEP_NCO de distancia (medido, no supuesto simetrico).
        orden = np.argsort(dbr_z)[::-1]
        f_portadora = float(fr_z[orden[0]])
        f_espurio = float(fr_z[orden[1]])
        marca1 = esp.marca_f(f_portadora, color=C_LO, ancho=1.6)
        marca2 = esp.marca_f(f_espurio, color=C_RUIDO, ancho=1.8)
        self.play(Create(marca1), Create(marca2), run_time=0.6)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"{fmt(ESP_NCO, 1)} dBc a {fmt(SEP_NCO, 0)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        cierre_leccion(self, rot, "Sintonizar ya no es girar un dial.",
                       "Es multiplicar por un fasor.", esp.ejes, esp.curva,
                       esp.area, ticks, u, etiq_modo, d1, d2, marca1, marca2,
                       espera=5.5)

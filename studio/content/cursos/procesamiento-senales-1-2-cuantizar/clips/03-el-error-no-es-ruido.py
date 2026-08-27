class Clip3(Scene):
    """1.2.3 - Un tono pequeno a 3 bits: el error se engancha a la senal
    y el espectro se llena de armonicos. El dither no baja el ruido, lo
    convierte en ruido: los picos se hunden y el piso sube. (~40 s)"""

    def _escalones_de(self, esc, t, xq):
        """La misma poligonal de escalones que dibuja `Escalera`, pero con
        una salida cuantizada dada: gemela exacta de `esc.pasos`."""
        pts = []
        for i in range(len(t)):
            pts.append(esc.en(t[i], xq[i]))
            if i + 1 < len(t):
                pts.append(esc.en(t[i + 1], xq[i]))
        c = VMobject(color=C_MUESTRA, stroke_width=2.2)
        c.set_points_as_corners(pts)
        return c

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Cuando el error no es ruido"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- arriba: el tono pequeno sobre cuatro escalones ---------------
        n_v = 120
        t_v = T_Q[:n_v]
        esc = Escalera(t_v, TONO[:n_v], BITS_DITHER, ancho=7.4, alto=2.1,
                       alto_err=0.40)
        esc.shift(UP * 1.90)
        self.play(FadeIn(esc.ejes), run_time=0.5)
        self.play(Create(esc.curva), run_time=1.6)
        self.play(Create(esc.pasos), run_time=1.6)
        rot.mostrar(cifra_pie(f"paso = {fmt(PASO_DITHER, 2)}"), zona="abajo",
                    run_time=0.5)
        self.wait(1.8)

        panel = panel_cifras(f"bits = {BITS_DITHER}",
                             (f"tono {fmt(TONO_F, 0)} Hz", C_SENAL),
                             (f"amplitud {fmt(TONO_A, 2)}", C_SENAL))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(1.6)

        # --- abajo: el espectro de ESE error ------------------------------
        ea = EspectroArea(F_ERR, DB_ERR_SIN, piso_db=-60.0, ancho=10.6,
                          alto=2.3, color=C_RUIDO)
        ea.shift(DOWN * 1.50)
        et_hz = tag_hud("Hz", font_size=19, color=C_TENUE)
        et_hz.next_to(ea.en(F_ERR[-1], -60.0), RIGHT, buff=0.14)
        et_cero = tag_hud("0", font_size=19, color=C_TENUE)
        et_cero.next_to(ea.en(0.0, -60.0), DL, buff=0.12)
        self.play(FadeIn(ea.ejes), FadeIn(et_hz), FadeIn(et_cero),
                  run_time=0.6)
        self.play(Create(ea.curva), FadeIn(ea.area), run_time=2.2)
        self.wait(1.6)

        # --- los picos caen en armonicos del tono -------------------------
        marcas = VGroup()
        for k in (3, 7):
            f_k = k * TONO_F
            marcas.add(ea.marca_f(f_k, color=C_CALCULO))
            et = tag_hud(f"{fmt(f_k, 0)} Hz", font_size=18, color=C_CALCULO)
            et.next_to(ea.en(f_k, 0.0), UP, buff=0.12)
            marcas.add(et)
        self.play(LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.15),
                  run_time=1.4)
        rot.mostrar(cifra_pie(f"espurio = {fmt(ESP_SIN, 1)} dBc"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)
        rot.mostrar(cifra_pie(f"piso = {fmt(PISO_SIN, 1)} dBc"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- el dither: se anade ruido A PROPOSITO ------------------------
        pasos_dither = self._escalones_de(esc, t_v, Q_CON[:n_v])
        gem = ea.con_psd(DB_ERR_CON)
        panel_2 = panel_cifras(
            (f"espurio {fmt(ESP_SIN, 1)} dBc", C_RUIDO),
            (f"con dither {fmt(ESP_CON, 1)} dBc", C_SALIDA))
        self.play(FadeOut(panel), run_time=0.5)
        self.wait(0.8)
        self.play(Transform(esc.pasos, pasos_dither),
                  Transform(ea.curva, gem.curva),
                  Transform(ea.area, gem.area),
                  FadeOut(marcas), FadeIn(panel_2), run_time=3.2)
        rot.mostrar(cifra_pie(f"espurio {fmt(ESP_SIN, 1)} -> "
                              f"{fmt(ESP_CON, 1)} dBc"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        rot.mostrar(cifra_pie(f"piso {fmt(PISO_SIN, 1)} -> "
                              f"{fmt(PISO_CON, 1)} dBc"), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)

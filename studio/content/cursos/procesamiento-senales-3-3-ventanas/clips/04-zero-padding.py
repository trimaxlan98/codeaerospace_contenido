class Clip4(Scene):
    """3.3.4 - Rellenar de ceros interpola la curva; solo medir mas
    tiempo separa dos tonos vecinos. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Rellenar de ceros"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        z_c = slice(46, 61)     # 15 bins de F_DOS: 179.7 .. 234.4 Hz
        z_p = slice(184, 241)   # los MISMOS Hz con cuatro veces mas bins

        # --- dos tonos separados 30 Hz: la caja los separa -----------------
        ed = EspectroDoble(F_DOS[z_c], DB_LEJOS[z_c], piso_db=-70.0,
                           ancho=9.2, alto=2.5, color=C_BANDA)
        ed.move_to(DOWN * 0.30)
        hz = tag_hud("Hz", font_size=17, color=C_TENUE)
        hz.next_to(ed.en(F_DOS[z_c][-1], -70.0), DOWN, buff=0.18)
        self.play(FadeIn(ed.ejes), FadeIn(hz), run_time=0.5)
        rot.mostrar(cifra_pie(f"N = {N_S}: paso {fmt(RESOLUCION, 2)} Hz"),
                    zona="abajo", run_time=0.5)
        self.play(Create(ed.curva), FadeIn(ed.area), run_time=1.5)

        m1 = ed.marca_f(F1_DOS, color=C_CALCULO)
        m2 = ed.marca_f(F2_LEJOS, color=C_CALCULO)
        self.play(Create(m1), Create(m2), run_time=0.8)
        self.wait(1.2)
        rot.mostrar(cifra_pie(f"valle = {fmt(VALLE_LEJOS, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)

        # --- los mismos 256 datos, tonos a 6 Hz: no los separa -------------
        gem = ed.con_db(DB_CERCA[z_c], color=C_RUIDO)
        m2b = ed.marca_f(F2_CERCA, color=C_CALCULO)
        self.play(Transform(ed.curva, gem.curva),
                  Transform(ed.area, gem.area),
                  Transform(m2, m2b), run_time=1.5)
        rot.mostrar(cifra_pie(f"tonos a {fmt(F2_CERCA - F1_DOS, 0)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)
        rot.mostrar(cifra_pie(f"valle = {fmt(VALLE_CERCA, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)

        # --- rellenar de ceros: mas bins, la misma informacion -------------
        ed_p = EspectroDoble(F_PAD[z_p], DB_PAD[z_p], piso_db=-70.0,
                             ancho=9.2, alto=2.5, color=C_CALCULO)
        ed_p.move_to(DOWN * 0.30)
        self.play(ed.area.animate.set_opacity(0.10),
                  ed.curva.animate.set_stroke(opacity=0.35), run_time=0.6)
        rot.mostrar(cifra_pie(f"nfft = {4 * N_S} con {N_S} datos"),
                    zona="abajo", run_time=0.5)
        self.play(Create(ed_p.curva), run_time=1.7)
        self.wait(1.4)
        rot.mostrar(cifra_pie(f"valle = {fmt(VALLE_PAD, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)

        # --- mas TIEMPO: 1024 muestras reales ------------------------------
        ed_l = EspectroDoble(F_PAD[z_p], DB_LARGO[z_p], piso_db=-70.0,
                             ancho=9.2, alto=2.5, color=C_SALIDA)
        ed_l.move_to(DOWN * 0.30)
        rot.mostrar(cifra_pie(f"N = {N_LARGO_V}: paso "
                              f"{fmt(RESOLUCION_LARGA, 2)} Hz"),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(ed.area), FadeOut(ed.curva), run_time=0.5)
        self.play(Transform(ed_p.curva, ed_l.curva), run_time=1.9)
        self.wait(1.4)
        rot.mostrar(cifra_pie(f"valle = {fmt(VALLE_LARGO, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(1.6)

        panel = panel_cifras((f"256: {fmt(VALLE_CERCA, 2)} dB", C_RUIDO),
                             (f"ceros: {fmt(VALLE_PAD, 2)} dB", C_CALCULO),
                             (f"1024: {fmt(VALLE_LARGO, 2)} dB", C_SALIDA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.4)

        cierre_leccion(self, rot, "Rellenar de ceros dibuja mejor.",
                       "Solo el tiempo resuelve.",
                       ed.ejes, ed_p.curva, m1, m2, hz, panel)

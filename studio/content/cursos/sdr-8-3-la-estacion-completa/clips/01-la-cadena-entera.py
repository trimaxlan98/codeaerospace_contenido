class Clip1(Scene):
    """8.3.1 - La cadena del 1.1 se enciende eslabon a eslabon y junto a
    cada uno aparece la cifra que su leccion midio: NF de la cascada,
    IRR corregida, rechazo del FIR, SQNR de 8 bits, caudal USB y los
    errores tras Viterbi. La antena lleva su parametro (gris). (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La cadena entera"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- las cifras, todas de la libreria ------------------------------
        irr = S.irr_corregida_minima()[0]
        h_fir = S.fir_paso_bajo(S.kaiser_taps(60, 40e3, 2.4e6), 120e3, 2.4e6)
        rechazo = S.aten_minima(h_fir, 2.4e6, 140e3)
        sqnr = S.sqnr_adc(8)
        caudal = S.caudal_bps() / 1e6
        errores = MET["errores_viterbi"]

        cad = S.Cadena(("ANTENA", "LNA", "MEZCLADOR", "FILTRO", "ADC",
                        "USB", "SOFTWARE"), ancho_total=12.2, alto=1.8,
                       tamano=24)
        cad.move_to(DOWN * 0.75)

        # (que, cifra, color, lado): alterna arriba / abajo
        filas = {
            "ANTENA": ("QFH", f"{fmt(P['g_rx_dbi'], 0)} dBi", C_DATO, UP),
            "LNA": ("NF", f"{fmt(NF_ANT, 2)} dB", C_CALCULO, DOWN),
            "MEZCLADOR": ("IRR", f"> {irr} dB", C_CALCULO, UP),
            "FILTRO": ("rechazo", f"{fmt(rechazo, 1)} dB", C_CALCULO, DOWN),
            "ADC": ("SQNR", f"{fmt(sqnr, 1)} dB", C_CALCULO, UP),
            "USB": ("caudal", f"{fmt(caudal, 1)} Mbit/s", C_CALCULO, DOWN),
            "SOFTWARE": ("Viterbi", f"{errores} errores", C_CALCULO, UP),
        }
        rotulos = []
        for i, nombre in enumerate(cad.nombres):
            que, cifra, color, lado = filas[nombre]
            t_que = Text(que, font_size=26, color=C_TENUE)
            t_cif = (tag_dato(cifra, font_size=28) if color == C_DATO
                     else tag_hud(cifra, font_size=28, color=color))
            g = VGroup(t_que, t_cif).arrange(DOWN, buff=0.12)
            g.next_to(cad.bloques[i], lado, buff=0.4)
            rotulos.append(g)
        # el LO del mezclador cuelga abajo: las cifras de abajo, a su nivel
        lo_y = cad.lo.get_center()[1]
        for i, nombre in enumerate(cad.nombres):
            if filas[nombre][3] is DOWN:
                rotulos[i].set_y(lo_y)

        # --- la cadena, apagada -------------------------------------------
        self.play(FadeIn(cad.bloques, lag_ratio=0.08),
                  FadeIn(cad.flechas), FadeIn(cad.lo), run_time=1.4)
        self.wait(1.0)

        # --- eslabon a eslabon: se enciende y dice su cifra ----------------
        for i, b in enumerate(cad.bloques):
            lado = filas[cad.nombres[i]][3]
            anims = [b[0].animate.set_stroke(C_SENAL, width=3.2)
                     .set_fill(C_SENAL, opacity=0.14),
                     FadeIn(rotulos[i], shift=-lado * 0.12)]
            if i > 0:
                anims.append(ShowPassingFlash(
                    cad.flechas[i - 1].copy().set_fill(opacity=0)
                    .set_stroke(C_SENAL, width=5, opacity=1),
                    time_width=0.6))
            self.play(*anims, run_time=0.8)
            self.wait(1.9)

        self.wait(1.0)
        # --- la senal la recorre entera ------------------------------------
        self.play(S.flujo(list(cad.flechas), color=C_SENAL,
                          por_conexion=0.4))
        self.play(cad.bloques[-1][0].animate.set_stroke(C_OK, width=3.6)
                  .set_fill(C_OK, opacity=0.2), run_time=0.8)
        self.wait(2.0)
        rot.mostrar(cifra_pie(f"{errores} errores tras Viterbi"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)
        self.play(S.flujo(list(cad.flechas), color=C_SENAL,
                          por_conexion=0.35))
        self.wait(3.4)

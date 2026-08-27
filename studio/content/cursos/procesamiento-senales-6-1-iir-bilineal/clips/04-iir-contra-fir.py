class Clip4(Scene):
    """6.1.4 - El MISMO pliego por los dos caminos: un FIR equirriple de
    orden 40 o un eliptico de orden 5. La cuenta no esta reñida. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("IIR contra FIR"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el pliego, el mismo de todo el modulo ------------------------
        rf = respuesta_dibujo(W_FIR, MAG_FIR, ancho=9.4, alto=3.2,
                              piso_db=-80.0, techo_db=8.0, color=C_MUESTRA)
        rf.move_to(DOWN * 0.55)
        banda_p = rf.banda(0.0, F_PASO * np.pi, color=C_SALIDA,
                           opacidad=0.10)
        banda_r = rf.banda(F_RECHAZO * np.pi, np.pi, color=C_RUIDO,
                           opacidad=0.10)
        nivel = DashedLine(rf.en(0.0, -ATEN_PEDIDA),
                           rf.en(np.pi, -ATEN_PEDIDA), color=C_DATO,
                           stroke_width=1.4, dash_length=0.07)
        et_niv = tag_hud(f"-{fmt(ATEN_PEDIDA, 0)} dB", font_size=18,
                         color=C_DATO)
        et_niv.next_to(rf.en(0.04 * np.pi, -ATEN_PEDIDA), RIGHT,
                       buff=0.10).shift(UP * 0.24)
        et_w = tag_hud("w / pi", font_size=18, color=C_TENUE)
        et_w.next_to(rf.en(np.pi, -80.0), RIGHT, buff=0.22)
        self.play(FadeIn(rf.ejes), FadeIn(banda_p), FadeIn(banda_r),
                  FadeIn(et_w), run_time=0.7)
        self.play(Create(nivel), FadeIn(et_niv), run_time=0.7)
        self.wait(1.0)

        # --- camino 1: el FIR equirriple ----------------------------------
        rot.mostrar(cifra_pie(f"FIR orden {ORDEN_FIR}", color=C_MUESTRA),
                    zona="abajo", run_time=0.5)
        self.play(Create(rf.curva), run_time=1.8)
        self.wait(2.0)
        rot.mostrar(cifra_pie(f"FIR {fmt(ATEN_FIR, 1)} dB", color=C_MUESTRA),
                    zona="abajo", run_time=0.5)
        self.wait(1.8)

        # --- camino 2: el mismo pliego con un eliptico de orden 5 ---------
        gem = rf.con_mag(MAG_ELIP, color=C_CALCULO)
        rot.mostrar(cifra_pie(f"elip orden {ORDEN_ELIP}"), zona="abajo",
                    run_time=0.5)
        self.play(rf.curva.animate.set_stroke(opacity=0.34), run_time=0.4)
        self.play(Create(gem.curva), run_time=1.8)
        self.add(gem.curva)
        self.wait(2.2)
        rot.mostrar(cifra_pie(f"elip {fmt(ATEN_ELIP, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(1.8)

        # --- lo que cuesta cada camino ------------------------------------
        panel = panel_cifras(
            (f"FIR {ORDEN_FIR}: {MACS_FIR_PLIEGO} mult", C_MUESTRA),
            (f"elip {ORDEN_ELIP}: {COEFS_ELIP} coefs", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.0)

        # --- la honestidad: el IIR no trae fase lineal (se vio en 4.3) ----
        rot.mostrar(dato_pie("IIR sin fase lineal"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        cierre_leccion(self, rot, "El filtro analogico no se copia.",
                       "Se dobla sobre el circulo.",
                       rf.ejes, rf.curva, gem.curva, banda_p, banda_r,
                       nivel, et_niv, et_w, panel)

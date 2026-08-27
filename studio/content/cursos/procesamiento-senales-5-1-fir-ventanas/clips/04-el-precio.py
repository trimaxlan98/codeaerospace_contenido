class Clip4(Scene):
    """5.1.4 - El mismo pliego, dos diseños: por ventanas cuesta orden 72;
    repartiendo el error, 40. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("El precio"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- el pliego ----------------------------------------------------
        w_v, m_v, _ = respuesta_frec(H_PLIEGO_VENT, [1.0], 2048)
        rf = respuesta_dibujo(w_v, m_v, ancho=9.4, alto=3.2, piso_db=-80.0,
                              techo_db=8.0, color=C_MUESTRA)
        rf.move_to(DOWN * 0.45)
        banda_p = rf.banda(0.0, F_PASO * np.pi, color=C_SALIDA,
                           opacidad=0.10)
        banda_r = rf.banda(F_RECHAZO * np.pi, np.pi, color=C_RUIDO,
                           opacidad=0.10)
        linea_a = DashedLine(rf.en(0.0, -ATEN_PEDIDA),
                             rf.en(np.pi, -ATEN_PEDIDA), color=C_TENUE,
                             stroke_width=1.4, dash_length=0.07)
        et_a = tag_hud(f"-{fmt(ATEN_PEDIDA, 0)} dB", font_size=19,
                       color=C_TENUE)
        et_a.next_to(rf.en(0.0, -ATEN_PEDIDA), RIGHT, buff=0.12).shift(
            UP * 0.16)
        self.play(FadeIn(banda_p), FadeIn(banda_r), run_time=0.6)
        self.play(Create(linea_a), FadeIn(et_a), run_time=0.7)
        self.wait(1.2)

        self.play(FadeIn(rf), run_time=0.9)
        rot.mostrar(cifra_pie(f"ventana: orden {ORDEN_VENTANA}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- el mismo pliego, repartiendo el error ------------------------
        gem = rf.con_mag(MAG_EQ, color=C_CALCULO)
        self.play(rf.curva.animate.set_stroke(opacity=0.30), run_time=0.5)
        self.play(Create(gem.curva), run_time=1.8)
        self.add(gem.curva)
        rot.mostrar(cifra_pie(f"equirriple: orden {ORDEN_EQ}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        panel = panel_cifras((f"ventana {MACS_VENTANA} mult", C_MUESTRA),
                             (f"equirriple {MACS_EQ} mult", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.4)
        rot.mostrar(cifra_pie(f"la mitad de cuentas"), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)

        cierre_leccion(self, rot, "El filtro ideal no existe.",
                       "Solo existe su recorte.",
                       rf, gem.curva, banda_p, banda_r, linea_a, et_a,
                       panel)

class Clip4(Scene):
    """5.3.4 - Lo que decide si un filtro cabe en el aparato no son los
    dB: son las multiplicaciones por segundo, y suben con la fs. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("El presupuesto"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        rot.mostrar(cifra_pie(f"{MACS} multiplicaciones"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        # --- el contador sube con fs = 48 kHz --------------------------------
        et_fs = tag_hud(f"{FS_AUDIO} Hz", font_size=20, color=C_MUESTRA)
        et_fs.move_to(UP * 1.9)
        pasos = np.linspace(0.0, MMAC_S, 6)[1:]
        cont = tag_hud(f"{pasos[0]:.3f} MMAC/s", font_size=48,
                       color=C_CALCULO)
        cont.move_to(UP * 0.7)
        self.play(FadeIn(et_fs), run_time=0.4)
        self.play(FadeIn(cont), run_time=0.4)
        for v in pasos[1:]:
            nuevo = tag_hud(f"{v:.3f} MMAC/s", font_size=48, color=C_CALCULO)
            nuevo.move_to(cont.get_center())
            self.play(Succession(Wait(0.12),
                                 Transform(cont, nuevo, run_time=0.12)))
        self.wait(1.8)
        rot.mostrar(cifra_pie(f"{FS_AUDIO} Hz = {fmt(MMAC_S, 3)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- y a fs = 192 kHz? -------------------------------------------
        et_fs_alta = tag_hud(f"{FS_ALTA} Hz", font_size=20, color=C_RUIDO)
        et_fs_alta.move_to(et_fs.get_center())
        self.play(FadeOut(et_fs), FadeIn(et_fs_alta), run_time=0.5)
        pasos_alta = np.linspace(MMAC_S, MMAC_S_ALTA, 5)[1:]
        for v in pasos_alta:
            nuevo = tag_hud(f"{v:.3f} MMAC/s", font_size=48, color=C_RUIDO)
            nuevo.move_to(cont.get_center())
            self.play(Succession(Wait(0.12),
                                 Transform(cont, nuevo, run_time=0.12)))
        self.wait(1.8)
        rot.mostrar(cifra_pie(f"{FS_ALTA} Hz = {fmt(MMAC_S_ALTA, 3)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- las dos, una junto a la otra -------------------------------
        self.play(FadeOut(et_fs_alta), FadeOut(cont), run_time=0.5)
        bars = Barras([MMAC_S, MMAC_S_ALTA], ancho=4.6, alto=2.6,
                     color=C_CALCULO, hueco=0.35)
        bars.move_to(DOWN * 0.7)
        et_b0 = tag_hud(f"{FS_AUDIO} Hz", font_size=17, color=C_MUESTRA)
        et_b0.next_to(bars.barra(0), DOWN, buff=0.16)
        et_b1 = tag_hud(f"{FS_ALTA} Hz", font_size=17, color=C_RUIDO)
        et_b1.next_to(bars.barra(1), DOWN, buff=0.16)
        et_v0 = tag_hud(fmt(MMAC_S, 3), font_size=19, color=C_MUESTRA)
        et_v0.next_to(bars.cima(0), UP, buff=0.12)
        et_v1 = tag_hud(fmt(MMAC_S_ALTA, 3), font_size=19, color=C_RUIDO)
        et_v1.next_to(bars.cima(1), UP, buff=0.12)
        self.play(FadeIn(bars.ejes), run_time=0.3)
        self.play(LaggedStart(Create(bars.barra(0)), Create(bars.barra(1)),
                              lag_ratio=0.5), FadeIn(et_b0), FadeIn(et_b1),
                  run_time=1.4)
        self.play(FadeIn(et_v0), FadeIn(et_v1), run_time=0.6)
        self.wait(3.4)

        cierre_leccion(self, rot, "Un filtro no se mide en decibelios.",
                       "Se mide en multiplicaciones por segundo.",
                       bars, et_b0, et_b1, et_v0, et_v1, espera=5.2)

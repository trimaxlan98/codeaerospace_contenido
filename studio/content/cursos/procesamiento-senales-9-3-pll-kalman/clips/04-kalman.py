class Clip4(Scene):
    """9.3.4 - Otro seguimiento: VERDAD cambia despacio, MEDIDAS la mide
    con ruido. Kalman decide cuanto creerse cada medida: con q chica se
    fia poco (suave y lento), con q grande se fia mas. Cierre de la
    leccion. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("Kalman"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        idx = np.arange(N_KAL)
        piso = float(min(VERDAD.min(), MEDIDAS.min())) - 0.1
        techo = float(max(VERDAD.max(), MEDIDAS.max())) + 0.1
        rf = respuesta_dibujo(idx, VERDAD, ancho=10.2, alto=3.0,
                              piso_db=piso, techo_db=techo, color=C_IDEAL)
        rf.move_to(DOWN * 0.35)
        self.play(FadeIn(rf.ejes), Create(rf.curva), run_time=1.4)
        et_verdad = tag_hud("verdad", font_size=19, color=C_IDEAL)
        et_verdad.next_to(rf.en(0, VERDAD[0]), LEFT, buff=0.20)
        self.play(FadeIn(et_verdad), run_time=0.4)
        self.wait(0.6)

        rf_med = rf.con_mag(MEDIDAS, color=C_RUIDO)
        self.play(Create(rf_med.curva), run_time=1.6)
        self.add(rf_med.curva)
        rot.mostrar(cifra_pie(f"rmse medidas {fmt(RMSE_MEDIDAS, 3)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        self.play(rf_med.curva.animate.set_stroke(opacity=0.30),
                  run_time=0.6)

        q_chico, q_grande = QS
        est_chico = rf.con_mag(EST[q_chico], color=C_APREND)
        est_grande = rf.con_mag(EST[q_grande], color=C_CALCULO)
        self.play(Create(est_chico.curva), run_time=1.5)
        self.add(est_chico.curva)
        et_chico = tag_hud("q chico", font_size=18, color=C_APREND)
        et_chico.next_to(rf.en(N_KAL - 1, EST[q_chico][-1]), RIGHT,
                         buff=0.16)
        self.play(FadeIn(et_chico), run_time=0.4)
        rot.mostrar(cifra_pie(f"q chica: {fmt(RMSE_KAL[q_chico], 3)} rmse"),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)

        self.play(Create(est_grande.curva), run_time=1.5)
        self.add(est_grande.curva)
        et_grande = tag_hud("q grande", font_size=18, color=C_CALCULO)
        et_grande.next_to(rf.en(N_KAL - 1, EST[q_grande][-1]), RIGHT,
                          buff=0.16).shift(DOWN * 0.32)
        self.play(FadeIn(et_grande), run_time=0.4)
        rot.mostrar(cifra_pie(f"q grande: {fmt(RMSE_KAL[q_grande], 3)} rmse"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        panel = panel_cifras(
            (f"gan chico {fmt(GAN_FINAL[q_chico], 3)}", C_APREND),
            (f"gan grande {fmt(GAN_FINAL[q_grande], 3)}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)

        cierre_leccion(
            self, rot, "Seguir no es medir.", "Es apostar y corregir.",
            rf.ejes, rf.curva, rf_med.curva, est_chico.curva,
            est_grande.curva, et_verdad, et_chico, et_grande, panel)

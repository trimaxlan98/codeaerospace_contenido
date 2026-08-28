class Clip4(Scene):
    """7.1.4 - La SNR que de verdad queda con 16 bits sobre esta señal, y
    por que no coincide con la formula de libro. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("Lo que queda"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        sec = Secuencia(X_Q[::4], 0, (-1.15, 1.15), ancho=10.0, alto=2.4,
                        color=C_SENAL, radio=0.035)
        sec.move_to(UP * 0.85)
        self.play(FadeIn(sec), run_time=0.9)
        self.wait(1.2)

        err = (q15(X_Q) - X_Q)[::4]
        sec_err = Secuencia(err, 0, (-2e-5, 2e-5), ancho=10.0, alto=1.3,
                            color=C_RUIDO, radio=0.03, eje_y=False)
        sec_err.move_to(DOWN * 1.55)
        et_err = tag_hud("error", font_size=19, color=C_RUIDO)
        et_err.next_to(sec_err, LEFT, buff=0.26)
        self.play(FadeIn(sec_err), FadeIn(et_err), run_time=0.9)
        rot.mostrar(cifra_pie(f"error rms = {ERR_RMS:.2e}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        panel = panel_cifras((f"SNR = {fmt(SNR_Q, 1)} dB", C_CALCULO),
                             (f"margen = {fmt(MARGEN_Q, 2)} dB", C_SALIDA))
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie(f"SNR medida {fmt(SNR_Q, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        # --- la formula de libro, y por que no cuadra ---------------------
        dato = dato_pie(f"teoria {fmt(TEORICA_Q, 1)} dB")
        rot.mostrar(dato, zona="abajo", run_time=0.5)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"medida {fmt(SNR_Q, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        cierre_leccion(self, rot, "El punto fijo no es coma flotante barata.",
                       "Es otro oficio.",
                       sec, sec_err, et_err, panel)

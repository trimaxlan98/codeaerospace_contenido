class Clip3(Scene):
    """3.1.3 - Tres receptores de la MISMA captura (CAP): tras verla
    entera, se apila en tres copias y cada una aplica su propio
    S.nco(TRES[i], FS, ...) para traer una emisora distinta a 0, con un
    canal verde de +-100 kHz. Los offsets (cian, tag_hud) salen de
    S.emisoras_captura via TRES, en el bloque de numeros. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Tres receptores en uno"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- una sola captura, el espectro completo -------------------------
        f0, db0 = S.espectro_db(CAP, FS, nfft=2048)
        base = S.Espectro(f0, db0, piso=-70.0, techo=2.0, ancho=11.8,
                          alto=2.7, color=C_SENAL)
        base.move_to(ORIGIN)
        ticks = base.marcas([-1.2e6, -0.6e6, 0.0, 0.6e6, 1.2e6],
                            ["-1200", "-600", "0", "600", "1200"])
        self.play(Create(base.ejes), FadeIn(ticks), run_time=0.6)
        self.play(Create(base.curva), FadeIn(base.area), run_time=1.6)
        rot.mostrar(dato_pie(f"captura: {FS / 1e6:.1f} MS/s"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        self.play(FadeOut(base.ejes), FadeOut(base.curva), FadeOut(base.area),
                  FadeOut(ticks), run_time=0.6)

        # --- se apila en tres receptores, cada uno con su NCO ---------------
        # (ancho mas angosto que la base: deja sitio a la cifra sin salirse)
        ancho, alto = 9.4, 1.2
        ys = [1.55, 0.0, -1.55]
        for i, off in enumerate(TRES):
            y = CAP * S.nco(off, FS, len(CAP))
            f, db = S.espectro_db(y, FS, nfft=2048)
            esp = S.Espectro(f, db, piso=-70.0, techo=2.0, ancho=ancho,
                             alto=alto, color=C_SENAL)
            esp.move_to(UP * ys[i])
            banda = esp.banda(-100e3, 100e3, color=C_OK, opacidad=0.18)
            cero = esp.marcas([0.0], ["0"])
            cifra = tag_hud(f"{fmt(off / 1e3, 0)} kHz", font_size=19)
            cifra.move_to(RIGHT * 5.9 + UP * ys[i])

            self.play(Create(esp.ejes), FadeIn(cero), FadeIn(cifra),
                      run_time=0.5)
            self.play(Create(esp.curva), FadeIn(esp.area), FadeIn(banda),
                      run_time=1.2)
            self.wait(2.1)

        self.wait(9.0)

class Clip3(Scene):
    """1.3.3 - La MISMA secuencia conformada con pulso rectangular vs
    coseno alzado (beta=0.35): la cola espectral cae mucho mas rapido y
    el ancho al 90% baja, medido con ancho_banda. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El conformado ahorra espectro")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el pulso rectangular -------------------------------------
        rot.mostrar(pie_curso("Hasta ahora mandamos rectángulos: fáciles "
                              "de generar, caros en espectro."),
                    zona="abajo", run_time=0.5)
        on = onda(T_VIS_1, Y_VIS_1, rango_y=(-1.3, 1.3), ancho=7.0, alto=1.7,
                 color=C_SENAL)
        on.move_to(UP * 1.6)
        et_on = tag_hud("rectangular", font_size=15, color=C_SENAL)
        et_on.next_to(on, LEFT, buff=0.18)
        self.play(FadeIn(on), FadeIn(et_on), run_time=1.0)
        self.wait(3.2)

        # --- momento: el coseno alzado redondea el pulso ------------------------
        rot.mostrar(pie_curso("El coseno alzado redondea el mismo "
                              "símbolo: sin esquinas."),
                    zona="abajo", run_time=0.5)
        on_rc = on.con_serie(Y_VIS_RC, color=C_COD)
        et_rc = tag_hud("coseno alzado", font_size=15, color=C_COD)
        et_rc.move_to(et_on)
        self.play(Transform(on.curva, on_rc.curva), FadeOut(et_on),
                  run_time=1.6)
        self.play(FadeIn(et_rc), run_time=0.4)
        et_on = et_rc
        self.wait(3.0)

        # --- momento: la PSD del rectangular -------------------------------------
        rot.mostrar(pie_curso("En frecuencia, el rectangular deja colas "
                              "largas: así se ve su PSD."),
                    zona="abajo", run_time=0.5)
        esp = espectro_area(F_1, P_1_DB, piso_db=-40.0, ancho=7.0, alto=2.0,
                            color=C_BANDA)
        esp.move_to(DOWN * 1.55)
        marca1 = esp.marca_f(BW_1_90, color=C_CIFRA)
        cifra1 = tag_hud(f"BW(90%) = {fmt(BW_1_90, 2)}", font_size=18)
        cifra1.next_to(marca1, UP, buff=0.1)
        self.play(FadeIn(esp), run_time=0.7)
        self.play(Create(marca1), FadeIn(cifra1), run_time=0.9)
        self.wait(3.2)

        # --- momento: la PSD del coseno alzado cae en picada ----------------------
        rot.mostrar(pie_curso("Con el coseno alzado, la cola cae en "
                              "picada: el ancho ocupado baja."),
                    zona="abajo", run_time=0.5)
        esp_rc = esp.con_psd(P_RC_DB, color=C_COD)
        self.play(FadeOut(marca1), FadeOut(cifra1),
                  Transform(esp.curva, esp_rc.curva),
                  Transform(esp.area, esp_rc.area), run_time=1.8)
        marca2 = esp.marca_f(BW_RC_90, color=C_CIFRA)
        cifra2 = tag_hud(f"BW(90%) = {fmt(BW_RC_90, 2)}", font_size=18)
        cifra2.next_to(marca2, UP, buff=0.1)
        self.play(Create(marca2), FadeIn(cifra2), run_time=0.9)
        self.wait(3.2)

        # --- momento: el ahorro medido ---------------------------------------------
        rot.mostrar(pie_curso("Por eso nadie transmite rectángulos."),
                    zona="abajo", run_time=0.5)
        ahorro = tag_hud(f"ahorro = {fmt(AHORRO_RC, 0)}%", font_size=20,
                         color=C_CIFRA)
        ahorro.next_to(esp, RIGHT, buff=0.3)
        self.play(FadeIn(ahorro, shift=0.15 * UP), run_time=0.6)
        self.wait(6.0)

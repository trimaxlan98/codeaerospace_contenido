class Clip4(Scene):
    """7.1.4 - Si la prediccion va 2 s adelantada (reloj o TLE viejos), lo
    que queda tras corregir es un residuo: maximo 246.3 Hz, cerca del
    cenit. residuo = error de tiempo x tasa. Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Lo que queda"), zona="arriba",
                   run_time=0.6)
        self.wait(0.4)

        t_min = T_P / 60.0
        dop_khz = DOP / 1000.0
        pred_khz = np.interp(T_P + ERR_T, T_P, DOP) / 1000.0
        residuo_hz = RESIDUO

        # --- panel A: lo medido (ambar) y lo predicho (fucsia, +2 s) -------
        lim_a = DOP_MAX / 1000.0 * 1.2
        esp_a = S.Espectro(t_min, dop_khz, piso=-lim_a, techo=lim_a,
                           ancho=5.5, alto=3.5, color=C_SENAL, area=False)
        esp_a.move_to(UP * 0.35 + LEFT * 3.35)
        pred = esp_a.con_db(pred_khz, color=C_LO)
        pred_dash = DashedVMobject(pred.curva, num_dashes=40)
        et_a = tag_junto(esp_a, "medido y predicho", UP, buff=0.22,
                         font_size=20)
        u_xa = tag_junto(esp_a.ejes, "min", DOWN, buff=0.16, font_size=15)
        u_ya = tag_hud("kHz", font_size=15, color=C_TENUE)
        u_ya.next_to(esp_a.en(t_min[0], lim_a), LEFT, buff=0.15)

        # --- panel B: lo que sobra (cian) -----------------------------------
        esp_b = S.Espectro(t_min, residuo_hz, piso=0.0, techo=RES_MAX * 1.2,
                           ancho=5.5, alto=3.5, color=C_CALCULO, area=True)
        esp_b.move_to(UP * 0.35 + RIGHT * 3.35)
        et_b = tag_junto(esp_b, "el residuo", UP, buff=0.22,
                         font_size=20)
        u_xb = tag_junto(esp_b.ejes, "min", DOWN, buff=0.16, font_size=15)
        u_yb = tag_hud("Hz", font_size=15, color=C_TENUE)
        u_yb.next_to(esp_b.en(t_min[0], RES_MAX * 1.2), LEFT, buff=0.15)

        self.play(Create(esp_a.ejes), FadeIn(et_a), FadeIn(u_xa),
                  FadeIn(u_ya), run_time=0.7)
        self.wait(0.3)
        self.play(Create(esp_a.curva), run_time=2.6)
        self.wait(1.0)
        self.play(Create(pred_dash), run_time=1.8)
        self.wait(1.2)

        self.play(Create(esp_b.ejes), FadeIn(et_b), FadeIn(u_xb),
                  FadeIn(u_yb), run_time=0.7)
        self.wait(0.3)
        self.play(Create(esp_b.curva), FadeIn(esp_b.area), run_time=2.4)
        self.wait(1.0)

        i_pico = int(np.argmax(np.abs(residuo_hz)))
        pico = Dot(esp_b.en(t_min[i_pico], residuo_hz[i_pico]), radius=0.09,
                  color=C_CALCULO)
        et_pico = tag_hud(f"{fmt(RES_MAX, 1)} Hz", font_size=21)
        et_pico.next_to(pico, RIGHT, buff=0.2)
        self.play(FadeIn(pico, scale=1.6), FadeIn(et_pico), run_time=0.6)
        self.wait(1.6)

        rot.mostrar(dato_pie("reloj 2 s adelantado"), zona="abajo",
                   run_time=0.5)
        self.wait(2.0)
        rot.mostrar(formula_pie(
            rf"{fmt(ERR_T, 0)}\,\text{{s}} \times {fmt(TASA_MAX, 1)}\,"
            rf"\text{{Hz/s}} \approx {fmt(RES_MAX, 0)}\,\text{{Hz}}"),
            zona="abajo", run_time=0.5)
        self.wait(3.4)

        cierre_leccion(
            self, rot, "El satelite cambia de frecuencia",
            "y el receptor lo persigue.", esp_a, pred_dash, et_a, u_xa,
            u_ya, esp_b, et_b, u_xb, u_yb, pico, et_pico, espera=5.2)

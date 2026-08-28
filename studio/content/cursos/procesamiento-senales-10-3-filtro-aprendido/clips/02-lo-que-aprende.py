class Clip2(Scene):
    """10.3.2 - El momento de la leccion: los pesos aprendidos SON el
    filtro que diseñamos en el modulo 5, tallo a tallo y en frecuencia.
    (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("Lo que aprende"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        rango_h = (-0.06, 0.30)
        caja = dict(ancho=7.6, alto=2.0, eje_y=False)

        # --- el filtro que se diseño en el modulo 5 -----------------------
        sec_h = Secuencia(H_OBJETIVO, 0, rango_h, color=C_MUESTRA,
                          radio=0.085, grosor=5.0, **caja)
        sec_h.move_to(UP * 1.75)
        et_h = tag_hud("h[n] modulo 5", font_size=19, color=C_MUESTRA)
        et_h.next_to(sec_h, LEFT, buff=0.22)
        self.play(FadeIn(sec_h), FadeIn(et_h), run_time=1.0)
        self.wait(1.8)

        # --- lo que la red aprendio, por su cuenta ------------------------
        sec_w = Secuencia(W_APRENDIDO, 0, rango_h, color=C_APREND,
                          radio=0.040, grosor=2.0, **caja)
        sec_w.move_to(DOWN * 1.15)
        et_w = tag_hud("w aprendido", font_size=19, color=C_APREND)
        et_w.next_to(sec_w, RIGHT, buff=0.22)
        self.play(FadeIn(sec_w), FadeIn(et_w), run_time=1.0)
        self.wait(1.8)

        # --- superponerlos: coinciden tallo a tallo -----------------------
        salto = sec_h._origen() - sec_w._origen()
        self.play(VGroup(sec_w, et_w).animate.shift(salto), run_time=1.4)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"coseno {COS:.6f}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)
        rot.mostrar(cifra_pie(f"error rel {ERR_REL:.1e}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        # --- y en frecuencia, la misma curva ------------------------------
        rf_h = respuesta_dibujo(H_RESP[0], H_RESP[1], ancho=8.4, alto=2.3,
                                piso_db=-150.0, techo_db=6.0,
                                color=C_MUESTRA)
        rf_h.move_to(DOWN * 1.45)
        et_db = tag_hud("dB", font_size=17, color=C_TENUE)
        et_db.next_to(rf_h.en(H_RESP[0][0], 6.0), LEFT, buff=0.12)
        et_pi = tag_hud("w/pi", font_size=17, color=C_TENUE)
        et_pi.next_to(rf_h.en(H_RESP[0][-1], -150.0), DR, buff=0.10)
        self.play(FadeIn(rf_h.ejes), FadeIn(et_db), FadeIn(et_pi),
                  run_time=0.5)
        self.play(Create(rf_h.curva), run_time=1.5)
        self.add(rf_h.curva)
        self.wait(1.6)

        rf_w = rf_h.con_mag(W_RESP[1], color=C_APREND)
        rf_w.curva.set_stroke(width=1.6)
        self.play(Create(rf_w.curva), run_time=1.5)
        self.add(rf_w.curva)
        self.wait(2.0)

        rot.mostrar(cifra_pie(f"dif max {fmt(DIF_RESP, 4)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        self.play(FadeOut(et_h), FadeOut(et_w), run_time=0.6)
        panel = panel_cifras((f"coseno {COS:.6f}", C_CALCULO),
                             (f"error rel {ERR_REL:.1e}", C_CALCULO),
                             (f"dif {fmt(DIF_RESP, 4)} dB", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.2)
        rot.mostrar(formula_pie(rf"\cos\theta = {COS:.6f}"), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

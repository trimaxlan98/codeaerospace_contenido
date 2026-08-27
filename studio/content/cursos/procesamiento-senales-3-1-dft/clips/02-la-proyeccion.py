class Clip2(Scene):
    """3.1.2 - Multiplicar la señal por el giro y SUMAR: si el giro
    coincide con la señal la suma se aleja; si no, se cierra. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("La proyeccion"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la señal -----------------------------------------------------
        sec = Secuencia(X_BIN, 0, (-1.25, 1.25), ancho=5.4, alto=1.7,
                        color=C_SENAL)
        sec.move_to(UP * 2.15)
        et_x = tag_hud("x[n]", font_size=19, color=C_SENAL)
        et_x.next_to(sec, LEFT, buff=0.28)
        self.play(FadeIn(sec), FadeIn(et_x), run_time=0.9)
        self.wait(1.4)

        # --- el camino de la suma, con el giro que SI coincide ------------
        pz = plano_z(unidad=0.42, alcance=9.5)
        pz.remove(pz.circulo)
        pz.move_to(DOWN * 1.25)
        self.play(FadeIn(pz.ejes), run_time=0.5)

        cam_b = VMobject(color=C_CALCULO, stroke_width=3.0)
        cam_b.set_points_as_corners([pz.en(0)] +
                                    [pz.en(z) for z in CAMINO_BUENO])
        et_k3 = tag_hud(f"k = {K_BUENO}", font_size=20, color=C_CALCULO)
        et_k3.next_to(pz.en(CAMINO_BUENO[-1]), UR, buff=0.14)
        self.play(Create(cam_b), run_time=2.8)
        self.play(FadeIn(Dot(pz.en(CAMINO_BUENO[-1]), radius=0.075,
                             color=C_CALCULO)), FadeIn(et_k3), run_time=0.6)
        rot.mostrar(cifra_pie(f"suma = {fmt(SUMA_BUENA, 3)}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        # --- y con el giro que NO ------------------------------------------
        cam_m = VMobject(color=C_RUIDO, stroke_width=3.0)
        cam_m.set_points_as_corners([pz.en(0)] +
                                    [pz.en(z) for z in CAMINO_MALO])
        et_k5 = tag_hud(f"k = {K_MALO}", font_size=20, color=C_RUIDO)
        # El camino que se cancela se queda pegado al origen: la etiqueta
        # NO puede colgarse de el (se le monta encima). Va debajo del eje.
        et_k5.next_to(pz.en(0), DOWN, buff=0.62)
        fin_malo = Dot(pz.en(CAMINO_MALO[-1]), radius=0.075, color=C_RUIDO)
        self.play(cam_b.animate.set_stroke(opacity=0.28),
                  FadeOut(et_k3), run_time=0.6)
        self.play(Create(cam_m), run_time=2.8)
        self.play(FadeIn(et_k5), FadeIn(fin_malo), run_time=0.4)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"suma = {SUMA_MALA:.1e}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        panel = panel_cifras((f"k = {K_BUENO}: {fmt(SUMA_BUENA, 3)}",
                              C_CALCULO),
                             (f"k = {K_MALO}: {SUMA_MALA:.0e}", C_RUIDO))
        self.play(cam_b.animate.set_stroke(opacity=1.0), FadeIn(panel),
                  run_time=0.8)
        self.wait(2.6)
        rot.mostrar(formula_pie(r"X[k] = \sum_n x[n]\,e^{-j\,2\pi k n/N}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

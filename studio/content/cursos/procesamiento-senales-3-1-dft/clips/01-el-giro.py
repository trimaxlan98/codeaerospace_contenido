class Clip1(Scene):
    """3.1.1 - La regla con la que la DFT pregunta: un giro que da k
    vueltas mientras la señal avanza N muestras. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("El giro"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        pz = plano_z(unidad=1.75, alcance=2.05)
        pz.move_to(LEFT * 3.1 + DOWN * 0.25)
        et_re = tag_hud("Re", font_size=18, color=C_TENUE)
        et_re.next_to(pz.en(2.05), RIGHT, buff=0.10)
        et_im = tag_hud("Im", font_size=18, color=C_TENUE)
        et_im.next_to(pz.en(2.05j), UP, buff=0.10)
        self.play(FadeIn(pz.ejes), FadeIn(et_re), FadeIn(et_im),
                  run_time=0.6)
        self.play(Create(pz.circulo), run_time=1.2)
        self.wait(0.6)

        # --- k = 1: una vuelta en N muestras ------------------------------
        g1 = giro(1, N_DFT)
        puntos1 = VGroup(*[Dot(pz.en(z), radius=0.062, color=C_MUESTRA)
                           for z in g1])
        camino1 = VMobject(color=C_MUESTRA, stroke_width=1.6,
                           stroke_opacity=0.55)
        camino1.set_points_as_corners([pz.en(z) for z in g1] + [pz.en(g1[0])])
        panel = panel_cifras(f"N = {N_DFT}", ("k = 1", C_MUESTRA))
        self.play(FadeIn(panel), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(p, scale=0.4) for p in puntos1],
                              lag_ratio=0.09), run_time=2.6)
        self.play(Create(camino1), run_time=1.4)
        self.wait(2.0)

        # --- k = 3: tres vueltas en las mismas N muestras -----------------
        g3 = giro(K_BUENO, N_DFT)
        puntos3 = VGroup(*[Dot(pz.en(z), radius=0.062, color=C_CALCULO)
                           for z in g3])
        camino3 = VMobject(color=C_CALCULO, stroke_width=1.8,
                           stroke_opacity=0.8)
        camino3.set_points_as_corners([pz.en(z) for z in g3] + [pz.en(g3[0])])
        panel3 = panel_cifras(f"N = {N_DFT}",
                              (f"k = {K_BUENO}", C_CALCULO))
        self.play(FadeOut(camino1), FadeOut(puntos1),
                  Transform(panel, panel3), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(p, scale=0.4) for p in puntos3],
                              lag_ratio=0.07), run_time=2.2)
        self.play(Create(camino3), run_time=2.2)
        self.wait(3.4)

        # --- el mismo giro, visto como muestras ---------------------------
        sec = Secuencia(np.real(g3), 0, (-1.25, 1.25), ancho=5.2, alto=1.9,
                        color=C_CALCULO)
        sec.move_to(RIGHT * 3.6 + DOWN * 0.45)
        et_sec = tag_hud("parte real", font_size=18, color=C_TENUE)
        et_sec.next_to(sec, DOWN, buff=0.22)
        self.play(FadeIn(sec.ejes), FadeIn(et_sec), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in range(N_DFT)],
                              lag_ratio=0.05),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in range(N_DFT)],
                              lag_ratio=0.05), run_time=1.8)
        self.wait(2.2)

        rot.mostrar(formula_pie(r"e^{-j\,2\pi k n / N}"), zona="abajo",
                    run_time=0.5)
        self.wait(5.4)

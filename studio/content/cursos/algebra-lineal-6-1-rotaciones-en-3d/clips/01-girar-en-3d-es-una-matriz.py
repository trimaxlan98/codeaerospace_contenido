class Clip1(Scene):
    """6.1.1 - En 3D girar tambien es una matriz: sus tres columnas dicen a
    donde van los tres ejes, y su determinante sigue valiendo 1. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Girar en 3D es una matriz")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el espacio y los tres ejes del cuerpo ----------------
        esp = espacio3(unidad=0.9, alcance=3)
        esp.move_to(LEFT * 1.15 + DOWN * 0.25)
        # La rejilla fija (gris) sube de opacidad: cuando la viva (azul) gire
        # hay que ver CONTRA que gira (trampa heredada de 3.3).
        esp.suelo.set_stroke(opacity=0.95)
        self.play(FadeIn(esp), run_time=0.9)
        rot.mostrar(pie_curso("El plano se queda corto: aquí hay tres ejes. "
                              "x ámbar, y cian, z violeta."),
                    zona="abajo", run_time=0.5)
        tri = triada3(esp, np.eye(3), largo=LARGO_TRIADA)
        self.play(*[GrowArrow(e.flecha) for e in tri.ejes], run_time=0.9)
        self.wait(3.9)

        # --- momento: el giro -----------------------------------------------
        rot.mostrar(pie_curso("Una guiñada: " + fmt(ANG_Z, 0)
                              + " grados alrededor del eje z. El suelo gira "
                              "con los ejes."), zona="abajo", run_time=0.5)
        self.wait(0.5)
        self.play(*esp.anim_matriz(R_Z, *tri.ejes), run_time=2.4)
        self.wait(2.6)

        # --- momento: los nueve numeros -------------------------------------
        rot.mostrar(pie_curso("Todo ese giro cabe en nueve números."),
                    zona="abajo", run_time=0.5)
        mat = matriz_columnas(R_Z, dec=DEC_R, font_size=30)
        det = tag_hud("det R = " + fmt(DET_RZ, 1), font_size=18)
        panel = panel_derecha(mat, det, buff=0.3)
        self.play(FadeIn(panel[0]), FadeIn(mat), run_time=0.7)
        self.wait(4.6)

        rot.mostrar(pie_curso("Cada columna dice a dónde fue un eje: la "
                              "primera es la nueva x, la segunda la nueva y."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(mat.columna(0), color=C_I, scale_factor=1.12),
                  Indicate(tri.ejes[0], color=C_I, scale_factor=1.06),
                  run_time=0.9)
        self.play(Indicate(mat.columna(1), color=C_J, scale_factor=1.12),
                  Indicate(tri.ejes[1], color=C_J, scale_factor=1.06),
                  run_time=0.9)
        self.wait(3.4)

        rot.mostrar(pie_curso("La tercera es la nueva z: no se movió, porque "
                              "z es el eje del giro."), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(mat.columna(2), color=C_K, scale_factor=1.12),
                  Indicate(tri.ejes[2], color=C_K, scale_factor=1.06),
                  run_time=0.9)
        self.wait(4.0)

        rot.mostrar(pie_curso("Y el determinante vale uno: girar no estira ni "
                              "encoge nada."), zona="abajo", run_time=0.5)
        self.play(FadeIn(det, shift=0.12 * UP), run_time=0.6)
        self.wait(4.6)

class Clip2(Scene):
    """6.1.2 - Alabeo y luego guiñada: el resultado no son dos giros, es UN
    giro, y su matriz es el producto. Sigue siendo ortogonal. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Dos giros hacen un giro")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # unidad 0.8 (y no 0.9): bajo R_z R_x el suelo vivo se pone casi
        # vertical y con 0.9 su esquina inferior aterriza sobre el pie.
        esp = espacio3(unidad=0.8, alcance=3)
        esp.move_to(LEFT * 1.15 + UP * 0.18)
        esp.suelo.set_stroke(opacity=0.95)
        self.play(FadeIn(esp), run_time=0.9)
        rot.mostrar(pie_curso("Los mismos tres ejes. Ahora dos maniobras, "
                              "una detrás de otra."), zona="abajo",
                    run_time=0.5)
        tri = triada3(esp, np.eye(3), largo=LARGO_TRIADA)
        self.play(*[GrowArrow(e.flecha) for e in tri.ejes], run_time=0.8)
        self.wait(3.4)

        # --- momento: primero el alabeo -------------------------------------
        rot.mostrar(pie_curso("Primero un alabeo: " + fmt(ANG_X, 0)
                              + " grados alrededor del eje x."),
                    zona="abajo", run_time=0.5)
        self.wait(0.4)
        self.play(*esp.anim_matriz(R_X, *tri.ejes), run_time=2.0)
        et_x = tag_hud("R_x  alabeo " + fmt(ANG_X, 0), font_size=17)
        mat_x = matriz_columnas(R_X, dec=DEC_R, font_size=26)
        panel_x = panel_derecha(et_x, mat_x, buff=0.2)
        self.play(FadeIn(panel_x, shift=0.15 * LEFT), run_time=0.6)
        self.wait(2.4)

        # --- momento: encima, la guiñada ------------------------------------
        rot.mostrar(pie_curso("Encima, la guiñada de antes: " + fmt(ANG_Z, 0)
                              + " grados alrededor del eje z."),
                    zona="abajo", run_time=0.5)
        self.wait(0.4)
        # anim_matriz es el estado TOTAL desde la identidad: se pasa el
        # PRODUCTO R_Z @ R_X, no el incremento R_Z.
        self.play(*esp.anim_matriz(R_COMP, *tri.ejes), run_time=2.0)
        et_c = tag_hud("R = Rz Rx", font_size=17)
        mat_c = matriz_columnas(R_COMP, dec=DEC_R, font_size=26)
        t_det = tag_hud("det R = " + fmt(DET_COMP, 1), font_size=17)
        t_ort = tag_hud("R^T R = I : "
                        + ("si" if ORTO_COMP else "no"), font_size=17)
        t_len = tag_hud("|columnas| = " + ", ".join(fmt(l, 1)
                                                   for l in LONG_COLS),
                        font_size=17)
        panel_c = panel_derecha(et_c, mat_c, t_det, t_ort, t_len, buff=0.2)
        # Transform entre dos paneles de distinta estructura morphea glifos
        # rotos: relevo con FadeOut + FadeIn.
        self.play(FadeOut(panel_x), run_time=0.4)
        self.play(FadeIn(panel_c[0]), FadeIn(et_c), FadeIn(mat_c),
                  run_time=0.6)
        self.wait(2.4)

        # --- momento: es UN giro --------------------------------------------
        rot.mostrar(pie_curso("El cuerpo no quedó a medio camino: quedó "
                              "girado. Un solo giro, otra vez."),
                    zona="abajo", run_time=0.5)
        # Indicate sobre la matriz entera la pinta toda de cian y borra el
        # codigo de columnas: se subraya la triada, cada eje en su color.
        self.play(*[Indicate(tri.ejes[k], color=c, scale_factor=1.06)
                    for k, c in enumerate((C_I, C_J, C_K))], run_time=0.9)
        self.wait(4.0)

        rot.mostrar(formula_pie(r"R = R_z\,R_x"), zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- momento: sigue siendo una rotacion -----------------------------
        rot.mostrar(pie_curso("Y sigue siendo una rotación: las columnas "
                              "miden uno y siguen siendo perpendiculares."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(t_det, shift=0.1 * UP),
                  FadeIn(t_ort, shift=0.1 * UP),
                  FadeIn(t_len, shift=0.1 * UP), run_time=0.7)
        self.wait(4.4)

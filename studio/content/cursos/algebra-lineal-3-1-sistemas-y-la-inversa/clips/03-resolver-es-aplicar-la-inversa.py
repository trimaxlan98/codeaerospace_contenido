class Clip3(Scene):
    """3.1.3 - Resolver Ax = b es aplicar A^-1 a b: se ve a b (verde)
    transformarse en x (rojo) mientras la rejilla se deforma con A^-1, y se
    comprueba la cuenta con numeros. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Resolver es aplicar la inversa")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion(vivo=True)
        b = vector(pl, B_VEC, color=C_IMG, nombre=r"\vec b")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Partimos de b y de la rejilla original. "
                              "¿Quién le dio origen?"), zona="abajo",
                    run_time=0.5)
        self.play(GrowArrow(b.flecha), FadeIn(b.etiqueta), run_time=0.9)
        self.wait(3.5)

        # --- momento: aplicar A^-1 a b, junto con la rejilla ------------------
        rot.mostrar(pie_curso("Aplicamos A elevado a menos uno: la rejilla "
                              "se deforma y b se convierte en x."),
                    zona="abajo", run_time=0.5)
        destino = b.con_matriz(A_INV, color=C_VEC, nombre=r"\vec x")
        anims = pl.anim_matriz(A_INV)
        anims.append(Transform(b, destino))
        self.play(*anims, run_time=2.4)
        # b es, EN SITIO, el objeto que Transform mutó a la forma de
        # "destino" (destino en si nunca se anadio a la escena). Seguimos
        # usando b como el x visible: si en su lugar reasignaramos
        # x = destino y luego animaramos x.flecha, el play() colaria a
        # destino como una flecha fantasma nueva ademas de la que ya esta
        # en pantalla.
        self.wait(3.3)

        # --- momento: la cuenta con numeros -------------------------------
        cuenta = (r"\vec x = A^{-1}\vec b = " + matriz_tex(A_INV, 2)
                  + r"\begin{bmatrix}" + fmt(B_VEC[0], 0) + r" \\ "
                  + fmt(B_VEC[1], 0) + r"\end{bmatrix}")
        rot.mostrar(formula_pie(cuenta, font_size=30), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        etiqueta_x = MathTex(r"\vec x =", font_size=34, color=C_TITULO)
        resultado = vector_columna(X_SOL, color=C_VEC, font_size=40)
        fila_x = VGroup(etiqueta_x, resultado).arrange(RIGHT, buff=0.22)
        panel = panel_derecha(fila_x)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.play(Indicate(b.flecha, color=C_VEC, scale_factor=1.05),
                  Indicate(resultado, color=C_VEC, scale_factor=1.05),
                  run_time=0.9)
        self.wait(3.0)

        # --- momento: la comprobacion ---------------------------------------
        comprobacion = (r"A\vec x = " + matriz_tex(CHEQUEO.reshape(-1, 1), 0)
                        + r" = \vec b")
        rot.mostrar(formula_pie(comprobacion), zona="abajo", run_time=0.5)
        self.wait(6.6)

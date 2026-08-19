class Clip3(Scene):
    """6.2.3 - Perpendicular = producto punto cero, tambien en R^12: cos 1 y
    sin 1 se cancelan termino a termino, y la base entera es ortonormal.
    (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        hud = hud_modulo("Modulo 03")
        self.add(hud)

        titulo = titulo_curso("Senos que no se estorban")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: perpendicular, en el plano de siempre -----------------
        pie_plano = pie_curso("En el plano ya lo sabíamos: perpendicular "
                              "quiere decir producto punto cero.")
        rot.mostrar(pie_plano, zona="abajo", run_time=0.5)
        pl = plano_leccion(vivo=False)
        pl.fijo.set_stroke(opacity=0.9)
        u = vector(pl, U_PERP, color=C_VEC, nombre=r"\vec u")
        w = vector(pl, W_PERP, color=C_VEC_2, nombre=r"\vec w")
        ang = marca_angulo(pl, U_PERP, W_PERP, radio=0.62, color=C_CALCULO)
        cifra_2d = tag_hud("u . w = " + fmt(DOT_PERP, 1), font_size=20)
        cifra_2d.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(pl), run_time=0.6)
        # El plano entra despues del pie y del titulo: sin esto la rejilla
        # se dibuja ENCIMA de sus letras.
        self.bring_to_front(pie_plano, titulo, hud)
        self.play(GrowArrow(u.flecha), GrowArrow(w.flecha), run_time=0.9)
        self.play(FadeIn(u.etiqueta), FadeIn(w.etiqueta), run_time=0.3)
        self.play(Create(ang.arco), FadeIn(ang.texto), FadeIn(cifra_2d),
                  run_time=0.7)
        self.wait(3.6)

        # --- geometria de las filas ---------------------------------------
        X_B, ANCHO_B = -2.5, 0.30
        Y_C, Y_S, Y_P = 1.75, 0.35, -1.35
        X_DER = 3.6

        def fila(valores, color, y, escala):
            b = barras(valores, colores=color, ancho=ANCHO_B, alto=1.0,
                       escala=escala)
            b.shift(np.array([X_B, y, 0.0]) - b.base.get_center())
            return b

        def rotulo(texto, color, y, dy=0.0):
            t = tag_hud(texto, font_size=16, color=color)
            t.move_to(np.array([X_B - 6.0 * ANCHO_B - 1.30, y + dy, 0.0]))
            return t

        def crecer(b, valores):
            return [GrowFromEdge(r, DOWN if v >= 0 else UP)
                    for r, v in zip(b.barras, valores)]

        # --- momento: dos de las doce direcciones --------------------------
        rot.mostrar(pie_curso("En R de doce, dos funciones de la base: el "
                              "coseno y el seno de una vuelta."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(pl), FadeOut(u), FadeOut(w), FadeOut(ang),
                  FadeOut(cifra_2d), run_time=0.6)
        fila_c = fila(COS_1, C_I, Y_C, ESC_3)
        fila_s = fila(SIN_1, C_J, Y_S, ESC_3)
        rot_c = rotulo(TAGS_B[1], C_I, Y_C)
        rot_s = rotulo(TAGS_B[2], C_J, Y_S)
        self.play(FadeIn(fila_c.base), FadeIn(rot_c), *crecer(fila_c, COS_1),
                  run_time=0.9)
        self.play(FadeIn(fila_s.base), FadeIn(rot_s), *crecer(fila_s, SIN_1),
                  run_time=0.9)
        self.wait(3.4)

        # --- momento: el producto se cancela --------------------------------
        rot.mostrar(pie_curso("Multiplica barra con barra: la mitad sale "
                              "positiva y la otra mitad, negativa."),
                    zona="abajo", run_time=0.5)
        fila_p = fila(PROD_CS, C_IMG, Y_P, ESC_3P)
        rot_p = rotulo("producto", C_IMG, Y_P, dy=0.16)
        rot_p2 = rotulo("(otra escala)", C_TENUE, Y_P, dy=-0.16)
        rot_p2.set_opacity(0.8)
        cifra_cs = tag_hud("cos 1 . sin 1 = " + fmt(DOT_CS, 2), font_size=19)
        cifra_cs.move_to(np.array([X_DER, 2.15, 0.0]))
        self.play(FadeIn(fila_p.base), FadeIn(rot_p), FadeIn(rot_p2),
                  *crecer(fila_p, PROD_CS), run_time=1.0)
        self.play(FadeIn(cifra_cs, shift=0.12 * LEFT), run_time=0.5)
        self.wait(3.8)

        # --- momento: consigo mismo, en cambio ------------------------------
        rot.mostrar(pie_curso("Consigo mismo no: todos los productos salen "
                              "positivos y suman uno. Está normalizado."),
                    zona="abajo", run_time=0.5)
        cifra_cc = tag_hud("cos 1 . cos 1 = " + fmt(DOT_CC, 2), font_size=19)
        cifra_cc.move_to(np.array([X_DER, 1.55, 0.0]))
        rot_p3 = rotulo("cuadrado", C_IMG, Y_P, dy=0.16)
        self.play(Transform(fila_p, fila(PROD_CC, C_IMG, Y_P, ESC_3P)),
                  FadeOut(rot_p), FadeIn(rot_p3),
                  Indicate(fila_c, color=C_I, scale_factor=1.05),
                  run_time=1.3)
        self.play(FadeIn(cifra_cc, shift=0.12 * LEFT), run_time=0.5)
        self.wait(3.6)

        # --- momento: la base entera --------------------------------------
        rot.mostrar(pie_curso("Y así las siete: ninguna se estorba con "
                              "ninguna. Eso es una base ortonormal."),
                    zona="abajo", run_time=0.5)
        gram = pixeles(GRAM, lado=0.30)
        gram.move_to(np.array([X_DER, -0.85, 0.0]))
        ley = MathTex(r"B^{\top} B = I", font_size=34, color=C_CALCULO)
        ley.move_to(np.array([X_DER, 0.75, 0.0]))
        pie_gram = tag_hud("7 x 7 productos punto", font_size=15,
                           color=C_TENUE)
        pie_gram.move_to(np.array([X_DER, -2.15, 0.0]))
        self.play(FadeIn(ley), run_time=0.5)
        self.play(FadeIn(gram, scale=0.85), FadeIn(pie_gram), run_time=0.8)
        self.wait(4.2)

class Clip1(Scene):
    """6.2.1 - Muestrear una funcion en 12 instantes la convierte en una
    lista de 12 numeros: un vector de R^12. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        hud = hud_modulo("Modulo 01")
        self.add(hud)

        titulo = titulo_curso("Una función es una lista")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la curva continua -----------------------------------
        ancho_g = 6.6
        g = grafica(f_pulso, (0.0, 1.0), (0.0, 1.12), ancho=ancho_g, alto=2.4,
                    color=C_VEC, etiqueta_x="t", etiqueta_y="f")
        g.move_to(UP * 1.0)
        curva = g.curva
        g.remove(curva)
        rot.mostrar(pie_curso("Una función es un objeto continuo: un valor "
                              "para cada instante."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(g), run_time=0.5)
        self.play(Create(curva), run_time=1.2)
        # `curva` se quedo fuera de `g` a proposito: si se re-anade, el
        # FadeOut del grupo NO la apaga (quedo tambien suelta en la escena
        # tras el Create) y la curva sobrevive al cambio de momento.
        self.wait(3.9)

        # --- momento: mirarla solo en 12 instantes -------------------------
        rot.mostrar(pie_curso("Mírala solo en doce instantes: la curva se "
                              "queda en doce alturas."), zona="abajo",
                    run_time=0.5)
        cortes = VGroup(*[g.vertical_en(x, color=C_J) for x in XS])
        for c in cortes:
            c.set_stroke(opacity=0.5)
        marcas = VGroup(*[Dot(g.punto_de(x), radius=0.055, color=C_J)
                          for x in XS])
        self.play(Create(cortes), run_time=0.9)
        self.play(FadeIn(marcas, scale=0.6), run_time=0.7)
        self.wait(4.0)

        # --- momento: las doce alturas, en barras --------------------------
        rot.mostrar(pie_curso("Cada altura, una barra. Doce números en un "
                              "orden fijo."), zona="abajo", run_time=0.5)
        # El ancho de barra = el paso de muestreo en pantalla: cada barra
        # cae justo bajo su corte de la curva.
        bs = barras(V_PULSO, colores=C_VEC, ancho=ancho_g / N_MUESTRAS,
                    alto=1.15,
                    etiquetas=[str(i + 1) for i in range(N_MUESTRAS)],
                    font_size=13)
        # g.ejes[0] es el eje x completo: su centro ES el centro de la caja
        # (el bbox de `g` incluye las etiquetas y se desplaza un pelo).
        bs.shift(np.array([g.ejes[0].get_center()[0], -1.72, 0.0])
                 - bs.base.get_center())
        resto = VGroup(*[m for m in bs.submobjects if m not in bs.barras])
        self.play(FadeIn(resto), run_time=0.4)
        self.play(*[GrowFromEdge(b, DOWN) for b in bs.barras], run_time=1.2)
        self.wait(3.8)

        # --- momento: eso es un vector de R^12 -----------------------------
        rot.mostrar(pie_curso("Doce números en columna: exactamente lo que "
                              "hasta ahora llamábamos vector."), zona="abajo",
                    run_time=0.5)
        filas = [fmt(V_PULSO[0], 2), fmt(V_PULSO[1], 2), fmt(V_PULSO[2], 2),
                 r"\vdots", fmt(V_PULSO[10], 2), fmt(V_PULSO[11], 2)]
        columna = MathTex(r"\vec f = \begin{bmatrix}"
                          + r" \\ ".join(filas) + r"\end{bmatrix}",
                          font_size=32, color=C_VEC)
        pertenece = MathTex(r"\vec f \in \mathbb{R}^{12}", font_size=32,
                            color=C_CALCULO)
        panel = panel_derecha(columna, pertenece, buff=0.3)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.2)

        # --- momento: R^12 no cabe; dos de sus doce coordenadas si ---------
        pie_plano = pie_curso("R de doce no cabe en la pantalla. Dos de sus "
                              "doce coordenadas, sí.")
        rot.mostrar(pie_plano, zona="abajo", run_time=0.5)
        self.play(FadeOut(g), FadeOut(curva), FadeOut(cortes),
                  FadeOut(marcas), FadeOut(bs), FadeOut(panel), run_time=0.7)
        pl = plano_leccion(unidad=2.0, vivo=False)
        pl.fijo.set_stroke(opacity=0.9)
        v = vector(pl, V_PAR, color=C_VEC, nombre=r"(x_5,\, x_6)",
                   etiqueta_dir=np.array([-0.7, 0.75, 0.0]))
        cifras = tag_hud("x5 = " + fmt(V_PAR[0], 2) + "   x6 = "
                         + fmt(V_PAR[1], 2), font_size=19)
        cifras.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(pl), run_time=0.7)
        # El plano entra despues del pie y del titulo: sin esto la rejilla
        # se dibuja ENCIMA de sus letras.
        self.bring_to_front(pie_plano, titulo, hud)
        self.play(GrowArrow(v.flecha), run_time=0.8)
        self.play(FadeIn(v.etiqueta), FadeIn(cifras), run_time=0.4)
        self.wait(4.4)

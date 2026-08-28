class Clip4(Scene):
    """7.2.4 - La cura: mas bits, o romper la realimentacion exacta. El
    cuantizador esta DENTRO del lazo, y eso no existe en coma flotante.
    (~37 s)"""

    N_DIB = 48

    def _caja(self, etiqueta, color, ancho=1.75, alto=0.9, mat=True):
        c = Rectangle(width=ancho, height=alto, color=color,
                      stroke_width=2.2, fill_color=CODE_BG,
                      fill_opacity=1.0)
        t = (MathTex(etiqueta, font_size=32, color=color) if mat
             else Text(etiqueta, font_size=30, color=color))
        t.move_to(c.get_center())
        return VGroup(c, t)

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("La cura"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- el lazo: el cuantizador esta DENTRO -------------------------
        y_lazo = 0.55
        caja_z = self._caja(r"z^{-1}", C_EJE).move_to(LEFT * 3.4
                                                      + UP * y_lazo)
        mult = VGroup(Circle(radius=0.42, color=C_MUESTRA, stroke_width=2.2,
                             fill_color=CODE_BG, fill_opacity=1.0))
        et_a = MathTex(r"\times a", font_size=28, color=C_MUESTRA)
        et_a.move_to(mult.get_center())
        mult.add(et_a)
        mult.move_to(UP * y_lazo)
        caja_q = self._caja("Q", C_RUIDO, ancho=1.2, mat=False)
        caja_q.move_to(RIGHT * 3.4 + UP * y_lazo)

        f1 = conectar(caja_z, mult, color=C_EJE)
        f2 = conectar(mult, caja_q, color=C_EJE)
        esquinas = [np.array([4.25, y_lazo, 0.0]),
                    np.array([5.35, y_lazo, 0.0]),
                    np.array([5.35, -1.25, 0.0]),
                    np.array([-5.35, -1.25, 0.0]),
                    np.array([-5.35, y_lazo, 0.0])]
        retorno = VMobject(color=C_EJE, stroke_width=2.4)
        retorno.set_points_as_corners(esquinas)
        f3 = Arrow(esquinas[-1], caja_z.get_left(), buff=0.06, color=C_EJE,
                   stroke_width=2.4, max_tip_length_to_length_ratio=0.22)

        et_x = tag_hud("x[n] = 0", font_size=18, color=C_TENUE)
        et_x.next_to(caja_z, UP, buff=0.34)
        et_y = tag_hud("y[n]", font_size=18, color=C_SALIDA)
        et_y.next_to(caja_q, UP, buff=0.34)
        et_yr = tag_hud("y[n-1]", font_size=18, color=C_TENUE)
        et_yr.next_to(esquinas[2] * 0 + np.array([0.0, -1.25, 0.0]), DOWN,
                      buff=0.16)

        self.play(FadeIn(caja_z), FadeIn(mult), FadeIn(caja_q), run_time=0.9)
        self.play(Create(f1), Create(f2), run_time=0.6)
        self.play(Create(retorno), Create(f3), FadeIn(et_yr), run_time=1.0)
        self.play(FadeIn(et_x), FadeIn(et_y), run_time=0.5)
        rot.mostrar(formula_pie(r"y[n] = Q\!\left(a\, y[n-1]\right)"),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)

        lazo = [f1, f2, retorno, f3]
        self.play(flujo(lazo, color=C_SALIDA, por_conexion=0.5))
        self.wait(0.6)

        marco = SurroundingRectangle(caja_q, color=C_RUIDO, buff=0.16,
                                     stroke_width=2.6)
        # Rajdhani a 18 px junta las palabras de un rotulo de cuatro
        # ("Qdentrodellazo"): esta va en Space Mono.
        et_q = tag_hud("Q dentro del lazo", font_size=18, color=C_RUIDO)
        et_q.next_to(caja_q, DOWN, buff=0.30)
        self.play(Create(marco), FadeIn(et_q), run_time=0.8)
        self.wait(2.6)

        # --- romper la realimentacion exacta ------------------------------
        nodo_d = Circle(radius=0.13, color=C_MUESTRA, stroke_width=2.2,
                        fill_color=CODE_BG, fill_opacity=1.0)
        nodo_d.move_to(np.array([1.5, -0.62, 0.0]))
        f_d = Arrow(nodo_d.get_top(), np.array([1.5, y_lazo - 0.04, 0.0]),
                    buff=0.06, color=C_MUESTRA, stroke_width=2.4,
                    max_tip_length_to_length_ratio=0.22)
        et_d = tag_hud("dither", font_size=18, color=C_MUESTRA)
        et_d.next_to(nodo_d, RIGHT, buff=0.16)
        self.play(FadeIn(nodo_d), Create(f_d), FadeIn(et_d), run_time=0.8)
        self.wait(2.4)

        # --- la otra cura, medida: mas bits --------------------------------
        self.play(FadeOut(VGroup(caja_z, mult, caja_q, f1, f2, retorno, f3,
                                 et_x, et_y, et_yr, marco, et_q, nodo_d,
                                 f_d, et_d)), run_time=0.8)

        n = self.N_DIB
        b_malo, b_bueno = BITS_CL[0], BITS_CL[-1]
        malo = Secuencia(Y_POS[b_malo][0][:n], 0, (0.0, 0.5), ancho=8.6,
                         alto=1.5, color=C_RUIDO, radio=0.034)
        malo.move_to(LEFT * 0.55 + UP * 1.15)
        bueno = Secuencia(Y_POS[b_bueno][0][:n], 0, (0.0, 0.5), ancho=8.6,
                          alto=1.5, color=C_SALIDA, radio=0.034)
        bueno.move_to(LEFT * 0.55 + DOWN * 0.75)
        et_malo = tag_hud(f"{b_malo} bits", font_size=18, color=C_RUIDO)
        et_malo.next_to(malo, LEFT, buff=0.24)
        et_bueno = tag_hud(f"{b_bueno} bits", font_size=18, color=C_SALIDA)
        et_bueno.next_to(bueno, LEFT, buff=0.24)
        v_malo = tag_hud(f"{fmt(ATRAPADA_POS[b_malo], 3)}", font_size=18,
                         color=C_CALCULO)
        v_malo.next_to(malo, RIGHT, buff=0.26)
        v_bueno = tag_hud(f"{fmt(ATRAPADA_POS[b_bueno], 4)}", font_size=18,
                          color=C_CALCULO)
        v_bueno.next_to(bueno, RIGHT, buff=0.26)

        self.play(FadeIn(malo.ejes), FadeIn(et_malo), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(malo.tallo(k)) for k in range(n)],
                              lag_ratio=0.025),
                  LaggedStart(*[FadeIn(malo.punto(k)) for k in range(n)],
                              lag_ratio=0.025), run_time=1.3)
        self.play(FadeIn(v_malo), run_time=0.35)
        rot.mostrar(cifra_pie(f"{b_malo} bits: "
                              f"{fmt(ATRAPADA_POS[b_malo] * 100, 1)} % "
                              f"de escala"), zona="abajo", run_time=0.5)
        self.wait(2.4)

        self.play(FadeIn(bueno.ejes), FadeIn(et_bueno), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(bueno.tallo(k)) for k in range(n)],
                              lag_ratio=0.025),
                  LaggedStart(*[FadeIn(bueno.punto(k)) for k in range(n)],
                              lag_ratio=0.025), run_time=1.3)
        self.play(FadeIn(v_bueno), run_time=0.35)
        rot.mostrar(cifra_pie(f"{b_bueno} bits: "
                              f"{fmt(ATRAPADA_POS[b_bueno], 4)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        razon = ATRAPADA_POS[b_malo] / ATRAPADA_POS[b_bueno]
        panel = panel_cifras(
            (f"{b_malo} bits = {fmt(ATRAPADA_POS[b_malo], 3)}", C_RUIDO),
            (f"{b_bueno} bits = {fmt(ATRAPADA_POS[b_bueno], 4)}", C_SALIDA),
            (f"razon = {fmt(razon, 0)}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie(f"4 bits mas: {fmt(razon, 0)} veces"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)

        cierre_leccion(self, rot, "Un filtro estable en el papel",
                       "puede no apagarse nunca.",
                       malo, bueno, et_malo, et_bueno, v_malo, v_bueno,
                       panel)

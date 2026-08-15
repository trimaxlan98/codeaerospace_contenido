class Clip3(Scene):
    """3 - Medir el aire. Una celda de 10 cm al vacio en un brazo del
    interferometro; al dejar entrar aire el indice sube a n - 1 = 2.7e-4, la
    luz va un poco mas despacio y las franjas corren: 85.3 franjas contadas
    con N = 2 L (n-1) / lambda. Nadie toco el aire. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Medir el aire"), zona="arriba",
                    run_time=0.6)

        # La celda (con sus dos lecturas a la derecha) arriba de la banda y
        # las franjas del detector abajo-izquierda; la formula y la cifra
        # quedan a la derecha de las franjas, sobre la marca de agua.
        celda = celda_gas(L=0.10, ancho=3.4, alto=1.60)
        celda.move_to(np.array([0.15, 1.05, 0.0]))

        patron = patron_franjas(0.0, 1.0, n_franjas=6, ancho=5.0, alto=1.25,
                                n_barras=140)
        patron.move_to(np.array([-1.10, -1.55, 0.0]))
        t_det = tag_junto(patron, "franjas del detector", DOWN, buff=0.20,
                          font_size=18, color=C_MEDIDA)

        # --- momento: la celda al vacio -------------------------------------
        rot.mostrar(pie_curso("En un brazo ponemos una celda de 10 "
                              "centímetros al vacío."), zona="abajo")
        self.play(FadeIn(celda, shift=0.12 * UP), run_time=1.0)
        self.wait(1.6)
        self.play(FadeIn(patron), run_time=1.0)
        self.play(FadeIn(t_det), run_time=0.5)
        self.wait(3.4)

        # --- momento: entra el aire -----------------------------------------
        rot.mostrar(pie_curso("Dejamos entrar aire: la luz va un poco más "
                              "despacio y las franjas corren."), zona="abajo")
        n1 = ValueTracker(0.0)

        def _llenar(mob):
            # `a_indice` DEVUELVE las franjas acumuladas: la fase del patron
            # sale de esa cuenta, no de un factor inventado.
            franjas = mob.a_indice(n1.get_value())
            patron.a_fase(TAU * franjas)

        # `a_indice` SUSTITUYE los dos mobjects de lectura; el renderer Cairo
        # congela la lista de mobiles al empezar el play y seguiria pintando
        # los de ARRANCAR encima de los nuevos toda la animacion. Se apagan
        # antes: la primera pasada del updater ya escribe los suyos.
        celda.lectura_n.set_opacity(0.0)
        celda.lectura_f.set_opacity(0.0)
        celda.add_updater(_llenar)
        self.play(n1.animate.set_value(2.7e-4), run_time=5.5,
                  rate_func=linear)
        celda.clear_updaters()
        self.wait(2.0)

        # --- momento: la cuenta ---------------------------------------------
        rot.mostrar(pie_curso("Ochenta y cinco franjas: el índice del aire "
                              "menos uno es 0.00027."), zona="abajo")
        eq = MathTex(r"N = \frac{2L\,(n-1)}{\lambda}", font_size=36,
                     color=C_MEDIDA)
        eq.move_to(np.array([4.05, -1.20, 0.0]))
        t_franjas = tag_hud(f"{FRANJAS_AIRE:.1f} franjas", font_size=17)
        t_franjas.move_to(np.array([4.05, -2.10, 0.0]))
        self.play(Write(eq), run_time=1.3)
        self.play(FadeIn(t_franjas, shift=0.10 * UP), run_time=0.5)
        self.wait(5.0)

        # --- cierre -----------------------------------------------------------
        rot.mostrar(pie_curso("Nadie tocó el aire. Lo midieron las franjas."),
                    zona="abajo")
        self.wait(5.0)

class Clip1(Scene):
    """2.3.1 - La estructura de la onda: E vertical, B perpendicular, los
    dos EN FASE, y el patron entero marchando a c.

    Se revela primero el campo electrico, luego el magnetico, se marcan los
    ceros comunes (el error clasico es dibujarlos desfasados), se pone la
    onda a andar y se acota lambda de cresta a cresta. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El campo que viaja solo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        onda = onda_em()
        onda.move_to(UP * 0.35 + RIGHT * 0.25)

        def cresta(pieza, k):
            """Cresta k del campo E (el localizador de la pieza ya ancla
            en coordenadas de construccion y sigue a cualquier move_to)."""
            return pieza.punto_cresta(k)

        # --- momento: el campo electrico -----------------------------------
        rot.mostrar(pie_curso("El campo eléctrico oscila en vertical: esa "
                              "es la onda ámbar."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(onda.eje), Create(onda.env_e),
                  FadeIn(onda.flechas_e), run_time=1.4)
        self.wait(4.6)

        # --- momento: el campo magnetico ------------------------------------
        rot.mostrar(pie_curso("Y con él, perpendicular, el magnético: la "
                              "onda verde que entra al papel."),
                    zona="abajo", run_time=0.5)
        self.play(Create(onda.env_b), FadeIn(onda.flechas_b), run_time=1.1)
        self.wait(4.6)

        # --- momento: van en fase -------------------------------------------
        # Los ceros se sacan de la propia pieza: un cuarto de longitud de
        # onda antes y despues de la cresta, proyectados sobre el eje.
        lam_escena = onda.lambda_escena()
        c0 = cresta(onda, 0)
        y_eje = onda.eje.get_center()[1]
        cero_a = np.array([c0[0] + lam_escena / 4, y_eje, 0.0])
        cero_b = np.array([c0[0] + 3 * lam_escena / 4, y_eje, 0.0])
        ceros = VGroup(Dot(cero_a, radius=0.065, color=C_CALCULO),
                       Dot(cero_b, radius=0.065, color=C_CALCULO))
        rot.mostrar(pie_curso("Van EN FASE: cruzan por cero juntos. "
                              "Dibujarlos desfasados es el error clásico."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(ceros, scale=1.6), run_time=0.5)
        self.wait(4.4)

        # --- momento: la marcha ---------------------------------------------
        self.add(onda)
        rot.mostrar(pie_curso("Nadie los sostiene: cada uno engendra al "
                              "otro y el patrón entero avanza a c."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(ceros), GrowArrow(onda.flecha_k), run_time=0.5)
        for fase in (1.2, 2.4, 3.6):
            nueva = onda.con_fase(fase)
            self.play(ReplacementTransform(onda, nueva), run_time=0.8,
                      rate_func=linear)
            onda = nueva
        self.wait(2.0)

        # --- momento: lambda acotada y c = lambda f --------------------------
        regla = Line(cresta(onda, 1), cresta(onda, 2), stroke_width=0)
        marca = llave(regla, direccion=UP)
        lam_tex = MathTex(r"\lambda", font_size=32, color=C_CALCULO)
        lam_tex.next_to(marca, UP, buff=0.10)
        c_tex = MathTex(r"c = \lambda\,f", font_size=40, color=C_CALCULO)
        c_tex.move_to(DOWN * 1.85)
        rot.mostrar(pie_curso("De cresta a cresta hay una longitud de "
                              "onda; y longitud por frecuencia es siempre "
                              "c."), zona="abajo", run_time=0.5)
        self.play(FadeIn(marca), FadeIn(lam_tex), FadeIn(c_tex),
                  run_time=0.9)
        self.wait(4.6)

        # --- momento: la cifra del plato de balcon ---------------------------
        cifra = tag_hud(f"{F_KU / 1e9:.0f} GHz  ->  lambda = "
                        f"{LAMBDA_KU * 1000:.0f} mm", font_size=20)
        cifra.move_to(DOWN * 2.55)
        rot.mostrar(pie_curso("A doce gigahercios, la banda del plato de "
                              "balcón, la onda mide 25 milímetros."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(cifra, shift=0.12 * UP), run_time=0.6)
        self.wait(4.8)

class Clip1(Scene):
    """1.1.1 - Una funcion de dos variables asigna un numero (la altura)
    a cada punto del plano; la tabla es infinita, hay que verla. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Un número para cada punto")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el plano es el dominio ------------------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Una función de dos variables toma un punto "
                              "del plano y devuelve un número."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(MathTex(r"f:\ \mathbb{R}^2 \to \mathbb{R}",
                                      font_size=36, color=C_TITULO))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.6)

        # --- momento: el primer punto y su altura -------------------------
        rot.mostrar(pie_curso("Aquí pensaremos ese número como una "
                              "ALTURA: el valor del terreno en el punto."),
                    zona="abajo", run_time=0.5)
        p0 = PUNTOS_MUESTRA[3]
        z0 = ALTURAS[3]
        dot0 = Dot(pl.p(p0), radius=0.09, color=color_calor(z0 / Z_MAX))
        cifra0 = tag_hud(f"f({fmt(p0[0])}, {fmt(p0[1])}) = {fmt(z0)}",
                         font_size=20, color=color_calor(z0 / Z_MAX))
        cifra0.next_to(dot0, UP, buff=0.18)
        self.play(FadeIn(dot0, scale=0.4), run_time=0.5)
        self.play(FadeIn(cifra0), run_time=0.4)
        self.wait(4.0)

        # --- momento: muchos puntos, muchas alturas -----------------------
        rot.mostrar(pie_curso("En cada punto, su altura: grandes en las "
                              "colinas, pequeñas en el llano."),
                    zona="abajo", run_time=0.5)
        marcas = VGroup()
        for (p, z) in zip(PUNTOS_MUESTRA, ALTURAS):
            if p == PUNTOS_MUESTRA[3]:
                continue
            c = color_calor(z / Z_MAX)
            d = Dot(pl.p(p), radius=0.07, color=c)
            t = tag_hud(fmt(z), font_size=18, color=c)
            t.next_to(d, UP, buff=0.14)
            marcas.add(VGroup(d, t))
        self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in marcas],
                              lag_ratio=0.25), run_time=2.4)
        self.wait(3.8)

        # --- momento: la tabla infinita no se puede leer ------------------
        rot.mostrar(pie_curso("La tabla completa tiene infinitas filas. "
                              "Nadie puede leerla: hay que VERLA."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(VGroup(dot0, cifra0), color=C_GRAD,
                           scale_factor=1.06), run_time=0.8)
        self.wait(4.0)

        rot.mostrar(pie_curso("Dos maneras de verla entera: como "
                              "superficie y como mapa. Vamos con la 3D."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

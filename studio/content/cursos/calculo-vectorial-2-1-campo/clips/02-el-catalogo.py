class Clip2(Scene):
    """2.1.2 - El catalogo cerrado: radial, rotor, silla y cizalla desfilan
    sobre la MISMA malla, con su formula cambiando antes del giro. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El catálogo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el plano y el primero de la familia -------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.7)
        rot.mostrar(pie_curso("Cuatro campos con carácter propio: cuatro "
                              "maneras de llenar el mismo plano."),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"F(x,y) = (x,\ y)"), zona="abajo",
                    run_time=0.5)
        campo = campo_flechas(pl, campo_radial, y0=-2.5, y1=2.5)
        self.play(FadeIn(campo), run_time=1.0)
        self.wait(1.6)
        rot.mostrar(pie_curso("Radial: todo huye del origen, cada flecha "
                              "es su propio punto, alargado."),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- momento: -> rotor ------------------------------------------------
        rot.mostrar(formula_pie(r"F(x,y) = (-y,\ x)"), zona="abajo",
                    run_time=0.5)
        self.play(Transform(campo, campo.con_campo(campo_rotor)),
                  run_time=1.8)
        self.wait(1.4)
        rot.mostrar(pie_curso("Rotor: gira alrededor del origen, siempre "
                              "perpendicular al radio."), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        # --- momento: -> silla ------------------------------------------------
        rot.mostrar(formula_pie(r"F(x,y) = (x,\ -y)"), zona="abajo",
                    run_time=0.5)
        self.play(Transform(campo, campo.con_campo(campo_silla)),
                  run_time=1.8)
        self.wait(1.4)
        rot.mostrar(pie_curso("Silla: entra por un eje y sale por el "
                              "otro. Ni fuente ni sumidero."),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- momento: -> cizalla ----------------------------------------------
        rot.mostrar(formula_pie(r"F(x,y) = (y,\ 0)"), zona="abajo",
                    run_time=0.5)
        self.play(Transform(campo, campo.con_campo(campo_cizalla)),
                  run_time=1.8)
        self.wait(1.4)
        rot.mostrar(pie_curso("Cizalla: todo va horizontal, pero más "
                              "rápido arriba que abajo."), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        # --- cierre de idea -----------------------------------------------------
        rot.mostrar(pie_curso("Cuatro personalidades, la misma receta: "
                              "una malla, una flecha por punto."),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

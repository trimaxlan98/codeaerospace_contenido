class Clip1(Scene):
    """1.2.1 - Gas ideal, ecuacion de estado y la constante R del aire.

    El embolo hace visible p V = m R T: mismo gas, mismas particulas, medio
    volumen, doble presion. Y despues el detalle que casi todo el mundo pasa
    por alto — que la R de la formula no es universal, es la del aire.
    (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El aire, como gas ideal")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: tres numeros describen el estado --------------------
        cilindro = piston_gas(1.0, n_particulas=52, largo=4.4,
                              alto=2.35)
        cilindro.move_to(UP * 0.05)
        self.play(FadeIn(cilindro), run_time=0.8)
        rot.mostrar(pie_curso("Tres números bastan para decir en qué estado "
                              "está el aire."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(formula_pie(r"p = \rho\,R\,T"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        # --- momento: apretar el gas --------------------------------------
        # El pie entra ANTES de las compresiones que ilustra, y cubre las
        # dos: partirlo en dos rotulos cortaria la subida a la mitad.
        rot.mostrar(pie_curso("A la mitad de volumen, el doble de presión. "
                              "A un tercio, el triple."), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)
        self.play(cilindro.a_fraccion(COMPRESIONES[0]), run_time=1.2)
        self.wait(2.6)
        self.play(cilindro.a_fraccion(COMPRESIONES[1]), run_time=1.2)
        self.wait(3.0)

        rot.mostrar(pie_curso("Las mismas moléculas, más juntas: golpean la "
                              "pared más veces por segundo."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: la R que no es universal ----------------------------
        # El numero sale del cociente, no de la memoria: si alguien cambia la
        # masa molar del style_block, el rotulo cambia con ella.
        rot.mostrar(pie_curso("Y esa R no es la constante universal: es la "
                              "del aire, y solo la del aire."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(formula_pie(rf"R = \frac{{\mathcal{{R}}}}{{\mathcal{{M}}}}"
                                rf" = \frac{{{R_UNIVERSAL:.0f}}}"
                                rf"{{{M_AIRE:.2f}}} = "
                                rf"{R_DEDUCIDA:.0f}\ \mathrm{{J/(kg\,K)}}"),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

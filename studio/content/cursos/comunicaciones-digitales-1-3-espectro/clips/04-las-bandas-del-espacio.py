class Clip4(Scene):
    """1.3.4 - `banda_espacio`: S (2.3 GHz), X (8.4 GHz), Ka (32 GHz) de
    la DSN sobre la regla logaritmica. Cierre de leccion. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Las bandas del espacio")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la regla logaritmica ---------------------------------
        rot.mostrar(pie_curso("El espectro es una regla logarítmica: "
                              "cada escalón, diez veces más alto."),
                    zona="abajo", run_time=0.5)
        be = banda_espacio(exp0=0, exp1=3, ancho=6.4)
        be.move_to(DOWN * 0.4)
        self.play(FadeIn(be), run_time=1.0)
        self.wait(4.2)

        # --- momento: banda S ------------------------------------------------
        rot.mostrar(pie_curso("La banda S: la más vieja del espacio "
                              "profundo, cerca del FM."),
                    zona="abajo", run_time=0.5)
        marca_s = be.marca(F_S_GHZ, "S", color=C_BANDA)
        self.play(FadeIn(marca_s, scale=0.7), run_time=0.8)
        self.wait(3.6)

        # --- momento: banda X ------------------------------------------------
        rot.mostrar(pie_curso("La banda X: el caballo de batalla del "
                              "espacio profundo."),
                    zona="abajo", run_time=0.5)
        marca_x = be.marca(F_X_GHZ, "X", color=C_BANDA)
        self.play(FadeIn(marca_x, scale=0.7), run_time=0.8)
        self.wait(3.6)

        # --- momento: banda Ka -------------------------------------------------
        rot.mostrar(pie_curso("La banda Ka: más ancho de banda, pero "
                              "más arriba también llueve peor."),
                    zona="abajo", run_time=0.5)
        marca_ka = be.marca(F_KA_GHZ, "Ka", color=C_BANDA)
        self.play(FadeIn(marca_ka, scale=0.7), run_time=0.8)
        self.wait(5.0)

        # --- cierre de leccion --------------------------------------------------
        cierre_leccion(
            self, rot,
            "El espectro es la tierra firme de las comunicaciones.",
            "Y está toda repartida.",
            "Siguiente leccion: la fase que habla.",
            be, marca_s, marca_x, marca_ka)

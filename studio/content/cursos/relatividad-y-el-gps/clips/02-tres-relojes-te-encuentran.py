class Clip2(Scene):
    """2 - Tres relojes te encuentran. Trilateracion en el plano: tres
    circulos que se cortan en tu punto, hasta que el sesgo del reloj los
    infla a todos y abre el triangulo de error. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Tres relojes te encuentran")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # Escala 0.62 para que los circulos inflados por el sesgo quepan en
        # la banda central; corrida a la izquierda para dejar la columna
        # derecha libre para la cifra.
        tri = trilateracion(escala=0.62).shift(LEFT * 1.75 + DOWN * 0.18)

        # --- momento: un satelite, una distancia ---------------------------
        rot.mostrar(pie_curso("Un satélite te da una distancia. Solo eso: "
                              "una distancia."), zona="abajo", run_time=0.5)
        tu = tag_junto(tri.receptor, "tú", DOWN, buff=0.18, font_size=21,
                       color=C_TIERRA)
        self.play(FadeIn(tri.receptor, scale=2.4), FadeIn(tu), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(s, scale=2.4) for s in tri.satelites],
                              lag_ratio=0.32), run_time=1.0)
        self.wait(3.5)

        # --- momento: cada distancia es un circulo -------------------------
        rot.mostrar(pie_curso("Cada distancia te encierra en un círculo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(tu), run_time=0.3)
        self.play(LaggedStart(*[Create(c) for c in tri.circulos],
                              lag_ratio=0.45), run_time=2.4)
        self.wait(2.8)

        # --- momento: los tres se cortan en un punto -----------------------
        rot.mostrar(pie_curso("Tres círculos se cortan en un solo punto: "
                              "ahí estás."), zona="abajo", run_time=0.5)
        self.play(Indicate(tri.receptor, scale_factor=2.6, color=C_LUZ),
                  run_time=0.9)
        self.wait(4.2)

        # --- momento: el reloj barato infla los tres radios ----------------
        # Regla dura: el pie NUEVO entra antes del Transform que describe.
        rot.mostrar(pie_curso("Pero el reloj de tu teléfono se equivoca y "
                              "los tres radios crecen a la vez."),
                    zona="abajo", run_time=0.5)
        con = tri.con_sesgo(0.35)          # anclado al receptor: misma pos.
        self.play(Transform(tri, con), run_time=1.8)
        self.wait(3.4)

        # --- momento: el triangulo de error y su precio --------------------
        rot.mostrar(pie_curso("En el plano para verlo: en 3D son esferas y "
                              "un cuarto satélite paga el sesgo."),
                    zona="abajo", run_time=0.5)
        # Tras el Transform los atributos de `tri` son viejos: la geometria
        # buena vive en `con`, que es la que se ve en pantalla.
        error = con.triangulo_error()
        self.play(FadeIn(error, scale=0.35), run_time=0.8)
        cifra = tag_hud(f"1 µs = {M_POR_US:.0f} m", font_size=25,
                        color=C_ERROR)
        cifra.move_to(RIGHT * 3.85 + DOWN * 0.20)
        self.play(FadeIn(cifra, shift=0.18 * LEFT), run_time=0.6)
        self.wait(4.8)

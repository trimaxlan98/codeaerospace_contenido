class Clip3(Scene):
    """2.1.3 - Irreversibilidad: por que solo existen choques de compresion.

    La primera ley no distingue: un choque de expansion la cumple igual de
    bien. Es la segunda la que lo prohibe, y se ve de un vistazo en el plano
    T-s de la leccion 1.2 — el estado de despues tendria que estar a la
    izquierda, y a la izquierda no se va. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Por qué no hay choques de expansión")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        ts = diagrama_ts(ancho=5.6, alto=3.0)
        ts.move_to(DOWN * 0.20)
        self.play(FadeIn(ts.ejes), run_time=0.6)

        uno = ts.estado(0.24, 0.30, "1", color=C_TENUE, direccion=DOWN)
        self.play(FadeIn(uno, scale=1.5), run_time=0.5)
        rot.mostrar(pie_curso("Antes del choque, aquí. Supersónico, frío y "
                              "a poca presión."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: el choque real ---------------------------------------
        rot.mostrar(pie_curso("Un choque de compresión sube la temperatura y "
                              "la entropía. Va arriba y a la derecha."),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)
        # Los dos procesos unen LOS MISMOS dos estados, uno en cada sentido:
        # dibujados sobre la misma recta se tapan y no se distingue cual es
        # cual. Se separan perpendicularmente y cada uno lleva su punta.
        a, b = ts.punto_de(0.24, 0.30), ts.punto_de(0.62, 0.78)
        direccion = (b - a) / np.linalg.norm(b - a)
        perp = np.array([-direccion[1], direccion[0], 0.0]) * 0.24

        real = Arrow(a + perp, b + perp, buff=0.10, stroke_width=3.4,
                     color=C_SUPER, max_tip_length_to_length_ratio=0.10)
        dos = ts.estado(0.62, 0.78, "2", color=C_SUPER, direccion=UP)
        self.play(Create(real), run_time=0.9)
        self.play(FadeIn(dos, scale=1.4), run_time=0.5)
        self.wait(3.6)

        # --- momento: el que no existe --------------------------------------
        rot.mostrar(pie_curso("Ahora al revés: un choque que expandiera el "
                              "aire de golpe."), zona="abajo", run_time=0.5)
        self.wait(1.2)
        prohibido = DashedVMobject(
            Arrow(b - perp, a - perp, buff=0.10, stroke_width=3.4,
                  color=C_SUB, max_tip_length_to_length_ratio=0.10),
            num_dashes=22)
        # La cruz se dibuja sobre el trayecto prohibido, en su punto medio:
        # el sitio donde el espectador esta mirando cuando cae la frase.
        centro = (a + b) / 2 - perp
        cruz = VGroup(
            Line(centro + np.array([-0.22, -0.22, 0]),
                 centro + np.array([0.22, 0.22, 0]), stroke_width=4.0,
                 color=C_SUPER),
            Line(centro + np.array([-0.22, 0.22, 0]),
                 centro + np.array([0.22, -0.22, 0]), stroke_width=4.0,
                 color=C_SUPER))
        self.play(Create(prohibido), run_time=0.9)
        self.play(Create(cruz), run_time=0.6)
        rot.mostrar(pie_curso("Cumple la conservación de masa, de cantidad "
                              "de movimiento y de energía."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(formula_pie(r"\Delta s < 0", color=C_SUPER),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(pie_curso("Pero tendría que ir a la izquierda. Y a la "
                              "izquierda no se va."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Por eso todos los choques comprimen. Ninguno "
                              "expande."), zona="abajo", run_time=0.5)
        self.wait(5.0)

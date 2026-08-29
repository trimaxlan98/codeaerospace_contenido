class Clip1(Scene):
    """3.2.1 - El catalogo de perturbaciones, presidido por el gigante:
    el viento. Contra el par de acelerar la inercia son 425 veces, y los
    DOS pares estan en el eje de carga. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Catalogo de perturbaciones"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- la montura que recibe el golpe ------------------------------
        # `montura` es ASIMETRICA: se ancla por su pivote, no con move_to.
        mont = montura(alto=2.0)
        mont.shift(LEFT * 5.15 + DOWN * 0.85 - mont.pivote)
        self.play(FadeIn(mont), run_time=0.9)

        t_plato = tag_hud(f"plato {fmt(DIAMETRO_PLATO_M, 0)} m",
                          font_size=19)
        t_plato.next_to(mont, DOWN, buff=0.20)
        self.play(FadeIn(t_plato), run_time=0.5)
        self.wait(0.5)

        # --- la rafaga ---------------------------------------------------
        # En diagonal y APUNTANDO al plato: horizontales y pegadas al
        # borde parecian tres rayas sueltas, no una rafaga sobre la antena.
        rafagas = VGroup(*[
            Arrow(LEFT * 6.55 + UP * y, LEFT * 5.60 + UP * (y - 0.52),
                  buff=0.0, color=C_PELIGRO, stroke_width=4,
                  max_tip_length_to_length_ratio=0.26)
            for y in (1.05, 0.70, 0.35)])
        t_raf = tag_hud(f"rafaga {fmt(V_RAFAGA, 0)} m/s", font_size=19,
                        color=C_PELIGRO)
        t_raf.move_to(LEFT * 5.55 + UP * 1.55)
        self.play(LaggedStart(*[GrowArrow(a) for a in rafagas],
                              lag_ratio=0.22), FadeIn(t_raf), run_time=1.1)
        self.wait(0.8)

        rot.mostrar(cifra_pie(f"plato {fmt(DIAMETRO_PLATO_M, 0)} m "
                              f"{fmt(AREA_PLATO, 2)} m2"), zona="abajo")
        self.wait(1.8)

        # --- viento contra inercia, EN ESCALA LOG ------------------------
        # La razon pasa de 20 (son 425): en lineal la barra de inercia
        # seria un pixel. La pieza se rotula sola "escala log", porque una
        # comparacion logaritmica presentada como lineal miente.
        barras = barras_comparar(
            [PAR_VIENTO, PAR_INERCIA], ["viento", "inercia"],
            ancho=3.4, alto=1.9, colores=[C_PELIGRO, C_CALCULO],
            log=True, unidad="N m")
        barras.move_to(LEFT * 1.55 + DOWN * 0.55)
        self.play(Create(barras.ejes), run_time=0.7)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN)
                                for b in barras.barras], lag_ratio=0.30),
                  FadeIn(barras.rotulos), run_time=1.5)
        self.play(FadeIn(barras.tag_log), run_time=0.5)
        self.wait(1.0)

        panel = panel_cifras((f"viento  {fmt(PAR_VIENTO, 1)} N m",
                              C_PELIGRO),
                             f"inercia {fmt(PAR_INERCIA, 3)} N m",
                             f"razon   {fmt(RAZON_VIENTO, 0)}x")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.0)

        # --- las DOS condiciones de esa razon ----------------------------
        rot.mostrar(cifra_pie(f"razon {fmt(RAZON_VIENTO, 0)}x en carga"),
                    zona="abajo")
        t_eje = tag_hud("eje de carga", font_size=19, color=C_TENUE)
        t_eje.next_to(barras.rotulos, DOWN, buff=0.22)
        self.play(FadeIn(t_eje), run_time=0.5)
        self.wait(2.2)

        # J = 2 kg m2 es la inercia de ESCALA DIDACTICA del curso fuente,
        # no la de un plato de 3 m real: va en gris, porque no se mide aqui.
        rot.mostrar(dato_pie(f"J {fmt(J_EJE, 0)} kg m2 didactico"),
                    zona="abajo")
        self.wait(2.4)

        # --- el resto del catalogo ---------------------------------------
        self.play(FadeOut(panel), run_time=0.5)

        filas = VGroup()
        catalogo = (("viento", TERMINOS["viento"], 3, C_PELIGRO),
                    ("latencia", TERMINOS["latencia"], 3, C_CALCULO),
                    ("sesgo", TERMINOS["sesgo"], 3, C_CALCULO),
                    ("ruido", TERMINOS["ruido"], 3, C_CALCULO),
                    ("cuantiz", RES_ENCODER, 4, C_OK))
        for nombre, valor, dec, color in catalogo:
            filas.add(tag_hud(f"{nombre:9s}{fmt(valor, dec):>7s} deg",
                              font_size=21, color=color))
        filas.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        filas.move_to(RIGHT * 3.60 + DOWN * 0.35)
        self.play(LaggedStart(*[FadeIn(f, shift=0.18 * RIGHT)
                                for f in filas], lag_ratio=0.30),
                  run_time=2.0)
        self.wait(1.6)

        marco = SurroundingRectangle(filas[0], color=C_PELIGRO,
                                     stroke_width=2.2, buff=0.14)
        self.play(Create(marco), run_time=0.6)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"encoder 16 bits "
                              f"{fmt(RES_ENCODER, 4)} deg"), zona="abajo")
        self.play(Transform(marco,
                            SurroundingRectangle(filas[4], color=C_OK,
                                                 stroke_width=2.2,
                                                 buff=0.14)),
                  run_time=0.9)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"razon {fmt(RAZON_VIENTO, 0)}x en carga"),
                    zona="abajo")
        self.wait(3.2)

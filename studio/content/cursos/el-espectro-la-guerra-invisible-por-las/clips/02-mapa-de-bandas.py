class Clip2(Scene):
    """2 - El mapa: de UHF a Q/V. La barra sube arriba; C y Ka pulsan en
    relevo mientras el pie explica la compra de ancho de banda. Abajo
    aparecen dos parabolas (Arc abiertas a la derecha, grande y chica)
    con sus tags de diametro, y la formula de ganancia releva al pie en
    su misma zona. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: arranque del modulo ---------------------------------
        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("El mapa: de UHF a Q/V")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: ocho barrios en una barra -----------------------------
        barra = barra_bandas(ancho=6.8, alto=0.8, font_size=15)
        barra.move_to(UP * 1.3)

        self.play(FadeIn(barra, shift=0.15 * UP), run_time=1.0)
        self.wait(0.4)

        rot.mostrar(pie_curso("Ocho barrios con nombres heredados de la "
                              "guerra: L, S, C, X, Ku, Ka..."),
                   zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: subir de banda compra ancho de banda -------------------
        rot.mostrar(pie_curso("Subir en frecuencia compra ancho de banda: "
                              "C ofrece 1.7 GHz..."), zona="abajo",
                   run_time=0.5)
        self.wait(0.6)
        self.play(Indicate(barra.segmento("C"), color=C_ONDA,
                           scale_factor=1.15), run_time=1.0)
        self.wait(3.0)

        rot.mostrar(pie_curso("...Ka ofrece 5. Tres veces más capacidad."),
                   zona="abajo", run_time=0.5)
        self.wait(0.6)
        self.play(Indicate(barra.segmento("Ka"), color=C_ONDA,
                           scale_factor=1.15), run_time=1.0)
        self.wait(3.0)

        # --- momento: la antena se encoge --------------------------------
        rot.mostrar(pie_curso("Y la antena se encoge: la misma ganancia "
                              "con la mitad de plato."), zona="abajo",
                   run_time=0.5)
        self.wait(0.6)

        parabola_grande = Arc(radius=0.85, start_angle=PI - 0.4 * PI,
                              angle=0.8 * PI, color=C_GSO, stroke_width=4.2)
        parabola_grande.move_to(np.array([-2.2, -1.2, 0.0]))
        tag_grande = tag_junto(parabola_grande, "60 cm · Ku", direccion=DOWN)

        parabola_chica = Arc(radius=0.5, start_angle=PI - 0.4 * PI,
                             angle=0.8 * PI, color=C_GSO, stroke_width=4.2)
        parabola_chica.move_to(np.array([2.2, -1.2, 0.0]))
        tag_chica = tag_junto(parabola_chica, "35 cm · Ka", direccion=DOWN)

        self.play(Create(parabola_grande), FadeIn(tag_grande, shift=0.1 * UP),
                  run_time=1.0)
        self.play(Create(parabola_chica), FadeIn(tag_chica, shift=0.1 * UP),
                  run_time=1.0)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"G \approx (\pi D / \lambda)^2"),
                   zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("¿El precio de subir? Lo cobra la "
                              "atmósfera."), zona="abajo", run_time=0.5)
        self.wait(5.2)

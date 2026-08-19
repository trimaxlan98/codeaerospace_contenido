class Clip1(Scene):
    """1.1.1 - Un vector es una flecha desde el origen Y una lista de dos
    numeros; los dos idiomas describen el mismo objeto. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Una flecha y una lista")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el plano y la flecha ----------------------------------
        pl = plano_leccion(vivo=False)
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Un vector es una flecha que sale del origen. "
                              "Siempre del origen."), zona="abajo",
                    run_time=0.5)
        v = vector(pl, V_DEMO, color=C_VEC, nombre=r"\vec v")
        self.play(GrowArrow(v.flecha), run_time=0.9)
        self.play(FadeIn(v.etiqueta), run_time=0.3)
        self.wait(4.2)

        # --- momento: leerla en la rejilla ----------------------------------
        rot.mostrar(pie_curso("Para describirla bastan dos números: cuánto "
                              "a la derecha, cuánto hacia arriba."),
                    zona="abajo", run_time=0.5)
        guia_x = DashedLine(pl.p(V_DEMO), pl.p(V_DEMO[0], 0), color=C_J,
                            stroke_width=2.0, dash_length=0.1)
        guia_y = DashedLine(pl.p(V_DEMO), pl.p(0, V_DEMO[1]), color=C_I,
                            stroke_width=2.0, dash_length=0.1)
        tramo_x = Line(pl.p(0, 0), pl.p(V_DEMO[0], 0), color=C_I,
                       stroke_width=6.0)
        tramo_y = Line(pl.p(0, 0), pl.p(0, V_DEMO[1]), color=C_J,
                       stroke_width=6.0)
        cifra_x = tag_hud(fmt(V_DEMO[0], 0), font_size=22, color=C_I)
        cifra_x.next_to(pl.p(V_DEMO[0] / 2, 0), DOWN, buff=0.18)
        cifra_y = tag_hud(fmt(V_DEMO[1], 0), font_size=22, color=C_J)
        cifra_y.next_to(pl.p(0, V_DEMO[1] / 2), LEFT, buff=0.18)
        self.play(Create(guia_x), Create(guia_y), run_time=0.7)
        self.play(Create(tramo_x), FadeIn(cifra_x), run_time=0.7)
        self.play(Create(tramo_y), FadeIn(cifra_y), run_time=0.7)
        self.wait(3.6)

        # --- momento: la lista --------------------------------------------
        rot.mostrar(pie_curso("Esa lista, escrita en columna, ES el "
                              "vector. No lo describe: lo es."),
                    zona="abajo", run_time=0.5)
        columna = vector_columna(V_DEMO, color=C_VEC, font_size=40)
        columna.matriz.get_rows()[0].set_color(C_I)
        columna.matriz.get_rows()[1].set_color(C_J)
        panel = panel_derecha(columna)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.4)

        rot.mostrar(pie_curso("Mismo objeto, dos idiomas: la geometría lo "
                              "dibuja, el álgebra lo escribe."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(v.flecha, color=C_VEC, scale_factor=1.05),
                  run_time=0.8)
        self.play(Indicate(columna, color=C_VEC, scale_factor=1.08),
                  run_time=0.8)
        self.wait(3.6)

        rot.mostrar(pie_curso("Con dos idiomas se piensa mejor: en este "
                              "curso cada idea se verá y se calculará."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

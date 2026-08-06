class Clip6(Scene):
    """6 - Demodular en una linea. AM arriba (portadora ambar, envolvente
    cian) y FM abajo (violeta): el modulo recupera el mensaje de la AM, la
    diferencia de fase el de la FM; el ruido quiebra la AM pero el
    limitador deja la FM intacta."""

    def construct(self):
        rot = Rotulos(self)

        def quiebre(punto, ancho=0.16, alto=0.09, color=C_RUIDO):
            """Zigzag corto y rojo apoyado en un punto de una curva."""
            p = np.asarray(punto, dtype=np.float64)
            esquinas = [
                p + np.array([-ancho / 2.0, 0.0, 0.0]),
                p + np.array([-ancho / 6.0, alto, 0.0]),
                p + np.array([ancho / 6.0, -alto, 0.0]),
                p + np.array([ancho / 2.0, 0.0, 0.0]),
            ]
            g = VGroup()
            for a, b in zip(esquinas[:-1], esquinas[1:]):
                g.add(Line(a, b, color=color, stroke_width=3))
            return g

        # --- momento: HUD y titulo -----------------------------------------
        modulo = hud_modulo("Modulo 06")
        titulo = titulo_curso("Demodular en una línea")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.35)
        rot.mostrar(titulo, zona="arriba", run_time=0.35)

        # --- momento: la AM arriba, la portadora primero --------------------
        am = onda_am(ancho=5.6, alto=1.0, ciclos_portadora=26.0,
                    ciclos_mensaje=2.0, indice=0.55)
        am.move_to(UP * 1.2)
        self.play(Create(am.portadora), run_time=0.7)
        rot.mostrar(pie_curso("AM: el mensaje viaja en la amplitud."),
                   zona="abajo", run_time=0.35)
        self.wait(5.2)

        # --- momento: la envolvente se dibuja y pulsa ------------------------
        self.play(Create(am.envolvente), run_time=0.6)
        self.play(Indicate(am.envolvente, color=C_I, scale_factor=1.04),
                  run_time=0.6)
        rot.mostrar(pie_curso("Recuperarlo es tomar el módulo de cada "
                              "muestra."), zona="abajo", run_time=0.35)
        self.wait(5.2)
        rot.mostrar(formula_pie("|z| = \\sqrt{I^2 + Q^2}"), zona="abajo",
                   run_time=0.35)
        self.wait(1.8)

        # --- momento: la FM abajo -------------------------------------------
        fm = onda_fm(ancho=5.6, alto=1.0, ciclos_base=18.0, desviacion=0.65,
                    ciclos_mensaje=1.5)
        fm.move_to(DOWN * 1.3)
        self.play(Create(fm.onda), run_time=0.7)
        rot.mostrar(pie_curso("FM: el mensaje viaja en la frecuencia..."),
                   zona="abajo", run_time=0.35)
        self.wait(5.2)
        rot.mostrar(formula_pie("\\varphi[n] - \\varphi[n-1]"), zona="abajo",
                   run_time=0.35)
        self.wait(1.8)
        rot.mostrar(pie_curso("...y se recupera restando la fase de "
                              "muestras vecinas."), zona="abajo",
                   run_time=0.35)
        self.wait(5.3)

        # --- momento: el ruido quiebra la AM ---------------------------------
        quiebres = VGroup(*[
            quiebre(am.envolvente.point_from_proportion(t))
            for t in (0.22, 0.5, 0.78)
        ])
        self.play(FadeIn(quiebres), run_time=0.4)
        rot.mostrar(pie_curso("El ruido golpea la amplitud: la AM lo "
                              "sufre..."), zona="abajo", run_time=0.35)
        self.wait(5.2)

        # --- momento: el limitador salva la FM --------------------------------
        cx, cy = fm.get_center()[0], fm.get_center()[1]
        medio = 2.9
        lim_arriba = DashedLine(np.array([cx - medio, cy + 0.7, 0.0]),
                                np.array([cx + medio, cy + 0.7, 0.0]),
                                color=C_OK, stroke_width=3)
        lim_abajo = DashedLine(np.array([cx - medio, cy - 0.7, 0.0]),
                               np.array([cx + medio, cy - 0.7, 0.0]),
                               color=C_OK, stroke_width=3)
        limitador = VGroup(lim_arriba, lim_abajo)
        self.play(FadeIn(limitador), run_time=0.4)
        fm_visual = VGroup(fm, limitador)
        tag = tag_junto(fm_visual, "mensaje a salvo", direccion=RIGHT,
                        buff=0.25, color=C_OK)
        self.play(FadeIn(tag, shift=0.12 * LEFT), run_time=0.4)
        rot.mostrar(pie_curso("...la FM lo recorta con un limitador y "
                              "sigue limpia."), zona="abajo", run_time=0.35)
        self.wait(5.5)

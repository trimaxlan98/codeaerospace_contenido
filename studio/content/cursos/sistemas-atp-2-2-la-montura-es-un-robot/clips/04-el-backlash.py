class Clip4(Scene):
    """2.2.4 - Al invertir el giro, la salida se queda quieta 0.3 grados:
    tres veces el presupuesto de 0.1. La banda del presupuesto se dibuja
    al lado para que se vea la razon. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("El backlash"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el ciclo de histeresis, entrada contra salida en el tiempo ---
        t, entrada, salida = BL["t"], BL["entrada"], BL["salida"]
        ejes = Axes(x_range=[0.0, float(t[-1]), float(t[-1]) / 4.0],
                   y_range=[-1.5, 1.5, 0.5], x_length=5.6, y_length=3.1,
                   axis_config={"color": C_EJE, "stroke_width": 2.2,
                               "include_ticks": False,
                               "include_tip": False})
        ejes.move_to(LEFT * 2.75 + DOWN * 0.35)
        self.play(Create(ejes), run_time=1.1)
        self.wait(0.3)

        curva_e = VMobject(color=C_CIELO, stroke_width=3.2)
        curva_e.set_points_as_corners([ejes.c2p(a, b)
                                       for a, b in zip(t, entrada)])
        curva_s = VMobject(color=C_CALCULO, stroke_width=3.6)
        curva_s.set_points_as_corners([ejes.c2p(a, b)
                                       for a, b in zip(t, salida)])
        t_ent = tag_hud("comandado", font_size=17, color=C_CIELO)
        t_ent.next_to(ejes, UP, buff=0.12).align_to(ejes, LEFT)
        t_sal = tag_hud("real", font_size=17, color=C_CALCULO)
        t_sal.next_to(t_ent, RIGHT, buff=0.35)
        self.play(Create(curva_e), FadeIn(t_ent), run_time=2.0)
        self.play(Create(curva_s), FadeIn(t_sal), run_time=2.0)
        self.wait(1.0)

        # --- se marca UNA meseta real: la salida no se mueve ahi -----------
        quieta = np.where(np.isclose(np.diff(salida), 0.0))[0]
        # los tramos quietos son varios (una meseta por inversion): se
        # agrupan en corridas contiguas y se toma la SEGUNDA, ya lejos
        # del enganche inicial (la primera es el arranque, no una
        # inversion real).
        grupos = np.split(quieta, np.where(np.diff(quieta) > 1)[0] + 1)
        grupos = [g for g in grupos if len(g) > 0]
        tramo = grupos[1] if len(grupos) > 1 else grupos[0]
        i0, i1 = int(tramo[0]), int(tramo[-1]) + 1
        p0, p1 = ejes.c2p(t[i0], salida[i0]), ejes.c2p(t[i1], salida[i1])
        caja = SurroundingRectangle(VMobject().set_points_as_corners(
            [p0 + UP * 0.10 + LEFT * 0.05,
             p1 + DOWN * 0.10 + RIGHT * 0.05]),
            color=C_PELIGRO, stroke_width=2.4, buff=0.0)
        t_quieta = tag_hud("quieta", font_size=16, color=C_PELIGRO)
        t_quieta.next_to(caja, DOWN, buff=0.10)
        self.play(Create(caja), FadeIn(t_quieta), run_time=1.0)
        self.wait(2.0)

        # --- las dos bandas, a la MISMA escala, una al lado de la otra ------
        escala = float(np.linalg.norm(ejes.c2p(0.0, 1.0) - ejes.c2p(0.0, 0.0)))
        base = RIGHT * 3.55 + DOWN * 1.55

        barra_hueco = Line(base, base + UP * escala * BACKLASH_DEG,
                           color=C_PELIGRO, stroke_width=8)
        t_hueco = tag_hud(f"holgura {fmt(BACKLASH_DEG, 1)} deg",
                          font_size=18, color=C_PELIGRO)
        t_hueco.next_to(barra_hueco, UP, buff=0.14)

        base2 = base + RIGHT * 0.85
        barra_pres = Line(base2, base2 + UP * escala * OBJETIVO_DEG,
                          color=C_CALCULO, stroke_width=8)
        t_pres = tag_hud(f"presupuesto {fmt(OBJETIVO_DEG, 1)} deg",
                         font_size=18, color=C_CALCULO)
        t_pres.next_to(barra_pres, UP, buff=0.14)

        self.play(GrowFromEdge(barra_hueco, DOWN), FadeIn(t_hueco),
                  run_time=1.2)
        self.wait(0.5)
        self.play(GrowFromEdge(barra_pres, DOWN), FadeIn(t_pres),
                  run_time=1.2)
        self.wait(1.2)

        rot.mostrar(cifra_pie(f"{fmt(VECES_PRESUPUESTO, 0)} veces el "
                              f"presupuesto"), zona="abajo")
        self.wait(3.4)

        # --- cierre literal de la leccion -----------------------------------
        cierre_leccion(
            self, rot,
            "La holgura se come el presupuesto",
            "antes de que el control opine.",
            ejes, curva_e, curva_s, t_ent, t_sal, caja, t_quieta,
            barra_hueco, t_hueco, barra_pres, t_pres, espera=8.5)

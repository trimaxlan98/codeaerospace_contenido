class Clip3(Scene):
    """1.1.3 - Multiplexacion estadistica: caben mas de los que caben,
    porque casi nunca hablan todos a la vez. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Compartir sin reservar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: diez flujos a rafagas -------------------------------
        rot.mostrar(pie_curso("Diez flujos a rafagas quieren el mismo "
                              "enlace. Cada uno pide 2 Mb/s cuando habla."),
                    zona="abajo", run_time=0.5)
        flujos = VGroup(*[
            Rectangle(width=0.42, height=0.42, stroke_color=C_RED,
                      stroke_width=1.8, fill_color=C_RED, fill_opacity=0.10)
            for _ in range(MUX["n_flujos"])]).arrange(RIGHT, buff=0.18)
        flujos.move_to(UP * 1.85)
        et_flujos = tag_hud("10 flujos", font_size=18, color=C_EJE)
        et_flujos.next_to(flujos, LEFT, buff=0.32)
        tubo = Rectangle(width=5.2, height=0.34, stroke_color=C_COLA,
                         stroke_width=2.2)
        tubo.move_to(UP * 0.95)
        et_tubo = tag_hud("enlace: %s Mb/s" % fmt(MUX["capacidad_mbps"], 0),
                          font_size=18, color=C_COLA)
        et_tubo.next_to(tubo, RIGHT, buff=0.28)
        self.play(FadeIn(flujos), FadeIn(et_flujos), run_time=0.7)
        self.play(FadeIn(tubo), FadeIn(et_tubo), run_time=0.5)
        activos = [int(x) for x in MUX["activos"][:4]]
        for k in activos[:3]:
            enc = VGroup(*[flujos[i].copy().set_fill(C_PAQUETE, opacity=0.55)
                           .set_stroke(C_PAQUETE, width=2.2)
                           for i in range(k)])
            self.play(FadeIn(enc), run_time=0.35)
            self.play(FadeOut(enc), run_time=0.35)
        self.wait(2.9)

        # --- momento: la demanda medida -----------------------------------
        rot.mostrar(pie_curso("Casi nunca hablan todos a la vez: la "
                              "demanda media es mucho menor que la suma."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(flujos), FadeOut(et_flujos), FadeOut(tubo),
                  FadeOut(et_tubo), run_time=0.5)
        g = grafica(DEMANDA, (0, MUX_VENTANA - 1), (0, 11.0), ancho=7.4,
                    alto=2.9, color=C_PAQUETE, muestras=MUX_VENTANA)
        g.move_to(UP * 0.55)
        et_y = tag_hud("Mb/s pedidos", font_size=15, color=C_EJE)
        et_y.next_to(g, UP, buff=0.14).shift(LEFT * 2.5)
        cap = g.horizontal_en(MUX["capacidad_mbps"], color=C_COLA)
        et_cap = tag_hud("capacidad %s Mb/s" % fmt(MUX["capacidad_mbps"], 0),
                         font_size=17, color=C_COLA)
        et_cap.next_to(cap, RIGHT, buff=0.12).shift(UP * 0.16)
        self.play(FadeIn(g.ejes), FadeIn(et_y), run_time=0.5)
        self.play(Create(g.curva), run_time=2.0)
        self.play(Create(cap), FadeIn(et_cap), run_time=0.6)
        et_media = tag_hud("demanda media medida: %s Mb/s"
                           % fmt(MUX_MEDIA_V, 2), font_size=20)
        et_media.next_to(g, DOWN, buff=0.30)
        self.play(FadeIn(et_media), run_time=0.5)
        self.wait(2.6)

        # --- momento: reservar el pico desperdicia ------------------------
        rot.mostrar(pie_curso("Si reservaramos el pico de cada uno, en "
                              "este enlace solo cabrian tres."),
                    zona="abajo", run_time=0.5)
        reserva = tag_hud("reservando 2 Mb/s por flujo  ->  caben %d"
                          % MUX["flujos_con_reserva"], font_size=20,
                          color=C_PERDIDA)
        compartir = tag_hud("compartiendo el enlace     ->  caben %d  "
                            "(%sx)" % (MUX["n_flujos"],
                                       fmt(MUX["ganancia"], 1)),
                            font_size=20, color=C_OK)
        panel = VGroup(reserva, compartir).arrange(DOWN, buff=0.22,
                                                   aligned_edge=LEFT)
        panel.next_to(g, DOWN, buff=0.26)
        self.play(FadeOut(et_media), run_time=0.3)
        self.play(FadeIn(reserva, shift=0.12 * UP), run_time=0.5)
        self.play(FadeIn(compartir, shift=0.12 * UP), run_time=0.5)
        self.wait(4.4)

        # --- momento: el precio -------------------------------------------
        rot.mostrar(pie_curso("El precio: a veces coinciden, y entonces "
                              "no caben."),
                    zona="abajo", run_time=0.5)
        picos = VGroup(*[
            Dot(g.punto_de(k), radius=0.065, color=C_PERDIDA)
            for k in range(MUX_VENTANA)
            if DEMANDA(k) > MUX["capacidad_mbps"]])
        self.play(FadeOut(panel), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(p, scale=1.6) for p in picos],
                              lag_ratio=0.12), run_time=1.2)
        et_exceso = tag_hud("por encima de la capacidad en %d de los %d "
                            "instantes  (%s %%)"
                            % (len(picos), MUX_VENTANA,
                               fmt(MUX_EXCESO_V, 1)), font_size=20,
                            color=C_PERDIDA)
        et_exceso.next_to(g, DOWN, buff=0.30)
        self.play(FadeIn(et_exceso), run_time=0.5)
        self.wait(5.0)

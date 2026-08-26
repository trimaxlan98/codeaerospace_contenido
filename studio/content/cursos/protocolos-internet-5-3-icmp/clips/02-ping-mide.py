class Clip2(Scene):
    """5.3.2 - Ping mide: eco (tipo 8) y respuesta (tipo 0); el RTT
    minimo se descompone en propagacion (tope duro: 2c/3 en fibra) y todo
    lo demas; el mismo ping, con el enlace cargado al 85%, sube su media
    en la cola medida, contable en las mismas 8 rondas. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Ping mide")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: eco y respuesta ---------------------------------------
        rot.mostrar(pie_curso("Ping manda un eco (ICMP tipo 8) y cronometra "
                              "hasta que vuelve la respuesta (tipo 0)."),
                    zona="abajo", run_time=0.5)
        no = nodo("host", "origen", tam=0.5, fs=15)
        no.move_to(LEFT * 4.6 + UP * 1.35)
        nd = nodo("servidor", "destino", tam=0.5, fs=15)
        nd.move_to(RIGHT * 4.6 + UP * 1.35)
        cable = enlace(no.centro(), nd.centro(), color=C_RED, grosor=2.2)
        et_dist = tag_hud("9000 km declarados (cable real, escala no "
                          "literal)", font_size=15, color=C_EJE)
        et_dist.next_to(cable.linea, DOWN, buff=0.55)
        self.play(FadeIn(no), FadeIn(nd), Create(cable.linea),
                  FadeIn(et_dist), run_time=1.0)
        eco = ficha("8", lado=0.36, color=C_PAQUETE)
        eco.move_to(no.centro() + RIGHT * 0.42)
        self.add(eco)
        self.play(eco.animate.move_to(nd.centro() + LEFT * 0.42),
                  run_time=1.0)
        resp = ficha("0", lado=0.36, color=C_OK)
        resp.move_to(nd.centro() + LEFT * 0.42)
        self.add(resp)
        self.remove(eco)
        self.play(resp.animate.move_to(no.centro() + RIGHT * 0.42),
                  run_time=1.0)
        rel = reloj(RTT_MIN, etiqueta="RTT", dec=1, fs=24)
        rel.move_to(DOWN * 0.55)
        self.play(FadeIn(rel), run_time=0.5)
        self.wait(4.0)

        # --- momento: el RTT se descompone -----------------------------------
        self.play(FadeOut(no), FadeOut(nd), FadeOut(cable.linea),
                  FadeOut(et_dist), FadeOut(resp), FadeOut(rel), run_time=0.5)
        rot.mostrar(pie_curso("Ese minimo, %s ms, se descompone: la "
                              "propagacion es el tope que impone la "
                              "velocidad de la luz en la fibra."
                              % fmt(RTT_MIN, 1)),
                    zona="abajo", run_time=0.5)
        ancho_b = 8.6
        px = ancho_b / RTT_MIN
        w_prop, w_resto = px * PROP_MS, px * RESTO_MS
        x0 = -ancho_b / 2.0
        b_prop = Rectangle(width=w_prop, height=0.62, stroke_color=C_RED,
                           fill_color=C_RED, fill_opacity=0.55,
                           stroke_width=2.0)
        b_prop.move_to(np.array([x0 + w_prop / 2.0, 0.0, 0.0]))
        b_resto = Rectangle(width=w_resto, height=0.62, stroke_color=C_EJE,
                            fill_color=C_EJE, fill_opacity=0.40,
                            stroke_width=2.0)
        b_resto.move_to(np.array([x0 + w_prop + w_resto / 2.0, 0.0, 0.0]))
        barra = VGroup(b_prop, b_resto)
        et_prop = tag_hud("propagacion: %s ms" % fmt(PROP_MS, 1),
                          font_size=18, color=C_CIFRA)
        et_prop.next_to(b_prop, UP, buff=0.16)
        et_resto = tag_hud("routers + variacion: %s ms" % fmt(RESTO_MS, 1),
                           font_size=15, color=C_EJE)
        et_resto.next_to(b_resto, DOWN, buff=0.16)
        self.play(GrowFromEdge(b_prop, LEFT), FadeIn(et_prop), run_time=0.9)
        self.play(GrowFromEdge(b_resto, LEFT), FadeIn(et_resto), run_time=0.7)
        self.wait(4.6)

        # --- momento: ocho pings reales, sin carga --------------------------
        self.play(FadeOut(barra), FadeOut(et_prop), FadeOut(et_resto),
                  run_time=0.5)
        rot.mostrar(pie_curso("Ocho pings reales al mismo destino, sin "
                              "carga: casi no varian."),
                    zona="abajo", run_time=0.5)

        def f_base(x):
            return float(MUESTRAS_BASE[int(round(min(max(x, 0), 7)))])

        def f_carga(x):
            return float(MUESTRAS_CARGA[int(round(min(max(x, 0), 7)))])

        gr_base = grafica(f_base, (0, 7), (85, 132), ancho=8.6, alto=2.6,
                          color=C_RED, muestras=8, etiqueta_x="ping numero",
                          etiqueta_y="RTT ms")
        gr_carga = grafica(f_carga, (0, 7), (85, 132), ancho=8.6, alto=2.6,
                           color=C_COLA, muestras=8)
        combo = VGroup(gr_base, gr_carga)
        combo.move_to(DOWN * 0.65)
        self.play(FadeIn(gr_base), run_time=1.0)
        self.wait(3.0)

        # --- momento: el mismo cable, cargado al 85% -------------------------
        rot.mostrar(pie_curso("El mismo cable, el mismo destino: con el "
                              "enlace al 85%% de carga, la media sube "
                              "%s ms, toda ella de cola." % fmt(DELTA_COLA,
                                                                1)),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(gr_carga.curva), run_time=0.8)
        flecha = Arrow(gr_base.punto_de(3), gr_carga.punto_de(3),
                      color=C_CIFRA, stroke_width=3.2, buff=0.06,
                      max_tip_length_to_length_ratio=0.14)
        et_delta = tag_hud("+%s ms de cola" % fmt(DELTA_COLA, 1),
                           font_size=19, color=C_CIFRA)
        et_delta.next_to(flecha, RIGHT, buff=0.18)
        self.play(Create(flecha), FadeIn(et_delta), run_time=0.8)
        self.wait(6.0)

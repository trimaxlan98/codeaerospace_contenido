class Clip1(Scene):
    """4.3.1 - Octubre de 1986: todos empujan, las colas se llenan, se
    descarta, se retransmite y se empuja mas. El trabajo util se desploma
    un 95 % MEDIDO al pasar de la capacidad. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El colapso")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la cola se llena ------------------------------------
        rot.mostrar(pie_curso("Octubre de 1986. Todos empujan a la vez y "
                              "la cola del router se llena."),
                    zona="abajo", run_time=0.5)
        q = cola(capacidad=COLA_CAP, ocupacion=0, lado=0.54,
                 etiqueta="bufer del router")
        q.move_to(UP * 0.60)
        emisores = nodo("host", "emisores", 0.50)
        emisores.next_to(q, LEFT, buff=0.90)
        salida = nodo("router", "salida", 0.50)
        salida.next_to(q, RIGHT, buff=0.90)
        self.play(FadeIn(emisores), FadeIn(q), FadeIn(salida), run_time=0.8)
        for n in OCUPACIONES[1:]:
            self.play(Transform(q, q.con_ocupacion(n)), run_time=0.22)
        et_desc = tag_hud("descartados: %d de %d  =  %s %% de lo que se envio"
                          % (COLA_COLAPSO["descartes"],
                             COLA_COLAPSO["llegadas"],
                             fmt(COLA_COLAPSO["pct_descarte"], 2)),
                          font_size=21, color=C_PERDIDA)
        et_desc.move_to(DOWN * 0.95)
        self.play(FadeIn(et_desc), run_time=0.5)
        self.wait(3.6)

        # --- momento: el bucle que se alimenta a si mismo -----------------
        rot.mostrar(pie_curso("Lo descartado se retransmite. Y retransmitir "
                              "es empujar todavia mas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_desc), FadeOut(emisores), FadeOut(salida),
                  FadeOut(q), run_time=0.5)
        cajas = VGroup()
        for texto in BUCLE:
            r = RoundedRectangle(corner_radius=0.12, width=3.5, height=0.78,
                                 stroke_color=C_PERDIDA, stroke_width=2.2,
                                 fill_color=C_PERDIDA, fill_opacity=0.08)
            t = Text(texto, font_size=21, color=C_TITULO)
            if t.width > 3.1:
                t.scale_to_fit_width(3.1)
            t.move_to(r.get_center())
            cajas.add(VGroup(r, t))
        cajas.arrange(RIGHT, buff=0.62).move_to(UP * 0.75)
        flechas = VGroup(*[
            Arrow(cajas[i].get_right(), cajas[i + 1].get_left(), buff=0.10,
                  color=C_PERDIDA, stroke_width=3.0,
                  max_tip_length_to_length_ratio=0.30)
            for i in range(2)])
        y_v = cajas.get_bottom()[1] - 0.72
        vuelta = VGroup(
            Line(cajas[2].get_bottom() + DOWN * 0.06,
                 np.array([cajas[2].get_center()[0], y_v, 0.0]),
                 color=C_PERDIDA, stroke_width=3.0),
            Line(np.array([cajas[2].get_center()[0], y_v, 0.0]),
                 np.array([cajas[0].get_center()[0], y_v, 0.0]),
                 color=C_PERDIDA, stroke_width=3.0),
            Arrow(np.array([cajas[0].get_center()[0], y_v, 0.0]),
                  cajas[0].get_bottom() + DOWN * 0.06, buff=0.0,
                  color=C_PERDIDA, stroke_width=3.0,
                  max_tip_length_to_length_ratio=0.30))
        self.play(LaggedStart(*[FadeIn(c) for c in cajas], lag_ratio=0.45),
                  run_time=1.1)
        self.play(Create(flechas), run_time=0.6)
        self.play(Create(vuelta), run_time=0.9)
        et_bucle = tag_hud("y vuelta a empezar", font_size=19,
                           color=C_PERDIDA)
        et_bucle.next_to(vuelta[1], DOWN, buff=0.16)
        self.play(FadeIn(et_bucle), run_time=0.4)
        self.wait(3.8)

        # --- momento: el trabajo util se desploma -------------------------
        rot.mostrar(pie_curso("Lo que se mide no es lo que se envia: es lo "
                              "que llega y sirve."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cajas), FadeOut(flechas), FadeOut(vuelta),
                  FadeOut(et_bucle), run_time=0.5)
        g = grafica(UTIL, (COL_X[0], COL_X[-1]), (0.0, 1.18), ancho=7.2,
                    alto=2.75, color=C_PAQUETE, muestras=COL_N)
        g.move_to(UP * 0.62)
        et_y = tag_hud("trabajo util", font_size=15, color=C_EJE)
        et_y.next_to(g, UP, buff=0.14).shift(LEFT * 2.6)
        et_x = tag_hud("carga ofrecida", font_size=15, color=C_EJE)
        et_x.next_to(g, DOWN, buff=0.16).shift(RIGHT * 2.4)
        cap = g.horizontal_en(COL_CAP, color=C_COLA)
        et_cap = tag_hud("capacidad", font_size=16, color=C_COLA)
        et_cap.next_to(cap, UP, buff=0.06).shift(LEFT * 2.5)
        self.play(FadeIn(g.ejes), FadeIn(et_y), FadeIn(et_x), run_time=0.5)
        self.play(Create(cap), FadeIn(et_cap), run_time=0.5)
        self.play(Create(g.curva), run_time=2.2)
        self.wait(2.2)

        # --- momento: la cifra de la caida --------------------------------
        rot.mostrar(pie_curso("Pasada la capacidad, empujar mas entrega "
                              "menos. Eso es el colapso."),
                    zona="abajo", run_time=0.5)
        caidos = VGroup(*[Dot(g.punto_de(x), radius=0.065, color=C_PERDIDA)
                          for x in COL_X if x > COL_CAP])
        self.play(LaggedStart(*[FadeIn(p, scale=1.6) for p in caidos],
                              lag_ratio=0.10), run_time=1.1)
        et_caida = tag_hud("trabajo util  %s  ->  %s  de la capacidad"
                           "   (%s %% menos)"
                           % (fmt(COLAPSO["util_max"], 2),
                              fmt(COLAPSO["util_final"], 2),
                              fmt(COL_CAIDA, 1)),
                           font_size=21, color=C_PERDIDA)
        et_caida.move_to(DOWN * 1.62)
        self.play(FadeIn(et_caida), run_time=0.5)
        self.wait(5.0)

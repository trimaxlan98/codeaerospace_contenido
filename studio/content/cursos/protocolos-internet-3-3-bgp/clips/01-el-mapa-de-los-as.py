class Clip1(Scene):
    """3.3.1 - Internet no es una red: son decenas de miles de redes
    unidas por contratos. Cada enlace dice quien paga a quien, y hay
    cables que existen y no se usan. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El mapa de los AS")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: no hay una red, hay muchas --------------------------
        rot.mostrar(pie_curso("Internet no es una red: es un acuerdo entre "
                              "decenas de miles de redes."),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_AS, ARISTAS_AS, TIPOS_AS, costos=False,
                         tam=0.46, fs=14)
        etiquetas_a(topo, ETIQ_AS)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.2)
        et_cuantos = tag_hud("%s sistemas autonomos  (medicion publica)"
                             % AS_EN_INTERNET, font_size=19, color=C_RED)
        et_cuantos.move_to(DOWN * 2.62)
        self.play(FadeIn(et_cuantos), run_time=0.4)
        self.wait(4.4)

        # --- momento: cada enlace es un contrato --------------------------
        rot.mostrar(pie_curso("Cada enlace es un contrato: el cliente paga "
                              "al proveedor, los pares no se cobran."),
                    zona="abajo", run_time=0.5)
        jer = VGroup(*[topo.enlace(a, b).linea.copy().set_stroke(
            C_CAPA, width=3.6) for a, b in JERARQUIA])
        par = VGroup(*[topo.enlace(a, b).linea.copy().set_stroke(
            C_OK, width=3.6) for a, b in PARES])
        self.play(LaggedStart(*[Create(t) for t in jer], lag_ratio=0.16),
                  run_time=1.3)
        self.play(LaggedStart(*[Create(t) for t in par], lag_ratio=0.3),
                  run_time=0.7)

        def _leyenda(color, texto):
            raya = Line(LEFT * 0.24, RIGHT * 0.24, color=color,
                        stroke_width=3.6)
            t = tag_hud(texto, font_size=18, color=color)
            t.next_to(raya, RIGHT, buff=0.16)
            return VGroup(raya, t)

        leyenda = VGroup(_leyenda(C_CAPA, "cliente paga al proveedor"),
                         _leyenda(C_OK, "pares: gratis")
                         ).arrange(RIGHT, buff=0.85)
        leyenda.move_to(DOWN * 2.62)
        self.play(FadeOut(et_cuantos), FadeIn(leyenda), run_time=0.5)
        self.wait(4.6)

        # --- momento: el cable que existe y no se usa ---------------------
        rot.mostrar(pie_curso("%s cuelga de dos proveedores. No va a pagar "
                              "a los dos por trafico ajeno." % VALLE[1]),
                    zona="abajo", run_time=0.5)
        via = tramo(topo, VALLE[0], VALLE[1], 0.0, 0.66)
        tok = ficha("dato", lado=0.64, fs=15)
        tok.move_to(via.get_start())
        self.play(FadeIn(tok, scale=1.3), run_time=0.4)
        self.play(MoveAlongPath(tok, via), run_time=1.1)
        veto = VGroup(
            Line(LEFT * 0.35 + DOWN * 0.35, RIGHT * 0.35 + UP * 0.35,
                 color=C_PERDIDA, stroke_width=5.5),
            Line(LEFT * 0.35 + UP * 0.35, RIGHT * 0.35 + DOWN * 0.35,
                 color=C_PERDIDA, stroke_width=5.5))
        veto.move_to(via.get_end())
        self.play(FadeIn(veto, scale=1.5),
                  topo.nodo(VALLE[1]).forma.animate.set_stroke(
                      C_PERDIDA, width=3.6),
                  run_time=0.6)
        self.wait(4.4)

        # --- momento: el rodeo que si tiene contrato ----------------------
        rot.mostrar(pie_curso("El cable esta ahi. El contrato, no: el "
                              "trafico da el rodeo que alguien paga."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(veto), FadeOut(tok),
                  topo.nodo(VALLE[1]).forma.animate.set_stroke(
                      C_RED, width=2.6),
                  run_time=0.4)
        tok2 = ficha("dato", lado=0.64, fs=15)
        tok2.move_to(tramo(topo, RODEO[0], RODEO[1]).get_start())
        self.play(FadeIn(tok2, scale=1.3), run_time=0.4)
        self.play(MoveAlongPath(tok2, tramo(topo, RODEO[0], RODEO[1])),
                  run_time=1.0)
        self.play(MoveAlongPath(tok2, tramo(topo, RODEO[1], RODEO[2],
                                            0.0, 0.74)), run_time=1.0)
        self.play(topo.nodo(RODEO[2]).forma.animate.set_stroke(
            C_OK, width=3.6), run_time=0.35)
        et_tesis = tag_hud("dentro de una red manda la distancia; "
                           "entre redes, el contrato",
                           font_size=19, color=C_CIFRA)
        et_tesis.move_to(DOWN * 2.62)
        self.play(FadeOut(leyenda), FadeIn(et_tesis), run_time=0.5)
        self.wait(4.6)

class Clip1(Scene):
    """8.1.1 - GEO: la luz manda. La geometria a escala DECLARADA y los
    tramos MEDIDOS: 119.4 ms al satelite, 238.7 de subir y bajar, 477.5 de
    usuario a usuario. Esa cifra no se negocia. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("GEO: la luz manda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la geometria, a escala declarada --------------------
        rot.mostrar(pie_curso("Un satelite geoestacionario vive a 35 786 km "
                              "sobre el ecuador."),
                    zona="abajo", run_time=0.5)
        cx, y_centro = -3.40, -2.35
        y_suelo = y_centro + R_TIERRA_U
        tierra = Arc(radius=R_TIERRA_U, start_angle=-20 * DEGREES,
                     angle=220 * DEGREES,
                     arc_center=np.array([cx, y_centro, 0.0]),
                     color=C_EJE, stroke_width=3.0)
        et_tierra = tag_hud("Tierra", font_size=16, color=C_EJE)
        et_tierra.next_to(tierra, DOWN, buff=0.10)
        est = nodo("host", None, tam=0.30, color=C_RED)
        est.move_to(np.array([cx, y_suelo + 0.20, 0.0]))
        et_est = tag_junto(est, "estacion", LEFT, buff=0.20, font_size=17)
        sat = nodo("satelite", None, tam=0.44, color=C_RED)
        sat.move_to(np.array([cx, y_suelo + GEO_U, 0.0]))
        et_sat = tag_junto(sat, "GEO", LEFT, buff=0.24, font_size=19)
        vinculo = enlace(est.centro(), sat.centro(), color=C_RED, grosor=2.6)
        escala = tag_hud("escala real: %s km por unidad de pantalla"
                         % miles(ESCALA_KM), font_size=16, color=C_EJE)
        escala.move_to(np.array([1.90, 2.45, 0.0]))
        self.play(Create(tierra), FadeIn(et_tierra), FadeIn(est),
                  FadeIn(et_est), run_time=0.9)
        self.play(Create(vinculo.linea), FadeIn(sat), FadeIn(et_sat),
                  run_time=1.0)
        medida = llave(vinculo.linea, "%s km" % miles(GEO_KM),
                       direccion=RIGHT, font_size=21, color=C_CALCULO)
        self.play(FadeIn(medida), FadeIn(escala), run_time=0.6)
        self.wait(4.4)

        # --- momento: la luz tarda lo que tarda ---------------------------
        rot.mostrar(pie_curso("La luz no negocia. Subir hasta el es un tramo "
                              "de ciento diecinueve milisegundos."),
                    zona="abajo", run_time=0.5)
        pkt = ficha("", lado=0.34, color=C_PAQUETE)
        pkt.move_to(vinculo.punto_en(0.02))
        camino = VMobject()
        camino.set_points_as_corners([vinculo.punto_en(0.02),
                                      vinculo.punto_en(0.80)])
        self.play(FadeIn(pkt, scale=1.3), run_time=0.3)
        self.play(MoveAlongPath(pkt, camino), run_time=1.6)
        marca = reloj(GEO_IDA, etiqueta="un tramo", dec=1, fs=27)
        marca.move_to(np.array([3.00, 0.45, 0.0]))
        self.play(FadeIn(marca, shift=0.15 * UP), run_time=0.5)
        self.wait(4.3)

        # --- momento: cuenta los tramos -----------------------------------
        rot.mostrar(pie_curso("Cuenta los tramos: subir, bajar al otro lado, "
                              "y todo otra vez para la respuesta."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(tierra, et_tierra, est, et_est, sat, et_sat,
                                 vinculo, medida, escala, pkt, marca)),
                  run_time=0.5)
        x0, av = -1.30, 1.42
        r1 = regla_viajes(1, "al satelite", ancho_viaje=av, alto=0.44,
                          fs=14, nombres=["subir"])
        r1.shift(np.array([x0, 1.00, 0.0]))
        r2 = regla_viajes(2, "y de vuelta", ancho_viaje=av, alto=0.44,
                          fs=14, nombres=["subir", "bajar"])
        r2.shift(np.array([x0, 0.00, 0.0]))
        r3 = regla_viajes(4, "y contestar", ancho_viaje=av, alto=0.44,
                          fs=14, nombres=["subir", "bajar", "subir", "bajar"])
        r3.shift(np.array([x0, -1.00, 0.0]))
        c1, c2, c3 = (cifra_ms(r1, GEO_IDA), cifra_ms(r2, GEO_RTT),
                      cifra_ms(r3, GEO_USR, font_size=22, color=C_PAQUETE))
        for regla, cifra, espera in ((r1, c1, 1.2), (r2, c2, 1.2),
                                     (r3, c3, 2.6)):
            self.play(FadeIn(regla, shift=0.10 * RIGHT), run_time=0.5)
            self.play(FadeIn(cifra), run_time=0.3)
            self.wait(espera)

        # --- momento: la cifra que no se negocia --------------------------
        rot.mostrar(pie_curso("Esa cifra no la pone el operador. La pone la "
                              "luz, y no hay contrato que la baje."),
                    zona="abajo", run_time=0.5)
        x_cable = x0 + (CABLE_MS / GEO_IDA) * av
        raya = DashedLine(np.array([x_cable, -1.35, 0.0]),
                          np.array([x_cable, 1.32, 0.0]),
                          color=C_OK, stroke_width=2.6, dash_length=0.11)
        et_cable = VGroup(
            tag_hud("un cable de %s km, ida y vuelta:" % miles(CABLE_KM),
                    font_size=17, color=C_EJE),
            tag_hud("%s ms" % fmt(CABLE_MS, 1), font_size=17, color=C_OK),
        ).arrange(RIGHT, buff=0.18)
        et_cable.move_to(np.array([x_cable, 1.70, 0.0]))
        self.play(Create(raya), run_time=0.6)
        self.play(FadeIn(et_cable), run_time=0.4)
        self.wait(5.0)

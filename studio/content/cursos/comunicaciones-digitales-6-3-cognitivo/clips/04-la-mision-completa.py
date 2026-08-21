class Clip4(Scene):
    """6.3.4 - La mision completa: un paquete cruza los seis modulos de la
    familia, de la sonda a la Tierra. Cierre de FAMILIA. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La mision completa")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        XS = [-4.55, 0.0, 4.55]
        Y_ARR, Y_ABA = 1.55, -1.45
        COLORES = [C_BIT, C_SENAL, C_RUIDO, C_COD, C_BANDA, C_IA]

        # --- los seis iconos de la familia ---------------------------------
        # M1: los bits de la muestra (leccion 1.1)
        ic1 = tren_bits(BITS_MISION, lado=0.26)
        # M2: la constelacion QPSK (leccion 2.1)
        piq = plano_iq(unidad=0.30, alcance=1.55)
        ic2 = VGroup(piq, piq.puntos(P_QPSK, color=C_BIT, radio=0.05))
        # M3: el vacio entre la nave y la Tierra (leccion 3.1)
        enl = enlace_tierra(dist=1.55, radio_tierra=0.26, curva=0.24)
        enl.rotate(PI)                      # la nave a la izquierda
        ic3 = enl
        # M4: el trellis que repara (leccion 4.2)
        tre = trellis(pasos=4, ancho=1.45, alto=0.80)
        ic4 = VGroup(tre.todas_ramas(color=C_REJILLA, grosor=1.0,
                                     opacidad=0.55),
                     tre.puntos,
                     tre.camino(CAMINO_TRELLIS, color=C_COD, grosor=3.0))
        # M5: la escalera de modcods (leccion 5.2)
        barras = VGroup()
        for a in range(len(MODCOD_TASAS)):
            h = 0.27 * MODCOD_TASAS[a]
            b = Rectangle(width=0.30, height=h, color=MODCOD_COLORES[a],
                          fill_color=MODCOD_COLORES[a], fill_opacity=0.45,
                          stroke_width=1.8)
            b.move_to([0.44 * (a - 1), -0.45 + h / 2.0, 0])
            barras.add(b)
        ic5 = barras
        # M6: el agente (leccion 6.1/6.2)
        ic6 = perceptron_mini(ocultas=4, salidas=3, ancho=1.10, alto=0.86)

        iconos = [ic1, ic2, ic3, ic4, ic5, ic6]
        pos_icono = [(XS[0], Y_ARR + 0.30), (XS[1], Y_ARR + 0.30),
                     (XS[2], Y_ARR + 0.30), (XS[2], Y_ABA + 0.30),
                     (XS[1], Y_ABA + 0.30), (XS[0], Y_ABA + 0.30)]
        pos_caja = [(XS[0], Y_ARR - 0.66), (XS[1], Y_ARR - 0.66),
                    (XS[2], Y_ARR - 0.66), (XS[2], Y_ABA - 0.66),
                    (XS[1], Y_ABA - 0.66), (XS[0], Y_ABA - 0.66)]
        etapas = []
        for k in range(6):
            iconos[k].move_to([pos_icono[k][0], pos_icono[k][1], 0])
            caja = bloque(MODULOS[k], ancho=2.75, alto=0.56,
                          color=COLORES[k], tamano=16)
            caja.move_to([pos_caja[k][0], pos_caja[k][1], 0])
            etapas.append(VGroup(iconos[k], caja))
        cajas = [e[1] for e in etapas]

        conexiones = [conectar(etapas[k], etapas[k + 1], color=C_EJE,
                               grosor=2.4) for k in range(5)]
        caminos = [Line(c.get_start(), c.get_end()) for c in conexiones]

        # --- momento: el camino entero -------------------------------------
        rot.mostrar(pie_curso("Un paquete sale de una sonda en Marte. Este "
                              "es su camino entero, modulo a modulo."),
                    zona="abajo", run_time=0.5)
        self.play(LaggedStart(*[FadeIn(e, shift=0.15 * UP) for e in etapas],
                              lag_ratio=0.16), run_time=2.0)
        self.play(LaggedStart(*[GrowArrow(c) for c in conexiones],
                              lag_ratio=0.18), run_time=1.2)
        self.wait(2.8)

        # --- momento: del dato al vacio -------------------------------------
        rot.mostrar(pie_curso("El dato hecho bits; la fase que los lleva; y "
                              "el vacio que los debilita."),
                    zona="abajo", run_time=0.5)
        paq = punto_brillante(caminos[0].get_start(), color=C_BIT,
                              radio=0.07, capas=5, alcance=2.6)
        self.play(Indicate(cajas[0], color=COLORES[0], scale_factor=1.08),
                  run_time=0.6)
        self.play(FadeIn(paq), run_time=0.3)
        for k in (0, 1):
            paq.move_to(caminos[k].get_start())
            self.play(PulsoDeSenal(paq, caminos[k], rate_func=linear),
                      destello(conexiones[k], color=C_BIT), run_time=0.9)
            self.play(Indicate(cajas[k + 1], color=COLORES[k + 1],
                               scale_factor=1.08), run_time=0.6)
        self.wait(2.0)

        # --- momento: reparar, adaptarse, decidir ---------------------------
        rot.mostrar(pie_curso("El codigo que los repara; el enlace que se "
                              "adapta; y el agente que eligio como hablar."),
                    zona="abajo", run_time=0.5)
        for k in (2, 3, 4):
            paq.move_to(caminos[k].get_start())
            self.play(PulsoDeSenal(paq, caminos[k], rate_func=linear),
                      destello(conexiones[k], color=C_BIT), run_time=0.9)
            self.play(Indicate(cajas[k + 1], color=COLORES[k + 1],
                               scale_factor=1.08), run_time=0.6)
        self.wait(1.6)

        # --- momento: la cadena entera --------------------------------------
        rot.mostrar(pie_curso("Seis modulos para que una sola frase cruce "
                              "el vacio y llegue entera."),
                    zona="abajo", run_time=0.5)
        eleccion = tag_hud(f"el agente eligio {MODCOD_MISION}  ->  "
                           f"{fmt(TASA_MISION, 2)} bits/simb", font_size=19)
        # a la izquierda del conector vertical M3 -> M4 (x = 4.55).
        eleccion.move_to([-0.55, 0.02, 0])
        eleccion = _con_fondo(eleccion, buff=0.14, opacidad=0.88)
        self.play(FadeOut(paq), FadeIn(eleccion, shift=0.15 * UP),
                  run_time=0.6)
        self.play(flujo(conexiones, color=C_BIT, ancho=6, cola=0.5,
                        por_conexion=0.42),
                  LaggedStart(*[Indicate(c, color=COLORES[i],
                                         scale_factor=1.05)
                                for i, c in enumerate(cajas)],
                              lag_ratio=0.42), run_time=2.3)
        self.wait(3.6)

        # --- cierre de FAMILIA ----------------------------------------------
        cierre_leccion(
            self, rot,
            "El vacio sigue sin tener nada que decir.",
            "Nosotros ya sabemos cruzarlo hablando.",
            "Fin del curso: Comunicaciones digitales.",
            *etapas, *conexiones, eleccion, espera=5.5)

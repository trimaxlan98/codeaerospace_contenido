class Clip3(Scene):
    """3.3.3 - El presupuesto entero en una cascada de decibelios: a 10
    grados de elevacion el enlace cierra con 12.4 dB de margen, y el
    termino de desapuntamiento ni se nota. (~42 s)"""

    def construct(self):
        # La cascada de dB la dibuja `enlace.py`, la libreria del curso 13:
        # aqui no se re-enseña el presupuesto, se USA. Se le pasa la sombra
        # de Text del bloque de estilo (los glifos vacios inflan la caja).
        import enlace as _enl
        from enlace import cascada_db
        _enl.Text = Text

        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("La cuenta completa"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # =================================================================
        # 1. La geometria: la misma orbita, dos elevaciones
        # =================================================================
        est = np.array([-5.20, -1.95, 0.0])
        horiz = Line(est + LEFT * 1.35, est + RIGHT * 3.35,
                     stroke_width=2.4, color=C_EJE)
        d_est = Dot(est, radius=0.075, color=C_CALCULO)

        # Los DOS rayos se dibujan del MISMO largo: la figura solo declara
        # el angulo. Las distancias, que si estan a escala, van en las
        # barras de la derecha.
        largo_rayo = 2.55
        dir_10 = np.array([np.cos(np.radians(EL_ENLACE)),
                           np.sin(np.radians(EL_ENLACE)), 0.0])
        r_cenit = DashedVMobject(
            Line(est, est + UP * largo_rayo, stroke_width=2.2,
                 color=C_CIELO), num_dashes=18)
        r_bajo = DashedVMobject(
            Line(est, est + dir_10 * largo_rayo, stroke_width=2.2,
                 color=C_CIELO), num_dashes=18)
        s_cenit = Dot(est + UP * largo_rayo, radius=0.08, color=C_SAT)
        s_bajo = Dot(est + dir_10 * largo_rayo, radius=0.08, color=C_SAT)

        self.play(Create(horiz), FadeIn(d_est), run_time=0.8)
        self.play(Create(r_cenit), Create(r_bajo), run_time=1.1)
        self.play(FadeIn(s_cenit, scale=1.5), FadeIn(s_bajo, scale=1.5),
                  run_time=0.6)

        arco_el = Arc(radius=0.80, arc_center=est, start_angle=0.0,
                      angle=np.radians(EL_ENLACE), color=C_CALCULO,
                      stroke_width=2.4)
        t_el = tag_hud(f"El {fmt(EL_ENLACE, 0)} deg", font_size=19)
        t_el.move_to(est + RIGHT * 1.15 + UP * 0.60)
        t_cenit = tag_hud("cenit", font_size=19, color=C_TENUE)
        t_cenit.move_to(est + LEFT * 0.75 + UP * largo_rayo)
        self.play(Create(arco_el), FadeIn(t_el), FadeIn(t_cenit),
                  run_time=0.8)
        self.wait(0.5)

        rot.mostrar(cifra_pie(f"rango {fmt(D_ENLACE, 0)} km"), zona="abajo")
        self.wait(1.3)

        # las distancias, ahora si, a escala
        rangos = barras_comparar([H_LEO, D_ENLACE], ["cenit", "10 deg"],
                                 ancho=3.0, alto=2.1, unidad="km",
                                 colores=[C_CIELO, C_SAT])
        rangos.move_to(RIGHT * 3.85 + DOWN * 0.30)
        self.play(FadeIn(rangos), run_time=0.9)
        self.wait(1.3)

        f_cenit = tag_hud(f"{fmt(FSPL_CENIT, 2)} dB", font_size=20,
                          color=C_TENUE)
        f_cenit.move_to(est + RIGHT * 0.95 + UP * largo_rayo)
        f_bajo = tag_hud(f"{fmt(FSPL_BAJO, 2)} dB", font_size=20)
        f_bajo.move_to(est + dir_10 * largo_rayo + RIGHT * 1.05
                       + UP * 0.42)
        rot.mostrar(cifra_pie(f"FSPL {fmt(FSPL_BAJO, 2)} dB"), zona="abajo")
        self.play(FadeIn(f_cenit), FadeIn(f_bajo), run_time=0.6)
        self.wait(1.4)

        rot.mostrar(cifra_pie(f"{fmt(DELTA_FSPL, 2)} dB por geometria"),
                    zona="abajo")
        self.wait(1.9)

        # =================================================================
        # 2. La cascada entera
        # =================================================================
        rot.limpiar("abajo", run_time=0.35)
        self.play(FadeOut(VGroup(horiz, d_est, r_cenit, r_bajo, s_cenit,
                                 s_bajo, arco_el, t_el, t_cenit, f_cenit,
                                 f_bajo, rangos)), run_time=0.7)

        casc = cascada_db(
            [("EIRP", PB["eirp_dbw"]),
             ("FSPL", -PB["fspl_db"]),
             ("perdidas", -PB["perdidas_db"]),
             ("apunt", -PB["l_point_db"]),
             ("G/T", PB["g_t_db"]),
             ("-k", PB["k_db"])],
            ancho=7.6, alto=3.0, font_size=16, etiqueta_saldo="C/N0")
        casc.move_to(UP * 0.30)
        self.add(casc)
        for i in range(len(casc)):
            self.play(casc.aparecer(i, run_time=0.60))
            self.wait(0.16)
        self.play(casc.aparecer_saldo(run_time=0.9))
        self.wait(0.6)

        rot.mostrar(cifra_pie(f"C/N0 {fmt(CN0, 2)} dB-Hz"), zona="abajo")
        self.wait(2.1)
        # el termino que da nombre a la leccion, en banda S, ni se ve en la
        # cascada: por eso la barra sale de un pelo y el numero, redondeado
        # a un decimal, es un cero.
        rot.mostrar(cifra_pie(f"apuntamiento {fmt(PB['l_point_db'], 3)} dB"),
                    zona="abajo")
        self.wait(1.9)

        # =================================================================
        # 3. Lo que queda para el demodulador
        # =================================================================
        rot.limpiar("abajo", run_time=0.35)
        self.play(FadeOut(casc), run_time=0.7)

        umbral = barras_comparar([EBN0, EBN0_QPSK], ["Eb/N0", "QPSK"],
                                 ancho=3.6, alto=2.4, unidad="dB",
                                 colores=[C_OK, C_DATO])
        umbral.move_to(LEFT * 2.30 + DOWN * 0.25)
        self.play(FadeIn(umbral), run_time=0.9)
        t_tasa = tag_hud(f"tasa {fmt(TASA_BPS / 1.0e6, 0)} Mbps",
                         font_size=20)
        t_tasa.move_to(RIGHT * 2.35 + DOWN * 1.55)
        self.play(FadeIn(t_tasa), run_time=0.5)
        self.wait(0.6)

        rot.mostrar(cifra_pie(f"Eb/N0 {fmt(EBN0, 1)} dB"), zona="abajo")
        self.wait(1.6)

        y_umbral = float(umbral.cima_de(1)[1])
        linea = DashedVMobject(
            Line(np.array([-4.35, y_umbral, 0.0]),
                 np.array([1.05, y_umbral, 0.0]), stroke_width=2.4,
                 color=C_DATO), num_dashes=32)
        self.play(Create(linea), run_time=0.7)
        # El umbral de QPSK es literatura, no se midio aqui: va en gris.
        rot.mostrar(dato_pie(f"QPSK pide {fmt(EBN0_QPSK, 1)} dB"),
                    zona="abajo")
        self.wait(1.8)

        cima = umbral.cima_de(0)
        flecha = DoubleArrow(np.array([0.55, y_umbral, 0.0]),
                             np.array([0.55, float(cima[1]), 0.0]),
                             buff=0.0, color=C_OK, stroke_width=4,
                             max_tip_length_to_length_ratio=0.10)
        t_margen = tag_hud(f"margen {fmt(MARGEN_ENLACE, 1)} dB",
                           font_size=21, color=C_OK)
        t_margen.move_to(RIGHT * 2.55 + UP * 0.35)
        self.play(GrowFromCenter(flecha), FadeIn(t_margen), run_time=0.9)
        self.wait(0.7)

        rot.mostrar(cifra_pie(f"margen {fmt(MARGEN_ENLACE, 1)} dB",
                              color=C_OK), zona="abajo")
        self.wait(1.8)

        panel = panel_cifras(f"C/N0 {fmt(CN0, 1)} dB-Hz",
                             f"Eb/N0 {fmt(EBN0, 1)} dB",
                             (f"margen {fmt(MARGEN_ENLACE, 1)} dB", C_OK))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)

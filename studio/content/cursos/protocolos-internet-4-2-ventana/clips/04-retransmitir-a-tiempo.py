class Clip4(Scene):
    """4.2.4 - El estimador de Jacobson (RFC 6298): SRTT y RTTVAR sobre
    muestras reales, el RTO y su margen. Cierre de la leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Retransmitir a tiempo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: TCP estima, no sabe -----------------------------
        rot.mostrar(pie_curso("TCP no sabe cuanto tardara un ACK: lo "
                              "estima con cada muestra que ve."),
                    zona="abajo", run_time=0.5)
        sig = sierra(MUESTRAS_RTT, perdidas=(IDX_PICO,), ancho=5.0,
                    alto=2.3, color=C_CIFRA, etiqueta="RTT muestreado (ms)")
        sig.move_to(LEFT * 3.6 + UP * 0.25)
        tab = tabla(["paso", "muestra", "SRTT", "RTO"], [],
                   anchos=[0.75, 1.15, 1.15, 1.15], alto=0.34, fs=13,
                   filas_max=7, resaltable=True)
        tab.move_to(RIGHT * 2.9 + UP * 0.25)
        self.play(FadeIn(sig.ejes), FadeIn(sig.etiqueta), FadeIn(tab),
                  run_time=0.8)
        self.play(Create(sig.curva), run_time=1.6)
        self.wait(2.0)

        # --- momento: muestras tranquilas ------------------------------
        rot.mostrar(pie_curso("Con muestras tranquilas, el estimado del "
                              "RTO baja poco a poco."),
                    zona="abajo", run_time=0.5)
        filas = []
        for k in range(3):
            filas.append(FILAS_RJ[k])
            nueva = tab.con_filas(filas, resaltar=k)
            self.play(Transform(tab, nueva), run_time=0.45)
        self.wait(2.0)

        # --- momento: la muestra fuera de lo comun --------------------
        rot.mostrar(pie_curso("Una muestra fuera de lo comun dispara la "
                              "varianza, y el RTO salta."),
                    zona="abajo", run_time=0.5)
        filas.append(FILAS_RJ[IDX_PICO])
        nueva = tab.con_filas(filas, resaltar=IDX_PICO)
        self.play(Transform(tab, nueva), FadeIn(sig.marcas), run_time=0.7)
        self.wait(3.0)

        # --- momento: vuelve a bajar, sin llegar al piso -------------------
        rot.mostrar(pie_curso("Las muestras siguientes son tranquilas de "
                              "nuevo: el RTO baja, sin volver al piso "
                              "anterior."),
                    zona="abajo", run_time=0.5)
        for k in range(IDX_PICO + 1, len(FILAS_RJ)):
            filas.append(FILAS_RJ[k])
            nueva = tab.con_filas(filas, resaltar=k)
            self.play(Transform(tab, nueva), run_time=0.45)
        self.play(FadeIn(sig.media), run_time=0.4)
        self.wait(2.4)

        # --- momento: el margen que separa varianza de perdida -------------
        rot.mostrar(pie_curso("El margen entre el SRTT y el RTO absorbe "
                              "esa variacion sin confundirla con una "
                              "perdida real."),
                    zona="abajo", run_time=0.5)
        resumen = VGroup(
            tag_hud("SRTT final = %s ms" % fmt(RJ["srtt"], 2),
                   font_size=19, color=C_CIFRA),
            tag_hud("RTO final = %s ms" % fmt(RJ["rto"], 2),
                   font_size=19, color=C_CIFRA),
            tag_hud("margen = %s ms  (%s veces el SRTT)"
                   % (fmt(RJ["margen"], 2), fmt(RATIO_RTO_SRTT, 2)),
                   font_size=19, color=C_COLA),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        resumen.move_to(DOWN * 1.9)
        self.play(FadeIn(resumen, shift=0.1 * UP), run_time=0.6)
        self.wait(4.2)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "Fiabilidad no es no perder nada.",
            "Es darse cuenta a tiempo.",
            "Siguiente: la congestion, la cortesia que sostiene la red.",
            resumen, sig, tab, espera=4.8)

class Clip3(Scene):
    """4.3.3 - El margen: los decibelios de respeto que separan el SNR
    de cielo claro del umbral, y la tormenta comiendoselos. La zona
    sombreada es el enlace CAIDO. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El margen")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        mar = margen_enlace(alto=3.4)
        mar.move_to(DOWN * 0.15)
        eje_t = tag_junto(mar.ejes[0], "tiempo (min)", DOWN, buff=0.16)
        eje_s = tag_junto(mar.ejes[1], "SNR (dB)", UP, buff=0.12)

        # --- momento: el umbral, la linea roja de la verdad -----------------
        rot.mostrar(pie_curso("Cerrar un enlace no es llegar: es llegar "
                              "con reserva. Y hay una raya roja."),
                    zona="abajo", run_time=0.45)
        self.play(FadeIn(mar.ejes), FadeIn(eje_t), FadeIn(eje_s),
                  Create(mar.umbral), run_time=0.9)
        self.wait(4.6)

        # --- momento: el cielo claro y los dB de respeto --------------------
        # La linea de cielo claro se traza con los localizadores de la
        # pieza: nace y muere exactamente sobre el SNR que dibuja la curva.
        claro = Line(mar.punto_de(0.0), mar.punto_de(40.0),
                     stroke_width=2.8, color=C_CALCULO)
        x_flecha = mar.punto_de(4.0)[0]
        y_claro = mar.punto_de(0.0)[1]
        y_umbral = mar.umbral.get_start()[1]
        flecha = DoubleArrow((x_flecha, y_umbral, 0.0),
                             (x_flecha, y_claro, 0.0), buff=0.04,
                             color=C_CALCULO, stroke_width=3.0,
                             tip_length=0.14)
        # Etiqueta corta: la curva bajara justo por donde caeria un rotulo
        # largo, y quien nombra el margen es el pie.
        tag_margen = tag_hud(f"{mar.margen_db():.0f} dB", font_size=18)
        tag_margen.next_to(flecha, RIGHT, buff=0.14)
        rot.mostrar(pie_curso("En cielo claro la señal va seis decibelios "
                              "por encima. Eso es el margen."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.play(Create(claro), run_time=0.8)
        self.play(GrowArrow(flecha), FadeIn(tag_margen), run_time=0.6)
        self.wait(4.6)

        # --- momento: la tormenta se lo come --------------------------------
        rot.mostrar(pie_curso("Entra la tormenta. El margen se gasta en "
                              "minutos y la señal se hunde."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.play(ReplacementTransform(claro, mar.curva), run_time=1.6)
        self.wait(3.0)

        # --- momento: la zona en la que el enlace esta caido ----------------
        t_min, snr_min = mar.minimo()
        fondo = Dot(mar.punto_de(t_min), radius=0.07, color=C_CARGA)
        tag_fondo = tag_hud(f"{snr_min:.1f} dB", font_size=17,
                            color=C_CARGA)
        # A la altura del fondo pero fuera de la V: dentro no cabe un rotulo
        # sin que la rama descendente lo cruce.
        tag_fondo.next_to(fondo, LEFT, buff=0.55)
        rot.mostrar(pie_curso("Bajo la raya no hay señal degradada: no "
                              "hay señal. El enlace está caído."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.play(FadeIn(mar.corte), FadeIn(fondo, scale=1.6),
                  FadeIn(tag_fondo), run_time=0.7)
        self.bring_to_front(mar.curva, mar.umbral, fondo, tag_fondo)
        self.wait(4.6)

        rot.mostrar(pie_curso("Un enlace moderno negocia antes de morir: "
                              "el DVB-S2 baja de modulación y aguanta."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.wait(4.6)

        rot.mostrar(pie_curso("Pero el margen no se negocia: se compra, "
                              "con decibelios de antena o de potencia."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.wait(4.8)

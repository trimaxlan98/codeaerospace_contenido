class Clip3(Scene):
    """1.1.3 - El dipolo: mas y menos juntos. De lejos casi se cancelan
    (el campo muere con el CUBO), y esa es justo la razon de que una
    antena tenga que oscilar. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El dipolo: la semilla de la antena")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el mapa del dipolo -----------------------------------
        dipolo = lineas_campo([(1.0, -1.4, -0.1), (-1.0, 1.4, -0.1)],
                              n_lineas=10)
        self.play(FadeIn(dipolo.cargas, scale=1.3), run_time=0.6)
        rot.mostrar(pie_curso("Una carga y su contraria, pegadas: la "
                              "pareja mas importante de la técnica."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        self.play(Create(dipolo.lineas), FadeIn(dipolo.flechas),
                  run_time=1.8)
        rot.mostrar(pie_curso("Cada línea sale del más y muere en el "
                              "menos: el mapa se cierra sobre sí."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: de lejos casi se cancela -----------------------------
        rot.mostrar(pie_curso("Vista de lejos, la pareja suma casi cero. "
                              "¿Cuánto le queda?"), zona="abajo",
                    run_time=0.5)
        curvas = haz_curvas(
            [lambda r: campo_puntual(1.0, r) / campo_puntual(1.0, 1.0),
             lambda r: campo_dipolo_eje(1.0, r) / campo_dipolo_eje(1.0,
                                                                   1.0)],
            (1.0, 3.0), [C_E, C_ONDA], nombres=["carga", "dipolo"],
            ancho=5.6, alto=2.8, etiqueta_x="distancia (relativa)")
        curvas.move_to(DOWN * 0.25 + LEFT * 0.4)
        self.play(ReplacementTransform(dipolo, curvas), run_time=1.4)
        self.wait(3.2)

        # Las cifras de la caida van sobre el corte de r = 3, cada una del
        # color de su curva; el numero sale de las MISMAS funciones.
        guia = curvas.vertical_en(3.0, color=C_EJE)
        p_mono = Dot(curvas.punto_de(0, 3.0), radius=0.06, color=C_E)
        p_dipo = Dot(curvas.punto_de(1, 3.0), radius=0.06, color=C_ONDA)
        tag_mono = tag_hud(f"{CAIDA_MONO_3M * 100:.0f} %", font_size=16,
                           color=C_E)
        tag_mono.next_to(p_mono, UR, buff=0.10)
        tag_dipo = tag_hud(f"{CAIDA_DIPO_3M * 100:.1f} %", font_size=16,
                           color=C_ONDA)
        tag_dipo.next_to(p_dipo, DR, buff=0.10)
        rot.mostrar(pie_curso("La carga cae con el cuadrado; el dipolo, "
                              "con el CUBO. Triple distancia: 4 %."),
                    zona="abajo", run_time=0.5)
        self.play(Create(guia), FadeIn(p_mono), FadeIn(p_dipo),
                  FadeIn(tag_mono), FadeIn(tag_dipo), run_time=0.8)
        self.wait(4.6)

        rot.mostrar(pie_curso("Un dipolo quieto no llega a ninguna "
                              "parte. La salida: hacerlo OSCILAR."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Toda antena que veas en este curso es "
                              "esto mismo, oscilando. Paciencia."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

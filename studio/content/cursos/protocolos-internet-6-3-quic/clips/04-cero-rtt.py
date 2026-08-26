class Clip4(Scene):
    """6.3.4 - 0-RTT: los datos en el primer paquete al reanudar, con su
    aviso honesto; y el ID de conexion que sobrevive al cambio de wifi a
    movil. Cierre de la leccion y del modulo 6. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("0-RTT y la mudanza de red")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: reanudar lo que ya se acordo ------------------------
        rot.mostrar(pie_curso("Si ya hablaste con ese sitio, QUIC guarda el "
                              "acuerdo y lo reanuda."),
                    zona="abajo", run_time=0.5)
        b_h3 = fila_viajes(VIAJES_H3, "HTTP/3", MS("h3"), y=1.55)
        b_0 = fila_viajes(VIAJES_0RTT, "0-RTT", MS("h3-0rtt"), y=0.45)
        self.play(FadeIn(b_h3), run_time=0.6)
        self.play(FadeIn(b_0), run_time=0.7)
        self.wait(3.2)

        # --- momento: los datos en el primer paquete ----------------------
        rot.mostrar(pie_curso("Los datos van dentro del primer paquete: cero "
                              "viajes de apreton."),
                    zona="abajo", run_time=0.5)
        cifras = VGroup(
            tag_hud("apreton al reanudar:   %s viajes" % fmt(APRETON_0RTT, 0),
                    font_size=20, color=C_COLA),
            tag_hud("la pagina entera:      %s ms" % fmt(MS("h3-0rtt"), 0),
                    font_size=22),
            tag_hud("%s veces menos que HTTP/1.0 en serie"
                    % fmt(GANANCIA_0RTT, 0), font_size=20, color=C_PAQUETE),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras.move_to(np.array([0.0, -0.90, 0.0]))
        self.play(LaggedStart(*[FadeIn(c, shift=0.10 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=1.2)
        self.wait(3.4)

        # --- momento: el aviso honesto ------------------------------------
        rot.mostrar(pie_curso("Ese primer paquete se puede grabar y volver a "
                              "mandar. No vale para todo."),
                    zona="abajo", run_time=0.5)
        aviso = tag_hud("aviso:  %s" % AVISO_0RTT, font_size=20,
                        color=C_PERDIDA)
        aviso.move_to(np.array([0.0, -2.20, 0.0]))
        self.play(FadeIn(aviso), run_time=0.5)
        self.wait(3.6)

        # --- momento: la mudanza de red -----------------------------------
        rot.mostrar(pie_curso("Y hay otra cosa que QUIC no pierde: cambiar "
                              "del wifi a los datos moviles."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(b_h3, b_0, cifras, aviso)), run_time=0.7)
        tab = tabla(["campo", "en el wifi", "en el movil"], FILAS_MUDANZA,
                    anchos=[3.2, 2.6, 2.6], alto=0.46, fs=17)
        tab.move_to(np.array([0.0, 0.55, 0.0]))
        tupla4 = VGroup(*[tab.fila(i) for i in range(4)])
        br_izq = llave(tupla4, "4-tupla", LEFT, font_size=18)
        self.play(FadeIn(tab), run_time=0.9)
        self.play(FadeIn(br_izq), run_time=0.5)
        cambio = [tab.celda(CAMBIA_FILA[0], j).animate.set_color(C_PERDIDA)
                  for j in range(3)]
        self.play(*cambio, run_time=0.6)
        self.wait(3.4)

        # --- momento: la conexion es un ID, no una direccion --------------
        rot.mostrar(pie_curso("Para TCP eso ya es otra conexion. Para QUIC, "
                              "el ID no ha cambiado."),
                    zona="abajo", run_time=0.5)
        igual = [tab.celda(4, j).animate.set_color(C_OK) for j in range(3)]
        # Un Brace sobre UNA fila sale como una astilla y se come su
        # propia etiqueta: la marca de esa fila va como tag suelto.
        br_der = tag_hud("no cambia", font_size=18, color=C_OK)
        br_der.next_to(tab.celda(4, 2), RIGHT, buff=0.55)
        self.play(*igual, FadeIn(br_der), run_time=0.7)
        razones = VGroup(
            tag_hud("TCP:   %s" % POR_QUE_TCP, font_size=19,
                    color=C_PERDIDA),
            tag_hud("QUIC:  %s" % POR_QUE_QUIC, font_size=19, color=C_OK),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        razones.move_to(np.array([0.0, -1.85, 0.0]))
        self.play(LaggedStart(*[FadeIn(r, shift=0.10 * UP) for r in razones],
                              lag_ratio=0.40), run_time=1.0)
        self.wait(3.4)

        # --- cierre de la leccion y del modulo 6 --------------------------
        cierre_leccion(
            self, rot,
            "La web no se hizo mas rapida cambiando el cable.",
            "Se hizo mas rapida cambiando la cola.",
            "Cierra el modulo 6. En el 7, la red real: distancia y colas.",
            tab, br_izq, br_der, razones, espera=6.6)

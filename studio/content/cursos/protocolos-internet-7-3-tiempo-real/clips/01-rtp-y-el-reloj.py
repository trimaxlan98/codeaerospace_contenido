class Clip1(Scene):
    """7.3.1 - La voz se trocea en paquetes de 20 ms sobre UDP, cada uno
    con su propia marca de tiempo; llegar tarde vale igual que perderse.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("RTP y el reloj")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la voz troceada, con su propio reloj -----------------
        rot.mostrar(pie_curso("Una llamada de voz se trocea en paquetes de "
                              "20 milisegundos, uno tras otro."),
                    zona="abajo", run_time=0.5)
        p = paquete([("Secuencia", 1.0, "1"), ("Marca de tiempo", 1.5,
                     "0 ms"), ("Carga util", 2.1, "voz 20 ms")],
                    ancho=6.4, alto=0.76)
        p.move_to(UP * 0.85)
        self.play(FadeIn(p), run_time=0.7)
        self.wait(2.0)
        for seq in range(2, RTP_N):
            marca = (seq - 1) * RTP_PASO_MS
            nuevo = p.con_valores({"Secuencia": str(seq),
                                   "Marca de tiempo": "%d ms" % marca})
            self.play(Transform(p, nuevo), run_time=0.35)
            self.wait(0.55)
        et_reloj = tag_hud("cada paquete lleva SU marca de tiempo: es su "
                           "reloj, no el de la red", font_size=18,
                           color=C_EJE)
        et_reloj.next_to(p, DOWN, buff=0.45)
        self.play(FadeIn(et_reloj), run_time=0.5)
        self.wait(1.2)

        # --- momento: sobre UDP, directo al socket -------------------------
        rot.mostrar(pie_curso("Van sueltos por UDP: nadie los reordena ni "
                              "los retransmite por el camino."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(p), FadeOut(et_reloj), run_time=0.4)
        socket_tag = tag_hud("socket en escucha  198.51.100.7:5004  ->  "
                             "app_voz", font_size=17, color=C_RED)
        socket_tag.move_to(UP * 1.35)
        paquetes_udp = VGroup(*[ficha(str(i + 1), lado=0.52,
                                      color=C_PAQUETE)
                                for i in range(RTP_N)])
        paquetes_udp.arrange(RIGHT, buff=0.22).move_to(UP * 0.30)
        self.play(FadeIn(socket_tag), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(f, shift=0.15 * DOWN)
                                for f in paquetes_udp], lag_ratio=0.2),
                  run_time=1.2)
        et_demux = tag_hud("%d de %d datagramas entregados al socket, en "
                           "cuanto llegan" % (DEMUX["entregados"],
                                              DEMUX["total"]),
                           font_size=19, color=C_OK)
        et_demux.next_to(paquetes_udp, DOWN, buff=0.35)
        self.play(FadeIn(et_demux), run_time=0.5)
        self.wait(4.0)

        # --- momento: llegar tarde es igual que perderse -------------------
        rot.mostrar(pie_curso("Pero el 4 llega despues que el 5: su turno "
                              "para sonar ya paso."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(socket_tag), FadeOut(paquetes_udp),
                  FadeOut(et_demux), run_time=0.5)
        def _con_secuencia(rng):
            """`Ranuras` numera 0..n-1; aqui las ranuras son turnos de
            paquete y deben leerse con el MISMO numero de 'Secuencia' del
            paquete de arriba (1-based). protocolos.py no expone un
            offset, asi que se reescribe el digito tras construir la
            pieza (sin tocar la libreria)."""
            for i, t in enumerate(rng.numeros):
                nuevo_d = tag_hud(str(i + 1), font_size=14, color=C_EJE)
                nuevo_d.move_to(t.get_center())
                t.become(nuevo_d)
            return rng

        r = _con_secuencia(ranuras(n=RTP_N, colores=[None] * RTP_N,
                                   lado=0.62, fs=16,
                                   etiqueta="turno para sonar"))
        r.move_to(UP * 0.20)
        self.play(FadeIn(r), run_time=0.6)
        for i in range(RTP_N):
            seq = i + 1
            colores = ([C_PERDIDA if s == RTP_PERDIDO else C_OK
                       for s in range(1, seq + 1)] + [None] * (RTP_N - seq))
            nuevo = _con_secuencia(r.con_colores(colores))
            self.play(Transform(r, nuevo), run_time=0.32)
            self.wait(0.14)
        et_perdido = tag_hud("paquete %d: llega tarde -> se descarta, no "
                             "se espera" % RTP_PERDIDO, font_size=19,
                             color=C_PERDIDA)
        et_perdido.next_to(r, DOWN, buff=0.42)
        self.play(FadeIn(et_perdido), run_time=0.5)
        self.wait(3.2)

        # --- momento: la idea que gobierna el modulo ------------------------
        rot.mostrar(pie_curso("Para la voz, un paquete tarde es un "
                              "paquete perdido. Por eso RTP va sobre UDP, "
                              "con su propio reloj."),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)

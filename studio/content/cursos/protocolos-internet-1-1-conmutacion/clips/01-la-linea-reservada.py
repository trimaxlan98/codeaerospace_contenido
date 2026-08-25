class Clip1(Scene):
    """1.1.1 - Reservar un camino entero para hablar: el circuito
    garantiza lo que promete y desperdicia lo que no usas. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La linea reservada")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la red y los dos extremos ---------------------------
        rot.mostrar(pie_curso("Durante cien anos, hablar con alguien lejos "
                              "fue tender una linea hasta el."),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_RED, ARISTAS_RED, TIPOS_RED, costos=False)
        topo.shift(UP * 0.45)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.2)
        self.wait(4.6)

        # --- momento: el circuito se reserva ------------------------------
        rot.mostrar(pie_curso("Antes del primer bit, la red reserva el "
                              "camino entero. Solo para ti."),
                    zona="abajo", run_time=0.5)
        tramos = VGroup(*[topo.enlace(a, b).linea.copy().set_stroke(
            C_OK, width=6.0)
                          for a, b in zip(CAMINO_ALTO[:-1], CAMINO_ALTO[1:])])
        self.play(LaggedStart(*[Create(t) for t in tramos], lag_ratio=0.45),
                  run_time=1.8)
        et_circ = tag_hud("circuito reservado", font_size=18, color=C_OK)
        et_circ.next_to(topo.punto("R2"), UP, buff=0.32)
        self.play(FadeIn(et_circ), run_time=0.4)
        self.wait(4.4)

        # --- momento: lo que cuesta reservar ------------------------------
        rot.mostrar(pie_curso("Reservar cuesta tiempo, y la linea sigue "
                              "tuya aunque te quedes callado."),
                    zona="abajo", run_time=0.5)
        cifras = VGroup(
            tag_hud("establecer el circuito   %s ms"
                    % fmt(CONM["establecer_ms"], 0), font_size=19),
            tag_hud("enviar 1 Mb a 10 Mb/s    %s ms"
                    % fmt(CONM["tx_total_ms"], 0), font_size=19),
            tag_hud("total del circuito       %s ms"
                    % fmt(CONM["circuito_ms"], 1), font_size=21,
                    color=C_PAQUETE),
        ).arrange(DOWN, buff=0.20, aligned_edge=LEFT)
        cifras.move_to(DOWN * 2.05)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=1.5)
        self.wait(4.8)

        # --- momento: lo que NO cabe --------------------------------------
        rot.mostrar(pie_curso("Y si el enlace ya tiene sus circuitos "
                              "reservados, el siguiente no entra."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cifras), run_time=0.4)
        banco = cola(capacidad=CIRCUITOS_ENLACE, ocupacion=CIRCUITOS_ENLACE,
                     lado=0.46, color=C_RED, color_lleno=C_OK,
                     etiqueta="circuitos del enlace R1-R2")
        banco.move_to(DOWN * 1.95)
        self.play(FadeIn(banco), run_time=0.6)
        rechazo = VGroup(*[tag_hud("X", font_size=26, color=C_PERDIDA)
                           for _ in range(LLAMADAS_BLOQUEADAS)])
        rechazo.arrange(RIGHT, buff=0.30)
        rechazo.next_to(banco.marco, RIGHT, buff=0.42)
        et_rech = tag_hud("%d de %d llamadas rechazadas"
                          % (LLAMADAS_BLOQUEADAS, LLAMADAS_PEDIDAS),
                          font_size=19, color=C_PERDIDA)
        et_rech.next_to(banco, DOWN, buff=0.28)
        self.play(LaggedStart(*[FadeIn(r, scale=1.4) for r in rechazo],
                              lag_ratio=0.4), run_time=1.0)
        self.play(FadeIn(et_rech), run_time=0.4)
        self.wait(5.2)

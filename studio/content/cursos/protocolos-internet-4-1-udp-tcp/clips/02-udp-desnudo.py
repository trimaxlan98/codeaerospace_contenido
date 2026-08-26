class Clip2(Scene):
    """4.1.2 - UDP: ocho bytes de cabecera y ninguna promesa. Tres
    datagramas, uno se pierde, y ni el emisor ni el receptor se enteran
    (UDP ni siquiera numera). Sobrecosto medido frente a TCP. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("UDP desnudo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: ocho bytes y nada mas ---------------------------------
        rot.mostrar(pie_curso("UDP no promete nada. Ocho bytes de "
                              "cabecera, y ya esta."),
                    zona="abajo", run_time=0.5)
        cab = cabecera(CAMPOS_UDP, CAB_UDP_VAL, ancho=6.4, alto_fila=0.62,
                      fs=16)
        cab.move_to(UP * 1.85)
        self.play(FadeIn(cab), run_time=0.9)
        et_cab = tag_hud("8 bytes = 64 bits, cuatro campos",
                         font_size=19, color=C_CAPA)
        et_cab.next_to(cab, DOWN, buff=0.32)
        self.play(FadeIn(et_cab), run_time=0.5)
        self.wait(4.4)

        # --- momento: tres datagramas, sin apreton ---------------------------
        rot.mostrar(pie_curso("Manda tres datagramas seguidos. Sin "
                              "apreton previo, sin pedir permiso."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cab), FadeOut(et_cab), run_time=0.5)
        emisor = nodo("host", "emisor", 0.55)
        emisor.move_to(LEFT * 4.6)
        receptor = nodo("host", "receptor", 0.55)
        receptor.move_to(RIGHT * 4.6)
        enl = enlace(emisor.centro(), receptor.centro(), color=C_RED)
        self.play(FadeIn(emisor), FadeIn(receptor), Create(enl.linea),
                  run_time=0.8)

        fichas = [ficha(str(n), lado=0.44, color=C_PAQUETE)
                 for n in NUMEROS_ENVIADOS]
        recibidos = VGroup()
        for i, (n, tk) in enumerate(zip(NUMEROS_ENVIADOS, fichas)):
            tk.move_to(emisor.centro())
            self.play(FadeIn(tk, scale=1.2), run_time=0.25)
            if n == PERDIDO:
                self.play(tk.animate.move_to(enl.punto_en(0.5)),
                          run_time=0.7)
            else:
                self.play(MoveAlongPath(tk, enl.linea), run_time=0.9)
            if n == PERDIDO:
                break
            recibidos.add(tk)
            recibidos.arrange(RIGHT, buff=0.16)
            recibidos.next_to(receptor, DOWN, buff=0.55)
        self.wait(2.6)

        # --- momento: se pierde y nadie se entera ---------------------------
        rot.mostrar(pie_curso("El segundo se pierde. UDP ni siquiera "
                              "numera los datagramas: nadie tiene como "
                              "notar el hueco."),
                    zona="abajo", run_time=0.5)
        perdido_tk = fichas[NUMEROS_ENVIADOS.index(PERDIDO)]
        self.play(perdido_tk.animate.set_color(C_PERDIDA), run_time=0.35)
        self.play(perdido_tk.animate.shift(DOWN * 1.1).set_opacity(0.0),
                  run_time=0.7)
        # el tercero llega igual, sin que nadie haya pedido reenvio
        tk3 = fichas[NUMEROS_ENVIADOS.index(3)]
        tk3.move_to(emisor.centro())
        self.play(FadeIn(tk3, scale=1.2), run_time=0.25)
        self.play(MoveAlongPath(tk3, enl.linea), run_time=0.9)
        recibidos.add(tk3)
        recibidos.arrange(RIGHT, buff=0.16)
        recibidos.next_to(receptor, DOWN, buff=0.55)
        et_recibido = tag_hud("recibido en el receptor", font_size=15,
                              color=C_EJE)
        et_recibido.next_to(recibidos, DOWN, buff=0.16)
        self.play(FadeIn(et_recibido), run_time=0.4)
        self.wait(3.2)

        # --- momento: el precio de no prometer -------------------------------
        rot.mostrar(pie_curso("El ahorro se paga en garantias: ocho bytes "
                              "frente a los veinte de TCP, y una perdida "
                              "que no deja rastro."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(emisor), FadeOut(receptor), FadeOut(enl),
                  FadeOut(recibidos), FadeOut(et_recibido), run_time=0.6)
        cifras = VGroup(
            tag_hud("%d B de datos  ->  %d B con UDP  (%s %% de "
                    "cabeceras)" % (DATOS_EJEMPLO, ENC_UDP["total"],
                                    fmt(ENC_UDP["sobrecosto_pct"], 1)),
                    font_size=21),
            tag_hud("%d B de datos  ->  %d B con TCP  (%s %% de "
                    "cabeceras)" % (DATOS_EJEMPLO, ENC_TCP["total"],
                                    fmt(ENC_TCP["sobrecosto_pct"], 1)),
                    font_size=21, color=C_CAPA),
        ).arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        cifras.move_to(UP * 0.6)
        self.play(LaggedStart(*[FadeIn(c, shift=0.14 * UP) for c in cifras],
                              lag_ratio=0.4), run_time=1.4)
        self.wait(5.4)

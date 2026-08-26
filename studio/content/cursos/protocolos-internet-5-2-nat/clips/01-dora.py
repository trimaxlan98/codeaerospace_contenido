class Clip1(Scene):
    """5.2.1 - Los cuatro mensajes REALES de dhcp_dora(): DISCOVER, OFFER,
    REQUEST, ACK. El cliente arranca sin direccion (0.0.0.0 a
    255.255.255.255) y el ACK trae mucho mas que la IP. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("DORA")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los dos extremos, sin direccion todavia --------------
        rot.mostrar(pie_curso("Tu telefono llega a una red nueva. No tiene "
                              "direccion: la tiene que pedir."),
                    zona="abajo", run_time=0.5)
        esc = escalera(["cliente", "servidor"], EVENTOS_DORA, ancho=6.4,
                       alto=3.1, fs=16)
        esc.shift(UP * 0.55)
        self.play(FadeIn(esc.actores), Create(esc.vidas), run_time=1.0)
        self.wait(3.0)

        # --- momento: DISCOVER ---------------------------------------------
        rot.mostrar(pie_curso("Sin direccion propia, manda un DISCOVER "
                              "desde 0.0.0.0 a todos: 255.255.255.255."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esc.paso(0)), run_time=0.7)
        et_bcast = tag_hud("origen 0.0.0.0   destino 255.255.255.255",
                           font_size=18, color=C_CIFRA)
        et_bcast.move_to(DOWN * 2.35)
        self.play(FadeIn(et_bcast), run_time=0.4)
        self.wait(3.6)

        # --- momento: OFFER ---------------------------------------------
        rot.mostrar(pie_curso("El servidor DHCP contesta con una oferta: "
                              "%s." % DORA["ip"]),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_bcast), run_time=0.3)
        self.play(Create(esc.paso(1)), run_time=0.7)
        self.wait(3.4)

        # --- momento: REQUEST ---------------------------------------------
        rot.mostrar(pie_curso("El cliente confirma que la acepta, otra vez "
                              "a todos: por si hay mas de un servidor."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esc.paso(2)), run_time=0.7)
        et_bcast2 = tag_hud("origen 0.0.0.0   destino 255.255.255.255",
                            font_size=18, color=C_CIFRA)
        et_bcast2.move_to(DOWN * 2.35)
        self.play(FadeIn(et_bcast2), run_time=0.4)
        self.wait(3.4)

        # --- momento: ACK con todo lo que hace falta ------------------------
        rot.mostrar(pie_curso("El ACK no trae solo la IP: trae mascara, "
                              "puerta de enlace y DNS. Todo lo necesario.",
                              font_size=23),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_bcast2), run_time=0.3)
        self.play(Create(esc.paso(3)), run_time=0.7)
        cifras = VGroup(
            tag_hud("IP %s   mascara %s" % (DORA["ip"], DORA["mascara"]),
                    font_size=19),
            tag_hud("puerta %s   DNS %s   arriendo %d h"
                    % (DORA["puerta"], DORA["dns"], DORA["arriendo_h"]),
                    font_size=19, color=C_CIFRA),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras.move_to(DOWN * 1.95)
        self.play(LaggedStart(*[FadeIn(c, shift=0.10 * UP) for c in cifras],
                              lag_ratio=0.3), run_time=1.0)
        self.wait(6.0)

class Clip1(Scene):
    """4.2.1 - Los tres mensajes del apreton (handshake_tcp real): SYN,
    SYN-ACK, ACK, y solo entonces el primer byte util. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Los tres mensajes")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los dos extremos, todavia sin hablarse --------------
        rot.mostrar(pie_curso("Antes de mandar el primer byte util, "
                              "cliente y servidor se ponen de acuerdo."),
                    zona="abajo", run_time=0.5)
        esc = escalera(["cliente", "servidor"], EVENTOS_HS, ancho=5.6,
                       alto=3.4, fs=17)
        self.play(FadeIn(esc.actores), Create(esc.vidas), run_time=1.0)
        self.wait(2.6)

        def estado(c, s):
            col_c = C_OK if c == "ESTABLISHED" else C_RED
            col_s = C_OK if s == "ESTABLISHED" else C_RED
            g = VGroup(tag_hud("cliente: %s" % c, font_size=18, color=col_c),
                      tag_hud("servidor: %s" % s, font_size=18, color=col_s)
                      ).arrange(RIGHT, buff=0.6)
            g.move_to(DOWN * 1.95)
            return g

        panel = VGroup()

        # --- momento: SYN ---------------------------------------------------
        rot.mostrar(pie_curso("El cliente abre con SYN: propone un numero "
                              "de secuencia inicial."),
                    zona="abajo", run_time=0.5)
        e0 = EVENTOS_HS[0]
        self.play(Create(esc.paso(0)), run_time=0.7)
        nuevo = estado(e0["estado_c"], e0["estado_s"])
        self.play(FadeIn(nuevo), run_time=0.4)
        panel = nuevo
        self.wait(3.6)

        # --- momento: SYN-ACK -------------------------------------------
        rot.mostrar(pie_curso("El servidor confirma ese numero y propone "
                              "el suyo: ack es tu numero mas uno."),
                    zona="abajo", run_time=0.5)
        e1 = EVENTOS_HS[1]
        self.play(Create(esc.paso(1)), run_time=0.7)
        nuevo = estado(e1["estado_c"], e1["estado_s"])
        self.play(FadeOut(panel), FadeIn(nuevo), run_time=0.4)
        panel = nuevo
        self.wait(3.8)

        # --- momento: ACK -------------------------------------------------
        rot.mostrar(pie_curso("El cliente confirma el numero del servidor: "
                              "para el, la conexion ya esta establecida."),
                    zona="abajo", run_time=0.5)
        e2 = EVENTOS_HS[2]
        self.play(Create(esc.paso(2)), run_time=0.7)
        nuevo = estado(e2["estado_c"], e2["estado_s"])
        self.play(FadeOut(panel), FadeIn(nuevo), run_time=0.4)
        panel = nuevo
        self.wait(3.8)

        # --- momento: el primer byte util -----------------------------
        rot.mostrar(pie_curso("Recien ahi, %s ms despues del primer SYN, "
                              "viaja el primer byte util."
                              % fmt(ANTES_PRIMER_BYTE, 0)),
                    zona="abajo", run_time=0.5)
        e3 = EVENTOS_HS[3]
        self.play(Create(esc.paso(3)), run_time=0.7)
        nuevo = estado(e3["estado_c"], e3["estado_s"])
        self.play(FadeOut(panel), FadeIn(nuevo), run_time=0.4)
        panel = nuevo
        cifra = tag_hud("%s ms antes del primer byte util  (RTT = %s ms)"
                        % (fmt(ANTES_PRIMER_BYTE, 0), fmt(RTT_HS, 0)),
                        font_size=19, color=C_CIFRA)
        cifra.move_to(DOWN * 2.55)
        self.play(FadeIn(cifra), run_time=0.5)
        self.wait(5.0)

class Clip4(Scene):
    """1.2.4 - En el destino los sobres se abren en orden inverso: Ethernet,
    IP, TCP, hasta el dato original, byte por byte igual al de partida.
    Cierre de la leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Desencapsular")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el sobre completo, tal como llego --------------------
        rot.mostrar(pie_curso("En el destino todo se hace al reves: los "
                              "sobres se abren del mas externo al mas "
                              "interno."),
                    zona="abajo", run_time=0.5)
        n = 4
        p = pila(datos=DATOS_CHICO, encapsulado=n, ancho=4.4)
        p.shift(LEFT * 0.3)
        self.play(FadeIn(p), run_time=0.8)
        et_llega = tag_hud("llega por el cable: %d B" % ENC_CHICO["total"],
                           font_size=18, color=C_PAQUETE)
        et_llega.next_to(p, DOWN, buff=0.45)
        self.play(FadeIn(et_llega), run_time=0.4)
        self.wait(4.4)

        # --- momento: Ethernet, IP, TCP, y lo que queda ---------------------
        rot.mostrar(pie_curso("Primero se abre Ethernet, luego IP, luego "
                              "TCP: cada capa entrega lo que traia a la "
                              "de arriba."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_llega), run_time=0.3)
        for k in range(n - 1, -1, -1):
            nueva = p.con_encapsulado(k)
            self.play(Transform(p, nueva), run_time=0.55)
            self.wait(1.0)
        self.wait(1.0)

        # --- momento: el mismo dato, byte por byte --------------------------
        rot.mostrar(pie_curso("Lo que llega es exactamente lo que salio: "
                              "el mismo dato, byte por byte."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(p), run_time=0.5)
        enviado = paquete([("enviado", 1.0, "%d B" % DATOS_CHICO)],
                          ancho=2.2, alto=0.62, color=C_PAQUETE)
        recibido = paquete([("recibido", 1.0, "%d B" % DATOS_CHICO)],
                           ancho=2.2, alto=0.62, color=C_OK)
        enviado.move_to(LEFT * 1.6)
        recibido.move_to(RIGHT * 1.6)
        self.play(FadeIn(enviado), run_time=0.6)
        self.play(FadeIn(recibido), run_time=0.6)
        ok = tag_hud("=", font_size=30, color=C_OK)
        ok.move_to((enviado.get_center() + recibido.get_center()) / 2)
        self.play(FadeIn(ok, scale=1.4), run_time=0.4)
        self.wait(5.4)

        # --- cierre de la leccion -------------------------------------------
        cierre_leccion(
            self, rot,
            "Nadie entiende la red entera.",
            "Cada capa entiende su propio sobre.",
            "Siguiente: el vecindario, Ethernet y MAC.",
            enviado, recibido, ok, espera=4.8)

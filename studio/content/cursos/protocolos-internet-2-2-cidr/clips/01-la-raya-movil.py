class Clip1(Scene):
    """2.2.1 - Una direccion IP son dos numeros pegados: red y host. La
    mascara traza la raya; moverla dos casillas crea una subred mas chica
    y recalcula, en vivo, cuantas maquinas caben. (~29 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La raya movil")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- momento: la direccion son dos numeros pegados ----------------
        rot.mostrar(pie_curso("Una direccion IP no es un numero: son dos, "
                              "pegados. Red y host."),
                    zona="abajo", run_time=0.5)
        barra = barra_bits(DIR_BASE, 24)
        barra.move_to(UP * 0.95)
        self.play(FadeIn(barra), run_time=0.9)
        self.wait(6.0)

        # --- momento: la mascara /24 recontada ------------------------------
        rot.mostrar(pie_curso("La mascara /24 traza la raya en el bit 24: "
                              "quedan 254 direcciones para maquinas."),
                    zona="abajo", run_time=0.5)
        cifras24 = VGroup(
            tag_hud("mascara   %s" % CIDR_24["mascara"], font_size=19),
            tag_hud("rango     %s - %s"
                    % (CIDR_24["primero"], CIDR_24["ultimo"]), font_size=19),
            tag_hud("hosts     %d" % CIDR_24["hosts"], font_size=19,
                    color=C_CIFRA),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras24.next_to(barra, DOWN, buff=0.95)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP)
                                for c in cifras24], lag_ratio=0.3),
                  run_time=1.2)
        self.wait(5.5)

        # --- momento: el gesto - mover la raya -----------------------------
        rot.mostrar(pie_curso("Mover la raya dos casillas a la derecha "
                              "crea una subred mas chica."),
                    zona="abajo", run_time=0.5)
        barra26 = barra.con_prefijo(26)
        self.play(FadeOut(cifras24), run_time=0.4)
        self.play(Transform(barra, barra26), run_time=1.6)
        self.wait(1.0)

        # --- momento: recontar sobre la nueva raya -------------------------
        rot.mostrar(pie_curso("Menos bits libres, menos maquinas: de 254 "
                              "a 62 hosts, mascara 255.255.255.192."),
                    zona="abajo", run_time=0.5)
        cifras26 = VGroup(
            tag_hud("mascara   %s" % CIDR_26["mascara"], font_size=19),
            tag_hud("rango     %s - %s"
                    % (CIDR_26["primero"], CIDR_26["ultimo"]), font_size=19),
            tag_hud("hosts     %d" % CIDR_26["hosts"], font_size=19,
                    color=C_CIFRA),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras26.next_to(barra, DOWN, buff=0.95)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP)
                                for c in cifras26], lag_ratio=0.3),
                  run_time=1.2)
        self.wait(7.5)

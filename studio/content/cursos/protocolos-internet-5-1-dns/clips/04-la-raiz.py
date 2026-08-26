class Clip4(Scene):
    """5.1.4 - La raiz: 13 identidades publicadas que en realidad son
    cientos de maquinas por anycast (7.1), y que pasa cuando el DNS falla
    aunque la red funcione. Cierre de la leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La raiz")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: 13 identidades, dato publico -------------------------
        rot.mostrar(pie_curso("La raiz del DNS no es un servidor: son "
                              "trece identidades publicadas (dato "
                              "publico)."),
                    zona="abajo", run_time=0.5)
        rejilla = VGroup(*[ficha(letra, lado=0.58, fs=17, color=C_TENUE)
                          for letra in RAIZ_LETRAS])
        rejilla.arrange_in_grid(rows=2, buff=0.22)
        rejilla.move_to(UP * 0.55)
        self.play(LaggedStart(*[FadeIn(f, scale=1.2) for f in rejilla],
                              lag_ratio=0.06), run_time=1.4)
        self.wait(3.8)

        # --- momento: cada identidad son cientos de maquinas ----------------
        rot.mostrar(pie_curso("Cada identidad son, en realidad, cientos de "
                              "maquinas repartidas por el mundo: anycast, "
                              "el tema de la 7.1."),
                    zona="abajo", run_time=0.5)
        resto = VGroup(*rejilla[1:])
        sola = rejilla[0]
        self.play(FadeOut(resto), run_time=0.5)
        self.play(sola.animate.move_to(UP * 0.55).scale(1.35), run_time=0.6)
        n_copias = 8
        angulos = [i * TAU / n_copias for i in range(n_copias)]
        copias = VGroup(*[sola.copy().scale(0.42).set_opacity(0.55)
                          for _ in angulos])
        for c in copias:
            c.move_to(sola.get_center())
        centro = sola.get_center()
        objetivos = [centro + np.array([1.7 * math.cos(a),
                                        0.62 * math.sin(a), 0.0])
                    for a in angulos]
        self.play(LaggedStart(*[c.animate.move_to(t)
                               for c, t in zip(copias, objetivos)],
                              lag_ratio=0.08), run_time=1.3)
        self.wait(4.0)

        # --- momento: la red funciona, el nombre no ------------------------
        rot.mostrar(pie_curso("La red entrega el paquete si tiene la IP: "
                              "el problema es no saber cual."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(sola), FadeOut(copias), run_time=0.5)
        ok = tag_hud("red: funciona   (ping a la IP: %s ms)"
                    % fmt(PING_IP_MS, 0), font_size=21, color=C_OK)
        mal = tag_hud("nombre: no resuelve", font_size=21, color=C_PERDIDA)
        estado = VGroup(ok, mal).arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        estado.move_to(UP * 0.4)
        self.play(FadeIn(ok, shift=0.12 * UP), run_time=0.5)
        self.wait(1.2)
        self.play(FadeIn(mal, shift=0.12 * UP), run_time=0.5)
        self.wait(4.4)

        # --- cierre de la leccion -------------------------------------------
        cierre_leccion(
            self, rot,
            "La red enruta numeros.",
            "Los nombres son un servicio que alguien sostiene.",
            "Siguiente: DHCP y NAT.",
            estado, espera=4.8)

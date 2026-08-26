class Clip2(Scene):
    """1.2.2 - El dato baja por la pila y cada capa le pega su propia
    cabecera: HTTP, TCP, IP, Ethernet, con los bytes REALES sumandose en
    el contador. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Encapsular: el sobre dentro del sobre")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el dato desnudo ---------------------------------------
        rot.mostrar(pie_curso("El dato no cambia. Cada capa le agrega su "
                              "propio sobre: una cabecera con su nombre."),
                    zona="abajo", run_time=0.5)
        p = pila(datos=DATOS_CHICO, encapsulado=0, ancho=4.4)
        p.shift(LEFT * 0.3)
        self.play(FadeIn(p), run_time=0.8)
        et_carga = tag_hud("carga util: %d B" % DATOS_CHICO, font_size=18,
                           color=C_PAQUETE)
        et_carga.next_to(p, DOWN, buff=0.45)
        self.play(FadeIn(et_carga), run_time=0.4)
        self.wait(6.0)

        # --- momento: HTTP -> TCP -> IP -> Ethernet -------------------------
        rot.mostrar(pie_curso("HTTP baja a TCP, TCP baja a IP, IP baja a "
                              "Ethernet: cada una pega su cabecera y el "
                              "contador crece."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_carga), run_time=0.3)
        for k in range(1, len(p.capas) + 1):
            nueva = p.con_encapsulado(k)
            self.play(Transform(p, nueva), run_time=0.55)
            self.wait(1.0)
        self.wait(1.2)

        # --- momento: el sobrecosto medido -----------------------------------
        rot.mostrar(pie_curso("Con datos chicos el sobre pesa mas que la "
                              "carta: cien bytes cuestan ciento "
                              "cincuenta y ocho en el cable."),
                    zona="abajo", run_time=0.5)
        cifras = VGroup(
            tag_hud("%d B de datos  ->  %d B en el cable  (%s %% de "
                    "sobrecosto)"
                    % (DATOS_CHICO, ENC_CHICO["total"],
                       fmt(ENC_CHICO["sobrecosto_pct"], 1)),
                    font_size=20),
            tag_hud("%d B de datos  ->  %d B en el cable  (%s %% de "
                    "sobrecosto)"
                    % (DATOS_GRANDE, ENC_GRANDE["total"],
                       fmt(ENC_GRANDE["sobrecosto_pct"], 1)),
                    font_size=20),
        ).arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        cifras.next_to(p, DOWN, buff=0.45)
        self.play(LaggedStart(*[FadeIn(c, shift=0.14 * UP) for c in cifras],
                              lag_ratio=0.4), run_time=1.4)
        self.wait(10.5)

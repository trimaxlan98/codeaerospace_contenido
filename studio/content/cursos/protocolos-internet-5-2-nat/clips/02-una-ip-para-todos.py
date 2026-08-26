class Clip2(Scene):
    """5.2.2 - Ocho aparatos, una sola direccion publica. Las privadas de
    RFC 1918 (es_privada() manda) no salen de casa: fuera de la puerta no
    existen. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Una IP para todos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la casa y el router ------------------------------
        rot.mostrar(pie_curso("En casa hay un router y muchos aparatos, "
                              "pero solo una direccion los representa "
                              "afuera.", font_size=23),
                    zona="abajo", run_time=0.5)
        hosts = VGroup(*[nodo("host", None, 0.30) for _ in range(
            N_APARATOS)])
        hosts.arrange_in_grid(rows=2, cols=4, buff=0.55)
        hosts.move_to(LEFT * 4.6 + UP * 0.30)
        router = nodo("router", "router", 0.55)
        router.move_to(LEFT * 0.4 + UP * 0.30)
        nube = nodo("nube", "Internet", 0.62)
        nube.move_to(RIGHT * 4.3 + UP * 0.30)
        lineas = VGroup(*[Line(h.centro(), router.centro(),
                               stroke_color=C_RED, stroke_width=1.3,
                               stroke_opacity=0.55) for h in hosts])
        enlace_ext = enlace(router.centro(), nube.centro())
        self.play(FadeIn(hosts), Create(lineas), run_time=1.1)
        self.play(FadeIn(router), Create(enlace_ext.linea), FadeIn(nube),
                  run_time=0.9)
        et_pub = tag_hud("IP publica  %s" % NAT_IP_PUBLICA, font_size=19,
                         color=C_CIFRA)
        et_pub.next_to(nube, DOWN, buff=0.30)
        self.play(FadeIn(et_pub), run_time=0.4)
        self.wait(3.4)

        # --- momento: cada aparato con la suya, puertas adentro -----------
        rot.mostrar(pie_curso("Puertas adentro cada uno tiene la suya: "
                              "%s, %s..." % (IP_LAPTOP, IP_TELEFONO),
                              font_size=23),
                    zona="abajo", run_time=0.5)
        et_a = tag_hud(IP_LAPTOP, font_size=13, color=C_CIFRA)
        et_a.next_to(hosts[4], DOWN, buff=0.12)
        et_b = tag_hud(IP_TELEFONO, font_size=13, color=C_CIFRA)
        et_b.next_to(hosts[7], DOWN, buff=0.12)
        et_n = tag_hud("%d aparatos  ->  1 direccion publica" % N_APARATOS,
                       font_size=19, color=C_CIFRA)
        et_n.move_to(DOWN * 1.65)
        self.play(FadeIn(et_a), FadeIn(et_b), run_time=0.5)
        self.play(FadeIn(et_n), run_time=0.4)
        self.wait(4.6)

        # --- momento: las tres franjas reservadas ------------------------
        rot.mostrar(pie_curso("Esas direcciones viven en tres franjas "
                              "reservadas, el RFC 1918."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(hosts, router, nube, lineas,
                                 enlace_ext.linea, et_pub, et_a, et_b,
                                 et_n)), run_time=0.6)
        tab = tabla(["Rango", "Mascara", "Direcciones"], RFC1918_FILAS,
                   anchos=[3.6, 2.6, 3.8], alto=0.55, fs=18)
        tab.move_to(UP * 0.55)
        self.play(FadeIn(tab), run_time=0.9)
        self.wait(4.3)

        # --- momento: es_privada(), la pregunta que decide -----------------
        rot.mostrar(pie_curso("La misma pregunta para cuatro direcciones: "
                              "es_privada?"),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(tab), run_time=0.5)
        filas_priv = VGroup()
        for ip, priv in PRIVADAS:
            veredicto = tag_hud("NO RUTEABLE" if priv else "RUTEABLE",
                                font_size=18,
                                color=C_PERDIDA if priv else C_OK)
            fila = VGroup(tag_hud(ip, font_size=20), veredicto).arrange(
                RIGHT, buff=0.55)
            filas_priv.add(fila)
        filas_priv.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        filas_priv.move_to(UP * 0.15)
        self.play(LaggedStart(*[FadeIn(f, shift=0.10 * UP)
                               for f in filas_priv], lag_ratio=0.3),
                  run_time=1.4)
        self.wait(6.5)

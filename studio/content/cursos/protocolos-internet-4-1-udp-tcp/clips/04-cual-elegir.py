class Clip4(Scene):
    """4.1.4 - Cual elegir: la tabla con cifras REALES (cabecera, viajes
    antes del primer byte, comportamiento ante la perdida) y tres casos de
    uso. Cierre de la leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Cual elegir")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la tabla, con numeros ----------------------------------
        rot.mostrar(pie_curso("Repasemos con numeros, no con adjetivos, "
                              "lo que cuesta cada promesa."),
                    zona="abajo", run_time=0.5)
        tab = tabla(["Criterio", "UDP", "TCP"], FILAS_TABLA,
                   anchos=[3.6, 2.7, 3.9], alto=0.62, fs=16,
                   color_cab=C_CAPA)
        tab.move_to(UP * 1.55)
        self.play(FadeIn(tab), run_time=1.0)
        self.wait(4.6)

        # --- momento: el viaje antes del primer byte --------------------------
        rot.mostrar(pie_curso("Antes del primer byte util, TCP paga un "
                              "viaje completo (el detalle es la proxima "
                              "leccion). UDP no paga ninguno."),
                    zona="abajo", run_time=0.5)
        eventos_tcp = [{"de": e["de"], "a": e["a"], "texto": e["flags"],
                       "t_ms": e["t_ms"]} for e in HS["eventos"][:3]]
        esc = escalera(["cliente", "servidor"], eventos_tcp, ancho=2.6,
                      alto=1.4, fs=11, color=C_EJE, color_msg=C_CAPA)
        esc.move_to(DOWN * 1.35 + RIGHT * 2.5)
        et_esc = tag_hud("TCP: el apreton completo", font_size=15,
                         color=C_CAPA)
        et_esc.next_to(esc, UP, buff=0.30)
        tcp_ms = tag_hud("primer byte util: %d ms mas tarde"
                         % ANTES_PRIMER_BYTE_TCP, font_size=17,
                         color=C_CIFRA)
        tcp_ms.next_to(esc, DOWN, buff=0.28)
        self.play(FadeIn(esc), FadeIn(et_esc), run_time=0.8)
        self.play(FadeIn(tcp_ms), run_time=0.4)

        udp_ms = tag_hud("UDP: primer byte util, 0 ms", font_size=18,
                         color=C_CIFRA)
        udp_ms.move_to(DOWN * 1.35 + LEFT * 3.3)
        self.play(FadeIn(udp_ms, shift=0.1 * UP), run_time=0.5)
        self.wait(4.2)

        # --- momento: ante la perdida -----------------------------------------
        rot.mostrar(pie_curso("Y si algo se pierde: UDP sigue como si "
                              "nada. TCP se da cuenta y lo arregla."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(esc), FadeOut(et_esc), FadeOut(tcp_ms),
                  FadeOut(udp_ms), run_time=0.5)
        recap = VGroup(
            tag_hud("UDP  ->  sigue mandando, nadie se entera",
                    font_size=20, color=C_PERDIDA),
            tag_hud("TCP  ->  detecta el hueco y lo rellena",
                    font_size=20, color=C_OK),
        ).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        recap.move_to(DOWN * 1.7)
        self.play(LaggedStart(*[FadeIn(r, shift=0.12 * UP) for r in recap],
                              lag_ratio=0.4), run_time=1.0)
        self.wait(3.4)

        # --- momento: tres casos reales -----------------------------------------
        rot.mostrar(pie_curso("La eleccion no es cual protocolo es "
                              "mejor. Es que promesa necesita tu dato."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(tab), FadeOut(recap), run_time=0.5)
        casos = VGroup()
        for texto, cual in CASOS_USO:
            col = C_PAQUETE if cual == "UDP" else C_CAPA
            fila = VGroup(
                tag_hud(texto, font_size=18, color=C_EJE),
                tag_hud("-> %s" % cual, font_size=19, color=col),
            ).arrange(RIGHT, buff=0.30)
            casos.add(fila)
        casos.arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        casos.move_to(UP * 0.35)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in casos],
                              lag_ratio=0.35), run_time=1.4)
        self.wait(4.6)

        # --- cierre de la leccion ---------------------------------------------
        cierre_leccion(
            self, rot,
            "No hay un protocolo mejor.",
            "Hay una promesa que quieres o no.",
            "Siguiente: el apreton y la ventana.",
            casos, espera=4.8)

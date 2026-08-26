class Clip1(Scene):
    """1.3.1 - La trama Ethernet y su sello: el FCS es el CRC-32 de todo lo
    anterior. Se voltea un bit, el CRC recalculado ya no coincide y la
    trama se descarta. Cifras REALES de `trama_ethernet`. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La trama y su sello")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la trama con sus campos -----------------------------
        rot.mostrar(pie_curso("En el cable de tu casa el mensaje no viaja "
                              "suelto: viaja dentro de una trama."),
                    zona="abajo", run_time=0.5)
        pk = trama_pieza()
        pk.move_to(UP * 0.80)
        self.play(FadeIn(pk), run_time=1.0)
        et_tam = tag_hud("%d bytes en el cable:  14 de cabecera  +  %d de "
                         "carga  +  %d de relleno"
                         % (TRAMA_BYTES, len(CARGA_TRAMA), TRAMA_RELLENO),
                         font_size=19, color=C_EJE)
        et_tam.next_to(pk, DOWN, buff=0.52)
        self.play(FadeIn(et_tam), run_time=0.4)
        self.wait(4.2)

        # --- momento: el sello ---------------------------------------------
        rot.mostrar(pie_curso("El ultimo campo es un sello: el CRC-32 de "
                              "todo lo que va delante."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(pk.campo("FCS"), color=C_CIFRA,
                           scale_factor=1.12), run_time=0.7)
        et_crc = tag_hud("FCS  =  CRC-32( los %d bytes )  =  %s"
                         % (TRAMA_BYTES, FCS_OK), font_size=22)
        et_crc.next_to(et_tam, DOWN, buff=0.42)
        self.play(FadeIn(et_crc, shift=0.12 * UP), run_time=0.5)
        self.wait(4.6)

        # --- momento: un bit se voltea -------------------------------------
        rot.mostrar(pie_curso("Basta con que el cable voltee UN bit. El 97, "
                              "que cae dentro del tipo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_tam), FadeOut(et_crc), run_time=0.4)
        rota = pk.con_valores({"Tipo": TIPO_ROTO})
        rota.iluminar("FCS", C_CIFRA)
        rota.iluminar("Tipo", C_PERDIDA)
        et_bit = tag_hud("bit %d  ->  byte %d:   08  ->  48"
                         % (BIT_ROTO, BYTE_ROTO), font_size=21,
                         color=C_PERDIDA)
        et_bit.next_to(pk, DOWN, buff=0.52)
        self.play(Succession(Transform(pk, rota, run_time=0.45), Wait(0.15)))
        self.play(FadeIn(et_bit), run_time=0.4)
        self.wait(4.4)

        # --- momento: el CRC no cuadra y la trama se tira ------------------
        rot.mostrar(pie_curso("El que recibe recalcula el CRC y compara. "
                              "Los dos numeros no son el mismo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_bit), run_time=0.3)
        comparacion = VGroup(
            tag_hud("FCS que viajaba      %s" % FCS_OK, font_size=23,
                    color=C_CIFRA),
            tag_hud("CRC-32 recalculado   %s" % FCS_ROTO, font_size=23,
                    color=C_PERDIDA),
        ).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        comparacion.move_to(DOWN * 1.10)
        self.play(FadeIn(comparacion[0], shift=0.12 * UP), run_time=0.5)
        self.play(FadeIn(comparacion[1], shift=0.12 * UP), run_time=0.5)
        veredicto = tag_hud("no coinciden  ->  trama descartada",
                            font_size=24, color=C_PERDIDA)
        veredicto.next_to(comparacion, DOWN, buff=0.36)
        self.play(FadeIn(veredicto), run_time=0.4)
        self.play(pk.animate.set_color(C_PERDIDA), run_time=0.5)
        self.play(pk.animate.shift(UP * 0.50).set_opacity(0.0), run_time=0.9)
        self.wait(4.8)

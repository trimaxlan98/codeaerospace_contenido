class Clip3(Scene):
    """2.3.3 - SLAAC: el router solo anuncia el prefijo /64. La maquina
    deriva el resto de su propia MAC con EUI-64 (relleno ff:fe en medio,
    bit universal/local invertido) y se autoconfigura sin pedirle nada a
    nadie. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La direccion que se pone sola")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el router solo anuncia el prefijo ----------------------
        rot.mostrar(pie_curso("El router no asigna nada: solo anuncia el "
                              "prefijo de la red."),
                    zona="abajo", run_time=0.5)
        r = nodo("router", "R1", tam=0.6, color=C_RED)
        h = nodo("host", "PC", tam=0.6, color=C_RED)
        r.move_to(LEFT * 3.6 + UP * 0.9)
        h.move_to(RIGHT * 3.6 + UP * 0.9)
        e = enlace(r.centro(), h.centro(), color=C_RED)
        self.play(FadeIn(r), FadeIn(h), FadeIn(e), run_time=0.6)
        anuncio = tag_hud("%s::/64" % PREFIJO_SLAAC, font_size=20,
                          color=C_RED)
        anuncio.move_to(r.centro())
        self.play(FadeIn(anuncio), run_time=0.4)
        self.play(anuncio.animate.move_to(h.centro() + UP * 0.55),
                  run_time=1.4)
        self.wait(3.4)

        # --- momento: la maquina ya sabe su MAC --------------------------
        rot.mostrar(pie_curso("La maquina ya tiene una identidad: su MAC, "
                              "%s." % MAC_EJEMPLO),
                    zona="abajo", run_time=0.5)
        cajas_mac = VGroup(*[
            VGroup(Rectangle(width=0.62, height=0.5, stroke_color=C_PAQUETE,
                             stroke_width=2.0, fill_color=C_PAQUETE,
                             fill_opacity=0.12),
                   tag_hud(b, font_size=15, color=C_PAQUETE))
            for b in MAC_BYTES])
        for c in cajas_mac:
            c[1].move_to(c[0].get_center())
        cajas_mac.arrange(RIGHT, buff=0.10)
        cajas_mac.move_to(DOWN * 0.6)
        self.play(FadeOut(anuncio),
                  LaggedStart(*[FadeIn(c, shift=0.1 * UP)
                               for c in cajas_mac], lag_ratio=0.2),
                  run_time=1.2)
        self.wait(3.2)

        # --- momento: EUI-64 rellena y voltea el bit ----------------------
        rot.mostrar(pie_curso("EUI-64 mete ff:fe en medio, e invierte el "
                              "bit universal/local: %s."
                              % EUI["bit_invertido"]),
                    zona="abajo", run_time=0.5)
        relleno = VGroup(*[
            VGroup(Rectangle(width=0.62, height=0.5, stroke_color=C_CIFRA,
                             stroke_width=2.0, fill_color=C_CIFRA,
                             fill_opacity=0.16),
                   tag_hud(b, font_size=15, color=C_CIFRA))
            for b in ("ff", "fe")])
        for c in relleno:
            c[1].move_to(c[0].get_center())
        relleno.arrange(RIGHT, buff=0.10)
        mitad_izq = VGroup(*cajas_mac[:3])
        mitad_der = VGroup(*cajas_mac[3:])
        centro_original = cajas_mac.get_center()
        self.play(mitad_izq.animate.shift(LEFT * 0.76),
                  mitad_der.animate.shift(RIGHT * 0.76), run_time=1.0)
        relleno.move_to(centro_original)
        self.play(FadeIn(relleno, shift=0.15 * UP), run_time=0.8)
        primero = cajas_mac[0]
        marco = SurroundingRectangle(primero, color=C_CIFRA, buff=0.04)
        nuevo = tag_hud("a8", font_size=15, color=C_CIFRA)
        nuevo.move_to(primero[1].get_center())
        self.play(Create(marco), run_time=0.5)
        self.play(FadeOut(primero[1]), FadeIn(nuevo), run_time=0.5)
        self.wait(3.4)

        # --- momento: la direccion completa -------------------------------
        rot.mostrar(pie_curso("El prefijo del router y la interfaz de la "
                              "MAC: la direccion completa, sola."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(marco), FadeOut(nuevo), FadeOut(relleno),
                  FadeOut(cajas_mac), FadeOut(r), FadeOut(h), FadeOut(e),
                  run_time=0.6)
        barra = barra_bits(valor=DIR6_SLAAC_BIN, prefijo=64, bits=128,
                           ancho=10.0, alto=0.34, color_red=C_RED,
                           color_host=C_CIFRA, mostrar_texto=False)
        barra.move_to(UP * 0.5)
        etq_red = tag_junto(barra.parte_red(), "prefijo del router",
                            direccion=UP, font_size=15, color=C_RED)
        etq_host = tag_junto(barra.parte_host(), "interfaz (de la MAC)",
                             direccion=DOWN, font_size=15, color=C_CIFRA)
        direccion = tag_hud(EUI["direccion"], font_size=24, color=C_CIFRA)
        direccion.next_to(etq_host, DOWN, buff=0.35)
        self.play(FadeIn(barra), FadeIn(etq_red), FadeIn(etq_host),
                  run_time=1.0)
        self.play(FadeIn(direccion, shift=0.15 * UP), run_time=0.7)
        self.wait(7.0)

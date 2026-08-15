class Clip4(Scene):
    """3.1.4 - Los decibelios que cobra el cable: ni la mejor linea es
    gratis. La atenuacion crece con la raiz de la frecuencia (efecto
    piel) — y a los gigahercios de un satelite el cable ya no sirve.
    Por eso el LNB amplifica ANTES de cablear. Cierra la leccion.
    (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Los decibelios que cobra el cable")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: ni el cable perfecto es gratis --------------------------
        rot.mostrar(pie_curso("Ni el cable mejor adaptado es gratis: "
                              "tambien cobra, en decibelios."),
                    zona="abajo", run_time=0.5)
        curva = haz_curvas([lambda f: atenuacion_rg6(f)], (10.0, 3000.0),
                           [C_CALCULO], ancho=6.6, alto=2.9, log_x=True,
                           etiqueta_x="frecuencia (MHz)",
                           etiqueta_y="dB / 100 m")
        curva.move_to(DOWN * 0.35)
        self.play(FadeIn(curva.ejes), run_time=0.6)
        self.play(Create(curva.curva(0)), run_time=1.6)
        self.wait(3.4)

        # --- momento: 100 MHz -------------------------------------------------
        rot.mostrar(pie_curso("A cien megahercios, un coaxial domestico "
                              "pierde seis decibelios cada cien metros."),
                    zona="abajo", run_time=0.5)
        p100 = Dot(curva.punto_de(0, 100.0), radius=0.07, color=C_E)
        tag100 = tag_hud(f"{ATEN_100M:.1f} dB/100m a 100 MHz",
                         font_size=15, color=C_E)
        tag100.next_to(p100, UR, buff=0.14)
        self.play(FadeIn(p100, scale=1.6), FadeIn(tag100, shift=0.1 * UP),
                  run_time=0.6)
        self.wait(4.4)

        # --- momento: 1 GHz -----------------------------------------------------
        rot.mostrar(pie_curso("Sube a un gigahercio y la perdida se "
                              "multiplica casi por tres."), zona="abajo",
                    run_time=0.5)
        p1g = Dot(curva.punto_de(0, 1000.0), radius=0.07, color=C_CALCULO)
        tag1g = tag_hud(f"{ATEN_1G:.1f} dB/100m a 1 GHz", font_size=15)
        tag1g.next_to(p1g, UR, buff=0.14)
        self.play(FadeIn(p1g, scale=1.6), FadeIn(tag1g, shift=0.1 * UP),
                  run_time=0.6)
        self.wait(4.4)

        # --- momento: los 12 GHz del satelite, fuera de escala -------------------
        rot.mostrar(pie_curso("Y a los doce gigahercios de un satelite, "
                              "el cable es sencillamente intransitable."),
                    zona="abajo", run_time=0.5)
        borde = curva.punto_de(0, 3000.0)
        flecha_fuera = Arrow(borde, borde + UP * 0.45 + RIGHT * 0.35,
                             buff=0.05, color=C_CARGA, stroke_width=4.0,
                             tip_length=0.16)
        tag_sat = tag_hud(f"12 GHz -> {ATEN_SAT:.0f} dB/100m "
                          "(fuera de escala)", font_size=15,
                          color=C_CARGA)
        tag_sat.next_to(flecha_fuera, UP, buff=0.12)
        if tag_sat.get_right()[0] > config.frame_width / 2 - 0.4:
            tag_sat.align_to(flecha_fuera.get_end(), RIGHT)
        self.play(GrowArrow(flecha_fuera), FadeIn(tag_sat, shift=0.1 * UP),
                  run_time=0.7)
        self.wait(4.6)

        rot.mostrar(pie_curso("Por eso el LNB vive EN el foco del plato: "
                              "amplifica, y solo entonces baja la señal "
                              "a uno o dos gigahercios para cablearla."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- cierre de la leccion ------------------------------------------------
        self.play(FadeOut(curva), FadeOut(p100), FadeOut(tag100),
                  FadeOut(p1g), FadeOut(tag1g), FadeOut(flecha_fuera),
                  FadeOut(tag_sat), run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        linea1 = Text("Amplifica primero.", font_size=40, color=C_TITULO)
        linea2 = Text("Cablea después.", font_size=40, color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        rot.mostrar(pie_curso("Ya tienes la linea guiando la señal. "
                              "Falta ver que pasa cuando la frontera se "
                              "la devuelve."), zona="abajo", run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(4.8)

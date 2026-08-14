class Clip4(Scene):
    """1.1.4 - Ejemplos de aeronaves y vehiculos en cada regimen.

    La misma regla del clip anterior, ahora poblada. Cinco vehiculos reales
    colgados de su Mach de operacion; el color del marcador lo decide la
    banda, no el clip, asi que un vehiculo nunca puede quedar pintado del
    regimen equivocado. Cierre de la leccion. (~40 s)"""

    # Dos alturas alternadas: con cinco marcadores en una sola fila, los
    # nombres de Concorde y X-43A se tocan (la regla los deja a 1.45 u y el
    # rotulo mide mas de uno). Alternando, la separacion efectiva se dobla.
    ALTURAS = (0.62, 1.72, 0.62, 1.72, 0.62)

    def _marcador(self, banda, nombre, mach, tipo, altura):
        """Silueta + nombre + Mach colgados de la regla por una guia."""
        color = banda.color_de(mach)
        base = banda.punto_de(mach)
        figura = silueta(tipo, escala=0.62, color=color)
        figura.move_to(base + UP * (altura + 0.30))

        etiqueta = Text(nombre, font_size=17, color=color)
        etiqueta.next_to(figura, UP, buff=0.10)
        cifra = Text(f"M {mach:g}", font=FUENTE_HUD, font_size=15,
                     color=color).set_opacity(0.9)
        cifra.next_to(figura, DOWN, buff=0.10)

        guia = DashedLine(base + UP * 0.04, cifra.get_bottom() + DOWN * 0.06,
                          stroke_width=1.2, color=color, dash_length=0.06)
        guia.set_opacity(0.55)
        return VGroup(guia, figura, etiqueta, cifra)

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Quién vuela en cada régimen")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        banda = banda_regimenes()
        banda.move_to(DOWN * 2.15)
        self.play(FadeIn(banda), run_time=0.8)

        marcas = [self._marcador(banda, nombre, mach, tipo, alto)
                  for (nombre, mach, tipo, _h), alto
                  in zip(FLOTA, self.ALTURAS)]

        # --- momento: lo que vuela todos los dias -------------------------
        self.play(LaggedStart(*[FadeIn(m, shift=0.12 * UP) for m in marcas[:2]],
                              lag_ratio=0.5), run_time=1.5)
        rot.mostrar(pie_curso("Casi toda la aviación vive en los dos "
                              "primeros tramos."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        v_787 = km_h(FLOTA[1][1], FLOTA[1][3])
        rot.mostrar(pie_curso(f"Un 787 crucero a {v_787:.0f} km/h ya es "
                              "transónico: sobre el ala el aire pasa de "
                              "Mach 1."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: supersonico -----------------------------------------
        self.play(FadeIn(marcas[2], shift=0.12 * UP), run_time=0.8)
        v_concorde = km_h(FLOTA[2][1], FLOTA[2][3])
        rot.mostrar(pie_curso(f"El Concorde cruzaba a {v_concorde:.0f} km/h "
                              "arrastrando su cono."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: hipersonico ------------------------------------------
        self.play(LaggedStart(*[FadeIn(m, shift=0.12 * UP) for m in marcas[3:]],
                              lag_ratio=0.5), run_time=1.4)
        rot.mostrar(pie_curso("Más allá de Mach 5 la forma cambia de "
                              "objetivo: ya no es volar, es sobrevivir al "
                              "calor."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Por eso una cápsula de reentrada es roma. "
                              "Un morro afilado se derretiría."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(*marcas, banda)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("Un solo número decide", font_size=38,
                         color=C_TITULO),
            titulo_marca("qué ecuaciones puedes usar.", font_size=38,
                         color=C_CALCULO)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.4)

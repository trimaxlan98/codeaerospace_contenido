class Clip7(Scene):
    """7 - 38 microsegundos. El presupuesto diario del reloj en orbita
    (-7.21 y +45.72 no se cancelan) y la factura de no corregirlo: el
    circulo de error rojo creciendo sobre el mapa a 1 h, 6 h y 24 h.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("38 microsegundos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: el presupuesto del dia ------------------------------
        rot.mostrar(pie_curso("Velocidad y gravedad tiran en sentidos "
                              "opuestos. La cuenta del día no se cancela."),
                    zona="abajo", run_time=0.5)

        def renglon(cifra, etiqueta, color, tam):
            num = tag_hud(cifra, font_size=tam, color=color)
            eti = Text(etiqueta, font_size=17, color=C_TENUE)
            eti.set_opacity(0.85)
            return VGroup(eti, num).arrange(RIGHT, buff=0.30)

        fila_sr = renglon(f"{DERIVA_SR:+.2f} µs/día", "velocidad",
                          C_ERROR, 22)
        fila_gr = renglon(f"{DERIVA_GR:+.2f} µs/día", "gravedad",
                          C_GRAVEDAD, 22)
        fila_net = renglon(f"{DERIVA_NETA:+.2f} µs/día", "neto",
                           C_SATELITE, 30)
        raya = Line(ORIGIN, RIGHT * 3.3, stroke_width=2.0, color=C_EJE)
        encabezado = Text("el reloj en órbita, cada día", font_size=17,
                          color=C_TENUE)
        encabezado.set_opacity(0.7)

        columna = VGroup(encabezado, fila_sr, fila_gr, raya, fila_net)
        columna.arrange(DOWN, buff=0.30, aligned_edge=RIGHT)
        if columna.width > 4.6:
            columna.scale_to_fit_width(4.6)
        columna.move_to(UP * 0.15)

        self.play(FadeIn(encabezado, shift=0.12 * DOWN), run_time=0.6)
        self.play(FadeIn(fila_sr, shift=0.14 * RIGHT), run_time=0.7)
        self.wait(0.8)
        self.play(FadeIn(fila_gr, shift=0.14 * RIGHT), run_time=0.7)
        self.wait(0.8)
        self.play(Create(raya), run_time=0.5)
        self.play(FadeIn(fila_net, scale=0.82), run_time=0.9)
        self.wait(3.6)

        # --- momento: lo que costaria no corregirlo -----------------------
        rot.mostrar(pie_curso(f"¿Y si nadie corrigiera? "
                              f"{ERROR_HORA_M:.0f} m de error en una hora, "
                              f"y el círculo no para."),
                    zona="abajo", run_time=0.5)

        mapa = mapa_error()
        mapa.scale(0.92).move_to(RIGHT * 3.0 + UP * 0.2)
        mapa.en(0.0)
        contador = tag_hud("0 h", font_size=20, color=C_TENUE)
        contador.next_to(mapa, UP, buff=0.20)
        marcas = [tag_hud(t, font_size=20, color=C_TENUE).next_to(
            mapa, UP, buff=0.20) for t in ("1 h", "6 h", "24 h")]

        self.play(columna.animate.move_to(LEFT * 2.85 + UP * 0.15),
                  FadeIn(mapa, shift=0.18 * LEFT), FadeIn(contador),
                  run_time=0.9)
        self.wait(0.6)

        def crecer(desde, hasta):
            return UpdateFromAlphaFunc(
                mapa, lambda m, a: m.en(desde + (hasta - desde) * a))

        self.play(crecer(0.0, 1.0), Transform(contador, marcas[0]),
                  run_time=1.1)
        self.wait(1.2)
        self.play(crecer(1.0, 6.0), Transform(contador, marcas[1]),
                  run_time=1.4)
        self.wait(1.2)
        self.play(crecer(6.0, 24.0), Transform(contador, marcas[2]),
                  run_time=1.9)
        self.wait(0.9)

        cifra_km = tag_hud(f"{ERROR_DIA_KM:.1f} km/día", font_size=22,
                           color=C_ERROR)
        cifra_km.next_to(mapa, DOWN, buff=0.22)
        self.play(FadeIn(cifra_km, shift=0.12 * UP), run_time=0.7)
        self.wait(2.8)

        # --- momento: la escala del desastre ------------------------------
        rot.mostrar(pie_curso("En una semana, el GPS te ubicaría en otra "
                              "ciudad."), zona="abajo", run_time=0.5)
        self.wait(6.4)

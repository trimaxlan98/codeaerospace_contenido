class Clip4(Scene):
    """4.2.4 - El pase de un LEO: doce minutos de horizonte a horizonte,
    siete utiles, y una rampa de Doppler de +50 a -50 kHz que la estacion
    tiene que corregir sobre la marcha. Cierra la leccion. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El pase: siete minutos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la cupula del cielo ----------------------------------
        pas = pase_leo(h=H_LEO, el_max_deg=EL_MAX_PASE)
        pas.move_to(DOWN * 0.95)

        # La pieza ancla sus localizadores al CENTRO del grupo, que aqui no
        # coincide con el centro de la cupula (el grupo es media esfera):
        # `a_tiempo` sale desplazado. Se corrige con el desfase medido en un
        # punto conocido — el arranque del trayecto, que es t = -t_max.
        _delta = pas.trayecto.get_start() - pas.a_tiempo(-pas.t_max())

        def punto(t):
            return pas.a_tiempo(t) + _delta

        rot.mostrar(pie_curso("Ponte en la estación: el cielo entero es "
                              "esta cúpula sobre tu cabeza."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(pas.horizonte), FadeIn(pas.observador),
                  Create(pas.cupula), run_time=0.7)
        self.wait(4.6)

        # --- momento: el pase, de horizonte a horizonte --------------------
        sat = Dot(pas.trayecto.get_start(), radius=0.09, color=C_CARGA)
        relojes = VGroup(
            tag_hud(f"{T_PASE_MIN:.1f} min horizonte a horizonte"),
            tag_hud(f"{T_UTIL_MIN:.1f} min sobre {EL_MIN_UTIL:.0f} deg"))
        relojes.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        relojes.move_to(RIGHT * 4.3 + UP * 2.0)
        rot.mostrar(pie_curso("Asoma por un borde, cruza y se va: doce "
                              "minutos de reloj, siete de ellos útiles."),
                    zona="abajo", run_time=0.5)
        self.play(Create(pas.trayecto), FadeIn(sat, scale=1.5),
                  FadeIn(relojes, shift=0.15 * RIGHT), run_time=0.9)
        self.play(MoveAlongPath(sat, pas.trayecto), run_time=2.6,
                  rate_func=linear)
        self.wait(1.2)

        # --- momento: lo que cambia mientras cruza -------------------------
        p_horiz = punto(-pas.t_max())
        p_cenit = punto(0.0)
        d_horiz = Dot(p_horiz, radius=0.07, color=C_CALCULO)
        d_cenit = Dot(p_cenit, radius=0.07, color=C_CALCULO)
        tag_horiz = tag_hud(f"{pas.distancia_km(-pas.t_max()):,.0f} km"
                            f"   {pas.elevacion(-pas.t_max()):.0f} deg"
                            .replace(",", " "), font_size=17)
        tag_horiz.next_to(d_horiz, UP, buff=0.18)
        tag_cenit = tag_hud(f"{pas.distancia_km(0.0):.0f} km   "
                            f"{pas.elevacion(0.0):.0f} deg", font_size=17)
        tag_cenit.next_to(d_cenit, UP, buff=0.16)

        rot.mostrar(pie_curso("Asoma a casi tres mil kilómetros y pasa "
                              "por encima a quinientos cincuenta."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(d_horiz), FadeIn(d_cenit), FadeIn(tag_horiz),
                  FadeIn(tag_cenit), run_time=0.6)
        self.wait(4.6)

        # --- momento: la S del Doppler -------------------------------------
        ancho_caja, alto_caja = 6.6, 3.0
        curva = haz_curvas([lambda t: pas.doppler_khz(t, F_S)],
                           (-pas.t_max(), pas.t_max()), [C_CALCULO],
                           ancho=ancho_caja, alto=alto_caja,
                           etiqueta_x="tiempo del pase (s)",
                           etiqueta_y="Doppler (kHz)")
        # Centrar la CAJA, no el grupo: las etiquetas de los ejes sobresalen
        # y un move_to dejaria el dibujo descuadrado.
        curva.shift(DOWN * 0.35 - (curva.ejes[0].get_center()
                                   + UP * alto_caja / 2.0))
        tag_port = tag_hud(f"portadora {F_S / 1e9:.1f} GHz   banda S",
                           font_size=17)
        tag_port.to_corner(UR, buff=0.55)
        rot.mostrar(pie_curso("Y mientras corre, corre la frecuencia: "
                              "viene, pasa y se aleja."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(pas.cupula), FadeOut(pas.horizonte),
                  FadeOut(pas.observador), FadeOut(pas.trayecto),
                  FadeOut(sat), FadeOut(d_horiz), FadeOut(d_cenit),
                  FadeOut(tag_horiz), FadeOut(tag_cenit),
                  FadeOut(relojes), FadeIn(curva.ejes), FadeIn(tag_port),
                  run_time=0.9)
        self.play(Create(curva.curva(0)), run_time=1.6)
        self.wait(2.6)

        # --- momento: el cruce por cero ------------------------------------
        cero = curva.horizontal_en(0.0, color=C_EJE)
        p_cruce = Dot(curva.punto_de(0, 0.0), radius=0.08, color=C_CARGA)
        tag_alto = tag_hud(f"+{curva.valor(0, -pas.t_max()):.0f} kHz",
                           font_size=18)
        tag_alto.next_to(curva.punto_de(0, -pas.t_max()), LEFT, buff=0.16)
        tag_bajo = tag_hud(f"{curva.valor(0, pas.t_max()):.0f} kHz",
                           font_size=18)
        tag_bajo.next_to(curva.punto_de(0, pas.t_max()), RIGHT, buff=0.16)
        tag_cruce = tag_hud("cruce: el punto mas alto", font_size=17,
                            color=C_CARGA)
        tag_cruce.next_to(p_cruce, UR, buff=0.18)

        rot.mostrar(pie_curso("De más cincuenta kilohercios a menos "
                              "cincuenta, cruzando cero en lo más alto."),
                    zona="abajo", run_time=0.5)
        self.play(Create(cero), FadeIn(tag_alto), FadeIn(tag_bajo),
                  FadeIn(p_cruce, scale=1.6), FadeIn(tag_cruce),
                  run_time=0.7)
        self.wait(4.6)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(curva.ejes), FadeOut(curva.curva(0)),
                  FadeOut(cero), FadeOut(p_cruce),
                  FadeOut(tag_alto), FadeOut(tag_bajo), FadeOut(tag_cruce),
                  FadeOut(tag_port), run_time=0.7)
        rot.limpiar("arriba", run_time=0.3)
        linea1 = Text("GEO espera quieto.", font_size=40, color=C_TITULO)
        linea2 = Text("A LEO hay que cazarlo.", font_size=40,
                      color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        rot.mostrar(pie_curso("La estación corrige esa rampa en tiempo "
                              "real, o no entiende ni un bit."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.6)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.6)
        self.wait(4.6)

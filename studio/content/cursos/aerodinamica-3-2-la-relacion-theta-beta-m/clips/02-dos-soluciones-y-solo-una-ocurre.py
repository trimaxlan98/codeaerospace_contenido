class Clip2(Scene):
    """3.2.2 - Soluciones de choque debil y choque fuerte.

    Cada deflexion admite DOS ondas y las dos son legales. La naturaleza
    elige casi siempre la debil, y no por gusto: la fuerte solo aparece
    cuando algo aguas abajo la impone — una presion alta, un cuerpo romo.
    (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Dos soluciones, y solo una ocurre")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        mapa = diagrama_theta_beta(machs=(M_EJEMPLO,), ancho=4.6, alto=2.8)
        mapa.move_to(LEFT * 3.2 + DOWN * 0.30)
        self.play(FadeIn(mapa.ejes), Create(mapa.curva(0)), run_time=1.3)

        corte = DashedLine(mapa._en(THETA_EJEMPLO, 0.0),
                           mapa._en(THETA_EJEMPLO, 90.0), stroke_width=1.4,
                           color=C_TENUE, dash_length=0.07)
        self.play(Create(corte), run_time=0.6)
        rot.mostrar(pie_curso("Sube por tu deflexión y verás que la curva se "
                              "cruza dos veces."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: las dos ondas, dibujadas ------------------------------
        marcas = VGroup()
        ondas = VGroup()
        for rama, color, altura in (("debil", C_SUB, 1.30),
                                    ("fuerte", C_SUPER, -1.30)):
            datos = choque_oblicuo(M_EJEMPLO, THETA_EJEMPLO, rama)
            marcas.add(Dot(mapa.punto_de(0, THETA_EJEMPLO, rama), radius=0.07,
                           color=color))
            dibujo = onda_oblicua(M_EJEMPLO, THETA_EJEMPLO, largo=1.9,
                                  entrada=1.3, color_choque=color)
            # La rama fuerte no cambia la rampa, solo la onda: se redibuja el
            # choque con SU beta sobre la misma esquina.
            b = np.deg2rad(datos["beta"])
            dibujo.choque.put_start_and_end_on(
                dibujo.esquina(),
                dibujo.esquina() + np.array([np.cos(b), np.sin(b), 0.0]) * 1.9)
            grupo = VGroup(dibujo.pared, dibujo.choque)
            grupo.move_to(RIGHT * 3.0 + UP * altura)
            tag = VGroup(
                Text(f"choque {rama}", font_size=20, color=color),
                Text(f"beta {datos['beta']:.1f}   M2 {datos['M2']:.2f}",
                     font=FUENTE_HUD, font_size=16,
                     color=color)).arrange(DOWN, buff=0.10)
            tag.next_to(grupo, DOWN, buff=0.18)
            ondas.add(VGroup(grupo, tag))

        pies = (f"Una onda tumbada, que deja el flujo supersónico: "
                f"M2 = {DEBIL['M2']:.2f}.",
                f"Y una casi vertical, que lo deja subsónico: "
                f"M2 = {FUERTE['M2']:.2f}.")
        for marca, onda, pie in zip(marcas, ondas, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(marca, scale=1.5), FadeIn(onda, shift=0.12 * UP),
                      run_time=0.8)
            self.wait(4.6)

        rot.mostrar(pie_curso("Las dos cumplen todas las ecuaciones. Ninguna "
                              "es ilegal."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Pero en una rampa sale siempre la débil. La "
                              "fuerte necesita que algo la empuje desde "
                              "atrás."), zona="abajo", run_time=0.5)
        self.wait(5.2)

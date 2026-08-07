class Clip1(Scene):
    """1 - Un recurso que no se fabrica. Portada del curso; la barra de
    bandas satelitales aparece y varios segmentos pulsan en secuencia.
    Despues cinco mini-etiquetas de usos (TV, 5G, WIFI, SAT, RADAR)
    cuelgan de sus bandas en dos tandas, cada una con una guia vertical
    a `tope_de` de su segmento -- verticales puras, asi nunca se cruzan
    entre si sin importar el orden. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: portada del curso ----------------------------------
        portada = VGroup(
            titulo_marca("El espectro", font_size=46),
            Text("la guerra invisible por las ondas", font_size=24,
                color=C_ONDA),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.3)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(2.5)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.7)

        titulo = titulo_curso("Un recurso que no se fabrica")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.8)

        # --- momento: la barra, una sola recta ----------------------------
        barra = barra_bandas(ancho=6.8, alto=0.8, font_size=15)
        barra.move_to(UP * 0.3)

        self.play(FadeIn(barra, shift=0.15 * UP), run_time=1.0)
        self.wait(0.6)

        rot.mostrar(pie_curso("Todo lo inalámbrico —radio, GPS, satélites, "
                              "tu teléfono— cabe en una sola recta."),
                   zona="abajo", run_time=0.5)

        secuencia = ["UHF", "S", "C", "Ku", "Ka"]
        self.play(LaggedStart(*[Indicate(barra.segmento(nombre),
                                         color=C_ONDA, scale_factor=1.12)
                               for nombre in secuencia], lag_ratio=0.5),
                  run_time=2.8)
        self.wait(2.4)

        rot.mostrar(pie_curso("No se puede fabricar más: solo repartirla "
                              "mejor."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: los usos se reparten la barra, en dos tandas --------
        rot.mostrar(pie_curso("Y todos la quieren al mismo tiempo."),
                   zona="abajo", run_time=0.5)

        # (nombre de uso, banda destino, tanda de aparicion)
        usos = [("TV", "UHF", 0), ("WIFI", "S", 0), ("5G", "C", 0),
                ("RADAR", "X", 1), ("SAT", "Ku", 1)]
        alturas = [0.95, 1.45]

        # Ordenadas por la x de su tope: la fila alterna 0/1 sobre ese
        # orden, y cada guia es una vertical pura (mismo x en tope y
        # etiqueta) -- ninguna puede cruzarse con otra.
        orden = sorted(usos, key=lambda u: barra.tope_de(u[1])[0])
        tandas = [VGroup(), VGroup()]
        for i, (nombre, banda, tanda) in enumerate(orden):
            tope = barra.tope_de(banda)
            etiqueta = etiqueta_hud(nombre, color=C_ONDA).scale(0.8)
            etiqueta.move_to(tope + UP * alturas[i % 2])
            linea = Line(tope, etiqueta.get_bottom() + DOWN * 0.02,
                        stroke_width=1.4, color=C_TENUE)
            linea.set_opacity(0.6)
            tandas[tanda].add(VGroup(linea, etiqueta))

        self.play(LaggedStart(*[FadeIn(g, shift=0.12 * DOWN)
                               for g in tandas[0]], lag_ratio=0.35),
                  run_time=1.3)
        self.wait(1.8)
        self.play(LaggedStart(*[FadeIn(g, shift=0.12 * DOWN)
                               for g in tandas[1]], lag_ratio=0.35),
                  run_time=1.1)
        self.wait(2.6)

        rot.mostrar(pie_curso("Esta es la historia de cómo se reparte el "
                              "cielo."), zona="abajo", run_time=0.5)
        self.wait(5.4)

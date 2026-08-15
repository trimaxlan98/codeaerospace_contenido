class Clip4(Scene):
    """4 - Redundancia: por qué comprime un zip (y un jpg). El idioma
    repite: quitar las vocales de una frase y se sigue leyendo. Contando
    solo frecuencias el español desperdicia ~13 % (medido); con contexto,
    Shannon estimó ~75 % (cita, ingles 1951). Un compresor sin perdida
    quita esa redundancia (RLE de un icono binario, medido); uno con
    perdida tira lo que el ojo no ve (una esfera en gris cuantizada de 8 a
    2 bits por pixel). Cierre: comprimir es no repetir, y a veces, no
    decir. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Redundancia: por qué comprime un zip"),
                    zona="arriba", run_time=0.6)

        # --- momento 1: el idioma repite --------------------------------------
        rot.mostrar(pie_curso("El idioma repite. Quita las vocales… y se "
                              "sigue leyendo."), zona="abajo")
        frase = Text(FRASE_REDUNDANTE, font_size=40, color=C_FUENTE)
        frase.move_to(np.array([0.0, 0.3, 0.0]))
        self.play(FadeIn(frase, shift=0.12 * UP), run_time=0.8)
        self.wait(2.2)
        frase_sv = Text(FRASE_SIN_VOCALES, font_size=40, color=C_FUENTE)
        frase_sv.move_to(frase.get_center())
        self.play(FadeOut(frase, shift=0.1 * UP),
                  FadeIn(frase_sv, shift=0.1 * UP), run_time=0.8)
        self.wait(2.0)

        # --- momento 2: la redundancia medida y con contexto ------------------
        rot.mostrar(pie_curso("Contando símbolos sueltos, el español "
                              f"desperdicia un {REDUNDANCIA_ES * 100:.0f} %; "
                              "con contexto, Shannon estimó "
                              f"~{REDUNDANCIA_SHANNON_1951 * 100:.0f} %."),
                    zona="abajo")
        tag_orden0 = tag_hud(
            f"orden 0 (medido): {REDUNDANCIA_ES * 100:.0f} %", font_size=14,
            color=C_LIMITE)
        tag_contexto = tag_hud(
            f"con contexto (Shannon 1951, cita): "
            f"~{REDUNDANCIA_SHANNON_1951 * 100:.0f} %", font_size=14,
            color=C_TENUE)
        bloque_red = VGroup(tag_orden0, tag_contexto).arrange(
            DOWN, buff=0.24, aligned_edge=ORIGIN)
        bloque_red.move_to(np.array([0.0, -0.6, 0.0]))
        self.play(FadeIn(tag_orden0, shift=0.08 * UP), run_time=0.5)
        self.play(FadeIn(tag_contexto, shift=0.08 * UP), run_time=0.5)
        self.wait(3.2)
        self.play(FadeOut(frase_sv), FadeOut(bloque_red), run_time=0.6)

        # --- momento 3: sin perdida, el principio de un zip ---------------------
        rot.mostrar(pie_curso("Un compresor sin pérdida quita lo que se "
                              "repite: el principio de un zip."),
                    zona="abajo")
        icono = imagen_bits(ICONO, C_FUENTE, celda=0.18)
        icono.move_to(np.array([-3.1, 0.35, 0.0]))
        self.play(LaggedStart(
            *[FadeIn(VGroup(*[icono.celda(f, c)
                              for c in range(icono.columnas)]), scale=0.9)
              for f in range(icono.filas)], lag_ratio=0.08), run_time=1.6)
        tag_crudo = tag_hud(f"crudo: {BITS_ICONO} bits", font_size=14,
                            color=C_FUENTE)
        tag_crudo.next_to(icono, DOWN, buff=0.20)
        self.play(FadeIn(tag_crudo, shift=0.08 * UP), run_time=0.4)
        self.wait(1.6)

        fila_marca = Rectangle(width=icono.columnas * 0.18 * 0.94,
                               height=0.18 * 0.94, stroke_width=1.6,
                               color=C_CODIGO, fill_opacity=0.0)
        fila_marca.move_to(icono.celda(4, icono.columnas // 2).get_center())
        fila_marca.stretch_to_fit_width(icono.columnas * 0.18)
        tag_rle = tag_hud(f"RLE (tramos): {BITS_ICONO_RLE} bits",
                          font_size=14, color=C_CODIGO)
        tag_rle.next_to(tag_crudo, DOWN, buff=0.16)
        self.play(Create(fila_marca), run_time=0.5)
        self.play(FadeIn(tag_rle, shift=0.08 * UP), run_time=0.5)
        self.wait(3.0)

        # --- momento 4: con perdida, el principio de un jpg ----------------------
        rot.mostrar(pie_curso("Y con pérdida: tirar lo que el ojo no ve. "
                              "El principio de un jpg."), zona="abajo")
        esfera = imagen_gris(ESFERA, celda=0.18)
        esfera.move_to(np.array([3.1, 0.35, 0.0]))
        self.play(LaggedStart(
            *[FadeIn(VGroup(*[esfera.celda(f, c)
                              for c in range(esfera.columnas)]), scale=0.9)
              for f in range(esfera.filas)], lag_ratio=0.08), run_time=1.6)
        tag_8bit = tag_hud(f"8 bits/pixel: {miles(BITS_ESFERA_8)} bits",
                           font_size=14, color=C_FUENTE)
        tag_8bit.next_to(esfera, DOWN, buff=0.20)
        self.play(FadeIn(tag_8bit, shift=0.08 * UP), run_time=0.4)
        self.wait(1.8)

        esfera_jpg = esfera.con_matriz(ESFERA_JPG)
        tag_2bit = tag_hud(f"2 bits/pixel: {BITS_ESFERA_2} bits",
                           font_size=14, color=C_CODIGO)
        tag_2bit.move_to(tag_8bit.get_center())
        self.play(Transform(esfera, esfera_jpg),
                  Transform(tag_8bit, tag_2bit), run_time=1.4)
        tag_x4 = tag_hud("/4", font_size=26, color=C_CODIGO)
        tag_x4.next_to(esfera, RIGHT, buff=0.24)
        self.play(FadeIn(tag_x4, shift=0.08 * LEFT), run_time=0.5)
        self.wait(3.0)

        # --- cierre --------------------------------------------------------
        rot.mostrar(pie_curso("Comprimir es no repetir. Y, a veces, no "
                              "decir."), zona="abajo")
        self.wait(5.0)

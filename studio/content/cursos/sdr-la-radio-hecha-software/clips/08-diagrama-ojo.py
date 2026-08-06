class Clip8(Scene):
    """8 - El diagrama de ojo. Superponer los tramos de dos simbolos
    dibuja un ojo: su altura es el margen contra el ruido, su anchura el
    margen contra el jitter de reloj. Cierra el curso con la tarjeta de
    marca. (~44 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ------------------------------------------------
        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("El ojo que vigila el enlace")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(0.6)

        # --- momento: el ojo se construye con sus trazas -------------------
        ojo = diagrama_ojo(ancho=3.6, alto=2.4)
        ojo.move_to(0.3 * UP)
        self.play(LaggedStart(*[Create(t) for t in ojo.trazas],
                              lag_ratio=0.05), run_time=1.0)
        rot.mostrar(pie_curso("Superpón todos los tramos de dos símbolos: "
                              "aparece un ojo."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: la llave vertical, margen contra el ruido -------------
        marca_v = Line(ojo.get_right() + 0.15 * RIGHT + 0.75 * DOWN,
                       ojo.get_right() + 0.15 * RIGHT + 0.75 * UP,
                       stroke_width=0)
        llave_v = llave(marca_v, "margen contra el ruido", direccion=RIGHT)
        self.play(GrowFromCenter(llave_v[0]),
                  FadeIn(llave_v[1], shift=0.1 * RIGHT), run_time=0.6)
        rot.mostrar(pie_curso("Su altura: cuánto ruido tolera cada "
                              "decisión."), zona="abajo", run_time=0.5)
        self.wait(5.2)
        self.play(FadeOut(llave_v), run_time=0.35)

        # --- momento: relevo -> llave horizontal, margen contra el reloj ----
        marca_h = Line(ojo.get_bottom() + 0.25 * DOWN + 0.5 * LEFT,
                       ojo.get_bottom() + 0.25 * DOWN + 0.5 * RIGHT,
                       stroke_width=0)
        llave_h = llave(marca_h, "margen contra el reloj", direccion=DOWN)
        self.play(GrowFromCenter(llave_h[0]),
                  FadeIn(llave_h[1], shift=0.1 * DOWN), run_time=0.6)
        rot.mostrar(pie_curso("Su anchura: cuánto puede errar el instante "
                              "de muestreo."), zona="abajo", run_time=0.5)
        self.wait(5.2)
        self.play(FadeOut(llave_h), run_time=0.35)

        # --- momento: el ruido crece y el ojo se cierra ----------------------
        ojo_cerrado = diagrama_ojo(ancho=3.6, alto=2.4, ruido=0.30)
        ojo_cerrado.move_to(ojo.get_center())
        self.play(ReplacementTransform(ojo, ojo_cerrado), run_time=0.9)
        rot.mostrar(pie_curso("Ojo cerrado: ningún decodificador te "
                              "salva."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: vuelve a abrirse, el enlace vive -----------------------
        # El pie cambia ANTES del transform: si el ojo reabre con el pie
        # "cerrado" aun visible, imagen y texto se contradicen ~1 s.
        ojo_abierto = diagrama_ojo(ancho=3.6, alto=2.4, ruido=0.05,
                                   color=C_OK)
        ojo_abierto.move_to(ojo_cerrado.get_center())
        rot.mostrar(pie_curso("Ojo abierto: el enlace vive."), zona="abajo",
                    run_time=0.5)
        self.play(ReplacementTransform(ojo_cerrado, ojo_abierto),
                  run_time=0.9)
        self.wait(5.2)

        # --- momento: pantalla limpia para la tarjeta de cierre --------------
        rot.limpiar(run_time=0.4)
        self.play(FadeOut(VGroup(ojo_abierto, modulo)), run_time=0.9)

        # --- momento: tarjeta final, patron exacto del curso ------------------
        titulo_final = titulo_marca("SDR", font_size=46)
        subtitulo = Text("la radio hecha software", font_size=25,
                         color=C_ACENTO)
        cuerpo = VGroup(titulo_final, subtitulo).arrange(DOWN, buff=0.26)

        subrayado = Line(LEFT, RIGHT, color=C_ACENTO)
        subrayado.set_width(subtitulo.width * 1.1)
        subrayado.next_to(subtitulo, DOWN, buff=0.16)
        brillo_subrayado = con_brillo(subrayado, color=C_ACENTO)

        tarjeta = VGroup(cuerpo, brillo_subrayado)
        tarjeta.move_to(ORIGIN)

        self.play(Write(titulo_final), run_time=1.6)
        self.play(FadeIn(subtitulo, shift=0.15 * UP), run_time=0.8)
        self.wait(1.2)
        self.play(Create(brillo_subrayado), run_time=1.2)
        self.wait(2)

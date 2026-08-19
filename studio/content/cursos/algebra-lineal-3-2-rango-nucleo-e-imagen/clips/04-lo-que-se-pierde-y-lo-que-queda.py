class Clip4(Scene):
    """3.2.4 - Rango mas nulidad es la dimension de la entrada: lo que queda
    mas lo que se pierde es todo lo que habia. 2 = 1 + 1 en el plano y
    3 = 2 + 1 en el espacio. Cierra la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Lo que se pierde y lo que queda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: las dos rectas del plano ------------------------------
        rot.mostrar(pie_curso("En el plano, A deja una recta y se traga "
                              "otra."), zona="abajo", run_time=0.5)
        pl = plano_leccion()
        linea_img = span_recta(pl, DIR_IMG, color=C_IMG, grosor=5.0,
                               opacidad=1.0)
        # Del nucleo se dibujan DOS copias: la tenue se queda (es el conjunto
        # de entradas, y sin ella el rotulo fucsia se quedaria solo en medio
        # de la nada) y la viva se va al origen con la transformacion.
        linea_nuc = span_recta(pl, DIR_NUC, color=C_PROPIO, grosor=2.2,
                               opacidad=0.35)
        linea_cae = span_recta(pl, DIR_NUC, color=C_PROPIO, grosor=3.0,
                               opacidad=0.9)
        self.play(FadeIn(pl), run_time=0.8)
        self.play(Create(linea_img), Create(linea_nuc), Create(linea_cae),
                  run_time=0.9)
        self.wait(2.9)

        # --- momento: la que sobrevive y la que cae -------------------------
        rot.mostrar(pie_curso("La verde sobrevive, la fucsia cae al origen: "
                              "una más una, dos."), zona="abajo",
                    run_time=0.5)
        cero = Dot(pl.p(0, 0), radius=0.11, color=C_PROPIO)
        self.play(*pl.anim_matriz(A_PLANA),
                  Transform(linea_cae, cero), run_time=2.0)
        self.bring_to_front(linea_img)
        et_img = tag_hud("imagen: dim " + fmt(RANGO_PLANA, 0), font_size=17,
                         color=C_IMG)
        et_img.next_to(pl.p(-2.6 * DIR_IMG), UP + LEFT, buff=0.10)
        et_nuc = tag_hud("nucleo: dim " + fmt(NUL_PLANA, 0), font_size=17,
                         color=C_PROPIO)
        et_nuc.next_to(pl.p(1.15 * DIR_NUC), RIGHT, buff=0.14)
        self.play(FadeIn(et_img), FadeIn(et_nuc), run_time=0.5)
        self.wait(1.6)
        panel_a = panel_derecha(
            matriz_columnas(A_PLANA),
            tag_hud("rango " + fmt(RANGO_PLANA, 0) + " + nulidad "
                    + fmt(NUL_PLANA, 0) + " = " + fmt(N_PLANO, 0)))
        self.play(FadeIn(panel_a, shift=0.15 * LEFT), run_time=0.6)
        self.wait(2.6)

        # --- momento: lo mismo en el espacio --------------------------------
        rot.mostrar(pie_curso("En el espacio pasa igual, con una dimensión "
                              "más."), zona="abajo", run_time=0.5)
        self.play(FadeOut(pl), FadeOut(linea_img), FadeOut(linea_nuc),
                  FadeOut(linea_cae), FadeOut(et_img), FadeOut(et_nuc),
                  FadeOut(panel_a), run_time=0.6)
        esp = espacio3(unidad=0.8, alcance=3)
        k3 = vector3(esp, K_ESPACIO, color=C_PROPIO)
        self.play(FadeIn(esp), run_time=0.8)
        self.play(GrowArrow(k3.flecha), run_time=0.6)
        self.wait(2.6)

        rot.mostrar(pie_curso("La vertical se pierde y queda un plano: dos "
                              "más una, tres."), zona="abajo", run_time=0.5)
        panel_b = panel_derecha(
            matriz_columnas(A_ESPACIO, font_size=26, h_buff=0.62,
                            v_buff=0.55),
            tag_hud("rango " + fmt(RANGO_ESPACIO, 0) + " + nulidad "
                    + fmt(NUL_ESPACIO, 0) + " = " + fmt(N_ESPACIO, 0)))
        self.play(FadeIn(panel_b, shift=0.15 * LEFT), run_time=0.5)
        self.play(*esp.anim_matriz(A_ESPACIO, k3), run_time=2.0)
        parche = plano_generado(esp, COL_ESP_1, COL_ESP_2, extension=2.2,
                                color=C_IMG, opacidad=0.20)
        self.play(FadeIn(parche), run_time=0.6)
        self.wait(2.4)

        # --- momento: el triptico -------------------------------------------
        rot.mostrar(pie_curso("Lo que queda más lo que se pierde es todo lo "
                              "que había."), zona="abajo", run_time=0.5)
        self.play(FadeOut(esp), FadeOut(k3), FadeOut(parche),
                  FadeOut(panel_b), run_time=0.6)

        def fila(etiqueta, r, k, n):
            cuenta = MathTex(fmt(r, 0), "+", fmt(k, 0), "=", fmt(n, 0),
                             font_size=44)
            cuenta[0].set_color(C_IMG)
            cuenta[2].set_color(C_PROPIO)
            cuenta[4].set_color(C_TITULO)
            etq = tag_hud(etiqueta, font_size=17, color=C_TENUE)
            return VGroup(etq, cuenta).arrange(RIGHT, buff=0.5)

        cabecera = MathTex(r"\mathrm{rango} + \mathrm{nulidad} = n",
                           font_size=34, color=C_TENUE)
        f_plano = fila("en el plano", RANGO_PLANA, NUL_PLANA, N_PLANO)
        f_espacio = fila("en el espacio", RANGO_ESPACIO, NUL_ESPACIO,
                         N_ESPACIO)
        triptico = VGroup(f_plano, f_espacio).arrange(DOWN, buff=0.5,
                                                      aligned_edge=RIGHT)
        bloque = VGroup(cabecera, triptico).arrange(DOWN, buff=0.6)
        bloque.move_to(DOWN * 0.15)
        self.play(FadeIn(bloque, shift=0.2 * UP), run_time=0.9)
        self.wait(3.7)

        # --- cierre de la leccion -------------------------------------------
        cierre_leccion(self, rot, "Imagen: lo que queda.",
                       "Núcleo: lo que se pierde.",
                       "En la próxima lección, el mismo vector contado en "
                       "otro idioma.", bloque)

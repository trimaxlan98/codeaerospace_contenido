class Clip2(Scene):
    """3.2.2 - El rango es la dimension de la imagen: cuantas direcciones
    independientes sobreviven. Rango 1 y 2 en el plano; rango 2 en el
    espacio, donde la imagen es un plano. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El rango es la dimensión de la imagen")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: las columnas son los destinos de i y j ----------------
        rot.mostrar(pie_curso("Mira a dónde van î y ĵ: sus destinos son las "
                              "columnas."), zona="abajo", run_time=0.5)
        pl = plano_leccion()
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN + RIGHT)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=UP + LEFT)
        self.play(FadeIn(pl), run_time=0.8)
        self.play(GrowArrow(i_hat.flecha), FadeIn(i_hat.etiqueta),
                  GrowArrow(j_hat.flecha), FadeIn(j_hat.etiqueta),
                  run_time=0.8)
        self.wait(3.4)

        # --- caso rango 1 ----------------------------------------------------
        rot.mostrar(pie_curso("Con A las dos llegan a la misma recta: una "
                              "sola dirección."), zona="abajo", run_time=0.5)
        panel_a = panel_derecha(matriz_columnas(A_PLANA),
                                tag_hud("rango " + fmt(RANGO_PLANA, 0)
                                        + " de " + fmt(N_PLANO, 0)))
        self.play(FadeIn(panel_a, shift=0.15 * LEFT), run_time=0.5)
        self.play(*pl.anim_matriz(A_PLANA, i_hat, j_hat), run_time=2.0)
        self.wait(2.7)

        # --- caso rango 2 ----------------------------------------------------
        rot.mostrar(pie_curso("Con B se separan: dos direcciones, y con "
                              "ellas todo el plano."), zona="abajo",
                    run_time=0.5)
        panel_b = panel_derecha(matriz_columnas(A_LLENA),
                                tag_hud("rango " + fmt(RANGO_LLENA, 0)
                                        + " de " + fmt(N_PLANO, 0)))
        self.play(FadeOut(panel_a), run_time=0.3)
        self.play(FadeIn(panel_b, shift=0.15 * LEFT), run_time=0.5)
        self.play(*pl.anim_matriz(A_LLENA, i_hat, j_hat), run_time=2.0)
        self.wait(2.4)

        # --- caso 3D: rango 2 dentro del espacio -----------------------------
        rot.mostrar(pie_curso("En el espacio caben tres direcciones "
                              "independientes."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(pl), FadeOut(i_hat), FadeOut(j_hat),
                  FadeOut(panel_b), run_time=0.6)
        esp = espacio3(unidad=0.8, alcance=3)
        self.play(FadeIn(esp), run_time=0.9)
        self.wait(3.5)

        rot.mostrar(pie_curso("Esta matriz deja dos: la imagen es un plano "
                              "dentro del espacio."), zona="abajo",
                    run_time=0.5)
        panel_c = panel_derecha(matriz_columnas(A_ESPACIO, font_size=26,
                                                h_buff=0.62, v_buff=0.55),
                                tag_hud("rango " + fmt(RANGO_ESPACIO, 0)
                                        + " de " + fmt(N_ESPACIO, 0)))
        self.play(FadeIn(panel_c, shift=0.15 * LEFT), run_time=0.5)
        self.play(*esp.anim_matriz(A_ESPACIO), run_time=2.0)
        parche = plano_generado(esp, COL_ESP_1, COL_ESP_2, extension=2.2,
                                color=C_IMG, opacidad=0.20)
        self.play(FadeIn(parche), run_time=0.7)
        self.wait(1.8)

        # --- resumen: los tres casos rotulados -------------------------------
        rot.mostrar(pie_curso("El rango cuenta las dimensiones que "
                              "sobreviven."), zona="abajo", run_time=0.5)
        resumen = panel_derecha(
            tag_hud("A  rango " + fmt(RANGO_PLANA, 0) + " de "
                    + fmt(N_PLANO, 0) + "  recta", font_size=15),
            tag_hud("B  rango " + fmt(RANGO_LLENA, 0) + " de "
                    + fmt(N_PLANO, 0) + "  plano", font_size=15),
            tag_hud("C  rango " + fmt(RANGO_ESPACIO, 0) + " de "
                    + fmt(N_ESPACIO, 0) + "  plano 3D", font_size=15),
            buff=0.22)
        # Baja del rincon: pegado arriba roza el titulo, que en esta leccion
        # es largo y llega casi al centro del cuadro.
        resumen.shift(DOWN * 0.4)
        self.play(FadeOut(panel_c), run_time=0.3)
        self.play(FadeIn(resumen, shift=0.15 * LEFT), run_time=0.6)
        self.wait(4.1)

        rot.mostrar(pie_curso("¿Y las direcciones que no sobreviven? Ese es "
                              "el núcleo."), zona="abajo", run_time=0.5)
        self.wait(5.0)

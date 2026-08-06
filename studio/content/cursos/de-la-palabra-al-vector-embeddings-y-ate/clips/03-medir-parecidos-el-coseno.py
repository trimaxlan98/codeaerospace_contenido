class Clip3(Scene):
    """3 - Medir parecidos: el coseno. Tres vectores en el plano semantico
    (gato, felino, luna): el angulo entre ellos, convertido en un numero
    entre -1 y 1, es la similitud coseno."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: titulo y HUD del modulo ------------------------------
        titulo = titulo_curso("Medir parecidos: el coseno")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.wait(1.4)

        # --- momento: plano a la izquierda con tres palabras ----------------
        ejes = ejes_plano(lado=4.4)
        ejes.move_to(np.array([-2.6, 0.0, 0.0]))
        # Direcciones explicitas: con el default UR las etiquetas de gato
        # y felino (puntos casi vecinos) se pisaban, y la de luna caia
        # sobre el eje horizontal y la punta de su flecha.
        mapa = mapa_embeddings(ejes, ["gato", "felino", "luna"],
                               colores=[C_VECTOR, C_VECTOR, C_TENUE],
                               font_size=17,
                               direcciones={"gato": UR, "felino": LEFT,
                                            "luna": DOWN})
        self.play(Create(ejes), run_time=1.0)
        self.play(FadeIn(mapa, lag_ratio=0.15), run_time=1.1)
        self.wait(1.3)

        # --- momento: flechas desde el origen -------------------------------
        flecha_gato = flecha_vector(ejes, (0, 0), "gato", color=C_VECTOR)
        flecha_felino = flecha_vector(ejes, (0, 0), "felino", color=C_VECTOR)
        flecha_luna = flecha_vector(ejes, (0, 0), "luna", color=C_TENUE)
        self.play(GrowArrow(flecha_gato), GrowArrow(flecha_felino),
                  run_time=1.0)
        self.play(GrowArrow(flecha_luna), run_time=0.8)
        self.wait(1.0)

        # --- momento: arco pequeno gato-felino -------------------------------
        arco = arco_similitud(ejes, "gato", "felino", color=C_ACENTO)
        self.play(Create(arco), run_time=0.9)
        rot.mostrar(pie_curso("Ángulo pequeño: significados cercanos."),
                   zona="abajo", run_time=0.5)
        self.wait(2.1)

        # --- momento: valor coseno gato-felino, columna derecha --------------
        cos_gf = similitud_coseno("gato", "felino")
        linea_gf = MathTex(
            rf"\cos(\text{{gato}},\text{{felino}}) = {cos_gf:.2f}",
            font_size=30, color=C_PROB)
        if linea_gf.width > 3.8:
            linea_gf.scale_to_fit_width(3.8)
        linea_gf.move_to(np.array([3.5, 0.35, 0.0]))
        self.play(Write(linea_gf), run_time=1.0)
        self.wait(1.9)

        # --- momento: relevo del arco -- ahora gato-luna ----------------------
        self.play(FadeOut(arco), run_time=0.4)
        arco2 = arco_similitud(ejes, "gato", "luna", color=C_ACENTO)
        self.play(Create(arco2), run_time=0.9)
        rot.mostrar(pie_curso("Ángulo grande: nada que ver."), zona="abajo",
                   run_time=0.5)
        self.wait(2.1)

        # --- momento: valor coseno gato-luna, apilado bajo el primero ---------
        cos_gl = similitud_coseno("gato", "luna")
        linea_gl = MathTex(
            rf"\cos(\text{{gato}},\text{{luna}}) = {cos_gl:.2f}",
            font_size=30, color=C_MAL)
        if linea_gl.width > 3.8:
            linea_gl.scale_to_fit_width(3.8)
        linea_gl.next_to(linea_gf, DOWN, buff=0.4)
        self.play(Write(linea_gl), run_time=1.0)
        self.wait(1.6)

        # --- momento: cierre -- los dos valores juntos, un rango claro -------
        self.play(Indicate(linea_gf, color=C_PROB), Indicate(linea_gl, color=C_MAL),
                  run_time=1.1)
        rot.mostrar(pie_curso("Un número entre -1 y 1: la similitud coseno."),
                   zona="abajo", run_time=0.5)
        self.wait(5.6)

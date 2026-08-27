# =====================================================================
# Promo "El secreto que se grita en publico" — curso 19, Criptografia.
#
#   estado 0   ..  Ana arriba y Beto abajo con su numero PRIVADO (ambar)
#   0.35-1.55  ..  cada uno calcula y saca su numero PUBLICO (cian)
#   1.55-4.55  ..  los publicos CRUZAN el canal, a la vista
#   4.55-6.65  ..  cada uno mezcla lo que oyo con lo suyo y aparece el
#                  MISMO secreto (verde) en los dos lados a la vez
#   6.65-10.55 ..  respiro: el verde esta arriba y abajo, y no cruzo nunca
#   10.55-12.15 .. todo vuelve a los dos numeros privados
#
# El verde no toca la linea del canal en ningun frame: ese es el clip.
# =====================================================================


class Promo(Scene):
    def setup(self):
        code_brand.aplicar_marca(self, esquinas=True, marca=False, fondo=True)

    def construct(self):
        fmt = FMT

        # Tres columnas por persona: PRIVADO a la izquierda (nunca se
        # mueve), lo RECIBIDO en el centro (llega cruzando el canal) y el
        # SECRETO a la derecha. Con menos separacion, "19" y "2" se leen
        # como "192".
        if fmt.es_vertical:
            y_ana, y_canal, y_beto = 3.30, 0.55, -2.20
            x_priv, x_pub, x_sec = -2.10, 0.55, 2.10
        else:
            y_ana, y_canal, y_beto = 2.30, 0.10, -2.10
            x_priv, x_pub, x_sec = -3.60, 0.00, 3.40

        self.add(_promo.fondo_seguro(fmt), _promo.marca_promo(fmt))
        if GUIAS:
            self.add(_promo.guias(fmt))

        # --- el canal, que lo ve todo el mundo ------------------------
        linea = DashedLine(LEFT * 3.4 + UP * y_canal,
                           RIGHT * 3.4 + UP * y_canal,
                           dash_length=0.14, stroke_width=2.0,
                           color=CODE_MUTED)
        linea.set_stroke(opacity=0.55)
        rotulo_canal = etiqueta_hud("CANAL PUBLICO", font_size=14,
                                    color=CODE_MUTED)
        rotulo_canal.next_to(linea, UP, buff=0.14).align_to(linea, LEFT)

        def persona(nombre, privado, y):
            tag = etiqueta_hud(nombre, font_size=16, color=CODE_MUTED)
            tag.move_to(UP * y + RIGHT * x_priv + UP * 0.45)
            n = numero(privado, C_PRIVADO).move_to(UP * y + RIGHT * x_priv)
            return VGroup(tag, n)

        ana = persona("ANA", A_DH, y_ana)
        beto = persona("BETO", B_DH, y_beto)

        # Lo publico nace al lado de su dueño y viaja al otro lado. Van por
        # carriles distintos (-0.55 y +0.55) para cruzarse sin pisarse.
        pub_ana = numero(PUB_A, C_PUBLICO).move_to(
            UP * y_ana + RIGHT * (x_pub - 1.1))
        pub_beto = numero(PUB_B, C_PUBLICO).move_to(
            UP * y_beto + RIGHT * x_pub)
        # El secreto aparece a la derecha de cada uno y NO se mueve jamas.
        sec_ana = numero(SECRETO, C_SECRETO, font_size=64).move_to(
            UP * y_ana + RIGHT * x_sec)
        sec_beto = numero(SECRETO, C_SECRETO, font_size=64).move_to(
            UP * y_beto + RIGHT * x_sec)
        # La leccion, en cuatro palabras, para quien lo vea sin sonido.
        moraleja = etiqueta_hud("EL VERDE NUNCA CRUZO", font_size=15,
                                color=C_SECRETO)
        moraleja.move_to(UP * (fmt.suelo + 0.75) if fmt.es_vertical
                         else UP * (fmt.suelo + 0.55))

        # --- estado de arranque Y de cierre ---------------------------
        self.add(linea, rotulo_canal, ana, beto)
        self.wait(0.35)

        # --- 1. cada uno grita su numero publico ----------------------
        self.play(FadeIn(pub_ana, shift=RIGHT * 0.3),
                  FadeIn(pub_beto, shift=RIGHT * 0.3), run_time=1.2)

        # --- 2. los publicos cruzan el canal --------------------------
        self.play(pub_ana.animate.move_to(UP * y_beto + RIGHT * (x_pub - 1.1)),
                  pub_beto.animate.move_to(UP * y_ana + RIGHT * x_pub),
                  run_time=3.0, rate_func=smooth)

        # --- 3. el mismo secreto en los dos lados ---------------------
        self.play(FadeIn(sec_ana, scale=0.6), FadeIn(sec_beto, scale=0.6),
                  FadeIn(moraleja), run_time=1.1)
        self.play(Indicate(sec_ana, color=C_SECRETO, scale_factor=1.25),
                  Indicate(sec_beto, color=C_SECRETO, scale_factor=1.25),
                  run_time=1.0)
        self.wait(3.9)

        # --- 4. vuelta al principio -----------------------------------
        self.play(FadeOut(sec_ana), FadeOut(sec_beto), FadeOut(moraleja),
                  FadeOut(pub_ana), FadeOut(pub_beto), run_time=1.6)
        self.wait(0.35)

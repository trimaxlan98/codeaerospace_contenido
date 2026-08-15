class Clip3(Scene):
    """3 - La llave perfecta. Bits: mensaje de 24 bits (tres letras ASCII),
    llave aleatoria de 24 bits y su XOR bit a bit, que parece ruido. La
    misma llave por segunda vez devuelve el mensaje; y lo perfecto
    (Shannon 1949): OTRA llave sobre el MISMO cifrado da OTRO mensaje
    igual de valido ("MAR" -> "SOL"), asi que el atacante no puede saber
    cual es real entre 2^24 = 16 777 216 llaves y otros tantos mensajes.
    Cierre: perfecta e impractica -- aleatoria, tan larga como el mensaje
    y de un solo uso. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La llave perfecta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # Geometria: tres tiras de 24 celdas apiladas, centradas en x=0.
        # mensaje y=+1.3 (ambar), llave y=+0.3 (verde), cifrado y=-0.9
        # (cian); "MAR"/"SOL" van sobre los 3 bytes del mensaje,
        # centradas en las celdas 4, 12 y 20.
        msg = tira_bits(BITS_OTP, C_CLARO, celda=0.28)
        msg.shift(UP * 1.3)
        llave = tira_bits(LLAVE_OTP, C_LLAVE, celda=0.28)
        llave.shift(UP * 0.3)
        cif = tira_bits(CIFRADO_OTP, C_CIFRADO, celda=0.28)
        cif.shift(DOWN * 0.9)

        def letras_sobre(texto):
            g = tira_letras(texto, C_CLARO, font_size=26)
            for i, idx in enumerate((4, 12, 20)):
                g.letra(i).move_to(msg.celda(idx).get_center() + UP * 0.35)
            return g

        letras = letras_sobre(MENSAJE_OTP)

        et_msg = tag_junto(msg, "mensaje", LEFT)
        et_llave = tag_junto(llave, "llave", LEFT)
        et_cif = tag_junto(cif, "cifrado", LEFT)

        oplus = MathTex(r"\oplus", color=C_ACENTO, font_size=34)
        oplus.move_to(np.array([0.0, 0.8, 0.0]))

        # --- momento 1: un mensaje son bits ---------------------------------
        rot.mostrar(pie_curso("Un mensaje son bits: tres letras, "
                              "veinticuatro ceros y unos."), zona="abajo",
                    run_time=0.45)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in msg.celdas],
                              lag_ratio=0.04),
                  FadeIn(et_msg, shift=0.1 * LEFT), run_time=1.4)
        self.play(FadeIn(letras, shift=0.1 * UP), run_time=0.5)
        self.wait(2.5)

        # --- momento 2: la llave y la operacion -----------------------------
        rot.mostrar(pie_curso("Una llave aleatoria, igual de larga, y "
                              "una sola operación: XOR."), zona="abajo")
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in llave.celdas],
                              lag_ratio=0.03),
                  FadeIn(et_llave, shift=0.1 * LEFT), run_time=1.0)
        self.play(FadeIn(oplus, scale=0.7), run_time=0.4)
        self.wait(2.0)

        # --- momento 3: XOR bit a bit, parece ruido -------------------------
        rot.mostrar(pie_curso("Bit a bit: iguales dan cero, distintos dan "
                              "uno. El resultado parece ruido."),
                    zona="abajo")
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in cif.celdas],
                              lag_ratio=0.06),
                  FadeIn(et_cif, shift=0.1 * LEFT), run_time=1.8)
        self.wait(2.0)

        # --- momento 4: XOR de vuelta devuelve el mensaje --------------------
        rot.mostrar(pie_curso("Con la misma llave, XOR otra vez devuelve "
                              "el mensaje."), zona="abajo")
        self.play(Indicate(llave, color=C_LLAVE, scale_factor=1.1),
                  run_time=0.8)
        self.play(Flash(msg, color=C_CLARO, line_length=0.15, num_lines=10,
                        flash_radius=0.32), run_time=0.6)
        self.wait(1.5)

        # --- momento 5: lo perfecto de Shannon --------------------------------
        rot.mostrar(pie_curso("Y aquí lo perfecto: otra llave da otro "
                              "mensaje igual de válido."), zona="abajo")
        letras_2 = letras_sobre(MENSAJE_OTP_2)
        self.play(Transform(msg, msg.con_bits(texto_a_bits(MENSAJE_OTP_2))),
                  Transform(llave, llave.con_bits(LLAVE_OTP_2)),
                  Transform(letras, letras_2),
                  Indicate(cif, color=C_CIFRADO, scale_factor=1.05),
                  run_time=1.2)
        self.wait(1.5)

        # --- momento 6: cuantas llaves, cuantos mensajes -----------------------
        rot.mostrar(pie_curso("Dieciséis millones de llaves, dieciséis "
                              "millones de mensajes: nada que adivinar."),
                    zona="abajo")
        tag_n = tag_hud(f"2^{N_BITS_OTP} llaves = 2^{N_BITS_OTP} mensajes",
                        color=C_LLAVE)
        tag_n.next_to(cif, DOWN, buff=0.30)
        self.play(FadeIn(tag_n, shift=0.1 * UP), run_time=0.5)
        self.wait(2.0)

        # --- cierre ------------------------------------------------------------
        rot.mostrar(pie_curso("Perfecta e impráctica: aleatoria, tan "
                              "larga como el mensaje y de un solo uso."),
                    zona="abajo")
        self.wait(5.0)

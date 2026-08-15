class Clip6(Scene):
    """6 - La huella digital. SHA-256 real (hashlib): un mensaje de
    cualquier tamano se convierte en una huella de 256 bits, dibujada
    como una rejilla 16x16. Cambiar una sola letra ("hola" -> "Hola")
    reparte de nuevo cerca de la mitad de las celdas -- la avalancha,
    CONTADA sobre el dibujo con `.marcar_distintos()`, nunca citada. Y de
    la huella no se recupera el mensaje. Cierre: una huella pequena,
    imposible de falsificar, es la firma de todo lo demas. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La huella digital")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # Geometria: dos rejillas 16x16 lado a lado, centradas en y=-0.1;
        # el mensaje encima de cada una, "SHA-256" debajo de cada una.
        rej1 = rejilla_hash(BITS_HASH, C_HUELLA, celda=0.17)
        rej1.move_to(np.array([-2.4, -0.1, 0.0]))
        rej2 = rejilla_hash(BITS_HASH_2, C_HUELLA, celda=0.17)
        rej2.move_to(np.array([2.4, -0.1, 0.0]))

        msg1 = Text(MENSAJE_HASH, font_size=30, color=C_CLARO)
        msg1.next_to(rej1, UP, buff=0.35)
        msg2 = Text(MENSAJE_HASH_2, font_size=30, color=C_CLARO)
        msg2.next_to(rej2, UP, buff=0.35)
        msg2[0].set_color(C_ATAQUE)   # la letra que cambio

        tag_sha1 = tag_hud("SHA-256", font_size=13, color=C_TENUE)
        tag_sha1.next_to(rej1, DOWN, buff=0.18)
        tag_sha2 = tag_hud("SHA-256", font_size=13, color=C_TENUE)
        tag_sha2.next_to(rej2, DOWN, buff=0.18)
        tag_hex = tag_hud(sha256_hex(MENSAJE_HASH)[:16] + "...",
                          font_size=11, color=C_HUELLA)
        tag_hex.next_to(tag_sha1, DOWN, buff=0.14)

        # --- momento 1: un hash da 256 bits ----------------------------------
        rot.mostrar(pie_curso("Un hash convierte cualquier mensaje en "
                              "una huella de 256 bits."), zona="abajo",
                    run_time=0.45)
        self.play(FadeIn(msg1, shift=0.1 * UP), FadeIn(tag_sha1),
                  LaggedStart(*[FadeIn(c, scale=0.6) for c in rej1.celdas],
                              lag_ratio=0.008), run_time=1.6)
        self.play(FadeIn(tag_hex, shift=0.08 * UP), run_time=0.5)
        self.wait(3.5)

        # --- momento 2: cambia una letra --------------------------------------
        rot.mostrar(pie_curso("Cambia una sola letra..."), zona="abajo")
        self.play(FadeIn(msg2, shift=0.1 * UP), FadeIn(tag_sha2),
                  LaggedStart(*[FadeIn(c, scale=0.6) for c in rej2.celdas],
                              lag_ratio=0.008), run_time=1.6)
        self.wait(2.8)

        # --- momento 3: efecto avalancha ----------------------------------------
        rot.mostrar(pie_curso("...y cambia la mitad de la huella: efecto "
                              "avalancha."), zona="abajo")
        rej2_marcado = rejilla_hash(BITS_HASH_2, C_HUELLA, celda=0.17)
        rej2_marcado.move_to(rej2.get_center())
        n_marcados = rej2_marcado.marcar_distintos(BITS_HASH, C_ATAQUE)
        neq = MathTex(r"\neq", font_size=36, color=C_ATAQUE)
        neq.move_to(np.array([0.0, -0.1, 0.0]))
        tag_cambian = tag_hud(f"{N_BITS_CAMBIAN} de 256 bits cambian",
                              color=C_ATAQUE)
        tag_cambian.move_to(np.array([0.0, -2.15, 0.0]))
        self.play(Transform(rej2, rej2_marcado), run_time=1.8)
        self.play(FadeIn(neq, scale=0.7),
                  FadeIn(tag_cambian, shift=0.1 * UP), run_time=0.6)
        self.wait(2.4)

        # --- momento 4: no hay vuelta atras ---------------------------------------
        rot.mostrar(pie_curso("Y no hay vuelta atrás: de la huella no se "
                              "recupera el mensaje."), zona="abajo")
        tag_no_vuelta = tag_hud("sin vuelta atras", font_size=13,
                                color=C_ATAQUE)
        tag_no_vuelta.move_to(np.array([0.0, -2.55, 0.0]))
        self.play(FadeIn(tag_no_vuelta, shift=0.1 * UP), run_time=0.5)
        self.wait(2.5)

        # --- momento 5: aplicaciones (se limpian los tags antes del cierre) ------
        rot.mostrar(pie_curso("Por eso las contraseñas se guardan como "
                              "huella, y así se vigila que un archivo no "
                              "cambió."), zona="abajo")
        self.play(FadeOut(tag_sha1), FadeOut(tag_sha2), FadeOut(tag_hex),
                  FadeOut(tag_no_vuelta), run_time=0.6)
        self.wait(2.6)

        # --- cierre --------------------------------------------------------------
        rot.mostrar(pie_curso("Una huella pequeña, imposible de "
                              "falsificar: la firma de todo lo demás."),
                    zona="abajo")
        self.wait(5.0)

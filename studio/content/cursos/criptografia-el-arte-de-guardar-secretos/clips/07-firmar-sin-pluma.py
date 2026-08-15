class Clip7(Scene):
    """7 - Firmar sin pluma. Firmar es RSA al reves: Ana cifra la huella h
    del mensaje con su llave PRIVADA d y sale la firma s; cualquiera
    verifica con la publica que s^e mod n vuelve a dar h. Eva cambia un bit
    del mensaje, la huella cambia y la verificacion falla. Cierre: la firma
    prueba autor e integridad. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Firmar sin pluma"), zona="arriba",
                    run_time=0.6)

        # --- geometria ------------------------------------------------------
        # Dos cadenas de 4 cajas apiladas en la banda central: la de Ana
        # arriba (y = +1.05), la de Eva abajo (y = -1.25). Con cajas de 2.0 y
        # separacion 0.5 la cadena mide 9.5 -> x en [-4.75, 4.75], dentro del
        # margen. Los valores cuelgan DEBAJO de cada caja (dos alturas: 0.15
        # y 0.34 de buff) y los tags de llave van ENCIMA, para que nunca se
        # crucen con las cifras.
        Y_ANA, Y_EVA = 1.05, -1.25
        PASOS = ["mensaje", "huella h", "firma s", "verifica"]
        VER_ANA = potencia_mod(S_FIRMA, E_RSA, N_RSA)
        # La verdad la dice la libreria, no el guion.
        OK_ANA = "OK" if FIRMA_OK else "FALLA"
        COL_ANA = C_LLAVE if FIRMA_OK else C_ATAQUE
        OK_EVA = "OK" if FIRMA_ALTERADA_OK else "FALLA"
        COL_EVA = C_LLAVE if FIRMA_ALTERADA_OK else C_ATAQUE

        ana = flujo(PASOS, [C_CLARO, C_HUELLA, C_CLARO, C_TENUE],
                    ancho_caja=2.0, alto_caja=0.66, sep=0.5, font_size=17)
        ana.shift(UP * Y_ANA)
        eva = flujo(PASOS, [C_ATAQUE, C_HUELLA, C_CLARO, C_TENUE],
                    ancho_caja=2.0, alto_caja=0.66, sep=0.5, font_size=17)
        eva.shift(UP * Y_EVA)

        def valor(caja, texto, color, font_size=13, buff=0.15):
            t = tag_hud(texto, font_size=font_size, color=color)
            t.next_to(caja, DOWN, buff=buff)
            return t

        v_msg = valor(ana.caja(0), f'"{MENSAJE_HASH}"', C_CLARO)
        v_h = valor(ana.caja(1), f"h = {H_FIRMA}", C_HUELLA)
        v_s = valor(ana.caja(2), f"s = {S_FIRMA}", C_CLARO)
        nota_h = tag_hud("juguete: sha256 mod n", font_size=11, color=C_TENUE)
        nota_h.next_to(v_h, DOWN, buff=0.10)
        nota_s = tag_hud("s = h^d mod n", font_size=11, color=C_TENUE)
        nota_s.next_to(v_s, DOWN, buff=0.10)
        t_priv = tag_hud(f"d = {D_RSA} (privada)", font_size=12, color=C_CLARO)
        t_priv.next_to(ana.caja(2), UP, buff=0.16)

        # --- momento 1: firmar es cifrar la huella con la privada -----------
        rot.mostrar(pie_curso("Firmar es RSA al revés: cifrar la huella con "
                              "la llave privada."), zona="abajo",
                    run_time=0.45)
        self.play(LaggedStart(FadeIn(ana.caja(0), scale=0.9),
                              Create(ana.flecha(0)),
                              FadeIn(ana.caja(1), scale=0.9),
                              Create(ana.flecha(1)),
                              FadeIn(ana.caja(2), scale=0.9),
                              lag_ratio=0.55), run_time=2.1)
        self.play(FadeIn(v_msg, shift=0.10 * UP), FadeIn(v_h, shift=0.10 * UP),
                  FadeIn(nota_h), run_time=0.6)
        self.play(FadeIn(t_priv, shift=0.10 * DOWN),
                  FadeIn(v_s, shift=0.10 * UP), FadeIn(nota_s), run_time=0.6)
        self.wait(3.0)

        # --- momento 2: cualquiera verifica con la publica ------------------
        rot.mostrar(pie_curso("Cualquiera verifica con la pública: s elevado "
                              "a e da la huella."), zona="abajo")
        v_ver = valor(ana.caja(3), f"s^e mod n = {VER_ANA}", C_TENUE,
                      font_size=12)
        t_ok = tag_hud(OK_ANA, font_size=16, color=COL_ANA)
        t_ok.next_to(ana.caja(3), UP, buff=0.16)
        formula = MathTex(r"s^{e} \bmod n = h", font_size=26, color=COL_ANA)
        formula.move_to(np.array([0.0, -0.28, 0.0]))
        self.play(Create(ana.flecha(2)), FadeIn(v_ver, shift=0.10 * UP),
                  run_time=0.7)
        self.play(ana.caja(3)[0].animate.set_stroke(COL_ANA).set_fill(
                      COL_ANA, opacity=0.10),
                  ana.caja(3)[1].animate.set_color(COL_ANA),
                  v_ver.animate.set_color(COL_ANA),
                  FadeIn(t_ok, shift=0.10 * DOWN), run_time=0.8)
        self.play(FadeIn(formula, shift=0.10 * UP), run_time=0.5)
        self.wait(3.2)

        # --- momento 3: Eva cambia un bit -----------------------------------
        rot.mostrar(pie_curso("Eva cambia un solo bit del mensaje…"),
                    zona="abajo")
        # La formula sale ANTES de que baje la cadena de Eva: ese sitio es
        # suyo a partir de aqui.
        self.play(FadeOut(formula), run_time=0.3)
        v_msg2 = valor(eva.caja(0), f'"{MENSAJE_ALTERADO}"', C_ATAQUE)
        nota_msg2 = tag_hud("1 bit distinto", font_size=11, color=C_ATAQUE)
        nota_msg2.next_to(v_msg2, DOWN, buff=0.10)
        v_h2 = valor(eva.caja(1), f"h = {H_ALTERADA}", C_ATAQUE)
        nota_h2 = tag_hud("otra huella", font_size=11, color=C_TENUE)
        nota_h2.next_to(v_h2, DOWN, buff=0.10)
        v_s2 = valor(eva.caja(2), f"s = {S_FIRMA}", C_CLARO)
        nota_s2 = tag_hud("la misma firma", font_size=11, color=C_TENUE)
        nota_s2.next_to(v_s2, DOWN, buff=0.10)
        self.play(LaggedStart(FadeIn(eva.caja(0), scale=0.9),
                              Create(eva.flecha(0)),
                              FadeIn(eva.caja(1), scale=0.9),
                              Create(eva.flecha(1)),
                              FadeIn(eva.caja(2), scale=0.9),
                              lag_ratio=0.5), run_time=1.8)
        self.play(FadeIn(v_msg2, shift=0.10 * UP), FadeIn(nota_msg2),
                  FadeIn(v_s2, shift=0.10 * UP), FadeIn(nota_s2),
                  run_time=0.5)
        self.play(FadeIn(v_h2, shift=0.10 * UP), FadeIn(nota_h2), run_time=0.5)
        self.play(Flash(v_h2, color=C_ATAQUE, line_length=0.16, num_lines=10,
                        flash_radius=0.45), run_time=0.6)
        self.wait(2.6)

        # --- momento 4: la firma ya no encaja -------------------------------
        rot.mostrar(pie_curso("…y la firma ya no encaja: la verificación "
                              "falla."), zona="abajo")
        v_ver2 = valor(eva.caja(3), f"s^e mod n = {VER_ANA}", C_TENUE,
                       font_size=12)
        t_falla = tag_hud(OK_EVA, font_size=16, color=COL_EVA)
        t_falla.next_to(v_ver2, DOWN, buff=0.12)
        marco = eva.caja(3)[0]
        r = 0.26
        cruz = VGroup(
            Line(marco.get_center() + np.array([-r, -r, 0.0]),
                 marco.get_center() + np.array([r, r, 0.0]),
                 stroke_width=4.0, color=COL_EVA),
            Line(marco.get_center() + np.array([-r, r, 0.0]),
                 marco.get_center() + np.array([r, -r, 0.0]),
                 stroke_width=4.0, color=COL_EVA))
        self.play(Create(eva.flecha(2)), FadeIn(v_ver2, shift=0.10 * UP),
                  run_time=0.6)
        self.play(marco.animate.set_stroke(COL_EVA).set_fill(COL_EVA,
                                                             opacity=0.10),
                  eva.caja(3)[1].animate.set_color(COL_EVA),
                  v_ver2.animate.set_color(COL_EVA), run_time=0.6)
        # El rotulo de la caja SALE cuando entra la cruz: la cruz ocupa su
        # sitio, no se le encima.
        self.play(FadeOut(eva.caja(3)[1]), Create(cruz),
                  FadeIn(t_falla, shift=0.10 * UP), run_time=0.7)
        self.play(Flash(marco, color=COL_EVA, line_length=0.18, num_lines=12,
                        flash_radius=0.6), run_time=0.6)
        self.wait(2.4)

        # --- cierre ---------------------------------------------------------
        rot.mostrar(pie_curso("La firma prueba dos cosas: quién lo escribió "
                              "y que nadie lo tocó."), zona="abajo")
        self.wait(5.0)

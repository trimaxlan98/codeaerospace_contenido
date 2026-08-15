class Clip8(Scene):
    """8 - El candado del navegador. Recapitulacion del curso en el apreton
    de manos TLS: Diffie-Hellman acuerda la llave de sesion, la firma RSA
    prueba quien es el servidor, un cifrado simetrico protege el volumen y
    el hash cuida la integridad. El mismo candado va en el enlace con el
    satelite. Cierre honesto: Shor rompe RSA y DH con una computadora
    cuantica grande que aun no existe, y el relevo post-cuantico ya esta
    aqui. Pantalla final: «Un secreto no se esconde. / Se calcula.» (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El candado del navegador"), zona="arriba",
                    run_time=0.6)

        # --- geometria ------------------------------------------------------
        # El candado en la columna izquierda (x = -4.5); a su derecha una
        # columna de miniaturas (x = -2.6, todas de menos de 0.7 de ancho) y
        # las filas de texto alineadas por la izquierda en x = -2.05. Cuatro
        # filas separadas 0.77 mas una quinta (el aviso cuantico) mas abajo:
        # nada baja de y = -2.3, muy por encima del pie.
        X_ICONO, X_TEXTO = -2.6, -2.05
        Y_FILAS = [1.58, 0.81, 0.04, -0.73]

        cand = candado(C_CIFRADO, alto=1.3)
        cand.move_to(np.array([-4.5, 0.35, 0.0]))
        cand.cerrado()
        p_cerrado = cand.arco.get_center()      # se guarda ANTES de abrirlo
        cand.abierto()

        def fila(i, texto, color):
            t = Text(texto, font_size=22, color=color)
            t.move_to(np.array([0.0, Y_FILAS[i], 0.0]))
            t.align_to(np.array([X_TEXTO, 0.0, 0.0]), LEFT)
            return t

        def icono(i, pieza):
            pieza.move_to(np.array([X_ICONO, Y_FILAS[i], 0.0]))
            return pieza

        f1 = fila(0, "1  Diffie–Hellman: llave de sesión", C_LLAVE)
        f2 = fila(1, "2  firma RSA: quién es el servidor", C_HUELLA)
        f3 = fila(2, "3  AES: cifra todo el tráfico", C_CIFRADO)
        f4 = fila(3, "4  hash: integridad de cada byte", C_HUELLA)
        i1 = icono(0, grafo_llaves(6).scale(0.22))
        i2 = icono(1, rejilla_hash(BITS_HASH, C_HUELLA, celda=0.042))
        i3 = icono(2, tira_bits(CIFRADO_OTP[:8], C_CIFRADO, celda=0.08))
        i4 = icono(3, tira_bits(BITS_HASH[:8], C_HUELLA, celda=0.08))

        # --- momento 1: todo esto pasa en un parpadeo -----------------------
        rot.mostrar(pie_curso("Al abrir una página segura, todo esto pasa en "
                              "un parpadeo."), zona="abajo", run_time=0.45)
        self.play(FadeIn(cand, scale=0.85), run_time=0.7)
        self.wait(2.2)

        # --- momento 2: Diffie-Hellman --------------------------------------
        rot.mostrar(pie_curso("Uno: Diffie–Hellman acuerda la llave de "
                              "sesión."), zona="abajo")
        self.play(FadeIn(i1, scale=0.8), FadeIn(f1, shift=0.14 * RIGHT),
                  run_time=0.8)
        self.wait(2.9)

        # --- momento 3: la firma RSA ----------------------------------------
        rot.mostrar(pie_curso("Dos: la firma RSA prueba quién es el "
                              "servidor."), zona="abajo")
        self.play(FadeIn(i2, scale=0.8), FadeIn(f2, shift=0.14 * RIGHT),
                  run_time=0.8)
        self.wait(2.9)

        # --- momento 4: cifrado simetrico + hash, y el candado cierra -------
        rot.mostrar(pie_curso("Tres: un cifrado simétrico rápido protege el "
                              "volumen; cuatro: el hash cuida cada byte."),
                    zona="abajo")
        self.play(FadeIn(i3, scale=0.8), FadeIn(f3, shift=0.14 * RIGHT),
                  run_time=0.7)
        self.play(FadeIn(i4, scale=0.8), FadeIn(f4, shift=0.14 * RIGHT),
                  run_time=0.7)
        self.play(cand.arco.animate.move_to(p_cerrado).set_color(C_LLAVE),
                  cand.cuerpo.animate.set_color(C_LLAVE).set_fill(
                      C_LLAVE, opacity=0.14), run_time=0.8)
        self.play(Flash(cand.cuerpo, color=C_LLAVE, line_length=0.20,
                        num_lines=14, flash_radius=0.75), run_time=0.6)
        self.wait(2.6)

        # --- momento 5: el mismo candado en el enlace satelital -------------
        rot.mostrar(pie_curso("El mismo candado va en el enlace con el "
                              "satélite."), zona="abajo")
        sat = Dot(np.array([-4.5, 2.42, 0.0]), radius=0.10, color=C_CIFRADO)
        t_sat = tag_hud("satelite", font_size=13, color=C_CIFRADO)
        t_sat.next_to(sat, UP, buff=0.14)
        enlace = DashedLine(cand.arco.get_top() + UP * 0.12,
                            sat.get_bottom() + DOWN * 0.06,
                            stroke_width=1.8, color=C_CIFRADO,
                            dash_length=0.10)
        enlace.set_stroke(opacity=0.55)
        t_canal = tag_hud("mismo candado, otro canal", font_size=12,
                          color=C_TENUE)
        t_canal.next_to(cand.cuerpo, DOWN, buff=0.26)
        self.play(Create(enlace), FadeIn(sat, scale=0.7), FadeIn(t_sat),
                  run_time=0.8)
        self.play(FadeIn(t_canal, shift=0.10 * UP), run_time=0.4)
        self.wait(2.3)

        # --- momento 6: la amenaza cuantica y su relevo ---------------------
        rot.mostrar(pie_curso("Shor rompería RSA y DH con una computadora "
                              "cuántica grande, que aún no existe."),
                    zona="abajo")
        f5 = Text("Shor (1994): rompe RSA y DH — si la máquina existiera",
                  font_size=19, color=C_ATAQUE)
        f5.move_to(np.array([0.0, -1.62, 0.0]))
        f5.align_to(np.array([X_TEXTO, 0.0, 0.0]), LEFT)
        self.play(FadeIn(f5, shift=0.14 * RIGHT), run_time=0.7)
        self.wait(2.4)

        rot.mostrar(pie_curso("El relevo ya está aquí: criptografía "
                              "post-cuántica."), zona="abajo")
        t_pqc = tag_hud("ML-KEM - NIST 2024", font_size=15, color=C_LLAVE)
        t_pqc.next_to(f5, DOWN, buff=0.24)
        t_pqc.align_to(f5, LEFT)
        self.play(FadeIn(t_pqc, shift=0.12 * UP), run_time=0.6)
        self.wait(2.4)

        # --- cierre: pantalla limpia ----------------------------------------
        rot.limpiar("abajo", run_time=0.35)
        rot.limpiar("arriba", run_time=0.35)
        todo = VGroup(cand, i1, i2, i3, i4, f1, f2, f3, f4, f5, t_pqc,
                      sat, t_sat, enlace, t_canal)
        self.play(FadeOut(todo), run_time=0.8)

        cierre_1 = Text("Un secreto no se esconde.", font_size=40,
                        color=C_TITULO)
        cierre_1.move_to(np.array([0.0, 0.45, 0.0]))
        cierre_2 = Text("Se calcula.", font_size=44, color=C_CIFRADO)
        cierre_2.next_to(cierre_1, DOWN, buff=0.45)
        self.play(FadeIn(cierre_1, shift=0.14 * UP), run_time=0.7)
        self.play(FadeIn(cierre_2, shift=0.14 * UP), run_time=0.7)
        self.wait(5.0)

class Clip4(Scene):
    """4 - Gritar en publico. Repartir llaves secretas por pares no escala:
    n(n-1)/2, de 45 con diez personas a 499 500 con mil. En 1976 Diffie y
    Hellman acuerdan un secreto hablando SOLO en publico: con p=23 y g=5,
    Ana grita 8, Beto grita 19 y a los dos les sale el mismo 2, que nunca
    viajo. Eva lo oye todo y se queda con el logaritmo discreto. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Gritar en público"), zona="arriba",
                    run_time=0.6)

        # --- momento: el problema de repartir llaves -----------------------
        # El grafo completo a la izquierda (banda central), la cuenta a la
        # derecha; la formula queda BAJO el grafo, lejos del pie.
        rot.mostrar(pie_curso("Diez personas: cuarenta y cinco llaves "
                              "secretas. Mil: medio millón."), zona="abajo")
        grafo = grafo_llaves(10).shift(LEFT * 3.3 + UP * 0.15)
        cuenta = VGroup(
            tag_hud(f"10 personas: {LLAVES_10} llaves", font_size=19,
                    color=C_LLAVE),
            tag_hud(f"100 personas: {LLAVES_100:,} llaves".replace(",", " "),
                    font_size=19, color=C_LLAVE),
            tag_hud(f"1000 personas: {LLAVES_1000:,} llaves".replace(",", " "),
                    font_size=19, color=C_ATAQUE),
        ).arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        cuenta.move_to(RIGHT * 2.7 + UP * 0.15)
        formula = MathTex(r"\frac{n(n-1)}{2}", font_size=40, color=C_TENUE)
        formula.next_to(grafo.nodos, DOWN, buff=0.34)

        self.play(LaggedStart(*[FadeIn(d, scale=0.6) for d in grafo.nodos],
                              lag_ratio=0.06), run_time=1.0)
        self.play(LaggedStart(*[Create(a) for a in grafo.aristas],
                              lag_ratio=0.02), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(t, shift=0.12 * UP) for t in cuenta],
                              lag_ratio=0.35), run_time=0.9)
        self.play(Write(formula), run_time=0.6)
        self.wait(2.6)
        self.play(FadeOut(grafo), FadeOut(cuenta), FadeOut(formula),
                  run_time=0.5)

        # --- momento: 1976, el acuerdo en publico --------------------------
        # El esquema sube 0.55 para dejar sitio a las cajas privadas bajo
        # Ana y Beto. La linea punteada de Eva NO entra todavia: ocuparia el
        # carril por el que pasa el mensaje de Beto (x = 0, bajo el canal).
        rot.mostrar(pie_curso("1976: acordar un secreto hablando solo en "
                              "público."), zona="abajo")
        # sep=4.6 (y no el 4.2 por omision): con la separacion corta los
        # mensajes posados alcanzaban a Beto y a la caja "privado a".
        esq = esquema_dh(sep=4.6).shift(UP * 0.55)
        publicos = tag_hud(f"p = {P_DH}   g = {G_DH}", font_size=17,
                           color=C_CIFRADO)
        publicos.move_to(esq.canal.get_center() + UP * 0.90)
        self.play(FadeIn(esq.ana), FadeIn(esq.beto), Create(esq.canal),
                  run_time=0.9)
        self.play(FadeIn(esq.eva, shift=0.15 * UP),
                  FadeIn(publicos, shift=0.12 * UP), run_time=0.6)
        self.wait(3.4)

        # --- momento: cada uno grita una potencia --------------------------
        rot.mostrar(pie_curso("Cada uno elige un número privado y grita una "
                              "potencia."), zona="abajo")
        caja_a = caja_numero("privado a", str(A_DH), C_CLARO, ancho=1.5)
        caja_a.move_to(esq.ana.get_center() + DOWN * 1.17)
        caja_b = caja_numero("privado b", str(B_DH), C_CLARO, ancho=1.5)
        caja_b.move_to(esq.beto.get_center() + DOWN * 1.17)
        self.play(FadeIn(caja_a, shift=0.12 * UP),
                  FadeIn(caja_b, shift=0.12 * UP), run_time=0.7)

        # Carril de ida POR ENCIMA del canal, carril de vuelta POR DEBAJO:
        # asi los dos mensajes quedan posados sin tocarse. Los extremos van
        # a x = +-2.40 (no al punto de la libreria, que deja el texto sobre
        # el circulo del destinatario) y el texto baja a 0.62 de escala.
        y_canal = esq.canal.get_center()[1]
        x_grito = 2.40
        ida = np.array([x_grito, y_canal + 0.50, 0.0])
        vuelta = np.array([x_grito, y_canal - 0.42, 0.0])
        msg_a = esq.mensaje(f"A = {G_DH}^{A_DH} mod {P_DH} = {DH['A']}",
                            desde="ana")
        msg_a.scale(0.62).move_to(ida * np.array([-1.0, 1.0, 1.0]))
        self.play(FadeIn(msg_a), run_time=0.35)
        self.play(msg_a.animate.move_to(ida), run_time=1.5)
        msg_b = esq.mensaje(f"B = {G_DH}^{B_DH} mod {P_DH} = {DH['B']}",
                            desde="beto")
        msg_b.scale(0.62).move_to(vuelta)
        self.play(FadeIn(msg_b), run_time=0.35)
        self.play(msg_b.animate.move_to(vuelta * np.array([-1.0, 1.0, 1.0])),
                  run_time=1.5)
        self.wait(1.6)

        # --- momento: a los dos les sale lo mismo --------------------------
        rot.mostrar(pie_curso("Cada uno eleva lo que recibió a su secreto y "
                              "sale lo mismo."), zona="abajo")
        sec_a = caja_numero("secreto", str(DH["s_ana"]), C_CLARO, ancho=1.5)
        sec_a.move_to(caja_a.get_center() + DOWN * 1.48)
        sec_b = caja_numero("secreto", str(DH["s_beto"]), C_CLARO, ancho=1.5)
        sec_b.move_to(caja_b.get_center() + DOWN * 1.48)
        op_a = tag_hud(f"{DH['B']}^{A_DH} mod {P_DH}", font_size=14,
                       color=C_TENUE)
        op_a.move_to((caja_a.get_bottom() + sec_a.get_top()) / 2.0)
        op_b = tag_hud(f"{DH['A']}^{B_DH} mod {P_DH}", font_size=14,
                       color=C_TENUE)
        op_b.move_to((caja_b.get_bottom() + sec_b.get_top()) / 2.0)
        self.play(FadeIn(op_a), FadeIn(op_b), run_time=0.5)
        self.play(FadeIn(sec_a, shift=0.12 * UP),
                  FadeIn(sec_b, shift=0.12 * UP), run_time=0.8)
        self.play(Flash(sec_a.valor, color=C_CLARO, line_length=0.18,
                        num_lines=12, flash_radius=0.42),
                  Flash(sec_b.valor, color=C_CLARO, line_length=0.18,
                        num_lines=12, flash_radius=0.42), run_time=0.7)
        # Bajo Eva y centrado: entre el canal y Eva no cabe (ahi va luego la
        # punteada) y a los lados estan las cajas.
        mismo = tag_hud(f"el mismo {DH['s_ana']}, y nunca viajo",
                        font_size=15, color=C_LLAVE)
        mismo.move_to(esq.eva.get_center() + DOWN * 0.92)
        self.play(FadeIn(mismo, shift=0.10 * UP), run_time=0.5)
        self.wait(2.4)

        # --- cierre: lo que le queda a Eva ---------------------------------
        rot.mostrar(pie_curso(f"Eva ve {P_DH}, {G_DH}, {DH['A']} y "
                              f"{DH['B']}: con {DIGITOS_RSA_2048} dígitos no "
                              f"le alcanza el universo."), zona="abajo")
        duda = tag_hud("?", font_size=30, color=C_ATAQUE)
        duda.next_to(esq.eva, RIGHT, buff=0.24)
        log = tag_hud("logaritmo discreto", font_size=13, color=C_ATAQUE)
        log.next_to(esq.eva, LEFT, buff=0.28)
        self.play(Create(esq.eva_linea), run_time=0.6)
        self.play(FadeIn(duda, scale=0.6), FadeIn(log), run_time=0.6)
        self.wait(5.0)

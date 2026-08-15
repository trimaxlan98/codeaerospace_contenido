class Clip5(Scene):
    """5 - Multiplicar es facil, factorizar no. RSA de juguete: 61 x 53 da
    3233 en un parpadeo; con la publica (n, e) cualquiera cierra (65 ->
    2790) y solo la privada d abre (2790 -> 65). Para hallar d hay que
    factorizar: 3233 cae en 16 divisiones MEDIDAS, pero la cuenta crece
    como 10^(d/2) y con 617 digitos pide 10^308. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Multiplicar es fácil, factorizar no"),
                    zona="arriba", run_time=0.6)

        # Las cinco cajas viven en la banda superior-central (y = +1.45):
        # 5 x 1.65 de ancho con paso 1.95 ocupan de -4.72 a 4.72, dentro del
        # margen y lejos de la marca de agua. La banda central de abajo
        # queda libre para las formulas, el contador y la curva.
        ancho_caja, paso, y_fila = 1.65, 1.95, 1.45
        caja_p = caja_numero("p", str(P_RSA), C_CLARO, ancho=ancho_caja)
        caja_q = caja_numero("q", str(Q_RSA), C_CLARO, ancho=ancho_caja)
        caja_n = caja_numero("n = p x q", str(N_RSA), C_CIFRADO,
                             ancho=ancho_caja)
        caja_e = caja_numero("e", str(E_RSA), C_CIFRADO, ancho=ancho_caja)
        caja_d = caja_numero("d", str(D_RSA), C_CLARO, ancho=ancho_caja)
        for i, caja in enumerate((caja_p, caja_q, caja_n, caja_e, caja_d)):
            caja.move_to(RIGHT * (i - 2) * paso + UP * y_fila)

        # --- momento: el candado que cualquiera cierra ---------------------
        rot.mostrar(pie_curso("1977: un candado que cualquiera cierra y solo "
                              "Ana abre."), zona="abajo")
        cand = candado(C_CIFRADO, alto=1.3)
        cand.cerrado().move_to(LEFT * 4.9 + DOWN * 0.70)
        self.play(FadeIn(cand, shift=0.15 * UP), run_time=0.6)
        self.play(FadeIn(caja_p, shift=0.12 * UP),
                  FadeIn(caja_q, shift=0.12 * UP), run_time=0.7)
        t_sec = tag_junto(VGroup(caja_p, caja_q), "secretos", DOWN, buff=0.18,
                          font_size=17, color=C_CLARO)
        self.play(FadeIn(t_sec), run_time=0.4)
        mult = MathTex(str(P_RSA), r"\times", str(Q_RSA), "=", str(N_RSA),
                       font_size=46, color=C_TENUE)
        mult[0].set_color(C_CLARO)
        mult[2].set_color(C_CLARO)
        mult[4].set_color(C_CIFRADO)
        mult.move_to(DOWN * 0.70)
        self.play(Write(mult), run_time=1.0)
        self.wait(0.8)
        self.play(ReplacementTransform(mult, caja_n), run_time=1.0)
        t_pub = tag_junto(caja_n, "público", DOWN, buff=0.18, font_size=17,
                          color=C_CIFRADO)
        self.play(FadeIn(t_pub), run_time=0.4)
        self.wait(1.4)

        # --- momento: cifrar con la llave publica ---------------------------
        rot.mostrar(pie_curso(f"Con la llave pública cualquiera cifra: "
                              f"{M_RSA} se vuelve {C_RSA}."), zona="abajo")
        self.play(FadeOut(cand), FadeIn(caja_e, shift=0.12 * UP),
                  FadeIn(caja_d, shift=0.12 * UP), run_time=0.7)
        t_pub_e = tag_junto(caja_e, "pública", DOWN, buff=0.18, font_size=17,
                            color=C_CIFRADO)
        t_priv = tag_junto(caja_d, "privada", DOWN, buff=0.18, font_size=17,
                           color=C_CLARO)
        self.play(FadeIn(t_pub_e), FadeIn(t_priv), run_time=0.4)
        eq1 = MathTex(str(M_RSA),
                      r"^{%d} \bmod %d =" % (E_RSA, N_RSA),
                      str(C_RSA), font_size=48, color=C_TENUE)
        eq1[0].set_color(C_CLARO)
        eq1[2].set_color(C_CIFRADO)
        eq1.move_to(DOWN * 0.55)
        self.play(Write(eq1), run_time=1.3)
        self.wait(3.0)

        # --- momento: solo la privada deshace -------------------------------
        rot.mostrar(pie_curso(f"Solo la privada deshace: {C_RSA} vuelve a "
                              f"ser {M_RSA_VUELTA}."), zona="abajo")
        eq2 = MathTex(str(C_RSA),
                      r"^{%d} \bmod %d =" % (D_RSA, N_RSA),
                      str(M_RSA_VUELTA), font_size=48, color=C_TENUE)
        eq2[0].set_color(C_CIFRADO)
        eq2[2].set_color(C_CLARO)
        eq2.move_to(DOWN * 0.55)
        self.play(ReplacementTransform(eq1, eq2), run_time=1.2)
        self.wait(3.6)

        # --- momento: a Eva solo le queda dividir ---------------------------
        rot.mostrar(pie_curso("Eva conoce n y e: para hallar d necesita p y "
                              "q. Solo dividir."), zona="abajo")
        self.play(FadeOut(eq2), run_time=0.4)

        # Los primos que se prueban: se generan por criba de divisiones y se
        # cortan en DIVISIONES_3233 (MEDIDO por la libreria), asi que el
        # ultimo es forzosamente el factor 53.
        primos, k = [], 2
        while len(primos) < DIVISIONES_3233:
            if all(k % q for q in primos):
                primos.append(k)
            k += 1

        curva = curva_divisiones().scale(0.8)
        curva.move_to(RIGHT * 3.15 + DOWN * 1.30)
        et_x = tag_junto(curva.etiquetas_x, "dígitos de n", DOWN, buff=0.14,
                         font_size=14)
        et_y = tag_junto(curva.ejes[1], "divisiones", UP, buff=0.16,
                         font_size=14)
        self.play(Create(curva.ejes), FadeIn(curva.ticks),
                  FadeIn(curva.etiquetas_x), FadeIn(et_x), FadeIn(et_y),
                  run_time=0.8)
        self.play(Create(curva.curva), run_time=1.3)

        def panel(i):
            a = tag_hud(f"divide entre {primos[i]}", font_size=21,
                        color=C_ATAQUE)
            b = tag_hud(f"divisiones: {i + 1}", font_size=21, color=C_ATAQUE)
            g = VGroup(a, b).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
            g.move_to(LEFT * 3.6 + DOWN * 1.20)
            return g

        cont = panel(0)
        self.play(FadeIn(cont), run_time=0.4)
        for i in range(1, DIVISIONES_3233):
            self.play(Transform(cont, panel(i)), run_time=0.11)
        halla = tag_hud(f"{DIVISIONES_3233} primos probados -> {Q_RSA}",
                        font_size=21, color=C_LLAVE)
        halla.move_to(cont.get_center())
        self.play(ReplacementTransform(cont, halla),
                  Flash(caja_q, color=C_LLAVE, line_length=0.20,
                        num_lines=14, flash_radius=1.05), run_time=0.7)
        self.wait(1.3)

        # --- momento: la cuenta que no perdona ------------------------------
        rot.mostrar(pie_curso(f"Con {DIGITOS_RSA_2048} dígitos: más "
                              f"divisiones que átomos en el universo."),
                    zona="abajo")
        # Las dos marcas van ARRIBA de la recta (el eje y ya es log10, asi
        # que la curva es una diagonal y el triangulo superior queda libre).
        p_bajo = curva.en(4)
        t_bajo = tag_hud(f"4 digitos: {DIVISIONES_3233}", font_size=15,
                         color=C_CLARO)
        # La recta sube 0.52 por unidad: el rotulo tiene que quedar por
        # encima de ella tambien en su extremo DERECHO, de ahi el +1.55.
        t_bajo.move_to(p_bajo + RIGHT * 1.35 + UP * 1.55)
        guia = DashedLine(p_bajo, t_bajo.get_bottom() + DOWN * 0.04,
                          stroke_width=1.2, color=C_CLARO, dash_length=0.08)
        guia.set_stroke(opacity=0.45)
        m_bajo = VGroup(Dot(p_bajo, radius=0.065, color=C_CLARO), guia,
                        t_bajo)
        p_alto = curva.en(DIGITOS_RSA_2048)
        t_alto = VGroup(
            MathTex(r"10^{%d}" % int(EXP_2048), font_size=30, color=C_ATAQUE),
            tag_hud(f"{DIGITOS_RSA_2048} digitos", font_size=14,
                    color=C_ATAQUE),
        ).arrange(DOWN, buff=0.10)
        t_alto.move_to(p_alto + LEFT * 1.25 + UP * 0.18)
        m_alto = VGroup(Dot(p_alto, radius=0.075, color=C_ATAQUE), t_alto)
        self.play(FadeIn(m_bajo, shift=0.10 * UP), run_time=0.6)
        self.play(FadeIn(m_alto, shift=0.10 * UP), run_time=0.7)
        self.wait(3.6)

        # --- cierre ---------------------------------------------------------
        rot.mostrar(pie_curso("Multiplicar es fácil. Factorizar, no. De eso "
                              "vive tu candado."), zona="abajo")
        self.wait(5.0)

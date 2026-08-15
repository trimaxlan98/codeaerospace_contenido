class Clip1(Scene):
    """1 - La rueda de Cesar. Un mensaje ambar y una rueda de dos anillos:
    el exterior gira 3 posiciones y cada letra se cambia por la de enfrente
    (cifrado cian). Eva no necesita ingenio: solo hay 25 llaves, las prueba
    todas y en el desplazamiento 3 el texto se vuelve legible (verde).
    Cierre: una llave que se puede enumerar no es una llave. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("La rueda de César"), zona="arriba",
                    run_time=0.6)

        # Geometria del clip: la rueda ocupa toda la mitad izquierda de la
        # banda central (radio ~1.96 tras el 0.85, asi que va de x=-5.41 a
        # x=-1.49 y de y=-1.76 a y=+2.16); a la derecha, las dos tiras de
        # letras alineadas columna a columna (x de -0.13 a 5.93) y, debajo,
        # la columna de intentos de Eva. El pie vive en y=-3.02 o mas abajo.
        rueda = rueda_cesar().scale(0.85)
        rueda.move_to(np.array([-3.45, 0.20, 0.0]))

        claro = tira_letras(MENSAJE_CESAR, C_CLARO, font_size=22)
        claro.move_to(np.array([2.90, 0.92, 0.0]))
        cifrado = tira_letras(CIFRADO_CESAR, C_CIFRADO, font_size=22)
        # Alineacion columna a columna: la celda de la primera letra manda
        # (el bounding box de tinta de "N" y "Q" no mide lo mismo).
        cifrado.shift(claro.letras[0].get_center()
                      - cifrado.letras[0].get_center() + DOWN * 0.72)

        et_claro = tag_junto(claro, "mensaje en claro", UP, buff=0.24,
                             font_size=17, color=C_CLARO)
        et_cifrado = tag_junto(cifrado, f"cifrado con llave {DESPLAZAMIENTO}",
                               DOWN, buff=0.24, font_size=17, color=C_CIFRADO)

        y_columna, y_ganador = -1.48, -2.22

        def intento(k, color, y):
            """Un descifrado de prueba, ya colocado: `cesar(c, 26-k)` deshace
            un Cesar de llave k. ASCII puro (Space Mono)."""
            t = tag_hud(f"intento {k:02d}: "
                        f"{cesar(CIFRADO_CESAR, len(ALFABETO) - k)}",
                        font_size=17, color=color)
            t.move_to(np.array([2.90, y, 0.0]))
            return t

        # --- momento: un mensaje y una llave -------------------------------
        rot.mostrar(pie_curso("Un mensaje, una llave: mover cada letra "
                              f"{DESPLAZAMIENTO} lugares."), zona="abajo",
                    run_time=0.45)
        self.play(Create(rueda.circulo_ext), Create(rueda.circulo_int),
                  run_time=0.8)
        self.play(LaggedStart(*[FadeIn(l, scale=0.5)
                                for l in rueda.interior], lag_ratio=0.025),
                  LaggedStart(*[FadeIn(l, scale=0.5)
                                for l in rueda.exterior], lag_ratio=0.025),
                  run_time=1.5)
        self.play(FadeIn(et_claro, shift=0.10 * UP),
                  LaggedStart(*[FadeIn(l, shift=0.10 * DOWN)
                                for l in claro.letras], lag_ratio=0.05),
                  run_time=1.5)
        self.play(rueda.girar(DESPLAZAMIENTO), run_time=1.4)
        self.wait(2.8)

        # --- momento: cada letra por la de enfrente -------------------------
        rot.mostrar(pie_curso("Cada letra se cambia por la de enfrente."),
                    zona="abajo")
        self.play(Indicate(rueda.letra_exterior(MENSAJE_CESAR[0]),
                           color=C_CLARO, scale_factor=1.9),
                  Indicate(rueda.letra_interior(CIFRADO_CESAR[0]),
                           color=C_CIFRADO, scale_factor=1.9),
                  Indicate(claro.letra(0), color=C_CLARO, scale_factor=1.6),
                  run_time=0.9)
        self.play(FadeIn(et_cifrado, shift=0.10 * DOWN),
                  LaggedStart(*[FadeIn(l, scale=0.6)
                                for l in cifrado.letras], lag_ratio=0.07),
                  run_time=1.9)
        self.wait(3.2)

        # --- momento: Eva enumera las 25 llaves -----------------------------
        rot.mostrar(pie_curso("Eva no necesita ingenio: solo hay "
                              f"{N_LLAVES_CESAR} llaves."), zona="abajo")
        rodando = intento(1, C_ATAQUE, y_columna)
        self.play(FadeIn(rodando), run_time=0.28)
        self.play(Transform(rodando, intento(2, C_ATAQUE, y_columna)),
                  run_time=0.26)
        # El desplazamiento 3 es el unico que devuelve espanol: se para, se
        # pone verde y baja a su propia linea mientras Eva sigue probando.
        self.play(Transform(rodando,
                            intento(DESPLAZAMIENTO, C_ATAQUE, y_columna)),
                  run_time=0.30)
        self.play(rodando.animate.set_color(C_LLAVE), run_time=0.40)
        self.wait(0.8)
        ganador = intento(DESPLAZAMIENTO, C_LLAVE, y_ganador)
        self.play(Transform(rodando, ganador), run_time=0.45)
        self.wait(0.5)

        rodando_2 = intento(4, C_ATAQUE, y_columna)
        self.play(FadeIn(rodando_2), run_time=0.24)
        for k in (6, 8, 11, 14, 17, 20, 22, N_LLAVES_CESAR):
            self.play(Transform(rodando_2, intento(k, C_ATAQUE, y_columna)),
                      run_time=0.26)
        self.wait(1.9)

        # --- cierre: enumerar no es guardar ---------------------------------
        self.play(FadeOut(rodando_2), run_time=0.35)
        rot.mostrar(pie_curso("Una llave que se puede enumerar no es una "
                              "llave."), zona="abajo")
        t_fuerza = tag_hud(f"{N_LLAVES_CESAR} llaves - fuerza bruta",
                           font_size=17, color=C_ATAQUE)
        t_fuerza.move_to(np.array([-3.45, -2.38, 0.0]))
        self.play(FadeIn(t_fuerza, shift=0.10 * UP), run_time=0.5)
        self.wait(5.0)

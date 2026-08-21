class Clip3(Scene):
    """4.2.3 - Lo mismo una dimension mas arriba: el cubo en el campo
    F = (x, y, z), las caras medidas y el total = la divergencia por el
    volumen. (~33 s)"""

    # Cuanto se aparta de la cara el rotulo de su cifra (unidades del
    # espacio, ADEMAS de lo que mide su propia flecha de flujo): la cara
    # de atras necesita mucho mas para no caer sobre el alambre del cubo.
    SEPARACION = {0: 0.62, 4: 0.62, 1: 2.07}

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("En 3D: el cubo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el campo radial en el espacio -----------------------
        esp = espacio_leccion(unidad=0.92, centro=DOWN * 0.85)
        campo3 = flechas3(esp, campo_radial3, paso=1.4, escala=0.55,
                          rango=2.1, opacidad=0.55)
        self.play(FadeIn(esp), run_time=0.8)
        rot.mostrar(pie_curso("El mismo campo, ahora en el espacio: cada "
                              "punto empujado hacia fuera."), zona="abajo",
                    run_time=0.5)
        panel = panel_derecha(MathTex(r"F = (x,\, y,\, z)", font_size=32,
                                      color=C_TITULO))
        self.play(LaggedStart(*[FadeIn(f, scale=0.6) for f in campo3],
                              lag_ratio=0.02), run_time=1.8)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.0)

        # --- momento: la caja se vuelve cubo ------------------------------
        rot.mostrar(pie_curso("La cajita del plano se vuelve un cubo, y "
                              "los cuatro lados, seis caras."), zona="abajo",
                    run_time=0.5)
        cubo = cubo_flujo3(esp, campo_radial3, CUBO_ESQUINA, CUBO_LADO,
                           escala=0.25)
        aristas = VGroup(*cubo.submobjects[:-1])
        caras = cubo.flechas
        self.play(campo3.animate.set_opacity(0.22), run_time=0.4)
        self.play(Create(aristas), run_time=1.4)
        self.wait(3.4)

        # --- momento: el flujo por cada cara ------------------------------
        rot.mostrar(pie_curso("Medimos el flujo por cada cara: verde el "
                              "que sale, rojo el que entra."), zona="abajo",
                    run_time=0.5)
        self.play(LaggedStart(*[GrowArrow(f) for f in caras],
                              lag_ratio=0.18), run_time=2.0)
        e = np.asarray(CUBO_ESQUINA, float)
        rotulos_caras = VGroup()
        for i in CARAS_ROTULADAS:
            nombre = NOMBRES_CARAS[i]
            signo = 1 if i % 2 == 0 else -1
            k = "xyz".index(nombre[1])
            n = np.zeros(3)
            n[k] = signo
            c = e + CUBO_LADO / 2
            c[k] = e[k] + (CUBO_LADO if signo > 0 else 0.0)
            fl = cubo.flujos[i]
            color = C_RES if fl >= 0 else C_VEC
            t = _con_fondo(tag_hud(f"{nombre} {fmt(fl, 2)}", font_size=18,
                                   color=color), buff=0.09, opacidad=0.88)
            t.move_to(esp.p(*(c + n * (0.25 * abs(fl)
                                       + self.SEPARACION[i]))))
            rotulos_caras.add(t)
        self.play(LaggedStart(*[FadeIn(t, scale=0.6) for t in rotulos_caras],
                              lag_ratio=0.3), run_time=1.4)
        self.wait(3.2)

        # --- momento: el total ---------------------------------------------
        rot.mostrar(pie_curso("Las seis caras sumadas dan el flujo total "
                              "del cubo."), zona="abajo", run_time=0.5)
        self.play(FadeOut(panel), run_time=0.3)
        panel2 = panel_derecha(
            MathTex(r"\oint_{S} F\cdot dS", font_size=30, color=C_CALCULO),
            tag_hud(f"total = {fmt(cubo.total, 2)}", font_size=20,
                    color=C_RES), buff=0.22)
        self.play(FadeIn(panel2, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.0)

        # --- momento: lo de dentro da el mismo numero ---------------------
        rot.mostrar(pie_curso(f"Y por dentro: divergencia constante "
                              f"{fmt(DIV_RADIAL3, 2)} por el volumen del "
                              f"cubo. El mismo número."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(panel2), run_time=0.3)
        panel3 = panel_derecha(
            MathTex(r"\oint_{S} F\cdot dS = \iiint_{V} \nabla\cdot F\, dV",
                    font_size=24, color=C_CALCULO),
            tag_hud(f"flujo = {fmt(cubo.total, 2)}", font_size=19,
                    color=C_RES),
            tag_hud(f"{fmt(DIV_RADIAL3, 2)} x {fmt(VOL_CUBO, 3)} = "
                    f"{fmt(TRIPLE_C3, 2)}", font_size=19, color=C_RES),
            buff=0.22)
        self.play(FadeIn(panel3, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.4)

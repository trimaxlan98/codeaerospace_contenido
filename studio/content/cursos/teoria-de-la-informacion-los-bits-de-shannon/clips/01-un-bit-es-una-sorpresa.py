class Clip1(Scene):
    """1 - Un bit es una sorpresa. Tres fuentes (moneda, dado, baraja)
    suben por la curva -log2 p: 1 bit, 2.58 y 5.70 -- lo improbable
    informa mas. Una moneda trucada al 90 % casi no sorprende cuando sale
    cara (0.15 bits) y sorprende mucho cuando sale cruz (3.32). Y el arbol
    de las preguntas de si o no: cada nivel duplica, asi que 20 preguntas
    distinguen 2^20 = 1 048 576 objetos. Cierre: informacion es
    incertidumbre que se despeja, y se mide en bits. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Un bit es una sorpresa"), zona="arriba",
                    run_time=0.6)

        # --- geometria -------------------------------------------------
        # Izquierda: la columna de las tres fuentes (luego, el arbol).
        # Derecha: la curva de la sorpresa. Todos los rotulos de cifras van
        # ARRIBA-DERECHA de su punto (la region sobre la curva esta vacia)
        # y con una guia punteada, para no pisar la curva ni los ticks.
        def punto(coords):
            v = [float(c) for c in coords]
            return np.array(v + [0.0] * (3 - len(v)))

        def rotulo(texto, centro, color, fs=14):
            t = tag_hud(texto, font_size=fs, color=color)
            t.move_to(punto(centro))
            return t

        def guia(desde, hasta, color):
            g = DashedLine(punto(desde), punto(hasta),
                           stroke_width=1.2, color=color, dash_length=0.08)
            g.set_stroke(opacity=0.45)
            return g

        curva = curva_sorpresa().scale(0.95)
        curva.move_to(np.array([1.90, 0.35, 0.0]))

        moneda = icono_fuente("moneda", C_FUENTE, alto=1.0)
        dado = icono_fuente("dado", C_FUENTE, alto=1.0)
        baraja = icono_fuente("baraja", C_FUENTE, alto=1.0)
        iconos = VGroup(moneda, dado, baraja)
        iconos.arrange(DOWN, buff=0.34)
        iconos.move_to(np.array([-4.15, 0.15, 0.0]))

        # --- momento 1: la moneda justa --------------------------------
        rot.mostrar(pie_curso("Una moneda justa: dos casos igual de "
                              "probables. Cae, y despeja una duda."),
                    zona="abajo")
        self.play(FadeIn(moneda, shift=0.12 * UP),
                  Create(curva.ejes), FadeIn(curva.ticks),
                  FadeIn(curva.etiqueta_x), FadeIn(curva.etiqueta_y),
                  run_time=0.9)
        self.play(Create(curva.curva), run_time=1.0)

        p_moneda = curva.en(0.5)
        d_moneda = Dot(p_moneda, radius=0.075, color=C_BIT)
        t_moneda = rotulo(f"{BITS_MONEDA:.0f} bit", [2.95, -0.13], C_BIT)
        g_moneda = guia(p_moneda, t_moneda.get_left() + LEFT * 0.05, C_BIT)
        self.play(FadeIn(d_moneda, scale=0.6), Create(g_moneda),
                  FadeIn(t_moneda), run_time=0.7)
        self.wait(2.9)

        # --- momento 2: lo improbable informa mas ----------------------
        rot.mostrar(pie_curso("Eso es un bit: la sorpresa de una moneda "
                              "justa. Lo improbable informa más."),
                    zona="abajo")
        self.play(FadeIn(dado, shift=0.12 * UP),
                  FadeIn(baraja, shift=0.12 * UP), run_time=0.8)

        p_dado = curva.en(1.0 / 6.0)
        d_dado = Dot(p_dado, radius=0.075, color=C_BIT)
        t_dado = rotulo(f"{BITS_DADO:.2f} bits", [1.90, 0.62], C_BIT)
        g_dado = guia(p_dado, t_dado.get_left() + LEFT * 0.05, C_BIT)
        p_baraja = curva.en(1.0 / 52.0)
        d_baraja = Dot(p_baraja, radius=0.075, color=C_BIT)
        t_baraja = rotulo(f"{BITS_BARAJA:.2f} bits", [1.30, 1.85], C_BIT)
        g_baraja = guia(p_baraja, t_baraja.get_left() + LEFT * 0.05, C_BIT)
        self.play(FadeIn(d_dado, scale=0.6), Create(g_dado), FadeIn(t_dado),
                  run_time=0.55)
        self.play(FadeIn(d_baraja, scale=0.6), Create(g_baraja),
                  FadeIn(t_baraja), run_time=0.55)

        ley = MathTex(r"I = -\log_2 p", font_size=30, color=C_BIT)
        ley.move_to(np.array([1.90, -1.92, 0.0]))
        self.play(Write(ley), run_time=0.8)
        self.wait(3.0)

        # --- momento 3: la moneda trucada ------------------------------
        rot.mostrar(pie_curso(f"Una moneda trucada "
                              f"({P_MONEDA_TRUCADA * 100:.0f} % cara) casi "
                              f"no sorprende... salvo cuando sale cruz."),
                    zona="abajo")
        base_tags = VGroup(t_moneda, g_moneda, t_dado, g_dado, t_baraja,
                           g_baraja)
        self.play(FadeOut(base_tags), run_time=0.5)

        p_cara = curva.en(P_MONEDA_TRUCADA)
        d_cara = Dot(p_cara, radius=0.075, color=C_BIT)
        t_cara = rotulo(f"cara: {BITS_CARA_TRUCADA:.2f} bits",
                        [4.25, 0.35], C_BIT)
        g_cara = guia(p_cara, t_cara.get_bottom() + DOWN * 0.05, C_BIT)
        p_cruz = curva.en(1 - P_MONEDA_TRUCADA)
        d_cruz = Dot(p_cruz, radius=0.075, color=C_BIT)
        t_cruz = rotulo(f"cruz: {BITS_CRUZ_TRUCADA:.2f} bits",
                        [1.75, 1.25], C_BIT)
        g_cruz = guia(p_cruz, t_cruz.get_left() + LEFT * 0.05, C_BIT)
        self.play(FadeIn(d_cara, scale=0.6), Create(g_cara), FadeIn(t_cara),
                  run_time=0.65)
        self.play(FadeIn(d_cruz, scale=0.6), Create(g_cruz), FadeIn(t_cruz),
                  run_time=0.65)
        self.wait(3.0)

        # --- momento 4: las veinte preguntas ---------------------------
        rot.mostrar(pie_curso(f"{N_PREGUNTAS} preguntas de sí o no bastan "
                              f"para distinguir un millón de cosas."),
                    zona="abajo")
        arbol = arbol_preguntas(4).scale(0.72)
        arbol.move_to(np.array([-4.05, 0.50, 0.0]))
        self.play(FadeOut(iconos), run_time=0.5)
        self.play(FadeIn(arbol.nivel(0)), FadeIn(arbol.etiquetas),
                  run_time=0.35)
        for k in range(arbol.profundidad):
            ramas_k = VGroup(*[arbol.rama(k, j, lado)
                               for j in range(2 ** k) for lado in (0, 1)])
            self.play(Create(ramas_k), FadeIn(arbol.nivel(k + 1)),
                      run_time=0.32)

        camino = arbol.camino([1, 0, 1, 1])
        self.play(*[r.animate.set_color(C_BIT).set_stroke(width=3.0,
                                                          opacity=1.0)
                    for r in camino], run_time=0.7)
        t_arbol = rotulo(f"2^{N_PREGUNTAS} = {miles(N_OBJETOS_20)} objetos",
                         [-4.05, -0.95, 0.0], C_BIT)
        self.play(FadeIn(t_arbol, shift=0.10 * UP), run_time=0.5)
        self.wait(2.5)

        # --- cierre ----------------------------------------------------
        rot.mostrar(pie_curso("Información es incertidumbre que se despeja. "
                              "Y se mide en bits."), zona="abajo")
        self.play(FadeOut(VGroup(d_cara, g_cara, t_cara, d_cruz, g_cruz,
                                 t_cruz)),
                  FadeIn(VGroup(t_moneda, g_moneda, t_dado, g_dado,
                                t_baraja, g_baraja)), run_time=0.6)
        self.wait(5.0)

class Clip1(Scene):
    """1 - La maquina que no existe. «La nube» es una rejilla de maquinas
    ordinarias al 99.9 %. La cuenta cruel, 1 - p^N: con diez casi nada, con
    cien ya duele y con mil hay un 63.2 % de que alguna este caida AHORA.
    Cierre: el sistema no evita las fallas, funciona con ellas. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La máquina que no existe")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # Geometria del clip: la rejilla (la nube) a la izquierda, la curva
        # 1 - p^N a la derecha, las dos dentro de la banda central. La curva
        # nace en (0.69, -0.94) y sube hasta (5.11, 0.56): las cifras de los
        # marcadores van ARRIBA de la curva, que es convexa y deja libre
        # todo el cuadrante superior izquierdo.
        rejilla = rejilla_nodos().scale(0.9).shift(LEFT * 3.1 + UP * 0.3)
        curva = curva_caidas().scale(0.85).shift(RIGHT * 2.9 + UP * 0.25)
        n_a, n_b, n_c = 10, 100, 1000     # los tres N que se marcan

        t_maquina = tag_hud(f"una máquina: {P_MAQUINA:.1%}", font_size=17)
        t_maquina.next_to(rejilla.nodos, UP, buff=0.30)

        # --- momento: la nube son maquinas ---------------------------------
        rot.mostrar(pie_curso("«La nube» no existe: son máquinas "
                              "ordinarias."), zona="abajo", run_time=0.45)
        self.play(LaggedStart(*[FadeIn(d, scale=0.6) for d in rejilla.nodos],
                              lag_ratio=0.035), run_time=1.6)
        self.play(FadeIn(t_maquina, shift=0.12 * UP), run_time=0.5)
        self.wait(3.0)

        # --- momento: la cuenta cruel --------------------------------------
        rot.mostrar(pie_curso("Multiplica las máquinas y la cuenta se "
                              "vuelve cruel."), zona="abajo")
        et_x = tag_junto(curva.ejes[0], "máquinas (escala log)", DOWN,
                         buff=0.22, font_size=14)
        et_y = tag_junto(curva.ejes[1], "P(alguna caída)", UP, buff=0.22,
                         font_size=14)
        self.play(Create(curva.ejes), run_time=0.7)
        self.play(FadeIn(et_x), FadeIn(et_y), run_time=0.4)
        self.play(Create(curva.curva), run_time=1.8)
        self.wait(2.3)

        # --- momento: los tres numeros -------------------------------------
        rot.mostrar(formula_pie(r"P(\text{alguna falla}) = 1 - p^{N}"),
                    zona="abajo")

        def marca(n, texto, color, font_size, dy, dx=0.0):
            """Punto sobre la curva ACTUAL y su cifra, ya colocada."""
            p = curva.en(n)
            t = tag_hud(texto, font_size=font_size, color=color)
            t.move_to(p + UP * dy + RIGHT * dx)
            return VGroup(Dot(p, radius=0.07, color=color), t)

        m_a = marca(n_a, f"N={n_a}: {P_CAIDA_10:.1%}", C_NODO, 16, 0.34)
        m_b = marca(n_b, f"N={n_b}: {P_CAIDA_100:.1%}", C_NODO, 16, 0.58,
                    -0.45)
        m_c = marca(n_c, f"N={n_c}: {P_CAIDA_1000:.1%}", C_FALLO, 24, 0.46,
                    -0.42)
        self.play(FadeIn(m_a, shift=0.12 * UP), run_time=0.55)
        self.wait(0.5)
        self.play(FadeIn(m_b, shift=0.12 * UP), run_time=0.55)
        self.wait(0.5)
        self.play(FadeIn(m_c, shift=0.14 * UP), run_time=0.7)
        self.play(Flash(m_c[0], color=C_FALLO, line_length=0.18,
                        num_lines=12, flash_radius=0.30), run_time=0.6)
        self.wait(1.9)

        # --- momento: siempre hay algo roto --------------------------------
        rot.mostrar(pie_curso("Con mil máquinas, ahora mismo hay algo "
                              "roto."), zona="abajo")
        idx = indices_caidos(len(rejilla.nodos), 5, SEMILLA_CAIDOS)
        caidos = VGroup(*[rejilla.nodo(i) for i in idx])
        t_caidos = tag_hud(f"{len(idx)} de {len(rejilla.nodos)} caídos",
                           font_size=16, color=C_FALLO)
        t_caidos.next_to(rejilla.nodos, DOWN, buff=0.32)
        self.play(LaggedStart(*[d.animate.set_color(C_FALLO).scale(0.85)
                                for d in caidos], lag_ratio=0.3),
                  run_time=1.7)
        self.play(*[Flash(d, color=C_FALLO, line_length=0.14, num_lines=8,
                          flash_radius=0.18) for d in caidos],
                  FadeIn(t_caidos, shift=0.12 * UP), run_time=0.7)
        self.wait(2.8)

        # --- cierre: funcionar CON fallas ----------------------------------
        rot.mostrar(pie_curso("El truco no es evitar las fallas: es "
                              "funcionar con ellas."), zona="abajo")
        self.wait(5.0)

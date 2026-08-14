class Clip1(Scene):
    """1 - Tu posicion es un reloj. Un satelite manda un pulso de luz, el
    receptor mide cuanto tardo, y esa medida de TIEMPO es la posicion:
    equivocarse 1 ns cuesta 30 cm. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Tu posición es un reloj")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # Geometria del clip: satelite arriba-derecha, pin abajo-izquierda.
        # Todo vive en la banda central (y entre -2.2 y 2.6).
        p_sat = RIGHT * 3.85 + UP * 1.95
        p_pin = LEFT * 3.85 + DOWN * 1.45
        u = normalize(p_pin - p_sat)          # del satelite hacia ti
        perp = np.array([u[1], -u[0], 0.0])   # normal, hacia arriba-izquierda

        # --- momento: tu y el satelite -------------------------------------
        rot.mostrar(pie_curso("¿Cómo sabe tu teléfono dónde estás?"),
                    zona="abajo", run_time=0.5)

        cuerpo = Dot(p_sat, radius=0.09, color=C_SATELITE)
        panel = Line(p_sat - RIGHT * 0.36 - UP * 0.06,
                     p_sat + RIGHT * 0.36 + UP * 0.06,
                     stroke_width=3.2, color=C_SATELITE)
        self.play(Create(panel), FadeIn(cuerpo, scale=2.0), run_time=0.7)

        suelo = Line(LEFT * 6.1 + DOWN * 2.02, LEFT * 1.7 + DOWN * 2.02,
                     stroke_width=2.2, color=C_EJE)
        palo = Line(p_pin, p_pin + DOWN * 0.57, stroke_width=2.6,
                    color=C_TIERRA)
        pin = Dot(p_pin, radius=0.10, color=C_TIERRA)
        tu = tag_junto(pin, "tú", LEFT, buff=0.20, font_size=21,
                       color=C_TIERRA)
        self.play(Create(suelo), Create(palo), FadeIn(pin, scale=2.0),
                  FadeIn(tu), run_time=0.7)
        self.wait(4.0)

        # --- momento: el pulso viaja ---------------------------------------
        rot.mostrar(pie_curso("Un satélite manda un pulso de luz y dice a "
                              "qué hora salió."), zona="abajo", run_time=0.5)

        camino = Line(p_sat + u * 0.20, p_pin - u * 0.22)
        haz = DashedVMobject(camino.copy(), num_dashes=34)
        haz.set_stroke(color=C_EJE, width=2.0, opacity=0.9)
        self.play(Create(haz), run_time=0.7)

        onda = Circle(radius=0.16, stroke_width=3.0, color=C_LUZ)
        onda.set_fill(opacity=0.0)
        onda.move_to(p_sat)
        self.add(onda)
        self.play(onda.animate.scale(4.2).set_stroke(opacity=0.0),
                  run_time=0.9)
        self.remove(onda)

        pulso = Dot(camino.get_start(), radius=0.085, color=C_LUZ)
        self.add(pulso)
        self.play(MoveAlongPath(pulso, camino), run_time=2.0,
                  rate_func=linear)
        self.play(Flash(pin, color=C_LUZ, line_length=0.16, num_lines=10,
                        flash_radius=0.30), run_time=0.5)
        self.wait(1.6)

        # --- momento: lo que se mide es el tiempo --------------------------
        rot.mostrar(pie_curso("El GPS no mide distancias: mide tiempos."),
                    zona="abajo", run_time=0.5)
        delta = MathTex(r"\Delta t", font_size=32, color=C_LUZ)
        delta.move_to(camino.get_center() + perp * 0.52)
        self.play(FadeIn(delta, shift=0.16 * UP), run_time=0.7)
        self.wait(4.3)

        # --- momento: el giro, la cifra ------------------------------------
        rot.mostrar(pie_curso("Y la luz es rapidísima: el GPS vive o muere "
                              "por sus relojes."), zona="abajo",
                    run_time=0.5)
        cifra = tag_hud(f"1 ns = {CM_POR_NS:.0f} cm", font_size=26)
        cifra.move_to(RIGHT * 4.40 + DOWN * 0.90)
        self.play(FadeIn(cifra, scale=0.55), run_time=0.9)
        self.wait(4.5)

        # --- cierre: la formula --------------------------------------------
        rot.mostrar(formula_pie(r"d = c\,\Delta t"), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

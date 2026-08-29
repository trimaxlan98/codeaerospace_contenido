class Clip2(Scene):
    """2.2.2 - El eje se reduce a J theta'' + b theta' = tau: un polo en
    el origen (integrador) y otro en -0.25. La constante mecanica J/b
    son 4 s, y una montura empujada tarda una eternidad en pararse.
    (~34 s)

    Los dos polos son reales y estan muy juntos (0 y -0.25) frente al
    rango +-4 de `plano_s()`: con esa escala compartida los dos marcadores
    se funden en uno solo (medido en el primer render). Se dibuja en su
    lugar un eje real propio, a la escala que SI los separa.
    """

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("J y b"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        rot.mostrar(formula_pie(r"J\ddot{\theta} + b\dot{\theta} = \tau"),
                    zona="abajo")
        self.wait(2.4)

        # --- el eje real, a una escala que SI separa los dos polos --------
        eje = Line(LEFT * 3.0, RIGHT * 3.0, stroke_width=2.4, color=C_EJE)
        eje.move_to(LEFT * 3.3 + UP * 0.1)
        t_re = tag_hud("Re", font_size=17, color=C_TENUE)
        t_re.next_to(eje, RIGHT, buff=0.16)
        self.play(Create(eje), FadeIn(t_re), run_time=1.0)
        self.wait(0.3)

        # Rango del eje en VALOR (no en escena): -1.0 a 0.4. Con un
        # rango tan estrecho los dos polos reales (0 y -0.25), que en la
        # escala +-4 de `plano_s()` se funden en un solo marcador
        # (medido en el primer render), quedan separados con holgura.
        def punto_re(valor):
            frac = (valor - (-1.0)) / (0.4 - (-1.0))
            return eje.get_start() + (eje.get_end() - eje.get_start()) * frac

        def marca_x(centro, tam=0.11, color=C_CALCULO):
            return VGroup(
                Line(centro + np.array([-tam, -tam, 0.0]),
                    centro + np.array([tam, tam, 0.0]),
                    stroke_width=4.2, color=color),
                Line(centro + np.array([-tam, tam, 0.0]),
                    centro + np.array([tam, -tam, 0.0]),
                    stroke_width=4.2, color=color))

        p0 = marca_x(punto_re(POLO_1))
        t0 = tag_junto(p0, "integrador", direccion=UP, buff=0.16,
                       font_size=17)
        v0 = tag_hud(fmt(POLO_1, 0), font_size=16, color=C_TENUE)
        v0.next_to(p0, DOWN, buff=0.14)
        self.play(FadeIn(p0, scale=1.8), FadeIn(t0), FadeIn(v0),
                  run_time=0.8)
        self.wait(1.0)

        p1 = marca_x(punto_re(POLO_2))
        t1 = tag_junto(p1, "friccion", direccion=UP, buff=0.16,
                       font_size=17)
        v1 = tag_hud(fmt(POLO_2, 2), font_size=16, color=C_TENUE)
        v1.next_to(p1, DOWN, buff=0.14)
        self.play(FadeIn(p1, scale=1.8), FadeIn(t1), FadeIn(v1),
                  run_time=0.8)
        self.wait(1.2)

        # --- la montura, empujada y soltada ------------------------------
        mont = montura(alto=2.7, font_size=15)
        destino = RIGHT * 3.15 + DOWN * 0.95
        delta = destino - mont.pivote
        mont.shift(delta)
        mont.pivote = mont.pivote + delta
        mont.base_izq = mont.base_izq + delta
        mont.base_der = mont.base_der + delta
        mont.apuntar(az_deg=0.0, el_deg=42.0)
        self.play(FadeIn(mont), run_time=0.9)

        empuje = tag_junto(mont.anillo, "empuje", direccion=UP, buff=0.16,
                           font_size=17, color=C_PELIGRO)
        self.play(FadeIn(empuje), run_time=0.5)

        az_t = ValueTracker(0.0)
        mont.add_updater(lambda m: m.apuntar(az_deg=az_t.get_value()))
        # un golpe rapido y luego la cola larga: casi todo el giro pasa
        # en el primer instante, y el resto se arrastra durante segundos.
        self.play(az_t.animate.set_value(30.0), run_time=0.4,
                  rate_func=rush_from)
        self.play(FadeOut(empuje), run_time=0.3)
        self.play(az_t.animate.set_value(38.0), run_time=3.6,
                  rate_func=lambda t: 1.0 - math.exp(-4.0 * t))
        mont.clear_updaters()
        self.wait(0.8)

        rot.mostrar(cifra_pie(f"J/b = {fmt(TAU_MEC, 1)} s"), zona="abajo")
        self.wait(2.2)

        panel = panel_cifras(f"J = {fmt(J_EJE, 1)} kg m2",
                             f"b = {fmt(B_EJE, 2)} N m s",
                             f"tau = {fmt(TAU_MEC, 1)} s")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(11.5)

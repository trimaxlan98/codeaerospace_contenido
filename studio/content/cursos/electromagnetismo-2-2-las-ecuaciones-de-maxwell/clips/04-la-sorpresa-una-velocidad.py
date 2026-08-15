class Clip4(Scene):
    """2.2.4 - La cuenta que nadie habia pedido: 1/sqrt(mu0 eps0) con dos
    constantes de mesa de laboratorio da 299 792 458 m/s, la velocidad de
    la luz que ya estaba medida. Cierra la leccion. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La sorpresa: una velocidad")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # Mantisa y exponente salen del propio numero (style_block), nunca
        # tecleados: la cifra escrita no puede discrepar de la constante.
        m_mu = MathTex(rf"\mu_0 = {MANT_MU0:.4f}\times "
                       rf"10^{{{EXP_MU0}}}\ \mathrm{{H/m}}",
                       font_size=32, color=C_B)
        m_eps = MathTex(rf"\varepsilon_0 = {MANT_EPS0:.4f}\times "
                        rf"10^{{{EXP_EPS0}}}\ \mathrm{{F/m}}",
                        font_size=32, color=C_E)
        constantes = VGroup(m_mu, m_eps)
        constantes.arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        # Entran centradas y suben cuando la cuenta ocupa el centro.
        constantes.move_to(UP * 0.55)

        cuenta = MathTex(r"\frac{1}{\sqrt{\mu_0\,\varepsilon_0}}",
                         font_size=46, color=C_CALCULO)
        cuenta.move_to(DOWN * 0.35)
        cifra = tag_hud(f"{C_MAXWELL:,.0f} m/s".replace(",", " "),
                        font_size=30)
        cifra.move_to(DOWN * 1.62)

        # --- momento: dos numeros de mesa de laboratorio ------------------
        rot.mostrar(pie_curso("Dos constantes. Ninguna de las dos habla de "
                              "luz."), zona="abajo", run_time=0.5)
        self.play(FadeIn(constantes, shift=0.15 * UP), run_time=0.9)
        self.wait(4.6)

        rot.mostrar(pie_curso("Mu cero se mide con bobinas; épsilon cero, "
                              "con condensadores. Mesa de laboratorio."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: la cuenta -------------------------------------------
        rot.mostrar(pie_curso("Maxwell hace con ellas una cuenta que nadie "
                              "le había pedido."), zona="abajo",
                    run_time=0.5)
        self.play(constantes.animate.move_to(UP * 1.35),
                  FadeIn(cuenta, scale=1.2), run_time=0.9)
        self.wait(4.6)

        rot.mostrar(pie_curso("El resultado no es una fuerza ni un campo. "
                              "Es una VELOCIDAD."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(cifra, shift=0.2 * DOWN), run_time=0.7)
        self.wait(4.6)

        rot.mostrar(pie_curso("Y esa velocidad ya estaba medida: era la de "
                              "la luz, al metro por segundo."),
                    zona="abajo", run_time=0.5)
        self.play(Flash(cifra, color=C_CALCULO, line_length=0.18,
                        flash_radius=1.9, num_lines=16), run_time=0.9)
        self.wait(4.6)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(constantes), FadeOut(cuenta), FadeOut(cifra),
                  run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        linea1 = Text("La luz no viaja por el campo.", font_size=40,
                      color=C_TITULO)
        linea2 = Text("La luz ES el campo.", font_size=40,
                      color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        rot.mostrar(pie_curso("La coincidencia más grande de la física del "
                              "siglo XIX no era coincidencia."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(4.6)

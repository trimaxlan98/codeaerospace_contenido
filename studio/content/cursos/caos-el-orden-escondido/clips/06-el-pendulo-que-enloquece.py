class Clip6(Scene):
    """6 - El pendulo que enloquece. Un pendulo doble reproduce su caos
    con la traza del extremo; despues, veinticinco pendulos separados una
    centesima de grado revientan en todas direcciones. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El péndulo que enloquece")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: el caos mas barato del mundo ------------------------
        rot.mostrar(pie_curso("Dos barras y dos tornillos: el sistema "
                              "caótico más barato del mundo."),
                    zona="abajo", run_time=0.5)
        estados = pendulo_doble(math.radians(120.0), math.radians(-10.0),
                                5200, 0.004)
        pendulo = PenduloDoble(estados, escala=1.15)
        pendulo.shift(UP * 0.55)
        pendulo.en(0.0)
        self.play(FadeIn(pendulo), run_time=0.6)
        self.play(UpdateFromAlphaFunc(pendulo, lambda m, a: m.en(a)),
                  run_time=7.5, rate_func=linear)
        self.wait(1.2)

        # --- momento: veinticinco gemelos ---------------------------------
        rot.mostrar(pie_curso("Veinticinco péndulos separados una "
                              "centésima de grado."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(pendulo), run_time=0.6)
        abanico = abanico_pendulos(N_PENDULOS, EPS_PENDULO_DEG, n=4600)
        abanico.shift(UP * 0.55)
        abanico.en(0.0)
        eps_tag = tag_hud(f"Δθ = {EPS_PENDULO_DEG}°", font_size=16)
        eps_tag.move_to(LEFT * 5.0 + UP * 2.5)
        rot.mostrar(eps_tag, zona="eps", run_time=0.4)
        self.play(FadeIn(abanico), run_time=0.6)
        self.wait(1.0)

        # --- momento: el abanico revienta ---------------------------------
        rot.mostrar(pie_curso("Ningún sensor del planeta distingue sus "
                              "arranques. El péndulo sí."), zona="abajo",
                    run_time=0.5)
        self.play(UpdateFromAlphaFunc(abanico, lambda m, a: m.en(a)),
                  run_time=9.0, rate_func=linear)
        self.wait(0.8)

        # --- momento: la moraleja mecanica --------------------------------
        rot.mostrar(pie_curso("El caos no vive en la ecuación: cuelga de "
                              "dos tornillos."), zona="abajo",
                    run_time=0.5)
        self.wait(5.6)

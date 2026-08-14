class Clip2(Scene):
    """3.5.2 - Placa plana a angulo de ataque en flujo supersonico.

    El caso mas simple que existe: dos caras, dos ondas. Y de el sale un
    resultado que no ocurre en subsonico — una placa plana supersonica
    ARRASTRA, y su arrastre no es un defecto, es el precio de la
    sustentacion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La placa plana")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        placa = perfil_supersonico("placa", M_PERFIL, ALFA, cuerda=3.0,
                                   largo_onda=1.6)
        placa.move_to(LEFT * 1.6 + UP * 0.55)
        self.play(Create(placa.perfil), run_time=0.8)
        rot.mostrar(pie_curso(f"Una placa plana a Mach {M_PERFIL:g}, con "
                              f"{ALFA:g} grados de ángulo de ataque."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        self.play(LaggedStart(*[Create(o) for o in placa.ondas],
                              lag_ratio=0.3), run_time=1.8)
        rot.mostrar(pie_curso("Abajo el aire se dobla hacia dentro: choque. "
                              "Arriba se abre: abanico."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: las dos presiones ------------------------------------
        # Las barras salen de la pieza: su longitud es |p/p1 - 1| y su
        # sentido dice si empuja o succiona.
        barras = VGroup(*[placa.barra_presion(c, escala=1.5)
                          for c in ("sup", "inf")])
        cifras = VGroup(
            Text(f"extradós  p/p1 = {placa.presion('sup'):.3f}",
                 font=FUENTE_HUD, font_size=18, color=C_CALCULO),
            Text(f"intradós  p/p1 = {placa.presion('inf'):.3f}",
                 font=FUENTE_HUD, font_size=18,
                 color=C_SUPER)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        cifras.move_to(RIGHT * 3.9 + UP * 0.85)

        self.play(FadeIn(barras), FadeIn(cifras, shift=0.10 * UP),
                  run_time=0.9)
        rot.mostrar(pie_curso("Arriba succiona, abajo empuja. La diferencia "
                              "es la sustentación."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: y el arrastre ----------------------------------------
        coef = VGroup(
            MathTex(rf"c_l = {placa.cl():.4f}", font_size=34, color=C_SUB),
            MathTex(rf"c_d = {placa.cd():.4f}", font_size=34,
                    color=C_SUPER)).arrange(DOWN, aligned_edge=LEFT,
                                            buff=0.26)
        coef.next_to(cifras, DOWN, buff=0.55).align_to(cifras, LEFT)
        self.play(FadeIn(coef, shift=0.10 * UP), run_time=0.8)
        rot.mostrar(pie_curso("Pero fíjate: también hay arrastre. Y el aire "
                              "aquí no tiene viscosidad."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Es arrastre de onda: la energía que se llevan "
                              "los choques. En subsónico no existe."),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)

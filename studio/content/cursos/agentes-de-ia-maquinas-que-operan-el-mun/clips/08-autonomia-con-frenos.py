class Clip8(Scene):
    """8 - Autonomia con frenos. La escala L0-L5 y los tres mecanismos que
    mantienen a un humano en el circuito aunque el agente opere solo.
    Cierra el curso con la tarjeta de marca. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ----------------------------------------------
        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.wait(0.4)

        titulo = titulo_curso("Autonomía con frenos")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(1.8)

        # --- momento: la escala de autonomia aparece en L0 ---------------
        escala = escala_autonomia(nivel=0)
        escala.move_to(0.6 * UP)
        self.play(Create(escala), run_time=1.2)
        rot.mostrar(pie_curso("L0: la persona hace todo."), zona="abajo",
                    run_time=0.5)
        self.wait(3.3)

        # --- momento: el marcador avanza, L0 -> L2 -> L4 -------------------
        self.play(escala.marcador.animate.move_to(escala.pos_nivel(2)),
                  run_time=0.9)
        rot.mostrar(pie_curso("L2: el agente propone, tú apruebas."),
                    zona="abajo", run_time=0.5)
        self.wait(3.3)

        self.play(escala.marcador.animate.move_to(escala.pos_nivel(4)),
                  run_time=0.9)
        rot.mostrar(pie_curso("L4: opera solo... dentro de límites."),
                    zona="abajo", run_time=0.5)
        self.wait(3.8)

        # --- momento: los frenos que sostienen esa autonomia ----------------
        presupuesto = tarjeta_json(["presupuesto: 100 tokens"], ancho=2.7,
                                   font_size=15, valida=True)
        guardia = escudo(radio=0.42, color=C_OK)
        aprueba = burbuja("humano aprueba", tipo="accion", ancho_max=2.6,
                          font_size=16)
        frenos = VGroup(presupuesto, guardia, aprueba).arrange(
            RIGHT, buff=0.8)
        frenos.move_to(1.4 * DOWN)

        self.play(FadeIn(frenos, lag_ratio=0.15, shift=0.15 * UP),
                  run_time=1.0)
        rot.mostrar(pie_curso("Presupuestos, permisos y un humano en el "
                              "circuito."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: pantalla limpia para la tarjeta de cierre --------------
        rot.limpiar(run_time=0.5)
        self.play(FadeOut(VGroup(escala, frenos, modulo)), run_time=1.0)

        # --- momento: tarjeta final, patron exacto del curso hermano ----------
        titulo_final = titulo_marca("Agentes de IA", font_size=46)
        subtitulo = Text("máquinas que operan el mundo", font_size=25,
                         color=C_ACENTO)
        cuerpo = VGroup(titulo_final, subtitulo).arrange(DOWN, buff=0.26)

        subrayado = Line(LEFT, RIGHT, color=C_ACENTO)
        subrayado.set_width(subtitulo.width * 1.1)
        subrayado.next_to(subtitulo, DOWN, buff=0.16)
        brillo_subrayado = con_brillo(subrayado, color=C_ACENTO)

        tarjeta = VGroup(cuerpo, brillo_subrayado)
        tarjeta.move_to(ORIGIN)

        self.play(Write(titulo_final), run_time=1.7)
        self.play(FadeIn(subtitulo, shift=0.15 * UP), run_time=0.9)
        self.wait(1.8)
        self.play(Create(brillo_subrayado), run_time=1.3)
        self.wait(2)

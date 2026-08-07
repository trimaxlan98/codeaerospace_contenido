class Clip8(Scene):
    """8 - Sintonizar: el arte. P rapido hasta oscilar, D amortigua, I
    apenas borra el resto: tres perillas, tres metricas que se hunden.
    Cierra el curso con la tarjeta de marca. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ------------------------------------------------
        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Sintonizar: el arte")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(0.6)

        # --- momento: P puro, rapido pero oscilando -----------------------
        resp = respuesta_escalon(zeta=0.056)
        resp.move_to((-2.9, -0.1, 0.0))
        barras = barras_metricas([0.9, 0.85, 0.95])
        barras.move_to((3.0, -0.1, 0.0))

        self.play(Create(resp.ejes), Create(resp.etiquetas),
                  Create(barras.marcos), Create(barras.linea), run_time=0.5)
        self.play(Create(resp.linea_ref), Create(barras.rotulos),
                  run_time=0.4)
        self.play(Create(resp.curva), Create(barras.barras), run_time=1.3)
        rot.mostrar(pie_curso("Primero P: rápido hasta que oscile."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: D amortigua (pie ANTES del transform, sincronizado) -
        resp2 = respuesta_escalon(zeta=0.35)
        resp2.move_to(resp.get_center())
        barras2 = barras_metricas([0.5, 0.5, 0.5])
        barras2.move_to(barras.get_center())
        rot.mostrar(pie_curso("Luego D: amortigua hasta que el motor "
                              "deje de zumbar."), zona="abajo", run_time=0.5)
        self.play(ReplacementTransform(resp, resp2),
                  ReplacementTransform(barras, barras2), run_time=1.1)
        self.wait(4.2)

        # --- momento: I apenas, cierra sin despertar al windup -------------
        resp3 = respuesta_escalon(zeta=0.7, color=C_OK)
        resp3.move_to(resp2.get_center())
        barras3 = barras_metricas([0.15, 0.10, 0.12])
        barras3.move_to(barras2.get_center())
        rot.mostrar(pie_curso("Al final I, apenas: borra el resto sin "
                              "despertar al windup."), zona="abajo",
                    run_time=0.5)
        self.play(ReplacementTransform(resp2, resp3),
                  ReplacementTransform(barras2, barras3), run_time=1.1)
        self.wait(4.0)

        # --- momento: las tres metricas que mandan -------------------------
        rot.mostrar(pie_curso("Tres métricas mandan: error RMS, "
                              "sobreimpulso, tiempo de establecimiento."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: pantalla limpia para la tarjeta de cierre -------------
        rot.limpiar(run_time=0.4)
        self.play(FadeOut(VGroup(resp3, barras3, modulo)), run_time=0.9)

        # --- momento: tarjeta final, patron exacto del curso ------------------
        titulo_final = titulo_marca("Control", font_size=46)
        subtitulo = Text("domar sistemas que se resisten", font_size=25,
                         color=C_ACENTO)
        cuerpo = VGroup(titulo_final, subtitulo).arrange(DOWN, buff=0.26)

        subrayado = Line(LEFT, RIGHT, color=C_ACENTO)
        subrayado.set_width(subtitulo.width * 1.1)
        subrayado.next_to(subtitulo, DOWN, buff=0.16)
        brillo_subrayado = con_brillo(subrayado, color=C_ACENTO)

        tarjeta = VGroup(cuerpo, brillo_subrayado)
        tarjeta.move_to(ORIGIN)

        self.play(Write(titulo_final), run_time=1.6)
        self.play(FadeIn(subtitulo, shift=0.15 * UP), run_time=0.8)
        self.wait(1.2)
        self.play(Create(brillo_subrayado), run_time=1.2)
        self.wait(2)

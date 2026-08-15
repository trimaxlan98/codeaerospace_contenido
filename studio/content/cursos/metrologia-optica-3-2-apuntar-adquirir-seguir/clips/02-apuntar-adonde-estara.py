class Clip2(Scene):
    """2 - Apuntar adonde estara. Mientras la luz cruza los 5000 km (16.7 ms)
    el otro satelite avanza a 7.6 km/s: el haz "ingenuo" (punteado, hacia
    donde SE VE) llega tarde. Hay que adelantar 2v/c = 50.70 urad, cinco
    anchos del haz de 9.87 urad. El desvio en pantalla es un salto fijo,
    exagerado a proposito (a escala real serian 5e-5 unidades). (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Apuntar adonde estará"), zona="arriba",
                    run_time=0.6)

        # `ancho` solo separa emisor y carril (los iconos no crecen): 8.0
        # llena el cuadro a lo ancho sin tocar el alto de 3.2.
        pa = adelanto_apuntado(V_LEO_KMS, R_ISL_KM, ancho=8.0, frac=0.0)
        pa.move_to(DOWN * 0.10)
        # Fase 1: solo el haz ingenuo. El fantasma y el haz adelantado entran
        # en el momento 2; su rotulo "estara" (marcas[0]) tambien se apaga.
        pa.haz_adelantado.set_opacity(0.0)
        pa.fantasma.set_opacity(0.0)
        pa.marcas[0].set_opacity(0.0)

        # --- momento: la luz tarda -------------------------------------------
        t_luz_ms = tiempo_luz(R_ISL_KM * 1e3) * 1e3
        rot.mostrar(pie_curso(
            f"El haz tarda {t_luz_ms:.1f} milisegundos en cruzar cinco mil "
            f"kilómetros."), zona="abajo")
        self.play(FadeIn(pa, shift=0.14 * UP), run_time=0.9)
        self.wait(4.4)

        # --- momento: el otro se mueve ----------------------------------------
        rot.mostrar(pie_curso(f"El otro satélite se mueve a {V_LEO_KMS:.1f} "
                              f"kilómetros por segundo mientras la luz "
                              f"viaja."), zona="abajo")
        # `a_t` MUTA (rehace el haz punteado y los rotulos): va con
        # ValueTracker, no con `.animate`. Se limpia el updater en cuanto
        # termina el barrido para no rehacer textos en cada frame del resto
        # del clip.
        avance = ValueTracker(0.0)
        oculto = [True]

        def _seguir(m):
            # El renderer cairo congela la lista de mobjects "en movimiento"
            # al empezar el play: los submobjects que `a_t` SUSTITUYE (el haz
            # punteado y las marcas) se siguen dibujando aunque la pieza ya no
            # los tenga. Se apagan a mano al relevarlos.
            viejos = (m.haz_ingenuo, m.marcas)
            m.a_t(avance.get_value())
            for v in viejos:
                v.set_opacity(0.0)
            if oculto[0]:
                m.marcas[0].set_opacity(0.0)

        pa.add_updater(_seguir)
        self.play(avance.animate.set_value(1.0), run_time=3.4,
                  rate_func=linear)
        pa.clear_updaters()
        pa.a_t(1.0)
        pa.marcas[0].set_opacity(0.0)
        self.wait(2.0)

        # --- momento: el angulo de adelanto ------------------------------------
        rot.mostrar(pie_curso("Hay que apuntar adonde estará: el ángulo de "
                              "adelanto es dos veces v sobre c."),
                    zona="abajo")
        eq = MathTex(r"\theta_{pa} = \frac{2v}{c}", font_size=38,
                     color=C_MEDIDA)
        eq.move_to(np.array([-3.55, 2.10, 0.0]))
        oculto[0] = False
        self.play(FadeIn(eq, shift=0.14 * UP),
                  pa.haz_adelantado.animate.set_stroke(opacity=1.0),
                  pa.fantasma.animate.set_stroke(opacity=0.40).set_fill(
                      opacity=0.06),
                  pa.marcas[0].animate.set_opacity(1.0), run_time=1.0)
        self.play(Flash(pa.fantasma, color=C_OBJETO, line_length=0.18,
                        num_lines=14, flash_radius=0.55), run_time=0.8)
        self.wait(3.6)

        # --- momento: cinco anchos de haz ---------------------------------------
        rot.mostrar(pie_curso(f"{ADELANTO_URAD:.1f} microrradianes: cinco "
                              f"anchos de haz por delante del blanco."),
                    zona="abajo")
        t_anchos = tag_hud(
            f"{ADELANTO_URAD:.1f} urad = {ADELANTO_URAD / DIV_ISL_URAD:.0f} "
            f"anchos de haz", font_size=16)
        t_anchos.move_to(np.array([-3.55, 1.42, 0.0]))
        self.play(FadeIn(t_anchos), run_time=0.4)
        self.wait(4.6)

        # --- cierre --------------------------------------------------------------
        rot.mostrar(pie_curso("Se apunta al futuro del otro satélite."),
                    zona="abajo")
        self.wait(5.0)

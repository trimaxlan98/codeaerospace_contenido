class Clip8(Scene):
    """8 - Negociar con el tirano. La unica variable libre es la velocidad
    de escape: el ionico baja la razon de masas de 14.6 a 1.37, pero
    empuja gramos. Recapitulacion en miniaturas y cierre del curso.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Negociar con el tirano")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: la unica variable libre -----------------------------
        rot.mostrar(pie_curso("La única variable libre de la ecuación es la "
                              "velocidad de escape."),
                    zona="abajo", run_time=0.5)

        def columna(nombre, texto_ve, texto_razon, color):
            cab = Text(nombre, font_size=24, color=color)
            ve = tag_hud(texto_ve, font_size=20, color=color)
            razon = tag_hud(texto_razon, font_size=36, color=color)
            return VGroup(cab, ve, razon).arrange(DOWN, buff=0.30)

        col_q = columna("química", f"ve = {VE_QUIMICO / 1000:.1f} km/s",
                        f"m0/mf = {RAZON_QUIMICO:.1f}", C_PROPELENTE)
        col_i = columna("iónico", f"ve = {VE_ION / 1000:.0f} km/s",
                        f"m0/mf = {RAZON_ION:.2f}", C_CARGA)
        col_q.move_to(LEFT * 3.1 + UP * 0.72)
        col_i.move_to(RIGHT * 3.1 + UP * 0.72)
        col_i.align_to(col_q, UP)
        divisor = Line(UP * 1.62, DOWN * 1.30, stroke_width=1.8, color=C_EJE)
        divisor.set_stroke(opacity=0.8)

        self.play(FadeIn(col_q, shift=0.16 * RIGHT), Create(divisor),
                  run_time=0.7)
        self.play(FadeIn(col_i, shift=0.16 * LEFT), run_time=0.9)
        self.wait(1.0)
        self.play(Indicate(col_i[2], color=C_CARGA, scale_factor=1.16),
                  run_time=0.9)
        self.wait(2.2)

        # --- momento: el precio del ionico --------------------------------
        rot.mostrar(pie_curso("Pero el iónico empuja gramos: sirve en el "
                              "vacío, no para despegar."),
                    zona="abajo", run_time=0.5)

        prop_q = tag_hud(f"propelente: {FRAC_PROP * 100:.0f} %",
                         font_size=19, color=C_PROPELENTE)
        prop_q.next_to(col_q, DOWN, buff=0.38)
        prop_i = tag_hud(f"propelente: {FRAC_PROP_ION * 100:.0f} %",
                         font_size=19, color=C_CARGA)
        prop_i.next_to(col_i, DOWN, buff=0.38)
        empuje = tag_hud("empuje: gramos", font_size=19, color=C_MUERTO)
        empuje.next_to(prop_i, DOWN, buff=0.26)

        self.play(FadeIn(prop_q, shift=0.10 * UP),
                  FadeIn(prop_i, shift=0.10 * UP), run_time=0.8)
        self.wait(1.0)
        self.play(FadeIn(empuje, shift=0.10 * UP), run_time=0.7)
        self.wait(4.0)

        # --- momento: la recapitulacion -----------------------------------
        rot.mostrar(pie_curso("Momento, logaritmo, etapas: cada gramo en "
                              "órbita pagó la cuenta."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(col_q), FadeOut(col_i), FadeOut(divisor),
                  FadeOut(prop_q), FadeOut(prop_i), FadeOut(empuje),
                  run_time=0.8)

        canon = canon_newton()
        orbita = canon.trayectoria(1.0, color=C_CARGA)
        minis = VGroup(
            silueta_cohete(FRAC_PROP, FRAC_ESTRUCTURA_SIL,
                           FRAC_CARGA_SIL).scale_to_fit_height(1.5),
            curva_tirania().scale_to_fit_height(1.3),
            VGroup(canon, orbita).scale_to_fit_height(1.4),
            barras_carga(tuple(c / t * 100 for _, c, t in COHETES_REALES))
            .scale_to_fit_height(1.2),
        )
        minis.arrange(RIGHT, buff=0.8)
        if minis.width > 11.0:
            minis.scale_to_fit_width(11.0)
        minis.move_to(UP * 0.35)
        self.play(LaggedStart(*[FadeIn(m, shift=0.18 * UP) for m in minis],
                              lag_ratio=0.22), run_time=1.8)
        self.wait(4.0)

        # --- momento: cierre del curso ------------------------------------
        rot.limpiar("arriba", run_time=0.3)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeOut(minis), run_time=0.5)
        cierre = VGroup(
            titulo_marca("La ecuación no se derrota: se negocia.",
                         font_size=38),
            Text("Cada gramo en órbita la pagó en logaritmos.",
                 font_size=26, color=C_CARGA),
        ).arrange(DOWN, buff=0.4)
        cierre.move_to(UP * 0.2)
        self.play(Write(cierre[0]), run_time=1.2)
        self.play(FadeIn(cierre[1], shift=0.18 * UP), run_time=0.8)
        self.wait(6.0)

class Clip4(Scene):
    """4 - Un espejo a lambda/20. El perfil medido contra el ideal, con la
    banda de error MEDIDA sobre los datos: pico-valle lambda/20 = 31.6 nm con
    el HeNe. En un metro de vidrio eso es 3e-8. Cierre: la forma no se toca,
    se lee en las franjas. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Un espejo a λ/20"), zona="arriba",
                    run_time=0.6)

        # --- geometria: el perfil llena la banda alta -----------------------
        # perfil_superficie mide 7.67 x 2.73; escalado 1.12 y centrado en
        # y = +0.50 va de -1.03 a +2.03, con el MathTex debajo (y = -1.85)
        # y el pie en -3.2. La lectura y el aviso de escala vertical vienen
        # de la pieza: las cifras las MIDE la libreria.
        perfil = perfil_superficie(error_ondas=0.05, lam=LAMBDA_HENE)
        perfil.scale(1.12).move_to(UP * 0.50)
        t_ideal, t_medido, t_escala = perfil.rotulos

        pv_nm = perfil.error_nm()
        razon = pv_nm * 1e-9 / 1.0                  # por METRO de vidrio
        exp = int(math.floor(math.log10(razon)))
        mant = razon / 10.0 ** exp
        form = MathTex(rf"\frac{{{pv_nm:.1f}\ \mathrm{{nm}}}}"
                       rf"{{1\ \mathrm{{m}}}} = {mant:.1f}\times 10^{{{exp}}}",
                       font_size=40, color=C_MEDIDA)
        form.move_to(np.array([0.0, -1.85, 0.0]))

        # --- momento: medido contra ideal ------------------------------------
        rot.mostrar(pie_curso("Así se mide un espejo de telescopio: perfil "
                              "medido contra el ideal."), zona="abajo")
        self.play(Create(perfil.ejes), FadeIn(t_escala), run_time=0.7)
        self.play(Create(perfil.ideal), FadeIn(t_ideal), run_time=1.1)
        self.play(Create(perfil.medido), FadeIn(t_medido), run_time=1.6)
        self.wait(4.0)

        # --- momento: el error en fracciones de lambda -----------------------
        rot.mostrar(pie_curso("El error se cuenta en fracciones de la "
                              "longitud de onda."), zona="abajo")
        self.play(FadeIn(perfil.banda), run_time=0.9)
        self.play(FadeIn(perfil.lectura, shift=0.12 * DOWN), run_time=0.7)
        self.wait(4.6)

        # --- momento: 30 nanometros en un metro ------------------------------
        rot.mostrar(pie_curso("Treinta nanómetros en un metro de vidrio: la "
                              "millonésima de la millonésima."), zona="abajo")
        self.play(Write(form), run_time=1.4)
        self.wait(4.8)

        # --- cierre a pantalla limpia ----------------------------------------
        rot.limpiar()
        self.play(FadeOut(perfil), FadeOut(form), run_time=0.9)
        frase_a = Text("La forma no se toca.", font_size=40, color=C_FRANJA)
        frase_b = Text("Se lee en las franjas.", font_size=40, color=C_FRANJA)
        frases = VGroup(frase_a, frase_b).arrange(DOWN, buff=0.46)
        frases.move_to(UP * 0.10)
        self.play(FadeIn(frase_a, shift=0.14 * UP), run_time=0.8)
        self.play(FadeIn(frase_b, shift=0.14 * UP), run_time=0.8)
        self.wait(5.0)

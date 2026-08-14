class Clip4(Scene):
    """1.3.4 - El cono de Mach y el angulo mu = arcsen(1/M).

    Los tres conos del curso, uno detras de otro, y despues la curva que los
    resume: el cono se cierra rapidisimo al principio y luego se resiste.
    Cierre de la leccion. (~34 s)"""

    def _tag_mu(self, ondas):
        """Rotulo del angulo, colgado FUERA del cono (dentro competiria con
        los propios frentes; fuera, la envolvente garantiza sitio limpio)."""
        t = MathTex(rf"\mu = {ondas.mu():.1f}^\circ", font_size=32,
                    color=C_SUPER)
        t.move_to(ondas.fuente() + np.array([-1.35, 1.55, 0.0]))
        return t

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El cono y su ángulo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: apenas superado el sonido ---------------------------
        ancla = RIGHT * 2.6 + UP * 0.45
        ondas = frentes_moviles(MACHS_CONO[0], n_ondas=5, paso=0.26)
        ondas.shift(ancla - ondas.fuente())
        tag = self._tag_mu(ondas)

        self.play(FadeIn(ondas), run_time=0.9)
        self.play(FadeIn(tag), run_time=0.5)
        rot.mostrar(pie_curso("Justo por encima del sonido el cono es casi "
                              "plano: va casi de perfil."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: acelerar lo cierra ----------------------------------
        # ReplacementTransform y no Transform: el localizador `fuente()` se
        # lee del centro actual, y un Transform dejaria al mobject con los
        # atributos del Mach viejo apuntando a un centro nuevo.
        rot.mostrar(pie_curso("Acelera, y el cono se cierra sobre el "
                              "vehículo."), zona="abajo", run_time=0.5)
        self.wait(1.0)
        for mach in MACHS_CONO[1:]:
            nuevas = ondas.con_mach(mach)
            nuevo_tag = self._tag_mu(nuevas)
            self.play(ReplacementTransform(ondas, nuevas),
                      ReplacementTransform(tag, nuevo_tag), run_time=1.2)
            ondas, tag = nuevas, nuevo_tag
            self.wait(3.0)

        # --- momento: la curva que lo resume ------------------------------
        self.play(FadeOut(VGroup(ondas, tag)), run_time=0.7)
        curva = curva_mu(ancho=5.6, alto=2.7)
        curva.move_to(DOWN * 0.30)
        self.play(FadeIn(curva.ejes), run_time=0.5)
        self.play(Create(curva.curva), run_time=1.6)

        marcas = VGroup()
        for mach in MACHS_CONO:
            punto = Dot(curva.punto_de(mach), radius=0.062, color=C_SUPER)
            tag_m = Text(f"{curva.mu(mach):.0f}", font=FUENTE_HUD,
                         font_size=16, color=C_SUPER)
            tag_m.next_to(punto, UR, buff=0.08)
            marcas.add(VGroup(punto, tag_m))
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in marcas],
                              lag_ratio=0.4), run_time=1.1)

        rot.mostrar(formula_pie(r"\mu = \operatorname{arcsen}"
                                r"\!\left(\tfrac{1}{M}\right)",
                                color=C_SUPER), zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(curva, marcas)), run_time=0.7)
        cierre = VGroup(
            titulo_marca("La velocidad del sonido no es un dato:",
                         font_size=34, color=C_TITULO),
            titulo_marca("es el termómetro del aire.", font_size=34,
                         color=C_CALCULO)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.2)

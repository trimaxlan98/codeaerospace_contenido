class Clip3(Scene):
    """1.1.3 - Regimenes subsonico, transonico, supersonico e hipersonico.

    Primero POR QUE hay una pared: los frentes que emite una fuente movil se
    apilan delante hasta que, a M = 1, el vehiculo viaja con su propio aviso.
    De ahi sale el cono de Mach y, de ahi, la regla de los cuatro
    regimenes. (~44 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La pared del sonido")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: una fuente quieta avisa por igual a todas partes ----
        # `con_mach` re-ancla por la FUENTE, no por el centro del dibujo: al
        # abrirse el cono, centro y fuente se separan y anclar por centro
        # haria que el emisor se deslizara solo durante la animacion.
        ancla = RIGHT * 1.9 + UP * 0.35
        ondas = frentes_moviles(0.0, n_ondas=4, paso=0.42)
        ondas.shift(ancla - ondas.fuente())

        self.play(FadeIn(ondas.punto_fuente), run_time=0.4)
        self.play(LaggedStart(*[Create(ondas.onda(k)) for k in range(4)],
                              lag_ratio=0.4), run_time=2.0)
        self.add(ondas)
        rot.mostrar(pie_curso("Un emisor quieto avisa a todas partes por "
                              "igual: el sonido va por delante."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: al moverse, los avisos se apilan delante ------------
        # ReplacementTransform y no Transform: tras un Transform el mobject
        # conserva sus atributos viejos y `fuente()` —que se lee del centro
        # actual— apuntaria a un sitio que ya no es el emisor.
        siguiente = ondas.con_mach(0.6)
        self.play(ReplacementTransform(ondas, siguiente), run_time=1.1)
        ondas = siguiente
        rot.mostrar(pie_curso("En movimiento, los frentes se apretujan "
                              "delante. Pero aún se adelantan."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        siguiente = ondas.con_mach(1.0)
        self.play(ReplacementTransform(ondas, siguiente), run_time=1.2)
        ondas = siguiente
        rot.mostrar(pie_curso("A Mach 1 ya no: el vehículo llega a la vez "
                              "que su propio aviso."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: el cono ---------------------------------------------
        siguiente = ondas.con_mach(2.0)
        self.play(ReplacementTransform(ondas, siguiente), run_time=1.2)
        ondas = siguiente

        # El angulo se mide contra la direccion de marcha, y el rotulo lo
        # calcula la libreria: el arco dibujado y el numero escrito salen del
        # mismo arcsen(1/M).
        eje_marcha = Line(ondas.fuente(), ondas.fuente() + LEFT * 1.7,
                          stroke_width=1.2, color=C_EJE)
        # Arc explicito y no Angle: Angle elige el cuadrante por su cuenta y
        # aqui se queda con el reflejo (330 grados), que se lee como una
        # circunferencia alrededor del emisor. El sector que interesa va de
        # la generatriz del cono (180 - mu) al eje de marcha (180).
        arco = Arc(radius=0.62, start_angle=np.deg2rad(180 - ondas.mu()),
                   angle=np.deg2rad(ondas.mu()), arc_center=ondas.fuente(),
                   color=C_SUPER, stroke_width=2.2)
        tag_mu = MathTex(rf"\mu = {ondas.mu():.0f}^\circ", font_size=30,
                         color=C_SUPER)
        # Fuera del cono: dentro compite con los propios frentes de onda, y
        # por definicion la envolvente deja limpio todo lo que queda fuera.
        tag_mu.move_to(ondas.fuente()
                       + np.array([-1.15, 1.05, 0.0]))

        self.play(Create(eje_marcha), run_time=0.4)
        self.play(Create(arco), FadeIn(tag_mu), run_time=0.7)
        rot.mostrar(formula_pie(r"\mu = \operatorname{arcsen}"
                                r"\!\left(\tfrac{1}{M}\right)",
                                color=C_SUPER), zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- momento: los cuatro regimenes --------------------------------
        self.play(FadeOut(VGroup(ondas, eje_marcha, arco, tag_mu)),
                  run_time=0.7)

        banda = banda_regimenes()
        banda.move_to(DOWN * 0.15)
        self.play(FadeIn(banda.eje), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(VGroup(banda.zona(i), banda.nombres[i]),
                                       shift=0.14 * UP) for i in range(4)],
                              lag_ratio=0.45), run_time=1.8)
        self.play(FadeIn(banda.fronteras), run_time=0.5)
        rot.mostrar(pie_curso("Cuatro regímenes. Cada uno con su física y "
                              "sus ecuaciones."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Ojo: los tramos no están a escala. El "
                              "transónico es estrecho y es donde más pasa."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

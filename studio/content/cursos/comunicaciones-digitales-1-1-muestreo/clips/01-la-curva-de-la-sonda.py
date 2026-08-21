class Clip1(Scene):
    """1.1.1 - La telemetria de una sonda es una curva continua con
    infinitos puntos: la radio no puede enviarlos todos. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La curva que nadie puede enviar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la sonda y su curva ---------------------------------
        rot.mostrar(pie_curso("Una sonda mide su temperatura: una curva "
                              "continua en el tiempo."),
                    zona="abajo", run_time=0.5)
        on = onda(T_CURVA, Y_CURVA, rango_y=(-1.15, 1.15), ancho=8.2,
                  alto=3.4)
        on.move_to(DOWN * 0.25)
        sonda = VGroup(Dot(radius=0.09, color=C_BIT),
                       Dot(radius=0.16, color=C_BIT, fill_opacity=0.25))
        sonda.move_to(on.en(0.06, 1.0) + UP * 0.75)
        et_sonda = tag_junto(sonda, "sonda", direccion=UP, buff=0.1)
        self.play(FadeIn(on.ejes), FadeIn(sonda), FadeIn(et_sonda),
                  run_time=0.8)
        self.play(Create(on.curva), run_time=2.2)
        self.wait(3.0)

        # --- momento: el punto que recorre la curva -----------------------
        rot.mostrar(pie_curso("En cada instante hay un valor. Y entre dos "
                              "instantes, otros infinitos."),
                    zona="abajo", run_time=0.5)
        tv = ValueTracker(0.12)
        punta = always_redraw(
            lambda: Dot(on.en(tv.get_value(), SENAL_TELE(tv.get_value())),
                        radius=0.08, color=C_CIFRA))
        cifra = always_redraw(
            lambda: tag_hud(f"y = {fmt(SENAL_TELE(tv.get_value()), 2)}",
                            font_size=19).next_to(
                on.en(tv.get_value(), SENAL_TELE(tv.get_value())),
                UP, buff=0.22))
        self.play(FadeIn(punta), FadeIn(cifra), run_time=0.4)
        self.play(tv.animate.set_value(1.82), run_time=4.2,
                  rate_func=linear)
        self.wait(2.2)

        # --- momento: la radio no puede con todos -------------------------
        rot.mostrar(pie_curso("La radio manda simbolos, uno tras otro: "
                              "nadie puede transmitir infinitos valores."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(punta), FadeOut(cifra), run_time=0.4)
        self.wait(4.8)

        # --- momento: la idea de preguntar --------------------------------
        rot.mostrar(pie_curso("Medir no es copiar la curva: es preguntarle "
                              "su valor de vez en cuando."),
                    zona="abajo", run_time=0.5)
        guias = VGroup(*[on.vertical_en(t, color=C_BIT)
                         for t in (0.3, 0.7, 1.1, 1.5)])
        self.play(LaggedStart(*[Create(g) for g in guias], lag_ratio=0.3),
                  run_time=1.6)
        self.wait(5.6)

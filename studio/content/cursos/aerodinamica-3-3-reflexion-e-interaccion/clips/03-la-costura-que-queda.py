class Clip3(Scene):
    """3.3.3 - Interseccion de choques y linea de deslizamiento.

    Dos choques distintos se cruzan y detras tienen que ponerse de acuerdo:
    misma presion y misma direccion, o el cruce no se sostendria. Pero han
    pasado por historias distintas, asi que su temperatura y su Mach NO
    coinciden. La frontera entre ambas es una costura, no una onda.
    (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La costura que queda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        cruce = interseccion_choques(mach1=M_CRUCE, theta_sup=THETA_SUP,
                                     theta_inf=THETA_INF, ancho=6.6,
                                     alto=2.6)
        cruce.move_to(DOWN * 0.15)
        self.play(FadeIn(cruce.paredes), run_time=0.5)
        self.play(LaggedStart(*[Create(o) for o in cruce.incidentes],
                              lag_ratio=0.35), run_time=1.3)
        rot.mostrar(pie_curso("Dos cuñas distintas, dos choques distintos. Y "
                              "se van a encontrar."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        punto = Dot(cruce.cruce(), radius=0.08, color=C_TRANS)
        self.play(FadeIn(punto, scale=1.6), run_time=0.5)
        self.play(LaggedStart(*[Create(o) for o in cruce.refractados],
                              lag_ratio=0.3), run_time=1.1)
        rot.mostrar(pie_curso("Se cruzan y siguen, cada uno hacia la pared "
                              "de enfrente."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: lo que queda entre medias ----------------------------
        rot.mostrar(pie_curso("Detrás del cruce, las dos corrientes tienen "
                              "que llevar la misma presión y la misma "
                              "dirección."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        self.play(Create(cruce.deslizamiento), run_time=0.9)
        tag = Text("línea de deslizamiento", font_size=19, color=C_TRANS)
        tag.next_to(cruce.deslizamiento.get_end(), UR, buff=0.10)
        self.play(FadeIn(tag), run_time=0.5)
        rot.mostrar(pie_curso("Pero vienen de historias distintas, así que "
                              "su temperatura y su Mach no coinciden."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        cifras = VGroup(
            Text(f"arriba  M = {cruce.datos['M_sup']:.3f}", font=FUENTE_HUD,
                 font_size=18, color=C_CALCULO),
            Text(f"abajo   M = {cruce.datos['M_inf']:.3f}", font=FUENTE_HUD,
                 font_size=18,
                 color=C_SUB)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        cifras.next_to(cruce, DOWN, buff=0.28)
        self.play(FadeIn(cifras, shift=0.10 * UP), run_time=0.7)
        rot.mostrar(pie_curso("Esa frontera no es una onda: no hay salto de "
                              "presión. Es una costura entre dos flujos."),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)

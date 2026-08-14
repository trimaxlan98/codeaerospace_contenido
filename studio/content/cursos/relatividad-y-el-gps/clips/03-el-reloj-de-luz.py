class Clip3(Scene):
    """3 - El reloj de luz. EL argumento visual del curso: mismo foton,
    misma c, camino mas largo -> el tic se estira. La hipotenusa se MIDE
    en pantalla y de ahi sale gamma. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El reloj de luz")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: el reloj perfecto en reposo -------------------------
        rot.mostrar(pie_curso("Un reloj perfecto: un fotón que rebota "
                              "entre dos espejos."), zona="abajo",
                    run_time=0.5)
        reposo = reloj_luz(beta=0.0, tics=4).scale(0.72)
        reposo.shift(np.array([-5.3, 0.75, 0.0])
                     - reposo.espejos[0].get_center())
        self.play(Create(reposo.espejos[0]), Create(reposo.espejos[1]),
                  run_time=0.8)
        guia = reposo.camino[0].copy()
        guia.set_stroke(opacity=0.3)
        self.add(guia, reposo.foton)
        self.play(UpdateFromAlphaFunc(
            reposo.foton,
            lambda m, a: m.move_to(reposo.punto_camino(a))),
            run_time=3.0, rate_func=linear)
        tag_tic = tag_junto(reposo.espejos[0], "tic… tac…", DOWN,
                            font_size=16)
        self.play(FadeIn(tag_tic), run_time=0.4)
        self.wait(1.3)

        # --- momento: el mismo reloj, en movimiento -----------------------
        rot.mostrar(pie_curso("Súbelo al satélite: para ti, el fotón "
                              "recorre un zigzag más largo."),
                    zona="abajo", run_time=0.5)
        movil = reloj_luz(beta=BETA_RELOJ, tics=4).scale(0.72)
        movil.move_to(np.array([1.7, 0.0, 0.0]))
        movil.shift(UP * (0.75 - movil.espejos[0].get_center()[1]))
        self.play(Create(movil.espejos[0]), Create(movil.espejos[1]),
                  run_time=0.9)
        self.play(LaggedStart(*[Create(t) for t in movil.camino],
                              lag_ratio=0.25), run_time=2.2)
        self.add(movil.foton)
        self.play(UpdateFromAlphaFunc(
            movil.foton,
            lambda m, a: m.move_to(movil.punto_camino(a))),
            run_time=2.2, rate_func=linear)
        self.wait(0.8)

        # --- momento: la hipotenusa se mide -------------------------------
        rot.mostrar(pie_curso("Misma velocidad de la luz, camino más "
                              "largo: un reloj que se mueve late más "
                              "despacio."), zona="abajo", run_time=0.5)
        tramo = movil.camino[1].copy()
        tramo.set_stroke(color=C_SATELITE, width=5.0, opacity=1.0)
        # gamma MEDIDO sobre la geometria en pantalla, no citado
        gamma_medida = movil.longitud_camino()
        cifra_tramo = tag_hud(f"tramo = {gamma_medida:.2f} × altura",
                              font_size=16)
        cifra_tramo.next_to(movil.espejos[1], UP, buff=0.18)
        self.play(Create(tramo), run_time=0.7)
        self.play(FadeIn(cifra_tramo, shift=0.15 * UP), run_time=0.6)
        self.wait(2.1)

        # --- momento: la curva gamma --------------------------------------
        rot.mostrar(formula_pie(r"\gamma = \frac{1}{\sqrt{1-\beta^2}}",
                                font_size=30), zona="abajo", run_time=0.5)
        curva = curva_gamma().scale(0.72)
        curva.shift(np.array([0.9, -1.4, 0.0]) - curva.get_center())
        etiq_beta = tag_junto(curva.ejes[0], "v/c", RIGHT, buff=0.14,
                              font_size=14)
        self.play(Create(curva.ejes[0]), Create(curva.ejes[1]),
                  FadeIn(etiq_beta), run_time=0.7)
        self.play(Create(curva.curva), run_time=1.3)

        punto_medio = Dot(curva.en(BETA_EJEMPLO), radius=0.06,
                          color=C_SATELITE)
        cifra_media = tag_hud(
            f"γ({BETA_EJEMPLO}) = {GAMMA_EJEMPLO:.4f}", font_size=15)
        cifra_media.next_to(punto_medio, DOWN + RIGHT, buff=0.12)
        self.play(FadeIn(punto_medio, scale=0.4), FadeIn(cifra_media),
                  run_time=0.7)
        self.wait(1.4)

        punto_reloj = Dot(curva.en(BETA_RELOJ), radius=0.06, color=C_LUZ)
        cifra_reloj = tag_hud(
            f"nuestro zigzag: γ = {gamma_medida:.2f}", font_size=15,
            color=C_LUZ)
        cifra_reloj.next_to(punto_reloj, UP + LEFT, buff=0.12)
        cifra_reloj.shift(UP * 0.24)   # despegado de la zona plana
        self.play(FadeIn(punto_reloj, scale=0.4), FadeIn(cifra_reloj),
                  run_time=0.7)
        self.wait(1.6)

        # --- momento: la tesis ---------------------------------------------
        tesis = tag_junto(curva, "No parece: ES.", DOWN, buff=0.2,
                          font_size=18, color=C_SATELITE)
        tesis.next_to(cifra_media, DOWN + RIGHT, buff=0.25)
        self.play(FadeIn(tesis, shift=0.15 * UP), run_time=0.6)
        self.wait(5.2)

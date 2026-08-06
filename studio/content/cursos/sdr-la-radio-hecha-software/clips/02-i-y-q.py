class Clip2(Scene):
    """2 - I y Q: la señal hecha número. Un fasor ambar gira en un plano
    IQ a la izquierda mientras dos senoidales (I cian, Q violeta) se
    apilan a la derecha; el fasor da una vuelta lenta, pulsa su modulo,
    marca su fase con un arco y por ultimo separa con el sentido de giro
    lo que sube de lo que baja de la sintonia. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        ANGULO0 = np.deg2rad(35.0)

        # --- momento: HUD y titulo ---------------------------------------
        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("I y Q: la señal hecha número")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.7)

        # --- momento: el plano IQ con el fasor a la izquierda -------------
        plano = plano_iq(radio=1.7)
        plano.move_to(np.array([-3.2, -0.2, 0.0]))
        fasor_ = fasor(plano, angulo=ANGULO0, r=1.0, color=C_SENAL)

        self.play(Create(plano), FadeIn(fasor_, scale=0.9), run_time=1.2)
        self.wait(0.3)

        # --- momento: I y Q apiladas a la derecha --------------------------
        onda_i = onda_senoidal(fase=0.0, color=C_I)
        onda_i.move_to(np.array([3.0, 0.9, 0.0]))
        etiqueta_i = Text("I", font_size=28, color=C_I)
        etiqueta_i.next_to(onda_i, LEFT, buff=0.3)

        onda_q = onda_senoidal(fase=np.pi / 2.0, color=C_Q)
        onda_q.move_to(np.array([3.0, -0.9, 0.0]))
        etiqueta_q = Text("Q", font_size=28, color=C_Q)
        etiqueta_q.next_to(onda_q, LEFT, buff=0.3)

        self.play(FadeIn(VGroup(onda_i, etiqueta_i), shift=0.15 * RIGHT),
                  run_time=0.7)
        self.play(FadeIn(VGroup(onda_q, etiqueta_q), shift=0.15 * RIGHT),
                  run_time=0.7)
        self.wait(0.3)

        # --- momento: dos secuencias, un numero complejo -------------------
        rot.mostrar(pie_curso("El SDR entrega dos secuencias: la misma "
                              "señal contra dos relojes a 90 grados."),
                   zona="abajo", run_time=0.45)
        self.wait(5.4)

        rot.mostrar(formula_pie(r"z[n] = I[n] + j\,Q[n]"), zona="abajo",
                   run_time=0.45)
        self.wait(5.3)

        # --- momento: el fasor da una vuelta lenta -------------------------
        rot.mostrar(pie_curso("Cada pareja (I, Q) es un número complejo: "
                              "una flecha que gira."), zona="abajo",
                   run_time=0.45)
        self.play(girar_fasor(fasor_, ANGULO0 + 2.0 * np.pi, run_time=4.0))
        self.wait(1.0)

        # --- momento: el largo es la amplitud -------------------------------
        rot.mostrar(pie_curso("Su largo es la amplitud..."), zona="abajo",
                   run_time=0.45)
        self.play(Indicate(fasor_, scale_factor=1.15, color=C_SENAL),
                  run_time=1.0)
        self.wait(3.8)

        # --- momento: el angulo es la fase -----------------------------------
        rot.mostrar(pie_curso("...su ángulo es la fase."), zona="abajo",
                   run_time=0.45)
        arco = Arc(radius=0.5, start_angle=0.0, angle=ANGULO0,
                  arc_center=plano.centro(), color=C_SENAL, stroke_width=3.0)
        self.play(Create(arco), run_time=0.8)
        self.wait(4.0)
        self.play(FadeOut(arco), run_time=0.4)

        # --- momento: el sentido de giro separa encima de debajo ------------
        rot.mostrar(pie_curso("El sentido de giro separa lo que está "
                              "encima de la sintonía de lo que está "
                              "debajo. Una sola onda no puede."),
                   zona="abajo", run_time=0.5)

        tag_sube = tag_junto(plano, "sube", direccion=UP, buff=0.55,
                             color=C_OK)
        tag_sube.set_x(plano.centro()[0])
        self.play(FadeIn(tag_sube, shift=0.12 * UP), run_time=0.4)
        self.play(girar_fasor(fasor_, fasor_.angulo + np.pi, run_time=2.2))
        self.play(FadeOut(tag_sube, shift=0.12 * DOWN), run_time=0.35)

        tag_baja = tag_junto(plano, "baja", direccion=UP, buff=0.55,
                             color=C_Q)
        tag_baja.set_x(plano.centro()[0])
        self.play(FadeIn(tag_baja, shift=0.12 * UP), run_time=0.4)
        self.play(girar_fasor(fasor_, fasor_.angulo - np.pi, run_time=2.2))
        self.wait(3.0)
        self.play(FadeOut(tag_baja, shift=0.12 * DOWN), run_time=0.35)

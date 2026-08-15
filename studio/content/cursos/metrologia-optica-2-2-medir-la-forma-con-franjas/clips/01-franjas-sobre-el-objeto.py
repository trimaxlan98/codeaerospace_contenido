class Clip1(Scene):
    """1 - Franjas sobre el objeto. Un proyector tira franjas RECTAS sobre
    una pieza; el relieve las curva (la semiesfera vale 6 franjas de altura)
    y una camara que mira desde otro angulo convierte esa fase en altura por
    triangulacion: con theta = 45 grados una franja son 447 nm. Nadie toca
    la pieza. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Franjas sobre el objeto"), zona="arriba",
                    run_time=0.6)

        # --- geometria: la pieza a la izquierda, el esquema a la derecha ---
        # El cuadro (4.2 de lado) escalado a 0.78 mide 3.28: centrado en
        # (-3.05, -0.15) ocupa x[-4.69, -1.41], y[-1.79, 1.49]. La columna
        # derecha (proyector arriba, camara abajo) vive en x ~ 1.5 y el
        # bloque de la formula bajo ella, lejos de la marca de agua.
        ESC, SAG = 0.78, 6.0
        CENTRO = LEFT * 3.05 + DOWN * 0.15
        plano = objeto_franjas(fase0=0.0, n_franjas=7, sag_ondas=0.0)
        obj = objeto_franjas(fase0=0.0, n_franjas=7, sag_ondas=SAG)
        for pieza in (plano, obj):
            pieza.scale(ESC)
            # Se alinean por la IMAGEN, no por el bbox del Group: el rotulo
            # de cada pieza no dice lo mismo y correria el centro.
            pieza.shift(CENTRO - pieza.imagen.get_center())
        marco, contornos = obj.marco, obj.contornos
        rot_sag = obj.vectorial[2]      # "semiesfera:  6 franjas de altura"

        P = np.array([1.50, 1.95, 0.0])          # proyector (emite: rojo)
        Q = np.array([1.50, -0.95, 0.0])         # camara (mide: cian)
        punto = CENTRO + np.array([1.15, 0.30, 0.0])   # borde de la pieza

        dot_p = Dot(P, radius=0.11, color=C_HAZ)
        et_p = tag_junto(dot_p, "proyector", RIGHT, buff=0.18, font_size=19,
                         color=C_HAZ)
        rayo_p = Arrow(P, punto, buff=0.10, color=C_HAZ, stroke_width=3.0,
                       tip_length=0.20)
        dot_q = Dot(Q, radius=0.11, color=C_MEDIDA)
        et_q = tag_junto(dot_q, "cámara", RIGHT, buff=0.18, font_size=19,
                         color=C_MEDIDA)
        rayo_q = Arrow(punto, Q, buff=0.10, color=C_MEDIDA, stroke_width=3.0,
                       tip_length=0.20)

        a_p = angle_of_vector(P - punto)
        a_q = angle_of_vector(Q - punto)
        arco = Arc(radius=0.78, start_angle=a_q, angle=a_p - a_q,
                   arc_center=punto, color=C_TENUE, stroke_width=2.2)
        arco.set_stroke(opacity=0.75)
        medio = (a_p + a_q) / 2.0
        et_th = MathTex(r"\theta", font_size=30, color=C_TENUE)
        et_th.move_to(punto + 1.06 * np.array([math.cos(medio),
                                               math.sin(medio), 0.0]))

        t_sim = tag_hud("simulacion", font_size=13, color=C_TENUE)
        t_sim.next_to(marco, UP, buff=0.14).align_to(marco, LEFT)

        form = MathTex(r"z = \frac{\phi\,\lambda_f}{4\pi\,\sin\theta}",
                       font_size=34, color=C_MEDIDA)
        t_alt = tag_hud(f"1 franja = {altura_de_fase(TAU) * 1e9:.0f} nm de "
                        f"altura  (theta = 45 grados)", font_size=13,
                        color=C_TENUE)
        bloque = VGroup(form, t_alt).arrange(DOWN, buff=0.22)
        bloque.move_to(np.array([2.15, -2.05, 0.0]))

        # --- momento: proyectar franjas rectas ------------------------------
        rot.mostrar(pie_curso("Proyectamos franjas rectas sobre una pieza."),
                    zona="abajo")
        self.play(FadeIn(dot_p, scale=0.6), FadeIn(et_p), run_time=0.6)
        self.play(FadeIn(plano.imagen), Create(marco), FadeIn(t_sim),
                  run_time=1.0)
        self.play(GrowArrow(rayo_p), run_time=0.8)
        self.wait(4.3)

        # --- momento: el relieve curva las franjas --------------------------
        rot.mostrar(pie_curso("Sobre el relieve, las franjas se curvan: la "
                              "forma está en la fase."), zona="abajo")
        self.play(FadeTransform(plano.imagen, obj.imagen), run_time=1.3)
        self.play(Create(contornos, lag_ratio=0.25), FadeIn(rot_sag),
                  run_time=1.2)
        self.wait(4.2)

        # --- momento: la camara triangula -----------------------------------
        rot.mostrar(pie_curso("Una cámara las mira desde otro ángulo: la "
                              "triangulación convierte fase en altura."),
                    zona="abajo")
        self.play(FadeIn(dot_q, scale=0.6), FadeIn(et_q), run_time=0.6)
        self.play(GrowArrow(rayo_q), run_time=0.7)
        self.play(Create(arco), FadeIn(et_th), run_time=0.6)
        self.play(Write(form), run_time=1.1)
        self.play(FadeIn(t_alt), run_time=0.5)
        self.wait(4.0)

        # --- cierre ---------------------------------------------------------
        rot.mostrar(pie_curso("Nadie toca la pieza. La luz la recorre entera "
                              "de una vez."), zona="abajo")
        self.wait(5.5)

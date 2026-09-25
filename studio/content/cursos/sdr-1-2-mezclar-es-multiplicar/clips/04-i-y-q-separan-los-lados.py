class Clip4(Scene):
    """1.2.4 - Con LO real la deseada y la imagen caen en los DOS lados
    de la FI (S.mezcla_imagen(complejo=False)); con LO complejo cada una
    cae en un solo lado (complejo=True). No se rotula la profundidad del
    rechazo: depende de la malla. Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("I y Q separan los lados"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- el eje de salida: 0 en medio, +-FI a los lados -----------------
        base_y = -1.8
        eje = Line(LEFT * 5.4 + UP * base_y, RIGHT * 5.4 + UP * base_y,
                   color=S.C_EJE, stroke_width=1.8)
        x_pos, x_neg = 3.0, -3.0
        marca_cero = DashedLine(UP * (base_y + 4.1), UP * base_y,
                                color=S.C_EJE, stroke_width=1.6)
        et_cero = tag_dato("0 Hz", font_size=18)
        et_cero.next_to(marca_cero, DOWN, buff=0.16)

        marca_pos = DashedLine(RIGHT * x_pos + UP * (base_y + 4.1),
                               RIGHT * x_pos + UP * base_y, color=C_DATO,
                               stroke_width=1.6)
        et_pos = tag_dato("+" + mhz(F_IF) + " MHz", font_size=18)
        et_pos.next_to(marca_pos, DOWN, buff=0.16)
        marca_neg = DashedLine(LEFT * abs(x_neg) + UP * (base_y + 4.1),
                               LEFT * abs(x_neg) + UP * base_y,
                               color=C_DATO, stroke_width=1.6)
        et_neg = tag_dato("-" + mhz(F_IF) + " MHz", font_size=18)
        et_neg.next_to(marca_neg, DOWN, buff=0.16)

        self.play(Create(eje), Create(marca_cero), FadeIn(et_cero),
                  run_time=0.7)
        self.play(Create(marca_pos), Create(marca_neg), FadeIn(et_pos),
                  FadeIn(et_neg), run_time=0.8)
        self.wait(1.4)

        # --- alturas de las rayas (dB medidos, S.mezcla_imagen) --------------
        piso, alto_max = -50.0, 3.8

        def altura(db):
            return max(0.0, (db - piso) / (0.0 - piso)) * alto_max

        off = 0.18
        des_x_pos, img_x_pos = x_pos - off, x_pos + off
        des_x_neg, img_x_neg = x_neg - off, x_neg + off

        def raya(x, db, color):
            return Line(RIGHT * x + UP * base_y,
                       RIGHT * x + UP * (base_y + altura(db)),
                       color=color, stroke_width=5.0)

        r_des_pos = raya(des_x_pos, MEZ_REAL["deseada"][0], C_SENAL)
        r_des_neg = raya(des_x_neg, MEZ_REAL["deseada"][1], C_SENAL)
        r_img_pos = raya(img_x_pos, MEZ_REAL["imagen"][0], C_RUIDO)
        r_img_neg = raya(img_x_neg, MEZ_REAL["imagen"][1], C_RUIDO)

        modo = tag_junto(eje, "mezclador real", UP, buff=0.16, font_size=22,
                         color=C_DATO)
        modo.move_to(UP * (base_y + 4.5))
        self.play(FadeIn(modo), run_time=0.5)
        self.play(Create(r_des_pos), Create(r_des_neg), Create(r_img_pos),
                  Create(r_img_neg), run_time=1.4)
        self.wait(4.6)

        # --- con LO complejo: cada una a un solo lado -------------------------
        modo2 = tag_junto(eje, "mezclador complejo", UP, buff=0.16,
                          font_size=22, color=C_LO)
        modo2.move_to(modo)
        n_des_pos = raya(des_x_pos, MEZ_CPLX["deseada"][0], C_SENAL)
        n_des_neg = raya(des_x_neg, MEZ_CPLX["deseada"][1], C_SENAL)
        n_img_pos = raya(img_x_pos, MEZ_CPLX["imagen"][0], C_RUIDO)
        n_img_neg = raya(img_x_neg, MEZ_CPLX["imagen"][1], C_RUIDO)

        self.play(Transform(modo, modo2), run_time=0.5)
        self.play(Transform(r_des_pos, n_des_pos),
                  Transform(r_des_neg, n_des_neg),
                  Transform(r_img_pos, n_img_pos),
                  Transform(r_img_neg, n_img_neg), run_time=1.8)
        self.wait(1.8)

        et_des = tag_junto(r_des_pos, "deseada", UP, buff=0.2, font_size=20,
                           color=C_SENAL)
        et_img = tag_junto(r_img_neg, "imagen", UP, buff=0.2, font_size=20,
                           color=C_RUIDO)
        self.play(FadeIn(et_des), FadeIn(et_img), run_time=0.6)
        self.wait(5.6)

        cierre_leccion(self, rot, "Mezclar es mover el espectro.",
                       "Con I y Q, hacia un solo lado.", eje, marca_cero,
                       et_cero, marca_pos, et_pos, marca_neg, et_neg, modo,
                       r_des_pos, r_des_neg, r_img_pos, r_img_neg, et_des,
                       et_img, espera=7.0)

class Clip2(Scene):
    """1.2.2 - Un mezclador real no distingue la deseada de su imagen:
    las dos caen en la MISMA FI (S.imagen_real). La imagen llega con la
    misma diferencia con la que emitia (S.mezcla_imagen). (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La frecuencia imagen"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- el eje de RF: LO en medio, deseada e imagen a +-FI --------------
        escala = 0.34e-6  # unidades de pantalla por Hz (mapeo, no una cifra)

        def x_de(f):
            return (f - F_LO) * escala

        centro_eje = UP * 1.8
        eje = Line(centro_eje + LEFT * 5.2, centro_eje + RIGHT * 5.2,
                   color=S.C_EJE, stroke_width=1.8)

        def punto(f):
            return centro_eje + RIGHT * x_de(f)

        dot_lo = Dot(punto(F_LO), radius=0.09, color=C_LO)
        dot_senal = Dot(punto(F_SENAL), radius=0.09, color=C_SENAL)
        dot_imagen = Dot(punto(F_IMG), radius=0.09, color=C_RUIDO)

        self.play(Create(eje), run_time=0.6)
        self.play(FadeIn(dot_lo), run_time=0.5)
        nom_lo = tag_junto(dot_lo, "LO", UP, buff=0.5, font_size=20,
                           color=C_LO)
        frec_lo = tag_dato(mhz(F_LO) + " MHz", font_size=18)
        frec_lo.next_to(nom_lo, DOWN, buff=0.08)
        self.play(FadeIn(nom_lo), FadeIn(frec_lo), run_time=0.5)
        self.wait(2.2)

        self.play(FadeIn(dot_senal), run_time=0.5)
        nom_senal = tag_junto(dot_senal, "deseada", UP, buff=0.5,
                              font_size=20, color=C_SENAL)
        frec_senal = tag_dato(mhz(F_SENAL) + " MHz", font_size=18)
        frec_senal.next_to(nom_senal, DOWN, buff=0.08)
        self.play(FadeIn(nom_senal), FadeIn(frec_senal), run_time=0.5)
        self.wait(1.6)

        self.play(FadeIn(dot_imagen), run_time=0.5)
        nom_imagen = tag_junto(dot_imagen, "imagen", UP, buff=0.5,
                               font_size=20, color=C_RUIDO)
        frec_imagen = tag_hud(mhz(F_IMG) + " MHz", font_size=18,
                              color=C_CALCULO)
        frec_imagen.next_to(nom_imagen, DOWN, buff=0.08)
        self.play(FadeIn(nom_imagen), FadeIn(frec_imagen), run_time=0.5)
        self.wait(2.2)

        # --- las dos flechas bajan a la MISMA raya de FI ----------------------
        punto_fi = centro_eje + DOWN * 3.6
        flecha_senal = Arrow(dot_senal.get_center(), punto_fi, buff=0.14,
                             color=C_SENAL, stroke_width=3.2,
                             max_tip_length_to_length_ratio=0.12)
        flecha_imagen = Arrow(dot_imagen.get_center(), punto_fi, buff=0.14,
                              color=C_RUIDO, stroke_width=3.2,
                              max_tip_length_to_length_ratio=0.12)
        self.play(GrowArrow(flecha_senal), GrowArrow(flecha_imagen),
                  run_time=1.2)
        marca_fi = DashedLine(punto_fi + UP * 0.32, punto_fi + DOWN * 0.32,
                              color=C_DATO, stroke_width=2.2)
        et_fi = tag_dato(mhz(F_IF) + " MHz", font_size=20)
        et_fi.next_to(marca_fi, DOWN, buff=0.2)
        cae = tag_junto(marca_fi, "cae en la FI", RIGHT, buff=0.35,
                        font_size=20)
        self.play(Create(marca_fi), FadeIn(et_fi), FadeIn(cae), run_time=0.8)
        self.wait(3.4)

        diferencia = MEZ_REAL["deseada"][0] - MEZ_REAL["imagen"][0]
        rot.mostrar(cifra_pie(f"diferencia: {fmt(diferencia, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
        rot.mostrar(formula_pie(r"f_{LO} - f_{IF} = f_{imagen}"),
                    zona="abajo", run_time=0.5)
        self.wait(6.5)

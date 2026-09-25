class Clip4(Scene):
    """2.3.4 - Un filtro que rechaza la banda de FM se pone delante del
    amplificador: la emisora llega hecha nada y el satelite recupera la
    ganancia que tenia antes de que ella se encendiera. Cierre. Formato
    mudo: sin pie narrado, solo datos reales y cifras. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El filtro de banda"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        f_lo, f_hi = 90e6, 145e6
        ancho_eje = 10.6
        y_eje = DOWN * 2.15

        def x_de(f):
            return (f - f_lo) / (f_hi - f_lo) * ancho_eje - ancho_eje / 2

        eje = Line(y_eje + LEFT * ancho_eje / 2, y_eje + RIGHT * ancho_eje / 2,
                  color=C_TENUE, stroke_width=1.8)
        x1, x2 = x_de(F1), x_de(F_SAT)
        t1 = tag_dato(f"{mhz(F1)} MHz", font_size=18)
        t2 = tag_dato(f"{mhz(F_SAT)} MHz", font_size=18)
        t1.next_to(y_eje + RIGHT * x1, DOWN, buff=0.2)
        t2.next_to(y_eje + RIGHT * x2, DOWN, buff=0.2)
        self.play(Create(eje), FadeIn(t1), FadeIn(t2), run_time=0.8)

        db_min, db_max, alto_max = 0.0, 25.0, 2.9

        def h(db):
            return alto_max * float(np.clip(db, db_min, db_max) - db_min) \
                / (db_max - db_min)

        def raya(x, altura, color):
            r = Rectangle(width=0.5, height=max(altura, 0.02),
                          stroke_width=0, fill_color=color, fill_opacity=0.9)
            r.move_to(y_eje + RIGHT * x + UP * altura / 2)
            return r

        # --- rotulos de mobiliario a un lado de cada barra: fijos, no se
        # mueven aunque la barra cambie de altura ---------------------------
        p_fm = y_eje + RIGHT * (x1 + 0.25) + UP * 1.8
        p_sat = y_eje + RIGHT * (x2 - 0.25) + UP * 1.8
        et_fm = tag_junto(p_fm, "emisora FM", RIGHT, buff=0.35, color=C_SENAL)
        et_sat = tag_junto(p_sat, "satelite", LEFT, buff=0.35, color=C_OK)

        raya_fm = raya(x1, 3.2, C_SENAL)
        raya_sat = raya(x2, h(G_LIN + DESENS), C_OK)
        self.play(FadeIn(raya_fm), FadeIn(raya_sat), FadeIn(et_fm),
                  FadeIn(et_sat), run_time=0.9)
        self.wait(3.2)

        # --- el filtro, contexto arriba a la izquierda: FILTRO->AMPLIFICADOR,
        # sin flecha desde el eje --------------------------------------------
        filtro = S.bloque("FILTRO", ancho=1.9, alto=0.55, color=C_TENUE,
                          tamano=17)
        filtro.move_to(LEFT * 5.0 + UP * 2.5)
        amp = S.bloque("AMPLIFICADOR", ancho=2.6, alto=0.6, color=C_TENUE,
                       tamano=18)
        amp.move_to(LEFT * 2.1 + UP * 2.5)
        con = S.conectar(filtro, amp, color=C_TENUE, grosor=2.0)
        self.play(FadeIn(filtro), FadeIn(amp), Create(con), run_time=0.9)
        rot.mostrar(dato_pie("40 dB de rechazo"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        # --- la emisora llega hecha nada; el satelite se recupera -----------
        factor = 10 ** (-S.ATEN_FILTRO_DB / 20)
        raya_fm2 = raya(x1, 3.2 * factor, C_SENAL)
        self.play(Transform(raya_fm, raya_fm2),
                  S.flujo([con], color=C_SENAL, por_conexion=0.5),
                  run_time=1.3)
        self.wait(1.4)

        _trasf = TRAS_FILTRO if round(TRAS_FILTRO, 1) != 0.0 else 0.0
        raya_sat2 = raya(x2, h(G_LIN + _trasf), C_OK)
        self.play(Transform(raya_sat, raya_sat2), run_time=1.3)
        rot.mostrar(cifra_pie(f"{fmt(_trasf, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(7.0)

        cierre_leccion(self, rot, "Lo fuerte tambien estorba.",
                       "Filtra antes de amplificar.", eje, t1, t2, raya_fm,
                       raya_sat, et_fm, et_sat, filtro, amp, con)

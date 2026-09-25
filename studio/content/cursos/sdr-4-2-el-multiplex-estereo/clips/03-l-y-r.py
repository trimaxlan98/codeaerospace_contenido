# Onda no viene en sdr.py (solo PlanoIQ): se trae directo de comunicaciones,
# que ya esta cargada porque sdr.py la importa. Mismo patron que 1.2.1.
from comunicaciones import Onda  # noqa: E402


class Clip3(Scene):
    """4.2.3 - L y R: la matriz de la desmodulacion estereo (L = S+D,
    R = S-D) como bloques, y las dos trazas cortas ya separadas (verde:
    L 1 kHz, R 3 kHz). Con el piloto enganchado, 59.3 dB de separacion;
    con 5 grados de error de fase, 48.4 dB. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("L y R"), zona="arriba", run_time=0.6)
        self.wait(0.6)

        # --- la matriz, como bloques -----------------------------------------
        s_box = bloque("S", ancho=1.6, alto=0.85, color=C_TENUE, tamano=30)
        d_box = bloque("D", ancho=1.6, alto=0.85, color=C_TENUE, tamano=30)
        l_box = bloque("L", ancho=1.6, alto=0.85, color=C_OK, tamano=30)
        r_box = bloque("R", ancho=1.6, alto=0.85, color=C_OK, tamano=30)
        s_box.move_to(LEFT * 4.6 + UP * 1.5)
        d_box.move_to(LEFT * 4.6 + DOWN * 1.5)
        l_box.move_to(RIGHT * 4.6 + UP * 1.5)
        r_box.move_to(RIGHT * 4.6 + DOWN * 1.5)
        self.play(FadeIn(s_box, shift=RIGHT * 0.15),
                  FadeIn(d_box, shift=RIGHT * 0.15), run_time=0.6)
        self.wait(0.4)
        self.play(FadeIn(l_box, shift=LEFT * 0.15),
                  FadeIn(r_box, shift=LEFT * 0.15), run_time=0.6)
        self.wait(0.6)

        a_sl = conectar(s_box, l_box, color=C_TENUE, grosor=2.2)
        a_sr = conectar(s_box, r_box, color=C_TENUE, grosor=2.2)
        a_dl = conectar(d_box, l_box, color=C_TENUE, grosor=2.2)
        a_dr = conectar(d_box, r_box, color=C_TENUE, grosor=2.2)
        signo_sl = Text("+", font=FUENTE_HUD, font_size=24, color=C_TENUE)
        signo_sl.move_to(a_sl.point_from_proportion(0.78) + UP * 0.2)
        signo_sr = Text("+", font=FUENTE_HUD, font_size=24, color=C_TENUE)
        signo_sr.move_to(a_sr.point_from_proportion(0.78) + DOWN * 0.2)
        signo_dl = Text("+", font=FUENTE_HUD, font_size=24, color=C_TENUE)
        signo_dl.move_to(a_dl.point_from_proportion(0.78) + UP * 0.2)
        signo_dr = Text("-", font=FUENTE_HUD, font_size=24, color=C_TENUE)
        signo_dr.move_to(a_dr.point_from_proportion(0.78) + DOWN * 0.2)
        self.play(Create(a_sl), Create(a_dr), FadeIn(signo_sl),
                  FadeIn(signo_dr), run_time=0.9)
        self.wait(0.5)
        self.play(Create(a_sr), Create(a_dl), FadeIn(signo_sr),
                  FadeIn(signo_dl), run_time=0.9)
        self.wait(1.6)
        rot.mostrar(formula_pie(r"L = S+D \qquad R = S-D"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        diagrama = VGroup(s_box, d_box, l_box, r_box, a_sl, a_sr, a_dl,
                          a_dr, signo_sl, signo_sr, signo_dl, signo_dr)
        self.play(FadeOut(diagrama), run_time=0.7)
        rot.limpiar(zona="abajo", run_time=0.3)

        # --- las dos trazas ya separadas, verde -------------------------------
        n0, n1 = 4000, 4700
        t_ms = np.arange(n1 - n0) / FS * 1e3
        o_l = Onda(t_ms, L_RX[n0:n1], ancho=10.6, alto=1.3, color=C_OK)
        o_r = Onda(t_ms, R_RX[n0:n1], ancho=10.6, alto=1.3, color=C_OK)
        grupo = VGroup(o_l, o_r).arrange(DOWN, buff=0.7)
        grupo.move_to(UP * 0.2)
        et_l = tag_junto(o_l, "L 1 kHz", LEFT, buff=0.3, font_size=18,
                         color=C_OK)
        et_r = tag_junto(o_r, "R 3 kHz", LEFT, buff=0.3, font_size=18,
                         color=C_OK)
        self.play(Create(o_l.ejes), Create(o_r.ejes), FadeIn(et_l),
                  FadeIn(et_r), run_time=0.6)
        self.play(Create(o_l.curva), run_time=1.2)
        self.play(Create(o_r.curva), run_time=1.2)
        self.wait(1.6)
        rot.mostrar(cifra_pie(f"separacion: {fmt(SEPARACION, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        o_l2 = o_l.con_serie(L5[n0:n1])
        o_r2 = o_r.con_serie(R5[n0:n1])
        self.play(Transform(o_l.curva, o_l2.curva),
                  Transform(o_r.curva, o_r2.curva), run_time=1.6)
        self.wait(1.0)
        rot.mostrar(dato_pie("5 grados de error"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)
        rot.mostrar(cifra_pie(f"{fmt(SEPARACION_5, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(4.5)

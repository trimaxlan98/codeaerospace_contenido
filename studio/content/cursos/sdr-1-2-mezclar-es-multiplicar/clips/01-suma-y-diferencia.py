# Onda no viene en sdr.py (solo PlanoIQ): se trae directo de comunicaciones,
# que ya esta cargada porque sdr.py la importa. Mismo patron que control.py
# en sistemas-atp.
from comunicaciones import Onda  # noqa: E402


class Clip1(Scene):
    """1.2.1 - Multiplicar dos ondas mueve el espectro: aparece la suma y
    la diferencia de las dos frecuencias (S.mezclar_real). Las ondas del
    tiempo son a escala ilustrativa; el espectro usa las frecuencias
    reales. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Suma y diferencia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- multiplicar en el tiempo (escala ilustrativa) ------------------
        t = np.linspace(0.0, 1.0, 600)
        x_senal = np.cos(2 * np.pi * 9.0 * t)
        x_lo = np.cos(2 * np.pi * 7.0 * t)
        prod = x_senal * x_lo

        o_senal = Onda(t, x_senal, ancho=10.8, alto=1.15, color=C_SENAL)
        o_lo = Onda(t, x_lo, ancho=10.8, alto=1.15, color=C_LO)
        o_prod = Onda(t, prod, ancho=10.8, alto=1.15, color=C_CALCULO)
        grupo = VGroup(o_senal, o_lo, o_prod).arrange(DOWN, buff=0.4)

        et_senal = tag_junto(o_senal, "senal", LEFT, buff=0.3, font_size=20,
                             color=C_SENAL)
        et_lo = tag_junto(o_lo, "LO", LEFT, buff=0.3, font_size=20,
                          color=C_LO)
        et_prod = tag_junto(o_prod, "producto", LEFT, buff=0.3,
                            font_size=20, color=C_CALCULO)
        ilustr = tag_junto(grupo, "escala ilustrativa", DOWN, buff=0.24,
                           font_size=18)

        self.play(Create(o_senal.curva), FadeIn(et_senal), run_time=1.0)
        self.wait(0.8)
        self.play(Create(o_lo.curva), FadeIn(et_lo), run_time=1.0)
        self.wait(0.8)
        self.play(Create(o_prod.curva), FadeIn(et_prod), FadeIn(ilustr),
                  run_time=1.2)
        self.wait(2.8)

        # --- el espectro real del producto -----------------------------------
        self.play(FadeOut(grupo), FadeOut(et_senal), FadeOut(et_lo),
                  FadeOut(et_prod), FadeOut(ilustr), run_time=0.6)

        f, db = S.para_dibujar(_ESP_F, _ESP_DB, 900, 0, 250e6)
        esp = S.Espectro(f, db, piso=-60.0, techo=2.0, ancho=12.2, alto=3.6,
                         color=C_SENAL)
        esp.move_to(DOWN * 0.15)
        ticks = esp.marcas([0, 50e6, 100e6, 150e6, 200e6, 250e6],
                           ["0", "50", "100", "150", "200", "250"])
        u = tag_junto(ticks[-1], "MHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.7)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.8)
        self.wait(1.4)

        m_dif = esp.marca_f(F_DIF)
        self.play(Create(m_dif), run_time=0.6)
        rot.mostrar(cifra_pie(f"diferencia: {mhz(F_DIF)} MHz"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        m_suma = esp.marca_f(F_SUMA)
        self.play(Create(m_suma), run_time=0.6)
        rot.mostrar(cifra_pie(f"suma: {mhz(F_SUMA)} MHz"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"\cos a \cos b = \tfrac{1}{2}"
                                r"[\cos(a{-}b) + \cos(a{+}b)]"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)
        rot.mostrar(dato_pie(f"FI de FM: {mhz(F_IF)} MHz"), zona="abajo",
                    run_time=0.5)
        self.wait(3.8)

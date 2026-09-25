# Onda no viene en sdr.py (solo PlanoIQ): se trae directo de comunicaciones,
# que ya esta cargada porque sdr.py la importa. Mismo patron que 1.2.1.
from comunicaciones import Onda  # noqa: E402


class Clip2(Scene):
    """4.2.2 - El piloto: el error de fase del PLL (fucsia, suavizado con un
    paso bajo de 500 Hz para verse por encima del ripple del propio MPX)
    cae a menos de 0.01 rad; despues, la subportadora regenerada = cos(2 x
    fase del piloto) enganchada, dos ciclos por cada uno del piloto.
    (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El piloto"), zona="arriba", run_time=0.6)
        self.wait(0.8)

        # --- el error del lazo cae a cero al engancharse ---------------------
        h = S.fir_paso_bajo(101, 500.0, FS)
        e_lp = np.convolve(ERR_P, h, mode="same")
        ventana = 20000
        idx = np.linspace(0, ventana - 1, 420).astype(int)
        t_ms = idx / FS * 1e3
        y = e_lp[idx]

        o = Onda(t_ms, y, rango_y=(-0.02, 0.02), ancho=11.0, alto=3.7,
                 color=C_LO)
        o.move_to(DOWN * 0.15)
        cero = o.horizontal_en(0.0, color=C_TENUE)
        et_y = tag_junto(o, "error de fase", UP, buff=0.25, font_size=20,
                         color=C_LO)
        et_x = tag_junto(o, "ms", RIGHT, buff=0.2, font_size=18)
        self.play(Create(o.ejes), Create(cero), FadeIn(et_y), FadeIn(et_x),
                  run_time=0.8)
        self.play(Create(o.curva), run_time=3.0)
        self.wait(2.4)
        rot.mostrar(cifra_pie("menos de 0.01 rad"), zona="abajo",
                    run_time=0.5)
        self.wait(7.0)

        self.play(FadeOut(o), FadeOut(cero), FadeOut(et_y), FadeOut(et_x),
                  run_time=0.7)
        rot.limpiar(zona="abajo", run_time=0.3)

        # --- la subportadora regenerada, dos ciclos por uno del piloto ------
        idx0 = 20500
        nc = 72
        tt = np.arange(nc) / FS * 1e3
        pil = np.cos(FASE_P[idx0:idx0 + nc])
        sub = np.cos(2.0 * FASE_P[idx0:idx0 + nc])

        o_pil = Onda(tt, pil, rango_y=(-1.25, 1.25), ancho=9.6, alto=1.3,
                     color=C_LO)
        o_sub = Onda(tt, sub, rango_y=(-1.25, 1.25), ancho=9.6, alto=1.3,
                     color=C_LO)
        grupo = VGroup(o_pil, o_sub).arrange(DOWN, buff=1.0)
        grupo.move_to(UP * 0.1)
        et_pil = tag_junto(o_pil, "piloto 19 kHz", UP, buff=0.15,
                           font_size=18, color=C_LO)
        et_sub = tag_junto(o_sub, "subportadora 38 kHz", UP, buff=0.15,
                           font_size=18, color=C_LO)
        self.play(Create(o_pil.ejes), Create(o_sub.ejes), FadeIn(et_pil),
                  FadeIn(et_sub), run_time=0.7)
        self.play(Create(o_pil.curva), run_time=1.6)
        self.play(Create(o_sub.curva), run_time=1.6)
        self.wait(3.2)
        rot.mostrar(formula_pie(r"38 = 2 \times 19"), zona="abajo",
                    run_time=0.5)
        self.wait(8.0)

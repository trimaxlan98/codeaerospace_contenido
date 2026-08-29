# EL WINDUP VIVE EN LA ADQUISICION, no en el seguimiento. Esta medido en
# el docstring de `simular_adquisicion`: a esta escala de planta el par de
# SEGUIMIENTO pica en 0.108 N m, asi que un accionamiento sensato no
# satura nunca siguiendo el pase (ni el cenital), y una rafaga mayor que
# el motor no da windup sino PERDIDA DE CONTROL. El windup de libro pide
# un salto de referencia grande con el actuador en su tope: eso es
# exactamente el preposicionamiento de 60 grados antes del AOS, que ademas
# es la primera fase del ATP.
T_ADQ = float(ADQ_SIN["t"][-1])
Y_TOPE = float(max(ADQ_SIN["real"].max(), ADQ_CON["real"].max())) * 1.06
U_TOPE = float(np.max(np.abs(ADQ_SIN["u"])))
T_VENT = T_ADQ - 5.0                       # la ventana final del zoom
TAS_SIN = ADQ_SIN["t_asentamiento"]
TXT_TAS_SIN = "inf" if math.isinf(TAS_SIN) else fmt(TAS_SIN, 2)


def _en_t(clave, cual):
    """Interpolador de una serie de la simulacion, para `grafica`."""
    d = ADQ_SIN if cual == "sin" else ADQ_CON
    return lambda x: float(np.interp(x, d["t"], d[clave]))


class Clip4(Scene):
    """2.3.4 - El windup: el integrador sigue cargando mientras el par
    esta en su tope. En la adquisicion, sin clamping la montura se pasa
    27.7 grados y NO se asienta dentro del presupuesto en 40 s. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Windup"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- la adquisicion: un salto grande antes del AOS ---------------
        g = grafica(_en_t("real", "sin"), (0.0, T_ADQ), (0.0, Y_TOPE),
                    ancho=6.4, alto=2.6, color=C_PELIGRO, muestras=281,
                    etiqueta_x="t s", etiqueta_y="deg")
        g.move_to(UP * 0.95)
        ref = g.horizontal_en(SALTO_ADQ, color=C_SAT)
        ref.set_stroke(width=2.6)
        self.play(Create(g.ejes), run_time=0.9)
        self.play(Create(ref), run_time=0.6)
        # El rotulo va FUERA de la caja, a la izquierda del eje: puesto
        # sobre el arranque de la referencia se le encimaban la linea
        # ambar y las dos curvas.
        t_ref = tag_hud(f"salto {fmt(SALTO_ADQ, 0)} deg", font_size=19,
                        color=C_SAT)
        t_ref.next_to(ref.get_start(), LEFT, buff=0.16)
        self.play(FadeIn(t_ref), run_time=0.5)
        rot.mostrar(cifra_pie(f"adquisicion {fmt(SALTO_ADQ, 0)} deg"),
                    zona="abajo")
        self.wait(1.2)

        self.play(Create(g.curva), run_time=2.6)
        rot.mostrar(cifra_pie(f"sobreimpulso {fmt(SOBRE_SIN, 1)} deg",
                              color=C_PELIGRO), zona="abajo")
        self.wait(2.0)

        # --- el par, pegado a su tope -----------------------------------
        gu = grafica(_en_t("u", "sin"), (0.0, T_ADQ),
                     (-U_TOPE * 1.30, U_TOPE * 1.30), ancho=6.4, alto=1.0,
                     color=C_PELIGRO, muestras=281, etiqueta_y="par")
        gu.move_to(DOWN * 1.85)
        gu.shift(RIGHT * float(g.punto_de(0.0)[0] - gu.punto_de(0.0)[0]))
        tope_sup = gu.horizontal_en(U_TOPE, color=C_PELIGRO)
        tope_inf = gu.horizontal_en(-U_TOPE, color=C_PELIGRO)
        self.play(Create(gu.ejes), run_time=0.6)
        self.play(Create(tope_sup), Create(tope_inf), run_time=0.6)
        self.play(Create(gu.curva), run_time=1.8)
        rot.mostrar(cifra_pie(f"saturado {fmt(SAT_SIN * 100.0, 0)} % "
                              f"del tiempo", color=C_PELIGRO),
                    zona="abajo")
        self.wait(2.0)

        # --- el clamping: la misma subida, otra llegada ------------------
        g2 = grafica(_en_t("real", "con"), (0.0, T_ADQ), (0.0, Y_TOPE),
                     ancho=6.4, alto=2.6, color=C_OK, muestras=281)
        g2.shift(np.asarray(g.punto_de(0.0), dtype=float)
                 - np.asarray(g2.punto_de(0.0), dtype=float))
        self.play(Create(g2.curva), run_time=2.2)
        rot.mostrar(cifra_pie(f"con clamping {fmt(SOBRE_CON, 1)} deg",
                              color=C_OK), zona="abajo")
        self.wait(2.0)

        panel = panel_cifras(
            (f"sobre sin {fmt(SOBRE_SIN, 1)} deg", C_PELIGRO),
            (f"sobre con {fmt(SOBRE_CON, 1)} deg", C_OK),
            (f"sat {fmt(SAT_SIN * 100.0, 0)} %", C_PELIGRO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.2)

        self.play(FadeOut(g.ejes), FadeOut(g.curva), FadeOut(g2.curva),
                  FadeOut(ref), FadeOut(t_ref), FadeOut(gu.ejes),
                  FadeOut(gu.curva), FadeOut(tope_sup), FadeOut(tope_inf),
                  FadeOut(panel), run_time=0.8)

        # --- el remate: los ultimos cinco segundos ----------------------
        # Se dibuja el MODULO del error: el presupuesto es sobre la
        # magnitud, y con el error firmado (siempre negativo aqui) la caja
        # quedaba vacia por arriba y el dibujo aplastado abajo.
        m = ADQ_SIN["t"] >= T_VENT
        tr = traza_error(ADQ_SIN["t"][m], np.abs(ADQ_SIN["error"][m]),
                         ancho=6.0, alto=2.2, y_max=0.62, color=C_PELIGRO,
                         etiqueta_x=None, etiqueta_y="err deg")
        tr.shift(DOWN * 0.85 - tr.cero.get_center())
        # Como en el clip 2: la etiqueta del eje t que trae la pieza cae
        # dentro de la banda, asi que se pone a mano mas abajo.
        t_eje = tag_hud(f"t {fmt(T_VENT, 0)}-{fmt(T_ADQ, 0)} s",
                        font_size=17, color=C_TENUE)
        t_eje.move_to(tr.cero.get_end() + DOWN * 0.62 + LEFT * 0.35)
        self.play(Create(tr.ejes), Create(tr.cero), FadeIn(t_eje),
                  run_time=0.7)
        self.play(FadeIn(tr.banda), Create(tr.borde_sup),
                  Create(tr.borde_inf), run_time=0.8)
        t_banda = tag_hud(f"+-{fmt(OBJETIVO_DEG, 1)} deg", font_size=19)
        t_banda.next_to(tr.borde_sup, RIGHT, buff=0.14)
        self.play(FadeIn(t_banda), run_time=0.5)

        self.play(Create(tr.curva), run_time=1.6)
        self.remove(*tr.get_family())
        self.add(tr)
        rot.mostrar(cifra_pie(f"sin clamping: t_est = {TXT_TAS_SIN}",
                              color=C_PELIGRO), zona="abajo")
        self.wait(2.2)

        tr_con = tr.gemela(np.abs(ADQ_CON["error"][m]), color=C_OK)
        tr_con.shift(DOWN * 0.85 - tr_con.cero.get_center())
        self.play(Create(tr_con.curva), run_time=1.6)
        rot.mostrar(cifra_pie(f"con clamping t_est {fmt(TAS_CON, 2)} s",
                              color=C_OK), zona="abajo")
        self.wait(2.4)

        cierre_leccion(self, rot,
                       "El pase es una rampa",
                       "y solo la integral borra el rezago.",
                       tr, tr_con.curva, t_banda, t_eje, espera=4.2)

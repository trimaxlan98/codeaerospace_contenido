import control as _control  # noqa: E402

_control.Text = Text
from control import respuesta_escalon  # noqa: E402

# La ventana de tiempo sale del propio dato: tiene que caber el
# establecimiento del caso lento, que es el peor de los dos.
T_VENTANA = TS_P * 1.15


class Clip3(Scene):
    """2.3.3 - Con kp solo, el lazo es un timbre: 83.9 % de sobreimpulso
    y medio minuto para asentarse. La derivada lo amortigua y se asienta
    12.5 veces mas rapido... y no toca el arrastre. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("D amortigua, I limpia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- La respuesta al escalon, con y sin D ------------------------
        rp = respuesta_escalon(ZETA_P, WN_P, ancho=6.2, alto=2.4,
                               t_max=T_VENTANA, color=C_PELIGRO,
                               color_ref=C_SAT)
        rp.move_to(UP * 1.05)
        # La referencia queda DEBAJO de trece oscilaciones: se sube de
        # capa y se engorda, o no se ve que la curva oscila en torno a
        # algo.
        rp.linea_ref.set_stroke(width=3.0, opacity=1.0)
        rp.linea_ref.set_z_index(3)
        self.play(Create(rp.ejes), FadeIn(rp.etiquetas), run_time=0.8)
        self.play(Create(rp.linea_ref), run_time=0.6)
        self.play(Create(rp.curva), run_time=2.6)
        rot.mostrar(cifra_pie(f"zeta {fmt(ZETA_P, 3)}", color=C_PELIGRO),
                    zona="abajo")
        self.wait(1.6)
        rot.mostrar(cifra_pie(f"sobreimpulso {fmt(MP_P * 100.0, 1)} %",
                              color=C_PELIGRO), zona="abajo")
        self.wait(2.0)

        def _marca(t_s, color):
            """Vertical punteada en el instante `t_s` del eje dibujado."""
            base = np.asarray(rp.eje_t.get_start(), dtype=float)
            x = base + RIGHT * (t_s / T_VENTANA) * float(rp.eje_t.width)
            return DashedLine(x, x + UP * float(rp.eje_y.height),
                              color=color, stroke_width=2.4,
                              dash_length=0.09)

        m_p = _marca(TS_P, C_PELIGRO)
        self.play(Create(m_p), run_time=0.8)
        rot.mostrar(cifra_pie(f"t_est {fmt(TS_P, 1)} s", color=C_PELIGRO),
                    zona="abajo")
        self.wait(2.0)

        rd = respuesta_escalon(ZETA_D, WN_D, ancho=6.2, alto=2.4,
                               t_max=T_VENTANA, color=C_CALCULO,
                               color_ref=C_SAT)
        # Los dos juegos de ejes son identicos: se alinean POR EL EJE, no
        # por el bounding box (que si depende de la curva).
        rd.shift(np.asarray(rp.eje_t.get_start(), dtype=float)
                 - np.asarray(rd.eje_t.get_start(), dtype=float))
        self.play(Create(rd.curva), run_time=2.0)
        rot.mostrar(cifra_pie(f"zeta {fmt(ZETA_D, 2)}"), zona="abajo")
        self.wait(1.6)
        rot.mostrar(cifra_pie(f"sobreimpulso {fmt(MP_D * 100.0, 1)} %"),
                    zona="abajo")
        self.wait(1.8)

        m_d = _marca(TS_D, C_CALCULO)
        self.play(Create(m_d), run_time=0.7)
        rot.mostrar(cifra_pie(f"t_est {fmt(TS_D, 2)} s"), zona="abajo")
        self.wait(1.8)
        rot.mostrar(cifra_pie(f"{fmt(MEJORA_TS, 1)}x mas rapido"),
                    zona="abajo")
        self.wait(2.0)

        panel = panel_cifras((f"zeta {fmt(ZETA_P, 3)}", C_PELIGRO),
                             (f"t_est {fmt(TS_P, 1)} s", C_PELIGRO),
                             f"zeta {fmt(ZETA_D, 2)}",
                             f"t_est {fmt(TS_D, 2)} s")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.0)

        # --- Y lo que D no cambio: el arrastre --------------------------
        # Kv = kp/b. La derivada no aparece en la formula, asi que el
        # rezago no se entera de que se ha amortiguado el lazo.
        b = barras_comparar([E_ARRASTRE_5, E_ARRASTRE_5],
                            ["kd 0", f"kd {fmt(KD_OBJ, 2)}"],
                            ancho=4.4, alto=1.2,
                            colores=[C_PELIGRO, C_CALCULO], unidad="deg")
        # El carril inferior sube hasta y = -2.9 con una formula alta: las
        # barras se quedan en 1.2 de alto para dejar aire por los dos
        # lados (la respuesta al escalon baja hasta y = 0).
        b.move_to(DOWN * 1.60)
        t_b = tag_junto(b, "error de arrastre", UP, buff=0.18)
        self.play(FadeIn(b), FadeIn(t_b), run_time=0.9)
        self.wait(1.8)

        rot.mostrar(formula_pie(r"e_{ss} = v\,b / k_p"), zona="abajo")
        self.wait(2.4)
        rot.mostrar(cifra_pie(f"arrastre {fmt(E_ARRASTRE_5, 2)} deg igual",
                              color=C_SAT), zona="abajo")
        self.wait(4.2)

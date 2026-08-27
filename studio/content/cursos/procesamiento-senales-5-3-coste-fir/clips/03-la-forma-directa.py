# El parche de namespace que hubo aqui (dsp.LEFT = LEFT) ya no hace
# falta: dsp.py importa LEFT desde manim desde que se cazo el bug.


class Clip3(Scene):
    """5.3.3 - La forma directa: la muestra cae por las cajas z^-1, cada
    toma se multiplica por su coeficiente y todo llega al sumador.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("La forma directa"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        lr = linea_retardos(H_CORTO, ancho=9.6, alto=2.6, color=C_MUESTRA)
        lr.move_to(DOWN * 0.25)
        et_ent = tag_hud("entrada", font_size=18, color=C_TENUE)
        et_ent.next_to(lr.linea.get_start(), UP, buff=0.16)
        et_suma = tag_hud("suma", font_size=18, color=C_TENUE)
        et_suma.next_to(lr.suma, DOWN, buff=0.18)
        self.play(Create(lr.linea), FadeIn(et_ent), run_time=1.2)
        self.wait(1.2)

        self.play(LaggedStart(*[Create(c) for c in lr.cajas],
                              lag_ratio=0.12), run_time=2.2)
        rot.mostrar(formula_pie(r"z^{-1}"), zona="abajo", run_time=0.5)
        self.wait(2.6)

        self.play(LaggedStart(*[Create(t) for t in lr.tomas],
                              lag_ratio=0.10), run_time=1.6)
        self.play(LaggedStart(*[FadeIn(c, scale=1.3) for c in lr.coefs],
                              lag_ratio=0.10), run_time=1.6)
        self.play(Create(lr.suma), FadeIn(et_suma), run_time=1.0)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"h[0] = {fmt(H_CORTO[0], 4)}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        # --- una muestra recorriendo la linea directa -----------------------
        muestra = Dot(lr.toma(0).get_start(), radius=0.09, color=C_SALIDA)
        resalte = lr.encender(0)
        self.play(FadeIn(muestra, scale=1.6), FadeIn(resalte), run_time=0.5)
        for i in range(1, len(H_CORTO)):
            nuevo_resalte = lr.encender(i)
            self.play(muestra.animate.move_to(lr.toma(i).get_start()),
                      Transform(resalte, nuevo_resalte), run_time=0.65)
        self.play(muestra.animate.move_to(lr.suma.get_center()),
                  FadeOut(resalte), run_time=0.6)
        self.wait(1.6)

        # --- la simetria tambien vive en la forma directa --------------------
        rot.limpiar(zona="abajo", run_time=0.4)
        y_base = lr.suma.get_center()[1] - 0.35
        arcos = VGroup()
        for i, j in PARES_SIMETRICOS:
            p1 = np.array([lr.coef(i).get_center()[0], y_base, 0.0])
            p2 = np.array([lr.coef(j).get_center()[0], y_base, 0.0])
            arco = ArcBetweenPoints(p1, p2, angle=-0.5, color=C_CALCULO,
                                    stroke_width=1.6)
            if arco.get_center()[1] > y_base + 1e-6:
                arco = ArcBetweenPoints(p1, p2, angle=0.5, color=C_CALCULO,
                                        stroke_width=1.6)
            arcos.add(arco)
        self.play(LaggedStart(*[Create(a) for a in arcos], lag_ratio=0.15),
                  run_time=1.6)
        rot.mostrar(cifra_pie(f"{len(PARES_SIMETRICOS)} parejas"),
                    zona="abajo", run_time=0.5)
        self.wait(4.5)

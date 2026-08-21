class Clip1(Scene):
    """3.3.1 - De A a B por tres caminos muy distintos: el contador de
    trabajo da 4.00 las tres veces. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Tres caminos, un número")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el campo estrella es un gradiente -------------------
        pl = plano_leccion(centro=UP * 0.1)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Este campo no es uno cualquiera: cada "
                              "flecha es la subida de un paisaje."),
                    zona="abajo", run_time=0.5)
        campo = campo_flechas(pl, CAMPO, paso=1.0, escala=0.7,
                              x0=-3.5, x1=3.5, y0=-2.5, y1=2.5,
                              magnitud_max=MAG_REF, opacidad=0.85)
        panel = panel_derecha(MathTex(r"\vec F = \nabla \varphi",
                                      font_size=38, color=C_TITULO))
        self.play(LaggedStart(*[FadeIn(f, scale=0.6) for f in campo.flechas],
                              lag_ratio=0.02), run_time=1.6)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.2)

        # --- momento: los dos extremos del viaje --------------------------
        rot.mostrar(pie_curso("Vamos de A a B. La pregunta: cuánto trabajo "
                              "cobra el campo por el viaje."),
                    zona="abajo", run_time=0.5)
        pa = Dot(pl.p(A_PT), radius=0.09, color=C_GRAD)
        pb = Dot(pl.p(B_PT), radius=0.09, color=C_GRAD)
        # Fondo bajo las etiquetas: a esta altura del plano pasan flechas
        # del campo y la letra se leia encima de una de ellas.
        la = _con_fondo(tag_junto(pa, "A", direccion=DL, buff=0.10,
                                  font_size=24, color=C_GRAD),
                        buff=0.07, opacidad=0.85)
        lb = _con_fondo(tag_junto(pb, "B", direccion=UR, buff=0.10,
                                  font_size=24, color=C_GRAD),
                        buff=0.07, opacidad=0.85)
        self.play(FadeIn(pa, scale=0.4), FadeIn(la), run_time=0.5)
        self.play(FadeIn(pb, scale=0.4), FadeIn(lb), run_time=0.5)
        self.wait(3.8)

        # --- momento: el contador de trabajo ------------------------------
        self.play(FadeOut(panel), run_time=0.4)
        marcador = tag_hud("trabajo W =", font_size=20)
        contador = DecimalNumber(0.0, num_decimal_places=2, color=C_CALCULO,
                                 font_size=34)
        medidor = VGroup(marcador, contador).arrange(RIGHT, buff=0.18)
        medidor.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        contador.add_updater(lambda d: d.next_to(marcador, RIGHT, buff=0.18))
        self.play(FadeIn(medidor), run_time=0.5)

        t = ValueTracker(0.0)
        viajero = Dot(pl.p(A_PT), radius=0.10, color=C_VEC)
        pies = ("Primero en línea recta. El contador suma el peaje tramo "
                "a tramo.",
                "Ahora por un arco que se desvía. Otro camino, otra "
                "longitud.",
                "Y a escalones, en zigzag: el camino más raro de los tres.")
        trazos = VGroup()
        resultados = VGroup()
        for i, (nombre, r) in enumerate(CAMINOS):
            rot.mostrar(pie_curso(pies[i]), zona="abajo", run_time=0.5)
            for viejo in trazos:
                viejo.set_stroke(opacity=0.30)
            ruta = camino(pl, r, color=C_VEC, grosor=3.4, n=260)
            trazos.add(ruta.trazo)
            self.play(Create(ruta.trazo), run_time=0.7)

            ts_i, s_i = SUMAS[i]
            t.set_value(0.0)
            contador.clear_updaters()
            viajero.clear_updaters()
            contador.add_updater(
                lambda d, ts=ts_i, s=s_i: d.set_value(
                    float(np.interp(t.get_value(), ts, s))))
            contador.add_updater(
                lambda d: d.next_to(marcador, RIGHT, buff=0.18))
            viajero.add_updater(
                lambda d, rr=r: d.move_to(pl.p(rr(t.get_value()))))
            if i == 0:
                self.play(FadeIn(viajero, scale=0.5), run_time=0.4)
            self.play(t.animate.set_value(1.0), run_time=3.0,
                      rate_func=linear)

            fila = tag_hud(f"{nombre}: W = {fmt(TRABAJOS[i], 2)}",
                           font_size=18, color=C_RES)
            fila.to_corner(UR, buff=0.6).shift(DOWN * (1.35 + 0.52 * i))
            fila = _con_fondo(fila, buff=0.10, opacidad=0.85)
            resultados.add(fila)
            self.play(FadeIn(fila, shift=0.12 * LEFT), run_time=0.5)
            self.wait(1.8 if i < 2 else 1.2)

        # --- momento: el mismo numero, tres veces -------------------------
        contador.clear_updaters()
        viajero.clear_updaters()
        rot.mostrar(pie_curso("Tres caminos distintos, el mismo número. "
                              "Aquí el camino no importa."),
                    zona="abajo", run_time=0.5)
        for trazo in trazos:
            trazo.set_stroke(opacity=0.85)
        self.play(FadeOut(viajero), run_time=0.4)
        self.play(Indicate(resultados, color=C_RES, scale_factor=1.05),
                  run_time=0.9)
        self.wait(4.0)

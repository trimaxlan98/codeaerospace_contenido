class Clip2(Scene):
    """3.3.2 - Ida por el arco y vuelta por la recta: el contador sube a
    4.00 y regresa a 0.00. En el rotor, la misma vuelta cobra 14.14.
    (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El circuito gratis")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mismo campo, ahora en circuito -------------------
        pl = plano_leccion(centro=UP * 0.1)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Si el camino no importa, ir y volver "
                              "debería salir gratis. Probémoslo."),
                    zona="abajo", run_time=0.5)
        campo = campo_flechas(pl, CAMPO, paso=1.0, escala=0.7,
                              x0=-3.5, x1=3.5, y0=-2.5, y1=2.5,
                              magnitud_max=MAG_REF, opacidad=0.6)
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
        self.play(FadeIn(campo), run_time=1.2)
        self.play(FadeIn(pa), FadeIn(la), FadeIn(pb), FadeIn(lb),
                  run_time=0.6)
        self.wait(3.0)

        # --- momento: la vuelta completa, con contador --------------------
        rot.mostrar(pie_curso("Ida de A a B por el arco, vuelta de B a A "
                              "por la recta: un circuito cerrado."),
                    zona="abajo", run_time=0.5)
        vuelta = camino(pl, CIRCUITO, color=C_VEC, grosor=3.4, n=400,
                        flechas=4)
        self.play(Create(vuelta.trazo), run_time=1.1)
        self.play(FadeIn(vuelta.marcas), run_time=0.3)

        marcador = tag_hud("circuito W =", font_size=20)
        contador = DecimalNumber(0.0, num_decimal_places=2, color=C_CALCULO,
                                 font_size=34)
        medidor = VGroup(marcador, contador).arrange(RIGHT, buff=0.18)
        medidor.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        contador.add_updater(lambda d: d.next_to(marcador, RIGHT, buff=0.18))
        t = ValueTracker(0.0)
        contador.add_updater(lambda d: d.set_value(
            float(np.interp(t.get_value(), TS_CIRC, S_CIRC))))
        viajero = Dot(pl.p(A_PT), radius=0.10, color=C_VEC)
        viajero.add_updater(lambda d: d.move_to(pl.p(CIRCUITO(
            t.get_value()))))
        self.play(FadeIn(medidor), FadeIn(viajero, scale=0.5), run_time=0.5)
        self.play(t.animate.set_value(1.0), run_time=5.0, rate_func=linear)
        self.wait(0.8)

        # --- momento: la cuenta cierra en cero ----------------------------
        rot.mostrar(formula_pie(r"\oint \vec F \cdot d\vec r = 0"),
                    zona="abajo", run_time=0.5)
        fila_grad = tag_hud(f"{'gradiente':<10s}{fmt(W_CIRCUITO, 2):>6s}",
                            font_size=18, color=C_RES)
        fila_grad.to_corner(UR, buff=0.6).shift(DOWN * 1.35)
        fila_grad = _con_fondo(fila_grad, buff=0.10, opacidad=0.85)
        self.play(FadeIn(fila_grad, shift=0.12 * LEFT), run_time=0.5)
        self.wait(4.2)

        # --- momento: el rotor no perdona ---------------------------------
        rot.mostrar(pie_curso("Repitamos la vuelta en un campo que gira: "
                              "el rotor."), zona="abajo", run_time=0.5)
        contador.clear_updaters()
        viajero.clear_updaters()
        self.play(FadeOut(campo), FadeOut(vuelta), FadeOut(viajero),
                  FadeOut(pa), FadeOut(la), FadeOut(pb), FadeOut(lb),
                  run_time=0.8)
        giro = campo_flechas(pl, campo_rotor, paso=1.0, escala=0.7,
                             x0=-3.5, x1=3.5, y0=-2.5, y1=2.5,
                             magnitud_max=3.5, opacidad=0.85)
        aro = camino(pl, CIR_ROTOR, color=C_VEC, grosor=3.4, n=320,
                     flechas=4)
        self.play(FadeIn(giro), run_time=1.0)
        self.play(Create(aro.trazo), FadeIn(aro.marcas), run_time=0.8)
        self.wait(2.0)

        rot.mostrar(pie_curso("Aquí el contador no vuelve a cero: la "
                              "vuelta entera cobra peaje."),
                    zona="abajo", run_time=0.5)
        t.set_value(0.0)
        contador.set_value(0.0)
        contador.add_updater(lambda d: d.next_to(marcador, RIGHT, buff=0.18))
        contador.add_updater(lambda d: d.set_value(
            float(np.interp(t.get_value(), TS_ROT, S_ROT))))
        piloto = Dot(pl.p(CIR_ROTOR(0.0)), radius=0.10, color=C_VEC)
        piloto.add_updater(lambda d: d.move_to(pl.p(CIR_ROTOR(
            t.get_value()))))
        self.play(FadeIn(piloto, scale=0.5), run_time=0.4)
        self.play(t.animate.set_value(1.0), run_time=4.0, rate_func=linear)
        contador.clear_updaters()
        piloto.clear_updaters()
        fila_rotor = tag_hud(f"{'rotor':<10s}{fmt(W_ROTOR, 2):>6s}",
                             font_size=18, color=C_RES)
        fila_rotor.to_corner(UR, buff=0.6).shift(DOWN * 1.87)
        fila_rotor = _con_fondo(fila_rotor, buff=0.10, opacidad=0.85)
        self.play(FadeIn(fila_rotor, shift=0.12 * LEFT), run_time=0.5)
        self.wait(0.8)

        # --- momento: la definicion ---------------------------------------
        rot.mostrar(pie_curso("Un campo es conservativo cuando toda vuelta "
                              "cerrada sale gratis."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(piloto), run_time=0.4)
        self.play(Indicate(VGroup(fila_grad, fila_rotor), color=C_RES,
                           scale_factor=1.05), run_time=0.9)
        self.wait(4.0)

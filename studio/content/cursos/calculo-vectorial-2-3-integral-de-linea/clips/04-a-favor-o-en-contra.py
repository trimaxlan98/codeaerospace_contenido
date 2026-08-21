class Clip4(Scene):
    """2.3.4 - El mismo camino al reves cambia el signo del trabajo, y en un
    circuito CERRADO del rotor la cuenta no vuelve a cero: acumula 14.14.
    Cierre de la leccion. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("A favor o en contra")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mismo camino, andado al reves --------------------
        pl = plano_leccion()
        campo = campo_leccion(pl, ancho=4.05, opacidad=0.55)
        guia = camino(pl, R_INV, grosor=2.2, flechas=3, opacidad=0.4)
        self.play(FadeIn(pl), FadeIn(campo), run_time=0.9)
        rot.mostrar(pie_curso("Mismo viento, mismo camino. Pero ahora lo "
                              "andamos de B hacia A."), zona="abajo",
                    run_time=0.5)
        self.play(Create(guia.trazo), run_time=0.9)
        self.play(FadeIn(guia.marcas), run_time=0.4)
        self.wait(3.3)

        # --- momento: el contador al reves --------------------------------
        rot.mostrar(pie_curso("Cada paso dr apunta al otro lado, así que "
                              "cada peaje cambia de signo."), zona="abajo",
                    run_time=0.5)
        marcador, num, etiq = contador("trabajo acumulado", 0.0)
        tt = ValueTracker(0.0)
        num.add_updater(lambda m: m.set_value(
            trabajo_inv_hasta(tt.get_value())))
        num.add_updater(lambda m: m.next_to(etiq, DOWN, buff=0.16))
        movil = Dot(pl.p(R_INV(0.0)), radius=0.095, color=C_VEC)
        movil.add_updater(lambda d: d.move_to(pl.p(R_INV(tt.get_value()))))
        vivo = camino(pl, R_INV, grosor=3.8)
        self.play(FadeIn(marcador), FadeIn(movil, scale=0.5), run_time=0.6)
        self.play(Create(vivo.trazo), tt.animate.set_value(1.0),
                  run_time=3.8, rate_func=linear)
        num.clear_updaters()
        movil.clear_updaters()
        self.wait(0.5)

        # --- momento: mismo numero, signo cambiado ------------------------
        rot.mostrar(pie_curso("Mismo número, signo cambiado: ahora el "
                              "viento estorba en vez de ayudar."),
                    zona="abajo", run_time=0.5)
        balance = panel_derecha(
            tag_hud("trabajo", font_size=18),
            tag_hud(f"ida    {fmt(W_TOTAL, 2):>6}", font_size=20,
                    color=C_RES),
            tag_hud(f"vuelta {fmt(W_INV, 2):>6}", font_size=20,
                    color=C_RES),
            buff=0.20)
        # Relevo SECUENCIAL en la esquina: si el contador y el balance se
        # cruzan en la misma animacion, medio segundo se leen encimados.
        self.play(FadeOut(marcador), run_time=0.4)
        self.play(FadeIn(balance, shift=0.15 * LEFT), run_time=0.5)
        self.play(Indicate(balance, color=C_GRAD, scale_factor=1.05),
                  run_time=0.9)
        self.wait(2.9)

        # --- momento: y si el camino se cierra ----------------------------
        rot.mostrar(pie_curso("¿Y si el camino se cierra sobre sí mismo? "
                              "Vamos a un remolino."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(campo), FadeOut(guia), FadeOut(vivo),
                  FadeOut(movil), FadeOut(balance), run_time=0.8)
        remolino = campo_flechas(pl, campo_rotor, paso=0.9, escala=0.62,
                                 x0=-2.7, x1=2.7, y0=-2.25, y1=2.25,
                                 opacidad=0.85)
        circuito = camino(pl, C_CIRC, grosor=3.4, flechas=4)
        self.play(LaggedStart(*[GrowArrow(f) for f in remolino.flechas],
                              lag_ratio=0.02), run_time=1.4)
        self.play(Create(circuito.trazo), FadeIn(circuito.marcas),
                  run_time=0.9)
        self.wait(1.6)

        # --- momento: la vuelta entera no sale gratis ---------------------
        rot.mostrar(pie_curso("Damos la vuelta entera, siempre a favor de "
                              "la corriente. La cuenta no vuelve a cero."),
                    zona="abajo", run_time=0.5)
        marcador2, num2, etiq2 = contador("circulacion", 0.0)
        s = ValueTracker(0.0)
        num2.add_updater(lambda m: m.set_value(circulacion_hasta(
            s.get_value())))
        num2.add_updater(lambda m: m.next_to(etiq2, DOWN, buff=0.16))
        bola = Dot(pl.p(C_CIRC(0.0)), radius=0.095, color=C_VEC)
        bola.add_updater(lambda d: d.move_to(pl.p(C_CIRC(s.get_value()))))
        self.play(FadeIn(marcador2), FadeIn(bola, scale=0.5), run_time=0.6)
        self.play(s.animate.set_value(1.0), run_time=3.6, rate_func=linear)
        num2.clear_updaters()
        bola.clear_updaters()
        self.wait(0.6)

        # --- momento: la circulacion medida -------------------------------
        rot.mostrar(formula_pie(r"\oint_C \vec F \cdot d\vec r = "
                                + fmt(CIRC_ROTOR, 2)),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(num2, color=C_RES, scale_factor=1.15),
                  run_time=0.9)
        self.wait(3.6)

        # --- cierre -------------------------------------------------------
        cierre_leccion(self, rot,
                       "El trabajo se paga por tramos.",
                       "El camino y el sentido importan.",
                       "Siguiente lección: la divergencia, el balance de "
                       "una cajita.",
                       pl, remolino, circuito, bola, marcador2)

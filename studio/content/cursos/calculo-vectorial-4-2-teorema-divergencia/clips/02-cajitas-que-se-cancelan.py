class Clip2(Scene):
    """4.2.2 - Trocear la region en cajitas: cada pared interior se cuenta
    dos veces con signos opuestos y se cancela; solo sobrevive el borde,
    y el borde mide lo mismo que la divergencia de dentro. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Cajitas que se cancelan")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la region troceada ----------------------------------
        pl = plano_leccion(unidad=1.45)
        campo = campo_flechas(pl, campo_radial, paso=0.9, escala=0.32,
                              x0=-2.25, x1=2.25, y0=-1.6, y1=1.7,
                              magnitud_max=MAG_MAX_RADIAL, opacidad=0.45)
        # la region y las cajitas suman sus rellenos: el de abajo va flojo
        reg = region_rect(pl, *RECT_C2, flechas=0, opacidad=0.07)
        self.play(FadeIn(pl), FadeIn(campo), run_time=0.9)
        rot.mostrar(pie_curso("Tomemos una región del mismo campo y "
                              "troceémosla en cajitas."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(reg), run_time=0.8)
        cajas = VGroup(*[caja_conteo(pl, campo_radial, c, lado=LADO_CAJA,
                                     escala=0.3) for c in CENTROS_CAJAS])
        self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in cajas],
                              lag_ratio=0.16), run_time=2.0)
        self.wait(3.2)

        # --- momento: cada cajita tiene su balance ------------------------
        rot.mostrar(pie_curso("Cada cajita mide su propio balance: lo que "
                              "sale menos lo que entra."), zona="abajo",
                    run_time=0.5)
        balances = VGroup()
        for c, centro in zip(cajas, CENTROS_CAJAS):
            t = _con_fondo(tag_hud(fmt(c.flujo, 2), font_size=19,
                                   color=C_RES), buff=0.09, opacidad=0.88)
            t.move_to(pl.p(np.array(centro)))
            balances.add(t)
        self.play(LaggedStart(*[FadeIn(b, scale=0.6) for b in balances],
                              lag_ratio=0.14), run_time=1.6)
        suma_cajas = sum(c.flujo for c in cajas)
        marcador = _con_fondo(tag_hud(f"suma de las 6 = "
                                      f"{fmt(suma_cajas, 2)}",
                                      font_size=21, color=C_RES),
                              buff=0.10, opacidad=0.88)
        marcador.move_to(pl.p(np.array([0.0, RECT_C2[3] + 0.55])))
        self.play(FadeIn(marcador, shift=0.12 * DOWN), run_time=0.6)
        self.wait(3.4)

        # --- momento: la pared interior se cuenta dos veces ---------------
        rot.mostrar(pie_curso("Mira una pared interior: para la cajita de "
                              "la izquierda es salida; para la vecina, "
                              "entrada."), zona="abajo", run_time=0.5)
        otras = VGroup(*[c for i, c in enumerate(cajas)
                         if i not in (I_CAJA_IZQ, I_CAJA_DER)])
        self.play(otras.animate.set_stroke(opacity=0.20).set_fill(
                      opacity=0.03),
                  FadeOut(balances),
                  campo.animate.set_opacity(0.18), run_time=0.7)
        y_izq, y_der = -0.50, -0.80
        propias = VGroup(cajas[I_CAJA_IZQ].flechas[0],   # pared compartida
                         cajas[I_CAJA_DER].flechas[2])
        self.play(FadeOut(propias), run_time=0.3)
        n_izq = flecha_libre(pl, (PARED_X, y_izq), (PARED_X + 0.48, y_izq),
                             color=C_GRAD, grosor=4.0, punta_len=0.14)
        n_der = flecha_libre(pl, (PARED_X, y_der), (PARED_X - 0.48, y_der),
                             color=C_GRAD, grosor=4.0, punta_len=0.14)
        v_izq = cajas[I_CAJA_IZQ].flujos_lados[0]      # su lado derecho
        v_der = cajas[I_CAJA_DER].flujos_lados[2]      # su lado izquierdo
        et_izq = _con_fondo(tag_hud(f"+{fmt(v_izq, 2)}", font_size=18,
                                    color=C_RES), buff=0.08, opacidad=0.9)
        et_izq.move_to(pl.p(np.array([CENTROS_CAJAS[I_CAJA_IZQ][0], y_izq])))
        et_der = _con_fondo(tag_hud(fmt(v_der, 2), font_size=18,
                                    color=C_VEC), buff=0.08, opacidad=0.9)
        et_der.move_to(pl.p(np.array([CENTROS_CAJAS[I_CAJA_DER][0], y_der])))
        self.play(GrowArrow(n_izq), FadeIn(et_izq), run_time=0.7)
        self.play(GrowArrow(n_der), FadeIn(et_der), run_time=0.7)
        self.wait(2.8)

        rot.mostrar(pie_curso("Las dos normales son opuestas: la misma "
                              "cifra con signo cambiado. Se anulan."),
                    zona="abajo", run_time=0.5)
        anula = panel_derecha(
            tag_hud("pared interior", font_size=18, color=C_TENUE),
            tag_hud(f"{fmt(v_izq, 2)} + ({fmt(v_der, 2)})"
                    f" = {fmt(v_izq + v_der, 2)}", font_size=20,
                    color=C_RES), buff=0.22)
        self.play(FadeIn(anula, shift=0.15 * LEFT), run_time=0.6)
        self.wait(4.7)

        # --- momento: al fundir las cajas queda el borde ------------------
        rot.mostrar(pie_curso("Fundamos las cajitas: todas las paredes "
                              "interiores desaparecen y queda el borde."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cajas), FadeOut(n_izq),
                  FadeOut(n_der), FadeOut(et_izq), FadeOut(et_der),
                  FadeOut(marcador),
                  campo.animate.set_opacity(0.5), run_time=0.9)
        normales = normales_borde(pl, reg.curva, a=0.02, b=1.02, n=16,
                                  largo=0.42, color=C_GRAD)
        self.play(LaggedStart(*[GrowArrow(n) for n in normales],
                              lag_ratio=0.06), run_time=1.6)
        self.wait(3.0)

        # --- momento: los dos lados medidos -------------------------------
        rot.mostrar(pie_curso("Y el borde mide exactamente lo que suman "
                              "todas las divergencias de dentro."),
                    zona="abajo", run_time=0.5)
        flujo_borde = flujo_curva(campo_radial, reg.curva, n=8000)
        panel = panel_derecha(
            MathTex(r"\oint_{C} F\cdot \hat n\, ds", font_size=30,
                    color=C_CALCULO),
            MathTex(r"=\ \iint_{R} \nabla\cdot F\, dA", font_size=30,
                    color=C_CALCULO),
            tag_hud(f"borde    = {fmt(flujo_borde, 2)}", font_size=19,
                    color=C_RES),
            tag_hud(f"interior = {fmt(DIV_INTERIOR_C2, 2)}", font_size=19,
                    color=C_RES),
            buff=0.22)
        self.play(FadeOut(anula), run_time=0.3)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.3)

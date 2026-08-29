class Clip2(Scene):
    """3.1.2 - Q castiga el estado, R castiga el par: dos platillos de
    una balanza. Al inclinarla hacia Q el lazo se acelera, y la curva
    del compromiso lo dice con su cifra. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Q contra R"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- la balanza ----------------------------------------------------
        centro = np.array([-3.70, -0.55, 0.0])
        largo = 1.58
        incl = ValueTracker(0.0)

        def ext(s):
            a = np.radians(incl.get_value())
            return centro + s * largo * np.array([np.cos(a), np.sin(a), 0.0])

        suelo = Line(centro + LEFT * 1.05 + DOWN * 0.86,
                     centro + RIGHT * 1.05 + DOWN * 0.86,
                     stroke_width=3.0, color=C_EJE)
        soporte = Polygon(centro + LEFT * 0.40 + DOWN * 0.86,
                          centro + RIGHT * 0.40 + DOWN * 0.86, centro,
                          color=C_EJE, stroke_width=2.6)
        viga = Line(ext(-1), ext(1), stroke_width=5.5, color=C_EJE)
        eje = Dot(centro, radius=0.06, color=C_EJE)

        def cuerda_de(s):
            return Line(ext(s), ext(s) + DOWN * 0.46, stroke_width=2.0,
                        color=C_EJE)

        def bol_de(s, col):
            b = Arc(radius=0.40, start_angle=PI, angle=PI, color=col,
                    stroke_width=4.5)
            b.move_arc_center_to(ext(s) + DOWN * 0.46)
            return b

        cu_q, cu_r = cuerda_de(-1), cuerda_de(1)
        bo_q, bo_r = bol_de(-1, C_CALCULO), bol_de(1, C_PELIGRO)
        l_q = MathTex("Q", font_size=34, color=C_CALCULO)
        l_q.move_to(ext(-1) + DOWN * 0.60)
        l_r = MathTex("R", font_size=34, color=C_PELIGRO)
        l_r.move_to(ext(1) + DOWN * 0.60)

        self.play(Create(suelo), Create(soporte), run_time=0.7)
        self.play(Create(viga), FadeIn(eje), run_time=0.7)
        self.play(Create(cu_q), Create(cu_r), Create(bo_q), Create(bo_r),
                  FadeIn(l_q), FadeIn(l_r), run_time=0.9)
        self.wait(0.5)

        # los updaters se enganchan DESPUES del Create: una pieza que ya
        # esta en pantalla se mueve, no se vuelve a dibujar.
        viga.add_updater(lambda m: m.put_start_and_end_on(ext(-1), ext(1)))
        for s, cu, bo, la in ((-1, cu_q, bo_q, l_q), (1, cu_r, bo_r, l_r)):
            cu.add_updater(lambda m, s=s: m.put_start_and_end_on(
                ext(s), ext(s) + DOWN * 0.46))
            bo.add_updater(lambda m, s=s: m.move_arc_center_to(
                ext(s) + DOWN * 0.46))
            la.add_updater(lambda m, s=s: m.move_to(ext(s) + DOWN * 0.60))

        t_q = tag_junto(suelo, "Q castiga el estado", direccion=UP,
                        font_size=22, color=C_CALCULO)
        t_q.move_to(np.array([-5.28, 0.78, 0.0]))
        t_r = tag_junto(suelo, "R castiga el par", direccion=UP,
                        font_size=22, color=C_PELIGRO)
        t_r.move_to(np.array([-2.16, 0.78, 0.0]))
        self.play(FadeIn(t_q), FadeIn(t_r), run_time=0.8)
        self.wait(1.4)

        rot.mostrar(formula_pie(
            r"J = \int_0^{\infty}\left(q\,\theta^{2} + r\,u^{2}\right)dt"),
            zona="abajo")
        self.wait(2.6)

        # --- la curva del compromiso ---------------------------------------
        pq = plano_qr(qs=(1.0, 10.0, 100.0, 1000.0, 10000.0), r=R_BAJO,
                      ancho=4.4, alto=2.1, font_size=15)
        pq.shift(RIGHT * 2.55 + DOWN * 0.72)
        self.play(Create(pq.ejes), run_time=0.8)
        self.play(Create(pq.curva), run_time=1.4)
        self.play(LaggedStart(*[FadeIn(p, scale=1.5) for p in pq.puntos],
                              lag_ratio=0.18), run_time=1.0)
        self.wait(0.5)

        # --- se recorre el compromiso, punto a punto ------------------------
        angs = [0.0, 6.0, 12.0, 17.0, 21.0]
        q0, wn0 = pq.valores[0]
        aro = Circle(radius=0.17, color=C_OK, stroke_width=3.2)
        aro.move_to(pq.puntos[0].get_center())
        p_lect = np.array([2.62, 0.92, 0.0])
        lect = tag_hud(f"q/r {fmt(q0, 0)}: wn {fmt(wn0, 2)}", font_size=22)
        lect.move_to(p_lect)
        self.play(Create(aro), FadeIn(lect), run_time=0.7)
        rot.mostrar(cifra_pie(f"q/r {fmt(q0, 0)}: wn {fmt(wn0, 2)}"),
                    zona="abajo")
        self.wait(2.0)
        # El carril se apaga durante el barrido: mientras el rotulo
        # flotante corre, una cifra fija abajo diria otra cosa que la de
        # arriba y el frame se contradiria a si mismo.
        rot.limpiar("abajo", run_time=0.35)

        # OJO: en esta version de manim `play(run_time=...)` PISA el
        # run_time de cada animacion (Scene.compile_animations hace
        # setattr sobre todas), asi que el truco del "Transform corto
        # dentro de un play largo" NO funciona: deja los digitos a medio
        # morfar. El contador se releva con `become` DESPUES del
        # movimiento, que ademas evita que la cifra se adelante al aro.
        for i in range(1, len(angs)):
            q_i, wn_i = pq.valores[i]
            self.play(incl.animate.set_value(angs[i]),
                      aro.animate.move_to(pq.puntos[i].get_center()),
                      run_time=1.10)
            lect.become(tag_hud(f"q/r {fmt(q_i, 0)}: wn {fmt(wn_i, 2)}",
                                font_size=22).move_to(p_lect))
            self.wait(0.35)

        q4, wn4 = pq.valores[4]
        rot.mostrar(cifra_pie(f"q/r {fmt(q4, 0)}: wn {fmt(wn4, 2)}"),
                    zona="abajo")
        self.wait(2.4)
        rot.mostrar(formula_pie(r"\omega_n = \left(q/r\right)^{1/4}"),
                    zona="abajo")
        self.wait(2.6)

        # --- y se vuelve al ajuste del curso -------------------------------
        # El carril se apaga ANTES del morfeo: si no, el frame muestreado
        # enseña la cifra del extremo con la balanza ya en el ajuste base.
        rot.limpiar("abajo", run_time=0.35)
        q2, wn2 = pq.valores[2]
        self.play(incl.animate.set_value(angs[2]),
                  aro.animate.move_to(pq.puntos[2].get_center()),
                  run_time=1.40)
        lect.become(tag_hud(f"q/r {fmt(q2, 0)}: wn {fmt(wn2, 2)}",
                            font_size=22).move_to(p_lect))
        self.wait(0.6)
        rot.mostrar(cifra_pie(f"q/r {fmt(q2, 0)}: wn {fmt(wn2, 2)}"),
                    zona="abajo")
        self.wait(2.4)

        panel = panel_cifras(f"q = {fmt(Q_ALTO, 0)}",
                             f"r = {fmt(R_BAJO, 0)}",
                             f"wn {fmt(WN_R, 2)} rad/s")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.8)

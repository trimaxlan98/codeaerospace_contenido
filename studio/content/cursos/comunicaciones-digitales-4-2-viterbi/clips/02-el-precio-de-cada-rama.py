class Clip2(Scene):
    """4.2.2 - El precio de cada rama: la senal llega con dos bits
    volteados y cada rama cuesta su distancia Hamming. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El precio de cada rama")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        tr = trellis(pasos=PASOS, ancho=8.6, alto=2.4)
        tr.move_to(DOWN * 0.55)
        ramas = tr.todas_ramas(color=C_REJILLA, grosor=1.2, opacidad=0.55)

        def medio(t, s0, s1):
            return (tr.nodo(t, s0) + tr.nodo(t + 1, s1)) / 2.0

        def par(t):
            return f"{PARES_RX[t][0]}{PARES_RX[t][1]}"

        # --- momento: los 16 bits que salen de la sonda -------------------
        rot.mostrar(pie_curso("La sonda transmite dieciséis bits: dos por "
                              "cada bit del mensaje."),
                    zona="abajo", run_time=0.5)
        tren = tren_bits(CODIFICADO, lado=0.42)
        tren.move_to(UP * 2.15)
        et_tren = tag_junto(tren, "transmitido", direccion=LEFT, buff=0.26)
        self.play(FadeIn(tr), FadeIn(ramas), FadeIn(tren), FadeIn(et_tren),
                  run_time=1.0)
        camino = tr.camino(ESTADOS, color=C_BIT, grosor=3.2)
        self.play(Create(camino), run_time=1.8)
        self.wait(2.8)

        # --- momento: el canal voltea dos bits ----------------------------
        rot.mostrar(pie_curso("El canal voltea dos. Esto es lo que llega."),
                    zona="abajo", run_time=0.5)
        tren_rx = tren.con_bits(RECIBIDO)
        for _i in IDX_ERROR:
            tren_rx.marcar(_i)
        et_rx = tag_junto(tren, "recibido", direccion=LEFT, buff=0.26)
        panel = panel_derecha(
            tag_hud(f"bits volteados = {N_ERR_CANAL}", color=C_RUIDO))
        self.play(Transform(tren, tren_rx), Transform(et_tren, et_rx),
                  run_time=1.3)
        self.play(FadeIn(panel), run_time=0.5)
        self.wait(3.7)

        # --- momento: el receptor no ve el camino -------------------------
        rot.mostrar(pie_curso("El decodificador no conoce el camino: solo "
                              "tiene esos bits y la rejilla."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(camino), run_time=0.9)
        self.wait(4.6)

        # --- momento: el precio de las dos primeras ramas -----------------
        rot.mostrar(pie_curso("Cada rama predice dos bits; su precio es en "
                              "cuántos difiere de lo recibido."),
                    zona="abajo", run_time=0.5)
        caja = SurroundingRectangle(VGroup(tren.celda(0), tren.celda(1)),
                                    color=C_CIFRA, buff=0.06)
        et_par = tag_hud(f"recibido {par(0)}", font_size=18)
        et_par.next_to(caja, DOWN, buff=0.18)
        self.play(Create(caja), FadeIn(et_par), run_time=0.8)
        s2_0, s2_1 = destino_rama(0, 0), destino_rama(0, 1)
        rb_0 = tr.rama(0, 0, s2_0, color=C_SENAL, grosor=2.6)
        rb_1 = tr.rama(0, 0, s2_1, color=C_SENAL, grosor=2.6)
        self.play(Create(rb_0), Create(rb_1), run_time=1.0)
        o1, o2 = salida_rama(0, 0)
        sal_0 = tag_hud(f"{o1}{o2}", font_size=18, color=C_COD)
        # los dos bits que predice cada rama, pegados a su ARRANQUE: uno
        # sobre la rama horizontal, el otro en la cuña entre las dos.
        sal_0.move_to(tr.nodo(0, 0) + RIGHT * 0.34 + UP * 0.24)
        p1, p2 = salida_rama(0, 1)
        sal_1 = tag_hud(f"{p1}{p2}", font_size=18, color=C_COD)
        sal_1.move_to(tr.nodo(0, 0) + RIGHT * 0.60 + DOWN * 0.36)
        self.play(FadeIn(sal_0), FadeIn(sal_1), run_time=0.5)
        m_0 = _con_fondo(tr.metrica(1, s2_0, costo_rama(0, 0, 0)), buff=0.10)
        m_1 = _con_fondo(tr.metrica(1, s2_1, costo_rama(0, 0, 1)), buff=0.10)
        self.play(FadeIn(m_0), FadeIn(m_1), run_time=0.6)
        self.wait(2.7)

        # --- momento: el bit volteado hace pagar a la rama verdadera ------
        rot.mostrar(pie_curso("Donde cayó un bit volteado, hasta la rama "
                              "verdadera paga uno."),
                    zona="abajo", run_time=0.5)
        caja2 = SurroundingRectangle(VGroup(tren.celda(2), tren.celda(3)),
                                     color=C_RUIDO, buff=0.06)
        self.play(FadeOut(caja), FadeOut(et_par), FadeOut(sal_0),
                  FadeOut(sal_1), FadeOut(m_0), FadeOut(m_1),
                  FadeOut(rb_0), FadeOut(rb_1), Create(caja2), run_time=0.8)
        s_v, b_v = ESTADOS[1], MENSAJE[1]          # la rama verdadera en t=1
        q1, q2 = salida_rama(s_v, b_v)
        comp = VGroup(tag_hud(f"recibido {par(1)}", font_size=18,
                              color=C_RUIDO),
                      tag_hud(f"la rama predice {q1}{q2}", font_size=18,
                              color=C_COD)).arrange(DOWN, buff=0.12)
        comp.next_to(caja2, DOWN, buff=0.18)
        self.play(FadeIn(comp), run_time=0.6)
        rv = tr.rama(1, s_v, destino_rama(s_v, b_v), color=C_BIT,
                     grosor=3.0)
        self.play(Create(rv), run_time=0.8)
        precio = tr.metrica(1, s_v, costo_rama(1, s_v, b_v))
        precio.move_to(medio(1, s_v, destino_rama(s_v, b_v)) + UP * 0.34)
        precio = _con_fondo(precio, buff=0.10)
        self.play(FadeIn(precio), run_time=0.5)
        self.wait(2.9)

        # --- momento: el coste de un camino entero ------------------------
        rot.mostrar(formula_pie(r"m(\text{camino}) = \sum_{t}"
                                r" d_H(y_t,\, r_t)"),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

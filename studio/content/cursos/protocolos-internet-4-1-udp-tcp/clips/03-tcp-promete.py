class Clip3(Scene):
    """4.1.3 - TCP: veinte bytes y una promesa. La MISMA perdida del clip
    anterior, pero aqui el hueco se nota y se rellena (el como, ventana y
    ACK duplicados, es de la proxima leccion). (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("TCP promete")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: veinte bytes, una promesa -----------------------------
        rot.mostrar(pie_curso("TCP tambien manda datos, pero antes de "
                              "eso construye una promesa: entrega "
                              "completa, en orden, sin duplicados."),
                    zona="abajo", run_time=0.5)
        cab = cabecera(CAMPOS_TCP, CAB_TCP_VAL, ancho=10.4, alto_fila=0.52,
                      fs=14, color=C_CAPA)
        cab.move_to(UP * 1.55)
        self.play(FadeIn(cab), run_time=0.9)
        et_cab = tag_hud("20 bytes de cabecera: dos veces y media UDP",
                         font_size=18, color=C_CAPA)
        et_cab.next_to(cab, DOWN, buff=0.28)
        self.play(FadeIn(et_cab), run_time=0.5)
        self.wait(3.8)

        # --- momento: los mismos tres segmentos, la misma perdida ------------
        rot.mostrar(pie_curso("Los mismos tres envios. La misma perdida "
                              "de antes: el segundo no llega."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cab), FadeOut(et_cab), run_time=0.5)
        emisor = nodo("host", "emisor", 0.55)
        emisor.move_to(LEFT * 4.6)
        receptor = nodo("host", "receptor", 0.55)
        receptor.move_to(RIGHT * 4.6)
        enl = enlace(emisor.centro(), receptor.centro(), color=C_OK)
        self.play(FadeIn(emisor), FadeIn(receptor), Create(enl.linea),
                  run_time=0.8)

        ranuras = VGroup()
        cajas_ranura = {}
        for n in NUMEROS_ENVIADOS:
            r = Square(0.46, stroke_color=C_EJE, stroke_width=1.8)
            cajas_ranura[n] = r
            ranuras.add(r)
        ranuras.arrange(RIGHT, buff=0.16)
        ranuras.next_to(receptor, DOWN, buff=0.55)

        for n in NUMEROS_ENVIADOS:
            tk = ficha(str(n), lado=0.44, color=C_PAQUETE)
            tk.move_to(emisor.centro())
            self.play(FadeIn(tk, scale=1.2), run_time=0.22)
            if n == PERDIDO:
                self.play(tk.animate.move_to(enl.punto_en(0.5)),
                          run_time=0.6)
                self.play(tk.animate.set_color(C_PERDIDA), run_time=0.3)
                self.play(tk.animate.shift(DOWN * 1.0).set_opacity(0.0),
                          run_time=0.6)
            else:
                self.play(MoveAlongPath(tk, enl.linea), run_time=0.8)
                self.play(FadeOut(tk), FadeIn(cajas_ranura[n]),
                          run_time=0.25)
                num = tag_hud(str(n), font_size=16, color=C_PAQUETE)
                num.move_to(cajas_ranura[n].get_center())
                cajas_ranura[n].add(num)
                self.play(FadeIn(num), run_time=0.15)
        self.wait(1.6)

        # --- momento: el hueco se nota ---------------------------------------
        rot.mostrar(pie_curso("Pero aqui el hueco se nota: al receptor le "
                              "falta un numero, y lo sabe."),
                    zona="abajo", run_time=0.5)
        hueco = cajas_ranura[PERDIDO]
        self.play(hueco.animate.set_stroke(C_PERDIDA, width=2.6),
                  run_time=0.4)
        interr = tag_hud("?", font_size=20, color=C_PERDIDA)
        interr.move_to(hueco.get_center())
        self.play(FadeIn(interr, scale=1.3), run_time=0.4)
        et_falta = tag_hud("falta el numero %d" % PERDIDO, font_size=18,
                           color=C_PERDIDA)
        et_falta.next_to(ranuras, DOWN, buff=0.24)
        self.play(FadeIn(et_falta), run_time=0.4)
        self.wait(3.4)

        # --- momento: se rellena ------------------------------------------
        rot.mostrar(pie_curso("Y se rellena: el emisor lo manda otra vez, "
                              "y el hueco se cierra en su lugar."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(interr), FadeOut(et_falta), run_time=0.35)
        reenvio = ficha(str(PERDIDO), lado=0.44, color=C_OK)
        reenvio.move_to(emisor.centro())
        self.play(FadeIn(reenvio, scale=1.2), run_time=0.3)
        self.play(MoveAlongPath(reenvio, enl.linea), run_time=0.9)
        self.play(FadeOut(reenvio),
                  hueco.animate.set_stroke(C_OK, width=2.6), run_time=0.4)
        num2 = tag_hud(str(PERDIDO), font_size=16, color=C_OK)
        num2.move_to(hueco.get_center())
        self.play(FadeIn(num2), run_time=0.3)
        et_ok = tag_hud("entregado: 3 de 3, en orden, sin duplicados",
                        font_size=21, color=C_OK)
        et_ok.move_to(DOWN * 2.55)
        self.play(FadeIn(et_ok, shift=0.1 * UP), run_time=0.5)
        self.wait(4.8)

class Clip1(Scene):
    """4.1.1 - La IP entrega al host; el puerto entrega al programa: la
    4-tupla que decide, con `demux`, incluido el paquete que no encuentra
    a nadie escuchando. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Puertos: la extension telefonica")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: un host, varios programas ---------------------------
        rot.mostrar(pie_curso("La IP dice a que maquina. El puerto dice a "
                              "que programa de esa maquina."),
                    zona="abajo", run_time=0.5)
        host = nodo("servidor", None, 0.62)
        host.move_to(LEFT * 3.0)
        et_host = tag_hud(IP_HOST, font_size=17, color=C_EJE)
        et_host.next_to(host, DOWN, buff=0.22)
        self.play(FadeIn(host), FadeIn(et_host), run_time=0.7)

        sockets = VGroup()
        cajas_s = {}
        for puerto, nombre in SOCKET_DE.items():
            caja = Rectangle(width=3.1, height=0.62, stroke_color=C_RED,
                             stroke_width=2.2, fill_color=C_RED,
                             fill_opacity=0.08)
            caja.move_to(RIGHT * 2.4 + UP * SOCKET_Y[puerto])
            et = tag_hud(":%d  %s" % (puerto, nombre), font_size=17,
                        color=C_RED)
            et.move_to(caja.get_center())
            cajas_s[puerto] = VGroup(caja, et)
            sockets.add(cajas_s[puerto])
        self.play(LaggedStart(*[FadeIn(s, shift=0.12 * RIGHT)
                               for s in sockets], lag_ratio=0.3),
                  run_time=1.0)
        self.wait(3.2)

        # --- momento: la 4-tupla llega y el puerto decide ------------------
        rot.mostrar(pie_curso("Cada paquete trae su 4-tupla: IP y puerto "
                              "de origen, IP y puerto de destino."),
                    zona="abajo", run_time=0.5)
        pk = paquete([("IP origen", 1.35, PAQUETES_DEMUX[0]["ip_o"]),
                     ("Puerto origen", 0.85,
                      str(PAQUETES_DEMUX[0]["pto_o"])),
                     ("IP destino", 1.35, PAQUETES_DEMUX[0]["ip_d"]),
                     ("Puerto destino", 0.85,
                      str(PAQUETES_DEMUX[0]["pto_d"]))],
                    ancho=7.6, alto=0.66, fs=14)
        pk.move_to(UP * 2.15)
        self.play(FadeIn(pk), run_time=0.6)
        self.wait(2.6)

        # --- momento: el puerto destino se ilumina y decide ----------------
        rot.mostrar(pie_curso("El puerto destino se ilumina: el mismo "
                              "campo, paquete a paquete, decide el socket."),
                    zona="abajo", run_time=0.5)
        campo_pd = pk.campo("Puerto destino")
        valor_pd = pk.valor("Puerto destino")
        rotulo_pd = pk.rotulo("Puerto destino")
        self.play(campo_pd.animate.set_stroke(C_CIFRA, width=3.4),
                  valor_pd.animate.set_color(C_CIFRA),
                  rotulo_pd.animate.set_color(C_CIFRA), run_time=0.5)
        # `Transform` no actualiza los atributos de python del original: si
        # no se anota aqui, `con_valores` (que SI conserva lo iluminado)
        # parte de un diccionario vacio y el campo se apaga al pasar al
        # siguiente paquete.
        pk._iluminados["Puerto destino"] = C_CIFRA
        entregados = 0
        for i, p in enumerate(PAQUETES_DEMUX):
            if i > 0:
                nueva = pk.con_valores({"IP origen": p["ip_o"],
                                        "Puerto origen": str(p["pto_o"]),
                                        "IP destino": p["ip_d"],
                                        "Puerto destino": str(p["pto_d"])})
                self.play(Transform(pk, nueva), run_time=0.55)
            paso = DEMUX["pasos"][i]
            tk = ficha(str(p["pto_d"]), lado=0.46, fs=14, color=C_CIFRA)
            tk.move_to(pk.campo("Puerto destino").get_center() +
                      DOWN * 1.1)
            self.play(FadeIn(tk, shift=0.1 * DOWN), run_time=0.35)
            if paso["entregado"]:
                destino = cajas_s[p["pto_d"]]
                punto_llegada = destino[0].get_left() + LEFT * 0.34
                self.play(tk.animate.move_to(punto_llegada), run_time=0.75)
                self.play(destino[0].animate.set_stroke(C_OK, width=3.4)
                          .set_fill(C_OK, opacity=0.22),
                          tk.animate.set_color(C_OK),
                          run_time=0.3)
                self.play(FadeOut(tk), run_time=0.3)
                entregados += 1
            else:
                self.play(tk.animate.set_color(C_PERDIDA).shift(
                    DOWN * 0.3), run_time=0.4)
                equis = tag_hud("X", font_size=24, color=C_PERDIDA)
                equis.next_to(tk, RIGHT, buff=0.18)
                self.play(FadeIn(equis, scale=1.4), run_time=0.3)
                self.wait(0.4)
                self.play(FadeOut(tk), FadeOut(equis), run_time=0.4)
            self.wait(0.4)
        self.wait(1.0)

        # --- momento: un puerto sin nadie escuchando -----------------------
        rot.mostrar(pie_curso("Un puerto sin socket no es un fallo de la "
                              "red: ahi no hay nadie. Por eso existe "
                              "'puerto cerrado'."),
                    zona="abajo", run_time=0.5)
        resumen = tag_hud("%d de %d paquetes entregados"
                          % (DEMUX["entregados"], DEMUX["total"]),
                          font_size=22, color=C_CIFRA)
        resumen.move_to(DOWN * 2.35)
        self.play(FadeIn(resumen, shift=0.12 * UP), run_time=0.5)
        self.wait(4.6)

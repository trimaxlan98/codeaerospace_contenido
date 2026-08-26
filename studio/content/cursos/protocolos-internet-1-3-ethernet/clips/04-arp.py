class Clip4(Scene):
    """1.3.4 - ARP: en el cable no hay IPs, hay MACs. Se pregunta a todos,
    contesta uno, y la cache evita la segunda pregunta. Pasos REALES de
    `arp_resolver`. Cierre de la leccion. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("ARP: quien tiene esta IP")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: tengo la IP, me falta la MAC -------------------------
        rot.mostrar(pie_curso("Tu paquete lleva una IP. Pero en el cable "
                              "solo se entrega a una MAC."),
                    zona="abajo", run_time=0.5)
        cable = Line(np.array([ARP_CABLE_X[0], ARP_CABLE_Y, 0.0]),
                     np.array([ARP_CABLE_X[1], ARP_CABLE_Y, 0.0]),
                     color=C_RED, stroke_width=3.4)
        casas, stubs, ips = VGroup(), VGroup(), VGroup()
        for i, x in enumerate(ARP_X):
            n = nodo("host", None, 0.55)
            n.move_to(np.array([x, ARP_HOST_Y, 0.0]))
            casas.add(n)
            stubs.add(DashedLine(np.array([x, ARP_HOST_Y - 0.36, 0.0]),
                                 np.array([x, ARP_CABLE_Y, 0.0]),
                                 color=C_RED, stroke_width=2.0))
            t = tag_hud(ARP_IPS[i], font_size=16, color=C_CAPA)
            t.move_to(np.array([x, ARP_IP_Y, 0.0]))
            ips.add(t)
        yo = tag_hud("tu", font_size=17, color=C_EJE)
        yo.move_to(np.array([ARP_X[0], ARP_IP_Y + 0.44, 0.0]))
        self.play(Create(cable), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(c) for c in casas], lag_ratio=0.18),
                  FadeIn(stubs), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(t) for t in ips], lag_ratio=0.18),
                  FadeIn(yo), run_time=0.8)
        falta = tag_hud("destino %s   ->   MAC ?" % IP_DEST, font_size=21,
                        color=C_PERDIDA)
        falta.move_to(np.array([0.0, ARP_TAG_Y, 0.0]))
        self.play(FadeIn(falta), run_time=0.4)
        self.wait(3.4)

        # --- momento: preguntar a todos -----------------------------------
        rot.mostrar(pie_curso("Asi que preguntas a todo el cable a la vez, "
                              "a la MAC que escuchan todos."),
                    zona="abajo", run_time=0.5)
        pregunta = tag_hud("a %s:  quien tiene %s ?"
                           % (ARP_BROADCAST, IP_DEST), font_size=21,
                           color=C_PAQUETE)
        pregunta.move_to(np.array([0.0, ARP_TAG_Y, 0.0]))
        self.play(FadeOut(falta), run_time=0.25)
        self.play(FadeIn(pregunta), run_time=0.35)
        peticion = Square(0.34, stroke_color=C_PAQUETE, stroke_width=2.4,
                          fill_color=C_PAQUETE, fill_opacity=0.24)
        peticion.move_to(casas[0].get_center())
        self.play(FadeIn(peticion, scale=1.3), run_time=0.25)
        self.play(peticion.animate.move_to(
            np.array([ARP_X[0], ARP_CABLE_Y, 0.0])), run_time=0.35)
        copias = VGroup(*[peticion.copy() for _ in range(3)])
        self.add(copias)
        self.play(*[c.animate.move_to(casas[i + 1].get_center())
                    for i, c in enumerate(copias)], run_time=0.65)
        self.play(FadeOut(copias), FadeOut(peticion), run_time=0.3)
        self.wait(3.4)

        # --- momento: contesta uno ----------------------------------------
        rot.mostrar(pie_curso("De los tres, solo contesta el que se "
                              "reconoce. Y al contestar, dice su MAC."),
                    zona="abajo", run_time=0.5)
        respuesta = Square(0.34, stroke_color=C_OK, stroke_width=2.4,
                           fill_color=C_OK, fill_opacity=0.26)
        respuesta.move_to(casas[1].get_center())
        self.play(FadeIn(respuesta, scale=1.3),
                  casas[1].forma.animate.set_stroke(C_OK, width=3.4),
                  run_time=0.35)
        self.play(respuesta.animate.move_to(casas[0].get_center()),
                  run_time=0.60)
        self.play(FadeOut(respuesta), run_time=0.22)
        soy_yo = tag_hud("soy yo:  %s" % ARP_MAC, font_size=21, color=C_OK)
        soy_yo.move_to(np.array([0.0, ARP_TAG_Y, 0.0]))
        self.play(FadeOut(pregunta), run_time=0.25)
        self.play(FadeIn(soy_yo), run_time=0.35)
        cache = tabla(["IP", "MAC"], [[IP_DEST, ARP_MAC]],
                      anchos=[2.35, 3.25], alto=0.42, fs=17)
        cache.move_to(np.array([0.0, ARP_TABLA_Y, 0.0]))
        et_cache = tag_hud("cache ARP", font_size=17, color=C_EJE)
        et_cache.next_to(cache, LEFT, buff=0.42)
        self.play(FadeIn(cache), FadeIn(et_cache), run_time=0.6)
        self.wait(3.2)

        # --- momento: la cache evita la segunda pregunta -------------------
        rot.mostrar(pie_curso("El siguiente paquete al mismo vecino ya no "
                              "pregunta nada: lo tienes apuntado."),
                    zona="abajo", run_time=0.5)
        directo = Square(0.34, stroke_color=C_PAQUETE, stroke_width=2.4,
                         fill_color=C_PAQUETE, fill_opacity=0.24)
        directo.move_to(casas[0].get_center())
        self.play(FadeOut(soy_yo), run_time=0.25)
        self.play(FadeIn(directo, scale=1.3), run_time=0.25)
        self.play(directo.animate.move_to(
            np.array([ARP_X[0], ARP_CABLE_Y, 0.0])), run_time=0.30)
        self.play(directo.animate.move_to(casas[1].get_center()),
                  run_time=0.55)
        self.play(directo.animate.set_color(C_OK), run_time=0.25)
        cuenta = tag_hud("2 envios al mismo vecino  ->  %d sola pregunta"
                         % ARP_PREGUNTAS, font_size=21, color=C_CIFRA)
        cuenta.move_to(np.array([0.0, ARP_CUENTA_Y, 0.0]))
        self.play(FadeIn(cuenta), run_time=0.5)
        self.wait(3.0)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "En tu cable no hay direcciones de Internet.",
            "Hay vecinos que responden.",
            "Siguiente: IP, la direccion y el datagrama.",
            cable, casas, stubs, ips, yo, cache, et_cache, cuenta, directo,
            espera=4.6)

class Clip3(Scene):
    """1.3.3 - El switch empieza sin saber nada: inunda la primera trama
    por todos los puertos, anota de donde venia y la respuesta ya sale por
    uno solo. Tabla y conteos REALES de `switch_aprende`. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El switch aprende")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la caja que no sabe nada ----------------------------
        rot.mostrar(pie_curso("Un switch nace sin saber nada: solo tiene "
                              "puertos y una tabla vacia."),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_SW, ARISTAS_SW, TIPOS_SW, costos=True, tam=0.50)
        tab = tabla(["MAC", "puerto"], filas_mac({}), anchos=[1.55, 1.30],
                    alto=0.42, fs=17)
        tab.move_to(np.array([TABLA_SW_POS[0], TABLA_SW_POS[1], 0.0]))
        et_tab = tag_hud("tabla MAC del switch", font_size=17, color=C_EJE)
        et_tab.next_to(tab, UP, buff=0.44)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.0)
        self.play(FadeIn(tab), FadeIn(et_tab), run_time=0.7)
        self.wait(4.0)

        # --- utiles --------------------------------------------------------
        accion = [None]

        def puerto_de(h):
            return "p%d" % (HOSTS_SW.index(h) + 1)

        def rotular(texto, color):
            t = tag_hud(texto, font_size=19, color=color)
            t.move_to(np.array([0.0, ACCION_Y, 0.0]))
            if accion[0] is None:
                self.play(FadeIn(t), run_time=0.35)
            else:
                self.play(FadeOut(accion[0]), run_time=0.2)
                self.play(FadeIn(t), run_time=0.3)
            accion[0] = t

        def trama_en(h):
            m = Square(0.36, stroke_color=C_PAQUETE, stroke_width=2.4,
                       fill_color=C_PAQUETE, fill_opacity=0.24)
            m.move_to(topo.punto(h))
            self.play(FadeIn(m, scale=1.3), run_time=0.25)
            self.play(m.animate.move_to(topo.punto("SW")), run_time=0.50)
            return m

        def aprender(k):
            nueva = tab.con_filas(filas_mac(SW_PASOS[k]["tabla"]))
            self.play(Succession(Transform(tab, nueva, run_time=0.40),
                                 Wait(0.10)))
            i = len(SW_PASOS[k]["tabla"]) - 1
            self.play(Indicate(tab.fila(i), color=C_CIFRA,
                               scale_factor=1.14), run_time=0.55)

        # --- momento: no conozco el destino -> inundo ----------------------
        rot.mostrar(pie_curso("La primera trama va a una MAC que no "
                              "conoce. Sin saber por donde, la manda por "
                              "todos."),
                    zona="abajo", run_time=0.5)
        org, dst = EV_SWITCH[0]
        otros = [h for h in HOSTS_SW if h != org]
        rotular("%s -> %s   destino desconocido: INUNDA (%s)"
                % (org, dst, " ".join(puerto_de(h) for h in otros)), C_COLA)
        m = trama_en(org)
        copias = VGroup(*[m.copy() for _ in otros])
        self.add(copias)
        self.play(*[c.animate.move_to(topo.punto(h))
                    for c, h in zip(copias, otros)], run_time=0.70)
        self.play(FadeOut(copias), FadeOut(m), run_time=0.30)
        aprender(0)
        self.wait(3.4)

        # --- momento: pero aprendio de donde venia -------------------------
        rot.mostrar(pie_curso("Al verla pasar anoto de que puerto venia. "
                              "La respuesta ya sale por uno solo."),
                    zona="abajo", run_time=0.5)
        org, dst = EV_SWITCH[1]
        rotular("%s -> %s   destino en la tabla: unicast por %s"
                % (org, dst, puerto_de(dst)), C_OK)
        m = trama_en(org)
        self.play(m.animate.set_color(C_OK), run_time=0.20)
        self.play(m.animate.move_to(topo.punto(dst)), run_time=0.55)
        self.play(FadeOut(m), run_time=0.25)
        aprender(1)
        self.wait(3.4)

        # --- momento: cuanto ahorra la tabla -------------------------------
        rot.mostrar(pie_curso("Cada trama nueva le ensena un vecino mas, y "
                              "el cable deja de llenarse de copias."),
                    zona="abajo", run_time=0.5)
        for k in (2, 3):
            org, dst = EV_SWITCH[k]
            rotular("%s -> %s   destino en la tabla: unicast por %s"
                    % (org, dst, puerto_de(dst)), C_OK)
            m = trama_en(org)
            self.play(m.animate.set_color(C_OK), run_time=0.20)
            self.play(m.animate.move_to(topo.punto(dst)), run_time=0.50)
            self.play(FadeOut(m), run_time=0.22)
        aprender(3)
        cuentas = VGroup(
            tag_hud("inundadas   %d de %d" % (SW_INUNDADAS, SW_TOTAL),
                    font_size=20, color=C_COLA),
            tag_hud("unicast     %d de %d" % (SW_UNICAST, SW_TOTAL),
                    font_size=20, color=C_OK),
        ).arrange(DOWN, buff=0.20, aligned_edge=LEFT)
        cuentas.next_to(tab, DOWN, buff=0.62)
        self.play(FadeIn(cuentas, shift=0.12 * UP), run_time=0.6)
        self.wait(4.2)

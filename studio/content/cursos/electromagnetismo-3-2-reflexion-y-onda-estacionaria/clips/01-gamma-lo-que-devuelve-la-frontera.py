class Clip1(Scene):
    """3.2.1 - Gamma: lo que devuelve la frontera. Una carga que no vale
    lo mismo que la linea rebota parte de la onda; el grosor de cada
    flecha ES la potencia que lleva. Adaptado, el salto real 50 -> 75 y
    los dos extremos (corto y abierto). (~38 s)"""

    POS = LEFT * 3.0 + UP * 0.25

    def _frontera(self, z_carga):
        """La pieza de la libreria, siempre en el mismo sitio del cuadro."""
        f = frontera_z(Z_LINEA, z_carga)
        f.move_to(self.POS)
        return f

    def _fila(self, nombre, cifra, y):
        """Una linea de la tabla de casos: nombre tenue, cifra en cian."""
        n = Text(nombre, font_size=19, color=C_TENUE)
        n.move_to(np.array([1.9, y, 0.0]), aligned_edge=LEFT)
        v = MathTex(rf"\Gamma = {cifra}", font_size=27, color=C_CALCULO)
        v.move_to(np.array([4.5, y, 0.0]), aligned_edge=LEFT)
        return VGroup(n, v)

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Lo que devuelve la frontera")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la frontera adaptada --------------------------------
        fro = self._frontera(Z_LINEA)
        fro.flechas[1].set_opacity(0.0)      # con gamma = 0 no hay reflejada
        z_izq = tag_hud("linea  Z0 = 50 ohm", font_size=17, color=C_TENUE)
        z_izq.next_to(fro.medios[0], DOWN, buff=0.20)
        z_der = tag_hud("carga  ZL = 50 ohm", font_size=17, color=C_TENUE)
        z_der.next_to(fro.medios[1], DOWN, buff=0.20)
        t_inc = tag_junto(fro.flechas[0], "incidente", UP, buff=0.12,
                          font_size=17, color=C_ONDA)
        t_ref = tag_junto(fro.flechas[1], "reflejada", DOWN, buff=0.12,
                          font_size=17, color=C_CARGA)
        t_tra = tag_junto(fro.flechas[2], "transmitida", UP, buff=0.12,
                          font_size=17, color=C_ONDA)

        rot.mostrar(pie_curso("Al final de la línea hay una carga. Lo que "
                              "no encaja con ella, se devuelve."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(fro), FadeIn(z_izq), FadeIn(z_der), run_time=0.8)
        self.play(FadeIn(t_inc), FadeIn(t_tra), run_time=0.5)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"\Gamma = \frac{Z_L - Z_0}{Z_L + Z_0}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- caso 1: adaptado ---------------------------------------------
        fila1 = self._fila("adaptada", f"{GAMMA_ADAPTADO:.2f}", 1.45)
        rot.mostrar(pie_curso("Carga adaptada, 50 contra 50: gamma vale "
                              "cero y no vuelve nada."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(fila1, shift=0.14 * RIGHT), run_time=0.6)
        self.wait(4.6)

        # --- caso 2: el salto real 50 -> 75 -------------------------------
        fro_nuevo = self._frontera(Z_CARGA)
        z_der_nuevo = tag_hud("carga  ZL = 75 ohm", font_size=17,
                              color=C_TENUE)
        z_der_nuevo.move_to(z_der)
        fila2 = self._fila("salto a 75", f"{GAMMA_SALTO:+.2f}", 0.62)
        # El % que rebota sale de la propia pieza, no de una cuenta aparte.
        t_pot = tag_hud(f"{fro_nuevo.reflejada() * 100:.0f} %",
                        font_size=18)
        t_pot.next_to(t_ref, RIGHT, buff=0.22)
        rot.mostrar(pie_curso("A 75 ohmios ya rebota. El grosor de cada "
                              "flecha es la potencia que lleva."),
                    zona="abajo", run_time=0.5)
        self.play(ReplacementTransform(fro, fro_nuevo),
                  ReplacementTransform(z_der, z_der_nuevo),
                  FadeIn(fila2, shift=0.14 * RIGHT), FadeIn(t_ref),
                  FadeIn(t_pot), run_time=1.0)
        fro, z_der = fro_nuevo, z_der_nuevo
        self.wait(4.6)

        # --- caso 3: cortocircuito ----------------------------------------
        fro_nuevo = self._frontera(0.0)
        # Con gamma = -1 no cruza nada: la pieza deja una punta de flecha
        # degenerada al otro lado, que se apaga junto con su etiqueta.
        fro_nuevo.flechas[2].set_opacity(0.0)
        z_der_nuevo = tag_hud("corto  ZL = 0 ohm", font_size=17,
                              color=C_TENUE)
        z_der_nuevo.move_to(z_der)
        fila3 = self._fila("cortocircuito", f"{GAMMA_CORTO:+.2f}", -0.21)
        t_pot_nuevo = tag_hud(f"{fro_nuevo.reflejada() * 100:.0f} %",
                              font_size=18)
        t_pot_nuevo.next_to(t_ref, RIGHT, buff=0.22)
        rot.mostrar(pie_curso("Cortocircuito: gamma vale menos uno. "
                              "Vuelve TODO, y vuelve del revés."),
                    zona="abajo", run_time=0.5)
        self.play(ReplacementTransform(fro, fro_nuevo),
                  ReplacementTransform(z_der, z_der_nuevo),
                  ReplacementTransform(t_pot, t_pot_nuevo),
                  FadeOut(t_tra), FadeIn(fila3, shift=0.14 * RIGHT),
                  run_time=1.0)
        fro, z_der, t_pot = fro_nuevo, z_der_nuevo, t_pot_nuevo
        self.wait(4.6)

        # --- caso 4: circuito abierto -------------------------------------
        fro_nuevo = self._frontera(float("inf"))
        fro_nuevo.flechas[2].set_opacity(0.0)
        z_der_nuevo = tag_hud("abierto  ZL = inf", font_size=17,
                              color=C_TENUE)
        z_der_nuevo.move_to(z_der)
        fila4 = self._fila("abierto", f"{GAMMA_ABIERTO:+.2f}", -1.04)
        rot.mostrar(pie_curso("Abierto: gamma vale más uno. Vuelve todo "
                              "igual, y nada cruza al otro lado."),
                    zona="abajo", run_time=0.5)
        self.play(ReplacementTransform(fro, fro_nuevo),
                  ReplacementTransform(z_der, z_der_nuevo),
                  FadeIn(fila4, shift=0.14 * RIGHT), run_time=1.0)
        fro, z_der = fro_nuevo, z_der_nuevo
        self.wait(4.8)

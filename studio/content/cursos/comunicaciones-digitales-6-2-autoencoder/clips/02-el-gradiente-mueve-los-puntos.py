class Clip2(Scene):
    """6.2.2 - El gradiente mueve los puntos: la constelacion aprendida
    por epoca (0, 10, 30, 60, 120, 250) y su distancia minima MEDIDA
    subiendo de 0.151 a 0.926. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El gradiente mueve los puntos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el amasijo inicial ----------------------------------
        rot.mostrar(pie_curso("Ocho puntos al azar, con una sola atadura: "
                              "la energía media vale uno."),
                    zona="abajo", run_time=0.5)
        piq = plano_iq(unidad=0.86, alcance=1.95)
        piq.move_to(LEFT * 3.6 + UP * 0.45)
        pts = piq.puntos(HIST_AE[EPOCAS[0]], color=C_IA, radio=0.085)
        self.play(FadeIn(piq), run_time=0.8)
        self.play(FadeIn(pts, scale=0.6), run_time=0.7)

        et_paso = tag_hud(f"paso {EPOCAS[0]:03d}", font_size=20, color=C_IA)
        et_d = tag_hud(f"d_min = {fmt(D_INI, 3)}", font_size=20)
        et_e = tag_hud(f"E media = {fmt(E_INI, 3)}", font_size=19,
                       color=C_BANDA)
        cifras = VGroup(et_paso, et_d, et_e)
        cifras.arrange(DOWN, buff=0.17, aligned_edge=LEFT)
        cifras.next_to(piq, DOWN, buff=0.28)
        self.play(FadeIn(cifras), run_time=0.6)
        self.wait(3.6)

        # --- momento: la regla que se va a medir --------------------------
        rot.mostrar(pie_curso("Al lado medimos su distancia mínima: la que "
                              "decide cuántos símbolos se confundirán."),
                    zona="abajo", run_time=0.5)
        on = onda(PASOS_DMIN, SERIE_DMIN, rango_y=(0.0, 1.0), ancho=5.0,
                  alto=2.5, color=C_CIFRA)
        on.remove(on.curva)                 # la curva se dibuja por tramos
        on.move_to(RIGHT * 3.4 + UP * 0.35)
        et_on = tag_junto(on, "distancia mínima por paso", direccion=UP,
                          buff=0.18)
        et_x = tag_junto(on, "pasos de gradiente", direccion=DOWN,
                         buff=0.18)
        self.play(FadeIn(on.ejes), FadeIn(et_on), FadeIn(et_x),
                  run_time=0.9)
        marca = Dot(on.en(PASOS_DMIN[0], SERIE_DMIN[0]), radius=0.06,
                    color=C_CIFRA)
        self.play(FadeIn(marca, scale=0.5), run_time=0.5)
        self.wait(3.7)

        # --- momento: el gradiente empuja ---------------------------------
        rot.mostrar(pie_curso("Cada paso del gradiente los empuja a "
                              "separarse. Nadie les dijo dónde ir."),
                    zona="abajo", run_time=0.5)
        # Cada epoca: la animacion es CORTA y luego se descansa, para que
        # el ojo lea la cifra y el dibujo ya quietos y de acuerdo.
        i_prev = IDX_PASO[EPOCAS[0]]
        for ep, dt, quieto in ((10, 0.8, 0.5), (30, 0.8, 0.5),
                               (60, 0.8, 1.9), (120, 0.9, 0.6),
                               (250, 0.9, 0.6)):
            if ep == 120:
                rot.mostrar(pie_curso("La curva sube deprisa y luego se "
                                      "aplana: la red ya casi no puede "
                                      "mejorar."),
                            zona="abajo", run_time=0.5)
            j = IDX_PASO[ep]
            tramo = on.curva_de(PASOS_DMIN[i_prev:j + 1],
                                SERIE_DMIN[i_prev:j + 1], color=C_CIFRA)
            d_ep = SERIE_DMIN[j]
            self.play(
                Transform(pts, piq.puntos(HIST_AE[ep], color=C_IA,
                                          radio=0.085)),
                # Las cifras SALTAN en un cuarto de segundo: un morfeo
                # lento de digitos se lee como glifo roto.
                Succession(
                    Transform(et_paso,
                              tag_hud(f"paso {ep:03d}", font_size=20,
                                      color=C_IA).move_to(et_paso),
                              run_time=0.25),
                    Wait(dt - 0.25)),
                Succession(
                    Transform(et_d,
                              tag_hud(f"d_min = {fmt(d_ep, 3)}",
                                      font_size=20).move_to(et_d),
                              run_time=0.25),
                    Wait(dt - 0.25)),
                Create(tramo),
                marca.animate.move_to(on.en(PASOS_DMIN[j], d_ep)),
                run_time=dt)
            self.wait(quieto)
            i_prev = j
        self.wait(2.0)

        # --- momento: el salto MEDIDO -------------------------------------
        rot.mostrar(pie_curso("De un amasijo a una constelación, sin "
                              "manual y sin maestro."),
                    zona="abajo", run_time=0.5)
        salto = tag_hud(f"d_min: {fmt(D_INI, 3)} -> {fmt(D_FIN, 3)}",
                        font_size=21)
        salto.next_to(et_x, DOWN, buff=0.24)
        self.play(FadeIn(salto, shift=0.12 * UP), run_time=0.7)
        self.wait(5.0)

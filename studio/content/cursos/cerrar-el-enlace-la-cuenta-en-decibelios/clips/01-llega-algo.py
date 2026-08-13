class Clip1(Scene):
    """1 - ¿Llega algo? Portada del curso; despues el enlace completo en una
    sola imagen (satelite arriba a la derecha, antena abajo a la izquierda,
    haz entre ambos) y la cifra de potencia recibida, primero escrita con
    todos sus ceros y luego en notacion cientifica. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: portada del curso ----------------------------------
        portada = VGroup(
            titulo_marca("Cerrar el enlace", font_size=46),
            Text("la cuenta en decibelios", font_size=24, color=C_MARGEN),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.3)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(2.5)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.7)

        titulo = titulo_curso("¿Llega algo?")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.8)

        # --- momento: los dos extremos del enlace -------------------------
        sat = satelite(escala=1.15).move_to(RIGHT * 3.6 + UP * 1.5)
        tag_sat = tag_junto(sat, f"{P_TX_W:.0f} W", UP, buff=0.18,
                            font_size=20, color=C_SENAL)
        plato = antena(escala=1.15, mirando=UP).move_to(LEFT * 3.7 + DOWN * 1.1)

        self.play(FadeIn(sat, shift=0.2 * DOWN), FadeIn(plato, shift=0.2 * UP),
                  run_time=1.0)
        self.play(FadeIn(tag_sat), run_time=0.5)
        self.wait(0.6)

        rot.mostrar(pie_curso("Un satélite geoestacionario transmite con 20 "
                              "vatios: menos que un foco de refrigerador."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: el haz cruza los 36 000 km --------------------------
        camino = Line(sat.get_bottom() + DOWN * 0.08,
                      plato.get_top() + UP * 0.08,
                      stroke_width=2.2, color=C_SENAL)
        camino.set_opacity(0.55)
        # La etiqueta se separa PERPENDICULARMENTE al haz, no en horizontal:
        # asi guarda la misma distancia al trazo en toda su longitud.
        normal = rotate_vector(camino.get_unit_vector(), PI / 2)
        tag_d = tag_junto(camino, "36 000 km", RIGHT, buff=0.22, font_size=17)
        tag_d.move_to(camino.get_center() + normal * 0.34)

        self.play(Create(camino), run_time=1.4)
        self.play(FadeIn(tag_d), run_time=0.5)

        rot.mostrar(pie_curso("Lo que llega a tu antena, al otro lado de esa "
                              "línea, es esto."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: la cifra, con todos sus ceros -----------------------
        # El numero sale del style_block (C_RX_W), no escrito a mano: la
        # cuenta del curso y la cifra de su portada son la misma cuenta.
        # 13 decimales: con 12 el 4.3 se redondeaba a 4 y la cifra cruda ya no
        # coincidia con la notacion cientifica en la que se transforma.
        crudo = Text(f"{C_RX_W:.13f} W", font=FUENTE_HUD, font_size=28,
                     color=C_SENAL)
        crudo.move_to(DOWN * 1.85)
        self.play(FadeIn(crudo, shift=0.16 * UP), run_time=0.8)
        self.wait(3.2)

        cientifica = MathTex(r"4.3 \times 10^{-12}\ \text{W}", font_size=44,
                             color=C_SENAL)
        cientifica.move_to(crudo.get_center())
        self.play(Transform(crudo, cientifica), run_time=1.0)
        self.wait(4.0)

        rot.mostrar(pie_curso("Cuatro billonésimas de vatio. Y aun así, el "
                              "enlace funciona."), zona="abajo", run_time=0.5)
        self.wait(5.6)

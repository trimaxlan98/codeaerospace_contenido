class Clip2(Scene):
    """2 - Shack-Hartmann. La pupila partida en microlentes (aqui 49):
    con el frente plano cada mancha cae en el centro de su cuadro; con el
    mismo desenfoque + coma del clip 1 cada mancha se corre segun la
    PENDIENTE local (`pendientes_locales`), y de esos desplazamientos se
    reconstruye el frente. El RMS de la lectura lo mide la libreria.
    (~30 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Shack-Hartmann"), zona="arriba",
                    run_time=0.6)

        COEFS = {"desenfoque": 0.45, "coma": 0.32}

        # 9 x 9 microlentes (49 caen dentro del circulo). La pupila se
        # centra en y = -0.30: la lectura de la pieza queda en +1.56 (el
        # titulo empieza en +2.95) y los tags de abajo, por debajo de -2.1.
        sh = shack_hartmann(None, n=9, radio=1.52)
        sh.shift(DOWN * 0.30 - sh.pupila.get_center())

        # --- momento: la pupila partida en microlentes --------------------
        rot.mostrar(pie_curso("Un sensor Shack-Hartmann divide la pupila en "
                              "microlentes."), zona="abajo")
        self.play(Create(sh.pupila), run_time=0.7)
        self.play(LaggedStart(*[Create(q) for q in sh.rejilla],
                              lag_ratio=0.03), run_time=1.6)
        self.play(FadeIn(sh.referencias), FadeIn(sh.manchas),
                  FadeIn(sh.lectura), run_time=0.8)
        # Consolidar el grupo antes del Transform (si no, las partes
        # sueltas se quedarian dibujadas encima).
        self.add(sh)
        t_estado = tag_hud("frente plano: manchas centradas", font_size=17,
                           color=C_ONDA)
        t_estado.next_to(sh.pupila, DOWN, buff=0.30)
        self.play(FadeIn(t_estado), run_time=0.4)
        self.wait(4.0)

        # --- momento: si el frente se inclina, la mancha se corre ---------
        rot.mostrar(pie_curso("Cada microlente enfoca una mancha; si el "
                              "frente está inclinado ahí, la mancha se "
                              "corre."), zona="abajo")
        torcido = sh.con_frente(COEFS)
        self.play(FadeOut(t_estado), run_time=0.3)
        self.play(Transform(sh, torcido), run_time=2.2)

        # Las flechas van de la referencia (centro ideal, gris) a la mancha
        # YA desplazada: se recorren las lentes de mayor a menor
        # desplazamiento y se quedan cuatro separadas al menos 0.9, para
        # que no salgan las cuatro pegadas en el mismo borde.
        claves = list(torcido.desplazamientos)
        orden = sorted(range(len(claves)),
                       key=lambda k: -(torcido.desplazamientos[claves[k]][0] ** 2
                                       + torcido.desplazamientos[claves[k]][1] ** 2))
        elegidas = []
        for k in orden:
            p = sh.manchas[k].get_center()
            if all(np.linalg.norm(p - sh.manchas[j].get_center()) > 0.9
                   for j in elegidas):
                elegidas.append(k)
            if len(elegidas) == 4:
                break
        flechas = VGroup()
        for k in elegidas:
            ini = sh.referencias[k].get_center()
            fin = sh.manchas[k].get_center()
            flechas.add(Arrow(ini, fin, buff=0.0, stroke_width=2.6,
                              color=C_MEDIDA,
                              max_tip_length_to_length_ratio=0.38,
                              max_stroke_width_to_length_ratio=16))
        self.play(FadeIn(flechas), run_time=0.7)
        t_corrida = tag_hud("frente torcido: cada mancha se corre",
                            font_size=17, color=C_FRANJA)
        t_corrida.next_to(sh.pupila, DOWN, buff=0.30)
        self.play(FadeIn(t_corrida), run_time=0.4)
        self.wait(3.6)

        # --- momento: de los desplazamientos, las pendientes --------------
        rot.mostrar(pie_curso("De los desplazamientos salen las pendientes; "
                              "de las pendientes, el frente."), zona="abajo")
        t_ley = tag_hud("pendiente local -> desplazamiento", font_size=18)
        t_ley.next_to(t_corrida, DOWN, buff=0.18)
        self.play(FadeIn(t_ley, shift=0.10 * UP), run_time=0.5)
        self.play(Indicate(flechas, color=C_MEDIDA, scale_factor=1.10),
                  run_time=1.0)
        self.wait(4.8)

        # --- cierre --------------------------------------------------------
        rot.mostrar(pie_curso("Cientos de manchas, un solo frente "
                              "reconstruido."), zona="abajo")
        self.wait(5.6)

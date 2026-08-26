class Clip3(Scene):
    """7.1.3 - La MISMA direccion IP anunciada por BGP desde ocho sitios:
    cada usuario cae en el mas cercano por simple ruteo, y la latencia
    media medida sobre las doce ciudades del mapa baja de golpe. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Anycast")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        def pos(c, dy=-0.3):
            x, y = POS_MUNDO[c]
            return np.array([x, y + dy, 0.0])

        # --- momento: la misma IP en ocho sitios a la vez -------------------
        rot.mostrar(pie_curso("La misma direccion IP se anuncia por BGP "
                              "desde ocho sitios distintos, a la vez."),
                    zona="abajo", run_time=0.5)
        sitios = VGroup()
        nodos = {}
        for c in SITIOS_ANYCAST:
            n = nodo("servidor", c, 0.42, fs=12)
            n.move_to(pos(c))
            nodos[c] = n
            sitios.add(n)
        self.play(LaggedStart(*[FadeIn(n) for n in sitios], lag_ratio=0.12),
                  run_time=1.2)
        etiqueta_ip = tag_hud(IP_ANYCAST, font_size=22, color=C_PAQUETE)
        etiqueta_ip.move_to(UP * 2.55)
        self.play(FadeIn(etiqueta_ip), run_time=0.5)
        chips = VGroup()
        for c in SITIOS_ANYCAST:
            chip = ficha("IP", lado=0.30, fs=12)
            chip.next_to(nodos[c], UP, buff=0.12)
            chips.add(chip)
        self.play(LaggedStart(*[FadeIn(ch, scale=1.3) for ch in chips],
                              lag_ratio=0.15), run_time=1.2)
        self.wait(3.6)

        # --- momento: cada usuario cae en el mas cercano ---------------------
        rot.mostrar(pie_curso("Cada usuario cae, por simple ruteo, en el "
                              "sitio anunciado mas cercano."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(etiqueta_ip), FadeOut(chips), run_time=0.4)

        et_local = tag_hud("CDMX -> CDMX (local): %s ms"
                           % fmt(EJEMPLO_LOCAL["ms"], 1), font_size=18,
                           color=C_CIFRA)
        et_local.to_edge(DOWN, buff=1.55)
        self.play(Indicate(nodos["CDMX"], color=C_PAQUETE, scale_factor=1.3),
                  run_time=0.5)
        self.play(FadeIn(et_local), run_time=0.4)
        self.wait(1.6)
        self.play(FadeOut(et_local), run_time=0.3)

        londres = nodo("host", "Londres", 0.42, fs=12)
        londres.move_to(pos("Londres"))
        self.play(FadeIn(londres), run_time=0.3)
        ruta_londres = enlace(londres.centro(), nodos["Madrid"].centro(),
                              color=C_PAQUETE)
        self.play(Create(ruta_londres.linea), run_time=0.5)
        paq_l = ficha("GET", lado=0.28)
        paq_l.move_to(ruta_londres.a)
        self.play(MoveAlongPath(paq_l, ruta_londres.linea), run_time=0.6,
                  rate_func=linear)
        et_londres = tag_hud("Londres -> Madrid: %s ms"
                             % fmt(EJEMPLO_MEDIO["ms"], 1), font_size=18,
                             color=C_CIFRA)
        et_londres.to_edge(DOWN, buff=1.55)
        self.play(FadeIn(et_londres), run_time=0.4)
        self.wait(1.6)
        self.play(FadeOut(et_londres), run_time=0.3)

        joburgo = nodo("host", "Johannesburgo", 0.42, fs=11)
        joburgo.move_to(pos("Johannesburgo"))
        self.play(FadeIn(joburgo), run_time=0.3)
        ruta_jo = enlace(joburgo.centro(), nodos["Lagos"].centro(),
                         color=C_PAQUETE)
        self.play(Create(ruta_jo.linea), run_time=0.5)
        paq_j = ficha("GET", lado=0.28)
        paq_j.move_to(ruta_jo.a)
        self.play(MoveAlongPath(paq_j, ruta_jo.linea), run_time=0.6,
                  rate_func=linear)
        et_jo = tag_hud("Johannesburgo -> Lagos: %s ms"
                        % fmt(EJEMPLO_LEJOS["ms"], 1), font_size=18,
                        color=C_CIFRA)
        et_jo.to_edge(DOWN, buff=1.55)
        self.play(FadeIn(et_jo), run_time=0.4)
        self.wait(2.4)

        # --- momento: la latencia media, medida sobre las doce ---------------
        mapa = VGroup(sitios, londres, ruta_londres, paq_l, joburgo, ruta_jo,
                     paq_j, et_jo)
        self.play(FadeOut(mapa), run_time=0.6)
        rot.mostrar(pie_curso("Sobre las doce ciudades del mapa, la "
                              "latencia media cae de golpe. Es ruteo, no "
                              "magia."),
                    zona="abajo", run_time=0.5)
        barra_uno = regla_viajes(1, etiqueta="1 solo sitio (Madrid)",
                                 ms=ANYCAST_1["media_ms"])
        barra_uno.move_to(UP * 0.6)
        barra_ocho = regla_viajes(1, etiqueta="anycast, 8 sitios",
                                  ms=ANYCAST_8["media_ms"])
        barra_ocho.move_to(DOWN * 0.3)
        self.play(FadeIn(barra_uno), run_time=0.5)
        self.wait(1.0)
        self.play(FadeIn(barra_ocho), run_time=0.5)
        factor = tag_hud("%sx mejor" % fmt(ANYCAST_FACTOR, 1), font_size=24,
                         color=C_OK)
        factor.move_to(DOWN * 1.3)
        self.play(FadeIn(factor), run_time=0.5)
        self.wait(6.5)

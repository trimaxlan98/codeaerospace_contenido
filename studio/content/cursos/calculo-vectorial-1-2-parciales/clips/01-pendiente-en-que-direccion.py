class Clip1(Scene):
    """1.2.1 - La pendiente de un paisaje depende de la direccion: desde un
    mismo punto, cada rumbo sube (o baja) un numero distinto. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("¿Pendiente de qué dirección?")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: un punto en la ladera --------------------------------
        pl = plano_leccion()
        mapa = curvas_nivel(pl, PAISAJE, opacidad=0.45)
        self.play(FadeIn(pl), FadeIn(mapa), run_time=1.0)
        rot.mostrar(pie_curso("Paremos en un punto de la ladera: "
                              "¿cuál es SU pendiente?"), zona="abajo",
                    run_time=0.5)
        p0 = pl.punto(P0, color=C_VEC, radio=0.09)
        cifra0 = tag_hud(f"f({fmt(X0)}, {fmt(Y0)}) = {fmt(F0)}",
                         font_size=19, color=C_VEC)
        cifra0.next_to(p0, DOWN, buff=0.16)
        self.play(FadeIn(p0, scale=0.4), FadeIn(cifra0), run_time=0.6)
        self.wait(3.8)

        # --- momento: probar varios rumbos ---------------------------------
        rot.mostrar(pie_curso("La respuesta depende de por dónde salgas: "
                              "probemos varios rumbos."), zona="abajo",
                    run_time=0.5)
        flechas = VGroup()
        for ang, subida in zip(ANGULOS_ABANICO, SUBIDAS_ABANICO):
            u = _u_abanico(ang)
            flecha = flecha_libre(pl, P0, P0 + 1.5 * u, color=C_CIFRA,
                                  grosor=3.2)
            cifra = tag_hud(fmt(subida), font_size=17, color=C_CIFRA)
            cifra.move_to(pl.p(P0 + 1.85 * u))
            flechas.add(VGroup(flecha, cifra))
        self.play(LaggedStart(*[GrowArrow(g[0]) for g in flechas],
                              lag_ratio=0.3), run_time=1.8)
        self.play(LaggedStart(*[FadeIn(g[1], scale=0.6) for g in flechas],
                              lag_ratio=0.3), run_time=1.2)
        self.wait(3.8)

        # --- momento: una sube mas que las demas ----------------------------
        rot.mostrar(pie_curso("Una sube más que todas las otras: la "
                              "guardaremos para más adelante."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(flechas[1], color=C_GRAD, scale_factor=1.12),
                  run_time=1.0)
        self.wait(3.8)

        # --- momento: dos rumbos especiales ---------------------------------
        rot.mostrar(pie_curso("Pero para MEDIR con precisión hace falta "
                              "fijar un rumbo: empecemos por el este y "
                              "el norte."), zona="abajo", run_time=0.5)
        self.play(Indicate(flechas[0], color=C_CIFRA, scale_factor=1.15),
                  Indicate(flechas[2], color=C_CIFRA, scale_factor=1.15),
                  run_time=1.0)
        self.wait(3.8)

        rot.mostrar(pie_curso("Cortemos el paisaje en esas dos "
                              "direcciones, una a la vez."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

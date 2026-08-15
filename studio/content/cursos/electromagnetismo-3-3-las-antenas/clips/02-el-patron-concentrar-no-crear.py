class Clip2(Scene):
    """3.3.2 - El patron de radiacion en polares: el donut del dipolo de
    media onda visto de perfil, y su ganancia (2.15 dBi) INTEGRADA del
    propio patron, no leida de una tabla. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El patrón: concentrar, no crear")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la antena vertical, como en el clip 1 ----------------
        antena = Line(UP * 0.55, DOWN * 0.55, stroke_width=5.0,
                      color=C_CARGA)
        antena.move_to(DOWN * 0.15)
        self.play(Create(antena), run_time=0.6)
        rot.mostrar(pie_curso("La antena radia, sí. Pero ¿reparte igual "
                              "en todas direcciones?"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- momento: el patron polar del dipolo de media onda -------------
        # El +PI/2 gira la funcion: lobulos en horizontal, eje del dipolo
        # en vertical, coherente con la antena dibujada.
        rot.mostrar(pie_curso("El patrón: en cada dirección, el radio "
                              "dice cuánta señal sale."), zona="abajo",
                    run_time=0.5)
        pat = patron_polar([lambda t: patron_dipolo_medio(t + PI / 2)])
        pat.move_to(antena.get_center())
        self.play(FadeIn(pat.rejilla), run_time=0.7)
        self.play(Create(pat.lobulo(0)), run_time=1.8)
        self.wait(2.8)

        # --- momento: maximo de frente, nada por el eje --------------------
        rot.mostrar(pie_curso("De frente, todo; por el eje del alambre, "
                              "NADA. Es un donut visto de perfil."),
                    zona="abajo", run_time=0.5)
        f_der = Arrow(antena.get_center(), pat.punto_de(0, 0.0), buff=0.3,
                      color=C_ONDA, stroke_width=3.4, tip_length=0.16)
        f_izq = Arrow(antena.get_center(), pat.punto_de(0, 180.0),
                      buff=0.3, color=C_ONDA, stroke_width=3.4,
                      tip_length=0.16)
        self.play(GrowArrow(f_der), GrowArrow(f_izq), run_time=0.8)
        self.wait(4.4)

        # --- momento: la ganancia, integrada del propio patron -------------
        rot.mostrar(pie_curso("Integrando este MISMO patrón sale su "
                              "ganancia. No es una tabla: es la cuenta."),
                    zona="abajo", run_time=0.5)
        tag_d = tag_hud(f"D = {D_DIPOLO_MEDIO:.2f} = "
                        f"{G_DIPOLO_DBI:.2f} dBi", font_size=17)
        tag_d.next_to(pat.punto_de(0, 0.0), RIGHT, buff=0.30)
        tag_d.shift(UP * 0.55)
        self.play(FadeIn(tag_d, shift=0.1 * LEFT), run_time=0.6)
        self.wait(4.4)

        # --- momento: la ganancia no crea, roba ----------------------------
        rot.mostrar(pie_curso("La ganancia no crea energía: lo que da de "
                              "frente lo ROBA de las otras direcciones."),
                    zona="abajo", run_time=0.5)
        self.play(pat.lobulo(0).animate(rate_func=there_and_back)
                  .set_stroke(width=5.0), run_time=1.2)
        self.wait(3.6)

        rot.mostrar(pie_curso("Para hablar con un satélite hay que robar "
                              "mucho más. Hace falta geometría."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

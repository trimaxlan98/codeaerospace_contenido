class Clip3(Scene):
    """4.3.3 - Aparicion del choque en el extrados y separacion inducida.

    Pasado Mcr no ocurre nada dramatico: aparece una burbuja supersonica
    pequeña. Lo dramatico viene despues — esa burbuja tiene que cerrarse
    contra el flujo subsonico de detras, y solo sabe hacerlo con un choque.
    Y un choque sobre una capa limite la despega. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La burbuja y su choque")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Perfil convencional de la libreria, a tamaño grande.
        perfiles = perfiles_transonicos(cuerda=5.4, escala_perfil=3.4)
        perfil = perfiles.perfil(0)
        perfil.move_to(UP * 0.35)
        self.play(Create(perfil), run_time=1.0)
        rot.mostrar(pie_curso(f"Volando justo por encima de "
                              f"{MCR_GRUESO:.2f}, el Mach crítico."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: la burbuja -------------------------------------------
        # Se dibuja sobre el propio contorno del perfil, no en el aire.
        izq = perfil.get_left()[0]
        cuerda = perfil.width
        burbuja = Polygon(
            np.array([izq + cuerda * 0.14, perfil.get_top()[1] - 0.03, 0]),
            np.array([izq + cuerda * 0.30, perfil.get_top()[1] + 0.34, 0]),
            np.array([izq + cuerda * 0.52, perfil.get_top()[1] + 0.28, 0]),
            np.array([izq + cuerda * 0.55, perfil.get_top()[1] - 0.05, 0]),
            stroke_width=0, fill_color=C_SUPER, fill_opacity=0.28)
        tag_burbuja = Text("burbuja supersónica", font_size=19, color=C_SUPER)
        tag_burbuja.next_to(burbuja, UP, buff=0.20)

        self.play(FadeIn(burbuja), FadeIn(tag_burbuja), run_time=0.8)
        rot.mostrar(pie_curso("Aparece una burbuja de aire supersónico sobre "
                              "el extradós. Pequeña, y por ahora inofensiva."),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)

        # --- momento: el cierre --------------------------------------------
        choque = Line(np.array([izq + cuerda * 0.55,
                                perfil.get_top()[1] - 0.06, 0]),
                      np.array([izq + cuerda * 0.55,
                                perfil.get_top()[1] + 0.62, 0]),
                      stroke_width=3.6, color=C_SUPER)
        tag_choque = Text("choque", font_size=19, color=C_SUPER)
        tag_choque.next_to(choque, UP, buff=0.12)
        self.play(Create(choque), FadeIn(tag_choque), run_time=0.8)
        rot.mostrar(pie_curso("Pero detrás el flujo vuelve a ser subsónico, "
                              "y la burbuja tiene que cerrarse."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Solo sabe hacerlo de una manera: con un "
                              "choque."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: la separacion -----------------------------------------
        estela = VMobject(color=C_TRANS, stroke_width=2.4)
        estela.set_points_smoothly([
            np.array([izq + cuerda * 0.55, perfil.get_top()[1] - 0.02, 0]),
            np.array([izq + cuerda * 0.75, perfil.get_top()[1] + 0.22, 0]),
            np.array([izq + cuerda * 1.05, perfil.get_top()[1] + 0.32, 0])])
        tag_estela = Text("capa límite despegada", font_size=19, color=C_TRANS)
        tag_estela.next_to(estela.get_end(), DR, buff=0.10)
        self.play(Create(estela), FadeIn(tag_estela), run_time=0.9)
        rot.mostrar(pie_curso("Y un choque sobre una capa límite la despega "
                              "del perfil."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Ahí es donde el arrastre se dispara. No en "
                              "el Mach crítico: un poco después."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

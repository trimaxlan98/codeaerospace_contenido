class Clip1(Scene):
    """4.3.1 - La lluvia que apaga la Ka: la atenuacion especifica de
    ITU-R P.838 a 12, 20 y 30 GHz. La misma tormenta cobra cinco veces
    mas arriba, y la razon es geometrica: a 30 GHz la onda ya mide lo
    que mide una gota. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La lluvia que apaga la Ka")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        curvas = haz_curvas(
            [lambda r: atenuacion_lluvia(F_KU, r),
             lambda r: atenuacion_lluvia(F_KA_BAJA, r),
             lambda r: atenuacion_lluvia(F_KA_ALTA, r)],
            (0.0, 50.0), [C_B, C_E, C_CARGA],
            nombres=["12 GHz", "20 GHz", "30 GHz"],
            etiqueta_x="lluvia (mm/h)", etiqueta_y="dB/km", alto=3.6)
        curvas.move_to(RIGHT * 0.95 + DOWN * 0.05)

        # --- momento: el enemigo que no es la distancia --------------------
        rot.mostrar(pie_curso("Ya sabes llegar al satélite. Falta lo que "
                              "se cruza en el camino de vuelta."),
                    zona="abajo", run_time=0.45)
        self.play(FadeIn(curvas.ejes), run_time=0.6)
        self.wait(4.6)

        # --- momento: las tres curvas de la recomendación ------------------
        rot.mostrar(pie_curso("Esto es la ITU-R P.838: los decibelios que "
                              "cobra la lluvia por cada kilómetro."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.play(Create(curvas.curvas), FadeIn(curvas.etiquetas),
                  run_time=1.6)
        self.wait(4.6)

        # --- momento: el mismo chaparrón para las tres ---------------------
        guia = curvas.vertical_en(R_CHAPARRON, color=C_EJE)
        puntos = VGroup(*[
            Dot(curvas.punto_de(i, R_CHAPARRON), radius=0.065, color=c)
            for i, c in enumerate((C_B, C_E, C_CARGA))])
        rot.mostrar(pie_curso("Un chaparrón de veinticinco milímetros por "
                              "hora. La misma agua para las tres."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.play(Create(guia), *[FadeIn(p, scale=1.6) for p in puntos],
                  run_time=0.7)
        self.wait(4.6)

        # --- momento: las cifras, fuera de la caja y a la altura del punto --
        # Cada cifra sale de `atenuacion_lluvia`, la misma funcion que traza
        # su curva: el numero escrito no puede discrepar del trazo.
        cifras = VGroup()
        for i, (valor, color) in enumerate(((AT_KU, C_B),
                                            (AT_KA_BAJA, C_E),
                                            (AT_KA_ALTA, C_CARGA))):
            t = tag_hud(f"{valor:.1f} dB/km", font_size=17, color=color)
            t.move_to([-3.25, curvas.punto_de(i, R_CHAPARRON)[1], 0.0])
            cifras.add(t)
        cabecera = tag_hud("a 25 mm/h", font_size=16, color=C_TENUE)
        cabecera.next_to(cifras, UP, buff=0.30)
        rot.mostrar(pie_curso("Uno en Ku. Cinco en Ka. La misma tormenta, "
                              "cinco veces el peaje."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.play(FadeIn(cabecera), *[FadeIn(c, shift=0.1 * RIGHT)
                                      for c in cifras], run_time=0.7)
        self.wait(4.6)

        # --- momento: la razón física --------------------------------------
        onda = tag_hud(f"onda de {LAM_KA_MM:.0f} mm", font_size=16,
                       color=C_CARGA)
        onda.next_to(curvas.etiquetas[2], DOWN, buff=0.22)
        onda.align_to(curvas.etiquetas[2], LEFT)
        rot.mostrar(pie_curso("A treinta gigahercios la onda mide diez "
                              "milímetros: el tamaño de una gota."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.play(FadeIn(onda), run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Cuando la gota y la onda se parecen, la "
                              "gota dispersa la señal."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.wait(4.6)

        rot.mostrar(pie_curso("Por eso la banda C aguanta tormentas que "
                              "dejan mudo a un plato Ka."),
                    zona="abajo", run_time=0.45, salida=0.25)
        self.wait(4.8)

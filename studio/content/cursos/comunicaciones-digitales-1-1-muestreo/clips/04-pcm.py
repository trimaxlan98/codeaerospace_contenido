class Clip4(Scene):
    """1.1.4 - PCM: la muestra cuantizada se escribe en binario y sale
    como bits hacia la antena. Cierre de leccion. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("PCM: la curva hecha bits")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: una muestra elegida ---------------------------------
        rot.mostrar(pie_curso("Tomamos UNA muestra: su valor, redondeado, "
                              "es uno de 256 niveles."),
                    zona="abajo", run_time=0.5)
        on = onda(T_CURVA, Y_CURVA, rango_y=(-1.15, 1.15), ancho=7.4,
                  alto=2.6)
        on.move_to(UP * 1.15)
        self.play(FadeIn(on), run_time=0.8)
        p_m = on.en(T_MUESTRA_PCM, Y_MUESTRA_PCM)
        dot = Dot(p_m, radius=0.08, color=C_CIFRA)
        guia = on.vertical_en(T_MUESTRA_PCM, color=C_CIFRA)
        cifra = tag_hud(f"y = {fmt(Y_MUESTRA_PCM, 2)}", font_size=19)
        cifra.next_to(p_m, UR, buff=0.14)
        self.play(Create(guia), FadeIn(dot, scale=0.5), FadeIn(cifra),
                  run_time=1.0)
        self.wait(3.9)

        # --- momento: el valor se escribe en binario ----------------------
        rot.mostrar(pie_curso("Ese nivel se escribe en binario: ocho "
                              "bits, y la muestra ya es un numero."),
                    zona="abajo", run_time=0.5)
        tren = tren_bits(BITS_PCM, lado=0.5)
        tren.move_to(DOWN * 1.3)
        et_tren = tag_junto(tren, "la muestra, en bits", direccion=DOWN,
                            buff=0.2)
        self.play(TransformFromCopy(VGroup(dot, cifra), tren),
                  run_time=1.2)
        self.play(FadeIn(et_tren), run_time=0.4)
        self.wait(4.1)

        # --- momento: los bits salen hacia la antena ----------------------
        rot.mostrar(pie_curso("Muestra a muestra, la curva entera se "
                              "vuelve un rio de bits rumbo a la Tierra."),
                    zona="abajo", run_time=0.5)
        enl = enlace_tierra(dist=3.2, radio_tierra=0.38, curva=0.3)
        enl.rotate(PI)  # la nave a la izquierda, la Tierra a la derecha
        enl.move_to(DOWN * 2.3 + RIGHT * 2.5)
        # el camino nace en la Tierra: para ir sonda -> Tierra se invierte
        cam_ida = enl.camino.copy().reverse_points()
        paq = enl.paquete(radio=0.06)
        paq.move_to(cam_ida.point_from_proportion(0.0))
        self.play(FadeIn(enl), run_time=0.8)
        self.play(PulsoDeSenal(paq, cam_ida, rate_func=linear),
                  destello(enl.camino, color=C_BIT), run_time=1.6)
        paq.move_to(cam_ida.point_from_proportion(0.0))
        self.play(PulsoDeSenal(paq, cam_ida, rate_func=linear),
                  run_time=1.2)
        self.wait(2.5)

        # --- cierre de leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "La voz de la sonda no es la curva.",
            "Son los bits que la cuentan.",
            "Siguiente leccion: el pulso que lleva cada bit.",
            on, dot, guia, cifra, tren, et_tren, enl, paq)

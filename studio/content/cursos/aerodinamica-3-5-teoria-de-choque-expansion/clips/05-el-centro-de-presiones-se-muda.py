class Clip5(Scene):
    """3.5.5 - Por que el centro de presiones se situa cerca de la mitad de
    la cuerda.

    En subsonico esta al cuarto de cuerda; en supersonico, a la mitad. Y no
    es un detalle academico: al cruzar Mach 1 el centro se MUEVE hacia atras
    y el avion pica. Cierre de la leccion y del modulo 3. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))

        titulo = titulo_curso("El centro de presiones se muda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        placa = perfil_supersonico("placa", M_PERFIL, ALFA, cuerda=4.2,
                                   largo_onda=1.2)
        placa.move_to(UP * 0.75)
        self.play(Create(placa.perfil), run_time=0.7)
        self.play(*[Create(o) for o in placa.ondas], run_time=1.0)
        rot.mostrar(pie_curso("En una placa plana supersónica la presión es "
                              "la MISMA a lo largo de toda la cara."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # Presion uniforme: flechas iguales repartidas por la cuerda. Que
        # sean todas del mismo tamaño ES el argumento del clip.
        extremos = placa.perfil.get_start(), placa.perfil.get_end()
        direccion = (extremos[1] - extremos[0])
        normal = np.array([-direccion[1], direccion[0], 0.0])
        normal = normal / np.linalg.norm(normal)
        uniformes = VGroup()
        for k in np.linspace(0.12, 0.88, 6):
            base = extremos[0] + direccion * k
            uniformes.add(Arrow(base - normal * 0.62, base - normal * 0.10,
                                buff=0, stroke_width=2.6, color=C_SUPER,
                                max_tip_length_to_length_ratio=0.30))
        self.play(LaggedStart(*[FadeIn(f) for f in uniformes],
                              lag_ratio=0.12), run_time=1.2)
        rot.mostrar(pie_curso("No hay pico en el borde de ataque. Todas las "
                              "flechas miden lo mismo."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: donde cae la resultante ------------------------------
        centro = extremos[0] + direccion * 0.5
        resultante = Arrow(centro - normal * 1.15, centro - normal * 0.10,
                           buff=0, stroke_width=5.0, color=C_TRANS,
                           max_tip_length_to_length_ratio=0.22)
        tag = Text("centro de presiones", font_size=20, color=C_TRANS)
        tag.next_to(resultante, DOWN, buff=0.18)
        self.play(FadeIn(resultante), FadeIn(tag), run_time=0.8)
        rot.mostrar(pie_curso("Y una carga uniforme tiene su resultante en "
                              "el medio. A media cuerda."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("En subsónico está al cuarto de cuerda. En "
                              "supersónico, a la mitad."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Al cruzar Mach 1 el centro se va hacia atrás. "
                              "Y el avión pica."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        # --- cierre de la leccion y del modulo -----------------------------
        self.play(FadeOut(VGroup(placa, uniformes, resultante, tag)),
                  run_time=0.8)
        cierre = VGroup(
            titulo_marca("Ya sabes resolver el aire", font_size=35,
                         color=C_TITULO),
            titulo_marca("cuando va rápido de verdad.", font_size=35,
                         color=C_SUPER)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)

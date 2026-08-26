class Clip2(Scene):
    """6.1.2 - Los codigos de estado: que familia decide que, y el
    precio en viajes de seguir una redireccion. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Los codigos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la tabla de codigos -----------------------------------
        rot.mostrar(pie_curso("Toda respuesta trae un codigo de tres "
                              "cifras. La primera cifra es la familia."),
                    zona="abajo", run_time=0.5)
        filas = [[str(c), n, s] for c, n, s in CODIGOS_LECCION]
        t = tabla(["Codigo", "Nombre", "Que dice"], filas,
                 anchos=[1.1, 3.6, 4.6], alto=0.52, fs=15,
                 resaltable=True)
        t.move_to(UP * 0.95)
        self.play(FadeIn(t), run_time=0.9)
        self.wait(5.0)

        # --- momento: de quien es la culpa ------------------------------------
        rot.mostrar(pie_curso("El 4 dice que la pediste mal; el 5 dice "
                              "que el que se rompio fue el servidor."),
                    zona="abajo", run_time=0.5)
        marco_404 = SurroundingRectangle(t.fila(2), color=C_PERDIDA,
                                         buff=0.08, stroke_width=2.4)
        marco_500 = SurroundingRectangle(t.fila(3), color=C_PERDIDA,
                                         buff=0.08, stroke_width=2.4)
        self.play(Create(marco_404), Create(marco_500), run_time=0.8)
        self.wait(4.8)

        # --- momento: el 301 se destaca -----------------------------------------
        rot.mostrar(pie_curso("El 301 es distinto: no es un error. Dice "
                              "'esto se mudo, ve alli'."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(marco_404), FadeOut(marco_500), run_time=0.4)
        t2 = t.con_filas(filas, resaltar=1)
        self.play(Transform(t, t2), run_time=0.7)
        self.wait(3.6)

        # --- momento: seguir la redireccion cuesta un viaje -----------------------
        rot.mostrar(pie_curso("Seguirlo cuesta un viaje entero mas: la "
                              "pagina nueva no aparece hasta los %d ms."
                              % int(2.0 * RTT_MS)),
                    zona="abajo", run_time=0.5)
        t_chica = tabla(["Codigo", "Nombre", "Que dice"], filas,
                       anchos=[0.75, 2.35, 3.05], alto=0.34, fs=12,
                       resaltar=1, resaltable=True)
        t_chica.to_edge(UP, buff=0.85)
        self.play(Transform(t, t_chica), run_time=0.7)
        esc = escalera(
            ["Navegador", "Servidor"],
            [{"de": "Navegador", "a": "Servidor", "texto": "GET /promo",
              "t_ms": 0.0},
             {"de": "Servidor", "a": "Navegador",
              "texto": "301  Location: /promo-actual", "t_ms": RTT_MS,
              "color": C_COLA},
             {"de": "Navegador", "a": "Servidor",
              "texto": "GET /promo-actual", "t_ms": RTT_MS},
             {"de": "Servidor", "a": "Navegador", "texto": "200 OK",
              "t_ms": 2.0 * RTT_MS, "color": C_OK}],
            ancho=6.4, alto=2.35, fs=14)
        esc.move_to(DOWN * 0.15)
        self.play(FadeIn(esc.actores), FadeIn(esc.vidas), run_time=0.5)
        for k in range(4):
            self.play(Create(esc.paso(k)), run_time=0.6)
        et_total = tag_hud("2 RTT completos  =  %d ms" % int(2.0 * RTT_MS),
                          font_size=20, color=C_CIFRA)
        et_total.move_to(DOWN * 2.35)
        self.play(FadeIn(et_total, shift=0.14 * UP), run_time=0.5)
        self.wait(4.4)

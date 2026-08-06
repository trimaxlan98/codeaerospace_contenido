class Clip5(Scene):
    """5 - Leer el waterfall. Cuatro firmas reales (portadora CW, banda FM,
    rafagas AFSK, traza Doppler) se identifican en relevo con un recuadro
    ambar sobre el waterfall sintetico; el Doppler vuelve al final, pulsa y
    queda resaltado en pantalla."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo ---------------------------------------
        modulo = hud_modulo("Modulo 05")
        titulo = titulo_curso("Leer el waterfall")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.35)
        rot.mostrar(titulo, zona="arriba", run_time=0.35)

        # --- momento: el waterfall aparece --------------------------------
        agua = waterfall_imagen(ancho=6.3, alto=3.3, columnas=220, filas=120,
                                semilla=7)
        agua.move_to(UP * 0.1)
        self.play(FadeIn(Group(agua)), run_time=0.6)
        rot.mostrar(pie_curso("Cada línea, una FFT. El tiempo cae, la "
                              "frecuencia cruza, el color es potencia."),
                   zona="abajo", run_time=0.35)
        self.wait(5.0)

        # --- momento: identificacion 1, la portadora CW -------------------
        rect_cw = Rectangle(width=agua.width * 0.03, height=agua.height * 0.90,
                            color=C_SENAL, stroke_width=3)
        rect_cw.move_to(agua.pos_de(-0.55, 0.5))
        self.play(FadeIn(rect_cw), run_time=0.3)
        rot.mostrar(pie_curso("Línea fina e inmóvil: una portadora."),
                   zona="abajo", run_time=0.35)
        self.wait(5.0)
        self.play(FadeOut(rect_cw), run_time=0.25)

        # --- momento: identificacion 2, la banda FM ------------------------
        rect_fm = Rectangle(width=agua.width * 0.15, height=agua.height * 0.90,
                            color=C_SENAL, stroke_width=3)
        rect_fm.move_to(agua.pos_de(-0.12, 0.5))
        self.play(FadeIn(rect_fm), run_time=0.3)
        rot.mostrar(pie_curso("Banda gruesa que respira: FM de "
                              "radiodifusión."), zona="abajo", run_time=0.35)
        self.wait(5.0)
        self.play(FadeOut(rect_fm), run_time=0.25)

        # --- momento: identificacion 3, rafagas AFSK ------------------------
        rect_afsk = Rectangle(width=agua.width * 0.11, height=agua.height * 0.90,
                              color=C_SENAL, stroke_width=3)
        rect_afsk.move_to(agua.pos_de(0.32, 0.5))
        self.play(FadeIn(rect_afsk), run_time=0.3)
        rot.mostrar(pie_curso("Trazos cortos e intermitentes: ráfagas de "
                              "un cubesat."), zona="abajo", run_time=0.35)
        self.wait(5.2)
        self.play(FadeOut(rect_afsk), run_time=0.25)

        # --- momento: identificacion 4, la traza Doppler ---------------------
        linea_doppler = Line(agua.pos_de(0.72, 0.02), agua.pos_de(0.38, 0.98),
                             stroke_width=10, color=C_SENAL, stroke_opacity=0.55)
        self.play(FadeIn(linea_doppler), run_time=0.3)
        rot.mostrar(pie_curso("Y la línea que se inclina: el Doppler de un "
                              "pase. La firma de un satélite."),
                   zona="abajo", run_time=0.35)
        self.wait(5.2)

        # --- momento: el Doppler pulsa y queda resaltado ---------------------
        # La linea no sale y vuelve: se intensifica en su sitio (sin
        # parpadeo). El resalte pasa a blanco (tope del colormap: potencia
        # maxima): ambar sobre la traza ambar del waterfall no contrastaba.
        self.play(linea_doppler.animate.set_stroke(color=C_TITULO, width=11,
                                                   opacity=0.9),
                  run_time=0.3)
        self.play(Indicate(linea_doppler, color=C_TITULO, scale_factor=1.05),
                  run_time=0.7)
        rot.mostrar(pie_curso("Una interferencia terrestre jamás deriva "
                              "así."), zona="abajo", run_time=0.35)
        self.wait(5.2)

        # --- momento: cierre ------------------------------------------------
        rot.mostrar(pie_curso("Leer esto en dos segundos: eso es operar "
                              "una estación."), zona="abajo", run_time=0.35)
        self.wait(5.2)

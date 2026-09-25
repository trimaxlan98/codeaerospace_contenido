class Clip4(Scene):
    """8.3.4 - La imagen del 7.2 (SINTETICA, 48 x 32, 8 bits) llega entera,
    grande y centrada, linea a linea, con marco verde: lo recuperado.
    A un lado su tamano (gris, parametro), al otro los errores tras
    Viterbi (cian, MET). Cierre del CURSO. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La imagen"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        alto_px, ancho_px = IMG_RX.shape
        alto = 5.0
        ancho = alto * ancho_px / alto_px
        centro = np.array([0.0, 0.05, 0.0])

        im = ImageMobject(np.stack([IMG_RX] * 3, -1).astype(np.uint8))
        im.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        im.stretch_to_fit_width(ancho).stretch_to_fit_height(alto)
        im.move_to(centro)
        marco = Rectangle(width=ancho, height=alto, color=C_OK,
                          stroke_width=4).move_to(centro)

        # la cortina: tapa las lineas que aun no llegan
        lineas = ValueTracker(0)

        def _cortina():
            k = int(np.floor(lineas.get_value() + 1e-6))
            h = alto * (alto_px - k) / alto_px
            r = Rectangle(width=ancho + 0.04, height=max(h, 1e-3),
                          stroke_width=0, fill_color=CODE_BG,
                          fill_opacity=1.0 if k < alto_px else 0.0)
            r.align_to(im, DOWN).set_x(centro[0])
            return r

        cortina = always_redraw(_cortina)
        self.add(Group(im), cortina)
        self.play(Create(marco), run_time=0.8)
        rot.mostrar(dato_pie("imagen sintetica"), zona="abajo", run_time=0.5)
        self.wait(0.6)
        self.play(lineas.animate.set_value(alto_px), run_time=8.0,
                  rate_func=linear)
        cortina.clear_updaters()
        self.remove(cortina)
        self.wait(1.0)

        # --- a los lados: su tamano (gris) y sus errores (cian) -------------
        d_tam = VGroup(tag_dato(f"{ancho_px} x {alto_px}", font_size=24),
                       tag_dato("8 bits", font_size=24)
                       ).arrange(DOWN, buff=0.16)
        d_tam.next_to(marco, LEFT, buff=0.45)
        c_err = VGroup(Text("Viterbi", font_size=24, color=C_TENUE),
                       tag_hud(f"{MET['errores_viterbi']} errores",
                               font_size=26)
                       ).arrange(DOWN, buff=0.16)
        c_err.next_to(marco, RIGHT, buff=0.45)
        self.play(FadeIn(d_tam, shift=RIGHT * 0.1), run_time=0.6)
        self.wait(1.4)
        self.play(FadeIn(c_err, shift=LEFT * 0.1), run_time=0.6)
        self.wait(1.6)
        self.play(Indicate(marco, color=C_OK, scale_factor=1.02),
                  run_time=1.0)
        self.wait(5.0)

        cierre_leccion(self, rot, "Una radio es aritmetica.",
                       "Ahora sabes leerla.", Group(im), marco, d_tam,
                       c_err, espera=6.0)

class Clip4(Scene):
    """7.2.4 - La imagen (SINTETICA, 48 x 32, 8 bits) se arma linea a
    linea: a la izquierda la recibida tras Viterbi (IMG_RX, marco verde),
    a la derecha la misma con los errores crudos del canal aplicados a sus
    bits (IMG_CRUDA, marco rojo, 'sin codigo'). Cian: pixeles errados de
    cada una. Cierre. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La imagen"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        alto_px, ancho_px = IMG_RX.shape
        ancho = 5.8
        alto = ancho * alto_px / ancho_px

        def imagen(arr, x):
            im = ImageMobject(np.stack([arr] * 3, -1).astype(np.uint8))
            im.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
            im.stretch_to_fit_width(ancho).stretch_to_fit_height(alto)
            im.move_to(np.array([x, 0.1, 0]))
            return im

        im_rx = imagen(IMG_RX, -3.3)
        im_cr = imagen(IMG_CRUDA, 3.3)
        m_rx = Rectangle(width=ancho, height=alto, color=C_OK,
                         stroke_width=3).move_to(im_rx)
        m_cr = Rectangle(width=ancho, height=alto, color=C_RUIDO,
                         stroke_width=3).move_to(im_cr)
        t_rx = tag_junto(m_rx, "tras Viterbi", UP, buff=0.2, font_size=24,
                         color=C_OK)
        t_cr = tag_junto(m_cr, "sin codigo", UP, buff=0.2, font_size=24,
                         color=C_DATO)
        t_cr.align_to(t_rx, UP)

        # la cortina: tapa las lineas que aun no llegan
        lineas = ValueTracker(0)

        def cortina(im):
            def f():
                k = int(np.floor(lineas.get_value() + 1e-6))
                h = alto * (alto_px - k) / alto_px
                r = Rectangle(width=ancho + 0.04, height=max(h, 1e-3),
                              stroke_width=0, fill_color=CODE_BG,
                              fill_opacity=1.0 if k < alto_px else 0.0)
                r.align_to(im, DOWN).set_x(im.get_x())
                return r
            return always_redraw(f)

        c_rx, c_cr = cortina(im_rx), cortina(im_cr)
        self.add(im_rx, im_cr, c_rx, c_cr)
        self.play(Create(m_rx), Create(m_cr), FadeIn(t_rx), FadeIn(t_cr),
                  run_time=0.8)
        rot.mostrar(dato_pie("imagen sintetica"), zona="abajo", run_time=0.5)
        self.wait(0.8)

        # --- linea a linea ---------------------------------------------------
        self.play(lineas.animate.set_value(alto_px), run_time=9.0,
                  rate_func=linear)
        c_rx.clear_updaters()
        c_cr.clear_updaters()
        self.remove(c_rx, c_cr)
        self.wait(1.2)

        # --- lo que llego: pixeles errados de cada una -----------------------
        n_px = alto_px * ancho_px
        mal_rx = int(np.sum(IMG_RX != IMG))
        mal_cr = int(np.sum(IMG_CRUDA != IMG))
        e_rx = tag_hud(f"{mal_rx} de {n_px} pixeles", font_size=24)
        e_rx.next_to(m_rx, DOWN, buff=0.28)
        e_cr = tag_hud(f"{mal_cr} de {n_px} pixeles", font_size=24)
        e_cr.next_to(m_cr, DOWN, buff=0.28)
        self.play(FadeIn(e_cr), run_time=0.5)
        self.wait(1.2)
        self.play(FadeIn(e_rx), run_time=0.5)
        self.wait(1.2)
        rot.mostrar(dato_pie(f"{ancho_px} x {alto_px}, 8 bits"), zona="abajo", run_time=0.5)
        self.wait(2.4)
        rot.mostrar(cifra_pie(f"{fmt(100 * BER_CRUDA, 1)} % -> {ERR_VIT}"
                              " errores"), zona="abajo", run_time=0.5)
        self.wait(3.0)
        self.play(Indicate(m_rx, color=C_OK, scale_factor=1.03),
                  run_time=1.0)
        self.wait(2.0)

        cierre_leccion(self, rot, "Una imagen del planeta",
                       "desde un aparato de 30 dolares.",
                       im_rx, im_cr, m_rx, m_cr, t_rx, t_cr, e_rx, e_cr,
                       espera=5.0)

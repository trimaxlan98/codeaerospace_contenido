# =====================================================================
# Promo "Nadie manda en Internet" — curso 25, Protocolos de Internet.
#
#   estado 0   ..  los ejes vacios
#   0.35-6.85  ..  la ventana se dibuja: sube +1 por RTT y cada vez que
#                  algo se pierde (marca roja) la parte por la mitad
#   6.85-8.05  ..  aparece la media MEDIDA de la traza
#   8.05-10.65 ..  respiro
#   10.65-12.45 .. el trazo se recoge
#   estado 0   ..  los ejes vacios otra vez
#
# Las marcas rojas no se encienden a ojo: cada una aparece cuando el
# trazo llega a su RTT, comparando el avance con su indice en la traza.
# =====================================================================


class Promo(Scene):
    def setup(self):
        code_brand.aplicar_marca(self, esquinas=True, marca=False, fondo=True)

    def construct(self):
        fmt = FMT

        if fmt.es_vertical:
            centro = fmt.centro_util + UP * 0.60
            ancho, alto = 6.4, 4.4
            pos_media = UP * (fmt.suelo + 1.15)
            pos_tag = UP * (fmt.tope - 0.70)
        else:
            centro = fmt.centro_util + LEFT * 2.2
            ancho, alto = 8.2, 4.2
            pos_media = centro + RIGHT * 5.6
            pos_tag = centro + UP * 2.9

        self.add(_promo.fondo_seguro(fmt), _promo.marca_promo(fmt))
        if GUIAS:
            self.add(_promo.guias(fmt))

        s = sierra(TRAZA, perdidas=PERDIDAS, ancho=ancho, alto=alto,
                   color=C_PAQUETE, media=True)
        s.move_to(centro)

        tag = etiqueta_hud("VENTANA DE ENVIO", font_size=15, color=CODE_MUTED)
        tag.move_to(pos_tag)
        cifra_media = Text(f"{MEDIA:.1f}", font=FUENTE_HUD, font_size=58,
                           color=C_CIFRA).move_to(pos_media)
        etiqueta = etiqueta_hud("DE MEDIA", font_size=17, color=CODE_MUTED)
        etiqueta.next_to(cifra_media, DOWN, buff=0.28)

        # --- estado de arranque Y de cierre ---------------------------
        self.add(s.ejes, tag)
        self.wait(0.35)

        # Las marcas empiezan apagadas y se encienden a su paso.
        for m in s.marcas:
            m.set_opacity(0.0)
        s.media.set_opacity(0.0)
        self.add(s.marcas, s.media)

        def revelar(m, alpha):
            for marca, rtt in zip(s.marcas, PERDIDAS):
                visible = alpha >= rtt / float(len(TRAZA) - 1)
                marca.set_opacity(1.0 if visible else 0.0)

        # --- 1. la sierra se dibuja -----------------------------------
        self.play(Create(s.curva), UpdateFromAlphaFunc(s.marcas, revelar),
                  run_time=6.5, rate_func=linear)

        # --- 2. la media medida ---------------------------------------
        self.play(s.media.animate.set_opacity(0.85),
                  FadeIn(cifra_media), FadeIn(etiqueta), run_time=1.2)
        self.wait(2.6)

        # --- 3. se recoge ---------------------------------------------
        self.play(Uncreate(s.curva),
                  s.media.animate.set_opacity(0.0),
                  s.marcas.animate.set_opacity(0.0),
                  FadeOut(cifra_media), FadeOut(etiqueta), run_time=1.8)
        # Tambien la curva: Uncreate la deja en la escena reducida a un
        # muñon de longitud cero que la costura del bucle sigue viendo.
        self.remove(s.curva, s.marcas, s.media, cifra_media, etiqueta)
        self.wait(0.35)

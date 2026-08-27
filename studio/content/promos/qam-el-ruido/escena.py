# =====================================================================
# Promo "Cuando el ruido se come el simbolo" — curso 24.
#
#   estado 0   ..  los 16 simbolos limpios, nada mas
#   0.35-1.05  ..  aparecen los 600 envios con poco ruido: nubes apretadas
#   1.05-6.05  ..  baja la señal: las nubes crecen, pisan al vecino y los
#                  que se deciden mal se ponen rojos y se cuentan
#   6.05-10.05 ..  vuelve a subir: las nubes se cierran y el contador baja
#   10.05-10.75 .. los envios se apagan
#   estado 0   ..  los 16 simbolos limpios otra vez
# =====================================================================


class Promo(Scene):
    def setup(self):
        code_brand.aplicar_marca(self, esquinas=True, marca=False, fondo=True)

    def construct(self):
        fmt = FMT

        if fmt.es_vertical:
            centro = fmt.centro_util + UP * 0.55
            pos_cifra = UP * (fmt.suelo + 1.20)
            pos_tag = UP * (fmt.tope - 0.70)
        else:
            centro = fmt.centro_util + LEFT * 3.3
            pos_cifra = centro + RIGHT * 4.7 + DOWN * 0.4
            pos_tag = centro + RIGHT * 4.7 + UP * 1.6

        self.add(_promo.fondo_seguro(fmt), _promo.marca_promo(fmt))
        if GUIAS:
            self.add(_promo.guias(fmt))

        def en_pantalla(z):
            return centro + np.array([z.real, z.imag, 0.0]) * ESCALA

        # Los 16 simbolos de la constelacion: el mapa que el receptor
        # conoce de memoria. Estan desde el primer frame y no se van.
        malla = VGroup(*[Dot(en_pantalla(p), radius=0.095, color=C_PUNTO)
                         for p in PUNTOS])
        malla.set_z_index(20)

        rx0, mal0 = recibidos(EB_ALTO)
        nube = VGroup(*[Dot(en_pantalla(z), radius=0.038,
                            color=C_ERR if m else C_OK)
                        for z, m in zip(rx0, mal0)])
        nube.set_opacity(0.0)

        lectura = VGroup(cifra(0).move_to(pos_cifra))
        etiqueta = etiqueta_hud("SE DECIDEN MAL", font_size=17,
                                color=CODE_MUTED)
        etiqueta.next_to(lectura, DOWN, buff=0.30)
        tag = etiqueta_hud(f"16 SIMBOLOS, {ENVIOS} ENVIOS", font_size=15,
                           color=CODE_MUTED)
        tag.move_to(pos_tag)

        # --- estado de arranque Y de cierre ---------------------------
        self.add(malla)
        self.wait(0.35)

        def pintar(ebn0):
            rx, mal = recibidos(ebn0)
            for punto, z, m in zip(nube, rx, mal):
                punto.move_to(en_pantalla(z))
                punto.set_color(C_ERR if m else C_OK)
            lectura.become(VGroup(cifra(int(np.sum(mal)))
                                  .move_to(pos_cifra)))
            return int(np.sum(mal))

        pintar(EB_ALTO)
        self.play(nube.animate.set_opacity(0.9), FadeIn(lectura),
                  FadeIn(etiqueta), FadeIn(tag), run_time=0.7)

        # --- 1. baja la señal ------------------------------------------
        vivo = VGroup(nube, lectura)

        def barrer(desde, hasta):
            def paso(m, alpha):
                pintar(desde + (hasta - desde) * alpha)
            return paso

        self.play(UpdateFromAlphaFunc(vivo, barrer(EB_ALTO, EB_BAJO)),
                  run_time=5.0, rate_func=smooth)
        # --- 2. y vuelve a subir --------------------------------------
        self.play(UpdateFromAlphaFunc(vivo, barrer(EB_BAJO, EB_ALTO)),
                  run_time=4.0, rate_func=smooth)

        # --- 3. se apagan los envios ----------------------------------
        self.play(nube.animate.set_opacity(0.0), FadeOut(lectura),
                  FadeOut(etiqueta), FadeOut(tag), run_time=0.7)
        self.remove(nube, lectura, etiqueta, tag)
        self.wait(0.35)

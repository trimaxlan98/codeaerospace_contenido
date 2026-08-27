# =====================================================================
# Promo "El muro del sonido" — curso 10, Aerodinamica.
#
#   estado 0   ..  Mach 0: los frentes son circulos concentricos
#   0.35-4.35  ..  el Mach sube a 1: los frentes se apilan por delante
#                  hasta hacerse todos tangentes en la fuente. La pared.
#   4.35-5.35  ..  respiro en Mach 1.00
#   5.35-7.55  ..  Mach 1.8: se abre el cono y aparece su angulo medido
#   7.55-8.95  ..  respiro con el cono
#   8.95-11.35 ..  vuelve a Mach 0
#   estado 0   ..  circulos concentricos otra vez
# =====================================================================


class Promo(Scene):
    def setup(self):
        code_brand.aplicar_marca(self, esquinas=True, marca=False, fondo=True)

    def construct(self):
        fmt = FMT

        if fmt.es_vertical:
            arriba = fmt.centro_util + UP * 2.2
            pos_cifra = UP * (fmt.suelo + 1.15)
            pos_angulo = UP * (fmt.tope - 0.70)
        else:
            arriba = fmt.centro_util + LEFT * 2.6 + UP * 1.4
            pos_cifra = fmt.centro_util + RIGHT * 4.4
            pos_angulo = fmt.centro_util + RIGHT * 4.4 + UP * 2.0

        self.add(_promo.fondo_seguro(fmt), _promo.marca_promo(fmt))
        if GUIAS:
            self.add(_promo.guias(fmt))

        dibujo = frentes(0.0, arriba)
        lectura = VGroup(cifra(0.0).move_to(pos_cifra))
        etiqueta = etiqueta_hud("MACH", font_size=17, color=CODE_MUTED)
        etiqueta.next_to(lectura, DOWN, buff=0.28)
        # El angulo del cono solo existe por encima de Mach 1: por debajo
        # este renglon esta, pero vacio y transparente (asi el bucle cierra
        # con el mismo numero de mobjects en pantalla).
        # Va ARRIBA, no debajo de la cifra: `next_to` respecto de una
        # etiqueta VACIA no mide nada y el rotulo caia en mitad del dibujo.
        angulo = VGroup(etiqueta_hud("", font_size=16, color=C_CONO)
                        .move_to(pos_angulo))

        # --- estado de arranque Y de cierre ---------------------------
        self.add(dibujo, lectura, etiqueta, angulo)
        self.wait(0.35)

        vivo = VGroup(dibujo, lectura, angulo)

        def poner(mach):
            dibujo.become(frentes(mach, arriba))
            lectura.become(VGroup(cifra(mach).move_to(pos_cifra)))
            if mach > 1.0001:
                texto = etiqueta_hud(f"CONO {angulo_mach(mach):.0f} GRADOS",
                                     font_size=16, color=C_CONO)
                texto.move_to(pos_angulo)
                texto.set_opacity(min(1.0, (mach - 1.0) * 5.0))
            else:
                texto = etiqueta_hud("", font_size=16, color=C_CONO)
                texto.move_to(pos_angulo)
            angulo.become(VGroup(texto))

        def barrer(desde, hasta):
            def paso(m, alpha):
                poner(desde + (hasta - desde) * alpha)
            return paso

        # --- 1. hasta la pared ----------------------------------------
        self.play(UpdateFromAlphaFunc(vivo, barrer(0.0, 1.0)),
                  run_time=4.0, rate_func=smooth)
        self.wait(1.0)
        # --- 2. al otro lado ------------------------------------------
        self.play(UpdateFromAlphaFunc(vivo, barrer(1.0, MACH_MAX)),
                  run_time=2.2, rate_func=smooth)
        self.wait(1.4)
        # --- 3. y de vuelta -------------------------------------------
        self.play(UpdateFromAlphaFunc(vivo, barrer(MACH_MAX, 0.0)),
                  run_time=2.4, rate_func=smooth)
        self.wait(0.35)

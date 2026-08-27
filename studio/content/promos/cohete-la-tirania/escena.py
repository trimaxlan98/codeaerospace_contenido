# =====================================================================
# Promo "La tirania del cohete" — curso 17, Tsiolkovsky.
#
#   estado 0   ..  el cohete ENTERO es carga util (cian), impulso 0
#   0.35-6.50  ..  el impulso sube y el combustible (ambar) va comiendose
#                  la carga; la cifra es el dv alcanzado
#   6.50-7.20  ..  la carga llega a CERO a 8840 m/s y la referencia se
#                  pone en rojo: faltan 548 m/s para orbita
#   7.20-8.80  ..  respiro
#   8.80-11.30 ..  el combustible se vacia y la carga vuelve
#   estado 0   ..  el cohete entero es carga util otra vez
#
# La referencia "ORBITA 9388" esta desde el primer frame: se ve subir la
# cifra hacia ella y pararse antes. Eso es la tirania.
# =====================================================================


class Promo(Scene):
    def setup(self):
        code_brand.aplicar_marca(self, esquinas=True, marca=False, fondo=True)

    def construct(self):
        fmt = FMT
        # La silueta suma cuerpo + nariz: 5.8 de cuerpo llegan a 6.6 de
        # alto real, y la punta se comia la etiqueta de arriba.
        alto = 5.8 if fmt.es_vertical else 5.0
        ancho = 1.35

        if fmt.es_vertical:
            centro = fmt.centro_util + UP * 0.25
            pos_cifra = UP * (fmt.suelo + 1.15)
            pos_tag = UP * (fmt.tope - 0.75)
        else:
            centro = fmt.centro_util + LEFT * 3.6
            pos_cifra = centro + RIGHT * 4.4 + UP * 0.4
            pos_tag = centro + RIGHT * 4.4 + UP * 2.2

        self.add(_promo.fondo_seguro(fmt), _promo.marca_promo(fmt))
        if GUIAS:
            self.add(_promo.guias(fmt))

        def cohete(dv):
            s = silueta_cohete(*fracciones(dv), alto=alto, ancho=ancho)
            return s.shift(centro)

        nave = cohete(0.0)
        lectura = VGroup(cifra(0.0).move_to(pos_cifra))
        referencia = etiqueta_hud(f"ORBITA {DV_LEO:.0f}", font_size=18,
                                  color=CODE_MUTED)
        referencia.next_to(lectura, DOWN, buff=0.30)
        falta = etiqueta_hud(f"FALTAN {FALTAN:.0f} M/S", font_size=18,
                             color=C_FALTA)
        falta.move_to(referencia)
        tag = etiqueta_hud("UNA SOLA ETAPA", font_size=16, color=CODE_MUTED)
        tag.move_to(pos_tag)

        # --- estado de arranque Y de cierre ---------------------------
        self.add(nave, lectura, referencia, tag)
        self.wait(0.35)

        # --- 1. el impulso sube y se come el cohete -------------------
        # Todo lo que cambia va DENTRO del play (un updater sobre un
        # mobject ajeno a la animacion se ejecuta pero no se ve).
        vivo = VGroup(nave, lectura)

        def subir(m, alpha):
            dv = DV_CERO * alpha
            nave.become(cohete(dv))
            lectura.become(VGroup(cifra(dv).move_to(pos_cifra)))

        self.play(UpdateFromAlphaFunc(vivo, subir),
                  run_time=6.15, rate_func=smooth)

        # --- 2. se acabo la carga util antes de llegar ----------------
        self.play(FadeOut(referencia), FadeIn(falta), run_time=0.7)
        self.wait(1.6)

        # --- 3. marcha atras: el cohete vuelve a ser carga util -------
        def bajar(m, alpha):
            dv = DV_CERO * (1.0 - alpha)
            nave.become(cohete(dv))
            lectura.become(VGroup(cifra(dv).move_to(pos_cifra)))

        self.play(UpdateFromAlphaFunc(vivo, bajar),
                  FadeOut(falta, run_time=0.8),
                  FadeIn(referencia, run_time=0.8),
                  run_time=2.5, rate_func=smooth)
        self.wait(0.35)

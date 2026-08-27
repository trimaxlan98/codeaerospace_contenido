# =====================================================================
# Promo "Que es un determinante" — curso 22, Algebra lineal.
#
#   estado 0   ..  la rejilla sin tocar y el cuadrado unidad; 1.00
#   0.35-5.35  ..  la transformacion aplasta el plano: la rejilla se
#                  inclina, el cuadrado se convierte en paralelogramo y
#                  la cifra baja hasta 0.00
#   5.35-8.85  ..  respiro con el plano aplastado sobre una recta
#   8.85-11.85 ..  vuelve a la identidad
#   estado 0   ..  la rejilla sin tocar otra vez
#
# La cifra es `paralelogramo(...).area`: el area con signo de las
# columnas de la matriz. Lo que se ve y lo que se lee son lo mismo.
# =====================================================================


class Promo(Scene):
    def setup(self):
        code_brand.aplicar_marca(self, esquinas=True, marca=False, fondo=True)

    def construct(self):
        fmt = FMT

        if fmt.es_vertical:
            centro = fmt.centro_util + UP * 0.55
            pos_cifra = UP * (fmt.suelo + 1.15)
            # 1.02 x 4 = 4.08 de alcance: la rejilla sangra por los
            # lados (un plano no puede tener bordes visibles) y aun
            # asi deja libre la banda de la cifra.
            unidad, alcance = 1.02, 4
        else:
            centro = fmt.centro_util + LEFT * 3.2
            pos_cifra = centro + RIGHT * 4.8
            unidad, alcance = 0.85, 5

        self.add(_promo.fondo_seguro(fmt), _promo.marca_promo(fmt))
        if GUIAS:
            self.add(_promo.guias(fmt))

        pl = plano(unidad=unidad, alcance=alcance)
        pl.move_to(centro)

        area = paralelogramo(pl, matriz(0.0), color=C_AREA, opacidad=0.35)
        area.set_z_index(5)
        lectura = VGroup(cifra(1.0).move_to(pos_cifra))
        etiqueta = etiqueta_hud("DETERMINANTE", font_size=17,
                                color=CODE_MUTED)
        etiqueta.next_to(lectura, DOWN, buff=0.30)

        # --- estado de arranque Y de cierre ---------------------------
        self.add(pl, area, lectura, etiqueta)
        self.wait(0.35)

        vivo = VGroup(pl, area, lectura)

        def poner(s):
            m = matriz(s)
            pl.aplicar(m)
            nuevo = paralelogramo(pl, m, color=C_AREA, opacidad=0.35)
            nuevo.set_z_index(5)
            area.become(nuevo)
            lectura.become(VGroup(cifra(nuevo.area).move_to(pos_cifra)))

        def barrer(desde, hasta):
            def paso(m, alpha):
                poner(desde + (hasta - desde) * alpha)
            return paso

        # --- 1. el plano se aplasta -----------------------------------
        self.play(UpdateFromAlphaFunc(vivo, barrer(0.0, 1.0)),
                  run_time=5.0, rate_func=smooth)
        self.wait(3.5)
        # --- 2. y vuelve --------------------------------------------
        self.play(UpdateFromAlphaFunc(vivo, barrer(1.0, 0.0)),
                  run_time=3.0, rate_func=smooth)
        self.wait(0.35)

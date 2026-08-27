# =====================================================================
# Promo "El angulo que la naturaleza eligio" — curso 14, Matematicas en
# la naturaleza.
#
# El bucle (lo que hace que el video se repita solo):
#
#   estado 0  ..  el polo, un punto ambar en un lienzo vacio
#   0.0-3.0   ..  las semillas nacen del centro hacia afuera
#   3.0-5.2   ..  aparecen las dos familias de espirales: 8 y 13
#   5.2-7.8   ..  el angulo se desafina y VUELVE: el patron se rompe y
#                 se recompone; la cifra en pantalla lo cuenta
#   7.8-9.3   ..  el disco se consume desde el filo hacia el polo
#   estado 0  ..  el polo otra vez -> el ultimo frame ES el primero
#
# Sin subtitulos: la unica letra en pantalla es la cifra medida y su
# etiqueta HUD. `render_promo.py --frames` mide la costura del bucle.
# =====================================================================


class Promo(Scene):
    def setup(self):
        # La marca de agua se pone aparte: en vertical la esquina inferior
        # derecha es la columna de botones de la app.
        code_brand.aplicar_marca(self, esquinas=True, marca=False, fondo=True)

    def construct(self):
        fmt = FMT
        radio = fmt.radio_max(0.80)

        if fmt.es_vertical:
            centro = fmt.centro_util
            # La cifra se ancla al SUELO util, no al disco: asi no se sale
            # de la zona que la app deja libre por muy grande que sea el
            # disco, y el hueco de abajo es siempre el mismo.
            pos_lectura = UP * (fmt.suelo + 1.15)
        else:
            # En 16:9 el disco ya llena el alto util: la cifra no cabe
            # debajo, pero sobra sitio al lado. Se RECOLOCA, no se encoge.
            centro = fmt.centro_util + LEFT * 3.0
            pos_lectura = centro + RIGHT * (radio + 3.1)

        self.add(_promo.fondo_seguro(fmt), _promo.marca_promo(fmt))
        if GUIAS:
            self.add(_promo.guias(fmt))

        # --- estado de arranque Y de cierre: el polo, solo -------------
        polo = Dot(centro, radius=0.06, color=C_SEMILLA_CENTRO)
        polo.set_z_index(5)
        self.add(polo)
        self.wait(0.35)

        disco = filotaxis(n=SEMILLAS, angulo_deg=ANGULO, escala=radio,
                          color_centro=C_SEMILLA_CENTRO,
                          color_borde=C_SEMILLA_BORDE)
        disco.move_to(centro)

        angulo = ValueTracker(ANGULO)
        lectura = cifra(ANGULO).move_to(pos_lectura)
        etiqueta = etiqueta_hud("GRADOS POR SEMILLA", font_size=17,
                                color=CODE_MUTED)
        etiqueta.next_to(lectura, DOWN, buff=0.34)

        # --- 1. las semillas nacen ------------------------------------
        self.play(disco.aparecer(run_time=3.0),
                  FadeIn(lectura, run_time=0.9),
                  FadeIn(etiqueta, run_time=0.9))

        # --- 2. las dos familias de espirales -------------------------
        # No se dibuja ninguna curva encima: se ENCIENDEN las semillas que
        # forman cada brazo. El brazo es de verdad esas semillas, y el disco
        # no se llena de tinta ajena.
        def brazos(m, cuantos):
            paso = max(1, m // cuantos)
            arranques = list(range(0, m, paso))[:cuantos]
            return VGroup(*[disco.puntos[k] for d in arranques
                            for k in range(d, SEMILLAS, m)])

        fam_a = brazos(FAMILIA_A, BRAZOS_A)
        fam_b = brazos(FAMILIA_B, BRAZOS_B)
        self.play(disco.puntos.animate.set_opacity(0.22), run_time=0.4)
        self.play(fam_a.animate.set_opacity(1.0).set_color(C_ESPIRAL_A),
                  run_time=0.7)
        self.wait(0.35)
        self.play(fam_a.animate.set_opacity(0.22).set_color(C_SEMILLA_BORDE),
                  fam_b.animate.set_opacity(1.0).set_color(C_ESPIRAL_B),
                  run_time=0.7)
        self.wait(0.35)
        # Las semillas vuelven a su degradado original (no a un color
        # plano): el disco tiene que quedar EXACTAMENTE como estaba.
        original = filotaxis(n=SEMILLAS, angulo_deg=ANGULO, escala=radio,
                             color_centro=C_SEMILLA_CENTRO,
                             color_borde=C_SEMILLA_BORDE)
        self.play(*[d.animate.set_opacity(1.0).set_color(o.get_color())
                    for d, o in zip(disco.puntos, original.puntos)],
                  run_time=0.5)

        # --- 3. el angulo se desafina y vuelve ------------------------
        # La cifra se re-dibuja cada frame SOLO durante el barrido: crear un
        # Text por frame es caro y el resto del clip no lo necesita.
        viva = always_redraw(
            lambda: cifra(angulo.get_value()).move_to(pos_lectura))
        self.remove(lectura)
        self.add(viva)
        disco.add_updater(lambda m: m.girar_a(angulo.get_value()))
        self.play(angulo.animate.set_value(ANGULO + DESVIO),
                  run_time=2.6, rate_func=there_and_back)
        disco.clear_updaters()
        self.remove(viva)
        self.add(lectura)

        # --- 4. el disco se consume desde el filo ---------------------
        semillas = list(disco.puntos)
        self.play(
            LaggedStart(*[ShrinkToCenter(d) for d in reversed(semillas)],
                        lag_ratio=2.4 / len(semillas), run_time=1.5),
            FadeOut(lectura, run_time=0.7),
            FadeOut(etiqueta, run_time=0.7))
        # Fuera del todo: una semilla de tamano cero sigue siendo un
        # mobject, y la costura del bucle se mide al pixel.
        self.remove(disco)
        self.wait(0.35)

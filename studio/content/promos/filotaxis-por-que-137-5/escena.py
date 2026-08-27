# =====================================================================
# Promo 2 "Por que 137.5" — curso 14, Matematicas en la naturaleza.
#
# Promo 1 enganchaba; este responde. La explicacion entra por la IMAGEN
# (el contraejemplo), no por la voz: quien lo vea en silencio —que son
# muchos— tiene que entenderlo igual.
#
#   estado 0   ..  el polo, un punto ambar en un lienzo vacio
#   0.35-2.75  ..  las semillas nacen con 90 grados: cuatro rayos y cuatro
#                  cuñas vacias
#   2.75-3.45  ..  se dibuja el hueco: el circulo vacio MAS GRANDE que
#                  cabe en el disco, medido por la libreria
#   3.95-8.15  ..  el angulo barre de 90 al aureo; los rayos se disuelven,
#                  los huecos se cierran y la cifra lo cuenta
#   8.15-9.95  ..  el hueco nuevo, 8 veces mas pequeño, junto al fantasma
#                  del viejo
#   9.95-11.55 ..  el disco se consume desde el filo hacia el polo
#   estado 0   ..  el polo otra vez -> el ultimo frame ES el primero
# =====================================================================


class Promo(Scene):
    def setup(self):
        code_brand.aplicar_marca(self, esquinas=True, marca=False, fondo=True)

    def construct(self):
        fmt = FMT
        # Algo mas pequeño que en el promo 1: aqui hay bloque arriba (la
        # cifra) y abajo (la medida), y los dos tienen que respirar.
        radio = fmt.radio_max(0.70)

        if fmt.es_vertical:
            centro = fmt.centro_util
            pos_cifra = UP * (fmt.tope - 1.05)
            pos_medida = UP * (fmt.suelo + 0.95)
        else:
            centro = fmt.centro_util + LEFT * 3.2
            pos_cifra = centro + RIGHT * (radio + 3.2) + UP * 0.9
            pos_medida = centro + RIGHT * (radio + 3.2) + DOWN * 0.9

        self.add(_promo.fondo_seguro(fmt), _promo.marca_promo(fmt))
        if GUIAS:
            self.add(_promo.guias(fmt))

        # Las dos medidas, calculadas ANTES de animar nada: lo que se ve en
        # pantalla es su salida, no un tamaño elegido a ojo.
        h_malo = hueco_maximo(SEMILLAS, ANGULO_MALO, radio)
        h_bueno = hueco_maximo(SEMILLAS, ANGULO, radio)
        veces = h_malo["radio"] / h_bueno["radio"]

        # --- estado de arranque Y de cierre: el polo, solo -------------
        polo = Dot(centro, radius=0.06, color=C_SEMILLA_CENTRO)
        polo.set_z_index(5)
        self.add(polo)
        self.wait(0.35)

        disco = filotaxis(n=SEMILLAS, angulo_deg=ANGULO_MALO, escala=radio,
                          color_centro=C_SEMILLA_CENTRO,
                          color_borde=C_SEMILLA_BORDE)
        disco.move_to(centro)

        angulo = ValueTracker(ANGULO_MALO)
        lectura = cifra(ANGULO_MALO).move_to(pos_cifra)
        etiqueta = etiqueta_hud("GRADOS POR SEMILLA", font_size=17,
                                color=CODE_MUTED)
        etiqueta.next_to(lectura, DOWN, buff=0.30)

        # --- 1. las semillas nacen con el angulo MALO ------------------
        self.play(disco.aparecer(run_time=2.4),
                  FadeIn(lectura, run_time=0.8),
                  FadeIn(etiqueta, run_time=0.8))

        # --- 2. el hueco, dibujado donde esta -------------------------
        aro_malo = anillo(h_malo, centro, C_HUECO, grosor=3.4)
        tag_hueco = etiqueta_hud("HUECO MAXIMO", font_size=18, color=C_HUECO)
        tag_hueco.move_to(pos_medida)
        self.play(GrowFromCenter(aro_malo), FadeIn(tag_hueco), run_time=0.7)
        self.wait(0.5)

        # --- 3. el barrido: de 90 al aureo ----------------------------
        # La cifra se re-dibuja cada frame SOLO durante el barrido: un Text
        # por frame es caro y el resto del clip no lo necesita.
        viva = always_redraw(
            lambda: cifra(angulo.get_value()).move_to(pos_cifra))
        self.remove(lectura)
        self.add(viva)
        # El barrido va como ANIMACION del disco, no como updater suelto:
        # el renderer cachea en una imagen estatica todo lo que no participa
        # del play, asi que un updater sobre un mobject ajeno a la animacion
        # se ejecuta pero NO se ve (las semillas se quedaban en la cruz con
        # la cifra ya en 137.5).
        def barrer(m, a):
            ang = ANGULO_MALO + (ANGULO - ANGULO_MALO) * a
            angulo.set_value(ang)
            m.girar_a(ang)

        self.play(UpdateFromAlphaFunc(disco, barrer),
                  aro_malo.animate.set_stroke(opacity=0.55),
                  FadeOut(tag_hueco, run_time=0.6),
                  run_time=4.2, rate_func=smooth)
        self.remove(viva)
        lectura = cifra(ANGULO).move_to(pos_cifra)
        self.add(lectura)

        # --- 4. el hueco nuevo, junto al fantasma del viejo ------------
        aro_bueno = anillo(h_bueno, centro, C_CIFRA, grosor=3.4)
        tag_veces = etiqueta_hud(f"{veces:.0f} veces mas pequeno",
                                 font_size=18, color=C_CIFRA)
        tag_veces.move_to(pos_medida)
        self.play(GrowFromCenter(aro_bueno), FadeIn(tag_veces), run_time=0.8)
        # El respiro largo no es estetico: la voz termina aqui, y el bucle
        # necesita que el audio calle ANTES del ultimo frame o el salto al
        # principio se oye.
        self.wait(2.4)

        # --- 5. el disco se consume desde el filo ---------------------
        semillas = list(disco.puntos)
        self.play(
            LaggedStart(*[ShrinkToCenter(d) for d in reversed(semillas)],
                        lag_ratio=2.4 / len(semillas), run_time=1.6),
            FadeOut(aro_malo, run_time=0.6),
            FadeOut(aro_bueno, run_time=0.6),
            FadeOut(tag_veces, run_time=0.7),
            FadeOut(lectura, run_time=0.7),
            FadeOut(etiqueta, run_time=0.7))
        # Fuera del todo: una semilla de tamaño cero sigue siendo un
        # mobject, y la costura del bucle se mide al pixel.
        self.remove(disco)
        self.wait(0.35)

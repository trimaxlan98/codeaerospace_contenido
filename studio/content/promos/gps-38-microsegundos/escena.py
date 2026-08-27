# =====================================================================
# Promo "Los 38 microsegundos del GPS" — curso 16, Relatividad y el GPS.
#
#   estado 0   ..  la Tierra, la orbita y el satelite en su sitio; 0.0 KM
#   0.35-7.85  ..  pasa un dia: el satelite da DOS vueltas y el error de
#                  posicion sube hasta 11.5 km
#   7.85-10.25 ..  respiro con la cifra arriba
#   10.25-11.35 .. la cifra se apaga y vuelve a 0.0: empieza otro dia
#   estado 0   ..  el satelite esta donde empezo -> el bucle cierra
#
# Que el satelite de dos vueltas EXACTAS no es decorativo: es lo que
# permite que el ultimo frame sea el primero.
# =====================================================================


class Promo(Scene):
    def setup(self):
        code_brand.aplicar_marca(self, esquinas=True, marca=False, fondo=True)

    def construct(self):
        fmt = FMT
        radio = 2.45 if fmt.es_vertical else 2.15

        if fmt.es_vertical:
            centro = fmt.centro_util + UP * 0.65
            pos_cifra = UP * (fmt.suelo + 1.25)
            pos_causa = UP * (fmt.tope - 0.70)
        else:
            centro = fmt.centro_util + LEFT * 3.5
            pos_cifra = centro + RIGHT * 4.6 + DOWN * 0.3
            pos_causa = centro + RIGHT * 4.6 + UP * 1.5

        self.add(_promo.fondo_seguro(fmt), _promo.marca_promo(fmt))
        if GUIAS:
            self.add(_promo.guias(fmt))

        orb = orbita_gps(radio_escena=radio, alpha0=ALPHA0)
        orb.shift(centro - orb.tierra.get_center())
        orb.en(ALPHA0)
        # El cuerpo de fabrica es un punto de dos pixeles en el telefono.
        orb.satelite[1].scale(2.0)
        r_orb = 0.5 * orb.orbita.width

        def estela(alpha):
            """Cola de cometa detras del satelite: da sensacion de avance
            tambien en la segunda vuelta, cuando la orbita ya esta pisada."""
            a = ALPHA0 + VUELTAS * alpha
            return Arc(radius=r_orb, start_angle=TAU * (a - COLA),
                       angle=TAU * COLA, arc_center=orb.tierra.get_center(),
                       stroke_color=C_SAT, stroke_width=3.0,
                       stroke_opacity=0.45)

        cola = estela(0.0)

        lectura = VGroup(cifra(0.0).move_to(pos_cifra))
        etiqueta = etiqueta_hud("ERROR EN UN DIA", font_size=17,
                                color=CODE_MUTED)
        etiqueta.next_to(lectura, DOWN, buff=0.30)
        # La causa, arriba: el reloj de ahi arriba adelanta. La consecuencia,
        # abajo: kilometros. Las dos cifras son de la libreria.
        # Un decimal, no cero: la deriva es 38.50 y ".0f" la redondeaba a
        # 39, que es justo la cifra que delata un rotulo mal hecho.
        causa = etiqueta_hud(f"ADELANTA {DERIVA:.1f} MICROSEGUNDOS",
                             font_size=14, color=C_SAT)
        causa.move_to(pos_causa)

        # --- estado de arranque Y de cierre ---------------------------
        self.add(cola, orb, lectura, etiqueta, causa)
        self.wait(0.35)

        # --- 1. pasa un dia -------------------------------------------
        vivo = VGroup(orb, lectura, cola)

        def pasar_el_dia(m, alpha):
            orb.en(ALPHA0 + VUELTAS * alpha)
            cola.become(estela(alpha))
            lectura.become(VGroup(
                cifra(error_metros(HORAS_DIA * alpha) / 1000.0)
                .move_to(pos_cifra)))

        self.play(UpdateFromAlphaFunc(vivo, pasar_el_dia),
                  run_time=7.5, rate_func=linear)
        self.wait(2.4)

        # --- 2. empieza otro dia --------------------------------------
        self.play(FadeOut(lectura), run_time=0.55)
        lectura.become(VGroup(cifra(0.0).move_to(pos_cifra)))
        self.play(FadeIn(lectura), run_time=0.55)
        self.wait(0.35)

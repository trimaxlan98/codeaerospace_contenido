# 04 · Un ciclo son metro y cuarto
#
# El clip que cierra el modulo del silicio. Cuatro estados y ni uno mas:
# el cristal, el PLL, el periodo y — el remate — el TAMAÑO FISICO de un
# ciclo.
#
# Cifras: las cuatro salen de `esp32.py` en el render. Los 40 MHz del
# cristal son hoja de datos (etiqueta APAGADA); el multiplicador, el
# periodo y los metros los calcula la libreria (etiqueta AMBAR).
#
# La densidad de los dos trenes del segundo estado NO es decorativa: el
# tren de la CPU lleva `round(3 * multiplicador_pll())` pulsos sobre el
# mismo ancho que los 3 del cristal, asi que el x6 que dice la cifra es el
# que se ve en el dibujo.
#
# El remate es una MEDIDA, no una grafica: un suelo, una barra ambar que
# crece desde el suelo y un tope. Crece mientras el contador sube, y las
# dos cosas paran a la vez porque el contador lee el reloj de la escena
# (`renderer.time`), no un `dt` acumulado.


def _tic(largo, color=AMBAR, grosor=4.0):
    """Una rayita vertical: el extremo de una medida. Es `lz.filete`
    girado, no una pieza nueva."""
    return lz.filete(ancho=largo, color=color, grosor=grosor).rotate(PI / 2)


class Clip(Pieza):
    NUMERO = 4

    def pieza(self):
        L = self.L

        f_cristal = chip.HOJA["f_cristal"]
        f_cpu = chip.HOJA["f_cpu"]
        mult = chip.multiplicador_pll()
        ns = chip.periodo(f_cpu) * 1e9
        metros = chip.luz_por_ciclo(f_cpu)

        n_x = 3
        n_cpu = int(round(n_x * mult))
        ancho_tren = 5.2

        # --- 1. el cuarzo: el latido de fuera -------------------------
        tren_1 = chip.pulsos(n=n_x, duty=0.5, ancho=ancho_tren, alto=3.0,
                             color=TINTA)
        etq_1 = rot("CRISTAL")
        b1 = VGroup(etq_1, tren_1).arrange(DOWN, buff=0.42)
        L.escena(b1, animacion=AnimationGroup(
            Create(tren_1, run_time=1.6),
            FadeIn(etq_1, run_time=0.8), lag_ratio=0.0))
        self.wait(0.8)

        L.dato(f"{f_cristal / 1e6:.0f}", "megahercios del cristal",
               medido=False, t=0.6)
        self.wait(3.6)

        # --- 2. el PLL: el mismo latido, seis veces mas denso ----------
        tren_x = chip.pulsos(n=n_x, duty=0.5, ancho=ancho_tren, alto=1.5,
                             color=APAGADO)
        tren_c = chip.pulsos(n=n_cpu, duty=0.5, ancho=ancho_tren, alto=1.5,
                             color=AMBAR)
        etq_x, etq_c = rot("CRISTAL"), rot("CPU")
        b2 = VGroup(VGroup(etq_x, tren_x).arrange(DOWN, buff=0.28),
                    VGroup(tren_c, etq_c).arrange(DOWN, buff=0.28)
                    ).arrange(DOWN, buff=0.80)
        L.escena(b2, salida=0.45, animacion=AnimationGroup(
            Create(VGroup(tren_x, tren_c), lag_ratio=0.0, run_time=1.6),
            FadeIn(VGroup(etq_x, etq_c), run_time=0.8), lag_ratio=0.0))
        self.wait(0.7)

        L.dato(f"{mult:.0f}x", "multiplicador del pll", t=0.6)
        self.wait(3.8)

        # --- 3. lo que dura UNO de esos ciclos -------------------------
        tren_3 = chip.pulsos(n=n_x, duty=0.5, ancho=ancho_tren, alto=2.6,
                             color=APAGADO)
        ancho_ciclo = tren_3.width / n_x
        span = VGroup(lz.filete(ancho=ancho_ciclo, color=AMBAR, grosor=4.0),
                      _tic(0.24), _tic(0.24))
        span[1].move_to(span[0].get_left())
        span[2].move_to(span[0].get_right())
        span.next_to(tren_3, DOWN, buff=0.34)
        span.shift(RIGHT * (tren_3.get_left()[0] + ancho_ciclo / 2
                            - span.get_center()[0]))
        etq_3 = rot("UN CICLO")
        etq_3.next_to(span, DOWN, buff=0.26)
        etq_3.set_x(span.get_center()[0])
        b3 = VGroup(tren_3, span, etq_3)
        L.escena(b3, salida=0.45, animacion=Succession(
            Create(tren_3, run_time=1.4),
            AnimationGroup(Create(span, lag_ratio=0.0, run_time=0.6),
                           FadeIn(etq_3, run_time=0.6), lag_ratio=0.0)))
        self.wait(0.7)

        L.dato(f"{ns:.2f}", "nanosegundos por ciclo", t=0.6)
        self.wait(4.0)

        # --- 4. el remate: ese ciclo tiene tamaño ---------------------
        # El tren se va ANTES para que la medida nazca en azul limpio.
        L.quitar("escena", t=0.5)

        # El contador arranca cuando arranca la barra (t0 + los 0.4 de
        # apagar el dato viejo, los 0.6 de encender el nuevo y los 0.35
        # que tardan en aparecer los dos extremos) y llega al final justo
        # cuando la barra toca el poste de la derecha.
        t0 = self.renderer.time
        subida = 2.2
        t_ini = t0 + 1.0 + 0.35

        def _avance(t):
            a = (float(t) - t_ini) / subida
            return f"{metros * min(max(a, 0.0), 1.0):.2f}"

        L.contador_vivo("metros que viaja la luz", _avance,
                        t_final=t_ini + subida + 0.4, paso=0.20, medido=True)

        # Dos extremos y el trazo que los une: la luz sale de uno y para
        # en el otro. Es la MISMA marca de medida del estado anterior, que
        # alli media un tiempo y aqui mide un espacio.
        largo, alto_postes = 5.2, 3.4
        postes = VGroup(_tic(alto_postes, color=APAGADO, grosor=2.0),
                        _tic(alto_postes, color=APAGADO, grosor=2.0))
        postes[0].move_to([-largo / 2, 0, 0])
        postes[1].move_to([largo / 2, 0, 0])
        barra = lz.filete(ancho=largo, color=AMBAR, grosor=7.0)
        etq_4 = rot("UN CICLO")
        etq_4.next_to(barra, DOWN, buff=0.30)
        b4 = VGroup(postes, barra, etq_4)
        L.escena(b4, animacion=AnimationGroup(
            FadeIn(postes, run_time=0.6),
            Succession(Wait(0.35),
                       Create(barra, run_time=subida),
                       FadeIn(etq_4, run_time=0.45)),
            lag_ratio=0.0))
        self.wait(5.6)

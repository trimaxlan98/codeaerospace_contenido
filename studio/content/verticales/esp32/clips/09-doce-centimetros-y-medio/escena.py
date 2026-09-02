# 09 · Doce centimetros y medio
#
# Abre el modulo de la radio. Cuatro estados: la onda de 2.437 GHz sola,
# una longitud de onda marcada de cresta a cresta, el cuarto de onda que
# quiere la antena, y el remate — el cuarto de onda ACORTADO por el
# sustrato, que es lo que de verdad cabe en la esquina de la placa.
#
# Cifras: 2.437 GHz es el centro del canal Wi-Fi (constante publica, no la
# calcula la libreria: etiqueta APAGADA, igual que los 240 MHz del clip
# 01). Los tres largos SI los calcula `chip.longitud_onda` /
# `chip.cuarto_de_onda` durante el render (etiqueta AMBAR). El 2.6 de
# constante dielectrica del FR4 es un valor tipico del sustrato, no una
# medida de la libreria — por eso no lleva cifra propia en pantalla, solo
# se usa como argumento de la funcion que SI calcula el largo.
#
# La marca de longitud es el mismo lenguaje visual del clip 04 (un trazo
# ambar con dos "tics" perpendiculares en los extremos, nunca una flecha):
# aqui se apoya justo sobre la cresta de la onda, asi que se ve DE DONDE
# sale el numero. El paso de una onda a un cuarto de onda es un
# `Transform` entre las dos marcas — misma estructura (trazo + dos tics),
# solo cambia el largo — y la onda de fondo no se toca.
def _tic(largo, color=AMBAR, grosor=4.0):
    """Una rayita corta: el extremo de una medida. `lz.filete` girado."""
    return lz.filete(ancho=largo, color=color, grosor=grosor).rotate(PI / 2)


def _marca(largo, y, x_izq, color=AMBAR):
    """Un trazo horizontal con sus dos tics, apoyado en (x_izq, y)."""
    barra = lz.filete(ancho=largo, color=color, grosor=4.0)
    t1, t2 = _tic(0.30, color=color), _tic(0.30, color=color)
    t1.move_to(barra.get_left())
    t2.move_to(barra.get_right())
    marca = VGroup(barra, t1, t2)
    marca.move_to([x_izq + largo / 2, y, 0])
    return marca


class Clip(Pieza):
    NUMERO = 9

    def pieza(self):
        L = self.L

        F = 2.437e9  # centro del canal Wi-Fi 6, 2.4 GHz — constante publica
        onda_cm = chip.longitud_onda(F) * 100.0
        cuarto_aire_cm = chip.cuarto_de_onda(F) * 100.0
        cuarto_fr4_cm = chip.cuarto_de_onda(F, 2.6) * 100.0

        ANCHO_ONDA, CICLOS, AMPLITUD = 5.5, 3.0, 1.4
        x_izq = -ANCHO_ONDA / 2
        largo_onda = ANCHO_ONDA / CICLOS         # cresta a cresta, en mundo
        largo_cuarto = largo_onda / 4.0

        # --- 1. la onda sola, ocupando el ancho de la franja -------------
        onda = chip.seno(ciclos=CICLOS, ancho=ANCHO_ONDA, amplitud=AMPLITUD,
                         color=TINTA, fase=PI / 2)
        L.escena(onda, animacion=Create(onda, run_time=1.6))
        self.wait(0.8)

        L.dato(f"{F / 1e9:.3f}", "gigahercios del canal", medido=False,
              t=0.6)
        self.wait(4.0)

        # --- 2. una longitud de onda, de cresta a cresta ------------------
        onda2 = chip.seno(ciclos=CICLOS, ancho=ANCHO_ONDA, amplitud=AMPLITUD,
                          color=TINTA, fase=PI / 2)
        marca_onda = _marca(largo_onda, AMPLITUD, x_izq)
        grupo2 = VGroup(onda2, marca_onda)
        L.escena(grupo2, animacion=AnimationGroup(
            FadeIn(onda2, run_time=0.7),
            Create(marca_onda, run_time=1.0), lag_ratio=0.25))
        self.wait(0.6)

        L.dato(medido(onda_cm, 1), "centimetros de onda", medido=True, t=0.6)
        self.wait(4.2)

        # --- 3. el cuarto de onda: el mismo trazo, encogido ---------------
        marca_cuarto = _marca(largo_cuarto, AMPLITUD, x_izq)
        grupo3 = VGroup(onda2, marca_cuarto)
        self.play(Transform(grupo2, grupo3, run_time=1.1))
        self.wait(0.6)

        L.dato(medido(cuarto_aire_cm, 2), "centimetros de antena",
              medido=True, t=0.6)
        self.wait(4.4)

        # --- 4. el remate: eso es lo que cabe en la esquina ---------------
        # La placa llena la franja de verdad (alto ~4.8, un 86 % de BANDA)
        # y el meandro crece con ella, a la MISMA proporcion que antes: el
        # trazo de comparacion sigue midiendo justo el ancho del meandro,
        # asi que "esto, en linea recta, mediria igual" y "y aun asi se
        # dobla en esta esquina" se leen los dos a un tamaño real. La
        # placa va en APAGADO (mobiliario) para que el ambar del meandro y
        # del trazo sean lo unico que llama la atencion en el remate.
        BOARD_ANCHO, BOARD_ALTO = 3.4, 4.8
        ANTENA_ANCHO, ANTENA_ALTO = 1.1, 0.65
        INSET = 0.28

        placa = chip.placa(ancho=BOARD_ANCHO, alto=BOARD_ALTO,
                           color=APAGADO)
        antena = chip.meandro(vueltas=3, ancho=ANTENA_ANCHO,
                              alto=ANTENA_ALTO, color=AMBAR)
        comp = _marca(ANTENA_ANCHO, 0.0, -ANTENA_ANCHO / 2)
        rincon = VGroup(antena, comp).arrange(DOWN, buff=0.20,
                                              aligned_edge=LEFT)
        objetivo = placa.get_corner(UL) + RIGHT * INSET + DOWN * INSET
        rincon.move_to(objetivo, aligned_edge=UL)
        remate = VGroup(placa, rincon)

        L.escena(remate, salida=0.5, animacion=AnimationGroup(
            Create(placa, run_time=1.0),
            FadeIn(rincon, run_time=0.9), lag_ratio=0.30))
        self.wait(0.6)

        L.dato(medido(cuarto_fr4_cm, 2), "centimetros de meandro",
              medido=True, t=0.6)
        self.wait(5.6)

# 07 · CAUSALIDAD — no responde antes del golpe.
#
# La unica pieza del curso que enseña un sistema que NO PUEDE EXISTIR, y
# esa es su gracia: se ve el absurdo sin tener que explicarlo con texto.
#
# El verbo visual: una marca CIAN fija en el eje dice donde cae el golpe
# (la entrada) y se queda ahi los tres planos enteros, porque es la unica
# referencia que hace legible "antes" y "despues" sin una sola palabra
# mas. Plano 2 dibuja `sis.h_no_causal`: una respuesta simetrica que tiene
# muestras a la izquierda de esa marca — se resaltan recoloreando esos
# tallos de APAGADO a AMBAR, para que el ojo vaya derecho al tramo
# imposible. Plano 3 la sustituye por una respuesta causal de verdad
# (`sis.h_amortiguada` con `retardo` puesto exactamente en el golpe): el
# mismo eje, la misma marca, y a la izquierda ya no hay nada que colorear.
#
# ROTULO SOBRE EL COMO: `sis.tallos` no distingue tramos por color; el
# recoleo se hace sobre el VGroup que devuelve, que alterna (Line, Dot)
# una pareja por muestra en el orden en que se construyen. No es un fallo
# de la libreria: es la estructura documentada de lo que `tallos` entrega,
# y aqui se usa tal cual, sin tocarla.
#
# Los dos ejes del eje comun (GOLPE=16, N=48) son los mismos numeros con
# los que el contrato mide la cifra: `sis.muestras_antes_de_cero(hnc, 16)`
# da 16 con estos parametros, y es exactamente lo que se rotula.
class Clip(Pieza):
    NOMBRE = "CAUSALIDAD"
    TESIS = "no responde antes del golpe"

    # Malla y posicion del golpe: PARAMETROS elegidos (etiqueta apagada).
    # Los tres planos comparten N y GOLPE para que la marca del golpe caiga
    # siempre en el mismo sitio del mismo eje.
    N = 48
    GOLPE = 16
    ANCHO_CAJA = ANCHO - 0.5
    ALTO_CAJA = 4.2
    # h_no_causal vive en [0, 1]; la version causal baja hasta -0.6. Un
    # solo rango para las dos, asi no hace falta declarar ningun salto de
    # escala entre planos.
    RANGO_Y = (-0.75, 1.05)

    def _x_de(self, indice):
        """La x de la muestra `indice` sobre el mismo eje que usa
        `sis.tallos` (misma matematica: -ancho/2 + i * ancho/(N-1)), para
        que la marca del golpe caiga exactamente sobre el tallo del golpe."""
        paso = self.ANCHO_CAJA / max(self.N - 1, 1)
        return -self.ANCHO_CAJA / 2 + indice * paso

    def _eje(self):
        """El suelo y la marca del golpe: la referencia que se queda
        encendida en los tres planos."""
        suelo = sis.cero(ancho=self.ANCHO_CAJA, y=-self.ALTO_CAJA / 2,
                         color=LINEA)
        x = self._x_de(self.GOLPE)
        marca = Line([x, -self.ALTO_CAJA / 2 - 0.14, 0],
                     [x, self.ALTO_CAJA / 2 + 0.14, 0],
                     stroke_color=CIAN, stroke_width=2.6)
        return VGroup(suelo, marca)

    def pieza(self):
        L = self.L

        # --- 1. donde cae el golpe, y solo eso -------------------------
        eje1 = self._eje()
        etiqueta_golpe = rot("EL GOLPE", color=CIAN)
        etiqueta_golpe.next_to(eje1, DOWN, buff=0.26)
        L.escena(VGroup(eje1, etiqueta_golpe), t=1.0)
        self.leer(3.4)

        # --- 2. la respuesta imposible: simetrica alrededor del golpe --
        hnc = sis.h_no_causal(N=self.N, centro=self.GOLPE, ancho=5.0)
        tallos_hnc = sis.tallos(hnc, ancho=self.ANCHO_CAJA,
                                alto=self.ALTO_CAJA, color=APAGADO,
                                grosor=2.2, punta=0.05,
                                rango_y=self.RANGO_Y)
        eje2 = self._eje()
        # La etiqueta del resalte se construye YA (apagada a opacidad 0) y
        # entra en el MISMO grupo que encaja `L.escena`: lo que se
        # construye despues de encajar no hereda su escala ni su
        # posicion, asi que aqui no hay "despues".
        etiqueta_antes = rot("ANTES DEL GOLPE", color=AMBAR)
        etiqueta_antes.next_to(eje2, DOWN, buff=0.26)
        etiqueta_antes.set_opacity(0.0)
        # La version resaltada se construye AHORA y entra en el mismo
        # grupo, para que herede la escala y la posicion de `encajar`.
        resaltado = sis.tallos(
            hnc, ancho=self.ANCHO_CAJA, alto=self.ALTO_CAJA, grosor=2.2,
            punta=0.05, rango_y=self.RANGO_Y,
            colores=[AMBAR] * self.GOLPE + [APAGADO] * (self.N - self.GOLPE))
        resaltado.set_opacity(0.0)
        L.escena(VGroup(eje2, tallos_hnc, resaltado, etiqueta_antes), t=1.0)
        self.leer(3.2)

        # Se resalta el tramo ANTES del golpe. El resalte se pide POR
        # MUESTRA (`colores=`), no indexando los hijos del VGroup: contar
        # "dos por muestra, Line y Dot" ata la pieza a la estructura
        # interna de `sis.tallos`, y el dia que alguien dibuje con
        # `punta=0` no hay Dots, la cuenta se desplaza y el color acaba en
        # la muestra equivocada sin que falle nada.
        # Se transforma hacia una COPIA con la opacidad devuelta. Sin la
        # copia, `Transform` se lleva tambien la opacidad 0 del objetivo y
        # el dibujo desaparece: lo hizo, y el fotograma quedaba con el eje
        # y ni un tallo. El objetivo de un Transform tiene que estar vivo
        # aunque no se vea.
        self.play(Transform(tallos_hnc, resaltado.copy().set_opacity(1.0)),
                  etiqueta_antes.animate.set_opacity(1.0), run_time=1.3)
        self.leer(3.4)

        antes = sis.muestras_antes_de_cero(hnc, self.GOLPE)
        L.dato(medido(antes, 0), "muestras antes del golpe", medido=True)
        self.leer(3.6)

        # --- 3. el remate: la misma forma, pero causal de verdad -------
        # `retardo` se pone en GOLPE a proposito: la respuesta empieza
        # exactamente donde esta la marca, y a su izquierda ya no queda
        # nada que resaltar.
        h_causal = sis.h_amortiguada(N=self.N, tau=9.0, f=0.11,
                                     retardo=self.GOLPE)
        tallos_causal = sis.tallos(h_causal, ancho=self.ANCHO_CAJA,
                                   alto=self.ALTO_CAJA, color=AMBAR,
                                   grosor=2.6, punta=0.05,
                                   rango_y=self.RANGO_Y)
        eje3 = self._eje()
        etiqueta_remate = rot("EMPIEZA EN EL GOLPE", color=AMBAR)
        etiqueta_remate.next_to(eje3, DOWN, buff=0.26)
        antes_causal = sis.muestras_antes_de_cero(h_causal, self.GOLPE)

        L.relevo(escena=VGroup(eje3, tallos_causal, etiqueta_remate),
                dato=(medido(antes_causal, 0), "muestras antes del golpe",
                      True), t=1.3, salida=0.5)
        self.leer(3.6)
        self.leer(3.0)

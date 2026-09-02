# 05 · Un pin es un bit
#
# Abre el modulo "tocar el mundo". Escribir en el registro de salida es
# mover fisicamente 32 patas del chip: el registro cambia de valor un par
# de veces (mismo tamaño de estructura, se releva con Transform en vez de
# ir y venir por el carril). Luego zoom conceptual a UN pin: la curva de
# carga de su pad contra una carga de 100 pF, y lo que pasa si el cable
# tiene mas capacidad.
#
# Cifras: HOJA["gpio"] son los 34 pines fisicos (hoja de datos, gris).
# chip.combinaciones(32) son los estados que caben en el registro entero.
# chip.flanco_rc mide el tiempo de subida 10-90% SOBRE LA CURVA que se
# dibuja, no por formula aparte. Las dos capacidades comparten el MISMO
# eje de tiempo (el de la carga mas lenta) para que "el flanco se estira"
# se vea en el dibujo y no solo se lea en la cifra.
class Clip(Pieza):
    NUMERO = 5

    def pieza(self):
        L = self.L

        BITS_LADO, BITS_BUFF = 0.66, 0.14

        def registro(valor):
            m = chip.bits(valor, n=32, por_fila=8,
                          lado=BITS_LADO, buff=BITS_BUFF)
            lz.encajar(m, que="registro")
            return m

        # --- el registro cambia: mover 32 patas -------------------------
        reg = registro(0xA5000000)
        L.escena(reg, animacion=Create(reg, run_time=1.3))
        L.dato(chip.HOJA["gpio"], "pines que tocan el mundo", medido=False)
        self.wait(3.4)

        reg2 = registro(0x0000FFFF)
        self.play(Transform(reg, reg2, run_time=0.8))
        self.wait(3.6)

        reg3 = registro(0x12345678)
        self.play(Transform(reg, reg3, run_time=0.8))
        self.wait(3.6)

        # --- cuantos valores caben en el registro entero -----------------
        L.dato(lz.miles(chip.combinaciones(32)), "estados posibles",
              medido=True)
        self.wait(4.6)

        # --- zoom a un pin: lo que tarda en subir -------------------------
        R = chip.HOJA["z_salida_ohm"]
        C1, C2 = 100e-12, 470e-12
        t_comun = np.linspace(0.0, 8.0 * R * C2, 2001)
        t1, v1, tsub1 = chip.flanco_rc(C=C1, t=t_comun)

        caja_ancho, caja_alto = 5.2, 3.8
        eje1 = chip.eje_ele(ancho=caja_ancho, alto=caja_alto)
        curva1, punto1 = chip.traza(t1, v1, ancho=caja_ancho, alto=caja_alto,
                                    rango_y=(0.0, chip.HOJA["vdd"]))
        n10 = chip.nivel(0.10 * chip.HOJA["vdd"], punto1, ancho=caja_ancho)
        n90 = chip.nivel(0.90 * chip.HOJA["vdd"], punto1, ancho=caja_ancho)
        etiqueta_pin = rot("UN PIN")
        caja1 = VGroup(eje1, n10, n90, curva1)
        etiqueta_pin.next_to(caja1, UP, buff=0.28)
        vista1 = VGroup(caja1, etiqueta_pin)

        L.escena(vista1, animacion=Create(vista1, run_time=1.5))
        L.dato(medido(tsub1 * 1e9, 2), "nanosegundos de subida", medido=True)
        self.wait(4.8)

        # --- con mas capacidad, el mismo flanco se estira ------------------
        t2, v2, tsub2 = chip.flanco_rc(C=C2, t=t_comun)
        curva1b, _ = chip.traza(t1, v1, ancho=caja_ancho, alto=caja_alto,
                                rango_y=(0.0, chip.HOJA["vdd"]), color=TINTA)
        curva2, _ = chip.traza(t2, v2, ancho=caja_ancho, alto=caja_alto,
                               rango_y=(0.0, chip.HOJA["vdd"]), color=CIAN)
        eje2 = chip.eje_ele(ancho=caja_ancho, alto=caja_alto)
        caja2 = VGroup(eje2, curva1b, curva2)
        rot1 = rot("POCA CARGA", color=TINTA)
        rot2 = rot("MUCHA CARGA", color=CIAN)
        rot1.move_to(caja2.get_top() + UP * 0.35 + LEFT * 1.7)
        rot2.move_to(caja2.get_top() + UP * 0.35 + RIGHT * 1.3)
        vista2 = VGroup(caja2, rot1, rot2)

        L.escena(vista2, animacion=FadeIn(vista2, run_time=1.0))
        L.dato(medido(tsub2 * 1e9, 2), "nanosegundos con mas carga",
              medido=True)
        self.wait(4.4)

# 13 · El planificador
#
# Una tarea periodica que tiene que despertar cada 10 ms. Sola en su
# nucleo despierta cuando debe; con un acaparador de la misma prioridad al
# lado, el planificador solo se la devuelve en el tick y cada despertar
# llega tarde una cantidad DISTINTA. Eso es el jitter.
#
# Honestidad del clip: `chip.planificar` NO modela el anclaje a un nucleo.
# Modela "con acaparador al lado" (acaparador_ms=4) y "sin acaparador"
# (acaparador_ms=0). El remate — la tarea anclada al segundo nucleo — ES
# el caso sin acaparador: el otro nucleo esta libre, asi que nadie compite
# por la CPU. No hay un tercer escenario ni una cifra que la libreria no
# calcule.
#
# Cifras: las dos desviaciones tipicas salen de `planificar` sobre los
# MISMOS 12 despertares que se dibujan (la ventana es la muestra), y la
# razon entre ellas se divide aqui. Solo el periodo (10 ms, el parametro
# de la simulacion) y los 2 nucleos (HOJA de Espressif) van en gris.
class Clip(Pieza):
    NUMERO = 13

    # --- el cronograma ------------------------------------------------
    # Dos renglones sobre la misma escala de tiempo: arriba los
    # despertares, abajo el retraso de cada uno respecto de su instante
    # ideal, ampliado (0.5 unidades por milisegundo). Las dos reglas
    # sostienen la composicion, asi que el dibujo mide lo mismo en los
    # cuatro estados y las marcas no saltan de sitio al relevarse: lo que
    # cambia entre un estado y otro es exactamente lo que hay que ver.
    ANCHO_T = 5.2          # ancho del renglon de tiempo
    T_MAX = 120.0          # ms de la ventana dibujada (12 periodos)
    N = 12                 # despertares simulados = despertares dibujados
    PERIODO_MS = 10.0
    ESCALA_RET = 0.5       # unidades de mundo por milisegundo de retraso
    Y_RETRASO = -1.90      # base de las rayitas ambar
    Y_TIEMPO = 0.65        # linea de tiempo
    ALTO_MARCA = 1.50

    def crono(self, instantes, retrasos, nucleo):
        grupo = VGroup(
            lz.regla(self.Y_TIEMPO, ancho=self.ANCHO_T, grosor=2.0),
            lz.regla(self.Y_RETRASO, ancho=self.ANCHO_T, grosor=2.0),
            chip.marcas_tiempo(instantes, y=self.Y_TIEMPO + self.ALTO_MARCA / 2,
                               ancho=self.ANCHO_T, alto=self.ALTO_MARCA,
                               t_max=self.T_MAX, color=TINTA))
        # Una rayita por retraso, a la misma escala en todos los estados.
        # Las que no llegan a media decima de unidad no se dibujan: a 6.9
        # microsegundos la barra medirla 0.003 unidades, o sea nada. El
        # renglon vacio es el dato, no un olvido.
        barras = VGroup()
        for t, d in zip(instantes, retrasos):
            largo = float(d) * self.ESCALA_RET
            if largo < 0.05:
                continue
            barras.add(chip.marcas_tiempo(
                [t], y=self.Y_RETRASO + largo / 2, ancho=self.ANCHO_T,
                alto=largo, t_max=self.T_MAX, color=AMBAR, grosor=2.6))
        if len(barras):
            grupo.add(barras)
        etiqueta = rot(nucleo)
        etiqueta.move_to([-self.ANCHO_T / 2 + etiqueta.width / 2,
                          self.Y_TIEMPO + self.ALTO_MARCA + 0.30, 0])
        grupo.add(etiqueta)
        return grupo

    def pieza(self):
        L = self.L
        ideal = np.arange(self.N) * self.PERIODO_MS
        sola, j_sola = chip.planificar(
            periodo_ms=self.PERIODO_MS, ejecucion_ms=1.0, tick_ms=1.0,
            acaparador_ms=0.0, n=self.N)
        con, j_con = chip.planificar(
            periodo_ms=self.PERIODO_MS, ejecucion_ms=1.0, tick_ms=1.0,
            acaparador_ms=4.0, n=self.N)

        # --- la tarea sola: doce despertares, doce huecos iguales ------
        limpio = self.crono(sola, sola - ideal, "NUCLEO 0")
        L.escena(limpio, animacion=Create(limpio, run_time=1.8))
        self.wait(0.8)
        L.dato(medido(self.PERIODO_MS, 0), "milisegundos de periodo",
               medido=False, t=0.6)
        self.wait(4.2)

        # --- y lo puntual que es, medido sobre esos doce ---------------
        L.dato(medido(j_sola * 1000.0, 1), "microsegundos de jitter", t=0.6)
        self.wait(5.0)

        # --- entra el acaparador --------------------------------------
        # Dibujo y cifra se relevan en el MISMO movimiento: dejar un
        # segundo las marcas nuevas con el jitter viejo debajo seria una
        # cifra que no corresponde a lo que se esta enseñando.
        sucio = self.crono(con, con - ideal, "NUCLEO 0")
        L.relevo(escena=sucio,
                 dato=lz.dato(medido(j_con, 2), "milisegundos de jitter"),
                 t=0.9)
        self.wait(5.6)

        # --- el remate: el segundo nucleo estaba libre -----------------
        # Anclada al otro nucleo no compite con nadie, que es exactamente
        # el caso simulado sin acaparador.
        anclada = self.crono(sola, sola - ideal, "NUCLEO 1")
        L.relevo(escena=anclada,
                 dato=lz.dato(chip.HOJA["nucleos"], "nucleos en el chip",
                              medido=False),
                 t=0.9)
        self.wait(5.0)

        # --- lo que cuesta no usarlo ----------------------------------
        L.dato(medido(j_con / j_sola, 0), "veces menos jitter", t=0.6)
        self.wait(5.6)

# 02 · Dos nucleos
#
# Doce tareas independientes, el mismo lote en dos repartos: UN nucleo
# (secuencial) y DOS (greedy LPT, la libreria escoge la tarea mas larga
# para el nucleo que antes queda libre). Las barras estan a la MISMA
# escala de tiempo en los dos casos -- la escala se calcula sobre el
# reparto de un nucleo (el que llega mas lejos) y se reutiliza en el de
# dos, asi el makespan se ve en el ancho del dibujo, no se rotula aparte.
#
# Barras bajas y apoyadas en el suelo de la franja (anclaje="abajo"),
# junto a la cifra: es un diagrama ancho y bajo, no un bloque que llena
# la franja a base de estirar el alto de cada barra.
class Clip(Pieza):
    NUMERO = 2

    def pieza(self):
        L = self.L
        d = chip.tareas()

        # --- un nucleo: las doce, una detras de otra --------------------
        asig1, ini1, carga1, mk1 = chip.reparto(d, 1)
        gt1, escala = chip.gantt(d, asig1, ini1, ancho=5.5, alto_barra=2.60)
        L.escena(gt1, animacion=Create(gt1, lag_ratio=0.05, run_time=1.4),
                anclaje="abajo")
        L.dato(medido(mk1, 1), "milisegundos", medido=True, t=0.6)
        self.wait(6.0)

        # --- dos nucleos: el reparto greedy LPT --------------------------
        # Misma escala que arriba: por eso esta fila llega solo a la mitad.
        # El relevo de escena y el de dato van en un UNICO play: si van
        # secuenciales, la fila partida se ve unos segundos con el
        # makespan de un nucleo debajo, que es mentir con la cifra.
        asig2, ini2, carga2, mk2 = chip.reparto(d, 2)
        gt2, _ = chip.gantt(d, asig2, ini2, ancho=5.5, alto_barra=1.15,
                           buff=0.30, escala=escala)
        et0 = rot("NUCLEO 0", color=AMBAR)
        et0.next_to(gt2[0], UP, buff=0.22)
        et1 = rot("NUCLEO 1", color=CIAN)
        et1.next_to(gt2[1], DOWN, buff=0.22)
        grupo2 = VGroup(gt2, et0, et1)
        lz.encajar(grupo2, anclaje="abajo")
        dato2 = lz.dato(medido(mk2, 1), "milisegundos", medido=True)
        viejo_escena = L.ocupantes["escena"]
        viejo_dato = L.ocupantes["dato"]
        L.ocupantes["escena"] = grupo2
        L.ocupantes["dato"] = dato2
        self.play(FadeOut(viejo_escena, run_time=0.8),
                 FadeOut(viejo_dato, run_time=0.8),
                 FadeIn(grupo2, run_time=0.8),
                 FadeIn(dato2, run_time=0.8))
        self.wait(6.4)

        # --- el remate: cuanto se gana repartiendo ------------------------
        ganancia = chip.aceleracion(d, 2)
        L.dato(f"x{medido(ganancia, 2)}", "veces mas rapido", medido=True,
              t=0.6)
        self.wait(6.4)

        # --- el limite que no se toca (teoria, no medida aqui) -------------
        L.dato("2", "limite teorico", medido=False, t=0.6)
        self.wait(5.8)

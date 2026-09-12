# 03 · LA ELIPTICA — el pendulo real, medido.
#
# La formula del periodo que se enseña en el instituto, T = 2·pi·raiz(L/g),
# es FALSA. Solo vale en el limite de amplitud cero. El periodo de verdad
# depende de la amplitud, y para escribirlo hizo falta una funcion nueva:
# la integral eliptica completa K, que no se calcula con una formula sino
# con un LIMITE (la media aritmetico-geometrica). A 90 grados el pendulo
# real tarda un 18.03 % mas de lo que promete el libro.
#
# El verbo visual: dos pendulos sueltos EN EL MISMO INSTANTE, uno a 10
# grados y otro a 90, colgados DEL MISMO punto. Empiezan juntos y se van
# descolgando a la vista. No hace falta decir nada.
#
# Tres cosas que decidieron la pieza:
#
#   - **Un solo pivote, no dos.** Con dos pendulos separados hay que mirar
#     dos sitios a la vez para ver un desfase; colgados del mismo punto, el
#     desfase es que uno esta a la izquierda cuando el otro esta a la
#     derecha, y eso se ve sin comparar nada.
#   - **El tiempo de video ES el tiempo de la fisica.** El updater lee el
#     reloj de la escena e interpola sobre una trayectoria integrada con
#     RK4 sin aproximar el seno. Un segundo de reel es un segundo de
#     pendulo: si se acelerara, el desfase que se ve no seria el que dice
#     la cifra.
#   - **Los updaters se quitan antes de relevar el dibujo.** `leer()` es un
#     `wait`, y durante un wait los updaters siguen corriendo: sin
#     `clear_updaters` los pendulos seguirian moviendose mientras se apagan.
class Clip(Pieza):
    # "ELIPTICA K" y no "LA ELIPTICA": lo destapo la hoja de contactos
    # de las veinte portadas al cerrar el curso. Diecisiete llevan el
    # nombre pelado —GAMMA, FRESNEL, BESSEL, CANTOR— y esta era la unica
    # con articulo. Ver las veinte juntas hace visible una incoherencia
    # que pieza a pieza no lo es. Y de paso nombra la funcion de verdad:
    # la integral eliptica COMPLETA de primera especie, K.
    NOMBRE = "ELIPTICA K"
    TESIS = "el pendulo real, medido"

    # PARAMETROS elegidos: las dos amplitudes y el largo del dibujo. La
    # cifra no depende del largo (el periodo va con raiz de L, y la RAZON
    # entre los dos periodos no lleva L ni g).
    ANG_A = 10.0
    ANG_B = 90.0
    LARGO = 2.78
    BALANCEO_1 = 6.0
    BALANCEO_2 = 5.5

    def pieza(self):
        L = self.L
        total = self.BALANCEO_1 + self.BALANCEO_2 + 4.0
        ts, th_a = esp.pendulo(self.ANG_A, T=total, dt=0.002)
        _, th_b = esp.pendulo(self.ANG_B, T=total, dt=0.002)

        # --- los dos pendulos, del mismo pivote -----------------------
        pa = esp.Pendulo(largo=self.LARGO, color=CIAN, radio=0.115)
        pb = esp.Pendulo(largo=self.LARGO, color=AMBAR, radio=0.135)
        pa.colocar(np.radians(self.ANG_A))
        pb.colocar(np.radians(self.ANG_B))

        vertical = DashedVMobject(
            Line([0, 0, 0], [0, -self.LARGO - 0.18, 0],
                 stroke_color=LINEA, stroke_width=esp.TRAZO_PELO),
            num_dashes=16)
        # El arco del recorrido. No es adorno: sin el, el grupo que entra
        # en escena es ASIMETRICO (a t=0 el de 90 grados asoma entero por
        # la derecha y el de 10 apenas por la izquierda), `encajar` centra
        # esa caja torcida y el pivote queda descentrado — con lo que el
        # balanceo, que si es simetrico, se ve caer hacia un lado. El arco
        # centra el grupo y ademas enseña por donde van a pasar.
        arco = DashedVMobject(
            Arc(radius=self.LARGO, start_angle=-PI, angle=PI,
                stroke_color=LINEA, stroke_width=esp.TRAZO_PELO),
            num_dashes=48)

        rot_a = rot(f"{self.ANG_A:.0f} GRADOS", color=CIAN)
        rot_b = rot(f"{self.ANG_B:.0f} GRADOS", color=AMBAR)
        # El largo sale de la ZONA SEGURA, no de la estetica: el pendulo
        # de 90 grados barre su largo a cada lado, asi que 2.78 da 5.56 de
        # barrido y la zona segura son 5.76. `cabe` solo mide el grupo
        # cuando entra —quieto y estrecho—, de modo que un largo mayor
        # pasaria el guardian y el bordon se meteria en la columna de
        # botones de Instagram justo en el punto mas alto del recorrido.
        rot_a.move_to([-1.32, 0.52, 0])
        rot_b.move_to([1.32, 0.52, 0])

        dibujo = lz.agrupar(arco, vertical, rot_a, rot_b, pa, pb)
        L.escena(dibujo, t=0.9)
        self.leer(2.4)

        # --- se sueltan los dos a la vez -------------------------------
        t0 = self.renderer.time

        def seguir(pend, angulos):
            def _tic(mob, dt):
                t = self.renderer.time - t0
                mob.colocar(float(np.interp(t, ts, angulos)))
            pend.add_updater(_tic)

        seguir(pa, th_a)
        seguir(pb, th_b)
        self.wait(self.BALANCEO_1)

        # --- lo que promete el libro ----------------------------------
        L.dato(medido(esp.periodo_pequeno(), 4),
               "segundos, dice el libro")
        self.leer(1.8)
        self.wait(self.BALANCEO_2)

        # --- lo que tarda de verdad el de noventa ---------------------
        L.dato(medido(esp.periodo_pendulo(self.ANG_B), 4),
               "segundos, el de 90")
        self.leer(2.2)
        for p in (pa, pb):
            p.clear_updaters()

        # --- el desfase, dibujado -------------------------------------
        # Los dos angulos van DIVIDIDOS por su amplitud. Es una
        # exageracion de escala —el de 10 grados se agranda nueve veces—
        # y por eso el rotulo lo declara: lo que se compara aqui es la
        # FASE, no el tamaño.
        P = esp.marco((0.0, total), (-1.12, 1.12), ancho=ANCHO - 0.60,
                      alto=3.9)
        traza_a = esp.curva(ts, th_a / np.radians(self.ANG_A), P,
                            color=CIAN, grosor=esp.TRAZO_FINO)
        traza_b = esp.curva(ts, th_b / np.radians(self.ANG_B), P,
                            color=AMBAR, grosor=esp.TRAZO)
        eti = rot("ANGULO RELATIVO", color=APAGADO)
        eti.next_to(P(total / 2, -1.12), DOWN, buff=0.22)
        panel = lz.agrupar(esp.eje_x(P), traza_a, traza_b, eti)

        L.relevo(escena=panel,
                 dato=(medido(esp.exceso_de_periodo(self.ANG_B), 2),
                       "por ciento mas lento"), t=0.9)
        self.leer(3.4)

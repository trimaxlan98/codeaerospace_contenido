# 16 · Radon — ver dentro sin abrir.
#
# Es un TAC, y por eso es la transformada mas facil de contar sin palabras
# de todo el curso: un objeto opaco, sombras tomadas desde muchos angulos,
# y el interior que aparece.
#
# La decision que ordena la pieza: el objeto NO se enseña por dentro hasta
# el final. Al principio solo esta su silueta —lo unico que se ve de fuera—
# y lo que hay dentro solo aparece cuando lo trae la reconstruccion. Si el
# fantasma se enseñara en el primer plano, la reconstruccion final seria un
# "sale lo mismo que ya viste" en vez de un "asi es como se ve dentro".
# Por eso la silueta va en APAGADO (un objeto mate, sin informacion) y las
# reconstrucciones en TINTA: el color mismo cuenta que ahi hay algo nuevo.
#
# Cuatro cosas que costaron una vuelta o que habrian costado una:
#
#   - EL SINOGRAMA SE DESTAPA, NO SE RECALCULA. `tf.mapa` normaliza de min
#     a max de la matriz que le des, asi que pintar el sinograma a medio
#     llenar (columnas futuras a cero) le cambia el contraste en cada
#     fotograma y la imagen parpadea mientras crece. Aqui se pinta ENTERO
#     una sola vez y se tapa con un rectangulo del color del fondo que se
#     encoge hacia la derecha. Lo que se ve es exactamente el sinograma
#     final, columna a columna, sin renormalizar nada.
#   - Y LA TAPA ENTRA ANTES QUE LA IMAGEN. Si el sinograma entrara con el
#     grupo, durante el fundido de entrada la tapa esta a media opacidad y
#     deja ver un fantasma de las 180 columnas que luego desaparece. La
#     imagen entra a opacidad 0 (la tapa, azul sobre azul, es invisible) y
#     se enciende ya tapada, justo antes del barrido.
#   - EL HAZ SE GIRA, no se sustituye. `become` sobre un estado construido
#     antes de `L.escena` lo devolveria a su tamaño y su sitio originales.
#     `Rotate` opera sobre el mobject ya colocado y no toca la escala.
#   - EL HUECO ENTRE LOS DOS PANELES ES EL DEL HAZ GIRADO, no el del haz
#     quieto: un haz de 2.10 de largo y 0.92 de radio barre un circulo de
#     1.40, o sea 0.35 mas que el borde del objeto. Con el hueco medido en
#     horizontal, a 45 grados los rayos se metian sobre el sinograma.
#   - LOS `leer` ESTAN AJUSTADOS AL MUESTREO. `render_vertical.py` saca los
#     frames de revision a duracion*(i+0.5)/9, o sea uno cada 4.4 s, y con
#     seis planos de 4.1-4.4 s el muestreo se queda ENGANCHADO a las
#     transiciones: la primera version dejaba tres de los nueve frames a
#     media opacidad y ningun frame de tres de los planos. Subir las
#     esperas a 3.0-3.5 (todas muy por encima del minimo de 1.8) rompe esa
#     coincidencia y cada plano se lleva su frame.
#
# Honestidad de las cifras: los dos errores los mide
# `tf.error_reconstruccion` en este render (ambar). El numero de angulos y
# el lado de 96 pixeles son parametros ELEGIDOS, y van en gris.
class Clip(Pieza):
    NOMBRE = "RADON"
    TESIS = "ver dentro sin abrir"

    N = 96                     # lado del objeto, en pixeles: ELEGIDO
    ANGULOS = 180              # el barrido completo: ELEGIDO
    POCOS = 8                  # el barrido pobre, el de las rayas: ELEGIDO
    GAMMA = 0.7                # el MISMO para las tres imagenes del objeto
    LADO = 3.60                # y el MISMO cuadro: la silueta opaca del
                               # principio y las dos reconstrucciones ocupan
                               # el mismo sitio y el mismo tamaño, para que
                               # el remate se lea como una SUSTITUCION y no
                               # como otro dibujo distinto
    BARRIDO = 7.0              # lo que dura la vuelta del haz

    def _angulos(self, cuantos):
        return np.linspace(0.0, 180.0, int(cuantos), endpoint=False)

    def pieza(self):
        L = self.L

        # --- todo lo caro, UNA vez y fuera de las animaciones ----------
        # `radon` con 180 angulos son 180 rotaciones bilineales, y
        # `error_reconstruccion` hace esas 180 dos veces. Medido en el
        # contenedor: 0.7 s las seis cosas juntas. Dentro de un `play`
        # serian 0.7 s POR FOTOGRAMA.
        img = tf.fantasma(self.N)
        silueta = (img > 0).astype(float)          # lo unico que se ve fuera
        a_muchos = self._angulos(self.ANGULOS)
        a_pocos = self._angulos(self.POCOS)
        sino = tf.radon(img, a_muchos)
        # La parte positiva, como en la pieza 13: la retroproyeccion filtrada
        # deja un halo negativo alrededor del objeto, y normalizar de min a
        # max pondria el CERO en un gris medio — el cuadro entero se
        # recortaria contra el azul como una foto pegada encima. Con la
        # parte positiva el cero ES el fondo y la imagen no lleva marco.
        rec_muchos = np.maximum(
            tf.retroproyeccion(sino, a_muchos, n=self.N), 0.0)
        rec_pocos = np.maximum(
            tf.retroproyeccion(tf.radon(img, a_pocos), a_pocos, n=self.N), 0.0)
        err_pocos = tf.error_reconstruccion(self.POCOS, n=self.N) * 100.0
        err_muchos = tf.error_reconstruccion(self.ANGULOS, n=self.N) * 100.0

        # --- 1. un objeto opaco ---------------------------------------
        # El unico plano de la pieza SIN cifra debajo, y es a proposito:
        # todavia no se ha medido nada. El carril se llena en cuanto la
        # maquina empieza a contar angulos y ya no se vacia.
        opaco = tf.mapa(silueta, alto=self.LADO, color_alto=APAGADO)
        r1 = rot("el objeto")
        r1.next_to(opaco, UP, buff=0.30)
        L.escena(Group(opaco, r1), t=0.9)
        self.leer(3.0)

        # --- 2. las sombras, desde todos los angulos ------------------
        # El haz arranca VERTICAL porque la columna 0 del sinograma es la
        # suma por columnas de la imagen sin girar, o sea la integral a lo
        # largo de rayos verticales. `haz_rayos(0)` los dibuja
        # horizontales, asi que el primer angulo dibujado es el 90.
        chico = tf.mapa(silueta, alto=2.10, color_alto=APAGADO)
        haz = tf.haz_rayos(90.0, radio=0.92, cuantos=11, largo=2.10,
                           color=AMBAR)
        # `haz_rayos` fija el trazo a TRAZO_PELO al 70 %: sobre el gris del
        # objeto y en un render de validacion a lado corto 540 eso es medio
        # pixel y no se ve. Se le sube el trazo al mobject ya construido.
        haz.set_stroke(width=tf.TRAZO_FINO, opacity=0.9)
        sombras = tf.mapa(sino, ancho=4.60)
        sombras.next_to(chico, DOWN, buff=0.75)
        sombras.set_opacity(0.0)
        tapa = Rectangle(width=sombras.width + 0.04,
                         height=sombras.height + 0.06,
                         stroke_width=0.0, fill_color=AZUL, fill_opacity=1.0)
        tapa.move_to(sombras)
        tapa.set_z_index(10)
        L.relevo(escena=Group(chico, haz, sombras, tapa), t=0.8, salida=0.45)

        # Ya colocado el grupo (y por tanto con su escala definitiva), se
        # miden los bordes de la tapa: el destape es una interpolacion
        # entre numeros de ESTE sistema de coordenadas, no del original.
        sombras.set_opacity(1.0)
        borde = tapa.get_right()[0]
        ancho_tapa = tapa.width
        alto_tapa = tapa.get_center()[1]

        def _destapar(mob, alpha):
            w = max(ancho_tapa * (1.0 - alpha), 1e-3)
            mob.stretch_to_fit_width(w)
            mob.move_to([borde - w / 2.0, alto_tapa, 0])

        # El contador lee el reloj ABSOLUTO de la escena, asi que el
        # arranque hay que decirselo en ese mismo reloj: ahora mismo mas el
        # fundido de entrada que el propio contador se gasta.
        arranque = self.renderer.time + 0.6
        L.contador_vivo(
            "angulos medidos",
            lambda t: int(np.clip((t - arranque) / self.BARRIDO, 0.0, 1.0)
                          * self.ANGULOS),
            t_final=arranque + self.BARRIDO, paso=0.25, medido=False, t=0.6)
        # `linear` en los tres a la vez: el haz gira, el sinograma se
        # destapa y la cuenta sube al mismo ritmo. Con `smooth` el numero
        # (que si es lineal en el tiempo) dejaria de corresponder a las
        # columnas que hay pintadas.
        self.play(Rotate(haz, angle=PI, about_point=haz.get_center()),
                  UpdateFromAlphaFunc(tapa, _destapar),
                  run_time=self.BARRIDO, rate_func=linear)
        self.leer(3.0)
        L.parar_contadores()

        # --- 3. eso es lo que mide la maquina -------------------------
        grande = tf.mapa(sino, ancho=5.40)
        r3 = rot("el sinograma")
        r3.next_to(grande, UP, buff=0.30)
        L.relevo(escena=Group(grande, r3), t=0.85, salida=0.45)
        self.leer(3.2)

        # --- 4. con ocho angulos, rayas -------------------------------
        pobre = tf.mapa(rec_pocos, alto=self.LADO, gamma=self.GAMMA)
        r4 = rot(f"{self.POCOS} angulos")
        r4.next_to(pobre, UP, buff=0.30)
        L.relevo(escena=Group(pobre, r4),
                 dato=(medido(err_pocos, 1), "por ciento de error"),
                 t=0.85, salida=0.45)
        self.leer(3.1)

        # --- 5. con ciento ochenta, el interior -----------------------
        bueno = tf.mapa(rec_muchos, alto=self.LADO, gamma=self.GAMMA)
        r5 = rot(f"{self.ANGULOS} angulos")
        r5.next_to(bueno, UP, buff=0.30)
        L.relevo(escena=Group(bueno, r5),
                 dato=(medido(err_muchos, 2), "por ciento de error"),
                 t=0.85, salida=0.45)
        self.leer(3.3)

        # --- 6. la comprobacion ---------------------------------------
        # Los dos cuadros con el MISMO gamma y el mismo lado: comparar dos
        # imagenes reveladas de distinta manera no demuestra nada. La cifra
        # de abajo no cambia porque es exactamente la distancia entre estos
        # dos cuadros. (No se puede usar `lz.dos_dominios`: monta los
        # paneles en VGroup y un mapa es un ImageMobject.)
        panel_rec = Group(rot("reconstruido", color=AMBAR),
                          tf.mapa(rec_muchos, alto=2.05, gamma=self.GAMMA))
        panel_obj = Group(rot("el objeto"),
                          tf.mapa(img, alto=2.05, gamma=self.GAMMA))
        for p in (panel_rec, panel_obj):
            p.arrange(DOWN, buff=0.22)
        L.relevo(escena=Group(panel_rec, panel_obj).arrange(DOWN, buff=0.45),
                 t=0.9, salida=0.45)
        self.leer(3.5)

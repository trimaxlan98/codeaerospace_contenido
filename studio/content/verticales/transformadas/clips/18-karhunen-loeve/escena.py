# 18 · Karhunen-Loeve — una base a la medida.
#
# El verbo visual: una nube de puntos alargada y torcida, con dos ejes que
# EMPIEZAN horizontal y vertical (la base "de fabrica", que no sabe nada
# de la nube) y GIRAN hasta quedar a lo largo de ella. Nadie les dice el
# angulo: lo dicta la propia nube, via su covarianza (`tf.base_kl`).
#
# Es la ULTIMA pieza de contenido y cierra el curso entero: las diecisiete
# anteriores usan bases FIJAS, elegidas antes de ver la señal (senos,
# cuadradas, ondulas...). Esta se la inventa la señal misma, y por eso el
# arco termina con la nube proyectada sobre su propio eje: casi nada se
# pierde, y la base que lo consigue no la eligio nadie.
#
# Honestidad, sin disimular: la nube se construye girando 28 grados
# (parametro ELEGIDO, gris — `GIRO`) y la base que MIDE `tf.base_kl` sobre
# esos 220 puntos da 27.75 (ambar). No es el mismo numero porque una
# muestra finita no es la poblacion entera: es lo que pasa al medir de
# verdad, y enseñar los dos hace la pieza mas honesta, no menos.
#
# Trampa evitada (la que avisa el contrato): `tf.nube` escala x e y por
# separado para llenar su caja, asi que un angulo dibujado dentro de una
# caja no cuadrada MIENTE aunque el numero de abajo sea correcto. Por eso
# el rango de datos es simetrico en los dos ejes (`RANGO`, +-R) y la caja
# es cuadrada (`SIDE` x `SIDE`): el angulo que se VE es el angulo que hay.
#
# Los dos ejes se construyen ANTES de que `L.relevo` los encaje (trampa 3
# del contrato) y se guardan en variables: la rotacion de la pieza 3 y el
# giro final no reconstruyen nada, animan esos MISMOS mobjects ya
# escalados y colocados.
class Clip(Pieza):
    NOMBRE = "KARHUNEN-LOEVE"
    TESIS = "una base a la medida"

    N = 220
    GIRO = 28.0            # el giro con el que se CONSTRUYE la nube: dado
    R = 3.0                # rango de datos, IGUAL en x e y (la trampa)
    SIDE = 5.2             # caja de la nube: cuadrada
    EJE_LARGO = 5.0

    def _nube(self, puntos, color=APAGADO):
        return tf.nube(puntos, ancho=self.SIDE, alto=self.SIDE,
                       color=color,
                       rango=((-self.R, self.R), (-self.R, self.R)))

    def pieza(self):
        L = self.L
        puntos = tf.nube_correlada(self.N, giro=self.GIRO)
        _, vec, angulo = tf.base_kl(puntos)
        varianza = tf.varianza_explicada(puntos, 1)

        # --- 1. la nube: 220 puntos, y nada mas ------------------------
        nube1, _ = self._nube(puntos)
        r1 = rot(f"{puntos.shape[0]} puntos", color=APAGADO)
        r1.next_to(nube1, UP, buff=0.28)
        L.escena(VGroup(nube1, r1), t=0.9)
        self.leer(4.0)

        # --- 2. los ejes de fabrica: no dicen nada de ella --------------
        nube2, _ = self._nube(puntos)
        eje_h = tf.eje_propio(0.0, largo=self.EJE_LARGO, color=APAGADO)
        eje_v = tf.eje_propio(90.0, largo=self.EJE_LARGO, color=APAGADO)
        ejes = VGroup(eje_h, eje_v)
        r2 = rot("los ejes de siempre", color=APAGADO)
        r2.next_to(VGroup(nube2, ejes), UP, buff=0.28)
        L.relevo(escena=VGroup(nube2, ejes, r2),
                 dato=(medido(self.GIRO, 1), "giro de fabrica", False),
                 t=0.7, salida=0.4)
        self.leer(3.8)

        # --- 3. giran hasta el angulo que dicta la nube -----------------
        r3 = rot("encuentra su angulo", color=AMBAR)
        r3.move_to(r2)
        centro = ejes.get_center()
        self.play(FadeOut(r2, run_time=0.4), FadeIn(r3, run_time=0.4))
        # `Rotate` sobre `ejes` y `.animate.set_color` sobre sus HIJOS
        # (eje_h, eje_v) en el MISMO play se pelean por los puntos cada
        # fotograma: las dos animaciones interpolan `eje_h`/`eje_v` y la
        # que se aplica despues en el bucle interno de manim GANA para
        # ese fotograma. El color se veia bien pero el giro se deshacia
        # solo cada frame y los ejes quedaban horizontales y verticales
        # para siempre, con la cifra ya diciendo "27.75 grados medidos".
        # Separar en dos `play` secuenciales lo evita.
        self.play(Rotate(ejes, angle=np.deg2rad(angulo), about_point=centro),
                  run_time=1.8, rate_func=smooth)
        self.play(eje_h.animate.set_color(AMBAR),
                  eje_v.animate.set_color(AMBAR), run_time=0.4)
        self.leer(3.6)

        L.relevo(dato=(medido(angulo, 2), "grados medidos", True),
                 t=0.6, salida=0.4)
        self.leer(3.6)

        # --- 4. con una sola direccion se guarda casi todo --------------
        L.relevo(dato=(medido(varianza * 100.0, 2), "de la varianza", True),
                 t=0.7, salida=0.45)
        self.leer(3.8)

        # --- 5. el remate: la nube aplastada sobre su eje largo ----------
        # Proyeccion sobre la primera componente (la de mas varianza):
        # cada punto se sustituye por su sombra en esa direccion. Si casi
        # no se pierde nada, la sombra tiene que parecerse a la nube.
        centro_datos = puntos.mean(axis=0)
        v1 = vec[:, 0]
        escalar = (puntos - centro_datos) @ v1
        proyectados = np.outer(escalar, v1) + centro_datos

        nube3, _ = self._nube(proyectados, color=AMBAR)
        eje_h2 = tf.eje_propio(angulo, largo=self.EJE_LARGO, color=AMBAR)
        eje_v2 = tf.eje_propio(angulo + 90.0, largo=self.EJE_LARGO,
                               color=AMBAR)
        r4 = rot("casi nada se pierde", color=AMBAR)
        grupo5 = VGroup(nube3, eje_h2, eje_v2)
        r4.next_to(grupo5, UP, buff=0.28)
        L.relevo(escena=VGroup(nube3, eje_h2, eje_v2, r4), t=0.8,
                 salida=0.45)
        self.leer(5.0)

# 17 · Hough — encontrar la recta escondida.
#
# El verbo visual: una nube donde no se ve nada. Cada punto, sea de la
# recta o del ruido, VOTA una senoide entera en el plano (theta, rho).
# Los puntos alineados votan senoides distintas que se cruzan TODAS en la
# misma casilla; los de ruido no se ponen de acuerdo entre si. Marcamos
# esa casilla y volvemos a la nube: la recta que pasa por ahi es la
# escondida.
#
# Cuatro estados, uno por parrafo del arco:
#   1. la nube cruda (84 puntos, mezclados, sin pista visual);
#   2. las 84 senoides (unas pocas primero, para que se entienda que cada
#      punto pone UNA curva antes de que entren las demas y la maraña
#      tape el detalle);
#   3. el cruce marcado con un aro ambar, y la cifra de sus votos;
#   4. la vuelta: la recta de ese cruce, encima de la nube original, con
#      los 24 puntos de la recta re-pintados en ambar para que se vea que
#      pasa exactamente por ellos.
#
# Honestidad: 24 alineados, 60 de ruido (y por tanto "84 puntos") son
# PARAMETROS de `tf.nube_con_recta` (gris). Los votos del cruce los MIDE
# `tf.pico_hough` en este render (ambar) — la sonda demuestra que ese
# pico junta 22 de los 24 puntos alineados.
#
# La posicion del cruce se calcula con la MISMA formula de mapeo que usa
# `tf.senoides_hough` puertas adentro (mismo ancho/alto y mismo
# rango_x=(0,pi), rango_y=(-rho_max,rho_max)): pedirle a `tf.traza` un
# `punto()` con esos mismos argumentos da exactamente esa correspondencia,
# sin reinventar la formula a mano. Y, como manda la Trampa 3 del
# contrato, el aro y el punto del cruce se construyen DENTRO del mismo
# grupo que las senoides, antes de que `L.relevo` los encaje juntos — si
# se añadieran despues no llevarian ni la escala ni la posicion que
# `encajar` le dio al grupo.
class Clip(Pieza):
    NOMBRE = "HOUGH"
    TESIS = "encontrar la recta escondida"

    N_RECTA = 24
    N_RUIDO = 60
    ANCHO_NUBE = 5.2
    ALTO_NUBE = 3.2
    ANCHO_H = 5.2
    ALTO_H = 3.2
    RHO_MAX = 1.5
    N_THETA = 180

    def _punto_hough(self):
        """El mismo mapeo (theta, rho) -> dibujo que usa `tf.senoides_hough`,
        para poder situar el cruce sin recalcular la formula a mano."""
        _, punto = tf.traza([0.0, 1.0], [0.0, 0.0], ancho=self.ANCHO_H,
                            alto=self.ALTO_H, rango_x=(0.0, np.pi),
                            rango_y=(-self.RHO_MAX, self.RHO_MAX))
        return punto

    def _senoides(self):
        return tf.senoides_hough(self.px, self.py, ancho=self.ANCHO_H,
                                 alto=self.ALTO_H, color=APAGADO,
                                 n_theta=self.N_THETA, rho_max=self.RHO_MAX)

    def pieza(self):
        L = self.L

        self.px, self.py = tf.nube_con_recta(self.N_RECTA, self.N_RUIDO)
        puntos = np.column_stack([self.px, self.py])
        th, rho, acc = tf.hough(self.px, self.py, n_theta=self.N_THETA,
                                rho_max=self.RHO_MAX)
        votos, fila, columna = tf.pico_hough(acc)
        theta_pico, rho_pico = float(th[columna]), float(rho[fila])

        # --- 1. la nube: a ojo no se ve nada -----------------------------
        nube1, _ = tf.nube(puntos, ancho=self.ANCHO_NUBE, alto=self.ALTO_NUBE,
                           color=TINTA, radio=0.05)
        et1 = rot(f"{len(self.px)} puntos", color=APAGADO)
        et1.next_to(nube1, UP, buff=0.3)
        L.escena(VGroup(nube1, et1), t=1.3)
        self.leer(3.6)

        # --- 2. cada punto vota una curva --------------------------------
        curvas = self._senoides()
        et2 = rot("cada punto, una curva", color=APAGADO)
        et2.next_to(curvas, UP, buff=0.3)
        # Unas pocas primero (mezcla de recta y ruido, para no adelantar el
        # cruce) y luego el resto: asi se lee "una curva por punto" antes
        # de que las 84 juntas se vuelvan una maraña.
        muestra = [0, 1, 2, self.N_RECTA, self.N_RECTA + 1, self.N_RECTA + 2]
        primeras = VGroup(*[curvas[i] for i in muestra])
        resto = VGroup(*[curvas[i] for i in range(len(curvas))
                         if i not in muestra])
        anim2 = Succession(
            AnimationGroup(Create(primeras, run_time=1.5),
                          FadeIn(et2, run_time=0.8)),
            FadeIn(resto, run_time=1.5),
        )
        L.relevo(escena=VGroup(curvas, et2), animacion=anim2, t=1.5,
                salida=0.5)
        self.leer(4.6)

        # --- 3. el cruce: ahi esta la recta -------------------------------
        curvas2 = self._senoides()
        punto_h = self._punto_hough()
        centro = punto_h(theta_pico, rho_pico)
        aro = Circle(radius=0.17, stroke_color=AMBAR,
                    stroke_width=tf.TRAZO_FINO, fill_opacity=0.0)
        aro.move_to(centro)
        cruce = Dot(centro, radius=0.075, color=AMBAR)
        et3 = rot("el cruce", color=AMBAR)
        et3.next_to(curvas2, UP, buff=0.3)
        grupo3 = VGroup(curvas2, aro, cruce, et3)
        L.relevo(escena=grupo3,
                dato=(medido(votos, 0), "votos en el cruce"),
                t=1.3, salida=0.5)
        self.leer(4.8)

        # --- 4. la vuelta: la recta sobre la nube original ----------------
        nube2, punto_n = tf.nube(puntos, ancho=self.ANCHO_NUBE,
                                 alto=self.ALTO_NUBE, color=APAGADO,
                                 radio=0.05)
        for i in range(self.N_RECTA):
            nube2[i].set_color(AMBAR)
        x0 = float(self.px[:self.N_RECTA].min())
        x1 = float(self.px[:self.N_RECTA].max())
        y0 = (rho_pico - x0 * np.cos(theta_pico)) / np.sin(theta_pico)
        y1 = (rho_pico - x1 * np.cos(theta_pico)) / np.sin(theta_pico)
        recta = Line(punto_n(x0, y0), punto_n(x1, y1), stroke_color=AMBAR,
                    stroke_width=tf.TRAZO)
        et4 = rot("la recta encontrada", color=AMBAR)
        et4.next_to(VGroup(nube2, recta), UP, buff=0.3)
        grupo4 = VGroup(nube2, recta, et4)
        anim4 = Succession(
            FadeIn(nube2, run_time=0.8),
            Create(recta, run_time=1.3),
            FadeIn(et4, run_time=0.6),
        )
        # La cifra del cruce se queda IGUAL: es la unica que este render
        # midio de verdad, y es la que cierra la pieza.
        L.relevo(escena=grupo4, animacion=anim4, t=1.2, salida=0.5)
        self.leer(6.0)

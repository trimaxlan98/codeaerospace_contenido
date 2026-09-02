# 06 · Voltajes que no existen
#
# El chip solo pone 0 o 3.3 V. El voltaje intermedio no existe en ningun
# instante: existe en la MEDIA. PWM + filtro RC.
#
# Cifras: TODAS salen de `chip.pwm_filtrado` + `chip.media_y_rizado`
# durante el render, y SIEMPRE sobre la ventana visible (de `i0` en
# adelante), que es exactamente la que se dibuja. Medir la simulacion
# entera daria 0.74 V en vez de 1.65 porque el condensador todavia se
# esta cargando. Lo unico de hoja de datos es el 3.3 (etiqueta APAGADA).
#
# Dos señales a la vez (el caso que lo permite): el tren va en APAGADO y
# lo que el filtro fabrica va en AMBAR. Un solo acento por fotograma.
#
# Y la cifra se APAGA antes de relevar el dibujo, no despues: si no, el
# segundo y medio que dura el relevo enseña el dibujo nuevo con la cifra
# vieja (se vio en el frame 4 de la primera pasada: el tren al 30 % con
# "1.65 voltios de media" debajo, que es mentir a quien mire justo ahi).
class Clip(Pieza):
    NUMERO = 6

    ANCHO_G = 5.30      # de 5.76 seguros
    ALTO_G = 3.80       # de 5.59 de banda: el 68 %

    def _plot(self, series, rango_y):
        """El cuadro completo: eje en ele + las trazas que se le pasen.

        `series` son tuplas (x, y, color, escalones). Devuelve el grupo y
        el localizador de la PRIMERA serie, que es el que usa `nivel`."""
        eje = chip.eje_ele(ancho=self.ANCHO_G, alto=self.ALTO_G)
        grupo = VGroup(eje)
        punto = None
        for x, y, color, esc in series:
            linea, pt = chip.traza(x, y, ancho=self.ANCHO_G,
                                   alto=self.ALTO_G, color=color,
                                   rango_y=rango_y, escalones=esc)
            punto = punto or pt
            grupo.add(linea)
        return grupo, punto

    def pieza(self):
        L = self.L
        VDD = chip.HOJA["vdd"]
        RANGO = (0.0, VDD)

        # --- la simulacion, ya en regimen ------------------------------
        # `i0` es donde empieza la ventana visible: lo anterior es el
        # transitorio de carga y ni se dibuja ni se mide.
        t, v, y, i0 = chip.pwm_filtrado(0.5, ciclos_vista=6)
        tv, vv, yv = t[i0:], v[i0:], y[i0:]
        media, rizado = chip.media_y_rizado(tv, yv)

        # --- 1. el chip solo tiene dos valores -------------------------
        # La discontinua marca la altura donde luego aterrizara la media:
        # ahora mismo es una altura por la que el tren solo PASA.
        g1, punto = self._plot([(tv, vv, TINTA, True)], RANGO)
        g1.add(chip.nivel(media, punto, ancho=self.ANCHO_G, color=APAGADO))
        L.escena(g1, animacion=Create(g1, run_time=1.8))
        self.wait(0.6)
        L.dato(medido(VDD, 1), "voltios y nada mas", medido=False)
        self.wait(4.4)

        # --- 2. y aun asi fabrica el de en medio -----------------------
        g2, _ = self._plot([(tv, vv, APAGADO, True),
                            (tv, yv, AMBAR, False)], RANGO)
        L.quitar("dato", t=0.35)
        L.escena(g2, t=0.9)
        self.wait(0.45)
        L.dato(medido(media, 2), "voltios de media")
        self.wait(4.2)

        # --- 3. menos tiempo encendido, menos media --------------------
        t3, v3, y3, i3 = chip.pwm_filtrado(0.3, ciclos_vista=6)
        t3v, v3v, y3v = t3[i3:], v3[i3:], y3[i3:]
        media3, _ = chip.media_y_rizado(t3v, y3v)

        g3, _ = self._plot([(t3v, v3v, APAGADO, True),
                            (t3v, y3v, AMBAR, False)], RANGO)
        L.quitar("dato", t=0.35)
        L.escena(g3, t=0.9)
        self.wait(0.45)
        L.dato(medido(media3, 2), "voltios de media")
        self.wait(4.2)

        # --- 4. de cerca, la linea no es plana -------------------------
        # Mismo dato de antes, otra escala vertical: el cuadro mide 1.24
        # rizados de alto, asi que la sierra ocupa el 80 % y queda un
        # margen que deja claro que no esta recortada.
        zoom = (media - 0.62 * rizado, media + 0.62 * rizado)
        g4, _ = self._plot([(tv, yv, AMBAR, False)], zoom)
        L.quitar("dato", t=0.35)
        L.escena(g4, t=0.9)
        self.wait(0.45)
        L.dato(medido(rizado * 1000, 1), "milivoltios de rizado")
        self.wait(4.2)

        # --- 5. remate: la decima parte de condensador -----------------
        t5, v5, y5, i5 = chip.pwm_filtrado(0.5, C=100e-9, ciclos_vista=6)
        t5v, y5v = t5[i5:], y5[i5:]
        _, rizado5 = chip.media_y_rizado(t5v, y5v)

        ancho_z = 0.62 * rizado5
        g5, _ = self._plot([(tv, yv, APAGADO, False),
                            (t5v, y5v, AMBAR, False)],
                           (media - ancho_z, media + ancho_z))
        L.quitar("dato", t=0.35)
        L.escena(g5, t=0.9)
        self.wait(0.45)
        L.dato(medido(rizado5 * 1000, 0), "milivoltios de rizado")
        self.wait(4.9)

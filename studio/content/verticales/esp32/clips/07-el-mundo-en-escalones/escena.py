# 07 · El mundo entra en escalones
#
# El mundo es continuo y el chip solo sabe contar. El ADC de 12 bits parte
# los 3.3 V en 4096 peldaños: todo lo que cae entre dos peldaños se pierde,
# y esa perdida tiene un tamaño exacto.
#
# LA EXAGERACION, declarada en pantalla: la escalera se dibuja a 5 bits, no
# a 12. Esta medido — a 12 bits el peldaño vale 3.3/4096 = 0.81 mV, que
# sobre la caja de 3.6 unidades son 0.00088 unidades, o sea 0.12 px en el
# 1080x1920 final: la escalera de 12 bits ES la curva, pixel a pixel, y
# dibujarla seria enseñar una recta y llamarla escalera. A 5 bits el
# peldaño mide 0.1125 unidades (15 px) y se ve. Por eso el dibujo lleva
# SIEMPRE el rotulo gris "5 BITS PARA VERLO" — en los tres estados en los
# que aparece.
#
# Las CIFRAS son todas de 12 bits y todas medidas sobre la MISMA ventana
# que se dibuja: `error_cuantizacion(x)` devuelve el RMS y el escalon de
# esta senoide, y `snr_medido` cuantiza su propia senoide a fondo de
# escala. Lo unico que viene de la hoja de datos son los 3.3 V (etiqueta
# gris); todo lo demas es ambar.
class Clip(Pieza):
    NUMERO = 7

    BITS_DIBUJO = 5          # solo para el dibujo, y se dice en pantalla
    ANCHO_C = 5.0
    ALTO_C = 3.6
    ALTO_E = 3.1             # la caja del error, un punto mas baja

    # --- piezas del dibujo --------------------------------------------
    def _aviso(self, alto):
        """El rotulo gris que declara la exageracion. Sin el, el clip
        miente: lo que se ve son 32 peldaños y lo que se rotula, 4096."""
        r = rot(f"{self.BITS_DIBUJO} bits para verlo")
        r.move_to([0, alto / 2 + 0.34, 0])
        return r

    def _curva(self, t, x, vref, color):
        ln, _ = chip.traza(t, x, ancho=self.ANCHO_C, alto=self.ALTO_C,
                           color=color, rango_y=(0.0, vref))
        return ln

    def _escalera(self, t, x, vref):
        """La curva apagada con su escalera ambar encima. Es el unico sitio
        del clip donde conviven dos trazas, y por eso una va en APAGADO."""
        y, _ = chip.cuantizar(x, bits=self.BITS_DIBUJO, vref=vref)
        esc, _ = chip.traza(t, y, ancho=self.ANCHO_C, alto=self.ALTO_C,
                            color=AMBAR, rango_y=(0.0, vref),
                            escalones=True)
        return VGroup(chip.eje_ele(self.ANCHO_C, self.ALTO_C),
                      self._curva(t, x, vref, APAGADO), esc,
                      self._aviso(self.ALTO_C))

    def _error(self, t, x, vref):
        """Lo que sobra: la diferencia entre la curva y la escalera. La caja
        va de -q/2 a +q/2, que es el rango REAL del error de redondeo, asi
        que el diente de sierra la llena por derecho. El suelo aqui no es
        cero (el cero esta en medio), asi que el eje en L se cambia por una
        horizontal discontinua a la altura del cero."""
        y, q5 = chip.cuantizar(x, bits=self.BITS_DIBUJO, vref=vref)
        ln, punto = chip.traza(t, x - y, ancho=self.ANCHO_C,
                               alto=self.ALTO_E, color=AMBAR,
                               rango_y=(-q5 / 2, q5 / 2))
        cero = chip.nivel(0.0, punto, ancho=self.ANCHO_C, color=LINEA)
        return VGroup(cero, ln, self._aviso(self.ALTO_E))

    # --- la pieza ------------------------------------------------------
    def pieza(self):
        L = self.L
        vref = chip.HOJA["vdd"]
        bits = chip.HOJA["adc_bits"]

        # La señal del mundo: una senoide que casi recorre el fondo de
        # escala (0.198 a 3.102 V) pero no lo toca. A proposito: pegada a
        # los topes, el cuantizador recorta y el error dejaria de ser solo
        # de redondeo — la cifra de abajo hablaria de otra cosa.
        t = np.linspace(0.0, 2.0, 1200)
        x = 0.5 * vref + 0.44 * vref * np.sin(2 * np.pi * t)

        # Las tres cifras calculadas, TODAS a 12 bits y sobre esta ventana.
        rms, q = chip.error_cuantizacion(x)      # bits=12 por defecto
        niveles = int(round(vref / q))           # 4096, del propio escalon
        snr = chip.snr_medido(bits)              # 73.79 dB medidos

        # --- 1. el mundo, continuo -------------------------------------
        g1 = VGroup(chip.eje_ele(self.ANCHO_C, self.ALTO_C),
                    self._curva(t, x, vref, TINTA))
        L.escena(g1, animacion=Create(g1, run_time=2.0, lag_ratio=0.3))
        self.wait(0.6)
        L.dato(medido(vref, 1), "voltios de fondo de escala",
               medido=False, t=0.7)
        self.wait(3.6)

        # --- 2. y como lo ve el chip -----------------------------------
        g2 = self._escalera(t, x, vref)
        L.escena(g2, animacion=FadeIn(g2, run_time=1.2))
        self.wait(0.5)
        L.dato(niveles, "escalones en doce bits")
        self.wait(3.9)

        # --- 3. cuanto mide un peldaño ---------------------------------
        L.dato(medido(q * 1000), "milivoltios por escalon")
        self.wait(4.6)

        # --- 4. lo que se queda fuera ----------------------------------
        g3 = self._error(t, x, vref)
        L.escena(g3, animacion=FadeIn(g3, run_time=1.3))
        self.wait(0.4)
        L.dato(medido(rms * 1000), "milivoltios de error eficaz")
        self.wait(4.4)

        # --- 5. el precio, en decibelios -------------------------------
        g4 = self._escalera(t, x, vref)
        L.escena(g4, animacion=FadeIn(g4, run_time=1.1))
        L.dato(str(int(round(snr))), "decibelios sobre el ruido")
        self.wait(5.0)

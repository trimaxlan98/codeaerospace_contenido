# 05 · DCT — tirar casi todo sin notarlo.
#
# El verbo visual es literalmente lo que hace JPEG: un bloque 8x8 de imagen
# se convierte en 64 coeficientes, se APAGAN 58 de ellos y al volver la
# imagen sigue ahi. No hace falta explicarlo con palabras porque se ve.
#
# Tres decisiones que costaron una vuelta cada una:
#
# 1. LA MALLA NO SE APAGA Y SE ENCIENDE: SE TRANSFORMA. `L.relevo` apaga el
#    dibujo viejo y enciende el nuevo en dos `play` seguidos, asi que las
#    64 casillas desaparecerian del todo y volverian con seis encendidas.
#    Eso no es "se apagan 58", es "cambia el dibujo". Como las dos mallas
#    son gemelas exactas (64 rectangulos en las mismas posiciones), un
#    `Transform` las empareja casilla a casilla: las seis que sobreviven se
#    quedan quietas con su brillo y las otras 58 se van al azul del fondo.
#    Ese es el plano entero de la pieza.
#    Para que el carril del lienzo siga siendo cierto, el `Transform` se
#    hace SOBRE el mobject que ya ocupa el carril (`Transform` muta el
#    primero), asi que `L.ocupantes["escena"]` sigue apuntando a lo que
#    hay en pantalla y el fundido final se lo lleva bien.
#
# 2. LOS 64 NUMEROS SE ENSEÑAN DOS VECES, Y LA PRIMERA ES LA VERDADERA. A
#    escala real el modulo de la DCT es UNA casilla blanca, otra gris y 62
#    practicamente al color del fondo: el 89.74 % de la energia esta en el
#    primer coeficiente. Esa imagen es la tesis, asi que va primera y sin
#    retoque. Solo despues se comprime la escala (|C| ** 0.35) para que se
#    vea que los pequeños no son cero — y se DECLARA con un rotulo gris,
#    porque enseñar una escala falseada sin decirlo seria mentir sobre la
#    magnitud, que es justo de lo que va la pieza.
#
# 3. LA COMPARACION FINAL NO SE MAQUILLA. `tf.malla` normaliza cada matriz
#    por su propio minimo y maximo, y el bloque rehecho tiene menos rango
#    que el original (0.579 contra 0.644), asi que sale mas contrastado de
#    lo que es. Medido: con la normalizacion de `malla` las dos imagenes
#    difieren hasta 0.137 de escala completa, y en una escala comun solo
#    0.089. O sea que el defecto va EN CONTRA de la tesis — se enseñan mas
#    distintas de lo que son. Se deja asi: corregirlo pediria tocar la
#    libreria y ademas el error conservador no hace daño.
#
# Honestidad de las cifras: el 8x8 y el 6 son parametros ELEGIDOS (gris);
# el 99.81 % lo calcula `tf.energia_en_mayores` en este render (ambar).
class Clip(Pieza):
    NOMBRE = "DCT"
    TESIS = "tirar casi todo sin notarlo"

    LADO = 3.4              # la malla sola: 3.4 + rotulos = 4.34 en 5.39
    LADO_PAR = 2.5          # las dos en fila: 5.45 en 5.76 de zona segura
    GUARDADOS = 6           # cuantos coeficientes sobreviven. Elegido.
    GAMMA = 0.35            # compresion SOLO de la escala de color, y se
                            # dice en pantalla. Ver la nota 2 de arriba.

    def _malla(self, valores, lado=None):
        return tf.malla(valores, lado=lado or self.LADO)

    def _gemela(self, valores, referencia):
        """Una malla colocada EXACTAMENTE encima de otra que ya esta en
        pantalla, lista para un `Transform`.

        Se construye despues de que el lienzo haya encajado el grupo, asi
        que no hereda ni su escala ni su posicion (la trampa 3 de la casa).
        En vez de adivinarlas se copian de la que ya esta puesta."""
        d = self._malla(valores)
        d.scale(referencia.width / d.width)
        d.move_to(referencia)
        return d

    def _mutar(self, *animaciones, dato=None):
        """Cambia el dibujo POR DENTRO —sin apagarlo— y, si hace falta, la
        cifra, dentro de UN SOLO play.

        Ni `L.relevo` ni `L.dato` sirven aqui. El primero apaga el dibujo
        entero antes de encender el siguiente, y lo que cuenta esta pieza
        es que las MISMAS casillas se apagan. El segundo gasta dos play y
        deja un rato el dibujo nuevo con la cifra vieja debajo, que es la
        mentira que el estilo prohibe. Asi que la cifra viaja en el mismo
        play (apagar y encender encadenados, para que los dos numeros no
        se solapen) y el carril queda apuntando a la nueva: la garantia de
        "un carril, un ocupante" se mantiene intacta."""
        anims = list(animaciones)
        if dato is not None:
            nuevo = lz.dato(*dato)
            viejo = self.L.ocupantes.get("dato")
            self.L.ocupantes["dato"] = nuevo
            anims.append(Succession(FadeOut(viejo, run_time=0.40),
                                    FadeIn(nuevo, run_time=0.55)))
        self.play(*anims)

    def pieza(self):
        L = self.L
        bloque = tf.bloque_ejemplo(8)
        coef = np.abs(tf.dct2(bloque))
        umbral = np.sort(coef.ravel())[::-1][self.GUARDADOS - 1]
        mascara = np.where(coef >= umbral, coef, 0.0)
        rehecho = tf.reconstruir_con(bloque, self.GUARDADOS)
        tirados = bloque.size - self.GUARDADOS

        # --- 1. el bloque: 64 casillas de una imagen ------------------
        m_bloque = self._malla(bloque)
        r_bloque = rot("el bloque")
        r_bloque.next_to(m_bloque, UP, buff=0.28)
        L.relevo(escena=VGroup(m_bloque, r_bloque),
                 dato=(medido(bloque.size, 0), "numeros del bloque", False),
                 t=0.8)
        self.leer(3.0)

        # --- 2. los mismos 64, en el otro dominio ---------------------
        # La cifra NO cambia, y ese es el argumento: la DCT no añade ni
        # quita numeros, los reparte de otra manera. Cambiar la etiqueta
        # aqui habria roto esa idea, asi que el carril del dato se deja
        # como esta y solo se releva el dibujo.
        m_coef = self._malla(coef)
        r_coef = rot("sus 64 numeros", color=AMBAR)
        r_coef.next_to(m_coef, UP, buff=0.28)
        r_pocos = rot("solo 6 de 64", color=AMBAR)
        r_pocos.next_to(m_coef, UP, buff=0.28)
        r_escala = rot("escala comprimida", cuerpo=lz.MICRO)
        r_escala.next_to(m_coef, DOWN, buff=0.26)
        # Los tres rotulos nacen dentro del grupo aunque dos esten
        # apagados: construidos despues de `L.escena` vendrian sin la
        # colocacion que el lienzo le da al grupo.
        for oculto in (r_pocos, r_escala):
            oculto.set_opacity(0.0)
        L.escena(VGroup(m_coef, r_coef, r_pocos, r_escala), t=0.8)
        self.leer(3.0)

        # --- 3. la misma matriz con la escala de color comprimida -----
        self.play(
            Transform(m_coef, self._gemela(coef ** self.GAMMA, m_coef),
                      run_time=0.9),
            r_escala.animate(run_time=0.9).set_opacity(1.0))
        self.leer(3.2)

        # --- 4. se apagan 58 ------------------------------------------
        # Los dos rotulos se relevan ENCADENADOS, no a la vez: ocupan el
        # mismo renglon, y cruzarles la opacidad dejaba medio segundo de
        # "SUSL646NUMEROS" ilegible (medido en el frame de t=16.9 de la
        # primera vuelta). Es la regla de "nada se encima" aplicada dentro
        # de un grupo, donde el lienzo ya no puede vigilarla.
        self._mutar(
            Transform(m_coef,
                      self._gemela(mascara ** self.GAMMA, m_coef),
                      run_time=0.95),
            Succession(r_coef.animate(run_time=0.40).set_opacity(0.0),
                       r_pocos.animate(run_time=0.55).set_opacity(1.0)),
            dato=(medido(self.GUARDADOS, 0), "numeros que quedan", False))
        self.leer(3.4)

        # --- 5. la vuelta: la imagen que dan esos seis ----------------
        # Sigue habiendo seis numeros, asi que la cifra sigue siendo
        # cierta y se queda: lo que cambia es lo que se ve con ellos.
        m_rehecho = self._malla(rehecho)
        r_rehecho = rot("rehecho con 6", color=AMBAR)
        r_rehecho.next_to(m_rehecho, UP, buff=0.28)
        L.escena(VGroup(m_rehecho, r_rehecho), t=0.8)
        self.leer(3.2)

        # --- 6. el original al lado, y lo que costo ------------------
        par_orig = self._malla(bloque, lado=self.LADO_PAR)
        rp_orig = rot("el bloque")
        rp_orig.next_to(par_orig, DOWN, buff=0.22)
        par_rec = self._malla(rehecho, lado=self.LADO_PAR)
        rp_rec = rot("con 6 numeros", color=AMBAR)
        rp_rec.next_to(par_rec, DOWN, buff=0.22)
        fila = VGroup(VGroup(par_orig, rp_orig), VGroup(par_rec, rp_rec))
        fila.arrange(RIGHT, buff=0.45, aligned_edge=UP)
        L.relevo(escena=fila,
                 dato=(medido(tirados, 0), "numeros tirados", False),
                 t=0.8)
        self.leer(3.2)

        # --- 7. y lo que se guardo ------------------------------------
        # El dibujo no se mueve: la misma pareja, y debajo el numero que
        # explica por que se parecen tanto. Es la unica cifra medida de la
        # pieza y por eso cierra.
        L.dato(medido(100.0 * tf.energia_en_mayores(bloque, self.GUARDADOS),
                      2),
               "por ciento de energia")
        self.leer(4.2)

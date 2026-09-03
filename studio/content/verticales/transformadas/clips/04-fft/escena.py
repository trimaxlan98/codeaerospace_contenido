# 04 · FFT — el mismo resultado, menos cuentas.
#
# El verbo visual: la malla de operaciones que se PARTE POR LA MITAD, una
# y otra vez. Primero la via directa, que une CADA entrada con CADA salida
# (N*N hilos, un tejido sin estructura); despues el grafo de mariposa, con
# el ambar bajando de etapa en etapa: una aspa que cruza el grafo entero,
# luego dos, luego cuatro, luego ocho.
#
# El barrido va de la ULTIMA etapa a la primera, y no al reves. En el
# grafo de mariposa la etapa k cruza a distancia 2**k, asi que recorrerlo
# de derecha a izquierda es ver el problema partirse: uno, dos, cuatro,
# ocho grupos. De izquierda a derecha se ve lo contrario — pares que se
# juntan— y el rotulo "partir por la mitad" estaria diciendo lo que no se
# ve. La primera version iba 0,1,2,3 y en el frame se leia al reves.
#
# HONESTIDAD, que es lo que decide esta pieza. Las cifras son para
# N = 4096: 16 777 216 productos por la via directa, 12 etapas, 24 576
# mariposas y 683 veces menos cuentas. Un grafo de 4096 nodos NO se puede
# dibujar (4096 filas en las 5.39 unidades de alto de la franja salen a
# 0.0013 por fila), asi que el dibujo lleva 16 nodos y cuatro etapas en
# vez de doce. Eso no se esconde, ni se arregla rebajando las cifras a las
# del dibujo pequeño — la cifra buena es la de 4096, que es la que se usa
# de verdad: se DECLARA. Debajo del dibujo vive un rotulo gris permanente,
# "dibujado con 16", y la etiqueta de cada cifra dice "con 4096". Las dos
# cosas en el mismo fotograma no dejan sitio a la confusion.
#
# Las CUATRO cifras comparten cuerpo de letra. Dejando que cada una
# eligiera el suyo, "16 777 216" bajaba a cuerpo 72 por lo ancho y "12" se
# quedaba en 128: el numero de diecisiete millones salia en pantalla la
# mitad de alto que el doce, y en una pieza muda el tamaño es lo unico que
# marca importancia. Compartir cuerpo es lo que hace que las cuatro se
# lean como la misma cuenta bajando.
#
# Provenencia: el 4096 y los 16 nodos del dibujo son parametros ELEGIDOS y
# van en gris; las cuatro cifras las calcula `transformadas.py` en este
# render (`coste_dft`, `niveles_fft`, `coste_fft`, `ahorro_fft`) y van con
# la etiqueta en ambar.
class Clip(Pieza):
    NOMBRE = "FFT"
    TESIS = "el mismo resultado, menos cuentas"

    N = 4096                 # el N de las cifras: elegido, no medido
    NIVELES = 4              # 16 nodos: lo mas que se sigue con la vista
    ANCHO_G = 4.8
    ALTO_G = 2.9
    ALTO_CHICO = 1.58        # los dos paneles de la comparacion final
    TINTE_MALLA = 0.30       # 256 hilos: a mas opacidad es una mancha
    # Hueco entre grupos de miles, en anchos de caracter. `lz.HUECO_MILES`
    # vale 0.34 y su propia docstring dice 0.42; medido en el frame, con
    # 0.34 "16 777 216" sale como un bloque macizo de ocho digitos pegados
    # — justo lo que el separador existia para evitar. Aqui se montan los
    # grupos a mano con hueco de 0.75. La libreria NO se toca: se rodea.
    HUECO_MILES = 0.75

    # --- dibujo -------------------------------------------------------
    def _nodos(self):
        return 2 ** self.NIVELES

    def _malla_llena(self, ancho, alto):
        """La via directa: cada salida toca TODAS las entradas.

        Misma geometria que `tf.mariposa` (las dos mismas columnas de
        puntos, el mismo alto) a proposito: asi el relevo de una a la otra
        se lee como el MISMO dibujo simplificandose, y no como dos dibujos
        que no tienen nada que ver."""
        n = self._nodos()
        ys = np.linspace(alto / 2, -alto / 2, n)
        x0, x1 = -ancho / 2, ancho / 2
        g = VGroup()
        for yi in ys:
            for yj in ys:
                g.add(Line([x0, yi, 0], [x1, yj, 0],
                           stroke_color=APAGADO, stroke_width=tf.TRAZO_PELO,
                           stroke_opacity=self.TINTE_MALLA))
        for yi in ys:
            g.add(Dot([x0, yi, 0], radius=0.032, color=APAGADO))
            g.add(Dot([x1, yi, 0], radius=0.032, color=APAGADO))
        return g

    def _capas_mariposa(self, ancho, alto):
        """El grafo apagado y, encima, UNA capa ambar por etapa.

        `tf.mariposa(activo=k)` devuelve el grafo entero con la etapa k
        encendida; de ahi se queda solo con las aristas ambar, filtradas
        por COLOR y no por su posicion dentro del grupo (asi no depende
        del orden interno de la libreria). Apiladas sobre el grafo
        apagado, encender una y apagar la anterior mueve el ambar de etapa
        sin tocar ni un trazo del resto del dibujo — que es lo que evita
        fundir el grafo entero cuatro veces y parpadear."""
        base = tf.mariposa(self.NIVELES, ancho=ancho, alto=alto)
        capas = []
        for k in range(self.NIVELES):
            m = tf.mariposa(self.NIVELES, ancho=ancho, alto=alto, activo=k)
            capas.append(VGroup(*[
                s for s in m.submobjects
                if isinstance(s, Line)
                and s.get_stroke_color().to_hex()[:7].upper()
                == AMBAR[:7].upper()]))
        return VGroup(base, *capas), capas

    def _cuadro(self, dibujo, titulo=None, color=AMBAR, hueco=0.26):
        """El dibujo, su nombre encima y la declaracion debajo.

        La nota gris no es un adorno: mientras haya en pantalla una cifra
        de 4096 sobre un dibujo de 16 nodos, tiene que estar dicho en el
        MISMO fotograma."""
        piezas = [dibujo]
        if titulo:
            t = rot(titulo, color=color)
            t.next_to(dibujo, UP, buff=0.30)
            piezas.append(t)
        nota = rot(f"dibujado con {self._nodos()}", cuerpo=lz.MICRO)
        nota.next_to(dibujo, DOWN, buff=hueco)
        piezas.append(nota)
        return VGroup(*piezas)

    # --- la cifra, con los miles separados de verdad --------------------
    def _numero(self, cadena, cuerpo):
        grupos = str(cadena).split(" ")
        piezas = [lz.cifra(g, font_size=cuerpo) for g in grupos]
        if len(piezas) == 1:
            return piezas[0]
        paso = piezas[0].width / max(len(grupos[0]), 1)
        return VGroup(*piezas).arrange(RIGHT, buff=paso * self.HUECO_MILES,
                                       aligned_edge=DOWN)

    def _cuerpo(self, cadenas):
        """El mayor cuerpo de la escala en el que entran TODAS las cifras
        ya con el hueco de miles ancho. Mismo criterio que
        `lz.cuerpo_cifra`, pero midiendo el numero tal y como se va a
        dibujar aqui."""
        for fs in lz.ESCALA_CIFRA:
            if all(self._numero(c, fs).width <= lz.ANCHO_SEGURO + 1e-6
                   for c in cadenas):
                return fs
        raise lz.FueraDelLienzo(
            f"{cadenas} no entran ni al cuerpo minimo {lz.ESCALA_CIFRA[-1]}")

    def _dato(self, cadena, texto, cuerpo, medido=True):
        num = self._numero(cadena, cuerpo)
        num.move_to([0, lz.Y_CIFRA, 0])
        eti = lz.etiqueta(texto, medido=medido)
        eti.next_to(num, DOWN, buff=0.30)
        lz.cabe(num, f"cifra '{cadena}'")
        lz.cabe(eti, f"etiqueta '{texto}'")
        tope = lz.Y_MARCA + 0.22
        if eti.get_bottom()[1] < tope:
            raise lz.FueraDelLienzo(
                f"el dato baja hasta {eti.get_bottom()[1]:.2f} y la marca "
                f"empieza en {tope:.2f}")
        return VGroup(num, eti)

    # --- la pieza -------------------------------------------------------
    def pieza(self):
        L = self.L
        directa = lz.miles(tf.coste_dft(self.N))
        rapida = lz.miles(tf.coste_fft(self.N))
        etapas = medido(tf.niveles_fft(self.N), 0)
        ahorro = medido(tf.ahorro_fft(self.N), 0)
        cuerpo = self._cuerpo([directa, rapida, etapas, ahorro])

        # --- 1. la via directa: todas con todas -----------------------
        malla = self._cuadro(self._malla_llena(self.ANCHO_G, self.ALTO_G),
                             "todas con todas", color=APAGADO)
        L.escena(malla, t=0.9)
        self.leer(2.4)
        L.poner("dato", self._dato(directa, f"productos con {self.N}",
                                   cuerpo), t=0.7)
        self.leer(3.2)

        # --- 2. el mismo trabajo, partido por la mitad ----------------
        grafo, capas = self._capas_mariposa(self.ANCHO_G, self.ALTO_G)
        for capa in capas[:-1]:
            capa.set_stroke(opacity=0.0)
        L.relevo(escena=self._cuadro(grafo, "partir por la mitad"),
                 dato=self._dato(etapas, f"etapas con {self.N}", cuerpo),
                 t=0.9, salida=0.5)
        self.leer(2.4)

        for i in range(self.NIVELES - 2, -1, -1):
            self.play(capas[i + 1].animate.set_stroke(opacity=0.0),
                      capas[i].animate.set_stroke(opacity=1.0),
                      run_time=0.5)
            self.leer(2.4 if i == 0 else 2.2)

        # --- 3. y esto de aqui es la fft ENTERA -----------------------
        self.play(*[c.animate.set_stroke(opacity=1.0) for c in capas],
                  run_time=0.7)
        self.leer(1.8)
        L.poner("dato", self._dato(rapida, f"mariposas con {self.N}",
                                   cuerpo), t=0.7)
        self.leer(3.2)

        # --- 4. las dos mallas, una sobre la otra ---------------------
        chica, _ = self._capas_mariposa(self.ANCHO_G, self.ALTO_CHICO)
        comparacion = lz.dos_dominios(
            self._malla_llena(self.ANCHO_G, self.ALTO_CHICO), chica,
            "la dft", "la fft", hueco=0.40)
        L.relevo(escena=self._cuadro(comparacion, hueco=0.44),
                 dato=self._dato(ahorro, "veces menos cuentas", cuerpo),
                 t=0.9, salida=0.5)
        self.leer(4.0)

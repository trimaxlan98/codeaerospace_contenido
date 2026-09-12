# 07 · CHLADNI — el sonido dibuja.
#
# Se echa arena sobre una placa, se la hace sonar, y la arena huye de donde
# vibra y se acumula donde no. Lo que queda dibujado son las lineas nodales
# del modo, y salen figuras que nadie esperaria de una placa cuadrada.
#
# La gracia —y lo que esta pieza tiene que enseñar— es POR QUE salen
# curvas: el modo (3,2) y el modo (2,3) suenan a la MISMA frecuencia, asi
# que cualquier mezcla de los dos tambien es un modo valido. Las figuras de
# Chladni no son un modo: son la interferencia de dos modos que suenan
# igual. Por separado, cada uno es una rejilla de rectas. Mezclados, no.
#
# Tres decisiones:
#
#   - **La arena se siembra al azar con semilla fija**, no se dibuja el
#     contorno con una regla. Lo que se ve es lo que haria la arena: caer
#     donde la placa no se mueve.
#   - **La cifra no cambia entre los tres planos** (3.6056, la frecuencia
#     relativa), y eso ES el contenido: dos dibujos distintos y una mezcla
#     que no se parece a ninguno, sonando exactamente igual.
#   - Los dos modos puros van en el MISMO cuadro uno sobre otro, para que
#     se vea que uno es el otro girado.
class Clip(Pieza):
    NOMBRE = "CHLADNI"
    TESIS = "el sonido dibuja"

    # PARAMETROS elegidos: el par de modos degenerados y la malla.
    M, N = 3, 2
    MALLA = 260
    GRANOS = 2400
    LADO = 4.30

    def _placa(self, U, X, Y, paso=13, radio=None):
        radio = radio or self.LADO / 2
        return esp.campo_signo(X, Y, U, radio=radio, paso=paso,
                               grano=0.042)

    def pieza(self):
        L = self.L
        X, Y, U32 = esp.modo_cuadrado(self.M, self.N, N=self.MALLA)
        _, _, U23 = esp.modo_cuadrado(self.N, self.M, N=self.MALLA)
        Xc, Yc, Uc = esp.chladni(self.M, self.N, N=self.MALLA)

        # --- 1. el modo puro: una rejilla de rectas -------------------
        radio = self.LADO / 2
        campo = self._placa(U32, X, Y)
        rectas = VGroup()
        for k in range(1, self.M):
            x = (k / self.M - 0.5) * self.LADO
            rectas.add(Line([x, -radio, 0], [x, radio, 0],
                            stroke_color=TINTA, stroke_width=esp.TRAZO))
        for k in range(1, self.N):
            y = (k / self.N - 0.5) * self.LADO
            rectas.add(Line([-radio, y, 0], [radio, y, 0],
                            stroke_color=TINTA, stroke_width=esp.TRAZO))
        marco_placa = Square(side_length=self.LADO, stroke_color=APAGADO,
                             stroke_width=esp.TRAZO_FINO, fill_opacity=0.0)
        eti32 = rot(f"MODO {self.M} {self.N}", color=APAGADO)
        eti32.next_to(marco_placa, DOWN, buff=0.22)
        placa = lz.agrupar(marco_placa, campo, rectas, eti32)

        L.escena(placa, t=0.9)
        self.leer(3.6)
        L.dato(medido(esp.lineas_nodales(self.M, self.N), 0),
               "lineas que no vibran")
        self.leer(4.0)

        # --- 2. el otro modo, que es el mismo girado -----------------
        campo23 = self._placa(U23, X, Y)
        rectas23 = VGroup()
        for k in range(1, self.N):
            x = (k / self.N - 0.5) * self.LADO
            rectas23.add(Line([x, -radio, 0], [x, radio, 0],
                              stroke_color=TINTA, stroke_width=esp.TRAZO))
        for k in range(1, self.M):
            y = (k / self.M - 0.5) * self.LADO
            rectas23.add(Line([-radio, y, 0], [radio, y, 0],
                              stroke_color=TINTA, stroke_width=esp.TRAZO))
        marco23 = Square(side_length=self.LADO, stroke_color=APAGADO,
                         stroke_width=esp.TRAZO_FINO, fill_opacity=0.0)
        eti23 = rot(f"MODO {self.N} {self.M}", color=APAGADO)
        eti23.next_to(marco23, DOWN, buff=0.22)
        placa23 = lz.agrupar(marco23, campo23, rectas23, eti23)

        L.relevo(escena=placa23,
                 dato=(medido(esp.frecuencia_modo(self.M, self.N), 4),
                       "lo que suenan los dos"), t=0.9)
        self.leer(4.2)

        # --- 3. y su mezcla, que suena igual y no se parece ----------
        granos = esp.arena(Uc, Xc, Yc, cuantos=self.GRANOS)
        nube = esp.nube(granos, radio=radio, color=TINTA, grano=0.020,
                        escala=self.LADO)
        marco_mezcla = Square(side_length=self.LADO, stroke_color=APAGADO,
                              stroke_width=esp.TRAZO_FINO,
                              fill_opacity=0.0)
        eti_mezcla = rot("LOS DOS A LA VEZ", color=AMBAR)
        eti_mezcla.next_to(marco_mezcla, DOWN, buff=0.22)
        mezcla = lz.agrupar(marco_mezcla, nube, eti_mezcla)

        L.relevo(escena=mezcla,
                 dato=(medido(esp.frecuencia_modo(self.M, self.N), 4),
                       "y su mezcla, igual"), t=1.0)
        self.leer(4.4)

        # --- 4. y cambiando la mezcla, otra figura distinta -----------
        # Restar los dos modos da una figura; sumarlos da otra. Las dos
        # suenan a la misma frecuencia que los dos modos puros, porque
        # cualquier combinacion de dos modos degenerados sigue siendo un
        # modo. De ahi salen las decenas de figuras de una sola placa.
        Xc2, Yc2, Uc2 = esp.chladni(self.M, self.N, mezcla=-1.0,
                                    N=self.MALLA)
        granos2 = esp.arena(Uc2, Xc2, Yc2, cuantos=self.GRANOS)
        nube2 = esp.nube(granos2, radio=radio, color=TINTA, grano=0.020,
                         escala=self.LADO)
        marco2 = Square(side_length=self.LADO, stroke_color=APAGADO,
                        stroke_width=esp.TRAZO_FINO, fill_opacity=0.0)
        eti2 = rot("LA OTRA MEZCLA", color=AMBAR)
        eti2.next_to(marco2, DOWN, buff=0.22)

        L.relevo(escena=lz.agrupar(marco2, nube2, eti2), t=1.0)
        self.leer(4.4)

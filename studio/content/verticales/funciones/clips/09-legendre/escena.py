# 09 · LEGENDRE — la Tierra no es esfera.
#
# La forma de un planeta no se escribe con una esfera y una lista de
# correcciones: se escribe como una SUMA de armonicos, y el primero de
# todos —el que dice cuanto se ensancha por el ecuador— es el polinomio de
# Legendre de grado 2. Los siguientes son capas cada vez mas finas.
#
# Lo que los hace utiles es que son ORTOGONALES: cada capa lleva
# informacion que no esta en ninguna otra, asi que se pueden medir por
# separado y sumarlas sin que se estorben. Por eso el campo de gravedad de
# la Tierra se publica como una tabla de coeficientes.
#
# EL ACHATAMIENTO REAL NO SE VE, y por eso va DECLARADO: 1 parte en 298.
# Dibujado a escala, la Tierra es una circunferencia perfecta. La pieza
# exagera por 100 y lo dice en pantalla, que es la regla de la casa para
# todo lo que se exagera.
#
# La cifra de los kilometros SI es real: sale de multiplicar el radio
# ecuatorial por el achatamiento de WGS84. Los dos son datos DADOS —van en
# gris—, pero su producto lo calcula el render.
class Clip(Pieza):
    NOMBRE = "LEGENDRE"
    TESIS = "la Tierra no es esfera"

    EXAGERACION = 100.0
    RADIO = 2.15

    def _perfil(self, l, texto, color_eti=APAGADO, extra=None,
                marcar=False):
        eps = -esp.ACHATAMIENTO * self.EXAGERACION
        phi, r = esp.perfil_armonico(l, eps, N=1400)
        curva = esp.polar(phi, r, radio=self.RADIO, color=AMBAR,
                          grosor=esp.TRAZO, referencia=True)
        eti = rot(texto, color=color_eti)
        eti.next_to(curva, DOWN, buff=0.28)
        piezas = [curva, eti]
        if marcar:
            # Los puntos donde el armonico no deforma: sobre la esfera de
            # referencia, para que la cifra se pueda CONTAR en pantalla.
            escala = self.RADIO / float(np.max(np.abs(r)))
            for a in esp.cruces_perfil(l):
                piezas.append(Dot([escala * np.cos(a), escala * np.sin(a),
                                   0.0], radius=0.055, color=TINTA))
        if extra:
            nota = rot(extra, color=APAGADO)
            nota.next_to(eti, DOWN, buff=0.16)
            piezas.append(nota)
        return lz.agrupar(*piezas)

    def pieza(self):
        L = self.L

        # --- 1. el achatamiento, exagerado y declarado ----------------
        L.escena(self._perfil(2, "ARMONICO 2", color_eti=AMBAR,
                              extra="EXAGERADO X100"), t=0.9)
        self.leer(3.2)
        L.dato(medido(esp.abultamiento_km(), 1),
               "kilometros de mas", medido=True)
        self.leer(3.6)

        # --- 2, 3, 4. las capas siguientes ---------------------------
        # Cada armonico tiene exactamente l paralelos donde no deforma
        # nada, y esos ceros se CUENTAN sobre el perfil dibujado.
        for l in (3, 4, 5):
            # La cifra es la que se puede CONTAR en el dibujo: los cruces
            # del perfil con la esfera. Son 2l, no l — cada paralelo nodal
            # del armonico corta este meridiano dos veces. La primera
            # version rotulaba "4 paralelos quietos" junto a un dibujo con
            # ocho cruces marcados.
            L.relevo(escena=self._perfil(l, f"ARMONICO {l}",
                                         color_eti=AMBAR, marcar=True),
                     dato=(medido(len(esp.cruces_perfil(l)), 0),
                           "puntos que no se mueven"), t=0.9)
            self.leer(3.4)

        # --- 5. y la suma de todas ellas es el planeta ---------------
        L.relevo(escena=self._perfil(2, "ARMONICO 2", color_eti=AMBAR,
                                     extra="EXAGERADO X100"),
                 # La tupla de `dato` es POSICIONAL: el tercer elemento
                 # es `medido`. Un `medido=False` dentro de la tupla es un
                 # error de sintaxis, no un argumento.
                 dato=(medido(1.0 / esp.ACHATAMIENTO, 1),
                       "una parte entre tantas", False), t=0.9)
        self.leer(3.6)

# 18 · SUPERFORMULA — una formula, mil formas.
#
# Cierra el curso al reves que las demas. Todas las anteriores son
# funciones que hubo que inventar porque un problema concreto no tenia
# solucion con lo que habia. Esta es de 2003, no lleva el nombre de ningun
# muerto ilustre, y no resuelve un problema: RESUME una familia. Con cuatro
# numeros da estrellas de mar, flores, gotas, diatomeas y un cuadrado.
#
# Los lobulos se CUENTAN sobre la curva dibujada, no se leen del parametro
# que los produce. Y esa cuenta destapo un defecto: comparando cada muestra
# con sus vecinas, un maximo que cae justo entre dos muestras no se ve, y
# tres de las cinco formas salian con un lobulo de menos. Se cuenta por el
# cambio de signo de la pendiente, con envoltura.
class Clip(Pieza):
    NOMBRE = "SUPERFORMULA"
    TESIS = "una formula, mil formas"

    RADIO = 2.05
    ORDEN = ("circunferencia", "flor", "estrella", "gota", "diatomea",
             "cuadrado")

    def _forma(self, nombre):
        if nombre == "circunferencia":
            kw = dict(m=0, n1=1.0, n2=1.0, n3=1.0)
        else:
            kw = esp.FORMAS[nombre]
        phi, r = esp.superformula(**kw)
        curva = esp.polar(phi, r, radio=self.RADIO, color=AMBAR,
                          grosor=esp.TRAZO)
        eti = rot(nombre.upper(), color=APAGADO)
        eti.next_to(curva, DOWN, buff=0.30)
        return lz.agrupar(curva, eti), esp.lobulos(phi, r)

    def pieza(self):
        L = self.L

        # --- 1. lo mismo que una circunferencia ----------------------
        dibujo, n = self._forma("circunferencia")
        L.escena(dibujo, t=0.9)
        self.leer(2.8)
        L.dato(medido(n, 0), "lobulos, de momento")
        self.leer(2.6)

        # --- 2 a 6. y cambiando cuatro numeros ----------------------
        for nombre in self.ORDEN[1:]:
            dibujo, n = self._forma(nombre)
            L.relevo(escena=dibujo,
                     dato=(medido(n, 0), "lobulos, contados"), t=0.9)
            self.leer(2.8)

        # --- 7. y todo eso con cuatro numeros -----------------------
        # El 4 es un parametro de la formula, no una medida: va en gris.
        L.dato("4", "numeros, y ya esta", False)
        self.leer(3.4)

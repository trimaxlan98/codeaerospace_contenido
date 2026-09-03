# LA CONVOLUCION — deslizar, multiplicar, sumar.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "LA CONVOLUCION"
    TESIS = "deslizar, multiplicar, sumar"

    def pieza(self):
        self.leer(2.0)

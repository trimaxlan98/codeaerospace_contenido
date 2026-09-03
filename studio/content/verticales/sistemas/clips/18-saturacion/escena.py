# SATURACION — aparecen tonos que no entraron.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "SATURACION"
    TESIS = "aparecen tonos que no entraron"

    def pieza(self):
        self.leer(2.0)

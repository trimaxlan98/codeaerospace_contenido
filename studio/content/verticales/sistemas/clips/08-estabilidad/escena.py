# ESTABILIDAD — entrada acotada, salida acotada.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "ESTABILIDAD"
    TESIS = "entrada acotada, salida acotada"

    def pieza(self):
        self.leer(2.0)

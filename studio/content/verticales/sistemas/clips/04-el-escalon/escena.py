# EL ESCALON — la suma de infinitos impulsos.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "EL ESCALON"
    TESIS = "la suma de infinitos impulsos"

    def pieza(self):
        self.leer(2.0)

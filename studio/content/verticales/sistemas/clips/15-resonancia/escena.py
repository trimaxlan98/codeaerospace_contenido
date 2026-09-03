# RESONANCIA — un empujon a tiempo.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "RESONANCIA"
    TESIS = "un empujon a tiempo"

    def pieza(self):
        self.leer(2.0)

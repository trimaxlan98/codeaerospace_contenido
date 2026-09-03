# TRANSITORIO — una parte se apaga.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "TRANSITORIO"
    TESIS = "una parte se apaga"

    def pieza(self):
        self.leer(2.0)

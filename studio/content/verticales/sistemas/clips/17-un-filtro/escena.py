# UN FILTRO — unas pasan y otras no.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "UN FILTRO"
    TESIS = "unas pasan y otras no"

    def pieza(self):
        self.leer(2.0)

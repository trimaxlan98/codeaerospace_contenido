# AUTOFUNCIONES — lo unico que no deforma.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "AUTOFUNCIONES"
    TESIS = "lo unico que no deforma"

    def pieza(self):
        self.leer(2.0)

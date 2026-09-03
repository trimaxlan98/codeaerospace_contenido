# INVARIANZA — manana hace exactamente lo mismo.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "INVARIANZA"
    TESIS = "manana hace exactamente lo mismo"

    def pieza(self):
        self.leer(2.0)

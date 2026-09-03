# CAUSALIDAD — no responde antes del golpe.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "CAUSALIDAD"
    TESIS = "no responde antes del golpe"

    def pieza(self):
        self.leer(2.0)

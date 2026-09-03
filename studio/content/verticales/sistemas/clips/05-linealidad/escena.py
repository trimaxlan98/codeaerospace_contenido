# LINEALIDAD — dos entradas no se estorban.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "LINEALIDAD"
    TESIS = "dos entradas no se estorban"

    def pieza(self):
        self.leer(2.0)

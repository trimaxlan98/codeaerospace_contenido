# EN CASCADA — el orden no importa.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "EN CASCADA"
    TESIS = "el orden no importa"

    def pieza(self):
        self.leer(2.0)

# RESPUESTA EN FRECUENCIA — no puede inventar frecuencias.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "RESPUESTA EN FRECUENCIA"
    TESIS = "no puede inventar frecuencias"

    def pieza(self):
        self.leer(2.0)

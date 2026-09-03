# FASE Y RETARDO — la forma se rompe sola.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "FASE Y RETARDO"
    TESIS = "la forma se rompe sola"

    def pieza(self):
        self.leer(2.0)

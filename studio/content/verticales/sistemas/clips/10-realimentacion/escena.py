# REALIMENTACION — la salida vuelve a entrar.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "REALIMENTACION"
    TESIS = "la salida vuelve a entrar"

    def pieza(self):
        self.leer(2.0)

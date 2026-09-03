# RESPUESTA AL IMPULSO — un golpe lo dice todo.
#
# ESQUELETO. Lo escribe un subagente segun el contrato.
class Clip(Pieza):
    NOMBRE = "RESPUESTA AL IMPULSO"
    TESIS = "un golpe lo dice todo"

    def pieza(self):
        self.leer(2.0)

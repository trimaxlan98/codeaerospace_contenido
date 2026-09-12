# ESQUELETO. Lo reemplaza la pieza de verdad.
class Clip(Pieza):
    ES_MARCA = True

    def pieza(self):
        self.wait(1)

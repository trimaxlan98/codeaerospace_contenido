from manim import *

class MiPrimeraAnimacion(Scene):
    def construct(self):
        circulo = Circle()  # Crea un círculo
        circulo.set_fill(PINK, opacity=0.5)  # Le da color y transparencia
        cuadrado = Square()  # Crea un cuadrado
        
        self.play(Create(circulo))  # Anima la creación del círculo
        self.wait(1)
        self.play(Transform(circulo, cuadrado))  # Transforma el círculo en cuadrado
        self.play(FadeOut(cuadrado))  # Desvanece el objeto
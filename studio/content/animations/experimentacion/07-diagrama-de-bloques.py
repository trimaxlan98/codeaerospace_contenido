import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from bloques import bloque, conectar, flujo


class DiagramaDeBloques(Scene):
    def construct(self):
        titulo = Text("Cadena de transmisión digital", font_size=32,
                      color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        sensor = bloque("Sensor", color=TEAL_B)
        adc = bloque("ADC", color=BLUE_B)
        dsp = bloque("DSP", color=BLUE_B)
        mod = bloque("Modulador", color=YELLOW)
        tx = bloque("TX RF", color=RED_B)

        fila = VGroup(sensor, adc, dsp).arrange(RIGHT, buff=1.1)
        fila.shift(UP * 0.6)
        mod.next_to(dsp, DOWN, buff=1.1)
        tx.next_to(mod, LEFT, buff=1.1)

        self.play(LaggedStart(
            *[FadeIn(b, shift=DOWN * 0.2) for b in (sensor, adc, dsp, mod, tx)],
            lag_ratio=0.15), run_time=1.8)

        conexiones = [conectar(sensor, adc), conectar(adc, dsp),
                      conectar(dsp, mod), conectar(mod, tx)]
        self.play(LaggedStart(*[GrowArrow(c) for c in conexiones],
                              lag_ratio=0.15), run_time=1.5)

        # La señal recorre el pipeline dos veces
        self.play(flujo(conexiones))
        self.play(Indicate(tx, color=YELLOW, scale_factor=1.15), run_time=0.6)
        self.play(flujo(conexiones, color=TEAL_B))
        self.play(Indicate(tx, color=TEAL_B, scale_factor=1.15), run_time=0.6)
        self.wait(0.8)

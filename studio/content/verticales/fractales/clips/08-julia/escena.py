class Clip(Scene):
    """ESQUELETO. `render_vertical.py` aborta si falta una
    pieza declarada en curso.json, y sin esqueletos no se
    puede renderizar ninguna otra."""

    def construct(self):
        self.wait(1)

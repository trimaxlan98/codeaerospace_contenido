# 15 · Cierre — se cierra por donde se abrio.
#
# El encapsulado vuelve, se encoge hasta ser otra vez el punto ambar del
# principio, y el punto se convierte en la marca. Sin texto de mas: el
# curso ya dijo lo que tenia que decir.
class Clip(Scene):

    def construct(self):
        pastilla = chip.encapsulado(lado=3.6, pines_por_lado=11)
        pastilla.move_to([0, 1.15, 0])
        punto = Dot([0, 1.15, 0], radius=0.075, color=AMBAR)

        co = lz.titulo_display("co", font_size=64)
        de = lz.titulo_display("de", font_size=64)
        punto_marca = Dot([0, -1.5, 0], radius=0.055, color=AMBAR)
        sep = punto_marca.width / 2 + 0.12
        co.move_to([0, -1.5, 0]).shift(LEFT * (sep + co.width / 2))
        de.move_to([0, -1.5, 0]).shift(RIGHT * (sep + de.width / 2))
        aca = lz.espaciado("academy", font_size=26, color=APAGADO,
                           tracking=0.42)
        aca.next_to(VGroup(co, de), DOWN, buff=0.34)
        lz.cabe(VGroup(co, de), "wordmark de cierre")

        self.wait(0.5)
        self.play(Create(pastilla), run_time=1.5)
        self.wait(1.0)
        # el chip se recoge en el punto del que salio
        self.play(pastilla.animate.scale(0.02).set_opacity(0.0),
                  GrowFromCenter(punto), run_time=1.2, rate_func=smooth)
        self.remove(pastilla)
        self.wait(0.4)
        self.play(punto.animate.move_to([0, -1.5, 0]).scale(0.75),
                  FadeIn(co, shift=RIGHT * 0.4), FadeIn(de, shift=LEFT * 0.4),
                  run_time=1.1, rate_func=smooth)
        self.remove(punto)
        self.add(punto_marca)
        self.play(FadeIn(aca, lag_ratio=0.10), run_time=0.8)
        self.wait(1.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
        self.remove(*self.mobjects)
        self.wait(0.5)

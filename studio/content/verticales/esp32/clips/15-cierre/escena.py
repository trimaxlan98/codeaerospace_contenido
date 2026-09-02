# 15 · Cierre — se cierra por donde se abrio, y la marca queda bien puesta.
#
# Mismo arreglo que la intro: el wordmark es "CO.DE" en MAYUSCULAS con un
# PUNTO TIPOGRAFICO alineado por el borde inferior, no dos silabas en
# minuscula con un circulo flotando en medio.
#
# El puente sigue siendo el de este curso: el encapsulado se recoge hasta
# ser un punto, y ese punto ES el punto de la marca. Despues, la
# coreografia sobria del cierre de la casa — subrayado, quietud, y el punto
# parpadeando dos veces como cursor, que es la firma del canal.
class Clip(Scene):

    def construct(self):
        Y_CHIP = 1.45
        Y_MARCA = -1.35

        pastilla = chip.encapsulado(lado=3.6, pines_por_lado=11)
        pastilla.move_to([0, Y_CHIP, 0])

        co = Text("CO", font=lz.FUENTE_DISPLAY, weight="SEMIBOLD",
                  font_size=76, color=TINTA)
        punto = Text(".", font=lz.FUENTE_DISPLAY, weight="BOLD",
                     font_size=76, color=AMBAR)
        de = Text("DE", font=lz.FUENTE_DISPLAY, weight="SEMIBOLD",
                  font_size=76, color=TINTA)
        marca = VGroup(co, punto, de).arrange(buff=0.10, aligned_edge=DOWN)
        marca.move_to([0, Y_MARCA, 0])
        lz.cabe(marca, "wordmark de cierre")

        academy = Text("A C A D E M Y", font=lz.FUENTE_DISPLAY,
                       weight="MEDIUM", font_size=26, color=APAGADO)
        academy.next_to(marca, DOWN, buff=0.34)

        raya = Line(marca.get_corner(DL), marca.get_corner(DR),
                    stroke_width=3.5, color=AMBAR)
        raya.shift(DOWN * 0.20)

        # El chip se recoge EN el punto de la marca: nace donde va a vivir.
        semilla = Dot(punto.get_center(), radius=0.075, color=AMBAR)

        self.wait(0.5)
        self.play(Create(pastilla), run_time=1.5)
        self.wait(1.0)
        self.play(pastilla.animate.scale(0.02).move_to(punto.get_center())
                  .set_opacity(0.0),
                  GrowFromCenter(semilla), run_time=1.3, rate_func=smooth)
        self.remove(pastilla)
        self.wait(0.35)

        # El punto redondo releva al punto TIPOGRAFICO, y a su lado se
        # ensamblan las dos silabas.
        self.remove(semilla)
        self.add(punto)
        self.play(FadeIn(co, shift=RIGHT * 0.45),
                  FadeIn(de, shift=LEFT * 0.45),
                  run_time=1.0, rate_func=smooth)
        self.play(FadeIn(academy, lag_ratio=0.08), Create(raya),
                  run_time=0.8)
        self.wait(0.9)

        # La firma del canal: el punto parpadea dos veces como un cursor.
        for _ in range(2):
            punto.set_opacity(0.0)
            self.wait(0.18)
            punto.set_opacity(1.0)
            self.wait(0.17)
        self.wait(1.1)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
        self.remove(*self.mobjects)
        self.wait(0.5)

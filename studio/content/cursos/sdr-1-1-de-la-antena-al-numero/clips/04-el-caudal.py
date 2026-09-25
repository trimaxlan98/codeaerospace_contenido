class Clip4(Scene):
    """1.1.4 - El caudal: 2.4 MS/s x (I y Q) x 8 bits = 38.4 Mbit/s, contra
    los 0.768 del audio que sale al final: 50 veces menos. Cierre. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El caudal"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- la cuenta, factor a factor -----------------------------------
        a = tag_dato("2.4 MS/s", font_size=30)
        x1 = Text("x", font=FUENTE_HUD, font_size=30, color=C_TENUE)
        b = Text("2", font=FUENTE_HUD, font_size=30, color=C_TITULO)
        x2 = Text("x", font=FUENTE_HUD, font_size=30, color=C_TENUE)
        c = tag_dato("8 bits", font_size=30)
        fila = VGroup(a, x1, b, x2, c).arrange(RIGHT, buff=0.4)
        fila.move_to(UP * 1.75 + LEFT * 2.2)
        t_b = VGroup(Text("I", font=FUENTE_HUD, font_size=22, color=C_I),
                     Text("Q", font=FUENTE_HUD, font_size=22, color=C_Q)
                     ).arrange(RIGHT, buff=0.18)
        t_b.next_to(b, DOWN, buff=0.18)
        self.play(FadeIn(a, shift=UP * 0.15), run_time=0.5)
        self.wait(0.8)
        self.play(FadeIn(x1), FadeIn(b, shift=UP * 0.15), FadeIn(t_b),
                  run_time=0.5)
        self.wait(0.8)
        self.play(FadeIn(x2), FadeIn(c, shift=UP * 0.15), run_time=0.5)
        self.wait(1.2)

        cont = Contador(0.0, rotulo="Mbit/s por el USB", dec=1,
                        muestra="88.8", font_size=60)
        cont.next_to(fila, RIGHT, buff=1.1).shift(DOWN * 0.1)
        igual = Text("=", font=FUENTE_HUD, font_size=30, color=C_TENUE)
        igual.next_to(fila, RIGHT, buff=0.4)
        self.play(FadeIn(igual), FadeIn(cont.num), FadeIn(cont.rot),
                  run_time=0.4)
        cont.anim(self, CAUDAL, run_time=2.4)
        self.wait(2.6)

        # --- dos barras en la misma escala ---------------------------------
        largo = 11.0
        izq = LEFT * 5.5
        b_rf = Rectangle(width=largo, height=0.5, stroke_width=0,
                         fill_color=C_CALCULO, fill_opacity=0.8)
        b_rf.move_to(izq + RIGHT * largo / 2 + DOWN * 0.6)
        l_au = largo * AUDIO / CAUDAL
        b_au = Rectangle(width=l_au, height=0.5, stroke_width=0,
                         fill_color=C_OK, fill_opacity=0.9)
        b_au.move_to(izq + RIGHT * l_au / 2 + DOWN * 1.9)
        t_rf = tag_hud(f"{fmt(CAUDAL, 1)} Mbit/s  entra", font_size=21)
        t_rf.next_to(b_rf, UP, buff=0.14).align_to(b_rf, LEFT)
        t_au = tag_hud(f"{fmt(AUDIO, 3)} Mbit/s  audio", font_size=21,
                       color=C_OK)
        t_au.next_to(b_au, RIGHT, buff=0.3)
        self.play(GrowFromEdge(b_rf, LEFT), FadeIn(t_rf), run_time=1.4)
        self.wait(1.2)
        d_au = tag_dato("48 kS/s x 16 bits", font_size=19)
        d_au.next_to(b_au, DOWN, buff=0.2).align_to(b_au, LEFT)
        self.play(GrowFromEdge(b_au, LEFT), FadeIn(t_au), FadeIn(d_au),
                  run_time=1.0)
        self.wait(2.6)
        rot.mostrar(cifra_pie(f"{fmt(REDUCCION, 0)} veces menos"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

        cierre_leccion(self, rot, "La radio termina en el ADC.",
                       "Lo demas es aritmetica.", fila, t_b, igual, cont,
                       b_rf, b_au, t_rf, t_au, d_au)

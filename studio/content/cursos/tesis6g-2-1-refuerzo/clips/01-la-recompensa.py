class Clip1(Scene):
    """2.1.1 - Lo unico que un agente de refuerzo recibe es un numero por
    paso. En la tesis: throughput que suma, latencia que resta, e
    interferencia que resta fuerte. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("La recompensa"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        f = MathTex(r"r", r"=", rf"{ALFA:g}", r"\cdot tp", r"-", rf"{abs(BETA):g}", r"\cdot lat",
                    r"-", rf"{GAMMA:g}", r"\cdot intf", font_size=54, color=CODE_INK)
        f.move_to([0, 1.9, 0])
        f[3].set_color(C_OK)
        f[6].set_color(C_ADAPTA)
        f[9].set_color(C_NO)
        self.play(Write(f), run_time=1.8)
        rot.mostrar(dato_pie("pesos del YAML"), zona="abajo", run_time=0.5)
        self.wait(4.2)

        # un paso de ejemplo: tres barras que suman y restan hasta r
        y0, esc = -1.9, 0.03
        partes = [("tp", ALFA * EJ_TP, C_OK), ("lat", BETA * EJ_LAT, C_ADAPTA),
                  ("intf", -GAMMA * EJ_INTF, C_NO)]
        x, base = -4.6, 0.0
        suelo = Line([-5.6, y0, 0], [5.8, y0, 0], stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(suelo), run_time=0.4)
        cascada = VGroup()
        for i, (nm, v, col) in enumerate(partes):
            y_a, y_b = y0 + esc * base, y0 + esc * (base + v)
            b = Rectangle(width=1.2, height=abs(y_b - y_a), stroke_width=0, fill_color=col,
                          fill_opacity=1.0).move_to([x + 2.3 * i, (y_a + y_b) / 2, 0])
            e = tag_hud(f"{nm} {v:+.0f}", font_size=18, color=col).next_to(b, UP, buff=0.12)
            self.play(GrowFromEdge(b, DOWN if v > 0 else UP), FadeIn(e), run_time=0.8)
            cascada.add(b, e)
            base += v
            self.wait(2.2)
        total = Rectangle(width=1.2, height=esc * EJ_R, stroke_width=0, fill_color=C_CALCULO,
                          fill_opacity=1.0).move_to([x + 2.3 * 3 + 0.6, y0 + esc * EJ_R / 2, 0])
        self.play(GrowFromEdge(total, DOWN), run_time=0.8)
        e_t = tag_hud(f"r = {fmt(EJ_R, 0)}", font_size=20, color=C_CALCULO).next_to(total, UP, buff=0.12)
        self.play(FadeIn(e_t), run_time=0.3)
        rot.mostrar(cifra_pie(f"r = {fmt(EJ_R, 0)} en este paso"), zona="abajo", run_time=0.5)
        self.wait(4.0)
        rot.mostrar(dato_pie(f"{E['pasos_episodio']} pasos por episodio"), zona="abajo", run_time=0.5)
        self.wait(4.4)
        self.wait(1.2)

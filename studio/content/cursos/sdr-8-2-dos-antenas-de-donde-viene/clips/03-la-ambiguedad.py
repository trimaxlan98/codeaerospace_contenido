class Clip3(Scene):
    """8.2.3 - Con d = lambda (el doble de separacion que en los clips
    1-2) la MISMA diferencia de fase medida admite dos direcciones
    compatibles: -35.2 y 25.0 grados (ANG_1, S.doa_estimar(THETA, 1.0)).
    Dos haces, un solo par de antenas. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La ambiguedad"), zona="arriba",
                   run_time=0.6)
        self.wait(0.3)

        # --- las antenas, ahora separadas d = lambda (el doble), y la ------
        # normal: todo junto, para no dejar el cuadro a medio llenar.
        D_VIS = 5.6
        Y0 = -0.85
        a_izq = np.array([-D_VIS / 2, Y0, 0.0])
        a_der = np.array([D_VIS / 2, Y0, 0.0])

        def antena(pos):
            palo = Line(pos, pos + UP * 0.4, color=C_TENUE, stroke_width=2.6)
            base = Dot(pos, radius=0.075, color=C_TENUE)
            return VGroup(palo, base)

        an1, an2 = antena(a_izq), antena(a_der)
        base_linea = Line(a_izq, a_der, color=C_EJE, stroke_width=1.8)
        centro = (a_izq + a_der) / 2.0
        d_lam = MathTex(r"d = \lambda", font_size=28, color=C_DATO)
        d_lam.next_to(base_linea, DOWN, buff=0.16)
        normal = DashedLine(centro, centro + UP * 3.2, color=C_TENUE,
                            stroke_width=1.8, dash_length=0.1)
        et_normal = tag_junto(normal, "normal", UP, buff=0.1, font_size=18)

        self.play(Create(base_linea), FadeIn(an1), FadeIn(an2),
                  FadeIn(d_lam), Create(normal), FadeIn(et_normal),
                  run_time=1.2)
        self.wait(0.6)
        rot.mostrar(dato_pie("d = lambda"), zona="abajo", run_time=0.5)
        self.wait(1.2)

        # --- los dos haces compatibles con la MISMA fase medida --------------
        def haz(angulo_deg, largo=3.6):
            th = math.radians(angulo_deg)
            direccion = np.array([-math.sin(th), math.cos(th), 0.0])
            return Arrow(centro + direccion * largo, centro,
                        color=C_CALCULO, stroke_width=3.0, tip_length=0.2,
                        buff=0.0)

        haz_b = haz(ANG_1[1])          # 25.0 grados
        et_b = tag_hud(f"{fmt(ANG_1[1], 1)} grados", font_size=21)
        et_b.next_to(haz_b.get_start(), UP, buff=0.14)
        haz_a = haz(ANG_1[0])          # -35.2 grados
        et_a = tag_hud(f"{fmt(ANG_1[0], 1)} grados", font_size=21)
        et_a.next_to(haz_a.get_start(), UP, buff=0.14)

        self.play(GrowArrow(haz_b), FadeIn(et_b), run_time=0.9)
        self.wait(1.2)
        self.play(GrowArrow(haz_a), FadeIn(et_a), run_time=0.9)
        self.wait(2.6)

        rot.mostrar(cifra_pie(f"{fmt(ANG_1[0], 1)} y {fmt(ANG_1[1], 1)} "
                              f"grados"), zona="abajo", run_time=0.5)
        self.wait(3.0)
        # Flash en el vertice compartido: las dos flechas llegan al MISMO
        # par de antenas (no un Indicate: estiraria las flechas desde su
        # bounding box y las despegaria de "centro").
        self.play(Flash(centro, color=C_CALCULO, line_length=0.22,
                        num_lines=10, flash_radius=0.35), run_time=0.9)
        self.wait(14.0)

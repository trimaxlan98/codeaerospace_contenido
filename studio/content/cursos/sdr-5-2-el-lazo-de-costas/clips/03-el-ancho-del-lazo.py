from comunicaciones import Onda  # noqa: E402


def _traza(o, t, y, color, grosor=2.2, salto=90.0):
    """Polilinea en la caja de `o`, cortada donde el error de fase da la
    vuelta (modulo 180 grados): sin la raya vertical del salto."""
    g = VGroup()
    cortes = np.where(np.abs(np.diff(y)) > salto)[0] + 1
    for a, b in zip(np.r_[0, cortes], np.r_[cortes, len(y)]):
        if b - a < 2:
            continue
        c = VMobject(color=color, stroke_width=grosor)
        c.set_points_as_corners([o.en(u, v) for u, v in zip(t[a:b], y[a:b])])
        g.add(c)
    return g


class Clip3(Scene):
    """5.2.3 - El ancho del lazo: tres trazas del error de fase (estrecho,
    medio, ancho) en la MISMA escala (+-90 grados, 1500 simbolos). El
    estrecho tarda en engancharse y luego tiembla poco; el ancho se
    engancha enseguida y tiembla mas. Cian por fila: enganche y temblor
    (medianas de enganche y temblor medio de 8 semillas). (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El ancho del lazo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        n = len(FASE_REAL)
        k = np.arange(n)
        nombres = ("estrecho", "medio", "ancho")
        filas = []
        for bn in ANCHOS:
            o = Onda(k, np.zeros(n), rango_y=(-90.0, 90.0), ancho=7.4,
                     alto=1.3, color=C_LO)
            filas.append(o)
        VGroup(*filas).arrange(DOWN, buff=0.36).move_to(LEFT * 0.6
                                                        + DOWN * 0.0)

        ejes = VGroup(*[o.ejes for o in filas])
        tr, izq, der = [], [], []
        for o, bn, nom in zip(filas, ANCHOS, nombres):
            e = np.degrees(np.angle(np.exp(
                1j * 2 * (LAZOS[bn]["fase"] - FASE_REAL))) / 2)
            tr.append(_traza(o, k, e, C_LO))
            t_nom = Text(nom, font_size=24, color=C_TITULO)
            t_bn = tag_dato(f"Bn T = {bn:g}", font_size=19)
            g = VGroup(t_nom, t_bn).arrange(DOWN, buff=0.1,
                                            aligned_edge=RIGHT)
            g.next_to(o, LEFT, buff=0.35)
            izq.append(g)
            v1 = tag_hud(f"{ENG_MED[bn]}", font_size=26)
            v2 = tag_hud(f"{fmt(JIT_MED[bn], 1)}", font_size=26)
            v1.move_to(np.array([o.get_right()[0] + 1.0, o.get_center()[1],
                                 0.0]))
            v2.move_to(np.array([o.get_right()[0] + 2.5, o.get_center()[1],
                                 0.0]))
            der.append(VGroup(v1, v2))
        # unidades de la columna cian, una sola vez, arriba
        o0 = filas[0]
        t90 = VGroup(
            Text("90", font=FUENTE_HUD, font_size=18, color=C_TENUE)
            .next_to(o0.en(0.0, 90.0), LEFT, buff=0.1),
            Text("-90", font=FUENTE_HUD, font_size=18, color=C_TENUE)
            .next_to(o0.en(0.0, -90.0), LEFT, buff=0.1))
        t_uy = tag_junto(o0, "error, grados", UP, buff=0.1, font_size=22,
                         color=C_LO)
        t_uy.next_to(t90[0], LEFT, buff=0.2)
        t_ux = Text(f"{n} simbolos", font=FUENTE_HUD, font_size=18,
                    color=C_TENUE)
        t_ux.next_to(filas[-1].en(float(k[-1]), -90.0), DOWN, buff=0.08)
        t_ux.align_to(filas[-1], RIGHT)
        u_col = VGroup()
        for cab, uni, v in (("enganche", "simbolos", der[0][0]),
                            ("temblor", "grados", der[0][1])):
            h = VGroup(Text(cab, font_size=24, color=C_TITULO),
                       Text(uni, font=FUENTE_HUD, font_size=18,
                            color=C_TENUE)).arrange(DOWN, buff=0.08)
            h.move_to(np.array([v.get_center()[0], o0.get_top()[1] + 0.05,
                                0.0]))
            u_col.add(h)

        self.play(Create(ejes), FadeIn(t90), FadeIn(t_uy), FadeIn(t_ux),
                  run_time=0.9)
        snr = S.escenario_costas.__defaults__[3]
        rot.mostrar(dato_pie(f"SNR {snr:g} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(0.8)

        for i in range(3):
            self.play(FadeIn(izq[i], shift=RIGHT * 0.1), run_time=0.5)
            self.play(Create(tr[i]), run_time=2.4, rate_func=linear)
            self.wait(0.8)
            extra = [FadeIn(u_col)] if i == 0 else []
            self.play(FadeIn(der[i][0]), *extra, run_time=0.5)
            self.wait(0.7)
            self.play(FadeIn(der[i][1]), run_time=0.5)
            self.wait(1.6)

        self.wait(12.0)

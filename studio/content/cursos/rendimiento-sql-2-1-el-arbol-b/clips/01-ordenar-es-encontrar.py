class Clip1(Scene):
    """2.1.1 - Sin orden, encontrar un valor es revisar cada carta una por
    una (casi todas, y quedan en rojo tenue: el costo); con un indice
    arriba (como el de un libro), se salta directo a la carta que toca.
    Sin cifras: es la idea, antes de nombrar el arbol. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Ordenar es encontrar"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # el objetivo va cerca del final: se revisan casi todas las cartas
        valores = [37, 12, 4, 91, 23, 66, 8, 45, 58, 71]

        def carta(n, color=C_TENUE):
            caja = RoundedRectangle(width=0.46, height=0.64, corner_radius=0.05,
                                    stroke_color=color, stroke_width=1.8,
                                    fill_color=color, fill_opacity=0.12)
            t = Text(str(n), font=FUENTE_HUD, font_size=16, color=C_TITULO)
            t.move_to(caja)
            g = VGroup(caja, t)
            g.caja = caja
            return g

        # --- izquierda: sin orden -----------------------------------------
        izq = VGroup(*[carta(v) for v in valores])
        izq.arrange(RIGHT, buff=0.1)
        izq.move_to(LEFT * 4.0 + UP * 0.3)
        tag_izq = tag_junto(izq, "sin orden", DOWN, buff=0.3, color=C_MALO)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in izq],
                              lag_ratio=0.08), run_time=1.6)
        self.play(FadeIn(tag_izq), run_time=0.4)
        self.wait(1.4)

        # --- derecha: la misma tienda, ordenada, con un indice arriba -----
        ordenados = sorted(valores)
        der = VGroup(*[carta(v) for v in ordenados])
        der.arrange(RIGHT, buff=0.1)
        der.move_to(RIGHT * 4.0 + UP * 0.3)
        tag_der = tag_junto(der, "con indice", DOWN, buff=0.3, color=C_BUENO)

        indice = VGroup(*[carta(v, color=C_INDICE) for v in ordenados[::3]])
        indice.arrange(RIGHT, buff=0.5)
        indice.next_to(der, UP, buff=0.5)
        flechas_idx = VGroup(*[
            Arrow(indice[i].get_bottom(), der[ordenados.index(ordenados[::3][i])].get_top(),
                  buff=0.06, stroke_width=1.8, color=C_INDICE,
                  max_tip_length_to_length_ratio=0.18)
            for i in range(len(indice))])

        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in der],
                              lag_ratio=0.05), run_time=1.4)
        self.play(FadeIn(tag_der), run_time=0.4)
        self.wait(0.6)
        self.play(FadeIn(indice, shift=DOWN * 0.15), run_time=0.6)
        self.play(Create(flechas_idx), run_time=0.9)
        libro = tag_junto(indice, "como en un libro", UP, buff=0.2)
        self.play(FadeIn(libro), run_time=0.4)
        self.wait(2.2)

        # --- buscar 58: a la izquierda se revisa carta por carta ----------
        objetivo = 58
        pos_izq = valores.index(objetivo)
        pos_der = ordenados.index(objetivo)
        self.play(FadeOut(libro), run_time=0.4)

        # las cartas revisadas EN VANO quedan en rojo tenue: el costo de
        # revisar, no "el camino caro es esta carta"
        previas = [izq[i][0] for i in range(pos_izq)]
        self.play(LaggedStart(
            *[c.animate.set_fill(C_MALO, 0.3).set_stroke(C_MALO, opacity=0.6)
              for c in previas], lag_ratio=0.16), run_time=2.8)
        self.wait(0.5)
        # la hallada: no es "el camino caro", solo el final de la revisión
        self.play(Indicate(izq[pos_izq][0], color=C_TITULO, scale_factor=1.18),
                  run_time=0.6)
        self.play(izq[pos_izq][0].animate.set_stroke(C_TITULO, width=2.6),
                  run_time=0.4)
        self.wait(1.4)

        # --- a la derecha: el indice salta directo ------------------------
        tramo = pos_der // 3
        salto = Arrow(indice[tramo].get_bottom(), der[pos_der].get_top(),
                      buff=0.06, stroke_width=4.0, color=C_BUENO,
                      max_tip_length_to_length_ratio=0.16)
        self.play(Indicate(indice[tramo][0], color=C_BUENO, scale_factor=1.2),
                  run_time=0.6)
        self.play(Create(salto), run_time=0.7)
        self.play(der[pos_der][0].animate.set_fill(C_BUENO, 0.85).set_stroke(C_BUENO),
                  run_time=0.5)
        self.wait(2.2)

        # el cierre baja a la mitad inferior, que hasta aqui quedaba vacia
        cierre_tag = tag_junto(VGroup(izq, der), "saltar, no revisar", DOWN,
                               buff=2.6, color=C_TITULO)
        self.play(FadeIn(cierre_tag), run_time=0.5)
        self.wait(8.0)

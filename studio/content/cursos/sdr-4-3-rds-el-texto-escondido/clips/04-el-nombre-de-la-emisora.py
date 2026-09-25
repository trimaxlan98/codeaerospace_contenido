class Clip4(Scene):
    """4.3.4 - Los bloques D de los cuatro grupos entregan dos letras cada
    uno; el nombre se arma en verde debajo de su bloque de origen. 0
    errores calculado, y a 8 dB de CNR todavia 12 bits errados sin perder
    el nombre (RDS8). Cierre de la leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El nombre de la emisora"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        hits_d = [h for h in RDS["hits"] if h[1] == "D"][:4]
        pares = [(chr(d >> 8), chr(d & 0xFF)) for (_, _, d) in hits_d]
        letras_txt = [ch for par in pares for ch in par]
        n_chars = len(letras_txt)

        lado = 1.15
        slots = VGroup(*[Square(lado, color=C_EJE, stroke_width=1.6)
                         for _ in range(n_chars)])
        slots.arrange(RIGHT, buff=0.18)
        slots.move_to(DOWN * 0.45)
        placeholders = VGroup(*[Text("?", font_size=40, color=C_TENUE)
                                for _ in range(n_chars)])
        for p, s in zip(placeholders, slots):
            p.move_to(s)

        # --- un bloque D (hex, gris) y su flecha sobre cada pareja -----------
        hexas, flechas = VGroup(), VGroup()
        for gi, (_, _, d) in enumerate(hits_d):
            par = VGroup(slots[2 * gi], slots[2 * gi + 1])
            hx = tag_hud(f"{d:04X}", font_size=20, color=C_DATO)
            hx.next_to(par, UP, buff=0.95)
            fl = Arrow(hx.get_bottom() + DOWN * 0.06,
                      par.get_top() + UP * 0.06, buff=0.0, color=C_DATO,
                      stroke_width=2.4, max_tip_length_to_length_ratio=0.28)
            hexas.add(hx)
            flechas.add(fl)

        self.play(Create(slots), run_time=0.9)
        self.wait(0.4)
        self.play(FadeIn(placeholders), run_time=0.5)
        self.wait(1.2)

        # --- cada grupo entrega un bloque D: dos letras -----------------
        for gi, (a, b) in enumerate(pares):
            self.play(FadeIn(hexas[gi]), GrowArrow(flechas[gi]),
                      run_time=0.5)
            self.wait(0.4)
            i0, i1 = 2 * gi, 2 * gi + 1
            anims = []
            for idx, ch in ((i0, a), (i1, b)):
                if ch == " ":
                    anims.append(FadeOut(placeholders[idx]))
                else:
                    letra = Text(ch, font_size=54, color=C_OK)
                    letra.move_to(slots[idx])
                    anims.append(Transform(placeholders[idx], letra))
            self.play(*anims, run_time=0.7)
            self.wait(0.8)

        self.wait(1.0)

        # --- cero errores, calculado sobre la cadena entera -----------------
        rot.mostrar(cifra_pie(f"{RDS['errores']} bits errados"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)

        # --- a 8 dB de CNR el nombre sobrevive --------------------------
        rot.mostrar(dato_pie("CNR elegido: 8 dB"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)
        rot.mostrar(cifra_pie(f"{RDS8['errores']} bits errados"),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)
        letras_visibles = VGroup(*[placeholders[i] for i in range(n_chars)
                                   if letras_txt[i] != " "])
        self.play(Indicate(letras_visibles, color=C_OK, scale_factor=1.08),
                  run_time=1.1)
        self.wait(2.0)

        rot.mostrar(dato_pie("emisora ficticia"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        cierre_leccion(self, rot, "La radio de siempre",
                       "lleva datos escondidos.", slots, placeholders,
                       hexas, flechas)

class Clip3(Scene):
    """3.4.3 - Las compuertas del protocolo como esclusas: G0 documenta el
    entorno que no servia, G1 aprueba el instrumento, G2a y G2b el
    aprendizaje. G3 y G4 estan desbloqueadas y SIN correr: a trazos.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Las compuertas"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        xs = np.linspace(-5.3, 5.3, len(ORDEN))
        y = -0.2
        canal = Line([-6.6, y, 0], [6.6, y, 0], stroke_color=C_TIERRA, stroke_width=14)
        self.play(Create(canal), run_time=0.6)
        puertas, cifras = {}, {}
        postes, noms = VGroup(), VGroup()
        for cid, x in zip(ORDEN, xs):
            hecha = COMP[cid]["estado"] == "passed"
            col = CODE_INK if hecha else C_TENUE
            postes.add(Line([x - 0.5, y - 0.7, 0], [x - 0.5, y + 0.7, 0], stroke_color=col, stroke_width=4),
                       Line([x + 0.5, y - 0.7, 0], [x + 0.5, y + 0.7, 0], stroke_color=col, stroke_width=4))
            if hecha:
                p = Rectangle(width=1.0, height=0.16, stroke_width=0, fill_color=col, fill_opacity=1.0).move_to([x, y, 0])
            else:
                p = DashedVMobject(Rectangle(width=1.0, height=0.16, stroke_color=col, stroke_width=3).move_to([x, y, 0]),
                                   num_dashes=10)
            puertas[cid] = p
            noms.add(tag_hud(cid, font_size=22, color=col).move_to([x, y + 1.1, 0]))
            if cid in VALOR:
                txt, rol = VALOR[cid]
                cifras[cid] = tag_hud(txt, font_size=16, color=C_NO if rol == "no" else C_OK).move_to([x, y - 1.1, 0])
        self.play(FadeIn(postes), FadeIn(noms), *[FadeIn(p) for p in puertas.values()], run_time=0.9)
        rot.mostrar(dato_pie("GATES.md de la tesis"), zona="abajo", run_time=0.5)
        self.wait(2.0)
        barco = Dot([-6.5, y, 0], radius=0.15, color=C_ADAPTA)
        self.add(barco)

        def cruzar(cid, x):
            self.play(barco.animate.move_to([x - 0.85, y, 0]), run_time=0.5, rate_func=linear)
            self.play(Rotate(puertas[cid], angle=PI / 2, about_point=[x - 0.5, y, 0]), run_time=0.4)
            self.play(puertas[cid].animate.set_fill(C_OK), run_time=0.15)
            self.play(FadeIn(cifras[cid], shift=UP * 0.1), barco.animate.move_to([x + 0.85, y, 0]),
                      run_time=0.5, rate_func=linear)
            self.wait(1.2)
        for cid, x in zip(ORDEN[:2], xs[:2]):
            cruzar(cid, x)
        rot.mostrar(dato_pie("instrumento: G0 y G1"), zona="abajo", run_time=0.5)
        self.wait(2.4)
        for cid, x in zip(ORDEN[2:4], xs[2:4]):
            cruzar(cid, x)
        rot.mostrar(dato_pie("aprendizaje: G2a y G2b"), zona="abajo", run_time=0.5)
        self.wait(2.2)
        self.play(barco.animate.move_to([xs[4] - 0.85, y, 0]), run_time=0.5, rate_func=linear)
        self.play(puertas["G3"].animate.set_stroke(C_ADAPTA), run_time=0.4)
        self.play(puertas["G3"].animate.set_stroke(C_TENUE), run_time=0.4)
        rot.mostrar(dato_pie("G3: desbloqueada, sin correr"), zona="abajo", run_time=0.5)
        self.wait(4.0)

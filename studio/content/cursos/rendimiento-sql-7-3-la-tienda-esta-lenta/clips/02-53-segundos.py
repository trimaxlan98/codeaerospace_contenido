class Clip2(Scene):
    """7.3.2 - Trescientas peticiones de la tienda, de los cuatro tipos que
    arreglan las lecciones anteriores, entran en una sola cola; sin los
    arreglos, el servidor tarda 53 segundos en atenderlas todas. Los dos
    numeros son la carga MEDIDA del caso (ambar). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Trescientas peticiones"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- cuatro carriles: los cuatro tipos de peticion -----------------
        tipos = [("login", 1.6), ("mis pedidos", 2.4), ("el ticket", 2.1),
                ("reporte", 1.8)]
        xs = np.linspace(-4.7, 4.7, 4)
        carriles = VGroup()
        for x, (nombre, ancho) in zip(xs, tipos):
            caja = S.operador(nombre, color=C_TENUE, ancho=ancho, alto=0.62,
                              font_size=18)
            caja.move_to([x, 2.35, 0])
            carriles.add(caja)
        et_carriles = tag_junto(carriles, "cuatro tipos", DOWN, buff=0.7)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in carriles],
                              lag_ratio=0.15), run_time=1.2)
        self.play(FadeIn(et_carriles), run_time=0.4)
        self.wait(1.3)

        # --- un embudo: las cuatro colas convergen en una sola ------------
        embudo = Polygon([-3.4, 1.35, 0], [3.4, 1.35, 0], [0.38, -0.55, 0],
                         [-0.38, -0.55, 0], stroke_color=C_TENUE,
                         stroke_width=2.0, fill_color=C_TENUE, fill_opacity=0.08)
        self.play(FadeOut(et_carriles), Create(embudo), run_time=0.7)
        self.wait(0.5)

        cont = Contador(0, rotulo="peticiones", font_size=48, digitos=3)
        cont.move_to(DOWN * 2.05)
        self.play(FadeIn(cont), run_time=0.4)

        puntos = VGroup()
        destino = embudo.get_bottom() + DOWN * 0.2
        for k in range(36):
            origen = carriles[k % 4].get_bottom()
            puntos.add(Dot(origen, radius=0.055, color=C_MOTOR))
        self.add(puntos)
        anims = [p.animate.move_to(destino).set_opacity(0.15) for p in puntos]
        cont.anim(self, PETICIONES, run_time=4.2,
                 extra=[LaggedStart(*anims, lag_ratio=0.06)])
        self.wait(2.4)

        # --- las 300 ya se ven en el contador: no se repite abajo ----------
        grupo1 = VGroup(carriles, embudo, puntos, cont)
        self.play(FadeOut(grupo1), run_time=0.7)

        # --- el reloj: sin los arreglos, la cola tarda 53 segundos --------
        reloj = Circle(radius=1.5, stroke_color=C_TENUE, stroke_width=3)
        centro = Dot(ORIGIN, radius=0.06, color=C_TENUE)
        manecilla = Line(ORIGIN, UP * 1.1, stroke_color=C_MOTOR, stroke_width=4)
        reloj_g = VGroup(reloj, centro, manecilla)
        reloj_g.move_to(UP * 0.45)
        self.play(FadeIn(reloj_g), run_time=0.6)
        self.wait(0.6)

        seg = Contador(0, rotulo="segundos", font_size=52, digitos=2)
        seg.next_to(reloj_g, DOWN, buff=0.85)
        self.play(FadeIn(seg), run_time=0.4)
        seg.anim(self, ANTES, run_time=4.2,
                extra=[Rotate(manecilla, angle=-7 * PI,
                              about_point=reloj.get_center())])
        self.wait(9.4)
